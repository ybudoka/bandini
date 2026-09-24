"""L'aéroport, côté jeu : fermé par étages, et peint.

⚠️ Chaque barrière se juge au BOUTON, comme le joueur la rencontre — pousser le
stick contre elle —, et chacune porte son TÉMOIN : la mission qu'elle attend,
faite, et on passe. Sans lui, « on ne passe pas » pourrait vouloir dire que le
banc a posé le joueur dans un mur.
"""

import math

from app import aeroport, carte

#: Vide la rue autour du joueur et coupe les naissances de chars : ce qu'on juge,
#: c'est la barrière, pas le trafic du hasard (la leçon de `test_barrieres_js`).
VIDER = """
    function vider(L) {
        const j = L.B.joueur;
        L.B.defs.conduite.trafic.vehicules_max = 0;
        L.B.entites.filter(function (e) {
            return e !== j && e !== j.dansVehicule && (e.type === 'vehicule' || e.type === 'pieton');
        }).forEach(function (e) { L.Entites.retirer(e); });
    }
    function poser(L, tx, ty) {
        const j = L.B.joueur;
        vider(L);
        j.x = tx * L.TT + 8; j.y = ty * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        L.Entites.indexer();
    }
"""


def test_la_barricade_du_pont_arrete_puis_s_enjambe_sans_etoile(banc):
    """À pied, depuis le trottoir de La Pointe : on se bute à la barricade (le HUD
    dit pourquoi), puis, à force de pousser, on l'enjambe — un chantier, pas un
    crime : aucune étoile. Derrière, le tablier."""
    pont = next(b for b in carte.BARRIERES if b["slug"] == "pont_aeroport")
    r = banc("""function (L, o) {""" + VIDER + """
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT;
        const b = L.Monde.carte.def.barrieres.find(function (q) { return q.slug === 'pont_aeroport'; });
        const out = { fermee: L.Monde.barriereFermee(b), b: { x: b.x, y: b.y } };
        poser(L, b.x + 1, b.y - 1);
        o.touche('KeyS'); o.frame(30);
        out.bute = { y: j.y / TT, msg: L.B.msg };
        o.frame(170); o.relacher('KeyS'); o.frame(30);
        out.passe = { y: j.y / TT, etoiles: L.B.recherche.etoiles };
        return out;
    }""")
    b = r["b"]
    assert r["fermee"] is True
    assert r["bute"]["y"] < b["y"], f"la barricade n'a pas arrêté le joueur : {r['bute']}"
    assert r["bute"]["msg"] == pont["raison"], r["bute"]
    assert r["passe"]["y"] > b["y"] + 1, f"on n'enjambe pas la barricade : {r['passe']}"
    assert r["passe"]["etoiles"] == 0, "enjamber une barricade de chantier a coûté une étoile"


def test_la_guerite_ne_se_force_pas_et_s_ouvre_avec_le_laissez_passer(banc):
    """Sorti de l'eau au bout du pont, côté île : la guérite arrête, et pousser
    n'y change rien (elle ne se force pas). TÉMOIN : a02 faite, on passe."""
    guerite = next(b for b in carte.BARRIERES if b["slug"] == "aeroport")
    r = banc("""function (L, o) {""" + VIDER + """
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT;
        const b = L.Monde.carte.def.barrieres.find(function (q) { return q.slug === 'aeroport'; });
        const out = { b: { y: b.y } };
        // Le carnet annonce ce qui est fermé : c'est lui qui dit qu'il y a là quelque chose à ouvrir.
        out.carnet = L.Missions.menuCasier().items.filter(function (i) { return i.libelle.indexOf('AÉROPORT') >= 0; })
                                           .map(function (i) { return i.detail; });
        poser(L, b.x + 1, b.y - 2);
        o.touche('KeyS'); o.frame(240); o.relacher('KeyS');
        out.ferme = { y: j.y / TT, msg: L.B.msg, enjambable: !!L.Monde.barriereEnjambable(j, b.x + 1, b.y) };
        L.B.partie.missionsFaites.a02 = true;
        poser(L, b.x + 1, b.y - 2);
        o.touche('KeyS'); o.frame(90); o.relacher('KeyS');
        out.ouvert = { y: j.y / TT, fermee: L.Monde.barriereFermee(b) };
        return out;
    }""")
    y = r["b"]["y"]
    pont = next(b for b in carte.BARRIERES if b["slug"] == "pont_aeroport")
    assert sorted(r["carnet"]) == sorted([pont["raison"], guerite["raison"]]), r["carnet"]
    assert r["ferme"]["y"] < y, f"la guérite a laissé passer : {r['ferme']}"
    assert r["ferme"]["msg"] == guerite["raison"], r["ferme"]
    assert r["ferme"]["enjambable"] is False
    assert r["ouvert"]["fermee"] is False and r["ouvert"]["y"] > y + 1, f"le témoin ne mord pas : {r['ouvert']}"


def test_l_aeroport_se_peint_dans_ses_morceaux_et_nulle_part_ailleurs(banc):
    """La piste (ses seuils blancs), les avions (leur livrée), les piles de la
    travée : chacun dans son morceau. Tous les morceaux de l'aéroport se peignent
    sans erreur, et un morceau loin de lui ne reçoit pas un trait."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const a = L.Monde.carte.def.aeroport;
        const c = L.Base.nouveauCanvas(256, 256).getContext('2d');
        function traits(mx, my) { c.traces = []; L.Aeroport.peindre(c, mx, my); const t = c.traces; c.traces = null; return t; }
        function couleur(t, coul) { return t.filter(function (r) { return r[4] === coul; }).length; }
        const m = function (x) { return Math.floor(x / 16); };
        const out = {};
        out.seuil = couleur(traits(m(a.piste.x), m(a.piste.y + 1)), '#e6e4da');
        const v = a.avions[0];
        out.avion = couleur(traits(m(v.x), m(v.y)), L.Aeroport.LIVREES[v.livree].bande);
        const pile = a.pont.piles[0];
        out.pile = couleur(traits(m(pile[0]), m(pile[1])), '#9c9d99');
        out.loin = traits(0, 0).length;
        let morceaux = 0;
        for (let my = m(a.pont.y); my <= m(a.plan[1] + a.plan[3]); my++) {
            for (let mx = m(a.plan[0]); mx <= m(a.plan[0] + a.plan[2]); mx++) { traits(mx, my); morceaux++; }
        }
        out.morceaux = morceaux;
        return out;
    }""")
    assert r["seuil"] >= 8, f"les seuils de la piste ne se peignent pas : {r}"
    assert r["avion"] > 0 and r["pile"] > 0, r
    assert r["loin"] == 0, "l'aéroport peint dans un morceau qui n'est pas le sien"
    assert r["morceaux"] > 20


def test_l_aeroport_est_surveille_et_le_large_n_est_a_personne(banc):
    """`Monde.zoneA` : devant l'aérogare, c'est l'aéroport, et ce n'est pas un
    refuge ; au milieu de l'eau que la carte a gagnée, c'est le large."""
    r = banc("""function (L, o) {""" + VIDER + """
        L.Jeu.commencer();
        const def = L.Monde.carte.def, TT = L.TT;
        const p = def.points_interet.find(function (q) { return q.slug === 'aeroport'; });
        poser(L, p.x, p.y);
        const z = L.Monde.zoneA(L.B.joueur.x, L.B.joueur.y);
        const large = L.Monde.zoneA(40 * TT, (def.hauteur - 5) * TT);
        return { zone: z && z.slug, refuge: L.Police.auRefuge(), large: large && large.slug,
                 hauteur: def.hauteur, lignes: def.sol.length };
    }""")
    assert r["zone"] == "aeroport" and r["refuge"] is False, r
    assert r["large"] == "large", r
    assert r["lignes"] == r["hauteur"]


def test_la_carte_cache_l_ile_jusqu_au_pont_fini(banc):
    """Mini-carte et grande carte : l'île est de l'eau, l'aérogare n'a pas de repère,
    et la grande carte s'arrête à la ville qu'on connaît — tant que a01 n'est pas
    faite. TÉMOIN : le pont fini, la mini-carte se recuit et tout apparaît."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const M = L.Monde, carte = M.carte, a = carte.def.aeroport, p = a.piste, j = L.B.joueur, TT = L.TT;
        const piste = [p.x + 5, p.y + 2], tablier = [a.pont.x + 1, a.pont.y + 2];
        function etat() {
            return { masquee: M.masquee(piste[0], piste[1]), couleur: M.couleurMiniA(piste[0], piste[1]),
                     tablier: M.couleurMiniA(tablier[0], tablier[1]),
                     lieux: L.Hud.lieuxSurLaCarte(carte).map(function (q) { return q.slug; }).indexOf('aeroport') >= 0,
                     hauteur: M.hauteurConnue(carte, j.y), surLIle: M.hauteurConnue(carte, (a.y + 10) * TT) };
        }
        const avant = etat(), miniAvant = M.miniCarte(), memeMini = M.miniCarte() === miniAvant;
        // La grande carte s'ouvre et se peint avec son cadrage.
        L.Jeu.ouvrirCarte(); o.frame(2); const ouverte = L.B.etat; L.Jeu.fermerCarte();
        L.B.partie.missionsFaites.a01 = true;
        const apres = etat(), recuite = M.miniCarte() !== miniAvant;
        return { avant: avant, apres: apres, memeMini: memeMini, recuite: recuite, ouverte: ouverte,
                 eau: '#24506f', route: M.couleurMini('#'), h: carte.h, connue: a.masque.carte_h };
    }""")
    avant, apres = r["avant"], r["apres"]
    assert avant["masquee"] and avant["couleur"] == r["eau"] and not avant["lieux"], avant
    assert avant["tablier"] == r["route"], "le tablier de La Pointe a disparu de la carte avec l'île"
    assert avant["hauteur"] == r["connue"] < r["h"] and avant["surLIle"] == r["h"], avant
    assert r["memeMini"], "la mini-carte se recuit à chaque image"
    assert r["ouverte"] == "carte"
    assert not apres["masquee"] and apres["couleur"] == r["route"] and apres["lieux"], f"le témoin ne mord pas : {apres}"
    assert apres["hauteur"] == r["h"] and r["recuite"], apres


#: ⚠️ LE LARGE REFUSÉ, jugé par la CAMÉRA : `Monde.majCamera` est enveloppée, et à
#: chaque image la vue — telle que `Jeu.rendre` la dessine, secousse comprise —
#: se compare au rectangle du masque. Un bateau, lancé à fond vers l'île, doit virer de
#: bord sans qu'une seule de ses tuiles passe à l'écran.
VIRER = """
    function rectDuMasque(L) {
        const m = L.Monde.carte.def.aeroport.masque, TT = L.TT;
        return { x0: m.x * TT, y0: m.y * TT, x1: (m.x + m.l) * TT, y1: (m.y + m.h) * TT };
    }
    function surveiller(L) {
        const M = L.Monde, ile = rectDuMasque(L), vieille = M.majCamera;
        const s = { vue: 0, images: 0 };
        M.majCamera = function () {
            vieille();
            s.images++;
            const c = L.B.cam, sec = c.secousse > 0.05 ? c.secousse * 4 : 0;
            const cx = c.x + L.VW / 2, cy = c.y + L.VH / 2, dx = L.VW / 2 + sec, dy = L.VH / 2 + sec;
            if (cx + dx > ile.x0 && cx - dx < ile.x1 && cy + dy > ile.y0 && cy - dy < ile.y1) s.vue++;
        };
        s.fin = function () { M.majCamera = vieille; };
        return s;
    }
    function lancer(L, o, tx, ty, angle, images, elan) {
        const j = L.B.joueur, TT = L.TT;
        // La coque d'un lancer précédent : on en descend, et elle s'en va (`vider`).
        if (j.dansVehicule) L.Vehicules.descendre(j, true);
        poser(L, tx, ty);
        j.invincible = 1e9;
        const v = L.Vehicules.creer('bateau', j.x, j.y, angle, { etat: 'stationne', aToi: true });
        L.Vehicules.monter(j, v);
        // `elan` : elle arrive DÉJÀ lancée, à fond — trop près pour que le virage suffise.
        if (elan) { v.vitesse = v.def.vitesse_max; v.vx = Math.cos(angle) * v.vitesse; v.vy = Math.sin(angle) * v.vitesse; }
        L.Monde.centrerCamera(j.x, j.y);
        const s = surveiller(L), depart = { x: v.x, y: v.y };
        let pire = -1e9, virage = 0, msg = null;
        o.touche('KeyW');
        for (let k = 0; k < images / 2; k++) {
            o.frame(2);
            // La ligne : de combien le centre de la coque est entré dans le large refusé.
            const z = L.Monde.largeRefuse();
            if (z) pire = Math.max(pire, Math.min(v.x - z.x0, z.x1 - v.x, v.y - z.y0, z.y1 - v.y));
            if (v.virage) { virage++; if (msg === null) msg = L.B.msg; }
        }
        o.relacher('KeyW');
        s.fin();
        return { vue: s.vue, images: s.images, pire: pire, virage: virage, msg: msg,
                 depart: depart, fin: { x: v.x, y: v.y, angle: v.angle }, dedans: j.dansVehicule === v };
    }
"""


def test_le_large_refuse_fait_virer_de_bord_avant_qu_on_voie_l_ile(banc):
    """« Même en bateau on ne puisse pas aller à l'île de l'aéroport avant que le pont
    soit réparé, une barrière invisible nous fait tourner de bord avant qu'on puisse
    voir l'île » (Martin, 22 sept. 2026). Gaz au plancher vers l'île, par le nord (sous
    La Pointe) et par l'ouest (le large de la ville) : la coque vire de bord toute
    seule, le HUD dit pourquoi, son centre ne passe jamais la ligne, elle repart d'où
    elle vient — et pas une image ne montre une tuile de l'île, bout du pont compris."""
    raison = aeroport.MASQUE["raisons"]["coque"]
    r = banc("""function (L, o) {""" + VIDER + VIRER + """
        L.Jeu.commencer();
        const M = L.Monde, TT = L.TT, m = M.carte.def.aeroport.masque, z = M.largeRefuse();
        const out = { z: z, TT: TT };
        // Par le nord : sous La Pointe, au milieu de l'île, vingt tuiles avant la ligne.
        out.nord = lancer(L, o, m.x + Math.floor(m.l / 2), Math.floor(z.y0 / TT) - 16, Math.PI / 2, 700);
        // Par l'ouest : le large de la ville, à la hauteur de la piste.
        out.ouest = lancer(L, o, Math.floor(z.x0 / TT) - 20, m.y + 20, 0, 700);
        // Déjà lancée à fond, à deux tuiles de la ligne : le virage n'a pas la place, la
        // ligne la retient quand même (`retenirAuLarge`), sans choc.
        out.lancee = lancer(L, o, m.x + Math.floor(m.l / 2), Math.floor(z.y0 / TT) - 2, Math.PI / 2, 400, true);
        return out;
    }""")
    z = r["z"]
    for cote, cap, recul in (("nord", -math.pi / 2, z["y0"] - r["nord"]["fin"]["y"]),
                             ("ouest", math.pi, z["x0"] - r["ouest"]["fin"]["x"]),
                             ("lancee", -math.pi / 2, z["y0"] - r["lancee"]["fin"]["y"])):
        c = r[cote]
        assert c["dedans"], f"{cote} : le joueur n'est plus dans sa coque — {c}"
        assert c["images"] > 300, f"{cote} : la caméra n'a pas tourné — {c}"
        assert c["virage"] > 0 and c["msg"] == raison, f"{cote} : la coque n'a pas viré de bord — {c}"
        assert c["pire"] <= 0, f"{cote} : la coque a passé la ligne de {c['pire']:.1f} px — {c}"
        assert c["vue"] == 0, f"{cote} : l'île s'est vue pendant {c['vue']} images — {c}"
        # Elle repart d'où elle vient, le moteur toujours au plancher : le nez vers le
        # large permis, et loin de la ligne.
        assert math.cos(c["fin"]["angle"] - cap) > 0.8, f"{cote} : le nez regarde encore l'île — {c}"
        assert recul > 3 * 16, f"{cote} : elle est restée collée à la ligne ({recul:.0f} px) — {c}"


def test_le_large_refuse_passe_a_une_vue_de_l_ile_et_ne_refuse_que_la_mer(banc):
    """La ligne, par construction : là où elle arrête le joueur, même la caméra qui
    regarde au plus loin DEVANT lui (la demi-vue et son avance au volant,
    `Monde.AVANCE_CAMERA`) s'arrête avant l'île. Le juge au bouton ne le dit pas seul :
    le virage détourne le nez avant que la caméra ait pris toute son avance. Et elle ne
    refuse que de la mer — pas une tuile de terre (hors de l'île) n'y est enfermée."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const M = L.Monde, TT = L.TT, c = M.carte, m = c.def.aeroport.masque, z = M.largeRefuse();
        const terres = [];
        for (let ty = Math.max(0, Math.floor(z.y0 / TT)); ty < Math.min(c.h, Math.ceil(z.y1 / TT)); ty++) {
            for (let tx = Math.max(0, Math.floor(z.x0 / TT)); tx < Math.min(c.w, Math.ceil(z.x1 / TT)); tx++) {
                if (tx >= m.x && tx < m.x + m.l && ty >= m.y && ty < m.y + m.h) continue;
                const g = M.glyphe(tx, ty);
                if (!M.estEau(tx, ty) && g !== 'M' && g !== 'C') terres.push([tx, ty, g]);
            }
        }
        return { z: z, m: m, avance: M.AVANCE_CAMERA, VW: L.VW, VH: L.VH, TT: TT, terres: terres.slice(0, 10) };
    }""")
    z, m, tt = r["z"], r["m"], r["TT"]
    assert r["avance"] >= 48, r
    assert z["y0"] + r["VH"] / 2 + r["avance"] < m["y"] * tt, f"arrêté à la ligne nord, on voit l'île : {r}"
    assert z["x0"] + r["VW"] / 2 + r["avance"] < m["x"] * tt, f"arrêté à la ligne ouest, on voit l'île : {r}"
    assert not r["terres"], f"de la terre enfermée dans le large refusé : {r['terres']}"


def test_le_large_refuse_ramene_le_nageur_de_la_travee(banc):
    """La travée manquante se nageait au café et à l'estomac plein ; plus jusqu'au
    bout : le nageur est arrêté à la ligne, le courant le ramène (le HUD dit pourquoi),
    et l'île ne passe pas à l'écran. Le souffle est mis hors de cause (un surplus sans
    fond) : c'est la ligne qu'on juge, pas la noyade."""
    raison = aeroport.MASQUE["raisons"]["nage"]
    r = banc("""function (L, o) {""" + VIDER + VIRER + """
        L.Jeu.commencer();
        const M = L.Monde, TT = L.TT, j = L.B.joueur, a = M.carte.def.aeroport, z = M.largeRefuse();
        poser(L, a.pont.x + 1, a.pont.y + a.pont.nord - 1);
        j.invincible = 1e9; j.surplus = 1e6; j.endurance = 100;
        const s = surveiller(L);
        let pire = -1e9, msg = null, courant = 0;
        o.touche('KeyS');
        for (let k = 0; k < 350; k++) {
            o.frame(2);
            pire = Math.max(pire, j.y - z.y0);
            if (j.courant && j.courant.t > 0) { courant++; if (msg === null) msg = L.B.msg; }
        }
        o.relacher('KeyS');
        s.fin();
        return { vue: s.vue, pire: pire, msg: msg, courant: courant, nage: j.nage, y: j.y, ligne: z.y0,
                 depart: (a.pont.y + a.pont.nord) * TT, vivant: j.vivant };
    }""")
    assert r["depart"] < r["ligne"], f"la ligne ne coupe pas la travée : {r}"
    assert r["courant"] > 0 and r["msg"] == raison, f"le courant n'a pas ramené le nageur : {r}"
    assert r["pire"] <= 0, f"le nageur a passé la ligne de {r['pire']:.1f} px : {r}"
    assert r["vue"] == 0, f"l'île s'est vue pendant {r['vue']} images : {r}"
    assert r["nage"] and r["y"] < r["ligne"], r


def test_le_mode_photo_ne_va_pas_ou_l_oeil_ne_va_pas(banc):
    """Le mode photo promène la caméra loin du joueur : collé à la ligne, le stick vers
    l'île, il glisse jusqu'au bord de l'île et pas un pixel plus loin."""
    r = banc("""function (L, o) {""" + VIDER + VIRER + """
        L.Jeu.commencer();
        const M = L.Monde, TT = L.TT, j = L.B.joueur, m = M.carte.def.aeroport.masque, z = M.largeRefuse();
        const ile = rectDuMasque(L);
        poser(L, m.x + Math.floor(m.l / 2), Math.floor(z.y0 / TT) - 1);
        L.Jeu.ouvrirPhoto();
        o.touche('KeyS');
        let vue = 0;
        for (let k = 0; k < 120; k++) {
            o.frame(2);
            const bas = L.B.cam.y + L.B.photo.dy + L.VH;
            if (bas > ile.y0) vue++;
        }
        o.relacher('KeyS');
        const bas = L.B.cam.y + L.B.photo.dy + L.VH;
        L.Jeu.fermerPhoto();
        return { vue: vue, bas: bas, ile: ile.y0, photo: !!L.B.photo };
    }""")
    assert r["vue"] == 0, f"la photo a montré l'île pendant {r['vue']} images : {r}"
    assert r["ile"] - r["bas"] < 16, f"la photo s'arrête avant le bord de l'île, pas à lui : {r}"


def test_le_pont_fini_le_large_s_ouvre(banc):
    """TÉMOIN : `a01` faite (le pont fini), la même coque lancée par le nord passe la
    ligne d'hier sans virer — c'est donc bien la mission, et elle seule, qui la tient."""
    r = banc("""function (L, o) {""" + VIDER + VIRER + """
        L.Jeu.commencer();
        const M = L.Monde, TT = L.TT, m = M.carte.def.aeroport.masque, z = M.largeRefuse();
        L.B.partie.missionsFaites.a01 = true;
        const c = lancer(L, o, m.x + Math.floor(m.l / 2), Math.floor(z.y0 / TT) - 20, Math.PI / 2, 700);
        return { c: c, ligne: z.y0, ouvert: M.largeRefuse() === null };
    }""")
    c = r["c"]
    assert r["ouvert"], r
    assert c["virage"] == 0, f"le large vire encore, le pont fini : {c}"
    assert c["fin"]["y"] > r["ligne"] + 3 * 16, f"le témoin ne mord pas : {c}"
