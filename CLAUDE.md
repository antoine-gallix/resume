# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static resume/CV generator. It reads semantic data from a directory of TOML files and renders it two ways: through a Jinja2 template into a standalone HTML page, and through a Typst template into a PDF.

## Commands

Tasks are run with `invoke` (Python task runner defined in `tasks.py`), not `make` or `just`. Tasks are grouped into `data.*`, `html.*`, and `pdf.*` collections (defined via `invoke.Collection` in `tasks.py`), plus a top-level `config` task.

- `invoke --list` — list available tasks
- `invoke config` — print the resolved Dynaconf config
- `invoke data.compile` — parse+enrich the resume data and write it to `COMPILED_DATA_FILE`
- `invoke data.print` — print the compiled data file
- `invoke html.build` — render the HTML resume once into `BUILD_DIR`
- `invoke html.autobuild` — rebuild the HTML resume whenever files under `static/`, `templates/`, or `DATA_DIR` change (PDF build is not wired into the watcher)
- `invoke html.serve` — serve `BUILD_DIR` with livereload on `localhost:35729`
- `invoke html.view` — open the served resume in Firefox
- `invoke pdf.build` — render the PDF resume via Typst into `BUILD_DIR` (requires the `typst` CLI on `PATH`; it's not a Python dependency)

There is no lint/test setup configured in this project currently.

Dependencies are managed with `uv` (see `uv.lock`, `.python-version` pins Python 3.13).

## Layout

Application code lives in the `resume` package under `src/` (`src/resume/`): `config.py` (Dynaconf setup), `parse.py` (TOML directory reader), `build.py` (data enrichment + the HTML/PDF render steps). `tasks.py` stays at the repo root — `invoke` discovers it there — and is a thin shim: it imports from `resume.build` / `resume.config` and only holds the `@task` wrappers. The package is installed (editable) via the `hatchling` build backend declared in `pyproject.toml`.

`src/resume/parse.py` replaces `etabli.reader.read_toml_data` (it's what `build_data()` calls) — same directory-to-nested-dict idea, but built on `deepmerge` so that a genuine key collision between files folds into a list instead of one file's value silently overwriting another's.

## Configuration

Config is loaded via Dynaconf from `config.default.toml` (checked in, empty placeholders) layered with `config.toml` (gitignored, user-specific). Two keys matter: `DATA_DIR` (where the TOML resume data lives) and `BUILD_DIR` (where the built HTML/static files are written) — both are `Validator`-enforced to exist and are expanded via `Path.expanduser()`.

If `config.toml` is missing, `src/resume/config.py` auto-creates it from `config.default.toml` on import and exits the process (`sys.exit()`) so the user can fill in the paths before rerunning — any task that imports `config` will exit early the first time it's run in a fresh checkout. Both TOMLs stay at the repo root; `config.py` locates them via `ROOT = Path(__file__).parents[2]` rather than the cwd.

## Architecture

Both render paths share one data step, `build_data()` in `src/resume/build.py`: `parse(data_dir)` (from `src/resume/parse.py`) loads all TOML files under `DATA_DIR` into a nested dict → `enrich_data()` walks `data["work"]` and `data["training"]` and adds computed fields (`delta`, `year_span`) via `add_human_timespan()`, using `arrow` for date math and `humanize` for the human-readable duration.

From there the two builds diverge:
- `_build_html()`: the Jinja2 template `templates/resume.html.jinja` renders the dict into `resume.html` → static assets in `static/` (CSS, favicon) are copied alongside it into `BUILD_DIR`.
- `_build_pdf()`: the data dict is dumped to JSON (`PDF_DIR / TYPST_DATA`) and a Typst template (`PDF_DIR / PDF_TEMPLATE`, reading that JSON via `json()`) is compiled to `BUILD_DIR / PDF_NAME` by shelling out to `typst compile`.

Known inconsistency as of this writing: `PDF_DIR` is set to `ROOT / "pdf"` in `src/resume/build.py`, but the only Typst template currently on disk is the untracked `templates/resume.typ`, and `pdf/` doesn't exist — `invoke pdf.build` will fail until either the constant or the file's location is fixed.

`DATA_DIR` is expected to hold TOML files arranged as documented in `README.md`: top-level files (`about.toml`, `languages.toml`, `skills.toml`) plus `training/` and `work/` subdirectories of dated entries — this directory lives outside the repo (path comes from config) and isn't part of the checked-in project structure.

`etabli.watcher.Watcher` (used by `invoke html.autobuild`) watches `static_dir`, `template_dir`, and `data_dir` and reruns `_build_html()` on change.

`write()` (the shared file-writing helper in `src/resume/build.py`) creates any missing parent directories before writing.
