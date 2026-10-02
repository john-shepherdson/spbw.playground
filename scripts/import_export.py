#!/usr/bin/env python3
"""Convert a WordPress admin export (WXR) into content/*.json.

Output has the same shape as the REST API files from fetch_content.py and
fetch_archived.py, so every later script works unchanged, but 'content.rendered'
holds the RAW editor content (block markup, straight quotes) instead of
theme-processed HTML.

Only published and archived posts and pages are written, so drafts, private
items, users, logs and menus in the export can never reach the public repo.
Usage: python3 scripts/import_export.py private/<export>.xml
"""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
NS = {"wp": "http://wordpress.org/export/1.2/", "content": "http://purl.org/rss/1.0/modules/content/",
      "excerpt": "http://wordpress.org/export/1.2/excerpt/", "dc": "http://purl.org/dc/elements/1.1/"}
PUBLIC = {"publish", "archive"}


def main(path):
    ch = ET.parse(path).getroot().find("channel")
    cats = {c.findtext("wp:category_nicename", namespaces=NS): int(c.findtext("wp:term_id", namespaces=NS))
            for c in ch.findall("wp:category", NS)}
    tags = {t.findtext("wp:tag_slug", namespaces=NS): int(t.findtext("wp:term_id", namespaces=NS))
            for t in ch.findall("wp:tag", NS)}
    out = {"posts": [], "posts_archived": [], "pages": [], "pages_archived": []}
    skipped = 0
    for it in ch.findall("item"):
        g = lambda t: it.findtext(t, namespaces=NS) or ""  # noqa: E731
        ptype, status = g("wp:post_type"), g("wp:status")
        if ptype not in ("post", "page"):
            continue
        if status not in PUBLIC:
            skipped += 1
            continue
        rec = {"id": int(g("wp:post_id")), "date": g("wp:post_date").replace(" ", "T"),
               "date_gmt": g("wp:post_date_gmt").replace(" ", "T"), "slug": g("wp:post_name"), "status": status,
               "type": ptype, "link": g("link"), "guid": {"rendered": g("guid")},
               "title": {"rendered": g("title")}, "content": {"rendered": g("content:encoded")},
               "excerpt": {"rendered": g("excerpt:encoded")}, "parent": int(g("wp:post_parent") or 0),
               "menu_order": int(g("wp:menu_order") or 0)}
        if ptype == "post":
            rec["categories"] = [cats[c.get("nicename")] for c in it.findall("category")
                                 if c.get("domain") == "category" and c.get("nicename") in cats]
            rec["tags"] = [tags[c.get("nicename")] for c in it.findall("category")
                           if c.get("domain") == "post_tag" and c.get("nicename") in tags]
        out[ptype + "s" + ("_archived" if status == "archive" else "")].append(rec)
    for k, v in out.items():
        v.sort(key=lambda r: r["id"])
        (ROOT / "content" / f"{k}.json").write_text(json.dumps(v, indent=1, ensure_ascii=False))
        print(f"{k}: {len(v)}")
    for name, src in (("categories", ch.findall("wp:category", NS)), ("tags", ch.findall("wp:tag", NS))):
        rows = []
        for t in src:
            slug = t.findtext("wp:category_nicename" if name == "categories" else "wp:tag_slug", namespaces=NS)
            nm = t.findtext("wp:cat_name" if name == "categories" else "wp:tag_name", namespaces=NS)
            rows.append({"id": int(t.findtext("wp:term_id", namespaces=NS)), "slug": slug, "name": nm})
        (ROOT / "content" / f"{name}.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
        print(f"{name}: {len(rows)}")
    if skipped:
        print(f"skipped {skipped} non-public posts/pages")


if __name__ == "__main__":
    main(sys.argv[1])
