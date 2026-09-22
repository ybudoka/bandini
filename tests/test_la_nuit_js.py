"""La nuit a ses habitudes — ce que la nuit change, joué au banc.

⚠️ Les heures sont écrites ici : 0,55 est l'après-midi, 0,9 la nuit (21 h 36), 0,82
la brunante (19 h 41, la plage vient de fermer, il ne fait pas encore nuit).
"""

import re
from pathlib import Path

from app.vehicules import CATALOGUE

JOUR, BRUNANTE, NUIT = 0.55, 0.82, 0.9

RACINE = Path(__file__).resolve().parent.parent


def js(nom: str) -> str:
    return (RACINE / "static" / "js" / nom).read_text(encoding="utf-8")

#: Pose le joueur au-dessus de la plus grosse grève de la carte (comme
#: `test_plage_js.py`), cinq tuiles au nord : la grève est dans la bulle, une
#: part hors champ.
GREVE = """
    function greve(L) {
      const c = L.Monde.carte, TT = L.TT;
      function eau(tx, ty, d) {
        return L.Monde.estEau(tx + d, ty) || L.Monde.estEau(tx - d, ty)
            || L.Monde.estEau(tx, ty + d) || L.Monde.estEau(tx, ty - d);
      }
      let mieux = null, plus = 0;
      for (let ty = 6; ty < c.h - 6; ty += 2) {
        for (let tx = 6; tx < c.w - 6; tx += 2) {
          if (L.Monde.glyphe(tx, ty) !== 's' || !L.Monde.marchablePieton(tx, ty)) continue;
          if (!eau(tx, ty, 1) && !eau(tx, ty, 2)) continue;
          let n = 0;
          for (let dy = -12; dy <= 12; dy++) for (let dx = -12; dx <= 12; dx++) {
            if (L.Monde.glyphe(tx + dx, ty + dy) === 's') n++;
          }
          if (n > plus) { plus = n; mieux = { tx: tx, ty: ty, x: tx * TT + 8, y: ty * TT + 8 }; }
        }
      }
      return plus >= 40 ? mieux : null;
    }
    function baigneurs(L) {
      return L.B.entites.filter(function (e) { return e.metier === 'baigneur' && e.vivant; });
    }
    function surLaGreve(L, heure) {
      L.Jeu.commencer();
      L.graine(31);
      L.B.partie.heure = heure;
      const g = greve(L);
      if (!g) return null;
      L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
      L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
      L.Entites.indexer();
      return g;
    }
"""


def test_la_nuit_personne_ne_nait_sur_la_plage(banc, paquet):
    """La même grève, la même graine : l'après-midi elle se peuple, la nuit elle
    reste vide. ⚠️ Le jour sert de témoin — sans lui, un juge « personne la
    nuit » passerait aussi sur une grève où il ne naît jamais personne."""
    r = banc("""function (L, o) {
        %s
        const out = {};
        for (const [nom, h] of [['jour', %s], ['nuit', %s]]) {
          if (!surLaGreve(L, h)) return { greve: false };
          for (let i = 0; i < 900; i++) { L.B.partie.heure = h; o.frame(1); }
          out[nom] = baigneurs(L).length;
        }
        out.greve = true;
        return out;
    }""" % (GREVE, JOUR, NUIT))
    assert r["greve"], "aucune grève sur la carte"
    assert r["jour"] > 0, "l'après-midi, personne sur la grève : le témoin ne dit rien"
    assert r["nuit"] == 0, "%s baigneurs sont nés sur la plage en pleine nuit" % r["nuit"]


def test_a_la_fermeture_on_sort_de_l_eau_et_on_rentre_hors_champ(banc, paquet):
    """La plage ferme : celui qui barbote sort de l'eau, et qui n'est pas à
    l'écran est rentré. ⚠️ Personne ne s'évapore SOUS NOS YEUX : un baigneur qui
    disparaît était hors champ l'image d'avant."""
    r = banc("""function (L, o) {
        %s
        const g = surLaGreve(L, %s);
        if (!g) return { greve: false };
        for (let i = 0; i < 900; i++) { L.B.partie.heure = %s; o.frame(1); }
        const avant = baigneurs(L).slice();
        if (!avant.length) return { greve: true, avant: 0 };
        // Un baigneur dans l'eau, A L'ECRAN, au moment ou la plage ferme.
        const TT = L.TT;
        let nageur = null;
        for (const e of avant) {
          const bord = L.Entites.bordDeLEau(e);
          if (!bord) continue;
          if (!L.Entites.visibleAEcran(bord.x, bord.y, -40)) continue;
          e.x = bord.x; e.y = bord.y; e.jeu = 'baignade'; e.jeuT = 400; e.barbote = true;
          e.etat = 'arret'; e.minuterie = 30;
          nageur = e; break;
        }
        const vus = new Map();
        let evapores = 0;
        for (let i = 0; i < 900; i++) {
          L.B.partie.heure = %s;
          for (const e of avant) vus.set(e, L.B.entites.indexOf(e) >= 0 && L.Entites.visibleAEcran(e.x, e.y, 0));
          o.frame(1);
          for (const e of avant) {
            if (vus.get(e) && L.B.entites.indexOf(e) < 0 && e.vivant) evapores++;
          }
        }
        const restent = baigneurs(L);
        const horsChamp = restent.filter(function (e) { return !L.Entites.visibleAEcran(e.x, e.y, 40); }).length;
        const mouilles = restent.filter(function (e) {
          return L.Monde.estEau(Math.floor(e.x / TT), Math.floor(e.y / TT));
        }).length;
        return { greve: true, avant: avant.length, apres: restent.length, horsChamp: horsChamp,
                 mouilles: mouilles, evapores: evapores, nageur: !!nageur,
                 nageurSec: nageur ? !L.Monde.estEau(Math.floor(nageur.x / TT), Math.floor(nageur.y / TT)) : null };
    }""" % (GREVE, JOUR, JOUR, BRUNANTE))
    assert r["greve"], "aucune grève sur la carte"
    assert r["avant"] > 0, "personne sur la grève avant la fermeture : le juge ne mesure rien"
    assert r["nageur"], "aucun baigneur à mettre à l'eau sous nos yeux"
    assert r["nageurSec"], "la plage est fermée, et il barbote encore"
    assert r["mouilles"] == 0, "%s baigneurs dans l'eau après la fermeture" % r["mouilles"]
    assert r["horsChamp"] == 0, "%s baigneurs restent sur la plage hors de l'écran" % r["horsChamp"]
    assert r["apres"] < r["avant"], "la plage a fermé et personne n'est rentré"
    assert r["evapores"] == 0, "%s baigneurs ont disparu sous nos yeux" % r["evapores"]


#: Compte les chars garés comme `Vehicules.peupler` : ni le trafic, ni la panne,
#: ni l'auto du lot du poste, ni l'autobus de ligne, ni le char du joueur. Et
#: pose le joueur dans un coin de ville dont l'anneau de naissance porte des
#: cases des DEUX usages — sinon la préférence n'aurait rien à choisir.
GARES = """
    function gares(L) {
      return L.B.entites.filter(function (v) {
        return v.type === 'vehicule' && v.etat === 'stationne' && !v.conducteur
          && !(v.panneT > 0) && !v.gareDeService && v.eau !== true && !(v.def && v.def.eau);
      });
    }
    //: Chaque coin de ville (un pas de huit tuiles) et les cases de son anneau
    //: de naissance, par usage. ⚠️ Sur la graine livrée, 581 cases : 515 en
    //: zone industrielle, 48 en rue résidentielle (les entrées des Érables),
    //: 18 devant des commerces — le premier coin venu n'a presque rien.
    function coins(L) {
      const c = L.Monde.carte, TT = L.TT;
      const NEZ = { '^': [0, -1], 'v': [0, 1], '<': [-1, 0], '>': [1, 0] };
      const fonds = [];
      for (let ty = 2; ty < c.h - 1; ty++) for (let tx = 1; tx < c.w - 1; tx++) {
        const g = L.Monde.glyphe(tx, ty), n = NEZ[g];
        if (!n || L.Monde.glyphe(tx + n[0], ty + n[1]) === g || L.Monde.glyphe(tx - n[0], ty - n[1]) !== g) continue;
        fonds.push({ tx: tx, ty: ty, res: L.Monde.usageA(tx, ty) === 'residentiel' });
      }
      const out = [];
      for (let ty = 30; ty < c.h - 30; ty += 8) for (let tx = 30; tx < c.w - 30; tx += 8) {
        if (!L.Monde.marchablePieton(tx, ty)) continue;
        let res = 0, autres = 0;
        for (const f of fonds) {
          const d = Math.hypot(f.tx - tx, f.ty - ty) * TT;
          if (d < 180 || d > 440) continue;
          if (f.res) res++; else autres++;
        }
        out.push({ tx: tx, ty: ty, res: res, autres: autres });
      }
      return out;
    }
    function meilleur(liste, note) {
      let m = null;
      for (const k of liste) if (!m || note(k) > note(m)) m = k;
      return m;
    }
    //: Les deux usages dans l'anneau : la préférence a de quoi choisir.
    function lieuMixte(L) {
      const m = meilleur(coins(L), function (k) { return Math.min(k.res, k.autres); });
      return m && m.res >= 8 && m.autres >= 8 ? m : null;
    }
    //: Le plus de cases : la nuit a de quoi se garer.
    function lieuPlein(L) {
      const m = meilleur(coins(L), function (k) { return k.res + k.autres; });
      return m && m.res + m.autres >= 30 ? m : null;
    }
    function allerA(L, lieu) {
      L.B.joueur.x = lieu.tx * L.TT + 8; L.B.joueur.y = lieu.ty * L.TT + 8;
      L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
      L.Entites.indexer();
    }
"""


def test_la_nuit_il_y_a_plus_de_chars_gares(banc, paquet):
    """Le même coin de ville, la même graine : la nuit, le monde est rentré, et
    il y a plus de chars garés que le jour. ⚠️ Les nombres sont écrits ici : six
    au plus le jour, et la nuit strictement plus."""
    r = banc("""function (L, o) {
        %s
        const out = {};
        for (const [nom, h] of [['jour', %s], ['nuit', %s]]) {
          L.Jeu.commencer();
          L.graine(7);
          const lieu = lieuPlein(L);
          if (!lieu) return { lieu: false };
          allerA(L, lieu);
          for (let i = 0; i < 4000; i++) { L.B.partie.heure = h; o.frame(1); }
          out[nom] = gares(L).length;
        }
        out.lieu = true;
        return out;
    }""" % (GARES, JOUR, NUIT))
    assert r["lieu"], "aucun coin de ville avec trente cases"
    assert r["jour"] <= 6, "le jour, %s chars garés (six au plus)" % r["jour"]
    assert r["nuit"] <= 12, "la nuit, %s chars garés (douze au plus)" % r["nuit"]
    assert r["nuit"] >= r["jour"] + 3, "la nuit, %s chars garés contre %s le jour" % (r["nuit"], r["jour"])


def test_la_nuit_les_chars_se_garent_d_abord_ou_l_on_habite(banc, paquet):
    """Deux cents places tirées au même endroit : la nuit, la part des cases en
    rue résidentielle monte nettement."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        L.graine(11);
        const TT = L.TT;
        const lieu = lieuMixte(L);
        if (!lieu) return { lieu: false };
        allerA(L, lieu);
        function part(prefere) {
          L.graine(5);
          let res = 0, n = 0;
          for (let k = 0; k < 200; k++) {
            const p = L.Vehicules.placeStationnee(prefere);
            if (!p) continue;
            n++;
            if (L.Monde.usageA(Math.floor(p.x / TT), Math.floor(p.y / TT)) === 'residentiel') res++;
          }
          return { n: n, part: n ? res / n : 0 };
        }
        L.B.partie.heure = %s;
        const jour = part(L.Vehicules.garesVoulus());
        L.B.partie.heure = %s;
        const nuit = part(L.Vehicules.garesVoulus());
        return { lieu: true, k: lieu.k, jour: jour, nuit: nuit };
    }""" % (GARES, JOUR, NUIT))
    assert r["lieu"], "aucun coin de ville avec des cases des deux usages"
    # Le tirage du jour ne tombe sur une case qu'une fois sur quelques-unes.
    assert r["jour"]["n"] >= 10 and r["nuit"]["n"] >= 100, r
    assert r["nuit"]["part"] >= r["jour"]["part"] + 0.25, \
        "la nuit, %.0f %% des chars en rue résidentielle contre %.0f %% le jour" % (
            r["nuit"]["part"] * 100, r["jour"]["part"] * 100)


def test_le_jour_on_se_gare_comme_avant_au_de_pres(banc, paquet):
    """⚠️ Le jour ne change pas d'un dé : une place tirée avec la préférence du
    jour est la même, et laisse le dé au même point, qu'une place tirée sans
    rien. C'est ce qui garde toute la suite — qui joue à 8 h 24 — à sa place."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.heure = %s;
        const out = [];
        for (const prefere of [undefined, L.Vehicules.garesVoulus()]) {
          L.graine(19);
          const places = [];
          for (let k = 0; k < 40; k++) places.push(JSON.stringify(L.Vehicules.placeStationnee(prefere)));
          out.push({ places: places.join('|'), suite: L.B.rng() });
        }
        return out;
    }""" % JOUR)
    assert r[0]["places"] == r[1]["places"], "le jour, les chars ne se garent plus aux mêmes places"
    assert r[0]["suite"] == r[1]["suite"], "le jour, la place d'un char garé consomme d'autres dés"


# --- Vague 2 : ce qu'on voit -----------------------------------------------------------

def test_les_fenetres_s_eteignent_une_a_une_et_se_rallument_avant_le_jour(banc, paquet):
    """À 21 h, toutes les fenêtres allumées le sont encore ; à 3 h 30, la rue est
    noire ; à 5 h 50, quelques cuisines se rallument. ⚠️ Et `lampesVisibles` le
    respecte : une fenêtre couchée n'éclaire pas, même sous nos yeux."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const fenetres = L.Monde.carte.lampes.filter(function (l) { return l.coucher !== undefined; });
        const eteintes = function (h) {
          return fenetres.filter(function (l) { return L.Monde.fenetreEteinte(l, h); }).length;
        };
        // Une fenetre sous nos yeux : on la regarde a 21 h, puis a 3 h 30.
        const f = fenetres[0];
        function vue(h) {
          L.B.partie.heure = h;
          L.Monde.centrerCamera(f.x, f.y);
          const cam = { x: L.B.cam.x, y: L.B.cam.y };
          const cx = Math.round(cam.x), cy = Math.round(cam.y);
          return L.Monde.lampesVisibles(cam).some(function (l) { return l.x === f.x - cx && l.y === f.y - cy; });
        }
        // Chacune a SON lever : couchee une minute avant, debout une minute apres —
        // qu'elle se soit couchee avant minuit ou apres.
        const minute = 1 / 1440;
        const aLHeure = fenetres.filter(function (l) {
          return L.Monde.fenetreEteinte(l, l.lever - minute) && !L.Monde.fenetreEteinte(l, l.lever + minute);
        }).length;
        const avantMinuit = fenetres.filter(function (l) { return l.coucher > 0.5; }).length;
        return { n: fenetres.length, soir: eteintes(21 / 24), creux: eteintes(3.5 / 24),
                 aube: eteintes(5.83 / 24), vueLeSoir: vue(21 / 24), vueLaNuit: vue(3.5 / 24),
                 aLHeure: aLHeure, avantMinuit: avantMinuit };
    }""")
    assert r["n"] > 10, "trop peu de fenêtres pour juger (%s)" % r["n"]
    assert r["soir"] == 0, "%s fenêtres déjà couchées à 21 h" % r["soir"]
    assert r["creux"] == r["n"], "à 3 h 30, %s fenêtres sur %s veillent encore" % (r["n"] - r["creux"], r["n"])
    assert 0 < r["aube"] < r["n"], "à 5 h 50, %s fenêtres sur %s dorment : personne ne se lève" % (r["aube"], r["n"])
    assert 0 < r["avantMinuit"] < r["n"], "les couchers ne passent pas minuit : le juge ne voit qu'un cas"
    assert r["aLHeure"] == r["n"], "%s fenêtres sur %s ne se lèvent pas à leur heure" % (r["n"] - r["aLHeure"], r["n"])
    assert r["vueLeSoir"], "à 21 h, la fenêtre sous nos yeux n'éclaire pas"
    assert not r["vueLaNuit"], "à 3 h 30, une fenêtre couchée éclaire encore"


def test_un_lampadaire_qui_gresille_hoquette_et_les_autres_tiennent(banc, paquet):
    """Sur quinze secondes de nuit, le lampadaire qui grésille s'éteint une part
    du temps — pas tout le temps : il n'est pas mort. Un lampadaire ordinaire ne
    s'éteint jamais."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const lampes = L.Monde.carte.lampes;
        const g = lampes.find(function (l) { return l.gresille; });
        const n = lampes.find(function (l) { return !l.gresille && !l.panne && l.coucher === undefined; });
        if (!g || !n) return { trouve: false };
        let noirG = 0, noirN = 0, vuNoir = 0, vuAllume = 0;
        L.B.partie.heure = 0.9;
        L.Monde.centrerCamera(g.x, g.y);
        const cam = { x: L.B.cam.x, y: L.B.cam.y };
        const cx = Math.round(cam.x), cy = Math.round(cam.y);
        for (let t = 0; t < 900; t++) {
          L.B.t = t;
          const eteint = L.Monde.gresilleEteint(g);
          if (eteint) noirG++;
          if (L.Monde.gresilleEteint(n)) noirN++;
          const vu = L.Monde.lampesVisibles(cam).some(function (l) { return l.x === g.x - cx && l.y === g.y - cy; });
          if (eteint && vu) vuNoir++;
          if (!eteint && vu) vuAllume++;
        }
        return { trouve: true, noirG: noirG, noirN: noirN, vuNoir: vuNoir, vuAllume: vuAllume };
    }""")
    assert r["trouve"], "pas de lampadaire qui grésille dans la ville"
    assert r["noirG"] > 20, "le lampadaire qui grésille ne s'est éteint que %s images sur 900" % r["noirG"]
    assert r["noirG"] < 450, "le lampadaire qui grésille est noir %s images sur 900 : il est mort" % r["noirG"]
    assert r["noirN"] == 0, "un lampadaire ordinaire s'est éteint"
    assert r["vuNoir"] == 0, "l'ampoule est noire et elle éclaire quand même"
    assert r["vuAllume"] > 0, "on ne voit jamais le lampadaire allumé"


#: Un char mené et un char garé, sous nos yeux, rue vidée.
DEUX_CHARS = """
    function deuxChars(L, heure) {
      L.Jeu.commencer();
      L.graine(3);
      L.B.defs.conduite.trafic.vehicules_max = 0;
      L.B.defs.conduite.trafic.stationnes_max = 0;
      L.B.defs.conduite.trafic.garer_la_nuit.max = 0;
      L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(L.Entites.retirer);
      L.B.partie.heure = heure;
      const j = L.B.joueur;
      const mene = L.Vehicules.creer('auto', j.x + 70, j.y, 0, { conducteur: 'trafic', etat: 'roule' });
      const gare = L.Vehicules.creer('auto', j.x - 70, j.y, Math.PI, { etat: 'stationne' });
      mene.vitesse = 0; gare.vitesse = 0;
      L.Monde.centrerCamera(j.x, j.y);
      // ⚠️ Rendu SANS avancer le monde : deux images de simulation, et le char
      // mené braquait de 0,9 rad pour suivre sa rue — « devant » n'était plus l'est.
      L.Jeu.rendre();
      return { mene: mene, gare: gare };
    }
"""


def test_la_nuit_un_char_mene_allume_ses_phares_et_un_char_gare_non(banc, paquet):
    """La nuit, le char qu'on mène jette un faisceau DEVANT lui, ses deux phares
    luisent à l'avant et ses deux feux rouges à l'arrière ; le char garé est
    éteint. Le jour, personne n'allume. (Vers l'est : l'axe du char est `x`.)"""
    r = banc("""function (L, o) {
        %s
        function releve(heure) {
          const c = deuxChars(L, heure);
          const cx = Math.round(L.B.cam.x), cy = Math.round(L.B.cam.y);
          const lampes = L.Vehicules.lampesDesPhares();
          const v = c.mene, demi = v.def.longueur / 2;
          const le = function (cle) { return lampes.filter(function (l) { return l[cle] === v; }); };
          const devant = le('faisceau').filter(function (l) { return l.x + cx - v.x + l.r > demi + 20; }).length;
          const phares = le('phare').filter(function (l) { return l.x + cx - v.x > demi / 2; }).length;
          const feux = le('arriere').filter(function (l) { return l.x + cx - v.x < -demi / 2; }).length;
          const duGare = lampes.filter(function (l) {
            return l.faisceau === c.gare || l.phare === c.gare || l.arriere === c.gare;
          }).length;
          return { total: lampes.length, devant: devant, phares: phares, feux: feux, duGare: duGare };
        }
        return { nuit: releve(%s), jour: releve(%s) };
    }""" % (DEUX_CHARS, NUIT, JOUR))
    assert r["nuit"]["devant"] == 1, "la nuit, le char mené n'éclaire pas devant lui : %s" % r["nuit"]
    assert r["nuit"]["phares"] == 2, "la nuit, les deux phares ne luisent pas à l'avant : %s" % r["nuit"]
    assert r["nuit"]["feux"] == 2, "la nuit, pas deux feux arrière : %s" % r["nuit"]
    assert r["nuit"]["duGare"] == 0, "un char garé a ses phares allumés"
    assert r["jour"]["total"] == 0, "en plein jour, des phares allumés"


#: Tout le parc : la silhouette de chaque fiche du catalogue, ses variantes et
#: celles qui se déclarent d'elle (le tramway), avec sa classe. Et un char mené,
#: SEUL sous nos yeux, rendu sans avancer le monde (`Jeu.rendre`) : une image
#: de simulation le ferait tourner d'un cran.
PARC = """
    function parc(L) {
      const out = [];
      for (const d of L.B.defs.vehicules) {
        const s = L.SPRITES[d.sprite];
        const noms = [d.sprite].concat(Object.keys(s.variantes || {}),
          Object.keys(L.SPRITES).filter(function (n) { return L.SPRITES[n].de === d.sprite; }));
        for (const n of noms) {
          if (!out.some(function (p) { return p.sprite === n; })) out.push({ slug: d.slug, sprite: n, classe: d.classe });
        }
      }
      return out;
    }
    function preparer(L) {
      L.Jeu.commencer();
      L.graine(3);
      L.B.defs.conduite.trafic.vehicules_max = 0;
      L.B.defs.conduite.trafic.stationnes_max = 0;
      L.B.defs.conduite.trafic.garer_la_nuit.max = 0;
    }
    function seul(L, p, heure, angle, z) {
      L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(L.Entites.retirer);
      L.B.partie.heure = heure;
      const j = L.B.joueur;
      const v = L.Vehicules.creer(p.slug, j.x + 40, j.y + 20, angle,
                                  { conducteur: 'trafic', etat: 'roule', sprite: p.sprite, couleur: '#c0392b' });
      v.vitesse = 0; v.z = z || 0;
      L.Monde.centrerCamera(j.x, j.y);
      L.Jeu.rendre();
      const cx = Math.round(L.B.cam.x), cy = Math.round(L.B.cam.y);
      const lampes = L.Vehicules.lampesDesPhares().filter(function (l) {
        return l.faisceau === v || l.phare === v || l.arriere === v;
      });
      // Chaque lampe relevée depuis le char : `dx`, `dy` depuis son centre DESSINÉ.
      return { v: v, lampes: lampes.map(function (l) {
        return Object.assign({}, l, { dx: l.x + cx - v.x, dy: l.y + cy - (v.y - v.z), sol: l.y + cy - v.y });
      }) };
    }
"""


def test_chaque_char_du_parc_allume_les_lampes_que_sa_machine_peint(banc, paquet):
    """⚠️ **« Ajuste correctement les phares pour tous les types de véhicules le
    soir »** (Martin, 21 sept. 2026). Un seul halo se posait 16 px devant le nez
    de tous les chars ; un camion n'avait qu'un feu arrière, au milieu. Chaque
    silhouette du parc déclare ses lampes dans sa machine (les pièces `l` et
    `t`) : chacune a sa lueur, POSÉE SUR ELLE, et aucune lampe peinte n'est
    oubliée.

    Juge sur la grille projetée (`Atlas.projeter`, celle que le jeu peint), à
    huit caps : chaque pixel de lampe peint est sous une lueur de sa sorte (son
    rayon), et chaque lueur tombe, à un cap au moins, à un pixel au plus d'une
    lettre de sa sorte. ⚠️ « À un cap au moins » : de face, les phares de la
    charrue sont cachés par sa lame, et une lampe d'auto l'est par la caisse
    quand elle s'éloigne — sa lueur est alors la lumière qui déborde."""
    r = banc("""function (L, o) {
        %s
        preparer(L);
        const out = {};
        const SORTES = [['l', 'phare'], ['t', 'arriere']];
        for (const p of parc(L)) {
          const fiche = L.SPRITES[p.sprite], cote = fiche.w;
          const res = { lettres: {}, loin: [], oubli: [], lampes: 0 };
          const vues = { l: [], t: [] };
          for (let k = 0; k < 8; k++) {
            const angle = k * Math.PI / 4 - Math.PI / 2;
            const s = seul(L, p, %s, angle);
            const grille = L.Atlas.projeter(fiche.machine, angle, cote);
            const a = function (x, y) { return y >= 0 && y < cote && x >= 0 && x < cote ? grille[y][x] : '.'; };
            res.lampes = Math.max(res.lampes, s.lampes.length);
            for (const [lettre, cle] of SORTES) {
              const lueurs = s.lampes.filter(function (l) { return l[cle] === s.v; });
              res.lettres[lettre] = lueurs.length;
              lueurs.forEach(function (l, i) {
                const gx = Math.floor(cote / 2 + l.dx), gy = Math.floor(cote / 2 + l.dy);
                for (let y = gy - 1; y <= gy + 1; y++) for (let x = gx - 1; x <= gx + 1; x++) if (a(x, y) === lettre) vues[lettre][i] = true;
              });
              for (let y = 0; y < cote; y++) for (let x = 0; x < cote; x++) {
                if (grille[y][x] !== lettre) continue;
                const px = x + 0.5 - cote / 2, py = y + 0.5 - cote / 2;
                if (!lueurs.some(function (l) { return Math.hypot(px - l.dx, py - l.dy) <= l.r; })) res.oubli.push([lettre, k, x, y]);
              }
            }
          }
          for (const [lettre] of SORTES) {
            for (let i = 0; i < res.lettres[lettre]; i++) if (!vues[lettre][i]) res.loin.push([lettre, i]);
          }
          out[p.sprite] = res;
        }
        return out;
    }""" % (PARC, NUIT))
    assert len(r) >= 20, f"le parc n'a que {len(r)} silhouettes : {sorted(r)}"
    for nom, res in r.items():
        assert res["lettres"]["l"] >= 1, f"{nom} : aucun phare ne luit la nuit"
        assert res["lettres"]["t"] >= 1, f"{nom} : aucun feu arrière ne luit la nuit"
        assert not res["loin"], f"{nom} : des lueurs sur aucune lampe, à aucun cap (lettre, rang) {res['loin'][:4]}"
        assert not res["oubli"], f"{nom} : des lampes peintes sans lueur (lettre, cap, x, y) {res['oubli'][:4]}"
    assert r["auto"]["lettres"] == {"l": 2, "t": 2}, r["auto"]
    assert r["camion"]["lettres"] == {"l": 2, "t": 2}, "un camion a DEUX feux arrière, pas un au milieu"
    assert r["moto"]["lettres"] == {"l": 1, "t": 1}, r["moto"]
    # Le plafond garde une place au char du joueur : sa place doit tenir le plus
    # éclairé du parc, sinon ce char-là roulerait éteint une fois l'écran plein.
    par_char = int(re.search(r"^  const LAMPES_PAR_CHAR_MAX = (\d+);", js("vehicules.js"), re.M).group(1))
    le_plus = max(r.items(), key=lambda kv: kv[1]["lampes"])
    assert le_plus[1]["lampes"] <= par_char, (
        f"{le_plus[0]} allume {le_plus[1]['lampes']} lampes, la place gardée n'en tient que {par_char}")


def test_le_faisceau_est_a_la_mesure_de_chaque_classe(banc, paquet):
    """Le faisceau part DES PHARES — pas de devant le nez : ce qui s'allumait
    derrière, c'était la caisse — et porte au-delà du nez. Il est à la mesure de
    son char : la lampe du vélo porte moins loin et moins fort que les phares
    d'une auto, ceux d'un camion ou d'un autobus plus loin, et plus large au
    départ (ses phares sont plus écartés). Un bateau n'en a pas : ses feux de
    navigation seulement. Et il est POSÉ AU SOL : écrasé comme l'ombre, et il
    reste sur la chaussée quand le char saute, pendant que ses phares montent."""
    r = banc("""function (L, o) {
        %s
        preparer(L);
        const out = {};
        for (const p of parc(L)) {
          const s = seul(L, p, %s, 0);
          const f = s.lampes.filter(function (l) { return l.faisceau === s.v; });
          const phares = s.lampes.filter(function (l) { return l.phare === s.v; });
          out[p.sprite] = { classe: p.classe, n: f.length, demi: s.v.def.longueur / 2,
            depart: f.length ? f[0].dx : null, portee: f.length ? f[0].r : null,
            cone: f.length ? f[0].cone : null, force: f.length ? +/,([0-9.]+)\\)$/.exec(f[0].c)[1] : null,
            avantMax: Math.max.apply(null, phares.map(function (l) { return l.dx; })) };
        }
        // Au sol : vers le nord, puis en l'air.
        const auto = parc(L).find(function (p) { return p.sprite === 'auto'; });
        const nord = seul(L, auto, %s, -Math.PI / 2);
        const saut = seul(L, auto, %s, -Math.PI / 2, 24);
        const f = function (s) { return s.lampes.find(function (l) { return l.faisceau === s.v; }); };
        const ph = function (s) { return s.lampes.find(function (l) { return l.phare === s.v; }); };
        out.sol = { p: f(nord).p, ombre: L.B.defs.conduite.ombre.profondeur,
                    solNord: f(nord).sol, solSaut: f(saut).sol, pharesNord: ph(nord).sol, pharesSaut: ph(saut).sol,
                    departNord: f(nord).sol, attendu: -(nord.v.def.longueur / 2) * L.SPRITES.auto.machine.profondeur };
        return out;
    }""" % (PARC, NUIT, NUIT, NUIT))
    sol = r.pop("sol")
    for nom, c in r.items():
        if c["classe"] == "bateau":
            assert c["n"] == 0, f"{nom} : un bateau éclaire l'eau devant lui comme une auto"
            continue
        assert c["n"] == 1, f"{nom} ({c['classe']}) roule sans faisceau"
        assert 0 < c["depart"] <= c["demi"] + 1, (
            f"{nom} : le faisceau part à {c['depart']} px du centre, le nez est à {c['demi']}")
        assert c["depart"] >= c["avantMax"] - 0.5, f"{nom} : le faisceau part derrière ses phares"
        assert c["depart"] + c["portee"] > c["demi"] + 20, f"{nom} : le faisceau ne dépasse pas le nez"
    velo, moto, auto, camion, autobus = r["velo"], r["moto"], r["auto"], r["camion"], r["autobus"]
    assert velo["portee"] < auto["portee"] and velo["force"] < auto["force"], (
        f"la lampe du vélo éclaire comme des phares d'auto : {velo} / {auto}")
    assert moto["cone"][0] < auto["cone"][0], f"une seule lampe, un faisceau aussi large que deux : {moto} / {auto}"
    for gros in (camion, autobus):
        assert gros["portee"] > auto["portee"], f"les phares d'un camion portent comme ceux d'une auto : {gros}"
        assert gros["cone"][0] > auto["cone"][0], f"des phares plus écartés, un départ aussi étroit : {gros}"
    assert sol["p"] == sol["ombre"], f"le faisceau n'est pas écrasé comme l'ombre : {sol}"
    assert abs(sol["departNord"] - sol["attendu"]) < 1.5, f"vers le nord, le faisceau ne part pas du nez écrasé : {sol}"
    assert sol["solSaut"] == sol["solNord"], f"le char saute et son faisceau quitte la chaussée : {sol}"
    assert sol["pharesSaut"] < sol["pharesNord"] - 20, f"le char saute et ses phares restent au sol : {sol}"


def test_chaque_classe_du_catalogue_a_decide_de_son_faisceau():
    """Une classe absente de `FAISCEAUX` roule sans faisceau : c'est une
    décision (un bateau), pas un oubli. La prochaine classe du catalogue — un
    avion au sol, un tracteur — fait rougir ce juge jusqu'à ce qu'on écrive la
    sienne, fût-ce `null`."""
    bloc = re.search(r"^  const FAISCEAUX = \{\n(.*?)^  \};", js("vehicules.js"), re.M | re.S).group(1)
    ecrites = set(re.findall(r"^    (\w+):", bloc, re.M))
    classes = {v["classe"] for v in CATALOGUE}
    assert classes <= ecrites, f"des classes sans décision de faisceau : {sorted(classes - ecrites)}"


def test_quatorze_chars_menes_s_allument_tous_et_le_joueur_toujours(banc, paquet):
    """⚠️ Le plafond comptait des LAMPES (douze, deux par char) : passé six chars à
    l'écran, les suivants roulaient éteints. Il compte des chars. Quatorze chars
    menés s'allument tous — autobus scolaire et cabriolet compris, les plus
    éclairés — et quand l'écran en est plein, celui du joueur, dessiné le
    dernier, s'allume quand même."""
    r = banc("""function (L, o) {
        %s
        preparer(L);
        L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(L.Entites.retirer);
        L.B.partie.heure = %s;
        const j = L.B.joueur;
        const sortes = [['autobus', 'autobus_scolaire'], ['cabriolet', 'cabriolet'], ['auto', 'auto'], ['camion', 'camion'],
                        ['moto', 'moto'], ['velo', 'velo'], ['taxi', 'taxi']];
        function poser(n, y0) {
          const out = [];
          for (let i = 0; i < n; i++) {
            const s = sortes[i %% sortes.length];
            const v = L.Vehicules.creer(s[0], j.x - 180 + (i %% 5) * 80, j.y - 100 + y0 + Math.floor(i / 5) * 40, 0,
                                        { conducteur: 'trafic', etat: 'roule', sprite: s[1], couleur: '#c0392b' });
            v.vitesse = 0;
            out.push(v);
          }
          return out;
        }
        const allume = function (v) {
          return L.Vehicules.lampesDesPhares().some(function (l) { return l.phare === v || l.faisceau === v; });
        };
        const quatorze = poser(14, 0);
        L.Monde.centrerCamera(j.x, j.y);
        L.Jeu.rendre();
        const eteints = quatorze.filter(function (v) { return !allume(v); }).map(function (v) { return v.sprite; });
        // L'écran plein : vingt de plus, et le char du joueur tout en bas.
        poser(20, 0);
        const sien = L.Vehicules.creer('auto', j.x, j.y + 110, 0, { conducteur: j, etat: 'roule', couleur: '#c0392b' });
        sien.vitesse = 0;
        L.Jeu.rendre();
        const derniers = L.Vehicules.lampesDesPhares();
        return { eteints: eteints, sien: allume(sien), dernier: derniers[derniers.length - 1].phare === sien
                 || derniers[derniers.length - 1].arriere === sien, total: derniers.length };
    }""" % (PARC, NUIT))
    assert not r["eteints"], f"des chars menés roulent éteints, l'écran n'en a que quatorze : {r['eteints']}"
    assert r["sien"], f"l'écran plein, le char du joueur roule éteint ({r['total']} lampes)"
    assert r["dernier"], "le char du joueur n'est pas le dernier dessiné : le juge ne dit pas ce qu'il croit"


def test_le_soir_le_faisceau_monte_avec_la_nuit(banc, paquet):
    """À la brune (19 h), le faisceau jetait déjà toute sa force sur une chaussée
    à peine assombrie. Il monte avec la nuit : plus faible à 19 h qu'à 21 h 36,
    et les LUEURS, elles, pleines dès qu'on allume — une lampe allumée se voit."""
    r = banc("""function (L, o) {
        %s
        preparer(L);
        const auto = parc(L).find(function (p) { return p.sprite === 'auto'; });
        const alpha = function (c) { return +/,([0-9.]+)\\)$/.exec(c)[1]; };
        const out = {};
        for (const [nom, h] of [['brune', 0.79], ['nuit', %s]]) {
          const s = seul(L, auto, h, 0);
          out[nom] = { faisceau: alpha(s.lampes.find(function (l) { return l.faisceau === s.v; }).c),
                       lueur: s.lampes.find(function (l) { return l.phare === s.v; }).c,
                       noir: L.Monde.ambiance().alpha };
        }
        return out;
    }""" % (PARC, NUIT))
    brune, nuit = r["brune"], r["nuit"]
    assert brune["noir"] >= 0.2, f"à 19 h il ne fait pas encore assez noir pour allumer : le juge ne dit rien ({brune})"
    assert brune["faisceau"] < nuit["faisceau"] * 0.6, f"le soir, le faisceau a déjà sa force de nuit : {r}"
    assert brune["lueur"] == nuit["lueur"], f"le soir, les phares luisent moins que la nuit : {r}"


#: Chercher un MUR (une façade, ou un toit — même solidité, 1) proche du joueur
#: dans les quatre directions cardinales, et une ROUTE dégagée sur plusieurs
#: tuiles : deux scènes construites dans la vraie ville générée, jamais posées
#: à la main, pour que le juge reste vrai si la ville change de graine.
MUR_ET_ROUTE = """
    // ⚠️ Le mur DOIT être à `minD` tuiles au moins, et le CHEMIN JUSQU'À LUI
    // (d'=1..d-1, DANS LA MÊME DIRECTION) confirmé dégagé — sinon un mur plus
    // proche que `minD` mais jamais vu (la boucle ne regardait qu'à partir de
    // `minD`) se glissait sous les roues de l'auto posée entre les deux.
    function murProche(L, minD) {
      const j = L.B.joueur, TT = L.TT;
      const tx0 = Math.floor(j.x / TT), ty0 = Math.floor(j.y / TT);
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        for (let d = 1; d < 25; d++) {
          if (L.Monde.solidite(tx0 + dx * d, ty0 + dy * d) === 1) {
            if (d >= minD) return { tx0: tx0, ty0: ty0, dx: dx, dy: dy, d: d };
            break;      // le mur de cette direction est trop proche : la suivante
          }
        }
      }
      return null;
    }
    function routeLibre(L, tuiles) {
      const j = L.B.joueur, TT = L.TT;
      for (let cy = -25; cy <= 25; cy++) {
        for (let cx = -25; cx <= 25; cx++) {
          const tx0 = Math.floor(j.x / TT) + cx, ty0 = Math.floor(j.y / TT) + cy;
          if (L.Monde.solidite(tx0, ty0) === 1) continue;
          for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            let ok = true;
            for (let d = 1; d <= tuiles; d++) {
              if (L.Monde.solidite(tx0 + dx * d, ty0 + dy * d) === 1) { ok = false; break; }
            }
            if (ok) return { x: tx0 * TT + 8, y: ty0 * TT + 8, angle: Math.atan2(dy, dx) };
          }
        }
      }
      return null;
    }
"""


def test_le_faisceau_ne_passe_pas_a_travers_un_mur(banc, paquet):
    """⚠️ **« Les phares ne doivent pas passer au travers des toits »** (Martin,
    21 sept. 2026). Un toit partage la même solidité qu'un mur (`Monde.solidite`,
    valeur 1) — la même règle que celle qui dit `Jeu.ligneLibre` — donc les deux
    s'arrêtent pareil. Une auto posée à 3 tuiles (48 px) d'un mur, face à lui, a
    un faisceau qui plafonne à 56 px normalement : sans la garde, il traverserait
    le mur, tout un pâté de maisons plus loin s'il le fallait."""
    r = banc("""function (L, o) {
        %s
        %s
        preparer(L);
        const m = murProche(L, 5);
        const out = { trouve: !!m };
        if (!m) return out;
        const tx = m.tx0 + m.dx * (m.d - 3), ty = m.ty0 + m.dy * (m.d - 3);
        L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(L.Entites.retirer);
        L.B.partie.heure = %s;
        const angle = Math.atan2(m.dy, m.dx);
        const auto = L.Vehicules.creer('auto', tx * L.TT + 8, ty * L.TT + 8, angle,
                                        { conducteur: 'trafic', etat: 'roule', couleur: '#c0392b' });
        auto.vitesse = 0;
        L.Monde.centrerCamera(auto.x, auto.y);
        L.Jeu.rendre();
        const f = L.Vehicules.lampesDesPhares().find(function (l) { return l.faisceau === auto; });
        out.r = f ? f.r : null;
        out.portee = 56;
        return out;
    }""" % (PARC, MUR_ET_ROUTE, NUIT))
    assert r["trouve"], "aucun mur trouvé près du joueur : le juge ne dit rien"
    assert r["r"] is not None, "l'auto face au mur n'a pas de faisceau"
    assert r["r"] < r["portee"], f"le faisceau garde sa pleine portée devant un mur à 48 px : {r}"
    assert 0 < r["r"] <= 48, f"le faisceau dépasse le mur planté à 48 px devant lui : {r}"
    assert r["r"] > 48 - 2 * 16, f"le faisceau s'arrête bien trop court (mur à 48 px) : {r}"


def test_le_faisceau_porte_sa_pleine_mesure_loin_de_tout_mur(banc, paquet):
    """Le pendant du juge précédent : rien devant, et le faisceau du camion — le
    plus long du parc — porte ses 68 px pleins, sans qu'un mur lointain le
    raccourcisse par erreur."""
    r = banc("""function (L, o) {
        %s
        %s
        preparer(L);
        const route = routeLibre(L, 6);
        const out = { trouve: !!route };
        if (!route) return out;
        L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(L.Entites.retirer);
        L.B.partie.heure = %s;
        const camion = L.Vehicules.creer('camion', route.x, route.y, route.angle,
                                          { conducteur: 'trafic', etat: 'roule', couleur: '#c0392b' });
        camion.vitesse = 0;
        L.Monde.centrerCamera(camion.x, camion.y);
        L.Jeu.rendre();
        const f = L.Vehicules.lampesDesPhares().find(function (l) { return l.faisceau === camion; });
        out.r = f ? f.r : null;
        return out;
    }""" % (PARC, MUR_ET_ROUTE, NUIT))
    assert r["trouve"], "aucune route dégagée sur 6 tuiles près du joueur : le juge ne dit rien"
    assert r["r"] == 68, f"loin de tout mur, le faisceau du camion ne porte pas ses 68 px pleins : {r}"


# --- Vague 3 : qui est dehors ------------------------------------------------------------

TROIS_H, QUATRE_H = 3.1 / 24, 4.1 / 24

#: Le joueur à dix tuiles d'un bar, rue vidée, à l'heure dite.
PRES_DU_BAR = """
    function presDuBar(L, heure, k) {
      L.Jeu.commencer();
      L.graine(5);
      const lc = L.B.defs.nuit.last_call, bar = lc.bars[k || 0];
      L.B.partie.heure = heure;
      L.B.joueur.x = bar.x * L.TT + 8; L.B.joueur.y = (bar.y + 10) * L.TT + 8;
      L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
      L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.personnage; }).forEach(L.Entites.retirer);
      L.Entites.indexer();
      return bar;
    }
    function fetards(L) { return L.B.entites.filter(function (e) { return e.fetard && e.vivant; }); }
"""


def test_a_trois_heures_les_fetards_sortent_du_bar_une_fois_par_nuit(banc, paquet):
    """À 3 h, une grappe sort par la porte du bar ; une fois par bar et par nuit.
    À 2 h 50 comme à 4 h, personne ne sort."""
    r = banc("""function (L, o) {
        %s
        const out = {};
        // Avant et apres : rien.
        for (const [nom, h] of [['avant', 2.83 / 24], ['apres', %s]]) {
          presDuBar(L, h);
          for (let i = 0; i < 300; i++) { L.B.partie.heure = h; o.frame(1); }
          out[nom] = fetards(L).length;
        }
        // A trois heures : la grappe, devant SA porte. ⚠️ Un autre bar peut etre dans la
        // bulle et se vider aussi : on compte ceux qui sont nes pres de CELUI-CI.
        const bar = presDuBar(L, %s);
        for (let i = 0; i < 60; i++) { L.B.partie.heure = %s; o.frame(1); }
        const pres = function (e) { return Math.hypot(e.x - (bar.x * L.TT + 8), e.y - (bar.y * L.TT + 8)) <= 3 * L.TT; };
        const f = fetards(L);
        const nes = f.filter(pres).length;
        const loin = f.filter(function (e) { return !pres(e); }).filter(function (e) {
          return !L.B.defs.nuit.last_call.bars.some(function (b) {
            return Math.hypot(e.x - (b.x * L.TT + 8), e.y - (b.y * L.TT + 8)) <= 3 * L.TT;
          });
        }).length;
        // Une deuxieme fois, la meme nuit : personne de plus.
        const encore = L.Entites.naitreLeLastCall();
        // La nuit d'apres, le bar se revide.
        L.B.partie.jour += 1;
        L.Entites.naitreLeLastCall();
        const lendemain = fetards(L).filter(pres).length - nes;
        out.nes = nes; out.ivrognes = f.every(function (e) { return e.arch === 'ivrogne' && e.metier === 'ivrogne'; });
        out.loin = loin; out.encore = encore; out.lendemain = lendemain;
        return out;
    }""" % (PRES_DU_BAR, QUATRE_H, TROIS_H, TROIS_H))
    assert r["avant"] == 0, "des fêtards avant la fermeture des bars"
    assert r["apres"] == 0, "des fêtards sortent encore à 4 h"
    assert 3 <= r["nes"] <= 5, "%s fêtards sortent du bar (trois à cinq)" % r["nes"]
    assert r["ivrognes"], "un fêtard est un ivrogne : il zigzague, il tombe, il ne fuit pas"
    assert r["loin"] == 0, "un fêtard est né loin de la porte du bar"
    assert r["encore"] == 0, "le même bar s'est vidé deux fois la même nuit"
    assert r["lendemain"] >= 3, "la nuit d'après, le bar ne se vide plus"


def test_les_fetards_chantent_et_celui_qu_on_frole_cherche_la_chicane(banc, paquet):
    """Ils chantent des airs à boire ; celui qu'on frôle se retourne et le dit — une
    part d'entre eux passe aux poings. ⚠️ Vingt fêtards : la part se mesure."""
    r = banc("""function (L, o) {
        %s
        const bar = presDuBar(L, %s);
        const lc = L.B.defs.nuit.last_call;
        L.Entites.naitreLeLastCall();
        // Les chansons : on les ecoute une minute.
        const chante = new Set();
        for (let i = 0; i < 3600; i++) {
          L.B.partie.heure = %s;
          o.frame(1);
          for (const e of fetards(L)) if (e.bulle && lc.chansons.indexOf(e.bulle.texte) >= 0) chante.add(e.bulle.texte);
        }
        // La chicane : vingt fetards, on les frole un a un.
        const j = L.B.joueur, mots = [], cogne = [];
        let deuxFois = 0;
        for (let k = 0; k < 20; k++) {
          const e = L.Entites.creerPieton(j.x + 200, j.y, L.Entites.archetype('ivrogne'));
          e.fetard = true; e.etat = 'flane';
          e.x = j.x + 12; e.y = j.y;
          L.Entites.chicaner(e);
          if (e.bulle && lc.chicane.mots.indexOf(e.bulle.texte) >= 0) mots.push(e.bulle.texte);
          if (e.etat === 'attaque_joueur') cogne.push(e.id);
          // Une fois par fetard : on le frole encore, il ne se retourne plus.
          e.bulle = null; e.etat = 'flane';
          L.Entites.chicaner(e);
          if (e.bulle || e.etat !== 'flane') deuxFois++;
          L.Entites.retirer(e);
        }
        return { chante: Array.from(chante), mots: mots.length, cogne: cogne.length, deuxFois: deuxFois };
    }""" % (PRES_DU_BAR, TROIS_H, TROIS_H))
    assert r["chante"], "une minute avec des fêtards, et pas une chanson"
    assert r["mots"] == 20, "%s fêtards sur 20 se sont retournés quand on les a frôlés" % r["mots"]
    assert 2 <= r["cogne"] <= 14, "%s fêtards sur 20 passent aux poings (une part)" % r["cogne"]
    assert r["deuxFois"] == 0, "%s fêtards se sont retournés deux fois" % r["deuxFois"]


def test_le_crieur_ne_crie_pas_la_nuit_et_rentre_hors_champ(banc, paquet):
    """⚠️ Il naissait à 2 h du matin pour hurler la manchette à une rue vide : ses
    heures (6 h → 13 h) ne comptaient qu'à la naissance de l'homme-sandwich."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(9);
        const crieurs = function () {
          return L.B.entites.filter(function (e) { return e.arch === 'crieur' && e.vivant; }).length;
        };
        const out = {};
        for (const [nom, h] of [['matin', 0.35], ['nuit', 0.9]]) {
          L.B.partie.heure = h;
          L.B.entites.filter(function (e) { return e.arch === 'crieur'; }).forEach(L.Entites.retirer);
          for (let k = 0; k < 12; k++) L.Entites.naitreLesSortes();
          out[nom] = crieurs();
        }
        // Un crieur encore la a la nuit tombee, hors de l'ecran : il rentre.
        L.B.partie.heure = 0.35;
        for (let k = 0; k < 12 && !crieurs(); k++) L.Entites.naitreLesSortes();
        const c = L.B.entites.find(function (e) { return e.arch === 'crieur' && e.vivant; });
        let rentre = null;
        if (c) {
          L.B.partie.heure = 0.9;
          for (let i = 0; i < 60; i++) { L.B.partie.heure = 0.9; o.frame(1); }
          rentre = L.B.entites.indexOf(c) < 0;
        }
        out.rentre = rentre;
        return out;
    }""")
    assert r["matin"] >= 1, "le matin, pas de crieur : le témoin ne dit rien"
    assert r["nuit"] == 0, "un crieur est né en pleine nuit"
    assert r["rentre"] is True, "à la nuit, le crieur hors de l'écran ne rentre pas"


def test_a_l_aube_le_camelot_lance_le_clairon_sur_les_perrons(banc, paquet):
    """À 5 h, le camelot fait les perrons : un journal roulé devant chaque porte qu'il
    sert, et il n'entre nulle part. Passé 9 h, les journaux sont rentrés."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(4);
        const AUBE = 5 / 24;
        L.B.partie.heure = AUBE;
        for (let k = 0; k < 20 && !L.B.entites.some(function (e) { return e.arch === 'camelot'; }); k++) {
          L.Entites.naitreLesSortes();
        }
        const c = L.B.entites.find(function (e) { return e.arch === 'camelot' && e.vivant; });
        if (!c) return { camelot: false };
        // ⚠️ Dans une rue qui a des perrons : ne au bord de la carte, il n'a qu'une porte
        // a portee, et le juge mesurerait la geographie. La rue la plus garnie des Erables.
        const portes = L.Monde.carte.portesFermees.filter(function (p) {
          return L.Monde.usageA(p.x, p.y) === 'residentiel' && L.Monde.marchablePieton(p.x, p.y + 1);
        });
        let rue = null, plus = 0;
        for (const p of portes) {
          const n = portes.filter(function (q) { return Math.abs(q.x - p.x) <= 8 && Math.abs(q.y - p.y) <= 2; }).length;
          if (n > plus) { plus = n; rue = p; }
        }
        if (!rue) return { camelot: false };
        c.x = rue.x * L.TT + 8; c.y = (rue.y + 1) * L.TT + 8; c.etat = 'flane';
        L.B.decals.length = 0;
        // ⚠️ La rue VIDEE : suivi de pres, le joueur se tient souvent sur la chaussee, et
        // depuis que la ville a grandi un char l'y fauchait — le juge finissait a l'hopital.
        const t = L.B.defs.conduite.trafic;
        t.vehicules_max = 0; t.stationnes_max = 0; t.garer_la_nuit.max = 0;
        L.B.entites.filter(function (v) { return v.type === 'vehicule'; }).forEach(L.Entites.retirer);
        for (let i = 0; i < 2400; i++) {
          L.B.partie.heure = AUBE;
          // Qu'il reste dans la bulle : on le suit.
          L.B.joueur.x = c.x; L.B.joueur.y = c.y + 60; L.B.joueur.vie = L.B.joueur.vieMax;
          o.frame(1);
        }
        if (L.B.interieur) return { camelot: true, interieur: L.B.interieur.slug };
        const journaux = L.B.decals.filter(function (d) { return d.type === 'journal'; });
        const toutes = L.Monde.carte.portesFermees;
        const devantUnePorte = journaux.filter(function (d) {
          return toutes.some(function (p) {
            return Math.abs(p.x * L.TT + 8 - d.x) <= 1 && Math.abs((p.y + 1) * L.TT + 3 - d.y) <= 1;
          });
        }).length;
        // Passe 9 h : le joueur s'en va, et les journaux sont rentres.
        L.B.joueur.x += 2000;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        for (let i = 0; i < 130; i++) { L.B.partie.heure = 9.5 / 24; o.frame(1); }
        const restent = L.B.decals.filter(function (d) { return d.type === 'journal'; }).length;
        return { camelot: true, journaux: journaux.length, devantUnePorte: devantUnePorte, restent: restent,
                 entre: c.etat === 'entre' };
    }""")
    assert r["camelot"], "pas de camelot à l'aube"
    assert not r.get("interieur"), "le juge a fini dans une pièce (%s) : il ne mesure plus la rue" % r.get("interieur")
    assert r["journaux"] >= 2, "quarante secondes de tournée, %s journal lancé" % r["journaux"]
    assert r["devantUnePorte"] == r["journaux"], "un journal n'est pas tombé sur un perron"
    assert r["restent"] == 0, "passé 9 h, %s journaux traînent encore sur les perrons" % r["restent"]


def test_la_nuit_la_poubelle_sort_un_raton_qui_file(banc, paquet):
    """Le même tirage (0,9) : le jour, un reste de poutine ; la nuit, le rat pèse
    double et c'est un raton laveur — qu'on voit filer, à l'opposé du joueur."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, p = L.B.partie;
        // Plante DEVANT une poubelle ou ACTION fouille (ni porte, ni arme, ni char
        // sous la main), comme les juges des gestes — et par le bouton.
        let d = null;
        for (const q of L.B.entites.filter(function (e) { return e.type === 'decor' && e.decor === 'poubelle' && !e.brise; })) {
          j.x = q.x; j.y = q.y + 14; j.vx = 0; j.vy = 0;
          L.Monde.centrerCamera(j.x, j.y);
          for (const e of L.Entites.autour(j.x, j.y, 100, function (x) { return x.type === 'pieton' || x.type === 'vehicule'; })) L.Entites.retirer(e);
          L.Entites.indexer(); o.viser(q);
          if (L.Monde.porteDevant(j) || L.Combat.objetSousLaMain(j) || L.Vehicules.vehiculeSousLaMain(j)) continue;
          if (!L.Monde.marchablePieton(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT))) continue;
          d = q; break;
        }
        if (!d) return { poubelle: false };
        function fouille(heure) {
          p.heure = heure; p.fouilles = {}; j.vie = 50; L.B.msg = null;
          const t = L.B.t; for (let k = 0; k < 6 && L.B.t === t; k++) o.frame(1);
          p.heure = heure; o.viser(d);
          // Quartier ordinaire, et 0,9 : sur la table ordinaire (50/26/10/7/7), le jour
          // tombe sur le reste de poutine ; la nuit, le rat pese double et c'est lui.
          L.Monde.standingA = function () { return 'ordinaire'; };
          const r = L.B.rng; L.B.rng = function () { return 0.9; };
          try { L.Missions.interagir(j); } finally { L.B.rng = r; }
          const raton = (L.B.betes || []).find(function (b) { return b.espece === 'raton'; });
          return { msg: L.B.msg, raton: !!raton, fuit: raton ? raton.fuite > 0 : false,
                   sens: raton ? (raton.vx * (raton.x - j.x) + raton.vy * (raton.y - j.y)) : 0 };
        }
        const jour = fouille(%s);
        L.B.betes = [];
        const nuit = fouille(%s);
        return { poubelle: true, jour: jour, nuit: nuit };
    }""" % (JOUR, NUIT))
    assert r["poubelle"], "pas de poubelle dans la ville"
    assert r["jour"]["msg"].startswith("UN RESTE DE POUTINE"), r["jour"]
    assert not r["jour"]["raton"], "un raton en plein jour"
    assert r["nuit"]["msg"].startswith("UN RATON LAVEUR"), r["nuit"]
    assert r["nuit"]["raton"] and r["nuit"]["fuit"], "le raton reste dans la poubelle"
    assert r["nuit"]["sens"] > 0, "le raton file vers le joueur au lieu de s'en éloigner"


def test_la_nuit_les_ratons_sortent_et_les_goelands_dorment(banc, paquet):
    """Le jour, pas un raton ; la nuit, pas un goéland de plus — et des ratons dans les
    ruelles. ⚠️ Le même coin : une ruelle près de l'eau, où naissent les deux."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, TT = L.TT;
        // Un coin qui a de la ruelle ET du sable pres de l'eau dans la bulle des betes.
        let lieu = null;
        for (let ty = 20; ty < c.h - 20 && !lieu; ty += 6) for (let tx = 20; tx < c.w - 20 && !lieu; tx += 6) {
          let ruelle = 0, greve = 0;
          for (let dy = -20; dy <= 20; dy += 2) for (let dx = -20; dx <= 20; dx += 2) {
            if (L.Entites.chezElle('raton', tx + dx, ty + dy)) ruelle++;
            if (L.Entites.chezElle('goeland', tx + dx, ty + dy)) greve++;
          }
          if (ruelle >= 6 && greve >= 6 && L.Monde.marchablePieton(tx, ty)) lieu = { x: tx * TT + 8, y: ty * TT + 8 };
        }
        if (!lieu) return { lieu: false };
        function compter(h) {
          L.B.betes = [];
          L.B.partie.heure = h;
          L.B.joueur.x = lieu.x; L.B.joueur.y = lieu.y;
          L.Monde.centrerCamera(lieu.x, lieu.y);
          for (let k = 0; k < 8; k++) L.Entites.naitreLesBetes();
          const n = {};
          for (const b of L.B.betes) n[b.espece] = (n[b.espece] || 0) + 1;
          return n;
        }
        return { lieu: true, jour: compter(%s), nuit: compter(%s) };
    }""" % (JOUR, NUIT))
    assert r["lieu"], "pas de coin de ville avec une ruelle et une grève"
    assert r["jour"].get("goeland", 0) > 0, "le jour, pas un goéland : le témoin ne dit rien"
    assert r["jour"].get("raton", 0) == 0, "un raton en plein jour"
    assert r["nuit"].get("goeland", 0) == 0, "la nuit, un goéland est sorti"
    assert r["nuit"].get("raton", 0) > 0, "la nuit, pas un raton dans les ruelles"


def test_le_camelot_ne_vise_que_le_perron_qu_il_voit_et_raye_celui_qu_il_rate(banc, paquet):
    """⚠️ `cap` marche en ligne droite : un perron derrière un mur le laissait dix
    secondes le nez contre la cour. Il vise le perron qu'il VOIT ; et un perron raté
    (`cap` a renoncé) se raye de sa tournée au lieu d'être revisé sans fin."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.heure = 5 / 24;
        const TT = L.TT, portes = L.Monde.carte.portesFermees;
        const devant = function (p) { return { x: p.x * TT + 8, y: (p.y + 1) * TT + 8 }; };
        // Un endroit ou le perron le plus proche est CACHE, et un autre visible a portee.
        let lieu = null;
        for (const p of portes) {
          if (lieu || !L.Monde.marchablePieton(p.x, p.y + 1)) continue;
          for (const [dx, dy] of [[0, 4], [0, -4], [4, 0], [-4, 0], [3, 3], [-3, 3]]) {
            const tx = p.x + dx, ty = p.y + 1 + dy;
            if (!L.Monde.marchablePieton(tx, ty)) continue;
            const x = tx * TT + 8, y = ty * TT + 8;
            const pres = portes.filter(function (q) {
              const d = devant(q);
              return L.Monde.marchablePieton(q.x, q.y + 1) && Math.hypot(d.x - x, d.y - y) < 150;
            }).sort(function (a, b) {
              const da = devant(a), db = devant(b);
              return Math.hypot(da.x - x, da.y - y) - Math.hypot(db.x - x, db.y - y);
            });
            if (pres.length < 2) continue;
            const d0 = devant(pres[0]);
            if (L.Monde.ligneLibre(x, y, d0.x, d0.y)) continue;
            if (!pres.some(function (q) { const d = devant(q); return L.Monde.ligneLibre(x, y, d.x, d.y); })) continue;
            lieu = { x: x, y: y, cache: pres[0] };
            break;
          }
        }
        if (!lieu) return { lieu: false };
        const c = L.Entites.creerPieton(lieu.x, lieu.y, L.Entites.archetype('camelot'));
        c.x = lieu.x; c.y = lieu.y; c.etat = 'flane';
        const vise = L.Entites.prochainPerron(c);
        const dv = devant(vise);
        const voit = L.Monde.ligneLibre(c.x, c.y, dv.x, dv.y);
        // Un perron rate : `cap` a renonce, il flane — le perron se raye.
        c.tournee = []; c.perron = vise; c.cap = null; c.etat = 'flane'; c.lanceT = 0;
        L.Entites.majCamelot(c);
        return { lieu: true, voit: voit, cacheVise: vise === lieu.cache,
                 raye: c.tournee.indexOf(vise) >= 0, reVise: c.perron === vise };
    }""")
    assert r["lieu"], "aucun endroit où le perron le plus proche est derrière un mur"
    assert not r["cacheVise"] and r["voit"], "le camelot vise un perron derrière un mur"
    assert r["raye"], "un perron raté ne se raye pas de la tournée"
    assert not r["reVise"], "le camelot revise le perron qu'il vient de rater"


# --- Vague 4 : ce que ça change au jeu ----------------------------------------------------

def test_la_nuit_le_comptoir_ferme_mais_pas_le_depanneur_ni_le_bar_avant_trois_heures(banc, paquet):
    """À 3 h 30, le comptoir d'un casse-croûte ordinaire est fermé — l'invite le dit, le
    menu ne vend rien ; le dépanneur sert encore. Le bar sert à 1 h et plus à 3 h 30.
    ⚠️ Par le BOUTON (`utiliserPoint`) : un menu fermé qui s'ouvrirait quand même se voit là."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        // Un comptoir « bouffe » qui n'est PAS le depanneur.
        const porte = c.portes.find(function (p) {
          return p.interieur !== 'depanneur' && (c.def.interieurs[p.interieur].points || []).some(function (q) {
            return q.type === 'emplettes' && q.genre === 'bouffe';
          });
        });
        if (!porte) return { porte: false };
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const point = L.B.interieur.points.find(function (p) { return p.type === 'emplettes'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8;
        L.B.partie.argent = 200;
        function essai(heure) {
          L.B.partie.heure = heure; L.B.menu = null;
          L.Missions.majInvite(j);
          const invite = L.B.invite;
          L.Missions.utiliserPoint(j);
          const m = L.B.menu;
          const actifs = m ? m.items.filter(function (i) { return i.actif; }).length : -1;
          L.B.menu = null;
          return { invite: invite, actifs: actifs, premier: m && m.items[0] ? m.items[0].libelle : null };
        }
        const nuit = essai(3.5 / 24), jour = essai(0.35);
        const piece = L.B.interieur;
        L.B.partie.heure = 3.5 / 24;
        L.B.interieur = { slug: 'depanneur', nom: 'Dépanneur' };
        const dep = L.Missions.menuComptoir({ type: 'emplettes', genre: 'bouffe' }, []);
        L.B.interieur = piece;
        const bar = function (h) {
          L.B.partie.heure = h;
          return L.Missions.comptoirFerme({ type: 'emplettes', genre: 'nuit' });
        };
        return { porte: true, nuit: nuit, jour: jour,
                 depanneur: dep.items.filter(function (i) { return i.actif; }).length,
                 barUneHeure: bar(1 / 24), barTroisHeures: bar(3.5 / 24) };
    }""")
    assert r["porte"], "pas de casse-croûte ordinaire dans la ville"
    assert r["nuit"]["invite"].startswith("FERMÉ — OUVRE À"), r["nuit"]
    assert r["nuit"]["actifs"] == 0, "à 3 h 30, le comptoir vend encore : %s" % r["nuit"]
    assert r["nuit"]["premier"] == r["nuit"]["invite"], "l'invite et le menu ne disent pas la même chose"
    assert r["jour"]["invite"] == "ACHETER" and r["jour"]["actifs"] > 0, "le matin, le comptoir est fermé"
    assert r["depanneur"] > 0, "à 3 h 30, le dépanneur est fermé"
    assert r["barUneHeure"] is None, "à 1 h, le bar est fermé"
    assert r["barTroisHeures"], "à 3 h 30, le bar sert encore : le last call est passé"


#: Le joueur au bord de la tournée de la charrue, qu'elle soit à l'heure dite.
TOURNEE = """
    function surLaTournee(L, heure, cameraSurElle) {
      L.Jeu.commencer();
      L.graine(2);
      L.B.partie.jour = 1;
      L.B.partie.heure = heure;
      const A = L.Autobus.donnees().arroseuse;
      if (!A) return null;
      // A trois cent cinquante pixels de l'endroit ou l'horaire la met : dans la bulle, hors champ.
      const p = L.Autobus.placeALHeure(A, 0, L.Autobus.tempsDeLaPartie());
      L.B.joueur.x = p.x + 350; L.B.joueur.y = p.y;
      if (!L.Monde.marchablePieton(Math.floor(L.B.joueur.x / L.TT), Math.floor(L.B.joueur.y / L.TT))) {
        L.B.joueur.x = p.x; L.B.joueur.y = p.y + 350;
      }
      // ⚠️ La camera peut etre EN AVANCE sur le joueur : posee sur la place de
      // l'arroseuse, elle glisse vers lui — et l'arroseuse attend d'etre hors du cadre.
      // La camera rejoint le joueur en quelques images : on cale l'horloge pour que la
      // PREMIERE image jouee soit un regard de l'arroseuse (`B.t % 20 === 13`).
      if (cameraSurElle) { L.Monde.centrerCamera(p.x, p.y); L.B.t = 12; }
      else L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
      return A;
    }
    function arroseuse(L) {
      return L.B.entites.find(function (v) { return v.type === 'vehicule' && v.ligne === 'arroseuse'; }) || null;
    }
"""


def test_l_arroseuse_sort_la_nuit_hors_champ_et_rentre_le_jour(banc, paquet):
    """À 2 h, l'arroseuse naît hors de l'écran, sur la tournée ; à 14 h, pas
    d'arroseuse — et quand la charrue est dehors, l'arroseuse reste au garage."""
    r = banc("""function (L, o) {
        %s
        const out = {};
        for (const [nom, h] of [['nuit', 2 / 24], ['jour', 14 / 24]]) {
          if (!surLaTournee(L, h, true)) return { tournee: false };
          let vue = false;
          for (let i = 0; i < 400 && !arroseuse(L); i++) {
            L.B.partie.heure = h; o.frame(1);
            const v = arroseuse(L);
            if (v && L.Entites.visibleAEcran(v.x, v.y, 0)) vue = true;
          }
          const v = arroseuse(L);
          out[nom] = v ? { sprite: v.sprite, vue: vue } : null;
        }
        // La charrue dehors : pas d'arroseuse.
        surLaTournee(L, 2 / 24);
        const dehors = L.Neige.charrueDehors;
        L.Neige.charrueDehors = function () { return true; };
        for (let i = 0; i < 400; i++) { L.B.partie.heure = 2 / 24; o.frame(1); }
        out.avecLaCharrue = !!arroseuse(L);
        L.Neige.charrueDehors = dehors;
        out.tournee = true;
        return out;
    }""" % TOURNEE)
    assert r["tournee"], "pas de tournée de charrue dans la ville"
    assert r["nuit"], "à 2 h, pas d'arroseuse"
    assert r["nuit"]["sprite"] == "camion_arroseuse"
    assert not r["nuit"]["vue"], "l'arroseuse est apparue sous nos yeux"
    assert r["jour"] is None, "une arroseuse à 14 h"
    assert not r["avecLaCharrue"], "l'arroseuse est sortie pendant la tempête"


def test_derriere_l_arroseuse_la_rue_est_mouillee_et_un_char_y_glisse_puis_elle_seche(banc, paquet):
    """Elle mouille ce qu'elle passe (la chaussée, pas le trottoir) ; un char sur une
    tuile mouillée tient moins la route et freine moins ; une heure plus tard, c'est sec."""
    r = banc("""function (L, o) {
        %s
        if (!surLaTournee(L, 2 / 24)) return { tournee: false };
        for (let i = 0; i < 400 && !arroseuse(L); i++) { L.B.partie.heure = 2 / 24; o.frame(1); }
        const v = arroseuse(L);
        if (!v) return { arroseuse: false };
        const traces = [];
        // ⚠️ LE JOUEUR EST PLANTE SUR LA CHAUSSEE, la nuit, six cents images : le trafic
        // finissait par le faucher, il se reveillait a l'hopital — et le juge lisait
        // alors la carte de la PIECE, ou tout ce que l'arroseuse avait mouille etait
        // « hors route » (21 sept. 2026 : douze tuiles de « trottoir » mouillees, rien
        // n'etait sur un trottoir). On juge l'arroseuse, pas la survie du joueur.
        L.B.partie.triches.invincible = true;
        let dedans = false;
        for (let i = 0; i < 600; i++) {
          L.B.partie.heure = 2 / 24;
          L.B.joueur.x = v.x + 200; L.B.joueur.y = v.y;   // qu'elle reste dans la bulle
          o.frame(1);
          dedans = dedans || !!L.B.interieur;
          if (i %% 60 === 0) traces.push([Math.floor(v.x / L.TT), Math.floor(v.y / L.TT)]);
        }
        const TT = L.TT;
        const mouilles = traces.filter(function (t) { return L.Monde.mouillee(t[0], t[1]); }).length;
        // Pas un trottoir mouille : on balaie autour de la derniere trace.
        let trottoirs = 0;
        const [lx, ly] = traces[traces.length - 1];
        for (let dy = -4; dy <= 4; dy++) for (let dx = -4; dx <= 4; dx++) {
          if (L.Monde.mouillee(lx + dx, ly + dy) && !L.Monde.estRoute(lx + dx, ly + dy)) trottoirs++;
        }
        // Un char sur la tuile mouillee, et le meme sur une tuile seche.
        const ici = { x: traces[traces.length - 1][0] * TT + 8, y: traces[traces.length - 1][1] * TT + 8 };
        const sec = { x: ici.x + 40 * TT, y: ici.y };
        const adh = [L.Monde.adherenceMouillee(ici), L.Monde.adherenceMouillee(sec)];
        const frein = [L.Monde.freinMouille(ici), L.Monde.freinMouille(sec)];
        // Une heure de jeu plus tard, c'est sec.
        L.B.t += Math.round(60 / 1440 * L.B.defs.economie.jour_secondes * 60);
        const seche = !L.Monde.mouillee(lx, ly);
        return { tournee: true, arroseuse: true, traces: traces.length, mouilles: mouilles, trottoirs: trottoirs,
                 adh: adh, frein: frein, seche: seche, dedans: dedans };
    }""" % TOURNEE)
    assert r["tournee"] and r["arroseuse"], r
    assert not r["dedans"], "le joueur est entré dans une pièce : le juge ne lit plus la rue"
    assert r["mouilles"] >= r["traces"] - 1, "%s de ses %s passages ne sont pas mouillés" % (r["mouilles"], r["traces"])
    assert r["trottoirs"] == 0, "l'arroseuse a mouillé %s tuiles de trottoir" % r["trottoirs"]
    assert r["adh"][0] < 1 and r["adh"][1] == 1, "sur l'asphalte mouillé, un char tient la route pareil : %s" % r["adh"]
    assert r["frein"][0] < 1 and r["frein"][1] == 1, r["frein"]
    assert r["seche"], "une heure plus tard, la rue est encore mouillée"
