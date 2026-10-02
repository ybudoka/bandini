"""Le lave-auto qu'on traverse, JOUÉ (docs/jalons/le-lave-auto-qu-on-traverse.md) : on arrive au pas devant la porte
vitrée, elle monte, on paie au seuil et le convoyeur tire le char jusqu'à la ruelle sans qu'on touche au volant ; une
étoile tombe. Sans argent, rien ne s'ouvre ; de la ruelle non plus ; un autre char bute ; on ne descend pas sur le rail ;
le char détruit lève les deux portes ; un menu fige le rail."""

from app import enseignes

OUTILS = """
  const TT = 16;
  function prep(L, argent) {
    L.Jeu.commencer(); while (L.B.menu) L.Hud.fermerMenu();
    const B = L.B, j = B.joueur, t = B.defs.enseignes.lave_auto;
    B.partie.jour = 22; B.partie.heure = 13 / 24;
    j.intouchable = true;
    B.defs.conduite.trafic.vehicules_max = 0;
    const cx = (t.x + t.l / 2) * TT;
    for (const e of B.entites.slice()) if ((e.type === 'vehicule' || e.type === 'pieton') && e !== j
        && Math.hypot(e.x - cx, e.y - t.entree * TT) < 300) L.Entites.retirer(e);
    const v = L.Vehicules.creer('auto', cx, (t.entree + 3) * TT, -Math.PI / 2, { etat: 'stationne', couleur: '#c0392b' });
    j.x = v.x; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Monde.centrerCamera(j.x, j.y);
    B.partie.argent = argent === undefined ? 100 : argent;
    return { B: B, j: j, t: t, v: v };
  }
  // Au pas vers la porte : un coup de gaz quand le char ralentit, jamais plus vite que le pas.
  function auPas(L, o, v, n, jusqua) {
    for (let k = 0; k < n; k++) {
      if (jusqua && jusqua()) break;
      if (v.vitesse < 0.6) o.touche('KeyW'); else o.relacher('KeyW');
      L.B.recherche.vu = 0;
      o.frame(1);
    }
    o.relacher('KeyW');
  }
"""


def test_on_traverse_de_la_rue_a_la_ruelle_sans_toucher_au_volant(banc):
    rl = enseignes.REGLES["lave_auto"]
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L), B = s.B, t = s.t, v = s.v, E = L.Enseignes;
        B.recherche.etoiles = 2; B.recherche.chaleur = 10;
        const sons = []; ['jet_lavage', 'brosses', 'sechoir'].forEach(function (n) {
            const f = L.Son.SFX[n]; L.Son.SFX[n] = function () { sons.push(n); return f.apply(this, arguments); }; });
        auPas(L, o, v, 400, function () { return E.lavage && E.lavage.phase === 'rail'; });
        const surLeRail = !!(E.lavage && E.lavage.phase === 'rail');
        // Sur le rail : le gaz et le volant ne font rien.
        let images = 0, centre = true;
        o.touche('KeyA'); o.touche('KeyS');
        for (; images < 800 && E.lavage; images++) {
            o.frame(1); B.recherche.vu = 0;
            if (E.lavage && Math.abs(v.x - (t.x + t.l / 2) * TT) > 0.5) centre = false;
        }
        o.relacher('KeyA'); o.relacher('KeyS');
        return { surLeRail: surLeRail, images: images, centre: centre, fini: !E.lavage,
                 derriere: v.y + v.def.longueur / 2 < t.sortie * TT, argent: B.partie.argent, etoiles: B.recherche.etoiles,
                 auVolant: s.j.dansVehicule === v, luisant: v.luisant > B.t, sons: sons };
    }""")
    assert r["surLeRail"] and r["fini"] and r["centre"] and r["auVolant"], r
    assert r["images"] <= rl["duree_s"] * 60 + 30, f"le convoyeur s'éternise : {r}"
    assert r["derriere"], f"le char n'est pas ressorti côté ruelle : {r}"
    assert r["argent"] == 100 - rl["prix"] and r["etoiles"] == 1 and r["luisant"], r
    assert r["sons"] == ["jet_lavage", "brosses", "jet_lavage", "sechoir"], r


def test_sans_argent_la_porte_reste_baissee(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L, 5), t = s.t, v = s.v, E = L.Enseignes;
        let messages = []; const m = L.Hud.message; L.Hud.message = function (x) { messages.push(x); return m.apply(this, arguments); };
        auPas(L, o, v, 300);
        return { lavage: !!E.lavage, porte: E.portesDuLavage.e, dehors: v.y > t.entree * TT, argent: L.B.partie.argent,
                 dit: messages.filter(function (x) { return x.indexOf('PAS ASSEZ') >= 0; }).length };
    }""")
    assert r == {"lavage": False, "porte": 0, "dehors": True, "argent": 5, "dit": 1}, r


def test_de_la_ruelle_rien_ne_s_ouvre(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L), t = s.t, v = s.v, E = L.Enseignes;
        v.x = (t.x + t.l / 2) * TT; v.y = (t.sortie - 2) * TT; v.angle = Math.PI / 2; L.B.joueur.x = v.x; L.B.joueur.y = v.y;
        auPas(L, o, v, 300);
        return { lavage: !!E.lavage, dehors: v.y < t.sortie * TT, argent: L.B.partie.argent };
    }""")
    assert r == {"lavage": False, "dehors": True, "argent": 100}, r


def test_un_autre_char_bute_sur_le_tunnel_pendant_le_lavage(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L), t = s.t, v = s.v, E = L.Enseignes;
        auPas(L, o, v, 400, function () { return E.lavage && E.lavage.phase === 'rail'; });
        // Une patrouille pousse derrière lui, dans l'axe : le tunnel est un mur pour elle.
        const p = L.Vehicules.creer('police', (t.x + t.l / 2) * TT, (t.entree + 3) * TT, -Math.PI / 2, { etat: 'stationne' });
        L.Entites.indexer();
        let plusHaut = p.y;
        for (let k = 0; k < 150; k++) { p.angle = -Math.PI / 2; p.vitesse = 1.5; o.frame(1); plusHaut = Math.min(plusHaut, p.y); }
        const tx = t.x, ty = t.entree - 1;
        return { rail: !!E.lavage, bute: plusHaut > (t.entree + 1) * TT - 2, ouvertAuLavage: E.tunnelOuvert(v, tx, ty),
                 ouvertALaPatrouille: E.tunnelOuvert(p, tx, ty) };
    }""")
    assert r["bute"] and not r["ouvertALaPatrouille"], r
    assert r["ouvertAuLavage"] or not r["rail"], r


def test_on_ne_descend_pas_sur_le_rail(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L), v = s.v, E = L.Enseignes;
        auPas(L, o, v, 400, function () { return E.lavage && E.lavage.phase === 'rail'; });
        let messages = []; const m = L.Hud.message; L.Hud.message = function (x) { messages.push(x); return m.apply(this, arguments); };
        o.tape('KeyE', 3);
        return { auVolant: s.j.dansVehicule === v, dit: messages.indexOf('PAS PENDANT LE LAVAGE') >= 0 };
    }""")
    assert r == {"auVolant": True, "dit": True}, r


def test_le_char_detruit_dans_le_tunnel_leve_les_deux_portes(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L), v = s.v, E = L.Enseignes;
        auPas(L, o, v, 400, function () { return E.lavage && E.lavage.phase === 'rail'; });
        for (let k = 0; k < 60; k++) o.frame(1);
        v.etat = 'epave';
        for (let k = 0; k < 40; k++) o.frame(1);
        return { phase: E.lavage && E.lavage.phase, e: E.portesDuLavage.e, s: E.portesDuLavage.s };
    }""")
    assert r == {"phase": "panne", "e": 1, "s": 1}, r


def test_un_menu_fige_le_rail(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L), v = s.v, E = L.Enseignes;
        auPas(L, o, v, 400, function () { return E.lavage && E.lavage.phase === 'rail'; });
        for (let k = 0; k < 30; k++) o.frame(1);
        const avant = v.y;
        L.Hud.ouvrirOnglet('carnet');
        for (let k = 0; k < 60; k++) o.frame(1);
        const pendant = v.y;
        while (L.B.menu) L.Hud.fermerMenu();
        if (L.B.etat === 'pause') L.Jeu.reprendre();
        for (let k = 0; k < 30; k++) o.frame(1);
        return { fige: pendant === avant, reprend: v.y < pendant, rail: !!E.lavage };
    }""")
    assert r == {"fige": True, "reprend": True, "rail": True}, r


def test_le_tunnel_se_peint_par_dessus_les_gens(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L), v = s.v, E = L.Enseignes;
        auPas(L, o, v, 400, function () { return E.lavage && E.lavage.phase === 'rail'; });
        const ordre = []; const d = L.Entites.dessiner, t = E.dessinerTunnel;
        L.Entites.dessiner = function () { ordre.push('gens'); return d.apply(this, arguments); };
        E.dessinerTunnel = function () { ordre.push('tunnel'); return t.apply(this, arguments); };
        L.Jeu.rendre();
        L.Entites.dessiner = d; E.dessinerTunnel = t;
        return ordre;
    }""")
    assert r == ["gens", "tunnel"], r


def test_on_ne_passe_qu_une_fois_la_porte_levee(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L), t = s.t, v = s.v, E = L.Enseignes;
        auPas(L, o, v, 300, function () { return !!E.lavage; });
        const baissee = { e: E.portesDuLavage.e, ouvert: E.tunnelOuvert(v, t.x, t.entree) };
        for (let k = 0; k < 40; k++) { v.vitesse = 0; o.frame(1); }
        return { phase: E.lavage && E.lavage.phase, baissee: baissee, levee: { e: E.portesDuLavage.e, ouvert: E.tunnelOuvert(v, t.x, t.entree) } };
    }""")
    assert r["phase"] == "devant" and r["baissee"]["e"] < 1 and r["baissee"]["ouvert"] is False, r
    assert r["levee"] == {"e": 1, "ouvert": True}, r


def test_en_reculant_vers_la_porte_rien_ne_s_ouvre(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const s = prep(L), t = s.t, v = s.v, E = L.Enseignes;
        v.angle = Math.PI / 2;                                  // le nez vers la rue, l'arrière vers la porte
        for (let k = 0; k < 200; k++) { if (v.vitesse > -0.6) o.touche('KeyS'); else o.relacher('KeyS'); o.frame(1); }
        o.relacher('KeyS');
        return { lavage: !!E.lavage, dehors: v.y > t.entree * TT };
    }""")
    assert r == {"lavage": False, "dehors": True}, r
