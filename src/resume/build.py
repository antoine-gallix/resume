import json
import shutil
import tempfile
from pathlib import Path

import arrow
import humanize
import markdown
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from resume.parse import parse

# ---


def write(content, output_file):
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


def _compile_data(data_dir):
    """collect all the data from the toml files and compute additional fields for display"""
    data = parse(data_dir)
    enrich_data(data)
    return data


def _build_html(*, template_dir, static_dir, compiled_data_file, build_dir, html_name):

    logger.info("build html resume")

    # render template with data
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["markdown"] = lambda text: markdown.markdown(text)
    data = json.loads(compiled_data_file.read_text())
    html_template = env.get_template(f"{html_name}.jinja")
    html_output = html_template.render(**data)
    write(html_output, build_dir / html_name)

    # copy static files, skip the jinja template
    for file in static_dir.iterdir():
        if file.suffix == ".jinja":
            continue
        logger.info(f"copy {file} into {build_dir}")
        shutil.copy(file, build_dir)

    logger.info("html resume generated successfully")


def _build_pdf(
    context, *, pdf_template, compiled_data_file, typst_data_name, pdf_output_file
):
    logger.info("build pdf resume")
    """ typst requires template, data and output must be under a common root. build therefore happens in a temp dir that is cleaned afterward.
    """
    with tempfile.TemporaryDirectory(prefix="resume-pdf-") as tmp:
        stage = Path(tmp)
        template = stage / pdf_template.name
        shutil.copy(pdf_template, template)
        shutil.copy(compiled_data_file, stage / typst_data_name)

        pdf = stage / "resume.pdf"
        context.run(f'typst compile --root "{stage}" "{template}" "{pdf}"')

        pdf_output_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(pdf, pdf_output_file)

    logger.info(f"pdf resume generated: {pdf_output_file}")
