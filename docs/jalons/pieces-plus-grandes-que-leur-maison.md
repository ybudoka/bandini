# Pièces plus grandes que leur maison

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Une pièce plus grande que sa maison (**correctif**, taille 2) — **livré le 14 sept. 2026**_

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

## Notes

demande de Martin, mesurée : **35 des 45 portes** de la graine livrée ouvraient sur plus
grand que leur bâtiment, jusqu'à **onze fois** (9 tuiles dehors, 98 dedans). Maintenant la
pièce **se choisit à la taille du bâtiment** — la plus grande qui tienne, et rien du tout si
même la plus petite déborde : la porte reste alors condamnée. **Quatre petites pièces
neuves** (deux de 9 tuiles de plancher, une de 18, une de 21) et **26 pièces redessinées**
plus petites ; la **parcelle d'un lieu garanti se taille à la mesure de sa pièce** au lieu
d'espérer que le découpage au sort en fasse une de la bonne taille ; et **chaque famille de
commerce ouvre au moins une porte**, parce que « tirer l'enseigne × être assez grand ×
gagner le dé » laissait quatre familles sur dix sans un seul intérieur. **0 débordement sur
5 graines**, contre 34 à 46 avant. 12 juges neufs
