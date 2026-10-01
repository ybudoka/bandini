"""La caisse populaire de La Shop, et le casse de l'arc X (docs/jalons/m16-cent-missions.md, vague 15).

Martin (1er oct. 2026) : « le casse dans un vrai lieu posé en dernier ». La CAISSE POP d'origine (une façade peinte du
Petit-Canton) est devenue l'ÉCOLE LA MANTE le 29 sept. ; celle-ci est neuve. ⚠️ **Le Faubourg n'a plus une porte de
commerce libre** (le dojo et le Rialto ont pris les deux) : la caisse est à LA SHOP — la caisse des ouvriers, où le
fourgon dépose la paie de l'usine Prévost. C'est le seul intérieur où l'on se bat contre le temps.

⚠️ **SUR LA VILLE FINIE, SANS UN DÉ, EN DERNIER** (juste avant les étages) : comme le DOJO DION et les enseignes, elle
reprend la pièce d'un commerce ordinaire — pièce redessinée, enseigne repeinte, porte renommée, un point d'intérêt au
bout de la liste. Aucune tuile, aucun décor, aucune porte de plus : la ville d'avant est la même, clé par clé
(`tests/test_caisse.py`). ⚠️ Posée APRÈS `devants.deplacer` : le devant d'un lieu de mission est plus large, et le
calculer pour elle aurait déplacé du décor — la porte choisie a donc déjà un devant de mission dégagé (un juge, sur
quatre graines). Et AVANT `etages.monter` : une pièce faite à la main n'a pas d'étages (comme le bingo).

Le choix est une MESURE : une porte de commerce de la trame (ni la bande nord, ni un lieu garanti, ni un logement),
d'une famille qui garde au moins une autre porte, dont l'enseigne tient « CAISSE POP » et dont aucune mission ne lit
le nom (`boutique:<mot>`) — la plus grande pièce, à égalité la plus au nord puis la plus à l'ouest.

Ce module dessine et choisit ; le navigateur joue le casse (`static/js/caisse.js`).
"""

from __future__ import annotations

import re

from . import devantures

#: Le slug de la caisse : sa porte, sa pièce, son lieu (`porte:caisse_pop`, `ruelle:caisse_pop:n`).
SLUG = "caisse_pop"
ENSEIGNE = "CAISSE POP"
NOM = "La caisse populaire"
#: Le plus petit plancher (murs déduits) : un comptoir de guichets, la voûte derrière et le bureau du gérant
#: dans un coin, une salle d'attente devant. En deçà, la caisse cherche une autre porte.
MESURES_MIN = (9, 8)

#: L'habit de la pièce (`sprites.js`, `TUILES['B@caisse']`…) : la boiserie brune et le plâtre crème des années
#: soixante-dix, le prélart beige, les guichets à vitre, la voûte d'acier, le bureau de chêne du gérant.
HABIT = "caisse"
MATERIAUX = {"B": HABIT, "W": HABIT, "D": HABIT, "u": HABIT, "c": HABIT, "m": HABIT, "a": HABIT}

#: Une pièce posée par la ville (`carte.poser_la_piece`) : `<famille>_<n>`, jamais une pièce dessinée à la main.
POSEE = re.compile(r"^[a-z]+_\d+$")

#: Ce que le casse met dans le sac, selon l'objectif (`obtenir`, `table: "caisse"`) : le navigateur joue chacun à
#: sa façon (`caisse.js`). ⚠️ Lu par `tests/test_missions.py` (un objet de table qui n'est pas ici ne se donne
#: jamais) et par le navigateur, qui en garde sa copie : un juge les compare.
OBJETS = {
    # x01 : regarder la voûte de près, le temps de compter ses boulons.
    "plan_caisse": "reperage",
    # x03 : le colis au gérant, en uniforme de livreur — le garde s'habitue à ta face.
    "bordereau": "livraison",
    # x04 : la minuterie de la voûte, une minute à tenir, et les sacs de la paie.
    "sacs_caisse": "coup",
}


def piece_de_caisse(largeur: int, hauteur: int, porte: int) -> dict:
    """La caisse aux mesures d'une part de bâtiment (`largeur` × `hauteur` de plancher, `porte` : la colonne de la
    sortie, murs compris). ⚠️ Sans un dé : les mêmes mesures donnent la même caisse.

    - Au fond, derrière le comptoir : la VOÛTE (un bloc de 2 × 2, sa porte ronde à minuterie) et le BUREAU DU
      GÉRANT, fermé d'une cloison, dans le coin le plus loin de la porte ; une allée libre devant les deux.
    - Le COMPTOIR DES GUICHETS barre la pièce d'un mur à l'autre, sauf la petite porte battante du bout.
    - Devant : la salle d'attente — un banc de chaises au mur, la table des bordereaux, une plante.
    """
    from .carte import _gens, _piece, _plan_de, _pt

    p = porte - 1                                        # la colonne de l'entrée, en plancher
    grille = [[" "] * largeur for _ in range(hauteur)]
    yc = max(3, hauteur // 2 - 1)                         # la rangée du comptoir
    gauche = p > largeur / 2                              # le bureau du côté le plus loin de la porte
    # Le bureau du gérant : trois colonnes, fermées d'une cloison, ouvertes sur l'allée (la rangée yc - 1).
    bx = (0, 1, 2) if gauche else (largeur - 3, largeur - 2, largeur - 1)
    cloison = 3 if gauche else largeur - 4
    for y in range(0, yc - 1):
        grille[y][cloison] = "B"
    fond, coin = (bx[0], bx[2]) if gauche else (bx[2], bx[0])
    grille[0][fond] = "k"                                 # le classeur des prêts
    grille[0][coin] = "n"                                 # le caoutchouc du gérant
    pupitre = (bx[0], bx[1]) if gauche else (bx[1], bx[2])
    for x in pupitre:
        grille[2][x] = "a"                                # son bureau de chêne
    gerant = (pupitre[0] if gauche else pupitre[1], 1)    # derrière son bureau, face à la porte
    # La voûte : deux sur deux contre le mur du fond, au milieu de ce qui reste.
    lo, hi = (cloison + 1, largeur - 1) if gauche else (0, cloison - 1)
    vx = (lo + hi) // 2 if gauche else (lo + hi - 1) // 2
    for y in (0, 1):
        grille[y][vx] = grille[y][vx + 1] = "m"
    # Le comptoir des guichets, d'un mur à l'autre — sauf la porte battante, au bout opposé au bureau.
    battante = largeur - 1 if gauche else 0
    for x in range(largeur):
        if x != battante:
            grille[yc][x] = "c"
    # La salle d'attente : un banc de chaises contre le mur du côté du bureau, la table des bordereaux, une plante
    # au coin opposé à l'entrée.
    banc = 0 if gauche else largeur - 1
    for y in range(yc + 2, hauteur - 2):
        grille[y][banc] = "h"
    tx = largeur // 2 - 1
    if abs(tx - p) <= 1 or abs(tx + 1 - p) <= 1:
        tx = 2 if not gauche else largeur - 4
    grille[yc + 2][tx] = grille[yc + 2][tx + 1] = "a"
    plante = largeur - 1 if p < largeur / 2 else 0
    if grille[hauteur - 1][plante] == " " and abs(plante - p) >= 2:
        grille[hauteur - 1][plante] = "n"
    # Les points : la voûte (sa tuile du bas, à côté de l'allée). Le gérant n'a pas de point : on lui parle.
    points = [_pt("voute", vx + 1, 2)]
    # Les gens : deux caissières derrière les guichets, le gérant à son bureau, le garde près de la porte, deux
    # clients en ligne devant un guichet.
    caissieres = [(x, yc - 1) for x in (largeur // 2 - 2, largeur // 2 + 1) if 0 <= x < largeur]
    gens = [("commis", x + 1, y + 1) for x, y in caissieres if grille[y][x] == " "]
    gens.append(("gerant", gerant[0] + 1, gerant[1] + 1))
    gx = p + 2 if p + 2 < largeur and grille[hauteur - 2][p + 2] == " " else p - 2
    gens.append(("vigile", gx + 1, hauteur - 2 + 1))
    for k, x in enumerate((largeur // 2, largeur // 2 + 2)):
        y = yc + 1
        if 0 <= x < largeur and grille[y][x] == " " and (x, y) != (p, hauteur - 1):
            gens.append(("client", x + 1, y + 1))
    piece = _piece(SLUG, NOM, _plan_de(grille, porte), sol="u", points=tuple(points), gens=_gens(*gens),
                   materiaux=MATERIAUX)
    # Pour le navigateur (en tuiles de la pièce, murs compris) : la PORTE BATTANTE du comptoir — un piéton ne cherche
    # pas son chemin, `caisse.js` fait passer par là qui doit changer de côté — et la PORTE D'EN ARRIÈRE, dans le mur
    # du côté de la battante, au bout de l'allée : c'est par là qu'entrent les gardes du fourgon (peinte par-dessus
    # le mur, ce n'est pas une tuile : la pièce n'a qu'une porte).
    piece["battante"] = {"x": battante + 1, "y": yc + 1}
    piece["arriere"] = {"x": largeur + 1 if gauche else 0, "y": yc}
    return piece


def _mots_des_missions() -> set[str]:
    """Les mots d'enseigne que les missions lisent (`boutique:<mot>`) : une façade qu'une mission nomme garde son nom."""
    from . import missions

    mots: set[str] = set()

    def lire(v) -> None:
        if isinstance(v, str) and v.startswith("boutique:"):
            mots.add(v.split(":", 1)[1].upper())
        elif isinstance(v, dict):
            for x in v.values():
                lire(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                lire(x)

    lire(missions.CATALOGUE)
    return mots


def _devanture(ville: dict, porte: dict) -> dict | None:
    return next((d for d in ville["devantures"] if d["y"] == porte["y"] and d["x"] <= porte["x"] < d["x"] + d["l"]),
                None)


def choisir(ville: dict, aires: dict | None = None) -> tuple[dict, dict, dict] | None:
    """(la porte, sa devanture, sa pièce) que la caisse reprend, ou None. Une mesure, jamais un dé.

    ⚠️ `aires` : les tuiles de bâtiment derrière chaque vitrine (`_Chantier.aires_des_devantures`, dans le repère de la
    ville finie). La caisse n'en prend pas une trop grande pour son enseigne (« CAISSE POP » est un nom MOYEN,
    `devantures.a_sa_taille`) : sur la graine 7, la plus grande pièce était un hangar de 361 tuiles."""
    familles: dict[str, int] = {}
    for porte in ville["portes"]:
        it = porte.get("interieur") or ""
        if POSEE.match(it) and it in ville["interieurs"]:
            familles[it.rsplit("_", 1)[0]] = familles.get(it.rsplit("_", 1)[0], 0) + 1
    mots = _mots_des_missions()
    meilleure = None
    for porte in ville["portes"]:
        it = porte.get("interieur") or ""
        dedans = ville["interieurs"].get(it)
        if not dedans or not POSEE.match(it) or it.startswith("logement") or porte.get("lieu") != it:
            continue
        if familles.get(it.rsplit("_", 1)[0], 0) <= 1:
            continue                                     # jamais la dernière porte d'une famille
        largeur, hauteur = dedans["largeur"] - 2, dedans["hauteur"] - 2
        if largeur < MESURES_MIN[0] or hauteur < MESURES_MIN[1]:
            continue
        devanture = _devanture(ville, porte)
        if not devanture or not devantures.tient_en(ENSEIGNE, devanture["l"]):
            continue
        aire = (aires or {}).get((devanture["x"], devanture["y"]))
        if aire is not None and not devantures.a_sa_taille(ENSEIGNE, aire):
            continue
        if any(m in (devanture.get("texte") or "").upper() for m in mots):
            continue
        cle = (-largeur * hauteur, porte["y"], porte["x"])
        if meilleure is None or cle < meilleure[0]:
            meilleure = (cle, porte, devanture, dedans)
    return meilleure[1:] if meilleure else None


def poser(ville: dict, aires: dict | None = None) -> dict | None:
    """Reprend la pièce choisie et en fait la caisse. Rend `{"porte": [x, y]}`, ou None si rien ne convient (rien ne
    plante : les missions du casse restent alors sans lieu, et `test_caisse` le dit pour la vraie ville)."""
    choix = choisir(ville, aires)
    if not choix:
        return None
    porte, devanture, dedans = choix
    ville["interieurs"].pop(porte["interieur"], None)
    ville["interieurs"][SLUG] = piece_de_caisse(dedans["largeur"] - 2, dedans["hauteur"] - 2, dedans["sortie"]["x"])
    porte.update({"interieur": SLUG, "lieu": SLUG, "nom": ENSEIGNE})
    devanture["texte"] = ENSEIGNE
    devanture["genre"] = devantures.genre_index("service")
    ville["points_interet"].append({"type": SLUG, "slug": SLUG, "nom": NOM, "x": porte["x"], "y": porte["y"] + 1,
                                    "famille": "service"})
    return {"porte": [porte["x"], porte["y"]]}
