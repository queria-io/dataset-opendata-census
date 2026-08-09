"""自治体オープンデータカタログの観測 + dbt ビルド。

1. census: 各カタログの CKAN API を叩き、自治体標準ODS 31項目の公開状況を観測
2. dbt:    観測結果をテーブルへ
"""

import logging
from pathlib import Path

from dbt.cli.main import dbtRunner

import census

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("main")

DATA_DIR = Path("data")


def dbt_build() -> None:
    dbt = dbtRunner()
    for cmd in (["deps"], ["build"], ["docs", "generate"]):
        result = dbt.invoke(cmd)
        if not result.success:
            raise SystemExit(f"dbt {cmd[0]} failed")


def main() -> None:
    logger.info("1/2: census (自治体標準ODS 公開状況の観測)")
    counts = census.run(DATA_DIR)
    for name, n in counts.items():
        logger.info("  %s.ndjson: %d 行", name, n)

    logger.info("2/2: dbt build")
    dbt_build()


if __name__ == "__main__":
    main()
