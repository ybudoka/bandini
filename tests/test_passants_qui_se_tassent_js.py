"""Des passants qui se tassent au klaxon (Martin, 30 sept. 2026) : « réduisons le nombre de
morts : si un piéton se fait klaxonner, il se déplace, laisse le véhicule passer et poursuit sa
route. Les véhicules n'écrasent qu'exceptionnellement les piétons. »

La sonde d'avant : six graines, 6 000 images chacune, le joueur immobile — **12 passants morts,
tous sous un char de PNJ** (l'autobus d'abord, puis le trafic). Environ un par minute.
"""

import pytest

#: La scène : une rue à une voie par sens, vidée de ses chars et de ses passants, le joueur
#: sur le trottoir d'en face (la scène reste dans sa bulle). `nettoyer` retire, à chaque image,
#: tout ce qui naît autour et n'est pas de la scène.
SCENE = """
    L.Jeu.commencer();
    const T = L.TT;
    const b = o.boulevard(false);
    const j = L.B.joueur;
    j.x = b.x + 5 * T; j.y = b.y + 4 * T;
    L.B.entites.filter(function (e) { return e.type === 'vehicule' || e.type === 'pieton'; })
      .forEach(function (e) { L.Entites.retirer(e); });
    L.Entites.indexer();
    function nettoyer(garder) {
      L.B.entites.filter(function (e) {
        return (e.type === 'vehicule' || e.type === 'pieton') && garder.indexOf(e) < 0;
      }).forEach(function (e) { L.Entites.retirer(e); });
    }
"""


@pytest.fixture(scope="module")
def tasses(banc):
    """Deux scènes sur la même rue : un passant planté au milieu de la voie, puis un
    passant qui MARCHE dans la voie vers un point plus loin. Un char du trafic arrive
    derrière chacun."""
    return banc("""function (L, o) {""" + SCENE + """
        const out = {};
        function scene(prepare) {
            const v = L.Vehicules.creer('auto', b.x, b.y, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
            v.vitesse = 1.2;
            const p = L.Entites.creerPieton(b.x + 6 * T, b.y, null);
            prepare(p);
            L.Entites.indexer();
            const vie = p.vie;
            let klaxonA = null, tasseA = null, passeA = null, ecart = 0, arriveA = null, etatApres = null;
            let tasseSur = null;
            for (let i = 0; i < 480; i++) {
                o.frame(1);
                nettoyer([v, p]);
                if (klaxonA === null && v.klaxonT > 0) klaxonA = i;
                if (tasseA === null && p.etat === 'tasse') { tasseA = i; tasseSur = L.Monde.estChaussee(Math.floor(p.x / T), Math.floor(p.y / T)); }
                ecart = Math.max(ecart, Math.abs(p.y - b.y));
                if (passeA === null && v.x > p.x + 24) passeA = i;
                if (passeA !== null && etatApres === null && i > passeA + 30) etatApres = p.etat;
                if (p.cap && arriveA === null && Math.hypot(p.cap.x - p.x, p.cap.y - p.y) <= 14) arriveA = i;
            }
            const r = { klaxonA: klaxonA, tasseA: tasseA, passeA: passeA, ecart: Math.round(ecart),
                        etatApres: etatApres, etatFin: p.etat, vivant: p.vivant, blesse: p.vie < vie,
                        minuterie: p.minuterie, arriveA: arriveA, cap: p.cap };
            L.Entites.retirer(v); L.Entites.retirer(p); L.Entites.indexer();
            return r;
        }
        // Planté : il attend quelqu'un au milieu de la rue.
        out.plante = scene(function (p) { p.etat = 'arret'; p.minuterie = 5000; });
        // Il marche dans la voie, vers un point huit tuiles plus loin.
        out.marche = scene(function (p) {
            p.etat = 'cap'; p.cap = { x: b.x + 14 * T, y: b.y }; p.capT = 0;
        });
        out.capVoulu = { x: b.x + 14 * T, y: b.y };
        return out;
    }""")


def test_le_trafic_klaxonne_tot_un_passant_dans_sa_voie(tasses):
    """Avant, le char attendait 200 images de patience (3,3 s) avant de klaxonner — puis il
    forçait. Il klaxonne maintenant dès qu'il voit le passant dans son couloir."""
    r = tasses["plante"]
    assert r["klaxonA"] is not None, "le char n'a jamais klaxonné le passant planté devant lui"
    assert r["klaxonA"] < 150, f"le char a klaxonné à l'image {r['klaxonA']} : c'est la patience, pas le klaxon"


def test_klaxonne_un_passant_plante_se_tasse_et_reprend(tasses):
    r = tasses["plante"]
    assert r["tasseA"] is not None, "klaxonné, le passant n'a pas bougé"
    assert r["tasseA"] >= r["klaxonA"], "il s'est tassé avant d'être klaxonné"
    assert r["ecart"] >= 10, f"il ne s'est écarté que de {r['ecart']} px : le char ne passe pas"
    assert r["passeA"] is not None, "le char n'a jamais passé le passant"
    assert r["vivant"] and not r["blesse"], "le char a touché le passant qui se tassait"
    # ⚠️ IL REPREND CE QU'IL FAISAIT : son état, et le temps qu'il lui restait.
    assert r["etatApres"] == "arret", f"après le passage, il est « {r['etatApres']} » au lieu de reprendre"
    assert r["minuterie"] > 4000, f"il a perdu son attente ({r['minuterie']})"


def test_klaxonne_un_passant_qui_marche_poursuit_sa_route(tasses):
    """Le cœur de la demande : il se tasse, laisse passer, et POURSUIT SA ROUTE."""
    r = tasses["marche"]
    assert r["tasseA"] is not None, "klaxonné, le passant qui marchait dans la voie n'a pas bougé"
    assert r["passeA"] is not None, "le char n'a jamais passé le passant"
    assert r["vivant"] and not r["blesse"], "le char a touché le passant"
    assert r["cap"] == tasses["capVoulu"], f"il a oublié où il allait : {r['cap']}"
    assert r["arriveA"] is not None and r["arriveA"] > r["passeA"], "il n'a pas fini sa route"


def test_un_char_de_pnj_ne_tue_qu_une_fois_sur_dix(banc):
    """⚠️ Le filet : un passant qui surgit sous un char de PNJ (il fuit, il traverse pour sauter
    sur le joueur) est renversé, blessé, et se relève — il ne meurt qu'une fois sur dix, à
    l'empreinte du char et du passant (aucun dé : `B.rng` décalerait la ville). Au volant, le
    joueur tue comme avant, et un char vide qui roule tout seul aussi."""
    r = banc("""function (L, o) {""" + SCENE + """
        function frapper(conducteur) {
            let morts = 0, riposte = 0, fuient = 0, enfants = 0;
            const crimes = L.B.crimes.length;
            for (let k = 0; k < 60; k++) {
                const v = L.Vehicules.creer('auto', b.x, b.y, 0, { conducteur: conducteur, etat: 'roule', sens: '>' });
                const p = L.Entites.creerPieton(b.x + v.def.longueur / 2 + 2, b.y, null);
                p.etat = 'flane';
                v.vx = 4; v.vy = 0; v.vitesse = 4;
                L.Entites.indexer();
                L.Vehicules.heurterPietons(v);
                // ⚠️ ET IL SURVIT POUR DE BON : un renversement fait saigner, et le saignement mord au
                // bout d'une seconde. Laissé à 1 PV, l'épargné mourait une seconde plus tard — la sonde
                // comptait autant de morts qu'avant, un char de moins au compteur.
                const etat = p.etat, ensuite = p.avantTasse && p.avantTasse.etat;
                for (let t = 0; t < 150; t++) { p.t++; L.Entites.majPieton(p); }
                // Un enfant n'est que bousculé (`intouchable`) : jamais renversé, il n'entre pas dans le compte.
                if (p.intouchable) enfants++;
                else if (!p.vivant) morts++;
                else if (etat === 'attaque_joueur') riposte++;
                // Il sort du couloir du char AVANT de détaler (`tasse`, puis `fuit`) : droit devant, il
                // se refaisait frapper par le même char.
                else if (etat === 'tasse' && ensuite === 'fuit' && Math.abs(p.y - b.y) > v.def.largeur / 2 + p.r) fuient++;
                L.Entites.retirer(v); L.Entites.retirer(p); nettoyer([]); L.Entites.indexer();
            }
            return { morts: morts, riposte: riposte, fuient: fuient, enfants: enfants, crimes: L.B.crimes.length - crimes };
        }
        return { trafic: frapper('trafic'), ligne: frapper('ligne'), vide: frapper(null) };
    }""")
    for qui in ("trafic", "ligne"):
        t = r[qui]
        assert 1 <= t["morts"] <= 12, f"{qui} : {t['morts']} morts sur 60 coups à 4 px/image (une fois sur dix voulu)"
        assert t["riposte"] == 0, f"{qui} : {t['riposte']} passants renversés par un PNJ s'en prennent au joueur"
        assert t["fuient"] == 60 - t["enfants"] - t["morts"], f"{qui} : un survivant ne sort pas du couloir avant de détaler ({t})"
        assert t["crimes"] == 0, f"{qui} : un renversement par un PNJ est compté comme un crime"
    # Pas 60 : un enfant n'est que bousculé (`intouchable`), et un costaud encaisse 4 px/image.
    assert r["vide"]["morts"] >= 50, f"un char vide qui roule tout seul ne tue plus ({r['vide']}) : ce n'est pas un PNJ"


def test_le_forcage_bouscule_il_ne_renverse_pas(banc, paquet):
    """Un char qui perd patience force le passage à 25 % de sa vitesse max : pour le coupé sport,
    le cabriolet et la moto, c'est déjà la vitesse qui renverse (1,2 à 1,3 px/image). Devant un
    passant, il pousse au pas : il bouscule."""
    ph = paquet["conduite"]["physique"]
    r = banc("""function (L, o) {""" + SCENE + """
        const out = {};
        for (const slug of ['sport', 'cabriolet', 'moto']) {
            const v = L.Vehicules.creer(slug, b.x, b.y, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
            // Planté pour de bon : un donneur tient son poste, il ne se tasse pas.
            const p = L.Entites.creerPieton(b.x + 5 * T, b.y, null);
            p.etat = 'fige';
            L.Entites.indexer();
            const vie = p.vie;
            let vMax = 0, force = false;
            for (let i = 0; i < 600; i++) {
                o.frame(1);
                nettoyer([v, p]);
                if (v.force > 0) force = true;
                // Tant que le passant est DEVANT le nez, à moins d'une tuile et demie.
                const devant = (p.x - v.x) * Math.cos(v.angle) + (p.y - v.y) * Math.sin(v.angle);
                if (devant > 0 && devant < v.def.longueur / 2 + 24) vMax = Math.max(vMax, Math.hypot(v.vx, v.vy));
            }
            out[slug] = { force: force, vMax: vMax, blesse: p.vie < vie, vivant: p.vivant };
            L.Entites.retirer(v); L.Entites.retirer(p); L.Entites.indexer();
        }
        return out;
    }""")
    for slug, t in r.items():
        assert t["vivant"] and not t["blesse"], f"{slug} : le forçage a blessé le passant planté"
        assert t["force"], f"{slug} : le char n'a jamais forcé (le juge ne mord pas)"
        assert t["vMax"] < ph["renverse_vitesse_min"], f"{slug} : il pousse le passant à {t['vMax']:.2f} px/image"
