import logging

from flask import Flask
from . import config as config_module
from .routes import all_blueprints


logging.basicConfig(
    level=config_module.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("unmonitarr")


def create_app():
    flask_app = Flask(__name__)
    for bp in all_blueprints:
        flask_app.register_blueprint(bp)

    cfg = config_module.get()
    missing = [k for k in ("radarr_api_key", "sonarr_api_key") if not cfg.get(k)]
    if missing:
        log.warning("Not yet configured: %s - visit /settings to set these up.", ", ".join(missing))

    return flask_app


app = create_app()