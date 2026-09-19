"""Les incendies : un bâtiment brûle, un pompier volontaire l'éteint (P4).

« Quatre activités que le jeu n'a pas » — la deuxième : le pompier volontaire.
Au Québec, les pompiers d'un village sont des volontaires qu'on appelle chez
eux. Ici, pas de caserne ni de camion à dessiner : un feu se déclare sur une
façade, on y arrive (à pied ou en char), on l'éteint à l'extincteur avant que
la façade brûle — et c'est une prime, pas un salaire.

⚠️ Python décide, le navigateur brûle — exactement comme le bris d'aqueduc.
Ce module ne pose rien dans la ville et ne tire aucun dé du jeu : les façades
où un feu PEUT se déclarer viennent de la ville finie (`devantures`,
`residences`), et QUAND il se déclare est une fonction de l'heure — la même
d'une partie à l'autre, lue par `incendies.js` au fil des minutes.

⚠️ **Jamais n'importe quoi.** Un feu ne se déclare ni dans une cour de gang
(elle est intouchable), ni sur un lieu garanti (la planque, l'hôpital) : on ne
brûle pas ce qu'une mission protège, et un feu sur sa propre planque serait une
taxe, pas une activité.

⚠️ **Une prime, pas un palier.** Le feu se paie à l'heure, sous ce que rapporte
une mission (juge `test_incendies`) — sinon éteindre des feux devient le seul
boulot qui vaille, et la ville brûle tout le temps.
"""

from __future__ import annotations

from . import carte

#: Ce que le navigateur suit. `chance_par_heure` : la part des heures qui ont un
#: feu (tiré à l'empreinte de l'heure, jamais au dé) ; `minutes` : le temps qu'il
#: brûle avant de s'éteindre tout seul — c'est le chrono d'arrivée ; `rayon_px` :
#: à quelle distance du mur le jet d'extincteur attrape le feu ; `prime` : ce que
#: rapporte une intervention menée à bien.
REGLE: dict = {
    "chance_par_heure": 0.06,
    "minutes": 40,
    "rayon_px": 44,
    "prime": 80,
    "max_candidats": 14,     # assez de façades pour disperser, pas une ville en flammes
    "ecart_min": 12,         # deux feux ne se voisinent pas (en tuiles)
}


def _interdites(ville: dict) -> set[tuple[int, int]]:
    """Les tuiles où le feu ne se déclare pas : une cour de gang, un lieu garanti."""
    out: set[tuple[int, int]] = set()
    for z in ville.get("zones") or []:
        if not z.get("gang"):
            continue
        for ty in range(z["y"], z["y"] + z["h"]):
            for tx in range(z["x"], z["x"] + z["l"]):
                out.add((tx, ty))
    # Un lieu garanti (planque, hôpital, poste…) : son point, et le mur au-dessus.
    for p in ville.get("points_interet") or []:
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                out.add((p["x"] + dx, p["y"] + dy))
    return out


def _façades(ville: dict) -> list[dict]:
    """Une façade par tuile de mur qui donne sur de quoi se tenir. Le feu monte
    du mur, et le pompier doit pouvoir s'en approcher : il faut du marchable
    juste au sud du bandeau (la rue, le trottoir).

    ⚠️ Rien que de la GÉOMÉTRIE, et un genre. Pas de nom : celui d'une devanture
    change quand « les commerces montent et descendent » (`vitrines`), et cette
    table doit rester la même tuile pour tuile (`test_les_commerces_montent_sans_rien_deplacer`).
    Le navigateur résout le nom à la lecture, sur la ville servie.
    """
    sol = ville["sol"]
    fronts: list[dict] = []
    for d in ville.get("devantures") or []:
        for i in range(d["l"]):
            x, y = d["x"] + i, d["y"]
            if y + 1 >= len(sol) or not carte.marchable(sol[y + 1][x]):
                continue
            fronts.append({"x": x, "y": y, "genre": "commerce"})
    for r in ville.get("residences") or []:
        for i in range(r["l"]):
            x, y = r["x"] + i, r["y"]
            if y + 1 >= len(sol) or not carte.marchable(sol[y + 1][x]):
                continue
            fronts.append({"x": x, "y": y, "genre": "logement"})
    return fronts


def candidats(ville: dict) -> list[dict]:
    """Les façades où un feu peut se déclarer, dispersées.

    ⚠️ Dispersion par `ecart_min` : deux feux collés ne font pas deux incendies,
    ils font un bûcher. ⚠️ L'ordre est celui de la ville, déterministe — le
    navigateur choisit par empreinte de l'heure, jamais au dé du jeu.
    """
    interdites = _interdites(ville)
    gardes: list[dict] = []
    for f in _façades(ville):
        if (f["x"], f["y"]) in interdites:
            continue
        if any(max(abs(f["x"] - g["x"]), abs(f["y"] - g["y"])) < REGLE["ecart_min"]
               for g in gardes):
            continue
        gardes.append(f)
        if len(gardes) >= REGLE["max_candidats"]:
            break
    return gardes


def tracer(ville: dict) -> dict:
    """La table d'incendies de la ville : la règle, et les façades candidates.

    ⚠️ Aucun dé n'est tiré : les façades viennent de la ville, et c'est le
    navigateur qui choisit QUI brûle à l'empreinte de l'heure.
    """
    return {"regle": dict(REGLE), "facades": candidats(ville)}