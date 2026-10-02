[![SQA badge](https://api.eu.badgr.io/public/assertions/<SQAaaS image ID>/image)](https://api.eu.badgr.io/public/badges/<SQAaaS badge ID>)

# SPBW Playground configuration

This repository contains the source code for SPBW Playground configuration

## Prerequisites

Python 3 (standard library only).

## Quick Start

1. Check prerequisites and install any required software.
1. Clone the repository to your local workspace.

## Project Structure

- `scripts/fetch_content.py` - pulls published posts, pages, categories, tags and media metadata from the spbw.beer REST API into `content/`.
- `scripts/fetch_archived.py` - the live site uses a custom `archive` status that the REST API list hides, so this fetches those posts/pages by ID (found via the sitemap).
- `scripts/build_wxr.py` - builds `wxr/spbw-baseline.xml` from `content/`. Archived items are imported as published with meta `_spbw_original_status=archive`.
- `blueprints/baseline.json` - WordPress Playground Blueprint that imports the WXR into a stock WordPress.
- `scripts/classify_posts.py` - keyword rules that assign categories and tags to posts (`config/option-a-classification.json`).
- `scripts/event_dates.py` - heuristic extraction of event dates from post titles and text.
- `scripts/structure.py` - shared step for every option: Photo Gallery and `-2` slug fixes, Our History under About us, and the proposed main menu (`redirects/structure.csv`).
- `scripts/build_option_a.py`, `build_option_b.py`, `build_option_c.py` - generate `blueprints/option-a.json`, `option-b.json` and `option-c.json`.
- `redirects/` - draft 301 maps (`option-b.csv`, `option-c.csv`, `structure.csv`). Old URLs are not redirected automatically in every case, so these are required.

Refresh: run `fetch_content.py`, `fetch_archived.py` and `build_wxr.py`, then `classify_posts.py`, then the three `build_option_*.py` scripts.

## Options

Each option is a Blueprint that rebuilds the site in your browser from the repo. Nothing touches spbw.beer. They answer the review's question of how Posts and events should relate. Open one:

| Option | Open in Playground |
|---|---|
| Baseline (current site content, stock theme) | [baseline](https://playground.wordpress.net/?blueprint-url=https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/blueprints/baseline.json) |
| A: categories and tags drive an Events Hub | [option A](https://playground.wordpress.net/?blueprint-url=https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/blueprints/option-a.json) |
| B: The Events Calendar with dated events | [option B](https://playground.wordpress.net/?blueprint-url=https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/blueprints/option-b.json) |
| C: one hand-maintained Events hub | [option C](https://playground.wordpress.net/?blueprint-url=https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/blueprints/option-c.json) |

| | A: taxonomy | B: events plugin | C: hybrid hub |
|---|---|---|---|
| Upcoming and Past views | No (publish date only) | Yes, automatic | Yes, but moved by hand |
| New plugin | None | The Events Calendar | None |
| Editor effort | Categorise each post | Enter dates for each event | Move events between two pages |
| Overlapping events pages removed | Partly | Yes | Yes |
| Old URLs | Mostly unchanged | Redirect map required | Redirect map required |

Notes:

- After pushing a changed Blueprint, GitHub's raw URL is cached for about 5 minutes. Add `?v=2` (any new value) to the end of the `blueprint-url` to force a fresh copy.
- Options A and C can be combined. Better categories help the whole site.
- B converts 77 posts with a date found in the title or text; the date source is stored in meta `_spbw_date_source` for review. Venues, times and RSVP are not extracted.
- A's classification is keyword-based and needs a human review.
- All options also apply the structure step: Photo Gallery slugs (`/photo-gallery/...`), `-2` slugs removed, the stray `/page-3-april-2026/` page retired, Our History under About us, and a proposed menu with 8 top-level items instead of 14.
- Playground cannot show the live theme (Genesis with a commercial child theme), plugins, widgets or media. Images hotlink from spbw.beer.

## Technology Stack

## Configuration

## Contributing

Please read [CONTRIBUTING](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

See [Semantic Versioning](https://semver.org/) for guidance.

## Contributors

You can find the list of contributors in the [CONTRIBUTORS](CONTRIBUTORS.md) file.

## License

See the [LICENSE](LICENSE.txt) file.

## CITING

See the [CITATION](CITATION.cff) file.
