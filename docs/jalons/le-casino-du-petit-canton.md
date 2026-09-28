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

_Rien de livré._
