import sys
from pathlib import Path

from dynaconf import Dynaconf, Validator
from loguru import logger

ROOT = Path(__file__).parents[2]
USER_CONFIG_PATH = ROOT / "config.toml"
DEFAULT_CONFIG_PATH = ROOT / "config.default.toml"

# ensure config file exists, otherwise create it and exit
if not (config_file := USER_CONFIG_PATH).exists():
    default_content = DEFAULT_CONFIG_PATH.read_text()
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(default_content)
    logger.info(
        f"default config created: {USER_CONFIG_PATH}; fill before running tasks again"
    )
    sys.exit()


config = Dynaconf(
    settings_files=[str(DEFAULT_CONFIG_PATH), str(USER_CONFIG_PATH)],
    validators=[
        Validator(
            "DATA_DIR",
            must_exist=True,
            cast=lambda path: Path(path).expanduser(),
        ),
        Validator(
            "BUILD_DIR",
            must_exist=True,
            cast=lambda path: Path(path).expanduser(),
        ),
    ],
)
