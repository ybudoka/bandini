"""La navette de l'île, au banc : elle part à l'heure, décalée d'une heure du traversier, et elle porte à
l'île ce qui est sur son pont — à pied, et un char (« le premier char que tu y emmènes est un événement »)."""

OUTILS = """
    function heure(L, h) { L.B.partie.heure = h / 24; }
    function escale(L, k) { return L.Navette.donnees().escales[k]; }
    function pont(L, q, col, voie) { return { x: (q.x + col) * L.TT + 8, y: (q.y + voie) * L.TT + 8 }; }
    function tuile(L, e) { return { x: Math.floor(e.x / L.TT), y: Math.floor(e.y / L.TT) }; }
    function poser(L, j, p) { j.x = p.x; j.y = p.y; j.vx = 0; j.vy = 0; L.Monde.centrerCamera(j.x, j.y); }
"""


def test_elle_part_une_heure_apres_le_traversier(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const N = L.Navette, T = L.Traversier;
        return { nav1: N.etatA(1.001 / 24), nav0: N.etatA(0.999 / 24), tra0: T.etatA(0.001 / 24),
                 navQuai: N.etatA(0.5 / 24), traQuai: T.etatA(1.5 / 24) };
    }""")
    assert r["nav0"]["phase"] == "quai" and r["nav0"]["escale"] == 0, r
    assert r["nav1"]["phase"] == "traverse" and r["nav1"]["de"] == 0, "elle quitte les Quais à l'heure impaire"
    assert r["tra0"]["phase"] == "traverse" and r["tra0"]["de"] == 0, "le traversier, lui, à l'heure paire"


def test_un_char_sur_son_pont_arrive_a_l_ile(banc):
    """Un char garé sur le pont aux Quais avant l'heure impaire ; à l'arrivée, il est au quai de l'île, sur la
    jetée de planches, pas dans l'eau. Et au quai, le HUD dit « NAVETTE POUR L'ÎLE-AUX-CORNEILLES »."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const j = L.B.joueur, a = escale(L, 0), b = escale(L, 1);
        j.intouchable = true;
        heure(L, 0.8); o.frame(2);
        const p = pont(L, a, 4, 0);
        const v = L.Vehicules.creer('auto', p.x, p.y, 0, { etat: 'stationne', couleur: '#ffffff' });
        poser(L, j, { x: p.x, y: p.y - 40 }); L.Entites.indexer();
        heure(L, 0.99); o.frame(2);
        const texte = L.Navette.texteDInfo({ x: a.acces[0][0] * 16 + 8, y: a.acces[0][1] * 16 + 8 });
        heure(L, 1.2); o.frame(2);
        const enRoute = { aBord: !!v.aBord };
        heure(L, 1.8); o.frame(2);
        return { texte: texte, enRoute: enRoute, arrive: tuile(L, v), aBord: !!v.aBord, eau: L.Monde.estEau(Math.floor(v.x / 16), Math.floor(v.y / 16)),
                 b: { x: b.x, y: b.y }, longueur: L.Navette.donnees().coque.longueur };
    }""")
    assert "NAVETTE POUR L'ÎLE-AUX-CORNEILLES" in (r["texte"] or ""), r["texte"]
    assert r["enRoute"]["aBord"] is True, "le char est resté aux Quais"
    b = r["b"]
    assert r["aBord"] is False and not r["eau"], r
    assert b["x"] <= r["arrive"]["x"] < b["x"] + r["longueur"] and b["y"] <= r["arrive"]["y"] <= b["y"] + 1, r
