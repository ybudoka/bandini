# Bandini — plan et état d'avancement

Document de reprise : à lire en début de session. Le plan ci-dessous a été
approuvé par Martin le 12 septembre 2026. Mettre à jour la section « État des
jalons » à chaque jalon livré.

## État des jalons

| Jalon | État | Notes |
|---|---|---|
| M0 Squelette et mise en ligne | **livré** (12 sept. 2026) | dépôt `ybudoka/bandini`, Flask + uv, 13 fichiers JS, entrées, banc Node, CI, tests ; serveur installé, https://bandini.gestiondojo.ca |
| M1 La ville | **livré** (12 sept. 2026) | `carte.py` : trame **irrégulière** (colonnes, rangées et rues toutes différentes), superblocs qui avalent des rues, parcelles BSP par îlot, 157×112 tuiles, 62 croisements dont des T, 10 intérieurs ; juges (voies fortement connexes, un seul îlot marchable, **asymétrie**) ; cache de morceaux borné, mini-carte |
| Audio ElevenLabs | **livré** (12 sept. 2026) | MCP `elevenlabs` + `app/audio.py` + 14 bruitages dans `static/audio/` ; **3 radios** (La Brume, Taxi-Radio, Le Choc) générées par ElevenLabs Music le 13 sept., chargées au premier tour de clé ; voix des personnages en M6 |
| Vie de rue | **livré** (12 sept. 2026) | femmes, enfants (**intouchables**), mères suivies de leur petit, filles de la Brume (la nuit, un fondu, jamais une scène), kiosques à hot-dogs / journaux / roulotte à café et camions-restaurants posés par `carte.py` |
| M2 Piétons et poings | **livré** (12 sept. 2026) | `pietons.py` (8 archétypes, courage, témoin, gangs) ; hachage spatial, bulle de foule, flâner/fuir/témoin/riposter, mêlée en trois temps, coup fort, roulade, projectiles + plombs + cloche, visée assistée, armes de fortune qui cassent, sang plafonné, pickpocket dans le dos |
| M3 Véhicules | **livré** (13 sept. 2026) | auto, taxi, moto, auto-patrouille (sprite) ; physique arcade, **chaîne de cercles**, sous-pas, monter/descendre/carjacking/éjection, trafic qui **lit le champ `voie`** (tourne à gauche après le croisement, ralentit avant le coin), feux sur les vrais croisements, dégâts/fumée/feu/explosion, alarmes, rampes, renversements, taxi au klaxon avec pourboire selon la douceur, hôpital quand on meurt, moteur qui monte dans les tours |
| M4 Police | à faire | |
| M5 Intérieurs et économie | à faire | |
| M6 Missions et gang | à faire | |
| M7 Finition v1 | à faire | |

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
uv run python scripts/audio_elevenlabs.py --refaire coup pas la_brume
```

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

## La vision (tout ce qui est retenu)

Étiquettes : **v1** = première version complète ; **v2** = vagues suivantes ; **risqué** = touche au moteur.

**Prémisse.** Tu es « Bandini », surnom hérité de ton oncle Rocco Bandini, petit bandit
mort en laissant un garage, une dette de 15 000 $ au shylock, une cachette et un téléphone
plein de contacts douteux, à **Baie-des-Brumes**, ville de port et de brouillard. Tu
débarques en autobus avec 50 $. Deux fins **v2** : *Le Boss* (posséder les 4 propriétés,
libérer 4 districts) ou *Sacrer son camp* (15 000 $ en poche, traversier de nuit à 0 étoile).

**Districts** : Le Faubourg (centre, gang Les Cravates) **v1** · Les Quais (port, Les Morues)
· Les Érables (banlieue, Les Chevreuils) · La Shop (industriel, Les Boulonneux) · La Pointe
(parc-île, Les Skateux) **v2**. Journal : *Le Clairon de la Baie*. Radios : *La Brume*
(jazz, auto), *Taxi-Radio* (country), *Le Choc* (punk, moto), *10-4* (ondes du poste),
*Radio-Traversier* (rigodon) ; l'autobus n'a que son moteur.

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
3 défis · contacts du marché noir, la peur fait taire les témoins **v1**.

**Meta et présentation** : tableau des scores en ligne (fortune, missions, propriétés,
durée) · bilan de session, caméra qui respire, visée assistée, GPS pointillé, options
(sang, palette daltonienne, vibration) **v1** · défi du jour à graine serveur **v1 si le
temps le permet, sinon v2** · mode photo, coop locale **v2**.

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

### Côté JS (`static/js/`, 13 scripts classiques, ordre = dépendances, listés dans `templates/index.html`)

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
| 12 | `hud.js` | vie + endurance, ★, argent, arme + munitions, mini-carte 64×48 avec blips, texte de mission, GPS pointillé, toasts, menus canvas (pause, magasin, téléphone, prison, planque, options), boîte de dialogue, fondus, voiles DOM (titre, pseudo + tableau), `fetch` scores |
| 13 | `jeu.js` | machine d'états (`chargement | titre | jeu | prison | hopital | fin`), `maj()`, `rendre()`, `boucle()`, amorçage (`fetch` du paquet), `window.BANDINI` (surface de test et débogage : `B`, espaces de noms, `graine(n)`, `entree(a)`, `debug.cones`, `maj`, `rendre`, `stats`) |

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
templates/  base.html index.html (canvas + #tactile + voiles + data-url-*) 404.html
static/css/styles.css  static/img/favicon.svg  static/js/ (13 fichiers ci-dessus)
tests/  conftest.py harnais_js.py banc.js (bac à sable Node : faux canvas/DOM/fetch/manette,
        frame(n), touches, singe)  test_routes.py test_scores.py test_definitions.py
        test_vehicules.py test_armes.py test_economie.py test_recherche.py test_carte.py
        test_missions.py test_magasins.py test_version.py test_moteur_js.py test_navigateur.py
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
| M4 | Police | crimes, cônes + ligne de vue, témoins (acheter le silence), recherche 1–3★, patrouille/poursuite/arrestation, autos de poursuite, prison (amende, pot-de-vin, casier), hôpital, sergent ami, affiches | se faire pincer ; tests cône, décroissance, amendes |
| M5 | Intérieurs et économie | 5 intérieurs, magasins, planque (sauvegarde, coffre, garage), revente, propriétés, paquets cachés, journal du matin, bilan de session, tableau des scores, options | acheter, vendre, sauvegarder, recharger |
| M6 | Missions et gang | cadre + téléphone + 5 missions + 3 défis, Les Cravates et leur territoire, boîte de dialogue, GPS, contacts du marché noir | finir les 5 missions |
| M7 | Finition v1 | 4–5★ (barrages, hélico), musique, passe sonore, HUD, performance sur vrai téléphone, Playwright, défi du jour si le temps le permet | 60 i/s de nuit à 3★ sur téléphone |
| v2 | vagues suivantes | autres districts + gangs, radio procédurale, tramway, traversier, fourrière complète, deux fins, guichets/skimmers, assurance, shylock, stool, avocat, carnet du poste, neige, remorqueuse, mode photo, coop | un jalon par vague |

Tailles relatives : M0 1, M1 3, M2 3, M3 4, M4 3, M5 2, M6 3, M7 2.

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
- **Audio absent ou cassé** : `exporter()` ne déclare que les fichiers présents, chaque
  effet retombe sur la synthèse, et un test navigateur prouve que chaque MP3 **se décode
  vraiment** (un fichier tronqué ne se verrait qu'à l'oreille, en jeu).
