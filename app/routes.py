"""Les routes : une page, un paquet de definitions, les scores, un healthcheck."""

from __future__ import annotations

from flask import Blueprint, Response, current_app, jsonify, render_template, request

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


@bp.route("/sante")
def sante():
    """Healthcheck lu par deploy.sh — en direct sur gunicorn, jamais via nginx."""
    return jsonify({"ok": True, "version": current_app.extensions["version"]})


@bp.app_errorhandler(404)
def introuvable(_erreur):
    return render_template("404.html"), 404
