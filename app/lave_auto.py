"""Le lave-auto qu'on traverse, en vitre (docs/jalons/le-lave-auto-qu-on-traverse.md).

Martin, 30 sept. 2026 : « le lave auto doit etre comme le garage mais en vitre, on doit passer dedans, se faire
laver et ressortir de l'autre coté ». Le lave-auto devient un TUNNEL VITRÉ qui traverse son bâtiment, de la rue à la
ruelle : deux colonnes du bâtiment, de la façade à sa dernière rangée de toit. On paie au rideau vitré, un convoyeur
tire le char (`static/js/enseignes.js`), et on ressort dans la ruelle, une étoile de moins.

⚠️ **SUR LA VILLE FINIE, SANS UN DÉ, ET SANS UNE TUILE** : le toit du tunnel reste un toit — solide pour tout le
monde, la patrouille bute devant — et le navigateur l'ouvre au seul char du lavage (`Enseignes.tunnelOuvert`, comme
le seuil d'un rideau de garage). Ce module ne fait que DÉCIDER : où est le tunnel (`ville["lave_auto"]`), et ce qui
reste au bureau des piétons (la vitrine de sa porte rognée, sa pièce redessinée à sa nouvelle mesure).

⚠️ **RIEN NE S'ENLÈVE** : un décor retiré décalerait les identifiants de tout ce qui naît ensuite. Le tunnel exige un
passage déjà libre devant l'entrée et derrière la sortie ; s'il n'y en a pas, pas de tunnel (le bureau reste, son
comptoir aussi), et rien ne plante.
"""

from __future__ import annotations

from . import carte

#: Le tunnel : deux tuiles de large (une auto en fait une, l'autobus deux) ; de 3 à 8 rangées de bâtiment, façade
#: comprise (l'autobus fait trois rangées ; au-delà de huit, le convoyeur s'éternise).
LARGEUR = 2
PROFONDEUR_MIN, PROFONDEUR_MAX = 3, 8
#: Derrière la sortie, du roulable jusqu'à la ruelle (`x`), au plus tant de rangées ; devant l'entrée, tant de rangées
#: roulables (le trottoir, puis la chaussée).
DERRIERE_MAX, DEVANT = 4, 2
#: Le plus petit bureau qui reste (la largeur de plancher d'un commerce, `enseignes.MESURES_MIN`).
BUREAU_MIN = 4


def _roulable(g: str) -> bool:
    return carte.LEGENDE.get(g, {}).get("solide", 0) == 0 and not carte.LEGENDE.get(g, {}).get("eau")


def tunnel(sol, decors: set[tuple[int, int]], porte: dict) -> dict | None:
    """Le tunnel d'une porte de commerce, ou None : `{x, l, entree, sortie, vitrine}` — `entree` la rangée de la
    façade, `sortie` la dernière rangée de toit, `vitrine` ce qui reste au bureau. Lit `sol[y][x]` (les lignes de la
    ville finie, ou celles du chantier) et les tuiles où un décor est posé. Sans un dé : la même ville, le même tunnel."""
    x0, large = porte["vitrine"]
    y = porte["y"]
    hauteur, largeur = len(sol), len(sol[0])
    candidats = []
    for cx in (x0, x0 + large - LARGEUR):
        cols = range(cx, cx + LARGEUR)
        if any(x == porte["x"] or not (0 <= x < largeur) or sol[y][x] not in "WF" for x in cols):
            continue
        # Le toit du MÊME bâtiment, au-dessus de la façade : la même couverture, d'un seul tenant.
        toit = sol[y - 1][cx]
        if _roulable(toit) or any(sol[y - 1][x] != toit for x in cols):
            continue
        d = 0
        while y - 1 - d >= 0 and all(sol[y - 1 - d][x] == toit for x in cols):
            d += 1
        if not PROFONDEUR_MIN <= d + 1 <= PROFONDEUR_MAX:
            continue
        sortie = y - d
        # Derrière : du roulable jusqu'à la ruelle, sans rien de posé.
        derriere, ok = [], False
        for k in range(1, DERRIERE_MAX + 1):
            yy = sortie - k
            if yy < 0 or not all(_roulable(sol[yy][x]) for x in cols):
                break
            derriere.extend((x, yy) for x in cols)
            if all(sol[yy][x] == "x" for x in cols):
                ok = True
                break
        if not ok:
            continue
        # Devant : le trottoir et la chaussée, sans rien de posé.
        devant = [(x, y + k) for k in range(1, DEVANT + 1) for x in cols]
        if any(yy >= hauteur or not _roulable(sol[yy][x]) for x, yy in devant):
            continue
        if any(t in decors for t in derriere + devant):
            continue
        # Le bureau : ce qui reste de la vitrine, la porte des piétons dedans.
        reste = (x0 + LARGEUR, large - LARGEUR) if cx == x0 else (x0, large - LARGEUR)
        if reste[1] < BUREAU_MIN or not reste[0] <= porte["x"] < reste[0] + reste[1]:
            continue
        candidats.append(((-reste[1], -abs(cx + 0.5 - porte["x"]), cx),
                          {"x": cx, "l": LARGEUR, "entree": y, "sortie": sortie, "vitrine": list(reste)}))
    return min(candidats, key=lambda c: c[0])[1] if candidats else None


def poser(ville: dict) -> dict | None:
    """Pose le tunnel du lave-auto sur la ville finie : `ville["lave_auto"]`, la vitrine de la porte rognée, et la pièce
    du bureau redessinée à la mesure de ce qui lui reste. Rend le tunnel, ou None (pas de lave-auto, ou pas de passage)."""
    from . import enseignes

    porte = next((p for p in ville["portes"] if p.get("lieu") == "lave_auto"), None)
    ville["lave_auto"] = None
    if not porte or "lave_auto" not in ville["interieurs"]:
        return None
    decors = {(d["x"], d["y"]) for d in ville.get("decor", [])}
    t = tunnel(ville["sol"], decors, porte)
    if not t:
        return None
    vieille = ville["interieurs"]["lave_auto"]
    decale = LARGEUR if t["x"] == porte["vitrine"][0] else 0
    ville["interieurs"]["lave_auto"] = enseignes.piece_de_lave_auto(
        vieille["largeur"] - 2 - LARGEUR, vieille["hauteur"] - 2, vieille["sortie"]["x"] - decale)
    porte["vitrine"] = t["vitrine"]
    ville["lave_auto"] = {k: t[k] for k in ("x", "l", "entree", "sortie")}
    return ville["lave_auto"]
