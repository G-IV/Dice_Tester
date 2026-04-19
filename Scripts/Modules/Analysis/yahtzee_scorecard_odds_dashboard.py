from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import escape
from itertools import combinations
from math import comb, sqrt
from pathlib import Path
import argparse
import sqlite3

from Scripts.Modules.Database.database import DBPath


YAHTZEE_PREFIX = 'six_sided_yahtzee_'
DEFAULT_HTML_OUTPUT_PATH = Path('Scripts/Modules/Database/Captures/yahtzee_scorecard_odds_dashboard.html')
FACES = (1, 2, 3, 4, 5, 6)


@dataclass(frozen=True)
class GroupOdds:
    dice_ids: tuple[str, ...]
    one_roll: dict[str, float]
    turn_3roll: dict[str, float]
    turn_distance: float


def _format_die_name(dice_id: str) -> str:
    return dice_id.removeprefix(YAHTZEE_PREFIX)


def _format_group(dice_ids: tuple[str, ...]) -> str:
    return ', '.join(_format_die_name(dice_id) for dice_id in dice_ids)


def _load_rows() -> dict[str, list[int]]:
    connection = sqlite3.connect(DBPath)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            '''
            SELECT dice_id, dice_result
            FROM test_results
            WHERE dice_id LIKE ?
            ORDER BY dice_id, timestamp
            ''',
            (f'{YAHTZEE_PREFIX}%',),
        ).fetchall()
    finally:
        connection.close()

    by_die: dict[str, list[int]] = {}
    for row in rows:
        by_die.setdefault(str(row['dice_id']), []).append(int(row['dice_result']))
    return by_die


def _face_probabilities(rolls_by_die: dict[str, list[int]]) -> dict[str, tuple[float, ...]]:
    probabilities: dict[str, tuple[float, ...]] = {}
    for dice_id, rolls in sorted(rolls_by_die.items()):
        if not rolls:
            raise ValueError(f'No rolls available for die {dice_id}')
        counts = [0, 0, 0, 0, 0, 0]
        for roll in rolls:
            if roll < 1 or roll > 6:
                raise ValueError(f'Invalid face value {roll} for die {dice_id}')
            counts[roll - 1] += 1
        total = float(len(rolls))
        probabilities[dice_id] = tuple(count / total for count in counts)
    return probabilities


def _ordered_metric_labels() -> list[tuple[str, str]]:
    labels = [
        ('yahtzee_any', 'Yahtzee (any face)'),
        ('full_house', 'Full house'),
        ('small_straight', 'Small straight (4-run)'),
        ('large_straight', 'Large straight (5-run)'),
    ]
    for face in FACES:
        labels.append((f'at_least_3_face_{face}', f'At least 3x face {face}'))
    for face in FACES:
        labels.append((f'at_least_4_face_{face}', f'At least 4x face {face}'))
    for face in FACES:
        labels.append((f'exact_5_face_{face}', f'Exactly 5x face {face}'))
    return labels


def _small_straight_from_counts(counts: tuple[int, ...]) -> bool:
    present = {index + 1 for index, value in enumerate(counts) if value > 0}
    return (
        {1, 2, 3, 4}.issubset(present)
        or {2, 3, 4, 5}.issubset(present)
        or {3, 4, 5, 6}.issubset(present)
    )


def _large_straight_from_counts(counts: tuple[int, ...]) -> bool:
    present = {index + 1 for index, value in enumerate(counts) if value > 0}
    return present == {1, 2, 3, 4, 5} or present == {2, 3, 4, 5, 6}


def _full_house_from_counts(counts: tuple[int, ...]) -> bool:
    ordered = sorted(counts, reverse=True)
    return ordered[0] == 3 and ordered[1] == 2


def _metrics_from_counts(counts: tuple[int, ...]) -> dict[str, float]:
    values: dict[str, float] = {key: 0.0 for key, _ in _ordered_metric_labels()}
    if max(counts) == 5:
        values['yahtzee_any'] = 1.0
    if _full_house_from_counts(counts):
        values['full_house'] = 1.0
    if _small_straight_from_counts(counts):
        values['small_straight'] = 1.0
    if _large_straight_from_counts(counts):
        values['large_straight'] = 1.0

    for face in FACES:
        value = counts[face - 1]
        if value >= 3:
            values[f'at_least_3_face_{face}'] = 1.0
        if value >= 4:
            values[f'at_least_4_face_{face}'] = 1.0
        if value == 5:
            values[f'exact_5_face_{face}'] = 1.0
    return values


def _all_count_states(total: int = 5) -> tuple[tuple[int, int, int, int, int, int], ...]:
    states: list[tuple[int, int, int, int, int, int]] = []
    for c1 in range(total + 1):
        for c2 in range(total - c1 + 1):
            for c3 in range(total - c1 - c2 + 1):
                for c4 in range(total - c1 - c2 - c3 + 1):
                    for c5 in range(total - c1 - c2 - c3 - c4 + 1):
                        c6 = total - c1 - c2 - c3 - c4 - c5
                        states.append((c1, c2, c3, c4, c5, c6))
    return tuple(states)


def _all_keeps_for_state(state: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    keeps: list[tuple[int, ...]] = []
    for k1 in range(state[0] + 1):
        for k2 in range(state[1] + 1):
            for k3 in range(state[2] + 1):
                for k4 in range(state[3] + 1):
                    for k5 in range(state[4] + 1):
                        for k6 in range(state[5] + 1):
                            keeps.append((k1, k2, k3, k4, k5, k6))
    return tuple(keeps)


def _compositions6(total: int) -> tuple[tuple[int, int, int, int, int, int], ...]:
    comps: list[tuple[int, int, int, int, int, int]] = []
    for c1 in range(total + 1):
        for c2 in range(total - c1 + 1):
            for c3 in range(total - c1 - c2 + 1):
                for c4 in range(total - c1 - c2 - c3 + 1):
                    for c5 in range(total - c1 - c2 - c3 - c4 + 1):
                        c6 = total - c1 - c2 - c3 - c4 - c5
                        comps.append((c1, c2, c3, c4, c5, c6))
    return tuple(comps)


def _multinomial_probability(counts: tuple[int, ...], probabilities: tuple[float, ...]) -> float:
    n = sum(counts)
    coefficient = comb(n, counts[0])
    remaining = n - counts[0]
    for index in range(1, 5):
        coefficient *= comb(remaining, counts[index])
        remaining -= counts[index]

    probability = float(coefficient)
    for count, chance in zip(counts, probabilities):
        if count:
            probability *= chance ** count
    return probability


def _one_roll_metrics_exact(group_probs: tuple[tuple[float, ...], ...]) -> dict[str, float]:
    # Exact by explicit 6^5 outcomes, preserving per-die biases.
    values: dict[str, float] = {key: 0.0 for key, _ in _ordered_metric_labels()}
    for d1 in FACES:
        p1 = group_probs[0][d1 - 1]
        for d2 in FACES:
            p2 = group_probs[1][d2 - 1]
            for d3 in FACES:
                p3 = group_probs[2][d3 - 1]
                for d4 in FACES:
                    p4 = group_probs[3][d4 - 1]
                    for d5 in FACES:
                        p5 = group_probs[4][d5 - 1]
                        probability = p1 * p2 * p3 * p4 * p5
                        if probability == 0.0:
                            continue
                        counts = [0, 0, 0, 0, 0, 0]
                        counts[d1 - 1] += 1
                        counts[d2 - 1] += 1
                        counts[d3 - 1] += 1
                        counts[d4 - 1] += 1
                        counts[d5 - 1] += 1
                        signal = _metrics_from_counts(tuple(counts))
                        for key in values:
                            values[key] += probability * signal[key]
    return values


def _turn_metrics_3roll_optimal_iid(group_probs: tuple[tuple[float, ...], ...]) -> dict[str, float]:
    # Strategy-aware, up to two rerolls, modeled as i.i.d using the group's mean face distribution.
    avg = tuple(sum(prob[face] for prob in group_probs) / 5.0 for face in range(6))
    states = _all_count_states(5)
    state_index = {state: index for index, state in enumerate(states)}

    metric_keys = [key for key, _ in _ordered_metric_labels()]
    metric_count = len(metric_keys)

    # Terminal values for each state/metric.
    terminal_values: list[list[float]] = []
    for state in states:
        metrics = _metrics_from_counts(state)
        terminal_values.append([metrics[key] for key in metric_keys])

    # Precompute multinomial outcomes and probabilities for reroll counts 0..5.
    outcome_options: dict[int, tuple[tuple[tuple[int, ...], float], ...]] = {}
    for reroll_count in range(6):
        options: list[tuple[tuple[int, ...], float]] = []
        for outcome in _compositions6(reroll_count):
            probability = _multinomial_probability(outcome, avg)
            if probability > 0.0:
                options.append((outcome, probability))
        outcome_options[reroll_count] = tuple(options)

    # For each state and hold action, cache transition probabilities to next states.
    transitions_by_state: list[list[tuple[tuple[int, float], ...]]] = []
    for state in states:
        state_transitions: list[tuple[tuple[int, float], ...]] = []
        for keep in _all_keeps_for_state(state):
            reroll_count = 5 - sum(keep)
            transitions: list[tuple[int, float]] = []
            for outcome, probability in outcome_options[reroll_count]:
                next_state = tuple(keep[index] + outcome[index] for index in range(6))
                transitions.append((state_index[next_state], probability))
            state_transitions.append(tuple(transitions))
        transitions_by_state.append(state_transitions)

    initial_distribution = [
        _multinomial_probability(state, avg)
        for state in states
    ]

    def _dp_step(next_values: list[list[float]]) -> list[list[float]]:
        current_values: list[list[float]] = []
        for state_actions in transitions_by_state:
            best = [0.0] * metric_count
            for action_transitions in state_actions:
                expected = [0.0] * metric_count
                for next_index, probability in action_transitions:
                    row = next_values[next_index]
                    for metric_index in range(metric_count):
                        expected[metric_index] += probability * row[metric_index]
                for metric_index in range(metric_count):
                    if expected[metric_index] > best[metric_index]:
                        best[metric_index] = expected[metric_index]
            current_values.append(best)
        return current_values

    values_with_zero_rerolls = terminal_values
    values_with_one_reroll = _dp_step(values_with_zero_rerolls)
    values_with_two_rerolls = _dp_step(values_with_one_reroll)

    start_values = [0.0] * metric_count
    for state_probability, row in zip(initial_distribution, values_with_two_rerolls):
        for metric_index in range(metric_count):
            start_values[metric_index] += state_probability * row[metric_index]

    return {
        key: start_values[index]
        for index, key in enumerate(metric_keys)
    }


def _distance_from_ideal(group_values: dict[str, float], ideal_values: dict[str, float]) -> float:
    keys = [key for key, _ in _ordered_metric_labels()]
    squared_error_sum = sum((group_values[key] - ideal_values[key]) ** 2 for key in keys)
    return sqrt(squared_error_sum / len(keys))


def _analyze_groups(probabilities_by_die: dict[str, tuple[float, ...]]) -> tuple[GroupOdds, GroupOdds, list[GroupOdds], dict[str, float], dict[str, float]]:
    ideal_iid = tuple(tuple(1.0 / 6.0 for _ in range(6)) for _ in range(5))
    ideal_one_roll = _one_roll_metrics_exact(ideal_iid)
    ideal_turn_3roll = _turn_metrics_3roll_optimal_iid(ideal_iid)

    groups: list[GroupOdds] = []
    for dice_ids in combinations(sorted(probabilities_by_die), 5):
        group_probs = tuple(probabilities_by_die[dice_id] for dice_id in dice_ids)
        one_roll = _one_roll_metrics_exact(group_probs)
        turn_3roll = _turn_metrics_3roll_optimal_iid(group_probs)
        groups.append(
            GroupOdds(
                dice_ids=dice_ids,
                one_roll=one_roll,
                turn_3roll=turn_3roll,
                turn_distance=_distance_from_ideal(turn_3roll, ideal_turn_3roll),
            )
        )

    ranked = sorted(groups, key=lambda item: item.turn_distance)
    return ranked[0], ranked[-1], ranked, ideal_one_roll, ideal_turn_3roll


def _render_delta_bar(best_value: float, worst_value: float, ideal_value: float, width: int = 360) -> str:
    peak = max(abs(best_value - ideal_value), abs(worst_value - ideal_value), 1e-9)
    center = width / 2
    scale = (width * 0.45) / peak
    best_x = center + (best_value - ideal_value) * scale
    worst_x = center + (worst_value - ideal_value) * scale

    return (
        f'<svg viewBox="0 0 {width} 44" role="img" aria-label="Deviation from ideal">'
        f'<line x1="{center:.2f}" y1="6" x2="{center:.2f}" y2="38" stroke="#4f3b2b" stroke-width="1.5" stroke-dasharray="3 3"/>'
        f'<line x1="{center - width * 0.45:.2f}" y1="22" x2="{center + width * 0.45:.2f}" y2="22" stroke="rgba(79,59,43,0.20)" stroke-width="2"/>'
        f'<circle cx="{best_x:.2f}" cy="22" r="6" fill="#2f7a72"/>'
        f'<circle cx="{worst_x:.2f}" cy="22" r="6" fill="#a63f3f"/>'
        '</svg>'
    )


def _render_primary_metric_rows(
    best_group: GroupOdds,
    worst_group: GroupOdds,
    ideal_turn_3roll: dict[str, float],
) -> str:
    rows = ''
    for key, label in _ordered_metric_labels():
        ideal = ideal_turn_3roll[key]
        best = best_group.turn_3roll[key]
        worst = worst_group.turn_3roll[key]
        rows += (
            '<tr>'
            f'<td>{escape(label)}</td>'
            f'<td>{ideal * 100:.4f}%</td>'
            f'<td>{best * 100:.4f}%</td>'
            f'<td>{(best - ideal) * 100:+.4f} pp</td>'
            f'<td>{worst * 100:.4f}%</td>'
            f'<td>{(worst - ideal) * 100:+.4f} pp</td>'
            f'<td>{_render_delta_bar(best, worst, ideal)}</td>'
            '</tr>'
        )
    return rows


def _render_secondary_metric_rows(
    best_group: GroupOdds,
    worst_group: GroupOdds,
    ideal_one_roll: dict[str, float],
) -> str:
    rows = ''
    for key, label in _ordered_metric_labels():
        ideal = ideal_one_roll[key]
        best = best_group.one_roll[key]
        worst = worst_group.one_roll[key]
        rows += (
            '<tr>'
            f'<td>{escape(label)}</td>'
            f'<td>{ideal * 100:.4f}%</td>'
            f'<td>{best * 100:.4f}%</td>'
            f'<td>{worst * 100:.4f}%</td>'
            '</tr>'
        )
    return rows


def _render_dashboard_html(
    best_group: GroupOdds,
    worst_group: GroupOdds,
    ranked_groups: list[GroupOdds],
    ideal_one_roll: dict[str, float],
    ideal_turn_3roll: dict[str, float],
  generated_at: str,
) -> str:
    top_rows = ''.join(
        (
            '<tr>'
            f'<td>{index}</td>'
            f'<td>{escape(_format_group(group.dice_ids))}</td>'
            f'<td>{group.turn_distance:.6f}</td>'
            '</tr>'
        )
        for index, group in enumerate(ranked_groups[:10], start=1)
    )
    bottom_rows = ''.join(
        (
            '<tr>'
            f'<td>{index}</td>'
            f'<td>{escape(_format_group(group.dice_ids))}</td>'
            f'<td>{group.turn_distance:.6f}</td>'
            '</tr>'
        )
        for index, group in enumerate(reversed(ranked_groups[-10:]), start=1)
    )

    primary_rows = _render_primary_metric_rows(best_group, worst_group, ideal_turn_3roll)
    secondary_rows = _render_secondary_metric_rows(best_group, worst_group, ideal_one_roll)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Yahtzee Scorecard Odds Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1f1a17;
      --muted: #6e6258;
      --card: rgba(255, 250, 242, 0.92);
      --line: rgba(79, 59, 43, 0.16);
      --shadow: 0 24px 60px rgba(54, 39, 29, 0.12);
      --good: #2f7a72;
      --bad: #a63f3f;
      --warm: #d06b2d;
      --surface: #f4ecde;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, 'Times New Roman', serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(47, 122, 114, 0.18), transparent 26%),
        radial-gradient(circle at right 20%, rgba(208, 107, 45, 0.18), transparent 22%),
        linear-gradient(180deg, #f7f0e5 0%, #efe3cf 100%);
      min-height: 100vh;
    }}
    main {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 34px 20px 64px;
    }}
    .hero {{
      display: grid;
      gap: 14px;
      margin-bottom: 24px;
    }}
    .eyebrow {{
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 0.8rem;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2.3rem, 5vw, 4.6rem);
      line-height: 0.95;
      letter-spacing: -0.05em;
      max-width: 12ch;
    }}
    .hero p {{
      margin: 0;
      max-width: 82ch;
      line-height: 1.55;
      color: var(--muted);
      font-size: 1.03rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 16px;
      margin: 24px 0 20px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 20px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }}
    .label {{
      display: block;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.8rem;
      margin-bottom: 8px;
    }}
    .value {{
      font-size: clamp(1.5rem, 3vw, 2.35rem);
      line-height: 1.08;
    }}
    .value small {{
      display: block;
      margin-top: 8px;
      font-size: 0.93rem;
      color: var(--muted);
    }}
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 1.35rem;
      letter-spacing: -0.03em;
    }}
    .section {{
      margin-top: 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 10px 8px;
      text-align: left;
      vertical-align: middle;
      font-size: 0.95rem;
    }}
    th {{
      color: var(--muted);
      font-weight: normal;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.78rem;
    }}
    .note {{
      color: var(--muted);
      line-height: 1.5;
      margin: 0;
    }}
    .swatch {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-right: 14px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .dot {{
      width: 12px;
      height: 12px;
      border-radius: 99px;
      display: inline-block;
    }}
    @media (max-width: 1000px) {{
      .two-col {{
        grid-template-columns: 1fr;
      }}
    }}
    @media (max-width: 700px) {{
      main {{ padding: 24px 14px 44px; }}
      .card {{ padding: 16px; border-radius: 18px; }}
      th, td {{ font-size: 0.9rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <span class="eyebrow">Yahtzee Odds Dashboard</span>
      <h1>Ideal vs Your Dice</h1>
      <p>Generated: {escape(generated_at)}</p>
      <p>This dashboard is now prioritized around full-turn Yahtzee odds: initial roll plus up to two rerolls using an optimal hold policy for each scorecard event. Rankings use turn-based odds. One-roll probabilities are included as a secondary reference table.</p>
      <p>Turn model note: to keep optimization tractable across all 252 groups and all events, each five-die group is modeled as i.i.d per roll using that group's mean face probabilities, then solved exactly with dynamic programming over hold decisions.</p>
    </section>

    <section class="grid">
      <article class="card">
        <span class="label">Best 5-Die Group (Turn Odds)</span>
        <div class="value">{escape(_format_group(best_group.dice_ids))}<small>distance from ideal: {best_group.turn_distance:.6f}</small></div>
      </article>
      <article class="card">
        <span class="label">Worst 5-Die Group (Turn Odds)</span>
        <div class="value">{escape(_format_group(worst_group.dice_ids))}<small>distance from ideal: {worst_group.turn_distance:.6f}</small></div>
      </article>
      <article class="card">
        <span class="label">Distance Gap</span>
        <div class="value">{(worst_group.turn_distance - best_group.turn_distance):.6f}<small>worst minus best (RMS probability error)</small></div>
      </article>
      <article class="card">
        <span class="label">Groups Evaluated</span>
        <div class="value">{len(ranked_groups)}<small>all combinations of 5 from 10 dice</small></div>
      </article>
    </section>

    <section class="two-col section">
      <article class="card">
        <h2>Closest Groups To Ideal (Turn Odds)</h2>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Dice</th>
              <th>Distance</th>
            </tr>
          </thead>
          <tbody>
            {top_rows}
          </tbody>
        </table>
      </article>
      <article class="card">
        <h2>Furthest Groups From Ideal (Turn Odds)</h2>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Dice</th>
              <th>Distance</th>
            </tr>
          </thead>
          <tbody>
            {bottom_rows}
          </tbody>
        </table>
      </article>
    </section>

    <section class="section card">
      <h2>Primary: Full-Turn Odds (Initial + Up To 2 Rerolls)</h2>
      <p class="note">Values are event probabilities at the end of a Yahtzee turn with optimal hold choices for each event. Delta columns are percentage-point differences from ideal. Sparkline markers: <span class="swatch"><span class="dot" style="background:#2f7a72"></span>best group</span><span class="swatch"><span class="dot" style="background:#a63f3f"></span>worst group</span><span class="swatch"><span class="dot" style="background:#4f3b2b"></span>ideal center line</span></p>
      <table>
        <thead>
          <tr>
            <th>Event</th>
            <th>Ideal</th>
            <th>Best Group</th>
            <th>Best Delta</th>
            <th>Worst Group</th>
            <th>Worst Delta</th>
            <th>Deviation Plot</th>
          </tr>
        </thead>
        <tbody>
          {primary_rows}
        </tbody>
      </table>
    </section>

    <section class="section card">
      <h2>Secondary: Exact One-Roll Odds</h2>
      <p class="note">Single-roll probabilities are shown for context only. This section is no longer used for group ranking.</p>
      <table>
        <thead>
          <tr>
            <th>Event</th>
            <th>Ideal</th>
            <th>Best Group</th>
            <th>Worst Group</th>
          </tr>
        </thead>
        <tbody>
          {secondary_rows}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
'''


def build_dashboard_html() -> str:
  rows_by_die = _load_rows()
  if len(rows_by_die) != 10:
    raise ValueError(f'Expected 10 Yahtzee dice, found {len(rows_by_die)}')

  probabilities_by_die = _face_probabilities(rows_by_die)
  best_group, worst_group, ranked_groups, ideal_one_roll, ideal_turn_3roll = _analyze_groups(probabilities_by_die)
  generated_at = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
  return _render_dashboard_html(best_group, worst_group, ranked_groups, ideal_one_roll, ideal_turn_3roll, generated_at)


def main() -> None:
  parser = argparse.ArgumentParser(
    description='Generate an HTML dashboard comparing ideal Yahtzee scorecard odds to best/worst five-die groups from tested dice.'
  )
  parser.add_argument(
    '--html-output',
    type=Path,
    default=DEFAULT_HTML_OUTPUT_PATH,
    help='Path to the HTML dashboard to generate.',
  )
  args = parser.parse_args()

  html = build_dashboard_html()
  args.html_output.parent.mkdir(parents=True, exist_ok=True)
  args.html_output.write_text(html, encoding='utf-8')
  print(f'Wrote HTML dashboard to {args.html_output}')


if __name__ == '__main__':
  main()
