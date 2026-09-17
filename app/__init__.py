"""Fabrique de l'application Flask."""

from __future__ import annotations

from datetime import date

from flask import Flask

from config import Config

from .definitions import construire
from .scores import Tableau
from .version import VERSION


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_object)

    app.extensions["tableau_scores"] = Tableau(app.config["DONNEES_DIR"])
    app.extensions["version"] = VERSION
    # Le paquet de definitions et la carte sont construits UNE fois : les
    # catalogues ne changent pas sous un processus lance.
    paquets = construire()
    app.extensions["definitions"] = paquets.definitions
    app.extensions["carte"] = paquets.carte

    from .routes import bp

    app.register_blueprint(bp)

    @app.context_processor
    def variables_globales() -> dict:
        return {
            "SITE_NAME": app.config["SITE_NAME"],
            "SITE_TAGLINE": app.config["SITE_TAGLINE"],
            "SITE_AUTEUR": app.config["SITE_AUTEUR"],
            "version": VERSION,
            "annee": date.today().year,
        }

    return app
