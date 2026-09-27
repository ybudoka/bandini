# Triches : un onglet classé, et la foire, le traversier et les blocs dans ENDROITS CLÉS

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Suite de « Triches : se téléporter chez un donneur et aux endroits clés ». Martin (27 sept.
2026) : oui à la foire, au traversier et au chalet dans ENDROITS CLÉS, et « classe bien le
menu de triche, il commence à y avoir beaucoup de menus ». Il a choisi des sections par
intention sur une seule page : LE JOUEUR (argent, santé, items, techniques), TOUJOURS (les
bascules OUI/NON), ALLER (À L'OBJECTIF, CHEZ UN DONNEUR, ENDROITS CLÉS — rien ne se lance),
JOUER (LANCER UNE MISSION, LANCER UN DÉFI, OBJECTIF SUIVANT, TERMINER LA MISSION), DIVERS
(coop, jukebox) ; « ... » à droite des lignes qui ouvrent une page. ENDROITS CLÉS gagne
l'arche de la foire (REPÈRES), les deux quais du traversier (TRANSPORT) et une section HORS
DE LA VILLE : les portes des blocs de carte (le chalet et la cabane à sucre au rang, les
Galeries), et l'arrivée d'un bloc sans porte (le ciné-parc) ; la carte du bloc se charge au
noir, comme le réveil au chalet (`Blocs.reprendre`).

## Notes

**Livré le 27 sept. 2026.**

- **L'onglet TRICHES, classé par intention** (`Hud.menuDebug`) — LE JOUEUR (argent, santé, items,
  techniques), TOUJOURS (les cinq bascules OUI/NON), ALLER (À L'OBJECTIF, CHEZ UN DONNEUR, ENDROITS
  CLÉS : on y va, rien ne se lance), JOUER (LANCER UNE MISSION, LANCER UN DÉFI, OBJECTIF SUIVANT,
  TERMINER LA MISSION : on y va ET ça part), DIVERS (coop, jukebox). Une ligne qui ouvre une page
  porte « ... » à droite (`page()`), aucune autre. Renommés : SAUT VERS UNE MISSION → LANCER UNE
  MISSION, SAUT VERS UN DÉFI → LANCER UN DÉFI, TÉLÉPORTER À L'OBJECTIF → À L'OBJECTIF (la section
  ALLER le dit déjà). Les fonctions gardent leur nom (`menuSautMissions`, `menuSautDefis`).
- **ENDROITS CLÉS gagne** l'arche de la foire sous REPÈRES (`Histoire.resoudre('foire')` — ⚠️
  `Histoire.lieu` ne la connaît pas), les deux quais du traversier sous TRANSPORT
  (`Traversier.donnees().escales`), et une section **HORS DE LA VILLE** : une ligne par porte de
  bloc de carte (le chalet du rang, la cabane à sucre, les Galeries), et l'arrivée d'un bloc sans
  porte (le ciné-parc). ⚠️ Le menu connaît ces portes sans charger la carte du bloc : le paquet
  des blocs (`blocs.pour_le_navigateur`) porte maintenant leurs `portes` (x, y, nom de la pièce).
- **`Blocs.sauter(slug, ici, apres)`** — le réveil au chalet (`Blocs.reprendre`) généralisé : au
  noir, le noir tient le temps que la carte arrive, puis on est à `ici` dans le bloc (à son
  arrivée sans `ici`). `reprendre` passe maintenant par lui. Le retour se fait au passage du
  bloc (`recul` borne la position le long du bord, d'où qu'on vienne en ville).
- La foire et le traversier ne se listent qu'en ville : ils se lisent sur `Monde.carte`, qui est
  la pièce ou le bloc quand on y est.

Juges (`tests/test_debug_js.py`) : l'onglet et ses cinq sections, chaque « ... » ouvre la page de
son nom ; la foire et les deux quais ; chaque porte de bloc se rejoint et s'ouvre à ACTION, le
ciné-parc à son arrivée, et un endroit de la ville nous ramène. Mutations : bloc posé à
l'arrivée au lieu de la porte, foire retirée, « ... » effacé, jukebox sans « ... » — chacune fait
rougir un juge.
