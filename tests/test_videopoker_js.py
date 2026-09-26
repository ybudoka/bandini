"""Le vidéopoker du Brouillard, JOUÉ au banc (docs/jalons/le-videopoker-du-brouillard.md).

Les règles vivent dans `app/videopoker.py` (et `test_videopoker.py` les juge) ; ici, la machine
qu'on touche : au bar et au dépanneur, au bouton ACTION ; une main qui se donne, se garde et se tire ;
son hasard qui n'est pas celui du jeu ; la table affichée qui est celle qui paie ; et, sur dix mille
mains, une machine qui rend moins qu'on y met.
"""

import json
import random

from app import videopoker as vp

#: Entrer dans une pièce et se planter devant son point, comme un joueur.
DEDANS = """
  function dedans(L, o, lieu, point) {
    const B = L.B, j = B.joueur, M = L.Monde;
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    const pt = B.interieur.points.find(function (q) { return q.type === point; });
    j.x = pt.x * 16 + 8; j.y = (pt.y + 1) * 16 + 8; j.angle = -Math.PI / 2; L.Entites.indexer();
    o.frame(2);
    return pt;
  }
"""

#: La stratégie de l'habitué (le jumeau de `test_videopoker.garder`), en JS.
HABITUE = """
  function garder(V, main) {
    const tout = [0, 1, 2, 3, 4];
    if (V.gainDuVideopoker(main) >= 20) return tout;                 // quinte ou mieux (4 × 5 $)
    const rangs = main.map(function (c) { return c % 13; }), coul = main.map(function (c) { return Math.floor(c / 13); });
    const compte = {};
    rangs.forEach(function (r) { compte[r] = (compte[r] || 0) + 1; });
    for (let s = 0; s < 4; s++) {
      const hauts = tout.filter(function (i) { return coul[i] === s && rangs[i] >= 8; });
      if (hauts.length >= 4) return hauts.slice(0, 4);
    }
    if (V.gainDuVideopoker(main) >= 5) return tout.filter(function (i) { return compte[rangs[i]] >= 2; });
    for (let s = 0; s < 4; s++) {
      const idx = tout.filter(function (i) { return coul[i] === s; });
      if (idx.length === 4) return idx;
    }
    if (Object.keys(compte).some(function (r) { return compte[r] === 2; })) return tout.filter(function (i) { return compte[rangs[i]] === 2; });
    for (let bas = 0; bas < 10; bas++) {
      const vus = {}, garde = [];
      tout.forEach(function (i) { if (rangs[i] >= bas && rangs[i] < bas + 5 && !vus[rangs[i]]) { vus[rangs[i]] = 1; garde.push(i); } });
      if (garde.length === 4) return garde;
    }
    return tout.filter(function (i) { return rangs[i] >= 9; }).sort(function (a, b) { return rangs[a] - rangs[b]; }).slice(0, 2);
  }
"""


def test_la_machine_est_au_bar_et_au_depanneur_et_s_ouvre_au_bouton(banc):
    """Au Brouillard et chez Ti-Paul : l'invite dit LE VIDÉOPOKER, ACTION ouvre la machine,
    DONNER prend la mise et donne cinq cartes — le menu reste ouvert (on quitte par B ou Échap)."""
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        const out = {};
        for (const lieu of ['bar', 'depanneur']) {
            L.B.partie.argent = 100;
            dedans(L, o, lieu, 'videopoker');
            const invite = L.B.invite;
            o.tape('KeyE', 2);
            const menu = L.B.menu;
            const vu = { invite: invite, titre: menu && menu.titre, aide: menu && menu.aide,
                         premiere: menu && menu.items[0].libelle };
            menu.curseur = 0;
            o.tape('KeyE', 2);
            vu.reste = L.B.menu === menu;
            vu.argent = L.B.partie.argent;
            vu.lignes = L.B.menu ? L.B.menu.items.map(function (q) { return q.libelle + '|' + (q.detail || ''); }) : null;
            L.Hud.fermerMenu(); L.B.videopoker = null;
            L.Jeu.sortir(); o.fondu();
            for (let k = 0; k < 200 && L.B.interieur; k++) o.frame(1);
            out[lieu] = vu;
        }
        return out;
    }""")
    for lieu, vu in r.items():
        assert vu["invite"] == "LE VIDÉOPOKER", (lieu, vu)
        assert vu["titre"] == "VIDÉOPOKER" and vu["premiere"] == "DONNER", (lieu, vu)
        assert f"RETOUR {vp.RETOUR_AFFICHE} %" in vu["aide"], (lieu, vu)
        assert vu["reste"], f"{lieu} : DONNER a refermé la machine"
        assert vu["argent"] == 100 - vp.MISE, (lieu, vu)
        assert len(vu["lignes"]) == 6 and vu["lignes"][-1] == "TIRER|", (lieu, vu)
        assert all(ligne.endswith("|JETER") for ligne in vu["lignes"][:5]), (lieu, vu)


def test_une_main_se_garde_se_tire_et_paie_selon_la_table(banc):
    """Garder deux cartes, tirer : les trois autres changent, les deux gardées restent ; la main
    paie ce que dit la table affichée (`B.defs.videopoker.gains`), et rien d'autre."""
    r = banc("function (L, o) {" + """
        L.Jeu.commencer();
        const V = L.Missions, B = L.B;
        B.partie.argent = 1000;
        V.donnerAuVideopoker();
        const avant = B.videopoker.cartes.slice();
        B.videopoker.gardes = [true, false, true, false, false];
        const argent = B.partie.argent;
        V.tirerAuVideopoker();
        const apres = B.videopoker.cartes.slice();
        return { avant: avant, apres: apres, resultat: B.videopoker.resultat, gagne: B.partie.argent - argent,
                 attendu: V.gainDuVideopoker(apres), phase: B.videopoker.phase };
    }""")
    assert r["apres"][0] == r["avant"][0] and r["apres"][2] == r["avant"][2]
    assert all(r["apres"][i] != r["avant"][i] for i in (1, 3, 4)), r
    assert len(set(r["apres"])) == 5, "une carte en double : le paquet est mal battu"
    assert r["gagne"] == r["attendu"] == vp.paie(r["apres"]) * vp.MISE, r
    assert r["phase"] == "mise"


def test_la_table_affichee_est_celle_qui_paie_et_l_evaluation_est_celle_de_python(banc):
    """Deux mille mains au hasard, évaluées des deux côtés : le navigateur et Python disent la même
    main, et la paient pareil. Et la table que la machine AFFICHE est celle du paquet."""
    rng = random.Random(11)
    mains = [rng.sample(range(52), 5) for _ in range(2000)]
    # Une main de chaque sorte, pour que la table entière soit essayée (le hasard n'en donne pas).
    mains += [[47, 48, 49, 50, 51], [3, 4, 5, 6, 7], [5, 18, 31, 44, 0], [5, 18, 31, 0, 13],
              [0, 3, 7, 9, 12], [0, 14, 2, 3, 4], [2, 15, 28, 7, 0], [2, 15, 7, 20, 0], [9, 22, 7, 1, 0]]
    r = banc("function (L, o) {" + """
        L.Jeu.commencer();
        const mains = """ + json.dumps(mains) + """;
        return { mains: mains.map(function (m) { return [L.Missions.evaluerMain(m), L.Missions.gainDuVideopoker(m)]; }),
                 gains: L.B.defs.videopoker.gains, mise: L.B.defs.videopoker.mise };
    }""")
    for main, (slug, gain) in zip(mains, r["mains"]):
        assert slug == vp.evaluer(main), (main, slug)
        assert gain == vp.paie(main) * vp.MISE, (main, gain)
    assert r["gains"] == vp.GAINS and r["mise"] == vp.MISE
    assert {s for s, _ in r["mains"]} >= {g["slug"] for g in vp.GAINS}, "une ligne de la table n'a jamais été essayée"


def test_jouer_ne_touche_pas_au_hasard_du_jeu(banc):
    """⚠️ La règle du plan : les cartes ne se tirent PAS à `B.rng()`. Cent mains jouées entre deux
    tirages ne changent pas le tirage suivant — et la même main revient au même numéro."""
    r = banc("function (L, o) {" + """
        L.Jeu.commencer();
        const B = L.B, V = L.Missions;
        L.graine(3);
        const temoin = [B.rng(), B.rng(), B.rng()];
        L.graine(3);
        B.partie.argent = 100000;
        for (let i = 0; i < 100; i++) {
            B.partie.videopoker = B.partie.videopoker || null;
            if (B.partie.videopoker) B.partie.videopoker.mains = 0;
            V.donnerAuVideopoker();
            B.videopoker.gardes = [true, true, false, false, false];
            V.tirerAuVideopoker();
        }
        const apres = [B.rng(), B.rng(), B.rng()];
        return { temoin: temoin, apres: apres, meme: V.paquetDuVideopoker(7).join() === V.paquetDuVideopoker(7).join(),
                 autre: V.paquetDuVideopoker(7).join() !== V.paquetDuVideopoker(8).join() };
    }""")
    assert r["apres"] == r["temoin"], "jouer au vidéopoker a décalé le hasard du jeu"
    assert r["meme"] and r["autre"]


def test_dix_mille_mains_rendent_moins_qu_on_y_met(banc):
    """Dix mille mains jouées par l'habitué, dans la vraie machine (sa mise, son paquet, sa table) :
    elle rend moins qu'on y met, à trois points de ce qu'elle affiche."""
    r = banc("function (L, o) {" + HABITUE + """
        L.Jeu.commencer();
        const B = L.B, V = L.Missions;
        B.partie.argent = 1000000;
        const depart = B.partie.argent;
        const n = 10000;
        for (let i = 0; i < n; i++) {
            if (B.partie.videopoker) B.partie.videopoker.mains = 0;
            V.donnerAuVideopoker();
            const garde = garder(V, B.videopoker.cartes);
            B.videopoker.gardes = [0, 1, 2, 3, 4].map(function (k) { return garde.indexOf(k) >= 0; });
            V.tirerAuVideopoker();
        }
        return { mis: n * B.defs.videopoker.mise, rendu: B.partie.argent - depart + n * B.defs.videopoker.mise };
    }""")
    retour = r["rendu"] / r["mis"] * 100
    assert retour < 100, f"la machine rend {retour:.1f} % sur dix mille mains"
    assert abs(retour - vp.RETOUR_AFFICHE) <= 3, f"elle affiche {vp.RETOUR_AFFICHE} % et rend {retour:.1f} %"


def test_la_machine_a_assez_mange_pour_aujourd_hui(banc):
    """`MAINS_PAR_JOUR`, toutes machines comprises : au-delà, DONNER s'éteint ; le lendemain, il
    revient."""
    r = banc("function (L, o) {" + """
        L.Jeu.commencer();
        const B = L.B, V = L.Missions, n = B.defs.videopoker.mains_par_jour;
        B.partie.argent = 100000;
        let donnees = 0;
        for (let i = 0; i < n + 5; i++) { if (V.donnerAuVideopoker()) { donnees++; V.tirerAuVideopoker(); } }
        const eteint = V.menuVideopoker().items[0].actif;
        B.partie.jour++;
        const lendemain = V.menuVideopoker().items[0].actif;
        return { donnees: donnees, n: n, eteint: eteint, lendemain: lendemain };
    }""")
    assert r["donnees"] == r["n"] == vp.MAINS_PAR_JOUR, r
    assert r["eteint"] is False and r["lendemain"] is True, r
