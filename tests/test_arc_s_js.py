"""L'arc S jusqu'à sa libération (M16, 29 sept. 2026) — s02, s05, s06, s09, s10 et s11 JOUÉES au bouton, sur le
modèle de `test_arc_q_js.py`.

⚠️ Depuis le 2 oct. 2026 (docs/jalons/des-missions-en-chapitres.md, vague S), La Shop est en CHAPITRES : s02 et s05 sont
les actes de _Ti-Loup et Gros-Boulon_, s06 et s10 les actes 2 et 3 de _Raymonde et le syndicat_ (s03, l'acte 1, est
jugé dans `test_cinq_missions_js.py`). Chaque juge commence le chapitre là où une vieille partie le reprendrait.

- s02 : Ti-Loup (devant la fourrière après s01 seulement), sa remorqueuse, trois épaves au lot (`boulots`).
- s05 : la berline de Prévost derrière l'usine, livrée au compacteur — `calme: boulonneux`.
- s06 : le char de Bob Sauvé filé jusqu'au Brouillard (`suivre`).
- s09 : le camion-citerne de Prévost qui saute, trois étoiles à semer.
- s10 : Raymonde menée à l'hôtel (`proteger`), et les gardiens de Prévost (`pieton: gardien`) qui arrivent.
- s11 : Prévost, dedans à son bureau de l'usine ; l'accord porté à Gros-Boulon **sans arme** — une arme au poing
  dans leur coin, c'est raté ; et **La Shop libérée, dans le monde** — cinq districts."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER
from test_arc_q_js import ESCORTE
from test_quatre_missions_js import RATTRAPER

AVANT_S = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 's01']"

#: Filer un char au pixel, collé derrière lui (le patron de `test_chute_du_pouce_js.py`).
FILER = """
  function filer(L, o, c) {
    const B = L.B, j = B.joueur;
    const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
    const arret = L.Histoire.tuileDeRue(j.x, j.y, 10);
    const mien = L.Vehicules.creer('auto', arret.x, arret.y, CAP[arret.sens], { etat: 'stationne' });
    j.x = mien.x + 10; j.y = mien.y; L.Entites.indexer();
    L.Vehicules.monter(j, mien); L.Entites.indexer();
    const e0 = etape(L);
    let i = 0;
    for (; i < 20000 && B.partie.mission && B.partie.mission.etape === e0; i++) {
      if (!c.attendLeJoueur) {
        mien.x = c.x - Math.cos(c.angle) * 96; mien.y = c.y - Math.sin(c.angle) * 96;
        mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
      }
      o.frame(1); ecouter(L);
    }
    jouer(L, o);
    return i;
  }
"""


def test_s02_la_remorqueuse_de_ti_loup_trois_epaves(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        recharger(L);
        const avant = !!L.Histoire.donneur('tiloup');
        faites(L, ['s01']);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('tiloup');
        commencer(L, o, 'ti_loup_et_gros_boulon'); jouer(L, o);
        const v = B.mission.vehicule || (B.mission.chars && B.mission.chars[0]);
        const f = L.Histoire.lieu('fourriere');
        const remorqueuse = { slug: v && v.slug, lot: v ? Math.round(Math.hypot(v.x - f.x, v.y - f.y) / 16) : null };
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const b = L.Missions.boulot;
        const contrats = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        b.faits.remorquage = B.mission.boulotsDepart + 3; jouer(L, o);
        const retour = { etape: etape(L) };
        versLui(L, 'tiloup'); jouer(L, o, 20);
        return { avant: avant, dispo: dispo && dispo.slug, remorqueuse: remorqueuse, contrats: contrats, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.s02, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["avant"] is False and r["dispo"] == "ti_loup_et_gros_boulon", r
    assert r["remorqueuse"]["slug"] == "remorqueuse" and r["remorqueuse"]["lot"] <= 10, r["remorqueuse"]
    assert r["contrats"]["etape"] == 2 and r["contrats"]["ligne"].endswith("0/3"), r["contrats"]
    assert r["retour"]["etape"] == 3
    for dite in ("pendant:tiloup:2", "pendant:tiloup:3", "pendant:tiloup:4", "pendant:boulon:4"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [250]


def test_s05_la_berline_de_prevost_au_compacteur_et_les_boulonneux_te_laissent_vivre(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + RATTRAPER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_S + """.concat(['s02']));
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('boulon');
        commencer(L, o, 'ti_loup_et_gros_boulon'); jouer(L, o);
        const v = B.mission.vehicule || (B.mission.chars && B.mission.chars[0]);
        const u = L.Histoire.lieu('usine');
        const berline = { slug: v && v.slug, usine: v ? Math.round(Math.hypot(v.x - u.x, v.y - u.y) / 16) : null };
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const route = { etape: etape(L) };
        conduireA(L, o, v, 'fourriere');
        const livree = { etape: etape(L) };
        versLui(L, 'boulon'); finir(L, o);
        return { dispo: dispo && dispo.slug, berline: berline, route: route, livree: livree, dites: dites,
                 fait: !!p.missionsFaites.s05 && !!p.missionsFaites.ti_loup_et_gros_boulon, argent: argent.map(function (a) { return a.montant; }), calmes: p.calmes.slice() };
    }""")
    assert r["dispo"] == "ti_loup_et_gros_boulon", "une vieille partie qui a fait s02 : Gros-Boulon donne l'acte 2"
    assert r["berline"]["slug"] == "luxe" and r["berline"]["usine"] <= 24, r["berline"]
    assert r["route"]["etape"] == 6 and r["livree"]["etape"] == 7, r
    for dite in ("pendant:boulon:4", "pendant:boulon:5", "pendant:boulon:6", "pendant:boulon:7"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [400] and r["calmes"] == ["boulonneux"], r


def test_s06_le_char_de_bob_sauve_file_jusqu_au_bar(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + FILER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02', 's03']);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibles().some(function (m) { return m.slug === 'raymonde_et_le_syndicat'; });
        commencer(L, o, 'raymonde_et_le_syndicat'); jouer(L, o);
        const c = B.mission.suivi;
        const images = filer(L, o, c);
        const bar = L.Histoire.lieu('bar');
        const file = { images: images, etape: etape(L), dBar: Math.round(Math.hypot(bar.x - c.x, bar.y - c.y) / 16) };
        versLui(L, 'raymonde'); finir(L, o);
        return { dispo: dispo, file: file, dites: dites, fait: !!p.missionsFaites.s06, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] is True
    assert r["file"]["etape"] == 9 and r["file"]["dBar"] < 10 and r["file"]["images"] > 20 * 60, r["file"]
    for dite in ("pendant:raymonde:7", "pendant:raymonde:8", "pendant:raymonde:9"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [250]


def test_s09_le_camion_citerne_saute_on_seme_trois_etoiles(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_S + """.concat(['s02', 's05']));
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('boulon');
        commencer(L, o, 's09'); jouer(L, o);
        const c = B.mission.chars && B.mission.chars[0];
        const u = L.Histoire.lieu('usine');
        const camion = { slug: c && c.slug, usine: c ? Math.round(Math.hypot(c.x - u.x, c.y - u.y) / 16) : null };
        j.x = c.x + 60; j.y = c.y; L.Entites.indexer();
        c.etat = 'epave'; jouer(L, o);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        versLui(L, 'boulon'); finir(L, o);
        return { dispo: dispo && dispo.slug, camion: camion, semer: semer, cache: cache, dites: dites,
                 fait: !!p.missionsFaites.s09, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "s09"
    assert r["camion"]["slug"] == "camion" and r["camion"]["usine"] <= 30, r["camion"]
    assert r["semer"]["etape"] == 1 and r["semer"]["etoiles"] >= 3 and r["cache"]["apres"] == 0, r
    for dite in ("pendant:boulon:1", "pendant:boulon:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [600]


def test_s10_raymonde_menee_au_maire_et_les_gardiens_de_prevost(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + ESCORTE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02', 's03', 's06']);
        const j = recharger(L);
        const argent = paiements(L);
        commencer(L, o, 'raymonde_et_le_syndicat'); jouer(L, o);
        const c = B.mission.protege;
        const suit = rejoindre(L, o, c);
        arriverAvec(L, o, c, 'hotel'); jouer(L, o, 30);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 12; });
        const h = L.Histoire.lieu('hotel');
        const gardiens = { n: eux.length, arch: eux.map(function (e) { return e.arch; }),
                           courent: eux.every(function (e) { return e.etat === 'attaque_joueur'; }),
                           loin: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - h.x, e.y - h.y) / 16); })) };
        eux.forEach(function (e) { L.Entites.assommer(e); });
        finir(L, o);
        return { personnage: c && c.personnage, suit: suit, gardiens: gardiens, dites: dites,
                 fait: !!p.missionsFaites.s10 && !!p.missionsFaites.raymonde_et_le_syndicat, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["personnage"] == "raymonde" and r["suit"] is True, r
    g = r["gardiens"]
    assert g["n"] == 2 and set(g["arch"]) == {"gardien"} and g["courent"] and g["loin"] <= 20, g
    for dite in ("pendant:raymonde:10", "pendant:raymonde:11", "pendant:raymonde:12"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300]


def _s11(banc, arme):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02', 's03', 's06', 's10', 's01', 's02', 's05', 's09']);
        const j = recharger(L);
        p.libere = ['faubourg', 'quais', 'erables', 'pointe']; p.faubourgLibere = true;
        const argent = paiements(L);
        const piece = dedans(L, o, 'usine');
        const prevost = !!B.entites.find(function (e) { return e.personnage === 'prevost'; });
        serrer(L, o, 'prevost');
        const debut = p.mission ? p.mission.slug : null;
        passer(L, o);
        sortir(L, o);
        const ligne = L.Histoire.ligneObjectif();
        if (""" + ("true" if arme else "false") + """) {
            p.armes.pistolet = { mun: 12, usure: 0 }; j.arme = 'pistolet'; p.arme = 'pistolet';
            const cour = L.Histoire.resoudre('zone:boulonneux', null);
            j.x = cour.x; j.y = cour.y; L.Entites.indexer(); jouer(L, o, 4);
            return { piece: piece, prevost: prevost, debut: debut, rate: !p.mission, echecs: p.stats.echecs || 0, libere: p.libere.slice() };
        }
        const accueil = serrer(L, o, 'boulon');
        finir(L, o);
        const cour = L.Histoire.resoudre('zone:boulonneux', null);
        return { piece: piece, prevost: prevost, debut: debut, ligne: ligne, accueil: accueil, dites: dites,
                 fait: !!p.missionsFaites.s11, argent: argent.map(function (a) { return a.montant; }), libere: p.libere.slice(),
                 manchette: p.manchetteForcee || null, chasse: L.Entites.gangChasse('boulonneux'),
                 horsJeu: L.Territoires.horsJeu('boulonneux'), nom: L.Hud.nomIci(j, L.Monde.zoneA(cour.x, cour.y)) };
    }""")


def test_s11_une_arme_au_poing_chez_les_boulonneux_c_est_rate(banc):
    r = _s11(banc, arme=True)
    assert r["piece"] == "usine" and r["prevost"] and r["debut"] == "s11", f"Prévost, à son bureau, donne s11 : {r}"
    assert r["rate"] is True and r["echecs"] == 1 and "shop" not in r["libere"], r


def test_s11_l_accord_sans_arme_puis_la_shop_est_libre_cinq_districts(banc):
    r = _s11(banc, arme=False)
    assert r["ligne"].startswith("PORTE L'ACCORD À GROS-BOULON"), r["ligne"]
    assert r["accueil"] == "accueil", "Gros-Boulon lit l'accord à la poignée de main"
    assert r["fait"] is True and r["argent"] == [500]
    assert r["libere"] == ["faubourg", "quais", "erables", "pointe", "shop"], r["libere"]
    assert r["manchette"] == "prevost_rembauche" and r["chasse"] and r["horsJeu"], r
    assert r["nom"] == {"nom": "La Shop", "gang": None}, r["nom"]
