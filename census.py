"""自治体オープンデータカタログを横断して、自治体標準ODS 31項目の公開状況を観測する。

データ本体は取得しない。CKAN の package_search を rows=0 で叩き、件数と
organization ファセットだけを読む。1リクエストごとに間隔を空ける。

CKAN(Solr) の癖が2つあり、これを外すと数字が桁で変わる。
- スペース区切りは AND として解釈され、`OR` キーワードは効かない
  → 語ごとに個別クエリを投げ、団体の集合として和を取る
- フリーテキストは notes まで一致するので過剰にヒットする
  （例: data.bodik.jp で「オープンデータ一覧」は 10,553 件、title 限定なら 125 件）
  → title 限定で検索する
"""

import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

from items import ITEMS

logger = logging.getLogger("census")

USER_AGENT = "queria-opendata-census/0.1 (+https://queria.io; contact: info@flo8s.com)"
REQUEST_INTERVAL = 2.0
TIMEOUT = 30
LG_CODE_RE = re.compile(r"^[0-9]{6}$")

# 観測対象のカタログ。CKAN API が生きている横断カタログのみを列挙する。
# 個別自治体のサブサイト（odcs.bodik.jp/<lg_code>/ 等）は WordPress のフロントで
# API を持たないため、横断カタログ側から一括で観測する。
PORTALS = [
    {
        "portal_id": "bodik",
        "title": "BODIK ODCS 横断カタログ",
        "operator": "公益財団法人九州先端科学技術研究所",
        "site_url": "https://data.bodik.jp/",
        "api_base": "https://data.bodik.jp/api/3/action",
        "type": "ckan",
    },
]


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return json.loads(res.read().decode("utf-8", errors="replace"))


def list_organizations(api_base: str) -> list[str]:
    """カタログの organization 名を全件返す。

    all_fields=true は CKAN 既定の 25 件で頭打ちになるため使わない。
    名前だけなら制限なく返る。団体名は lg_code データセット側で解決する。
    """
    return _get(f"{api_base}/organization_list")["result"]


def search_title(api_base: str, word: str) -> tuple[int, dict[str, int]]:
    """タイトルに word を含むデータセットの件数と、団体別の内訳を返す。"""
    q = urllib.parse.quote(f"title:{word}")
    url = (
        f"{api_base}/package_search?q={q}&rows=0"
        '&facet.field=%5B%22organization%22%5D&facet.limit=2000'
    )
    result = _get(url)["result"]
    return result["count"], result.get("facets", {}).get("organization", {})


def observe(portal: dict, measured_on: str) -> tuple[list[dict], list[dict], dict]:
    """1つのカタログを観測し、(measurements, word_hits, portal_record) を返す。"""
    api_base = portal["api_base"]

    orgs = list_organizations(api_base)
    lg_orgs = sorted(o for o in orgs if LG_CODE_RE.match(o))
    other_orgs = sorted(o for o in orgs if not LG_CODE_RE.match(o))
    logger.info(
        "  %s: organization %d 件（うち団体コード %d 件）",
        portal["portal_id"], len(orgs), len(lg_orgs),
    )

    # item_key -> {lg_code: dataset_count}
    hits: dict[str, dict[str, int]] = {}
    word_hits: list[dict] = []

    for no, key, label, book, words in ITEMS:
        found: dict[str, int] = {}
        for word in words:
            time.sleep(REQUEST_INTERVAL)
            try:
                count, facet = search_title(api_base, word)
            except (urllib.error.URLError, TimeoutError, ValueError) as e:
                logger.warning("    %s / %s: %s", label, word, type(e).__name__)
                word_hits.append(
                    {
                        "portal_id": portal["portal_id"],
                        "item_no": no,
                        "item_key": key,
                        "search_word": word,
                        "dataset_count": None,
                        "status": "failed",
                        "measured_on": measured_on,
                    }
                )
                continue
            word_hits.append(
                {
                    "portal_id": portal["portal_id"],
                    "item_no": no,
                    "item_key": key,
                    "search_word": word,
                    "dataset_count": count,
                    "status": "ok",
                    "measured_on": measured_on,
                }
            )
            for org, c in facet.items():
                # 同じ団体が複数の語に当たることがある。最大値を採る
                # （語をまたいで足すと同一データセットを重複計上するため）
                found[org] = max(found.get(org, 0), c)
        hits[key] = found
        logger.info("    %2d %-24s %4d 団体", no, label, len([o for o in found if LG_CODE_RE.match(o)]))

    measurements = []
    for no, key, label, book, words in ITEMS:
        found = hits[key]
        for org in lg_orgs:
            count = found.get(org, 0)
            measurements.append(
                {
                    "portal_id": portal["portal_id"],
                    "lg_code": org,
                    "item_no": no,
                    "item_key": key,
                    "is_published": count > 0,
                    "dataset_count": count,
                    "measured_on": measured_on,
                }
            )

    portal_record = {
        **portal,
        "organization_count": len(orgs),
        "lg_organization_count": len(lg_orgs),
        "non_lg_organizations": ";".join(other_orgs),
        "status": "measured",
        "measured_on": measured_on,
    }
    return measurements, word_hits, portal_record


def write_ndjson(path: Path, rows: list[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(rows)


def run(data_dir: Path) -> dict[str, int]:
    measured_on = date.today().isoformat()

    all_measurements: list[dict] = []
    all_word_hits: list[dict] = []
    portal_records: list[dict] = []

    for portal in PORTALS:
        logger.info("観測: %s", portal["title"])
        try:
            m, w, p = observe(portal, measured_on)
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            logger.warning("  失敗: %s", type(e).__name__)
            portal_records.append(
                {
                    **portal,
                    "organization_count": None,
                    "lg_organization_count": None,
                    "non_lg_organizations": None,
                    "status": f"failed:{type(e).__name__}",
                    "measured_on": measured_on,
                }
            )
            continue
        all_measurements += m
        all_word_hits += w
        portal_records.append(p)

    items = [
        {
            "item_no": no,
            "item_key": key,
            "item_label": label,
            "definition_book": book,
            "search_words": ";".join(words),
        }
        for no, key, label, book, words in ITEMS
    ]

    return {
        "measurement": write_ndjson(data_dir / "measurement.ndjson", all_measurements),
        "word_hit": write_ndjson(data_dir / "word_hit.ndjson", all_word_hits),
        "portal": write_ndjson(data_dir / "portal.ndjson", portal_records),
        "item": write_ndjson(data_dir / "item.ndjson", items),
    }
