"""Le son de l'eau — entrer, nager, sortir, couler.

_Demande de Martin (14 sept. 2026) :_ « améliore le son de quand on va dans
l'eau. » Il n'y avait rien a ameliorer : l'entree dans la baie jouait `choc` —
« Tole froissee », le son d'un ACCIDENT DE CHAR — et le reste etait du silence.
`majJoueur` coupe les pas dans l'eau et ne mettait rien a la place ; la noyade,
la sortie de l'eau et le char qui coule ne faisaient aucun bruit du tout.

⚠️ Ces juges lisent les APPELS (`Son.SFX.x`, `Son.jouerA`), pas les octets : ce
qui est en cause ici, c'est le cablage — quel son a quel moment. La qualite des
fichiers, elle, se juge dans `test_audio.py`, et l'oreille de Martin decide du
reste.
"""

import pytest

#: Une rive avec neuf tuiles d'eau plein est, sur trois rangees.
#: ⚠️ Trois rangees et pas une : sur un filet d'une tuile de haut, un corps
#: longe la berge au sec et le juge mesure quelqu'un qui contourne.
RIVE = """
        let rive = null;
        for (let y = 4; y < c.h - 4 && !rive; y++) {
            for (let x = 4; x < c.w - 10; x++) {
                if (!L.Monde.marchablePieton(x, y) || L.Monde.estEau(x, y)) continue;
                let eau = true;
                for (let k = 1; k <= 9; k++) {
                    for (const dy of [-1, 0, 1]) if (!L.Monde.estEau(x + k, y + dy)) eau = false;
                }
                if (eau) { rive = { x: x, y: y }; break; }
            }
        }
        if (!rive) throw new Error('aucune rive : la carte n\\'a plus d\\'eau ?');
"""

#: On note ce qui SONNE, dans l'ordre. `SFX` pour les sons du joueur (ils ont
#: leur filet synthetise), `jouerA` pour ceux qui sont poses dans le monde.
ESPION = """
        const sons = [];
        ['plongeon', 'nage', 'couler', 'char_a_l_eau', 'choc', 'pas'].forEach(function (nom) {
            const vrai = L.Son.SFX[nom];
            L.Son.SFX[nom] = function () { sons.push(nom); return vrai.apply(null, arguments); };
        });
        const vraiJouerA = L.Son.jouerA;
        L.Son.jouerA = function (slug) { sons.push('a:' + slug); return vraiJouerA.apply(null, arguments); };
"""


@pytest.fixture
def eau(banc):
    """Fait tourner `corps` avec le joueur pose sur une rive, et l'espion en place."""
    def lancer(corps):
        return banc("""function (L, o) {
            L.Jeu.commencer();
            L.graine(31);
            const j = L.B.joueur, c = L.Monde.carte, TT = L.TT, out = {};
            """ + RIVE + ESPION + """
            j.x = rive.x * TT + 8; j.y = rive.y * TT + 8;
            L.Monde.centrerCamera(j.x, j.y);
            j.endurance = 100; j.surplus = 0; j.cafeine = 0;
            (""" + corps + """)(L, o, j, rive, TT, sons, out);
            return out;
        }""")
    return lancer


def test_entrer_dans_l_eau_joue_un_plongeon_et_plus_jamais_de_tole(eau):
    """⚠️ LE juge de cette demande. Il est rouge sur le code d'avant : c'est
    `SFX.choc` que `majJoueur` appelait, le froissement de carrosserie de deux
    chars qui se rentrent dedans."""
    r = eau("""function (L, o, j, rive, TT, sons, out) {
        o.touche('KeyD');
        let entre = -1;
        for (let i = 0; i < 180 && entre < 0; i++) { o.frame(1); if (j.nage) entre = i; }
        o.relacher('KeyD');
        out.entre = entre >= 0;
        out.sons = sons.slice(0, 4);
    }""")
    assert r["entre"] is True, "on n'entre pas dans l'eau : le juge ne prouve rien"
    assert "plongeon" in r["sons"], f"entrer dans l'eau ne fait pas de plongeon : {r['sons']}"
    assert "choc" not in r["sons"], f"c'est encore la tôle froissée d'un accident de char : {r['sons']}"


def test_nager_fait_des_brassees_et_aucun_pas(eau):
    """On ne fait pas de pas dans l'eau — mais le silence n'est pas la reponse.

    ⚠️ Le souffle est remis a 100 a chaque image : sans ca le nageur coule au
    bout de deux secondes et le juge mesure une noyade, pas une nage."""
    r = eau("""function (L, o, j, rive, TT, sons, out) {
        o.touche('KeyD');
        for (let i = 0; i < 30; i++) o.frame(1);       // on entre
        const depart = sons.length;
        const x0 = j.x;
        for (let i = 0; i < 180; i++) { j.endurance = 100; o.frame(1); }
        o.relacher('KeyD');
        const pendant = sons.slice(depart);
        out.nage = !!j.nage;
        out.avance = Math.round(j.x - x0);
        out.brassees = pendant.filter(function (s) { return s === 'nage'; }).length;
        out.pas = pendant.filter(function (s) { return s === 'pas'; }).length;
    }""")
    assert r["nage"] is True and r["avance"] > 60, f"on n'a pas nagé : {r}"
    # 180 images a 1 px, une brassee aux 34 px : cinq, a une pres.
    assert 3 <= r["brassees"] <= 8, f"le rythme des brassées n'est pas celui de la nage : {r}"
    assert r["pas"] == 0, f"on fait des pas dans l'eau : {r}"


def test_sortir_de_l_eau_s_entend(eau):
    r = eau("""function (L, o, j, rive, TT, sons, out) {
        o.touche('KeyD');
        for (let i = 0; i < 60; i++) { j.endurance = 100; o.frame(1); }
        o.relacher('KeyD');
        const depart = sons.length;
        o.touche('KeyA');
        let sorti = -1;
        for (let i = 0; i < 240 && sorti < 0; i++) { j.endurance = 100; o.frame(1); if (!j.nage) sorti = i; }
        o.relacher('KeyA');
        out.sorti = sorti >= 0;
        out.apres = sons.slice(depart).filter(function (s) { return s === 'nage' || s === 'plongeon'; }).length;
    }""")
    assert r["sorti"] is True, "on ne ressort pas de l'eau : le juge ne prouve rien"
    assert r["apres"] > 0, "on sort de l'eau sans un bruit"


def test_a_bout_de_souffle_on_entend_couler(eau):
    """Le moment le plus grave que l'eau produit ne peut pas etre muet."""
    r = eau("""function (L, o, j, rive, TT, sons, out) {
        o.touche('KeyD');
        for (let i = 0; i < 30; i++) { j.endurance = 100; o.frame(1); }
        o.relacher('KeyD');
        j.endurance = 1; j.surplus = 0;
        const depart = sons.length;
        let noye = -1;
        for (let i = 0; i < 120 && noye < 0; i++) { o.frame(1); if (L.B.transition) noye = i; }
        out.noye = noye >= 0;
        out.sons = sons.slice(depart);
    }""")
    assert r["noye"] is True, "on ne coule pas : le juge ne prouve rien"
    assert "couler" in r["sons"], f"on coule en silence : {r['sons']}"


def test_un_passant_qui_entre_dans_l_eau_est_pose_dans_le_monde(banc):
    """⚠️ Un agent lance derriere toi se jette a l'eau — et ca s'entend, plus
    faible de loin (`jouerA`). Un son plein pot pour un corps a dix tuiles
    sonnerait comme si c'etait toi qui plongeais."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const j = L.B.joueur, c = L.Monde.carte, TT = L.TT, out = {};
        """ + RIVE + ESPION + """
        // Le joueur au large, l'agent sur la rive : il doit se mouiller pour venir.
        j.x = (rive.x + 6) * TT + 8; j.y = rive.y * TT + 8;
        j.endurance = 100; j.surplus = 60;
        L.Monde.centrerCamera(j.x, j.y);
        L.Police.remiseAZero();
        L.Police.etoilesAuMoins(2);
        const agent = L.Police.creerAgent(rive.x * TT + 8, rive.y * TT + 8, 'poursuit');
        agent.but = { x: j.x, y: j.y };
        agent.vuT = 0;
        L.Entites.indexer();
        let mouille = false;
        for (let i = 0; i < 300 && !mouille; i++) { j.endurance = 100; o.frame(1); if (L.Entites.dansLEau(agent)) mouille = true; }
        // ⚠️ DEUX images de plus, et elles comptent : la police pose `a.nage`
        // AVANT de deplacer son agent, donc l'image ou `dansLEau` devient vrai
        // est celle ou il entre — le plongeon part a la suivante. Un juge qui
        // s'arrete pile a la premiere mesure un silence qui n'existe pas.
        o.frame(2);
        out.mouille = mouille;
        out.pose = sons.filter(function (s) { return s === 'a:plongeon'; }).length;
        L.Entites.retirer(agent);
        return out;
    }""")
    assert r["mouille"] is True, "l'agent n'est pas entré dans l'eau : le juge ne prouve rien"
    assert r["pose"] > 0, "un agent se jette à l'eau derrière toi sans un bruit"


def test_le_char_du_joueur_plonge_coule_et_le_rejette(banc):
    """Trois secondes de char qui s'enfonce, et rien ne s'entendait.

    ⚠️ Et le juge en attrape un autre, bien plus grave que le silence :
    `v.conducteur === 'joueur'` — la chaîne — n'etait JAMAIS vrai (le conducteur
    est l'entite). Donc « IL COULE — SORS » ne s'affichait jamais, et le joueur
    restait `dansVehicule` un char RETIRE des entites : immobile pour toujours,
    au fond de la baie. Mesure du 14 sept. 2026 : 0 px en 60 images de touche.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const j = L.B.joueur, c = L.Monde.carte, TT = L.TT, out = {};
        """ + RIVE + ESPION + """
        const eau = { x: (rive.x + 4) * TT + 8, y: rive.y * TT + 8 };
        const v = L.Vehicules.creer('auto', eau.x, eau.y, 0, { etat: 'stationne' });
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
        L.Monde.centrerCamera(j.x, j.y);
        o.frame(1);
        out.alEntree = sons.slice();
        out.avertit = L.B.msg || null;
        let sombre = -1;
        for (let i = 0; i < 400 && sombre < 0; i++) { o.frame(1); if (L.B.entites.indexOf(v) < 0) sombre = i; }
        out.sombre = sombre >= 0;
        out.pendant = sons.filter(function (s) { return s === 'a:nage'; }).length;
        out.auFond = sons.filter(function (s) { return s === 'couler'; }).length;
        // Il est rejete a l'eau, et il nage : sans ca, il est pris dans un char absent.
        out.dansVehicule = !!j.dansVehicule;
        out.nage = !!j.nage;
        const avant = { x: j.x, y: j.y };
        j.endurance = 100;
        o.touche('KeyA');
        for (let i = 0; i < 60; i++) { j.endurance = 100; o.frame(1); }
        o.relacher('KeyA');
        out.bouge = Math.round(Math.hypot(j.x - avant.x, j.y - avant.y));
        return out;
    }""")
    assert "char_a_l_eau" in r["alEntree"], f"un char entre dans l'eau sans un bruit : {r['alEntree']}"
    assert r["avertit"] == "IL COULE — SORS", f"le HUD n'avertit pas : {r['avertit']!r}"
    assert r["sombre"] is True, "le char n'a pas coulé : le juge ne prouve rien"
    assert r["pendant"] > 0, "l'eau bout autour du char en silence"
    assert r["auFond"] > 0, "le char touche le fond sans un glouglou"
    assert r["dansVehicule"] is False, "le joueur est resté dans un char retiré des entités"
    assert r["nage"] is True, "le joueur ne nage pas : il coule avec le char"
    assert r["bouge"] > 20, f"le joueur ne bouge plus d'un pixel : {r['bouge']} px en 60 images"
