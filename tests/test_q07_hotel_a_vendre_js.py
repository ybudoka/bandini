"""q07, _La chambre 12_ (M16, 29 sept. 2026) — la mission qui met l'Hôtel Bandini EN VENTE (`donne.a_vendre`), la
quatrième propriété que _Le Boss_ (M13) demande et que rien ne vendait (`phase: 2`). JOUÉE au bouton, de l'appel
à la prime, puis l'hôtel acheté au comptoir : quatre propriétés."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER
from test_quatre_missions_js import RATTRAPER


def test_q07_la_chambre_12_le_colis_chez_gilles_puis_l_hotel_est_a_vendre(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + RATTRAPER + DEDANS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm50', 'f01', 'f03', 'f10', 's01']);
        const j = recharger(L);
        p.argent = 20000;
        const avant = !!L.Missions.aVendre('hotel');
        const argent = paiements(L);
        const dispo = L.Histoire.disponibles().some(function (m) { return m.slug === 'q07'; });
        commencer(L, o, 'q07'); jouer(L, o);
        const h = L.Histoire.lieu('hotel');
        j.x = h.x; j.y = h.y + 8; L.Entites.indexer();
        laNuit(L, o); jouer(L, o, 10);
        const camion = B.mission.vehicule || (B.mission.chars && B.mission.chars[1]);
        const nuit = { etape: etape(L), slug: camion && camion.slug,
                       hotel: camion ? Math.round(Math.hypot(camion.x - h.x, camion.y - h.y) / 16) : null };
        j.x = camion.x + 12; j.y = camion.y; L.Entites.indexer(); L.Vehicules.monter(j, camion); L.Entites.indexer(); jouer(L, o);
        const route = { etape: etape(L) };
        conduireA(L, o, camion, 'fourriere');
        const livre = { etape: etape(L) };
        const accueil = serrer(L, o, 'gilles');
        finir(L, o);
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs);
        // Une partie abîmée (`enVente: null`) repart avec rien en vente, comme `libere` et `calmes`.
        const vieille = JSON.parse(JSON.stringify(p)); vieille.enVente = null;
        const vieilleRelue = L.Sauvegarde.completer(vieille, B.defs).enVente;
        const aVendre = L.Missions.aVendre('hotel');
        // Et on l'ACHÈTE, au comptoir du hall : la quatrième propriété que _Le Boss_ demande.
        p.proprietes = { kiosque: { jour: 1, caisse: 0 }, bar: { jour: 1, caisse: 0 }, garage: { jour: 1, caisse: 0 } };
        p.argent = 20000;
        const piece = dedans(L, o, 'hotel');
        let achat = null;
        for (const q of (L.B.interieur ? L.B.interieur.points : [])) {
            const menu = L.Missions.menuDuPoint(q);
            const it = menu && (menu.items || []).find(function (i) { return i.libelle === 'ACHETER LE COMMERCE'; });
            if (it) { achat = it.detail; it.faire(); break; }
        }
        const quatre = { achat: achat, proprietes: Object.keys(p.proprietes).sort(), boss: L.Histoire.exigeTenu({ proprietes: 4 }) };
        return { piece: piece, quatre: quatre, avant: avant, dispo: dispo, nuit: nuit, route: route, livre: livre, accueil: accueil, dites: dites,
                 fait: !!p.missionsFaites.q07, argent: argent.map(function (a) { return a.montant; }),
                 enVente: p.enVente.slice(), relue: relue.enVente, vieille: vieilleRelue, aVendre: aVendre && aVendre.slug };
    }""")
    assert r["avant"] is False, "l'hôtel n'est à vendre nulle part avant q07"
    assert r["dispo"] is True
    assert r["nuit"]["etape"] == 1 and r["nuit"]["slug"] == "camion" and r["nuit"]["hotel"] <= 20, r["nuit"]
    assert r["route"]["etape"] == 2 and r["livre"]["etape"] == 3, r
    assert r["accueil"] == "accueil", "Gilles s'occupe du reste, à la poignée de main"
    assert r["fait"] is True and r["argent"] == [500]
    assert r["enVente"] == ["hotel"] and r["relue"] == ["hotel"] and r["aVendre"] == "hotel", r
    assert r["vieille"] == [], "une partie d'avant q07 se relit avec rien en vente"
    assert r["piece"] == "hotel" and r["quatre"]["achat"] == "10000 $", f"l'hôtel s'achète au comptoir du hall : {r['quatre']}"
    assert r["quatre"]["proprietes"] == ["bar", "garage", "hotel", "kiosque"] and r["quatre"]["boss"] is True, r["quatre"]
