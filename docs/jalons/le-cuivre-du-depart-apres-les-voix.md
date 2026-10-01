# Le cuivre du départ après les voix

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (1er oct. 2026) :_ « quand une mission démarre il y a un son, mais souvent un autre texte du
donneur juste après. il faudrait t'assurer que le son soit à la fin de tous les audios ».

Le coup de cuivre du départ (`Son.SFX.mission`) part dans `Histoire.annoncer`, à la fin de l'intro — mais la réplique
`pendant` du premier objectif ne se dit qu'APRÈS (`B.mission.pendant`, à l'image suivante), et la voix de la dernière
réplique de l'intro peut encore jouer. Le cuivre tombe donc au milieu de ce que dit le donneur.

**Ce qu'on veut** : le cuivre du départ sonne quand plus personne ne parle — après l'intro, après la réplique
`pendant` du premier objectif, après la dernière voix. Une seule fois, et jamais perdu (une voix qui ne finit pas ne
le retient pas indéfiniment).

**Juges** : le cuivre sonne après la dernière réplique du départ, une seule fois ; il attend qu'une voix finisse ; il
ne reste pas pris si la voix ne finit jamais.

## Notes

Livré le 1er oct. 2026.

- `Histoire.annoncer` (la fin de l'intro) et `commencer` (un départ sans intro) n'ARMENT plus que le cuivre
  (`B.mission.cuivre`) ; `majCuivre`, dans `Histoire.maj`, le sonne quand tout le monde s'est tu. Il est placé APRÈS
  la réplique `pendant` en attente : à cet endroit, pas de scène (le jeu ne passe pas dans `maj`), pas de réplique à
  l'écran (`majCinema` en sort), pas de `pendant` (dite juste au-dessus). Il ne reste qu'à attendre la **voix** : une
  qui joue (`Son.Voix.enCours`) ou qui se charge encore (`attendue`) — si elle a un mp3 (`Voix.histoire`) ; une
  réplique sans fichier reste « attendue » pour toujours et ne retient rien.
- **Jamais retenu pour toujours** : au bout de 900 images (15 s), il sonne quand même — la même borne que celle qui
  retient une réplique sur sa voix (`majCinema`).
- Le titre et l'objectif s'affichent toujours tout de suite ; seul le son attend. Les défis (le panneau, la foire)
  gardent leur cuivre immédiat : personne ne parle après.
- **Juges** : `test_cuivre_du_depart_js.py` (e02 : Ti-Paul finit son intro puis dit « Douce, douce! », le cuivre sonne
  après, une fois ; il attend une voix, pas plus de 15 s, et pas une réplique sans mp3). Mutations : le cuivre
  immédiat d'avant, l'attente de la voix, la borne, le filtre des mp3, le désarmement — toutes mordues. Trois gardes
  écrites d'abord (scène, réplique à l'écran, `pendant` en attente) ne mordaient pas : `maj` les tient déjà, elles
  sont retirées.
