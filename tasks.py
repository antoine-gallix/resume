import json
import shutil
import time
import tomllib
from dataclasses import dataclass
from functools import reduce
from operator import or_
from pathlib import Path
from typing import Callable

from invoke import task  # type:ignore
from jinja2 import Environment, FileSystemLoader
from rich import print

from config import settings

# ---

TEMPLATE_DIR = "templates"
HTML_NAME = "resume.html"
STATIC_DIR = "static"
SERVER_HOST = "localhost"
SERVER_PORT = 35729

# ---


def resolved_path(path: str):
    return Path(path).expanduser()


STATIC_DIR = resolved_path(STATIC_DIR)
TEMPLATE_DIR = resolved_path(TEMPLATE_DIR)
DATA_DIR = resolved_path(settings.DATA_DIR)
BUILD_DIR = resolved_path(settings.BUILD_DIR)
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
    output_file = BUILD_DIR / name
    output_file.write_text(content)
    print(f"file written: {output_file}")


# ---


@task
def show_data(context):
    data = read_data(DATA_DIR)
    json_data = json.dumps(data, indent=4)
    print(json_data)


def _build():
    BUILD_DIR.mkdir(exist_ok=True, parents=True)

    print("build resume from templates")

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    data = read_data(DATA_DIR)

    html_template = env.get_template(f"{HTML_NAME}.jinja")
    html_output = html_template.render(**data)
    write(html_output, HTML_NAME)

    for file in STATIC_DIR.iterdir():
        print(f"copy {file} into {BUILD_DIR}")
        shutil.copy(file, BUILD_DIR)

    print("resume generated successfully")


@task
def build(context):
    _build()


@task
def autobuild(context):
    watcher = Watcher(targets=[STATIC_DIR, TEMPLATE_DIR], callback=_build)
    _build()
    watcher.watch()


@task
def serve(context):
    from livereload import Server

    server = Server()
    # prevent caching
    server.setHeader("Cache-Control", "no-store")
    for ext in ["html", "css", "png"]:
        path = str(BUILD_DIR / f"*.{ext}")
        print(f"watching {path}")
        server.watch(path)
    print(f"serving build content at {URL}")
    server.serve(root=BUILD_DIR, port=SERVER_PORT, host=SERVER_HOST)


@task
def firefox(context):
    context.run(f"firefox --new-window {URL}")
