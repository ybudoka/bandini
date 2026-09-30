"""Des corps qui tombent pour vrai, et les bêtes qu'on écrase.

Demande de Martin (30 sept. 2026) : « valide et améliore les sprites des personnages qui peuvent se
faire écraser, et il faut que les chats et ratons puissent aussi se faire écraser ».

La planche de validation a montré 14 passants renversables qui restaient DEBOUT une fois morts : leur
dessin n'avait pas de pose `couche`, et `imageDe` retombait sur `bas`. Et les bêtes étaient hors
d'atteinte de tout char, exprès.

⚠️ Les nombres sont écrits ici, pas relus dans la fiche : un juge qui relit la constante qu'il juge
change avec elle.
"""

import pytest

#: Un coin dégagé où poser un char et une bête, le joueur à côté, la rue vidée.
COIN = """
    function degage(L) {
      const c = L.Monde.carte, M = L.Monde;
      for (let ty = 20; ty < c.h - 20; ty += 3) for (let tx = 20; tx < c.w - 30; tx += 3) {
        let ok = true;
        for (let k = -2; k <= 12 && ok; k++) for (let d = -2; d <= 2 && ok; d++) {
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
    //: Une bête posée là, qui ne bouge pas d'elle-même.
    function bete(L, espece, x, y) {
      const e = { type: 'bete', espece: espece, decor: espece, x: x, y: y, r: 0, solide: false, id: 700 + L.B.betes.length,
                  t: 0, v: 0, humeur: 'pose', minuterie: 99999, vx: 0, vy: 0, altitude: 0, fuite: 0 };
      L.B.betes.push(e);
      return e;
    }
    //: Un char du joueur lancé vers l'est à `vitesse`, le nez sur (x, y).
    function charLance(L, x, y, vitesse) {
      const v = L.Vehicules.creer('auto', x - 20, y, 0, { etat: 'roule' });
      v.conducteur = L.B.joueur; L.B.joueur.dansVehicule = v;
      v.vx = vitesse; v.vy = 0; v.vitesse = vitesse;
      return v;
    }
    function monter(L) {
      L.Jeu.commencer();
      vider(L);
      const g = degage(L);
      if (!g) return null;
      L.B.joueur.x = g.x; L.B.joueur.y = g.y - 3 * L.TT;
      L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
      return g;
    }
"""


def test_tout_passant_qu_on_renverse_tombe_couche(banc):
    """Chaque passant du catalogue qu'un char peut renverser (pas un enfant, qui n'est que
    bousculé) se dessine COUCHÉ une fois mort — pas debout dans sa flaque."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const debout = [];
        for (const a of L.B.defs.pietons.catalogue) {
          if (a.intouchable) continue;
          const e = L.Entites.creerPieton(L.B.joueur.x, L.B.joueur.y, a);
          e.vivant = false; e.etat = 'mort'; e.face = 'couche';
          const img = L.Entites.imageDe(e);
          if (!img || img.pose !== 'couche') debout.push(a.slug + ':' + (img && img.pose));
          L.Entites.retirer(e);
        }
        return { debout: debout, n: L.B.defs.pietons.catalogue.length };
    }""")
    assert r["n"] > 40
    assert r["debout"] == []


def test_une_pose_couchee_est_couchee_et_montre_une_tete(banc):
    """La pose `couche` de chaque dessin est un corps À TERRE : ses cheveux et ses jambes sont sur
    les mêmes rangées (debout, les cheveux sont en haut et les jambes en bas) — ou, sans jambes à
    voir (la mascotte), il est plus large que haut. Et on y voit une tête : de la peau (ou le fard
    du mime) et des cheveux (ou un capuchon)."""
    r = banc("""function (L) {
        const out = {};
        for (const nom in L.SPRITES) {
          const d = L.SPRITES[nom];
          if (!d.poses || !d.poses.couche || d.machine) continue;
          const g = d.poses.couche[0];
          let x0 = 99, x1 = -1, y0 = 99, y1 = -1;
          g.forEach(function (r, y) { for (let x = 0; x < r.length; x++) if (r[x] !== '.') {
            x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); } });
          const tout = g.join('');
          const rangs = function (re) { return g.map(function (r, y) { return re.test(r) ? y : -1; }).filter(function (y) { return y >= 0; }); };
          const cheveux = rangs(/h/), jambes = rangs(/[pb]/);
          out[nom] = { w: x1 - x0 + 1, h: y1 - y0 + 1, largeur: d.w, hauteur: d.h, lignes: g.length,
                       jambes: jambes.length, cote_a_cote: jambes.some(function (y) { return cheveux.indexOf(y) >= 0; }),
                       peau: /[so]/.test(tout), cheveux: cheveux.length > 0 };
        }
        return out;
    }""")
    for nom in ("joueur", "musicien", "amuseur", "jongleur", "echassier", "exhibitionniste", "contractuelle",
                "touriste", "ivrogne", "jogger", "facteur", "crieur", "laveur", "pickpocket",
                "racoleuse", "conductrice", "avocat", "homme_sandwich", "mascotte"):
        assert nom in r, f"{nom} n'a pas de pose couchée"
    for nom, c in r.items():
        assert c["lignes"] == c["hauteur"], nom
        if c["jambes"]:
            assert c["cote_a_cote"], f"{nom} : les jambes sous les cheveux, c'est un corps debout"
        else:
            assert c["w"] > c["h"], f"{nom} : {c['w']}x{c['h']}, ce n'est pas un corps à terre"
        assert c["peau"] and c["cheveux"], nom


@pytest.mark.parametrize("espece", ["chat", "raton"])
def test_un_char_lance_ecrase_la_bete(banc, espece):
    """Un char lancé sur un chat ou un raton l'écrase : il reste au sol, aplati, et ne détale
    plus. ⚠️ Par `avancer`, le chemin de la physique — pas une fonction appelée à la main."""
    r = banc("""function (L) {
        %s
        const g = monter(L);
        if (!g) return { lieu: false };
        const b = bete(L, '%s', g.x + 40, g.y);
        const v = charLance(L, g.x + 40, g.y, 4);
        for (let i = 0; i < 20 && !b.ecrasee; i++) L.Vehicules.avancer(v);
        const apres = { x: b.x, y: b.y };
        for (let i = 0; i < 60; i++) L.Entites.majBete(b);
        return { lieu: true, ecrasee: !!b.ecrasee, decor: b.decor, bouge: Math.hypot(b.x - apres.x, b.y - apres.y),
                 fuite: b.fuite, encore: L.B.betes.indexOf(b) >= 0, pose: L.Entites.poseDeBete(b) };
    }""" % (COIN, espece))
    assert r["lieu"]
    assert r["ecrasee"]
    assert r["decor"] == espece + "_ecrase"
    assert r["encore"], "le corps reste là où il est tombé"
    assert r["bouge"] == 0 and r["fuite"] == 0 and r["pose"] is None


def test_un_char_au_pas_n_ecrase_rien_et_le_goeland_s_envole(banc):
    """Sous la vitesse qui renverse, le char pousse la bête sans l'écraser ; et le goéland, lui,
    ne s'écrase jamais — il s'envole."""
    r = banc("""function (L) {
        %s
        const g = monter(L);
        if (!g) return { lieu: false };
        const chat = bete(L, 'chat', g.x + 40, g.y);
        const lent = charLance(L, g.x + 40, g.y, 0.8);
        for (let i = 0; i < 40; i++) L.Vehicules.avancer(lent);
        L.Entites.retirer(lent);
        const goeland = bete(L, 'goeland', g.x + 40, g.y + 2 * L.TT);
        const vite = charLance(L, g.x + 40, g.y + 2 * L.TT, 4);
        for (let i = 0; i < 20; i++) L.Vehicules.avancer(vite);
        return { lieu: true, chat: !!chat.ecrasee, goeland: !!goeland.ecrasee };
    }""" % COIN)
    assert r["lieu"]
    assert r == {"lieu": True, "chat": False, "goeland": False}


def test_ecraser_une_bete_ne_tire_aucun_de_et_n_est_pas_un_crime(banc):
    """Aucune étoile, aucun témoin (tranché par Martin : les bêtes restent hors du crime), et pas
    un seul `B.rng()` : un dé de plus déplacerait tout le hasard qui suit."""
    r = banc("""function (L) {
        %s
        const g = monter(L);
        if (!g) return { lieu: false };
        const b = bete(L, 'raton', g.x + 40, g.y);
        const v = charLance(L, g.x + 40, g.y, 4);
        let des = 0;
        const rng = L.B.rng;
        L.B.rng = function () { des++; return rng(); };
        const signale = L.Police.signalerCrime; let crimes = 0;
        L.Police.signalerCrime = function () { crimes++; return signale.apply(null, arguments); };
        for (let i = 0; i < 20 && !b.ecrasee; i++) { v.x += v.vx; L.Vehicules.heurterBetes(v); }
        L.B.rng = rng; L.Police.signalerCrime = signale;
        return { lieu: true, ecrasee: !!b.ecrasee, des: des, crimes: crimes, etoiles: L.B.recherche.etoiles };
    }""" % COIN)
    assert r["lieu"] and r["ecrasee"]
    assert r["des"] == 0 and r["crimes"] == 0 and r["etoiles"] == 0


def test_une_bete_ecrasee_ne_compte_plus_et_ne_se_caresse_pas(banc):
    """Le corps ne tient pas la place d'une bête vivante (il en renaît une autre), et on ne
    caresse pas un chat écrasé."""
    r = banc("""function (L) {
        %s
        const g = monter(L);
        if (!g) return { lieu: false };
        const f = L.B.defs.pietons.betes;
        const morts = [];
        for (let i = 0; i < f.chat.combien; i++) {
          const b = bete(L, 'chat', g.x + 40, g.y);
          b.confiance = true;
          const v = charLance(L, g.x + 40, g.y, 4);
          for (let k = 0; k < 20 && !b.ecrasee; k++) { v.x += v.vx; L.Vehicules.heurterBetes(v); }
          L.Entites.retirer(v);
          morts.push(b);
        }
        L.B.joueur.dansVehicule = null;
        const j = L.B.joueur; j.x = g.x + 40; j.y = g.y + 6;
        const main = L.Interactions.chatSousLaMain ? L.Interactions.chatSousLaMain(j) : null;
        return { lieu: true, ecrasees: morts.filter(function (b) { return b.ecrasee; }).length,
                 confiance: morts.some(function (b) { return b.confiance; }),
                 vivants: L.Entites.betesVivantes('chat').length, main: !!main };
    }""" % COIN)
    assert r["lieu"]
    assert r["ecrasees"] == 3
    assert r["vivants"] == 0
    assert not r["confiance"] and not r["main"]


def test_la_bete_ecrasee_se_dessine_aplatie(banc):
    """Le corps écrasé a son dessin (`chat_ecrase`, `raton_ecrase`) : plus large que haut, et
    `dessinerBetes` le peint — on espionne le peintre."""
    r = banc("""function (L) {
        %s
        const g = monter(L);
        if (!g) return { lieu: false };
        const out = { lieu: true };
        for (const esp of ['chat', 'raton']) {
          const d = L.DECORS[esp + '_ecrase'];
          out[esp] = d ? { w: d.w, h: d.h, variantes: d.variantes } : null;
        }
        const b = bete(L, 'chat', L.B.cam.x + 100, L.B.cam.y + 80);
        const v = charLance(L, b.x, b.y, 4);
        for (let i = 0; i < 20 && !b.ecrasee; i++) { v.x += v.vx; L.Vehicules.heurterBetes(v); }
        const d = L.DECORS.chat_ecrase; let peint = 0;
        const p = d.peindre; d.peindre = function () { peint++; return p.apply(this, arguments); };
        const c = L.Base.nouveauCanvas(L.VW, L.VH);
        L.Entites.dessinerBetes(c.getContext('2d'), L.B.cam);
        d.peindre = p;
        out.peint = peint;
        return out;
    }""" % COIN)
    assert r["lieu"]
    for esp in ("chat", "raton"):
        assert r[esp], esp
        assert r[esp]["w"] > r[esp]["h"]
    assert r["peint"] >= 1


def test_la_ruelle_a_encore_ses_chats_apres_une_hecatombe(banc):
    """Trois chats écrasés (le `combien` du chat) ne l'empêchent pas d'en naître un vivant : un corps
    ne tient pas la place d'une bête. ⚠️ On cherche d'abord un endroit où un chat NAÎT, sur une ville
    sans corps (le témoin), puis on y rejoue la naissance avec les trois corps."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        const t = L.B.defs.conduite.trafic;
        t.vehicules_max = 0; t.stationnes_max = 0; t.garer_la_nuit.max = 0;
        const c = L.Monde.carte, TT = L.TT, j = L.B.joueur;
        const f = L.B.defs.pietons.betes;
        for (let ty = 10; ty < c.h - 10; ty += 7) for (let tx = 10; tx < c.w - 30; tx += 7) {
          if (L.Monde.glyphe(tx, ty) !== 'x') continue;
          const px = tx + 15;
          if (!L.Monde.marchablePieton(px, ty)) continue;
          j.x = px * TT + 8; j.y = ty * TT + 8;
          L.Monde.centrerCamera(j.x, j.y);
          L.B.betes = [];
          L.Entites.naitreLesBetes();
          if (!L.Entites.betesVivantes('chat').length) continue;
          const lieu = L.Entites.betesVivantes('chat')[0];
          L.B.betes = [];
          for (let i = 0; i < f.chat.combien; i++) {
            const b = { type: 'bete', espece: 'chat', decor: 'chat', x: lieu.x, y: lieu.y, r: 0, solide: false,
                        id: 800 + i, t: 0, v: 0, humeur: 'pose', minuterie: 99999, vx: 0, vy: 0, altitude: 0, fuite: 0 };
            L.B.betes.push(b);
            L.Entites.ecraserBete(b, null);
          }
          L.Entites.naitreLesBetes();
          return { lieu: true, corps: L.B.betes.filter(function (b) { return b.ecrasee; }).length,
                   vivants: L.Entites.betesVivantes('chat').length };
        }
        return { lieu: false };
    }""")
    assert r["lieu"]
    assert r["corps"] == 3
    assert r["vivants"] >= 1
