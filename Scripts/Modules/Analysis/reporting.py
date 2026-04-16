from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from html import escape
import math
from pathlib import Path


_EPSILON = 1e-14
_SMALL_NUMBER = 1e-30
_MAX_ITERATIONS = 200


@dataclass(frozen=True)
class OutcomeFrequency:
    face: int
    count: int
    expected_count: float
    percentage: float


@dataclass(frozen=True)
class DiceAnalysisReport:
    dice_id: str
    dice_sides: int
    sample_count: int
    first_timestamp: str
    last_timestamp: str
    mean_roll: float
    expected_mean_roll: float
    chi_square_statistic: float
    p_value: float
    longest_streak_value: int
    longest_streak_length: int
    frequencies: tuple[OutcomeFrequency, ...]
    ordered_rolls: tuple[int, ...]


def _regularized_gamma_p_series(a: float, x: float) -> float:
    gln = math.lgamma(a)
    term = 1.0 / a
    total = term

    for iteration in range(1, _MAX_ITERATIONS + 1):
        term *= x / (a + iteration)
        total += term
        if abs(term) <= abs(total) * _EPSILON:
            break

    return total * math.exp(-x + (a * math.log(x)) - gln)


def _regularized_gamma_q_continued_fraction(a: float, x: float) -> float:
    gln = math.lgamma(a)
    b = x + 1.0 - a
    c = 1.0 / _SMALL_NUMBER
    d = 1.0 / max(b, _SMALL_NUMBER)
    h = d

    for iteration in range(1, _MAX_ITERATIONS + 1):
        an = -iteration * (iteration - a)
        b += 2.0
        d = an * d + b
        if abs(d) < _SMALL_NUMBER:
            d = _SMALL_NUMBER
        c = b + (an / c)
        if abs(c) < _SMALL_NUMBER:
            c = _SMALL_NUMBER
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) <= _EPSILON:
            break

    return math.exp(-x + (a * math.log(x)) - gln) * h


def chi_square_p_value(statistic: float, degrees_of_freedom: int) -> float:
    if degrees_of_freedom <= 0:
        raise ValueError('degrees_of_freedom must be positive')
    if statistic < 0:
        raise ValueError('statistic must be non-negative')
    if statistic == 0:
        return 1.0

    a = degrees_of_freedom / 2.0
    x = statistic / 2.0
    if x < a + 1.0:
        return max(0.0, min(1.0, 1.0 - _regularized_gamma_p_series(a, x)))
    return max(0.0, min(1.0, _regularized_gamma_q_continued_fraction(a, x)))


def _longest_streak(values: list[int]) -> tuple[int, int]:
    if not values:
        return 0, 0

    best_value = values[0]
    best_length = 1
    current_value = values[0]
    current_length = 1

    for value in values[1:]:
        if value == current_value:
            current_length += 1
        else:
            current_value = value
            current_length = 1

        if current_length > best_length:
            best_value = current_value
            best_length = current_length

    return best_value, best_length


def _normalize_rows(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda row: row['timestamp'])


def analyze_results(dice_id: str, rows: list[dict], dice_sides: int) -> DiceAnalysisReport:
    if not rows:
        raise ValueError('rows must not be empty')
    if dice_sides < 2:
        raise ValueError('dice_sides must be at least 2')

    normalized_rows = _normalize_rows(rows)
    ordered_rolls = [int(row['dice_result']) for row in normalized_rows]

    invalid_rolls = [roll for roll in ordered_rolls if roll < 1 or roll > dice_sides]
    if invalid_rolls:
        raise ValueError(f'Found roll values outside 1..{dice_sides}: {invalid_rolls}')

    sample_count = len(ordered_rolls)
    expected_count = sample_count / dice_sides
    counts = Counter(ordered_rolls)
    frequencies = tuple(
        OutcomeFrequency(
            face=face,
            count=counts.get(face, 0),
            expected_count=expected_count,
            percentage=(counts.get(face, 0) / sample_count) * 100,
        )
        for face in range(1, dice_sides + 1)
    )
    chi_square_statistic = sum(
        ((frequency.count - frequency.expected_count) ** 2) / frequency.expected_count
        for frequency in frequencies
    )
    streak_value, streak_length = _longest_streak(ordered_rolls)

    return DiceAnalysisReport(
        dice_id=str(dice_id),
        dice_sides=dice_sides,
        sample_count=sample_count,
        first_timestamp=normalized_rows[0]['timestamp'],
        last_timestamp=normalized_rows[-1]['timestamp'],
        mean_roll=sum(ordered_rolls) / sample_count,
        expected_mean_roll=(dice_sides + 1) / 2,
        chi_square_statistic=chi_square_statistic,
        p_value=chi_square_p_value(chi_square_statistic, dice_sides - 1),
        longest_streak_value=streak_value,
        longest_streak_length=streak_length,
        frequencies=frequencies,
        ordered_rolls=tuple(ordered_rolls),
    )


def build_summary_lines(report: DiceAnalysisReport) -> list[str]:
    expected_per_face = report.sample_count / report.dice_sides
    has_adequate_sample = expected_per_face >= 5.0
    if not has_adequate_sample:
        interpretation = 'Interpretation: expected count per face is below 5; chi-square approximation may be unreliable.'
    elif report.p_value < 0.05:
        interpretation = 'Interpretation: evidence of non-uniform outcomes at alpha=0.05.'
    else:
        interpretation = 'Interpretation: no evidence of non-uniform outcomes at alpha=0.05.'

    summary = [
        '',
        '=' * 50,
        f'Dice ID: {report.dice_id}',
        f'Sides: {report.dice_sides}',
        f'Samples analyzed: {report.sample_count}',
        f'Expected count per face: {expected_per_face:.2f}',
        f'Sample adequacy (expected >= 5 per face): {"PASS" if has_adequate_sample else "LOW"}',
        f'Time range: {report.first_timestamp} -> {report.last_timestamp}',
        f'Observed mean roll: {report.mean_roll:.3f} (expected {report.expected_mean_roll:.3f})',
        f'Chi-square statistic: {report.chi_square_statistic:.4f}',
        f'Chi-square p-value: {report.p_value:.4f}',
        interpretation,
        f'Longest streak: face {report.longest_streak_value} repeated {report.longest_streak_length} times',
        'Observed face counts:',
    ]
    summary.extend(
        f'  {frequency.face}: {frequency.count} ({frequency.percentage:.1f}%)'
        for frequency in report.frequencies
    )
    summary.append('=' * 50)
    return summary


def _render_distribution_svg(report: DiceAnalysisReport) -> str:
    width = 860
    height = 340
    margin_left = 72
    margin_right = 28
    margin_top = 28
    margin_bottom = 56
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    bar_gap = 18
    bar_width = (chart_width - (bar_gap * (report.dice_sides - 1))) / report.dice_sides
    max_count = max(max(frequency.count for frequency in report.frequencies), report.sample_count / report.dice_sides, 1)
    expected_y = margin_top + chart_height - ((report.sample_count / report.dice_sides) / max_count) * chart_height

    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Observed face frequencies">',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="#fffaf2"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#4f3b2b" stroke-width="2"/>',
        f'<line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="#4f3b2b" stroke-width="2"/>',
        f'<line x1="{margin_left}" y1="{expected_y:.2f}" x2="{margin_left + chart_width}" y2="{expected_y:.2f}" stroke="#d06b2d" stroke-width="2" stroke-dasharray="8 6"/>',
        f'<text x="{margin_left + chart_width - 4}" y="{expected_y - 8:.2f}" text-anchor="end" fill="#d06b2d" font-size="13">Expected count</text>',
    ]

    for index, frequency in enumerate(report.frequencies):
        x = margin_left + index * (bar_width + bar_gap)
        bar_height = (frequency.count / max_count) * chart_height
        y = margin_top + chart_height - bar_height
        parts.extend([
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" rx="12" fill="#2f7a72"/>',
            f'<text x="{x + bar_width / 2:.2f}" y="{y - 8:.2f}" text-anchor="middle" fill="#21312d" font-size="14">{frequency.count}</text>',
            f'<text x="{x + bar_width / 2:.2f}" y="{margin_top + chart_height + 28}" text-anchor="middle" fill="#4f3b2b" font-size="14">{frequency.face}</text>',
        ])

    parts.append('</svg>')
    return ''.join(parts)


def _render_recent_rolls(report: DiceAnalysisReport) -> str:
  if report.sample_count > 1000:
    return (
      '<p class="muted-note">'
      'Recent rolls are hidden for large sample sizes. '
      'Use the distribution chart and frequency table for interpretation.'
      '</p>'
    )

    recent = report.ordered_rolls[-12:]
    if not recent:
        return ''

    cells = ''.join(
        f'<span class="roll-chip">{value}</span>'
        for value in recent
    )
    return f'<div class="roll-strip">{cells}</div>'


def _render_report_html(report: DiceAnalysisReport) -> str:
    expected_per_face = report.sample_count / report.dice_sides
    has_adequate_sample = expected_per_face >= 5.0
    if not has_adequate_sample:
        interpretation = 'Expected count per face is below 5; chi-square approximation may be unreliable.'
        callout_state = 'warning'
    elif report.p_value < 0.05:
        interpretation = 'Evidence of non-uniform outcomes at alpha=0.05.'
        callout_state = 'alert'
    else:
        interpretation = 'No evidence of non-uniform outcomes at alpha=0.05.'
        callout_state = 'success'

    frequencies = ''.join(
        (
            '<tr>'
            f'<td>{frequency.face}</td>'
            f'<td>{frequency.count}</td>'
            f'<td>{frequency.expected_count:.2f}</td>'
            f'<td>{frequency.percentage:.2f}%</td>'
            '</tr>'
        )
        for frequency in report.frequencies
    )
    distribution_svg = _render_distribution_svg(report)
    recent_rolls = _render_recent_rolls(report)
    recent_rolls_label = 'Recent rolls' if report.sample_count <= 1000 else 'Recent rolls (scaled view)'
    title = escape(f'Dice {report.dice_id} analysis report')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1f1a17;
      --muted: #6e6258;
      --card: rgba(255, 250, 242, 0.88);
      --accent: #2f7a72;
      --accent-warm: #d06b2d;
      --surface: #f4ecde;
      --line: rgba(79, 59, 43, 0.16);
      --shadow: 0 24px 60px rgba(54, 39, 29, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, 'Times New Roman', serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(47, 122, 114, 0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(208, 107, 45, 0.16), transparent 24%),
        linear-gradient(180deg, #f7f0e5 0%, #efe3cf 100%);
      min-height: 100vh;
    }}
    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 40px 20px 64px;
    }}
    .hero {{
      display: grid;
      gap: 18px;
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2.2rem, 5vw, 4rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
    }}
    p {{
      margin: 0;
      color: var(--muted);
      font-size: 1.05rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin: 28px 0;
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
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 10px;
    }}
    .value {{
      font-size: clamp(1.8rem, 4vw, 2.6rem);
      line-height: 1;
    }}
    .value small {{
      display: block;
      margin-top: 8px;
      font-size: 0.95rem;
      color: var(--muted);
    }}
    .wide {{
      margin-top: 18px;
    }}
    .callout {{
      margin-top: 18px;
    }}
    .callout--warning {{
      border-left: 6px solid var(--accent-warm);
      background: rgba(208, 107, 45, 0.08);
    }}
    .callout--alert {{
      border-left: 6px solid #a63f3f;
      background: rgba(166, 63, 63, 0.10);
    }}
    .callout--success {{
      border-left: 6px solid var(--accent);
      background: rgba(47, 122, 114, 0.10);
    }}
    .callout p {{
      color: var(--ink);
      line-height: 1.45;
      margin-top: 10px;
    }}
    .muted-note {{
      color: var(--muted);
      font-style: italic;
      margin-top: 12px;
    }}
    .chart {{
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
    }}
    th, td {{
      padding: 12px 10px;
      text-align: left;
      border-bottom: 1px solid var(--line);
    }}
    th {{
      color: var(--muted);
      font-weight: normal;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.8rem;
    }}
    .roll-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    .roll-chip {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: var(--surface);
      border: 1px solid var(--line);
      font-size: 1rem;
    }}
    @media (max-width: 700px) {{
      main {{ padding: 28px 14px 48px; }}
      .card {{ padding: 16px; border-radius: 18px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <p>Dice analysis report</p>
      <h1>Die {escape(report.dice_id)} over {report.sample_count} rolls</h1>
      <p>{escape(report.first_timestamp)} through {escape(report.last_timestamp)}</p>
    </section>
    <section class="grid">
      <article class="card">
        <span class="label">Mean roll</span>
        <div class="value">{report.mean_roll:.3f}<small>Expected {report.expected_mean_roll:.3f}</small></div>
      </article>
      <article class="card">
        <span class="label">Chi-square</span>
        <div class="value">{report.chi_square_statistic:.4f}<small>p-value {report.p_value:.4f}</small></div>
      </article>
      <article class="card">
        <span class="label">Longest streak</span>
        <div class="value">{report.longest_streak_length}<small>Face {report.longest_streak_value}</small></div>
      </article>
      <article class="card">
        <span class="label">Die shape</span>
        <div class="value">d{report.dice_sides}<small>{expected_per_face:.2f} expected per face</small></div>
      </article>
    </section>
    <section class="card callout callout--{callout_state}">
      <span class="label">Statistical interpretation</span>
      <p>Sample adequacy (expected &gt;= 5 per face): <strong>{'PASS' if has_adequate_sample else 'LOW'}</strong></p>
      <p>{interpretation}</p>
    </section>
    <section class="card wide">
      <span class="label">Observed distribution</span>
      <div class="chart">{distribution_svg}</div>
    </section>
    <section class="card wide">
      <span class="label">Face frequency table</span>
      <table>
        <thead>
          <tr>
            <th>Face</th>
            <th>Observed</th>
            <th>Expected</th>
            <th>Share</th>
          </tr>
        </thead>
        <tbody>
          {frequencies}
        </tbody>
      </table>
      <span class="label" style="margin-top: 18px; display: block;">{recent_rolls_label}</span>
      {recent_rolls}
    </section>
  </main>
</body>
</html>
'''


def write_report(report: DiceAnalysisReport, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'results.html'
    output_path.write_text(_render_report_html(report), encoding='utf-8')
    return output_path