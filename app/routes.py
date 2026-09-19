"""Les routes : une page, un paquet de definitions et sa carte, les comptes, un healthcheck, les icones."""

from __future__ import annotations

import json
import re
import sqlite3
from functools import lru_cache
from pathlib import Path

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

from . import bd, comptes
from . import hors_ligne

bp = Blueprint("jeu", __name__)


@lru_cache(maxsize=1)
def _scripts_du_jeu(gabarit: str) -> int:
    """Combien de scripts la page charge : `chargement.js` compte leur arrivee.

    ⚠️ Lu dans le gabarit lui-meme, pas ecrit a la main : un script de plus dans
    la page et la barre s'arreterait avant la fin, ou deborderait."""
    return len(re.findall(r"filename='js/[^']+'", Path(gabarit).read_text(encoding="utf-8")))


@bp.route("/")
def accueil():
    return _page_d_accueil()


def _page_d_accueil() -> str:
    gabarit = str(Path(current_app.root_path, current_app.template_folder, "index.html"))
    # ⚠️ Les deux paquets se demandent PAR LEUR EMPREINTE (`?e=`), que le serveur
    # ignore : c'est la cle du cache hors ligne. Une page gardee n'y retrouve que
    # la ville de SA construction — jamais un paquet d'un autre deploiement sous
    # des scripts qui ne le connaissent pas.
    return render_template("index.html", scripts_du_jeu=_scripts_du_jeu(gabarit),
                           empreinte_definitions=current_app.extensions["definitions"].etag,
                           empreinte_carte=current_app.extensions["carte"].etag,
                           url_compte=comptes.CHEMIN_COOKIE + "/")


def _revalide(paquet) -> Response:
    """Un paquet JSON revalide par son ETag : 304 si le navigateur l'a deja."""
    etag = f'"{paquet.etag}"'
    # ⚠️ `contains_weak`, pas `contains` : nginx compresse la reponse et marque
    # l'ETag faible (W/"...") en passant ; le navigateur le renvoie tel quel.
    # Avec une comparaison forte, la revalidation ne donnerait jamais 304 en
    # production — tout en marchant parfaitement en local.
    if request.if_none_match.contains_weak(paquet.etag):
        reponse = Response(status=304)
    else:
        reponse = Response(paquet.corps, mimetype="application/json")
        # ⚠️ LA TAILLE DECOMPRESSEE, pour la barre de chargement : nginx compresse
        # la reponse, et `Content-Length` (s'il reste) compte des octets gzip —
        # alors que le navigateur, lui, lit des octets decompresses. Sans ce
        # nombre-la, la barre avancerait au jugé.
        reponse.headers["X-Octets"] = str(paquet.taille)
    reponse.headers["ETag"] = etag
    reponse.headers["Cache-Control"] = "no-cache"
    return reponse


@bp.route("/api/definitions")
def api_definitions():
    """Tout ce que le navigateur doit savoir, sauf la carte, revalide par ETag."""
    return _revalide(current_app.extensions["definitions"])


@bp.route("/api/carte")
def api_carte():
    """La ville, a part : la moitie du poids, et elle ne change pas au meme rythme.

    ⚠️ La meme revalidation que les definitions, ETag faible compris (nginx le
    marque faible en compressant). Les definitions nomment l'empreinte de la
    carte qui va avec elles (`carte_empreinte`) : le navigateur verifie que les
    deux reponses sont de la meme construction.
    """
    return _revalide(current_app.extensions["carte"])


# --- Les comptes (M14) : le local joue, le serveur se souvient ---------------------------


def _jeton() -> str | None:
    return request.cookies.get(comptes.COOKIE)


def _cookie(reponse: Response, jeton: str | None) -> None:
    """Pose le jeton d'appareil — ou l'efface, avec `None`.

    ⚠️ `Secure` en production seulement : le telephone du salon joue en http sur
    le wifi, et un cookie `Secure` n'y serait jamais garde.
    """
    options = dict(path=comptes.CHEMIN_COOKIE, httponly=True, samesite="Lax",
                   secure=bool(current_app.config.get("PRODUCTION")))
    if jeton is None:
        reponse.delete_cookie(comptes.COOKIE, **options)
    else:
        reponse.set_cookie(comptes.COOKIE, jeton, max_age=comptes.DUREE_JETON_S, **options)


def _compte_ouvert(session: comptes.Session, statut: int = 200) -> Response:
    corps = {"compte": {"pseudo": session.pseudo,
                        "parties": comptes.etat_des_parties(bd.connexion(), session.compte_id)}}
    reponse = jsonify(corps)
    reponse.status_code = statut
    if session.jeton:
        _cookie(reponse, session.jeton)
    return reponse


@bp.after_request
def _jamais_en_cache(reponse: Response) -> Response:
    if request.path.startswith(comptes.CHEMIN_COOKIE):
        reponse.headers["Cache-Control"] = "no-store"
    return reponse


@bp.errorhandler(comptes.CompteInvalide)
def _compte_invalide(erreur: comptes.CompteInvalide):
    return jsonify({"erreur": str(erreur)}), erreur.statut


@bp.errorhandler(comptes.NonAutorise)
def _non_autorise(erreur: comptes.NonAutorise):
    reponse = jsonify({"erreur": str(erreur), "coupe": erreur.coupe})
    reponse.status_code = 401
    _cookie(reponse, None)
    return reponse


@bp.errorhandler(bd.Indisponible)
@bp.errorhandler(sqlite3.Error)
def _base_indisponible(erreur: Exception):
    """⚠️ Les comptes tombent, pas le jeu : la page et les definitions n'ouvrent jamais la base."""
    current_app.logger.error("base de donnees indisponible : %r", erreur)
    return jsonify({"erreur": "les comptes sont indisponibles pour l'instant"}), 503


@bp.route("/api/compte/inscription", methods=["POST"])
def api_compte_inscription():
    return _compte_ouvert(comptes.inscrire(bd.connexion(), request.get_json(silent=True)), 201)


@bp.route("/api/compte/connexion", methods=["POST"])
def api_compte_connexion():
    return _compte_ouvert(
        comptes.connecter(bd.connexion(), request.get_json(silent=True), jeton_actuel=_jeton())
    )


@bp.route("/api/compte/ouvrir", methods=["POST"])
def api_compte_ouvrir():
    """Au chargement du jeu : le compte de cet appareil, s'il en a un — et le jeton tourne."""
    if not _jeton():
        return jsonify({"compte": None})
    return _compte_ouvert(comptes.authentifier(bd.connexion(), _jeton(), tourner=True))


@bp.route("/api/compte/deconnexion", methods=["POST"])
def api_compte_deconnexion():
    if _jeton():
        try:
            comptes.deconnecter(bd.connexion(), comptes.authentifier(bd.connexion(), _jeton()))
        except comptes.NonAutorise:
            pass  # deja delie : le cookie s'efface quand meme
    reponse = jsonify({"compte": None})
    _cookie(reponse, None)
    return reponse


@bp.route("/api/compte/parties/<int:n>", methods=["GET"])
def api_compte_partie(n: int):
    session = comptes.authentifier(bd.connexion(), _jeton())
    return jsonify(comptes.lire_partie(bd.connexion(), session.compte_id, n))


@bp.route("/api/compte/parties/<int:n>", methods=["POST"])
def api_compte_partie_ecrire(n: int):
    """Un instantane monte. POST et pas PUT : `sendBeacon`, le seul appel qui survit a
    la fermeture d'un onglet sur telephone, ne sait faire que POST."""
    # ⚠️ AVANT de lire le corps : la borne du site est celle d'un corps ordinaire.
    request.max_content_length = comptes.REQUETE_PARTIE_MAX_OCTETS
    session = comptes.authentifier(bd.connexion(), _jeton())
    ecrite, etat = comptes.ecrire_partie(
        bd.connexion(), session.compte_id, n, request.get_json(silent=True)
    )
    if ecrite:
        return jsonify(etat)
    return jsonify({"erreur": "la partie du serveur est plus avancée", "serveur": etat}), 409


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


@bp.route("/travailleur.js")
def travailleur():
    """Le travailleur hors ligne, A LA RACINE : il ne controle que son dossier.

    Rien de fige : `no-cache` et un ETag (faible compris, comme `_revalide`) — le
    navigateur le redemande a chaque visite, et un 304 ne coute rien. Voir
    `app/hors_ligne.py`.
    """
    corps, empreinte = hors_ligne.travailleur(
        _page_d_accueil(), url_for("jeu.accueil"),
        Path(current_app.static_folder, "audio"), url_for("static", filename="audio/"))
    if request.if_none_match.contains_weak(empreinte):
        reponse = Response(status=304)
    else:
        reponse = Response(corps, mimetype="text/javascript")
    reponse.headers["ETag"] = f'"{empreinte}"'
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
