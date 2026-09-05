import json
from pathlib import Path

from etabli.watcher import Watcher
from invoke import task  # type: ignore
from livereload import Server
from loguru import logger

from resume.build import (
    COMPILED_DATA_FILE,
    HTML_NAME,
    STATIC_DIR,
    TEMPLATE_DIR,
    _build_html,
    _build_pdf,
    _compile_data,
)
from resume.config import config

SERVER_HOST = "localhost"
SERVER_PORT = 35729
URL = f"{SERVER_HOST}:{SERVER_PORT}/{HTML_NAME}"


class PathEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def print_json(data):
    print(json.dumps(data, indent=4, cls=PathEncoder))


@task
def print_config(context):
    print_json(config.to_dict())


@task
def compile_data(context):
    data = _compile_data()
    COMPILED_DATA_FILE.write_text(json.dumps(data, indent=4))


@task
def print_data(context):
    """print the parsed and enriched resumedata"""
    print(COMPILED_DATA_FILE.read_text())


@task
def build_pdf(context):
    _build_pdf(context)


@task
def build_html(context):
    _build_html()


@task
def autobuild(context):
    watcher = Watcher(
        targets=[STATIC_DIR, TEMPLATE_DIR, config.DATA_DIR], callback=_build_html
    )
    _build_html()
    watcher.watch()


@task
def serve(context):
    """serve the resume locally with livereload"""

    server = Server()
    server.setHeader("Cache-Control", "no-store")  # prevent caching
    server.watch(config.BUILD_DIR)
    logger.info(f"serving build content at {URL}")
    server.serve(
        root=config.BUILD_DIR,
        port=SERVER_PORT,
        host=SERVER_HOST,
        default_filename=HTML_NAME,
    )


@task
def view(context):
    context.run(f"firefox --new-window {URL}", disown=True)


@task
def build_all(context):
    _build_html()
    _build_pdf(context)
