"""Des maisons vraiment de luxe (docs/jalons/des-etages-pour-vrai-des-maisons-de-luxe-et-des-terrains-clotures.md,
vague 3). Martin, 30 sept. 2026 : « je veux pouvoir avoir plusieurs étages et aussi des maisons vraiment de luxe ».

Une VILLA, c'est un cossu des Érables qui a de la place : la maison s'ÉLARGIT sur la pelouse libre de ses côtés
(le toit et la façade avancent d'autant), monte sur tout son toit, et sa cour avant se ferme d'une haie de cèdres
taillée, ouverte au sentier. La façade — la pierre grise, le portique à colonnes, les fenêtres cintrées, la
balustrade — se peint dans le navigateur (`r.villa`, `sprites.js`).

⚠️ **POSÉES EN TOUT DERNIER, SUR LA VILLE FINIE, SANS UN DÉ**, juste avant les clôtures (qui ferment les cours sur
la ville aux villas) : la ville d'avant est la même à la tuile près, hors des villas. On n'élargit QUE sur de
l'herbe libre — ni décor, ni paquet, ni scène, ni réclame —, en gardant une colonne de pelouse entre la villa et
ce qui la borde ; la haie ne passe jamais devant une porte ni sur le sentier.
"""

from __future__ import annotations

from . import clotures

#: Le quartier des villas (les cossus de banlieue : les grands terrains).
QUARTIER = "erables"

#: La haie de cèdres (`carte.LEGENDE`, le jardin de la villa du maire) : taillée, elle ne se traverse pas.
HAIE = "`"

#: Une maison devient villa si elle atteint tant de tuiles de large, en s'élargissant d'au plus `COTE_MAX` par
#: côté, et jamais au-delà de `LARGE_MAX`.
LARGE_MIN = 6
COTE_MAX = 3
LARGE_MAX = 8

#: Une villa a un toit d'au moins tant de rangées (le toit qui porte ses étages).
TOIT_MIN = 2

#: Le jardin (vague 4) : la piscine creusée (`carte.LEGENDE`), la fontaine et les deux piliers du portail (des décors
#: posés sur la ville finie : ils prennent leurs numéros d'entité À PART, `horsSuite` dans `sprites.js`).
PISCINE = "?"
FONTAINE = "fontaine_villa"
PILIER_OUEST, PILIER_EST = "pilier_portail_o", "pilier_portail_e"
#: Une piscine se creuse si la cour avant a tant de rangées (elle en prend deux, contre la haie).
PISCINE_RANGEES_MIN = 3

#: Ses étages, rez compris (le navigateur n'en peint jamais plus que son toit n'en porte).
ETAGES = 3


def _toit(sol: list[list[str]], r: dict) -> int:
    """Combien de rangées de toit à deux versants, au-dessus de TOUTE la façade."""
    n = 0
    while r["y"] - 1 - n >= 0 and all(sol[r["y"] - 1 - n][x] == "P" for x in range(r["x"], r["x"] + r["l"])):
        n += 1
    return n


def _jardin(sol: list[list[str]], r: dict, x0: int, x1: int, fond: int, herbe) -> list[dict]:
    """LE JARDIN DE LA VILLA (vague 4) : le PORTAIL — deux piliers de pierre, leur battant de fer ouvert, de part
    et d'autre du sentier, dans la haie ; la PISCINE CREUSÉE, sur les deux rangées contre la haie, du côté de la
    porte qui a le plus de place (quand la cour en a trois) ; la FONTAINE au milieu de l'autre côté. Change `sol`
    (la piscine, et l'herbe sous les piliers) ; rend ce qui s'est posé (`type`, `x`, `y` ; la piscine : une entrée
    par tuile)."""
    poses: list[dict] = []
    porte = r["x"] + r["porte"]
    # Le portail : là où le sentier traverse la haie.
    if sol[fond][porte] == "." and sol[fond][porte - 1] == HAIE and sol[fond][porte + 1] == HAIE:
        for x, type_ in ((porte - 1, PILIER_OUEST), (porte + 1, PILIER_EST)):
            sol[fond][x] = ","
            poses.append({"type": type_, "x": x, "y": fond})
    rangees = list(range(r["y"] + 1, fond))
    cotes = sorted(([x for x in range(x0, porte)], [x for x in range(porte + 1, x1 + 1)]), key=lambda c: -len(c))
    # La piscine : du côté le plus large, au bout (loin du sentier), sur les deux rangées du fond de la cour.
    large, etroit = cotes
    piscine = False
    if len(rangees) >= PISCINE_RANGEES_MIN and len(large) >= 3:
        largeur = 3 if len(large) >= 4 else 2
        xs = large[-largeur:] if large[0] > porte else large[:largeur]
        tuiles = [(x, y) for x in xs for y in rangees[-2:]]
        if all(herbe(x, y) for x, y in tuiles):
            piscine = True
            for x, y in tuiles:
                sol[y][x] = PISCINE
                poses.append({"type": PISCINE, "x": x, "y": y})
    # La fontaine : au milieu de l'autre côté (ou du plus large, s'il n'a pas de piscine), sur la rangée du milieu —
    # jamais dans la colonne qui longe le sentier (elle se collait au pilier du portail).
    fy = rangees[len(rangees) // 2]
    for cote in (etroit, [] if piscine else large):
        cote = [x for x in cote if abs(x - porte) >= 2]
        if cote and herbe(cote[len(cote) // 2], fy):
            poses.append({"type": FONTAINE, "x": cote[len(cote) // 2], "y": fy})
            break
    return poses


def poser(ville: dict) -> list[dict]:
    """Élargit les villas et ferme leur cour d'une haie. Rend la liste des villas (`x`, `y`, `l`, `avant`). Change
    `ville["sol"]` et, pour chaque villa, sa résidence (`x`, `l`, `motifs`, `porte`, `etages`, `villa`)."""
    sol = [list(r) for r in ville["sol"]]
    h = len(sol)
    enceintes, _ = clotures.chantiers(ville)
    occ = clotures._occupees(ville) | enceintes
    district = clotures._district(ville)
    portes = {(x, y) for y, r in enumerate(sol) for x, g in enumerate(r) if g in "DdG"}
    posees: list[dict] = []
    decor = ville.setdefault("decor", [])

    def herbe(x: int, y: int) -> bool:
        return 0 <= y < h and 0 <= x < len(sol[y]) and sol[y][x] == "," and (x, y) not in occ

    for r in sorted(ville.get("residences") or [], key=lambda q: (q["y"], q["x"])):
        if r.get("standing") != "+" or r.get("declin") is not None or district(r["x"], r["y"]) != QUARTIER:
            continue
        if any((r["x"] + i, r["y"] - j) in enceintes for i in range(r["l"]) for j in range(4)):
            continue
        toit = _toit(sol, r)
        if toit < TOIT_MIN:
            continue
        rangees = range(r["y"] - toit, r["y"] + 1)

        def libre(x: int) -> bool:
            return all(herbe(x, y) for y in rangees)

        # De chaque côté : les colonnes d'herbe libre du haut du toit à la façade, moins UNE (la marge).
        gauche = 0
        while gauche <= COTE_MAX and libre(r["x"] - 1 - gauche):
            gauche += 1
        droite = 0
        while droite <= COTE_MAX and libre(r["x"] + r["l"] + droite):
            droite += 1
        gauche, droite = max(0, min(COTE_MAX, gauche - 1)), max(0, min(COTE_MAX, droite - 1))
        while r["l"] + gauche + droite > LARGE_MAX:
            if droite >= gauche:
                droite -= 1
            else:
                gauche -= 1
        if r["l"] + gauche + droite < LARGE_MIN:
            continue
        x0, x1 = r["x"] - gauche, r["x"] + r["l"] - 1 + droite
        for y in rangees:
            for x in list(range(x0, r["x"])) + list(range(r["x"] + r["l"], x1 + 1)):
                sol[y][x] = "F" if y == r["y"] else "P"
        avant = dict(r)
        r["motifs"] = "F" * gauche + (r.get("motifs") or "F" * r["l"]) + "F" * droite
        r["porte"] = r["porte"] + gauche
        r["x"], r["l"] = x0, x1 - x0 + 1
        r["etages"] = ETAGES
        r["villa"] = True
        r["escalier"] = None                              # ni escalier de fer : un portique

        # LA HAIE : sur la dernière rangée d'herbe devant la villa (et sa marge), puis de chaque côté jusqu'à la
        # façade — ouverte au sentier et à l'entrée de voiture, jamais devant une porte.
        # La cour avant s'arrête à la première rangée qui n'est plus de l'herbe pour moitié (l'abord, le trottoir —
        # le sentier et l'entrée de voiture la traversent).
        fond = r["y"]
        while fond + 1 < h and 2 * sum(sol[fond + 1][x] == "," for x in range(x0, x1 + 1)) > x1 - x0 + 1:
            fond += 1
        if fond - r["y"] < 2:
            posees.append({"x": r["x"], "y": r["y"], "l": r["l"], "avant": avant})
            continue
        haie = [(x, fond) for x in range(x0 - 1, x1 + 2)]
        haie += [(x, y) for x in (x0 - 1, x1 + 1) for y in range(r["y"] + 1, fond)]
        # ⚠️ Jamais devant une porte : du côté où la villa ne s'est pas élargie, le retour longe le voisin mitoyen,
        # et sa porte peut être juste là (la ville du témoin n'a pas le cas : le juge ne peut pas le faire rougir).
        for x, y in haie:
            if herbe(x, y) and (x, y - 1) not in portes:
                sol[y][x] = HAIE
        jardin = _jardin(sol, r, x0, x1, fond, herbe)
        for d in jardin:
            occ.add((d["x"], d["y"]))
        decor.extend(d for d in jardin if d["type"] != PISCINE)
        posees.append({"x": r["x"], "y": r["y"], "l": r["l"], "avant": avant, "jardin": jardin})
    ville["sol"] = ["".join(r) for r in sol]
    return posees
