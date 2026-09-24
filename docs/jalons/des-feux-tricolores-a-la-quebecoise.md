# Des feux tricolores, à la québécoise

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Des feux tricolores, à la québécoise (**correctif**, taille 2) — **livré le 15 sept. 2026**_

_Demandes de Martin, dans l'ordre :_ « les feux pourraient être mieux, cherche sur le web des
représentations visuelles » · « assure-toi que les feux et les voitures suivent la même logique »
· « je veux des feux tricolores et un seul allumé à la fois » · « les feux piétons sont à part
mais les piétons le respectent (sauf exception) et les véhicules aussi (sauf exception) » · « mets
les lumières qui tiennent d'un seul bout sur le poteau et la partie dans le vide au-dessus de la
route » · « moins de lignes pour les traverses piétons » · « ne mets pas de lampadaire aux
intersections, déplace-les, ça va laisser la place libre aux feux ».

⚠️ **La recherche a donné mieux qu'une référence de pixel art.** Au **Québec**, les feux sont
**horizontaux**, et leurs lentilles ont des **formes** : le rouge **carré**, le jaune en
**losange**, le vert **rond**. Ce n'est pas un détail pittoresque — c'est fait pour qui ne
distingue pas le rouge du vert (le Nouveau-Brunswick, la Nouvelle-Écosse, l'Île-du-Prince-Édouard
et l'est de l'Ontario ont suivi). Et ça règle du même coup le problème de lisibilité du jeu : **à
trois pixels, une forme se lit quand une teinte se devine**. La signalisation d'ici était déjà la
réponse.

- **Un vrai tricolore, une seule lentille allumée.** Avant, un boîtier portait **deux** lanternes,
  une par axe, chacune changeant de couleur : ce n'était pas un feu, c'était deux témoins. Un mât
  montre maintenant **une rue** et **une couleur** ; les deux autres lentilles sont des **douilles
  éteintes**, cuites dans la fiche, chacune dans un ton très sombre de sa couleur — c'est ce qui
  fait qu'on voit qu'il y en a trois, et laquelle brille.
- ⚠️ **Une seule source pour la couleur.** `Monde.feuDeCirculation()` rend `vert`, `jaune` ou
  `rouge` ; `feuVert` en **découle** (`=== 'vert'`), le **dessin** en découle, et le trafic obéit à
  `feuVert`. Un feu ne peut donc plus montrer une couleur qu'un char ne respecte pas : c'est la
  même phrase lue deux fois, jamais deux phrases. Le feu piéton s'était trompé d'un temps
  exactement parce qu'il relisait `!feuVert` au lieu d'avoir sa règle — on ne recommence pas.
- ⚠️ **Le jaune n'est pas vert.** Un char qui arrive à la ligne d'arrêt sur le jaune s'arrête.
  Sans ça, le dégagement du feu piéton ne servirait à rien : le croisement ne se viderait jamais.
- **L'exception, c'est la sirène.** En poursuite, un char brûle le feu, le STOP et la boîte — une
  auto-patrouille qui attend au rouge pendant que le joueur s'enfuit n'est pas une poursuite. Un
  juge neuf pose un char sur une ligne d'arrêt et mesure : il ne bouge pas au rouge, pas au jaune,
  il part au vert, et il passe au rouge sirène allumée.
- **Quatre mâts, un par coin** — ce qui règle le coin manquant laissé ouvert la veille. ⚠️ Et
  l'**axe suit la diagonale** : nord-est et sud-ouest portent le nord-sud, nord-ouest et sud-est
  l'est-ouest. Qui arrive du sud a les deux coins nord devant lui, donc un de chaque diagonale,
  donc un feu de **son** axe. Ce n'est pas une convention de goût : c'est une propriété, et un
  juge la vérifie **pour les quatre approches, à tous les croisements de la ville**.
- **Une potence, pas un poteau.** Le mât est planté au **bord du trottoir**, côté rue, et la tête
  porte à faux **au-dessus de la voie**. ⚠️ Planté au **centre** de sa tuile — ce qu'il était —,
  dix des treize pixels du bras restaient au-dessus du **trottoir** : la tête n'était pas sur la
  chaussée, elle était à côté. Collé au bord, le bras passe la bordure à trois pixels.
- ⚠️ **Un seul gabarit, et un miroir.** Tout est écrit « bras vers l'est » ; un mât tourné vers
  l'ouest se peint avec les **mêmes nombres** passés par `miroir()`, des deux côtés (la fiche cuite
  **et** la lentille vive — si les deux ne retournaient pas pareil, elle s'allumerait à côté de son
  trou). Et le miroir **retourne l'ordre des lentilles**, ce qui est juste : le rouge est à gauche
  **du conducteur**, et deux têtes qui se regardent en sens opposés se voient à l'envers l'une de
  l'autre, vues d'en haut.
- **Moins de lignes aux traverses, et la norme dit combien.** Une bande de passage fait **0,50 m**
  et l'interdistance **0,50 à 0,80 m** : le **vide est plus large que la bande**. Ici c'était
  l'inverse (3 px de bande, 2 de vide) et un passage se lisait comme un mur blanc. À l'échelle du
  jeu (1 px ≈ 0,20 m), c'est **3 de bande, 5 de vide**. ⚠️ **Et le pas divise la tuile** : à 5, les
  bandes tombaient à 1, 6, 11 — deux pixels de vide dedans, **trois à la couture** entre deux
  tuiles. Le motif boitait à chaque tuile sans qu'on sache pourquoi. À 8, elles tombent à 1 et 9 et
  le vide fait cinq **partout**, couture comprise.
- **Les lampadaires quittent les coins.** `lampadaires()` les plantait **sur** les coins du
  croisement — la place du mât. Tant qu'il n'y avait que deux mâts et aucune lanterne peinte, ça ne
  se voyait pas ; à quatre mâts peints, ils se disputaient la tuile au vu de tous. Ils s'écartent
  de **trois tuiles le long de la rue** (jamais en diagonale : un poteau qui recule de biais finit
  au milieu d'un parterre), et **316 lampadaires, zéro sur un coin réservé**. Ils éclairent
  d'ailleurs mieux là : entre deux croisements plutôt que dessus.
- **Juges (5 neufs)** : un tricolore n'allume **qu'une** lentille, à la colonne de sa couleur et de
  sa **forme**, à cinq instants du cycle ; ce qu'il **montre** et ce que le char **respecte** ne
  peuvent pas diverger ; de chacune des quatre approches un feu de son axe est en face ; un char
  s'arrête au rouge et au jaune, part au vert, et brûle le rouge sirène allumée ; aucun lampadaire
  sur un coin réservé au feu. Les deux juges du dessin **lisent le gabarit dans `DECORS.feu`** au
  lieu de le recopier — et le miroir avec, sans quoi ils chercheraient la lentille du mauvais côté
  et diraient « le feu est éteint » alors qu'il brille.
- **Les lampadaires et les bornes quittent les coins.** `lampadaires()` plantait ses poteaux **sur**
  les coins du croisement — la place du mât. Tant qu'il n'y avait que deux mâts et aucune lanterne
  peinte, ça ne se voyait pas ; à quatre mâts peints, ils se disputaient la tuile au vu de tous. Ils
  s'écartent de **trois tuiles le long de la rue** (jamais en diagonale : un poteau qui recule de
  biais finit au milieu d'un parterre) — **316 lampadaires, zéro sur un coin réservé**. Ils
  éclairent d'ailleurs mieux là : entre deux croisements plutôt que dessus.
- **La borne-fontaine : rouge, et elle crache.** Elle était **jaune** — au coin d'une rue, une tache
  jaune se lit comme une borne de stationnement, pas comme de l'eau. ⚠️ Et c'était une **tuile**
  (`'b'`, solide) : une tuile ne se casse pas, elle ne pouvait donc ni tomber sous un char ni gicler.
  C'est maintenant un **décor** avec sa fiche — `casse: 0.75`, `pv: 40`, moins qu'un lampadaire (60),
  et c'est la vraie borne qui le dit : elle est boulonnée sur des vis qui **cassent exprès**, pour
  qu'un char l'arrache au lieu de se plier autour. Défoncée, elle crache **dix secondes** : une
  **entité invisible** qui vit sa minuterie et lâche deux gouttes par image — le patron du brasier du
  Molotov, et la même raison, on ne repeint pas une tuile à chaque image pour un effet qui passe.
  ⚠️ **Son bruit emprunte `choc` et synthétise l'eau** : le seau des bruitages est à 14 Ko de son
  plafond, un échantillon à elle attendra une séance ElevenLabs.
- ⚠️ **Et un vieux juge a rougi sans qu'une ligne de son code change** : celui de la fille de la
  Brume. Il prenait son écart maximum sur quarante secondes, **fuite comprise** — une fille qui
  détale d'un coup de feu court 240 px, et c'est exactement ce qu'elle doit faire ; une fois partie
  elle ne revient pas, parce que la fuite lui fait traverser une rue et qu'un passant ne remet pas le
  pied sur la chaussée hors d'un passage. Il tenait par chance, et trois tuiles de lampadaire ont
  suffi à le faire tomber. Il mesure maintenant le **contraste** avec une passante **sur la même
  fenêtre** — un rapport juge la règle, un seuil en pixels juge le trajet qu'une graine a tiré.
  ⚠️ **Essayé et annulé** : lui donner un vrai cap de retour à chaque image la collait au trottoir à
  vibrer contre la bordure dès que le chemin direct était barré. La ramener demanderait un vrai
  chemin (`Monde.chemin`), pas un cap — c'est écrit dans le juge.

- **Ce qui reste ouvert** : les quatre bras d'un croisement portent tous au-dessus de la rue
  **nord-sud** (c'est la géométrie des coins), jamais au-dessus de l'est-ouest. Ça ne se voit pas,
  mais un vrai carrefour les alterne.

## Notes

demande de Martin : « les feux pourraient être mieux — cherche sur le web des
représentations visuelles. Assure-toi que les feux et les voitures suivent la même logique.
Je veux des feux tricolores et un seul allumé à la fois », puis « mets les lumières qui
tiennent d'un seul bout sur le poteau et la partie dans le vide au-dessus de la route »,
« moins de lignes pour les traverses piétons », « ne mets pas de lampadaire aux
intersections, déplace-les ». La recherche donne mieux qu'une image : au **Québec les feux
sont HORIZONTAUX**, et leurs lentilles ont des **formes** — **carré** rouge, **losange**
jaune, **cercle** vert — pour qui ne distingue pas le rouge du vert. À 480 × 270, une forme
se lit là où une teinte se devine. Donc : un **vrai tricolore par mât, une seule lentille
allumée** ; un mât à **chacun des quatre coins** (ce qui règle le coin manquant), l'axe
suivant sa **diagonale** pour que de n'importe quelle approche un feu de son axe soit en
face ; une **potence** — le poteau planté au bord du trottoir, la tête en porte-à-faux
**au-dessus de la voie**, et un seul gabarit lu par **miroir** ; les **bandes des
traverses** ramenées à la norme (bande 0,50 m, vide 0,50 à 0,80 m : le vide est plus large
que la bande, c'était l'inverse), avec un pas qui **divise la tuile** — le motif boitait à
chaque couture ; et les **lampadaires écartés des coins**, qui sont la place du feu.

- ⚠️ **Une seule source** : `Monde.feuDeCirculation()` rend la couleur, `feuVert` en
  découle, le dessin en découle, le trafic obéit à `feuVert` — une lanterne ne peut plus
  montrer ce qu'un char ne respecte pas.
- ⚠️ Et ce que la passe a **découvert au passage** : les **lampadaires** étaient plantés sur
  les coins du croisement (la place du mât) — écartés de trois tuiles le long de la rue,
  **316 poteaux, zéro sur un coin** ; les **bornes-fontaines** aussi, et elles étaient
  **jaunes** et **en tuile** — les voilà **rouges**, en **décor** (donc une masse, une
  résistance, un bris), écartées des coins, et une borne défoncée **crache dix secondes**
  avec son bruit. Et un vieux juge a rougi sans qu'une ligne de son code change : celui de
  la fille de la Brume mesurait son écart **fuite comprise** — il tenait par chance, il
  mesure maintenant le **contraste** avec une passante sur la même fenêtre. 9 juges neufs
