"""La garde-robe dessinée : des squelettes qu'on habille, sous le banc Node.

Voir `test_garderobe.py` pour le catalogue.
"""

TOUT = """
    const G = L.Garderobe, D = L.B.defs.garderobe;
    const base = { squelette: 'homme', peau: '#e8b088', cheveux: '#3a2a1a', coiffure: 'courte', chapeau: 'aucun',
                   couleur_chapeau: '#c0392b', haut: 'chandail', couleur_haut: '#2980b9', motif: 'uni', bas: 'pantalon',
                   couleur_bas: '#2a2a3a', souliers: 'souliers', couleur_souliers: '#1a1a1a', accessoires: [], accent: '#e8b33c' };
    const vues = ['bas', 'haut', 'cote'];
    const grilles = function (tn) { return vues.map(function (v) { return G.grille(tn, v, 0).join('\\n'); }).join('\\n\\n'); };
"""


def test_chaque_squelette_se_tient_debout_et_garde_ses_mesures(banc):
    r = banc("""function (L, o) {
        """ + TOUT + """
        const out = {};
        D.squelettes.forEach(function (s) {
            const q = G.squelette(s);
            const tailles = {}, pieds = {};
            Object.keys(q.poses).forEach(function (p) {
                q.poses[p].forEach(function (g) { tailles[g.length + 'x' + g[0].length] = 1; });
            });
            vues.forEach(function (v) { pieds[v] = q.poses[v][0][q.h - 1].join('').replace(/\\./g, '').length > 0; });
            out[s] = { w: q.w, h: q.h, ancre: q.ancre, tailles: Object.keys(tailles), pieds: pieds,
                       poses: Object.keys(q.poses).length, silhouette: grilles(Object.assign({}, base, { squelette: s })) };
        });
        return out;
    }""")
    assert set(r) == {"homme", "femme", "costaud", "vieux", "grand", "enfant"}
    for s, q in r.items():
        assert q["tailles"] == [f"{q['h']}x{q['w']}"], f"{s} : des poses de tailles différentes {q['tailles']}"
        assert q["ancre"][1] == q["h"] - 1 and all(q["pieds"].values()), f"{s} : les pieds ne sont pas sur l'ancre"
    assert r["homme"]["poses"] >= 38, "l'homme garde toutes les poses du joueur (gestes, assis, à vélo…)"
    assert r["grand"]["h"] > r["homme"]["h"], "le grand est plus grand"
    silhouettes = {q["silhouette"] for q in r.values()}
    assert len(silhouettes) == len(r), "deux squelettes ont la même silhouette"


def test_chaque_piece_change_le_dessin_sur_chaque_squelette(banc):
    """Le juge qui mord : une pièce sans effet sur un corps est une pièce invisible."""
    r = banc("""function (L, o) {
        """ + TOUT + """
        const rates = [], inconnues = {};
        const pal = G.palette(base);
        D.squelettes.forEach(function (s) {
            const nu = Object.assign({}, base, { squelette: s });
            const ref = grilles(nu);
            const essai = function (quoi, tn) {
                const g = grilles(tn);
                if (g === ref) rates.push(s + ':' + quoi);
                g.split('').forEach(function (ch) { if (ch !== '.' && ch !== '\\n' && !pal[ch]) inconnues[ch] = quoi; });
            };
            // Un chapeau se voit de face, de dos ET de profil : chaque vue est jugee seule.
            D.chapeaux.filter(function (c) { return c !== 'aucun'; }).forEach(function (c) {
                vues.forEach(function (v) {
                    if (G.grille(Object.assign({}, nu, { chapeau: c }), v, 0).join('') === G.grille(nu, v, 0).join('')) rates.push(s + ':chapeau ' + c + ' ' + v);
                });
            });
            D.coiffures.filter(function (c) { return c !== 'courte'; }).forEach(function (c) { essai('coiffure ' + c, Object.assign({}, nu, { coiffure: c })); });
            D.hauts.filter(function (c) { return c !== 'chandail'; }).forEach(function (c) {
                // Un t-shirt ou une camisole sur un enfant, dont les bras ne depassent pas : pareil.
                if (s === 'enfant' && (c === 'tshirt' || c === 'camisole' || c === 'chemise' || c === 'coton_ouate')) return;
                essai('haut ' + c, Object.assign({}, nu, { haut: c }));
            });
            ['short', 'jupe'].forEach(function (c) { essai('bas ' + c, Object.assign({}, nu, { bas: c })); });
            essai('bottes', Object.assign({}, nu, { souliers: 'bottes' }));
            ['raye', 'carreaute'].forEach(function (m) { essai('motif ' + m, Object.assign({}, nu, { motif: m })); });
            D.accessoires.forEach(function (a) { essai('acc ' + a, Object.assign({}, nu, { accessoires: [a] })); });
        });
        return { rates: rates, inconnues: inconnues };
    }""")
    assert not r["inconnues"], f"lettres sans couleur : {r['inconnues']}"
    # L'enfant n'a que trois poses et une tête de dix pixels : la jupe courte ne se voit pas.
    assert not [x for x in r["rates"] if not x.startswith("enfant:bas")], r["rates"]


def test_un_chapeau_se_pose_sur_la_tete_dans_chaque_vue_et_chaque_pose_debout(banc):
    r = banc("""function (L, o) {
        """ + TOUT + """
        const q = G.squelette('homme'), sans = {};
        Object.keys(q.poses).forEach(function (p) {
            if (!G.vueDe(p)) return;
            const g = G.grille(Object.assign({}, base, { chapeau: 'tuque' }), p, 0).join('');
            if (g.indexOf('t') < 0) sans[p] = true;
        });
        const couche = G.grille(Object.assign({}, base, { chapeau: 'tuque' }), 'couche', 0).join('');
        return { sans: Object.keys(sans), couche: couche.indexOf('t') >= 0 };
    }""")
    assert r["sans"] == [], f"la tuque tombe dans : {r['sans']}"
    assert r["couche"] is False, "couché, le chapeau tombe"


def test_les_passants_s_habillent_sans_tirer_un_seul_de(banc):
    """Chaque passant ordinaire porte une tenue à lui, tirée à l'EMPREINTE de son id : la
    ville tire exactement les mêmes dés qu'avant (`B.rng`)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const E = L.Entites, B = L.B;
        const arch = B.defs.pietons.catalogue ? null : null;
        const archs = (B.defs.pietons.catalogue || B.defs.pietons.archetypes || B.defs.pietons);
        const liste = Array.isArray(archs) ? archs : [];
        const passant = liste.find(function (a) { return a.slug === 'passant'; });
        const mesure = function (avec) {
            const garde = L.Garderobe.tirer;
            if (!avec) L.Garderobe.tirer = function () { return null; };
            L.graine(4242);
            const nes = [];
            for (let i = 0; i < 40; i++) nes.push(E.creerPieton(B.joueur.x + 400 + i, B.joueur.y + 400, passant));
            const suite = B.rng();
            L.Garderobe.tirer = garde;
            return { suite: suite, nes: nes };
        };
        const sans = mesure(false), avec = mesure(true);
        const tenues = avec.nes.map(function (e) { return JSON.stringify(e.tenue); });
        const img = E.imageDe ? E.imageDe(avec.nes[0]) : null;
        return { memeDe: sans.suite === avec.suite, habilles: avec.nes.filter(function (e) { return !!e.tenue; }).length,
                 differentes: new Set(tenues).size, chapeaux: avec.nes.filter(function (e) { return e.tenue && e.tenue.chapeau !== 'aucun'; }).length,
                 swaps: avec.nes.every(function (e) { return e.swaps.c === e.tenue.couleur_haut; }),
                 image: img ? { w: img.canvas.width, h: img.canvas.height } : null, trouve: !!passant };
    }""")
    assert r["trouve"]
    assert r["memeDe"], "s'habiller a tiré un dé : la ville se décale"
    assert r["habilles"] == 40 and r["differentes"] >= 35, r
    assert r["chapeaux"] >= 5, "un passant sur trois a un chapeau, à peu près"
    assert r["swaps"], "les couleurs de rue suivent la tenue"


def test_les_donneurs_portent_leur_tenue_et_le_cache_reste_borne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const G = L.Garderobe;
        const b = L.Histoire.donneur('bouchard') || null, t = L.Histoire.donneur('ti_guy');
        G.vider();
        for (let i = 0; i < 600; i++) {
            const tn = G.tirer('passant', i * 2654435761 >>> 0);
            const c = G.cuire(tn);
            if (i % 50 === 0) c.poses.bas;
        }
        return { tiGuy: t && t.tenue ? t.tenue.squelette : null, tiGuyChapeau: t && t.tenue ? t.tenue.chapeau : null,
                 taille: G.taille, max: G.CACHE_MAX };
    }""")
    assert r["tiGuy"] == "costaud"
    assert r["taille"] <= r["max"], "le cache des tenues grossit sans borne"


def test_le_joueur_achete_un_chapeau_le_porte_par_dessus_son_linge_et_l_enleve(banc):
    """Chez Rosa, un chapeau se met SUR la tête sans changer le linge ; le reporter l'enlève ;
    et en changer fait oublier ta tête à la police, comme le linge."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, p = B.partie, j = B.joueur, M = L.Missions;
        p.argent = 1000;
        let oublis = 0; const vrai = L.Police.onNeTeReconnaitPlus;
        L.Police.onNeTeReconnaitPlus = function () { oublis++; return vrai.apply(null, arguments); };
        const menu = M.menuVetements();
        const titres = menu.items.filter(function (i) { return i.entete; }).map(function (i) { return i.entete; });
        const achat = function (slug) {
            const t = B.defs.tenues.find(function (x) { return x.slug === slug; });
            const it = M.menuVetements().items.find(function (i) { return i.libelle === t.nom.toUpperCase(); });
            it.faire();
        };
        const avant = j.tenue ? j.tenue.chapeau : null;
        achat('complet');
        achat('feutre');
        const coiffe = { chapeau: j.tenue.chapeau, haut: j.tenue.haut, cravate: j.tenue.accessoires.indexOf('cravate') >= 0,
                         linge: p.tenue, sur: p.chapeau, argent: p.argent,
                         dessine: L.Garderobe.grille(j.tenue, 'bas', 0).join('').indexOf('t') >= 0,
                         image: L.Entites.imageDe(j).canvas.width };
        achat('feutre');
        const retire = { chapeau: j.tenue.chapeau, sur: p.chapeau, linge: p.tenue };
        L.Police.onNeTeReconnaitPlus = vrai;
        return { titres: titres, avant: avant, coiffe: coiffe, retire: retire, oublis: oublis };
    }""")
    assert r["titres"] == ["LE LINGE", "LES CHAPEAUX"]
    assert r["avant"] == "aucun"
    c = r["coiffe"]
    assert c["chapeau"] == "feutre" and c["sur"] == "feutre" and c["linge"] == "complet"
    assert c["haut"] == "veston" and c["cravate"], "le complet est un veston et une cravate"
    assert c["dessine"] and c["image"] == 16, "le joueur se dessine habillé"
    assert c["argent"] == 1000 - 500 - 150
    assert r["retire"] == {"chapeau": "aucun", "sur": None, "linge": "complet"}, "le reporter l'enlève"
    assert r["oublis"] == 3, "chaque changement (linge, chapeau, chapeau enlevé) fait oublier ta tête"


def test_une_vieille_sauvegarde_qui_portait_la_casquette_comme_linge(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const t = L.Garderobe.duJoueur({ tenue: 'casquette_foire', chapeau: null, cheveux: null }, L.B.defs);
        const s = L.apparenceDuJoueur ? null : null;
        return { chapeau: t.chapeau, couleur: t.couleur_chapeau, haut: t.haut, torse: t.couleur_haut };
    }""")
    assert r == {"chapeau": "casquette", "couleur": "#e8a33a", "haut": "chandail", "torse": "#c0392b"}


def test_le_cavalier_se_dessine_habille_et_les_agents_portent_le_kepi(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, V = L.Vehicules;
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        B.partie.tenues.push('tuque'); L.Missions.porterTenue('tuque');
        const v = V.creer('moto', j.x + 10, j.y, 0, {});
        V.monter(j, v);
        const tn = V.tenueDuCavalier(v);
        const img = V.imageDuCavalier(L.SPRITES[v.sprite], v, V.cavalierDe(v), tn);
        const agents = [];
        for (let i = 0; i < 12; i++) {
            const a = L.Police.creerAgent(j.x + 300, j.y + 300 + i, 'flane', i % 3 === 0 ? 'garde' : null);
            agents.push({ garde: a.metier === 'garde', chapeau: a.tenue && a.tenue.chapeau, haut: a.tenue && a.tenue.couleur_haut });
        }
        return { chapeau: tn && tn.chapeau, largeur: img && img.canvas.width, agents: agents };
    }""")
    assert r["chapeau"] == "tuque" and r["largeur"] == 16, "sur la moto, le joueur garde sa tuque"
    flics = [a for a in r["agents"] if not a["garde"]]
    gardes = [a for a in r["agents"] if a["garde"]]
    assert flics and all(a["chapeau"] == "kepi" and a["haut"] == "#1f3a6e" for a in flics), flics
    assert gardes and all(a["haut"] == "#5a5f47" for a in gardes), gardes
