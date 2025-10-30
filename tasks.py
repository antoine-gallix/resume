import pathlib
import tomllib
from functools import reduce
from operator import or_
from pathlib import Path

from invoke import task  # type:ignore
from jinja2 import Environment, FileSystemLoader

from config import settings

# ------------------------ config ------------------------


TEMPLATE_DIR = "templates"

HTML_NAME = "index.html"
STYLE_NAME = "style.css"


def read_data(path: Path, first_call=True) -> dict:
    """Read a toml file, or a nested directory of files"""
    if path.is_file():
        return {path.stem: tomllib.loads(path.read_text())}
    elif path.is_dir():
        data = reduce(
            or_,
            (read_data(subpath, first_call=False) for subpath in path.iterdir()),
            {},
        )
        if first_call:
            return data
        else:
            return {path.name: data}
    else:
        raise RuntimeError(f"path not supported: {path}")


def write(content, name):
    output_file = Path(settings.BUILD_DIR).expanduser() / name
    output_file.write_text(content)
    print(f"file written: {output_file}")


@task
def build(context):
    pathlib.Path(settings.BUILD_DIR).expanduser().mkdir(exist_ok=True, parents=True)
    print("build resume from templates")

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    data = read_data(Path(settings.DATA_DIR).expanduser())

    html_template = env.get_template(f"{HTML_NAME}.jinja")
    html_output = html_template.render(**data)
    write(html_output, HTML_NAME)

    css_template = env.get_template(f"{STYLE_NAME}.jinja")
    css_output = css_template.render()
    write(css_output, STYLE_NAME)

    print("resume generated successfully")


@task
def autobuild(context):
    context.run(f"fd . {TEMPLATE_DIR} | entr invoke build")


@task
def serve(context):
    url = "localhost:35729/resume.html"
    print(f"output served at {url}")
    context.run(f"livereload {settings.BUILD_DIR}")
