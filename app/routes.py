"""Les routes : une page, un paquet de definitions, les scores, un healthcheck, les icones."""

from __future__ import annotations

import json

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from .scores import ScoreInvalide, Tableau

bp = Blueprint("jeu", __name__)


def tableau() -> Tableau:
    return current_app.extensions["tableau_scores"]


@bp.route("/")
def accueil():
    return render_template("index.html")


@bp.route("/api/definitions")
def api_definitions():
    """Tout ce que le navigateur doit savoir, en une requete, revalidee par ETag."""
    paquet = current_app.extensions["definitions"]
    etag = f'"{paquet.etag}"'
    # ⚠️ `contains_weak`, pas `contains` : nginx compresse la reponse et marque
    # l'ETag faible (W/"...") en passant ; le navigateur le renvoie tel quel.
    # Avec une comparaison forte, la revalidation ne donnerait jamais 304 en
    # production — tout en marchant parfaitement en local.
    if request.if_none_match.contains_weak(paquet.etag):
        reponse = Response(status=304)
    else:
        reponse = Response(paquet.corps, mimetype="application/json")
    reponse.headers["ETag"] = etag
    reponse.headers["Cache-Control"] = "no-cache"
    return reponse


@bp.route("/api/scores", methods=["GET"])
def api_scores():
    return jsonify({"scores": tableau().meilleurs()})


@bp.route("/api/scores", methods=["POST"])
def api_scores_ajouter():
    try:
        score, rang = tableau().ajouter(request.get_json(silent=True))
    except ScoreInvalide as erreur:
        return jsonify({"erreur": str(erreur)}), 400
    return jsonify({"score": score, "rang": rang, "scores": tableau().meilleurs()}), 201


#: (fichier de static/img/, cote, usage). La 512 sert deux fois : Bandini tient
#: dans le cercle du masque d'Android (tests/test_icones.py le verifie), une
#: seconde image « maskable » serait la meme.
ICONES_DU_MANIFESTE = [
    ("icone-192.png", 192, "any"),
    ("icone-512.png", 512, "any"),
    ("icone-512.png", 512, "maskable"),
]


@bp.route("/manifest.webmanifest")
def manifeste():
    """Ce que Chrome et Android lisent pour mettre le jeu sur l'ecran d'accueil.

    Une route et pas un fichier de `static/` : le nom et la devise viennent de
    la config, et nginx garde `/static/` sept jours — un manifeste fige une
    semaine, c'est une icone qu'on ne peut plus changer.
    """
    accueil = url_for("jeu.accueil")
    corps = {
        "name": current_app.config["SITE_NAME"],
        "short_name": current_app.config["SITE_NAME"],
        "description": current_app.config["SITE_TAGLINE"],
        "lang": "fr-CA",
        "id": accueil,
        "start_url": accueil,
        "scope": accueil,
        "display": "fullscreen",
        "background_color": "#0b0a12",
        "theme_color": "#0b0a12",
        "icons": [
            {"src": url_for("static", filename=f"img/{nom}"), "sizes": f"{cote}x{cote}",
             "type": "image/png", "purpose": usage}
            for nom, cote, usage in ICONES_DU_MANIFESTE
        ],
    }
    reponse = Response(json.dumps(corps, ensure_ascii=False, indent=2),
                       mimetype="application/manifest+json")
    reponse.headers["Cache-Control"] = "no-cache"
    return reponse


@bp.route("/favicon.ico")
def favicon():
    """Tout navigateur le demande a la racine, lien ou pas : sans elle, un 404 par visite."""
    return send_from_directory(current_app.static_folder, "img/favicon.ico", max_age=86400)


@bp.route("/sante")
def sante():
    """Healthcheck lu par deploy.sh — en direct sur gunicorn, jamais via nginx."""
    return jsonify({"ok": True, "version": current_app.extensions["version"]})


@bp.app_errorhandler(404)
def introuvable(_erreur):
    return render_template("404.html"), 404
