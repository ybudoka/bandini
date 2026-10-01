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

⚠️ **CINQ ÉTAGES DANS UNE CARTE.** Le terrain et le rez-de-chaussée en haut (rangées 0 à 45) ; sous la
rangée de toit qui les sépare, l'étage (à gauche) et la cave (à droite) ; sous une autre, le 2e étage (à
gauche) et le sous-sol (à droite). Martin (30 sept. 2026) : « ajoute même deux étages intermédiaires avant
la fin » — le bureau du maire est monté au 2e (on traverse l'étage pour y aller), la chambre forte est
descendue au sous-sol (on traverse la cave). Chaque étage est un CADRE : la
caméra ne sort jamais du sien (`Monde.cibleCamera`), et chacun est plus grand que l'écran — on ne voit
jamais l'étage d'à côté. Les escaliers (`escaliers`) passent de l'un à l'autre au noir.

⚠️ **LES GARDES SONT AU BLOC, PAS AUX MISSIONS** : la villa est gardée de jour comme de nuit. Chacun a
sa ronde (`GARDES`) ; `Infiltration` les pose en entrant (la relève : les mêmes à chaque visite), et
`Police.garder` les mène. Un garde qui te voit sur le terrain privé (`prive`) le temps de te reconnaître
donne l'alerte : une étoile, et il te court après. Une mission `sans_etoile` est alors ratée.
"""

from .. import carte  # noqa: F401  (la légende des glyphes : `blocs.erreurs` la lit)

#: ⚠️ LES MURS FISSURÉS (`0`, les explosifs, vague 3b) : deux murs du rez — entre le salon et la salle à manger, entre
#: la salle à manger et la cuisine — cèdent à une explosion (le C4, une grenade) et deviennent des gravats où l'on
#: passe. Une route de plus, bruyante : jamais vers la chambre forte ni le bureau du maire.
PLAN: tuple[str, ...] = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,AA",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AA,,'''''''''''''''',''''''''''''''''''''''''''''''''''''''',,,,,,,,,,,A",
    "A,,,',,,,,,,,,A,,,``,``,,,,,,,A,,,,,,,,,,,,,,,A,,,,,,,,,,,,',,,,,,,,,,,A",
    "AA,,',,,,gggggggggggggggggggggggggggggggggggggggggg,,,,,,,,',,,,,,,,,,,A",
    "A,,,',,,,g,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,g,,,,,,,,',,,,,,,,,,,A",
    "AA,,',,,,g,,,,,,``,,,,,,,,,,,,``,,,,,,,,,,``,,,,,,g,,,A,,,,',,,,,,,,,,,A",
    "A,,,',,A,g,,BBBWBBBWBBBWBBBBBBBWBBBWBBBBBBBWBBBB,,g,,,,,,,,',,,,,,,,,,,A",
    "AA,,',,,,g,,BttttttttttttttBtttttttttBtttttttttB,,g,,,,``,,',,,,,,,,,,,A",
    "A,,,',,,,g,,BtnttttttttttntBtttttttttBttt//tnttB,,g,,,,,,,,',,,,,,,,,,,A",
    "AA,,'```,g,,WttttttttttttttBthhhhhhttBtttttttttB,,g,,,A,,,,',,,,,,,,,,,A",
    "A,,,',,A,g,,BttttttttttttttBtaaaaaattBtttttttttW,,g,,,,,,,,',,,,,,,,,,,A",
    "AA,,',,,,g``BttttyyyyyyttttBthhhhhhttBtttttttttB,,g,,,,OOO,',,,,,,,,,,,A",
    "A,,,',,,,g,,Bttttyyyyyytttt0tttttttttBtttttttttB,,g,,,,OOO,',,,,,,,,,,,A",
    "AA,,',,,,g,,WttttyaayhyttttttttttttttBtttttttttB,,g,,,,OOO,',,,,,,,,,,,A",
    "A,,,',,A,g,,BttttyyyyyyttttBtttttttttBtttttttttB,,g,,,,FWF,',,,,,,,,,,,A",
    "AA,,',,,,g,,BttttyyyyyyttttBtttttttttttttttttttB,,g,,,,,,,,',,,,,,,,,,,A",
    "A,,,',,,,g,,BttttttttttttttBttttttttt0tttttttttB,,g,,,,,,,,',,,,,,,,,,,A",
    "AA,,'```,g,,BttttttttttttttBttttttttnBtttttttttBgggggggggggg############",
    "A,,,',,,,g,,BttttttttttttttBtttttttttBtttttttttDgggggggggggg############",
    "AA,,',,,,g,,BttttttttttttttBtttttttttBtttttttttDgggggggggggg############",
    "A,,,',,,,g,,BBBBBBBBtBBBBBBBBBBBtBBBBBBBBBttBBBBgggggggggggg############",
    "AA,,',,,,g,,BuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuB,,g,,,,,,,,',,,,,,,,,,,A",
    "A,,,',,A,g,,BuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuB,,g,,,,,,,,',,,,,,,,,,,A",
    "AA,,',,,,g``BBBBBBtBBBBBBBBBBBBtBBBBBBBBBBttBBBB,,g,,,,,,,,',,,,,,,,,,,A",
    "A,,,',,,,g,,BuuuuuuuuuuuuBtttttttttttBtttttttttB,,g,,,,,,,,',,,,,,,,,,,A",
    "AA,,'```,g,,Bu/uuuuuuuuuuBtqqqtttttttBttttttttnB,,g,,,,,,,,',,,,,,,,,,,A",
    "A,,,',,A,g,,WuuuuuuuuuaauBtthttttttttBtttttttttW,,g,,,,,,,,',,,,,,,,,,,A",
    "AA,,',,,,g,,BuuuuuuuuuuuuBtttttttttttBtttttttttB,,g,,,,``,,',,,,,,,,,,,A",
    "A,,,',,,,g,,BuuuuuuuuuuuuBtttttttttttBtttttttttB,,g,,,A,,,,',,,,,,,,,,,A",
    "AA,,',,,,g,,BuuuuuuuuuuuuBtttttttttktBtttttttttB,,g,,,,,,,,',,,,,,,,,,,A",
    "A,,,',,A,g,,BjczzccuuuuuuBtttttttttttBtntttttttB,,g,,,,,,,,',,,,,,,,,,,A",
    "AA,,',,,,g,,BBBBBBBBuBBBBBBBWBBBWBBBBBBBWBBBWBBB,,g,,,,,,,,',,,,,,,,,,,A",
    "A,,,',,,,g,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,g,,,A,,,,',,,,,,,,,,,A",
    "AA,,',,,,g,,,,,,,``,,,``,,,,,,,,,,,,,,,,,,,,,,,,,,g,,,,,,,,',,,,,,,,,,,A",
    "A,,,',,,,gggggggggggggggggggggggggggggggggggggggggg,,,,,,,,',,,,,,,,,,,A",
    "AA,,',,,,,,,,,,`,,,,,,,,,,,`,,,,,,,,,,,`,,,,,,,,,,,,,,,,,,,',,,,,,,,,,,A",
    "A,,,',,,,,,,,,A`,,,,,,A,,,,`,,A,,,,,,,A`,,,,,,A,,,,,,,,,,,,',,,,,,,,,,,A",
    "AA,,',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,',,,,,,,,,,,A",
    "A,,,'''''''''''''''''''''''''''''''''''''''''''''''''''''''',,,,,,,,,,,A",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,AA",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
    "BttttttttttBetttByyBeettBkktt//ttkkBBuuuuuuuuuuuuuuuuBuuuuuBucccu//cccuB",
    "BtlltttttntBttttByyBttttBttttttttttBBueuueuueuueuueuuBuuuuuBuuuuuuuuuuuB",
    "BtlltttttttBttjtByyBttttBetttttttteBBueuueuueuueuueuuBuuuuuBuuuuuuuuuuuB",
    "BttttttttttBtttttyytttttBetttttttteBBueuueuueuueuueuuBuuuuuBuuuuuuuuuuuB",
    "BttttttttttBttttByyBttttBetttttttteBBueuueuueuueuueuuBuuuuuBuuuuuuuuuuuB",
    "BttttttatttBttttByyBttetBetttttttneBBueuueuueuueuueuuBuuuuuBukuuuuuuukuB",
    "BtkktttttttBttttByyBttttBttttttttttBBueuueuueuueuueuuBuuuuuBuuuuuuuuuuuB",
    "BttttttttttBttttByyBttttBttttttttttBBueuueuueuueuueuuBuuuuuBBBBBBuBBBBBB",
    "BBBBBtBBBBBBBBBBByyBBBBBBBBBBtBBBBBBBueuueuueuueuueuuBuuuuuuuuukuuuuuuuB",
    "ByyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyBBueuueuueuueuueuuBuuuuuuuuuuuuuuuuuB",
    "ByyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyBBueuueuueuueuueuuBuuuuuuuuuuuuuuuuuB",
    "BBBBBtBBBBBBBtBBByyBBtBBBBBBBtBBBBBBBueuueuueuueuueuuBuuuuuuuuuuuuuuuuuB",
    "BttttttttttBttttByyBttttBeeeeteeeeeBBueuueuueuueuueuuBummuuuuuuuuuuukuuB",
    "BtlltttttttBttttByyBttttBttttttttttBBueuueuueuueuueuuBummuuuuuuuuuuuuuuB",
    "BtlltttttttBttttByyBttttBttttttttttBBuuuuuuuuuuuuuuuuBuuuuuuuuuuuuuuuuuB",
    "BttttttttntBttttByyBttttBttaatthhttBBBBBBBBBBuBBBBBBBBBBBBBBBBuBBBBBBBBB",
    "BttttttttttBeettByyBetttBttttttttttBBuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuB",
    "BBBBBBBBBBBBBBBBBttBBBBBBBBBBBBBBBBBBuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuB",
    "BttttttttttttttttttttttttttttttttttBBBBBuuBBBBBBBBBBBBBuBBBBBBBBBBBBBBBB",
    "BttttttttttttttttttttttttttttttttttBBu/uuuuuuuuuuuuuuuuuuummmuuuuukkuuuB",
    "Btttttttttttttttt//ttttttttttttttttBBu/uuuuuujjuuuuuuuuuuuuuuuuuuuuuuuuB",
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
    "BBBBBBWBBBBBBBBWBBBBBBBBBBBBBWBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
    "BnttttttttkBccuuuuunBkkttttttttttkkBBu//uuuueeeeuBummuummuBuuuuuuuuuuuuB",
    "BtlltttttttBuuuuuuuuBttttttthttttttBBuuuuuuuuuuuuBummuummuBummmmuummmuuB",
    "BtlltttttttBuuuuuuuuBttttttaaaattttBBuuuuuuueeeeuBuuuuuuuuBuuuuuuuuuuuuB",
    "WttttttttttBuuuuuuuuBttttttttttttttWBuuuuuuuuuuuuBuuuuuuuuBuuuuuuuuuuuuB",
    "BttttttttttBuuuuuuuuBttttttttttttttBBuuuuuuueeeeuBuuuuuuuuBummmmuummmuuB",
    "BtttttttteeBuuuuuuuuBttttttttttttttBBuuuuuuuuuuuuBzzuuuuuuBuuuuuuuuuuuuB",
    "BttttttttttBuuuuuccuBnttttttttttttnBBBBBBBuBBBBBBBBBBuBBBBBuuuuuuuuuuuuB",
    "BBBBBtBBBBBBBBBBtBBBBBBBBBBtBBBBBBBBBuuuuuuuuuuuBuuuuuuuuuBummmmuummmuuB",
    "ByyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyBBueeuuuukkuuBuccuuuuuuBuuuuuuuuuuuuB",
    "ByyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyBBuuuuuuuuuuuBuuuuuuuuuuuuuuuuuuuuuuB",
    "BBBBBBtBBBBBBBBBBBtBBBBBBBBBBBtBBBBBBuuuuuuuuuuuuuuuuuuuuuBummmmuummmuuB",
    "BntttttttttnBtttttttttttBttttttttttBBueeuuuuuuuuBuuuuuuuuuBuuuuuuuuuuuuB",
    "BtttttttttttBtttttttttttBteeeeteeetBBuuuuuuuuuuuBuuuuuukkuBuuuuuuuuuuuqB",
    "BtttttttttttBttttttttttttttttttttttBBuuuuuuuuuuuBuuuuuuuuuBuuuuuuuuuuuuB",
    "BtttttttttttBttyyyyyyyttBttttttttttBBBBBBuBBBBBBBBBBBuBBBBBBBBBBBBBBBBBB",
    "WtttttttttttBttyhaahyyttBteeeeteeetWBuuuuuuuuuuuuuuuuuuuuuuuuuBucccucccB",
    "BttttttttttttttyyyyyyyttBttttttttttBBummuuuuuuuuuuuuuuuuuuuuuuBuuuuuuuuB",
    "BtttttttttttBttyyyyyyyttBttttttttttBBuuuuuuuuuuuuuuuuuuuuuuuquBuuuuuuuuB",
    "BtttttttttttBtttttttttttBteeeeteeetBBuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuB",
    "BtttttttttttBtttttttttttBttttttttttBBukkuuuuuuuuuuuuuuuuuuuuuuBuuuuuuuuB",
    "Bt//ttttttttBntttttttttnBttttttttttBBuuuuuuuuukkuuuuuuuuuuuuuuBucccucccB",
    "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
)

DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
}

#: ⚠️ LA PALISSADE EST SURMONTÉE DE BARBELÉ (`'`, Martin, 30 sept. 2026 : « la villa devrait avoir des
#: clôtures barbelées ») : elle ne s'enjambe plus. Il n'y a que deux entrées — le trou où manque une planche,
#: au nord (20, 4), et la grille, qui a son garde.

#: Les lieux de la villa : ses `points_interet`. Une mission les nomme comme un lieu de la ville (`lieu`,
#: `ou`) ; en ville, le GPS vise le passage du bloc, et dans le bloc, le lieu lui-même.
LIEUX: dict[str, dict] = {
    "villa_chemin": {"nom": "Le chemin de la villa", "x": 66, "y": 21},
    "villa_service": {"nom": "La porte de service", "x": 20, "y": 32},
    "villa_bureau": {"nom": "Le bureau du maire", "x": 29, "y": 76},
    "villa_terminal": {"nom": "Le terminal de la chambre forte", "x": 60, "y": 90},
    "villa_voute": {"nom": "La chambre forte", "x": 66, "y": 90},
}

#: Les serrures : des barrières du bloc (`carte.BARRIERES`, la condition `objet`) — fermées tant que
#: l'objet n'est pas dans le sac, et elles ne se forcent pas.
SERRURES: tuple[dict, ...] = (
    {"slug": "villa_service", "nom": "La porte de service", "x": 20, "y": 34, "l": 1, "h": 1,
     "condition": {"objet": "cle_villa"}, "raison": "LA PORTE DE SERVICE EST BARRÉE — IL TE FAUT LA CLÉ"},
    {"slug": "villa_voute", "nom": "La chambre forte", "x": 62, "y": 90, "l": 1, "h": 1,
     "condition": {"objet": "code_voute"}, "raison": "LA CHAMBRE FORTE : IL FAUT SON CODE, AU TERMINAL"},
)

#: Les escaliers : deux bouts, chacun ses tuiles (on y pose le pied) et son arrivée (où l'on se
#: retrouve en montant ou en descendant par l'autre bout) — à deux tuiles des marches, pour ne pas
#: repartir aussitôt. ⚠️ **L'ARRIVÉE EST UN REFUGE** : on monte à l'aveugle (l'autre étage est un autre cadre),
#: alors aucun garde ne doit la voir, jamais — ni par une porte, ni au bout de sa ronde. La cuisine (16, 29) se
#: voyait du corridor par sa porte, la cave (40, 67) par l'ouverture de son couloir, l'étage (18, 66) du bout
#: de la ronde du tapis (Martin, v02 ratée deux fois, 30 sept.) ; un juge plante le joueur à chaque arrivée.
ESCALIERS: tuple[dict, ...] = (
    {"a": {"tuiles": [[41, 11], [42, 11]], "arrivee": [42, 13], "nom": "LE REZ-DE-CHAUSSÉE"},
     "b": {"tuiles": [[17, 68], [18, 68]], "arrivee": [18, 66], "nom": "L'ÉTAGE"}},
    {"a": {"tuiles": [[14, 28]], "arrivee": [14, 30], "nom": "LA CUISINE"},
     "b": {"tuiles": [[38, 67], [38, 68]], "arrivee": [40, 68], "nom": "LA CAVE"}},
    # Les deux étages intermédiaires : l'ancien bureau de l'étage est une bibliothèque, et son escalier monte au
    # 2e ; l'ancienne chambre forte de la cave est une antichambre, et le sien descend au sous-sol.
    {"a": {"tuiles": [[29, 48], [30, 48]], "arrivee": [30, 50], "nom": "L'ÉTAGE"},
     "b": {"tuiles": [[2, 92], [3, 92]], "arrivee": [3, 90], "nom": "LE 2E ÉTAGE"}},
    {"a": {"tuiles": [[65, 48], [66, 48]], "arrivee": [66, 50], "nom": "LA CAVE"},
     "b": {"tuiles": [[38, 72], [39, 72]], "arrivee": [39, 74], "nom": "LE SOUS-SOL"}},
)

#: Les cadres de la caméra, en tuiles (x, y, largeur, hauteur) : le terrain, l'étage, la cave, le 2e étage, le
#: sous-sol. ⚠️ Chacun plus grand que l'écran (30 × 17 tuiles) : sinon on y verrait l'étage d'à côté.
CADRES: tuple[tuple[int, int, int, int], ...] = ((0, 0, 72, 46), (0, 47, 36, 23), (36, 47, 36, 23),
                                                 (0, 71, 36, 23), (36, 71, 36, 23))
#: Le nom de chaque cadre, dans le même ordre : la grande carte n'en montre qu'un — celui où l'on se tient
#: — et le titre le nomme.
NOMS_DES_CADRES: tuple[str, ...] = ("LE REZ-DE-CHAUSSÉE", "L'ÉTAGE", "LA CAVE", "LE 2E ÉTAGE", "LE SOUS-SOL")

#: Le terrain privé : dans la palissade, et tous les étages. Le chemin devant la grille est public — on
#: y arrive, on peut s'y tenir.
PRIVE: tuple[tuple[int, int, int, int], ...] = ((4, 4, 56, 38),) + CADRES[1:]

#: Les gardes et leur ronde : des points (x, y) en tuiles, et le cap (en degrés, 0 = l'est, 90 = le sud)
#: qu'ils prennent en s'y arrêtant — `pause_s` secondes à balayer du regard. Un seul point : il tient son
#: poste. `porte` : ce qu'il a dans la poche (la clé de la porte de service, pour le garde du jardin).
GARDES: tuple[dict, ...] = (
    {"slug": "grille", "ronde": [[57, 20, 0], [57, 23, 0]], "pause_s": 4},
    {"slug": "jardin", "ronde": [[50, 37, 180], [9, 37, 270], [9, 6, 0], [50, 6, 90]], "pause_s": 2,
     "porte": "cle_villa"},
    {"slug": "hall", "ronde": [[44, 17, 0]], "pause_s": 5},
    {"slug": "corridor", "ronde": [[13, 24, 180], [46, 25, 0]], "pause_s": 3},
    # ⚠️ Il tourne à la rangée 60 : six tuiles de l'arrivée du grand escalier, sa lampe en porte cinq. Il
    # descendait à 64, deux tuiles devant elle, en la regardant.
    {"slug": "etage_nord_sud", "ronde": [[17, 49, 90], [18, 60, 270]], "pause_s": 2},
    {"slug": "etage_coursive", "ronde": [[2, 57, 0], [33, 58, 180]], "pause_s": 2},
    {"slug": "cave_couloir", "ronde": [[37, 64, 0], [70, 65, 180]], "pause_s": 2},
    # ⚠️ Il tourne à la colonne 57, pas 55 : un meuble arrête un garde depuis le 30 sept. 2026, et sa ronde
    # passait sur les deux machines de (55, 60) — il y restait pris. `blocs.erreurs` le refuse maintenant.
    {"slug": "cave_voute", "ronde": [[57, 57, 0], [69, 57, 90], [69, 62, 180], [57, 62, 270]], "pause_s": 1},
    # « Plus de gardes » (Martin, 30 sept. 2026) : cinq de plus aux étages d'avant, deux à chaque étage neuf.
    # Dehors, un deuxième tour du jardin EN SENS INVERSE, parti du coin nord-est : les deux se croisent à
    # l'ouest et à l'est de la maison, jamais au nord — le trou reste un passage. Et la pelouse de l'est.
    {"slug": "jardin_inverse", "ronde": [[50, 6, 180], [9, 6, 90], [9, 37, 0], [50, 37, 270]], "pause_s": 2},
    {"slug": "pelouse_est", "ronde": [[53, 7, 90], [53, 36, 270]], "pause_s": 3},
    {"slug": "salon", "ronde": [[15, 13, 0], [25, 13, 90], [25, 21, 180], [15, 21, 270]], "pause_s": 2},
    {"slug": "etage_chambres", "ronde": [[5, 52, 90], [5, 62, 270]], "pause_s": 2},
    {"slug": "cave_cellier", "ronde": [[40, 62, 270], [40, 49, 90]], "pause_s": 2},
    # Le 2e étage : le corridor devant le bureau, et la bibliothèque (l'autre chemin, par le salon).
    {"slug": "second_corridor", "ronde": [[2, 80, 0], [33, 81, 180]], "pause_s": 2},
    {"slug": "second_bibliotheque", "ronde": [[25, 85, 0], [34, 85, 90], [34, 91, 180], [25, 91, 270]],
     "pause_s": 2},
    # Le sous-sol : le couloir de la voûte (⚠️ il tourne à huit tuiles du terminal : on pirate dans son dos)
    # et la salle des serveurs.
    {"slug": "sous_sol_couloir", "ronde": [[38, 89, 0], [52, 89, 180]], "pause_s": 2},
    {"slug": "sous_sol_serveurs", "ronde": [[59, 75, 90], [59, 85, 0], [69, 85, 270], [69, 75, 180]],
     "pause_s": 2},
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
    "noms_des_cadres": NOMS_DES_CADRES,
    "prive": PRIVE,
    "gardes": GARDES,
    "regles_des_gardes": REGLES,
    # ⚠️ LA NUIT TIENT (Martin, 30 sept. 2026) : de nuit, l'horloge s'arrête tant qu'on est dans la villa —
    # une infiltration prudente, avec dix-sept gardes, durait plus qu'une nuit (`Monde.majHeure`).
    "nuit_tient": True,
    # Les deux lampadaires de la grille, et quelques lampes dedans : le reste est noir, la nuit — c'est là
    # qu'on se cache.
    "lampes": [{"x": 58, "y": 19, "r": 40, "c": "lampadaire"}, {"x": 58, "y": 24, "r": 40, "c": "lampadaire"},
               {"x": 42, "y": 15, "r": 26, "c": "fenetre"}, {"x": 30, "y": 24, "r": 26, "c": "fenetre"},
               {"x": 17, "y": 57, "r": 26, "c": "fenetre"}, {"x": 54, "y": 64, "r": 26, "c": "fenetre"},
               {"x": 60, "y": 89, "r": 26, "c": "fenetre"}, {"x": 29, "y": 75, "r": 26, "c": "fenetre"},
               {"x": 18, "y": 87, "r": 26, "c": "fenetre"}, {"x": 64, "y": 79, "r": 26, "c": "fenetre"}],
}
