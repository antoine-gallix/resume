import json
import pathlib
import tomllib
from functools import reduce
from operator import or_
from pathlib import Path

from invoke import task  # type:ignore
from jinja2 import Environment, FileSystemLoader
from rich import print

from config import settings

# ------------------------ config ------------------------


TEMPLATE_DIR = "templates"
HTML_NAME = "resume.html"
STATIC_DIR = "static"
SERVER_SOCKET = "localhost:35729"


def resolved_path(path: str) -> Path:
    return Path(path).expanduser()


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
    output_file = resolved_path(settings.BUILD_DIR) / name
    output_file.write_text(content)
    print(f"file written: {output_file}")


@task
def show_data(context):
    data = read_data(resolved_path(settings.DATA_DIR))
    json_data = json.dumps(data, indent=4)
    print(json_data)


@task
def build(context):
    template_dir = resolved_path(TEMPLATE_DIR)
    build_dir = pathlib.Path(settings.BUILD_DIR).expanduser()

    build_dir.mkdir(exist_ok=True, parents=True)

    print("build resume from templates")

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    data = read_data(Path(settings.DATA_DIR).expanduser())

    html_template = env.get_template(f"{HTML_NAME}.jinja")
    html_output = html_template.render(**data)
    write(html_output, HTML_NAME)

    for file in resolved_path(STATIC_DIR).iterdir():
        context.run(f"cp {file} {build_dir / file.name}", echo=True)

    print("resume generated successfully")


@task
def autobuild(context):
    context.run(f"fd . {TEMPLATE_DIR} | entr invoke build", echo=True)


@task
def serve(context):
    print(f"output served at {SERVER_SOCKET}/{HTML_NAME}")
    context.run(f"livereload {settings.BUILD_DIR}", echo=True)


@task
def firefox(context):
    context.run(f"firefox --new-window {SERVER_SOCKET}/{HTML_NAME}")
