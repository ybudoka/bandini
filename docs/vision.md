# Bandini — le contexte, les décisions et la vision

← [le plan](plan.md), qui ne garde que ce qui reste à faire

Ce que Martin veut, ce qu'on a décidé avec lui, et tout ce qui est retenu. Les décisions qui ont leur propre fichier y renvoient : [les voix de l'histoire](voix-de-l-histoire.md), [les missions mises en scène et le jeu d'acteur](missions-en-scene.md).

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
| Commandes | clavier + manette (API Gamepad, stick analogique) + tactile (joystick virtuel + boutons) dès la v1 ; les **manettes Touch d'un Meta Quest** depuis le 17 sept. 2026, par une session WebXR (`casque.js`) |
| Adresse | `https://bandini.gestiondojo.ca`, gunicorn **8006** (8005 = Auto Évasion, 8004 = KidTube), service `bandini-gestiondojo`, `/srv/bandini`, port local 5400 |
| Mise en ligne | **tôt puis à chaque jalon** : le site existe dès le squelette, chaque jalon est déployé, Martin teste sur téléphone |
| Idées | **toutes** les idées de la première liste + les 28 nouvelles ; prémisse, ville et personnages retenus |
| Audio (12 sept. 2026) | les sons importants sont de **vrais échantillons ElevenLabs**, générés par le serveur MCP `elevenlabs` et versionnés dans `static/audio/` ; la synthèse de `son.js` reste le **filet** quand un fichier manque. Voix des personnages en M6, radios en M3. |
| Voix de l'histoire (13 sept. 2026) | **chaque réplique de l'histoire est dite à voix haute, en plus d'être écrite.** Les dialogues des donneurs (Ti-Guy, Mme Thibodeau, Sgt Bouchard, Josée, Dr Lachance, Marco), le téléphone, les manchettes du journal : une voix ElevenLabs **par personnage**, générée une fois par TTS et versionnée comme le reste. Le texte reste affiché (lisibilité, muet, tactile) ; la voix s'ajoute, elle ne remplace pas. |
| Tests (17 sept. 2026) | **les tests tournent en local seulement.** La suite ne tenait plus dans le délai d'un runner GitHub (coupée à 25 min, à 94 %, sans un juge tombé) et bloquait toutes les mises en ligne. La CI ne garde que les dépendances et le lint ; le verdict d'une livraison est la suite **complète**, navigateur compris, verte **en local** sur le commit exact poussé sur `main`. Voir [exploitation.md](exploitation.md), « Tests et CI ». |
| Missions mises en scène (16 sept. 2026) | **chaque mission vient avec ses animations et ses dialogues.** Une mission, c'est trois choses : ses objectifs, ses **répliques dites à voix haute** à chaque temps (appel, intro, pendant, fin, échec) et ses **scènes** (le donneur qui fait un geste, la caméra qui va voir où l'on s'en va, ce qu'on gagne qu'on voit arriver). Une mission à qui il en manque une **n'est pas finie**, et le juge du catalogue la refuse. Les scènes sont des **données** dans `missions.py`, écrites dans un vocabulaire de plans — jamais un script par mission. Voir [missions-en-scene.md](missions-en-scene.md), « Les missions mises en scène ». |
| Le jeu d'acteur (20 sept. 2026) | **les futures missions se jouent, elles ne se récitent pas.** Demande de Martin : de bonnes animations cinématiques, intéressantes, et de bonnes voix avec de l'émotion — « un bon jeu d'acteur ». Le savoir-faire est écrit dans `docs/jeu-d-acteur.md` : mettre une scène en images (l'image dit le *où*, la voix dit le *pourquoi* ; le geste tombe sur le mot ; le silence se joue dans la scène) et dire une réplique avec une intention, un arc et des balises v3. **Les juges vérifient le câblage, jamais le jeu : c'est Martin qui écoute.** Voir [missions-en-scene.md](missions-en-scene.md), « Le jeu d'acteur ». |

## La vision (tout ce qui est retenu)

Étiquettes : **v1** = première version complète ; **M9**…**M16** = le jalon qui le porte ; **risqué** = touche au moteur.

**Prémisse.** Tu es « Bandini », surnom hérité de ton oncle Rocco Bandini, petit bandit
mort en laissant un garage, une dette de 15 000 $ au shylock, une cachette et un téléphone
plein de contacts douteux, à **Baie-des-Brumes**, ville de port et de brouillard. Tu
débarques en autobus avec 50 $. Deux fins **M13** : _Le Boss_ (posséder les 4 propriétés,
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
Dr Lachance (urgentologue), Marco « Le Cousin » (veut sa part, te vendra en M13).

**Monde** : quartiers à police/véhicules/gangs propres · cycle jour-nuit (8 min) · intérieurs
(armurerie, vêtements, hôpital, garage clandestin, poste) · planque (sauvegarde, coffre,
stationnement) **v1** · fourrière, auto-stoppeurs, journal du matin **v1** · tramway,
traversier, tempête de neige avec charrue **M12, risqué**.

**Police** : cône de vision + ligne de vue · témoins qui courent avertir · recherche 1–5 ★
(1 : à pied ; 3 : autos ; 5 : barrages + hélico) · décroissance hors de vue, −1★ en
changeant de véhicule, remise à 0 en changeant de linge · arrestation au contact → prison :
amende, armes confisquées, casier · pot-de-vin (crime si refusé) · **alarmes de char** (3e
canal de détection), **acheter le silence** ou assommer le témoin, **le sergent qui mange**
(policier soudoyé devient ami), affiches « Recherché » **v1** · carnet du poste, le stool,
l'avocat du Carré **M11**.

**Combat** : poing, coup fort (projection), esquive · bâton, couteau, pistolet, fusil,
fronde, extincteur, munitions limitées, armes lâchées par les KO · armes improvisées qui
cassent, projeter dans le trafic **v1** · pompes à essence, bornes-fontaines **v1** ·
bouclier humain **M11, risqué**.

**Véhicules** : auto, moto (rapide, fragile, éjecte), camion, autobus, taxi, ambulance,
auto-patrouille (déguisement), bateau · dégâts, fumée, feu, explosion · garage qui répare
et repeint (la peinture efface le vol) · missions par véhicule au klaxon (taxi, ambulance,
pizza) · pourboire selon la douceur de conduite, cascades notées, rampes **v1** · radio
procédurale par véhicule, remorqueuse **M9**.

**Économie** : 50 $ de départ · taxi, livraisons, courses, revente au garage, cash au sol,
pickpocket **v1** · propriétés à revenu (kiosque 800 $, bar 2 500 $, garage 4 500 $, hôtel
10 000 $) · hôpital facturé · paquets cachés · guichets défoncés au camion et skimmers,
assurance et fraude, le shylock **M10**.

**Missions et narratif** : histoire par téléphone et PNJ, 5 missions v1 (voir plus bas),
3 défis · contacts du marché noir, la peur fait taire les témoins **v1** · **toutes les
répliques sont dites à voix haute** (ElevenLabs, une voix par personnage) en plus du texte
**v1** — voir « Les voix de l'histoire » ci-dessous · **chaque mission est mise en scène** :
des scènes animées à l'intro et à la fin, et une réplique à chaque temps, pendant compris —
voir « Les missions mises en scène ».

**Meta et présentation** : ~~tableau des scores en ligne~~ (**retiré du jeu** le
17 sept. 2026, à la demande de Martin — voir « Le tableau des scores s'en va ») · bilan de
session, caméra qui respire, visée assistée, GPS pointillé, options
(sang, palette daltonienne, vibration) **v1** · défi du jour à graine serveur, mode photo,
coop locale **à deux vrais joueurs** (un clavier, une manette) **M14** — la coop *en ligne*
n'est pas promise, mais le joint qui l'accueillerait est posé (une source d'entrées par
joueur, voir [plan.md](plan.md)).
