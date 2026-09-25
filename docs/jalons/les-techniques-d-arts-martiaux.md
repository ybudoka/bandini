# Les techniques d'arts martiaux : le répertoire

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026) : « je veux des animations variées pour les coups et je veux des coups de
pieds et des projections et autres qu'on peut apprendre dans une école d'arts martiaux. »

Le premier de trois jalons : **le répertoire** (celui-ci), puis [le dojo](le-dojo-du-quartier.md#fiche) où on
l'apprend, puis [l'école rivale](l-ecole-rivale.md#fiche) qui le connaît aussi. Tranché avec Martin le 25 sept. :
un dojo DANS la ville ; un bouton SAISIR neuf ; un mélange de styles (boxe, karaté, judo, jiu-jitsu) aux noms
**en français** ; les poings de rue varient pour tout le monde, pieds et projections au joueur (et au gang de
l'école rivale) ; l'animation est **hybride** (voir plus bas).

- ⚠️ **Mesuré avant** : un coup, pour tout le monde, c'est UNE pose `frappe_<face>` et un élan de ±3 px
  (`Entites.nomDePose`, `Entites.pose`) — trois temps (`anticipation` → `actif` → `repos`) lus dans `armes.py`,
  plus le coup fort chargé. Aucun coup de pied, aucune projection dans l'historique (`git log --all`).

### La grammaire des boutons

- **FRAPPE en tapes** : un enchaînement ; chaque tape dans la fenêtre de rythme (≈ 0,4 s) passe au maillon
  suivant. **La chaîne s'allonge avec ce qu'on a appris** : chaque cours ajoute un maillon au bout. Une tape
  donnée pendant le coup en cours est **gardée en réserve** (une seule), sinon on rate une tape sur deux.
- **FRAPPE tenue** : le coup chargé. **FRAPPE en pleine course** : le coup sauté. **FRAPPE au sortir d'une
  roulade** : le balayage.
- **SAISIR** (neuf) : on attrape l'ennemi devant soi et on le tient ≈ 1,2 s ; **la direction du stick,
  relative à l'axe joueur → cible, choisit la projection** (vers l'avant, vers soi, de côté). FRAPPE dans la
  prise : des coups de genou. Relâcher sans rien : on le **repousse**. Rien pendant 1,2 s : il se dégage.
- **SAISIR tenu dans le dos** (écart de plus de 120° avec sa face) : l'étranglement. **SAISIR pendant que
  l'ennemi arme son coup** (sa phase `anticipation`, portée comprise) : la parade-contre.
- ⚠️ **Où va SAISIR** : clavier **U** — ni G, ni R, I, O, L, qui épèlent la suite secrète `RIGOLO`
  (`Jeu.SEQUENCE_DEBUG`) ; manette **RB (5)**, qui ne faisait que doubler FRAPPE ; l'écran MANETTE l'apprend
  comme les autres, et le tactile a son bouton. La prise d'otage reste sur ACTION.
- ⚠️ **Une arme de mêlée en main** (batte, couteau) : FRAPPE reste le coup de l'arme ; SAISIR marche toujours.
  Mains nues et poing américain passent par les techniques.

### Le répertoire

**Les poings de rue** — gratuits, pour tout le monde (passants et gangs compris) :

| Geste | Technique |
|---|---|
| FRAPPE 1, 2, 3 | direct du gauche → direct du droit → crochet |
| FRAPPE collé à la cible | coup de genou |
| SAISIR, relâcher | repousser (il titube) |
| SAISIR + FRAPPE | genoux dans la prise |

Un passant tire sa variante **à l'empreinte** — `(e.id + e.coups) % 3`, le genou s'il est collé — jamais par
`B.rng()`, qui décalerait tout le hasard de la ville.

**Les cours du dojo** — dix, au joueur seulement :

| Style | Technique | Geste | Ce qu'elle apporte |
|---|---|---|---|
| Boxe | uppercut | 4e tape | renverse |
| Karaté | coup de pied circulaire | 5e tape | large arc, deux ennemis |
| Karaté | coup de pied de côté | FRAPPE tenue | longue portée, l'envoie loin |
| Karaté | coup de pied sauté | FRAPPE en course | ferme la distance |
| Karaté | balayage | FRAPPE au sortir d'une roulade | couche tout ce qui est autour |
| Judo | projection de hanche | prise + stick vers l'avant | il passe par-dessus, retombe devant |
| Judo | grand fauchage | prise + stick vers soi | il tombe sur le dos, sur place |
| Judo | sacrifice en cercle | prise + stick de côté | on tombe, pied au ventre, il vole par-dessus |
| Jiu-jitsu | retournement du poignet | SAISIR pendant qu'il arme | parade-contre, il roule au sol |
| Jiu-jitsu | étranglement | SAISIR tenu, dans le dos | l'assomme **en silence** |

**Pourquoi les apprendre** : les pieds portent plus loin mais partent plus lentement ; les projections
**assomment sans faire saigner** (moins d'étoiles que cogner) ; l'étranglement, c'est la furtivité.

### L'animation : hybride

- **Une dizaine de poses clés**, dessinées une fois par face (bas, haut, côté ; la gauche est le miroir) dans
  le squelette `homme` de `garderobe.js` — les tenues les habillent toutes seules : poing avant (existe :
  `frappe`), poing arrière, crochet, genou, pied de face, pied de côté, saisie à deux mains, charge sur la
  hanche, au sol sur le dos, accroupi. **10 poses × 3 faces.** Le circulaire, l'uppercut et le coup sauté
  sont ces poses plus une rotation ou une hauteur.
- **Chaque technique est une ligne de temps** : `[(pose, images, dx, dy, rot, z), …]`, une seule étape
  marquée `actif`.
- **La victime projetée** (`e.vol`) : un arc en hauteur (`z = 4h·t(1−t)`), un demi-tour (un tour pour le
  sacrifice), la poussière et la secousse à l'atterrissage, puis couchée. ⚠️ **Le point de chute se raccourcit
  jusqu'à la dernière tuile marchable** : on ne projette personne dans un mur.
- `Entites.nomDePose` demande `tech_<pose>_<face>`, puis `frappe_<face>`, puis la face : un sprite dessiné à
  la main qui n'a pas les poses frappe comme aujourd'hui.

### La mécanique

- **`app/techniques.py`** (frère de `armes.py`) : `slug`, `nom`, `style`, `geste` (`tape`, `tenue`, `course`,
  `roulade`, `prise_avant`, `prise_vers_soi`, `prise_cote`, `contre`, `dos`), `rang` (sa place dans la
  chaîne), `gratuite`, `prix`, `degats`, `portee`, `arc`, `renverse`, `assomme`, `projete` (px),
  `silencieuse`, `sans_sang`, et `temps` (la ligne de temps). Servi par `definitions.py` →
  `B.defs.techniques`.
- **`static/js/techniques.js`** (neuf — `combat.js` fait déjà 1 080 lignes) : `choisir(e, geste)` **pure**
  (ce que `e` sait + son contexte → un slug) ; `demarrer(e, slug)` ; `maj(e)` avance la ligne de temps et
  applique l'arc à l'étape `actif` (`arcDeMelee`).
- ⚠️ **`j.prise`, pas `j.saisie`** : `saisie` est déjà la prise d'otage (`Combat.majSaisie`). La cible passe à
  l'état `tenu`, figée face à nous.
- ⚠️ **`Entites.blesser` fait TOUJOURS saigner un passant** (`sang(...)`) et **alerte toujours** : deux
  options neuves, `sans_sang` (les projections) et `silencieuse` (l'étranglement : ni cri ni `alerter` ;
  `Police.quelqu_un_voit` décide seul s'il y a un crime).
- **Ce qu'on sait** : `B.partie.techniques = {slug: true}`, sauvé avec la partie. L'onglet TRICHES gagne
  « TOUTES LES TECHNIQUES » — c'est par là qu'on joue avec avant que le dojo existe.
- **Le nom** de la technique apprise s'affiche brièvement quand elle porte (« GRAND FAUCHAGE ! »).
- **Trois bruitages** ElevenLabs au catalogue audio : le pied qui fend l'air, le corps qui tombe,
  l'étranglement.

### Les juges

- **Python** : chaque pose citée existe dans le squelette `homme` pour les trois faces ; une seule étape
  `actif` par technique ; pas deux techniques sur le même geste et le même rang ; portée ≤ 240 (la borne de
  `base.js`, comme `test_armes`).
- **Banc Node**, un par geste, **joués au bouton** (pas en appelant la fonction) : `choisir` rend le bon slug ;
  la tape en réserve enchaîne ; une projection vers un mur tombe sur une tuile libre ; un étranglement non vu
  n'alerte personne ; un passant rejoue la même suite de coups pour la même empreinte. Chacun **muté** une
  fois pour le voir rougir.
- **Capture Chromium** des 30 poses et d'une projection en vol, regardée avant de livrer.
- ⚠️ Les juges « ce module ne déplace rien » : aucun dé, aucun id global consommé au démarrage.

## Notes

_Rien de livré._
