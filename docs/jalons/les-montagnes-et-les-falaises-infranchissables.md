# Les montagnes et les falaises infranchissables

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demande de Martin (21 sept. 2026) :_ « ajoute des falaises et montagnes infranchissable pour
délimiter les endroits strategique ».

Deux questions tranchées avec Martin avant de coder (l'endroit, puis le besoin) : le relief
délimite des **zones précises de la carte** (pas tout le pourtour au hasard), et sert à la fois de
**bordure de carte** et de **renfort autour de l'aéroport**.

- ⚠️ **La trame ne bouge pas.** Le chenal du 17 sept. l'a montré : changer une rangée ou une
  colonne de `COLONNES`/`RANGEES`/`RUES_V`/`RUES_H` re-tire toute la ville (26 juges sans rapport
  tombés d'un coup). Le relief se pose comme l'aéroport et l'Île-aux-Corneilles : en **ajoutant**
  au bord de la carte finie, jamais en la redessinant.
- ⚠️ **Est et sud seulement, pour l'instant.** Ajouter des colonnes après la dernière rue (à
  l'est) ne décale aucune coordonnée déjà posée — exactement comme l'aéroport a ajouté des
  rangées après la dernière rue (au sud). Ajouter au **nord** ou à l'**ouest** décalerait TOUT ce
  qui a un `x, y` dans la ville entière (portes, décor, personnages, missions, chantiers, zones…) :
  un chantier à part, bien plus gros que celui-ci, pas dans cette vague. Le nord et l'ouest
  gardent leur mur invisible déjà en place (`solidite` hors carte = 1, déjà infranchissable) —
  seulement, on ne le VOIT pas encore.
- ⚠️ **Ce qui se pose**, en tout dernier dans `generer`, sans un dé (comme `aeroport.poser`) :
  1. une chaîne de **montagnes à l'est** de la ville — des colonnes ajoutées après la dernière rue,
     une paroi de **falaise** en bordure (le mur qu'on voit depuis la ville) puis du rocher plein
     derrière, jusqu'au bord de la carte ;
  2. des **falaises au sud du large**, au-delà de l'aéroport — le « large » (`baie`) est de l'eau à
     perte de vue depuis le 21 sept. ; une ligne de falaises au bord lui donne une limite, et une
     raison de ne pas naviguer plus loin.
- ⚠️ Le relief est **infranchissable** comme une façade (`solide 1`) : ni à pied, ni en char, ni en
  bateau, ni à la nage — ce n'est pas une clôture qu'on enjambe ou qu'on défonce, ni de l'eau qu'on
  traverse à bout de souffle.
- ⚠️ Posé **après l'aéroport** (le dernier morceau de ville aujourd'hui) : rien de la ville
  d'aujourd'hui, aéroport compris, ne bouge d'une tuile.
