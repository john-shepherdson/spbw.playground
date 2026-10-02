[![SQAaaS badge shields.io](https://img.shields.io/badge/sqaaas%20software-silver-lightgrey)](https://sqaaas.eosc-synergy.eu/full-assessment/report/https://raw.githubusercontent.com/eosc-synergy/spbw.playground.git.assess.sqaaas/main/.report/assessment_output.json "SQAaaS silver badge achieved")

# SPBW Playground configuration

This repository contains the source code for SPBW Playground configuration

## Prerequisites

Python 3 (standard library only).

## Quick Start

1. Check prerequisites and install any required software.
1. Clone the repository to your local workspace.

## Project Structure

- `scripts/import_export.py` - converts a WordPress admin export (the "All
  content" option under Tools, Export, kept in the git-ignored `private/`
  folder) into `content/*.json`. Only published and archived posts and pages are
  kept, so drafts, users and logs never reach the repo. This is the main content
  source.
- `scripts/fetch_content.py` and `scripts/fetch_archived.py` - the earlier route
  when there was no admin access: pull content from the public REST API and, for
  the custom `archive` status that the API list hides, by ID via the sitemap.
  These produce theme-processed text, so prefer the export.
- `scripts/build_wxr.py` - builds `wxr/spbw-baseline.xml` from `content/`.
  Archived items are imported as published with meta
  `_spbw_original_status=archive`.
- `config/baseline-template.json` - the baseline Blueprint settings (PHP and
  WordPress versions, site name, permalinks, WXR import).
- `scripts/build_baseline.py` - generates `blueprints/baseline.json` from the
  template, adding a step for each image in `media/`.
- `media/` and `scripts/make_sample_media.py` - sample images loaded into the
  Media Library, and the script that generated the placeholders.
- `scripts/classify_posts.py` - keyword rules that assign categories and tags to
  posts (`config/option-a-classification.json`).
- `scripts/event_tables.py` - parses the hand-maintained event tables on the
  live events pages (Event, Date/Time, Venue, Details, Contact) into dated
  events with times and venues.
- `scripts/structure.py` - shared step for every option: Photo Gallery and `-2`
  slug fixes, Our History under About us, and the proposed main menu
  (`redirects/structure.csv`).
- `scripts/build_option_a.py`, `build_option_b.py`, `build_option_c.py` -
  generate `blueprints/option-a.json`, `option-b.json` and `option-c.json`.
- `redirects/` - draft 301 maps (`option-b.csv`, `option-c.csv`,
  `structure.csv`). Old URLs are not redirected automatically in every case, so
  these are required.

Refresh: export the content from WordPress admin into `private/`, then run
`import_export.py <file>`, `build_wxr.py`, `build_baseline.py` and
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
- B builds 66 events from the live event tables (about 50 with a start time, the
  rest all-day), with venues. Dates are parsed from free text and one weekday
  mismatch in the source is flagged in meta `_spbw_date_check`. End times are
  not in the source, so timed events default to three hours. Posts are left as
  they are.
- A keeps the categories editors have already assigned (83 posts) and classifies
  only the 53 still Uncategorised, using keyword rules that need a human review.
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

## Media

Playground keeps uploads inside the browser, so anything uploaded in a preview
is lost when it closes, and it is not saved to this repository. To make images
appear in every preview, add them to `media/` (PNG, JPEG, GIF or WebP), run
`scripts/build_baseline.py` and the three `build_option_*.py` scripts, then
commit and push. Each image is loaded into the Media Library when a preview
starts. Three placeholder images (`sample-1.png` to `sample-3.png`) are
included.

Keep `media/` small: the images are downloaded every time a preview starts, and
Git is not suited to large photo collections. The pages imported from spbw.beer
still show their original images straight from the live site; they are not
copied into the repository.

## Technology Stack

- Python 3 (standard library only) for the fetch, classification and build
  scripts.
- [WordPress Playground](https://playground.wordpress.net/): WordPress running
  in the browser (PHP compiled to WebAssembly, SQLite as the database), driven
  by [Blueprints](https://wordpress.github.io/wordpress-playground/blueprints/)
  (JSON).
- WordPress eXtended RSS (WXR) as the import format for site content.
- Source content from a WordPress admin export, and earlier from the public REST
  API and sitemap of spbw.beer.
- [The Events Calendar](https://wordpress.org/plugins/the-events-calendar/)
  plugin, installed from wordpress.org by Option B only.
- A stock WordPress block theme (the Playground default). The live site's
  Genesis theme is not reproduced.

## Configuration

There are no environment variables, secrets or credentials. Everything is read
from public endpoints.

- **Source content:** `scripts/import_export.py` takes the path of the export
  file. The export holds private data (drafts and users, if any exist), so keep
  it in `private/`, which is git-ignored. For the older route,
  `scripts/fetch_content.py` takes `--base` (default `https://spbw.beer`) and
  `scripts/fetch_archived.py` uses `https://www.spbw.beer`; change `BASE` in the
  script to point elsewhere.
- **Blueprint settings:** `config/baseline-template.json` sets PHP 8.3, the
  latest WordPress, networking on, the site name, and the date-based permalink
  structure `/%year%/%monthnum%/%day%/%postname%/`. `blueprints/baseline.json`
  and the other options are generated from it, so change it there and rebuild.
- **WXR and media location:** the baseline Blueprint loads
  `wxr/spbw-baseline.xml` from
  `raw.githubusercontent.com/john-shepherdson/spbw.playground/main/`, and
  `scripts/build_baseline.py` loads `media/` from the same place. If the
  repository is renamed, forked or made private, update the URL in
  `config/baseline-template.json` and `RAW` in `scripts/build_baseline.py`.
- **Post categories and tags (Option A):** edit the keyword rules in
  `scripts/classify_posts.py`; the output is
  `config/option-a-classification.json`.
- **Events (Option B):** the 66 events, their dates, venues and source page are
  in `config/option-b-events.json`. Parsing rules are in
  `scripts/event_tables.py`, duplicate handling and the three-hour default
  length are in `scripts/build_option_b.py`, along with `RETIRED_PAGES`, the
  list of retired pages.
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
