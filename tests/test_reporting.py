from pathlib import Path

from Scripts.Modules.Analysis.reporting import analyze_results, build_summary_lines, chi_square_p_value, write_report


def test_chi_square_p_value_is_one_for_zero_statistic() -> None:
    assert chi_square_p_value(0.0, 5) == 1.0


def test_analyze_results_builds_expected_distribution() -> None:
    rows = [
        {'timestamp': '2026-04-16T10:00:00.000', 'dice_result': 1, 'dice_sides': 6, 'image': 'a.png'},
        {'timestamp': '2026-04-16T10:00:01.000', 'dice_result': 2, 'dice_sides': 6, 'image': 'b.png'},
        {'timestamp': '2026-04-16T10:00:02.000', 'dice_result': 2, 'dice_sides': 6, 'image': 'c.png'},
        {'timestamp': '2026-04-16T10:00:03.000', 'dice_result': 6, 'dice_sides': 6, 'image': 'd.png'},
        {'timestamp': '2026-04-16T10:00:04.000', 'dice_result': 6, 'dice_sides': 6, 'image': 'e.png'},
        {'timestamp': '2026-04-16T10:00:05.000', 'dice_result': 6, 'dice_sides': 6, 'image': 'f.png'},
    ]

    report = analyze_results(dice_id='12', rows=rows, dice_sides=6)

    assert report.sample_count == 6
    assert report.longest_streak_value == 6
    assert report.longest_streak_length == 3
    assert [frequency.count for frequency in report.frequencies] == [1, 2, 0, 0, 0, 3]
    assert round(report.chi_square_statistic, 4) == 8.0
    assert round(report.p_value, 4) == 0.1562


def test_write_report_creates_html_file(tmp_path: Path) -> None:
    rows = [
        {'timestamp': '2026-04-16T10:00:00.000', 'dice_result': 1, 'dice_sides': 6, 'image': 'a.png'},
        {'timestamp': '2026-04-16T10:00:01.000', 'dice_result': 2, 'dice_sides': 6, 'image': 'b.png'},
        {'timestamp': '2026-04-16T10:00:02.000', 'dice_result': 3, 'dice_sides': 6, 'image': 'c.png'},
        {'timestamp': '2026-04-16T10:00:03.000', 'dice_result': 4, 'dice_sides': 6, 'image': 'd.png'},
        {'timestamp': '2026-04-16T10:00:04.000', 'dice_result': 5, 'dice_sides': 6, 'image': 'e.png'},
        {'timestamp': '2026-04-16T10:00:05.000', 'dice_result': 6, 'dice_sides': 6, 'image': 'f.png'},
    ]

    report = analyze_results(dice_id='44', rows=rows, dice_sides=6)
    report_path = write_report(report, tmp_path)

    assert report_path.exists()
    assert report_path.name == 'results.html'
    html = report_path.read_text(encoding='utf-8')
    assert 'Die 44 over 6 rolls' in html
    assert 'Observed distribution' in html
    assert 'Statistical interpretation' in html
    assert 'Sample adequacy (expected &gt;= 5 per face):' in html
    assert 'callout--warning' in html
    assert '<svg' in html


def test_build_summary_lines_includes_sample_adequacy_and_interpretation() -> None:
    rows = [
        {'timestamp': '2026-04-16T10:00:00.000', 'dice_result': 1, 'dice_sides': 6, 'image': 'a.png'},
        {'timestamp': '2026-04-16T10:00:01.000', 'dice_result': 2, 'dice_sides': 6, 'image': 'b.png'},
        {'timestamp': '2026-04-16T10:00:02.000', 'dice_result': 2, 'dice_sides': 6, 'image': 'c.png'},
        {'timestamp': '2026-04-16T10:00:03.000', 'dice_result': 6, 'dice_sides': 6, 'image': 'd.png'},
        {'timestamp': '2026-04-16T10:00:04.000', 'dice_result': 6, 'dice_sides': 6, 'image': 'e.png'},
        {'timestamp': '2026-04-16T10:00:05.000', 'dice_result': 6, 'dice_sides': 6, 'image': 'f.png'},
    ]
    report = analyze_results(dice_id='12', rows=rows, dice_sides=6)

    summary = build_summary_lines(report)

    assert any(line.startswith('Expected count per face:') for line in summary)
    assert 'Sample adequacy (expected >= 5 per face): LOW' in summary
    assert any('chi-square approximation may be unreliable' in line for line in summary)


def test_large_sample_hides_recent_roll_chips_in_html(tmp_path: Path) -> None:
    rows = [
        {
            'timestamp': f'2026-04-16T10:00:{index // 1000:02d}.{index % 1000:03d}',
            'dice_result': (index % 6) + 1,
            'dice_sides': 6,
            'image': f'{index}.png',
        }
        for index in range(1200)
    ]
    report = analyze_results(dice_id='99', rows=rows, dice_sides=6)
    report_path = write_report(report, tmp_path)
    html = report_path.read_text(encoding='utf-8')

    assert 'Recent rolls (scaled view)' in html
    assert 'Recent rolls are hidden for large sample sizes.' in html
    assert '<span class="roll-chip">' not in html