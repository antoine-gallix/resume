import pathlib
import tomllib
from functools import reduce
from operator import or_
from pathlib import Path

from invoke import task  # type:ignore
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "templates"
BUILD_DIR = "output"
DATA_DIR = "data"


def read_data(path: Path, first_call=True) -> dict:
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
    output_file = Path(BUILD_DIR) / name
    output_file.write_text(content)
    print(f"file written: {name}")


@task
def build(context):
    pathlib.Path(BUILD_DIR).mkdir(exist_ok=True)
    print("build resume from templates")

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    data = read_data(Path(DATA_DIR))

    html_template = env.get_template("resume.html.jinja")
    html_output = html_template.render(**data)
    write(html_output, "resume.html.jinja")

    css_template = env.get_template("style.css.jinja")
    css_output = css_template.render()
    write(css_output, "style.css")

    print("resume generated successfully")


@task
def autobuild(context):
    context.run(f"fd . {TEMPLATE_DIR} | entr invoke build")


@task
def serve(context):
    url = "localhost:35729/resume.html"
    print(f"output served at {url}")
    context.run(f"livereload {BUILD_DIR}")
