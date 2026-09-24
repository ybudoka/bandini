# Une clôture, pas deux

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

bug de Martin, capture à l'appui : « je ne devrais pas voir de double clôtures d'épais comme
ça, seulement une d'épais ». Mesuré : **15 carrés de 2 × 2 tuiles de clôture** sur la graine
livrée, jusqu'à **17** sur d'autres — chaque cour arrière ceinturait son *propre* rectangle,
donc deux terrains voisins posaient **deux palissades collées** sur la même ligne mitoyenne.
Vu du jeu c'est pire que laid : une clôture s'enjambe en une seconde **immobile**, passer
d'une cour à l'autre en coûtait donc **deux**, et à la fourrière la seconde était du
**barbelé** — qui ne s'enjambe pas du tout. Une règle, deux endroits où elle s'applique :
`cote_deja_longe()` dit qu'un côté que **longe déjà une course de clôture** est un côté
clôturé, et `clore()` n'y repose rien — le terrain reste fermé par celle du voisin, une
tuile plus loin.

- ⚠️ **Les coins, eux, se posent quand même** : un coin tient deux côtés à la fois, et c'est
  lui qui fait *tourner* la course que cherche `elaguer_les_clotures`. La fourrière, elle,
  n'a pas le choix — **une seule grille**, c'est tout son lot — alors c'est au voisin de
  s'effacer (`degager_les_doubles()`, avant la première tuile de grillage ; `_terrain_vague`
  passe avant elle, par `_ilot_bati`).
- ⚠️ **« Sans voisine » se compte sur la VILLE**, pas sur la seule enceinte qu'on pose : le
  garde-fou anti-tuile-seule de `clore` ne regardait que ses propres tuiles, et du jour où
  deux voisins partagent une clôture, le coin d'une cour dont la suite est **chez le voisin,
  déjà au sol** tombait — la colonne mitoyenne perdait son tournant et l'élagage l'emportait
  à son tour. **Deux palissades collées devenaient aucune**, mesuré avant de s'en
  apercevoir. Résultat : 401 → 386 tuiles sur la graine livrée, **zéro carré de 2 × 2 sur 40
  graines**. 1 juge neuf (`test_une_cloture_fait_une_tuile_d_epais`, cinq villes)
