# Un stationnement touche la rue

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « les stationnements doivent absolument être rattachés à la route ou
collés à un trottoir au moins une fois ». Mesuré sur la graine livrée : **un lot de 4 × 4 au
milieu des cours arrière** d'un bloc de maisons du Faubourg (219, 28) — quatre cases, une
allée, un îlot, et **rien que du gazon sur ses quatre côtés**. On y peignait des places où
aucun char ne pouvait entrer, et rien ne le disait : les lignes sont peintes pareil. La
règle se tient maintenant **par construction**, un cran au-dessus de celle qui tient déjà le
dessin d'un lot (« toute rangée touche une allée ») : un terrain donne sur la rue s'il
touche un **bord de sa bande** — la ruelle derrière, la couronne d'abord à gauche ou à
droite, le trottoir du devant.

- ⚠️ **Sauf le devant d'un bloc de maisons, qui est du GAZON** : celui-là se perce d'une
  **ENTRÉE** large d'une allée (deux tuiles), sortie de l'**allée** du lot et non du fond
  d'une case — une entrée qui débouche sur un pare-chocs fait entrer les autos par la place
  de quelqu'un d'autre — et poussée à travers l'herbe jusqu'à ce qui borde la rue. Et le
  terrain où même l'entrée ne passe pas **n'est plus un stationnement** : il redevient ce
  que son genre aurait dessiné (jardin, terrain vague) — on ne laisse pas un lot muré.
- ⚠️ `_chemin_vers_la_rue` est la règle de l'entrée de cour de banlieue, sortie d'une
  fonction imbriquée et **partagée** : ce qu'on traverse (herbe, dalle, abord), jusqu'où on
  cherche (dix tuiles), et « pas d'entrée » quand la liste est vide. Seule l'**arrivée**
  change : une cour vise la chaussée, un lot se contente de tout ce qui borde la rue
  (`RUE_DU_LOT` — chaussée, ruelle, trottoir, abord).
- ⚠️ **Et l'entrée s'arrête là où la rue commence**, sans paver une tuile de dalle ni
  d'abord. Ce n'est pas une question de goût : `_places_ambulantes` construit une LISTE de
  places et `ambulants()` y pioche avec `des.suivant() % len(candidats)` — **quatre tuiles
  de sol changées déplacent les treize kiosques de la ville**, donc les hommes-sandwichs,
  donc ce qui vit autour du terminus. Première version, l'entrée poussée jusqu'à la
  chaussée : la fille de la Brume s'est mise à flâner au lieu de tenir son coin (**9 relevés
  d'arrêt sur 80 au lieu de 41**) et son juge a rougi sans qu'une ligne de son code ait
  bougé. L'entrée est en plus **réservée** (`self.entrees`) : un camion-restaurant garé
  dedans refermerait le seul chemin par où l'on entre. Bilan sur la ville livrée : **4
  tuiles changées**, un lot rattaché, kiosques et enseignes inchangés. 3 juges — la règle
  sur cinq graines (rouge avant : « 1 stationnements sans rue » sur la graine livrée), la
  forme de l'entrée, et le chemin qui ne mène nulle part
