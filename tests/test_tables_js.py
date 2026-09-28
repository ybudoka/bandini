"""Les tables du Dragon d'or, JOUÉES au banc (docs/jalons/le-casino-du-petit-canton.md, vague 2).

Chaque table s'ouvre au bouton ACTION devant son feutre, prend la mise et paie selon ses règles ; le navigateur
joue les mêmes règles que Python, coup pour coup ; son hasard n'est pas celui du jeu ; sur des dizaines de
milliers de coups, chaque table rend moins qu'on y met ; la limite du jour ; la bille qui roule avant qu'on
annonce ; GAUCHE et DROITE qui changent le pari ; et un croupier derrière chaque table.
"""

import json
import random
from itertools import product

import pytest

from app import casino
from app import tables_de_jeu as t

DEDANS = """
  function dedans(L, o, lieu, point) {
    const B = L.B, j = B.joueur, M = L.Monde;
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    const pt = B.interieur.points.find(function (q) { return q.type === point; });
    j.x = pt.x * 16 + 8; j.y = (pt.y + 1) * 16 + 8; j.angle = -Math.PI / 2; j.face = 'haut'; L.Entites.indexer();
    o.frame(2);
    return pt;
  }
"""

#: La stratégie de l'habitué, en JS — la même que `test_tables_de_jeu.habitue_bj` et `tables_de_jeu.poker_habitue`.
HABITUE = """
  function habitueBj(T) {
    return function (main, visible) {
      const v = T.bjValeur(main), up = T.bjValeur([visible]).total;
      if (v.souple) return v.total <= 17 || (v.total === 18 && up >= 9);
      if (v.total >= 17) return false;
      if (v.total >= 13) return !(up >= 2 && up <= 6);
      if (v.total === 12) return !(up >= 4 && up <= 6);
      return true;
    };
  }
  function habituePoker(T, cartes) {
    const f = T.pokerForce(cartes);
    if (f[0] >= 1) return true;
    const seuil = [T.regles().dame, 4, 2];
    for (let i = 0; i < 3; i++) if (f[i + 1] !== seuil[i]) return f[i + 1] > seuil[i];
    return true;
  }
"""


def habitue_bj(main, visible):
    """L'habitué de `test_tables_de_jeu`, recopié : un fichier de juges n'en importe pas un autre."""
    total, souple = t.bj_valeur(main)
    v = t.bj_valeur([visible])[0]
    if souple:
        return total <= 17 or (total == 18 and v in (9, 10, 11))
    if total >= 17:
        return False
    if total >= 13:
        return not 2 <= v <= 6
    return not 4 <= v <= 6 if total == 12 else True


@pytest.mark.parametrize("jeu", ["blackjack", "roulette", "poker", "sic_bo", "baccara"])
def test_chaque_table_s_ouvre_au_bouton_et_prend_la_mise(banc, jeu):
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B;
        B.partie.argent = 500;
        dedans(L, o, 'nord_casino', 'JEU');
        const invite = B.invite;
        o.tape('KeyE', 2);
        const menu = B.menu;
        const vu = { invite: invite, titre: menu && menu.titre, aide: menu && menu.aide,
                     geste: menu && menu.items[menu.curseur].libelle, mise: L.Tables.etat().mise };
        o.tape('KeyE', 2);                                     // DONNER, LANCER, SECOUER
        let t = L.Tables.enCours('JEU');
        vu.phase = t && t.phase;
        if (t && t.phase === 'joue') {                         // le blackjack : on reste ; le poker : on joue
            B.menu.curseur = 'JEU' === 'blackjack' ? 1 : 0;
            o.tape('KeyE', 2);
            t = L.Tables.enCours('JEU');
        }
        vu.reste = B.menu === menu;
        vu.fin = t && t.phase;
        vu.coups = L.Tables.compteur('JEU').coups;
        vu.gain = t && t.resultat ? t.resultat.gain : null;
        vu.mise_totale = t && t.resultat ? t.resultat.mise : null;
        vu.argent = B.partie.argent;
        return vu;
    }""".replace("JEU", jeu))
    assert r["invite"] == {"blackjack": "LE BLACKJACK", "roulette": "LA ROULETTE", "poker": "LE POKER",
                           "sic_bo": "LE SIC BO", "baccara": "LE BACCARA"}[jeu], r
    assert r["titre"] == t.JEUX[jeu] and "RETOUR " in r["aide"] and "COUPS AUJOURD" in r["aide"], r
    assert r["geste"] in ("DONNER", "LANCER LA BILLE", "SECOUER LES DÉS"), r
    assert r["reste"], "le geste a refermé la table"
    assert r["fin"] == "fin" and r["coups"] == 1, r
    assert r["argent"] == 500 - r["mise_totale"] + r["gain"], r


def test_le_navigateur_joue_les_regles_de_python_coup_pour_coup(banc):
    """Deux mille paquets battus par Python, joués par le navigateur : les mêmes mains, les mêmes gains, au
    blackjack (avec l'habitué), au poker et au baccara ; et toutes les cases de la roulette, tous les jets du sic
    bo, pour chaque pari."""
    rng = random.Random(3)
    paquets = [rng.sample(range(52), 52) for _ in range(2000)]
    attendu = {
        "bj": [list(t.bj_jouer(p, habitue_bj)) for p in paquets],
        "poker": [t.poker_regler(p[:3], p[3:6], j) for p in paquets for j in (t.poker_habitue(p[:3]), True, False)],
        "bac": [[list(t.bac_coup(p)), [t.bac_regler(q, *t.bac_coup(p)) for q in t.PARIS_BACCARA]] for p in paquets],
        "roulette": [t.roulette_paie(q, n) for q in (*t.CHANCES, *range(37)) for n in range(37)],
        "sic_bo": [t.sic_bo_paie(q, d) for q in ("petit", "grand", 1, 2, 3, 4, 5, 6) for d in product(range(1, 7), repeat=3)],
    }
    r = banc("function (L, o) {" + HABITUE + """
        L.Jeu.commencer();
        const T = L.Tables, P = PAQUETS, h = habitueBj(T);
        const des = [];
        for (let a = 1; a <= 6; a++) for (let b = 1; b <= 6; b++) for (let c = 1; c <= 6; c++) des.push([a, b, c]);
        const chances = ['rouge', 'noir', 'pair', 'impair'].concat(Array.from({ length: 37 }, function (_, i) { return i; }));
        return {
            bj: P.map(function (p) { const m = T.bjJouer(p, h); return [m.paie, m.joueur, m.croupier]; }),
            poker: [].concat.apply([], P.map(function (p) {
                const j = p.slice(0, 3), c = p.slice(3, 6);
                return [habituePoker(T, j), true, false].map(function (joue) { return T.pokerRegler(j, c, joue); });
            })),
            bac: P.map(function (p) {
                const k = T.bacCoup(p);
                return [[k.joueur, k.banque], ['joueur', 'banque', 'egalite'].map(function (q) { return T.bacRegler(q, k.joueur, k.banque); })];
            }),
            roulette: [].concat.apply([], chances.map(function (q) {
                return Array.from({ length: 37 }, function (_, n) { return T.roulettePaie(q, n); });
            })),
            sic_bo: [].concat.apply([], ['petit', 'grand', 1, 2, 3, 4, 5, 6].map(function (q) {
                return des.map(function (d) { return T.sicBoPaie(q, d); });
            })),
        };
    }""".replace("PAQUETS", json.dumps(paquets)))
    for cle in attendu:
        assert r[cle] == json.loads(json.dumps(attendu[cle])), cle


def test_des_dizaines_de_milliers_de_coups_rendent_moins_qu_on_y_met(banc):
    """Le hasard du NAVIGATEUR (la graine, le numéro du coup, le sel de la table) : chaque table rend moins de
    cent pour cent, près de ce que Python calcule ou mesure."""
    r = banc("function (L, o) {" + HABITUE + """
        L.Jeu.commencer();
        const T = L.Tables, h = habitueBj(T), N = 40000;
        let bj = 0, pk = 0, pkMise = 0, rouge = 0, plein = 0, petit = 0, chiffre = 0;
        const bac = { joueur: 0, banque: 0, egalite: 0 };
        for (let n = 0; n < N; n++) {
            bj += T.bjJouer(T.paquet('blackjack', n), h).paie;
            const p = T.paquet('poker', n), joue = habituePoker(T, p.slice(0, 3));
            pk += T.pokerRegler(p.slice(0, 3), p.slice(3, 6), joue); pkMise += joue ? 2 : 1;
            const k = T.bacCoup(T.paquet('baccara', n));
            for (const q in bac) bac[q] += T.bacRegler(q, k.joueur, k.banque);
            const num = T.numeroDuTour(n);
            rouge += T.roulettePaie('rouge', num); plein += T.roulettePaie(17, num);
            const d = T.desDuJet(n);
            petit += T.sicBoPaie('petit', d); chiffre += T.sicBoPaie(4, d);
        }
        return { blackjack: bj / N, poker: pk / pkMise, joueur: bac.joueur / N, banque: bac.banque / N,
                 egalite: bac.egalite / N, rouge: rouge / N, plein: plein / N, petit: petit / N, chiffre: chiffre / N };
    }""")
    attendu = {"blackjack": 0.979, "poker": 0.980, **t.bac_retours_exacts(), "rouge": 36 / 37, "plein": 36 / 37,
               "petit": t.sic_bo_retour("petit"), "chiffre": t.sic_bo_retour(4)}
    #: Quatre écarts types sur quarante mille coups : le plein et l'égalité paient gros, ils varient.
    ecart = {"plein": 0.12, "egalite": 0.06, "chiffre": 0.025}
    for cle, retour in r.items():
        assert retour < 1.0 or cle == "plein", f"{cle} rend {retour:.4f}"
        assert abs(retour - attendu[cle]) < ecart.get(cle, 0.025), (cle, retour, attendu[cle])


def test_jouer_aux_tables_ne_touche_pas_au_hasard_du_jeu(banc):
    """Un coup à chaque table entre deux tirages ne change pas le tirage suivant — et le même coup revient au
    même numéro, différent d'une table à l'autre (chacune son sel)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, T = L.Tables;
        L.graine(3);
        const temoin = [B.rng(), B.rng(), B.rng()];
        L.graine(3);
        B.partie.argent = 100000;
        for (let i = 0; i < 10; i++) {
            T.bjDonner(); T.bjRester(); T.lancer(); T.secouer(); T.pkDonner(); T.pkDecider(true); T.bacDonner();
        }
        const apres = [B.rng(), B.rng(), B.rng()];
        return { temoin: temoin, apres: apres,
                 meme: T.paquet('poker', 7).join() === T.paquet('poker', 7).join(),
                 sels: new Set(['blackjack', 'poker', 'baccara'].map(function (j) { return T.paquet(j, 7).slice(0, 6).join(); })).size,
                 numeros: new Set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(T.numeroDuTour)).size };
    }""")
    assert r["apres"] == r["temoin"], "jouer aux tables a décalé le hasard du jeu"
    assert r["meme"] and r["sels"] == 3 and r["numeros"] >= 6, r


def test_la_table_ferme_pour_toi_apres_quarante_coups(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, T = L.Tables;
        B.partie.argent = 100000;
        let ok = 0;
        for (let i = 0; i < T.regles().par_jour + 5; i++) if (T.lancer()) ok++;
        const roulette = ok;
        const bj = T.bjDonner();
        B.partie.jour++;
        return { roulette: roulette, bj: bj, lendemain: T.lancer() };
    }""")
    assert r["roulette"] == t.COUPS_PAR_JOUR, r
    assert r["bj"] is True, "la limite d'une table a fermé les autres"
    assert r["lendemain"] is True, "la roulette ne rouvre pas le lendemain"


def test_la_triche_machines_sans_limite_ouvre_les_tables_aussi(banc):
    """La bascule MACHINES SANS LIMITE (onglet TRICHES) vaut aux tables : la roulette se lance au-delà de
    ses quarante coups, son menu dit SANS LIMITE et garde son geste allumé ; éteinte, la table referme."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, T = L.Tables, n = T.regles().par_jour;
        B.partie.argent = 1000000;
        B.partie.triches.machines = true;
        let ok = 0;
        for (let i = 0; i < n + 5; i++) if (T.lancer()) ok++;
        const m = T.menu('roulette'), geste = m.items[m.items.length - 1];
        B.partie.triches.machines = false;
        const m2 = T.menu('roulette');
        return { ok: ok, n: n, aide: m.aide, actif: geste.actif, eteinte: !!T.lancer(),
                 actifEteinte: m2.items[m2.items.length - 1].actif };
    }""")
    assert r["ok"] == r["n"] + 5, r
    assert "SANS LIMITE" in r["aide"] and r["actif"] is True, r
    assert r["eteinte"] is False and r["actifEteinte"] is False, r


def test_la_bille_roule_avant_qu_on_annonce_mais_le_gain_est_deja_paye(banc):
    """Payé tout de suite (fermer le menu pendant que la roue tourne ne vole personne), annoncé quand la bille
    s'arrête — et l'argent en haut du menu ne saute pas avant."""
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tables;
        B.partie.argent = 1000;
        dedans(L, o, 'nord_casino', 'roulette');
        o.tape('KeyE', 2);
        // Un numéro plein : on cherche le tour qui le fait tomber, pour voir un gain.
        const n = T.numeroDuTour(T.compteur('roulette').total);
        T.etat().roulette = 'numero'; T.etat().numero = n;
        L.Hud.rafraichirMenu(); B.menu.curseur = B.menu.items.length - 1;
        o.tape('KeyE', 1);
        const t = T.enCours('roulette');
        const vu = { n: t.n, voulu: n, gain: t.resultat.gain, argent: B.partie.argent, sur: B.menu.sur,
                     annonce_tot: t.annonce, images_tot: t.images };
        o.frame(150);
        vu.annonce = t.annonce; vu.images = t.images; vu.sur_apres = B.menu.sur; vu.msg = B.msg;
        return vu;
    }""")
    mise = t.MISES[0]
    assert r["n"] == r["voulu"] and r["gain"] == mise * t.NUMERO_PLEIN, r
    assert r["argent"] == 1000 - mise + r["gain"], "le gain n'est pas payé tout de suite"
    assert r["annonce_tot"] is False and r["sur"] == f"{1000 - mise} $", r
    assert r["annonce"] is True and r["images"] > 100 and r["sur_apres"] == f"{r['argent']} $", r
    assert f"+{r['gain'] - mise} $" in r["msg"], r


def test_gauche_et_droite_changent_le_pari_et_la_mise(banc):
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tables;
        B.partie.argent = 1000;
        dedans(L, o, 'nord_casino', 'roulette');
        o.tape('KeyE', 2);
        B.menu.curseur = 0;                         // PARI
        const avant = T.etat().roulette;
        o.tape('ArrowRight', 2);
        const droite = T.etat().roulette;
        o.tape('ArrowLeft', 2); o.tape('ArrowLeft', 2);
        const gauche = T.etat().roulette;
        const lignes = B.menu.items.map(function (i) { return i.libelle; });
        o.tape('KeyE', 2);                          // ACTION : un cran de plus
        const action = T.etat().roulette;
        return { avant: avant, droite: droite, gauche: gauche, action: action, lignes: lignes,
                 detail: B.menu.items[0].detail, curseur: B.menu.curseur };
    }""")
    assert (r["avant"], r["droite"], r["gauche"], r["action"]) == ("rouge", "noir", "numero", "rouge"), r
    assert r["lignes"] == ["PARI", "NUMÉRO", "MISE", "LANCER LA BILLE"], "UN NUMÉRO ouvre sa ligne"
    assert r["detail"] == "ROUGE" and r["curseur"] == 0, r


def test_un_croupier_tient_chaque_table(banc):
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B;
        dedans(L, o, 'nord_casino', 'poker');
        o.frame(120);
        return B.entites.filter(function (e) { return e.vivant && e.poste && e.tenue && e.tenue.couleur_haut === '#f4f1e8'; })
                        .map(function (e) { return [Math.floor(e.x / 16), Math.floor(e.y / 16)]; });
    }""")
    attendu = sorted([x, 3] for _, x in casino.TABLES)
    assert sorted(r) == attendu, r


def test_chaque_geste_a_son_bruit(banc):
    """Les jetons à la mise, les cartes, la bille, les dés (`Son.SFX`, « La cabane et le casino s'entendent ») —
    et le gros lot d'un numéro plein sonne comme celui de la machine."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, T = L.Tables, S = L.Son.SFX, entendus = [];
        ['jetons', 'cartes_donnees', 'roulette_bille', 'des_sic_bo', 'gain_machine', 'jackpot'].forEach(function (n) {
            const vrai = S[n]; S[n] = function () { entendus.push(n); return vrai.apply(this, arguments); };
        });
        B.partie.argent = 1000;
        const vu = {};
        const ecouter = function (nom, geste) { entendus.length = 0; geste(); vu[nom] = entendus.slice(); };
        ecouter('blackjack', function () { T.bjDonner(); });
        ecouter('roulette', function () { T.lancer(); });
        ecouter('sic_bo', function () { T.secouer(); });
        ecouter('baccara', function () { T.bacDonner(); });
        // Un numéro plein qui tombe : l'annonce, quand la bille s'arrête, est celle du gros lot.
        T.etat().roulette = 'numero'; T.etat().numero = T.numeroDuTour(T.compteur('roulette').total);
        T.lancer();
        const t = T.enCours('roulette');
        entendus.length = 0;
        const c = o.doc.createElement('canvas').getContext('2d');
        L.Hud.ouvrirMenu(T.menu('roulette'));
        for (let k = 0; k < 130; k++) B.menu.dessiner(c, 0, 0);
        vu.annonce = entendus.slice();
        return vu;
    }""")
    assert r["blackjack"] == ["jetons", "cartes_donnees"], r
    assert r["roulette"] == ["jetons", "roulette_bille"] and r["sic_bo"] == ["jetons", "des_sic_bo"], r
    assert r["baccara"] == ["jetons", "cartes_donnees"], r
    assert r["annonce"] == ["jackpot"], r
