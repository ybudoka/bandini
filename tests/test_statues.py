"""Des statues dans les parcs (P4) : où elles se tiennent, et ce qu'elles ne déplacent pas.

⚠️ Les règles sont écrites ICI en toutes lettres (le coeur de la place, le bord du sentier, la
ville d'à côté inchangée) : un juge qui relirait `statues.poser` changerait avec lui.
"""

import json

import pytest

from app import carte, statues

GRANDES = {"statue_fondateur", "statue_cavalier", "statue_hockeyeur"}
BUSTES = {"buste_mairesse", "buste_cure", "buste_inventeur"}


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def _statues(ville, types):
    return [d for d in ville["decor"] if d["type"] in types]


def test_une_statue_au_coeur_de_la_place_de_chaque_parc_de_ville(ville):
    """Un parc de ville a sa place : cinq tuiles sur cinq de poussière de pierre (`g`) où ses allées se
    rejoignent. La statue en occupe le CENTRE — la place l'entoure de deux tuiles de pierre de chaque côté."""
    grandes = _statues(ville, GRANDES)
    assert len(grandes) == 3, f"une statue par parc de ville (trois), pas {len(grandes)}"
    assert {d["type"] for d in grandes} == GRANDES, "les trois grands hommes, chacun le sien"
    sol = ville["sol"]
    for d in grandes:
        x, y = d["x"], d["y"]
        autour = {sol[y + dy][x + dx] for dy in range(-2, 3) for dx in range(-2, 3)}
        assert autour == {"g"}, f"{d['type']} ({x}, {y}) n'est pas au coeur d'une place pavée : {autour}"


def test_un_buste_au_bord_du_sentier_des_grands_parcs_de_quartier_jamais_dessus(ville):
    """Le sentier d'un parc de quartier fait UNE tuile de large : un buste posé dessus le couperait. Il se
    tient sur le gazon, collé au sentier — et à rien d'autre."""
    bustes = _statues(ville, BUSTES)
    assert len(bustes) >= 3, f"les grands parcs de quartier ont leur buste : {len(bustes)}"
    assert {d["type"] for d in bustes} == BUSTES
    sol = ville["sol"]
    for d in bustes:
        x, y = d["x"], d["y"]
        assert sol[y][x] == ",", f"{d['type']} ({x}, {y}) sur « {sol[y][x]} », pas sur le gazon"
        voisins = [sol[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        assert "g" in voisins, f"{d['type']} ({x}, {y}) loin du sentier : {voisins}"
        colles = [o["type"] for o in ville["decor"] if abs(o["x"] - x) + abs(o["y"] - y) == 1]
        assert not colles, f"{d['type']} ({x}, {y}) adossé à {colles} : un meuble de plus, pas un monument"


def test_rien_d_autre_sur_la_tuile_d_une_statue(ville):
    tuiles = {(d["x"], d["y"]) for d in _statues(ville, GRANDES | BUSTES)}
    for cle in statues.COUCHES_PRISES:
        for o in ville.get(cle) or []:
            if o.get("type") in GRANDES | BUSTES:
                continue
            assert (o["x"], o["y"]) not in tuiles, f"un {cle} ({o.get('type')}) sous une statue, en {o['x']}, {o['y']}"


def test_la_ville_sans_ses_statues_est_la_meme_a_la_tuile_pres(ville, monkeypatch):
    """⚠️ Posées sur la ville finie, sans un dé : retirer l'étape ne change RIEN d'autre — ni un arbre, ni un
    paquet, ni un nid-de-poule. C'est la règle qui permet d'en ajouter sans faire tomber les juges des autres."""
    monkeypatch.setattr(statues, "poser", lambda chantier, v: [])
    sans = carte.generer()
    avec = dict(ville, decor=[d for d in ville["decor"] if d["type"] not in GRANDES | BUSTES])
    differentes = [k for k in avec if json.dumps(avec[k], sort_keys=True) != json.dumps(sans.get(k), sort_keys=True)]
    assert not differentes, f"les statues déplacent : {differentes}"


def test_les_statues_arretent_et_ont_une_plaque():
    for t in GRANDES | BUSTES:
        assert t in carte.DECOR_SOLIDE, f"{t} n'est pas solide : on traverserait le bronze"
    plaques = statues.exporter()
    assert set(plaques) == GRANDES | BUSTES
    for t, lignes in plaques.items():
        assert len(lignes) >= 3 and all(ligne.strip() for ligne in lignes), f"la plaque de {t} est vide"
