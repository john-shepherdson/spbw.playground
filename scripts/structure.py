"""Shared site-structure step used by every option Blueprint.

Fixes slug cruft (Photo Gallery, '-2' slugs, stray root page), moves Society History
under About us, and builds the proposed main menu as a block-theme navigation.
Writes redirects/structure.csv. Option builders call step(events_menu).

events_menu: dict with 'url' (Events parent link, site-relative) and 'children'
(list of {"label", "path"} for a page path or {"label", "url"} for a site-relative URL).
"""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (current page path, new slug, new title or None)
SLUG_FIXES = [
    ("photographs-taken-by-spbw-members/photographs-taken-by-spbw-members", "2017-to-2025-07", None),
    ("photographs-taken-by-spbw-members/photographs-taken-by-spbw-members-2", "2025-08-to-2026-03", None),
    ("photographs-taken-by-spbw-members/page-3", "2026-04-to-2026-09", None),
    ("photographs-taken-by-spbw-members/bill-english-dfeb", "bill-english-dfeb-amsterdam-2026", None),
    ("photographs-taken-by-spbw-members", "photo-gallery", "Photo Gallery"),
    ("national-and-regional-news-2", "national-and-regional-news", None),
    ("lpoty-2", "lpoty", None),
]
RETIRE = ["page-3-april-2026"]  # stray archived duplicate of Photo Gallery page 3

REDIRECTS = [
    ("/photographs-taken-by-spbw-members/", "/photo-gallery/"),
    ("/photographs-taken-by-spbw-members/photographs-taken-by-spbw-members/", "/photo-gallery/2017-to-2025-07/"),
    ("/photographs-taken-by-spbw-members/photographs-taken-by-spbw-members-2/", "/photo-gallery/2025-08-to-2026-03/"),
    ("/photographs-taken-by-spbw-members/page-3/", "/photo-gallery/2026-04-to-2026-09/"),
    ("/photographs-taken-by-spbw-members/bill-english-dfeb/", "/photo-gallery/bill-english-dfeb-amsterdam-2026/"),
    ("/page-3-april-2026/", "/photo-gallery/2026-04-to-2026-09/"),
    ("/national-and-regional-news-2/", "/national-and-regional-news/"),
    ("/lpoty-2/", "/lpoty/"),
]


def menu(events):
    P = lambda label, path: {"label": label, "path": path}  # noqa: E731
    return [
        {"label": "Home", "url": "/"},
        {"label": "About us", "path": "about-us", "children": [
            P("Aims", "about-us/history"), P("Our History", "about-us/our-history"), P("N.E.C.", "about-us/n-e-c"),
            P("Branches", "about-us/branches"), P("Lapsed Branches", "about-us/defunct-branches"),
            P("Role of Honour", "role-of-honour"), P("Woodfest Collective (Committee)", "about-us/woodfest-collective-committee"),
            P("Regional Wood Liaison Officers", "regional-wood-liaison-officers-rwlo")]},
        {"label": "Events", "url": events["url"], "children": events["children"]},
        {"label": "Woodfests", "path": "woodfests-news-info", "children": [
            P("Woodfests News and Info", "woodfests-news-info"), P("Beer List", "woodfest-beer-list"),
            P("Previous Venues and WBOB Winners", "previous-woodfest-venues-wbob-winners"),
            P("Volunteer of the Festival", "woodfest-volunteer-of-the-festival"),
            P("Beer In The Wood Breweries", "brewery-directory")]},
        {"label": "Photo Gallery", "path": "photo-gallery", "children": [
            P("2017 to July 2025", "photo-gallery/2017-to-2025-07"), P("August 2025 to March 2026", "photo-gallery/2025-08-to-2026-03"),
            P("April 2026 to September 2026", "photo-gallery/2026-04-to-2026-09"),
            P("Bill English (DFEB) Amsterdam Memorial", "photo-gallery/bill-english-dfeb-amsterdam-2026")]},
        {"label": "Information", "path": "information", "children": [
            P("Pint In Hand Magazine", "information/pint-in-hand"), P("Wood", "information/wood"),
            P("Starting a Branch", "starting-a-branch"), P("Join", "information/join"), P("Disclaimer", "information/disclaimer")]},
        {"label": "Online Shop", "path": "online-shop"},
        {"label": "Contact Us", "path": "contact-us"},
    ]


PHP = r"""<?php
require '/wordpress/wp-load.php';

foreach (__RETIRE__ as $s) { $p = get_page_by_path($s); if ($p) { wp_delete_post($p->ID, true); } }
foreach (__FIXES__ as $f) {
    $p = get_page_by_path($f[0]);
    if (!$p) { continue; }
    $a = ['ID' => $p->ID, 'post_name' => $f[1]];
    if ($f[2]) { $a['post_title'] = $f[2]; }
    wp_update_post($a);
}
// Society History -> About us > Our History (Option C already does this)
$h = get_page_by_path('society-history');
$about = get_page_by_path('about-us');
if ($h && $about) { wp_update_post(['ID' => $h->ID, 'post_title' => 'Our History', 'post_name' => 'our-history', 'post_parent' => $about->ID]); }

function spbw_url($i) {
    if (isset($i['path'])) { $p = get_page_by_path($i['path']); return $p ? get_permalink($p) : home_url('/'); }
    return home_url($i['url']);
}
function spbw_block($i) {
    $a = wp_json_encode(['label' => $i['label'], 'url' => spbw_url($i), 'kind' => 'custom'], JSON_UNESCAPED_SLASHES);
    if (empty($i['children'])) { return '<!-- wp:navigation-link ' . $a . ' /-->'; }
    $out = '<!-- wp:navigation-submenu ' . $a . ' -->';
    foreach ($i['children'] as $c) { $out .= spbw_block($c); }
    return $out . '<!-- /wp:navigation-submenu -->';
}
$menu = json_decode(<<<'JSON'
__MENU__
JSON
, true);
$markup = '';
foreach ($menu as $i) { $markup .= spbw_block($i); }
wp_insert_post(['post_type' => 'wp_navigation', 'post_status' => 'publish', 'post_title' => 'Proposed main menu', 'post_content' => $markup]);
"""


def step(events):
    php = (PHP.replace("__RETIRE__", json.dumps(RETIRE))
              .replace("__FIXES__", json.dumps(SLUG_FIXES))
              .replace("__MENU__", json.dumps(menu(events))))
    with open(ROOT / "redirects" / "structure.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["old_path", "new_path"])
        w.writerows(REDIRECTS + [("/society-history/", "/about-us/our-history/")])
    return {"step": "runPHP", "code": php}
