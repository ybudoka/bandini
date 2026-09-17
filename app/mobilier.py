"""Le mobilier de rue : des arbres de temps à autre, bien placés, et des bancs.

Demande de Martin (16 sept. 2026) : « je veux des bancs sur le bord de la rue,
des arbres de temps à autre bien positionnés ».

⚠️ **Un arbre de rue se plante en RANGÉE, pas au hasard.** Semés tuile par tuile,
des arbres tombent deux fois au même coin et nulle part sur le reste du trottoir :
c'est un terrain vague, pas une rue plantée. Ici on lit chaque BORD de rue — la
file de tuiles qui longe un trottoir entre deux croisements — et on y plante à
intervalle régulier, avec le pas du quartier. Les Érables sont bordés d'arbres,
La Shop n'en a presque pas : c'est ce qui distingue une banlieue d'une cour de
ferraille avant même d'avoir lu une enseigne.

⚠️ **Bien placé veut dire qu'il ne gêne rien.** Jamais dans le coin d'un
croisement (le feu, le lampadaire et la vue du piéton qui traverse), jamais
devant une porte ni juste à côté, jamais au bout d'une entrée de cour, jamais
collé à un autre meuble, et jamais là où il couperait un passage : la tuile
qu'il prend ne doit séparer aucune de ses voisines marchables des autres.

⚠️ **Un banc regarde la rue.** Il a quatre dessins (`banc`, `banc_nord`,
`banc_est`, `banc_ouest`), et c'est le côté du trottoir qui choisit.

⚠️ **Son propre dé, en tout dernier** — après les chantiers et les lignes
d'autobus : un arbre de plus ne déplace ni un abribus, ni un paquet, ni une
enseigne. Un juge compare la ville avec et sans.
"""

from __future__ import annotations

#: Le rythme de chaque quartier. `arbres` : le pas entre deux arbres d'un même
#: bord, en tuiles, et la part des bords qu'on plante. `bancs` : pareil pour les
#: bancs — `None` quand le quartier n'en pose pas au bord de la rue.
RYTHMES: dict[str, dict] = {
    "erables": {"arbres": ((7, 9), 0.80), "bancs": ((22, 28), 0.25)},
    "faubourg": {"arbres": ((10, 12), 0.55), "bancs": ((14, 18), 0.60)},
    "shop": {"arbres": ((14, 18), 0.20), "bancs": None},
    "quais": {"arbres": ((11, 13), 0.40), "bancs": ((18, 22), 0.45)},
    "baie": {"arbres": ((11, 13), 0.40), "bancs": ((18, 22), 0.45)},
    "pointe": {"arbres": ((8, 10), 0.70), "bancs": ((20, 26), 0.35)},
}

#: ⚠️ **LE STANDING PASSE PAR-DESSUS LE QUARTIER** pour les arbres (demande de
#: Martin : « des cartiers plus riche et propre [...], des cartiers plus pauvre et
#: sale »). Une rue cossue est plantée serré et partout ; une rue pauvre ne l'est
#: pas du tout — c'est ce qu'on voit d'abord en changeant de rue, avant la
#: moindre enseigne. `None` : le rythme du district, tel quel.
ARBRES_PAR_STANDING: dict[str, tuple | None] = {
    "cossu": ((6, 8), 0.95),
    "ordinaire": None,
    "pauvre": ((14, 18), 0.0),
}

#: Les bacs à fleurs, en cossu seulement : la part des intervalles d'un bord
#: (d'un bout à l'arbre, d'un arbre au suivant) qui en reçoivent un, au milieu.
#: ⚠️ Pas seulement ENTRE deux arbres : un bord cossu fait huit tuiles en
#: moyenne (813 tuiles sur 94 bords), il porte donc un arbre, et « entre deux
#: arbres » n'a posé que trois bacs dans toute la ville.
PART_BAC_FLEURS = 0.5

#: Un bord plus court que ça ne se plante pas : deux tuiles entre deux coins de
#: rue, ce n'est pas une rue, c'est un bout de trottoir.
BORD_MIN = 5

#: Le coin d'un croisement se garde sur tant de tuiles autour de la boîte.
COIN = 3

#: Ce qui, derrière la tuile, dit qu'un CHAR en sort : un stationnement, une
#: case, une rampe. Un arbre planté là ferme la sortie — jamais.
SORTIES_DE_CHAR = frozenset("pI^v<>RJ")

#: Ce qui, derrière la tuile, dit qu'un PIÉTON en sort : une allée, un chemin,
#: une ruelle. ⚠️ Seulement quand c'en est la BOUCHE : une ruelle qui court
#: parallèle au trottoir, derrière toute la rangée, n'est pas une entrée — et la
#: refuser privait d'arbres la moitié des rues du Faubourg.
PASSAGES = frozenset(".gx")

#: Le côté du trottoir, et le dessin du banc qui le regarde.
BANCS_PAR_COTE = {(0, 1): "banc", (0, -1): "banc_nord", (1, 0): "banc_est", (-1, 0): "banc_ouest"}


def _bords(chantier, ville: dict) -> list[dict]:
    """Chaque bord de rue : une file de tuiles contiguës qui longent le MÊME
    trottoir, du même côté, et qui peuvent recevoir un meuble."""
    from . import autobus, carte

    sol, voie = chantier.sol, ville["voie"]
    largeur, hauteur = chantier.largeur, chantier.hauteur
    coins: set[tuple[int, int]] = set()
    for inter in chantier.intersections:
        for y in range(inter["y"] - COIN - 1, inter["y"] + inter["h"] + COIN + 1):
            for x in range(inter["x"] - COIN - 1, inter["x"] + inter["l"] + COIN + 1):
                coins.add((x, y))
    evites: set[tuple[int, int]] = set(coins) | autobus.parvis(ville)
    rectangles = list(ville.get("chantiers") or []) + list(ville.get("plages") or [])
    if ville.get("foire"):
        rectangles.append(ville["foire"])
    for r in rectangles:
        for y in range(r["y"] - 1, r["y"] + r["h"] + 1):
            for x in range(r["x"] - 1, r["x"] + r["l"] + 1):
                evites.add((x, y))

    def cote_du_trottoir(x: int, y: int) -> tuple[int, int] | None:
        trouves = []
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            tx, ty = x + dx, y + dy
            rx, ry = x + 2 * dx, y + 2 * dy
            if not (0 <= rx < largeur and 0 <= ry < hauteur):
                continue
            if sol[ty][tx] == "." and voie[ry][rx] != "." and carte.LEGENDE[sol[ry][rx]].get("route"):
                trouves.append((dx, dy))
        return trouves[0] if len(trouves) == 1 else None

    places: dict[tuple[int, int], tuple[int, int]] = {}
    for y in range(1, hauteur - 1):
        for x in range(1, largeur - 1):
            if sol[y][x] not in ("_", ",") or (x, y) in evites:
                continue
            cote = cote_du_trottoir(x, y)
            if cote is None:
                continue
            bx, by = x - cote[0], y - cote[1]
            derriere = sol[by][bx]
            if derriere in SORTIES_DE_CHAR or (bx, by) in chantier.entrees:
                continue
            if derriere in PASSAGES:
                cotes = [sol[by + cote[0]][bx + cote[1]], sol[by - cote[0]][bx - cote[1]]]
                if not all(c in PASSAGES for c in cotes):
                    continue                      # la bouche d'une allee
            places[(x, y)] = cote
    bords: list[dict] = []
    vus: set[tuple[int, int]] = set()
    for (x, y) in sorted(places, key=lambda t: (t[1], t[0])):
        if (x, y) in vus:
            continue
        cote = places[(x, y)]
        pas = (1, 0) if cote[0] == 0 else (0, 1)
        file = []
        cx, cy = x, y
        while places.get((cx, cy)) == cote:
            file.append((cx, cy))
            vus.add((cx, cy))
            cx, cy = cx + pas[0], cy + pas[1]
        if len(file) >= BORD_MIN:
            bords.append({"tuiles": file, "cote": cote,
                          "district": chantier.district_en(*file[len(file) // 2]),
                          "standing": chantier.standing_en(*file[len(file) // 2])})
    return bords


def _ne_coupe_rien(chantier, x: int, y: int, solides: set[tuple[int, int]]) -> bool:
    """La tuile prise, ses voisines marchables se rejoignent-elles encore sans
    elle, dans une fenêtre de cinq tuiles ?"""
    from . import carte

    def marche(i: int, j: int) -> bool:
        if not (0 <= i < chantier.largeur and 0 <= j < chantier.hauteur):
            return False
        if (i, j) == (x, y) or (i, j) in solides:
            return False
        glyphe = chantier.sol[j][i]
        return carte.marchable(glyphe) and not carte.LEGENDE[glyphe].get("cloture")

    voisines = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if marche(x + dx, y + dy)]
    if len(voisines) <= 1:
        return True
    fenetre = {(i, j) for j in range(y - 2, y + 3) for i in range(x - 2, x + 3) if marche(i, j)}
    vues = {voisines[0]}
    pile = [voisines[0]]
    while pile:
        i, j = pile.pop()
        for n in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if n in fenetre and n not in vues:
                vues.add(n)
                pile.append(n)
    return all(v in vues for v in voisines)


def _place_libre(chantier, x: int, y: int, solides: set[tuple[int, int]]) -> bool:
    if (x, y) in chantier.occupe or (x, y) in chantier.reserve:
        return False
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            # ⚠️ Ni devant une porte, ni JUSTE À CÔTÉ, ni collé à un autre meuble.
            if (x + dx, y + dy) in chantier.reserve or (x + dx, y + dy) in chantier.occupe:
                return False
    return _ne_coupe_rien(chantier, x, y, solides)


def semer(chantier, ville: dict, graine: int) -> dict[str, int]:
    """Plante les arbres, pose les bancs et les bacs à fleurs du bord des rues.
    Rend les comptes."""
    from . import carte

    des = carte.Des(graine ^ 0xA4B4E5)
    # ⚠️ Les bacs à fleurs tirent dans LEUR dé : tirés dans celui des arbres, ils
    # décalaient chaque bord qui suit, et les arbres des rues ordinaires
    # bougeaient d'un bout à l'autre de la ville sans que leur règle ait changé.
    des_bacs = carte.Des(graine ^ 0xBAC5)
    solides = {(d["x"], d["y"]) for d in chantier.decor if d["type"] in carte.DECOR_SOLIDE}
    poses = {"arbres": 0, "bancs": 0, "bacs": 0}
    for bord in _bords(chantier, ville):
        rythme = RYTHMES.get(bord["district"])
        if rythme is None:
            continue
        tuiles = bord["tuiles"]
        # Le tirage se fait pour CHAQUE bord, qu'on le plante ou non : un bord de
        # plus ou de moins ne décale pas le dé de tous ceux qui suivent.
        (pas_min, pas_max), part = ARBRES_PAR_STANDING.get(bord["standing"]) or rythme["arbres"]
        plante = des.chance(part)
        pas = des.entier(pas_min, pas_max)
        depart = des.entier(1, max(1, pas // 2))
        arbres: list[int] = []
        if plante:
            k = depart
            while k < len(tuiles) - 1:
                for essai in (k, k + 1, k - 1):
                    if not (0 < essai < len(tuiles) - 1):
                        continue
                    x, y = tuiles[essai]
                    if _place_libre(chantier, x, y, solides) and chantier.poser_decor("arbre", x, y):
                        solides.add((x, y))
                        arbres.append(essai)
                        poses["arbres"] += 1
                        break
                k += pas
        fiche_bancs = rythme["bancs"]
        if fiche_bancs is not None:
            (banc_min, banc_max), part_bancs = fiche_bancs
            assis = des.chance(part_bancs)
            pas_banc = des.entier(banc_min, banc_max)
            # ⚠️ Entre deux arbres, jamais dessous : un banc se met à l'ombre, pas
            # dans le tronc. On part du milieu du premier intervalle.
            k = (arbres[0] + (arbres[1] if len(arbres) > 1 else arbres[0] + pas)) // 2 if arbres else pas_banc // 2
            while assis and k < len(tuiles) - 1:
                for essai in (k, k + 1, k - 1, k + 2, k - 2):
                    if not (0 < essai < len(tuiles) - 1):
                        continue
                    x, y = tuiles[essai]
                    if _place_libre(chantier, x, y, solides) and chantier.poser_decor(BANCS_PAR_COTE[bord["cote"]], x, y):
                        solides.add((x, y))
                        poses["bancs"] += 1
                        break
                k += pas_banc
        if bord["standing"] != "cossu":
            continue
        # Les bacs à fleurs : au milieu d'un intervalle sur deux, entre les
        # arbres et les bouts du bord. Là où un banc a déjà pris l'ombre,
        # `_place_libre` refuse.
        reperes = [0, *arbres, len(tuiles) - 1]
        for a, b in zip(reperes, reperes[1:]):
            if not des_bacs.chance(PART_BAC_FLEURS):
                continue
            if b - a < 4:
                continue
            x, y = tuiles[(a + b) // 2]
            if _place_libre(chantier, x, y, solides) and chantier.poser_decor("bac_fleurs", x, y):
                solides.add((x, y))
                poses["bacs"] += 1
    return poses
