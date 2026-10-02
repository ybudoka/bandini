"""Les territoires des gangs bougent (docs/jalons/les-territoires-des-gangs-bougent.md, vague 1).

Martin (29 sept. 2026) : **un coin par nuit** — chaque nuit, un gang plus fort que son voisin lui prend UN îlot à
la frontière ; **coucher ses membres** l'affaiblit (sa force remonte doucement) ; **il garde son cœur** — les
îlots de sa cour ne se prennent jamais par la frontière (pour ça, une mission : `libere`, M16).

Ce module dit la CARTE des territoires, telle que la ville la donne : les îlots de chaque district de la ville
d'avant, le gang qui les tient au départ, les îlots d'eau (on ne les prend pas), et le cœur de chaque gang (les
îlots de sa cour, le glyphe `g` du plan et ce qu'il a avalé). Le reste — la force, les îlots pris — vit dans la
PARTIE et se calcule dans le navigateur (`static/js/territoires.js`), sans un dé.

⚠️ **LA BANDE NORD A SA PROPRE TRAME** (vague 4, 2 oct. 2026) : ses rangées ne sont pas celles de la ville d'avant,
mais ses COLONNES le sont (`carte.COLONNES`). Seul le Petit-Canton y entre, avec les Mantes : ses îlots prennent des
rangées NÉGATIVES (−7 à −1, du nord au sud), si bien que sa rangée du bas touche celle du haut du Faubourg, colonne pour
colonne — la couture, face aux Cravates. Le navigateur reçoit la trame du nord (`nord`) pour y retrouver ses îlots. Le
cœur des Mantes, c'est le coin de leur école (`mantes.ZONE`) : elles n'ont pas de cour `g`. Les Friches et la Gare
(les Chevreuils et les Boulonneux du voisin du sud) restent hors du jeu : leurs gangs ne s'y étendent pas.
"""

from __future__ import annotations

from . import carte
from . import devantures, mantes, nord

#: Le district de la bande nord qui entre dans le jeu des territoires, et ses mots sur les murs. ⚠️ Pas dans
#: `devantures.TAGS_GANG` : la ville s'y sert pour cuire ses tags, et une clé de plus y changerait des murs.
DISTRICT_NORD = "canton"
TAGS_DES_MANTES: tuple[str, ...] = ("MANTES", "MNT")

#: Au plus trois tuiles de mur d'un seul tenant pour un tag (la règle de `Chantier.taguer`).
TAG_TUILES_MAX = 3

#: Les règles. `force` : la force d'un gang au départ et au plus haut ; `coup` : ce qu'un membre couché par le
#: joueur lui coûte ; `regain` : ce qu'il reprend par jour ; `marge` : de combien un gang doit dépasser son voisin
#: pour lui prendre un îlot (à égalité, rien ne bouge) ; `reprise` : combien de ses membres coucher dans un îlot
#: qu'il a PRIS, le même jour, pour le rendre au gang de son district (vague 2).
REGLES = {"force": 100, "coup": 4, "regain": 8, "marge": 15, "reprise": 4}

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
    # Le Petit-Canton et ses Mantes, dans la trame du nord : des rangées négatives, au-dessus du Faubourg.
    c, n = nord.district(DISTRICT_NORD), len(nord.RANGEES_NORD)
    districts.append({"slug": c["slug"], "gang": c["gang"], "bx": c["bx"], "by": c["by"] - n, "plan": list(c["plan"])})
    coeurs[c["gang"]] = [[c["bx"] + i, c["by"] + j - n] for j in range(*mantes.ZONE["rangees"])
                         for i in range(*mantes.ZONE["colonnes"])]
    return {"districts": districts, "coeurs": coeurs, "eau": sorted(PAS_UN_ILOT), "regles": dict(REGLES),
            "tags": tags_des_gangs(),
            "nord": {"rangees": list(nord.RANGEES_NORD), "rues_h": list(nord.RUES_H_NORD)}}


def tags_des_gangs() -> dict[str, list[list]]:
    """LES GRAFFITIS SUIVENT LA FRONTIÈRE (vague 3) : pour chaque gang, ses tags et le nombre de tuiles de mur
    qu'il faut à chacun (`[mot, tuiles]`). Le navigateur ne mesure pas un texte : il reçoit la place, calculée
    comme `Chantier.taguer` la calcule (`tient_en`, sans marge)."""
    sortie = {}
    for gang, mots in {**devantures.TAGS_GANG, "mantes": TAGS_DES_MANTES}.items():
        tailles = []
        for mot in mots:
            n = next((n for n in range(1, TAG_TUILES_MAX + 1) if devantures.tient_en(mot, n, carte.TUILE_PX, marge=0)),
                     None)
            if n is not None:
                tailles.append([mot, n])
        sortie[gang] = tailles
    return sortie
