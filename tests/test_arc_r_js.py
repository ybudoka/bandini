"""L'arc R, Roy contre Bouchard (M16, vague 10, 30 sept. 2026) — r02 à r05 JOUÉES au bouton.

- Roy n'est au poste qu'après r01 (`arrive_apres`), dedans (`point:roy`).
- r02 : le carnet au coffre de l'hôtel (la poignée de main de Norbert), rapporté à Roy ; le choix s'ouvre.
- r03 : Mado jase, le char du sergent filé jusqu'à l'hôtel, Roy ; cinq pages de moins, et r04 fermée.
- r04 : l'auto-patrouille de Roy volée dans la ruelle du poste, semée, livrée au lot ; r03 fermée.
- r05 : le camion des pièces à conviction, semé, livré au garage."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER

AVANT_R = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'r01']

CHEZ_ROY = """
  function chezRoy(L, o) {
    const piece = dedans(L, o, 'poste');
    const la = !!L.B.entites.find(function (e) { return e.personnage === 'roy'; });
    if (la) serrer(L, o, 'roy');
    const mission = L.B.partie.mission ? L.B.partie.mission.slug : null;
    passer(L, o); ecouter(L);
    sortir(L, o);
    return { piece: piece, la: la, mission: mission };
  }
  function chezBouchard(L, o) {
    dedans(L, o, 'casse_croute');
    serrer(L, o, 'bouchard');
    const mission = L.B.partie.mission ? L.B.partie.mission.slug : null;
    passer(L, o); ecouter(L);
    sortir(L, o);
    return mission;
  }
  // Voler un char de mission, puis le semer (caché dedans), puis y remonter.
  function volerEtSemer(L, o) {
    const B = L.B, j = B.joueur, v = B.mission.vehicule;
    j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
    const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
    const cache = seCacher(L, o);
    j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
    return { v: v, slug: v.slug, semer: semer, cache: cache };
  }
"""


def _avant(*plus):
    return str(AVANT_R + list(plus))


def test_r02_roy_reprend_son_carnet_et_pose_le_marche(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_ROY + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        recharger(L);
        dedans(L, o, 'poste');
        const avant = !!B.entites.find(function (e) { return e.personnage === 'roy'; });
        sortir(L, o);
        faites(L, ['r01']);
        const j = recharger(L);
        const argent = paiements(L);
        const chez = chezRoy(L, o);
        dedans(L, o, 'hotel'); serrer(L, o, 'norbert'); sortir(L, o);
        const carnet = etape(L);
        dedans(L, o, 'poste'); serrer(L, o, 'roy'); finir(L, o);
        const choix = ['r03', 'r04'].map(function (s) { return L.Histoire.disponibles().some(function (m) { return m.slug === s; }); });
        return { avant: avant, chez: chez, carnet: carnet, dites: dites, choix: choix,
                 fait: !!p.missionsFaites.r02, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["avant"] is False, "pas de Roy au poste avant r01"
    assert r["chez"] == {"piece": "poste", "la": True, "mission": "r02"}, r["chez"]
    assert r["carnet"] == 1, r
    for dite in ("pendant:roy:0", "accueil:norbert:0", "pendant:roy:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150], r
    assert r["choix"] == [True, True], "après r02, les deux côtés du choix"


def test_r03_le_sergent_file_jusqu_a_l_hotel_ferme_r04(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_ROY + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant("r02") + """);
        const j = recharger(L);
        p.casier = 8;
        const argent = paiements(L);
        const chez = chezRoy(L, o);
        serrer(L, o, 'mado');
        const c = B.mission.suivi;
        const char = { etape: etape(L), slug: c && c.slug, attend: c && c.attendLeJoueur };
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const arret = L.Histoire.tuileDeRue(j.x, j.y, 10);
        const mien = L.Vehicules.creer('auto', arret.x, arret.y, CAP[arret.sens], { etat: 'stationne' });
        j.x = mien.x + 10; j.y = mien.y; L.Entites.indexer();
        L.Vehicules.monter(j, mien); L.Entites.indexer();
        let i = 0;
        for (; i < 20000 && p.mission && p.mission.etape === 1; i++) {
            if (!c.attendLeJoueur) {
                mien.x = c.x - Math.cos(c.angle) * 96; mien.y = c.y - Math.sin(c.angle) * 96;
                mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
            }
            o.frame(1); ecouter(L);
        }
        jouer(L, o, 10);   // le `pendant` de l'étape suivante part une image après : on l'écoute avant d'entrer
        const h = L.Histoire.lieu('hotel');
        const file = { images: i, etape: etape(L), dHotel: Math.round(Math.hypot(h.x - c.x, h.y - c.y) / 16) };
        const piece = dedans(L, o, 'poste'); const serre = serrer(L, o, 'roy');
        const apres = { piece: piece, serre: serre, etape: etape(L), mission: p.mission && p.mission.slug, echecs: p.stats.echecs || 0 };
        finir(L, o);
        return { chez: chez, char: char, file: file, apres: apres, dites: dites, casier: p.casier, fermees: p.fermees,
                 fait: !!p.missionsFaites.r03, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "r03", r["chez"]
    assert r["char"] == {"etape": 1, "slug": "police", "attend": True}, r["char"]
    assert r["file"]["etape"] == 2 and r["file"]["dHotel"] < 10 and r["file"]["images"] > 10 * 60, r["file"]
    for dite in ("accueil:mado:0", "pendant:roy:1", "pendant:roy:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [500] and r["casier"] == 3, r
    assert "r04" in r["fermees"], "le stool de Roy ne travaille plus pour le sergent"


def test_r04_l_auto_de_roy_au_lot_ferme_r03(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_ROY + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant("r02") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const mission = chezBouchard(L, o);
        const po = L.Histoire.lieu('poste');
        j.x = po.x; j.y = po.y; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const nuit = etape(L);
        const vol = volerEtSemer(L, o);
        const f = L.Histoire.lieu('fourriere');
        vol.v.x = f.x; vol.v.y = f.y; vol.v.vitesse = 0; j.x = vol.v.x; j.y = vol.v.y; L.Entites.indexer();
        finir(L, o);
        return { mission: mission, nuit: nuit, slug: vol.slug, semer: vol.semer, cache: vol.cache, dites: dites,
                 fermees: p.fermees, ami: p.sergentAmi, fait: !!p.missionsFaites.r04,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "r04", r
    assert r["nuit"] == 1 and r["slug"] == "police", r
    assert r["semer"]["etape"] == 2 and r["semer"]["etoiles"] >= 2 and r["cache"]["apres"] == 0, r
    for dite in ("pendant:bouchard:1", "pendant:bouchard:2", "pendant:bouchard:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [500] and r["ami"] is True, r
    assert "r03" in r["fermees"], "le sergent a gagné : plus de stool pour Roy"


def test_r05_le_camion_des_pieces_a_conviction_au_garage(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_ROY + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant("r02", "r04") + """);
        const j = recharger(L);
        const argent = paiements(L);
        const mission = chezBouchard(L, o);
        const po = L.Histoire.lieu('poste');
        j.x = po.x; j.y = po.y; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const vol = volerEtSemer(L, o);
        const baie = L.Histoire.lieuDeLivraison('garage');
        vol.v.x = baie.x; vol.v.y = baie.y; vol.v.vitesse = 0; j.x = vol.v.x; j.y = vol.v.y; L.Entites.indexer();
        finir(L, o);
        return { mission: mission, slug: vol.slug, semer: vol.semer, cache: vol.cache, dites: dites,
                 fait: !!p.missionsFaites.r05, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "r05", r
    assert r["slug"] == "camion" and r["semer"]["etape"] == 2 and r["semer"]["etoiles"] >= 2, r
    assert r["cache"]["apres"] == 0, r
    for dite in ("pendant:bouchard:1", "pendant:bouchard:2", "pendant:bouchard:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [250], r
