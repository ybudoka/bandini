"""Les enseignes qu'on dévisse la nuit (P4, des choses à collectionner, vague 5) au banc — PAR LE BOUTON : ACTION sous
le néon, la nuit, ouvre le tournevis ; quatre vis d'un tour chacune (HAUT, GAUCHE, BAS, DROITE), à son rythme ; le
mauvais sens ne défait rien ; l'enseigne tombe, une effraction devant témoin ; la façade garde sa potence vide, la
planque son mur, le carnet et le BILAN leur compte.
"""

#: Amener le joueur sous une enseigne, la rue vidée (aucun passant ne vient prendre le bouton ni témoigner), à l'heure
#: voulue. ⚠️ `jour = 21` : une couleur et une heure qui ne bougent pas avec la saison (« un juge de couleur pose sa
#: saison ») ; et le joueur invincible (les hommes de Sal).
AMENER = """
    function amener(L, o, slug, heure) {
        L.Jeu.commencer();
        if (L.B.menu) { L.Hud.fermerMenu && L.Hud.fermerMenu(); L.B.menu = null; }
        L.B.partie.jour = 21;
        L.B.partie.heure = heure === undefined ? 23 / 24 : heure;
        L.B.defs.trafic && (L.B.defs.trafic.vehicules_max = 0);
        L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.personnage; }).forEach(L.Entites.retirer);
        const f = L.Devisser.enseigne(slug);
        const j = L.B.joueur;
        j.invincible = true;
        j.x = L.Devisser.point(f).x; j.y = (f.y + 1) * 16 + 9; j.vx = 0; j.vy = 0;
        L.Entites.indexer();
        L.Monde.centrerCamera(j.x, j.y);
        o.frame(2);
        j.x = L.Devisser.point(f).x; j.y = (f.y + 1) * 16 + 9; j.vx = 0; j.vy = 0;
        return { f: f, j: j };
    }
    //: Un quart de tour : la direction tenue deux images, puis relâchée.
    function quart(o, code) { o.touche(code); o.frame(2); o.relacher(code); o.frame(2); }
    //: Un tour dans le sens contraire des aiguilles : HAUT, GAUCHE, BAS, DROITE (puis HAUT : la lame part d'en haut).
    const TOUR = ['KeyA', 'KeyS', 'KeyD', 'KeyW'];
"""


def test_par_le_bouton_quatre_vis_et_l_enseigne_monte_au_mur(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'rialto');
        const invite = L.B.invite;
        const argent = L.B.partie.argent;
        let vis = 0; const vrai = L.Son.SFX.devisser; L.Son.SFX.devisser = function () { vis++; };
        o.tape('KeyE', 2);
        const ouverte = L.B.epreuve && L.B.epreuve.sorte;
        o.frame(14);                                   // « PRÊT ? »
        quart(o, 'KeyW');                              // la lame dans la vis
        for (let k = 0; k < 4; k++) TOUR.forEach(function (c) { quart(o, c); });
        o.frame(40);
        L.Son.SFX.devisser = vrai;
        const journal = L.B.partie.carnet[L.B.partie.carnet.length - 1];
        return { invite: invite, ouverte: ouverte, fermee: !L.B.epreuve, vis: vis, gain: L.B.partie.argent - argent,
                 prise: L.B.partie.collections.enseignes.rialto || null, msg: L.B.msg, journal: journal && journal.t,
                 cle: L.Devisser.cle(), masque: L.Devisser.masque(),
                 bilan: L.Hud.menuBilan().items.filter(function (i) { return i.libelle === 'ENSEIGNES'; })[0].detail,
                 carnet: L.Hud.menuCarnet().items.filter(function (i) { return i.cle === 'enseignes'; })[0].detail };
    }""")
    assert r["invite"] == "DÉVISSER : LE CINÉMA RIALTO", r["invite"]
    assert r["ouverte"] == "tournevis", "ACTION sous le néon, la nuit, n'ouvre pas le tournevis"
    assert r["vis"] == 4 and r["fermee"], r
    assert r["prise"] and r["prise"]["source"] == "rue", r
    assert r["gain"] == 200, "une enseigne paie 200 $, une fois"
    assert r["msg"].startswith("ENSEIGNE 1/12 — LE CINÉMA RIALTO"), r["msg"]
    assert r["journal"] == "ENSEIGNE : LE CINÉMA RIALTO — AU MUR DE LA PLANQUE", r["journal"]
    assert r["masque"] == 1 << 4, "le Rialto est le cinquième du mur"
    assert r["bilan"] == "1 / 12" and r["carnet"] == "1 / 12"


def test_le_jour_rien_ni_invite_ni_tournevis(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'cantine', 12 / 24);
        const invite = L.B.invite;
        o.tape('KeyE', 2);
        return { invite: invite, epreuve: !!L.B.epreuve, sous: !!L.Devisser.sousLaMain(a.j) };
    }""")
    assert r["invite"] != "DÉVISSER : LA CANTINE" and not r["sous"], r
    assert not r["epreuve"], "le jour, ACTION ouvre le tournevis"


def test_le_mauvais_sens_ne_defait_rien_et_aucun_temps_ne_presse(banc):
    """À son rythme : un quart dans le mauvais sens est DIT, pas puni ; une longue pause ne fait rien rater."""
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'cantine');
        o.tape('KeyE', 2); o.frame(14);
        quart(o, 'KeyW');
        quart(o, 'KeyA'); quart(o, 'KeyS');                 // deux quarts dans le bon sens
        const deux = L.B.epreuve.quarts;
        quart(o, 'KeyA');                                    // un en arrière
        const dit = L.B.epreuve.dit, apres = L.B.epreuve.quarts;
        o.frame(1200);                                       // vingt secondes à réfléchir
        const encore = !!L.B.epreuve && L.B.epreuve.quarts;
        return { deux: deux, dit: dit, apres: apres, encore: encore };
    }""")
    assert r["deux"] == 2
    assert r["dit"] == "DANS L’AUTRE SENS, TU LA REVISSES" and r["apres"] == 2, r
    assert r["encore"] == 2, "le tournevis s'est refermé ou a perdu ses quarts pendant la pause"


def test_esquive_abandonne_et_l_enseigne_reste(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'cantine');
        o.tape('KeyE', 2); o.frame(14);
        quart(o, 'KeyW'); quart(o, 'KeyA');
        o.tape('ShiftLeft', 3);
        return { epreuve: !!L.B.epreuve, prise: !!L.B.partie.collections.enseignes.cantine, msg: L.B.msg };
    }""")
    assert not r["epreuve"] and not r["prise"], r
    assert r["msg"].startswith("L’ENSEIGNE RESTE"), r["msg"]


def test_un_temoin_qui_voit_c_est_une_effraction(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'cantine');
        const appels = [];
        const vrai = L.Police.signalerCrime;
        L.Police.signalerCrime = function (type, x, y, vu) { appels.push({ type: type, vu: vu }); return vrai.apply(this, arguments); };
        const vraiVoit = L.Police.quelqu_un_voit;
        L.Police.quelqu_un_voit = function () { return true; };
        L.Devisser.TOURNEVIS.maj = (function (m) { return function (e, r) { e.vis = r.vis; e.fini = 1; return m(e, r); }; })(L.Devisser.TOURNEVIS.maj);
        o.tape('KeyE', 2); o.frame(20);
        L.Police.signalerCrime = vrai; L.Police.quelqu_un_voit = vraiVoit;
        return { appels: appels, prise: !!L.B.partie.collections.enseignes.cantine };
    }""")
    assert r["prise"], r
    assert r["appels"] == [{"type": "effraction", "vu": True}], r["appels"]


def test_chacune_des_douze_s_atteint_par_le_bouton(banc):
    """Le juge qui a trouvé les tremplins injouables, ici : chaque enseigne de la ville, ACTION sous son néon la nuit
    ouvre SON tournevis — aucune porte, aucun comptoir ni passant ne lui prend le bouton."""
    r = banc("function (L, o) {" + AMENER + """
        const out = {};
        for (const f of L.Devisser.liste()) {
            const a = amener(L, o, f.slug);
            o.tape('KeyE', 2);
            out[f.slug] = L.B.epreuve ? (L.Devisser.chantier && L.Devisser.chantier.f.slug) : (L.B.invite || 'rien');
            if (L.B.epreuve) L.Adresse.fermer();
            L.Devisser.oublier();
        }
        return out;
    }""")
    assert len(r) == 12
    rates = {s: v for s, v in r.items() if v != s}
    assert not rates, f"enseignes qu'ACTION n'atteint pas : {rates}"


def test_la_facade_garde_sa_potence_et_la_planque_son_mur(banc):
    """Dévissée, l'enseigne ne se peint plus sur la façade (la potence vide à la place) ; le mur de la planque la
    porte ; la clé des façades change (les morceaux se recuisent) ; la sauvegarde la garde."""
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'taverne_port');
        const d = (L.Monde.carte.def.devantures || []).find(function (q) { return q.x === a.f.x && q.y === a.f.y; });
        //: Un pinceau qui retient les couleurs posées : le cadre du néon (#8a8c94), le cuivre du fil coupé (#c87a3a).
        function peindre() {
            const vues = [];
            const ctx = { fillStyle: '', fillRect: function () { vues.push(this.fillStyle); } };
            L.Devisser.peindreDrapeau(ctx, a.f, d, 0, 0);
            return vues;
        }
        const avant = peindre();
        const avantCle = L.Devisser.cle();
        L.Devisser.donner('taverne_port', 'rue', true);
        const apres = peindre();
        const neons = [avant.indexOf('#8a8c94') >= 0, apres.indexOf('#8a8c94') >= 0, apres.indexOf('#c87a3a') >= 0];
        const apresCle = L.Devisser.cle();
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(L.B.partie)), L.B.defs);
        const vieille = L.Sauvegarde.completer({ argent: 10, jour: 3, collections: { cartes: {} } }, L.B.defs);
        const abimee = L.Sauvegarde.completer({ argent: 10, collections: { enseignes: ['rialto'] } }, L.B.defs);
        const piece = L.Decoration.presents('planque');
        return { neons: neons, avantCle: avantCle, apresCle: apresCle, piece: piece,
                 relue: relue.collections.enseignes.taverne_port || null, vieille: vieille.collections.enseignes, abimee: abimee.collections.enseignes,
                 rien: L.Devisser.aDevisser().some(function (f) { return f.slug === 'taverne_port'; }) };
    }""")
    assert r["neons"] == [True, False, True], "pendue : le néon ; dévissée : plus de néon, le fil coupé"
    assert r["avantCle"] != r["apresCle"], "la clé des façades ne change pas : la potence vide ne se peindrait jamais"
    assert "mur_enseignes" in r["piece"], "la première enseigne n'accroche pas le mur de la planque"
    assert not r["rien"]
    assert r["relue"] and r["relue"]["source"] == "rue", "la sauvegarde perd l'enseigne"
    assert r["vieille"] == {} and r["abimee"] == {}, "une partie d'avant les enseignes (ou abîmée) n'a pas son mur vide"


def test_les_paliers_paient_et_jouent_le_reel(banc):
    r = banc("function (L, o) {" + AMENER + """
        L.Jeu.commencer();
        const tous = L.Devisser.liste().map(function (f) { return f.slug; });
        tous.slice(0, 5).forEach(function (s) { L.Devisser.donner(s, 'debug', true); });
        let reel = 0; const vrai = L.Son.SFX.reel_bebelles; L.Son.SFX.reel_bebelles = function () { reel++; };
        const argent = L.B.partie.argent;
        L.Devisser.donner(tous[5], 'rue');
        const six = L.B.partie.argent - argent;
        tous.slice(6, 11).forEach(function (s) { L.Devisser.donner(s, 'debug', true); });
        const avant = L.B.partie.argent;
        L.Devisser.donner(tous[11], 'rue');
        L.Son.SFX.reel_bebelles = vrai;
        return { six: six, douze: L.B.partie.argent - avant, reel: reel, n: L.Devisser.nombre(), masque: L.Devisser.masque() };
    }""")
    assert r["six"] == 200 + 1000 and r["douze"] == 200 + 3000 and r["reel"] == 2, r
    assert r["n"] == 12 and r["masque"] == 4095


def test_les_triches_y_menent_la_nuit(banc):
    r = banc("function (L, o) {" + AMENER + """
        L.Jeu.commencer();
        if (L.B.menu) { L.Hud.fermerMenu && L.Hud.fermerMenu(); L.B.menu = null; }
        L.B.partie.jour = 21; L.B.partie.heure = 12 / 24;
        const menu = L.Hud.menuDebugCollections();
        const item = menu.items.filter(function (i) { return i.enseigne === 'souvenirs'; })[0];
        item.faire(item);
        o.frame(2);
        const sous = L.Devisser.sousLaMain(L.B.joueur);
        const n = L.Devisser.toutes();
        return { sous: sous && sous.slug, nuit: L.Monde.estNuit(), n: n, nombre: L.Devisser.nombre() };
    }""")
    assert r["nuit"] and r["sous"] == "souvenirs", r
    assert r["n"] == 12 and r["nombre"] == 12


def test_le_neon_luit_la_nuit_et_s_eteint_devisse(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'dragon_or');
        const cam = { x: a.j.x - 200, y: a.j.y - 150 };
        function la() { return L.Devisser.lampes(cam).length; }
        // Le grésillement : une image sur 84 environ s'éteint — on en prend une où il luit.
        L.B.t = 1000;
        const nuit = la();
        L.B.partie.heure = 12 / 24;
        const jour = la();
        L.B.partie.heure = 23 / 24;
        L.Devisser.donner('dragon_or', 'debug', true);
        const devisse = la();
        return { nuit: nuit, jour: jour, devisse: devisse };
    }""")
    assert r["nuit"] >= 1 and r["jour"] == 0, r
    assert r["devisse"] == r["nuit"] - 1, r


def test_la_ville_recuit_ses_facades_quand_une_enseigne_tombe(banc):
    """Les façades sont cuites une fois dans des morceaux : sans recuisson, la potence vide ne se verrait jamais."""
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L, o, 'clairon');
        L.Jeu.rendre(); o.frame(1);
        const morceaux = L.Monde.carte.morceaux;
        const cle = Math.floor(a.f.x / 16) + ',' + Math.floor((a.f.y + 1) / 16);
        const avant = morceaux.get(cle);
        L.Devisser.donner('clairon', 'debug', true);
        L.Jeu.rendre();
        const apres = L.Monde.carte.morceaux.get(cle);
        return { avant: !!avant, recuit: !!apres && apres !== avant, cle: L.Monde.carte.enseignes === L.Devisser.cle() };
    }""")
    assert r["avant"] and r["recuit"] and r["cle"], r


def test_le_mur_de_la_planque_porte_ce_qu_on_a_devisse(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = L.Decoration.DESSINS.mur_enseignes;
        function neons(v) {
            const vues = [];
            const ctx = { fillStyle: '', fillRect: function () { vues.push(this.fillStyle); } };
            d.peindre(ctx, d.w, d.h, v);
            return vues.filter(function (c) { return c === '#8a8c94'; }).length;
        }
        L.Devisser.donner('bingo', 'debug', true); L.Devisser.donner('ti_pout', 'debug', true);
        return { vide: neons(0), deux: neons(L.Devisser.masque()), plein: neons(4095), masque: L.Devisser.masque(),
                 solide: d.solide, variantes: d.variantes };
    }""")
    assert r["vide"] == 0 and r["deux"] == 2 and r["plein"] == 12, r
    assert r["masque"] == (1 << 0) | (1 << 11)
    assert r["solide"] and r["variantes"] == 4096
