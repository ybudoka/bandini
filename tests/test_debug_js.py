"""Le menu DEBUG : une suite secrete de touches, jamais un bouton visible — et
ses tricheries, faites pour tester a la main sans y perdre la soiree : de
l'argent, la sante, sauter l'objectif, teleporter au repere que le HUD montre
deja (`Histoire.cible`, la meme fleche que celle du joueur ordinaire).

⚠️ La suite (`SEQUENCE_DEBUG` dans `jeu.js`, « RIGOLO ») ne prend QUE des
lettres hors d'`Entree.MAP_TOUCHES` : le Konami classique (fleches, B, A) a
d'abord ete essaye, et KeyB (ANNULER) fermait le menu PAUSE puis relançait la
partie (`reprendre()`) juste avant que le dernier appui n'ouvre DEBUG
par-dessus — voir `test_pas_par_dessus_un_autre_menu`.
"""

TAPER_LA_SUITE = (
    "['KeyR','KeyI','KeyG','KeyO','KeyL','KeyO'].forEach(function (c) { o.tape(c); });"
)


def test_la_suite_secrete_ouvre_le_menu_debug_en_partie(banc):
    r = banc(
        """function (L, o) {
        L.Jeu.commencer();
        """
        + TAPER_LA_SUITE
        + """
        return { titre: L.B.menu && L.B.menu.titre };
    }"""
    )
    assert r["titre"] == "DEBUG"


def test_une_suite_fausse_n_ouvre_rien(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        ['KeyR', 'KeyI', 'KeyG', 'KeyO', 'KeyL', 'KeyR'].forEach(function (c) { o.tape(c); });
        return { menu: L.B.menu };
    }""")
    assert r["menu"] is None


def test_pas_de_menu_debug_au_titre(banc):
    """Avant JOUER, `B.etat` vaut 'titre' : la suite ne fait rien."""
    r = banc(
        """function (L, o) {
        """
        + TAPER_LA_SUITE
        + """
        return { etat: L.B.etat, menu: L.B.menu };
    }"""
    )
    assert r["etat"] == "titre"
    assert r["menu"] is None


def test_pas_par_dessus_un_autre_menu(banc):
    """La suite ne vole pas un menu deja ouvert — ici, PAUSE."""
    r = banc(
        """function (L, o) {
        L.Jeu.commencer();
        L.Jeu.pause();
        """
        + TAPER_LA_SUITE
        + """
        return { titre: L.B.menu && L.B.menu.titre };
    }"""
    )
    assert r["titre"] == "PAUSE"


def test_argent_et_sante_dans_le_menu_debug(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        j.vie = 1;
        const avant = L.B.partie.argent;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const parNom = {};
        L.B.menu.items.forEach(function (i) { parNom[i.libelle] = i; });
        const resteArgent = parNom['ARGENT +1 000 $'].faire(parNom['ARGENT +1 000 $']);
        parNom['SANTÉ COMPLÈTE'].faire(parNom['SANTÉ COMPLÈTE']);
        return { avant: avant, apres: L.B.partie.argent, resteArgent: resteArgent,
                 vie: j.vie, vieMax: j.vieMax, viePartie: L.B.partie.vie, menuOuvert: !!L.B.menu };
    }""")
    assert r["apres"] == r["avant"] + 1000
    assert r["resteArgent"] is False, "l'item garde le menu ouvert pour en reprendre"
    assert r["vie"] == r["vieMax"]
    assert r["viePartie"] == r["vieMax"]
    assert r["menuOuvert"] is True


def test_invincible_bascule_et_bloque_les_degats(banc):
    """`B.debugInvincible` recharge les images d'invincibilite ORDINAIRES a
    chaque image (voir `Jeu.maj`) : `Entites.blesser` les respecte deja pour
    tout le monde, combat, tirs, explosions et collisions compris."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle === 'INVINCIBLE'; })[0];
        const avant = item.detail;
        item.faire(item);
        const apres = item.detail;
        o.frame(5);
        const invincibleApres = j.invincible;
        const encaisse = L.Entites.blesser(j, 999, null, {});
        const vieApresCoupBloque = j.vie;
        item.faire(item);
        L.Hud.fermerMenu();               // un menu ouvert fige la simulation : rien ne decroit dessous
        o.frame(90);
        const invincibleEteint = j.invincible;
        const encaisse2 = L.Entites.blesser(j, 5, null, {});
        return { avant: avant, apres: apres, invincibleApres: invincibleApres, encaisse: encaisse,
                 vieApresCoupBloque: vieApresCoupBloque, vieMax: j.vieMax,
                 invincibleEteint: invincibleEteint, encaisse2: encaisse2, vieApresCoup2: j.vie };
    }""")
    assert (r["avant"], r["apres"]) == ("NON", "OUI")
    assert r["invincibleApres"] > 0
    assert r["encaisse"] is False, "un coup ne doit pas porter pendant INVINCIBLE"
    assert r["vieApresCoupBloque"] == r["vieMax"]
    assert r["invincibleEteint"] == 0, "et redescend a zero une fois eteint"
    assert r["encaisse2"] is True
    assert r["vieApresCoup2"] == r["vieMax"] - 5


def test_teleporter_sans_objectif_ne_bouge_personne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const x = j.x, y = j.y;
        L.Histoire.cible = function () { return null; };
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle.indexOf('TÉLÉPORTER') === 0; })[0];
        item.faire(item);
        return { actif: item.actif, x: j.x, y: j.y, ax: x, ay: y };
    }""")
    assert r["actif"] is False
    assert (r["x"], r["y"]) == (r["ax"], r["ay"])


def test_teleporter_vers_l_objectif(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const cx = j.x + 3000, cy = j.y - 500;
        L.Histoire.cible = function () { return { x: cx, y: cy }; };
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle.indexOf('TÉLÉPORTER') === 0; })[0];
        const actif = item.actif;
        item.faire(item);
        return { actif: actif, x: j.x, y: j.y, cx: cx, cy: cy };
    }""")
    assert r["actif"] is True
    assert (r["x"], r["y"]) == (r["cx"], r["cy"])


def test_teleporter_refuse_dans_une_piece(banc):
    """`Jeu.sortir` orchestre sa propre transition : le debug n'ecrase pas la
    sienne, alors il ne fait rien tant qu'on n'est pas dehors."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.interieur = {};
        const x = j.x, y = j.y;
        L.Histoire.cible = function () { return { x: j.x + 3000, y: j.y - 500 }; };
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle.indexOf('TÉLÉPORTER') === 0; })[0];
        item.faire(item);
        return { x: j.x, y: j.y, ax: x, ay: y };
    }""")
    assert (r["x"], r["y"]) == (r["ax"], r["ay"])


def test_objectif_suivant_et_terminer_actifs_seulement_en_mission(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const avant = {};
        L.B.menu.items.forEach(function (i) { avant[i.libelle] = i.actif; });
        L.Hud.fermerMenu();
        L.Histoire.commencer('m1');
        L.B.cinema = null;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const pendant = {};
        L.B.menu.items.forEach(function (i) { pendant[i.libelle] = i.actif; });
        return { avant: avant, pendant: pendant };
    }""")
    assert r["avant"]["OBJECTIF SUIVANT"] is False
    assert r["avant"]["TERMINER LA MISSION"] is False
    assert r["pendant"]["OBJECTIF SUIVANT"] is True
    assert r["pendant"]["TERMINER LA MISSION"] is True


def test_terminer_la_mission_compte_la_reussite(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Histoire.commencer('m1');
        L.B.cinema = null;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle === 'TERMINER LA MISSION'; })[0];
        const fini = item.faire(item);
        return { fini: fini, missionsFaites: L.B.partie.missionsFaites, enCours: L.B.partie.mission };
    }""")
    assert r["fini"] is True
    assert "m1" in r["missionsFaites"]
    assert r["enCours"] is None


def test_retour_ferme_le_menu_debug_par_le_clavier(banc):
    r = banc(
        """function (L, o) {
        L.Jeu.commencer();
        """
        + TAPER_LA_SUITE
        + """
        const items = L.B.menu.items.map(function (i) { return i.libelle; });
        L.B.menu.curseur = items.indexOf('RETOUR');
        o.tape('KeyE', 2);
        return { menu: L.B.menu };
    }"""
    )
    assert r["menu"] is None
