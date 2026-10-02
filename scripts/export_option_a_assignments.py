#!/usr/bin/env python3
"""Turn config/option-a-classification.json into files for applying Option A to the live site.

Writes config/option-a-assignments.csv (for bulk edit in the WordPress admin) and
config/option-a-apply.sh (WP-CLI commands; dry run unless DRY_RUN=0). Run
classify_posts.py first.
"""
import csv
import html
import json
import pathlib
import shlex

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://www.spbw.beer"
cls = json.loads((ROOT / "config" / "option-a-classification.json").read_text())
names = {c["id"]: c["name"] for c in json.loads((ROOT / "content" / "categories.json").read_text())}
posts = {}
for f in ("posts", "posts_archived"):
    for p in json.loads((ROOT / "content" / f"{f}.json").read_text()):
        posts[p["id"]] = p

rows = []
for pid, c in cls.items():
    p = posts[int(pid)]
    rows.append({"post_id": pid, "date": p["date"][:10], "title": html.unescape(p["title"]["rendered"]),
                 "add_categories": "; ".join(c["categories"]), "add_tags": "; ".join(c["tags"]),
                 "edit_url": f"{SITE}/wp-admin/post.php?post={pid}&action=edit"})
rows.sort(key=lambda r: (r["add_categories"], r["date"]))
with open(ROOT / "config" / "option-a-assignments.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

# posts that carry 'Uncategorised' alongside another category (redundant)
redundant = [str(p["id"]) for p in posts.values()
             if "Uncategorised" in {names.get(c) for c in p.get("categories", [])} and len(p.get("categories", [])) > 1]
lines = ["#!/bin/sh",
         "# Apply the Option A categories and tags to spbw.beer with WP-CLI.",
         "# Run from the WordPress folder as the site user. BACK UP THE SITE FIRST.",
         "# Dry run by default (prints the commands). Run with DRY_RUN=0 to apply them.",
         'if [ "${DRY_RUN:-1}" = "0" ]; then RUN=""; else RUN="echo"; fi', "",
         "# 1. Existing categories are reused by name; new ones are created as needed.", ""]
for r in sorted(rows, key=lambda r: int(r["post_id"])):
    for cat in filter(None, r["add_categories"].split("; ")):
        lines.append(f"$RUN wp post term add {r['post_id']} category {shlex.quote(cat)}")
    for tag in filter(None, r["add_tags"].split("; ")):
        lines.append(f"$RUN wp post term add {r['post_id']} post_tag {shlex.quote(tag)}")
lines += ["", "# 2. Remove 'Uncategorised' from every post that now has a real category.", ""]
lines += [f"$RUN wp post term remove {pid} category uncategorised" for pid in sorted(set(cls) | set(redundant), key=int)]
lines += ["", "# 3. Check the result.", "$RUN wp term list category --fields=name,slug,count", ""]
(ROOT / "config" / "option-a-apply.sh").write_text("\n".join(lines))
print(f"{len(rows)} posts; {len(set(cls) | set(redundant))} Uncategorised removals; "
      f"{len(lines)} script lines")
