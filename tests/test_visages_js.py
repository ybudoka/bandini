"""Les visages des dialogues, dessinés : chaque portrait se peint, bouge et tient dans la boîte.

Voir `tests/test_visages.py` pour les fiches ; ici, `static/js/visages.js` et la boîte de
dialogue (`Hud.dialogue`) sous le banc Node.
"""


def test_chaque_visage_se_peint_avec_sa_palette_et_chaque_humeur_change_la_mine(banc, paquet):
    r = banc("""function (L, o) {
        const V = L.Visages, sortie = {};
        Object.keys(L.B.defs.visages).forEach(function (slug) {
            const pal = V.palette(L.B.defs.visages[slug]);
            const mines = {}, inconnues = [];
            V.HUMEURS.forEach(function (h) {
                const g = V.grille(L.B.defs.visages[slug], h, 0, false, slug);
                g.join('').split('').forEach(function (ch) { if (ch !== '.' && !pal[ch]) inconnues.push(ch); });
                mines[h] = g.join('\\n');
            });
            const parle = [1, 2].map(function (b) { return V.grille(L.B.defs.visages[slug], 'neutre', b, false, slug).join('\\n'); });
            const clin = V.grille(L.B.defs.visages[slug], 'neutre', 0, true, slug).join('\\n');
            sortie[slug] = { mines: mines, parle: parle, clin: clin, inconnues: inconnues,
                             cuit: !!V.cuire(slug, 'content', 0, false), taille: V.grille(L.B.defs.visages[slug], 'neutre', 0, false, slug).length };
        });
        return sortie;
    }""")
    assert set(r) == set(paquet["visages"])
    neutres = {}
    for slug, v in r.items():
        assert not v["inconnues"], f"{slug} : lettres sans couleur {set(v['inconnues'])}"
        assert v["cuit"] and v["taille"] == 40
        mines = v["mines"]
        assert len(set(mines.values())) >= 8, f"{slug} : trop d'humeurs se ressemblent"
        assert mines["content"] != mines["neutre"] and mines["fache"] != mines["neutre"]
        assert v["parle"][0] != mines["neutre"] and v["parle"][1] != v["parle"][0], f"{slug} : la bouche ne bouge pas"
        assert v["clin"] != mines["neutre"], f"{slug} : il ne cligne pas"
        neutres.setdefault(mines["neutre"], []).append(slug)
    doublons = [s for s in neutres.values() if len(s) > 1]
    assert not doublons, f"même portrait pour {doublons}"


def test_la_replique_montre_le_visage_de_qui_parle_avec_sa_mine(banc, paquet, dialogues):
    """La première réplique de Ti-Guy : son portrait, à gauche, et le texte poussé à droite."""
    humeur = next((r.get("humeur") for r in dialogues["m1"]["dialogue"]["intro"] if r["qui"] == "ti_guy"), None)
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, t = L.Histoire.donneur('ti_guy');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        o.viser(t);
        L.Missions.majInvite(j);
        L.Missions.interagir(j);
        const d = L.B.dialogue;
        const dessins = [], vrai = L.Visages.dessiner;
        L.Visages.dessiner = function (c, slug, x, y, h, tt, parle) { dessins.push({ slug: slug, x: x, y: y, humeur: h }); return vrai.apply(null, arguments); };
        L.Hud.dessiner();
        return { visage: d && d.visage, qui: d && d.qui, dessins: dessins };
    }""")
    assert r["visage"]["slug"] == "ti_guy"
    assert r["visage"]["humeur"] == (humeur or "neutre")
    assert r["dessins"] and r["dessins"][0]["slug"] == "ti_guy" and r["dessins"][0]["x"] == 16


def test_la_boite_grandit_pour_le_portrait_et_pousse_le_texte(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const mesure = function (visage) {
            L.Hud.dialogue('Ti-Guy', ['UNE LIGNE.'], 0, visage);
            const traces = o.ctx.traces = [];
            L.Hud.dessiner();
            o.ctx.traces = null;
            const boite = traces.find(function (t) { return t[4].indexOf('rgba(11,10,18') === 0; });
            const portrait = traces.filter(function (t) { return t[2] === 42 && t[3] === 42; });
            return { boite: boite, portrait: portrait.length, visage: !!L.B.dialogue.visage };
        };
        return { avec: mesure({ slug: 'ti_guy', humeur: 'content' }), sans: mesure(null),
                 inconnu: mesure({ slug: 'personne', humeur: 'fache' }) };
    }""")
    avec, sans = r["avec"], r["sans"]
    assert avec["visage"] and avec["portrait"] == 1
    assert avec["boite"][3] >= 50, "la boîte tient les 42 pixels du cadre"
    assert avec["boite"][1] + avec["boite"][3] == sans["boite"][1] + sans["boite"][3], "le bas de la boîte ne bouge pas"
    assert sans["portrait"] == 0 and not sans["visage"]
    assert not r["inconnu"]["visage"] and r["inconnu"]["portrait"] == 0, "un slug sans visage garde la boîte d'avant"


def test_la_bouche_bouge_le_temps_de_dire_puis_se_tait(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Son.Voix.couper();
        L.Hud.dialogue('Marco', ['COUSIN.'], 0, { slug: 'marco', humeur: 'neutre' });
        const d = L.B.dialogue, vu = [];
        const vrai = L.Visages.dessiner;
        L.Visages.dessiner = function (c, slug, x, y, h, t, parle) { vu.push(parle); return vrai.apply(null, arguments); };
        for (let i = 0; i < 60; i++) L.Hud.dessiner();
        // Avec une voix : la bouche suit la voix, pas le texte.
        L.Hud.dialogue('Marco', ['COUSIN.'], 0, { slug: 'marco', humeur: 'neutre' });
        L.B.dialogue.voix = true;
        L.Son.Voix.enCours = { slug: 'x' };
        const pendant = []; L.Visages.dessiner = function (c, s, x, y, h, t, parle) { pendant.push(parle); return true; };
        for (let i = 0; i < 60; i++) L.Hud.dessiner();
        L.Son.Voix.enCours = null;
        const apres = []; L.Visages.dessiner = function (c, s, x, y, h, t, parle) { apres.push(parle); return true; };
        L.Hud.dessiner();
        return { vu: vu, pendant: pendant, apres: apres };
    }""")
    assert r["vu"][0] is True and r["vu"][-1] is False, "sans voix : le temps du texte, puis la bouche se ferme"
    assert all(r["pendant"]), "tant que la voix joue, la bouche bouge"
    assert r["apres"] == [False]
