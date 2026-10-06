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
   ⚠️ _Découpée en quatre tranches (Martin, 6 oct. 2026), chacune atterrit seule :_ **2a** les tenues et les armes
   (le rayon transporte ce que le comptoir sait déjà vendre) ; **2b** les options du garage, chez les commerces de
   l'auto, sur le char garé devant la porte ; **2c** les meubles de la planque, livrés le lendemain comme ceux du
   catalogue Beausoleil ; **2d** le neuf qui se dessine — les bijoux de la bijouterie, les lunettes fumées de
   l'opticien.
3. **Les services** (Martin, 3 oct. 2026 : chaque commerce sans vente rend un service à lui). Un service par
   métier, et chacun est une mécanique : la liste se fait au début de la vague, et chaque service qui n'a pas
   d'effet en jeu évident se tranche avec Martin. Des pistes : l'hôtel et le motel louent une chambre (DORMIR, comme
   la planque), la banque fait le change ou garde l'argent, la poste envoie un colis, le photographe fait un
   portrait, le taxi te conduit, la garderie… à trouver. Puis les articles qui demandent une mécanique neuve (le
   bouquet qui se donne, la nourriture pour le chat, le vélo).

   ⚠️ _Tranché par Martin le 6 oct. 2026, en quatre tranches :_ **3a** les services dont la mécanique existe — l'HÔTEL
   et le MOTEL louent une chambre (dormir, comme la planque), les cliniques, dentistes et le SPA soignent au PV
   manquant, la BUANDERIE et le NETTOYEUR lavent le linge (une étoile de moins), la BANQUE et la CAISSE POP tiennent un
   compte (à l'abri de la prison et de l'hôpital), les ASSURANCES assurent le char garé devant, le LAVE-AUTO et CIRE ET
   HUILE le lavent, la FERRAILLE l'achète au prix d'une épave, le CLUB VIDÉO loue un film, le BINGO vend sa carte, le
   CLUB MAH-JONG et la SALLE DE JEUX ont une table du Dragon d'or ; les PRÊTS RAPIDES et CHÈQUES CASH prennent les
   versements de la dette de Rocco, le PRÊT SUR GAGES rachète les armes ; **3b** TAXI DIAMANT, une course où l'on
   veut, payée à la distance ; **3c** le photographe (PHOTO EXPRESS, PHOTO SOUVENIR, PHOTOGRAPHE, STUDIO LAU) rachète
   les photos, fait un portrait, des photos de voyage ; **3d** la MISSION DU PORT et l'HOSPICE donnent une soupe à
   qui est cassé, et les comptoirs sans effet (la POSTE, le NOTAIRE, les DOUANES…) disent une réplique de leur métier.

4. **Les 53 dernières** (tranché par Martin le 6 oct. 2026, en trois tranches) : **4a** ce qui se branche sur
   l'existant — GROSSISTE, ENTREPÔT 7 et IMPORT YIP rachètent la contrebande de Sven au prix du jour, LOCATION VÉLOS
   pose un vélo devant la porte, le CHANTIER NAVAL et la CALE SÈCHE réparent le bateau amarré devant, les fournisseurs
   (des pièces, du bois, de la tôle, des cordages…) et À LOUER disent leur réplique ; **4b** la planque de Rocco gagne
   une pièce (celle d'en arrière, par une porte intérieure) pour ce qui se décore — la lanterne, les plantes, la
   vaisselle, le tableau, les antiquités, le cadre ; **4c** les objets neufs — les disques et les livres deviennent des
   collections (comme les bebelles), le tatouage change ta tête pour la police, le parfum, le bouquet et les jouets se
   donnent à un passant.

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

### Vague 2a : les tenues et les armes (livrée le 6 oct. 2026)

- **16 rayons de plus** (`rayons.RAYONS`, sous « Vague 2a »), et **23 enseignes** sorties de `EN_ATTENTE` : les bottes
  (BOTTES DE TRAVAIL, BOTTES ET CIRES, CHAUSSURES LÉO, la CORDONNERIE avec la ceinture), le linge de travail
  (SALOPETTES), la boutique (BOUTIQUE DIANE, COUTURE CHEZ EVA), le tailleur (le complet, la veste de cuir), la HAUTE
  COUTURE (les mêmes, à 1,4 fois le prix de Rosa), les chapeaux (MODISTE), la MERCERIE (les tuques, la ceinture, le
  parapluie), le magasin d'usine (TEXTILE, MANUFACTURE, à 0,8), la MAROQUINERIE ; les SPORTS (le bâton et la tuque
  bleu-blanc-rouge), PÊCHE ET CHASSE (le couteau, la fronde, les bottes de loup marin), le SURPLUS d'armée, la
  LIQUIDATION (à moitié prix), le BRIC-À-BRAC (la tuque en Phentex et le poing américain), les SOUVENIRS (la ceinture
  fléchée) ; l'ATELIER vend ce que vend la quincaillerie (`artisan`).
- **Rien de neuf** : chaque article est une tenue de Rosa (`_tenue`) ou une arme de Chez Gus (`_arme`), sous son nom
  de catalogue. Une arme prend son prix fois la `marge` du rayon, une tenue le sien fois le `rabais` — les deux que
  le comptoir de famille avait déjà. Aucun rayon ne vend ce qui détone (le marché noir seul) ni un lot ou un cadeau
  (la casquette de la foire, la tuque de Rocco) : un juge le tient.
- **Le poids** : la suite était à 500 octets de son plafond. Le format compact a maigri plutôt que de demander un
  plafond de plus : plus de nom de rayon (le menu porte celui de la porte), le nom d'une bouchée écrit UNE fois
  (`noms` ; un juge veut le même nom dans tous les rayons), une tenue en `t:<slug>` et une arme en `a:<slug>`, et
  plus les 50 enseignes qui retombent d'elles-mêmes au comptoir de leur famille (la TAVERNE, le barbier). Les rayons
  pèsent 7 220 octets bruts au lieu de 8 128 ; la suite fait 36 749 bruts (plafond 37 000) et 15 102 gzip (15 500).
  ⚠️ Les tranches 2b et 2c ne tiendront pas dans 251 octets : à trancher avec Martin à ce moment-là.
- **Juges** : `test_rayons.py` (les tenues et les armes chez qui le dit, ce qui ne se vend pas, le format compact, un
  nom par bouchée) ; `test_rayons_js.py` (les menus des 120 enseignes décidées, et au bouton par de vraies portes :
  le bâton aux SPORTS BEAULIEU au prix de Gus fois la marge, les bottes d'hiver payées, rangées et portées aux BOTTES
  DE TRAVAIL). Retirer du navigateur la lecture des tenues et des armes fait rougir les deux.

### Vague 2b : les commerces de l'auto (livrée le 6 oct. 2026)

- **7 rayons de plus**, et **13 enseignes** sorties de `EN_ATTENTE` : les PNEUS (BEAULIEU, DESCHAMPS) posent les pneus
  d'hiver, la SOUDURE (et PELLETIER) le blindage et répare, les MOTEURS et la TRANSMISSION le moteur gonflé et la
  nitro, l'ATELIER 12 et les PIÈCES D'AUTO les quatre pièces, les PIÈCES USAGÉES trois d'entre elles à 0,7 ; la
  PEINTURE AUTO et le SABLAGE AU JET repeignent (le vol s'efface, comme chez Ti-Guy), le DÉBOSSELAGE et les RADIATEURS
  réparent. Et le café de la salle d'attente, partout.
- **Sur le char garé devant la porte** (`Missions.charDevant`, le même que Ti-Guy) : sans char, le menu le dit une
  fois (« GARE UN CHAR DEVANT LA PORTE ») et ne propose que le café. Les pièces sont celles de `garage.PIECES`
  (`Garage.itemPiece`, sortie de `Garage.items`), au prix de Ti-Guy fois la `marge` du rayon, sans la voix de Ti-Guy
  (ce n'est pas lui au comptoir) ; réparer et repeindre, ceux de `menuGarage` (`itemServiceAuChar`).
- **Deux sortes d'article de plus**, que seuls les rayons portent (`_piece`, `_service` : rien ne change dans
  `magasins.Article`, que les définitions d'avant l'écran titre transportent) ; au format compact, `p:<slug>` et
  `s:<slug>`, et le nom des services voyage une fois (`services`).
- **Restent** : SILENCIEUX (aucune pièce ne fait taire un char), CIRE ET HUILE et le LAVE-AUTO (un lavage, avec les
  services), la FERRAILLE (revendre une épave), et ce qui vend « des pièces » sans dire pour quoi (ACIER DU NORD,
  MACHINERIE, ÉLECTRIQUE, USINAGE, FONDERIE).
- **Le plafond de la suite** : 37 000 → 40 000 bruts, 15 500 → 16 500 gzip (Martin, 6 oct. 2026).
- **Juges** : `test_rayons.py` (ce que fait chaque commerce de l'auto, toute pièce et tout service existent) ;
  `test_rayons_js.py` (au bouton, par une vraie porte, un char garé devant : les pneus d'hiver posés sur CE char au
  prix de Ti-Guy, la PEINTURE AUTO qui efface le vol, le DÉBOSSELAGE qui rend le char neuf ; sans char, la ligne qui
  le dit). Les pièces retirées du menu font rougir le juge des pneus.

### Vague 2c : les meubles de la planque (livrée le 6 oct. 2026)

- **4 rayons de plus**, et **5 enseignes** sorties de `EN_ATTENTE` : les RADIO-TV (DUMAS, KWOK) vendent le téléviseur
  et le juke-box, MEUBLES GAGNON le sofa, le tapis tressé et la lampe à lave, le TAPISSIER le sofa et le tapis (à 0,9 :
  c'est lui qui les refait), l'ANIMALERIE l'aquarium (poisson rouge inclus, il s'appelle Gérald).
- **Livrés le lendemain à la planque de Rocco**, comme chez Gisèle aux puces : `Decoration.livrerA(piece, slug, prix,
  carnet)`, sorti de `commander` (le catalogue Beausoleil y passe aussi). Un meuble commandé ici se dit « LIVRÉ
  DEMAIN » au catalogue et aux puces, et l'inverse — c'est la même commande (`partie.meubles.planque`).
- **Le nom et le prix voyagent avec les collections** (`/api/collections`, `decoration.MEUBLES`) : le rayon ne porte
  que `m:<slug>`. Si les collections ne sont pas encore arrivées, la ligne dit « EN ROUTE », inactive.
- **Restent** : LANTERNES FUNG (une lanterne pour la planque — un meuble neuf à dessiner), la PÉPINIÈRE et la
  VAISSELLE CHOW (la planque n'a ni plantes ni vaisselle), l'ANIMALERIE garde l'idée de nourrir le chat pour plus tard.
- **Juges** : `test_rayons.py` (qui vend quel meuble, et chacun a sa place à la planque) ; `test_rayons_js.py` (au
  bouton, à la RADIO-TV DUMAS : le téléviseur payé au prix du catalogue, « LIVRÉ DEMAIN », livré le jour suivant).
  Le meuble retiré du menu fait rougir les deux juges du banc.

### Vague 2d : le neuf qui se porte (livrée le 6 oct. 2026)

- **Deux places neuves sur le joueur** (`magasins.PLACES`, `PLACES_DE_TENUE`, `partie.cou` et `partie.yeux`) : ce qui
  se porte AU COU et SUR LES YEUX, en plus du reste, comme la ceinture et le parapluie. Chez Rosa, deux sections de
  plus (AU COU, LES LUNETTES).
- **Quatre tenues neuves**, marquées `en_ville` : Rosa ne les vend pas — elles n'y paraissent qu'une fois à soi, pour
  les remettre. La BIJOUTERIE et BIJOUX CHEUNG vendent la chaîne en or (400 $) et la chaîne plaquée or (90 $, la même
  de loin) ; l'OPTICIEN et l'OPTIQUE, les lunettes fumées ; la SOIERIE MEI et TISSUS ET SOIES, le foulard de soie (et
  la chemise hawaïenne).
- **Un seul dessin neuf** : la chaîne (`chaine`, ajoutée au BOUT de `garderobe.ACCESSOIRES` — aucune garde-robe de
  passant ne la nomme, aucun dé ne bouge), un V d'or au col de face, une maille de profil, dans le jaune de la
  palette (`y`). Les lunettes fumées (`lunettes_soleil`) et le foulard se dessinaient déjà sur les passants. Les
  grilles cuites ont été regardées de face et de profil avant la livraison.
- **Le poids** : les quatre tenues voyagent avec les autres, dans les définitions ; leur budget (`tenues`, 1 050 gzip)
  et celui du paquet tiennent.
- **Juges** : `test_rayons.py` (qui vend le neuf, les deux places, chaque tenue `en_ville` vendue par quelqu'un) ;
  `test_garderobe.py` (les places, les pièces du cou et des yeux) ; `test_rayons_js.py` (au bouton, à la BIJOUTERIE :
  la chaîne payée, portée au cou, dessinée ; absente chez Rosa avant, présente après).

### Ce qui reste après la vague 2

102 enseignes attendent encore. Les services (vague 3, une cinquantaine), et les marchandises qui demandent une
mécanique neuve : le bouquet qui se donne (FLEURISTE), les jouets, le cerf-volant, le vélo à louer, la planche, la
lanterne de la planque, les plantes et la vaisselle, les disques, les livres et l'instrument, le parfum, le
tatouage ; le gros (ENTREPÔT 7, GROSSISTE) et le prêt sur gages ; « des pièces » sans destinataire (ACIER DU NORD,
MACHINERIE, USINAGE…) ; et la marine (cordages, voilerie, moteurs marins : le bateau n'a pas encore de garage).

### Vague 3a : les services dont la mécanique existe (livrée le 6 oct. 2026)

- **18 rayons de plus**, et **24 enseignes** sorties de `EN_ATTENTE` (168 décidées sur 246). Chaque service réutilise
  une mécanique du jeu (`rayons.SERVICES`, `Missions.itemsDuService`), aucun n'a d'état à lui :
  - l'HÔTEL DES QUAIS et le MOTEL LA POINTE (à 0,6) : le lit de la planque, payé — dormir jusqu'au matin (la partie
    se sauve, devant leur porte) ou jusqu'au soir ;
  - la CLINIQUE, le DOCTEUR, la POLYCLINIQUE, les DENTISTES (1,2), l'ACUPUNCTURE LEE (0,8), le SPA (2) : les soins, au
    PV manquant (0,50 $ le PV : un peu plus que les pilules, mais jusqu'au bout) ;
  - la BUANDERIE, le NETTOYEUR (1,5) : laver son linge, une étoile de moins (comme le lave-auto) ;
  - la BANQUE et la CAISSE POP : le coffre de la planque au guichet — pas un compte de plus, le même argent à l'abri
    de la prison ;
  - les ASSURANCES : l'assurance de Ti-Guy, sur le char garé devant ; le LAVE-AUTO et CIRE ET HUILE : le laver (une
    étoile de moins) ; la FERRAILLE : l'acheter, épave comprise, à la moitié du prix de vente de Ti-Guy, et il quitte
    la rue ;
  - le CLUB VIDÉO : le film du soir, regardé dans l'arrière-boutique (`repos_pv` du Rialto) ; le CLUB MAH-JONG : la
    table de sic bo du Dragon d'or ; la SALLE DE JEUX : la machine à sous (les limites du jour sont celles du casino) ;
  - les PRÊTS RAPIDES et CHÈQUES CASH : les versements de la dette de Rocco (`menuDette`, le répit compris) ; le PRÊT
    SUR GAGES : il rachète tes armes à 40 % du prix de Gus, et revend un poing américain et un couteau à 0,8.
- **Plus de coupe de cheveux à la banque** : les pièces de SERVICE n'ont pas de comptoir, mais le fauteuil du barbier
  (`salon`). Quand la porte a un rayon neuf (`Missions.rayonDuFauteuil`), le fauteuil devient son comptoir, aux heures
  de la famille `service`, et l'invite dit « AU COMPTOIR ». Le barbier et le coiffeur gardent leur fauteuil.
- **L'hôtel dit « DORMIR JUSQU’AU MATIN »**, comme le lit de la planque : ce sont deux départs, et le menu se referme
  (`test_un_comptoir_reste_ouvert`) ; le film aussi (il passe au noir), et les tables ouvrent leur propre menu.
- **Juges** : `test_rayons.py` (chaque service rendu par quelqu'un, qui rend quoi, plus de fauteuil de barbier ailleurs
  que chez les barbiers) ; `test_rayons_js.py` (au bouton, par de vraies portes : la CLINIQUE soigne au PV manquant, la
  BUANDERIE fait tomber une étoile, la BANQUE dépose au coffre, les PRÊTS RAPIDES prennent l'acompte, le PRÊT SUR GAGES
  rachète le couteau, l'HÔTEL fait dormir jusqu'au lendemain ; l'assurance et le lavage sur le char garé devant, la
  FERRAILLE qui prend l'épave, le film, la table de sic bo, le motel). Le fauteuil rendu au barbier et le gage qui ne
  retire pas l'arme font rougir le juge du bouton.

### Vague 3b : la course de taxi (livrée le 6 oct. 2026)

- **TAXI DIAMANT** a son rayon (le répartiteur, et son café) : une ligne par destination (`rayons.TAXI`, écrites à la
  main — la planque, le garage, Rosa, Gus, le Brouillard, l'hôpital, le dojo, le Dragon d'or, le phare, l'aéroport),
  payée 5 $ plus un dollar par huit tuiles à vol d'oiseau (`TAXI_BASE`, `TAXI_TUILES`). Une destination à moins de
  douze tuiles ne se propose pas : on y va à pied.
- **On sort chez Rosa** : la rue de sortie (`B.exterieur`) est recalée sur la porte de la destination, puis
  `Jeu.sortir` — comme le métro remonte à l'édicule d'une autre station. Le char qu'on avait garé devant le taxi y
  reste.
- **Le plafond de la suite** : 40 000 → 44 000 bruts, 16 500 → 18 000 gzip (Martin, 6 oct. 2026) — elle était à 40 131 ; les
  services ont maigri (un nom seul quand il n'y a ni prix ni char, et rien pour ceux qui font leurs lignes).
- **Juges** : chaque destination a sa porte dans la ville (`test_rayons.py`) ; au bouton, la course CHEZ ROSA payée,
  et l'on sort devant la boutique (`test_rayons_js.py`). Sans la rue recalée, le juge rougit.

### Vague 3c, 1re partie : l'album des lieux et le rachat (livrée le 6 oct. 2026)

- **L'album des lieux** (Martin, 6 oct. 2026 : « photos de voyage », un album à collectionner) : le mode photo
  reconnaît dix lieux (`photos.ALBUM` — le phare, l'aéroport, le Dragon d'or, la chapelle, le terminus, l'usine, le
  Rialto, l'hôpital, la caisse populaire, la fourrière), par la PORTE du lieu dans le cadre (`Photos.lieuDuCadre`). Le
  déclic le met sur la pellicule (`partie.pellicule`) et le dit (« SUR LA PELLICULE : LE PHARE DE LA POINTE ») ; une
  photo de lieu n'empêche pas la photo du Clairon, les deux se prennent du même déclic.
- **Les quatre photographes** (PHOTO EXPRESS, PHOTO SOUVENIR, PHOTOGRAPHE, STUDIO LAU) ont leur rayon : l'album
  (n / 10), DÉVELOPPER LA PELLICULE (5 $ le lieu, `photos.PHOTOGRAPHE`), et le RACHAT de la photo du jour à la moitié
  du prix de Louise — même trop vieille pour le Clairon : il en fait des cartes postales.
- **Juges** : chaque lieu de l'album a sa porte, et les quatre développent et rachètent (`test_rayons.py`) ; au
  bouton : le phare dans le cadre sur la pellicule, développé au STUDIO LAU, la photo rachetée (`test_rayons_js.py`).
  Sans la pellicule, le juge rougit.

### Vague 3c, 2e partie : le portrait et le cadre de l'album (livrée le 6 oct. 2026)

- **TON PORTRAIT** (60 $, `decoration.MEUBLES`, `ou: photographe`) : chez les quatre photographes, tiré au studio avec
  la tenue et la coupe du jour (`partie.portrait` : la peau, les cheveux, la couleur du haut, le chapeau s'il y en a
  un), encadré d'or, livré le lendemain au mur de la planque de Rocco (`Decoration.livrerA`, comme les meubles).
- **L'ALBUM DES LIEUX** complet (les dix) pose son cadre au mur, comme les cartes de hockey posent les leurs : un
  trophée (`famille: lieux`, `palier: 10`), dix cartes postales sous verre, chacune son ciel et la couleur de son lieu.
- **La planque de Rocco seulement** (`decoration.SEULEMENT`) : les rondins du chalet n'ont plus un bout de mur (les deux
  cadres, les fenêtres, la cheminée) ni une table libre. Dans la planque, les deux derniers bouts de mur : au-dessus du
  coffre et dans le coin de la garde-robe. Le juge de la décoration admet une place absente quand `SEULEMENT` le dit.
- **Regardés avant la livraison** : les deux portraits (avec et sans chapeau) et le cadre de l'album, peints par le jeu
  à ×8 dans Chromium, à côté du cadre des dix cartes pour l'échelle.
- **Juges** : `test_decoration.py` (les places, `photographe` comme lieu de vente) ; `test_rayons_js.py` (au bouton, au
  PHOTOGRAPHE : le portrait payé, tiré avec la tenue du jour, absent aujourd'hui, au mur demain ; l'album complet pose
  son cadre à la planque, pas au chalet).

### Vague 3d : la soupe des pauvres et les répliques (livrée le 6 oct. 2026)

- **La soupe** : la MISSION DU PORT et l'HOSPICE servent un bol de soupe aux pois (ses gains, `economie.TARIFS`),
  gratuit, une fois par jour (`partie.soupe`), à qui a moins de 20 $ en poche (`rayons.SOUPE`). Riche, la ligne le dit
  gentiment : « POUR CEUX QUI SONT CASSÉS » — on ne rit pas des pauvres (docs/ecrire-drole.md).
- **Les répliques** (`rayons.REPLIQUES`, 20 enseignes, cinquante lettres au plus) : ceux qui ne vendent rien ont un
  comptoir quand même — « RIEN À VENDRE ICI », et leur réplique sous le menu (`aide`) : le métier qui se moque de
  lui-même (« Le guichet ferme dans cinq minutes. Depuis 1974. », « Chut. »). Les fausses façades BINGO servent le café
  et le beigne de la salle, et renvoient au vrai, au sous-sol du Faubourg.
- **Le présentoir du savoir** : l'ÉCOLE, l'ÉCOLE DE DANSE, la BIBLIOTHÈQUE et les ARCHIVES n'ont ni comptoir ni
  fauteuil, mais le présentoir du Clairon (`journal`) ; comme le fauteuil des pièces de service, il devient le comptoir
  de leur rayon (`rayonDuFauteuil`), aux heures de la famille `service`. Le kiosque et les journaux gardent le Clairon.
- **Juges** : chaque enseigne à réplique a la sienne, assez courte, et plus aucun service n'attend (`test_rayons.py`) ;
  au bouton, la soupe à la MISSION DU PORT (riche : refusée ; cassé : servie, puis « À DEMAIN »), et l'ÉCOLE qui dit sa
  réplique (`test_rayons_js.py`). Le présentoir rendu au Clairon fait rougir le juge.

### Ce qui reste après la vague 3

53 enseignes attendent une mécanique neuve : le bouquet qui se donne (FLEURISTE), les jouets, le cerf-volant, le vélo à
louer, la planche, la lanterne de la planque, les plantes et la vaisselle, les disques, les livres et l'instrument, la
papeterie, le tableau, l'antiquaire et le cadre, le parfum, le tatouage ; le gros (ENTREPÔT 7, GROSSISTE) et les
importations ; « des pièces » sans destinataire (ACIER DU NORD, MACHINERIE, USINAGE…), le bois, la tôle, le fer forgé ;
et la marine (cordages, voilerie, moteurs marins, chantier naval : le bateau n'a pas encore de garage). Elles vendent
encore au comptoir de leur couleur.

⚠️ **Une ville sans barbier, réparée le jour même** : la ville n'ouvrait que trois pièces de service (la BUANDERIE, le
STUDIO LAU, le NOTAIRE LEUNG), et c'est là qu'on se faisait couper les cheveux ; une fois leur service rendu, la coupe
qui fait oublier ta face n'était plus nulle part. Tranché par Martin (6 oct. 2026) : **ouvrir une porte de barbier**.
Le BARBIER est la cinquième des enseignes qui ouvrent pour vrai (`enseignes.ENSEIGNES`, EN DERNIER : les quatre
d'avant choisissent leur porte sans lui), sur la ville finie et sans dé : le Faubourg n'ayant plus de porte, il prend
la porte de commerce la plus proche de son cœur, près de la planque — la pièce d'un commerce de service, et son
fauteuil (`piece_de_barbier`). La suite complète, passée en parallèle avec lui, n'a rougi qu'au juge des enseignes qui
voulait un comptoir.
