"""La tempête de neige et la charrue (M12).

M12, « La ville vit » : « Tempête de neige (risqué) : visibilité réduite, adhérence
divisée, charrue qui pousse la neige et les chars mal garés ; la police glisse aussi.
⚠️ La neige touche à la physique et au rendu : elle arrive derrière une option, et la
sonde de performance Playwright la mesure avant qu'elle soit allumée par défaut. »

⚠️ **Python règle, le navigateur neige.** Ce module ne pose rien dans la ville et ne
tire aucun dé : il dit QUAND il neige (une fonction du jour et de l'heure, la même d'une
partie à l'autre), ce que la neige fait aux chars, et la tournée de la charrue — une
boucle tracée avec la machinerie des autobus, comme celle des éboueurs.

⚠️ **Derrière une option** (`B.options.neige`, NON par défaut) : sans elle, pas un
flocon, pas un coefficient — le jeu est celui d'avant, octet pour octet.
"""

from __future__ import annotations

from . import autobus

#: Quand il neige. ⚠️ Une tempête tous les `tous_les` jours, à partir du jour `premier`
#: (jamais le premier soir d'une partie : on apprend la ville avant qu'elle glisse),
#: le soir de `debut_h` à `fin_h`, et elle monte et retombe en `montee_h`.
TEMPETE: dict = {
    "premier": 2,
    "tous_les": 3,
    "debut_h": 17.0,
    "fin_h": 23.5,
    "montee_h": 0.75,
}

#: Ce que la neige fait, à pleine tempête (la moitié à mi-montée).
EFFETS: dict = {
    "adherence": 0.3,            # l'adhérence d'un char sur la neige, en part de la sienne
    "adherence_deneigee": 0.75,  # derrière la charrue
    "frein": 0.5,                # et son freinage
    "vitesse_trafic": 0.65,      # le trafic lève le pied
    "voile": 0.22,               # le voile blanc sur l'écran (la visibilité)
    "flocons": 120,              # combien de flocons à l'écran
    "sol": 0.5,                  # l'opacité de la neige au sol
    "deneige_images": 3600,      # une tuile déneigée le reste tant d'images (trois heures de jeu)
}

#: La charrue : sa tournée passe par ces lieux garantis, et elle sort avec la tempête.
CHARRUE: dict = {
    "passe_par": ("terminus", "hopital", "usine", "garage"),
    "vitesse_px": 0.9,
    "largeur_tuiles": 1,         # de chaque côté de sa voie, ce qu'elle déneige
}


def _lieu(ville: dict, slug: str) -> tuple[int, int] | None:
    p = next((p for p in ville["points_interet"] if p.get("slug") == slug), None)
    return (p["x"], p["y"]) if p else None


def tracer_charrue(ville: dict) -> dict | None:
    """La tournée de la charrue : une boucle d'autobus par ses lieux, ou None."""
    reseau = autobus._Reseau(ville)
    lieux = [_lieu(ville, s) for s in CHARRUE["passe_par"]]
    if not all(lieux):
        return None
    voies = [(x, y) for y in range(reseau.hauteur) for x in range(reseau.largeur)
             if reseau.longe_le_trottoir(x, y) and (x, y) not in reseau.boites and (x, y) not in reseau.interdites]
    etapes = [sorted(voies, key=lambda t, c=c: (abs(t[0] - c[0]) + abs(t[1] - c[1]), t))[:autobus.ESSAIS_PAR_ETAPE]
              for c in lieux]
    construite = autobus._boucle(reseau, etapes)
    if construite is None:
        return None
    return {"trace": autobus.coins(construite[0])}


def tracer(ville: dict) -> dict:
    """Ce que le paquet transporte : l'horaire des tempêtes, leurs effets, la charrue."""
    charrue = tracer_charrue(ville)
    return {"tempete": dict(TEMPETE), "effets": dict(EFFETS),
            "charrue": ({**charrue, **{k: v for k, v in CHARRUE.items() if k != "passe_par"}} if charrue else None)}
