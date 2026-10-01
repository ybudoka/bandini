"""Les lignes des passants (`app/lectures.py`, `docs/jalons/la-reputation-et-la-lecture-des-passants.md`) : une
soixantaine, un lot par quartier, qui tiennent au-dessus d'une tête — et que rien d'autre que la lecture ne lit."""

import pathlib
import re

from app import definitions, lectures
from tests import villes

RACINE = pathlib.Path(__file__).resolve().parent.parent

#: Les quartiers où l'on vit : huit lignes au moins chacun (tranché par Martin : huit à dix par quartier).
GRANDS = ("faubourg", "erables", "shop", "quais", "pointe", "canton", "gare")


def ranger(texte: str, largeur: int) -> list[str]:
    """La même coupe que `Lecture.ranger` (le juge au banc compare les rangées peintes à celles-ci)."""
    rangees = [""]
    for mot in texte.split(" "):
        if rangees[-1] and len(rangees[-1]) + 1 + len(mot) > largeur:
            rangees.append(mot)
        else:
            rangees[-1] = f"{rangees[-1]} {mot}" if rangees[-1] else mot
    return rangees


def toutes() -> list[str]:
    return [ligne for lot in lectures.LIGNES.values() for ligne in lot]


def test_une_soixantaine_huit_a_dix_par_grand_quartier():
    assert 55 <= len(toutes()) <= 75, len(toutes())
    for q in GRANDS:
        assert 8 <= len(lectures.LIGNES[q]) <= 10, (q, len(lectures.LIGNES[q]))
    assert len(set(toutes())) == len(toutes()), "une ligne en double"


def test_chaque_lot_est_un_quartier_de_la_ville():
    quartiers = {z.get("district") or z["slug"] for z in villes.exporter()["zones"]}
    assert set(lectures.LIGNES) <= quartiers, set(lectures.LIGNES) - quartiers
    assert set(GRANDS) <= set(lectures.LIGNES)


def test_chaque_ligne_tient_en_deux_rangees_au_dessus_d_une_tete():
    for ligne in toutes():
        rangees = ranger(ligne, lectures.LARGEUR_RANGEE)
        assert len(rangees) <= 2 and max(map(len, rangees)) <= lectures.LARGEUR_RANGEE, rangees


def test_chaque_lettre_se_dessine():
    """La police pixel (`POLICE_PIXEL`) n'a que des capitales, des chiffres et un peu de ponctuation ; les accents se
    posent par-dessus (`MARQUES_PIXEL`)."""
    permis = re.compile(r"^[A-Za-zÀÂÇÉÈÊËÎÏÔÛÙÜàâçéèêëîïôûùüœŒ0-9 .,:'!?$/()%-]+$")
    for ligne in toutes():
        assert permis.match(ligne), ligne
        assert ligne == ligne.strip() and "  " not in ligne, ligne


def test_les_lignes_voyagent_dans_la_suite_du_paquet():
    assert "lectures" in definitions.DANS_LA_SUITE
    d = definitions.assembler()["lectures"]
    assert d["lignes"]["faubourg"] == list(lectures.LIGNES["faubourg"])
    assert d["largeur_rangee"] == lectures.LARGEUR_RANGEE


def test_aucune_mission_ne_lit_une_ligne_de_passant():
    """Une ligne, c'est de la couleur : ni une mission, ni un boulot, ni un objectif ne la lit."""
    fautifs = []
    for chemin in [*(RACINE / "app" / "missions").rglob("*.py"), *(RACINE / "static" / "js").glob("*.js")]:
        if chemin.name in ("lecture.js", "jeu.js"):
            continue
        texte = chemin.read_text(encoding="utf-8")
        if re.search(r"\bLecture\.|\.lectures?\b|[\x27\"]lectures[\x27\"]", texte):
            fautifs.append(chemin.name)
    assert not fautifs, fautifs


def test_lire_n_est_pas_un_objectif():
    from app import missions
    types = missions.TYPES_OBJECTIFS
    assert types and not any("lire" in t or "lecture" in t for t in types), types
