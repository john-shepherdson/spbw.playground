#!/usr/bin/env python3
"""Fetch posts/pages with the custom 'archive' status.

The REST API only lists published items, but archived ones are still in the
public sitemap and fetchable by ID. For each sitemap URL missing from
content/{posts,pages}.json: read the post ID from the page's <body> class,
then fetch /wp-json/wp/v2/<type>/<id>. Run fetch_content.py first.
Writes content/{posts,pages}_archived.json.
"""
import json
import pathlib
import re
import time
import urllib.request

BASE = "https://www.spbw.beer"
OUT = pathlib.Path(__file__).resolve().parent.parent / "content"
SITEMAPS = {"posts": "wp-sitemap-posts-post-1.xml", "pages": "wp-sitemap-posts-page-1.xml"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "spbw-playground-fetch/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


for kind, sitemap in SITEMAPS.items():
    known = {x["link"].rstrip("/") for x in json.loads((OUT / f"{kind}.json").read_text())}
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", fetch(f"{BASE}/{sitemap}"))
            if u.rstrip("/") not in known]
    print(f"{kind}: {len(urls)} not in API listing")
    items = []
    for u in urls:
        m = re.search(r"<body[^>]*\b(?:postid|page-id)-(\d+)", fetch(u))
        if not m:
            print("  no id:", u)
            continue
        items.append(json.loads(fetch(f"{BASE}/wp-json/wp/v2/{kind}/{m.group(1)}?context=view")))
        time.sleep(0.4)
    (OUT / f"{kind}_archived.json").write_text(json.dumps(items, indent=1, ensure_ascii=False))
    print(f"  saved {len(items)}")
