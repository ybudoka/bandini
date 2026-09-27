"""Les enseignes qui ouvrent pour vrai : bingo, quilles, lave-auto, Rialto
(docs/jalons/les-enseignes-qui-ouvrent-pour-vrai.md).

Quatre façades de la ville deviennent des endroits où l'on entre : le BINGO du sous-sol, la SALLE DE
QUILLES, le LAVE-AUTO et le CINÉMA RIALTO. Chacune reprend la porte d'un commerce ordinaire — sa pièce
est redessinée, son enseigne repeinte, sa porte renommée —, comme le DOJO DION (`poser_le_dojo`).

⚠️ **SUR LA VILLE FINIE ET SANS UN DÉ** : ni tuile, ni bâtiment, ni décor ne bouge. Le choix est une
MESURE : la façade qui porte déjà le nom (le BINGO d'une rue pauvre), sinon une porte de son district
(une qui tient le nom entier d'abord), la plus proche de son cœur — et faute de mieux, d'un autre
district. ⚠️ Le Faubourg, serré de lieux garantis, n'a que DEUX portes de commerce (mesure du 26 sept.
2026 : le dojo en a pris une, le Rialto l'autre) : la salle de quilles est à La Shop, un hangar de
ligue. Aucune qui convient : l'enseigne n'ouvre pas, et rien ne plante.

⚠️ **LE LAVE-AUTO SE TRAVERSE EN CHAR** : sa baie est peinte sur la chaussée devant la porte
(`ville["lave_auto"]`) — rien n'y est solide, la rue reste une rue. On y roule au pas, on paie, et le
char lavé est MOINS RECONNAISSABLE : la chaleur baisse d'un cran (`static/js/enseignes.js`).
"""

from __future__ import annotations

from . import devantures as devantures_mod

#: Les quatre, dans l'ordre où elles choisissent leur porte. `prefere` : la façade qui porte déjà le
#: nom l'emporte (la ville AFFICHAIT « BINGO » sans pièce derrière — c'est ce mensonge-là qu'on répare).
#: `court` : ce qu'on peint quand le nom ne tient pas sur le bandeau (quatre tuiles : quinze lettres).
#: `sans_standing` : le standing qu'une façade ne doit pas avoir (un bingo n'est pas cossu :
#: `devantures.COMMERCES_PAUVRES`, et un juge le garde).
ENSEIGNES: tuple[dict, ...] = (
    {"slug": "bingo", "texte": "BINGO", "nom": "Le bingo du sous-sol", "district": "faubourg",
     "famille": "repere", "prefere": "BINGO", "sans_standing": "+"},
    {"slug": "rialto", "texte": "CINÉMA RIALTO", "nom": "Le cinéma Rialto", "district": "faubourg",
     "famille": "repere", "prefere": "CINÉMA RIALTO", "sans_standing": None},
    {"slug": "quilles", "texte": "SALLE DE QUILLES", "court": "QUILLES", "nom": "La salle de quilles",
     "district": "shop", "famille": "repere", "prefere": "SALLE DE QUILLES",
     "sans_standing": None},
    {"slug": "lave_auto", "texte": "LAVE-AUTO", "nom": "Le lave-auto", "district": "erables",
     "famille": "service", "prefere": "LAVE-AUTO", "sans_standing": None},
)

#: Deux enseignes neuves jamais à moins de tant de tuiles l'une de l'autre : un Rialto collé sur la
#: salle de quilles, c'est une rue qui a changé de nom, pas deux endroits.
ECART = 12

#: Les règles que le navigateur joue (`static/js/enseignes.js`).
REGLES = {
    # LE BINGO : une carte de 5 sur 5 (la case du milieu est gratuite), une boule toutes les
    # `appel_s` secondes ; on la marque en appuyant sur ACTION pendant `fenetre_s` (le crayon est
    # dans ta main). Trois madames jouent aussi : la première ligne pleine gagne le gros lot.
    # ⚠️ Tout se tire à l'empreinte du jour et du numéro de la carte : jamais `B.rng()`.
    "bingo": {"carte": 3, "gros_lot": 20, "appel_s": 3.2, "fenetre_s": 2.6, "madames": 3},
    # LE RIALTO : le billet, les heures des séances (en heures du jour), et la longueur du film
    # (en secondes de jeu). Le film se regarde assis dans le noir ; il se joue sur la toile.
    "rialto": {"billet": 5, "seances": [18.0, 23.5], "film_s": 45, "repos_pv": 20},
    # LE LAVE-AUTO : le prix, et combien de temps rester AU PAS dans la baie avant que les brosses
    # aient fini. Au-dessus de `vitesse_max`, on passe tout droit sans se faire laver.
    "lave_auto": {"prix": 12, "duree_s": 1.5, "vitesse_max": 1.2},
}


# --- Les pièces --------------------------------------------------------------------------------
#
# ⚠️ **À LA MESURE DE LEUR BÂTIMENT** (le juge `la pièce a les mesures de son bâtiment`, et « je veux que
# l'intérieur soit PROPORTIONNÉ à l'extérieur », Martin) : chaque pièce se dessine dans le plancher de la
# pièce qu'elle remplace, comme le dojo. `MESURES_MIN` : en deçà, l'enseigne cherche une autre porte — un
# cinéma de cinq tuiles sur quatre n'est pas un cinéma. Sans un dé : les mêmes mesures donnent la même pièce.

#: Le plus petit plancher (largeur, profondeur, murs déduits) de chacune.
MESURES_MIN = {"bingo": (6, 4), "rialto": (6, 5), "quilles": (7, 5), "lave_auto": (4, 3)}


def _comptoir(grille: list[list[str]], porte: int, long_: int) -> list[tuple[int, int]]:
    """Le comptoir à l'avant-dernière rangée, du côté opposé à la porte (comme un commerce)."""
    largeur, rangee = len(grille[0]), len(grille) - 2
    debut = 0 if porte > largeur / 2 else largeur - long_
    tuiles = [(x, rangee) for x in range(debut, debut + long_)]
    for x, y in tuiles:
        grille[y][x] = "c"
    return tuiles


def piece_de_bingo(largeur: int, hauteur: int, porte: int) -> dict:
    """Le sous-sol : le boulier au fond, les tables de la paroisse (une table, une chaise de chaque côté),
    le comptoir du café à l'avant."""
    from .carte import _completer_les_meubles, _gens, _piece, _plan_de, _poser_le_point, _quelqu_un
    grille = [[" "] * largeur for _ in range(hauteur)]
    grille[0][0], grille[0][largeur - 1] = "k", "j"
    cx = largeur // 2 - 1
    grille[0][cx] = grille[0][cx + 1] = "m"                          # le boulier
    haut, bas = 1, hauteur - 3
    pas = 3 if bas - haut + 1 >= 2 else 1
    for y in range(haut, bas + 1, pas):
        epais = 2 if pas == 3 and y + 1 <= bas else 1
        for x0 in range(1, largeur - 3, 5):
            for dy in range(epais):
                grille[y + dy][x0:x0 + 4] = list("haah")
    comptoir = _comptoir(grille, porte, 2)
    points = [_poser_le_point(grille, "emplettes", "bingo", porte, list(reversed(comptoir)))]
    _completer_les_meubles(grille, porte, "enk", tuple((p["x"] - 1, p["y"] - 1) for p in points))
    pris: set[tuple[int, int]] = set()
    gens = [_quelqu_un(grille, "commis", (comptoir[0][0], hauteur - 3), porte, pris),
            _quelqu_un(grille, "commis", (cx, 1), porte, pris),                       # celui qui crie les boules
            _quelqu_un(grille, "client", (0, hauteur // 2), porte, pris),
            _quelqu_un(grille, "client", (largeur - 1, 1), porte, pris)]
    return _piece("bingo", "Le bingo du sous-sol", _plan_de(grille, porte), sol="u",
                  points=tuple(points), gens=_gens(*[g for g in gens if g]))


def piece_de_rialto(largeur: int, hauteur: int, porte: int) -> dict:
    """La salle : la toile au fond, les rangées de fauteuils et leur allée au milieu, le comptoir du maïs
    soufflé à l'avant. `toile` et `siege` (en tuiles de la pièce, murs compris) servent au film."""
    from .carte import _completer_les_meubles, _gens, _piece, _plan_de, _poser_le_point, _quelqu_un
    grille = [[" "] * largeur for _ in range(hauteur)]
    for x in range(1, largeur - 1):
        grille[0][x] = "]"
    allee = largeur // 2
    for y in range(2, hauteur - 2, 2):
        for x in range(1, largeur - 1):
            if x != allee:
                grille[y][x] = "h"
    comptoir = _comptoir(grille, porte, 2)
    points = [_poser_le_point(grille, "emplettes", "rialto", porte, list(reversed(comptoir)))]
    _completer_les_meubles(grille, porte, "n", tuple((p["x"] - 1, p["y"] - 1) for p in points))
    pris: set[tuple[int, int]] = {(allee, 2)}
    gens = [_quelqu_un(grille, "commis", (comptoir[0][0], hauteur - 3), porte, pris),
            _quelqu_un(grille, "client", (0, 1), porte, pris)]
    piece = _piece("rialto", "Le cinéma Rialto", _plan_de(grille, porte), sol="t",
                   points=tuple(points), gens=_gens(*[g for g in gens if g]))
    piece["toile"] = {"x": 2, "y": 1, "l": largeur - 2}
    piece["siege"] = {"x": allee + 1, "y": 3}
    return piece


def piece_de_quilles(largeur: int, hauteur: int, porte: int) -> dict:
    """La salle : les allées (deux tuiles de large, une tuile entre deux) du fond jusqu'à l'approche, les
    souliers sur l'étagère, le comptoir de la ligue à l'avant."""
    from .carte import _completer_les_meubles, _gens, _piece, _plan_de, _poser_le_point, _quelqu_un
    grille = [[" "] * largeur for _ in range(hauteur)]
    allees = max(1, (largeur - 3) // 3)
    for k in range(allees):
        for y in range(0, hauteur - 3):
            grille[y][3 * k] = grille[y][3 * k + 1] = "["
    for x in range(3 * allees, largeur):
        grille[0][x] = "e"                                           # les souliers de location
    grille[0][largeur - 1] = "j"
    comptoir = _comptoir(grille, porte, 3)
    points = [_poser_le_point(grille, "emplettes", "quilles", porte, list(reversed(comptoir)))]
    _completer_les_meubles(grille, porte, "hn", tuple((p["x"] - 1, p["y"] - 1) for p in points))
    pris: set[tuple[int, int]] = set()
    gens = [_quelqu_un(grille, "commis", (comptoir[1][0], hauteur - 3), porte, pris),
            _quelqu_un(grille, "client", (1, hauteur - 3), porte, pris)]
    return _piece("quilles", "La salle de quilles", _plan_de(grille, porte), sol="t",
                  points=tuple(points), gens=_gens(*[g for g in gens if g]))


def piece_de_lave_auto(largeur: int, hauteur: int, porte: int) -> dict:
    """Le bureau du lave-auto : un commerce de La Shop, et son comptoir qui dit le prix du lavage."""
    from .carte import piece_de_commerce
    piece = piece_de_commerce("lave_auto", "industrie", largeur, hauteur, porte)
    piece["nom"] = "Le lave-auto"
    for q in piece["points"]:
        if q["type"] == "emplettes":
            q["genre"] = "lave_auto"
    return piece


PIECES = {"bingo": piece_de_bingo, "rialto": piece_de_rialto, "quilles": piece_de_quilles,
          "lave_auto": piece_de_lave_auto}


# --- Le choix des portes ----------------------------------------------------------------------

def _devanture(ville: dict, porte: dict) -> dict | None:
    return next((d for d in ville["devantures"] if d["y"] == porte["y"]
                 and d["x"] <= porte["x"] < d["x"] + d["l"]), None)


def _baie(chantier, porte: dict) -> dict | None:
    """La baie du lave-auto : les deux premières rangées de chaussée sous la porte, sur trois
    tuiles de large. ⚠️ Rien n'y est posé : c'est une zone, peinte et lue par le navigateur."""
    from .carte import LEGENDE
    for j in range(1, 6):
        y = porte["y"] + j
        if y + 1 >= chantier.hauteur:
            return None
        rangees = [y, y + 1]
        if all(LEGENDE[chantier.sol[yy][x]].get("route") for yy in rangees
               for x in range(porte["x"] - 1, porte["x"] + 2)):
            return {"x": porte["x"] - 1, "y": y, "l": 3, "h": 2}
    return None


def poser(chantier, ville: dict) -> list[str]:
    """Rend les slugs des enseignes posées. Appelée après le DOJO DION, avant les devants."""
    from . import chantiers as chantiers_mod
    from .carte import DISTRICTS, SPECIAUX, TUILE_PX

    garantis = {s["slug"] for s in SPECIAUX.values()} | {"dojo"}
    interdites: set[tuple[int, int]] = set()
    for ch in ville.get("chantiers") or []:
        interdites |= set(chantiers_mod.tuiles(ch))
    prises: list[tuple[int, int]] = []
    posees = []
    # ⚠️ Une famille de commerce garde toujours une porte (le juge `chaque famille de commerce ouvre une
    # porte`) : la GALERIE D'ART était la seule porte « savoir » de la ville.
    familles: dict[str, int] = {}
    for porte in ville["portes"]:
        if porte.get("interieur") in chantier.pieces:
            famille = porte["interieur"].rsplit("_", 1)[0]
            familles[famille] = familles.get(famille, 0) + 1
    for fiche in ENSEIGNES:
        district = next(d for d in DISTRICTS if d["slug"] == fiche["district"])
        x0, y0, dl, dh = chantier.rect_district(district)
        cx, cy = x0 + dl / 2, y0 + dh / 2
        meilleure = None
        for porte in ville["portes"]:
            dedans = chantier.pieces.get(porte.get("interieur") or "")
            if not dedans or porte["interieur"].startswith("logement") or porte.get("lieu") in garantis:
                continue
            if porte["interieur"] in PIECES or any(max(abs(px - porte["x"]), abs(py - porte["y"])) < ECART
                                                   for px, py in prises):
                continue
            if familles.get(porte["interieur"].rsplit("_", 1)[0], 0) <= 1:
                continue
            mini = MESURES_MIN[fiche["slug"]]
            if dedans["largeur"] - 2 < mini[0] or dedans["hauteur"] - 2 < mini[1]:
                continue
            devanture = _devanture(ville, porte)
            texte = next((t for t in (fiche["texte"], fiche.get("court")) if t and devanture
                          and devantures_mod.tient_en(t, devanture["l"], TUILE_PX)), None)
            if not texte:
                continue
            # ⚠️ Et le BATIMENT a sa mesure, pas seulement la piece (`devantures.TAILLES`) : une salle de
            # quilles se lit de la rue, et un cinema dans une boutique de coin de rue ne se lit pas.
            aire = chantier.aires_des_devantures.get((devanture["x"], devanture["y"]))
            if aire is not None and not devantures_mod.a_sa_taille(texte, aire):
                continue
            deja = devanture["texte"] == fiche["prefere"]
            ailleurs = chantier.district_en(porte["x"], porte["y"]) != fiche["district"]
            if fiche["sans_standing"] and devanture.get("standing") == fiche["sans_standing"]:
                continue
            if (porte["x"], porte["y"]) in interdites:
                continue
            baie = _baie(chantier, porte) if fiche["slug"] == "lave_auto" else None
            if fiche["slug"] == "lave_auto" and not baie:
                continue
            cle = (not deja, ailleurs, texte != fiche["texte"], abs(porte["x"] - cx) + abs(porte["y"] - cy),
                   porte["y"], porte["x"])
            if meilleure is None or cle < meilleure[0]:
                meilleure = (cle, porte, devanture, baie, texte, dedans)
        if not meilleure:
            continue
        _, porte, devanture, baie, texte, dedans = meilleure
        slug = fiche["slug"]
        ancienne = porte["interieur"]
        chantier.pieces.pop(ancienne, None)
        ville["interieurs"].pop(ancienne, None)
        familles[ancienne.rsplit("_", 1)[0]] -= 1
        chantier.pieces[slug] = ville["interieurs"][slug] = PIECES[slug](
            dedans["largeur"] - 2, dedans["hauteur"] - 2, dedans["sortie"]["x"])
        porte.update({"interieur": slug, "lieu": slug, "nom": texte})
        devanture["texte"] = texte
        # ⚠️ La façade GARDE sa famille (`genre`) : la distributrice adossée à côté vend selon elle
        # (`magasins.sortes_devant`), posée avant — un Rialto repeint « nuit » avait une machine à café.
        ville["points_interet"].append({"type": slug, "slug": slug, "nom": fiche["nom"],
                                        "x": porte["x"], "y": porte["y"] + 1, "famille": fiche["famille"]})
        if baie:
            ville["lave_auto"] = baie
        prises.append((porte["x"], porte["y"]))
        posees.append(slug)
    return posees


def pour_le_navigateur(ville: dict) -> dict:
    return {"regles": {k: dict(v) for k, v in REGLES.items()}, "lave_auto": ville.get("lave_auto"),
            "noms": {f["slug"]: f["nom"] for f in ENSEIGNES}}
