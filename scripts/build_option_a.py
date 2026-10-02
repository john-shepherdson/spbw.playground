#!/usr/bin/env python3
"""Generate blueprints/option-a.json: baseline + taxonomy cleanup + auto-populated Events hub.

Run classify_posts.py first. Posts are matched by slug (IDs can change on import).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from structure import step as structure_step  # noqa: E402
base = json.loads((ROOT / "blueprints" / "baseline.json").read_text())
cls = json.loads((ROOT / "config" / "option-a-classification.json").read_text())

by_slug = {}
for f in ("posts", "posts_archived"):
    for p in json.loads((ROOT / "content" / f"{f}.json").read_text()):
        by_slug[p["slug"]] = cls[str(p["id"])]

PHP = r"""<?php
require '/wordpress/wp-load.php';
$map = json_decode(<<<'JSON'
__MAP__
JSON
, true);

// 1. Apply categories and tags (keep existing non-default categories such as Important)
foreach ($map as $slug => $terms) {
    $posts = get_posts(['name' => $slug, 'post_type' => 'post', 'post_status' => 'any', 'numberposts' => 1]);
    if (!$posts) { continue; }
    $id = $posts[0]->ID;
    $cur = wp_get_post_categories($id, ['fields' => 'names']);
    $cur = array_diff($cur, ['Uncategorised', 'Uncategorized']);
    wp_set_object_terms($id, array_values(array_unique(array_merge($cur, $terms['categories']))), 'category');
    if ($terms['tags']) { wp_set_object_terms($id, $terms['tags'], 'post_tag', true); }
}

// 2. Remove default sample content and the now-empty live 'Uncategorised' term
wp_delete_post(1, true);
$sample = get_page_by_path('sample-page');
if ($sample) { wp_delete_post($sample->ID, true); }
$unc = get_term_by('slug', 'uncategorised', 'category');
if ($unc && $unc->count == 0) { wp_delete_term($unc->term_id, 'category'); }

// 3. Events hub: type links plus a Query Loop fed by the Event category
$event = get_term_by('name', 'Event', 'category');
$links = [];
foreach (['Woodfest', 'National Weekend', 'AGM', 'Anniversary', 'Memorial', 'Social', 'Walk', 'Beer Festival', 'Quiz'] as $name) {
    $t = get_term_by('name', $name, 'post_tag');
    if ($t) { $links[] = '<a href="' . esc_url(get_term_link($t)) . '">' . esc_html($name) . '</a>'; }
}
$q = '{"queryId":1,"query":{"perPage":20,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date",'
   . '"author":"","search":"","exclude":[],"sticky":"","inherit":false,"taxQuery":{"category":[' . (int) $event->term_id . ']}}}';
$content = '<!-- wp:paragraph --><p>Everything we announce, in one place. Filter by type: ' . implode(' | ', $links) . '</p><!-- /wp:paragraph -->'
  . '<!-- wp:query ' . $q . ' --><div class="wp-block-query"><!-- wp:post-template -->'
  . '<!-- wp:post-title {"isLink":true,"level":3} /--><!-- wp:post-date /--><!-- wp:post-excerpt {"excerptLength":30} /-->'
  . '<!-- /wp:post-template --><!-- wp:query-pagination --><!-- wp:query-pagination-previous /-->'
  . '<!-- wp:query-pagination-numbers /--><!-- wp:query-pagination-next /--><!-- /wp:query-pagination --></div><!-- /wp:query -->';
wp_insert_post(['post_type' => 'page', 'post_status' => 'publish', 'post_title' => 'Events Hub',
                'post_name' => 'events-hub', 'post_content' => $content]);
"""

step = {"step": "runPHP", "code": PHP.replace("__MAP__", json.dumps(by_slug, indent=0))}
bp = dict(base)
bp["meta"] = {**base["meta"], "title": "SPBW Option A: categories and tags drive the Events hub",
              "description": "Baseline plus a real taxonomy and an auto-populated Events Hub page (Query Loop). No plugins."}
bp["landingPage"] = "/events-hub/"
bp["steps"] = base["steps"] + [step]
bp["steps"].append(structure_step({"url": "/events-hub/", "children": [{"label": "National Weekend", "path": "national-and-regional-news-2/national-weekend"}]}))
(ROOT / "blueprints" / "option-a.json").write_text(json.dumps(bp, indent=2))
print("wrote blueprints/option-a.json with", len(by_slug), "posts mapped")
