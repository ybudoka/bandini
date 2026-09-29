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


def _jouer_jusqu_au_bout(slug: str) -> str:
    """Le JS qui joue la mission `slug` jusqu'au bout de sa scène de fin, sans recharger la partie."""
    return """
        H.commencer('%s');
        for (let k = 0; k < 4000 && (B.scene || B.cinema); k++) { if (B.cinema) H.suivante(); else o.frame(1); }
        H.reussir();
        for (let k = 0; k < 4000 && (B.scene || B.cinema || B.finEnAttente); k++) { if (B.cinema) H.suivante(); else o.frame(1); }
    """ % slug


def test_marco_disparait_apres_m97(banc):
    """⚠️ Martin, 29 sept. 2026 : « Marco disparaît après m97 ». Après t'avoir vendu (« Moi, je disparais »),
    Marco attendait encore devant le garage comme si de rien n'était. Il part maintenant comme Ti-Guy et Bérubé
    (`parti_apres`) : à la fin de m97, sans recharger ; ni dehors ni au garage à la partie suivante ; grisé
    (PARTI) dans le menu « chez un donneur ».

    ⚠️ Mais PAS tant qu'une mission a encore besoin de lui (`Histoire.estParti`) : m97 ne demande que m5 et
    trois districts, et f08, f09 (les siennes) et f12 (son enveloppe, au garage) peuvent venir après. Là, il
    reste — et il s'en va à la fin de la dernière."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, H = L.Histoire; B.joueur.invincible = 1e6;
        const out = { avant: !!H.donneur('marco'), partiAvant: H.estParti(H.personnage('marco')) };
        const recharger = function (faites) {
            if (B.interieur) L.Jeu.quitterLaPiece();
            L.Jeu.retourTitre();
            B.partie.missionsFaites = {}; B.partie.mission = null;
            faites.forEach(function (s) { B.partie.missionsFaites[s] = 1; });
            L.Jeu.commencer(); B.joueur.invincible = 1e6;
        };
        const chezUnDonneur = function () {
            const it = L.Hud.menuChezUnDonneur().items.find(function (i) { return i.personnage === 'marco'; });
            return it ? it.detail : null;
        };
        // 1. Tout ce qui a besoin de lui est fait : il part à la fin de m97, et pour de bon.
        recharger(['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01', 'f08', 'f09', 'f12']);
        out.laAvantM97 = !!H.donneur('marco');
        """ + _jouer_jusqu_au_bout("m97") + """
        out.m97 = !!B.partie.missionsFaites.m97;
        out.apresLaFin = !!H.donneur('marco');
        out.menu = chezUnDonneur();
        recharger(Object.keys(B.partie.missionsFaites));
        out.dehors = !!H.donneur('marco');
        o.entrer(L.Monde.carte.portes.find(function (p) { return p.lieu === 'garage'; }));
        out.garage = B.interieur && B.interieur.slug;
        out.dedans = B.entites.some(function (e) { return e.personnage === 'marco'; });
        // 2. m97 jouée AVANT f08 : il reste pour elle (et pour f09, f12), puis s'en va à la fin de la dernière.
        recharger(['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01', 'f02', 'f03', 'f09', 'f10', 'f12', 'm97']);
        out.retenu = !!H.donneur('marco');
        out.menuRetenu = chezUnDonneur();
        """ + _jouer_jusqu_au_bout("f08") + """
        out.f08 = !!B.partie.missionsFaites.f08;
        out.apresF08 = !!H.donneur('marco');
        return out;
    }""")
    assert r["avant"] and r["partiAvant"] is False, f"Marco doit attendre devant le garage avant m97 : {r}"
    assert r["laAvantM97"], f"Marco n'est pas là pour donner m97 : {r}"
    assert r["m97"], f"m97 ne s'est pas finie : {r}"
    assert not r["apresLaFin"], f"Marco attend encore devant le garage à la fin de m97 : {r}"
    assert r["menu"] == "PARTI", f"le menu « chez un donneur » le montre encore : {r}"
    assert not r["dehors"], f"Marco revient devant le garage à la partie suivante : {r}"
    assert r["garage"], f"le juge n'est pas entré au garage : {r}"
    assert not r["dedans"], f"Marco se tient dans le garage : {r}"
    assert r["retenu"], f"Marco est parti alors que f08 l'attend encore — elle ne se jouerait plus jamais : {r}"
    assert r["menuRetenu"] != "PARTI", f"le menu le dit parti alors que f08 l'attend : {r}"
    assert r["f08"], f"f08 ne s'est pas finie : {r}"
    assert not r["apresF08"], f"f08 était la dernière à le retenir : il devait s'en aller à sa fin : {r}"
