import json
import shutil
import time
import tomllib
from dataclasses import dataclass
from functools import reduce
from operator import or_
from pathlib import Path
from typing import Callable

import markdown
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


static_dir: Path = resolved_path(STATIC_DIR)
template_dir: Path = resolved_path(TEMPLATE_DIR)
data_dir = resolved_path(settings.DATA_DIR)
build_dir = resolved_path(settings.BUILD_DIR)
URL = f"{SERVER_HOST}:{SERVER_PORT}/{HTML_NAME}"

# ---


@dataclass
class Watcher:
    targets: list[Path]
    callback: Callable

    def files(self):
        for target in self.targets:
            for dir_, _, files in target.walk():
                for file in files:
                    yield dir_ / file

    def mtimes(self):
        return [(str(file), file.stat().st_mtime) for file in self.files()]

    def watch(self):
        last_times = self.mtimes()
        try:
            while True:
                time.sleep(1)
                new_times = self.mtimes()
                if new_times == last_times:
                    pass
                else:
                    last_times = new_times
                    self.callback()
        except KeyboardInterrupt:
            exit()


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
    output_file = build_dir / name
    output_file.write_text(content)
    print(f"file written: {output_file}")


# ---


@task
def show_data(context):
    data = read_data(data_dir)
    json_data = json.dumps(data, indent=4)
    print(json_data)


def _build():
    build_dir.mkdir(exist_ok=True, parents=True)

    print("build resume from templates")

    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["markdown"] = lambda text: markdown.markdown(text)
    data = read_data(data_dir)

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
