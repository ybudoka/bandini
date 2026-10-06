"""L'année de Baie-des-Brumes : quarante jours, douze mois, quatre saisons (26 sept. 2026).

Le jeu n'avait pas de saisons — la neige de M12 est une météo, pas un hiver. Or le plan en demande :
le pont de glace et la motoneige (l'hiver), la cabane à sucre (le printemps), la Saint-Jean et le
ciné-parc (l'été), le temps des Fêtes. Plutôt que d'inventer un cycle par idée, UNE année les tient
toutes : Martin a dit « fais tout le reste », et c'est la décision la plus simple qui les porte.

⚠️ **UNE PURE FONCTION DU JOUR** : `mois(jour)`, `saison(jour)`. Rien à sauvegarder, aucun dé, la même
année pour tout le monde. Le jour 1 de l'année est le premier janvier, mais une partie neuve commence
au jour `DEPART`, le 1er mai (Martin, 4 oct. 2026 : « le jeu doit débuter à un moment sans neige ») —
on apprend la ville avant qu'elle glisse. Une partie déjà commencée garde son jour.

⚠️ **SEULS LES JALONS QUI LA LISENT EN DÉPENDENT** : la neige ne tombe que l'hiver (depuis le
29 sept. 2026, pour tout le monde), la ville change de couleur avec elle (`saisons.py`) ; le verglas
tombe les trois derniers jours de mars (8 à 10), pour tout le monde (les saisons, lot 6, vague 6b).
"""

from __future__ import annotations

#: Combien de jours dans une année du jeu.
ANNEE = 40

#: Le jour de l'année où commence une partie neuve : le 1er mai, la neige fondue et la gadoue
#: d'avril partie (`pluie.EFFETS["gadoue"]`, jusqu'à 13,5). Un juge tient qu'il n'y neige pas.
DEPART = 14

#: Le premier jour de chaque mois, dans l'année (1 à 40) : trois ou quatre jours par mois.
MOIS = [
    ("janvier", 1), ("fevrier", 4), ("mars", 7), ("avril", 11), ("mai", 14), ("juin", 17),
    ("juillet", 21), ("aout", 24), ("septembre", 27), ("octobre", 31), ("novembre", 34), ("decembre", 37),
]

#: La saison de chaque mois.
SAISONS = {
    "decembre": "hiver", "janvier": "hiver", "fevrier": "hiver", "mars": "hiver",
    "avril": "printemps", "mai": "printemps",
    "juin": "ete", "juillet": "ete", "aout": "ete",
    "septembre": "automne", "octobre": "automne", "novembre": "automne",
}

#: Les dates qui comptent, en jour de l'année (1 à 40).
DATES = {
    "saint_jean": 20,        # le 24 juin, le dernier jour de juin
    "demenagement": 21,      # le 1er juillet
    "noel": 39,
    "halloween": 33,         # le 31 octobre, le dernier jour d'octobre (les quatre saisons, lot 3)
}


def jour_de_l_annee(jour: int) -> int:
    """Le jour d'une partie (1, 2, …) dans son année (1 à 40)."""
    return (jour - 1) % ANNEE + 1


def mois(jour: int) -> str:
    j = jour_de_l_annee(jour)
    nom = MOIS[0][0]
    for m, debut in MOIS:
        if j >= debut:
            nom = m
    return nom


def saison(jour: int) -> str:
    return SAISONS[mois(jour)]


def pour_le_navigateur() -> dict:
    return {"annee": ANNEE, "mois": [[m, d] for m, d in MOIS], "saisons": dict(SAISONS), "dates": dict(DATES), "depart": DEPART}
