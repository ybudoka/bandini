# Bandini — plan et état d'avancement

Document de reprise : à lire en début de session. Le plan ci-dessous a été
approuvé par Martin le 12 septembre 2026. Mettre à jour la section « État des
jalons » à chaque jalon livré.

## État des jalons

Les lignes **livrées** sont dans l'ordre où elles l'ont été ; celles **à faire** sont dans
l'ordre où on compte les faire — **par priorité**, prérequis devant (le détail est dans
« La v2 » plus bas).

⚠️ **Une colonne, une question** — chaque ligne se lit en quatre coups d'œil avant d'entrer
dans les notes :

- **État** — `à faire`, `en cours`, `livré`. Une seule chose s'y lit d'un balayage : ce qui
  bouge en ce moment. ⚠️ **On passe une ligne à `en cours` et on la pousse _avant_ d'écrire
  le code** — plusieurs sessions travaillent dans le même arbre, et cette colonne est le
  seul endroit où elles se voient.
- **Date** — le jour de la **livraison** ; pour une ligne `en cours`, le jour où elle a
  commencé ; pour un essai annulé, le jour de l'essai. `—` tant que rien n'a commencé.
- **Prio** — « qu'est-ce qui coûte le plus cher à ne pas faire ? » : **P1** le jeu ment,
  **P2** ça se sent à chaque partie, **P3** ça porte le reste, **P4** ça enrichit ; l'échelle
  est détaillée dans « La v2 ». ⚠️ `—` ne veut pas dire « pas urgent » : **la priorité n'est
  notée que depuis M9** (13 sept. 2026), alors tout ce qui est livré avant n'en porte pas.
- **Genre** — un **correctif** répare une promesse que le jeu fait déjà et ne tient pas ; un
  **ajout** en fait une nouvelle. Il suit les préfixes de commit du dépôt (`fix:` et `feat:`),
  donc pour les lignes déjà livrées, c'est l'historique git qui le dit.

⚠️ **Toute ligne à faire doit porter sa prio et son genre** : ce sont eux qui décident de
l'ordre plus bas.

⚠️ Les numéros de jalon sont des **noms**, pas un ordre : tout le dépôt y renvoie, alors ils
ne bougent pas quand l'ordre de travail change.

| Jalon | État | Date | Prio | Genre | Notes |
|---|---|---|---|---|---|
| Le char abrite, l'appel fige | **livré** | 15 sept. 2026 | **P2** | **correctif** | retour de Martin : « quand on est dans un voiture ou autre, il ne faut pas que les pietons puisse nous faire du domage » et « il faut aussi figer tout lors qu'on est au téléphone et qu'on ne peut pas bouger ». Deux promesses que le jeu ne tenait pas, et la règle qui les répare était **déjà écrite une fois**, pour le feu : un brasier mord le CHAR et saute qui est dedans (`majBrasiers`). Ni le poing ni la balle ne la connaissaient — mesuré, un passant planté à douze pixels enlevait **8 points de vie à travers la portière**, et une balle de pistolet **30**, sans que la carrosserie perde un seul point. ⚠️ **La règle vit maintenant dans `Entites.blesser`** — `if (e.dansVehicule) return false` — c'est-à-dire au seul endroit par où passe toute blessure du jeu, plutôt qu'en trois exemplaires dans `Combat` (le poing, la balle, la grenaille, et le prochain qui s'ajoutera). Ce qui SORT du char descend AVANT de blesser — l'explosion et l'éjection appellent `descendre` d'abord, et le char qui renverse quelqu'un ne regarde que ceux qui marchent : c'est ce qui rend la ligne sans danger. ⚠️ **Et la tôle encaisse VRAIMENT** : la balle qui aurait touché le conducteur mord le char (`Vehicules.endommager`), exactement comme le brasier. Sans ça, le seul effet de l'abri aurait été de faire **disparaître** la balle, et la police aurait pu vider ses chargeurs sur une carrosserie sans jamais rien obtenir — un char serait devenu le seul endroit du jeu où l'on ne risque rien. (Tirer sur le capot d'un char **vide** ne fait toujours rien : les projectiles ne visent que les gens, c'est un autre chantier.) ⚠️ **Le téléphone fige la ville comme un menu** : `B.cinema` clouait le JOUEUR sur place (`majJoueur`, `vx = vy = 0`) pendant que le trafic, la foule et la police continuaient — mesuré, **26 entités bougeaient pendant qu'on écoutait**, et on encaissait des coups qu'on ne pouvait pas rendre. `Jeu.maj` traite désormais un dialogue comme un menu (« le temps ne passe pas au comptoir ») ou un fondu de porte : seul `Histoire.maj` tourne, pour que la réplique avance et qu'on puisse raccrocher. ⚠️ **Sauf au volant**, et cette moitié compte autant : là on PEUT encore bouger (`Vehicules.majJoueur` lit toujours le gaz pendant un dialogue), et figer un char lancé parce que le téléphone sonne, ce serait poser un mur au milieu de la rue. ⚠️ Et « ACTION > » clignote maintenant sur l'horloge de l'**œil** (`B.image`), pas sur celle du monde : `B.t` ne bouge plus pendant l'appel, et l'invite serait restée éteinte au seul moment où elle a quelque chose à dire. 4 juges neufs (`test_abri_js.py`), **rouge-avant prouvé trois fois** (8 points au poing, 30 à la balle, 26 entités qui bougeaient) ; le 4e était **vert avant** et le reste — il tient l'autre moitié (au volant, la ville tourne et le char répond au gaz), c'est un garde-fou, pas une mesure. 1650 tests. ⚠️ Jugé dans un **worktree isolé** : deux autres sessions écrivaient dans l'arbre. |
| Un menu qui ne choisit rien | **livré** | 15 sept. 2026 | **P2** | **correctif** | retour de Martin, capture à l'appui (« il n'y a pas de sélection dans ce menu ») : au comptoir des **hommes de Sal**, aucune ligne n'est surlignée, HAUT et BAS ne bougent rien, ACTION ne donne pas un sou. La collecte était le **seul menu du jeu posé à la main** — `B.menu = menuDette(...)` au lieu de `Hud.ouvrirMenu` — donc ouvert **sans curseur** : `undefined`, que HAUT et BAS transforment en `NaN` (`(undefined + 1) % 4`), et un curseur `NaN` ne surligne aucune ligne, n'en choisit aucune et ne revient jamais. Deux dégâts de plus par la même porte manquée : les boutons de l'écran tactile continuaient d'annoncer FRAPPE et ACTION au lieu de RETOUR et CHOISIR (`Entree.contexte('menu')` est dans `ouvrirMenu`), et le petit son du menu ne sortait pas. **On ne pouvait pas payer Sal**, au moment le plus tendu du jeu. ⚠️ Deux autres choses tenaient sur la même capture. **L'en-tête** : même passé par la porte, ce menu s'ouvrait sur « LA DETTE », une ligne qui se lit et ne se choisit pas — le menu n'a l'air d'avoir aucune sélection, et ACTION n'y répond qu'un bip. La règle existait, mais **à la main** (les OPTIONS portent `curseur: 1` parce que leur première ligne est un diagnostic) et **cinq menus l'avaient oublié** : la dette, le carnet du poste, l'avocat, le comptoir du fond, la revente de contrebande. Elle se tient maintenant **une fois**, dans `ouvrirMenu` : le curseur se pose sur la première ligne qui porte un `faire`. ⚠️ Une ligne **hors de portée** reste un choix — le curseur s'y pose et c'est le prix qui dit non ; un menu qui **nomme** son curseur le garde (le JOURNAL s'ouvre en haut de sa liste et s'y promène) ; un menu où il n'y a rien à choisir (le BILAN) reste en haut. **Le fond** : la boîte d'un menu ne couvre qu'à 92 %, et ce qui est clair derrière la traverse — la bulle d'un passant qui parlait sous le comptoir s'imprimait **en travers** de « TOUT REGLER », illisible sur la capture. La pause posait déjà son voile avant son menu ; un menu en jeu fige le monde autant qu'elle et a maintenant le même (mesuré après, au navigateur : le fantôme de la bulle tombe à **3 niveaux sur 255**, sous la lecture). 3 juges de banc, rouges avant : le menu de Sal se joue pour de vrai (il s'ouvre sur l'acompte, BAS descend d'un cran, ACTION donne 2000 $, la dette baisse d'autant, ils s'en vont, et le bouton dit CHOISIR) ; un menu s'ouvre sur une ligne qu'on peut choisir dans les quatre cas ; la rue s'efface sous un menu ouvert, et le voile passe **avant** la boîte. |
| Le char tourne comme son ombre | **livré** | 15 sept. 2026 | **P1** | **correctif** | retour de Martin : « le pilotage des véhicules est vraiment impossible maintenant, il faut que le véhicule tourne vraiment comme l'ombre le fait, sinon impossible de conduire ». Le char DEBOUT n'avait que **quatre dessins** — profil, dos, face — pour un cap **continu** : l'ombre pivotait sous lui à chaque image, la caisse attendait 45° et **claquait**, et en claquant elle **sautait** d'une demi-longueur (la ligne de sol du profil et celle du dos ne sont pas au même endroit). Au volant, on ne voyait plus où on pointait : on lisait son cap sur son ombre. ⚠️ **Une ÉLÉVATION ne se laisse pas tourner** — un dessin de flanc pivoté de 40°, c'est un char qui cabre — mais une **vue d'en haut**, oui : c'est `haut`, le toit, qui roule désormais, tourné en **32 caps** comme l'ombre (moins de 6° d'écart avec le vrai cap, contre 45 avant), autour du **centre de l'empreinte du catalogue** — donc sur `v.x`, `v.y`, là où l'ombre est posée et où les cercles bloquent. ⚠️ **Et les caps ne coûtent plus ce qui les avait tués** : les 32 de toute la flotte cuits d'avance pesaient 1 024 canevas et 6 Mo ; ils sont maintenant cuits **un par un, à la demande** (`Atlas.cuireCap`) — un char à l'arrêt en coûte 3, un tour complet 34, et le trafic sur ses rails n'en montre que quatre. ⚠️ **Les phares viennent de `bas`** : les deux vues d'en haut sont le même toit lu dans l'autre sens (l'une ne montre que les feux arrière, l'autre que les phares), et le dessin qui tourne les porte **tous les deux**, sinon un char qui vient vers nous roule tous phares éteints — au passage, un vieux bogue de dessin : la moto et le vélo portaient leur phare **à la queue** dans leur pose `bas`. ⚠️ **La selle est un point de la MACHINE** et elle tourne avec elle (une seule `selle` au lieu de trois, une par pose) : sans ça, le cycliste restait assis au nord de son vélo dès qu'il roulait vers le sud. `cote` reste dans `sprites.js`, entier et **non dessiné** — une belle élévation pour le jour où un char se montre de profil sans rouler ; elle ne coûte rien tant que personne ne l'appelle. ⚠️ **Reste à faire, mesuré en chemin** : quatre dessins sont plus **courts** que leur fiche (l'ambulance et la remorqueuse de 5 px, le camion et l'autobus de 3 — leur grille a été taillée à `longueur` au lieu de `longueur + 4`), et le manque se voit au nez. 4 juges de banc neufs (le cap dessiné suit l'ombre à un demi-cran près et les 32 servent tous ; le dessin est centré sur son empreinte à tous les caps ; le toit qui tourne porte phares ET feux, chacun à son bout ; l'atlas ne cuit que les caps montrés), 3 refaits (la ligne de sol devenue le milieu, les phares qui pointent où le char va, le cavalier qui reste assis quand sa machine tourne) |
| Un char garé dans ses lignes | **livré** | 15 sept. 2026 | **P2** | **correctif** | retour de Martin, capture à l'appui (« les voitures sont mal garré ») : dans un stationnement, les chars débordaient par le nez sur le trottoir et laissaient le fond de leur case vide. La cause est dans la ligne précédente — **la vue plongeante**. Le jour où les poses `haut` et `bas` sont passées de douze rangées à la **longueur** du char (28 px pour une berline), elles sont restées posées à la ligne de sol du **profil**. Or ces deux lignes ne sont pas au même endroit : de profil, le dessin est une **élévation** — sa dernière rangée est le **flanc**, et le flanc passe par le milieu du char, donc l'ancre tombe sur `v.y` comme les pieds d'un passant ; de dos, c'est le char **vu d'en haut** — sa dernière rangée est le **pare-chocs**, à une **demi-longueur** de `v.y`. Posée sur `v.y`, elle mettait 28 px de caisse au nord d'un centre qui n'en compte que 14 : **tout char tourné vers le nord ou le sud se dessinait 14 px devant lui-même**, garé comme en marche. Une case de stationnement le montre au premier coup d'œil — elle fait 32 px de creux, le gabarit exact d'une auto, alors le nez sortait sur le trottoir et le fond restait vide. ⚠️ **L'ancre du sprite ne bouge pas** (la même pour les trois poses, sinon le char saute d'un pixel en tournant) : c'est le SOL qu'on va chercher là où il est (`solDeLaPose`), et il vient de l'**empreinte du catalogue** — la même que la physique et que l'ombre. Ce qu'on voit est exactement ce qui bloque. ⚠️ **Et le cavalier prend le même décalage** : sans ça, le passant assis sur un vélo pédalait une demi-longueur devant sa selle. Mesuré après, sur les onze véhicules debout et les quatre caps : la dernière rangée tombe à la demi-longueur du centre (0 avant). 2 juges de banc, rouges avant (la caisse tient dans son empreinte de dos comme de face sans dépasser ni derrière ni devant, et le profil pose toujours sa ligne de sol sur `v.y` ; le cavalier est assis au milieu de sa machine) |
| Ce qui se dit destructible l'est | **livré** | 15 sept. 2026 | **P2** | **correctif** | un lampadaire portait `casse: 0.7` depuis toujours et encaissait un chargeur de carabine sans broncher : `Entites.briser` n'avait qu'**un seul appelant**, le char lancé. La balle traversait le décor (`majProjectiles` ne s'arrêtait que sur une façade), l'explosion d'un char ne filtrait que `q.vivant` — ce que le décor n'est pas — et le brasier d'un molotov non plus. Deuxième moitié, plus vieille : `buisson` et `corde_a_linge` déclaraient `casse` avec `solide: false`, et l'index du décor ne prenait que le solide — deux fiches destructibles sur le papier que **rien au monde** ne pouvait toucher ; la règle existait en **deux exemplaires** (`reindexerDecor` et `creerDecor`), si bien que le premier correctif n'en a réparé qu'un et qu'il a fallu un juge qui tire sur un buisson de la **vraie carte** pour voir la copie oubliée. La fiche gagne `pv` (l'échelle se lit en balles de pistolet : poubelle 25, lampadaire 60, kiosque 90) et `Entites.endommagerDecor` est le second chemin vers `briser` — balle, explosion, feu. Ce qui porte `arrete` (arbre, fontaine, camion-restaurant) n'a **pas** de `pv` : il encaisse et ne tombe jamais, c'est ce qui fait un abri. Trois pièges réglés en chemin : la balle jugée sur son **trajet** et non son point d'arrivée (10 px par image, un poteau en fait 8 — elle le traversait une fois sur deux) ; la cible visée à **hauteur de canon** (`y - 6`) plutôt qu'élargie de 7 px, sans quoi un banc devenait un gilet pare-balles plus large qu'un passant ; et **une balle, une morsure**, sinon ce qui ne l'arrête pas se faisait mordre à chaque image. `scripts/verifier_ce_qui_casse.py` tient le catalogue et le câblage, branché en **garde Claude Code** à l'écriture et avant `git commit` comme ses deux voisins ; `tests/test_ce_qui_casse.py` : 6 juges de forme + 6 de banc qui tirent pour de vrai |
| M0 Squelette et mise en ligne | **livré** | 12 sept. 2026 | — | ajout | dépôt `ybudoka/bandini`, Flask + uv, 13 fichiers JS, entrées, banc Node, CI, tests ; serveur installé, https://bandini.gestiondojo.ca |
| M1 La ville | **livré** | 12 sept. 2026 | — | ajout | `carte.py` : trame **irrégulière** (colonnes, rangées et rues toutes différentes), superblocs qui avalent des rues, parcelles BSP par îlot, 157×112 tuiles, 62 croisements dont des T, 10 intérieurs ; juges (voies fortement connexes, un seul îlot marchable, **asymétrie**) ; cache de morceaux borné, mini-carte |
| Audio ElevenLabs | **livré** | 12 sept. 2026 | — | ajout | MCP `elevenlabs` + `app/audio.py` + 18 bruitages dans `static/audio/` ; **3 radios** (La Brume jazz, Taxi-Radio country, Le Choc **techno**) et une **musique de fond** de ville (à pied) par ElevenLabs Music, chargées au premier geste ; **rumeur de la foule** (volume selon les gens autour), chars et motos qu'on entend passer (placés dans le stéréo), sonnette de vélo ; **8 répliques de passants** (Léo québécois / Sarah) par TTS — voix des donneurs en M6 |
| Vie de rue | **livré** | 12 sept. 2026 | — | ajout | femmes, enfants (**intouchables**), mères suivies de leur petit, filles de la Brume (la nuit, un fondu, jamais une scène), kiosques à hot-dogs / journaux / roulotte à café et camions-restaurants posés par `carte.py` |
| La rue dans la vraie vie | **livré** | 13 sept. 2026 | — | **correctif** | retour de Martin (chars fous, piétons sur la chaussée, puis chars coincés au croisement, bandes des passages à l'envers) : un char d'en face dans la voie d'à côté n'est plus un obstacle, un croisement se **réserve** (un char à la fois, jusqu'à ce qu'il ressorte), les bandes sont parallèles à la circulation ; le trafic roule **sur des rails** (centre de tuile en centre de tuile, jamais un coin coupé), les piétons **ne posent pas le pied sur la chaussée** et traversent au passage quand c'est sûr, sortent des portes et rentrent chez eux ; **feux visibles** aux vrais croisements, **STOP** à la tige des T, priorité aux piétons engagés, **cyclistes** dont on prend le vélo |
| M2 Piétons et poings | **livré** | 12 sept. 2026 | — | ajout | `pietons.py` (8 archétypes, courage, témoin, gangs) ; hachage spatial, bulle de foule, flâner/fuir/témoin/riposter, mêlée en trois temps, coup fort, roulade, projectiles + plombs + cloche, visée assistée, armes de fortune qui cassent, sang plafonné, pickpocket dans le dos |
| M3 Véhicules | **livré** | 13 sept. 2026 | — | ajout | auto, taxi, moto, auto-patrouille (sprite) ; physique arcade, **chaîne de cercles**, sous-pas, monter/descendre/carjacking/éjection, trafic qui **lit le champ `voie`** (tourne à gauche après le croisement, ralentit avant le coin), feux sur les vrais croisements, dégâts/fumée/feu/explosion, alarmes, rampes, renversements, taxi au klaxon avec pourboire selon la douceur, hôpital quand on meurt, moteur qui monte dans les tours |
| M5 Intérieurs et économie | **livré** | 13 sept. 2026 | — | ajout | entrer/sortir des 10 intérieurs (fondu, pièce centrée, points d'action), menus canvas qui figent le jeu, planque (dormir = sauvegarder + lendemain, coffre à l'abri de la prison, garde-robe, char stationné qui revient), garage (revente, réparation, peinture qui efface le vol), Chez Gus (armes, munitions), Boutique Rosa (tenues), casse-croûte, hôpital, propriétés (achat à la porte, caisse plafonnée à 3 jours), 20 paquets cachés + primes, journal du matin (`journal.py`), pause = menu (reprendre, **bilan de session**, **options** sang/vibration/son/daltonien sauvegardées, envoi du score) |
| Gestes et lisibilité | **livré** | 13 sept. 2026 | — | **correctif** | retour de Martin : le corps **bouge** quand on agit — élan du coup, bras et arme superposés (toutes armes, PNJ compris), chancellement quand on est touché, roulade qui tourne, dos courbé pour ramasser, éclair de bouche au tir ; les accents et l'apostrophe courbe tombaient sur « ? » dans la police pixel — normalisés avant le dessin, avec un test sur chaque nom du jeu |
| M4 Police | **livré** | 13 sept. 2026 | — | ajout | `police.js` réécrit : agents à pied (archétype `policier`, patrouille par zone, cône vérifié une image sur trois, poursuite par **A\*** sur les trottoirs, arrestation au contact, sortent le joueur d'un char arrêté), **rien n'est compté tant qu'un agent ne l'a pas vu** — un passant qui a vu devient témoin porteur du crime, court le raconter à un agent ou téléphone (`temoins`), et on peut **acheter son silence** (20 $) ; délits bruyants (`temoin: false`) comptés tout de suite ; étoiles qui ne tombent qu'hors de vue (dedans aussi) ; menu d'arrestation **obligatoire** (pot-de-vin selon casier/étoiles, sergent ami plus tard, refus = délit) ; prison (amende, armes confisquées, casier, 6 h, réveil au poste, sauvegarde) ; autos de patrouille à 3★ qui **suivent les rails** vers le joueur (feux brûlés, sortie vers lui) et foncent de près, agents qui descendent ; tirs à 3★ ; −1★ en changeant de char hors de vue ; affiches « Recherché » sur les façades à 2★ ; blips bleus, étoiles qui clignotent ; **mode TRACE** (idée de Martin) : le jeu dessine le trajet de chaque char et se surveille (chien de garde, tour en rond, hors voie) |
| M6 Missions et gang | **livré** | 13 sept. 2026 | — | ajout | `missions.py` : 6 personnages (une voix ElevenLabs chacun), **5 missions** (Ti-Guy, Mme Thibodeau, Marco, Sgt Bouchard, Josée) en objectifs typés, 35 répliques, 3 défis ; `histoire.js` : donneurs devant leur porte (ou à leur point dedans), **dialogues dits à voix haute** (chargés par mission, ducking radio/ambiance, voix « du combiné » au téléphone, le joueur écoute), **téléphone** (le donneur suivant appelle), machine à objectifs (aller/monter/livrer/tuer/ramasser/courses/semer/retourner), char de M1 dans une ruelle, fuyard en moto sur les rails (fuite), escorte de Ti-Guy, Cravates posées en ville, échec sur prison/hôpital, récompenses (bâton, rabais, sergent ami → pot-de-vin, bar, Faubourg libéré, manchette), **GPS** (blip, flèche au bord, distance), objectif en haut, **défis** à panneaux (saut, tour chrono, livraison sans bosse), gang qui attaque l'arme au poing sur son territoire |
| M7 Finition v1 | **livré** | 13 sept. 2026 | — | ajout | **5★** : hélico (te survole, rien ne retombe sous lui, ombre au sol, projecteur la nuit, rotor en boucle ElevenLabs) et **barrages** (deux autos-patrouille en travers devant toi, deux agents derrière) ; **journal lu par le narrateur** (9 manchettes + celle de M5, voix « annonceur centre d'achat 1 », version `lu` en casse naturelle) ; **marché noir** chez Josée après M5 (`magasins.MARCHE_NOIR`, −30 %) ; **carte de la ville** plein écran (N, ou PAUSE → CARTE : lieux, police, objectif, joueur) ; sonnerie de téléphone réelle ; sonde de performance Playwright (ms par image de nuit à 3★ au volant). Défi du jour à graine serveur : reporté en v2 |
| **v1 complète** | **livrée** | 13 sept. 2026 | — | — | M0 → M7 en ligne, 308 tests ; la suite est planifiée ci-dessous (« La v2 — huit vagues ») |
| M8 Les cinq districts | **livré** | 13 sept. 2026 | — | ajout | la ville passe de 157×112 à **421×213 tuiles** (5,1 ×) : Les Érables (banlieue, Les Chevreuils), La Shop (industriel, Les Boulonneux), Les Quais (port, Les Morues), La Pointe (parc, Les Skateux) et **la baie** — une seule grille de blocs, un district par rectangle, aucune fusion par-dessus une frontière ; une rue dont tous les blocs voisins sont de l'eau est **noyée** (c'est ce qui ferme la baie et coupe le chenal), et **un pont** relie La Pointe ; 5 nouveaux lieux (dépanneur, Hôtel Bandini, cantine des Quais, usine Prévost, phare) ; 4 gangs + 4 passants de quartier (`districts` les enferme chez eux) ; densité **et rythme** par district (La Shop déserte la nuit, les Quais le matin) ; radios _10-4_ et _Radio-Traversier_ ; paquet **319 Ko bruts / 33 Ko gzip**, `generer()` 94 ms au démarrage, **0,29 ms par image** de nuit à 5★ (0,26 avant) ; chien de garde du trafic corrigé (480 images de feu rouge **puis** l'attente de boîte faisaient 600 : il mordait un char sage) |
| Manette réapprenable | **livré** | 13 sept. 2026 | — | **correctif** | retour de Martin (« les boutons de la manette bluetooth ne sont pas bien mappé ») : les numéros de boutons d'une manette que le navigateur ne reconnaît pas (`mapping: ""`) ne veulent rien dire — la même manette n'a pas les mêmes numéros sur le téléphone et sur le Mac, **ça ne se devine pas**. OPTIONS > **MANETTE** : des **dispositions à choisir** (`app/manettes.py` : Xbox/PlayStation, **8BitDo en Bluetooth**, Bluetooth croix-sur-un-axe) et un **dessin de manette en pixels** qui sert de **preuve** — on appuie, la pièce s'allume ; au bon endroit, c'est la bonne disposition. Le dessin s'allume par **numéro de bouton**, pas par action : l'épaule droite et le bouton de gauche font la même chose et doivent pourtant se distinguer. ⚠️ Sur cet écran la manette ne **ferme** plus le menu (`manetteInerte`) — on y appuie sur ses boutons pour les voir, pas pour commander — mais elle peut encore bouger le curseur et choisir, sinon un joueur qui n'a qu'une manette resterait enfermé. Deuxième écran, RÉAPPRENDRE : ce que la manette dit d'elle-même (nom, RECONNUE / NON RECONNUE, boutons enfoncés et axes qui bougent en direct), une ligne par action qu'on réapprend en l'appuyant, la croix en quatre gestes, gaz et frein en **bouton ou en axe** (repos mesuré : une gâchette-axe repose à −1 sur une manette et à 0 sur la suivante), TOUT RÉAPPRENDRE qui enchaîne, PAR DÉFAUT ; gardé dans les options. **Croix-chapeau** : sur une 8BitDo en Bluetooth la croix n'est pas quatre boutons mais UN axe — on appuie et aucun numéro ne s'allume, elle a l'air morte ; on apprend HAUT et DROITE et le tour des huit positions se déduit, diagonales comprises (sinon repli sur les quatre côtés). L'écran liste les **axes qui bougent**, nomme un bouton **que la disposition ne connaît pas** (sinon il n'allume rien et on croirait la manette morte), et souffle le mode Xbox aux 8BitDo (le dongle 2,4 GHz ou le câble : c'est là que le navigateur les reconnaît). ⚠️ **Mesure de Martin** : ses gâchettes ouvraient la carte et la pause — or carte et pause sont 8 et 9 sur une manette reconnue, donc ses gâchettes _sont_ 8 et 9, et toute la numérotation DirectInput suit (boutons de droite 0/1/3/4, épaules 6-7, SELECT/START 10-11). Un juge garde ce fait : le « corriger » effacerait le retour. ⚠️ Un apprentissage **attend qu'on relâche** : sur un axe, lâcher le haut bouge autant qu'appuyer sur le bas, et la direction suivante s'apprenait sur la valeur du repos — la croix tenait alors les quatre directions en permanence. Corrigé au passage : `annuler` n'avait **aucun** bouton (le bouton de droite fait RETOUR), et « Jouer » n'était qu'un bouton de la page — on commence maintenant la partie à la manette ou au clavier |
| Le son retenu | **livré** | 13 sept. 2026 | — | **correctif** | retour de Martin (« regarde pourquoi je n'ai pas de son ») : un `AudioContext` naît **suspended** tant que la page n'a reçu aucun **vrai geste** (clic, touche, toucher), et `resume()` est alors refusé — or **l'API Manette ne compte pas comme un geste**. Depuis qu'on peut commencer la partie au pad (0.16.0), un joueur à la manette traversait donc toute la ville en silence, et le refus était avalé par un `.catch()` vide : **rien** ne le disait. ⚠️ La panne n'était ni dans les fichiers (79 mp3 servis en 200) ni dans le serveur (le paquet annonce bien ses 20 échantillons) ni dans le code du son — elle était dans **la permission du navigateur**, qu'on ne pensait même pas à demander. `Son.etatSon()` distingue maintenant quatre silences très différents : `actif`, `attente` (il manque un geste), `coupe` (choix du joueur, OPTIONS) et `absent` (pas d'audio du tout — le banc) ; un bandeau sur l'écran titre dit quoi faire **avant** qu'on joue, un message le redit si on commence quand même au pad, et OPTIONS porte une ligne **SON** qui n'est pas un réglage mais un **diagnostic** — sans elle, on cherche la panne dans ses haut-parleurs. `resume()` étant asynchrone, l'état revient par `onstatechange`, sinon le bandeau resterait affiché alors que le son est revenu. ⚠️ Le banc a maintenant un **faux AudioContext** (`o.brancherAudio(false)`) qui refuse `resume()` : c'est le seul endroit où l'on peut reproduire le silence à volonté — et le vrai Chromium des tests le confirme, il charge la page avec un contexte `suspended` |
| Devantures et graffitis | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« ajoute des façades distinctes et vraiment commerciales, pour les commerces et avec du lettrage et pancartes ; ajoute des graffitis sur certains bâtiments »). Avant, tous les commerces étaient le même mur percé d'une porte : on savait qu'un bâtiment était un commerce parce que le générateur le disait, pas parce qu'on le voyait. **118 devantures** (`app/devantures.py`) — un BANDEAU sombre, le NOM en lettres pixel (la police 3×5 du HUD, 4 px par lettre : 16 caractères sur quatre tuiles), un AUVENT rayé, une VITRINE au pied du mur et une PANCARTE qui dépasse sur le trottoir. Sept familles de couleurs (bouffe, service, artisan, nuit, commerce, marine, industrie) et **des noms par district** : une poissonnerie aux Quais, un atelier de soudure à La Shop, une garderie aux Érables — un juge interdit de les mélanger, sinon les cinq districts redeviennent le même quartier repeint. Les lieux garantis portent leur vraie enseigne (CHEZ GUS, LE BROUILLARD, CHEZ TI-PAUL) ; ⚠️ **la planque n'en a pas** — une planque avec son nom sur le mur n'est plus une planque. **54 graffitis** : les gangs signent **chez eux** (voir « CRAVATES » sur un mur apprend au joueur chez qui il est, sans un mot de HUD — un juge vérifie qu'aucun nom de gang ne traîne hors de son territoire), les autres taguent ROCCO, ICITTE, PAS DE JOBS. ⚠️ **Deux règles portent tout le reste.** (1) Une devanture est une **couche peinte** : elle ne déplace aucune tuile et ne change aucune solidité (elle transforme des `F` en `W`, qui ont exactement la même) — un juge garde cette frontière, parce que la violer ferait tomber les juges de circulation trois fichiers plus loin. (2) Elle tire dans **son propre dé** : avec le dé commun, choisir un nom d'enseigne décalait toute la suite du hasard et déplaçait des arbres à l'autre bout de la ville (deux tests de banc sont tombés là-dessus). Le dessin vit dans le **morceau de décor**, cuit une fois : une rue commerçante ne coûte pas une image de plus — et une enseigne à cheval sur deux morceaux est rangée dans **les deux**, sinon le nom est coupé net au milieu d'un mot. Chaque devanture pose une **lueur de vitrine** (basse, courte, chaude) : sans elle tout ce travail disparaissait la moitié du temps de jeu. 25 juges Python + 5 de banc ; rythme **0,7 ms** par image de nuit à 5★ (0,6 avant), paquet **341 Ko bruts / 35 Ko gzip**. ⚠️ **On voit toujours une porte** (retour de Martin) : le bandeau, l'auvent et la vitrine couvraient toute la bande — on lisait le nom du commerce et on ne voyait plus par où entrer. La devanture porte donc `motifs`, une lettre par tuile, qui dit au peintre ce qu'il y a dessous : `W` vitrine, `D` porte qu'on ouvre, `d` condamnée, `G` garage, `P` porte **peinte**. Une porte garde toute sa hauteur (pas d'auvent ni de vitrine par-dessus), et **celle où l'on peut entrer se reconnaît de loin** : vitre claire, poignée dorée, rai de lumière au seuil — les autres sont sombres, planches en travers pour les condamnées. Un tiers des bandes n'avaient **aucune** ouverture (le bâtiment avait tiré « pas de porte ») : on en peint une (`P`) sur la tuile qui donne sur le trottoir, sans toucher au sol — elle ne promet donc rien qu'on ne tienne. 11 juges de plus, dont un qui vérifie que `D` correspond à une **vraie** porte du catalogue : peindre une poignée dorée sur un mur serait une promesse qu'on ne tient pas. 473 tests |
| Musique du menu | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« s'il n'y en a pas je veux aussi une musique au menu d'accueil ») : il n'y en avait pas — `Mus` était resté l'ébauche de M7 (trois lignes). ⚠️ Le thème est **écrit en notes**, pas enregistré (`app/musique.py`) : un mp3 de menu pèserait plus que tout le paquet réuni, coûterait des crédits à générer et ne se **testerait** pas, alors que 2 Ko de notes se relisent, se corrigent à la note près et se jugent. _Baie-des-Brumes_ : 92 bpm, la mineur, une grille de huit mesures qui tourne (Am7 Dm7 G7 Cmaj7 Fmaj7 Bm7b5 E7 Am7 — le tour de chant le plus banal du jazz, **et c'est voulu** : il doit tourner sous un menu sans jamais accrocher l'oreille), quatre voix (basse marchante, nappe, chant sur seize mesures qui ne se répètent pas, balai sur le contretemps), boucle de 42 s. `Mus` est maintenant un vrai séquenceur : il pose les notes sur **l'horloge audio** avec un quart de seconde d'avance, jamais sur les images — sinon un à-coup d'affichage troue la mesure. ⚠️ Il ne programme **rien** tant que le son n'est pas accordé (voir « Le son retenu ») : dans un contexte suspendu l'horloge est figée, et toute la boucle sortirait d'un bloc à la seconde où le joueur touche l'écran. 13 juges Python (aucune note hors du clavier, aucune qui déborde de son motif — elle ne jouerait **jamais**, aucun chevauchement dans une voix, volumes cumulés sous l'écrêtage, la boucle finit sur un la) + 7 de banc (le rythme tombe sur un multiple exact du pas, la boucle reboucle sur la même note, le menu se tait quand la partie commence). `scripts/musique_apercu.py` rend un morceau en WAV sans lancer le jeu : une note fausse s'entend là plutôt qu'en ligne. Paquet **322 Ko bruts / 32,5 Ko gzip** (+2 Ko) |
| Aucun son n'a jamais joué | **livré** | 13 sept. 2026 | — | **correctif** | retour de Martin (« j'ai le son de la page titre, mais rien ensuite ») — et c'était bien pire que ça. Dans `echantillon()`, **`source.connect(gain)` manquait** : la source n'entrait dans aucune chaîne. Tout le reste était juste — le fichier se téléchargeait (200), se décodait (tampon de 0,68 s, pic 0,22), la source démarrait, le gain était au bon volume **et** relié au maître. Aucune erreur, aucun 404, aucune trace : **aucun des 79 fichiers ElevenLabs n'a jamais été entendu** — ni un bruitage, ni une voix, ni une radio, ni l'ambiance. ⚠️ Et le filet de synthèse ne prenait pas le relais, parce que `joue()` rend `true` dès que l'objet existe : ni échantillon, ni repli, **silence**. Deux pannes se masquaient l'une l'autre — le son retenu par le navigateur empêchait de découvrir celle-ci, et la musique du menu (de la **synthèse**, elle) l'a révélée en sonnant seule. ⚠️ Ce qui manquait, ce n'était pas un test de plus mais un test d'une autre **nature** : tous nos juges vérifiaient l'intention (fichiers servis, tampons décodés, sources démarrées, volumes justes) et tous étaient verts. Désormais on écoute la **sortie** : au banc, le faux AudioContext trace ses branchements et `atteintLaSortie(noeud)` exige un chemin jusqu'à la destination (3 juges, vérifiés en remettant le bug) ; au navigateur, un `AnalyserNode` posé sur la sortie mesure ce qui sort vraiment (3 juges : la synthèse, un échantillon, l'ambiance, le thème). Mesures après correctif : échantillon −35,7 dB (avant : **silence**), ambiance −25,8 dB, et l'écart menu/jeu retombe de **136 dB à 2,6 dB**. ⚠️ **La même soudure manquait une seconde fois**, dans `Voix.parler()` : retour de Martin (« je n'entends pas les voix des gens dans les dialogues »). Les 44 répliques se chargeaient, `enCours` se posait, la radio baissait, le texte défilait — et rien ne sortait ; un juge existant vérifiait même que la réplique « se décode et baisse la radio », et il était vert. D'où un juge d'une portée plus large que les deux cas connus : `ctx.sourcesMuettes()` au banc recense **toute** source qui a démarré sans atteindre la sortie, quel que soit le chemin — on fait sonner bruitages, boucles, musique, répliques (dont une au téléphone, qui a un filtre de plus) et on exige zéro. Les deux bugs ont été remis exprès pour vérifier que les juges tombent. ⚠️ Effet de bord découvert au passage : ouvrir un `AudioContext` dès le chargement (pour savoir si le son est accordé) en laisse un ouvert par page — le navigateur en limite le nombre, et la suite navigateur devenait instable ; `Son.fermer()` sur `pagehide` rend la carte son. Et `Son.estCharge(slug)` répond « ce son est-il prêt ? » sans le **jouer** : les attentes de test le faisaient en démarrant une source à chaque sondage, jusqu'à faire caler le contexte |
| Les filles de la Brume dans la foule | **livré** | 13 sept. 2026 | — | **correctif** | retour de Martin (« on ne distingue plus les prostituées, elles sont trop pareilles que tout le monde ») : elles n'étaient qu'un **échange de palette** sur le corps commun — un chandail rose voisin de celui de la passante, des cheveux noirs comme la moitié du catalogue — et à **douze pixels de large**, sous la teinte de nuit, une couleur ne distingue rien. ⚠️ Ce qui se reconnaît à cette taille, c'est un **contour** : `SPRITES.racoleuse` est le **seul archétype de piéton à avoir son propre dessin** (jupe évasée **plus large que les épaules** — personne d'autre dans le jeu, jambes nues sous l'ourlet, talons, cheveux qui tombent de chaque côté du cou, blond platine que personne ne porte ; trois vues, trois images de marche, et la pose `couche` **sans laquelle un KO serait resté debout**). Rien de plus ne se montre : c'est une silhouette, pas une tenue. Deuxième signe, lu avant même la robe : elle **tient son coin** (`poste` à la naissance, rayon de 3 tuiles) — elle s'arrête deux fois plus souvent que les autres et revient vers son lampadaire, là où elle se remettait à flâner comme tout le monde dix secondes après être apparue ; ⚠️ une flânerie dure jusqu'à 330 images, alors elle **redécide toutes les 30** — sinon elle était à l'autre bout de la rue avant de seulement songer à revenir (mesuré : 56 px d'écart maximum en 40 s, contre 224 px pour une passante). Troisième signe, à bout de bras : l'invite ACTION la **nomme** (« LA BRUME — 60 $ ») — `interagir` la servait déjà mais `majInvite` l'avait oubliée, on appuyait sur ACTION en espérant que c'en était une ; une seule fonction (`filleSousLaMain`) sert les deux, pour que le HUD ne promette jamais autre chose que ce qui va se passer. 4 juges (le contour s'évase et le corps commun non, ses couleurs ne se recroisent nulle part dans le catalogue, elle tient son coin quand la passante s'en va, le HUD la nomme et se tait quand elle est partie) |
| Rien ne se chevauche plus | **livré** | 13 sept. 2026 | — | **correctif** | retour de Martin, capture à l'appui (« empêche que les choses se chevauchent ») : le joueur **debout dans la carrosserie** du camion-restaurant. Deux chevauchements, deux causes. ⚠️ **Le décor** : la collision n'était pas absente, sa **forme** était fausse. Un camion-restaurant fait 44 px de large et 8 px de profond ; son unique cercle (r 16) tenait dans la profondeur, donc il laissait **6 px de carrosserie** libres de chaque côté — et le cercle qui aurait couvert la largeur (r 22) aurait posé un mur invisible de 22 px devant et derrière. Un cercle ne sait pas tenir un rectangle. Chaque décor carré porte maintenant une **boîte au sol** (`sol: [demi-largeur, demi-profondeur]`, mesurée sur les `fillRect` de son peintre) dont on ressort par le côté le moins enfoncé : banc, caisse, fontaine, les deux kiosques, la roulotte, le camion. L'arbre, lui, **garde son cercle** : son tronc fait 3 px et sa cime est peinte en hauteur — on passe sous une cime, pas dans un comptoir (même raison pour le parasol du kiosque à hot-dogs). ⚠️ **La foule** : personne ne poussait personne. Deux passants qui se croisaient se superposaient **exactement** — mesuré en marchant deux minutes : **1032 paires** enfoncées l'une dans l'autre en 960 images, jusqu'à **9,9 px**, soit deux corps de 10 px parfaitement confondus. `demeler()` sépare maintenant tout le monde à chaque image, sur un index **refait** (celui du début d'image est périmé : il laissait passer exactement les paires qui venaient de se rejoindre), en poussant par `deplacerCercle` — sinon on se pousse mutuellement **dans un mur**, ce qui est pire. Après : **0,1 px** au pire, dès la première image. ⚠️ Et l'on ne **naît** plus dans quelqu'un : les deux branches de `placeDeNaissance` rendent un **centre de tuile**, donc deux naissances sur la même tuile, c'est le même pixel (deux agents nés l'un dans l'autre à l'image 31). ⚠️ Le plafond de séparation doit passer **devant les jambes les plus rapides** : fixé à 1,5 px il arrêtait bien le joueur qui **marche** (1,2) et laissait passer celui qui **sprinte** (2,1) — il suffisait de tenir MAJ pour entrer dans le vendeur ; il se calcule désormais sur les vitesses du paquet. ⚠️ Et « figé » veut dire **il tient son poste**, pas **c'est un poteau** : vraiment immobile, un donneur planté sur le trottoir bouchait la rue **pour toujours** — l'agent lancé aux trousses du joueur venait buter sur Ti-Guy et y restait (260 images sur place, l'arrestation n'arrivait jamais). Il se laisse donc bousculer de 10 px et **rentre chez lui** ; au-delà il redevient un mur, sinon on promènerait un personnage d'histoire jusqu'au port. 6 juges (on ne se tient dans aucun décor par aucun des quatre côtés, la portée de recherche couvre le **coin** de la plus grosse boîte — sinon le camion n'est même pas trouvé et rien ne rougit —, la foule ne se chevauche plus et ne naît plus empilée, courir ne traverse pas les gens, le figé cède puis revient). Coût : **0,337 → 0,356 ms par image** à 5★ avec 1992 entités |
| La voix au téléphone qu'on n'entendait plus | **livré** | 13 sept. 2026 | — | **correctif** | retour de Martin (« les voix au téléphone ne sont pas assez forte ») : ce n'était pas une question de **volume** mais de **filtre**. Le combiné était un seul `bandpass` à 1,5 kHz (Q 1,2) — bien plus pincé qu'un vrai téléphone, 6 dB par octave de chaque côté. Or c'est **sous 900 Hz** que la parole porte le gros de sa puissance : mesuré, la voix au combiné sortait à **−6,5 dB à 500 Hz** et **−11 dB à 300 Hz**, donc **plus bas qu'en direct**, et les 1,6× de compensation étaient loin du compte. C'est maintenant la **vraie bande téléphonique** (300 Hz – 3,4 kHz), dessinée par un passe-haut puis un passe-bas qui laissent **plat** tout ce qu'il y a entre — et 2× de compensation, parce qu'une voix coupée de ses graves s'entend moins fort à puissance égale et qu'un appel se prend au milieu des moteurs. Après : **+8,1 dB à 500 Hz, +7,6 dB à 1 kHz, +7,7 dB à 3 kHz** — de +4 à +18 dB selon la fréquence, et le combiné passe **au-dessus** de la voix en direct sur toute la bande de la parole. ⚠️ Encore un test d'une autre **nature** : les juges existants vérifiaient que la réplique au téléphone **atteint la sortie** (elle l'atteignait, la chaîne était branchée, la source démarrait) — atteindre la sortie ne dit rien de ce qui **en sort**. Les 2 nouveaux ne lisent pas les réglages, ils **calculent** la réponse réelle de la chaîne (formules RBJ, celles que le Web Audio implémente) en suivant les branchements du gain jusqu'au maître : le combiné doit sortir au-dessus du direct sur toute la bande de la parole, et cette bande doit rester plate à 6 dB près. Remis l'ancien filtre, ils tombent (12,7 dB d'écart : « le combiné pince trop ») |
| Manger, boire, courir | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« il faut que la bouffe redonne de l'énergie et le café permet de courir plus longtemps ») : un kiosque ne rendait que des **PV**, et le souffle (`endurance`, 100 points, 0,4 par image au sprint) ne se refaisait **qu'en arrêtant de courir** — autrement dit, les quatre commerces de trottoir ne servaient à rien à la seule minute où l'on en a besoin, celle où la police est derrière. Manger rend maintenant les deux (`*_souffle` dans `economie.TARIFS` : hot-dog +40, poutine +70, café +30), et ce qui coûte plus cher nourrit plus, en vie **comme en jambes**. ⚠️ **Le café n'achète que de la DURÉE.** Pendant 90 s (`economie.CAFE`) le sprint ne coûte que la **moitié** : 4,2 s de course d'une traite deviennent 8,4 s. Sa vitesse, elle, ne bouge pas d'un pixel — les 2,1 du sprint contre 1,9 au policier et 1,35 au fuyard sont ce qui rend une poursuite **gagnable des deux côtés** ; y toucher pour 4 $ aurait cassé toutes les poursuites du jeu d'un coup, alors un juge mesure la distance par image sous café et la refuse si elle change. ⚠️ C'est une **minuterie, pas une dépense** : elle s'écoule dans `Missions.maj` (donc aussi au volant et dans une pièce, là où `majJoueur` ne passe pas), elle ne s'**empile** pas (un deuxième café repart le compte — sinon on s'achète l'endurance infinie à 4 $) et elle ne survit ni à la nuit ni à l'hôpital. ⚠️ Et elle **se voit** : la barre d'endurance passe au vert et clignote la dernière seconde, parce qu'un souffle long qui s'arrête au milieu d'une fuite sans rien annoncer se lit comme une panne. Le **casse-croûte sert le café** lui aussi : la roulotte du trottoir ferme de 14 h 24 à 4 h 48 et elle était le seul endroit du jeu où courir plus longtemps s'achetait. 4 juges Python (la bouffe rend du souffle sans faire déborder la barre, la poutine vaut son prix, le café n'achète que de la durée et dure plus qu'un plein de souffle, seul le café réveille) + 2 de banc (manger remonte le souffle et ne déborde pas, un hot-dog ne réveille pas ; sous café on tient **deux fois plus d'images à la même vitesse**) |
| Des commerces, du monde qui habite, des vrais intérieurs | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« beaucoup plus de variété de commerce ou bien enlever certaines devantures pour remplacer par des résidences ; ajouter des appartements à étage ; améliorer les intérieurs, car présentement il n'y a jamais rien, seulement des comptoirs vides ; ajoute aussi des intérieurs pour plusieurs types ; valide les missions qui doivent avoir des choses à l'intérieur ») : **142 noms d'enseigne** au lieu de 56 (14 à 48 par quartier) et **trois familles de plus** (santé, mode, savoir) ; `choisir_enseigne` refuse le même nom à moins de **40 tuiles** — La Shop affichait sept fois « FERRAILLE ». **74 immeubles à logements** remplacent 20 devantures et habillent les quartiers d'habitation : une couche peinte comme les enseignes (zéro solidité touchée), **1 à 3 étages** de fenêtres, balcon, **escalier de fer** sur le trottoir, et une fenêtre sur trois allumée la nuit. Les **29 intérieurs** sont maintenant **dessinés à la main** (un plan par pièce, l'espace = le plancher) avec **onze meubles** (comptoir, étagère, table, chaise, lit, frigo, machine, plante, classeur, poêle, escalier) et **trois planchers** (bois, céramique, tapis) — et du **monde dedans** : un commis à son poste, des clients tirés dans les passants du quartier. **Un commerce ordinaire sur cinq s'ouvre pour de vrai** (42 portes au lieu de 16) : dix pièces génériques, une par famille de devanture, et le **nom de l'enseigne voyage sur la porte** — on entre chez « TABAGIE DUBOIS », pas dans « Boutique ». Nouveaux comptoirs : `emplettes` (`magasins.COMPTOIRS`, data), `salon` (le barbier change tes cheveux **et fait oublier ta tête à la police**), `escalier` (l'étage du plex et la chambre de l'hôtel), `fouiller` (les tiroirs d'un logement, une fois par adresse), `casier` (le carnet du poste). ⚠️ **Trois comptoirs étaient morts** (`guichet`, `sortie_prison`, `casier` : un libellé, aucun menu, « PLUS TARD ») — un juge du banc compare maintenant ce que `carte.INTERIEURS` dessine à ce que `missions.js` sert, et seul le comptoir de la fourrière reste en chantier (il appartient à M9). ⚠️ **Un meuble ne remplit pas sa tuile** : sans plancher peint dessous, chaque table était un trou **noir** — `plancher` voyage donc avec la pièce. **125 juges de plus** (`test_interieurs.py`, `test_interieurs_js.py`, et les logements dans `test_devantures.py`) |
| Les transitions des portes | **livré** | 13 sept. 2026 | — | **correctif** | retour de Martin (« la transition n'est pas juste ») : elle ne l'était pas parce qu'elle arrivait **dans le mauvais ordre** — `entrer()` chargeait la pièce, _puis_ lançait le fondu, dont la première moitié noircissait donc sur la scène déjà changée. Ce n'était pas un fondu enchaîné, c'était un clignotement. `Jeu.transiter()` remet l'ordre : **noircir sur l'ancienne → changer au noir → éclaircir sur la nouvelle**, le jeu **figé** pendant (un char ne te renverse plus sur un écran noir), des durées **asymétriques** (entrer 46 images, sortir 26), la caméra posée au noir sur la cible que l'amorti viserait, la porte qui s'entend au noir, et un reste d'élan au pas de la porte. 3 juges de banc : la scène mesurée **à chaque image**, le gel (ni temps, ni passant, ni char), et sortir **pendant** le fondu d'entrée |
| Les clôtures : grillage, bois, barbelé | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin (« il faut des clôtures, mais si elles ne sont pas barbelées, qu'on puisse passer par-dessus », puis « ajoute aussi des clôtures de bois pour la variété ») : on passait par-dessus **toutes** les clôtures — sans même ralentir, parce que `f` était solide 3 et que le masque des piétons ne la voyait pas. Elles ont maintenant leur solidité à elles : **4 s'enjambe** (grillage, palissade de bois — 48 images en haut, immobile, sans frapper ni courir), **5 ne se passe pas** (barbelé). Franchir est une capacité de **tout le monde**, au même prix : l'A\* des agents traverse le grillage à 5 tuiles de coût et l'agent l'enjambe pour de vrai — une poursuite ne se gagne pas en escaladant. Du barbelé dans les cours de gang et de La Shop, du grillage à la fourrière (décision) et sur les terrains vagues, **de la palissade de bois dans les cours arrière des Érables** (188 tuiles). 6 juges neufs |
| Enfermé dans six commerces | **livré** | 13 sept. 2026 | — | **correctif** | bug de Martin (« chez Ti-Paul, impossible de sortir ») : `utiliserPoint` passait **avant** la porte et attrape tout point à 1,6 tuile — or il n'y a qu'une tuile d'où sortir, et il rend `true` même quand il n'a qu'un « PLUS TARD » à dire. **Deux corrections, et il fallait les deux** : la porte passe maintenant avant le comptoir (un comptoir se sert d'un pas de côté, une porte non), et un **juge Python** interdit tout point d'action à moins de `RAYON_POINT` (1,6 tuile) de la tuile de sortie — il rougissait six fois le jour où il a été écrit. Les six pièces se sont redessinées (le comptoir recule, le journal du dépanneur s'en va contre son mur). 3 juges neufs, dont un qui **remet le piège à la main** |
| Clôtures nord-sud couchées | **livré** | 13 sept. 2026 | — | **correctif** | bug de Martin : les trois peintres ne dessinaient que l'est-ouest, donc une clôture verticale était une pile de panneaux vus de face. Elles lisent maintenant leurs voisines (`varianteDeCloture` : un masque des quatre côtés où la clôture continue) et se peignent en **bras** — le même code pour les trois, avec les deux axes échangés en nord-sud, un poteau au centre à chaque coin et à chaque bout. Le juge compare les **deux cuissons trait par trait** : le nord-sud doit être l'est-ouest tourné |
| La carte | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin (« un icône clignotant pour savoir où on est, une légende, savoir où est la mission en cours ») : le joueur **était** dessiné — un carré blanc de 2 px, lisible sur le Faubourg de 157×112 et perdu depuis que la ville fait 421×213. Il **pulse** maintenant (un anneau qui s'ouvre et se referme, 40 images) et ne disparaît **jamais** — on ne cache pas ce qu'on cherche ; l'objectif bat à un autre rythme (16) et dans une autre forme (un losange doré). Hors du cadre de la mini-carte, il devient une **flèche** au lieu d'une position bornée au coin, qui mentait. Et la **légende** se construit depuis la table des couleurs, descendue de Python (`FAMILLES_DE_LIEU`, 8 familles) : les seize lieux ont tous une couleur **déclarée**, là où `COULEUR_BLIP` en connaissait dix et laissait six au gris. 4 juges neufs |
| Les donneurs qu'on ne voyait pas | **livré** | 13 sept. 2026 | — | **correctif** | bug de Martin (« je n'arrive pas à faire la mission sergent Bouchard, je vais à la cantine, mais je ne vois pas quoi faire ») — et il avait raison deux fois. D'abord le **nom** : Marco l'envoie au « casse-croûte » (le Faubourg, à côté du poste), pas à la **Cantine des Quais**, un autre bâtiment à l'autre bout de la ville. Ensuite, et c'est le vrai bug : **Bouchard et Josée n'existaient nulle part**. Ce sont les deux seuls donneurs qui se tiennent DEDANS (`ou: point:sergent`, `point:contact`), et `creerDonneurs()` ne posait que ceux de la rue (`porte:`) : on poussait la porte, la salle était vide, et il fallait deviner qu'un **point invisible** attendait au fond à droite. Ils sont maintenant **posés en entrant** (`creerDonneursDedans`, appelée par `Jeu.entrer` juste après le commis et les clients), ils naissent et meurent avec la pièce comme tout le monde, et la table Python→piece ne se recopie plus en JS : `personnageDuPoint` / `pieceDuPoint` la **déduisent** du `ou` de `missions.py`. ⚠️ Josée pointe une **table** (personne ne se tient debout sur une table) : `placeDebout` prend la tuile libre voisine la plus proche du milieu de la pièce — le fond d'un coin, ce n'est pas une scène. ⚠️ Le GPS a fallu le corriger du même coup (`ouTrouver`) : dedans, un donneur vit en coordonnées de **pièce**, et le poser tel quel sur la minicarte envoyait la flèche à six tuiles du coin de la ville. Et une **bulle de bande dessinée** dit qui attend après toi — voir la ligne suivante. ACTION dedans vise maintenant **la personne avant le comptoir**, et le HUD la nomme (« PARLER À SERGENT BOUCHARD »). 2 juges de banc (on entre, quelqu'un est là, debout hors des meubles, à portée de son point, et il parle ; il ne suit pas dans la rue) |
| Les bulles qui interpellent | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« avec une petite bulle de type bande dessiné qui nous interpelle ») : le jeu avait déjà deux pastilles de 8 px au-dessus des têtes — le « ! » du témoin, le trait de la peur (`cri`). Elles disent un **état d'esprit** ; elles ne peuvent pas dire un **mot**, et c'est le mot qui manquait. `Entites.bulle(e, texte, {duree, fond, encre})` pose une boîte à queue au-dessus de **n'importe quelle entité** (police 3x5, coins coupés, la queue sur la tête de celui qui parle, une montée de 6 images puis une respiration), `Entites.taire(e)` l'efface, et elle se dessine dans une **deuxième passe**, après tout le monde : dans une pièce, un client passe devant le donneur une fois sur deux, et une bulle à moitié cachée par une nuque ne se lit plus. ⚠️ Le texte **ne s'invente pas en JS** : `personnages[].heler` dans `missions.py`, comme toutes les répliques du jeu, court par force (`HELER_MAX`) et vérifié par un juge. ⚠️ Une bulle qui ne s'éteint jamais ne veut plus rien dire : elle ne s'allume que si **ce donneur-là** a une job pour toi (ou t'attend pour la finir), elle se tait pendant sa propre mission, et **aucune** bulle ne s'affiche pendant un dialogue — quelqu'un te parle déjà, en bas de l'écran. Deux emplois pour l'instant : les **cinq donneurs** et le **client du taxi** de M3, qui levait le bras au bord du trottoir sans rien dire. 1 juge Python (chaque donneur a son mot, assez court), 1 de banc (elle s'allume sur le bon donneur, s'éteint après, et vit d'une image à l'autre), 1 dans le taxi ; vérifié à l'écran dans un vrai navigateur (casse-croûte, bar, terminus) |
| Le souffle en surplus | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin (« les choses qui donnent du souffle devraient donner un **bonus**, parce que le souffle monte seul ») : il remontait de 0,24 par image — une barre vide pleine en **7 s** — et `nourrir` plafonnait à 100, donc une poutine à 18 $ rendait 70 points qu'on avait gratuitement en s'arrêtant quatre secondes. Manger ajoute maintenant **par-dessus** les 100 (plafond 60) : le surplus **part en premier** au sprint, ne remonte **jamais** tout seul, et se perd en dormant, à l'hôpital et en prison. À l'écran, une ligne cyan d'un pixel **posée sur** la barre — elle garde sa couleur sous café (barre verte) et **disparaît au volant**, où la barre montre la carrosserie. Son plafond est un réglage de **poursuite** : 60 points = 2,5 s de sprint de plus, 5 s sous café, et un juge refait le calcul. 2 juges neufs |
| Les toits | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin (« je veux que les toits soient plus réalistes ») : ils étaient peints **tuile par tuile**, chacune ignorant les autres — une texture, pas un toit. Ils ont maintenant un **bord** (parapet clair + ligne d'ombre, lu dans le voisinage comme les passages piétons), un **grain** qui varie de tuile en tuile, une **couverture par genre** (`COUVERTURES` : deux versants en banlieue, tôle et gravier à La Shop, ardoise en ville) que **deux voisins collés ne partagent jamais** (sans quoi il n'y a pas de bord à trouver entre eux), des **versants** avec leur ligne de faîte — comptés dans les voisines, zéro donnée de plus —, **172 équipements** (ventilation, climatisation, cheminée, cage d'escalier, réservoir, antennes) qui voyagent dans le paquet comme les enseignes, et une **ombre portée** sur la rue qui donne d'un coup de la hauteur à la ville. 4 juges neufs ; paquet à 368 Ko bruts / 41 Ko gzip |
| Le fondu de l'hôpital et de la prison | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin (« il faut corriger le fade out et in quand on va à l'hôpital ou qu'on se fait enfermer ») : quatre changements de scène — l'hôpital, la prison, la compagnie, le coucher — étaient restés sur `Hud.fondu` + `setTimeoutJeu`, soit **deux horloges** que rien ne liait : l'une comptait dans le dessin, l'autre dans la mise à jour. On se regardait donc disparaître de la rue à **80 % de noir**, le texte se lisait par-dessus le trottoir où l'on venait de tomber, et la ville continuait de tourner pendant les deux secondes et demie — un char pouvait repasser sur un joueur à 1 PV. Les quatre passent maintenant par la machine des portes, `Jeu.transiter()`, qui n'a **qu'une** horloge et change la scène **pile** à alpha 1. Elle gagne pour eux un troisième nombre, `[fermer, tenir, ouvrir]` : une porte, on la passe ; une nuit, un séjour à l'hôpital **font passer du temps**, et ce temps se sent dans le noir tenu, où le texte s'écrit — et **seulement** là. `Hud.fondu`, `setTimeoutJeu` et leurs minuteries sont supprimés : plus une seule deuxième horloge dans le jeu |
| Des sirènes qu'on entend | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin (« je veux des sirènes pour les ambulances et polices ») : il n'y en avait **qu'une**, et presque jamais — `Son.boucle('sirene', …)` ne s'allumait que pour une auto-patrouille de l'IA en chasse, à volume fixe, sans distance. L'ambulance déclare pourtant `sirene: true` depuis M9 et n'en a **jamais** fait entendre une seule ; au volant, aucune des deux. Maintenant : **deux sons** (celle de la police monte et descend, celle de l'ambulance fait deux notes — les confondre, c'est ne pas savoir qui arrive derrière soi), un **volume qui suit la distance** (460 px de portée), une **ambulance sur trois** qui naît en course dans le trafic, et au volant d'un char à sirène le **bouton du klaxon devient celui de la sirène** — l'étiquette du bouton tactile le dit |
| Des bruitages qui ont encore leur aigu | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin (« améliore les effets spéciaux en qualité », puis « génère-les avec l'IA ») : les 24 bruitages étaient générés **à leur taille finale** (22 kHz, 32 kbit/s, stéréo), et c'était trois défauts d'un coup. ⚠️ **Presque plus d'aigu** : en comparant le pic du signal filtré à 8 kHz au pic du fichier entier, il restait **−26 dB** pour la caisse enregistreuse, **−27** pour la tôle froissée, **−30** pour le clic de menu, **−32** pour la porte. Or c'est là que vit le clinquant d'une pièce et le verre d'un phare : on payait une génération dont on jetait le haut **avant même de l'écouter**. Les mêmes sons sont aujourd'hui entre **−6 et −10 dB**. ⚠️ Le klaxon, la sirène et le moteur n'ont pas bougé — ils n'ont pas d'aigu à avoir, et le juge ne leur en demande pas. ⚠️ **Des niveaux au hasard** : les pics allaient de **−34 dB** (un pas) à **0 dB pile** (huit fichiers collés au plafond), donc le `volume` du catalogue ne dosait rien — il multipliait un accident. ⚠️ **Deux fichiers larges** (la porte, le refus : leurs deux canaux ne se ressemblent qu'à 1 dB près) — et un son déjà large ne se laisse plus placer par le `StereoPanner` de `son.js`, il arrive à gauche quoi qu'on lui demande. ElevenLabs rend désormais un **master** (`mp3_44100_128`) que `ffmpeg` ramène à la taille du jeu (`finir()`) : mono, normalisé au même pic (−1 dBFS), queue rognée puis fermée par un fondu de 15 ms, 96 kbit/s pour un bruit bref et 64 pour une boucle. ⚠️ **L'ordre des gestes est tout le problème** : rogner avant de normaliser — ce que j'avais fait d'abord — applique un seuil **absolu** de −45 dBFS à une génération sortie à −34 dB, donc **en plein milieu du son** ; mesuré : un pas réduit à 0,06 s puis remonté de +37 dB, il ne restait que le souffle. Normalisé d'abord, le seuil est toujours à 44 dB sous le pic. ⚠️ Une **boucle** ne se rogne ni ne se fond : c'est sa couture qu'on abîmerait, et le trou s'entendrait à chaque tour. Les `volume` sont recalculés pour **reproduire le mélange d'avant** (pic mesuré × ancien volume), sauf `pas` et `sonnette`, qui sortaient sous −23 dB une fois mixés — sous ce qu'on entend en jouant. Nouveau champ `influence` : haut pour ce qui doit être **une** chose exacte (un clic, un klaxon, une sirène), plus bas pour une matière (une explosion, une foule), où le modèle rend mieux quand on lui laisse de la place. **32 fichiers pour 21 sons** — `pas` passe à 4 variantes, `coup` et `touche` à 3, `choc`, `klaxon` et `ramasse` à 2. Le script **dénonce ses propres ratés**, et il a fallu deux essais pour qu'il dénonce la bonne chose : j'avais posé « plus de +20 dB de gain = génération ratée », ce qui est **faux** — ElevenLabs rend souvent un pas à bas niveau mais parfaitement propre, et le drapeau envoyait refaire, à crédits perdus, la meilleure prise du lot (`pas-2` demandait +29 dB **et** affichait le meilleur plancher des quatre, −47 dB). Ce qui compte est le **rapport signal/bruit du fichier fini**, pas le chemin pour y arriver : sous 30 dB, ça souffle, et `--refaire pas-2` refait **cette variante-là seule** au lieu des quatre. ⚠️ Et on ne voit le souffle **que quand le son s'arrête** : un buzzer de refus ou une auto qui passe remplissent toute leur durée, leur « plancher » est leur son (1 dB de RSB sur des fichiers impeccables) — sans un moment de calme, pas de verdict. Juges d'une autre **nature** que ceux du catalogue : ils ouvrent les octets (mono, 44,1 kHz, pic à −1 dBFS, pas de vide en queue, pas de souffle, et de l'énergie au-dessus de 8 kHz sur les deux sons les plus brillants). L'écart de niveau entre fichiers tombe de **34,4 dB à 1,8 dB**, ce qui reste étant celui de l'encodeur mp3. Poids : 184 Ko → **512 Ko** pour 32 fichiers, soit 551 Ko dans le seau que le juge plafonne à 600 — **il reste 49 Ko**, donc une variante de plus ne rentre pas sans relever le plafond ou baisser un débit. ⚠️ **Premier retour, et il valide la raison d'être du « en cours »** : Martin a écouté et « moto qui passe » était **un chien**. Le prompt disait « exhaust **bark** » — un mot d'argot de sonorisation est d'abord un cri d'animal, et le modèle l'a pris au pied de la lettre ; aucune mesure ne pouvait attraper ça, seule une oreille le pouvait. Prompt réécrit sans le mot (et `influence` remontée à 0,6 : sur ce son-là on ne laisse plus de place), son refait. ⚠️ Et le chien est **gardé** : `static/audio/reserve/` tient les générations ratées mais bonnes, hors catalogue — donc jamais téléchargées, jamais jouées. Ça ne tient qu'à un détail : `orphelins()` liste le dossier avec `iterdir()`, qui ne descend pas dans les sous-dossiers. Un juge garde cet invariant, pour que le jour où quelqu'un passera à `rglob()` ça se voie au lieu de réclamer la suppression de toute la réserve. Le chien jappera derrière une clôture quand viendront **les terrains de banlieue** (P4). ⚠️ **Ce qui a clos l'étape, c'est l'oreille de Martin**, pas un juge : aucun ne dit qu'un son est le BON son, seulement que la chaîne a tourné. Il a écouté le 13 sept. : la moto était un chien, la porte de commerce, la montée à vélo était un objet qu'on ramasse — les trois refaits (les deux derniers aux deux lignes suivantes), le reste tient |
| Trois portes qui ne sonnent pas pareil | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« change le bruit de porte et différencie le bruit de porte de maison, commerce et véhicule ; moto et vélo ont pas de portes ») : un seul grincement de bois servait au logement, au dépanneur, au taxi — et à la descente d'un vélo. Trois échantillons ElevenLabs à la place : `porte_maison` (la clé dans la serrure, le bois qui claque dans une cage d'escalier), `porte_commerce` (la vitre, le ferme-porte qui siffle), `porte_vehicule` (la portière qui claque). ⚠️ **Le genre vient de la fiche, pas du JS** : chaque pièce de `carte._piece` dit quelle porte on pousse (champ `porte`, « maison » pour les logements, la planque, la chambre d'hôtel et le phare, « commerce » ailleurs) et chaque char dit s'il a des portières (`vehicules.portieres`, vrai pour les classes auto et camion seulement). `Son.SFX.porte(genre)` choisit ; `Jeu.entrer`, `sortir` et `changerEtage` lisent la pièce, `vehicules.js` lit le char. Une moto et un vélo **s'enfourchent** : le cliquetis de `ramasse` à la montée comme à la descente, comme le vélo le faisait déjà à la montée. Le crochet de la remorqueuse et le client du taxi claquent une portière. Le filet synthétisé suit : un repli par porte (bois grave, tôle). Juges : chaque pièce a un genre de porte connu, chaque char dit ses portières, et un banc JS pousse la planque, le dépanneur, un logement, puis monte et descend d'une auto, d'un camion, d'une moto et d'un vélo en écoutant quel genre sort. Poids : 551 → **577 Ko** pour 34 fichiers, il reste 23 Ko sous le plafond de 600. ⚠️ Écoutée par Martin : la porte de commerce est **renvoyée**. Refaite deux fois. La première reprise (sans le ferme-porte « qui siffle ») est sortie : 0,67 s, **−12 dB** au-dessus de 2 kHz là où la sonnette de vélo tient son pic — et le juge de l'aigu l'a refusée : c'est la mesure qui a tenu lieu d'oreille. Deuxième reprise avec l **en tête du prompt** et la porte en second : trois candidats, tous à 1,48 s avec leur pic au-dessus de 2 kHz, gardé le plus propre (RSB 71 dB, −2,6 dB au-dessus de 8 kHz). La portière, elle, est sortie à **0,34 s** (un seul claquement, sans le cliquetis de la poignée demandé) — Martin dira si elle se tient, `--refaire porte_vehicule` sinon |
| Le vélo s'enfourche et sonne | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« je veux aussi un nouveau son pour ramasser et monter sur un vélo. je veux la sonnette comme klaxon de vélo ») : monter sur un vélo — ou une moto — jouait `ramasse`, le cliquetis d'un objet qu'on ramasse, et Martin l'a entendu pour ce que c'était. Nouvel échantillon `enfourcher` (la béquille qui claque, le cadre et la chaîne qui tintent sous le poids), pour tout char **sans portières** — la moto aussi, donc. Et **la sonnette est l'avertisseur du vélo** : la fiche nomme l'avertisseur (`vehicules.klaxon`, « sonnette » pour le vélo, « klaxon » pour tous les autres, juge sur `AVERTISSEURS`), `avertir(v)` joue celui de la fiche au même bouton — le trafic impatient passe par là aussi — et l'étiquette du bouton tactile dit **SONNETTE** (contexte `vehicule_sonnette`, sur le modèle de `vehicule_sirene`). Les vélos du trafic sonnaient déjà en passant (`jouerA('sonnette')`) : même son, désormais aussi sous le pouce, avec un repli synthétisé. Juges : la fiche du vélo dit « sonnette » et les autres « klaxon » ; au banc, au guidon d'un vélo le bouton dit SONNETTE et fait sonner la sonnette, au volant d'une auto KLAXON et le klaxon ; monter et descendre d'une moto et d'un vélo joue `enfourcher` deux fois et aucune portière. Poids : 578 → **586 Ko**, il reste **14 Ko** sous le plafond de 600 — la prochaine variante ne rentre pas sans baisser un débit ou relever le plafond. ⚠️ Pas écouté : `enfourcher` est sorti à 0,62 s avec +11 dB de gain (plancher propre, 43 dB) — `--refaire enfourcher` si ce n'est pas ça |
| M9 Le parc et les boulots | **livré** | 13 sept. 2026 | **P1** | ajout | ⚠️ Le Python était commité et **le JS n'existait pas** : quatre chars de phase 1 vivaient dans le paquet, se tiraient au trafic et se revendaient au garage, mais **rien ne les dessinait** — et aucun test ne le disait, alors que le prologue de `vehicules.py` le promettait. **Livré** : les quatre sprites (camion, autobus, ambulance, remorqueuse), le juge manquant (« tout char de phase 1 a son sprite »), et la **chaîne de cercles lue dans la fiche** — elle valait 3 pour tout le monde, donc une moto entrait dans l'autobus par le milieu. Et **un vélo ne saute plus** : il n'a pas de réservoir, donc il se **plie** — pas de feu, pas de fumée, pas de secousse, aucun délit. Le **camion défonce** ce qui est bas et jamais une façade, l'**ambulance soigne** qui la conduit sans ressusciter personne. La **remorqueuse traîne** un char, un seul. Et le **haut de gamme** est là : un coupé sport et une berline de luxe, `rare`, qui ne naissent que dans les districts qui les déclarent. La **pizza** et l'**ambulance** se prennent au klaxon — et dans une ambulance, l'appel se prend **quand on allume** la sirène, jamais quand on l'éteint (retour de Martin). La **fourrière** saisit ton char à l'arrestation et te le revend. Le **remorquage** paie les épaves qu'on lui amène au crochet, et **reprendre son char par-dessus la clôture** met le lot et ses gardiens sur toi. **M9 est complet** |
| « Mal garé » veut enfin dire quelque chose | **livré** | 13 sept. 2026 | — | **correctif** | le dernier morceau de M9, et un **correctif** : la fourrière promettait qu'un char mal garé part au lot, et la règle n'existait nulle part. Elle tombe des **cases** de stationnement : est mal garé un char **laissé hors d'une case ET qui gêne** — la chaussée, un passage piéton, le devant d'une porte. On regarde **toutes** les tuiles qu'il couvre, pas son centre. La remorqueuse municipale passe après 45 s, et elle **prévient** d'abord. ⚠️ Jamais le trafic (ça viderait les rues), jamais dans une case, une ruelle ou du stationnement, et **jamais** celui de la planque |
| La fourrière : remorquage et reprise par-dessus la clôture | **livré** | 13 sept. 2026 | — | ajout | le **boulot de remorquage** (une épave au crochet, payée dans la cour du lot — et la fourrière **ne paie que les épaves**), la **reprise sans payer** (sortir un char saisi : délit `fourriere`, bruyant, et un **plancher** d'étoiles parce que le lot _appelle_ au lieu de chauffer l'ambiance), les **gardiens** qui ripostent, et `aToi` — un char payé au guichet n'est plus un vol quand on monte dedans |
| Rampes vraiment prenables | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin : `ELAN` et `RECEPTION` sont des nombres de tuiles, alors que la portée d'un saut est **quadratique en vitesse**. La moto vole **126 px** pour 96 px de réception exigée — et c'est le char du _Grand Saut_. Il manque aussi le **freinage** (75 px de plus) |
| Un saut qu'on ne voit pas | **livré** | 13 sept. 2026 | — | **correctif** | bug de Martin (« les rampes n'ont pas l'air de fonctionner »). ⚠️ Elles fonctionnent : le saut mesure **7,8 px** pour une berline (2,0 px pour un vélo) et dure **0,3 s**, sur des tuiles de 16 px. Et l'ombre est un rectangle **fixe** de 20 × 10 qui ne rétrécit ni ne s'éloigne — elle ne raconte aucune hauteur |
| Entrer au garage, pas dans le char garé devant | **livré** | 13 sept. 2026 | — | **correctif** | bug de Martin (« quand on veut entrer au garage et qu'un véhicule est devant, quand on choisit "entrer" on entre dans le véhicule au lieu du bâtiment »). ⚠️ Une seule pression d'ACTION est lue **deux fois dans la même image** : `Combat.maj` ouvre le menu ACHETER / ENTRER de la propriété (ou lance le fondu de la porte), puis `Vehicules.maj` relit la même pression et fait monter dans le char garé devant. Au moment de choisir ENTRER, `Jeu.entrer` refuse : on est déjà au volant. **La porte gagne sur la portière** : un char ne se prend plus dans l'image où un menu vient de s'ouvrir ou un fondu vient de partir — un menu et un fondu figent déjà tout le jeu (`Jeu.maj`), à plus forte raison la portière d'à côté. Deux juges de banc : une seule pression devant le garage ouvre le menu **sans** prendre le char, puis ENTRER mène dedans ; et à une porte à soi (sans menu), le fondu part et le char reste là. 1033 tests |
| L'endurance du Faubourg | **livré** | 13 sept. 2026 | **P2** | **correctif** | demande de Martin (« que la course ne consomme plus d'énergie, mais que ce soit le sprint ») : le modèle avait été réglé pour le Faubourg de 157 tuiles et M8 a **quintuplé la ville**. Un souffle valait **33 tuiles sur 421**, et la vitesse qu'on pouvait tenir tombait **sous celle du policier** — la barre ne récompensait rien, elle taxait le déplacement. **Trois vitesses** : marche 1,2 · **course 2,0, gratuite** · sprint 2,6, qui coûte. ⚠️ Et le policier court **exactement** à la vitesse de la course, sinon une course gratuite serait l'impunité : on gagne du terrain par **bouffées de sprint**, ou en cassant la ligne de vue. La barre s'**efface** quand elle n'a rien à dire, et le bouton s'appelle **SPRINT** |
| Un char qui ne reste plus pris dans un mur | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin (« mets un garde-fou pour éviter que mon véhicule coince dans un mur ou un objet »). ⚠️ `avancer` teste les tuiles **avant** chaque pas, mais rien ne regardait où le char **est** : poussé par un autre char (`heurterVehicules` déplace sans lire les tuiles), tourné sur place contre une façade (la chaîne de cercles pivote **dans** le mur) ou retombé d'un saut (en l'air, les tuiles ne comptent pas), il se retrouvait dans le mur — et de là **chaque direction était bloquée**, même celle qui sort : pris pour toujours. `degager()`, à chaque image, pour tout char qui n'est pas sur ses rails : **poussé** hors des tuiles chevauchées (mesuré : 4,01 px pour 4 px d'enfoncement, cap gardé — pivoter contre un mur fait maintenant glisser le long), sinon **posé** à la place libre la plus proche, par anneaux de 2 px jusqu'à 96 px (posé à 48 px du milieu d'un toit, à l'arrêt : son élan est ce qui l'a mis là). ⚠️ La poussée garde la plus longue sortie par axe, pas la somme : trois cercles enfoncés de 4 px demandaient 12. « Un objet », c'est tout ce que `MASQUE_VEHICULE` arrête (borne-fontaine, clôture, meuble) ; les poteaux et les bancs ne bloquent pas encore les chars — c'est « Le décor se brise ». 2 juges |
| Étoiles de recherche illisibles | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin : plus grosses, jaunes, au centre. ⚠️ Ce sont des `★` de texte à l'échelle **1** dans un coin, sous un montant d'argent à l'échelle **2** — la chose la plus importante d'une poursuite est le plus petit élément de l'écran |
| Clôture nord-sud trop large | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin : elles ont été redressées **par une rotation**, donc le nord-sud est un panneau de 7 px vu à plat. Vue d'en haut, une clôture nord-sud se voit **par la tranche** — la règle est déjà écrite pour les façades et les meubles. ⚠️ Le juge actuel exige la rotation : il verrouille le défaut |
| La nuit ne se vide pas | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin. ⚠️ Le rythme de nuit existe depuis M8 mais ne fait presque rien : le Faubourg garde **9 véhicules sur 9** (12 × 0,75 = 9, pile le plafond) et **19 piétons sur 26**. Le plafond s'applique **après** le rythme au lieu d'avant, et la police n'en suit aucun |
| Arbres dans les sentiers | **livré** | 13 sept. 2026 | — | **correctif** | demande de Martin : `_parc()` sème arbres, bancs et buissons sur tout le rectangle, et une allée n'est ni solide ni routière — rien ne la protège. Or un arbre est **solide** : il barre le sentier qu'on a dessiné pour y passer |
| Fruits de mer, hommes-sandwichs et des comptoirs garnis | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« ajoute des commerces de fruits de mer et des solliciteurs hommes-sandwichs », puis « ajoute aussi plus de bouffe et de choses à manger et à boire dans tous les magasins, où ça fit »). **Les fruits de mer** : une **cabane** de trottoir (`fruits_de_mer`, guédille au homard, toit de tôles rayées, deux homards sur la glace, l'enseigne HOMARD au pied) que le générateur ne pose **qu'aux Quais et à La Pointe** — `AMBULANTS[].districts` enferme un commerce chez lui comme `pietons.districts` enferme un passant, et un juge vérifie que c'est le port qu'on mange ; huit enseignes de plus (FRUITS DE MER, HOMARD VIVANT, CRABE DES NEIGES…) dans les deux districts qui touchent l'eau ; la poissonnerie sert guédille, crevettes de Matane et chaudrée. ⚠️ Le toit de la cabane s'arrête à la rangée 3 : le marchand a les pieds 11 px au-dessus de l'ancre, ses yeux tombent à la rangée 5 — un toit plus bas les cachait et on se faisait servir par un chapeau (le camion-restaurant avait eu la même leçon, avec son guichet troué). **L'homme-sandwich** (`pietons.homme_sandwich`, métier `reclame`) : un **solliciteur**. `carte.reclames` lui donne un **poste** de trottoir à 5–14 tuiles du kiosque pour lequel il crie (le hot-dog, la poutine, la guédille — pas le journal ni le café : `AMBULANTS[].reclame` est son boniment, None = personne), tiré dans **son propre dé** (`des_reclame`) pour ne pas déplacer un paquet caché à l'autre bout de la ville ; il naît à son poste, le jour, hors champ (`naitreLesHommesSandwichs`), il fait les cent pas dans un rayon de six tuiles (le `poste` de la Brume, plus large), et quand il te voit à six tuiles il **vient vers toi** (`aborde`, à la vitesse d'un piéton, jamais en courant), s'arrête à 22 px, te regarde et **crie son boniment** dans une bulle pendant trois secondes (`boniment`, voix ElevenLabs « Approchez, approchez, venez voir ! » — genre `crieur`, dite par **Léo**, la voix de pub du compte, poussée au style : avec Felix, l'homme de tous les jours, Martin les trouvait « pas assez vendeur ») ; ACTION devant lui donne un **coupon** : la prochaine bouchée à SON kiosque à moitié prix, **une fois**, et il expire au bout de trois minutes (`RECLAME`, sur le joueur comme la caféine — trois minutes ne méritent pas une sauvegarde) ; l'invite le dit (« KIOSQUE À HOT-DOGS — 5 $ (COUPON) ») et la caisse le fait, même calcul (`prixAmbulant`). ⚠️ **Un solliciteur n'est pas un mur ni un radar** : il regarde une image sur dix, il n'aborde **que celui qui flâne** (au-dessus de la marche, il te laisse : un homme-sandwich qui se jetait dans les jambes du joueur au sprint le ralentissait de 10 % — le juge du café l'a mesuré, la police rattrapait à cause d'une pancarte), il lâche prise si tu cours, si la chaussée ou un mur barre le chemin ou si ça fait quatre secondes qu'il n'arrive pas, et une fois son boniment fait il te laisse **vingt secondes de paix** (`repos_images`) — sans ça il te suivait d'un bout à l'autre de la rue en répétant la même phrase, et un personnage qu'on veut frapper n'est pas de la vie de rue, c'est une plaie. ⚠️ **Deuxième archétype à avoir son propre sprite** (`homme_sandwich`, 14 × 16) : une pancarte plus large que les épaules, bande rouge et deux lignes d'écriture, un « A » de deux planches vu de côté — même leçon que la Brume, un contour se lit là où une couleur ne dit rien ; son `c` est la pancarte, pas un chandail. **Les comptoirs garnis** : de quoi manger et boire dans **toutes** les familles où ça a du sens — soupe aux pois, pâté chinois, pointe de tarte et liqueur au dépanneur ; beigne et liqueur au comptoir de service ; liqueur et barre de chocolat à la quincaillerie (le présentoir à côté de la caisse) ; ailes de poulet, chips et shooter de rye au bar ; chips, chocolat et liqueur au magasin ; sandwich et liqueur à la cantine de la shop ; jus d'orange et chocolat à la pharmacie ; poutine, soupe et liqueur au casse-croûte garanti. La **friperie n'en vend pas** : ça ne fitte pas, et un comptoir qui vend n'importe quoi ne dit plus où l'on est. ⚠️ Toujours la même borne, et un juge fait la division : **au dollar, rien ne bat le hot-dog** (6,5 points par dollar) — ce qu'on achète au comptoir, on l'achète parce qu'on est devant. 14 juges Python (`test_reclame.py`) + 5 de banc (`test_reclame_js.py` : il naît à son poste le jour et pas la nuit, il vient et il parle sans courir puis se tait, le coupon rabat le prix une fois et expire, la cabane sert une guédille, les comptoirs et le casse-croûte ont de quoi manger) |
| Des lits qui ont l'air de lits | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« les lits existants doivent vraiment avoir l'air de lits, juste un set d'oreillers et des couvertes ; actuellement c'est 2 ou 4 cases avec chacune leur oreiller »). ⚠️ Le peintre du lit ne savait pas qu'il avait des voisines : chaque tuile `l` dessinait son oreiller, sa couverture et son ombre, donc un lit de 2 × 2 (tous les lits du jeu : planque, hôpital, hôtel, phare, logements) était **quatre lits d'une place collés**. Le remède était déjà écrit trois fois dans `monde.js` : le lit **lit ses voisines** comme la clôture et le toit (`varianteDeLit`, le masque des côtés où le lit continue — 1 nord, 2 est, 4 sud, 8 ouest). Le peintre n'a plus qu'une règle : la **tête de lit et l'oreiller** ne vont qu'aux tuiles sans lit au nord, l'oreiller et la couverte **courent d'une tuile à l'autre** sans couture (le piqué de la couverte tombe sur la même grille de 4 px des deux côtés de la couture), et le **cadre de bois ne se ferme que là où le lit s'arrête** — avec un pixel de plancher devant, comme tous les meubles, et l'ombre au pied seulement. ⚠️ Le corollaire, gardé par un juge des plans : **deux lits ne se touchent jamais** (collés, ils seraient peints comme un seul lit de quatre de large) et un lit est un rectangle plein d'au plus deux tuiles de côté — pas de lit en L sans tête. Un lit d'une seule tuile, d'une tuile sur deux ou de deux sur une se dessine aussi, la même règle suffit. Juges : 29 en Python (`test_interieurs.py`, un par pièce) + 1 de banc (`test_interieurs_js.py` : les quatre variantes lues dans la planque, puis les traces des quatre tuiles — un oreiller par tuile de tête et aucun au pied, à cheval sur la couture, la couverte continue, le cadre qui laisse son pixel de plancher au nord-ouest et pas à la couture). Vu à l'œil dans un rendu des traces (2 × 2, 1 × 2, 2 × 1, 1 × 1) |
| Des meubles d'un seul tenant : table, tapis, machine | **livré** | 14 sept. 2026 | — | ajout | suite des lits, demande de Martin (« regarde si d'autres composantes mériteraient un traitement similaire », puis « oui vas-y »). J'ai compté les blocs dans les 29 plans et rendu chaque forme telle qu'elle se peignait : même défaut pour trois glyphes. Le **billard** du bar et de la taverne (table 4 × 2), l'établi du garage (3 × 2) et treize tables sur deux rangées étaient autant de petites tables avec chacune ses bords rentrés, son vernis, son chant et son ombre ; le **tapis** mettait son galon en haut et en bas de chaque tuile, donc un 3 × 3 était trois chemins de couloir sans bord à gauche ni à droite ; une **presse** de l'usine (4 × 2) était huit petites machines avec leurs boulons. ⚠️ **C'est la fiche qui le dit** : `bloc` dans `carte.LEGENDE` (lit, table, tapis, machine), et `varianteDeLit` devient `varianteDeBloc(g)` — le masque des côtés où le même glyphe continue, plus un **grain** dans les bits 4 et 5 (sans lui, deux tuiles au même masque avaient le même grain de tapis, et une machine seule ne pouvait plus tirer le sens de sa courroie au sort). Chaque peintre n'a qu'une règle de plus : ce qui marque un bout (chant, vernis, galon, boulon, face, ombre) ne va qu'aux tuiles où le bloc s'arrête, le reste court d'une tuile à l'autre ; la courroie d'une machine suit le sens du bloc. Une table, un tapis, une machine d'une seule tuile n'ont pas changé d'un pixel (un juge le vérifie). ⚠️ **Le juge des plans a rougi une fois** : dans la taverne, la table de gauche touchait le billard, et les deux auraient été peints comme un meuble en L de 4 × 4 — le billard passe contre le mur de l'est. Restent tels quels, à dessein : le comptoir (déjà d'une seule planche), l'étagère (cadre continu), les classeurs et les frigos (des unités côte à côte), l'escalier (ses marches s'enchaînent), les chaises (des rangées de sièges, jamais une banquette). Juges : la liste des `bloc` est exactement ces quatre-là ; un bloc est un rectangle plein dans les 29 pièces (et un lit fait au plus 2 × 2) ; trois juges de banc cuisent un 4 × 2 de tables, un 3 × 3 de tapis et un 4 × 2 de machines et lisent les traces (vernis au nord seulement, chant au sud, deux galons aux coins et aucun au centre, un boulon par coin, courroie couchée qui court jusqu'au bord). Vu à l'œil dans un rendu avant/après des onze formes de blocs du jeu |
| Le décor se brise | **livré** | 13 sept. 2026 | **P2** | **correctif** | demande de Martin (« les bris de poteau, de banc de parc et d'arbre ») : le décor était **solide pour les piétons et fantôme pour les chars** — un autobus traversait un arbre, un kiosque et une fontaine sans ralentir, et le **lampadaire était fantôme pour tout le monde**. La **fiche décide** maintenant : `arrete` (un arbre stoppe une berline, un camion le déracine) ou `casse` (un banc, un poteau, un cône cèdent sous n'importe quoi lancé). Le bris laisse des **débris** plafonnés, **éteint la lampe** du poteau tombé, compte une **conduite dangereuse**, et la ville se **répare au lever du jour** — pas dans la minute : le quartier porte ses blessures |
| Des sortes de gens | **livré** (1re vague) | 14 sept. 2026 | **P2** | ajout | demande de Martin (« des amuseurs publics, des musiciens de rue, des exhibitionnistes ») : la ville avait **24 archétypes pour 4 corps** — vingt et un portaient celui du joueur repeint — et sur six `metier`, **deux** faisaient quelque chose. Une sorte était une couleur et trois chiffres. Règle posée : **une sorte = un corps + une routine**. Les trois que Martin a nommées ont chacune son sprite 12×13 et sa routine : le **musicien** et l'**amuseur** tiennent un poste et **attroupent** (et un attroupement est une **foule de témoins**), l'**homme au manteau** l'ouvre au passage d'une dame — qui crie et fuit — et ⚠️ **un agent l'arrête, lui**. Le réservoir de la fiche reste à piger, par vagues |
| Des sortes de gens — deuxième vague | **livré** | 14 sept. 2026 | **P2** | ajout | **cinq des sept**, celles dont la routine se branche sur ce qui est déjà livré : la **contractuelle** (elle va au char mal garé, elle verbalise, et « mal garé » cesse d'être un message venu de nulle part), le **touriste** (`temoin: 1.0`, le seul — il lève la tête devant une vitrine et il photographie), l'**ivrogne** (il zigzague, il tombe tout seul, et **il ne fuit pas** devant une arme : il répond), le **jogger** (il ne s'arrête **jamais** — une routine en creux — et ne témoigne de rien), le **facteur** (de porte en porte, il fait battre le battant et **n'entre pas**). Un corps 12×13 chacune, ses **quartiers** déclarés, et ses **mots en Python** (`pietons.PAROLES`). Restent la **personne âgée** (elle attend les feux pour piétons, P4) et le **pickpocket** (M12). 3 juges neufs |
| Des sortes de gens — troisième vague | **livré** | 14 sept. 2026 | **P2** | ajout | trois du réservoir, choisies pour leur **crochet** : le **crieur de journaux** hurle la manchette du Clairon — donc **ce que tu as fait hier** (`journal.py` compare tes statistiques du jour à celles de la veille : trois morts un soir, et tu l'entends crier au coin de la rue le lendemain) ; le **laveur de vitres** ne s'approche que des chars **arrêtés** — la même horloge que les feux, et un char qui repart le laisse le chiffon en l'air ; le **pickpocket** vole **les autres**, dans le dos et au même angle que le joueur, l'argent change de poche pour de vrai, la victime crie AU VOLEUR et un agent l'arrête **lui**. 1 juge neuf |
| Les portes s'ouvrent | **livré** | 13 sept. 2026 | **P2** | ajout | demande de Martin (« les piétons devraient aussi sortir et entrer dans les commerces ; profites-en pour faire ouvrir concrètement les portes ») : ⚠️ un piéton sur trois sortait **déjà** d'une porte — mais `placeDeNaissance()` refusait la place si elle était **visible à l'écran**. Ce n'était pas une sortie, c'était une naissance déguisée en sortie, dont le seul intérêt aurait été d'être vue. Maintenant : un **battant** qui s'ouvre, tient et se referme — posé **par-dessus** le sol, jamais dans le morceau cuit —, on naît **dans** la porte et on en sort à l'écran, et un flâneur se choisit une porte et **rentre**, ce qui remplace une part de l'oubli par distance. ⚠️ Jamais la planque, ni le poste, ni l'hôpital ; un commerce pas la nuit — sauf le bar |
| La porte s'ouvre pour le joueur aussi | **livré** | 14 sept. 2026 | — | **correctif** | retour de Martin (« les portes doivent ouvrir quand j'entre aussi ») : le battant s'ouvrait pour les piétons et **pas pour lui** — d'autant plus voyant que les passants, eux, attendaient poliment l'ouverture. ⚠️ Le piège était dans l'ordre : le jeu est **figé** pendant un fondu de porte, donc un battant ouvert au départ y restait au premier pixel. Les battants battent maintenant **pendant** la transition — la seule chose qui bouge quand tout le reste est arrêté. La porte s'ouvre **avant** de noircir (c'est là qu'on la voit), et au retour c'est celle de la **rue** qui s'ouvre, une fois la ville restaurée |
| Le carnet | **livré** | 13 sept. 2026 | **P2** | ajout | demande de Martin (« un rappel de la mission en cours dans le menu, un journal et un bestiaire avec les personnages connus ») : **LE CARNET** au menu Pause, trois pages — **EN COURS** (donneur, récompense, objectifs faits marqués, celui du moment, et où), **JOURNAL** (écrit tout seul depuis ce que le jeu émet déjà, daté au jour, plafonné — le quotidien cède avant les jalons), **RÉPERTOIRE** (⚠️ `p.connus` seulement : un répertoire qui montre la fin est pire que pas de répertoire). Les menus savent maintenant **défiler**, et une page recule d'un cran au lieu de rendre la main au jeu |
| Des sons pour les armes | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« fait moi des sons pour les armes ») : toutes les armes jouaient le **coup de poing** — la batte, le couteau, le pistolet et le fusil aussi (`majAttaque` et `tirer` appelaient `SFX.coup`), le jet d'extincteur ne faisait aucun bruit, et un chargeur vide comme une arme qui casse faisaient le **buzzer de refus** des menus. Chaque arme porte maintenant son `son` (`armes.py`) et le combat passe par `SFX.arme(def)` ; **16 échantillons ElevenLabs** (batte ×2, couteau ×2, pelle, cône, bouteille, fronde, pistolet ×2, fusil ×2, le **jet en boucle** tenu par `SFX.jet(actif)` à chaque image, la gâchette **à vide**, la **casse**, le **dégainage**), ≈ 141 Ko, chacun avec son repli synthétisé ; budget des bruitages relevé à 800 Ko. ⚠️ Au passage, un **hoquet** au départ du jet : la première pression partait par le chemin de la mêlée (anticipation, quatre images de jet, deux de repos) avant que le maintien ne prenne le relais — invisible, mais audible avec une boucle. ⚠️ **Martin n'a pas encore écouté** : `batte-1` et `batte-2` sont sortis très courts (0,18 et 0,26 s), à refaire s'ils ne sonnent pas (`--refaire batte`) ⚠️ **Correctif, 15 sept. 2026** (retour de Martin : « le son des bornes-fontaines brisées n'est pas correct ») : la borne jouait **`SFX.choc`** — la tôle froissée d'une collision — au bris **et toutes les 24 images pendant les dix secondes du jet**. Mesuré : **26 sons d'accident de char pour une borne défoncée**, dont le premier en doublon avec le char qui vient de la renverser (`heurterDecor` joue déjà `choc` à la même image). Deux sons désormais, et la frontière est nette : **le bruit de l'impact appartient à ce qui a défoncé**, la borne n'a que son bouchon et son eau. `borne_cassee` — le bouchon qui saute, la tôle qui cède, l'eau qui s'ouvre — **une seule fois** ; `borne_jet(force)` — un souffle **tenu**, appelé à chaque image avec la vérité du moment (le patron de `jet()` de l'extincteur), dont le volume **suit la distance** (portée 260 px) et qui se tait quand la gerbe meurt. ⚠️ Les deux sont **entièrement synthétisés** : le seau des bruitages est à 14 Ko de son plafond, et le navigateur ne réclame au catalogue que des slugs que Python déclare (un juge le tient) — le jour d'une séance ElevenLabs, la fiche gagnera ses deux entrées et ces fonctions leur repli, ensemble. 2 juges de banc, rouge-avant prouvé (26 chocs) |
| La fille de la Brume parle | **livré** | 13 sept. 2026 | — | ajout | demande de Martin (« la prostituée aussi doit parler, avec plusieurs dialogues différents ») : `rumeurEtRepliques` saute tout piéton qui a un `metier`, et elle en a un (`compagnie`) — elle ne disait jamais rien, alors que la regex des voix de femmes la nommait déjà. **Six répliques à elle** (genre `brume`, voix **Julia**, québécoise et rauque, poussée au style), dites par `Entites.accosterDepuisLaBrume` quand on passe à trois tuiles de son coin : une **bulle** avec le texte, la voix par-dessus, **jamais deux fois de suite la même** (`Son.Voix.choisir(genre, sauf)`, tiré dans le dé du jeu), pas deux fois en moins d'une demi-minute, jamais en char, jamais quand elle fuit. Le chemin des passants ne bouge pas. Budget des bruitages à 850 Ko (+52 Ko). ⚠️ Martin n'a pas encore écouté |
| Une seule musique pour toute la ville | **livré** | 14 sept. 2026 | **P2** | ajout | demande de Martin (« des musiques différentes par district, et des musiques pour quand on se bat avec des gangs, et quand on a plusieurs étoiles ») : il y en avait **une**, la même de La Pointe aux Quais. ⚠️ Le vrai travail n'était pas les pistes, c'était **qui gagne** — l'échelle est maintenant **écrite une fois en Python** et le navigateur la lit. Cinq ambiances de district + poursuite + bagarre, **écrites en notes** (aucun mp3, aucun crédit : `musique.py` promettait cette porte depuis le premier jour), avec **hystérésis** aux frontières et **queue** sur les musiques d'état — c'est elle qui fait qu'on souffle |
| Les véhicules vus de profil | **livré** (douze debout, modelés, pilotés) | 15 sept. 2026 | **P2** | **correctif** | demande de Martin : « une refonte complète des véhicules. Je les veux comme les piétons, de profil ». Tout ce qui est **debout** dans le jeu est dessiné debout — le passant ancré à ses pieds, l'arbre, le lampadaire, le banc, le feu et son poteau, les clôtures nord-sud vues par la tranche — et le char est la **dernière chose regardée d'aplomb**. Trois poses (profil miroité, dos, face) choisies comme la face d'un passant, au lieu de 32 caps cuites : l'atlas du parc passe de **1 024 canevas et 6 Mo à 96 et 0,3 Mo**. ⚠️ Mesuré : **94,5 %** des chars en marche sont à moins de 2° d'un cap cardinal — la rotation libre coûte 6 Mo pour 3 % du temps. ⚠️ De dos, les 28 px de longueur ne se voient plus : l'ombre au sol permanente est le filet — **livrée**, permanente, à l'empreinte du catalogue, orientée comme le char. **Dix chars sur douze sont debout** (auto, taxi, police, sport, luxe, ambulance, camion, remorqueuse, autobus) : trois poses au vocabulaire du passant, choisies par le même code que sa face, ancre à la ligne de sol. Puis, sur « raffine les designs » de Martin, **le modelé** : rehaut `C` et ombre `D` dérivés de la couleur de caisse par une seule formule (`nuances`, dans `base.js`, partagée entre les palettes et la naissance d'un char), moyeu `M`, chrome `B`, reflet `G` et ombre `E` de vitre — en majuscules, parce qu'aucune palette n'en a. Le taxi et la police ont retrouvé leur livrée sur la carrosserie commune. ⚠️ **L'aperçu est à trancher par Martin** (l'artefact « La flotte debout »). ⚠️ Cette ligne est repassée trois fois à « à faire » sous mes marqueurs : des plans reconstruits depuis une base plus vieille. **Livré en entier** : les douze véhicules debout, modelés (rehaut, ombre, moyeu, chrome, reflet — `nuances` partagée), et le vélo et la moto avec un **passant assis** dessus, aux couleurs du joueur ou d'un archétype de rue. Sur retour de Martin, la sport est basse, les roues dans les ailes. ⚠️ La tête du pilote ne consomme pas un dé (`hash2` de sa position) : un choix cosmétique ne perturbe pas la simulation. Restent, hors fiche : le bateau qui n'a pas de sprite (dette), et la pose couchée de l'épave — `debout()` la choisit déjà si un sprite la déclare. ⚠️ **Correctif, 15 sept. 2026** (retour de Martin : « corrige les ombres pour les véhicules en nord-sud ») : l'ombre posait l'empreinte du catalogue **à plat**, donc un char qui roule vers le nord traînait ses 28 px de long — **quinze pixels sous ses roues, pour un dessin haut de onze** : on lisait une remorque. Or **le sol se voit de biais**, et le jeu le disait déjà ailleurs : l'ombre d'un passant fait 12 × 6 pour un corps rond. L'axe nord-sud est donc écrasé du **même** biais (`OMBRE.profondeur`, 0,5), appliqué au dessin **après** la rotation (sinon une empreinte en diagonale est cisaillée au lieu d'être posée à plat) ; l'empreinte en X, celle que le dessin montre, ne bouge pas d'un pixel. Et l'écart a deux composantes : au sol elle tombe **à l'est** (la lumière vient du nord-ouest) et **pas au sud** — rien ne dépasse devant les roues d'un char posé ; ce qui s'échappe vers le sud-est, c'est l'altitude. 3 juges : la fiche, « un seul biais pour toute la ville » (le passant et le char comparés), et la règle mesurée — **une ombre ne dépasse jamais la ligne de sol de plus que la hauteur du dessin qui la jette**, sur les quatre caps et tous les véhicules debout ; rouge avant (« auto vers le nord : l'ombre traîne 15 px sous ses roues, et le dessin n'est haut que de 13 px »). ⚠️ **Deuxième correctif, 15 sept. 2026** (« améliore les virages et valide la direction des phares quand je pilote »). **Les virages** : le char tournait d'un nombre fixe de radians par image, quelle que soit sa vitesse — le cercle qu'il décrivait valait donc `vitesse / braquage` et **grandissait avec elle** : mesuré sur une berline, 1,4 tuile au pas et **12,6 tuiles à fond**. Un coin de rue en demande une et demie ; à pleine vitesse le coin était impossible, et `majTrafic` l'écrivait déjà noir sur blanc (« il ratait son virage et finissait sur le trottoir d'en face »). Une vraie auto décrit **toujours le même cercle** à volant fixe : la rotation est maintenant `vitesse / rayon_braquage`, et la fiche déclare un **rayon en pixels** (22 px pour une berline, une tuile et demie ; 40 pour un autobus) au lieu de radians par image — les valeurs sont les anciennes inversées, le caractère de chaque char ne bouge pas. Mesuré après : **1,4 tuile au pas, 3,2 à fond** (le volant perd de la prise à haute vitesse, `braquage_vite`). ⚠️ **Le volant se tourne, il ne se claque pas** : la direction passait de 0 à 1 en une image — au clavier, chaque appui était un coup de butée à butée ; il prend et se recentre en un dixième de seconde. ⚠️ **Et un char pivote sur son arrière**, pas sur son nombril : le nez balaie, le train arrière suit (le décalage n'est pris que si la place est libre). L'**adhérence** suit le reste : à rotation trois fois plus vive, l'ancienne valeur aurait mis le char en travers de 34° en permanence — 0,30 pour une auto (glisse 6–11°), 0,22 pour les lourds qui labourent, **0,18 pour la sport** qui reste de loin la plus glissante, 0,40 pour le luxe. **Les phares** : validés, rien à corriger — l'ancre est exactement au milieu (le miroir ne décale pas d'un pixel), le blanc est devant et le rouge derrière dans les onze sprites, et les seules lampes blanches visibles de dos sont les **gyrophares** de l'ambulance et de la remorqueuse, sur l'axe du toit. Un juge le tient maintenant, sur les 72 caps du cadran. 4 juges de banc + 3 de fiche ; rouge avant sur les trois règles (le cercle qui passe de 22,6 à 201,6 px, le volant qui claque à la butée en une image, le nez et le coffre qui parcourent le même chemin). 1580 tests |
| Les chars de dos et de face, en vue plongeante | **livré** | 15 sept. 2026 | **P2** | **correctif** | retour de Martin : « les voitures de face et de dos devraient être vues à 45 degrés, pas de face, vu la carte » — « vue plongeante ». Les poses `haut` et `bas` sont des **élévations au ras du sol** : on voit la face arrière (ou avant) bien à plat et presque pas de toit, alors que la carte se regarde d'en haut. Un char qui roule vers le nord ne montre donc **rien de ses 28 px de longueur** — c'est le défaut que l'ombre au sol compensait. À 45°, la longueur se projette sur l'axe vertical (28 × sin 45° ≈ 20 px) : il faut donc **agrandir la toile** des sprites vers le haut et remonter l'ancre, redessiner les 18 grilles (9 familles × 2 poses), replacer la selle des deux-roues, et rejouer les juges qui lisent l'ancre comme « la hauteur du dessin ». ✅ **Livré** (15 sept. 2026) : les 18 grilles redessinées (9 familles × 2 poses), la toile agrandie vers le haut et l'ancre remontée à la nouvelle ligne de sol. **La règle, et elle se mesure** : de dos comme de face, un char occupe à l'écran sa **longueur** — exactement ce que son ombre au sol annonce déjà (avant : 12 rangées peintes pour une berline longue de 28). ⚠️ Ce qui fait lire une auto vue d'en haut, et qui manquait au premier jet : **une silhouette**. Un char n'est pas un pavé — il se pince au nez et à la queue, ses ailes débordent sur les roues, sa cabine est **posée en arrière du milieu** et plus étroite que la caisse, et son montant est l'ombre de la caisse (`D`) et non un trait noir : cerclée de `k`, la cabine se lit comme un trou de toit ouvrant. Le **capot reste plat et sombre** pour que le toit soit la seule surface haute — une arête claire sur le capot le mettait au même ton que le toit, et plus rien ne levait. La lumière vient du **nord-ouest** comme partout ailleurs : flanc gauche au jour, flanc droit dans l'ombre. Les familles dérivent d'un seul patron (`berline` / `camion`) et ne diffèrent que par quelques nombres — capot, toit, coffre, longueur de boîte, nervures : une berline, un coupé, une limousine, une ambulance, une remorqueuse, un camion, un autobus. Les deux-roues sont écrits à la main (un vélo n'a ni capot ni coffre) et leur **selle** remonte avec la toile. ⚠️ Trois juges rejoués, et ils ont payé : le char **flottait d'une rangée** (l'ancre n'était pas la dernière rangée peinte), la règle « rien n'est plus haut que long » datait du dessin à plat, et le juge de l'ombre prenait l'ancre pour la hauteur du char — il mesure maintenant ce que le **flanc** monte, sinon sa borne se relâchait de vingt pixels en silence. 1 juge neuf, rouge-avant prouvé (« auto de dos : 12 rangées pour un char long de 28 — il est dessiné de face, pas vu d'en haut ») ; 1590 tests |
| Un stationnement touche la rue | **livré** | 15 sept. 2026 | **P2** | **correctif** | demande de Martin : « les stationnements doivent absolument être rattachés à la route ou collés à un trottoir au moins une fois ». Mesuré sur la graine livrée : **un lot de 4 × 4 au milieu des cours arrière** d'un bloc de maisons du Faubourg (219, 28) — quatre cases, une allée, un îlot, et **rien que du gazon sur ses quatre côtés**. On y peignait des places où aucun char ne pouvait entrer, et rien ne le disait : les lignes sont peintes pareil. La règle se tient maintenant **par construction**, un cran au-dessus de celle qui tient déjà le dessin d'un lot (« toute rangée touche une allée ») : un terrain donne sur la rue s'il touche un **bord de sa bande** — la ruelle derrière, la couronne d'abord à gauche ou à droite, le trottoir du devant. ⚠️ **Sauf le devant d'un bloc de maisons, qui est du GAZON** : celui-là se perce d'une **ENTRÉE** large d'une allée (deux tuiles), sortie de l'**allée** du lot et non du fond d'une case — une entrée qui débouche sur un pare-chocs fait entrer les autos par la place de quelqu'un d'autre — et poussée à travers l'herbe jusqu'à ce qui borde la rue. Et le terrain où même l'entrée ne passe pas **n'est plus un stationnement** : il redevient ce que son genre aurait dessiné (jardin, terrain vague) — on ne laisse pas un lot muré. ⚠️ `_chemin_vers_la_rue` est la règle de l'entrée de cour de banlieue, sortie d'une fonction imbriquée et **partagée** : ce qu'on traverse (herbe, dalle, abord), jusqu'où on cherche (dix tuiles), et « pas d'entrée » quand la liste est vide. Seule l'**arrivée** change : une cour vise la chaussée, un lot se contente de tout ce qui borde la rue (`RUE_DU_LOT` — chaussée, ruelle, trottoir, abord). ⚠️ **Et l'entrée s'arrête là où la rue commence**, sans paver une tuile de dalle ni d'abord. Ce n'est pas une question de goût : `_places_ambulantes` construit une LISTE de places et `ambulants()` y pioche avec `des.suivant() % len(candidats)` — **quatre tuiles de sol changées déplacent les treize kiosques de la ville**, donc les hommes-sandwichs, donc ce qui vit autour du terminus. Première version, l'entrée poussée jusqu'à la chaussée : la fille de la Brume s'est mise à flâner au lieu de tenir son coin (**9 relevés d'arrêt sur 80 au lieu de 41**) et son juge a rougi sans qu'une ligne de son code ait bougé. L'entrée est en plus **réservée** (`self.entrees`) : un camion-restaurant garé dedans refermerait le seul chemin par où l'on entre. Bilan sur la ville livrée : **4 tuiles changées**, un lot rattaché, kiosques et enseignes inchangés. 3 juges — la règle sur cinq graines (rouge avant : « 1 stationnements sans rue » sur la graine livrée), la forme de l'entrée, et le chemin qui ne mène nulle part |
| Trottoir et traverses de deux tuiles | **livré** (2e tentative) | 15 sept. 2026 | **P3** | **correctif** | demande de Martin : `TROTTOIR = 2` construit chaque rue **et la profondeur des passages piétons** — une seule constante pour les deux. Le passer à 1 demande de rétrécir les rues de deux tuiles (sinon elles gagnent deux voies), de reloger lampadaires, bornes, kiosques et la réserve devant les portes, de trancher sur la foule, et ⚠️ de sortir le **2 écrit en dur** dans `monde.js`. ✅ **Le prérequis est payé** (15 sept. 2026) : `monde.js` lit `grille.trottoir`, et trois juges le tiennent — dont un qui donne au navigateur un paquet à une tuile et compte ce qu'il range comme croisement, et un qui mesure que **toutes les traverses font exactement la largeur du trottoir**. Il rougira le jour où la constante bougera sans elles. Les trois questions ouvertes sont tranchées par Martin : on se croise, les tuiles libérées vont **aux terrains** (dont la bordure devient marchable), et la dalle reste prioritaire. ✅ **Le gros œuvre est livré** (15 sept. 2026, 2e tentative — la première avait été annulée) : `TROTTOIR = 1` ; chaque rue perd deux tuiles (`RUES_V`/`RUES_H`) et chaque bloc les gagne (`COLONNES`/`RANGEES`) — mêmes voies, même ville, ⚠️ sauf la rangée du chenal, gardée telle quelle pour que le pont reste le seul lien carrossable. La couronne extérieure de chaque bloc bâti (commerces, logements, gangs, industrie, lieux garantis, fourrière — pas les parcs, les places ni les quais) devient un **abord** (`_`, pavé, marchable, sol nu) où déménagent les **lampadaires** des coins de croisement, les **kiosques** et les **postes** des hommes-sandwichs ; le trottoir reste la **dalle prioritaire** : un flâneur qui passerait de la dalle à l'abord fait demi-tour trois fois sur quatre (`REACTIONS.abord_renonce`, dans la fiche), sauf s'il va vers une porte. ⚠️ Les sentiers de banlieue, l'allée vers la rue et la réserve devant les portes traversent l'abord en le **pavant** (`_` → `.`), sinon une porte donnait sur un anneau de pavés. **Les neuf juges rejoués un par un** : les lampadaires (près d'une rue à plus de 80 %, aucun sur la dalle), les kiosques (sur l'abord, la dalle devant), la banlieue, la fourrière, le chenal, la traverse (pleine, sans déborder), le toit (« un bord ne se peint pas COMME un plein », pas « plus » — il tenait par chance sur le premier toit venu), le témoin des cinq, la foule qui se creuse, l'amuseur (le juge le pose sur sa scène comme le moteur le fait, au lieu de parier qu'il naîtra hors champ en 400 images) et l'homme-sandwich — ⚠️ dont le juge de banc tombait pour une raison à lui : `retirer` ôte de la liste, pas de la **grille**, et `placeLibre` voyait encore le crieur qu'on venait d'ôter ; il tenait tant que le poste 0 était hors de la bulle du départ. 6 juges neufs dans `test_trottoir.py`, rouge-avant prouvé pour `abord_renonce` ; 1547 tests. Aperçu : l'artefact « La rue d'une tuile » |
| Pièces plus grandes que leur maison | **livré** | 14 sept. 2026 | **P3** | **correctif** | demande de Martin, mesurée : **35 des 45 portes** de la graine livrée ouvraient sur plus grand que leur bâtiment, jusqu'à **onze fois** (9 tuiles dehors, 98 dedans). Maintenant la pièce **se choisit à la taille du bâtiment** — la plus grande qui tienne, et rien du tout si même la plus petite déborde : la porte reste alors condamnée. **Quatre petites pièces neuves** (deux de 9 tuiles de plancher, une de 18, une de 21) et **26 pièces redessinées** plus petites ; la **parcelle d'un lieu garanti se taille à la mesure de sa pièce** au lieu d'espérer que le découpage au sort en fasse une de la bonne taille ; et **chaque famille de commerce ouvre au moins une porte**, parce que « tirer l'enseigne × être assez grand × gagner le dé » laissait quatre familles sur dix sans un seul intérieur. **0 débordement sur 5 graines**, contre 34 à 46 avant. 12 juges neufs |
| L'eau n'est plus un mur | **livré** | 14 sept. 2026 | **P3** | **correctif** | demande de Martin : l'eau était **littéralement un mur** (`MASQUE_PIETON` la comptait comme une façade). Maintenant : un **masque de nageur** pour le joueur et les agents (les passants, eux, n'y entrent jamais), le **souffle qui décide** — 8 points par tuile, le chenal du pont en coûte 88 sur 100 : un **pari** —, la **noyade par `Missions.hopital`** (une seule façon de perdre connaissance), le **char qui coule et qui est perdu** (jamais à la fourrière : couler ne doit pas devenir un remboursement d'épave ; le **bateau** flotte, et c'est sa fiche qui le dit), et la **police qui nage** au prix fort dans l'A\*. ⚠️ Le juge du pont est **reformulé, pas affaibli** : le pont est le seul lien **carrossable**. Le large de la baie est à **73 tuiles** de toute terre pour **40** au plafond absolu (café + estomac plein) : on n'y va pas. 6 juges neufs |
| La dépanneuse lève les roues | **livré** | 14 sept. 2026 | **P4** | ajout | demande de Martin : « la dépanneuse devrait embarquer les roues avant des véhicules qu'elle remorque, sauf les motos et vélos qu'elle embarque complètement sur sa plateforme ». C'était une **corde** : le char roulait à plat au bout d'un élastique, pointé **vers** elle, et le lien lâchait quand on l'étirait. Maintenant une **fourche** — écart fixe, **dans l'axe**, avant **levé de deux pixels** (l'ombre restée au sol, sans un seul cap de sprite en plus) — et un **plateau** pour ce que `vehicules.py` déclare `plateau` (la moto, le vélo) : elles montent **en entier**, ne heurtent plus rien, et se peignent **après** la remorqueuse. ⚠️ La remorqueuse **refuse d'avancer** là où sa charge ne passe pas (sans le garde-fou, elle reculait de 22 px dans la façade), et on **ne monte plus** dans un char remorqué. 2 juges neufs, 2 réécrits |
| Le taxi de Marco n'est pas à vendre | **livré** | 14 sept. 2026 | **P1** | **correctif** | demande de Martin : « il ne faut pas pouvoir vendre le taxi de Marco ». Le garage de Ti-Guy achète **n'importe quel char garé devant sa porte**, et M3 pose le taxi à `porte:garage` — cette porte-là. Vendu, il sort du monde, et ⚠️ **la mission ne rate même pas** (`monter` et `livrer` n'échouent que sur une **épave**) : elle reste prise, le téléphone ne sonne plus jamais. `aQui` — le contraire de `aToi` — dit à qui est le char, vient de la fiche (`prete` dans `missions.py`) et **ne s'efface jamais** : le taxi est à Marco avant, pendant et après. Le menu le dit au lieu de le cacher : « IL EST À MARCO ». 2 juges |
| Des feux pour piétons | **livré** | 14 sept. 2026 | **P4** | ajout | demande de Martin : « pour les piétons, il faut ajouter des lumières de priorité, et sinon ils ne passent pas ». La règle existait (`traverseeSure`) mais **personne ne la voyait** — et ⚠️ elle **se trompait d'un temps** : `!feuVert(...)` est vrai pendant l'**orange** aussi, donc les piétons s'engageaient pile quand les chars accélèrent pour vider le croisement, **240 images sur 960**. Maintenant `Monde.feuPieton()` rend **blanc / dégage / rouge**, le blanc ne croise ni le vert des chars ni l'orange, et il s'éteint **180 images avant** que les chars repartent (dégagement 120 + orange 60). **351 poteaux** posés par `carte.py` **sur la traverse** — un à chaque bout, jamais un par tuile — avec le **sens du passage** dans la fiche ; blanc fixe, orange **clignotant** au dégagement. ⚠️ **Sans feu (un T), on traverse quand c'est libre** : sinon un côté de rue entier devient un cul-de-sac pour la foule, et aucun juge existant ne le verrait. 2 juges neufs |
| Les terrains de banlieue | **livré** | 14 sept. 2026 | **P4** | ajout | demande de Martin : « les terrains des résidences doivent être plus fournis ». `_jardin()` ne posait que du gazon et un arbre par dix tuiles — or un terrain de banlieue est le **contraire du vide**. Maintenant : **38 entrées de voiture** qui vont jusqu'à la chaussée (une sur trois porte une **case**, donc une auto — mesuré 28 %), un **sentier de la porte à la rue** pour 100 % des portes, une **piscine ronde** (quatre tuiles, chacune son quart du disque), **cabanon / corde à linge / BBQ**. Le paquet passe de 410 à **413 Ko** bruts, 52 Ko gzip (plafonds 600 / 70). ⚠️ Trois défauts trouvés en chemin : une **plage qui suivait la boîte au lieu de la côte** (bancs de sable isolés en pleine baie), un **char plus long que sa case** qui finissait à cheval sur ses lignes, et un **témoin qui déréférençait `e.vers` après l'avoir mis à zéro** — le jeu plantait. 8 juges neufs |
| Les armes à feu | **livré** | 14 sept. 2026 | **P4** | ajout | demande de Martin : il n'y en avait que **deux** (pistolet, fusil à pompe) sur dix armes. Trois de plus, chacune pour une question : la **mitraillette** (automatique — on tient, la cadence rythme la rafale, la dispersion s'ouvre en 45 images et se referme quand on lâche), la **carabine** (230 px, un passant d'une balle, bornée par un juge à la demi-vue lue dans `base.js`) et le **cocktail Molotov** (en cloche, et un **brasier** de 5 s là où il casse — une entité invisible qui crache des particules, jamais une tuile repeinte). **Un coup de feu s'entend** : `Police.entendre`, rayon `bruit` de la fiche, l'agent hors du cône vient voir sans étoile. Vendues au marché noir seulement, munitions comprises. 4 juges Python + 3 au banc |
| L'objectif écrit par-dessus la course | **livré** | 14 sept. 2026 | **P4** | **correctif** | bug de Martin, capture à l'appui (« bug de hoverlap en haut ») : en taxi, « COURSE : POSTE DE POLICE 51M » et « FAIS TROIS COURSES — KLAXONNE POUR UN CLIENT 0/3 » étaient écrits l'un **dans** l'autre, tous les deux dorés, à un pixel de hauteur près. ⚠️ Rien n'était cassé : chaque ligne était à sa place. La ligne de boulot est collée sous le compteur (x 70, y 16) et la ligne d'objectif tombait sous les étoiles (4 + 11 + 2 = y 17) — mais elle est **centrée**, et une phrase de soixante-dix caractères centrée commence bien avant le milieu de l'écran (x 144 pour la course de Marco, en plein dans une ligne de boulot qui court de 70 à 181). Deux mises en page qui ne se connaissaient pas. La ligne de boulot, l'argent et l'heure **rendent leur boîte** au lieu de s'écrire et de s'oublier (et le boulot devient une ancre, donc le juge tactile de `test_navigateur.py` le voit aussi) ; à la place d'un `y` fixe, **une seule règle** : toute boîte du bandeau du haut que la ligne d'objectif chevauche **en largeur** la pousse d'une rangée vers le bas. C'est toujours elle qui cède, comme elle cédait déjà aux étoiles. 1 juge — la règle entière, pas le seul cas de la capture : la ligne d'objectif ne chevauche **aucune** autre ancre du HUD |
| Les feux s'allument pour vrai | **livré** | 14 sept. 2026 | **P2** | **correctif** | demande de Martin : « je veux que les feux de circulation et de piéton allument pour vrai ». ⚠️ **Ils n'ont jamais été allumés du tout, et personne ne l'a vu.** L'entité portait `decor: 'feu'`, et `Entites.dessiner` teste `if (e.decor)` **avant** `if (e.type === 'feu')` : la branche générique peignait le boîtier cuit et s'en allait. `dessinerFeu` n'a **jamais** été appelé — ni rouge, ni vert, ni blanc, un poteau noir à chacun des **482** coins de la ville. Aucun juge ne le voyait : ils parlent tous de l'**horloge** (`feuVert`, `feuPieton`, l'alternance, le dégagement), aucun du **dessin**. Et la nuit s'ajoutait à ça : sans lampe à elle, une ampoule ne reçoit que la **multiplication** du voile — le vert (46, 204, 113) tombe à (16, 76, 57), le blanc qui dit MARCHE (242, 242, 242) à (86, 90, 122), **plus sombre qu'un trottoir de midi**. Maintenant : les peintres nommés passent **avant** la branche générique, chaque ampoule a un **cœur** plus pâle qui la dit allumée, et elle **pose sa lampe** à la brune, de la couleur de sa phase, ramassée **en dessinant**. 5 juges neufs |
| Un poteau par coin, pas quatre | **livré** | 14 sept. 2026 | **P2** | **correctif** | retour de Martin, une fois les feux visibles : « il y en a trop, il faut que ce soit plus réaliste ». Mesuré, et c'était pire que trop : **les 124 feux de chars étaient plantés DANS un poteau piéton**, à la tuile près — 124 sur 124. `coinLibre` vise les coins nord-est et sud-ouest du croisement, exactement les bouts de traverse où `carte.py` pose ses poteaux, et il ne les voyait pas : il n'écarte que le décor **solide** (`grilleFixe`), où un feu n'entre jamais. ⚠️ **Et les écarter d'une tuile aurait fait un poteau de PLUS.** Le reste se groupait par deux à **une tuile** d'écart — 174 paires, pas une seule à deux : c'est le même coin de rue, et un vrai carrefour met ces têtes-là sur **le même mât**. Un mât porte donc la tête des chars **et** jusqu'à deux têtes de traverse, alignées sous elle. **484 poteaux → 186** (−61 %), **3 par croisement au lieu de 8**, et **les 360 traverses sont toujours montrées** : on a retiré des poteaux, pas de l'information. 2 juges neufs |
| Des feux tricolores, à la québécoise | **livré** | 15 sept. 2026 | **P2** | **correctif** | demande de Martin : « les feux pourraient être mieux — cherche sur le web des représentations visuelles. Assure-toi que les feux et les voitures suivent la même logique. Je veux des feux tricolores et un seul allumé à la fois », puis « mets les lumières qui tiennent d'un seul bout sur le poteau et la partie dans le vide au-dessus de la route », « moins de lignes pour les traverses piétons », « ne mets pas de lampadaire aux intersections, déplace-les ». La recherche donne mieux qu'une image : au **Québec les feux sont HORIZONTAUX**, et leurs lentilles ont des **formes** — **carré** rouge, **losange** jaune, **cercle** vert — pour qui ne distingue pas le rouge du vert. À 480 × 270, une forme se lit là où une teinte se devine. Donc : un **vrai tricolore par mât, une seule lentille allumée** ; un mât à **chacun des quatre coins** (ce qui règle le coin manquant), l'axe suivant sa **diagonale** pour que de n'importe quelle approche un feu de son axe soit en face ; une **potence** — le poteau planté au bord du trottoir, la tête en porte-à-faux **au-dessus de la voie**, et un seul gabarit lu par **miroir** ; les **bandes des traverses** ramenées à la norme (bande 0,50 m, vide 0,50 à 0,80 m : le vide est plus large que la bande, c'était l'inverse), avec un pas qui **divise la tuile** — le motif boitait à chaque couture ; et les **lampadaires écartés des coins**, qui sont la place du feu. ⚠️ **Une seule source** : `Monde.feuDeCirculation()` rend la couleur, `feuVert` en découle, le dessin en découle, le trafic obéit à `feuVert` — une lanterne ne peut plus montrer ce qu'un char ne respecte pas. ⚠️ Et ce que la passe a **découvert au passage** : les **lampadaires** étaient plantés sur les coins du croisement (la place du mât) — écartés de trois tuiles le long de la rue, **316 poteaux, zéro sur un coin** ; les **bornes-fontaines** aussi, et elles étaient **jaunes** et **en tuile** — les voilà **rouges**, en **décor** (donc une masse, une résistance, un bris), écartées des coins, et une borne défoncée **crache dix secondes** avec son bruit. Et un vieux juge a rougi sans qu'une ligne de son code change : celui de la fille de la Brume mesurait son écart **fuite comprise** — il tenait par chance, il mesure maintenant le **contraste** avec une passante sur la même fenêtre. 9 juges neufs |
| Le son de l'eau | **livré** | 14 sept. 2026 | **P2** | **correctif** | demande de Martin : « améliore le son de quand on va dans l'eau ». Il n'y avait **rien à améliorer** : on y entrait sur de la **tôle froissée** (`SFX.choc`, un accident de char), on nageait dans le **silence complet** — pas même un pas — et un char qui coule était muet de bout en bout. Trois bruitages neufs (`plongeon` ×2, `nage` ×3, `couler`) et le câblage des six moments que l'eau produit. ⚠️ **Et un cul-de-sac trouvé en chemin** : `v.conducteur === 'joueur'` — la chaîne — n'était **jamais vrai**, donc « IL COULE — SORS » ne s'affichait jamais et le joueur restait dans un char **retiré des entités**, immobile pour toujours au fond de la baie. 6 juges neufs |
| M15 La ville te parle | **livré** (1re vague) | 14 sept. 2026 | **P4** | ajout | tout ce qui ne demandait **aucun son neuf**. ⚠️ **La rue se tait quand tu sors une arme** — `Son.Rumeur` réglait déjà son volume sur le nombre de gens autour, il ne manquait qu'une **raison** de le faire tomber ; elle tombe d'un coup, remonte en quatre secondes, et **crie** après un coup de feu. ⚠️ **Les répliques : moins souvent et jamais les mêmes** — `audio.VOIX` promettait « jamais deux fois de suite le même » et le moteur tirait par `Math.random()` **sans mémoire** ; le tirage passe maintenant par `B.rng()` (donc reproductible, donc jugeable) et écarte les dernières. **Parler devient une chance** (35 %), pas une certitude. ⚠️ **Le repli du Clairon enseigne** : un matin calme apprend une chose que tu n'as **pas encore faite**, jamais deux fois la même, et quand il n'y a plus rien à apprendre il redevient « rien à signaler ». ✅ **Les six leçons ont leur voix** (16 sept. 2026, 350 Ko) : `exporter()` les déclare tout seul, sans une ligne de code. **Reste à générer** (crédits + une oreille) : la radio qui parle, la police à la radio, les bruits de quartier, le souffle du joueur, et les banques de répliques par contexte. ⚠️ **Deux choses mesurées en chemin, à savoir avant de reprendre** : (1) le **budget audio** (950 Ko) est la vraie contrainte de la 2e vague — 18 clips l'ont fait sauter à 1,16 Mo, et il faudra soit le relever, soit générer en 22 kHz comme les répliques de passants ; (2) « la pub change quand tu achètes le commerce » **ne peut viser que ce qui s'achète** — Chez Gus et Boutique Rosa existent mais ne se vendent pas ; les quatre propriétés sont le kiosque, le bar, le garage et l'hôtel. 11 juges neufs |
| Les amuseurs de rue font un vrai spectacle | **livré** | 14 sept. 2026 | **P2** | **correctif** | demande de Martin : « les amuseurs de rue ne font rien et sont ennuyants ; je veux qu'ils soient animés, qu'il y ait toujours entre 3 et 5 personnes autour, que le musicien fasse vraiment de la musique (5 musiques différentes), et des jongleurs et des échassiers ». Ils tiennent leur coin **au centre-ville**, là où il y a du monde — et la ville y met plus de passants, la périphérie moins |
| L'intérieur à la mesure du bâtiment | **livré** | 14 sept. 2026 | **P3** | **correctif** | demande de Martin : « je veux que l'intérieur de bâtiment soit proportionné à l'extérieur, tu avais mal compris ». La fiche d'hier n'a tenu que la moitié de la promesse — elle interdisait à la pièce de **dépasser** son bâtiment, rien ne l'obligeait à le **remplir** : 13 % pour un bloc de 59 × 8, et une pièce de six tuiles de profond dans un bâtiment qui en fait quatre. Maintenant : le plancher fait **exactement** la boîte du bâtiment au-dessus de sa vitrine, à toutes les portes et sur cinq graines ; une longue façade se **coupe en vitrines de huit tuiles**, chacune sa porte, son enseigne et sa pièce ; les commerces et logements ordinaires sont **posés** à la mesure (`MOBILIER`, dix palettes) et les seize lieux garantis gardent leur plan dessiné — c'est leur bâtiment qui se taille à eux |
| Toute la musique générée par IA | **livré** | 14 sept. 2026 | **P2** | **correctif** | demande de Martin : « je veux que toutes les musiques soient des musiques générées par IA ». Les **15 pièces écrites en notes** (thème du menu, 2 stations de char, 5 ambiances de district, poursuite, bagarre, 5 pièces du musicien de rue) deviennent des mp3 ElevenLabs Music — c'est la porte que `musique.py` annonce depuis le premier jour : « le jour où Martin veut une vraie pièce jouée par de vrais instruments, elle se posera **par-dessus** comme les radios ». La synthèse reste le **filet** : un fichier absent, et le séquenceur reprend |
| M11 La police apprend | **livré** (3 vagues) | 15 sept. 2026 | **P4** | ajout | ⚠️ **LE CASIER PÈSE**, et c'est tout le jalon : chacune des trois vagues en tire une conséquence. **1.** Il allonge la portée du cône des agents (+4 % la page, **plafonné à +50 %** — sans ce plafond, vingt pages feraient voir la police à seize tuiles en pleine nuit et il n'y aurait plus une ruelle où souffler). Pour le joueur seulement : c'est un signalement, pas une paire de jumelles. Et le carnet du poste le **dit** — une règle qu'on subit sans jamais la lire n'est pas une règle, c'est une malchance. **2.** On peut effacer une page, et c'est un **choix** : **Me Desjardins** (table du fond du Brouillard) vend la certitude — une page tout de suite, cher, jamais deux fois le même jour — ou une **provision** qui efface l'amende de la prochaine arrestation ; ⚠️ *sans amende, pas innocent* : la page s'ajoute, les armes partent, le char va au lot. **Électronique Turcotte** (La Shop, le seul lieu neuf) vend le **pari** : on paie d'avance, on revient le lendemain, et on ne sait pas ce qu'on a acheté — rien une fois sur trois, jusqu'à trois pages d'un coup, et **une page DE PLUS** une fois sur cinq. ⚠️ *L'espérance du pari reste sous la certitude à prix égal, à dossier mince comme à dossier épais* — sinon l'avocat ne sert plus à rien et le choix disparaît. **3.** Il transforme les passants en délateurs : **le stool** n'a rien vu, il a reconnu ta FACE, il va téléphoner, et ce qu'il donne au poste est un **plancher** d'étoiles, pas de la chaleur. On le paie, on l'assomme, ou **on change de tête** — le seul levier gratuit, puisque le casier ne redescend qu'en payant. ⚠️ *Il ne naît jamais dans ton dos.* Et **le bouclier humain** : la police ne tire plus **et recule**, mais il se débat, il se dégage à douze secondes, et le compteur monte tant qu'on le tient. ⚠️ *Une sortie de secours, jamais un abri.* 26 juges neufs |
| Le bouclier se tient | **livré** | 15 sept. 2026 | **P2** | **correctif** | retour de Martin : « pour le bouclier humain, il faudrait tenir le bouton plus longtemps pour éviter de le faire par accident ». ⚠️ **Le bouclier est LE DERNIER de la chaîne d'ACTION** — ce que le bouton fait quand il n'a rien trouvé d'autre à faire —, donc exactement ce qu'on déclenche sans le vouloir : on visait une porte d'un pas trop loin, une arme par terre, un char, et on repartait avec un bonhomme dans les bras et **deux étoiles** qu'on n'avait pas demandées. La pression **arme** la prise, le maintien la prend (`saisie_s` = 0,5 s, `Combat.majSaisie`). ⚠️ La demi-seconde se juge **des deux côtés** : plus longue qu'une pression (le coup fort, l'autre bouton qu'on tient, en demande un tiers) et plus courte que la **cadence de tir** de la police (1,2 s) — une sortie de secours doit s'ouvrir avant la deuxième balle. ⚠️ **Et l'invite le dit, puis se remplit** : « ACTION : BOUCLIER HUMAIN — TENIR », et le bandeau se remplit pendant qu'on insiste ; un bouton qui demande qu'on insiste sans le montrer ne se lit pas comme un bouton qui résiste, il se lit comme un bouton brisé. ⚠️ La prise rejuge `otageSousLaMain` **à chaque image** plutôt que de garder la personne visée : le passant qui s'éloigne, la porte ou le char qui entre à portée la font tomber — le bouton ne fait jamais autre chose que ce que l'écran promet. ⚠️ **Un défaut de décor trouvé au passage** : les juges du bouclier **dégelaient** leur victime (`etat = 'flane'`) au milieu de la chaussée, et un piéton sur la chaussée court vers le trottoir le plus proche à `pieton_course` — instantanée, la prise ne s'en apercevait pas ; tenue une demi-seconde, elle tombait à la vingt-cinquième image. Les passants du jeu sont sur le trottoir : la victime reste **figée**, comme `o.poser` la rend. Et le juge du recul prend l'otage **avant** de lancer l'agent, puis le lâche et remesure — vingt balles cherchaient le joueur, et celui qu'on voulait prendre se tenait dans la trajectoire. 2 juges neufs (1 Python, 1 de banc), rouge-avant prouvé : sans le maintien, une pression pose 48 points de chaleur |
| Une passe visuelle sur les pâtés de maison | **livré** | 15 sept. 2026 | **P2** | **correctif** | demande de Martin : « fais une passe visuelle d'amélioration de tous les pâtés de maison », puis « les affiches des commerçants doivent être au-dessus du mur » et « les clôtures doivent clôturer les terrains, pas juste être là seules ». Quatre morceaux, un seul sujet : ce qu'on voit d'un îlot. **Le sol** — trottoir, herbe, ruelle font **43 % de la ville** (28 %, 10,5 %, 4,7 %) et se peignaient avec **quatre** tuiles de 16 px tirées sur `hash2 % 4` ; seize usures maintenant (`Monde.USURES_DE_SOL`, la leçon de l'asphalte du stationnement appliquée à trente fois la surface) et, sur le trottoir, une **dalle de deux tuiles de côté** : il peignait son joint sur *chaque* tuile, en haut et à gauche — un trait tous les seize pixels sur le quart de la ville, et ce qu'on lisait c'était la grille de la carte. Fissures, rapiéçages, taches, mousse au joint ; touffes, plaques de terre et pissenlits dans le gazon ; goudron, huile, gravier dans la ruelle ; et **huit grains de toit** au lieu de quatre, avec membrane rapiécée, flaque et coulée de rouille — un entrepôt de La Shop couvre trois cents tuiles d'un seul tenant, quatre grains dessus font un papier peint. ⚠️ Deux règles tiennent tout le bloc, et elles viennent du stationnement : **aucune usure ne touche le bord de la tuile** (sinon on redessine la grille), et **une usure est un dessin, pas du bruit** (trois ou quatre variantes sur seize). **Les allées de parc** : glyphe `g`, de la **poussière de pierre**. Quatre allées de deux tuiles et une place de 5 × 5 au cœur, ça fait près de la moitié d'un îlot — peintes avec le béton de la rue, nos parcs étaient des dalles avec du gazon dessus. Ce n'est pas du sable non plus : la plage borde l'eau, l'allée traverse la pelouse. **L'enseigne** monte **au-dessus du mur** (`ENSEIGNE_Y` négatif : elle déborde de 12 px sur la tuile de toit) ; le bandeau, l'auvent et la vitre se partageaient les 16 px d'*une* tuile — cinq pixels pour le nom, quatre pour l'auvent, trois pour la vitrine. Le mur dégagé donne un auvent de 5 px et une **vitrine de 9** (elle triple, et c'est elle qui s'allume la nuit). Ça tient à un invariant que personne n'avait écrit — **au-dessus d'une devanture il y a du toit, sur toute sa largeur**, vrai 105 fois sur 105 — et un juge le dit maintenant tout haut, sur cinq graines. **Les clôtures** : mesuré sur la ville livrée, **361 tuiles en 80 morceaux, dont 69 sans un seul coin** (216 tuiles de barre droite) et **24 toutes seules**. Trois sources, trois torts : le terrain vague ne peignait qu'**un** côté et **une tuile sur deux** (le code le disait : « à demi n'est pas un juge »), la cour de gang que la rangée du sud, et le U de `_jardin` se posait tuile par tuile pendant que `poser_cloture` en refusait **en silence**. `clore()` pose des **enceintes** — tout ou rien à 75 %, une trouée garantie qui donne sur du marchable, aucune tuile laissée seule — et `elaguer_les_clotures()` enlève après coup ce que la ville leur mange (le glyphe de remplacement se lit dans les voisines, comme `defoncer`). ⚠️ **Une clôture ne remplace ni un mur ni une chaussée** : sans ce garde-fou, le barbelé de la cour des Skateux mangeait deux colonnes de leur stationnement et « il y a un tremplin à La Pointe à tout coup » redevenait une légende. Et la **cour arrière d'un bungalow se clôture** enfin — la banlieue clôturait ses terrains *vides* et pas ses maisons, l'inverse de ce qu'on voit par la fenêtre. Résultat : **483 tuiles en 41 enceintes, zéro barre droite, zéro tuile seule**. ⚠️ **`Des.brule()`** : le barbelé et le terrain vague tiraient dans le dé PRINCIPAL, un coup par tuile. Cesser de tirer décale toute la suite du hasard (`batiment_forme` l'écrivait déjà) — mesuré, douze scènes d'amuseur disparaissaient du Faubourg et « un amuseur naît au centre-ville » tombait, pour une histoire de clôture. On brûle ce qu'on ne tire plus, et on le dit. **Et un rond de terre au pied des arbres de trottoir** (retour de Martin, une fois la passe vue) : un arbre planté dans le béton sans rien à son pied n'est pas planté, il est *posé* — la place publique du Faubourg en portait quatre debout sur des dalles. C'est la **légende** qui décide (`terre` sur l'herbe, le sable et l'allée de parc), pas le dessin, et c'est une **couche peinte** cuite avec le morceau : rien ne s'y cogne, et elle passe sous les entités — repeinte à chaque image, elle recouvrirait les pieds de qui marche juste au nord de l'arbre. ⚠️ C'est la **bordure** d'un pixel qui fait la fosse, pas la terre : sans la coupe dans le béton, le rond brun se lit comme une tache. 583 arbres sur 596 sont sur du gazon — le jour où l'on plantera des arbres de rue pour de bon, chacun aura sa fosse sans qu'on touche à une ligne. ⚠️ Trois juges de banc tenaient à **un pixel**, au **premier décor de la liste** et à **deux pas près** : re-semés et resserrés sur ce qu'ils mesurent vraiment. 11 juges neufs |
| Une clôture, pas deux | **livré** | 15 sept. 2026 | **P2** | **correctif** | bug de Martin, capture à l'appui : « je ne devrais pas voir de double clôtures d'épais comme ça, seulement une d'épais ». Mesuré : **15 carrés de 2 × 2 tuiles de clôture** sur la graine livrée, jusqu'à **17** sur d'autres — chaque cour arrière ceinturait son *propre* rectangle, donc deux terrains voisins posaient **deux palissades collées** sur la même ligne mitoyenne. Vu du jeu c'est pire que laid : une clôture s'enjambe en une seconde **immobile**, passer d'une cour à l'autre en coûtait donc **deux**, et à la fourrière la seconde était du **barbelé** — qui ne s'enjambe pas du tout. Une règle, deux endroits où elle s'applique : `cote_deja_longe()` dit qu'un côté que **longe déjà une course de clôture** est un côté clôturé, et `clore()` n'y repose rien — le terrain reste fermé par celle du voisin, une tuile plus loin. ⚠️ **Les coins, eux, se posent quand même** : un coin tient deux côtés à la fois, et c'est lui qui fait *tourner* la course que cherche `elaguer_les_clotures`. La fourrière, elle, n'a pas le choix — **une seule grille**, c'est tout son lot — alors c'est au voisin de s'effacer (`degager_les_doubles()`, avant la première tuile de grillage ; `_terrain_vague` passe avant elle, par `_ilot_bati`). ⚠️ **« Sans voisine » se compte sur la VILLE**, pas sur la seule enceinte qu'on pose : le garde-fou anti-tuile-seule de `clore` ne regardait que ses propres tuiles, et du jour où deux voisins partagent une clôture, le coin d'une cour dont la suite est **chez le voisin, déjà au sol** tombait — la colonne mitoyenne perdait son tournant et l'élagage l'emportait à son tour. **Deux palissades collées devenaient aucune**, mesuré avant de s'en apercevoir. Résultat : 401 → 386 tuiles sur la graine livrée, **zéro carré de 2 × 2 sur 40 graines**. 1 juge neuf (`test_une_cloture_fait_une_tuile_d_epais`, cinq villes) |
| M10 L'argent sale | **livré** (trois vagues) | 15 sept. 2026 | **P4** | ajout | **1re vague : la dette de Rocco**, celle qui donne une raison de se lever le matin. ⚠️ **Aucun lieu neuf, et c'est un choix de design, pas une économie** : un shylock ne tient pas un comptoir où l'on vient payer, il **envoie du monde**. Les rappels arrivent, puis les hommes de main te trouvent où que tu sois — et c'est À EUX qu'on paie. La collecte devient une scène au lieu d'un menu. ✅ **2e vague livrée** (15 sept. 2026) : **les guichets** — une caisse de banque posée dans la rue, encastrée **sous une vitrine**, sur l'abord, servie depuis la dalle (12 dans la ville, espacés, tirés dans leur propre dé) ; `lourd: 2.5` sur la fiche du décor — un quatrième mot dans `verifier_ce_qui_casse.py`, toujours avec `casse` — fait qu'il **ne cède qu'au camion ou à l'autobus**, une berline s'y arrête ; il cède aussi à huit balles de pistolet ou à l'explosion d'à côté. Quand il cède, **la caisse tombe en six liasses** (300–900 $) qu'on ramasse en passant, à pied ; c'est un **délit à deux étoiles** quoi que ce soit qui l'ait ouvert, et il se répare au lever du jour comme le reste. **Le skimmer** s'achète chez Josée (350 $ — pas une arme : `MARCHE_NOIR.objets`), se pose sur un guichet par ACTION, **lit pendant la nuit** (350–900 $) ou se fait trouver (trois fois sur dix), et se vide au même guichet le lendemain ; trois posés à la fois au plus, et l'invite du HUD dit exactement ce qu'ACTION va faire (poser, attendre, vider). **L'assurance** au garage : Ti-Guy couvre ce qui est garé devant, sans demander à qui c'est — la moitié du prix neuf, **jamais plus de 900 $**, prime de 30 % ; le char qui brûle, plie ou coule ouvre une réclamation qu'on **encaisse au garage** ; à la troisième, **l'assureur enquête** : quatre jours sans police, une page au casier, puis le dossier se classe. ⚠️ **La règle de tout M10, jugée char par char** : la caisse d'un guichet vaut moins qu'une journée honnête, trois skimmers moins qu'une journée de taxi, et la fraude — sur les 300 s qu'elle prend au moins — moins que le taxi **à l'heure** ; frauder avec un char qu'on a payé perd de l'argent, ce n'est payant qu'avec un char volé. 7 juges Python + 4 de banc ; 1558 tests. ✅ **3e vague livrée** (15 sept. 2026) : **la run de Sven** — la cale du Norvégien, un comptoir de contrebande sur les planches des Quais (un ambulant `sur: "quai"`, sans tarif ni coupon : ses prix vivent dans `economie.CONTREBANDE`). Cigarettes et boisson — ⚠️ pas de drogue, tranché — s'achètent **dans le coffre du char garé à côté** (90 px ; sans char, la cale ne vend rien : elle ne se porte pas), huit caisses au plus, et **le prix monte de 10 % par caisse déjà prise dans la journée**. Elles se revendent au comptoir de quatre commerces (dépanneur, bar, cantine, casse-croûte — la ville n'a pas de taverne) au **prix du jour du district**, tiré du jour et du district par `hash2` (pas un dé), affiché au comptoir même sans cargaison, entre 0,7 et 1,3 fois le prix de vente : le mauvais district fait **perdre** de l'argent, et c'est jugé. Un char qui brûle ou coule emporte la run ; **la police fouille** : arrêté, le char saisi part au lot sans ses caisses. ⚠️ Jugé : la meilleure run possible (coffre plein, vendu au meilleur prix qui existe) vaut moins que la plus grosse mission de l'arc et moins que le taxi **à l'heure** sur les 240 s qu'elle prend au moins. 6 juges Python + 3 de banc ; ⚠️ un juge de défi tombé pour une raison à lui — il lisait le **dernier** message du HUD après deux minutes ; le vendeur de la cale a décalé les dés, un facteur en colère a fait le reste — lit maintenant le verdict à l'instant où il tombe. 1567 tests. **M10 est livré en entier** : la dette, les guichets, le skimmer, l'assurance, la run |
| Ça travaille : chantiers et démolitions | **à faire** | — | **P4** | ajout | demande de Martin : « des maisons ou commerces ou des rues en construction, avec des pelles, des boules de démolition, des grues ». ⚠️ Un chantier est une **horloge**, pas un décor : cinq phases (condamné → boule de démolition → terrain rasé → grue et échafaudage → bâtiment neuf), une phase tous les trois ou quatre jours, et au bout de vingt jours **la ville n'est plus celle du premier matin**. La pelle, la grue et la boule sont d'abord du **décor animé** (une articulation, comme les lanternes d'un feu) ⚠️ parce que la refonte des véhicules interdit d'ajouter un char avant elle ; conduisibles ensuite. Plus un réservoir : tas de terre qui fait rampe, conteneur qu'on pousse, plaques d'acier qui claquent, signaleur qui arrête le trafic, trou de fondation en eau basse |
| M12 La ville vit | **en cours** (huit vagues livrées) | 15 sept. 2026 | **P4** | ajout | tramway, traversier à l'heure, tempête de neige et charrue, **une famille d'entraves** (réparations, fermetures avec DÉTOUR, bris d'aqueduc, pannes) tirées d'une liste que Python valide, nids-de-poule, nuit de déneigement qui envoie les chars au lot, feux au clignotant la nuit, heures de pointe qui ont une direction, la ville coupable d'elle-même, l'arrêt d'autobus, les éboueurs, goélands et chats ✅ **1re vague livrée** (15 sept. 2026) — *le rythme de la ville*, trois choses qui la font changer d'une heure à l'autre **sans regénérer une seule tuile**. ⚠️ **Les feux passent au clignotant la nuit** : de 20 h 40 à 6 h, l'**artère** (la rue la plus large du croisement) clignote jaune et la rue secondaire clignote rouge. `feuDeCirculation` reste **la seule source** — le dessin de la lanterne en découle, `feuVert` en découle, et le trafic obéit à `feuVert` : un clignotant ne peut donc pas montrer une couleur que le char ne respecte pas. ⚠️ Le rouge qui bat est un **STOP**, pas un mur : on s'immobilise puis on passe — sans cette ligne, le trafic de nuit attendait la fin des temps. Le bonhomme s'éteint avec le cycle (on traverse à vue). La lentille pulse : la douille reste, la lumière part. ⚠️ **Les heures de pointe ont une direction** : le matin (6 h 30 → 10 h) le trafic converge vers le Faubourg, le soir (16 h 20 → 20 h) il s'en disperse — en **pondérant le choix de sortie** aux croisements, jamais en touchant au champ de direction, qui est fixe et jugé. `penchant` est la **part** des chars qui suivent le mouvement (0,45) : le reste tire au sort comme toujours, sinon la ville entière roule dans le même sens et ce n'est plus une heure de pointe, c'est une évacuation. ⚠️ **Les nids-de-poule** : 30 à 90 tuiles de chaussée qui secouent la caméra et coûtent deux points de carrosserie — **jamais dans un croisement** (on y freine déjà, et une secousse au milieu d'un virage se lit comme un bogue de collision), jamais sur une ligne d'arrêt, jamais deux collés, et un **répit** de 30 images pour qu'un char lent ne le paie pas à chaque image. Un char à l'arrêt n'y tombe pas. Son bruit est synthétisé (le talonnage, le gravier, la tôle qui résonne). ⚠️ **Un vrai trou dans les barrières, trouvé au passage** : une barrière fermée n'était consultée que sur les **voies** — un char qui abordait le pont *depuis la boîte* d'un croisement en sortait dessus sans que rien ne le lui demande, et une fois sur le tablier il était **dedans**, donc exempté, et il traversait tout du long. Une sortie barrée n'est plus une sortie (`peutSortir`). Le juge du demi-tour l'a attrapé le jour où les dés ont changé la route d'un char ; le trou, lui, était là depuis le premier jour des barrières. ⚠️ Et deux juges des lanternes testaient « la nuit » **à minuit** — heure où les feux clignotent désormais : ils visent l'heure qui est sombre sans être clignotante. 7 juges neufs (`test_ville_vit.py`), rouge-avant prouvé sur les trois règles ; 1611 tests. ✅ **2e vague livrée** (15 sept. 2026) — *les entraves du jour*. Python calcule **une fois** la liste des voies qu'on peut fermer, le paquet la transporte, et la **graine du jour** en tire une : la ville change d'un jour à l'autre sans qu'on regénère une seule tuile. ⚠️ `hash2(jour, …)`, jamais `B.rng()` — un décor qui change la ville ne consomme pas un dé du jeu. ⚠️ **Une entrave ne coupe jamais la ville en deux, et elle ne le peut pas PAR CONSTRUCTION** : elle ferme **une voie** d'une rue qui en a deux dans le même sens, donc le champ de direction ne bouge pas d'une flèche et `voies_bloquees` rend exactement ce qu'il rendait. C'est ce qui permet de se passer du juge de connexité à la construction — il coûte 14 ms, et en valider cent doublerait le temps de bâtir la ville ; la rue **entière** barrée, elle, l'exigera, et viendra avec son panneau DÉTOUR. Hors croisement, hors ligne d'arrêt, espacées de 20 tuiles. ⚠️ Le chantier est une **barrière comme les autres** — rien de neuf dans le mécanisme, seulement dans le choix : il arrête les chars et pas les jambes, il se force en poussant les cônes (8 points), il se voit, et le carnet le liste. ⚠️ **Et le trafic se DÉPORTE avant de faire demi-tour** : une voie fermée laisse sa voisine ouverte, y rebrousser chemin pour trois cônes serait absurde — c'est la voie d'à côté qui tranche, pas le genre de la barrière. Une voie barrée n'est pas non plus une voie où se déporter. 3 juges de plus, rouge-avant prouvé ; 1614 tests. ✅ **3e vague livrée** (15 sept. 2026) — *la rue barrée*. ⚠️ **Mesuré, et c'est ce qui a tout décidé** : barrer la MOITIÉ d'un tronçon laisse l'autre moitié en **cul-de-sac dans les deux sens** — la voie qui monte n'a plus d'entrée, celle qui descend n'a plus de sortie. Le juge de connexité de M1 a refusé les **vingt-six premières candidates**, toutes pour cette raison. Une rue barrée couvre donc **tout son tronçon, d'un croisement à l'autre** : fermée en entier, elle disparaît du graphe et la grille route autour — c'est d'ailleurs ce que « rue barrée » veut dire. `voies_bloquees` tranche à la construction, une fois, sur 20 candidates au plus (il coûte 14 ms pièce). Jamais sur le pont. ⚠️ Elle bloque **tout son rectangle** et pas sa seule couronne : une chaussée de quatre tuiles de large aurait laissé passer le monde par le milieu — les cours, elles, gardent leur couronne. Sa **barricade** se peint aux deux bouts seulement : on ferme une rue par ses extrémités, on ne la clôture pas. Elle coûte 14 points à forcer contre 8 pour des cônes. ⚠️ **Une seule entrave par jour**, tirée dans les deux listes réunies : c'est ce qui évite d'avoir à juger les **combinaisons** — deux fermetures valides séparément peuvent, ensemble, isoler un bloc. Et le trafic n'y entre jamais : une sortie barrée n'est pas une sortie, donc les chars tournent **avant**, au croisement, comme devant un vrai détour. 1 juge de plus et deux rouverts aux deux genres ; 1615 tests. ✅ **4e vague livrée** (15 sept. 2026) — *l'entrave se lit*. ⚠️ **Une fermeture sans détour affiché n'est pas une entrave, c'est un piège** : on arrive, on ne passe pas, et rien ne dit par où aller. Le **panneau DÉTOUR** se pose au-dessus de la barricade, aux deux bouts, et sa flèche montre le côté où la rue continue. Il a coûté deux défauts avant de dire vrai : il cherchait la rue de rechange **dans l'axe de la rue barrée** (elle n'y est pas — le détour croise la rue barrée à son bout, pas à son milieu), puis, une fois qu'il regardait au bon endroit, il **se taisait aux carrefours** parce que les deux côtés se valent. Il sort donc du rectangle par le bon bout, et quand les deux mènent quelque part il montre la **droite** : une flèche qui hésite est un panneau pour rien. ⚠️ **Les ouvriers au chantier** : un ou deux, plantés sur la voie fermée, et **intouchables comme les enfants** — un chantier où l'on fauche l'équipe au premier passage n'est pas un chantier, c'est une cible. C'est une propriété de l'**entité**, pas de l'archétype : un ouvrier qui rentre chez lui reste un passant comme un autre, et un juge le vérifie. Ils ne comptent pas dans la foule : ils ont un poste, comme l'homme-sandwich. 2 juges de plus ; 1617 tests. ⚠️ Rouge-avant prouvé pour les ouvriers ; celui du panneau ne l'est pas — il affirme une vérité utile (chaque bout parle, et montre une chaussée qui n'est pas la voie barrée elle-même) et il a attrapé les deux défauts ci-dessus en cours de route, mais la neutralisation évidente lui échappe. ✅ **5e vague livrée** (15 sept. 2026) — *le char en panne*, une entrave qu'on n'a **pas** vue venir : ni cônes, ni panneau, ni liste validée par Python. Un camion s'arrête en travers d'une voie, ses **feux de détresse** battent aux quatre coins de sa caisse, et il repart au bout de quarante minutes de jeu — une entrave du jour change la ville, une panne ne fait que la contrarier. Le trafic sait déjà quoi en faire : il se déporte (`obstacleDevant` voit les chars à l'arrêt), exactement comme devant un piéton planté sur la chaussée. ⚠️ Elle a coûté **deux leçons, et les deux étaient déjà écrites dans le dépôt**. (1) **Un décor ne tire pas dans le dé du jeu** : la panne prenait sa couleur et sa place au hasard commun, et **quatre juges sont tombés d'un coup** — aucun ne parlait de pannes. Sa couleur et sa place se tirent maintenant par `hash2` du jour et de l'heure, `creer` n'appelle plus le dé quand on lui donne une couleur, et un juge compte les dés sur six cents images pour le tenir. (2) **`laisse` veut dire « le JOUEUR l'a abandonné ici »** — marquer la panne ainsi la faisait suivre par la fourrière, et le HUD nageait dans « la fourrière va passer » pendant qu'un camion battait ses feux. Elle ne compte pas non plus dans les places de stationnement de la ville. ⚠️ Et un juge d'amuseurs a été **resserré sur ce qu'il dit mesurer** : il annonçait mesurer le GESTE, mais il le mesurait dans une ville vivante — il a suffi qu'un camion tombe en panne au bout de la rue pour que le jongleur devienne témoin, s'en aille, et ne montre plus que deux dessins. Il tient maintenant l'amuseur sur sa scène. 3 juges neufs ; 1620 tests. ⚠️ Jugé dans un **worktree isolé** : deux autres sessions écrivaient dans l'arbre. 🔧 **Réparé après coup** (15 sept. 2026) — *une panne ne s'efface pas sous celui qui la tient*. Monter dans la remorqueuse en panne et la voir disparaître : l'heure finie, le compte à rebours retirait le char de la ville **sans regarder qui était dedans**, et le joueur restait accroché (`dansVehicule`) à une entité absente de `B.entites` — plus mise à jour ni dessinée, donc invisible et immobile, et rien ne le lui disait. La charge sur la fourche et un char de mission partaient pareil. Tenu, le char cesse simplement d'**être en panne** (ses feux s'éteignent) et redevient un char ordinaire : c'est `peupler` qui l'oubliera, loin et hors champ. La liste est **exactement la sienne**, et ce n'est pas un hasard — « qui tient ce char ? » n'a pas deux réponses selon qui pose la question. 1 juge neuf, rouge-avant prouvé ; 1645 tests. ✅ **6e vague livrée** (15 sept. 2026) — *la ville est coupable d'elle-même*, première moitié : **un vol de char sous tes yeux**. ⚠️ Le **vol à la tire entre passants existait déjà** (`majPickpocket`, livré avec les sortes de gens) — vérifié avant de risquer de le réécrire. Voici l'autre : un passant ordinaire repère un char garé, marche dessus d'un pas pressé, ouvre la portière et s'en va avec ; la rue crie **AU VOLEUR** et s'écarte. ⚠️ **Il se voit, ou il n'a pas lieu** : on ne déclenche un vol que sur un char **à l'écran** — un vol hors champ est du travail qu'on fait pour personne. ⚠️ **Et ce n'est PAS le joueur qui le paie** : la police du jeu est centrée sur lui, et signaler le geste d'un autre lui mettrait une étoile — un juge vérifie qu'il n'en écope aucune. (« Ça peut te tomber dessus » reste à faire, avec son propre juge.) ⚠️ Le voleur ne touche **ni au char du joueur, ni à celui qu'il a laissé** : un char abandonné appartient à la fourrière, pas aux voleurs — deux systèmes qui se disputent le même char, c'est l'un des deux qui ment, et le juge de la fourrière est justement tombé le jour où un voleur lui a pris le sien. ⚠️ Et **pas de réplique neuve** : un juge exige que chaque parole soit le métier de quelqu'un, et « AU VOLEUR » existait déjà chez le pickpocket — c'est la rue qui parle, pas le voleur. Le tirage se fait à l'empreinte de la minute, jamais au dé du jeu. 3 juges neufs, rouge-avant prouvé deux fois ; 1625 tests. ⚠️ Jugé dans un **worktree isolé** : une autre session écrivait dans l'arbre. Restent, pour les vagues suivantes : la **bagarre de gangs à leur frontière** (elle demande un état d'attaque qui vise quelqu'un d'autre que le joueur — aujourd'hui `attaque_joueur` ne sait viser que lui), le bris d'aqueduc (il demande `carte.py`, occupé), le tramway, le traversier, la neige et la charrue, la nuit de déneigement, la ville coupable d'elle-même, l'arrêt d'autobus, les éboueurs, les goélands et les chats ✅ **7e vague livrée** (15 sept. 2026) — *la bagarre de gangs à leur frontière*, deuxième moitié de « la ville est coupable d'elle-même ». Le vol de char se passait **de travers** du joueur ; celle-ci se passe **sans lui**. Deux gangs se tombent dessus là où leurs districts se touchent — cinq frontières sur toute la carte, que `pietons.frontieres()` calcule des **deux** fiches : les rectangles viennent de `carte`, qui ne sait pas qui tient quoi ; les gangs viennent de `pietons`, qui ne sait pas où sont les rectangles. C'est `definitions.assembler` qui les marie, une fois, au démarrage — « une fiche que le navigateur ne lisait pas » a son symétrique, **« un calcul que Python ne pouvait pas juger »**. ⚠️ **Ce qui a coûté cher n'est pas la rixe : c'est que `attaque_joueur` est le SEUL état d'attaque du jeu, et que TROIS mécanismes y ramenaient tout le monde.** `alerter` retournait contre le joueur toute gang à portée d'un coup, `blesser` faisait de même du blessé, et `majAttaque` y ramenait tout piéton qui finissait son geste : six hommes qui se tapaient dessus se retournaient contre lui au premier poing — et il n'avait rien fait, il passait par là. Les trois sont corrigés, **chacun sous son rouge-avant** (115, 30 et 184 images de rixe retournée contre lui). ⚠️ **Et un quatrième, trouvé au passage et plus vieux que la vague** : un piéton en plein coup n'avait pas de branche à lui dans la machine à états et tombait dans le DERNIER `else`, celui qui flâne — il pouvait donc décider de s'arrêter au milieu de son geste. `majAttaque` refuse alors de continuer (l'état n'est plus `attaque`), le coup reste **en suspens pour toujours**, et l'homme repart faire autre chose. Une gang qui attaquait le joueur le faisait déjà ; ça ne se voyait pas, parce qu'elle y revenait toute seule. ⚠️ **`stats.tues` était le compteur de la VILLE, pas celui du joueur** : toute mort de piéton y entrait, y compris les passants fauchés par un char du trafic. Il tire la manchette du Clairon (« UN MORT DANS LA RUE », « NUIT ROUGE AU FAUBOURG ») et le bilan de fin de mission — créditer le joueur d'une rixe qu'il a regardée de loin est un **mensonge imprimé**. ⚠️ **La seule inimitié que la ville connaisse** s'écrit dans `arcDeMelee` et pas dans l'état `bagarre` : c'est le même test qui empêche un coup perdu de faucher le badaud venu regarder. ⚠️ **La fenêtre est mesurée, pas choisie** : sous 300 px on serait à l'ÉCRAN (la vue fait 480 × 270, donc tout ce qui est à plus de 276 px du joueur est forcément dehors) et on verrait six hommes se matérialiser ; au-delà de 500 px on serait hors de la BULLE D'OUBLI (520) et ils naîtraient pour être effacés à l'image suivante. ⚠️ Le tirage se fait à l'**empreinte de la minute**, jamais au dé du jeu (la leçon du char en panne, qui avait fait tomber quatre juges sans rapport), et un juge le tient en comptant les dés sur six cents images. ⚠️ Ils **ne sont pas la foule** : ils sont venus pour ça, comme l'ouvrier à son chantier — sans cette marque, six hommes de plus passent par-dessus le plafond de passants, faute que le juge de la foule a déjà attrapée une fois. ⚠️ Et **l'autre moitié de la règle compte autant** : on a appris à la rixe à ignorer le joueur, il ne faut pas qu'elle l'ignore quand il ENTRE dedans — un coup de sa part, et la gang lui tombe dessus comme chez elle. **Pas de réplique neuve** (le `cri` et les coups suffisent) : un juge exige que chaque parole soit le métier de quelqu'un. 14 juges neufs (`test_bagarre.py`, `test_bagarre_js.py`), rouge-avant prouvé **six fois** ; 1644 tests. ✅ **8e vague livrée** (16 sept. 2026) — *le bris d'aqueduc*, troisième visage de l'entrave et le seul que personne n'a posé : une conduite lâche sous la chaussée, la rue gicle, et la ville met presque une heure à trouver la vanne. ⚠️ **Il arrive à une HEURE, pas à l'aube** : l'entrave du jour et la rue barrée se tirent au lever du jour et tiennent la journée ; celui-ci est de la famille du char en panne — on roulait, la rue était libre, elle ne l'est plus. Ni cônes, ni panneau DÉTOUR. ⚠️ **Rien n'a été écrit pour l'eau** : la gerbe est le `jet_eau` de la borne-fontaine défoncée, tel quel — il crache ses gouttes et **tient** son souffle (`Son.SFX.borne_jet`, une fois par image, à distance). Un bris d'aqueduc est cette gerbe-là, en pleine rue et pour une heure de jeu. ⚠️ **Et le trafic n'a rien demandé non plus** : un bris est une barrière comme les autres, et `peutSortir` les consulte déjà depuis la 1re vague. Sans elle, mesuré, le char roule sept images **dans le trou**. ⚠️ **Le juge qu'il a fallu jeter, et ce qu'il a appris.** La tentation était d'appliquer le standard de la **rue barrée** : effacer la flèche et redemander à `voies_bloquees` si les rues sont encore fortement connexes. Mesuré : les **trente** candidates échouent — et ce n'est pas un défaut, c'est la leçon de la 3e vague relue à l'envers. Une voie est un couloir dirigé d'une tuile de large : boucher une tuile laisse toujours le reste du tronçon en cul-de-sac dans les deux sens, jusqu'au croisement suivant. C'est exactement **pourquoi** une rue barrée doit couvrir tout son tronçon. Un bris, lui, ne touche pas au champ de direction : ce qui le rend franchissable n'est pas le graphe des flèches, c'est **le changement de voie**. Le juge mesure donc la manœuvre — se déporter une tuile avant, passer, continuer — sur les trois tuiles qu'elle emprunte, et il exige que la voie d'à côté mène quelque part **des deux bouts** : une voisine qui commence ou finit pile au trou n'est pas un détour, c'est une impasse d'une tuile. ⚠️ **Et la première version de ce juge-là ne mesurait rien du tout** : elle lisait un `_Chantier` neuf, qui est une toile **vide** — `voies_bloquees` y rend deux ensembles vides quoi qu'on fasse. Les juges lisent maintenant la ville **bâtie**, celle du paquet, c'est-à-dire exactement ce que le navigateur reçoit. ⚠️ Il arrête les **chars** et pas les **jambes** — la règle du pont de La Pointe : on traverse la gerbe à pied, on se mouille, on passe ; un trou d'eau qui arrêterait tout le monde serait un mur, et la ville n'en a pas. ⚠️ **Un bris ne déborde jamais sur l'heure suivante**, et c'est la fiche qui le garantit (`minutes` < 60, sous son juge) : cette borne a permis de **supprimer** une branche du navigateur qui, écrite pour ce cas, ne pouvait jamais s'exécuter. ⚠️ Le tirage se fait à l'**empreinte de l'heure**, jamais au dé du jeu — rouge-avant prouvé en faisant tirer la tuile au dé (715 dés d'écart sur six cents images). ⚠️ Et un juge qui plantait le joueur au **milieu de la chaussée** à côté du bris le faisait faucher par le trafic : l'hôpital le renvoyait à deux mille pixels de là, la gerbe sortait de la bulle, et le juge mesurait un oubli par distance en croyant mesurer une minuterie. Il se tient sur le trottoir. ⚠️ Note honnête : le **renouvellement** de la gerbe n'a pas de rouge-avant — la branche d'à côté en refait une à l'image même où l'autre meurt, et un juge qui regarde chaque image ne voit aucun creux sans elle ; elle évite de jeter et refaire une entité toutes les dix secondes, rien de plus. 10 juges neufs (`test_aqueduc.py`, `test_aqueduc_js.py`), rouge-avant prouvé **cinq fois** ; 1652 tests. ⚠️ Jugé dans un **worktree isolé** : une autre session écrivait dans l'arbre. ✅ **9e vague livrée** (16 sept. 2026) — *les goélands et les chats*. « La vie qui n'est pas humaine : un goéland qui s'envole quand tu passes aux Quais, un chat qui file dans une ruelle du Faubourg. Ils ne comptent pour rien — ni témoins, ni victimes — et c'est précisément ce qui les rend vivants : ils ne sont là que pour être là. » ⚠️ **Et « ne compter pour rien » a fini par vouloir dire quelque chose de très précis : ne pas être dans `B.entites`.** Les sortir de l'index des gens ne suffisait pas — mesure, un juge du trottoir qui compte un TAUX sur cent essais tombait de 75 % à 2 % rien qu'en les laissant vivre dans la liste du monde, **sans qu'aucune ne tire un seul dé** (vérifié par attribution de pile d'appel, puis en neutralisant l'oubli, puis le semis). Elles ont leur liste : ni parcourues, ni démêlées, ni oubliées, ni indexées avec le reste. ⚠️ **`blesser` acceptait n'importe quoi de vivant** : `creer` donne `vivant: true` à TOUT ce qu'il fabrique, si bien qu'un goéland — ou un ballon, ou une gerbe d'eau — se laissait « blesser » de 99 points. Un goéland qu'on peut tuer est une **cible**, et une cible demande un score, un crime, un juge. ⚠️ Elles partent **avant** qu'on les touche : leur distance de fuite est plus grande que la portée de tout ce qui pourrait les atteindre, et c'est ce qui évite d'avoir à répondre à « que se passe-t-il si je lui roule dessus » — on n'y arrive pas. Un char qui fonce compte double. ⚠️ Chacune chez soi (le goéland au bord de l'eau, le chat dans les ruelles), et rien ne se tire au dé : le semis balaie la bulle en anneaux, l'humeur se tire à l'empreinte. ⚠️ **Et une heure perdue avant de comprendre** : trois des juges qui tombaient appartenaient à une autre session en vol (`carte.py`, `test_trottoir.py`). La leçon du dossier partagé, apprise deux fois en deux vagues : **avant d'accuser son propre code, vérifier à qui appartient le diff**. 4 juges neufs, rouge-avant prouvé trois fois ; 1716 tests. Restent ensuite : le tramway, le traversier, la neige et la charrue, la nuit de déneigement, l'arrêt d'autobus, les éboueurs. |
| M14 Meta v2 | **à faire** (v2) | — | **P4** | ajout | **un compte et une base de données** (demande de Martin, précisée le 15 sept. 2026) : **les parties vivent sur le serveur** (SQLite, trois emplacements, un **compteur** par partie — jamais une horloge — et le joueur tranche quand deux appareils divergent), **session longue durée** par jeton d'appareil **tournant** (cookie d'un an, haché en base, un jeton périmé qui revient coupe tous les appareils), et **ouverture par NIP** — ⚠️ le NIP rouvre une session sur un appareil déjà lié, il n'ouvre **pas** un compte : il déchiffre le jeton localement, cinq essais et le jeton s'efface, le compte ne se bloque pas. Mesuré : une partie pèse 790 o à 4,5 Ko. Plus le défi du jour à graine serveur (reporté de M7), le mode photo, la coop locale |
| Les zones conditionnelles | **livré** (le mécanisme et quatre barrières) | 15 sept. 2026 | **P4** | ajout | demande de Martin : « certaines zones pourraient être bloquées conditionnellement à des missions ou prérequis ». Le jeu a déjà **trois** barrières écrites chacune à sa façon (la guérite de la fourrière, les zones de gang, les barrages à 5★) et M12 en promet une quatrième : une seule fiche `carte.BARRIERES` — où, ce qu'elle arrête (piéton / véhicule / les deux), à quelle condition, ce que coûte de forcer, et la **raison** qui s'affiche. ⚠️ Le juge qui compte : aucune combinaison de barrières fermées n'enferme la planque ni ne rend un lieu de mission inatteignable ✅ **Livré** (15 sept. 2026) : `carte.BARRIERES`, une fiche par barrière — `ou` (résolu par le chantier en rectangle de tuiles : le tablier d'un pont, la grille d'un lot, le bâtiment d'un lieu garanti plus `marge` tuiles de cour, le quai qui porte un ambulant), `arrete` (piéton, véhicule, les deux), `condition` (`apres` une mission, `heure` jour/nuit, `jour_tire` pour les entraves de M12, `payer` pour la guérite), `forcer` (étoiles, dégâts, ou rien), `raison`. ⚠️ **Seule la couronne du rectangle arrête, et seulement quand on vient de l'extérieur** : qui est dedans quand elle se ferme en sort librement — c'est ce qui fait qu'une barrière bloque sans jamais enfermer, et c'est écrit une fois (`Monde.barriereBloque`), lu par le mouvement des piétons, des chars et du trafic. Un char lancé pousse les cônes (dégâts de la fiche, une seule fois par traversée) ; à pied, on pousse une seconde — le temps de lire la raison —, l'enjambée part, et l'étoile tombe à la retombée. **Le trafic fait demi-tour** devant une barrière fermée (la voie d'en face la plus proche) au lieu de s'empiler — un juge le tient. Ce qui ferme **se voit** : des cônes sur la couronne d'un pont, une chaîne sur des poteaux autour d'une cour ; et le carnet liste ce qui est fermé, avec sa raison. **Quatre barrières** : le pont de La Pointe (chars, fermé tant que m2 n'est pas faite — ⚠️ p02 n'existe pas encore, M16 le remplacera), la guérite de la fourrière (déclarée `existant` : `majFourriere` la joue déjà, un juge tient son étoile d'accord avec `economie.FOURRIERE`), la cour de l'usine Prévost (les deux, ouverte le jour, 1★), le quai du cargo (les deux, ouvert la nuit, 1★ — la run de Sven est une affaire de nuit). Les zones de gang et les barrages ne sont pas des barrières : une menace et un char en travers ne sont pas des murs à condition. Le juge qui compte tient : toutes fermées en même temps, la planque n'est dans aucune et chaque lieu de mission reste à portée de jambes ; ce qui ne rouvre jamais tout seul (`apres`) n'enferme aucun lieu ; une barrière d'heure ne couvre jamais un lieu de mission. 4 juges Python + 3 de banc ; 1574 tests. Restent, avec M16 : la cour à ferraille de Ti-Loup (s02), l'allée de la villa du maire (e07), et les gardiens |
| Toutes les façons de lancer ouvrent le réseau local | **livré** | 15 sept. 2026 | **P3** | **correctif** | demande de Martin (« je veux que toutes les run soit accessible depuis mon reseau interne ») : `APP_HOST` valait `127.0.0.1` par défaut, et **une seule** des cinq façons de lancer ouvrait le wifi de la maison — la configuration VS Code « réseau local ». F5 « Jouer », la tâche `serveur`, `uv run python run.py` et Flask sans rechargement restaient sourds au téléphone. Le défaut est maintenant `0.0.0.0` (`run.py`), la configuration « sans rechargement » écoute pareil, et celle qui disait « réseau local » devient **son contraire** : « local seulement », la seule fermée — et la seule où la console interactive de Werkzeug s'allume. ⚠️ **La bannière mentait**, et c'est le vrai piège : Werkzeug annonce une adresse trouvée en ouvrant une socket vers une adresse privée quelconque (`get_interface_ip`), donc celle de la **route par défaut** — VPN monté sur le Mac de Martin, il imprimait `http://10.14.0.2:5400`, un tunnel que le téléphone du salon ne joint **pas**, pendant que le wifi répondait en `192.168.4.188`. `config.adresses_du_reseau_local()` lit plutôt ce que le nom de la machine résout (les vraies interfaces, loopback et `169.254.x` écartés), et `run.py` imprime l'adresse **en dernier**, après la bannière, dans le processus qui sert vraiment (`WERKZEUG_RUN_MAIN`) pour ne pas la dire deux fois. ⚠️ Et `APP_HOST` **reste commenté** dans `.env.example` : le `.env` est chargé avec `override=True`, donc une ligne écrite là gagnerait sur le `env` des configurations VS Code et « local seulement » mentirait à son tour. La règle de sécurité sort du bloc `__main__` où personne ne pouvait la tester — `config.hote_est_local()` décide de `use_debugger`, et un juge rougit le jour où `0.0.0.0` entrerait dans la liste des hôtes « locaux » : un shell Python ouvert à toute la maison n'a rien à faire là. La production ne bouge pas (gunicorn sur `127.0.0.1:8006` derrière nginx). 7 juges neufs, 14 cas |
| La première bagarre ne se gagne pas | **livré** | 16 sept. 2026 | **P1** | **correctif** | retour de Martin : « la premiere mission des cravattes est trop difficile, ils font trop de dommage ». ⚠️ **Mesuré au banc, et il a raison** : M2 est la **première bagarre du jeu** — le joueur a 100 PV et ses **poings** (8 de dégâts), en face deux Cravates sorties de l'archétype avec **90 PV** et le **bâton** (18 de dégâts, et `renverse`). Mesure d'avant : un joueur qui les laisse cogner tombe en **2,8 s**. ⚠️ **Et le bâton est la RÉCOMPENSE de M2** : on le rencontrait avant de le posséder — le dialogue promet pourtant l'inverse (« Fais-leur comprendre. **Avec tes poings, pas plus.** »). ⚠️ **On ne touche PAS à l'archétype pour régler une bagarre** : la Cravate de rue tient le Faubourg en M5 et vient encaisser la dette de Rocco — l'affaiblir pour arranger M2 aurait rendu mou tout le reste du jeu. Ce qui change, c'est **qui on envoie** : un objectif `tuer` porte désormais deux clés facultatives, `arme` (`""` = les poings) et `vie`, qui passent par-dessus la fiche de l'archétype **et seulement pour ces hommes-là** (`missions.py`, appliquées dans `poserLesCravates`). Les deux du kiosque arrivent donc **les mains vides**, à 55 PV : ils sont venus racketter une dame, pas casser un homme. ⚠️ `''` veut dire les poings, donc le JS teste `!== undefined` — un repli « ou sinon la valeur de l'archétype » aurait rendu le bâton à qui vient les mains vides, c'est-à-dire exactement le bogue qu'on répare. **Après** : on encaisse **6,1 s** avant de tomber au lieu de 2,8, et la bagarre se conclut en 2,4 à 3,8 s selon qu'on cogne bien ou mal, avec **28 à 92 PV** restants. ⚠️ Et elle reste une **bagarre** : deux hommes qu'on laisse faire ont toujours raison de toi. 1 juge neuf, **rouge-avant prouvé deux fois** (la fiche `batte`/90, et les 2,8 s) dans un **worktree isolé** ; sa moitié « il gagne » est nommée **garde-fou** dans le juge lui-même, parce qu'elle était **verte avant** : un banc qui cogne sans jamais rater ni tourner le dos chancelle ses deux hommes en continu et gagnait déjà. |
| L'eau basse : le premier pas ne noie pas | **livré** | 16 sept. 2026 | **P2** | **correctif** | retour de Martin : « la premiere case de l eau ne prend pas d'énergie nie ne noie ». ⚠️ **Mesuré** : l'eau n'a aujourd'hui qu'une seule profondeur — dès le premier pixel mouillé le souffle part à **0,5 par image**, et immobile les pieds dans l'eau au bord de la grève **on coule en 3,3 s** (200 images pour 100 points), avec le réveil à l'hôpital et la facture. ⚠️ **Le plan le promettait déjà** : « L'eau n'est plus un mur » écrivait noir sur blanc « **il faut un bord** — on ne doit pas passer d'un pas de la terre ferme à la noyade », et c'est le seul point de cette fiche resté ouvert. Depuis, la grève s'est meublée et un **enfant barbote** dans la première tuile sans jamais rien risquer, à côté d'un joueur qui s'y noie. La règle tient en une phrase : **l'eau qui touche la terre est de l'eau basse — on y a pied**. Elle se **lit** dans la carte (quatre voisines en croix, la même mesure que le `trop_loin` de l'enfant qui barbote), elle ne se marque pas : un glyphe de haut-fond serait une deuxième vérité à tenir à jour, et la moindre retouche de la côte la ferait mentir. **975 tuiles sur 18 778** (5 %) : un liseré, pas une plage. ⚠️ **Et la géographie de M8 tient toujours** : les deux berges du chenal deviennent gratuites, la traversée passe de 88 à **72 points sur 100** — un pari, toujours au-dessus du seuil de 60 en deçà duquel le pont ne servirait plus à rien ; le juge de `test_eau.py` refait le calcul avec les deux berges en moins. ✅ **Livré** (16 sept. 2026) : `Monde.eauBasse(tx, ty)` — de l'eau dont une des quatre voisines n'en est pas — et `majJoueur` n'en tire que deux conséquences : le souffle ne part pas, `noyade` n'est pas appelée. **On y patauge quand même** à la vitesse de la nage, avec les remous et le corps coupé à la ligne d'eau : c'est de l'eau, ça se voit et ça ralentit — ce qui change, c'est ce qu'on y risque. ⚠️ **Et la barre remonte**, comme sur le sable (la régénération ordinaire, jamais le surplus) : l'eau basse est de la terre ferme pour le souffle, pas un purgatoire où il resterait figé — sinon revenir au bord à bout de souffle laissait le joueur planté dans dix centimètres d'eau, vivant et incapable de repartir. ⚠️ **Hors carte n'est pas de la terre** : la baie touche le bord du monde, et compter le vide comme une rive aurait fait un haut-fond du large. ⚠️ **Deux juges d'à côté ont dû recompter, et c'est le vrai travail de cette fiche** : le chenal du pont paie maintenant **9 tuiles sur 11** (72 points, toujours un pari), et `test_moteur_js` mesurait « une seconde de nage » **depuis l'entrée dans l'eau** — seize images de patauge dans le compte, 22 points là où la fiche en promet 30 ; il attend désormais d'être au large pour partir sa mesure. ⚠️ **Et un juge neuf a failli passer pour la mauvaise raison** : il lisait `B.transition` **à la fin** de sa boucle, quand le fondu est retombé et qu'on s'est réveillé à l'hôpital avec 100 points tout neufs — il aurait félicité le code d'avant pour une noyade complète. La noyade se guette **pendant** la boucle. ⚠️ **Ce qui ne change pas** : un char qui touche l'eau coule, l'eau basse comprise — c'est une règle de char, pas de souffle, et elle a ses propres juges. 5 juges neufs (`test_eau_basse_js.py`), **rouge-avant prouvé sur trois** dans un worktree isolé ; 1675 tests. |
| Le bord de l'eau et la foire | **en cours** (1re vague livrée) | 16 sept. 2026 | **P4** | ajout | demande de Martin : « des belvédères, table à pic nic, des plages parasol, enfants qui joue, château de sable, etc. des sea doo, ski nautique, bateau, quai. un parc d'attraction avec grande roue, jeu d'adresse, manèges, etc. » ⚠️ **Mesuré : la plage existe déjà** — 2 507 tuiles de sable (dont 782 au bord de l'eau), 1 818 tuiles de quai, 1 701 décors de treize sortes, et pas un parasol, pas une table, pas une coque amarrée. Quatre vagues : **la grève se meuble** (six `DECORS`, aucun moteur neuf) ; **les enfants jouent** (un `metier`, trois routines — et ⚠️ un enfant ne se noie pas) ; **l'eau porte enfin quelque chose** (⚠️ **bloqué** : la chaloupe est `phase=2` et « Le char tourne comme son ombre » est P1 en cours ; le ski nautique est un `crochet`, pas un véhicule) ; **la foire de La Pointe** dans un de ses deux blocs de bois — la grande roue est un **belvédère qui tourne** (elle montre les paquets cachés), les manèges sont du décor animé qu'on ne monte pas, les jeux d'adresse sont des `DEFIS`. ✅ **1re vague livrée** (16 sept. 2026) — *la grève se meuble*, à la demande de Martin (« je veux que tu fasses la plage »). Six fiches `DECORS` et un semis, **aucun moteur neuf** : table à pique-nique (un **H couché** vu d'en haut), parasol, serviette et sa glacière, château de sable, bouée, poteau d'amarrage, belvédère — **174 meubles** sur la graine livrée. ⚠️ **Une plage suit la côte ; elle ne suit pas une boîte** : le semis marche tuile par tuile et ne meuble que du sable qui a l'eau à trois tuiles. ⚠️ **Le château est le seul du lot qui ait une règle** — `pv: 5`, le décor le plus fragile du jeu, rasé par un char et **revenu au matin**. ⚠️ **Le parasol est le seul qu'on ne heurte pas** : on passe dessous. ⚠️ **La bouée est le premier décor du jeu à flotter**, et ça a demandé deux choses : `poser_decor` refuse le solide et l'eau **en est** (`solide: 2`) — on le lui accorde par demande explicite (`sur_eau`) plutôt qu'en ouvrant l'eau à tout le catalogue ; et le juge de M1 « tout décor est sur une tuile marchable » l'a arrêtée net. **Ce juge a raison sur le fond — ce n'est pas lui qu'on jette, c'est l'exception qu'on déclare** : `carte.FLOTTANTS` vit en Python, le paquet la porte, et un juge de banc vérifie que le `flotte` des fiches de dessin dit exactement la même chose. ⚠️ **Mesure qui a tout réorienté** : le glyphe `Q` n'est pas un ponton, c'est le **pavage du district des Quais** — **16 de ses 1 818 tuiles touchent l'eau**. Un poteau semé « sur le quai » se plantait six tuiles à l'intérieur des terres, ou nulle part (0 poteau, 0 bouée au premier essai). Ce qui amarre un bateau n'est pas un glyphe, c'est une **rive** : une tuile où l'on marche, ni sable ni route, avec l'eau devant — 222 tuiles, dont **199 de trottoir**. Et le trottoir ne porte pas `terre` dans la légende : tester la propriété au lieu de la marchabilité laissait dehors 199 des 222. ⚠️ **Un crochet de variante par tuile** : le décor est cuit **une fois par type**, donc sans lui tous les parasols de la ville sont du même rouge. Le mécanisme existait pour les `DECALS` (`d.v`) ; c'est la première fiche de décor à en avoir besoin — et la variante se tire à l'**empreinte de la tuile**, jamais au dé du jeu. ⚠️ **Deux dessins jetés après les avoir REGARDÉS** (rendus au navigateur, pas devinés) : le château était une **motte beige** — tours et courtine du même sable — et le belvédère une **caisse**. Ce qui nomme un belvédère vu d'en haut, c'est la rambarde sur **trois** côtés et la trouée du sud par où l'on monte : un plancher fermé est une boîte, un plancher ouvert d'un côté est un endroit où l'on va. ⚠️ **Et une précaution nommée comme telle** : le semis passe après `boucher_les_poches` (on ne meuble pas un terrain que la ville va retirer), mais **mesuré sur huit graines et 1 139 meubles, semer avant n'en noie aujourd'hui aucun** — le juge n'y répare rien, il épingle l'ordre. 13 juges neufs, rouge-avant prouvé deux fois, et le juge de l'écart en a attrapé un troisième en vol (un belvédère posé contre un parasol) ; 1659 tests. ✅ **2e vague livrée** (16 sept. 2026) — *les enfants jouent*. ⚠️ **Jouer, c'est un `metier`, pas un costume** : l'enfant existait depuis la v1 et n'avait jamais rien fait d'autre que marcher. Trois routines branchées sur ce qui existe — le **château** (il y revient, et s'il n'y est plus il s'en cherche un autre), la **baignade**, le **ballon** entre deux enfants. ⚠️ Ce ne sont **pas** tous les enfants de la ville : ceux-là naissent sur la grève et y restent. Donner un `metier` à l'archétype les aurait tous sortis de la foule et aurait rendu muette la mère qui promène le sien. ⚠️ **UN ENFANT NE SE NOIE PAS** — et mesure, pour ne pas s'attribuer un correctif : **aucun piéton ne se noie dans le jeu**, le souffle et `noyade` n'existent que pour le joueur. Le juge n'y répare rien, il **épingle** la garantie. ⚠️ Et ce qui la tient n'est **aucun des deux gardes écrits pour ça** : c'est qu'on ne donne jamais à un enfant de destination au-delà de la première tuile, et qu'il s'immobilise dès qu'il y a le pied — neutraliser l'un ou l'autre ne fait tomber aucun juge, et les deux sont commentés comme des **ceintures**. ⚠️ **Le juge qui passait à vide** : il annonçait « il ne dépasse jamais la première tuile » et il passait sur une plage où **personne n'entrait jamais dans l'eau** — `cap` s'arrête à 12 px de son but (un palier écrit pour le pickpocket) et une tuile en fait 16, donc l'enfant s'immobilisait *avant* de se mouiller les pieds. Une ligne de plus au juge (« il faut qu'ils y soient entrés »), et le défaut est tombé tout seul. ⚠️ **Et la leçon des dés, payée une troisième fois cette semaine** : la naissance des enfants tirait quarante couples dans `B.rng()` — **le pickpocket a cessé de voler**, et le budget de la foule a sauté. Un juge qui ne parle pas de plage, tombé parce que chaque dé consommé décale tous ceux qui suivent. Le semis balaie maintenant la bulle en spirale, le choix du jeu se tire à l'empreinte de l'enfant, et **plus un seul dé**. ⚠️ **Le ballon vole dans la boucle des entités, pas dans la routine** : les routines battent une image sur quinze — mesuré, le ballon ne bougeait que 13 images sur 400 et sautait par à-coups d'un quart de seconde. Et il lui faut de la **distance** : deux enfants collés ne se lancent rien, la balle arrive avant d'être partie. ⚠️ **Un enfant oublié emporte son ballon**, sinon la balle vole toute seule pour toujours. ⚠️ **Un juge existant resserré plutôt qu'affaibli** : « aucun passant ne se met à l'eau » a raison sur le fond — une flânerie qui mène à la baie ne se voit qu'en jeu —, donc ce n'est pas lui qu'on jette, c'est l'exception qu'on **nomme**. ⚠️ **Et un défaut de la 1re vague trouvé par le juge du PONT** : une serviette et deux bouées s'étaient posées à une tuile du tablier de La Pointe, et un char lancé les accrochait — le juge a vu la carrosserie tomber à 90 sur 100 *après* l'ouverture du pont et en a conclu que le pont coûtait encore. Un quai n'est pas une plage, et le pied d'un pont non plus (`FERMETURES` le disait déjà pour les rues barrées). 5 juges neufs, rouge-avant prouvé trois fois ; 1669 tests. ✅ **3e vague livrée** (16 sept. 2026) — *l'eau porte enfin quelque chose*, **la dette de M3**. ⚠️ « Phase 2 » voulait dire « sans sprite et sans trafic », et le plan annonçait une **physique à part** : mesuré, il n'en fallait aucune. La fiche de la chaloupe existait depuis M3 (eau, friction 0,995, adhérence 0,05, trois cercles) et `majNoyade` l'exemptait déjà du naufrage depuis que l'eau n'est plus un mur. Il manquait **un dessin et une règle de tuile**. ⚠️ **Un char et une coque ne sont pas arrêtés par les mêmes choses**, et c'est toute la différence entre les deux mondes : le char est arrêté par les murs et **passe** sur l'eau (il coule, c'est son affaire) ; la coque est arrêtée par **tout ce qui n'est pas de l'eau**. Une ligne dans `tuileInterdite`, pas une classe — un masque est une liste de ce qui bloque, et la règle du bateau est l'inverse : une liste de ce qui laisse passer, et elle n'a qu'une entrée. ⚠️ **18 amarrages** contre la rive **bâtie**, jamais le sable (on amarre à un quai, on n'amarre pas à une plage — on y échoue) et jamais au pied d'un pont, la règle que le juge du pont avait déjà trouvée pour le mobilier de grève. Elle ne naît **pas dans le trafic** (`frequence: 0`) : une chaloupe sur la rue Principale est exactement ce que la règle de tuile interdit. ⚠️ **La leçon des dés, une cinquième fois** : les coques tiraient un dé pour leur couleur, et **onze juges sans rapport sont tombés d'un coup**. Empreinte de l'amarrage, comme la panne, le pilote des deux-roues et les enfants de la grève. ⚠️ Et une heure perdue à chasser huit défauts **qui n'étaient pas les miens** : `app/carte.py` portait la vague « terrains vagues et parcs » d'une autre session, et c'est elle qui déplaçait le mobilier de plage. La leçon du dossier partagé : **avant d'accuser son propre code, vérifier à qui appartient le diff**. 5 juges neufs (`test_bateau.py`), 4 juges existants resserrés plutôt qu'affaiblis (le parc n'a plus de phase 2 ; une coque ne se juge pas au gaz sur l'asphalte ; son élévation est mesurée comme celle des autres) ; 1687 tests. 🔨 **4e vague en cours** (16 sept. 2026) — *la foire de La Pointe*. ✅ **Le terrain est posé** : ⚠️ **on n'agrandit pas la grille, on la DÉPENSE** — la leçon de l'île vaut ici aussi. Une des trois taches de bois de La Pointe devient la foire (un glyphe `n` du plan devient `f`), et la grève est juste au-dessus. ⚠️ **Une foire est une ALLÉE bordée de choses, pas une place** : c'est ce qui la distingue du parc d'à côté, qui est un centre avec des allées en baïonnette. On marche entre deux rangs de manèges, et **la grande roue est au bout** — on la voit de l'entrée, et c'est elle qui dit où l'on va. ⚠️ **Du décor animé, et on n'y monte pas** : le carrousel, les tasses et les chaises volantes tournent par `anime` + `variantes` — chaque pose est cuite **une fois** et reste en cache, donc un manège qui tourne coûte quatre canevas, pas un par image. C'est l'étage 1 des machines de chantier, mot pour mot. ⚠️ **L'empreinte de la roue est celle de son PORTIQUE, pas de sa jante** : la roue est en l'air, on passe dessous — et le juge de `PORTEE_DECOR` l'a dit avant moi (son coin tombait à 29 px pour une portée de recherche de 24, donc on serait entré dedans sans que rien ne le voie). ⚠️ Et deux réflexes qui ont payé : `poser_decor` refuse une tuile **réservée**, donc réserver le pied de la roue avant de la poser revenait à lui interdire sa propre place — elle ne se posait jamais, en silence ; et la foire **déclare son rectangle** au lieu de le laisser deviner, parce que mon premier juge supposait « une trentaine de tuiles » et accusait d'un débordement qui n'existait pas (le bloc en fait 69). La foire a son propre dé. 7 juges neufs ; 1780 tests. ✅ **Refaite** (16 sept. 2026) — retour de Martin, capture à l'appui, en six phrases : « c'est assez décevant », « une foire, c'est beaucoup de choses et beaucoup de monde », « plein de kiosques, de vendeurs, de mascottes », « de l'exagération », « clôturée — pas un carré, des clôtures asymétriques — et une entrée avec une arche, et ça doit coûter quelque chose d'entrer », « plus compacte ». ⚠️ **La première version écrivait « une allée bordée de choses » dans son commentaire et faisait l'inverse dans son code** : sept objets tirés uniformément sur 80 × 33 tuiles de gazon, une roue de 44 px perdue au milieu, tout éteint à 21 h 50. Ce qu'il y a maintenant : **une enceinte compacte** (50 × 21) calée à l'ouest du bloc ; **23 comptoirs** qui bordent l'allée des deux côtés, un tous les trois pas — vingt kiosques de neuf sortes (dont la **poutine** et les **queues de castor** : c'est une foire au Québec) et les trois jeux d'adresse glissés dans le rang ; **un vendeur peint derrière chaque kiosque**, pas une entité (vingt vendeurs à vingt entités mangeraient le budget d'images de la rue pour des gens immobiles), son visage tiré à l'empreinte de la tuile ; **les manèges en double** juste derrière les comptoirs et une **grande roue de 84 × 92** au bout de l'allée ; **des guirlandes en damier** ; **45 forains et 4 mascottes** (un ours, une bleue, une rose — un corps, trois pelages) qui naissent DANS l'enceinte, vont d'un kiosque à l'autre, et saluent les bras levés. ⚠️ **L'arche se paie** : 15 $, un billet par JOUR (pas par passage — une foire qui refacture l'aller-retour au hot-dog d'en face est un péage), on ressort librement, et c'est une barrière comme les autres (`payer`, dans `carte.BARRIERES`). ⚠️ **Resquiller coûte une étoile** : la clôture s'enjambe comme toutes celles du jeu (un mur qui ment serait pire), mais la retombée dans la foire sans billet coûte ce que coûte de forcer l'arche. ⚠️ **Six défauts trouvés en chemin, et presque tous par des juges qui ne parlaient pas de foire.** (1) **Un trou dans la clôture** : elle se posait en dernier et sautait toute tuile déjà occupée — une table sur le bord laissait une tuile de gazon, et on entrait sans payer ; trouvé par un juge qui cherchait où sauter. L'anneau est réservé avant tout le reste, et **un juge remplit l'intérieur pour vérifier qu'on n'en sort que par l'arche**. (2) **La clôture s'effaçait toute seule** : en 4-voisinage les marches ne se touchaient plus que par un coin, et `elaguer_les_clotures` coupait chaque morceau droit comme « une barre qui ne clôt rien » — 78 tuiles sur 159. (3) En 8-voisinage, elle faisait des **carrés de 2 × 2** (un juge du dépôt tient qu'une clôture fait une tuile d'épais) : 4-voisinage, un raccord en L à chaque marche, et un amincissement qui ne retire une tuile que si la clôture reste étanche. (4) **Le plafond de lumières** : une lampe par kiosque dépassait les 50 du rendu, et les feux du carrefour d'à côté se seraient éteints — une guirlande sur deux, au halo plus large, en **damier** (la parité de pose allumait tout le rang sud et aucun kiosque du nord). (5) **La foule effacée à l'image suivante** : elle naissait au bout de la foire, hors de la bulle d'oubli — six forains sur trente. (6) **La clôture dans l'élan du pont** : centrée, l'enceinte tombait pile dans l'axe de sortie du pont de La Pointe, et un char lancé s'y écrasait après douze tuiles de gazon — le juge du pont a vu sa carrosserie tomber à 60. ⚠️ **Trois juges existants resserrés plutôt qu'affaiblis** : la clôture est en **grillage** et non en palissade (la palissade de bois est l'image de la banlieue des Érables, et une foire se clôt de panneaux temporaires) ; une guirlande n'est pas un lampadaire planté ; une table de la cour à manger n'est pas du mobilier de plage. 15 juges (`test_foire.py`), dont un qui prouve que le détecteur de trou **voit** un trou (le trou d'origine a disparu avec le déplacement des tables : remettre le défaut ne suffisait plus à rougir) ; 1837 tests. **Restent les trois défis** (galerie de tir, marteau de force, pêche aux canards) et les quatre pistes audio. |
| Plus de champs : des terrains vagues et des parcs | **livré** | 16 sept. 2026 | **P2** | ajout | demande de Martin : « au lieu des champs, mets des terrains vague un peu salle et avec des déchets, mais aussi des parcs ». ⚠️ **Mesuré, et le mot est juste** : **24 lots** de la ville — **1 328 tuiles** — se peignent avec le **gazon des parcs** (`,`), et il n'y a qu'**un objet par 17 tuiles** dessus. Dix sont des terrains nus (`_jardin`, 406 tuiles, un arbre ou un buisson par 16 tuiles, et en banlieue une palissade autour) ; quatorze sont des **terrains vagues** (922 tuiles) dont le seul décor est le gravat, semé un par 17 tuiles — sur de la pelouse. Vu d'en haut, un lot abandonné derrière son grillage a donc exactement la surface d'un parterre de banlieue : un champ. Trois choses : (1) une **friche** (`;`) dans la légende — la terre perce, l'herbe est sèche, et ⚠️ **pas de `herbe`** dans sa fiche, sinon la mini-carte la repeint en vert et c'est un parc de plus ; (2) **trois déchets** au catalogue (sacs d'ordures, pneu, baril rouillé) semés avec les gravats et les mauvaises herbes ; (3) un **parc de quartier** — un sentier de poussière de pierre, des bancs, des arbres serrés, parfois une table à pique-nique — qui remplace le gazon nu moitié-moitié avec le terrain vague. Plus un seul lot de pelouse rase. ✅ **Livré** (16 sept. 2026). **La friche** (`;`) : un terrain vague ne se peint plus au gazon des parcs — 1 238 tuiles de terre sèche, l'herbe haute, la plaque de terre nue, le gravat brûlé. ⚠️ **Pas de `herbe`** dans sa fiche : la mini-carte peint le vert avec cette propriété-là, et une friche verte sur la carte est un parc de plus. **Trois déchets** au catalogue (`ordures` — deux sacs dont un crevé ; `pneu` — un ANNEAU, un disque se lit comme une flaque, et le seul du lot qui ne soit pas solide ; `baril` rouillé), semés avec les gravats, les caisses et les mauvaises herbes : **256 objets sur 1 677 tuiles**, un par 6,6 au lieu d'un par 17. **Le parc de quartier** remplace le gazon nu, une sorte pour une sorte : ⚠️ ce qui fait un parc, c'est le SENTIER — un carré de gazon planté d'arbres reste un terrain, le jour où quelque chose le traverse c'est un endroit où l'on va. Le sentier se réserve en se traçant (la leçon de `_allee`), les bancs le bordent, et le parc **ne se clôture pas**. 9 parcs, 1 objet par 5,6 tuiles. ⚠️ **LA LEÇON DE LA SÉANCE, ET ELLE A COÛTÉ DIX JUGES** : le semis neuf tirait plus de dés que l'ancien dans le **dé commun**, donc toute la ville se rebattait — une barrière d'usine dont la couronne passait sur une case de stationnement, un buisson que la balle du banc ne rencontrait plus, deux enfants qui ne jouaient plus au ballon, et pas un juge ne parlait de terrain vague. Le décor des lots a maintenant **son propre dé** (`des_dechet`), on **brûle** exactement ce que l'ancien semis tirait (`Des.brule`, `_tirages_de_semis` — ⚠️ `entier(a, b)` ne tire pas quand `b <= a`), et `_contenu` échange `jardin` contre `parc` **sans toucher au tirage**. Mesuré : **1 066 tuiles changent dans toute la ville, dont 128 hors des lots redessinés** — et ces 128 sont voulues (voir ci-dessous). Les terrains vagues restent donc exactement où ils étaient ; ils changent de surface, pas de place. ⚠️ **Et un défaut de M8 découvert en passant** : la palissade de bois, « l'image de banlieue » que le plan promet depuis M8, tenait aux **LOTS VIDES** et pas aux cours — l'exact inverse de ce qu'on voit par la fenêtre, et le commentaire de `_jardin` le disait déjà. Mesuré : sur 36 terrains de banlieue, **SIX** avaient trois tuiles derrière la maison, deux ont appelé `clore`, et il restait **onze tuiles** de palissade dans toute la ville une fois les lots devenus des parcs. Deux tuiles de fond suffisent maintenant, la chance monte à 0,8 : **64 tuiles**, sur de vraies cours arrière. ⚠️ **Un correctif attrapé en chemin, et il ne parle pas de terrains vagues** : le juge « toujours entre 3 et 5 personnes autour d'un amuseur » tenait **par chance**. `majSpectacle` ne retenait les partants qu'à `vus.length <= mini` — or il ne tourne qu'une image sur quinze, et deux minuteries peuvent tomber dans le même intervalle : à quatre spectateurs, deux partants, le tour suivant trouvait le cercle à DEUX. Mesuré sur six graines de partie, il tombait déjà sur **deux d'entre elles avant** tout changement de carte. On compte maintenant les PARTANTS et on retient les plus pressés jusqu'à ce que le minimum tienne (`sursis_images`) : cinq graines sur six. ⚠️ **Pas de table à pique-nique dans un parc de quartier** : `test_greve` tient que toute table de la ville est au bord de l'eau, et il a raison — c'est un meuble de PLAGE. 8 juges neufs ; 1741 tests. ⚠️ **Reste ouvert, mesuré et nommé** : sur une graine de partie (82), un artiste né à huit tuiles d'un autre reste **seul 900 images** — `placeDansLeCercle` renonce et `garnirLeCercle` abandonne avant même d'essayer de recruter. Le défaut existe à l'identique avant ce changement (graine 81). |
| La roue d'armes | **livré** | 16 sept. 2026 | **P2** | ajout | demande de Martin : « je veux un meilleur sélecteur d'arme ». ⚠️ **Mesuré** : le catalogue compte **13 armes** et `cycler` n'avançait que d'**un cran, dans un seul sens** — revenir de la carabine aux poings coûtait **12 pressions**, en pleine fusillade, et le HUD ne montrant que l'arme en main, on cyclait **à l'aveugle**. Deux gestes sur le même bouton : une **tape** bascule entre les **deux dernières** armes (les poings pour les poches, la carabine pour le toit — le geste qu'on fait le plus souvent, et il ne coûte rien) ; **tenir** ouvre la **roue**, les armes possédées en cercle, on choisit à la direction (stick, flèches, pouce), on relâche pour dégainer. Rien de neuf n'a été dessiné : les icônes sont les `OBJETS` 16×10 des armes lâchées par terre, avec les munitions sous chacune et **grisée + rouge à sec** — c'est tout ce que le vieux cycle ne disait pas (on dégainait un pistolet à zéro et on perdait le tour). ⚠️ **La roue RALENTIT le monde, elle ne le FIGE pas** : une image sur quatre. Les menus du jeu figent (« le temps ne passe pas au comptoir ») et c'est juste pour un comptoir ; une roue qui fige est une **pause gratuite** au milieu d'une fusillade. Le prix, c'est le quart de vitesse **et** un joueur cloué sur place — une seule direction, un seul rôle, sinon choisir son arme au stick ferait marcher le personnage vers son choix. ⚠️ **Et on ne se bat pas dedans** : ni frappe, ni ACTION, ni prise d'otage qui mûrit. Sans ces portes, tenir ARME donne un **ralenti à la demande** — viser tranquillement, puis tirer ; la prise d'otage lisait ACTION **avant** la porte de la frappe, et elle a été fermée avec les autres. ⚠️ **Deux défauts trouvés en chemin, et le premier n'a rien à voir avec les armes.** `Jeu.boucle` avance par **accumulateur** — zéro à quatre `maj` par image dessinée — donc une **tape d'une image tombe parfois ENTIÈREMENT entre deux `maj`**, et le niveau du bouton (`bas`) ne la voit jamais : mesuré, elle se perdait une fois sur deux et le bouton avait l'air brisé. Elle se latche sur `neuf`, qui survit jusqu'au `videPresse` fermant le tour : le seul signal qu'un pas variable ne peut pas manger. Le second est le `cycler` à sens inverse, écrit puis **supprimé** — la roue rend le cycle à rebours inutile, et le dépôt ne garde pas une branche que rien n'atteint. ⚠️ **Le juge qui compte le plus refait le chemin complet** : du créneau au pixel (`Hud.posteDeLaRoue`), du pixel à la direction, de la direction au créneau (`Combat.creneauVise`). Une roue dessinée dans un sens et lue dans l'autre se joue à l'envers — le pouce pointe la carabine, le jeu dégaine la pelle — **sans qu'aucun test de logique ne rougisse**. 11 juges neufs (`test_roue_js.py`), **rouge-avant prouvé sept fois** ; 1715 tests. ⚠️ Jugé dans un **worktree isolé**, et la première tentative était **fausse** : y copier mes fichiers entiers a emporté le chantier d'une autre session — 168 juges rouges qui n'étaient pas à moi, mon `jeu.js` appelant un `Histoire` qui n'existe que chez elle. Les hunks se posent maintenant par **texte exact**, et le juge tourne sur `HEAD` + la seule roue. |
| La ligne d'histoire : une ouverture et un générique | **en cours** (l'ouverture livrée) | 16 sept. 2026 | **P2** | ajout | demande de Martin : « il faut qu'il y ait une ligne d'histoire qui commence par une introduction audio et visuel au lancement du jeu... aussi une animation audio visuel à la fin ». ⚠️ **1re vague livrée le 16 sept. 2026 — l'ouverture.** Le car de six heures entre au terminus, s'arrête, le bonhomme descend, le car repart et le titre s'inscrit ; le **narrateur du Clairon** dit la prémisse en quatre phrases (`missions.OUVERTURE`, voix ElevenLabs, `musique-ouverture.mp3` **et** trente secondes écrites en notes dans `musique.py`). Elle part sur **JOUER** (`Jeu.jouer()`, distinct de `commencer()`), se passe d'un bouton, ne se rejoue pas, et se revoit du carnet. **13 juges** (`test_ouverture.py`) + un juge navigateur qui prouve que la voix se décode. ⚠️ Le morceau s'appelle `ouverture`, pas `ouverture` : `mus_*` est réservé aux deux musiques d'ÉTAT. Reste le **générique**. ⚠️ **Mesuré le 16 sept. 2026 : le jeu ne dit JAMAIS sa prémisse, et il ne finit nulle part.** Le titre est un voile HTML (`voile-titre`) posé sur la ville figée au terminus — et **vide**, les entités ne naissant qu'à `Jeu.commencer()`, qui pose le bonhomme devant la porte et écrit `BAIE-DES-BRUMES` pendant 150 images. C'est tout. L'oncle Rocco, le garage, les 15 000 $ de Sal : c'est écrit **dans ce plan**, dans `economie.DETTE` et dans une réplique de Ti-Guy qu'il faut aller chercher à la porte du terminus. À l'autre bout, `B.etat` ne prend que `titre`, `jeu`, `pause` et `carte` : l'état `fin` qu'annonce la carte du dépôt (« Côté JS », `jeu.js`) **n'a jamais été écrit**, et le score ne part que d'un item du menu PAUSE. ⚠️ **Deux vagues, deux échéances** : l'**ouverture** se livre tout de suite (rien de neuf à dessiner — l'autobus, le terminus, la caméra, le fondu `Jeu.transiter()` et le cinéma `B.cinema`, qui fige la ville et dit une réplique à voix haute, existent tous), le **générique** attend une fin à laquelle arriver (**M13**, dernière tranche de M16). ⚠️ **Le son n'a pas le droit de jouer avant un geste** : le navigateur retient l'`AudioContext` tant que personne n'a touché — une ouverture partie au chargement serait muette une fois sur deux. Elle part donc sur JOUER, pas sur `demarrer()`. ⚠️ **Et on la passe** : ACTION saute une réplique, PAUSE saute l'ouverture entière, une partie en cours ne la rejoue pas, et elle se revoit depuis le carnet. Le **même narrateur** aux deux bouts (celui du Clairon) : c'est lui qui en fait une ligne et non deux animations |
| Le port touche enfin l'eau | **livré** | 16 sept. 2026 | **P2** | **correctif** | retour de Martin, capture à l'appui : « c'est le quai !! je ne savais même pas que c'était un quai… **il y a une route entre le quai et l'eau** !! j'aimerais que tu refactore toute cette région pour que ça soit logique ». ⚠️ **Mesuré, et c'est pire que ça — trois défauts empilés.** (1) **Le quai ne touche pas l'eau** : 1 818 tuiles de planches, **16 au bord de l'eau — 0,9 %**. Le chiffre était déjà écrit dans ce plan (« le glyphe `Q` n'est pas un ponton, c'est le pavage du district des Quais ») et personne n'en avait tiré la conséquence : ce n'est pas le semis des poteaux d'amarrage qui est faux, c'est la GÉOGRAPHIE. (2) **Ce qu'il y a entre les deux** : la coupe du port, du nord au sud, donne `#+.` boulevard, `QQQQQQQQQQ` dix tuiles de quai, `.#+.` un **boulevard à quatre voies**, `s` une **plage de sable** (294 tuiles), puis la baie. Un débardeur qui décharge un cargo traverse une autoroute et une plage. La cause est dans la trame : la rangée de quai et la rangée d'eau sont **deux blocs séparés**, et la trame met une rue entre deux blocs. (3) **Le bassin du Faubourg n'est relié à rien** : 250 tuiles d'eau (120,89 → 146,103) que le boulevard de la rangée 6 coupe de la baie — un étang au milieu du port, sur les neuf plans d'eau de la ville. ⚠️ Et il vient de devenir dangereux : la 3<sup>e</sup> vague du bord de l'eau y amarre des chaloupes, et **une coque qui y naît ne peut pas en sortir**. Ce qui arrive, dans cette passe : **Les Quais**, le port que Martin a montré. La rangée d'eau est **avalée** par la rangée de quai (`^`, le mécanisme des superblocs — c'est lui qui efface une rue, et il est déjà la règle partout ailleurs), un glyphe de plan `j` dit « quai SUR l'eau » (le `q` du Faubourg, lui, n'a pas de baie dessous et reste du plancher plein), et `_quai` dessine le tablier au nord, la baie au sud, la lèvre entre les deux. Puis un port qui a l'air d'un port : des **appontements** qui avancent dans la baie, des **bornes d'amarrage** le long de la lèvre, des caisses et des barils en arrière, des pneus en défense au bord. ⚠️ **Le bassin du Faubourg n'est PAS dans cette passe** — il demande une darse et un pont sur le boulevard, c'est-à-dire un jalon à lui. Il est mesuré et nommé ici pour ne pas être reperdu. ✅ **Livré** (16 sept. 2026). **La rangée d'eau est avalée par la rangée de quai** (`^`) : la trame n'a plus de raison d'y mettre une rue, c'est le mécanisme des superblocs qui fait déjà les gros îlots partout ailleurs. Un glyphe de plan `j` dit « quai SUR l'eau » — le `q` du Faubourg n'a pas de baie dessous et reste du plancher plein. ⚠️ **`j` entre dans `EAUX`**, et ce n'est pas un abus de langage : les deux tiers de sa hauteur sont la baie, et son tablier n'est pas une rue — un quai ne se traverse pas en char, on y descend du boulevard de service qui le borde au nord. Conséquence heureuse : **les rues verticales qui coupaient le quai deviennent des DARSES**, de l'eau entre deux appontements, ce qu'on veut justement y voir. **Après** : `#+.` boulevard de service, `QQQQQQQQQQ` le tablier, puis l'eau — **270 tuiles de quai au bord de l'eau (14 %) contre 16 (0,9 %)**, plus une tuile de sable contre les planches, et **223 objets** sur le port (58 bornes d'amarrage, 33 barils, 98 caisses, 16 pneus en défense) contre 120 caisses et rien d'autre. ⚠️ **La lèvre et l'arrière ne portent pas la même chose** : au bord ce qui sert au bateau, en arrière ce qui attend d'être chargé — semé au hasard sur toute la surface, on obtient des bornes d'amarrage à six tuiles de l'eau. ⚠️ **Un ÉCART, pas « une tuile sur six »** : la lèvre n'est pas une ligne droite (elle contourne les appontements), et compter le long d'une liste collait deux bornes dès qu'elle tournait le coin. ⚠️ **Le quai se meuble AVANT la grève**, et `greve()` ne comptait que ses propres poses : deux bornes se sont retrouvées collées sans qu'aucun des deux semis en soit responsable (`MEUBLES_DU_BORD` amorce maintenant la règle d'écart). ⚠️ **Quatre juges d'à côté sont tombés, et chacun cachait une vraie fragilité** — aucun ne parle de port. (1) *La pièce a les mesures de son bâtiment* exigeait la boîte entière, alors que `mesures_de_la_part` rogne la profondeur d'un bâtiment en L : le juge était en contradiction avec le générateur et ne passait que tant qu'aucune vitrine ne possédait une part trouée. (2) *Une case de stationnement se gare* comptait **une chaloupe amarrée** comme une auto garée hors case — une coque naît `stationne`, dans la baie, ce qui est sa place. (3) *Une balle mord la tôle* n'en tirait **qu'une**, et une arme DISPERSE : le juge pariait sur l'état du dé. (4) *Celui qui tient son poste cède* courait 240 images vers l'est et **contournait** le donneur au lieu de le pousser — 228 px plus loin, personne de bousculé. ⚠️ **Et un vrai défaut du générateur** : `fermetures` gardait un tronçon dont la boucle avait épuisé `long_max` au lieu d'atteindre le croisement suivant — une rue barrée qui finit au milieu de nulle part n'a pas de transversale à son bout, donc **pas de détour à montrer**. Son propre commentaire disait déjà la règle. 9 juges neufs (`test_port.py`) ; 1790 tests. ⚠️ **Reste ouvert, mesuré et nommé** : le **bassin du Faubourg**, 342 tuiles d'eau (118,89 → 147,103) qu'un boulevard coupe de la baie, et le quai du Faubourg qui ne le touche pas non plus. Il demande une **darse et un pont** sur le boulevard de la rangée 6 — c'est-à-dire un jalon à lui, pas une ligne de celui-ci. |
| Le quai se marche, et la ville est moins sale | **livré** | 16 sept. 2026 | **P1** | **correctif** | retour de Martin : « il y a **trop de saleté partout** et **impossible d'aller sur une partie du quai, il est clôturé, sans chemin à pied** ». ⚠️ **Mesuré, et les deux sont vrais — le second est P1 : une partie de la ville ne se visite pas.** **191 tuiles de quai sont inatteignables à pied**, en une quarantaine de poches. Et ce n'est PAS une clôture : c'est du décor solide. (1) **Deux semis posent des bornes d'amarrage sur la même lèvre** — `_meubler_le_quai` (écart 6) et `greve()` (`quai_poteau`, écart 3) — et la rangée du bord donne `QpQQAQQAQQQpQQQQQAQQpQQpQQAQQA` : une borne ou un pneu **tous les 3 pas sur soixante tuiles**. Vu d'en haut, c'est une palissade, et Martin l'a nommée comme telle. (2) **La cargaison couvre tout le tablier** : `PART_CARGAISON` sème une caisse par dix tuiles d'arrière, soit ~60 caisses SOLIDES sur dix rangées de profondeur — un plancher d'entrepôt, pas un quai. (3) **Les terrains vagues sont trop chargés** : un déchet par six tuiles, plus une mauvaise herbe par quatorze — 303 objets de saleté dans la ville (126 caisses, 65 sacs, 44 barils, 34 pneus, 34 gravats). Ce qui arrive : **un quai a un APRON** — la bande du bord reste dégagée (des bornes espacées, rien d'autre), la cargaison s'empile **au fond**, contre la rue par où les camions arrivent, et le milieu se marche ; la grève **cesse d'amarrer sur les planches** (le quai le fait chez lui) ; les densités baissent. Et une garantie plutôt qu'un réglage : **`carte.DECOR_SOLIDE`** dit en Python ce qui arrête un piéton, un juge de banc vérifie qu'elle dit la même chose que les fiches de dessin, et un juge tient qu'**aucun lot ni aucun quai ne se referme sur lui-même**. ✅ **Livré** (16 sept. 2026). ⚠️ **La « clôture » n'était pas un décor semé : c'était une BARRIÈRE.** « Le quai du cargo » est une zone conditionnelle (fermée le jour, décor `chaine`) qui prenait la **région** de quai du contrebandier — et depuis que le port a avalé la baie, cette région faisait **61 × 26 tuiles, eau comprise**. C'est la chaîne de la capture : le long du trottoir et en travers de tout le quai ouest. Elle ferme maintenant le **mouillage** (15 × 6, `MOUILLAGE`), sur le tablier seulement, et jamais l'apron — on longe le quai par le bord de l'eau, cargo ou pas. ⚠️ **Et on a failli ne pas la trouver** : « aucune clôture ne touche le quai » était vrai (la barrière n'est pas un glyphe), « aucun décor régulier sur la rangée nord » aussi ; il a fallu REGARDER la capture — des poteaux gris à chaque tuile, reliés par une lisse — et chercher ce qui se dessine au pourtour d'une région plutôt que dans une tuile. **Le générateur sait maintenant ce qui arrête un piéton** : `DECOR_SOLIDE`, déclaré en Python, porté par le paquet, et un juge de banc vérifie qu'il dit exactement ce que disent les fiches de dessin (la parade de `FLOTTANTS`). **`degager_le_decor`** est le pendant de `boucher_les_poches` pour le mobilier : après chaque quai et chaque terrain vague, il enlève ce qui enferme une tuile — on ENLÈVE, on ne déplace pas, sinon le décor déplacé ferme autre chose. Mesuré : **191 tuiles de quai enfermées → 0**, et zéro sur les friches et les trottoirs. **Un seul semis amarre le quai** : la grève tire encore son dé (pour ne pas décaler le sien) mais ne pose plus sur les planches ; les bornes passent d'un écart de 6 à **11** — la rangée du bord donnait une borne ou un pneu tous les trois pas. **Un quai a un APRON** (deux tuiles depuis la lèvre, où rien ne s'empile) et un **FOND** (trois rangées côté rue, où la cargaison attend le camion) ; le milieu se marche. **Moins de saleté** : un déchet par dix tuiles de friche au lieu de six, une mauvaise herbe par dix-huit — **303 objets de saleté → 166**. ⚠️ **Mes propres juges de la veille ont dû changer de sens**, et c'est la vraie leçon : ils disaient « au moins un objet par douze tuiles de quai », « une tuile de friche sur huit au plus », « vingt bornes » — c'est-à-dire qu'ils garantissaient exactement ce que Martin a renvoyé. Ce sont maintenant des **fourchettes**. ⚠️ **Et un juge voisin ne tenait que par un singe coincé** : « la bagarre tient le budget » faisait marcher 2 500 images au hasard ; à HEAD le singe finissait dans un coin vide (10, 1) avec un seul piéton à métier, après le changement il arrivait au centre-ville (146, 6) — et son plafond **recopiait** le nombre de vendeurs fixes (douze, ils sont treize), ce que sa propre note interdit. Il les lit maintenant dans la carte. 7 juges neufs (`test_quai_se_marche.py`) ; 1804 tests. |
| Un hôpital qui soigne du monde | **livré** | 16 sept. 2026 | **P4** | ajout | demande de Martin : « l'hôpital devrait être plus grand et avec des malades, une salle d'attente, des solutés, machines de santé ». ⚠️ **Mesuré avant** : 11 × 8 tuiles (54 de plancher), deux lits de bois, trois chaises, un comptoir — et **pas un malade**. **Livré** : **deux étages de 14 × 10** reliés par un escalier (192 tuiles de plancher, 3,5 fois plus). En bas, **l'urgence** : le triage et sa soignante en blouse, un lit d'examen occupé, une **salle d'attente** de seize chaises où **six patients attendent assis**, et deux distributrices (café, grignotines). En haut, **l'étage des soins** : **six malades couchés** dans six lits d'hôpital, chacun entre son **soluté** et son **moniteur** (le pic du tracé tombe ailleurs d'un écran à l'autre), et le poste des infirmières. Quatre glyphes de meuble — `r` lit d'hôpital (un bloc d'une place), `i` soluté, `q` moniteur, `b` distributrice — : ⚠️ ce sont **les quatre dernières minuscules libres** de la légende. Deux archétypes (`soignante`, `malade` en jaquette, fréquence 0) et deux sortes de gens dedans, jugées au chargement du plan : le `patient` naît **sur une chaise**, le `malade` **dans la tuile de tête** d'un lit (`ASSIS_OU_COUCHE`) — ailleurs, `_piece` lève. Ils tiennent leur place comme un donneur (`fige`) ; qu'on frappe un malade, il redevient un passant et se sauve en jaquette. ⚠️ **Plus grand en profondeur et par un étage, pas en largeur** : l'îlot de l'hôpital fait douze tuiles de large, et une pièce a exactement les mesures de son bâtiment (`test_la_piece_a_les_mesures_de_son_batiment`, cinq graines) — le bâtiment est passé de 9 × 6 à 12 × 8 sans qu'un autre juge de la ville bouge. ⚠️ **Mais le tirage de la ville, lui, glisse** : un bâtiment plus grand consomme le dé autrement, et tout ce qui se pose après change de place. Deux juges prenaient « la première borne » et « la première voie de la colonne 14 » — la borne est tombée au coin nord-est de la carte (on ne pouvait plus s'en éloigner de 900 px) et, au nouvel endroit du pickpocket, le **joueur se tenait entre le voleur et sa victime** et les poussait tous les deux vers l'est ; et la rumeur de la foule devait « crier plus fort que le murmure voulu » alors que ce voulu plafonne à 1 dès dix passants — il y en avait plus au départ. Trois juges verts par chance de tirage, durcis sans changer ce qu'ils mesurent, et vérifiés verts sur l'ancienne ville comme sur la nouvelle. `tests/test_distributrices.py` (le matériel au chevet, la salle d'attente, le plan qui refuse un malade au pied du lit) et `test_distributrices_js.py` (trois cents images plus tard, personne ne s'est levé) |
| Les machines distributrices | **livré** | 16 sept. 2026 | **P4** | ajout | demande de Martin : « ajoute aussi un concept de machine distributrice partout dans la ville ». ⚠️ **Mesuré avant : zéro.** **Livré** : **trois sortes** (`magasins.DISTRIBUTRICES`) — la machine à **liqueur** (liqueur, jus), à **grignotines** (chips, chocolat), à **café** (café, soupe en gobelet) —, chacune avec sa couleur qu'on reconnaît de l'autre bord de la rue. **Dans la rue**, 32 à 35 machines selon la graine (`carte.distributrices`) : adossées à une devanture, jamais sous une porte, une rangée libre devant, la sorte tirée dans la famille du commerce (du café devant la soudure, de la liqueur devant la taverne), et **neuf au plus par district** — sans ce plafond, La Shop et les Quais en prenaient 35 sur 48 et les Érables une seule. ⚠️ **Mesuré** : sous les 313 façades de commerce, 265 donnent sur un parvis de dalle et 35 sur l'abord ; la règle du guichet (l'abord seulement) ne laissait que **cinq** machines dans toute la ville. ⚠️ Elles tirent dans **leur propre dé, après les paquets** : un juge génère la ville avec et sans, et tout le reste est identique. **Dans les salles d'attente** : le terminus (la première pièce du jeu), le poste de police (sa machine à café) et l'urgence, en meuble `b` portant un point `distributrice`. ⚠️ **Jamais collée à une porte** : à moins de 22 px de la tuile où l'on pousse une porte, une machine lui volait ACTION — l'invite disait MACHINE À CAFÉ devant l'entrée d'un commerce (un juge des intérieurs l'a vu le jour même). La ville ne les colle plus, et `distributriceSousLaMain` cède la main à la porte. **Au prix du comptoir** (les articles pointent dans `TARIFS`, `itemBouchee` sert les deux), et la **spirale** garde l'achat une fois sur sept : on a payé, rien ne tombe, l'invite devient BRASSER LA MACHINE, et une secousse sur deux le fait tomber ; la nuit vide ce qui est resté pris. **Défoncée** — une berline suffit, trois balles aussi — elle crache sa monnaie en trois tas et deux canettes qui se boivent en passant : une étoile, et seulement si un témoin va le raconter ; au matin elle est debout. ⚠️ Un juge tient qu'une nuit à défoncer **toutes** les machines (40 × 22 $) rapporte moins qu'une journée honnête (1 230 $). Trois bruitages synthétisés (la canette qui tombe, la machine brassée, la monnaie) : le seau des échantillons est plein |
| Dormir jusqu'au soir | **livré** | 16 sept. 2026 | **P2** | ajout | demande de Martin : « ajoute un mécanisme pour passer de jour à nuit ». ⚠️ **Mesuré avant** : le lit ne mène qu'au MATIN (7 h 12), et `estNuit()` ne s'allume qu'à **19 h 52** — une mission `nuit` prise au réveil faisait donc **attendre 4 min 15 réelles** sous « ATTENDS LA NUIT », sans rien à faire. Le lit (la planque, la chambre de l'Hôtel Bandini) propose **DORMIR JUSQU'AU SOIR** tant qu'il fait jour dehors : fondu au noir, réveil à **20 h 45** (lampadaires allumés, feux déjà au clignotant), endurance pleine, **25 % de la vie** (choix de Martin : une sieste n'est pas une nuit), étoiles effacées et partie sauvée comme au sommeil. ⚠️ Offerte seulement le jour, elle ne passe **jamais minuit** : aucun `nouveauJour()`, donc ni dette, ni revenus, ni skimmers de plus. Les réglages sont `economie.SIESTE` (`reveil` 0,865, `soin` 0,25) ; la nuit et la sieste partagent `seReveiller`, et `Monde.estNuit(heure)` répond pour DEHORS même depuis une pièce (sans argument, un intérieur n'est jamais de nuit — le lit posait la mauvaise question). ⚠️ Un juge mesure la nuit **minute par minute sur la table des teintes** : le réveil doit tomber après le clignotant et laisser au moins 85 % de la nuit. 4 juges de banc (`test_sieste_js.py`). |
| Le port du Faubourg touche l'eau, et les chaloupes mouillent dans la baie | **livré** | 16 sept. 2026 | **P2** | **correctif** | retour de Martin, capture à l'appui : « il y a encore des quais entre deux routes ». ⚠️ **Mesuré** : les deux quais du Faubourg (`qq` au plan) sont du plancher plein **entouré de rues** — une rue de chaque côté, et dessous un boulevard à quatre voies, une plage, puis la baie. Le défaut des Quais, un bloc plus à l'est, et il était nommé comme « reste ouvert » dans la livraison du port. ⚠️ **Et un second, trouvé en mesurant** : **8 des 18 chaloupes ne mouillent pas dans la baie** — trois dans l'étang du Faubourg, trois dans le chenal de La Pointe, deux dans des **mares de parc de 2 et 6 tuiles**. Le semis parcourt la carte du nord au sud et s'arrête à dix-huit : il remplit les mares du nord avant d'atteindre le port. ✅ **Livré** (16 sept. 2026). **`jj`, pas `qq`, dans le plan du Faubourg.** Ses quais ne peuvent pas AVALER la baie comme ceux des Quais — elle est dans un autre district, et une fusion ne passe jamais une frontière — mais `j` est de l'eau pour la trame (`EAUX`), et c'est suffisant : une rue qui ne longe que de l'eau et du quai est noyée. Le boulevard sous les quais devient la baie, la rue entre eux une darse, la rue vers l'étang un bras d'eau ; celle du nord, qui longe des immeubles, reste la rue de service. Plus un seul quai de la ville sans lèvre sur la baie. ⚠️ **Les chaloupes** : le semis parcourait la carte du nord au sud et s'arrêtait à dix-huit — il remplissait les mares avant d'atteindre le port. `la_baie()` (le plus grand plan d'eau), et les rives de quai passent avant les autres : **18 chaloupes sur 18 dans la baie, dont 10 à quai** (contre 8 hors de la baie). Rouge-avant prouvé sur les deux juges neufs. ⚠️ **Deux juges voisins changeaient avec la carte, et c'est eux qui ont bougé** : l'homme-sandwich se plaçait toujours 22 tuiles à l'EST de son poste, et le poste 0 est tombé à 21 tuiles du bord — joueur posé hors du monde ; le ballon de plage attendait que le hasard rapproche deux enfants alors que le juge dit lui-même mesurer « le geste, pas la chance » — il les rapproche maintenant, dans la bulle du joueur. ⚠️ **Et la leçon du dossier partagé, payée une fois de plus** : une autre session écrivait l'arche de la foire dans `app/carte.py` pendant ce temps-là, et recopier le fichier de l'arbre dans le worktree de mesure a fait tomber sept juges qui n'étaient pas à moi. Le fichier se reconstruit sur HEAD, par ancres. ⚠️ **Reste ouvert, nommé** : l'**étang du Faubourg** (439 tuiles) touche maintenant le quai mais pas la baie — un croisement de rues le ferme au sud-est ; le relier demande un pont, donc un jalon à lui. 1836 tests. |
| Une chaloupe sur la route | **livré** | 16 sept. 2026 | **P2** | **correctif** | retour de Martin, capture à l'appui : « un bateau sur la route ?? » — une chaloupe arrêtée dans sa voie au passage piéton, cap à l'est. ⚠️ **Ce n'était pas l'amarrage** : les dix-huit places sont bien sur l'eau. **C'était un VOL.** Le voleur de char (`Entites.majVolDeChar`) prend le premier véhicule garé à l'écran, et une coque amarrée est `stationne` comme une auto : pour un passant du quai, c'était elle. Volée, elle passait au trafic (`conducteur: 'trafic'`), et **le trafic roule sur des rails sans lire une seule tuile** (`v.x += v.vx`) — `tuileInterdite`, la seule règle qui tient une coque sur l'eau, n'y est jamais consultée. La voie la plus proche (`voieLaPlusProche`, trois tuiles) l'attendait sur la rive : elle y montait et faisait sa tournée. **Mesuré au banc avant** : visée, emportée, puis **911 images sur 1 500 au sec**, cap à l'est sur une chaussée. ✅ **Livré** (16 sept. 2026) : **on vole un char, pas un bateau** — le voleur ignore une coque (`def.eau`) ; et **le trafic ne navigue pas** — une coque qu'on lui confierait est lâchée sur place, sans conducteur (`majConducteur`), pour le prochain chemin qui le ferait. ⚠️ Au banc, **le témoin compte autant que la règle** : une auto garée au même endroit se fait toujours voler — sans lui, un voleur qui ne vole plus rien passerait le juge. ⚠️ Et le juge cherche son eau **dans la carte, pas dans `amarrages`** : une autre session déplace les chaloupes vers la baie le même jour. 2 juges neufs dans `test_ville_vit.py` (429 images au sec pour une coque confiée au trafic, avant), 1836 tests. |
| Le motard revient sur la moto volée | **livré** | 16 sept. 2026 | **P1** | **correctif** | retour de Martin : « quand on vole une moto, la personne qui était dessus s'en va, mais quand on la quitte, il y a encore une personne dessus ». ⚠️ **Mesuré** : descendu de la moto, on revoyait **le même** motard qu'avant le vol (mêmes couleurs), et le passant qui sortait n'avait pas sa tête. `Vehicules.monter` n'effaçait le pilote du trafic (`v.pilote = null`) que dans la branche du **vélo** ; la moto passe par le carjacking, qui faisait sortir un passant tiré au hasard et laissait `v.pilote` sur la selle — caché par le joueur tant qu'il roulait, revenu dès qu'il descendait. Le carjacking fait maintenant descendre **celui qui était dessus**, avec ses couleurs, comme le vélo — sans tirer de dé de plus. ⚠️ **Et la règle se tient une fois pour tous**, dans `cavalierDe` : le pilote du trafic ne se peint que tant que le **trafic** conduit. Le même fantôme restait assis sur la moto du **fuyard** quand il en tombe (`faireTomberLeFuyard` remet `conducteur` à null sans toucher au pilote) pendant que le Cravate s'enfuit avec la caisse. ⚠️ **Reste ouvert, vu en chemin** : ce motard du fuyard porte une tête **de la rue**, pas celle du Cravate qui en descend. 1 juge neuf (`test_poses_vehicules.py`), **rouge avant** sur les trois constats. 1839 tests, jugés dans un worktree isolé, et les fichiers de véhicules rejugés sur le HEAD de la chaloupe. |
| De vraies plages, pas des bouts de sable | **livré** | 16 sept. 2026 | **P2** | **correctif** | retour de Martin : « moins de plage autour, et des accessoires de plage et des gens s'il y a beaucoup de place, pas juste des petits morceaux de plage ». ⚠️ **Mesuré** (graine livrée) : **1 754 tuiles de sable en 65 morceaux**, dont **41 de moins de dix tuiles** — `_eau()` bordait CHAQUE côté de chaque bassin d'une bande de 0 à 4 tuiles qui avançait et reculait, jusque dans le chenal de La Pointe, des deux rives ; et les **104 meubles de plage** tombaient tous sur ces bandes étroites. ✅ **Livré** (16 sept. 2026). **`PLAGES` : peu, mais larges.** Au plus une plage par côté de bassin, sur le plus long bout de rivage d'un seul tenant : **26 à 44 tuiles de long, 5 à 8 de profondeur**, les deux bouts qui s'amincissent. **Jamais dans un chenal** : un bassin donne un tiers de sa largeur s'il y a une rive en face, la moitié sinon, et sous cinq tuiles ce côté n'a pas de plage ; sous **120 tuiles**, pas de plage du tout. Le reste de la côte touche l'eau sans sable. Sur la graine livrée : **cinq plages** de 164 à 224 tuiles — le nord de la baie, sa rive ouest, la rive ouest de La Pointe et deux au sud de La Pointe. Elles **déclarent leur rectangle** (`plages`, dans le paquet). ⚠️ **Leur dé à elles** (`des_plage`), et `_eau` **brûle** ce que l'ancienne rive tirait dans le dé commun (un coup par colonne et par rangée du bassin) : aucun îlot posé après la baie ne change de gabarit. **Les accessoires** : seulement sur une plage déclarée, mais **sur toute sa profondeur** (`GREVE["bord"]` passe de 3 à 8 : à trois, le fond d'une plage large restait nu), une vingtaine par plage ; trois fiches neuves — la **chaise longue**, le **kayak** et la **chaise du sauveteur** (une par plage, au milieu, posée avant le semis ; solide, elle cède sous un char comme un banc). Le château passe **en tête** du tirage : tiré en dernier, il n'en restait que deux pour cinq plages. ⚠️ **Effet de bord, trouvé en mesurant** : sans sable, le trottoir du chenal de La Pointe touchait l'eau et prenait un **poteau d'amarrage tous les trois pas** — la palissade que le quai avait déjà appris à ne pas planter ; poteaux espacés de 11 tuiles, bouées de 6. **Les gens** : `baigneur` et `baigneuse` (le corps commun, et la palette qui les met en maillot), **deux plafonds** — cinq enfants, sept grands — pour que les premiers nés ne prennent pas toutes les places. Ils ne naissent **que sur une plage déclarée** (la première règle, « du sable avec l'eau à trois tuiles », en faisait naître au bord des étangs de parc). Les grands se font **bronzer** sur une serviette ou une chaise longue **libre**, tout le monde se **promène** sur le sable sans traverser d'anse, et l'on trouve l'eau depuis le fond d'une plage (`bordDeLEau` cherche à neuf tuiles au lieu de quatre). ⚠️ **Un juge rendu déterministe** : « un enfant ne dépasse jamais la première tuile d'eau » attendait qu'un baigneur TIRE la baignade — or le jeu se tire à l'empreinte et dure une à trois minutes, donc un tirage en trente secondes ; sur la ville d'après la foire, personne ne l'a tirée et le juge est tombé sur « il ne mesure rien ». Il envoie désormais chacun à l'eau par `bordDeLEau` (le geste, pas la chance) ; vérifié en retirant l'arrêt au premier pied mouillé : **962 images au large**. **Juges** (`test_greve`, `test_plage_js`) : chaque plage a la place, **tout sable qui touche le large est une plage déclarée**, les accessoires de plage n'existent que dedans, un sauveteur par plage, pas de plage dans un chenal, le dé de la ville intact ; les baigneurs ne naissent que sur une plage (vérifié en retirant la règle : **12 baigneurs au bord d'un étang**), des grands aussi, et un grand bronze sur une serviette que personne d'autre ne prend. |
| Se réveiller dans un lit d’hôpital | **livré** | 16 sept. 2026 | **P2** | ajout | demande de Martin : « pour le réveil à l'hôpital, je veux qu'on se réveille à l'intérieur et dans un lit, couché, dès le premier déplacement on se lève et on peut partir ». On se réveillait **dehors**, sur le trottoir devant la porte. Au noir de l'ellipse, la pièce de l'hôpital se charge **comme par sa porte** (`Jeu.chargerPiece`, désormais la seule façon d'entrer : `entrer()` y passe aussi) et le joueur prend **le lit du malade de l'urgence** — sa tuile de tête, la pose `alite`, les pieds à `PIEDS_ALITE` ; le malade n'y est pas cette fois. Rien ne sort du lit — ni FRAPPE, ni SPRINT, ni ACTION, ni un passant qui bouscule le dormeur (`cede`) — sauf **la première poussée du stick**, qui pose le joueur **à côté** du lit, du côté où l'on pousse, et on marche dans la même image. ⚠️ Un meuble n'arrête personne : se lever sur place, c'était se tenir debout sur l'oreiller. La porte d'en bas mène devant l'hôpital. ⚠️ **Tomber dans une pièce** (la planque, un comptoir) : on en ressort d'abord (`Jeu.quitterLaPiece`) — `Monde.entrer` part de la ville, et une pièce chargée par-dessus une pièce perdait le chemin du retour. ⚠️ **Arrêté pendant le fondu de l'hôpital** : la prison lève le joueur et sort de la pièce ; sans ça, on sortait de prison… couché dans le lit. ⚠️ **Pas de clignotement** dans le lit (personne à craindre, et un corps qui clignote sous sa couverture a l'air d'un bogue) ; la ville sans hôpital garde l'ancien réveil devant la porte. ⚠️ **Mesuré en chemin, PAS corrigé** : le `recul` d'un coup n'est **jamais** décompté pour le joueur (seul `majPieton` le fait) — après n'importe quel coup, il reste penché de 0,22 rad pour de bon. Le lit le remet à zéro ; la rue, non. 3 juges neufs (`test_distributrices_js.py`), **rouges avant** ; chaque garde prouvée par mutation (sans `cede`, poussé de 3,5 px ; sans le recul remis, penché de 0,22 ; sans la garde du combat, le poing part du lit ; sans la sortie de prison, le juge de l'arrestation tombe). 4 juges d'hôpital de `test_moteur_js.py` suivent maintenant le joueur dans la pièce au lieu de le chercher sur le trottoir. |
| Des voix qui jouent, et qui finissent leurs phrases | **livré** | 16 sept. 2026 | **P2** | **correctif** | demande de Martin : « je veux que tu regénères toutes les voix en mettant des pauses dans le texte et de l'émotion, et un léger temps mort à la fin pour éviter les fins coupées ». Les **83 répliques** (passants, radios, pubs, missions, journal, ouverture) refaites en **eleven_v3** ; leur jeu vit dans `app/interpretation.py` — balises d'émotion **en anglais** (`[sighs]`, `[coldly]`, liste fermée : une balise inconnue se lit à voix haute), pauses « … » — et un juge exige **les mêmes mots** que la boîte (il attrape aussi un slug décalé par une ligne insérée). ⚠️ **Les fins coupées venaient de DEUX endroits** : (1) le **fichier** — les 19 répliques du narrateur finissaient à 10-47 ms du dernier son ; `finir_voix` pose maintenant **0,35 s de temps mort** ; (2) **le jeu** — `majCinema` passait à la ligne suivante après le temps de *lire* (90 + 3 par caractère), voix ou pas, et la suivante **coupe** la voix : **9 répliques de mission y perdaient déjà leur fin** (`bouchard-m4-6` : 7,06 s de voix, 5,65 s de ligne). Régénérer n'aurait réparé que la moitié, et les pauses auraient coupé tout le reste : la ligne **attend sa voix** (plafond +15 s si le navigateur ne dit jamais qu'elle s'est tue ; ACTION passe toujours). ⚠️ **v3 ajoute du silence de lui-même** — 1re génération : jusqu'à **2,9 s de zéros** après la dernière syllabe, 1 s avant « Excusez-moi », neuf trous de 1,2 à 1,6 s. La finition rogne les bords et ramène toute pause à **0,7 s** (seuil −45 dB, mesuré : le silence tombe sous −45, un soupir entre −35 et −45 — −48 d'abord ne ramenait rien), et la règle d'écriture est devenue « une balise par réplique dès qu'elle respire ». **Niveau** : de −32 à −15 LUFS avant (17 dB d'écart), toutes à **−19** maintenant ; l'encodeur mp3 dépassait le pic visé de **2,3 dB**, la finition remesure et réencode. Durée totale 336 → 407 s (×1,21), ouverture 25,7 s (sa musique fait 30 s) ; poids : histoire 2,5 Mo / 3, bruitages + passants 1,21 Mo / 1,5. Outils : `--masters DIR` garde les masters, **`--refinir`** rejoue la finition sans rien payer ; `--refaire ti_guy-m1-1` répondait « slug inconnu » (le `-1` lu comme une variante) — réparé. **13 159 crédits** (3 essais, 2 générations). `test_interpretation.py` : 335 juges (mots, balises, câblage, temps mort et niveau mesurés sur chaque fichier, la ligne qui attend sa voix au banc — rouge sans le correctif de `histoire.js`). ⚠️ **À écouter** : aucun juge ne dit si l'émotion est la bonne — `--refinir` et `--refaire <slug>` pour celles à reprendre. |
| Des voix sans réverbération | **livré** | 16 sept. 2026 | **P2** | **correctif** | retour de Martin après écoute : « caverneuses ou étouffées », puis « regénère Mme Thibodeau et les prostituées et toutes les voix avec réverbération, je les veux sans réverbération ». ⚠️ **Mesuré d'abord, et étalonné** : la vitesse de chute du son en fin de syllabe (95e centile, dB/s) — une pièce la borne ; une voix sèche à 534 tombe à 315 quand on lui ajoute soi-même une réverbération de 0,4 s. ⚠️ **Régénérer ne sèche rien** : même phrase de Mme Thibodeau, v3 en stabilité 0 / 0,5 / 1 et en similarité basse, entre 294 et 350 ; v2 et turbo montent à 423-443 mais perdent l'émotion. Ce qui sèche, c'est l'**isolateur d'ElevenLabs** — ajouté au serveur MCP maison (`elevenlabs_voice_isolation`, hors dépôt ; refuse sous 4,6 s : on allonge de silence et on recoupe) : sur la voix réverbérée à 0,4 s, **315 → 532**. Passé sur les masters déjà payés, **sans régénérer une réplique** (`--secher --masters`). ⚠️ **Il ne sèche que ce qui est mouillé** : Julia (Thibodeau, la Brume, La Brume radio) 347 → 373 et le narrateur 428 → 471, timbre intact (Julia gagne même 6 dB d'air) ; Amélie, Felix et Léo **rien à retirer** (432, 436, 443 avant comme après — leur écart avec v2 était le débit de v3) et Felix et Léo y perdaient 1,5 à 4,6 dB d'aigus : **pas séchés**, sinon plus étouffés. `interpretation.VOIX_A_SECHER` = Julia + narrateur ; la génération sèche avant de finir, `--refinir` repart du master séché, et chaque fichier séché porte `comment=voix isolee` — un juge le lit sur les **35 fichiers** (rouge avant). ⚠️ Ce qui reste à Julia (373, une voix sèche est à 510+) **n'est pas la pièce, c'est sa voix** : rauque, fins de mots soufflées — même v2 isolée plafonne à 441 ; plus sec voudrait dire **une autre voix** pour Thibodeau et la Brume. 7 378 crédits (essais compris). ⚠️ **À écouter** : c'est l'oreille de Martin qui dit si la pièce est partie. |
| Le vélo et son cycliste | **livré** | 16 sept. 2026 | **P2** | **correctif** | retour de Martin, capture à l'appui : « il faut améliorer ça ». ⚠️ **Mesuré** : la machine qui tournait était le **toit** d'un deux-roues — vu d'en haut, un vélo est un bâton avec une barre en travers (vers l'est, un trait de trois pixels et le guidon dressé en travers) — et le cycliste posé dessus était un passant **assis**, la pose d'un banc : les fesses à la hauteur des moyeux, les mains sur les cuisses, les pieds dans le vide. On lisait un passant sur une échasse. **La machine est maintenant décrite en volume** (`MACHINE_VELO`, `MACHINE_MOTO` : roues, cadre, guidon, selle, porte-bagages, réservoir, moteur, lampes) **et se projette au cap** (`Atlas.projeter`) dans la vue de la ville : ce qui est debout monte à l'écran, et le sol se voit du **même biais que l'ombre** (0,5 — un juge les tient d'accord). De profil, deux roues rondes ; de dos, un trait, un guidon et un feu ; en diagonale, des roues en ellipse. ⚠️ **Rien de « le char tourne comme son ombre » n'est perdu** : 32 caps, 32 dessins distincts, cuits un par un à la demande (la grille par cap, le canevas par couleur) ; les poses `cote`, `haut`, `bas` du vélo et de la moto sont désormais **tirées** de la machine, plus dessinées à la main. ⚠️ **Une lampe est un bloc, pas un point** : un point se cachait derrière la première roue venue — le phare du vélo ne se voyait qu'à 13 caps sur 32, et la moto n'avait aucune lampe visible à 6 ; en bloc, phare et feu se voient ensemble à 28 caps sur 32. **Le cycliste roule** : trois poses neuves du passant (`roule_cote`, `roule_haut`, `roule_bas`, deux images chacune), dessinées là où la projection met la selle, le guidon et les pédales — de dos, le guidon est devant lui, donc plus **haut** à l'écran, et ses mains montent aux épaules ; de face, plus **bas**, et elles tombent à la ceinture. Il **pédale** avec la distance roulée (`v.parcouru` — la distance, pas la vitesse : un vélo poussé contre un mur ne pédale pas), un demi-tour tous les `pedale` px de la fiche ; la moto n'en a pas, et son pilote garde les pieds aux repose-pieds. La `selle` est **tirée** de l'`assise` de la machine : un seul siège, pas deux nombres à tenir d'accord. `assis` reste la pose du banc. 4 juges neufs, **rouge avant prouvé en retirant chaque règle** (vue d'en haut : « sa rangée de sol touche 1 fois — on voit une machine d'en haut » ; cap figé : « aux caps 1 à 31, ce qui se peint n'est pas sa projection » ; pose assise : « sa main est à 3,0 px de la poignée » ; compteur retiré : « le vélo a roulé 40,9 px et n'en compte que 0 ») ; 3 juges de toit (phares, bouts de caisse, lampes du moteur) ne regardent plus que les chars, et le dessin centré sur son empreinte tient toujours les deux-roues. 2189 tests |
| Les chars en volume | **en cours** (la berline livrée) | 16 sept. 2026 | **P2** | **correctif** | demande de Martin, après le vélo : « je veux que tu fasses une belle job comme ça avec les voitures, commence par une et je te donne le go pour la suite ». Le char qui roule est son **toit** (la pose `haut`, une vue plongeante de dos) tourné en 32 caps : vers l'est, un toit couché sur le flanc, pas une auto de profil. ✅ **La berline, livrée** : l'auto, le taxi et la police partagent **une seule carrosserie** (un juge le tient), donc convertir « une voiture », c'est les convertir tous les trois. Elle est décrite en volume (`MACHINE_BERLINE`) et projetée au cap comme le vélo, avec deux outils de plus dans `Atlas.projeter` : la **silhouette de profil extrudée** (`profil` — capot et pare-brise en pente, quatre passages de roue, ce qu'une boîte ne sait pas faire) et le **contour** `k` de la silhouette, comme tout ce qui est dessiné à la main (le vélo n'en veut pas : ses tubes d'un pixel en feraient des barres). ⚠️ **La livrée était rouge en dur** : la carrosserie commune peignait bande `y` et damier `x`, et l'auto les rendait « invisibles » en les mettant au rouge de sa palette — mais seul `c` suit la couleur tirée à la naissance, et une berline bleu marine aurait roulé avec une bande et un damier rouges dès que son flanc se dessinait. Le taxi et la police **ajoutent** leur livrée (`LIVREE`) ; l'auto n'en porte pas. ⚠️ **Des phares posés dans la caisse ne se voient que de face** (4 caps sur 32) : ils enveloppent maintenant le coin, et phare et feu se voient ensemble à 25 caps ou plus. ⚠️ **À trancher par Martin** (artefact « La berline de Bandini ») : de dos, le sol se voit du biais de l'ombre (0,5), et la berline occupe 21 rangées pour 28 px de long, là où le toit tourné en occupait 28. 1 juge neuf (la livrée s'ajoute, l'auto n'en porte pas — **rouge avant** en remettant la livrée sur l'auto), les juges des machines (roues au sol de profil, projection au cap, lampes) étendus à toute fiche en volume, et 9 juges de grille repris : l'ancre à la ligne de sol se juge sur la sport, le compte d'atlas admet une grille et un canevas par cap, et ceux qui comptaient les chars à toit en attendent sept. Restent, au go de Martin : sport, luxe, camion, autobus, ambulance, remorqueuse, chaloupe. 2189 tests |
| Gyrophares et enseignes sur le toit | **en cours** | 16 sept. 2026 | **P2** | ajout | demande de Martin : « taxi et tous les véhicules qui en ont besoin doivent avoir des indicateurs ou gyrophare sur leur toit. comme en vrai. » ⚠️ **Mesuré** : aucun char n'en a — la police n'a jamais eu de rampe, et les dessins de dos de l'ambulance et de la remorqueuse n'ont ni gyrophare ni croix (les commentaires qui en parlent sont restés d'un dessin d'avant). |
| L'Île-aux-Corneilles | **à faire** | — | **P4** | ajout | demande de Martin : « tu peux extensionner la carte au besoin » — ⚠️ mesuré, le besoin est nul : **21 % de la carte est déjà de l'eau** (18 675 tuiles) et un rectangle de **40 × 24 tuiles d'eau pleine** attend au milieu de la baie. Une île, un quai, une chapelle, une usine à poisson fermée, **pas de police** (on y laisse refroidir un char et un casier), et une seule porte de sortie. Elle donne enfin une destination au traversier de M12 et à la fin _Le dernier traversier_ |
| Quatre activités que le jeu n'a pas | **à faire** — ⚠️ **une des quatre est déjà livrée** | 15 sept. 2026 | **P4** | ajout | sorti de la tournée du net : des **paliers** de boulot avec récompense permanente (**livrés le 15 sept.**, `aee8543` : +25 % de vie à 25 ambulances, le char à la planque à 50), deux boulots de plus sans un seul véhicule neuf (**la patrouille** — la _vigilante_, mais avec un casier et un char volé — et **pompier volontaire**), **la liste du quai** (quatre modèles demandés, sans bosse) et **les frénésies**, à trancher par Martin ; ⚠️ les enfants restent intouchables |
| Installable, et jouable hors ligne | **à faire** | — | **P4** | ajout | demande de Martin : « est-ce compliqué de faire du jeu une webapp installable ? », puis « jouable hors ligne ». ⚠️ **Mesuré : sur iPhone, la moitié est déjà faite, et personne ne l'a voulu** — `base.html` porte déjà `apple-mobile-web-app-capable`, `mobile-web-app-capable`, `theme-color` et `viewport-fit=cover` : « Ajouter à l'écran d'accueil » donne **aujourd'hui** une app plein écran sans barre Safari. Il n'y manque qu'une **icône** — iOS ne prend pas un `favicon.svg` et colle une capture d'écran floue à la place. Android et Chrome bureau, eux, exigent trois choses : un `manifest.webmanifest`, des icônes PNG (192, 512, une *maskable* — Chromium est **déjà là** pour Playwright, il rend le SVG sans rien ajouter au projet) et un service worker **qui a un gestionnaire `fetch`** : sans lui, Chrome ne propose pas l'installation du tout. ⚠️ **Le worker se sert à la RACINE, et c'est le seul vrai piège** : Flask sert tout sous `/static/`, or un worker ne contrôle que son dossier — `/static/js/sw.js` ne verrait jamais `/`. Il lui faut sa route à lui dans `routes.py`, en `no-cache` : nginx met `expires 7d` sur `/static/`, et un worker figé une semaine est un piège qui se referme sur la session suivante. ⚠️ **Le poids est mesuré, et c'est lui qui décide** : la coquille pèse **300 Ko** de JS gzippé et **65 Ko** de définitions (492 Ko brut) — précachée sans y penser ; l'audio pèse **12 Mo en 166 fichiers**, chargés à la demande (`son.js` : `fetch` puis `decodeAudioData`). Avaler 12 Mo en silence sur un forfait cellulaire n'est pas une fonctionnalité : l'audio se cache **à l'usage**, et « toute la ville hors ligne » est un **bouton** qu'on choisit. ⚠️ **Le cache se nomme par l'EMPREINTE, jamais par la version** — `definitions.py` calcule déjà un sha256 du paquet, et la sauvegarde s'en sert pour oublier une position qui n'existe plus (`jeu.js`). Un paquet caché qui ne correspond plus au JS servi ne ressemble pas à un bogue de cache : il ressemble à un bogue de jeu. C'est mot pour mot ce que `version.py` dit déjà dans sa propre docstring. ⚠️ Et **un worker naïf casserait la revalidation 304** montée dans `api_definitions` — celle qui accepte l'ETag **faible** de nginx. ⚠️ **Les mp3 ne portent pas `?v=`**, contrairement au JS : un bruitage regénéré garde son nom, donc un cache d'usage servirait l'ancien pour toujours. Il faut une règle de purge, et elle n'a pas de version à quoi se raccrocher. ⚠️ **Les scores restent en ligne** : `horsLigne` existe (`jeu.js`) mais ne couvre que l'échec de chargement des définitions — l'écran des scores n'a aucun chemin hors-ligne, et un tableau vide qui ment est pire qu'un tableau qui dit « pas de réseau ». ⚠️ À **vérifier sur le serveur** : le snippet de sécurité nginx (`gestion-dojo-security-server.conf`, hors dépôt) peut porter un CSP qui bloque `worker-src` ou `manifest-src` — et ça ne se verra qu'en prod. Deux vagues : **(1) l'installation** (manifeste, icônes, worker minimal — ~2 h), **(2) le hors-ligne pour vrai** (coquille précachée, audio à l'usage, définitions par empreinte, scores qui disent la vérité — ~1 jour). Les juges ont déjà leur banc : `test_navigateur.py` lance un vrai Chromium, donc le worker se juge en coupant le réseau après le premier chargement. |
| M16 Cent missions | **à faire** (v2) | — | **P4** | ajout | demande de Martin : « plus de 100 missions avec les personnages existants et de nouveaux personnages, partout sur la carte ». **109 missions de plus** en 9 arcs, 34 personnages, 9 types d'objectifs de plus — et rien d'autre : le moteur apprend neuf verbes, le reste est du catalogue. ⚠️ Le carnet passe avant (cent missions sans carnet, c'est cent appels qu'on oublie) ; M13 en devient la dernière tranche |
| M13 Les deux fins | **à faire** (v2) | — | **P4** | ajout | une mission par district, Marco qui te vend, Dr Lachance donneur, _Le Boss_ et _Sacrer son camp_ |

## Dettes

⚠️ Ce qui est **sciemment pas fait**. Ça vivait éparpillé dans les notes de jalons, là où on
ne relit jamais — et une dette qu'on ne relit pas devient un oubli. Chacune porte donc son
**déclencheur** : la chose qui dit qu'il est temps de la payer. Une dette sans déclencheur
est un oubli avec du style.

| Dette | Pourquoi pas fait | Déclencheur |
|---|---|---|
| Les radios **10-4** et **Radio-Traversier** sont déclarées mais jamais générées ni écoutées | ElevenLabs Music se paie à la seconde, et M8 avait déjà de quoi écouter | La prochaine séance avec la clé : `uv run python scripts/audio_elevenlabs.py --refaire dix_quatre traversier` — puis **les écouter**, un fichier qui se décode n'est pas un fichier qui sonne bien |
| Le **rythme mesuré sur le vrai téléphone** de Martin (reporté de M7) | Les chiffres du banc (0,29 ms/image de nuit à 5★) sont ceux d'une machine de développement | Avant M12 : la neige touche à la physique **et** au rendu, c'est là que le budget casse |
| Le **découpage du paquet** (`/api/carte`, ETag, districts chargés autour du joueur) | 43 Ko gzip aujourd'hui (370 Ko bruts ; plafond brut relevé à 600 le 13 sept. 2026, parce qu'il n'est qu'un indicateur : le fil et `JSON.parse` sont les vraies bornes) : le découper maintenant coûterait de la complexité pour rien | Écrit d'avance depuis M8 : **plus de 2 s entre « Jouer » et la ville** sur le téléphone de Martin |
| Le **bateau** reste en phase 2 (sans sprite, hors trafic) | Physique à part, tuiles d'eau carrossables, un quai où embarquer — il coûte plus qu'il ne donne aujourd'hui | Si le **traversier de M12** ne suffit pas à donner envie de l'eau. Sinon il tombe en v3, et la fiche le dit |
| `SECRET_KEY` vaut `cle-de-developpement-a-changer` **par défaut** — ⚠️ mais `installer.sh` en génère déjà une vraie (`token_hex(32)`) dans le `.env` partagé, depuis M0 : ce qui reste, c'est que l'application **refuse de démarrer** avec la clé de développement quand `FLASK_DEBUG` est faux | Sans compte ni session, une clé faible ne protège rien | **M14** : le jour où une session vaut une partie |

⚠️ Et une **fausse** dette, pour qu'on arrête de la reprendre : `tests/test_navigateur.py` est
exclu de la commande locale ci-dessous parce qu'il monte un Chromium et prend des minutes —
mais **la CI le fait tourner**, dans un deuxième job, avec `BANDINI_TESTS_OBLIGATOIRES=1`.
Il n'est pas oublié, il est ailleurs.

## Reprendre le travail

```bash
cd ~/dev/bandini
uv sync --all-groups && cp -n .env.example .env
git config core.hooksPath scripts/git-hooks
uv run ruff check . && uv run pytest -q --ignore=tests/test_navigateur.py
uv run python run.py          # http://127.0.0.1:5400 — et http://192.168.x.x:5400
                              # depuis le telephone (APP_HOST=0.0.0.0 par defaut)
```

Les sons manquants se regénèrent par le serveur MCP `elevenlabs` (clé dans
`~/.mcp-servers/elevenlabs/cle.txt`) :

```bash
uv run python scripts/audio_elevenlabs.py --essai       # ce qui serait généré
uv run python scripts/audio_elevenlabs.py               # génère les bruitages qui manquent
uv run python scripts/audio_elevenlabs.py --radios      # … et les stations de radio (musique : cher)
uv run python scripts/audio_elevenlabs.py --voix        # … et les voix (passants + histoire, au caractère ; eleven_v3, leur jeu dans app/interpretation.py)
uv run python scripts/audio_elevenlabs.py --musiques    # … et les 15 musiques du jeu (30 crédits/seconde)
uv run python scripts/audio_elevenlabs.py --refaire coup pas la_brume titre amb_quais ti_guy-m1-1
```

La musique se génère **et** s'écrit. Les quinze morceaux sont des mp3 ElevenLabs
(recette dans `audio.MUSIQUES`) **et** restent écrits en notes dans
`app/musique.py` : le fichier joue, les notes sont le **filet**. Elles se rendent
en WAV pour l'oreille, gratuitement et hors ligne :

```bash
uv run python scripts/musique_apercu.py                       # le thème du menu, en notes
uv run python scripts/musique_apercu.py titre --tours 2 --normaliser --sortie /tmp/t.wav
```

Les répliques de l'histoire vivent dans `app/missions.py` (`CATALOGUE[…]["dialogue"]`) ;
le slug de voix `<qui>-<mission>-<n>` suit la place de la réplique (appel, intro,
client, fin, échec). Changer un mot = régénérer cette ligne (`--refaire`). Les voix
des personnages sont nommées dans `missions.PERSONNAGES` (compte ElevenLabs de Martin).

**Mode trace** (quand un char reste pris, tourne en rond, sort de la rue) : ouvrir
`https://bandini.gestiondojo.ca/?trace=1` (ou PAUSE → OPTIONS → TRACE DES VÉHICULES).
Chaque char du trafic traîne son trajet (vert : roule, jaune : attend un feu, un stop ou
la boîte, rouge : immobile depuis 2 s), une ligne bleue vers sa tuile cible, un carré sur
la sortie choisie, et son état au-dessus (`FEU 4S`, `BOITE`, `DANS`…). Le jeu se surveille
lui-même : **chien de garde** déclenché, **tourne en rond** (trois fois la même boîte en
20 s), **hors voie** (90 images hors de la chaussée) — l'anomalie s'affiche en rouge sur
place pendant dix secondes avec le trajet des huit dernières secondes, et s'écrit dans la
console (`[trace] …`) et dans `BANDINI.B.trace.anomalies`. Le bilan est en bas à droite.
Une capture d'écran de l'anomalie suffit pour la reproduire au banc.

Mise en ligne : `deploy/README.md`. Chaque jalon terminé est déployé et testé
par Martin sur téléphone (tactile) et ordinateur (manette).

---

## Contexte

Martin veut un nouveau jeu, **Bandini**, publié sur **bandini.gestiondojo.ca** comme ses
autres jeux (Flask + uv, gunicorn, systemd, nginx, Caddy, DNS NameSilo, modèle
« releases + current »). Concept : un monde ouvert en **pixel art, vue trois-quarts**
(GTA 1/2, Zelda), où l'on incarne un petit bonhomme qui marche, se bat à mains nues ou
avec des armes ramassées au sol, affronte d'autres personnages, vole des véhicules de
plusieurs types ; des policiers patrouillent et, s'ils **voient** un crime, poursuivent
et emprisonnent ; la prison coûte de l'argent.

Décisions prises avec Martin (12 sept. 2026) :

| Décision | Choix |
|---|---|
| Vue | trois-quarts, tuiles carrées 16 px, façades visibles (pas d'isométrique) |
| Ton | **adulte** : les personnages meurent, sang pixel **activé par défaut**, désactivable dans les options |
| Dépôt | **nouveau** `ybudoka/bandini` (public), même recette que `car-game`, géré avec **uv** |
| Commandes | clavier + manette (API Gamepad, stick analogique) + tactile (joystick virtuel + boutons) dès la v1 |
| Adresse | `https://bandini.gestiondojo.ca`, gunicorn **8006** (8005 = Auto Évasion, 8004 = KidTube), service `bandini-gestiondojo`, `/srv/bandini`, port local 5400 |
| Mise en ligne | **tôt puis à chaque jalon** : le site existe dès le squelette, chaque jalon est déployé, Martin teste sur téléphone |
| Idées | **toutes** les idées de la première liste + les 28 nouvelles ; prémisse, ville et personnages retenus |
| Audio (12 sept. 2026) | les sons importants sont de **vrais échantillons ElevenLabs**, générés par le serveur MCP `elevenlabs` et versionnés dans `static/audio/` ; la synthèse de `son.js` reste le **filet** quand un fichier manque. Voix des personnages en M6, radios en M3. |
| Voix de l'histoire (13 sept. 2026) | **chaque réplique de l'histoire est dite à voix haute, en plus d'être écrite.** Les dialogues des donneurs (Ti-Guy, Mme Thibodeau, Sgt Bouchard, Josée, Dr Lachance, Marco), le téléphone, les manchettes du journal : une voix ElevenLabs **par personnage**, générée une fois par TTS et versionnée comme le reste. Le texte reste affiché (lisibilité, muet, tactile) ; la voix s'ajoute, elle ne remplace pas. |

## La vision (tout ce qui est retenu)

Étiquettes : **v1** = première version complète ; **v2** = vagues suivantes ; **risqué** = touche au moteur.

**Prémisse.** Tu es « Bandini », surnom hérité de ton oncle Rocco Bandini, petit bandit
mort en laissant un garage, une dette de 15 000 $ au shylock, une cachette et un téléphone
plein de contacts douteux, à **Baie-des-Brumes**, ville de port et de brouillard. Tu
débarques en autobus avec 50 $. Deux fins **v2** : _Le Boss_ (posséder les 4 propriétés,
libérer 4 districts) ou _Sacrer son camp_ (15 000 $ en poche, traversier de nuit à 0 étoile).

**Districts** (M8) : Le Faubourg (centre, gang Les Cravates) · Les Quais (port, Les Morues)
· Les Érables (banlieue, Les Chevreuils) · La Shop (industriel, Les Boulonneux) · La Pointe
(parc au bout d'un pont, Les Skateux), autour de **la baie**. Journal : _Le Clairon de la
Baie_. Radios : _La Brume_ (jazz, auto), _Taxi-Radio_ (country), _Le Choc_ (techno, moto),
_10-4_ (ondes du poste, auto-patrouille), _Radio-Traversier_ (rigodon, camion) ; l'autobus
n'a que son moteur.

**La rue dans la vraie vie (13 sept. 2026)** : un char du trafic ne quitte jamais sa voie
— il est **sur des rails** (centre de tuile en centre de tuile ; la physique arcade ne sert
qu'au joueur, seule exception autorisée hors route). Un piéton ne pose pas le pied sur la
chaussée : il traverse **au passage**, quand les chars de cette rue sont au rouge (ou, sans
feu, quand aucun n'approche) ; poussé sur la rue par un char, il regagne le trottoir. Il
sort des portes et y rentre parfois. Sur un **boulevard** (deux voies dans le même sens), un
char bloqué par un piéton planté sur la chaussée, une épave ou une auto arrêtée **se déporte**
— par la gauche si elle est libre, sinon par la droite — au lieu d'attendre derrière : il vise
la tuile d'à côté et les rails font le virage. Il ne se déporte jamais dans une voie occupée
(couloir vérifié deux tuiles derrière, cinq devant), jamais à l'approche d'une ligne d'arrêt,
et il reste sous la vitesse qui renverse tant qu'il longe l'obstacle. Il ne revient pas dans
sa voie ensuite : la nouvelle en est une. Les croisements à quatre bras ont des **feux** (deux
lanternes), la tige d'un **T** a un **STOP** (arrêt complet, puis passage si la boîte est
libre), et un char cède aux piétons engagés. Des **cyclistes** roulent avec le trafic ; on
peut prendre leur vélo (ils tombent et témoignent) — pas de moteur, pas de radio.

**Vie de rue (12 sept. 2026)** : la foule mêle hommes, femmes, ados, itinérants, livreurs,
**mères accompagnées de leur enfant** et **enfants** — ces derniers sont **intouchables** :
aucune arme, aucun véhicule ne les atteint, ils détalent de plus loin que les adultes. C'est
une règle du catalogue (`pietons.intouchable`), pas une consigne. Les **filles de la Brume**
travaillent la nuit près du bar et du port : on paie, l'écran fond au noir, la vie remonte —
rien ne se montre, et elles refusent quand la police te cherche. Ce sont les **seules à avoir
leur propre sprite** (jupe évasée, jambes nues, blond platine) et elles **tiennent leur coin**
au lieu de flâner : c'est à ça qu'on les reconnaît, pas à la couleur de leur robe. Les **commerces ambulants**
(kiosque à hot-dogs, kiosque à journaux, roulotte à café, camion-restaurant, **cabane à fruits
de mer** aux Quais et à La Pointe) sont posés par le générateur sur les trottoirs et les
stationnements, avec un marchand derrière. Les **hommes-sandwichs** (13 sept. 2026) crient pour
un kiosque : un poste à quelques tuiles, une pancarte plus large que les épaules, ils viennent
vers celui qui flâne, lui tiennent le crachoir dans une bulle et lui glissent un **coupon** —
moitié prix, une fois, trois minutes.

**Donneurs** : Ti-Guy Lelièvre (receleur du garage), Mme Thibodeau (kiosque, potins),
Sgt Réjean Bouchard (mange au casse-croûte, prend 20 %), Josée « La Chef » (Morues),
Dr Lachance (urgentologue), Marco « Le Cousin » (veut sa part, te vendra en v2).

**Monde** : quartiers à police/véhicules/gangs propres · cycle jour-nuit (8 min) · intérieurs
(armurerie, vêtements, hôpital, garage clandestin, poste) · planque (sauvegarde, coffre,
stationnement) **v1** · fourrière, auto-stoppeurs, journal du matin **v1** · tramway,
traversier, tempête de neige avec charrue **v2 risqué**.

**Police** : cône de vision + ligne de vue · témoins qui courent avertir · recherche 1–5 ★
(1 : à pied ; 3 : autos ; 5 : barrages + hélico) · décroissance hors de vue, −1★ en
changeant de véhicule, remise à 0 en changeant de linge · arrestation au contact → prison :
amende, armes confisquées, casier · pot-de-vin (crime si refusé) · **alarmes de char** (3e
canal de détection), **acheter le silence** ou assommer le témoin, **le sergent qui mange**
(policier soudoyé devient ami), affiches « Recherché » **v1** · carnet du poste, le stool,
l'avocat du Carré **v2**.

**Combat** : poing, coup fort (projection), esquive · bâton, couteau, pistolet, fusil,
fronde, extincteur, munitions limitées, armes lâchées par les KO · armes improvisées qui
cassent, projeter dans le trafic **v1** · pompes à essence, bornes-fontaines **v1** ·
bouclier humain **v2 risqué**.

**Véhicules** : auto, moto (rapide, fragile, éjecte), camion, autobus, taxi, ambulance,
auto-patrouille (déguisement), bateau · dégâts, fumée, feu, explosion · garage qui répare
et repeint (la peinture efface le vol) · missions par véhicule au klaxon (taxi, ambulance,
pizza) · pourboire selon la douceur de conduite, cascades notées, rampes **v1** · radio
procédurale par véhicule, remorqueuse **v2**.

**Économie** : 50 $ de départ · taxi, livraisons, courses, revente au garage, cash au sol,
pickpocket **v1** · propriétés à revenu (kiosque 800 $, bar 2 500 $, garage 4 500 $, hôtel
10 000 $) · hôpital facturé · paquets cachés · guichets défoncés au camion et skimmers,
assurance et fraude, le shylock **v2**.

**Missions et narratif** : histoire par téléphone et PNJ, 5 missions v1 (voir plus bas),
3 défis · contacts du marché noir, la peur fait taire les témoins **v1** · **toutes les
répliques sont dites à voix haute** (ElevenLabs, une voix par personnage) en plus du texte
**v1** — voir « Les voix de l'histoire » ci-dessous.

**Meta et présentation** : tableau des scores en ligne (fortune, missions, propriétés,
durée) · bilan de session, caméra qui respire, visée assistée, GPS pointillé, options
(sang, palette daltonienne, vibration) **v1** · défi du jour à graine serveur, mode photo,
coop locale **v2 (M14)**.

## Les voix de l'histoire (décision du 13 sept. 2026)

Le jeu **parle**. Chaque réplique de l'histoire est écrite dans `missions.py` (le texte,
source unique) et **dite** par une voix ElevenLabs générée une fois, comme les répliques
des passants. Ce que ça implique, jalon par jalon :

- **Une voix par personnage**, nommée dans `audio.VOIX_PERSONNAGES`. Martin a ajouté des
  voix québécoises à son compte le 13 sept. ; distribution proposée : Ti-Guy = _Felix
  Tabarnak_ (l'homme de tous les jours), Sgt Bouchard = _Khaivan_ (accent bien dialectal),
  Mme Thibodeau = _Julia_ (courtoise, chaleureuse), Josée « La Chef » = _Jeanne Mance_,
  Dr Lachance = _Patrick_ (clair, ancien journaliste), Marco « Le Cousin » = _Québec
  Tremblay_, le narrateur du Clairon = _annonceur centre d'achat 1_ (vieil homme qui
  soupire), les passants = _Felix_ et _Amélie_ (déjà en place). Une ligne à changer par
  personnage.
- **La réplique est la source** : `missions.py` porte `{"qui": "ti_guy", "texte": "…"}` ;
  le slug du fichier se déduit (`voix-ti_guy-m1-03.mp3`), la recette est donc le texte
  lui-même. `scripts/audio_elevenlabs.py --voix` génère ce qui manque, au caractère (≈ 40
  répliques × 80 caractères : quelques milliers de caractères, rien).
- **Le texte reste affiché** dans la boîte de dialogue (lisibilité, jeu en sourdine,
  tactile) ; la voix **s'ajoute**, elle ne remplace pas. Une réplique dont le fichier
  manque s'affiche sans voix — le filet, comme pour les bruitages.
- **Une seule voix à la fois** : une réplique coupe la précédente ; la radio et l'ambiance
  baissent pendant qu'on parle (_ducking_), puis remontent.
- **Le téléphone** : la voix vient « du combiné » (filtre passe-bande, un peu de grésil) ;
  le journal du matin est lu par le narrateur, en plus de la manchette.
- **Un test navigateur** prouve que chaque voix se décode ; un test Python que chaque
  réplique a un personnage connu et tient en une phrase ou deux.

## Architecture

### Principe

Comme dans `car-game` : **Python décide, JS calcule.** Tout ce qui tient dans une table
(catalogues, économie, paliers de recherche, carte, missions, magasins) vit en Python, est
testé par pytest et servi en **un seul paquet** `/api/definitions` (ETag, ~10 Ko gzip). Le
JS joue ce qu'il reçoit : physique, rendu, IA locale, entrées. Les sprites restent
dessinés en code ; l'audio est **mixte depuis le 12 sept. 2026** : de vrais échantillons
ElevenLabs versionnés dans `static/audio/` (catalogue et recettes dans `app/audio.py`),
et la synthèse de `son.js` comme filet quand un fichier manque.

### Côté Python (`app/`)

| Module | Contenu | Tests pytest |
|---|---|---|
| `vehicules.py` | 8 types : vitesse, accélération, virage, PV, places, prix, fréquence, couleurs, `sprite` | slugs uniques, bornes, une auto `police`, sprite existe (harnais Node) |
| `armes.py` | poings + 9 armes : dégâts, portée, cadence, chargeur, prix, `etoiles_usage`, `son` (le bruitage de l'arme, un slug de `audio.CATALOGUE`) | première = poings à 0 $, prix croissants, chaque `son` existe au catalogue audio |
| `economie.py` | `ARGENT_DEPART`, `amende(etoiles, casier)` = `min(argent, base[★] × (1 + 0,5 × casier))`, pots-de-vin `40 × ★ × (1 + 0,5 × casier)`, hôpital `clamp(10 %, 30, 500)`, propriétés, `FORTUNE_MAX`, ce que la bouffe rend (`*_pv` et `*_souffle`) et `CAFE` (durée + dépense du sprint) | jamais négatif, monotone, plafonné, retour sur investissement 10–60 min, coordonnées sur une porte, le café n'achète que de la **durée** et dure plus qu'un plein de souffle |
| `recherche.py` | paliers 0–5 (agents, autos, barrages, tirent, décroissance 15/25/40/60/90 s), délits → ★ (taxonomie ci-dessous), cônes (à pied 90° 9 tuiles jour / 6 nuit ; auto 60° 14/12 ; témoin 120° 6/4 ; alarme rayon 12) | contigus, monotones, palier 0 sans réponse |
| `carte.py` | **plan compact** du district (grille de blocs 8×6 : `h` habitations, `c` commerces, `g` gang, `p` parc, `o` place, `q` quai, `~` eau, majuscules = bâtiment spécial garanti, `<` et `^` = bloc **avalé** par son voisin) + `COLONNES`/`RANGEES`/`RUES_V`/`RUES_H` (aucune égale à sa voisine) ; `generer(plan, graine)` produit tuiles (`sol`, `voie` = champ de direction + lignes d'arrêt), intersections (avec leurs bras), portes, lampes, décor, zones, apparitions ; intérieurs en ASCII. **Trois sources d'irrégularité** : la trame, les superblocs (une rue qui n'existe pas → des T), et le découpage BSP en parcelles inégales (bâtiments en U ou en L, dents creuses, terrains vagues, stationnements). Un **stationnement est dessiné**, pas rayé au hasard : des rangées de cases de 1 × 2 tuiles (le gabarit exact de l'auto, glyphes `^ v < >` = où pointe le **nez**), des allées de manœuvre — toute rangée en touche une —, des rangées **dos à dos** dès qu'il y a douze tuiles de creux, des îlots de béton (`I`) et un lampadaire au bout des rangées. Un **filet** bouche les poches injoignables au lieu de livrer un îlot muré. Deux **couches peintes** par-dessus, qui ne touchent à aucune solidité : les **devantures** (bandeau, nom, vitrines, pancarte) et les **résidences** (étages de fenêtres, balcon, escalier de fer) — `_a_quoi_sert()` décide, par bâtiment, commerce ou logement. Les **intérieurs sont dessinés à la main** (`_piece`, un plan par pièce, l'espace = le plancher, meubles en glyphes) et **jugés à l'import** : une porte, un plancher d'un seul tenant, des points atteignables | rectangulaire, glyphes connus, **connexité forte des voies** (BFS), un seul îlot marchable **sur cinq graines**, portes ⇔ intérieurs, aucun gabarit sur une rue **qui existe**, un superbloc avale bien sa rue, **toute rangée de stationnement touche une allée** et toute case fait deux tuiles de creux, **juge d'asymétrie**, déterministe |
| `missions.py` | 5 missions v1 + 3 défis : donneur, prérequis, objectifs typés (aller, monter, livrer, tuer, survivre, course, chrono, retourner), récompense, dialogues | prérequis sans cycle, cibles sur tuile marchable, références existantes |
| `pietons.py` | 8 archétypes (couleurs = échanges de palette, `courage`, `temoin`, bourse, arme), les gangs et leur territoire, `REACTIONS` (recul, KO, fuite, saignement, pickpocket) ; les **métiers** qui ne naissent pas au hasard (la Brume, le marchand, le commis, l'agent, l'**homme-sandwich** et ses heures) | couleurs valides, courage de 0 à 1, un gang a un territoire qui existe, aucun membre de gang au hasard dans la rue, un métier a ses heures |
| `magasins.py` | inventaires armurerie / vêtements / garage ; les ambulants : ce qu'on y achète, les PV et le **souffle** rendus, l'`effet` qui dure (`EFFETS`), leurs `districts` (la cabane à fruits de mer ne quitte pas le port) et leur `reclame` ; `RECLAME` : l'homme-sandwich (portée, boniment, repos, coupon) ; `COMPTOIRS` : de quoi manger et boire par famille de commerce ; `DISTRIBUTRICES` : les trois sortes de machine, leurs articles au prix du comptoir et les familles de devanture devant lesquelles elles se posent (`sortes_devant`) | articles existants, tout ce qui se mange nourrit les jambes, un `effet` que le navigateur sait tenir, seul le café réveille, rien ne bat le hot-dog au dollar, un solliciteur n'est pas un mur |
| `audio.py` | catalogue des sons : slug, **prompt ElevenLabs** (la recette reste à côté du son), durée, boucle, volume, variantes ; `exporter()` ne déclare que les fichiers **présents** | bornes ElevenLabs, aucun orphelin, poids < 600 Ko, chaque effet garde son repli synthétisé |
| `interpretation.py` | comment une réplique se **dit** : le texte joué qu'ElevenLabs **v3** reçoit (balises d'émotion en anglais `[sighs]`, pauses « … »), une par voix, qui dit **les mêmes mots** que la boîte ; le temps mort ajouté à la fin (0,35 s), le niveau commun (−19 LUFS) et le pic — `scripts/audio_elevenlabs.py` les pose après la génération (`finir_voix`) | chaque voix a son jeu, mêmes mots que la boîte (attrape un slug décalé), balises connues de v3, chaque fichier finit sur un temps mort et au niveau, **la ligne de dialogue attend sa voix** (banc) |
| `journal.py` | _Le Clairon de la Baie_ : la manchette du matin, une règle par gravité — la première qui passe gagne, la dernière est le repli ; lue par le narrateur (M7) | règles ordonnées et repli ; `test_audio.py`, `test_histoire_js.py` |
| `manettes.py` | les **dispositions de manette** (Xbox/PlayStation, 8BitDo en Bluetooth, croix-sur-un-axe) et la numérotation DirectInput **mesurée** chez Martin ; le dessin de manette qui sert de preuve s'allume par numéro de bouton | `test_manettes.py` (un juge garde la mesure : la « corriger » effacerait le retour), `test_manette_js.py` |
| `musique.py` | la musique **écrite en notes** (notes, tempo, formes d'onde) — le **filet** depuis que les quinze morceaux sont des mp3 générés (`audio.MUSIQUES` en porte la recette) ; `scripts/musique_apercu.py` rend les notes en WAV pour l'oreille, gratuitement et hors ligne | `test_musique.py` (tonalité, longueur de boucle, collisions entre voix, et la couverture : aucun morceau sans musique générée) |
| `devantures.py` | 118 devantures et 142 noms d'enseigne **par district**, dix familles de couleurs, 54 graffitis signés chez leur gang, 74 immeubles à logements — une **couche peinte** (zéro solidité touchée) qui tire dans son propre dé | `test_devantures.py`, `test_devantures_js.py` (aucune enseigne hors de son district, aucun gang hors de chez lui, une porte visible partout) |
| `definitions.py` | `assembler()` → `Paquet(corps, etag, taille)` construit une fois au démarrage | déterministe, < 200 Ko |
| `scores.py` | copie de `car-game`, `valider()` : pseudo, `fortune`, `missions`, `proprietes`, `duree_s` ; tri fortune puis missions puis durée ; borne `fortune / duree_s` | copie des tests |
| `version.py` + `scripts/git-hooks/post-commit` | copie intégrale d'`online-4all-games` (numéro déduit du message de commit, garde `BANDINI_VERSION`) ; `version = "0.0.0"` au départ | `test_version.py` copié |
| `routes.py` | `/`, `/api/definitions` (ETag, 304), `/api/scores` GET/POST, `/sante`, 404 « Cul-de-sac » | page, ETag/304, scores, 413 |
| `bd.py` (M14) | SQLite sous `DONNEES_DIR` : ouverture, **WAL + `timeout`** (deux workers gunicorn), migrations numérotées, vidage quotidien | une migration s'applique une seule fois, deux workers écrivent sans se barrer, une base vide se crée toute seule |
| `comptes.py` (M14) | inscription, connexion, mot de passe haché, session signée, la partie au serveur, l'effacement du compte | un mot de passe n'est jamais gardé en clair, un pseudo pris est refusé, effacer efface vraiment, le jeu marche **sans** compte |

Réutiliser tels quels : `create_app` de `/Users/martingagne/dev/car-game/app/__init__.py`,
`config.py`, `run.py`, `Tableau` de `app/scores.py`, `scripts/verifier_dependances.py`,
`tests/harnais_js.py` et la fixture `serveur` (make_server port 0) de
`/Users/martingagne/dev/online-4all-games/tests/`.

### Côté JS (`static/js/`, 14 scripts classiques, ordre = dépendances, listés dans `templates/index.html`)

Résolution logique **480×270**, échelle entière 1–8 selon les pixels physiques,
`image-rendering: pixelated`. Boucle à pas fixe 60 Hz (accumulateur, `boucle()` de Loren).
Tout le hasard de jeu passe par `B.rng()` (mulberry32 réensemençable). Les menus figent la
simulation (`if (B.menu) return`). Sprites = **palette + grilles de caractères**, cuits une
fois en canevas hors écran (personnages 12×16, 4 directions × 3 poses ; véhicules 32×16,
3 caps dessinés → 8 par miroirs → 32 par rotation au cuisson).

| # | Fichier | Rôle |
|---|---|---|
| 1 | `base.js` | constantes, `B` (sac d'état), maths, RNG, `Rendu` (cible hors écran + tampon lumière demi-résolution + `lampe()`), sauvegarde versionnée avec repli des champs |
| 2 | `atlas.js` | cuisson des sprites/tuiles/police 5×7 depuis les grilles, validateur, miroirs, rotations, swaps de palette |
| 3 | `sprites.js` | `SPRITES`, `TUILES`, `POLICE_PIXEL`, gabarits de particules et décalques (données seulement) |
| 4 | `entree.js` | trois sacs d'entrées fusionnés par action (clavier `MAP_TOUCHES` AZERTY+QWERTY, manette `MAP_MANETTE` avec zone morte radiale et gâchettes analogiques, tactile `#croix` joystick suivi du pouce + boutons DOM 74/66/54/44 px), `contexte('pied'\|'vehicule'\|'menu')`, `empecherZoom()`, vibration |
| 5 | `son.js` | échantillons réels (fetch + `decodeAudioData`, variantes tirées au hasard, boucles allumables) **avec repli synthétisé** (`ton`, `bruit`), `SFX`, `Mus` séquenceur 3 voix (Loren) |
| 6 | `monde.js` | carte active depuis le paquet, `solide()` (masques : mur, eau, basse, **clôture**, **barbelé**), `ligneLibre()` (DDA), A\* à budget (2/image, cap 800 nœuds, file, repli ligne droite, **une clôture se paie 5 tuiles**), feux, cache de morceaux 256 px, caméra amortie avec avance, horloge jour-nuit, intérieurs (pile `B.exterieur`), mini-carte |
| 7 | `entites.js` | **enjamber une clôture** (capacité de tout le monde, au même prix), structure unique `{x, y, vx, vy, r, z, angle, face, etat, t, vie, sprite, swaps, …}`, **deux** index spatiaux 64 px (le décor ne bouge jamais : bâti une fois ; le reste rebâti à chaque image), cercle-vs-tuiles, piétons (flâne, figé, fuit, **témoin**, riposte, assommé, aveuglé, mort), gangs, bulle 300–520 px, armes de fortune semées, ramassages, particules, décalques, tri par y (les morts d'abord), **bulles de bande dessinée** (`bulle`/`taire`, un mot au-dessus de n'importe qui, dessinées en deuxième passe par-dessus tout le monde) |
| 8 | `combat.js` | arcs de mêlée (anticipation → actif → repos), coup fort, esquive, projectiles, fusil à plombs, fronde en cloche, extincteur, réactions, saignement, mort, sang (plafond 150 décalques), lâcher/ramasser, cycle d'armes, visée assistée |
| 9 | `vehicules.js` | physique arcade (accélération, friction, braquage selon vitesse, adhérence/dérive, frein à main), **chaîne de cercles** pour les collisions (tuiles, véhicules, piétons), sous-pas au-dessus de 3 px/image, monter/descendre/éjecter, trafic sur le champ de direction (regard devant, feux, choix de sortie **par la voie qui va dans son sens** — d'où le virage à gauche après le croisement —, ralentissement avant le coin, **déport dans la voie d'à côté** sur un boulevard pour dépasser ou contourner un piéton, déblocage par patience), dégâts/fumée/feu/explosion, rampes (`z`), alarmes, klaxon. Sprites : **un seul dessin** par char, 32 caps cuits par rotation |
| 10 | `police.js` | `signalerCrime()`, `voit()` (distance, cône, ligne de vue, budget 20 rayons/image), rapports de témoins, machine de recherche (`chaleur`, ★, `vu`, décroissance), apparition par palier, patrouille/poursuite (A\*)/arrestation, autos de poursuite, barrages, hélico, sergent ami, affiches, prison et hôpital |
| 11 | `missions.js` | cadre `TYPES_ETAPE`, téléphone, boulots (taxi avec pouce lisse, pizza, ambulance, courses, cascades, paquets), magasins, planque, propriétés (caisse par jour, plafond 3 jours), économie (`encaisser`, `payer`), pickpocket, journal du matin, bilan de session |
| 12 | `histoire.js` | les donneurs et leurs dialogues **dits à voix haute** (une voix par personnage, ducking, combiné au téléphone), posés **dehors** devant leur porte ou **dedans** à leur point en entrant chez eux, leur **bulle** quand ils ont une job pour toi, le téléphone qui appelle, la machine à objectifs des missions, les figurants posés en ville, les défis à panneaux, le GPS |
| 13 | `hud.js` | vie + endurance, ★, argent, arme + munitions, mini-carte 64×48 avec blips, texte de mission, GPS pointillé, toasts, menus canvas (pause, magasin, téléphone, prison, planque, options), boîte de dialogue, fondus, voiles DOM (titre, pseudo + tableau), `fetch` scores |
| 14 | `jeu.js` | machine d'états (`chargement \| titre \| jeu \| prison \| hopital \| fin`), `maj()`, `rendre()`, `boucle()`, **les portes** (`transiter()` : noircir sur l'ancienne scène, changer au noir, éclaircir sur la nouvelle — le jeu figé pendant, comme sous un menu), amorçage (`fetch` du paquet), `window.BANDINI` (surface de test et débogage : `B`, espaces de noms, `graine(n)`, `entree(a)`, `debug.cones`, `maj`, `rendre`, `stats`) |

Budget par image (téléphone milieu de gamme) : ≤ 6 blits de morceaux, ≤ 160 `drawImage`,
≤ 300 particules, ≤ 25 lampes, ≤ 200 entités actives ; compteurs `stats` plafonnés par
test ; dégradation automatique si > 20 ms pendant 2 s.

### Taxonomie des crimes (source : `recherche.DELITS`)

pickpocket +1 (témoin) · vol de véhicule stationné +1 (cône, témoin, alarme) · carjacking
+2 (la victime témoigne) · coup sur piéton +1 · mort de piéton +2 (+1 par mort en 30 s) ·
renverser +1 (+2 si mort) · arme sortie près d'un policier +1 · coup sur policier +2 · mort
de policier +3 · conduite dangereuse +1 · explosion +2 (alarme rayon 15) · pot-de-vin
refusé +1 · entrer armé en territoire de gang : 0 ★ mais la gang attaque.

### Les 5 missions et 3 défis de la v1

1. **Bienvenue en ville** (Ti-Guy) : marcher du terminus au garage, voler l'auto de la
   ruelle sans témoin, la ramener sans bosse → 100 $, clé de la planque.
2. **Le kiosque de Madame Thibodeau** : battre deux Cravates à mains nues, poursuivre le
   fuyard en moto, rapporter la caisse → 150 $, bâton, kiosque à −25 %.
3. **Le taxi de Marco** : trois courses ; le 3e client est un policier en civil : le
   laisser débarquer (témoin) ou l'emmener ailleurs → 200 $, contact du sergent.
4. **Le lunch du sergent** (Bouchard) : voler une auto-patrouille au poste, de nuit, sans
   être vu ; escorter l'auto de Ti-Guy (2★ sur lui) ; larguer au garage → 400 $, sergent ami.
5. **La Chef des Quais** (Josée) : nettoyer trois coins des Cravates, chef au dernier ; un
   témoin appelle, 3★ ; semer la police et rentrer → 800 $, Faubourg libéré, manchette, bar.

Défis : Le Grand Saut du viaduc (moto) · Tour du Faubourg (3 tours < 2:00) · Livraison sans
bosse (90 s, 1★ au départ, zéro dégât).

La suite — 109 missions, 34 personnages, les cinq districts — est en **M16**.

## Arborescence du dépôt `ybudoka/bandini`

```
run.py  config.py  pyproject.toml (name bandini, version posée par le crochet post-commit)  requirements.txt  uv.lock
.env.example  .gitignore  LICENSE (GPL-3)  README.md
.claude/settings.json (gardes Claude Code : la carte du dépôt, voir « Tests et CI »)
.vscode/  launch.json settings.json tasks.json
docs/plan.md (ce document : la vision, les jalons, et cette carte)
app/  __init__.py routes.py version.py scores.py definitions.py
      vehicules.py armes.py economie.py recherche.py carte.py missions.py magasins.py
      audio.py journal.py pietons.py manettes.py musique.py devantures.py interpretation.py
      bd.py comptes.py (M14 — jusque-la, le jeu n'a ni compte ni base de donnees)
templates/  base.html index.html (canvas + #tactile + voiles + data-url-*) 404.html
static/css/styles.css  static/img/favicon.svg  static/js/ (14 fichiers ci-dessus)
static/audio/  bruitages, radios, ambiances et voix (.mp3 ElevenLabs, recette dans app/audio.py)
tests/  conftest.py harnais_js.py banc.js (bac à sable Node : faux canvas/DOM/fetch/manette/audio,
        frame(n), touches, singe)  test_routes.py test_scores.py test_definitions.py
        test_vehicules.py test_armes.py test_armes_js.py test_brume_js.py test_economie.py test_recherche.py test_carte.py
        test_districts.py test_missions.py test_magasins.py test_pietons.py test_audio.py
        test_version.py test_moteur_js.py test_police_js.py test_histoire_js.py
        test_trace_js.py test_districts_js.py test_manettes.py test_manette_js.py test_son_js.py
        test_musique.py test_devantures.py test_devantures_js.py test_interieurs.py
        test_interieurs_js.py test_rampes.py test_carte_du_depot.py test_eau.py test_banlieue.py test_parole.py test_effacer.py test_stool.py test_bouclier.py test_trottoir.py test_dette.py test_paliers.py test_ombre.py test_reproductible.py test_poses_vehicules.py
        test_eau_son_js.py test_eau_basse_js.py test_amuseurs_js.py test_roue_js.py test_sieste_js.py
        test_reclame.py test_reclame_js.py test_argent_sale.py test_argent_sale_js.py test_distributrices.py test_distributrices_js.py test_contrebande.py test_contrebande_js.py test_barrieres.py test_barrieres_js.py test_ville_vit.py test_bagarre.py test_bagarre_js.py test_aqueduc.py test_aqueduc_js.py test_greve.py test_greve_js.py test_plage_js.py test_musique_commerce.py test_bateau.py test_betes_js.py test_foire.py test_abri_js.py test_terrains_vagues.py test_port.py test_quai_se_marche.py
        test_ouverture.py test_interpretation.py
        test_table_des_jalons.py test_navigateur.py test_ce_qui_casse.py test_reseau_local.py
scripts/  verifier_dependances.py verifier_carte_du_depot.py verifier_table_des_jalons.py
          verifier_ce_qui_casse.py
          audio_elevenlabs.py musique_apercu.py
          git-hooks/post-commit
deploy/  README.md deploy.sh installer.sh gunicorn.conf.py
         systemd/bandini-gestiondojo.service.example nginx/bandini-gestiondojo.conf.example caddy/README.md
.github/workflows/ci.yml
```

## Jalons (chacun jouable, testé, **déployé**)

| # | Jalon | Livré | Vérifié par |
|---|---|---|---|
| M0 | Squelette et mise en ligne | dépôt créé (`gh repo create ybudoka/bandini --public`), Flask + uv + crochet de version, `index.html` avec canvas/tactile/voiles, 13 fichiers avec espaces de noms, boucle, échelle entière, entrées (3 sources + analogique), `BANDINI`, `banc.js`, CI ; **installation serveur + DNS + Caddy + première release** (écran titre « Baie-des-Brumes, bientôt ») | CI verte ; `https://bandini.gestiondojo.ca/sante` |
| M1 | La ville | `carte.py` générateur + juges, paquet `/api/definitions`, atlas + validateur, tuiles, cache de morceaux, caméra, joueur qui marche (clavier, manette, tactile), jour-nuit + lampes, mini-carte | on parcourt tout le Faubourg au téléphone |
| M2 | Piétons et poings | **fait** : apparition, flâner/fuir/témoin/riposte, mêlée en trois temps, coup fort chargé, roulade, armes du catalogue (mêlée, tir, plombs, cloche, jet), projectiles, ramassage, armes improvisées qui cassent, sang plafonné, pickpocket, HUD arme et charge | bagarre dans la rue ; 13 tests de banc (arc devant/derrière, un coup = un dégât, poings assomment vs lame tue, budget, témoin) |
| M3 | Véhicules | **fait** : auto, taxi, moto, auto-patrouille ; physique, chaîne de cercles, monter/descendre/éjecter, trafic + feux, dégâts/explosion, alarmes, rampes, taxi au klaxon (pourboire selon la douceur), son moteur ; hôpital quand on meurt (avancé de M4). Radios livrées (bouton RADIO : station suivante, puis silence). Reste : projeter un piéton dans le trafic | voler, conduire, planter ; 11 tests de banc (vMax, marche arrière, dérive au frein à main, mur, **trafic 3000 images**, renversement, explosion, carjacking, feux, taxi, hôpital) |
| M4 | Police | **fait** : cônes + ligne de vue, témoins qui rapportent (acheter le silence), recherche 1–5★, patrouille/poursuite (A\*)/arrestation, autos de poursuite sur rails, tirs, prison (amende, pot-de-vin, casier), affiches, déguisement par char ; sergent ami branché en M6 ; **mode trace** des véhicules | se faire pincer ; 9 tests de banc (cône, poursuite + arrestation + prison, pot-de-vin, témoin → agent, silence acheté, décroissance hors de vue, autos + tirs, déguisement, affiches) + 3 de trace |
| M5 | Intérieurs et économie | **fait** : 10 intérieurs, magasins, planque (sauvegarde, coffre, garde-robe, char stationné), revente/réparation/peinture, propriétés, paquets cachés, journal du matin, bilan de session, options, envoi du score depuis la pause | acheter, vendre, sauvegarder, recharger ; 9 tests de banc |
| M6 | Missions et gang | **fait** : cadre + téléphone + 5 missions + 3 défis, Les Cravates et leur territoire, boîte de dialogue **avec la voix de chaque réplique** (une voix par personnage, ducking, voix « du combiné »), GPS ; reste pour M7 : contacts du marché noir, journal lu par le narrateur | finir les 5 missions, **les entendre** ; 7 tests de banc (donneurs, M1 de bout en bout, échec + reprise, appel, M2 combat + fuyard, M4/M5 récompenses, défis) + 1 navigateur (la voix se décode, la radio baisse) |
| M7 | Finition v1 | **fait** : 5★ (barrages, hélico), journal lu par le narrateur, marché noir, carte plein écran, sonnerie et rotor réels, sonde Playwright ; reste v2 : défi du jour à graine serveur, mesure sur vrai téléphone (Martin) | 60 i/s de nuit à 3★ sur téléphone ; 2 tests de banc police (hélico, barrage), 2 histoire (narrateur + marché noir, carte), 1 sonde navigateur |
| M8 | Les cinq districts | **fait** : quatre districts de plus autour de la baie (trame, gang, passants, densité et rythme propres), rues **noyées** et un pont, 5 lieux, 2 radios, carte plein écran à l'échelle de la ville, vieille sauvegarde rattrapée (le char de la planque revient à la rue la plus proche) | on roule du Faubourg à La Pointe sans chargement (test de banc : on le conduit) ; 15 juges de carte + 5 de banc ; connexité forte sur **toute** la ville, à quatre graines |
| — | Les transitions | fondu enchaîné dans le bon ordre pour entrer et sortir, jeu figé pendant, caméra posée au noir, son de porte au noir | entrer et sortir vingt fois sans un clignotement ; ne jamais se faire renverser pendant un écran noir |
| — | Les clôtures | **livré** : grillage et palissade de bois qu'on enjambe (48 images, sans frapper), barbelé infranchissable, et la police qui enjambe au même prix | couper par une cour et se faire suivre par l'agent ; ne jamais semer la police avec une clôture |
| — | Enfermé dans six commerces | la porte ne se laisse plus voler par un comptoir, et un juge Python interdit tout point d'action à moins de 1,6 tuile de la sortie | entrer et ressortir de chacune des seize pièces |
| — | Clôtures nord-sud couchées | **livré** : variante de clôture lue dans les voisines (est-ouest, nord-sud, coin, bout), pour les trois glyphes | une clôture verticale a l'air verticale ; un bout de course porte son poteau |
| — | La carte | joueur qui pulse (autre rythme et autre forme que l'objectif), flèche au bord pour une cible hors cadre, légende dérivée de la table des couleurs, une couleur déclarée par lieu | se trouver du premier coup d'œil sur la carte plein écran ; lire un blip sans l'avoir appris |
| — | Le souffle en surplus | **livré** : surplus au-dessus de 100, dépensé en premier, jamais régénéré, perdu en dormant ; ligne mince d'une autre couleur sur la barre, absente au volant | courir plus longtemps parce qu'on a mangé, et le voir sur la barre ; ne pas récupérer ce surplus en s'arrêtant |
| — | Les toits | **livré** : bord et parapet, un toit par bâtiment (faîte, versants, équipements), ombre au sol, couverture selon le genre | reconnaître deux bâtiments mitoyens à leurs toits ; une banlieue qui a l'air d'une banlieue vue d'en haut |
| — | Le fondu de l'hôpital et de la prison | **livré** : les quatre ellipses passent par `Jeu.transiter()`, exporté, avec un temps de **noir tenu** où le texte s'écrit ; `Hud.fondu` et les minuteries de `missions.js` disparaissent | se réveiller à l'hôpital sans avoir vu la téléportation, et ne pas se faire écraser pendant le noir |
| — | Des sirènes qu'on entend | **livré** : deux boucles (police, ambulance), volume selon la distance, une ambulance sur trois en course, et le klaxon qui devient la sirène au volant | reconnaître une ambulance d'une auto-patrouille sans la voir ; allumer sa sirène et sentir la rue changer |
| M9 | **P1** Le parc et les boulots | **les quatre sprites : livrés** (le catalogue ne ment plus, et un juge le tient) ; **le sport et le luxe : livrés** (rares, par quartier, la meilleure revente) ; restent le bateau ; **pizza et ambulance au klaxon : livrés** ; le remorquage attend la fourrière ; **fourrière : comptoir et saisie livrés** ; radio procédurale par véhicule ; la cour de la fourrière rangée en cases, sans tremplin ; `reservoir` : ce qui n'en a pas ne brûle ni n'explose | trois boulots finis d'affilée ; sortir son char de la fourrière ; trouver un luxe et le revendre ; démolir un vélo sans que la police arrive ; se faire remorquer pour avoir laissé son char en travers, jamais pour l'avoir mis dans une case |
| — | Rampes vraiment prenables | **livré** : élan, portée et freinage **calculés** depuis la fiche du char au lieu d'être écrits en tuiles ; la trajectoire rejouée par un test pour chaque rampe posée | réussir Le Grand Saut en moto et retomber sur la rue, pas dans un mur |
| — | Un saut qu'on ne voit pas | **livré** : impulsion et gravité réglées **avec** la réception, le vélo qui ne décolle plus, ombre à la taille du char qui s'éloigne et pâlit avec l'altitude (comme celle de l'hélico) | voir un char quitter le sol et retomber, et savoir de combien |
| — | **P2** L'endurance du Faubourg | trois vitesses (marche / course gratuite / sprint coûteux), policier aligné sur la course, renommage `joueur_course`, barre qui s'efface quand elle est pleine | traverser la ville sans gérer une barre ; ne plus semer un agent en marchant vite |
| — | Étoiles de recherche illisibles | **livré** : étoile **dessinée** (pas un caractère agrandi), jaune à elle, en haut au centre avec la ligne d'objectif qui descend, étoiles éteintes **creuses**, clignotement rouge gardé, ancre tactile réenregistrée | lire son niveau de recherche sans quitter la route des yeux |
| — | Clôture nord-sud trop large | **livré** : brin nord-sud réduit à son épaisseur (trait, chapeaux de poteaux, liseré d'ombre), poteau à la jointure des coins, juge retourné : le nord-sud est **plus mince**, pas une rotation | une clôture verticale qui a l'air debout, pas couchée |
| — | La nuit ne se vide pas | **livré** : rythmes de nuit abaissés, plafond appliqué **avant** le rythme, police soumise au rythme, chars stationnés redistribués | rouler dix secondes sans croiser personne à 3 h du matin |
| — | Arbres dans les sentiers | **livré** : une allée se **réserve** en se traçant (arbres, bancs et buissons réglés d'un coup), et le futur sentier de banlieue aussi | traverser un parc en ligne droite par son allée, sans contourner un tronc |
| — | **P2** Le décor se brise | fiches `DECORS` qui disent arrête/casse et sous quel poids, débris enjambables, lampe éteinte avec son poteau, délit et témoin, réindexation au bris seulement, remise à neuf au lendemain, plafond de débris | déraciner un arbre en camion et s'écraser dessus en berline ; voir le matin ce qu'on a cassé la nuit |
| — | **P2** Des sortes de gens | un corps par sorte (juge : plus rien sur `sprite: 'joueur'`), une routine par métier dans `majPieton`, plafond par sorte dans la bulle, quartier et heure | voir la police arrêter quelqu'un d'autre ; savoir devant qui ne pas sortir une arme |
| — | **P2** Les portes s'ouvrent | battant dessiné **par-dessus** la tuile (le sol est cuit dans le morceau), sortie visible, entrée qui remplace une part de l'oubli, portes triées par ce qu'elles valent, rythme matin/soir | voir quelqu'un sortir du dépanneur et y entrer, sans que le cache de morceaux bouge |
| — | **P2** Le carnet | page EN COURS (objectifs barrés, donneur, récompense), page JOURNAL (écrite par les événements déjà émis, plafonnée), page RÉPERTOIRE (`p.connus` seulement) | retrouver quoi faire en deux secondes après trois jours sans jouer ; aucun personnage non rencontré dans le répertoire |
| — | **P2** Une seule musique pour toute la ville | cinq ambiances de district (fondu + hystérésis aux frontières), thème du titre enregistré par-dessus la synthèse, musique de poursuite et de bagarre avec durée minimale et queue, échelle de priorité écrite une fois | entendre qu'on a changé de quartier ; entendre que ça tourne mal avant de le voir |
| — | **P2** Les véhicules vus de profil | trois poses par véhicule (profil miroité, dos, face) au lieu de 32 rotations cuites, pose choisie par la même règle que la face d'un passant, ancre posée sur la ligne de sol, ombre au sol **permanente** à l'empreinte du catalogue, pose couchée pour l'épave et le vélo plié, conducteur sorti du sprite du deux-roues | l'atlas du parc entier sous 0,5 Mo (6 Mo aujourd'hui), aucune pose manquante ni empruntée, un char au sol qui ne flotte pas d'un pixel, et le tri par y qui range le char avec les passants |
| — | **P3** Trottoir et traverses de deux tuiles | `TROTTOIR = 1` (trottoirs **et** traverses), rues rétrécies pour garder leurs voies, tout ce qui vivait sur le trottoir relogé, le littéral `2` de `monde.js` remplacé par `grille.trottoir`, juges de géométrie rejoués | une rue qui a l'air d'une rue ; aucun bouchon de piétons devant un commerce ni à une traverse |
| — | **P3** Pièces plus grandes que leur maison | **livré** : plancher de la pièce ≤ empreinte du bâtiment, à toutes les portes ; pièces **par tranche de taille** et la porte prend la plus grande qui tienne (sinon elle reste condamnée) ; parcelle d'un lieu garanti taillée à la mesure de sa pièce ; chaque famille de commerce ouvre au moins une porte | sortir d'un dépanneur sans avoir l'impression d'être sorti d'une cabane |
| — | **P3** L'eau n'est plus un mur | **livré** : masque de nageur (joueur et agents), souffle qui décide (8 points la tuile), noyade par `Missions.hopital`, char qui coule et qui est perdu, bateau qui flotte par sa fiche, police qui nage, juge du pont reformulé en **carrossable** | traverser le chenal de justesse ; ne jamais atteindre le large ; un char noyé ne revient pas |
| — | **P4** Ça travaille : chantiers et démolitions | `CHANTIERS` par parcelle avec une **phase** qui avance d'un cran tous les trois ou quatre jours (condamné, démolition, terrain rasé, dalle et grue, bâtiment neuf) ; pelle, grue et boule de démolition en décor **animé** (une articulation) ; marteau-piqueur, godet et **bip de recul** à la distance, muets la nuit | aucun chantier sur un lieu spécial, un commerce ou une porte de donneur ; à chaque phase, un seul îlot marchable et aucune poche murée ; une porte démolie quitte `portes` ; le cache de morceaux ne se vide qu'au changement de jour |
| — | **P4** Les zones conditionnelles | une fiche `carte.BARRIERES` (où, ce qu'elle arrête, la condition, le prix de forcer, la raison affichée) qui avale les trois barrières déjà écrites et les entraves de M12 ; huit barrières de départ, dont le pont fermé aux chars mais jamais aux jambes | aucune combinaison fermée n'enferme la planque ni un lieu de mission, le trafic ne s'empile pas devant une grille, et une zone fermée ne fabrique pas de piétons dedans |
| — | **P4** L'Île-aux-Corneilles | une île de 40 × 24 dans l'eau qui existe déjà, sans un pont : quai, chapelle (deuxième sauvegarde), usine à poisson, hangar de Sven, **pas de police** ; huit missions (arc I) et la dernière image de _Le dernier traversier_ | l'île ne touche aucune rive, aucune route ne la relie, les étoiles y descendent, chaque terre ferme reste un seul îlot marchable, et le paquet tient sous son plafond |
| — | **P4** Quatre activités de plus | paliers de boulot à récompense permanente (**livrés**), boulots patrouille et pompier volontaire, la liste du quai, les frénésies | un palier ne se donne qu'une fois et sa récompense existe vraiment ; aucun ne paie mieux à l'heure qu'une mission ; une frénésie ne touche jamais un intouchable |
| — | **P4** La dépanneuse lève les roues | lien **rigide** au lieu d'un câble, avant levé (collé, deux pixels plus haut, l'ombre restée au sol) et **dans l'axe** ; `plateau` en fiche : moto et vélo montent en entier, dessinés par-dessus, hors des tuiles et hors des chocs ; la remorqueuse refuse d'avancer là où sa charge ne passe pas | reconnaître une dépanneuse d'une auto qui tire une corde ; ramasser une moto sans qu'elle se traîne le nez par terre |
| — | **P4** Feux pour piétons | poteau à chaque bout de traverse (blanc/orange, lisible par la couleur), dégagement avant le vert des chars, et « sans feu, on traverse quand c'est libre » pour ne pas échouer la foule aux T | voir quand la foule va s'engager, et ne plus voir personne partir sur l'orange |
| — | **P4** Les terrains de banlieue | entrée qui touche la rue, une case sur trois (pas plus), sentier porte→rue qui ne traverse pas la piscine, grillage mitoyen, et le paquet qui reste sous ses bornes | traverser trois cours pour semer un agent ; reconnaître une maison habitée d'un coup d'œil |
| — | **P4** Les armes à feu | **livré** : `auto` (tenir, la cadence rythme, la dispersion s'ouvre et se referme), `bruit` (l'agent hors du cône **entend** et vient voir, sans étoile ; recherché, le coup dit où tu es), `feu_s` (le brasier, entité invisible faite de particules, qui mord passants, joueur et chars avec le lanceur pour auteur), portée bornée à la demi-vue, marché noir seul comptoir | choisir son arme selon la situation, pas selon son prix ; ne jamais gagner un 5★ en tirant hors du cône |
| M15 | **P4** La ville te parle | le repli du journal enseigne une chose par jour, animateur + pubs + bulletin sur les radios, banques de répliques par contexte, tirage sans les quatre dernières, la rumeur qui se tait devant une arme, la police à la radio, bruits de quartier, souffle du joueur | apprendre le klaxon sans l'avoir lu nulle part ; entendre sa propre nuit au bulletin ; sentir la rue se taire avant de voir l'étoile |
| M10 | **P4** L'argent sale | le shylock (dette, intérêts, hommes de main), guichets au camion, skimmers, assurance et fraude | rembourser 15 000 $ sans se faire tuer ; la fraude rapporte moins que le travail à l'heure |
| M12 | **P4** La ville vit | tramway sur rails, traversier à l'heure, tempête de neige avec charrue, entraves du jour (liste validée par Python), nuit de déneigement, feux clignotants la nuit, pointe directionnelle, crimes d'autrui, arrêts d'autobus, éboueurs, bêtes | traverser à La Pointe en traversier ; conduire dans la neige sans que le rythme tombe ; suivre un DÉTOUR qui mène de l'autre côté ; perdre son char une nuit de déneigement |
| M14 | **P4** Meta v2 | compte + SQLite (partie et classement au serveur, `localStorage` toujours le défaut), défi du jour à graine serveur, mode photo, coop locale | commencer au téléphone et finir à l'ordi ; le classement du jour tourne ; deux manettes sur un écran |
| M16 | **P4** Cent missions | neuf types d'objectifs de plus, `exige` / `ferme` / `donne` étendu, lieux nommés, dialogues hors paquet, téléphone qui trie ; 109 missions en 9 arcs, 34 personnages, 3 piétons de mission, un chien, 5 défis | finir un arc par district au téléphone ; aucune mission morte au singe ; les deux fins atteignables par le catalogue |
| — | **P2** Une ouverture et un générique | **l'ouverture : livrée** — jouée au premier JOUER (l'autobus arrive au terminus, le narrateur dit la prémisse, `ouverture` en mp3 **et** en notes), passable d'un bouton, rejouable du carnet, jamais rejouée sur une partie en cours ; le générique branché sur les deux fins de M13 (caméra sur la ville, chiffres de la partie, manchette du Clairon, `generique`, puis l'envoi du score) | commencer une partie et savoir qui on est sans avoir lu le plan ; passer l'ouverture d'un bouton, à la manette comme au doigt ; voir une fin, envoyer son score, et retrouver la ville après |
| M13 | **P4** Les deux fins | une mission par district (4 donneurs, 4 voix), Marco qui te vend, Dr Lachance donneur, _Le Boss_ et _Sacrer son camp_ | atteindre les deux fins ; chaque réplique se dit à voix haute |

Tailles relatives : M0 1, M1 3, M2 3, M3 4, M4 3, M5 2, M6 3, M7 2 (v1 = 21) ;
M8 4, M9 3, M10 3, M11 2, M12 4, M13 4, M14 4, M15 4, M16 8 (v2 = 36) ;
hors vague, parce qu'elles se paient quand on veut : les transitions d'entrée et de
sortie 1, le fondu de l'hôpital et de la prison 1, les clôtures 1, les toits 2, les armes à
feu 2, le carnet 2, l'eau 3.

Ce qui reste, **trié par priorité** (le détail et la règle de tri sont dans « La v2 ») :

- **P1, le jeu ment** — M9 (le catalogue promet quatre chars que rien ne dessine) · la rampe
  du _Grand Saut_, qu'on ne peut pas gagner.
- **P2, ça se sent à chaque partie** — les arbres dans les sentiers · le carnet · la ligne d'histoire
  (l'ouverture tout de suite, le générique avec M13).
- **P3, ça porte le reste** — le trottoir et les traverses · les pièces plus grandes que leur
  maison · l'eau qui n'est plus un mur.
- **P4, ça enrichit** — les feux pour piétons · les terrains de banlieue · les armes à feu ·
  M15 · M10 · M12 · M14 · M16 · M13.

## La v2 — huit vagues (plan du 13 sept. 2026)

Règle inchangée : **chaque vague reste jouable, testée, déployée**.

⚠️ **Le tri est un tri de PRIORITÉ, pas de taille.** Quatre niveaux, et ils répondent à une
seule question : qu'est-ce qui coûte le plus cher à ne pas faire ?

- **P1 — le jeu ment.** Quelque chose est promis et pas tenu : un catalogue qui annonce des
  chars que rien ne dessine, un défi affiché qu'on ne peut pas gagner. C'est ce qui coûte le
  plus cher, parce que ça se paie en confiance et qu'aucun ajout ne la rachète.
- **P2 — ça se sent à chaque partie**, et ça coûte une bouchée. Un défaut qu'on rencontre à
  chaque mort, à chaque parc, à chaque nouvelle partie — et dont le mécanisme existe déjà.
- **P3 — ça porte le reste.** Ce qui redessine la ville ou débloque d'autres fiches. À faire
  avant ce qui s'appuie dessus, sinon on ajuste deux fois.
- **P4 — ça enrichit**, du plus utile au moins.

À l'intérieur d'un niveau : le moins cher d'abord, le correctif avant l'ajout, et les
prérequis toujours devant.

⚠️ **Correctif ou ajout, et ça se voit.** Un **correctif** répare une promesse que le jeu
fait déjà et ne tient pas ; un **ajout** en fait une nouvelle. C'est la même coupure que les
préfixes de commit du dépôt, `fix:` et `feat:` — et c'est voulu : ce qui est écrit ici doit
se retrouver mot pour mot dans l'historique.

⚠️ **Les numéros sont des noms, pas un ordre.** M9 s'appelle M9 parce qu'on l'a nommée là,
et le dépôt entier y renvoie — renuméroter casserait tous les renvois pour rien. L'ordre de
travail, c'est celui du tableau ci-dessous, et les sections qui suivent sont dans cet
ordre-là.

| P | Genre | Ce qu'il y a à faire | Taille | Pourquoi là, et ce qu'il attend |
|---|---|---|---|---|
| **P2** | ajout | Des sortes de gens — le réservoir | 3 | ⚠️ **deux vagues livrées** (les trois de Martin, puis cinq des sept « qui viennent avec »). Reste le réservoir, où l'on pige par vagues — plus la **personne âgée** (attend les feux pour piétons) et le **pickpocket** (M12) |
| **P2** | **correctif** | Les véhicules vus **de profil**, comme les piétons | 5 | ⚠️ **avant tout véhicule de plus** — le tramway et le traversier de M12, le sprite du bateau en dette : chaque char dessiné avant la refonte se dessine deux fois. Ne touche **qu'au dessin** (la physique voit toujours un rectangle vu d'en haut), et jette les quatre toits de M9 |
| **P2** | ajout | La ligne d'histoire : une ouverture et un générique | 3 | ⚠️ **l'ouverture est livrée** (16 sept. 2026) — elle ne dépendait de rien ; le **générique**, lui, attend **M13** : il n'y a pas de fin à filmer avant |
| **P3** | **correctif** | Le trottoir **et les traverses** de deux tuiles | 2 | ⚠️ redessine la ville : tout ce qui touche à la géométrie passe après |
| **P4** | ajout | M15 La ville te parle | 4 | le narrateur, le journal et les voix existent ; ⚠️ contient un correctif (les passants se répètent) |
| **P4** | ajout | M10 L'argent sale | 3 | **M9** : les guichets se défoncent au camion |
| **P4** | ajout | Ça travaille : chantiers et démolitions | 3 | ⚠️ **la refonte des véhicules d'abord** (la pelle et la grue sont du décor animé tant qu'elle n'est pas faite) ; partage son mécanisme avec les **entraves de M12**, qui s'y branchent au lieu de vivre à part |
| **P4** | ajout | M12 La ville vit | 4 | tramway, traversier et neige touchent à la physique |
| **P4** | ajout | M14 Meta v2 | 4 | de l'**infrastructure** (serveur, BD, comptes, sessions, NIP) : un autre métier que le reste. ⚠️ Rien n'en dépend, et rien n'en doit dépendre : un compte est un **confort**, le jeu se joue serveur éteint |
| **P4** | ajout | Les zones conditionnelles | 3 | avant l'île et avant les entraves de M12 : c'est le mécanisme qu'elles partagent toutes les deux |
| **P4** | ajout | L'Île-aux-Corneilles | 3 | **les zones conditionnelles** d'abord ; l'eau est livrée, le traversier (M12) viendra après et l'île l'attend sans lui |
| **P4** | ajout | Quatre activités que le jeu n'a pas | 2 | ⚠️ la **refonte des véhicules** d'abord (les deux boulots neufs ne demandent aucun char de plus, mais la liste du quai fait regarder le parc de près) |
| **P4** | ajout | M16 Cent missions | 8 (4 × 2) | le **carnet** d'abord (c'est lui qui rend cent missions lisibles) ; ⚠️ les dialogues sortent du paquet ; M13 en est la dernière tranche |
| **P4** | ajout | M13 Les deux fins | 4 | **M8** pour les districts, et ça gagne à suivre **M10** : la dette de Rocco est le fil des deux fins. C'est la fin — elle se pose en dernier |

M8 porte tout le reste (les gangs, les fins, le traversier, la fourrière ont besoin de la
ville complète) ; il est livré. Rien n'oblige à suivre la liste à la lettre : à l'intérieur
d'un niveau de priorité, on prend ce dont on a envie. Mais **on ne descend pas d'un niveau
tant qu'il en reste au-dessus** — c'est tout ce que le tri veut dire.

Ce que la v2 **ne fait pas**, pour que le plan tienne : pas de multijoueur en ligne, pas
de 3D, pas d'histoire à plus de deux fins, pas de génération de sprites par IA. Le jeu
reste un GTA 1 québécois en pixels, joué au téléphone.

⚠️ **Un compte (M14) n'est pas du multijoueur.** Deux joueurs ne se voient jamais dans la
même ville ; le serveur ne fait que garder une partie et un classement. La ligne ci-dessus
tient : c'est une sauvegarde qui voyage, pas une partie partagée — et le jeu continue de
tourner entièrement dans le navigateur, compte ou pas.

### M8 — Les cinq districts (taille 4) — **livré le 13 sept. 2026**

_Ce que ça donne :_ la ville cesse d'être un quartier. **421 × 213 tuiles** au lieu de
157 × 112 (5,1 ×), quatre quartiers de plus autour d'une baie, chacun avec sa trame, son
gang, son bruit et une raison d'y aller. Le Faubourg n'a pas bougé d'une tuile.

- `carte.py` : **une seule grille de blocs** (20 × 12), un district par rectangle,
  assemblés par `_assembler()`. C'est ce qui garde la ville d'un seul tenant — les artères
  traversent les frontières, rien ne se charge en roulant. Un district ne fusionne **jamais**
  par-dessus sa frontière (sinon déplacer un quartier en casserait un autre) : le juge est
  dans l'assembleur.
- ⚠️ **La règle qui fait la géographie** : une rue dont _tous_ les blocs voisins sont de
  l'eau est **noyée** — elle n'est ni bâtie ni carrossable, et l'eau reste dessous. Une rue
  de rive (eau d'un bord, terre de l'autre) reste une rue : c'est le boulevard du bassin.
  Cette seule règle ferme la baie, arrête la rue du pourtour au bord de l'eau et coupe pour
  de bon le chenal de La Pointe. Et `PONTS` fait l'exception : **un** pont, tablier de
  planches, que le juge défait pour vérifier qu'il est bien le seul lien.
- Les trames se distinguent à l'œil, et un juge le mesure sur trois chiffres (rues au mètre
  carré, taux de fusion, largeur moyenne des colonnes) : Les Quais = blocs longs de trois
  blocs, hangars, quais ; Les Érables = grandes parcelles, maisons détachées sur gazon ;
  La Shop = des 2 × 2 partout, presque pas de rues, stationnements ; La Pointe = bois,
  sentiers de terre, quatre maisons et un phare.
- ⚠️ **Pas de vrai cul-de-sac.** Un croisement à un seul bras piège un char : il y entre et
  la seule sortie est la voie qui pointe sur lui. La banlieue a donc des rues qui s'arrêtent
  en **T** (déjà gérées : STOP à la tige) et des ruelles sans issue dans les îlots, pas des
  culs-de-sac routiers — et `test_les_croisements_sont_des_croisements` interdit le reste.
- `pietons.py` : Les Morues, Les Chevreuils, Les Boulonneux (les seuls hostiles sans qu'on
  sorte une arme), Les Skateux ; et quatre passants de quartier — débardeur, banlieusard,
  machiniste, promeneur de chien — que le champ `districts` **enferme chez eux**.
- `carte.zones()` : police, véhicules et piétons par district, plus un **rythme**
  (nuit, matin, soir) : La Shop tombe à 0,15 la nuit, les Quais montent à 1,4 le matin.
- 5 lieux de plus, un par district : dépanneur Chez Ti-Paul (caisse, journal), **Hôtel
  Bandini** (un deuxième lit, donc une deuxième sauvegarde — et la propriété v2 qui
  l'attendait existe enfin), cantine des Quais (hot-dog), usine Prévost, phare de La Pointe.
- `audio.py` : _10-4_ (auto-patrouille) et _Radio-Traversier_ (camion). **À générer et à
  écouter** : `uv run python scripts/audio_elevenlabs.py --refaire dix_quatre traversier`.
- **Le paquet, mesuré** : 319 Ko bruts, **33 Ko gzip** (prévu : 360 / 60), `generer()`
  94 ms **une fois au démarrage du serveur** — le paquet est construit à la création de
  l'app, pas par requête. Budget du test relevé à 400 Ko bruts (puis à **600** le 13 sept. : le brut n'est qu'un indicateur, voir « Dettes »), et un second juge tient le
  gzip sous 70 Ko : c'est lui qui voyage. La carte reste dans le paquet ; le déclencheur du
  découpage est toujours écrit d'avance (plus de 2 s entre « Jouer » et la ville sur le
  téléphone de Martin → `/api/carte`, ETag, districts chargés autour du joueur).
- **Rythme** : 0,29 ms par image de nuit à 5★ (0,26 avant M8). La ville a quintuplé, pas le
  coût de l'image : rien ne parcourt la carte par image.
- ⚠️ **Le chien de garde mordait un char sage.** Un feu rouge dure jusqu'à 480 images ;
  l'attente de boîte qui suit, jusqu'à 400. 480 + 110 = 600, exactement le seuil du chien —
  et le mode TRACE signalait une anomalie sur un char parfaitement poli. `immobileT` ne
  compte plus le temps d'une **attente légitime** (feu rouge, stop qui s'égrène, boîte
  encore prise), chacune bornée. L'anomalie garde en plus l'état d'**avant** le déblocage.
- **Une vieille sauvegarde** ne place plus rien dans un mur : l'empreinte du catalogue a
  changé, donc la position du joueur _et_ celle du char gardé devant la planque sont
  oubliées ; le char revient sur la rue la plus proche de la porte.

### Les transitions d'entrée et de sortie (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Retour de Martin :_ « il faut améliorer les transitions quand on entre et sort des endroits.
La transition n'est pas juste. »

⚠️ **Elle n'était pas juste parce qu'elle arrivait dans le mauvais ordre.** `Jeu.entrer()`
chargeait la pièce, téléportait le joueur, recentrait la caméra — **puis** appelait
`Hud.fondu(40)`. Or ce fondu va de transparent à noir puis à transparent : sa première moitié
noircissait donc sur la scène **déjà changée**. On voyait la pièce une image, l'écran
noircissait, il s'éclaircissait sur la même pièce. Ce n'est pas un fondu enchaîné, c'est un
clignotement — et l'œil le sait même quand on n'arrive pas à le nommer.

L'ordre juste : **noircir sur l'ancienne scène → changer au noir → éclaircir sur la
nouvelle**. C'est maintenant `Jeu.transiter(durée, faire)` : `B.transition` porte le fondu,
et `faire()` — tout le changement de scène, sans exception — ne s'exécute qu'**au noir**.
⚠️ _Ajouté le 13 sept. 2026 :_ cette fiche disait ici que « la prison et l'hôpital le font
depuis M4 ». **C'était faux**, et ça a coûté le correctif d'après : ils étaient sur `Hud.fondu`
et changeaient de scène à 80 % de noir — voir « Le fondu de l'hôpital et de la prison ».

Ce qui a été livré avec l'ordre :

- **Le jeu se fige pendant le fondu.** `maj()` ne fait plus avancer que la transition quand
  il y en a une, exactement comme un menu ouvert (`if (B.menu) return`). Avant, la simulation
  continuait : on pouvait sortir d'une pièce et se faire renverser par un char qu'on n'a pas
  vu venir, pendant un écran noir où l'on ne contrôle rien.
- **Des durées qui se sentent, et asymétriques** : entrer 26 + 20 images (0,77 s — on pousse
  une porte, on veut le sentir), sortir 15 + 11 (0,43 s — on veut retourner au jeu), l'étage
  20 + 16. Les 40 images d'avant, partagées en deux, étaient juste assez pour clignoter et
  pas assez pour lire.
- **La caméra ne saute plus.** `poserDansLaPorte()` la pose **au noir**, sur la cible exacte
  que `majCamera` viserait à la première image (position + avance de l'élan) : personne ne
  voit le saut, et l'amorti n'a rien à rattraper quand le jeu repart. Le juge mesure moins de
  2 px de déplacement à la première image jouable.
- **Le son au bon moment.** `Son.SFX.porte()` est dans `faire()` : la porte s'entend **au
  noir**, à l'image du changement. Le juge le vérifie en espionnant l'appel.
- **On ne repart pas d'un arrêt complet.** La face et la moitié d'un pas de marche restent
  dans le sens de la porte (`ELAN_DE_PORTE`) — ça se sent traversé, pas téléporté.
- ⚠️ **Le cas qui casse tout : passer une porte pendant qu'un autre fondu joue.** Comme la
  scène ne change qu'au noir, `sortir()` appelé avant le noir d'une entrée ne trouverait
  aucun intérieur, refuserait — et le joueur se réveillerait dedans sans l'avoir demandé.
  `finirTransition()` termine donc le fondu en cours (changement compris) avant d'en lancer un
  autre. Entrer puis sortir ramène **au pixel** devant la porte, fondu interrompu ou non.
- ⚠️ **Le noir doit avoir été DESSINÉ avant qu'on éclaircisse.** La boucle rattrape jusqu'à
  quatre images de simulation entre deux images dessinées : sans le drapeau `vu` que le HUD
  pose, la première image de la nouvelle scène pouvait se montrer à 94 % de noir — donc se
  montrer. C'est le seul endroit où le rendu parle à la simulation, et c'est pour ça.
- **Au banc** : `o.entrer(porte)`, `o.sortir()` et `o.fondu()` laissent jouer le fondu — un
  test qui lirait `B.interieur` juste après `Jeu.entrer()` lirait encore la rue. 3 juges
  neufs : la scène et l'alpha mesurés **à chaque image** (aucune ne montre la nouvelle avant
  le noir complet), le gel (ni `B.t`, ni l'heure, ni un passant, ni un char ne bougent), et la
  sortie **pendant** le fondu d'entrée.

### Les clôtures : grillage, bois ou barbelé (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Demande de Martin :_ « il faut des clôtures, mais si elles ne sont pas barbelées, qu'on
puisse passer par-dessus. » Puis, en cours de route : « ajoute aussi des clôtures de bois
pour de la variété. »

⚠️ **On passait par-dessus toutes les clôtures — sans même ralentir.** `f` était solide **3** :
le masque des véhicules la voyait, celui des piétons non (`MASQUE_PIETON = MUR | EAU`). Une
clôture n'arrêtait donc que les chars, et à pied elle n'existait pas. C'est ce qui la rendait
muette : on la traversait en courant comme si elle n'était pas là.

Les clôtures ont maintenant **leur solidité à elles**, et c'est la légende — elle seule — qui
dit laquelle fait quoi :

- **4, ça s'enjambe** : le **grillage** (`f`) et la **palissade de bois** (`w`). Une pose de
  48 images (0,8 s), pendant laquelle on ne frappe pas, on ne tire pas, on ne court pas — et
  on est une cible immobile, soulevée de 5 px, en haut d'une clôture. C'est ce prix-là qui
  fait d'une clôture un **choix** : couper par la cour, ou faire le tour.
- **5, ça ne se passe pas** : le **barbelé** (`X`). Ni à pied, ni en char. Il se met là où
  quelqu'un a payé pour que personne n'entre : les cours de gang (avec leur seule entrée de
  chars) et les cours de ferraille de La Shop.
- ⚠️ **Aucune n'est solide 1** : on **voit** à travers une clôture, donc un cône de police la
  traverse (`ligneLibre` ne s'arrête qu'au 1). Une clôture qui cache serait un autre
  mécanisme, avec ses propres juges.

⚠️ **Le piège, et c'était le plus gros : la police sait enjamber.** Le A\* des piétons
travaillait sur `MASQUE_PIETON` ; si le grillage n'avait été un coût que pour le joueur, la
première clôture venue serait devenue l'exploit qui gagne toutes les poursuites. Il y a donc
un **masque de chemin** à part (`MASQUE_A_PIED` : le barbelé bloque, le grillage non) et un
**coût** de 5 tuiles par clôture traversée — les deux chiffres, la durée et le coût, vivent
dans les mêmes données (`recherche.CLOTURES`) parce qu'ils disent la même chose. Un agent
lancé derrière le joueur franchit la même clôture, au même prix. ⚠️ Et devant une clôture
d'une seule tuile, il fait le **tour** — c'est moins cher, et il a raison : le juge se pose
donc au milieu d'un grillage de neuf tuiles.

**La palissade de bois** ne change aucune règle : c'est de la **variété**, et elle a sa place.
Une banlieue dont les cours arrière sont en grillage industriel n'a pas l'air d'une banlieue.
Elle ne se pose donc que dans **Les Érables** (188 tuiles), toujours avec une **barrière**, et
jamais devant une façade.

- ⚠️ **Trois pièges de génération, tous payés comptant** (mesures à l'appui) :
  - En clôturant aussi les quartiers de maisons du Faubourg, 274 tuiles de palissade tombaient
    au milieu du vieux quartier : le carré où l'on commence la partie devenait un labyrinthe
    de cours, et quatre juges de banc ne trouvaient plus une tuile libre autour du joueur.
  - Une barrière qui s'ouvre sur le mur du voisin fait de la cour une **poche** :
    `boucher_les_poches` la mure en silence — huit tuiles, dont le devant d'une porte, et un
    commerce se retrouvait sans entrée. La barrière s'ouvre donc sur du marchable, sinon la
    cour reste ouverte.
  - Les clôtures tirent dans **leur propre dé** (`des_cloture`), comme les devantures et les
    rampes : avec le dé commun, la trouée d'un terrain vague décalait toute la suite du hasard
    et la ville livrée changeait de gabarits.
- **Deux prédicats, et il fallait les deux** : `marchable` (ce qu'un piéton peut **fouler** —
  une clôture, non) et `franchissable` (ce qu'il peut **traverser**, en enjambant s'il le
  faut). La connexité et le bouchage des poches passent par le second : une cour derrière un
  grillage fait partie de la ville, une cour derrière du barbelé n'en fait pas partie. C'est
  ce qui fait du vieux juge « tout ce qui est marchable est relié » la garantie qu'**un
  barbelé ne referme jamais une poche**.
- **Juges (6 neufs)** : les trois clôtures disent ce qu'elles font (solidité, jamais foulables,
  aucune franchissable en char) ; la ville porte les trois **là où elles ont un sens** (le bois
  aux Érables seulement, du barbelé à La Shop, et la fourrière **garde son grillage** — « on le
  reprend par-dessus la clôture » est la moitié de ce qui la rend intéressante) ; un barbelé ne
  referme jamais une poche ; un grillage relie ses deux côtés et un barbelé coupe (sur une
  petite carte à la main) ; on ne traverse plus une clôture en courant (on l'enjambe, ça dure
  ce que les données disent, on ne frappe pas pendant, on retombe de l'autre côté) ; le barbelé
  ne se passe ni à pied ni en char ; et **une poursuite ne se gagne pas en enjambant**.

### On est enfermé dans six commerces (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Bug signalé par Martin :_ « chez Ti-Paul, il est impossible de sortir. »

⚠️ **C'était vrai, et ce n'était pas que chez Ti-Paul : six pièces étaient sans issue.** La
cause tenait en deux lignes de `combat.js` — **le comptoir passait avant la porte** — et en
deux rayons qui ne se parlaient pas : `pointSousLaMain()` attrape le point le plus proche
dans **1,6 tuile autour** de soi, quand `porteDevant()` n'accepte que la tuile collée à la
porte. Dans une pièce dont la porte est au mur du bas, il n'y a donc **qu'une seule tuile
d'où l'on peut sortir** : qu'un point d'action tombe à moins de 1,6 tuile de celle-là, et
ACTION sert le comptoir — toujours. Chez Ti-Paul, le point du journal était **sur** la tuile
de sortie (distance 0,00) ; Rosa, le kiosque, le phare et les deux boutiques génériques
étaient à 1,00 ou 1,41.

⚠️ Et il n'y avait **aucun repli** : `utiliserPoint()` rend `true` dès qu'il trouve un point
— même sans menu à ouvrir, il affiche « PLUS TARD » et rend `true`. Aucune deuxième pression
ne finissait par sortir. On quittait vers le titre, ou on restait.

**Deux corrections, et il fallait les deux** — l'une répare aujourd'hui, l'autre empêche
demain :

- **La porte ne se laisse plus voler** : sur la tuile de sortie, ACTION sort. Un comptoir se
  sert d'un pas de côté ; une porte, non.
- ⚠️ **Un juge Python sur `INTERIEURS`**, parce que c'est là que le mal se crée : aucun point
  d'action à moins de `RAYON_POINT` (1,6 tuile) de la tuile de sortie. Il rougissait **six
  fois** le jour où il a été écrit, et il lève maintenant **à l'import** (`_verifier_piece`),
  comme les autres règles de plan — une pièce fautive ne se charge plus.
- **Les six pièces se sont redessinées** : le comptoir recule d'une tuile, et le journal du
  dépanneur s'en va contre son mur, sur sa propre étagère.
- **Juges (3 neufs)** : aucun point à moins de 1,6 tuile de la sortie (une pièce à la fois,
  par `parametrize`) ; on ressort de **chaque** pièce de la ville en appuyant sur ACTION là où
  l'on arrive ; et un troisième qui **remet le piège à la main** — un point d'action posé pile
  sur la tuile de sortie — pour que la correction du jeu ait son propre juge, indépendant du
  dessin des pièces. Ce dernier rougit dès qu'on remet le comptoir avant la porte.

### Les clôtures nord-sud sont couchées (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Bug signalé par Martin :_ « les clôtures qui sont nord-sud ne sont pas dans le bon sens. »

Les trois clôtures venaient d'être livrées, et leurs trois peintres ne savaient dessiner
qu'**un seul sens** : est-ouest. Les lisses traversaient la tuile sur toute sa largeur, les
poteaux étaient à `x = 2` et `x = 13`, et les planches du bois se tenaient côte à côte en
travers. Une clôture qui descend du nord au sud était donc une **pile de panneaux vus de
face** — d'où l'impression, juste, qu'elle était couchée.

⚠️ **Et le remède était déjà écrit trois fois dans le dépôt.** `varianteDeTuile()` sait
demander à une tuile ce que ses voisines lui apprennent : les passages piétons, les cases de
stationnement et les rampes s'en servent. Les clôtures tombaient dans le repli et ne
recevaient qu'un bruit stable. Elles ont maintenant `varianteDeCloture()` — **un masque des
quatre côtés où la clôture continue** (1 nord, 2 est, 4 sud, 8 ouest).

- **Le dessin se fait en BRAS** : un brin du centre vers chaque côté où ça continue. Tout
  passe par `bloc`/`trait`, qui **échangent les deux axes** selon le sens — c'est tout le
  correctif, et c'est ce qui garantit qu'un nord-sud est un est-ouest tourné.
- **Un coin et un bout comptent** : un poteau se pose au centre dès que ce n'est pas une ligne
  droite. Sans lui, une clôture qui s'arrête a l'air coupée au couteau et la maille flotte au
  tournant.
- ⚠️ **Les trois partagent la géométrie** et ne diffèrent que par leur palette et ce qu'elles
  portent (la maille du grillage, les planches du bois, les trois fils et les épines du
  barbelé) — sinon on corrige un sens sur une clôture et on recommence à la prochaine. Et les
  trois se **continuent l'une l'autre** : un grillage qui se poursuit en barbelé est une seule
  ligne, parce qu'ici c'est la géométrie qui compte, pas la matière.
- ⚠️ **La hauteur des planches se tire sur un seul axe** : le même brin tourné doit donner le
  même dessin tourné, sinon le juge ne peut plus rien comparer.
- **Juges** : pour **chacun des trois glyphes**, le nord-sud n'est pas le même dessin que
  l'est-ouest, il en est le **tourné trait par trait**, un bout de course porte son poteau
  central, un coin aussi, et une ligne droite ne l'a pas. ⚠️ Le banc sait maintenant
  **enregistrer les `fillRect`** d'une cuisson (`ctx.traces`) : sans ça, on ne peut pas juger
  un dessin sous Node — le canevas du banc ne garde aucun pixel.

### La carte : se trouver, lire, et voir où va la mission (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Demande de Martin :_ « un icône clignotant pour savoir où on est, une légende, savoir où est
la mission en cours. »

Les trois manquaient pour trois raisons différentes, et une seule des trois était un ajout.

- **Se trouver.** Le joueur _était_ dessiné — un carré blanc de 2 px sur la mini-carte, de
  4 px sur la carte plein écran. ⚠️ **Ce n'était donc pas un manque, c'était une régression** :
  ce carré était lisible sur le Faubourg de 157 × 112, et la ville a quintuplé sans qu'il
  grossisse. Il **pulse** maintenant — un anneau blanc qui s'ouvre et se referme en 40 images
  — et le point, lui, reste dessiné **à chaque image** : on ne cache pas la seule chose qu'on
  cherche. Un repère qui clignote s'efface une image sur deux ; celui-là, jamais.
- **L'objectif bat, mais pas pareil.** ⚠️ Deux choses qui clignotent au même rythme se
  confondent : l'objectif garde son battement de 16 images et devient un **losange doré**,
  contre l'anneau blanc du joueur à 40. Deux rythmes, deux formes, deux couleurs.
- ⚠️ **Une cible hors cadre était un mensonge.** Le code la _bornait_ au bord de la
  mini-carte : un objectif à deux cents tuiles s'affichait collé au coin, exactement comme un
  objectif à trois tuiles. Hors cadre, c'est maintenant une **flèche** qui pointe — une
  direction est une information, une position inventée dit le contraire de la vérité. (Elle
  ne clignote pas : une direction n'est pas une alerte.)
- **Une légende** (c'était l'ajout), en deux rangées sous la ville, sur son propre bandeau —
  sans lui elle se lisait sur du vert, du bleu et du gris à la fois. ⚠️ **Et elle ne se
  recopie pas à la main** : elle se construit depuis la table des couleurs, dans l'ordre de la
  table (sinon elle se réordonne d'une ville à l'autre et on la relit à chaque partie).
- ⚠️ **Les couleurs sont des données.** `FAMILLES_DE_LIEU` (Python) déclare 8 familles —
  tes places, magasins, manger, services, soins, transport, travail, repères — et **chaque
  lieu déclare la sienne**. La preuve que c'était nécessaire était déjà là : `COULEUR_BLIP`
  (hud.js) connaissait dix lieux, la ville en compte seize, et les six autres — dépanneur,
  hôtel, cantine, usine, phare, fourrière — tombaient tous sur le même gris par défaut. M8 en
  avait ajouté cinq, M9 un sixième, et personne n'avait touché à la table.
- **La ville entière tient au-dessus de la légende** : centrée bêtement, ses dernières rangées
  finissaient sous le bandeau — et c'est La Pointe qu'on ne voyait plus.
- **Juges (4 neufs)** : chaque lieu déclare une famille qui existe, chaque famille a une
  couleur et un libellé, et **aucune famille déclarée n'est sans lieu** (une ligne de légende
  vide) ; les blips prennent leur couleur dans les données et la légende parle des mêmes
  familles qu'eux, dans l'ordre de la table ; le repère du joueur est présent à **toutes** les
  images avec un rayon qui varie, l'objectif clignote, et les deux formes diffèrent ; une
  cible hors cadre est une flèche, deux cibles dans deux directions différentes ne pointent
  jamais au même endroit, et une cible proche redevient un losange.
- ⚠️ Les juges lisent `Hud.marqueurs()` — ce que la dernière image a dessiné pour se repérer.
  C'est la seule façon de mesurer un clignotement sans regarder l'écran, et c'est le même
  patron que les ancres du test tactile.

### Le souffle en surplus (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Demande de Martin :_ « les choses qui donnent du souffle devraient donner un **bonus** de
souffle, parce que le souffle monte seul actuellement. Ce serait une petite ligne de couleur
différente qui se superposerait sur la ligne jaune du souffle. »

⚠️ **Et c'était mesurable.** Le sprint coûte 0,4 par image ; dès qu'on arrête de courir, le
souffle remonte de 0,4 × 0,6 = **0,24 par image** — une barre vide se remplit toute seule en
**sept secondes**. Or `nourrir()` faisait `min(100, endurance + souffle)`. Une poutine à 18 $
rendait donc 70 points… qu'on aurait eus gratuitement en s'arrêtant quatre secondes.

⚠️ Pire : le dépôt s'était déjà donné cette raison-là, et elle n'avait jamais tenu. Le commit
`1a03d16` dit « manger reprend le souffle », et `economie.py` expliquait : « sans ça, le seul
moyen de reprendre son souffle était d'arrêter de courir ». L'intention était juste ; la
régénération automatique la vidait de son sens le jour même.

**Le surplus est ce que la régénération ne peut pas donner.** Manger ne remplit plus la barre :
il ajoute par-dessus, au-delà des 100 (plafond **60**). Et cette part-là :

- **se dépense en premier** quand on sprinte — c'est la seule qui vaille ce qu'on l'a payée ;
- **ne revient jamais toute seule**, et c'est exactement ce qui redonne un sens au kiosque ;
- **se perd** en dormant, à l'hôpital et en prison, comme le reste de ce qui est passager.

**À l'écran** : une ligne cyan d'un pixel, **posée sur** la barre jaune plutôt qu'à côté — on
lit d'un coup d'œil « j'ai du souffle, et j'ai de l'avance en plus ».

- ⚠️ **Cette barre porte déjà deux autres messages**, et c'était le vrai risque. Sous café elle
  passe au **vert** et clignote la dernière seconde ; **au volant**, ce n'est plus le souffle
  du tout mais la carrosserie du char. Le surplus se pose donc **sur** la barre sans la
  remplacer, garde sa couleur que la base soit jaune ou verte, et **disparaît au volant** —
  sinon il se superposerait aux points de vie d'une auto, ce qui ne veut rien dire.
- ⚠️ **Le plafond est un réglage de poursuite, pas de confort.** Le joueur sprinte à 2,1, le
  policier court à 1,9 : chaque point de surplus est de l'avance qu'on ne peut pas lui
  reprendre. À 0,4 par image, 60 points valent **2,5 secondes** de sprint de plus — et **5**
  sous café, puisque le café divise la dépense par deux. Le budget (`surplus_secondes_max`)
  est déclaré à côté, et un juge refait le calcul dès qu'un des trois nombres bouge.
- **Juges (2 neufs)** : côté Python, le plein de surplus reste sous le budget de secondes,
  café compris, et une poutine en donne un vrai morceau ; côté banc, les quatre promesses d'un
  coup — manger à barre pleine monte le surplus et pas la base, jamais au-delà du plafond ; à
  l'arrêt il ne remonte pas d'un point quand la base, elle, remonte ; au sprint c'est lui qui
  part en premier (la base reste pleine) ; et une nuit l'efface.

### Les toits (**correctif**, taille 2) — **livré le 13 sept. 2026**

_Demande de Martin :_ « je veux que les toits des bâtiments soient plus réalistes. »

⚠️ **Le défaut était le même que celui des stationnements avant qu'on les dessine** : le toit
était peint **tuile par tuile**, chacune ignorant les autres. `TUILES.B/E/O` remplissait un
carré d'une couleur et semait des points tirés de `hash2(x, y)` — et comme la variante valait
0 pour tous les toits, **toutes les tuiles d'un toit étaient rigoureusement identiques**.
C'était une texture, pas un toit — et une texture uniforme ne peut pas être réaliste, parce
qu'un vrai toit vu d'en haut ne se lit ni par son grain ni par sa couleur.

Ce qui a été livré, dans l'ordre de ce qui se voit :

- **Un bord.** Parapet clair au ras du vide et sa ligne d'ombre à l'intérieur, sur chaque côté
  où le toit s'arrête. C'est le premier repère d'un toit : celui qui dit où finit le bâtiment.
- ⚠️ **Et c'est pour ça que deux voisins collés ne portent jamais la même couverture.** Le bord
  se lit dans le voisinage (« ma voisine n'est pas le même toit ») : entre deux toits
  identiques, il n'y a **aucun bord à trouver**. Le générateur corrige donc le tirage — sans
  en refaire un, parce qu'un dé de plus décalerait toute la ville (la leçon des devantures,
  des rampes et des clôtures).
- **Une identité par bâtiment.** `COUVERTURES` choisit la matière sur le **genre** :
  deux versants en banlieue, tôle et gravier à La Shop, ardoise dans la vieille ville. Avant,
  `des.choix(TOITS)` donnait l'ardoise à un entrepôt et le gravier goudronné à un bungalow.
- **Un grain qui varie.** Le bruit entre dans la variante (`GRAINS_DE_TOIT`), donc deux tuiles
  voisines ne sont plus le même dessin — un hangar de 26 tuiles ne se lit plus comme un damier.
- **Des pentes.** Le toit `P` a deux versants et une ligne de faîte, et le versant se
  **compte dans les voisines** (combien de tuiles du même toit au nord, combien au sud) : la
  faîte apparaît toute seule là où les deux pentes se rencontrent, sans qu'une tuile ait
  besoin de savoir qu'elle est au milieu, et **sans une donnée de plus dans le paquet**.
- **De quoi l'encombrer.** 172 équipements : ventilation, climatisation, cheminée, cage
  d'escalier, réservoir d'eau, antennes. ⚠️ **Ce n'est pas du décor** — `poser_decor` refuse
  les tuiles solides, et il a raison : le décor est une entité qu'on heurte. Ce qui est sur un
  toit n'est heurté par personne : c'est du dessin, il voyage dans le paquet et s'indexe par
  morceau comme les devantures et les graffitis.
- **Une ombre sur la rue.** Une bande sombre en dégradé au sud de chaque mur — elle donne
  d'un coup de la hauteur à toute la ville. ⚠️ Elle se peint **sous** les enseignes (une ombre
  par-dessus une pancarte donnerait une pancarte sale), et la boucle part **une rangée
  au-dessus du morceau** : l'ombre d'un mur assis sur la dernière rangée du morceau voisin
  appartient à celui-ci, et sans ça une bande de trottoir sur seize n'avait pas d'ombre.
- **Rien de tout ça ne coûte par image** : tout est peint **dans le morceau**, une fois. Le
  budget d'image (≤ 6 blits, ≤ 160 `drawImage`) n'y touche jamais.
- ⚠️ **Un beau toit donne envie d'y monter.** Rien n'est prévu pour : le joueur à pied n'a pas
  de `z`, le toit est solide 1, et une ville où l'on croit pouvoir grimper sans pouvoir le
  faire est plus frustrante qu'une ville aux toits plats. Les toits restent **muets pour le
  jeu** tant qu'on n'a pas d'escaliers — et c'est une décision, pas un oubli.
- **Juges (4 neufs)** : la couverture suit le genre (et la banlieue n'a que des versants, un
  entrepôt jamais d'ardoise) ; deux bâtiments collés posés l'un après l'autre ne portent pas la
  même couverture ; l'équipement ne se pose jamais au bord d'un toit, ni collé à un autre, ni
  ailleurs que sur du toit ; et au banc, une tuile de bord ne se peint pas comme un plein toit
  (les cuissons se comparent trait par trait) pendant que les versants se suivent du nord au
  sud avec **une seule** ligne de faîte. Le paquet pèse **368 Ko bruts / 41 Ko gzip**, sous ses
  bornes de 400 / 70.

### Le fondu de l'hôpital et de la prison (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Demande de Martin :_ « il faut corriger le fade out et in quand on va à l'hôpital ou qu'on
se fait enfermer. »

Les portes avaient reçu leur machine : `transiter([fermer, ouvrir], faire)` noircit sur la
scène qu'on quitte, change **au noir**, éclaircit sur la nouvelle, et fige le jeu pendant.
⚠️ **Quatre changements de scène étaient restés derrière** — l'hôpital, la prison, la
compagnie (« on reprend son souffle ») et le coucher (« le lendemain matin »). Ils faisaient
ceci :

```js
Hud.fondu(150, "REVEIL A L’HOPITAL — " + facture + " $");
setTimeoutJeu(60, function () {
  /* on téléporte le joueur */
});
```

⚠️ **Le vrai défaut n'était pas le fondu, c'étaient DEUX HORLOGES que rien ne liait.**
`Hud.fondu` comptait dans le **dessin** (`dessinerFondu`), `setTimeoutJeu` comptait dans la
**mise à jour** (`majMinuteries`). Rien n'attachait le 60 au 150 : changer l'un ne bougeait
pas l'autre, et le changement de scène pouvait glisser n'importe où sur la courbe sans
qu'aucun test ne bronche. Tout le reste en découlait :

- **Le décor changeait à 80 % de noir, pas au noir.** `dessinerFondu` montait l'alpha à
  `t / durée × 2` : à l'image 60 d'un fondu de 150, on était à **0,8**. On se regardait
  disparaître de la rue et réapparaître à l'hôpital à travers un voile transparent d'un
  cinquième.
- **Le texte s'écrivait sur une rue qu'on voyait encore** : entre 35 % et 75 % du fondu, donc
  avant le noir et fini avant la clarté. « RÉVEIL À L'HÔPITAL — 120 $ » se lisait par-dessus
  le trottoir où l'on venait de tomber.
- **Et le jeu n'était pas figé.** Pendant les deux secondes et demie, la ville continuait de
  tourner, la caméra restait sur l'ancien endroit, et le joueur gisait à 1 PV au milieu de la
  rue — un char pouvait lui repasser dessus pendant l'écran noir.

Ce qui a été livré, dans l'ordre de ce qui se voit :

- **Les quatre passent par `Jeu.transiter()`**, exporté pour l'occasion (il était interne à
  `jeu.js`, et `missions.js` en avait besoin). Une seule horloge, et la scène change **pile**
  à alpha 1.
- **Un fondu qui raconte quelque chose tient le noir.** La machine a gagné un troisième
  nombre — `[fermer, tenir, ouvrir]`. ⚠️ Une porte, on la passe : rien à tenir, et les trois
  fondus de porte gardent leurs deux nombres. Mais l'hôpital, la prison et la nuit font
  **passer du temps**, et ce temps se sent dans le noir : `[40, 70, 40]` pour l'hôpital et la
  prison, `[32, 56, 32]` pour une nuit, `[24, 42, 24]` pour la compagnie. Le noir tenu fait la
  moitié de la durée — plus court, on n'a pas fini de lire ; plus long, on attend.
- **Le texte ne se dessine que pendant `tenir`**, quand l'écran est vraiment plein. Il n'est
  plus une option du HUD : il appartient à la transition, comme sa durée.
- **La ville est figée**, comme pour une porte : le même `if (B.etat === 'jeu' && B.transition)`
  la couvre, sans une ligne de plus. C'est ce qui règle le joueur à 1 PV laissé dans la rue.
- ⚠️ **Un fondu par-dessus un autre n'en empile plus deux.** `transiter()` appelle lui-même
  `finirTransition()` : celui qui joue finit tout de suite — sa scène change, **une fois** —
  et le nouveau repart du clair. C'était déjà la règle des portes ; se faire arrêter pendant
  le fondu de l'hôpital la demandait aussi, et personne ne l'aurait vue en la codant quatre
  fois à la main.
- **Ce qui disparaît** : `Hud.fondu`, `dessinerFondu`, `B.fondu`, et — puisque plus personne ne
  s'en servait — `setTimeoutJeu`, ses minuteries et `majMinuteries`. **Il ne reste plus une
  seule deuxième horloge dans le jeu**, et c'était tout l'objet du correctif.
- ⚠️ **Un juge du trafic a cassé, et il avait raison de casser.** Celui du char hors voie
  (`tests/test_trace_js.py`) posait un char roulant à 32 px du joueur : il l'écrasait, et
  depuis que l'hôpital fige la ville, ses 120 images de surveillance ne surveillaient plus
  rien. Ce test juge le trafic, pas la santé du joueur — il le rend intouchable, et il dit
  pourquoi.
- **Juges (2 neufs)** : le premier mesure, image par image, l'alpha **à l'instant exact** où
  le joueur est téléporté (1,0 exigé) et l'alpha à **chaque** fois que le texte est écrit
  (`Atlas.texte` est espionné : le banc ne garde aucun pixel), pendant qu'un passant et un
  char servent de témoins que rien ne bouge dans le noir. Le second se fait arrêter au beau
  milieu du fondu de l'hôpital et vérifie qu'on se réveille bien à l'hôpital **puis** au poste,
  chacun une fois, sans un fondu resté ouvert. Quatre juges existants ont été rejoués à la
  nouvelle machine : la compagnie, l'hôpital, le coucher au lit de la planque et le souffle
  perdu la nuit lisent maintenant `B.transition`, et jouent le fondu avant de mesurer.

### Des sirènes qu'on entend (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Demande de Martin :_ « je veux des sirènes pour les ambulances et polices. »

⚠️ **Il n'y en avait qu'une, et presque jamais.** `Son.boucle('sirene', true, 0.5)`
s'allumait dans une seule branche : `v.conducteur === 'police'` avec au moins une étoile.
Trois conséquences, et Martin les a toutes entendues d'un coup :

- **L'ambulance n'a jamais fait entendre une sirène.** Sa fiche déclare pourtant
  `sirene: true` depuis M9 — comme `cercles` et `defonce`, c'est une promesse du catalogue
  que le navigateur ne lisait pas.
- **Au volant, aucune des deux.** On volait une auto-patrouille ou une ambulance, et on
  conduisait en silence. C'est la première chose qu'on essaie.
- **Et le volume était fixe** : allumée, elle sonnait pareil à dix pixels et à l'autre bout
  du district. Une sirène qu'on entend toujours ne veut plus rien dire.

Ce qui a été livré :

- **Deux sons, pas un.** `sirene_ambulance` rejoint le catalogue audio (ElevenLabs, 4 s en
  boucle, 16 Ko) : deux notes qui alternent lentement, là où celle de la police monte et
  descend sans s'arrêter. ⚠️ **Les confondre, c'est ne pas savoir qui arrive derrière soi**,
  et c'est toute la différence entre se ranger et se sauver.
- **Un mélangeur**, `majSirenes()` : une boucle par **sorte**, à chaque image, au volume du
  char le plus proche qui la fait hurler — `1 − d / 460 px`, et zéro au-delà. Les deux
  peuvent sonner en même temps ; ni l'une ni l'autre ne dépend d'une branche de l'IA.
- ⚠️ **Le mélangeur retient ce qu'il a demandé**, il ne lit pas l'état de `Son`. Un mp3
  absent — ou un navigateur qui n'a pas encore reçu de geste — laisse `boucleActive` à faux
  **pour toujours** : s'y fier, c'est redemander la même boucle soixante fois par seconde
  sans jamais s'en apercevoir. C'est la leçon du son retenu, appliquée avant de se la reprendre.
- **Une ambulance sur trois qui naît dans le trafic est en course**, sirène allumée : on
  l'entend traverser. Les deux autres rentrent au garage — une ville où **toutes** les
  ambulances hurlent n'est pas une ville, c'est une alarme.
- **Au volant d'un char à sirène, le bouton du klaxon est celui de la sirène**, et
  l'étiquette du bouton tactile passe de KLAXON à SIRÈNE. ⚠️ Le klaxon d'une auto-patrouille
  n'a jamais servi à rien, et le boulot se prendra **au même bouton** : dans une ambulance,
  on répond à l'appel et on part la sirène allumée, d'un seul geste. Dans une auto, le bouton
  reste le klaxon — un juge le vérifie, pour que le métier du bouton ne change pas pour tout
  le monde.
- ⚠️ **Ce qui n'a pas été jugé, et il faut le dire** : _le son lui-même_. Le juge du
  navigateur prouve que `sirene_ambulance-1.mp3` se **décode** ; personne ici n'a d'oreilles.
  Si elle ne sonne pas comme une ambulance, c'est `--refaire sirene_ambulance`.
- **Juge (1 neuf)** : deux boucles distinctes pour une ambulance et une auto-patrouille ; le
  volume tombe à zéro à 520 px et revient en se rapprochant ; éteindre la sirène la fait
  taire ; le bouton l'allume et l'éteint au volant, avec la bonne étiquette ; et dans une
  auto le même bouton klaxonne toujours.

### M9 — Le parc automobile et les boulots (**ajout**, taille 3)

_Ce que ça donne :_ autre chose à conduire, et de quoi gagner sa vie autrement.

⚠️ **Aux deux tiers le 13 sept. 2026, et il faut être précis sur ce qui manque.**
Le **Python est commité** (`7a4d26e` pour le catalogue, les boulots, les stations ; `e49603a`
pour le lot de la fourrière) : les fiches, l'économie, la carte et leurs juges existent.

**Livré le 13 sept. 2026** — les quatre chars existent, et un vélo ne saute plus (les deux
fiches ci-dessous). **Reste à faire**, et c'est celui qui se joue :

- « **mal garé** » ne veut encore rien dire : rien ne part au lot tout seul ;
- la **radio procédurale** est dans le paquet mais `Son.Radio` ne sait pas qu'une station
  peut venir de `musiques` plutôt que d'un mp3 — le bouton RADIO du camion ne fait rien ;
- et la remorqueuse **traîne** au lieu de **lever** — elle a une corde, pas une fourche (fiche
  ci-dessous, P4).

- `vehicules.py` : les quatre chars **existent, roulent, défoncent, soignent et remorquent**
  (fiches livrées plus bas) — plus une seule ligne de fiche que le navigateur ignore.
  Le **bateau** vient en dernier : il demande une physique à part et des tuiles d'eau
  carrossables — s'il coûte plus qu'il ne donne, il tombe en v3, et le traversier de M12
  suffit pour l'eau.
- Boulots au klaxon, sur le patron du taxi : **ambulance** (un blessé quelque part, chrono,
  le sortir vivant), **pizza** (trois livraisons, la pizza refroidit — le pourboire fond),
  **remorquage** (la fourrière paie pour les épaves).
- **Fourrière** : un char mal garé, ou saisi à l'arrestation, part au lot ; on le rachète
  au comptoir, ou on le reprend par-dessus la clôture (1★, et les gars du lot ripostent).
  - ⚠️ **« Mal garé » veut dire quelque chose** — **livré le 13 sept. 2026**. La règle était
    promise par la fourrière et n'existait nulle part. Depuis que les stationnements ont de
    vraies **cases** (`^ v < >`), elle tombe toute seule et se teste : est mal garé un char
    **laissé hors d'une case ET qui gêne** — la chaussée (où personne ne s'arrête), un
    passage piéton (où les gens traversent), le devant d'une porte (où les gens sortent).
    ⚠️ On regarde **toutes les tuiles que le char couvre**, pas son centre : un autobus de
    48 px en travers d'un passage a son centre sur le trottoir et bloque quand même. Un char
    dans sa case, rangé sur une ruelle ou sur du stationnement ne se fait **jamais**
    remorquer — même mal aligné, même depuis trois jours. ⚠️ Et **jamais le trafic** : seuls
    les chars que le joueur a **laissés** (`v.laisse`, posé en descendant) sont guettés —
    remorquer le trafic viderait les rues sans que personne comprenne pourquoi. ⚠️ Et
    **jamais celui de la planque** : c'est la sauvegarde de Martin. La remorqueuse passe
    après `FOURRIERE.remorquage_s` (45 s) et **prévient** dès la première seconde — sans
    avertissement, un char qui disparaît pendant qu'on fait une course passe pour un bogue,
    pas pour une règle. **Juges (2 neufs)** : les quatre cas de la règle (chaussée et passage
    oui, case et ruelle non), le trafic jamais touché, le chrono à trois secondes près, et le
    char de la planque intact ; côté Python, le délai est borné et le rachat minimum reste
    **au-dessus d'une course de taxi** — sinon se faire remorquer ne serait pas une punition.
  - ⚠️ **Le lot de la fourrière se gare comme les autres** (**correctif**). Sa cour est aujourd'hui un
    rectangle de `p` avec des places calculées à la main — alors que `_stationnement()`
    sait maintenant poser des rangées de cases, des allées et un îlot de béton. La cour doit
    passer par lui : des chars saisis rangés de travers dans un lot municipal, c'est
    exactement ce qu'on vient de corriger partout ailleurs, et les `places` du paquet se
    lisent alors dans les cases plutôt que dans une grille inventée.
  - ⚠️ **Mais pas de tremplin dans la cour.** `_stationnement()` finit par poser un
    `_tremplin_de_stationnement` dans une allée — dans la fourrière, ce serait une sortie
    par-dessus la clôture sans payer, et toute l'idée du lot tombe. La cour demande les
    cases **sans** le tremplin.
- **Radio procédurale** : `Son.Mus` (le séquenceur trois voix, déjà là) génère une station
  par véhicule à partir d'une graine — le camion a sa toune, l'autobus n'a que son moteur.
- **Juges** : chaque char a son sprite (harnais Node) ; la remorqueuse n'en traîne qu'un à
  la fois ; l'ambulance ne ressuscite personne ; la fourrière ne peut **jamais** manger le
  char de la planque (c'est la sauvegarde de Martin) ; le sport reste **sous** la moto et
  ne dépasse l'auto-patrouille que d'un cheveu ; le luxe est la plus grosse revente et la
  plus basse fréquence du parc ; aucun des deux ne naît dans un district qui ne les veut
  pas.

#### Le remorquage, et reprendre son char par-dessus la clôture (taille 2) — **livré le 13 sept. 2026**

La fourrière avait son comptoir et sa saisie ; il lui manquait ses **deux portes de sortie**
et le boulot qui la remplit.

- **Le remorquage** est le seul boulot dont ce qu'on ramasse n'est pas une personne mais ce
  qu'on a **au crochet**. ⚠️ Le bouton du klaxon accroche d'abord (`basculerCrochet`) puis
  appelle le boulot : **une seule pression** attelle l'épave et prend le contrat. Il n'y a
  pas deux gestes à apprendre, et c'est ce qu'annonçait déjà la fiche du crochet.
- ⚠️ **La fourrière ne paie que les ÉPAVES.** Traîner une berline saine au lot, ce n'est pas
  du remorquage, c'est du vol — et le refus **se dit**, sinon le bouton a l'air cassé.
- ⚠️ **On livre DANS LA COUR**, pas à 44 px d'un point comme les autres boulots : la grille
  fait quatre tuiles et une remorqueuse de 36 px avec son épave au bout ne s'arrête pas au
  pixel près dessus. L'épave part à la ferraille — le lot la prend, il ne la range pas.
- **Reprendre son char par-dessus la clôture** est l'autre moitié de la fourrière, et elle ne
  demande **aucun code de géométrie** : le grillage s'enjambe à pied et arrête les chars, il
  n'y a qu'une grille, donc sortir un char saisi de la cour suffit à tout déclencher. C'est
  `_fourriere()` qui l'avait prévu en Python ; le navigateur n'avait qu'à regarder.
- ⚠️ **Un PLANCHER d'étoiles, pas de la chaleur.** Un délit de gravité 1 pose 35 points sur
  les 100 d'une étoile : il aurait fallu voler trois fois pour que quiconque se déplace. Or
  le lot **appelle** — ce n'est pas une ambiance qui chauffe, c'est un signalement.
  `Police.etoilesAuMoins()` est la différence entre « quelqu'un a vu » et « quelqu'un a
  appelé », et elle resservira.
- **Les gars du lot ripostent** : un archétype `gardien` (batte et courage 1, ⚠️ **pas** de
  pistolet — ils ripostent, ils n'abattent pas), `frequence: 0` donc jamais dans la rue, deux
  à la grille. ⚠️ Ils se lancent **après** `Entites.alerter()` : celui-ci repasse sur tout le
  monde autour et remplace l'état de qui n'est ni en fuite ni témoin — il effaçait leur
  riposte à l'image même où on la posait.
- ⚠️ **`aToi` : un char payé au guichet n'est plus un vol.** Racheter le sien puis monter
  dedans signalait un `vol_vehicule` — et le comptoir ne servait alors plus à rien : autant
  sauter la clôture. C'est le genre de trou qui ne se voit qu'en jouant les deux chemins
  l'un après l'autre, ce que fait le juge.
- ⚠️ **Et `garnirLaFourriere` est idempotent** : `commencer()` garnit la cour, un
  rechargement la garnit encore — deux fois les gardiens, c'est quatre gars à la grille, et
  deux fois les chars, c'est un char par-dessus l'autre.
- **Ce qui reste** : « mal garé » (le remorquage automatique) et la radio du camion.
- **Juges (2 neufs, 2 Python)** : une berline saine au crochet ne lance rien et le dit, une
  épave prend le contrat en une pression, décrocher en route le fait tomber, et la livraison
  dans la cour paie base + distance ; sortir un char saisi signale `fourriere`, donne son
  étoile, vide sa ligne du lot, fait **glisser les rangs** des autres (sinon le comptoir
  libère le mauvais char), et met les deux gardiens sur toi — pendant que le même trajet,
  **racheté**, ne coûte rien. Côté Python : le délit `fourriere` est bruyant et vaut
  exactement `FOURRIERE.etoiles_vol` (deux tables, une seule vérité), et le gardien a un
  métier, du courage et une batte.

#### La fourrière : on te prend ton char, tu le rachètes (taille 2) — **livré le 13 sept. 2026**

⚠️ **La fourrière existait en Python depuis M9** — une cour clôturée avec sa guérite et sa
grille, 40 cases de stationnement, un intérieur, `economie.FOURRIERE` et son juge
d'équilibrage — et **le navigateur n'en savait rien**. Le comptoir « LE LOT » avait un
libellé et **aucun menu** (il était même sur la liste des comptoirs en chantier), et rien n'y
amenait jamais un char. Une cour entière dessinée pour rien.

- **On te prend le char que tu CONDUISAIS.** ⚠️ Pas celui où tu es : la police te **sort** du
  char avant de t'embarquer, donc `j.dansVehicule` est déjà nul à l'arrestation. Sans un
  souvenir du dernier char conduit (`j.dernierVehicule`, posé au montage), on n'aurait
  **jamais rien saisi** — et le bogue aurait eu l'air d'un oubli de règle plutôt que d'une
  question d'ordre.
- ⚠️ **Jamais celui de la planque.** C'est la sauvegarde de Martin : un char qui disparaît de
  devant chez soi pendant qu'on dort n'est pas une règle de jeu, c'est une perte.
- **Le lot garde `places` chars, et c'est le plus VIEUX qui part** quand il déborde — d'où un
  **tableau** dans la sauvegarde, pas un objet : il y a un ordre, pas un sac.
- **Ils attendent dans la cour**, sur les cases du lot, posés au démarrage comme le char de la
  planque l'est devant sa porte. ⚠️ `Monde.carte` ne portait pas `fourriere` : la cour était
  dans le paquet et le navigateur ne la lisait pas — encore.
- **Le comptoir les liste et les revend**, du plus récent au plus vieux. ⚠️ Un char racheté
  **n'est plus volé** : on vient d'en payer la sortie devant un guichet municipal, avec son
  numéro au registre. Et un lot vide **le dit** au lieu de se taire.
- ⚠️ **LA règle, et elle est économique** : racheter doit coûter **plus cher que revendre** le
  même char au garage. Sinon on se fait saisir un char exprès pour le racheter moins cher
  qu'il ne se revend, et la fourrière devient une machine à argent. Le juge la vérifie sur
  **tout** le catalogue, pas sur un exemple.
- ⚠️ **Une vieille partie n'a pas le tableau.** Un tableau ne passe pas par la fusion des
  objets de `completer()` : une sauvegarde d'avant la fourrière arriverait avec `undefined`,
  et le comptoir planterait au premier clic.
- **Ce qui reste** (fiche à part) : « mal garé » qui remorque tout seul, reprendre son char
  **par-dessus la clôture** (1★, les gardiens ripostent), et le **boulot de remorquage** — il
  attendait la fourrière, il l'a maintenant.
- **Juges (1 neuf, 1 exemption levée)** : l'arrestation saisit le dernier char conduit alors
  qu'on est **dehors**, le lot déborde par le plus vieux, le comptoir vend et encaisse le bon
  prix, un lot vide le dit, les chars saisis se posent **dans la cour**, et le rachat est plus
  cher que la revente **pour chaque char du catalogue**. ⚠️ Et `fourriere` sort de la liste
  des comptoirs en chantier de `test_interieurs_js` — cette liste est pénible à garder
  **exprès** : un comptoir dessiné sans menu doit coûter quelque chose.

#### Les boulots au klaxon : la pizza et l'ambulance (taille 2) — **livré le 13 sept. 2026**

⚠️ **`Missions.taxi` était le seul boulot du jeu.** Les trois autres vivaient dans
`economie.BOULOTS` — fiches complètes, juge d'équilibrage Python, exportées dans le paquet —
et le klaxon d'une moto ne faisait **rien**. Encore des fiches que le navigateur ne lisait
pas, comme `cercles`, `defonce` et `soigne` avant elles.

- **Une machine pour les quatre, pas quatre machines.** À quatre boulots, on aurait recopié
  quatre fois « va là, reviens ici, encaisse » avec quatre façons de se tromper. Ce qui
  **diffère** tient dans une table de dix lignes (`SORTES` : ce qu'on va chercher, où l'on
  va, ce qu'on affiche) ; tout le reste est commun. ⚠️ Et les **nombres** ne sont pas là non
  plus : ils viennent de `economie.BOULOTS`, où un juge Python les compare entre eux.
- **La pizza** a ce que le taxi n'a pas : **trois livraisons de suite**, et une prime qui
  **fond toute seule** (50 s). Pas de ramassage — on part avec les boîtes, et la seule
  pression du boulot est que ça refroidit. ⚠️ **La distance se paie à chaque étape** : sinon
  trois livraisons rapporteraient trois fois le premier trajet.
- **L'ambulance** va **chercher** quelqu'un. ⚠️ Le blessé est **à terre**, pas debout à héler
  — c'est ce qui le distingue d'un client de taxi à douze pixels. Et **il ne se relève pas** :
  un assommé se remet debout au bout de `ko_images` et s'enfuit, un blessé attend. Le seul
  chrono qui compte est celui du boulot, et **la prime EST sa vie** : passé les 100 s, il ne
  reste que la base. ⚠️ Sa destination n'est pas tirée au hasard comme celle du taxi : un
  blessé va **à l'hôpital**.
- ⚠️ **Un compteur par sorte**, et c'est ce qui sauve une mission de M6 : le défi « trois
  courses » compte des courses de **taxi**, et une pizza livrée n'en est pas une. Un compteur
  unique aurait laissé gagner le défi en livrant des pizzas, sans qu'aucun test ne bronche.
- **Le HUD dit lequel** : la ligne au volant affichait « TAXI : … » en dur. À quatre boulots,
  « TAXI » en tête d'une livraison de pizza ne veut plus rien dire — elle prend le nom de la
  fiche.
- **Le remorquage reste dehors**, et c'est voulu : il a besoin de la **fourrière** (où
  déposer l'épave, et qui paie). `SORTES` ne le déclare pas, donc le klaxon d'une remorqueuse
  ne promet rien — il **accroche**, ce qui est déjà son geste.
- **Juges (2 neufs)** : la pizza part sans ramassage, se livre **trois** fois, paie plus
  chaude que froide et jamais moins que la base ; l'ambulance va chercher un blessé **à
  terre** à moins de 30 % de vie, l'emmène **à l'hôpital** (pas au hasard), donne la prime
  pleine à temps et la base seule trop tard ; et dans les deux cas le compteur du **taxi**
  reste à zéro. Le juge du taxi, lui, a été rejoué à la nouvelle machine.
- ⚠️ **Corrigé le 13 sept. 2026, dans l'heure** (retour de Martin : « on ne devrait pas avoir
  de nouveaux contrats quand on arrête la sirène ; et quand un contrat est en cours, on ne
  peut pas en ravoir un autre »). Le bouton du klaxon fait **deux** choses dans une
  ambulance : il bascule la sirène **et** il prend l'appel. Le premier geste est le bon ; le
  second l'était aussi, mais **dans les deux sens** — éteindre sa sirène en sortant de
  l'hôpital rappelait aussitôt une ambulance, et on repartait sans l'avoir demandé. Un appel
  ne se prend plus que **quand on allume** : le geste inverse veut dire « j'ai fini ». Et le
  refus d'un deuxième contrat, qui était muet, **se dit** maintenant sur un char à sirène —
  le bouton vient d'allumer la sirène, il a donc l'air d'avoir fait quelque chose, et un
  refus silencieux passerait pour une panne. ⚠️ Dans un taxi, on se tait : le klaxon y sert à
  la circulation, et le répéter à chaque coup serait du harcèlement. **Juge (1 neuf)** : les
  trois états du bouton — on allume (contrat), on éteint (rien), on rallume pendant un
  contrat (rien de plus, le même client) — et il rougissait exactement sur le cas de Martin.

#### Le haut de gamme : deux chars qu'on vole exprès (taille 1) — **livré le 13 sept. 2026**

_Demande de Martin._ ⚠️ **Tout le reste du parc est utilitaire** — on le prend parce qu'il
sert : un camion pour défoncer, une ambulance pour se soigner, un taxi pour gagner sa vie. Il
manquait le contraire : un char qu'on prend parce qu'on le **veut**. Deux fiches, pas dix, et
elles ne valent que si elles **s'opposent**.

- **Le sport** (coupé décapotable, 26 × 13) : le plus rapide **sur quatre roues** — la moto
  reste devant, c'est la règle du parc depuis M3 — reprise sèche (0,085 contre 0,06 pour une
  berline), et une **adhérence de 0,055** là où tout le monde est à 0,12. ⚠️ **C'est
  l'adhérence qui EST le caractère du char** : `majPhysique` fait glisser la vitesse réelle
  vers le cap à ce taux, donc le coupé part en travers là où une berline se contente de
  ralentir. Et il le paie : **75 PV**, la carrosserie la plus mince des autos — un barrage
  l'arrête pour de bon.
- **Le luxe** (grosse berline noire, 32 × 15) : lourde (masse 1,8), elle encaisse (220 PV),
  elle colle à la route (0,16) et **elle ne va pas vite** (3,6). ⚠️ Elle ne récompense pas la
  conduite, elle récompense **le vol** : c'est la **meilleure revente du jeu** (5 200 $ neuf),
  et ça tombe tout seul — `economie.prix_vente` est déjà proportionnelle au prix neuf, et le
  malus par doublon du même jour empêche d'en faire une usine. Son alarme dure **30 s** contre
  12 pour les autres (`alarme_s` en fiche) : c'est le prix de cette revente.
- ⚠️ **Ce qui les rend rares, ce n'est pas leur `frequence`, c'est LA CARTE.** Ils portent
  `rare: true`, et un char rare ne naît **que** dans un district qui le déclare (`rares` de
  `carte.DISTRICTS`) : le luxe au Faubourg (l'Hôtel Bandini) et aux Érables (les entrées de
  banlieue), le sport au Faubourg et à La Pointe (le Carré). **Ni l'un ni l'autre à La Shop** —
  on ne laisse pas une décapotable dans une cour à ferraille — ni sur la baie. Un char rare
  qu'on croise partout n'est plus rare, et c'est tout ce qui fait qu'on le veut.
- ⚠️ **Et une cour de gang hérite des rares de son district.** `Monde.zoneA` rend la zone la
  **plus précise** : sans ça, un coupé ne naîtrait jamais dans le seul coin où l'on se bat
  pour eux.
- **Les deux dessins s'opposent aussi**, sinon ce sont deux lignes de catalogue de plus. Le
  sport est le **seul char du parc dont l'habitacle est ouvert** — un trou dans le toit, deux
  sièges dedans ; le luxe est le seul dont le toit est **plein, lisse et cerné de chrome**. Vu
  d'en haut, c'est tout ce qu'on a pour les nommer, et ça suffit.
- ⚠️ **Un juge du trafic a dû être réparé, pas contourné.** `test_le_trafic_roule_3000_images`
  ne suivait que les chars présents à **une** image donnée — or le joueur ne bouge pas, donc la
  plupart s'en vont en quelques secondes, et l'échantillon tombait à deux ou trois. Le juge
  dépendait alors du tirage plutôt que du trafic, et deux entrées de catalogue de plus ont
  suffi à le faire rougir. Il suit maintenant **tous** ceux qui passent pendant les
  1 800 images. ⚠️ Un char **bloqué**, lui, reste dans la bulle et accumule des images sans
  avancer d'un pixel : élargir l'échantillon le trouve **mieux**, pas moins bien — et le juge
  élargi passe aussi sur l'ancien code, ce qui prouve qu'on n'a pas baissé la barre.
- **Juges (2 neufs)** : les deux s'opposent (le sport est le plus rapide des autos et le plus
  fragile, le luxe le plus cher, le plus lourd, le plus accrocheur, et son alarme la plus
  longue) et **aucun char non rare n'est aussi rare qu'eux** ; côté carte, tout ce qui est
  déclaré `rare` naît **quelque part**, rien d'étranger ne se déclare, La Shop et la baie n'en
  ont aucun, et une cour de gang connaît les chars de son district.

#### Le camion défonce, l'ambulance soigne (taille 1) — **livré le 13 sept. 2026**

`defonce` et `soigne` étaient dans les fiches depuis M9, et **personne ne les lisait** : le
camion rebondissait sur un grillage comme une berline, et l'ambulance était une fourgonnette
blanche. Trois nombres du catalogue (0,75 · 0,7 · 0,6) et un quatrième (2 PV/s) qui ne
voulaient rien dire.

- **`Monde.defoncer(tx, ty)`** fait tomber une tuile **basse** et met à sa place le sol de ses
  voisines. ⚠️ **Le glyphe de remplacement se LIT DANS LES VOISINES** : une clôture entre un
  gazon et un trottoir laisse du gazon ou du trottoir. C'est ce qui évite un glyphe
  « décombres » de plus, avec son peintre, son entrée de légende et son octet dans le
  paquet — le trou dans une clôture, c'est la clôture qui manque, pas des gravats.
- ⚠️ **Et les morceaux voisins se repeignent, pas seulement le sien.** Une clôture lit ses
  voisines pour savoir comment se dessiner (`varianteDeCloture`, livré le matin même) : en
  casser une change le dessin des deux d'à côté, qui peuvent être dans un autre morceau.
- ⚠️ **Tout ou rien.** `defoncerDevant()` regarde **toutes** les tuiles qui bloquent avant de
  trancher : s'il y en a une seule qu'on ne casse pas, le camion s'arrête comme n'importe qui.
  Casser « celles qu'on peut » et s'arrêter sur le reste laisserait un trou dans une clôture
  **sans être passé** — le pire des deux mondes.
- ⚠️ **Jamais une façade**, jamais l'eau, jamais le barbelé, jamais un meuble. La ville tient
  par ses murs : les juges de connexité, les intérieurs et les devantures en dépendent, et un
  trou dans un mur ouvrirait sur un toit.
- **Ce qui reste de vitesse est le `defonce` de la fiche** — 0,75 pour le camion. Un mur de
  clôture coûte donc quelque chose (et `defonce_degats` à la carrosserie), sinon on le
  franchit sans le sentir.
- **L'ambulance rend `soigne` PV par seconde à qui la conduit.** ⚠️ Elle ne **ressuscite**
  personne : un mort reste mort. Sinon elle devient la sortie de secours de toutes les
  fusillades, et l'hôpital ne veut plus rien dire.
- ⚠️ **Ça ne se sauvegarde pas.** La ville se répare au rechargement : le trou dans la
  clôture vit le temps de la session. C'est une décision — la carte est le paquet, et écrire
  les tuiles cassées dans la sauvegarde ferait grossir chaque partie de tout ce qu'on a
  renversé depuis le premier jour.
- **Juges (2 neufs)** : un camion lancé traverse un grillage **et** une borne-fontaine, en
  garde 0,75 de sa vitesse mesurée **à l'image du passage**, et s'abîme ; il **ne traverse ni
  une façade ni du barbelé** ; une berline ne casse rien ; au pas (sous
  `defonce_vitesse_min`), personne ne défonce. Et l'ambulance rend bien ses PV, s'arrête au
  plafond, met la sauvegarde à jour, pendant qu'une berline n'en rend aucun.

#### La dépanneuse lève les roues (**ajout**, taille 1) — **livré le 14 sept. 2026**

_Demande de Martin :_ « la dépanneuse devrait embarquer les roues avant des véhicules qu'elle
remorque, sauf les motos et vélos qu'elle embarque complètement sur sa plateforme. »

⚠️ **Aujourd'hui, c'est une corde, pas une fourche.** `majCrochet()` tire le char vers un
point derrière la remorqueuse avec `crochet_raideur`, le char pointe **vers** elle, et le
lien **lâche** si on l'étire. Autrement dit : le véhicule remorqué roule sur ses quatre roues,
à plat, au bout d'un élastique. C'est ce qu'on écrit quand on a `crochet_cable_px` sous les
yeux — et c'est ce qui fait qu'une remorqueuse ressemble encore à une auto qui tire une auto.

Ce qu'il faut, et dans cet ordre :

- **Le lien devient RIGIDE.** Une fourche ne s'étire pas : le point d'attache est fixe, et
  `crochet_raideur` ne décrit plus rien. ⚠️ **Et ça change la réponse à la seule question qui
  compte** : que se passe-t-il quand la charge est bloquée par une tuile ? Ce n'est plus le
  câble qui s'allonge, c'est **la remorqueuse qui ne passe pas**. Elle teste donc **les deux
  corps** avant d'avancer — le même « tout ou rien » que `defoncerDevant()`. Sans ça, on
  recule dans un mur avec une auto au bout de la fourche et elle le traverse.
- **L'avant est levé, et ça se voit.** ⚠️ **Ne pas inventer un sprite « nez en l'air »** : ce
  serait 32 caps de plus par char et par couleur, pour deux pixels. Trois détails suffisent,
  et le moteur sait déjà les faire :
  - le char remorqué se **colle** à la remorqueuse — plus de trou de câble entre les deux ;
  - il se dessine **deux pixels plus haut**, l'ombre restée au sol : c'est exactement ce que
    `dessinerUn()` fait déjà pour `v.z > 2` ;
  - et il est **dans l'axe** de la remorqueuse, plus « pointé vers elle ». Une fourche ne
    laisse pas de jeu, et c'est ce jeu qui trahit la corde.
- **Le plateau, pour ce qui tient dessus.** Une moto, un vélo : ça ne se lève pas par l'avant,
  ça se **charge en entier**. ⚠️ **C'est Python qui le décide** — un champ `plateau` dans la
  fiche (vrai pour la moto et le vélo), pas un `classe === 'moto'` caché dans le JS. C'est la
  leçon de `reservoir` : le jour où une trottinette arrive, elle le dit elle-même, et un juge
  vérifie que la liste n'a pas changé de sens dans notre dos.
  - À bord, le deux-roues **ne traîne plus du tout** : même décalage, même cap, zéro écart —
    il bouge avec la remorqueuse comme s'il en faisait partie.
  - Il n'est plus **bloqué par les tuiles** et ne **heurte** plus rien : c'est de la
    cargaison, pas un véhicule sur la route.
  - Le lien ne peut donc pas lâcher : on n'étire pas un plateau. Le message « LE CÂBLE A
    LÂCHÉ » n'a plus de sens pour lui.
  - ⚠️ **L'ordre de dessin** : la charge se peint **après** la remorqueuse, sinon la moto
    disparaît sous elle. C'est le genre de détail qu'on ne voit qu'une fois en jeu.
- ⚠️ **On ne monte plus dans un char remorqué.** Rien ne l'interdit aujourd'hui, et ce serait
  la façon la plus courte de casser la physique : deux conducteurs, deux volontés, un seul
  lien rigide. Le refus doit se **dire** (une invite), pas juste ne rien faire.
- **Le sprite de la remorqueuse ne change pas** : il porte déjà son bras couché et son
  plateau. C'est la charge qui se place dessus.
- **Juges** : une auto remorquée est **collée** (l'écart tombe sous ce qu'il vaut aujourd'hui)
  et **dans l'axe**, pas en biais ; une moto et un vélo montent **sur** la remorqueuse — même
  cap, même vitesse, écart nul — et se dessinent après elle ; une moto à bord ne heurte rien
  et aucune tuile ne l'arrête ; la remorqueuse **refuse d'avancer** là où sa charge ne passe
  pas au lieu de la traîner dans un mur ; on ne monte pas dans un char remorqué ; et `plateau`
  est vrai pour **exactement** la moto et le vélo.

**Livré le 14 sept. 2026.** Tout y est, et deux choses se sont apprises en chemin.

- **Le lien est rigide** : `placeDeLaCharge()` rend un point fixe, `majCrochet()` **pose** la
  charge au pixel et au cap. Elle ne suit plus — elle **est** posée. `crochet_cable_px` et
  `crochet_raideur` ont disparu de la fiche : ils ne décrivaient plus rien.
- ⚠️ **La charge se pose APRÈS que la remorqueuse a bougé**, et c'est le juge qui l'a dit.
  Placée au début de l'image, elle l'était d'après la position de l'image **précédente** :
  l'écart respirait alors de la distance parcourue dans l'image — deux pixels à vitesse de
  croisière, et c'est **exactement** le jeu qu'une corde a et qu'une fourche n'a pas.
- ⚠️ **Une charge ne conduit pas.** Elle passait encore par `majPhysique` et `avancer` : elle
  refaisait sa propre physique par-dessus le placement, se dégageait des tuiles, rebondissait
  sur les murs et repartait de biais. Exactement le jeu qu'on venait d'enlever.
- **La remorqueuse ne passe pas là où sa charge ne passe pas** (`chargeBloquee`), le même
  « tout ou rien » que `defoncerDevant`. **Mesuré sans le garde-fou : 22 px de recul dans la
  façade**, l'auto au bout traversant le mur.
- **Le plateau vient de Python** : `plateau` dans la fiche, vrai pour exactement la moto et le
  vélo, et un juge le tient. À bord, zéro dérive (mesurée sur 120 images de virage), aucune
  tuile ne les arrête, et elles se peignent **après** la remorqueuse — sinon la moto disparaît
  dessous, et c'est le genre de détail qu'on ne voit qu'une fois en jeu.
- **Décrochée, la charge redescend** (`z = 0`). Sans ça elle restait en l'air, ombre décollée —
  et au-dessus de six pixels d'altitude, `bloqueParLesTuiles` la répute en plein saut et la
  laisse **traverser les murs**.
- **On ne monte plus dans un char remorqué**, et le refus **se dit** (« IL EST SUR LA
  FOURCHE ») : une portière qui ne s'ouvre pas sans un mot se lit comme un bogue.
- ⚠️ **Deux juges ont été réécrits, pas assouplis** : ils décrivaient le câble (« il s'étire »,
  « il lâche à 400 px »), ce que la fiche demandait précisément de supprimer. Ils mesurent
  maintenant la fourche — écart **constant** à un pixel près, valeur attendue lue dans la
  fiche, biais sous 0,02 rad — ce qui est plus strict que ce qu'ils exigeaient avant.

#### Le crochet de la remorqueuse (taille 1) — **livré le 13 sept. 2026**

`crochet` était la dernière ligne de fiche que personne ne lisait : la remorqueuse était un
camion orange. Elle traîne maintenant un char — **un seul**.

- **On accroche DERRIÈRE.** Un crochet est à l'arrière : il faut reculer dessus. C'est ce
  geste, et pas le catalogue, qui fait qu'une remorqueuse n'est pas un camion.
- ⚠️ **Un seul à la fois**, et ce n'est pas un détail de confort : c'est ce qui empêche le
  train de douze chars qu'on ne saurait plus arrêter. Le **même bouton** accroche et décroche.
- **Le câble** tire le char vers un point fixe derrière la remorqueuse (`crochet_cable_px`,
  `crochet_raideur`), et le char **pointe vers elle** — c'est ce qui se lit d'un coup d'œil.
- ⚠️ **Il reste bloqué par les tuiles** : on ne traîne pas une épave à travers un mur. Le
  câble s'étire alors, et **s'il s'étire trop, il lâche**. Un virage serré coûte donc quelque
  chose, sans une seule ligne de plus.
- ⚠️ **Jamais un char conduit** : on n'accroche pas une auto avec quelqu'un dedans.
- ⚠️ **Deux chars reliés ne se bousculent pas** (`heurterVehicules` saute la paire) et le
  trafic **n'oublie pas** un char qu'on traîne — sinon il disparaîtrait au bout du câble dès
  qu'il passerait la distance d'oubli. Et si la remorqueuse saute, le câble lâche : sans ça,
  un char reste accroché à une carcasse que plus personne ne met à jour.
- **Le boulot de remorquage est le même bouton** : il n'y aura pas deux gestes à apprendre
  quand la fourrière ouvrira.
- **Juge (1 neuf)** : rien ne s'accroche **devant** ; ce qui est derrière s'accroche ; un
  deuxième appui décroche au lieu d'ajouter ; un char conduit se refuse ; en roulant droit sur
  90 images le char suit sans monter dans la remorqueuse ni s'éloigner sans fin, et il pointe
  vers elle ; étiré de force à 400 px, le câble lâche.

#### Un vélo ne saute plus, il se plie (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Retour de Martin :_ il part en boule de feu et donne 2★.

⚠️ **Et c'est exactement ce qui se passait.** `endommager()` appelait `exploser()` dès que
les PV tombaient à zéro, **pour tous les véhicules sans une seule exception** — et le vélo a
30 PV, le plus fragile du jeu. Deux coups de batte, et le juge du banc le mesure : quarante
particules, quatre marques au sol, une déflagration de 60 px qui blesse le passant à 18 px
**et** cabosse l'auto d'à côté, l'écran qui tremble, un délit `explosion` et son alarme de
15 tuiles. On renversait un vélo, et la police arrivait.

Ce qui a été livré :

- **La règle tient sur une ligne de fiche** : `vehicules.py` gagne `reservoir` — **ce qui n'a
  pas de réservoir ne brûle pas et n'explose pas**. ⚠️ C'est **Python** qui le décide, pas un
  `slug === 'velo'` caché dans le navigateur : le jour où une trottinette arrive, elle se plie
  toute seule, et un juge dit que le vélo est le **seul** du catalogue dans ce cas.
- **Un vélo à zéro PV se plie** : il gît de travers (un peu de cap au hasard, pour qu'on voie
  qu'il est tombé), il grisonne, son cycliste part avec — il est déjà `ejecte` —, huit
  poussières et le bruit d'un choc. Pas d'explosion, pas de secousse, pas de marque au sol.
- ⚠️ **Il ne brûle pas non plus avant.** `majEtatDuChar` mettait le feu sous 20 % des PV et
  rongeait 4 PV par seconde jusqu'à l'explosion : un vélo cabossé au bord du trottoir
  s'enflammait tout seul, puis sautait. Ni feu ni fumée sans réservoir.
- ⚠️ **Ni une fois plié.** La carcasse d'un char fume tant qu'elle est là ; celle d'un vélo,
  non — il n'avait rien à brûler. C'est le détail qu'on ne voit qu'en regardant l'épave dix
  secondes, et c'est là qu'une règle à moitié appliquée se remarque.
- ⚠️ **Ni dans la chaîne** : `exploser()` endommage les véhicules autour, donc une explosion
  en déclenche d'autres. Un vélo garé à côté d'un char qui saute se plie maintenant au lieu
  d'agrandir la déflagration gratuitement — sans une ligne de plus, parce que c'est
  `endommager()` qui tranche, et que toute la chaîne passe par lui.
- **Juges (2 neufs)** : côté Python, le vélo est le seul sans réservoir et tout ce qui n'est
  pas de la classe `velo` en a un ; côté banc, **le même décor que le juge de l'explosion**,
  au vélo près — le voisin est intact, l'auto d'à côté est intacte, l'écran n'a pas tremblé,
  zéro marque, zéro délit, zéro étoile, et **zéro particule près du vélo pendant les cent
  images qui suivent**. ⚠️ Le même test fait ensuite sauter une auto pour de vrai : il mesure
  une **différence**, pas une panne.

#### Les quatre chars existent (taille 1) — **livré le 13 sept. 2026**

⚠️ **Le catalogue promettait des chars que le jeu ne montrait pas, et rien ne le disait.**
`camion`, `autobus`, `ambulance` et `remorqueuse` étaient en phase 1 : le trafic les tirait,
le garage les rachetait, la fourrière les comptait — et `SPRITES[v.sprite]` n'existait pas,
donc `dessinerUn()` sortait en silence sur son `if (!def) return`. Un char invisible qui
roule, qu'on peut heurter et voler.

Le prologue de `vehicules.py` annonçait pourtant : « phase 1 = le navigateur a son sprite. Un
test vérifie que chaque véhicule de phase 1 a un sprite. » ⚠️ **Ce test n'existait pas.**
`test_les_sprites_sont_integres` valide les sprites _déclarés_ dans `SPRITES` — il ne dit
rien du catalogue. C'est donc lui qu'on a écrit en premier, et il rougissait quatre fois.

Ce qui a été livré :

- **Le juge d'abord** : pour chaque véhicule de phase 1, `SPRITES[v.sprite]` existe, le
  sprite **couvre** la carrosserie (jamais plus court que `longueur`, jamais une affiche non
  plus : `longueur + 6` au plus) et il se cuit en 32 caps. ⚠️ Il tient aussi la liste de la
  phase 2 : le jour où le bateau y passe, le test le réclame au lieu de se taire.
- **Quatre sprites, et une règle de dessin qui vient de la vue.** ⚠️ **Vu d'en haut, un char
  est un TOIT** : à douze pixels de large, ce n'est pas le pare-brise qui nomme un véhicule,
  c'est ce qu'il porte sur le dos. D'où les **nervures** de la caisse du camion, les
  **trappes** de l'autobus, la **croix rouge** de l'ambulance, et le **bras couché avec son
  crochet qui dépasse** de la remorqueuse. La marge reste celle de l'auto (longueur + 4,
  largeur + 2) : deux pixels pour les roues, de chaque côté.
- ⚠️ **La chaîne de cercles lit enfin la fiche.** `cercles()` prenait `PHYSIQUE.cercles` — 3
  pour tout le monde, y compris pour un autobus de 48 px de long sur 16 de large. Le juge
  Python `test_la_chaine_de_cercles_ne_laisse_aucun_trou` exigeait 5 depuis M9, le catalogue
  les déclarait, et **le navigateur ne les lisait pas** : deux trous restaient entre les
  cercles, par lesquels une moto entrait dans l'autobus sans que rien ne se touche. Un
  deuxième juge mesure maintenant l'écart entre cercles voisins **au banc**, char par char.
- **Juges (2 neufs)** : celui des sprites de phase 1, et celui qui crée les cinq chars, les
  conduit vingt images, mesure la chaîne de cercles (aucun trou, le compte de la fiche) et
  dessine une image sans planter.
- ⚠️ **Corrigé le 13 sept. 2026, une heure après la mise en ligne** (bug de Martin :
  « l'autobus est transparent »). Il l'était. `s` valait `#00000030` — un noir à 19 % — copié
  des trois autos, **où il ne couvre que huit pixels de capot** : un reflet. Sur l'autobus, la
  même lettre couvrait deux trappes de toit de 66 pixels, soit **17 %** de la carrosserie, et
  le canevas de cuisson est transparent : on voyait la rue à travers l'autobus. Les quatre
  nouvelles palettes prennent des tons **opaques** (une trappe grise, une bande orange sur le
  blanc de l'ambulance), et **un troisième juge** tient la règle : un reflet est un détail,
  **au plus un pixel peint sur vingt** par sprite de véhicule. La règle n'est pas « aucune
  couleur translucide » — les trois autos en vivent très bien — c'est la **surface** qui
  décide. Il rougissait à 17 %.

### Un saut qu'on ne voit pas (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Bug signalé par Martin :_ « les rampes n'ont pas l'air de fonctionner, et s'il marche, il
faut qu'on voie une ombre pour bien imager le saut. »

⚠️ **Elles fonctionnent. Le saut mesure sept pixels et dure un tiers de seconde.** C'est pour
ça qu'il n'a pas l'air d'exister : `vz` vaut `vitesse × 0,42`, la gravité vaut 0,18, et la
hauteur d'un saut est donc `vz² / 2g` :

| Char | Vitesse max | Hauteur du saut | Durée |
|---|---|---|---|
| Berline | 4,0 | **7,8 px** | 0,31 s |
| Moto | 5,2 | **13,2 px** | 0,40 s |
| Auto-patrouille | 4,4 | 9,5 px | 0,34 s |
| Camion | 2,8 | 3,8 px | 0,22 s |
| **Vélo** | 2,0 | **2,0 px** | 0,16 s |

**Une tuile fait 16 px et un char est dessiné 32 × 16.** Un char qui monte de sept pixels
pendant un tiers de seconde, ce n'est pas un saut : c'est une bosse. Le joueur passe sur le
tremplin, entend le moteur, et ne voit rien — il en conclut, raisonnablement, que la rampe ne
marche pas.

- **Il faut que ça décolle pour de vrai.** L'impulsion et la gravité sont deux nombres dans
  `PHYSIQUE`, et ils se règlent ensemble : on veut un char qui monte assez haut pour passer
  **par-dessus quelque chose** et qui reste en l'air assez longtemps pour qu'on le voie
  partir. ⚠️ Et ça se règle **avec** la fiche de la réception : plus le saut est haut, plus il
  est long, et plus il faut de place pour retomber. Les deux se décident ensemble ou pas du
  tout.
- ⚠️ **Le vélo ne devrait pas sauter.** À 2 px/image il monte de deux pixels — moins que
  l'épaisseur de son ombre. Un vélo qui « saute » sans que rien ne bouge est pire qu'un vélo
  qui refuse la rampe. Soit il passe le seuil, soit il ne le passe pas ; à deux pixels, il ne
  le passe pas.

**L'ombre existe déjà, et elle ne dit rien.** `dessinerUn()` pose un rectangle noir de
**20 × 10 px, fixe**, dès que `z > 2` :

- elle a **la même taille pour tout le monde** — l'autobus fait 48 px de long et projette la
  même tache qu'une moto ;
- elle ne **bouge pas avec la hauteur** : elle ne rétrécit pas, ne s'écarte pas, ne pâlit pas.
  Or c'est exactement ça qui dit « il est haut » — une ombre qui reste collée sous le char ne
  raconte aucune altitude ;
- elle est **rectangulaire et non orientée**, alors que le char tourne sur 32 caps.

Ce qu'il faut : une ombre **à la taille du char**, qui **s'éloigne** et **rétrécit** à mesure
qu'il monte, et qui s'éclaircit avec l'altitude. Le jeu sait déjà faire ça — l'hélicoptère de
M7 a son ombre au sol depuis le premier jour.

- **Juges** : la hauteur d'un saut se voit (elle dépasse la hauteur d'un char dessiné) ; un
  vélo ne décolle jamais ; l'ombre existe pendant **tout** le vol, pas seulement au-dessus
  d'un seuil ; sa taille suit celle du char ; et la hauteur du saut reste cohérente avec la
  réception exigée par le générateur — le même calcul, une seule fois.

### Une rampe qu'on peut vraiment prendre (**correctif**, taille 2) — **livré le 13 sept. 2026**

_Demande de Martin :_ « les défis de rampe doivent vraiment être réalisables, avec assez
d'élan et assez de place pour atterrir sans frapper un mur. »

Les rampes se mesurent maintenant avant d'être posées — `ELAN_RAMPE = 10` tuiles devant,
`RECEPTION_RAMPE = 6` derrière, et rien ne se pose sans les deux. ⚠️ **Mais ces deux nombres
sont choisis en tuiles, alors que la portée d'un saut est de la physique** : elle vaut
`vitesse² × 2 × impulsion / gravité`, donc elle est **quadratique en vitesse** et différente
pour chaque char. Le calcul, avec les constantes d'aujourd'hui :

| Char | Vitesse max | Portée du saut | Réception exigée |
|---|---|---|---|
| **Moto** | 5,2 | **126 px** (7,9 tuiles) | 96 px — **il en manque 30** |
| Auto-patrouille | 4,4 | 90 px | 96 px, juste |
| Berline | 4,0 | 75 px | ça va |
| Camion | 2,8 | 37 px | ça va |

⚠️ **Et la moto est justement le char du défi.** _Le Grand Saut_ exige `vehicule: "moto"` et
60 px de vol. Le seul char que le défi demande est le seul que la règle de placement ne sait
pas recevoir.

**Les deux hypothèses sont fausses en même temps, et en sens contraire** : l'élan est mesuré
comme si l'on partait d'un arrêt (dix tuiles suffisent alors à peine), et la réception comme
si l'on ne dépassait jamais cet élan — alors que le code encourage exactement le contraire,
et il a raison : « l'élan n'a pas à tenir dans le terrain : il continue dans la rue, on arrive
lancé au lieu de partir d'arrêt ».

**Trois longueurs, pas deux, et toutes les trois se calculent :**

1. **L'élan** = la distance qu'il faut pour atteindre la vitesse que le défi demande. Elle
   sort de l'accélération et de la friction de la fiche — Python les a déjà.
2. **La portée** = `vitesse² × 2 × impulsion / gravité`, plus la longueur du char.
3. ⚠️ **Le freinage**, qu'on oublie et qui est le vrai mur : atterrir à 5,2 px/image et
   s'arrêter demande encore **75 px**, cinq tuiles de plus. La réception n'est pas le point de
   chute, c'est le point de chute **plus de quoi s'arrêter**.

- **Donc `RECEPTION_RAMPE` cesse d'être un nombre écrit à la main** : `carte.py` le calcule
  depuis `vehicules.PHYSIQUE` et le catalogue, pour le char le plus rapide qui peut arriver
  là. Un réglage de physique change, la ville se replace toute seule — et un test vérifie que
  les deux restent d'accord.
- ⚠️ **En l'air, on survole les murs**, et c'est voulu : `bloqueParLesTuiles` rend faux
  au-dessus de `z > 6`. Ce qui doit être dégagé n'est donc pas tout le trajet, mais la **zone
  d'atterrissage** et ce qui la suit. Un saut par-dessus un mur est un bon saut ; un saut qui
  finit **dans** un mur est un défi qu'on ne peut pas gagner.
- **Juges** : pour chaque rampe posée, et pour chaque char capable d'y arriver, la chute **et**
  le freinage tombent sur du roulable — le test rejoue la trajectoire, il ne la devine pas ;
  la rampe du _Grand Saut_ est validée **pour la moto**, pas pour un char moyen ; et l'élan
  disponible permet vraiment d'atteindre les 60 px de vol exigés, en partant de la rue.

### L'endurance est restée celle du Faubourg (**correctif**, taille 2) — **livré le 13 sept. 2026**

_Demande de Martin :_ « je veux que la course ne consomme plus d'énergie, mais que ce soit le
sprint qui en consomme — étant donné qu'on court quand même tout le temps, avec la grandeur
de la carte. »

⚠️ **Mesuré, et c'est pire que « on court tout le temps ».** Le modèle d'endurance a été réglé
pour le Faubourg de 157 tuiles ; M8 a quintuplé la ville et personne n'y est revenu :

|  |  |
|---|---|
| Un souffle complet de course | **4,2 secondes**, soit 525 px — **33 tuiles** |
| La ville | **421 tuiles** de large |
| Refaire le plein, en marchant | **6,9 secondes** |
| Vitesse **soutenable** (courir, puis marcher pour souffler) | **1,54 px/image** |
| Vitesse du policier à pied | **1,9** |
| Traverser la ville à ce rythme | **73 secondes** |

⚠️ **Le policier court donc plus vite que la vitesse que le joueur peut tenir.** Fuir à pied
ne marche déjà pas — et pendant ce temps, traverser la ville demande de gérer une barre
pendant une minute et quart. La barre ne récompense rien : elle taxe le déplacement.

**Trois vitesses au lieu de deux**, et c'est exactement ce qui est demandé :

|  | Vitesse | Coût |
|---|---|---|
| **Marche** | 1,2 | rien |
| **Course** | ~2,0 | **rien** — la vitesse de voyage, celle qu'on tient de La Pointe aux Quais |
| **Sprint** | ~2,6 | l'endurance, par bouffées |

⚠️ **Mais rendre la course gratuite casse toutes les poursuites à pied si on s'arrête là.** Le
dépôt a déjà écrit pourquoi, dans `economie.py`, à propos du café : « la vitesse, c'est ce qui
sépare le joueur (2,1) du policier (1,9) ; y toucher casserait toutes les poursuites du jeu ».
Une course gratuite à 2,0 contre un policier à 1,9, c'est **s'échapper à pied, toujours, sans
rien dépenser**. La parade est celle déjà écrite deux fois ailleurs — le char rapide, les
armes à feu : **la vitesse achète de la distance, jamais l'impunité**.

- **Le policier court à la vitesse de ta course.** À pied, on ne gagne plus de terrain en
  courant : on en gagne par **bouffées de sprint**, et ça coûte. On sème la police en cassant
  la ligne de vue, en montant dans un char, ou en payant du souffle. C'est mieux que ce qu'on
  a — aujourd'hui la poursuite à pied se perd toujours, et lentement.
- ⚠️ **M5 en dépend** : « semer la police et rentrer » est une mission au tableau. Elle se
  rejoue après le changement, elle ne se suppose pas.
- **Le café et le surplus y gagnent.** Le café divise la dépense du sprint ; le surplus, qui
  vient d'arriver, est ce que le repos ne donne pas. Les deux servaient à courir un peu plus
  longtemps ; ils serviront à **s'échapper** — une bien meilleure raison de s'arrêter au
  kiosque.
- ⚠️ **La barre sera presque toujours pleine**, puisque seul le sprint la vide. Une barre qui
  ne bouge jamais ne dit rien : elle doit se montrer quand elle compte et s'effacer sinon.
- ⚠️ **Le vocabulaire ment déjà.** `VITESSES["joueur_sprint"]` désigne ce qui deviendra la
  **course**, et le commentaire du café raisonne sur « 2,1 contre 1,9 ». Renommer fait partie
  du correctif — `joueur_course` et `joueur_sprint` — sinon la prochaine personne lira le
  contraire de ce que le code fait.
- **Juges** : traverser la ville d'un bout à l'autre ne consomme **rien** ; un policier lancé
  derrière un joueur qui court ne perd pas de terrain ; un sprint plein, café compris, ouvre
  un écart **borné** (le même calcul que pour le char rapide) ; et la durée d'un souffle se
  compare à la **taille de la ville**, pas à un nombre choisi une fois pour toutes.

**Livré le 13 sept. 2026 :**

- **Trois vitesses, un seul bouton** — et la **course est la vitesse par défaut**. Pousser le
  pouce à fond, ou n'importe quelle touche de direction, c'est courir ; l'effleurer, c'est
  marcher ; le bouton, c'est sprinter. ⚠️ **Au clavier, on ne marche donc plus**, et c'est
  voulu : il n'y a pas d'analogique sur un clavier, et inventer une touche « marcher »
  ajouterait une commande pour un usage que personne n'a réclamé. La marche reste là où elle
  se dose — au pouce.
- **Le bouton s'appelle SPRINT**, plus « COURS » : l'étiquette disait le contraire de ce que
  le bouton fait maintenant.
- ⚠️ **La barre de souffle s'efface quand elle n'a rien à dire.** Seul le sprint la vide :
  elle est pleine presque tout le temps, et une barre qui ne bouge jamais ne se lit plus — on
  cesse de la regarder le jour où elle compte. Elle revient dès qu'on entame le souffle, qu'on
  a du surplus ou qu'on est sous café, et s'attarde une seconde pour ne pas clignoter.
- **Le vocabulaire a été corrigé** : `joueur_course` (gratuite) et `joueur_sprint` (payante).
  L'ancien `joueur_sprint` désignait ce qui devient la course, et le commentaire du café
  raisonnait sur « 2,1 contre 1,9 » — la prochaine personne aurait lu le contraire de ce que
  le code fait.
- **Juges (3 neufs, 1 réécrit)** : traverser la ville d'un bout à l'autre — 421 tuiles, 56 s
  de touche tenue — ne coûte **rien** ; un agent lancé derrière un joueur qui court ne perd
  **pas un pixel**, et le même agent, même décor, perd **plus de trois tuiles** quand le
  joueur sprinte (et le souffle baisse) ; l'écart d'un sprint plein, café compris, reste
  **borné** sous quatre fois la portée de vision d'un agent ; et le juge du mouvement mesure
  maintenant les **trois** vitesses au lieu de deux. ⚠️ Le juge de la fuite est une vraie
  poursuite simulée, pas un calcul : c'est la seule façon de voir que le A\* de l'agent, ses
  virages et ses sous-pas ne lui rendent pas le terrain que la vitesse lui refuse.

### Les étoiles de recherche, grosses, jaunes et au centre (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Demande de Martin :_ « je veux les étoiles de police plus grosses, jaunes et au centre de
l'écran. »

⚠️ **Aujourd'hui, l'argent est dessiné deux fois plus gros que le niveau de recherche.** Les
étoiles sont du **texte** — des `★` de la police 5 × 7, à l'échelle **1** — rangés dans la
colonne du coin haut-droit, sous un montant en argent tracé à l'échelle **2**. La chose la
plus importante d'une poursuite est donc le plus petit élément de l'écran, dans un coin, en
blanc. C'est à l'envers.

- **Plus grosses** : pas en agrandissant le caractère. Un `★` de 5 × 7 tiré à l'échelle 3
  donne une bouillie de blocs. Une **étoile dessinée**, cuite comme les autres sprites depuis
  sa grille de caractères, se lit à n'importe quelle taille — et l'atlas sait déjà faire
  exactement ça.
- **Jaunes.** ⚠️ Avec une nuance à trancher : le doré `#e8b33c` est **déjà** celui de
  l'argent, juste au-dessus, et celui de « ce qui est à toi » sur la carte. Deux choses
  différentes de la même couleur dans le même coin, ça ne se lit plus. Soit les étoiles
  prennent un jaune à elles, soit elles déménagent — et justement, elles déménagent.
- **Au centre.** ⚠️ Pas au milieu de l'écran : le milieu, c'est le joueur, et une rangée
  d'étoiles par-dessus l'action cacherait ce qu'on regarde. **En haut, centré** — la place des
  étoiles dans le genre. Mais ce coin-là est déjà pris : `noter('objectif', …)` y écrit la
  ligne de mission. Les étoiles passent devant (en poursuite, c'est **l'information**), et la
  ligne d'objectif descend sous elles.
- **Les étoiles éteintes ne sont pas des points.** Le code écrit `'.'` pour celles qu'on n'a
  pas — ça se voyait à l'échelle 1, ça ne tiendra pas en gros. Il faut une étoile **creuse** :
  on doit lire « trois sur cinq » d'un coup d'œil, sans compter.
- **Le clignotement rouge reste**, et c'est lui qui dit qu'un palier vient de changer. En
  jaune, il doit rester aussi visible qu'en blanc — c'est le seul signal du passage à
  l'étoile suivante, et il ne se remplace pas par « c'est plus gros ».
- ⚠️ **Le tactile** : `noter()` enregistre chaque élément du HUD, et un test vérifie
  qu'aucun ne finit sous un bouton du pouce. Les étoiles qui déménagent réenregistrent leur
  ancre, sinon le juge tactile parle encore de l'ancien coin.
- **Juges** : les étoiles sont l'élément le plus grand du HUD en poursuite ; on distingue
  allumée d'éteinte sans compter ; rien du HUD ne se chevauche au centre (étoiles et ligne
  d'objectif) ; et aucune ancre ne tombe sous un bouton tactile.

### Les clôtures nord-sud doivent être MINCES, vues par la tranche (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Demande de Martin :_ « les clôtures nord-sud doivent être plus vues de haut, donc mince. »

Les clôtures lisent maintenant leurs voisines et ne sont plus couchées — mais elles ont été
corrigées **par une rotation** : le nord-sud est l'est-ouest tourné de 90°, les deux axes
échangés. D'où un panneau vertical large de sept pixels, avec sa maille et ses lisses, qui a
l'air d'être **posé à plat** plutôt que debout.

⚠️ **La bonne règle est déjà écrite deux fois dans le dépôt, et les clôtures ne l'appliquent
pas.** Les bâtiments : « toute tuile dont la voisine du sud n'appartient pas au bâtiment est
une façade — on voit toujours le mur avant, jamais le dos d'un toit ». Les meubles : « un
meuble se dessine **vu d'en haut, avec juste assez de face au sud** pour qu'on lise son
volume — c'est la même règle que les façades de la ville ».

La caméra regarde donc d'en haut, avec un peu de face au sud. Il en découle, sans rien
inventer :

- **Est-ouest** : on la voit **de face**. Sa hauteur est visible — lisses, maille, poteaux. Le
  panneau actuel est juste, il ne change pas.
- **Nord-sud** : on la voit **par la tranche**. Il ne reste que son **épaisseur** : un trait
  fin, les chapeaux de poteaux, et un liseré d'ombre d'un côté. Deux ou trois pixels de large,
  pas sept. Une clôture n'a pas d'épaisseur, c'est tout son propos.
- **Au coin**, les deux se rencontrent : le bras est-ouest garde sa face, le bras nord-sud est
  mince, et le poteau du centre fait la jointure — c'est lui qui empêche que la différence de
  largeur ait l'air d'une cassure.

⚠️ **Et un juge verrouille aujourd'hui exactement le défaut.**
`test_une_cloture_nord_sud_ne_se_peint_pas_comme_une_est_ouest` compare les deux cuissons
trait par trait et exige que « le nord-sud soit l'est-ouest **tourné**, les deux axes
échangés ». Il a rendu service — il a sorti les clôtures de leur premier bug — mais il
**interdit maintenant la correction**. Il doit être remplacé par son contraire : le nord-sud
n'est **pas** la rotation de l'est-ouest, il est **plus mince** que lui, et le juge mesure
cette largeur.

- **Juges** : la largeur peinte d'un brin nord-sud est au plus la **moitié** de la hauteur
  peinte d'un brin est-ouest, pour les **trois** clôtures ; un bout nord-sud se ferme par un
  **chapeau** et jamais par un piquet debout ; un coin garde son poteau ; et le nord-sud n'est
  plus la rotation de l'est-ouest — l'ancien juge, retourné.

**Livré.** Mesuré après coup : grillage 12 px de haut en est-ouest contre **4 px de large** en
nord-sud, bois 12 contre **5**, barbelé 14 contre **4**. Le poteau se montre debout quand un
bras est-ouest donne sa face, et en **chapeau** quand la tuile est toute en nord-sud.

### La nuit ne se vide pas (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Demande de Martin :_ « la nuit, il devrait y avoir moins de monde et de voitures sur les
routes. »

Le mécanisme existe depuis M8 — chaque district a un `rythme` (nuit, matin, soir) que
`Monde.rythme()` applique aux piétons et aux véhicules. ⚠️ **Mais il ne fait presque rien, et
dans le Faubourg il ne fait littéralement rien.**

| District | Piétons | Véhicules en circulation |
|---|---|---|
| **Le Faubourg** | 26 → **19,5** | 9 → **9** |
| Les Quais | 20 → 14 | 8 → 5,6 |
| Les Érables | 14 → 7 | 7 → 3,5 |
| La Pointe | 12 → 4,2 | 4 → 1,4 |
| La Shop | 11 → 1,6 | 9 → 1,3 |

⚠️ **Le Faubourg ne perd pas une seule voiture la nuit**, et c'est arithmétique, pas une
impression : il en déclare 12, son rythme de nuit vaut 0,75, et le plafond `vehicules_max`
vaut **9**. Or 12 × 0,75 = 9. `min(9, 9)` le jour, `min(9, 9)` la nuit — **le plafond mord
avant le rythme**, et la nuit n'existe pas. C'est le quartier où l'on passe le plus de temps,
et c'est le seul où la valeur tombe pile sur le plafond.

⚠️ **Et il garde 19 piétons à 3 h du matin.** Un rythme de 0,75 enlève un quart du monde : ça
ne se voit pas. Une nuit, c'est un trottoir vide et deux phares au loin.

- **Les rythmes de nuit descendent**, et le Faubourg le premier. La Shop à 0,15 est le bon
  exemple : elle se vide pour de vrai, et c'est exactement ce qui la rend inquiétante — le
  reste de la ville devrait avoir le droit d'être inquiétant aussi.
- ⚠️ **Le plafond doit s'appliquer avant le rythme, pas après.** `min(plafond, déclaré) ×
rythme`, et non `min(plafond, déclaré × rythme)`. Sinon tout district généreux le jour se
  retrouve coincé au plafond la nuit, et la correction des nombres ne suffira pas.
- ⚠️ **La police, elle, ne suit aucun rythme.** `zone.police` est lu tel quel : autant
  d'agents à 4 h du matin qu'à midi. Une ville déserte patrouillée comme en plein jour, ça se
  remarque tout de suite — et à l'inverse, une police plus rare la nuit rend la nuit
  intéressante.
- **Les chars stationnés restent**, et c'est juste : on ne rentre pas son char dans sa poche.
  Mais leur répartition devrait tourner — plus dans les entrées des Érables la nuit, moins sur
  les rues commerçantes.
- **Ce que ça donne, et c'est le vrai gain** : la nuit devient un **choix**. Moins de monde,
  c'est moins de témoins, donc moins d'étoiles pour le même geste. Le jeu a déjà tout ce qu'il
  faut pour ça — les témoins, les cônes de vision réduits la nuit — il ne manquait que des
  rues vraiment vides pour que ça se sente.
- **Juges** : dans **chaque** district, la nuit compte strictement moins de piétons et moins
  de véhicules que le jour (un test qui aurait rougi sur le Faubourg) ; le plafond ne masque
  jamais le rythme ; et la police suit le rythme comme le reste.

### Des arbres plantés au milieu des sentiers (**correctif**, taille 1) — **livré le 13 sept. 2026**

_Demande de Martin :_ « les arbres ne devraient pas être dans les sentiers. »

⚠️ **Et ce n'est pas qu'une question de vue : un arbre est SOLIDE.** `_parc()` trace ses
allées en baïonnette, puis sème ses arbres, ses bancs et ses buissons **sur tout le rectangle
du parc**, au hasard. `poser_decor()` refuse ce qui est solide, routier, occupé ou réservé —
mais une allée est du pavé `.` (ou de la terre battue `s`) : marchable, pas routière. Rien ne
la protège. Un arbre tombe donc dans l'allée, et comme il a un rayon de 5 px et qu'une allée
fait deux tuiles, il la bouche à moitié. **Un sentier barré par ses propres arbres est pire
qu'un parc sans sentier** : on l'a dessiné pour dire « passe par ici ».

**Le mécanisme du remède existe déjà** : `self.reserve` — les tuiles qu'on garde libres, dont
`poser_decor` ne veut pas. C'est ce qui tient le devant des portes depuis M1. Il suffit
qu'une allée **se réserve en se traçant**.

- ⚠️ Ça vaut pour **tout ce qui se pose après** : les bancs et les buissons tombent dans les
  allées par le même chemin, et le banc est solide lui aussi. La réserve les règle tous d'un
  coup — c'est pour ça qu'on corrige là plutôt que dans le tirage des arbres.
- ⚠️ Et ça vaut pour **le sentier de banlieue** que la fiche des terrains prévoit : de la
  porte à la rue, réservé, sinon on y replantera un arbre le jour où on le dessinera.
- Un banc **à côté** d'une allée, en revanche, est exactement ce qu'on veut : la réserve
  couvre l'allée, pas ses bords.
- **Juges** : aucun décor solide sur une tuile d'allée, dans aucun parc, sur cinq graines ;
  et de l'entrée d'un parc jusqu'à son cœur, le chemin reste franchissable à pied sans
  contourner un tronc.

### La musique dit où tu es et ce qui t'arrive (**ajout**, taille 3) — **livré le 14 sept. 2026**

_Demande de Martin :_ « je veux des musiques différentes par district, et une musique générée
par IA pour l'écran titre. Je veux aussi des musiques pour quand on se bat avec des gangs, et
quand on a plusieurs étoiles. »

Aujourd'hui il y a **une** musique de fond — `ville`, 60 secondes, la même de La Pointe aux
Quais — et le thème du menu, écrit en notes. Rien ne change quand on traverse un pont, rien ne
change quand trois Cravates te tombent dessus, rien ne change à quatre étoiles.

**Le thème du titre : le plan l'avait déjà prévu, mot pour mot.** `musique.py` s'explique
là-dessus depuis le premier jour : « le jour où Martin veut une vraie pièce jouée par de vrais
instruments, elle se posera **par-dessus** comme les radios — c'est la même règle que partout
dans `audio.py` : l'échantillon quand il existe, la synthèse sinon ». Ce n'est donc pas un
revirement : le thème écrit en notes devient le **filet**, et un enregistrement se pose
dessus. Le jour où le fichier manque — réseau coupé, génération ratée — le menu a encore sa
musique.

**Cinq districts, cinq ambiances**, chacune avec ce qui fait son quartier : la brume et le
piano du Faubourg, le calme plat des Érables, le fer et le vide de La Shop, la corne et les
mouettes des Quais, le vent et les arbres de La Pointe.

⚠️ **Trois choses à régler, et ce sont elles le vrai travail** — pas les pistes :

- **Le poids.** Une piste de 60 s à 64 kbit/s pèse 480 Ko. Cinq districts, un titre, une
  poursuite et une bagarre font **huit** pistes, presque 4 Mo — le dossier audio en pèse déjà 4. Elles ne peuvent donc **pas** se charger au démarrage. La règle des radios s'applique
  telle quelle : on charge **au moment d'en avoir besoin**, une à la fois, et la piste d'un
  district s'annonce quand on approche de sa frontière, pas quand on y entre.
- **La couture.** Les districts se touchent — c'est tout le propos de M8, la ville est d'un
  seul tenant et rien ne se charge en roulant. Une musique ne peut donc pas **couper** à la
  frontière : elle se fond sur quelques secondes. ⚠️ Et il faut de l'**hystérésis** : on
  traverse une frontière en zigzag sur un boulevard, et une musique qui bascule à chaque pas
  de côté est pire que pas de musique du tout.
- ⚠️ **Qui gagne.** C'est la question qu'aucune des quatre demandes ne pose et dont tout
  dépend. Il y a déjà de la radio dans un char, l'ambiance à pied, la rumeur de la foule, les
  sirènes et les voix. Il faut **une échelle, écrite une fois** :

  |     |                                                             |
  | --- | ----------------------------------------------------------- |
  | 1   | une réplique de l'histoire — elle baisse déjà tout le reste |
  | 2   | **la poursuite**, à partir de N étoiles                     |
  | 3   | **la bagarre de gang**                                      |
  | 4   | la radio du char, ou l'ambiance du district                 |

  Et la rumeur de la foule passe dessous, toujours.

- ⚠️ **Une musique d'état a besoin d'une queue.** Les étoiles montent et descendent, une
  bagarre s'arrête et reprend. Sans durée minimale ni fondu de sortie, la poursuite
  démarrerait et s'arrêterait trois fois en dix secondes. La musique de poursuite continue
  quelques secondes après la dernière étoile perdue — c'est ce qui fait qu'on **souffle**.
- **À partir de combien d'étoiles ?** Une étoile, c'est un témoin qui a appelé ; ça n'est pas
  une poursuite. La musique arrive à **deux**, et peut monter d'un cran à quatre, quand
  l'hélico entre. Un seul réglage en Python, comme tout le reste.
- **Juges** : chaque district a une ambiance déclarée, et aucune ne se charge avant qu'on en
  approche ; une seule piste de musique joue à la fois (l'échelle est respectée, un test la
  rejoue) ; traverser une frontière en zigzag ne change pas de piste plus d'une fois ; le
  thème du menu joue **même sans aucun fichier** ; et le poids total reste sous son plafond,
  mesuré comme celui des radios.

**Livré le 14 sept. 2026 :**

- ⚠️ **Écrites en notes, et le poids disparaît avec la question.** Huit pistes de 60 s à
  64 kbit/s pèsent 4 Mo — autant que tout le dossier audio — et coûtent des crédits
  ElevenLabs. En notes, elles pèsent quelques kilo-octets, se chargent avec le paquet, et il
  n'y a **rien à charger à l'approche d'une frontière**. Ce n'est pas un raccourci :
  `musique.py` l'écrit depuis le premier jour — « le jour où Martin veut une vraie pièce
  jouée par de vrais instruments, elle se posera **par-dessus** comme les radios ». Le jour où
  un mp3 arrive, il se pose et celles-ci redeviennent le filet.
- **L'échelle est en Python** (`musique.ECHELLE`) et le navigateur la **lit** : histoire 1,
  poursuite 2, bagarre 3, ambiance 4. Sans ça, chaque endroit du JS aurait la sienne et deux
  musiques joueraient ensemble un jour sur trois.
- ⚠️ **La radio d'un char et l'ambiance occupent la MÊME case.** Et c'est `demandee` qu'on
  regarde, pas `courante` : une station se demande tout de suite et n'arrive qu'une seconde
  plus tard — attendre son arrivée laisserait le district jouer par-dessus pendant tout le
  téléchargement.
- ⚠️ **L'hystérésis ne s'applique pas au PREMIER district.** Elle sert à ne pas basculer trop
  vite ; au démarrage il n'y a rien à quitter — et sans ce cas, la musique attendait qu'on
  marche six tuiles avant de commencer, c'est-à-dire qu'elle ne commençait **jamais** si on
  restait sur place.
- **La queue** : la poursuite continue sept secondes après la dernière étoile perdue. Sans
  elle, elle démarrerait et s'arrêterait trois fois en dix secondes — et c'est cette queue
  qui fait qu'on **souffle**.
- ⚠️ **La musique unique de la ville ne démarre plus**, c'est tout le propos. Le fichier
  `ville.mp3` reste sur le disque et garde son juge de navigateur — celui qui prouve qu'il se
  **décode** — mais on le demande maintenant explicitement au lieu de l'attendre.
- **Juges (1 neuf, 4 rejoués)** : l'échelle est ordonnée et la poursuite couvre l'ambiance à
  deux étoiles ; la queue tient ses sept secondes puis rend la main au district ; un **zigzag
  de quarante images sur une frontière ne change de piste qu'une fois**, et s'enfoncer pour de
  bon la change ; à pied c'est l'ambiance du district, au volant la radio, et jamais les deux.

### Toute la musique est générée par IA (**correctif**, taille 2) — **livré le 14 sept. 2026**

_Demande de Martin :_ « je veux que toutes les musiques soient des musiques générées par IA. »

Il en restait **quinze écrites en notes** : le thème du menu, les deux stations de char du
camion et de la remorqueuse, les cinq ambiances de district, la poursuite, la bagarre et les
cinq pièces du musicien de rue. Elles sont maintenant **quinze mp3 ElevenLabs Music** —
641 secondes, **5,2 Mo**, 30 crédits la seconde (mesuré : 1 350 crédits pour les 45 s du thème).

**La porte était écrite depuis le premier jour, mot pour mot.** `musique.py` s'explique en
tête de fichier depuis M7 : « le jour où Martin veut une vraie pièce jouée par de vrais
instruments, elle se posera **par-dessus** comme les radios — c'est la même règle que partout
dans `audio.py` : l'échantillon quand il existe, la synthèse sinon ». C'est exactement ce qui a
été fait, et c'est pour ça que la fiche est petite : rien n'a été remplacé, un étage a été posé.

- **Les notes restent, et ce n'est pas de la sentimentalité** — c'est la règle 1 d'`audio.py`.
  `exporter()` ne déclare que les fichiers **réellement présents** ; un dépôt frais, une
  génération ratée, un réseau coupé, et le séquenceur reprend le morceau exactement là où il
  est écrit. Le joueur n'a jamais un trou de musique. Un juge remet le cas : mp3 introuvable →
  les oscillateurs repartent.
- ⚠️ **Le slug ne change pas, et c'est tout l'intérêt.** Le chef d'orchestre demande
  `amb_quais` comme avant, le bouton RADIO du camion demande `station_camion`, l'hystérésis aux
  frontières, la queue des musiques d'état et l'échelle de priorité **n'apprennent rien**.
  Seul `son.js` sait, morceau par morceau, si c'est le fichier ou le séquenceur qui joue.
- ⚠️ **Deux volumes par morceau, et il en fallait deux.** Dans le séquenceur, le volume du
  morceau **multiplie** celui de chaque voix (0,11 à 0,45) : `titre` à 0,85 sort à un dixième
  de l'échelle. Un mp3, lui, arrive normalisé à −1 dBFS — le même chiffre saturerait. Python
  déclare les deux (`musique.py` pour les notes, `audio.MUSIQUES` pour le fichier) et le
  navigateur prend celui de la source qui joue.
- ⚠️ **Trois états de chargement, pas deux.** « en cours » n'est pas « ratée » : pendant le
  téléchargement on se **tait** quelques centaines de millisecondes, comme une vraie radio
  qu'on allume, plutôt que de lancer un bout de séquenceur qu'il faudrait couper net à
  l'arrivée du fichier. « ratée » rend la main aux notes pour de bon.
- ⚠️ **Deux clés de tampon** (`musique-` et `rue-`) : le musicien de rue joue **par-dessus**
  l'ambiance du district, comme un moteur de char — deux boucles tournent donc en même temps,
  et une clé partagée ferait que l'une chasserait l'autre. Son volume vient de la **distance**
  et se repose à chaque image (`Son.volumeBoucle` le rend lisible pour un juge) ; sa main
  gratte **en mesure** sur l'horloge audio, au tempo que Python déclare, puisqu'un mp3 n'a pas
  de « pas ».
- ⚠️ **Rien ne se charge au démarrage.** Une ambiance arrive quand on entre dans son district,
  une station au premier tour de clé, la toune du musicien quand on s'en approche. Le dépôt,
  lui, porte les 5,2 Mo.
- ⚠️ **On ne génère que ce que le jeu joue.** Une pièce dont le slug ne correspond à aucun
  morceau de `musique.py` serait un fichier **payé** que personne ne jouerait jamais :
  `musiques_manquantes()` filtre sur ce que `musique.exporter()` rend vraiment.

**Et un vrai défaut trouvé en chemin, qui ne touchait pas qu'au mp3.** `Son.Rue.tick()` passe
en tête de `maj()` dans `jeu.js`, alors qu'`Entites.maj()` — celui qui **demande** la toune du
musicien le plus proche — tourne tout à la fin, juste avant `B.t++`. La demande que le tick lit
porte donc **toujours** le numéro de l'image précédente, et le test d'égalité stricte
(`demandeT !== B.t`) réduisait le musicien au silence à l'image suivant chacune de ses
demandes, sans arrêt : sa musique ne démarrait **jamais**, ni en notes ni en fichier, et rien
ne le disait — `Entites` continuait sagement à la demander. Une image de retard est désormais
normale ; au-delà, plus personne ne joue. Le bug a été remis exprès pour vérifier que le juge
tombe.

⚠️ **Ce qu'aucun test ne dit** : si c'est beau. Quatre masters sortent à 0,0 dBFS (poursuite,
bagarre, le reel du trottoir) — au plafond, comme les radios de M3, et tenus en dessous par le
`volume` du catalogue. C'est l'oreille de Martin qui tranche, et `--refaire <slug>` qui refait.

**Juges** : 11 Python (`test_musique.py` — couverture : aucun morceau sans musique générée ;
aucune pièce payée pour un morceau qui n'existe pas ; le musicien de rue reste **un homme seul
avec une guitare** ; aucune batterie sous un district ; aucune voix chantée ; la boucle tient
24 s ; le budget du dépôt) et 6 de banc (`test_son_js.py` — le mp3 boucle **et** le séquenceur
se tait ; un mp3 qui n'arrive pas rend la main aux notes ; le ducking atteint les musiques en
mp3 ; le musicien suit la distance et s'arrête quand on le laisse derrière ; le musicien et le
district jouent ensemble ; le musicien n'est pas coupé à chaque image).

### Le décor se brise (**correctif**, taille 2) — **livré le 13 sept. 2026**

_Demande de Martin :_ « une interaction réaliste avec le décor — les bris de poteau, de banc
de parc et d'arbre, tout ce qui se brise. »

⚠️ **Le décor est solide pour les piétons et fantôme pour les chars.** `bloquerParDecor`
repousse un passant hors d'un arbre, d'un banc, d'une poubelle ; côté véhicules, le seul
appel à `decorAutour` sert à choisir une place de stationnement. Un autobus traverse donc un
arbre, un kiosque à hot-dogs et une fontaine sans ralentir — et **le lampadaire est fantôme
pour tout le monde** (`solide: false`), on le traverse à pied comme en char. Le défonçage
de M9 ne casse que des **tuiles** (clôtures, bornes) : le décor, lui, n'est ni un obstacle
ni une chose qui casse. C'est la moitié d'un monde.

**Deux familles, et c'est la fiche qui décide** (`DECORS`, comme `vehicules.py` décide ce
qu'un char sait faire) :

- **ce qui ARRÊTE un char** : un arbre, une fontaine, une borne — le char prend des dégâts
  comme contre un mur, et la chose ne cède qu'au-dessus d'un poids (le `defonce` de la fiche
  existe déjà : un camion déracine un arbre, une berline s'y écrase) ;
- **ce qui CASSE sous un char** : un banc, une poubelle, un kiosque à journaux, un cône, un
  lampadaire — le char ralentit d'une fraction (`defonce`) et continue, la chose est par
  terre.

**Le bris a un après, sinon ce n'est qu'une disparition :**

- des **débris** (le décor `debris` existe) là où c'était, et un banc cassé, un arbre couché
  ou un poteau à terre deviennent des obstacles **bas** — solidité 3, comme une clôture : on
  les enjambe à pied, un char les évite ou les défonce ;
- ⚠️ **un lampadaire à terre ne s'allume plus.** Sa lumière vit dans `carte.lampes`, à part
  de son poteau ; casser l'un sans éteindre l'autre donnerait un halo qui flotte au-dessus
  de rien — exactement le genre de chose qu'on ne voit qu'en jouant, la nuit ;
- **la ville se souvient jusqu'au lendemain** : rien ne repousse dans la minute. Ce qu'on a
  cassé reste cassé jusqu'à `nouveauJour()`, et le quartier porte ses blessures — c'est ce
  qui fait qu'une nuit de folie **se voit** le matin.

- ⚠️ **Le décor est bâti une fois.** `grilleFixe` est l'index « qui ne bouge jamais », et
  c'est ce qui le rend gratuit par image. Casser un décor, c'est le sortir de cet index :
  `reindexerDecor` existe, il est rare, et il doit le rester — on réindexe au bris, jamais
  par image. Rien à repeindre dans les morceaux : le décor est une entité, pas une tuile.
- ⚠️ **Casser, c'est un délit.** La taxonomie a déjà « conduite dangereuse +1 » et un témoin
  qui rapporte. Un lampadaire couché en pleine rue, un arbre déraciné dans le parc : la même
  étoile, le même témoin. Sans ça, défoncer devient gratuit, et un char lourd vaut plus
  qu'un char rapide.
- ⚠️ **Le budget.** Les débris sont des entités, donc ils comptent dans le plafond. Un
  plafond de débris par jour, les plus vieux disparaissent en premier — et un test rejoue une
  nuit à tout casser pour vérifier que le rythme tient.
- **Si ça coûte peu** : un poteau qui tombe peut renverser un piéton (la réaction `renverse`
  existe). Sinon, il tombe sans toucher personne, et ce n'est pas grave.
- **Juges** : chaque décor solide déclare s'il arrête ou s'il casse, et sous quel poids ; un
  banc n'arrête jamais un camion, un arbre arrête toujours une berline ; un lampadaire à
  terre a sa lumière éteinte ; un décor cassé est **enjambable** et pas fantôme ; tout est
  debout le lendemain ; et les débris ne dépassent jamais leur plafond.

**Livré le 13 sept. 2026 :**

- **La fiche décide**, comme `vehicules.py` décide ce qu'un char sait faire : `arrete: n` est
  la **masse** au-delà de laquelle ça cède (l'arbre à 2,0 — une berline de 1,0 s'y écrase, un
  camion de 3,0 le déracine), `casse: f` la **fraction de vitesse** qu'on garde en passant au
  travers. Un décor sans l'un ni l'autre reste ce qu'il était : ⚠️ **les feux et les panneaux
  ne se renversent pas**, sinon un croisement se démonte au premier virage raté.
- **Le lampadaire devient solide.** Il était `solide: false` — fantôme pour tout le monde,
  traversé à pied comme en char. Un poteau de deux pixels de rayon qu'on traverse, c'est la
  moitié d'un monde ; un juge qui affirmait le contraire a été retourné.
- ⚠️ **Le rebond se pose dans l'appelant, pas dans `heurterMur`.** Celui-ci ne touche qu'à
  `v.vitesse` — pour les tuiles, c'est `avancer()` qui renverse `vx`/`vy`, axe par axe. Sans
  ça, la berline s'écrasait sur l'arbre **en gardant sa vitesse réelle** et le traversait
  quand même. Ça ne se voit qu'en mesurant la position finale, pas la collision.
- ⚠️ **`debris: true` et `ne: B.t` séparés.** L'image de naissance vaut **zéro** au premier
  instant d'une partie, et `if (e.debris)` laissait alors passer le tout premier morceau
  cassé du jeu. Le genre de bogue qui ne se montre qu'une fois par partie, au pire moment.
- ⚠️ **La ville pose déjà 88 débris à la main** (cour de la fourrière, terrains vagues) : le
  plafond et les juges ne comptent que ceux **nés d'un bris**.
- **La lampe s'éteint avec son poteau** : sa lumière vit dans `carte.lampes`, à part du
  poteau ; casser l'un sans éteindre l'autre donnerait un halo qui flotte au-dessus de rien.
- **Casser est un délit** (`conduite_dangereuse`, avec son témoin) : sans ça, défoncer est
  gratuit et un char lourd vaut plus qu'un char rapide.
- **Le lendemain, tout est debout** — par `nouveauJour()`, pas par un appel à la main : c'est
  le lever du jour qui répare, et c'est ce lien-là que le juge tient.
- ⚠️ **Ce qui n'est PAS fait, et c'est une décision** : un décor cassé n'est pas
  _enjambable_ — il est **traversable**. La fiche voulait de la solidité 3 (comme une
  clôture), mais `enjamber` est une machine à **tuiles** et le décor est une **entité** : lui
  donner l'enjambement demanderait de porter cette machine sur les entités, pour un banc
  couché. Les débris sont donc du décor qu'on foule.
- **Juges (1 neuf, 1 retourné)** : une berline s'arrête sur un arbre et ne passe pas, un
  camion le déracine et passe, un banc cède sous une berline ; le bris laisse des débris et
  n'est plus solide ; déraciner au camion compte un délit ; un lampadaire à terre a sa lumière
  éteinte ; tout casser d'un coup ne dépasse jamais le plafond de débris ; et `nouveauJour()`
  remet **exactement** ce qui était cassé, déblaie et rallume.

### Des sortes de gens, pas des couleurs (**ajout**, taille 3)

_Demande de Martin :_ « je veux plusieurs sortes de personnages non joueurs — des amuseurs
publics, des musiciens de rue, des exhibitionnistes. »

⚠️ **Il y a 24 archétypes, et 4 corps.** Vingt et un portent le corps du joueur avec un
échange de palette. Et sur six `metier`, **deux** déclenchent quelque chose dans le moteur
(`reclame`, `compagnie`) ; les autres sont des nombres — courage, témoin, vitesse. Une
« sorte » est donc aujourd'hui une couleur et trois chiffres, et le plan a déjà payé ce
défaut une fois : les filles de la Brume « n'étaient qu'un échange de palette sur le corps
commun » et on ne les distinguait plus de personne.

**La règle : une sorte = un corps + une routine.** Le catalogue garde ses nombres ; ce qui
fait une sorte, c'est ce qu'elle **fait** que les autres ne font pas. `metier` est le
crochet, il existe déjà — chaque sorte en apporte un, et `majPieton` gagne une routine par
métier au lieu d'une palette par slug.

**Les sortes de Martin :**

- **Le musicien de rue.** Posté à un coin, il joue — et **ça s'entend** : un bruitage court en
  boucle (M15 en a le mécanisme), ducké comme le reste sous une voix. Un chapeau devant lui :
  on y jette une pièce, ou on la lui prend (le pickpocket existe). La foule s'arrête autour
  (l'état `arret` existe pour l'homme-sandwich).
- **L'amuseur public** — mime, jongleur, statue vivante. Il attire un **attroupement**, et un
  attroupement est une **foule de témoins** : faire un coup devant lui, c'est dix témoins
  d'un seul geste. Ce n'est pas du décor, c'est du jeu — l'endroit de la rue où il ne faut
  pas sortir une arme.
- **L'exhibitionniste.** Un imperméable, qu'il ouvre au passage des dames ; elles crient et
  fuient (le cri et `fuit` existent), et **un policier qui passe l'arrête, lui** — la seule
  fois où la police s'occupe de quelqu'un d'autre que le joueur. C'est un gag, et c'est le
  gag qui rend la police crédible : elle n'existe pas que pour toi.

**Et celles qui viennent avec, parce qu'elles servent d'autres fiches :**

- **la contractuelle**, qui met des contraventions — c'est elle qui rend « mal garé »
  **visible** avant que la fourrière ne l'avale ;
- **le jogger**, écouteurs sur les oreilles : il ne témoigne de rien, il ne s'arrête pas ;
- **le touriste**, qui lève la tête devant les enseignes et photographie (un flash) — le
  témoin le plus attentif de la ville, et le plus lent ;
- **l'ivrogne**, qui zigzague, tombe, insulte, et n'a peur de rien — le seul qui ne fuit pas
  devant une arme, ce qui le rend dangereux pour lui ;
- **le pickpocket**, qui vole les autres (M12, la ville coupable d'elle-même) ;
- **la personne âgée**, à la marchette : elle traverse lentement, et les chars attendent
  (les feux pour piétons) ;
- **le facteur**, qui fait sa tournée de porte en porte (les portes s'ouvrent).

**Première vague livrée le 14 sept. 2026** — les trois que Martin a nommées :

- **Trois corps, pas trois palettes.** Chacune a son sprite 12 × 13 (deux colonnes de plus
  que le corps commun, pour le chapeau, le manteau et la guitare) : ⚠️ à douze pixels, c'est
  la **guitare en travers du torse** qui nomme le musicien, le **melon et le visage blanc**
  qui nomment le mime, le **long manteau** qui nomme le troisième. Un juge Python refuse
  qu'une sorte porte le corps d'une autre, ou celui du joueur.
- **Et une routine chacune**, accrochée au `metier` — c'est là que la sorte existe vraiment :
  - le **musicien** et l'**amuseur** tiennent un poste (`vitesse: 0`, comme le marchand
    derrière son kiosque) et **attroupent** les passants autour d'eux ;
  - ⚠️ **un attroupement est une foule de témoins** : les badauds qui regardent un spectacle
    **regardent**, et leur `probaTemoin` monte. Faire un coup devant l'amuseur, c'est dix
    témoins d'un seul geste — c'est l'endroit de la rue où il ne faut pas sortir une arme ;
  - l'**homme au manteau** l'ouvre au passage de quelqu'un : elle crie et fuit. ⚠️ Et **un
    agent qui le voit l'arrête, LUI** — la seule fois où la police s'occupe de quelqu'un
    d'autre que le joueur, et c'est ce gag qui la rend crédible : elle n'existe pas que pour
    toi.
- ⚠️ **Une image imposée, pour un corps qui n'est pas une marche.** Les deux images du manteau
  sont « fermé » et « **ouvert** », pas deux pas — or l'animation choisit son image d'après la
  distance parcourue, et un personnage **immobile** tombe toujours sur l'image zéro. Son geste
  ne se serait jamais vu. `poseFixe` règle ça pour toutes les sortes à venir.
- ⚠️ **Un flâneur fait des pauses tout seul**, et celui qui traînait déjà à côté du jongleur
  restait le seul de la rue à ne pas le regarder : l'attroupement prend aussi les `arret`.
- ⚠️ **Elles ne naissent pas dans la foule** (`frequence: 0`, comme l'homme-sandwich) : on les
  pose aux coins de rue, hors champ, deux de chaque au plus dans la bulle.
- ⚠️ **Un juge de la Brume a dû être réparé, pas contourné** : il comptait **toutes** les voix
  entendues pendant dix secondes pour dire si la fille s'était répétée — donc un bonjour de
  passante passait pour une relance. Ajouter du monde dans la rue l'a révélé. Il ne compte
  plus que les voix **de la Brume**.
- **Juges (2 neufs)** : côté Python, chaque sorte a un corps **à elle**, un métier à elle, et
  ne naît pas au hasard ; au banc, l'amuseur arrête quatre badauds sur quatre **et en fait de
  meilleurs témoins**, le musicien ne quitte pas son coin, le manteau s'ouvre **sur la bonne
  image** pendant qu'elle crie et fuit, et un agent posé à côté le met en fuite avec le bon
  poursuivant.

**Deuxième vague livrée le 14 sept. 2026** — cinq des sept « qui viennent avec ». Le choix
n'est pas arbitraire : ce sont celles dont la routine **se branche sur une fiche déjà
livrée**. La personne âgée attend « des feux pour piétons » (P4) — sans feu, « les chars
attendent » n'a nulle part où s'accrocher — et le pickpocket est logé dans M12.

- **La contractuelle.** Elle repère le char mal garé, **y va** (un état `cap` neuf : flâner
  suit une direction, elle a un endroit où aller), se plante devant et verbalise — un papier
  blanc sous l'essuie-glace, et le HUD le dit. ⚠️ **Elle lit la règle de la fourrière, pas une
  deuxième écrite pour elle** (`Missions.malGare`) : deux règles qui disent « mal garé » se
  contrediraient le jour où l'une bouge, et on verrait une contravention sur un char que
  personne ne remorque. Ce qu'elle change : l'avertissement cesse d'être un message venu de
  nulle part.
- **Le touriste.** `temoin: 1.0` — le seul de la ville. Faire un coup devant lui, c'est se
  faire voir à coup sûr, et il est lent : on ne le sème pas en marchant. Sa routine le rend
  **visible comme témoin** : il s'arrête devant une vitrine, lève la tête, et le flash part.
- **L'ivrogne.** Il zigzague (sa direction est bonne, sa trajectoire ne l'est pas), il tombe
  tout seul, et ⚠️ **il ne fuit pas devant une arme** : il répond. C'est le seul — une rue où
  tout le monde détale de la même façon n'a qu'une réaction, et on cesse de la voir.
- **Le jogger.** Une routine **en creux** : il ne s'arrête jamais, ni pour souffler ni pour
  regarder un amuseur, et `temoin: 0.0`. Ce qu'une sorte ne fait pas la nomme aussi.
- **Le facteur.** De porte en porte, il fait battre le battant — et ⚠️ **il n'entre pas** :
  c'est toute la différence avec le flâneur qui rentre chez lui, celui-là disparaît derrière
  le battant.

⚠️ **Chacune a ses quartiers** (`districts`). Huit sortes qui naissent partout, ce n'est plus
de la variété, c'est de la figuration : on les croise toutes dans la même rue et on cesse de
les voir. Un touriste sur les Quais et pas dans La Shop, un facteur aux Érables et pas au
port — un quartier se reconnaît à ses enseignes, à ses toits, à sa gang, et aussi **à qui y
marche**. Et **une seule** de chaque dans la bulle quand elle marche (deux restent pour les
deux spectacles, qui sont plantés quelque part).

⚠️ **Ce qu'une sorte dit vit en Python** (`pietons.PAROLES`). Le dépôt a payé huit fois « une
fiche que le navigateur ne lisait pas » ; le symétrique coûte aussi cher — un mot écrit en dur
dans `entites.js` est un mot que personne ne peut relire ni juger depuis la source de vérité.

**Trois défauts trouvés par les juges neufs**, et aucun n'était dans la fiche :

- ⚠️ **`e.t % 60` ne tombe jamais.** `majSortes` ne tourne qu'une image sur quinze et `e.t`
  compte depuis la **naissance** : les deux ne coïncident que si l'on est né sur un multiple
  de quinze. Un ivrogne né du mauvais pied n'aurait jamais trébuché de sa vie — et rien ne
  l'aurait dit, parce que « il tombe rarement » et « il ne tombe jamais » se ressemblent
  beaucoup. Chaque routine a maintenant **son compte à elle**.
- ⚠️ **L'homme au manteau ignorait qui était arrêté.** Exactement la leçon déjà payée pour
  l'attroupement (« un flâneur fait des pauses tout seul »), et corrigée à un seul endroit :
  celle qui s'arrêtait pile devant lui était la seule de la rue à ne rien voir.
- ⚠️ **On naissait dans quelqu'un** (corrigé à la fiche des pièces, le même jour) : `placeLibre`
  ne lit que l'index de la foule, et l'index ne se refait qu'une fois par image.

⚠️ **Et un juge d'à côté mesurait la mesure du jour, pas la règle** : « la foule ne se traverse
plus » exigeait moins d'un pixel de chevauchement à **toute** image. Or deux passants qui se
croisent de face se rapprochent de quatre pixels en une image, et la séparation les défait à
la suivante : l'exiger sous un pixel revenait à exiger que personne ne se croise jamais de
face. Il mesure maintenant ce que « se traverser » veut dire — la **durée** d'un chevauchement
(jamais plus d'une image) et **combien** dépassent le pixel (au plus cinq en 960 images) —
et le défaut d'origine (1032 paires, 9,9 px, tenues) le fait rougir des trois côtés.

**Troisième vague livrée le 14 sept. 2026** — trois de ceux qui « gagnent leur vie dans la
rue », prises pour leur **crochet** et pas pour leur costume :

- **Le crieur de journaux** hurle la manchette du Clairon. ⚠️ C'est **ce que tu as fait
  hier** : `journal.py` compare tes statistiques du jour à celles de la veille, et trois
  morts un soir s'entendent crier au coin de la rue le lendemain matin. La boucle la moins
  chère du jeu, et la seule qui te renvoie ton reflet sans passer par un menu. ⚠️ Il **lit**
  `derniereManchette` et ne la recalcule pas : `manchetteDuJour()` remet le compteur d'hier à
  zéro au passage, et un crieur qui l'appellerait effacerait la mémoire du journal à chaque
  cri.
- **Le laveur de vitres** ne s'approche que des chars **arrêtés**, sur la chaussée. Même
  horloge que les feux qu'on vient de livrer : un feu rouge, c'est quinze secondes de
  travail ; un char qui repart le laisse le chiffon en l'air. Sans cette contrainte, il
  laverait des pare-brise à soixante à l'heure — une animation, pas un métier.
- **Le pickpocket** vole **les autres**. ⚠️ **L'argent change de poche pour de vrai** — sinon
  le vol n'est qu'une animation, et fouiller le volé rapporterait quand même. Il aborde
  **dans le dos**, au même angle que le joueur (`pickpocket_dos_degres`, lu dans la fiche),
  la victime crie AU VOLEUR et le désigne **lui** comme menace, et un agent qui passe
  l'arrête. C'est le deuxième après l'homme au manteau, et les deux disent la même chose :
  **la police n'existe pas que pour toi**.

⚠️ **Un défaut qu'on n'aurait pas vu** : le pickpocket marche 10 % plus vite qu'un passant,
donc il gagnait **cinq centièmes de pixel par image** et mettait une minute et demie à
couvrir trente pixels. Il ne volait jamais personne — et de loin, ça ressemblait à quelqu'un
qui suit. Celui qui **rattrape** quelqu'un court (`capVite`).

**Le réservoir** — « je veux plein d'idées ». Chacune avec ce qu'elle _fait_ ; celles qui
n'ont qu'un costume n'y sont pas. On y pige par vagues, jamais tout d'un coup.

- _Ceux qui gagnent leur vie dans la rue_ : le **laveur de vitres** au feu rouge, qui
  s'approche des chars arrêtés, essuie et tend la main — refuser, c'est un pare-brise sale ;
  le **crieur de journaux**, qui hurle la manchette du matin (celle de `journal.py`, donc ce
  que **tu** as fait hier) ; le **distributeur de tracts**, qui te colle un papier — et un
  tract, c'est une chose de plus à ramasser ; le **cireur de chaussures** sur sa caisse ; le
  **chauffeur de taxi** qui attend assis sur son capot, et qui témoigne de tout ce qui se
  passe à son coin ; la **vendeuse de fleurs**.
- _Ceux qui font du bruit_ : le musicien, mais **par instrument** — guitare, accordéon,
  saxophone, et le **joueur de cuillères**, parce que c'est ici ; le **prédicateur** du coin
  qui harangue, et le **fou de la place** ; le **cracheur de feu** la nuit — une lampe qui
  bouge ; une **petite manif** avec ses pancartes, qui bloque un trottoir : une entrave
  piétonne, avec un policier qui la surveille.
- _Ceux qui sont là pour toi_ : l'**arnaqueur au bonneteau** — trois gobelets, on peut
  jouer, on perd, et si on le frappe, ses deux compères sortent de la foule ; le **mendiant**
  qui te suit trois pas et lâche ; le **dealer** au coin, qui ouvre M10 ; le **fan** qui te
  suit quand tu es célèbre, et qui gêne ; le **journaliste** qui débarque après un gros coup
  et photographie — le lendemain, c'est en manchette.
- _Ceux qui font la ville_ : le **brigadier scolaire**, le matin devant l'école, qui arrête
  les chars pour faire traverser les enfants — un char qui ne s'arrête pas, c'est deux
  étoiles ; le **déneigeur** à la pelle devant sa porte, l'hiver ; l'**employé de parc** qui
  ramasse ; le **camion-balai** de nuit, et son gars ; l'**ouvrier de chantier** sur ses
  entraves (M12).
- _Ceux qui ne vont nulle part_ : le **vieux sur son banc**, qui nourrit les goélands ; les
  **enfants qui jouent au hockey dans la rue** — ils crient « CAR ! » et tassent leur but
  quand un char arrive, et **ils sont intouchables**, comme les autres enfants ; le
  **couple qui se chicane** sur un pas de porte ; les **fêtards** qui sortent du bar en
  groupe, bruyants, la nuit — la seule foule qui ne fuit pas tout de suite.
- _Ceux qui te jugent_ : le **badaud qui filme** avec son téléphone — le témoin moderne, et
  la vidéo vaut une étoile de plus si on ne la lui prend pas ; et **la madame au balcon**,
  qui voit tout depuis sa fenêtre : un témoin qu'on **ne peut ni acheter ni rattraper**, et
  la raison de regarder en l'air avant de faire un coup dans une ruelle.

- ⚠️ **Chaque sorte a SON corps, ou elle n'existe pas.** C'est la leçon des filles de la
  Brume. Un corps coûte peu — 12 × 16, quatre directions, trois poses — mais l'atlas et le
  paquet grossissent, et le paquet est à 92 % de son budget brut. Un juge interdit toute
  sorte nouvelle sur `sprite: 'joueur'`.
- ⚠️ **Une routine coûte par image.** Un musicien qui joue est une boucle audio ; dix
  musiciens font dix boucles. Chaque sorte a un **plafond dans la bulle** — un musicien, un
  amuseur, un exhibitionniste à la fois — et c'est ce qui les garde rares, donc remarqués.
- **Elles ont un quartier et une heure.** Le champ `districts` existe (le débardeur ne quitte
  pas les Quais) et le rythme aussi : un musicien au Carré le soir, un touriste sur les Quais
  le matin, un exhibitionniste au parc — et personne de tout ça à La Shop à 3 h.
- **Juges** : toute sorte a son corps ; toute sorte a une routine **mesurable au banc** (elle
  fait quelque chose qu'un passant ne fait pas) ; le musicien s'entend et se tait sous une
  voix ; l'amuseur attroupe (N piétons en `arret` autour de lui) ; l'exhibitionniste finit
  arrêté par un agent qui passe, sans une étoile pour le joueur ; et jamais plus de son
  plafond d'une sorte dans la bulle.

### Les portes s'ouvrent, et les gens les passent (**ajout**, taille 2) — **livré le 13 sept. 2026**

_Demande de Martin :_ « les piétons devraient aussi sortir et entrer dans les commerces.
Profites-en pour aussi faire ouvrir concrètement les portes. »

Les deux demandes n'en font qu'une, et le code dit pourquoi.

⚠️ **Un piéton sur trois SORT déjà d'une porte — et on ne le voit jamais.**
`placeDeNaissance()` tire une porte une fois sur trois, puis refuse la place si elle est
**visible à l'écran** (`if (visibleAEcran(x, y, 24)) continue`). Les gens apparaissent donc
sur un pas de porte **là où l'on ne regarde pas**. Ce n'est pas une sortie, c'est une
naissance déguisée en sortie — et elle ne rapporte rien, puisque son seul intérêt serait
d'être vue.

⚠️ **Et personne n'entre nulle part.** Les piétons disparaissent par oubli, quand ils sortent
de la bulle. La ville a des dedans qui n'avalent jamais personne.

⚠️ **Enfin, une porte ne s'ouvre pas.** Les peintres `D` et `d` dessinent un battant fixe, et
il n'existe nulle part d'état d'ouverture.

**Une porte qui s'ouvre est ce qui rend une sortie crédible**, et une sortie visible est ce
qui justifie qu'une porte s'ouvre. D'où une seule fiche.

- ⚠️ **Une porte animée ne peut pas être une tuile.** Le sol est **cuit dans le morceau** de
  256 px : repeindre un morceau à chaque image pour un battant tuerait le cache qui tient le
  rythme sur téléphone. La porte qui s'ouvre est donc un petit dessin posé **par-dessus**,
  dans la passe des entités, et seulement pour les portes à l'écran — il y en a une poignée.
  C'est la même leçon que les feux pour piétons : le poteau est une entité, la traverse est
  une tuile.
- **Sortir, pour de vrai.** Le piéton naît **dans** la porte (invisible), la porte s'ouvre, il
  avance d'une tuile, elle se referme. La règle « hors écran seulement » saute : c'est
  précisément parce qu'on ne le voyait pas que ça ne servait à rien.
- **Entrer.** Un piéton qui flâne se choisit une porte comme but, marche jusqu'à elle, attend
  qu'elle s'ouvre, disparaît dedans. ⚠️ Ça doit **remplacer une part de l'oubli par
  distance** : sinon la ville se vide toujours de la même façon et on a juste ajouté une
  animation.
- ⚠️ **Toutes les portes n'ont pas le même sens.** `portesFermees` mélange les `d` — portes
  condamnées, les logements — et les `D`, les vraies portes qui mènent à un intérieur. Il faut
  trancher : un logement, oui ; un commerce, **aux heures d'ouverture** (`ouvert()` existe
  déjà) ; le poste de police et l'hôpital, seulement pour qui y travaille ; **la planque de
  Rocco, jamais** — c'est chez le joueur.
- ⚠️ **Et le joueur ne doit pas pouvoir suivre dans le vide.** Une porte condamnée est solide :
  elle ne mène nulle part. Si quelqu'un y entre sous les yeux du joueur, il essaiera d'entrer
  et trouvera un mur — une promesse qu'on ne tient pas. Soit le piéton n'entre que par des
  portes que le joueur peut franchir, soit la porte condamnée **dit** qu'elle ne s'ouvre que
  pour ceux qui habitent là (une poignée, pas d'enseigne, aucune lumière).
- **Le rythme s'en sert.** La nuit vide maintenant la ville pour de vrai ; les portes doivent
  battre au **matin** (on sort) et au **soir** (on rentre), et presque plus la nuit. C'est
  `Monde.rythme(zone)`, qui donne déjà les trois.
- **Juges** : une porte ne s'ouvre jamais sur rien — un piéton qui entre disparaît **après**
  l'ouverture, jamais avant ; la planque du joueur n'avale personne ; un commerce fermé ne
  laisse entrer personne ; le cache de morceaux **ne bouge pas** quand une porte s'ouvre
  (`stats.morceaux` le mesure) ; et le va-et-vient ne fait pas déborder le plafond de piétons.

**Livré le 13 sept. 2026 :**

- **Le battant est une entité de dessin, pas une tuile** : `carte.battants`, une poignée
  d'états, dessinés **par-dessus** le sol dans `Jeu.rendre()`. ⚠️ Le juge mesure
  `stats.morceaux` avant et après une ouverture : le cache ne bouge pas d'un morceau.
- ⚠️ **Redemander une porte déjà en train de s'ouvrir ne la remet pas à zéro.** Un piéton qui
  attend devant appelle `ouvrirPorte` à **chaque image** : le battant restait figé au premier
  pixel et ne s'ouvrait jamais — donc personne n'entrait. Une porte qui se referme, elle, se
  retient ouverte. C'est le genre de bogue qu'on ne voit qu'en regardant la courbe.
- **Sortir** : on naît **dans** la porte, invisible tant qu'elle s'ouvre, puis on avance d'une
  tuile et elle se referme. La règle « hors écran seulement » saute — c'était précisément
  parce qu'on ne le voyait pas que ça ne servait à rien.
- **Entrer** : un flâneur se choisit la porte utile la plus proche, y marche, **attend qu'elle
  soit grande ouverte**, et disparaît — jamais devant un battant fermé. S'il est bloqué par la
  foule une seconde, il renonce plutôt que de piétiner.
- **Quelles portes** : un `d` est un **logement** (toujours) ; un `D` mène à un intérieur — ⚠️
  jamais la **planque** (c'est chez le joueur), ni le **poste**, ni l'**hôpital**.
- ⚠️ **Et le joueur n'est pas trompé.** La fiche laissait le choix ; c'est le **dessin** qui
  tranche, et il était déjà bon : un `D` a une poignée de laiton, un `d` est un battant sombre
  sans poignée, sans enseigne et sans lumière. On apprend à ne pas pousser celle-là.
- ⚠️ **Les intérieurs n'ont PAS d'heures déclarées** — seuls les kiosques de rue
  (`ambulants`) en ont. La **nuit** tient donc lieu de fermeture, avec la seule exception qui
  compte : le **bar**, qui vit justement la nuit. Le jour où `carte.INTERIEURS` portera des
  heures, ces deux lignes deviennent `Missions.ouvert(...)`.
- **Juge (1 neuf)** : le battant monte, tient et redescend tout seul ; le cache de morceaux ne
  bouge pas ; la planque, le poste et l'hôpital n'avalent personne, un logement oui, un
  commerce le jour mais pas la nuit, le bar la nuit ; on naît caché et on sort **visible, en
  plein écran** ; et celui qui entre disparaît avec la porte **à plus de 90 % ouverte**.

**Corrigé le 14 sept. 2026** (retour de Martin : « les portes doivent ouvrir quand j'entre
aussi »). Elles s'ouvraient pour les piétons et **pas pour le joueur** — il traversait un
battant fermé, et c'était d'autant plus voyant que les passants, eux, attendaient poliment.

- ⚠️ **Le piège était dans l'ordre.** Le jeu est **figé** pendant un fondu de porte (`maj()`
  ne fait avancer que la transition) : un battant ouvert juste avant y resterait au premier
  pixel, et la porte serait fermée à l'écran pendant tout le fondu. `Monde.majBattants()`
  tourne donc **aussi** dans la branche de transition — c'est la seule chose qui bouge quand
  tout le reste est arrêté, et elle ne touche qu'à son propre compteur.
- **La porte s'ouvre AVANT de noircir**, pas au noir : la première moitié du fondu se joue
  sur la rue, et c'est là — et seulement là — qu'on peut voir le battant bouger.
- **Au retour, c'est celle de la RUE qui s'ouvre**, et seulement une fois `Monde.restaurer()`
  fait : avant, `Monde.carte` est encore la pièce, et ses battants ne sont pas ceux de la
  ville.
- **Juge (1 neuf)** : il mesure l'ouverture **image par image pendant le fondu**, et n'accepte
  que ce qui se passe tant que la rue est encore visible ; puis la porte de la rue au retour,
  et le fait qu'elle se referme derrière.

### Le carnet : la mission, le journal, le répertoire (**ajout**, taille 2) — **livré le 13 sept. 2026**

_Demande de Martin :_ « je veux pouvoir avoir un rappel de la mission en cours dans le menu.
Un journal et un "bestiaire" avec les personnages connus. »

Une seule entrée au menu Pause — **LE CARNET** — et trois pages. ⚠️ Il n'invente **aucune
donnée** : tout est déjà là, et n'est montré nulle part.

- **EN COURS.** `Histoire.ligneObjectif()` écrit déjà une ligne en haut de l'écran, et
  `Histoire.cible()` pose déjà le point du GPS — mais une ligne de trente caractères ne dit
  ni qui t'a donné ça, ni ce que tu as déjà fait, ni ce que ça paie. La page donne le titre,
  le donneur, **les objectifs faits barrés et celui qui reste**, la récompense promise et où
  c'est. ⚠️ Elle rappelle **ce qu'il faut faire**, elle ne raconte pas l'histoire : quelqu'un
  qui rouvre le jeu après trois jours doit savoir où aller en deux secondes.
- **JOURNAL.** Ce qui s'est passé, en ordre, daté au jour de jeu : missions finies, défis,
  manchettes du matin, arrestations, propriétés achetées, premières fois (le premier char
  volé, le premier boulot). ⚠️ **Il s'écrit tout seul** à partir de ce que le jeu émet déjà
  (`Histoire.evenement(...)`, `p.stats`) — le jour où c'est une deuxième comptabilité à tenir
  à la main, elle dérive de la première et plus personne ne sait laquelle a raison.
- **RÉPERTOIRE** (le « bestiaire »). Les gens qu'on a rencontrés : leur visage — on a déjà
  leurs couleurs de palette dans `missions.PERSONNAGES` et le sprite 12×16 pour le dessiner —,
  leur nom, ce qu'on sait d'eux, et la dernière chose qu'ils ont dite. Les gangs y ont leur
  fiche aussi : `pietons.py` les décrit déjà, avec leur territoire.

⚠️ **Rien ne dit aujourd'hui qu'on a rencontré quelqu'un.** `p.appels` et `p.missionsFaites`
le disent à moitié. Il faut un `p.connus` — un ensemble, écrit la première fois qu'on parle à
quelqu'un. Sans lui, le répertoire affiche des gens qu'on n'a jamais vus, et il **divulgâche
l'histoire** : Josée, le Dr Lachance de M13, Marco qui te vend. Un répertoire qui montre la
fin est pire que pas de répertoire.

⚠️ **Le mot « journal » est déjà pris deux fois dans ce dépôt**, et c'est le genre de
collision qu'on paie six mois plus tard : `journal.py` est **Le Clairon**, la manchette du
matin lue par le narrateur ; M11 prévoit le **carnet du poste**, le dossier de la police sur
toi. La page du joueur s'appelle **JOURNAL**, elle vit dans **LE CARNET**, et les deux autres
gardent leur nom. Trois choses, trois noms — écrit ici pour qu'on arrête de les confondre.

- **La sauvegarde grossit.** `Sauvegarde.completer()` a déjà le repli champ par champ, donc
  une vieille partie sans carnet repart avec un carnet vide plutôt que de planter. Mais une
  partie de dix jours accumule des dizaines d'entrées : le journal est **plafonné** (les
  dernières, plus les jalons qu'on ne jette jamais). Ça compte double en M14, où la partie
  voyage par le réseau.
- **Le vrai travail est à l'écran.** Les menus canvas savent afficher une liste de boutons
  avec un curseur ; une **page de texte qui défile** sur 480 × 270 en police 5×7, c'est autre
  chose. C'est là que va le temps de cette entrée, pas dans les données.
- **Juges** : le rappel de mission dit toujours la même chose que la ligne du HUD et que le
  GPS (trois endroits, une seule vérité) ; le journal ne contient que des événements réellement
  émis, jamais recalculés ; le répertoire ne montre **que** `p.connus`, et un test rejoue une
  partie neuve pour vérifier qu'aucun personnage non rencontré n'y apparaît ; le carnet reste
  sous son plafond après cent jours de jeu simulés.

**Livré le 13 sept. 2026 :**

- **Le défilement manquait à TOUS les menus**, et c'est ce qui bloquait la page de texte
  annoncée plus haut. `dessinerMenu` dessinait ses items du premier au dernier : au-delà de
  quatorze lignes, ils sortaient de la boîte. Une **fenêtre** suit maintenant le curseur, avec
  deux petites flèches. ⚠️ Elles sont **dessinées**, pas écrites : la police pixel n'a que des
  lettres, des chiffres et un peu de ponctuation — un « ▲ » y tomberait sur un « ? », comme
  les accents avant qu'on les normalise. ⚠️ Et un menu qui tient au complet ne change pas
  d'allure : le calcul rend exactement son nombre d'items tant que la hauteur ne bute pas sur
  l'écran.
- **`m.retour`** : sortir d'une page recule d'un cran au lieu de rendre la main au jeu. Sans
  ça, quitter le JOURNAL relançait la partie et il fallait remettre PAUSE pour lire la page
  d'à côté.
- **EN COURS** donne le donneur, la récompense, **tous** les objectifs — celui du moment
  marqué d'un chevron, les faits d'un point — et **où**. ⚠️ « Barré » n'existe pas en 5×7 :
  on marque et on éteint, et `actif: false` grise le reste.
- **JOURNAL** : le plus récent en haut, daté au jour de jeu. ⚠️ Il s'écrit depuis ce que le
  jeu **émet déjà** — `Histoire.evenement('mort')` et `('arrete')` sont les mêmes émissions
  qui font échouer une mission ; il n'y a pas deux endroits qui décident qu'on est allé à
  l'hôpital.
- **RÉPERTOIRE** : `p.connus`, écrit à la **première parole** (`Histoire.parler`), et sa fiche
  cuit le visage avec **ses** couleurs de palette — les mêmes que celles de son sosie dans la
  rue, rien de neuf à dessiner.
- **Le plafond** jette le quotidien **avant** les jalons, et quand il n'y a plus que des
  jalons, ils cèdent aussi : rien ne grossit sans fin, ce qui comptera double en M14.
- ⚠️ **Ce qui manque encore au journal** : les manchettes du matin et les propriétés
  achetées. Elles s'émettent dans `missions.js`, qu'une autre session réécrivait au même
  moment — c'est **une ligne chacune** le jour où ce fichier est libre (`Histoire.noter(...)`
  est exporté pour ça).
- **Juges (3 neufs)** : la page EN COURS dit la même mission que `ligneObjectif()` **et** que
  `cible()` (trois endroits, une seule vérité) et barre exactement les objectifs faits ; le
  journal retient une mission réussie, une arrestation et un séjour à l'hôpital **sans qu'une
  ligne du carnet ne les déclenche**, reste sous son plafond après 300 entrées et n'y perd
  aucun jalon ; le répertoire est **vide** dans une partie neuve, ne prend Ti-Guy qu'après lui
  avoir parlé, ne le prend **qu'une fois**, et sa fiche dessine bien un visage.

### Les véhicules vus de profil, comme les piétons (**correctif**, taille 5)

_Demande de Martin :_ « une refonte complète des véhicules. Je les veux comme les piétons,
de profil. »

**Tout ce qui est debout dans Bandini est dessiné debout — sauf le char.** Le passant fait
12 × 16 et il est ancré à ses **pieds** (`ancre: [6, 15]`) ; l'arbre fait 18 × 26, le tronc
en bas ; le lampadaire, 8 × 30 ; le banc se voit de côté, avec ses pattes ; le feu de
circulation a son poteau (13 × 24) ; et les clôtures nord-sud ont été refaites **vues par la
tranche** le 13 septembre, parce que Martin l'a demandé en disant déjà exactement ça. La
ville, elle, est un **sol** : de l'asphalte, des toits, et l'ombre d'un mur qui tombe vers le
sud. Le char est la **dernière chose que le jeu regarde d'aplomb** — et le code le dit
lui-même, en toutes lettres, dans M9 : « Vu d'en haut, un char est un TOIT (…) ce n'est pas
le pare-brise qui nomme un véhicule à douze pixels de large, c'est ce qu'il porte sur le
dos. » C'était vrai. Ça cesse de l'être le jour où on ne le regarde plus d'en haut.

⚠️ **C'est un correctif, pas un ajout** : rien de neuf n'apparaît dans le jeu. Les mêmes
douze véhicules, redessinés pour qu'ils regardent dans le même sens que tout le reste.

**Mesuré avant d'écrire :**

- **12 véhicules, 32 variantes de couleur, 1 900 lignes** de grilles de pixels dans
  `sprites.js`. C'est ça qu'on jette et qu'on redessine.
- Le char tourne par **32 caps cuites** (`Atlas.cuireRotations`), une tous les 11,25°. Le
  parc entier, cuit, pèse **1 024 canevas — 6 Mo**.
- Et il ne s'en sert presque jamais : sur **3 129 relevés** de chars en marche (600 images de
  trafic), **94,5 % sont à moins de 2° d'un cap cardinal**, 97 % à moins de 10°. La rotation
  libre coûte six mégaoctets pour **3 % du temps**.

**La règle : une vue = un dessin, pas une rotation.** Le char choisit sa pose comme le
passant choisit sa face — `regarder()` tient déjà la règle en une ligne
(`Math.abs(dx) >= Math.abs(dy)`). Trois dessins par véhicule : **de profil** (miroité pour
l'autre sens), **de dos** (il s'éloigne), **de face** (il vient). L'atlas tombe de 1 024 caps
à **96**, et de 6 Mo à **0,3 Mo**.

**⚠️ Et voici ce que ça coûte, dans l'ordre où ça fait mal.**

1. ⚠️ **Le dessin cesse de dire l'encombrement.** Un char fait 28 px de long ; de profil, ces
   28 px se voient. **De dos, non** : il devient un objet de 14 px de large, et ses 28 px
   d'asphalte disparaissent de l'écran. Or se garer dans une case, juger l'espace entre deux
   chars, reculer dans une ruelle, tout ça se joue **à l'œil**. C'est le vrai prix de la
   demande, et il se paie en jeu, pas en pixels. Deux parades, à décider :
   - **l'ombre au sol permanente**, à l'empreinte exacte du catalogue, sous tous les chars,
     tout le temps — elle n'existe aujourd'hui qu'en vol (`v.z > 0`). Dix lignes, et elle
     rend à l'œil la longueur que le dessin ne montre plus ;
   - le **trois-quarts** au lieu du profil pur pour les vues de dos et de face : on voit
     alors un bout du toit qui fuit, donc un bout de la longueur.
   - **Recommandation : les deux, l'ombre d'abord** — c'est elle le filet, et elle se mesure.
2. ⚠️ **L'ancre change de sens.** Un char est cuit **centré** (`ancre: [16, 8]`) ; un passant
   est ancré à ses pieds, et c'est ce qui le pose au sol et le trie par y (`y de tri = y`,
   `y de dessin = y - z`). Un char debout s'ancre pareil, à sa ligne de sol, sinon il flotte.
   Ça touche le tri, l'ombre, le saut de rampe, et **la remorqueuse**, qui pose sa charge au
   pixel et dans l'axe.
3. ⚠️ **Les 3 % obliques sont exactement les virages** — le seul moment où l'on regarde
   vraiment un char tourner. Trois poses y font donc un **saut**. Le passant a le même défaut
   et personne ne le voit : il tourne en un pas, le char met une seconde et demie. Les
   parades, par prix croissant : accepter le saut ; ajouter deux poses de trois-quarts (**5
   poses, 160 caps, 0,5 Mo**) ; ou **pencher** le dessin de quelques degrés pendant le virage
   — ⚠️ mais au-delà d'une quinzaine de degrés, un profil penché redevient une vue d'en haut
   de travers, et on a refait le problème qu'on venait de régler.
4. ⚠️ **Le char sera TRAPU, et il faut le vouloir.** Le passant est dessiné à **9,1 px/m**
   (16 px pour 1,75 m) ; le char à **6,2 px/m** (28 px pour 4,5 m). À l'échelle du passant,
   un toit d'auto (1,45 m) fait **13 px de haut pour 28 px de long** — un vrai char en ferait
   41 de long. **On ne peut pas l'allonger : c'est la rue qui tient la longueur** (les voies,
   les cases de stationnement, les lignes d'arrêt, tout le trafic). Donc un char court et
   haut, comme dans les jeux de petites autos. Et un passant plus grand que le toit d'une
   auto, ce qui est vrai dans la vie.
5. ⚠️ **Les quatre dessins de M9 sont à jeter**, et c'est le gros du travail. Le camion,
   l'autobus, l'ambulance et la remorqueuse ont été dessinés **pour être des toits** : les
   nervures de la caisse, les trappes, la croix rouge, le bras de levage. De profil, ce qui
   nomme un véhicule est sa **silhouette** — la caisse haute, les fenêtres en bande de
   l'autobus, le gyrophare, le bras qui dépasse à l'arrière.
6. ⚠️ **Le conducteur cesse d'être peint dans le véhicule, et c'est un cadeau.** La palette du
   vélo porte déjà une peau (`s`) et des cheveux (`h`) : le cycliste est **cuit dans le
   vélo**, de la même couleur pour toujours. De profil, il redevient ce qu'il aurait dû être
   — un passant **assis dessus**, avec ses propres couleurs, ce qui applique aux deux-roues
   le correctif des « sortes de gens ». Et dans une auto, on verra enfin **une tête derrière
   la vitre**.
7. ⚠️ **L'épave et le vélo plié se servent de la rotation libre** pour dire « il est tombé »
   (`v.angle += (rng - 0.5) * 1.6`). Debout, ça demande une pose de plus : **couchée** —
   exactement ce que le passant a déjà (`couche` : une image, pas un canevas qui tourne).
8. ⚠️ **La physique ne bouge pas d'un pixel**, et c'est ce qui rend la fiche faisable :
   `cercles()`, les masques, les voies, les cases de stationnement, le crochet, les défonces,
   le trafic — tout continue de voir un rectangle vu d'en haut. On ne touche **qu'au
   dessin**. En revanche, les juges qui mesurent des **pixels** changent (l'ombre en vol, le
   « nez » du char) ; ceux qui mesurent des **positions** — la charge de la remorqueuse collée
   et dans l'axe — tiennent tels quels.
9. ⚠️ **Ça se fait AVANT d'ajouter des véhicules.** M12 promet un tramway et un traversier, et
   le bateau attend son sprite en dette. Chaque véhicule dessiné avant la refonte se dessine
   deux fois.

**Juges** : chaque véhicule a ses trois poses, aucune manquante et aucune empruntée à un
autre ; la pose suit le cap avec **la même règle que la face d'un passant** (un seul code,
pas deux jeux de seuils) ; l'ancre est la ligne de sol, mesurée — un char au sol ne flotte
pas d'un pixel ; l'ombre au sol a l'empreinte du catalogue, pour tous les chars, tout le
temps ; le tri par y met le char devant le passant qu'il dépasse et derrière celui qu'il
croise ; une épave et un vélo plié ont leur pose couchée ; la remorqueuse pose toujours sa
charge au pixel et dans l'axe ; et **l'atlas du parc entier reste sous 0,5 Mo** (mesuré :
6 Mo aujourd'hui).

### Le trottoir et les traverses font deux tuiles, ils devraient en faire une (**correctif**, taille 2)

_Demande de Martin :_ « les trottoirs ne devraient être que d'une tuile de large », et
« les traverses de piéton devraient aussi être d'une tuile ».

`TROTTOIR = 2` depuis M1, et il se voit : 32 px de trottoir contre une rue de deux voies, ce
n'est pas une proportion de ville, c'est une promenade. ⚠️ **Mais cette constante ne décore
rien — elle construit.** `_coupe()` la lit pour découper _chaque_ rue, et tout le reste en
découle. Il faut donc dire d'avance ce que ça déplace, parce que ça déplace la ville entière.

**Le choix à faire, et il n'y en a que deux.** Une rue fait `largeur - 2 × TROTTOIR` voies.
Passer le trottoir à 1 sans rien d'autre transforme une **rue de 6 en quatre voies** et un
boulevard de 8 en six. Donc :

- soit **les rues rétrécissent de deux tuiles** (rue 6 → 4, boulevard 8 → 6) et le nombre de
  voies ne bouge pas — la ville perd environ 10 % de sa largeur et de sa hauteur, et c'est
  l'option qui respecte la demande sans toucher au trafic ;
- soit **on garde les largeurs** et chaque rue gagne deux voies — ce qui refait le trafic, le
  déport dans la voie d'à côté, les feux et les lignes d'arrêt. Ce n'est pas ce qui a été
  demandé.

**Les traverses suivent toutes seules — c'est la même constante.** Au croisement, la bande
de passage piéton fait exactement `TROTTOIR` tuiles de profond : c'est l'endroit où la
chaussée traverse la ligne du trottoir. La demande de Martin sur les traverses n'est donc pas
un deuxième chantier, c'est la **preuve que le premier est le bon** — le trottoir et sa
traverse sont le même nombre, et ils doivent le rester.

- ⚠️ **Mais le 2 est écrit en dur dans le JS**, et c'est le piège qui mordra. `monde.js` range
  les tuiles d'un croisement avec `inter.y - 2` et `inter.x - 2` — deux littéraux — « pour
  inclure les passages piétons, deux tuiles de chaque côté ». Le paquet transporte pourtant
  déjà `grille.trottoir`. Le jour où `TROTTOIR` passe à 1, Python dessinera des traverses
  d'une tuile et le JS continuera d'en réclamer deux : un piéton demanderait à quel feu obéir
  en se tenant sur la chaussée, et un char lirait un croisement là où il n'y en a plus. **Ce
  littéral doit lire le paquet avant qu'on touche à la constante.**
- ⚠️ **Une traverse d'une tuile est une porte de 16 px pour tout un coin de rue.** Les piétons
  ne traversent qu'aux passages, et un char cède à celui qui est engagé dessus
  (`priorite_pieton_px`). En file indienne, à un coin passant, ça peut faire attendre un char
  pour chaque piéton, l'un après l'autre. C'est la même question que la foule sur un trottoir
  d'une tuile, et elle se tranche en même temps.

⚠️ **Ce qui vivait sur le trottoir doit déménager**, parce qu'il n'y aura plus qu'une tuile et
que tout s'y bouscule déjà : les lampadaires, les bornes-fontaines, les kiosques et roulottes
(`_places_ambulantes` cherche du `.`), les enseignes qui pendent au-dessus, et surtout la
**réserve de deux tuiles devant chaque porte** posée par `poser_porte` — avec un trottoir
d'une tuile, la deuxième réservée tombe sur la chaussée. Chacun a besoin d'un chez-soi
explicite : contre le mur pour les lampadaires et les bornes, dans un élargissement de coin
ou sur une place pour les ambulants, et une seule tuile réservée devant les portes.

⚠️ **Et la foule.** Un personnage fait 12 px de large ; une tuile en fait 16. Deux piétons ne
se croisent donc plus sur un trottoir d'une tuile — or la règle du jeu est qu'**un piéton ne
pose pas le pied sur la chaussée**. Il faut trancher : ou bien les piétons acceptent de se
frôler (la foule se démêle déjà, `demeler()`), ou bien le trottoir s'élargit là où il y a du
monde. Sans décision, on obtient des bouchons de piétons devant chaque commerce.

- ⚠️ **Toutes les graines changent.** Ce n'est pas un réglage : c'est une ville redessinée.
  Les positions sauvegardées se rattrapent déjà par l'empreinte du catalogue (M8 l'a fait une
  fois), et tous les juges de géométrie se rejouent — connexité forte des voies, un seul îlot
  marchable, les croisements, les lignes d'arrêt. **C'est exactement à ça qu'ils servent**, et
  c'est ce qui rend ce changement possible sans y passer la semaine.
**⚠️ Essayé le 14 sept. 2026, et ANNULÉ par Martin en cours de route.** Ce que la tentative
a appris — et qui vaut plus que le code qu'elle a produit :

- **Les deux questions ouvertes de la fiche sont tranchées**, par Martin, pendant l'essai :
  1. « on laisse les gens se **croiser** » — pas d'élargissement du trottoir pour la foule ;
  2. « on **agrandit les terrains et non les rues** ; les gens peuvent passer sur le nouveau
     terrain ainsi créé » — ⚠️ **c'est une troisième option, que la fiche n'avait pas vue** :
     les deux tuiles libérées par chaque rue ne reviennent ni aux voies ni au néant, elles
     vont au **bloc**, et sa bordure devient un abord **marchable**. La ville garde sa taille,
     le nombre de voies ne bouge pas, et la largeur où l'on marche reste la même (1 trottoir +
     1 abord) — ce qui règle du même coup les bouchons de piétons ;
  3. « mais **priorité de marcher sur le trottoir** » — l'abord est un débordement, pas un
     deuxième trottoir : le flâneur préfère la dalle.
- **Le littéral du JS est un vrai prérequis, et il se corrige seul.** `monde.js` rangeait les
  tuiles d'un croisement avec `inter.y - 2` / `inter.x - 2` alors que le paquet transporte
  `grille.trottoir`. Ça se change en cinq lignes, **avant** de toucher à la constante, et ça
  ne casse rien — c'est le premier pas de la prochaine tentative.
- **Le coût réel, mesuré** : avec `TROTTOIR = 1` et les rues rétrécies, **neuf juges rougissent
  d'un coup** — poches de barbelé, ossature d'une autre graine, arbres dans les sentiers,
  enseignes des lieux garantis, foule qui se traverse, passages piétons, vélo du cycliste,
  homme-sandwich à son poste. ⚠️ Ce n'est pas un défaut des juges : **c'est exactement à ça
  qu'ils servent**, et c'est la mesure honnête de ce que « redessiner la ville » veut dire.
  La prochaine tentative doit prévoir de les rejouer **un par un**, pas de tout faire passer
  d'un coup.

- **Juges** : la largeur de la ville suit toujours sa trame (`somme(COLONNES) + somme(RUES)`) ;
  une rue garde deux voies et un boulevard quatre ; aucune tuile réservée ne tombe sur la
  chaussée ; aucun kiosque, aucune borne et aucun lampadaire ne bouche la seule tuile de
  trottoir devant une porte ; et **aucune largeur de trottoir n'est écrite en dur** — ni en
  Python ni en JS, le paquet est la seule source (un test lit les deux).

### Une pièce plus grande que sa maison (**correctif**, taille 2) — **livré le 14 sept. 2026**

_Demande de Martin :_ « les intérieurs ne devraient pas être plus petits que l'extérieur. »

⚠️ **Mesuré : les 41 intérieurs de la ville sont plus grands que le bâtiment qui les
contient. Les 41.** Et parfois de façon spectaculaire :

| Lieu | Bâtiment | Intérieur |  |
|---|---|---|---|
| Un logement de banlieue | 3 × 3 | 16 × 9 | **seize fois** la surface |
| Dépanneur Chez Ti-Paul | 4 × 3 | 15 × 10 |  |
| Kiosque de Mme Thibodeau | 4 × 3 | 11 × 7 |  |
| Garage Rocco Bandini | 7 × 3 | 17 × 10 |  |
| Hôpital de Baie-des-Brumes | 6 × 5 | 17 × 10 |  |
| Usine Prévost | 16 × 10 | 17 × 10 | le moins pire, et il déborde encore |

La cause est simple : les deux côtés ne se parlent pas. `_pose_batiment()` tire ses marges au
sort et donne au bâtiment la taille qui reste dans sa parcelle ; `INTERIEURS` déclare des
pièces écrites à la main, toutes autour de 14 × 9. **Personne ne compare les deux**, et le
joueur, lui, compare à chaque porte.

**La règle, et elle tient en une phrase** : une pièce ne dépasse jamais l'empreinte de son
bâtiment. ⚠️ Avec la nuance que les étages viennent d'apporter : un bâtiment de N étages peut
contenir **N pièces de son empreinte**, jamais **une pièce N fois plus grande**.

Ce qui suit de la règle :

- **Une porte impose une taille minimale à son bâtiment.** `poser_porte()` dégage déjà le
  devant d'un bâtiment garanti — « un bâtiment garanti DOIT s'ouvrir ». On y ajoute : il doit
  être **assez gros pour ce qu'il contient**. C'est le côté le plus facile à corriger, et
  celui qui rend les commerces reconnaissables **de la rue**.
- **Et il faut de petites pièces.** Un bungalow de 4 × 3 ne s'ouvrira jamais sur un 16 × 9 —
  il lui faut une pièce de bungalow. Les intérieurs ne peuvent plus être une taille unique
  déguisée : il en faut par tranche, et la porte prend la plus grande **qui tienne**.
- ⚠️ **On compare les planchers, pas les boîtes.** Une pièce de 15 × 10 a 13 × 8 tuiles de
  plancher une fois ses murs déduits ; un bâtiment de 4 × 3 en a douze en tout. C'est le
  plancher contre l'empreinte qui dit la vérité, et c'est lui que le juge mesure.
- ⚠️ ~~**Ça se joue avec le trottoir.**~~ **Plus maintenant** (14 sept. 2026). La fiche
  disait d'attendre le trottoir, parce que rétrécir les rues rétrécirait les parcelles donc
  les bâtiments. Or Martin a tranché autrement : les tuiles libérées vont **aux terrains**,
  pas aux rues. Les bâtiments ne peuvent donc que **grossir** — une pièce qui tient
  aujourd'hui tiendra encore demain, et l'ordre s'inverse : celle-ci peut passer la première.
- **Juges** : pour chaque porte, le plancher de la pièce tient dans l'empreinte du bâtiment
  × son nombre d'étages ; aucun bâtiment portant une porte ne descend sous la taille de sa
  plus petite pièce ; et le juge tourne **sur cinq graines**, parce que c'est le tirage des
  marges qui crée l'écart.

**Livré le 14 sept. 2026.** Les deux côtés se parlent, et c'est `interieur_qui_tient()` qui
les fait parler : `_pose_batiment()` retient désormais l'**empreinte** de ce qu'il vient de
poser (`len(tuiles)` — pas la parcelle, qui ment de trois fois la surface), et la porte
choisit **la plus grande pièce qui tienne dedans**.

- **Quatre petites pièces neuves.** `logement_minuscule` et `boutique_minuscule` (9 tuiles
  de plancher : trois sur trois, un lit et un poêle, ou un comptoir), `logement_petit` (18)
  et `boutique_petite` (21). ⚠️ **Il fallait descendre jusqu'à neuf** : vingt-sept bâtiments
  ordinaires de la graine livrée ne font que neuf tuiles, et sans cette taille-là leurs
  portes restaient toutes condamnées — la ville perdait un tiers de ses entrées.
- **Vingt-six pièces redessinées plus petites** : les douze lieux garantis (le garage passe
  de 17 × 10 à 10 × 7, l'hôpital de 17 × 10 à 11 × 8, le kiosque de 11 × 7 à 6 × 5), les dix
  boutiques de famille (14 × 9 → 9 × 8) et les deux logements. Tous leurs points d'action,
  leurs commis et leurs clients ont suivi — c'est `_piece()` qui le vérifie, au chargement
  du module.
- **La parcelle d'un lieu garanti se taille à la mesure de sa pièce**, et avant le
  découpage. Lui demander ensuite « la plus grosse parcelle » revenait à espérer que le
  hasard ait fait un terrain de la bonne taille : le garage Bandini se retrouvait sur
  vingt-sept tuiles pour une pièce qui en veut cent vingt. ⚠️ Et **le reste de sa bande fait
  un seul bâtiment** : le découpage récursif laissait entre ses parcelles des cours de deux
  tuiles que le lieu garanti — qui n'a plus de marge — refermait, jusqu'à **quarante-six
  tuiles enclavées** à murer sur une graine.
- **Chaque famille de commerce ouvre au moins une porte** (`premiere_du_genre`). Il fallait
  qu'un bâtiment tire cette enseigne-là, qu'il soit assez grand, **et** qu'il gagne le dé :
  trois chances qui se multiplient, et quatre familles sur dix restaient des couleurs
  d'enseigne qui ne mènent jamais à rien. Le dé décide du **nombre** de portes qui s'ouvrent,
  pas de l'existence d'un pan entier de la ville.
- ⚠️ **L'identité d'un commerce voyage sur la PORTE, pas dans les murs.** La petite boutique
  est la même pour les dix familles : une boucherie de neuf tuiles reste une boucherie sur
  son enseigne et dans le carnet, elle a juste un comptoir au lieu de trois allées.
- **Mesure.** Avant : 35 portes sur 45 débordaient (34 à 46 selon la graine), la pire de
  onze fois. Après : **zéro**, sur cinq graines — et la ville garde ses portes (53 contre 45,
  parce que les petites pièces en ouvrent plus qu'elles n'en condamnent).
- **Douze juges**, dont un par graine sur les deux moitiés de la règle : aucune pièce ne
  dépasse son bâtiment, **et** les petites pièces servent pour de vrai — condamner les
  quarante portes serait, sinon, une façon de ne jamais mentir.

⚠️ **Trois juges d'à côté sont tombés avec la ville, et aucun ne mesurait ce qu'il croyait**
— ils tenaient par la position du décor, pas par une règle :

- `la bagarre tient le budget` exigeait 30 piétons actifs quand le budget des flâneurs
  (`MAX_PIETONS`) en vaut 22 **et** que douze vendeurs de kiosque naissent avec la ville sans
  jamais dormir : 34 au minimum, arithmétiquement. Il ne tenait que tant que le singe ne
  traversait pas un quartier dense. Il mesure maintenant les flâneurs et la figuration
  séparément.
- `la pizza refroidit` comparait **deux tournées différentes** (les clients se tirent autour
  de la moto) : trois livraisons froides à l'autre bout de la ville paient plus, en distance,
  que trois chaudes à côté. Il juge maintenant la **prime**, qui ne dépend que du chrono.
- `l'homme-sandwich se tait` exigeait qu'il **remarche** ensuite ; un piéton à poste s'arrête
  tout seul une fois sur trois. Il juge maintenant qu'il a fini son boniment et fermé sa
  bulle.

Et **deux vrais défauts** sont tombés avec eux :

- **On naissait dans quelqu'un.** `placeLibre` ne lit que l'index de la foule, et l'index ne
  se refait qu'une fois par image : deux naissances dans la **même** image ne se voyaient pas
  l'une l'autre. `peupler()` posait un passant, `Police.peuplerAgents()` regardait un index
  d'où il manquait, et l'agent naissait dessus **au pixel près** (9 px de chevauchement pour
  deux corps de 10). Seuls `peuplerDabord` et les hommes-sandwichs indexaient leurs
  naissances ; c'est maintenant **la naissance elle-même** qui le fait, pour tout le monde.
- **Le tremplin des Skateux tenait par chance.** « Dans La Pointe, il y en a un à tout coup »
  disait le commentaire, trois lignes au-dessus d'un code qui n'essayait **qu'une** allée, et
  seulement sa tuile du milieu — arrondie vers le fond, celle qui longe le grillage du voisin
  et n'a aucun élan. Cinq tuiles de décalage du terrain, et La Pointe n'avait plus de
  tremplin. On essaie maintenant toutes les allées, leurs deux tuiles, et toutes les
  positions le long de l'allée — les meilleures d'abord, les recours **après**, pour ne pas
  déplacer un tremplin qui tient très bien.

### L'intérieur à la mesure du bâtiment (**correctif**, taille 3) — **livré le 14 sept. 2026**

_Demande de Martin :_ « je veux que l'intérieur de bâtiment soit proportionné à l'extérieur,
tu avais mal compris. »

⚠️ **La fiche du dessus n'a tenu que la moitié de la promesse.** « Une pièce plus grande que
sa maison » a posé une **inégalité** — le plancher ne dépasse jamais l'empreinte — et une
inégalité se satisfait très bien d'une pièce minuscule dans un immeuble immense. Mesuré sur
la ville livrée, aujourd'hui :

| Dehors | Dedans | |
|---|---|---|
| 59 × 8 (328 tuiles) | 9 × 8 (42 de plancher) | **13 %** |
| 58 × 7 (380) | 14 × 9 (84) | 22 % |
| 35 × 5 (153) | 17 × 10 (120) | la pièce est **deux fois plus profonde** que le bâtiment |
| 14 × 4 (56) | 11 × 8 (54) | la surface est juste, et il y a **six tuiles de profond dans un bâtiment qui en fait quatre** |

Médiane du rapport plancher / empreinte : **0,64 à 0,75** selon la graine. Et la **forme** ne
suit jamais : les pièces dessinées font toutes autour de 9 × 8, les bâtiments vont de 3 × 3 à
59 × 8.

**La règle, et elle remplace celle d'hier** : _la pièce a les **mesures** de son bâtiment._
Son plancher fait la boîte de ce qu'on voit de la rue — large et plat dehors, large et plat
dedans — et jamais plus de tuiles que l'empreinte.

Deux décisions de Martin, le 14 sept. :

1. **« les mesures du bâtiment »**, pas seulement la surface ;
2. **une longue façade se découpe en plusieurs vitrines** : soixante tuiles de large, ce
   n'est pas un commerce, c'est une **rangée** de commerces — chacun sa porte, son enseigne
   et sa pièce à sa mesure.

Ce qui suit de la règle :

- **La façade se découpe en vitrines.** Une bande de façade se coupe en segments de la
  largeur d'un commerce ; chaque segment tire son enseigne, sa famille et sa porte, et
  **possède les tuiles de bâtiment au-dessus de lui** — c'est sa part de l'empreinte, et
  c'est elle qui donne les mesures de sa pièce. Un bâtiment en L ou en U se partage tout
  seul, colonne par colonne.
- **La pièce se pose à la mesure.** Trois tailles dessinées ne peuvent pas couvrir des
  bâtiments qui vont de neuf tuiles à trois cent quatre-vingts, dans toutes les formes. Les
  commerces et logements **ordinaires** se posent donc à la mesure de leur part, meublés par
  **famille** (l'épicerie a ses frigos et ses allées, l'atelier ses machines, le logement son
  lit et son poêle) — la famille dit **quoi**, la mesure dit **combien**.
- ⚠️ **Les seize lieux garantis gardent leur plan dessiné à la main** : le billard du bar, les
  lits de l'hôpital et les ponts du garage ne se génèrent pas. C'est leur **bâtiment** qui se
  taille à eux — en largeur **et** en profondeur, alors qu'hier seule la surface était visée
  (la cantine se retrouvait dans 58 × 7).
- ⚠️ **On compare toujours les planchers**, et la convention d'hier tient : le plancher d'une
  pièce fait la **boîte** du bâtiment (une cabane de 3 × 3 ouvre sur 3 × 3 de plancher, donc
  une pièce de 5 × 5 murs compris). Les murs de la pièce sont ceux du bâtiment.
- ⚠️ **La ville va bouger** : tailler les parcelles des lieux garantis change le nombre de
  tuiles de façade, donc le nombre de tirages, donc la suite du hasard. C'est arrivé hier
  pour la même raison ; les juges de géométrie sont là pour ça et se rejouent tous.
- ⚠️ **Le mur ne bouge pas pour une porte.** Les vitrines, les portes et les pièces sont une
  **couche peinte** : elles tirent leurs décisions du dé des devantures, jamais du dé commun
  (celui qui pose les murs). Une porte de plus ne déplace pas un bâtiment à l'autre bout de
  la ville.
- **Juges** : pour chaque porte et sur cinq graines, le plancher de la pièce a **les mesures**
  de sa part de bâtiment (et plus seulement « pas plus ») ; chaque pièce **posée** passe les
  mêmes juges que les pièces dessinées (une porte, plancher d'un seul tenant, points
  atteignables qui ne volent pas la porte, un dixième de meubles au minimum, lits en blocs qui
  ne se touchent pas) ; et une longue façade porte **plusieurs** enseignes.

**Livré le 14 sept. 2026.** Sur cinq graines, **toutes les portes** : le plancher de la pièce
fait **exactement** la boîte du bâtiment qu'on voit au-dessus de sa vitrine — largeur ET
profondeur, à la tuile près. Mesuré avant : rapport médian **0,64 à 0,75**, le pire à
**0,07**.

- **Une vitrine, un commerce, une pièce.** `decouper_la_facade()` coupe la rangée de façade
  en morceaux de **huit tuiles** (la largeur d'un magasin de rue : une enseigne, une porte,
  deux vitrines), et chaque morceau **possède les tuiles de bâtiment au-dessus de lui** —
  c'est sa part, et c'est elle qui donne les mesures de sa pièce. Un bâtiment en L ou en U se
  partage tout seul, colonne par colonne. ⚠️ **Sauf un entrepôt** : un hangar est une seule
  affaire, sa façade porte un nom et une porte, et derrière il y a un entrepôt de toute sa
  largeur. Le découper en sept magasins aurait inventé une rue commerçante dans La Shop.
- **La pièce se POSE.** `piece_de_commerce()` et `piece_de_logement()` construisent un plan à
  la mesure et le font passer par `_piece()` — même validation que les plans dessinés, donc
  une pièce impossible lève **pendant la génération**. Un commerce, c'est trois rangées qui
  ne changent jamais (le **fond** contre le mur du fond, le **comptoir** à l'avant-dernière,
  la dernière **libre** — c'est celle où l'on entre) et une **allée une rangée sur deux** ;
  un logement, c'est des **coins meublés** de deux tuiles sur deux, tous les cinq tuiles.
- ⚠️ **Les dix boutiques dessinées d'hier sont supprimées**, avec les deux logements et les
  quatre petites pièces : elles répondaient à la règle d'hier par des **tailles**, et trois
  tailles ne couvrent pas des bâtiments qui vont de 9 à 380 tuiles dans toutes les formes. Ce
  qu'elles disaient de bon — une épicerie a des frigos et des allées, une taverne des tables,
  un atelier des machines — est passé dans **`MOBILIER`**, dix palettes de deux motifs. **La
  famille dit quoi, la mesure dit combien.** Les **seize lieux garantis** gardent leur plan
  dessiné à la main : le billard du Brouillard et les lits de l'hôpital sont des endroits,
  pas des gabarits.
- **Et leur bâtiment se taille à eux**, en largeur **et** en profondeur — hier seule la
  surface était visée, et la cantine se retrouvait dans un 58 × 7 pour une pièce de 14 × 9.
  ⚠️ **La bande aussi** : un îlot se partage en bandes égales (ruelle, bâtiments, devant), et
  la plus profonde de l'îlot qui porte l'hôtel en fait **neuf**, dont quatre pour la ruelle
  et le devant. Un lieu garanti **occupe son terrain** — c'est vrai d'un poste de police
  comme d'une usine — et sa façade donne alors sur le trottoir, ce qui est bien où l'on veut
  une porte.
- ⚠️ **Le dé commun ne décide plus des portes.** Une porte — vraie ou condamnée — est une
  **couche peinte** ; elle se tirait au dé commun (celui qui pose les murs) quand il y avait
  une porte par bâtiment, et depuis qu'il y en a une par vitrine, ce serait le nombre de
  commerces d'une rue qui déplacerait les bâtiments de l'autre bout de la ville.
- **Ce qui a bougé, et qu'aucune capture n'aurait montré :**
  - **Deux enseignes pareilles à trente tuiles.** La Shop a **vingt-six noms pour trente-six
    murs** (c'était déjà 31 pour 26 hier) : passé le vingt-septième, la question n'est plus
    « lequel est libre » mais « lequel a sa copie **la plus loin** ». `choisir_enseigne` rend
    maintenant le plus éloigné au lieu du tirage — deux pareilles restent à **40 tuiles au
    minimum** sur les cinq graines, la règle du quartier.
  - **Des débris sur un pas de porte.** `poser_decor` refuse une tuile réservée, mais le
    décor d'un terrain vague se sème **avant** les portes de l'îlot : une porte **dégage**
    désormais son devant. Deux par ville, et c'est le genre de chose qu'on ne voit qu'en
    restant coincé contre sa propre porte.
  - **Un point d'action ne creuse plus un meuble en bloc** (un lit à qui l'on enlève un coin
    n'est plus un lit) **ni l'escalier** — il restait un point « escalier » sur du plancher
    nu, et la pièce n'avait plus qu'une sorte de meuble.
- **Mesure.** Ville livrée : **56 portes** (45 hier), **106 enseignes** (94), **49 pièces
  posées** + 16 dessinées. Planchers de 9 à 120 tuiles, **médiane 32** — au lieu de 41 pièces
  toutes autour de 54. Paquet : +11 Ko d'intérieurs (23 Ko en tout), 445 Ko au total.
- **Juges.** `test_interieurs.py` ne lisait que le **catalogue du module** : les 49 pièces
  posées — la grande majorité — échappaient à tout. Elles passent maintenant **les mêmes
  juges** que les dessinées (une porte, plancher d'un seul tenant, un dixième de meubles et
  deux sortes, points atteignables qui ne volent pas la porte, blocs rectangulaires qui ne se
  touchent pas), et sur la ville livrée : **421 cas** au lieu de 265. Six juges neufs pour la
  règle elle-même — les mesures à chaque porte sur cinq graines, les portes qui s'ouvrent
  quand même (condamner les quarante serait une façon de ne jamais mentir), les vitrines qui
  ne se chevauchent pas, la coupe d'une façade de soixante tuiles, la part qui donne les
  mesures, et l'étage qui est une pièce de **plus**.
- ⚠️ **Deux juges d'à côté sont tombés avec la ville, et aucun ne mesurait ce qu'il croyait** :
  « la banlieue a des entrées » comptait les blocs d'asphalte de **huit tuiles au plus** —
  huit, c'était une entrée **sans case**, et trente-cinq entrées sur trente-six ont dépassé
  le seuil d'une ou deux tuiles ; il mesure maintenant ce qu'on dessine (une allée jusqu'à
  six tuiles **plus** une case de huit). Et « l'eau n'est plus un mur » cherchait une rive
  avec **trois** rangées d'eau : la première rive de la ville neuve est une langue de sable
  que l'agent contournait par une rangée sèche quatre tuiles plus haut — hors de la fenêtre
  que le juge regardait. Sept rangées, et la ville en offre trente-quatre.

### L'eau n'est plus un mur (**correctif**, taille 3) — **livré le 14 sept. 2026**

_Demande de Martin :_ « l'eau ne doit plus être un mur, mais qu'on puisse soit y nager ou
s'y noyer, à pied ou dans un véhicule. »

Aujourd'hui c'est littéralement un mur : `MASQUE_PIETON = MUR | EAU` et `MASQUE_VEHICULE =
MUR | EAU | BASSE`. On s'arrête au bord de la baie comme contre une façade, ce qui est le
plus étrange dans une ville qui s'appelle Baie-des-Brumes.

**À pied : on nage, et c'est le souffle qui décide.** L'endurance existe déjà — 100 points,
0,4 par image à la course, rendue par la bouffe et tenue plus longtemps par le café. Nager
la dépense plus vite. À bout de souffle, on coule : on se réveille à l'hôpital avec sa
facture, exactement comme quand on tombe (`Missions.hopital` fait déjà tout ça).

**En véhicule : il coule.** Aucun char ne flotte. Il s'enfonce en quelques secondes ; le
conducteur sort et nage, ou coule avec. Le char est perdu — ⚠️ et la fourrière ne va pas le
chercher au fond : un char noyé est un char perdu, sinon couler devient un moyen commode de
se faire rembourser une épave.

⚠️ **Le vrai enjeu n'est pas la noyade, c'est le pont.** M8 a bâti sa géographie sur une
règle : une rue dont tous les blocs voisins sont de l'eau est **noyée**, et `PONTS` fait
l'unique exception — « un pont, que le juge défait pour vérifier qu'il est bien le seul
lien ». Si l'on nage, La Pointe n'est plus une île et ce juge devient un mensonge.

La sortie est de reformuler le juge, pas de l'affaiblir : **le pont est le seul lien
CARROSSABLE**. Un homme traverse un chenal à la nage, une auto non — c'est plus vrai qu'avant,
pas moins. Et le souffle fait le reste : la largeur du chenal doit coûter assez de souffle
pour que la traversée soit un pari, et la baie, elle, ne se traverse pas. ⚠️ **Ça se mesure**
et c'est un test : largeur de l'eau × dépense par image contre les 100 points d'endurance.

- ⚠️ **La police nage aussi**, comme elle enjambe les clôtures. Sinon l'eau devient l'exploit
  anti-police le plus simple du jeu : deux pas dans la baie et on est intouchable.
- ⚠️ **Les piétons, eux, ne se noient jamais.** `marchablePieton` exclut déjà la chaussée ;
  il doit exclure l'eau pour tout ce qui flâne. Un passant qui part se baigner dans la baie
  parce que son errance l'y a mené, c'est le genre de chose qu'on ne voit qu'en jeu.
- ⚠️ **Les juges de connexité gardent leur sens.** `composantes_marchables` continue
  d'ignorer l'eau : il sert à prouver qu'aucun trottoir n'est enclavé, et si l'eau reliait
  les rives, il ne dirait plus rien du tout.
- **Il faut un bord.** On ne doit pas passer d'un pas de la terre ferme à la noyade : le
  sable (`s`) existe déjà comme rive, et il devient l'eau **basse** où l'on entre encore
  debout. C'est là que se joue la lisibilité — voir où ça devient sérieux.
- **Coût réel à ne pas cacher** : nager est un état de plus (une pose de sprite — on ne voit
  que la tête et les bras), plus les remous, plus le char qui s'enfonce.
- **Et ça débloque le bateau.** M9 le reporte faute de « tuiles d'eau carrossables » : c'est
  exactement ce que cette vague apporte. Le traversier de M12 y gagne aussi.
- **Juges** : on ne traverse pas la baie à la nage, quel que soit le café bu ; le pont reste
  le seul lien carrossable (le juge de M8, reformulé) ; un char dans l'eau coule toujours et
  ne revient jamais ; un policier lancé derrière le joueur entre dans l'eau comme lui ;
  aucun piéton ordinaire ne met un pied dans l'eau de toute une partie de banc.

**Livré le 14 sept. 2026.** L'eau n'arrête plus que ce qui doit être arrêté, et c'est le
**souffle** qui a repris le travail que faisait la collision.

- **Deux masques au lieu d'un.** `MASQUE_NAGEUR` (le joueur, les agents) ne voit pas l'eau ;
  `MASQUE_PIETON` la garde, et les passants avec. ⚠️ Et **le masque d'un corps dépend d'où il
  est, pas de qui il est** : celui qui a les pieds dans l'eau doit pouvoir en **sortir**. Un
  agent lancé à la nage, revenu à `flane`, serait resté figé au milieu de la baie pour
  toujours.
- **Le souffle décide, et ça se calcule.** `recherche.NAGE` : 1,0 px par image, 0,5 point par
  image — donc **8 points la tuile d'eau**. Le chenal du pont fait 11 tuiles : **88 points sur
  100**, un pari. Le large de la baie est à **73 tuiles** de toute terre, pour **40** au
  plafond absolu (café **et** estomac plein) : on ne l'atteint même pas, et il faudrait
  revenir. ⚠️ **Nager coûte même immobile** — sans ça, s'arrêter au milieu de l'eau serait un
  moyen de refaire son souffle à l'abri de la police.
- **On coule comme on tombe.** `Missions.hopital` fait déjà tout : la facture, la police
  remise à zéro, le boulot abandonné, le fondu et le réveil. Une deuxième façon de perdre
  connaissance aurait sa propre facture, ses propres oublis, et le jour où l'une des deux
  change, l'autre ment.
- **Un char coule, et il est perdu** — ni au fond, ni à la fourrière. ⚠️ Sinon couler devient
  le moyen commode de se faire rembourser une épave : on pousse sa carcasse à l'eau et on va
  la racheter au lot pour le prix d'un remorquage. Trois secondes pour en sortir, et le HUD
  le dit. **Le bateau flotte**, et c'est **sa fiche** qui le dit (`eau`, déjà là pour sa
  friction et son adhérence) — une classe écrite dans le JavaScript en aurait fait une
  deuxième vérité à tenir à jour.
- **La police nage**, à la vitesse de la nage comme tout le monde, et son chemin **paie
  l'eau** (8 tuiles de marche par tuile d'eau, comme le grillage se paie 5). Sans prix, le
  plus court chemin couperait par la baie à chaque fois.
- **Ça se voit.** Un nageur n'a pas d'ombre : il a un **remous**, et son corps est **coupé à
  la ligne d'eau** — cinq pixels, assez pour noyer les jambes, pas assez pour couper le
  visage, qui dit dans quel sens on nage. ⚠️ On coupe **à la source** du `drawImage`, pas avec
  un `clip` : un `clip` coûte un `save`/`restore` par nageur et par image.
- ⚠️ **Le juge du pont est reformulé, pas affaibli**, et il lisait déjà la bonne chose : il
  travaille sur `voie`, la grille des **rues**. « La Pointe est une île pour les chars » est
  une phrase **plus vraie** que « La Pointe est une île », et c'est celle que la géographie de
  M8 a toujours voulu dire.
- ⚠️ **Un défaut trouvé par le juge, et il aurait été invisible** : `v.coule++` sur un char
  qui n'a jamais touché l'eau rend **NaN**, et `NaN < 180` est faux — le char coulait **à la
  première image**, sans qu'on ait le temps d'en sortir. Le compteur s'écrit
  `(v.coule || 0) + 1`.
- **Ce qui reste ouvert** : la rive de sable est là (elle borde presque toute l'eau — 237
  tuiles de bord franc sur 18 569, et ce sont les **quais**, qui doivent être francs), mais
  elle ne ralentit pas encore. Et **le bateau** de M9 a maintenant ses tuiles d'eau : il lui
  manque son sprite et sa place au port.

### Des feux pour piétons (**ajout**, taille 2) — **livré le 14 sept. 2026**

_Demande de Martin :_ « pour les piétons, il faut ajouter des lumières de priorité, et sinon
ils ne passent pas. »

La règle existe déjà, mais **personne ne la voit**. `traverseeSure()` fait traverser un piéton
quand les chars de sa rue ne sont pas au vert ; ailleurs, quand aucun char ne roule à moins de
70 px. Rien ne l'annonce : un piéton planté au bord d'un passage a l'air indécis, pas
discipliné — et le joueur n'a aucun moyen de savoir quand c'est son tour.

⚠️ **Et au passage, le code se trompe d'un temps.** `!feuVert(...)` est vrai pendant
**l'orange** aussi. Les piétons s'engagent donc exactement quand les chars accélèrent pour
vider le croisement — le pire moment du cycle. Un vrai feu piéton ne s'allume pas au rouge :
il s'éteint **avant** que les chars repartent, et c'est ce dégagement qui manque.

- **Le feu lui-même** : un petit poteau à chaque bout de traverse, sur le coin. ⚠️ À 480 × 270,
  il se lira par sa **couleur et sa forme**, jamais par son détail — le blanc qui marche,
  l'orange qui arrête. Rien à inventer côté horloge : `feuVert()` est une pure fonction de
  `B.t` et du décalage du croisement, sans état ; le feu piéton s'en déduit et ne coûte rien
  à garder.
- ⚠️ **Faire clignoter la traverse elle-même serait plus lisible et plus cher.** Les tuiles de
  passage sont **cuites dans le morceau** de 256 px : les animer voudrait dire repeindre
  par-dessus à chaque image. Le poteau est une entité, il se dessine dans le budget déjà
  prévu. Si l'on veut quand même que la traverse s'éclaire, c'est un choix de budget, pas de
  goût, et il se mesure avant.
- ⚠️ **« Sinon ils ne passent pas » demande une exception, sinon la foule s'échoue.** Les
  croisements en **T** n'ont pas de feux — ils ont un STOP (M8). Si un piéton n'y traverse
  jamais, un côté de rue entier devient un cul-de-sac pour la foule, et aucun juge ne le
  verrait : « un seul îlot marchable » parle de géométrie, pas de circulation. La règle juste
  est donc : **au feu, on attend le blanc ; sans feu, on traverse quand c'est libre** — ce qui
  est déjà le comportement, et ce que fait le vrai monde. Un piéton ne reste bloqué que là où
  un feu lui dit d'attendre.
- **Le joueur, lui, n'obéit pas.** Le feu piéton est une **information**, pas une règle : le
  joueur traverse où il veut, c'est déjà l'exception écrite dans la vision. Ce qu'il gagne,
  c'est de savoir quand la foule va bouger — et donc quand un char va devoir s'arrêter.
- ⚠️ **Ça se joue avec la traverse d'une tuile.** Si la traverse rétrécit à une tuile et que
  tout un coin attend le même blanc, la file part d'un coup dans un couloir de 16 px. Les deux
  fiches se décident ensemble : c'est la même question.
- **Juges** : un piéton ne s'engage jamais pendant l'orange ni pendant le vert des chars ; le
  feu piéton s'éteint avant que les chars repartent (le dégagement se mesure en images) ;
  aucun piéton ne reste bloqué plus de N secondes à un passage sans feu ; et le nombre de
  poteaux reste dans le budget de décor et de paquet — un feu par bout de traverse, pas un par
  tuile.

**Livré le 14 sept. 2026.** Le correctif d'abord, l'affichage ensuite — c'est l'ordre qui
compte : un feu qui montre la mauvaise chose est pire que pas de feu.

- ⚠️ **Le temps était faux, et ça se mesure : 240 images sur 960.** `!feuVert(...)` est vrai
  pendant l'orange, donc un piéton s'engageait pendant tout l'orange des deux sens.
  `Monde.feuPieton()` rend maintenant trois états — **blanc** (on s'engage), **dégage** (on
  finit, on ne part plus), **rouge** — et `traverseeSure` n'accepte que le blanc. Le
  dégagement laisse finir ceux qui sont déjà engagés : on ne teste qu'à **l'entrée** du
  passage.
- **Le dégagement vaut 120 images**, l'orange 60 : **180 images** séparent la dernière image
  blanche du premier char qui roule. Deux secondes pour franchir deux tuiles à 0,45 px par
  image — il en faut 71. ⚠️ Sans ce temps-là, celui qui s'engage à la dernière image se fait
  cueillir par le premier char du vert suivant, et **c'est le jeu qui a l'air injuste**, pas le
  piéton qui a l'air imprudent.
- **351 poteaux**, posés par `carte.py` **sur la traverse** — un à chaque bout, jamais un par
  tuile — et refusés partout où le trottoir est déjà pris (496 possibles, 145 écartés). ⚠️ Et
  **le sens du passage voyage avec le poteau** : sans lui, le navigateur devrait redeviner à
  quel feu chaque poteau obéit, et il se tromperait une fois sur deux.
- ⚠️ **Les feux des chars se devinent depuis la boîte du croisement ; ceux des piétons, non.**
  Une traverse ne tombe pas toujours où l'on croit — c'est la carte qui sait où elle est.
- **Ça se lit par la couleur et la forme** : un boîtier plus petit que celui des autos (six
  pixels sur dix-huit — trois cent cinquante fois la taille du grand mangerait la rue), le
  **blanc qui marche**, l'**orange qui arrête**. Et l'orange du dégagement **clignote** : fixe,
  il se lit « attends » ; qui bat, il se lit « finis, mais ne pars plus ».
- ⚠️ **Aucun état à garder** : comme `feuVert`, `feuPieton` est une pure fonction de `B.t` et
  du décalage du croisement. Trois cent cinquante poteaux ne coûtent donc rien de plus qu'un.
- ⚠️ **Le juge du cycle a failli mentir** : il cherchait le prochain vert **en avant** dans une
  fenêtre qui commence à une phase quelconque, et la dernière image blanche tombe souvent
  après le dernier vert de la fenêtre. Il tourne maintenant **en rond** — sans quoi il aurait
  dit « pas de dégagement » pour un dégagement parfait.
- **Ce qui reste ouvert** : la traverse elle-même ne s'éclaire pas. Les tuiles de passage sont
  **cuites dans le morceau** de 256 px, et les animer voudrait dire repeindre par-dessus à
  chaque image — c'est un choix de budget, pas de goût, et il se mesure avant.

### Le taxi de Marco n'est pas à vendre (**correctif**, taille 1) — **livré le 14 sept. 2026**

_Demande de Martin :_ « il ne faut pas pouvoir vendre le taxi de Marco. »

⚠️ **Et ce n'est pas une question d'argent : c'est une histoire qui s'arrête.** M3 pose le
taxi à `porte:garage` — la porte **même** du garage où Ti-Guy rachète n'importe quel char
garé devant (`charDevant()` : le plus proche dans les 90 px, sans une seule question sur à
qui il est). Trois pas, 175 $, et le taxi **sort du monde** : `menuGarage` le retire de
`B.exterieur.entites`. L'objectif « MONTE DANS LE TAXI DE MARCO » attend alors un char qui
n'existe plus — et **la mission ne rate même pas** : `monter` et `livrer` ne font échouer que
sur une **épave**, jamais sur une absence. `p.mission` reste pris, `disponibles()` ne rend
donc plus rien, le téléphone ne sonne plus jamais, et il faut **se faire arrêter**
(`m3.echec` contient `arrete`) pour s'en sortir.

**Le remède dit à qui est le char, et il le dit en Python.** `aToi` existait déjà — un char
**payé** au guichet de la fourrière, sans quoi monter dans le sien était un vol ; il lui
manquait son contraire. `aQui` porte le **slug du personnage** à qui le char appartient, il
vient de la fiche (`prete` sur l'objectif `monter` de `missions.py`), et le navigateur ne
fait que le lire : le menu affiche « IL EST À MARCO » avec le nom de `PERSONNAGES`. Une
ligne grise **qui donne sa raison**, plutôt qu'une vente disparue sans explication.

- ⚠️ **Deux refus, deux raisons, et elles ne se recouvrent pas.** `aQui` dit *à qui il est*
  et ne s'efface **jamais** : le taxi reste à Marco une fois M3 finie, alors que `livrer`
  remet `mission` à `null`. `mission` dit *il sert à quelque chose en ce moment* : ça couvre
  l'**auto-patrouille de M4**, qu'on ne prête pas mais qu'on ne peut pas vendre avant de
  l'avoir larguée — s'arrêter à cinq tuiles du garage, entrer et vendre prenait la mission
  exactement de la même façon.
- **RÉPARER reste ouvert** : Marco veut son taxi **entier**, et le garage est justement là
  pour ça.
- ⚠️ Le refus est **dans `faire`** autant que dans `actif` : un item grisé ne se déclenche
  pas au clavier, mais c'est le **menu** qui le garantit, pas la vente. Appelée en direct,
  elle rend `false` et fait le bruit du refus.
- **Juges** : un Python (un char prêté l'est par un **personnage connu**, sur un objectif
  `monter` ; le taxi de M3 est à son **donneur**) et un de banc en **trois temps** — pendant
  la mission, **après la livraison** (`mission` tombé, `aQui` resté), et une auto de
  n'importe qui garée à la même place, qui elle **se vend toujours** : sinon on aurait
  réparé la fuite en fermant le garage.
- **Resté ouvert, et c'est une question pour Martin** : monter dans le taxi que Marco te
  **prête** compte encore comme un **vol de véhicule** (`Vehicules.monter` : un char
  stationné qui n'est ni volé ni `aToi`), donc un passant peut te dénoncer pour un char
  qu'on t'a confié. `aQui` donne de quoi le corriger en une ligne — mais c'est un choix de
  jeu, pas un bogue à trancher tout seul.

### Les terrains de banlieue (**ajout**, taille 2) — **livré le 14 sept. 2026**

_Demande de Martin :_ « les terrains des résidences doivent être plus fournis — jardin,
piscine, sentier vers la rue, entrée de voiture, voiture, et autres idées. »

M8 a eu raison sur le principe et le dit dans son propre code : « la banlieue se reconnaît au
**vide** autour des maisons, pas aux maisons ». Les marges sont donc larges — jusqu'à cinq
tuiles. Mais ce vide est aujourd'hui `_jardin()` : du gazon, et un arbre ou un buisson par
dix tuiles, posés au hasard. Or un terrain de banlieue est le contraire du vide — c'est
**plein des traces de la vie de quelqu'un**.

- **L'entrée de voiture, et l'auto dedans.** Une bande d'asphalte de la rue jusqu'au côté de
  la maison. ⚠️ Et voici le meilleur morceau : elle se dessine avec les **cases de
  stationnement** qu'on vient de livrer — une case `^`/`v` tournée vers la maison. Comme
  `placeStationnee()` cherche déjà les cases pour y garer une auto dans ses lignes, **la
  voiture dans l'entrée arrive sans une ligne de code de plus**.
  - ⚠️ **Mais pas dans toutes les entrées.** Si chaque bungalow porte une case, la banlieue
    se remplit de chars stationnés et le budget d'entités y passe. Une entrée sur trois, pas
    plus ; les autres restent de l'asphalte nu — ce qui est aussi la vraie vie.
  - ⚠️ **Une entrée touche la rue**, toujours. C'est la même règle que « toute rangée de
    stationnement touche une allée » : une entrée qui ne rejoint pas la chaussée n'est pas
    une entrée, c'est un carré d'asphalte.
- **Le sentier de la porte à la rue.** `poser_porte()` réserve déjà les deux tuiles devant la
  porte ; le sentier les relie au trottoir. Sans lui, on marche sur le gazon pour entrer chez
  les gens — et c'est précisément ce qui donne l'impression du « pas fini ».
- **La piscine**, hors terre, au fond de la cour. ⚠️ Elle rencontre de plein fouet la vague
  de l'eau : une piscine de banlieue n'est pas la baie. C'est de l'**eau basse** — on y entre
  debout, on ne s'y noie pas — donc le même cas que la rive de sable que cette vague-là
  prévoit déjà. Et un juge : **une piscine ne coupe jamais le sentier** de la porte à la rue.
- **Le grillage entre deux terrains**, et c'est là que ça cesse d'être décoratif : avec la
  vague des clôtures, une haie de grillage s'enjambe. Une poursuite à pied dans Les Érables
  devient une suite de cours à traverser, au lieu d'une course en ligne droite sur le
  trottoir. **C'est la seule idée de la liste qui change le jeu**, et elle ne coûte rien de
  plus une fois les clôtures faites.
- **Le reste, qui n'est que du décor et c'est très bien** : un cabanon au fond, une corde à
  linge, un BBQ sur la galerie, une balançoire là où il y a des enfants (le jeu en a déjà).
- **Deux idées de plus, avec leur crochet** :
  - une **pancarte À VENDRE** sur un terrain de temps en temps — `economie.PROPRIETES` existe,
    et une maison à vendre devient une propriété de plus le jour où on veut en ajouter ;
  - un **chien attaché dans une cour**, qui jappe quand tu passes. ⚠️ Ce n'est pas du décor :
    un chien qui jappe est un **témoin**, il réveille la rue. À décider franchement — soit il
    alerte pour vrai, soit il ne fait qu'un bruit, mais pas « un peu ».
- ⚠️ **Le vrai coût est dans le paquet, pas à l'écran.** `decor` est une liste qui voyage :
  six objets par terrain, sur un district entier, et on sort des bornes (600 Ko bruts, 70 Ko
  gzip). **On mesure avant**, et si ça déborde, le décor de terrain se **dérive de la
  position** (`hash2`) au lieu de voyager — exactement ce qui a été fait pour les usures
  d'asphalte des stationnements.
- **Juges** : toute entrée de voiture rejoint la chaussée ; un sentier relie chaque porte de
  banlieue à la rue, sans passer par une piscine ; une case d'entrée n'apparaît que sur une
  fraction des terrains, mesurée ; et le paquet reste sous ses bornes, sinon le décor se
  dérive et ne voyage plus.

**Livré le 14 sept. 2026.** Le terrain se meuble **après la porte**, et c'est tout le
travail : le sentier part d'elle, la piscine et le cabanon se posent après le sentier. Posé
dans l'autre sens, un cabanon se retrouve sur le pas de la porte.

- **38 entrées de voiture**, et chacune **va jusqu'à la chaussée**. ⚠️ La parcelle ne touche
  pas la rue : entre les deux il y a la bande de devant, deux rangées de **gazon** en
  banlieue. Une entrée qui s'arrête au bord de la parcelle s'arrête dans l'herbe — ce n'est
  pas une entrée, c'est un carré d'asphalte.
- **Une sur trois porte une case**, donc une auto garée : **28 % mesuré**, et le juge mesure
  au lieu de croire. Si chaque bungalow en portait une, la banlieue se remplirait de chars.
- **Un sentier pour 100 % des portes.** ⚠️ La fenêtre de recherche était à six rangées, et
  les marges de banlieue vont jusqu'à cinq, plus deux de bande et deux de trottoir : quinze
  portes sur vingt-sept restaient sans sentier, et **rien ne le disait** sinon le juge.
- **La piscine est ronde**, et c'est un retour de Martin en regardant l'écran : « piscine
  ronde stp et pas 4 carrés ». Chaque tuile porte un **quart du disque** et sait lequel en
  lisant ses voisines (`bloc`) — peintes chacune pour soi, les quatre montraient quatre
  margelles. Elle est de solidité 3 : un piéton la traverse, une auto non, et **on ne s'y
  noie pas** — une piscine de banlieue n'est pas la baie, et la couleur le dit avant le
  joueur.
- **Le paquet** passe de 410 à **413 Ko** bruts et de 51 à **52 Ko** gzip, pour des plafonds
  de 600 et 70. La fiche craignait qu'il faille dériver le décor de la position : ce n'est
  pas nécessaire, et **c'est la mesure qui le dit**.

⚠️ **Trois défauts trouvés en chemin, dont deux qui n'ont rien à voir avec la banlieue** —
c'est le décalage des dés qui les a mis sous le nez des juges :

- **Une plage suivait la boîte, pas la côte.** `_terre_a_cote` promet « on ne dessine une
  rive que là où il y a un rivage », et ne tenait la promesse qu'à l'échelle du bord : une
  seule tuile de terre quelque part le long du côté, et le sable courait sur **toute** sa
  longueur, y compris là où le voisin est de l'eau. D'où des bancs de sable isolés en pleine
  baie, que `boucher_les_poches` doit noyer un à un. Le rivage se vérifie maintenant **rangée
  par rangée**.
- **Un char plus long que sa case.** Une case fait deux tuiles, 32 px ; la remorqueuse en
  fait 36. Garée là, elle dépassait, le garde-fou la poussait hors des tuiles qu'elle
  chevauche, et elle finissait **à cheval sur ses lignes** — à un centième de pixel près, ce
  qu'un juge voit et qu'un œil ne voit pas.
- ⚠️ **Le jeu plantait.** Un témoin qui court vers un agent met `e.vers` à zéro quand sa
  minuterie tombe — et la ligne suivante lisait `e.vers.x`. Une seule image sur des milliers,
  celle où il finit sa course pendant qu'il court : invisible jusqu'à ce qu'un singe tombe
  dessus.
- **Et les Skateux tiennent enfin tout leur stationnement.** Leur bande ne se découpe plus :
  c'est une **piste**. Un terrain de sept tuiles tiré au sort n'en laisse que cinq d'élan une
  fois la rampe posée, et il en faut sept — La Pointe se retrouvait sans tremplin dès que le
  découpage bougeait d'une tuile.

**Ce qui n'est pas livré, et pourquoi** : la **pancarte À VENDRE** et le **chien attaché**.
La fiche dit du chien qu'il faut trancher franchement — « soit il alerte pour vrai, soit il
ne fait qu'un bruit, mais pas *un peu* » — et un témoin de plus dans chaque cour est une
décision de jeu, pas de décor. Les deux restent au réservoir.

### Les armes à feu (**ajout**, taille 2) — **livré le 14 sept. 2026**

_Demande de Martin :_ « je veux des armes à feu. »

Il y en a **deux** aujourd'hui, et c'est ça le problème : le **pistolet** (250 $, chargeur
de 12, 30 points) et le **fusil à pompe** (600 $, 8 cartouches, 6 plombs). Sur dix armes au
catalogue, huit sont de la mêlée, du ramassé par terre ou une fronde. Il ne manque pas _une_
arme à feu — il manque une **raison de choisir** entre elles. Trois de plus, et chacune
répond à une question que les deux autres ne savent pas régler :

- **La mitraillette** — _« ils sont trois. »_ Automatique : on tient le bouton, la cadence
  est haute, les dégâts par balle bas, et la dispersion **monte tant qu'on tient**. On arrose
  ou on tire par rafales courtes ; c'est le choix qui fait l'arme. ⚠️ Le moteur ne sait pas
  tirer en automatique : une arme tire un coup par pression, `cadence` images plus tard. Le
  champ `auto` est du travail neuf, et il touche au tactile — au téléphone, « tenir » est un
  geste, pas un clic.
- **La carabine** — _« il est loin. »_ Longue portée, lente, précise, un passant d'une balle.
  ⚠️ **Plafonnée à la largeur de l'écran** : la vue fait 480 px de large, soit 30 tuiles.
  Une portée qui dépasse ça, c'est tirer sur ce qu'on ne voit pas — et le pistolet est déjà
  à 180 px, onze tuiles. La carabine s'arrête à ce que l'écran montre, et c'est une borne,
  pas un réglage.
- **Le cocktail Molotov** — _« ils sont groupés, et je veux que ça dure. »_ Il se lance **en
  cloche**, comme la fronde (le seul projectile qui a déjà un `z` et une gravité), et il
  laisse une **flaque de feu** qui brûle quelques secondes — le feu existe déjà, c'est celui
  des chars sous 20 % de PV, avec ses dégâts par seconde. Deux mécaniques déjà écrites, une
  arme neuve.

Ce qu'il faut décider en même temps, sinon l'ajout se retourne contre le jeu :

- ⚠️ **Une arme à feu change le jeu de police, pas seulement le combat.** La taxonomie est
  déjà là : sortir une arme près d'un policier +1★, tirer sur un policier +2★, le tuer +3★.
  Chaque nouvelle arme déclare donc son `etoiles_usage` — et **une arme bruyante réveille le
  quartier** : une rafale s'entend comme une explosion s'entend (l'alarme de rayon existe
  déjà), même quand personne ne t'a vu.
- ⚠️ **La même parade que pour le char rapide.** Une carabine qui descend les policiers hors
  de leur cône rendrait le 5★ gratuit. La parade est celle qu'on a déjà écrite pour la
  vitesse : le cône n'est pas le seul sens. **Un coup de feu s'entend** — tirer de loin
  t'évite d'être _vu_, jamais d'être _cherché_. La distance achète du temps, pas
  l'impunité.
- ⚠️ **Les munitions font l'équilibre, pas les dégâts.** Une mitraillette qui vide trente
  balles en deux secondes est inutile ou infinie selon le prix du chargeur, et rien entre les
  deux. `prix_munitions` porte tout le poids.
- **Où on les achète** : pas chez Gus. Le **marché noir** existe depuis M7, en arrière du
  bar — c'est là que se vend ce qui fait du bruit, et ça donne enfin à ce comptoir autre
  chose à offrir qu'à M10.
- **Juges** : les prix montent toujours dans l'ordre du catalogue (le test existe) ; aucune
  portée ne dépasse la largeur de la vue ; une arme automatique consomme bien une balle par
  coup et s'arrête chargeur vide ; le feu d'un Molotov s'éteint, ne se propage pas à
  l'infini, et compte comme une mort **causée par le joueur** (sinon on tue sans étoiles) ;
  et un policier abattu laisse tomber son arme — ça marche déjà, ça doit continuer.

**Livré le 14 sept. 2026.** Les trois armes, le comptoir, l'ouïe — et cinq choses apprises
en chemin.

- **Trois champs de fiche, pas trois cas dans le JS** : `auto`, `bruit` (tuiles) et `feu_s`
  (secondes), plus `dispersion_max`. Le pistolet et le fusil ont reçu leur `bruit` du même
  coup (14 et 18 tuiles) : ils détonaient déjà, personne ne les entendait. Ce qui n'est pas
  propre à une arme (`rafale_images`, le rayon et la morsure de l'incendie) voyage dans
  `armes_regles`.
- **L'automatique ne demande rien de neuf à l'entrée.** `frapper` refuse déjà tant que la
  cadence court : tenir le bouton et rappeler `frapper` à chaque image suffit, **c'est la
  cadence qui rythme la rafale** — et le tactile suit sans un geste de plus, puisque le bouton
  FRAPPE tenu se lit déjà comme « bas ». ⚠️ **À vide, la gâchette tenue ne clique qu'à la
  pression** : sans ce garde, un chargeur vide cliquait soixante fois par seconde.
- **L'ouïe, c'est `alerterAgent` sans le cône.** `Police.entendre(x, y, rayon)` envoie en
  enquête chaque agent dans le rayon, **sans étoile** — il n'a rien vu — et, si tu es déjà
  recherché, déplace `dernierVu` sur le coup. Mesuré au banc : un agent qui te tourne le dos à
  douze tuiles vient voir la carabine, celui à trente reste, et la fronde ne s'entend pas.
- ⚠️ **Le type `feu` était pris — c'est le feu de circulation.** La flaque s'appelle donc
  `brasier` : une entité `dessine: false` qui n'existe que par ses particules (des flammes à
  chaque deuxième image, de la fumée) et mord toutes les vingt images un tiers des dégâts de la
  seconde — passants, joueur, chars (`Vehicules.endommager`, le lanceur pour agresseur : un
  char qui en explose, c'est **son** explosion). Sur l'eau, un remous et rien d'autre.
- ⚠️ **`Entites.blesser` pousse la victime loin de la SOURCE**, par défaut : dans le feu, la
  source est le lanceur, et le passant aurait été poussé loin du joueur — donc parfois plus
  au fond du feu. Le brasier passe son propre angle : il pousse **dehors**.
- **La bouteille s'entend quand elle casse**, pas quand elle part : `tirer` se tait pour une
  arme à `feu_s`, et `allumer` joue le son. Le juge compte zéro au lancer, un à l'arrivée.
- ⚠️ **Le script de génération audio tombait sur `duree_s: 0.4`** sans rien expliquer : le
  serveur MCP a un plancher de 0,5 s et répond alors par une erreur qui n'est pas du JSON. Le
  catalogue dit 0,5 maintenant, et la note est dans `audio.py`. Quatre fichiers (45 Ko) ont
  fait déborder le budget des bruitages de 700 octets : relevé à 900 Ko, encore un son qu'on
  n'avait pas.
- **Ce qui n'a pas bougé, et c'est voulu** : les agents gardent leur pistolet à tous les
  paliers (donner la mitraillette au 4★ est une décision de M11, pas de cette fiche) ; et le
  sprite en main est celui de l'objet par terre, comme pour les autres — le chargeur qui
  pend, la crosse de bois, le chiffon allumé, c'est ce qui les nomme à seize pixels.
- **Juges (7 neufs)** : côté Python, trois questions distinctes (une seule `auto`, la plus
  longue portée sans dispersion, le seul `feu_s` en cloche), aucune portée au-delà de la
  demi-vue **lue dans `base.js`**, tout ce qui détone déclare un `bruit` et se vend chez Josée
  sans vitrine chez Gus, et les règles voyagent ; au banc, la mitraillette tenue 90 images
  tire exactement ses huit balles, s'ouvre à `dispersion_max` et se referme quand on lâche ;
  la carabine s'entend à douze tuiles dans le dos d'un agent, sans étoile ; le Molotov
  n'allume qu'un brasier, tue celui qui y reste avant qu'il s'éteigne, le signale comme une
  mort du joueur, et s'éteint.

### Les feux s'allument pour vrai (**correctif**, taille 1) — **livré le 14 sept. 2026**

_Demande de Martin :_ « je veux que les feux de circulation et de piéton allument pour vrai. »

Ils sont **peints**, pas allumés — et la nuit, ça se retourne contre eux. `Base.fin` compose la
nuit en **multipliant** toute l'image par la teinte de l'heure, puis rajoute les lampes en
`lighter` par-dessus. Un feu n'a aucune lampe : il ne reçoit donc que la multiplication, comme
une brique. À minuit (teinte 26, 32, 80 à 0,72) :

| ce qu'on peint | de jour | à minuit |
|---|---|---|
| le vert des chars | 46, 204, 113 | **16, 76, 57** |
| le rouge des chars | 231, 76, 60 | **82, 28, 30** |
| le blanc qui dit MARCHE | 242, 242, 242 | **86, 90, 122** |
| le trottoir sous le poteau | 154, 150, 137 | 54, 56, 69 |

⚠️ **Le blanc du feu piéton à minuit est plus sombre qu'un trottoir de midi** (luminance 92
contre 150). Le seul objet de la ville qui éclaire pour vrai, c'est le **lampadaire** — et la
seule raison, c'est qu'il a une entrée dans `carte.lampes`. Les feux n'en ont pas.

- **Une ampoule allumée pose une lampe, de la couleur de sa phase.** Rouge, vert, orange, le
  blanc du piéton : ce n'est pas un halo jaune de plus, c'est **la couleur de l'information**
  qui se répand sur l'asphalte. C'est aussi ce qui fait qu'on lit un feu **de loin**, la nuit,
  avant même de distinguer le poteau.
- ⚠️ **Elles se ramassent EN DESSINANT, jamais en parcourant la ville.** `carte.lampes` est une
  liste fixe qu'on peut balayer ; les feux sont **482 poteaux** (124 pour les chars, 358 pour
  les piétons) dont la couleur change à chaque phase. Les parcourir par image pour trouver ceux
  de l'écran serait payer la ville entière pour en éclairer trente. `dessinerFeu` est déjà
  appelé **une fois par feu visible** — c'est là, et nulle part ailleurs, que la lampe se pose.
- ⚠️ **Et elles se vident toutes seules.** Une liste qu'un dessin remplit et qu'un autre module
  doit penser à vider finit par fuir le jour où quelqu'un dessine sans composer. Elle porte donc
  son numéro d'image (`B.image`, l'horloge de l'œil) : à l'image suivante, elle est vide sans
  que personne l'ait vidée.
- **Le plafond de `Base.fin` doit monter.** Il est à 25 lampes, taillé pour les lampadaires
  seuls. Un croisement, c'est 2 poteaux de chars (2 ampoules chacun) et jusqu'à 4 poteaux de
  piétons : **8 lampes** — et il en tient plusieurs à l'écran. Sans un plafond plus haut, les
  feux **éteindraient les lampadaires** au lieu de s'ajouter à eux.
- **De jour, une ampoule doit aussi se lire comme allumée**, et ça ne se joue pas sur la
  couleur : un carré vert plat est un carré vert. Ce qui dit « allumé », c'est un **cœur** plus
  pâle que le pourtour — la convention du pixel art pour une source de lumière, et la seule qui
  tienne dans trois pixels sur trois.
- ⚠️ **Deux ampoules à cinq pixels l'une de l'autre mélangent leurs halos.** Le feu des chars
  porte le nord-sud et l'est-ouest côte à côte : quand l'un est rouge et l'autre vert, la flaque
  au sol tire vers le jaune. C'est ce que fait un vrai croisement vu de haut ; ce qui doit rester
  **net**, c'est le cœur de chaque ampoule, donc les halos restent **petits**.
- ⚠️ **Le seuil de la brune est celui de tout le monde** : sous `ambiance().alpha` 0,2, les
  lampadaires ne s'allument pas et les feux non plus. Deux seuils voudraient dire deux règles
  pour « il fait noir », et la deuxième serait fausse un jour.
- **Juges** : à minuit, un feu au vert pose une lampe verte et un feu au rouge une lampe rouge —
  la couleur **suit la phase** ; en plein jour, aucune lampe ; l'orange **clignotant** du piéton
  n'éclaire pas pendant qu'il est éteint (sinon il clignote à l'œil et brille en continu au sol) ;
  et le compte des lampes d'une image tient sous le plafond de `Base.fin`.

**Livré le 14 sept. 2026.** ⚠️ **L'analyse ci-dessus était trop généreuse, et la mesure l'a
dit tout de suite** : les feux n'étaient pas *peints puis éteints par la nuit*, ils n'étaient **pas
peints du tout**. Le premier juge écrit — « un feu au vert pose une lampe verte » — est revenu
avec **zéro lampe**, à midi comme à minuit. En remontant : `dessinerFeu` et `dessinerFeuPieton`
n'avaient **jamais été appelés une seule fois** depuis qu'on a posé les feux.

- ⚠️ **Un champ de trop suffisait.** `creerSignalisation` créait l'entité avec `decor: 'feu'`, et
  `Entites.dessiner` teste `if (e.decor)` **avant** `if (e.type === 'feu')` : la branche générique
  peignait le boîtier cuit — le poteau noir, sans lanternes — et faisait `continue`. Le peintre
  nommé était derrière, inatteignable. **482 poteaux** noirs (124 pour les chars, 358 pour les
  piétons), à tous les croisements de la ville, depuis le premier jour.
- ⚠️ **Et le champ ne servait à rien.** Un feu n'est pas solide, il n'entre donc jamais dans
  `grilleFixe` — les deux seuls autres lecteurs de `e.decor` (`bloquerParDecor`, `heurterDecor`)
  passent par là. Il ne faisait que **masquer le peintre**. Il est parti, **et** l'ordre du
  dispatch est corrigé : les peintres nommés d'abord, la branche générique ensuite. Dans l'autre
  sens, le prochain `decor` posé sur une entité qui a déjà son peintre l'effacerait pareil.
- ⚠️ **Pourquoi aucun juge ne l'a vu, et c'est la vraie leçon.** Les feux avaient déjà quatre
  juges — l'alternance, les T sans feu, le dégagement de 180 images, les poteaux posés sur le
  trottoir et pas sur la route. **Tous parlent de l'horloge ou de la carte, aucun du dessin.** Un
  système peut être juste de bout en bout et ne rien montrer ; il manquait la question bête :
  *est-ce qu'on voit quelque chose ?* Le banc sait y répondre — `ctx.traces` garde chaque
  `fillRect` — et c'est ce que fait le juge neuf `test_un_feu_peint_ses_lanternes...`, **en plein
  jour**, là où aucune lampe ne vient aider.
- **La lampe, ensuite**, comme prévu : une par ampoule allumée, de la couleur de sa phase,
  ramassée **en dessinant** (`Vehicules.lampesDesFeux()`), remise à `Base.fin` par `jeu.js`. La
  liste porte son numéro d'image et se vide toute seule.
- ⚠️ **Le rayon s'est décidé à l'écran, pas sur le papier.** À **10 px**, les deux ampoules du feu
  des chars — cinq pixels d'écart — additionnaient assez de rouge et de vert pour rendre du
  **blanc** : on voyait bien qu'un feu brillait, on ne lisait plus **lequel des deux sens** était
  vert. À **7 px** et une lumière moins forte, les deux cœurs restent nets et la flaque tire vers
  le jaune, ce qui est ce que fait un vrai croisement vu d'en haut. Le lampadaire garde ses 44 px :
  lui éclaire une rue, un feu ne s'éclaire que lui-même — et la hiérarchie se voit.
- **Le plafond de `Base.fin` passe de 25 à 50** : 25 lampadaires (`lampesVisibles`), 24 feux et le
  projecteur de l'hélico. Deux juges le tiennent, et ils **lisent les trois nombres dans le JS**
  plutôt que de les recopier — avec le seuil de la brune, qui doit rester **le même** que celui des
  lampadaires.
- **Juges (5 neufs)** : un feu **peint** ses deux lanternes (vert pour le sens qui roule, rouge pour
  l'autre) et son cœur, en plein midi, mesuré sur les rectangles ; à minuit une ampoule pose une
  lampe et **la couleur suit la phase** (les deux sens échangent au demi-cycle, l'orange n'est ni
  l'un ni l'autre) ; **rien n'éclaire à midi** ; l'orange qui clignote **n'éclaire pas** pendant
  qu'il est éteint ; le plafond de lampes et le seuil de la brune tiennent. Les trois juges de banc
  sont **rouges sur le code d'avant** — vérifié en remettant le bogue.
- **Ce qui reste ouvert, inchangé** : la traverse elle-même ne s'éclaire toujours pas (tuiles
  cuites dans le morceau de 256 px), et les feux ne passent pas au **clignotant la nuit** — c'est
  M12, « la ville vit ».

### Le son de l'eau (**correctif**, taille 1) — **livré le 14 sept. 2026**

_Demande de Martin :_ « améliore le son de quand on va dans l'eau. »

Il n'y a **rien à améliorer** : il n'y a pas de son d'eau dans le jeu. Ce qu'on entend en
entrant dans la baie, c'est `SFX.choc` — « Tôle froissée », le son d'un **accident de
char** (`app/audio.py` : deux variantes de carrosserie qui se plie). C'est la seule ligne de
son que « L'eau n'est plus un mur » a posée, et elle l'a été faute de mieux.

Le reste est du silence, et c'est pire que le mauvais son :

- **On nage sans rien entendre.** `majJoueur` coupe les pas dans l'eau (« On ne fait pas de
  pas dans l'eau ») et ne met rien à la place : onze tuiles de chenal, 88 points de souffle,
  et pas un bruit.
- **On sort de l'eau sans un bruit** non plus : le drapeau `j.nage` retombe, les remous
  s'arrêtent, rien ne se fait entendre.
- **On coule en silence.** `noyade()` fait seize remous et appelle l'hôpital — le moment le
  plus grave que l'eau peut produire ne s'entend pas.
- **Un char qui coule est muet de bout en bout.** `majNoyade` écrit « IL COULE — SORS » au
  HUD, fait bouillir l'eau autour pendant trois secondes, et on n'entend **rien** : ni la
  plongée, ni les bulles, ni le dernier glouglou. Le HUD dit ce que l'oreille aurait dû dire
  la première.

**Ce qu'on fait.** Trois bruitages ElevenLabs de plus, et le câblage qui manque :

- `plongeon` (2 variantes) — un corps qui entre dans l'eau. Il remplace la tôle froissée à
  l'entrée, **et** sert à la sortie de l'eau, à l'entrée des piétons et des agents
  (`Son.jouerA`, donc plus faible de loin) et au char qui plonge.
- `nage` (3 variantes) — la brassée. Elle se joue **à la distance parcourue**, exactement
  comme `pas` : c'est le même geste et le même besoin. Une boucle tenue sous un nageur
  immobile sonnerait comme une fontaine. ⚠️ Trois variantes et pas une : une brassée revient
  une fois et demie par seconde, c'est là que l'oreille s'agace le plus vite.
- `couler` (1) — la tête qui passe sous l'eau : le glouglou et les bulles. Il joue à la
  noyade du joueur **et** quand le char touche le fond.

⚠️ **Le char n'a pas son propre fichier, et c'est voulu** : c'est la même eau, avec plus de
masse. Il joue `plongeon` **plus un coup de grave synthétisé** — le poids, c'est ce qui
manque à un corps de 80 kg, pas la matière. Un quatrième fichier aurait coûté 20 Ko pour
dire la même chose.

⚠️ **Le budget des bruitages doit monter** (900 → 950 Ko) : c'est un son qu'on n'avait pas,
pas un son qu'on a laissé grossir. On reste sous le mégaoctet, et la finition ne change pas.

- **Juges** : entrer dans l'eau joue le plongeon et **plus jamais la tôle** ; nager fait des
  brassées et **aucun pas** ; à bout de souffle, on entend `couler` ; un char qui entre dans
  l'eau plonge, puis fait du bruit en coulant ; et le filet synthétisé des trois **atteint la
  sortie**, comme pour tous les autres effets.

**Livré le 14 sept. 2026.** Six fichiers (83 Ko), six moments qui ne s'entendaient pas, et un
cul-de-sac trouvé en chemin.

- **Les trois sons sont générés et mesurés.** `plongeon` et `nage` **brillent** (‑10 dB au-dessus
  de 8 kHz : ce qui fait entendre l'eau, ce sont les gouttes — le plongeon entre donc dans le
  juge de l'aigu), et `couler` est **sourd** (‑47 dB), ce qui est le signe que le son est le
  bon : une tête qui passe sous l'eau n'a plus d'aigu. ⚠️ **Martin ne les a pas encore
  écoutés** — c'est la seule chose qu'aucun juge ne remplace ; `--refaire plongeon` est là pour
  ça.
- **Six moments câblés**, et chacun existait déjà sans bruit : on entre (plongeon), on avance
  (brassée à la distance, comme un pas), on sort (une dernière brassée), on coule (`couler`),
  un autre corps entre (`jouerA`, donc plus faible de loin), un char plonge et s'enfonce.
- ⚠️ **Une seule porte pour entrer dans l'eau** (`Entites.mouiller`). `police.js` posait lui
  aussi `a.nage` avant de déplacer son agent : deux endroits qui lisent la même transition, et
  le premier la mange. Tant que la transition se lisait à deux endroits, le son de l'agent
  dépendait de **l'ordre d'appel** — le genre de dépendance qu'on ne voit pas et qui se casse
  au prochain remaniement.
- ⚠️ **LE défaut trouvé en chemin, et il vaut plus que le son** : `v.conducteur === 'joueur'`
  — la chaîne — n'était **jamais vrai**. Partout ailleurs le conducteur est l'**entité**
  (`v.conducteur = j` dans `monter`) ; seul le trafic porte une chaîne. Trois lignes en
  dépendaient, et le silence était la moins grave : « IL COULE — SORS » **ne s'affichait
  jamais**, et surtout le joueur restait `dansVehicule` un char **retiré des entités** —
  mesure du banc : `nage` faux, et **0 px en 60 images de touche**. Couler dans son char était
  un **cul-de-sac**, et personne ne l'avait vu parce que le juge de « L'eau n'est plus un mur »
  poussait un char **vide** à l'eau.
- ⚠️ **Le juge de l'agent se trompait d'une image**, et c'est instructif : la police pose
  `a.nage` **avant** de déplacer son agent, donc l'image où `dansLEau` devient vrai est celle
  où il entre — le plongeon part à la suivante. Un juge qui s'arrête pile à la première mesure
  un silence qui n'existe pas.
- **Ce qui reste ouvert** : le **sable** (`s`) borde l'eau mais ne sonne pas encore comme une
  rive (l'eau basse où l'on entre debout, cf. « L'eau n'est plus un mur ») ; et rien ne dit
  encore, à l'oreille, qu'on **manque de souffle** dans l'eau — c'est le souffle du joueur de
  M15, qui attend ses clips.

### Les amuseurs de rue font un vrai spectacle (**correctif**, taille 3) — **livré le 14 sept. 2026**

_Demande de Martin :_ « je veux que les amuseurs de rue soient animés et qu'il y ait toujours
entre 3 et 5 personnes autour. Présentement ils ne font rien et sont ennuyants. Je veux que le
musicien fasse vraiment de la musique, 5 musiques différentes, je veux des jongleurs et des
échassiers. » Et : « ils doivent toujours être dans le centre-ville, où il y a plus de gens.
Tu peux aussi mettre plus de gens en centre-ville et moins en périphérie. »

⚠️ **Martin a raison, et la fiche d'origine le disait déjà.** « Des sortes de gens » promettait
un musicien qui « joue — et **ça s'entend** » ; ce qui a été livré, c'est un corps avec une
guitare dessinée dessus et **zéro note**. Le jeu a un séquenceur (`Son.Mus`), dix morceaux
écrits en notes, un chef d'orchestre — et l'homme à la guitare est muet. C'est la neuvième fois
que le dépôt paie « une fiche que le navigateur ne lisait pas », et la première où c'est
l'**oreille** qui le dit.

Ce qui ne va pas, mesuré :

- **Ils ne font rien.** `majSortes` envoie le musicien et l'amuseur dans la même fonction,
  `attrouper`, qui ne touche **qu'aux badauds** : elle ne change rien à l'artiste. Ils sont
  `vitesse: 0`, donc `bouge` est faux, donc `imageDe` tombe sur **l'image zéro** — la même,
  toujours, pour toute la partie. Le mime n'a jamais bougé un doigt.
- **L'attroupement est un hasard, pas une foule.** `attrouper` attend qu'un passant entre dans
  les 46 px et qu'il soit en `flane` ou `arret`. Dans une rue vide, il n'y a **personne** ; et
  une fois attroupés, leur `minuterie` de 4 à 8 s les renvoie ailleurs sans que rien ne les
  remplace. Le juge du banc pose lui-même quatre badauds avant de mesurer — c'est-à-dire qu'il
  mesure l'attroupement d'une foule qu'il a fabriquée.
- **Ils naissent partout.** `musicien` et `amuseur` n'ont pas de `districts` : un mime dans une
  cour à ferraille de La Shop à 3 h du matin, devant personne.
- **Il n'y a qu'un genre d'amuseur** : le mime. Pas de jongleur, pas d'échassier.

**Ce qu'on fait.**

- **Quatre corps, quatre spectacles.** Le musicien et le mime gagnent de vraies images de
  spectacle ; le **jongleur** et l'**échassier** sont deux sortes neuves, avec leur corps à
  elles (règle du dépôt : une sorte = un corps + une routine, et un juge Python refuse une
  sorte qui porte le corps d'une autre).
  - le **musicien** gratte : la main descend et remonte **en mesure**, sur le tempo du morceau
    qu'il joue ;
  - le **mime** enferme le vide : mur invisible, boîte, salut — des poses, pas des pas ;
  - le **jongleur** a **trois balles dans les airs**, et elles sont dans le sprite : quatre
    images, la balle monte, tourne, retombe. ⚠️ Dessiner les balles à part aurait voulu dire
    un deuxième chemin de dessin pour une seule sorte — le sprite les porte, l'atlas les cuit
    une fois, et le tri par `y` reste le seul tri ;
  - l'**échassier** est **plus haut que tout le monde** : son sprite fait 26 px au lieu de 13,
    il dépasse la foule, et il tangue doucement — c'est précisément ce qui le rend visible de
    loin, par-dessus l'attroupement.
- **Toujours 3 à 5 personnes autour**, et c'est une **règle**, pas une chance : si le cercle
  est en dessous du minimum, un badaud **naît hors champ** et vient se planter dedans ; au
  maximum, on n'en prend plus. Les spectateurs **tournent** — un qui s'en va est remplacé — et
  ils **applaudissent**. ⚠️ Les chiffres (3, 5, le rayon du cercle, la patience) vivent dans
  `pietons.py` : le navigateur les lit, il ne les invente pas.
- **Le musicien joue vraiment, et cinq morceaux.** Cinq pièces de rue **écrites en notes**
  (`musique.py`), comme le thème du menu et les radios — deux voix, une guitare qui gratte et
  une mélodie, pas un orchestre : ⚠️ un homme seul sur un trottoir n'a ni basse ni batterie, et
  une station de radio à quatre voix sous un mime aurait sonné comme un haut-parleur.
  - **La complainte du Faubourg**, **Le reel du trottoir**, **Le blues du coin**, **La valse de
    la Baie** (à trois temps — la seule du jeu) et **La ballade des brumes**. Chaque musicien
    en tire une **à la naissance** et la garde.
  - ⚠️ **Elle se joue DANS LA RUE, pas dans le casque** : un deuxième séquenceur (`Son.Rue`)
    avec sa propre sortie, et **le volume suit la distance** — on l'entend d'un coin de rue, on
    l'a dans les oreilles devant lui, et elle s'éteint quand on s'en va. Un seul musicien
    sonne à la fois (le plus proche) : dix musiciens auraient fait dix séquenceurs.
  - ⚠️ Elle passe **sous** la voix (le ducking l'atteint, comme la radio) et **sous** la musique
    d'état : quand la police te court après, la toune du guitariste n'a plus d'importance.
    L'échelle de `musique.py` ne change pas — la rue s'ajoute **en dessous**.
- **Ils tiennent le centre-ville.** Les quatre sortes déclarent `districts: ("faubourg",)` —
  c'est le centre-ville ouvrier (`devantures.py` le dit déjà en toutes lettres) et c'est le
  district le plus peuplé. Un amuseur joue là où il y a du monde ; ailleurs, il joue pour les
  goélands.
- **Et il y a plus de monde au centre, moins en périphérie.** `carte.py` donne à chaque
  district son nombre de piétons : le Faubourg monte, les Érables, La Shop et La Pointe
  baissent. ⚠️ Le plafond de la bulle (`MAX_PIETONS`) ne bouge pas : c'est la **répartition**
  qu'on change, pas le budget d'image — un quartier plus dense doit se payer avec la foule d'un
  quartier plus vide.

⚠️ **Le budget du paquet.** Cinq morceaux de plus, c'est le catalogue de musique qui passe de
25 à ~33 Ko — le plafond du juge est à 48 Ko, et aucun fichier audio n'est téléchargé : une
pièce écrite en notes pèse 1,6 Ko, une minute de mp3 en pèse 500.

**Livré le 14 sept. 2026**, et trois choses se sont révélées en chemin :

- ⚠️ **Deux artistes se volaient leur public, et rien ne le disait.** `recrutable` ne refusait
  qu'un badaud déjà dans SON cercle : le second artiste né dans le quartier, n'ayant personne
  de libre à portée, prenait les trois du premier — qui restait **seul au milieu de sa scène
  et n'en retrouvait plus jamais**. Un numéro sans personne, c'est exactement ce que Martin a
  signalé ; le faire arriver à coups de règles neuves aurait été une belle façon de ne rien
  réparer. On ne vole plus le public du voisin.
- ⚠️ **La relève part AVANT que la place se libère.** Un remplaçant traverse la rue à pied :
  attendre que le cercle tombe à deux pour l'appeler, c'est deux secondes à deux. On compte
  donc ceux qui seront **encore là quand il arrivera** — et **le dernier ne part pas** tant
  que la relève n'est pas assise. Mesuré : le cercle passait sous 3 pendant **6,3 %** du temps
  avant ces deux règles, **0,1 %** après (une seule fois, onze images).
- ⚠️ **Le contrat porte sur ce qu'on VOIT.** Un artiste naît hors champ, à l'autre bout du
  quartier ; s'il n'y a personne de libre hors écran, son cercle met quelques secondes à se
  faire — les badauds marchent, ils ne se matérialisent pas. Sur 1800 images où un amuseur est
  **à l'écran**, il n'a jamais eu moins de 3 ni plus de 5 personnes autour, et **jamais zéro**.
  C'est ce que le juge mesure, et c'est ce qui se voit.

Et deux juges qui tenaient par chance sont tombés, parce qu'une routine de plus **décale le
dé** : celui du touriste sortait de sa boucle au **premier arrêt** (or un flâneur s'arrête
aussi tout seul, et `majPhoto` ne part que depuis `flane`), et celui du stationnement
**espérait** que le quartier finisse par remplir ses rues. Les deux mesurent maintenant la
règle au lieu d'espérer le hasard — c'est la leçon que la chute de l'ivrogne avait déjà écrite.

- **Juges (9 neufs)** : côté Python, chaque sorte a son corps, son métier et ses quartiers ;
  les cinq pièces de rue ont toutes leurs notes **dans leur gamme**, aucune ne déborde de sa
  boucle, deux n'ont ni le même tempo ni la même tonalité ni la même mélodie, et il y a **une
  valse et une seule**. Au banc (`tests/test_amuseurs_js.py`) : les quatre ne naissent **qu'au
  centre-ville**, ils partagent un plafond de deux, le cercle tient **entre 3 et 5 à chaque
  image où on les voit** dans une rue qu'on n'a pas garnie à la main, les quatre **changent
  d'image** (et de vrai dessin — un `poseFixe` qui tourne dans le vide les fait rougir),
  l'échassier **dépasse le plus grand corps de la ville de huit pixels**, le musicien **pose
  des notes qui atteignent la sortie**, plus fort de près que de loin, et **se tait** quand on
  s'en va ; le public **applaudit, paie et se renouvelle** ; et aucun artiste ne se plante
  **hors d'une scène de la carte**.

### Un poteau par coin, pas quatre (**correctif**, taille 1) — **livré le 14 sept. 2026**

_Retour de Martin, une fois les feux visibles :_ « refais une passe de validation visuelle des
feux, car il y en a trop, il faut que ce soit plus réaliste. »

Il avait raison, et la mesure a trouvé pire que « trop ».

- ⚠️ **Les 124 feux de chars étaient plantés DANS un poteau piéton** — à la tuile près, 124 sur
  124, pas un seul qui ne le soit. `coinLibre` vise le coin **nord-est** et le coin **sud-ouest**
  du croisement ; `carte.py` pose ses feux piétons au **bout de chaque traverse**, ce qui est
  exactement ces coins-là. Et `coinLibre` ne les voyait pas : il n'écarte que le décor **solide**
  (`decorAutour` lit `grilleFixe`), où un feu n'entre jamais — il n'est pas solide. Tant que les
  lanternes n'étaient pas peintes, deux poteaux noirs l'un dans l'autre ne se voyaient pas ; le
  correctif d'avant les a rendus visibles, et le défaut avec.
- ⚠️ **Et il ne fallait surtout pas les écarter d'une tuile.** Ça aurait fait un poteau **de
  plus** à regarder, au lieu d'un de moins. La mesure suivante dit quoi faire à la place : en
  groupant les poteaux d'un croisement par proximité, **chaque croisement en donne exactement
  trois grappes**, et sur 186 grappes il y en a **174 de deux poteaux — tous à UNE tuile d'écart,
  pas un seul à deux**. Une tuile, c'est deux mètres et demi. Ce ne sont pas deux endroits, c'est
  **un coin de rue**, et dans la vraie vie ces deux têtes-là sont sur le même mât.
- **Un mât par coin, jusqu'à trois têtes.** Les feux des chars se posent **d'abord** ; chaque
  traverse cherche ensuite le mât de son coin (la tuile même, puis l'anneau d'une tuile) et lui
  accroche sa tête — au plus deux, celles des deux rues qui s'y croisent. Ce qui ne trouve pas de
  mât en plante un.
- **484 poteaux → 186**, soit **3 par croisement au lieu de 8** (124 mâts de chars, 62 poteaux
  seuls). ⚠️ **Et les 360 traverses sont toujours montrées** : un juge compare le nombre de têtes
  peintes au nombre de traverses que la carte pose. On a retiré des **poteaux**, pas de
  l'**information** — c'est toute la différence entre alléger et amputer.
- ⚠️ **À deux têtes, les ampoules rétrécissent à trois pixels** et se posent aux **mêmes colonnes**
  que celles des chars, juste au-dessus. Deux raisons, et la seconde n'est pas du goût : à quatre
  pixels chacune elles se **toucheraient**, et deux rouges qui se touchent font un seul rectangle
  rouge. L'alignement, lui, est ce qui fait lire le mât comme **un** poteau plutôt que comme deux
  collés — un empilement de boîtiers dont les feux tombent sur la même verticale.
- ⚠️ **Deux rangées de vide entre la tête des chars et celle des piétons.** Collées, les deux ne
  font qu'un bloc noir et on ne voit plus qu'il y en a deux. Et la tête est à la **hauteur du
  poteau isolé**, à un pixel près : la même tête au même niveau, qu'elle ait son mât ou qu'elle le
  partage.
- **Juges (2 neufs)** : aucun poteau planté dans un autre, aucune paire de mâts du **même
  croisement** à une tuile, aucun mât à plus de deux traverses, **autant de têtes que de traverses
  posées par la carte**, et le compte borné à trois par croisement — sans cette borne-là, un jour
  ou l'autre on en remet. Le premier est **rouge sur le code d'avant** : « 124 poteaux plantés
  dans un autre ».
- **Ce qui reste ouvert** : un croisement n'a de poteau qu'à **trois** coins — le quatrième est
  refusé par `carte.py` quand le trottoir y est déjà pris. Ça se voit peu, et ça se corrigerait
  côté carte, pas côté dessin.

### Des feux tricolores, à la québécoise (**correctif**, taille 2) — **livré le 15 sept. 2026**

_Demandes de Martin, dans l'ordre :_ « les feux pourraient être mieux, cherche sur le web des
représentations visuelles » · « assure-toi que les feux et les voitures suivent la même logique »
· « je veux des feux tricolores et un seul allumé à la fois » · « les feux piétons sont à part
mais les piétons le respectent (sauf exception) et les véhicules aussi (sauf exception) » · « mets
les lumières qui tiennent d'un seul bout sur le poteau et la partie dans le vide au-dessus de la
route » · « moins de lignes pour les traverses piétons » · « ne mets pas de lampadaire aux
intersections, déplace-les, ça va laisser la place libre aux feux ».

⚠️ **La recherche a donné mieux qu'une référence de pixel art.** Au **Québec**, les feux sont
**horizontaux**, et leurs lentilles ont des **formes** : le rouge **carré**, le jaune en
**losange**, le vert **rond**. Ce n'est pas un détail pittoresque — c'est fait pour qui ne
distingue pas le rouge du vert (le Nouveau-Brunswick, la Nouvelle-Écosse, l'Île-du-Prince-Édouard
et l'est de l'Ontario ont suivi). Et ça règle du même coup le problème de lisibilité du jeu : **à
trois pixels, une forme se lit quand une teinte se devine**. La signalisation d'ici était déjà la
réponse.

- **Un vrai tricolore, une seule lentille allumée.** Avant, un boîtier portait **deux** lanternes,
  une par axe, chacune changeant de couleur : ce n'était pas un feu, c'était deux témoins. Un mât
  montre maintenant **une rue** et **une couleur** ; les deux autres lentilles sont des **douilles
  éteintes**, cuites dans la fiche, chacune dans un ton très sombre de sa couleur — c'est ce qui
  fait qu'on voit qu'il y en a trois, et laquelle brille.
- ⚠️ **Une seule source pour la couleur.** `Monde.feuDeCirculation()` rend `vert`, `jaune` ou
  `rouge` ; `feuVert` en **découle** (`=== 'vert'`), le **dessin** en découle, et le trafic obéit à
  `feuVert`. Un feu ne peut donc plus montrer une couleur qu'un char ne respecte pas : c'est la
  même phrase lue deux fois, jamais deux phrases. Le feu piéton s'était trompé d'un temps
  exactement parce qu'il relisait `!feuVert` au lieu d'avoir sa règle — on ne recommence pas.
- ⚠️ **Le jaune n'est pas vert.** Un char qui arrive à la ligne d'arrêt sur le jaune s'arrête.
  Sans ça, le dégagement du feu piéton ne servirait à rien : le croisement ne se viderait jamais.
- **L'exception, c'est la sirène.** En poursuite, un char brûle le feu, le STOP et la boîte — une
  auto-patrouille qui attend au rouge pendant que le joueur s'enfuit n'est pas une poursuite. Un
  juge neuf pose un char sur une ligne d'arrêt et mesure : il ne bouge pas au rouge, pas au jaune,
  il part au vert, et il passe au rouge sirène allumée.
- **Quatre mâts, un par coin** — ce qui règle le coin manquant laissé ouvert la veille. ⚠️ Et
  l'**axe suit la diagonale** : nord-est et sud-ouest portent le nord-sud, nord-ouest et sud-est
  l'est-ouest. Qui arrive du sud a les deux coins nord devant lui, donc un de chaque diagonale,
  donc un feu de **son** axe. Ce n'est pas une convention de goût : c'est une propriété, et un
  juge la vérifie **pour les quatre approches, à tous les croisements de la ville**.
- **Une potence, pas un poteau.** Le mât est planté au **bord du trottoir**, côté rue, et la tête
  porte à faux **au-dessus de la voie**. ⚠️ Planté au **centre** de sa tuile — ce qu'il était —,
  dix des treize pixels du bras restaient au-dessus du **trottoir** : la tête n'était pas sur la
  chaussée, elle était à côté. Collé au bord, le bras passe la bordure à trois pixels.
- ⚠️ **Un seul gabarit, et un miroir.** Tout est écrit « bras vers l'est » ; un mât tourné vers
  l'ouest se peint avec les **mêmes nombres** passés par `miroir()`, des deux côtés (la fiche cuite
  **et** la lentille vive — si les deux ne retournaient pas pareil, elle s'allumerait à côté de son
  trou). Et le miroir **retourne l'ordre des lentilles**, ce qui est juste : le rouge est à gauche
  **du conducteur**, et deux têtes qui se regardent en sens opposés se voient à l'envers l'une de
  l'autre, vues d'en haut.
- **Moins de lignes aux traverses, et la norme dit combien.** Une bande de passage fait **0,50 m**
  et l'interdistance **0,50 à 0,80 m** : le **vide est plus large que la bande**. Ici c'était
  l'inverse (3 px de bande, 2 de vide) et un passage se lisait comme un mur blanc. À l'échelle du
  jeu (1 px ≈ 0,20 m), c'est **3 de bande, 5 de vide**. ⚠️ **Et le pas divise la tuile** : à 5, les
  bandes tombaient à 1, 6, 11 — deux pixels de vide dedans, **trois à la couture** entre deux
  tuiles. Le motif boitait à chaque tuile sans qu'on sache pourquoi. À 8, elles tombent à 1 et 9 et
  le vide fait cinq **partout**, couture comprise.
- **Les lampadaires quittent les coins.** `lampadaires()` les plantait **sur** les coins du
  croisement — la place du mât. Tant qu'il n'y avait que deux mâts et aucune lanterne peinte, ça ne
  se voyait pas ; à quatre mâts peints, ils se disputaient la tuile au vu de tous. Ils s'écartent
  de **trois tuiles le long de la rue** (jamais en diagonale : un poteau qui recule de biais finit
  au milieu d'un parterre), et **316 lampadaires, zéro sur un coin réservé**. Ils éclairent
  d'ailleurs mieux là : entre deux croisements plutôt que dessus.
- **Juges (5 neufs)** : un tricolore n'allume **qu'une** lentille, à la colonne de sa couleur et de
  sa **forme**, à cinq instants du cycle ; ce qu'il **montre** et ce que le char **respecte** ne
  peuvent pas diverger ; de chacune des quatre approches un feu de son axe est en face ; un char
  s'arrête au rouge et au jaune, part au vert, et brûle le rouge sirène allumée ; aucun lampadaire
  sur un coin réservé au feu. Les deux juges du dessin **lisent le gabarit dans `DECORS.feu`** au
  lieu de le recopier — et le miroir avec, sans quoi ils chercheraient la lentille du mauvais côté
  et diraient « le feu est éteint » alors qu'il brille.
- **Les lampadaires et les bornes quittent les coins.** `lampadaires()` plantait ses poteaux **sur**
  les coins du croisement — la place du mât. Tant qu'il n'y avait que deux mâts et aucune lanterne
  peinte, ça ne se voyait pas ; à quatre mâts peints, ils se disputaient la tuile au vu de tous. Ils
  s'écartent de **trois tuiles le long de la rue** (jamais en diagonale : un poteau qui recule de
  biais finit au milieu d'un parterre) — **316 lampadaires, zéro sur un coin réservé**. Ils
  éclairent d'ailleurs mieux là : entre deux croisements plutôt que dessus.
- **La borne-fontaine : rouge, et elle crache.** Elle était **jaune** — au coin d'une rue, une tache
  jaune se lit comme une borne de stationnement, pas comme de l'eau. ⚠️ Et c'était une **tuile**
  (`'b'`, solide) : une tuile ne se casse pas, elle ne pouvait donc ni tomber sous un char ni gicler.
  C'est maintenant un **décor** avec sa fiche — `casse: 0.75`, `pv: 40`, moins qu'un lampadaire (60),
  et c'est la vraie borne qui le dit : elle est boulonnée sur des vis qui **cassent exprès**, pour
  qu'un char l'arrache au lieu de se plier autour. Défoncée, elle crache **dix secondes** : une
  **entité invisible** qui vit sa minuterie et lâche deux gouttes par image — le patron du brasier du
  Molotov, et la même raison, on ne repeint pas une tuile à chaque image pour un effet qui passe.
  ⚠️ **Son bruit emprunte `choc` et synthétise l'eau** : le seau des bruitages est à 14 Ko de son
  plafond, un échantillon à elle attendra une séance ElevenLabs.
- ⚠️ **Et un vieux juge a rougi sans qu'une ligne de son code change** : celui de la fille de la
  Brume. Il prenait son écart maximum sur quarante secondes, **fuite comprise** — une fille qui
  détale d'un coup de feu court 240 px, et c'est exactement ce qu'elle doit faire ; une fois partie
  elle ne revient pas, parce que la fuite lui fait traverser une rue et qu'un passant ne remet pas le
  pied sur la chaussée hors d'un passage. Il tenait par chance, et trois tuiles de lampadaire ont
  suffi à le faire tomber. Il mesure maintenant le **contraste** avec une passante **sur la même
  fenêtre** — un rapport juge la règle, un seuil en pixels juge le trajet qu'une graine a tiré.
  ⚠️ **Essayé et annulé** : lui donner un vrai cap de retour à chaque image la collait au trottoir à
  vibrer contre la bordure dès que le chemin direct était barré. La ramener demanderait un vrai
  chemin (`Monde.chemin`), pas un cap — c'est écrit dans le juge.

- **Ce qui reste ouvert** : les quatre bras d'un croisement portent tous au-dessus de la rue
  **nord-sud** (c'est la géométrie des coins), jamais au-dessus de l'est-ouest. Ça ne se voit pas,
  mais un vrai carrefour les alterne.

### M15 — La ville te parle (**ajout**, taille 4) — **1re vague livrée le 14 sept. 2026**

_Ce que ça donne :_ le jeu cesse d'être muet entre deux répliques de mission — et il
t'apprend enfin ce qu'il sait faire.

**Première vague livrée le 14 sept. 2026** — et la vague se prend en deux, pour une raison
simple : la moitié de M15 demande des **clips ElevenLabs**, donc des crédits, donc une oreille
que je n'ai pas. Cette première moitié ne demande **aucun son neuf**.

- **La rue se tait quand tu sors une arme.** L'ajout le moins cher de toute la vague, et celui
  qui se sent le plus : `Son.Rumeur` réglait déjà son volume sur le nombre de gens autour — il
  ne manquait qu'une **raison** de le faire tomber. Elle tombe d'un coup à 18 % et remonte en
  quatre secondes. ⚠️ Et **après un coup de feu, elle ne reprend pas au même endroit** : elle
  revient en **cris** (1,7 fois son volume), puis se calme. Une foule qui murmure pareil avant
  et après un mort n'est pas une foule, c'est un bruit de fond. Au volant, rien : on ne voit
  pas ce que tu tiens.
- **Les répliques : moins souvent, et jamais les mêmes.** ⚠️ `audio.VOIX` promettait « jamais
  deux fois de suite le même » — **c'était faux, et ça l'a toujours été** : le moteur tirait
  par `Math.random()` sans aucune mémoire. Sur quatre répliques par genre, une chance sur
  quatre de répéter la précédente. Le tirage écarte maintenant les dernières, **et passe par
  `B.rng()`** : tout le hasard du jeu y passe déjà, c'est ce qui rend le banc reproductible —
  donc juge. Cette ligne-là lui échappait, et c'était précisément celle qu'on voulait pouvoir
  tester.
  - ⚠️ **La mémoire est à DEUX, pas à quatre** comme la fiche l'annonçait : la plus petite
    banque en compte **trois** (le crieur). Pour en exclure quatre, il en faudrait six par
    banque — ce nombre monte le jour où les banques montent, et **un juge tient les deux
    ensemble** pour qu'on ne puisse pas bouger l'un sans l'autre.
  - **Parler devient une chance** (35 %), pas une certitude : un passant qui parle chaque fois
    qu'on le frôle rend huit répliques fatigantes bien avant qu'elles soient usées.
- **Le repli du Clairon enseigne.** Six leçons, une par matin calme : le klaxon des boulots,
  la fourrière, le café, le garage, les propriétés, les clôtures qui s'enjambent. ⚠️ **On
  n'enseigne que ce que le joueur n'a pas fait** (chaque leçon dit par quelle statistique on
  prouve qu'on sait déjà), **jamais deux fois la même** (la partie retient), et quand il n'y a
  plus rien à apprendre le repli **redevient** « rien à signaler » — ce qui est une bonne
  nouvelle. Le narrateur les lit comme une manchette. ✅ **Les six mp3 existent depuis le 16 sept. 2026**
  et l'encadré a sa voix : `exporter()` les déclare tout seul, **sans une ligne de code** —
  la porte ouverte par la 1re vague s'est refermée d'elle-même le jour où les fichiers sont
  arrivés.

⚠️ **Deux défauts trouvés en chemin, et le second ne se voyait pas du tout :**

- **Un enfant naissait dans le mur.** Le petit d'une mère naît à côté d'elle (`x + 10`), et
  **personne ne vérifiait la tuile** : une mère née au ras d'une façade posait son enfant
  dedans — et de là il ne pouvait plus sortir, le masque du piéton ne laissant pas sortir d'un
  mur plus qu'il n'y laisse entrer.
- **`Rumeur.maj` ne tourne qu'une image sur quinze**, et le compteur de peur se décrémentait
  de **un** par appel : 240 images de peur en duraient 3 600. La rue ne revenait jamais — et
  ça ne se voit pas, ça ressemble juste à une ville silencieuse. Les deux minuteries sont
  maintenant des **échéances** en `B.t` : une échéance ne se trompe pas de cadence.

**Ce qui reste, et ce que ça coûte** : la radio qui parle (animateur, pubs, bulletin), la
police à la radio, les bruits de quartier, le souffle du joueur, et les banques de répliques
par contexte — une cinquantaine de clips ElevenLabs. C'est la deuxième vague, et elle demande
les crédits de Martin **et son oreille** : aucun juge ne dit qu'un son est le BON son.

⚠️ **Cette vague ne dépend de rien.** C'est celle qu'on prend quand on veut un gain rapide :
les trois morceaux passent par des pièces déjà en place (le narrateur de M7, le journal de
M5, les voix de M6), et aucun ne touche à la physique ni à la carte.

- **Le journal du matin t'apprend à jouer.** Le jeu a maintenant des boulots au klaxon, une
  fourrière, un marché noir, des propriétés, trois défis — et **rien n'explique rien** : M1
  apprend à marcher et à voler un char, et après ça le joueur est tout seul. Or `journal.py`
  trie déjà ses règles du plus grave au plus banal et finit par un repli « rien à signaler ».
  Ce repli devient **un encadré qui enseigne une chose** — « Saviez-vous qu'un coup de klaxon
  dans un taxi vous trouve un client? ». Une par jour, lue à voix haute par le narrateur qui
  existe déjà, **sans une seule fenêtre de plus**.
  - ⚠️ On n'enseigne que ce que le joueur n'a **pas encore fait** : `p.stats` le sait. Un jeu
    qui explique le taxi à quelqu'un qui a fait trente courses n'explique rien, il agace.
  - Jamais deux fois la même : la partie garde ce qui a été lu. Quand il n'y a plus rien à
    apprendre, le repli redevient « rien à signaler » — et c'est une bonne nouvelle.
- **La radio parle.** Les trois stations sont des boucles instrumentales ; or l'âme d'une
  radio, c'est ce qui se dit **entre** les tounes. Tout le mécanisme est là : `Son.Voix`, le
  ducking, le filtre du combiné. Un clip toutes les deux ou trois boucles, en trois sortes :
  - **un animateur par station** — feutré à La Brume, jovial au Taxi-Radio, et personne au
    Choc : juste un jingle, c'est le propos de la station ;
  - **des pubs** pour des commerces qui existent (Chez Gus, Boutique Rosa, le Dépanneur
    Ti-Paul). ⚠️ **La pub change quand tu achètes le commerce** — c'est cette ligne-là qui
    fait que ça vaut la peine, et pas une autre ;
  - **un bulletin de nouvelles** qui rejoue la manchette de `journal.py` : la radio parle
    donc de **ce que tu as fait hier**, dans un char que tu viens de voler.
  - Une vingtaine de clips à 40 Ko : 800 Ko, largement sous le plafond de 3 Mo des voix. Et
    la règle de `audio.py` tient toujours — `exporter()` ne déclare que les fichiers
    présents, une station sans animateur joue simplement sa musique.
- **Les passants : plus de choses, moins souvent, et jamais les mêmes** — demande de
  Martin, et **pour moitié un correctif** : « plus de choses » est un ajout, « jamais les
  mêmes » répare une promesse écrite dans le code et jamais tenue.
  Aujourd'hui il y a **huit** répliques — quatre par genre. Un passant parle dès qu'il passe
  à 30 px, avec un temps mort global de 4 secondes, et la réplique est tirée par un
  `Math.random()` **sans aucune mémoire**. Sur quatre choix, une chance sur quatre de répéter
  la précédente : dans une rue passante, on entend « Fait frette, hein? » trois fois en vingt
  secondes. ⚠️ Le commentaire d'`audio.VOIX` promet pourtant « jamais deux fois de suite le
  même » — **c'est faux**, et ça l'a toujours été : un tirage au hasard peut sortir deux fois
  le même, c'est même sa définition.
  - **Plus de choses.** La banque grossit, et elle grossit **deux fois** : `audio.VOIX` gagne
    un champ `quand` (`normal`, `peur`, `celebre`, `nuit`), et chaque contexte a ses
    répliques. La ville se met à te reconnaître au lieu de te dire bonjour pendant que tu
    saignes.
  - **Moins souvent.** Le temps mort monte, et surtout **parler devient une chance, pas une
    certitude** : la plupart des gens qu'on croise ne disent rien, comme dans la vraie vie.
    Un passant qui parle à chaque fois qu'on le frôle, c'est ce qui rend huit répliques
    fatigantes bien avant qu'elles soient usées.
  - **Jamais les mêmes.** Le moteur garde les **quatre dernières** répliques dites et les
    exclut du tirage. ⚠️ **Ça impose une taille minimale à chaque banque** : pour en exclure
    quatre, il en faut au moins six, sinon il ne reste rien à tirer et la règle se retourne
    contre elle-même. C'est un test, pas une intention — et une banque trop courte retombe
    sur `normal` plutôt que de se répéter.
  - ⚠️ **Et le tirage passe par `B.rng()`**, pas par `Math.random()`. Tout le hasard du jeu
    y passe déjà — c'est ce qui rend le banc reproductible et donc juge. Cette ligne-là lui
    échappe, et c'est précisément celle qu'on veut pouvoir tester.
  - Le compte : 4 contextes × 2 genres × 6 répliques = **48 clips**, soit environ 1,2 Mo —
    sous le plafond de 3 Mo des voix. Et la règle d'`audio.py` tient : `exporter()` ne
    déclare que les fichiers présents, une banque vide se rabat sur `normal`.
- **Le silence quand tu sors une arme.** C'est l'ajout le moins cher de toute la vague et
  celui qui se sent le plus. `Son.Rumeur.maj(gens)` règle déjà le volume de la foule sur le
  nombre de personnes autour — **il ne manque qu'une raison de le faire tomber**. Une rue qui
  se tait d'un coup dit « ils t'ont vu » mieux qu'une étoile de plus, et elle le dit avant que
  tu regardes le HUD. Elle remonte quand la peur passe.
  - ⚠️ Et le contraire compte autant : après un coup de feu, la rumeur ne reprend **pas** au
    même endroit — elle revient en cris, puis se calme. Une foule qui murmure pareil avant et
    après un mort n'est pas une foule, c'est un bruit de fond.
- **La police se parle à la radio.** On voit les cônes, on voit les blips, on n'entend rien —
  alors qu'une poursuite est ce qu'il y a de plus tendu dans le jeu. Cinq répliques courtes
  suffisent : _il l'a repéré_, _la poursuite commence_, _on l'a perdu_, _un barrage se pose_,
  _l'hélico décolle_. Filtrées comme le combiné du téléphone (le filtre existe depuis M6),
  elles rendent la police **lisible à l'oreille** — on sait ce qui va nous tomber dessus sans
  quitter la route des yeux.
  - ⚠️ Elles passent **au-dessus** de la musique de poursuite dans l'échelle ci-dessus, sinon
    elles arrivent pile quand on ne peut plus les entendre.
- **Les bruits de quartier, ponctuels.** Distincts de la musique de district : ce ne sont pas
  des nappes, ce sont des **événements** — une mouette et une corne de brume aux Quais, un
  martèlement lointain à La Shop, une tondeuse et des oiseaux aux Érables, le vent dans les
  arbres à La Pointe. Trois ou quatre par district, tirés rarement, et un quartier s'entend
  avant de se voir. Beaucoup moins cher qu'une piste : ce sont des bruitages, pas de la
  musique.
- **Le souffle du joueur.** Il sprinte, il s'essouffle, et on n'entend rien. Un halètement qui
  monte avec la dépense, et une inspiration quand le souffle repart : ça rend la barre
  d'endurance lisible **sans la regarder**, et ça vaut double depuis que le sprint est devenu
  une ressource qu'on dépense par bouffées.
- **Juges** : une leçon ne se donne qu'une fois et jamais sur ce qui est déjà fait ; un clip
  de radio ne coupe jamais une réplique de mission (le ducking a déjà sa file d'attente) ;
  la pub d'un commerce possédé n'est plus celle d'un commerce à visiter ; **aucune des quatre dernières
  répliques dites ne peut ressortir**, et toute banque où l'on tire en contient au moins six
  (quatre à exclure, deux pour que ça reste un tirage) ; le tirage passe par `B.rng()`, donc
  le banc peut jouer mille rencontres et compter les répétitions — il doit en trouver zéro.

### M11 — La police apprend (**ajout**, taille 2)

_Ce que ça donne :_ un casier qui pèse, et des façons de le faire taire.

- **Le carnet du poste** : au poste, ton casier, tes affiches, tes surnoms. Plus il est
  épais, plus les agents te reconnaissent **de loin** (la portée du cône monte avec le
  casier) — en plus des amendes et des pots-de-vin, qui en tiennent déjà compte.
- **Le stool** : un passant qui te reconnaît et part téléphoner. L'acheter, le suivre, ou
  le faire taire : chacun a son prix en étoiles.
- **L'avocat du Carré** : cher, il efface une page du casier ou te sort de prison sans
  amende — et il ne travaille pas deux fois la même journée.
- **Le hacker** (demande de Martin) : quelque part en ville, quelqu'un entre dans le fichier
  de la police et efface du casier — **de façon variable**, contre rémunération.
  - ⚠️ **Il doit être le CONTRAIRE de l'avocat, pas son doublon.** L'avocat du Carré est
    légal, cher, sûr : une page, une fois par jour. Le hacker est **le pari** — moins cher la
    page, mais on paie **d'avance** sans savoir combien il effacera : de rien du tout à
    plusieurs pages d'un coup.
  - ⚠️ **Et son espérance doit rester SOUS l'avocat à prix égal**, sinon l'avocat ne sert plus
    à rien et le choix disparaît. C'est la règle de tout le reste : la certitude se paie plus
    cher que la chance, jamais l'inverse.
  - **Où** : pas au Carré, pas au bar — le marché noir y est déjà, et un deuxième comptoir au
    même endroit n'est plus un trajet. Il travaille dans **La Shop**, le district qui tombe à
    0,15 la nuit : y aller quand il travaille, c'est y aller seul. Le trajet fait le risque,
    comme la caisse d'une propriété.
  - **Ça prend du temps**, pas un clic : on paie, on revient **le lendemain**. Un trajet de
    plus, et de quoi se refaire un casier entre-temps.
  - ⚠️ **Le risque est réel dans les deux sens.** Payer quelqu'un pour entrer dans le fichier
    de la police est un délit : s'il rate, ça peut **ajouter** une page au lieu d'en enlever —
    et le **stool** de cette même vague peut apprendre qu'on y est allé. C'est ce qui empêche
    le hacker de devenir un bouton « annuler la partie ».
- **Bouclier humain** (risqué) : attraper un piéton à bout portant — en **tenant** ACTION une
  demi-seconde, parce que c'est le dernier geste de la chaîne, donc celui qu'on faisait par
  accident ; la police ne tire plus, mais le compteur monte et le piéton se débat.
- **Juges** : la portée du cône reste bornée quel que soit le casier ; le stool ne naît pas
  dans le dos d'un joueur immobile ; l'avocat ne rend jamais un casier négatif ; le hacker non
  plus, il ne vide jamais un casier plein en une visite, son espérance reste sous l'avocat à
  prix égal, et **effacer coûte toujours plus cher que ce que le casier coûte** — sinon le
  casier ne veut plus rien dire, et tout M11 avec lui.

### M10 — L'argent sale (**ajout**, taille 3)

_Ce que ça donne :_ une raison de se lever le matin — la dette de Rocco.

- **Le shylock** : 15 000 $, un intérêt par jour, des rappels au téléphone, puis des hommes
  de main qui te trouvent où que tu sois. Rembourser ouvre une des deux fins (M13).
- **Guichets** : les défoncer au camion (bruyant, 2★, la caisse par terre) ou poser un
  **skimmer** et revenir le lendemain (silencieux, lent, il peut être trouvé).
- **Assurance et fraude** : assurer un char au garage, le faire disparaître, encaisser —
  trois fois de suite et l'assureur enquête.
- **La run** (ajouté le 15 sept. 2026, de la tournée du net) : le commerce d'un district à
  l'autre — acheter bas, vendre haut. C'est le cœur de Chinatown Wars, et ici il ne demande
  ni marchandise neuve ni personnage neuf : **la contrebande de Sven** (caisses de cigarettes
  et de boisson) s'achète au quai et se revend au dépanneur, à la taverne, au bar, à la
  cantine. Un prix par district qui **bouge chaque jour** (la graine du jour, comme les
  entraves), affiché au comptoir ; le stock se transporte dans le coffre, donc un char qui
  brûle brûle la run avec.
  - ⚠️ **Ce qui empêche la machine à argent** : la police **fouille**. Se faire arrêter avec
    des caisses, c'est les perdre en entier (et c'est pour ça que l'île — pas de police — vaut
    le détour). Le prix d'achat monte avec ce qu'on a déjà acheté dans la journée, et la
    marge d'une run complète reste **sous celle d'une mission de l'arc où on se trouve** :
    un commerce qui paie mieux que l'histoire vide l'histoire.
  - ⚠️ **Et un garde-fou de ton, tranché ici** : de la boisson et du tabac de contrebande,
    pas de la drogue. Le jeu se moque de la ville, il ne vend pas ça.
- `economie.py` : dette, intérêts **bornés**, primes, seuils de suspicion.
- **Juges** : la dette ne dépasse jamais son plafond ; un joueur qui ne fait rien ne devient
  pas insolvable en une nuit ; la fraude rapporte **moins à l'heure** que le travail honnête
  — sinon le jeu se joue tout seul et le taxi ne sert plus à rien.

### Ça travaille : maisons, commerces et rues en chantier (**ajout**, taille 3)

_Demande de Martin (15 sept. 2026) :_ « je veux des zones comme des maisons ou commerces ou
des rues soit en construction avec des pelles, des boules de démolition, des… » puis, tout de
suite après : « des grues ».

**Ce qui existe déjà, et c'est presque tout** — la fiche est courte parce que le dépôt a fait
le gros du travail sans le savoir :

- le **terrain vague** est un genre de parcelle depuis M1 : ceinturé de grillage (de barbelé
  dans La Shop), ouvert au nord sur la ruelle, avec du décor semé dedans. Une parcelle sur
  vingt au centre, une sur huit ailleurs ;
- les **entraves** de M12 font déjà la rue : une voie fermée, des cônes, un détour, tirés par
  la graine du jour ;
- le **décor se brise** (20 fiches `DECORS` avec leur `pv`), et `reparerLeDecor()` remet tout
  au matin ;
- et surtout : **une tuile se change en cours de partie**, avec ses morceaux voisins recuits —
  c'est le chemin qu'emprunte une clôture qu'on défonce.

Ce qui manque n'est donc pas la mécanique. C'est qu'**aucun endroit de la ville ne dit
« ça travaille ici »**.

**La règle : un chantier est un état de parcelle, pas un dessin.** `carte` déclare des
`CHANTIERS` — une parcelle, un genre (démolition, construction, réfection de rue), et une
**phase**. Le reste en découle, et voici la seule idée qui compte :

⚠️ **Un chantier est une HORLOGE, pas un décor.** La partie compte les jours (`p.jour`) et
personne ne s'en sert pour changer la ville. Un chantier avance :

| Phase | Ce qu'on voit | Ce que ça change |
|---|---|---|
| 0 | la maison debout, des pancartes, des fenêtres placardées | la porte est condamnée |
| 1 | la **boule de démolition**, la moitié du mur par terre, la poussière | le bâtiment devient franchissable en partie |
| 2 | le terrain rasé, la **pelle** qui charge un camion, un tas de terre | un terrain vague… qui n'était pas là hier |
| 3 | la dalle, l'**échafaudage**, la **grue** qui tourne | on peut y grimper (la clôture s'enjambe déjà) |
| 4 | un bâtiment neuf, propre, une devanture qui n'existait pas | une porte de plus dans la ville |

Deux ou trois chantiers par partie, chacun avançant d'une phase tous les trois ou quatre
jours. Au bout d'une vingtaine de jours, **la ville n'est plus celle du premier matin** — et
c'est la seule façon honnête de faire sentir le temps dans un jeu où il ne se passe rien
entre deux missions.

**Les machines** — et ⚠️ **c'est là que le plan se mord la queue** : une pelle et une grue
sont des véhicules, et la fiche de la refonte des véhicules (plus haut) dit noir sur blanc
qu'on n'ajoute **aucun char** avant qu'elle soit faite. Deux étages, donc :

- **Étage 1, sans un seul véhicule neuf** : la pelle, la grue et la boule sont du **décor
  animé**. Elles ne roulent pas — elles **travaillent** : le bras de la pelle monte et
  descend, la flèche de la grue tourne lentement, la boule se balance et **casse ce qu'elle
  touche** (`endommagerDecor` existe). ⚠️ Une articulation, pas dix : le feu de circulation
  fait déjà exactement ça — un poteau cuit une fois, des lanternes peintes par-dessus à
  chaque image.
- **Étage 2, après la refonte** : la pelle se conduit. Et elle est drôle pour une raison
  précise, déjà écrite dans les fiches : `defonce`. Elle roule à 12 km/h et **passe à
  travers** ce qu'aucun autre char ne défonce. La grue, elle, ne roulera jamais — on monte
  dans la cabine, on tourne la flèche, et c'est tout ce qu'on lui demande.

**Le réservoir** (la phrase de Martin s'arrête sur « des… » : voici de quoi la finir). Chaque
idée porte ce qu'elle **fait**, parce qu'un chantier qui ne fait rien est un fond d'écran :

- **La boule de démolition** — elle se balance sur son câble, et ⚠️ **elle frappe pour vrai** :
  passer dessous en char, c'est un choc et une carcasse. Le seul décor du jeu qui attaque.
- **La grue à tour** — sa flèche tourne, son contrepoids suit, et elle se voit **de l'autre
  bout du district**. C'est un point de repère, donc un lieu de mission gratuit.
- **La pelle et le bulldozer** — le godet levé fait une **rampe** (les rampes sont livrées),
  et une pelle garée à côté d'un mur est une façon d'entrer dans une cour.
- **Le tas de terre ou de gravier** — une rampe naturelle, en plus doux. ⚠️ C'est le décor le
  plus rentable de la liste : il ne coûte qu'un dessin et il change la carte.
- **Le conteneur à déchets** — il se pousse (la physique des chars pousse déjà), donc il se
  place. Et il cache ce qu'on veut y cacher.
- **La tranchée et ses plaques d'acier** — rouler dessus **claque** : un son, une secousse, et
  la rue cesse d'être lisse.
- **L'échafaudage** et ses planches — on passe dessous, et la clôture orange qui le ceinture
  s'enjambe comme les autres.
- **La roulotte de chantier**, les **toilettes portatives** (le gag, et un abri d'une tuile),
  les **palettes de briques**, les **poutres d'acier**, le **rouleau compresseur**, la
  **bétonnière**, le **camion à benne** (⚠️ celui-là est un vrai véhicule : étage 2).
- **Le signaleur** — pancarte LENTEMENT d'un côté, ARRÊT de l'autre. ⚠️ C'est une **sorte de
  gens**, pas du décor : il va au réservoir de la fiche des sortes, et il fait ce que personne
  ne fait encore — **arrêter le trafic**, donc te bloquer, toi aussi.
- **L'ouvrier au marteau-piqueur** — il s'arrête quand tu t'approches et te regarde passer.
- **La maison condamnée** (planches en croix sur les fenêtres), **la façade seule** qu'on a
  gardée en démolissant le reste, **le trou de fondation** plein d'eau boueuse — ⚠️ de l'eau
  **basse**, exactement comme la piscine de banlieue : on y barbote, on ne s'y noie pas.
- **La rue neuve** : un carré d'asphalte plus noir que le reste, et des lignes fraîches. Ça ne
  fait rien du tout, et c'est ce qui rend le reste crédible.

**⚠️ Les cinq pièges, et ils sont tous du même genre : une ville qui change casse ce qui
comptait sur elle.**

1. ⚠️ **Jamais un lieu qui sert.** Aucun `SPECIAUX`, aucun commerce, aucune porte de donneur
   de mission ne passe en chantier — sinon on démolit la quincaillerie le jour où une mission
   y envoie. Les chantiers se tirent **parmi les parcelles qui ne portent rien**, et le juge
   le vérifie à chaque phase.
2. ⚠️ **Une porte en chantier ne mène nulle part.** Si un bâtiment est démoli, sa porte doit
   **disparaître** de `portes`, pas rester ouverte sur un intérieur qui flotte. Et en phase 4,
   la porte neuve doit avoir une pièce à la bonne taille — le correctif « une pièce plus
   grande que sa maison » est livré, il s'applique ici aussi.
3. ⚠️ **Les juges de géométrie se rejouent à CHAQUE phase**, pas seulement à la génération :
   un seul îlot marchable, aucune poche murée, les sentiers qui rejoignent la rue. C'est
   exactement ce que la tentative du trottoir a appris — neuf juges rougissent d'un coup quand
   la ville bouge, et c'est à ça qu'ils servent.
4. ⚠️ **Le cache de morceaux se vide au changement de JOUR**, jamais en pleine image : une
   phase qui avance change des tuiles, et recuire en plein jeu se voit. Le chemin existe (une
   clôture cassée oublie son morceau **et les huit voisins**) ; ici on l'appelle au matin,
   pendant le fondu qui existe déjà.
5. ⚠️ **La phase voyage dans la sauvegarde**, une ligne par chantier — et une vieille partie
   repart avec tout à zéro (`completer()` sait déjà faire ça). Sinon deux appareils voient deux
   villes différentes, et la fiche des sauvegardes sur le serveur devient un mensonge.

**Et ça s'entend.** Un chantier sans bruit n'existe pas : le marteau-piqueur, le godet qui
racle, et ⚠️ **le bip de recul** — c'est LE son d'un chantier, celui qu'on reconnaît sans
regarder. Trois échantillons, joués à la distance (`Son.jouerA` existe), et **ça se tait la
nuit**, sauf le chantier de nuit qui fait râler le quartier — une manchette pour le journal
de M15.

**Juges** : aucun chantier ne tombe sur un lieu spécial, un commerce ou une porte de donneur ;
à chaque phase, la ville garde un seul îlot marchable et aucune poche murée ; une porte
démolie disparaît de `portes` et une porte neuve a une pièce qui tient dans son bâtiment ; la
boule de démolition endommage ce qu'elle touche et rien d'autre ; le cache de morceaux ne se
vide qu'au changement de jour ; les phases sont dans la sauvegarde et une vieille partie
repart à zéro sans planter ; et le chantier se tait entre minuit et six heures.

### M12 — La ville vit (**ajout**, taille 4)

_Ce que ça donne :_ une ville qui bouge toute seule, avec ou sans toi.

- **Le chantier** (demande de Martin) : rien ne dit « Québec » comme une voie barrée depuis
  trois ans — et ce n'est pas qu'une farce. C'est une **surcouche** au champ `voie`, tirée
  par la graine du jour : une voie fermée, des cônes orange (le sprite `cone` existe déjà
  dans `OBJETS`), un détour. Le trafic sait déjà se déporter dans la voie d'à côté ; ici il
  n'a plus le choix. La ville devient différente d'un jour à l'autre **sans regénérer une
  seule tuile**, et la police a enfin un endroit où se tenir sans raison.
  - **Pas un chantier : une famille d'entraves** (demande de Martin : « des réparations,
    des blocages de route aléatoires, des détours »). Le même mécanisme — une surcouche au
    champ `voie`, tirée par la graine du jour — porte plusieurs visages, et c'est la
    variété qui fait qu'on ne s'y habitue pas :
    - **la réparation** : une voie fermée, des cônes, un ouvrier ou deux (des piétons
      `intouchables`, comme les enfants) et une pelle mécanique — le trafic se déporte ;
    - **la fermeture** : la rue entière barrée par une barricade et un panneau **DÉTOUR** avec
      sa flèche, et un itinéraire de rechange que le trafic **suit** ;
    - **le bris d'aqueduc** : la rue inondée sur trois tuiles, roulable au ralenti — il
      manque au Faubourg un printemps où la rue est un lac ;
    - **le camion de déménagement** ou l'**autobus en panne** : une entrave qui n'a pas de
      cônes parce qu'elle n'était pas prévue, et qui dure une heure de jeu, pas un jour.
  - ⚠️ **Une entrave ne coupe jamais la ville en deux — et une FERMETURE le pourrait.** Une
    voie fermée sur un boulevard laisse l'autre ; une rue entière barrée change le champ de
    direction lui-même, et une fermeture tirée au hasard peut isoler un quartier. Le juge est
    celui de M1 (`voies_bloquees` : fortement connexes), mais il ne peut pas tourner dans le
    navigateur à chaque jour de jeu. La sortie est celle de tout le dépôt : **Python décide,
    JS calcule**. `carte.py` calcule une fois, avec le juge, la liste des **segments qui
    peuvent se fermer** sans casser la connexité — et le paquet la transporte. La graine du
    jour ne tire que dans cette liste. Un pont n'y est jamais, ni la seule approche d'un
    croisement, ni une rue à voie unique.
  - ⚠️ **Deux entraves ne se combinent pas sans juge.** Deux fermetures prises séparément
    dans la liste peuvent, ENSEMBLE, isoler un bloc. Soit on n'en tire qu'une par jour, soit
    la liste est faite de **paires** validées — jamais de tirages indépendants.
  - **Le détour se lit.** Un panneau DÉTOUR avec une flèche à chaque coin de l'itinéraire de
    rechange, pour le joueur autant que pour le trafic : une fermeture sans détour affiché
    n'est pas une entrave, c'est un piège.
  - **Nid-de-poule** : une tuile qui secoue la caméra et coûte deux points de carrosserie.
    Deux lignes, et toute la ville prend un accent. Jamais dans un croisement (on y freine
    déjà), jamais deux côte à côte.

- **Tramway** : une ligne sur rails du Faubourg aux Quais, des arrêts, des portes — et il
  ne s'arrête pas pour toi. ⚠️ C'est un véhicule qui **ignore** le champ de direction : il
  a ses propres rails, et le trafic doit lui céder.
- **Traversier** : Les Quais ↔ La Pointe, à l'heure, quatre chars à bord, il part sans toi.
- **Tempête de neige** (risqué) : visibilité réduite, adhérence divisée, **charrue** qui
  pousse la neige et les chars mal garés ; la police glisse aussi.
- ⚠️ La neige touche à la physique **et** au rendu : elle arrive derrière une option, et la
  sonde de performance Playwright la mesure avant qu'elle soit allumée par défaut.
- **La nuit de déneigement** — et c'est ce qui donne enfin à la fourrière une raison d'être.
  À Québec, la veille d'une opération, un **feu orange clignote** sur le panneau de la rue :
  interdiction de stationner cette nuit-là, et ce qui reste dans la rue part au lot. Le jeu a
  déjà les trois morceaux — la fourrière (M9), la charrue (ci-dessus), le rythme de nuit — il
  ne manque que le panneau qui clignote **la veille**, pour qu'on ait eu le temps de lire.
  Laisse ton char dans la mauvaise rue, et le lendemain il est au lot : c'est la meilleure
  façon d'apprendre ce que « mal garé » veut dire, parce que ce n'est pas une punition, c'est
  la ville.
- **Les feux passent au clignotant la nuit.** Vrai partout au Québec, et presque gratuit ici :
  `feuVert()` est une pure fonction de l'heure, et la nuit vide maintenant la ville. À partir
  d'une heure, plus de cycle — l'artère clignote orange, la rue secondaire clignote rouge (un
  STOP), et le trafic de nuit, qui n'a plus personne à croiser, cesse d'attendre devant un
  feu rouge pour rien. Ça se voit de loin sur une ville déserte, et c'est exactement le
  genre de détail qui dit « c'est la nuit » mieux qu'un voile bleu.
- **Les heures de pointe ont une direction.** Le rythme (nuit, matin, soir) règle _combien_
  de chars roulent ; il ne dit pas _où ils vont_. Le matin, le trafic devrait **converger**
  vers le Faubourg et les Quais, et le soir se **disperser** vers les Érables. ⚠️ Pas en
  touchant au champ de direction, qui est fixe et jugé : en **pondérant le choix de sortie**
  aux croisements selon l'heure. C'est trois lignes dans `prochaineCible`, et le matin a
  soudain un sens.
- **La ville est coupable d'elle-même.** GTA 2 le faisait déjà : des pickpockets qui
  travaillent la foule, un vol de char sous tes yeux, deux gangs qui se battent à leur
  frontière — **sans toi**. Le jeu a tout ce qu'il faut : le pickpocket, le carjacking, les
  témoins, les gangs et leurs territoires. Il manque que ça arrive à d'autres qu'au joueur.
  - ⚠️ Et ça change la police : un crime qu'on n'a pas commis peut te tomber dessus si tu es
    au mauvais endroit — un témoin qui te confond, un agent qui arrive sur une bagarre où tu
    passais. C'est risqué, donc c'est **rare** et **lisible** (on voit le vrai coupable), et
    un juge vérifie qu'aucune étoile ne tombe sur un joueur immobile à plus de N tuiles.
- **On attend l'autobus.** GTA 2 avait des piétons à l'arrêt ; ici il y a un autobus (M9) et
  bientôt un tramway. Des gens qui attendent à l'arrêt, montent quand il s'arrête, et
  descendent trois arrêts plus loin : c'est de la vie qui a un **but**, et c'est aussi la
  façon la moins chère de faire entrer et sortir des piétons sans qu'ils naissent hors écran.
- **Les éboueurs.** Un camion à bras mécanique — Québec ramasse les bacs comme ça — qui
  s'arrête tous les vingt mètres, lève un bac, repart. Un obstacle qui **bouge** dans la
  rue, une raison de le dépasser, et le camion de M9 qui sert à autre chose qu'à défoncer.
- **Les goélands et les chats.** La vie qui n'est pas humaine : un goéland qui s'envole quand
  tu passes aux Quais, un chat qui file dans une ruelle du Faubourg. Ils ne comptent pour
  rien — ni témoins, ni victimes — et c'est précisément ce qui les rend vivants : ils ne sont
  là que pour être là.
- **Juges** : toute entrave du jour vient de la liste calculée par Python, jamais d'un
  tirage libre ; la ville reste fortement connexe **avec** les entraves du jour posées (sur
  cinq graines) ; un détour affiché mène bien de l'autre côté ; la nuit de déneigement
  s'annonce la **veille** ou n'arrive pas ; un feu au
  clignotant ne fait plus attendre personne pour rien ; le trafic de pointe converge et se
  disperse (on compte les sorties choisies à un croisement, matin contre soir) ; aucun crime
  d'autrui ne vaut une étoile à un joueur qui n'y est pour rien ; et un autobus qui s'arrête
  fait vraiment monter quelqu'un.

### M14 — Meta v2 (**ajout**, taille 4)

- **Un compte et une base de données** (demande de Martin, précisée le 15 sept. 2026 :
  « des sauvegardes sur le serveur dans une base de données, connexion par compte avec
  session ouverte longue durée avec option d'ouverture par NIP »). Aujourd'hui la partie vit
  dans le `localStorage` du navigateur : elle ne traverse pas. Vingt minutes au téléphone,
  puis on s'assoit à l'ordi, et on recommence. Un compte règle ça, et il porte aussi le défi
  du jour et le classement — qui ont besoin d'un serveur de toute façon. ⚠️ **Le détail de la
  sauvegarde, de la session longue et du NIP est plus bas**, dans sa propre partie : c'est
  là que se trouvent les chiffres et les pièges.
  - **`app/bd.py` + SQLite**, sous `DONNEES_DIR`. Une seule machine, deux workers gunicorn,
    quelques dizaines de joueurs : un serveur de base de données serait une pièce de plus à
    installer, à surveiller et à redémarrer pour rien. ⚠️ **WAL et un `timeout`**, sinon les
    deux workers se marchent dessus et ça donne `database is locked` — en production
    seulement, jamais en local où il n'y a qu'un worker.
  - **`app/comptes.py`** : pseudo + mot de passe haché (`generate_password_hash`, déjà là
    avec Flask), session signée. ⚠️ **`SECRET_KEY` vaut encore `cle-de-developpement-a-changer`
    par défaut** — tant qu'un compte n'existe pas, ça ne coûte rien ; le jour où une session
    vaut une partie, une clé par défaut en production laisse forger n'importe qui. Le
    `installer.sh` doit la générer et refuser de démarrer sans elle.
  - **Ce qu'on demande, et rien d'autre** : un pseudo, un mot de passe, et un courriel
    **facultatif** qui ne sert qu'à reprendre un mot de passe perdu. Sans lui, un mot de
    passe perdu est un compte perdu, et c'est écrit noir sur blanc à l'inscription. Une page
    dit ce qui est gardé et comment tout effacer — c'est un jeu pour s'amuser, pas une
    raison de tenir un fichier sur du monde.
  - ⚠️ **Le compte ne devient jamais obligatoire.** Le `localStorage` reste le défaut : on
    joue sans compte, comme avant, et le compte n'est qu'une **synchronisation**. Sinon une
    panne de serveur, une connexion coupée dans l'autobus ou un certificat expiré empêchent
    de jouer à un jeu qui tourne entièrement dans le navigateur.
  - **Le tableau des scores déménage** dans la BD avec ses règles intactes (pseudo validé,
    borne de vraisemblance de `economie.GAIN_MAX_PAR_SECONDE`, tri, plafond). Deux endroits
    pour la même chose, c'est deux endroits qui dérivent. Un score sans compte s'y inscrit
    toujours, sous un pseudo, comme aujourd'hui.
  - ⚠️ **On ne peut pas empêcher la triche d'un jeu qui tourne dans le navigateur** — une
    partie qu'on peut poster est une partie qu'on peut fabriquer. Ce qu'on peut faire, c'est
    que ça ne rapporte rien : le classement garde sa borne, le serveur garde la durée et la
    date de chaque partie, et une partie reprise repart avec sa durée, pas à zéro.
  - **Le schéma va changer** : la sauvegarde a déjà `version` + `empreinte` + le repli de
    `completer()`. La même discipline s'applique côté serveur — une migration par version,
    jamais une colonne ajoutée à la main sur le serveur.
  - **Une BD, c'est quelque chose à sauvegarder.** `deploy/installer.sh` pose un vidage
    quotidien (`.backup`, pas une copie du fichier à chaud) et une rétention de sept jours.
    Une base de données sans copie de sûreté est une perte de données qui attend sa date.

#### Les parties vivent sur le serveur — compte, session longue, NIP (15 sept. 2026)

_Demande de Martin :_ « je veux des sauvegardes sur le serveur dans une base de données.
Connexion par compte avec session ouverte longue durée avec option d'ouverture par NIP. »

**Mesuré d'abord, parce que les chiffres tranchent la moitié des questions :**

- une partie neuve pèse **790 octets** ; une partie bien avancée (toutes les armes, vingt
  paquets, cinq missions, quarante lignes de journal, vingt personnages connus, les paliers de
  boulot) pèse **4,5 Ko**, en 39 champs. Mille joueurs avec trois parties chacune : **13 Mo**.
  SQLite n'a pas à réfléchir, et le débat « vraie base de données ou non » n'existe pas ;
- le jeu se sauvegarde **tout seul toutes les dix secondes** (`B.t % 600`, dans `Missions.maj`).
  ⚠️ **Ce chiffre-là décide du reste** : on ne poste pas six fois par minute par joueur ;
- l'installeur **génère déjà** une vraie `SECRET_KEY` (`secrets.token_hex(32)` dans le `.env`
  partagé, depuis M0). La dette qui reste n'est donc pas de la générer, c'est de **refuser de
  démarrer** avec la clé de développement quand `FLASK_DEBUG` est faux.

**La règle : le local joue, le serveur se souvient.** Le `localStorage` reste la vérité pendant
qu'on joue — c'est déjà la promesse de M14, et c'est ce qui permet de jouer dans l'autobus. Le
serveur reçoit des **instantanés**, jamais chaque image.

- **Quand un instantané monte** : à la sauvegarde volontaire (le lit de la planque, le menu),
  au changement de jour, à la fin d'une mission, quand l'onglet part en arrière-plan — et au
  plus **une fois par minute** le reste du temps. ⚠️ `beforeunload` ne se déclenche pas de
  façon fiable sur téléphone : c'est `visibilitychange` qui compte, avec `sendBeacon`, la
  seule requête qui survit à la fermeture de l'onglet.
- ⚠️ **Le conflit est la vraie question, et il se règle par un compteur, jamais par une
  horloge.** Deux appareils n'ont pas la même heure ; un compteur qui monte à chaque écriture,
  oui. Le serveur **refuse** un instantané dont le compteur est plus petit ou égal au sien et
  renvoie ce qu'il a. Le jeu pose alors la question en clair — « LA PARTIE DU SERVEUR EST PLUS
  AVANCÉE : JOUR 12, 4 300 $. GARDER CELLE-CI / PRENDRE CELLE-LÀ » — et **ne fusionne jamais
  rien** : deux parties ne se fusionnent pas, et un jeu qui tranche tout seul efface la soirée
  de quelqu'un.
- **Trois emplacements** par compte. Ça ne coûte qu'une colonne, et ça évite la question
  « j'ai fini le jeu, est-ce que je perds ma partie si j'en recommence une ? ».

**La base** — quatre tables, et elles tiennent en une page :

| Table | Ce qu'elle garde |
|---|---|
| `comptes` | pseudo (unique, les mêmes règles que le pseudo des scores), empreinte du mot de passe (`generate_password_hash`, scrypt), courriel **facultatif**, date de création |
| `parties` | compte, emplacement (1–3), **compteur**, le JSON de la partie (4,5 Ko), version du schéma, empreinte des définitions, date |
| `appareils` | compte, **empreinte** du jeton (jamais le jeton), nom donné par le joueur (« le téléphone »), dernière visite, date de péremption |
| `scores` | le tableau des scores, déménagé du fichier JSON (M14 le dit déjà), avec un compte **facultatif** |

**La session longue durée** — c'est un **jeton d'appareil**, pas un mot de passe qu'on retape :

- 32 octets aléatoires, posés en cookie `httpOnly; Secure; SameSite=Lax; Max-Age=1 an`, et
  ⚠️ **hachés en base comme un mot de passe** : une base volée ne doit pas ouvrir les comptes.
- **Il tourne** : chaque usage en émet un nouveau et périme l'ancien. ⚠️ Et c'est ce qui donne
  la détection de vol gratuitement — si un jeton **déjà périmé** revient, c'est que deux
  appareils portent la même session : on coupe tous les appareils du compte et on redemande le
  mot de passe. C'est la seule façon simple de réagir à un vol de cookie.
- Le mot de passe ne sert donc qu'à **lier un appareil**, une fois. C'est tout ce qu'on tape.

**Le NIP** — et ⚠️ **il faut dire tout de suite ce qu'il n'est pas** : le NIP **n'ouvre pas un
compte**, il rouvre une session sur un appareil **déjà lié**. Quatre chiffres, c'est 10 000
possibilités : inacceptable comme secret de compte, parfait comme verrou d'écran.

- À l'ouverture, si l'appareil porte un jeton, le jeu ne demande **que le NIP**.
- Le NIP **déchiffre le jeton localement** : ce qui dort dans le navigateur est le jeton
  **chiffré** par une clé dérivée du NIP (WebCrypto, PBKDF2 — présent dans tous les
  navigateurs visés). Sans le NIP, le contenu du stockage ne vaut rien à lui seul.
- **Cinq essais**, puis le jeton chiffré est **effacé** et il faut le mot de passe. ⚠️ Le
  **compte**, lui, ne se bloque pas : bloquer un compte parce qu'un inconnu a tapé cinq fois
  sur un téléphone perdu punirait exactement la mauvaise personne.
- ⚠️ **Ce qu'un NIP promet, et rien de plus** : il arrête quelqu'un qui emprunte le téléphone
  deux minutes. Il n'arrête pas quelqu'un qui l'emporte chez lui et prend son temps — 10 000
  candidats, ça s'essaie hors ligne. La vraie protection est ailleurs et elle existe déjà : le
  jeton **tourne**, le serveur peut le révoquer, et ce qu'il y a à voler est une partie de jeu
  vidéo. C'est écrit ici pour que personne ne prenne le NIP pour ce qu'il n'est pas.
- **Facultatif**, et il ne remplace jamais le mot de passe : sans NIP, la session longue
  s'ouvre toute seule, comme sur un site où l'on reste connecté. Avec NIP, elle demande quatre
  chiffres. ⚠️ Et on refuse les vingt NIP les plus tapés de la Terre (0000, 1234, 1111,
  l'année en cours) — c'est une liste, pas un algorithme.

**Ce qui ne doit jamais arriver**, et chacun a son juge :

- ⚠️ **Le serveur en panne ne doit pas empêcher de jouer.** Toute la synchronisation est
  « au mieux » : un appel raté se retente plus tard, et rien dans la boucle de jeu n'attend une
  réponse. Un compte est un **confort**, jamais une condition.
- ⚠️ **Une partie plus vieille ne peut pas écraser une plus neuve** — c'est le compteur, et
  c'est le juge le plus important de la fiche.
- ⚠️ **Effacer un compte efface pour vrai** : les parties disparaissent, les appareils sont
  révoqués, et les scores restent sous un pseudo sans compte. Un bouton, une confirmation, et
  une page qui dit ce qui est gardé.
- ⚠️ **Le mot de passe perdu sans courriel est un compte perdu**, et c'est écrit à
  l'inscription, pas découvert après.

**Juges** : un instantané au compteur plus petit ou égal est refusé et rend celui du serveur ;
un jeton périmé qui revient coupe tous les appareils du compte ; cinq NIP ratés effacent le
jeton local sans toucher au compte ; les vingt NIP interdits le sont ; le jeton n'existe en
clair nulle part dans la base ; une partie de 4,5 Ko ne monte pas plus d'une fois par minute
hors des moments déclarés ; le jeu démarre et se joue avec l'API des comptes éteinte ; effacer
un compte efface ses parties et révoque ses appareils ; et l'application **refuse de démarrer**
en production avec la clé de développement.

- **Défi du jour** à graine serveur (reporté de M7) : `/api/defi` donne la graine du jour,
  le classement est celui du jour, tout le monde joue la même ville.
- **Mode photo** : le jeu se fige, la caméra se détache, quelques filtres, et l'image se
  télécharge.
- **Coop locale** (risqué) : deux manettes, une caméra qui tient les deux joueurs, zoom
  arrière quand ils s'éloignent. ⚠️ 480 × 270 n'est pas grand : à décider **après un essai**,
  pas avant.

### Les zones conditionnelles : une porte, une condition, un prix (**ajout**, taille 3)

_Demande de Martin (15 sept. 2026) :_ « certaines zones pourraient être bloquées
conditionnellement à des missions ou prérequis. »

⚠️ **La ville est ouverte en entier depuis M1, et elle le restera** — c'est la promesse de la
vision. Ce qui manque n'est pas une clôture, c'est une **raison** : un endroit qu'on regarde
trois jours avant d'y entrer vaut mieux qu'un endroit qu'on traverse sans le voir. Les jeux
qui ont posé la question avant nous répondent toujours pareil : la barrière doit avoir une
**cause dans la fiction** (un pont qu'on répare, un gang qui tient un coin) et non un mur
invisible, et le joueur doit **voir** ce qui le bloque.

Or le jeu a déjà **trois barrières**, chacune écrite à sa façon, et aucune ne se déclare :
la **guérite de la fourrière** (une grille de 4 tuiles, un comptoir, `etoiles_vol` si on
force), les **zones de gang** (`hostile_toujours`, `hostile_si_arme` : ce n'est pas un mur,
c'est une menace) et les **barrages de police** à 5★. M12 en promet une quatrième famille
(les entraves du jour). Quatre mécanismes pour la même idée, c'est trois de trop.

**La règle : une barrière est une fiche, pas un cas.** `carte.BARRIERES` en Python, lue par
le navigateur comme le reste :

- **où** : un rectangle de tuiles, ou la grille d'un lieu spécial ;
- **quoi** : ce qu'elle arrête — `pieton`, `vehicule`, ou les deux. ⚠️ C'est la clé qui évite
  la moitié des pièges : un pont fermé aux **chars** mais pas aux **jambes** bloque sans
  jamais enfermer ;
- **quand** : la condition — `apres: "<mission>"`, `exige: {...}` (le même objet que M16),
  `heure: "jour"|"nuit"`, ou `jour_tire` (la graine du jour : c'est ainsi que les entraves de
  M12 entrent dans le même mécanisme) ;
- **combien** : `forcer` — ce que ça coûte de passer quand même (`etoiles`, `degats`,
  `payer`), ou `null` pour les deux seules qui ne se forcent pas : le barbelé et l'eau ;
- **quoi dire** : `raison`, une ligne en majuscules — « LES SKATEUX TIENNENT LE PONT ». Elle
  s'affiche quand on s'y bute, et le carnet la liste.

**Les huit barrières de départ** (les trois qui existent y rentrent, cinq sont neuves) :

| Barrière | Où | Arrête | Condition | Forcer |
|---|---|---|---|---|
| Le pont de La Pointe | l'unique pont de la carte (`PONTS`) | **véhicules** | ouvert par p02 | passer à pied, ou pousser les cônes au char (dégâts) |
| La guérite de la fourrière | lot de La Shop (existe) | véhicules | payer au comptoir | 1★ (`etoiles_vol`, déjà écrit) |
| La cour de l'usine Prévost | La Shop | les deux | ouverte le **jour** | 1★ et deux gardiens |
| La cour à ferraille de Ti-Loup | La Shop | les deux | après s02 | 1★ |
| L'allée de la villa du maire | Les Érables | véhicules | après e07 (la clé) | 2★ et deux gardiens |
| Le quai du cargo | Les Quais | les deux | ouvert la **nuit** (déchargement) | 1★ et les matelots |
| Les entraves du jour | n'importe quelle rue | véhicules | `jour_tire` (M12) | dégâts, et un détour existe toujours |
| Le traversier | quai → l'Île | — | un horaire, un billet | aucun : c'est de l'eau (voir la fiche de l'Île) |

**⚠️ Les quatre pièges, et ils sont tous du même genre : enfermer quelqu'un.**

1. ⚠️ **Une barrière fermée ne doit jamais couper un chemin de retour.** Le juge se calcule :
   pour **chaque combinaison** de barrières fermées, la composante marchable qui contient la
   planque doit contenir tous les lieux des missions alors disponibles. `composantes_marchables()`
   existe depuis M1, le juge est une boucle par-dessus.
2. ⚠️ **Le trafic doit la voir**, sinon les chars s'empilent devant une grille qu'ils ne
   connaissent pas. Une barrière écrit dans les **masques de tuiles** (comme les entraves de
   M12), pas seulement dans le dessin — et le chien de garde du trafic (dix secondes sans
   bouger) dira tout de suite si on s'est trompé.
3. ⚠️ **Une zone fermée ne se peuple pas.** Les piétons et les chars naissent dans une bulle
   autour du joueur : une cour fermée qui en fabrique quand même donne des gens enfermés qui
   tournent en rond. Ce que la barrière ferme, elle le vide.
4. ⚠️ **On doit voir pourquoi.** La barrière se dessine (une grille, des cônes, une guérite),
   la mini-carte la marque, et `raison` s'affiche quand on s'y bute. Une porte fermée sans
   raison lisible est un bogue, même quand c'est voulu.

**Juges** : aucune combinaison de barrières n'enferme la planque ni ne rend un lieu de mission
inatteignable ; chaque barrière déclare son `arrete`, sa condition, son `forcer` et sa
`raison` ; aucune ne bloque un **piéton** sans qu'un autre chemin existe (seul le barbelé en a
le droit) ; le trafic ne s'empile pas devant une barrière fermée (le chien de garde ne mord
pas plus qu'avant) ; et une zone fermée ne contient aucun piéton ni char né après sa
fermeture.

### Le bord de l'eau et la foire (**ajout**, taille 4)

_Demande de Martin (15 sept. 2026) :_ « je veux des belvédères, table à pic nic, des plages
parasol, enfants qui joue, château de sable, etc. des sea doo, ski nautique, bateau, quai.
un parc d'attraction avec grande roue, jeu d'adresse, manèges, etc. »

⚠️ **Mesuré d'abord, et c'est la même surprise que pour l'île : la plage existe déjà.** Sur la
graine livrée, le sol compte **2 507 tuiles de sable**, dont **782 touchent l'eau** — une grève
qui court tout le long de la baie, des Quais à La Pointe — et **1 818 tuiles de quai**. La
ville pose **1 701 décors**, de **treize** sortes : arbre (705), buisson, lampadaire, poubelle,
caisse, banc, débris, borne-fontaine, cabanon, corde à linge, guichet, BBQ, fontaine. Aucun
n'est une table à pique-nique, un parasol, un belvédère ou un château de sable ; **personne ne
s'assoit jamais sur les 782 tuiles de grève**, et **aucune coque n'est amarrée aux 1 818 tuiles
de quai**.

Ce qui manque n'est donc pas le terrain : c'est que **le bord de l'eau est un décor qu'on
traverse**, et la demande est d'en faire un endroit **où on va**.

**Quatre vagues, et elles ne coûtent pas du tout la même chose.** La première ne touche à aucun
moteur ; la deuxième non plus, mais elle décide de ce que les enfants ont le droit de vivre ;
la troisième attend une dette nommée depuis M3 ; la quatrième est un jalon à elle seule.

#### 1re vague — la grève se meuble (taille 1, aucun moteur neuf)

Six fiches `DECORS` de plus et une passe de semis sur le sable — exactement le chemin des
terrains de banlieue (cabanon, corde à linge, BBQ, livrés le 14 sept.), et rien de plus :

- **la table à pique-nique** : deux bancs et un plateau ; vue d'en haut, c'est un **H couché**,
  et c'est ce qui la nomme à douze pixels. `casse`, comme le banc ;
- **le parasol** : la seule chose du lot qui se lise **de loin**, et la seule qu'on ne heurte
  pas — `solide: false`, on passe dessous. Rayé, sa couleur tirée par tuile ;
- **la serviette et sa glacière** : ⚠️ un **décal** au sol (`DECALS` existe pour ça), pas une
  entité. Rien ne l'arrête, rien ne la casse, et elle ne pèse rien dans le hachage spatial ;
- **le château de sable** : ⚠️ le seul du lot qui ait une **règle**. Le décor le plus fragile de
  la table (`pv` 5) — un char qui roule sur la grève le rase — et il **revient au matin** avec
  tout le reste (`reparerLeDecor()`). Un enfant qui recommence son château tous les jours, c'est
  une blague que la ville raconte sans qu'on l'écrive ;
- **la bouée** et **le poteau d'amarrage**, sur le quai ;
- **le belvédère** : un plancher de bois sur pilotis, une rambarde, deux marches, posé là où la
  terre domine l'eau — le bout de La Pointe, la tête du pont, la falaise des Érables. Il
  **arrête** (comme les kiosques) au lieu de bloquer : on y monte, on ne le traverse pas.

⚠️ **Une plage suit la côte ; elle ne suit pas une boîte.** La phrase est déjà dans `_eau()`, et
elle a coûté douze bancs de sable en pleine baie : le semis doit marcher **tuile par tuile**, en
regardant si l'eau est à deux tuiles de là — jamais sur le rectangle du bassin. Un parasol
planté au milieu d'un sentier du bois dit le contraire de ce qu'on veut.

⚠️ **`poser_decor` ne connaît pas l'eau.** Il refuse le solide, le routier, le devant de porte
et le réservé, parce qu'aucun décor n'a jamais eu à flotter. Il faut le lui apprendre une fois —
sinon la bouée est le seul décor du jeu à avoir raison de flotter, et tous les autres l'imitent.

#### 2e vague — les enfants jouent (taille 1)

L'enfant existe depuis la v1 : `intouchable`, vitesse 1,15, témoin 0,5, et il détale de **douze
tuiles** (`enfant_peur_tuiles`). Il n'a aucune routine — il marche comme tout le monde, en plus
petit et en plus vite.

⚠️ **Jouer, c'est un `metier`, pas un costume.** La règle des « sortes de gens » est écrite trois
fois dans `pietons.py`, et le dépôt l'a déjà payée une fois avec les filles de la Brume : une
sorte sans routine est un déguisement. Trois routines, toutes branchées sur ce qui existe :

- **le château** : il s'accroupit devant un décor `chateau_sable`, il y revient, et si le château
  n'y est plus il en recommence un ailleurs ;
- **la baignade** : depuis que l'eau n'est plus un mur (14 sept.), un piéton peut y entrer. Les
  enfants pataugent dans la **première tuile** et pas plus loin. ⚠️ **Un enfant ne se noie pas** :
  `intouchable` dit aujourd'hui « aucune arme, aucun char » ; il doit dire aussi « pas l'eau »,
  sinon la plage est une trappe à noyade et le jeu devient autre chose ;
- **le ballon** : deux enfants et un ballon qui va de l'un à l'autre. C'est tout, et ça suffit —
  un décor qui bouge se voit de trois écrans.

⚠️ **Une plage pleine d'enfants est une plage pleine de TÉMOINS** (0,5 chacun). C'est la seule
conséquence mécanique de la vague, et elle est bonne : la grève devient le plus mauvais endroit
de la ville pour faire un coup, exactement comme l'attroupement de l'amuseur.

#### 3e vague — l'eau porte enfin quelque chose (taille 2, ⚠️ **bloquée**)

`vehicules.py` déclare déjà **la chaloupe** : `eau=True`, friction 0,995, adhérence 0,05, trois
cercles — et **`phase=2`**, « sans sprite et sans trafic », parce que l'eau demande une physique
à part. Le sea-doo et le bateau de ski ne sont pas trois dettes : c'est **la même**, payée une
fois.

⚠️ **Rien ne se met à l'eau tant que le char ne tient pas son cap sur la terre ferme.** « Le char
tourne comme son ombre » est **P1 et en cours** ; une coque qui dérape est le pire endroit du
monde où découvrir un défaut de cap.

Ce que l'eau demande une fois, et ce qui en découle ensuite :

- **une coque** : pas de freins, de la dérive, un sillage, et une vitesse qui ne tient qu'au
  moteur. La fiche de la chaloupe l'a déjà chiffrée ; il reste à la faire flotter ;
- **la mise à l'eau** : `_quai()` pose déjà une rampe de débarquement « là où un quai en porte
  vraiment une ». La porte entre les deux mondes existe — personne ne l'a jamais franchie ;
- **le sea-doo** : la moto de l'eau. Il `ejecte` comme elle, il est rapide, il ne pardonne rien,
  et c'est le seul véhicule du jeu dont la chute ne coûte que l'orgueil ;
- **le ski nautique** : ⚠️ **c'est un crochet, pas un véhicule.** La liaison existe (`crochet`,
  la remorqueuse de M9), avec une épave au bout ; ici c'est un piéton. Et elle donne à la baie
  son premier **spectacle** : un bateau qui passe au large avec quelqu'un derrière ;
- **des coques amarrées** sur les 1 818 tuiles de quai, qu'on peut prendre — et c'est ce qui rend
  **L'Île-aux-Corneilles** (fiche suivante) atteignable autrement qu'à la nage ;
- ⚠️ **la police n'a pas de bateau.** Deux sorties, et il faut en choisir une **exprès** : au
  large, les étoiles **descendent** (comme sur l'île), ou la Sûreté a une vedette et c'est un
  jalon de plus. Le plan choisit la première — et l'île a déjà écrit pourquoi : un endroit sûr
  qui n'a qu'un chemin de retour n'est pas un endroit sûr, c'est un piège qu'on choisit.

#### 4e vague — la foire de La Pointe (taille 2)

**Où.** La Pointe est le district-parc, et son plan porte **deux grandes taches de bois** de
quatre blocs de large sur deux de haut. La foire en prend **une**. ⚠️ On n'agrandit pas la
grille : la leçon de l'île vaut ici aussi — la ville a la place, il faut la **dépenser**. Un
glyphe de plan de plus (`f`), un `_foire()` à côté de `_parc()` et `_place()`, une allée
centrale en terre battue, et la grève juste en dessous.

- **La grande roue** — la seule vraie idée de la vague. ⚠️ **Ce n'est pas un manège, c'est un
  belvédère qui tourne.** On paie, le fondu des portes joue (livré), la caméra monte, et la ville
  est là, en dessous, avec ses lumières si c'est le soir. Ce qu'on redescend avec : **les paquets
  cachés qu'on n'a pas trouvés clignotent sur la mini-carte jusqu'au soir**. Les vingt paquets
  existent, ils ne sont marqués nulle part, et `carte.paquets()` dit en toutes lettres que « les
  trouver doit faire visiter la ville » — un point de vue qui montre la ville est exactement la
  bonne façon de les donner. Une fois par jour, et ça se paie.
- **Les manèges** (carrousel, tasses, chaises volantes) : ⚠️ **du décor animé, et on n'y monte
  pas.** Un manège où l'on monte et qui ne donne rien est un décor cher ; un manège qui tourne
  avec du monde dessus est une ville qui vit. C'est l'étage 1 des machines de chantier, mot pour
  mot : une articulation, pas dix — un socle cuit une fois, des nacelles peintes par-dessus à
  chaque image.
- **Les jeux d'adresse** : ⚠️ **un jeu d'adresse est un défi, pas un moteur.** `missions.DEFIS`
  en porte trois depuis la v1 (le saut, le tour, la livraison) : un lieu, un compte, un chrono,
  une prime, un texte en majuscules. Trois de plus sur les mêmes rails — **la galerie de tir**
  (les armes existent, une cible est un décor avec des `pv`), **le marteau de force** (marteler
  ACTION contre un chrono : aucune statistique neuve, c'est le bouton qui fait la force), et **la
  pêche aux canards**, qu'on peut gagner mais pas voler. La prime : de l'argent, et au troisième
  palier une **casquette de la foire** — le vestiaire existe (`magasins.TENUES`) et ne demande
  rien à personne.
- **Le son, et ce n'est pas un détail** : ⚠️ une foire muette est une peinture. L'orgue de manège,
  les cris, les vagues et le moteur du sea-doo sont quatre pistes ElevenLabs de plus
  (`app/audio.py`, `app/musique.py`). Le chemin est déjà tracé : **le musicien de rue est « une
  musique qui sort de QUELQU'UN »**, avec son gain à lui, par-dessus l'ambiance du district et
  sans prendre le rang de personne. L'orgue de la foire est **une musique qui sort d'un
  ENDROIT** — le même code, une source fixe. Surtout pas une ambiance de district de plus.

**Ce que ça coûte ailleurs**, et il faut le dire avant de dessiner : six à dix fiches `DECORS`
(du JS, pas du paquet), un glyphe de plan, un `metier` de plus, trois défis, quatre pistes audio
— et ⚠️ **aucun juge de géométrie ne parle du sable**. Un décor de plage vit à deux tuiles de
l'eau, là où aucun décor n'allait jamais ; c'est une ligne de juge à écrire **exprès**, pas à
découvrir.

**Juges** : aucun décor de plage à plus de trois tuiles du sable, et aucun sur l'eau ; un château
de sable se casse et revient au matin ; un enfant ne dépasse jamais la première tuile d'eau et
rien ne le tue ; la foire tient dans son bloc et n'avale aucune rue ; on ne monte dans la grande
roue qu'en payant, une fois par jour, et ce qu'elle révèle s'éteint le soir ; aucun manège n'est
montable ; un défi de foire ne paie pas mieux à l'heure qu'une mission (la règle des paliers de
boulot) ; aucune coque ne roule sur la terre et aucun char ne flotte ; et un enfant reste
intouchable, sur la grève comme ailleurs.

### L'Île-aux-Corneilles : la ville a une île et ne le sait pas (**ajout**, taille 3)

_Demande de Martin (15 sept. 2026) :_ « tu peux extensionner la carte au besoin. »

⚠️ **Mesuré d'abord : le besoin est plus petit qu'il en a l'air.** La carte fait 421 × 213
tuiles, et **21 % en sont déjà de l'eau** — 18 675 tuiles. Au milieu de la baie il y a un
rectangle de **40 × 24 tuiles d'eau pleine** (à partir de 158, 116) qui ne touche aucune
rive. On n'agrandit donc **rien** : on pose une île dans ce qui existe, et la carte garde sa
taille, son paquet et tous ses juges de géométrie.

**Pourquoi une île, et pas un quartier de plus.** Depuis que l'eau n'est plus un mur (livré le
14 sept.), la baie est **traversable** — à la nage, en chaloupe, et un char y coule. La ville
a donc un cinquième de sa surface qui ne sert qu'à se noyer. Et deux choses du plan pointent
déjà vers un ailleurs sans l'avoir : le **traversier** de M12, qui ne va nulle part, et
_Le dernier traversier_ (m99), la fin où l'on sacre son camp — aujourd'hui un fondu au noir
sur un quai. L'île leur donne une destination.

**Ce qu'elle est.** Un quai de bois, une **chapelle** et son couvent à moitié vide, une
**usine à poisson** fermée depuis quinze ans, six maisons, un hangar sans nom au bout du
chemin. Trente habitants l'hiver. Pas de gang. Et surtout :

- ⚠️ **Pas de police.** C'est la seule idée mécanique de la fiche, et elle vaut toutes les
  autres : on peut y **laisser refroidir** un char et un casier. Les étoiles tombent à quai
  et ne remontent pas — mais l'île n'a qu'un chemin de retour, et Roy finit par le savoir
  (M11). Un endroit sûr qui n'a qu'une porte n'est pas un endroit sûr, c'est un piège qu'on
  choisit.
- **On y va comme on veut** : à la nage (long, et on arrive les mains vides), en chaloupe
  (celle du capitaine, gagnée en q08), en bateau volé, ou par le **traversier** quand M12 le
  fera rouler. C'est la barrière la plus honnête du jeu : elle n'est pas fermée, elle est
  **loin**.
- **Un char sur l'île y reste** : rien n'y roule qui n'ait été débarqué. Le premier char que
  tu y emmènes par le traversier est un événement.

**⚠️ Ce que coûte un septième district**, et il faut le dire avant de dessiner :

- **une ambiance de plus** (la musique par district est livrée) — ou elle emprunte celle de La
  Pointe, et ça s'entend ;
- **un rythme de population** (`DISTRICTS`), une couleur de légende, une ligne de mini-carte ;
- ⚠️ **les juges de géométrie ne parlent pas de l'eau** : « un seul îlot marchable » deviendrait
  faux le jour où l'île existe. Il devient « **un îlot par terre ferme**, et chacun atteignable
  par l'eau » — c'est une ligne de juge, mais il faut la changer **exprès**, pas la découvrir ;
- ⚠️ **le paquet** : 40 × 24 tuiles de plus, plus une chapelle et un hangar en intérieurs. On
  mesure avant (370 Ko bruts sur 600).

**L'arc de l'île est dans M16** (arc I, huit missions), et _Le dernier traversier_ y gagne sa
dernière image : le traversier passe devant l'île, et la ville rapetisse derrière.

**Juges** : l'île ne touche aucune rive (une ceinture d'eau d'au moins quatre tuiles tout
autour) ; on ne peut y arriver qu'à la nage, par un bateau ou par le traversier — aucun pont,
aucune tuile de route ne la relie ; la police n'y patrouille pas et les étoiles y descendent ;
chaque terre ferme reste un seul îlot marchable ; et le paquet reste sous son plafond.

### Ce que le net apprend : quatre activités que le jeu n'a pas (**ajout**, taille 2)

_Demande de Martin (15 sept. 2026) :_ « regarde sur le net pour des idées de missions ».

En comparant Bandini aux classiques vus d'en haut (GTA 1 et 2, Chinatown Wars) et aux
inventaires de « tout ce qu'il y a à faire » des GTA 3D, **la ville a déjà presque tout** : les
paquets cachés (20), les défis de saut (3, cinq de plus dans M16), quatre boulots au klaxon,
les propriétés, le marché noir. Quatre choses manquent, et chacune se paie en données, pas en
moteur.

1. **Les boulots montent en grade** — **livré le 15 sept. 2026**, quelques heures après
   l'écriture de cette fiche (`aee8543`). Trois paliers par boulot (10, 25, 50) et une
   récompense qui **change la partie**, presque jamais de l'argent : +10 % puis +25 % de vie
   pour l'ambulance, le rachat au lot à moitié puis gratuit pour le remorquage, l'hôpital à
   moitié prix pour la pizza, et à 50 le **char à la planque** dans les quatre cas. ⚠️ Quand
   deux paliers portent le même type, c'est le **plus fort** qui compte, pas la somme.
2. **Deux boulots de plus**, et aucun ne demande un véhicule neuf (⚠️ la refonte des
   véhicules passe avant tout char de plus) :
   - **La patrouille** — dans une auto-patrouille **volée**, un point rouge sur la mini-carte :
     un fuyard à rattraper avant la fin du chrono. C'est la _vigilante_ des GTA, et Bandini lui
     donne ce qu'elle n'a nulle part ailleurs : tu fais la police **avec un casier**, dans un
     char qui n'est pas à toi. Récompense de palier : `casier −1` tous les cinq (M11).
   - **Pompier volontaire** — au Québec, les pompiers d'un village sont des volontaires qu'on
     appelle chez eux. Un feu quelque part, un extincteur, un chrono (`eteindre` arrive avec
     M16). Pas de camion à dessiner : ce qui compte, c'est d'arriver.
3. **La liste du quai** (le _wheeler-dealing_ de GTA 2, le quai d'exportation de GTA III) :
   Sven — ou Ti-Loup si on l'a brûlé — affiche **quatre modèles** sur une ardoise au quai. Les
   livrer, sans bosse, un par jour. La liste se renouvelle. ⚠️ C'est l'activité qui donne enfin
   une raison de **regarder** le parc automobile : aujourd'hui un coupé sport et une berline
   valent pareil dès qu'ils roulent.
4. **Les frénésies** (les _rampages_). Une icône cachée, une arme, un chrono, un compte à
   faire. C'est le classique du genre, et c'est trois lignes de données : `tuer` + `chrono_s`
   + une arme imposée. ⚠️ Deux garde-fous, et ils ne sont pas négociables : **les enfants
   restent intouchables** (ils le sont déjà, dans le code, pour tout le monde), et une frénésie
   se déclenche **exprès** — jamais un objectif qu'on reçoit au téléphone. C'est la seule
   activité du jeu qui ne prétend pas être autre chose que du chaos, et c'est à Martin de dire
   si la ville en veut.

**Juges** : un palier de boulot ne se donne qu'une fois et sa récompense existe (un char à la
planque est vraiment garé) ; aucun palier ne paie mieux à l'heure qu'une mission ; la
patrouille ne compte que les vrais fuyards ; la liste du quai ne demande que des modèles qui
existent au catalogue et qu'on peut trouver dans la ville ; une frénésie ne touche jamais un
intouchable.

### M16 — Cent missions (**ajout**, taille 8, en quatre tranches de 2)

_Demande de Martin (13 sept. 2026) :_ « je veux plus de 100 missions avec les personnages
existants et de nouveaux personnages, partout sur la carte, plein de nouvelles idées ! »

_Ce que ça donne :_ une ville où **chaque quartier a une histoire**, et où le téléphone
sonne pour autre chose que les cinq missions du Faubourg. **109 missions de plus** (114 en
tout), **9 arcs**, **34 personnages de plus**, et une raison d'aller dans chacun des cinq
districts, à chaque heure du jour. Les deux fins de M13 sont les trois dernières lignes du
catalogue : ce jalon est celui qui les rend **atteignables**.

⚠️ **Cent missions, c'est un catalogue, pas cent scripts.** Les cinq missions de la v1
tiennent sur onze types d'objectifs et quatre causes d'échec, et `histoire.js` ne connaît
aucune mission par son nom. La règle tient : **une mission est une liste d'objectifs dans
`missions.py`**, et si une idée ne s'écrit pas avec les types existants, on ajoute **un
type** — jamais un `if (slug === 'q07')`. Ce jalon en ajoute neuf, listés plus bas, et
c'est tout ce que le moteur apprend. Les cent missions sont des **données**.

#### Ce que le moteur apprend (et rien d'autre)

- **Neuf types d'objectifs de plus** dans `TYPES_OBJECTIFS`, chacun avec son juge de banc :
  `suivre` (filer un piéton ou un char sans être vu : trop près ou trop loin, c'est raté),
  `proteger` (un personnage te suit à pied ou monte avec toi ; s'il meurt, échec
  `protege_mort`), `pickpocket` (les poches d'un piéton **précis**, par-derrière — le
  mécanisme de M2 existe), `payer` (donner un montant), `acheter` (un article à un
  comptoir), `detruire` (un véhicule de la mission), `sauter` (une rampe, `vol_px` — le
  juge du défi _Le Grand Saut_), `eteindre` (un feu à l'extincteur — le jet existe, le feu
  de char aussi) et `boulots` (`n` boulots d'une `sorte` : généralise `courses`, qui reste
  pour le taxi). `parler` et `survivre`, déclarés depuis M6 et jamais utilisés, servent
  enfin.
- **Quatre options qui traversent les types** : `chrono_s` sur n'importe quel objectif (le
  défi l'avait, la mission non), `sans_etoile` (échec `etoile` dès qu'on est vu : les
  missions discrètes), `sans_arme` (entrer en territoire de gang les mains vides), `contre`
  (des adversaires sur une `course`). `ECHECS` gagne `etoile` et `protege_mort`.
- **`exige`** : ce qu'il faut avoir **en plus** des prérequis — `argent_min` (m99),
  `proprietes` et `liberes` (m98), `dette` (d08), `tenue` (f10), `heure`. Un prérequis dit
  « après quoi » ; `exige` dit « dans quel état ». Les deux se lisent dans le carnet.
- **`ferme`** : une mission qui en **ferme** une autre. C'est ce qui fait les choix (q10 ou
  q11, r03 ou r04, d07 ou d08) : une mission fermée n'apparaît plus jamais, ni au téléphone
  ni au carnet. ⚠️ Un choix est un choix **parce qu'il coûte** : chaque paire ferme aussi une
  récompense, et le juge vérifie qu'aucune des deux branches ne rapporte plus du double de
  l'autre.
- **`donne` grossit** : `libere: "<district>"` (généralise `faubourg_libere` ; le gang
  devient des passants, la zone s'efface de `carte.zones()`, c'est ce que compte _Le Boss_),
  `calme: "<gang>"` (`hostile_toujours` et `hostile_si_arme` tombent — la seule façon de
  marcher dans La Shop), `contact` (un numéro de plus au téléphone), `vehicule` (un char
  garé devant la planque), `tenue`, `munitions`, `rabais` par comptoir, `dette: -n`,
  `casier: -n`, `ami`/`ennemi` (Roy, Sal), `boulot` (un boulot de plus au klaxon),
  `manchette`. Chaque clé a **un** endroit qui la lit, dans `Histoire.recompenser()`.
- **Des lieux qu'on peut nommer.** `resoudre()` apprend `district:<slug>` (une tuile
  marchable tirée dans le district), `boutique:<genre>` (la plus proche de ce genre :
  pharmacie, taverne, quincaillerie…), `pont`, `quai`, `bois`, `rampe:<district>`. Et
  **quatre lieux spéciaux de plus** dans `carte.SPECIAUX`, parce qu'une mission a besoin
  d'une adresse stable : la **villa du maire** (Les Érables), le **Salon Ferraro** (Faubourg,
  le barbier-shylock), le **bureau du Clairon** (Faubourg) et la **cour à ferraille de
  Ti-Loup** (La Shop). ⚠️ Pas cinq : chaque lieu spécial est une pièce à dessiner, une
  porte à poser et un juge de plus. Tout le reste passe par `boutique:` et `district:`.
- **Le téléphone trie.** Avec cent missions, il sonnerait sans arrêt. Règles : **un appel
  par demi-journée**, jamais pendant une mission, jamais à 3★ et plus ; le donneur **le plus
  proche** appelle d'abord ; un donneur qu'on croise **hèle** (la bulle de M6) même si le
  téléphone n'a pas encore sonné. Le carnet (P2) liste ce qui est disponible, par district :
  c'est là que cent missions deviennent lisibles, et c'est pour ça que le carnet passe
  avant.
- **Les dialogues sortent du paquet.** 114 missions × 7 répliques ≈ 150 Ko bruts : le
  paquet (370 Ko, plafond 600) les prendrait en brut, mais pas sur le fil : 50 Ko de texte
  gzippé par-dessus les 43 d'aujourd'hui, et les 70 Ko sautent. Le catalogue (objectifs, prérequis, `donne`)
  reste dedans — c'est ce que le carnet et le GPS lisent — et les répliques viennent par
  `/api/dialogue/<slug>` **quand le téléphone sonne**, avec un ETag comme le reste. Une
  requête par mission, avant que la première voix se charge de toute façon.
- **Trois personnages qui ne sont pas des donneurs** dans `pietons.py`, fréquence 0, posés
  par les missions comme le fuyard de m2 : le **matelot** (les gars de Sven), le **ciseau**
  (les hommes de main de Sal), le **gardien** (les gardes de Prévost et du lot). Et
  **Biscuit**, le premier animal du jeu : un sprite de 8 × 6, quatre images, qui court comme
  un fuyard et ne rapporte rien — le promeneur de chien de La Pointe n'a toujours pas de
  chien, c'est l'occasion.
- **La sauvegarde** : `p.libere` (par district), `p.calmes` (par gang), `p.dette`,
  `p.contacts`, `p.fermees`, `p.choix`. `Sauvegarde.completer()` a le repli champ par champ :
  une vieille partie repart avec tout à vide, et m6 lui est proposée dès qu'elle a fini m5.

#### Les 34 personnages de plus

⚠️ **Trente-quatre voix, c'est le vrai coût.** La règle de M6 est _une voix par
personnage_, et le compte ElevenLabs de Martin n'a pas trente-quatre voix québécoises. Ce
qu'on fait : **une voix par famille** (une douzaine), partagée entre des personnages qui ne
parlent **jamais dans la même mission**, avec un réglage différent (stabilité, style) pour
que ça ne s'entende pas. `audio.VOIX_PERSONNAGES` garde une ligne par personnage, et un
juge interdit deux personnages de même voix dans un même dialogue. Les **petites jobs**
(arc T) sont dites par les voix des passants qui existent déjà : zéro voix de plus.

| Slug | Qui | Où il se tient | Ce qu'il est |
|---|---|---|---|
| `gus` | Gus Lévesque | Chez Gus, derrière le comptoir | l'armurier ; bourru, vend à tout le monde, n'aime personne |
| `rosa` | Rosa Di Meo | Boutique Rosa | la couturière ; l'ancienne blonde de Rocco, en sait long |
| `mo` | Le Grand Mo | le banc du terminus | l'itinérant qui a tout vu ; se paie en bière et en potins |
| `fern` | Fern Côté | porte du terminus, côté quai d'autobus | le chauffeur du dernier autobus |
| `mado` | Mado | Casse-croûte du Faubourg | la propriétaire ; nourrit le sergent, et te nourrit |
| `lachance` | Dr Lachance | Hôpital, bureau | l'urgentologue ; prévu depuis la vision, jamais posé |
| `ginette` | Ginette | Hôpital, comptoir | l'infirmière-chef ; sait ce que le docteur ne dit pas |
| `sal` | Sal « Le Barbier » Ferraro | Salon Ferraro | le shylock de Rocco : 15 000 $, coupe à 12 $ |
| `desjardins` | Me Pierre-Luc Desjardins | Bar Le Brouillard, table du fond | l'avocat du Carré ; cher, et jamais deux fois le même jour |
| `louise` | Louise Tremblay-Dion | bureau du Clairon | la journaliste ; veut la une, quoi qu'il en coûte |
| `roy` | Inspectrice Claudine Roy | Poste, bureau d'en haut | la police honnête ; enquête sur Bouchard |
| `momo` | Momo Taxi | porte du casse-croûte | le chauffeur rival de Marco, endetté chez Sal |
| `lulu` | Lucienne « Lulu » Pelletier | Cantine des Quais | la sœur de Josée ; la cantine, le poisson du vendredi |
| `gege` | Gérard « Gégé » Morin | porte de la cantine | chef des débardeurs ; syndiqué jusqu'aux dents |
| `sven` | Sven Haugen, « Le Norvégien » | le quai, à côté de son cargo | le contrebandier qui veut Les Quais |
| `mireille` | Mireille | la Brume, près de l'hôtel | une fille de la Brume qui veut sortir de la rue |
| `norbert` | Norbert | Hôtel Bandini, réception | le concierge ; discret, tarifé |
| `berube` | Capitaine Aurèle Bérubé | le quai du traversier | le traversier de nuit — la deuxième fin |
| `denis` | Le Beau Denis | zone des Morues | le lieutenant de Josée, et le souteneur de Mireille |
| `tipaul` | Ti-Paul Gagnon | Dépanneur Chez Ti-Paul | le dépanneur des Érables ; bière, potins, drifts dans son parking |
| `diane` | Diane Larivière | villa d'à côté (porte de logement, Érables) | conseillère municipale ; veut la paix, et le pouvoir |
| `maire` | Le maire Réal Tanguay | villa du maire | corrompu, jovial, dort à l'Hôtel Bandini |
| `jo` | Jo Bellemare | stationnement du dépanneur, le soir | chef des Chevreuils — et le fils de Diane |
| `beaulieu` | Mme Beaulieu | un sentier des Érables, avec Biscuit | la promeneuse ; perd son chien, puis déménage |
| `xavier` | Xavier | porte du dépanneur | l'ado qui veut un selfie avec un coupé sport |
| `prevost` | Réjean Prévost | Usine Prévost, bureau | le patron ; a mis à pied la moitié de La Shop |
| `raymonde` | Raymonde Fortin | porte de l'usine | présidente du syndicat |
| `sauve` | Bob Sauvé | cour de l'usine | le contremaître ; joue sur deux tableaux |
| `gilles` | Gilles Thériault | guérite de la fourrière | le gardien du lot ; prend sa retraite à la fin |
| `boulon` | Gros-Boulon (Marcel Boulanger) | zone des Boulonneux | chef des Boulonneux — les gars que Prévost a mis dehors |
| `tiloup` | Ti-Loup Ferraille | cour à ferraille | le ferrailleur ; achète les épaves, ne pose pas de questions |
| `ovila` | Ovila Saint-Onge | Le phare | le gardien, presque aveugle, voit des lumières la nuit |
| `zed` | Zed (Zacharie Lemieux) | stationnement de La Pointe | chef des Skateux ; respecte ceux qui sautent |
| `maude` | Maude | un mur de La Pointe | la muraliste ; peint la ville qu'on lui laisse |
| `trappeur` | Le Trappeur (Armand) | les bois de La Pointe | l'ermite ; collets, fronde, et pas de police |

Et deux qui existent déjà et changent : **Josée** s'appelle Josée Pelletier (Lulu est sa
sœur, ça compte dans q12), et **Marco** a une fin (m97).

#### Les 109 missions

Colonnes : **Après** = prérequis (`exige` entre crochets) ; **Ce qu'on fait** = les
objectifs, dans l'ordre, avec le type en italique quand il est nouveau ; **Paie** = la
récompense, puis ce que `donne` accorde. ⏳ = la mission attend un autre jalon, et elle est
alors en `phase: 2` — **jamais un prérequis d'une autre** : un arc ne bloque pas sur ce qui
n'est pas livré. Les montants sont en dollars du jeu.

**Le tronc** — Josée ouvre la ville, Marco la referme.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| m6 | Le tour du propriétaire | Josée | m5 | aller au dépanneur, à la cantine, à l'usine, au phare — un district à la fois, en un jour ; _parler_ à Ti-Paul, Lulu, Raymonde, Ovila | 300 ; **ouvre les neuf arcs**, quatre contacts |
| m97 | Marco te vend | Marco | 3 districts libérés | l'appel : « viens au garage » — c'est un piège, 5★ à l'intro ; semer ; rattraper le taxi de Marco (fuyard) ; le coucher **ou** le laisser filer (choix dans la fin) | 0 ; le taxi de Marco garé à la planque, Marco disparu du jeu |
| m98 | Le Boss | Josée | m97 [4 propriétés, 4 districts libérés] | le maire envoie tout ce qu'il a sur le Brouillard : _survivre_ 180 s à 5★ avec les Morues, les Skateux et les Boulonneux à tes côtés ; aller à la villa ; _parler_ au maire, qui cède | 0 ; **le générique** — la ville change de couleur (M13) |
| m99 | Le dernier traversier | Capitaine Bérubé | m6 [15 000 $ en poche] | de nuit, 0★ (`sans_etoile`) : aller au quai du traversier ; _payer_ le passage ; monter ⏳ traversier (M12) — repli : la chaloupe du capitaine, un fondu au quai | 0 ; **l'autre générique** (M13) |

**Arc F — Le Faubourg après les Cravates** (12) — les commerçants respirent, Marco compte.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| f01 | Les Cravates reviennent | Ti-Guy | m6 | de nuit, six Cravates mettent le feu à la porte du bar : ramasser l'extincteur derrière le comptoir, _eteindre_ ; _survivre_ 120 s à la porte ; coucher celui qui reste (chef) | 300 ; la caisse du bar tient un jour de plus |
| f02 | Le stock de Gus | Gus | f01 | le camion de munitions de Gus est à la fourrière : le prendre de nuit (`sans_etoile`), le livrer à l'armurerie sans bosse | 350 ; munitions, armurerie à −20 % |
| f03 | La robe de Rosa | Rosa | f01 | un Chevreuil est parti avec sa livraison dans une berline de luxe : le rattraper (fuyard, en auto), ramasser la caisse, retourner | 250 ; le complet gris, Boutique Rosa à −25 % |
| f04 | Le Grand Mo sait tout | Le Grand Mo | m6 | _acheter_ trois bières à la taverne, les lui apporter ; il dit où Rocco cachait trois paquets : les ramasser | 150 ; trois paquets comptés |
| f05 | Le dernier autobus | Fern | m6 | monter dans l'autobus au terminus ; _boulots_ n=4 sorte autobus (quatre arrêts, des passagers qui montent) ; le ramener | 200 ; le boulot **autobus** au klaxon |
| f06 | Deuxième service | Bouchard | f01 | un témoin de m4 parle : _suivre_ le stool du casse-croûte jusqu'au poste sans être vu ; puis _payer_ 200 son silence **ou** l'assommer à mains nues | 300 |
| f07 | La caisse, encore | Mme Thibodeau | f04 | quelqu'un vide le kiosque : c'est un Cravate en complet gris ; _pickpocket_ pour reprendre la clé ; retourner | 200 |
| f08 | Le char de Rocco | Ti-Guy | f02, f03 | la berline de luxe de Rocco est au lot : la prendre de nuit (1★, le lot appelle), semer, la livrer au garage pour la repeindre | 0 ; **la berline de luxe** garée à la planque |
| f09 | Marco veut sa part | Marco | f06 | _proteger_ Marco, qui monte avec toi, jusqu'au kiosque, au bar et au garage pour ramasser les caisses ; deux Cravates tendent une embuscade ; sans bosse | 250 ; Marco a vu où est l'argent (ça se paie en m97) |
| f10 | La chemise hawaïenne | Rosa | f03 [tenue : chemise hawaïenne] | un client a oublié une chemise, une lettre dans la poche : la porter — **en la portant** — à Norbert, à l'Hôtel Bandini | 300 ; contact Norbert |
| f11 | Le feu chez Mado | Mado | m6 | un char brûle devant le casse-croûte : ramasser l'extincteur, _eteindre_ avant l'explosion, chrono 40 s | 150 ; l'extincteur |
| f12 | Le Faubourg te dit merci | Mme Thibodeau | f08, f09, f10 | cinq commerçants ont mis une enveloppe : _parler_ à cinq commis dans cinq boutiques du Faubourg avant la nuit, `sans_etoile` (on ne paie pas un gars recherché) | 500 ; toutes les boutiques du Faubourg à −10 % |

**Arc Q — Les Quais** (13) — Josée tient le port, Sven le veut, Mireille veut en sortir.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| q01 | La cantine de Lulu | Lulu | m6 | trois matelots mangent sans payer : les mettre dehors (tuer n=3, à la porte de la cantine) | 150 ; cantine à −25 % |
| q02 | Le poisson du vendredi | Lulu | q01 | un camion de poisson à livrer à trois poissonneries (`boutique:marine`) dans trois districts avant qu'il tourne, chrono 180 s | 250 |
| q03 | Les briseurs de grève | Gégé | m6 | Prévost fait venir des scabs par camion : l'intercepter sur le boulevard et le _detruire_ avant l'usine | 300 |
| q04 | La cargaison du Norvégien | Josée | q01 | de nuit, le cargo décharge : ramasser une caisse sur le quai pendant que quatre matelots patrouillent, `sans_etoile` ; la porter au bar | 400 |
| q05 | Mireille veut sortir | Mireille | q04 | _proteger_ Mireille, à pied, de la Brume jusqu'à l'hôtel, de nuit, pendant que Le Beau Denis te court après | 100 ; Mireille travaille à la réception — l'hôtel rapportera 10 % de plus |
| q06 | Le Beau Denis | Josée | q05 | Josée est furieuse — règle ça toi-même : coucher Denis (chef) en zone des Morues, `sans_arme` ; semer 2★ | 350 ; les Morues te laissent passer (`calme`) |
| q07 | La chambre 12 | Norbert | f10 | un client est mort dans la chambre 12 — un comptable de Prévost ; de nuit, porter le « colis » (lourd, on marche) au camion, le livrer à la cour de Ti-Loup, `sans_etoile` | 500 ; **l'Hôtel Bandini est à vendre** (10 000) |
| q08 | Le moteur du capitaine | Capitaine Bérubé | m6 | les Skateux ont volé le moteur de sa chaloupe : le ramasser dans leur stationnement (trois Skateux), le rapporter | 200 ; ⏳ eau — la chaloupe devient conduisible quand l'eau s'ouvre |
| q09 | La course des débardeurs | Gégé | q03 | _course_ en camion autour des Quais `contre` deux débardeurs, quatre points, chrono 150 s | 300 |
| q10 | Le Norvégien te reçoit | Sven | q04 | Sven propose mieux que Josée : une moto chargée au pont, à livrer au phare sans bosse, chrono 120 s | 600 ; **ferme q11** ; les Morues redeviennent méfiantes un jour |
| q11 | Le cargo brûle | Josée | q04 | _detruire_ les deux camions de Sven sur le quai (explosion, 2★), semer 3★ | 700 ; **ferme q10** ; manchette _Le Norvégien lève l'ancre_ |
| q12 | La Chef a un cœur | Josée | q06 | la mère de Josée et Lulu fait une crise aux Érables : monter dans l'ambulance, la ramasser, la livrer à l'hôpital, chrono 120 s, chocs pénalisés | 300 ; Josée amie (le bar rapporte 10 % de plus) |
| q13 | La nuit des Morues | Josée | q06, q11 ou q10 | Sven se venge : _survivre_ 120 s à l'hôtel, les Morues à tes côtés ; coucher le chef des matelots | 500 ; **Les Quais libérés** (`libere: quais`), manchette |

**Arc E — Les Érables** (13) — la banlieue, le maire, et des ados qui tournent en rond.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| e01 | Les drifts de Ti-Paul | Ti-Paul | m6 | tous les soirs, les Chevreuils font des ronds dans son stationnement : _survivre_ 60 s de nuit et en coucher trois quand ils descendent | 150 ; dépanneur à −25 % |
| e02 | La bière de Ti-Paul | Ti-Paul | e01 | un camion de bière attend au quai : le ramener au dépanneur sans bosse, à travers la ville | 250 |
| e03 | Biscuit s'est sauvé | Mme Beaulieu | m6 | le chien a filé dans les bois de La Pointe : le rattraper (fuyard, à pied) et le ramener | 80 ; Biscuit te suit dans les Érables |
| e04 | La course des Chevreuils | Jo | e01 | _course_ sur le boulevard des Érables `contre` trois Chevreuils, cinq points, chrono 90 s, le char que tu veux | 300 ; les Chevreuils respectent (`calme`) |
| e05 | Le char dans la piscine | Diane | e01 | les Chevreuils ont poussé une auto dans sa piscine : la sortir à la remorqueuse, la livrer au lot | 200 ; ⏳ terrains de banlieue |
| e06 | Le maire ne dort pas chez lui | Diane | m6 | de nuit, _suivre_ la berline du maire de la villa à… l'Hôtel Bandini, sans être vu | 300 |
| e07 | La clé de la villa | Diane | e06 | _pickpocket_ le chauffeur du maire au dépanneur ; fouiller la villa (ramasser le dossier), `sans_etoile` | 400 ; **le dossier** (sert en e11 et c02) |
| e08 | Jo a un problème | Jo | e04 | sa mère a trouvé sa cachette : deux paquets à ramasser au stationnement des Skateux avant eux, en coupé sport, chrono 200 s | 250 |
| e09 | Le barbecue | Ti-Paul | e02 | quatre poutines du camion-restaurant à livrer à quatre maisons **en vélo** avant qu'elles refroidissent, chrono 120 s | 150 |
| e10 | Diane veut la paix | Diane | e04, e07 | vider les Chevreuils : tuer n=6 sur deux coins, puis le chef — et le chef, c'est Jo ; la fin le dit à Diane | 600 ; **Les Érables libérés**, manchette |
| e11 | Le maire te reçoit | Le maire | e07 | il veut le dossier : le lui vendre (_payer_ à l'envers : 1 000 $) **ou** le garder pour Louise — le choix se fait dans le dialogue | 1 000 si vendu ; sinon 0 et **c02 s'ouvre** |
| e12 | Le selfie de Xavier | Xavier | m6 | amener un coupé sport au dépanneur et _sauter_ la rampe des Érables devant lui, 40 px de vol | 200 |
| e13 | Le char de Diane | Diane | e10 | sa berline de luxe est au lot : la reprendre sans payer (1★), semer, la livrer à la villa sans bosse | 300 |

**Arc S — La Shop** (13) — une usine, un syndicat, et les gars qu'on a mis dehors.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| s01 | Gilles à la guérite | Gilles | m6 | un Boulonneux est parti avec la remorqueuse du lot : la reprendre en zone des Boulonneux, la ramener | 200 ; rachat au lot à −20 % |
| s02 | La ferraille de Ti-Loup | Ti-Loup | m6 | _boulots_ n=3 sorte remorquage, destination la cour à ferraille | 250 ; le boulot **ferraille** : Ti-Loup achète les épaves |
| s03 | La paie de la Prévost | Raymonde | q03 | le camion de paie arrive le vendredi, deux gardiens dedans : le prendre, le livrer derrière l'usine, semer 2★ | 500 |
| s04 | Le quart de nuit | Bob Sauvé | m6 | les Boulonneux menacent le quart de nuit : _survivre_ 120 s à la porte de l'usine contre huit | 300 |
| s05 | Gros-Boulon te parle | Gros-Boulon | s02 | Ti-Loup t'a présenté : voler la berline de luxe de Prévost dans la cour de l'usine, la livrer à la ferraille pour la compacter | 400 ; **les Boulonneux te laissent vivre** (`calme`) — la seule façon de marcher dans La Shop |
| s06 | Le rat de l'usine | Raymonde | s03 | quelqu'un a vendu la liste du syndicat : _suivre_ Bob Sauvé de l'usine au bar sans être vu | 250 |
| s07 | Le camion de Prévost | Prévost | s04 | un camion de pièces doit être au quai avant le départ du bateau : livrer sans bosse, chrono 150 s — tu travailles pour les deux bords, et c'est le propos | 350 |
| s08 | Le lot se fait vider | Gilles | s01 | de nuit, trois Boulonneux volent des chars au lot : les coucher sur place | 200 |
| s09 | L'explosion | Gros-Boulon | s05 | faire sauter le réservoir de l'usine : _detruire_ le camion-citerne stationné dans la cour (au pistolet ou en le percutant), 2★, semer 3★ | 600 |
| s10 | Raymonde négocie | Raymonde | s06 | _proteger_ Raymonde, qui monte avec toi, jusqu'à la villa du maire et retour, deux gardiens de Prévost en poursuite | 300 |
| s11 | La paix des Boulonneux | Prévost | s09, s10 | Prévost plie : ramasser l'accord à l'usine, l'apporter à Gros-Boulon en zone des Boulonneux `sans_arme` | 500 ; **La Shop libérée** — les Boulonneux redeviennent des machinistes, manchette _La Prévost rembauche_ |
| s12 | Le dernier char du lot | Gilles | s08 | Gilles prend sa retraite : _boulots_ n=5 sorte remorquage en un jour, chrono jour | 0 ; **la remorqueuse** garée à la planque |
| s13 | Le prototype | Prévost | s07 | un coupé sport volé à l'usine dort au stationnement des Skateux, le pont est bloqué par les Chevreuils : le reprendre, _sauter_ la rampe du stationnement (30 px), le livrer à l'usine sans bosse | 400 |

**Arc P — La Pointe** (11) — un phare, des bois, des planches à roulettes.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| p01 | La lampe du phare | Ovila | m6 | l'ampoule est morte : en _acheter_ une à la quincaillerie la plus proche, la rapporter avant la nuit | 100 ; Ovila te connaît |
| p02 | Le pont est bloqué | Bilodeau (retraité, porte de logement) | m6 | les Skateux ont fermé le seul pont avec des cônes : ramasser quatre cônes (ce sont des armes), coucher deux Skateux | 150 |
| p03 | La murale de Maude | Maude | m6 | trois bombes de peinture à l'atelier de La Shop, à rapporter en moto, chrono 180 s | 150 |
| p04 | Zed veut un défi | Zed | p02 | _course_ **à pied** dans les sentiers `contre` Zed, cinq points, chrono 60 s — les Skateux courent à 1,3 | 200 ; les Skateux respectent (`calme`) |
| p05 | Les collets du Trappeur | Le Trappeur | p01 | quelqu'un vole ses collets : attendre la nuit dans les bois, coucher les deux Skateux qui viennent | 120 ; la fronde et 60 billes |
| p06 | Ovila voit des lumières | Ovila | p01, q04 | de nuit, une chaloupe accoste sous le phare : _suivre_ les deux matelots jusqu'à leur cabane sans être vu, ramasser la caisse, l'apporter à Josée | 300 |
| p07 | Les Bilodeau déménagent | Bilodeau | p02 | l'autobus : ramasser quatre retraités à quatre maisons du bout, les livrer à l'Hôtel Bandini, chocs pénalisés | 250 |
| p08 | La fête au stationnement | Zed | p04 | deux caisses de bière de la taverne, en camion, sans bosse ; la police arrive : semer 1★ | 200 |
| p09 | Le phare s'éteint | Ovila | p05 | des Skateux ont grimpé au phare et éteint la lampe, un bateau approche : monter (aller dedans), coucher trois Skateux, chrono 90 s | 300 ; manchette _Le phare a tenu_ |
| p10 | Le saut de La Pointe | Zed | p04 | _sauter_ la rampe du stationnement en moto, 80 px de vol, devant les Skateux | 250 |
| p11 | Zed et la Chef | Josée | p09, p10 | _proteger_ Zed, à pied puis en char, par le pont jusqu'au Brouillard ; les Chevreuils attaquent en autos sur le boulevard | 500 ; **La Pointe libérée**, manchette |

**Arc H — L'hôpital** (7) — le Dr Lachance a des secrets, et des ordonnances.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| h01 | L'ambulance de nuit | Dr Lachance | m6 | _boulots_ n=3 sorte ambulance, de nuit | 300 ; facture d'hôpital à moitié |
| h02 | Les pilules | Ginette | h01 | quelqu'un vide la pharmacie : _suivre_ le commis à sa sortie — il vend aux Chevreuils au dépanneur | 200 |
| h03 | Le docteur a une dette | Dr Lachance | h01, d01 | _proteger_ Lachance, qui monte avec toi, jusqu'au Salon Ferraro et retour ; deux ciseaux suivent | 250 |
| h04 | Le cœur | Dr Lachance | h02 | une glacière arrive par autobus au terminus : la ramasser, la livrer à l'hôpital en 90 s, n'importe quel char | 400 |
| h05 | Le patient qui s'est sauvé | Ginette | h02 | un patient a filé — c'est le chef des Cravates de m5, recousu : le rattraper (fuyard, à pied), le ramener vivant | 200 |
| h06 | Les ordonnances | Dr Lachance | h04 | trois ordonnances à porter à trois pharmacies dans trois districts, `sans_etoile` — elles sont fausses | 350 |
| h07 | La nuit des urgences | Dr Lachance | h06, 1 district libéré | la guerre de gangs a rempli l'urgence : _boulots_ n=5 sorte ambulance en un jour | 500 ; un séjour à l'hôpital gratuit |

**Arc D — La dette de Rocco** (8) — Sal coupe les cheveux, et le reste. ⚠️ L'arc **ne dépend
pas de M10** : la dette y est un compteur de partie (`p.dette`, 15 000 au départ, que `donne`
fait baisser). M10 la fera vivre en dehors des missions (intérêts, rappels, hommes de main).

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| d01 | Le barbier | Sal | m6 | Sal appelle : « Rocco me devait 15 000 » ; _acheter_ une coupe au salon — c'est la rencontre | 0 ; la dette s'affiche au carnet |
| d02 | Le premier versement | Sal | d01 | _payer_ 500 avant demain, chrono jour ; sinon deux ciseaux passent te voir | 0 ; dette −500 |
| d03 | Les Ciseaux | Sal | d02 | collecter chez Momo Taxi : _parler_ ; il refuse ; le coucher, _pickpocket_ | 300 ; dette −300 |
| d04 | La collecte du barbier | Sal | d03 | trois débiteurs dans trois districts : Ti-Paul, Lulu, Ovila ; _parler_ à chacun — et _payer_ pour eux si tu veux qu'ils t'aiment encore | 400, ou dette −800 si tu couvres les trois |
| d05 | L'avocat du Carré | Me Desjardins | d02 | Sal veut saisir le garage : ramasser les papiers de Rocco dans le coffre de la planque, les porter au bar | 0 ; casier −2 (M11 : il efface une page) |
| d06 | Sal perd patience | Ti-Guy | d04 | les ciseaux s'en prennent au garage : _survivre_ 120 s, en coucher quatre | 200 |
| d07 | Le coffre de Sal | Josée | d06 | de nuit, vider le salon : ramasser le coffre (lourd, on marche), 2★, semer, le porter au bar | 2 000 ; **ferme d08** ; Sal ennemi — des ciseaux toutes les nuits, pour de bon |
| d08 | La dernière coupe | Sal | d06 [dette 0] | Sal te coupe les cheveux gratis et te donne la bague de Rocco | 0 ; **ferme d07** ; dette payée (le fil de _Sacrer son camp_) |

**Arc C — Le Clairon** (6) — Louise veut la une. Toi aussi, parfois.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| c01 | Une photo pour la une | Louise | m6 | _proteger_ Louise, qui monte avec toi : le poste, l'usine, le quai, dans la journée, pour ses photos | 150 |
| c02 | Le scoop du maire | Louise | e11 (dossier gardé) | lui porter le dossier de la villa | 800 ; manchette _Le maire dort à l'hôtel_ |
| c03 | La source | Louise | c01 | _proteger_ son informateur, un commis du poste, du poste à l'hôtel, de nuit, deux ciseaux aux trousses | 300 |
| c04 | La manchette sur toi | Louise | c01 | elle titrera si tu fais parler de toi : monter à 3★ et les semer en moins de 90 s | 200 ; manchette _Bandini l'insaisissable_ |
| c05 | Le Clairon brûle | Louise | c02 | les hommes du maire (des Chevreuils) attaquent le bureau : _survivre_ 120 s à l'intérieur, en coucher cinq | 400 |
| c06 | L'entrevue | Louise | 3 districts libérés | _parler_ seulement : trois questions, trois réponses au choix ; le narrateur lit la une le lendemain | 0 ; manchette au choix, lue par le narrateur |

**Arc R — Roy contre Bouchard** (7) — deux polices, et il faut choisir la sienne.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| r01 | La nouvelle inspectrice | Bouchard | m6 | Roy enquête sur lui : ramasser son carnet dans son bureau au poste, de nuit, `sans_etoile` | 400 |
| r02 | Roy te convoque | Roy | r01 | elle sait que c'est toi : _parler_ — elle offre un marché ; **r03 ou r04**, pas les deux | 0 |
| r03 | Le stool, c'est toi | Roy | r02 | être au casse-croûte à midi (`heure`), à moins de six tuiles de Bouchard quand Mado lui glisse l'enveloppe : _suivre_, _survivre_ 30 s sans qu'il te voie | 500 ; **ferme r04** ; Roy amie (casier −5), le sergent n'est plus ton ami |
| r04 | Le sergent contre-attaque | Bouchard | r02 | faire partir Roy : voler son auto-patrouille, la livrer au lot sous un faux nom (⏳ eau : au fond de la baie) | 500 ; **ferme r03** ; sergent ami pour de bon (pot-de-vin toujours accepté) |
| r05 | La salle des pièces | Bouchard | r01 | tes armes confisquées dorment au poste : en ramasser trois, de nuit, 2★, semer | 200 ; les armes reviennent |
| r06 | Une affiche de moins | Roy | r03 | arracher cinq affiches _Recherché_ dans le Faubourg avant le matin | 0 ; casier −3 |
| r07 | L'auto banalisée | Bouchard | r04 | en auto-patrouille (le déguisement), « arrêter » trois ciseaux de Sal pour lui — tuer n=3 en zone du Faubourg, sans étoile tant que tu es au volant | 400 |

**Arc T — Les petites jobs** (15) — des gens ordinaires, un peu partout. ⚠️ Le donneur est un
**archétype** (`pieton:<slug>@district:<slug>`), pas un personnage : le jeu en pose **un par
jour**, tiré parmi celles qu'on n'a pas faites, près d'un lieu du district, avec la bulle
« Hé! ». Ses répliques sont dites par les voix des passants. Une par jour, pas plus : ce
sont des rencontres, pas un tableau de bord.

| # | Titre | Qui, où | Ce qu'on fait | Paie |
|---|---|---|---|---|
| t01 | Mon char est au lot | banlieusard, Érables | reprendre son auto au lot (payer ou voler), la livrer chez lui | 80 |
| t02 | Le lunch des gars | débardeur, Quais | trois hot-dogs au kiosque, à rapporter avant midi | 30, et un hot-dog |
| t03 | Un lift au terminus | dame du Faubourg | la conduire au terminus en 60 s, sans un choc | 40 |
| t04 | Mon vélo | ado, La Pointe | un Skateux a son vélo : le reprendre, le lui ramener | 25 |
| t05 | La sacoche | passante, Faubourg | un itinérant est parti avec sa sacoche : le rattraper à pied | 50 |
| t06 | La commande de la taverne | commis, taverne (partout) | deux caisses de bière au quai, en camion | 90 |
| t07 | Le p'tit est perdu | mère, partout | trouver l'enfant (intouchable, il se cache), _proteger_ jusqu'à sa mère | 60 |
| t08 | Une job de bras | ouvrier, La Shop | trois boîtes à porter dans l'usine (lourdes, on marche) | 45 |
| t09 | La tournée du Clairon | marchand de journaux, Faubourg | six journaux à six portes, en vélo, 90 s | 60 |
| t10 | Le quart commence | machiniste, La Shop | le conduire à l'usine avant le quart, chrono 45 s | 40 |
| t11 | Le feu de camp | promeneur, La Pointe | un feu dans les bois : trouver un extincteur, _eteindre_ | 50 |
| t12 | Une course avec le livreur | livreur, Faubourg | _course_ en moto jusqu'à l'hôpital `contre` lui | 70 |
| t13 | La pelle du vieux | itinérant, Quais | une Morue a sa pelle : la reprendre | 20, et la pelle |
| t14 | Les mariés | dame, Érables | les conduire, à deux, en berline de luxe jusqu'au phare, sans bosse | 120 |
| t15 | L'autobus manqué | passant, terminus | il rate son quart à l'usine : taxi, chrono 90 s | 40 |

**Cinq défis de plus**, un par district, sur le modèle des trois qui existent (un panneau,
un chrono, une prime, une fois) : _Le tour des Quais_ (camion, 3 tours < 2:30) · _La descente
des Érables_ (vélo, du dépanneur à la villa < 0:45, sans tomber) · _Le drift de La Shop_
(coupé sport, dix stationnements traversés < 1:30) · _Le sentier de La Pointe_ (moto, six
points dans les bois < 1:00) · _Le port à port_ (n'importe quoi, du quai au phare < 1:20).
250 $ chacun.

#### Ajouté le 15 sept. 2026 — vingt missions de plus, après une tournée du net

_Demande de Martin :_ « regarde sur le net pour des idées de missions et tu peux en ajouter ou
modifier ce qui est dans le plan. »

Ce qui est ressorti de la comparaison avec les classiques vus d'en haut (GTA 1 et 2,
Chinatown Wars) : le catalogue d'ici **couvre déjà leurs verbes** — voler un véhicule précis,
filer quelqu'un, protéger, détruire, livrer au chrono, tenir un siège. Trois formes leur
appartiennent encore, et les voici. Les activités qui n'en sont pas (frénésies, liste du quai,
boulots gradés) ont leur propre fiche, plus haut.

**Arc I — L'Île-aux-Corneilles** (8) — la fiche de l'île est plus haut ; voici ce qu'on y
fait. Deux personnages de plus : **Sœur Jeanne** (`jeanne`, la dernière religieuse de la
chapelle) et **Léo Cyr** (`leo`, l'insulaire qui garde le hangar et ne pose pas de questions).

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| i01 | Le moteur tourne | Capitaine Bérubé | q08 | la chaloupe marche enfin : lui porter sa caisse d'outils **sur l'île**, et y mettre le pied pour la première fois | 120 ; l'île au carnet, contact Léo |
| i02 | La cloche de Sœur Jeanne | Sœur Jeanne | i01 | la cloche de la chapelle a fini chez Ti-Loup : la racheter (_payer_ 200) ou la reprendre, et la ramener par l'eau (lourde, on marche) | 150 ; **on dort à la chapelle** — une deuxième sauvegarde, à l'autre bout de la baie |
| i03 | Le hangar sans nom | Josée | q04, i01 | de nuit, `sans_etoile` : deux caisses à ramasser dans le hangar de Sven et à charger sur le bateau | 400 |
| i04 | Laisser refroidir | Léo | i01 | y amener un char **chaud** (3★ au départ), le laisser une journée entière, revenir le chercher | 0 ; le char repeint, les plaques changées — et la règle de l'île comprise |
| i05 | L'usine à poisson | Sœur Jeanne | i02 | des squatteurs ont mis le feu à l'ancienne usine : _eteindre_, puis en coucher trois | 200 |
| i06 | Le dernier bateau du Norvégien | Josée | i03, q11 | _detruire_ le bateau de Sven à quai, 3★ **sur l'eau** — et la police ne nage pas vite | 500 |
| i07 | Le tour de l'île | Léo | i04 | _course_ en bateau autour de l'île `contre` Léo, six points ⏳ bateau (repli : à la nage, trois points) | 200 |
| i08 | La cache de Rocco | Ti-Guy | i01, d05 | les papiers du coffre parlaient d'une île : ramasser la cache sous la chapelle, 2★ (quelqu'un d'autre la cherchait) | 1 200 |

**Le casse — arc X, _Le coup de la Caisse populaire_** (4) — la forme que le plan n'avait pas :
**trois préparatifs, puis le coup, et ce qu'on a préparé change le coup**. C'est le patron des
casses modernes, et il ne demande **aucun type neuf** : `exige` fait tout le travail.

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| x01 | Le repérage | Josée | d06, q11 ou q10 | la caisse populaire du Faubourg : y aller à trois heures différentes (matin, midi, soir) et _suivre_ le convoyeur jusqu'à son camion | 0 ; **ouvre x02, x03, x04** |
| x02 | Le char qui part vite | Josée | x01 | voler un **coupé sport**, le faire repeindre au garage, le garer à la planque | 0 ; le char à la planque (`exige` de x04) |
| x03 | Le linge propre | Rosa | x01 | une tenue de livreur oubliée à la boutique : la prendre et la porter | 0 ; la tenue (`exige` de x04) |
| x04 | Le coup | Josée | x01 [ce qu'on a préparé] | entrer à la caisse, _survivre_ 60 s, ramasser les sacs, semer 4★, livrer au bar | 2 500 ; **ferme d08** (Sal prend sa part) |

⚠️ **Sans les préparatifs, x04 se joue quand même — plus mal**, et c'est tout l'intérêt : sans
la tenue, on entre à 2★ au lieu de 0 ; sans le coupé sport, la police tient la poursuite ; sans
arme à feu, les 60 secondes se font aux poings. Le juge : la mission est **finissable** dans
les quatre combinaisons, et chaque préparatif manquant se **dit** à l'intro.

⚠️ **La caisse populaire est un cinquième lieu spécial** — le plan s'en tenait à quatre
exprès (une pièce à dessiner, une porte, un juge). Celui-là se paie : c'est le seul intérieur
où l'on se bat contre le temps.

**Huit missions de plus dans les arcs existants** — chacune vient d'un verbe des classiques
que Bandini n'utilisait pas encore :

| # | Titre | Donneur | Après | Ce qu'on fait | Paie |
|---|---|---|---|---|---|
| f13 | Les volontaires | Mado | f11 | trois feux dans la nuit, aux quatre coins du Faubourg : _eteindre_ chacun avant qu'il gagne la façade | 200 ; **le boulot pompier volontaire** |
| q14 | La liste du Norvégien | Sven (ou Ti-Loup si q11) | q10 ou q11 | quatre modèles sur l'ardoise du quai, à livrer sans bosse, un par jour | 250 ; **la liste du quai** (l'activité) |
| e14 | C'était un accident | Diane | e07 | la berline du maire doit finir dans sa propre piscine, et personne ne doit t'avoir vu (`sans_etoile`) | 300 ; Louise a sa photo |
| s14 | La casse à Ti-Loup | Ti-Loup | s02 | trois **autos-patrouilles** au compacteur dans la même nuit — chacune coûte au moins 1★, et il faut semer entre les deux | 450 |
| p12 | Le radeau de Zed | Zed | p04, i01 | les Skateux veulent l'île : leur amener un bateau au quai de La Pointe, sans le couler | 150 |
| h08 | La traverse de l'urgence | Dr Lachance | h04, i01 | quelqu'un s'est blessé sur l'île : y aller, le ramasser, le ramener à l'hôpital, chrono 200 s ⏳ traversier (repli : la chaloupe) | 250 |
| r08 | La patrouille de Roy | Inspectrice Roy | r03 | cinq fuyards rattrapés en auto-patrouille, en une semaine de jeu — le boulot patrouille, avec sa bénédiction | 250 ; casier −2 |
| d09 | Un compte sur l'île | Sal | d04, i01 | Léo doit 800 à Sal : _parler_, puis choisir — le coucher, ou payer pour lui | 250, ou dette −800 |

**Et deux choses qui changent dans ce qui existait :**

- **m99 _Le dernier traversier_ a enfin une dernière image.** Le traversier ne s'en va plus
  dans un fondu au noir : il **passe devant l'île**, Sœur Jeanne sonne sa cloche si on la lui a
  rendue (i02), et la ville rapetisse derrière. Rien de neuf à écrire — un trajet, et la caméra
  qui reste sur le quai.
- **p02 _Le pont est bloqué_ cesse d'être une fiction.** Les cônes des Skateux deviennent une
  **vraie barrière** du catalogue (fiche des zones conditionnelles) : fermée aux chars, jamais
  aux jambes, et forçable en défonçant. La mission ne pose plus le décor, elle **ouvre la
  barrière**.

#### Le compte, et l'équilibre

- **134 missions** (5 + 109 + 20), **8 défis**, **11 arcs**, **36 personnages**, 3 piétons de
  mission et un chien. Les missions **paient 35 990 $** si l'on additionne tout, un peu
  moins dans une vraie partie (les choix en ferment) — de quoi rembourser Rocco (15 000)
  **ou** acheter les quatre propriétés (17 800), jamais les deux : le reste vient des
  boulots, des propriétés et de ce qu'on vole.
  - ⚠️ **Et voilà exactement ce que vingt missions de plus coûtent à l'équilibre**, compté :
    elles paient **7 370 $** (368 en moyenne, contre 340 pour les 109 — les deux gros coups,
    le casse et la cache, en portent la moitié à eux seuls). La somme passe donc de 28 620 à
    **35 990**, soit **2,4 fois la dette** : la borne absolue du juge (24 000–32 000) ne
    survit pas à un catalogue qui grossit, et il faut le dire au lieu de le découvrir.
    - Ce qui la remplace est un **rapport**, parce que c'est lui qui porte le sens :
      **la somme reste sous 2,4 fois la dette**, et surtout **une vraie partie reste sous
      32 800** — le prix des deux fins ensemble (15 000 de dette + 17 800 de propriétés).
    - Et c'est tenable sans rien couper, parce que les **choix ferment** : q10/q11, r03/r04,
      d07/d08, e11, et maintenant x04 qui ferme d08. Une partie qui va au bout en perd
      environ 3 000 en chemin — donc ≈ 33 000 encaissés pour 32 800 à dépenser. ⚠️ **C'est
      serré exprès**, et c'est le juge à écrire : la partie la plus gourmande possible ne doit
      pas dépasser le prix des deux fins de plus de 5 %.
- **Chaque type d'objectif est utilisé au moins trois fois**, sinon il ne valait pas un
  type. Chaque district a **au moins dix missions** qui s'y passent, et chaque heure
  (jour, soir, nuit) en a.
- **Les fins tiennent.** _Le Boss_ demande quatre districts libérés : le Faubourg (m5), Les
  Quais (q13), Les Érables (e10), La Shop (s11), La Pointe (p11) — cinq possibles, quatre
  suffisent. _Sacrer son camp_ demande 15 000 $, et l'arc D ne l'exige pas : on peut partir
  sans payer Rocco, c'est même le propos de cette fin-là.
- ⚠️ **Le budget de voix** : ≈ 109 × 7 répliques × 75 caractères ≈ **57 000 caractères**,
  dix fois la v1, générés **par tranche** et jamais tous d'un coup. Les tests de
  `test_missions.py` qui bornent le catalogue à 30–60 voix et 4 000 caractères deviennent
  des bornes **par arc** ; la borne globale monte à 70 000. Et la règle de M6 tient : une
  réplique dont le fichier manque s'affiche sans voix.

#### Comment on le livre — quatre tranches, chacune jouable et déployée

1. **Le moteur, et le Faubourg** (taille 2) : les neuf types, `exige`, `ferme`, `donne`
   étendu, les résolveurs de lieux, les dialogues hors paquet, le téléphone qui trie ;
   m6 et l'arc F comme banc d'essai — douze missions qui utilisent tout. ⚠️ Le carnet
   (P2) doit être livré avant : sans lui, treize missions disponibles sont treize appels
   qu'on oublie.
2. **Les trois districts** (taille 2) : arcs Q, E, S et leurs dix-neuf personnages, les
   quatre lieux spéciaux, les trois piétons de mission, `libere` et `calme`.
3. **La Pointe, l'hôpital, la dette, le Clairon, la police** (taille 2) : arcs P, H, D, C,
   R ; Biscuit ; les choix (`ferme`).
4. **Les petites jobs, les défis et les fins** (taille 2) : arc T, les cinq défis, m97 à
   m99 — cette tranche-là **est** M13, qui garde les génériques et la ville qui change de
   couleur.
5. **L'île et le casse** (taille 2, ajoutée le 15 sept. 2026) : l'île et ses barrières
   d'abord (les deux fiches plus haut), puis l'arc I, l'arc X et les huit missions des autres
   arcs. ⚠️ Elle vient **en dernier** et elle ne bloque rien : aucune mission des quatre
   premières tranches n'en dépend, et les deux fins tiennent sans elle.

#### Juges

- **Le catalogue** : chaque mission a un donneur placé (jamais deux à la même porte), des
  lieux que `resoudre()` connaît, des types connus, des objectifs en majuscules de moins de
  60 caractères ; les prérequis sont sans cycle ; **une mission ⏳ n'est le prérequis de
  rien** ; chaque arc est atteignable depuis m6 ; chaque paire `ferme` ferme dans les deux
  sens et ne rapporte pas plus du double d'un côté ; la somme des récompenses reste dans sa
  fourchette ; chaque type sert au moins trois fois ; chaque district a ses dix missions.
- **Les fins** : un test rejoue le catalogue en respectant prérequis, `exige` et `ferme`, et
  atteint m98 **et** m99 (pas dans la même partie : m98 exige quatre propriétés et m99 quinze
  mille dollars en poche, le test le prouve).
- **Les voix** : un slug par réplique, ≤ 110 caractères, ≤ 2 phrases, un personnage connu
  avec une voix nommée ; jamais deux personnages de même voix dans un même dialogue ; le
  compte par arc et le total sous leurs bornes.
- **Le paquet** : sans les dialogues, il reste sous 600 Ko bruts et 70 Ko gzip ;
  `/api/dialogue/<slug>` répond 304 au deuxième passage et 404 pour un slug inconnu.
- **Le banc** : m6 de bout en bout ; **une mission par nouveau type**, jouée jusqu'à la
  récompense ; le singe qui prend vingt missions au hasard et ne trouve **aucune mission
  morte** (un objectif qu'on ne peut pas commencer depuis l'état où on le reçoit — un char
  qui naît dans un mur, un fuyard sans rue) ; le téléphone ne sonne jamais deux fois dans la
  même demi-journée, jamais en mission, jamais à 3★ ; une mission fermée n'apparaît ni au
  téléphone ni au carnet ; `libere` retire la zone du gang et `calme` retire l'hostilité, et
  les deux survivent à une sauvegarde.
- **Martin** : finir un arc par district au téléphone ; ne jamais se demander quoi faire
  (le carnet le dit) ; entendre trente-quatre personnes différentes sans qu'une seule
  paraisse en avoir la voix d'une autre.

### La ligne d'histoire : une ouverture et un générique (**ajout**, taille 3)

_Demande de Martin (16 sept. 2026) :_ « il faut qu'il y ait une ligne d'histoire qui
commence par une introduction audio et visuel au lancement du jeu... aussi une animation
audio visuel à la fin. »

_Ce que ça donne :_ on **sait qui on est** avant de faire un pas, et la partie **se termine**
au lieu de s'arrêter. L'histoire est déjà écrite partout dans le dépôt — l'oncle Rocco mort,
le garage dont on hérite, les 15 000 $ de Sal « Le Barbier » ; ce qui manque, ce sont ses
**deux bouts**, et le même narrateur aux deux.

⚠️ **Mesuré le 16 sept. 2026, et c'est ce qui découpe les deux vagues.**

- **Le lancement ne raconte rien.** Le titre est un voile HTML (`templates/index.html`,
  `voile-titre`) : un `<h1>Bandini</h1>`, la tagline du site, deux boutons et la liste des
  touches. Derrière, le canvas dessine **déjà** la ville figée au terminus — `rendre()`
  tourne dès le chargement, caméra centrée sur l'apparition — mais elle est **vide** : les
  entités ne naissent qu'à `Jeu.commencer()`. Celui-ci pose le bonhomme devant la porte,
  coupe le thème du menu et écrit `BAIE-DES-BRUMES` pendant 150 images. **C'est tout ce que
  le jeu dit de sa prémisse.**
- **La prémisse existe pourtant à trois endroits, et aucun n'est le jeu** : ce plan
  (« Prémisse »), `economie.DETTE` (15 000 $, 2 % par nuit, plafond à une fois et demie) et
  une réplique de Ti-Guy (`missions.py`, m1 : « Heille! Le cousin de Rocco! T'as fait bon
  voyage? ») qu'il faut **aller chercher** à la porte du terminus, et que rien n'oblige à
  entendre. Un joueur qui part à gauche ne saura jamais pourquoi il est là.
- **Le jeu ne finit nulle part.** `B.etat` ne prend que `titre | jeu | pause | carte` :
  l'état `fin` qu'annonce la carte du dépôt (« Côté JS », ligne `jeu.js`) **n'a jamais été
  écrit**, et le score ne part que d'un item du menu PAUSE (`BILAN DE LA SESSION` →
  `ENVOYER MON SCORE`, `Hud.demanderScore`). Une partie se quitte ; elle ne se conclut pas.
- **Le mécanisme, lui, est entièrement là** — c'est pour ça que l'ouverture est une vague de
  taille 2 et pas un jalon : `B.cinema` fige la ville et enchaîne des répliques **dites à
  voix haute** (`Histoire.dire` : ACTION passe, la voix finie passe toute seule, la radio et
  l'ambiance baissent), `Jeu.transiter()` fait un fondu dans le bon ordre, `Son.Mus` tient un
  thème avec sa queue, le **narrateur du Clairon** a déjà sa voix (`annonceur centre d'achat
  1`) et lit des textes qui ne sont pas des répliques de mission (`audio.voix_journal`, slug
  `narrateur-journal-…`), et l'**autobus** est un véhicule du catalogue avec son sprite,
  devant un **terminus** qui est le point d'apparition du joueur. Aucun sprite neuf, aucun
  moteur neuf.

#### 1re vague — l'ouverture — **livrée le 16 sept. 2026**

⚠️ **Ce qui a bougé en la faisant, et qui ne se devine pas** : `Jeu.commencer()` s'est coupé en
**deux**. Il POSE une partie — c'est ce qu'appellent cent tests du banc, qui veulent une ville et pas
une introduction — et le nouveau `Jeu.jouer()` est le **geste** : il pose la partie, puis lance
l'ouverture si elle est neuve. Les deux chemins de JOUER (le bouton de la page et la manette) passent
par `jouer()`. Sans cette coupure, chacun des cent tests aurait joué la scène avant de mesurer quoi
que ce soit. Et le morceau s'appelle **`ouverture`**, pas `mus_ouverture` : `mus_*` est le préfixe des
deux musiques d'ÉTAT (poursuite, bagarre), et l'ouverture est une pièce nommée comme `titre`.

- ⚠️ **Elle part sur JOUER, jamais au chargement de la page.** Le navigateur retient
  l'`AudioContext` tant que personne n'a touché (`Son.reveiller`, `Son.enAttente`) : une
  ouverture lancée par `Jeu.demarrer()` serait **muette une fois sur deux**, et une
  introduction audio muette n'est pas une introduction. Le bandeau du titre reste donc ce
  qu'il est — c'est lui qui réclame le geste — et l'ouverture commence juste après, dans
  `commencer()`. ⚠️ **Après**, et pas avant : c'est `commencer()` qui peuple la ville, et un
  autobus filmé sur une carte vide n'existe pas.
- **Ce qu'on voit** (rien de neuf à dessiner) : l'autobus entre par le bord de l'écran,
  s'arrête devant le terminus, la caméra le suit ; la portière s'ouvre, le bonhomme descend
  — il n'y a pas de valise dessinée, et on n'en promet pas ; le car repart, la caméra monte sur la ville et le titre s'inscrit.
  ⚠️ **Son propre noir, pas celui de `Jeu.transiter()`** : un fondu de porte FIGE la boucle
  (`B.transition` coupe `maj()`), or c'est justement pendant le noir que le car doit
  arriver. Deux compteurs qui ne veulent pas dire la même chose ne partagent pas une
  variable — le voile de l'ouverture vit dans `B.ouverture.noir`, dessiné par le HUD.
- **Ce qu'on entend** : le narrateur dit la prémisse en trois ou quatre phrases (l'oncle, le
  garage, la dette, les 50 $) sur `ouverture` — un morceau de plus dans `audio.MUSIQUES`
  (19 aujourd'hui, 851 s en tout) **et** écrit en notes dans `musique.py`, parce que les
  notes restent le filet. Le moteur au ralenti, la portière et la rumeur de la rue existent
  déjà au catalogue ; il n'y a que le soupir des portes d'air à ajouter, s'il en faut un.
- **Le texte reste la source** : les répliques de l'ouverture vivent dans `missions.py` comme
  toutes les autres, **jamais dans `histoire.js`**, et `audio.voix_ouverture()` les génère
  sur le modèle exact de `voix_journal()` (`mission: 'ouverture'`, slugs
  `narrateur-ouverture-1…n`). Une réplique dont le mp3 manque **s'affiche sans voix** : c'est
  la règle du fichier, et c'est elle qui permet d'écrire le texte avant de dépenser un
  crédit.
- ⚠️ **On la passe, et on la revoit.** ACTION saute une réplique (le cinéma sait déjà le
  faire), PAUSE saute l'ouverture entière — à la manette et au doigt comme au clavier. Une
  ouverture qu'on ne peut pas passer devient une punition à la deuxième partie.
- ⚠️ **Une partie en cours ne la rejoue pas.** `commencer()` reprend une sauvegarde (jour,
  position, char devant la planque) : l'ouverture ne joue qu'à la **première** partie d'une
  sauvegarde (drapeau `ouvertureVue`, versionné comme le reste de la sauvegarde et couvert
  par le repli sur `etatInitial()`), et se revoit à la demande depuis le carnet.
- ⚠️ **Le poids se surveille** : `static/audio/` pèse **12 Mo en 166 fichiers**, chargés à la
  demande (`fetch` puis `decodeAudioData`). L'ouverture est le seul son qu'il faut avoir
  **avant** de le jouer : elle se précharge pendant que le joueur lit l'écran titre, et si le
  fichier n'est pas là, le texte défile quand même.

#### 2e vague — le générique (taille 1, ⚠️ **attend M13**)

- ⚠️ **Il n'y a pas de fin à filmer avant M13.** Les deux fins (_Le Boss_, _Sacrer son camp_)
  sont la dernière tranche de **M16** ; cette vague est ce qui se **branche dessus**, pas ce
  qui les écrit. Ce qu'elle apporte au moteur : l'état `fin` qui manque à `B.etat`, et un
  enchaînement qui ne soit pas un item de menu.
- **Ce qu'on voit** : la ville en plan large, la caméra qui traverse le district libéré — ou
  le traversier qui s'éloigne du quai, selon la fin — puis les chiffres de la partie qui
  montent un à un (fortune, missions, propriétés, jours, la dette de Rocco réglée ou non),
  et la manchette du Clairon du lendemain.
- **Ce qu'on entend** : `generique`, dans `audio.MUSIQUES` et en notes comme les autres —
  une variante de l'ouverture, même tonalité, plus lente, pas un morceau étranger. Et la
  manchette **lue par le narrateur qui a ouvert le jeu** : c'est le même homme aux deux
  bouts, et c'est ça qui fait une ligne plutôt que deux animations.
- **Elle mène au score** : `Hud.demanderScore()` existe déjà et n'est appelé de nulle part
  ailleurs qu'un menu. Le générique est le seul endroit du jeu où l'envoi s'offre tout seul.
- ⚠️ **La partie continue après le générique** (règle de M13, inchangée) : le score part, le
  monde reste, la sauvegarde ne se referme pas. Un générique qui verrouille la ville
  transforme une fin en écran de défaite.

**Ce que ça coûte en crédits** : deux morceaux de 45 s à **30 crédits la seconde = 2 700**
sur les 90 000 du mois, plus quelques centaines de caractères de narration (les voix se
paient au caractère). Même échelle que les dix-neuf morceaux déjà générés.

**Juges** — la règle habituelle : on juge le **câblage**, pas la fiche.

- _Python_ : chaque réplique de l'ouverture a un personnage connu et un slug de voix unique ;
  `ouverture` et `generique` existent des **deux** côtés (un mp3 déclaré par
  `exporter()` **ou** des notes dans `musique.py`) — une musique qui n'a ni fichier ni notes
  est un silence qui se déploie.
- _Banc_ : l'ouverture se **termine toujours** (elle ne peut pas laisser `B.cinema` ouvert),
  PAUSE la saute à n'importe quelle réplique, et l'état de la partie après l'ouverture est
  exactement celui qu'on aurait sans elle — joueur vivant, à sa tuile, sans étoile, sans
  mission en cours.
- _Banc_ : une sauvegarde qui porte `ouvertureVue` ne rejoue pas l'ouverture ; une sauvegarde
  d'avant le drapeau ne plante pas.
- _Navigateur_ : JOUER au clavier **et** à la manette lance l'ouverture, aucune erreur
  console, et le son n'est jamais demandé avant le geste.
- _Générique_ : le test qui force chacune des deux fins (déjà prévu par M13) vérifie qu'on
  retombe sur une ville jouable, score envoyé ou non.

⚠️ **Ce que les juges de la 1re vague ont réellement attrapé** (13 dans `test_ouverture.py`, plus un
dans `test_navigateur.py`) : deux pièges de mesure dans les juges eux-mêmes — le banc **écrit dans le
tableau de traces qu'on tient** (sans `.slice()`, les images suivantes remplissent la mesure qu'on
vient de prendre), et compter les `fillRect` pour prouver que le HUD se tait **accuse l'ouverture** :
le titre « BANDINI » en corps 4 s'écrit pixel par pixel et en dessine plus qu'un HUD complet. On juge
donc un rectangle NOMMÉ (la barre de vie, `6, 6, 60, 5`), pas un nombre. Et le juge « l'ouverture ne
change rien » a tenu du premier coup — parce que la règle « aucun dé tiré » était écrite avant le
code, pas après.

### M13 — Les deux fins (**ajout**, taille 4)

_Ce que ça donne :_ une histoire qui se termine, de deux façons.

- **Une mission par district** — et bien plus : les arcs de district, les donneurs, les
  voix et les trois missions de fin (m97 _Marco te vend_, m98 _Le Boss_, m99 _Le dernier
  traversier_) sont décrits dans **M16**, dont M13 est la dernière tranche. Ce qui reste
  ici : les génériques, la ville qui change de couleur, la partie qui continue.
- **Marco te vend** : au bout de l'arc, le cousin parle à la police — la mission bascule en
  cours de route.
- **Dr Lachance** devient donneur : l'hôpital a ses secrets (et ses ordonnances).
- **Le Boss** : les 4 propriétés **et** les 4 districts libérés → manchette, générique, la
  ville change de couleur.
- **Sacrer son camp** : 15 000 $ en poche, traversier de nuit, 0★ → l'autre générique.
- **Le générique** — l'animation audio-visuelle de fin, le narrateur du Clairon,
  `generique` — est décrit juste au-dessus, dans « La ligne d'histoire » : M13
  fournit les deux fins, cette section-là fournit ce qu'on en voit et ce qu'on en entend.
- La partie **continue après la fin** : le score part, le monde reste.
- **Juges** : un test force chacune des deux fins (elles sont atteignables) ; la dette reste
  remboursable jusqu'au bout (aucune fin ne se referme sur un bug) ; chaque réplique
  nouvelle a son personnage et sa voix.

## Serveur (M0, `deploy/installer.sh`, idempotent, en `dojoadmin`)

1. DNS d'abord : `namesilo_addDnsRecord(domain=gestiondojo.ca, rrtype=A, rrhost=bandini, rrvalue=103.98.215.181, rrttl=3600)`.
2. `ss -ltnp | grep ':8006'` vide ; `/srv/bandini/{repo,shared/donnees,releases}`, `chown www-data shared/donnees` ; clone HTTPS public ; `.env` (SECRET_KEY généré, `APP_BASE_URL`, `DONNEES_DIR`, `STATIC_MAX_AGE=604800`), `chown dojoadmin:www-data`, `chmod 640`.
3. systemd (`enable`), nginx (`nginx -t`, reload), Caddy : sauvegarde, `sed` après `auto.gestiondojo.ca,`, `caddy validate`, reload.
4. `bash /srv/bandini/repo/deploy/deploy.sh main` ; quand `dig +short bandini.gestiondojo.ca @1.1.1.1` répond, `systemctl reload caddy` pour relancer le certificat.
5. SSH toujours avec `-i ~/.ssh/dojo_deploy -o IdentitiesOnly=yes -o BatchMode=yes` (fail2ban après 3 échecs) ; `curl` toujours avec `-A navigateur` et `--resolve` tant que le cache DNS local est vide.

## Tests et CI

- **pytest** : modules Python (invariants ci-dessus), routes, scores, version.
- **JS déterministe via pytest + Node** (`harnais_js.py` + `banc.js`, `ENTREE` = le paquet Python réel) : intégrité des sprites, cercle-vs-tuiles, cône de vision, décroissance des ★, amendes, monter/descendre, trafic, physique, missions, sauvegarde v0 → repli, budget de rendu, singe (3 000 pas en CI, `BANDINI_SINGE_PAS=50000` en local).
- **Playwright** (`test_navigateur.py`, fixture `serveur`) : 4 écrans (1280×720, 1024×768, 390×844, 844×390) ; aucune erreur console ; Jouer → état `jeu` ; clavier déplace ; tactile : commandes ≥ 64 px (pause 44), dans l'écran, sans chevauchement, glisser sur `#croix` déplace ; envoi de score.
- **CI** (dépôt public) : job `rapide` (uv sync, dépendances synchronisées, ruff, pytest sans navigateur, `BANDINI_TESTS_OBLIGATOIRES=1`) puis `navigateur` (cache Chromium sur `uv.lock`), < 3 min.
- **La carte du dépôt** (l'arborescence ci-dessus et les tableaux « Côté Python » / « Côté JS ») : `scripts/verifier_carte_du_depot.py` la compare aux fichiers que git suit, `tests/test_carte_du_depot.py` fait échouer la CI quand un fichier n'y est pas — et deux **gardes Claude Code** (`.claude/settings.json`) le rappellent plus tôt, là où corriger ne coûte rien : à l'écriture d'un fichier (PostToolUse `Write|Edit`) et avant `git commit` (PreToolUse `Bash`, qui lit le plan de l'**index**, pas celui de l'arbre — sinon la carte corrigée resterait sur le bureau). ⚠️ Pourquoi une garde et pas seulement un test : le 13 sept. 2026, trois tests, deux scripts et quatre modules existaient sans y être, et personne ne relit l'arborescence avant de committer. Un fichier **à venir** se note avec son jalon entre parenthèses sur sa ligne (`bd.py comptes.py (M14 — …)`) : c'est ce qui l'excuse d'être absent ; `static/audio/` se couvre d'un seul trait.
- **La table des jalons** (« État des jalons », tout en haut) : `scripts/verifier_table_des_jalons.py` vérifie qu'elle garde ses **six colonnes** (`Jalon | État | Date | Prio | Genre | Notes`) et que chaque cellule dit ce qu'elle doit dire — un état connu, une date `14 sept. 2026` ou `—`, une prio `P1`–`P4` ou `—`, un genre `ajout` ou `correctif`. `tests/test_table_des_jalons.py` fait échouer la CI, et les deux mêmes **gardes Claude Code** que la carte du dépôt le rappellent à l'écriture et avant `git commit`. ⚠️ Pourquoi : la table a été divisée le 14 sept. 2026, et le jour même une session qui n'avait pas vu passer le changement a rajouté sa ligne dans l'**ancienne forme à trois colonnes** (`| Un poteau par coin | **P2** **correctif**, **en cours** (14 sept. 2026) | … |`). Markdown ne s'en plaint pas : il avale la ligne et la rend de travers, et la division se perd sans qu'un test rougisse. C'est le risque propre à un fichier que **plusieurs sessions écrivent en même temps** — la forme doit se défendre toute seule, parce que personne ne relit l'en-tête avant d'ajouter sa ligne.
- **Ce qui se dit destructible** (`const DECORS`, dans `static/js/sprites.js`) : `scripts/verifier_ce_qui_casse.py` tient la fiche d'un décor et le **câblage** qui s'en sert. La fiche dit trois choses et elles vont par paires — `arrete: masse` (il arrête un char sous cette masse, encaisse les balles et ne tombe **jamais** : c'est ce qui fait un abri), `casse: fraction` (il cède sous un char lancé) et `pv` (ce qu'il faut lui mettre à l'**arme** pour l'abattre, en balles de pistolet). Le juge exige qu'un décor `solide` déclare l'un des deux (sinon il est **fantôme pour les chars**), que `casse` et `pv` aillent ensemble dans les deux sens, qu'`arrete` n'ait jamais de `pv` — et que les **quatre appelants existent** : le char (`Entites.briser`), la balle, le feu et l'explosion (`Entites.endommagerDecor`). `tests/test_ce_qui_casse.py` fait échouer la CI (6 juges de forme, 6 de banc qui tirent pour de vrai), et les deux mêmes **gardes Claude Code** que la carte du dépôt le rappellent à l'écriture et avant `git commit`. ⚠️ Pourquoi : un lampadaire portait `casse: 0.7` **depuis toujours** et encaissait un chargeur de carabine sans broncher — `Entites.briser` n'avait qu'un seul appelant, le char. Rien ne rougissait : la fiche promettait, et personne ne vérifiait que quelqu'un s'en servait. Et pire, `buisson` et `corde_a_linge` promettaient `casse` avec `solide: false` alors que l'index du décor ne prenait que le solide : **rien au monde** ne pouvait les toucher, depuis le premier jour. Une fiche n'est pas une garantie tant qu'un juge ne relie pas les deux bouts.
- **Le filtre des trois gardes** (`.claude/settings.json`, `PreToolUse` / `Bash`) : ils ne se réveillent que devant une commande qui commite, et ce filtre est le **même pour les trois** — un détecteur qui diverge de son jumeau ne garantit plus rien des deux côtés. ⚠️ Mesuré le 15 sept. 2026 sur treize commandes : `*'git commit'*` laissait passer **deux vrais commits** — `git -C /autre/depot commit` et `git -c user.name=X commit`, où les deux mots ne sont pas collés. Élargi en `*'git commit'*|*'git -'*' commit'*` : zéro faux négatif, et **pas un bruit de plus** (`git log … | grep commit` ne le réveille toujours pas). ⚠️ On **élargit, on ne rétrécit jamais** : un garde doit rater bruyamment. Il reste donc cinq faux positifs assumés — `git commit-tree`, `git commit-graph`, et toute commande dont le simple *texte* contient la chaîne (un `echo`, un `grep`, un message en heredoc). Ils ne coûtent qu'un démarrage de Python, et ils ne **bloquent** que si le dépôt viole vraiment l'invariant — auquel cas ils disent vrai, juste à un moment inattendu. Pour faire de la plomberie git sans les réveiller, couper la chaîne (`G=git; $G commit-tree …`).

## Vérification de bout en bout

1. `uv run ruff check . && uv run pytest -q` verts ; `uv run python run.py` → http://127.0.0.1:5400.
2. Playwright local : captures aux 4 écrans (garage, rue de jour, nuit à 3★, prison).
3. Après chaque déploiement : `/sante`, `/api/definitions` (gzip + ETag → 304), `/static/js/jeu.js` 200, POST puis GET `/api/scores`, `journalctl -u bandini-gestiondojo`.
4. Martin teste sur téléphone (tactile) et sur ordinateur (manette) à chaque jalon.

## Risques et parades

- **Sensation de conduite** : cercles plutôt qu'OBB, sous-pas, constantes éditables en console, séance de réglage tactile/manette en fin de M3.
- **Performance téléphone** : cache de morceaux, bulle d'activité, lumière demi-résolution, plafonds `stats` en CI, dégradation automatique.
- **Police omnisciente ou aveugle** : tout passe par `voit()`, cônes en débogage, tests déterministes, témoins visibles (bulle « ! »).
- **Volume d'art en code** : petits sprites, swaps de palette, 3 caps par véhicule, galerie `planche()` pour tout inspecter, validateur strict en CI.
- **Ville générée injouable** : plan à la main, graine fixe, juges de connexité en pytest **avant** de dessiner.
- **Dérive de la sauvegarde** : clé versionnée, repli sur `etatInitial()`, test d'un blob v0.
- **Audio iOS** : réveil au premier geste, pause sur `visibilitychange`.
- **Ville cinq fois plus grande (M8)** : le paquet est mesuré (17 Ko gzip aujourd'hui), le
  budget du test relevé en connaissance de cause, et le déclencheur du découpage écrit
  d'avance ; le cache de morceaux et la bulle d'activité bornent déjà le travail par image.
- **Véhicules qui sortent des rails (M9, M12)** : le tramway et le bateau **n'obéissent pas**
  au champ de direction. Chacun est un conducteur à part (`conducteur: 'rail'`, `'eau'`),
  jamais une exception glissée dans `majConducteur` — et le mode trace les surveille comme
  le reste.
- **Un char rapide qui casse toutes les poursuites (M9)** : le jour où le sport roule plus
  vite que l'auto-patrouille, la police du jeu entier devient décorative — et c'est le genre
  de dégât qu'on ne voit pas en jouant dix minutes. Trois parades, et il en faut trois :
  la vitesse de pointe reste **sous la moto** et ne dépasse la patrouille que d'un cheveu
  (un juge le mesure) ; la carrosserie est mince, donc un **barrage** l'arrête pour de bon ;
  et l'**hélico** de 4★ ne court pas après, il suit. La vitesse achète de la distance,
  jamais l'impunité.
- **Économie qui se joue toute seule (M10)** : tout gain passe par un juge « à l'heure »,
  comparé au taxi ; la fraude et les skimmers doivent rester moins payants que le travail.
  Le **luxe** de M9 tombe sous la même règle : sa revente est la meilleure du jeu, mais le
  malus par doublon du même jour interdit d'en faire une chaîne de montage.
- **Le serveur devient indispensable (M14)** : c'est le vrai danger du compte. Un jeu qui
  tourne dans le navigateur et qui ne démarre plus parce qu'une base de données est barrée,
  qu'un certificat a expiré ou qu'on est dans le métro, a perdu ce qu'il avait de mieux. Le
  `localStorage` reste donc le **défaut**, le compte n'est qu'une synchronisation, et le
  jeu doit se lancer, se jouer et se sauvegarder **serveur éteint**. Un test le vérifie en
  coupant le réseau, pas en le supposant.
- **Des mots de passe et des comptes à garder (M14)** : hachage par `generate_password_hash`,
  `SECRET_KEY` vraie en production (voir les Dettes), courriel facultatif, une page qui dit
  ce qui est gardé et un bouton qui efface tout. Et une base de données sans **copie de
  sûreté quotidienne** est une perte de données qui attend sa date : le vidage est dans
  `installer.sh`, pas dans une bonne intention.
- **Un chantier qui coupe la ville (M12)** : une voie fermée au mauvais endroit, et un
  quartier devient inatteignable en char sans qu'aucune capture d'écran ne le montre. Le
  juge de M1 (`voies_bloquees`, fortement connexes) se rejoue **avec le chantier posé** ; il
  rougit, le chantier se pose ailleurs. Jamais sur un pont, jamais sur une rue à voie unique.
- **Coop locale (M14)** : un essai jetable avant toute promesse ; si l'écran est trop petit
  à deux, le jalon tombe et le mode photo suffit.
- **Audio absent ou cassé** : `exporter()` ne déclare que les fichiers présents, chaque
  effet retombe sur la synthèse, et un test navigateur prouve que chaque MP3 **se décode
  vraiment** (un fichier tronqué ne se verrait qu'à l'oreille, en jeu).
