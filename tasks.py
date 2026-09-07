import json
import shutil
from pathlib import Path

from etabli.watcher import Watcher
from invoke import Collection, task  # type: ignore
from livereload import Server
from loguru import logger

from resume.build import _build_html, _build_pdf, _compile_data
from resume.config import ROOT, config

SERVER_HOST = "localhost"
SERVER_PORT = 35729

HTML_DIR = ROOT / "html"
TEMPLATE_DIR = HTML_DIR
STATIC_DIR = HTML_DIR
PDF_DIR = ROOT / "pdf"
PDF_TEMPLATE = PDF_DIR / "resume.typ"
COMPILED_DATA_FILE = config.BUILD_DIR / "data.json"
# filename the typst template's json() call expects, relative to itself
TYPST_DATA_NAME = "resume.json"
PDF_OUTPUT_FILE = config.BUILD_DIR / "resume.pdf"
HTML_NAME = "resume.html"

URL = f"{SERVER_HOST}:{SERVER_PORT}/{HTML_NAME}"


class PathEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def print_json(data):
    print(json.dumps(data, indent=4, cls=PathEncoder))


@task
def print_config(context):
    """show the config"""
    print_json(config.to_dict())


# --- data -------------------------------------------------------------------


@task
def compile_data(context):
    """compile data directory to a file"""
    data = _compile_data(config.DATA_DIR)
    COMPILED_DATA_FILE.write_text(json.dumps(data, indent=4))


@task
def print_data(context):
    """show compiled data"""
    print(COMPILED_DATA_FILE.read_text())


# --- html -----------------------------------------------------------------


def build_html_args():
    return {
        "template_dir": TEMPLATE_DIR,
        "static_dir": STATIC_DIR,
        "compiled_data_file": COMPILED_DATA_FILE,
        "build_dir": config.BUILD_DIR,
        "html_name": HTML_NAME,
    }


@task
def build_html(context):
    """build html resume"""
    _build_html(**build_html_args())


@task
def autobuild_html(context):
    """rebuild html when source files change"""
    watcher = Watcher(
        targets=[STATIC_DIR, TEMPLATE_DIR, config.DATA_DIR],
        callback=lambda: _build_html(**build_html_args()),
    )
    _build_html(**build_html_args())
    watcher.watch()


@task
def serve_html(context):
    """serve the html resume locally with livereload"""

    server = Server()
    server.setHeader("Cache-Control", "no-store")  # prevent caching
    server.watch(config.BUILD_DIR)
    logger.info(f"serving build content at {URL}")
    server.serve(
        root=config.BUILD_DIR,
        port=SERVER_PORT,
        host=SERVER_HOST,
        default_filename=HTML_NAME,
    )


@task
def view_html(context):
    """open local html resume in a browser. requires local server running"""
    context.run(f"firefox --new-window {URL}", disown=True)


# --- pdf ------------------------------------------------------------------


@task
def build_pdf(context):
    """build pdf resume"""
    _build_pdf(
        context,
        pdf_template=PDF_TEMPLATE,
        compiled_data_file=COMPILED_DATA_FILE,
        typst_data_name=TYPST_DATA_NAME,
        pdf_output_file=PDF_OUTPUT_FILE,
    )


@task
def autobuild_pdf(context):
    """recompile the pdf whenever the data or the typst template changes.

    two things run together: a watcher that regenerates the json inputs from the
    toml data, and `typst watch` which recompiles on any change to the template
    or the json it reads. open the result with a viewer that reloads on change
    (e.g. `okular BUILD_DIR/resume.pdf`).
    """
    stage = config.BUILD_DIR / "_pdf_stage"
    stage.mkdir(parents=True, exist_ok=True)
    template = stage / PDF_TEMPLATE.name

    def refresh_inputs():
        shutil.copy(PDF_TEMPLATE, template)
        data = _compile_data(config.DATA_DIR)
        (stage / TYPST_DATA_NAME).write_text(json.dumps(data, indent=4))
        logger.info("pdf inputs refreshed")

    refresh_inputs()
    watcher = Watcher(
        targets=[PDF_DIR, config.DATA_DIR],
        callback=refresh_inputs,
    )

    typst = context.run(
        f'typst watch --root "{stage}" "{template}" "{PDF_OUTPUT_FILE}"',
        asynchronous=True,
    )
    try:
        watcher.watch()
    finally:
        typst.runner.kill()


@task
def open_pdf(context):
    """open the built pdf resume. linux only"""
    context.run(f'xdg-open "{PDF_OUTPUT_FILE}"', disown=True)


# --- namespace ----------------------------------------------------------------

data = Collection("data")
data.add_task(compile_data, "compile")  # type: ignore[arg-type]
data.add_task(print_data, "print")  # type: ignore[arg-type]

html = Collection("html")
html.add_task(build_html, "build")  # type: ignore[arg-type]
html.add_task(autobuild_html)  # type: ignore[arg-type]
html.add_task(serve_html)  # type: ignore[arg-type]
html.add_task(view_html, "view")  # type: ignore[arg-type]

pdf = Collection("pdf")
pdf.add_task(build_pdf, "build")  # type: ignore[arg-type]
pdf.add_task(autobuild_pdf)  # type: ignore[arg-type]
pdf.add_task(open_pdf, "open")  # type: ignore[arg-type]

namespace = Collection()
namespace.add_task(print_config, "config")  # type: ignore[arg-type]
namespace.add_collection(data)
namespace.add_collection(html)
namespace.add_collection(pdf)
