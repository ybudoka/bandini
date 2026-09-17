"""Les menus au doigt avancent d'une ligne a la fois.

Retour de Martin (17 sept. 2026) : « ameliore les controles sur mobile, surtout
dans les menus. il deplace souvent de 2 menus a la fois vers le haut et le bas. »

Trois causes, chacune gardee ici :
- le « haut » neuf du pouce bougeait le curseur, et l'axe analogique du MEME
  pouce le rebougeait a l'image suivante (la repetition n'etait pas armee) ;
- la repetition partait apres 200 ms, moins qu'un appui ordinaire ;
- un pouce qui tremble autour du seuil faisait un nouvel appui a chaque
  tremblement.

Et les boutons HAUT et BAS, affiches au doigt dans un menu, ne faisaient rien.

⚠️ Le centre de #croix est en (90, 570) d'apres le faux rectangle du banc, et le
pouce va au bout de sa course a 56 px : `mag = (distance - 8) / 48`.
"""

MENU = """
    function ouvrir() {
        const items = [];
        for (let i = 0; i < 12; i++) items.push({ libelle: 'LIGNE ' + i, faire: function () { return false; } });
        L.Hud.ouvrirMenu({ titre: 'ESSAI', items: items });
        o.frame(2);
    }
    // Le pouce a `v` de sa course vers le bas (negatif : vers le haut).
    function pouce(v) { o.pointeur('pointermove', 90, 570 + Math.sign(v) * (8 + Math.abs(v) * 48), 1); }
    function poser(v) { o.pointeur('pointerdown', 90, 570, 1); pouce(v); }
    function lacher() { o.pointeur('pointerup', 90, 570, 1); }
"""


def test_un_appui_du_pouce_avance_d_une_seule_ligne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MENU + """
        ouvrir();
        const vu = {};
        // Un appui ordinaire, court puis moins court : UNE ligne chaque fois.
        for (const images of [6, 12, 20]) {
            const avant = L.B.menu.curseur;
            poser(0.9); o.frame(images); lacher(); o.frame(4);
            vu[images] = L.B.menu.curseur - avant;
        }
        // Vers le haut, pareil.
        const avant = L.B.menu.curseur;
        poser(-0.9); o.frame(12); lacher(); o.frame(4);
        vu.haut = L.B.menu.curseur - avant;
        return vu;
    }""")
    assert r["6"] == 1 and r["12"] == 1 and r["20"] == 1, "un appui du pouce saute plus d'une ligne : %s" % r
    assert r["haut"] == -1, r


def test_le_pouce_tenu_repete_sans_s_emballer(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MENU + """
        ouvrir();
        poser(0.9);
        const suite = [];
        for (let k = 0; k < 60; k++) { o.frame(1); suite.push(L.B.menu.curseur); }
        lacher(); o.frame(2);
        return { a20: suite[19], a60: suite[59] };
    }""")
    assert r["a20"] == 1, "la repetition part avant 1/3 de seconde : %s" % r
    assert 3 <= r["a60"] <= 5, "un pouce tenu une seconde doit descendre de quelques lignes : %s" % r


def test_un_pouce_qui_tremble_autour_du_seuil_ne_compte_qu_une_fois(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MENU + """
        ouvrir();
        poser(0.55);
        // Le pouce pose sur la vitre : 0.55, 0.42, 0.56, 0.44... sans jamais
        // revenir vraiment au centre.
        for (let k = 0; k < 12; k++) { pouce(k % 2 ? 0.55 : 0.42); o.frame(1); }
        lacher(); o.frame(2);
        return L.B.menu.curseur;
    }""")
    assert r == 1, "chaque tremblement du pouce a fait une ligne : %s" % r


def test_les_boutons_haut_et_bas_marchent_au_doigt_dans_un_menu(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MENU + """
        ouvrir();
        const etiquettes = {};
        o.elements.tactile.querySelectorAll('[data-a]').forEach(function (b) { etiquettes[b.dataset.a] = b.textContent; });
        o.bouton('esquive', 'pointerdown'); o.frame(10); o.bouton('esquive', 'pointerup'); o.frame(2);
        o.bouton('esquive', 'pointerdown'); o.frame(10); o.bouton('esquive', 'pointerup'); o.frame(2);
        const apresBas = L.B.menu.curseur;
        o.bouton('arme', 'pointerdown'); o.frame(10); o.bouton('arme', 'pointerup'); o.frame(2);
        return { etiquettes: etiquettes, apresBas: apresBas, apresHaut: L.B.menu.curseur };
    }""")
    assert r["etiquettes"]["esquive"] == "BAS" and r["etiquettes"]["arme"] == "HAUT", r
    assert r["apresBas"] == 2, "le bouton BAS ne descend pas : %s" % r
    assert r["apresHaut"] == 1, "le bouton HAUT ne monte pas : %s" % r


def test_un_menu_ouvert_sous_un_pouce_deja_pousse_attend_qu_on_le_lache(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MENU + """
        poser(0.9); o.frame(4);                // on marche vers le comptoir...
        ouvrir();                              // ...et le menu s'ouvre sous le pouce
        o.frame(90);
        const tenu = L.B.menu.curseur;
        lacher(); o.frame(4);
        poser(0.9); o.frame(10); lacher(); o.frame(4);
        return { tenu: tenu, apres: L.B.menu.curseur };
    }""")
    assert r["tenu"] == 0, "le curseur a file sous un pouce qui marchait encore : %s" % r
    assert r["apres"] == 1, r


def test_la_manette_et_le_clavier_font_toujours_une_ligne_par_appui(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + MENU + """
        ouvrir();
        o.pad([0, 0.9], [0, 0]); o.frame(12); o.pad([0, 0], [0, 0]); o.frame(4);
        const stick = L.B.menu.curseur;
        // Un stick qui tremble autour du seuil ne compte qu'une fois (0.8 et 0.5
        // bruts font 0.8 et 0.4 apres la zone morte).
        for (let k = 0; k < 10; k++) { o.pad([0, k % 2 ? 0.8 : 0.5], [0, 0]); o.frame(1); }
        o.pad([0, 0], [0, 0]); o.frame(4);
        const tremble = L.B.menu.curseur;
        o.pad(null); o.frame(2);
        o.tape('KeyS', 2);
        const clavier = L.B.menu.curseur;
        o.touche('KeyW'); o.frame(60); o.relacher('KeyW'); o.frame(2);
        return { stick: stick, tremble: tremble, clavier: clavier, tenu: L.B.menu.curseur };
    }""")
    assert r["stick"] == 1 and r["tremble"] == 2 and r["clavier"] == 3, r
    # Une fleche tenue repete aussi, maintenant, et s'arrete en haut de la liste
    # au lieu d'en faire le tour.
    assert r["tenu"] == 0, r
