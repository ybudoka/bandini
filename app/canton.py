"""Le Petit-Canton, étape 2, vague B : l'arche et les lanternes (docs/jalons/le-quartier-chinois.md).

Martin (27 sept. 2026) : « un grand quartier bien défini » qu'on reconnaît d'un coup d'œil — son arche à
l'entrée, ses lanternes au-dessus de la rue. Posées sur la carte FINIE, par `nord.poser`, en tout dernier et
SANS UN DÉ : tout se calcule depuis la trame de la bande (`nord._bande()`), rien ne se tire.

⚠️ CE QUI PASSE AU-DESSUS DES GENS (le toit de l'arche, les cordes de lanternes) n'est pas du décor : un décor
est un sprite trié à son pied, et on passerait DEVANT un toit tendu en travers de la rue. Ça voyage sous la clé
`canton` et le navigateur le peint après les entités (`canton.js`). Seuls les deux PILIERS de l'arche sont du
décor (`pilier_arche`, solide) : on s'y cogne, en char comme à pied.
"""

from __future__ import annotations

from . import devantures

#: La colonne de la trame dont la rue ouest est la rue principale du Petit-Canton : entre ses 4e et 5e colonnes
#: d'îlots (`nord.DISTRICTS_NORD`, le plan du canton), c'est-à-dire la rue ouest de la colonne `bx + 4`.
COLONNE_DE_LA_RUE = 4
#: L'arche se tient à tant de rangées au nord de la couture : sur le trottoir, avant le passage piéton.
RECUL_DE_L_ARCHE = 2
#: Une corde de lanternes toutes les tant de rangées, le long de la rue principale.
PAS_DES_LANTERNES = 5
#: La paire d'idéogrammes du panneau de l'arche (`devantures.PAIRES`) : Zhongshan, le nom de mille rues.
PAIRE_DE_L_ARCHE = devantures.PAIRES.index("中山")


def rue_principale(ch, district: dict) -> tuple[int, int]:
    """(x du trottoir ouest, largeur) de la rue principale, lus dans la trame de la bande."""
    col = district["bx"] + COLONNE_DE_LA_RUE
    return ch.xr[col], ch.rues_v[col]


def poser(ville: dict, ch, district: dict, n: int) -> dict:
    """Pose les piliers de l'arche dans `ville["decor"]`, les lueurs des lanternes dans `ville["lampes"]`, et
    rend ce qui se peint au-dessus des gens : `{"arches": [...], "lanternes": [...]}`.

    ⚠️ Lève si une tuile n'est pas ce qu'on attend : un pilier sur autre chose qu'un trottoir libre, c'est que
    la trame a bougé — on le sait à la construction, pas en voyant une arche plantée dans un mur.
    """
    x0, large = rue_principale(ch, district)
    x1 = x0 + large - 1
    ya = n - RECUL_DE_L_ARCHE
    occupees = {(d["x"], d["y"]) for d in ville["decor"]}
    for x in (x0, x1):
        if ville["sol"][ya][x] != "." or (x, ya) in occupees:
            raise ValueError(f"canton : le pilier de l'arche ne se pose pas en {(x, ya)}")
        ville["decor"].append({"type": "pilier_arche", "x": x, "y": ya})
    arches = [{"x": x0, "y": ya, "l": large, "paire": PAIRE_DE_L_ARCHE}]

    # Les cordes : d'un trottoir à l'autre, au-dessus des rangées d'îlots seulement — jamais au-dessus d'un
    # croisement, où elles cacheraient les feux.
    lanternes = []
    for k, rangee in enumerate(ch.rangees):
        y0 = ch.yb[k]
        for y in range(y0 + 2, y0 + rangee - 1, PAS_DES_LANTERNES):
            if y >= ya - 1:
                continue
            lanternes.append({"x": x0, "y": y, "l": large})
            ville["lampes"].append({"x": x0 + large // 2, "y": y, "r": 34, "c": "lanterne"})
    # Les idéogrammes des plaques et du panneau de l'arche : avec la carte, qu'ils servent seuls à peindre.
    ideogrammes = {"glyphes": {k: list(v) for k, v in devantures.IDEOGRAMMES.items()},
                   "paires": list(devantures.PAIRES)}
    return {"arches": arches, "lanternes": lanternes, "ideogrammes": ideogrammes}
