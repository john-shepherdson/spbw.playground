#!/usr/bin/env python3
"""Classify still-uncategorised posts into categories and tags by title keywords (Option A).

Posts that already have a real category on the live site are left exactly as
they are. Only posts whose sole category is 'Uncategorised' are classified.

Writes config/option-a-classification.json: {post_id: {"categories": [...], "tags": [...]}}
and prints a summary. Rules are first-pass heuristics for editors to review,
not a final taxonomy.
"""
import collections
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

CATEGORY_RULES = [  # (category, regex)
    ("Event", r"agm|annual general|anniversary|social\b|memorial|walk\b|crawl|meander|festival|woodfest|quiz|curry|buffet|"
              r"national weekend|members weekend|upcoming events|event|trip|outing|derby day|dinner|bash|beer from the wood in|"
              r"beer by the seaside|beer from the wood was|first launch|beer and buffet|branch meeting|branch day|feast|launch|"
              r"dedication|dfeb|postponed|cancelled|saturday|sunday|amsterdam"),
    ("Woodfest", r"woodfest|wbob|woodfest beer"),
    ("Branch News", r"branch|manchester|cobra-cow|campden hill|ightham|colaps|common and aldbrickham|central london"),
    ("Shop", r"polo shirt|online shop|products|clothing"),
    ("Pictures", r"photo"),
]
# Woodfest posts that are reports/results rather than events to attend
NOT_EVENT = re.compile(r"photos|beer list|wbob|voty|volunteer")

TAG_RULES = [
    ("Greater Manchester", r"greater manchester|manchester"),
    ("Central London", r"central london"),
    ("Campden Hill", r"campden hill"),
    ("COBRA-COW", r"cobra-cow"),
    ("Social", r"social\b"),
    ("AGM", r"agm|annual general"),
    ("Anniversary", r"anniversary"),
    ("Memorial", r"memorial|dfeb|full double english"),
    ("Bill English", r"bill english|dfeb|fdeb"),
    ("Walk", r"walk\b|crawl|meander"),
    ("Beer and Curry", r"curry"),
    ("Quiz", r"quiz"),
    ("National Weekend", r"national weekend"),
    ("Woodfest", r"woodfest"),
    ("Beer Festival", r"festival|springfest"),
    ("Beer from the Wood", r"beer from the wood|beers from the wood|bftw"),
    ("Polo Shirts", r"polo shirt"),
    ("Buffet", r"buffet"),
]


def classify(title):
    t = title.lower()
    cats = [c for c, rx in CATEGORY_RULES if re.search(rx, t)]
    if "Event" in cats and "Woodfest" in cats and NOT_EVENT.search(t):
        cats.remove("Event")
    if not cats:
        cats = ["Society News"]
    tags = [g for g, rx in TAG_RULES if re.search(rx, t)]
    return cats, tags


if __name__ == "__main__":
    posts = []
    for f in ("posts", "posts_archived"):
        posts += json.loads((ROOT / "content" / f"{f}.json").read_text())
    names = {c["id"]: c["name"] for c in json.loads((ROOT / "content" / "categories.json").read_text())}
    out, cc, tc, kept = {}, collections.Counter(), collections.Counter(), 0
    for p in sorted(posts, key=lambda x: x["date"]):
        if {names.get(c) for c in p.get("categories", [])} - {"Uncategorised", None}:
            kept += 1
            continue
        title = html.unescape(p["title"]["rendered"])
        cats, tags = classify(title)
        out[str(p["id"])] = {"categories": cats, "tags": tags}
        cc.update(cats)
        tc.update(tags)
        if "--list" in __import__("sys").argv:
            print(f"{p['date'][:10]} {title[:60]:60} {cats} {tags}")
    (ROOT / "config" / "option-a-classification.json").write_text(json.dumps(out, indent=1))
    print(f"kept existing categories on {kept} posts; classified {len(out)} uncategorised posts")
    print("categories:", dict(cc))
    print("tags:", dict(tc))
