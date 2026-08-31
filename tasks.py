import json

from etabli.watcher import Watcher
from invoke import task  # type: ignore
from livereload import Server
from loguru import logger

from resume.build import (
    HTML_NAME,
    SERVER_HOST,
    SERVER_PORT,
    URL,
    _build_html,
    _build_pdf,
    build_data,
    build_dir,
    data_dir,
    static_dir,
    template_dir,
)
from resume.config import config


@task
def print_config(context):
    print(config.to_dict())


@task
def show_data(context):
    """print the data that will be used to generate the resume"""
    print(json.dumps(build_data(), indent=4))


@task
def build_pdf(context):
    _build_pdf(context)


@task
def autobuild(context):
    watcher = Watcher(
        targets=[static_dir, template_dir, data_dir], callback=_build_html
    )
    _build_html()
    watcher.watch()


@task
def serve_html(context):
    server = Server()
    server.setHeader("Cache-Control", "no-store")  # prevent caching
    server.watch(build_dir)
    logger.info(f"serving build content at {URL}")
    server.serve(
        root=build_dir, port=SERVER_PORT, host=SERVER_HOST, default_filename=HTML_NAME
    )


@task
def build(context):
    _build_html()
    _build_pdf(context)


@task
def view(context):
    context.run(f"firefox --new-window {URL}", disown=True)
