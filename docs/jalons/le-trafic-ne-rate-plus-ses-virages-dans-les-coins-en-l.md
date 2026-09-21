# Le trafic ne rate plus ses virages dans les coins en L

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (capture du coin en L des Quais, 149,189 : la route à quatre voies du nord
tourne vers une route à deux voies, l'eau à une tuile) : « améliore les virages pour les
situations complexes comme ça » — c'est le trafic. Mesuré au banc : sur 2 238 entrées de
boîte, 24 font TROIS virages, toutes dans les onze coins en L de la ville. `prochaineCible`
tire sa sortie (tout droit, à droite, à gauche) sans savoir si la boîte l'a : un char qui
descend du nord et voulait « tout droit » traverse la boîte jusqu'à la rangée du bord de
l'eau, n'y trouve rien, puis zigzague (ouest, nord, ouest) :
`149,188v 149,189v 149,190v 148,190< 148,189^ 147,189<`.

- ⚠️ Le correctif : la sortie voulue est la première de la liste qui PART DE LA BOÎTE, tout
  droit devant — sinon la suivante ; et une fois tourné, on ne change plus d'avis. Le tirage
  « tout droit » devient « tout droit, sinon à gauche » pour que les T gardent le partage
  qu'ils avaient (77 % à gauche depuis le pied du T).
- ⚠️ Un juge : de chaque entrée de chaque boîte, avec les trois préférences et en poursuite,
  UN virage au plus, pris à la première tuile d'où il mène — rouge avant (24 zigzags).

## Notes

Livré le 21 sept. 2026. `prochaineCible` (`static/js/vehicules.js`) ne prend plus pour sortie
voulue le premier tirage : c'est la **première de la liste qui part de la boîte**, d'ici ou d'une
tuile plus loin tout droit (`sortieDevant`, qui promène `peutSortir` le long du cap). Le tirage
« tout droit » devient « tout droit, sinon à gauche » : au pied d'un T, c'est ce que le char
faisait déjà en traversant jusqu'au fond, et le partage des T ne bouge pas.

- Au coin de la capture (149,189), un vrai char du trafic qui descend la voie 149 en voulant
  « tout droit » : avant, `149,188 149,189 149,190 148,190 148,189 147,189` — il plonge dans la
  rangée du bord de l'eau, recule, remonte ; après, `149,188 149,189 148,189 147,189`, le même
  chemin que celui qui voulait tourner à droite.
- Le juge des boîtes d'avant ne demandait que de **sortir**. Le nouveau,
  `test_trace_js::test_d_une_entree_de_boite_un_seul_virage_pris_au_plus_tot`, part de chaque
  entrée de chaque boîte (5 222 départs par heure : les trois préférences, et la poursuite avec le
  joueur loin dans chacune des quatre directions), à trois heures (les deux pointes et midi) : un
  virage au plus, pris à la première tuile d'où il mène, et « tout droit » au pied d'un T tourne à
  gauche. Sur la base, à midi : 85 départs à trois virages et 284 virages pris trop loin ;
  après : zéro, aux trois heures.
- ⚠️ **Ce qui change ailleurs, et c'est voulu.** Hors poursuite, aucune sortie ne change de
  direction ; 97 départs sur 5 222 changent de VOIE : le virage à gauche depuis le pied d'un T ou
  d'un L prend la voie intérieure (la première qu'il croise) au lieu de filer à la voie du fond. En
  poursuite et aux heures de pointe, le char qui ne trouvait pas sa première sortie se rabattait
  sur « ce qu'il trouvait au fond » ; il prend maintenant sa **deuxième** — la police sur rails va
  vers le joueur, et la pointe vers le cœur de la ville, même là où la première n'existe pas.
- ⚠️ La fiche prévoyait aussi qu'un char engagé « ne change plus d'avis » (`v.sortie = [voulu]`).
  Retiré : la mutation qui l'enlève ne rougit aucun juge — dans les boîtes de la ville, une fois la
  bonne sortie choisie, aucune autre ne devient atteignable le long du nouveau cap.
- Mutations : sans le correctif (la base), sans `sortieDevant`, et avec l'ancien ordre « tout droit,
  à droite, à gauche » : rouge les trois fois.
