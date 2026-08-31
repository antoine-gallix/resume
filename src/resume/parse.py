"""Read a directory of toml files and merge them into a single dict

Pipeline: list every toml file under the data dir -> embed each file's
content into a nested dict following its relative path -> merge all the
per-file dicts into one, turning colliding values into a list instead of
overwriting them.
"""

import tomllib
from functools import reduce
from pathlib import Path

from deepmerge.merger import Merger


def list_files(data_dir: Path) -> list[Path]:
    """list toml files in that directory"""
    return sorted(data_dir.rglob("*.toml"))


def embed(data_dir: Path, file_path: Path) -> dict:
    """Nest a file's parsed content under keys taken from its path, e.g.
    experiences/company.toml -> {"experiences": {"company": {...}}}"""
    content = tomllib.loads(file_path.read_text())
    parts = file_path.relative_to(data_dir).with_suffix("").parts
    for part in reversed(parts):
        content = {part: content}
    return content


def _collide_into_list(config, path, base, nxt):
    if isinstance(base, list):
        return base + [nxt]
    return [base, nxt]


# dicts keep recursively merging (that's how sibling files build up a
# shared "work"/"training" branch); anything else that collides on the
# same key gets collected into a list instead of the last value winning.
merger = Merger(
    [(dict, "merge")],
    [_collide_into_list],
    [_collide_into_list],
)


def parse(data_dir: Path) -> dict:
    files = list_files(data_dir)
    embedded = [embed(data_dir, file) for file in files]
    return reduce(merger.merge, embedded, {})
