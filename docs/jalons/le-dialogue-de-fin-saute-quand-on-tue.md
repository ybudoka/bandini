# Le dialogue de fin sauté quand on tue

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (8 oct. 2026) : « quand on termine une mission en tuant un personnage, l'écran saute
jusqu'à la fin du dialogue ». La fin de mission se gagne sur le coup qui tue, et la scène de
fin (ou ses répliques) part d'un coup jusqu'au bout : on ne l'entend pas. FRAPPE ne passe
plus de réplique depuis le 30 sept. 2026 (`Histoire.majCinema`) : c'est donc un autre chemin
— une réplique dite par celui qu'on vient de tuer, un autre bouton, ou la mort qui ferme la
scène. À faire : rejouer au banc une mission qui finit sur un `tuer`, trouver le chemin, le
juger, le fermer.

## Notes

**La racine : la secousse du dernier coup, figée avec la ville** (8 oct. 2026). Ce n'était ni un bouton ni une
réplique sautée : chaque coup du joueur secoue la caméra (`Combat`, `B.cam.secousse` à 0,5 ou 0,9 ; une explosion,
1,2), et la secousse ne retombait (× 0,9 par image) que dans `Monde.majCamera`, qui ne tourne qu'avec la ville. Le
coup qui couche le dernier homme gagne la mission dans la même image, la scène de fin fige la ville (`Jeu.maj` ne
fait plus tourner qu'elle)… et la secousse restait à 0,9 : `Jeu.rendre` tirait la vue au hasard de ±3,6 px à chaque
image, jusqu'à la dernière réplique. L'écran « sautait » jusqu'à la fin du dialogue. Une fin gagnée au calme
(`retourner`) ne secouait rien : c'est pour ça que seules les fins « en tuant » sautaient. Même chose sous un
dialogue qui fige la ville à pied (un `pendant`, un appel) juste après un coup.

- Rejoué au banc : q13 (_La nuit des Morues_, finit sur le bosco), FRAPPE martelée au clavier puis à la manette —
  la vue bouge sur 851 images sur 852 de la scène de fin.
- Le correctif : `Monde.amortirSecousse()` (le même × 0,9) tourne aussi sous une scène et sous un dialogue qui
  fige la ville (`Jeu.maj`). La secousse retombe en une demi-seconde, comme en ville.
- Le juge : `tests/test_l_ecran_ne_tremble_pas_sous_un_dialogue_js.py` espionne la vue que `rendre` passe à
  `Monde.dessinerSol` ; sans le correctif, 812 images sur 852 (scène) et 226 sur 266 (dialogue) bougent après la
  retombée.
- Éliminé en chemin (aucun ne saute une réplique) : FRAPPE et la manette (standard et `mapping: ''`) pendant la
  scène, la mort plutôt que le K.-O., le pistolet, trois étoiles à la victoire, la victoire au volant ; les 6
  missions qui finissent sur un `tuer` et ~60 étapes `tuer` du catalogue (chapitres compris) rejouées au banc ;
  les 6 fins rejouées dans Chromium avec leurs vraies voix — chaque réplique dure sa voix.
- Pas touché : un fondu de porte, un menu et la pause figent aussi la ville sans amortir la secousse (un coup
  juste avant d'entrer ou d'ouvrir un comptoir tremble sous le fondu ou le menu) — même remède si Martin le voit.
