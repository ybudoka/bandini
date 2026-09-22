"""L'aéroport, côté jeu : fermé par étages, et peint.

⚠️ Chaque barrière se juge au BOUTON, comme le joueur la rencontre — pousser le
stick contre elle —, et chacune porte son TÉMOIN : la mission qu'elle attend,
faite, et on passe. Sans lui, « on ne passe pas » pourrait vouloir dire que le
banc a posé le joueur dans un mur.
"""

from app import carte

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
