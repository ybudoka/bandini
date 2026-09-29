"""La garde-robe des saisons (les quatre saisons, vague 4a ; `Saisons.vetir`, `Saisons.parapluie`) : la
tenue TIRÉE d'un passant ne change pas, c'est son image qui s'habille — manteau, bottes et tuque
l'hiver, t-shirt et short l'été, le parapluie sous la pluie. Une pure fonction de la tenue, du froid du
moment et de la pluie : aucun dé, rien de sauvé."""

#: Des tenues de rue de tout le monde, tirées comme la ville les tire (à l'empreinte), et l'habit du moment.
TIRER = """
    const ARCHS = ['passant', 'passante', 'ado', 'dame', 'banlieusard', 'promeneur', 'livreur', 'mere', 'itinerant'];
    function monde(L, n) {
        const out = [];
        for (let i = 0; i < n; i++) {
            const arch = ARCHS[i % ARCHS.length], tn = L.Garderobe.tirer(arch, L.hash2(i, 0x7e4e));
            out.push({ arch: arch, tn: tn, e: { arch: arch, type: 'pieton', tenue: tn } });
        }
        return out;
    }
    function habits(L, gens) { return gens.map(function (g) { return L.Saisons.vetir(g.tn, g.e); }); }
    function part(liste, f) { return liste.filter(f).length / liste.length; }
"""


def test_janvier_en_manteau_bottes_et_tuque_juillet_en_t_shirt(banc):
    r = banc("function (L) {" + TIRER + """
        L.Jeu.commencer();
        const p = L.B.partie, gens = monde(L, 360), H = L.B.defs.saisons.habits;
        const metier = function (h) { return H.hauts_de_metier.indexOf(h) >= 0; };
        p.jour = 2; p.heure = 0.5;
        const jan = habits(L, gens);
        p.jour = 21; p.heure = 0.5;
        while (L.Pluie.intensite() > 0) p.jour++;
        const juil = habits(L, gens);
        return {
            janManteau: part(jan.filter(function (t, i) { return !metier(gens[i].tn.haut); }), function (t) { return t.haut === 'manteau'; }),
            janBottes: part(jan, function (t) { return t.souliers === 'bottes'; }),
            janShort: part(jan, function (t) { return t.bas === 'short'; }),
            janNuTete: part(jan.filter(function (t, i) { return H.chapeau_d_uniforme.indexOf(gens[i].arch) < 0; }),
                            function (t) { return H.chapeaux_chauds.indexOf(t.chapeau) < 0; }),
            janTuque: part(jan, function (t) { return t.chapeau === 'tuque'; }),
            janFoulard: part(jan, function (t) { return t.accessoires.indexOf('foulard') >= 0; }),
            juilManteau: part(juil, function (t) { return t.haut === 'manteau'; }),
            juilTuque: part(juil, function (t) { return t.chapeau === 'tuque' || t.chapeau === 'capuche'; }),
            juilShort: part(juil, function (t) { return t.bas === 'short'; }),
            juilTshirt: part(juil, function (t) { return t.haut === 'tshirt'; }),
            juilFoulard: part(juil, function (t) { return t.accessoires.indexOf('foulard') >= 0; }),
            avantManteau: part(gens, function (g) { return g.tn.haut === 'manteau'; }),
            avantShort: part(gens, function (g) { return g.tn.bas === 'short'; }),
        };
    }""")
    assert r["janManteau"] == 1, f"en janvier, {1 - r['janManteau']:.0%} des passants sans manteau"
    assert r["janBottes"] == 1 and r["janShort"] == 0 and r["janNuTete"] == 0
    assert r["janTuque"] > 0.6 and 0.3 < r["janFoulard"] < 0.9
    assert r["juilManteau"] == 0 and r["juilTuque"] == 0 and r["juilFoulard"] == 0
    assert r["juilShort"] > r["avantShort"] + 0.05, "pas plus de shorts en juillet que dans le tirage"
    assert r["juilTshirt"] > 0.3
    assert r["avantManteau"] > 0.05, "le tirage n'a plus de manteaux : le juge ne mord plus"


def test_l_uniforme_et_le_gang_gardent_leur_couleur_et_leur_chapeau(banc):
    r = banc("function (L) {" + TIRER + """
        L.Jeu.commencer();
        const p = L.B.partie, out = {};
        ['policier', 'mante', 'garde', 'skateux', 'morue', 'cravate'].forEach(function (arch) {
            const liste = [];
            for (let i = 0; i < 40; i++) {
                const tn = L.Garderobe.tirer(arch, L.hash2(i, 77)), e = { arch: arch, type: 'pieton', tenue: tn };
                p.jour = 2; const h = L.Saisons.vetir(tn, e);
                p.jour = 21; const e2 = L.Saisons.vetir(tn, e);
                liste.push({ c: [tn.couleur_haut, h.couleur_haut, e2.couleur_haut], ch: [tn.chapeau, h.chapeau], haut: [tn.haut, h.haut] });
            }
            out[arch] = liste;
        });
        return out;
    }""")
    for arch, liste in r.items():
        for t in liste:
            assert t["c"][0] == t["c"][1] == t["c"][2], f"{arch} change de couleur avec la saison"
    for t in r["policier"]:
        assert t["ch"] == ["kepi", "kepi"] and t["haut"][1] == "manteau", "l'agent perd son képi ou gèle en chemise"
    for t in r["mante"]:
        assert t["haut"] == ["veste_kungfu", "veste_kungfu"] and t["ch"][1] in ("aucun", "bandana")
        assert t["ch"][0] == t["ch"][1], "une Mante en tuque"


def test_une_pure_fonction_sans_de_qui_ne_touche_pas_la_tenue(banc):
    r = banc("function (L) {" + TIRER + """
        L.Jeu.commencer();
        const p = L.B.partie, gens = monde(L, 120);
        const avant = JSON.stringify(gens.map(function (g) { return g.tn; }));
        let des = 0; const rng = L.B.rng; L.B.rng = function () { des++; return rng(); };
        p.jour = 2; const a = habits(L, gens), b = habits(L, gens);
        p.jour = 21; habits(L, gens); p.jour = 33; habits(L, gens);
        L.B.rng = rng;
        p.jour = 2;
        const dedans = (function () { L.B.interieur = { slug: 'x' }; const t = L.Saisons.vetir(gens[2].tn, gens[2].e); L.B.interieur = null; return t; })();
        return { des: des, touche: avant !== JSON.stringify(gens.map(function (g) { return g.tn; })),
                 memes: a.every(function (t, i) { return t === b[i]; }),
                 dedans: dedans === gens[2].tn, dehors: L.Saisons.vetir(gens[2].tn, gens[2].e) !== gens[2].tn };
    }""")
    assert r["des"] == 0, f"{r['des']} dés tirés pour habiller la ville"
    assert not r["touche"], "la tenue tirée a été modifiée"
    assert r["memes"], "le même moment ne rend pas le même habit (la cuisson recommencerait à chaque image)"
    assert r["dedans"] and r["dehors"], "dedans, on garde son manteau (ou dehors, on ne s'habille plus)"


def test_les_personnages_et_le_joueur_s_habillent_dehors_dans_leur_palette(banc):
    """Vague 4c (Martin : « il change juste à l'extérieur ») : en janvier, DEHORS, Marco, Josée, Irène, le
    maître… et le joueur enfilent un manteau de LEUR couleur, des bottes et une tuque de la couleur de leur
    bas ; dedans, et l'été, leur tenue de tous les jours, telle quelle. Aucun dé."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie, H = L.B.defs.saisons.habits, persos = L.B.defs.garderobe.personnages;
        let des = 0; const rng = L.B.rng; L.B.rng = function () { des++; return rng(); };
        const gens = Object.keys(persos).map(function (slug) {
            return { slug: slug, tn: persos[slug], e: { type: 'pieton', personnage: slug, arch: 'perso_' + slug, tenue: persos[slug] } };
        });
        gens.push({ slug: 'joueur', tn: L.B.joueur.tenue, e: L.B.joueur });
        const vetir = function () { return gens.map(function (g) { return L.Saisons.vetir(g.tn, g.e); }); };
        p.jour = 2; p.heure = 0.5; while (L.Pluie.intensite() > 0) p.heure += 0.02;
        const jan = vetir();
        L.B.interieur = { slug: 'x' }; const dedans = vetir(); L.B.interieur = null;
        p.jour = 21; p.heure = 0.5; while (L.Pluie.intensite() > 0) p.jour++;
        const juil = vetir();
        L.B.rng = rng;
        return { des: des, n: gens.length, slugs: gens.map(function (g) { return g.slug; }),
                 jan: jan.map(function (t, i) {
                     const tn = gens[i].tn;
                     return { slug: gens[i].slug, haut: t.haut, metier: H.hauts_de_metier.indexOf(tn.haut) >= 0,
                              c: [tn.couleur_haut, t.couleur_haut], chapeau: [tn.chapeau, t.chapeau], chaud: H.chapeaux_chauds.indexOf(t.chapeau) >= 0,
                              tuque: t.couleur_chapeau, bas: tn.couleur_bas, bottes: t.souliers === 'bottes' };
                 }),
                 dedans: dedans.every(function (t, i) { return t === gens[i].tn; }),
                 juil: juil.filter(function (t, i) { return t !== gens[i].tn; }).map(function (t) { return t.haut; }) };
    }""")
    assert r["des"] == 0
    assert "joueur" in r["slugs"] and {"marco", "josee", "irene"} <= set(r["slugs"]), r["slugs"]
    for t in r["jan"]:
        assert t["metier"] or t["haut"] == "manteau", f"{t['slug']} gèle en {t['haut']} en janvier"
        assert t["c"][0] == t["c"][1], f"{t['slug']} n'a plus sa couleur (un manteau foncé de passant)"
        assert t["chaud"] and t["bottes"], f"{t['slug']} nu-tête ou en souliers en janvier : {t['chapeau']}"
        if t["chapeau"][0] != "tuque" and t["chapeau"][1] == "tuque":
            assert t["tuque"] == t["bas"], f"la tuque de {t['slug']} n'est pas dans sa palette"
    assert sum(t["chapeau"][1] == "tuque" for t in r["jan"]) >= 3
    assert r["dedans"], "dedans, un personnage ou le joueur garde son manteau"
    assert r["juil"] == [], f"l'été, un personnage change de tenue : {r['juil']}"


def test_les_manteaux_d_hiver_sont_foncés_et_variés(banc):
    """Vague 4c (Martin : « des manteaux d'hiver de vraies couleurs ») : en janvier, une bonne part des
    passants porte un manteau foncé de la liste (marine, noir, bourgogne, forêt, brun…), les autres la
    couleur de leur haut ; à l'empreinte, jamais au dé."""
    r = banc("function (L) {" + TIRER + """
        L.Jeu.commencer();
        const p = L.B.partie, gens = monde(L, 400), M = L.B.defs.saisons.habits.manteaux;
        p.jour = 2; p.heure = 0.5;
        const jan = habits(L, gens);
        const foncés = jan.filter(function (t, i) { return t.haut === 'manteau' && M.couleurs.indexOf(t.couleur_haut) >= 0 && t.couleur_haut !== gens[i].tn.couleur_haut; });
        const repris = jan.filter(function (t, i) { return t.haut === 'manteau' && t.couleur_haut === gens[i].tn.couleur_haut; });
        const sortes = {}; foncés.forEach(function (t) { sortes[t.couleur_haut] = 1; });
        p.jour = 21; while (L.Pluie.intensite() > 0) p.jour++;
        const juil = habits(L, gens);
        return { foncés: foncés.length / jan.length, repris: repris.length / jan.length, sortes: Object.keys(sortes).length,
                 n: M.couleurs.length, sombres: M.couleurs.every(function (c) { return parseInt(c.substr(1, 2), 16) + parseInt(c.substr(3, 2), 16) + parseInt(c.substr(5, 2), 16) < 3 * 0x70; }),
                 juilFoncés: juil.filter(function (t, i) { return t.couleur_haut !== gens[i].tn.couleur_haut; }).length };
    }""")
    assert 0.45 < r["foncés"] < 0.85, f"{r['foncés']:.0%} de manteaux foncés"
    assert r["repris"] > 0.1, "plus personne ne reprend la couleur de son haut"
    assert r["sortes"] == r["n"] >= 6 and r["sombres"]
    assert r["juilFoncés"] == 0, "un manteau foncé en juillet"


def test_les_enfants_s_habillent_selon_la_saison(banc):
    """Vague 4c : l'enfant, dessiné à la main, a ses manches longues au frais et son habit de neige (tuque,
    mitaines) au grand froid — dehors ; ses couleurs à lui restent (`e.swaps`)."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie, j = L.B.joueur;
        const e = L.Entites.creerPieton(j.x + 30, j.y + 10, L.Entites.archetype('enfant'));
        e.vx = 0; e.vy = 0; e.etat = 'arret'; e.face = 'bas';
        const nom = function () { return L.Saisons.ficheDuMoment(e.sprite, L.SPRITES[e.sprite])[0]; };
        const img = function () { return L.Entites.imageDe(e).canvas; };
        const out = {};
        [['janvier', 2], ['novembre', 36], ['juillet', 21], ['avril', 14]].forEach(function (m) {
            p.jour = m[1]; p.heure = 0.5; out[m[0]] = { nom: nom(), img: img() };
        });
        p.jour = 2; L.B.interieur = { slug: 'x' }; const dedans = nom(); L.B.interieur = null;
        const F = L.SPRITES.enfant.saisons.froid.poses.bas[0], B0 = L.SPRITES.enfant.poses.bas[0];
        return { noms: [out.janvier.nom, out.novembre.nom, out.juillet.nom, out.avril.nom], dedans: dedans,
                 differe: out.janvier.img !== out.juillet.img && out.novembre.img !== out.juillet.img,
                 tuque: F[1].indexOf('h') < 0 && B0[1].indexOf('h') >= 0, mitaines: F[9].indexOf('s') < 0 && B0[9].indexOf('s') >= 0,
                 visage: F[4] === B0[4] };
    }""")
    assert r["noms"] == ["enfant~froid", "enfant~frais", "enfant", "enfant~frais"], r["noms"]
    assert r["dedans"] == "enfant", "dedans, un enfant en habit de neige"
    assert r["differe"] and r["tuque"] and r["mitaines"] and r["visage"]


def test_de_novembre_a_l_hiver_on_se_couvre_peu_a_peu(banc):
    """Pas une coupure à minuit : d'une demi-heure à l'autre, une petite part des passants seulement
    enfile son manteau, et la part ne redescend pas."""
    r = banc("function (L) {" + TIRER + """
        L.Jeu.commencer();
        const p = L.B.partie, gens = monde(L, 400), parts = [];
        for (let j = 34; j <= 39; j++) for (let k = 0; k < 48; k++) {
            p.jour = j; p.heure = k / 48;
            parts.push(part(habits(L, gens), function (t) { return t.haut === 'manteau'; }));
        }
        let saut = 0, recul = 0;
        for (let i = 1; i < parts.length; i++) { saut = Math.max(saut, parts[i] - parts[i - 1]); recul = Math.max(recul, parts[i - 1] - parts[i]); }
        return { debut: parts[0], fin: parts[parts.length - 1], saut: saut, recul: recul };
    }""")
    assert r["debut"] < 0.4 and r["fin"] > 0.9
    assert r["recul"] == 0, "des manteaux tombent en marchant vers l'hiver"
    assert r["saut"] <= 0.25, f"{r['saut']:.0%} des passants enfilent leur manteau d'un coup"


def test_le_passant_se_dessine_dans_l_habit_du_moment(banc):
    r = banc("""function (L) {
        L.Jeu.commencer();
        const p = L.B.partie, j = L.B.joueur;
        let e = null;
        for (let i = 0; i < 40 && !e; i++) {
            const q = L.Entites.creerPieton(j.x + 30, j.y + 10, L.Entites.archetype('passant'));
            if (q.tenue && q.tenue.haut !== 'manteau') e = q; else L.Entites.retirer(q);
        }
        e.vx = 0; e.vy = 0; e.etat = 'arret';
        const image = function () { const i = L.Entites.imageDe(e); return i.canvas; };
        p.jour = 2; const hiver = image(), attendu = L.Garderobe.cuire(L.Saisons.vetir(e.tenue, e)).poses[L.Entites.imageDe(e).pose][0];
        p.jour = 21; while (L.Pluie.intensite() > 0) p.jour++;
        const ete = image();
        return { hiver: hiver === attendu, differe: hiver !== ete, haut: L.Saisons.vetir(e.tenue, e).haut, tire: e.tenue.haut };
    }""")
    assert r["hiver"], "imageDe ne dessine pas l'habit du moment"
    assert r["differe"], "le même dessin en janvier et en juillet"


PLUIE = """
    function averse(L) {
        const P = L.Pluie;
        for (let j = 11; j < 200; j++) {
            const a = P.journee(j);
            if (a && !a.orage) { L.B.partie.jour = j; L.B.partie.heure = (a.debut + a.fin) / 2 / 24; return j; }
        }
    }
"""


def test_le_parapluie_sous_la_pluie_seulement(banc):
    r = banc("function (L) {" + PLUIE + """
        L.Jeu.commencer();
        const p = L.B.partie, j = L.B.joueur, gens = [];
        for (let i = 0; i < 80; i++) {
            const e = L.Entites.creerPieton(j.x + 20 + (i % 10) * 6, j.y - 30 + Math.floor(i / 10) * 6, L.Entites.archetype('passant'));
            e.etat = 'flane'; gens.push(e);
        }
        const compte = function () { return gens.filter(function (e) { return L.Saisons.parapluie(e); }).length / gens.length; };
        averse(L); const sousLaPluie = compte();
        const couleur = L.Saisons.parapluie(gens.find(function (e) { return L.Saisons.parapluie(e); }));
        // Qui court le referme.
        const ouvert = gens.filter(function (e) { return L.Saisons.parapluie(e); });
        ouvert.forEach(function (e) { e.etat = 'fuit'; });
        const enCourant = ouvert.filter(function (e) { return L.Saisons.parapluie(e); }).length;
        ouvert.forEach(function (e) { e.etat = 'flane'; });
        // Il se peint : une image rendue cuit le parapluie.
        const cuits = []; const cp = L.Atlas.cuirePeintre;
        L.Atlas.cuirePeintre = function (cle) { cuits.push(cle); return cp.apply(null, arguments); };
        L.Entites.indexer(); L.Jeu.rendre();
        L.Atlas.cuirePeintre = cp;
        // Au sec, en janvier : rien.
        p.jour = 21; p.heure = 0.5; while (L.Pluie.intensite() > 0) p.jour++;
        const auSec = compte();
        p.jour = 2; const janvier = compte();
        return { sousLaPluie: sousLaPluie, couleur: couleur, enCourant: enCourant, auSec: auSec, janvier: janvier,
                 peint: cuits.filter(function (c) { return c.indexOf('parapluie|') === 0; }).length,
                 largeurs: L.Entites.PARAPLUIE.map(function (l) { return l.length; }) };
    }""")
    assert 0.25 <= r["sousLaPluie"] <= 0.75, f"{r['sousLaPluie']:.0%} des passants sous un parapluie"
    assert r["couleur"] and r["couleur"].startswith("#")
    assert r["enCourant"] == 0, "on court avec son parapluie ouvert"
    assert r["peint"] > 0, "le parapluie ne se peint pas"
    assert r["auSec"] == 0 and r["janvier"] == 0
    assert set(r["largeurs"]) == {18}


def test_sous_la_pluie_les_frileux_sans_parapluie_remontent_leur_capuche(banc):
    r = banc("function (L) {" + TIRER + PLUIE + """
        L.Jeu.commencer();
        const gens = monde(L, 300);
        L.B.partie.jour = 21; L.B.partie.heure = 0.5; while (L.Pluie.intensite() > 0) L.B.partie.jour++;
        const sec = habits(L, gens);
        averse(L);
        const mouille = habits(L, gens);
        const sans = gens.filter(function (g) { return !L.Saisons.aUnParapluie(g.tn); });
        return { capSec: part(sec, function (t) { return t.chapeau === 'capuche'; }),
                 capPluie: part(mouille, function (t) { return t.chapeau === 'capuche'; }),
                 capAvecParapluie: gens.filter(function (g, i) { return L.Saisons.aUnParapluie(g.tn) && mouille[i].chapeau === 'capuche' && g.tn.chapeau !== 'capuche'; }).length,
                 sans: sans.length };
    }""")
    assert r["capPluie"] > r["capSec"] + 0.1, "personne ne remonte sa capuche sous la pluie"
    assert r["capAvecParapluie"] == 0
