# Rien ne se chevauche plus

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin, capture à l'appui (« empêche que les choses se chevauchent ») : le joueur
**debout dans la carrosserie** du camion-restaurant. Deux chevauchements, deux causes.

- ⚠️ **Le décor** : la collision n'était pas absente, sa **forme** était fausse. Un
  camion-restaurant fait 44 px de large et 8 px de profond ; son unique cercle (r 16) tenait
  dans la profondeur, donc il laissait **6 px de carrosserie** libres de chaque côté — et le
  cercle qui aurait couvert la largeur (r 22) aurait posé un mur invisible de 22 px devant
  et derrière. Un cercle ne sait pas tenir un rectangle. Chaque décor carré porte maintenant
  une **boîte au sol** (`sol: [demi-largeur, demi-profondeur]`, mesurée sur les `fillRect`
  de son peintre) dont on ressort par le côté le moins enfoncé : banc, caisse, fontaine, les
  deux kiosques, la roulotte, le camion. L'arbre, lui, **garde son cercle** : son tronc fait
  3 px et sa cime est peinte en hauteur — on passe sous une cime, pas dans un comptoir (même
  raison pour le parasol du kiosque à hot-dogs).
- ⚠️ **La foule** : personne ne poussait personne. Deux passants qui se croisaient se
  superposaient **exactement** — mesuré en marchant deux minutes : **1032 paires** enfoncées
  l'une dans l'autre en 960 images, jusqu'à **9,9 px**, soit deux corps de 10 px
  parfaitement confondus. `demeler()` sépare maintenant tout le monde à chaque image, sur un
  index **refait** (celui du début d'image est périmé : il laissait passer exactement les
  paires qui venaient de se rejoindre), en poussant par `deplacerCercle` — sinon on se
  pousse mutuellement **dans un mur**, ce qui est pire. Après : **0,1 px** au pire, dès la
  première image.
- ⚠️ Et l'on ne **naît** plus dans quelqu'un : les deux branches de `placeDeNaissance`
  rendent un **centre de tuile**, donc deux naissances sur la même tuile, c'est le même
  pixel (deux agents nés l'un dans l'autre à l'image 31).
- ⚠️ Le plafond de séparation doit passer **devant les jambes les plus rapides** : fixé à
  1,5 px il arrêtait bien le joueur qui **marche** (1,2) et laissait passer celui qui
  **sprinte** (2,1) — il suffisait de tenir MAJ pour entrer dans le vendeur ; il se calcule
  désormais sur les vitesses du paquet.
- ⚠️ Et « figé » veut dire **il tient son poste**, pas **c'est un poteau** : vraiment
  immobile, un donneur planté sur le trottoir bouchait la rue **pour toujours** — l'agent
  lancé aux trousses du joueur venait buter sur Ti-Guy et y restait (260 images sur place,
  l'arrestation n'arrivait jamais). Il se laisse donc bousculer de 10 px et **rentre chez
  lui** ; au-delà il redevient un mur, sinon on promènerait un personnage d'histoire
  jusqu'au port. 6 juges (on ne se tient dans aucun décor par aucun des quatre côtés, la
  portée de recherche couvre le **coin** de la plus grosse boîte — sinon le camion n'est
  même pas trouvé et rien ne rougit —, la foule ne se chevauche plus et ne naît plus
  empilée, courir ne traverse pas les gens, le figé cède puis revient). Coût : **0,337 →
  0,356 ms par image** à 5★ avec 1992 entités
