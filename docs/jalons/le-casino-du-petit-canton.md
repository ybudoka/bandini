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
   gardes repèrent, et on se fait sortir — ou barrer du casino pour une semaine. ✅ _Livrée le 28 sept. 2026 (le
   complice, non : voir les notes)._
4. **Le tripot du sous-sol** : une porte gardée, une mission pour l'ouvrir (avec le donneur du Petit-Canton,
   étape 3 du quartier), une salle enfumée où les mises sont plus grosses et où la maison triche aussi. ✅ _Livrée le 29 sept. 2026 (voir les notes)._

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

### Vague 3 — tricher : le sabot, le compte, la sécurité — **livrée le 28 sept. 2026** (Martin : « va y pour vague 3 »)

- **Un SABOT au blackjack** (`tables_de_jeu.PAQUETS_DU_SABOT`, `COUPE`) : deux paquets battus ensemble, qui servent
  main après main ; le croupier rebrasse quand la carte de coupe sort, aux trois quarts (78 cartes données) — et ça
  s'entend (`sabot_brasse`). ⚠️ Deux paquets plutôt que six : le compte monte et descend plus vite, un sabot chaud
  arrive quelques fois par jour de jeu. Le sabot est DANS la partie (`B.partie.tables.sabot` : son numéro, qui sème
  son brassage — la graine, le numéro, un sel à lui, jamais `B.rng()` —, et combien de cartes en sont sorties) :
  on le retrouve au même point le lendemain. On le voit à droite du feutre, une pile qui baisse jusqu'au trait
  rouge de la coupe.
- **DOUBLER** (`bj_main`, le jumeau `Tables.bjMain`) : sur ses deux premières cartes, une deuxième mise et UNE
  carte. ⚠️ Sans lui, le compte ne pouvait pas payer : mesuré, sans doubler, même un compte de +6 par paquet ne
  rendait qu'un demi pour cent de plus — c'est en doublant, et avec les naturels, qu'un sabot chaud paie. Le
  blackjack de l'habitué au sabot rend donc **99 %** (99,1 mesuré sur un million de mains), affiché 99 (c'était 97
  sans doubler, paquet neuf à chaque main).
- **Les mises du blackjack, de 10 à 500 $** (`MISES_BLACKJACK`, paires) — l'écart qu'il faut à un compteur ; les
  autres tables gardent 10, 20, 50. Une ligne à elle dans `B.partie.tables` (`mise_bj`) : une mise de 500 $ posée
  au blackjack ne se retrouve pas sur le numéro plein de la roulette.
- **Compter** : on peut toujours compter soi-même (les cartes sont toutes montrées, le sabot baisse à vue). Et
  **après vingt mains au sabot, on SAIT compter** (« À FORCE DE REGARDER LE SABOT, TU SAIS COMPTER LES CARTES ») :
  une ligne COMPTER (NON / OUI) apparaît, et le compte Hi-Lo des cartes VUES s'affiche sous le sabot — le compte
  courant et le compte PAR PAQUET (le compte réel), en or à partir de +2. ⚠️ Les cartes VUES : jamais la cachée du
  croupier avant qu'il la retourne (jugé, et une mutation qui la compte rougit).
- **LA MESURE** (`test_tables_de_jeu.py`, un million de mains au sabot, les mêmes pour tous) : **sans compter**, à
  mise égale, l'habitué rend **99,1 %** — la maison garde près d'un pour cent ; **un compteur parfait** qui mise de
  10 à 500 $ selon le compte par paquet avant la main (`compteur_parfait` : 10 sous +1, puis 20, 50, 100, 200, et
  500 à +5) rend **101,2 %** par dollar misé, environ **+0,85 $ par main** (sur trois graines : 101,2 à 101,9 %) ;
  un **compteur prudent** (de 10 à 100 $) rend 100,4 à 100,8 %, +0,13 à +0,24 $ par main. Le compte paie, un peu —
  et quarante mains par jour, c'est quelques dizaines de dollars : pas de quoi casser l'économie.
- **La SÉCURITÉ** (`SURVEILLANCE`, `Casino.surveillerMise` / `surveillerGain` / `refuseLaMise` / `refuseLaPorte`) :
  un œil, une chaleur de 0 à 100 qui n'a RIEN d'une étoile de police. Elle monte quand la mise du blackjack saute
  (une fois et demie sa mise d'habitude, une moyenne qui glisse) alors que le sabot est chaud — par doublement de
  la mise, par point de compte au-delà de un ; et quand, au-delà de mille dollars gagnés aux tables dans la
  journée, on gagne encore. Elle baisse à chaque main à sa mise d'habitude, quand la mise saute sur un sabot FROID
  (on a l'air d'un joueur, pas d'un compteur : la couverture), et de six points par heure loin des tables. On la
  voit en bas du menu de chaque table : un œil et cinq crans, vert, jaune, rouge, le mot SÉCURITÉ.
  - À **50** : un **garde** (le garde de la salle, près de la porte — né à la demande, hors de la suite, avec un
    dé prêté, comme le portier ; sans la batte de son archétype, vu à la capture) vient se poster à ton épaule :
    « TU COMPTES BIEN. MOI AUSSI, JE COMPTE. », un grésillement de talkie (`talkie_securite`).
  - À **100** : à ta mise suivante (jamais au milieu d'une main), il t'arrête la main — « LA MAISON TE REMERCIE. LA
    PORTE AUSSI. » — et **te reconduit à la porte** (le fondu de la sortie). Le portier ne te rouvre que **le
    lendemain** (« PAS CE SOIR, L'AMI. », l'invite dit LE PORTIER et plus ENTRER) ; à la **récidive**, **une
    semaine** (« TA PHOTO EST AU MUR, L'AMI. ELLE EST BELLE. »). Pas une étoile (jugé).
  - **Frapper la sécurité** (le garde, le portier) : barré une semaine d'un coup, et là, oui, la police (au moins
    une étoile).
  - Mesuré sur trois cents jours de quarante mains : qui mise toujours pareil (à 10 comme à 500 $) n'est jamais
    inquiété ; le compteur parfait est averti trois jours sur quatre et sorti plus d'un jour sur deux, vers sa
    quinzième main ; le prudent (10 à 100 $) sorti un jour sur six ; et quelques grosses mises sur un sabot froid le
    couvrent encore mieux (un jour sur douze).
- **MACHINES SANS LIMITE** ne lève que le plafond du jour : au-delà de quarante mains, le sabot sert et se rebrasse
  pareil, et l'œil voit toujours (jugé ; une mutation où la triche aveuglerait la sécurité rougit).
- **Le complice à la roulette : pas fait.** Il fallait un personnage de plus à la table, un signal qu'il te fait
  (lisible sans texte), et une règle qui le rend payant sans casser la roue — ni lisible, ni pas cher. Laissé pour
  plus tard, si Martin le veut.
- **Les sons** : `sabot_brasse` (le croupier brasse deux paquets) et `talkie_securite` (le talkie du garde), générés
  par ElevenLabs, chargés en approchant du casino (`audio.LIEUX['casino']`), chacun avec son repli synthétisé.
- **Juges** : `test_tables_de_jeu.py` (doubler, le Hi-Lo, la coupe, la MESURE sur un million de mains, la sécurité sur
  trois cents jours, ce que l'œil pense d'une mise), `test_triche_casino_js.py` (JS = Python sur deux mille bouts de
  sabot et deux mille avis de l'œil ; le sabot au bouton qui se rebrasse et s'entend ; apprendre à compter et le
  compte des cartes vues ; doubler au bouton ; l'avertissement, la sortie sans étoile, la porte refusée, le
  lendemain, la semaine ; miser pareil ne chauffe pas ; frapper un garde ; le hasard du jeu intact et le dé prêté
  du garde ; MACHINES SANS LIMITE ; quarante mille mains au hasard du navigateur). Treize mutations, treize rouges.
- **Reste** : vague 4 (le tripot du sous-sol).

### Vague 4 — le tripot du sous-sol : la barbotte du Pouce — **livrée le 29 sept. 2026** (Martin : « va y »)

- **Le donneur du Petit-Canton, d'abord** (l'étape 3 du quartier commence ici) : **Irène Lam**, trente ans croupière
  au Dragon d'or, reine du mah-jong, qui vient chaque soir au bout du bar « surveiller le travail des jeunes »
  (`point:irene`, dedans : elle naît quand on entre, pas un dé en ville). Honnête ET joueuse — tricher aux dés, c'est
  voler quelqu'un qui te regarde dans les yeux. Sa fiche : [`docs/personnages/irene.md`](../personnages/irene.md).
  ⚠️ **Proposée par Claude, à valider par Martin** (nom, histoire, voix) : voir la fiche du quartier.
- **c01, _La barbotte du Pouce_** (`app/missions/c01.py`, après m6, 400 $) : Irène appelle ; au bar, elle raconte le
  Pouce Vachon, qui a loué la cave « pour entreposer des chaises » et y plume le quartier ; on entre avec un jeton de
  laiton, et ses rabatteurs (deux Cravates, aux poings) en distribuent au terminus. On les couche, on rapporte le
  jeton au Dragon d'or (un `aller` de six tuiles sur le lieu garanti de la bande — `test_missions` admet maintenant
  `casino.CASINO`). À la fin, elle livre le truc du métier : **les pipés sont plus jaunes que les vrais**. Scènes
  écrites (la coupe en `ensemble` PUIS la réplique : c'est la voix qui retient la scène).
- **La porte gardée** (`tripot.PORTE`) : une **barrière de la PIÈCE**, au format de `carte.BARRIERES` (comme les
  serrures de la villa), condition `apres: c01`, pleine, qu'on ne force pas — dans le coin sud-est de la grande salle,
  muré d'un pan, devant l'escalier. `Monde.entrer` donne maintenant ses `barrieres` à la carte d'une pièce (aucune
  ailleurs), et `Jeu.rendre` les peint dedans : une porte de laque rouge, ses clous de laiton, son judas (`decor:
  porte_tripot`). Un gros bras du Pouce la garde : « SUR INVITATION, MON CHAMPION. », puis « LE JETON? ENVOYE,
  DESCENDS. ». ⚠️ Pas dans `carte.BARRIERES` : ce tuple est résolu en rectangles de la VILLE, et chaque fiche doit y
  être (`test_barrieres`).
- **Le tripot** (`tripot.PIECE`, `nord_tripot`, 24 × 9) : sous la grande salle, par l'escalier (`vers`). ⚠️ Plus
  petit qu'elle : le bâtiment se taille à la plus grande pièce de sa suite (`carte.mesures_de_la_suite`), et un tripot
  plus grand aurait fait grandir le Dragon d'or — la ville aurait glissé. La table de la **barbotte** au milieu, le
  **Pouce** derrière (veston moutarde, moustache — le corps du commis), deux **gros bras** (le corps du garde, en cuir
  noir, sans batte), le bar, deux tables de cartes, des caisses ; la porte `D` du bas est la sortie de secours des
  descentes de police. `pouce` et `gros_bras` rejoignent `carte.QUI_DEDANS` ; pas d'archétype neuf (le paquet).
- **Enfumée, mal éclairée** (`Tripot.dessinerFumee`, par-dessus les gens) : un voile qui noircit les coins, une lampe
  à abat-jour vert qui pend au-dessus de la barbotte et son halo, et neuf nappes de fumée grise qui dérivent et
  respirent d'après `B.t`, sans un dé. Pas de musique en bas (`MUSIQUES_DE_COMMERCE` n'a pas `nord_tripot` : la toune
  du casino se tait en descendant) ; la rumeur de la salle (`tripot_salle`, ElevenLabs, en boucle) et les dés contre la
  planche (`des_barbotte`), chargés avec les sons du casino (`audio.LIEUX["casino"]`), chacun avec son repli.
- **La barbotte** (le jeu des arrière-boutiques de Montréal) : deux dés ; POUR sur 3-3, 5-5, 6-6, 5-6, CONTRE sur
  1-1, 2-2, 4-4, 1-2, le reste se relance ; **un sur deux**, et le Pouce vit de sa **piastre**, 5 % de chaque gain :
  honnête, elle rend **97,5 %** (calculé ; affiché 97). **Mises de 100 à 1 000 $** (dix fois celles d'en haut), vingt
  coups par jour. Au menu : PARI, MISE, MISER — la main du Pouce passe sur le feutre et pose les dés —, puis LANCER,
  CHANGER DE CÔTÉ, DÉNONCER LES DÉS. Son hasard est à lui (la graine, le numéro du coup, un sel), jamais `B.rng()`.
- **LA MAISON TRICHE, ET ÇA SE VOIT** : à partir de 500 $, six fois sur dix, le Pouce pose ses **dés pipés** contre le
  côté que tu as pris — de la vieille ivoire, **plus jaune** que les vrais (`Tripot.IVOIRE`) ; les deux paires pèsent
  leurs faces 3-3-2-3-2-2 ou 2-2-3-2-3-3 sur quinze. Qui les voit a trois choix :
  - **lancer quand même** : le côté du Pouce sort sept fois sur dix — la table rend **60 %** (calculé) ;
  - **DÉNONCER** : justes, le Pouce rend la mise (« ÇA S'EST GLISSÉ TOUT SEUL, MON AMI. ») et ne pipe plus de la
    journée — mais +40 de méfiance ⚠️ (**corrigé le 29 sept. 2026**, [la barbotte à l'essai](la-barbotte-du-pouce-a-l-essai.md#notes) :
    **cinq coups** propres, affichés au menu, et +10 — une journée sans dé jaune, sans un mot, se lisait comme un
    tripot brisé) ; faux (des dés honnêtes), les gros bras te sortent par la porte d'en arrière,
    la mise perdue, l'escalier refusé jusqu'au lendemain ;
  - **CHANGER DE CÔTÉ** une fois ses pipés posés : ils jouent pour toi — **135 %** (calculé) ; le Pouce le voit
    (+25, et +15 si tu gagnes).
  La **méfiance** (cinq crans en bas du menu, LE POUCE) fond de 30 par jour ; à 100, à la mise suivante, les gros bras
  te raccompagnent et l'escalier te reste fermé **une semaine** (`refuseLEscalier`). Frapper le Pouce ou un gros bras :
  une semaine aussi. **Jamais une étoile** : dans un tripot, on n'appelle pas la police.
- **LA MESURE** (`test_tripot.py`, 4 500 jours de vingt coups, trois graines) : à 200 $ (sous le seuil), **97,3 %** ; le
  **naïf** à 1 000 $ qui lance quoi qu'il voie, **75,0 %** (−5 000 $ par jour : la leçon est chère) ; qui **dénonce**
  les pipés, **98,2 %** — mais il finit dehors de temps en temps (345 sorties) ; depuis les cinq coups propres, **98,3 %** et
  sept sorties ; qui **retourne** les pipés, **117 %**
  par dollar misé, sorti 645 fois, l'escalier fermé 3 855 jours sur 4 500 : **+133 $ par jour** en moyenne — pas de quoi
  casser l'économie. Au banc, 20 000 coups du navigateur retombent dessus (≈ 97 % et ≈ 75 %), et deux mille coups
  retournés rendent ≈ 135 %.
- **Juges** : `test_tripot.py` (7 : un sur deux et la piastre, les pipés calculés, les faces pondérées, les quatre
  façons mesurées, le tripot plus petit que le casino, la porte qui garde vraiment l'escalier, la ville finie) et
  `test_tripot_js.py` (11 : JS = Python sur deux mille suites de tirages ; la porte avant et après c01, au clavier, et
  l'escalier au bouton ; un coup au bouton et la limite du jour ; les pipés qu'on VOIT, seulement au-dessus du seuil ;
  dénoncer juste et faux ; retourner jusqu'à la sortie ; 40 000 coups ; le hasard du jeu intact ; frapper les gens du
  Pouce ; la fumée et la rumeur ; **c01 jouée au bouton**, de l'appel d'Irène à la descente). Voisins ajustés :
  `test_missions` (le repos d'Irène, le lieu du casino), `test_interieurs` (`barbotte` servi),
  `test_un_comptoir_reste_ouvert_js` (MISER mène à LANCER), `test_tables_js` (un croupier se juge à son POSTE : lire sa
  tuile à l'image 120 tenait par la graine, et deux gens de plus dans la salle l'ont rebattue).
- **Reste** : rien de la fiche. Le complice de la roulette (vague 3) n'est toujours pas fait ; la suite de l'étape 3
  du quartier (faire tomber le Pouce pour de bon ?) est à écrire avec Martin.
- ✅ **29 sept. 2026 — le Pouce est tombé** ([le Petit-Canton, étape 3](le-quartier-chinois.md#notes)) :
  pendant c02, la barbotte offre **GLISSER TES DÉS** quand les pipés sont sur le feutre (`tripot.PREUVE`) ; après c04,
  le tripot **a changé de mains** (`tripot.REPRISE`) — plus de Pouce ni de gros bras (en bas comme à la porte d'en
  haut), le vieux Chan tient la table, jamais de pipés, plus de méfiance ni de semaine barrée, plus rien à dénoncer,
  et la piastre va au quartier : le « RETOUR 97 % » du menu cesse de mentir.
