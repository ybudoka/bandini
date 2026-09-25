"""Les blocs de carte, JOUÉS : on pousse contre le bord nord des Érables, la carte fait un noir,
la clairière se charge, et on revient — à pied (vague 1), au volant et à deux, la police
reprenant au bord (vague 2). Voir `static/js/blocs.js`."""

import pytest

OUTILS = """
  const TT = 16;
  function passage(L) { return L.B.defs.blocs.find(function (b) { return b.slug === 'clairiere'; }).passage; }
  function auPassage(L, o) {
    const j = L.B.joueur, p = passage(L);
    if (L.B.menu) L.Hud.fermerMenu();
    j.x = (p.de + 2) * TT + 8; j.y = TT + 8; L.Entites.indexer();
  }
  async function laisserArriver(L, o) { for (let i = 0; i < 6; i++) { o.frame(1); await o.attendre(); } }
  function pousser(L, o, touche, n) {
    o.touche(touche);
    let min = 1e9, max = -1e9;
    for (let i = 0; i < (n || 120); i++) { o.frame(1); min = Math.min(min, L.B.joueur.y); max = Math.max(max, L.B.joueur.y); if (L.B.transition) break; }
    o.relacher(touche);
    for (let i = 0; i < 80; i++) o.frame(1);
    return { min: min, max: max };
  }
  async function entrer(L, o) {
    auPassage(L, o); await laisserArriver(L, o);
    pousser(L, o, 'KeyW');
  }
  function versLeRetour(L, o) {
    const r = L.B.bloc.def.bloc.retour, j = L.B.joueur;
    j.x = (r.de + 1) * TT + 8; j.y = (L.Monde.carte.h - 2) * TT + 8; L.Entites.indexer();
    pousser(L, o, 'KeyS');
  }
"""


def test_on_pousse_contre_le_bord_nord_et_la_clairiere_se_charge_puis_on_revient(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        const ville = L.Monde.carte, x0 = j.x;
        pousser(L, o, 'KeyW');
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
                 dx: Math.round(j.x - x0), y: j.y } };
    }""")
    d = r["dedans"]
    assert d["bloc"] == "clairiere" and (d["w"], d["h"]) == (40, 26), d
    assert (d["x"], d["y"]) == (20 * 16 + 8, 22 * 16 + 8), "on apparaît à l'arrivée du bloc"
    assert d["interieur"] is False, "un bloc est DEHORS : ce n'est pas une pièce"
    assert d["gps"] and d["gps"]["nom"] == "Vers la ville", "la flèche vise la sortie"
    a = r["apres"]
    assert a["bloc"] is False and a["laVille"] and a["memesGens"], f"la ville revient telle qu'on l'a laissée : {a}"
    assert abs(a["dx"]) <= 16 and 6 < a["y"] < 24, f"on revient au passage d'où l'on était parti : {a}"


def test_longer_le_trottoir_ne_passe_pas_et_a_cote_du_passage_non_plus(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, p = passage(L);
        auPassage(L, o); await laisserArriver(L, o);
        // Le long du trottoir de ceinture, d'un bout à l'autre du passage.
        j.x = (p.de - 3) * TT + 8; j.y = 8; L.Entites.indexer();
        o.touche('KeyD'); for (let i = 0; i < 160; i++) o.frame(1); o.relacher('KeyD');
        const longe = !!B.bloc || !!B.transition;
        // Pousser contre le bord, mais à côté de l'ouverture.
        j.x = (p.de + p.l + 3) * TT + 8; j.y = TT + 8; L.Entites.indexer();
        const pousse = pousser(L, o, 'KeyW');
        return { longe: longe, acote: !!B.bloc, contre: pousse.min };
    }""")
    assert r["longe"] is False, "longer le trottoir ne doit pas faire passer"
    assert r["contre"] <= 6 and r["acote"] is False, f"à côté de l'ouverture, le bord reste un bord : {r}"


VOLANT = """
  function auVolant(L, o, slug, cap) {
    const B = L.B, j = B.joueur, p = passage(L);
    const v = L.Vehicules.creer(slug, (p.de + 2) * TT + 8, 4 * TT, cap === undefined ? -Math.PI / 2 : cap, { etat: 'stationne' });
    j.x = v.x + 12; j.y = v.y; L.Entites.indexer();
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
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        const v = auVolant(L, o, '""" + slug + """');
        const ville = B.entites;
        foncer(L, o);
        const dedans = { bloc: B.bloc && B.bloc.slug, dansLeBloc: B.entites.indexOf(v) >= 0, horsDeLaVille: ville.indexOf(v) < 0,
                         auVolant: j.dansVehicule === v, cap: Math.round(v.angle * 100) / 100, y: Math.round(v.y) };
        // Demi-tour vers le chemin du sud, et on fonce — et on regarde OÙ le char revient,
        // à la première image en ville : posé en entier dans la carte, pas à moitié dehors.
        v.angle = Math.PI / 2; v.vitesse = 0; v.x = 20 * TT + 8; v.y = 20 * TT; j.x = v.x; j.y = v.y;
        o.touche('KeyW');
        for (let i = 0; i < 400 && B.bloc; i++) o.frame(1);
        o.relacher('KeyW');
        const yRetour = v.y, cap = Math.round(v.angle * 100) / 100;
        for (let i = 0; i < 120; i++) o.frame(1);
        return { dedans: dedans, apres: { bloc: !!B.bloc, enVille: B.entites.indexOf(v) >= 0 && B.entites === ville,
                 auVolant: j.dansVehicule === v, cap: cap, y: Math.round(yRetour),
                 demi: L.Vehicules.vehiculeDef(v.slug).longueur / 2 } };
    }""")
    d, a = r["dedans"], r["apres"]
    assert d["bloc"] == "clairiere" and d["dansLeBloc"] and d["horsDeLaVille"] and d["auVolant"], d
    assert d["cap"] == -1.57, f"le char arrive tourné vers l'intérieur du bloc : {d}"
    assert a["bloc"] is False and a["enVille"] and a["auVolant"], f"le char revient avec nous : {a}"
    assert a["y"] > a["demi"], f"revenu, le char dépasse du bord nord de la ville : {a}"
    assert a["cap"] == 1.57, f"il revient tourné vers la ville : {a}"


def test_un_char_qui_longe_le_bord_ne_passe_pas(banc):
    r = banc("async function (L, o) {" + OUTILS + VOLANT + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, p = passage(L);
        auPassage(L, o); await laisserArriver(L, o);
        const v = auVolant(L, o, 'auto', 0);
        v.x = (p.de - 4) * TT; v.y = 8; j.x = v.x; j.y = v.y;
        foncer(L, o, 120);
        return { bloc: !!B.bloc, x: Math.round(v.x / TT), y: Math.round(v.y) };
    }""")
    assert r["bloc"] is False and r["y"] < 16, f"en longeant le trottoir, on est passé : {r}"


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
        v.angle = Math.PI / 2; v.x = 20 * TT + 8; v.y = 20 * TT; j.x = v.x; j.y = v.y;
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
        pousser(L, o, 'KeyW');
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
        pousser(L, o, 'KeyW');
        const agents = function () { return B.entites.filter(function (e) { return e.agent; }); };
        const toutDeSuite = agents().length;
        const anciens = agents().filter(function (a) { return avant.indexOf(a) >= 0; }).length;
        for (let i = 0; i < L.Blocs.DELAI_POURSUIVANTS + 10; i++) o.frame(1);
        const bord = (L.Monde.carte.h - 1) * TT;
        const venus = agents().map(function (a) { return { y: Math.round(a.y), etat: a.etat }; });
        return { etoiles: B.recherche.etoiles, toutDeSuite: toutDeSuite, anciens: anciens, venus: venus, bord: bord };
    }""")
    assert r["etoiles"] == 2, "les étoiles passent le bord"
    assert r["toutDeSuite"] == 0 and r["anciens"] == 0, f"les agents d'avant ne suivent pas : {r}"
    assert len(r["venus"]) == 2, f"deux étoiles, deux poursuivants : {r}"
    assert all(v["y"] > r["bord"] - 4 * 16 for v in r["venus"]), f"ils arrivent par le bord : {r}"


def test_une_carte_pas_encore_arrivee_ne_noircit_pas_et_le_reseau_revenu_elle_passe(banc):
    """⚠️ Une carte ne peut pas arriver en retard : pousser avant, c'est pousser contre un
    bord. Et un réseau qui tombe une fois ne ferme pas le passage pour la partie."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        auPassage(L, o); await laisserArriver(L, o);
        const enPanne = { bloc: !!B.bloc, noir: !!B.transition, carte: !!L.Blocs.cartes.clairiere };
        pousser(L, o, 'KeyW', 40);
        const pousseEnPanne = !!B.bloc;
        const pendantLaPanne = o.fetchs.filter(function (f) { return String(f.url).indexOf('/api/carte/bloc/') === 0; }).length;
        // Le réseau revient : le délai passe, la carte arrive, on passe.
        for (let i = 0; i < L.Blocs.RELANCE; i++) { o.frame(1); if (i % 30 === 0) await o.attendre(); }
        auPassage(L, o); await laisserArriver(L, o);
        pousser(L, o, 'KeyW');
        return { enPanne: enPanne, pousseEnPanne: pousseEnPanne, pendantLaPanne: pendantLaPanne, apres: B.bloc && B.bloc.slug,
                 demandes: o.fetchs.filter(function (f) { return String(f.url).indexOf('/api/carte/bloc/') === 0; }).length };
    }""", blocs_panne=1)
    assert r["enPanne"] == {"bloc": False, "noir": False, "carte": False}, r
    assert r["pousseEnPanne"] is False
    assert r["pendantLaPanne"] == 1, f"un réseau mort redemandé à chaque image : {r['pendantLaPanne']} demandes"
    assert r["apres"] == "clairiere" and r["demandes"] == 2, r


def test_personne_ne_nait_dans_la_clairiere(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        await entrer(L, o);
        for (let i = 0; i < 900; i++) o.frame(1);
        return B.entites.filter(function (e) { return e.type === 'pieton'; }).map(function (e) { return e.archetype || e.arch || '?'; });
    }""")
    assert r == [], f"des passants de la ville dans les bois : {r}"


def test_jour_nuit_et_police_tournent_dans_le_bloc_sans_tomber(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B;
        await entrer(L, o);
        for (let i = 0; i < 300; i++) o.frame(1);
        let h = B.partie.heure; for (let k = 0; k < 400 && !L.Monde.estNuit(h); k++) h = (h + 0.005) % 1; B.partie.heure = h;
        for (let i = 0; i < 300; i++) o.frame(1);
        B.recherche.etoiles = 2; B.recherche.chaleur = 50;
        for (let i = 0; i < 300; i++) o.frame(1);
        L.Jeu.rendre();
        L.Jeu.ouvrirCarte(); L.Jeu.rendre(); L.Jeu.fermerCarte();
        return { bloc: B.bloc && B.bloc.slug, etat: B.etat };
    }""")
    assert r["bloc"] == "clairiere"


def test_arrete_dans_la_clairiere_on_se_reveille_au_poste_en_ville(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        const ville = L.Monde.carte;
        pousser(L, o, 'KeyW');
        const dedans = !!B.bloc;
        L.Missions.prison(null);
        for (let i = 0; i < 400 && B.transition; i++) o.frame(1);
        if (B.menu) L.Hud.fermerMenu();
        const poste = ville.points.find(function (q) { return q.slug === 'poste'; });
        return { dedans: dedans, bloc: !!B.bloc, laVille: L.Monde.carte === ville,
                 loin: Math.round(Math.hypot(j.x - (poste.x * TT + 8), j.y - (poste.y * TT + 20)) / TT) };
    }""")
    assert r["dedans"] is True
    assert r["bloc"] is False and r["laVille"] is True, "on se réveille en ville, pas dans la clairière"
    assert r["loin"] <= 4, f"au poste : {r}"


def test_tombe_dans_la_clairiere_on_se_reveille_a_l_hopital_en_ville(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        const ville = L.Monde.carte;
        pousser(L, o, 'KeyW');
        const dedans = !!B.bloc;
        L.Missions.hopital('test');
        for (let i = 0; i < 400 && B.transition; i++) o.frame(1);
        return { dedans: dedans, bloc: !!B.bloc, piece: B.interieur && B.interieur.slug,
                 laVille: (B.exterieur && B.exterieur.carte) === ville };
    }""")
    assert r["dedans"] is True
    assert r == {"dedans": True, "bloc": False, "piece": "hopital", "laVille": True}, r


def test_sauvegardee_dans_la_clairiere_la_partie_se_rouvre_au_passage_en_ville(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        pousser(L, o, 'KeyW');
        const retour = { x: B.bloc.ville.x, y: B.bloc.ville.y };
        L.Missions.sauvegarderPartie();
        return { x: B.partie.x, y: B.partie.y, retour: retour, bloc: !!B.bloc };
    }""")
    assert r["bloc"] is True
    assert (r["x"], r["y"]) == (round(r["retour"]["x"]), round(r["retour"]["y"])), r


def test_les_arbres_du_bloc_sont_la_et_arretent_le_joueur(banc, cartes_des_blocs):
    """Ses arbres sont des entités de décor, comme en ville — sinon on ne voyait que leurs
    pieds, et on marchait au travers."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        await entrer(L, o);
        const arbres = B.entites.filter(function (e) { return e.type === 'decor' && e.decor === 'arbre'; });
        // Contre la rangée d'arbres de l'ouest : on pousse vers la gauche, on reste dans la clairière.
        j.x = 4 * TT + 8; j.y = 16 * TT + 8; L.Entites.indexer();
        o.touche('KeyA'); for (let i = 0; i < 90; i++) o.frame(1); o.relacher('KeyA');
        const bloque = j.x;
        versLeRetour(L, o);
        const ville = B.entites.filter(function (e) { return e.type === 'decor' && e.decor === 'arbre'; }).length;
        return { arbres: arbres.length, bloque: bloque, villeArbres: ville };
    }""")
    attendus = sum(1 for d in cartes_des_blocs["clairiere"]["decor"] if d["type"] == "arbre")
    assert r["arbres"] == attendus > 50, r
    # L'arbre de la tuile 0 arrête le joueur vers x = 12 ; sans lui, seul le bord de la
    # carte l'arrêterait, à son rayon (5 px).
    assert r["bloque"] > 10, f"on traverse les arbres : x = {r['bloque']}"
    assert r["villeArbres"] > 100, "de retour, les arbres de la ville sont revenus"


def test_une_plaque_dit_ou_pousser_des_deux_cotes(banc):
    """Un passage qu'on ne voit pas, personne ne le trouve : une plaque au sol, et la ligne
    du bas qui dit où il mène et dans quel sens pousser."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        const enVille = L.Blocs.texteDInfo(j);
        j.y = 20 * TT; L.Entites.indexer();
        const loin = L.Blocs.texteDInfo(j);
        auPassage(L, o);
        pousser(L, o, 'KeyW');
        j.x = 20 * TT + 8; j.y = (L.Monde.carte.h - 2) * TT + 8;
        const dansLeBloc = L.Blocs.texteDInfo(j);
        L.Jeu.rendre();
        return { enVille: enVille, loin: loin, dansLeBloc: dansLeBloc };
    }""")
    assert r["enVille"] == "LA CLAIRIÈRE DU LAC : POUSSE VERS LE NORD", r
    assert r["loin"] is None
    assert r["dansLeBloc"] == "VERS LA VILLE : POUSSE VERS LE SUD", r
