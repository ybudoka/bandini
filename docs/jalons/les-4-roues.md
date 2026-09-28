# Les 4 roues

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux aussi des 4 roues ».

**Tranché avec Martin le même jour** :

- **Où on les trouve** : **dans les Friches** (deux ou trois garés près des cabanons, à voler), **au chalet du
  rang** (le tien, garé à la deuxième planque, pour faire le tour du lac) et **chez le concessionnaire** (le lot
  d'usagés des Friches — le jalon « Les concessionnaires », en cours dans une autre session).
- **Ce qui le distingue d'une moto** — les quatre à la fois :
  - **rapide hors route** : plein régime sur l'herbe, la friche, le sable et la neige, là où les chars
    ralentissent ; un peu moins vite qu'une moto sur l'asphalte ;
  - **stable** : quatre roues, il ne se couche pas ; on n'en est éjecté qu'en frappant fort ;
  - **deux places** : un passager derrière (la coop à deux, ou un personnage en mission) ;
  - **il saute** : les rampes et les buttes le font voler, comme la moto.
- **Une activité dès le départ** : **une course dans les Friches**, sur le modèle de la course de motoneige —
  des fanions le long des sentiers, un chrono, une prime ; le 4 roues attend au départ.

**Les vagues**, chacune jouable, jugée et livrée seule :

1. **Le véhicule** : sa fiche au catalogue (`vehicules.py`), son dessin, sa conduite (hors route, stable, deux
   places, les sauts), et ses places garées — les Friches et le chalet du rang.
2. **La course des Friches** : le défi, ses fanions le long des sentiers, son chrono et sa prime.
3. **Chez le concessionnaire** : au lot d'usagés des Friches, quand ce jalon-là sera livré.

⚠️ **Ce que ça touche** (à relire avant de coder) :
- **Le modèle est la motoneige** (`docs/jalons/la-motoneige.md`, `vehicules.py` : `hors_neige`, `ejecte`) :
  un véhicule qui va vite sur SON terrain et moins ailleurs.
- **Les Friches sont dans la bande nord**, bâtie avec ses propres dés : ce qu'on y pose (des 4 roues garés,
  des fanions) se pose SANS DÉ, ou avec des dés à part, sinon la bande glisse (`test_canton`, « la bande ne
  bouge pas »). Et la bande est dans la bulle de naissance du terminus : le hasard du départ se rebat (mémoire
  « Juge vert par chance de graine »).
- **Le chalet du rang est un bloc** (`app/blocs/rang.py`) : `Monde.carte` y est le bloc (mémoire « Monde.carte est
  le bloc »).
- **Le catalogue des véhicules** est lu par beaucoup de juges (le trafic, la fourrière, la liste du quai, les
  dessins) : un véhicule neuf doit dire s'il roule dans le trafic (`freq` 0 : non), et avoir son dessin.

## Notes

_Rien de livré._
