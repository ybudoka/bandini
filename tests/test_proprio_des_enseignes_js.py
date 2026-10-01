"""Le propriétaire qui sort quand on dévisse son enseigne (P4, des choses à collectionner, vague 6) au banc — PAR LE
BOUTON : à la vis de son réveil, il sort par la porte de son commerce, en pyjama ou en robe de chambre (même en
janvier) ; il crie, puis il te court après (le tournevis tombe des mains) ou il rentre appeler la police (l'effraction
est rapportée) ; assommé, il n'appelle personne ; il lâche et rentre chez lui ; une fois par nuit ; et il naît hors de
la suite des numéros, sans tirer un dé du jeu.
"""

from tests.test_enseignes_devissees_js import AMENER

#: Dévisser `n` vis au bouton (la lame d'abord), sous l'enseigne déjà amenée ; la police aveugle et sans agents, pour
#: que seul le coup de fil du proprio puisse rapporter l'effraction.
OUTILS = AMENER + """
    //: ⚠️ Les hommes de Sal passent au jour 21 (« un juge de couleur pose sa saison ») : le joueur invincible POUR DE BON.
    function ouvrir(L, o) { L.B.partie.dette = 0; L.B.joueur.invincible = 1e9; o.tape('KeyE', 2); o.frame(14); quart(o, 'KeyW'); }
    function vis(o, n) { for (let k = 0; k < n; k++) TOUR.forEach(function (c) { quart(o, c); }); }
    function aveugler(L) {
        L.Police.quelqu_un_voit = function () { return false; };
        L.Police.agents().forEach(L.Entites.retirer);
        L.Police.peuplerAgents = function () {};
    }
    function chaleur(L) { return L.B.recherche.chaleur + L.B.recherche.etoiles * 100; }
    function proprio(L) { return L.Devisser.dehors.length ? L.Devisser.dehors[0] : null; }
"""


def test_il_sort_par_sa_porte_a_sa_vis_hors_de_la_suite_et_sans_un_de(banc):
    """Aux Quilles, il se réveille à la deuxième vis : personne après la première, quelqu'un après la deuxième — né
    DANS la porte du commerce (invisible tant qu'elle s'ouvre), numéroté à part, et sa naissance ne tire aucun dé."""
    r = banc("function (L, o) {" + OUTILS + """
        const a = amener(L, o, 'quilles');
        ouvrir(L, o);
        vis(o, 1);
        const apresUne = L.Devisser.dehors.length;
        let des = 0; const de = L.B.rng; L.B.rng = function () { des++; return de(); };
        const tournevis = L.Devisser.TOURNEVIS.maj, vrai = L.Devisser.sortir;
        vis(o, 1);
        L.B.rng = de;
        const d = proprio(L), e = d && d.e;
        const porte = a.f.proprio.porte;
        const nee = e && { id: e.id, x: Math.round(e.x), y: Math.round(e.y), dessine: e.dessine, sortie: !!e.sortie,
                           metier: e.metier, tenue: e.tenue.haut };
        // Le dé, compté sur SA naissance seule : on la refait à la main, la nuit suivante.
        L.Entites.retirer(e); L.Devisser.oublier();
        L.B.partie.jour = 22;
        let desNaissance = 0; L.B.rng = function () { desNaissance++; return de(); };
        const autre = L.Devisser.sortir(a.f);
        L.B.rng = de;
        return { apresUne: apresUne, nee: nee, porte: porte, desNaissance: desNaissance, autre: !!autre };
    }""")
    assert r["apresUne"] == 0, "le proprio sort avant sa vis"
    assert r["nee"], "deux vis aux Quilles, et personne ne sort"
    n, (px, py) = r["nee"], r["porte"]
    assert n["id"] >= 1e9, f"il prend un numéro de la ville ({n['id']}) : tout ce qui naît après glisse"
    assert abs(n["x"] - (px * 16 + 8)) <= 2 and (py + 1) * 16 <= n["y"] <= (py + 2) * 16, (n, r["porte"])
    assert n["sortie"] and n["metier"] == "proprio", n
    assert r["autre"] and r["desNaissance"] == 0, f"sa naissance tire {r['desNaissance']} dé(s) du jeu"


def test_en_pyjama_ou_en_robe_de_chambre_meme_en_janvier(banc):
    """Le 1er janvier, un passant enfile son manteau (`Saisons.vetir`) : le proprio tiré du lit, non — c'est son habit
    de nuit que la ville dessine. Les Quilles : la robe de chambre ; le Bingo : le pyjama rayé."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        if (L.B.menu) { L.Hud.fermerMenu && L.Hud.fermerMenu(); L.B.menu = null; }
        L.B.partie.jour = 1; L.B.partie.heure = 23 / 24;
        const out = {};
        for (const slug of ['quilles', 'bingo']) {
            const f = L.Devisser.enseigne(slug);
            const e = L.Devisser.sortir(f);
            let cuite = null; const vrai = L.Garderobe.cuire;
            L.Garderobe.cuire = function (tn) { cuite = tn; return vrai(tn); };
            L.Entites.imageDe(e);
            L.Garderobe.cuire = vrai;
            out[slug] = { haut: cuite.haut, motif: cuite.motif, bas: cuite.bas, souliers: cuite.couleur_souliers,
                          meme: cuite === e.tenue, manteau: L.Saisons.vetir(e.tenue, e).haut };
        }
        return out;
    }""")
    q, b = r["quilles"], r["bingo"]
    assert q["manteau"] != "robe", "le juge ne mord pas : en janvier, la saison n'habille plus personne"
    assert q["meme"] and q["haut"] == "robe", f"en janvier, le proprio sort en {q['haut']}, pas en robe de chambre"
    assert b["meme"] and (b["haut"], b["motif"]) == ("chemise", "raye"), b


def test_il_crie_puis_te_court_apres_et_le_tournevis_tombe_des_mains(banc):
    """Le proprio des Quilles crie en sortant (sa bulle, sa voix de passant), puis il court : arrivé sur toi, le
    tournevis se referme — « L'ENSEIGNE RESTE — LE PROPRIO ! » — et l'enseigne pend encore."""
    r = banc("function (L, o) {" + OUTILS + """
        const a = amener(L, o, 'quilles');
        const voix = []; const vrai = L.Son.Voix.parler;
        L.Son.Voix.parler = function (slug) { voix.push(slug); return vrai.apply(this, arguments); };
        ouvrir(L, o);
        vis(o, 2);
        const vus = { bulles: [], etats: [] };
        let fermee = -1;
        for (let i = 0; i < 400 && fermee < 0; i++) {
            o.frame(1);
            const d = proprio(L);
            if (d && d.e.bulle && vus.bulles.indexOf(d.e.bulle.texte) < 0) vus.bulles.push(d.e.bulle.texte);
            if (d && vus.etats.indexOf(d.e.etat) < 0) vus.etats.push(d.e.etat);
            if (!L.B.epreuve) fermee = i;
        }
        L.Son.Voix.parler = vrai;
        // Collé à toi, il ne frappe pas : trois secondes de plus, et pas un coup (l'état `attaque` est celui du poing).
        let collé = 0, coups = 0;
        for (let i = 0; i < 180; i++) {
            o.frame(1);
            const d = proprio(L);
            if (d && Math.hypot(d.e.x - a.j.x, d.e.y - a.j.y) < 20) collé++;
            if (d && d.e.etat === 'attaque') coups++;
        }
        return { vus: vus, voix: voix, fermee: fermee, msg: L.B.msg, prise: !!L.B.partie.collections.enseignes.quilles,
                 coups: coups, colle: collé };
    }""")
    assert r["vus"]["bulles"][:2] == ["Heille! Ça fait trente ans qu'a pend là, mon enseigne!",
                                      "Attends que j'te pogne! J'cours vite, en pantoufles!"], r["vus"]
    assert r["voix"][:2] == ["proprio-h-sort", "proprio-h-court"], r["voix"]
    assert "attaque_joueur" in r["vus"]["etats"] and "attaque" not in r["vus"]["etats"], r["vus"]
    assert r["fermee"] >= 0 and r["msg"] == "L’ENSEIGNE RESTE — LE PROPRIO !", (r["fermee"], r["msg"])
    assert not r["prise"]
    assert r["colle"] > 120, f"il ne te colle pas aux talons ({r['colle']} images sur 180)"
    assert r["coups"] == 0, f"un proprio en pantoufles te frappe ({r['coups']} images de poing)"


def test_celui_qui_appelle_rentre_et_la_police_l_apprend(banc):
    """À la Cantine, il annonce le coup de fil, rentre par sa porte, et au bout du temps de trouver ses lunettes,
    l'effraction est rapportée — personne d'autre ne l'a vue (police aveugle, rue vide)."""
    r = banc("function (L, o) {" + OUTILS + """
        const a = amener(L, o, 'cantine');
        aveugler(L);
        ouvrir(L, o);
        vis(o, 4);
        o.frame(40);
        const tombee = !!L.B.partie.collections.enseignes.cantine;
        const avant = chaleur(L);
        const vus = [];
        let rentre = -1, appel = -1, annonce = -1;
        for (let i = 0; i < 1200 && appel < 0; i++) {
            o.frame(1);
            const d = proprio(L);
            if (d && d.e.bulle && vus.indexOf(d.e.bulle.texte) < 0) vus.push(d.e.bulle.texte);
            if (annonce < 0 && d && d.phase === 'annonce') annonce = i;
            if (rentre < 0 && !L.Devisser.dehors.length) rentre = i;
            if (chaleur(L) > avant) appel = i;
        }
        return { tombee: tombee, vus: vus, rentre: rentre, appel: appel, annonce: annonce, gain: chaleur(L) - avant, msg: L.B.msg,
                 une: L.B.defs.recherche.chaleur_par_gravite * L.B.defs.recherche.delits.effraction.etoiles };
    }""")
    assert r["tombee"], "le juge n'a pas fait tomber la Cantine"
    assert "Bouge pas! J'appelle la police… dès que j'trouve mes lunettes!" in r["vus"], r["vus"]
    assert r["rentre"] >= 0, "il ne rentre pas chez lui"
    assert r["rentre"] - r["annonce"] >= 100, "il rentre avant qu'on ait pu lire son annonce"
    assert r["appel"] > r["rentre"], "la police l'apprend sans que personne l'appelle"
    assert r["gain"] == r["une"] and r["msg"] == "LE PROPRIO A APPELÉ LA POLICE", r


def test_assomme_il_n_appelle_personne_et_c_est_un_delit_de_plus(banc):
    """À la Cantine encore : on l'assomme sur son perron, AU BOUTON, avant qu'il rentre — un coup sur un passant se
    signale, et relevé, il rentre sans décrocher le téléphone."""
    r = banc("function (L, o) {" + OUTILS + """
        const a = amener(L, o, 'cantine');
        aveugler(L);
        const delits = []; const vrai = L.Police.signalerCrime;
        L.Police.signalerCrime = function (type) { delits.push(type); return vrai.apply(this, arguments); };
        ouvrir(L, o);
        vis(o, 2);
        let d = null;
        for (let i = 0; i < 200 && !(d && !d.e.sortie && d.e.dessine); i++) { o.frame(1); d = proprio(L); }
        const e = d.e;
        L.Adresse.fermer();
        // Collé à lui, tourné vers lui, et on frappe.
        let coups = 0;
        for (; coups < 40 && e.etat !== 'assomme'; coups++) {
            a.j.x = e.x; a.j.y = e.y - 12; a.j.face = 'bas'; a.j.angle = Math.PI / 2; a.j.vx = 0; a.j.vy = 0;
            o.tape('Space', 2); o.frame(16);
        }
        const ko = e.etat === 'assomme';
        // Relevé, il rentre : on guette s'il décroche le téléphone en passant sa porte.
        let auTelephone = 0, rentre = false;
        for (let i = 0; i < 60 * 30; i++) {
            o.frame(1);
            auTelephone = Math.max(auTelephone, L.Devisser.appels.length);
            if (!L.Devisser.dehors.length) rentre = true;
        }
        return { ko: ko, coups: coups, delits: delits, auTelephone: auTelephone, rentre: rentre };
    }""")
    assert r["ko"], f"le proprio ne tombe pas sous {r['coups']} coups"
    assert "coup_pieton" in r["delits"], r["delits"]
    assert r["rentre"], "relevé, il ne rentre pas chez lui"
    assert r["auTelephone"] == 0, "assommé, il appelle quand même la police"


def test_il_lache_au_bout_de_sa_poursuite_et_rentre_chez_lui(banc):
    """Celui qui court ne court pas toute la nuit : planté devant lui (on ne bouge pas d'un pixel), il cogne, puis au
    bout de sa poursuite il le dit et rentre par sa porte."""
    r = banc("function (L, o) {" + OUTILS + """
        const a = amener(L, o, 'quilles');
        const x = a.j.x, y = a.j.y;
        ouvrir(L, o);
        vis(o, 2);
        const vus = [];
        let parti = -1, lache = -1;
        for (let i = 0; i < 60 * 30 && parti < 0; i++) {
            a.j.x = x; a.j.y = y; a.j.vx = 0; a.j.vy = 0;
            o.frame(1);
            const d = proprio(L);
            if (d && d.e.bulle && vus.indexOf(d.e.bulle.texte) < 0) vus.push(d.e.bulle.texte);
            if (lache < 0 && d && d.e.bulle && d.e.bulle.texte.indexOf('Pfff') === 0) lache = i;
            if (!L.Devisser.dehors.length) parti = i;
        }
        return { vus: vus, parti: parti, lache: lache };
    }""")
    assert r["lache"] > 12 * 60, f"il lâche trop tôt ({r['lache']}), ou jamais : {r['vus']}"
    assert r["parti"] > r["lache"], r


def test_il_ne_court_pas_loin_de_chez_lui(banc):
    """Qu'on s'éloigne sur le trottoir, il suit — jusqu'à deux cents pixels de sa porte, pas plus : il lâche bien avant
    la fin de sa poursuite."""
    r = banc("function (L, o) {" + OUTILS + """
        const a = amener(L, o, 'quilles');
        ouvrir(L, o);
        vis(o, 2);
        let d = null;
        for (let i = 0; i < 400 && !(d && d.phase === 'court'); i++) { o.frame(1); d = proprio(L); }
        const x0 = a.j.x, y0 = a.j.y;
        let lache = -1, loin = 0;
        for (let i = 0; i < 60 * 10 && lache < 0; i++) {
            a.j.x = x0 + Math.min(i, 160) * 2; a.j.y = y0; a.j.vx = 0; a.j.vy = 0;
            o.frame(1);
            const e = d.e, px = a.f.proprio.porte[0] * 16 + 8;
            loin = Math.max(loin, Math.round(e.x - px));
            if (e.bulle && e.bulle.texte.indexOf('Pfff') === 0) lache = i;
        }
        return { lache: lache, loin: loin };
    }""")
    assert 0 <= r["lache"] < 6 * 60, r
    assert r["loin"] <= 215, r


def test_une_fois_par_nuit_et_certains_ne_sortent_jamais(banc):
    """Un proprio ne sort qu'une fois par nuit (la nuit suivante, il ressort) ; au Rialto, personne n'est en haut ;
    chez Ti-Paul et au Dragon d'or, la porte est tenue ; aux Souvenirs, il n'y a pas de porte."""
    r = banc("function (L, o) {" + OUTILS + """
        const a = amener(L, o, 'bingo');
        const une = !!L.Devisser.sortir(a.f), deux = !!L.Devisser.sortir(a.f);
        L.B.partie.jour = 22; L.B.partie.heure = 3 / 24;     // la même nuit, passé minuit
        const minuit = !!L.Devisser.sortir(a.f);
        L.B.partie.jour = 23; L.B.partie.heure = 22 / 24;
        const lendemain = !!L.Devisser.sortir(a.f);
        const sans = L.Devisser.liste().filter(function (f) { return !f.proprio; }).map(function (f) { return f.slug; });
        const b = amener(L, o, 'rialto');
        ouvrir(L, o);
        vis(o, 4);
        o.frame(120);
        return { une: une, deux: deux, minuit: minuit, lendemain: lendemain, sans: sans,
                 rialto: L.Devisser.dehors.length, prise: !!L.B.partie.collections.enseignes.rialto };
    }""")
    assert r["une"] and not r["deux"] and not r["minuit"], r
    assert r["lendemain"], "il ne ressort jamais, même la nuit d'après"
    assert sorted(r["sans"]) == ["dragon_or", "rialto", "souvenirs", "taverne_port", "tipaul"], r["sans"]
    assert r["prise"] and r["rialto"] == 0, "quelqu'un sort du Rialto"
