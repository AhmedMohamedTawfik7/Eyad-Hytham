# Wasla — transport marketplace concept

This repository contains an early Wasla concept: small Python examples and a
static HTML brand demo. It is **not** a finished or production-ready transport
marketplace.

## Code and file explanations

See [CODE_GUIDE.md](./CODE_GUIDE.md) for an editable, file-by-file explanation
of the source, demo, and brand assets, plus instructions for running the
examples and understanding the owner profit-share sample.

## Current contents

- [`012/`](./012/) — Python examples, a minimal Flask sample, and static demo
  files with brand assets.
- [`CODE_GUIDE.md`](./CODE_GUIDE.md) — explanations and limitations.

The `.kt.py` files are Python files with misleading filenames; several model
and build placeholders are empty. No accounts, database, payments, driver
verification, or production security controls are implemented.

## Local preview

Open `012/brand-demo.html` in a browser to view the static concept. The Flask
example requires Flask and can be run with `python 012/build.gradle.py`, then
viewed at `http://127.0.0.1:5000/`. Flask's built-in server is for local
development only.

## Changes and GitHub sync

Edit these Markdown and source files in VS Code or on GitHub. In VS Code, save
your files, review the Source Control changes, commit them, then use **Sync
Changes** to push and pull against the private `AMT7` branch. Saving a file
does not automatically publish it; review and commit each intended change
before syncing.