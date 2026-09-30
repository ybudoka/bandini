# Une file pour entrer à la foire

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « je veux une file de personnes qui attendent pour entrer à la foire quand
c'est ouvert », puis « je veux que la clôture soit infranchissable » et « mets aussi des câbles de
gestion de file ».

Mesuré : la foire est ouverte jour et nuit (seul l'hiver la fermera, [la foire fermée
l'hiver](la-foire-fermee-l-hiver.md), `Foire.fermee`). L'arche (`carte.BARRIERES`, slug `foire`) est une
ouverture de trois tuiles dans le grillage (`foire_entree`) ; au sud, une rangée d'abord, le trottoir, puis
la rue. Le joueur paie 15 $ en se butant à l'arche ; le grillage s'enjambe comme toutes les clôtures, et
retomber dedans sans billet coûte une étoile (`Monde.resquille`).

Tranché par Martin :

- **Quand** : tant que la foire est ouverte (pas l'hiver), avec une longueur qui suit l'heure : deux ou trois
  personnes le matin, une douzaine en fin d'après-midi et en soirée, presque personne la nuit.
- **Elle avance** : toutes les quelques secondes, le premier passe l'arche (son billet payé) et va se perdre
  dans la foule de la foire ; les autres font un pas, et un nouveau arrive au bout. Rien au dé : à l'empreinte.
- **Des câbles à sangle, en zigzag sur le trottoir** : le vrai serpentin d'attente, devant l'arche. Il prend
  le trottoir : les passants le contournent par le bord de la rue.
- **Le joueur coupe s'il veut** : l'arche ne l'oblige pas à faire la file, mais ceux qui y sont le lui disent
  à voix haute (« Heille ! Y'a une file, là ! »), sans étoile ni bagarre.
- **Le grillage de la foire ne s'enjambe plus.** L'arche, elle, se force encore (on pousse, une étoile).
