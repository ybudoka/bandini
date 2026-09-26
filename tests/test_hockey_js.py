"""Le hockey de ruelle, au banc (docs/jalons/le-hockey-de-ruelle.md) : le soir seulement, dans une ruelle
des Érables ; une partie finit toujours (le chrono) ; un tir droit au filet vide marque ; les jeunes ne
sortent pas de la ruelle et ne tirent aucun `B.rng()` ; on gagne par trois buts ; l'hiver, la balle glisse."""

OUTILS = """
  function hockey(L, heure) {
    const B = L.B, H = L.Histoire, j = B.joueur;
    B.partie.heure = heure / 24;
    const d = B.defs.defis.find(function (q) { return q.slug === 'hockey'; });
    H.ouvrirDefi(d, true);
    const dep = H.lieu('depanneur'); j.x = dep.x; j.y = dep.y + 24; L.Entites.indexer();
    H.commencerDefi(d);
    return d;
  }
  function entrer(L, o) {
    const e = L.B.rue, p = e.piste, j = L.B.joueur;
    j.x = (p.x0 + p.x1) / 2 - 20; j.y = p.y; L.Entites.indexer();
    o.frame(2);
  }
"""


def test_le_soir_dans_une_ruelle_des_erables(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        hockey(L, 12); const midi = !!B.defi;
        hockey(L, 21);
        const e = B.rue, p = e && e.piste, Mo = L.Monde;
        let ruelle = true;
        if (p) for (let x = p.x0 + 8; x < p.x1; x += 16) for (const y of [p.haut + 8, p.bas - 8]) ruelle = ruelle && Mo.glyphe(Math.floor(x / 16), Math.floor(y / 16)) === 'x';
        const z = p ? Mo.zoneA((p.x0 + p.x1) / 2, p.y) : null;
        return { midi: midi, soir: !!B.defi, sorte: e && e.sorte, ruelle: ruelle, district: z && z.district, jeunes: e ? e.jeunes.length : 0 };
    }""")
    assert r["midi"] is False, "le hockey part en plein jour"
    assert r["soir"] and r["sorte"] == "hockey" and r["ruelle"] and r["district"] == "erables", r
    assert r["jeunes"] == 5, "trois contre trois : toi, deux jeunes, et trois Chevreuils"


def test_une_partie_finit_toujours_et_les_jeunes_restent_dans_la_ruelle(banc):
    """Le joueur ne bouge pas : la partie va au bout de ses trois minutes, et finit ratée. Pendant tout ce
    temps, aucun jeune ne sort de la ruelle."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, d = hockey(L, 21);
        entrer(L, o);
        const e = B.rue, p = e.piste;
        let dehors = 0, k = 0;
        const msgs = [], hud = L.Hud.message; L.Hud.message = function (m) { msgs.push(m); return hud.apply(null, arguments); };
        for (; k < (d.chrono_s + 5) * 60 && B.defi; k++) {
            o.frame(1);
            for (const y of e.jeunes) if (y.x < p.x0 || y.x > p.x1 || y.y < p.haut || y.y > p.bas) dehors++;
        }
        // Un jeune pousse hors de la ruelle (un coup d'epaule) : la patinoire le ramene.
        const ep = L.Rue.EPREUVES.hockey, y0 = e.jeunes[1];
        B.rue = e; y0.x = p.x1 + 40; y0.y = p.bas + 30; e.pause = 0; e.phase = 'jeu';
        ep.maj(e, d.regles);
        if (y0.x < p.x0 || y0.x > p.x1 || y0.y < p.haut || y0.y > p.bas) dehors += 1000;
        return { fini: !B.defi, s: Math.round(k / 60), dehors: dehors, fin: msgs.filter(function (m) { return /DÉFI/.test(m); }).pop() || '',
                 temps: d.chrono_s, buts: e.nous + e.eux };
    }""")
    assert r["fini"] and r["s"] <= r["temps"] + 3, r
    assert "RATÉ" in r["fin"], r
    assert r["dehors"] == 0, f"un jeune est sorti de la ruelle : {r}"
    assert r["buts"] > 0, "trois minutes sans un but : les Chevreuils ne jouent pas"


def test_un_tir_droit_au_filet_vide_marque(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        hockey(L, 21); entrer(L, o);
        const e = B.rue, p = e.piste, j = B.joueur;
        // Le gardien des Chevreuils parti a l'autre bout ; le joueur, la balle au baton, face au filet.
        for (const y of e.jeunes) { y.x = p.x0 + 20; y.y = p.y; y.depart = { x: p.x0 + 20, y: p.y }; }
        j.x = p.x1 - 60; j.y = p.y; j.angle = 0; L.Entites.indexer();
        e.balle.x = j.x + 6; e.balle.y = j.y; e.balle.vx = 0; e.balle.vy = 0; e.porteur = { q: j, equipe: 'nous', joueur: true };
        o.tape('KeyJ', 1);
        for (let k = 0; k < 40 && !e.nous; k++) o.frame(1);
        return { nous: e.nous, eux: e.eux };
    }""")
    assert r == {"nous": 1, "eux": 0}, r


def test_les_jeunes_ne_tirent_aucun_de_du_jeu(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, d = hockey(L, 21);
        entrer(L, o);
        const e = B.rue, ep = L.Rue.EPREUVES.hockey;
        L.graine(9); const temoin = [B.rng(), B.rng()]; L.graine(9);
        for (let k = 0; k < 900; k++) { ep.maj(e, d.regles); }
        return { temoin: temoin, apres: [B.rng(), B.rng()], buts: e.nous + e.eux };
    }""")
    assert r["apres"] == r["temoin"], "le hockey a tiré au dé du jeu"
    assert r["buts"] > 0, "le juge n'a rien fait jouer"


def test_on_gagne_par_trois_buts(banc):
    """Un joueur qui court à la balle et tire dans le coin que le gardien ne couvre pas gagne avant la fin."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, d = hockey(L, 21);
        entrer(L, o);
        const e = B.rue, p = e.piste, j = B.joueur;
        let k = 0;
        for (; k < (d.chrono_s + 5) * 60 && B.defi; k++) {
            const b = e.balle, a = Math.atan2(b.y - j.y, b.x - j.x);
            ['KeyW', 'KeyA', 'KeyS', 'KeyD'].forEach(function (t) { o.relacher(t); });
            if (e.porteur && e.porteur.joueur) {
                const g = e.jeunes.find(function (y) { return y.equipe === 'eux' && y.k === 0; });
                const vise = g && g.y > p.y ? p.y - 5 : p.y + 5;
                j.angle = Math.atan2(vise - j.y, p.x1 - j.x);
                if (p.x1 - j.x < 70) o.tape('KeyJ', 1); else o.touche('KeyD');
            } else {
                if (Math.cos(a) > 0.4) o.touche('KeyD'); if (Math.cos(a) < -0.4) o.touche('KeyA');
                if (Math.sin(a) > 0.4) o.touche('KeyS'); if (Math.sin(a) < -0.4) o.touche('KeyW');
            }
            o.frame(1);
        }
        return { fait: !!B.partie.defisFaits.hockey, nous: e.nous, eux: e.eux, s: Math.round(k / 60) };
    }""")
    assert r["fait"] and r["nous"] - r["eux"] >= 3, r


def test_l_hiver_la_balle_glisse(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, d = hockey(L, 21);
        entrer(L, o);
        const e = B.rue, p = e.piste, ep = L.Rue.EPREUVES.hockey;
        function glisse(jour, neige) {
            B.partie.jour = jour; B.options.neige = neige;
            for (const y of e.jeunes) { y.x = p.x0 + 10; y.y = p.bas - 5; y.depart = { x: y.x, y: y.y }; y.repit = 999; }
            B.joueur.x = p.x0 + 10; B.joueur.y = p.haut + 5; e.repitJoueur = 999;
            e.porteur = null; e.pause = 0; e.balle.x = p.x0 + 60; e.balle.y = p.y; e.balle.vx = 3; e.balle.vy = 0;
            for (let k = 0; k < 60; k++) ep.maj(e, d.regles);
            return Math.round(e.balle.x - (p.x0 + 60));
        }
        return { ete: glisse(22, false), hiver: glisse(2, true) };
    }""")
    assert r["hiver"] > r["ete"] * 1.3, r
