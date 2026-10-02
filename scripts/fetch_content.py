#!/usr/bin/env python3
"""Pull public content from spbw.beer's WordPress REST API into content/*.json.

Read-only, public endpoints only. Stdlib only.
Usage: python3 scripts/fetch_content.py [--base https://spbw.beer]
"""
import argparse
import json
import pathlib
import time
import urllib.request

ENDPOINTS = ["posts", "pages", "categories", "tags", "media", "users"]
OUT = pathlib.Path(__file__).resolve().parent.parent / "content"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "spbw-playground-fetch/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r), int(r.headers.get("X-WP-TotalPages", "1"))


def fetch_all(base, name):
    items, page = [], 1
    while True:
        try:
            data, pages = get(f"{base}/wp-json/wp/v2/{name}?per_page=100&page={page}&context=view")
        except Exception as e:  # e.g. 401/403 on users
            print(f"  {name}: skipped ({e})")
            return None
        items += data
        if page >= pages:
            return items
        page += 1
        time.sleep(0.5)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://spbw.beer")
    base = ap.parse_args().base.rstrip("/")
    OUT.mkdir(exist_ok=True)
    for name in ENDPOINTS:
        items = fetch_all(base, name)
        if items is None:
            continue
        (OUT / f"{name}.json").write_text(json.dumps(items, indent=1, ensure_ascii=False))
        print(f"{name}: {len(items)}")
