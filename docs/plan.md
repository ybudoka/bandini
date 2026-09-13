# Bandini — plan et état d'avancement

Document de reprise : à lire en début de session. Le plan ci-dessous a été
approuvé par Martin le 12 septembre 2026. Mettre à jour la section « État des
jalons » à chaque jalon livré.

## État des jalons

Les lignes **livrées** sont dans l'ordre où elles l'ont été ; celles **à faire** sont dans
l'ordre où on compte les faire — **par priorité**, prérequis devant (le détail est dans
« La v2 » plus bas).

⚠️ **Chaque ligne à faire porte sa priorité (P1 à P4) et son genre.** Un **correctif** répare
une promesse que le jeu fait déjà et ne tient pas ; un **ajout** en fait une nouvelle. La
priorité répond à « qu'est-ce qui coûte le plus cher à ne pas faire ? » — **P1** le jeu ment,
**P2** ça se sent à chaque partie, **P3** ça porte le reste, **P4** ça enrichit ; l'échelle
est détaillée dans « La v2 ». Le genre suit les préfixes de commit du dépôt (`fix:` et
`feat:`) ; pour les lignes déjà livrées, c'est donc l'historique git qui le dit.

⚠️ Les numéros de jalon sont des **noms**, pas un ordre : tout le dépôt y renvoie, alors ils
ne bougent pas quand l'ordre de travail change.

| Jalon | État | Notes |
|---|---|---|
| M0 Squelette et mise en ligne | **livré** (12 sept. 2026) | dépôt `ybudoka/bandini`, Flask + uv, 13 fichiers JS, entrées, banc Node, CI, tests ; serveur installé, https://bandini.gestiondojo.ca |
| M1 La ville | **livré** (12 sept. 2026) | `carte.py` : trame **irrégulière** (colonnes, rangées et rues toutes différentes), superblocs qui avalent des rues, parcelles BSP par îlot, 157×112 tuiles, 62 croisements dont des T, 10 intérieurs ; juges (voies fortement connexes, un seul îlot marchable, **asymétrie**) ; cache de morceaux borné, mini-carte |
| Audio ElevenLabs | **livré** (12 sept. 2026) | MCP `elevenlabs` + `app/audio.py` + 18 bruitages dans `static/audio/` ; **3 radios** (La Brume jazz, Taxi-Radio country, Le Choc **techno**) et une **musique de fond** de ville (à pied) par ElevenLabs Music, chargées au premier geste ; **rumeur de la foule** (volume selon les gens autour), chars et motos qu'on entend passer (placés dans le stéréo), sonnette de vélo ; **8 répliques de passants** (Léo québécois / Sarah) par TTS — voix des donneurs en M6 |
| Vie de rue | **livré** (12 sept. 2026) | femmes, enfants (**intouchables**), mères suivies de leur petit, filles de la Brume (la nuit, un fondu, jamais une scène), kiosques à hot-dogs / journaux / roulotte à café et camions-restaurants posés par `carte.py` |
| La rue dans la vraie vie | **livré** (13 sept. 2026) | retour de Martin (chars fous, piétons sur la chaussée, puis chars coincés au croisement, bandes des passages à l'envers) : un char d'en face dans la voie d'à côté n'est plus un obstacle, un croisement se **réserve** (un char à la fois, jusqu'à ce qu'il ressorte), les bandes sont parallèles à la circulation ; le trafic roule **sur des rails** (centre de tuile en centre de tuile, jamais un coin coupé), les piétons **ne posent pas le pied sur la chaussée** et traversent au passage quand c'est sûr, sortent des portes et rentrent chez eux ; **feux visibles** aux vrais croisements, **STOP** à la tige des T, priorité aux piétons engagés, **cyclistes** dont on prend le vélo |
| M2 Piétons et poings | **livré** (12 sept. 2026) | `pietons.py` (8 archétypes, courage, témoin, gangs) ; hachage spatial, bulle de foule, flâner/fuir/témoin/riposter, mêlée en trois temps, coup fort, roulade, projectiles + plombs + cloche, visée assistée, armes de fortune qui cassent, sang plafonné, pickpocket dans le dos |
| M3 Véhicules | **livré** (13 sept. 2026) | auto, taxi, moto, auto-patrouille (sprite) ; physique arcade, **chaîne de cercles**, sous-pas, monter/descendre/carjacking/éjection, trafic qui **lit le champ `voie`** (tourne à gauche après le croisement, ralentit avant le coin), feux sur les vrais croisements, dégâts/fumée/feu/explosion, alarmes, rampes, renversements, taxi au klaxon avec pourboire selon la douceur, hôpital quand on meurt, moteur qui monte dans les tours |
| M5 Intérieurs et économie | **livré** (13 sept. 2026) | entrer/sortir des 10 intérieurs (fondu, pièce centrée, points d'action), menus canvas qui figent le jeu, planque (dormir = sauvegarder + lendemain, coffre à l'abri de la prison, garde-robe, char stationné qui revient), garage (revente, réparation, peinture qui efface le vol), Chez Gus (armes, munitions), Boutique Rosa (tenues), casse-croûte, hôpital, propriétés (achat à la porte, caisse plafonnée à 3 jours), 20 paquets cachés + primes, journal du matin (`journal.py`), pause = menu (reprendre, **bilan de session**, **options** sang/vibration/son/daltonien sauvegardées, envoi du score) |
| Gestes et lisibilité | **livré** (13 sept. 2026) | retour de Martin : le corps **bouge** quand on agit — élan du coup, bras et arme superposés (toutes armes, PNJ compris), chancellement quand on est touché, roulade qui tourne, dos courbé pour ramasser, éclair de bouche au tir ; les accents et l'apostrophe courbe tombaient sur « ? » dans la police pixel — normalisés avant le dessin, avec un test sur chaque nom du jeu |
| M4 Police | **livré** (13 sept. 2026) | `police.js` réécrit : agents à pied (archétype `policier`, patrouille par zone, cône vérifié une image sur trois, poursuite par **A\*** sur les trottoirs, arrestation au contact, sortent le joueur d'un char arrêté), **rien n'est compté tant qu'un agent ne l'a pas vu** — un passant qui a vu devient témoin porteur du crime, court le raconter à un agent ou téléphone (`temoins`), et on peut **acheter son silence** (20 $) ; délits bruyants (`temoin: false`) comptés tout de suite ; étoiles qui ne tombent qu'hors de vue (dedans aussi) ; menu d'arrestation **obligatoire** (pot-de-vin selon casier/étoiles, sergent ami plus tard, refus = délit) ; prison (amende, armes confisquées, casier, 6 h, réveil au poste, sauvegarde) ; autos de patrouille à 3★ qui **suivent les rails** vers le joueur (feux brûlés, sortie vers lui) et foncent de près, agents qui descendent ; tirs à 3★ ; −1★ en changeant de char hors de vue ; affiches « Recherché » sur les façades à 2★ ; blips bleus, étoiles qui clignotent ; **mode TRACE** (idée de Martin) : le jeu dessine le trajet de chaque char et se surveille (chien de garde, tour en rond, hors voie) |
| M6 Missions et gang | **livré** (13 sept. 2026) | `missions.py` : 6 personnages (une voix ElevenLabs chacun), **5 missions** (Ti-Guy, Mme Thibodeau, Marco, Sgt Bouchard, Josée) en objectifs typés, 35 répliques, 3 défis ; `histoire.js` : donneurs devant leur porte (ou à leur point dedans), **dialogues dits à voix haute** (chargés par mission, ducking radio/ambiance, voix « du combiné » au téléphone, le joueur écoute), **téléphone** (le donneur suivant appelle), machine à objectifs (aller/monter/livrer/tuer/ramasser/courses/semer/retourner), char de M1 dans une ruelle, fuyard en moto sur les rails (fuite), escorte de Ti-Guy, Cravates posées en ville, échec sur prison/hôpital, récompenses (bâton, rabais, sergent ami → pot-de-vin, bar, Faubourg libéré, manchette), **GPS** (blip, flèche au bord, distance), objectif en haut, **défis** à panneaux (saut, tour chrono, livraison sans bosse), gang qui attaque l'arme au poing sur son territoire |
| M7 Finition v1 | **livré** (13 sept. 2026) | **5★** : hélico (te survole, rien ne retombe sous lui, ombre au sol, projecteur la nuit, rotor en boucle ElevenLabs) et **barrages** (deux autos-patrouille en travers devant toi, deux agents derrière) ; **journal lu par le narrateur** (9 manchettes + celle de M5, voix « annonceur centre d'achat 1 », version `lu` en casse naturelle) ; **marché noir** chez Josée après M5 (`magasins.MARCHE_NOIR`, −30 %) ; **carte de la ville** plein écran (N, ou PAUSE → CARTE : lieux, police, objectif, joueur) ; sonnerie de téléphone réelle ; sonde de performance Playwright (ms par image de nuit à 3★ au volant). Défi du jour à graine serveur : reporté en v2 |
| **v1 complète** | **livrée** (13 sept. 2026) | M0 → M7 en ligne, 308 tests ; la suite est planifiée ci-dessous (« La v2 — huit vagues ») |
| M8 Les cinq districts | **livré** (13 sept. 2026) | la ville passe de 157×112 à **421×213 tuiles** (5,1 ×) : Les Érables (banlieue, Les Chevreuils), La Shop (industriel, Les Boulonneux), Les Quais (port, Les Morues), La Pointe (parc, Les Skateux) et **la baie** — une seule grille de blocs, un district par rectangle, aucune fusion par-dessus une frontière ; une rue dont tous les blocs voisins sont de l'eau est **noyée** (c'est ce qui ferme la baie et coupe le chenal), et **un pont** relie La Pointe ; 5 nouveaux lieux (dépanneur, Hôtel Bandini, cantine des Quais, usine Prévost, phare) ; 4 gangs + 4 passants de quartier (`districts` les enferme chez eux) ; densité **et rythme** par district (La Shop déserte la nuit, les Quais le matin) ; radios *10-4* et *Radio-Traversier* ; paquet **319 Ko bruts / 33 Ko gzip**, `generer()` 94 ms au démarrage, **0,29 ms par image** de nuit à 5★ (0,26 avant) ; chien de garde du trafic corrigé (480 images de feu rouge **puis** l'attente de boîte faisaient 600 : il mordait un char sage) |
| Manette réapprenable | **livré** (13 sept. 2026) | retour de Martin (« les boutons de la manette bluetooth ne sont pas bien mappé ») : les numéros de boutons d'une manette que le navigateur ne reconnaît pas (`mapping: ""`) ne veulent rien dire — la même manette n'a pas les mêmes numéros sur le téléphone et sur le Mac, **ça ne se devine pas**. OPTIONS > **MANETTE** : des **dispositions à choisir** (`app/manettes.py` : Xbox/PlayStation, **8BitDo en Bluetooth**, Bluetooth croix-sur-un-axe) et un **dessin de manette en pixels** qui sert de **preuve** — on appuie, la pièce s'allume ; au bon endroit, c'est la bonne disposition. Le dessin s'allume par **numéro de bouton**, pas par action : l'épaule droite et le bouton de gauche font la même chose et doivent pourtant se distinguer. ⚠️ Sur cet écran la manette ne **ferme** plus le menu (`manetteInerte`) — on y appuie sur ses boutons pour les voir, pas pour commander — mais elle peut encore bouger le curseur et choisir, sinon un joueur qui n'a qu'une manette resterait enfermé. Deuxième écran, RÉAPPRENDRE : ce que la manette dit d'elle-même (nom, RECONNUE / NON RECONNUE, boutons enfoncés et axes qui bougent en direct), une ligne par action qu'on réapprend en l'appuyant, la croix en quatre gestes, gaz et frein en **bouton ou en axe** (repos mesuré : une gâchette-axe repose à −1 sur une manette et à 0 sur la suivante), TOUT RÉAPPRENDRE qui enchaîne, PAR DÉFAUT ; gardé dans les options. **Croix-chapeau** : sur une 8BitDo en Bluetooth la croix n'est pas quatre boutons mais UN axe — on appuie et aucun numéro ne s'allume, elle a l'air morte ; on apprend HAUT et DROITE et le tour des huit positions se déduit, diagonales comprises (sinon repli sur les quatre côtés). L'écran liste les **axes qui bougent**, nomme un bouton **que la disposition ne connaît pas** (sinon il n'allume rien et on croirait la manette morte), et souffle le mode Xbox aux 8BitDo (le dongle 2,4 GHz ou le câble : c'est là que le navigateur les reconnaît). ⚠️ **Mesure de Martin** : ses gâchettes ouvraient la carte et la pause — or carte et pause sont 8 et 9 sur une manette reconnue, donc ses gâchettes *sont* 8 et 9, et toute la numérotation DirectInput suit (boutons de droite 0/1/3/4, épaules 6-7, SELECT/START 10-11). Un juge garde ce fait : le « corriger » effacerait le retour. ⚠️ Un apprentissage **attend qu'on relâche** : sur un axe, lâcher le haut bouge autant qu'appuyer sur le bas, et la direction suivante s'apprenait sur la valeur du repos — la croix tenait alors les quatre directions en permanence. Corrigé au passage : `annuler` n'avait **aucun** bouton (le bouton de droite fait RETOUR), et « Jouer » n'était qu'un bouton de la page — on commence maintenant la partie à la manette ou au clavier |
| Le son retenu | **livré** (13 sept. 2026) | retour de Martin (« regarde pourquoi je n'ai pas de son ») : un `AudioContext` naît **suspended** tant que la page n'a reçu aucun **vrai geste** (clic, touche, toucher), et `resume()` est alors refusé — or **l'API Manette ne compte pas comme un geste**. Depuis qu'on peut commencer la partie au pad (0.16.0), un joueur à la manette traversait donc toute la ville en silence, et le refus était avalé par un `.catch()` vide : **rien** ne le disait. ⚠️ La panne n'était ni dans les fichiers (79 mp3 servis en 200) ni dans le serveur (le paquet annonce bien ses 20 échantillons) ni dans le code du son — elle était dans **la permission du navigateur**, qu'on ne pensait même pas à demander. `Son.etatSon()` distingue maintenant quatre silences très différents : `actif`, `attente` (il manque un geste), `coupe` (choix du joueur, OPTIONS) et `absent` (pas d'audio du tout — le banc) ; un bandeau sur l'écran titre dit quoi faire **avant** qu'on joue, un message le redit si on commence quand même au pad, et OPTIONS porte une ligne **SON** qui n'est pas un réglage mais un **diagnostic** — sans elle, on cherche la panne dans ses haut-parleurs. `resume()` étant asynchrone, l'état revient par `onstatechange`, sinon le bandeau resterait affiché alors que le son est revenu. ⚠️ Le banc a maintenant un **faux AudioContext** (`o.brancherAudio(false)`) qui refuse `resume()` : c'est le seul endroit où l'on peut reproduire le silence à volonté — et le vrai Chromium des tests le confirme, il charge la page avec un contexte `suspended` |
| Devantures et graffitis | **livré** (13 sept. 2026) | demande de Martin (« ajoute des façades distinctes et vraiment commerciales, pour les commerces et avec du lettrage et pancartes ; ajoute des graffitis sur certains bâtiments »). Avant, tous les commerces étaient le même mur percé d'une porte : on savait qu'un bâtiment était un commerce parce que le générateur le disait, pas parce qu'on le voyait. **118 devantures** (`app/devantures.py`) — un BANDEAU sombre, le NOM en lettres pixel (la police 3×5 du HUD, 4 px par lettre : 16 caractères sur quatre tuiles), un AUVENT rayé, une VITRINE au pied du mur et une PANCARTE qui dépasse sur le trottoir. Sept familles de couleurs (bouffe, service, artisan, nuit, commerce, marine, industrie) et **des noms par district** : une poissonnerie aux Quais, un atelier de soudure à La Shop, une garderie aux Érables — un juge interdit de les mélanger, sinon les cinq districts redeviennent le même quartier repeint. Les lieux garantis portent leur vraie enseigne (CHEZ GUS, LE BROUILLARD, CHEZ TI-PAUL) ; ⚠️ **la planque n'en a pas** — une planque avec son nom sur le mur n'est plus une planque. **54 graffitis** : les gangs signent **chez eux** (voir « CRAVATES » sur un mur apprend au joueur chez qui il est, sans un mot de HUD — un juge vérifie qu'aucun nom de gang ne traîne hors de son territoire), les autres taguent ROCCO, ICITTE, PAS DE JOBS. ⚠️ **Deux règles portent tout le reste.** (1) Une devanture est une **couche peinte** : elle ne déplace aucune tuile et ne change aucune solidité (elle transforme des `F` en `W`, qui ont exactement la même) — un juge garde cette frontière, parce que la violer ferait tomber les juges de circulation trois fichiers plus loin. (2) Elle tire dans **son propre dé** : avec le dé commun, choisir un nom d'enseigne décalait toute la suite du hasard et déplaçait des arbres à l'autre bout de la ville (deux tests de banc sont tombés là-dessus). Le dessin vit dans le **morceau de décor**, cuit une fois : une rue commerçante ne coûte pas une image de plus — et une enseigne à cheval sur deux morceaux est rangée dans **les deux**, sinon le nom est coupé net au milieu d'un mot. Chaque devanture pose une **lueur de vitrine** (basse, courte, chaude) : sans elle tout ce travail disparaissait la moitié du temps de jeu. 25 juges Python + 5 de banc ; rythme **0,7 ms** par image de nuit à 5★ (0,6 avant), paquet **341 Ko bruts / 35 Ko gzip**. ⚠️ **On voit toujours une porte** (retour de Martin) : le bandeau, l'auvent et la vitrine couvraient toute la bande — on lisait le nom du commerce et on ne voyait plus par où entrer. La devanture porte donc `motifs`, une lettre par tuile, qui dit au peintre ce qu'il y a dessous : `W` vitrine, `D` porte qu'on ouvre, `d` condamnée, `G` garage, `P` porte **peinte**. Une porte garde toute sa hauteur (pas d'auvent ni de vitrine par-dessus), et **celle où l'on peut entrer se reconnaît de loin** : vitre claire, poignée dorée, rai de lumière au seuil — les autres sont sombres, planches en travers pour les condamnées. Un tiers des bandes n'avaient **aucune** ouverture (le bâtiment avait tiré « pas de porte ») : on en peint une (`P`) sur la tuile qui donne sur le trottoir, sans toucher au sol — elle ne promet donc rien qu'on ne tienne. 11 juges de plus, dont un qui vérifie que `D` correspond à une **vraie** porte du catalogue : peindre une poignée dorée sur un mur serait une promesse qu'on ne tient pas. 473 tests |
| Musique du menu | **livré** (13 sept. 2026) | demande de Martin (« s'il n'y en a pas je veux aussi une musique au menu d'accueil ») : il n'y en avait pas — `Mus` était resté l'ébauche de M7 (trois lignes). ⚠️ Le thème est **écrit en notes**, pas enregistré (`app/musique.py`) : un mp3 de menu pèserait plus que tout le paquet réuni, coûterait des crédits à générer et ne se **testerait** pas, alors que 2 Ko de notes se relisent, se corrigent à la note près et se jugent. *Baie-des-Brumes* : 92 bpm, la mineur, une grille de huit mesures qui tourne (Am7 Dm7 G7 Cmaj7 Fmaj7 Bm7b5 E7 Am7 — le tour de chant le plus banal du jazz, **et c'est voulu** : il doit tourner sous un menu sans jamais accrocher l'oreille), quatre voix (basse marchante, nappe, chant sur seize mesures qui ne se répètent pas, balai sur le contretemps), boucle de 42 s. `Mus` est maintenant un vrai séquenceur : il pose les notes sur **l'horloge audio** avec un quart de seconde d'avance, jamais sur les images — sinon un à-coup d'affichage troue la mesure. ⚠️ Il ne programme **rien** tant que le son n'est pas accordé (voir « Le son retenu ») : dans un contexte suspendu l'horloge est figée, et toute la boucle sortirait d'un bloc à la seconde où le joueur touche l'écran. 13 juges Python (aucune note hors du clavier, aucune qui déborde de son motif — elle ne jouerait **jamais**, aucun chevauchement dans une voix, volumes cumulés sous l'écrêtage, la boucle finit sur un la) + 7 de banc (le rythme tombe sur un multiple exact du pas, la boucle reboucle sur la même note, le menu se tait quand la partie commence). `scripts/musique_apercu.py` rend un morceau en WAV sans lancer le jeu : une note fausse s'entend là plutôt qu'en ligne. Paquet **322 Ko bruts / 32,5 Ko gzip** (+2 Ko) |
| Aucun son n'a jamais joué | **livré** (13 sept. 2026) | retour de Martin (« j'ai le son de la page titre, mais rien ensuite ») — et c'était bien pire que ça. Dans `echantillon()`, **`source.connect(gain)` manquait** : la source n'entrait dans aucune chaîne. Tout le reste était juste — le fichier se téléchargeait (200), se décodait (tampon de 0,68 s, pic 0,22), la source démarrait, le gain était au bon volume **et** relié au maître. Aucune erreur, aucun 404, aucune trace : **aucun des 79 fichiers ElevenLabs n'a jamais été entendu** — ni un bruitage, ni une voix, ni une radio, ni l'ambiance. ⚠️ Et le filet de synthèse ne prenait pas le relais, parce que `joue()` rend `true` dès que l'objet existe : ni échantillon, ni repli, **silence**. Deux pannes se masquaient l'une l'autre — le son retenu par le navigateur empêchait de découvrir celle-ci, et la musique du menu (de la **synthèse**, elle) l'a révélée en sonnant seule. ⚠️ Ce qui manquait, ce n'était pas un test de plus mais un test d'une autre **nature** : tous nos juges vérifiaient l'intention (fichiers servis, tampons décodés, sources démarrées, volumes justes) et tous étaient verts. Désormais on écoute la **sortie** : au banc, le faux AudioContext trace ses branchements et `atteintLaSortie(noeud)` exige un chemin jusqu'à la destination (3 juges, vérifiés en remettant le bug) ; au navigateur, un `AnalyserNode` posé sur la sortie mesure ce qui sort vraiment (3 juges : la synthèse, un échantillon, l'ambiance, le thème). Mesures après correctif : échantillon −35,7 dB (avant : **silence**), ambiance −25,8 dB, et l'écart menu/jeu retombe de **136 dB à 2,6 dB**. ⚠️ **La même soudure manquait une seconde fois**, dans `Voix.parler()` : retour de Martin (« je n'entends pas les voix des gens dans les dialogues »). Les 44 répliques se chargeaient, `enCours` se posait, la radio baissait, le texte défilait — et rien ne sortait ; un juge existant vérifiait même que la réplique « se décode et baisse la radio », et il était vert. D'où un juge d'une portée plus large que les deux cas connus : `ctx.sourcesMuettes()` au banc recense **toute** source qui a démarré sans atteindre la sortie, quel que soit le chemin — on fait sonner bruitages, boucles, musique, répliques (dont une au téléphone, qui a un filtre de plus) et on exige zéro. Les deux bugs ont été remis exprès pour vérifier que les juges tombent. ⚠️ Effet de bord découvert au passage : ouvrir un `AudioContext` dès le chargement (pour savoir si le son est accordé) en laisse un ouvert par page — le navigateur en limite le nombre, et la suite navigateur devenait instable ; `Son.fermer()` sur `pagehide` rend la carte son. Et `Son.estCharge(slug)` répond « ce son est-il prêt ? » sans le **jouer** : les attentes de test le faisaient en démarrant une source à chaque sondage, jusqu'à faire caler le contexte |
| Les filles de la Brume dans la foule | **livré** (13 sept. 2026) | retour de Martin (« on ne distingue plus les prostituées, elles sont trop pareilles que tout le monde ») : elles n'étaient qu'un **échange de palette** sur le corps commun — un chandail rose voisin de celui de la passante, des cheveux noirs comme la moitié du catalogue — et à **douze pixels de large**, sous la teinte de nuit, une couleur ne distingue rien. ⚠️ Ce qui se reconnaît à cette taille, c'est un **contour** : `SPRITES.racoleuse` est le **seul archétype de piéton à avoir son propre dessin** (jupe évasée **plus large que les épaules** — personne d'autre dans le jeu, jambes nues sous l'ourlet, talons, cheveux qui tombent de chaque côté du cou, blond platine que personne ne porte ; trois vues, trois images de marche, et la pose `couche` **sans laquelle un KO serait resté debout**). Rien de plus ne se montre : c'est une silhouette, pas une tenue. Deuxième signe, lu avant même la robe : elle **tient son coin** (`poste` à la naissance, rayon de 3 tuiles) — elle s'arrête deux fois plus souvent que les autres et revient vers son lampadaire, là où elle se remettait à flâner comme tout le monde dix secondes après être apparue ; ⚠️ une flânerie dure jusqu'à 330 images, alors elle **redécide toutes les 30** — sinon elle était à l'autre bout de la rue avant de seulement songer à revenir (mesuré : 56 px d'écart maximum en 40 s, contre 224 px pour une passante). Troisième signe, à bout de bras : l'invite ACTION la **nomme** (« LA BRUME — 60 $ ») — `interagir` la servait déjà mais `majInvite` l'avait oubliée, on appuyait sur ACTION en espérant que c'en était une ; une seule fonction (`filleSousLaMain`) sert les deux, pour que le HUD ne promette jamais autre chose que ce qui va se passer. 4 juges (le contour s'évase et le corps commun non, ses couleurs ne se recroisent nulle part dans le catalogue, elle tient son coin quand la passante s'en va, le HUD la nomme et se tait quand elle est partie) |
| Rien ne se chevauche plus | **livré** (13 sept. 2026) | retour de Martin, capture à l'appui (« empêche que les choses se chevauchent ») : le joueur **debout dans la carrosserie** du camion-restaurant. Deux chevauchements, deux causes. ⚠️ **Le décor** : la collision n'était pas absente, sa **forme** était fausse. Un camion-restaurant fait 44 px de large et 8 px de profond ; son unique cercle (r 16) tenait dans la profondeur, donc il laissait **6 px de carrosserie** libres de chaque côté — et le cercle qui aurait couvert la largeur (r 22) aurait posé un mur invisible de 22 px devant et derrière. Un cercle ne sait pas tenir un rectangle. Chaque décor carré porte maintenant une **boîte au sol** (`sol: [demi-largeur, demi-profondeur]`, mesurée sur les `fillRect` de son peintre) dont on ressort par le côté le moins enfoncé : banc, caisse, fontaine, les deux kiosques, la roulotte, le camion. L'arbre, lui, **garde son cercle** : son tronc fait 3 px et sa cime est peinte en hauteur — on passe sous une cime, pas dans un comptoir (même raison pour le parasol du kiosque à hot-dogs). ⚠️ **La foule** : personne ne poussait personne. Deux passants qui se croisaient se superposaient **exactement** — mesuré en marchant deux minutes : **1032 paires** enfoncées l'une dans l'autre en 960 images, jusqu'à **9,9 px**, soit deux corps de 10 px parfaitement confondus. `demeler()` sépare maintenant tout le monde à chaque image, sur un index **refait** (celui du début d'image est périmé : il laissait passer exactement les paires qui venaient de se rejoindre), en poussant par `deplacerCercle` — sinon on se pousse mutuellement **dans un mur**, ce qui est pire. Après : **0,1 px** au pire, dès la première image. ⚠️ Et l'on ne **naît** plus dans quelqu'un : les deux branches de `placeDeNaissance` rendent un **centre de tuile**, donc deux naissances sur la même tuile, c'est le même pixel (deux agents nés l'un dans l'autre à l'image 31). ⚠️ Le plafond de séparation doit passer **devant les jambes les plus rapides** : fixé à 1,5 px il arrêtait bien le joueur qui **marche** (1,2) et laissait passer celui qui **sprinte** (2,1) — il suffisait de tenir MAJ pour entrer dans le vendeur ; il se calcule désormais sur les vitesses du paquet. ⚠️ Et « figé » veut dire **il tient son poste**, pas **c'est un poteau** : vraiment immobile, un donneur planté sur le trottoir bouchait la rue **pour toujours** — l'agent lancé aux trousses du joueur venait buter sur Ti-Guy et y restait (260 images sur place, l'arrestation n'arrivait jamais). Il se laisse donc bousculer de 10 px et **rentre chez lui** ; au-delà il redevient un mur, sinon on promènerait un personnage d'histoire jusqu'au port. 6 juges (on ne se tient dans aucun décor par aucun des quatre côtés, la portée de recherche couvre le **coin** de la plus grosse boîte — sinon le camion n'est même pas trouvé et rien ne rougit —, la foule ne se chevauche plus et ne naît plus empilée, courir ne traverse pas les gens, le figé cède puis revient). Coût : **0,337 → 0,356 ms par image** à 5★ avec 1992 entités |
| La voix au téléphone qu'on n'entendait plus | **livré** (13 sept. 2026) | retour de Martin (« les voix au téléphone ne sont pas assez forte ») : ce n'était pas une question de **volume** mais de **filtre**. Le combiné était un seul `bandpass` à 1,5 kHz (Q 1,2) — bien plus pincé qu'un vrai téléphone, 6 dB par octave de chaque côté. Or c'est **sous 900 Hz** que la parole porte le gros de sa puissance : mesuré, la voix au combiné sortait à **−6,5 dB à 500 Hz** et **−11 dB à 300 Hz**, donc **plus bas qu'en direct**, et les 1,6× de compensation étaient loin du compte. C'est maintenant la **vraie bande téléphonique** (300 Hz – 3,4 kHz), dessinée par un passe-haut puis un passe-bas qui laissent **plat** tout ce qu'il y a entre — et 2× de compensation, parce qu'une voix coupée de ses graves s'entend moins fort à puissance égale et qu'un appel se prend au milieu des moteurs. Après : **+8,1 dB à 500 Hz, +7,6 dB à 1 kHz, +7,7 dB à 3 kHz** — de +4 à +18 dB selon la fréquence, et le combiné passe **au-dessus** de la voix en direct sur toute la bande de la parole. ⚠️ Encore un test d'une autre **nature** : les juges existants vérifiaient que la réplique au téléphone **atteint la sortie** (elle l'atteignait, la chaîne était branchée, la source démarrait) — atteindre la sortie ne dit rien de ce qui **en sort**. Les 2 nouveaux ne lisent pas les réglages, ils **calculent** la réponse réelle de la chaîne (formules RBJ, celles que le Web Audio implémente) en suivant les branchements du gain jusqu'au maître : le combiné doit sortir au-dessus du direct sur toute la bande de la parole, et cette bande doit rester plate à 6 dB près. Remis l'ancien filtre, ils tombent (12,7 dB d'écart : « le combiné pince trop ») |
| Manger, boire, courir | **livré** (13 sept. 2026) | demande de Martin (« il faut que la bouffe redonne de l'énergie et le café permet de courir plus longtemps ») : un kiosque ne rendait que des **PV**, et le souffle (`endurance`, 100 points, 0,4 par image au sprint) ne se refaisait **qu'en arrêtant de courir** — autrement dit, les quatre commerces de trottoir ne servaient à rien à la seule minute où l'on en a besoin, celle où la police est derrière. Manger rend maintenant les deux (`*_souffle` dans `economie.TARIFS` : hot-dog +40, poutine +70, café +30), et ce qui coûte plus cher nourrit plus, en vie **comme en jambes**. ⚠️ **Le café n'achète que de la DURÉE.** Pendant 90 s (`economie.CAFE`) le sprint ne coûte que la **moitié** : 4,2 s de course d'une traite deviennent 8,4 s. Sa vitesse, elle, ne bouge pas d'un pixel — les 2,1 du sprint contre 1,9 au policier et 1,35 au fuyard sont ce qui rend une poursuite **gagnable des deux côtés** ; y toucher pour 4 $ aurait cassé toutes les poursuites du jeu d'un coup, alors un juge mesure la distance par image sous café et la refuse si elle change. ⚠️ C'est une **minuterie, pas une dépense** : elle s'écoule dans `Missions.maj` (donc aussi au volant et dans une pièce, là où `majJoueur` ne passe pas), elle ne s'**empile** pas (un deuxième café repart le compte — sinon on s'achète l'endurance infinie à 4 $) et elle ne survit ni à la nuit ni à l'hôpital. ⚠️ Et elle **se voit** : la barre d'endurance passe au vert et clignote la dernière seconde, parce qu'un souffle long qui s'arrête au milieu d'une fuite sans rien annoncer se lit comme une panne. Le **casse-croûte sert le café** lui aussi : la roulotte du trottoir ferme de 14 h 24 à 4 h 48 et elle était le seul endroit du jeu où courir plus longtemps s'achetait. 4 juges Python (la bouffe rend du souffle sans faire déborder la barre, la poutine vaut son prix, le café n'achète que de la durée et dure plus qu'un plein de souffle, seul le café réveille) + 2 de banc (manger remonte le souffle et ne déborde pas, un hot-dog ne réveille pas ; sous café on tient **deux fois plus d'images à la même vitesse**) |
| Des commerces, du monde qui habite, des vrais intérieurs | **livré** (13 sept. 2026) | demande de Martin (« beaucoup plus de variété de commerce ou bien enlever certaines devantures pour remplacer par des résidences ; ajouter des appartements à étage ; améliorer les intérieurs, car présentement il n'y a jamais rien, seulement des comptoirs vides ; ajoute aussi des intérieurs pour plusieurs types ; valide les missions qui doivent avoir des choses à l'intérieur ») : **142 noms d'enseigne** au lieu de 56 (14 à 48 par quartier) et **trois familles de plus** (santé, mode, savoir) ; `choisir_enseigne` refuse le même nom à moins de **40 tuiles** — La Shop affichait sept fois « FERRAILLE ». **74 immeubles à logements** remplacent 20 devantures et habillent les quartiers d'habitation : une couche peinte comme les enseignes (zéro solidité touchée), **1 à 3 étages** de fenêtres, balcon, **escalier de fer** sur le trottoir, et une fenêtre sur trois allumée la nuit. Les **29 intérieurs** sont maintenant **dessinés à la main** (un plan par pièce, l'espace = le plancher) avec **onze meubles** (comptoir, étagère, table, chaise, lit, frigo, machine, plante, classeur, poêle, escalier) et **trois planchers** (bois, céramique, tapis) — et du **monde dedans** : un commis à son poste, des clients tirés dans les passants du quartier. **Un commerce ordinaire sur cinq s'ouvre pour de vrai** (42 portes au lieu de 16) : dix pièces génériques, une par famille de devanture, et le **nom de l'enseigne voyage sur la porte** — on entre chez « TABAGIE DUBOIS », pas dans « Boutique ». Nouveaux comptoirs : `emplettes` (`magasins.COMPTOIRS`, data), `salon` (le barbier change tes cheveux **et fait oublier ta tête à la police**), `escalier` (l'étage du plex et la chambre de l'hôtel), `fouiller` (les tiroirs d'un logement, une fois par adresse), `casier` (le carnet du poste). ⚠️ **Trois comptoirs étaient morts** (`guichet`, `sortie_prison`, `casier` : un libellé, aucun menu, « PLUS TARD ») — un juge du banc compare maintenant ce que `carte.INTERIEURS` dessine à ce que `missions.js` sert, et seul le comptoir de la fourrière reste en chantier (il appartient à M9). ⚠️ **Un meuble ne remplit pas sa tuile** : sans plancher peint dessous, chaque table était un trou **noir** — `plancher` voyage donc avec la pièce. **125 juges de plus** (`test_interieurs.py`, `test_interieurs_js.py`, et les logements dans `test_devantures.py`) |
| Les transitions des portes | **livré** (13 sept. 2026) | retour de Martin (« la transition n'est pas juste ») : elle ne l'était pas parce qu'elle arrivait **dans le mauvais ordre** — `entrer()` chargeait la pièce, *puis* lançait le fondu, dont la première moitié noircissait donc sur la scène déjà changée. Ce n'était pas un fondu enchaîné, c'était un clignotement. `Jeu.transiter()` remet l'ordre : **noircir sur l'ancienne → changer au noir → éclaircir sur la nouvelle**, le jeu **figé** pendant (un char ne te renverse plus sur un écran noir), des durées **asymétriques** (entrer 46 images, sortir 26), la caméra posée au noir sur la cible que l'amorti viserait, la porte qui s'entend au noir, et un reste d'élan au pas de la porte. 3 juges de banc : la scène mesurée **à chaque image**, le gel (ni temps, ni passant, ni char), et sortir **pendant** le fondu d'entrée |
| Les clôtures : grillage, bois, barbelé | **livré** (13 sept. 2026) | demande de Martin (« il faut des clôtures, mais si elles ne sont pas barbelées, qu'on puisse passer par-dessus », puis « ajoute aussi des clôtures de bois pour la variété ») : on passait par-dessus **toutes** les clôtures — sans même ralentir, parce que `f` était solide 3 et que le masque des piétons ne la voyait pas. Elles ont maintenant leur solidité à elles : **4 s'enjambe** (grillage, palissade de bois — 48 images en haut, immobile, sans frapper ni courir), **5 ne se passe pas** (barbelé). Franchir est une capacité de **tout le monde**, au même prix : l'A\* des agents traverse le grillage à 5 tuiles de coût et l'agent l'enjambe pour de vrai — une poursuite ne se gagne pas en escaladant. Du barbelé dans les cours de gang et de La Shop, du grillage à la fourrière (décision) et sur les terrains vagues, **de la palissade de bois dans les cours arrière des Érables** (188 tuiles). 6 juges neufs |
| Enfermé dans six commerces | **livré** (13 sept. 2026) | bug de Martin (« chez Ti-Paul, impossible de sortir ») : `utiliserPoint` passait **avant** la porte et attrape tout point à 1,6 tuile — or il n'y a qu'une tuile d'où sortir, et il rend `true` même quand il n'a qu'un « PLUS TARD » à dire. **Deux corrections, et il fallait les deux** : la porte passe maintenant avant le comptoir (un comptoir se sert d'un pas de côté, une porte non), et un **juge Python** interdit tout point d'action à moins de `RAYON_POINT` (1,6 tuile) de la tuile de sortie — il rougissait six fois le jour où il a été écrit. Les six pièces se sont redessinées (le comptoir recule, le journal du dépanneur s'en va contre son mur). 3 juges neufs, dont un qui **remet le piège à la main** |
| Clôtures nord-sud couchées | **livré** (13 sept. 2026) | bug de Martin : les trois peintres ne dessinaient que l'est-ouest, donc une clôture verticale était une pile de panneaux vus de face. Elles lisent maintenant leurs voisines (`varianteDeCloture` : un masque des quatre côtés où la clôture continue) et se peignent en **bras** — le même code pour les trois, avec les deux axes échangés en nord-sud, un poteau au centre à chaque coin et à chaque bout. Le juge compare les **deux cuissons trait par trait** : le nord-sud doit être l'est-ouest tourné |
| La carte | **livré** (13 sept. 2026) | demande de Martin (« un icône clignotant pour savoir où on est, une légende, savoir où est la mission en cours ») : le joueur **était** dessiné — un carré blanc de 2 px, lisible sur le Faubourg de 157×112 et perdu depuis que la ville fait 421×213. Il **pulse** maintenant (un anneau qui s'ouvre et se referme, 40 images) et ne disparaît **jamais** — on ne cache pas ce qu'on cherche ; l'objectif bat à un autre rythme (16) et dans une autre forme (un losange doré). Hors du cadre de la mini-carte, il devient une **flèche** au lieu d'une position bornée au coin, qui mentait. Et la **légende** se construit depuis la table des couleurs, descendue de Python (`FAMILLES_DE_LIEU`, 8 familles) : les seize lieux ont tous une couleur **déclarée**, là où `COULEUR_BLIP` en connaissait dix et laissait six au gris. 4 juges neufs |
| Les donneurs qu'on ne voyait pas | **livré** (13 sept. 2026) | bug de Martin (« je n'arrive pas à faire la mission sergent Bouchard, je vais à la cantine, mais je ne vois pas quoi faire ») — et il avait raison deux fois. D'abord le **nom** : Marco l'envoie au « casse-croûte » (le Faubourg, à côté du poste), pas à la **Cantine des Quais**, un autre bâtiment à l'autre bout de la ville. Ensuite, et c'est le vrai bug : **Bouchard et Josée n'existaient nulle part**. Ce sont les deux seuls donneurs qui se tiennent DEDANS (`ou: point:sergent`, `point:contact`), et `creerDonneurs()` ne posait que ceux de la rue (`porte:`) : on poussait la porte, la salle était vide, et il fallait deviner qu'un **point invisible** attendait au fond à droite. Ils sont maintenant **posés en entrant** (`creerDonneursDedans`, appelée par `Jeu.entrer` juste après le commis et les clients), ils naissent et meurent avec la pièce comme tout le monde, et la table Python→piece ne se recopie plus en JS : `personnageDuPoint` / `pieceDuPoint` la **déduisent** du `ou` de `missions.py`. ⚠️ Josée pointe une **table** (personne ne se tient debout sur une table) : `placeDebout` prend la tuile libre voisine la plus proche du milieu de la pièce — le fond d'un coin, ce n'est pas une scène. ⚠️ Le GPS a fallu le corriger du même coup (`ouTrouver`) : dedans, un donneur vit en coordonnées de **pièce**, et le poser tel quel sur la minicarte envoyait la flèche à six tuiles du coin de la ville. Et une **bulle de bande dessinée** dit qui attend après toi — voir la ligne suivante. ACTION dedans vise maintenant **la personne avant le comptoir**, et le HUD la nomme (« PARLER À SERGENT BOUCHARD ») | 2 juges de banc (on entre, quelqu'un est là, debout hors des meubles, à portée de son point, et il parle ; il ne suit pas dans la rue) |
| Les bulles qui interpellent | **livré** (13 sept. 2026) | demande de Martin (« avec une petite bulle de type bande dessiné qui nous interpelle ») : le jeu avait déjà deux pastilles de 8 px au-dessus des têtes — le « ! » du témoin, le trait de la peur (`cri`). Elles disent un **état d'esprit** ; elles ne peuvent pas dire un **mot**, et c'est le mot qui manquait. `Entites.bulle(e, texte, {duree, fond, encre})` pose une boîte à queue au-dessus de **n'importe quelle entité** (police 3x5, coins coupés, la queue sur la tête de celui qui parle, une montée de 6 images puis une respiration), `Entites.taire(e)` l'efface, et elle se dessine dans une **deuxième passe**, après tout le monde : dans une pièce, un client passe devant le donneur une fois sur deux, et une bulle à moitié cachée par une nuque ne se lit plus. ⚠️ Le texte **ne s'invente pas en JS** : `personnages[].heler` dans `missions.py`, comme toutes les répliques du jeu, court par force (`HELER_MAX`) et vérifié par un juge. ⚠️ Une bulle qui ne s'éteint jamais ne veut plus rien dire : elle ne s'allume que si **ce donneur-là** a une job pour toi (ou t'attend pour la finir), elle se tait pendant sa propre mission, et **aucune** bulle ne s'affiche pendant un dialogue — quelqu'un te parle déjà, en bas de l'écran. Deux emplois pour l'instant : les **cinq donneurs** et le **client du taxi** de M3, qui levait le bras au bord du trottoir sans rien dire | 1 juge Python (chaque donneur a son mot, assez court), 1 de banc (elle s'allume sur le bon donneur, s'éteint après, et vit d'une image à l'autre), 1 dans le taxi ; vérifié à l'écran dans un vrai navigateur (casse-croûte, bar, terminus) |
| Le souffle en surplus | **livré** (13 sept. 2026) | demande de Martin (« les choses qui donnent du souffle devraient donner un **bonus**, parce que le souffle monte seul ») : il remontait de 0,24 par image — une barre vide pleine en **7 s** — et `nourrir` plafonnait à 100, donc une poutine à 18 $ rendait 70 points qu'on avait gratuitement en s'arrêtant quatre secondes. Manger ajoute maintenant **par-dessus** les 100 (plafond 60) : le surplus **part en premier** au sprint, ne remonte **jamais** tout seul, et se perd en dormant, à l'hôpital et en prison. À l'écran, une ligne cyan d'un pixel **posée sur** la barre — elle garde sa couleur sous café (barre verte) et **disparaît au volant**, où la barre montre la carrosserie. Son plafond est un réglage de **poursuite** : 60 points = 2,5 s de sprint de plus, 5 s sous café, et un juge refait le calcul. 2 juges neufs |
| Les toits | **livré** (13 sept. 2026) | demande de Martin (« je veux que les toits soient plus réalistes ») : ils étaient peints **tuile par tuile**, chacune ignorant les autres — une texture, pas un toit. Ils ont maintenant un **bord** (parapet clair + ligne d'ombre, lu dans le voisinage comme les passages piétons), un **grain** qui varie de tuile en tuile, une **couverture par genre** (`COUVERTURES` : deux versants en banlieue, tôle et gravier à La Shop, ardoise en ville) que **deux voisins collés ne partagent jamais** (sans quoi il n'y a pas de bord à trouver entre eux), des **versants** avec leur ligne de faîte — comptés dans les voisines, zéro donnée de plus —, **172 équipements** (ventilation, climatisation, cheminée, cage d'escalier, réservoir, antennes) qui voyagent dans le paquet comme les enseignes, et une **ombre portée** sur la rue qui donne d'un coup de la hauteur à la ville. 4 juges neufs ; paquet à 368 Ko bruts / 41 Ko gzip |
| Le fondu de l'hôpital et de la prison | **livré** (13 sept. 2026) | demande de Martin (« il faut corriger le fade out et in quand on va à l'hôpital ou qu'on se fait enfermer ») : quatre changements de scène — l'hôpital, la prison, la compagnie, le coucher — étaient restés sur `Hud.fondu` + `setTimeoutJeu`, soit **deux horloges** que rien ne liait : l'une comptait dans le dessin, l'autre dans la mise à jour. On se regardait donc disparaître de la rue à **80 % de noir**, le texte se lisait par-dessus le trottoir où l'on venait de tomber, et la ville continuait de tourner pendant les deux secondes et demie — un char pouvait repasser sur un joueur à 1 PV. Les quatre passent maintenant par la machine des portes, `Jeu.transiter()`, qui n'a **qu'une** horloge et change la scène **pile** à alpha 1. Elle gagne pour eux un troisième nombre, `[fermer, tenir, ouvrir]` : une porte, on la passe ; une nuit, un séjour à l'hôpital **font passer du temps**, et ce temps se sent dans le noir tenu, où le texte s'écrit — et **seulement** là. `Hud.fondu`, `setTimeoutJeu` et leurs minuteries sont supprimés : plus une seule deuxième horloge dans le jeu |
| Des sirènes qu'on entend | **livré** (13 sept. 2026) | demande de Martin (« je veux des sirènes pour les ambulances et polices ») : il n'y en avait **qu'une**, et presque jamais — `Son.boucle('sirene', …)` ne s'allumait que pour une auto-patrouille de l'IA en chasse, à volume fixe, sans distance. L'ambulance déclare pourtant `sirene: true` depuis M9 et n'en a **jamais** fait entendre une seule ; au volant, aucune des deux. Maintenant : **deux sons** (celle de la police monte et descend, celle de l'ambulance fait deux notes — les confondre, c'est ne pas savoir qui arrive derrière soi), un **volume qui suit la distance** (460 px de portée), une **ambulance sur trois** qui naît en course dans le trafic, et au volant d'un char à sirène le **bouton du klaxon devient celui de la sirène** — l'étiquette du bouton tactile le dit |
| M9 Le parc et les boulots | **P1** ajout, **aux deux tiers** (13 sept. 2026) | ⚠️ Le Python était commité et **le JS n'existait pas** : quatre chars de phase 1 vivaient dans le paquet, se tiraient au trafic et se revendaient au garage, mais **rien ne les dessinait** — et aucun test ne le disait, alors que le prologue de `vehicules.py` le promettait. **Livré** : les quatre sprites (camion, autobus, ambulance, remorqueuse), le juge manquant (« tout char de phase 1 a son sprite »), et la **chaîne de cercles lue dans la fiche** — elle valait 3 pour tout le monde, donc une moto entrait dans l'autobus par le milieu. Et **un vélo ne saute plus** : il n'a pas de réservoir, donc il se **plie** — pas de feu, pas de fumée, pas de secousse, aucun délit. **Reste** : `defonce`, `soigne`, `crochet`, les boulots au klaxon, la fourrière, la radio procédurale, le sport et le luxe |
| Rampes vraiment prenables | **P1** **correctif** à faire | demande de Martin : `ELAN` et `RECEPTION` sont des nombres de tuiles, alors que la portée d'un saut est **quadratique en vitesse**. La moto vole **126 px** pour 96 px de réception exigée — et c'est le char du *Grand Saut*. Il manque aussi le **freinage** (75 px de plus) |
| Un saut qu'on ne voit pas | **P1** **correctif** à faire | bug de Martin (« les rampes n'ont pas l'air de fonctionner »). ⚠️ Elles fonctionnent : le saut mesure **7,8 px** pour une berline (2,0 px pour un vélo) et dure **0,3 s**, sur des tuiles de 16 px. Et l'ombre est un rectangle **fixe** de 20 × 10 qui ne rétrécit ni ne s'éloigne — elle ne raconte aucune hauteur |
| L'endurance du Faubourg | **P2** **correctif** à faire | demande de Martin : la course doit être **gratuite**, le sprint seul coûte. ⚠️ Mesuré : un souffle vaut **4,2 s** (33 tuiles) sur une ville de **421**, et la vitesse soutenable (1,54) est **sous** celle du policier (1,9). Trois vitesses, et le policier remonte à la course — sinon on s'échappe à pied pour toujours |
| Étoiles de recherche illisibles | **P2** **correctif** à faire | demande de Martin : plus grosses, jaunes, au centre. ⚠️ Ce sont des `★` de texte à l'échelle **1** dans un coin, sous un montant d'argent à l'échelle **2** — la chose la plus importante d'une poursuite est le plus petit élément de l'écran |
| Clôture nord-sud trop large | **P2** **correctif** à faire | demande de Martin : elles ont été redressées **par une rotation**, donc le nord-sud est un panneau de 7 px vu à plat. Vue d'en haut, une clôture nord-sud se voit **par la tranche** — la règle est déjà écrite pour les façades et les meubles. ⚠️ Le juge actuel exige la rotation : il verrouille le défaut |
| La nuit ne se vide pas | **P2** **correctif** à faire | demande de Martin. ⚠️ Le rythme de nuit existe depuis M8 mais ne fait presque rien : le Faubourg garde **9 véhicules sur 9** (12 × 0,75 = 9, pile le plafond) et **19 piétons sur 26**. Le plafond s'applique **après** le rythme au lieu d'avant, et la police n'en suit aucun |
| Arbres dans les sentiers | **P2** **correctif** à faire | demande de Martin : `_parc()` sème arbres, bancs et buissons sur tout le rectangle, et une allée n'est ni solide ni routière — rien ne la protège. Or un arbre est **solide** : il barre le sentier qu'on a dessiné pour y passer |
| Le carnet | **P2** ajout à faire | demande de Martin : un rappel de la mission en cours, un journal de ce qui s'est passé, et un répertoire des personnages **rencontrés** — au menu Pause. ⚠️ « Journal » est déjà pris deux fois (Le Clairon, le carnet du poste de M11) |
| Une seule musique pour toute la ville | **P2** ajout à faire | demande de Martin : une ambiance **par district**, un vrai enregistrement pour le titre (le thème en notes devient le filet, comme `musique.py` l'avait prévu), et des musiques d'**état** — poursuite à partir de 2★, bagarre de gang. ⚠️ Huit pistes = ~4 Mo : chargement paresseux obligatoire, et une échelle de priorité à écrire |
| Trottoir et traverses de deux tuiles | **P3** **correctif** à faire | demande de Martin : `TROTTOIR = 2` construit chaque rue **et la profondeur des passages piétons** — une seule constante pour les deux. Le passer à 1 demande de rétrécir les rues de deux tuiles (sinon elles gagnent deux voies), de reloger lampadaires, bornes, kiosques et la réserve devant les portes, de trancher sur la foule, et ⚠️ de sortir le **2 écrit en dur** dans `monde.js` |
| Pièces plus grandes que leur maison | **P3** **correctif** à faire | demande de Martin, mesurée : **les 41 intérieurs** dépassent l'empreinte de leur bâtiment — un logement de banlieue de 3 × 3 ouvre sur une pièce de 16 × 9. Une porte doit imposer une taille minimale au bâtiment, et il faut de **petites** pièces |
| L'eau n'est plus un mur | **P3** **correctif** à faire | demande de Martin : l'eau bloque tout (`MASQUE_PIETON` la compte comme un mur) — il faut pouvoir y nager, s'y noyer à bout de souffle, et y couler en char. ⚠️ Le juge du pont de M8 se reformule : seul lien **carrossable** |
| Feux pour piétons | **P4** ajout à faire | demande de Martin : la règle existe (on traverse quand les chars ne sont pas au vert) mais **rien ne la montre**. ⚠️ Et elle se trompe d'un temps : `!feuVert()` est vrai pendant **l'orange**, donc les piétons s'engagent quand les chars accélèrent pour vider le croisement |
| Les terrains de banlieue | **P4** ajout à faire | demande de Martin : `_jardin()` ne pose que du gazon et un arbre par dix tuiles. Entrée de voiture **en case de stationnement** (donc l'auto s'y gare toute seule), sentier de la porte à la rue, piscine en eau basse, grillage entre les cours, cabanon, corde à linge |
| Les armes à feu | **P4** ajout à faire | demande de Martin : il n'y en a que **deux** (pistolet, fusil à pompe) sur dix armes — une mitraillette (automatique), une carabine (longue, plafonnée à la largeur de l'écran) et un cocktail Molotov (en cloche, flaque de feu), vendus au marché noir |
| M15 La ville te parle | **P4** ajout à faire (v2) | le journal du matin t'apprend à jouer, la radio parle (animateur, pubs, bulletin), et les passants disent **plus de choses, moins souvent, et jamais une des quatre dernières** (8 répliques aujourd'hui, tirées sans mémoire) |
| M11 La police apprend | **P4** ajout à faire (v2) | carnet du poste (le casier se voit de loin), le stool, l'avocat du Carré, bouclier humain |
| M10 L'argent sale | **P4** ajout à faire (v2) | le shylock et la dette de Rocco, guichets au camion, skimmers, assurance et fraude |
| M12 La ville vit | **P4** ajout à faire (v2) | tramway, traversier à l'heure, tempête de neige et charrue, **le chantier** et les nids-de-poule |
| M14 Meta v2 | **P4** ajout à faire (v2) | **un compte et une base de données** (la partie voyage du téléphone à l'ordi), défi du jour à graine serveur (reporté de M7), mode photo, coop locale |
| M13 Les deux fins | **P4** ajout à faire (v2) | une mission par district, Marco qui te vend, Dr Lachance donneur, *Le Boss* et *Sacrer son camp* |

## Dettes

⚠️ Ce qui est **sciemment pas fait**. Ça vivait éparpillé dans les notes de jalons, là où on
ne relit jamais — et une dette qu'on ne relit pas devient un oubli. Chacune porte donc son
**déclencheur** : la chose qui dit qu'il est temps de la payer. Une dette sans déclencheur
est un oubli avec du style.

| Dette | Pourquoi pas fait | Déclencheur |
|---|---|---|
| Les radios **10-4** et **Radio-Traversier** sont déclarées mais jamais générées ni écoutées | ElevenLabs Music se paie à la seconde, et M8 avait déjà de quoi écouter | La prochaine séance avec la clé : `uv run python scripts/audio_elevenlabs.py --refaire dix_quatre traversier` — puis **les écouter**, un fichier qui se décode n'est pas un fichier qui sonne bien |
| Le **rythme mesuré sur le vrai téléphone** de Martin (reporté de M7) | Les chiffres du banc (0,29 ms/image de nuit à 5★) sont ceux d'une machine de développement | Avant M12 : la neige touche à la physique **et** au rendu, c'est là que le budget casse |
| Le **découpage du paquet** (`/api/carte`, ETag, districts chargés autour du joueur) | 33 Ko gzip aujourd'hui : le découper maintenant coûterait de la complexité pour rien | Écrit d'avance depuis M8 : **plus de 2 s entre « Jouer » et la ville** sur le téléphone de Martin |
| Le **bateau** reste en phase 2 (sans sprite, hors trafic) | Physique à part, tuiles d'eau carrossables, un quai où embarquer — il coûte plus qu'il ne donne aujourd'hui | Si le **traversier de M12** ne suffit pas à donner envie de l'eau. Sinon il tombe en v3, et la fiche le dit |
| `SECRET_KEY` vaut encore `cle-de-developpement-a-changer` par défaut | Sans compte ni session, une clé faible ne protège rien | **M14** : le jour où une session vaut une partie. `installer.sh` devra la générer et refuser de démarrer sans elle |

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
uv run python run.py          # http://127.0.0.1:5400
```

Les sons manquants se regénèrent par le serveur MCP `elevenlabs` (clé dans
`~/.mcp-servers/elevenlabs/cle.txt`) :

```bash
uv run python scripts/audio_elevenlabs.py --essai       # ce qui serait généré
uv run python scripts/audio_elevenlabs.py               # génère les bruitages qui manquent
uv run python scripts/audio_elevenlabs.py --radios      # … et les stations de radio (musique : cher)
uv run python scripts/audio_elevenlabs.py --voix        # … et les voix (passants + histoire, au caractère)
uv run python scripts/audio_elevenlabs.py --refaire coup pas la_brume ti_guy-m1-1
```

La musique, elle, ne se génère pas : elle s'écrit en notes dans `app/musique.py`
et se rend en WAV pour l'oreille, gratuitement et hors ligne :

```bash
uv run python scripts/musique_apercu.py                       # le thème du menu
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
débarques en autobus avec 50 $. Deux fins **v2** : *Le Boss* (posséder les 4 propriétés,
libérer 4 districts) ou *Sacrer son camp* (15 000 $ en poche, traversier de nuit à 0 étoile).

**Districts** (M8) : Le Faubourg (centre, gang Les Cravates) · Les Quais (port, Les Morues)
· Les Érables (banlieue, Les Chevreuils) · La Shop (industriel, Les Boulonneux) · La Pointe
(parc au bout d'un pont, Les Skateux), autour de **la baie**. Journal : *Le Clairon de la
Baie*. Radios : *La Brume* (jazz, auto), *Taxi-Radio* (country), *Le Choc* (techno, moto),
*10-4* (ondes du poste, auto-patrouille), *Radio-Traversier* (rigodon, camion) ; l'autobus
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
(kiosque à hot-dogs, kiosque à journaux, roulotte à café, camion-restaurant) sont posés par
le générateur sur les trottoirs et les stationnements, avec un marchand derrière.

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
  voix québécoises à son compte le 13 sept. ; distribution proposée : Ti-Guy = *Felix
  Tabarnak* (l'homme de tous les jours), Sgt Bouchard = *Khaivan* (accent bien dialectal),
  Mme Thibodeau = *Julia* (courtoise, chaleureuse), Josée « La Chef » = *Jeanne Mance*,
  Dr Lachance = *Patrick* (clair, ancien journaliste), Marco « Le Cousin » = *Québec
  Tremblay*, le narrateur du Clairon = *annonceur centre d'achat 1* (vieil homme qui
  soupire), les passants = *Felix* et *Amélie* (déjà en place). Une ligne à changer par
  personnage.
- **La réplique est la source** : `missions.py` porte `{"qui": "ti_guy", "texte": "…"}` ;
  le slug du fichier se déduit (`voix-ti_guy-m1-03.mp3`), la recette est donc le texte
  lui-même. `scripts/audio_elevenlabs.py --voix` génère ce qui manque, au caractère (≈ 40
  répliques × 80 caractères : quelques milliers de caractères, rien).
- **Le texte reste affiché** dans la boîte de dialogue (lisibilité, jeu en sourdine,
  tactile) ; la voix **s'ajoute**, elle ne remplace pas. Une réplique dont le fichier
  manque s'affiche sans voix — le filet, comme pour les bruitages.
- **Une seule voix à la fois** : une réplique coupe la précédente ; la radio et l'ambiance
  baissent pendant qu'on parle (*ducking*), puis remontent.
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
| `armes.py` | poings + 7 armes : dégâts, portée, cadence, chargeur, prix, `etoiles_usage` | première = poings à 0 $, prix croissants |
| `economie.py` | `ARGENT_DEPART`, `amende(etoiles, casier)` = `min(argent, base[★] × (1 + 0,5 × casier))`, pots-de-vin `40 × ★ × (1 + 0,5 × casier)`, hôpital `clamp(10 %, 30, 500)`, propriétés, `FORTUNE_MAX`, ce que la bouffe rend (`*_pv` et `*_souffle`) et `CAFE` (durée + dépense du sprint) | jamais négatif, monotone, plafonné, retour sur investissement 10–60 min, coordonnées sur une porte, le café n'achète que de la **durée** et dure plus qu'un plein de souffle |
| `recherche.py` | paliers 0–5 (agents, autos, barrages, tirent, décroissance 15/25/40/60/90 s), délits → ★ (taxonomie ci-dessous), cônes (à pied 90° 9 tuiles jour / 6 nuit ; auto 60° 14/12 ; témoin 120° 6/4 ; alarme rayon 12) | contigus, monotones, palier 0 sans réponse |
| `carte.py` | **plan compact** du district (grille de blocs 8×6 : `h` habitations, `c` commerces, `g` gang, `p` parc, `o` place, `q` quai, `~` eau, majuscules = bâtiment spécial garanti, `<` et `^` = bloc **avalé** par son voisin) + `COLONNES`/`RANGEES`/`RUES_V`/`RUES_H` (aucune égale à sa voisine) ; `generer(plan, graine)` produit tuiles (`sol`, `voie` = champ de direction + lignes d'arrêt), intersections (avec leurs bras), portes, lampes, décor, zones, apparitions ; intérieurs en ASCII. **Trois sources d'irrégularité** : la trame, les superblocs (une rue qui n'existe pas → des T), et le découpage BSP en parcelles inégales (bâtiments en U ou en L, dents creuses, terrains vagues, stationnements). Un **stationnement est dessiné**, pas rayé au hasard : des rangées de cases de 1 × 2 tuiles (le gabarit exact de l'auto, glyphes `^ v < >` = où pointe le **nez**), des allées de manœuvre — toute rangée en touche une —, des rangées **dos à dos** dès qu'il y a douze tuiles de creux, des îlots de béton (`I`) et un lampadaire au bout des rangées. Un **filet** bouche les poches injoignables au lieu de livrer un îlot muré. Deux **couches peintes** par-dessus, qui ne touchent à aucune solidité : les **devantures** (bandeau, nom, vitrines, pancarte) et les **résidences** (étages de fenêtres, balcon, escalier de fer) — `_a_quoi_sert()` décide, par bâtiment, commerce ou logement. Les **intérieurs sont dessinés à la main** (`_piece`, un plan par pièce, l'espace = le plancher, meubles en glyphes) et **jugés à l'import** : une porte, un plancher d'un seul tenant, des points atteignables | rectangulaire, glyphes connus, **connexité forte des voies** (BFS), un seul îlot marchable **sur cinq graines**, portes ⇔ intérieurs, aucun gabarit sur une rue **qui existe**, un superbloc avale bien sa rue, **toute rangée de stationnement touche une allée** et toute case fait deux tuiles de creux, **juge d'asymétrie**, déterministe |
| `missions.py` | 5 missions v1 + 3 défis : donneur, prérequis, objectifs typés (aller, monter, livrer, tuer, survivre, course, chrono, retourner), récompense, dialogues | prérequis sans cycle, cibles sur tuile marchable, références existantes |
| `pietons.py` | 8 archétypes (couleurs = échanges de palette, `courage`, `temoin`, bourse, arme), les gangs et leur territoire, `REACTIONS` (recul, KO, fuite, saignement, pickpocket) | couleurs valides, courage de 0 à 1, un gang a un territoire qui existe, aucun membre de gang au hasard dans la rue |
| `magasins.py` | inventaires armurerie / vêtements / garage ; les ambulants : ce qu'on y achète, les PV et le **souffle** rendus, l'`effet` qui dure (`EFFETS`) | articles existants, tout ce qui se mange nourrit les jambes, un `effet` que le navigateur sait tenir, seul le café réveille |
| `audio.py` | catalogue des sons : slug, **prompt ElevenLabs** (la recette reste à côté du son), durée, boucle, volume, variantes ; `exporter()` ne déclare que les fichiers **présents** | bornes ElevenLabs, aucun orphelin, poids < 600 Ko, chaque effet garde son repli synthétisé |
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
| 4 | `entree.js` | trois sacs d'entrées fusionnés par action (clavier `MAP_TOUCHES` AZERTY+QWERTY, manette `MAP_MANETTE` avec zone morte radiale et gâchettes analogiques, tactile `#croix` joystick suivi du pouce + boutons DOM 74/66/54/44 px), `contexte('pied'|'vehicule'|'menu')`, `empecherZoom()`, vibration |
| 5 | `son.js` | échantillons réels (fetch + `decodeAudioData`, variantes tirées au hasard, boucles allumables) **avec repli synthétisé** (`ton`, `bruit`), `SFX`, `Mus` séquenceur 3 voix (Loren) |
| 6 | `monde.js` | carte active depuis le paquet, `solide()` (masques : mur, eau, basse, **clôture**, **barbelé**), `ligneLibre()` (DDA), A* à budget (2/image, cap 800 nœuds, file, repli ligne droite, **une clôture se paie 5 tuiles**), feux, cache de morceaux 256 px, caméra amortie avec avance, horloge jour-nuit, intérieurs (pile `B.exterieur`), mini-carte |
| 7 | `entites.js` | **enjamber une clôture** (capacité de tout le monde, au même prix), structure unique `{x, y, vx, vy, r, z, angle, face, etat, t, vie, sprite, swaps, …}`, **deux** index spatiaux 64 px (le décor ne bouge jamais : bâti une fois ; le reste rebâti à chaque image), cercle-vs-tuiles, piétons (flâne, figé, fuit, **témoin**, riposte, assommé, aveuglé, mort), gangs, bulle 300–520 px, armes de fortune semées, ramassages, particules, décalques, tri par y (les morts d'abord), **bulles de bande dessinée** (`bulle`/`taire`, un mot au-dessus de n'importe qui, dessinées en deuxième passe par-dessus tout le monde) |
| 8 | `combat.js` | arcs de mêlée (anticipation → actif → repos), coup fort, esquive, projectiles, fusil à plombs, fronde en cloche, extincteur, réactions, saignement, mort, sang (plafond 150 décalques), lâcher/ramasser, cycle d'armes, visée assistée |
| 9 | `vehicules.js` | physique arcade (accélération, friction, braquage selon vitesse, adhérence/dérive, frein à main), **chaîne de cercles** pour les collisions (tuiles, véhicules, piétons), sous-pas au-dessus de 3 px/image, monter/descendre/éjecter, trafic sur le champ de direction (regard devant, feux, choix de sortie **par la voie qui va dans son sens** — d'où le virage à gauche après le croisement —, ralentissement avant le coin, **déport dans la voie d'à côté** sur un boulevard pour dépasser ou contourner un piéton, déblocage par patience), dégâts/fumée/feu/explosion, rampes (`z`), alarmes, klaxon. Sprites : **un seul dessin** par char, 32 caps cuits par rotation |
| 10 | `police.js` | `signalerCrime()`, `voit()` (distance, cône, ligne de vue, budget 20 rayons/image), rapports de témoins, machine de recherche (`chaleur`, ★, `vu`, décroissance), apparition par palier, patrouille/poursuite (A*)/arrestation, autos de poursuite, barrages, hélico, sergent ami, affiches, prison et hôpital |
| 11 | `missions.js` | cadre `TYPES_ETAPE`, téléphone, boulots (taxi avec pouce lisse, pizza, ambulance, courses, cascades, paquets), magasins, planque, propriétés (caisse par jour, plafond 3 jours), économie (`encaisser`, `payer`), pickpocket, journal du matin, bilan de session |
| 12 | `histoire.js` | les donneurs et leurs dialogues **dits à voix haute** (une voix par personnage, ducking, combiné au téléphone), posés **dehors** devant leur porte ou **dedans** à leur point en entrant chez eux, leur **bulle** quand ils ont une job pour toi, le téléphone qui appelle, la machine à objectifs des missions, les figurants posés en ville, les défis à panneaux, le GPS |
| 13 | `hud.js` | vie + endurance, ★, argent, arme + munitions, mini-carte 64×48 avec blips, texte de mission, GPS pointillé, toasts, menus canvas (pause, magasin, téléphone, prison, planque, options), boîte de dialogue, fondus, voiles DOM (titre, pseudo + tableau), `fetch` scores |
| 14 | `jeu.js` | machine d'états (`chargement | titre | jeu | prison | hopital | fin`), `maj()`, `rendre()`, `boucle()`, **les portes** (`transiter()` : noircir sur l'ancienne scène, changer au noir, éclaircir sur la nouvelle — le jeu figé pendant, comme sous un menu), amorçage (`fetch` du paquet), `window.BANDINI` (surface de test et débogage : `B`, espaces de noms, `graine(n)`, `entree(a)`, `debug.cones`, `maj`, `rendre`, `stats`) |

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

## Arborescence du dépôt `ybudoka/bandini`

```
run.py  config.py  pyproject.toml (name bandini, version 0.0.0)  requirements.txt  uv.lock
.env.example  .gitignore  LICENSE (GPL-3)  README.md
app/  __init__.py routes.py version.py scores.py definitions.py
      vehicules.py armes.py economie.py recherche.py carte.py missions.py magasins.py
      audio.py journal.py pietons.py manettes.py musique.py devantures.py
      bd.py comptes.py (M14 — jusque-la, le jeu n'a ni compte ni base de donnees)
templates/  base.html index.html (canvas + #tactile + voiles + data-url-*) 404.html
static/css/styles.css  static/img/favicon.svg  static/js/ (14 fichiers ci-dessus)
tests/  conftest.py harnais_js.py banc.js (bac à sable Node : faux canvas/DOM/fetch/manette/audio,
        frame(n), touches, singe)  test_routes.py test_scores.py test_definitions.py
        test_vehicules.py test_armes.py test_economie.py test_recherche.py test_carte.py
        test_districts.py test_missions.py test_magasins.py test_pietons.py test_audio.py
        test_version.py test_moteur_js.py test_police_js.py test_histoire_js.py
        test_trace_js.py test_districts_js.py test_manettes.py test_manette_js.py test_son_js.py
        test_musique.py test_devantures.py test_devantures_js.py
        test_navigateur.py
scripts/  verifier_dependances.py  git-hooks/post-commit
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
| M9 | **P1** Le parc et les boulots | **les quatre sprites : livrés** (le catalogue ne ment plus, et un juge le tient) ; restent le bateau ; le sport et le luxe (rares, par quartier, la meilleure revente) ; boulots ambulance/pizza/remorquage au klaxon ; fourrière ; radio procédurale par véhicule ; la cour de la fourrière rangée en cases, sans tremplin ; `reservoir` : ce qui n'en a pas ne brûle ni n'explose | trois boulots finis d'affilée ; sortir son char de la fourrière ; trouver un luxe et le revendre ; démolir un vélo sans que la police arrive ; se faire remorquer pour avoir laissé son char en travers, jamais pour l'avoir mis dans une case |
| — | **P1** Rampes vraiment prenables | élan, portée et freinage **calculés** depuis la fiche du char au lieu d'être écrits en tuiles ; la trajectoire rejouée par un test pour chaque rampe posée | réussir Le Grand Saut en moto et retomber sur la rue, pas dans un mur |
| — | **P1** Un saut qu'on ne voit pas | impulsion et gravité réglées **avec** la réception, le vélo qui ne décolle plus, ombre à la taille du char qui s'éloigne et pâlit avec l'altitude (comme celle de l'hélico) | voir un char quitter le sol et retomber, et savoir de combien |
| — | **P2** L'endurance du Faubourg | trois vitesses (marche / course gratuite / sprint coûteux), policier aligné sur la course, renommage `joueur_course`, barre qui s'efface quand elle est pleine | traverser la ville sans gérer une barre ; ne plus semer un agent en marchant vite |
| — | **P2** Étoiles de recherche illisibles | étoile **dessinée** (pas un caractère agrandi), jaune à elle, en haut au centre avec la ligne d'objectif qui descend, étoiles éteintes **creuses**, clignotement rouge gardé, ancre tactile réenregistrée | lire son niveau de recherche sans quitter la route des yeux |
| — | **P2** Clôture nord-sud trop large | brin nord-sud réduit à son épaisseur (trait, chapeaux de poteaux, liseré d'ombre), poteau à la jointure des coins, juge retourné : le nord-sud est **plus mince**, pas une rotation | une clôture verticale qui a l'air debout, pas couchée |
| — | **P2** La nuit ne se vide pas | rythmes de nuit abaissés, plafond appliqué **avant** le rythme, police soumise au rythme, chars stationnés redistribués | rouler dix secondes sans croiser personne à 3 h du matin |
| — | **P2** Arbres dans les sentiers | une allée se **réserve** en se traçant (arbres, bancs et buissons réglés d'un coup), et le futur sentier de banlieue aussi | traverser un parc en ligne droite par son allée, sans contourner un tronc |
| — | **P2** Le carnet | page EN COURS (objectifs barrés, donneur, récompense), page JOURNAL (écrite par les événements déjà émis, plafonnée), page RÉPERTOIRE (`p.connus` seulement) | retrouver quoi faire en deux secondes après trois jours sans jouer ; aucun personnage non rencontré dans le répertoire |
| — | **P2** Une seule musique pour toute la ville | cinq ambiances de district (fondu + hystérésis aux frontières), thème du titre enregistré par-dessus la synthèse, musique de poursuite et de bagarre avec durée minimale et queue, échelle de priorité écrite une fois | entendre qu'on a changé de quartier ; entendre que ça tourne mal avant de le voir |
| — | **P3** Trottoir et traverses de deux tuiles | `TROTTOIR = 1` (trottoirs **et** traverses), rues rétrécies pour garder leurs voies, tout ce qui vivait sur le trottoir relogé, le littéral `2` de `monde.js` remplacé par `grille.trottoir`, juges de géométrie rejoués | une rue qui a l'air d'une rue ; aucun bouchon de piétons devant un commerce ni à une traverse |
| — | **P3** Pièces plus grandes que leur maison | plancher de la pièce ≤ empreinte × étages, taille minimale imposée par la porte, pièces par tranche de taille | sortir d'un dépanneur sans avoir l'impression d'être sorti d'une cabane |
| — | **P3** L'eau n'est plus un mur | nage à l'endurance, noyade à bout de souffle, char qui coule et ne revient pas, police qui nage aussi, rive de sable en eau basse | traverser un chenal de justesse ; ne jamais traverser la baie ; un char noyé reste au fond |
| — | **P4** Feux pour piétons | poteau à chaque bout de traverse (blanc/orange, lisible par la couleur), dégagement avant le vert des chars, et « sans feu, on traverse quand c'est libre » pour ne pas échouer la foule aux T | voir quand la foule va s'engager, et ne plus voir personne partir sur l'orange |
| — | **P4** Les terrains de banlieue | entrée qui touche la rue, une case sur trois (pas plus), sentier porte→rue qui ne traverse pas la piscine, grillage mitoyen, et le paquet qui reste sous ses bornes | traverser trois cours pour semer un agent ; reconnaître une maison habitée d'un coup d'œil |
| — | **P4** Les armes à feu | mitraillette automatique, carabine, Molotov ; un coup de feu **s'entend** même sans être vu ; les munitions font l'équilibre ; vendues au marché noir | choisir son arme selon la situation, pas selon son prix ; ne jamais gagner un 5★ en tirant hors du cône |
| M15 | **P4** La ville te parle | le repli du journal enseigne une chose par jour, animateur + pubs + bulletin sur les radios, banques de répliques par contexte (48 clips), tirage sans les quatre dernières, par `B.rng()` | apprendre le klaxon sans l'avoir lu nulle part ; entendre sa propre nuit au bulletin ; traverser une foule sans entendre deux fois la même phrase |
| M11 | **P4** La police apprend | carnet du poste (portée du cône selon le casier), le stool, l'avocat du Carré, bouclier humain | un casier épais se sent en jeu ; acheter le silence du stool |
| M10 | **P4** L'argent sale | le shylock (dette, intérêts, hommes de main), guichets au camion, skimmers, assurance et fraude | rembourser 15 000 $ sans se faire tuer ; la fraude rapporte moins que le travail à l'heure |
| M12 | **P4** La ville vit | tramway sur rails, traversier à l'heure, tempête de neige avec charrue, chantier du jour et nids-de-poule | traverser à La Pointe en traversier ; conduire dans la neige sans que le rythme tombe ; un chantier qui force un détour sans couper la ville |
| M14 | **P4** Meta v2 | compte + SQLite (partie et classement au serveur, `localStorage` toujours le défaut), défi du jour à graine serveur, mode photo, coop locale | commencer au téléphone et finir à l'ordi ; le classement du jour tourne ; deux manettes sur un écran |
| M13 | **P4** Les deux fins | une mission par district (4 donneurs, 4 voix), Marco qui te vend, Dr Lachance donneur, *Le Boss* et *Sacrer son camp* | atteindre les deux fins ; chaque réplique se dit à voix haute |

Tailles relatives : M0 1, M1 3, M2 3, M3 4, M4 3, M5 2, M6 3, M7 2 (v1 = 21) ;
M8 4, M9 3, M10 3, M11 2, M12 4, M13 4, M14 4, M15 3 (v2 = 27) ;
hors vague, parce qu'elles se paient quand on veut : les transitions d'entrée et de
sortie 1, le fondu de l'hôpital et de la prison 1, les clôtures 1, les toits 2, les armes à
feu 2, le carnet 2, l'eau 3.

Ce qui reste, **trié par priorité** (le détail et la règle de tri sont dans « La v2 ») :

- **P1, le jeu ment** — M9 (le catalogue promet quatre chars que rien ne dessine) · la rampe
  du *Grand Saut*, qu'on ne peut pas gagner.
- **P2, ça se sent à chaque partie** — les arbres dans les sentiers · le carnet.
- **P3, ça porte le reste** — le trottoir et les traverses · les pièces plus grandes que leur
  maison · l'eau qui n'est plus un mur.
- **P4, ça enrichit** — les feux pour piétons · les terrains de banlieue · les armes à feu ·
  M15 · M11 · M10 · M12 · M14 · M13.

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
| **P1** | ajout | M9 Le parc et les boulots | 2 | ⚠️ **Les sprites sont livrés — le catalogue ne ment plus.** Restent les boulots au klaxon, le comptoir de fourrière, la radio du camion, ce que les fiches disent que les chars savent faire (`defonce`, `soigne`, `crochet`), et le sport et le luxe. Prérequis de M10 |
| **P1** | **correctif** | Une rampe qu'on peut vraiment prendre | 2 | ⚠️ *Le Grand Saut* est au tableau des défis et **ne peut pas se gagner** : la moto vole 126 px pour 96 px de réception |
| **P1** | **correctif** | Un saut qu'on ne voit pas | 1 | ⚠️ un saut mesure **7 px** et dure 0,3 s : les rampes ont l'air de ne pas marcher, et l'ombre est un rectangle fixe qui ne dit aucune hauteur |
| **P2** | **correctif** | L'endurance est restée celle du Faubourg | 2 | ⚠️ M8 a **quintuplé la ville** sans y revenir : un souffle vaut 33 tuiles sur 421, et le policier court plus vite que la vitesse qu'on peut tenir |
| **P2** | **correctif** | Les étoiles de recherche, grosses, jaunes et au centre | 1 | ⚠️ l'argent est dessiné **deux fois plus gros** que le niveau de recherche, qui est la seule chose qui compte en poursuite |
| **P2** | **correctif** | Une clôture nord-sud se voit par la tranche | 1 | ⚠️ corrigée **par une rotation** : un panneau de 7 px posé à plat. Et un juge exige cette rotation — il interdit la correction |
| **P2** | **correctif** | La nuit ne se vide pas | 1 | ⚠️ le Faubourg ne perd **aucune** voiture la nuit — le plafond `vehicules_max` mord avant le rythme — et garde 19 piétons à 3 h du matin |
| **P2** | **correctif** | Des arbres plantés au milieu des sentiers | 1 | à chaque parc — et `self.reserve` fait déjà ça pour le devant des portes |
| **P2** | ajout | Le carnet (mission, journal, répertoire) | 2 | **personne ne sait ce que le jeu sait faire** ; toutes les données existent déjà |
| **P2** | ajout | La musique par district, en poursuite et en bagarre | 3 | une seule musique de fond pour cinq districts ; ⚠️ le vrai travail est **l'échelle de qui gagne**, pas les pistes |
| **P3** | **correctif** | Le trottoir **et les traverses** de deux tuiles | 2 | ⚠️ redessine la ville : tout ce qui touche à la géométrie passe après |
| **P3** | **correctif** | Une pièce plus grande que sa maison | 2 | **le trottoir** : rétrécir les rues rétrécit les bâtiments |
| **P3** | **correctif** | L'eau n'est plus un mur | 3 | débloque le **bateau** de M9 et le **traversier** de M12, et décide de la piscine des terrains |
| **P4** | ajout | Des feux pour piétons | 2 | se décide avec la traverse d'une tuile ; ⚠️ contient un correctif (on traverse pendant l'orange) |
| **P4** | ajout | Les terrains de banlieue | 2 | les clôtures sont livrées : les cours se traversent déjà |
| **P4** | ajout | Les armes à feu | 2 | le marché noir de M7 leur sert de comptoir |
| **P4** | ajout | M15 La ville te parle | 3 | le narrateur, le journal et les voix existent ; ⚠️ contient un correctif (les passants se répètent) |
| **P4** | ajout | M11 La police apprend | 2 | la police de M4 suffit |
| **P4** | ajout | M10 L'argent sale | 3 | **M9** : les guichets se défoncent au camion |
| **P4** | ajout | M12 La ville vit | 4 | tramway, traversier et neige touchent à la physique |
| **P4** | ajout | M14 Meta v2 | 4 | de l'**infrastructure** (serveur, BD, comptes) : un autre métier que le reste |
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

*Ce que ça donne :* la ville cesse d'être un quartier. **421 × 213 tuiles** au lieu de
157 × 112 (5,1 ×), quatre quartiers de plus autour d'une baie, chacun avec sa trame, son
gang, son bruit et une raison d'y aller. Le Faubourg n'a pas bougé d'une tuile.

- `carte.py` : **une seule grille de blocs** (20 × 12), un district par rectangle,
  assemblés par `_assembler()`. C'est ce qui garde la ville d'un seul tenant — les artères
  traversent les frontières, rien ne se charge en roulant. Un district ne fusionne **jamais**
  par-dessus sa frontière (sinon déplacer un quartier en casserait un autre) : le juge est
  dans l'assembleur.
- ⚠️ **La règle qui fait la géographie** : une rue dont *tous* les blocs voisins sont de
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
- `audio.py` : *10-4* (auto-patrouille) et *Radio-Traversier* (camion). **À générer et à
  écouter** : `uv run python scripts/audio_elevenlabs.py --refaire dix_quatre traversier`.
- **Le paquet, mesuré** : 319 Ko bruts, **33 Ko gzip** (prévu : 360 / 60), `generer()`
  94 ms **une fois au démarrage du serveur** — le paquet est construit à la création de
  l'app, pas par requête. Budget du test relevé à 400 Ko bruts, et un second juge tient le
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
  changé, donc la position du joueur *et* celle du char gardé devant la planque sont
  oubliées ; le char revient sur la rue la plus proche de la porte.

### Les transitions d'entrée et de sortie (**correctif**, taille 1) — **livré le 13 sept. 2026**

*Retour de Martin :* « il faut améliorer les transitions quand on entre et sort des endroits.
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
⚠️ *Ajouté le 13 sept. 2026 :* cette fiche disait ici que « la prison et l'hôpital le font
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

*Demande de Martin :* « il faut des clôtures, mais si elles ne sont pas barbelées, qu'on
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

*Bug signalé par Martin :* « chez Ti-Paul, il est impossible de sortir. »

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

*Bug signalé par Martin :* « les clôtures qui sont nord-sud ne sont pas dans le bon sens. »

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

*Demande de Martin :* « un icône clignotant pour savoir où on est, une légende, savoir où est
la mission en cours. »

Les trois manquaient pour trois raisons différentes, et une seule des trois était un ajout.

- **Se trouver.** Le joueur *était* dessiné — un carré blanc de 2 px sur la mini-carte, de
  4 px sur la carte plein écran. ⚠️ **Ce n'était donc pas un manque, c'était une régression** :
  ce carré était lisible sur le Faubourg de 157 × 112, et la ville a quintuplé sans qu'il
  grossisse. Il **pulse** maintenant — un anneau blanc qui s'ouvre et se referme en 40 images
  — et le point, lui, reste dessiné **à chaque image** : on ne cache pas la seule chose qu'on
  cherche. Un repère qui clignote s'efface une image sur deux ; celui-là, jamais.
- **L'objectif bat, mais pas pareil.** ⚠️ Deux choses qui clignotent au même rythme se
  confondent : l'objectif garde son battement de 16 images et devient un **losange doré**,
  contre l'anneau blanc du joueur à 40. Deux rythmes, deux formes, deux couleurs.
- ⚠️ **Une cible hors cadre était un mensonge.** Le code la *bornait* au bord de la
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

*Demande de Martin :* « les choses qui donnent du souffle devraient donner un **bonus** de
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

*Demande de Martin :* « je veux que les toits des bâtiments soient plus réalistes. »

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

*Demande de Martin :* « il faut corriger le fade out et in quand on va à l'hôpital ou qu'on
se fait enfermer. »

Les portes avaient reçu leur machine : `transiter([fermer, ouvrir], faire)` noircit sur la
scène qu'on quitte, change **au noir**, éclaircit sur la nouvelle, et fige le jeu pendant.
⚠️ **Quatre changements de scène étaient restés derrière** — l'hôpital, la prison, la
compagnie (« on reprend son souffle ») et le coucher (« le lendemain matin »). Ils faisaient
ceci :

```js
Hud.fondu(150, 'REVEIL A L’HOPITAL — ' + facture + ' $');
setTimeoutJeu(60, function () { /* on téléporte le joueur */ });
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

*Demande de Martin :* « je veux des sirènes pour les ambulances et polices. »

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
- ⚠️ **Ce qui n'a pas été jugé, et il faut le dire** : *le son lui-même*. Le juge du
  navigateur prouve que `sirene_ambulance-1.mp3` se **décode** ; personne ici n'a d'oreilles.
  Si elle ne sonne pas comme une ambulance, c'est `--refaire sirene_ambulance`.
- **Juge (1 neuf)** : deux boucles distinctes pour une ambulance et une auto-patrouille ; le
  volume tombe à zéro à 520 px et revient en se rapprochant ; éteindre la sirène la fait
  taire ; le bouton l'allume et l'éteint au volant, avec la bonne étiquette ; et dans une
  auto le même bouton klaxonne toujours.

### M9 — Le parc automobile et les boulots (**ajout**, taille 3)

*Ce que ça donne :* autre chose à conduire, et de quoi gagner sa vie autrement.

⚠️ **Aux deux tiers le 13 sept. 2026, et il faut être précis sur ce qui manque.**
Le **Python est commité** (`7a4d26e` pour le catalogue, les boulots, les stations ; `e49603a`
pour le lot de la fourrière) : les fiches, l'économie, la carte et leurs juges existent.

**Livré le 13 sept. 2026** — les quatre chars existent, et un vélo ne saute plus (les deux
fiches ci-dessous). **Reste à faire**, et c'est celui qui se joue :

- `defonce`, `soigne`, `crochet` sont dans les fiches et **personne ne les lit** ;
- les **boulots au klaxon** ne se prennent pas : `Missions.taxi` est encore le seul, et la
  fourrière n'a ni comptoir, ni saisie à l'arrestation, ni chars dans sa cour ;
- la **radio procédurale** est dans le paquet mais `Son.Radio` ne sait pas qu'une station
  peut venir de `musiques` plutôt que d'un mp3 — le bouton RADIO du camion ne fait rien ;
- le **sport** et le **luxe** n'existent pas encore.

- `vehicules.py` : les quatre chars **existent et roulent** (fiche livrée plus bas) ; ce que
  leurs fiches disent qu'ils savent faire reste à brancher — le `defonce` du **camion** (il
  sert à M10), le `soigne` de l'**ambulance**, le `crochet` de la **remorqueuse**.
  Le **bateau** vient en dernier : il demande une physique à part et des tuiles d'eau
  carrossables — s'il coûte plus qu'il ne donne, il tombe en v3, et le traversier de M12
  suffit pour l'eau.
- **Le haut de gamme : deux chars qu'on vole exprès** (demande de Martin). Tout le reste du
  parc est utilitaire — on le prend parce qu'il sert. Il manque le contraire : un char
  qu'on prend parce qu'on le **veut**. Deux fiches, pas dix, et elles s'opposent.
  - **Le sport** (coupé décapotable) : la plus rapide sur quatre roues, reprise sèche, et
    une adhérence basse qui la fait partir en travers au frein à main. Carrosserie mince
    (peu de PV) : un barrage l'arrête pour de bon. Alarme.
  - **Le luxe** (grosse berline noire) : lourde, elle encaisse, elle ne va pas vite — et
    c'est **la meilleure revente du jeu** au garage de Ti-Guy. Alarme longue.
  - ⚠️ **Ce qui compte, c'est où on les trouve**, sinon ce sont deux lignes de catalogue
    de plus. Leur `frequence` est la plus basse du parc, et `carte.zones()` leur donne un
    **goût de quartier** : le luxe se gare devant l'Hôtel Bandini et dans les entrées des
    Érables, le sport traîne au Carré et devant le bar le soir. Ni l'un ni l'autre ne naît
    dans La Shop — on ne laisse pas une décapotable dans une cour à ferraille. Un char rare
    qu'on croise partout n'est plus rare.
  - Le reste tombe tout seul : `economie.prix_vente` est déjà proportionnelle au prix neuf,
    donc le luxe devient la meilleure course d'argent du jeu **sans une ligne de plus**, et
    le malus par doublon du même jour empêche d'en faire une usine. En M10, le shylock
    accepte un char de luxe en acompte : c'est la passerelle.
- Boulots au klaxon, sur le patron du taxi : **ambulance** (un blessé quelque part, chrono,
  le sortir vivant), **pizza** (trois livraisons, la pizza refroidit — le pourboire fond),
  **remorquage** (la fourrière paie pour les épaves).
- **Fourrière** : un char mal garé, ou saisi à l'arrestation, part au lot ; on le rachète
  au comptoir, ou on le reprend par-dessus la clôture (1★, et les gars du lot ripostent).
  - ⚠️ **« Mal garé » doit vouloir dire quelque chose** (**correctif** : la règle est
    promise par la fourrière et n'existe nulle part). Depuis que les stationnements ont
    de vraies **cases** (`^ v < >`, une tuile de large, deux de creux), la définition tombe
    toute seule et se teste : est mal garé un char **laissé hors d'une case ET qui gêne** —
    sur la chaussée, en travers d'une allée, devant une porte, sur un passage piéton, dans
    la cour d'un commerce. Un char dans sa case, ou rangé sur une ruelle, ne se fait jamais
    remorquer. ⚠️ Et **jamais celui de la planque**, quoi qu'il arrive : c'est la
    sauvegarde de Martin.
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

#### Un vélo ne saute plus, il se plie (**correctif**, taille 1) — **livré le 13 sept. 2026**

*Retour de Martin :* il part en boule de feu et donne 2★.

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
`test_les_sprites_sont_integres` valide les sprites *déclarés* dans `SPRITES` — il ne dit
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

### Un saut qu'on ne voit pas (**correctif**, taille 1)

*Bug signalé par Martin :* « les rampes n'ont pas l'air de fonctionner, et s'il marche, il
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

### Une rampe qu'on peut vraiment prendre (**correctif**, taille 2)

*Demande de Martin :* « les défis de rampe doivent vraiment être réalisables, avec assez
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

⚠️ **Et la moto est justement le char du défi.** *Le Grand Saut* exige `vehicule: "moto"` et
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
  la rampe du *Grand Saut* est validée **pour la moto**, pas pour un char moyen ; et l'élan
  disponible permet vraiment d'atteindre les 60 px de vol exigés, en partant de la rue.

### L'endurance est restée celle du Faubourg (**correctif**, taille 2)

*Demande de Martin :* « je veux que la course ne consomme plus d'énergie, mais que ce soit le
sprint qui en consomme — étant donné qu'on court quand même tout le temps, avec la grandeur
de la carte. »

⚠️ **Mesuré, et c'est pire que « on court tout le temps ».** Le modèle d'endurance a été réglé
pour le Faubourg de 157 tuiles ; M8 a quintuplé la ville et personne n'y est revenu :

| | |
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

| | Vitesse | Coût |
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

### Les étoiles de recherche, grosses, jaunes et au centre (**correctif**, taille 1)

*Demande de Martin :* « je veux les étoiles de police plus grosses, jaunes et au centre de
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

### Une clôture nord-sud se voit par la tranche (**correctif**, taille 1)

*Demande de Martin :* « les clôtures nord-sud doivent être plus vues de haut, donc mince. »

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

- **Juges** : la largeur peinte d'un brin nord-sud est strictement inférieure à la hauteur
  peinte d'un brin est-ouest, pour les **trois** clôtures ; un coin porte son poteau ; et le
  nord-sud n'est plus la rotation de l'est-ouest (l'ancien juge, retourné).

### La nuit ne se vide pas (**correctif**, taille 1)

*Demande de Martin :* « la nuit, il devrait y avoir moins de monde et de voitures sur les
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

### Des arbres plantés au milieu des sentiers (**correctif**, taille 1)

*Demande de Martin :* « les arbres ne devraient pas être dans les sentiers. »

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

### La musique dit où tu es et ce qui t'arrive (**ajout**, taille 3)

*Demande de Martin :* « je veux des musiques différentes par district, et une musique générée
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
  poursuite et une bagarre font **huit** pistes, presque 4 Mo — le dossier audio en pèse déjà
  4. Elles ne peuvent donc **pas** se charger au démarrage. La règle des radios s'applique
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

  | | |
  |---|---|
  | 1 | une réplique de l'histoire — elle baisse déjà tout le reste |
  | 2 | **la poursuite**, à partir de N étoiles |
  | 3 | **la bagarre de gang** |
  | 4 | la radio du char, ou l'ambiance du district |

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

### Le carnet : la mission, le journal, le répertoire (**ajout**, taille 2)

*Demande de Martin :* « je veux pouvoir avoir un rappel de la mission en cours dans le menu.
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

### Le trottoir et les traverses font deux tuiles, ils devraient en faire une (**correctif**, taille 2)

*Demande de Martin :* « les trottoirs ne devraient être que d'une tuile de large », et
« les traverses de piéton devraient aussi être d'une tuile ».

`TROTTOIR = 2` depuis M1, et il se voit : 32 px de trottoir contre une rue de deux voies, ce
n'est pas une proportion de ville, c'est une promenade. ⚠️ **Mais cette constante ne décore
rien — elle construit.** `_coupe()` la lit pour découper *chaque* rue, et tout le reste en
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
- **Juges** : la largeur de la ville suit toujours sa trame (`somme(COLONNES) + somme(RUES)`) ;
  une rue garde deux voies et un boulevard quatre ; aucune tuile réservée ne tombe sur la
  chaussée ; aucun kiosque, aucune borne et aucun lampadaire ne bouche la seule tuile de
  trottoir devant une porte ; et **aucune largeur de trottoir n'est écrite en dur** — ni en
  Python ni en JS, le paquet est la seule source (un test lit les deux).

### Une pièce plus grande que sa maison (**correctif**, taille 2)

*Demande de Martin :* « les intérieurs ne devraient pas être plus petits que l'extérieur. »

⚠️ **Mesuré : les 41 intérieurs de la ville sont plus grands que le bâtiment qui les
contient. Les 41.** Et parfois de façon spectaculaire :

| Lieu | Bâtiment | Intérieur | |
|---|---|---|---|
| Un logement de banlieue | 3 × 3 | 16 × 9 | **seize fois** la surface |
| Dépanneur Chez Ti-Paul | 4 × 3 | 15 × 10 | |
| Kiosque de Mme Thibodeau | 4 × 3 | 11 × 7 | |
| Garage Rocco Bandini | 7 × 3 | 17 × 10 | |
| Hôpital de Baie-des-Brumes | 6 × 5 | 17 × 10 | |
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
- ⚠️ **Ça se joue avec le trottoir.** Rétrécir les rues rétrécit les parcelles, donc les
  bâtiments : la fiche du trottoir passe avant celle-ci, sinon on ajuste les pièces à des
  bâtiments qui vont changer de taille le lendemain.
- **Juges** : pour chaque porte, le plancher de la pièce tient dans l'empreinte du bâtiment
  × son nombre d'étages ; aucun bâtiment portant une porte ne descend sous la taille de sa
  plus petite pièce ; et le juge tourne **sur cinq graines**, parce que c'est le tirage des
  marges qui crée l'écart.

### L'eau n'est plus un mur (**correctif**, taille 3)

*Demande de Martin :* « l'eau ne doit plus être un mur, mais qu'on puisse soit y nager ou
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

### Des feux pour piétons (**ajout**, taille 2)

*Demande de Martin :* « pour les piétons, il faut ajouter des lumières de priorité, et sinon
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

### Les terrains de banlieue (**ajout**, taille 2)

*Demande de Martin :* « les terrains des résidences doivent être plus fournis — jardin,
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
  six objets par terrain, sur un district entier, et on sort des bornes (400 Ko bruts, 70 Ko
  gzip). **On mesure avant**, et si ça déborde, le décor de terrain se **dérive de la
  position** (`hash2`) au lieu de voyager — exactement ce qui a été fait pour les usures
  d'asphalte des stationnements.
- **Juges** : toute entrée de voiture rejoint la chaussée ; un sentier relie chaque porte de
  banlieue à la rue, sans passer par une piscine ; une case d'entrée n'apparaît que sur une
  fraction des terrains, mesurée ; et le paquet reste sous ses bornes, sinon le décor se
  dérive et ne voyage plus.

### Les armes à feu (**ajout**, taille 2)

*Demande de Martin :* « je veux des armes à feu. »

Il y en a **deux** aujourd'hui, et c'est ça le problème : le **pistolet** (250 $, chargeur
de 12, 30 points) et le **fusil à pompe** (600 $, 8 cartouches, 6 plombs). Sur dix armes au
catalogue, huit sont de la mêlée, du ramassé par terre ou une fronde. Il ne manque pas *une*
arme à feu — il manque une **raison de choisir** entre elles. Trois de plus, et chacune
répond à une question que les deux autres ne savent pas régler :

- **La mitraillette** — *« ils sont trois. »* Automatique : on tient le bouton, la cadence
  est haute, les dégâts par balle bas, et la dispersion **monte tant qu'on tient**. On arrose
  ou on tire par rafales courtes ; c'est le choix qui fait l'arme. ⚠️ Le moteur ne sait pas
  tirer en automatique : une arme tire un coup par pression, `cadence` images plus tard. Le
  champ `auto` est du travail neuf, et il touche au tactile — au téléphone, « tenir » est un
  geste, pas un clic.
- **La carabine** — *« il est loin. »* Longue portée, lente, précise, un passant d'une balle.
  ⚠️ **Plafonnée à la largeur de l'écran** : la vue fait 480 px de large, soit 30 tuiles.
  Une portée qui dépasse ça, c'est tirer sur ce qu'on ne voit pas — et le pistolet est déjà
  à 180 px, onze tuiles. La carabine s'arrête à ce que l'écran montre, et c'est une borne,
  pas un réglage.
- **Le cocktail Molotov** — *« ils sont groupés, et je veux que ça dure. »* Il se lance **en
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
  t'évite d'être *vu*, jamais d'être *cherché*. La distance achète du temps, pas
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

### M15 — La ville te parle (**ajout**, taille 3)

*Ce que ça donne :* le jeu cesse d'être muet entre deux répliques de mission — et il
t'apprend enfin ce qu'il sait faire.

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
- **Juges** : une leçon ne se donne qu'une fois et jamais sur ce qui est déjà fait ; un clip
  de radio ne coupe jamais une réplique de mission (le ducking a déjà sa file d'attente) ;
  la pub d'un commerce possédé n'est plus celle d'un commerce à visiter ; **aucune des quatre dernières
  répliques dites ne peut ressortir**, et toute banque où l'on tire en contient au moins six
  (quatre à exclure, deux pour que ça reste un tirage) ; le tirage passe par `B.rng()`, donc
  le banc peut jouer mille rencontres et compter les répétitions — il doit en trouver zéro.

### M11 — La police apprend (**ajout**, taille 2)

*Ce que ça donne :* un casier qui pèse, et des façons de le faire taire.

- **Le carnet du poste** : au poste, ton casier, tes affiches, tes surnoms. Plus il est
  épais, plus les agents te reconnaissent **de loin** (la portée du cône monte avec le
  casier) — en plus des amendes et des pots-de-vin, qui en tiennent déjà compte.
- **Le stool** : un passant qui te reconnaît et part téléphoner. L'acheter, le suivre, ou
  le faire taire : chacun a son prix en étoiles.
- **L'avocat du Carré** : cher, il efface une page du casier ou te sort de prison sans
  amende — et il ne travaille pas deux fois la même journée.
- **Bouclier humain** (risqué) : attraper un piéton à bout portant ; la police ne tire plus,
  mais le compteur monte et le piéton se débat.
- **Juges** : la portée du cône reste bornée quel que soit le casier ; le stool ne naît pas
  dans le dos d'un joueur immobile ; l'avocat ne rend jamais un casier négatif.

### M10 — L'argent sale (**ajout**, taille 3)

*Ce que ça donne :* une raison de se lever le matin — la dette de Rocco.

- **Le shylock** : 15 000 $, un intérêt par jour, des rappels au téléphone, puis des hommes
  de main qui te trouvent où que tu sois. Rembourser ouvre une des deux fins (M13).
- **Guichets** : les défoncer au camion (bruyant, 2★, la caisse par terre) ou poser un
  **skimmer** et revenir le lendemain (silencieux, lent, il peut être trouvé).
- **Assurance et fraude** : assurer un char au garage, le faire disparaître, encaisser —
  trois fois de suite et l'assureur enquête.
- `economie.py` : dette, intérêts **bornés**, primes, seuils de suspicion.
- **Juges** : la dette ne dépasse jamais son plafond ; un joueur qui ne fait rien ne devient
  pas insolvable en une nuit ; la fraude rapporte **moins à l'heure** que le travail honnête
  — sinon le jeu se joue tout seul et le taxi ne sert plus à rien.

### M12 — La ville vit (**ajout**, taille 4)

*Ce que ça donne :* une ville qui bouge toute seule, avec ou sans toi.

- **Le chantier** (demande de Martin) : rien ne dit « Québec » comme une voie barrée depuis
  trois ans — et ce n'est pas qu'une farce. C'est une **surcouche** au champ `voie`, tirée
  par la graine du jour : une voie fermée, des cônes orange (le sprite `cone` existe déjà
  dans `OBJETS`), un détour. Le trafic sait déjà se déporter dans la voie d'à côté ; ici il
  n'a plus le choix. La ville devient différente d'un jour à l'autre **sans regénérer une
  seule tuile**, et la police a enfin un endroit où se tenir sans raison.
  - ⚠️ **Un chantier ne coupe jamais la ville en deux.** Il ferme UNE voie d'un boulevard,
    jamais une rue à voie unique, jamais un pont, jamais la seule approche d'un croisement.
    Le juge est celui de M1 (`voies_bloquees` : fortement connexes) rejoué **avec** le
    chantier posé — s'il rougit, le chantier se pose ailleurs.
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

### M14 — Meta v2 (**ajout**, taille 4)

- **Un compte et une base de données** (demande de Martin). Aujourd'hui la partie vit dans
  le `localStorage` du navigateur : elle ne traverse pas. Vingt minutes au téléphone, puis
  on s'assoit à l'ordi, et on recommence. Un compte règle ça, et il porte aussi le défi du
  jour et le classement — qui ont besoin d'un serveur de toute façon.
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
- **Défi du jour** à graine serveur (reporté de M7) : `/api/defi` donne la graine du jour,
  le classement est celui du jour, tout le monde joue la même ville.
- **Mode photo** : le jeu se fige, la caméra se détache, quelques filtres, et l'image se
  télécharge.
- **Coop locale** (risqué) : deux manettes, une caméra qui tient les deux joueurs, zoom
  arrière quand ils s'éloignent. ⚠️ 480 × 270 n'est pas grand : à décider **après un essai**,
  pas avant.

### M13 — Les deux fins (**ajout**, taille 4)

*Ce que ça donne :* une histoire qui se termine, de deux façons.

- **Une mission par district** : quatre donneurs de plus, quatre voix ElevenLabs de plus,
  un gang à déloger par quartier.
- **Marco te vend** : au bout de l'arc, le cousin parle à la police — la mission bascule en
  cours de route.
- **Dr Lachance** devient donneur : l'hôpital a ses secrets (et ses ordonnances).
- **Le Boss** : les 4 propriétés **et** les 4 districts libérés → manchette, générique, la
  ville change de couleur.
- **Sacrer son camp** : 15 000 $ en poche, traversier de nuit, 0★ → l'autre générique.
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
