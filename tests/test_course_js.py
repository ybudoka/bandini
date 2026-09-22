"""Les courses : on suit les flèches au sol, et chaque quartier a son tour (21-22 sept. 2026).

Demandes de Martin : « pour les courses, il faut un nouveau concept de flèches lumineuses sur
la route qui trace le chemin de la course, pas des flèches avec les mètres » ; « je veux une
side quest de course par secteur » ; et « pas besoin de point de passage, on doit suivre les
flèches lumineuses au sol. Si on quitte, on a 5 sec pour revenir ou on doit recommencer. »

Une course (`circuit` dans `missions.DEFIS`) est un circuit fermé, tiré au panneau sur la
chaussée (`Histoire.circuit`, `Monde.cheminRoute`), et on le suit.

⚠️ Juges : le chemin d'un char reste sur la chaussée et roule à droite ; chacun des cinq
quartiers a un circuit fermé sur SES rues, qui part près de son panneau ; les chronos
exigent tous la même vitesse ; on gagne en suivant les flèches, sans point de passage ; hors
de la piste, cinq secondes pour revenir, puis c'est raté ; et la flèche-avec-les-mètres du
GPS se tait sur la piste, puis revient.
"""

#: Joue le panneau d'une course comme le jeu : le menu, COMMENCER — et le menu se referme.
#: ⚠️ `faire()` appelé à la main ne ferme pas le menu (c'est `Hud.majMenu` qui lit son retour),
#: et un menu ouvert FIGE la ville : sans `fermerMenu`, `majDefi` ne tournerait jamais.
COMMENCER = """
    function commencer(L, slug) {
        L.Histoire.proposerDefi(slug);
        L.B.menu.items[0].faire();
        L.Hud.fermerMenu();
        return L.B.defi;
    }
    function auVolant(L, o, x, y) {
        const j = L.B.joueur;
        j.intouchable = true;
        j.x = x; j.y = y;
        L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('auto', 0, 0, 0);
        v.vitesse = 0;
        L.Vehicules.monter(j, v);
        return v;
    }
    function poser(L, v, p) {
        v.x = p.x; v.y = p.y; v.vitesse = 0; v.vx = 0; v.vy = 0;
        const j = L.B.joueur; j.x = p.x; j.y = p.y;
        L.Monde.centrerCamera(p.x, p.y);
    }
"""


def test_le_chemin_de_char_suit_la_chaussee_et_roule_a_droite(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const a = L.Histoire.lieu('terminus'), b = L.Histoire.lieu('garage');
        const t0 = Date.now();
        const chemin = L.Monde.cheminRoute(a.x, a.y, b.x, b.y);
        const ms = Date.now() - t0;
        const CONTRE = { '16,0': '<', '-16,0': '>', '0,16': '^', '0,-16': 'v' };
        let horsChaussee = 0, contreSens = 0, prec = null;
        for (const p of chemin || []) {
            const tx = Math.floor(p.x / L.TT), ty = Math.floor(p.y / L.TT);
            if (!L.Monde.estRoute(tx, ty)) horsChaussee++;
            if (prec && L.Monde.fleche(tx, ty) === CONTRE[(p.x - prec.x) + ',' + (p.y - prec.y)]) contreSens++;
            prec = p;
        }
        const dernier = chemin && chemin.length ? chemin[chemin.length - 1] : null;
        return { n: chemin ? chemin.length : 0, horsChaussee: horsChaussee, contreSens: contreSens, ms: ms,
                 pres: dernier ? Math.hypot(dernier.x - b.x, dernier.y - b.y) / L.TT : null };
    }""")
    assert r["n"] > 0, "aucun chemin de char entre le terminus et le garage"
    assert r["horsChaussee"] == 0, "le tracé a quitté la chaussée"
    assert r["contreSens"] == 0, f"le tracé roule à contre-sens sur {r['contreSens']} tuiles"
    assert r["ms"] < 100, "un A* sur la chaussée ne doit pas geler l'image"
    assert r["pres"] is not None and r["pres"] < 12, "le chemin ne finit pas près du garage"


def test_une_cible_hors_de_toute_route_ne_gele_pas(banc):
    """Une cible en dehors de la carte : `null`, tout de suite — pas de plantage."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const a = L.Histoire.lieu('terminus');
        const t0 = Date.now();
        return { chemin: L.Monde.cheminRoute(a.x, a.y, -500, -500), ms: Date.now() - t0 };
    }""")
    assert r["chemin"] is None
    assert r["ms"] < 50


def test_chaque_quartier_a_son_circuit_ferme_sur_ses_rues(banc):
    """⚠️ Rouge avant : un circuit de la Shop tiré depuis la fourrière partait de la chaussée
    de sa COUR, qui ne touche aucune rue — pas un seul tronçon ne sortait. Les ancres se
    posent sur une vraie rue (une voie, un sens, `Monde.routeLaPlusProche`)."""
    r = banc("function (L, o) {" + COMMENCER + """
        L.Jeu.commencer();
        const out = {};
        for (const d of L.B.defs.defis.filter(function (q) { return q.circuit; })) {
            const t0 = Date.now();
            const f = commencer(L, d.slug), p = f.piste, ms = Date.now() - t0;
            const panneau = L.B.entites.find(function (e) { return e.type === 'panneau' && e.defi === d.slug; });
            let horsChaussee = 0, dedans = 0, trous = 0;
            (p || []).forEach(function (q, i) {
                if (!L.Monde.estRoute(Math.floor(q.x / L.TT), Math.floor(q.y / L.TT))) horsChaussee++;
                const z = L.Monde.zoneA(q.x, q.y);
                if (z && z.district === d.district) dedans++;
                const s = p[(i + 1) % p.length];
                if (Math.abs(s.x - q.x) + Math.abs(s.y - q.y) !== L.TT) trous++;
            });
            out[d.slug] = { n: p ? p.length : 0, ms: ms, horsChaussee: horsChaussee, trous: trous,
                            dedans: p ? dedans / p.length : 0,
                            panneau: p && panneau ? Math.hypot(p[0].x - panneau.x, p[0].y - panneau.y) / L.TT : null };
            L.Histoire.finirDefi(false, 'JUGE');
        }
        return out;
    }""")
    assert sorted(r) == ["tour", "tour_erables", "tour_pointe", "tour_quais", "tour_shop"]
    for slug, c in r.items():
        assert c["n"] >= 150, f"{slug} : pas de circuit (ou un circuit ridicule) — {c}"
        assert c["horsChaussee"] == 0, f"{slug} : le circuit quitte la chaussée"
        assert c["trous"] == 0, f"{slug} : le circuit n'est pas fermé d'une tuile à la suivante"
        assert c["dedans"] >= 0.9, f"{slug} : le tour du quartier en sort ({c['dedans']:.0%} dedans)"
        assert c["panneau"] is not None and c["panneau"] <= 16, f"{slug} : la ligne de départ est loin du panneau — {c}"
        assert c["ms"] < 100, f"{slug} : tirer le circuit gèle l'image ({c['ms']} ms)"


def test_les_chronos_exigent_la_meme_vitesse_que_le_tour_du_faubourg(banc):
    """⚠️ Un chrono se MESURE sur la longueur du circuit, il ne s'estime pas sur la surface du
    quartier : le Tour du Faubourg est l'étalon (joué depuis la v1), les autres exigent la même
    vitesse moyenne, arrondie en faveur du joueur — et aucun ne demande de rouler à fond."""
    r = banc("function (L, o) {" + COMMENCER + """
        L.Jeu.commencer();
        const auto = L.Vehicules.vehiculeDef('auto');
        const out = { max: auto.vitesse_max * 60, courses: {} };
        for (const d of L.B.defs.defis.filter(function (q) { return q.circuit; })) {
            const p = commencer(L, d.slug).piste;
            out.courses[d.slug] = d.tours * p.length * L.TT / d.chrono_s;
            L.Histoire.finirDefi(false, 'JUGE');
        }
        return out;
    }""")
    etalon = r["courses"]["tour"]
    for slug, vitesse in r["courses"].items():
        assert 0.9 * etalon <= vitesse <= etalon, f"{slug} : {vitesse:.0f} px/s exigés, l'étalon en demande {etalon:.0f}"
        assert vitesse <= 0.75 * r["max"], f"{slug} : il faudrait rouler à {vitesse / r['max']:.0%} de la vitesse max"


def test_on_suit_les_fleches_et_on_gagne_sans_point_de_passage(banc):
    r = banc("function (L, o) {" + COMMENCER + """
        L.Jeu.commencer();
        const d = L.B.defs.defis.find(function (q) { return q.slug === 'tour_quais'; });
        d.tours = 1;                                   // un tour suffit à juger
        const f = commencer(L, d.slug), p = f.piste, n = p.length;
        // Au volant, mais pas sur la ligne : le chrono attend.
        const v = auVolant(L, o, p[20].x, p[20].y);
        poser(L, v, { x: p[0].x + 12 * L.TT, y: p[0].y });
        o.frame(3);
        const avant = { ligne: L.Histoire.ligneObjectif(), t: L.B.defi.t, course: L.Histoire.estCourse() };
        // Sur la ligne : GO. Puis on roule le circuit, deux points par image.
        poser(L, v, p[0]);
        o.frame(2);
        const depart = { course: L.Histoire.estCourse(), ecran: L.Hud.marqueurs().ecran, ligne: L.Histoire.ligneObjectif() };
        const argent = L.B.partie.argent;
        let k = 0;
        for (; k <= n + 4 && L.B.defi; k += 2) { poser(L, v, p[k % n]); o.frame(1); }
        return { avant: avant, depart: depart, fini: !L.B.defi, fait: !!L.B.partie.defisFaits[d.slug],
                 gain: L.B.partie.argent - argent, k: k, n: n,
                 apres: { course: L.Histoire.estCourse() } };
    }""")
    assert "REJOINS LA LIGNE DE DÉPART" in r["avant"]["ligne"], r["avant"]
    assert r["avant"]["t"] == 0, "le chrono ne part que sur la ligne de départ"
    assert r["avant"]["course"] is False
    assert r["depart"]["course"] is True
    assert r["depart"]["ecran"] is None, "sur la piste, pas de flèche-et-mètres : les flèches au sol parlent"
    assert "TOUR 1/1" in r["depart"]["ligne"], r["depart"]
    assert r["fini"] and r["fait"], f"un tour entier du circuit, et la course n'est pas gagnée : {r}"
    assert r["k"] >= r["n"], "gagné avant d'avoir bouclé le circuit"
    assert r["gain"] > 0, "la prime n'est pas payée"
    assert r["apres"]["course"] is False


def test_hors_piste_cinq_secondes_pour_revenir_puis_c_est_rate(banc):
    r = banc("function (L, o) {" + COMMENCER + """
        L.Jeu.commencer();
        const f = commencer(L, 'tour_pointe'), p = f.piste;
        const v = auVolant(L, o, p[0].x, p[0].y);
        poser(L, v, p[0]); o.frame(2);
        for (let k = 1; k <= 30; k++) { poser(L, v, p[k]); o.frame(1); }
        // La rue d'à côté — une vraie chaussée, loin de toute la piste (⚠️ pas la baie :
        // un char s'y enfonce, et la course se rate « sans char », pas hors piste).
        let loin = null;
        for (let r = 8; r < 40 && !loin; r++) {
            for (let a = 0; a < 16 && !loin; a++) {
                const q = { x: p[30].x + Math.round(Math.cos(a * Math.PI / 8) * r) * L.TT, y: p[30].y + Math.round(Math.sin(a * Math.PI / 8) * r) * L.TT };
                const tx = Math.floor(q.x / L.TT), ty = Math.floor(q.y / L.TT);
                if (L.Monde.estRoute(tx, ty) && !L.Monde.estEau(tx, ty)
                    && !p.some(function (s) { return Math.hypot(s.x - q.x, s.y - q.y) < 8 * L.TT; })) loin = q;
            }
        }
        // Hors piste : quatre secondes et demie, puis on revient.
        poser(L, v, loin); o.frame(270);
        const presque = { encore: !!L.B.defi, ligne: L.Histoire.ligneObjectif() };
        poser(L, v, p[30]); o.frame(2);
        const revenu = { encore: !!L.B.defi, ligne: L.Histoire.ligneObjectif() };
        // Et cette fois on ne revient pas.
        poser(L, v, loin); o.frame(310);
        return { presque: presque, revenu: revenu, rate: !L.B.defi, fait: !!L.B.partie.defisFaits.tour_pointe, msg: L.B.msg };
    }""")
    assert r["presque"]["encore"], "rattrapé avant les cinq secondes, la course doit continuer"
    assert "REVIENS" in r["presque"]["ligne"], r["presque"]
    assert r["revenu"]["encore"] and "REVIENS" not in r["revenu"]["ligne"], f"revenu sur la piste, le compte s'annule : {r['revenu']}"
    assert r["rate"] and not r["fait"], "cinq secondes hors piste : la course est ratée"
    assert "HORS PISTE" in (r["msg"] or ""), r["msg"]


def test_la_ligne_de_depart_se_voit_des_le_panneau(banc):
    """Le circuit se tire AU PANNEAU : ses flèches sont au sol avant même qu'on ait trouvé un
    char, et le GPS montre la ligne de départ. ⚠️ Et elles sont LUMINEUSES : peintes au sol, la
    nuit les éteignait avec la ville (on ne les voyait plus que dans ses phares) — chaque flèche
    à l'écran pose sa lampe."""
    r = banc("function (L, o) {" + COMMENCER + """
        L.Jeu.commencer();
        const f = commencer(L, 'tour_erables'), p = f.piste;
        L.Monde.centrerCamera(p[0].x, p[0].y);
        const ctx = L.Base.ecran(), vrai = ctx.fill;
        let traits = 0;
        ctx.fill = function () { traits++; return vrai.apply(this, arguments); };
        L.Histoire.dessinerCheminCourse(ctx, { x: L.B.cam.x, y: L.B.cam.y });
        ctx.fill = vrai;
        const c = L.Histoire.cible();
        const lampes = L.Histoire.lampesDeCourse({ x: L.B.cam.x, y: L.B.cam.y });
        return { traits: traits, lampes: lampes.length, cible: c && Math.hypot(c.x - p[0].x, c.y - p[0].y), parti: f.parti };
    }""")
    assert r["parti"] is False
    assert r["traits"] >= 10, f"les flèches de la ligne de départ ne se peignent pas ({r['traits']} traits)"
    assert r["cible"] == 0, "le GPS ne montre pas la ligne de départ"
    assert r["lampes"] * 2 == r["traits"], f"une lampe par flèche peinte (un halo et un trait chacune) : {r}"


def test_les_fleches_restent_fixes_quand_on_avance(banc):
    """Retour de Martin (22 sept. 2026) : « les flèches clignotent quand on avance, il faudrait
    qu'elles restent fixes ». ⚠️ Rouge avant : posées DEPUIS LE CHAR (un point sur deux à partir
    de lui), elles changeaient de parité à chaque tuile et sautaient de 16 px ; et leur lueur
    battait, à une phase lue sur leur rang devant le char.

    La caméra est tenue fixe : d'une image à la suivante, le char avancé d'une tuile, les flèches
    à l'écran sont les MÊMES — même place dans le monde, même lumière —, moins celles qu'on a
    dépassées."""
    r = banc("function (L, o) {" + COMMENCER + """
        L.Jeu.commencer();
        const f = commencer(L, 'tour_quais'), p = f.piste;
        const v = auVolant(L, o, p[0].x, p[0].y);
        poser(L, v, p[0]); o.frame(2);
        const cam = { x: L.B.cam.x, y: L.B.cam.y };
        function fleches() {
            L.B.cam.x = cam.x; L.B.cam.y = cam.y;
            return L.Histoire.lampesDeCourse({ x: cam.x, y: cam.y }).map(function (l) {
                return Math.round(l.x + cam.x) + ',' + Math.round(l.y + cam.y) + ' ' + l.c;
            });
        }
        let avant = fleches();
        const premier = avant.length, sauts = [];
        for (let k = 1; k <= 30; k++) {
            poser(L, v, p[k]); o.frame(1);
            const apres = fleches();
            const bouge = apres.filter(function (q) { return avant.indexOf(q) < 0; });
            if (bouge.length) sauts.push({ k: k, bouge: bouge.slice(0, 2), avant: avant.slice(0, 2) });
            avant = apres;
        }
        return { premier: premier, dernier: avant.length, sauts: sauts.length, exemple: sauts[0] || null, i: L.B.defi.i };
    }""")
    assert r["premier"] >= 5, f"pas assez de flèches à l'écran pour juger : {r}"
    assert r["i"] >= 25, f"le char n'a pas avancé sur la piste : {r}"
    assert r["dernier"] < r["premier"], "on a dépassé des flèches : elles doivent disparaître derrière le char"
    assert r["sauts"] == 0, f"les flèches bougent ou changent de lumière quand on avance ({r['sauts']} images sur 30) : {r['exemple']}"
