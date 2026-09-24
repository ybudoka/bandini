"""Le trottoir : une seule source pour sa largeur, des deux côtés du fil.

⚠️ **Le premier pas d'un chantier qu'on a déjà essayé et annulé** (14 sept.
2026). `TROTTOIR` ne décore rien : `_coupe()` la lit pour découper CHAQUE rue,
et la traverse d'un croisement fait exactement `TROTTOIR` tuiles de profond —
c'est la même constante des deux côtés, par construction.

Or `monde.js` rangeait les tuiles d'un croisement avec deux littéraux, `inter.y
- 2` et `inter.x - 2`, « pour inclure les passages piétons, deux tuiles de
chaque côté ». Le jour où la constante bouge, Python dessinerait des traverses
d'une tuile et le JS en réclamerait encore deux : un piéton demanderait à quel
feu obéir en se tenant sur la chaussée, et un char lirait un croisement là où il
n'y en a plus.

La fiche le disait : « ce littéral doit lire le paquet **avant** qu'on touche à
la constante ». Ces juges-ci sont ce « avant » — ils ne changent rien à la
ville, et ils rendent le changement possible.
"""

from app import carte


def test_la_largeur_du_trottoir_descend_dans_le_paquet():
    """⚠️ Le défaut qui revient : une fiche que le navigateur ne lisait pas. Ici
    c'est le symétrique — un nombre que le navigateur réécrivait tout seul."""
    grille = carte.exporter()["grille"]
    assert grille["trottoir"] == carte.TROTTOIR
    assert grille["trottoir"] >= 1


def test_la_traverse_fait_exactement_la_largeur_du_trottoir():
    """⚠️ CE N'EST PAS UNE COÏNCIDENCE, C'EST LA DÉFINITION : une traverse est le
    prolongement du trottoir à travers la chaussée, et elle en fait donc la
    largeur. La demande de Martin sur les traverses n'est pas un deuxième
    chantier — c'est la preuve que le premier est le bon, et ce juge tient les
    deux ensemble : le jour où `TROTTOIR` passera à 1, il rougira si les
    traverses restent à 2.

    ⚠️ On mesure la LARGEUR DU COULOIR, pas sa longueur. Une traverse « = »
    fait `TROTTOIR` tuiles de large en **x** et traverse la chaussée sur toute
    sa hauteur ; une « : », l'inverse. Mesuré sur le mauvais axe, on lit la
    largeur de la RUE (deux ou quatre voies) et le juge accuse la géométrie
    d'une chose qu'elle n'a jamais dite."""
    ville = carte.exporter()
    sol, largeur, hauteur = ville["sol"], ville["largeur"], ville["hauteur"]
    passages = {"=": [], ":": []}
    for y in range(hauteur):
        ligne = sol[y]
        for x in range(largeur):
            if ligne[x] in passages:
                passages[ligne[x]].append((x, y))
    assert passages["="] and passages[":"], "la ville n'a plus de passages piétons"

    def largeurs(points, fixe, mobile):
        """Les largeurs des bandes contiguës, tranche par tranche."""
        par_tranche: dict[int, list[int]] = {}
        for point in points:
            par_tranche.setdefault(point[fixe], []).append(point[mobile])
        trouvees = []
        for valeurs in par_tranche.values():
            valeurs.sort()
            debut = precedent = valeurs[0]
            for v in valeurs[1:] + [None]:
                if v is None or v != precedent + 1:
                    trouvees.append(precedent - debut + 1)
                    if v is not None:
                        debut = v
                if v is not None:
                    precedent = v
        return trouvees

    # « = » : on lit sa largeur en x, rangée par rangée. « : » : en y, colonne
    # par colonne. Chaque tranche traverse un couloir de part en part.
    for glyphe, fixe, mobile in (("=", 1, 0), (":", 0, 1)):
        trouvees = set(largeurs(passages[glyphe], fixe, mobile))
        assert trouvees == {carte.TROTTOIR}, (
            f"les traverses « {glyphe} » font {sorted(trouvees)} tuiles de large "
            f"et le trottoir en fait {carte.TROTTOIR}"
        )


def test_le_navigateur_lit_la_largeur_au_lieu_de_l_ecrire(banc):
    """⚠️ LE JUGE QUI TIENT LE PRÉREQUIS. On ne lit pas le code source : on
    donne au navigateur un paquet dont le trottoir fait une tuile, et on compte
    les tuiles qu'il range comme « croisement ». Si le 2 était encore écrit en
    dur, la marge ne bougerait pas d'un pouce.

    ⚠️ Et le témoin est indispensable dans les deux sens : sans la mesure à
    deux, un `charger` qui ne rangerait RIEN passerait au vert."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const def = L.Monde.carte.def;
        const compter = function (bord) {
            def.grille.trottoir = bord;
            L.Monde.charger(def);
            const inter = def.intersections[0];
            let dedans = 0;
            // On balaie large autour du croisement et on compte ce que le
            // moteur reconnait comme etant a lui.
            for (let y = inter.y - 4; y < inter.y + inter.h + 4; y++) {
                for (let x = inter.x - 4; x < inter.x + inter.l + 4; x++) {
                    if (L.Monde.intersectionA(x, y) === inter) dedans++;
                }
            }
            return { dedans: dedans, l: inter.l, h: inter.h };
        };
        // ⚠️ ON LIT LA VRAIE VALEUR AVANT DE LA TRAFIQUER : `def` EST
        // `L.B.defs.carte`, le meme objet. La relire apres, c'est relire ce
        // qu'on vient d'y ecrire.
        const vrai = def.grille.trottoir;
        const aDeux = compter(2), aUne = compter(1);
        def.grille.trottoir = vrai; L.Monde.charger(def);
        return { aDeux: aDeux, aUne: aUne, vrai: vrai };
    }""")
    # La marge attendue est géométrique : (l + 2b) × (h + 2b).
    def attendu(inter, bord):
        return (inter["l"] + 2 * bord) * (inter["h"] + 2 * bord)

    assert r["aDeux"]["dedans"] == attendu(r["aDeux"], 2), (
        "le décor du juge est faux : la marge à deux ne fait pas ce que la géométrie dit (%s)" % r
    )
    assert r["aUne"]["dedans"] == attendu(r["aUne"], 1), (
        "le navigateur n'a pas lu la largeur du paquet : il range encore deux tuiles (%s)" % r
    )
    assert r["aUne"]["dedans"] < r["aDeux"]["dedans"], r
    assert r["vrai"] == carte.TROTTOIR, "le paquet ne porte plus la largeur : %s" % r


# --- Le trottoir a une tuile : ce que la fiche exige --------------------------


def test_la_largeur_de_la_ville_suit_sa_trame():
    """La ville fait exactement la somme de ses blocs et de ses rues, dans les
    deux sens. ⚠️ C'est ce qui a permis de rétrécir les rues et d'élargir les
    blocs sans rien casser : un juge de trame ne dit rien de la beauté, mais il
    dit tout de suite si une rue a été comptée deux fois."""
    ville = carte.exporter()
    # ⚠️ À l'est de la trame, le relief (21 sept. 2026) : la carte s'allonge d'une
    # chaîne de montagnes après la dernière rue, et pas une colonne de blocs ne bouge.
    largeur_trame = sum(carte.COLONNES) + sum(carte.RUES_V)
    montagnes = ville["relief"]["montagnes"]
    assert montagnes["x"] == largeur_trame and ville["largeur"] == largeur_trame + montagnes["l"]
    # ⚠️ Sous la trame, l'aéroport (21 sept. 2026) : la carte s'allonge jusqu'au bas
    # de son plan, et pas une rangée de blocs ne bouge.
    _, y0, _, hauteur = ville["aeroport"]["plan"]
    assert sum(carte.RANGEES) + sum(carte.RUES_H) < y0 and ville["hauteur"] == y0 + hauteur


def test_une_rue_garde_deux_voies_et_un_boulevard_quatre():
    """⚠️ Les deux tuiles que chaque rue a perdues ne sont PAS revenues aux
    voies : c'était l'option que la fiche refusait (« ce n'est pas ce qui a été
    demandé »). Une rue fait deux voies, un boulevard quatre — comme avant."""
    voies = {largeur - 2 * carte.TROTTOIR for largeur in carte.RUES_V + carte.RUES_H}
    assert voies == {2, 4}, f"des rues à {sorted(voies)} voies"
    coupe = carte._coupe(min(carte.RUES_V), True)
    assert coupe[0] == (".", ".") and coupe[-1] == (".", "."), "la rue ne commence pas par son trottoir"
    assert sum(1 for g, _ in coupe if g == ".") == 2 * carte.TROTTOIR, "plus d'une tuile de trottoir par bord"


def test_aucune_tuile_reservee_ne_tombe_sur_la_chaussee():
    """`poser_porte` réserve deux tuiles devant chaque porte (le pas, puis la
    dalle). ⚠️ Avec un trottoir d'une tuile, la deuxième réservée pouvait tomber
    sur la chaussée — la fiche le prévoyait. Ce n'est pas le cas parce que
    l'abord s'est glissé entre le bâtiment et la dalle, et ce juge le tient."""
    ville = carte.exporter()
    sol = ville["sol"]
    for porte in ville["portes"]:
        for j in (1, 2):
            y = porte["y"] + j
            if y >= ville["hauteur"]:
                continue
            glyphe = sol[y][porte["x"]]
            fiche = carte.LEGENDE[glyphe]
            # ⚠️ La CHAUSSEE, pas un stationnement : la guerite de la fourriere
            # ouvre sur la cour d'asphalte du lot, et c'est voulu — on y entre
            # pour racheter son char. Ce qu'on interdit, c'est une porte qui
            # ouvre sur les voies, la ou les chars roulent.
            assert not (fiche.get("route") and not fiche.get("stationnement")), (
                f"devant la porte {porte.get('lieu', porte.get('interieur'))} en "
                f"({porte['x']},{porte['y']}), la tuile {j} est de la chaussée : « {glyphe} »"
            )


def test_rien_ne_bouche_la_seule_tuile_de_trottoir_devant_une_porte():
    """⚠️ Le trottoir ne fait plus qu'une tuile : un kiosque, une borne ou un
    lampadaire posé dessus devant une porte en ferait une impasse. Le mobilier
    de rue vit sur l'ABORD (la couronne du bloc) ; la dalle devant une porte
    reste libre."""
    ville = carte.exporter()
    sol = ville["sol"]
    occupe = {(d["x"], d["y"]) for d in ville["decor"]}
    occupe |= {(a["x"], a["y"]) for a in ville.get("ambulants", [])}
    bouches = []
    for porte in ville["portes"]:
        x = porte["x"]
        for j in range(1, 6):
            y = porte["y"] + j
            if y >= ville["hauteur"] or carte.routier(sol[y][x]):
                break
            if sol[y][x] == "." and (x, y) in occupe:
                bouches.append((x, y))
    assert not bouches, f"du mobilier sur la dalle devant une porte : {bouches[:5]}"


def test_aucune_largeur_de_trottoir_n_est_ecrite_en_dur():
    """⚠️ Ni en Python ni en JS : le paquet est la seule source. Côté Python, la
    traverse et la coupe lisent `TROTTOIR` ; côté JS, `test_le_navigateur_lit_la
    _largeur_au_lieu_de_l_ecrire` le prouve en jeu. Ici, on vérifie que le
    nombre de tuiles de dalle de chaque côté d'une rue EST la constante — pour
    toutes les largeurs de rue de la trame, pas seulement une."""
    for largeur in sorted(set(carte.RUES_V + carte.RUES_H)):
        for vertical in (True, False):
            coupe = carte._coupe(largeur, vertical)
            bord = 0
            while bord < len(coupe) and coupe[bord][0] == ".":
                bord += 1
            assert bord == carte.TROTTOIR, f"rue de {largeur} : {bord} tuiles de trottoir au bord"


def test_le_flaneur_prefere_la_dalle_a_l_abord(banc):
    """⚠️ La troisième décision de Martin : « priorité de marcher sur le
    trottoir ». L'abord se foule, mais c'est un débordement. On mesure la règle
    comme une DÉCISION, pas comme une promenade : un flâneur posé sur la dalle,
    face à l'abord, une image — a-t-il fait demi-tour ? Cent essais avec le
    taux de la fiche (`pietons.REACTIONS.abord_renonce`), cent à zéro comme
    témoin. (Une promenade de mille images ne prouvait rien : en le faisant
    redécider à chaque image, il piétinait sur place et n'atteignait jamais
    l'abord, renoncement ou pas.)

    ⚠️ Le juge comptait les DEMI-TOURS ; il compte les RENONCEMENTS. Le
    demi-tour était l'implémentation, pas la règle — et il envoyait parfois le
    flâneur droit sur la chaussée (le décor de ce juge-ci est exactement ça :
    l'abord au nord, la rue au sud). Voir `versLaDalle`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        // Une dalle qui longe un abord au NORD, avec de la dalle des deux cotes.
        let place = null;
        for (let y = 8; y < c.h - 8 && !place; y++) for (let x = 8; x < c.w - 8 && !place; x++) {
            if (L.Monde.estTrottoir(x, y) && L.Monde.estAbord(x, y - 1)
                && L.Monde.estTrottoir(x - 1, y) && L.Monde.estTrottoir(x + 1, y)) place = { x: x, y: y };
        }
        if (!place) return { place: null };
        const j = L.B.joueur; j.x = place.x * L.TT + 8; j.y = place.y * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        const essais = function (renonce, graine) {
            L.graine(graine);
            L.B.defs.pietons.reactions.abord_renonce = renonce;
            let renoncements = 0, avances = 0;
            for (let n = 0; n < 100; n++) {
                // ⚠️ UNE GRAINE PAR ESSAI. Posee une seule fois, elle faisait
                // mesurer un ENCHAINEMENT et non une probabilite : entre deux
                // decisions, toute la ville tire au sort, et le tirage qui tombe
                // sur le flaneur depend de tout ce qui existe ailleurs. Mesure du
                // 16 sept. 2026, sur la base : une seule caisse posee a l'autre
                // bout de la carte faisait tomber le taux de 75 % a 2 %.
                L.graine(graine + n);
                const p = o.poser('passant', 0, 0);
                p.etat = 'flane'; p.porteBut = null; p.intouchable = true;
                p.dir = 3; p.butT = 5;                     // face au nord, l'abord devant, decide
                p.y = place.y * L.TT + 8;
                L.Entites.indexer();
                o.frame(1);
                // ⚠️ ON COMPTE LE RENONCEMENT, PAS LE DEMI-TOUR : il se
                // detourne de l'abord — il ne bouge pas de l'image, et ce
                // n'est plus le nord qu'il vise. VERS OU il se detourne est
                // une autre question, et c'est `versLaDalle` qui y repond
                // (juge : `test_le_pas_d_une_porte_n_est_pas_un_piege`).
                if (p.dir !== 3 && p.vx === 0 && p.vy === 0) renoncements++;
                else if (p.vy < 0) avances++;
                L.Entites.retirer(p);
            }
            return { renoncements: renoncements, avances: avances };
        };
        const vraiTaux = L.B.defs.pietons.reactions.abord_renonce;
        const avec = essais(vraiTaux, 41), sans = essais(0, 41);
        L.B.defs.pietons.reactions.abord_renonce = vraiTaux;
        return { place: place, avec: avec, sans: sans, taux: vraiTaux };
    }""")
    assert r["place"], "le décor du juge est faux : aucune dalle ne longe un abord"
    assert 0 < r["taux"] < 1, "le renoncement n'est pas une chance : %s" % r
    # ⚠️ Le témoin est indispensable : sans renoncement, il AVANCE sur l'abord.
    assert r["sans"]["renoncements"] == 0 and r["sans"]["avances"] >= 90, (
        "le décor du juge est faux : sans renoncement, il n'avance pas vers l'abord (%s)" % r
    )
    part = r["avec"]["renoncements"] / 100
    assert abs(part - r["taux"]) < 0.15, (
        "il ne renonce pas au taux de la fiche : %s renoncements sur cent pour %s (%s)"
        % (r["avec"]["renoncements"], r["taux"], r)
    )


def test_le_pas_d_une_porte_n_est_pas_un_piege_a_flaneur(banc):
    """⚠️ **LE DEMI-TOUR SEUL TENAIT DES PASSANTS DEVANT LES PORTES, POUR
    TOUJOURS.** `poser_porte` pave l'abord jusqu'à la dalle : le pas d'une porte
    est donc UNE tuile de trottoir entre deux tuiles d'abord. Est et ouest y
    débordent tous les deux — le flâneur renonçait des deux côtés, le demi-tour
    le renvoyait de l'un à l'autre, et chaque renoncement remettait `butT` à
    trente images : il ne retirait jamais sa direction au sort. Il tremblait sur
    place à deux pixels près, le sud libre devant lui.

    Mesuré avant le correctif : onze passants sur douze n'avaient pas quitté
    leur pas de porte au bout de 1200 images — vingt secondes. Et une naissance
    sur trois se fait sur un pas de porte (`Entites.placeDeNaissance`) : ils
    s'y empilaient, et c'est ce qu'on voyait en jouant.

    Le juge pose un flâneur sur CHAQUE pas de porte piégé, face à l'abord, et
    exige qu'il en soit sorti."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // Les pas de porte piegeants : une dalle entre deux abords.
        const pieges = L.Monde.carte.portesFermees.filter(function (p) {
            return L.Monde.estTrottoir(p.x, p.y + 1)
                && L.Monde.estAbord(p.x - 1, p.y + 1) && L.Monde.estAbord(p.x + 1, p.y + 1);
        });
        const j = L.B.joueur, coinces = [];
        for (const p of pieges) {
            const x = p.x * L.TT + 8, y = (p.y + 1) * L.TT + 8;
            // Le joueur a cote : sinon la ville l'oublie et le juge ne mesure rien.
            j.x = x; j.y = y + 48;
            L.Monde.centrerCamera(j.x, j.y);
            const e = o.poser(null, 0, 0);
            e.x = x; e.y = y;
            e.etat = 'flane'; e.intouchable = true; e.porteBut = null;
            e.dir = 0; e.butT = 90;                    // face a l'est, vers l'abord
            L.Entites.indexer();
            let sorti = -1;
            for (let i = 0; i < 600 && sorti < 0; i++) {
                o.frame(1);
                // ⚠️ IL PEUT AUSSI RENTRER — une porte juste au nord, une
                // flanerie sur douze, et la ville se l'avale (`etat: 'entre'`,
                // puis `retirer`). C'est une sortie comme une autre, et le
                // juge la manquait : `retirer` ne baisse pas `actif`, il
                // DECROCHE de `B.entites`. On lit donc la liste.
                if (L.B.entites.indexOf(e) < 0) { sorti = i; break; }
                if (Math.floor(e.x / L.TT) !== p.x || Math.floor(e.y / L.TT) !== p.y + 1) sorti = i;
            }
            if (sorti < 0) coinces.push({ porte: p.x + ',' + p.y, etat: e.etat, dir: e.dir,
                                          dx: Math.round((e.x - x) * 10) / 10,
                                          dy: Math.round((e.y - y) * 10) / 10 });
            if (L.B.entites.indexOf(e) >= 0) L.Entites.retirer(e);
        }
        return { pieges: pieges.length, coinces: coinces };
    }""")
    assert r["pieges"] >= 5, (
        "le décor du juge est faux : la ville n'a que %s pas de porte entre deux abords" % r["pieges"]
    )
    assert not r["coinces"], (
        "%s flâneurs sur %s n'ont pas quitté leur pas de porte en 600 images : %s"
        % (len(r["coinces"]), r["pieges"], r["coinces"][:5])
    )
