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
- **Vague 2 — les pièces voyagent à part** (option 2), si la marge rendue par la vague 1 ne suffit pas ou
  que le premier chargement sur le téléphone le demande. Preuve au banc : une porte passée avant l'arrivée
  des pièces attend dans son fondu, jamais un trou.
- **Vague 3 — le squelette et les morceaux par district** (option 3). ⚠️ C'est le vrai remède, et le plus
  cher : son **déclencheur** reste celui de la dette (« plus de 2 s entre JOUER et la ville sur le téléphone
  de Martin »), ou le plafond de la carte pliée qui cède à son tour. Preuve au banc obligatoire : conduire
  vite d'un bout à l'autre de la ville et se téléporter par le debug sans jamais voir un morceau vide ; les
  numéros d'entités identiques à ceux d'avant (le premier numéro libre après `commencer()`).
- **Vague 4** (option 4) : pas prévue ; écrite pour qu'on ne la reprenne pas sans raison.
