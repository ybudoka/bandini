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


#: Chaque passant du catalogue, debout de face puis à terre : les GRILLES de lettres que la cuisson
#: peint (le banc n'a pas de pixels), et l'image qu'`imageDe` rend à terre (sa taille, son ancre).
#: Sans chapeau : il tombe, il est jugé à part (`test_garderobe_js.py`).
DEBOUT_ET_COUCHE = """
    function lesDeux(L, a, court) {
      const e = L.Entites.creerPieton(L.B.joueur.x, L.B.joueur.y, a);
      if (e.tenue && e.tenue.chapeau !== 'capuche') e.tenue = Object.assign({}, e.tenue, { chapeau: 'aucun' });
      // `court` : coiffe court, sans rien sur la tete — une crete perce la capuche, debout comme a terre.
      if (e.tenue && court) e.tenue = Object.assign({}, e.tenue, { chapeau: 'aucun', coiffure: 'courte' });
      e.horsSaison = true; e.vx = 0; e.vy = 0;
      e.face = 'bas'; const ib = L.Entites.imageDe(e);
      e.vivant = false; e.etat = 'mort'; e.face = 'couche'; const ic = L.Entites.imageDe(e);
      L.Entites.retirer(e);
      let debout, couche;
      if (e.tenue) { debout = L.Garderobe.grille(e.tenue, 'bas', 0); couche = L.Garderobe.grille(e.tenue, 'couche', 0); }
      else {
        debout = L.Saisons.ficheDuMoment(e.sprite, L.SPRITES[e.sprite])[1].poses.bas[0];
        couche = L.Atlas.coucher(debout);
      }
      return { debout: debout, couche: couche, image: { w: ic.canvas.width, h: ic.canvas.height, ancre: ic.ancre, pose: ic.pose },
               imageDebout: { w: ib.canvas.width, h: ib.canvas.height } };
    }
"""


def test_le_corps_a_terre_est_le_corps_debout_tourne(banc):
    """Demande de Martin (2 oct. 2026) : les corps à terre « ne sont pas équivalents au personnage
    debout ». Le gabarit couché commun faisait 12 px de long contre 16 debout et perdait la tenue
    (la robe, le short, les bottes, la coiffure, la barbe, la carrure). Maintenant, chaque pixel du
    passant debout se retrouve à terre, tourné d'un quart de tour (la tête à droite) — tous les
    passants du catalogue, ceux de la garde-robe comme ceux dessinés à la main — et seuls les yeux
    changent : fermés, en contour."""
    r = banc("""function (L) {
        """ + DEBOUT_ET_COUCHE + """
        L.Jeu.commencer();
        const out = {};
        for (const a of L.B.defs.pietons.catalogue) {
          const d = lesDeux(L, a), b = d.debout, c = d.couche, H = b.length;
          let manque = 0, yeux = 0, tous = 0, couches = 0;
          for (let y = 0; y < H; y++) for (let x = 0; x < b[y].length; x++) {
            if (b[y][x] === '.') continue;
            tous++;
            const v = c[x][H - 1 - y];
            if (v === b[y][x]) continue;
            if (v === 'k' && b[y][x] === 'o') yeux++; else manque++;
          }
          c.forEach(function (r) { couches += r.replace(/\\./g, '').length; });
          out[a.slug] = { forme: [d.image.w, d.image.h, d.imageDebout.h, d.imageDebout.w], pose: d.image.pose,
                          tous: tous, manque: manque, yeux: yeux, enTrop: couches - tous };
        }
        return out;
    }""")
    assert len(r) > 40
    for slug, c in r.items():
        assert c["pose"] == "couche", slug
        assert c["forme"][0] == c["forme"][2] and c["forme"][1] == c["forme"][3], \
            f"{slug} : couché {c['forme'][:2]}, debout {c['forme'][2:]} (hauteur, largeur) — pas le même corps"
        assert c["tous"] > 60, slug
        assert c["manque"] == 0 and c["enTrop"] == 0, f"{slug} : {c['manque']} pixels du corps debout perdus à terre"
        assert c["yeux"] <= 2, f"{slug} : {c['yeux']} pixels blancs fermés — un `o` qui n'était pas un oeil"
    fermes = [s for s, c in r.items() if c["yeux"] == 2]
    assert len(fermes) > len(r) // 2, f"les yeux restent ouverts à terre ({len(fermes)} sur {len(r)} fermés)"


def test_le_corps_a_terre_tombe_sur_ses_pieds(banc):
    """Le corps couché est centré sur l'endroit où se tenaient ses pieds (l'ancre), et il repose
    juste au-dessus : un mort ne glisse pas d'un demi-corps en tombant, et le plus long (l'échassier,
    26 px avec ses échasses) aussi. Coiffé court et sans chapeau : l'ancre est celle du corps (le
    squelette nu), une crête qui perce la capuche la dépasse."""
    r = banc("""function (L) {
        """ + DEBOUT_ET_COUCHE + """
        L.Jeu.commencer();
        const out = {};
        for (const a of L.B.defs.pietons.catalogue) {
          const d = lesDeux(L, a, true), c = d.couche;
          let x0 = 99, x1 = -1, y1 = -1;
          c.forEach(function (r, y) { for (let x = 0; x < r.length; x++) if (r[x] !== '.') { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y1 = Math.max(y1, y); } });
          out[a.slug] = { milieu: (x0 + x1 + 1) / 2 - d.image.ancre[0], dessous: d.image.ancre[1] - y1, long: x1 - x0 + 1 };
        }
        return out;
    }""")
    for slug, c in r.items():
        assert abs(c["milieu"]) <= 0.5, f"{slug} : le corps est décalé de {c['milieu']} px de ses pieds"
        assert c["dessous"] == 1, f"{slug} : le corps flotte ou s'enfonce ({c['dessous']})"
    assert r["echassier"]["long"] >= 26, "l'échassier tombe avec ses échasses"


def test_coucher_ferme_les_yeux_et_rien_d_autre(banc):
    """`Atlas.coucher` est un quart de tour : la tête (en haut) passe à droite, le côté gauche en
    haut. Les yeux sont les `o` SEULS de la première rangée qui en a : la chemise de l'avocat (un `o`
    plus bas) et le fard du mime (tout en `o`, les yeux en contour) ne bougent pas."""
    r = banc("""function (L) {
        const A = L.Atlas;
        return {
          tour: A.coucher(['ab', 'cd', 'ef']),
          yeux: A.coucher(['.oo.', 'o..o', '.o..']),
          mime: A.coucher(['oooo', 'okko']),
          ancre: A.ancreCouchee(['....', '.kk.', '.kk.', '.kk.']),
        };
    }""")
    assert r["tour"] == ["eca", "fdb"]
    # La première rangée a des `o` collés : ce ne sont pas des yeux ; la deuxième, si.
    assert r["yeux"] == [".k.", "o.o", "..o", ".k."]
    assert r["mime"] == ["oo", "ko", "ko", "oo"]
    assert r["ancre"] == [1, 3]


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
