"""La liste du Norvégien (M16, vague 23, 1er oct. 2026) — q14 JOUÉE au bouton : la berline derrière l'hôtel, le quai sans
une bosse, une demi-journée de jeu pendant que Sven la charge, le coupé derrière chez Mado, le quai, la passerelle."""

import json

from test_erables_shop_suite_js import AIDES as AIDES_V21

from app import missions

AVANT = json.dumps([m["slug"] for m in missions.CATALOGUE if m["slug"] not in ("q14", "m97", "m98", "m99")])

AIDES = AIDES_V21 + """
  function partieQ14(L) { faites(L, """ + AVANT + """); return recharger(L); }
"""


def _q14(banc, bosse=False):
    return banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partieQ14(L);
        const argent = paiements(L);
        const pris = chezLui(L, o, 'sven');
        const v = B.mission.vehicule;
        const berline = { slug: v && v.slug, hotel: loin(v, L.Histoire.lieu('hotel')) };
        monterDans(L, o, v);
        poser(L, v, L.Histoire.lieuDeLivraison('cantine')); jouer(L, o, 8);
        const livre1 = { etape: etape(L), aPied: !j.dansVehicule };
        // Une demi-journée : une heure ne suffit pas, douze oui.
        p.heure = (p.heure + 1 / 24) % 1; jouer(L, o, 4);
        const uneHeure = etape(L);
        p.jour += 1; jouer(L, o, 6);
        const charge = etape(L);
        const w = B.mission.vehicule;
        const coupe = { slug: w && w.slug, mado: loin(w, L.Histoire.lieu('casse_croute')) };
        monterDans(L, o, w);
        if (""" + ("true" if bosse else "false") + """) { w.chocs = (w.chocs || 0) + 1; w.vie -= 10; }
        poser(L, w, L.Histoire.lieuDeLivraison('cantine')); jouer(L, o, 8);
        const livre2 = etape(L);
        versLui(L, 'sven'); finir(L, o);
        return { pris: pris, berline: berline, livre1: livre1, uneHeure: uneHeure, charge: charge, coupe: coupe,
                 livre2: livre2, dites: dites, fait: !!p.missionsFaites.q14, argent: montants(argent) };
    }""")


def test_q14_deux_modeles_une_demi_journee_entre_les_deux_sans_une_bosse(banc):
    r = _q14(banc)
    assert r["pris"] == {"dispo": "q14", "mission": "q14"}, r["pris"]
    assert r["berline"]["slug"] == "luxe" and r["berline"]["hotel"] <= 16, r["berline"]
    assert r["livre1"] == {"etape": 2, "aPied": True}, r["livre1"]
    assert r["uneHeure"] == 2 and r["charge"] == 3, f"une heure ne suffit pas, douze oui : {r}"
    assert r["coupe"]["slug"] == "sport" and r["coupe"]["mado"] <= 16, r["coupe"]
    assert r["livre2"] == 5, r
    for dite in ("pendant:sven:0", "pendant:sven:1", "pendant:sven:2", "pendant:sven:3", "pendant:sven:4", "pendant:sven:5"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [375], r["argent"]


def test_q14_une_bosse_sur_le_coupe_coute_la_prime(banc):
    r = _q14(banc, bosse=True)
    assert r["fait"] is True and r["argent"] == [250], r["argent"]
