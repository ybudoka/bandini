"""Un personnage qui ARRIVE après une mission (`arrive_apres`) est là dès la fin de celle-ci.

⚠️ Rouge avant (29 sept. 2026, vu en réparant `test_donneurs_visibles_js`) : les donneurs du dehors
ne se posaient qu'au CHARGEMENT d'une partie (`Histoire.creerDonneurs`). Le joueur qui finissait q04
ne trouvait Cindy devant la cantine qu'après avoir rechargé — et pareil pour Diane et Jo, Zed, le
Trappeur, Ti-Loup… C'est la fin de la mission qui les pose maintenant, comme elle retire déjà ceux
qui partent (`parti_apres`).
"""


def _tardifs(banc):
    return banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, H = L.Histoire, j = B.joueur; j.invincible = 1e6;
        const persos = B.defs.personnages || [];
        const tardifs = persos.filter(function (p) { return p.arrive_apres && p.ou && p.ou.indexOf('porte:') === 0; });
        const out = {};
        // Avant toute mission : aucun n'est la (plusieurs arrivent apres la MEME mission : Diane et Jo).
        const avant = {};
        for (const p of tardifs) avant[p.slug] = !!H.donneur(p.slug);
        for (const p of tardifs) {
            if (B.partie.missionsFaites[p.arrive_apres]) { out[p.slug] = { mission: p.arrive_apres, avant: avant[p.slug], apres: !!H.donneur(p.slug), faite: true }; continue; }
            // La mission d'arrivee, jouee jusqu'au bout — sans recharger la partie.
            H.commencer(p.arrive_apres);
            for (let k = 0; k < 4000 && (B.scene || B.cinema); k++) { if (B.cinema) H.suivante(); else o.frame(1); }
            H.reussir();
            for (let k = 0; k < 4000 && (B.scene || B.cinema || B.finEnAttente); k++) { if (B.cinema) H.suivante(); else o.frame(1); }
            out[p.slug] = { mission: p.arrive_apres, avant: avant[p.slug], apres: !!H.donneur(p.slug),
                            faite: !!B.partie.missionsFaites[p.arrive_apres] };
        }
        return out;
    }""")


def test_un_personnage_qui_arrive_apres_une_mission_est_la_des_sa_fin(banc):
    r = _tardifs(banc)
    assert "cindy" in r, f"Cindy n'arrive plus après une mission : le juge ne mesure pas ce qu'il croit ({sorted(r)})"
    for slug, t in r.items():
        assert t["faite"], f"{slug} : sa mission d'arrivée ({t['mission']}) ne s'est pas finie : {t}"
        assert not t["avant"], f"{slug} est déjà là avant {t['mission']}"
        assert t["apres"], f"{slug} n'est pas là à la fin de {t['mission']} — il faudrait recharger la partie"
