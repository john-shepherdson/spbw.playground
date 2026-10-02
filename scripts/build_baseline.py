#!/usr/bin/env python3
"""Generate blueprints/baseline.json from config/baseline-template.json plus media/.

Each image in media/ is fetched from this repo's raw GitHub URL into the
WordPress uploads folder, then registered in the Media Library. All option
Blueprints are built from the generated baseline.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/media/"
DIR = "/wordpress/wp-content/uploads/spbw-samples"
EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}

REGISTER = r"""<?php
require '/wordpress/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/image.php';
foreach (__FILES__ as $name => $mime) {
    $path = '__DIR__/' . $name;
    if (!file_exists($path)) { continue; }
    $id = wp_insert_attachment([
        'post_mime_type' => $mime, 'post_title' => pathinfo($name, PATHINFO_FILENAME),
        'post_status' => 'inherit',
    ], $path);
    if ($id && !is_wp_error($id)) {
        wp_update_attachment_metadata($id, wp_generate_attachment_metadata($id, $path));
        update_post_meta($id, '_wp_attachment_image_alt', 'Sample image ' . pathinfo($name, PATHINFO_FILENAME));
    }
}
"""

def php_array(d):
    return "[" + ", ".join(f"{json.dumps(k)} => {json.dumps(v)}" for k, v in d.items()) + "]"


bp = json.loads((ROOT / "config" / "baseline-template.json").read_text())
files = {p.name: EXT[p.suffix.lower()] for p in sorted((ROOT / "media").iterdir()) if p.suffix.lower() in EXT}
if files:
    bp["steps"].append({"step": "mkdir", "path": DIR})
    for name in files:
        bp["steps"].append({"step": "writeFile", "path": f"{DIR}/{name}",
                            "data": {"resource": "url", "url": RAW + name}})
    bp["steps"].append({"step": "runPHP", "code": REGISTER.replace("__FILES__", php_array(files)).replace("__DIR__", DIR)})
(ROOT / "blueprints" / "baseline.json").write_text(json.dumps(bp, indent=2))
print(f"wrote blueprints/baseline.json with {len(files)} media files")
