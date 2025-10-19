import tomllib
from functools import reduce
from operator import or_
from pathlib import Path

from icecream import ic
from jinja2 import Environment, FileSystemLoader

import config


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


def render_resume(template_name, output_name):
    print(f"build resume from template: {template_name}")
    env = Environment(loader=FileSystemLoader(config.TEMPLATE_DIR))
    template = env.get_template(template_name)
    data = read_data(Path(config.DATA_DIR))
    ic(data)
    output = template.render(**data)
    output_file = Path(config.BUILD_DIR) / output_name
    output_file.write_text(output)
    print(f"resume generated successfully: {output_file}")
