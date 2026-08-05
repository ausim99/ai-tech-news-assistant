"""Delete daily digest files older than the retention window. Run weekly by
cleanup.yml. history.json's lightweight per-day index is kept forever -
only the full digest payloads under data/daily/ get rotated."""

import argparse
from datetime import UTC, datetime, timedelta

from services import storage
from services.logging import logger


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retention-days", type=int, default=90)
    args = parser.parse_args()

    cutoff = datetime.now(UTC).date() - timedelta(days=args.retention_days)
    daily_dir = storage.DATA_DIR / "daily"
    if not daily_dir.exists():
        logger.info("no daily/ directory yet, nothing to clean up")
        return

    removed = 0
    for path in daily_dir.glob("*.json"):
        try:
            file_date = datetime.strptime(path.stem, "%Y-%m-%d").replace(tzinfo=UTC).date()
        except ValueError:
            continue
        if file_date < cutoff:
            path.unlink()
            removed += 1

    logger.info(f"removed {removed} digest file(s) older than {args.retention_days} days")


if __name__ == "__main__":
    main()
