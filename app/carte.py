"""La carte de Baie-des-Brumes — servie au navigateur, testee ici.

⚠️ M0 : un TERRAIN D'ESSAI genere par une petite fonction, pour marcher et
brancher les commandes. Le vrai Faubourg (plan de blocs + gabarits de
batiments + generateur deterministe) arrive au jalon M1, avec la MEME forme de
sortie : le navigateur n'aura rien a changer.

Forme servie (`exporter()`) :
    largeur, hauteur           en tuiles
    sol                        lignes de glyphes (LEGENDE)
    voie                       lignes de direction routiere : . aucune, > < ^ v, + croisement, S arret
    legende                    glyphe -> proprietes (solide, route, trottoir, eau, ...)
    portes, lampes, decor      listes de positions en tuiles
    zones                      rectangles nommes (district, territoire de gang)
    points_interet             lieux nommes (planque, hopital, poste, magasins, proprietes)
    apparition                 ou le joueur commence
    interieurs                 petites cartes, meme forme, par slug
"""

from __future__ import annotations

TUILE_PX = 16

#: Solidite : 0 libre, 1 mur (bloque tout), 2 eau (bloque sauf les bateaux),
#: 3 basse (bloque les vehicules, pas les pietons).
LEGENDE: dict[str, dict] = {
    ".": {"nom": "trottoir", "trottoir": True},
    "#": {"nom": "asphalte", "route": True},
    "-": {"nom": "ligne de voie", "route": True},
    "+": {"nom": "ligne centrale", "route": True},
    "=": {"nom": "passage pieton", "route": True, "trottoir": True},
    ",": {"nom": "herbe", "herbe": True},
    "s": {"nom": "sable"},
    "~": {"nom": "eau", "solide": 2},
    "Q": {"nom": "quai"},
    "p": {"nom": "stationnement", "route": True, "stationnement": True},
    "R": {"nom": "rampe", "route": True, "rampe": True},
    "B": {"nom": "toit", "solide": 1},
    "F": {"nom": "façade", "solide": 1},
    "W": {"nom": "vitrine", "solide": 1, "lampe": True},
    "D": {"nom": "porte", "solide": 1, "porte": True},
    "G": {"nom": "porte de garage", "solide": 1, "garage": True},
    "b": {"nom": "borne", "solide": 3},
    "f": {"nom": "clôture", "solide": 3},
    "x": {"nom": "ruelle"},
    "t": {"nom": "plancher"},
    "c": {"nom": "comptoir", "solide": 3},
}

VOIES = {".", ">", "<", "^", "v", "+", "S"}


def _terrain_essai(largeur: int = 60, hauteur: int = 34) -> dict:
    """Une prairie, une rue en boucle a deux voies, quatre batiments, des arbres."""
    sol = [[","] * largeur for _ in range(hauteur)]
    voie = [["."] * largeur for _ in range(hauteur)]

    # Boucle routiere : rue de 6 tuiles (trottoir, 2 voies, 2 voies, trottoir).
    # Circulation a droite : sur la rue du haut on roule vers l'ouest sur les
    # deux voies nord, vers l'est sur les deux voies sud ; sur les rues
    # verticales, vers le sud a l'ouest et vers le nord a l'est.
    x0, x1, y0, y1 = 6, largeur - 7, 5, hauteur - 6
    bandes_h = (y0, y1 - 5)
    bandes_v = (x0, x1 - 5)

    # 1. Les trottoirs : la bande entiere.
    for by in bandes_h:
        for dy in range(6):
            for x in range(x0, x1 + 1):
                sol[by + dy][x] = "."
    for bx in bandes_v:
        for dx in range(6):
            for y in range(y0, y1 + 1):
                sol[y][bx + dx] = "."

    # 2. Les chaussees (4 tuiles) et leur sens.
    for by in bandes_h:
        for x in range(x0 + 1, x1):
            for dy in range(1, 5):
                sol[by + dy][x] = "+" if (dy == 3 and x % 4 < 2) else "#"
                voie[by + dy][x] = "<" if dy <= 2 else ">"
    for bx in bandes_v:
        for y in range(y0 + 1, y1):
            for dx in range(1, 5):
                sol[y][bx + dx] = "+" if (dx == 3 and y % 4 < 2) else "#"
                voie[y][bx + dx] = "v" if dx <= 2 else "^"

    # 3. Les croisements : chaussee nue, sens libre.
    for by in bandes_h:
        for bx in bandes_v:
            for dy in range(1, 5):
                for dx in range(1, 5):
                    sol[by + dy][bx + dx] = "#"
                    voie[by + dy][bx + dx] = "+"

    # Quatre batiments dans le bloc central, facade vers le sud.
    def batiment(bx, by, bw, bh, porte=True):
        for y in range(by, by + bh):
            for x in range(bx, bx + bw):
                sol[y][x] = "B"
        for x in range(bx, bx + bw):
            sol[by + bh - 1][x] = "W" if x % 3 == 1 else "F"
        if porte:
            sol[by + bh - 1][bx + bw // 2] = "D"
        # Un trottoir devant, sans jamais ecraser une route.
        for x in range(bx - 1, bx + bw + 1):
            if 0 <= x < largeur and sol[by + bh][x] == ",":
                sol[by + bh][x] = "."

    batiment(16, 12, 8, 6)
    batiment(28, 12, 10, 6)
    batiment(42, 12, 7, 6)
    batiment(20, 19, 12, 3, porte=False)

    # Arbres et lampadaires (decor : entites triees par y).
    decor = []
    for x in range(8, largeur - 8, 9):
        decor.append({"type": "arbre", "x": x, "y": 2})
        decor.append({"type": "arbre", "x": x + 4, "y": hauteur - 3})
    lampes = []
    for x in range(x0, x1, 8):
        lampes.append({"x": x, "y": y0})
        lampes.append({"x": x, "y": y1})
        decor.append({"type": "lampadaire", "x": x, "y": y0})
        decor.append({"type": "lampadaire", "x": x, "y": y1})

    portes = [{"x": 16 + 4, "y": 17, "interieur": "armurerie", "lieu": "armurerie"},
              {"x": 28 + 5, "y": 17, "interieur": "garage", "lieu": "garage"},
              {"x": 42 + 3, "y": 17, "interieur": "planque", "lieu": "planque"}]

    return {
        "slug": "terrain_essai",
        "nom": "Terrain d'essai",
        "largeur": largeur,
        "hauteur": hauteur,
        "tuile_px": TUILE_PX,
        "sol": ["".join(ligne) for ligne in sol],
        "voie": ["".join(ligne) for ligne in voie],
        "portes": portes,
        "lampes": lampes,
        "decor": decor,
        "zones": [{"slug": "faubourg", "nom": "Le Faubourg", "x": 0, "y": 0,
                   "l": largeur, "h": hauteur, "pietons": 24, "vehicules": 8,
                   "police": 1}],
        "points_interet": [{"type": p["lieu"], "slug": p["lieu"], "x": p["x"],
                            "y": p["y"] + 1} for p in portes],
        "apparition": {"joueur": {"x": 30, "y": 22}},
        "interieurs": {},
    }


def exporter() -> dict:
    carte = _terrain_essai()
    carte["legende"] = LEGENDE
    return carte


# --- Outils de verification (utilises par les tests) ------------------------


def solidite(glyphe: str) -> int:
    return int(LEGENDE.get(glyphe, {}).get("solide", 0))


def marchable(glyphe: str) -> bool:
    return solidite(glyphe) in (0, 3)


def routier(glyphe: str) -> bool:
    return bool(LEGENDE.get(glyphe, {}).get("route"))


def composantes_marchables(carte: dict) -> list[set[tuple[int, int]]]:
    """Les groupes de tuiles marchables reliees entre elles (4-connexite)."""
    sol = carte["sol"]
    vues: set[tuple[int, int]] = set()
    groupes = []
    for y, ligne in enumerate(sol):
        for x, g in enumerate(ligne):
            if not marchable(g) or (x, y) in vues:
                continue
            groupe = set()
            pile = [(x, y)]
            while pile:
                cx, cy = pile.pop()
                if (cx, cy) in groupe:
                    continue
                if not (0 <= cy < len(sol) and 0 <= cx < len(sol[cy])):
                    continue
                if not marchable(sol[cy][cx]):
                    continue
                groupe.add((cx, cy))
                pile.extend(((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)))
            vues |= groupe
            groupes.append(groupe)
    return groupes


def suivre_voie(carte: dict, x: int, y: int) -> list[tuple[int, int]]:
    """Les tuiles ou peut aller un vehicule qui suit les fleches depuis (x, y)."""
    voie = carte["voie"]
    h, w = len(voie), len(voie[0])
    fleche = voie[y][x]
    pas = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}
    if fleche in pas:
        dx, dy = pas[fleche]
        candidats = [(x + dx, y + dy)]
    elif fleche == "+":
        candidats = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    else:
        return []
    return [(cx, cy) for cx, cy in candidats
            if 0 <= cy < h and 0 <= cx < w and voie[cy][cx] in VOIES - {"."}]
