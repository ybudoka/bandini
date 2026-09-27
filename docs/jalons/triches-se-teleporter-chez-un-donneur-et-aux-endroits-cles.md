# Triches : se téléporter chez un donneur et aux endroits clés

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (27 sept. 2026) : « avec la triche je veux pouvoir me téléporter chez les
donneurs et endroits clé ». SAUT VERS UNE MISSION pose déjà chez le donneur, mais LANCE la
mission. Deux sous-pages de plus dans la section ALLER de l'onglet TRICHES. CHEZ UN
DONNEUR : le catalogue `B.defs.personnages` (un personnage ajouté y tombe seul), sa
prochaine mission disponible à droite, `allerChezLeDonneur` réutilisé tel quel (on sort du
char et de la pièce sans fondu, posé à côté de lui, dans sa pièce s'il est dedans) — aucune
mission ne part. ENDROITS CLÉS : les points de la carte (les blips de la mini-carte), rangés
par famille dans l'ordre de la légende ; posé sur le trottoir devant la porte, tourné vers
elle ; un lieu que la carte cache encore est grisé. Hors champ : les blocs de carte (chalet,
cabane à sucre). Juge dans `tests/test_classeur_js.py`.
