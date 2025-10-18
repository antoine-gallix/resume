import pathlib

from invoke import task  # type:ignore

import config
from build import render_resume


@task
def build(context):
    pathlib.Path(config.BUILD_DIR).mkdir(exist_ok=True)
    render_resume("resume.html", "resume.html")
    context.run(f"cp {config.TEMPLATE_DIR}/style.css {config.BUILD_DIR}/style.css")


@task
def autobuild(context):
    context.run(f"fd . {config.TEMPLATE_DIR} | entr invoke build")


@task
def serve(context):
    url = "localhost:35729/resume.html"
    print(f"output served at {url}")
    context.run(f"livereload {config.BUILD_DIR}")
