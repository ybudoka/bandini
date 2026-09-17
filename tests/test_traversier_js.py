"""Le traversier (M12) au banc : l'horaire, le pont à quai, à bord, et il part sans toi.

⚠️ On ne fait pas attendre le banc deux heures de jeu : la place du traversier est une
fonction de l'heure (`Traversier.placeA`), et `heure` la règle à la main. ⚠️ Toujours
DEUX images après : le jeu avance à pas fixe, et une image du banc peut n'en faire
aucun — le juge lisait alors la carte d'avant le départ. Un saut
d'heure pendant la traversée ne décroche personne : ce qui est à bord est reposé sur la
coque, où qu'elle soit.
"""

OUTILS = """
    function heure(L, h) { L.B.partie.heure = h / 24; }
    function coque(L) { return L.Traversier.placeA(L.B.partie.heure); }
    function escale(L, k) { return L.Traversier.donnees().escales[k]; }
    // Le centre d'une tuile du pont : colonne `col`, voie `voie` (0 ou 1).
    function pont(L, q, col, voie) { return { x: (q.x + col) * L.TT + 8, y: (q.y + voie) * L.TT + 8 }; }
    function tuile(L, e) { return { x: Math.floor(e.x / L.TT), y: Math.floor(e.y / L.TT) }; }
    function poser(L, j, p) { j.x = p.x; j.y = p.y; j.vx = 0; j.vy = 0; L.Monde.centrerCamera(j.x, j.y); }
"""


def test_l_horaire_est_une_fonction_de_l_heure_et_le_bateau_ne_saute_pas(banc):
    """A quai pile sur l'escale ; départ à l'heure juste (des Quais aux heures paires, de
    La Pointe aux impaires) ; et d'une image à l'autre, jamais un saut plus grand que
    sa vitesse de pointe."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const T = L.Traversier, d = T.donnees(), a = escale(L, 0), b = escale(L, 1);
        const parHeure = L.B.defs.economie.jour_secondes * 60 / 24;
        const out = {
            avantPair: T.etatA((2 - 0.001) / 24), apresPair: T.etatA((2 + 0.001) / 24),
            avantImpair: T.etatA((3 - 0.001) / 24), apresImpair: T.etatA((3 + 0.001) / 24),
            quaiA: T.placeA(1.9 / 24), quaiB: T.placeA(0.9 / 24),
            a: { x: a.px, y: a.py }, b: { x: b.px, y: b.py },
        };
        let pire = 0, avant = T.placeA(0);
        for (let k = 1; k <= 2 * parHeure; k++) {
            const p = T.placeA(k / parHeure / 24);
            pire = Math.max(pire, Math.hypot(p.x - avant.x, p.y - avant.y));
            avant = p;
        }
        out.pire = pire;
        out.vitesseMax = L.B.defs.vehicules.find(function (v) { return v.slug === 'auto'; }).vitesse_max;
        return out;
    }""")
    assert r["avantPair"]["phase"] == "quai" and r["avantPair"]["escale"] == 0
    assert r["apresPair"]["phase"] == "traverse" and r["apresPair"]["de"] == 0
    assert r["avantImpair"]["phase"] == "quai" and r["avantImpair"]["escale"] == 1
    assert r["apresImpair"]["phase"] == "traverse" and r["apresImpair"]["de"] == 1
    assert (r["quaiA"]["x"], r["quaiA"]["y"]) == (r["a"]["x"], r["a"]["y"])
    assert (r["quaiB"]["x"], r["quaiB"]["y"]) == (r["b"]["x"], r["b"]["y"])
    assert 0 < r["pire"] <= r["vitesseMax"], f"le traversier saute de {r['pire']:.2f} px en une image"


def test_a_quai_le_pont_se_roule_et_la_carte_est_rendue_intacte(banc):
    """À quai, le pont est du sol (et de la chaussée : un flâneur n'y descend pas), la
    cabine un mur. En route, la baie redevient de l'eau. Et après deux allers-retours,
    la carte est la même, octet par octet."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const c = L.Monde.carte, a = escale(L, 0), b = escale(L, 1);
        const j = L.B.joueur;
        poser(L, j, { x: a.px - 200, y: a.py - 200 });
        heure(L, 1.2);
        o.frame(2);
        L.Traversier.oublier();
        const avant = { solide: Array.from(c.solide), route: Array.from(c.route), passage: Array.from(c.passage) };
        heure(L, 1.9); o.frame(2);
        const aQuai = { pont: L.Monde.estEau(a.x + 3, a.y), cabine: L.Monde.bloque(a.x + 3, a.y + 2, L.Monde.MASQUE_PIETON),
                        route: L.Monde.estChaussee(a.x + 3, a.y + 1), marchable: L.Monde.marchablePieton(a.x + 3, a.y) };
        heure(L, 2.3); o.frame(2);
        const enRoute = { a: L.Monde.estEau(a.x + 3, a.y) && L.Monde.estEau(a.x + 3, a.y + 2), b: L.Monde.estEau(b.x + 3, b.y) };
        for (const h of [2.8, 3.3, 3.9, 4.3, 4.8, 5.3, 5.9]) { heure(L, h); o.frame(2); }
        L.Traversier.oublier();
        const pareil = ['solide', 'route', 'passage'].every(function (k) {
            const t = c[k]; return avant[k].every(function (v, i) { return t[i] === v; });
        });
        return { aQuai: aQuai, enRoute: enRoute, pareil: pareil };
    }""")
    q = r["aQuai"]
    assert q["pont"] is False, "à quai, le pont est encore de l'eau"
    assert q["cabine"] is True, "on traverse la cabine"
    assert q["route"] is True and q["marchable"] is False, "un flâneur descendrait se promener sur le pont"
    assert r["enRoute"]["a"] is True and r["enRoute"]["b"] is True, "le pont reste posé quand le bateau est parti"
    assert r["pareil"], "la carte n'est pas rendue telle qu'elle était"


def test_a_pied_on_traverse_et_on_descend_de_l_autre_cote(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const j = L.B.joueur, a = escale(L, 0), b = escale(L, 1);
        j.intouchable = true;
        heure(L, 1.9);
        o.frame(2);
        poser(L, j, pont(L, a, 4, 0));
        heure(L, 1.995);
        o.frame(20);
        const parti = { aBord: !!j.aBord, radio: L.Son.Radio.demandee };
        // En pleine baie.
        heure(L, 2.3); o.frame(2);
        const h = coque(L);
        const enRoute = { dx: j.x - h.x, dy: j.y - h.y, nage: !!j.nage, aBord: !!j.aBord, texte: L.Traversier.texteDInfo(j) };
        heure(L, 2.35); o.frame(30);
        const h2 = coque(L);
        enRoute.dx2 = j.x - h2.x; enRoute.dy2 = j.y - h2.y; enRoute.nage2 = !!j.nage;
        // L'arrivée, puis on marche vers la rive.
        heure(L, 2.7); o.frame(2);
        const arrive = { aBord: !!j.aBord, tuile: tuile(L, j), radio: L.Son.Radio.demandee };
        const sens = b.cote === 'est' ? 'KeyD' : b.cote === 'ouest' ? 'KeyA' : 'KeyW';
        o.touche(sens); o.frame(90); o.relacher(sens); o.frame(1);
        return { parti: parti, enRoute: enRoute, arrive: arrive, fin: tuile(L, j), nageFin: !!j.nage,
                 b: { x: b.x, y: b.y, cote: b.cote, acces: b.acces }, largeur: L.Traversier.donnees().coque.longueur };
    }""")
    assert r["parti"]["aBord"] is True, "sur le pont à l'heure du départ, et resté à quai"
    assert r["parti"]["radio"] == "traversier", "à bord, la radio du pont ne joue pas"
    e = r["enRoute"]
    assert e["aBord"] is True and e["nage"] is False and e["nage2"] is False, "le joueur nage sous le traversier"
    assert (e["dx"], e["dy"]) == (e["dx2"], e["dy2"]), "le joueur glisse sur le pont"
    assert "LA POINTE DANS" in (e["texte"] or ""), e["texte"]
    a = r["arrive"]
    b = r["b"]
    assert a["aBord"] is False, "à quai, le joueur est encore tenu"
    assert b["x"] <= a["tuile"]["x"] < b["x"] + r["largeur"] and b["y"] <= a["tuile"]["y"] <= b["y"] + 1, a
    assert a["radio"] is None, "descendu à pied, la radio du pont joue encore"
    assert r["nageFin"] is False, "le joueur est tombé à l'eau en descendant"
    assert b["cote"] == "est" and r["fin"]["x"] >= b["x"] + r["largeur"], f"le joueur n'a pas mis pied à terre : {r['fin']}"


def test_en_char_on_monte_en_roulant_et_on_debarque_sans_couler(banc):
    """Le pont se prend au volant, depuis le bout de rue : pas de bouton. À bord, le
    char ne coule pas et ne roule pas ; à l'autre quai, on en sort en roulant."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const j = L.B.joueur, a = escale(L, 0), b = escale(L, 1);
        j.intouchable = true;
        heure(L, 1.8);
        o.frame(2);
        // Sur le bout de quai, le nez vers le pont.
        const t = a.acces[0];
        const vers = a.cote === 'ouest' ? 0 : a.cote === 'est' ? Math.PI : Math.PI / 2;
        const p = { x: t[0] * L.TT + 8 - Math.cos(vers) * 8, y: t[1] * L.TT + 8 - Math.sin(vers) * 8 };
        poser(L, j, p);
        const v = L.Vehicules.creer('auto', p.x, p.y, vers, { etat: 'stationne' });
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
        o.touche('KeyW');
        let surLePont = false;
        for (let i = 0; i < 120 && !surLePont; i++) {
            o.frame(1);
            const q = tuile(L, v);
            surLePont = q.x >= a.x + 2 && q.x < a.x + 6 && q.y >= a.y && q.y <= a.y + 1;
        }
        o.relacher('KeyW');
        o.touche('KeyS'); o.frame(25); o.relacher('KeyS');
        o.frame(20);
        const monte = { surLePont: surLePont, tuile: tuile(L, v), vitesse: v.vitesse };
        heure(L, 1.999); o.frame(10);
        const parti = { v: !!v.aBord, j: !!j.aBord, dedans: j.dansVehicule === v };
        heure(L, 2.3); o.frame(60);
        const h = coque(L);
        const enRoute = { coule: v.coule, epave: v.etat === 'epave', dx: v.x - h.x, dy: v.y - h.y, jx: j.x === v.x && j.y === v.y };
        heure(L, 2.7); o.frame(2);
        const arrive = { v: !!v.aBord, j: !!j.aBord, tuile: tuile(L, v) };
        // On sort par le bout de l'escale d'en face.
        const sortie = b.cote === 'est' ? 0 : b.cote === 'ouest' ? Math.PI : -Math.PI / 2;
        v.angle = sortie;
        o.touche('KeyW'); o.frame(80); o.relacher('KeyW'); o.frame(30);
        return { monte: monte, parti: parti, enRoute: enRoute, arrive: arrive,
                 fin: { tuile: tuile(L, v), coule: v.coule, epave: v.etat === 'epave', eau: L.Monde.estEau(tuile(L, v).x, tuile(L, v).y) },
                 b: { x: b.x, y: b.y, cote: b.cote } };
    }""")
    assert r["monte"]["surLePont"], f"le char n'est pas monté sur le pont : {r['monte']}"
    assert r["parti"] == {"v": True, "j": True, "dedans": True}, r["parti"]
    e = r["enRoute"]
    assert e["coule"] == 0 and not e["epave"], f"le char coule à bord : {e}"
    assert e["jx"], "le joueur n'est plus dans son char"
    assert r["arrive"]["v"] is False and r["arrive"]["j"] is False
    f = r["fin"]
    assert not f["eau"] and f["coule"] == 0 and not f["epave"], f"débarqué à l'eau : {f}"
    assert r["b"]["cote"] == "est" and f["tuile"]["x"] >= r["b"]["x"] + 8, f"le char n'a pas quitté le pont : {f}"


def test_il_part_sans_toi(banc):
    """Sur le bout de quai et pas sur le pont à l'heure du départ : on reste à terre, et
    le pont redevient de l'eau sous le nez. Un passant égaré sur le pont, lui, est remis
    sur le quai — personne ne part sans billet ni ne reste au-dessus de l'eau."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const j = L.B.joueur, a = escale(L, 0);
        j.intouchable = true;
        heure(L, 1.9); o.frame(2);
        const t = a.acces[0];
        poser(L, j, { x: t[0] * L.TT + 8, y: t[1] * L.TT + 8 });
        const p = L.Entites.creerPieton(pont(L, a, 5, 1).x, pont(L, a, 5, 1).y, L.Entites.archetype('passant'));
        p.etat = 'fige'; p.plante = { x: p.x, y: p.y };
        L.Entites.indexer();
        const avant = { x: j.x, y: j.y };
        heure(L, 1.998); o.frame(12);
        const tp = tuile(L, p);
        return { aBord: !!j.aBord, bouge: Math.hypot(j.x - avant.x, j.y - avant.y), pontEau: L.Monde.estEau(a.x + 1, a.y),
                 passant: { tuile: [tp.x, tp.y], aBord: !!p.aBord, eau: L.Monde.estEau(tp.x, tp.y) }, acces: a.acces,
                 parti: L.Traversier.etatA(L.B.partie.heure).phase };
    }""")
    assert r["parti"] == "traverse", "le juge n'a pas passé l'heure du départ"
    assert r["aBord"] is False and r["bouge"] < 2, "resté sur le quai, le joueur est parti quand même"
    assert r["pontEau"] is True
    assert r["passant"]["aBord"] is False and r["passant"]["eau"] is False, r["passant"]
    assert r["passant"]["tuile"] in r["acces"], f"le passant n'a pas été remis sur le quai : {r['passant']}"


def test_au_quai_le_hud_dit_quand_il_part(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const j = L.B.joueur, a = escale(L, 0), b = escale(L, 1);
        const t = a.acces[0];
        poser(L, j, { x: t[0] * L.TT + 8, y: t[1] * L.TT + 8 });
        heure(L, 1.9); o.frame(2);
        const aQuai = L.Traversier.texteDInfo(j);
        heure(L, 2.5); o.frame(2);
        const parti = L.Traversier.texteDInfo(j);
        const u = b.acces[0];
        poser(L, j, { x: u[0] * L.TT + 8, y: u[1] * L.TT + 8 });
        heure(L, 5.5); o.frame(2);
        const enFace = L.Traversier.texteDInfo(j);
        poser(L, j, { x: t[0] * L.TT + 8 + 400, y: t[1] * L.TT + 8 });
        return { aQuai: aQuai, parti: parti, enFace: enFace, loin: L.Traversier.texteDInfo(j) };
    }""")
    assert r["aQuai"].startswith("TRAVERSIER POUR LA POINTE · DÉPART DANS"), r["aQuai"]
    assert r["parti"] == "TRAVERSIER POUR LA POINTE · DÉPART 04:00", r["parti"]
    assert r["enFace"] == "TRAVERSIER POUR LES QUAIS · DÉPART 07:00", r["enFace"]
    assert r["loin"] is None


def test_le_traversier_ne_tire_aucun_de_et_se_dessine(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const j = L.B.joueur, a = escale(L, 0);
        j.intouchable = true;
        L.graine(99);
        const tirage = L.B.rng;
        let dansLeTraversier = 0;
        L.B.rng = function () {
            if (String(new Error().stack).indexOf('traversier.js') >= 0) dansLeTraversier++;
            return tirage();
        };
        heure(L, 1.9); o.frame(2);
        poser(L, j, pont(L, a, 3, 0));
        for (const h of [1.95, 1.999, 2.2, 2.5, 2.7, 2.9, 3.001, 3.4]) { heure(L, h); o.frame(3); }
        // Le dessin : la caméra sur la coque, une image peinte.
        const h = coque(L);
        L.Monde.centrerCamera(h.x + 64, h.y + 24);
        const visibles = [];
        L.Traversier.ajouterVisibles(visibles, h.x + 64 - L.VW / 2, h.y + 24 - L.VH / 2);
        let peint = true;
        const ctx = { fillStyle: '', fillRect: function () {} };
        try { visibles.forEach(function (v) { v.peindreFoire(ctx); }); }
        catch (e) { peint = String(e); }
        o.frame(2);
        return { des: dansLeTraversier, visibles: visibles.length, peint: peint };
    }""")
    assert r["des"] == 0, f"{r['des']} dés tirés par le traversier"
    assert r["visibles"] >= 1, "la coque ne se dessine pas quand la caméra est dessus"
    assert r["peint"] is True, r["peint"]


def test_une_piece_pendant_le_depart_ne_laisse_pas_de_pont_fantome(banc):
    """On entre dans la planque avec le traversier à quai, on en sort après son départ :
    le pont ne reste pas posé sur l'eau."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const j = L.B.joueur, a = escale(L, 0), c = L.Monde.carte, TT = L.TT;
        heure(L, 1.9); o.frame(2);
        const pose = L.Monde.estEau(a.x + 2, a.y);
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 10;
        L.Monde.centrerCamera(j.x, j.y);
        L.Jeu.entrer(porte); o.fondu();
        const dedans = !!L.B.interieur;
        heure(L, 2.4); o.frame(2);
        L.Jeu.sortir(); o.fondu();
        o.frame(2);
        return { pose: pose, dedans: dedans, apres: L.Monde.estEau(a.x + 2, a.y) };
    }""")
    assert r["dedans"] is True, "le juge n'est pas entré"
    assert r["pose"] is False
    assert r["apres"] is True, "un pont fantôme est resté sur l'eau"
