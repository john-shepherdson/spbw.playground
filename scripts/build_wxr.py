#!/usr/bin/env python3
"""Build wxr/spbw-baseline.xml from content/*.json (live + archived posts/pages).

Items keep their original IDs, slugs, dates, parents and menu order. The live
site's custom 'archive' status doesn't exist in a stock WordPress, so archived
items are imported as 'publish' with postmeta _spbw_original_status=archive.
Media is not imported: content keeps pointing at spbw.beer URLs.
"""
import json
import pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
C = ROOT / "content"


def load(name):
    p = C / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else []


def cd(s):
    return "<![CDATA[" + (s or "").replace("]]>", "]]]]><![CDATA[>") + "]]>"


cats, tags = load("categories"), load("tags")
cat_by_id = {c["id"]: c for c in cats}
tag_by_id = {t["id"]: t for t in tags}

out = ['<?xml version="1.0" encoding="UTF-8" ?>',
       '<rss version="2.0" xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/" '
       'xmlns:content="http://purl.org/rss/1.0/modules/content/" '
       'xmlns:wfw="http://wellformedweb.org/CommentAPI/" xmlns:dc="http://purl.org/dc/elements/1.1/" '
       'xmlns:wp="http://wordpress.org/export/1.2/"><channel>',
       "<title>SPBW baseline</title><link>https://www.spbw.beer</link>",
       "<wp:wxr_version>1.2</wp:wxr_version>",
       "<wp:base_site_url>https://www.spbw.beer</wp:base_site_url>",
       "<wp:base_blog_url>https://www.spbw.beer</wp:base_blog_url>"]
for c in cats:
    out.append(f"<wp:category><wp:term_id>{c['id']}</wp:term_id><wp:category_nicename>{escape(c['slug'])}"
               f"</wp:category_nicename><wp:category_parent></wp:category_parent>"
               f"<wp:cat_name>{cd(c['name'])}</wp:cat_name></wp:category>")
for t in tags:
    out.append(f"<wp:tag><wp:term_id>{t['id']}</wp:term_id><wp:tag_slug>{escape(t['slug'])}</wp:tag_slug>"
               f"<wp:tag_name>{cd(t['name'])}</wp:tag_name></wp:tag>")

n = 0
for kind, ptype in (("pages", "page"), ("posts", "post")):
    for src in ("", "_archived"):
        for it in load(kind + src):
            archived = it["status"] == "archive"
            status = "publish" if archived or it["status"] == "publish" else it["status"]
            out.append("<item>")
            out.append(f"<title>{cd(it['title']['rendered'])}</title><link>{escape(it['link'])}</link>")
            out.append(f"<dc:creator>{cd('admin')}</dc:creator><guid isPermaLink=\"false\">{escape(it['guid']['rendered'])}</guid>")
            out.append(f"<content:encoded>{cd(it['content']['rendered'])}</content:encoded>")
            out.append(f"<excerpt:encoded>{cd(it.get('excerpt', {}).get('rendered', ''))}</excerpt:encoded>")
            out.append(f"<wp:post_id>{it['id']}</wp:post_id><wp:post_date>{it['date']}</wp:post_date>"
                       f"<wp:post_date_gmt>{it.get('date_gmt', it['date'])}</wp:post_date_gmt>")
            out.append(f"<wp:post_name>{cd(it['slug'])}</wp:post_name><wp:status>{status}</wp:status>"
                       f"<wp:post_parent>{it.get('parent', 0)}</wp:post_parent>"
                       f"<wp:menu_order>{it.get('menu_order', 0)}</wp:menu_order><wp:post_type>{ptype}</wp:post_type>")
            for cid in it.get("categories", []):
                if cid in cat_by_id:
                    c = cat_by_id[cid]
                    out.append(f'<category domain="category" nicename="{escape(c["slug"])}">{cd(c["name"])}</category>')
            for tid in it.get("tags", []):
                if tid in tag_by_id:
                    t = tag_by_id[tid]
                    out.append(f'<category domain="post_tag" nicename="{escape(t["slug"])}">{cd(t["name"])}</category>')
            if archived:
                out.append("<wp:postmeta><wp:meta_key>_spbw_original_status</wp:meta_key>"
                           "<wp:meta_value>archive</wp:meta_value></wp:postmeta>")
            out.append("</item>")
            n += 1
out.append("</channel></rss>")
dest = ROOT / "wxr" / "spbw-baseline.xml"
dest.write_text("\n".join(out), encoding="utf-8")
print(f"wrote {dest.relative_to(ROOT)}: {n} items, {dest.stat().st_size // 1024} KB")
