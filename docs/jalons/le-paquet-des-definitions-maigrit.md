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

**Livré le 29 sept. 2026.** Mesure : **296 109 octets bruts / 66 090 gzip** sur `dev`, **246 381 / 56 345**
après deux sorties. Les plafonds de `test_le_paquet_reste_leger` **descendent** : 300 000 → **256 000** bruts,
67 000 → **59 000** gzip ; les notes ont le leur (50 000 / 10 000 pour 43 775 / 8 382).

- **Les notes de la musique** (−43 504 bruts / −8 783 gzip) : `definitions.sortir_les_notes` retire les
  `voix` de chaque morceau, sauf celles du thème du menu (`musique.NOTES_DANS_LE_PAQUET`) ; elles voyagent
  sur `/api/musiques` (ETag, `?e=`, `musiques_empreinte` dans les définitions). Le navigateur les demande
  juste après les définitions, pendant que la ville se bâtit (`Son.Notes.charger`), et les remet à leur
  morceau. Un morceau qui doit jouer en notes avant leur arrivée se tait, comme pendant le téléchargement
  d'un mp3 ; si la demande a raté, il la refait une fois toutes les dix secondes. La coquille du travailleur
  les garde : le filet tient hors ligne (juge dans Chromium, réseau coupé). `Radio.estProcedurale` ne lit
  plus « le morceau porte ses notes » (la station du camion aurait été prise pour un mp3 de radio).
- **Les bruitages** (−6 224 bruts / −961 gzip) : le nom, la catégorie et `boucle`, qu'aucun script ne lit.
  ⚠️ Et une réparation : la cure du 28 sept. avait emporté `duree_s`, que `Son.SFX.telephone()` lit — l'appel
  parlait 0,37 s après le premier coup d'une sonnerie de deux secondes. Elle revient pour la seule sonnerie
  (`audio.DUREES_LUES`).
- ⚠️ **Ce que ça n'achète pas** : au premier chargement, presque autant d'octets arrivent, en une requête de
  plus, après les définitions au lieu de dedans. Ce que ça achète : un `JSON.parse` plus petit avant le
  menu, des notes qui revalident en 304 quand un catalogue change, et dix Ko gzip de marge rendus au paquet.

**Les prochaines sorties possibles** (mesurées, pas faites) :

- `journal`, `journal_speciales`, `journal_lecons`, `journal_matins` (≈ 4,4 Ko gzip) : ils ne servent qu'au
  journal du matin (sa manchette et sa voix). ⚠️ Un texte n'a pas de repli : il faudrait les demander au démarrage comme les notes
  (et les garder dans la coquille), pas au lever du jour.
- `types_plans` et `types_objectifs` (≈ 750 bruts) : aucun script ne les lit, mais deux juges en font un
  contrat (`test_le_paquet_porte_les_scenes`, `test_le_paquet_contient_tout`) — à trancher.
- `defis` (4 Ko gzip), `personnages` et `visages` (4,8 Ko), `garderobe` (3,4 Ko) : lus au démarrage ou
  à chaque image ; ils ne sortiraient qu'avec la dette des districts chargés autour du joueur.

