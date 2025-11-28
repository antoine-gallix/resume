import json
import shutil
from pathlib import Path

import markdown
from etabli.reader import read_toml_data
from etabli.watcher import Watcher
from invoke import task  # type:ignore
from jinja2 import Environment, FileSystemLoader
from livereload import Server
from rich import print

from config import settings

# ---

TEMPLATE_DIR = "templates"
HTML_NAME = "resume.html"
STATIC_DIR = "static"
SERVER_HOST = "localhost"
SERVER_PORT = 35729

# ---


def resolved_path(path: str) -> Path:
    return Path(path).expanduser()


def write(content, name):
    output_file = build_dir / name
    output_file.write_text(content)
    print(f"file written: {output_file}")


# ---

static_dir: Path = resolved_path(STATIC_DIR)
template_dir: Path = resolved_path(TEMPLATE_DIR)
data_dir = resolved_path(settings.DATA_DIR)
build_dir = resolved_path(settings.BUILD_DIR)
URL = f"{SERVER_HOST}:{SERVER_PORT}/{HTML_NAME}"


# ---


@task
def show_data(context):
    data = read_toml_data(data_dir)
    json_data = json.dumps(data, indent=4)
    print(json_data)


def _build():
    build_dir.mkdir(exist_ok=True, parents=True)

    print("build resume from templates")

    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["markdown"] = lambda text: markdown.markdown(text)
    data = read_toml_data(data_dir)

    html_template = env.get_template(f"{HTML_NAME}.jinja")
    html_output = html_template.render(**data)
    write(html_output, HTML_NAME)

    for file in static_dir.iterdir():
        print(f"copy {file} into {build_dir}")
        shutil.copy(file, build_dir)

    print("resume generated successfully")


def _autobuild():
    watcher = Watcher(targets=[static_dir, template_dir, data_dir], callback=_build)
    _build()
    watcher.watch()


@task
def build(context, auto=False):
    if auto:
        _autobuild()
    else:
        _build()


@task
def serve(context):
    server = Server()
    server.setHeader("Cache-Control", "no-store")  # prevent caching
    server.watch(build_dir)
    print(f"serving build content at {URL}")
    server.serve(
        root=build_dir, port=SERVER_PORT, host=SERVER_HOST, default_filename=HTML_NAME
    )


@task
def firefox(context):
    context.run(f"firefox --new-window {URL}")
