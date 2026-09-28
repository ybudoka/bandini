# La cour à scrap de la gare

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je n'aime pas la partie avec les morceaux de train, trouve une autre
idée » — les « wagons » de la Gare de triage (des toits de tôle de 6 × 1 posés sur les voies, tous les trois
rangs) se lisaient comme des bouts de train éparpillés. Choix de Martin parmi quatre : **la cour à scrap**.

**Ce que ça donne** : l'ouest de la Gare de triage (la lettre de plan `v`, `_voies_ferrees` dans `nord.py`)
devient la casse des Boulonneux ; le quartier garde son nom, ses hangars au sud et son bidonville à l'est.

- **Une seule voie rouillée** longe le bord nord, sans wagon (que « Gare de triage » veuille encore dire
  quelque chose). Plus aucun wagon nulle part.
- **La cour** : clôture de barbelé (comme les cours de La Shop), un portail au sud, de la terre battue et du
  gravier dedans.
- **Des rangées de carcasses d'autos** (`carcasse`, solide) en allées étroites — un petit labyrinthe pour
  semer la police ; **des montagnes de pneus** (`pneus`) ; **des piles de ferraille compactée** (décor neuf :
  des chars écrasés en cubes de toutes les couleurs, par deux ou trois).
- **Une grue à aimant** (sprite neuf) : une carcasse pend au câble, le bras pivote lentement le jour.
- **Le poste d'aiguillage devient le bureau du ferrailleur** : même place, même taille, même porte ; un autre
  nom, une autre clé de pièce, d'autres meubles (comptoir, balance, poêle, et le classeur qu'on fouille).
- ⚠️ **Rien d'autre ne bouge** : tirage à l'empreinte de la tuile, sans dé ; numéros d'entité à part (la bande
  y est déjà) ; la ville hors de la gare comparée en JSON clé par clé.

## Notes

**Livré le 28 sept. 2026.** `app/nord.py` (`_cour_a_scrap`, `PILES_DE_SCRAP`, `PIECE_FERRAILLEUR`, `BUREAU`),
`app/carte.py` (`clore(depart=…)`, `DECOR_SOLIDE`), `static/js/sprites.js` (`peindreEpave` et les quatre décors
neufs), `tests/test_nord.py`, `tests/test_definitions.py`.

- **La cour** (85 × 74 tuiles, la lettre `v`) : la voie du nord (`T`, d'un bord à l'autre), deux rangs d'herbe,
  puis la cour de barbelé ; son portail de quatre tuiles s'ouvre juste à l'est du bureau (`clore` a gagné un
  `depart` : une trouée voulue, sans dé) et un chemin de gravier le relie à la rue. Dedans, sur la terre
  sèche : une allée de ronde le long du barbelé, l'allée maîtresse (4 de large) du portail jusqu'au fond,
  l'allée en travers (3), la place de la grue (9 × 9). Entre elles, **une rangée de piles tous les quatre
  rangs**, une pile par trois tuiles, et une trouée par rangée de chaque côté de l'allée maîtresse.
- **Quatre décors neufs, solides** : `pile_de_carcasses` (deux chars aplatis et un troisième dessus, six
  peintures délavées), `cubes_de_ferraille` (chars passés à la presse, empilés trois-deux-un), `tas_de_pneus`
  (trois couches à plat et un debout), `grue_aimant` (chenilles, tourelle, la flèche qui pivote le jour en seize
  poses — `travaille: 'jour'` — et l'aimant qui tient un char). Demi-boîte de 22 × 7 px : quatre pixels entre
  deux piles, un passant en demande dix ; on ne se faufile pas dans une rangée.
- **Rien d'autre ne bouge** : la cour se bâtit dans les dés de la gare (`_a_ses_des`, rendus intacts — les
  hangars gardent leurs palettes) et ses piles se tirent à la position (`_empreinte`, `crc32`). La bande
  numérote déjà son décor à part (`Entites.enDehorsDeLaSuite`).
- **Le bureau du ferrailleur** remplace le poste d'aiguillage : même bâtiment, même porte, `nord_ferrailleur`
  (comptoir, classeur des reçus qu'on fouille, étagère, chaise, poêle).
- **Le paquet de la carte** : 67 248 → 68 270 octets gzip (287 piles, +1 Ko) ; plafond relevé à 69 000
  (`test_definitions`). C'est déjà trois fois moins d'objets qu'une carcasse par tuile.
- **Les juges** : `test_la_gare_a_sa_cour_a_scrap_et_plus_un_wagon` (une voie au nord et une seule, plus un toit
  de tôle, le barbelé, les sortes de piles, la grue, le bureau qu'on rejoint) et
  `test_chaque_allee_de_la_cour_a_scrap_se_rejoint_du_portail` (tout le libre de la cour se marche depuis le
  portail, piles comptées en murs). ⚠️ Ce dernier ne rougit que si les TROIS passages tombent (ronde, allée
  maîtresse, trouées) : chacun suffit à tout relier. Mutation vue : 3 587 tuiles isolées.
- **Regardé dans Chromium** avant de livrer : la première grue posait sa carcasse sur le toit de la tourelle
  (flèche trop basse, câble trop long) ; la flèche monte maintenant à 13 px du haut, le câble fait 15 px.
