"""Le classeur de la PAUSE : des onglets qu'on tourne aux epaules (LB/RB), a la
croix, aux fleches ← →, ou qu'on touche du doigt ; des sous-pages qui gardent
leur onglet ; des titres de section que le curseur saute.

Demande de Martin (22 sept. 2026) : « remanier tous les menus pour que ce soit
plus convivial et plus facile de s'y retrouver — des onglets cliquables ou
deplacables avec les touches R et L ». Juge PAR LE BOUTON, et sur SA manette :
une 8BitDo en Bluetooth, que le navigateur ne reconnait pas (`mapping: ""`),
disposition `bt_dinput` — epaules 6 et 7, FRAPPE a 3, croix sur l'axe 9.
"""

#: La manette de Martin, et ce qu'on en fait au banc. ⚠️ Un appui se tient deux
#: images (un appui d'une image tombe parfois entre deux pas de la boucle).
MARTIN = """
    const REPOS = 1.2857142857142858, DROITE = -0.42857142857142855, GAUCHE = 0.7142857142857143;
    function martin(L) {
        const p = L.B.defs.manettes.profils.find(function (q) { return q.slug === 'bt_dinput'; });
        L.Entree.reglerManette(p);
        L.B.options.manette = L.Entree.profilManette();
        L.B.options.manetteProfil = 'bt_dinput';
    }
    function rien() { return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; }
    function bouton(o, i) {
        const b = rien(); b[i] = 1;
        o.pad([0, 0, 0, 0, 0, 0, 0, 0, 0, REPOS], b, { mapping: '' }); o.frame(2);
        o.pad([0, 0, 0, 0, 0, 0, 0, 0, 0, REPOS], rien(), { mapping: '' }); o.frame(2);
    }
    function croix(o, v) {
        o.pad([0, 0, 0, 0, 0, 0, 0, 0, 0, v], rien(), { mapping: '' }); o.frame(2);
        o.pad([0, 0, 0, 0, 0, 0, 0, 0, 0, REPOS], rien(), { mapping: '' }); o.frame(2);
    }
    function ou(L) {
        const m = L.B.menu;
        if (!m) return L.B.etat;
        if (!m.classeur) return 'hors:' + m.titre;
        return m.classeur.onglet + (m.classeur.racine ? '' : '/' + m.titre);
    }
"""


def test_les_epaules_de_la_manette_de_martin_tournent_les_onglets(banc):
    """RB tourne a droite, LB a gauche, et on fait le tour du classeur ; la croix
    (sur un axe) tourne aussi. ⚠️ RB est AUSSI FRAPPE, qui ferme un menu : il
    tourne sans rien fermer. FRAPPE a la croix de droite (le 3), lui, reprend."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MARTIN + """
        martin(L);
        L.Jeu.pause();
        const vu = [ou(L)];
        bouton(o, 7); vu.push(ou(L));
        bouton(o, 7); vu.push(ou(L));
        bouton(o, 6); vu.push(ou(L));
        bouton(o, 6); vu.push(ou(L));
        bouton(o, 6); vu.push(ou(L));
        croix(o, DROITE); vu.push(ou(L));
        croix(o, GAUCHE); vu.push(ou(L));
        bouton(o, 3);
        return { vu: vu, apresFrappe: ou(L), appareil: L.Entree.appareil };
    }""")
    assert r["vu"] == ["pause", "carnet", "bilan", "carnet", "pause", "options", "pause", "options"], r["vu"]
    assert r["apresFrappe"] == "jeu", "FRAPPE (le 3, pas l'epaule) reprend la partie depuis un onglet"
    assert r["appareil"] == "manette"


def test_le_clavier_tourne_aux_fleches_et_echap_reprend(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MARTIN + """
        o.tape('Escape', 2);
        const vu = [ou(L)];
        o.tape('ArrowRight', 2); vu.push(ou(L));
        o.tape('ArrowLeft', 2); vu.push(ou(L));
        o.tape('ArrowLeft', 2); vu.push(ou(L));
        o.tape('Escape', 2);
        return { vu: vu, apres: ou(L) };
    }""")
    assert r["vu"] == ["pause", "carnet", "pause", "options"]
    assert r["apres"] == "jeu"


def test_une_sous_page_garde_son_onglet_et_b_recule(banc):
    """Le JOURNAL s'ouvre du CARNET : l'onglet CARNET reste allume, B recule au
    carnet, et l'epaule mene a l'onglet d'a cote depuis la sous-page meme."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MARTIN + """
        martin(L);
        L.Jeu.pause();
        bouton(o, 7);                                   // CARNET
        const carnet = L.B.menu.items.map(function (i) { return i.libelle; });
        croix(o, 0.14285714285714285);                  // BAS : JOURNAL
        bouton(o, 0);                                   // A
        const journal = ou(L);
        bouton(o, 1);                                   // B
        const recule = ou(L);
        croix(o, 0.14285714285714285); bouton(o, 0);
        bouton(o, 7);                                   // RB depuis le journal
        const aCote = ou(L);
        return { carnet: carnet, journal: journal, recule: recule, aCote: aCote };
    }""")
    assert "RETOUR" not in r["carnet"], "un onglet n'a pas de RETOUR a chercher : B reprend"
    assert r["journal"] == "carnet/JOURNAL"
    assert r["recule"] == "carnet"
    assert r["aCote"] == "bilan"


def test_sur_l_ecran_manette_les_epaules_s_essaient_sans_tourner(banc):
    """On y ESSAIE sa manette, epaules comprises : ni RB ni la croix n'y
    tournent l'onglet. Les fleches du clavier, elles, tournent."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MARTIN + """
        martin(L);
        L.Jeu.pause();
        L.Hud.ouvrirOnglet('options');
        L.B.menu.items.find(function (i) { return i.libelle === 'MANETTE'; }).faire();
        const avant = ou(L);
        bouton(o, 7); const rb = ou(L);
        croix(o, DROITE); const droite = ou(L);
        o.pad(null); o.frame(2);
        o.tape('ArrowRight', 2);
        return { avant: avant, rb: rb, droite: droite, fleche: ou(L) };
    }""")
    assert r["avant"] == r["rb"] == r["droite"] == "options/MANETTE"
    assert r["fleche"] == "pause"


def test_les_titres_de_section_se_sautent(banc):
    """Les TRICHES sont rangees en sections : le curseur passe par-dessus leurs
    titres, dans les deux sens, et ne s'y pose jamais."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.triches.menu = true;
        L.Jeu.pause();
        L.Hud.ouvrirOnglet('triches');
        const m = L.B.menu;
        const libelle = function () { return m.items[m.curseur].libelle; };
        const entetes = m.items.filter(function (i) { return i.entete; }).map(function (i) { return i.entete; });
        const depart = libelle();
        m.curseur = m.items.findIndex(function (i) { return i.libelle === 'LA POLICE NE T\\'ARRÊTE PAS'; });
        o.tape('ArrowDown', 2); const apresPolice = libelle();
        o.tape('ArrowUp', 2); const retourPolice = libelle();
        const poses = [];
        for (let k = 0; k < m.items.length + 2; k++) { o.tape('ArrowDown', 2); poses.push(!!m.items[m.curseur].entete); }
        m.curseur = 1;
        o.tape('ArrowUp', 2); const tour = libelle();
        return { entetes: entetes, depart: depart, apresPolice: apresPolice, retourPolice: retourPolice,
                 surUnTitre: poses.some(Boolean), tour: tour, titre: m.titre };
    }""")
    assert r["entetes"] == ["LE JOUEUR", "ALLER", "LA MISSION", "DIVERS"]
    assert r["depart"] == "ARGENT +1 000 $"
    assert r["apresPolice"] == "TÉLÉPORTER À L'OBJECTIF", "le titre ALLER se saute"
    assert r["retourPolice"] == "LA POLICE NE T'ARRÊTE PAS"
    assert r["surUnTitre"] is False
    assert r["tour"] == "JUKEBOX", "en haut, un appui neuf fait le tour sans se poser sur LE JOUEUR"


def test_un_onglet_et_une_ligne_se_touchent(banc):
    """Au doigt et a la souris : toucher un onglet l'ouvre, toucher une ligne la
    choisit — la ou le dernier dessin les a poses. Toucher a cote ne fait rien.
    Et un comptoir (hors classeur) a aussi ses lignes a toucher."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.pause();
        o.frame(1);
        function centre(z) { return [z.x + z.l / 2, z.y + z.h / 2]; }
        function toucher(z) { const c = centre(z); L.Hud.toucherMenu(c[0], c[1]); o.frame(2); }
        const onglets = L.Hud.ciblesDuMenu().filter(function (z) { return z.onglet; }).map(function (z) { return z.onglet; });
        toucher(L.Hud.ciblesDuMenu().find(function (z) { return z.onglet === 'options'; }));
        const options = L.B.menu.titre;
        const iSang = L.B.menu.items.findIndex(function (i) { return i.libelle === 'SANG'; });
        const sang = L.B.options.sang;
        toucher(L.Hud.ciblesDuMenu().find(function (z) { return z.item === iSang; }));
        const bascule = L.B.options.sang !== sang, reste = L.B.menu.titre;
        L.Hud.toucherMenu(2, 268); o.frame(2);
        const aCote = L.B.menu.titre;
        L.Hud.fermerMenu(); L.Jeu.reprendre();
        let achete = 0;
        L.Hud.ouvrirMenu({ titre: 'COMPTOIR', items: [{ libelle: 'UN HOT-DOG', faire: function () { achete++; return false; } },
                                                     { libelle: 'MERCI', faire: function () { return true; } }] });
        o.frame(1);
        toucher(L.Hud.ciblesDuMenu().find(function (z) { return z.item === 0; }));
        toucher(L.Hud.ciblesDuMenu().find(function (z) { return z.item === 0; }));
        const hotdogs = achete;
        toucher(L.Hud.ciblesDuMenu().find(function (z) { return z.item === 1; }));
        return { onglets: onglets, options: options, bascule: bascule, reste: reste, aCote: aCote,
                 hotdogs: hotdogs, comptoir: L.B.menu };
    }""")
    assert r["onglets"] == ["pause", "carnet", "bilan", "commandes", "options"]
    assert r["options"] == "OPTIONS"
    assert r["bascule"] is True and r["reste"] == "OPTIONS"
    assert r["aCote"] == "OPTIONS"
    assert r["hotdogs"] == 2 and r["comptoir"] is None


def test_les_onglets_ne_bougent_pas_d_une_page_a_l_autre(banc):
    """COMMANDES est plus large que les autres pages : la rangee d'onglets est
    centree sur l'ECRAN et la boite a le haut fixe — rien ne glisse sous le
    doigt quand on tourne. Et elle reste entre les pouces du telephone : les
    lignes d'une liste tiennent dans les 320 px du milieu."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.pause();
        const vu = {};
        for (const slug of L.Hud.onglets()) {
            L.Hud.ouvrirOnglet(slug); o.frame(1);
            const z = L.Hud.ciblesDuMenu();
            vu[slug] = { onglets: z.filter(function (q) { return q.onglet; }).map(function (q) { return [q.x, q.y, q.l]; }),
                         lignes: z.filter(function (q) { return q.item !== undefined; }).map(function (q) { return [q.x, q.x + q.l]; }) };
        }
        return vu;
    }""")
    rangees = {slug: v["onglets"] for slug, v in r.items()}
    premiere = next(iter(rangees.values()))
    assert all(v == premiere for v in rangees.values()), rangees
    for slug, v in r.items():
        for x0, x1 in v["lignes"]:
            assert x0 >= 80 and x1 <= 400, (slug, x0, x1)


def test_au_doigt_une_diagonale_ne_tourne_pas_l_onglet(banc):
    """⚠️ Au telephone, le pouce monte et descend dans la liste : une diagonale
    passe par GAUCHE sans qu'on veuille changer de page. Seul un geste
    franchement de cote tourne l'onglet (la croix tactile est au banc a 90, 570)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.pause();
        o.pointeur('pointerdown', 90, 570, 1); o.pointeur('pointermove', 60, 530, 1); o.frame(2);
        const diagonale = { onglet: L.B.menu.classeur.onglet, curseur: L.B.menu.items[L.B.menu.curseur].libelle };
        o.pointeur('pointerup', 60, 530, 1); o.frame(2);
        o.pointeur('pointerdown', 90, 570, 1); o.pointeur('pointermove', 140, 572, 1); o.frame(2);
        const cote = L.B.menu.classeur.onglet;
        o.pointeur('pointerup', 140, 572, 1); o.frame(2);
        return { diagonale: diagonale, cote: cote };
    }""")
    assert r["diagonale"] == {"onglet": "pause", "curseur": "QUITTER VERS LE TITRE"}, "la diagonale monte dans la liste"
    assert r["cote"] == "carnet", "de cote, le pouce tourne l'onglet"


def test_en_coop_les_epaules_suivent_celui_qui_tient_la_manette(banc):
    """La coop locale (essai) : par defaut la manette est celle du DEUXIEME
    joueur, et rien de ce qu'elle pese ne fait agir le premier — pas meme
    tourner les onglets de sa pause ; le clavier du premier, lui, tourne. Avec
    JOUEUR 1 À LA MANETTE, c'est l'inverse : l'epaule tourne."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MARTIN + """
        martin(L);
        L.Jeu.basculerCoop();
        L.Jeu.pause();
        bouton(o, 7); const rb = ou(L);
        croix(o, DROITE); const croixDroite = ou(L);
        o.tape('ArrowRight', 2);
        const clavier = ou(L);
        L.B.options.coopP1Manette = true;
        bouton(o, 7); const sienne = ou(L);
        return { coop: !!L.B.coop, rb: rb, croix: croixDroite, clavier: clavier, sienne: sienne };
    }""")
    assert r["coop"] is True
    assert r["rb"] == "pause" and r["croix"] == "pause"
    assert r["clavier"] == "carnet"
    assert r["sienne"] == "bilan", "quand le joueur 1 tient la manette, son epaule tourne l'onglet"
