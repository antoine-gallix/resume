# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static resume/CV generator. It reads semantic data from a directory of TOML files, renders it through a single Jinja2 template, and produces a standalone HTML page.

## Commands

Tasks are run with `invoke` (Python task runner defined in `tasks.py`), not `make` or `just`.

- `invoke --list` — list available tasks
- `invoke build` — render the resume once into `BUILD_DIR`
- `invoke autobuild` — rebuild whenever files under `static/`, `templates/`, or `DATA_DIR` change
- `invoke serve` — serve `BUILD_DIR` with livereload on `localhost:35729`
- `invoke view` — open the served resume in Firefox
- `invoke show-config` — print the resolved Dynaconf config
- `invoke show-data` — print the parsed+enriched resume data as JSON

There is no lint/test setup configured in this project currently.

Dependencies are managed with `uv` (see `uv.lock`, `.python-version` pins Python 3.13).

## Configuration

Config is loaded via Dynaconf from `config.default.toml` (checked in, empty placeholders) layered with `config.toml` (gitignored, user-specific). Two keys matter: `DATA_DIR` (where the TOML resume data lives) and `BUILD_DIR` (where the built HTML/static files are written) — both are `Validator`-enforced to exist and are expanded via `Path.expanduser()`.

If `config.toml` is missing, `config.py` auto-creates it from `config.default.toml` on import and exits the process (`sys.exit()`) so the user can fill in the paths before rerunning — any task that imports `config` will exit early the first time it's run in a fresh checkout.

## Architecture

The pipeline in `tasks.py` is: `read_toml_data(data_dir)` (from the external `etabli` package, pinned to a git source in `pyproject.toml`) loads all TOML files under `DATA_DIR` into a nested dict → `enrich_data()` walks `data["work"]` and `data["training"]` and adds computed fields (`delta`, `year_span`) via `add_human_timespan()`, using `arrow` for date math and `humanize` for the human-readable duration → the single Jinja2 template `templates/resume.html.jinja` (in `templates/`) renders the dict into `resume.html` → static assets in `static/` (CSS, favicon) are copied alongside it into `BUILD_DIR`.

`DATA_DIR` is expected to hold TOML files arranged as documented in `README.md`: top-level files (`about.toml`, `languages.toml`, `skills.toml`) plus `training/` and `work/` subdirectories of dated entries — this directory lives outside the repo (path comes from config) and isn't part of the checked-in project structure.

`etabli.watcher.Watcher` (used by `invoke autobuild`) watches `static_dir`, `template_dir`, and `data_dir` and reruns `_build()` on change.
