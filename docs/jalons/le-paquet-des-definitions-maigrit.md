# Le paquet des définitions maigrit

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé le 29 sept. 2026 : le plafond de `test_le_paquet_reste_leger` a été relevé presque chaque jour
(60 → 62 → 64 → 67 Ko gzip, 270 → 300 Ko bruts), et chaque relève écrivait « le remède reste celui d'en
haut »._ Mesure du jour : 296 109 octets bruts, 66 090 gzip.

_Ce que ça donne :_ le paquet que le téléphone télécharge au démarrage (`/api/definitions`) perd ce qu'il
n'a pas besoin de lire pour ouvrir le menu, et ses plafonds **redescendent**.

**Première cure : les notes de la musique** (`audio.musiques`, les partitions de secours de `musique.py`,
≈ 45 Ko bruts / 8,7 Ko gzip). Elles sont le FILET : un mp3 absent ou un réseau coupé fait jouer le
séquenceur. ⚠️ Un filet qui dépendrait du réseau n'en serait plus un :

- ce qui joue avant tout réseau (le thème du menu, `titre`) garde ses notes dans le paquet ;
- le reste voyage sur `/api/musiques` (ETag, `?e=` comme la carte), demandé **tout de suite après** les
  définitions, en arrière-plan — jamais au moment où un mp3 rate (c'est souvent que le réseau vient de
  tomber) ;
- l'adresse est dans la **coquille** du travailleur : hors ligne, les notes sont déjà gardées ;
- les métadonnées (slug, nom, fichier, tempo) restent au paquet : `Mus.def`, le jukebox, la radio et les
  musiciens de rue les lisent sans attendre.

**Ensuite** : mesurer le paquet clé par clé et sortir, si c'est aussi sûr, ce que le navigateur ne lit
jamais ou ce qui ne sert qu'à un endroit.

**Juges** : le paquet ne porte plus les notes (sauf le menu) ; `/api/musiques` se revalide et se demande
par son empreinte ; au banc, un morceau sans mp3 dont les notes arrivent après le démarrage joue quand
même ; un réseau qui tombe une fois ne tue pas le filet ; les plafonds baissés à la nouvelle mesure.

## Notes
