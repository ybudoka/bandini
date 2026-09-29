"""Les blocs de carte, JOUÉS : on prend la rue des Quais qui traverse jusqu'au bord ouest, la carte fait un
noir, le rang se charge (le chalet, le lac et la cabane), et on revient — à pied (vague 1), au volant et à deux, la police
reprenant au bord (vague 2). Voir `static/js/blocs.js`."""

import pytest

OUTILS = """
  const TT = 16;
  function passage(L) { return L.B.defs.blocs.find(function (b) { return b.slug === 'rang'; }).passage; }
  // Au passage du rang : la rue des Quais qui traverse jusqu'au bord OUEST (sa chaussée, y p.de + 1).
  function auPassage(L, o) {
    const j = L.B.joueur, p = passage(L);
    if (L.B.menu) L.Hud.fermerMenu();
    j.x = TT + 8; j.y = (p.de + 1) * TT + 8; L.Entites.indexer();
  }
  async function laisserArriver(L, o) { for (let i = 0; i < 6; i++) { o.frame(1); await o.attendre(); } }
  function pousser(L, o, touche, n) {
    o.touche(touche);
    let min = 1e9, max = -1e9, minX = 1e9;
    for (let i = 0; i < (n || 120); i++) {
      o.frame(1); min = Math.min(min, L.B.joueur.y); max = Math.max(max, L.B.joueur.y); minX = Math.min(minX, L.B.joueur.x);
      if (L.B.transition) break;
    }
    o.relacher(touche);
    for (let i = 0; i < 80; i++) o.frame(1);
    return { min: min, max: max, minX: minX };
  }
  async function entrer(L, o) {
    auPassage(L, o); await laisserArriver(L, o);
    pousser(L, o, 'KeyA');
  }
  // Le retour du rang : le chemin de gravier, au bord EST du bloc.
  function versLeRetour(L, o) {
    const r = L.B.bloc.def.bloc.retour, j = L.B.joueur;
    j.x = (L.Monde.carte.w - 2) * TT + 8; j.y = (r.de + 1) * TT + 8; L.Entites.indexer();
    pousser(L, o, 'KeyD');
  }
"""


def test_on_pousse_contre_le_bord_ouest_et_le_rang_se_charge_puis_on_revient(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        const ville = L.Monde.carte, y0 = j.y;
        pousser(L, o, 'KeyA');
        // Les gens de la ville, tels qu'ils ont été mis de côté AU PASSAGE (la ville vit
        // pendant qu'on marche : la comparer à avant, c'était juger les passants).
        // ⚠️ Seulement ce qui ne bouge pas tout seul : les passants naissent et s'oublient
        // pendant les images qui suivent le retour, les chars garés et le décor non.
        const gardes = B.bloc.ville.entites;
        const fixes = gardes.filter(function (e) { return e.type !== 'pieton' && e.type !== 'joueur' && (e.type !== 'vehicule' || e.etat === 'stationne'); });
        const dedans = { bloc: B.bloc && B.bloc.slug, w: L.Monde.carte.w, h: L.Monde.carte.h,
                         x: j.x, y: j.y, gps: L.Histoire.cible(), interieur: !!B.interieur,
                         entites: B.entites.length };
        versLeRetour(L, o);
        return { dedans: dedans, apres: { bloc: !!B.bloc, laVille: L.Monde.carte === ville,
                 memesGens: B.entites === gardes && fixes.length > 100 && fixes.every(function (e) { return B.entites.indexOf(e) >= 0; }),
                 dy: Math.round(j.y - y0), x: j.x } };
    }""")
    d = r["dedans"]
    assert d["bloc"] == "rang" and (d["w"], d["h"]) == (80, 50), d
    assert (d["x"], d["y"]) == (77 * 16 + 8, 24 * 16 + 8), "on apparaît à l'arrivée du bloc"
    assert d["interieur"] is False, "un bloc est DEHORS : ce n'est pas une pièce"
    assert d["gps"] and d["gps"]["nom"] == "Vers la ville", "la flèche vise la sortie"
    a = r["apres"]
    assert a["bloc"] is False and a["laVille"] and a["memesGens"], f"la ville revient telle qu'on l'a laissée : {a}"
    assert abs(a["dy"]) <= 16 and 6 < a["x"] < 24, f"on revient au passage d'où l'on était parti : {a}"


def test_longer_le_trottoir_ne_passe_pas_et_a_cote_du_passage_non_plus(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, p = passage(L);
        auPassage(L, o); await laisserArriver(L, o);
        // Le long du trottoir de ceinture de l'ouest, d'un bout à l'autre du passage.
        j.x = 8; j.y = (p.de - 3) * TT + 8; L.Entites.indexer();
        o.touche('KeyS'); for (let i = 0; i < 160; i++) o.frame(1); o.relacher('KeyS');
        const longe = !!B.bloc || !!B.transition;
        // Pousser contre le bord, mais à côté de l'ouverture.
        j.x = TT + 8; j.y = (p.de + p.l + 3) * TT + 8; L.Entites.indexer();
        const pousse = pousser(L, o, 'KeyA');
        return { longe: longe, acote: !!B.bloc, contre: pousse.minX };
    }""")
    assert r["longe"] is False, "longer le trottoir ne doit pas faire passer"
    assert r["contre"] <= 6 and r["acote"] is False, f"à côté de l'ouverture, le bord reste un bord : {r}"


VOLANT = """
  function auVolant(L, o, slug, cap) {
    const B = L.B, j = B.joueur, p = passage(L);
    // Sur la chaussée de la rue qui traverse, tourné vers l'ouest.
    const v = L.Vehicules.creer(slug, 5 * TT, (p.de + 2) * TT, cap === undefined ? Math.PI : cap, { etat: 'stationne' });
    j.x = v.x; j.y = v.y + 12; L.Entites.indexer();
    L.Vehicules.monter(j, v); L.Entites.indexer();
    return v;
  }
  function foncer(L, o, n) {
    o.touche('KeyW');
    for (let i = 0; i < (n || 200) && !L.B.transition; i++) o.frame(1);
    o.relacher('KeyW');
    for (let i = 0; i < 90; i++) o.frame(1);
  }
"""


@pytest.mark.parametrize("slug", ["auto", "camion", "moto", "velo"])
def test_au_volant_on_passe_avec_son_char_et_on_revient_avec_lui(banc, slug):
    """⚠️ Vague 2 : le char passe le bord, tourné vers l'intérieur du bloc, le joueur dedans ;
    et il revient avec lui, assez loin du bord pour ne pas repartir aussitôt."""
    r = banc("async function (L, o) {" + OUTILS + VOLANT + """
        L.Jeu.commencer(); L.B.partie.jour = 21;  // ⚠️ EN JUILLET : l'hiver, motos et vélos sont remisés (test_motos_velos_remises_js.py)
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        const v = auVolant(L, o, '""" + slug + """');
        const ville = B.entites;
        foncer(L, o);
        const dedans = { bloc: B.bloc && B.bloc.slug, dansLeBloc: B.entites.indexOf(v) >= 0, horsDeLaVille: ville.indexOf(v) < 0,
                         auVolant: j.dansVehicule === v, cap: Math.round(v.angle * 100) / 100, x: Math.round(v.x) };
        // Demi-tour vers le chemin de l'est, et on fonce — et on regarde OÙ le char revient,
        // à la première image en ville : posé en entier dans la carte, pas à moitié dehors.
        v.angle = 0; v.vitesse = 0; v.x = 70 * TT + 8; v.y = 25 * TT; j.x = v.x; j.y = v.y;
        o.touche('KeyW');
        for (let i = 0; i < 400 && B.bloc; i++) o.frame(1);
        o.relacher('KeyW');
        const xRetour = v.x, cap = Math.round(v.angle * 100) / 100;
        for (let i = 0; i < 120; i++) o.frame(1);
        return { dedans: dedans, apres: { bloc: !!B.bloc, enVille: B.entites.indexOf(v) >= 0 && B.entites === ville,
                 auVolant: j.dansVehicule === v, cap: cap, x: Math.round(xRetour),
                 demi: L.Vehicules.vehiculeDef(v.slug).longueur / 2 } };
    }""")
    d, a = r["dedans"], r["apres"]
    assert d["bloc"] == "rang" and d["dansLeBloc"] and d["horsDeLaVille"] and d["auVolant"], d
    assert abs(d["cap"]) == 3.14, f"le char arrive tourné vers l'intérieur du bloc : {d}"
    assert a["bloc"] is False and a["enVille"] and a["auVolant"], f"le char revient avec nous : {a}"
    assert a["x"] > a["demi"], f"revenu, le char dépasse du bord ouest de la ville : {a}"
    assert a["cap"] == 0, f"il revient tourné vers la ville : {a}"


def test_un_char_qui_longe_le_bord_ne_passe_pas(banc):
    r = banc("async function (L, o) {" + OUTILS + VOLANT + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, p = passage(L);
        auPassage(L, o); await laisserArriver(L, o);
        const v = auVolant(L, o, 'auto', Math.PI / 2);
        v.x = 8; v.y = (p.de - 4) * TT; j.x = v.x; j.y = v.y;
        foncer(L, o, 120);
        return { bloc: !!B.bloc, x: Math.round(v.x), y: Math.round(v.y / TT) };
    }""")
    assert r["bloc"] is False and r["x"] < 16, f"en longeant le trottoir, on est passé : {r}"


def test_ce_qui_est_dans_le_char_passe_avec_lui(banc):
    """Un client, un protégé de mission : tout ce qui est `dansVehicule` du char passe."""
    r = banc("async function (L, o) {" + OUTILS + VOLANT + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        const v = auVolant(L, o, 'auto');
        const c = L.Entites.creerPieton(v.x, v.y, L.Entites.archetype('passant'));
        c.dansVehicule = v; c.dessine = false;
        foncer(L, o);
        const dedans = { bloc: !!B.bloc, lui: B.entites.indexOf(c) >= 0, dansLeChar: c.dansVehicule === v };
        v.angle = 0; v.x = 70 * TT + 8; v.y = 25 * TT; j.x = v.x; j.y = v.y;
        foncer(L, o);
        return { dedans: dedans, revenu: !B.bloc && B.entites.indexOf(c) >= 0 && c.dansVehicule === v };
    }""")
    assert r["dedans"] == {"bloc": True, "lui": True, "dansLeChar": True}, r
    assert r["revenu"] is True


def test_a_deux_le_deuxieme_joueur_passe_aussi(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        L.Jeu.basculerCoop();
        const j2 = B.coop && B.coop.entite;
        auPassage(L, o); await laisserArriver(L, o);
        j2.x = j.x + 200; j2.y = j.y + 120;
        pousser(L, o, 'KeyA');
        const dedans = { bloc: !!B.bloc, j2: B.entites.indexOf(j2) >= 0, pres: Math.hypot(j2.x - j.x, j2.y - j.y) < 40 };
        versLeRetour(L, o);
        return { dedans: dedans, revenu: !B.bloc && B.entites.indexOf(j2) >= 0 && Math.hypot(j2.x - j.x, j2.y - j.y) < 60 };
    }""")
    assert r["dedans"] == {"bloc": True, "j2": True, "pres": True}, r
    assert r["revenu"] is True


def test_recherche_la_poursuite_reprend_au_bord(banc):
    """Les agents d'avant restent en ville ; ceux qui te suivent passent le MÊME bord,
    quelques secondes après toi — jamais d'un bosquet, jamais à tes pieds."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        B.recherche.etoiles = 2; B.recherche.chaleur = 60;
        const avant = L.Police.agents().slice();
        pousser(L, o, 'KeyA');
        const agents = function () { return B.entites.filter(function (e) { return e.agent; }); };
        const toutDeSuite = agents().length;
        const anciens = agents().filter(function (a) { return avant.indexOf(a) >= 0; }).length;
        for (let i = 0; i < L.Blocs.DELAI_POURSUIVANTS + 10; i++) o.frame(1);
        const bord = (L.Monde.carte.w - 1) * TT;
        const venus = agents().map(function (a) { return { x: Math.round(a.x), etat: a.etat }; });
        return { etoiles: B.recherche.etoiles, toutDeSuite: toutDeSuite, anciens: anciens, venus: venus, bord: bord };
    }""")
    assert r["etoiles"] == 2, "les étoiles passent le bord"
    assert r["toutDeSuite"] == 0 and r["anciens"] == 0, f"les agents d'avant ne suivent pas : {r}"
    assert len(r["venus"]) == 2, f"deux étoiles, deux poursuivants : {r}"
    assert all(v["x"] > r["bord"] - 4 * 16 for v in r["venus"]), f"ils arrivent par le bord : {r}"


def test_une_carte_pas_encore_arrivee_ne_noircit_pas_et_le_reseau_revenu_elle_passe(banc):
    """⚠️ Une carte ne peut pas arriver en retard : pousser avant, c'est pousser contre un
    bord. Et un réseau qui tombe une fois ne ferme pas le passage pour la partie."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        auPassage(L, o); await laisserArriver(L, o);
        const enPanne = { bloc: !!B.bloc, noir: !!B.transition, carte: !!L.Blocs.cartes.rang };
        pousser(L, o, 'KeyA', 40);
        const pousseEnPanne = !!B.bloc;
        const pendantLaPanne = o.fetchs.filter(function (f) { return String(f.url).indexOf('/api/carte/bloc/') === 0; }).length;
        // Le réseau revient : le délai passe, la carte arrive, on passe.
        for (let i = 0; i < L.Blocs.RELANCE; i++) { o.frame(1); if (i % 30 === 0) await o.attendre(); }
        auPassage(L, o); await laisserArriver(L, o);
        pousser(L, o, 'KeyA');
        return { enPanne: enPanne, pousseEnPanne: pousseEnPanne, pendantLaPanne: pendantLaPanne, apres: B.bloc && B.bloc.slug,
                 demandes: o.fetchs.filter(function (f) { return String(f.url).indexOf('/api/carte/bloc/') === 0; }).length };
    }""", blocs_panne=1)
    assert r["enPanne"] == {"bloc": False, "noir": False, "carte": False}, r
    assert r["pousseEnPanne"] is False
    assert r["pendantLaPanne"] == 1, f"un réseau mort redemandé à chaque image : {r['pendantLaPanne']} demandes"
    assert r["apres"] == "rang" and r["demandes"] == 2, r


@pytest.fixture(scope="module")
def au_rang_sans_bruit(banc):
    """UNE entrée au rang, quatre scènes qui ne le dérangent pas (vague C, 28 sept. 2026 — quatre
    bancs refaisaient la même entrée) : la plaque des deux côtés, la sauvegarde au rang, les arbres
    du bloc, puis personne n'y naît ; et le retour en ville, où les arbres reviennent.

    ⚠️ Entre deux scènes, le joueur est remis où chaque juge le prenait : à l'arrivée du bloc pour
    les quinze secondes où personne ne doit naître (les arbres l'avaient poussé contre la rangée
    de l'ouest)."""
    return banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        // 1. La plaque, en ville puis dans le bloc.
        auPassage(L, o); await laisserArriver(L, o);
        const enVille = L.Blocs.texteDInfo(j);
        j.y = 20 * TT; L.Entites.indexer();
        const loin = L.Blocs.texteDInfo(j);
        auPassage(L, o);
        pousser(L, o, 'KeyA');
        const arrivee = { x: j.x, y: j.y };
        const r0 = L.B.bloc.def.bloc.retour;
        j.x = (L.Monde.carte.w - 2) * TT + 8; j.y = (r0.de + 1) * TT + 8;
        const dansLeBloc = L.Blocs.texteDInfo(j);
        L.Jeu.rendre();
        const plaque = { enVille: enVille, loin: loin, dansLeBloc: dansLeBloc };
        // 2. Sauvegardée au rang.
        const retour = { x: B.bloc.ville.x, y: B.bloc.ville.y };
        L.Missions.sauvegarderPartie();
        const sauvee = { x: B.partie.x, y: B.partie.y, retour: retour, bloc: !!B.bloc };
        // 3. Les arbres du bloc — contre la rangée de l'ouest (rangée 30 : les tuiles 1 à 4
        // sont libres, l'arbre de la tuile 0 non) : on pousse vers la gauche, on reste au rang.
        const arbres = B.entites.filter(function (e) { return e.type === 'decor' && e.decor === 'arbre'; });
        j.x = 4 * TT + 8; j.y = 30 * TT + 8; L.Entites.indexer();
        o.touche('KeyA'); for (let i = 0; i < 90; i++) o.frame(1); o.relacher('KeyA');
        const bloque = j.x;
        // 4. Personne ne naît au rang : quinze secondes, le joueur remis à l'arrivée.
        j.x = arrivee.x; j.y = arrivee.y; L.Entites.indexer();
        for (let i = 0; i < 900; i++) o.frame(1);
        const pietons = B.entites.filter(function (e) { return e.type === 'pieton'; }).map(function (e) { return e.archetype || e.arch || '?'; });
        const auRang = B.bloc && B.bloc.slug;
        // 5. Le retour : les arbres de la ville reviennent.
        versLeRetour(L, o);
        const villeArbres = B.entites.filter(function (e) { return e.type === 'decor' && e.decor === 'arbre'; }).length;
        return { plaque: plaque, sauvee: sauvee, arbres: arbres.length, bloque: bloque, pietons: pietons,
                 auRang: auRang, villeArbres: villeArbres };
    }""")


def test_personne_ne_nait_au_rang(au_rang_sans_bruit):
    r = au_rang_sans_bruit
    assert r["auRang"] == "rang", f"le décor du juge est faux : on n'est plus au rang ({r['auRang']})"
    assert r["pietons"] == [], f"des passants de la ville dans les bois : {r['pietons']}"


@pytest.fixture(scope="module")
def au_rang_la_nuit_puis_arrete(banc):
    """UNE entrée au rang (vague C, 28 sept. 2026 — deux bancs) : le jour, la nuit et la police y
    tournent sans tomber ; puis arrêté, on se réveille au poste en ville.

    ⚠️ Entre les deux : zéro étoile, comme le juge de l'arrestation au départ — `prison` est
    appelée à la main, ce ne sont pas les agents de la nuit qui l'ont cueilli."""
    return banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        const ville = L.Monde.carte;
        await entrer(L, o);
        const dedans = !!B.bloc;
        for (let i = 0; i < 300; i++) o.frame(1);
        let h = B.partie.heure; for (let k = 0; k < 400 && !L.Monde.estNuit(h); k++) h = (h + 0.005) % 1; B.partie.heure = h;
        for (let i = 0; i < 300; i++) o.frame(1);
        B.recherche.etoiles = 2; B.recherche.chaleur = 50;
        for (let i = 0; i < 300; i++) o.frame(1);
        L.Jeu.rendre();
        L.Jeu.ouvrirCarte(); L.Jeu.rendre(); L.Jeu.fermerCarte();
        const nuit = { bloc: B.bloc && B.bloc.slug, etat: B.etat };
        B.recherche.etoiles = 0; B.recherche.chaleur = 0;
        L.Missions.prison(null);
        for (let i = 0; i < 400 && B.transition; i++) o.frame(1);
        if (B.menu) L.Hud.fermerMenu();
        const poste = ville.points.find(function (q) { return q.slug === 'poste'; });
        return { nuit: nuit, arrete: { dedans: dedans, bloc: !!B.bloc, laVille: L.Monde.carte === ville,
                 loin: Math.round(Math.hypot(j.x - (poste.x * TT + 8), j.y - (poste.y * TT + 20)) / TT) } };
    }""")


def test_jour_nuit_et_police_tournent_dans_le_bloc_sans_tomber(au_rang_la_nuit_puis_arrete):
    r = au_rang_la_nuit_puis_arrete["nuit"]
    assert r["bloc"] == "rang"


def test_arrete_au_rang_on_se_reveille_au_poste_en_ville(au_rang_la_nuit_puis_arrete):
    r = au_rang_la_nuit_puis_arrete["arrete"]
    assert r["dedans"] is True
    assert r["bloc"] is False and r["laVille"] is True, "on se réveille en ville, pas au rang"
    assert r["loin"] <= 4, f"au poste : {r}"


# ⚠️ « Tombé au rang, on se réveille à l'hôpital en ville » : `test_chalet_js.py::
# test_tombe_au_chalet_on_va_a_l_hopital_et_le_chalet_garde_le_char` (vague C) — tombé DANS le
# chalet, au rang, le réveil passe par le même `revenirEnVille` (la pièce, puis le bloc).


def test_sauvegardee_au_rang_la_partie_se_rouvre_au_passage_en_ville(au_rang_sans_bruit):
    r = au_rang_sans_bruit["sauvee"]
    assert r["bloc"] is True
    assert (r["x"], r["y"]) == (round(r["retour"]["x"]), round(r["retour"]["y"])), r


def test_les_arbres_du_bloc_sont_la_et_arretent_le_joueur(au_rang_sans_bruit, cartes_des_blocs):
    """Ses arbres sont des entités de décor, comme en ville — sinon on ne voyait que leurs
    pieds, et on marchait au travers."""
    r = au_rang_sans_bruit
    attendus = sum(1 for d in cartes_des_blocs["rang"]["decor"] if d["type"] == "arbre")
    assert r["arbres"] == attendus > 50, r
    # L'arbre de la tuile 0 arrête le joueur vers x = 12 ; sans lui, seul le bord de la
    # carte l'arrêterait, à son rayon (5 px).
    assert r["bloque"] > 10, f"on traverse les arbres : x = {r['bloque']}"
    assert r["villeArbres"] > 100, "de retour, les arbres de la ville sont revenus"


def test_une_plaque_dit_ou_pousser_des_deux_cotes(au_rang_sans_bruit):
    """Un passage qu'on ne voit pas, personne ne le trouve : une plaque au sol, et la ligne
    du bas qui dit où il mène et dans quel sens pousser."""
    r = au_rang_sans_bruit["plaque"]
    assert r["enVille"] == "LE RANG : POUSSE VERS L'OUEST", r
    assert r["loin"] is None
    assert r["dansLeBloc"] == "VERS LA VILLE : POUSSE VERS L'EST", r
