import json
import shutil
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
PDF_TEMPLATE = "resume.typ"
HTML_NAME = "resume.html"
TYPST_DATA = "resume.json"
PDF_DIR = ROOT / "pdf"
PDF_NAME = "resume.pdf"
STATIC_DIR = ROOT / "static"
SERVER_HOST = "localhost"
SERVER_PORT = 35729

# ---


def resolved_path(path: str) -> Path:
    return Path(path).expanduser()


def write(content, name):
    output_file = build_dir / name
    output_file.parent.mkdir(exist_ok=True, parents=True)
    output_file.write_text(content)
    logger.info(f"file written: {output_file}")


# ---

static_dir: Path = STATIC_DIR
template_dir: Path = TEMPLATE_DIR
typst_dir: Path = PDF_DIR
data_dir = resolved_path(config.DATA_DIR)
build_dir = resolved_path(config.BUILD_DIR)
URL = f"{SERVER_HOST}:{SERVER_PORT}/{HTML_NAME}"


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
    data = parse(data_dir)
    enrich_data(data)
    return data


def _build_html():

    logger.info("build html resume")

    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["markdown"] = lambda text: markdown.markdown(text)
    data = build_data()

    html_template = env.get_template(f"{HTML_NAME}.jinja")
    html_output = html_template.render(**data)
    write(html_output, build_dir / HTML_NAME)

    for file in static_dir.iterdir():
        logger.info(f"copy {file} into {build_dir}")
        shutil.copy(file, build_dir)

    logger.info("html resume generated successfully")


def _build_pdf(context):
    logger.info("build pdf resume")

    data = build_data()
    (typst_dir / TYPST_DATA).write_text(json.dumps(data, indent=4))

    context.run(f'typst compile "{typst_dir / PDF_TEMPLATE}" "{build_dir / PDF_NAME}"')

    logger.info("pdf resume generated successfully")
