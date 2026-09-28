"""La villa du maire Tanguay, au bout d'un chemin privé des Érables
(docs/jalons/infiltration-portes-verrouillees-et-gardes-prives.md).

Martin (28 sept. 2026) : « fais des missions d'infiltration » — un bâtiment grand et labyrinthique, des
gardes privés qui font leur ronde, une clé à voler, une porte verrouillée, ne pas être vu. Le plan de M16
attendait « la villa du maire » ; la voici.

⚠️ **UN BLOC, PAS UN LIEU DE LA VILLE.** Une pièce de cette taille en ville ferait glisser la ville (la
règle « agrandir la carte sous la trame »), et une PIÈCE arrête tout : `Histoire.majObjectif` et
`Police.maj` ne tournent pas dedans. Dans un bloc, `B.interieur` reste nul — les objectifs avancent, les
gardes voient, les étoiles montent. On y entre par le bout de la rue est-ouest du bord OUEST des Érables ;
on arrive sur le chemin, devant la grille.

⚠️ **TROIS ÉTAGES DANS UNE CARTE.** Le terrain et le rez-de-chaussée en haut (rangées 0 à 45) ; sous la
rangée de toit qui les sépare, l'étage (à gauche) et la cave (à droite). Chaque étage est un CADRE : la
caméra ne sort jamais du sien (`Monde.cibleCamera`), et chacun est plus grand que l'écran — on ne voit
jamais l'étage d'à côté. Les escaliers (`escaliers`) passent de l'un à l'autre au noir.

⚠️ **LES GARDES SONT AU BLOC, PAS AUX MISSIONS** : la villa est gardée de jour comme de nuit. Chacun a
sa ronde (`GARDES`) ; `Infiltration` les pose en entrant (la relève : les mêmes à chaque visite), et
`Police.garder` les mène. Un garde qui te voit sur le terrain privé (`prive`) le temps de te reconnaître
donne l'alerte : une étoile, et il te court après. Une mission `sans_etoile` est alors ratée.
"""

from .. import carte  # noqa: F401  (la légende des glyphes : `blocs.erreurs` la lit)

PLAN: tuple[str, ...] = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,AA",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AA,,wwwwwwwwwwwwwwww,wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww,,,,,,,,,,,A",
    "A,,,w,,,,,,,,,A,,,,,,,,,,,,,,,A,,,,,,,,,,,,,,,A,,,,,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,gggggggggggggggggggggggggggggggggggggggggg,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,,,g,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,g,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,g,,,A,,,,w,,,,,,,,,,,A",
    "A,,,w,,A,g,,BBBWBBBWBBBWBBBBBBBWBBBWBBBBBBBWBBBB,,g,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,BttttttttttttttBtttttttttBtttttttttB,,g,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,,,g,,BtnttttttttttntBtttttttttBttt//tnttB,,g,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,WttttttttttttttBthhhhhhttBtttttttttB,,g,,,A,,,,w,,,,,,,,,,,A",
    "A,,,w,,A,g,,BttttttttttttttBtaaaaaattBtttttttttW,,g,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,BttttyyyyyyttttBthhhhhhttBtttttttttB,,g,,,,OOO,w,,,,,,,,,,,A",
    "A,,,w,,,,g,,BttttyyyyyyttttBtttttttttBtttttttttB,,g,,,,OOO,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,WttttyaayhyttttttttttttttBtttttttttB,,g,,,,OOO,w,,,,,,,,,,,A",
    "A,,,w,,A,g,,BttttyyyyyyttttBtttttttttBtttttttttB,,g,,,,FWF,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,BttttyyyyyyttttBtttttttttttttttttttB,,g,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,,,g,,BttttttttttttttBtttttttttBtttttttttB,,g,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,BttttttttttttttBttttttttnBtttttttttBgggggggggggg############",
    "A,,,w,,,,g,,BttttttttttttttBtttttttttBtttttttttDgggggggggggg############",
    "AA,,w,,,,g,,BttttttttttttttBtttttttttBtttttttttDgggggggggggg############",
    "A,,,w,,,,g,,BBBBBBBBtBBBBBBBBBBBtBBBBBBBBBttBBBBgggggggggggg############",
    "AA,,w,,,,g,,BuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuB,,g,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,A,g,,BuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuB,,g,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,BBBBBBtBBBBBBBBBBBBtBBBBBBBBBBttBBBB,,g,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,,,g,,BuuuuuuuuuuuuBtttttttttttBtttttttttB,,g,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,Bu/uuuuuuuuuuBtqqqtttttttBttttttttnB,,g,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,A,g,,WuuuuuuuuuaauBtthttttttttBtttttttttW,,g,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,BuuuuuuuuuuuuBtttttttttttBtttttttttB,,g,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,,,g,,BuuuuuuuuuuuuBtttttttttttBtttttttttB,,g,,,A,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,BuuuuuuuuuuuuBtttttttttktBtttttttttB,,g,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,A,g,,BjczzccuuuuuuBtttttttttttBtntttttttB,,g,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,BBBBBBBBuBBBBBBBWBBBWBBBBBBBWBBBWBBB,,g,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,,,g,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,g,,,A,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,g,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,g,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,,,gggggggggggggggggggggggggggggggggggggggggg,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,w,,,,,,,,,,,A",
    "A,,,w,,,,,,,,,A,,,,,,,A,,,,,,,A,,,,,,,A,,,,,,,A,,,,,,,,,,,,w,,,,,,,,,,,A",
    "AA,,w,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,w,,,,,,,,,,,A",
    "A,,,wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww,,,,,,,,,,,A",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,AA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
    "BttttttttttBetttByyBeettBkkttttttkkBBuuuuuuuuuuuuuuuuBuuuuuBucccuuucccuB",
    "BtlltttttntBttttByyBttttBtttaaattttBBueuueuueuueuueuuBuuuuuBuuuuuuuuuuuB",
    "BtlltttttttBttjtByyBttttBtttthtttttBBueuueuueuueuueuuBuuuuuBuuuummuuuuuB",
    "BttttttttttBtttttyytttttBttttttttttBBueuueuueuueuueuuBuuuuuBuuuuuuuuuuuB",
    "BttttttttttBttttByyBttttBttttttttttBBueuueuueuueuueuuBuuuuuBuuuuuuuuuuuB",
    "BttttttatttBttttByyBttetBttttttttttBBueuueuueuueuueuuBuuuuuBukuuuuuuukuB",
    "BtkktttttttBttttByyBttttBttttttttntBBueuueuueuueuueuuBuuuuuBuuuuuuuuuuuB",
    "BttttttttttBttttByyBttttBttttttttttBBueuueuueuueuueuuBuuuuuBBBBBBuBBBBBB",
    "BBBBBtBBBBBBBBBBByyBBBBBBBBBBtBBBBBBBueuueuueuueuueuuBuuuuuuuuuquuuuuuuB",
    "ByyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyBBueuueuueuueuueuuBuuuuuuuuuuuuuuuuuB",
    "ByyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyBBueuueuueuueuueuuBuuuuuuuuuuuuuuuuuB",
    "BBBBBtBBBBBBBtBBByyBBtBBBBBBBtBBBBBBBueuueuueuueuueuuBuuuuuuuuuuuuuuuuuB",
    "BttttttttttBttttByyBttttBeeeeeeeeeeBBueuueuueuueuueuuBummuuuuuuuuuuukuuB",
    "BtlltttttttBttttByyBttttBttttttttttBBueuueuueuueuueuuBummuuuuuuuuuuuuuuB",
    "BtlltttttttBttttByyBttttBttttttttttBBuuuuuuuuuuuuuuuuBuuuuuuuuuuuuuuuuuB",
    "BttttttttntBttttByyBttttBttaatthhttBBBBBBBBBBuBBBBBBBBBBBBBBBBuBBBBBBBBB",
    "BttttttttttBeettByyBetttBttttttttttBBuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuB",
    "BBBBBBBBBBBBBBBBBttBBBBBBBBBBBBBBBBBBuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuB",
    "BttttttttttttttttttttttttttttttttttBBBBBuuBBBBBBBBBBBBBuBBBBBBBBBBBBBBBB",
    "BttttttttttttttttttttttttttttttttttBBu/uuuuuuuuuuuuuuuuuuummmuuuuukkuuuB",
    "Btttttttttttttttt//ttttttttttttttttBBu/uuuuuujjuuuuuuuuuuuuuuuuuuuuuuuuB",
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
)

DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
}

#: ⚠️ LA PALISSADE A UN TROU : une planche manque au nord (20, 4). La grille, elle, a son garde — qui
#: connaît le domaine passe par là, ou enjambe (la palissade s'enjambe, comme toutes celles du jeu).

#: Les lieux de la villa : ses `points_interet`. Une mission les nomme comme un lieu de la ville (`lieu`,
#: `ou`) ; en ville, le GPS vise le passage du bloc, et dans le bloc, le lieu lui-même.
LIEUX: dict[str, dict] = {
    "villa_chemin": {"nom": "Le chemin de la villa", "x": 66, "y": 21},
    "villa_service": {"nom": "La porte de service", "x": 20, "y": 32},
    "villa_bureau": {"nom": "Le bureau du maire", "x": 30, "y": 52},
    "villa_terminal": {"nom": "Le terminal de la chambre forte", "x": 63, "y": 57},
    "villa_voute": {"nom": "La chambre forte", "x": 65, "y": 51},
}

#: Les serrures : des barrières du bloc (`carte.BARRIERES`, la condition `objet`) — fermées tant que
#: l'objet n'est pas dans le sac, et elles ne se forcent pas.
SERRURES: tuple[dict, ...] = (
    {"slug": "villa_service", "nom": "La porte de service", "x": 20, "y": 34, "l": 1, "h": 1,
     "condition": {"objet": "cle_villa"}, "raison": "LA PORTE DE SERVICE EST BARRÉE — IL TE FAUT LA CLÉ"},
    {"slug": "villa_voute", "nom": "La chambre forte", "x": 65, "y": 55, "l": 1, "h": 1,
     "condition": {"objet": "code_voute"}, "raison": "LA CHAMBRE FORTE : IL FAUT SON CODE, AU TERMINAL"},
)

#: Les escaliers : deux bouts, chacun ses tuiles (on y pose le pied) et son arrivée (où l'on se
#: retrouve en montant ou en descendant par l'autre bout) — à deux tuiles des marches, pour ne pas
#: repartir aussitôt.
ESCALIERS: tuple[dict, ...] = (
    {"a": {"tuiles": [[41, 11], [42, 11]], "arrivee": [42, 13], "nom": "LE REZ-DE-CHAUSSÉE"},
     "b": {"tuiles": [[17, 68], [18, 68]], "arrivee": [18, 66], "nom": "L'ÉTAGE"}},
    {"a": {"tuiles": [[14, 28]], "arrivee": [16, 29], "nom": "LA CUISINE"},
     "b": {"tuiles": [[38, 67], [38, 68]], "arrivee": [40, 67], "nom": "LA CAVE"}},
)

#: Les cadres de la caméra, en tuiles (x, y, largeur, hauteur) : le terrain, l'étage, la cave. ⚠️ Chacun
#: plus grand que l'écran (30 × 17 tuiles) : sinon on y verrait l'étage d'à côté.
CADRES: tuple[tuple[int, int, int, int], ...] = ((0, 0, 72, 46), (0, 47, 36, 23), (36, 47, 36, 23))

#: Le terrain privé : dans la palissade, et les deux étages. Le chemin devant la grille est public — on
#: y arrive, on peut s'y tenir.
PRIVE: tuple[tuple[int, int, int, int], ...] = ((4, 4, 56, 38), (0, 47, 36, 23), (36, 47, 36, 23))

#: Les gardes et leur ronde : des points (x, y) en tuiles, et le cap (en degrés, 0 = l'est, 90 = le sud)
#: qu'ils prennent en s'y arrêtant — `pause_s` secondes à balayer du regard. Un seul point : il tient son
#: poste. `porte` : ce qu'il a dans la poche (la clé de la porte de service, pour le garde du jardin).
GARDES: tuple[dict, ...] = (
    {"slug": "grille", "ronde": [[57, 20, 0], [57, 23, 0]], "pause_s": 4},
    {"slug": "jardin", "ronde": [[50, 37, 180], [9, 37, 270], [9, 6, 0], [50, 6, 90]], "pause_s": 2,
     "porte": "cle_villa"},
    {"slug": "hall", "ronde": [[44, 17, 0]], "pause_s": 5},
    {"slug": "corridor", "ronde": [[13, 24, 180], [46, 25, 0]], "pause_s": 3},
    {"slug": "etage_nord_sud", "ronde": [[17, 49, 90], [18, 64, 270]], "pause_s": 2},
    {"slug": "etage_coursive", "ronde": [[2, 57, 0], [33, 58, 180]], "pause_s": 2},
    {"slug": "cave_couloir", "ronde": [[37, 64, 0], [70, 65, 180]], "pause_s": 2},
    {"slug": "cave_voute", "ronde": [[55, 57, 0], [69, 57, 90], [69, 62, 180], [55, 62, 270]], "pause_s": 1},
)

#: Comment un garde tient sa ronde et te reconnaît. `reperage_s` : le temps qu'il te regarde, au bout
#: de son cône, avant de donner l'alerte — plus court de près (jamais moins de `reperage_min`, en part
#: de ce temps). `pas` : sa vitesse de ronde (px/image) ; il marche, il ne court pas. `balaye_deg` : de
#: combien il tourne la tête de chaque côté, à l'arrêt.
REGLES = {"reperage_s": 0.9, "reperage_min": 0.3, "pas": 0.45, "balaye_deg": 35}

BLOC = {
    "slug": "villa",
    "nom": "La villa du maire",
    "plan": PLAN,
    "decors": DECORS,
    "panneau": "VILLA", "panneau_retour": "VILLE",
    # Le passage : le bout de la rue est-ouest (quatre rangées) du bord OUEST des Érables, au nord des
    # Galeries (60 à 64) et du ciné-parc (94 à 98).
    "passage": {"bord": "ouest", "de": 36, "l": 4},
    # Le chemin la continue par le bord EST du bloc : les mêmes quatre rangées.
    "retour": {"bord": "est", "de": 20, "l": 4},
    "arrivee": {"x": 69, "y": 21},
    "gens": False,
    "lieux": LIEUX,
    "serrures": SERRURES,
    "escaliers": ESCALIERS,
    "cadres": CADRES,
    "prive": PRIVE,
    "gardes": GARDES,
    "regles_des_gardes": REGLES,
    # Les deux lampadaires de la grille, et quelques lampes dedans : le reste est noir, la nuit — c'est là
    # qu'on se cache.
    "lampes": [{"x": 58, "y": 19, "r": 40, "c": "lampadaire"}, {"x": 58, "y": 24, "r": 40, "c": "lampadaire"},
               {"x": 42, "y": 15, "r": 26, "c": "fenetre"}, {"x": 30, "y": 24, "r": 26, "c": "fenetre"},
               {"x": 17, "y": 57, "r": 26, "c": "fenetre"}, {"x": 54, "y": 64, "r": 26, "c": "fenetre"},
               {"x": 63, "y": 58, "r": 26, "c": "fenetre"}],
}
