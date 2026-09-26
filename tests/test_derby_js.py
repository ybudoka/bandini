"""Le derby de démolition, au banc (docs/jalons/le-derby-de-demolition-a-la-foire.md).

Le soir seulement ; le Bonimenteur prête un bazou (y monter n'est pas un vol) ; quatre autres foncent
sur ce qui roule et se cognent pour vrai ; un derby se termine toujours — dernier debout, bazou mort,
ou aux points ; les bazous restent dans l'arène ; ni crime ni étoile ; et à la fin, l'arène se vide.
"""

#: Le derby, ouvert et commencé a cette heure ; `dur` : le bazou du joueur ne meurt pas.
DERBY = """
  function derby(L, heure, dur) {
    const B = L.B, H = L.Histoire;
    B.partie.heure = heure / 24;
    const d = B.defs.defis.find(function (q) { return q.slug === 'derby'; });
    H.ouvrirDefi(d, true);
    H.commencerDefi(d);
    const e = B.conduite;
    if (e && dur) e.moi.vie = e.moi.vieMax = 1e6;
    return { d: d, e: e };
  }
  function jouer(L, o, e, images, chaque) {
    let k = 0;
    for (; k < images && L.B.defi; k++) { o.frame(1); if (chaque) chaque(e); }
    return k;
  }
"""


def test_le_soir_seulement_et_le_bazou_est_prete(banc):
    r = banc("function (L, o) {" + DERBY + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        const midi = derby(L, 12);
        const aMidi = { defi: !!B.defi, conduite: !!B.conduite };
        const soir = derby(L, 21);
        const e = soir.e;
        return { aMidi: aMidi, defi: !!B.defi, dedans: !!e && j.dansVehicule === e.moi, n: e ? e.bazous.length : 0,
                 pilotes: e ? e.bazous.filter(function (b) { return b.conducteur === 'derby'; }).length : 0,
                 crimes: B.partie.stats.crimes, etoiles: B.recherche.etoiles };
    }""")
    assert r["aMidi"] == {"defi": False, "conduite": False}, f"le derby part en plein jour : {r}"
    assert r["defi"] and r["dedans"] and r["n"] == 5 and r["pilotes"] == 4, r
    assert r["crimes"] == 0 and r["etoiles"] == 0, "monter dans le bazou prêté est un vol"


def test_un_derby_se_termine_toujours_et_les_bazous_restent_dans_l_arene(banc):
    """Trois derbies : le joueur immobile (son bazou meurt), le joueur increvable (le dernier debout),
    et personne ne meurt (aux points : le verdict suit la carrosserie qui reste). Les trois finissent avant le chrono du défi, et à chaque image
    tous les bazous sont dans l'arène."""
    r = banc("function (L, o) {" + DERBY + """
        L.Jeu.commencer();
        const B = L.B;
        function un(dur, increvables) {
            const x = derby(L, 21, dur), e = x.e;
            if (increvables) e.bazous.forEach(function (b) { b.vie = b.vieMax = 1e6; });
            const hud = L.Hud.message, msgs = [];
            L.Hud.message = function (t) { msgs.push(t); return hud.apply(null, arguments); };
            let dehors = 0;
            const a = e.arene;
            const images = jouer(L, o, e, (x.d.chrono_s + 5) * 60, function () {
                for (const b of e.bazous) if (b.x < a.x || b.x > a.x + a.l || b.y < a.y || b.y > a.y + a.h) dehors++;
            });
            L.Hud.message = hud;
            const fin = msgs.filter(function (m) { return /DÉFI|DERBY/.test(m); }).pop() || '';
            const restent = e.bazous.filter(function (b) { return B.entites.indexOf(b) >= 0; });
            const out = { fini: !B.defi, s: Math.round(images / 60), dehors: dehors, fin: fin, restent: restent.length,
                          hopital: msgs.some(function (m) { return /HÔPITAL/.test(m); }),
                          parts: e.bazous.map(function (b) { return b.vie / b.vieMax; }),
                          garde: restent.length === 1 && restent[0] === e.moi && !e.moi.mission };
            if (B.joueur.dansVehicule) L.Vehicules.descendre(B.joueur, true);
            B.partie.defisFaits = {};
            return out;
        }
        return { mort: un(false, false), debout: un(true, false), points: un(false, true),
                 crimes: B.partie.stats.crimes, etoiles: B.recherche.etoiles, chrono: B.defs.defis.find(function (q) { return q.slug === 'derby'; }).chrono_s,
                 temps: B.defs.defis.find(function (q) { return q.slug === 'derby'; }).regles.temps_s };
    }""")
    for cas in ("mort", "debout", "points"):
        c = r[cas]
        assert c["fini"] and c["s"] <= r["chrono"], f"{cas} : le derby ne finit pas ({c})"
        assert c["dehors"] == 0, f"{cas} : un bazou est sorti de l'arène ({c})"
        if cas == "mort":
            assert c["restent"] == 0, f"son bazou mort, l'arène ne s'est pas vidée ({c})"
        else:
            assert c["garde"], f"{cas} : l'arène ne s'est pas vidée, ou le bazou du joueur est parti ({c})"
    assert "RATÉ" in r["mort"]["fin"] and "MORT" in r["mort"]["fin"], r["mort"]
    assert "RATÉ" not in r["debout"]["fin"], r["debout"]
    assert r["debout"]["s"] < r["temps"], f"les bazous ne s'entre-détruisent pas : le dernier debout n'arrive jamais ({r['debout']})"
    assert not any(r[c]["hopital"] for c in ("mort", "debout", "points")), "un bazou mort envoie le joueur à l'hôpital"
    # Aux points : au bout du temps, et le verdict suit la carrosserie qui reste (en part de la sienne).
    p = r["points"]
    assert abs(p["s"] - r["chrono"]) <= 2, f"personne ne meurt : ça finit au bout du temps ({p})"
    assert "POINTS" in p["fin"] or "RATÉ" not in p["fin"], p
    assert ("RATÉ" not in p["fin"]) == (p["parts"][0] >= max(p["parts"][1:])), f"le verdict aux points ment : {p}"
    assert r["crimes"] == 0 and r["etoiles"] == 0, "le derby est un crime"


def test_deux_bazous_se_cognent_pour_vrai_mais_pas_a_chaque_image(banc):
    """Deux bazous qui se rentrent dedans perdent de la carrosserie ; collés, pas une seconde fois
    pendant le répit. Deux autos du trafic, elles, se poussent sans dégâts."""
    r = banc("function (L, o) {" + DERBY + """
        L.Jeu.commencer();
        const B = L.B, V = L.Vehicules;
        const x = derby(L, 21, true), e = x.e;
        const a = e.bazous[1], b = e.bazous[2];
        // Chaque paire se cogne a sa rangee, loin des autres.
        function heurt(p, q, rang) {
            p.x = e.arene.x + 40; p.y = e.arene.y + 30 + (rang || 0) * 40; q.x = p.x + 16; q.y = p.y;
            p.angle = 0; q.angle = Math.PI; p.vx = 2.5; q.vx = -2.5; p.vy = q.vy = 0; p.vitesse = q.vitesse = 2.5;
            L.Entites.indexer();
            const va = p.vie, vb = q.vie;
            V.heurterVehicules(p);
            return (va - p.vie) + (vb - q.vie);
        }
        // Le joueur fonce sur un bazou : c'est le jeu, pas de la conduite dangereuse.
        const crimes = B.crimes.length;
        const moi = heurt(e.moi, e.bazous[3], 3);
        const delit = B.crimes.length - crimes;
        const premier = heurt(a, b);
        const colle = heurt(a, b);
        B.t += Math.round(x.d.regles.repit_s * 60) + 1;
        const apres = heurt(a, b);
        a.derby = false; b.derby = false;
        B.t += 999;
        const trafic = heurt(a, b);
        return { premier: premier, colle: colle, apres: apres, trafic: trafic, moi: moi, delit: delit };
    }""")
    assert r["premier"] > 0 and r["apres"] > 0, r
    assert r["colle"] == 0, f"collés, deux bazous se sont encore cognés pendant le répit : {r}"
    assert r["trafic"] == 0, r
    assert r["moi"] > 0 and r["delit"] == 0, f"foncer sur un bazou au derby est un délit : {r}"


def test_le_panneau_se_plante_au_bord_de_l_arene_quand_il_s_ouvre(banc):
    r = banc("function (L, o) {" + DERBY + """
        L.Jeu.commencer();
        const B = L.B, H = L.Histoire;
        const avant = B.entites.filter(function (e) { return e.type === 'panneau' && e.defi === 'derby'; }).length;
        H.ouvrirDefi(B.defs.defis.find(function (q) { return q.slug === 'derby'; }), true);
        for (let k = 0; k < 130; k++) o.frame(1);
        const p = B.entites.find(function (e) { return e.type === 'panneau' && e.defi === 'derby'; });
        const a = B.defs.derby.arene;
        return { avant: avant, p: !!p, loin: p ? Math.round(Math.hypot(p.x - (a.panneau.x * 16 + 8), p.y - (a.panneau.y * 16 + 8))) : null };
    }""")
    assert r["avant"] == 0, "le panneau du derby est planté au démarrage"
    assert r["p"] and r["loin"] < 12 * 16, r


def test_au_bout_du_temps_la_carrosserie_decide(banc):
    r = banc("function (L, o) {" + DERBY + """
        L.Jeu.commencer();
        const B = L.B, x = derby(L, 21, false), e = x.e, r = x.d.regles, ep = L.Conduite.EPREUVES.derby;
        function aux(moi, autres) {
            e.moi.vie = Math.round(e.moi.vieMax * moi);
            e.bazous.slice(1).forEach(function (b) { b.vie = Math.round(b.vieMax * autres); });
            e.t = (r.attente_s + r.temps_s) * 60 - 1;
            return ep.maj(e, r, e.moi);
        }
        return { cabosse: aux(0.3, 0.9), intact: aux(0.9, 0.3) };
    }""")
    assert r["cabosse"] == {"gagne": False, "raison": "AUX POINTS"}, r
    assert r["intact"] == {"gagne": True}, r
