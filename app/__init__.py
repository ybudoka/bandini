"""Fabrique de l'application Flask."""

from __future__ import annotations

from datetime import date

from flask import Flask

from config import CLES_DE_DEVELOPPEMENT, Config

from . import bd
from .definitions import construire
from .version import VERSION


def refuser_la_cle_de_developpement(config) -> None:
    """⚠️ En production, une cle que tout le monde connait ne se prend pas.

    Rien ne signe encore avec elle — le jeton d'appareil de M14 vit en base, pas
    dans un cookie signe —, mais le jour ou quelque chose le fera (un lien pour
    reprendre un mot de passe perdu), cette cle-la n'existera deja plus en ligne.
    L'installeur en genere une vraie depuis M0 ; ce refus garde qu'elle y reste.
    """
    if not config.get("PRODUCTION"):
        return
    cle = config.get("SECRET_KEY") or ""
    if cle in CLES_DE_DEVELOPPEMENT or len(cle) < 32:
        raise RuntimeError(
            "SECRET_KEY : la cle de developpement (ou une cle de moins de 32 caracteres) "
            "en production. Generer une vraie cle : "
            "python3 -c 'import secrets; print(secrets.token_hex(32))'"
        )


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_object)
    refuser_la_cle_de_developpement(app.config)

    app.extensions["version"] = VERSION
    # Le paquet de definitions et la carte sont construits UNE fois : les
    # catalogues ne changent pas sous un processus lance.
    paquets = construire()
    app.extensions["definitions"] = paquets.definitions
    app.extensions["carte"] = paquets.carte

    from .routes import bp

    app.register_blueprint(bp)
    app.teardown_appcontext(bd.fermer)

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
