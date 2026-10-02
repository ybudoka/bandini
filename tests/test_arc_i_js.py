"""L'arc I, l'Île-aux-Corneilles (M16, vague 13, 30 sept. 2026) — q08 et i01 à i05 JOUÉES au bouton.

- q08 : Bérubé au bout du quai du traversier ; le moteur file dans un pick-up, on le rattrape, on le rapporte.
- i01 : la chaloupe du capitaine, la baie traversée jusqu'au hangar de l'île, et Léo à pied (sa poignée de main).
- i02 : Sœur Jeanne (sur l'île), Ti-Loup au lot, deux cents piastres, la cloche traversée en chaloupe, la sœur.
- i03 : de nuit, sans une étoile : le hangar de Sven, ses caisses, le retour par l'eau, Josée au bar.
- i05 : la conserverie qui brûle près du hangar, l'extincteur de la sœur, trois matelots, la sœur."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER
from test_quatre_missions_js import RATTRAPER

BASE = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']

EAU = """
  function embarquer(L, o, v) {
    const j = L.B.joueur;
    aPied(L); j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o, 3);
    return j.dansVehicule === v;
  }
  // La chaloupe menée jusqu'au point de livraison (un amarrage) : le trajet sur l'eau a son juge (m52, m53).
  function accoster(L, o, v, lieu) {
    const j = L.B.joueur, l = L.Histoire.lieuDeLivraison(lieu);
    v.x = l.x; v.y = l.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); jouer(L, o, 6);
    return !!l;
  }
  function aTerre(L, o) { L.Vehicules.descendre(L.B.joueur, true); L.Entites.indexer(); jouer(L, o, 2); }
"""


def _faites(*plus):
    return str(BASE + list(plus))


def test_q08_le_moteur_du_capitaine(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + RATTRAPER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites() + """);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('berube') || {}).slug || null;
        serrer(L, o, 'berube'); passer(L, o); ecouter(L);
        const f = B.mission.fuyard;
        j.x = f.x + 40; j.y = f.y; L.Entites.indexer(); jouer(L, o, 300);
        rattraper(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        versLui(L, 'berube'); finir(L, o);
        return { dispo: dispo, retour: retour, dites: dites, fait: !!p.missionsFaites.q08,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    # q08 et i01 sont les actes du _Moteur du capitaine_ (2 oct. 2026, marqueurs 0 et 3).
    assert r["dispo"] == "le_moteur_du_capitaine", r
    assert r["retour"]["etape"] == 2 and r["retour"]["ligne"].startswith("RAPPORTE LE MOTEUR"), r["retour"]
    for dite in ("pendant:berube:1", "pendant:berube:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [200], r


def test_i01_la_chaloupe_jusqu_au_hangar_de_l_ile(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + EAU + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("q08") + """);
        const j = recharger(L);
        const argent = paiements(L);
        serrer(L, o, 'berube'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        const v = B.mission.vehicule;
        const chaloupe = { slug: v && v.slug, eau: v ? L.Monde.estEau(Math.floor(v.x / 16), Math.floor(v.y / 16)) : null };
        const monte = embarquer(L, o, v) && etape(L);
        accoster(L, o, v, 'amarrage:hangar_ile');
        const accoste = etape(L);
        aTerre(L, o);
        const accueil = serrer(L, o, 'leo');
        finir(L, o);
        return { mission: mission, chaloupe: chaloupe, monte: monte, accoste: accoste, accueil: accueil, dites: dites,
                 fait: !!p.missionsFaites.i01, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "le_moteur_du_capitaine", "le capitaine donne l'acte 2 à qui a fait q08"
    assert r["chaloupe"] == {"slug": "bateau", "eau": True}, r["chaloupe"]
    assert r["monte"] == 5 and r["accoste"] == 6, r
    assert r["accueil"] == "accueil", r
    for dite in ("pendant:berube:3", "pendant:berube:4", "pendant:berube:5", "pendant:berube:6", "accueil:leo:6"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [120], r


def test_i02_la_cloche_rachetee_et_ramenee_par_l_eau(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + EAU + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("q08", "i01", "s01", "s02") + """);
        const j = recharger(L);
        p.argent = 1000;
        const argent = paiements(L);
        serrer(L, o, 'jeanne'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        jouer(L, o, 10);   // le `pendant` de l'étape 0 part une image après l'intro : on l'écoute avant de serrer
        serrer(L, o, 'tiloup');
        jouer(L, o, 10);
        const paye = { etape: etape(L), argent: p.argent };
        const v = B.mission.vehicule;
        embarquer(L, o, v);
        accoster(L, o, v, 'amarrage:chapelle');
        const accoste = etape(L);
        aTerre(L, o);
        versLui(L, 'jeanne'); finir(L, o);
        return { mission: mission, paye: paye, slug: v && v.slug, accoste: accoste, dites: dites,
                 fait: !!p.missionsFaites.i02, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    # i02 et i05 sont les actes de _Sœur Jeanne_ (2 oct. 2026, marqueurs 0 et 6).
    assert r["mission"] == "soeur_jeanne", r
    assert r["paye"]["etape"] == 3 and r["paye"]["argent"] == 800, r["paye"]
    assert r["slug"] == "bateau" and r["accoste"] == 5, r
    for dite in ("accueil:tiloup:1", "pendant:jeanne:2", "pendant:jeanne:3", "pendant:jeanne:4"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150], r


def test_i03_les_caisses_du_hangar_sans_nom(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + EAU + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("e01", "q02", "q04", "q08", "i01", "v01", "q11") + """);
        const j = recharger(L);
        const argent = paiements(L);
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        sortir(L, o);
        const b = L.Histoire.lieu('bar');
        j.x = b.x; j.y = b.y; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const v = B.mission.vehicule;
        embarquer(L, o, v);
        accoster(L, o, v, 'amarrage:hangar_ile');
        const ile = etape(L);
        aTerre(L, o);
        const caisses = B.entites.find(function (e) { return e.objetDeMission === 'caisses_de_sven'; });
        const h = L.Histoire.lieu('hangar_ile');
        const posees = caisses ? Math.round(Math.hypot(caisses.x - h.x, caisses.y - h.y) / 16) : null;
        j.x = caisses.x; j.y = caisses.y; L.Entites.indexer(); jouer(L, o, 4);
        const prises = etape(L);
        embarquer(L, o, v);
        accoster(L, o, v, 'amarrage:bar');
        const retour = etape(L);
        aTerre(L, o);
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); finir(L, o);
        return { mission: mission, ile: ile, posees: posees, prises: prises, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.i03, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "i03", r
    assert r["ile"] == 3 and r["posees"] is not None and r["posees"] <= 3 and r["prises"] == 4 and r["retour"] == 5, r
    for dite in ("pendant:josee:2", "pendant:josee:3", "pendant:josee:4", "pendant:josee:5"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [400], r


def test_i05_la_conserverie_brule_pres_du_hangar(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("q08", "i01", "s01", "s02", "i02") + """);
        const j = recharger(L);
        const argent = paiements(L);
        serrer(L, o, 'jeanne'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        const feu = B.mission.feu, h = L.Histoire.lieu('hangar_ile');
        const ou = feu ? L.Incendies.position(feu) : null;
        const brule = { feu: !!feu, arme: j.arme, pres: ou ? Math.round(Math.hypot(ou.x - h.x, ou.y - h.y) / 16) : null };
        aPied(L); o.touche('KeyJ');
        for (let k = 0; k < 400 && etape(L) === 7; k++) { j.x = ou.x; j.y = ou.y + 18; j.angle = -Math.PI / 2; o.frame(1); ecouter(L); }
        o.relacher('KeyJ'); o.frame(1);
        const eteint = etape(L);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 8; });
        const matelots = { n: eux.length, arch: eux.map(function (e) { return e.arch; }) };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const retour = etape(L);
        versLui(L, 'jeanne'); finir(L, o);
        return { mission: mission, brule: brule, eteint: eteint, matelots: matelots, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.i05, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "soeur_jeanne", r
    assert r["brule"]["feu"] and r["brule"]["arme"] == "extincteur" and r["brule"]["pres"] <= 8, r["brule"]
    assert r["eteint"] == 8 and r["matelots"]["n"] == 3 and set(r["matelots"]["arch"]) == {"matelot"}, r
    assert r["retour"] == 9, r
    for dite in ("pendant:jeanne:6", "pendant:jeanne:7", "pendant:jeanne:8", "pendant:jeanne:9"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [200], r


# --- L'île, deuxième moitié (vague 14, 30 sept. 2026) : le chalutier de Sven coulé, la cache de Rocco, la traverse de
# l'urgence.

def test_i06_le_chalutier_de_sven_coule_a_quai(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + EAU + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("e01", "q02", "q04", "q08", "i01", "v01", "q11", "i03") + """);
        const j = recharger(L);
        const argent = paiements(L);
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        sortir(L, o);
        const v = B.mission.vehicule;
        embarquer(L, o, v); jouer(L, o, 6);
        const c = B.mission.entites.find(function (e) { return e.type === 'vehicule' && e.slug === 'chalutier'; });
        const cible = { etape: etape(L), chalutier: !!c, eau: c ? L.Monde.estEau(Math.floor(c.x / 16), Math.floor(c.y / 16)) : null,
                        arme: j.arme };
        L.Vehicules.endommager(c, 99999, j); jouer(L, o, 10);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); finir(L, o);
        return { mission: mission, cible: cible, semer: semer, cache: cache, dites: dites, fait: !!p.missionsFaites.i06,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "i06", r
    assert r["cible"] == {"etape": 1, "chalutier": True, "eau": True, "arme": "pistolet"}, r["cible"]
    assert r["semer"]["etape"] == 2 and r["semer"]["etoiles"] >= 3 and r["cache"]["apres"] == 0, r
    for dite in ("pendant:josee:1", "pendant:josee:2", "pendant:josee:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [500], r


def test_i08_la_cache_de_rocco_sous_la_chapelle(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + EAU + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("e01", "q02", "q04", "q08", "i01", "v01", "q11", "i03", "i06", "d01", "d02", "d03", "d04", "d05") + """);
        const j = recharger(L);
        const argent = paiements(L);
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        sortir(L, o);
        const v = B.mission.vehicule;
        embarquer(L, o, v);
        accoster(L, o, v, 'amarrage:chapelle');
        const ile = etape(L);
        aTerre(L, o);
        const cache = B.entites.find(function (e) { return e.objetDeMission === 'cache_de_rocco'; });
        const c = L.Histoire.lieu('chapelle');
        const posee = cache ? Math.round(Math.hypot(cache.x - c.x, cache.y - c.y) / 16) : null;
        j.x = cache.x; j.y = cache.y; L.Entites.indexer(); jouer(L, o, 4);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 3; });
        const matelots = { etape: etape(L), n: eux.length };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        embarquer(L, o, v);
        accoster(L, o, v, 'amarrage:bar');
        const retour = etape(L);
        aTerre(L, o);
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); finir(L, o);
        return { mission: mission, ile: ile, posee: posee, matelots: matelots, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.i08, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "i08", r
    assert r["ile"] == 2 and r["posee"] is not None and r["posee"] <= 3, r
    assert r["matelots"] == {"etape": 3, "n": 2} and r["retour"] == 5, r
    for dite in ("pendant:josee:2", "pendant:josee:3", "pendant:josee:4", "pendant:josee:5"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [1200], r


def test_h08_la_traverse_de_l_urgence(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + EAU + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _faites("h01", "h02", "d01", "h03", "h04", "h05", "h06", "q08", "i01") + """);
        const j = recharger(L);
        const argent = paiements(L);
        dedans(L, o, 'hopital'); serrer(L, o, 'lachance'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        sortir(L, o);
        const v = B.mission.vehicule;
        embarquer(L, o, v);
        accoster(L, o, v, 'amarrage:chapelle');
        const ile = etape(L);
        aTerre(L, o);
        const accueil = serrer(L, o, 'jeanne');
        const confie = etape(L);
        embarquer(L, o, v);
        accoster(L, o, v, 'amarrage:hopital');
        finir(L, o);
        return { mission: mission, slug: v.slug, ile: ile, accueil: accueil, confie: confie, dites: dites,
                 fait: !!p.missionsFaites.h08, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "h08" and r["slug"] == "bateau", r
    assert r["ile"] == 2 and r["accueil"] == "accueil" and r["confie"] == 3, r
    for dite in ("pendant:lachance:0", "pendant:lachance:1", "accueil:jeanne:2", "pendant:lachance:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [250], r
