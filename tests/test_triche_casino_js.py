"""Tricher au Dragon d'or, JOUÉ au banc (docs/jalons/le-casino-du-petit-canton.md, vague 3).

Le blackjack se donne d'un SABOT (deux paquets, rebrassés à la carte de coupe) ; après vingt mains on sait
COMPTER, et le compte s'affiche à côté du sabot ; on peut DOUBLER. La sécurité du casino regarde tes mises :
un garde vient te glisser un mot, puis te reconduit à la porte, et le portier ne te rouvre que le lendemain —
une semaine à la récidive. Frapper un garde, c'est une semaine d'un coup, et la police. Le navigateur joue les
mêmes règles que Python (`tables_de_jeu.py`), et rien de tout ça ne tire un dé du jeu.
"""

import json
import math
import random

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
  function aLaPorte(L, o) {
    const B = L.B, j = B.joueur;
    const porte = L.Monde.carte.def.portes.find(function (q) { return q.lieu === 'nord_casino' && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; j.angle = -Math.PI / 2; j.face = 'haut'; L.Entites.indexer();
    o.frame(1);
    return porte;
  }
"""

#: L'habitué, en JS : la stratégie de base, et quand il double — les mêmes que `tables_de_jeu.bj_habitue*`.
HABITUE = """
  function habitue(T) {
    return function (main, visible) {
      const v = T.bjValeur(main), up = T.bjValeur([visible]).total;
      if (v.souple) return v.total <= 17 || (v.total === 18 && up >= 9);
      if (v.total >= 17) return false;
      if (v.total >= 13) return !(up >= 2 && up <= 6);
      if (v.total === 12) return !(up >= 4 && up <= 6);
      return true;
    };
  }
  function double(T) {
    return function (main, visible) {
      const v = T.bjValeur(main), up = T.bjValeur([visible]).total;
      if (v.souple) return ((v.total === 17 || v.total === 18) && up >= 3 && up <= 6)
        || ((v.total === 15 || v.total === 16) && up >= 4 && up <= 6) || ((v.total === 13 || v.total === 14) && up >= 5 && up <= 6);
      return (v.total === 11 && up !== 11) || (v.total === 10 && up <= 9) || (v.total === 9 && up >= 3 && up <= 6);
    };
  }
"""


def test_le_navigateur_joue_le_sabot_et_surveille_comme_python(banc):
    """Deux mille bouts de sabot joués par l'habitué qui double : les mêmes mains, les mêmes gains ; le même
    compte Hi-Lo ; et l'œil de la sécurité pense la même chose de mille mises et de mille gains."""
    rng = random.Random(8)
    sabots = [rng.sample(list(range(52)) * 2, 20) for _ in range(2000)]
    mises = [(rng.choice([0, 30, 120]), rng.choice([None, 10, 25, 80]), rng.choice(t.MISES_BLACKJACK),
              rng.uniform(-6, 8)) for _ in range(1000)]
    gains = [(rng.uniform(0, 140), rng.uniform(-500, 3000), rng.choice([-50, 0, 30, 750])) for _ in range(1000)]
    attendu = {
        "mains": [list(t.bj_main(p, t.bj_habitue, t.bj_habitue_double)) for p in sabots],
        "hilo": [t.hi_lo(c) for c in range(52)],
        "mises": [list(t.chaleur_de_la_mise(*m)) for m in mises],
        "gains": [t.chaleur_du_gain(*g) for g in gains],
    }
    r = banc("function (L, o) {" + HABITUE + """
        L.Jeu.commencer();
        const T = L.Tables, C = L.Casino, h = habitue(T), d = double(T);
        return {
            mains: SABOTS.map(function (p) { const m = T.bjMain(p, h, d); return [m.paie, m.fois, m.joueur, m.croupier]; }),
            hilo: Array.from({ length: 52 }, function (_, c) { return T.hiLo(c); }),
            mises: MISES.map(function (m) { return C.chaleurDeLaMise(m[0], m[1], m[2], m[3]); }),
            gains: GAINS.map(function (g) { return C.chaleurDuGain(g[0], g[1], g[2]); }),
        };
    }""".replace("SABOTS", json.dumps(sabots)).replace("MISES", json.dumps(mises)).replace("GAINS", json.dumps(gains)))
    assert r["mains"] == json.loads(json.dumps(attendu["mains"]))
    assert r["hilo"] == attendu["hilo"]
    for a, b in zip(r["mises"], attendu["mises"]):
        assert math.isclose(a[0], b[0], abs_tol=1e-9) and math.isclose(a[1], b[1], abs_tol=1e-9), (a, b)
    assert all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(r["gains"], attendu["gains"]))


def test_le_sabot_sert_main_apres_main_au_bouton_et_se_rebrasse(banc):
    """DONNER, RESTER, au bouton : les cartes sortent du sabot dans l'ordre (la main d'après commence où la
    précédente s'arrête) ; passé la carte de coupe, le croupier rebrasse un sabot neuf, et ça s'entend."""
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tables, S = L.Son.SFX, entendus = [];
        const vrai = S.sabot_brasse; S.sabot_brasse = function () { entendus.push(B.partie.tables.sabot.n); return vrai.apply(this, arguments); };
        B.partie.argent = 100000;
        B.partie.triches.machines = true;                      // assez de mains pour passer la coupe
        dedans(L, o, 'nord_casino', 'blackjack');
        o.tape('KeyE', 2);
        const menu = B.menu, suites = [], mains = [];
        for (let i = 0; i < 40 && B.menu === menu; i++) {
            const s = T.sabot(), avant = { n: s.n, pos: s.pos };
            B.menu.curseur = B.menu.items.length - 1;           // DONNER
            o.tape('KeyE', 2);
            let t = T.enCours('blackjack');
            if (t.phase === 'joue') { B.menu.curseur = 1; o.tape('KeyE', 2); t = T.enCours('blackjack'); }
            const cartes = T.cartesDuSabot(t.sabot);
            mains.push({ avant: avant, sabot: t.sabot, depart: t.depart, apres: T.sabot().pos,
                         vues: t.joueur.length + t.croupier.length,
                         ordre: [cartes[t.depart], cartes[t.depart + 1], cartes[t.depart + 2], cartes[t.depart + 3]].join() ===
                                [t.joueur[0], t.croupier[0], t.joueur[1], t.croupier[1]].join() });
        }
        return { mains: mains, entendus: entendus, coupe: T.regles().sabot.coupe, taille: T.cartesDuSabot(0).length,
                 differents: T.cartesDuSabot(0).join() !== T.cartesDuSabot(1).join() };
    }""")
    assert r["taille"] == 52 * t.PAQUETS_DU_SABOT and r["coupe"] == t.COUPE and r["differents"], r
    mains = r["mains"]
    assert len(mains) == 40
    for m in mains:
        assert m["ordre"], "les cartes ne sortent pas du sabot dans l'ordre"
        assert m["apres"] == m["depart"] + m["vues"], m
        if m["avant"]["pos"] >= t.COUPE:
            assert m["sabot"] == m["avant"]["n"] + 1 and m["depart"] == 0, f"la coupe est sortie, pas de brassage : {m}"
        else:
            assert m["sabot"] == m["avant"]["n"] and m["depart"] == m["avant"]["pos"], m
    brasses = [m["sabot"] for m in mains if m["depart"] == 0 and m["sabot"] > 0]
    assert len(brasses) >= 2 and r["entendus"] == brasses, r["entendus"]


def test_apres_vingt_mains_on_sait_compter_et_le_compte_s_affiche(banc):
    """Pas de ligne COMPTER avant la vingtième main ; ensuite, on la choisit au bouton, et le compte affiché est
    celui des cartes VUES (pas la cachée du croupier) — le Hi-Lo de Python."""
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tables;
        B.partie.argent = 100000;
        B.partie.triches.machines = true;
        dedans(L, o, 'nord_casino', 'blackjack');
        o.tape('KeyE', 2);
        const avant = B.menu.items.map(function (i) { return i.libelle; });
        for (let i = 0; i < T.APPRENDRE; i++) { T.bjDonner(); T.bjRester(); }
        L.Hud.fermerMenu(); o.frame(2); o.tape('KeyE', 2);
        const apres = B.menu.items.map(function (i) { return i.libelle; });
        B.menu.curseur = apres.indexOf('COMPTER');
        o.tape('KeyE', 2);                                      // COMPTER : OUI
        const compter = T.etat().compter, msg = B.msg;
        B.menu.curseur = B.menu.items.length - 1;
        o.tape('KeyE', 2);                                      // une main de plus
        let t = T.enCours('blackjack');
        const pendant = t.phase === 'joue' ? T.compte() : null;
        const vuesPendant = t.phase === 'joue' ? t.joueur.concat([t.croupier[0]]) : null;
        const depart = t.depart, n = t.sabot;
        if (t.phase === 'joue') { B.menu.curseur = 1; o.tape('KeyE', 2); t = T.enCours('blackjack'); }
        return { avant: avant, apres: apres, compter: compter, pendant: pendant, vuesPendant: vuesPendant,
                 sorties: T.cartesDuSabot(n).slice(0, depart), fin: T.compte(), toutes: T.cartesDuSabot(T.sabot().n).slice(0, T.sabot().pos),
                 restantes: T.cartesDuSabot(T.sabot().n).length - T.sabot().pos };
    }""")
    assert r["avant"] == ["MISE", "DONNER"], r["avant"]
    assert r["apres"] == ["MISE", "COMPTER", "DONNER"] and r["compter"] is True, r
    hl = lambda cartes: sum(t.hi_lo(c) for c in cartes)  # noqa: E731
    if r["pendant"]:
        assert r["pendant"]["courant"] == hl(r["sorties"]) + hl(r["vuesPendant"]), "le compte voit la carte cachée"
    assert r["fin"]["courant"] == hl(r["toutes"]) and r["fin"]["restantes"] == r["restantes"], r["fin"]
    assert math.isclose(r["fin"]["parPaquet"], t.compte_par_paquet(hl(r["toutes"]), r["restantes"])), r["fin"]


def test_doubler_au_bouton(banc):
    """Sur ses deux premières cartes : DOUBLER, une deuxième mise, UNE carte, et le croupier joue."""
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tables;
        B.partie.argent = 1000;
        dedans(L, o, 'nord_casino', 'blackjack');
        o.tape('KeyE', 2);
        let t = null;
        for (let i = 0; i < 30; i++) {                          // une main qui n'est pas un naturel
            B.menu.curseur = B.menu.items.length - 1;
            o.tape('KeyE', 2);
            t = T.enCours('blackjack');
            if (t.phase === 'joue') break;
        }
        const lignes = B.menu.items.map(function (i) { return i.libelle; }), argent = B.partie.argent;
        B.menu.curseur = lignes.indexOf('DOUBLER');
        o.tape('KeyE', 2);
        t = T.enCours('blackjack');
        return { lignes: lignes, argent: argent, apres: B.partie.argent, cartes: t.joueur.length, phase: t.phase,
                 double: t.double, gain: t.resultat.gain, mise: t.resultat.mise, nom: t.resultat.nom,
                 unite: T.miseDe('blackjack') };
    }""")
    assert r["lignes"] == ["TIRER", "RESTER", "DOUBLER"], r
    assert r["double"] and r["cartes"] == 3 and r["phase"] == "fin", r
    assert r["mise"] == 2 * r["unite"] and r["nom"].startswith("DOUBLÉ"), r
    assert r["apres"] == r["argent"] - r["unite"] + r["gain"], "la deuxième mise n'est pas prise ou le gain mal payé"
    assert r["gain"] in (0, 2 * r["unite"], 4 * r["unite"]), r


def test_la_securite_avertit_puis_reconduit_puis_barre(banc):
    """Miser 500 $ sur un sabot chaud (quatre par paquet), après des mains à 10 : l'œil s'allume, un garde vient à ton épaule et te
    glisse un mot. Trop chaud : à la mise suivante il t'arrête la main, te reconduit à la porte — sans une étoile
    — et le portier ne te rouvre que demain ; à la récidive, une semaine."""
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tables, C = L.Casino, vu = {};
        B.partie.argent = 1000000;
        B.partie.triches.machines = true;
        dedans(L, o, 'nord_casino', 'blackjack');
        o.frame(2);
        const g0 = C.garde();
        vu.garde = g0 ? { id: g0.id, tx: Math.floor(g0.x / 16), ty: Math.floor(g0.y / 16) } : null;
        o.tape('KeyE', 2);
        // Des mains à 10 $ jusqu'à un sabot chaud (compte par paquet de 4 et plus).
        T.etat().mise_bj = 10;
        for (let i = 0; i < 3000 && T.compteAvantLaMain() < 4; i++) { T.bjDonner(); T.bjRester(); if (T.sabot().pos >= T.regles().sabot.coupe) { T.bjDonner(); T.bjRester(); } }
        vu.tc = T.compteAvantLaMain();
        vu.chaleurAvant = C.dossier().chaleur;
        T.etat().mise_bj = 500;
        L.Hud.rafraichirMenu();
        B.menu.curseur = B.menu.items.length - 1;
        o.tape('KeyE', 2);                                       // DONNER, 500 $, au bouton
        vu.chaleur = C.dossier().chaleur; vu.averti = C.dossier().averti; vu.msg = B.msg;
        const g = C.garde();
        vu.gardeApres = g ? { d: Math.hypot(g.x - B.joueur.x, g.y - B.joueur.y), bulle: g.bulle && g.bulle.texte } : null;
        const t = T.enCours('blackjack');
        if (t.phase === 'joue') { B.menu.curseur = 1; o.tape('KeyE', 2); }
        // Trop chaud : la mise suivante, le garde t'arrête la main.
        C.dossier().chaleur = T.regles().surveillance.sortir;
        const argent = B.partie.argent, coups = T.compteur('blackjack').coups;
        B.menu.curseur = B.menu.items.length - 1;
        o.tape('KeyE', 2);
        vu.menuFerme = !B.menu; vu.pris = argent - B.partie.argent; vu.coups = T.compteur('blackjack').coups - coups;
        vu.msgSortie = B.msg;
        for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
        o.fondu();
        vu.dehors = !B.interieur; vu.etoiles = B.recherche.etoiles;
        vu.barre = C.dossier().barre - B.partie.jour;
        // Le portier refuse, au bouton.
        aLaPorte(L, o);
        o.frame(2);
        vu.invite = B.invite;
        o.tape('KeyE', 2);
        for (let k = 0; k < 60; k++) o.frame(1);
        vu.refuse = !B.interieur; vu.msgPorte = B.msg;
        // Le lendemain, on rentre.
        B.partie.jour += 1;
        aLaPorte(L, o);
        o.tape('KeyE', 2);
        for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
        o.fondu();
        vu.lendemain = !!B.interieur;
        // La récidive : une semaine.
        C.dossier().chaleur = T.regles().surveillance.sortir;
        T.bjDonner();
        for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
        o.fondu();
        vu.recidive = C.dossier().barre - B.partie.jour; vu.msgRecidive = B.msg;
        B.partie.jour += 3;
        aLaPorte(L, o);
        o.tape('KeyE', 2);
        for (let k = 0; k < 60; k++) o.frame(1);
        vu.troisJoursPlusTard = !B.interieur; vu.msgPorte3 = B.msg;
        return vu;
    }""")
    s = t.SURVEILLANCE
    assert r["garde"] and r["garde"]["id"] >= 1e9, f"pas de garde dans la salle, ou né dans la suite : {r['garde']}"
    assert r["tc"] >= 4 and r["chaleurAvant"] < s["avertir"] <= r["chaleur"], r
    assert r["averti"] and "À L’ŒIL" in r["msg"], r
    assert r["gardeApres"] and r["gardeApres"]["d"] < 30 and r["gardeApres"]["bulle"], r["gardeApres"]
    assert r["menuFerme"] and r["pris"] == 0 and r["coups"] == 0, "le garde a laissé passer la mise"
    assert "RECONDUIT" in r["msgSortie"], r["msgSortie"]
    assert r["dehors"] and r["etoiles"] == 0, "reconduit par la police ?"
    assert r["barre"] == 1 and r["refuse"] and "NE TE LAISSE PAS ENTRER" in r["msgPorte"], r
    assert r["invite"] == "LE PORTIER", f"l'invite promet d'entrer : {r['invite']}"
    assert r["lendemain"], "le portier ne rouvre pas le lendemain"
    assert r["recidive"] == s["barre_jours"] and "SEMAINE" in r["msgRecidive"], r
    assert r["troisJoursPlusTard"] and "ENCORE 4 JOURS" in r["msgPorte3"], r


def test_miser_toujours_pareil_ne_chauffe_pas_l_oeil(banc):
    """Cent mains à 500 $, toujours la même mise, au sabot : aucun garde ne se dérange (la chance, oui, se
    remarque un peu — jamais jusqu'à la porte)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, T = L.Tables, C = L.Casino;
        B.partie.argent = 10000000;
        B.partie.triches.machines = true;
        T.etat().mise_bj = 500;
        let max = 0, refus = 0;
        for (let i = 0; i < 100; i++) { if (!T.bjDonner()) refus++; T.bjRester(); max = Math.max(max, C.dossier().chaleur); }
        return { max: max, refus: refus, averti: C.dossier().averti };
    }""")
    assert r["refus"] == 0 and not r["averti"] and r["max"] < t.SURVEILLANCE["avertir"], r


def test_frapper_un_garde_barre_une_semaine_et_la_police_s_en_mele(banc):
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B, C = L.Casino;
        dedans(L, o, 'nord_casino', 'blackjack');
        o.frame(2);
        const g = C.garde();
        L.Entites.blesser(g, 10, B.joueur, { assomme: true });
        o.frame(2);
        return { barre: C.dossier().barre - B.partie.jour, etoiles: B.recherche.etoiles, msg: B.msg };
    }""")
    assert r["barre"] == t.SURVEILLANCE["barre_jours"] and r["etoiles"] >= 1 and "FRAPPÉ" in r["msg"], r


def test_la_triche_ne_touche_pas_au_hasard_du_jeu(banc):
    """Cent mains au sabot, un avertissement, une sortie : le tirage suivant du jeu est le même. Et le garde de
    la salle naît avec un dé prêté."""
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const B = L.B, T = L.Tables, C = L.Casino;
        L.graine(3);
        const temoin = [B.rng(), B.rng(), B.rng()];
        L.graine(3);
        B.partie.argent = 10000000;
        B.partie.triches.machines = true;
        for (let i = 0; i < 100; i++) {
            T.etat().mise_bj = T.compteAvantLaMain() >= 2 ? 500 : 10;
            T.bjDonner(); T.bjDoubler(); T.bjRester();
        }
        C.dossier().chaleur = 200; T.bjDonner();
        const apres = [B.rng(), B.rng(), B.rng()];
        C.dossier().barre = 0;                                   // reconduit : on repasse la porte quand même
        dedans(L, o, 'nord_casino', 'blackjack');
        L.Entites.retirer(C.garde());
        L.graine(9); const temoin2 = B.rng(); L.graine(9);
        C.maj();
        return { temoin: temoin, apres: apres, garde: !!C.garde(), temoin2: temoin2, apres2: B.rng() };
    }""")
    assert r["apres"] == r["temoin"], "tricher a décalé le hasard du jeu"
    assert r["garde"] and r["apres2"] == r["temoin2"], "la naissance du garde a tiré un dé du jeu"


def test_la_triche_machines_sans_limite_garde_le_sabot_et_l_oeil(banc):
    """MACHINES SANS LIMITE lève le plafond du jour, rien d'autre : au-delà de quarante mains, le sabot sert et se
    rebrasse comme avant, et l'œil voit toujours (trop chaud, la main est refusée)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, T = L.Tables, C = L.Casino;
        B.partie.argent = 1000000;
        B.partie.triches.machines = true;
        let ok = 0, suivies = 0;
        for (let i = 0; i < 90; i++) {
            const s = T.sabot(), n = s.n, pos = s.pos;
            if (T.bjDonner()) ok++;
            T.bjRester();
            const t = T.enCours('blackjack');
            if (t.sabot === (pos >= T.regles().sabot.coupe ? n + 1 : n) && T.sabot().pos === t.depart + t.joueur.length + t.croupier.length) suivies++;
        }
        C.dossier().chaleur = T.regles().surveillance.sortir;
        const refusee = !T.bjDonner();
        return { ok: ok, suivies: suivies, sabots: T.sabot().n, refusee: refusee, barre: C.barre() };
    }""")
    assert r["ok"] == 90 and r["suivies"] == 90 and r["sabots"] >= 4, r
    assert r["refusee"] and r["barre"], r


def test_au_hasard_du_navigateur_le_sabot_rend_moins_qu_on_y_met(banc):
    """Quarante mille mains au sabot, battu par le navigateur (la graine, le numéro du sabot, son sel) : l'habitué
    qui double, à mise égale, rend moins de cent pour cent, près de ce que Python mesure."""
    r = banc("function (L, o) {" + HABITUE + """
        L.Jeu.commencer();
        const T = L.Tables, h = habitue(T), d = double(T), coupe = T.regles().sabot.coupe;
        let n = 0, pos = 0, rendu = 0, pris = 0;
        for (let i = 0; i < 40000; i++) {
            if (pos >= coupe) { n++; pos = 0; }
            const m = T.bjMain(T.cartesDuSabot(n).slice(pos), h, d);
            rendu += m.paie; pris += m.fois; pos += m.joueur.length + m.croupier.length;
        }
        return { retour: rendu / pris, sabots: n };
    }""")
    assert r["retour"] < 1.0 and abs(r["retour"] - t.RETOURS["blackjack"]["main"] / 100 - 0.005) < 0.02, r
    assert r["sabots"] > 2000, r
