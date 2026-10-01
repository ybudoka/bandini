"""La tempête de verglas (docs/jalons/la-tempete-de-verglas.md).

Un événement rare et mémorable : trois jours de glace, des quartiers entiers au noir, et la ville qui
change de règles le temps que ça fonde.

⚠️ **PYTHON RÈGLE, LE NAVIGATEUR GIVRE** — la même règle que la neige de M12 (`neige.py`) et que le
brouillard (`brouillard.py`). Tout est une fonction du JOUR et de l'HEURE (`Verglas.intensiteA`,
`Verglas.quartiersNoirsA`) : rien à simuler, aucun dé, et deux joueurs ont la même tempête le même
jour. Les quartiers au noir se tirent à l'EMPREINTE de la tempête et du jour, pas au tirage.

⚠️ **POUR TOUT LE MONDE, LES DERNIERS JOURS DE MARS** (les quatre saisons, lot 6, vague 6b — Martin,
29 sept. 2026) : l'option « VERGLAS (ESSAI) » a disparu, comme celle de la neige. Hors de ses jours,
l'intensité vaut 0, et 0 ne change rien — l'adhérence est multipliée par 1, la police voit comme avant,
les lampes brillent, rien ne se peint. Ces soirs-là, la pluie verglaçante prend la place de la tempête de
neige (`Neige.intensiteA`).
"""

from __future__ import annotations

#: Quand. ⚠️ Trois jours de suite au jour `premier`, puis tous les `tous_les` jours : les trois derniers
#: jours de mars (8, 9 et 10 de l'année, `calendrier.MOIS`), chaque année du jeu. La pluie verglaçante prend dans la nuit du
#: premier jour (pleine à `arrive_h`) ; la glace fond le soir du dernier (de `fond_h` à minuit).
TEMPETE = {
    "premier": 8,
    "jours": 3,
    "tous_les": 40,
    "arrive_h": 3.0,
    "fond_h": 18.0,
    "sel": 0x61ACE,
}

#: Ce que fait la glace, à son plein.
EFFETS = {
    #: L'adhérence d'un char sur la glace, et son freinage, en part des siens.
    "adherence": 0.4,
    "frein": 0.55,
    #: Le trafic lève le pied.
    "vitesse_trafic": 0.7,
    #: La police débordée : sa vue, en part de sa portée ; ses renforts et ses dépêches, plus lents.
    "vision_police": 0.6,
    "retard_police": 1.6,
    #: Dans un quartier au noir, la nuit est plus noire de tant (l'opacité du voile de nuit).
    "nuit_noire": 0.14,
    #: Le reflet bleuté de la glace sur toute la ville, et le vernis de la chaussée (plus franc : un
    #: voile clair sur du gris ne se voit presque pas).
    "reflet": 0.07,
    "vernis": 0.30,
    #: Une tuile de chaussée sur tant scintille ; une tuile de trottoir sur tant porte une branche.
    "eclats_une_sur": 5,
    "branches_une_sur": 9,
}

#: Le noir : les quartiers qui peuvent perdre le courant, et combien le perdent chaque jour de la
#: tempête (le premier, le pire, le dernier).
PANNES = {
    "quartiers": ["faubourg", "erables", "quais", "shop", "pointe", "ile"],
    "par_jour": [2, 3, 2],
}

#: Ce que le Clairon écrit : la veille, puis chaque matin de tempête (`{quartiers}` : leurs noms).
CLAIRON = {
    "veille": "PLUIE VERGLAÇANTE DEMAIN : HYDRO-BAIE PRÉVOIT TROIS JOURS DIFFICILES.",
    "pendant": "VERGLAS : PAS DE COURANT DANS {quartiers}.",
}


def pour_le_navigateur() -> dict:
    return {"tempete": dict(TEMPETE), "effets": dict(EFFETS),
            "pannes": {"quartiers": list(PANNES["quartiers"]), "par_jour": list(PANNES["par_jour"])},
            "clairon": dict(CLAIRON)}
