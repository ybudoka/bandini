# Charger les districts autour du joueur

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé le 30 sept. 2026 (Martin)._ C'est la dette que tous les juges de poids nomment depuis le 13 sept.
comme « le vrai remède » (`test_definitions::test_le_paquet_reste_leger`, [la carte sort du
paquet](la-carte-sort-du-paquet.md), [la ville s'agrandit au nord](la-ville-s-agrandit-au-nord.md), [le
paquet des définitions maigrit](le-paquet-des-definitions-maigrit.md)). Le paquet de la **carte**
(`/api/carte`) pèse **720 915 octets bruts / 70 538 gzip** pour un plafond de 71 000 : 462 octets de marge,
et c'est lui qui craquera le prochain. Le plafond a été relevé onze fois en quinze jours (41 → 71 Ko gzip).

### L'état actuel (mesuré le 30 sept. 2026)

- **Une requête, toute la ville** : `definitions.construire` signe `carte.exporter()` (459 × 414 tuiles,
  97 clés) ; `Jeu.chargerDefinitions` la remet dans `defs.carte`, `Monde.charger` en tire des tableaux
  typés pour toute la ville (solidité, route, passages), et `Jeu.commencer` crée **les 2 986 décors en
  entités** (`Entites.creerDecor`), dans l'ordre de la liste — leurs numéros (`suivantId`) en dépendent.
- **Ce qui pèse** (gzip de chaque clé seule) : `decor` 13 871, `sol` 9 556, `interieurs` 6 360, `arrets`
  2 948, `voie` 2 760, `lampes` 2 638, `devantures` 2 300, `portes` 2 093, `montagne_russe` 1 988,
  `residences` 1 690, `toits` 1 689, `autobus` 1 479, `feux_pietons` 1 298, `chantiers` 1 145, `legende`
  1 121 ; les 82 autres, moins de 1 050 chacune. En brut, `sol` et `voie` font 382 Ko sur 721.
- **Ce que le navigateur lit, et quand** (sonde au banc : un `Proxy` sur la carte, qui note la phase de la
  première lecture de chaque clé) : **32 clés au chargement** (`Monde.charger` : sol, voie, légende,
  portes, intersections, arrêts, lampes, décor, toits, façades…), 17 avant JOUER (autobus, traversier,
  train, neige…), 19 à JOUER (`commencer` : intérieurs, scènes, paquets, métro, foire…), 2 en roulant,
  2 à la carte plein écran, et quelques-unes seulement dans un cas rare (les sentiers de La Pointe la nuit,
  les jeux de la foire). **Huit ne sont lues par aucun script** (`decor_solide`, `flottants`, `ponts`,
  `relief`, `tuiles_bouchees`, `graine`, `lave_auto`, `tuile_px` : 684 octets gzip en tout ; deux sont des
  contrats que des juges comparent au JS — trop peu pour une vague à elles).
- **Ce que ça coûte au démarrage** (sonde Chromium, processeur ralenti ×4 pour faire « un téléphone »,
  médiane de cinq) : écran titre à **1 378 ms**, dont **319 ms** entre la dernière réponse et le titre ;
  le `JSON.parse` de la carte n'en prend que **12 ms**. Au banc Node : `Monde.charger` 8 ms, `commencer`
  63 ms. ⚠️ **Le coût de la carte au démarrage est sur le fil, pas dans le processeur** : ce qu'on gagnera
  se compte en octets téléchargés, pas en millisecondes de calcul.

### Les options

1. **Plier la carte** (une meilleure représentation, sans perte) : les listes d'objets de même forme
   voyagent **en colonnes** (une colonne par champ ; les entiers en écarts, les chaînes répétées en palette),
   les dictionnaires « x,y » en deux colonnes. Le navigateur la **déplie** en arrivant, avant que quoi que ce
   soit la lise : aucun lecteur ne change, la ville est la même à l'octet près (JSON comparé). Mesuré :
   **70 538 → 52 004 gzip, 721 → 539 Ko bruts**. Coût : un module de chaque côté (plier, déplier) et leurs
   juges. Risque : un déplieur qui ne rend pas exactement la ville — un juge le compare à l'octet près,
   côté Python et côté navigateur.
   Le sol, lui, ne gagne presque rien : transposé −1 %, RLE −3 %, delta vertical +7 % ; gzip le fait déjà.
2. **Ce qui attend sort de la carte** : `interieurs` (6,4 Ko gzip) n'est lu qu'à JOUER et en passant une
   porte ; il peut voyager à part, demandé juste après la carte en arrière-plan et gardé dans la coquille,
   comme les notes et la suite (et une porte passée avant son arrivée attend dans son fondu, comme un bloc
   de carte). Risque : les lecteurs de `commencer` (métro, histoire, halloween) doivent attendre, ou
   l'intérieur doit arriver avant JOUER.
3. **Un squelette et des morceaux par district** : toute la ville garde son squelette (sol, voie, légende,
   portes, intersections, arrêts, zones, points — ce que la physique, le A*, le GPS, la carte N et les
   missions lisent partout), et **ce qui ne sert qu'à peindre ou à toucher de près** (décor, lampes, toits,
   façades, graffitis, feux piétons ≈ 13 Ko gzip une fois plié) arrive par district autour du joueur.
   Coûts et risques, et ils sont lourds :
   - **les numéros d'entités** : le décor naît à JOUER dans l'ordre de la liste ; né par district, il
     décale tout ce qui naît après (mémoire « Décor eager décale les identifiants ») — il faudrait réserver
     les numéros par position dans la liste, ou tout le décor `enDehorsDeLaSuite` ;
   - **ce qui lit le décor loin du joueur** : les guichets et distributrices des missions, les lits de la
     carte, les châteaux de sable, la foire, les juges « le premier X de la ville » ;
   - **la pose relative au joueur** et `Histoire.lieu` : une mission qui pose près d'un décor d'un district
     pas encore arrivé ;
   - **le rendu** : un morceau (16 × 16 tuiles, `Monde.morceaux`) cuit avant l'arrivée de son district
     serait à recuire ; le téléport du debug (ALLER, ENDROITS CLÉS), le traversier, le train et l'autobus
     sautent loin d'un coup — il faut un fondu qui attend, comme les blocs ;
   - **hors ligne** : la coquille doit garder chaque district ;
   - **les centaines de juges** qui supposent la ville entière en mémoire.
   Gain : environ 10 Ko gzip au démarrage (les districts loin du joueur), et l'assurance que la ville peut
   encore grandir sans que le premier chargement grandisse avec.
4. **Découper par district TOUTE la carte, sol compris** : le squelette lui-même par morceaux. Le A* des
   agents et du GPS, la carte plein écran et les rues des autobus lisent toute la ville ; il faudrait un
   squelette de secours. Rien ne le justifie tant que le sol plié tient en 10 Ko.

### Le découpage en vagues (chacune livrable et verte seule)

- **Vague 1 — la carte voyage pliée** (option 1). Aucun lecteur ne change. `app/pliage.py` plie à la
  signature de `/api/carte` ; `static/js/pliage.js` déplie dans `Jeu.chargerDefinitions`, avant `defs.carte =
  carte`. Juges : Python `deplier(plier(ville)) == ville` ; le déplieur du navigateur rend la carte **à
  l'octet près** (le JSON de la carte dépliée au banc Node égale celui de `carte.exporter()`) ; le banc sert
  la carte **pliée**, comme le serveur, donc tous les juges JS jouent sur la ville dépliée ; le jeu hors ligne
  (Chromium réseau coupé) ; une **garde par clé** sur la carte (`MESURE_DE_LA_CARTE`, comme
  `MESURE_DU_PAQUET`) ; le plafond redescend à la nouvelle mesure plus une marge. Sonde de performance
  avant et après.
- **Vague 2 — le fil compressé une fois, au plus fort** (trouvé en mesurant la vague 1). ⚠️ Les juges comptent
  le gzip au niveau 6, mais **nginx compresse au niveau 1** (`deploy/nginx`, aucun `gzip_comp_level`) : sur
  le vrai fil, la carte pesait **98 091** octets (71 755 une fois pliée) et les définitions 62 773. Compressés
  UNE fois par l'application, au niveau 9, à la construction des paquets (`Content-Encoding: gzip` quand le
  navigateur l'accepte — nginx et Caddy ne recompressent pas une réponse déjà encodée) : **50 069** pour la
  carte, **52 610** pour les définitions, sans rien changer au jeu. À vérifier en ligne par Martin (le `curl`
  de `deploy/README.md`).
Les vagues 3 à 5 de ce premier découpage sont **révisées** le 1er oct. 2026 : voir plus bas.

### La remesure (1er oct. 2026) : ce sont les scripts

_Avant de prendre la vague 4 (Martin l'avait choisie), la mesure qu'elle demandait : le démarrage sous Chromium
comme sur un téléphone, et pas seulement le poids de la carte._ La sonde : Chromium derrière un faux « Caddy +
nginx » local (HTTP/2 sur TLS comme la prod, gzip au niveau 1 comme nginx sans `gzip_comp_level`, `expires 7d`
sur `/static/`), processeur ralenti ×4, réseau « 3G rapide » de DevTools (562,5 ms d'aller-retour, 180 Ko/s),
travailleur hors ligne bloqué, médiane de trois, à `bd8f4b96` (0.393.0). La machine était très chargée (load
30, d'autres sessions) : le ralentissement simulé domine, les passages ne s'écartent que de 1 %.

| Visite | Écran titre | Dont les scripts | Octets sur le fil | JOUER → la ville |
|---|---|---|---|---|
| **Première visite** (cache vide) | **12 625 ms** | arrivés à 10 137 ms, exécutés à 11 238 | 1 679 321, dont **1 561 400 de scripts** | 309 ms |
| **Après une mise en ligne** (la version change) | **12 042 ms** | retéléchargés TOUS : 1 561 400 octets | 1 571 088 | 305 ms |
| Deuxième visite, même version | 2 630 ms | du cache (0 octet), exécutés à 1 855 | 600 (deux 304) | 302 ms |

- **Les scripts font 93 % de ce qui voyage avant l'écran titre.** 87 fichiers, 4 043 789 octets bruts, très
  commentés : **1 535 300 sur le fil** au niveau 1 de nginx (mesuré en ligne à 0.391.23 : 1 532 944), 1 297 114
  au niveau 9, 1 137 433 en brotli. La carte (53 121) et les définitions (55 712) font ensemble 108 Ko.
- **Une mise en ligne coûte autant qu'une première visite** : chaque script porte `?v=<version>`, la version monte
  à chaque `feat:`/`fix:`, et les 87 adresses changent — même celles des fichiers qui n'ont pas bougé d'un octet.
  C'est le cas de tous les jours sur le téléphone de Martin (il met en ligne plusieurs fois par jour).
- **Les définitions et la carte attendent les scripts** : elles ne partent qu'une fois les 87 exécutés
  (`Jeu.demarrer`, au `DOMContentLoaded`) — un aller-retour (0,56 s) et 108 Ko (0,6 s) APRÈS les scripts : de
  11 252 à 12 437 ms à froid, et deux 304 de 590 ms à chaud.
- **JOUER → la ville : 0,3 s** (`commencer()` 184 ms, la première image 125 ms de plus), à froid comme à chaud.
  Le déclencheur écrit depuis M8 (« plus de 2 s entre JOUER et la ville ») n'est pas là : **l'attente est avant
  l'écran titre**, pas après JOUER.
- **Ce que la carte pèse encore**, clé par clé (gzip 9 de chaque clé seule, la carte pliée : 561 155 bruts,
  52 821 gzip) : `sol` 9 318, `interieurs` 7 609, `decor` 7 098, `devantures` 2 015, `montagne_russe` 1 982,
  `voie` 1 944, `portes` 1 600, `lampes` 1 479, `residences` 1 349, `autobus` 1 278 ; les 74 autres, moins de
  1 220 chacune. **Les définitions** (247 350 bruts, 55 412 gzip, 66 clés) : `audio` 7 478, `pietons` 5 211,
  `defis` 4 078, `economie` 4 006, `garderobe` 3 553, `missions` 3 225, `personnages` 3 105, `saisons` 2 116,
  `vehicules` 1 990 ; les 57 autres, moins de 1 900 chacune.
- **Ce que les vagues 3 et 4 d'avant auraient acheté** : les pièces à part, 7,6 Ko gzip (≈ 40 ms en 3G rapide) ;
  le décor, les lampes, les toits et les façades par district, ≈ 10 Ko (≈ 55 ms) — sur douze secondes. Les
  scripts sans leurs commentaires ni leur indentation (ligne pour ligne, essayé sur les 87 : `node --check` et
  esbuild les tiennent pour le même code) : **627 492 octets au niveau 9, 749 512 au niveau 1** — 785 Ko de
  moins sur le fil que la carte et les définitions ensemble, onze fois.

### Le découpage révisé (1er oct. 2026)

D'abord ce qui achète le plus de secondes au démarrage pour le moins de risque. Les vagues 1 et 2 restent
livrées ; les vagues 3 et 4 d'avant passent derrière (6 et 7), en attente : elles achètent moins de 0,1 s.

- **Vague 3 — les scripts à l'empreinte de leur contenu.** Chaque adresse statique porte `?v=<empreinte de SON
  fichier>` au lieu de la version du site (`app/statiques.py`) : après une mise en ligne, seuls les scripts qui
  ont changé repartent, et le cache du navigateur (nginx les garde sept jours) rend les autres sans rien
  demander. Gain : une mise en ligne coûte ce qu'elle a changé au lieu de 1,56 Mo. Risque faible : la liste
  reste lue dans le gabarit (`filename='js/…'`) par le banc, la barre et la coquille hors ligne ; l'empreinte se
  relit quand un fichier change sous le serveur de dev. Juges : chaque adresse porte l'empreinte de son fichier ;
  deux versions du site, les mêmes adresses ; un fichier changé ne change que la sienne. A/B : la visite après
  une mise en ligne.
- **Vague 4 — les scripts maigrissent.** Servis sans commentaires ni indentation, **ligne pour ligne** (une erreur
  nomme toujours la bonne ligne du source) : 1 535 → 750 Ko sur le fil au niveau 1 de nginx, 627 Ko si Martin
  pose `gzip_static on` (le déploiement écrit le `.gz` au niveau 9 à côté). Un seul maigrisseur (Python) sert
  partout : `deploy.sh` l'applique à la release, le serveur de dev sert les mêmes octets, et **le banc d'essai joue
  les scripts maigres** — tous les juges JS et Chromium jugent ce que le téléphone reçoit. Risque : un
  maigrisseur qui changerait le sens (une expression régulière prise pour une division, un gabarit `` ` `` sur
  plusieurs lignes) — juges : chaque script maigre se compile (`node --check`), garde son nombre de lignes, ne
  garde aucun commentaire, et les cas pièges un par un ; et le banc entier qui joue sur eux. Gain attendu ≈ 4 s
  à froid et après une mise en ligne.
- **Vague 5 — les paquets partent avec les scripts.** Les définitions et la carte se préchargent dès le haut de
  la page (`<link rel="preload" as="fetch">`), pendant que les scripts arrivent et s'exécutent ; `Jeu.demarrer`
  reprend la même réponse, et sans préchargement (un vieux navigateur, le banc) il la demande comme avant. Gain
  attendu ≈ 1 s à froid (l'aller-retour et les 108 Ko qui suivaient les scripts), ≈ 0,6 s à chaque visite (les
  deux 304 pendant l'exécution des scripts). Juges : la page précharge exactement les deux adresses que le jeu
  demande (sinon le navigateur les télécharge deux fois) ; Chromium : une seule requête par paquet, la ville
  s'ouvre, hors ligne compris.
- **Vague 6 — les pièces voyagent à part** (l'ancienne vague 3, option 2) : en attente. 7,6 Ko gzip, ≈ 40 ms en
  3G rapide, et beaucoup de lecteurs à faire attendre ; à reprendre si le plafond de la carte cède. Le texte
  d'avant, pour le jour où on la reprend :
  « ⚠️ **Elle n'achète presque rien au démarrage tant que
  les définitions pèsent autant que la carte** : les deux requêtes partent ENSEMBLE, et c'est la plus lourde
  qui fait attendre le titre — après la vague 1, la carte (52 129) et les définitions (52 993) sont à égalité.
  Les lecteurs sont nombreux (`Jeu.entrer` refuse une porte sans sa pièce, `Histoire` pose dans les pièces,
  le métro, l'Halloween, une partie sauvée dedans), et chacun devrait attendre. À prendre quand les
  définitions auront maigri, ou si le plafond de la carte cède avant. Preuve au banc : une porte passée avant
  l'arrivée des pièces attend dans son fondu, jamais un trou. »
- **Vague 7 — le squelette et les morceaux par district** (l'ancienne vague 4, option 3) : ⚠️ **en attente d'une
  décision de Martin.** Elle achète ≈ 10 Ko (≈ 55 ms en 3G rapide) pour le plus gros risque du jalon (les
  numéros d'entités, la pose relative, les blips, le hors ligne, des centaines de juges). Son déclencheur
  révisé : le plafond de la carte pliée (55 000) qui cède, ou une ville qui double. Preuve au banc obligatoire le
  jour venu : conduire vite d'un bout à l'autre de la ville et se téléporter par le debug sans jamais voir un
  morceau vide ; les numéros d'entités identiques à ceux d'avant (le premier numéro libre après `commencer()`).
- **Vague 8** (option 4) : pas prévue ; écrite pour qu'on ne la reprenne pas sans raison.

## Notes

**Vague 1 — la carte voyage pliée (30 sept. 2026).** `app/pliage.py` plie la ville à la signature de
`/api/carte` (`definitions.construire`) ; `static/js/pliage.js` la déplie dans `Jeu.chargerDefinitions`, avant
`defs.carte`. Aucun lecteur n'a changé, la génération non plus (`carte.generer` n'est pas touché).

- **Le poids** : **720 915 → 539 632 octets bruts, 70 538 → 52 129 gzip** (niveau 6, celui des juges) ; au
  niveau 1 de nginx, le vrai fil : 98 091 → 71 755. Le décor seul : 13 871 → 7 054 ; les arrêts 2 948 → 969 ;
  les feux piétons 1 298 → 383 ; les sentiers de La Pointe 999 → 189. Le sol (9 556) et les voies (2 760)
  n'ont pas bougé : rien ne les plie mieux que gzip.
- **Les plafonds de la carte descendent** : 722 000 → **560 000** bruts, 71 000 → **55 000** gzip (2 871 octets
  de marge, six fois celle d'avant) ; et **une garde par clé** (`MESURE_DE_LA_CARTE`,
  `test_chaque_cle_de_la_carte_tient_son_budget`) : une clé neuve de la carte s'y écrit avec son poids, une clé
  qui dépasse son budget rougit en se nommant, et le plafond qui cède nomme les trois clés qui ont grossi.
- ⚠️ **Deux pièges vus en chemin, que les juges tiennent** : (1) les arrêts (`"x,y"` → sens) se pliaient dans
  l'ordre d'INSERTION du dictionnaire Python, alors que le JSON d'avant les triait — le navigateur les
  rebâtissait dans un autre ordre, et `Object.keys(arrets)` aussi ; seul le juge « à l'octet près » sous Node
  l'a vu. (2) La légende a une clé `~` (l'eau) : une marque de pli est une clé ENTIÈRE (`~t`, `~p`, `~xy`),
  jamais un préfixe, et `plier` refuse une carte qui en porterait une.
- **Le banc sert la carte PLIÉE**, comme le serveur (`conftest.carte_pliee`) : tous les juges JS jouent sur la
  ville dépliée par le navigateur (et l'entrée de chaque banc a maigri de 180 Ko).
- **La performance** (sonde Chromium, processeur ×4, `service_workers: block`, base et vague 1 en alternance ;
  la machine était chargée — d'autres sessions — alors seuls les écarts comptent) : écran titre 1 761 / 1 730 ms
  (base) contre 1 779 / 1 735 ms ; bâtir la ville après la dernière réponse 499 / 473 contre 471 / 475 ;
  `JSON.parse` de la carte 16,4 / 17,3 contre 14,1 / 13,6 ms ; JOUER → la ville et le temps d'une image,
  pareils (bruit). Sous Node : `JSON.parse` de la carte entière 2,21 ms, de la carte pliée 1,34, pliée et
  dépliée 3,04 — le dépliage coûte moins d'une milliseconde. ⚠️ **Le gain est sur le fil**, pas dans le
  processeur : c'est ce que le téléphone de Martin doit dire (la dette « plus de 2 s entre JOUER et la ville »).
- **Juges** : `test_pliage.py` (huit : chaque pli et chaque refus de plier, sans rien toucher en place, la
  marque refusée, la ville qui voyage dépliée à l'octet près contre `assembler()`, le poids, le déplieur du
  navigateur sur chaque cas et sur la ville entière — `JSON.stringify` à l'octet près, l'ordre des clés compris —,
  et le jeu au banc qui reçoit la carte pliée et tient la ville dépliée). Ils MORDENT : les arrêts pliés dans
  l'ordre d'insertion → deux rouges ; les écarts non cumulés dans le déplieur → trois rouges. Verts à côté :
  `test_definitions`, `test_moteur_js`, `test_carte`, `test_reproductible`, `test_nord`, `test_nord_js`,
  `test_canton`, `test_debug_js`, `test_hors_ligne` (le jeu réseau coupé compris), `test_navigateur` (dix
  rouges sous la charge de la machine, tous verts rejoués seuls), `test_routes`, `test_collections`,
  `test_collections_js`, `test_blocs`, `test_blocs_js`, `test_suite_js`, `test_comptes`, `test_chargement_js`,
  `test_monde_js`, `test_table_des_jalons`.

**Vague 2 — le fil compressé une fois, au plus fort (30 sept. 2026).** `Paquet.fil` : le corps compressé au
niveau 9 (`mtime=0`, les mêmes octets à chaque construction), une fois, à la première demande ;
`routes._revalide` l'envoie avec `Content-Encoding: gzip` à tout navigateur qui accepte gzip (`Vary:
Accept-Encoding`, `X-Octets` toujours la taille décompressée pour la barre), et le JSON tel quel aux autres.
Toutes les routes des paquets en profitent : définitions, carte, notes, suite, collections, missions, blocs.

- **Sur le fil** (mesuré dans Chromium : `encodedBodySize`) : la carte **50 041** octets, les définitions
  **52 614**. Avant, derrière nginx au niveau 1 : la carte 98 091 (avant la vague 1), 71 755 (après), les
  définitions 62 773. Les deux requêtes partent ensemble : **160 864 → 102 655 octets** avant l'écran titre
  (−36 %). À la main, pour un réseau « 3G rapide » (1,6 Mbit/s) : ≈ 0,80 s → 0,51 s de téléchargement.
  (Calcul, pas une mesure : le banc local n'a pas de nginx.)
- ⚠️ **À vérifier en ligne par Martin, après la mise en ligne** : `curl -s -A navigateur -H 'Accept-Encoding:
  gzip' https://bandini.gestiondojo.ca/api/carte | wc -c` doit dire ≈ 50 000 (`deploy/README.md`). nginx (`gzip
  on`) et Caddy (`encode`) ne recompressent pas une réponse qui porte son `Content-Encoding` — c'est leur
  comportement documenté, mais la chaîne de production n'a pas pu être essayée d'ici. L'ETag reste fort
  (nginx ne le touche plus) ; `contains_weak` revalide les deux.
- **La performance** (même sonde, machine toujours chargée) : titre 1 692 ms, bâtir la ville 473 ms,
  `JSON.parse` de la carte 13,3 ms, image 16,3 ms — le bruit de la vague 1 ; le processeur ne paie rien de plus
  (le navigateur décompressait déjà ce que nginx compressait).
- **Juges** : `test_routes` (les sept routes de paquets partent compressées, le même JSON à l'octet près, 304
  intact, `Vary`, la taille décompressée ; un client sans gzip — ou `gzip;q=0` — reçoit le JSON ; le fil est le
  niveau 9, déterministe), `test_navigateur::test_les_paquets_arrivent_compresses_par_le_serveur` (un vrai
  navigateur les reçoit compressés, les octets EXACTS de `Paquet.fil` — un intermédiaire qui recompresse se
  verrait —, la barre, et la ville s'ouvre). Ils MORDENT : la branche gzip coupée → deux rouges ; le niveau 6 au
  lieu de 9 → rouge. Verts à côté : `test_hors_ligne` (le jeu réseau coupé compris), `test_navigateur` (46),
  `test_comptes`, `test_blocs`, `test_collections`, `test_definitions`, `test_pliage`. ⚠️ Vérifié en passant :
  la carte truquée de `test_une_carte_d_une_autre_construction_est_refusee` est refusée pour la bonne raison
  (« carte 0000… au lieu de … »), pas pour un corps mal décodé.

**Vague 3 — les scripts à l'empreinte de leur contenu (1er oct. 2026).** `app/statiques.py` (`Empreintes`) : chaque
adresse statique de la page (les 87 scripts, la feuille, les icônes, le logo) porte `?v=<sha256 court de SON
fichier>` au lieu de `?v=<version du site>` ; le gabarit l'écrit `statique(filename='js/…')`, et garde ainsi le
texte que le banc, la barre (`routes._scripts_du_jeu`) et la coquille hors ligne lisent. L'empreinte se relit
quand le fichier change sous le serveur (date et taille) : le serveur de dev change maintenant le `?v=` d'un
script qu'on édite.

- **La mesure** (la sonde de la remesure, A/B apparié base `bd8f4b96` contre la vague 3, en alternance, deux
  passages chacun, « une mise en ligne » = le serveur relancé sous une autre version, les mêmes fichiers) :
  écran titre **12 007 → 2 634 ms**, scripts sur le fil **1 561 400 → 0 octet** ; JOUER → la ville, pareil
  (312 / 303 ms). Une mise en ligne qui touche des scripts fait repartir ceux-là seulement : entre 0.391.23 (en
  ligne) et `dev` aujourd'hui, 7 scripts sur 87 ont changé — mais ce sont les plus gros (`sprites`, `entites`,
  `hud`, `monde`, `son`, `combat`, `explosions`) : 617 654 octets au lieu de 1 535 300. D'où la vague 4.
- **Juges** (`test_routes.py`) : chaque adresse statique de la page porte l'empreinte de son fichier, et la
  version n'y paraît plus ; deux versions du site rendent les mêmes adresses, à l'octet près ; un fichier changé
  sous le serveur change SON empreinte, pas celle de l'autre. Ils MORDENT : la version remise à la place de
  l'empreinte → deux rouges. Verts à côté : `test_hors_ligne` (le jeu réseau coupé compris), `test_navigateur`,
  `test_carte_du_depot`, `test_table_des_jalons`, `test_version`, `test_chargement_js`, `test_comptes` ; ruff.

**Vague 4 — les scripts maigrissent (1er oct. 2026).** `statiques.maigrir` : le script sans ses commentaires ni son
indentation, **ligne pour ligne** (le même nombre de lignes, chaque instruction sur la sienne — une erreur nomme
toujours la bonne ligne du source, et les points-virgules automatiques voient les mêmes fins de ligne). Les
chaînes, les expressions régulières et le texte des gabarits `` ` `` (indentation comprise) passent tels quels ;
la seule ambiguïté — une barre oblique divise-t-elle ou ouvre-t-elle une expression régulière ? — se tranche par
le jeton d'avant, l'en-tête d'un `if`/`while`/`for` compris. Un script que le maigrisseur ne sait pas lire est
refusé (`ScriptIllisible`), jamais changé. Un seul maigrisseur, servi partout :

- **en ligne** : `deploy.sh` maigrit la release avant la bascule (`python app/statiques.py`), et pose à côté de
  chaque script son `.gz` au niveau 9 ; nginx sert `/static/` lui-même. ⚠️ **`gzip_static on`** dans le
  `location /static/` du vhost (`deploy/nginx/…example`) lui fait servir ces `.gz` au lieu de compresser au
  niveau 1 : une ligne à poser à la main sur le serveur (Martin), qui n'est pas nécessaire pour que ça marche ;
- **le serveur de dev et les juges Chromium** reçoivent les mêmes octets (`Maigres`, branché sur la vue
  `static` par `create_app`, relu quand un script change) ;
- **le banc d'essai joue les scripts maigres** (`conftest.scripts_servis`, `ENTREE.scripts`) : les milliers de
  juges JS jugent ce que le téléphone exécute.

- **Le poids** (87 scripts) : 4 048 017 → 2 225 342 octets bruts ; sur le fil **1 535 300 → 749 512** au niveau 1
  de nginx, **628 102** au niveau 9 (`gzip_static`). `jeu.js` seul : 37 385 → 13 573 (11 415).
- **La mesure** (la sonde de la remesure, A/B apparié vague 3 contre vague 4, en alternance, trois passages
  chacun, première visite) : écran titre **12 612 → 8 214 ms** (−4,4 s), scripts arrivés à 10 138 → 5 767 ms,
  scripts sur le fil 1 562 784 → 776 813 octets ; JOUER → la ville, pareil (300 / 320 ms, le bruit). Le
  processeur n'y gagne presque rien (tâches longues avant le titre : 1 405 / 1 392 ms) : le gain est sur le fil.
  Avec `gzip_static on` (la sonde au niveau 9, deux passages, pas apparié) : **7 585 ms**, 654 636 octets de
  scripts — 0,6 s de moins encore, pour une ligne de nginx.
- **Vérifié hors des juges** : esbuild (`--minify-whitespace`) rend, pour chacun des 87 scripts, exactement le
  même code de la source et du script maigre — un second lecteur de JavaScript, indépendant du nôtre.
- **Juges** : `test_statiques.py` — treize pièges joués sous Node, maigres ou pas, la même sortie (chaînes et
  gabarits qui portent `//` et `/*`, expressions régulières à barres obliques, après `return` et après l'en-tête
  d'un `if`, divisions après une parenthèse, un crochet, un nombre, gabarits imbriqués, points-virgules
  automatiques et `return` seul sur sa ligne, continuation de chaîne, commentaire collé `a/**/-/**/b`) ; un
  script illisible refusé ; les 87 scripts de la page maigrissent, gardent leurs lignes, maigrissent une seconde
  fois sans rien changer et se compilent (`vm.Script`) ; moins de 55 % du poids gzip ; le serveur les sert
  maigres (304 compris), le reste de `static/` tel quel ; le déploiement les écrit avec leur `.gz` (décompressé
  = le script maigre), refaire ne change rien, le travailleur n'est pas touché, et `deploy.sh` maigrit AVANT la
  bascule. `test_statiques_js.py` — le banc joue les scripts maigres (`Jeu.demarrer` sans ses ⚠️, ses lignes
  à leur place). Ils MORDENT, huit mutations, huit rouges : le banc qui lit les sources, le serveur qui sert les
  sources, le gabarit pris pour du code, l'en-tête du `if` oublié, un commentaire de bloc qui mange ses lignes,
  `return` suivi d'une division, `deploy.sh` sans l'étape, le `.gz` oublié.

**Vague 5 — les paquets partent avec les scripts (1er oct. 2026).** La page précharge les définitions et la carte
dès son `<head>` (`<link rel="preload" as="fetch" crossorigin>`, `{% block tete %}` de `base.html`) : elles
voyagent pendant que les 87 scripts arrivent et s'exécutent, et le `fetch()` de `Jeu.chargerDefinitions` reprend
la réponse déjà là — aucune ligne du jeu n'a changé. Sans préchargement (un vieux navigateur, le banc d'essai), il
la demande comme avant. ⚠️ Les trois conditions pour que le navigateur rende le préchargement au `fetch()` : la
MÊME adresse (l'empreinte `?e=` comprise), `as="fetch"`, et `crossorigin` — sans ce dernier, Chromium télécharge
tout deux fois (vu en mutation).

- **La mesure** (A/B apparié vague 4 contre vague 5, trois passages chacun) : première visite, écran titre
  **8 234 → 7 672 ms** (les deux paquets demandés à 595 ms au lieu de 6 864 ; les scripts finissent un peu plus
  tard, 6 386 contre 5 772 ms, la bande passante est partagée, mais il ne reste après eux que 212 ms pour bâtir la
  ville) ; deuxième visite, **2 636 → 2 052 ms** (les deux 304 pendant l'exécution des scripts au lieu d'après).
  Une seule requête par paquet, les mêmes octets.
- **Juges** : `test_routes.py` — la page précharge exactement les deux adresses que le jeu demande (`data-url-…`),
  dans le `<head>`, `as="fetch" crossorigin`, et rien d'autre ; `test_navigateur.py` — sous Chromium, les deux
  paquets sont demandés AVANT le `DOMContentLoaded`, une seule fois chacun, sans avertissement de préchargement
  perdu, et la ville s'ouvre. Ils MORDENT : sans `crossorigin` → deux requêtes par paquet, rouge ; sans
  préchargement → demandés après le `DOMContentLoaded` (1 004 ms contre 767), deux rouges. Verts à côté :
  `test_hors_ligne` (la coquille garde les mêmes adresses, le jeu réseau coupé compris), `test_routes`.

**Le démarrage, avant et après les vagues 3 à 5** (la sonde de la remesure, A/B apparié `bd8f4b96` contre la
vague 5, en alternance, trois passages — deux pour la mise en ligne, où le serveur est relancé sous une autre
version, les mêmes fichiers) :

| Visite | `bd8f4b96` (avant) | après la vague 5 | Scripts sur le fil |
|---|---|---|---|
| Première visite | 12 612 ms | **7 658 ms** | 1 561 400 → 776 814 octets (654 636 avec `gzip_static`) |
| Après une mise en ligne qui ne touche aucun script | 11 983 ms | **2 023 ms** | 1 561 400 → 0 octet |
| Deuxième visite | 2 621 ms | **2 015 ms** | 0 |
| JOUER → la ville | 310 ms | 302 ms | — |

Une vraie mise en ligne fait repartir les scripts qu'elle a touchés, maigres : entre 0.391.23 (en ligne
aujourd'hui) et `dev`, sept scripts, les plus gros — 281 690 octets au lieu de 1 535 300 (≈ 1,6 s en 3G rapide au
lieu de ≈ 8,5).

**Ce qui reste.** Les vagues 3 à 5 du découpage révisé sont livrées. Les pièces à part (vague 6, ≈ 40 ms) et le
squelette par district (vague 7, ≈ 55 ms, le plus gros risque du jalon) attendent : **le second, une décision de
Martin** — après les vagues 3 à 5, la carte et les définitions font 108 Ko sur 885 à la première visite, et
plus rien après une mise en ligne qui ne les change pas. Ce qui pèserait encore, s'il faut aller plus loin : les
scripts eux-mêmes (777 Ko maigres ; brotli en ferait ≈ 520, mais ni nginx ni Python ne l'ont sans paquet en plus),
et leur exécution (≈ 1,1 s de processeur ×4 à chaque visite, que rien ici n'a touché). ⚠️ **À poser sur le
serveur par Martin** (facultatif, 0,6 s de plus en 3G rapide à la première visite) : `gzip_static on;` dans le
`location /static/` du vhost nginx (`deploy/nginx/bandini-gestiondojo.conf.example`), puis `sudo nginx -t && sudo
systemctl reload nginx`. ⚠️ Le téléphone de Martin est le seul juge qui manque : la sonde simule un réseau et un
processeur, pas les siens.
