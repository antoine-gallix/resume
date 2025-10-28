from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="RESUME",
    settings_files=["settings.toml", ".secrets.toml"],
)
