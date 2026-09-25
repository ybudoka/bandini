"""Un comptoir reste ouvert après un achat — on le quitte par B, Échap ou RETOUR.

Demande de Martin (22 sept. 2026) : « lors d'une sélection d'un achat ou autre,
je veux rester dans le même menu, pas quitter, on quitte seulement avec B ou Esc
ou un menu retour ou quitter ». La moitié des comptoirs le faisaient déjà (Chez
Gus, le casse-croûte, le coffre) ; les autres se refermaient au premier choix,
et il fallait revenir au comptoir, relancer le menu, redescendre à la ligne.

⚠️ Le juge presse le VRAI bouton ACTION (`o.tape('KeyE')`), dans la vraie
boucle : c'est `Hud.choisirLigne` qui décide de fermer, pas le `faire` de la
ligne — un juge qui appellerait `item.faire()` ne verrait pas le menu partir.
"""

import json

from app import carte, missions

#: Les points qui ne passent PAS par un menu (voir test_interieurs_js.py).
# Le point d'un personnage posé dedans se lit dans le catalogue (voir `test_interieurs_js.py`).
SANS_MENU = ("escalier", "fouiller", "rame") + tuple(
    p["ou"][len("point:"):] for p in missions.PERSONNAGES if p["ou"].startswith("point:"))

#: ⚠️ Les SEULES lignes d'un comptoir qui le referment : le choix y est un
#: départ. Dormir passe au noir ; le Clairon se lit, en voix, hors du menu.
#: Allonger cette liste demande une raison de la même force.
QUI_FERMENT = ("DORMIR JUSQU’AU MATIN", "DORMIR JUSQU’AU SOIR", "LE CLAIRON DE LA BAIE")

#: Les comptoirs de la ville livrée, un par type et par famille (`genre`).
COMPTOIRS = sorted({(p["type"], p.get("genre") or "")
                    for piece in carte.exporter()["interieurs"].values()
                    for p in piece["points"] if p["type"] not in SANS_MENU})

#: Ouvrir un menu comme le jeu l'ouvre — `refaire` compris —, poser le pouce
#: sur la ligne `i`, et presser ACTION.
PRESSER = """
    function presser(o, L, faireMenu, i) {
        // ⚠️ Un fondu en cours (dormir) fige la boucle : ACTION n'y serait pas lu.
        if (L.B.transition) o.fondu();
        L.B.msg = null; L.B.msgT = 0;
        const menu = faireMenu();
        // Le choix d'avant a raccourci la liste (la commande au hacker) : rien a presser.
        if (!menu.items[i] || !menu.items[i].faire || menu.items[i].actif === false) return null;
        menu.refaire = faireMenu;
        L.Hud.ouvrirMenu(menu);
        menu.curseur = i;
        const libelle = menu.items[i].libelle;
        o.tape('KeyE', 2);
        const reste = L.B.menu === menu;
        const vu = { libelle: libelle, reste: reste, rang: i, curseur: reste ? menu.curseur : null,
                     sur: reste ? menu.sur || null : null, items: reste ? menu.items.map(function (q) {
                         return q.libelle + '|' + (q.detail || ''); }) : null };
        L.Hud.fermerMenu();
        return vu;
    }
    function actives(menu) {
        const out = [];
        menu.items.forEach(function (q, i) { if (!q.entete && q.actif !== false && q.faire) out.push(i); });
        return out;
    }
"""


def test_chaque_ligne_de_chaque_comptoir_garde_le_menu_ouvert(banc):
    """Toutes les lignes de tous les comptoirs de la ville, une par une, au bouton :
    le menu est encore là après, et le pouce n'a pas bougé."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const comptoirs = %s, c = L.Monde.carte, j = L.B.joueur, p = L.B.partie;
        const vus = [], sansLigne = [];
        for (const [type, genre] of comptoirs) {
            let point = null, piece = null;
            for (const cle in c.def.interieurs) {
                const q = (c.def.interieurs[cle].points || []).find(function (x) {
                    return x.type === type && (x.genre || '') === genre;
                });
                if (q) { point = q; piece = c.def.interieurs[cle]; break; }
            }
            if (!point) continue;
            L.B.interieur = piece;
            // De quoi TOUT s'offrir, et une raison de se faire soigner.
            p.argent = 999999; p.casier = 3; j.vie = 10; p.heure = 0.5;
            const faireMenu = function () { return L.Missions.menuDuPoint(point); };
            const menu = faireMenu();
            if (!menu) continue;
            const lignes = actives(menu);
            if (!lignes.length) { sansLigne.push(type + ':' + genre); continue; }
            lignes.forEach(function (i) {
                p.argent = 999999; j.vie = 10; p.heure = 0.5;
                const vu = presser(o, L, faireMenu, i);
                if (!vu) return;
                vu.comptoir = type + (genre ? ':' + genre : '');
                vus.push(vu);
            });
        }
        L.B.interieur = null;
        return { vus: vus, sansLigne: sansLigne };
    }""" % (PRESSER, json.dumps(COMPTOIRS)))
    vus = r["vus"]
    assert len({v["comptoir"] for v in vus}) >= 8, f"trop peu de comptoirs jugés : {r}"
    fermes = [f"{v['comptoir']} → {v['libelle']}" for v in vus
              if not v["reste"] and v["libelle"] not in QUI_FERMENT]
    assert fermes == [], f"ces choix referment encore le comptoir : {fermes}"
    # Un choix peut RENOMMER sa ligne (le commerce acheté devient la caisse, la
    # commande au hacker devient « IL Y TRAVAILLE ») : le pouce reste au même
    # RANG, c'est tout ce qu'on exige — il ne file pas en haut de la liste.
    bouges = [f"{v['comptoir']} → {v['libelle']} (rang {v['rang']}, pouce au {v['curseur']})" for v in vus
              if v["reste"] and v["curseur"] != v["rang"]]
    assert bouges == [], f"le pouce a bougé : {bouges}"
    # Les départs, eux, partent encore.
    for v in vus:
        if v["libelle"] in QUI_FERMENT:
            assert not v["reste"], f"{v['libelle']} devait quitter le comptoir"


def test_un_achat_se_voit_dans_le_menu_resté_ouvert(banc):
    """Resté ouvert, le menu doit dire la vérité : le magot en haut à droite a
    fondu, et la tenue achetée chez Rosa se dit PORTÉE."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const c = L.Monde.carte, p = L.B.partie;
        let point = null;
        for (const cle in c.def.interieurs) {
            const q = (c.def.interieurs[cle].points || []).find(function (x) { return x.type === 'acheter'; });
            if (q && cle !== 'armurerie') { point = q; L.B.interieur = c.def.interieurs[cle]; break; }
        }
        p.argent = 5000;
        const faireMenu = function () { return L.Missions.menuDuPoint(point); };
        const menu = faireMenu();
        const i = menu.items.findIndex(function (q) { return !q.entete && q.faire && p.tenues.indexOf(
            (L.B.defs.tenues.find(function (t) { return t.nom.toUpperCase() === q.libelle; }) || {}).slug) < 0; });
        const vu = presser(o, L, faireMenu, i);
        return { vu: vu, argent: p.argent };
    }""" % PRESSER)
    vu = r["vu"]
    assert vu["reste"], f"Rosa a refermé son comptoir : {vu}"
    assert vu["sur"] == f"{r['argent']} $", f"le magot affiché n'a pas fondu : {vu}"
    assert f"{vu['libelle']}|PORTÉE" in vu["items"], f"la tenue achetée ne se dit pas portée : {vu}"


def test_au_rideau_ti_guy_garde_son_menu_sauf_pour_vendre(banc):
    """Le menu du garage ouvert du volant : réparer, repeindre, assurer le
    laissent ouvert et refait ; VENDRE le ferme — le char est parti, et le
    volant avec. REPARTIR est la sortie."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const j = L.B.joueur, p = L.B.partie;
        const v = L.Vehicules.creer('auto', j.x + 20, j.y, 0, { etat: 'stationne' });
        L.Vehicules.monter(j, v);
        v.vie = Math.round(v.vieMax / 2);
        const faireMenu = function () { return L.Missions.menuDuRideau(v); };
        const indice = function (debut) {
            return faireMenu().items.findIndex(function (q) { return q.libelle.indexOf(debut) === 0; });
        };
        const out = {};
        for (const debut of ['RÉPARER', 'REPEINDRE', 'ASSURER', 'REPARTIR', 'VENDRE']) {
            p.argent = 999999;
            out[debut] = presser(o, L, faireMenu, indice(debut));
        }
        out.vie = v.vie === v.vieMax;
        return out;
    }""" % PRESSER)
    for debut in ("RÉPARER", "REPEINDRE", "ASSURER"):
        assert r[debut]["reste"], f"{debut} referme le garage : {r[debut]}"
    assert any(i.endswith("|DÉJÀ ASSURÉ") for i in r["ASSURER"]["items"]), \
        f"le menu resté ouvert ne dit pas le char assuré : {r['ASSURER']}"
    assert r["vie"], "RÉPARER n'a pas réparé"
    assert not r["REPARTIR"]["reste"], "REPARTIR doit quitter le garage"
    assert not r["VENDRE"]["reste"], "vendu au rideau, il n'y a plus de char à qui parler"


def test_le_toast_d_un_achat_se_lit_par_dessus_le_comptoir(banc):
    """⚠️ Un comptoir qui reste ouvert cachait le mot de l'achat : le toast se
    dessinait SOUS le voile et la boîte du menu. Il se dessine maintenant
    au-dessus de la boîte, par-dessus le voile."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        L.B.partie.argent = 5000;
        L.Hud.ouvrirMenu(L.Missions.menuArmurerie());
        L.Hud.message('CHAR RACHETÉ — IL EST DANS LA COUR');
        const ctx = L.Base.ecran(), appels = [];
        const avant = ctx.fillRect;
        let voile = -1;
        ctx.fillRect = function (x, y, l, h) {
            if (ctx.fillStyle === 'rgba(11,10,18,0.6)' && l >= 400) voile = appels.length;
            appels.push({ style: ctx.fillStyle, y: y, h: h });
            return avant.apply(this, arguments);
        };
        L.Jeu.rendre();
        ctx.fillRect = avant;
        const toast = appels.findIndex(function (a) { return a.style === 'rgba(11,10,18,0.75)' && a.h === 16; });
        return { voile: voile, toast: toast, y: toast >= 0 ? appels[toast].y : null, reste: L.B.msgT };
    }""")
    assert r["toast"] > r["voile"] >= 0, f"le toast se dessine encore sous le voile du menu : {r}"
    assert r["reste"] > 0
