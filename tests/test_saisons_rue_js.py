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
