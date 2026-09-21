# Les amuseurs de rue font un vrai spectacle

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les amuseurs de rue font un vrai spectacle (**correctif**, taille 3) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « je veux que les amuseurs de rue soient animés et qu'il y ait toujours
entre 3 et 5 personnes autour. Présentement ils ne font rien et sont ennuyants. Je veux que le
musicien fasse vraiment de la musique, 5 musiques différentes, je veux des jongleurs et des
échassiers. » Et : « ils doivent toujours être dans le centre-ville, où il y a plus de gens.
Tu peux aussi mettre plus de gens en centre-ville et moins en périphérie. »

⚠️ **Martin a raison, et la fiche d'origine le disait déjà.** « Des sortes de gens » promettait
un musicien qui « joue — et **ça s'entend** » ; ce qui a été livré, c'est un corps avec une
guitare dessinée dessus et **zéro note**. Le jeu a un séquenceur (`Son.Mus`), dix morceaux
écrits en notes, un chef d'orchestre — et l'homme à la guitare est muet. C'est la neuvième fois
que le dépôt paie « une fiche que le navigateur ne lisait pas », et la première où c'est
l'**oreille** qui le dit.

Ce qui ne va pas, mesuré :

- **Ils ne font rien.** `majSortes` envoie le musicien et l'amuseur dans la même fonction,
  `attrouper`, qui ne touche **qu'aux badauds** : elle ne change rien à l'artiste. Ils sont
  `vitesse: 0`, donc `bouge` est faux, donc `imageDe` tombe sur **l'image zéro** — la même,
  toujours, pour toute la partie. Le mime n'a jamais bougé un doigt.
- **L'attroupement est un hasard, pas une foule.** `attrouper` attend qu'un passant entre dans
  les 46 px et qu'il soit en `flane` ou `arret`. Dans une rue vide, il n'y a **personne** ; et
  une fois attroupés, leur `minuterie` de 4 à 8 s les renvoie ailleurs sans que rien ne les
  remplace. Le juge du banc pose lui-même quatre badauds avant de mesurer — c'est-à-dire qu'il
  mesure l'attroupement d'une foule qu'il a fabriquée.
- **Ils naissent partout.** `musicien` et `amuseur` n'ont pas de `districts` : un mime dans une
  cour à ferraille de La Shop à 3 h du matin, devant personne.
- **Il n'y a qu'un genre d'amuseur** : le mime. Pas de jongleur, pas d'échassier.

**Ce qu'on fait.**

- **Quatre corps, quatre spectacles.** Le musicien et le mime gagnent de vraies images de
  spectacle ; le **jongleur** et l'**échassier** sont deux sortes neuves, avec leur corps à
  elles (règle du dépôt : une sorte = un corps + une routine, et un juge Python refuse une
  sorte qui porte le corps d'une autre).
  - le **musicien** gratte : la main descend et remonte **en mesure**, sur le tempo du morceau
    qu'il joue ;
  - le **mime** enferme le vide : mur invisible, boîte, salut — des poses, pas des pas ;
  - le **jongleur** a **trois balles dans les airs**, et elles sont dans le sprite : quatre
    images, la balle monte, tourne, retombe. ⚠️ Dessiner les balles à part aurait voulu dire
    un deuxième chemin de dessin pour une seule sorte — le sprite les porte, l'atlas les cuit
    une fois, et le tri par `y` reste le seul tri ;
  - l'**échassier** est **plus haut que tout le monde** : son sprite fait 26 px au lieu de 13,
    il dépasse la foule, et il tangue doucement — c'est précisément ce qui le rend visible de
    loin, par-dessus l'attroupement.
- **Toujours 3 à 5 personnes autour**, et c'est une **règle**, pas une chance : si le cercle
  est en dessous du minimum, un badaud **naît hors champ** et vient se planter dedans ; au
  maximum, on n'en prend plus. Les spectateurs **tournent** — un qui s'en va est remplacé — et
  ils **applaudissent**. ⚠️ Les chiffres (3, 5, le rayon du cercle, la patience) vivent dans
  `pietons.py` : le navigateur les lit, il ne les invente pas.
- **Le musicien joue vraiment, et cinq morceaux.** Cinq pièces de rue **écrites en notes**
  (`musique.py`), comme le thème du menu et les radios — deux voix, une guitare qui gratte et
  une mélodie, pas un orchestre : ⚠️ un homme seul sur un trottoir n'a ni basse ni batterie, et
  une station de radio à quatre voix sous un mime aurait sonné comme un haut-parleur.
  - **La complainte du Faubourg**, **Le reel du trottoir**, **Le blues du coin**, **La valse de
    la Baie** (à trois temps — la seule du jeu) et **La ballade des brumes**. Chaque musicien
    en tire une **à la naissance** et la garde.
  - ⚠️ **Elle se joue DANS LA RUE, pas dans le casque** : un deuxième séquenceur (`Son.Rue`)
    avec sa propre sortie, et **le volume suit la distance** — on l'entend d'un coin de rue, on
    l'a dans les oreilles devant lui, et elle s'éteint quand on s'en va. Un seul musicien
    sonne à la fois (le plus proche) : dix musiciens auraient fait dix séquenceurs.
  - ⚠️ Elle passe **sous** la voix (le ducking l'atteint, comme la radio) et **sous** la musique
    d'état : quand la police te court après, la toune du guitariste n'a plus d'importance.
    L'échelle de `musique.py` ne change pas — la rue s'ajoute **en dessous**.
- **Ils tiennent le centre-ville.** Les quatre sortes déclarent `districts: ("faubourg",)` —
  c'est le centre-ville ouvrier (`devantures.py` le dit déjà en toutes lettres) et c'est le
  district le plus peuplé. Un amuseur joue là où il y a du monde ; ailleurs, il joue pour les
  goélands.
- **Et il y a plus de monde au centre, moins en périphérie.** `carte.py` donne à chaque
  district son nombre de piétons : le Faubourg monte, les Érables, La Shop et La Pointe
  baissent. ⚠️ Le plafond de la bulle (`MAX_PIETONS`) ne bouge pas : c'est la **répartition**
  qu'on change, pas le budget d'image — un quartier plus dense doit se payer avec la foule d'un
  quartier plus vide.

⚠️ **Le budget du paquet.** Cinq morceaux de plus, c'est le catalogue de musique qui passe de
25 à ~33 Ko — le plafond du juge est à 48 Ko, et aucun fichier audio n'est téléchargé : une
pièce écrite en notes pèse 1,6 Ko, une minute de mp3 en pèse 500.

**Livré le 14 sept. 2026**, et trois choses se sont révélées en chemin :

- ⚠️ **Deux artistes se volaient leur public, et rien ne le disait.** `recrutable` ne refusait
  qu'un badaud déjà dans SON cercle : le second artiste né dans le quartier, n'ayant personne
  de libre à portée, prenait les trois du premier — qui restait **seul au milieu de sa scène
  et n'en retrouvait plus jamais**. Un numéro sans personne, c'est exactement ce que Martin a
  signalé ; le faire arriver à coups de règles neuves aurait été une belle façon de ne rien
  réparer. On ne vole plus le public du voisin.
- ⚠️ **La relève part AVANT que la place se libère.** Un remplaçant traverse la rue à pied :
  attendre que le cercle tombe à deux pour l'appeler, c'est deux secondes à deux. On compte
  donc ceux qui seront **encore là quand il arrivera** — et **le dernier ne part pas** tant
  que la relève n'est pas assise. Mesuré : le cercle passait sous 3 pendant **6,3 %** du temps
  avant ces deux règles, **0,1 %** après (une seule fois, onze images).
- ⚠️ **Le contrat porte sur ce qu'on VOIT.** Un artiste naît hors champ, à l'autre bout du
  quartier ; s'il n'y a personne de libre hors écran, son cercle met quelques secondes à se
  faire — les badauds marchent, ils ne se matérialisent pas. Sur 1800 images où un amuseur est
  **à l'écran**, il n'a jamais eu moins de 3 ni plus de 5 personnes autour, et **jamais zéro**.
  C'est ce que le juge mesure, et c'est ce qui se voit.

Et deux juges qui tenaient par chance sont tombés, parce qu'une routine de plus **décale le
dé** : celui du touriste sortait de sa boucle au **premier arrêt** (or un flâneur s'arrête
aussi tout seul, et `majPhoto` ne part que depuis `flane`), et celui du stationnement
**espérait** que le quartier finisse par remplir ses rues. Les deux mesurent maintenant la
règle au lieu d'espérer le hasard — c'est la leçon que la chute de l'ivrogne avait déjà écrite.

- **Juges (9 neufs)** : côté Python, chaque sorte a son corps, son métier et ses quartiers ;
  les cinq pièces de rue ont toutes leurs notes **dans leur gamme**, aucune ne déborde de sa
  boucle, deux n'ont ni le même tempo ni la même tonalité ni la même mélodie, et il y a **une
  valse et une seule**. Au banc (`tests/test_amuseurs_js.py`) : les quatre ne naissent **qu'au
  centre-ville**, ils partagent un plafond de deux, le cercle tient **entre 3 et 5 à chaque
  image où on les voit** dans une rue qu'on n'a pas garnie à la main, les quatre **changent
  d'image** (et de vrai dessin — un `poseFixe` qui tourne dans le vide les fait rougir),
  l'échassier **dépasse le plus grand corps de la ville de huit pixels**, le musicien **pose
  des notes qui atteignent la sortie**, plus fort de près que de loin, et **se tait** quand on
  s'en va ; le public **applaudit, paie et se renouvelle** ; et aucun artiste ne se plante
  **hors d'une scène de la carte**.

## Notes

demande de Martin : « les amuseurs de rue ne font rien et sont ennuyants ; je veux qu'ils
soient animés, qu'il y ait toujours entre 3 et 5 personnes autour, que le musicien fasse
vraiment de la musique (5 musiques différentes), et des jongleurs et des échassiers ». Ils
tiennent leur coin **au centre-ville**, là où il y a du monde — et la ville y met plus de
passants, la périphérie moins
