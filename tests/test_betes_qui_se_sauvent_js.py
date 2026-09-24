"""Les bêtes qui se sauvent pour vrai — le chat et le raton courent, ils ne glissent plus.

Demande de Martin (22 sept. 2026) : « des ratons et des chats plus réalistes quand ils courent
pour s'enfuir ». Avant : une image fixe, le nez au nord, à pleine vitesse dès la première image,
effacée net dès qu'elle quittait sa ruelle — sous nos yeux.

⚠️ Les nombres sont écrits ici, pas relus dans la fiche : un juge qui relit la constante qu'il
juge change avec elle.
"""

import pytest

from app import pietons

#: Un coin dégagé : une tuile marchable d'où l'on peut courir dix tuiles vers l'est, et d'où
#: part la bête. Le joueur à côté, pour que la bulle vive ; la rue vidée.
DEGAGE = """
    function degage(L) {
      const c = L.Monde.carte, M = L.Monde;
      for (let ty = 20; ty < c.h - 20; ty += 3) for (let tx = 20; tx < c.w - 30; tx += 3) {
        let ok = true;
        for (let k = -2; k <= 12 && ok; k++) for (let d = -1; d <= 1 && ok; d++) {
          if (!M.marchablePieton(tx + k, ty + d)) ok = false;
        }
        if (ok) return { tx: tx, ty: ty, x: tx * L.TT + 8, y: ty * L.TT + 8 };
      }
      return null;
    }
    function vider(L) {
      const t = L.B.defs.conduite.trafic;
      t.vehicules_max = 0; t.stationnes_max = 0; t.garer_la_nuit.max = 0;
      L.B.entites.filter(function (e) { return e.type === 'vehicule' || (e.type === 'pieton' && !e.personnage); })
        .forEach(L.Entites.retirer);
      L.B.betes = [];
    }
    //: Une bete posee la, qui part a l'oppose de `menace`.
    function lancer(L, espece, x, y, menace) {
      const fiche = L.B.defs.pietons.betes[espece];
      const e = { type: 'bete', espece: espece, decor: espece, x: x, y: y, r: 0, solide: false, id: 900 + L.B.betes.length,
                  t: 0, v: 0, humeur: 'pose', minuterie: 99999, vx: 0, vy: 0, altitude: 0, fuite: 0 };
      L.B.betes.push(e);
      L.Entites.sEnvoler(e, fiche, menace);
      return e;
    }
    function suivre(L, e, n, chaque) {
      for (let i = 0; i < n && L.B.betes.indexOf(e) >= 0; i++) {
        const avant = { x: e.x, y: e.y };
        L.Entites.majBete(e);
        if (chaque) chaque(i, avant);
      }
    }
"""


def test_la_fiche_dit_un_depart_une_foulee_et_une_vitesse():
    """Il se ramasse moins d'un quart de seconde, prend son élan en moins d'une seconde, et
    sa foulée de course est plus longue que celle de sa marche."""
    for espece in ("chat", "raton"):
        f = pietons.BETES[espece]
        assert 3 <= f["sursaut_images"] <= 15, espece
        assert f["sursaut_images"] < f["elan_images"] <= 60, espece
        assert f["foulee_px"]["fuit"] > f["foulee_px"]["marche"] > 0, espece
    # Le raton a les pattes courtes : sa foulée est plus courte que celle du chat.
    assert pietons.BETES["raton"]["foulee_px"]["fuit"] < pietons.BETES["chat"]["foulee_px"]["fuit"]


@pytest.mark.parametrize("espece", ["chat", "raton"])
def test_il_court_dans_le_sens_ou_il_va(banc, paquet, espece):
    """Menacé de l'ouest, il file à droite, de profil ; de l'est, à gauche ; du nord, il
    descend (de face) ; du sud, il monte (de dos). ⚠️ Et à chaque image où il avance, le
    dessin regarde là où il va — pas au nord."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        vider(L);
        const g = degage(L);
        if (!g) return { lieu: false };
        L.B.joueur.x = g.x + 5 * L.TT; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        const out = {};
        for (const [nom, mx, my] of [['ouest', -30, 0], ['est', 30, 0], ['nord', 0, -30], ['sud', 0, 30]]) {
          L.B.betes = [];
          const x = g.x + 5 * L.TT, y = g.y;
          const e = lancer(L, '%s', x, y, { x: x + mx, y: y + my });
          const dirs = {}; let contre = 0, avance = 0;
          suivre(L, e, 40, function (i, avant) {
            const p = L.Entites.poseDeBete(e);
            if (!p || p.allure !== 'fuit') return;
            dirs[p.dir] = (dirs[p.dir] || 0) + 1;
            const dx = e.x - avant.x, dy = e.y - avant.y;
            if (Math.hypot(dx, dy) < 0.2 || Math.abs(Math.abs(dx) - Math.abs(dy)) < 0.3) return;
            avance++;
            const vrai = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
            if (vrai !== p.dir) contre++;
          });
          out[nom] = { dirs: dirs, contre: contre, avance: avance };
        }
        // Un VIRAGE en pleine course (c'est ce que fait un mur qu'elle longe) : le dessin
        // suit — pas seulement le sens qu'elle avait au depart.
        L.B.betes = [];
        const v = lancer(L, '%s', g.x + 5 * L.TT, g.y, { x: g.x + 5 * L.TT - 30, y: g.y });
        suivre(L, v, 30);
        const vite = Math.hypot(v.vx, v.vy);
        v.vx = 0; v.vy = vite;
        suivre(L, v, 6);
        const p = L.Entites.poseDeBete(v);
        out.virage = p ? p.dir : null;
        out.lieu = true;
        return out;
    }""" % (DEGAGE, espece, espece))
    assert r["lieu"], "aucun coin dégagé dans la ville"
    assert r["virage"] == "bas", "elle a tourné vers le sud, et on la dessine encore %s" % r["virage"]
    for nom, sens in (("ouest", "droite"), ("est", "gauche"), ("nord", "bas"), ("sud", "haut")):
        d = r[nom]
        assert d["avance"] > 15, "%s, menacé de l'%s, n'a pas couru (%s)" % (espece, nom, d)
        assert max(d["dirs"], key=d["dirs"].get) == sens, "%s menacé de l'%s : %s" % (espece, nom, d["dirs"])
        assert d["contre"] == 0, "%s : %s images où le dessin regarde ailleurs que sa course" % (espece, d["contre"])


@pytest.mark.parametrize("espece", ["chat", "raton"])
def test_il_se_ramasse_puis_accelere_et_sa_foulee_suit_la_distance(banc, paquet, espece):
    """Le départ : quelques images ramassé, sans bouger ; puis il accélère — ses premiers pas
    sont plus courts que sa course. La foulée : les quatre images passent, au rythme de la
    DISTANCE ; une bête qui ne bouge plus ne court pas sur place."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        vider(L);
        const g = degage(L);
        if (!g) return { lieu: false };
        L.B.joueur.x = g.x + 5 * L.TT; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        const e = lancer(L, '%s', g.x + 16, g.y, { x: g.x - 14, y: g.y });
        const pas = [], allures = [], images = new Set();
        suivre(L, e, 60, function (i, avant) {
          pas.push(Math.hypot(e.x - avant.x, e.y - avant.y));
          const p = L.Entites.poseDeBete(e);
          allures.push(p ? p.allure : null);
          if (p && p.allure === 'fuit') images.add(p.image);
        });
        // Figee sur place (plus de vitesse) : son image ne tourne plus.
        e.vx = 0; e.vy = 0; e.elan = 1;
        const figee = new Set();
        suivre(L, e, 12, function () { const p = L.Entites.poseDeBete(e); if (p) figee.add(p.image); });
        return { lieu: true, pas: pas, allures: allures, images: Array.from(images), figee: Array.from(figee) };
    }""" % (DEGAGE, espece))
    assert r["lieu"], "aucun coin dégagé dans la ville"
    sursaut = pietons.BETES[espece]["sursaut_images"]
    assert all(a == "sursaut" for a in r["allures"][:sursaut - 1]), r["allures"][:sursaut + 2]
    assert all(p < 0.01 for p in r["pas"][:sursaut - 1]), "il glisse pendant qu'il se ramasse : %s" % r["pas"][:sursaut]
    debut = sum(r["pas"][sursaut + 1:sursaut + 4]) / 3
    lance = sum(r["pas"][sursaut + 30:sursaut + 36]) / 6
    assert 0 < debut < lance * 0.6, "il part pleine vitesse : %.2f au départ, %.2f lancé" % (debut, lance)
    assert sorted(r["images"]) == [0, 1, 2, 3], "une foulée à %s images : %s" % (len(r["images"]), r["images"])
    assert len(r["figee"]) == 1, "immobile, il court sur place : %s" % r["figee"]


RUELLE = """
    //: Une tuile de ruelle dont la sortie (marchable, hors de la ruelle) est a deux tuiles,
    //: dans l'une des quatre directions : `d` dit laquelle.
    function boutDeRuelle(L) {
      const c = L.Monde.carte, M = L.Monde, R = function (x, y) { return L.Entites.chezElle('chat', x, y); };
      for (let ty = 10; ty < c.h - 10; ty++) for (let tx = 10; tx < c.w - 10; tx++) {
        if (!R(tx, ty)) continue;
        for (const d of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
          if (R(tx + d[0], ty + d[1]) && !R(tx + 2 * d[0], ty + 2 * d[1])
              && M.marchablePieton(tx + 2 * d[0], ty + 2 * d[1]) && M.marchablePieton(tx + 3 * d[0], ty + 3 * d[1])
              && M.marchablePieton(tx + 4 * d[0], ty + 4 * d[1])) {
            return { tx: tx, ty: ty, x: tx * L.TT + 8, y: ty * L.TT + 8, d: d };
          }
        }
      }
      return null;
    }
"""


@pytest.mark.parametrize("espece", ["chat", "raton"])
def test_il_ne_s_evapore_plus_sous_nos_yeux_et_ne_traverse_pas_les_murs(banc, paquet, espece):
    """Au bout d'une ruelle, il en sort en fuyant : il ne disparaît pas au premier pas sur le
    trottoir (c'était le cas). Et sur toute sa course, il ne pose jamais la patte dans un mur ;
    sa fuite finie, il ne s'efface qu'une fois hors de l'écran."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        %s
        vider(L);
        const b = boutDeRuelle(L);
        if (!b) return { lieu: false };
        L.B.joueur.x = b.x; L.B.joueur.y = b.y - 3 * L.TT;
        L.Monde.centrerCamera(b.x, b.y);
        const e = lancer(L, '%s', b.x, b.y, { x: b.x - 30 * b.d[0], y: b.y - 30 * b.d[1] });
        let vuDisparaitre = 0, dansUnMur = 0, sortie = false, images = 0, vu = true;
        for (let i = 0; i < 600 && L.B.betes.indexOf(e) >= 0; i++) {
          vu = L.Entites.visibleAEcran(e.x, e.y, 0);
          L.Entites.majBete(e);
          images++;
          if (L.B.betes.indexOf(e) < 0) { if (vu) vuDisparaitre++; break; }
          if (!L.Monde.marchablePieton(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT))) dansUnMur++;
          if (!L.Entites.chezElle('chat', Math.floor(e.x / L.TT), Math.floor(e.y / L.TT))) sortie = true;
        }
        return { lieu: true, vuDisparaitre: vuDisparaitre, dansUnMur: dansUnMur, sortie: sortie, images: images };
    }""" % (DEGAGE, RUELLE, espece))
    assert r["lieu"], "aucun bout de ruelle qui donne sur un trottoir"
    assert r["sortie"], "la bête n'est pas sortie de sa ruelle : le juge ne mesure rien (%s)" % r
    assert r["vuDisparaitre"] == 0, "la bête s'est évaporée sous nos yeux"
    assert r["dansUnMur"] == 0, "%s images la patte dans un mur" % r["dansUnMur"]
    assert r["images"] > 20, "elle a disparu au bout de %s images" % r["images"]


def test_coincee_sous_nos_yeux_elle_s_assoit(banc, paquet):
    """Sa fuite finie, sous nos yeux, sans pouvoir avancer : elle ne disparaît pas, elle
    s'assoit là où elle est — et reprend sa vie de bête."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        vider(L);
        const g = degage(L);
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 3 * L.TT;
        L.Monde.centrerCamera(g.x, g.y);
        const e = lancer(L, 'chat', g.x, g.y, { x: g.x - 30, y: g.y });
        e.sursaut = 0; e.elan = 1; e.fuite = 1; e.vx = 0; e.vy = 0;
        suivre(L, e, 60);
        return { la: L.B.betes.indexOf(e) >= 0, humeur: e.humeur, fuite: e.fuite,
                 vu: L.Entites.visibleAEcran(e.x, e.y, 0) };
    }""" % DEGAGE)
    assert r["vu"], "le juge n'a pas la bête sous les yeux"
    assert r["la"], "coincée sous nos yeux, la bête s'est évaporée"
    assert r["fuite"] == 0 and r["humeur"] == "pose", "coincée, elle court sur place pour toujours : %s" % r


def test_la_course_ne_tire_pas_un_de(banc, paquet):
    """⚠️ La leçon des dés : chaque dé consommé décale tous ceux qui suivent. La course, la
    foulée et le sens ne tirent rien — ni la bouffée de poussière du départ."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        vider(L);
        const g = degage(L);
        L.B.joueur.x = g.x + 5 * L.TT; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        const parSite = {}, vrai = L.B.rng;
        L.B.rng = function () {
          const pile = new Error().stack || '';
          for (const nom of ['sEnvoler', 'majCourse', 'poseDeBete', 'directionDeBete', 'majFuite']) {
            if (pile.indexOf(nom) >= 0) parSite[nom] = (parSite[nom] || 0) + 1;
          }
          return vrai();
        };
        for (const espece of ['chat', 'raton']) {
          const e = lancer(L, espece, g.x + 16, g.y, { x: g.x - 14, y: g.y });
          suivre(L, e, 200, function () { L.Entites.poseDeBete(e); });
        }
        L.B.rng = vrai;
        return parSite;
    }""" % DEGAGE)
    assert r == {}, "la course a tiré dans le dé du jeu : %s" % r


def test_a_l_ecran_on_peint_la_bete_qui_court_pas_l_image_fixe(banc, paquet):
    """Par le RENDU, pas par la fonction : pendant qu'un chat détale sous nos yeux, le jeu
    peint le chat en course (son allure, son sens, son image) — plus la vieille pose fixe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        vider(L);
        const g = degage(L);
        L.B.joueur.x = g.x + 3 * L.TT; L.B.joueur.y = g.y - 3 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        const e = lancer(L, 'chat', g.x + 16, g.y, { x: g.x - 14, y: g.y });
        const cles = new Set(), vrai = L.Atlas.cuirePeintre;
        L.Atlas.cuirePeintre = function (cle, w, h, p) { if (cle.indexOf('decor|chat') === 0) cles.add(cle); return vrai(cle, w, h, p); };
        L.Atlas.vider();
        for (let i = 0; i < 40; i++) { L.Entites.majBete(e); e.minuterie = 99999; L.Jeu.rendre(); }
        L.Atlas.cuirePeintre = vrai;
        return Array.from(cles);
    }""" % DEGAGE)
    course = [c for c in r if c.startswith("decor|chat_bouge|fuit|droite|")]
    assert len(course) >= 3, "le chat qui détale n'est pas peint en course : %s" % r
    assert not [c for c in r if c.startswith("decor|chat|")], "l'image fixe est encore peinte pendant la course : %s" % r
