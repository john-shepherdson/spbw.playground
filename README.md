[![SQA badge](https://api.eu.badgr.io/public/assertions/<SQAaaS image ID>/image)](https://api.eu.badgr.io/public/badges/<SQAaaS badge ID>)

# SPBW Playground configuration

This repository contains the source code for SPBW Playground configuration

## Prerequisites

Python 3 (standard library only).

## Quick Start

1. Check prerequisites and install any required software.
1. Clone the repository to your local workspace.

## Project Structure

- `scripts/fetch_content.py` - pulls published posts, pages, categories, tags
  and media metadata from the spbw.beer REST API into `content/`.
- `scripts/fetch_archived.py` - the live site uses a custom `archive` status
  that the REST API list hides, so this fetches those posts/pages by ID (found
  via the sitemap).
- `scripts/build_wxr.py` - builds `wxr/spbw-baseline.xml` from `content/`.
  Archived items are imported as published with meta
  `_spbw_original_status=archive`.
- `blueprints/baseline.json` - WordPress Playground Blueprint that imports the
  WXR into a stock WordPress.
- `scripts/classify_posts.py` - keyword rules that assign categories and tags to
  posts (`config/option-a-classification.json`).
- `scripts/event_dates.py` - heuristic extraction of event dates from post
  titles and text.
- `scripts/structure.py` - shared step for every option: Photo Gallery and `-2`
  slug fixes, Our History under About us, and the proposed main menu
  (`redirects/structure.csv`).
- `scripts/build_option_a.py`, `build_option_b.py`, `build_option_c.py` -
  generate `blueprints/option-a.json`, `option-b.json` and `option-c.json`.
- `redirects/` - draft 301 maps (`option-b.csv`, `option-c.csv`,
  `structure.csv`). Old URLs are not redirected automatically in every case, so
  these are required.

Refresh: run `fetch_content.py`, `fetch_archived.py` and `build_wxr.py`, then
`classify_posts.py`, then the three `build_option_*.py` scripts.

## Options

Each option is a Blueprint that rebuilds the site in your browser from the repo.
Nothing touches spbw.beer. They answer the review's question of how Posts and
events should relate. Open one:

| Option                                       | Open in Playground |
| -------------------------------------------- | ------------------ |
| Baseline (current site content, stock theme) | [baseline]         |
| A: categories and tags drive an Events Hub   | [option A]         |
| B: The Events Calendar with dated events     | [option B]         |
| C: one hand-maintained Events hub            | [option C]         |

|                    | A: taxonomy | B: plugin   | C: hybrid |
| ------------------ | ----------- | ----------- | --------- |
| Upcoming/Past      | No          | Automatic   | By hand   |
| New plugin         | None        | Events Cal. | None      |
| Editor effort      | Low         | Higher      | Medium    |
| Duplicates removed | Partly      | Yes         | Yes       |
| Old URLs           | Unchanged   | Redirects   | Redirects |

- A: publish dates only, so no Upcoming/Past split. Editors categorise each
  post.
- B: The Events Calendar gives automatic Upcoming and Past views. Editors enter
  a date for each event, and a redirect map is required.
- C: one hub page plus a Past events page, no plugin. Editors move events
  between the two pages by hand, and a redirect map is required.

Notes:

- After pushing a changed Blueprint, GitHub's raw URL for `main` can serve the
  old file for about 5 minutes, and adding a query parameter does not help. To
  test straight away, use the commit hash in place of `main`:

  ```text
  https://raw.githubusercontent.com/john-shepherdson/spbw.playground/<commit-sha>/blueprints/option-a.json
  ```

- Options A and C can be combined. Better categories help the whole site.
- B converts 77 posts with a date found in the title or text; the date source is
  stored in meta `_spbw_date_source` for review. Venues, times and RSVP are not
  extracted.
- A's classification is keyword-based and needs a human review.
- All options also apply the structure step: Photo Gallery slugs
  (`/photo-gallery/...`), `-2` slugs removed, the stray `/page-3-april-2026/`
  page retired, Our History under About us, and a proposed menu with 8 top-level
  items instead of 14.
- Playground cannot show the live theme (Genesis with a commercial child theme),
  plugins, widgets or media. Images hotlink from spbw.beer.

[baseline]: https://playground.wordpress.net/?blueprint-url=https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/blueprints/baseline.json
[option A]: https://playground.wordpress.net/?blueprint-url=https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/blueprints/option-a.json
[option B]: https://playground.wordpress.net/?blueprint-url=https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/blueprints/option-b.json
[option C]: https://playground.wordpress.net/?blueprint-url=https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/blueprints/option-c.json

## Technology Stack

- Python 3 (standard library only) for the fetch, classification and build
  scripts.
- [WordPress Playground](https://playground.wordpress.net/): WordPress running
  in the browser (PHP compiled to WebAssembly, SQLite as the database), driven
  by [Blueprints](https://wordpress.github.io/wordpress-playground/blueprints/)
  (JSON).
- WordPress eXtended RSS (WXR) as the import format for site content.
- Source content from the public WordPress REST API and sitemap of spbw.beer.
- [The Events Calendar](https://wordpress.org/plugins/the-events-calendar/)
  plugin, installed from wordpress.org by Option B only.
- A stock WordPress block theme (the Playground default). The live site's
  Genesis theme is not reproduced.

## Configuration

There are no environment variables, secrets or credentials. Everything is read
from public endpoints.

- **Source site:** `scripts/fetch_content.py` takes `--base` (default
  `https://spbw.beer`). `scripts/fetch_archived.py` uses `https://www.spbw.beer`
  for sitemap and page requests; change `BASE` in the script to point elsewhere.
- **Blueprint settings:** `blueprints/baseline.json` sets PHP 8.3, the latest
  WordPress, networking on, the site name, and the date-based permalink
  structure `/%year%/%monthnum%/%day%/%postname%/`. The other options are
  generated from it, so change it there and rebuild.
- **WXR location:** the baseline Blueprint loads `wxr/spbw-baseline.xml` from
  `raw.githubusercontent.com/john-shepherdson/spbw.playground/main/`. If the
  repository is renamed, forked or made private, update that URL in
  `blueprints/baseline.json`.
- **Post categories and tags (Option A):** edit the keyword rules in
  `scripts/classify_posts.py`; the output is
  `config/option-a-classification.json`.
- **Event dates (Option B):** the dates and their source (title or text) are in
  `config/option-b-events.json`. Rules are in `scripts/event_dates.py`, and the
  list of retired pages is `RETIRED_PAGES` in `scripts/build_option_b.py`.
- **Menu and slug fixes:** edit `SLUG_FIXES`, `RETIRE` and `menu()` in
  `scripts/structure.py`. The build checks every menu path and fails if a page
  cannot be found.

After changing any of these, rebuild with the steps under Project Structure and
push to `main`.

## Contributing

Please read [CONTRIBUTING](CONTRIBUTING.md) for details on our code of conduct,
and the process for submitting pull requests to us.

## Versioning

See [Semantic Versioning](https://semver.org/) for guidance.

## Contributors

You can find the list of contributors in the [CONTRIBUTORS](CONTRIBUTORS.md)
file.

## License

See the [LICENSE](LICENSE.txt) file.

## CITING

See the [CITATION](CITATION.cff) file.
