# Bandini — plan et état d'avancement

Document de reprise : à lire en début de session. Le plan ci-dessous a été
approuvé par Martin le 12 septembre 2026. Mettre à jour la section « État des
jalons » à chaque jalon livré.

## État des jalons

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
| **v1 complète** | **livrée** (13 sept. 2026) | M0 → M7 en ligne, 308 tests ; la suite est planifiée ci-dessous (« La v2 — sept vagues ») |
| M8 Les cinq districts | **livré** (13 sept. 2026) | la ville passe de 157×112 à **421×213 tuiles** (5,1 ×) : Les Érables (banlieue, Les Chevreuils), La Shop (industriel, Les Boulonneux), Les Quais (port, Les Morues), La Pointe (parc, Les Skateux) et **la baie** — une seule grille de blocs, un district par rectangle, aucune fusion par-dessus une frontière ; une rue dont tous les blocs voisins sont de l'eau est **noyée** (c'est ce qui ferme la baie et coupe le chenal), et **un pont** relie La Pointe ; 5 nouveaux lieux (dépanneur, Hôtel Bandini, cantine des Quais, usine Prévost, phare) ; 4 gangs + 4 passants de quartier (`districts` les enferme chez eux) ; densité **et rythme** par district (La Shop déserte la nuit, les Quais le matin) ; radios *10-4* et *Radio-Traversier* ; paquet **319 Ko bruts / 33 Ko gzip**, `generer()` 94 ms au démarrage, **0,29 ms par image** de nuit à 5★ (0,26 avant) ; chien de garde du trafic corrigé (480 images de feu rouge **puis** l'attente de boîte faisaient 600 : il mordait un char sage) |
| Manette réapprenable | **livré** (13 sept. 2026) | retour de Martin (« les boutons de la manette bluetooth ne sont pas bien mappé ») : les numéros de boutons d'une manette que le navigateur ne reconnaît pas (`mapping: ""`) ne veulent rien dire — la même manette n'a pas les mêmes numéros sur le téléphone et sur le Mac, **ça ne se devine pas**. OPTIONS > **MANETTE** : ce que la manette dit d'elle-même (nom, RECONNUE / NON RECONNUE, boutons enfoncés en direct), une ligne par action qu'on réapprend en l'appuyant, la croix en quatre gestes, gaz et frein en **bouton ou en axe** (repos mesuré : une gâchette-axe repose à −1 sur une manette et à 0 sur la suivante), TOUT RÉAPPRENDRE qui enchaîne, PAR DÉFAUT ; gardé dans les options. **Croix-chapeau** : sur une 8BitDo en Bluetooth la croix n'est pas quatre boutons mais UN axe — on appuie et aucun numéro ne s'allume, elle a l'air morte ; on apprend HAUT et DROITE et le tour des huit positions se déduit, diagonales comprises (sinon repli sur les quatre côtés). L'écran liste les **axes qui bougent**, et souffle le mode Xbox aux 8BitDo. ⚠️ Un apprentissage **attend qu'on relâche** : sur un axe, lâcher le haut bouge autant qu'appuyer sur le bas, et la direction suivante s'apprenait sur la valeur du repos — la croix tenait alors les quatre directions en permanence. Corrigé au passage : `annuler` n'avait **aucun** bouton (le bouton de droite fait RETOUR), et « Jouer » n'était qu'un bouton de la page — on commence maintenant la partie à la manette ou au clavier |
| M9 Le parc et les boulots | à faire (v2) | camion, autobus, ambulance, remorqueuse (bateau en dernier) ; ambulance/pizza/remorquage au klaxon, fourrière, radio procédurale |
| M10 L'argent sale | à faire (v2) | le shylock et la dette de Rocco, guichets au camion, skimmers, assurance et fraude |
| M11 La police apprend | à faire (v2) | carnet du poste (le casier se voit de loin), le stool, l'avocat du Carré, bouclier humain |
| M12 La ville vit | à faire (v2) | tramway, traversier à l'heure, tempête de neige et charrue |
| M13 Les deux fins | à faire (v2) | une mission par district, Marco qui te vend, Dr Lachance donneur, *Le Boss* et *Sacrer son camp* |
| M14 Meta v2 | à faire (v2) | défi du jour à graine serveur (reporté de M7), mode photo, coop locale |

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
sort des portes et y rentre parfois. Les croisements à quatre bras ont des **feux** (deux
lanternes), la tige d'un **T** a un **STOP** (arrêt complet, puis passage si la boîte est
libre), et un char cède aux piétons engagés. Des **cyclistes** roulent avec le trafic ; on
peut prendre leur vélo (ils tombent et témoignent) — pas de moteur, pas de radio.

**Vie de rue (12 sept. 2026)** : la foule mêle hommes, femmes, ados, itinérants, livreurs,
**mères accompagnées de leur enfant** et **enfants** — ces derniers sont **intouchables** :
aucune arme, aucun véhicule ne les atteint, ils détalent de plus loin que les adultes. C'est
une règle du catalogue (`pietons.intouchable`), pas une consigne. Les **filles de la Brume**
travaillent la nuit près du bar et du port : on paie, l'écran fond au noir, la vie remonte —
rien ne se montre, et elles refusent quand la police te cherche. Les **commerces ambulants**
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
| `economie.py` | `ARGENT_DEPART`, `amende(etoiles, casier)` = `min(argent, base[★] × (1 + 0,5 × casier))`, pots-de-vin `40 × ★ × (1 + 0,5 × casier)`, hôpital `clamp(10 %, 30, 500)`, propriétés, `FORTUNE_MAX` | jamais négatif, monotone, plafonné, retour sur investissement 10–60 min, coordonnées sur une porte |
| `recherche.py` | paliers 0–5 (agents, autos, barrages, tirent, décroissance 15/25/40/60/90 s), délits → ★ (taxonomie ci-dessous), cônes (à pied 90° 9 tuiles jour / 6 nuit ; auto 60° 14/12 ; témoin 120° 6/4 ; alarme rayon 12) | contigus, monotones, palier 0 sans réponse |
| `carte.py` | **plan compact** du district (grille de blocs 8×6 : `h` habitations, `c` commerces, `g` gang, `p` parc, `o` place, `q` quai, `~` eau, majuscules = bâtiment spécial garanti, `<` et `^` = bloc **avalé** par son voisin) + `COLONNES`/`RANGEES`/`RUES_V`/`RUES_H` (aucune égale à sa voisine) ; `generer(plan, graine)` produit tuiles (`sol`, `voie` = champ de direction + lignes d'arrêt), intersections (avec leurs bras), portes, lampes, décor, zones, apparitions ; intérieurs en ASCII. **Trois sources d'irrégularité** : la trame, les superblocs (une rue qui n'existe pas → des T), et le découpage BSP en parcelles inégales (bâtiments en U ou en L, dents creuses, terrains vagues, stationnements). Un **filet** bouche les poches injoignables au lieu de livrer un îlot muré | rectangulaire, glyphes connus, **connexité forte des voies** (BFS), un seul îlot marchable **sur cinq graines**, portes ⇔ intérieurs, aucun gabarit sur une rue **qui existe**, un superbloc avale bien sa rue, **juge d'asymétrie**, déterministe |
| `missions.py` | 5 missions v1 + 3 défis : donneur, prérequis, objectifs typés (aller, monter, livrer, tuer, survivre, course, chrono, retourner), récompense, dialogues | prérequis sans cycle, cibles sur tuile marchable, références existantes |
| `pietons.py` | 8 archétypes (couleurs = échanges de palette, `courage`, `temoin`, bourse, arme), les gangs et leur territoire, `REACTIONS` (recul, KO, fuite, saignement, pickpocket) | couleurs valides, courage de 0 à 1, un gang a un territoire qui existe, aucun membre de gang au hasard dans la rue |
| `magasins.py` | inventaires armurerie / vêtements / garage | articles existants |
| `audio.py` | catalogue des sons : slug, **prompt ElevenLabs** (la recette reste à côté du son), durée, boucle, volume, variantes ; `exporter()` ne déclare que les fichiers **présents** | bornes ElevenLabs, aucun orphelin, poids < 600 Ko, chaque effet garde son repli synthétisé |
| `definitions.py` | `assembler()` → `Paquet(corps, etag, taille)` construit une fois au démarrage | déterministe, < 200 Ko |
| `scores.py` | copie de `car-game`, `valider()` : pseudo, `fortune`, `missions`, `proprietes`, `duree_s` ; tri fortune puis missions puis durée ; borne `fortune / duree_s` | copie des tests |
| `version.py` + `scripts/git-hooks/post-commit` | copie intégrale d'`online-4all-games` (numéro déduit du message de commit, garde `BANDINI_VERSION`) ; `version = "0.0.0"` au départ | `test_version.py` copié |
| `routes.py` | `/`, `/api/definitions` (ETag, 304), `/api/scores` GET/POST, `/sante`, 404 « Cul-de-sac » | page, ETag/304, scores, 413 |

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
| 6 | `monde.js` | carte active depuis le paquet, `solide()`, `ligneLibre()` (DDA), A* à budget (2/image, cap 800 nœuds, file, repli ligne droite), feux, cache de morceaux 256 px, caméra amortie avec avance, horloge jour-nuit, intérieurs (pile `B.exterieur`), mini-carte |
| 7 | `entites.js` | structure unique `{x, y, vx, vy, r, z, angle, face, etat, t, vie, sprite, swaps, …}`, **deux** index spatiaux 64 px (le décor ne bouge jamais : bâti une fois ; le reste rebâti à chaque image), cercle-vs-tuiles, piétons (flâne, figé, fuit, **témoin**, riposte, assommé, aveuglé, mort), gangs, bulle 300–520 px, armes de fortune semées, ramassages, particules, décalques, tri par y (les morts d'abord) |
| 8 | `combat.js` | arcs de mêlée (anticipation → actif → repos), coup fort, esquive, projectiles, fusil à plombs, fronde en cloche, extincteur, réactions, saignement, mort, sang (plafond 150 décalques), lâcher/ramasser, cycle d'armes, visée assistée |
| 9 | `vehicules.js` | physique arcade (accélération, friction, braquage selon vitesse, adhérence/dérive, frein à main), **chaîne de cercles** pour les collisions (tuiles, véhicules, piétons), sous-pas au-dessus de 3 px/image, monter/descendre/éjecter, trafic sur le champ de direction (regard devant, feux, choix de sortie **par la voie qui va dans son sens** — d'où le virage à gauche après le croisement —, ralentissement avant le coin, déblocage par patience), dégâts/fumée/feu/explosion, rampes (`z`), alarmes, klaxon. Sprites : **un seul dessin** par char, 32 caps cuits par rotation |
| 10 | `police.js` | `signalerCrime()`, `voit()` (distance, cône, ligne de vue, budget 20 rayons/image), rapports de témoins, machine de recherche (`chaleur`, ★, `vu`, décroissance), apparition par palier, patrouille/poursuite (A*)/arrestation, autos de poursuite, barrages, hélico, sergent ami, affiches, prison et hôpital |
| 11 | `missions.js` | cadre `TYPES_ETAPE`, téléphone, boulots (taxi avec pouce lisse, pizza, ambulance, courses, cascades, paquets), magasins, planque, propriétés (caisse par jour, plafond 3 jours), économie (`encaisser`, `payer`), pickpocket, journal du matin, bilan de session |
| 12 | `histoire.js` | les donneurs et leurs dialogues **dits à voix haute** (une voix par personnage, ducking, combiné au téléphone), le téléphone qui appelle, la machine à objectifs des missions, les figurants posés en ville, les défis à panneaux, le GPS |
| 13 | `hud.js` | vie + endurance, ★, argent, arme + munitions, mini-carte 64×48 avec blips, texte de mission, GPS pointillé, toasts, menus canvas (pause, magasin, téléphone, prison, planque, options), boîte de dialogue, fondus, voiles DOM (titre, pseudo + tableau), `fetch` scores |
| 14 | `jeu.js` | machine d'états (`chargement | titre | jeu | prison | hopital | fin`), `maj()`, `rendre()`, `boucle()`, amorçage (`fetch` du paquet), `window.BANDINI` (surface de test et débogage : `B`, espaces de noms, `graine(n)`, `entree(a)`, `debug.cones`, `maj`, `rendre`, `stats`) |

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
      audio.py journal.py pietons.py
templates/  base.html index.html (canvas + #tactile + voiles + data-url-*) 404.html
static/css/styles.css  static/img/favicon.svg  static/js/ (14 fichiers ci-dessus)
tests/  conftest.py harnais_js.py banc.js (bac à sable Node : faux canvas/DOM/fetch/manette,
        frame(n), touches, singe)  test_routes.py test_scores.py test_definitions.py
        test_vehicules.py test_armes.py test_economie.py test_recherche.py test_carte.py
        test_districts.py test_missions.py test_magasins.py test_pietons.py test_audio.py
        test_version.py test_moteur_js.py test_police_js.py test_histoire_js.py
        test_trace_js.py test_districts_js.py test_manette_js.py test_navigateur.py
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
| M9 | Le parc et les boulots | camion, autobus, ambulance, remorqueuse, bateau ; boulots ambulance/pizza/remorquage au klaxon ; fourrière ; radio procédurale par véhicule | trois boulots finis d'affilée ; sortir son char de la fourrière |
| M10 | L'argent sale | le shylock (dette, intérêts, hommes de main), guichets au camion, skimmers, assurance et fraude | rembourser 15 000 $ sans se faire tuer ; la fraude rapporte moins que le travail à l'heure |
| M11 | La police apprend | carnet du poste (portée du cône selon le casier), le stool, l'avocat du Carré, bouclier humain | un casier épais se sent en jeu ; acheter le silence du stool |
| M12 | La ville vit | tramway sur rails, traversier à l'heure, tempête de neige avec charrue | traverser à La Pointe en traversier ; conduire dans la neige sans que le rythme tombe |
| M13 | Les deux fins | une mission par district (4 donneurs, 4 voix), Marco qui te vend, Dr Lachance donneur, *Le Boss* et *Sacrer son camp* | atteindre les deux fins ; chaque réplique se dit à voix haute |
| M14 | Meta v2 | défi du jour à graine serveur, mode photo, coop locale | le classement du jour tourne ; deux manettes sur un écran |

Tailles relatives : M0 1, M1 3, M2 3, M3 4, M4 3, M5 2, M6 3, M7 2 (v1 = 21) ;
M8 4, M9 3, M10 3, M11 2, M12 3, M13 4, M14 2 (v2 = 21).

## La v2 — sept vagues (plan du 13 sept. 2026)

Règle inchangée : **chaque vague reste jouable, testée, déployée**. L'ordre suit les
dépendances — M8 porte tout le reste (les gangs, les fins, le traversier, la fourrière
ont besoin de la ville complète) ; M9 à M12 se permutent selon l'envie du moment.

Ce que la v2 **ne fait pas**, pour que le plan tienne : pas de multijoueur en ligne, pas
de 3D, pas d'histoire à plus de deux fins, pas de génération de sprites par IA. Le jeu
reste un GTA 1 québécois en pixels, joué au téléphone.

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

### M9 — Le parc automobile et les boulots (taille 3)

*Ce que ça donne :* autre chose à conduire, et de quoi gagner sa vie autrement.

- `vehicules.py` : **camion** (lent, lourd, défonce un mur — il sert à M10), **autobus**
  (long, deux cercles de collision de plus, pas de radio), **ambulance** (rapide, sirène,
  soigne), **remorqueuse** (un crochet : on accroche un char et on le traîne).
  Le **bateau** vient en dernier : il demande une physique à part et des tuiles d'eau
  carrossables — s'il coûte plus qu'il ne donne, il tombe en v3, et le traversier de M12
  suffit pour l'eau.
- Boulots au klaxon, sur le patron du taxi : **ambulance** (un blessé quelque part, chrono,
  le sortir vivant), **pizza** (trois livraisons, la pizza refroidit — le pourboire fond),
  **remorquage** (la fourrière paie pour les épaves).
- **Fourrière** : un char mal garé, ou saisi à l'arrestation, part au lot ; on le rachète
  au comptoir, ou on le reprend par-dessus la clôture (1★, et les gars du lot ripostent).
- **Radio procédurale** : `Son.Mus` (le séquenceur trois voix, déjà là) génère une station
  par véhicule à partir d'une graine — le camion a sa toune, l'autobus n'a que son moteur.
- **Juges** : chaque char a son sprite (harnais Node) ; la remorqueuse n'en traîne qu'un à
  la fois ; l'ambulance ne ressuscite personne ; la fourrière ne peut **jamais** manger le
  char de la planque (c'est la sauvegarde de Martin).

### M10 — L'argent sale (taille 3)

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

### M11 — La police apprend (taille 2)

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

### M12 — La ville vit (taille 3)

*Ce que ça donne :* une ville qui bouge toute seule, avec ou sans toi.

- **Tramway** : une ligne sur rails du Faubourg aux Quais, des arrêts, des portes — et il
  ne s'arrête pas pour toi. ⚠️ C'est un véhicule qui **ignore** le champ de direction : il
  a ses propres rails, et le trafic doit lui céder.
- **Traversier** : Les Quais ↔ La Pointe, à l'heure, quatre chars à bord, il part sans toi.
- **Tempête de neige** (risqué) : visibilité réduite, adhérence divisée, **charrue** qui
  pousse la neige et les chars mal garés ; la police glisse aussi.
- ⚠️ La neige touche à la physique **et** au rendu : elle arrive derrière une option, et la
  sonde de performance Playwright la mesure avant qu'elle soit allumée par défaut.

### M13 — Les deux fins (taille 4)

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

### M14 — Meta v2 (taille 2)

- **Défi du jour** à graine serveur (reporté de M7) : `/api/defi` donne la graine du jour,
  le classement est celui du jour, tout le monde joue la même ville.
- **Mode photo** : le jeu se fige, la caméra se détache, quelques filtres, et l'image se
  télécharge.
- **Coop locale** (risqué) : deux manettes, une caméra qui tient les deux joueurs, zoom
  arrière quand ils s'éloignent. ⚠️ 480 × 270 n'est pas grand : à décider **après un essai**,
  pas avant.

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
- **Économie qui se joue toute seule (M10)** : tout gain passe par un juge « à l'heure »,
  comparé au taxi ; la fraude et les skimmers doivent rester moins payants que le travail.
- **Coop locale (M14)** : un essai jetable avant toute promesse ; si l'écran est trop petit
  à deux, le jalon tombe et le mode photo suffit.
- **Audio absent ou cassé** : `exporter()` ne déclare que les fichiers présents, chaque
  effet retombe sur la synthèse, et un test navigateur prouve que chaque MP3 **se décode
  vraiment** (un fichier tronqué ne se verrait qu'à l'oreille, en jeu).
