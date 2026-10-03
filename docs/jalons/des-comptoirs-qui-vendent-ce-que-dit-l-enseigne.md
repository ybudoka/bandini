# Des comptoirs qui vendent ce que dit l'enseigne

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (3 oct. 2026) :_ « assure-toi qu'on puisse acheter des choses cohérentes dans les commerces qui
vendent des choses ».

### Ce qui se passe aujourd'hui

L'offre d'un comptoir de commerce ne dépend que de la **couleur** de son enseigne (son genre, `devantures.GENRES`),
jamais de son **nom**. La porte prend `famille = enseigne[1]` (`carte.py`), la pièce est celle du genre
(`piece_de_commerce`), et le point du comptoir ouvre `emplettes`, le comptoir du genre (`magasins.COMPTOIRS`) ; deux
exceptions : `service` ouvre le `salon` (les coupes de cheveux), `savoir` ouvre le `journal`. Le titre du menu, lui,
est bien l'enseigne : on lit « BIJOUTERIE » au-dessus d'un sandwich et de chips.

Le compte du 3 oct. 2026, nom par nom sur les 177 enseignes de `devantures.COMMERCES` :

| Genre | Cohérent | Générique (le bon rayon, pas le bon article) | Contredit l'enseigne |
|---|---|---|---|
| bouffe (34) | 10 | 24 : la BOUCHERIE, la BOULANGERIE, la PIZZERIA, la LAITERIE, les restos chinois servent pâté chinois et tarte au sucre ; BEIGNES CHEZ TI n'a pas de beigne | — |
| service (23) | 5 (barbiers, coiffeurs) | — | **18** : une coupe de cheveux à la BANQUE, chez le NOTAIRE, à la POSTE, aux DOUANES, à la GARDERIE, chez le PHOTOGRAPHE, au TAXI |
| commerce (20) | 3 (tabagies, 5-10-15) | — | **17** : BIJOUTERIE, FLEURISTE, RADIO-TV, ANIMALERIE, SPORTS, JOUETS, VÉLOS vendent sandwich et chips |
| marine (19) | 9 (poissonnerie, homard, fumoir) | — | **10** : VOILERIE, CORDAGES, CAPITAINERIE, MOTEURS MARINS, CHANTIER NAVAL servent de la chaudrée |
| industrie (18) | 1 | 17 : extincteur et sandwich partout — PNEUS, DÉBOSSELAGE, PEINTURE AUTO promettent ce que seul le garage fait | — |
| artisan (16) | 3 (quincaillerie, outillage) | 13 : bâton et couteau chez le CORDONNIER, à la PÉPINIÈRE, à l'IMPRIMERIE | — |
| nuit (15) | 10 (tavernes, bars, disco) | 5 : HÔTEL et MOTEL sans chambre, CLUB VIDÉO qui sert des shooters | — |
| mode (12) | 5 (friperie, tailleurs) | 7 : SALOPETTES et BOTTES ne vendent ni salopette ni bottes — qui sont pourtant dans `TENUES` | — |
| sante (11) | 5 (pharmacies, clinique) | 6 : des pilules chez le DENTISTE, l'OPTICIEN, le VÉTÉRINAIRE | — |
| savoir (9) | 2 (journaux) | 3 (librairies, papeterie : un journal) | **4** : DISQUES VOGUE, BIBLIOTHÈQUE, MUSIQUE LAROSE, ÉCOLE DE DANSE ne vendent que le Clairon |
| **177** | **53** | **75** | **49** |

C'est la règle que `magasins.py` écrit lui-même (13 sept. 2026) et ne tient plus : « un comptoir qui vend n'importe
quoi ne dit plus où l'on est ». Une porte de commerce sur cinq s'ouvre (`PART_COMMERCE_VISITABLE`) : on y entre
rarement, et c'est une raison de plus pour que ce qu'on y trouve soit juste.

### Ce qu'on veut

**Le comptoir vend ce que dit l'enseigne.** On entre à la BOULANGERIE, on achète du pain et des beignes ; à la
BIJOUTERIE, une chaîne en or ; chez PNEUS DESCHAMPS, des pneus d'hiver. Et un commerce qui ne vend rien au comptoir
(la BANQUE, le NOTAIRE, les DOUANES) **ne fait pas semblant** : pas de menu d'emplettes, **il rend un service à lui**
— tranché par Martin le 3 oct. 2026, plutôt qu'une simple réplique ou une porte fermée.

- **Un rayon par enseigne, écrit à la main.** Une table `enseigne → rayon` (à côté de `COMMERCES`) et une table
  `rayon → articles` (dans `magasins.py`). Le genre garde la couleur, la pièce et le mobilier ; c'est le rayon qui
  remplit le comptoir. ⚠️ Rien de tiré au dé : un rayon de plus ne doit pas faire glisser la ville
  (une pièce, une tuile ou un dé de plus fait glisser toute la ville). Le rayon voyage avec la porte, comme le nom de l'enseigne.
- **Ce qui existe déjà d'abord.** Beaucoup de rayons cohérents se font avec les catalogues en place : les bouchées
  (`economie.TARIFS` : une bouchée neuve est une ligne et un prix), les tenues (`TENUES` : bottes, salopette,
  chapeaux, parapluie), les armes de sport (bâton), la déco de la planque (RADIO-TV, MEUBLES), les options du garage
  (pneus d'hiver, peinture) chez les commerces de l'auto, le 6/49 et le Clairon aux tabagies.
- **Le neuf, seulement s'il sert.** Un article qui n'a aucun effet en jeu est une promesse de plus qu'on ne tient
  pas. Chaque article neuf doit faire quelque chose : se manger, se porter, se poser à la planque, se donner (un
  bouquet, une chaîne pour un contact), servir en mission, ou se collectionner.
- **Le prix suit le quartier**, comme aujourd'hui (`marge`, `rabais`), et **les heures** restent celles du genre
  (`HEURES_DES_COMPTOIRS`) sauf quand l'enseigne dit autre chose (la boulangerie ouvre tôt).

### Les vagues proposées

1. **La table et la bouffe.** Le rayon de chaque enseigne (les 177, aucune sans rayon) ; les rayons de bouffe qui
   disent leur nom : boulangerie (pain, beigne, croissant), boucherie (tourtière, saucisses), pizzeria (pointe de
   pizza), restos chinois (egg roll, chop suey), laiterie (crème glacée, lait au chocolat), beignerie. Que des
   bouchées : la mécanique existe.
2. **Les marchandises qui existent déjà.** Mode (bottes, salopette, chapeaux, sans les doublons de Rosa),
   commerce (bijouterie → accessoires de tenue ; sports → bâton, casque ; radio-tv et meubles → la déco de la
   planque), industrie de l'auto (pneus d'hiver, peinture, débosselage : les options du garage, au prix du voisin),
   artisan (cordonnier → bottes ; pépinière → plantes de la planque), marine (cordages, moteurs → rien au comptoir, ou
   une pièce pour le bateau), santé (opticien → lunettes, dentiste et vétérinaire → soins, pas de pilules), savoir
   (disques, livres → la collection, si elle existe).
3. **Les services** (Martin, 3 oct. 2026 : chaque commerce sans vente rend un service à lui). Un service par
   métier, et chacun est une mécanique : la liste se fait au début de la vague, et chaque service qui n'a pas
   d'effet en jeu évident se tranche avec Martin. Des pistes : l'hôtel et le motel louent une chambre (DORMIR, comme
   la planque), la banque fait le change ou garde l'argent, la poste envoie un colis, le photographe fait un
   portrait, le taxi te conduit, la garderie… à trouver. Puis les articles qui demandent une mécanique neuve (le
   bouquet qui se donne, la nourriture pour le chat, le vélo).

### Juges

- **Toutes les enseignes ont un rayon**, et tout rayon nommé existe : une enseigne neuve sans rayon fait rougir la
  suite (elle tomberait sinon au comptoir du genre).
- **Rien n'est vendu hors de son rayon** : chaque article d'un comptoir de commerce appartient au rayon de son
  enseigne, et chaque article existe dans son catalogue (bouchée, tenue, arme, déco).
- **Au banc** : on entre dans une porte de chaque rayon, ACTION au comptoir, et le menu porte l'enseigne au-dessus
  des articles de son rayon ; un commerce sans vente n'ouvre pas de menu d'emplettes, mais son service.
- **La ville ne bouge pas** : la même ville avec et sans les rayons, clé par clé (les juges « ce module ne déplace rien »).

## Notes

### Vague 1 : la table et la bouffe (livrée le 3 oct. 2026)

- **`app/rayons.py`** : 246 noms d'enseigne que la ville peut peindre (les trois catalogues de `devantures` et la
  réserve). **97 décidés** (`ENSEIGNES`) et **149 en attente** (`EN_ATTENTE`, chacun avec ce qu'il vendra et sa
  vague). Un juge veut chaque nom dans l'une des deux tables, jamais dans les deux.
- **24 rayons** (`RAYONS`), 23 de bouffe : boulangerie, pâtisserie, pâtisserie chinoise, beignerie, boucherie,
  traiteur, pizzeria, resto chinois, dim sum, BBQ cantonais, nouilles, rôtisserie, casse-croûte, binerie, moules,
  épicerie, épicerie chinoise, fruiterie, laiterie, fromagerie, chocolatier, vins, bistro ; et le comptoir d'un
  CINÉMA RIALTO qui n'est pas le Rialto. **36 bouchées neuves** (`rayons.BOUCHEES`, pas dans `economie.TARIFS` :
  elles voyagent avec leurs rayons) : de 4 à 5 au dollar, sous la borne du hot-dog. Plus une enseigne de bouffe au
  comptoir de sa couleur.
- **Déjà justes** : les tavernes et les bars (`nuit`), les poissonneries (`marine`), les pharmacies (`sante`), les
  quincailleries (`artisan`), les tabagies et les dépanneurs (`commerce`), la friperie (`mode`), les barbiers
  (`salon`), les journaux (`journal`) — décidés vers le comptoir de leur famille.
- **Le poids** : 20 370 octets bruts tels quels, 6 201 compactés (`rayons.exporter` : `[slug, nom]` par article,
  les noms rangés par rayon), dans la **suite** du paquet (`DANS_LA_SUITE`), qui part après l'écran titre. Aucun
  plafond n'avait la marge : Martin a relevé celui de la suite (31 000 → 37 000 bruts, 13 000 → 15 500 gzip).
  `Missions.rayons` les déplie une fois et verse les prix des bouchées dans les tarifs du jeu.
- **Le navigateur** : `Missions.comptoirDuPoint` prend le rayon au nom de la porte (que `Monde.entrer` donne à la
  pièce) quand le point est un comptoir de famille ; sinon, et pour une enseigne en attente, le comptoir du genre.
  Les heures restent celles du genre. Rien ne bouge dans la ville : ni tuile, ni porte, ni dé.
- **Juges** : `test_rayons.py` (les deux tables couvrent tout, un rayon vend à son point, la bouffe dit son nom,
  les articles existent, rien ne bat le hot-dog, chaque porte de commerce de la ville porte un nom connu, le paquet
  porte les rayons) ; `test_rayons_js.py` (le menu de chacune des 97 enseignes décidées, une en attente et le
  dépanneur qui gardent le leur, et l'achat du pain au bouton par la vraie porte d'une BOULANGERIE). Chacun rougit
  quand on retire le rayon du navigateur ou une ligne de la table.
