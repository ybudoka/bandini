"""Des garages où l'on entre : semer la police et repeindre (21 sept. 2026) — au banc.

Demande de Martin : « il faut des portes de garage qu'on peut vraiment entrer. pour
permettre de semer la police en voiture. », puis « repeindre des voitures ».

La ville (les carrosseries, la baie sous le toit, l'abord) se juge dans
`test_garages_ou_l_on_entre.py`. Ici, ce qui vit — au BOUTON, parce que c'est le
gaz qui fait passer le seuil : le rideau qui monte pour le char admis et pour lui
seul, le char qui disparait sous le toit, le rideau qui retombe, le pistolet, la
police remise a zero, et la marche arriere pour ressortir.
"""

import pytest

#: Arriver droit sur un rideau, au volant, pour de vrai : un char nez au nord a
#: quatre tuiles de la facade, la rue videe autour (le trafic et les passants du
#: hasard ne sont pas ce qu'on juge), gaz jusqu'a ce que l'atelier le prenne — ou
#: jusqu'a ce qu'il bute. On garde la trace de chaque image.
ENTRER = """
    function preparer(L, lieu, slug, options) {
        const j = L.B.joueur, TT = L.TT;
        const pg = L.Monde.porteDeGarage(lieu), baie = L.Monde.baieDeLaPorteDeGarage(pg);
        j.x = baie.x; j.y = baie.y + 3 * TT; L.Monde.centrerCamera(j.x, j.y);
        L.B.entites.filter(function (e) { return (e.type === 'vehicule' || e.type === 'pieton') && e !== j
            && Math.hypot(e.x - baie.x, e.y - baie.y) < 300; }).forEach(function (e) { L.Entites.retirer(e); });
        L.B.defs.conduite.trafic.vehicules_max = 0;
        const v = L.Vehicules.creer(slug || 'auto', baie.x, baie.y + 3 * TT, -Math.PI / 2,
                                    Object.assign({ etat: 'stationne', couleur: '#c0392b' }, options || {}));
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
        v.vole = true;
        return { v: v, pg: pg, baie: baie };
    }
    function entrer(L, o, a, images) {
        const v = a.v, pg = a.pg, TT = L.TT, trace = [];
        for (let k = 0; k < (images || 240) && !v.atelier; k++) {
            if (Math.abs(v.vitesse) > 1.4) o.relacher('KeyW'); else o.touche('KeyW');
            o.frame(1);
            trace.push({ y: (v.y - (pg.y + 1) * TT) / TT, ouverture: pg.ouverture, atelier: !!v.atelier });
        }
        o.relacher('KeyW');
        return trace;
    }
"""


def _jouer(banc, corps):
    return banc("function (L, o) {\n%s\nL.Jeu.commencer();\n%s\n}" % (ENTRER, corps))


def test_a_la_carrosserie_on_entre_le_rideau_tombe_et_le_char_ressort_repeint(banc, paquet):
    """Le coeur de la demande : trois etoiles au dos, on entre au gaz. Le rideau est
    leve avant que le nez touche la facade ; le char passe TOUT ENTIER sous le linteau ;
    le rideau retombe, le volant ne repond plus (le gaz tenu ne le bouge pas) ; il
    ressort d'une autre couleur, le vol efface, la police a zero, la peinture payee
    avec son supplement par etoile ; et on ressort en reculant."""
    eco = paquet["economie"]["carrosserie"]
    r = _jouer(banc, """
        const a = preparer(L, 'carrosserie_faubourg');
        const TT = L.TT, v = a.v, pg = a.pg;
        L.B.partie.argent = 1000;
        L.B.recherche.etoiles = 3; L.B.recherche.chaleur = 40;
        const trace = entrer(L, o, a);
        const pris = { atelier: !!v.atelier, arriere: (v.y - (pg.y + 1) * TT) / TT };
        // Le gaz tenu pendant l'atelier : le char ne bouge pas d'un pixel.
        const y0 = v.y;
        o.touche('KeyW');
        let fermeCache = false, bouge = 0, images = 0, repeintRideau = null;
        while (v.atelier && images < 400) {
            const avant = pg.ouverture;             // le rideau AU MOMENT du pistolet
            o.frame(1); images++;
            if (pg.ouverture === 0) fermeCache = true;
            if (repeintRideau === null && v.couleur !== '#c0392b') repeintRideau = avant;
            bouge = Math.max(bouge, Math.abs(v.y - y0));
        }
        o.relacher('KeyW');
        const apres = { couleur: v.couleur, vole: v.vole, etoiles: L.B.recherche.etoiles, chaleur: L.B.recherche.chaleur,
                        argent: L.B.partie.argent, ouverture: pg.ouverture, phase: pg.phase, msg: L.B.msg };
        // On recule jusqu'a la baie : l'atelier se referme derriere.
        o.touche('KeyS');
        for (let k = 0; k < 240 && v.y < a.baie.y + 2 * TT; k++) o.frame(1);
        o.relacher('KeyS');
        o.touche('ShiftLeft');
        for (let k = 0; k < 90 && Math.abs(v.vitesse) > 0.05; k++) o.frame(1);
        o.relacher('ShiftLeft');
        o.frame(2);
        return { avant: trace[0], leve: trace.find(function (p) { return p.ouverture === 1; }), trace: trace,
                 pris: pris, fermeCache: fermeCache, repeintRideau: repeintRideau, bouge: bouge, images: images, apres: apres,
                 sorti: { y: (v.y - (pg.y + 1) * TT) / TT, dedans: !!pg.dedans, auVolant: L.B.joueur.dansVehicule === v } };
    """)
    assert r["leve"], "le rideau ne s'est jamais leve"
    assert r["leve"]["y"] > 0.5, f"le rideau se leve trop tard, nez sur la facade ({r['leve']['y']:.2f} tuile)"
    assert r["pris"]["atelier"], f"le char n'est jamais passe sous le linteau : {r['trace'][-5:]}"
    assert r["pris"]["arriere"] <= 0, f"l'atelier a pris un char qui depasse encore ({r['pris']['arriere']:.2f})"
    assert r["fermeCache"], "le rideau n'est jamais retombe sur le char"
    assert r["repeintRideau"] == 0, f"repeint rideau ouvert a {r['repeintRideau']} : toute la rue a vu le pistolet"
    assert r["bouge"] == 0, f"le gaz a deplace le char de {r['bouge']:.2f} px pendant l'atelier"
    duree = round(eco["atelier_s"] * 60)
    assert r["images"] >= duree, f"l'atelier a dure {r['images']} images, le pistolet en demande {duree}"
    apres = r["apres"]
    assert apres["couleur"] != "#c0392b", "le char ressort de la meme couleur"
    assert apres["vole"] is False, "la peinture n'efface pas le vol"
    assert apres["etoiles"] == 0 and apres["chaleur"] == 0, apres
    assert apres["argent"] == 1000 - (eco["prix"] + 3 * eco["par_etoile"]), apres
    assert "PEINTURE" in apres["msg"], apres["msg"]
    assert apres["ouverture"] == 1 and apres["phase"] == "sortie", apres
    assert r["sorti"]["y"] > 0 and not r["sorti"]["dedans"] and r["sorti"]["auVolant"], r["sorti"]


def test_sans_l_argent_le_rideau_reste_baisse_et_le_char_bute(banc):
    r = _jouer(banc, """
        const a = preparer(L, 'carrosserie_faubourg');
        const TT = L.TT;
        L.B.partie.argent = 0;
        L.B.recherche.etoiles = 1;
        const trace = entrer(L, o, a, 200);
        return { ouverture: Math.max.apply(null, trace.map(function (p) { return p.ouverture; })),
                 plusLoin: Math.min.apply(null, trace.map(function (p) { return p.y; })) * TT,
                 atelier: !!a.v.atelier, msg: L.B.msg, etoiles: L.B.recherche.etoiles, admis: a.pg.admis === a.v };
    """)
    assert r["ouverture"] == 0, "le rideau s'est leve pour quelqu'un qui n'a pas de quoi payer"
    assert not r["atelier"] and not r["admis"], r
    assert r["plusLoin"] >= -1, f"le char est entre de {-r['plusLoin']:.1f} px dans un rideau baisse"
    assert "PAS" in r["msg"] and "$" in r["msg"], r["msg"]
    assert r["etoiles"] == 1


def test_une_auto_patrouille_ne_se_repeint_pas(banc):
    r = _jouer(banc, """
        const a = preparer(L, 'carrosserie_faubourg', 'police');
        L.B.partie.argent = 5000;
        const trace = entrer(L, o, a, 200);
        return { ouverture: Math.max.apply(null, trace.map(function (p) { return p.ouverture; })), atelier: !!a.v.atelier, msg: L.B.msg };
    """)
    assert r["ouverture"] == 0 and not r["atelier"], r
    assert "POLICE" in r["msg"], r["msg"]


def test_le_seuil_ne_s_ouvre_que_pour_le_char_admis(banc):
    """⚠️ La tuile qui s'ouvre pour UN SEUL char. Rideau leve pour le joueur, la meme
    place dans le passage reste un mur pour l'auto-patrouille qui le suit ; et pour le
    joueur aussi, une fois reparti."""
    r = _jouer(banc, """
        const a = preparer(L, 'carrosserie_faubourg');
        const TT = L.TT, v = a.v, pg = a.pg;
        L.B.partie.argent = 1000;
        const x = (pg.x + 1) * TT, y = (pg.y - 0.2) * TT;
        // Pendant qu'il monte, le rideau est encore un mur — meme pour le char admis.
        let aMiCourse = null;
        for (let k = 0; k < 40; k++) {
            o.touche('KeyW'); if (Math.abs(v.vitesse) > 0.6) o.relacher('KeyW'); o.frame(1);
            if (aMiCourse === null && pg.ouverture > 0.2 && pg.ouverture < 0.8) aMiCourse = L.Vehicules.bloqueParLesTuiles(v, x, y, -Math.PI / 2);
        }
        o.relacher('KeyW');
        const flic = L.Vehicules.creer('police', x + 60, a.baie.y + 5 * TT, -Math.PI / 2, { conducteur: 'police', etat: 'roule' });
        const ouvert = { ouverture: pg.ouverture, admis: pg.admis === v,
                         joueur: L.Vehicules.bloqueParLesTuiles(v, x, y, -Math.PI / 2),
                         flic: L.Vehicules.bloqueParLesTuiles(flic, x, y, -Math.PI / 2) };
        // Le joueur repart loin : le seuil se referme pour lui aussi.
        v.x = a.baie.x; v.y = a.baie.y + 9 * TT; L.B.joueur.x = v.x; L.B.joueur.y = v.y;
        o.frame(80);
        return { aMiCourse: aMiCourse, ouvert: ouvert, apres: { ouverture: pg.ouverture, admis: pg.admis, joueur: L.Vehicules.bloqueParLesTuiles(v, x, y, -Math.PI / 2) } };
    """)
    assert r["aMiCourse"] is True, "le char admis passe sous un rideau a mi-course"
    assert r["ouvert"]["ouverture"] == 1 and r["ouvert"]["admis"], r["ouvert"]
    assert r["ouvert"]["joueur"] is False, "le rideau leve, le char admis bute encore sur le seuil"
    assert r["ouvert"]["flic"] is True, "l'auto-patrouille passe le seuil derriere le joueur"
    assert r["apres"]["ouverture"] == 0 and r["apres"]["admis"] is None, r["apres"]
    assert r["apres"]["joueur"] is True, "le seuil reste ouvert au joueur reparti"


def test_une_poursuite_s_arrete_devant_le_rideau(banc):
    """Quatre etoiles, une auto-patrouille aux trousses : on entre, elle reste dehors
    (jamais dans le passage), et le joueur n'est jamais sorti du char a travers le
    rideau ; a la fin, la police a lache."""
    r = _jouer(banc, """
        const a = preparer(L, 'carrosserie_faubourg');
        const TT = L.TT, v = a.v, pg = a.pg;
        L.B.partie.argent = 1000;
        L.B.recherche.etoiles = 4;
        const flic = L.Vehicules.creer('police', a.baie.x + 20, a.baie.y + 6 * TT, -Math.PI / 2, { conducteur: 'police', etat: 'roule' });
        L.Entites.indexer();
        entrer(L, o, a);
        // L'agent arrive a pied quand le rideau tombe : colle au seuil, a portee de main
        // d'un char arrete — dans la rue, il l'en sortirait.
        const agent = L.Police.creerAgent(v.x + 2, (pg.y + 1) * TT + 5, 'poursuit');
        L.Entites.indexer();
        let dansLePassage = 0, sorti = 0, images = 0, aPortee = 0;
        while ((v.atelier || pg.phase !== 'sortie') && images < 400) {
            o.frame(1); images++;
            if (L.Monde.dansLePassage(pg, flic.x, flic.y)) dansLePassage++;
            if (L.B.joueur.dansVehicule !== v) sorti++;
            if (agent.vivant && agent.etat === 'poursuit' && L.B.recherche.etoiles > 0 && Math.hypot(agent.x - v.x, agent.y - v.y) < 30) aPortee++;
        }
        return { entre: images > 0, dansLePassage: dansLePassage, sorti: sorti, aPortee: aPortee, etoiles: L.B.recherche.etoiles };
    """)
    assert r["entre"], "le char n'est jamais entre"
    assert r["aPortee"] > 30, f"l'agent n'a ete a portee de main que {r['aPortee']} images : le juge ne mesure rien"
    assert r["dansLePassage"] == 0, "l'auto-patrouille est entree sous le toit"
    assert r["sorti"] == 0, "un agent a sorti le joueur du char a travers le rideau"
    assert r["etoiles"] == 0


def test_chez_ti_guy_on_entre_et_son_menu_s_ouvre_rideau_baisse(banc):
    """Chez Ti-Guy, entrer ouvre SON menu, a l'abri : rideau baisse, char sous le toit.
    REPARTIR (en tete) le releve ; on recule par la baie sans que le menu de devant nous
    rattrape."""
    r = _jouer(banc, """
        const a = preparer(L, 'garage');
        const TT = L.TT, v = a.v, pg = a.pg;
        entrer(L, o, a);
        let images = 0;
        while (!L.B.menu && images < 200) { o.frame(1); images++; }
        const menu = L.B.menu && { titre: L.B.menu.titre, premier: L.B.menu.items[0].libelle, ouverture: pg.ouverture,
                                   sousLeToit: v.y + 14 <= (pg.y + 1) * TT };
        o.tape('KeyE', 2);
        for (let k = 0; k < 60 && (pg.ouverture < 1 || v.atelier); k++) o.frame(1);
        const leve = { menu: !!L.B.menu, ouverture: pg.ouverture, atelier: !!v.atelier };
        // On recule, et on s'arrete DANS la baie, la ou le menu de devant s'ouvrirait.
        o.touche('KeyS');
        let rattrape = false;
        for (let k = 0; k < 300 && v.y < (pg.y + 1.5) * TT; k++) {
            if (Math.abs(v.vitesse) > 0.5) o.relacher('KeyS'); else o.touche('KeyS');
            o.frame(1); if (L.B.menu) rattrape = true;
        }
        o.relacher('KeyS');
        o.touche('ShiftLeft');
        for (let k = 0; k < 90 && Math.abs(v.vitesse) > 0.05; k++) { o.frame(1); if (L.B.menu) rattrape = true; }
        o.relacher('ShiftLeft');
        const dansLaBaie = L.Monde.devantLaPorteDeGarage(pg, v.x, v.y, 2, 0);
        for (let k = 0; k < 40; k++) { o.frame(1); if (L.B.menu) rattrape = true; }
        return { menu: menu, leve: leve, rattrape: rattrape, dansLaBaie: dansLaBaie, auVolant: L.B.joueur.dansVehicule === v };
    """)
    assert r["menu"], "entre chez Ti-Guy, son menu ne s'ouvre pas"
    assert r["menu"]["titre"] == "GARAGE ROCCO BANDINI" and r["menu"]["premier"] == "REPARTIR", r["menu"]
    assert r["menu"]["ouverture"] == 0 and r["menu"]["sousLeToit"], r["menu"]
    assert r["leve"] == {"menu": False, "ouverture": 1, "atelier": False}, r["leve"]
    assert r["dansLaBaie"], "le juge devait s'arreter dans la baie"
    assert r["rattrape"] is False, "le menu de devant nous rattrape en reculant"
    assert r["auVolant"]


def test_sous_le_toit_on_ne_descend_pas_et_vendu_on_ressort_dans_la_baie(banc):
    """Les portieres donnent sur des murs : ACTION ne fait pas descendre sous le toit.
    Et vendu du volant chez Ti-Guy, on ressort a pied par-dessous le rideau, sur une
    tuile ou l'on marche."""
    r = _jouer(banc, """
        const a = preparer(L, 'garage');
        const TT = L.TT, v = a.v, pg = a.pg;
        entrer(L, o, a);
        for (let k = 0; k < 200 && !L.B.menu; k++) o.frame(1);
        o.tape('KeyE', 2);                       // REPARTIR
        for (let k = 0; k < 60 && v.atelier; k++) o.frame(1);
        o.tape('KeyE', 2);                       // descendre ? sous le toit : non
        const reste = { auVolant: L.B.joueur.dansVehicule === v, msg: L.B.msg };
        // On rentre de nouveau, et cette fois on VEND.
        o.touche('KeyS'); for (let k = 0; k < 200 && v.y < a.baie.y + 3 * TT; k++) o.frame(1); o.relacher('KeyS');
        o.touche('ShiftLeft'); for (let k = 0; k < 90 && Math.abs(v.vitesse) > 0.05; k++) o.frame(1); o.relacher('ShiftLeft');
        o.frame(2);
        entrer(L, o, a);
        for (let k = 0; k < 200 && !L.B.menu; k++) o.frame(1);
        const ligne = L.B.menu && (o.tape('ArrowDown', 2), L.B.menu.items[L.B.menu.curseur].libelle);
        o.tape('KeyE', 1);
        const j = L.B.joueur;
        const pose = { dx: Math.abs(j.x - a.baie.x), dy: Math.abs(j.y - a.baie.y) };
        o.frame(3);
        return { reste: reste, ligne: ligne, pose: pose, vendu: L.B.entites.indexOf(v) < 0, aPied: !j.dansVehicule,
                 marchable: !L.Monde.bloque(Math.floor(j.x / TT), Math.floor(j.y / TT), L.Monde.MASQUE_PIETON),
                 devant: j.y >= (pg.y + 1) * TT, atelier: !!pg.dedans };
    """)
    assert r["reste"]["auVolant"], "descendu sous le toit : le joueur est dans le mur"
    assert "RECULE" in r["reste"]["msg"], r["reste"]["msg"]
    assert r["ligne"] and r["ligne"].startswith("VENDRE"), r["ligne"]
    assert r["vendu"] and r["aPied"], r
    assert r["marchable"] and r["devant"], "vendu sous le toit, le joueur ressort dans un mur"
    assert r["pose"]["dx"] < 2 and r["pose"]["dy"] < 2, f"vendu, le joueur ne ressort pas dans la baie : {r['pose']}"
    assert r["atelier"] is False, "l'atelier attend un char vendu"


@pytest.mark.parametrize("lieu, passe", [("garage", False), ("carrosserie_faubourg", True)])
def test_le_char_d_une_mission(banc, lieu, passe):
    """Chez Ti-Guy, le char d'une mission se LIVRE devant le rideau : le rideau se leve
    pour lui, mais il ne passe pas. A la carrosserie, il passe — semer la police en
    pleine mission, c'est tout l'interet."""
    r = _jouer(banc, """
        const a = preparer(L, '%s', 'auto', { mission: 'm1' });
        a.v.mission = 'm1';
        L.B.partie.argent = 1000;
        const trace = entrer(L, o, a, 200);
        return { ouverture: Math.max.apply(null, trace.map(function (p) { return p.ouverture; })), atelier: !!a.v.atelier };
    """ % lieu)
    assert r["ouverture"] == 1, "le rideau reste baisse devant le char d'une mission"
    assert r["atelier"] is passe, r


def test_sous_le_linteau_le_char_se_peint_coupe_au_bas_du_rideau(banc):
    """Le canevas du banc ne garde aucun pixel : on juge la DECOUPE. Un char dans le
    passage se peint sous un masque qui retire, dans les colonnes du rideau, tout ce qui
    est au-dessus de son bas (le linteau, rideau leve ; les lames, a mi-course). Un
    char de la rue, loin des rideaux, se peint sans masque."""
    r = _jouer(banc, """
        const a = preparer(L, 'carrosserie_faubourg');
        const TT = L.TT, v = a.v, pg = a.pg;
        L.B.partie.argent = 1000;
        entrer(L, o, a);
        o.frame(12);                                 // le rideau a mi-course, qui retombe
        const cam = L.B.cam, ctx = L.Base.debut();
        const journal = [];
        const rect = ctx.rect, clip = ctx.clip, dessinerUn = L.Vehicules.dessinerUn;
        ctx.rect = function (x, y, w, h) { journal.push(['rect', Math.round(x), Math.round(y), Math.round(w), Math.round(h)]); };
        ctx.clip = function (regle) { journal.push(['clip', regle]); };
        L.Vehicules.dessinerUn = function (c, e) { if (e.type === 'vehicule') journal.push(['char', e === v]); return dessinerUn.apply(null, arguments); };
        L.Entites.dessiner(ctx, cam);
        const pourLui = journal.slice();
        journal.length = 0;
        const loin = L.Vehicules.creer('auto', a.baie.x + 7 * TT, a.baie.y + 3 * TT, 0, { etat: 'stationne' });
        L.Entites.indexer();
        L.Entites.retirer(v);
        L.Entites.dessiner(ctx, cam);
        ctx.rect = rect; ctx.clip = clip; L.Vehicules.dessinerUn = dessinerUn;
        const cx = Math.round(cam.x), cy = Math.round(cam.y);
        return { pourLui: pourLui, pourLoin: journal.slice(), ouverture: pg.ouverture,
                 // Le bas des lames : 3 px sous le haut de la rangee du rideau, plus ce qui
                 // en est descendu (12 px de course, `dessinerPortesDeGarage`).
                 attendu: [pg.x * TT - cx, (pg.y - pg.baie) * TT - cy, pg.l * TT,
                           pg.y * TT + 3 + Math.round(12 * (1 - pg.ouverture)) - (pg.y - pg.baie) * TT] };
    """)
    assert 0 < r["ouverture"] < 1, f"le juge voulait un rideau a mi-course ({r['ouverture']})"
    lui = r["pourLui"]
    i = lui.index(["char", True])
    assert lui[i - 1] == ["clip", "evenodd"], lui
    rects = [e[1:] for e in lui[:i] if e[0] == "rect"][-2:]
    assert rects[-1] == [round(n) for n in r["attendu"]], (rects, r["attendu"])
    assert ["clip", "evenodd"] not in r["pourLoin"], "un char loin des rideaux se peint sous un masque"
