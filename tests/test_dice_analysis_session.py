from types import SimpleNamespace

from Scripts.Modules.Dice.dice import DiceState
from Scripts.Modules.queue_data import Command as QuCmd
from Scripts.Modules.Workflow.dice_analysis_session import DiceAnalysisSession


class FakeQueue:
    def __init__(self) -> None:
        self.items = []

    def put(self, item) -> None:
        self.items.append(item)


class FakeProcessData:
    def __init__(self) -> None:
        self.frames = [[1, 2, 3]]
        self.results = ['result-1']
        self.fps = 30

    def clear_frames(self) -> None:
        self.frames = []
        self.results = []


class FakeFeed:
    def destroy(self) -> None:
        pass

    def ready_for_frames(self, ready: bool = True) -> None:
        pass


class FakeStream:
    window = None

    def show_frame(self, frame, delay: int = 1) -> None:
        pass

    def destroy(self) -> None:
        pass


class FakeMotor:
    def __init__(self) -> None:
        self.reset_calls = 0

    def close(self) -> None:
        pass

    def move_to_uncap(self) -> None:
        pass

    def flip(self) -> None:
        pass

    def reset_position(self) -> None:
        self.reset_calls += 1


class FakeDB:
    def __init__(self) -> None:
        self.dice_id = '1'

    def generate_id(self) -> str:
        self.dice_id = '1'
        return self.dice_id

    def wait_for_writes(self) -> None:
        pass

    def stop_writer(self) -> None:
        pass


class SequencedDice:
    def __init__(self, states: list[DiceState], value: int | None = 2) -> None:
        self._states = list(states)
        self.dice_state = DiceState.UNKNOWN
        self.sides = 6
        self.value = value

    def set_dice_state(self) -> None:
        if self._states:
            self.dice_state = self._states.pop(0)

    def get_dice_value(self, result) -> int:
        return self.value


class ImmediateFuture:
    def result(self):
        return None

    def add_done_callback(self, callback) -> None:
        callback(self)


class RecordingExecutor:
    def __init__(self) -> None:
        self.submissions = []

    def submit(self, fn, *args, **kwargs):
        self.submissions.append((fn, args, kwargs))
        return ImmediateFuture()


def create_session(dice: SequencedDice) -> DiceAnalysisSession:
    return DiceAnalysisSession(
        process_queue=FakeQueue(),
        process_data=FakeProcessData(),
        feed=FakeFeed(),
        stream=FakeStream(),
        dice=dice,
        motor=FakeMotor(),
        db=FakeDB(),
        config=SimpleNamespace(
            max_time_before_flip=4,
            analysis_image_output_dir='unused',
        ),
        target_samples=10,
        logging=False,
    )


def test_settled_value_is_not_recorded_twice_without_transition() -> None:
    dice = SequencedDice(
        [
            DiceState.SETTLED,
            DiceState.SETTLED,
            DiceState.UNKNOWN,
            DiceState.SETTLED,
        ]
    )
    session = create_session(dice)
    image_executor = RecordingExecutor()

    session.handle_evaluate_dice_state(image_executor)
    session.handle_evaluate_dice_state(image_executor)
    session.handle_evaluate_dice_state(image_executor)
    session.handle_evaluate_dice_state(image_executor)

    assert len(image_executor.submissions) == 2
    assert session.awaiting_next_roll is True


def test_get_next_sample_does_not_clear_transition_guard() -> None:
    session = create_session(SequencedDice([DiceState.UNKNOWN]))
    session.awaiting_next_roll = True

    session.handle_get_next_sample()

    assert session.awaiting_next_roll is True


def test_invalid_settled_value_requests_retry_without_persist() -> None:
    session = create_session(SequencedDice([DiceState.SETTLED], value=None))
    image_executor = RecordingExecutor()

    session.handle_evaluate_dice_state(image_executor)

    assert len(image_executor.submissions) == 0
    assert session.submitted_samples == 0
    assert session.awaiting_next_roll is True
    assert any(item.cmd == QuCmd.GET_NEXT_SAMPLE for item in session.process_queue.items)


def test_unknown_timeout_enters_reset_once_and_ignores_follow_up_evaluations() -> None:
    session = create_session(SequencedDice([DiceState.UNKNOWN, DiceState.UNKNOWN, DiceState.UNKNOWN]))
    image_executor = RecordingExecutor()
    session.process_data.frames = [0] * 200

    session.handle_evaluate_dice_state(image_executor)
    session.handle_evaluate_dice_state(image_executor)
    session.handle_evaluate_dice_state(image_executor)

    reset_cmds = [item for item in session.process_queue.items if item.cmd == QuCmd.RESET_TOWER]
    assert session.state == session.state.RESETTING_TOWER
    assert len(reset_cmds) == 1


def test_handle_reset_tower_ignored_when_not_resetting() -> None:
    session = create_session(SequencedDice([DiceState.UNKNOWN]))
    session.state = session.state.ANALYZING

    session.handle_reset_tower()

    assert session.motor.reset_calls == 0