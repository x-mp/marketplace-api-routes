#!/usr/bin/env python3
"""Build Ozon and Yandex Market route indexes from pinned source snapshots."""

import argparse
import csv
import hashlib
import json
import subprocess
import tempfile
from datetime import date
from pathlib import Path
from urllib.request import urlopen

import yaml


OZON_COMMIT = "1953152c36955225b459cf55963a2c3a7a234661"
YANDEX_COMMIT = "321c272cfe218c21fd1644242cef205b6c9b8dbe"
METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


def normalize_servers(servers):
    result = set()
    for server in servers or []:
        if isinstance(server, dict) and server.get("url"):
            url = server["url"].rstrip("/")
            result.add("https:" + url if url.startswith("//") else url)
    return sorted(result)


def write_catalog(marketplace, rows, sources, output_dir, source_date):
    rows.sort(key=lambda r: (r["category"], r["path"], r["method"]))
    if len({(r["category"], r["method"], r["path"]) for r in rows}) != len(rows):
        raise ValueError(f"Duplicate {marketplace} route")
    output_dir.mkdir(parents=True, exist_ok=True)
    catalog = {"marketplace": marketplace, "catalog_generated_at": date.today().isoformat(),
               "source_snapshot_at": source_date, "current_status": "not_live_verified",
               "route_count": len(rows), "source_count": len(sources), "sources": sources, "routes": rows}
    (output_dir / "routes.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output_dir / "routes.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "method", "path", "base_url", "summary", "tags", "deprecated", "official_docs"])
        writer.writeheader()
        for row in rows:
            for base_url in row["base_urls"] or [""]:
                writer.writerow({"category": row["category"], "method": row["method"], "path": row["path"],
                                 "base_url": base_url, "summary": row["summary"], "tags": "; ".join(row["tags"]),
                                 "deprecated": row["deprecated"], "official_docs": row["official_docs"]})
    print(f"{marketplace}: {len(sources)} sources, {len(rows)} routes")


def route(marketplace, category, method, path, operation, servers, official_docs, source_file):
    bases = normalize_servers(servers)
    return {"marketplace": marketplace, "category": category, "method": method.upper(), "path": path,
            "base_urls": bases, "urls": [base + path for base in bases],
            "summary": " ".join(str(operation.get("summary", "")).split()), "tags": operation.get("tags", []),
            "operation_id": operation.get("operationId"), "deprecated": bool(operation.get("deprecated", False)),
            "official_docs": official_docs, "source_file": source_file}


def build_ozon(source_dir, output_dir):
    rows, sources = [], []
    for category in ("seller", "performance"):
        filename = f"ozon-{category}-openapi.json"
        source_url = f"https://raw.githubusercontent.com/MissiaL/ozon-api/{OZON_COMMIT}/references/{filename}"
        raw = (source_dir / filename).read_bytes() if source_dir else urlopen(source_url, timeout=45).read()
        spec = json.loads(raw)
        if not str(spec.get("openapi", "")).startswith("3."):
            raise ValueError(f"Invalid Ozon OpenAPI: {filename}")
        sources.append({"category": category, "url": source_url, "sha256": hashlib.sha256(raw).hexdigest(),
                        "upstream": f"https://docs.ozon.ru/api/{category}/swagger.json"})
        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() in METHODS and isinstance(operation, dict):
                    servers = operation.get("servers") or path_item.get("servers") or spec.get("servers")
                    rows.append(route("ozon", category, method, path, operation, servers,
                                      f"https://docs.ozon.ru/api/{category}/", filename))
    write_catalog("ozon", rows, sources, output_dir, "2026-08-19")


def build_yandex(source_dir, output_dir):
    with tempfile.TemporaryDirectory() if source_dir is None else _NoopContext(source_dir) as root:
        if source_dir is None:
            repo = Path(root) / "repo"
            subprocess.run(["git", "clone", "--quiet", "--filter=blob:none", "https://github.com/yandex-market/yandex-market-partner-api.git", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "checkout", "--quiet", "--detach", YANDEX_COMMIT], check=True)
        else:
            repo = Path(root)
        base = repo / "openapi"
        raw = (base / "openapi.yaml").read_bytes()
        spec = yaml.safe_load(raw)
        if not str(spec.get("openapi", "")).startswith("3."):
            raise ValueError("Invalid Yandex OpenAPI")
        source_url = f"https://github.com/yandex-market/yandex-market-partner-api/tree/{YANDEX_COMMIT}/openapi"
        sources = [{"category": "partner-api", "url": source_url, "root_sha256": hashlib.sha256(raw).hexdigest()}]
        rows = []
        for path, path_item in spec.get("paths", {}).items():
            source_file = "openapi.yaml"
            if "$ref" in path_item:
                source_file = path_item["$ref"]
                path_item = yaml.safe_load((base / source_file).read_text(encoding="utf-8"))
            for method, operation in path_item.items():
                if method.lower() in METHODS and isinstance(operation, dict):
                    servers = operation.get("servers") or path_item.get("servers") or spec.get("servers")
                    rows.append(route("yandex-market", "partner-api", method, path, operation, servers,
                                      "https://yandex.ru/dev/market/partner-api/doc/ru/", source_file))
        write_catalog("yandex-market", rows, sources, output_dir, "2026-09-22")


class _NoopContext:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value

    def __exit__(self, *args):
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("marketplace", choices=["ozon", "yandex-market"])
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    destination = args.output_dir or Path(args.marketplace)
    if args.marketplace == "ozon":
        build_ozon(args.source_dir, destination)
    else:
        build_yandex(args.source_dir, destination)
