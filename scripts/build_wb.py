#!/usr/bin/env python3
"""Build a compact route index from a pinned Wildberries OpenAPI snapshot."""

import argparse
import csv
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.request import urlopen

import yaml


COMMIT = "d6cb5a3ca0f2fad242ad3297926d802c45fd49c5"
SNAPSHOT_DATE = "2026-05-14"
SPECS = {
    "general": ("01-general.yaml", "api-information"),
    "products": ("02-products.yaml", "work-with-products"),
    "orders-fbs": ("03-orders-fbs.yaml", "orders-fbs"),
    "orders-dbw": ("04-orders-dbw.yaml", "orders-dbw"),
    "orders-dbs": ("05-orders-dbs.yaml", "orders-dbs"),
    "in-store-pickup": ("06-in-store-pickup.yaml", "in-store-pickup"),
    "orders-fbw": ("07-orders-fbw.yaml", "orders-fbw"),
    "promotion": ("08-promotion.yaml", "promotion"),
    "communications": ("09-communications.yaml", "user-communication"),
    "tariffs": ("10-tariffs.yaml", "wb-tariffs"),
    "analytics": ("11-analytics.yaml", "analytics"),
    "reports": ("12-reports.yaml", "reports"),
    "finances": ("13-finances.yaml", "financial-reports-and-accounting"),
}
METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
BASE = f"https://raw.githubusercontent.com/bigancientmammoth/wb-swagger/{COMMIT}/original/ru"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, help="Use already downloaded YAML files")
    parser.add_argument("--output-dir", type=Path, default=Path("wildberries"))
    args = parser.parse_args()
    rows = []
    sources = []
    for category, (filename, doc_slug) in SPECS.items():
        source_url = f"{BASE}/{filename}"
        raw = (args.source_dir / filename).read_bytes() if args.source_dir else urlopen(source_url, timeout=30).read()
        spec = yaml.safe_load(raw)
        if not isinstance(spec, dict) or not str(spec.get("openapi", "")).startswith("3."):
            raise ValueError(f"Invalid OpenAPI 3 document: {filename}")
        sources.append({"category": category, "url": source_url, "sha256": hashlib.sha256(raw).hexdigest()})
        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() not in METHODS or not isinstance(operation, dict):
                    continue
                servers = operation.get("servers") or path_item.get("servers") or spec.get("servers") or []
                base_urls = sorted({s["url"].rstrip("/") for s in servers if isinstance(s, dict) and s.get("url")})
                rows.append({
                    "marketplace": "wildberries",
                    "category": category,
                    "method": method.upper(),
                    "path": path,
                    "base_urls": base_urls,
                    "urls": [base + path for base in base_urls],
                    "summary": " ".join(str(operation.get("summary", "")).split()),
                    "tags": operation.get("tags", []),
                    "operation_id": operation.get("operationId"),
                    "deprecated": bool(operation.get("deprecated", False)),
                    "official_docs": f"https://dev.wildberries.ru/docs/openapi/{doc_slug}",
                    "source_file": filename,
                })
    rows.sort(key=lambda x: (x["category"], x["path"], x["method"]))
    if len({(r["category"], r["method"], r["path"]) for r in rows}) != len(rows):
        raise ValueError("Duplicate route records")
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    catalog = {
        "marketplace": "wildberries",
        "catalog_generated_at": today,
        "source_snapshot_at": SNAPSHOT_DATE,
        "current_status": "not_live_verified",
        "route_count": len(rows),
        "source_count": len(sources),
        "sources": sources,
        "routes": rows,
    }
    (output / "routes.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "routes.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "method", "path", "base_url", "summary", "tags", "deprecated", "official_docs"])
        writer.writeheader()
        for row in rows:
            for base_url in row["base_urls"] or [""]:
                writer.writerow({"category": row["category"], "method": row["method"], "path": row["path"], "base_url": base_url,
                                 "summary": row["summary"], "tags": "; ".join(row["tags"]), "deprecated": row["deprecated"],
                                 "official_docs": row["official_docs"]})
    print(f"Wildberries: {len(sources)} sources, {len(rows)} routes; generated {today}")


if __name__ == "__main__":
    main()
