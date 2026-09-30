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
- **Vague 3 — les pièces voyagent à part** (option 2). ⚠️ **Elle n'achète presque rien au démarrage tant que
  les définitions pèsent autant que la carte** : les deux requêtes partent ENSEMBLE, et c'est la plus lourde
  qui fait attendre le titre — après la vague 1, la carte (52 129) et les définitions (52 993) sont à égalité.
  Les lecteurs sont nombreux (`Jeu.entrer` refuse une porte sans sa pièce, `Histoire` pose dans les pièces,
  le métro, l'Halloween, une partie sauvée dedans), et chacun devrait attendre. À prendre quand les
  définitions auront maigri, ou si le plafond de la carte cède avant. Preuve au banc : une porte passée avant
  l'arrivée des pièces attend dans son fondu, jamais un trou.
- **Vague 4 — le squelette et les morceaux par district** (option 3). ⚠️ C'est le vrai remède, et le plus
  cher : son **déclencheur** reste celui de la dette (« plus de 2 s entre JOUER et la ville sur le téléphone
  de Martin »), ou le plafond de la carte pliée qui cède à son tour. Preuve au banc obligatoire : conduire
  vite d'un bout à l'autre de la ville et se téléporter par le debug sans jamais voir un morceau vide ; les
  numéros d'entités identiques à ceux d'avant (le premier numéro libre après `commencer()`).
- **Vague 5** (option 4) : pas prévue ; écrite pour qu'on ne la reprenne pas sans raison.

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

**Ce qui reste.** La vague 3 (les pièces à part) n'achète presque rien tant que les définitions pèsent autant
que la carte sur le fil (50 et 52 Ko, les deux en même temps). La vague 4 (le squelette et les morceaux par
district) garde son déclencheur : « plus de 2 s entre JOUER et la ville sur le téléphone de Martin », ou le
plafond de la carte pliée (55 000) qui cède. ⚠️ Le téléphone de Martin est le seul juge qui manque : la sonde
ralentit le processeur ×4, elle ne sait rien de son réseau.
