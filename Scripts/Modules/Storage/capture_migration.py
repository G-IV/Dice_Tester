from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MigrationSummary:
    moved_images: int = 0
    updated_image_paths: int = 0
    deleted_rows: int = 0
    moved_reports: int = 0
    archived_reports: int = 0

    def changed(self) -> bool:
        return any(
            (
                self.moved_images,
                self.updated_image_paths,
                self.deleted_rows,
                self.moved_reports,
                self.archived_reports,
            )
        )


def _safe_move(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        stem = destination.stem
        suffix = destination.suffix
        index = 1
        while True:
            candidate = destination.with_name(f'{stem}_{index}{suffix}')
            if not candidate.exists():
                destination = candidate
                break
            index += 1
    source.rename(destination)
    return destination


def _latest_report_path(paths: list[Path]) -> Path:
    return max(paths, key=lambda candidate: candidate.stat().st_mtime)


def migrate_capture_layout(db, captures_root: Path, legacy_reports_root: Path | None = None, logging: bool = False) -> MigrationSummary:
    moved_images = 0
    updated_image_paths = 0
    deleted_rows = 0
    moved_reports = 0
    archived_reports = 0

    captures_root.mkdir(parents=True, exist_ok=True)

    all_rows = db.read_all_results()
    dice_ids = {str(row['dice_id']) for row in all_rows}

    for row in all_rows:
        dice_id = str(row['dice_id'])
        timestamp = row['timestamp']
        source_image = Path(row['image'])
        target_dir = captures_root / dice_id / 'images'
        target_dir.mkdir(parents=True, exist_ok=True)
        target_image = target_dir / source_image.name

        if source_image == target_image:
            continue

        if source_image.exists():
            moved_to = _safe_move(source_image, target_image)
            db.update_image_path(dice_id, timestamp, str(moved_to), wait=False)
            moved_images += 1
            updated_image_paths += 1
            continue

        if target_image.exists():
            db.update_image_path(dice_id, timestamp, str(target_image), wait=False)
            updated_image_paths += 1
            continue

        db.delete_result(dice_id, timestamp, wait=False)
        deleted_rows += 1

    db.wait_for_writes()

    if legacy_reports_root is not None and legacy_reports_root.exists():
        for dice_id in sorted(dice_ids):
            dice_dir = captures_root / dice_id
            dice_dir.mkdir(parents=True, exist_ok=True)
            target_report = dice_dir / 'results.html'

            report_candidates = [
                path for path in legacy_reports_root.glob(f'dice_{dice_id}_*.html') if path.is_file()
            ]
            report_candidates.extend(
                path for path in dice_dir.glob(f'dice_{dice_id}_*.html') if path.is_file()
            )

            if not report_candidates:
                continue

            latest_report = _latest_report_path(report_candidates)

            if not target_report.exists():
                moved_to = _safe_move(latest_report, target_report)
                if moved_to == target_report:
                    moved_reports += 1
            elif latest_report != target_report:
                archive_dir = dice_dir / 'reports_archive'
                archive_target = archive_dir / latest_report.name
                _safe_move(latest_report, archive_target)
                archived_reports += 1

            for extra_report in report_candidates:
                if extra_report.exists() and extra_report != target_report:
                    archive_dir = dice_dir / 'reports_archive'
                    archive_target = archive_dir / extra_report.name
                    _safe_move(extra_report, archive_target)
                    archived_reports += 1

    summary = MigrationSummary(
        moved_images=moved_images,
        updated_image_paths=updated_image_paths,
        deleted_rows=deleted_rows,
        moved_reports=moved_reports,
        archived_reports=archived_reports,
    )

    if logging and summary.changed():
        print(
            'Capture migration summary: '
            f'moved_images={summary.moved_images}, '
            f'updated_image_paths={summary.updated_image_paths}, '
            f'deleted_rows={summary.deleted_rows}, '
            f'moved_reports={summary.moved_reports}, '
            f'archived_reports={summary.archived_reports}'
        )

    return summary
