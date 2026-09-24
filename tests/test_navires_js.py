"""Deux bateaux de plus, côté navigateur : le chalutier et le porte-conteneurs
naissent à leur mouillage hors champ — par leur BOUT, pas par leur centre —, on y
monte depuis le quai au bouton, et le porte-conteneurs sort de son bassin en avant,
sans racler une jetée. Et une coque de dix tuiles se dégage à sa propre échelle."""

# Ce qui sert à tous : couper le trafic, vider les grands bateaux, poser le joueur.
PRELUDE = """
    L.Jeu.commencer();
    L.B.defs.conduite.trafic.vehicules_max = 0;
    const j = L.B.joueur, TT = L.TT, mouillages = L.Monde.carte.def.mouillages;
    function grands() {
        return L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.amarrage && e.amarrage.slug; });
    }
    function vider() { grands().forEach(function (e) { L.Entites.retirer(e); }); }
    function poser(x, y) { j.x = x; j.y = y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer(); }
    // ⚠️ Les coques naissent dans `peupler`, qui ne tourne qu'une image sur vingt :
    // trois images de banc ne voyaient rien passer, et « rien ne nait » etait vert a vide.
    const TOUR = 21;
    // La demi-etendue de la coque sur l'axe nord-sud, a son cap.
    function demiY(m) {
        const d = L.Vehicules.vehiculeDef(m.slug);
        return Math.abs(Math.sin(m.angle)) * d.longueur / 2 + Math.abs(Math.cos(m.angle)) * d.largeur / 2;
    }
"""


def test_les_grands_bateaux_naissent_a_quai_hors_champ_par_leur_bout(banc):
    """⚠️ **Hors champ par son BOUT.** La règle des chaloupes (le centre à 24 px du
    bord) laissait naître un porte-conteneurs la poupe déjà à l'écran : 160 px de
    coque qui apparaissent d'un coup. On pose la caméra pour que le centre soit
    hors champ et le bout dedans : rien ne naît ; on recule, il naît — à sa place, à
    son cap, d'une couleur de sa fiche, et libre des tuiles."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const m = mouillages.find(function (q) { return q.slug === 'porte_conteneurs'; });
        vider();
        // Au nord de la coque, le bout le plus proche a 20 px au-dessus du bas de l'ecran.
        poser(m.x + 144, m.y - demiY(m) + 20 - L.VH / 2);
        const avant = { bout: L.Entites.visibleAEcran(m.x, m.y - demiY(m) + 4, 0),
                        centre24: L.Entites.visibleAEcran(m.x, m.y, 24) };
        o.frame(TOUR);
        const cache = grands().filter(function (e) { return e.amarrage === m; }).length;
        vider();
        poser(m.x + 144, m.y - demiY(m) - 60 - L.VH / 2);
        o.frame(TOUR);
        const nes = grands().filter(function (e) { return e.amarrage === m; });
        const v = nes[0];
        // Et chacun des autres, de loin, a son mouillage.
        const tous = mouillages.map(function (q) {
            vider();
            poser(q.x + 144, q.y - demiY(q) - 60 - L.VH / 2);
            o.frame(TOUR);
            const n = grands().filter(function (e) { return e.amarrage === q; });
            return { slug: q.slug, nes: n.length, sien: n.length ? n[0].slug : null,
                     bloque: n.length ? L.Vehicules.bloqueParLesTuiles(n[0], n[0].x, n[0].y) : null };
        });
        return { avant: avant, cache: cache, nes: nes.length,
                 v: v && { slug: v.slug, x: v.x, y: v.y, angle: v.angle, etat: v.etat, couleur: v.couleur,
                           bloque: L.Vehicules.bloqueParLesTuiles(v, v.x, v.y) },
                 m: m, couleurs: L.Vehicules.vehiculeDef('porte_conteneurs').couleurs, tous: tous };
    }""")
    assert r["avant"]["bout"] and not r["avant"]["centre24"], f"le décor du juge est faux : {r['avant']}"
    assert r["cache"] == 0, "le porte-conteneurs est né la poupe à l'écran"
    assert r["nes"] == 1, "le porte-conteneurs n'est pas né à son mouillage"
    v, m = r["v"], r["m"]
    assert (v["slug"], v["x"], v["y"], v["angle"], v["etat"]) == ("porte_conteneurs", m["x"], m["y"], m["angle"], "stationne"), v
    assert v["couleur"] in r["couleurs"]
    assert v["bloque"] is False, "le porte-conteneurs naît dans le quai"
    assert [t["slug"] for t in r["tous"]] == ["porte_conteneurs", "chalutier", "chalutier"], r["tous"]
    for t in r["tous"]:
        assert t["nes"] == 1 and t["sien"] == t["slug"], f"{t['slug']} n'est pas né à son mouillage : {t}"
        assert t["bloque"] is False, f"{t['slug']} naît dans le quai"


def test_on_monte_depuis_le_quai_et_le_cargo_sort_de_son_bassin(banc):
    """⚠️ **Au bouton, depuis le quai** : on se tient sur la jetée, tourné vers la
    coque, on appuie sur ACTION — et plein gaz, le porte-conteneurs file dans son
    chenal, dans le sens de son cap, sur une longueur de coque au moins, sans
    toucher une jetée (aucun dégagement), sans couler, sans cornes de travers."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const m = mouillages.find(function (q) { return q.slug === 'porte_conteneurs'; });
        vider();
        poser(m.x + 144, m.y - demiY(m) - 60 - L.VH / 2);
        o.frame(TOUR);
        const v = grands().find(function (e) { return e.amarrage === m; });
        // La tuile de quai la plus proche de la coque, d'ou l'on monte.
        let quai = null, dMin = Infinity;
        const cercles = L.Vehicules.cercles(v);
        for (let ty = Math.floor(m.y / TT) - 8; ty <= Math.floor(m.y / TT) + 8; ty++) {
            for (let tx = Math.floor(m.x / TT) - 8; tx <= Math.floor(m.x / TT) + 8; tx++) {
                if (L.Monde.glyphe(tx, ty) !== 'Q') continue;
                const x = tx * TT + 8, y = ty * TT + 8;
                cercles.forEach(function (c) {
                    const d = Math.hypot(c.x - x, c.y - y) - c.r;
                    if (d < dMin) { dMin = d; quai = { x: x, y: y, c: c }; }
                });
            }
        }
        poser(quai.x, quai.y);
        o.viser(quai.c);
        o.tape('KeyE', 2);
        const monte = j.dansVehicule === v, klaxon = v.def.klaxon;
        const x0 = v.x, y0 = v.y, longueur = v.def.longueur;
        o.touche('KeyW');
        let n = 0;
        while (n < 1200 && Math.hypot(v.x - x0, v.y - y0) < longueur + 16) { o.frame(1); n++; }
        o.relacher('KeyW');
        const parcouru = Math.hypot(v.x - x0, v.y - y0);
        return { monte: monte, klaxon: klaxon, quai: dMin, parcouru: parcouru, images: n, longueur: longueur,
                 sens: ((v.x - x0) * Math.cos(m.angle) + (v.y - y0) * Math.sin(m.angle)) / Math.max(1, parcouru),
                 eau: L.Monde.estEau(Math.floor(v.x / TT), Math.floor(v.y / TT)),
                 coule: v.coule || 0, etat: v.etat, degagements: v.degagements || 0,
                 vie: v.vie, vieMax: v.vieMax };
    }""")
    assert r["quai"] <= 30, f"le décor du juge est faux : le quai le plus proche est à {r['quai']} px de la coque"
    assert r["monte"], "on ne monte pas dans le porte-conteneurs depuis le quai"
    assert r["klaxon"] == "corne"
    assert r["parcouru"] >= r["longueur"], f"il n'a fait que {r['parcouru']:.0f} px en {r['images']} images"
    assert r["sens"] > 0.9, f"il ne suit pas son chenal (sens {r['sens']:.2f})"
    assert r["eau"] and r["coule"] == 0 and r["etat"] != "epave", r
    assert r["degagements"] == 0, "il a raclé une jetée en sortant (le garde-fou l'a dégagé)"
    assert r["vie"] == r["vieMax"], f"il a touché quelque chose en sortant : {r['vie']} / {r['vieMax']}"


def test_une_coque_se_degage_a_sa_propre_echelle(banc):
    """⚠️ Le garde-fou cherchait une place libre à six tuiles au plus (`degagement_px`)
    — assez pour tout ce qui roule en ville, pas pour dix tuiles de coque. Un
    porte-conteneurs posé sur le quai, à cent huit pixels de l'eau où il tient, en
    sort — et pas plus loin que sa propre longueur."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const ph = L.B.defs.conduite.physique;
        // Une rangee de quai dont les rangees d'eau commencent juste au sud, sur
        // toute la longueur d'un porte-conteneurs couche.
        const def = L.Vehicules.vehiculeDef('porte_conteneurs');
        const demi = Math.ceil(def.longueur / 2 / TT) + 1;
        let place = null;
        const c = L.Monde.carte;
        for (let ty = 8; ty < c.h - 6 && !place; ty++) {
            for (let tx = demi + 2; tx < c.w - demi - 2 && !place; tx++) {
                let ok = true;
                for (let dx = -demi; dx <= demi && ok; dx++) {
                    for (let dy = -6; dy <= -1 && ok; dy++) if (L.Monde.glyphe(tx + dx, ty + dy) !== 'Q') ok = false;
                    for (let dy = 0; dy <= 3 && ok; dy++) if (!L.Monde.estEau(tx + dx, ty + dy)) ok = false;
                }
                if (ok) place = { tx: tx, ty: ty };
            }
        }
        if (!place) return { place: null };
        poser(place.tx * TT + 8, (place.ty - 12) * TT);
        // Le centre sur le quai, a 108 px au nord de la premiere place ou la coque tient.
        const y = place.ty * TT + def.largeur / 2 + 4 - 108;
        const v = L.Vehicules.creer('porte_conteneurs', place.tx * TT + 8, y, 0, { etat: 'stationne' });
        L.Entites.indexer();
        const coince = L.Vehicules.bloqueParLesTuiles(v, v.x, v.y);
        const bouge = L.Vehicules.degager(v);
        return { place: place, portee: ph.degagement_px, coince: coince, bouge: bouge,
                 libre: !L.Vehicules.bloqueParLesTuiles(v, v.x, v.y), dy: v.y - y };
    }""")
    assert r["place"], "le décor du juge est faux : pas de quai droit au bord de l'eau"
    assert r["coince"], "le décor du juge est faux : le porte-conteneurs n'est pas coincé"
    assert r["portee"] < 108, "le décor du juge est faux : la portée ordinaire suffit déjà"
    assert r["bouge"] and r["libre"], "le porte-conteneurs reste pris dans le quai"
    assert 0 < r["dy"] <= 160, f"dégagé de {r['dy']} px : ce n'est plus un dégagement"
