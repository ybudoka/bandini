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
