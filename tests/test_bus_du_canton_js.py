"""Le bus du Petit-Canton, au banc : ses autobus naissent hors de la suite des numéros d'entités."""


def test_les_autobus_de_la_ligne_4_naissent_hors_de_la_suite(banc):
    """On se pose près de son tracé, dans la bande, et on laisse l'horaire les faire naître : un autobus de la
    ligne 4 prend un numéro de la plage à part ; ceux des autres lignes, jamais (le témoin)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, A = L.Autobus, d = A.donnees(), j = B.joueur;
        const l4 = d.lignes.find(function (l) { return l.numero === 4; });
        const out = { aPart: l4 && l4.aPart, ids: {} };
        for (let essai = 0; essai < 40; essai++) {
            const p = A.placeALHeure(l4, 0, A.tempsDeLaPartie());
            j.x = p.x + 360; j.y = p.y; L.Entites.indexer();
            B.t = 20 * Math.ceil((B.t + 1) / 20) + 7; A.faireNaitre();
            B.entites.forEach(function (e) { if (e.type === 'vehicule' && e.ligne) out.ids[e.ligne] = Math.max(out.ids[e.ligne] || 0, e.id); });
            if (out.ids[4]) break;
            o.frame(30);
        }
        return out;
    }""")
    assert r["aPart"] is True, r
    assert r["ids"].get("4", 0) >= 1e9, f"pas d'autobus de la ligne 4, ou dans la suite : {r}"
    assert all(v < 1e9 for k, v in r["ids"].items() if k != "4"), r
