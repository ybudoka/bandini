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
(la BANQUE, le NOTAIRE, les DOUANES) **ne fait pas semblant** : pas de menu d'emplettes, il rend un service à lui ou
on y est reçu d'une réplique.

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
3. **Les services, et ce qui reste à trancher avec Martin** : ce que fait un commerce qui ne vend rien au comptoir
   (une réplique, ou un service à lui — la banque, la poste, l'hôtel qui loue une chambre pour dormir) ; les
   articles qui demandent une mécanique neuve (le bouquet qui se donne, la nourriture pour le chat, le vélo).

### Juges

- **Toutes les enseignes ont un rayon**, et tout rayon nommé existe : une enseigne neuve sans rayon fait rougir la
  suite (elle tomberait sinon au comptoir du genre).
- **Rien n'est vendu hors de son rayon** : chaque article d'un comptoir de commerce appartient au rayon de son
  enseigne, et chaque article existe dans son catalogue (bouchée, tenue, arme, déco).
- **Au banc** : on entre dans une porte de chaque rayon, ACTION au comptoir, et le menu porte l'enseigne au-dessus
  des articles de son rayon ; un commerce sans vente n'ouvre pas de menu d'emplettes.
- **La ville ne bouge pas** : la même ville avec et sans les rayons, clé par clé (les juges « ce module ne déplace rien »).

## Notes
