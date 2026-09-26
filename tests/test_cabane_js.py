"""La cabane à sucre, au banc (docs/jalons/la-cabane-a-sucre.md) : on y entre par le bord nord du Faubourg ;
son comptoir sert le repas des sucres au printemps et se dit fermé hors saison (pas un menu vide) ; il
propose la tire sur la neige, qui se gagne à point et se rate trop chaude ou trop froide, sans un dé."""

OUTILS = """
  const TT = 16;
  async function laisserArriver(L, o) { for (let i = 0; i < 6; i++) { o.frame(1); await o.attendre(); } }
  async function entrerDansLeBloc(L, o, jour, heure) {
    const B = L.B, j = B.joueur, p = B.defs.blocs.find(function (b) { return b.slug === 'cabane'; }).passage;
    B.partie.jour = jour; B.partie.heure = heure / 24;
    if (B.menu) L.Hud.fermerMenu();
    j.x = (p.de + 2) * TT + 8; j.y = TT + 8; L.Entites.indexer();
    await laisserArriver(L, o);
    o.touche('KeyW');
    for (let i = 0; i < 120 && !B.transition; i++) o.frame(1);
    o.relacher('KeyW');
    for (let i = 0; i < 100; i++) o.frame(1);
    await laisserArriver(L, o);
    for (let i = 0; i < 20; i++) o.frame(1);
  }
  function entrerDansLaCabane(L, o) {
    const B = L.B, j = B.joueur, porte = L.Monde.carte.def.portes.find(function (q) { return q.interieur === 'cabane'; });
    j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    return B.interieur && B.interieur.points.find(function (q) { return q.type === 'emplettes'; });
  }
  function libelles(m) { return m ? m.items.map(function (i) { return i.libelle; }) : null; }
"""


def test_le_comptoir_des_sucres_au_printemps_et_ferme_hors_saison(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions;
        L.Histoire.ouvrirDefi(B.defs.defis.find(function (q) { return q.slug === 'tire'; }), true);
        await entrerDansLeBloc(L, o, 12, 13);
        const bloc = B.bloc && B.bloc.slug;
        const pt = entrerDansLaCabane(L, o);
        if (!pt) return { bloc: bloc, piece: false };
        const printemps = libelles(M.menuDuPoint(pt));
        B.partie.jour = 2; const hiver = libelles(M.menuDuPoint(pt));
        B.partie.jour = 22; const ete = libelles(M.menuDuPoint(pt));
        return { bloc: bloc, piece: B.interieur.slug, printemps: printemps, hiver: hiver, ete: ete };
    }""")
    assert r["bloc"] == "cabane" and r["piece"] == "cabane", r
    assert "OREILLES DE CRISSE" in r["printemps"] and "TIRE SUR LA NEIGE" in r["printemps"], r["printemps"]
    assert "LA TIRE SUR LA NEIGE — DÉFI" in r["printemps"], r["printemps"]
    for hors in (r["hiver"], r["ete"]):
        assert hors == ["FERMÉ — ON OUVRE AU TEMPS DES SUCRES"], hors


def test_la_tire_se_gagne_a_point_et_se_rate_sans_un_de(banc):
    """À point à chaque palette : quatre, et le défi est réussi. Les mains dans les poches : elle casse deux
    fois, et c'est raté. Entre deux tirages de `B.rng()`, l'épreuve n'en prend aucun."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, H = L.Histoire, A = L.Adresse;
        const d = B.defs.defis.find(function (q) { return q.slug === 'tire'; });
        function jouer(aPoint, tropTot) {
            B.partie.defisFaits = {};
            H.commencerDefi(d);
            const e = B.epreuve || (A.etat && A.etat());
            const msgs = [], hud = L.Hud.message; L.Hud.message = function (m) { msgs.push(m); return hud.apply(null, arguments); };
            let k = 0;
            for (; k < (d.chrono_s + 2) * 60 && B.defi; k++) {
                const ep = B.epreuve;
                if (aPoint && ep && ep.pause === 0 && Math.abs(ep.temp - ep.centre) < d.regles.zone / 4) o.tape('KeyE', 1);
                else if (tropTot && ep && ep.pause === 0 && ep.temp > 0.95) o.tape('KeyE', 1);
                else o.frame(1);
            }
            L.Hud.message = hud;
            return { fait: !!B.partie.defisFaits.tire, fin: msgs.filter(function (m) { return /DÉFI|TIRE/.test(m); }).pop() || '' };
        }
        const gagne = jouer(true), rate = jouer(false), tot = jouer(false, true);
        // Aucun de : l'epreuve seule, entre deux tirages — en reussissant des palettes (le point change).
        H.commencerDefi(d);
        const ep = B.epreuve, neuf = L.Entree.neuf;
        L.Entree.neuf = function (a) { return a === 'action' && ep.pause === 0 && Math.abs(ep.temp - ep.centre) < d.regles.zone / 4; };
        L.graine(9); const temoin = [B.rng(), B.rng()]; L.graine(9);
        for (let k = 0; k < 400; k++) A.maj(d);
        const apres = [B.rng(), B.rng()];
        L.Entree.neuf = neuf;
        return { gagne: gagne, rate: rate, tot: tot, temoin: temoin, apres: apres, palettes: ep.reussis };
    }""")
    assert r["gagne"]["fait"], r
    assert not r["rate"]["fait"] and "LA TIRE EST RATÉE" in r["rate"]["fin"], r
    assert not r["tot"]["fait"] and "LA TIRE EST RATÉE" in r["tot"]["fin"], f"trop chaude, elle a pris quand même : {r['tot']}"
    assert r["palettes"] >= 2, "le juge du dé n'a réussi aucune palette : le point n'a pas changé"
    assert r["apres"] == r["temoin"], "la tire a tiré au dé du jeu"
