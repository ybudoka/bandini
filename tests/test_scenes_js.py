"""Le metteur en scène, au banc : chaque plan joue, une scène passée tombe au même
endroit qu'une scène vue, elle se termine toujours, et elle ne tire aucun dé.

⚠️ Ces juges jouent une scène d'ESSAI qui n'est dans aucun catalogue : c'est le
moteur qu'on juge, pas une scène. L'ouverture, elle, a ses treize juges
(`test_ouverture.py`), qui n'ont pas bougé d'une lettre quand elle est passée dans
le vocabulaire.
"""

#: Une scène qui passe par TOUS les types, autour du joueur : `ici` (où il est),
#: `rue` (la rue la plus proche, avec son sens), `ailleurs` (le garage). Un
#: figurant (`figurant`) marche puis rentre ; un autre (`cache`) sort d'une porte.
ESSAI = """
  function preparer(L) {
    L.Jeu.commencer();
    L.B.partie.heure = 0.5;
    const j = L.B.joueur;
    const rue = L.Histoire.tuileDeRue(j.x, j.y, 12);
    const garage = L.Histoire.lieu('garage');
    const figurant = L.Entites.creerPieton(j.x + 30, j.y, L.Entites.archetype(L.B.defs.pietons.catalogue[0].slug));
    figurant.personnage = 'figurant'; figurant.etat = 'fige'; figurant.intouchable = true;
    const cache = L.Entites.creerPieton(j.x - 30, j.y, L.Entites.archetype(L.B.defs.pietons.catalogue[0].slug));
    cache.personnage = 'cache'; cache.etat = 'fige'; cache.intouchable = true;
    L.Entites.indexer();
    return { j: j, rue: rue, garage: garage, figurant: figurant, cache: cache };
  }
  const SCENE = [
    { type: 'coupe', vers: 'ailleurs', ferme: 10, ouvre: 10, tient: 10 },
    { type: 'son', sfx: 'pas' },
    { type: 'camera', vers: 'ici' },
    { type: 'conduire', acteur: 'char', vehicule: 'auto', couleur: '#aa3322', vers: 'rue', depuis: 120, duree: 30, courbe: 'freine', fumee: 3, portiere: true },
    { type: 'sortir', acteur: 'cache', de: 'ici', vers: 'rue' },
    { type: 'marcher', acteur: 'figurant', vers: 'rue', duree: 20, ensemble: true },
    { type: 'camera', vers: 'rue', lissage: 0.1 },
    { type: 'geste', acteur: 'joueur', geste: 'montrer', vers: 'rue', duree: 20 },
    { type: 'marcher', acteur: 'joueur', vers: 'rue', duree: 15 },
    { type: 'dire', ensemble: true },
    { type: 'titre', texte: 'ESSAI', sous: 'LE BANC', monte: 5, tenu: 20, descend: 5 },
    { type: 'entrer', acteur: 'figurant', dans: 'ici', duree: 10 },
    { type: 'conduire', acteur: 'char', part: 120, duree: 20, courbe: 'accelere', retirer: true },
    { type: 'camera', vers: 'ici', duree: 15, courbe: 'droite' },
    { type: 'attendre', duree: 5 },
  ];
  function lancer(L, p) {
    const lignes = [{ qui: 'narrateur', texte: 'Une phrase du banc.', slug: 'banc-1', telephone: false },
                    { qui: 'narrateur', texte: 'Et une deuxième.', slug: 'banc-2', telephone: false }];
    return L.Scenes.jouer(SCENE, {
      lieux: { ici: { x: p.j.x, y: p.j.y }, rue: p.rue, ailleurs: p.garage },
      lignes: lignes, fin: function () { p.finie = (p.finie || 0) + 1; },
    });
  }
  function etat(L, p) {
    const j = L.B.joueur;
    return { scene: !!L.B.scene, cinema: !!L.B.cinema, x: j.x, y: j.y, dessine: j.dessine, geste: j.geste || null,
             entites: L.B.entites.length, chars: L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.couleur === '#aa3322'; }).length,
             figurant: L.B.entites.indexOf(p.figurant) >= 0, cache: p.cache.dessine !== false,
             camera: [Math.round(L.B.cam.x), Math.round(L.B.cam.y)], finie: p.finie || 0,
             moteur: L.Son.boucleActive('moteur') };
  }
"""


def test_chaque_plan_se_joue_et_la_scene_rend_la_ville(banc):
    r = banc("function (L, o) {" + ESSAI + """
        const p = preparer(L);
        const avant = { x: p.j.x, y: p.j.y, entites: L.B.entites.length, de: null };
        const s = lancer(L, p);
        const cacheAuDebut = p.cache.dessine;
        const vu = { noir: 0, sauts: 0, char: 0, figurantBouge: false, geste: null, cinema: false, titre: 0,
                     bande: false, cache: false, camera: new Set() };
        let n = 0;
        const fx = p.figurant.x;
        while (L.B.scene && n < 2000) {
            vu.noir = Math.max(vu.noir, s.noir);
            vu.titre = Math.max(vu.titre, s.titre);
            if (L.B.entites.some(function (e) { return e.couleur === '#aa3322'; })) vu.char++;
            if (p.figurant.x !== fx) vu.figurantBouge = true;
            if (p.j.x !== avant.x || p.j.y !== avant.y) vu.joueurBouge = true;
            if (p.j.geste) vu.geste = L.Entites.nomDePose(p.j);
            if (L.B.cinema) vu.cinema = true;
            if (p.cache.dessine !== false) vu.cache = true;
            vu.camera.add(Math.round(L.B.cam.x) + ',' + Math.round(L.B.cam.y));
            if (s.titre > 0.5 && !vu.bande) {
                o.ctx.traces = []; L.Hud.dessiner();
                vu.bande = o.ctx.traces.some(function (q) { return q[0] === 0 && q[1] === 50 && q[2] === L.VW && q[3] === 68; });
                o.ctx.traces = null;
            }
            L.Scenes.maj(); n++;
        }
        const apres = etat(L, p);
        vu.camera = vu.camera.size;
        return { n: n, vu: vu, apres: apres, avant: avant, cacheAuDebut: cacheAuDebut, marche: vu.joueurBouge };
    }""")
    vu, apres, avant = r["vu"], r["apres"], r["avant"]
    assert r["n"] < 2000 and not apres["scene"], "la scène d'essai ne se termine pas"
    assert apres["finie"] == 1, "`fin` s'appelle une fois, et une seule"
    assert vu["noir"] >= 0.99, "coupe : pas de noir plein"
    assert vu["camera"] >= 3, "la caméra n'a pas voyagé"
    assert vu["char"] > 30, "conduire : le char n'a pas existé le temps de ses plans"
    assert vu["figurantBouge"], "marcher : le figurant n'a pas bougé"
    assert vu["geste"] and vu["geste"].startswith("geste_montrer_"), vu["geste"]
    assert vu["cinema"], "dire : aucune réplique"
    assert vu["titre"] > 0.99 and vu["bande"], "titre : le carton ne s'est pas inscrit"
    assert vu["cache"], "sortir : celui qui sort ne s'est pas montré"
    assert r["cacheAuDebut"] is False, "sortir : celui qui va sortir était déjà là avant"
    assert r["marche"], "marcher : le joueur n'a pas bougé pendant la scène"
    # Et la ville est rendue.
    assert apres["x"] == avant["x"] and apres["y"] == avant["y"], "la scène a déplacé le joueur"
    assert apres["dessine"] is True and apres["geste"] is None
    assert apres["chars"] == 0, "le char de la scène est resté en ville"
    assert apres["figurant"] is False, "entrer : le figurant est rentré, il quitte la ville"
    assert apres["cache"] is True
    assert apres["entites"] == avant["entites"] - 1, "rien d'autre ne naît ni ne meurt qu'avec les plans"
    assert apres["cinema"] is False and apres["moteur"] is False


def test_passer_a_n_importe_quel_moment_tombe_au_meme_etat(banc):
    """⚠️ PAUSE à n'importe quel plan tombe exactement où la scène vue jusqu'au bout
    nous aurait laissés — et le prochain dé est le même, vue ou passée."""
    r = banc("function (L, o) {" + ESSAI + """
        const sorties = [];
        for (const k of [0, 1, 12, 35, 60, 90, 130, -1]) {
            L.Jeu.retourTitre();
            L.graine(31337);
            const p = preparer(L);
            lancer(L, p);
            let n = 0;
            if (k < 0) { while (L.B.scene && n < 2000) { L.Scenes.maj(); n++; } }
            else { for (; n < k && L.B.scene; n++) L.Scenes.maj(); L.Scenes.passer(); }
            const e = etat(L, p);
            delete e.camera;
            e.de = L.B.rng();
            sorties.push({ k: k, e: e });
        }
        return sorties;
    }""")
    reference = r[-1]["e"]
    assert reference["finie"] == 1
    for s in r[:-1]:
        assert s["e"] == reference, f"passée à l'image {s['k']} : {s['e']} au lieu de {reference}"


def test_une_scene_ne_tire_aucun_de(banc):
    """LE JUGE CENTRAL, étendu à toute scène : le prochain dé est le même avec la
    scène vue jusqu'au bout et sans scène du tout."""
    r = banc("function (L, o) {" + ESSAI + """
        function mesurer(avec) {
            L.Jeu.retourTitre();
            L.graine(4242);
            const p = preparer(L);
            if (avec) { lancer(L, p); let n = 0; while (L.B.scene && n < 2000) { L.Scenes.maj(); n++; } }
            return L.B.rng();
        }
        return { sans: mesurer(false), avec: mesurer(true) };
    }""")
    assert r["avec"] == r["sans"], "la scène a tiré un dé : tout ce qui naît ensuite tomberait ailleurs"


def test_une_scene_se_termine_toujours(banc):
    """Un lieu qui ne se trouve pas, un acteur qui n'existe pas : le plan saute,
    jamais attendu. Et une scène ne tient pas plus de trois secondes après son
    dernier plan parti."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const scenes = {
            introuvable: [
                { type: 'camera', vers: 'nulle_part', duree: 500 },
                { type: 'marcher', acteur: 'personne', vers: 'nulle_part', duree: 500 },
                { type: 'conduire', acteur: 'fantome', part: 100, duree: 500 },
                { type: 'dire' },
                { type: 'geste', acteur: 'personne', geste: 'hausser' },
            ],
            interminable: [{ type: 'attendre', duree: 100000 }],
        };
        const sortie = {};
        for (const nom in scenes) {
            L.Scenes.jouer(scenes[nom], { lieux: {} });
            let n = 0;
            while (L.B.scene && n < 5000) { L.Scenes.maj(); n++; }
            sortie[nom] = { n: n, reste: !!L.B.scene };
        }
        return { sortie: sortie, apres: L.Scenes.APRES_LE_DERNIER_MOT };
    }""")
    assert r["sortie"]["introuvable"]["reste"] is False and r["sortie"]["introuvable"]["n"] <= 1, r
    assert r["sortie"]["interminable"]["reste"] is False, "une scène qui ne finit jamais fige la ville pour toujours"
    assert r["sortie"]["interminable"]["n"] <= r["apres"] + 1, r


def test_une_scene_fige_la_ville_et_pause_la_passe(banc):
    """La ville ne tourne pas pendant une scène, et PAUSE la passe au lieu d'ouvrir
    le menu — comme pour l'ouverture, mais pour n'importe quelle scène."""
    r = banc("function (L, o) {" + ESSAI + """
        const p = preparer(L);
        lancer(L, p);
        const t0 = L.B.t;
        o.frame(40);
        const horloge = L.B.t - t0, pendant = !!L.B.scene;
        o.tape('Escape', 2);
        return { horloge: horloge, pendant: pendant, apres: !!L.B.scene, etat: L.B.etat };
    }""")
    assert r["pendant"] and r["horloge"] == 0, "la ville a tourné pendant la scène"
    assert r["apres"] is False and r["etat"] == "jeu", "PAUSE passe la scène, elle n'ouvre pas le menu"


def test_les_six_gestes_se_dessinent_sur_le_sprite_de_tout_le_monde(banc):
    r = banc("""function (L, o) {
        const sortie = {};
        for (const geste of ['montrer', 'donner', 'prendre', 'bras_croises', 'hausser', 'telephone']) {
            for (const face of ['bas', 'haut', 'droite', 'gauche']) {
                const e = { sprite: 'joueur', face: face, geste: geste, anim: { dist: 0 }, vx: 0, vy: 0, swaps: { c: '#8e44ad' } };
                const img = L.Entites.imageDe(e);
                const immobile = L.Entites.imageDe({ sprite: 'joueur', face: face, anim: { dist: 0 }, vx: 0, vy: 0, swaps: { c: '#8e44ad' } });
                sortie[geste + '/' + face] = { pose: img.pose, different: img.canvas !== immobile.canvas };
            }
        }
        // Un sprite qui n'a pas le geste retombe sur sa face, il ne disparaît pas.
        const autre = L.Entites.imageDe({ sprite: 'racoleuse', face: 'bas', geste: 'montrer', anim: { dist: 0 }, vx: 0, vy: 0 });
        return { gestes: sortie, repli: autre && autre.pose };
    }""")
    for cle, g in r["gestes"].items():
        geste, face = cle.split("/")
        assert g["pose"] == f"geste_{geste}_{face}", (cle, g)
        assert g["different"], f"{cle} : la pose immobile"
    assert r["repli"] == "bas"


def test_la_mission_est_posee_avant_son_intro(banc):
    """⚠️ Quand Marco parle de son taxi, le taxi existe : la scène d'intro pourra
    aller le voir. Et c'est la même partie qu'avant — le prochain dé ne bouge pas,
    et le titre et l'objectif s'annoncent à la fin de l'intro, pas dessous."""
    def partie(avec_intro):
        return banc("""function (L, o) {
            L.Jeu.commencer();
            L.graine(777);
            L.B.partie.missionsFaites.m1 = 1; L.B.partie.missionsFaites.m2 = 1;
            const vus = {};
            if (%s) {
                L.Histoire.parler('marco');
                vus.pendant = { mission: L.B.partie.mission && L.B.partie.mission.slug, cinema: !!L.B.cinema,
                                taxi: !!(L.B.mission && L.B.mission.vehicule), msg: L.B.msg || '' };
                // L'intro est une SCENE (2e vague) : elle continue apres ses mots.
                let n = 0;
                while ((L.B.cinema || L.B.scene) && n < 5000) {
                    if (L.B.cinema) L.Histoire.suivante();
                    if (L.B.scene) L.Scenes.maj();
                    n++;
                }
                vus.msg = L.B.msg || '';
            } else {
                L.Histoire.commencer('m3');
            }
            const m = L.Histoire.courante();
            return { vus: vus, etape: L.B.partie.mission.etape, texte: m.objectifs[0].texte, titre: m.titre.toUpperCase(),
                     taxi: !!L.B.mission.vehicule, de: L.B.rng(), entites: L.B.entites.length };
        }""" % ("true" if avec_intro else "false"))
    avec, sans = partie(True), partie(False)
    assert avec["vus"]["pendant"]["cinema"] is True, "l'intro ne s'est pas dite"
    assert avec["vus"]["pendant"]["mission"] == "m3", "pendant l'intro, la mission n'est pas encore posée"
    assert avec["vus"]["pendant"]["taxi"] is True, "pendant l'intro, le taxi n'existe pas : la scène filmerait un coin vide"
    assert avec["vus"]["pendant"]["msg"] not in (avec["texte"], avec["titre"]), "l'objectif s'affiche sous l'intro"
    assert avec["vus"]["msg"] == avec["texte"], "à la fin de l'intro, l'objectif s'annonce"
    assert avec["de"] == sans["de"] and avec["entites"] == sans["entites"], "poser avant l'intro a déplacé un dé"
