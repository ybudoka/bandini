# Des étages pour vrai, des maisons de luxe et des terrains clôturés

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 30 sept. 2026, après la revue des façades : « les maisons et bâtiments doivent avoir vraiment
plusieurs étages, présentement seulement un étage avec une compression de fenêtres », « je veux pouvoir avoir plusieurs
étages et aussi des maisons vraiment de luxe », « aussi des terrains vraiment clôturés »._

**Aujourd'hui** une façade tient sur une seule rangée de 16 px : un triplex y serre trois rangées de fenêtres de 3 px.
Il n'y a pas de maison de luxe (le cossu, ce sont des jardinières et une corniche), et les cours des maisons ne sont pas
fermées.

**Trois vagues, chacune jouable et livrée seule :**

1. **Les étages pour vrai** — la façade monte d'une rangée de tuiles par étage, peinte sur le bas du toit de SON
   bâtiment (vue de trois quarts) : des fenêtres pleine taille, un balcon ou une galerie par étage, la corniche en haut.
   ⚠️ **Rien ne bouge** : les tuiles, les collisions, la ville restent les mêmes — c'est une couche peinte. Une rangée
   de toit reste toujours visible au-dessus ; un bâtiment trop peu profond montre moins d'étages qu'il n'en a. Les
   logements d'abord, puis les commerces (leurs logements au-dessus de la vitrine).
2. **Les terrains clôturés** — autour de la cour d'une maison, une clôture (bois, fer ou haie selon le standing) et un
   portail devant l'allée ou la porte. ⚠️ Posés **en dernier, sur la ville finie, sans un dé** (des tuiles changent :
   les juges « ce module ne déplace rien » les neutralisent des deux côtés), jamais sur un chemin ni devant une porte,
   et tout reste rejoignable à pied (le juge de connexité).
3. **Les maisons de luxe** — dans les îlots cossus, des villas : façade de pierre, grandes fenêtres, colonnes, haie
   taillée, piscine, fontaine, portail de fer forgé. Sur des terrains qui existent déjà, sans déplacer la ville.

**Juges** : un logement de trois étages se peint sur trois rangées quand son bâtiment est assez profond, jamais sur
un autre bâtiment ni sans laisser de toit ; une clôture n'enferme ni un lieu ni un passant ; une villa se reconnaît.

## Notes

### Les références (Martin : « regarde sur le net pour des images réalistes »)

Rangées dans `captures/references/` (hors du dépôt) :

- **Un triplex de la Petite-Patrie** (6565, rue Saint-Denis — [Images Montréal](https://imtl.org/montreal/template.php?Montreal=Duplex+et+triplex+typiques&TYPE=13)) :
  trois étages de brique jaune, une fenêtre haute par travée aux cadres blancs, linteau et appui de pierre, une porte
  par étage et son petit balcon de fer, l'escalier de fer qui longe la façade, un cordon entre les étages, la
  corniche de brique et son fronton orné ; devant, une clôture basse de fer. C'est le modèle de la vague 1.
- **Une rangée de maisons en pierre grise** du centre-ville (même source) : fenêtres cintrées, balcons de bois,
  escaliers de bois, toit mansardé et lucarnes ornées — pour les maisons de luxe (vague 3).
- **Une maison derrière un muret de pierre et une grille de fer forgé** ([Unsplash](https://unsplash.com/photos/beautiful-house-behind-a-wrought-iron-fence-and-stone-wall-OlUKIjLQmSM)) :
  le muret, ses piliers de pierre, la grille à pointes — pour les terrains clôturés (vague 2).
- **Un jeu de tuiles de ville vu de dessus** ([Modern Building Pixel Art Tileset](https://comshadow.itch.io/modern-building-pixel-art-tileset)) :
  la façon de faire des jeux vus de dessus — un mince bandeau de toit, et toute la hauteur pour la façade, un
  étage par rangée, des fenêtres pleine taille.

### Vague 1 — les étages pour vrai, les logements (✅ livrée le 30 sept. 2026)

- **Un étage = une rangée de tuiles** (`etagePlein`, `sprites.js`), peinte sur le bas du toit de SON bâtiment
  (`Monde.logementElargi`, `e.hauts`) : une fenêtre haute par travée (6 × 9 px), son linteau et son appui (la clé de
  voûte chez les cossus) ; à la travée de la porte, une porte d'étage et son balcon de fer ; un cordon entre les
  étages ; la corniche en haut — ornée, avec son fronton, chez les cossus. Le rez prend toute sa rangée : une porte
  de 12 px (le battant qui s'ouvre s'y cale), des fenêtres de 10 × 8. **Les rangées de fenêtres écrasées de 3 px
  sont parties.**
- ⚠️ **Une rangée de toit reste toujours visible** au-dessus : un bâtiment peu profond montre moins d'étages qu'il
  n'en a (mesure du 30 sept. : 121 logements montrent un étage de plus que le rez, 35 en montrent deux, 21 n'en
  montrent aucun — des bungalows, et des bâtiments sans toit de matière teinte). Grossir les bâtiments ferait glisser
  la ville (la mémoire « grossir un lieu garanti déplace la ville ») : c'est du dessin seulement.
- Ce que le toit porte (une cheminée, une ventilation) ne se peint plus sous un étage (`Monde.sousLesEtages`).
- Juges `tests/test_facades_js.py` (les étages : quatre mutations, toutes mordent) ; captures regardées (Faubourg,
  Petit-Canton, Quais, Gare).
- **Les commerces** (✅ le même jour) : la rangée au-dessus de la vitrine reste celle de l'enseigne (le mur derrière le
  panneau), et leurs logements montent à partir de la suivante — deux ou trois étages en tout, à l'empreinte de la
  devanture (`Monde.etagesDuCommerce`), une rangée de toit toujours visible. Leur mur va au bout de leur bâtiment,
  comme celui d'un logement, sans prendre ce qu'un logement voisin a pris (`murDesLogements`), et le rez à côté de la
  vitrine prend le même mur. 129 devantures sur 135 portent des étages.

### Vague 2 — les terrains clôturés (✅ livrée le 30 sept. 2026)

- **La cour avant d'un logement se ferme** (`app/clotures.py`, `poser`) : une clôture le long du trottoir sur la
  dernière rangée d'herbe, un portail ouvert devant la porte, et des retours sur les côtés jusqu'à la façade — là où
  il n'y a pas de voisin mitoyen. Le terrain s'étend de chaque côté jusqu'à mi-chemin du voisin (4 tuiles au plus).
  Une cour se ferme si elle a la même profondeur partout, deux rangées d'herbe au moins. Mesure du 30 sept. (graine
  de la ville) : **97 terrains, 660 tuiles** — 65 en fer forgé, 32 en grillage.
- **La matière suit le standing** : le fer forgé chez les cossus et à l'ordinaire en ville (le triplex de la
  référence), le grillage chez les pauvres, la palissade de bois à l'ordinaire des Érables seulement (la règle de
  Martin : le bois est une image de banlieue — aucune cour des Érables ne s'y prête encore).
- ⚠️ **Posées après la bande nord, sans un dé, AVANT les frénésies et les cartes de hockey** (elles choisissent leurs
  recoins sur la ville clôturée) ; jamais sur un décor, un paquet, un ambulant, une scène ou une réclame, jamais
  devant une porte. Les deux règles des clôtures de Martin tiennent après coup (`_elaguer`) : une course sans coin
  part, et jamais un carré de 2 × 2.
- Juges `tests/test_clotures.py` (seule l'herbe devient clôture, rien d'autre ne bouge, la matière au standing et
  au district, aucune porte nouvellement enfermée) ; les juges « ce module ne déplace rien » les neutralisent
  (bungalows, commerces qui montent) ou comparent le sol hors d'elles (`test_devants`).
- **Trois juges de conduite tenaient par la graine** et sont tombés quand les passants ont changé de trottoir : le
  démarrage au feu (le banc monte dans un char en pleine rue — un vol — et un agent à pied le voyait : la chaleur
  retombe à chaque image, comme le trafic s'en va), la filature de Marco (le char téléporté derrière le Cravate
  s'usait contre le décor jusqu'à brûler, et Marco se sauvait de NOTRE char : il reste entier), et le camion qui fonce
  (`test_conduite_js` : il faut trois colonnes libres devant lui).
