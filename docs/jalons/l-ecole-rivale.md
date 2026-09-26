# L'école rivale : un gang qui sait se battre

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026), troisième des trois jalons des arts martiaux — après
[le répertoire](les-techniques-d-arts-martiaux.md#fiche) et [le dojo](le-dojo-du-quartier.md#fiche).

_Ce que ça donne :_ un gang qui connaît les coups de pied et les projections — pour avoir à qui rendre ce
qu'on a appris. Les autres gangs gardent les poings de rue (variés depuis le premier jalon).

- **Où** : dans [le quartier chinois](le-quartier-chinois.md#fiche), un 7e district (Martin, 26 sept. 2026) —
  il doit être livré avant.
- **Qui** : **un gang neuf** — tranché par Martin le 26 sept. 2026. Les élèves d'un dojo concurrent, avec
  leur couleur, leur territoire et leur garde-robe (`app/garderobe.py`, une garde-robe par archétype).
- ⚠️ **Ce que coûte un gang neuf** : un archétype de plus dans `pietons.py`, sa place dans les frontières de
  gangs (`pietons.frontieres`, la bagarre), et son territoire sur la carte — or « grossir un lieu garanti
  déplace la ville » : ce qu'on ajoute se pose en dernier, sans dé, et on compare les deux villes clé par clé.
  Relire la ligne « Les territoires des gangs bougent » du plan avant de poser le sien.
- **Comment ils choisissent** : `Techniques.choisir` pour eux aussi, avec leur liste de techniques ; leurs
  choix se tirent **à l'empreinte**, jamais par `B.rng()`.
- **Ce qu'on leur répond** : la parade-contre (retournement du poignet) prend tout son sens contre eux ; une
  projection subie par le joueur le couche sans l'assommer.
- ⚠️ **Ce qui guette** : le joueur projeté passe par `e.vol` comme un passant — la caméra, le volant et la
  coop (le deuxième joueur) doivent le suivre en l'air.

**Juges** : un membre de l'école rivale finit par projeter le joueur ; le joueur projeté retombe sur une tuile
libre ; aucun dé consommé.

## Notes

_Rien de livré._
