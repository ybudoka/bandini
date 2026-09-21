# Des feux pour piétons

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Des feux pour piétons (**ajout**, taille 2) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « pour les piétons, il faut ajouter des lumières de priorité, et sinon
ils ne passent pas. »

La règle existe déjà, mais **personne ne la voit**. `traverseeSure()` fait traverser un piéton
quand les chars de sa rue ne sont pas au vert ; ailleurs, quand aucun char ne roule à moins de
70 px. Rien ne l'annonce : un piéton planté au bord d'un passage a l'air indécis, pas
discipliné — et le joueur n'a aucun moyen de savoir quand c'est son tour.

⚠️ **Et au passage, le code se trompe d'un temps.** `!feuVert(...)` est vrai pendant
**l'orange** aussi. Les piétons s'engagent donc exactement quand les chars accélèrent pour
vider le croisement — le pire moment du cycle. Un vrai feu piéton ne s'allume pas au rouge :
il s'éteint **avant** que les chars repartent, et c'est ce dégagement qui manque.

- **Le feu lui-même** : un petit poteau à chaque bout de traverse, sur le coin. ⚠️ À 480 × 270,
  il se lira par sa **couleur et sa forme**, jamais par son détail — le blanc qui marche,
  l'orange qui arrête. Rien à inventer côté horloge : `feuVert()` est une pure fonction de
  `B.t` et du décalage du croisement, sans état ; le feu piéton s'en déduit et ne coûte rien
  à garder.
- ⚠️ **Faire clignoter la traverse elle-même serait plus lisible et plus cher.** Les tuiles de
  passage sont **cuites dans le morceau** de 256 px : les animer voudrait dire repeindre
  par-dessus à chaque image. Le poteau est une entité, il se dessine dans le budget déjà
  prévu. Si l'on veut quand même que la traverse s'éclaire, c'est un choix de budget, pas de
  goût, et il se mesure avant.
- ⚠️ **« Sinon ils ne passent pas » demande une exception, sinon la foule s'échoue.** Les
  croisements en **T** n'ont pas de feux — ils ont un STOP (M8). Si un piéton n'y traverse
  jamais, un côté de rue entier devient un cul-de-sac pour la foule, et aucun juge ne le
  verrait : « un seul îlot marchable » parle de géométrie, pas de circulation. La règle juste
  est donc : **au feu, on attend le blanc ; sans feu, on traverse quand c'est libre** — ce qui
  est déjà le comportement, et ce que fait le vrai monde. Un piéton ne reste bloqué que là où
  un feu lui dit d'attendre.
- **Le joueur, lui, n'obéit pas.** Le feu piéton est une **information**, pas une règle : le
  joueur traverse où il veut, c'est déjà l'exception écrite dans la vision. Ce qu'il gagne,
  c'est de savoir quand la foule va bouger — et donc quand un char va devoir s'arrêter.
- ⚠️ **Ça se joue avec la traverse d'une tuile.** Si la traverse rétrécit à une tuile et que
  tout un coin attend le même blanc, la file part d'un coup dans un couloir de 16 px. Les deux
  fiches se décident ensemble : c'est la même question.
- **Juges** : un piéton ne s'engage jamais pendant l'orange ni pendant le vert des chars ; le
  feu piéton s'éteint avant que les chars repartent (le dégagement se mesure en images) ;
  aucun piéton ne reste bloqué plus de N secondes à un passage sans feu ; et le nombre de
  poteaux reste dans le budget de décor et de paquet — un feu par bout de traverse, pas un par
  tuile.

**Livré le 14 sept. 2026.** Le correctif d'abord, l'affichage ensuite — c'est l'ordre qui
compte : un feu qui montre la mauvaise chose est pire que pas de feu.

- ⚠️ **Le temps était faux, et ça se mesure : 240 images sur 960.** `!feuVert(...)` est vrai
  pendant l'orange, donc un piéton s'engageait pendant tout l'orange des deux sens.
  `Monde.feuPieton()` rend maintenant trois états — **blanc** (on s'engage), **dégage** (on
  finit, on ne part plus), **rouge** — et `traverseeSure` n'accepte que le blanc. Le
  dégagement laisse finir ceux qui sont déjà engagés : on ne teste qu'à **l'entrée** du
  passage.
- **Le dégagement vaut 120 images**, l'orange 60 : **180 images** séparent la dernière image
  blanche du premier char qui roule. Deux secondes pour franchir deux tuiles à 0,45 px par
  image — il en faut 71. ⚠️ Sans ce temps-là, celui qui s'engage à la dernière image se fait
  cueillir par le premier char du vert suivant, et **c'est le jeu qui a l'air injuste**, pas le
  piéton qui a l'air imprudent.
- **351 poteaux**, posés par `carte.py` **sur la traverse** — un à chaque bout, jamais un par
  tuile — et refusés partout où le trottoir est déjà pris (496 possibles, 145 écartés). ⚠️ Et
  **le sens du passage voyage avec le poteau** : sans lui, le navigateur devrait redeviner à
  quel feu chaque poteau obéit, et il se tromperait une fois sur deux.
- ⚠️ **Les feux des chars se devinent depuis la boîte du croisement ; ceux des piétons, non.**
  Une traverse ne tombe pas toujours où l'on croit — c'est la carte qui sait où elle est.
- **Ça se lit par la couleur et la forme** : un boîtier plus petit que celui des autos (six
  pixels sur dix-huit — trois cent cinquante fois la taille du grand mangerait la rue), le
  **blanc qui marche**, l'**orange qui arrête**. Et l'orange du dégagement **clignote** : fixe,
  il se lit « attends » ; qui bat, il se lit « finis, mais ne pars plus ».
- ⚠️ **Aucun état à garder** : comme `feuVert`, `feuPieton` est une pure fonction de `B.t` et
  du décalage du croisement. Trois cent cinquante poteaux ne coûtent donc rien de plus qu'un.
- ⚠️ **Le juge du cycle a failli mentir** : il cherchait le prochain vert **en avant** dans une
  fenêtre qui commence à une phase quelconque, et la dernière image blanche tombe souvent
  après le dernier vert de la fenêtre. Il tourne maintenant **en rond** — sans quoi il aurait
  dit « pas de dégagement » pour un dégagement parfait.
- **Ce qui reste ouvert** : la traverse elle-même ne s'éclaire pas. Les tuiles de passage sont
  **cuites dans le morceau** de 256 px, et les animer voudrait dire repeindre par-dessus à
  chaque image — c'est un choix de budget, pas de goût, et il se mesure avant.

## Notes

demande de Martin : « pour les piétons, il faut ajouter des lumières de priorité, et sinon
ils ne passent pas ». La règle existait (`traverseeSure`) mais **personne ne la voyait** —
et ⚠️ elle **se trompait d'un temps** : `!feuVert(...)` est vrai pendant l'**orange** aussi,
donc les piétons s'engageaient pile quand les chars accélèrent pour vider le croisement,
**240 images sur 960**. Maintenant `Monde.feuPieton()` rend **blanc / dégage / rouge**, le
blanc ne croise ni le vert des chars ni l'orange, et il s'éteint **180 images avant** que
les chars repartent (dégagement 120 + orange 60). **351 poteaux** posés par `carte.py` **sur
la traverse** — un à chaque bout, jamais un par tuile — avec le **sens du passage** dans la
fiche ; blanc fixe, orange **clignotant** au dégagement.

- ⚠️ **Sans feu (un T), on traverse quand c'est libre** : sinon un côté de rue entier
  devient un cul-de-sac pour la foule, et aucun juge existant ne le verrait. 2 juges neufs
