import json
import shutil
import tempfile
from pathlib import Path

import arrow
import humanize
import markdown
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from resume.config import ROOT, config
from resume.parse import parse

# ---

TEMPLATE_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
PDF_TEMPLATE = TEMPLATE_DIR / "resume.typ"
COMPILED_DATA_FILE = config.BUILD_DIR / "data.json"
# filename the typst template's json() call expects, relative to itself
TYPST_DATA_NAME = "resume.json"
PDF_OUTPUT_FILE = config.BUILD_DIR / "resume.pdf"
HTML_NAME = "resume.html"

# ---


def write(content, name):
    output_file = config.BUILD_DIR / name
    output_file.parent.mkdir(exist_ok=True, parents=True)
    output_file.write_text(content)
    logger.info(f"file written: {output_file}")


# ---


def add_human_timespan(period):
    begin = arrow.get(period["begin"])
    end = arrow.get(period["end"])
    period["delta"] = humanize.naturaldelta(end - begin)
    year_begin = begin.date().year
    year_end = end.date().year
    if year_begin == year_end:
        period["year_span"] = year_begin
    else:
        period["year_span"] = f"{year_begin}-{year_end}"


def enrich_data(data):
    """add human-readable timespan and year span to each work/training period"""
    for period in data["work"].values():
        add_human_timespan(period)
    for period in data["training"].values():
        add_human_timespan(period)


def _compile_data():
    """collect all the data from the toml files and compute additional fields for display"""
    data = parse(config.DATA_DIR)
    enrich_data(data)
    return data


def _build_html():

    logger.info("build html resume")

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    env.filters["markdown"] = lambda text: markdown.markdown(text)
    data = json.loads(COMPILED_DATA_FILE.read_text())

    html_template = env.get_template(f"{HTML_NAME}.jinja")
    html_output = html_template.render(**data)
    write(html_output, config.BUILD_DIR / HTML_NAME)

    for file in STATIC_DIR.iterdir():
        logger.info(f"copy {file} into {config.BUILD_DIR}")
        shutil.copy(file, config.BUILD_DIR)

    logger.info("html resume generated successfully")


def _build_pdf(context):
    logger.info("build pdf resume")

    with tempfile.TemporaryDirectory(prefix="resume-pdf-") as tmp:
        stage = Path(tmp)
        template = stage / PDF_TEMPLATE.name
        shutil.copy(PDF_TEMPLATE, template)
        shutil.copy(COMPILED_DATA_FILE, stage / TYPST_DATA_NAME)

        pdf = stage / "resume.pdf"
        context.run(f'typst compile --root "{stage}" "{template}" "{pdf}"')

        PDF_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(pdf, PDF_OUTPUT_FILE)

    logger.info(f"pdf resume generated: {PDF_OUTPUT_FILE}")
