"""Le train : une ligne de passage au rang 6 de la bande nord — au sol, sur le viaduc, dans le tunnel.

Martin (28 sept. 2026) : « je veux un vrai train aérien, terrestre et tunnel » (docs/jalons/le-train.md).

⚠️ **Python ne pose rien, le navigateur roule** — comme le tramway : ce module lit la ville FINIE et rend la
géométrie de la ligne ; pas une tuile, pas un décor, pas un dé. La ville est la même avec et sans lui
(`test_le_train_ne_deplace_rien`). Il passe AVANT les frénésies, qui doivent rester les dernières.
"""

from __future__ import annotations

#: Le rang de la voie, dans la carte finie : libre d'un bout à l'autre de la bande, sous le grand boulevard.
RANG = 6
#: Le viaduc, en tuiles, rampes comprises : il monte dans les Friches, enjambe le Petit-Canton, redescend à la gare.
VIADUC = (96, 284)
RAMPE = 12
#: Un pilier toutes les tant de tuiles, sur le tablier haut ; jamais sur une rue ni sur un trottoir.
PAS_PILIERS = 8
GARES = (("Les Friches", 50), ("Petit-Canton", 236), ("Gare centrale", 310))
#: px/image, px/image², images d'arrêt en gare, images d'attente à chaque bout (hors carte), longueur en tuiles,
#: et à combien de px devant sa tête un passage à niveau se ferme.
HORAIRE = {"vitesse": 4.5, "acceleration": 0.04, "arret": 600, "bout": 900, "longueur": 14, "annonce": 1100}


def _libre(ville, x):
    """Une tuile où planter un pilier : ni rue, ni trottoir."""
    return ville["voie"][RANG][x] == "." and ville["sol"][RANG][x] != "."


def _piliers(ville):
    haut0, haut1 = VIADUC[0] + RAMPE, VIADUC[1] - RAMPE
    piliers, x = [], haut0
    while x <= haut1:
        pris = next((p for p in range(x, min(x + 4, haut1 + 1)) if _libre(ville, p)), None)
        if pris is not None:
            piliers.append(pris)
        x += PAS_PILIERS
    return piliers


def _passages(ville, tunnel):
    rang, passages, x = ville["voie"][RANG], [], 0
    while x < tunnel:
        if rang[x] == ".":
            x += 1
            continue
        x0 = x
        while rang[x] != ".":
            x += 1
        if not VIADUC[0] <= x0 <= VIADUC[1]:
            passages.append([x0, x - 1])
    return passages


def poser(ville):
    # Le portail est dans la falaise de l'est ; sans montagnes (le juge du relief les retire), la voie sort au bord
    # de la carte.
    montagnes = (ville.get("relief") or {}).get("montagnes")
    tunnel = montagnes["x"] if montagnes else ville["largeur"]
    return {
        "rang": RANG, "tunnel": tunnel, "viaduc": list(VIADUC), "rampe": RAMPE,
        "piliers": _piliers(ville), "passages": _passages(ville, tunnel),
        "gares": [list(g) for g in GARES], "horaire": dict(HORAIRE),
    }
