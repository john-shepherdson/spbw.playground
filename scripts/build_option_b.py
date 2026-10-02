#!/usr/bin/env python3
"""Generate blueprints/option-b.json: baseline + The Events Calendar with real event dates.

Event-category posts whose title or text contains a date become tribe_events
(all-day, dated); the original post is removed and its URL kept in meta and in
redirects/option-b.csv. Dates are heuristic (scripts/event_dates.py): the
source ('title' or 'content') is stored in meta _spbw_date_source for review.
Run classify_posts.py first.
"""
import csv
import datetime as dt
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from structure import step as structure_step  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
from event_dates import extract  # noqa: E402

NOT_EVENTS = re.compile(r"upcoming events|event details updated|events page now live|^update:", re.I)
RETIRED_PAGES = ["events", "upcoming-events", "archived-events-and-meetings", "bftw-pub-events"]

base = json.loads((ROOT / "blueprints" / "baseline.json").read_text())
cls = json.loads((ROOT / "config" / "option-a-classification.json").read_text())

events, redirects = {}, []
for f in ("posts", "posts_archived"):
    for p in json.loads((ROOT / "content" / f"{f}.json").read_text()):
        c = cls[str(p["id"])]
        title = html.unescape(p["title"]["rendered"])
        if "Event" not in c["categories"] or NOT_EVENTS.search(title):
            continue
        start, end, src = extract(title, p["content"]["rendered"], dt.date.fromisoformat(p["date"][:10]))
        if not start:
            continue
        events[p["slug"]] = {"start": start.isoformat(), "end": (end or start).isoformat(), "source": src,
                             "url": p["link"],
                             "cats": [x for x in c["categories"] if x != "Event"], "tags": c["tags"]}
        redirects.append((p["link"].replace("https://www.spbw.beer", ""), f"/event/{p['slug']}/"))
for s in RETIRED_PAGES:
    redirects.append((f"/{s}/", "/events/"))

(ROOT / "config" / "option-b-events.json").write_text(json.dumps(events, indent=1))
(ROOT / "redirects").mkdir(exist_ok=True)
with open(ROOT / "redirects" / "option-b.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["old_path", "new_path"])
    w.writerows(redirects)

PHP = r"""<?php
require '/wordpress/wp-load.php';
$events = json_decode(<<<'JSON'
__EVENTS__
JSON
, true);

foreach ($events as $slug => $e) {
    $posts = get_posts(['name' => $slug, 'post_type' => 'post', 'post_status' => 'any', 'numberposts' => 1]);
    if (!$posts) { continue; }
    $p = $posts[0];
    $id = wp_insert_post([
        'post_type' => 'tribe_events', 'post_status' => 'publish', 'post_title' => $p->post_title,
        'post_content' => $p->post_content, 'post_name' => $slug, 'post_date' => $p->post_date,
        'post_date_gmt' => $p->post_date_gmt,
    ]);
    if (!$id || is_wp_error($id)) { continue; }
    $start = $e['start'] . ' 00:00:00';
    $end = $e['end'] . ' 23:59:59';
    $dur = strtotime($end) - strtotime($start);
    foreach ([
        '_EventStartDate' => $start, '_EventEndDate' => $end, '_EventStartDateUTC' => $start, '_EventEndDateUTC' => $end,
        '_EventDuration' => $dur, '_EventAllDay' => 'yes', '_EventTimezone' => 'UTC', '_EventTimezoneAbbr' => 'UTC',
        '_spbw_date_source' => $e['source'], '_spbw_original_url' => $e['url'],
    ] as $k => $v) { update_post_meta($id, $k, $v); }
    if ($e['cats']) { wp_set_object_terms($id, $e['cats'], 'tribe_events_cat'); }
    if ($e['tags']) { wp_set_object_terms($id, $e['tags'], 'post_tag'); }
    wp_delete_post($p->ID, true);
}

// Retire the overlapping hand-maintained events pages (301s: redirects/option-b.csv)
foreach (__RETIRED__ as $s) {
    $pg = get_page_by_path($s);
    if ($pg) { wp_delete_post($pg->ID, true); }
}
wp_delete_post(1, true);
$sample = get_page_by_path('sample-page');
if ($sample) { wp_delete_post($sample->ID, true); }
flush_rewrite_rules();
"""
php = PHP.replace("__EVENTS__", json.dumps(events)).replace("__RETIRED__", "[" + ",".join(f"'{s}'" for s in RETIRED_PAGES) + "]")

bp = dict(base)
bp["meta"] = {**base["meta"], "title": "SPBW Option B: The Events Calendar with dated events",
              "description": "Baseline plus The Events Calendar. Dated posts become real events with Upcoming/Past views."}
bp["landingPage"] = "/events/"
bp["steps"] = base["steps"] + [
    {"step": "installPlugin", "pluginData": {"resource": "wordpress.org/plugins", "slug": "the-events-calendar"},
     "options": {"activate": True}},
    {"step": "runPHP", "code": php},
]
bp["steps"].append(structure_step({"url": "/events/", "children": [{"label": "Upcoming events", "url": "/events/"}, {"label": "Past events", "url": "/events/list/?eventDisplay=past"}, {"label": "National Weekend", "path": "national-and-regional-news-2/national-weekend"}]}))
(ROOT / "blueprints" / "option-b.json").write_text(json.dumps(bp, indent=2))
src = {}
for v in events.values():
    src[v["source"]] = src.get(v["source"], 0) + 1
print(f"{len(events)} events ({src}); {len(redirects)} redirects")
