# Le casino du Petit-Canton

← [le plan](../plan.md) · [les jalons livrés](README.md) · [le Petit-Canton](le-quartier-chinois.md#fiche)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux un grand casino dans le quartier Petit-Canton ».

**Tranché avec Martin le même jour** :

- **Les deux** : un grand casino **légal** qu'on voit de la rue — le **Dragon d'or**, une façade de néons rouge et
  or, un portier —, et un **tripot clandestin** au sous-sol, qu'on découvre par une mission.
- **Quatre jeux** : les **machines à sous**, le **blackjack**, la **roulette**, et le **vidéopoker** du Brouillard
  (`videopoker.py`, réutilisé).
- **La place** : laissée à Claude — mesurer les îlots, prendre celui qui laisse le plus de place à un grand
  bâtiment, et que la place du marché lui serve de parvis si c'est possible.
- **La maison gagne, mais on peut tricher** : chaque jeu rend moins qu'on y met, en moyenne, et le casino
  l'affiche (la règle du vidéopoker : un jeu d'argent qui paierait plus qu'un boulot casserait l'économie) ; un
  joueur malin peut tricher — compter les cartes au blackjack, par exemple — au risque d'être repéré et sorti par
  les gardes.

**Les vagues**, chacune jouable, jugée et livrée seule :

1. **Le bâtiment et la salle** : le Dragon d'or bâti au Petit-Canton (un lieu garanti de la bande, sa façade, son
   enseigne, son portier), sa grande salle à la mesure du bâtiment, une rangée de **vidéopokers** et de
   **machines à sous** (trois rouleaux, la table des gains mesurée comme celle du vidéopoker).
2. **Les tables** : le **blackjack** et la **roulette**, un croupier à chacune ; les mises, les limites du jour.
3. **Tricher** : compter les cartes au blackjack (et peut-être un complice à la roulette) ; la chaleur monte, les
   gardes repèrent, et on se fait sortir — ou barrer du casino pour une semaine.
4. **Le tripot du sous-sol** : une porte gardée, une mission pour l'ouvrir (avec le donneur du Petit-Canton,
   étape 3 du quartier), une salle enfumée où les mises sont plus grosses et où la maison triche aussi.

⚠️ **Ce que ça touche** (à relire avant de coder) :
- **Poser un lieu garanti dans la bande** : les îlots du Petit-Canton sont bâtis avec LEURS dés
  (`nord._ChantierNord._a_ses_des`) — un îlot spécial doit l'être aussi, et le juge « bâtir le quartier ne
  déplace rien de la bande » (`test_canton`) doit rester vert. ⚠️ La pièce DESSINÉE d'un lieu garanti doit avoir
  les mesures de son bâtiment (`test_carte.test_la_piece_a_les_mesures_de_son_batiment`).
- **Le hasard du départ** : le Petit-Canton est dans la bulle de naissance du terminus ; tout ce qu'on y change
  rebat les juges qui tiennent par une graine (mémoire « Juge vert par chance de graine »).
- **L'économie** : les tables de gains se MESURENT (des centaines de milliers de mains au juge), comme au
  vidéopoker ; une limite de pertes et de gains par jour, peut-être.
- **Le ton** (`ecrire-drole.md`, la fiche du quartier) : le casino est à ses habitants et à ses clients, jamais une
  caricature ; le gang, ce sont les Mantes, pas « les Chinois ».

## Notes

### Vague 1 — le bâtiment, la salle, les vidéopokers et les machines à sous — **livrée le 28 sept. 2026**

- **La place, mesurée** : l'îlot juste au nord de la place du marché, deux colonnes fusionnées sur UNE rangée
  (`hhcc¤<hh`, le plan du Petit-Canton) — 34 × 11 tuiles, un bâtiment de 32 × 9. ⚠️ Pas deux rangées : un lieu
  garanti se pose dans la bande la plus PROFONDE de son îlot et ouvre sur son devant ; dans un îlot de deux
  rangées, c'est la bande du nord qui l'emporte, et la porte donnait sur la ruelle de l'autre. Sur une rangée,
  la façade regarde la rue qui longe la place : la place est son parvis, fontaine comprise. Le casino borde
  aussi la rue principale, sur son flanc ouest.
- **Un lieu garanti de la bande, pas de `SPECIAUX`** (`app/casino.py`) : une lettre de plan à elle (`¤`, peu
  courante), un bâtisseur de `nord._ChantierNord` qui appelle le bâtisseur des lieux garantis de la ville avec
  la fiche `nord_casino`. La ville d'avant n'en sait rien (jugé). La salle est posée dans les pièces du chantier
  AVANT de bâtir, et `_ilot_bati` lit maintenant les mesures d'un lieu garanti dans `{**INTERIEURS,
  **self.pieces}` — sans elle, le casino faisait trois tuiles sur trois.
- **La grande salle** (32 × 9, à la mesure) : huit **machines à sous** le long du mur du nord, quatre
  **vidéopokers** (ceux du Brouillard, tels quels), le bar du fond, des plantes, trois clients et un commis ; le
  milieu reste libre pour les tables (vague 2).
- **La machine à sous** (`app/machine_a_sous.py`, `static/js/casino.js`) : 2 $ le tour, 80 tours par jour, trois
  rouleaux de vingt cases, neuf gains (du triple dragon à 400 fois la mise à la cerise du premier rouleau). ⚠️
  **Le retour est CALCULÉ, pas mesuré** : les 8 000 arrêts, tous également probables — 89,2 %, affiché 89.
  Son hasard est à elle (la graine et le numéro du tour, un sel qui n'est pas celui du vidéopoker), jamais
  `B.rng()`. Les rouleaux défilent puis s'arrêtent un à un — ⚠️ comptés en IMAGES DESSINÉES : un menu ouvert
  fige `B.t`, et ils défilaient pour toujours (vu à la capture).
- **La façade** : l'enseigne DRAGON D'OR (un genre neuf, `casino`, rouge et or, au bout de `devantures.GENRES`),
  sa plaque à idéogrammes comme tout le quartier, et — une enseigne de quatre tuiles sur trente-deux, c'était
  trop sage pour un « grand » casino — une **marquise de néon** de douze tuiles au-dessus de la porte, son nom
  en grandes lettres et des ampoules qui chassent (`Casino.dessinerMarquise`, au-dessus des gens).
- **Le portier** : un gardien figé à deux tuiles de la porte. ⚠️ Il naît À LA DEMANDE, quand on approche, et
  renaît s'il a été oublié — pas au démarrage : le Petit-Canton est dans la bulle de naissance du terminus. Et
  il naît hors de la suite des numéros, avec un dé prêté (jugé : le tirage suivant du jeu est le même).
- ⚠️ **Les bornes-fontaines de la bande** : fusionner deux îlots retire un croisement, et les bornes, tirées un
  dé par croisement à la file, glissaient d'un cran jusqu'à la Gare (`test_canton`, la bande ne bouge pas).
  `_ChantierNord.bornes` tire maintenant un dé PAR CROISEMENT, à sa position : les bornes de la bande ont été
  retirées une fois, et plus jamais après.
- **Juges** : `test_machine_a_sous.py`, `test_casino.py`, `test_casino_js.py` (au bouton ; JS = Python sur les
  8 000 arrêts ; le hasard intact ; 20 000 tours sous 100 % ; la limite du jour ; le portier sans rien
  déplacer ; la marquise). Deux mutations rouges (l'évaluation JS, le dé du portier). `test_canton` admet le
  casino sur la rue principale et son enseigne.
- **Reste** : vague 2 (le blackjack et la roulette, leurs croupiers), vague 3 (tricher), vague 4 (le tripot du
  sous-sol).
