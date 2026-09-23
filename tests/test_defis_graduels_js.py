"""Les dix-huit défis au doigt, à la manette et au clavier (23 sept. 2026) — côté jeu.

Martin : « je veux tout ça sur la carte, on doit les voir selon s'il est possible de les faire
avec les doigts ou avec la manette ou le clavier. Je veux qu'ils n'apparaissent pas tous en même
temps, mais graduellement quand on passe des défis ou qu'on avance dans l'histoire. »

Trois choses, jugées PAR LE BOUTON quand il y en a un : ce qui s'ouvre et quand
(`Histoire.majDeblocages`), ce que la carte montre selon l'appareil (`Hud.defisSurLaCarte`,
ARME sur la carte), et chaque épreuve debout (`Adresse`) jouée jusqu'au bout.
"""

import pytest

#: Aller au défi `slug` comme la triche SAUT VERS UN DÉFI (elle l'ouvre s'il est caché), puis
#: COMMENCER. Rend le défi du catalogue.
ALLER = """
    function aller(L, o, slug) {
        L.B.scene = null; L.B.cinema = null;
        if (L.B.menu) L.Hud.fermerMenu();
        const d = L.B.defs.defis.find(function (q) { return q.slug === slug; });
        if (!L.Hud.menuSautDefis().items.find(function (i) { return i.defi === slug; }).faire()) return null;
        L.B.menu.items[0].faire();
        L.Hud.fermerMenu();
        return d;
    }
"""


def _jeu(corps):
    return "function (L, o) {" + ALLER + "L.Jeu.commencer(); if (L.B.menu) L.Hud.fermerMenu(); o.frame(2);" + corps + "}"


def test_une_partie_neuve_n_a_que_les_dix_defis_de_la_v1(banc):
    r = banc(_jeu("""
        L.Histoire.majDeblocages(true);
        return { ouverts: L.Histoire.defisOuverts().map(function (d) { return d.slug; }),
                 panneaux: L.B.entites.filter(function (e) { return e.type === 'panneau'; }).map(function (e) { return e.defi; }),
                 caches: L.B.defs.defis.filter(function (d) { return d.debloque; }).length };
    """))
    assert len(r["ouverts"]) == 10
    assert r["caches"] >= 9
    assert "roue" not in r["panneaux"], "un défi caché n'a pas de panneau"


#: Un joueur PARFAIT, par le bouton : il lit l'état de l'épreuve (où est le lot, où est le raton)
#: et appuie au clavier — ou pousse le stick de la manette pour le cadenas. Rend l'issue.
ROBOT = """
    const TOUCHE = { haut: 'KeyW', bas: 'KeyS', gauche: 'KeyA', droite: 'KeyD', attaque: 'Space', action: 'KeyE' };
    function taper(o, code) { o.touche(code); o.frame(1); o.relacher(code); o.frame(1); }
    function stick(o, deg) {
        const a = deg * Math.PI / 180;
        o.pad([Math.sin(a), -Math.cos(a), 0, 0], []);
    }
    function jouer(L, o, d, max) {
        const r = d.regles, rate = [];
        let tenue = null;
        for (let n = 0; n < (max || 6000) && L.B.defi; n++) {
            const e = L.B.epreuve;
            if (!e || e.t <= L.Adresse.PRET) { o.frame(1); continue; }
            if (e.sorte === 'roue') {
                const v = r.secteurs * r.tours_par_s / 60, F = Math.round(r.freinage_s * 60);
                const fin = ((e.angle + v * (F + 1) / 2) % r.secteurs) - e.lot;
                if (e.freine < 0 && e.pause === 0 && fin > 0.3 && fin < 0.7) { taper(o, 'KeyE'); continue; }
            } else if (e.sorte === 'anneaux') {
                if (e.pause === 0 && !tenue && !e.attendLacher) { o.touche('KeyE'); tenue = 'KeyE'; }
                else if (tenue && e.tient && e.sens > 0 && Math.abs(e.charge - e.centre) < r.bande / 4) { o.relacher('KeyE'); tenue = null; }
            } else if (e.sorte === 'ratons') {
                if (e.trou >= 0) { taper(o, TOUCHE[r.trous[e.trou]]); o.frame(1); continue; }
            } else if (e.sorte === 'danse') {
                if (e.appel) { taper(o, TOUCHE[e.appel]); o.frame(1); continue; }
            } else if (e.sorte === 'mannequin') {
                const x = 0.5 + 0.5 * Math.sin(e.phase + 2 * Math.PI / Math.round(60 * r.periode_s[0]));
                if (e.pause === 0 && Math.abs(x - e.centre) < r.zone / 4) { taper(o, 'KeyE'); continue; }
            } else if (e.sorte === 'radio') {
                const ecart = e.cibles[e.k] - e.aiguille, voulu = e.pause ? null : (ecart > r.tolerance / 3 ? 'KeyD' : (ecart < -r.tolerance / 3 ? 'KeyA' : null));
                if (voulu !== tenue) { if (tenue) o.relacher(tenue); if (voulu) o.touche(voulu); tenue = voulu; }
            } else if (e.sorte === 'moteur') {
                const p = Math.round(r.cadence_s * 60);
                if ((e.t + 1) % p === 0) { taper(o, 'KeyE'); continue; }
            } else if (e.sorte === 'crochet' || (e.sorte === 'coffre' && e.pos >= e.code.length)) {
                stick(o, e.cible);
            } else if (e.sorte === 'coffre') {
                taper(o, TOUCHE[e.code[e.pos]]); o.frame(1); continue;
            }
            o.frame(1);
        }
        if (tenue) o.relacher(tenue);
        o.pad(null);
    }
"""

EPREUVES = ["roue", "anneaux", "ratons", "danse", "mannequin", "radio", "moteur", "crochet", "coffre"]


@pytest.mark.parametrize("slug", EPREUVES)
def test_chaque_epreuve_se_gagne_au_bouton(banc, slug):
    r = banc(_jeu(ROBOT + """
        const d = aller(L, o, '%s');
        if (!d) return { erreur: 'saut' };
        const ouverte = !!L.B.epreuve, avant = L.B.partie.argent;
        jouer(L, o, d);
        return { ouverte: ouverte, defi: L.B.defi && L.B.defi.slug, epreuve: !!L.B.epreuve,
                 fait: !!L.B.partie.defisFaits['%s'], gain: L.B.partie.argent - avant, prime: d.prime,
                 carnet: L.B.partie.carnet.slice(-2).map(function (l) { return l.t; }) };
    """ % (slug, slug)))
    assert r.get("erreur") is None, r
    assert r["ouverte"], "COMMENCER n'ouvre pas l'épreuve"
    assert r["fait"], r
    assert r["defi"] is None and r["epreuve"] is False
    assert r["gain"] == r["prime"], r


@pytest.mark.parametrize("slug", EPREUVES)
def test_sans_rien_faire_chaque_epreuve_se_rate(banc, slug):
    """Le juge d'en haut mord : un joueur qui ne touche à rien ne gagne rien."""
    r = banc(_jeu("""
        const d = aller(L, o, '%s'), avant = L.B.partie.argent;
        for (let n = 0; n < d.chrono_s * 60 + 30 && L.B.defi; n++) o.frame(1);
        return { defi: !!L.B.defi, fait: !!L.B.partie.defisFaits['%s'], gain: L.B.partie.argent - avant,
                 carnet: L.B.partie.carnet.slice(-1)[0].t };
    """ % (slug, slug)))
    assert r["defi"] is False and r["fait"] is False and r["gain"] == 0, r
    assert r["carnet"].startswith("DÉFI RATÉ"), r


def test_esquive_abandonne_et_rend_les_boutons(banc):
    r = banc(_jeu("""
        aller(L, o, 'radio');
        o.frame(L.Adresse.PRET + 2);
        const pendant = { epreuve: !!L.B.epreuve, etiquette: L.Entree.etiquettesTactiles('epreuve').esquive };
        o.tape('ShiftLeft', 2);
        return { pendant: pendant, defi: !!L.B.defi, epreuve: !!L.B.epreuve, carnet: L.B.partie.carnet.slice(-1)[0].t };
    """))
    assert r["pendant"] == {"epreuve": True, "etiquette": "ABANDONNER"}
    assert r["defi"] is False and r["epreuve"] is False
    assert r["carnet"] == "DÉFI RATÉ : LA RADIO DE LA POLICE"


def test_pendant_l_epreuve_le_joueur_ne_marche_pas_et_ne_frappe_pas(banc):
    """⚠️ Les ratons et la danse se jouent aux flèches, la danse à FRAPPE : sans les portes de
    `B.epreuve`, chaque appel ferait marcher le personnage hors de son comptoir, ou frapper."""
    r = banc(_jeu("""
        aller(L, o, 'ratons');
        const j = L.B.joueur, x = j.x, y = j.y;
        let vitesse = 0;
        // ⚠️ Les QUATRE directions, et la vitesse autant que la place : face au comptoir,
        // pousser vers lui ne déplace personne, épreuve ou pas.
        for (const t of ['KeyW', 'KeyD', 'KeyS', 'KeyA']) {
            o.touche(t);
            for (let k = 0; k < 15; k++) { o.frame(1); vitesse = Math.max(vitesse, Math.abs(j.vx) + Math.abs(j.vy)); }
            o.relacher(t); o.frame(2);
        }
        let frappe = false;
        // ⚠️ Aux poings, FRAPPE tenue CHARGE (`j.charge`) et part au relâché (`j.phase`).
        o.touche('Space');
        for (let k = 0; k < 6; k++) { o.frame(1); frappe = frappe || !!j.phase || j.charge > 0; }
        o.relacher('Space');
        for (let k = 0; k < 4; k++) { o.frame(1); frappe = frappe || !!j.phase; }
        return { dx: j.x - x, dy: j.y - y, vitesse: vitesse, attaque: frappe, defi: L.B.defi && L.B.defi.slug };
    """))
    assert r["dx"] == 0 and r["dy"] == 0 and r["vitesse"] == 0, r
    assert r["attaque"] is False
    assert r["defi"] == "ratons"


@pytest.mark.parametrize("slug", ["crochet", "coffre"])
def test_le_clavier_ne_crochete_jamais_une_goupille(banc, slug):
    """Le catalogue exclut le clavier du cadenas et du coffre, et c'est VRAI : ses huit
    directions tombent toujours entre deux goupilles. On essaie les huit, longtemps, sur
    beaucoup de goupilles tirées."""
    r = banc(_jeu("""
        const d = aller(L, o, '%s');
        const COMBOS = [['KeyW'], ['KeyW', 'KeyD'], ['KeyD'], ['KeyD', 'KeyS'], ['KeyS'], ['KeyS', 'KeyA'], ['KeyA'], ['KeyA', 'KeyW']];
        const TOUCHE = { haut: 'KeyW', bas: 'KeyS', gauche: 'KeyA', droite: 'KeyD' };
        o.frame(L.Adresse.PRET + 1);
        let goupilles = 0, essais = 0;
        for (let tour = 0; tour < 12; tour++) {
            const e = L.B.epreuve;
            if (!e) break;
            if (e.code) while (L.B.epreuve && L.B.epreuve.pos < e.code.length) {
                const t = TOUCHE[e.code[L.B.epreuve.pos]]; o.touche(t); o.frame(2); o.relacher(t); o.frame(2);
            }
            for (const combo of COMBOS) {
                combo.forEach(function (t) { o.touche(t); });
                o.frame(60); essais++;
                combo.forEach(function (t) { o.relacher(t); });
                o.frame(1);
                if (L.B.epreuve) goupilles = L.B.epreuve.k;
            }
            if (L.B.epreuve) L.B.epreuve.cible = L.B.epreuve.cible;   // la même goupille
            L.B.defi.t = 0;                                          // le chrono ne coupe pas l'essai
        }
        return { goupilles: goupilles, essais: essais, fait: !!L.B.partie.defisFaits['%s'] };
    """ % (slug, slug)))
    assert r["essais"] >= 80
    assert r["goupilles"] == 0 and r["fait"] is False, r


def test_le_meme_cadenas_se_crochete_au_stick_du_doigt(banc):
    """Le doigt, lui, y va : le stick virtuel est analogique, comme celui de la manette."""
    r = banc(_jeu("""
        const d = aller(L, o, 'crochet');
        o.frame(L.Adresse.PRET + 1);
        const croix = { x: 90, y: 570 };            // le centre de #croix au banc (20 + 140/2, 500 + 140/2)
        for (let n = 0; n < 1200 && L.B.defi; n++) {
            const a = L.B.epreuve.cible * Math.PI / 180;
            if (n === 0) o.pointeur('pointerdown', croix.x, croix.y);
            o.pointeur('pointermove', croix.x + Math.sin(a) * 60, croix.y - Math.cos(a) * 60);
            o.frame(1);
        }
        o.pointeur('pointerup', croix.x, croix.y);
        return { fait: !!L.B.partie.defisFaits.crochet, appareil: L.Entree.appareil };
    """))
    assert r["fait"] is True, r


def test_un_defi_reussi_ouvre_la_roue_et_le_dit(banc):
    """Le premier palier : un défi réussi, n'importe lequel. Son panneau se plante À CE
    MOMENT-LÀ, devant le kiosque de Madame Thibodeau ; le journal le note, le HUD l'annonce."""
    r = banc(_jeu("""
        const avant = L.B.entites.filter(function (e) { return e.type === 'panneau'; }).length;
        L.B.partie.defisFaits.tour = { jour: 1, temps: 100 };
        L.Histoire.majDeblocages(true);
        const p = L.B.entites.find(function (e) { return e.type === 'panneau' && e.defi === 'roue'; });
        const kiosque = L.Histoire.lieu('kiosque');
        return { ouverts: Object.keys(L.B.partie.defisOuverts), neuf: L.Histoire.defiNeuf(L.B.defs.defis.find(function (d) { return d.slug === 'roue'; })),
                 panneaux: L.B.entites.filter(function (e) { return e.type === 'panneau'; }).length - avant,
                 loin: p ? Math.round(Math.hypot(p.x - kiosque.x, p.y - kiosque.y) / L.TT) : null,
                 message: L.B.message && L.B.message.texte, carnet: L.B.partie.carnet.slice(-1)[0].t };
    """))
    assert r["ouverts"] == ["roue"]
    assert r["neuf"] is True
    assert r["panneaux"] == 1 and r["loin"] is not None and r["loin"] <= 12, r
    assert r["carnet"] == "NOUVEAU DÉFI : LA ROUE DE MADAME THIBODEAU"


def test_l_histoire_ouvre_ses_defis_et_rien_d_autre(banc):
    """m6 ouvre le mannequin (le pickpocket de Josée), m4 la radio du sergent — et une mission
    ne rouvre pas un défi déjà ouvert, ni n'annonce deux fois."""
    r = banc(_jeu("""
        const vus = [];
        L.B.partie.missionsFaites = { m1: 1, m2: 1, m3: 1, m4: 1 };
        L.Histoire.majDeblocages(true); vus.push(Object.keys(L.B.partie.defisOuverts).sort());
        L.B.partie.missionsFaites.m5 = 1; L.B.partie.missionsFaites.m6 = 1;
        L.Histoire.majDeblocages(true); vus.push(Object.keys(L.B.partie.defisOuverts).sort());
        const lignes = L.B.partie.carnet.filter(function (l) { return l.t.indexOf('NOUVEAU DÉFI') === 0; }).length;
        L.Histoire.majDeblocages(true);
        return { vus: vus, lignes: lignes, apres: L.B.partie.carnet.filter(function (l) { return l.t.indexOf('NOUVEAU DÉFI') === 0; }).length };
    """))
    assert r["vus"][0] == ["radio"]
    assert r["vus"][1] == ["mannequin", "radio"]
    assert r["lignes"] == r["apres"] == 2


def test_le_coffre_attend_la_mission_ET_le_cadenas(banc):
    r = banc(_jeu("""
        const coffre = L.B.defs.defis.find(function (d) { return d.slug === 'coffre'; });
        L.B.partie.missionsFaites.m54 = 1;
        L.Histoire.majDeblocages(true);
        const seul = L.Histoire.defiOuvert(coffre);
        L.B.partie.defisFaits.crochet = { jour: 1, temps: 1 };
        L.Histoire.majDeblocages(true);
        return { seul: seul, ensemble: L.Histoire.defiOuvert(coffre) };
    """))
    assert r == {"seul": False, "ensemble": True}


def test_un_defi_ouvert_le_reste_et_se_sauvegarde(banc):
    r = banc(_jeu("""
        L.B.partie.defisFaits.tour = { jour: 1, temps: 100 };
        L.Histoire.majDeblocages(true);
        L.Histoire.proposerDefi('roue');
        L.Hud.fermerMenu();
        const copie = L.Sauvegarde.completer(JSON.parse(JSON.stringify(L.B.partie)), L.B.defs);
        const vieille = L.Sauvegarde.completer({ argent: 5 }, L.B.defs);
        return { lu: copie.defisOuverts.roue.lu, vieille: vieille.defisOuverts };
    """))
    assert r == {"lu": True, "vieille": {}}


#: Rendre la grande carte et lire ce qu'elle a dessiné.
CARTE = """
    function carte(L) { L.Jeu.ouvrirCarte(); L.Jeu.rendre(); const m = L.Hud.marqueurs(); return { defis: m.defis.map(function (d) { return d.slug; }), filtre: m.filtre }; }
"""


def test_la_carte_montre_les_defis_ouverts_selon_ce_qu_on_tient(banc):
    """Au clavier, le cadenas n'est pas sur la carte ; à la manette, il y est. ARME tourne le
    filtre : l'appareil qu'on tient, les deux autres, puis TOUS."""
    r = banc(_jeu(CARTE + """
        L.B.partie.missionsFaites.m53 = 1;
        L.Histoire.majDeblocages(true);
        o.tape('KeyW', 1);                                  // on tient le clavier
        const clavier = carte(L);
        const filtres = [clavier.filtre];
        for (let k = 0; k < 4; k++) { o.tape('Tab', 1); L.Jeu.rendre(); filtres.push(L.Hud.marqueurs().filtre); }
        L.Jeu.fermerCarte();
        o.pad([0, 0, 0, 0], [1]); o.frame(1); o.pad([0, 0, 0, 0], []); o.frame(1);   // un geste neuf à la manette
        const manette = carte(L);
        L.Jeu.fermerCarte();
        return { clavier: clavier.defis, manette: manette.defis, filtres: filtres, appareil: L.Entree.appareil,
                 v1: L.B.defs.defis.filter(function (d) { return !d.debloque && d.ou.indexOf('porte:') === 0 || d.ou.indexOf('foire:') === 0 && !d.debloque; }).length };
    """))
    assert r["appareil"] == "manette"
    assert "crochet" not in r["clavier"] and "crochet" in r["manette"]
    assert "roue" not in r["manette"], "un défi encore caché n'est pas sur la carte"
    assert "tour" in r["clavier"] and "tir" in r["clavier"]
    assert r["filtres"] == ["clavier", "doigts", "manette", "tous", "clavier"]


def test_sur_la_carte_un_defi_neuf_bat_jusqu_a_ce_qu_on_lise_son_panneau(banc):
    r = banc(_jeu(CARTE + """
        L.B.partie.defisFaits.tour = { jour: 1, temps: 100 };
        L.Histoire.majDeblocages(true);
        carte(L);
        const avant = L.Hud.marqueurs().defis.find(function (d) { return d.slug === 'roue'; });
        L.Jeu.fermerCarte();
        L.Histoire.proposerDefi('roue'); L.Hud.fermerMenu();
        carte(L);
        const apres = L.Hud.marqueurs().defis.find(function (d) { return d.slug === 'roue'; });
        return { avant: avant.neuf, apres: apres.neuf, couleur: apres.couleur, jouable: L.Hud.DRAPEAU.jouable };
    """))
    assert r["avant"] is True and r["apres"] is False
    assert r["couleur"] == r["jouable"]


#: Un joueur MALADROIT : il joue, mais à côté — la roue freinée pour tomber à l'opposé du lot,
#: l'anneau lâché hors du vert, le mauvais trou, le faux pas, la toux ratée d'une demi-cadence,
#: la goupille cherchée 30° trop loin. Sans lui, un juge « ne rien faire rate » ne dirait rien
#: d'une règle qui laisserait tout passer dès qu'on appuie.
MALADROIT = """
    const TOUCHE = { haut: 'KeyW', bas: 'KeyS', gauche: 'KeyA', droite: 'KeyD', attaque: 'Space', action: 'KeyE' };
    const AUTRE = { haut: 'bas', bas: 'haut', gauche: 'droite', droite: 'gauche', attaque: 'haut' };
    function taper(o, code) { o.touche(code); o.frame(1); o.relacher(code); o.frame(1); }
    function rater(L, o, d) {
        const r = d.regles;
        let tenue = null;
        for (let n = 0; n < d.chrono_s * 60 + 30 && L.B.defi; n++) {
            const e = L.B.epreuve;
            if (!e || e.t <= L.Adresse.PRET) { o.frame(1); continue; }
            if (e.sorte === 'roue') {
                const v = r.secteurs * r.tours_par_s / 60, F = Math.round(r.freinage_s * 60);
                const fin = ((e.angle + v * (F + 1) / 2 - e.lot) % r.secteurs + r.secteurs) % r.secteurs;
                if (e.freine < 0 && e.pause === 0 && Math.abs(fin - r.secteurs / 2) < 0.3) { taper(o, 'KeyE'); continue; }
            } else if (e.sorte === 'anneaux') {
                if (e.pause === 0 && !tenue && !e.attendLacher) { o.touche('KeyE'); tenue = 'KeyE'; }
                else if (tenue && e.tient && Math.abs(e.charge - e.centre) > r.bande * 1.5) { o.relacher('KeyE'); tenue = null; }
            } else if (e.sorte === 'ratons') {
                if (e.trou >= 0) { taper(o, TOUCHE[AUTRE[r.trous[e.trou]]]); o.frame(1); continue; }
            } else if (e.sorte === 'danse') {
                if (e.appel) { taper(o, TOUCHE[AUTRE[e.appel]]); o.frame(1); continue; }
            } else if (e.sorte === 'mannequin') {
                const x = 0.5 + 0.5 * Math.sin(e.phase);
                if (e.pause === 0 && Math.abs(x - e.centre) > r.zone * 1.5) { taper(o, 'KeyE'); continue; }
            } else if (e.sorte === 'radio') {
                // Il passe et repasse sur la fréquence sans jamais s'y arrêter.
                const voulu = (Math.floor(e.t / 90) % 2) ? 'KeyD' : 'KeyA';
                if (voulu !== tenue) { if (tenue) o.relacher(tenue); o.touche(voulu); tenue = voulu; }
            } else if (e.sorte === 'moteur') {
                const p = Math.round(r.cadence_s * 60);
                if ((e.t + 1) % p === Math.floor(p / 2)) { taper(o, 'KeyE'); continue; }
            } else if (e.sorte === 'crochet') {
                const a = (e.cible + 30) * Math.PI / 180;
                o.pad([Math.sin(a), -Math.cos(a), 0, 0], []);
            } else if (e.sorte === 'coffre' && e.pos >= e.code.length) {
                // ⚠️ Au coffre, il ne rate QUE le code : ses goupilles sont justes. Sinon le
                // cadenas raterait pour lui, et rien ne dirait si le code est jugé.
                const a = e.cible * Math.PI / 180;
                o.pad([Math.sin(a), -Math.cos(a), 0, 0], []);
            } else if (e.sorte === 'coffre') {
                taper(o, TOUCHE[AUTRE[e.code[e.pos]]]); o.frame(1); continue;
            }
            o.frame(1);
        }
        if (tenue) o.relacher(tenue);
        o.pad(null);
    }
"""


@pytest.mark.parametrize("slug", EPREUVES)
def test_le_joueur_maladroit_rate_chaque_epreuve(banc, slug):
    r = banc(_jeu(MALADROIT + """
        const d = aller(L, o, '%s'), avant = L.B.partie.argent;
        rater(L, o, d);
        return { defi: !!L.B.defi, fait: !!L.B.partie.defisFaits['%s'], gain: L.B.partie.argent - avant,
                 carnet: L.B.partie.carnet.slice(-1)[0].t };
    """ % (slug, slug)))
    assert r["defi"] is False and r["fait"] is False and r["gain"] == 0, r
    assert r["carnet"].startswith("DÉFI RATÉ"), r


def test_un_kiosque_dont_le_defi_est_cache_reste_un_kiosque(banc):
    """Par le BOUTON, devant le lance-anneaux : caché, ACTION ne propose rien ; ouvert, il
    propose le défi — la baraque sert de panneau, comme les trois jeux de la v1."""
    r = banc(_jeu("""
        aller(L, o, 'anneaux');
        L.Histoire.abandonnerDefi(); L.Hud.fermerMenu();
        delete L.B.partie.defisOuverts.anneaux;
        o.frame(2);
        o.tape('KeyE', 2);
        const cache = L.B.menu ? L.B.menu.titre : null;
        if (L.B.menu) L.Hud.fermerMenu();
        L.B.partie.defisFaits = { tour: {}, saut: {}, tir: {} };
        L.Histoire.majDeblocages(true);
        o.frame(2);
        o.tape('KeyE', 2);
        return { cache: cache, ouvert: L.B.menu ? L.B.menu.titre : null };
    """))
    assert r["cache"] != "LE LANCER D'ANNEAUX"
    assert r["ouvert"] == "LE LANCER D'ANNEAUX"


def test_chaque_epreuve_du_catalogue_a_son_jeu(banc, paquet):
    r = banc("function (L, o) { return Object.keys(L.Adresse.EPREUVES).sort(); }")
    catalogue = sorted(d["epreuve"] for d in paquet["defis"] if d.get("epreuve"))
    assert catalogue == sorted(EPREUVES) == r
