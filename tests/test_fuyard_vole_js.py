"""Le char du fuyard, volé en marche (Martin, 29 sept. 2026 : « j'ai volé le char du pyromane et après
quelques secondes j'ai perdu tout contrôle »).

`ramasser` + `fuyard` (m2, f03, f13…) fait « tomber » le fuyard quand on l'a rattrapé : son char
s'arrête, `conducteur = null`, et un Cravate en descend avec la caisse. Mais on peut aussi lui PRENDRE
son char (`Vehicules.monter`, le carjacking) : le joueur est au volant, la mission croyait encore que
le fuyard conduisait, et au premier freinage (< 0,6 px/image, à moins de 40 px… de soi-même) elle
vidait le siège — le joueur restait assis dans un char que plus personne ne conduisait.
"""


def test_on_vole_le_char_du_fuyard_et_on_garde_le_volant(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer(); L.B.partie.jour = 21;  // EN JUILLET : la moto roule (l'hiver, elle est remisée)
        L.graine(6);
        const j = L.B.joueur;
        L.B.partie.missionsFaites.m1 = 1;
        const t = L.Histoire.donneur('thibodeau');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        L.Histoire.commencer('m2');
        L.B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible; }).forEach(function (e) { L.Entites.assommer(e); });
        o.frame(2);
        while (L.B.cinema) L.Histoire.suivante();
        const v = L.B.mission.fuyard;
        for (let i = 0; i < 30; i++) o.frame(1);
        const vitesse = v.vitesse;
        j.x = v.x + 10; j.y = v.y; L.Entites.indexer();
        const monte = L.Vehicules.monter(j, v);
        o.frame(2);
        const tombe = !!L.B.mission.fuyardTombe;
        const porteurs = L.B.mission.entites.filter(function (e) { return e.porteLaCaisse; }).length;
        // Celui qui descend, c'est LE fuyard (avec la caisse) : pas un passant témoin de plus.
        const temoins = L.B.entites.filter(function (e) {
          return e.type === 'pieton' && e.menace === j && e.etat === 'temoin' && !e.porteLaCaisse;
        }).length;
        // On freine, puis on repart : le volant répond toujours.
        v.vitesse = 0.2; o.frame(10);
        const auFrein = { conducteur: v.conducteur === j, etat: v.etat, fuite: !!v.fuite, poursuite: !!v.poursuite };
        const x0 = v.x, y0 = v.y;
        o.touche('KeyW'); o.frame(60); o.relacher('KeyW');
        const avance = Math.hypot(v.x - x0, v.y - y0);
        // La mission rate (le pire cas : `nettoyer(true)` emporte tous ses chars) : le char volé reste sous le joueur, c'est le sien maintenant.
        L.Histoire.echouer('arrete'); while (L.B.cinema) L.Histoire.suivante();
        o.frame(2);
        return { vitesse: vitesse, monte: monte, tombe: tombe, porteurs: porteurs, temoins: temoins, auFrein: auFrein,
                 avance: avance, dedans: j.dansVehicule === v, enVille: L.B.entites.indexOf(v) >= 0,
                 conducteur: v.conducteur === j, fuyard: !!v.fuyard, mission: v.mission || null };
    }""")
    assert r["vitesse"] >= 0.6 and r["monte"], f"on monte dans le char du fuyard EN MARCHE ({r})"
    assert r["tombe"] and r["porteurs"] == 1, "le fuyard tiré de son char file à pied avec la caisse"
    assert r["temoins"] == 0, "un seul homme sort du char : le fuyard, pas un passant de plus"
    assert r["auFrein"] == {"conducteur": True, "etat": "roule", "fuite": False, "poursuite": False}, r["auFrein"]
    assert r["avance"] > 20, f"au gaz, le char repart ({r['avance']:.1f} px en une seconde)"
    assert r["dedans"] and r["enVille"] and r["conducteur"], "la mission finie, le char volé reste sous le joueur"
    assert not r["fuyard"] and r["mission"] is None
