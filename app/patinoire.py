"""La patinoire du parc (P4, docs/jalons/la-patinoire-du-parc.md).

Demande de Martin (30 sept. 2026) : « l'hiver, mets une patinoire dans un parc avec des gens qui
patinent ». Une patinoire extérieure à bandes, à la québécoise, dans le parc du Faubourg : l'hiver,
tant que la neige tient, la glace, ses bandes et ses deux filets ; l'été, une clairière de gazon.

Ici ne se choisit que sa PLACE : un rectangle de gazon et d'allée dans le parc, et les portes de ses
bandes. Tout le reste (la glace, les bandes, les patineurs, la glisse) vit dans le navigateur
(`static/js/patinoire.js`), peint et sans rien poser.

⚠️ **LE PARC N'A PAS LA PLACE** : 29 arbres semés partout, et le plus grand coin libre fait six tuiles
sur six. On taille donc une CLAIRIÈRE, à la toute fin (après les statues, avant la bande nord) et
**sans un dé** : le choix se fait au moindre coût, dans l'ordre de lecture ; le décor qui s'y trouve
(des arbres, des buissons, des bancs) se DÉPLACE sur la pelouse voisine, **à sa place dans la liste** —
jamais retiré : un décor de moins renumérote tout ce qui le suit (`Entites.creerDecor`), et avec lui
tout ce qui se tire à l'empreinte d'un numéro.

⚠️ **AUCUNE TUILE NE CHANGE** : la glace est une couche peinte. Le sol reste du gazon (`,`) et de la
poussière de pierre (`g`) ; les juges de circulation et de connexité ne voient pas de patinoire.
"""

from __future__ import annotations

#: Le parc qui la reçoit : le plus grand parc de ville, celui du Faubourg.
DISTRICT = "faubourg"

#: Les mesures essayées, de la plus grande à la plus petite (largeur, hauteur, en tuiles) : la
#: première qui trouve sa place l'emporte.
MESURES: tuple[tuple[int, int], ...] = ((14, 6), (14, 5), (13, 5), (12, 5), (12, 4))

#: Le sol sur lequel la glace peut se poser : le gazon et l'allée de poussière de pierre.
SOLS = frozenset({",", "g"})

#: Ce qui peut se déplacer pour lui faire de la place. Le reste (une statue, un belvédère, un banc
#: qui regarde la rue) arrête la fenêtre.
DEPLACABLES = frozenset({"arbre", "buisson", "banc"})

#: Ce que coûte chaque tuile d'allée couverte : une allée coupée se contourne, mais on la préfère
#: libre. Un décor déplacé coûte 1.
COUT_D_ALLEE = 0.25

#: Jusqu'où un décor déplacé cherche sa nouvelle place (en tuiles).
PORTEE = 10

#: Les couches qui prennent une tuile pour elles (la même liste que les statues).
COUCHES_PRISES = ("paquets", "scenes", "ambulants", "reclames", "points_interet")

#: Les quatre côtés : (nom, dx, dy) vers l'extérieur.
COTES = (("nord", 0, -1), ("sud", 0, 1), ("ouest", -1, 0), ("est", 1, 0))

#: Au plus deux portes dans les bandes.
PORTES_MAX = 2


def _parc(chantier) -> tuple[int, int, int, int] | None:
    for x, y, largeur, hauteur, district in chantier.parcs_de_ville:
        if district == DISTRICT:
            return x, y, largeur, hauteur
    return None


def _fenetres(chantier, ville: dict, parc, largeur: int, hauteur: int, decor: dict, pris: set):
    """Les fenêtres possibles de cette mesure dans le parc, (coût, x, y), de la moins chère à la plus chère
    puis dans l'ordre de lecture. Pure."""
    px, py, pl, ph = parc
    toutes = []
    for y in range(py, py + ph - hauteur + 1):
        for x in range(px, px + pl - largeur + 1):
            cout, ok = 0.0, True
            for j in range(y - 1, y + hauteur + 1):
                for i in range(x - 1, x + largeur + 1):
                    dedans = x <= i < x + largeur and y <= j < y + hauteur
                    d = decor.get((i, j))
                    if not dedans:
                        if not (px <= i < px + pl and py <= j < py + ph):
                            continue            # le trottoir d'a cote : son mobilier ne gene pas
                        # ⚠️ Le tour des bandes reste praticable : ni une statue ni un belvédère collé
                        # contre (on ne passerait plus entre les deux), ni le devant d'une porte.
                        if d and d not in DEPLACABLES:
                            ok = False
                        continue
                    if ville["sol"][j][i] not in SOLS or (i, j) in pris or (i, j) in chantier.reserve:
                        ok = False
                    elif d:
                        if d not in DEPLACABLES:
                            ok = False
                        cout += 1
                    elif ville["sol"][j][i] == "g":
                        cout += COUT_D_ALLEE
                    if not ok:
                        break
                if not ok:
                    break
            if ok:
                toutes.append((cout, y, x))
    return [(cout, x, y) for cout, y, x in sorted(toutes)]


def _portes(ville: dict, x: int, y: int, largeur: int, hauteur: int) -> list[dict]:
    """Les portes des bandes : là où une allée ou un trottoir arrive contre elles, au milieu de chaque
    arrivée ; l'allée d'abord, puis le trottoir, puis l'ordre de lecture. Sans arrivée, une porte au
    milieu du côté sud."""
    arrivees = []
    for cote, dx, dy in COTES:
        if dx == 0:
            bord = [(i, y if dy < 0 else y + hauteur - 1) for i in range(x + 1, x + largeur - 1)]
        else:
            bord = [(x if dx < 0 else x + largeur - 1, j) for j in range(y + 1, y + hauteur - 1)]
        suite: list[tuple[int, int]] = []
        for i, j in bord + [(None, None)]:
            dehors = None if i is None else ville["sol"][j + dy][i + dx]
            if dehors in ("g", "."):
                suite.append((i, j))
                continue
            if suite:
                mi, mj = suite[len(suite) // 2]
                sorte = ville["sol"][mj + dy][mi + dx]
                arrivees.append((0 if sorte == "g" else 1, mj, mi, cote))
                suite = []
    arrivees.sort()
    portes = [{"x": i, "y": j, "cote": cote} for _, j, i, cote in arrivees[:PORTES_MAX]]
    return portes or [{"x": x + largeur // 2, "y": y + hauteur - 1, "cote": "sud"}]


def _deplacer(chantier, ville: dict, parc, zone: set, pris: set) -> int | None:
    """Le décor de la zone, sur la pelouse la plus proche du parc, à sa place dans la liste. Rend le
    nombre de décors déplacés — ou None si l'un d'eux ne trouve pas sa place : alors RIEN n'a bougé
    (on ne retire jamais un décor, et la fenêtre suivante essaiera)."""
    from . import carte, devants, mobilier

    px, py, pl, ph = parc
    solides = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE}
    occupe, pris_avant, faits = set(chantier.occupe), set(pris), []
    deplaces = 0
    for d in sorted((d for d in ville["decor"] if (d["x"], d["y"]) in zone), key=lambda d: (d["y"], d["x"])):
        x0, y0 = d["x"], d["y"]
        chantier.occupe.discard((x0, y0))
        solides.discard((x0, y0))
        cible = next(((x, y) for x, y in devants._anneaux(x0, y0, PORTEE)
                      if px <= x < px + pl and py <= y < py + ph
                      and ville["sol"][y][x] == ","
                      and (x, y) not in zone and (x, y) not in pris
                      and mobilier._place_libre(chantier, x, y, solides)), None)
        if cible is None:
            for fait in faits:
                fait[0]["x"], fait[0]["y"] = fait[1]
            chantier.occupe.clear()
            chantier.occupe.update(occupe)
            pris.clear()
            pris.update(pris_avant)
            return None
        faits.append((d, (x0, y0)))
        d["x"], d["y"] = cible
        chantier.occupe.add(cible)
        pris.add(cible)
        if d["type"] in carte.DECOR_SOLIDE:
            solides.add(cible)
        deplaces += 1
    return deplaces


def poser(chantier, ville: dict) -> dict | None:
    """La clairière de la patinoire au parc du Faubourg, et ses portes ; rend sa fiche, ou None (une
    ville sans ce parc). Sur la ville finie, sans un dé : seul le décor de la clairière bouge."""
    parc = _parc(chantier)
    if parc is None:
        return None
    decor = {(d["x"], d["y"]): d["type"] for d in ville["decor"]}
    pris = {(o["x"], o["y"]) for cle in COUCHES_PRISES for o in ville.get(cle) or []}
    px, py, pl, ph = parc
    for largeur, hauteur in MESURES:
        for _, x, y in _fenetres(chantier, ville, parc, largeur, hauteur, decor, pris):
            # ⚠️ La clairière ET le tour des bandes : un arbre planté contre une bande bouche le passage.
            zone = {(i, j) for j in range(max(py, y - 1), min(py + ph, y + hauteur + 1))
                    for i in range(max(px, x - 1), min(px + pl, x + largeur + 1))}
            deplaces = _deplacer(chantier, ville, parc, zone, pris)
            if deplaces is not None:
                return {"x": x, "y": y, "l": largeur, "h": hauteur,
                        "portes": _portes(ville, x, y, largeur, hauteur), "deplaces": deplaces}
    return None


#: Ce que le navigateur en fait (`static/js/patinoire.js`) : les couleurs, la glisse, la chute.
FICHE: dict = {
    "couleurs": {
        "glace": "#dfeef6", "rayure": "#c6dcea", "reflet": "#f4fbff",
        "bande": "#f2f1ea", "ombre": "#9aa6ad", "liseret": "#c8302a",
        "filet": "#d23b2e", "poteau": "#e8e8e8", "lampe": "#3b3f44",
    },
    # ⚠️ LA GLISSE : la vitesse voulue (celle que donnent les commandes) se rejoint PEU À PEU. `elan` est
    # la part de l'écart comblée à chaque image quand on pousse, `freinage` quand on lâche tout : petite,
    # c'est un arrêt qui prend du temps et un virage large. Les passants ont la leur, un peu plus sûre.
    "glisse": {
        "joueur": {"elan": 0.05, "freinage": 0.015},
        "pieton": {"elan": 0.07, "freinage": 0.03},
    },
    # ⚠️ LA CHUTE, sans un dé : courir sur la glace sans patins (ESQUIVE tenue) `images_de_course` de suite,
    # ou virer de plus de `virage_deg` lancé à plus de `vitesse_de_virage` px par image — on tombe
    # `images_au_sol` images, comme projeté (`auSol`).
    "chute": {"images_de_course": 50, "virage_deg": 110, "vitesse_de_virage": 1.1, "images_au_sol": 50},
    # Les lampadaires des quatre coins, le soir : leur lueur (rgb), sa force et son rayon en px.
    "lampes": {"lueur": [255, 236, 190], "force": 0.55, "rayon": 58},
}


def pour_le_navigateur() -> dict:
    return FICHE
