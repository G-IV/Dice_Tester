from pathlib import Path

import Scripts.main as main_module


class FakeDB:
    def __init__(self, dice_id: str, rows: list[dict] | None = None) -> None:
        self.dice_id = dice_id
        self.rows = list(rows or [])
        self.deleted_ids: list[str] = []
        self.waited = False

    def delete_results_for_die(self, dice_id: str, wait: bool = True) -> None:
        self.deleted_ids.append(dice_id)
        self.rows = [row for row in self.rows if str(row['dice_id']) != str(dice_id)]

    def write_test_result(self, dice_result: str, image_path: str, dice_sides: int | None = None, wait: bool = False) -> None:
        self.rows.append(
            {
                'dice_id': self.dice_id,
                'timestamp': f'ts-{len(self.rows)}',
                'dice_sides': dice_sides,
                'dice_result': int(dice_result),
                'image': image_path,
            }
        )

    def wait_for_writes(self) -> None:
        self.waited = True

    def read_results_for_die(self, dice_id: str) -> list[dict]:
        return [dict(row) for row in self.rows if str(row['dice_id']) == str(dice_id)]


class FakeBoxes:
    def __init__(self, classes) -> None:
        self.cls = classes


class FakeResult:
    def __init__(self, classes, value: int | None) -> None:
        self.boxes = FakeBoxes(classes)
        self.value = value


class FakeModel:
    def __call__(self, frame, verbose: bool = False):
        name = Path(frame).name
        if name == 'valid.jpg':
            return [FakeResult([7], 4)]
        if name == 'invalid.jpg':
            return [FakeResult([1], None)]
        return [FakeResult([], None)]


class FakeDice:
    sides = 6

    def _dice_key(self) -> int:
        return 7

    def get_dice_value(self, result) -> int | None:
        return result.value


def test_rebuild_capture_folder_results_moves_valid_and_unknown_images(tmp_path: Path, monkeypatch) -> None:
    capture_dir = tmp_path / '77'
    capture_dir.mkdir()
    (capture_dir / 'valid.jpg').write_bytes(b'valid')
    (capture_dir / 'invalid.jpg').write_bytes(b'invalid')
    (capture_dir / 'results.html').write_text('old report', encoding='utf-8')

    db = FakeDB(
        dice_id='77',
        rows=[
            {
                'dice_id': '77',
                'timestamp': 'old-ts',
                'dice_sides': 6,
                'dice_result': 2,
                'image': str(capture_dir / 'images' / 'old.jpg'),
            }
        ],
    )

    monkeypatch.setattr(main_module.cv2, 'imread', lambda path: path)
    monkeypatch.setattr(main_module, 'analyze_results', lambda dice_id, rows, dice_sides: {'rows': rows, 'dice_id': dice_id, 'dice_sides': dice_sides})

    def fake_write_report(report, output_dir: Path) -> Path:
        report_path = output_dir / 'results.html'
        report_path.write_text('fresh report', encoding='utf-8')
        return report_path

    monkeypatch.setattr(main_module, 'write_report', fake_write_report)

    report_path, total_count, valid_count, unknown_count = main_module._rebuild_capture_folder_results(
        dice_id='77',
        capture_dir=capture_dir,
        db=db,
        dice=FakeDice(),
        model=FakeModel(),
    )

    assert report_path == capture_dir / 'results.html'
    assert report_path.read_text(encoding='utf-8') == 'fresh report'
    assert total_count == 2
    assert valid_count == 1
    assert unknown_count == 1
    assert db.deleted_ids == ['77']
    assert db.waited is True
    assert db.read_results_for_die('77') == [
        {
            'dice_id': '77',
            'timestamp': 'ts-0',
            'dice_sides': 6,
            'dice_result': 4,
            'image': str(capture_dir / 'images' / 'valid.jpg'),
        }
    ]
    assert (capture_dir / 'images' / 'valid.jpg').exists()
    assert (capture_dir / 'Unknown' / 'invalid.jpg').exists()


def test_rebuild_capture_folder_results_writes_empty_report_when_no_images_validate(tmp_path: Path, monkeypatch) -> None:
    capture_dir = tmp_path / '88'
    capture_dir.mkdir()
    (capture_dir / 'invalid.jpg').write_bytes(b'invalid')
    db = FakeDB(dice_id='88')

    monkeypatch.setattr(main_module.cv2, 'imread', lambda path: path)
    monkeypatch.setattr(main_module, 'write_report', lambda report, output_dir: (_ for _ in ()).throw(AssertionError('write_report should not be called')))

    report_path, total_count, valid_count, unknown_count = main_module._rebuild_capture_folder_results(
        dice_id='88',
        capture_dir=capture_dir,
        db=db,
        dice=FakeDice(),
        model=FakeModel(),
    )

    assert report_path == capture_dir / 'results.html'
    assert total_count == 1
    assert valid_count == 0
    assert unknown_count == 1
    assert (capture_dir / 'Unknown' / 'invalid.jpg').exists()
    assert 'has no validated samples' in report_path.read_text(encoding='utf-8')
    assert db.read_results_for_die('88') == []