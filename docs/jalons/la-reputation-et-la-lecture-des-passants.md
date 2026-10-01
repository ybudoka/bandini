# La réputation et la lecture des passants

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : La réputation et la lecture des passants (**ajout**, taille 2) — ⚠️ à trancher par Martin_

_Demande de Martin (18 sept. 2026) :_ « cherche aussi pour cyberpunk et watchdog ».

La deuxième tournée du net (Watch Dogs, Cyberpunk 2077) n'ajoute **aucun type d'objectif** :
les gigs des _fixers_ de Cyberpunk sont déjà le « donneur qui hèle », et le **choix** au
dialogue (le centre de Cyberpunk) est déjà toute la colonne `ferme`/`donne` de M16. Un seul
patron leur appartient encore, et il ne tient pas dans une mission : **lire un passant et
choisir quoi en faire** — le profiling de Watch Dogs, où chaque piéton porte un état du monde
(« ancien combattant », « revenu 8 000 $ », « harcèlement ») et où **agir** change ta
réputation.

Ce que ça donne, dans l'esprit de la ville : Bandini a déjà un levier de réputation en germe
(`casier` de M11, `ami`/`ennemi` de M16, la rumeur qui se tait devant une arme de M15), mais
il ne dit **jamais** ce qu'un passant pense de toi. La lecture comble ce trou. Elle n'est
**pas** une activité de boulot, et surtout **pas un cent-et-unième type d'objectif** : un
objectif `lire` pousserait à du `if (slug === '…')`, et la règle de M16 l'interdit. C'est un
état continu de la ville, un module autonome comme les frénésies — **branché dans `jeu.js`
`maj()`, jamais dans `BOULOTS`**.

- **Lire** — au contact d'un passant (la bulle « Hé ! » de M6, ou un geste volontaire), on
  voit **une** ligne sur lui : un mot-clé sans enjeu mécanique (« retourne chanter le
  vendredi », « doit 200 $ à Sal », « a perdu Biscuit »). Une ligne = de la **couleur**, pas
  un fil à tirer — aucune mission n'en dépend, et rien ne s'y enchaîne. C'est exactement la
  promesse de M15 « la ville te parle », étendue des radios aux visages.
- **La réputation** — les gestes existants y écrivent déjà (payer pour un débiteur en d04,
  couvrir un témoin en f06, tuer un intouchable) : un compteur par district, invisible ou
  lisible au carnet, qui change **une** chose concrète — un passant d'un district où tu es
  bien vu ne te dénonce pas à la police (le vol de char de Watch Dogs) ; là où tu es mal vu,
  il **appelle** même sans étoile. C'est le seul effet, borné et dur : pas de statistique de
  peur générale (M15 en a déjà une), pas de prix à l'acte.
- ⚠️ **Deux garde-fous non négociables**, calqués sur les frénésies : les enfants restent
  **illisibles** (pas de profil sur un gosse), et **rien ne se tire au dé de la partie** — une
  ligne de passant se lit à l'empreinte, comme le bris d'aqueduc, jamais au `B.rng()`. Et un
  troisième, propre à la lecture : **une lecture ne coûte rien et ne rapporte rien** ; si
  elle se met à donner, elle devient l'objectif qu'on a juré de ne pas écrire.

⚠️ **Le vrai coût n'est pas le code, c'est l'écriture** : 50 à 100 lignes de passant, une par
quartier, rédigées et auditées comme les répliques de M15 — sans elles, la lecture est un
menu vide. C'est à Martin de dire si la ville en veut, et dans quelle vague.

**Tranché par Martin le 1er oct. 2026** :

- **Les deux**, en deux vagues : **vague 1, la lecture** (une ligne par passant), **vague 2, la réputation** (par
  quartier ; elle ne change que la délation).
- **On lit au bouton tenu** (comme Watch Dogs) : tenir un bouton en regardant un passant affiche sa ligne au-dessus de
  lui ; rien ne s'affiche sans qu'on le veuille.
- **La réputation est chiffrée** : une jauge par quartier, au carnet et sur la carte.
- **Une soixantaine de lignes** de passant, huit à dix par quartier, dans le ton de `docs/ecrire-drole.md`, relues
  avant de livrer.

**Juges** : une ligne de passant ne pèse sur aucune mission (grep : aucun slug ne la lit) ;
un enfant n'a jamais de profil ; la réputation ne change rien d'autre que la délation, et elle
survit à une sauvegarde ; lire n'est jamais un objectif du catalogue.

## Notes

### Vague 1 — la lecture, livrée le 1er oct. 2026

- **Le geste** : on **tient** LIRE — Y au clavier (au-dessus de H, VISER), la **gâchette de gauche** à pied à la
  manette (`Entree.gachetteLit`, le pendant de VISER à droite ; au volant elle reste le frein), le bouton **LIRE** au
  doigt (au-dessus d'ARME ; il s'éteint hors de la marche). L'écran COMMANDES le montre à la page À PIED (« LIRE UN
  PASSANT »). On lâche, la fiche s'en va.
- **Qui on lit** (`static/js/lecture.js`) : celui qu'on vise s'il est lisible, sinon le plus proche dans le regard
  (40° de chaque côté, 120 px, une ligne de vue). Tant qu'on tient, la fiche **ne saute pas** d'une tête à l'autre
  (elle garde sa cible jusqu'à 160 px). Jamais **un enfant** — ni un intouchable, ni un corps d'enfant, ni un ado :
  les lignes sont écrites pour des grandes personnes —, ni un personnage, une bête, un figurant de mission. Au volant,
  rien.
- **Sa ligne** : le lot de son **quartier** (la zone de la ville sous ses pieds ; dans une pièce, celle de la porte
  passée ; un bloc ou la baie n'ont rien à dire), **à l'empreinte** de son identifiant (`hash2`, jamais `B.rng`), et
  il la **garde** (`e.lecture`) : il ne change pas d'histoire en traversant une rue.
- **66 lignes** (`app/lectures.py`) : neuf au Faubourg, huit aux Érables, à la Shop, aux Quais, à La Pointe, au
  Petit-Canton et à la Gare, trois aux Friches, sur l'île et à l'aéroport. Un fait, puis la chute ; on frappe en
  haut (Sal, Prévost, les gangs). Muettes : écrites pour l'œil, pas de voix.
- **Rien ne se gagne** : `Lecture` ne touche ni la partie ni le passant (il ne s'arrête pas, ne se retourne pas), et
  aucune mission ni aucun objectif ne la lit (juge par grep).
- **Le poids** : les lignes voyagent dans la **suite** du paquet (`DANS_LA_SUITE`, après l'écran titre) — 3 641 bruts,
  1 914 gzip. La suite passe à 28 533 / 11 844 ; plafond relevé de 25 000 → 29 000 bruts et 10 500 → 12 500 gzip,
  **tranché par Martin** le 1er oct. 2026. Sans la suite, tenir LIRE ne fait rien et ne lève rien.
- **Juges** : `test_lectures.py` (7) et `test_lectures_js.py` (11, au clavier, à la manette, au doigt) ; douze
  mutations, toutes mordues (le cône, la garde de la cible, les enfants, le dé, la ligne gardée, le volant, le
  relâchement, la peinture, la gâchette, un passant qu'on dérange, la suite absente, la touche). Le bouton tactile
  est mesuré avec les autres (`test_navigateur`, aucun chevauchement).
