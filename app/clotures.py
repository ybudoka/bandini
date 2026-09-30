"""Des terrains vraiment clôturés (docs/jalons/des-etages-pour-vrai-des-maisons-de-luxe-et-des-terrains-clotures.md,
vague 2). Martin, 30 sept. 2026 : « aussi des terrains vraiment clôturés ».

La cour avant d'un logement — l'herbe entre sa façade et le trottoir — se ferme : une clôture le long du trottoir, des
retours sur les côtés là où il n'y a pas de voisin mitoyen, et un portail ouvert devant la porte. Le fer forgé chez
les cossus (la grille de la référence : un muret, sa grille à pointes), la palissade de bois à l'ordinaire, le grillage
chez les pauvres. On les enjambe comme toutes les clôtures du jeu (`LEGENDE[...]["cloture"]`).

⚠️ **POSÉES EN TOUT DERNIER, SUR LA VILLE FINIE, SANS UN DÉ** : après la bande nord et les cartes de hockey — la
ville d'avant est la même à la tuile près, hors des clôtures. Une règle écrite choisit : une cour d'une seule
profondeur (deux rangées d'herbe au moins), jamais une tuile de décor, de paquet, de scène, de carte à ramasser ou de
frénésie, jamais devant une porte, et le portail toujours ouvert devant la porte du logement (le juge de connexité
le tient).
"""

from __future__ import annotations

from . import chantiers as chantiers_mod

#: Ce qui fait une cour (l'herbe, la friche) — jamais une allée, un trottoir ou une ruelle.
COUR = frozenset(",;")

#: La clôture de chaque standing (les glyphes de `carte.LEGENDE`). ⚠️ La palissade de bois est une image de BANLIEUE
#: (Martin, le juge `test_la_ville_porte_les_trois_clotures…`) : ailleurs, l'ordinaire a la grille de fer basse du
#: triplex de la référence (`CLOTURE_EN_VILLE`).
CLOTURE = {"+": "(", "=": "w", "-": "f"}
CLOTURE_EN_VILLE = {"+": "(", "=": "(", "-": "f"}
BANLIEUE = "erables"

#: Toutes les clôtures (celles de la ville et la grille de fer) : les deux règles de Martin les lisent ensemble.
TOUTES = frozenset("fwX(")

#: Une cour se ferme si elle a au moins tant de rangées d'herbe (sinon, la galerie touche le trottoir).
PROFONDEUR_MIN = 2

#: Un terrain s'etend de tant de tuiles au plus, de chaque cote de sa facade (jusqu'a mi-chemin du voisin).
COTE_MAX = 4

#: Les glyphes d'une façade (celle d'un voisin mitoyen ferme déjà le côté).
FACADE = frozenset("FWDdPG")


def chantiers(ville: dict) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    """Les tuiles des chantiers (leur enceinte) et de leurs annexes (l'équipe à ses postes, les machines, la
    tranchée, le signaleur, la benne) : posées AVANT, elles lisent la ville finie (`chantiers.completer`) — une
    villa ne pousse ni sur un bâtiment en chantier ni sur un poste de l'équipe."""
    enceintes: set[tuple[int, int]] = set()
    annexes: set[tuple[int, int]] = set()
    for c in ville.get("chantiers") or []:
        enceintes |= {(c["x"] + i, c["y"] + j) for i in range(c["l"]) for j in range(c["h"])}
        for ph in c.get("phases") or []:
            annexes |= {(x, y) for x, y in ph.get("equipe") or []}
            for m in ph.get("machines") or []:
                annexes.add((m["x"], m["y"]))
                if m.get("frappe"):
                    annexes.add(tuple(m["frappe"]))
        annexes |= {(x, y) for x, y in c.get("tranchee") or []}
        if c.get("signaleur"):
            annexes.add(tuple(c["signaleur"]))
        if c.get("conteneur"):                            # la benne, et tout son bloc
            bx, by = c["conteneur"]
            demi = chantiers_mod.CONTENEUR_LARGEUR // 2
            annexes |= {(bx + i, by + j) for i in range(-demi, demi + 1) for j in range(chantiers_mod.CONTENEUR_PROFONDEUR)}
    return enceintes, annexes


def _occupees(ville: dict) -> set[tuple[int, int]]:
    """Ce qu'on ne couvre jamais : le décor, les paquets, les ambulants, les scènes, les réclames — et les annexes
    des chantiers (`chantiers`)."""
    occ = {(d["x"], d["y"]) for d in ville.get("decor") or []}
    for cle in ("paquets", "ambulants", "scenes", "reclames"):
        occ |= {(q["x"], q["y"]) for q in ville.get(cle) or [] if "x" in q and "y" in q}
    return occ | chantiers(ville)[1]


def _district(ville: dict):
    zones = [z for z in ville.get("zones") or [] if z.get("district")]

    def qui(x: int, y: int) -> str | None:
        for z in zones:
            if z["x"] <= x < z["x"] + z["l"] and z["y"] <= y < z["y"] + z["h"]:
                return z["district"]
        return None
    return qui


def _elaguer(sol: list[list[str]], miennes: set[tuple[int, int]], avant: dict) -> None:
    """LES DEUX RÈGLES DE MARTIN, après coup : « une clôture tourne, ou elle n'est pas là » (une course sans coin
    part — seulement mes tuiles), et « une clôture fait une tuile d'épais » (pas de carré de 2 × 2 : la mienne part).
    `avant` : le glyphe d'avant de chaque tuile posée."""
    h = len(sol)

    def cloture(x, y):
        return 0 <= y < h and 0 <= x < len(sol[y]) and sol[y][x] in TOUTES

    def enlever(t):
        sol[t[1]][t[0]] = avant[t]
        miennes.discard(t)

    change = True
    while change:
        change = False
        for x, y in sorted(miennes):
            for ox, oy in ((0, 0), (-1, 0), (0, -1), (-1, -1)):
                if all(cloture(x + ox + i, y + oy + j) for i in (0, 1) for j in (0, 1)):
                    enlever((x, y))
                    change = True
                    break
        vus: set = set()
        for t in sorted(miennes):
            if t in vus:
                continue
            pile, course = [t], []
            vus.add(t)
            while pile:
                x, y = pile.pop()
                course.append((x, y))
                for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if q not in vus and cloture(*q):
                        vus.add(q)
                        pile.append(q)
            dedans = set(course)
            tourne = any(((x + 1, y) in dedans or (x - 1, y) in dedans) and ((x, y + 1) in dedans or (x, y - 1) in dedans)
                         for x, y in course)
            if not tourne:
                for q in course:
                    if q in miennes:
                        enlever(q)
                        change = True


def _voisin(x: int, y: int, colonnes: set, pas: int, sens: int) -> bool:
    """La facade d'un voisin est-elle a `pas` tuiles au plus au-dela de x, dans le sens `sens` ? (Chacun s'arrete a
    mi-chemin de l'herbe qui les separe.)"""
    return any((x + sens * k, y) in colonnes for k in range(1, pas + 1))


def poser(ville: dict) -> list[dict]:
    """Ferme les cours avant ; rend la liste des terrains clôturés (`x`, `y`, `l`, `profondeur`, `porte`,
    `cloture`). Change `ville["sol"]`."""
    sol = [list(r) for r in ville["sol"]]
    h = len(sol)
    occ = _occupees(ville)
    district = _district(ville)
    miennes: set[tuple[int, int]] = set()
    avant: dict = {}
    portes = {(x, y) for y, r in enumerate(sol) for x, g in enumerate(r) if g in "DdG"}
    posees: list[dict] = []

    def cour(x: int, y: int) -> bool:
        return 0 <= y < h and 0 <= x < len(sol[y]) and sol[y][x] in COUR and (x, y) not in occ

    #: Les tuiles deja dans un terrain (le suivant s'arrete devant : deux voisins se partagent l'herbe entre eux).
    prises: set[tuple[int, int]] = set()
    facades = sorted(ville.get("residences") or [], key=lambda q: (q["y"], q["x"]))
    colonnes_de_facade = {(x, q["y"]) for q in facades for x in range(q["x"], q["x"] + q["l"])}

    def libre(x: int, y0: int, y1: int) -> bool:
        """Toute la colonne x, de la rangee y0 a y1, est de l'herbe libre ?"""
        return all(cour(x, yy) and (x, yy) not in prises and (x, yy) not in colonnes_de_facade for yy in range(y0, y1 + 1))

    for r in facades:
        if r.get("declin") is not None:
            continue
        table = CLOTURE if district(r["x"], r["y"]) == BANLIEUE else CLOTURE_EN_VILLE
        g = table.get(r.get("standing") or "=")
        x0, x1, y = r["x"], r["x"] + r["l"] - 1, r["y"]
        # La profondeur de la cour, colonne par colonne : il la faut la meme partout.
        profondeurs = set()
        for x in range(x0, x1 + 1):
            d = 0
            while cour(x, y + 1 + d):
                d += 1
            profondeurs.add(d)
        if len(profondeurs) != 1:
            continue
        d = profondeurs.pop()
        if d < PROFONDEUR_MIN:
            continue
        rang = y + d                                         # la derniere rangee d'herbe, contre le trottoir
        # LE TERRAIN : la facade, et de chaque cote la cour de cote (de l'herbe de la facade au trottoir), jusqu'a
        # mi-chemin du voisin — `COTE_MAX` tuiles au plus.
        xa, xb = x0, x1
        while x0 - xa < COTE_MAX and libre(xa - 1, y, rang) and not _voisin(xa - 1, y, colonnes_de_facade, x0 - xa + 1, -1):
            xa -= 1
        while xb - x1 < COTE_MAX and libre(xb + 1, y, rang) and not _voisin(xb + 1, y, colonnes_de_facade, xb - x1 + 1, 1):
            xb += 1
        porte = r["x"] + r["porte"]
        tuiles = [(x, rang) for x in range(xa, xb + 1) if x != porte]
        if xa < x0:
            tuiles += [(xa, yy) for yy in range(y, rang)]            # le cote, du coin de la maison au trottoir
        elif xa - 1 >= 0 and sol[y][xa - 1] not in FACADE:
            tuiles += [(xa - 1, yy) for yy in range(y + 1, rang + 1) if cour(xa - 1, yy)]
        if xb > x1:
            tuiles += [(xb, yy) for yy in range(y, rang)]
        elif xb + 1 < len(sol[y]) and sol[y][xb + 1] not in FACADE:
            tuiles += [(xb + 1, yy) for yy in range(y + 1, rang + 1) if cour(xb + 1, yy)]
        tuiles = [(x, yy) for x, yy in tuiles if cour(x, yy) and (x, yy) not in prises and (x, yy - 1) not in portes]
        if not tuiles:
            continue
        for x in range(xa, xb + 1):
            for yy in range(y, rang + 1):
                prises.add((x, yy))
        for x, yy in tuiles:
            avant[(x, yy)] = sol[yy][x]
            sol[yy][x] = g
            miennes.add((x, yy))
        posees.append({"x": xa, "y": y, "l": xb - xa + 1, "profondeur": d, "porte": porte, "cloture": g})
    _elaguer(sol, miennes, avant)
    ville["sol"] = ["".join(r) for r in sol]
    return [p for p in posees if any((x, yy) in miennes for x in range(p["x"], p["x"] + p["l"])
                                     for yy in range(p["y"], p["y"] + p["profondeur"] + 1))]
