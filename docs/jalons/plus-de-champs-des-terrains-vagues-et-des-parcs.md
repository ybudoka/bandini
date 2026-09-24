# Plus de champs : des terrains vagues et des parcs

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « au lieu des champs, mets des terrains vague un peu salle et avec des
déchets, mais aussi des parcs ».

- ⚠️ **Mesuré, et le mot est juste** : **24 lots** de la ville — **1 328 tuiles** — se
  peignent avec le **gazon des parcs** (`,`), et il n'y a qu'**un objet par 17 tuiles**
  dessus. Dix sont des terrains nus (`_jardin`, 406 tuiles, un arbre ou un buisson par 16
  tuiles, et en banlieue une palissade autour) ; quatorze sont des **terrains vagues** (922
  tuiles) dont le seul décor est le gravat, semé un par 17 tuiles — sur de la pelouse. Vu
  d'en haut, un lot abandonné derrière son grillage a donc exactement la surface d'un
  parterre de banlieue : un champ. Trois choses : (1) une **friche** (`;`) dans la légende —
  la terre perce, l'herbe est sèche, et ⚠️ **pas de `herbe`** dans sa fiche, sinon la
  mini-carte la repeint en vert et c'est un parc de plus ; (2) **trois déchets** au
  catalogue (sacs d'ordures, pneu, baril rouillé) semés avec les gravats et les mauvaises
  herbes ; (3) un **parc de quartier** — un sentier de poussière de pierre, des bancs, des
  arbres serrés, parfois une table à pique-nique — qui remplace le gazon nu moitié-moitié
  avec le terrain vague. Plus un seul lot de pelouse rase. ✅ **Livré** (16 sept. 2026). **La
  friche** (`;`) : un terrain vague ne se peint plus au gazon des parcs — 1 238 tuiles de
  terre sèche, l'herbe haute, la plaque de terre nue, le gravat brûlé.
- ⚠️ **Pas de `herbe`** dans sa fiche : la mini-carte peint le vert avec cette propriété-là,
  et une friche verte sur la carte est un parc de plus. **Trois déchets** au catalogue
  (`ordures` — deux sacs dont un crevé ; `pneu` — un ANNEAU, un disque se lit comme une
  flaque, et le seul du lot qui ne soit pas solide ; `baril` rouillé), semés avec les
  gravats, les caisses et les mauvaises herbes : **256 objets sur 1 677 tuiles**, un par 6,6
  au lieu d'un par 17. **Le parc de quartier** remplace le gazon nu, une sorte pour une
  sorte : ⚠️ ce qui fait un parc, c'est le SENTIER — un carré de gazon planté d'arbres reste
  un terrain, le jour où quelque chose le traverse c'est un endroit où l'on va. Le sentier
  se réserve en se traçant (la leçon de `_allee`), les bancs le bordent, et le parc **ne se
  clôture pas**. 9 parcs, 1 objet par 5,6 tuiles.
- ⚠️ **LA LEÇON DE LA SÉANCE, ET ELLE A COÛTÉ DIX JUGES** : le semis neuf tirait plus de dés
  que l'ancien dans le **dé commun**, donc toute la ville se rebattait — une barrière
  d'usine dont la couronne passait sur une case de stationnement, un buisson que la balle du
  banc ne rencontrait plus, deux enfants qui ne jouaient plus au ballon, et pas un juge ne
  parlait de terrain vague. Le décor des lots a maintenant **son propre dé** (`des_dechet`),
  on **brûle** exactement ce que l'ancien semis tirait (`Des.brule`, `_tirages_de_semis` —
  ⚠️ `entier(a, b)` ne tire pas quand `b <= a`), et `_contenu` échange `jardin` contre
  `parc` **sans toucher au tirage**. Mesuré : **1 066 tuiles changent dans toute la ville,
  dont 128 hors des lots redessinés** — et ces 128 sont voulues (voir ci-dessous). Les
  terrains vagues restent donc exactement où ils étaient ; ils changent de surface, pas de
  place.
- ⚠️ **Et un défaut de M8 découvert en passant** : la palissade de bois, « l'image de
  banlieue » que le plan promet depuis M8, tenait aux **LOTS VIDES** et pas aux cours —
  l'exact inverse de ce qu'on voit par la fenêtre, et le commentaire de `_jardin` le disait
  déjà. Mesuré : sur 36 terrains de banlieue, **SIX** avaient trois tuiles derrière la
  maison, deux ont appelé `clore`, et il restait **onze tuiles** de palissade dans toute la
  ville une fois les lots devenus des parcs. Deux tuiles de fond suffisent maintenant, la
  chance monte à 0,8 : **64 tuiles**, sur de vraies cours arrière.
- ⚠️ **Un correctif attrapé en chemin, et il ne parle pas de terrains vagues** : le juge
  « toujours entre 3 et 5 personnes autour d'un amuseur » tenait **par chance**.
  `majSpectacle` ne retenait les partants qu'à `vus.length <= mini` — or il ne tourne qu'une
  image sur quinze, et deux minuteries peuvent tomber dans le même intervalle : à quatre
  spectateurs, deux partants, le tour suivant trouvait le cercle à DEUX. Mesuré sur six
  graines de partie, il tombait déjà sur **deux d'entre elles avant** tout changement de
  carte. On compte maintenant les PARTANTS et on retient les plus pressés jusqu'à ce que le
  minimum tienne (`sursis_images`) : cinq graines sur six.
- ⚠️ **Pas de table à pique-nique dans un parc de quartier** : `test_greve` tient que toute
  table de la ville est au bord de l'eau, et il a raison — c'est un meuble de PLAGE. 8 juges
  neufs ; 1741 tests.
- ⚠️ **Reste ouvert, mesuré et nommé** : sur une graine de partie (82), un artiste né à huit
  tuiles d'un autre reste **seul 900 images** — `placeDansLeCercle` renonce et
  `garnirLeCercle` abandonne avant même d'essayer de recruter. Le défaut existe à
  l'identique avant ce changement (graine 81).
