import sys
from pathlib import Path

from dynaconf import Dynaconf
from loguru import logger

USER_CONFIG_PATH = "config.toml"
DEFAULT_CONFIG_PATH = "config.default.toml"
if not (config_file := Path(USER_CONFIG_PATH)).exists():
    default_content = Path(DEFAULT_CONFIG_PATH).read_text()
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(default_content)
    logger.info(
        f"default config created: {USER_CONFIG_PATH}; fill before running tasks again"
    )
    sys.exit()

config = Dynaconf(
    settings_files=["settings.toml"],
)
