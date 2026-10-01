"""Des étages dedans aussi (docs/jalons/des-etages-dedans-aussi.md) : combien d'étages une façade peint au-dessus
de son rez — compté ICI, une fois, sur la ville finie et sans un dé — et autant de pièces derrière sa porte.

⚠️ Python compte, le JS peint : `Monde.logementElargi` et `Monde.etagesDuCommerce` lisent `au_dessus`. La règle ne
vit qu'ici ; la changer, c'est changer le dehors ET le dedans.
"""
from __future__ import annotations

import math
import re

#: Au plus tant d'étages peints au-dessus du rez (la boîte d'un morceau de ville le sait, `monde.js`).
ETAGES_MAX = 3
#: Jusqu'où le mur d'une façade s'étend, de chaque côté, sur le mur nu de son bâtiment.
MUR_ETENDU = 8
#: Les matières de toit qui font un bâtiment — pas la tôle des cabanes (`MATIERES_TEINTES`, monde.js).
MATIERES = "BEOP"
VOISINES = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _u32(v: float | int) -> int:
    return int(v) & 0xFFFFFFFF


def _i32(v: float | int) -> int:
    n = _u32(v)
    return n - (1 << 32) if n >= 1 << 31 else n


def hash2(x: int, y: int) -> int:
    """`hash2` de base.js, au bit près. ⚠️ Sa deuxième multiplication est un FLOTTANT en JS (pas `Math.imul`) :
    le produit dépasse 2**53 et s'arrondit — un float Python s'arrondit pareil."""
    h = _i32(x * 374761393 + y * 668265263)
    h = float(_i32(h ^ (_u32(h) >> 13))) * 1274126177.0
    return _u32(_i32(h) ^ (_u32(h) >> 16))


def _toits(sol: list[str]) -> list[list[int]]:
    """Le bâtiment de chaque tuile de toit (-1 ailleurs) : les tuiles d'une même matière reliées entre elles,
    numérotées dans l'ordre de lecture — `teintesDesToits().qui`."""
    h, w = len(sol), len(sol[0])
    qui = [[-1] * w for _ in range(h)]
    n = 0
    for y in range(h):
        for x in range(w):
            g = sol[y][x]
            if qui[y][x] >= 0 or g not in MATIERES:
                continue
            qui[y][x] = n
            pile = [(x, y)]
            while pile:
                cx, cy = pile.pop()
                for dx, dy in VOISINES:
                    xx, yy = cx + dx, cy + dy
                    if 0 <= xx < w and 0 <= yy < h and qui[yy][xx] < 0 and sol[yy][xx] == g:
                        qui[yy][xx] = n
                        pile.append((xx, yy))
            n += 1
    return qui


def _mur(q: dict, qui: list[list[int]], sol: list[str], prises: set, aussi: frozenset | set = frozenset()
         ) -> tuple[int, int]:
    """Le mur d'une façade va au bout de son bâtiment (`murDuBatiment`) : (x, largeur)."""
    w, y = len(sol[0]), q["y"]

    def batiment(x: int) -> int:
        return qui[y - 1][x] if 0 <= x < w and y > 0 else -1

    lui = batiment(q["x"])

    def libre(x: int) -> bool:
        return (0 <= x < w and lui >= 0 and batiment(x) == lui and sol[y][x] in "FW"
                and (x, y) not in prises and (x, y) not in aussi)

    x0, x1 = q["x"], q["x"] + q["l"] - 1
    if q.get("declin") is None:
        while x0 > q["x"] - MUR_ETENDU and libre(x0 - 1):
            x0 -= 1
        while x1 < q["x"] + q["l"] - 1 + MUR_ETENDU and libre(x1 + 1):
            x1 += 1
    return x0, x1 - x0 + 1


def _profondeur(qui: list[list[int]], y: int, x0: int, large: int) -> int:
    """Combien de rangées de SON toit il y a au-dessus de la façade, à sa colonne la moins profonde."""
    profondeur = 99
    for x in range(x0, x0 + large):
        lui = qui[y - 1][x] if x >= 0 and y > 0 else -1
        p = 0
        while lui >= 0 and y - 1 - p >= 0 and qui[y - 1 - p][x] == lui:
            p += 1
        profondeur = min(profondeur, p)
    return profondeur


def compter(ville: dict) -> None:
    """`au_dessus` sur chaque logement et chaque devanture : les étages que sa façade peint au-dessus du rez.
    ⚠️ Une rangée de toit reste toujours visible : un bâtiment peu profond en montre moins qu'il n'en a."""
    sol, residences, devantures = ville["sol"], ville["residences"], ville["devantures"]
    qui = _toits(sol)
    prises = {(q["x"] + i, q["y"]) for q in devantures + residences for i in range(q["l"])}
    murs_des_logements: set[tuple[int, int]] = set()
    for r in residences:
        x0, large = _mur(r, qui, sol, prises)
        murs_des_logements |= {(x0 + i, r["y"]) for i in range(large)}
        r["au_dessus"] = max(0, min(r["etages"] - 1, ETAGES_MAX, _profondeur(qui, r["y"], x0, large) - 1))
    for d in devantures:
        # Un commerce : deux ou trois étages en tout, à l'empreinte de sa devanture ; la rangée au-dessus de la
        # vitrine est celle de l'enseigne. Son mur s'arrête devant celui d'un logement.
        x0, large = _mur({"x": d["x"], "y": d["y"], "l": d["l"]}, qui, sol, prises, murs_des_logements)
        etages = 2 + hash2(d["x"], d["y"]) % 2
        d["au_dessus"] = max(0, min(etages - 1, ETAGES_MAX, _profondeur(qui, d["y"], x0, large) - 2))


#: Une pièce POSÉE par la ville (`poser_la_piece` : `<famille>_<n>`, renommée `nord_…` dans la bande) — jamais
#: une pièce dessinée à la main (le terminus, l'hôtel, le tripot).
GENEREE = re.compile(r"^(?:nord_)?[a-z_]+?_(\d+)$")
#: Un meuble d'une tuile qui cède sa place à l'escalier quand le plancher n'en a plus (jamais un lit, un comptoir).
MEUBLES_QUI_CEDENT = "nke"


def niveau(slug: str, k: int) -> str:
    """Le nom du k-ième niveau : le rez, `_haut`, `_haut2`… (`_haut` était celui des plex, on le garde)."""
    return slug if k == 0 else f"{slug}_haut" if k == 1 else f"{slug}_haut{k}"


def suite(pieces: dict, slug: str) -> list[str]:
    """Le rez et ses étages, du bas vers le haut."""
    niveaux = [slug]
    while niveau(slug, len(niveaux)) in pieces:
        niveaux.append(niveau(slug, len(niveaux)))
    return niveaux


def facade_de(ville: dict, porte: dict) -> dict | None:
    for q in ville["residences"] + ville["devantures"]:
        if q["y"] == porte["y"] and q["x"] <= porte["x"] < q["x"] + q["l"]:
            return q
    return None


def ajouter_un_escalier(piece: dict, vers: str, *, descend: bool = False) -> bool:
    """Un escalier de plus dans une pièce finie : sur le plancher qu'on rejoint depuis la porte, le plus loin
    d'elle, jamais sur la rangée d'entrée ni à moins de deux tuiles d'un autre point (`pointSousLaMain` les
    confondrait) — sauf d'un autre escalier, qu'on foule. Faute de plancher, un petit meuble (`MEUBLES_QUI_CEDENT`) cède sa place ; faute de tout, le
    point `fouiller` qui gêne s'en va. `False` : aucune place."""
    from . import carte
    sol = [list(ligne) for ligne in piece["sol"]]
    ax, ay = piece["apparition"]["x"], piece["apparition"]["y"]
    atteignable = next(g for g in carte.composantes_marchables(piece) if (ax, ay) in g)
    gens = {(g["x"], g["y"]) for g in piece["gens"]}
    sous_un_point = {(p["x"], p["y"]) for p in piece["points"]}

    def places(points: list[dict], colle: int) -> list[tuple[int, int]]:
        bonnes = []
        for y in range(1, piece["hauteur"] - 2):
            for x in range(1, piece["largeur"] - 1):
                g = sol[y][x]
                sur_le_plancher = g == piece["plancher"] and (x, y) in atteignable
                cede = g in MEUBLES_QUI_CEDENT and any((x + dx, y + dy) in atteignable for dx, dy in VOISINES)
                if not (sur_le_plancher or cede) or (x, y) in gens or (x, y) in sous_un_point:
                    continue
                if math.hypot(x - ax, y - ay) < carte.RAYON_POINT:
                    continue
                # ⚠️ Deux escaliers peuvent se toucher (`colle`), en dernier recours : debout sur une marche, c'est
                # elle que prend `pointSousLaMain` (`faceA` : dessus). Une petite pièce du milieu n'a parfois pas
                # d'autre place.
                if all(max(abs(x - p["x"]), abs(y - p["y"])) >= (colle if p["type"] == "escalier" else 2)
                       for p in points):
                    bonnes.append((x, y))
        # Le plancher d'abord, puis le plus loin de la porte ; l'ordre de lecture départage.
        return sorted(bonnes, key=lambda t: (sol[t[1]][t[0]] != piece["plancher"],
                                             -math.hypot(t[0] - ax, t[1] - ay), t[1], t[0]))

    points = piece["points"]
    choix = places(points, 2) or places(points, 1)
    if not choix:
        points = [p for p in points if p["type"] != "fouiller"]
        choix = places(points, 2) or places(points, 1)
    if not choix:
        return False
    x, y = choix[0]
    sol[y][x] = "/"
    piece["sol"] = ["".join(ligne) for ligne in sol]
    piece["points"] = [p for p in points] + [{"type": "escalier", "x": x, "y": y, "vers": vers,
                                              **({"descend": True} if descend else {})}]
    carte._verifier_piece(piece)
    return True


def retirer_l_escalier(piece: dict, vers: str) -> None:
    """L'escalier qui menait à un étage que la façade ne peint pas : sa marche redevient du plancher."""
    for p in [p for p in piece["points"] if p["type"] == "escalier" and p["vers"] == vers]:
        ligne = piece["sol"][p["y"]]
        piece["sol"][p["y"]] = ligne[:p["x"]] + piece["plancher"] + ligne[p["x"] + 1:]
        piece["points"].remove(p)


def monter(ville: dict) -> None:
    """Derrière chaque porte posée par la ville, `1 + au_dessus` niveaux : on retire ce que la façade ne peint pas,
    on empile ce qui manque. ⚠️ Les deux escaliers ou aucun : un étage qu'on n'a pas pu relier ne se pose pas."""
    from . import carte
    pieces = ville["interieurs"]
    faites: set[str] = set()
    for porte in ville["portes"]:
        slug = porte.get("interieur")
        m = GENEREE.match(slug or "")
        if not m or slug not in pieces or slug in faites:
            continue
        faites.add(slug)
        facade = facade_de(ville, porte)
        if facade is None:
            continue
        voulu = 1 + facade["au_dessus"]
        niveaux = suite(pieces, slug)
        while len(niveaux) > voulu:
            haut = niveaux.pop()
            del pieces[haut]
            retirer_l_escalier(pieces[niveaux[-1]], haut)
        rez = pieces[slug]
        commerce = facade in ville["devantures"]
        while len(niveaux) < voulu:
            k, dessous = len(niveaux), niveaux[-1]
            neuf = niveau(slug, k)
            haut = carte.piece_de_logement(
                neuf, rez["largeur"] - 2, rez["hauteur"] - 2, rez["sortie"]["x"], etage=dessous, haut=True,
                variante=int(m.group(1)) + k, nom="Le logement du commerçant" if commerce else None)
            if not any(p["type"] == "escalier" for p in haut["points"]):
                break
            if not ajouter_un_escalier(pieces[dessous], neuf):
                break
            pieces[neuf] = haut
            niveaux.append(neuf)
