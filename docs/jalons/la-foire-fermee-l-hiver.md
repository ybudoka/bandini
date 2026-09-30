# La foire fermée l'hiver, et le tour de ce qui ferme

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « la foire, fermée l'hiver. Et fais le tour des choses qui devraient l'être. »
Mesuré : rien de la foire ne lit la saison (les manèges roulent, l'orgue joue, la foule et les mascottes
naissent en janvier) ; ni le derby, ni le camion de crème glacée, ni la cabane de fruits de mer, ni les
amuseurs de rue, ni les piscines hors terre (de l'eau bleue sous la neige), ni la fontaine, ni le BBQ, ni
les chaloupes amarrées. Ce qui fermait déjà : le ciné-parc, la cabane à sucre, les terrasses, les motos et
les vélos. La plage a sa propre ligne ([la plage l'hiver](la-plage-l-hiver.md)).

Tranché par Martin :

- **Quand** : hors hiver — fermée tant que la neige tient (`Saisons.enHiver()`), du premier banc de
  décembre au dégel de la fin mars ; ouverte du printemps à l'automne.
- **Ce qu'on voit** : cadenassée. L'arche fermée (« FERMÉ POUR L'HIVER »), les manèges immobiles sous la
  neige, les kiosques les volets baissés, tout éteint et muet, ni foule ni mascotte, on ne monte à rien.
- **Les missions du Bonimenteur** (la caisse de l'arche, la taxe des Skateux) attendent : l'hiver, il
  n'est pas à sa foire ; elles viennent quand elle ouvre. Le parcours de Zed, qui passe à l'arche, reste
  jouable. Les défis de la foire (tir, marteau, canards, anneaux…) attendent aussi.
- **Le tour** — ferment aussi l'hiver : le derby de démolition, le camion de crème glacée (remisé, sa
  ritournelle avec), la cabane de fruits de mer ; les amuseurs de rue (musicien, jongleur, échassier,
  amuseur) ne sortent plus et rentrent hors champ ; les piscines hors terre bâchées sous la neige, la
  fontaine de la place à sec, le BBQ remisé ; les chaloupes sorties de l'eau (le traversier continue).
- **Et à la place**, l'hiver amène : un **jongleur de feu**, des **foyers** au milieu des places, des
  **vendeurs de chocolat chaud**.
  Tranché ensuite (vague 3) : un brasero de part et d'autre de la fontaine à sec de chaque place, où des
  passants se chauffent les mains et où le joueur reprend son souffle plus vite ; une roulotte de chocolat
  chaud près des foyers ; et le jongleur du Faubourg qui jongle avec le feu à la place du jongleur d'été.

En trois vagues, sans un dé et sans rien déplacer (ce qui se pose, en dernier) :

1. **La foire cadenassée** — manèges, lumières, sons, foule, arche, défis et missions du Bonimenteur.
2. **Le tour** — derby, crème glacée, fruits de mer, amuseurs, piscines, fontaine, BBQ, chaloupes.
3. **Ce que l'hiver amène** — le jongleur de feu, les foyers des places, le chocolat chaud.

## Notes

### Vague 1 — la foire cadenassée (30 sept. 2026)

- **Une seule question** : `Foire.fermee()` = `Saisons.enHiver()` (la neige qui tient). Tout le reste la lit
  là où il vit, sans un dé et sans rien sauvegarder.
- **Les machines** (`foire.js`) : une machine en gare y reste (son attente ne tombe jamais à zéro, pas de
  sifflet) ; en route, elle finit son tour. Une partie qui s'ouvre en janvier trouve le train en gare. La
  roue s'arrête à son cran 0, celui de son décor. On ne monte à rien, on ne joue à rien
  (`sousLaMain`, `jeuSousLaMain`), l'orgue et les cris se taisent, et les sièges sont vides (ni machiniste,
  ni voyageurs, nacelles vides, `chariot_vide`).
- **Le décor** (`sprites.js`, `DECORS_DE_FOIRE` → `fermeLHiver`) : `Entites.poseDuDecor` rend 0 (rien ne
  tourne), et le peintre reçoit `ferme` : volets de tôle baissés et cadenassés sur les comptoirs, plus de
  vendeur, les ampoules éteintes, les tasses et les chaises volantes vides (les chaînes pendent droit), le
  bassin des canards gelé, et une chaîne avec sa pancarte FERMÉ sous l'arche.
- **La neige qui coiffe** (`Saisons.coiffer`) : deux rangs de blanc sur le dessus de ce qui a au moins trois
  pixels de haut, par composition, sans lire un pixel. ⚠️ La première version blanchissait tout pixel au ciel
  ouvert : la jante et les rayons de la grande roue, et la chaîne de l'arche, disparaissaient sous la neige.
  C'est la capture qui l'a montré, pas les juges.
- **Les guirlandes** (`Monde.lampesVisibles`) : les lampes `foire_*` s'éteignent.
- **L'arche** (`carte.BARRIERES`, `hiver`) : `Monde.barriereFermee` la ferme même avec un billet du jour, la
  caisse ne vend rien, on lit LA FOIRE EST FERMÉE POUR L'HIVER (`Monde.raisonDe`), on ressort librement, et
  resquiller coûte pareil.
- **La foule** : `naitreLaFoire` ne fait naître personne ; forains et mascottes rentrent hors de l'écran.
  Et la foule de la rue ne naît plus dans l'enceinte (`dansLaFoireFermee`, dans `placeDeNaissance` et
  `peuplerDabord`) : la capture de janvier montrait deux passants dans la foire cadenassée.
- **Le Bonimenteur** (`absent_l_hiver`) : pas posé l'hiver, ses missions ne sont pas `disponibles` ;
  `Histoire.majSaisonniers` (toutes les cinq secondes) le retire hors de l'écran à la neige et le repose au
  dégel, jamais pendant une mission qui a besoin de lui.
- **Juges** : `tests/test_foire_l_hiver_js.py` (dix juges, chacun janvier ET juillet, mutés un à un). Les juges
  de la foire ouverte se posent en juillet (`jour = 21`, puis `Foire.demarrer()` : le train garé en janvier
  comptait un arrêt de trop), comme ceux de p13/p14 (`Histoire.majSaisonniers(true)`).
- ⚠️ **Un dé de moins déplace tout** : le Bonimenteur qui ne naît plus en janvier est un `creerPieton` de
  moins, et la filature des défis gradués (7 200 images à traverser des rues) finissait sous une auto du
  trafic. Le juge mesure une distance, pas le trafic : le joueur y est invincible.
- **Pas fait** : les allées de la foire (`g`, « poussière de pierre ») restent sans neige. C'est le glyphe de
  tous les sentiers de parc de la ville : une décision à part.

### Vague 2 — le tour (30 sept. 2026)

- **Les artistes de rue** (`pietons.ARTISTES_FROID_MAX` = 0,75, le seuil de l'homme au manteau) : le
  musicien, le mime, le jongleur et l'échassier ne naissent plus au grand froid et rentrent hors de l'écran
  (`enSaison`, le mécanisme livré par la plage).
- **La cabane de fruits de mer** (`froid_max` sur son ambulant) : `Missions.ouvert` et `majKiosques` lisent
  la saison ; personne au comptoir, « FERMÉ POUR L'HIVER » (`fermeDuKiosque`), et son homme-sandwich ne
  crie plus la guédille. Le hot-dog, le café et le camion-restaurant restent ouverts.
- **Le camion de crème glacée** (`majCremeGlacee`) : il ne vient plus se garer, et celui qui attend à sa place
  repart hors de l'écran — jamais celui qu'on conduit ou qu'on a laissé ailleurs.
- **Le derby de démolition** (`hors_hiver` sur le défi, le miroir de `hiver`) : ÇA REPREND AU PRINTEMPS.
- **La piscine hors terre** (`o`) : une bâche grise dans son rebord, un coussin de neige dessus.
- **La fontaine à sec, le barbecue sous sa housse** : `fermeLHiver` sur `fontaine`, `fontaine_villa` et
  `bbq` (même mécanisme que la foire : `dortLHiver` lit maintenant la saison) — plus de jet, de la neige au
  fond du bassin, la housse verte sanglée. ACTION : À SEC POUR L'HIVER, SOUS SA HOUSSE POUR L'HIVER.
- **Pas fait ici** : les chaloupes sorties de l'eau — c'est la vague 5 de « Les bateaux ne sont pas des
  chars » (les chaloupes de plaisance sur des bers à quai), déjà tranchée avec eux.
- **Juges** : `tests/test_le_tour_de_l_hiver_js.py` (sept juges, janvier ET juillet, mutés d'un coup : six rougissent).
- ⚠️ **Les juges de l'été se posent en été, et parfois AVANT `commencer`** : un marchand se poste pendant
  `commencer` (`creerAmbulants`), donc `jour = 22` posé après arrive trop tard (`test_kiosque_ferme_js`,
  `test_reclame_js`, `test_commerces_js`, `test_pietons_js`). Le 22, pas le 21 (le 21 déménage le joueur), et
  sans dette quand le juge joue au barbecue : l'été, les hommes de Sal passent collecter chaque jour. Les juges
  des amuseurs retirent seulement la saison des artistes (`delete froid_max`) : ils tiennent à la rue exacte
  de janvier (la graine 64 du jongleur).
- ⚠️ **Un dé de moins, un défaut de plus au grand jour** : les trois marchands de fruits de mer qui ne se
  postent plus en janvier décalent le hasard de la ville, et `test_demeler_ne_pousse_pas_un_passant_sur_la_chaussee`
  est tombé de 0,01 px. Sur la base, 2 graines sur 12 le faisaient déjà tomber : `demeler` tolérait 0,01 px
  d'enfoncement PAR IMAGE. Resserré à un millionième (`TOLERANCE_BORDURE`) : 12 graines sur 12.

### Vague 3 — ce que l'hiver amène (30 sept. 2026)

- **Les foyers des places** (`static/js/foyers.js`, `app/foyers.py`) : sur chaque place publique (la ville en a
  deux, la fontaine au centre de `_place`), un brasero de part et d'autre de la fontaine à sec et une roulotte
  de chocolat chaud, chacun sur la première tuile libre d'une liste écrite à la main — du pavé, hors de la rue
  et du pas d'une porte, à distance de tout décor posé **sur toute la hauteur du dessin** (la roulotte, posée
  d'abord sous un banc, le couvrait : c'est la capture qui l'a montré). ⚠️ RIEN NE NAÎT : ils se peignent,
  triés avec les gens, arrêtent le pas, éclairent le soir (les lampes du plafond commun) — sans un dé, sans une
  entité, pas un numéro décalé (jugé : `B.rng` n'est jamais appelé).
- **Se chauffer** (`Entites.majLesFoyers`) : un passant qui flâne près d'un feu y va, un sur trois à
  l'empreinte de son numéro et du jour, une fois par jour, trois au plus par feu, chacun à SA place (trois
  places à 60° au sud du feu). ⚠️ Un angle à l'empreinte donnait parfois la même place à deux passants : ils
  marchaient l'un dans l'autre (`test_la_foule_ne_se_traverse_plus`). Le joueur debout près d'un feu reprend
  son souffle plus vite (`chaleur_souffle`), « ÇA RÉCHAUFFE ».
- **Le chocolat chaud** : un commerce du trottoir (`Missions.acheterAmbulant`, `commerceDe('chocolat')`), 3 $
  pour 4 PV et 15 de souffle. ⚠️ Ses tarifs s'appellent `chocolat_chaud` : la clé `chocolat` existait déjà (la
  tablette des distributrices) et, doublée, elle écrasait le chocolat chaud — le juge lisait la même clé
  écrasée et restait vert ; c'est ruff (F601) qui l'a vu.
- **Le jongleur de feu** : la MÊME sorte, pas une de plus — une sorte neuve dans les amuseurs, c'était un
  tirage de plus à chaque mélange (`ordreDesSortes`), été compris. L'hiver, `SPRITES.jongleur.hiver` change ses
  trois balles en flammes (cœur jaune, bord orangé), et ses torches éclairent la rue le soir
  (`Foyers.lampes`). Le jongleur perd donc son `froid_max` de la vague 2.
- **Le crépitement** (`foyer_feu`, ElevenLabs, 8 s en boucle, lieu `foyers`) : tenu tant qu'on est près d'un feu,
  dosé à la distance ; faute de fichier, un crépitement synthétisé.
- **Juges** : `tests/test_foyers_de_l_hiver_js.py` (huit juges ; `allumes()` muté : les cinq de comportement
  rougissent). Le juge du public du jongleur (la graine 64) éteint les foyers et la saison des kiosques
  avant `commencer` : il tient à la rue exacte de janvier.
- ⚠️ **Hors sujet, trouvé en passant** : `test_la_foule_ne_se_traverse_plus` tombe pour 3 graines sur 10 sur
  dev, même sans ces vagues — deux passants coincés dans le goulot d'une tuile entre la façade et l'abribus
  du terminus (128, 125) creusent leur chevauchement. Avec le jongleur revenu en janvier, la graine du juge
  tombe dessus.
