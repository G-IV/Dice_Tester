from pathlib import Path

from Scripts.Modules.Storage.capture_migration import migrate_capture_layout


class FakeDB:
    def __init__(self, rows):
        self._rows = rows

    def read_all_results(self):
        return [dict(row) for row in self._rows]

    def list_dice_ids(self):
        return sorted({str(row['dice_id']) for row in self._rows})

    def update_image_path(self, dice_id: str, timestamp: str, image_path: str, wait=False):
        for row in self._rows:
            if str(row['dice_id']) == str(dice_id) and str(row['timestamp']) == str(timestamp):
                row['image'] = image_path
                return
        raise AssertionError('Row not found for update_image_path')

    def delete_result(self, dice_id: str, timestamp: str, wait=False):
        self._rows[:] = [
            row for row in self._rows
            if not (str(row['dice_id']) == str(dice_id) and str(row['timestamp']) == str(timestamp))
        ]

    def wait_for_writes(self):
        return


def test_migrate_capture_layout_moves_images_and_reports(tmp_path: Path) -> None:
    captures_root = tmp_path / 'Scripts' / 'Modules' / 'Database' / 'Captures'
    legacy_reports = tmp_path / 'Captures' / 'Images' / 'Results'
    captures_root.mkdir(parents=True)
    legacy_reports.mkdir(parents=True)

    old_image_parent = captures_root / '9'
    old_image_parent.mkdir(parents=True)
    old_image_path = old_image_parent / 'old_capture.jpg'
    old_image_path.write_bytes(b'data')

    report_path = legacy_reports / 'dice_9_20260416_130328.html'
    report_path.write_text('<html>legacy report</html>', encoding='utf-8')

    db = FakeDB(
        rows=[
            {
                'dice_id': '9',
                'timestamp': '2026-04-16T10:47:21.360',
                'dice_sides': 6,
                'dice_result': 4,
                'image': str(old_image_path),
            }
        ]
    )

    summary = migrate_capture_layout(
        db,
        captures_root=captures_root,
        legacy_reports_root=legacy_reports,
        logging=False,
    )

    expected_image = captures_root / '9' / 'images' / 'old_capture.jpg'
    expected_report = captures_root / '9' / 'results.html'

    assert summary.moved_images == 1
    assert summary.updated_image_paths == 1
    assert summary.moved_reports == 1
    assert expected_image.exists()
    assert expected_report.exists()
    assert db._rows[0]['image'] == str(expected_image)


def test_migrate_capture_layout_deletes_rows_with_missing_images(tmp_path: Path) -> None:
    captures_root = tmp_path / 'Captures'
    captures_root.mkdir()

    db = FakeDB(
        rows=[
            {
                'dice_id': '1',
                'timestamp': '2026-01-01T00:00:00.000',
                'dice_sides': 6,
                'dice_result': 3,
                'image': str(captures_root / 'old_location' / 'ghost.jpg'),
            }
        ]
    )

    summary = migrate_capture_layout(db, captures_root=captures_root, logging=False)

    assert summary.deleted_rows == 1
    assert db._rows == []
