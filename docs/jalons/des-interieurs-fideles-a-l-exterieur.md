# Des intérieurs fidèles à l'extérieur : la revue complète

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (29 sept. 2026)_, après la deuxième vague du bidonville de la gare (on entre dans les maisons
pauvres, et on y trouve un logement ordinaire) : « je veux des intérieurs toujours représentatifs de l'extérieur.
Ajoute au plan que je veux une revue complète des intérieurs dans ce sens ».

**La règle, pour toute la ville et pour de bon** : ce qu'on voit en poussant une porte doit se lire comme la
suite de ce qu'on a vu dehors. Une maison pauvre a un intérieur pauvre, une maison cossue un intérieur cossu, un
logement du Petit-Canton est au Petit-Canton, un bungalow de banlieue n'est pas un plex du Faubourg.

**Ce qui tient déjà** (livré, à ne pas refaire) :

- **La taille** : la pièce a les mesures de sa part de bâtiment
  ([l'intérieur à la mesure du bâtiment](l-interieur-a-la-mesure-du-batiment.md#fiche)), et un étage a la même
  empreinte que le rez-de-chaussée.
- **Le nom du commerce** suit la taille de son bâtiment
  ([le commerce à la mesure de son bâtiment](le-commerce-a-la-mesure-de-son-batiment.md#fiche)).
- **Un peu du standing, pour les commerces seulement** : `piece_de_commerce(standing=…)` (le comptoir d'un commerce
  pauvre, les plantes d'un commerce cossu —
  [des quartiers qu'on reconnaît](des-quartiers-qu-on-reconnait-riches-pauvres-et-zones.md#fiche)).

**Ce qui manque** (le premier inventaire, à compléter par la revue) :

- **Les logements ne suivent rien** : `piece_de_logement` ne reçoit ni le standing, ni le district, ni le genre
  du bâtiment. Les maisons pauvres de la gare, les maisons cossues des Érables et les logements du Petit-Canton
  ont le même intérieur.
- **Le district** : un intérieur du Petit-Canton, des Quais, de La Shop ne dit rien de son quartier.
- **Le genre du bâtiment** : bungalow, plex à escalier, maison de brique, hangar — dehors on les distingue, dedans
  non.
- **Les matériaux et l'état** : la façade (brique, bois, planches), les fenêtres placardées, le fer rouillé — dedans,
  des murs propres et des meubles neufs partout.
- ⚠️ **Le mur de la porte, vu de dedans, n'est pas un mur de la pièce** — Martin (29 sept. 2026) : « les portes
  et murs des portes intérieur doivent avoir des murs harmonisés ». Dans le logement `nord_logement_1001`
  (capture du 29 sept.), trois murs sont en plâtre gris et le quatrième, celui de la porte, est la **façade
  de brique rouge** et ses fenêtres bleues, peinte comme dehors (le plan de la pièce emploie les tuiles de
  façade `F`, `W`, `D`). Le mur de la porte et la porte elle-même doivent être du même mur que les trois
  autres : même matière, même couleur, fenêtres et porte vues de l'intérieur. À vérifier dans **toutes** les
  pièces (logements, commerces, lieux garantis, blocs), avec un juge qui compare la matière du mur de la porte
  à celle des autres murs.
- **Les pièces faites à la main** (les lieux garantis, les blocs de carte, les pièces des missions) : chacune à
  relire contre son extérieur.

**La revue** : faire l'inventaire de tous les intérieurs (chaque famille de pièce × standing × district × genre
de bâtiment, plus chaque pièce faite à la main), avec une capture dedans et dehors pour chacun ; dresser la liste
des écarts ; puis corriger par vagues, chacune jouable et jugée.

- ⚠️ **Le contenu, pas les mesures** : la taille est tenue par ses juges, on n'y touche pas.
- ⚠️ **Rien au dé** : l'intérieur se décide à ce qu'on lit dehors (standing, district, genre, empreinte), comme
  la pièce de commerce suit déjà le standing du bloc. Un tirage de plus dans le dé
  commun déplacerait toute la ville.
- ⚠️ **Un juge par règle**, qui compare l'intérieur à son extérieur (le standing de la porte, le district, le genre
  du bâtiment) pour TOUTES les portes de la ville, et qu'on fait rougir en retirant la règle.
- ⚠️ **Se regarde** : une capture dedans et dehors par genre avant de livrer, parce qu'aucun juge ne dit qu'un
  intérieur « fait pauvre ».
- ⚠️ **Après les façades**, ou avec elles ([la revue des façades](une-revue-des-facades-des-residences.md#fiche)) :
  l'intérieur suit ce que la façade dit, alors la façade doit d'abord bien le dire.
- La première vague qui s'impose : **le mur de la porte harmonisé** (il se voit dans chaque pièce, et c'est
  une règle de dessin, pas de contenu), puis les logements selon le standing (pauvre, ordinaire, cossu), en commençant par
  les maisons pauvres de la gare.

## Notes
