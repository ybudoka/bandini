# L'orignal de La Pointe

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui »)._

_Ce que ça donne :_ une bête rare et énorme sur le chemin des bois — la frapper, c'est le char détruit,
et la une du Clairon le lendemain.

**Aujourd'hui** le jeu a ses bêtes (le chat, le raton, les bêtes qui se sauvent pour vrai) ; aucune n'est
plus grosse qu'un char.

- **L'orignal** : une bête rare (une fois de temps en temps, la nuit surtout), qui traverse le chemin des bois
  de La Pointe, s'arrête dans les phares et **ne bouge plus**.
- **Le choc** : le frapper détruit presque le char (il pèse une tonne) ; il repart dans le bois, fâché.
- **Le journal** : le Clairon du lendemain titre dessus (« Un orignal gagne contre une Chevrolet »).
- **Le klaxon** le fait fuir — la leçon, dite par Ovila, le gardien du phare.

⚠️ **Ce qui guette** : l'apparition ne se tire pas au dé du jeu (`B.rng()`) — une règle d'horaire, comme la
nuit a ses habitudes ; un sprite de bête plus gros que les autres.

**Juges** : l'orignal n'apparaît que sur le chemin des bois ; le frapper abîme le char plus qu'un mur ;
aucun `B.rng()` tiré par sa venue ; le journal en parle le lendemain.

## Notes

_Rien de livré._

**Livré le 26 sept. 2026.**

- **Le chemin des bois** n'existait pas sous ce nom : le bois de La Pointe est un parc sauvage, avec des
  allées de sable réservées. La carte les exporte maintenant (`chemins_des_bois`, 501 tuiles) — lues,
  jamais tirées : la ville ne bouge pas d'une tuile.
- **L'orignal** (`Entites.majOrignal`) : une nuit sur trois environ, à l'empreinte du jour, sur un
  sentier choisi de même ; il ne naît qu'à l'approche du joueur, hors champ (ailleurs, personne ne crée
  rien). Il va au pas d'une tuile de sentier à l'autre, se **fige** dans les phares d'un char qui vient
  vers lui et ne bouge plus ; un **coup de klaxon** le fait détaler, et il s'efface loin du joueur.
- ⚠️ **Un décor, pas une bête** : les bêtes vivent hors de `B.entites` pour qu'aucun char ne les touche —
  celle-ci, on la frappe. Il tient l'index des décors à jour à chaque pas, comme la benne qu'on pousse.
- **Le choc** (`Vehicules.heurterDecor`) : le char y laisse 85 % de sa vie (un mur, à la même vitesse,
  une vingtaine de points), la bête repart dans le bois, fâchée ; et si c'est toi, **le Clairon titre
  dessus** le lendemain — « Un orignal gagne contre un char », et la leçon du klaxon, celle d'Ovila, citée
  par le narrateur (une voix générée, 13 s).
- **Le dessin** : 32 × 26, plus haut qu'un char — le panache en palettes, la bosse au garrot, le fanon,
  les bas pâles ; tourné vers l'est ou l'ouest selon où il va.
- **Juges** (`tests/test_orignal_js.py`) : une nuit sur trois sur 300, né et resté sur les sentiers, pas
  le jour ; aucun `B.rng()` ni pour sa venue ni pour ses pas ; figé dans les phares, en fuite au klaxon ;
  le choc qui coûte plus qu'un mur et fait la une. Quatre mutations le font rougir.

