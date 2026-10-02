#!/usr/bin/env python3
"""Generate blueprints/option-b.json: baseline + The Events Calendar fed from the live event tables.

The hand-maintained tables on /upcoming-events/, /archived-events-and-meetings/ and the
old /events/ page (Event, Date/Time, Venue, Details, Contact) become real events with
dates, times and venues. Posts are left untouched as the announcement stream. The four
overlapping events pages are retired. Writes config/option-b-events.json and
redirects/option-b.csv. Run import_export.py (or the fetch scripts) first.
"""
import csv
import datetime as dt
import difflib
import json
import pathlib
import re
import sys
import zoneinfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from classify_posts import classify  # noqa: E402
from event_tables import parse  # noqa: E402
from structure import step as structure_step  # noqa: E402

SOURCES = ["upcoming-events", "archived-events-and-meetings", "events"]  # priority order for duplicates
RETIRED_PAGES = ["events", "upcoming-events", "archived-events-and-meetings", "bftw-pub-events"]
CAT_TAGS = {"Woodfest", "National Weekend", "AGM", "Anniversary", "Memorial", "Social", "Walk", "Beer Festival", "Quiz"}
TZ = zoneinfo.ZoneInfo("Europe/London")
DEFAULT_HOURS = 3  # no end times in the source tables

base = json.loads((ROOT / "blueprints" / "baseline.json").read_text())
pages = {}
for f in ("pages", "pages_archived"):
    for p in json.loads((ROOT / "content" / f"{f}.json").read_text()):
        pages[p["slug"]] = p

events, unparsed = [], []
for s in SOURCES:
    found, bad = parse(pages[s]["content"]["rendered"], s)
    unparsed += bad
    for e in found:
        dup = any(o["start"] == e["start"] and difflib.SequenceMatcher(None, o["title"].lower(), e["title"].lower()).ratio() >= 0.45
                  for o in events)
        if not dup:
            events.append(e)
events.sort(key=lambda e: (e["start"], e["time"] or ""))

out = []
for e in events:
    start = dt.date.fromisoformat(e["start"])
    end = dt.date.fromisoformat(e["end"]) if e["end"] else start
    if e["time"]:
        hh, mm = map(int, e["time"].split(":"))
        ls = dt.datetime.combine(start, dt.time(hh, mm), TZ)
        le = ls + dt.timedelta(hours=DEFAULT_HOURS)
        allday = False
    else:
        ls = dt.datetime.combine(start, dt.time(0, 0), TZ)
        le = dt.datetime.combine(end, dt.time(23, 59, 59), TZ)
        allday = True
    utc = lambda d: d.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")  # noqa: E731
    name, _, addr = e["venue"].partition(",")
    tags = [t for _, t in [(0, t) for t in classify(e["title"])[1]]]
    out.append({"title": e["title"], "start": ls.strftime("%Y-%m-%d %H:%M:%S"), "end": le.strftime("%Y-%m-%d %H:%M:%S"),
                "start_utc": utc(ls), "end_utc": utc(le), "all_day": allday, "tz_abbr": ls.tzname(),
                "venue": name.strip(), "address": addr.strip(), "when": e["when"], "source": e["source"],
                "date_check": "" if e["weekday_ok"] else "weekday does not match date in source",
                "content": (f"<p><strong>When:</strong> {e['when']}</p>" + e["details"]
                            + (f"<p><strong>Contact:</strong> {e['contact']}</p>" if e["contact"] else "")),
                "tags": tags, "cats": [t for t in tags if t in CAT_TAGS]})

(ROOT / "config" / "option-b-events.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
(ROOT / "redirects").mkdir(exist_ok=True)
with open(ROOT / "redirects" / "option-b.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["old_path", "new_path"])
    w.writerows([("/upcoming-events/", "/events/"), ("/archived-events-and-meetings/", "/events/list/?eventDisplay=past"),
                 ("/bftw-pub-events/", "/events/list/?eventDisplay=past")])

PHP = r"""<?php
require '/wordpress/wp-load.php';
update_option('timezone_string', 'Europe/London');
$events = json_decode(<<<'JSON'
__EVENTS__
JSON
, true);
$venues = [];
foreach ($events as $e) {
    $vid = 0;
    if ($e['venue'] !== '' && function_exists('tribe_create_venue')) {
        $k = $e['venue'] . '|' . $e['address'];
        if (!isset($venues[$k])) { $venues[$k] = tribe_create_venue(['Venue' => $e['venue'], 'Address' => $e['address'], 'ShowMap' => 'false']); }
        $vid = $venues[$k];
    }
    $id = wp_insert_post(['post_type' => 'tribe_events', 'post_status' => 'publish', 'post_title' => $e['title'], 'post_content' => $e['content']]);
    if (!$id || is_wp_error($id)) { continue; }
    $dur = strtotime($e['end_utc']) - strtotime($e['start_utc']);
    foreach ([
        '_EventStartDate' => $e['start'], '_EventEndDate' => $e['end'], '_EventStartDateUTC' => $e['start_utc'],
        '_EventEndDateUTC' => $e['end_utc'], '_EventDuration' => $dur, '_EventAllDay' => $e['all_day'] ? 'yes' : '',
        '_EventTimezone' => 'Europe/London', '_EventTimezoneAbbr' => $e['tz_abbr'], '_EventVenueID' => $vid,
        '_spbw_source_page' => $e['source'], '_spbw_date_text' => $e['when'], '_spbw_date_check' => $e['date_check'],
    ] as $k => $v) { update_post_meta($id, $k, $v); }
    if ($e['cats']) { wp_set_object_terms($id, $e['cats'], 'tribe_events_cat'); }
    if ($e['tags']) { wp_set_object_terms($id, $e['tags'], 'post_tag'); }
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
php = PHP.replace("__EVENTS__", json.dumps(out, ensure_ascii=False)).replace(
    "__RETIRED__", "[" + ",".join(f"'{s}'" for s in RETIRED_PAGES) + "]")

bp = dict(base)
bp["meta"] = {**base["meta"], "title": "SPBW Option B: The Events Calendar fed from the event tables",
              "description": "Baseline plus The Events Calendar. The hand-maintained event tables become real events."}
bp["landingPage"] = "/events/"
bp["steps"] = base["steps"] + [
    {"step": "installPlugin", "pluginData": {"resource": "wordpress.org/plugins", "slug": "the-events-calendar"},
     "options": {"activate": True}},
    {"step": "runPHP", "code": php},
]
bp["steps"].append(structure_step({"url": "/events/", "children": [
    {"label": "Upcoming events", "url": "/events/"}, {"label": "Past events", "url": "/events/list/?eventDisplay=past"},
    {"label": "National Weekend", "path": "national-and-regional-news/national-weekend"}]}))
(ROOT / "blueprints" / "option-b.json").write_text(json.dumps(bp, indent=2))
withtime = sum(1 for e in out if not e["all_day"])
print(f"{len(out)} events ({withtime} with a start time, {len(out) - withtime} all-day); "
      f"{len({e['venue'] for e in out})} venues; {len(unparsed)} unparsed; "
      f"{sum(1 for e in out if e['date_check'])} date flags")
