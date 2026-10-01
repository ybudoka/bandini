"""La liste de Ti-Loup (M16, les deux restes, 1er oct. 2026) — q15, la variante de q14 pour qui a choisi Josée (q11),
JOUÉE au bouton : le taxi derrière le terminus, le lot de la fourrière sans une bosse, une demi-journée pendant que
Ti-Loup le démonte, le cabriolet rose derrière le dépanneur, le lot, sa cour.

Et l'ardoise du quai qui suit le choix (la fiche : « Sven — ou Ti-Loup si on l'a brûlé — affiche quatre modèles ») :
après q11, Sven ne prend plus rien à sa jetée ; après q15, Ti-Loup prend la liste à son lot."""

import json

from test_erables_shop_suite_js import AIDES as AIDES_V21
from test_liste_du_quai_js import AU_QUAI

from app import economie, missions

#: Tout, sauf q15 — et sauf le côté de Sven (q10, q14) : c'est la partie de qui a choisi Josée.
AVANT = json.dumps([m["slug"] for m in missions.CATALOGUE if m["slug"] not in ("q15", "q10", "q14", "m97", "m98", "m99")])

AIDES = AIDES_V21 + AU_QUAI + """
  function partieQ15(L, plus) { faites(L, """ + AVANT + """.concat(plus || [])); return recharger(L); }
"""


def _q15(banc, bosse=False):
    return banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        const j = partieQ15(L);
        const argent = paiements(L);
        const pris = chezLui(L, o, 'tiloup');
        const v = B.mission.vehicule;
        const taxi = { slug: v && v.slug, terminus: loin(v, L.Histoire.lieu('terminus')) };
        monterDans(L, o, v);
        poser(L, v, L.Histoire.lieuDeLivraison('fourriere')); jouer(L, o, 8);
        const livre1 = { etape: etape(L), aPied: !j.dansVehicule };
        // Une demi-journée : une heure ne suffit pas, douze oui.
        p.heure = (p.heure + 1 / 24) % 1; jouer(L, o, 4);
        const uneHeure = etape(L);
        p.jour += 1; jouer(L, o, 6);
        const demonte = etape(L);
        const w = B.mission.vehicule;
        const cabriolet = { slug: w && w.slug, depanneur: loin(w, L.Histoire.lieu('depanneur')) };
        monterDans(L, o, w);
        if (""" + ("true" if bosse else "false") + """) { w.chocs = (w.chocs || 0) + 1; w.vie -= 10; }
        poser(L, w, L.Histoire.lieuDeLivraison('fourriere')); jouer(L, o, 8);
        const livre2 = etape(L);
        versLui(L, 'tiloup'); finir(L, o);
        return { pris: pris, taxi: taxi, livre1: livre1, uneHeure: uneHeure, demonte: demonte, cabriolet: cabriolet,
                 livre2: livre2, dites: dites, fait: !!p.missionsFaites.q15, argent: montants(argent),
                 q14: !!L.Histoire.disponibleDe('sven') && L.Histoire.disponibleDe('sven').slug === 'q14' };
    }""")


def test_q15_un_taxi_puis_un_cabriolet_en_pieces_sans_une_bosse(banc):
    r = _q15(banc)
    assert r["pris"] == {"dispo": "q15", "mission": "q15"}, r["pris"]
    assert r["taxi"]["slug"] == "taxi" and r["taxi"]["terminus"] <= 16, r["taxi"]
    assert r["livre1"] == {"etape": 2, "aPied": True}, r["livre1"]
    assert r["uneHeure"] == 2 and r["demonte"] == 3, f"une heure ne suffit pas, douze oui : {r}"
    assert r["cabriolet"]["slug"] == "cabriolet" and r["cabriolet"]["depanneur"] <= 16, r["cabriolet"]
    assert r["livre2"] == 5, r
    for dite in ("pendant:tiloup:0", "pendant:tiloup:1", "pendant:tiloup:2", "pendant:tiloup:3", "pendant:tiloup:4",
                 "pendant:tiloup:5"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [375], r["argent"]
    assert r["q14"] is False, "Sven offre sa liste à qui a brûlé ses camions"


def test_q15_une_bosse_sur_le_cabriolet_coute_la_prime(banc):
    r = _q15(banc, bosse=True)
    assert r["fait"] is True and r["argent"] == [250], r["argent"]


def test_l_ardoise_du_quai_suit_le_choix_sven_personne_puis_ti_loup(banc):
    """Sans q11 : Sven, à sa jetée (la liste du quai, telle que livrée le 26 sept.). Après q11 : personne — Sven ne prend
    rien, la ligne du bas se tait. Après q15 : Ti-Loup, à son lot ; Sven, toujours rien."""
    brule = economie.LISTE_DU_QUAI["brule"]
    assert (brule["par"], brule["relais"], brule["apres"]) == ("q11", "tiloup", "q15")
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, M = L.Missions;
        const jetee = L.Histoire.lieuDuPersonnage('sven'), lot = L.Histoire.lieuDeLivraison('fourriere');
        function livrerA(l) {
          const p = B.partie, liste = M.listeDuQuai(p.jour);
          const v = o.char(liste[0], 0, 0, 0), j = B.joueur;
          if (j.dansVehicule) L.Vehicules.descendre(j, true);
          L.Vehicules.monter(j, v);
          v.x = l.x; v.y = l.y; j.x = v.x; j.y = v.y; v.vitesse = 0; v.vx = 0; v.vy = 0; L.Entites.indexer();
          const avant = p.argent, info = M.texteDuQuai(j);
          M.majQuai();
          const r = { paye: p.argent - avant, info: info, msg: B.msg };
          if (j.dansVehicule) L.Vehicules.descendre(j, true);
          p.jour += 1;                                          // un par jour : le suivant, demain
          return r;
        }
        function etat(plus) {
          partieQ15(L, plus); B.partie.mission = null; B.mission = null; B.partie.jour = 21;   // ⚠️ en juillet : pas de motoneige
          B.partie.quai = null;                                 // ce qu'une autre partie a livré ne compte pas
          return { qui: M.donneurDuQuai(), jetee: livrerA(jetee), lot: livrerA(lot) };
        }
        // Le côté de Sven : q10 fait, pas q11.
        """ + "faites(L, " + json.dumps([m["slug"] for m in missions.CATALOGUE
                                           if m["slug"] not in ("q11", "q15", "m97", "m98", "m99")]) + ");" + """
        recharger(L); B.partie.mission = null; B.mission = null; B.partie.jour = 21; B.partie.quai = null;
        const sven = { qui: M.donneurDuQuai(), jetee: livrerA(jetee), lot: livrerA(lot) };
        // Le côté de Josée : q11, sans q15, puis avec.
        const brule = etat([]);
        const tiloup = etat(['q15']);
        return { sven: sven, brule: brule, tiloup: tiloup };
    }""")
    s, b, t = r["sven"], r["brule"], r["tiloup"]
    assert s["qui"] == "sven" and s["jetee"]["paye"] > 0 and s["jetee"]["info"].startswith("LA LISTE DE SVEN"), s
    assert s["lot"]["paye"] == 0, f"Ti-Loup prend la liste du côté de Sven : {s}"
    assert b["qui"] is None and b["jetee"]["paye"] == 0 and b["jetee"]["info"] is None, f"Sven prend encore : {b}"
    assert b["lot"]["paye"] == 0, b
    assert t["qui"] == "tiloup" and t["lot"]["paye"] > 0, t
    assert t["lot"]["info"].startswith("LA LISTE DE TI-LOUP"), t
    assert t["jetee"]["paye"] == 0, f"Sven prend encore après q15 : {t}"
