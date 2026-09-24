# Deux bateaux de plus : le chalutier et le porte-conteneurs

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « nouveau bateau : chalutier + porte-conteneurs ». La
chaloupe était seule sur l'eau depuis le 16 sept. (ses deux silhouettes, la barre et la console),
et le **quai du cargo** avait sa chaîne, son contrebandier et sa cale — mais pas de cargo.

**Deux fiches de plus au catalogue** (`vehicules.py`), de classe `bateau`, `eau=True`, hors du
trafic (`frequence: 0`) comme la chaloupe : la règle des deux mondes tient telle quelle (« la
coque est arrêtée par tout ce qui n'est pas de l'eau »), aucune physique à part.

- **Le chalutier** — 48 × 18 px (trois tuiles) : une coque haute à l'étrave relevée, la timonerie
  blanche, le mât, le portique de poupe et son tambour de filet. Plus lent et plus lourd que la
  chaloupe, il encaisse. Deux par ville, à quai, près du port.
- **Le porte-conteneurs** — 160 × 40 px (dix tuiles, plus long que le traversier) : la coque
  sombre, les conteneurs empilés en couleurs, le château et sa cheminée à la poupe. Lent, lourd
  (il pousse tout ce qui flotte), il tourne large et il glisse. **Un seul**, au **mouillage du
  cargo** : le quai du cargo a enfin son cargo.
- Les deux sonnent la **corne** au bouton du klaxon (l'échantillon du traversier), et c'est la
  fiche qui le dit (`klaxon`), pas un `slug ===` dans le JS.

**Où ils mouillent** (`app/navires.py`, nouveau) : sur la ville **finie**, sans un dé, avant le
traversier — un rectangle d'eau de la baie assez grand pour la coque, **le long d'un quai**, de
l'eau libre devant pour repartir, loin des chaloupes, des ponts et du couloir du traversier. Le
porte-conteneurs prend le plus proche de la chaîne du cargo ; les chalutiers les suivants,
espacés. Le navigateur les fait naître hors champ comme les chaloupes (`majAmarrages`), leur
couleur tirée à l'empreinte du mouillage.

- ⚠️ **Ce qu'on AJOUTE se pose en dernier** : aucun lieu garanti ne grossit, aucune tuile ne
  change — la ville doit rester identique, clé par clé.
- ⚠️ **Un grand char naît et s'oublie par son bout, pas par son centre** : à 160 px, le centre
  hors champ laisse la proue à l'écran. Les marges de naissance et d'oubli suivent la longueur,
  sans rien changer pour les chars de moins de 80 px (les dés du trafic ne bougent pas).
- ⚠️ Les juges qui parcourent tout le parc les jugent d'office : la toile qui ne rogne rien à 32
  caps, la chaîne de cercles qui couvre la coque, « de dos, un char montre sa longueur ».
- ⚠️ `test_le_bateau_est_le_seul_a_flotter` et « le klaxon de tous les autres » changent de
  sens : ce sont **les bateaux** qui flottent et qui ont la corne — la règle reste la fiche.
- ⚠️ Le budget des définitions (44 000 octets gzip) : deux fiches de plus, se mesure avant.

À voir en jeu avant de livrer (capture) : les deux silhouettes à plusieurs caps, et le
porte-conteneurs qu'on sort de son bassin.

## Notes

**Livré le 21 sept. 2026.** Deux fiches de plus au catalogue (`vehicules.py`), deux machines
(`sprites.js`), un module qui leur trouve une place (`app/navires.py`), et la naissance à quai
dans le navigateur (`Vehicules.majMouillages`).

- **Le chalutier** — 56 × 18 px, 2,6 de vitesse, 300 PV, masse 3 : la coque rouge (ou bleue,
  verte, crème) à l'étrave relevée, la timonerie, le mât et son feu, le tambour du filet, le
  portique orange. **Le porte-conteneurs** — 160 × 40 px, 1,9 de vitesse, cinq secondes pour
  prendre son erre, 1 500 PV, masse 12, le braquage le plus large que le juge permette (96 px) :
  huit travées de conteneurs aux couleurs écrites (pas tirées), le château, la cheminée, le mât
  avant. Les deux ont **la corne** du traversier au bouton du klaxon.
- **Où ils mouillent**, dans cette ville : le porte-conteneurs le long de la jetée sous la chaîne
  du cargo, **le nez au large** ; un chalutier de l'autre côté de la jetée, l'autre à la bouche de
  la cale. `navires.amarrer` tourne tout à la fin de `generer` et ne pose rien : la ville est la
  même clé par clé (un juge compare), et le traversier n'a pas bougé d'une tuile.
- ⚠️ **Le chenal.** Le premier essai couchait le porte-conteneurs dans le bassin sous la chaîne,
  le nez à quatre tuiles d'une jetée, la poupe contre l'autre : on y montait, il ne sortait plus.
  Un mouillage exige maintenant une longueur de coque d'eau libre devant l'étrave, et aucun autre
  bateau ne mouille dans ce chenal (un chalutier s'était glissé dans la cale, derrière le cargo).
  Le juge du banc monte à bord depuis la jetée, au bouton, et sort du bassin plein gaz sans un
  point de carrosserie.
- ⚠️ **« De dos, un char montre sa longueur »** : au biais de 0,75, 160 px de coque basse vue de
  dos n'occupent que 120 rangées. Ce sont le mât avant (52 px) et la cheminée (55 px) qui paient
  la différence — ce qu'un porte-conteneurs a, de toute façon.
- ⚠️ **Hors champ par le bout** : la règle des chaloupes (le centre à 24 px du bord) faisait naître
  la poupe à l'écran. La marge est la demi-longueur ; celle de l'oubli (`peupler`) aussi, sans
  rien changer sous 72 px (les dés du trafic ne bougent pas).
- ⚠️ **Le garde-fou à l'échelle de la coque** : `degager` cherche au moins à la longueur du char.
  `degagement_px` (96) couvrait tout ce qui roule en ville, pas dix tuiles ; le juge des huit
  tuiles ne porte plus que sur ce qui roule (`not eau`).
- ⚠️ **Au banc, les coques naissent dans `peupler`, une image sur vingt** : un juge qui attend trois
  images ne voit rien naître — et « rien ne naît » y est vert à vide. Les juges attendent 21 images.
- ⚠️ Un piège de `navires.postes` pour qui y touchera : la borne de la fenêtre de recherche
  s'appelait `xa`, comme le large ; la rangée suivante recommençait où finissait le large, et un
  poste sur trois n'était jamais regardé. Les bornes ont leurs noms à elles.
- Le paquet : définitions 42 070 octets gzip (plafond 44 000), carte 48 076 (plafond 50 000).
- La dette « le bateau reste en phase 2 » quitte le plan : elle était payée depuis le 16 sept. (la
  chaloupe a son dessin et flotte), et l'eau a maintenant trois bateaux.

**Pas fait, sciemment :** le bouton tactile dit encore KLAXON sur un bateau à corne (`entree.js`
est pris par « les commandes à l'écran » — un contexte `vehicule_corne` s'y ajoute en une ligne) ;
les grands bateaux ne naviguent pas seuls (aucun trafic sur l'eau) ; aucune mission ne s'en sert
encore — le porte-conteneurs est tout désigné pour la cale du contrebandier.
