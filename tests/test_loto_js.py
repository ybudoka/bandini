"""Le 6/49 du dépanneur, JOUÉ au banc (docs/jalons/le-6-49-du-depanneur.md) : le billet chez Ti-Paul,
le tirage de la nuit, et les numéros sous la manchette du Clairon."""

from app import loto


def test_le_meme_jour_les_memes_numeros_pour_tout_le_monde(banc):
    """Deux parties, deux graines : le tirage du jour 3 est le même. Six numéros différents, de 1
    à 49, en ordre — et d'un jour à l'autre, ils changent."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const M = L.Missions, tirages = [];
        for (const graine of [1, 999]) { L.graine(graine); tirages.push([M.tirageDuLoto(3), M.tirageDuLoto(4), M.numerosDuBillet(3, 0)]); }
        return tirages;
    }""")
    assert r[0][:2] == r[1][:2], "le tirage dépend de la partie"
    assert r[0][2] != r[1][2], "le billet, lui, dépend de la partie (sa graine)"
    t3, t4 = r[0][:2]
    assert t3 != t4
    for t in (t3, t4):
        assert len(set(t)) == loto.NUMEROS and t == sorted(t) and all(1 <= n <= loto.BOULES for n in t)


def test_le_billet_se_vend_chez_ti_paul_et_ne_touche_pas_au_hasard_du_jeu(banc):
    """Au présentoir du Clairon, chez Ti-Paul : UN BILLET DE 6/49, 2 $. Cinq par jour, pas un de
    plus. Et cinq billets achetés entre deux tirages de `B.rng()` ne changent pas le suivant."""
    r = banc("function (L, o) {" + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions;
        const porte = (L.Monde.carte.def.portes || []).find(function (q) { return q.lieu === 'depanneur' && q.interieur; });
        B.joueur.x = porte.x * 16 + 8; B.joueur.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
        L.Jeu.entrer(porte); o.fondu();
        for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
        const pt = B.interieur.points.find(function (q) { return q.type === 'journal'; });
        const menu = M.menuDuPoint(pt);
        const ligne = menu.items.find(function (q) { return /6\\/49/.test(q.libelle); });
        L.graine(5);
        const temoin = [B.rng(), B.rng()];
        L.graine(5);
        B.partie.argent = 100;
        const billets = [];
        for (let i = 0; i < 7; i++) { const b = M.acheterUnBillet(); billets.push(b ? b.numeros : null); }
        return { ligne: ligne ? ligne.libelle + '|' + ligne.detail : null, argent: B.partie.argent, billets: billets,
                 apres: [B.rng(), B.rng()], temoin: temoin, fini: M.itemLoto().detail };
    }""")
    assert r["ligne"] == f"UN BILLET DE 6/49|{loto.PRIX} $", r
    assert r["billets"][loto.BILLETS_PAR_JOUR:] == [None, None], "Ti-Paul en vend plus que cinq"
    assert all(len(b) == 6 for b in r["billets"][:loto.BILLETS_PAR_JOUR])
    assert len({tuple(b) for b in r["billets"][:loto.BILLETS_PAR_JOUR]}) == loto.BILLETS_PAR_JOUR
    assert r["argent"] == 100 - loto.BILLETS_PAR_JOUR * loto.PRIX
    assert r["apres"] == r["temoin"], "acheter un billet a décalé le hasard du jeu"
    assert r["fini"] == "PLUS AUJOURD’HUI"


def test_un_billet_gagnant_paie_le_bon_lot_une_seule_fois_et_le_clairon_le_dit(banc):
    """Un billet aux numéros du tirage (six bons) et un autre à trois bons : la nuit paie les deux
    lots, une fois ; la ligne du 6/49 s'écrit sous la manchette du matin, avec les numéros ; la
    nuit d'après ne repaie rien."""
    r = banc("function (L, o) {" + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, p = B.partie;
        const t = M.tirageDuLoto(p.jour);
        const autres = [];
        for (let n = 1; autres.length < 3; n++) if (t.indexOf(n) < 0) autres.push(n);
        p.loto = { billets: [{ jour: p.jour, numeros: t.slice() },
                             { jour: p.jour, numeros: t.slice(0, 3).concat(autres) }], ligne: null };
        p.argent = 0;
        p.jour += 1; M.nouveauJour();
        const premier = p.argent;
        const lignes = B.dialogue ? B.dialogue.lignes || B.dialogue.texte || null : null;
        const ligne = M.ligneDuLoto();
        p.jour += 1; M.nouveauJour();
        return { tirage: t, premier: premier, second: p.argent, ligne: ligne, dialogue: lignes, reste: p.loto.billets.length };
    }""")
    attendu = loto.LOTS[6] + loto.LOTS[3]
    assert r["premier"] == attendu, r
    assert r["second"] == attendu, "la nuit d'après a repayé"
    assert r["reste"] == 0
    assert r["ligne"].startswith("6/49 : " + " ".join(str(n) for n in r["tirage"])), r["ligne"]
    assert "LE GAGNANT EST D’ICI" in r["ligne"] and f"+{attendu} $" in r["ligne"], r["ligne"]
    assert r["dialogue"] and any("6/49" in str(x) for x in r["dialogue"]), r["dialogue"]
