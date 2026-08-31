import json
import shutil

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
PDF_TEMPLATE = "resume.typ"
TYPST_DATA = "resume.json"
PDF_DIR = ROOT / "pdf"
PDF_NAME = "resume.pdf"
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


def build_data():
    """collect all the data from the toml files and compute additional fields for display"""
    data = parse(config.DATA_DIR)
    enrich_data(data)
    return data


def _build_html():

    logger.info("build html resume")

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    env.filters["markdown"] = lambda text: markdown.markdown(text)
    data = build_data()

    html_template = env.get_template(f"{HTML_NAME}.jinja")
    html_output = html_template.render(**data)
    write(html_output, config.BUILD_DIR / HTML_NAME)

    for file in STATIC_DIR.iterdir():
        logger.info(f"copy {file} into {config.BUILD_DIR}")
        shutil.copy(file, config.BUILD_DIR)

    logger.info("html resume generated successfully")


def _build_pdf(context):
    logger.info("build pdf resume")

    data = build_data()
    (config.PDF_DIR / TYPST_DATA).write_text(json.dumps(data, indent=4))

    context.run(
        f'typst compile "{config.PDF_DIR / PDF_TEMPLATE}" "{config.BUILD_DIR / PDF_NAME}"'
    )

    logger.info("pdf resume generated successfully")
