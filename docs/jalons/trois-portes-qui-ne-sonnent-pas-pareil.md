# Trois portes qui ne sonnent pas pareil

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« change le bruit de porte et différencie le bruit de porte de maison,
commerce et véhicule ; moto et vélo ont pas de portes ») : un seul grincement de bois
servait au logement, au dépanneur, au taxi — et à la descente d'un vélo. Trois échantillons
ElevenLabs à la place : `porte_maison` (la clé dans la serrure, le bois qui claque dans une
cage d'escalier), `porte_commerce` (la vitre, le ferme-porte qui siffle), `porte_vehicule`
(la portière qui claque).

- ⚠️ **Le genre vient de la fiche, pas du JS** : chaque pièce de `carte._piece` dit quelle
  porte on pousse (champ `porte`, « maison » pour les logements, la planque, la chambre
  d'hôtel et le phare, « commerce » ailleurs) et chaque char dit s'il a des portières
  (`vehicules.portieres`, vrai pour les classes auto et camion seulement).
  `Son.SFX.porte(genre)` choisit ; `Jeu.entrer`, `sortir` et `changerEtage` lisent la pièce,
  `vehicules.js` lit le char. Une moto et un vélo **s'enfourchent** : le cliquetis de
  `ramasse` à la montée comme à la descente, comme le vélo le faisait déjà à la montée. Le
  crochet de la remorqueuse et le client du taxi claquent une portière. Le filet synthétisé
  suit : un repli par porte (bois grave, tôle). Juges : chaque pièce a un genre de porte
  connu, chaque char dit ses portières, et un banc JS pousse la planque, le dépanneur, un
  logement, puis monte et descend d'une auto, d'un camion, d'une moto et d'un vélo en
  écoutant quel genre sort. Poids : 551 → **577 Ko** pour 34 fichiers, il reste 23 Ko sous
  le plafond de 600.
- ⚠️ Écoutée par Martin : la porte de commerce est **renvoyée**. Refaite deux fois. La
  première reprise (sans le ferme-porte « qui siffle ») est sortie : 0,67 s, **−12 dB**
  au-dessus de 2 kHz là où la sonnette de vélo tient son pic — et le juge de l'aigu l'a
  refusée : c'est la mesure qui a tenu lieu d'oreille. Deuxième reprise avec l **en tête du
  prompt** et la porte en second : trois candidats, tous à 1,48 s avec leur pic au-dessus de
  2 kHz, gardé le plus propre (RSB 71 dB, −2,6 dB au-dessus de 8 kHz). La portière, elle,
  est sortie à **0,34 s** (un seul claquement, sans le cliquetis de la poignée demandé) —
  Martin dira si elle se tient, `--refaire porte_vehicule` sinon
