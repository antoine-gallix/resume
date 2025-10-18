import pathlib

from jinja2 import Environment, FileSystemLoader

import config
from data import data


def render_resume(template_name, output_name):
    print(f"build resume from template: {template_name}")
    env = Environment(loader=FileSystemLoader(config.TEMPLATE_DIR))
    template = env.get_template(template_name)
    output = template.render(**data)
    output_file = pathlib.Path(config.BUILD_DIR) / output_name
    output_file.write_text(output)
    print(f"resume generated successfully: {output_file}")
