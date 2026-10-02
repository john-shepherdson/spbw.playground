#!/usr/bin/env python3
"""Generate blueprints/option-c.json: baseline + one hand-maintained Events hub, no plugin.

- /upcoming-events/ becomes the canonical hub at /events/ (titled Events), with links to
  event-type pages (National Weekend, Woodfests News & Info) and Past events.
- /archived-events-and-meetings/ becomes /events/past/ (Past events).
- The stale archived /events/ and /bftw-pub-events/ pages are retired.
- 'Society History' moves under About us as 'Our History'.
Posts are untouched and stay the announcement stream. Writes redirects/option-c.csv.
"""
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from structure import step as structure_step  # noqa: E402
base = json.loads((ROOT / "blueprints" / "baseline.json").read_text())

PHP = r"""<?php
require '/wordpress/wp-load.php';

function spbw_page($slug) { return get_page_by_path($slug); }

// Retire the stale pages first so the 'events' slug is free
foreach (['events', 'bftw-pub-events'] as $s) {
    $p = spbw_page($s);
    if ($p) { wp_delete_post($p->ID, true); }
}

// Hub: upcoming-events -> /events/
$hub = spbw_page('upcoming-events');
$past = spbw_page('archived-events-and-meetings');
$nw = get_page_by_path('national-and-regional-news-2/national-weekend');
$wf = spbw_page('woodfests-news-info');
if ($hub) {
    $links = ['<a href="' . esc_url(home_url('/events/past/')) . '">Past events</a>'];
    if ($nw) { $links[] = '<a href="' . esc_url(get_permalink($nw)) . '">National Weekend</a>'; }
    if ($wf) { $links[] = '<a href="' . esc_url(get_permalink($wf)) . '">Woodfests News &amp; Info</a>'; }
    wp_update_post(['ID' => $hub->ID, 'post_title' => 'Events', 'post_name' => 'events',
        'post_content' => '<p><strong>Event types and history:</strong> ' . implode(' | ', $links) . '</p>' . $hub->post_content]);
    if ($past) {
        wp_update_post(['ID' => $past->ID, 'post_title' => 'Past events', 'post_name' => 'past', 'post_parent' => $hub->ID]);
    }
}

// Our History under About us
$hist = spbw_page('society-history');
$about = spbw_page('about-us');
if ($hist && $about) {
    wp_update_post(['ID' => $hist->ID, 'post_title' => 'Our History', 'post_name' => 'our-history', 'post_parent' => $about->ID]);
}

wp_delete_post(1, true);
$sample = spbw_page('sample-page');
if ($sample) { wp_delete_post($sample->ID, true); }
flush_rewrite_rules();
"""

bp = dict(base)
bp["meta"] = {**base["meta"], "title": "SPBW Option C: one hand-maintained Events hub",
              "description": "Baseline plus a single canonical Events hub (Upcoming plus Past), no plugin. Posts stay as news."}
bp["landingPage"] = "/events/"
bp["steps"] = base["steps"] + [{"step": "runPHP", "code": PHP}]
bp["steps"].append(structure_step({"url": "/events/", "children": [{"label": "Upcoming events", "url": "/events/"}, {"label": "Past events", "url": "/events/past/"}, {"label": "National Weekend", "path": "national-and-regional-news/national-weekend"}]}))
(ROOT / "blueprints" / "option-c.json").write_text(json.dumps(bp, indent=2))

rows = [("/upcoming-events/", "/events/"),
        ("/archived-events-and-meetings/", "/events/past/"),
        ("/bftw-pub-events/", "/events/past/"),
        ("/society-history/", "/about-us/our-history/")]
with open(ROOT / "redirects" / "option-c.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["old_path", "new_path"])
    w.writerows(rows)
print("wrote blueprints/option-c.json and redirects/option-c.csv")
