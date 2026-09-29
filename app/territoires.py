"""Les territoires des gangs bougent (docs/jalons/les-territoires-des-gangs-bougent.md, vague 1).

Martin (29 sept. 2026) : **un coin par nuit** — chaque nuit, un gang plus fort que son voisin lui prend UN îlot à
la frontière ; **coucher ses membres** l'affaiblit (sa force remonte doucement) ; **il garde son cœur** — les
îlots de sa cour ne se prennent jamais par la frontière (pour ça, une mission : `libere`, M16).

Ce module dit la CARTE des territoires, telle que la ville la donne : les îlots de chaque district de la ville
d'avant, le gang qui les tient au départ, les îlots d'eau (on ne les prend pas), et le cœur de chaque gang (les
îlots de sa cour, le glyphe `g` du plan et ce qu'il a avalé). Le reste — la force, les îlots pris — vit dans la
PARTIE et se calcule dans le navigateur (`static/js/territoires.js`), sans un dé.

⚠️ **La bande nord n'en est pas** (les Friches, le Petit-Canton, la Gare) : son gang du Canton sera les Mantes
(l'école rivale) ; on l'ajoutera avec eux.
"""

from __future__ import annotations

from . import carte

#: Les règles. `force` : la force d'un gang au départ et au plus haut ; `coup` : ce qu'un membre couché par le
#: joueur lui coûte ; `regain` : ce qu'il reprend par jour ; `marge` : de combien un gang doit dépasser son voisin
#: pour lui prendre un îlot (à égalité, rien ne bouge).
REGLES = {"force": 100, "coup": 4, "regain": 8, "marge": 15}

#: Les îlots qu'on ne prend pas : l'eau.
PAS_UN_ILOT = frozenset("~")


def pour_le_navigateur() -> dict:
    """`districts` : pour chacun, son slug, son gang, son coin (`bx`, `by`) et son plan (une lettre par îlot) ;
    `coeurs` : pour chaque gang, les îlots de sa cour ; `regles`."""
    maitre = carte.regions_du_plan(carte.PLAN)
    districts, coeurs = [], {}
    for d in carte.DISTRICTS:
        if not d.get("gang"):
            continue
        districts.append({"slug": d["slug"], "gang": d["gang"], "bx": d["bx"], "by": d["by"], "plan": list(d["plan"])})
        for j, ligne in enumerate(d["plan"]):
            for i, _lettre in enumerate(ligne):
                b = (d["bx"] + i, d["by"] + j)
                mx, my = maitre[b]
                if carte.PLAN[my][mx] == "g":
                    coeurs.setdefault(d["gang"], []).append(list(b))
    return {"districts": districts, "coeurs": coeurs, "eau": sorted(PAS_UN_ILOT), "regles": dict(REGLES)}
