"""La lecture des passants au banc (`docs/jalons/la-reputation-et-la-lecture-des-passants.md`, vague 1) : on TIENT
LIRE en regardant un passant, sa ligne s'affiche au-dessus de lui ; on lâche, elle s'en va. Un enfant ne se lit
pas, rien ne se tire au dé, et lire ne change rien à la partie ni au passant."""

PRELUDE = """
    L.Jeu.commencer(); if (L.B.menu) L.Hud.fermerMenu();
    const j = L.B.joueur;
    j.intouchable = true;
    const ligne = o.ligneDroite(); j.x = ligne.x; j.y = ligne.y; j.angle = 0; j.face = 'droite';
    L.Monde.centrerCamera(j.x, j.y);
    for (const e of L.B.entites.slice()) if ((e.type === 'pieton' || e.type === 'vehicule') && Math.hypot(e.x - j.x, e.y - j.y) < 260) L.Entites.retirer(e);
    L.Entites.indexer();
    function lot(e) { return L.B.defs.lectures.lignes[L.Lecture.quartierDe(e)] || []; }
    function tenir(n) { o.touche('KeyY'); o.frame(n || 3); }
    function lacher() { o.relacher('KeyY'); o.frame(2); }
"""


def test_tenir_lire_montre_la_ligne_du_passant_regarde_lacher_l_efface(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const p = o.poser('passant', 50, 0);
        o.frame(1);
        const avant = L.B.lecture;
        tenir(4);
        const lu = L.B.lecture && { cible: L.B.lecture.cible === p, ligne: L.Lecture.ligneDe(p) };
        lacher();
        return { avant: avant, lu: lu, dansLeLot: lot(p).indexOf(lu && lu.ligne) >= 0, apres: L.B.lecture };
    }""")
    assert r["avant"] is None and r["apres"] is None, r
    assert r["lu"]["cible"] and r["dansLeLot"], f"la ligne ne vient pas du lot de son quartier : {r}"


def test_on_lit_celui_qu_on_regarde_pas_celui_d_a_cote_ni_celui_de_derriere(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const devant = o.poser('passant', 70, 0), derriere = o.poser('passante', -30, 0), cote = o.poser('ouvrier', 0, 50);
        o.frame(1);
        tenir(3);
        const lu = L.B.lecture && L.B.lecture.cible;
        return { devant: lu === devant, derriere: lu === derriere, cote: lu === cote };
    }""")
    assert r == {"devant": True, "derriere": False, "cote": False}, r


def test_la_cible_ne_saute_pas_d_une_tete_a_l_autre_tant_qu_on_tient(banc):
    """Un passant plus proche entre dans le regard pendant qu'on en lit un autre : la fiche reste sur le premier."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const loin = o.poser('passant', 90, 0);
        o.frame(1); tenir(3);
        const premier = L.B.lecture && L.B.lecture.cible === loin;
        const pres = o.poser('passante', 30, 2);
        o.frame(3);
        return { premier: premier, reste: L.B.lecture && L.B.lecture.cible === loin };
    }""")
    assert r == {"premier": True, "reste": True}, r


def test_un_enfant_ne_se_lit_jamais(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const petit = o.poser('enfant', 40, 0), velo = o.poser('enfant_velo', 60, 0), ado = o.poser('ado', 80, 0);
        o.frame(1); tenir(4);
        const seuls = L.B.lecture;
        const grand = o.poser('passant', 100, 0);
        o.frame(3);
        return { seuls: seuls, grand: L.B.lecture && L.B.lecture.cible === grand,
                 lisibles: [petit, velo, ado].map(L.Lecture.lisible) };
    }""")
    assert r["seuls"] is None, f"un enfant a une fiche : {r}"
    assert r["lisibles"] == [False, False, False], r
    assert r["grand"], f"les enfants devant cachent le grand derrière eux : {r}"


def test_rien_au_de_la_ligne_tient_a_l_identifiant_et_se_garde(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const p = o.poser('passant', 50, 0);
        o.frame(1);
        let des = 0; const rng = L.B.rng;
        L.B.rng = function () { des++; return rng.apply(this, arguments); };
        const premiere = L.Lecture.ligneDe(p);
        delete p.lecture;
        const seconde = L.Lecture.ligneDe(p);
        p.x += 4000;                                   // il change de quartier : il garde son histoire
        const ailleurs = L.Lecture.ligneDe(p);
        L.B.rng = rng;
        // Le lot du Faubourg, lu par 400 identifiants qui s'y tiennent : chaque ligne y sort.
        const z = L.B.defs.carte.zones.find(function (q) { return q.slug === 'faubourg'; });
        const l = L.B.defs.lectures.lignes.faubourg, vues = {};
        for (let id = 1; id <= 400; id++) vues[L.Lecture.ligneDe({ id: id, x: (z.x + 4) * L.TT, y: (z.y + 4) * L.TT })] = 1;
        return { des: des, meme: premiere === seconde, garde: ailleurs === premiere, vues: Object.keys(vues).length, n: l.length };
    }""")
    assert r["des"] == 0 and r["meme"] and r["garde"], r
    assert r["vues"] == r["n"], f"des lignes du Faubourg ne sortent jamais : {r}"


def test_lire_ne_change_rien_ni_a_la_partie_ni_au_passant(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const p = o.poser('passant', 50, 0);
        o.frame(1); o.touche('KeyY'); o.frame(1);
        const partie = JSON.stringify(L.B.partie), lui = JSON.stringify([p.x, p.y, p.etat, p.argent, p.vie, p.cri, p.angle]);
        for (let i = 0; i < 60; i++) L.Lecture.maj();
        return { lu: !!L.B.lecture, partie: JSON.stringify(L.B.partie) === partie,
                 lui: JSON.stringify([p.x, p.y, p.etat, p.argent, p.vie, p.cri, p.angle]) === lui };
    }""")
    assert r == {"lu": True, "partie": True, "lui": True}, r


def test_au_volant_on_ne_lit_pas(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const v = o.char('auto', 0, 0); L.Vehicules.monter(j, v);
        const p = o.poser('passant', 60, 0);
        o.frame(2); tenir(4);
        return { lu: L.B.lecture };
    }""")
    assert r["lu"] is None, r


def test_la_fiche_se_peint_au_dessus_de_la_tete(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const p = o.poser('passant', 50, 0);
        o.frame(1); tenir(8);
        const ecrits = []; const t = L.Atlas.texte;
        L.Atlas.texte = function (ctx, s, x, y) { ecrits.push({ s: s, y: y }); return t.apply(this, arguments); };
        L.Jeu.rendre();
        L.Atlas.texte = t;
        const rangees = L.Lecture.ranger(L.Lecture.ligneDe(p), L.B.defs.lectures.largeur_rangee);
        const peintes = ecrits.filter(function (e) { return rangees.indexOf(e.s) >= 0; });
        return { rangees: rangees.length, peintes: peintes.length,
                 dessus: peintes.every(function (e) { return e.y < p.y - L.B.cam.y - 20; }) };
    }""")
    assert r["peintes"] == r["rangees"] >= 1 and r["dessus"], r


def test_a_la_manette_la_gachette_de_gauche_lit(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const p = o.poser('passant', 50, 0);
        const b = []; for (let i = 0; i < 17; i++) b.push(0);
        o.pad([0, 0, 0, 0], b); o.frame(2);
        b[6] = 1; o.pad([0, 0, 0, 0], b); o.frame(3);
        const lu = L.B.lecture && L.B.lecture.cible === p;
        b[6] = 0; o.pad([0, 0, 0, 0], b); o.frame(2);
        return { lu: lu, apres: L.B.lecture };
    }""")
    assert r == {"lu": True, "apres": None}, r


def test_au_doigt_le_bouton_lire(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        const p = o.poser('passant', 50, 0);
        o.frame(1);
        o.bouton('lire', 'pointerdown'); o.frame(3);
        const lu = L.B.lecture && L.B.lecture.cible === p;
        o.bouton('lire', 'pointerup'); o.frame(2);
        return { lu: lu, apres: L.B.lecture };
    }""")
    assert r == {"lu": True, "apres": None}, r


def test_sans_la_suite_on_tient_lire_et_rien_ne_leve(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        delete L.B.defs.lectures;
        const p = o.poser('passant', 50, 0);
        o.frame(1); tenir(4);
        L.Jeu.rendre();
        return { lu: L.B.lecture };
    }""", poser_la_suite=False, suite_panne=1000)
    assert r["lu"] is None, r
