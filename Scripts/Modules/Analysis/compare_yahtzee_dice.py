from __future__ import annotations

from dataclasses import dataclass
from html import escape
from itertools import combinations
from math import log2
from pathlib import Path
import argparse
import sqlite3

from Scripts.Modules.Analysis.reporting import analyze_results
from Scripts.Modules.Database.database import DBPath


YAHTZEE_PREFIX = 'six_sided_yahtzee_'
DEFAULT_MARKDOWN_OUTPUT_PATH = Path('Scripts/Modules/Database/Captures/yahtzee_comparison_report.md')
DEFAULT_HTML_OUTPUT_PATH = Path('Scripts/Modules/Database/Captures/yahtzee_comparison_dashboard.html')
EXPECTED_REPEAT_RATE = 1.0 / 6.0
IDEAL_ENTROPY_BITS = log2(6)


@dataclass(frozen=True)
class DieMetrics:
    dice_id: str
    sample_count: int
    chi_square: float
    p_value: float
    tvd: float
    max_abs_deviation: float
    entropy_bits: float
    entropy_gap_bits: float
    mean_roll: float
    mean_delta: float
    repeat_rate: float
    repeat_delta: float
    longest_streak_value: int
    longest_streak_length: int
    counts: tuple[int, ...]
    deviations: tuple[float, ...]
    most_overrepresented_face: int
    most_overrepresented_delta: float
    most_underrepresented_face: int
    most_underrepresented_delta: float


@dataclass(frozen=True)
class GroupMetrics:
    dice_ids: tuple[str, ...]
    pooled_metrics: DieMetrics
    average_individual_chi_square: float
    average_individual_tvd: float


@dataclass(frozen=True)
class ComparisonSummary:
    ranked_dice: tuple[DieMetrics, ...]
    ranked_groups: tuple[GroupMetrics, ...]
    all_dice: DieMetrics


def _load_rows(db_path: Path, dice_prefix: str) -> dict[str, list[dict]]:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            '''
            SELECT dice_id, timestamp, dice_sides, dice_result, image
            FROM test_results
            WHERE dice_id LIKE ?
            ORDER BY dice_id, timestamp
            ''',
            (f'{dice_prefix}%',),
        ).fetchall()
    finally:
        connection.close()

    by_die: dict[str, list[dict]] = {}
    for row in rows:
        by_die.setdefault(str(row['dice_id']), []).append(dict(row))
    return by_die


def _compute_metrics(dice_id: str, rows: list[dict]) -> DieMetrics:
    report = analyze_results(dice_id=dice_id, rows=rows, dice_sides=6)
    counts_by_face = {frequency.face: frequency.count for frequency in report.frequencies}
    probabilities = {face: counts_by_face[face] / report.sample_count for face in range(1, 7)}
    deviations = {face: probabilities[face] - (1.0 / 6.0) for face in range(1, 7)}
    repeated_pairs = sum(
        1 for previous, current in zip(report.ordered_rolls, report.ordered_rolls[1:]) if previous == current
    )
    repeat_rate = repeated_pairs / (report.sample_count - 1)
    entropy_bits = -sum(probability * log2(probability) for probability in probabilities.values() if probability > 0.0)
    most_overrepresented_face = max(deviations, key=deviations.get)
    most_underrepresented_face = min(deviations, key=deviations.get)

    return DieMetrics(
        dice_id=dice_id,
        sample_count=report.sample_count,
        chi_square=report.chi_square_statistic,
        p_value=report.p_value,
        tvd=0.5 * sum(abs(deviation) for deviation in deviations.values()),
        max_abs_deviation=max(abs(deviation) for deviation in deviations.values()),
        entropy_bits=entropy_bits,
        entropy_gap_bits=IDEAL_ENTROPY_BITS - entropy_bits,
        mean_roll=report.mean_roll,
        mean_delta=report.mean_roll - report.expected_mean_roll,
        repeat_rate=repeat_rate,
        repeat_delta=repeat_rate - EXPECTED_REPEAT_RATE,
        longest_streak_value=report.longest_streak_value,
        longest_streak_length=report.longest_streak_length,
        counts=tuple(counts_by_face[face] for face in range(1, 7)),
        deviations=tuple(deviations[face] for face in range(1, 7)),
        most_overrepresented_face=most_overrepresented_face,
        most_overrepresented_delta=deviations[most_overrepresented_face],
        most_underrepresented_face=most_underrepresented_face,
        most_underrepresented_delta=deviations[most_underrepresented_face],
    )


def _rank_dice(rows_by_die: dict[str, list[dict]]) -> list[DieMetrics]:
    metrics = [_compute_metrics(dice_id, rows) for dice_id, rows in sorted(rows_by_die.items())]
    return sorted(metrics, key=lambda item: (item.chi_square, item.tvd, item.entropy_gap_bits))


def _rank_groups(rows_by_die: dict[str, list[dict]], ranked_dice: list[DieMetrics]) -> list[GroupMetrics]:
    metrics_by_die = {item.dice_id: item for item in ranked_dice}
    groups: list[GroupMetrics] = []

    for combo in combinations(sorted(rows_by_die), 5):
        pooled_rows: list[dict] = []
        for dice_id in combo:
            pooled_rows.extend(rows_by_die[dice_id])

        pooled_metrics = _compute_metrics('+'.join(combo), pooled_rows)
        groups.append(
            GroupMetrics(
                dice_ids=combo,
                pooled_metrics=pooled_metrics,
                average_individual_chi_square=sum(metrics_by_die[dice_id].chi_square for dice_id in combo) / len(combo),
                average_individual_tvd=sum(metrics_by_die[dice_id].tvd for dice_id in combo) / len(combo),
            )
        )

    return sorted(
        groups,
        key=lambda item: (
            item.pooled_metrics.chi_square,
            item.pooled_metrics.tvd,
            item.pooled_metrics.entropy_gap_bits,
        ),
    )


def _pool_all_rows(rows_by_die: dict[str, list[dict]]) -> list[dict]:
    pooled_rows: list[dict] = []
    for rows in rows_by_die.values():
        pooled_rows.extend(rows)
    return pooled_rows


def _format_die_name(dice_id: str) -> str:
    return dice_id.removeprefix(YAHTZEE_PREFIX).replace('_', ' ')


def _format_group(group: GroupMetrics) -> str:
    return ', '.join(_format_die_name(dice_id) for dice_id in group.dice_ids)


def _build_summary() -> ComparisonSummary:
    rows_by_die = _load_rows(DBPath, YAHTZEE_PREFIX)
    if len(rows_by_die) != 10:
        raise ValueError(f'Expected 10 Yahtzee dice, found {len(rows_by_die)}')

    ranked_dice = _rank_dice(rows_by_die)
    ranked_groups = _rank_groups(rows_by_die, ranked_dice)
    all_dice = _compute_metrics('all_yahtzee_dice', _pool_all_rows(rows_by_die))
    return ComparisonSummary(
        ranked_dice=tuple(ranked_dice),
        ranked_groups=tuple(ranked_groups),
        all_dice=all_dice,
    )


def _summary_highlights(summary: ComparisonSummary) -> dict[str, DieMetrics | GroupMetrics | tuple[str, ...] | float]:
    ranked_dice = summary.ranked_dice
    ranked_groups = summary.ranked_groups
    best_individual_five = tuple(item.dice_id for item in ranked_dice[:5])
    best_pooled_group = ranked_groups[0]
    best_individual_group = next(group for group in ranked_groups if group.dice_ids == tuple(sorted(best_individual_five)))
    worst_pooled_group = ranked_groups[-1]

    chi_reduction = 1.0 - (best_pooled_group.pooled_metrics.chi_square / best_individual_group.pooled_metrics.chi_square)
    return {
        'best_individual_five': best_individual_five,
        'best_pooled_group': best_pooled_group,
        'best_individual_group': best_individual_group,
        'worst_pooled_group': worst_pooled_group,
        'most_random_die': ranked_dice[0],
        'least_random_die': ranked_dice[-1],
        'closest_mean_die': min(ranked_dice, key=lambda item: abs(item.mean_delta)),
        'lowest_repeat_die': min(ranked_dice, key=lambda item: item.repeat_rate),
        'highest_repeat_die': max(ranked_dice, key=lambda item: item.repeat_rate),
        'longest_streak_die': max(ranked_dice, key=lambda item: item.longest_streak_length),
        'chi_reduction': chi_reduction,
    }


def _render_markdown_report(summary: ComparisonSummary) -> str:
    ranked_dice = list(summary.ranked_dice)
    ranked_groups = list(summary.ranked_groups)
    all_dice = summary.all_dice
    highlights = _summary_highlights(summary)

    best_pooled_group = highlights['best_pooled_group']
    best_individual_group = highlights['best_individual_group']
    worst_pooled_group = highlights['worst_pooled_group']
    most_random_die = highlights['most_random_die']
    least_random_die = highlights['least_random_die']
    closest_mean_die = highlights['closest_mean_die']
    lowest_repeat_die = highlights['lowest_repeat_die']
    highest_repeat_die = highlights['highest_repeat_die']
    longest_streak_die = highlights['longest_streak_die']
    chi_reduction = highlights['chi_reduction']

    lines = [
        '# Yahtzee Dice Comparison Report',
        '',
        'This report compares the ten `six_sided_yahtzee_*` dice stored in the project database and ranks them by how close their observed face distribution is to a fair d6.',
        '',
        '## Dataset',
        '',
        f'- Dice compared: {len(ranked_dice)}',
        f'- Rolls per die: {ranked_dice[0].sample_count}',
        f'- Total rolls analyzed: {all_dice.sample_count}',
        '- Primary ranking metric: chi-square goodness-of-fit to a uniform d6 distribution',
        '- Supporting metrics: p-value, total variation distance (TVD), entropy gap, mean shift, repeat rate, and longest streak',
        '- Group-of-5 ranking metric: pooled chi-square/TVD across all rolls from the five selected dice',
        '- Caveat: the group ranking measures pooled balance, not physical independence between dice',
        '',
        '## Executive Summary',
        '',
        f'- Closest single die to random: `{_format_die_name(most_random_die.dice_id)}` with chi-square {most_random_die.chi_square:.3f} and p-value {most_random_die.p_value:.3f}.',
        f'- Weakest single die in this sample: `{_format_die_name(least_random_die.dice_id)}` with chi-square {least_random_die.chi_square:.3f} and p-value {least_random_die.p_value:.3f}.',
        f'- Best five-die group by pooled fairness: `{_format_group(best_pooled_group)}` with pooled chi-square {best_pooled_group.pooled_metrics.chi_square:.3f}, TVD {best_pooled_group.pooled_metrics.tvd:.4f}, and p-value {best_pooled_group.pooled_metrics.p_value:.3f}.',
        f'- The naive "pick the five best individual dice" set is `{_format_group(best_individual_group)}`. Its pooled chi-square is {best_individual_group.pooled_metrics.chi_square:.3f}, so the best pooled group improves that by {chi_reduction * 100:.1f}%.',
        f'- All ten dice pooled together still look reasonably balanced: chi-square {all_dice.chi_square:.3f}, p-value {all_dice.p_value:.3f}, TVD {all_dice.tvd:.4f}.',
        '',
        '## Ranked Single Dice',
        '',
        '| Rank | Die | Chi-square | p-value | TVD | Entropy gap (bits) | Mean | Repeat rate | Longest streak | Strongest bias |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |',
    ]

    for rank, metrics in enumerate(ranked_dice, start=1):
        bias_summary = (
            f'+{metrics.most_overrepresented_face} {metrics.most_overrepresented_delta * 100:+.2f} pp; '
            f'-{metrics.most_underrepresented_face} {metrics.most_underrepresented_delta * 100:+.2f} pp'
        )
        lines.append(
            '| '
            f'{rank} | `{_format_die_name(metrics.dice_id)}` | {metrics.chi_square:.3f} | {metrics.p_value:.3f} '
            f'| {metrics.tvd:.4f} | {metrics.entropy_gap_bits:.6f} | {metrics.mean_roll:.3f} '
            f'| {metrics.repeat_rate * 100:.2f}% | {metrics.longest_streak_length}x face {metrics.longest_streak_value} | {bias_summary} |'
        )

    lines.extend([
        '',
        '## Best Five-Die Groups',
        '',
        '| Rank | Dice | Pooled chi-square | p-value | TVD | Mean | Most over/underrepresented faces |',
        '| --- | --- | ---: | ---: | ---: | ---: | --- |',
    ])

    for rank, group in enumerate(ranked_groups[:5], start=1):
        pooled = group.pooled_metrics
        bias_summary = (
            f'+{pooled.most_overrepresented_face} {pooled.most_overrepresented_delta * 100:+.2f} pp; '
            f'-{pooled.most_underrepresented_face} {pooled.most_underrepresented_delta * 100:+.2f} pp'
        )
        lines.append(
            '| '
            f'{rank} | `{_format_group(group)}` | {pooled.chi_square:.3f} | {pooled.p_value:.3f} '
            f'| {pooled.tvd:.4f} | {pooled.mean_roll:.3f} | {bias_summary} |'
        )

    lines.extend([
        '',
        '## Interesting Metrics',
        '',
        f'- Closest to the expected mean roll of 3.5: `{_format_die_name(closest_mean_die.dice_id)}` at {closest_mean_die.mean_roll:.3f}.',
        f'- Lowest repeat rate: `{_format_die_name(lowest_repeat_die.dice_id)}` at {lowest_repeat_die.repeat_rate * 100:.2f}% versus the ideal 16.67%.',
        f'- Highest repeat rate: `{_format_die_name(highest_repeat_die.dice_id)}` at {highest_repeat_die.repeat_rate * 100:.2f}%.',
        f'- Longest run of identical faces: `{_format_die_name(longest_streak_die.dice_id)}` with {longest_streak_die.longest_streak_length} consecutive `{longest_streak_die.longest_streak_value}`s.',
        f'- Only one die crosses the common alpha=0.05 rejection threshold on its own: `{_format_die_name(least_random_die.dice_id)}` (p-value {least_random_die.p_value:.3f}).',
        f'- The best pooled group includes `{_format_die_name(ranked_dice[5].dice_id)}` even though it ranks sixth individually. Its biases complement the top dice better than `{_format_die_name(ranked_dice[4].dice_id)}` does.',
        '',
        '## Worst Five-Die Group',
        '',
        f'- Worst pooled set: `{_format_group(worst_pooled_group)}`.',
        f'- Pooled chi-square: {worst_pooled_group.pooled_metrics.chi_square:.3f}',
        f'- Pooled p-value: {worst_pooled_group.pooled_metrics.p_value:.4f}',
        f'- Pooled TVD: {worst_pooled_group.pooled_metrics.tvd:.4f}',
        '',
        '## All Ten Dice Pooled',
        '',
        f'- Chi-square: {all_dice.chi_square:.3f}',
        f'- p-value: {all_dice.p_value:.3f}',
        f'- TVD: {all_dice.tvd:.4f}',
        f'- Mean roll: {all_dice.mean_roll:.4f}',
        f'- Aggregate bias: +face {all_dice.most_overrepresented_face} {all_dice.most_overrepresented_delta * 100:+.2f} pp, -face {all_dice.most_underrepresented_face} {all_dice.most_underrepresented_delta * 100:+.2f} pp',
        '',
        '## Recommendation',
        '',
        f'- If you want the single best die, pick `{_format_die_name(most_random_die.dice_id)}`.',
        f'- If you want the most balanced set of five from the ten tested dice, use `{_format_group(best_pooled_group)}`.',
        '- If you want a conservative shortlist for future re-testing, focus on dice `9` and `2` first, because they show the strongest single-die departures from uniformity in this sample.',
        '',
    ])
    return '\n'.join(lines)


def _format_pp(value: float) -> str:
        return f'{value * 100:+.2f} pp'


def _chart_bar_fill(index: int, total: int) -> str:
        if index == 0:
                return '#2f7a72'
        if index == total - 1:
                return '#a63f3f'
        return '#d06b2d'


def _render_single_die_rank_svg(ranked_dice: tuple[DieMetrics, ...]) -> str:
        width = 980
        height = 520
        margin_left = 170
        margin_right = 70
        margin_top = 48
        margin_bottom = 44
        chart_width = width - margin_left - margin_right
        row_gap = 12
        bar_height = 32
        max_value = max(die.chi_square for die in ranked_dice) * 1.1
        chart_height = (bar_height + row_gap) * len(ranked_dice) - row_gap

        parts = [
                f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Single-die chi-square rankings">',
                f'<rect x="0" y="0" width="{width}" height="{height}" rx="24" fill="#fffaf2"/>',
                f'<text x="{margin_left}" y="28" fill="#1f1a17" font-size="22" font-weight="700">Single-die chi-square ranking</text>',
                f'<text x="{margin_left}" y="46" fill="#6e6258" font-size="13">Lower is better. Redder bars indicate weaker fit to a fair d6.</text>',
        ]

        for tick in range(6):
                value = max_value * tick / 5
                x = margin_left + (value / max_value) * chart_width
                parts.append(f'<line x1="{x:.2f}" y1="{margin_top}" x2="{x:.2f}" y2="{margin_top + chart_height}" stroke="rgba(79,59,43,0.12)" stroke-width="1"/>')
                parts.append(f'<text x="{x:.2f}" y="{margin_top + chart_height + 24}" text-anchor="middle" fill="#6e6258" font-size="12">{value:.1f}</text>')

        for index, die in enumerate(ranked_dice):
                y = margin_top + index * (bar_height + row_gap)
                bar_width = (die.chi_square / max_value) * chart_width
                fill = _chart_bar_fill(index, len(ranked_dice))
                parts.extend([
                        f'<text x="{margin_left - 12}" y="{y + 22}" text-anchor="end" fill="#1f1a17" font-size="14">Die {_format_die_name(die.dice_id)}</text>',
                        f'<rect x="{margin_left}" y="{y}" width="{bar_width:.2f}" height="{bar_height}" rx="10" fill="{fill}" opacity="0.92"/>',
                        f'<text x="{margin_left + bar_width + 10:.2f}" y="{y + 22}" fill="#1f1a17" font-size="13">{die.chi_square:.3f} | p={die.p_value:.3f}</text>',
                ])

        parts.append('</svg>')
        return ''.join(parts)


def _heatmap_color(value: float, max_abs: float) -> str:
        if max_abs <= 0:
                return 'rgb(244, 236, 222)'
        intensity = min(abs(value) / max_abs, 1.0)
        if value >= 0:
                red = round(239 - (31 * intensity))
                green = round(227 - (105 * intensity))
                blue = round(207 - (162 * intensity))
                return f'rgb({red}, {green}, {blue})'

        red = round(233 - (136 * intensity))
        green = round(243 - (74 * intensity))
        blue = round(239 - (59 * intensity))
        return f'rgb({red}, {green}, {blue})'


def _render_face_bias_heatmap_svg(ranked_dice: tuple[DieMetrics, ...]) -> str:
        width = 980
        height = 470
        margin_left = 170
        margin_top = 70
        cell_width = 108
        cell_height = 34
        row_gap = 10
        col_gap = 10
        max_abs = max(abs(value) for die in ranked_dice for value in die.deviations)

        parts = [
                f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Face bias heatmap across all Yahtzee dice">',
                f'<rect x="0" y="0" width="{width}" height="{height}" rx="24" fill="#fffaf2"/>',
                '<text x="170" y="30" fill="#1f1a17" font-size="22" font-weight="700">Per-face bias heatmap</text>',
                '<text x="170" y="50" fill="#6e6258" font-size="13">Each cell shows deviation from the ideal 16.67% frequency. Green is low, warm is high.</text>',
        ]

        for column, face in enumerate(range(1, 7)):
                x = margin_left + column * (cell_width + col_gap)
                parts.append(f'<text x="{x + cell_width / 2:.2f}" y="{margin_top - 14}" text-anchor="middle" fill="#6e6258" font-size="13">Face {face}</text>')

        for row_index, die in enumerate(ranked_dice):
                y = margin_top + row_index * (cell_height + row_gap)
                parts.append(f'<text x="{margin_left - 14}" y="{y + 22}" text-anchor="end" fill="#1f1a17" font-size="14">Die {_format_die_name(die.dice_id)}</text>')
                for column, deviation in enumerate(die.deviations, start=0):
                        x = margin_left + column * (cell_width + col_gap)
                        parts.append(f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" rx="10" fill="{_heatmap_color(deviation, max_abs)}" stroke="rgba(79,59,43,0.10)"/>')
                        parts.append(f'<text x="{x + cell_width / 2:.2f}" y="{y + 22}" text-anchor="middle" fill="#1f1a17" font-size="13">{_format_pp(deviation)}</text>')

        legend_y = margin_top + len(ranked_dice) * (cell_height + row_gap) + 8
        for index, sample in enumerate([-max_abs, -max_abs / 2, 0.0, max_abs / 2, max_abs]):
                x = margin_left + index * 145
                parts.append(f'<rect x="{x}" y="{legend_y}" width="110" height="20" rx="8" fill="{_heatmap_color(sample, max_abs)}"/>')
                parts.append(f'<text x="{x + 55:.2f}" y="{legend_y + 36}" text-anchor="middle" fill="#6e6258" font-size="12">{_format_pp(sample)}</text>')

        parts.append('</svg>')
        return ''.join(parts)


def _render_group_comparison_svg(summary: ComparisonSummary) -> str:
        highlights = _summary_highlights(summary)
        scenarios = [
                ('Best pooled 5', highlights['best_pooled_group'].pooled_metrics.chi_square, '#2f7a72'),
                ('Top-5 individuals', highlights['best_individual_group'].pooled_metrics.chi_square, '#d06b2d'),
                ('All 10 pooled', summary.all_dice.chi_square, '#7c6a58'),
                ('Worst pooled 5', highlights['worst_pooled_group'].pooled_metrics.chi_square, '#a63f3f'),
        ]

        width = 920
        height = 420
        margin_left = 82
        margin_right = 30
        margin_top = 48
        margin_bottom = 70
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        bar_gap = 40
        bar_width = (chart_width - bar_gap * (len(scenarios) - 1)) / len(scenarios)
        max_value = max(value for _, value, _ in scenarios) * 1.15

        parts = [
                f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Group fairness comparison chart">',
                f'<rect x="0" y="0" width="{width}" height="{height}" rx="24" fill="#fffaf2"/>',
                f'<text x="{margin_left}" y="28" fill="#1f1a17" font-size="22" font-weight="700">Group fairness comparison</text>',
                f'<text x="{margin_left}" y="46" fill="#6e6258" font-size="13">Comparing the best pooled set, the naive top-five pick, all ten pooled, and the worst pooled set.</text>',
                f'<line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="#4f3b2b" stroke-width="2"/>',
        ]

        for tick in range(6):
                value = max_value * tick / 5
                y = margin_top + chart_height - (value / max_value) * chart_height
                parts.append(f'<line x1="{margin_left}" y1="{y:.2f}" x2="{margin_left + chart_width}" y2="{y:.2f}" stroke="rgba(79,59,43,0.10)" stroke-width="1"/>')
                parts.append(f'<text x="{margin_left - 10}" y="{y + 4:.2f}" text-anchor="end" fill="#6e6258" font-size="12">{value:.1f}</text>')

        for index, (label, value, fill) in enumerate(scenarios):
                x = margin_left + index * (bar_width + bar_gap)
                bar_height = (value / max_value) * chart_height
                y = margin_top + chart_height - bar_height
                label_lines = label.split(' ')
                parts.extend([
                        f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" rx="14" fill="{fill}" opacity="0.92"/>',
                        f'<text x="{x + bar_width / 2:.2f}" y="{y - 10:.2f}" text-anchor="middle" fill="#1f1a17" font-size="13">{value:.3f}</text>',
                ])
                for line_index, line in enumerate(label_lines):
                        parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{margin_top + chart_height + 24 + line_index * 15}" text-anchor="middle" fill="#6e6258" font-size="12">{escape(line)}</text>')

        parts.append('</svg>')
        return ''.join(parts)


def _render_html_dashboard(summary: ComparisonSummary) -> str:
        ranked_dice = summary.ranked_dice
        ranked_groups = summary.ranked_groups
        all_dice = summary.all_dice
        highlights = _summary_highlights(summary)

        best_pooled_group = highlights['best_pooled_group']
        best_individual_group = highlights['best_individual_group']
        worst_pooled_group = highlights['worst_pooled_group']
        most_random_die = highlights['most_random_die']
        least_random_die = highlights['least_random_die']
        closest_mean_die = highlights['closest_mean_die']
        chi_reduction = highlights['chi_reduction']

        single_die_rows = ''.join(
                (
                        '<tr>'
                        f'<td>{rank}</td>'
                        f'<td>Die {escape(_format_die_name(die.dice_id))}</td>'
                        f'<td>{die.chi_square:.3f}</td>'
                        f'<td>{die.p_value:.3f}</td>'
                        f'<td>{die.tvd:.4f}</td>'
                        f'<td>{die.mean_roll:.3f}</td>'
                        f'<td>+{die.most_overrepresented_face} {_format_pp(die.most_overrepresented_delta)} / -{die.most_underrepresented_face} {_format_pp(die.most_underrepresented_delta)}</td>'
                        '</tr>'
                )
                for rank, die in enumerate(ranked_dice, start=1)
        )

        group_rows = ''.join(
                (
                        '<tr>'
                        f'<td>{rank}</td>'
                        f'<td>{escape(_format_group(group))}</td>'
                        f'<td>{group.pooled_metrics.chi_square:.3f}</td>'
                        f'<td>{group.pooled_metrics.p_value:.3f}</td>'
                        f'<td>{group.pooled_metrics.tvd:.4f}</td>'
                        f'<td>{group.pooled_metrics.mean_roll:.3f}</td>'
                        '</tr>'
                )
                for rank, group in enumerate(ranked_groups[:10], start=1)
        )

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Yahtzee Dice Comparison Dashboard</title>
    <style>
        :root {{
            color-scheme: light;
            --ink: #1f1a17;
            --muted: #6e6258;
            --card: rgba(255, 250, 242, 0.9);
            --accent: #2f7a72;
            --accent-warm: #d06b2d;
            --accent-danger: #a63f3f;
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
                radial-gradient(circle at top left, rgba(47, 122, 114, 0.18), transparent 26%),
                radial-gradient(circle at right 20%, rgba(208, 107, 45, 0.18), transparent 22%),
                linear-gradient(180deg, #f7f0e5 0%, #efe3cf 100%);
            min-height: 100vh;
        }}
        main {{
            max-width: 1220px;
            margin: 0 auto;
            padding: 36px 20px 64px;
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
            font-size: clamp(2.6rem, 6vw, 5rem);
            line-height: 0.94;
            letter-spacing: -0.05em;
            max-width: 12ch;
        }}
        .hero p {{
            margin: 0;
            max-width: 70ch;
            color: var(--muted);
            font-size: 1.05rem;
            line-height: 1.5;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin: 26px 0 18px;
        }}
        .card {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 20px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(12px);
        }}
        .metric-label {{
            display: block;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.78rem;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-size: clamp(1.8rem, 4vw, 2.8rem);
            line-height: 1;
        }}
        .metric-value small {{
            display: block;
            margin-top: 8px;
            font-size: 0.95rem;
            color: var(--muted);
        }}
        .section {{
            margin-top: 22px;
        }}
        .section h2 {{
            margin: 0 0 12px;
            font-size: 1.45rem;
            letter-spacing: -0.03em;
        }}
        .section p.section-note {{
            margin: 0 0 14px;
            color: var(--muted);
            line-height: 1.45;
        }}
        .chart-card {{
            overflow-x: auto;
        }}
        .summary-list {{
            display: grid;
            gap: 10px;
            margin: 0;
            padding: 0;
            list-style: none;
        }}
        .summary-list li {{
            line-height: 1.45;
            color: var(--ink);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 12px 10px;
            text-align: left;
            border-bottom: 1px solid var(--line);
            vertical-align: top;
        }}
        th {{
            color: var(--muted);
            font-size: 0.8rem;
            font-weight: normal;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        .two-column {{
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 16px;
            align-items: start;
        }}
        .callout {{
            border-left: 6px solid var(--accent);
            background: rgba(47, 122, 114, 0.09);
        }}
        .callout.callout--warning {{
            border-left-color: var(--accent-warm);
            background: rgba(208, 107, 45, 0.09);
        }}
        .badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        .badge {{
            display: inline-flex;
            padding: 8px 12px;
            border-radius: 999px;
            background: var(--surface);
            border: 1px solid var(--line);
            font-size: 0.92rem;
        }}
        @media (max-width: 900px) {{
            .two-column {{
                grid-template-columns: 1fr;
            }}
        }}
        @media (max-width: 700px) {{
            main {{ padding: 24px 14px 48px; }}
            .card {{ padding: 16px; border-radius: 18px; }}
        }}
    </style>
</head>
<body>
    <main>
        <section class="hero">
            <span class="eyebrow">Dice Analysis Dashboard</span>
            <h1>Yahtzee Comparison</h1>
            <p>This dashboard compares the ten recorded Yahtzee dice across 10,000 total rolls. It ranks single-die fairness, visualizes per-face biases, and compares the best and worst five-die groups using pooled goodness-of-fit metrics.</p>
        </section>

        <section class="grid">
            <article class="card">
                <span class="metric-label">Best Single Die</span>
                <div class="metric-value">Die {escape(_format_die_name(most_random_die.dice_id))}<small>chi-square {most_random_die.chi_square:.3f} | p-value {most_random_die.p_value:.3f}</small></div>
            </article>
            <article class="card">
                <span class="metric-label">Best Five-Die Group</span>
                <div class="metric-value">{escape(_format_group(best_pooled_group))}<small>pooled chi-square {best_pooled_group.pooled_metrics.chi_square:.3f}</small></div>
            </article>
            <article class="card">
                <span class="metric-label">Weakest Single Die</span>
                <div class="metric-value">Die {escape(_format_die_name(least_random_die.dice_id))}<small>chi-square {least_random_die.chi_square:.3f} | p-value {least_random_die.p_value:.3f}</small></div>
            </article>
            <article class="card">
                <span class="metric-label">Top-5 Improvement</span>
                <div class="metric-value">{chi_reduction * 100:.1f}%<small>better pooled chi-square than the naive top-five pick</small></div>
            </article>
        </section>

        <section class="two-column section">
            <article class="card callout">
                <h2>Executive Summary</h2>
                <ul class="summary-list">
                    <li>Die {escape(_format_die_name(most_random_die.dice_id))} is the closest single die to a uniform d6 in this sample.</li>
                    <li>The most balanced five-die set is {escape(_format_group(best_pooled_group))}, not the simple top-five by individual ranking.</li>
                    <li>Die {escape(_format_die_name(least_random_die.dice_id))} is the only single die that rejects uniformity at the 0.05 level.</li>
                    <li>All ten dice pooled together still look broadly acceptable: chi-square {all_dice.chi_square:.3f}, p-value {all_dice.p_value:.3f}, TVD {all_dice.tvd:.4f}.</li>
                    <li>Die {escape(_format_die_name(closest_mean_die.dice_id))} is closest to the expected mean of 3.5 with an observed mean of {closest_mean_die.mean_roll:.3f}.</li>
                </ul>
                <div class="badges">
                    <span class="badge">Best pooled set: {escape(_format_group(best_pooled_group))}</span>
                    <span class="badge">Naive top five: {escape(_format_group(best_individual_group))}</span>
                    <span class="badge">Worst pooled set: {escape(_format_group(worst_pooled_group))}</span>
                </div>
            </article>
            <article class="card callout callout--warning">
                <h2>Interpretation Notes</h2>
                <ul class="summary-list">
                    <li>The primary fairness metric is chi-square goodness-of-fit against a uniform d6.</li>
                    <li>TVD is a direct measure of how far the observed distribution moves away from 16.67% per face.</li>
                    <li>Group rankings here measure pooled balance only. They do not establish physical independence between dice.</li>
                    <li>Bias cancellation matters: a sixth-ranked die can improve a five-die pool if its face biases offset the others.</li>
                </ul>
            </article>
        </section>

        <section class="section">
            <article class="card chart-card">
                <h2>Single-Die Ranking Chart</h2>
                <p class="section-note">This chart ranks all ten dice by chi-square. Lower values indicate a closer match to a fair six-sided die.</p>
                {_render_single_die_rank_svg(ranked_dice)}
            </article>
        </section>

        <section class="section">
            <article class="card chart-card">
                <h2>Face Bias Heatmap</h2>
                <p class="section-note">Each cell shows how far a face is above or below the ideal 16.67% frequency. This is the quickest way to see why some mediocre individual dice combine well in a group.</p>
                {_render_face_bias_heatmap_svg(ranked_dice)}
            </article>
        </section>

        <section class="section">
            <article class="card chart-card">
                <h2>Group Comparison Chart</h2>
                <p class="section-note">The best pooled group outperforms the naive top-five selection, while the weakest pooled group is materially worse than both.</p>
                {_render_group_comparison_svg(summary)}
            </article>
        </section>

        <section class="two-column section">
            <article class="card">
                <h2>Ranked Single Dice</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Die</th>
                            <th>Chi-square</th>
                            <th>p-value</th>
                            <th>TVD</th>
                            <th>Mean</th>
                            <th>Bias summary</th>
                        </tr>
                    </thead>
                    <tbody>
                        {single_die_rows}
                    </tbody>
                </table>
            </article>
            <article class="card">
                <h2>Best Five-Die Groups</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Dice</th>
                            <th>Chi-square</th>
                            <th>p-value</th>
                            <th>TVD</th>
                            <th>Mean</th>
                        </tr>
                    </thead>
                    <tbody>
                        {group_rows}
                    </tbody>
                </table>
            </article>
        </section>
    </main>
</body>
</html>
'''


def build_report() -> str:
    return _render_markdown_report(_build_summary())


def build_dashboard_html() -> str:
    return _render_html_dashboard(_build_summary())


def main() -> None:
    parser = argparse.ArgumentParser(description='Compare the ten recorded Yahtzee dice and write Markdown and HTML reports.')
    parser.add_argument(
    '--output',
        type=Path,
    default=DEFAULT_MARKDOWN_OUTPUT_PATH,
    help='Path to the Markdown report to generate.',
    )
    parser.add_argument(
    '--html-output',
    type=Path,
    default=DEFAULT_HTML_OUTPUT_PATH,
    help='Path to the HTML dashboard to generate.',
    )
    args = parser.parse_args()

    summary = _build_summary()
    markdown_report = _render_markdown_report(summary)
    html_dashboard = _render_html_dashboard(summary)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown_report, encoding='utf-8')
    args.html_output.parent.mkdir(parents=True, exist_ok=True)
    args.html_output.write_text(html_dashboard, encoding='utf-8')
    print(f'Wrote Markdown report to {args.output}')
    print(f'Wrote HTML dashboard to {args.html_output}')


if __name__ == '__main__':
    main()