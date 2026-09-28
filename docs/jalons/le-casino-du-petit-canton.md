# Le casino du Petit-Canton

← [le plan](../plan.md) · [les jalons livrés](README.md) · [le Petit-Canton](le-quartier-chinois.md#fiche)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux un grand casino dans le quartier Petit-Canton ».

**Tranché avec Martin le même jour** :

- **Les deux** : un grand casino **légal** qu'on voit de la rue — le **Dragon d'or**, une façade de néons rouge et
  or, un portier —, et un **tripot clandestin** au sous-sol, qu'on découvre par une mission.
- **Quatre jeux** : les **machines à sous**, le **blackjack**, la **roulette**, et le **vidéopoker** du Brouillard
  (`videopoker.py`, réutilisé). _Puis, à la vague 2 (Martin, le même soir) : « ajoute des machines : roulette,
  poker, black jack et plus »_ — le **poker à trois cartes**, le **sic bo** et le **baccara** s'ajoutent.
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
2. **Les tables** : le **blackjack** et la **roulette**, un croupier à chacune ; les mises, les limites du jour — et
   le poker, le sic bo, le baccara.
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

### Vague 2 — les tables : blackjack, roulette, poker, sic bo, baccara — **livrée le 28 sept. 2026**

- **Cinq tables au milieu de la salle** (`casino.TABLES`), d'ouest en est : le **blackjack**, la **roulette**, le
  **poker à trois cartes**, le **baccara**, le **sic bo**. Un glyphe neuf, `!` (la table de jeu, un BLOC : la
  bordure de bois seulement là où le feutre s'arrête) ; ce qu'il y a SUR le feutre (le sabot et les cercles, la
  roue qui tourne plus vite quand on joue, les trois cartes, les cases JOUEUR et BANQUE, la cloche) se peint
  par-dessus (`Tables.dessinerSalle`). Un **croupier** derrière chacune (`qui: "croupier"`, le corps du commis en
  chemise blanche et pantalon noir, tenu à son poste — pas d'archétype neuf : le paquet est à son plafond). Les
  dix machines du milieu descendent en deux îlots au sud, loin de la porte ; la salle garde ses 32 × 9 (la
  grossir ferait glisser la ville), ses dix-huit machines et ses quatre vidéopokers.
- **Un menu par table, comme la machine à sous** (`static/js/tables.js`) : MISE (10, 20 ou 50 $ — des mises
  PAIRES, pour que le 3 pour 2 et la demi-paie de la banque tombent sur un dollar rond), PARI, puis le geste
  (DONNER, LANCER LA BILLE, SECOUER LES DÉS) ; au blackjack TIRER / RESTER, au poker JOUER / PASSER. Une ligne
  à choix change à ACTION (un cran) ou à GAUCHE / DROITE (le menu n'avait que haut, bas et ACTION : c'est la
  table qui lit les deux autres, `maj`). Quarante coups par jour à CHAQUE table.
- **Les règles, à Python** (`app/tables_de_jeu.py`), et leur jumeau en JS jugé coup pour coup sur deux mille
  paquets : le **blackjack** sans doubler ni séparer, le croupier tire jusqu'à 17 et reste à 17 souple, le
  naturel paie 3 pour 2 ; la **roulette européenne** (un seul zéro ; rouge, noir, pair, impair, ou un numéro
  plein à 35 pour 1 — la roue alterne ses couleurs, le navigateur les lit ainsi) ; le **poker à trois cartes**
  (la mise de départ, puis JOUER une mise de plus ou PASSER ; le croupier ouvre à la dame ; un bonus au départ
  sur la quinte, le brelan, la quinte flush) — préféré au hold'em : trois cartes et deux choix, ça se lit d'un
  coup d'œil et ça se joue à deux boutons ; le **sic bo** (petit, grand — un triple les perd —, ou un chiffre) ;
  le **baccara sans commission** (la banque qui gagne à six ne paie que la moitié ; l'égalité 8 pour 1).
- **La maison gagne à chaque pari, et le dit** (le retour du pari choisi dans l'aide du menu, arrondi en
  dessous) : roulette **97 %** (36/37, calculé) ; sic bo petit/grand **97 %**, un chiffre **92 %** (calculés sur
  les 216 jets) ; baccara joueur **98 %** (98,71), banque **98 %** (98,61), égalité **84 %** (84,25) — CALCULÉS
  sur toutes les suites de valeurs de cartes (`bac_retours_exacts`) ; blackjack **97 %** (97,9 mesuré, avec la
  stratégie de base) et poker **98 %** (98,0 par dollar misé, « jouer à partir de dame-six-quatre ») — MESURÉS
  sur deux cent mille mains, et deux millions pour choisir le chiffre. Au banc, quarante mille coups par table
  tirés par le hasard du navigateur retombent dessus.
- **Un paquet neuf à chaque main**, semé par la graine, le numéro du coup et un SEL PAR TABLE — jamais `B.rng()`
  (jugé : dix coups à chaque table ne décalent pas le tirage suivant). ⚠️ On ne peut donc PAS compter les cartes
  au blackjack : la vague 3 devra y mettre un sabot de plusieurs mains.
- ⚠️ **Payé tout de suite, annoncé quand la bille s'arrête** : payer à la fin de l'animation, c'était ne jamais
  payer celui qui ferme le menu pendant que la roue tourne. Le gain entre en poche au geste, en silence ; l'argent
  en haut du menu ne le montre qu'à l'annonce (jugé). Les animations se comptent en IMAGES DESSINÉES (la leçon de
  la vague 1 : un menu ouvert fige `B.t`).
- **Les sons** (« La cabane et le casino s'entendent », livré le même soir) : `Son.SFX.jetons` à la mise,
  `cartes_donnees`, `roulette_bille`, `des_sic_bo` ; à l'annonce, `gain_machine`, et `jackpot` pour dix mises de
  profit et plus (un numéro plein, un chiffre sorti trois fois). Chacun a son repli synthétisé.
- **Juges** : `test_tables_de_jeu.py` (27 : la maison gagne au chiffre affiché, 200 000 mains, chaque règle main
  par main, le tableau du baccara, la salle), `test_tables_js.py` (13 : chaque table au bouton, JS = Python coup
  pour coup, 40 000 coups sous 100 %, le hasard intact, la limite du jour, la bille avant l'annonce, GAUCHE /
  DROITE, un croupier par table, le bruit de chaque geste). Huit mutations, huit rouges (le naturel, le dé du jeu, le paiement, la limite,
  l'habit du croupier, GAUCHE / DROITE, le poker qui paie trop, le tableau de la banque).
- **Reste** : vague 3 (tricher : le sabot et le compte des cartes, la chaleur, les gardes), vague 4 (le tripot du
  sous-sol).

### Vague 3 — tricher : le sabot, le compte, la chaleur et les gardes — **en cours** (Martin, 28 sept. : « va y pour vague 3 »)
