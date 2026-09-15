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
