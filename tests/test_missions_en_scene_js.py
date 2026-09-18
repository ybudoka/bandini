"""Les cinq missions de la v1, mises en scène — au banc.

⚠️ On juge le CÂBLAGE, pas la fiche : chaque scène du catalogue se termine jouée
sans jamais toucher ACTION et sans aucune voix ; passée à n'importe quel moment,
elle tombe au même état que vue jusqu'au bout ; elle ne tire aucun dé ; aucune ne
part à 3★ ou au volant d'un char qui roule ; et une fin dite loin de celui qui
parle se dit au combiné.
"""

import pytest

from app import missions

MISSIONS = [m["slug"] for m in missions.CATALOGUE]

#: Mettre en place une intro (aller voir le donneur, chez lui s'il le faut) ou une
#: fin (la mission à son dernier objectif, le joueur là où il s'accomplit).
OUTILS = """
  const ORDRE = ['m1', 'm2', 'm3', 'm4', 'm5'];
  function mission(L, slug) { return L.B.defs.missions.find(function (m) { return m.slug === slug; }); }
  function faites(L, slug) { for (const s of ORDRE) { if (s === slug) break; L.B.partie.missionsFaites[s] = 1; } }
  // ⚠️ Les missions faites AVANT `commencer` : c'est lui qui pose les donneurs, et
  // Ti-Guy n'attend plus au terminus une fois M1 faite (`parti_apres`).
  function partie(L, slug) { if (L.B.interieur) L.Jeu.quitterLaPiece(); L.Jeu.retourTitre(); L.B.partie.missionsFaites = {}; L.B.partie.mission = null; faites(L, slug); L.Jeu.commencer(); }
  function allerVoir(L, o, m) {
    const perso = L.B.defs.personnages.find(function (p) { return p.slug === m.donneur; });
    if (perso.ou.indexOf('point:') === 0) {
      const piece = L.Histoire.pieceDuPoint(perso.ou.slice(6));
      o.entrer(L.Monde.carte.portes.find(function (p) { return p.lieu === piece.slug; }));
    }
    const e = L.Histoire.donneur(m.donneur), j = L.B.joueur;
    j.x = e.x - 14; j.y = e.y; L.Entites.indexer();
  }
  function versLaFin(L, m) {
    L.Histoire.commencer(m.slug);
    while (L.B.cinema) L.Histoire.suivante();
    L.B.partie.mission.etape = m.objectifs.length - 1;
    const o = m.objectifs[m.objectifs.length - 1], j = L.B.joueur;
    const ou = o.lieu ? L.Histoire.lieu(o.lieu) : L.Histoire.donneur(m.donneur) || L.Histoire.lieuDuPersonnage(m.donneur);
    j.x = ou.x - (o.lieu ? 0 : 14); j.y = ou.y;
    // Ce qu'on LIVRE est la, a l'arret, a cote de soi : comme dans une vraie partie.
    const monter = m.objectifs.slice().reverse().find(function (q) { return q.type === 'monter'; });
    L.B.mission.vehicule = (o.type === 'livrer' && monter)
      ? L.Vehicules.creer(monter.vehicule, j.x, j.y + 24, 0, { etat: 'stationne', couleur: '#777777' }) : null;
    L.Entites.indexer();
  }
  // Ce qu'on entend, et d'où : chaque boîte de dialogue ouverte.
  function ecouter(L) {
    const dites = [], vrai = L.Hud.dialogue;
    L.Hud.dialogue = function (qui, lignes, duree) { dites.push(qui); return vrai.apply(null, arguments); };
    return dites;
  }
  function jouerJusquauBout(L, o, max) {
    let n = 0, dehors = false;
    const dedans = !!L.B.interieur;
    while ((L.B.scene || L.B.cinema) && n < max) { o.frame(1); n++; if (dedans && L.B.scene && !L.B.interieur) dehors = true; }
    return { n: n, dehors: dehors };
  }
  function etat(L) {
    const j = L.B.joueur;
    return { x: Math.round(j.x * 100), y: Math.round(j.y * 100), dessine: j.dessine, piece: L.B.interieur ? L.B.interieur.slug : null,
             carte: L.Monde.carte.interieur ? L.Monde.carte.interieur.slug : null, entites: L.B.entites.length,
             moi: L.B.entites.indexOf(j) >= 0, tiGuy: !!L.Histoire.donneur('ti_guy'), scene: !!L.B.scene,
             cinema: !!L.B.cinema, mission: L.B.partie.mission ? L.B.partie.mission.slug : null, fin: !!L.B.finEnAttente,
             // Où se tiennent les donneurs : une scène qui en fait marcher un le laisse
             // là où la scène vue jusqu'au bout l'aurait laissé.
             donneurs: L.B.defs.personnages.map(function (p) {
               const e = L.Histoire.donneur(p.slug); return e ? [p.slug, Math.round(e.x), Math.round(e.y)] : null;
             }).filter(Boolean) };
  }
"""


@pytest.mark.parametrize("slug", MISSIONS)
def test_chaque_intro_se_joue_seule_et_rend_la_ville(banc, slug):
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, '%s');
        partie(L, m.slug);
        allerVoir(L, o, m);
        const avant = etat(L);
        L.Histoire.parler(m.donneur);
        const s = L.B.scene, scene = !!s, posee = L.B.partie.mission && L.B.partie.mission.slug;
        const joue = jouerJusquauBout(L, o, 6000);
        return { scene: scene, sautes: s ? s.sautes : null, posee: posee, joue: joue, avant: avant, apres: etat(L) };
    }""" % slug)
    assert r["scene"], f"{slug} : parler au donneur ne joue pas sa scène d'intro"
    assert r["sautes"] == 0, f"{slug} : {r['sautes']} plan(s) de l'intro n'ont trouvé ni leur lieu ni leur acteur"
    assert r["posee"] == slug, "la mission se pose avant son intro"
    assert r["joue"]["n"] < 6000, f"{slug} : la scène d'intro ne se termine pas sans ACTION ni voix"
    avant, apres = r["avant"], r["apres"]
    for cle in ("x", "y", "piece", "carte", "moi"):
        assert apres[cle] == avant[cle], f"{slug} : {cle} {avant[cle]} -> {apres[cle]}"
    if avant["piece"]:
        assert r["joue"]["dehors"], f"{slug} : dedans, la scène n'est jamais allée voir la ville"


@pytest.mark.parametrize("slug", MISSIONS)
def test_chaque_fin_se_joue_seule_et_se_dit_la_ou_il_faut(banc, slug):
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, '%s');
        partie(L, m.slug);
        versLaFin(L, m);
        const dites = ecouter(L);
        L.Histoire.reussir();
        const s = L.B.scene, scene = !!s, faite = !!L.B.partie.missionsFaites[m.slug];
        const joue = jouerJusquauBout(L, o, 6000);
        return { scene: scene, sautes: s ? s.sautes : null, faite: faite, joue: joue, dites: dites, apres: etat(L) };
    }""" % slug)
    assert r["faite"] and r["scene"], f"{slug} : la fin ne joue pas sa scène"
    assert r["sautes"] == 0, f"{slug} : {r['sautes']} plan(s) de la fin n'ont trouvé ni leur lieu ni leur acteur"
    assert r["joue"]["n"] < 6000, f"{slug} : la scène de fin ne se termine pas"
    fin = missions.par_slug(slug)["dialogue"]["fin"]
    assert len(r["dites"]) == len(fin), (slug, r["dites"])
    au_combine = [("(AU TÉLÉPHONE)" in qui) for qui in r["dites"]]
    # ⚠️ m6 se conclut après le dernier contact : Josée est dedans (au bar), le
    # joueur dehors — sa fin se dit au combiné, comme M4 et M5.
    loin = slug in ("m4", "m5", "m6")
    assert all(au_combine) if loin else not any(au_combine), \
        f"{slug} : {r['dites']} — la fin se dit au combiné quand, et seulement quand, celui qui parle n'est pas là"
    if slug == "m1":
        assert r["apres"]["tiGuy"] is False, "Ti-Guy rentre au garage et quitte la ville avec la scène"


@pytest.mark.parametrize("cas", ["m1-fin", "m3-fin", "m4-intro", "m5-fin"])
def test_passer_une_scene_de_mission_a_n_importe_quel_moment(banc, cas):
    """PAUSE à n'importe quel plan tombe au même état que la scène vue jusqu'au bout
    — Ti-Guy rentré, la pièce rendue après une coupe dehors — et le même dé."""
    slug, partie = cas.split("-")
    r = banc("function (L, o) {" + OUTILS + """
        const sorties = [];
        for (const k of [0, 5, 40, 120, 260, 420, -1]) {
            const m = mission(L, '%s');
            partie(L, m.slug); L.graine(2468);
            if ('%s' === 'intro') { allerVoir(L, o, m); L.Histoire.parler(m.donneur); }
            else { versLaFin(L, m); L.Histoire.reussir(); }
            let n = 0;
            if (k < 0) jouerJusquauBout(L, o, 6000);
            else {
                for (; n < k && L.B.scene; n++) o.frame(1);
                L.Scenes.passer();
                while (L.B.cinema) L.Histoire.suivante();
            }
            const e = etat(L);
            e.de = L.B.rng();
            sorties.push({ k: k, e: e });
        }
        return sorties;
    }""" % (slug, partie))
    reference = r[-1]["e"]
    assert not reference["scene"] and not reference["cinema"]
    for s in r[:-1]:
        assert s["e"] == reference, f"{cas} passée à l'image {s['k']} : {s['e']} au lieu de {reference}"


def test_une_scene_de_mission_ne_tire_aucun_de(banc):
    """Le prochain dé est le même avec les scènes et sans elles (répliques seules)."""
    def partie(avec):
        return banc("function (L, o) {" + OUTILS + """
            if (!%s) L.B.defs.missions.forEach(function (m) { m.scenes = null; });
            const m = mission(L, 'm3');
            partie(L, 'm3'); L.graine(1357);
            allerVoir(L, o, m);
            L.Histoire.parler(m.donneur);
            jouerJusquauBout(L, o, 6000);
            const e = etat(L);
            L.Histoire.reussir();
            jouerJusquauBout(L, o, 6000);
            return { x: e.x, y: e.y, entites: e.entites, de: L.B.rng() };
        }""" % ("true" if avec else "false"))
    assert partie(True) == partie(False)


def test_une_fin_attend_qu_on_soit_calme(banc):
    """⚠️ JAMAIS EN PLEINE ACTION : ni à 3★, ni au volant d'un char qui roule. Ce
    qu'on gagne, lui, est accordé tout de suite — rien ne dépend d'avoir regardé."""
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, 'm3');
        partie(L, 'm3');
        versLaFin(L, m);
        const argent0 = L.B.partie.argent;
        L.B.recherche.etoiles = 3;
        L.Histoire.reussir();
        const a3 = { scene: !!L.B.scene, attend: !!L.B.finEnAttente, paye: L.B.partie.argent > argent0,
                     faite: !!L.B.partie.missionsFaites.m3 };
        L.Histoire.maj();
        const encore = !!L.B.scene;
        // Au volant, lancé.
        const j = L.B.joueur, v = o.char('auto', 0, 20, 0);
        L.Vehicules.monter(j, v); v.vitesse = 3;
        L.B.recherche.etoiles = 0;
        L.Histoire.maj();
        const roule = !!L.B.scene;
        v.vitesse = 0;
        L.Histoire.maj();
        return { a3: a3, encore: encore, roule: roule, calme: !!L.B.scene, attend: !!L.B.finEnAttente };
    }""")
    assert r["a3"] == {"scene": False, "attend": True, "paye": True, "faite": True}, r["a3"]
    assert r["encore"] is False, "à 3★, la scène de fin attend"
    assert r["roule"] is False, "au volant d'un char qui roule, elle attend encore"
    assert r["calme"] is True and r["attend"] is False, "à l'arrêt et hors poursuite, elle part"


def test_une_intro_a_trois_etoiles_se_dit_sans_scene(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, 'm2');
        partie(L, 'm2');
        allerVoir(L, o, m);
        L.B.recherche.etoiles = 3;
        L.Histoire.parler(m.donneur);
        return { scene: !!L.B.scene, cinema: !!L.B.cinema, posee: L.B.partie.mission && L.B.partie.mission.slug };
    }""")
    assert r == {"scene": False, "cinema": True, "posee": "m2"}, "à 3★, les mots sans la scène"


def test_l_echec_se_dit_au_combine_au_banc(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, 'm2');
        partie(L, 'm2');
        allerVoir(L, o, m);
        L.Histoire.commencer('m2');
        while (L.B.cinema) L.Histoire.suivante();
        const dites = ecouter(L);
        L.Histoire.echouer('mort');
        return dites;
    }""")
    assert r and all("(AU TÉLÉPHONE)" in qui for qui in r), r


def test_ti_guy_n_attend_plus_au_terminus_une_fois_m1_faite(banc):
    """⚠️ C'était un `if (p.slug === 'ti_guy' && faite('m1'))` dans `histoire.js` ;
    c'est maintenant `parti_apres` dans `missions.py`. Une partie rechargée après M1
    ne le repose pas."""
    r = banc("function (L, o) {" + OUTILS + """
        partie(L, 'm1');
        const avant = !!L.Histoire.donneur('ti_guy');
        partie(L, 'm2');
        return { avant: avant, apres: !!L.Histoire.donneur('ti_guy'), thibodeau: !!L.Histoire.donneur('thibodeau') };
    }""")
    assert r == {"avant": True, "apres": False, "thibodeau": True}, r


def test_la_coupe_de_l_intro_de_m1_filme_le_char_pas_une_ruelle_vide(banc):
    """⚠️ Rouge avant (17 sept. 2026), demande de Martin : « pour la mission du
    véhicule à apporter au garage, il faut voir l'auto en place durant
    l'animation ». Ti-Guy dit « y a un char qui traîne dans une ruelle », la
    coupe va voir CETTE ruelle-là — et elle la filmait vide : le char naissait
    au tour de son objectif, deux objectifs plus loin. Mesuré : 158 images à
    l'écran, aucun char à 200 px. Les chars des objectifs `monter` se posent
    maintenant dès le début de la mission (`Histoire.poser`)."""
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, 'm1');
        partie(L, m.slug);
        allerVoir(L, o, m);
        L.Histoire.parler(m.donneur);
        // La ruelle que la coupe va voir : le lieu de l'objectif `monter`.
        const but = L.Histoire.resoudre(m.objectifs.find(function (q) { return q.type === 'monter'; }).ou, m);
        let images = 0, vues = 0, chars = 0;
        for (let n = 0; n < 6000 && (L.B.scene || L.B.cinema); n++) {
          o.frame(1);
          const s = L.B.scene;
          // La caméra est LÀ-BAS, et l'écran n'est pas au noir : ce que Martin voit.
          if (!s || (s.noir || 0) > 0.2 || !s.vise || Math.hypot(s.vise.x - but.x, s.vise.y - but.y) > 8) continue;
          images++;
          const v = L.B.entites.find(function (e) { return e.type === 'vehicule' && e.mission === 'm1'; });
          if (v) { chars++; if (L.Entites.visibleAEcran(v.x, v.y, -20)) vues++; }
        }
        return { images: images, chars: chars, vues: vues, poses: Object.keys(L.B.mission.chars || {}).length };
    }""")
    assert r["images"] > 60, f"la coupe ne tient pas la ruelle à l'écran ({r})"
    assert r["chars"] == r["images"], f"le char de M1 n'est pas dans la ruelle pendant la coupe ({r})"
    assert r["vues"] == r["images"], f"le char de M1 est posé, mais hors de l'écran pendant la coupe ({r})"


@pytest.mark.parametrize("slug,vers,cible", [
    ("m4", "porte:poste", "police"),       # l'auto-patrouille attend devant le poste
    ("m5", "zone:cravates", "cravates"),   # les Cravates tiennent leurs coins
])
def test_la_coupe_d_une_intro_qui_commence_dedans_filme_ce_qu_elle_pose(banc, slug, vers, cible):
    """⚠️ La règle des scènes, généralisée : une coupe vers la rue doit y trouver
    ce que la mission y pose, MÊME quand la mission commence DANS une pièce. m4
    (Bouchard, au casse-croûte) et m5 (Josée, au bar) posaient leurs éléments
    seulement à la SORTIE : leur intro coupait vers la rue et filmait le poste ou
    le coin des Cravates vide."""
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, '%s');
        partie(L, m.slug);
        // La coupe de l'intro, et ce qu'elle doit montrer — résolu DANS LA VILLE,
        // avant d'entrer : une fois dedans, `Monde.carte` est la pièce.
        const coupe = m.scenes.intro.find(function (p) { return p.type === 'coupe'; });
        const but = L.Histoire.resoudre(coupe.vers, m);
        allerVoir(L, o, m);
        L.Histoire.parler(m.donneur);
        // Ce qu'on cherche : le char `monter`, sinon les Cravates `tuer`.
        function montre(e) {
          if (e.type === 'vehicule') return e.mission === '%s';
          return e.cible && e.mission === '%s';
        }
        let images = 0, vues = 0, poses = 0;
        for (let n = 0; n < 6000 && (L.B.scene || L.B.cinema); n++) {
          o.frame(1);
          const s = L.B.scene;
          if (!s || (s.noir || 0) > 0.2 || !s.vise || Math.hypot(s.vise.x - but.x, s.vise.y - but.y) > 8) continue;
          images++;
          const e = L.B.entites.find(montre);
          if (e) { poses++; if (L.Entites.visibleAEcran(e.x, e.y, -20)) vues++; }
        }
        return { images: images, poses: poses, vues: vues, dedans: L.B.interieur ? L.B.interieur.slug : null };
    }""" % (slug, slug, slug))
    assert r["images"] > 30, f"{slug} : la coupe ne tient pas son lieu à l'écran ({r})"
    assert r["poses"] == r["images"], f"{slug} : {cible} absent pendant la coupe ({r})"
    assert r["vues"] == r["images"], f"{slug} : {cible} posé mais hors de l'écran pendant la coupe ({r})"
    assert r["dedans"], f"{slug} : la mission commence bien DANS une pièce (le juge ne filme pas la rue)"


def test_le_char_d_un_objectif_a_venir_dort_deja_la_et_ne_se_pose_qu_une_fois(banc):
    """La règle, hors mise en scène : le char d'un objectif `monter` est là dès le
    début de la mission, mais il ne devient `B.mission.vehicule` qu'à son tour — et
    l'objectif venu ne pose pas un deuxième char."""
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, 'm1');
        partie(L, m.slug);
        L.Histoire.commencer('m1'); L.B.cinema = null;
        const chars = function () { return L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.mission === 'm1'; }); };
        const auDebut = chars(), premier = auDebut[0];
        const avant = { n: auDebut.length, slug: premier ? premier.slug : null,
                        etape: L.B.partie.mission.etape, vehicule: !!L.B.mission.vehicule };
        // L'objectif du char, venu son tour : le même char, pas un deuxième.
        L.Histoire.avancer();
        const apres = chars();
        return { avant: avant, n: apres.length, meme: apres[0] === premier,
                 vehicule: L.B.mission.vehicule === premier, etape: L.B.partie.mission.etape };
    }""")
    assert r["avant"] == {"n": 1, "slug": "auto", "etape": 0, "vehicule": False}, r["avant"]
    assert r["n"] == 1 and r["meme"], f"un deuxième char est né au tour de l'objectif ({r})"
    assert r["vehicule"] and r["etape"] == 1, f"le char posé d'avance n'est pas devenu celui de la mission ({r})"
