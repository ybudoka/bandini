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
    """Le premier palier : un défi réussi, n'importe lequel. Les panneaux se plantent À CE
    MOMENT-LÀ, devant le kiosque de Madame Thibodeau et à l'hôpital ; le journal note chacun,
    le HUD les annonce en une ligne."""
    r = banc(_jeu("""
        const avant = L.B.entites.filter(function (e) { return e.type === 'panneau'; }).length;
        L.B.partie.defisFaits.tour = { jour: 1, temps: 100 };
        L.Histoire.majDeblocages(true);
        const p = L.B.entites.find(function (e) { return e.type === 'panneau' && e.defi === 'roue'; });
        const kiosque = L.Histoire.lieu('kiosque');
        return { ouverts: Object.keys(L.B.partie.defisOuverts), neuf: L.Histoire.defiNeuf(L.B.defs.defis.find(function (d) { return d.slug === 'roue'; })),
                 panneaux: L.B.entites.filter(function (e) { return e.type === 'panneau'; }).length - avant,
                 loin: p ? Math.round(Math.hypot(p.x - kiosque.x, p.y - kiosque.y) / L.TT) : null,
                 message: L.B.msg, carnet: L.B.partie.carnet.slice(-2).map(function (l) { return l.t; }) };
    """))
    # ⚠️ Le premier palier en ouvre DEUX : la roue, et le frein pile (2e vague).
    assert r["ouverts"] == ["roue", "frein_pile"]
    assert r["neuf"] is True
    assert r["panneaux"] == 2 and r["loin"] is not None and r["loin"] <= 12, r
    assert r["carnet"] == ["NOUVEAU DÉFI : LA ROUE DE MADAME THIBODEAU", "NOUVEAU DÉFI : LE FREIN PILE DE L'HÔPITAL"]
    assert r["message"] == "2 NOUVEAUX DÉFIS — VOIS LA CARTE", "deux défis ensemble : une seule annonce"


def test_l_histoire_ouvre_ses_defis_et_rien_d_autre(banc):
    """m6 ouvre le mannequin (le pickpocket de Josée), m4 la radio du sergent, m1 et m3 le feu et
    le créneau — et une mission ne rouvre pas un défi déjà ouvert, ni n'annonce deux fois."""
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
    # m1 ouvre le feu du terminus, m3 le créneau, m4 la radio ; m6 le mannequin.
    assert r["vus"][0] == ["creneau", "feu", "radio"]
    assert r["vus"][1] == ["creneau", "feu", "mannequin", "radio"]
    assert r["lignes"] == r["apres"] == 4


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


# --- La 2e vague : au volant ------------------------------------------------------------------

#: Au volant, par la MANETTE : `piloter(o, gaz, frein, volant)` pose les gâchettes (analogiques,
#: boutons 7 et 6 de la disposition standard) et le stick. `auVolant` pose une auto sur la piste
#: de l'épreuve (à `sl` pixels devant la ligne, `lat` à droite) et y assoit le joueur.
VOLANT = """
    function piloter(o, gaz, frein, volant) { o.pad([volant || 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, frein || 0, gaz || 0]); }
    function auVolant(L, o, sl, lat, slug) {
        const p = L.B.conduite.piste, pt = L.Conduite.point(p, sl, lat || 0);
        const v = L.Vehicules.creer(slug || 'auto', pt.x, pt.y, Math.atan2(p.dy, p.dx), { etat: 'stationne', couleur: '#8a8698' });
        L.Entites.indexer(); L.Vehicules.monter(L.B.joueur, v); L.Monde.centrerCamera(v.x, v.y);
        o.frame(2);
        return v;
    }
    /** Le volant qui tient la piste à `lat` pixels à droite de son axe. */
    function tenir(L, v, lat) {
        const p = L.B.conduite.piste, q = L.Conduite.projeter(p, v.x, v.y);
        let e = Math.atan2(p.dy, p.dx) + Math.atan2(lat - q.lat, 28) - v.angle;
        while (e > Math.PI) e -= 2 * Math.PI; while (e < -Math.PI) e += 2 * Math.PI;
        return Math.max(-1, Math.min(1, e * 2.2));
    }
    /** Le volant qui suit la voie sous le char (son sens), sans piste d'épreuve. */
    function tenirLaRue(L, v) {
        const g = L.Monde.fleche(Math.floor(v.x / L.TT), Math.floor(v.y / L.TT));
        const cap = { '>': 0, 'v': Math.PI / 2, '<': Math.PI, '^': -Math.PI / 2 }[g];
        if (cap === undefined) return 0;
        let e = cap - v.angle;
        while (e > Math.PI) e -= 2 * Math.PI; while (e < -Math.PI) e += 2 * Math.PI;
        return Math.max(-1, Math.min(1, e * 2));
    }
    /** `tenir`, sur une piste donnée (celle d'une étape de la Chef). */
    function tenir2(L, v, p, lat) {
        const q = L.Conduite.projeter(p, v.x, v.y);
        let e = Math.atan2(p.dy, p.dx) + Math.atan2(lat - q.lat, 28) - v.angle;
        while (e > Math.PI) e -= 2 * Math.PI; while (e < -Math.PI) e += 2 * Math.PI;
        return Math.max(-1, Math.min(1, e * 2.2));
    }
    /** Où il s'arrêterait, pied au frein à partir de maintenant (la physique de `majPhysique` :
        ⚠️ sous 0,15 px/image, le frein est la MARCHE ARRIÈRE — il ralentit moins fort). */
    function arretA(v) {
        let u = v.vitesse, d = 0;
        while (u > 0.05) { u = (u - (u > 0.15 ? v.def.frein : v.def.acceleration * 0.7)) * v.def.friction; d += Math.max(0, u); }
        return d;
    }
"""


def test_le_frein_pile_se_gagne_lance_et_s_arrete_dans_la_case(banc):
    r = banc(_jeu(VOLANT + """
        const d = aller(L, o, 'frein_pile'), r = d.regles, p = L.B.conduite.piste;
        const v = auVolant(L, o, -8 * L.TT, 0);
        let lanceA = null;
        for (let n = 0; n < 900 && L.B.defi; n++) {
            const q = L.Conduite.projeter(p, v.x, v.y);
            if (L.B.conduite.phase === 'lance' && lanceA === null) lanceA = v.vitesse / v.def.vitesse_max;
            const freine = L.B.conduite.phase === 'lance' && q.s + arretA(v) >= r.case * L.TT - 2;
            piloter(o, freine ? 0 : 1, freine && v.vitesse > 0.05 ? 1 : 0, tenir(L, v, 0));
            o.frame(1);
        }
        o.pad(null);
        return { fait: !!L.B.partie.defisFaits.frein_pile, lanceA: lanceA, carnet: L.B.partie.carnet.slice(-1)[0].t };
    """))
    assert r["fait"] is True, r
    assert r["lanceA"] >= 0.55


@pytest.mark.parametrize("freinA,raison", [(1, "TROP LOIN"), (-2, "TROP COURT")])
def test_le_frein_pile_se_rate_trop_loin_ou_trop_court(banc, freinA, raison):
    """`freinA` : on freine une tuile trop tard, ou deux trop tôt."""
    r = banc(_jeu(VOLANT + """
        const d = aller(L, o, 'frein_pile'), r = d.regles, p = L.B.conduite.piste;
        const v = auVolant(L, o, -8 * L.TT, 0);
        for (let n = 0; n < 900 && L.B.defi; n++) {
            const q = L.Conduite.projeter(p, v.x, v.y);
            const freine = L.B.conduite.phase === 'lance' && q.s + arretA(v) >= (r.case + %d) * L.TT;
            piloter(o, freine ? 0 : 1, freine && v.vitesse > 0.05 ? 1 : 0, tenir(L, v, 0));
            o.frame(1);
        }
        o.pad(null);
        return { fait: !!L.B.partie.defisFaits.frein_pile, carnet: L.B.partie.carnet.slice(-1)[0].t };
    """ % freinA))
    assert r["fait"] is False
    assert r["carnet"] == "DÉFI RATÉ : LE FREIN PILE DE L'HÔPITAL", r


def test_le_frein_pile_refuse_qui_passe_la_ligne_au_pas(banc):
    r = banc(_jeu(VOLANT + """
        const d = aller(L, o, 'frein_pile'), p = L.B.conduite.piste;
        const v = auVolant(L, o, -3 * L.TT, 0);
        for (let n = 0; n < 240 && L.B.defi; n++) {
            piloter(o, v.vitesse < 1 ? 0.5 : 0, 0, tenir(L, v, 0));
            o.frame(1);
        }
        o.pad(null);
        return { phase: L.B.conduite && L.B.conduite.phase, defi: L.B.defi && L.B.defi.slug };
    """))
    assert r == {"phase": "approche", "defi": "frein_pile"}


def test_le_demarrage_au_feu_se_gagne_au_vert_et_se_rate_avant(banc):
    r = banc(_jeu(VOLANT + """
        const issues = {};
        for (const tricheur of [false, true]) {
            aller(L, o, 'feu');
            const v = auVolant(L, o, -L.TT / 2, 0);
            let vuRouge = false;
            for (let n = 0; n < 900 && L.B.defi; n++) {
                const c = L.B.conduite;
                vuRouge = vuRouge || c.phase === 'rouge';
                const go = c.phase === 'vert' || (tricheur && c.phase === 'rouge' && c.t > 20);
                piloter(o, go ? 1 : 0, 0, go ? tenir(L, v, 0) : 0);
                o.frame(1);
            }
            o.pad(null);
            issues[tricheur ? 'tricheur' : 'honnete'] = { rouge: vuRouge, fait: !!L.B.partie.defisFaits.feu,
                                                          carnet: L.B.partie.carnet.slice(-1)[0].t };
            L.Vehicules.descendre(L.B.joueur, true); L.Entites.retirer(v);
            delete L.B.partie.defisFaits.feu;
        }
        return issues;
    """))
    assert r["honnete"]["rouge"] and r["honnete"]["fait"], r
    assert r["tricheur"]["rouge"] and not r["tricheur"]["fait"], r
    assert r["tricheur"]["carnet"] == "DÉFI RATÉ : LE DÉMARRAGE DU TERMINUS"


@pytest.mark.parametrize("vehicule", ["moto", "auto", "autobus", "pelleteuse"])
@pytest.mark.parametrize("reflexe,gagne", [(18, True), (60, False)])
def test_le_feu_se_mesure_au_char_qu_on_conduit(banc, vehicule, reflexe, gagne):
    """Un réflexe d'un tiers de seconde gagne, avec la moto comme avec la pelleteuse ; une
    seconde de rêverie au vert perd, avec les deux aussi."""
    r = banc(_jeu(VOLANT + """
        aller(L, o, 'feu');
        const v = auVolant(L, o, -L.TT / 2, 0, '%s');
        let attente = 0;
        for (let n = 0; n < 1500 && L.B.defi; n++) {
            const c = L.B.conduite;
            if (c.phase === 'vert') attente++;
            const go = c.phase === 'vert' && attente > %d;
            piloter(o, go ? 1 : 0, 0, go ? tenir(L, v, 0) : 0);
            o.frame(1);
        }
        o.pad(null);
        return !!L.B.partie.defisFaits.feu;
    """ % (vehicule, reflexe)))
    assert r is gagne


def test_le_creneau_pose_deux_chars_et_la_place_a_la_mesure_du_sien(banc):
    r = banc(_jeu(VOLANT + """
        aller(L, o, 'creneau');
        const v = auVolant(L, o, -3 * L.TT, 0);
        o.frame(2);
        const c = L.B.conduite, p = c.piste;
        const garees = c.garees.map(function (g) { return Math.round(L.Conduite.projeter(p, g.x, g.y).s); });
        // Dans la place, droit, arrêté : on pose le char comme s'il s'y était glissé.
        const pt = L.Conduite.point(p, c.milieu, 0);
        v.x = pt.x; v.y = pt.y; v.vx = 0; v.vy = 0; v.vitesse = 0; v.angle = Math.atan2(p.dy, p.dx);
        L.Entites.indexer();
        for (let n = 0; n < 60 && L.B.defi; n++) { piloter(o, 0, 0, 0); o.frame(1); }
        o.pad(null);
        return { place: c.place, lon: v.def.longueur, garees: garees, milieu: c.milieu, fait: !!L.B.partie.defisFaits.creneau,
                 restent: c.garees.filter(function (g) { return L.B.entites.indexOf(g) >= 0; }).length };
    """))
    assert abs(r["place"] - 1.6 * r["lon"]) < 0.01
    assert r["garees"][0] < r["milieu"] < r["garees"][1]
    assert r["fait"] is True, r
    assert r["restent"] == 0, "les deux chars de l'épreuve repartent avec elle"


def test_le_creneau_se_rate_en_touchant_un_char(banc):
    r = banc(_jeu(VOLANT + """
        aller(L, o, 'creneau');
        const v = auVolant(L, o, -3 * L.TT, 0);
        o.frame(2);
        const c = L.B.conduite, p = c.piste, pt = L.Conduite.point(p, c.milieu, 0);
        v.x = pt.x; v.y = pt.y; v.vx = 0; v.vy = 0; v.vitesse = 0; v.angle = Math.atan2(p.dy, p.dx);
        L.Entites.indexer();
        for (let n = 0; n < 240 && L.B.defi; n++) { piloter(o, 1, 0, 0); o.frame(1); }
        o.pad(null);
        return { fait: !!L.B.partie.defisFaits.creneau, carnet: L.B.partie.carnet.slice(-1)[0].t, message: L.B.msg };
    """))
    assert r["fait"] is False
    assert r["carnet"] == "DÉFI RATÉ : LE CRÉNEAU DEVANT LA PLANQUE", r
    assert r["message"] == "DÉFI RATÉ — TU AS ACCROCHÉ", r


def test_le_slalom_se_gagne_en_zigzag_et_se_rate_tout_droit(banc):
    r = banc(_jeu(VOLANT + """
        const issues = {};
        for (const droit of [false, true]) {
            const d = aller(L, o, 'slalom'), r = d.regles;
            const c = L.B.conduite, p = c.piste;
            const v = auVolant(L, o, -5 * L.TT, 0);
            function voulu(sl) {
                // Entre deux cônes, on vise le côté du PROCHAIN — dans sa voie (droite) ou dans l'autre.
                const k = Math.max(0, Math.min(c.cones.length - 1, Math.round((sl - r.depart * L.TT) / (r.pas * L.TT))));
                return k % 2 === 0 ? 3 : -19;
            }
            let temps = null;
            for (let n = 0; n < 1500 && L.B.defi; n++) {
                const q = L.Conduite.projeter(p, v.x, v.y);
                const lat = droit ? 2 : voulu(q.s + 28);
                piloter(o, v.vitesse < 1.8 ? 0.8 : 0, 0, tenir(L, v, lat));
                o.frame(1);
                if (L.B.conduite && L.B.conduite.phase === 'slalom') temps = L.B.conduite.t;
            }
            o.pad(null);
            issues[droit ? 'droit' : 'zigzag'] = { fait: !!L.B.partie.defisFaits.slalom, temps: temps,
                                                    tombes: c.cones.filter(function (k) { return k.tombe; }).length,
                                                    carnet: L.B.partie.carnet.slice(-1)[0].t };
            L.Vehicules.descendre(L.B.joueur, true); L.Entites.retirer(v);
            delete L.B.partie.defisFaits.slalom;
        }
        return issues;
    """))
    assert r["zigzag"]["fait"], r
    assert not r["droit"]["fait"] and r["droit"]["carnet"] == "DÉFI RATÉ : LE SLALOM DE L'HÔTEL", r


#: Une auto posée sur la rue la plus proche du joueur, dans le sens de la voie, et le joueur dedans.
SUR_LA_RUE = """
    function surLaRue(L, o, slug) {
        const j = L.B.joueur, r = L.Monde.routeLaPlusProche(j.x, j.y, 16);
        const g = L.Monde.fleche(Math.floor(r.x / L.TT), Math.floor(r.y / L.TT));
        const cap = { '>': 0, 'v': Math.PI / 2, '<': Math.PI, '^': -Math.PI / 2 }[g] || 0;
        const v = L.Vehicules.creer(slug || 'auto', r.x, r.y, cap, { etat: 'stationne', couleur: '#8a8698' });
        L.Entites.indexer(); L.Vehicules.monter(j, v); L.Monde.centrerCamera(v.x, v.y);
        o.frame(2);
        return v;
    }
"""


def test_le_verre_de_lait_tient_a_la_gachette_douce_et_deborde_au_clavier(banc):
    """À la manette, 60 % de gaz puis 50 % de frein : pas une goutte. Au clavier, UN départ et
    UN arrêt — tout le gaz, tout le frein, les seuls que les touches connaissent — et le verre
    est vide. C'est ce qui l'exclut du clavier, et c'est la physique qui le dit."""
    r = banc(_jeu(VOLANT + SUR_LA_RUE + """
        const out = {};
        for (const appareil of ['manette', 'clavier']) {
            aller(L, o, 'lait');
            const v = surLaRue(L, o);
            for (let n = 0; n < 50; n++) {
                if (appareil === 'manette') piloter(o, 0.6, 0, 0); else o.touche('KeyW');
                o.frame(1);
            }
            o.pad(null); o.relacher('KeyW');
            const vite = v.vitesse;
            for (let n = 0; n < 80 && L.B.defi && v.vitesse > 0.05; n++) {
                if (appareil === 'manette') piloter(o, 0, 0.5, 0); else o.touche('KeyS');
                o.frame(1);
            }
            o.pad(null); o.relacher('KeyS'); o.frame(2);
            out[appareil] = { vite: vite, lait: L.B.conduite ? L.B.conduite.lait : null, defi: L.B.defi && L.B.defi.slug,
                              message: L.B.msg };
            if (L.B.defi) L.Histoire.abandonnerDefi();
            L.Vehicules.descendre(L.B.joueur, true); L.Entites.retirer(v);
        }
        return out;
    """))
    assert r["manette"]["lait"] == 0 and r["manette"]["defi"] == "lait", r
    assert r["manette"]["vite"] > 1.0
    assert r["clavier"]["defi"] is None and "LE LAIT A DÉBORDÉ" in r["clavier"]["message"], r


def test_le_verre_de_lait_se_livre_au_casse_croute(banc):
    r = banc(_jeu(VOLANT + SUR_LA_RUE + """
        aller(L, o, 'lait');
        const v = surLaRue(L, o);
        piloter(o, 0.5, 0, 0); o.frame(10); o.pad(null);
        const l = L.Histoire.lieu('casse_croute'), rue = L.Monde.routeLaPlusProche(l.x, l.y, 3);
        v.x = rue.x; v.y = rue.y; v.vx = 0; v.vy = 0; v.vitesse = 0;
        L.Entites.indexer();
        o.frame(5);
        return { fait: !!L.B.partie.defisFaits.lait, loin: Math.hypot(rue.x - l.x, rue.y - l.y) / L.TT };
    """))
    assert r["loin"] < 4
    assert r["fait"] is True


def test_le_remorquage_pose_ses_deux_chars_et_se_gagne_en_douceur(banc):
    """La remorqueuse attend près de la fourrière, l'épave plus loin. On monte, on recule sur
    l'épave, le KLAXON l'accroche ; ramenée à la fourrière et arrêtée, c'est gagné — et les
    deux chars de l'épreuve repartent, sauf celui qu'on conduit."""
    r = banc(_jeu(VOLANT + """
        aller(L, o, 'remorquage');
        const c = L.B.conduite, rq = c.remorqueuse, ep = c.epave, j = L.B.joueur;
        const lot = L.Monde.carte.fourriere, f = { x: (lot.x + lot.largeur / 2) * L.TT, y: (lot.y + lot.hauteur / 2) * L.TT };
        const loin = Math.round(Math.hypot(ep.x - f.x, ep.y - f.y) / L.TT);
        L.Vehicules.monter(j, rq); o.frame(2);
        // Devant l'épave, dans son axe : elle est DERRIÈRE la fourche.
        const d = (rq.def.longueur + ep.def.longueur) / 2 + 2;
        rq.angle = ep.angle; rq.x = ep.x + Math.cos(ep.angle) * d; rq.y = ep.y + Math.sin(ep.angle) * d;
        rq.vx = 0; rq.vy = 0; rq.vitesse = 0; L.Entites.indexer();
        o.tape('Space', 2);
        const accroche = rq.remorque === ep;
        o.frame(30);
        const ailleurs = !!L.B.partie.defisFaits.remorquage;      // arrêtée, mais pas dans la cour
        // Dans la cour du lot, arrêtée : l'épave suit sur la fourche.
        rq.x = f.x; rq.y = f.y; rq.vitesse = 0; rq.vx = 0; rq.vy = 0; L.Entites.indexer();
        o.frame(6);
        return { loin: loin, accroche: accroche, ailleurs: ailleurs, fait: !!L.B.partie.defisFaits.remorquage,
                 restent: [rq, ep].map(function (v) { return L.B.entites.indexOf(v) >= 0; }),
                 message: L.B.msg };
    """))
    assert r["loin"] >= 12, r
    assert r["accroche"] is True, r
    assert r["ailleurs"] is False, "arrêté hors de la cour, rien n'est livré"
    assert r["fait"] is True, r
    assert r["restent"] == [True, False], "on garde la remorqueuse qu'on conduit ; l'épave repart"


def test_au_remorquage_un_coup_de_frein_fait_lacher_l_epave(banc):
    r = banc(_jeu(VOLANT + """
        aller(L, o, 'remorquage');
        const c = L.B.conduite, rq = c.remorqueuse, ep = c.epave, j = L.B.joueur;
        L.Vehicules.monter(j, rq); o.frame(2);
        const d = (rq.def.longueur + ep.def.longueur) / 2 + 2;
        rq.angle = ep.angle; rq.x = ep.x + Math.cos(ep.angle) * d; rq.y = ep.y + Math.sin(ep.angle) * d;
        rq.vx = 0; rq.vy = 0; rq.vitesse = 0; L.Entites.indexer();
        o.tape('Space', 2);
        // Lancé en douceur (70 % de gaz, sous le seuil) jusqu'à un bon pas, puis un coup de
        // frein franc. ⚠️ Au pas, le même coup de frein ne secoue presque rien : il dure trop peu.
        for (let n = 0; n < 240 && L.B.defi && rq.vitesse < 1.6; n++) { piloter(o, 0.7, 0, tenirLaRue(L, rq)); o.frame(1); }
        const secousses = c.secousses, vite = rq.vitesse;
        for (let n = 0; n < 60 && L.B.defi; n++) { piloter(o, 0, 1, 0); o.frame(1); }
        o.pad(null);
        return { avant: secousses, vite: vite, defi: L.B.defi && L.B.defi.slug, accroche: rq.remorque === ep,
                 message: L.B.msg };
    """))
    assert r["avant"] == 0 and r["vite"] >= 1.6, r
    assert r["defi"] is None and r["accroche"] is False, r
    assert "L'ÉPAVE A LÂCHÉ" in r["message"], r


# --- La 3e vague : dans la rue, et la Chef ----------------------------------------------------

#: Marcher au clavier vers un point (huit directions), comme un joueur : les flèches qu'il faut,
#: tenues tant qu'on n'y est pas.
MARCHER = """
    let tenues = [];
    function marcherVers(o, j, x, y, marge) {
        const dx = x - j.x, dy = y - j.y, voulues = [];
        if (Math.abs(dx) > marge) voulues.push(dx > 0 ? 'KeyD' : 'KeyA');
        if (Math.abs(dy) > marge) voulues.push(dy > 0 ? 'KeyS' : 'KeyW');
        tenues.filter(function (t) { return voulues.indexOf(t) < 0; }).forEach(function (t) { o.relacher(t); });
        voulues.filter(function (t) { return tenues.indexOf(t) < 0; }).forEach(function (t) { o.touche(t); });
        tenues = voulues;
    }
    function toutLacher(o) { tenues.forEach(function (t) { o.relacher(t); }); tenues = []; }
"""


@pytest.mark.parametrize("ecart,gagne,raison", [(7, True, None), (4, False, "IL T'A VU"), (11, False, "TU L'AS PERDU")])
def test_la_filature_se_gagne_a_bonne_distance(banc, ecart, gagne, raison):
    """Au clavier, en marchant : à sept tuiles derrière lui, on le suit jusqu'au bout ; à quatre,
    il nous voit en se retournant ; à onze, on le perd."""
    r = banc(_jeu(MARCHER + """
        aller(L, o, 'filature');
        const j = L.B.joueur, e = L.B.rue, p = e.piste;
        for (let n = 0; n < 7200 && L.B.defi; n++) {
            const cible = L.Conduite.point(p, e.s - %d * L.TT, e.lat);
            marcherVers(o, j, cible.x, cible.y, 6);
            o.frame(1);
        }
        toutLacher(o);
        return { fait: !!L.B.partie.defisFaits.filature, message: L.B.msg, suspect: L.B.entites.indexOf(e.suspect) >= 0 };
    """ % ecart))
    assert r["fait"] is gagne, r
    if raison:
        assert r["message"] == "DÉFI RATÉ — " + raison, r
    assert r["suspect"] is False, "le suspect repart avec l'épreuve"


ESQUIVE = MARCHER + """
    function combat(L, o, frappeur) {
        const j = L.B.joueur, e = L.B.rue, q = e.adversaire, R = 3 * L.TT;
        // D'abord, entrer dans le ring.
        for (let n = 0; n < 900 && L.B.defi && e.phase !== 'combat'; n++) { marcherVers(o, j, e.depart.x + R, e.depart.y, 4); o.frame(1); }
        let roulades = 0, a = Math.atan2(j.y - e.depart.y, j.x - e.depart.x);
        for (let n = 0; n < 2400 && L.B.defi; n++) {
            const d = Math.hypot(q.x - j.x, q.y - j.y);
            if (frappeur && d < 30) { toutLacher(o); o.tape('Space', 1); continue; }
            // Il arme son coup, TOUT PRÈS : on roule. Sinon on tourne dans le ring, en
            // gardant le cercle — c'est le pas du boxeur, pas la fuite.
            if (q.phase === 'anticipation' && d < 24 && !j.roule) {
                o.touche('ShiftLeft'); o.frame(1); o.relacher('ShiftLeft');
                roulades++;
                continue;
            }
            if (Math.hypot(j.x - (e.depart.x + Math.cos(a) * R), j.y - (e.depart.y + Math.sin(a) * R)) < 10) a += 0.35;
            marcherVers(o, j, e.depart.x + Math.cos(a) * R, e.depart.y + Math.sin(a) * R, 4);
            o.frame(1);
        }
        toutLacher(o);
        return { fait: !!L.B.partie.defisFaits.esquive, message: L.B.msg, roulades: roulades,
                 vie: j.vie / j.vieMax, reste: L.B.entites.indexOf(q) >= 0 };
    }
"""


def test_l_esquive_se_gagne_sans_frapper(banc):
    r = banc(_jeu(ESQUIVE + """
        aller(L, o, 'esquive');
        return combat(L, o, false);
    """))
    assert r["fait"] is True, r
    assert r["roulades"] >= 3, "il a fallu esquiver pour de vrai"
    assert r["reste"] is False


def test_l_esquive_se_rate_au_premier_coup_de_poing(banc):
    r = banc(_jeu(ESQUIVE + """
        aller(L, o, 'esquive');
        return combat(L, o, true);
    """))
    assert r["fait"] is False and r["message"] == "DÉFI RATÉ — TU AS FRAPPÉ", r


def test_l_esquive_se_rate_sans_esquiver(banc):
    """Entré dans le ring, planté là, les bras le long du corps : il nous sonne avant la fin."""
    r = banc(_jeu(MARCHER + """
        aller(L, o, 'esquive');
        const j = L.B.joueur, e = L.B.rue;
        for (let n = 0; n < 900 && L.B.defi && e.phase !== 'combat'; n++) { marcherVers(o, j, e.depart.x + 3 * L.TT, e.depart.y, 4); o.frame(1); }
        // Au MILIEU du ring : repoussé par les coups, on y reste — c'est le coup qui juge.
        for (let n = 0; n < 120 && L.B.defi; n++) { marcherVers(o, j, e.depart.x, e.depart.y, 3); o.frame(1); }
        toutLacher(o);
        for (let n = 0; n < 2400 && L.B.defi; n++) o.frame(1);
        return { fait: !!L.B.partie.defisFaits.esquive, message: L.B.msg };
    """))
    assert r["fait"] is False and r["message"] == "DÉFI RATÉ — IL T'A SONNÉ", r


def test_la_chef_enchaine_les_trois_epreuves_a_leurs_panneaux(banc):
    """Chaque étape est l'épreuve d'un autre défi, à son panneau, avec ses règles. On joue le
    frein pile et le slalom au volant (le pilote du banc), puis on pose le char dans la place du
    créneau ; entre deux étapes, on saute d'un panneau à l'autre."""
    r = banc(_jeu(VOLANT + """
        const d = aller(L, o, 'chef'), c = L.B.conduite;
        const etapes = [];
        function poserSur(sl) {
            const p = c.etape.e.piste, pt = L.Conduite.point(p, sl, 0);
            let v = L.B.joueur.dansVehicule;
            if (!v) {
                v = L.Vehicules.creer('auto', pt.x, pt.y, Math.atan2(p.dy, p.dx), { etat: 'stationne', couleur: '#8a8698' });
                L.Entites.indexer(); L.Vehicules.monter(L.B.joueur, v); o.frame(2);
            }
            v.x = pt.x; v.y = pt.y; v.vx = 0; v.vy = 0; v.vitesse = 0; v.angle = Math.atan2(p.dy, p.dx);
            L.Entites.indexer(); L.Monde.centrerCamera(v.x, v.y);
            return v;
        }
        // 1. Le frein pile.
        etapes.push(c.etape.d.slug);
        let v = poserSur(-8 * L.TT);
        o.frame(2);
        const rf = c.etape.d.regles;
        for (let n = 0; n < 900 && L.B.defi && c.k === 0; n++) {
            const q = L.Conduite.projeter(c.etape.e.piste, v.x, v.y);
            const freine = c.etape.e.phase === 'lance' && q.s + arretA(v) >= rf.case * L.TT - 2;
            piloter(o, freine ? 0 : 1, freine && v.vitesse > 0.05 ? 1 : 0, tenir2(L, v, c.etape.e.piste, 0));
            o.frame(1);
        }
        o.pad(null);
        // 2. Le slalom.
        etapes.push(c.etape && c.etape.d.slug);
        v = poserSur(-5 * L.TT);
        const rs = c.etape.d.regles, cones = c.etape.e.cones;
        for (let n = 0; n < 1500 && L.B.defi && c.k === 1; n++) {
            const q = L.Conduite.projeter(c.etape.e.piste, v.x, v.y);
            const k = Math.max(0, Math.min(cones.length - 1, Math.round((q.s + 28 - rs.depart * L.TT) / (rs.pas * L.TT))));
            piloter(o, v.vitesse < 1.8 ? 0.8 : 0, 0, tenir2(L, v, c.etape.e.piste, k % 2 === 0 ? 3 : -19));
            o.frame(1);
        }
        o.pad(null);
        // 3. Le créneau.
        etapes.push(c.etape && c.etape.d.slug);
        v = poserSur(c.etape.e.milieu);
        for (let n = 0; n < 90 && L.B.defi; n++) o.frame(1);
        return { etapes: etapes, fait: !!L.B.partie.defisFaits.chef, message: L.B.msg };
    """.replace("tenir(L", "tenir(L")))
    assert r["etapes"] == ["frein_pile", "slalom", "creneau"], r
    assert r["fait"] is True, r


def test_le_ring_de_l_esquive_ne_touche_aucune_chaussee(banc):
    r = banc(_jeu("""
        aller(L, o, 'esquive');
        const e = L.B.rue, d = L.B.defs.defis.find(function (q) { return q.slug === 'esquive'; }), R = d.regles.ring;
        const cx = Math.floor(e.depart.x / L.TT), cy = Math.floor(e.depart.y / L.TT);
        let chaussee = 0;
        for (let y = cy - R; y <= cy + R; y++) for (let x = cx - R; x <= cx + R; x++) {
            if ((x - cx) * (x - cx) + (y - cy) * (y - cy) > R * R) continue;
            if (L.Monde.fleche(x, y) !== '.' || L.Monde.estChaussee(x, y)) chaussee++;
        }
        const loin = Math.hypot(e.depart.x - L.B.joueur.x, e.depart.y - L.B.joueur.y) / L.TT;
        // Hors du ring (sur sa couronne, dehors), le combat attend ; dedans, il part.
        const j = L.B.joueur;
        j.x = e.depart.x + (R + 1) * L.TT; j.y = e.depart.y; L.Entites.indexer();
        o.frame(30);
        const dehors = e.phase;
        j.x = e.depart.x + L.TT; j.y = e.depart.y; L.Entites.indexer();
        o.frame(2);
        return { chaussee: chaussee, loin: loin, dehors: dehors, dedans: e.phase };
    """))
    assert r["chaussee"] == 0
    assert r["loin"] <= 12
    assert r["dehors"] == "attend", "le combat attend qu'on entre dans le ring"
    assert r["dedans"] == "combat"
