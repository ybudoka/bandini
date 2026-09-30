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
