"""La pluie de Baie-des-Brumes (docs/jalons/les-quatre-saisons-realistes.md, lot 2, 29 sept. 2026).

Au printemps et à l'automne, des averses ; l'été, des orages le soir ; jamais l'hiver (il neige). La rue
mouillée glisse comme derrière l'arroseuse, des flaques éclaboussent, la fonte d'avril laisse de la
gadoue, et en octobre les chars soulèvent les feuilles mortes.

⚠️ **PYTHON RÈGLE, LE NAVIGATEUR MOUILLE** — la recette du brouillard (`brouillard.py`) : un jour a sa
pluie à l'empreinte du jour (`hash2(jour, sel)`), pas au tirage ; son heure et sa durée aussi. Rien à
simuler, aucun dé, et deux joueurs ont la même averse le même après-midi.

⚠️ **POUR TOUT LE MONDE**, sans option (Martin, 29 sept. 2026 : la saison remplace l'option de la neige,
et la pluie suit la même règle). Au sec, rien ne change : l'adhérence est multipliée par 1.

⚠️ **RIEN NE SE POSE** : les flaques, la gadoue et les feuilles sont des couches PEINTES (à l'empreinte de
la tuile) ou des particules bornées — la ville ne bouge pas d'un octet.
"""

from __future__ import annotations

#: Les averses du printemps et de l'automne : une chance par jour, à l'empreinte du jour ; l'heure où
#: elle commence et sa durée, tirées du même jour dans ces bornes (heures). `montee_h` : le temps
#: qu'elle met à prendre toute sa force, et à retomber.
AVERSES = {"chance": 0.5, "sel": 0x9A1E, "debut_h": [6.0, 16.0], "duree_h": [2.0, 7.0], "montee_h": 0.4}

#: Les orages de l'été : plus rares, le soir, courts et violents.
ORAGES = {"chance": 0.34, "sel": 0x0A6E, "debut_h": [16.5, 20.0], "duree_h": [1.0, 3.0], "montee_h": 0.2}

#: Ce que fait la pluie.
EFFETS = {
    #: La rue mouillée : comme derrière l'arroseuse (`nuit.ARROSEUSE`), pendant l'averse puis en séchant.
    "adherence": 0.8,
    "frein": 0.85,
    #: Combien d'heures la rue met à sécher après la pluie ; les flaques, elles, durent plus longtemps.
    "seche_h": 1.0,
    "flaques_h": 3.0,
    #: Le trafic lève un peu le pied sous la pluie.
    "vitesse_trafic": 0.9,
    #: À l'écran : des traits de pluie (combien, au plein), et le voile gris.
    "gouttes": 150,
    "gouttes_orage": 280,
    "voile": 0.10,
    "voile_orage": 0.2,
    #: L'orage : un éclair toutes les tant de secondes (en moyenne), le flash en images, et le tonnerre
    #: qui suit après un délai (en images) — l'orage n'est pas au-dessus de la tête.
    "eclair_s": 9,
    "eclair_images": 5,
    "tonnerre_apres": [40, 110],
    #: Les flaques : une tuile de rue ou de trottoir sur `part`, à l'empreinte de la tuile.
    "flaques": {"part": 0.035, "sel": 0xF1A9, "vitesse_min": 1.2, "repit_images": 40, "rayon_passant_px": 30},
    #: Les feuilles d'octobre, mouillées, glissent un peu plus que l'asphalte ; un char en soulève une
    #: toutes les `feuilles_images` images au-dessus de `feuilles_vitesse`.
    "feuilles_adherence": 0.75,
    "feuilles_images": 4,
    "feuilles_vitesse": 1.5,
    #: La fonte d'avril (avril commence au jour 11) : de la gadoue au bord des rues et sur les trottoirs (jours
#: de l'année), une tuile
    #: sur `part`, qui glisse un peu.
    "gadoue": {"jours": [11.0, 13.5], "part": 0.22, "sel": 0x6AD0, "adherence": 0.9},
}

#: Ce que dit un passant qu'un char vient d'éclabousser.
ECLABOUSSES = ["HEILLE!", "MON MANTEAU!", "WÔ LÀ!", "MERCI BEN!", "T'AURAIS PU RALENTIR!"]


def pour_le_navigateur() -> dict:
    return {"averses": dict(AVERSES), "orages": dict(ORAGES),
            "effets": {**EFFETS, "flaques": dict(EFFETS["flaques"]), "gadoue": dict(EFFETS["gadoue"])},
            "eclabousses": list(ECLABOUSSES)}
