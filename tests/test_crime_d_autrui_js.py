"""Le crime d'autrui (M12) au banc : un passant te confond avec le vrai coupable — rarement,
lisiblement, et jamais quand tu n'es pas tout près.

⚠️ `VOL` met en scène un VRAI vol à la tire (la routine du pickpocket, pas un appel à la
main) : un voleur, sa victime de dos, un badaud planté qui regarde, et le joueur immobile
à la distance voulue. La méprise est forcée (`chance = 1`) : ce qu'on juge, c'est QUI
peut être confondu, pas le tirage.
"""

VOL = """
    function vol(L, o, ecart) {
        L.Jeu.commencer();
        const r = L.B.defs.recherche.autrui;
        r.chance = 1; r.repos_s = 0;
        L.graine(88);
        const j = L.B.joueur, TT = L.TT, d = o.ligneDroite();
        j.x = d.x; j.y = d.y - 3 * TT; L.Monde.centrerCamera(j.x, j.y);
        for (const q of L.B.entites.slice()) if (q.type === 'pieton' && Math.hypot(q.x - j.x, q.y - j.y) < 400) L.Entites.retirer(q);
        const voleur = o.poser('pickpocket', 0, 0);
        voleur.etat = 'flane'; voleur.argent = 0;
        const victime = o.poser('passant', 40, 0);
        victime.etat = 'flane'; victime.argent = 37; victime.face = 'droite';
        // ⚠️ Sur le MEME trottoir, derriere le voleur : a vingt-quatre pixels au sud, il
        // se tenait sur la chaussee, et un char l'a fauche a l'image 221.
        const badaud = o.poser('passant', -40, 0);
        badaud.etat = 'fige'; badaud.plante = { x: badaud.x, y: badaud.y }; badaud.argent = 0; badaud.probaTemoin = 0;
        // Le joueur, immobile, a `ecart` pixels de la victime — sur le trottoir, du cote du voleur.
        j.x = victime.x - ecart; j.y = victime.y;
        L.Monde.centrerCamera(victime.x, victime.y);
        L.Entites.indexer();
        let vole = -1;
        for (let i = 0; i < 900 && vole < 0; i++) {
            o.frame(1);
            for (const q of L.B.entites.slice()) if (q.type === 'pieton' && q !== voleur && q !== victime && q !== badaud) L.Entites.retirer(q);
            victime.face = 'droite';
            j.x = victime.x - ecart; j.y = victime.y; j.vx = 0; j.vy = 0;
            L.Monde.centrerCamera(victime.x, victime.y);
            if (voleur.voleT > 0) vole = i;
        }
        const meprise = L.B.crimes.find(function (c) { return c.autrui; }) || null;
        const temoin = { etat: badaud.etat, dit: badaud.bulle ? badaud.bulle.texte : null, menace: badaud.menace === j };
        // La suite : la machine des temoins (il court, ou il telephone). ⚠️ On lit la
        // CHALEUR, pas les etoiles : un vol a la tire rapporte en vaut le tiers d'une.
        let chaleur = 0;
        for (let i = 0; i < 1500; i++) {
            o.frame(1);
            j.vx = 0; j.vy = 0;
            chaleur = Math.max(chaleur, L.B.recherche.chaleur + L.B.recherche.etoiles * 100);
        }
        return { vole: vole >= 0, meprise: !!meprise, temoin: temoin, chaleur: chaleur, rapporte: !!(meprise && meprise.rapporte),
                 cri: r.cri, rayon: r.rayon_px };
    }
"""


def test_aucune_etoile_a_un_joueur_qui_n_y_est_pour_rien(banc):
    """⚠️ Le juge du plan : le joueur immobile à plus du rayon de la méprise — même quand
    elle est certaine — ne reçoit rien : pas de crime à son nom, pas d'étoile."""
    r = banc("function (L, o) {" + VOL + """
        return vol(L, o, L.B.defs.recherche.autrui.rayon_px + 40);
    }""")
    assert r["vole"], "le juge ne met aucun vol en scène"
    assert r["meprise"] is False, "on confond un joueur qui se tenait loin"
    assert r["chaleur"] == 0, f"chaleur {r['chaleur']} pour un joueur qui n'y est pour rien"


def test_tout_pres_un_temoin_te_confond_et_ca_se_lit(banc):
    """Tout près, le badaud te désigne — « C'EST LUI! » —, il porte le crime, et la machine
    des témoins en fait une étoile. Le vrai coupable, lui, est là : la victime crie après LUI."""
    r = banc("function (L, o) {" + VOL + """
        return vol(L, o, 24);
    }""")
    assert r["vole"], "le juge ne met aucun vol en scène"
    assert r["meprise"] is True, "tout près, personne ne t'a confondu"
    assert r["temoin"]["dit"] == r["cri"] and r["temoin"]["menace"], r["temoin"]
    assert r["rapporte"] and r["chaleur"] > 0, f"le témoin n'a rien fait de sa méprise : {r}"


def test_la_meprise_est_rare_lisible_et_jamais_au_volant(banc):
    r = banc("function (L, o) {" + """
        L.Jeu.commencer();
        const P = L.Police, r = L.B.defs.recherche.autrui, j = L.B.joueur, TT = L.TT;
        r.repos_s = 0;
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y - 3 * TT; L.Monde.centrerCamera(j.x, j.y);
        for (const q of L.B.entites.slice()) if (q.type === 'pieton') L.Entites.retirer(q);
        const coupable = o.poser('pickpocket', 30, 0), temoin = o.poser('passant', 0, 30);
        L.Entites.indexer();
        function essai(t) {
            temoin.etat = 'flane'; temoin.bulle = null; L.B.recherche.autruiT = undefined;
            L.B.t = t;
            return P.crimeDAutrui('pickpocket', j.x + 20, j.y, coupable) ? 1 : 0;
        }
        let n = 0;
        for (let t = 1000; t < 1400; t++) n += essai(t);
        const part = n / 400;
        // Lisible : la scene hors de l'ecran, personne ne te confond.
        r.chance = 1;
        L.Monde.centrerCamera(j.x + 2000, j.y);
        const horsChamp = essai(5000);
        L.Monde.centrerCamera(j.x, j.y);
        // Au volant : on passe.
        const v = L.Vehicules.creer('auto', j.x, j.y, 0, { etat: 'stationne', couleur: '#3a6fb0' });
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
        const auVolant = essai(5001);
        L.Vehicules.descendre(j, true);
        // Le repos : deux mepris coup sur coup, non.
        r.repos_s = 90;
        temoin.etat = 'flane'; L.B.recherche.autruiT = undefined; L.B.t = 6000;
        const premiere = !!P.crimeDAutrui('pickpocket', j.x + 20, j.y, coupable);
        temoin.etat = 'flane'; L.B.t = 6100;
        const seconde = !!P.crimeDAutrui('pickpocket', j.x + 20, j.y, coupable);
        return { part: part, reglage: 0.35, horsChamp: horsChamp, auVolant: auVolant, premiere: premiere, seconde: seconde };
    }""")
    assert 0.2 <= r["part"] <= 0.5, f"la méprise tombe {r['part']:.0%} du temps"
    assert r["horsChamp"] == 0, "on te confond pour une scène qu'on ne voit pas"
    assert r["auVolant"] == 0, "on confond un char avec un voleur à pied"
    assert r["premiere"] is True and r["seconde"] is False, r


def test_la_meprise_ne_tire_aucun_de(banc):
    r = banc("function (L, o) {" + VOL + """
        const tirage = { f: null, n: 0 };
        const res = (function () {
            L.Jeu.commencer();
            tirage.f = L.B.rng;
            const P = L.Police, avant = P.crimeDAutrui;
            P.crimeDAutrui = function () {
                const b = L.B.rng;
                L.B.rng = function () { tirage.n++; return b(); };
                try { return avant.apply(null, arguments); } finally { L.B.rng = b; }
            };
            const j = L.B.joueur, d = o.ligneDroite();
            j.x = d.x; j.y = d.y - 48; L.Monde.centrerCamera(j.x, j.y);
            const coupable = o.poser('pickpocket', 30, 0), temoin = o.poser('passant', 0, 30);
            L.Entites.indexer();
            L.B.defs.recherche.autrui.chance = 1; L.B.defs.recherche.autrui.repos_s = 0;
            let n = 0;
            for (let t = 0; t < 50; t++) { temoin.etat = 'flane'; L.B.t = 2000 + t; if (P.crimeDAutrui('pickpocket', j.x + 20, j.y, coupable)) n++; }
            P.crimeDAutrui = avant;
            return n;
        })();
        return { meprises: res, des: tirage.n };
    }""")
    assert r["meprises"] > 0
    assert r["des"] == 0, f"{r['des']} dés tirés par la méprise"
