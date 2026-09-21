"""Les cinq missions de la v1, mises en scène — au banc.

⚠️ On juge le CÂBLAGE, pas la fiche : chaque scène du catalogue se termine jouée
sans jamais toucher ACTION et sans aucune voix ; passée à n'importe quel moment,
elle tombe au même état que vue jusqu'au bout ; elle ne tire aucun dé ; aucune ne
part à 3★ ou au volant d'un char qui roule ; et une fin dite loin de celui qui
parle se dit au combiné.
"""

import json
import math
import shutil
import subprocess

import pytest

from app import missions
# Les deux usines de répliques, là où les fichiers de mission les prennent.
from app.missions._commun import _l, _p

MISSIONS = [m["slug"] for m in missions.CATALOGUE]

#: ⚠️ **CHAQUE MISSION EST JUGÉE DEUX FOIS : avec la scène qu'elle écrit, et avec
#: celle que `missions.py` lui bâtirait si elle n'en écrivait pas.** C'est la
#: preuve du bloc Lego (demande de Martin, 20 sept. 2026) : une mission qui
#: n'apporte que ses objectifs et ses répliques reçoit des animations qui JOUENT
#: — pas seulement qui passent le juge de forme. Les huit du catalogue couvrent
#: les quatre formes du défaut : un donneur dehors, un donneur dedans, une fin
#: devant lui, une fin ailleurs.
MODES = ("écrite", "défaut")
CAS = [f"{slug}-{mode}" for slug in MISSIONS for mode in MODES]


def scene_jugee(cas: str, partie: str) -> list[dict]:
    """La scène que le banc va vraiment jouer : celle qu'écrit la mission, ou
    celle que `missions.scene_par_defaut` lui bâtirait."""
    slug, mode = cas.split("-")
    m = missions.par_slug(slug)
    return m["scenes"][partie] if mode == "écrite" else missions.scene_par_defaut(m, partie)


def poser(cas: str, partie: str) -> tuple[str, str]:
    """Le slug, et le JS qui pose la scène à juger (rien, si elle est déjà là)."""
    slug, mode = cas.split("-")
    if mode == "écrite":
        return slug, ""
    return slug, f"mission(L, '{slug}').scenes['{partie}'] = {json.dumps(scene_jugee(cas, partie), ensure_ascii=False)};"


#: ⚠️ **UNE FICHE RÉDUITE À L'OS**, pour le juge du bloc Lego : ce qui distingue
#: une mission, et rien d'autre — pas de `prerequis` au-delà du fil, pas de
#: `phase`, pas d'`echec`, pas de `donne`, **pas de `scenes`**. Elle finit chez
#: Josée, qui se tient DEDANS.
NEUVE: dict = {
    "slug": "zz", "titre": "Un essai", "donneur": "josee",
    "prerequis": [missions.ordre_topologique()[-1]], "recompense": 300,
    "objectifs": [
        {"type": "aller", "lieu": "garage", "rayon": 4, "texte": "VA AU GARAGE"},
        {"type": "retourner", "texte": "REVIENS ME VOIR"},
    ],
    "dialogue": {
        "appel": [_l("josee", "C'est moi. Viens me voir, j'ai une job.")],
        "intro": [_l("josee", "Va au garage."), _l("josee", "Pis reviens me voir.")],
        "pendant": [_p("josee", "Ça avance, ton affaire?", 1)],
        "fin": [_l("josee", "C'est fait. Merci."), _l("josee", "On se reparle.")],
        "echec": [_l("josee", "Une autre fois. Repose-toi.")],
    },
}

#: Mettre en place une intro (aller voir le donneur, chez lui s'il le faut) ou une
#: fin (la mission à son dernier objectif, le joueur là où il s'accomplit).
#: ⚠️ L'ordre vient de `ordre_topologique()`, jamais d'une liste recopiée : elle
#: s'était déjà arrêtée à m5 pendant que le catalogue en comptait huit.
OUTILS = ('  const ORDRE = ' + json.dumps(missions.ordre_topologique()) + ';' + """
  function mission(L, slug) { return L.B.defs.missions.find(function (m) { return m.slug === slug; }); }
  function faites(L, slug) {
    for (const s of ORDRE) { if (s === slug) break; L.B.partie.missionsFaites[s] = 1; }
    // ⚠️ Un donneur donne la PREMIERE mission disponible de sa liste (`disponibleDe`, l'ordre du catalogue) :
    // chez Marco, f01 se donne avant m97, et parler a Marco posait f01 quand le juge attendait m97. Celles du
    // meme donneur qui viennent AVANT la mission jugee sont donc faites aussi — sans les nommer.
    const cible = mission(L, slug);
    for (const m of L.B.defs.missions) { if (m.slug === slug) break; if (cible && m.donneur === cible.donneur) L.B.partie.missionsFaites[m.slug] = 1; }
  }
  // ⚠️ **CE QU'UNE MISSION EXIGE EN PLUS DE SES PREREQUIS** (`exige`, M16) : le
  // juge le TIENT, au lieu de faire comme s'il n'existait pas. Sans ca, une
  // mission conditionnelle n'est jamais offerte au banc et sa scene d'intro
  // n'est jugee par personne — c'est ce qui arrivait a m97 (`liberes: 3`), rouge
  // sur `dev` sans que rien ne le dise. Les cles sont celles d'`exigeTenu`.
  function tenirExige(L, m) {
    const e = m && m.exige, p = L.B.partie;
    if (!e) return;
    if (e.argent_min !== undefined) p.argent = Math.max(p.argent || 0, e.argent_min);
    if (e.dette !== undefined) p.dette = Math.min(p.dette || 0, e.dette);
    if (e.tenue) { p.tenues = p.tenues || []; if (p.tenues.indexOf(e.tenue) < 0) p.tenues.push(e.tenue); }
    // ⚠️ `exigeTenu` ne fait que COMPTER ces deux-la ; on prend quand meme les
    // vrais slugs de la ville et du catalogue, pour que le carnet et le HUD
    // lisent quelque chose qui existe.
    if (e.liberes !== undefined) {
      const d = (L.Monde.carte && L.Monde.carte.def && L.Monde.carte.def.districts) || [];
      p.libere = d.map(function (q) { return q.slug; }).slice(0, e.liberes);
      while (p.libere.length < e.liberes) p.libere.push('district' + p.libere.length);
    }
    if (e.proprietes !== undefined) {
      p.proprietes = p.proprietes || {};
      const noms = (L.B.defs.economie.proprietes || []).map(function (q) { return q.slug; });
      for (let i = 0; Object.keys(p.proprietes).length < e.proprietes; i++) {
        p.proprietes[noms[i] || ('propriete' + i)] = { jour: 1, caisse: 0 };
      }
    }
  }
  // ⚠️ Les missions faites AVANT `commencer` : c'est lui qui pose les donneurs, et
  // Ti-Guy n'attend plus au terminus une fois M1 faite (`parti_apres`).
  function partie(L, slug) { if (L.B.interieur) L.Jeu.quitterLaPiece(); L.Jeu.retourTitre(); L.B.partie.missionsFaites = {}; L.B.partie.mission = null; faites(L, slug); L.Jeu.commencer(); tenirExige(L, mission(L, slug)); }
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
    // ⚠️ **OU L'ON EST QUAND LA FIN PART**, et c'est le dernier objectif qui le
    // dit — c'est lui, ensuite, qui decide si le donneur est a portee de voix.
    // Un LIEU nous y emmene ; `retourner` nous ramene devant lui ; tout le reste
    // (rattraper un fuyard, semer la police) se finit LA OU L'ON EST, et le
    // donneur, lui, est reste chez lui. Poser le joueur sur le donneur dans ce
    // dernier cas faisait parler en personne quelqu'un que la vraie partie
    // aurait mis au combine.
    if (o.lieu) { const l = L.Histoire.lieu(o.lieu); j.x = l.x; j.y = l.y; }
    else if (o.type === 'retourner') {
      const e = L.Histoire.donneur(m.donneur) || L.Histoire.lieuDuPersonnage(m.donneur);
      j.x = e.x - 14; j.y = e.y;
    }
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
             carte: L.Monde.carte.interieur ? L.Monde.carte.interieur.slug : null,
             // ⚠️ **CE QU'UNE SCENE PEUT EMPORTER, PAS LE COMPTE BRUT DE LA VILLE.**
             // La foule se repeuple autour du joueur au fil des images VIVANTES, et
             // une scene passee n'en consomme pas le meme nombre qu'une scene
             // regardee : `B.entites.length` mesurait donc le va-et-vient des
             // passants — 2 488 contre 2 489 sur m2, sans qu'aucune des deux scenes
             // ait laisse ni emporte quoi que ce soit. On compte ce qu'une scene
             // TOUCHE : les hommes que la mission a poses, les personnages de
             // l'histoire.
             restes: L.B.entites.filter(function (e) { return e.mission || e.personnage; }).length,
             moi: L.B.entites.indexOf(j) >= 0, tiGuy: !!L.Histoire.donneur('ti_guy'), scene: !!L.B.scene,
             cinema: !!L.B.cinema, mission: L.B.partie.mission ? L.B.partie.mission.slug : null, fin: !!L.B.finEnAttente,
             // Où se tiennent les donneurs : une scène qui en fait marcher un le laisse
             // là où la scène vue jusqu'au bout l'aurait laissé.
             donneurs: L.B.defs.personnages.map(function (p) {
               const e = L.Histoire.donneur(p.slug); return e ? [p.slug, Math.round(e.x), Math.round(e.y)] : null;
             }).filter(Boolean) };
  }
""")


@pytest.mark.parametrize("cas", CAS)
def test_chaque_intro_se_joue_seule_et_rend_la_ville(banc, cas):
    slug, pose = poser(cas, "intro")
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, '%s');
        %s
        partie(L, m.slug);
        allerVoir(L, o, m);
        const avant = etat(L);
        L.Histoire.parler(m.donneur);
        const s = L.B.scene, scene = !!s, posee = L.B.partie.mission && L.B.partie.mission.slug;
        const joue = jouerJusquauBout(L, o, 6000);
        return { scene: scene, sautes: s ? s.sautes : null, posee: posee, joue: joue, avant: avant, apres: etat(L) };
    }""" % (slug, pose))
    assert r["scene"], f"{slug} : parler au donneur ne joue pas sa scène d'intro"
    assert r["sautes"] == 0, f"{slug} : {r['sautes']} plan(s) de l'intro n'ont trouvé ni leur lieu ni leur acteur"
    assert r["posee"] == slug, "la mission se pose avant son intro"
    assert r["joue"]["n"] < 6000, f"{slug} : la scène d'intro ne se termine pas sans ACTION ni voix"
    avant, apres = r["avant"], r["apres"]
    for cle in ("x", "y", "piece", "carte", "moi"):
        assert apres[cle] == avant[cle], f"{slug} : {cle} {avant[cle]} -> {apres[cle]}"
    if avant["piece"]:
        assert r["joue"]["dehors"], f"{slug} : dedans, la scène n'est jamais allée voir la ville"


@pytest.mark.parametrize("cas", CAS)
def test_chaque_fin_se_joue_seule_et_se_dit_la_ou_il_faut(banc, cas):
    slug, pose = poser(cas, "fin")
    r = banc("function (L, o) {" + OUTILS + """
        const m = mission(L, '%s');
        %s
        partie(L, m.slug);
        versLaFin(L, m);
        const dites = ecouter(L);
        L.Histoire.reussir();
        const s = L.B.scene, scene = !!s, faite = !!L.B.partie.missionsFaites[m.slug];
        const joue = jouerJusquauBout(L, o, 6000);
        return { scene: scene, sautes: s ? s.sautes : null, faite: faite, joue: joue, dites: dites, apres: etat(L) };
    }""" % (slug, pose))
    assert r["faite"] and r["scene"], f"{slug} : la fin ne joue pas sa scène"
    assert r["sautes"] == 0, f"{slug} : {r['sautes']} plan(s) de la fin n'ont trouvé ni leur lieu ni leur acteur"
    assert r["joue"]["n"] < 6000, f"{slug} : la scène de fin ne se termine pas"
    fin = missions.par_slug(slug)["dialogue"]["fin"]
    assert len(r["dites"]) == len(fin), (slug, r["dites"])
    au_combine = [("(AU TÉLÉPHONE)" in qui) for qui in r["dites"]]
    # ⚠️ m6 se conclut après le dernier contact : Josée est dedans (au bar), le
    # joueur dehors — sa fin se dit au combiné, comme M4 et M5.
    # ⚠️ **LA RÈGLE SE LIT DANS LES DONNÉES**, pas dans une liste de slugs : une
    # mission de plus doit être jugée sans qu'on vienne l'inscrire ici.
    loin = not missions.fin_dite_en_personne(missions.par_slug(slug), scene_jugee(cas, "fin"))
    assert all(au_combine) if loin else not any(au_combine), \
        f"{slug} : {r['dites']} — la fin se dit au combiné quand, et seulement quand, celui qui parle n'est pas là"
    if missions.personnage(missions.par_slug(slug)["donneur"]).get("parti_apres") == slug:
        assert r["apres"]["tiGuy"] is False, "Ti-Guy rentre au garage et quitte la ville avec la scène"


@pytest.mark.parametrize("cas", [f"{slug}-{partie}" for slug in MISSIONS for partie in ("intro", "fin")])
def test_passer_une_scene_de_mission_a_n_importe_quel_moment(banc, cas):
    """PAUSE à n'importe quel plan tombe au même état que la scène vue jusqu'au bout
    — Ti-Guy rentré, la pièce rendue après une coupe dehors — et le même dé.

    ⚠️ **TOUTES les scènes du catalogue**, et plus quatre cas choisis à la main :
    une mission de plus doit hériter de cette garantie sans qu'on l'inscrive ici."""
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


@pytest.mark.parametrize("slug", MISSIONS)
def test_une_scene_de_mission_ne_tire_aucun_de(banc, slug):
    """Le prochain dé est le même avec les scènes et sans elles (répliques seules).
    ⚠️ Chaque mission du catalogue, et plus la seule m3."""
    def partie(avec):
        return banc("function (L, o) {" + OUTILS + """
            if (!%s) L.B.defs.missions.forEach(function (m) { m.scenes = null; });
            const m = mission(L, '%s');
            partie(L, m.slug); L.graine(1357);
            allerVoir(L, o, m);
            L.Histoire.parler(m.donneur);
            jouerJusquauBout(L, o, 6000);
            const e = etat(L);
            L.Histoire.reussir();
            jouerJusquauBout(L, o, 6000);
            return { x: e.x, y: e.y, restes: e.restes, de: L.B.rng() };
        }""" % ("true" if avec else "false", slug))
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


def test_une_mission_neuve_qui_n_apporte_que_ses_donnees_se_joue(banc):
    """⚠️ **LA PREUVE DU BLOC LEGO, AU BANC** (demande de Martin, 20 sept. 2026).
    Une fiche qui n'écrit QUE ce qui la distingue — son donneur, ses objectifs,
    ses répliques — est posée dans le catalogue du navigateur, et l'on joue son
    intro et sa fin comme celles des autres : elles partent, elles ne sautent
    aucun plan, elles se terminent sans ACTION et sans voix.

    ⚠️ Une promesse qu'on n'essaie pas est une promesse : c'est le seul juge qui
    monte une mission que personne n'a écrite à la main."""
    fiche = dict(NEUVE)
    missions._completer(fiche)
    r = banc("function (L, o) {" + OUTILS + """
        L.B.defs.missions.push(NEUVE);
        const m = mission(L, 'zz');
        partie(L, m.slug);
        allerVoir(L, o, m);
        const offerte = L.Histoire.parler(m.donneur) !== false;
        const intro = L.B.scene, plansIntro = intro ? intro.plans.length : 0;
        const sautesIntro = intro ? (jouerJusquauBout(L, o, 6000), intro.sautes) : null;
        versLaFin(L, m);
        const dites = ecouter(L);
        L.Histoire.reussir();
        const fin = L.B.scene;
        const joue = jouerJusquauBout(L, o, 6000);
        return { offerte: offerte, intro: !!intro, plansIntro: plansIntro, sautesIntro: sautesIntro,
                 fin: !!fin, sautesFin: fin ? fin.sautes : null, n: joue.n, dites: dites,
                 faite: !!L.B.partie.missionsFaites.zz };
    }""".replace("NEUVE", json.dumps(fiche, ensure_ascii=False)))
    assert r["offerte"] and r["intro"], "parler au donneur ne joue pas l'intro de la mission neuve"
    assert r["plansIntro"] >= 3, f"son intro n'a que {r['plansIntro']} plans : ce n'est pas une scène"
    assert r["sautesIntro"] == 0, f"{r['sautesIntro']} plan(s) de son intro n'ont rien trouvé"
    assert r["faite"] and r["fin"], "sa fin ne joue pas sa scène"
    assert r["sautesFin"] == 0, f"{r['sautesFin']} plan(s) de sa fin n'ont rien trouvé"
    assert r["n"] < 6000, "sa fin ne se termine pas sans ACTION ni voix"
    assert len(r["dites"]) == len(fiche["dialogue"]["fin"]), r["dites"]
    assert not any("(AU TÉLÉPHONE)" in qui for qui in r["dites"]), \
        "elle finit chez son donneur : il parle en personne, pas au combiné"


# --- Le tour du propriétaire : ses quatre portes, chacune quand Josée la nomme ---------------

#: Jouer l'intro de m6 dans le bar, image par image, et rendre ce que la caméra a montré.
#: ⚠️ Les portes se résolvent DANS LA VILLE, avant d'entrer : une fois dedans,
#: `Monde.carte` est la pièce.
TOUR_DE_M6 = """function (L, o) {""" + OUTILS + """
        const m = mission(L, 'm6');
        partie(L, m.slug);
        const portes = m.objectifs.map(function (q) {
          const l = L.Histoire.lieuDuPersonnage(q.cible);
          return { slug: q.cible, x: l.x, y: l.y };
        });
        allerVoir(L, o, m);
        const avant = etat(L);
        const debuts = [], vues = portes.map(function () { return { n: 0, premiere: null }; });
        const vrai = L.Hud.dialogue;
        let n = 0;
        L.Hud.dialogue = function () { debuts.push(n); return vrai.apply(null, arguments); };
        const d0 = L.Son.Voix.demandees.length;
        L.Histoire.parler(m.donneur);
        const s = L.B.scene;
        while ((L.B.scene || L.B.cinema) && n < 6000) {
          o.frame(1); n++;
          const sc = L.B.scene;
          // La caméra est LÀ-BAS, et l'écran n'est pas au noir : ce que Martin voit.
          if (!sc || (sc.noir || 0) > 0.2 || !sc.vise) continue;
          portes.forEach(function (p, i) {
            if (Math.hypot(sc.vise.x - p.x, sc.vise.y - p.y) < 8) { vues[i].n++; if (vues[i].premiere === null) vues[i].premiere = n; }
          });
        }
        return { portes: portes.map(function (p) { return p.slug; }), vues: vues, debuts: debuts, sautes: s ? s.sautes : null,
                 images: n, voix: L.Son.Voix.demandees.slice(d0), avant: avant, apres: etat(L) };
    }"""


def test_le_tour_du_proprietaire_montre_ses_quatre_contacts(banc):
    """⚠️ Rouge avant (20 sept. 2026), demande de Martin : « améliore l'animation de la
    mission tour du propriétaire pour voir toutes les cibles, pas juste la première ».
    L'intro de m6 ne filmait que le dépanneur (159 images) alors que Josée nomme quatre
    portes : la cantine, l'usine et le phare ne se voyaient jamais. Chaque contact doit
    être à l'écran (hors du noir) au moins une seconde, dans l'ordre du tour, et pendant la
    réplique qui le nomme — Ti-Paul et Lulu sous la première, Raymonde et Ovila sous la
    seconde."""
    r = banc(TOUR_DE_M6)
    assert r["portes"] == ["tipaul", "lulu", "raymonde", "ovila"]
    assert r["sautes"] == 0, f"{r['sautes']} plan(s) de l'intro n'ont trouvé ni leur lieu ni leur acteur"
    for slug, vue in zip(r["portes"], r["vues"]):
        assert vue["n"] >= 60, f"{slug} : la caméra ne le montre que {vue['n']} images (il en faut 60, une seconde)"
    premieres = [v["premiere"] for v in r["vues"]]
    assert premieres == sorted(premieres), f"le tour n'est pas dans l'ordre : {dict(zip(r['portes'], premieres))}"
    un, deux, trois = r["debuts"]
    for i in (0, 1):
        assert un <= premieres[i] < deux, f"{r['portes'][i]} paraît à l'image {premieres[i]}, hors de la réplique 1 ({un}-{deux})"
    for i in (2, 3):
        assert deux <= premieres[i] < trois, f"{r['portes'][i]} paraît à l'image {premieres[i]}, hors de la réplique 2 ({deux}-{trois})"
    # Et le bar est rendu tel qu'on l'a laissé.
    for cle in ("x", "y", "piece", "carte", "moi"):
        assert r["apres"][cle] == r["avant"][cle], f"{cle} : {r['avant'][cle]} -> {r['apres'][cle]}"


ffprobe_present = pytest.mark.skipif(shutil.which("ffprobe") is None, reason="ffprobe n'est pas installé : ce juge mesure des mp3")


def _duree_s(chemin) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(chemin)], capture_output=True, text=True).stdout)


@ffprobe_present
def test_le_tour_du_proprietaire_laisse_finir_ses_repliques(banc, racine):
    """⚠️ Rouge avant (20 sept. 2026) : la coupe qui portait la réplique 1 ne tenait que 230
    images, la voix en dure 360 — la réplique 2 la coupait à l'image 229, en plein « ma sœur
    Lulu à la cantine ». Une réplique suivante ne part qu'une fois la voix précédente finie,
    avec de quoi absorber un mp3 qui met du temps à arriver (`CHARGEMENT`).

    ⚠️ La durée est celle du FICHIER : si une voix est régénérée plus longue, ce juge dit de
    recaler `scenes.intro` de `m6.py` — c'est ce qu'il garde."""
    CHARGEMENT = 30        # images : une demi-seconde
    r = banc(TOUR_DE_M6)
    assert len(r["debuts"]) == len(r["voix"]) == 3, (r["debuts"], r["voix"])
    for i in (0, 1):
        voix = _duree_s(racine / "static" / "audio" / f"histoire-{r['voix'][i]}.mp3") * 60
        place = r["debuts"][i + 1] - r["debuts"][i]
        assert place >= math.ceil(voix) + CHARGEMENT, (
            f"{r['voix'][i]} : {voix:.0f} images de voix, mais la réplique suivante part {place} images après la sienne")
