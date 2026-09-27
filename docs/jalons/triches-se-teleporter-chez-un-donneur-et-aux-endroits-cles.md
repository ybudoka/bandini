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
cabane à sucre). Juge dans `tests/test_debug_js.py`.

## Notes

**Livré le 27 sept. 2026.** Deux lignes de plus sous ALLER, dans l'onglet TRICHES :

- **CHEZ UN DONNEUR** (`Hud.menuChezUnDonneur`) — chaque personnage qui a une adresse (`ou`), dans
  l'ordre du catalogue ; le Clairon et « le client », sans adresse, n'y sont pas. MISSION à droite
  quand il en a une à donner (`Histoire.disponibleDe`), et son titre dans l'aide du bas, sous le
  curseur : il ne tenait pas à côté des noms longs (le Bonimenteur). On y va par
  `allerChezLeDonneur`, le même chemin que le saut de mission, sans `Histoire.demarrer`. ⚠️ Un
  personnage PARTI après sa mission (`parti_apres` : Ti-Guy après M1, Bérubé après m99) est grisé
  (PARTI) : aller le voir le reposerait en ville pour de bon.
- **ENDROITS CLÉS** (`Hud.menuEndroitsCles`) — les 27 points de la carte, sous les titres de la
  légende dans son ordre (`carte.familles`, `parRang`). ⚠️ La liste se lit sur la carte de la
  **ville** (`carteDeLaVille`) : dans une pièce, `Monde.carte` est la pièce, qui a ses propres
  `points`. On se pose sur la tuile sous la porte (le point lui-même), tourné vers elle ; ACTION
  l'ouvre. ⚠️ Le trottoir d'abord, la chaussée à défaut : la porte de la fourrière donne droit sur
  l'asphalte de sa cour, sans trottoir à trois tuiles — le juge l'a trouvé. L'aérogare, cachée
  tant que le pont n'est pas fini (`Monde.masquee`), est grisée (CACHÉ).

Juges : six dans `tests/test_debug_js.py` (catalogue, chaque donneur sans mission lancée, ordre de
la légende, chaque endroit dont la porte s'ouvre à ACTION, sortir du char et de la pièce, rien
pendant une scène). Mutations : lancer la mission, lire la carte de la pièce, ne pas sortir de la
pièce, laisser un parti actif — chacune fait rougir un juge. Hors champ : la foire, le traversier,
les mouillages et les blocs de carte (chalet, cabane à sucre) ne sont pas des points de la carte ;
les donneurs de la foire, de Sven et de Bérubé s'atteignent par CHEZ UN DONNEUR.
