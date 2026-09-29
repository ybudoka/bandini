"""La rue des saisons (les quatre saisons, vague 4b ; `static/js/rue_des_saisons.js`) : les bancs de neige au
bord des trottoirs l'hiver, les abris Tempo dans les entrées de novembre au dégel, la fumée des cheminées
quand il fait froid, les terrasses l'été. Tout est PEINT d'après la palette du moment — rien n'est posé,
aucun dé n'est tiré, et les morceaux ne se repeignent qu'au palier."""

#: Peint le morceau (mx, my) de la ville par la rue des saisons seule, et rend les couleurs posées.
PEINDRE = """
    function peindre(L, mx, my) {
        const ctx = L.Base.nouveauCanvas(256, 256).getContext('2d'); ctx.traces = [];
        L.RueDesSaisons.peindre(ctx, L.Monde.carte, mx, my, 16, 16);
        return ctx.traces;
    }
    function morceauDe(tx, ty) { return [Math.floor(tx / 16), Math.floor(ty / 16)]; }
    function moment(L, jour, h) { L.B.partie.jour = jour; L.B.partie.heure = h === undefined ? 0.5 : h; }
"""


def test_les_bancs_de_neige_bordent_les_trottoirs_l_hiver_seulement(banc):
    r = banc("function (L) {" + PEINDRE + """
        L.Jeu.commencer();
        const M = L.Monde, c = M.carte, R = L.RueDesSaisons, d = L.B.defs.saisons.rue.bancs;
        // Une tuile de rue au bord d'un trottoir, une traverse, une entrée.
        let rue = null, faux = 0, bords = 0;
        for (let ty = 60; ty < c.h - 10; ty++) for (let tx = 5; tx < c.w - 5; tx++) {
            const cotes = R.bancsDe(tx, ty);
            if (!cotes.length) continue;
            bords++;
            if (!rue && !M.estTrottoir(tx, ty)) rue = [tx, ty];
            const l = c.legende[M.glyphe(tx, ty)] || {};
            if (!M.estRoute(tx, ty) || M.estPassage(tx, ty) || l.stationnement || l.ruelle) faux++;
            cotes.forEach(function (i) { const o = [[0, -1], [0, 1], [-1, 0], [1, 0]][i]; if (!M.estTrottoir(tx + o[0], ty + o[1])) faux++; });
        }
        const m = morceauDe(rue[0], rue[1]);
        moment(L, 2); const janvier = peindre(L, m[0], m[1]);
        moment(L, 21); const juillet = peindre(L, m[0], m[1]);
        moment(L, 11, 0.4); const degel = peindre(L, m[0], m[1]);
        const couleurs = function (t) { return t.map(function (x) { return x[4]; }); };
        return { bords: bords, faux: faux, blancJanvier: couleurs(janvier).indexOf(d.neige) >= 0,
                 juillet: juillet.filter(function (x) { return x[4] === d.neige || x[4] === d.ombre; }).length,
                 blancDegel: couleurs(degel).indexOf(d.neige) >= 0, nDegel: degel.length, nJanvier: janvier.length };
    }""")
    assert r["bords"] > 500, f"{r['bords']} tuiles de rue au bord d'un trottoir : le juge ne voit pas la ville"
    assert r["faux"] == 0, "un banc sur une traverse, une entrée, une ruelle, ou loin du trottoir"
    assert r["blancJanvier"] and r["juillet"] == 0, "pas de banc en janvier, ou un banc en juillet"
    assert not r["blancDegel"] and 0 < r["nDegel"], "au dégel, le banc reste blanc (ou disparaît d'un coup)"


def test_les_tempo_de_novembre_au_degel_dans_les_entrees(banc):
    r = banc("function (L) {" + PEINDRE + """
        L.Jeu.commencer();
        const c = L.Monde.carte, R = L.RueDesSaisons, d = L.B.defs.saisons.rue.tempo;
        const t = R.lieux(c).tempos, hors = [];
        t.forEach(function (x) {
            for (let dy = 0; dy < x.h; dy++) for (let dx = 0; dx < x.w; dx++) if (L.Monde.glyphe(x.x + dx, x.y + dy) !== 'p') hors.push([x.x + dx, x.y + dy]);
        });
        const monte = function (jour, h) { moment(L, jour, h); return R.tempoMonte(R.moment()); };
        const m = morceauDe(t[0].x, t[0].y);
        moment(L, 2); const janvier = peindre(L, m[0], m[1]).filter(function (x) { return x[4] === d.toile; }).length;
        moment(L, 21); const juillet = peindre(L, m[0], m[1]).filter(function (x) { return x[4] === d.toile; }).length;
        return { n: t.length, hors: hors, janvier: janvier, juillet: juillet,
                 novembre: monte(37), decembre: monte(39), avril: monte(14), octobre: monte(31), juin: monte(19),
                 debutDegel: monte(10, 0.6), finDegel: monte(11, 0.7) };
    }""")
    assert r["n"] >= 12, f"{r['n']} Tempo dans toute la ville"
    assert r["hors"] == [], f"un Tempo déborde de son entrée : {r['hors'][:5]}"
    assert r["janvier"] > 0 and r["juillet"] == 0
    assert r["novembre"] and r["decembre"] and r["debutDegel"]
    assert not r["avril"] and not r["octobre"] and not r["juin"] and not r["finDegel"]


def test_les_terrasses_l_ete_devant_les_restos_jamais_devant_une_porte(banc):
    r = banc("function (L) {" + PEINDRE + """
        L.Jeu.commencer();
        const c = L.Monde.carte, R = L.RueDesSaisons, D = L.B.defs.carte, genres = L.B.defs.devantures.genres;
        const t = R.lieux(c).terrasses, fautes = [];
        const pris = new Set(D.decor.map(function (o) { return o.x + ',' + o.y; }));
        t.forEach(function (x) {
            const f = D.devantures.find(function (f) { return f.y === x.y - 1 && x.x >= f.x && x.x < f.x + f.l; });
            if (!f || ['bouffe', 'nuit'].indexOf(genres[f.genre].slug) < 0) fautes.push('pas un resto');
            if ('DdG'.indexOf(L.Monde.glyphe(x.x, x.y - 1)) >= 0) fautes.push('devant une porte');
            if (pris.has(x.x + ',' + x.y)) fautes.push('sur du décor');
        });
        const m = morceauDe(t[0].x, t[0].y), rouge = L.B.defs.saisons.rue.terrasses.parasols;
        const table = function (tr) { return tr.filter(function (x) { return x[4] === '#d9d4ca'; }).length; };
        moment(L, 21); const juillet = table(peindre(L, m[0], m[1]));
        moment(L, 2); const janvier = table(peindre(L, m[0], m[1]));
        moment(L, 31); const octobre = table(peindre(L, m[0], m[1]));
        return { n: t.length, fautes: fautes, juillet: juillet, janvier: janvier, octobre: octobre };
    }""")
    assert r["n"] >= 10 and r["fautes"] == []
    assert r["juillet"] > 0 and r["janvier"] == 0 and r["octobre"] == 0


def test_les_cheminees_fument_quand_il_fait_froid_d_apres_l_horloge(banc):
    r = banc("function (L) {" + PEINDRE + """
        L.Jeu.commencer();
        const c = L.Monde.carte, B = L.B, j = B.joueur, R = L.RueDesSaisons;
        const ch = L.B.defs.carte.toits.filter(function (t) { return t.type === 'cheminee'; });
        // Le joueur sous la cheminée la plus au nord de la ville (hors de la bande nord), et la ville rendue.
        const t = ch[Math.floor(ch.length / 2)];
        j.x = t.x * 16 + 8; j.y = (t.y + 3) * 16; L.Monde.centrerCamera(j.x, j.y);
        const fumee = function (jour) {
            moment(L, jour); L.Jeu.rendre();
            const ctx = L.Base.nouveauCanvas(10, 10).getContext('2d'); ctx.traces = [];
            R.dessinerFumees(ctx, B.cam);
            return ctx.traces.length;
        };
        let des = 0; const rng = B.rng; B.rng = function () { des++; return rng(); };
        B.t = 1000; const janvier = fumee(2), cheminees = R.cheminees().length;
        const pareil = fumee(2);
        B.t = 1040; const plusTard = JSON.stringify(R.cheminees().map(function (x) { return [x.x, x.y]; }));
        const juillet = fumee(21), novembre = fumee(37), octobre = fumee(31);
        B.rng = rng;
        const part = ch.filter(function (x) { return R.fumeA(x, 0.65); }).length / ch.length;
        return { janvier: janvier, pareil: pareil, cheminees: cheminees, juillet: juillet, novembre: novembre, octobre: octobre, des: des, part: part,
                 toutes: ch.every(function (x) { return R.fumeA(x, 1); }), aucuneEnOctobre: ch.every(function (x) { return !R.fumeA(x, 0.4); }) };
    }""")
    assert r["cheminees"] > 0 and r["janvier"] > 0, "pas de fumée en janvier"
    assert r["pareil"] == r["janvier"], "la même image ne fume pas pareil"
    assert r["juillet"] == 0 and r["octobre"] == 0
    assert r["aucuneEnOctobre"], "une cheminée fume en octobre"
    assert r["toutes"] and 0.3 < r["part"] < 0.95, f"en novembre, {r['part']:.0%} des cheminées fument"
    assert r["des"] == 0


def test_rien_n_est_pose_rien_n_est_tire_et_le_morceau_attend_son_palier(banc):
    r = banc("function (L) {" + PEINDRE + """
        L.Jeu.commencer();
        const B = L.B, c = L.Monde.carte, avant = JSON.stringify(L.B.defs.carte.sol).length, ids = [];
        const n0 = L.Entites.creerDecor ? B.entites.length : 0;
        let des = 0; const rng = B.rng; B.rng = function () { des++; return rng(); };
        moment(L, 2); L.Jeu.rendre();
        const m0 = Array.from(c.morceaux.values())[0];
        B.partie.heure = 0.7; L.Jeu.rendre();
        const garde = Array.from(c.morceaux.values())[0] === m0;
        moment(L, 21); L.Jeu.rendre(); moment(L, 37); L.Jeu.rendre(); moment(L, 11); L.Jeu.rendre();
        B.rng = rng;
        // Le rendu passe bien par la rue des saisons : les morceaux la peignent, et la fumée se dessine.
        const R = L.RueDesSaisons, appels = { peindre: 0, fumees: 0 }, p0 = R.peindre, f0 = R.dessinerFumees;
        R.peindre = function () { appels.peindre++; return p0.apply(null, arguments); };
        R.dessinerFumees = function () { appels.fumees++; return f0.apply(null, arguments); };
        moment(L, 3); L.Jeu.rendre();
        R.peindre = p0; R.dessinerFumees = f0;
        return { des: des, garde: garde, appels: appels, sol: JSON.stringify(L.B.defs.carte.sol).length === avant, entites: B.entites.length - n0 };
    }""")
    assert r["des"] == 0, f"{r['des']} dés tirés pour peindre la rue"
    assert r["garde"], "un morceau repeint sans changement de palier"
    assert r["appels"]["peindre"] > 0 and r["appels"]["fumees"] > 0, f"le rendu ne passe pas par la rue des saisons : {r['appels']}"
    assert r["sol"] and r["entites"] == 0, "la rue des saisons a posé quelque chose"


# --- Solides selon la saison (vague 4c, Martin : « on ne marche plus sur les tables, les chars ne passent plus
# sous les Tempo ») : leur collision apparaît et disparaît avec eux, sans rien poser ni tirer. ------------------

#: Une terrasse dont la tuile à l'ouest et celle à l'est sont libres (trottoir, sans décor solide) : on y marche.
TERRASSE_LIBRE = """
    function terrasseLibre(L) {
        const c = L.Monde.carte, l = L.RueDesSaisons.lieux(c), TT = 16;
        const libre = function (tx, ty) {
            if (!L.Monde.marchablePieton(tx, ty)) return false;
            if (l.terrasses.some(function (t) { return t.x === tx && t.y === ty; })) return false;
            return !L.Entites.decorAutour(tx * TT + 8, ty * TT + 8, 14).some(function (d) { return d.solide; });
        };
        return l.terrasses.find(function (t) { return libre(t.x - 1, t.y) && libre(t.x - 2, t.y) && libre(t.x + 1, t.y) && libre(t.x + 2, t.y); });
    }
"""


def test_on_ne_marche_plus_sur_les_tables_des_terrasses_l_ete(banc):
    """Le joueur marche vers une table le long du trottoir : l'été, il bute sur la table et ses chaises ;
    l'hiver (pas de terrasse), il passe. Par la vraie marche (les touches), pas par la fonction."""
    r = banc("function (L, o) {" + PEINDRE + TERRASSE_LIBRE + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, TT = 16, t = terrasseLibre(L), bx = t.x * TT + 8;
        function marcher(jour) {
            moment(L, jour);
            j.x = (t.x - 2) * TT + 8; j.y = t.y * TT + 8; j.vx = 0; j.vy = 0; L.Entites.indexer();
            o.touche('KeyD'); o.frame(70); o.relacher('KeyD'); o.frame(5);
            return j.x;
        }
        let des = 0; const rng = B.rng;
        const juillet = marcher(21), janvier = marcher(2);
        return { t: t, bx: bx, juillet: juillet, janvier: janvier };
    }""")
    assert r["t"], "aucune terrasse avec du trottoir libre de chaque côté : le juge ne voit rien"
    assert r["juillet"] <= r["bx"] - 7 - 5 + 0.5, f"l'été, le joueur marche sur la table ({r['juillet']:.1f} contre {r['bx']})"
    assert r["janvier"] > r["bx"] + 8, f"l'hiver, une table invisible arrête le joueur ({r['janvier']:.1f})"


def test_un_passant_sur_une_table_au_premier_jour_d_ete_en_sort_par_le_trottoir(banc):
    """Posé sur la table en juin (il y était avant qu'elle sorte), il en est poussé au sud — le trottoir —,
    jamais dans la façade ; puis il repart. Et un donneur n'est jamais sur une terrasse."""
    r = banc("function (L, o) {" + PEINDRE + TERRASSE_LIBRE + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, TT = 16, c = L.Monde.carte, R = L.RueDesSaisons;
        const idx = R.index(c).tables, sorties = [];
        const liste = R.lieux(c).terrasses.slice(0, 12);
        for (const t of liste) {
            // Au printemps, il attend là (pas de terrasse) ; l'été arrive, la table sort sous lui.
            moment(L, 16);
            const e = L.Entites.creerPieton(t.x * TT + 8, t.y * TT + 8, L.Entites.archetype('passant'));
            e.etat = 'arret'; e.vx = 0; e.vy = 0; e.butT = 600;
            j.x = e.x + 60; j.y = e.y + 40;
            L.Entites.indexer();
            o.frame(4);
            moment(L, 21);
            o.frame(4);
            const b = idx.get(t.y * c.w + t.x);
            // Enfoncé de plus d'un pixel dans la table et ses chaises (la foule qui se démêle pousse d'un cheveu).
            const px = b.l + e.r - Math.abs(e.x - b.x), py = b.h + e.r - Math.abs(e.y - b.y);
            const dedans = px > 1 && py > 1;
            sorties.push({ dedans: dedans, px: px, py: py, e: [e.x, e.y, e.etat], b: [b.x, b.y], pieds: L.Monde.marchablePieton(Math.floor(e.x / TT), Math.floor(e.y / TT)), nord: e.y < b.y - 0.5 });
            L.Entites.retirer(e);
        }
        const donneurs = L.B.defs.personnages.map(function (p) { return L.Histoire.donneur(p.slug); }).filter(Boolean)
            .filter(function (e) { const b = idx.get(Math.floor(e.y / TT) * c.w + Math.floor(e.x / TT)); return !!b; })
            .map(function (e) { return e.personnage; });
        return { n: sorties.length, sorties: sorties, donneurs: donneurs };
    }""")
    assert r["n"] >= 10
    for s in r["sorties"]:
        assert not s["dedans"], f"un passant reste pris dans une table : {s}"
        assert s["pieds"] and not s["nord"], "poussé hors de la table vers la façade (ou dans un mur)"
    assert r["donneurs"] == [], f"des donneurs debout sur une terrasse : {r['donneurs']}"


#: Un Tempo et, au sud de lui, une place de char libre (le char y part le nez vers l'abri).
TEMPO_ACCESSIBLE = """
    function tempoAccessible(L) {
        const c = L.Monde.carte, TT = 16;
        L.B.partie.jour = 21;             // l'été : les abris sont démontés, on cherche la place libre
        const v = L.Vehicules.creer('auto', 0, 0, -Math.PI / 2, { etat: 'stationne', couleur: '#c0392b' });
        const t = L.RueDesSaisons.lieux(c).tempos.find(function (t) {
            const x = (t.x + t.w / 2) * TT, y = (t.y + t.h) * TT + 26;
            return !L.Vehicules.bloqueParLesTuiles(v, x, y) && !L.Vehicules.bloqueParLesTuiles(v, x, y - 20);
        });
        L.Entites.retirer(v);
        return t;
    }
"""


def test_les_chars_ne_passent_plus_sous_les_tempo_l_hiver(banc):
    """Au volant, nez vers un Tempo : en juillet (pas d'abri) on y entre ; en janvier on bute à l'abri.
    Un char DÉJÀ dessous quand on le monte en sort librement ; un piéton y passe toujours."""
    r = banc("function (L, o) {" + PEINDRE + TEMPO_ACCESSIBLE + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, TT = 16, t = tempoAccessible(L);
        if (!t) return { t: null };
        const x = (t.x + t.w / 2) * TT, bas = (t.y + t.h) * TT, bonds = [];
        function rouler(jour, y0, cap, touche, n) {
            moment(L, jour);
            if (j.dansVehicule) L.Vehicules.descendre ? L.Vehicules.descendre(j) : null;
            const v = L.Vehicules.creer('auto', x, y0, cap, { etat: 'stationne', couleur: '#c0392b' });
            j.x = v.x + 14; j.y = v.y; L.Entites.indexer();
            L.Vehicules.monter(j, v); L.Entites.indexer();
            // Pas a pas : un char qu'on DEGAGE (le garde-fou des murs le saute hors de ce qui le coince)
            // fait un bond ; un char qui sort de lui-meme roule.
            let bond = 0, px = v.x, py = v.y;
            const suivre = function (k) { for (let i = 0; i < k; i++) { o.frame(1); bond = Math.max(bond, Math.hypot(v.x - px, v.y - py)); px = v.x; py = v.y; } };
            o.touche(touche); suivre(n || 50); o.relacher(touche); suivre(40);
            bonds.push(bond);
            const y = v.y; j.dansVehicule = null; j.x = v.x + 30; L.Entites.retirer(v); L.Entites.indexer();
            return y;
        }
        const juillet = rouler(21, bas + 26, -Math.PI / 2, 'KeyW');
        const janvier = rouler(2, bas + 26, -Math.PI / 2, 'KeyW');
        // Garé dessous en été, l'abri monté par-dessus : il sort (le nez vers la rue).
        const sort = rouler(2, t.y * TT + t.h * TT / 2, Math.PI / 2, 'KeyW', 40);
        // Le piéton, lui, passe dessous.
        moment(L, 2); j.x = x; j.y = bas + 20; j.vx = 0; j.vy = 0; L.Entites.indexer();
        o.touche('KeyW'); o.frame(40); o.relacher('KeyW'); o.frame(5);
        return { t: t, bas: bas, juillet: juillet, janvier: janvier, sort: sort, pieton: j.y, bonds: bonds };
    }""")
    assert r["t"], "aucun Tempo où un char peut arriver : le juge ne voit rien"
    assert r["juillet"] < r["bas"] - 4, f"en juillet, le char n'entre pas dans l'entrée ({r['juillet']:.1f} / {r['bas']})"
    assert r["janvier"] > r["bas"] + 4, f"en janvier, le char passe sous le Tempo ({r['janvier']:.1f} / {r['bas']})"
    assert r["sort"] > r["bas"] + 4, f"un char garé sous le Tempo y reste pris ({r['sort']:.1f} / {r['bas']})"
    assert r["bonds"][2] < 8, f"le char garé sous le Tempo n'en sort qu'en sautant (garde-fou) : {r['bonds']}"
    assert r["pieton"] < r["bas"] - 8, "un piéton ne passe plus sous l'abri"


def test_aucun_tempo_devant_un_garage_qui_sert_ni_une_terrasse_devant_une_porte(banc):
    """Rien de solide selon la saison ne bloque une porte : aucun Tempo devant le rideau d'un garage où l'on
    entre (`carte.portesGarage`), aucune table devant ni à côté d'une porte, et rien n'est tiré."""
    r = banc("function (L) {" + PEINDRE + """
        L.Jeu.commencer();
        const B = L.B, c = L.Monde.carte, R = L.RueDesSaisons, l = R.lieux(c);
        let des = 0; const rng = B.rng; B.rng = function () { des++; return rng(); };
        const garages = (c.portesGarage || []).filter(function (pg) {
            return l.tempos.some(function (t) { return t.x < pg.x + pg.l && t.x + t.w > pg.x && t.y <= pg.y + 4 && t.y + t.h > pg.y; });
        }).map(function (pg) { return pg.lieu; });
        const portes = (c.portes || []).filter(function (p) {
            return l.terrasses.some(function (t) { return Math.abs(t.x - p.x) <= 1 && t.y >= p.y && t.y <= p.y + 1; });
        }).map(function (p) { return p.lieu || p.nom; });
        moment(L, 2); for (let ty = 0; ty < c.h; ty += 3) for (let tx = 0; tx < c.w; tx += 3) R.tempoBloque({ type: 'vehicule', x: 0, y: 0, angle: 0, r: 6, def: { longueur: 30 } }, tx, ty);
        moment(L, 21); const j = B.joueur; R.bloquer(j);
        B.rng = rng;
        return { garages: garages, portes: portes, nPortes: (c.portes || []).length, nGarages: (c.portesGarage || []).length, des: des };
    }""")
    assert r["nPortes"] > 50 and r["nGarages"] > 0
    assert r["garages"] == [], f"un Tempo devant un garage où l'on entre : {r['garages']}"
    assert r["portes"] == [], f"une terrasse devant une porte : {r['portes']}"
    assert r["des"] == 0


# --- Les bornes-fontaines ouvertes de la canicule (vague 4c) ------------------------------------------------

#: Un jour de chaleur de l'été, à 15 h, sans pluie, et ses bornes ouvertes.
CANICULE = """
    function canicule(L) {
        const R = L.RueDesSaisons, p = L.B.partie;
        for (let j = 18; j < 24; j++) {
            p.jour = j; p.heure = 15 / 24;
            if (R.jourDeChaleur(j) && L.Pluie.intensite() <= 0.05 && R.bornesOuvertes().length) return j;
        }
        return null;
    }
"""


def test_quelques_bornes_crachent_les_jours_de_chaleur_seulement(banc):
    r = banc("function (L) {" + PEINDRE + CANICULE + """
        L.Jeu.commencer();
        const R = L.RueDesSaisons, p = L.B.partie, c = L.Monde.carte, d = L.B.defs.saisons.rue.bornes;
        let des = 0; const rng = L.B.rng; L.B.rng = function () { des++; return rng(); };
        const toutes = R.bornesDe(c).length;
        const jour = canicule(L);
        const ouvertes = R.bornesOuvertes().length;
        const memes = JSON.stringify(R.bornesOuvertes().map(function (b) { return [b.tx, b.ty]; }));
        p.heure = 15.1 / 24; const memesPlusTard = JSON.stringify(R.bornesOuvertes().map(function (b) { return [b.tx, b.ty]; })) === memes;
        p.heure = 8 / 24; const matin = R.bornesOuvertes().length;
        p.heure = 22 / 24; const soir = R.bornesOuvertes().length;
        // Jamais hors de l'été : janvier, avril, octobre, novembre, toutes les heures du jour.
        let horsEte = 0;
        [2, 5, 13, 15, 30, 33, 36].forEach(function (j) { for (let h = 10; h < 20; h++) { p.jour = j; p.heure = h / 24; horsEte += R.bornesOuvertes().length; } });
        // Les jours d'été : pas tous chauds, pas aucun.
        let chauds = 0; for (let j = 18; j <= 23; j++) if (R.jourDeChaleur(j)) chauds++;
        L.B.rng = rng;
        return { toutes: toutes, jour: jour, ouvertes: ouvertes, memes: memesPlusTard, matin: matin, soir: soir, horsEte: horsEte, chauds: chauds, des: des };
    }""")
    assert r["toutes"] >= 40, f"{r['toutes']} bornes : le juge ne voit pas la ville"
    assert r["jour"], "aucun jour de chaleur sans pluie en juillet"
    assert 3 <= r["ouvertes"] <= r["toutes"] * 0.4, f"{r['ouvertes']} bornes ouvertes sur {r['toutes']}"
    assert r["memes"], "les bornes ouvertes changent d'une minute à l'autre"
    assert r["matin"] == 0 and r["soir"] == 0, "une borne ouverte à 8 h ou à 22 h"
    assert r["horsEte"] == 0, "une borne ouverte hors de l'été"
    assert 1 <= r["chauds"] <= 5
    assert r["des"] == 0


def test_la_borne_ouverte_se_peint_avec_ses_enfants_et_rien_n_est_pose(banc):
    """Le jet, la flaque et les enfants se dessinent au rendu (triés avec les gens), les enfants courent (ils
    changent de place d'une image à l'autre) ; rien ne naît (pas une entité de plus, pas un dé)."""
    r = banc("function (L) {" + PEINDRE + CANICULE + """
        L.Jeu.commencer();
        const B = L.B, R = L.RueDesSaisons, j = B.joueur;
        canicule(L);
        const b = R.bornesOuvertes()[0];
        j.x = b.x + 40; j.y = b.y + 30; L.Entites.indexer(); B.cam.x = b.x - 160; B.cam.y = b.y - 90;
        const n0 = B.entites.length;
        let des = 0; const rng = B.rng; B.rng = function () { des++; return rng(); };
        const cuits = []; const cu = L.Atlas.cuire;
        L.Atlas.cuire = function (nom) { cuits.push(nom); return cu.apply(null, arguments); };
        const appels = { flaques: 0 }; const f0 = R.dessinerFlaques;
        R.dessinerFlaques = function () { appels.flaques++; return f0.apply(null, arguments); };
        const k0 = R.enfantsDe(b).map(function (k) { return [k.x, k.y]; });
        L.Jeu.rendre(); B.t += 20; L.Jeu.rendre();
        const k1 = R.enfantsDe(b).map(function (k) { return [k.x, k.y]; });
        L.Atlas.cuire = cu; R.dessinerFlaques = f0; B.rng = rng;
        return { enfants: k0.length, courent: JSON.stringify(k0) !== JSON.stringify(k1),
                 cuitsEnfant: cuits.filter(function (n) { return n === 'enfant'; }).length, flaques: appels.flaques,
                 nes: B.entites.length - n0, des: des,
                 pres: k1.every(function (k) { return Math.hypot(k[0] - b.x, k[1] - b.y) < 45; }) };
    }""")
    assert r["enfants"] >= 2 and r["courent"] and r["pres"], "pas d'enfants qui courent autour de la borne"
    assert r["cuitsEnfant"] > 0, "les enfants ne se peignent pas au rendu"
    assert r["flaques"] > 0, "le rendu ne peint pas la flaque"
    assert r["nes"] == 0 and r["des"] == 0, "la borne ouverte a posé une entité ou tiré un dé"


def test_la_borne_ouverte_s_entend_rafraichit_et_se_laisse_couler(banc):
    r = banc("function (L, o) {" + PEINDRE + CANICULE + """
        L.Jeu.commencer();
        const B = L.B, R = L.RueDesSaisons, j = B.joueur, S = L.Son;
        canicule(L);
        const b = R.bornesOuvertes()[0];
        const charges = []; const ch = S.Lieu.charger; S.Lieu.charger = function (s) { charges.push(s); return ch.apply(null, arguments); };
        j.x = b.x + 12; j.y = b.y + 12; L.Entites.indexer();
        for (let i = 0; i < 120; i++) R.majSon();
        const pres = R.sonBorne;
        j.x = b.x + 2000; for (let i = 0; i < 200; i++) R.majSon();
        const loin = R.sonBorne;
        j.x = b.x + 12; for (let i = 0; i < 120; i++) R.majSon();
        B.interieur = { slug: 'x' }; for (let i = 0; i < 200; i++) R.majSon(); const dedans = R.sonBorne; B.interieur = null;
        S.Lieu.charger = ch;
        // Le geste : la borne de la canicule ne se ferme pas (les enfants jouent).
        const c = L.B.defs.interactions.borne;
        const refus = (function () {
            j.x = b.x + 6; j.y = b.y + 4; L.Entites.indexer();
            const s = L.Interactions.decorSousLaMain ? L.Interactions.decorSousLaMain(j) : null;
            return s ? s.invite : null;
        })();
        // La boucle du jeu l'appelle (un pas de `Jeu.maj`), et l'eau de la borne rend le souffle.
        let pas = 0; const m0 = R.majSon; R.majSon = function () { pas++; return m0.apply(null, arguments); };
        o.frame(8); R.majSon = m0;
        const souffle = function (x, y) {
            j.x = x; j.y = y; j.endurance = 10; L.Entites.indexer();
            for (let i = 0; i < 40; i++) { B.t++; L.Interactions.maj(); }
            return j.endurance;
        };
        const q = { x: b.x + b.dir[0] * 18, y: b.y - 2 + b.dir[1] * 18 };
        const mouille = souffle(q.x, q.y), sec = souffle(b.x + 300, b.y + 300);
        return { pres: pres, loin: loin, dedans: dedans, charges: charges.filter(function (s) { return s === 'borne_ete'; }).length,
                 pas: pas, mouille: mouille, sec: sec,
                 refus: refus, attendu: c.enfants, dansLeJet: R.dansUnJet(b.x, b.y + 2, 20), horsDuJet: R.dansUnJet(b.x + 200, b.y, 20) };
    }""")
    assert r["pres"] > 0.2 and r["loin"] < 0.01 and r["dedans"] < 0.01, r
    assert r["charges"] >= 1, "le lieu borne_ete n'est jamais demandé"
    assert r["attendu"] and r["refus"] == r["attendu"], f"on peut fermer la borne des enfants : {r['refus']}"
    assert r["dansLeJet"] and not r["horsDuJet"]
    assert r["pas"] > 0, "la boucle du jeu n'appelle pas le son des bornes"
    assert r["mouille"] > r["sec"] + 0.5, "l'eau de la borne ouverte ne rafraîchit pas"


def test_les_enfants_de_la_borne_remontent_sur_le_trottoir_quand_un_char_approche(banc):
    """Ils courent dans le jet, au bord de la rue ; un char qui roule à côté, et ils attendent sur le
    trottoir derrière la borne — jamais peints dans la rue sous un char. Et une ville encore vide (le rendu
    sous l'écran titre) n'est pas retenue : les bornes se trouvent une fois le décor né."""
    r = banc("function (L) {" + PEINDRE + CANICULE + """
        L.Jeu.commencer();
        const B = L.B, R = L.RueDesSaisons, M = L.Monde, TT = 16;
        const c = M.carte, garde = B.entites; delete c.bornesFontaines;
        B.entites = []; const vide = R.bornesDe(c).length; B.entites = garde;
        const apres = R.bornesDe(c).length;
        canicule(L);
        const chaussee = function (x, y) { const tx = Math.floor(x / TT), ty = Math.floor(y / TT); return M.estRoute(tx, ty) && !M.estTrottoir(tx, ty); };
        let libresDansLaRue = 0, prudentsDansLaRue = 0, prudents = 0, n = 0;
        for (const b of R.bornesOuvertes()) {
            B.t += 1; R.enfantsDe(b).forEach(function (k) { if (chaussee(k.x, k.y)) libresDansLaRue++; });
            const v = L.Vehicules.creer('auto', b.x + b.dir[0] * 40, b.y + b.dir[1] * 40 - 40, 0, { etat: 'roule', couleur: '#c0392b' });
            v.vitesse = 2; B.t += 1;
            R.enfantsDe(b).forEach(function (k) { n++; if (k.prudent) prudents++; if (chaussee(k.x, k.y)) prudentsDansLaRue++; });
            L.Entites.retirer(v);
        }
        return { vide: vide, apres: apres, n: n, prudents: prudents, prudentsDansLaRue: prudentsDansLaRue, libresDansLaRue: libresDansLaRue };
    }""")
    assert r["vide"] == 0 and r["apres"] >= 40, "une ville vide a été retenue : plus jamais de borne ouverte"
    assert r["n"] >= 6 and r["prudents"] == r["n"], "un char approche et les enfants jouent encore dans le jet"
    assert r["prudentsDansLaRue"] == 0, "des enfants attendent dans la rue"
    assert r["libresDansLaRue"] > 0, "les enfants ne vont jamais dans le jet (le juge ne mord plus)"
