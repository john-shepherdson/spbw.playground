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

Refresh: run the three scripts in the order above.

Open the baseline once pushed to `main`:
`https://playground.wordpress.net/?blueprint-url=https://raw.githubusercontent.com/john-shepherdson/spbw.playground/main/blueprints/baseline.json`

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
