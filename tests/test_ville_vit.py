"""M12, 1re vague — le rythme de la ville : les feux clignotent la nuit, les
heures de pointe ont une direction, et la chaussée a des nids-de-poule.

⚠️ Les trois tiennent la même promesse : **la ville change d'une heure à
l'autre sans qu'on regénère une seule tuile**. Tout vient de la fiche, et le
navigateur n'invente rien.
"""

import itertools

import pytest

from app import carte, pietons, vehicules


def dans(h, debut, fin):
    return (debut <= h < fin) if debut < fin else (h >= debut or h < fin)


# --- Les feux qui clignotent la nuit -----------------------------------------


def test_les_feux_ne_clignotent_que_la_nuit():
    """⚠️ Des feux qui clignotent pendant que la rue est encore pleine, ce
    n'est pas la nuit, c'est une panne. La fenêtre du clignotant doit donc
    tomber **dans** la nuit du rythme (`DISTRICTS[].rythme`, 0,82 → 0,25) — la
    même nuit qui vide la ville de ses passants et de ses chars."""
    t = vehicules.TRAFIC
    depuis, jusqu_a = t["clignotant_depuis"], t["clignotant_jusqu_a"]
    assert 0 <= depuis < 1 and 0 <= jusqu_a < 1
    assert t["clignotant_images"] > 0
    # La nuit du rythme, telle que `Monde.rythme` la lit.
    for h in (depuis, (depuis + 1.0) / 2 % 1.0, jusqu_a - 0.01):
        assert dans(h % 1.0, 0.82, 0.25), f"il clignote à {h % 1.0:.2f}, et il fait encore jour"
    # ... et il y a une vraie nuit AVANT la bascule : sans elle, on n'aurait
    # jamais vu un tricolore tourner sous les lampadaires allumés.
    assert dans(depuis - 0.02, 0.82, 0.25), "le clignotant commence dès la tombée du jour"


def test_la_nuit_l_artere_clignote_jaune_et_la_rue_secondaire_rouge(banc, paquet):
    """⚠️ **`feuDeCirculation` reste LA SEULE SOURCE** : le dessin de la
    lanterne en découle, `feuVert` en découle, et le trafic obéit à `feuVert`.
    Un clignotant ne peut donc pas montrer une couleur que le char ne respecte
    pas — c'est la même phrase lue deux fois, jamais deux phrases."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const t = L.B.defs.conduite.trafic;
        const out = { jour: [], nuit: [] };
        const inters = L.Monde.carte.intersections.filter(function (i) { return i.feux; }).slice(0, 40);
        [['jour', 0.5], ['nuit', (t.clignotant_depuis + 0.04) % 1]].forEach(function (p) {
            L.B.partie.heure = p[1];
            inters.forEach(function (i) {
                const ns = L.Monde.feuDeCirculation(i, '^'), eo = L.Monde.feuDeCirculation(i, '>');
                out[p[0]].push({ ns: ns, eo: eo, l: i.l, h: i.h,
                                 vertNS: L.Monde.feuVert(i, '^'), vertEO: L.Monde.feuVert(i, '>'),
                                 pieton: L.Monde.feuPieton(i, '^') });
            });
        });
        out.clignoteLaNuit = (L.B.partie.heure = (t.clignotant_depuis + 0.04) % 1, L.Monde.feuxClignotent());
        L.B.partie.heure = 0.5;
        out.clignoteLeJour = L.Monde.feuxClignotent();
        return out;
    }""")
    assert r["clignoteLaNuit"] is True and r["clignoteLeJour"] is False
    assert len(r["nuit"]) >= 10, "trop peu de croisements à feux : %s" % len(r["nuit"])
    for i in r["jour"]:
        assert i["ns"] in ("vert", "jaune", "rouge") and i["eo"] in ("vert", "jaune", "rouge"), i
        assert i["pieton"] != "aucun", "un feu piéton éteint en plein jour"
    for i in r["nuit"]:
        # L'artère est la rue la plus LARGE : `l` est la largeur de la rue
        # nord-sud, `h` celle de l'est-ouest.
        artere, secondaire = ("ns", "eo") if i["l"] >= i["h"] else ("eo", "ns")
        assert i[artere] == "clignote_jaune", f"l'artère ne clignote pas jaune : {i}"
        assert i[secondaire] == "clignote_rouge", f"la rue secondaire ne clignote pas rouge : {i}"
        # ⚠️ Et le trafic lit la MÊME phrase : le jaune clignotant laisse
        # passer, le jaune FIXE non — ce n'est pas la même chose.
        assert i["vertNS" if artere == "ns" else "vertEO"] is True, f"l'artère s'arrête à son clignotant : {i}"
        assert i["vertNS" if secondaire == "ns" else "vertEO"] is False, i
        # Le bonhomme s'éteint avec le cycle : on traverse à vue.
        assert i["pieton"] == "aucun", f"un feu piéton qui tourne encore pendant que les chars clignotent : {i}"


def test_au_clignotant_rouge_le_trafic_s_arrete_puis_repart(banc, paquet):
    """⚠️ **Un clignotant n'est pas un mur.** Le rouge qui bat se lit comme un
    STOP : on s'immobilise, puis on passe. Sans cette règle, le trafic de nuit
    attendait la fin des temps devant un feu qui ne redeviendrait jamais vert
    — et la ville de nuit se serait figée d'un bloc."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(23);
        const t = L.B.defs.conduite.trafic;
        L.B.partie.heure = (t.clignotant_depuis + 0.04) % 1;
        const j = L.B.joueur, d = o.boulevard ? o.boulevard() : o.ligneDroite();
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        o.frame(900);
        // Qui roule, qui est planté ? On suit chaque char du trafic et on garde
        // sa plus longue immobilité d'affilée.
        const plantes = new Map();
        let pire = 0, vus = 0, roulants = 0;
        for (let i = 0; i < 900; i++) {
            o.frame(1);
            for (const e of L.B.entites) {
                if (e.type !== 'vehicule' || e.conducteur !== 'trafic') continue;
                const n = Math.abs(e.vitesse) < 0.05 ? (plantes.get(e) || 0) + 1 : 0;
                plantes.set(e, n);
                if (n > pire) pire = n;
            }
        }
        for (const e of L.B.entites) {
            if (e.type !== 'vehicule' || e.conducteur !== 'trafic') continue;
            vus++;
            if (Math.abs(e.vitesse) > 0.2) roulants++;
        }
        return { pire: pire, vus: vus, roulants: roulants, arret: t.arret_images,
                 cycle: 2 * (t.feu_vert_images + t.feu_orange_images) };
    }""")
    assert r["vus"] >= 2, "pas de trafic la nuit : le juge ne mesure rien (%s)" % r
    assert r["roulants"] >= 1, "tout le trafic de nuit est à l'arrêt : %s" % r
    # ⚠️ La borne est le CYCLE d'un feu : au clignotant on s'arrête le temps
    # d'un STOP, pas le temps d'un feu. Avant la règle, un char planté devant
    # un clignotant rouge y restait les 900 images du juge.
    assert r["pire"] < r["cycle"], "un char reste planté %s images la nuit : %s" % (r["pire"], r)


# --- Les heures de pointe ----------------------------------------------------


def test_la_fiche_des_heures_de_pointe_se_tient():
    p = vehicules.TRAFIC["pointe"]
    for nom in ("matin", "soir"):
        debut, fin = p[nom]
        assert 0 <= debut < fin < 1, f"{nom} : {p[nom]}"
    assert p["matin"][1] <= p["soir"][0], "le matin et le soir se chevauchent"
    # ⚠️ `penchant` est une PART, pas une consigne : le reste du trafic tire au
    # sort comme toujours. À 1, toute la ville roule dans le même sens — ce
    # n'est plus une heure de pointe, c'est une évacuation.
    assert 0 < p["penchant"] < 0.7
    assert p["vers"] in {d["slug"] for d in carte.DISTRICTS}


def test_le_matin_le_trafic_converge_et_le_soir_il_se_disperse(banc, paquet):
    """⚠️ **Le rythme dit COMBIEN de chars roulent ; il ne dit pas OÙ ils
    vont.** Et on ne touche pas au champ de direction, qui est fixe et jugé :
    on pondère le choix de sortie. Le juge mesure ce que ça change — la
    distance au cœur de la ville que chaque sortie choisie rapproche ou
    éloigne, sur des centaines de tirages."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const t = L.B.defs.conduite.trafic, p = t.pointe;
        const c = L.Monde.coeurDeLaVille();
        const heures = { matin: (p.matin[0] + p.matin[1]) / 2,
                         soir: (p.soir[0] + p.soir[1]) / 2,
                         creux: (p.matin[1] + p.soir[0]) / 2 };
        const out = { penchants: {}, gains: {} };
        for (const nom in heures) {
            L.B.partie.heure = heures[nom];
            out.penchants[nom] = L.Vehicules.pointeDuMoment();
            // On rejoue le choix de sortie sur une grille de croisements et on
            // mesure, en moyenne, si la sortie retenue RAPPROCHE du coeur.
            L.graine(5);
            let somme = 0, n = 0;
            const inters = L.Monde.carte.intersections.slice(0, 60);
            for (const i of inters) {
                const tx = i.x + Math.floor(i.l / 2), ty = i.y + Math.floor(i.h / 2);
                for (let k = 0; k < 6; k++) {
                    const v = L.Vehicules.creer('auto', tx * L.TT + 8, ty * L.TT + 8, 0,
                                                { conducteur: 'trafic', etat: 'roule', sens: '>' });
                    if (!v) continue;
                    v.sortie = null;
                    const avant = Math.hypot(v.x - c.x, v.y - c.y);
                    const cible = L.Vehicules.prochaineCible(v);
                    if (cible) {
                        somme += avant - Math.hypot(cible.x - c.x, cible.y - c.y);
                        n++;
                    }
                    L.Entites.retirer(v);
                }
            }
            out.gains[nom] = n ? somme / n : 0;
        }
        return out;
    }""")
    p = vehicules.TRAFIC["pointe"]
    assert abs(r["penchants"]["matin"] - p["penchant"]) < 1e-9, r["penchants"]
    assert abs(r["penchants"]["soir"] + p["penchant"]) < 1e-9, r["penchants"]
    assert r["penchants"]["creux"] == 0, "il y a une heure de pointe au creux du jour : %s" % r["penchants"]
    matin, soir, creux = r["gains"]["matin"], r["gains"]["soir"], r["gains"]["creux"]
    assert matin > creux, f"le matin ne rapproche pas du cœur plus que le creux ({matin:.2f} contre {creux:.2f})"
    assert soir < creux, f"le soir n'éloigne pas du cœur plus que le creux ({soir:.2f} contre {creux:.2f})"


# --- Les nids-de-poule -------------------------------------------------------


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def test_les_nids_sont_sur_la_chaussee_hors_croisement_et_espaces(ville):
    """⚠️ **Jamais dans un croisement** — on y freine déjà, on y regarde le
    feu, et une secousse au milieu d'un virage se lit comme un bogue de
    collision. Jamais sur une ligne d'arrêt non plus : c'est là qu'on est
    immobile. Et jamais deux collés : deux nids côte à côte ne font pas un
    nid-de-poule, ils font une rue défoncée."""
    fiche = carte.NIDS_DE_POULE
    nids = ville["nids_de_poule"]
    lo, hi = fiche["par_ville"]
    assert lo <= len(nids) <= hi, f"{len(nids)} nids-de-poule"
    sol = ville["sol"]
    boites = [(i["x"], i["y"], i["l"], i["h"]) for i in ville["intersections"]]
    arrets = {tuple(int(n) for n in cle.split(",")) for cle in ville["arrets"]}
    for n in nids:
        glyphe = sol[n["y"]][n["x"]]
        assert carte.LEGENDE[glyphe].get("route"), f"un nid sur « {glyphe} »"
        assert not carte.LEGENDE[glyphe].get("trottoir"), "un nid sur une traverse"
        assert (n["x"], n["y"]) not in arrets, f"un nid sur une ligne d'arrêt : {n}"
        for bx, by, bl, bh in boites:
            assert not (bx <= n["x"] < bx + bl and by <= n["y"] < by + bh), f"un nid dans un croisement : {n}"
    for a, b in itertools.combinations(nids, 2):
        ecart = abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])
        assert ecart >= fiche["ecart"], f"deux nids collés : {a} et {b}"
    # Et ils sont répandus : tous dans un coin, c'est une rue défoncée, pas une ville.
    moitie = ville["largeur"] // 2
    assert any(n["x"] < moitie for n in nids) and any(n["x"] >= moitie for n in nids)


def test_un_nid_secoue_et_coute_deux_points_une_seule_fois(banc, paquet):
    """⚠️ Un répit après chaque nid : sans lui, un char lent le paie à chaque
    image de la tuile, et un nid devient un piège au lieu d'un cahot."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, ph = L.B.defs.conduite.physique;
        const nid = L.Monde.carte.def.nids_de_poule[0];
        j.x = nid.x * TT + 8; j.y = nid.y * TT + 8; L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        v.x = nid.x * TT + 8; v.y = nid.y * TT + 8; L.Entites.indexer();
        const out = { indexe: L.Monde.nidDePoule(nid.x, nid.y),
                      ailleurs: L.Monde.nidDePoule(nid.x + 3, nid.y + 3) };
        // 1. A L'ARRET : un char immobile ne tombe pas dans un nid.
        v.vitesse = 0; v.vx = 0; v.vy = 0; v.nidT = 0;
        const vie0 = v.vie;
        L.B.cam.secousse = 0;
        for (let i = 0; i < 10; i++) L.Vehicules.majNidDePoule(v);
        out.arret = { perdu: vie0 - v.vie, secousse: L.B.cam.secousse };
        // 2. EN ROULANT : une fois, et une seule, le temps du répit.
        v.vitesse = 2; v.vx = 2; v.vy = 0; v.nidT = 0;
        const vie1 = v.vie;
        for (let i = 0; i < 10; i++) L.Vehicules.majNidDePoule(v);
        out.roule = { perdu: vie1 - v.vie, secousse: L.B.cam.secousse, repit: v.nidT };
        // 3. Le répit passé, on le paie de nouveau.
        v.nidT = 0;
        const vie2 = v.vie;
        L.Vehicules.majNidDePoule(v);
        out.encore = vie2 - v.vie;
        return out;
    }""")
    ph = vehicules.PHYSIQUE
    assert r["indexe"] is True and r["ailleurs"] is False, "l'index des nids ne dit pas la vérité : %s" % r
    assert r["arret"]["perdu"] == 0 and r["arret"]["secousse"] == 0, "un char à l'arrêt tombe dans un nid : %s" % r["arret"]
    assert r["roule"]["perdu"] == ph["nid_degats"], "le nid ne coûte pas ce que la fiche dit : %s" % r["roule"]
    assert abs(r["roule"]["secousse"] - ph["nid_secousse"]) < 1e-9, r["roule"]
    assert r["roule"]["repit"] > 0, "aucun répit : le nid se paie à chaque image"
    assert r["encore"] == ph["nid_degats"], "le répit passé, le nid ne se sent plus : %s" % r


# --- Les entraves du jour ----------------------------------------------------


def test_une_entrave_ferme_une_voie_et_jamais_la_rue(ville):
    """⚠️ **Une entrave ne coupe jamais la ville en deux**, et c'est la seule
    chose qui compte. Celle-ci ne le peut pas **par construction** : elle ferme
    UNE voie d'une rue qui en a deux dans le même sens — le champ de direction
    ne bouge pas d'une flèche, donc `voies_bloquees` rend exactement ce qu'il
    rendait. C'est ce qui permet de se passer du juge de connexité à la
    construction (il coûte 14 ms, et en valider cent doublerait le temps de
    bâtir la ville)."""
    fiche = carte.ENTRAVES
    liste = ville["entraves"]
    lo, hi = fiche["par_ville"]
    assert lo <= len(liste) <= hi, f"{len(liste)} entraves possibles"
    voie = ville["voie"]
    boites = [(i["x"], i["y"], i["l"], i["h"]) for i in ville["intersections"]]
    arrets = {tuple(int(n) for n in cle.split(",")) for cle in ville["arrets"]}
    pas = {">": (1, 0), "<": (-1, 0), "^": (0, -1), "v": (0, 1)}
    mini, maxi = fiche["longueur"]
    for e in liste:
        assert e["sens"] in pas, e
        dx, dy = pas[e["sens"]]
        n = max(e["l"], e["h"])
        assert mini <= n <= maxi, f"une entrave de {n} tuiles : {e}"
        assert (e["l"] == 1) != (e["h"] == 1), f"une entrave qui n'est pas une voie : {e}"
        for k in range(n):
            x, y = e["x"] + (0 if dy else k), e["y"] + (0 if dx else k)
            assert voie[y][x] == e["sens"], f"{e} : la tuile {x},{y} ne va pas dans son sens"
            assert (x, y) not in arrets, f"une entrave sur une ligne d'arrêt : {e}"
            for bx, by, bl, bh in boites:
                assert not (bx <= x < bx + bl and by <= y < by + bh), f"une entrave dans un croisement : {e}"
            # ⚠️ LA VOIE D'À CÔTÉ : c'est elle qui reste ouverte, et c'est
            # pour ça que fermer celle-ci ne coupe rien.
            assert any(voie[y + ny][x + nx] == e["sens"] for nx, ny in ((-dy, dx), (dy, -dx))), (
                f"{e} : la tuile {x},{y} n'a pas de voie parallèle — la fermer couperait la rue"
            )
    for a, b in itertools.combinations(liste, 2):
        assert abs(a["x"] - b["x"]) + abs(a["y"] - b["y"]) >= fiche["ecart"], f"deux chantiers collés : {a} et {b}"
    # Et la ville reste fortement connexe, entraves comprises : elles ne
    # touchent à aucune flèche, donc la mesure est la même qu'avant.
    sans_aller, sans_retour = carte.voies_bloquees(ville)
    assert not sans_aller and not sans_retour


def test_la_ville_change_de_chantier_chaque_jour(banc, paquet):
    """⚠️ La graine du JOUR, jamais `B.rng()` : un décor qui change la ville ne
    consomme pas un dé du jeu — c'est la leçon des pilotes de deux-roues. Et le
    chantier est une **barrière** comme les autres : il bloque les chars et pas
    les jambes, il se force en poussant les cônes, il se voit, et le carnet le
    liste. Rien de neuf dans le mécanisme, seulement dans le choix."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        const jours = [];
        for (let j = 1; j <= 12; j++) {
            p.jour = j;
            const e = L.Monde.entraveDuJour();
            jours.push(e ? e.x + ',' + e.y : null);
        }
        // Un jour de CHANTIER (une voie fermee) et un jour de RUE BARREE : les
        // deux genres sortent de la meme liste, et un seul par jour.
        let jourVoie = 0, jourRue = 0;
        for (let j = 1; j <= 60; j++) {
            p.jour = j;
            const b = L.Monde.entraveDuJour();
            if (b.slug === 'entrave' && !jourVoie) jourVoie = j;
            if (b.slug === 'rue_barree' && !jourRue) jourRue = j;
        }
        p.jour = jourVoie || 1;
        const e = L.Monde.entraveDuJour();
        // Le meme jour rend le meme chantier, et sans tirer un seul de.
        const avant = L.B.rng();
        const encore = L.Monde.entraveDuJour();
        p.jour = (jourVoie || 1) + 1; L.Monde.entraveDuJour(); p.jour = jourVoie || 1;
        const rejoue = L.Monde.entraveDuJour();
        const fermees = L.Monde.barrieresFermees().filter(function (b) { return b.slug === 'entrave' || b.slug === 'rue_barree'; });
        const carnet = L.Missions.menuCasier().items.some(function (i) { return i.detail === e.raison; });
        p.jour = jourRue || 1;
        const rue = L.Monde.entraveDuJour();
        p.jour = jourVoie || 1;
        return { jours: jours, distincts: new Set(jours).size, jourVoie: jourVoie, jourRue: jourRue,
                 stable: encore === e && rejoue.x === e.x && rejoue.y === e.y,
                 arrete: e.arrete, forcer: e.forcer, decor: e.decor, raison: e.raison, slug: e.slug,
                 rue: jourRue ? { slug: rue.slug, decor: rue.decor, plein: !!rue.plein,
                                  forcer: rue.forcer, raison: rue.raison, arrete: rue.arrete,
                                  l: rue.l, h: rue.h } : null,
                 fermees: fermees.length, carnet: carnet,
                 bloqueLesChars: L.Monde.barriereBloque({ type: 'vehicule', x: (e.x - 3) * 16, y: (e.y - 3) * 16 }, e.x, e.y),
                 bloquePasLesJambes: L.Monde.barriereBloque({ type: 'pieton', x: (e.x - 3) * 16, y: (e.y - 3) * 16 }, e.x, e.y) };
    }""")
    fiche, ferme = carte.ENTRAVES, carte.FERMETURES
    assert None not in r["jours"], "il n'y a pas de chantier : %s" % r["jours"]
    assert r["distincts"] >= 5, "la ville a le même chantier tous les jours : %s" % r["jours"]
    assert r["stable"] is True, "le chantier bouge dans la journée"
    # ⚠️ LES DEUX GENRES SORTENT, et un seul par jour : c'est ce qui évite
    # d'avoir à juger les COMBINAISONS — deux fermetures prises séparément dans
    # une liste valide peuvent, ensemble, isoler un bloc. Une seule, et la
    # question ne se pose pas.
    assert r["jourVoie"] and r["jourRue"], "un seul genre d'entrave sort jamais : %s" % r
    assert r["fermees"] == 1, "il n'y a pas exactement une entrave fermée : %s" % r["fermees"]
    assert r["slug"] == "entrave" and r["decor"] == "cones"
    assert r["arrete"] == ["vehicule"], "un chantier qui barre le trottoir : %s" % r["arrete"]
    assert r["bloqueLesChars"] is True and r["bloquePasLesJambes"] is False
    assert r["forcer"]["degats"] == fiche["degats"], r["forcer"]
    assert r["raison"] == fiche["raison"]
    # La rue barrée : sa barricade, son prix plus lourd, et surtout elle bloque
    # TOUT son rectangle — une chaussée de quatre tuiles de large aurait laissé
    # passer le monde par le milieu.
    rue = r["rue"]
    assert rue["slug"] == "rue_barree" and rue["decor"] == "barricade"
    assert rue["plein"] is True, "une rue barrée qu'on traverse par le milieu"
    assert rue["arrete"] == ["vehicule"], "une rue barrée qui barre aussi le trottoir"
    assert rue["forcer"]["degats"] == ferme["degats"] > fiche["degats"], rue["forcer"]
    assert rue["raison"] == ferme["raison"]
    assert max(rue["l"], rue["h"]) >= 6, "une « rue barrée » de trois tuiles : %s" % rue
    assert r["carnet"] is True, "le carnet ne dit pas ce qui est fermé en ville"


def test_devant_un_chantier_le_trafic_se_deporte_au_lieu_de_rebrousser(banc, paquet):
    """⚠️ **Une voie fermée laisse sa voisine ouverte** : y faire demi-tour
    serait absurde, et toute la rue rebrousserait chemin pour trois cônes. On
    se déporte d'abord, on ne fait demi-tour que s'il n'y a pas de voisine —
    c'est la voie d'à côté qui tranche, pas le genre de la barrière."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(61);
        const j = L.B.joueur, TT = L.TT, p = L.B.partie;
        // ⚠️ On veut un jour de CHANTIER (une voie fermee) : c'est la qu'il y a
        // une voisine ou se deporter. Devant une rue barree, on tourne avant.
        let e = null;
        for (let jour = 1; jour <= 60 && !e; jour++) {
            p.jour = jour;
            const b = L.Monde.entraveDuJour();
            if (b.slug === 'entrave') e = b;
        }
        if (!e) return { pasDeChantier: true };
        const pas = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] }[e.sens || L.Monde.fleche(e.x, e.y)];
        // On se met a cote du chantier et on lache un char du trafic en amont.
        j.x = (e.x + 6) * TT; j.y = (e.y + 6) * TT; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        const amont = { x: (e.x - pas[0] * 5) * TT + 8, y: (e.y - pas[1] * 5) * TT + 8 };
        const v = L.Vehicules.creer('auto', amont.x, amont.y, Math.atan2(pas[1], pas[0]),
                                    { conducteur: 'trafic', etat: 'roule', sens: e.sens });
        L.Entites.indexer();
        const voie0 = pas[0] ? Math.floor(v.y / TT) : Math.floor(v.x / TT);
        let plante = 0, pire = 0, passe = false, changeDeVoie = false;
        for (let i = 0; i < 700; i++) {
            o.frame(1);
            if (L.B.entites.indexOf(v) < 0) break;
            plante = Math.abs(v.vitesse) < 0.05 ? plante + 1 : 0;
            if (plante > pire) pire = plante;
            const voie = pas[0] ? Math.floor(v.y / TT) : Math.floor(v.x / TT);
            if (voie !== voie0) changeDeVoie = true;
            const long = pas[0] ? Math.floor(v.x / TT) : Math.floor(v.y / TT);
            const bout = pas[0] ? e.x + pas[0] * (e.l + 1) : e.y + pas[1] * (e.h + 1);
            if (pas[0] > 0 || pas[1] > 0 ? long > bout : long < bout) passe = true;
        }
        return { changeDeVoie: changeDeVoie, passe: passe, pire: pire,
                 cycle: 2 * (L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images) };
    }""")
    assert not r.get("pasDeChantier"), "aucun jour ne donne une voie fermée"
    assert r["changeDeVoie"] is True, "le trafic ne se déporte pas devant le chantier : %s" % r
    assert r["passe"] is True, "le trafic ne passe jamais le chantier : %s" % r
    assert r["pire"] < r["cycle"], "un char reste planté %s images devant les cônes : %s" % (r["pire"], r)


def test_une_rue_barree_couvre_tout_son_troncon_et_la_ville_reste_connexe(ville):
    """⚠️ **Mesuré, et c'est ce qui a tout décidé** : barrer la MOITIÉ d'un
    tronçon laisse l'autre moitié en cul-de-sac **dans les deux sens** — la voie
    qui monte n'a plus d'entrée, celle qui descend n'a plus de sortie. Le juge
    de connexité refusait les vingt-six premières candidates, toutes pour cette
    raison. Fermée en entier, la rue disparaît du graphe et la grille route
    autour : c'est d'ailleurs ce que « rue barrée » veut dire.

    Ce juge rejoue ce que la construction a promis : chaque fermeture, prise
    seule, laisse les rues **fortement connexes**."""
    fiche = carte.FERMETURES
    liste = ville["fermetures"]
    lo, hi = fiche["par_ville"]
    assert lo <= len(liste) <= hi, f"{len(liste)} rues barrables"
    boites = [(i["x"], i["y"], i["l"], i["h"]) for i in ville["intersections"]]
    ponts = [(p["x"], p["y"], p["l"], p["h"]) for p in ville["ponts"]]
    voie = ville["voie"]
    for f in liste:
        assert max(f["l"], f["h"]) <= fiche["long_max"], f"une fermeture de {max(f['l'], f['h'])} tuiles : {f}"
        tuiles = [(x, y) for y in range(f["y"], f["y"] + f["h"]) for x in range(f["x"], f["x"] + f["l"])]
        for x, y in tuiles:
            assert voie[y][x] != ".", f"{f} : la tuile {x},{y} n'est pas une chaussée"
            for bx, by, bl, bh in boites:
                assert not (bx <= x < bx + bl and by <= y < by + bh), f"une fermeture dans un croisement : {f}"
            for px, py, pl, ph in ponts:
                assert not (px <= x < px + pl and py <= y < py + ph), f"une fermeture SUR LE PONT : {f}"
        # ⚠️ LE JUGE DE M1, rejoué : on retire ses flèches, et les rues doivent
        # rester fortement connexes.
        grille = [list(ligne) for ligne in voie]
        for x, y in tuiles:
            grille[y][x] = "."
        sans_aller, sans_retour = carte.voies_bloquees(
            {"voie": ["".join(ligne) for ligne in grille], "arrets": ville["arrets"]})
        assert not sans_aller and not sans_retour, (
            f"{f} coupe la ville : {len(sans_aller)} tuiles inatteignables, "
            f"{len(sans_retour)} d'où l'on ne revient pas"
        )
    for a, b in itertools.combinations(liste, 2):
        assert abs(a["x"] - b["x"]) + abs(a["y"] - b["y"]) >= fiche["ecart"], f"deux rues barrées collées : {a} et {b}"


def test_une_rue_barree_montre_son_detour(banc, paquet):
    """⚠️ **Une fermeture sans détour affiché n'est pas une entrave, c'est un
    piège** : on arrive, on ne passe pas, et rien ne dit par où aller. Le
    panneau se pose au-dessus de la barricade, et sa flèche montre le côté où
    la rue continue — jamais un côté au hasard : il cherche la chaussée la plus
    proche, et il se tait plutôt que de mentir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        let rue = null;
        for (let jour = 1; jour <= 60 && !rue; jour++) {
            p.jour = jour;
            const b = L.Monde.entraveDuJour();
            if (b.slug === 'rue_barree') rue = b;
        }
        if (!rue) return { pasDeRue: true };
        const vertical = rue.h >= rue.l;
        // Les deux bouts de la rue barree : c'est la que se pose le panneau.
        const bouts = [];
        for (let ty = rue.y; ty < rue.y + rue.h; ty++) {
            for (let tx = rue.x; tx < rue.x + rue.l; tx++) {
                const bout = vertical ? (ty === rue.y || ty === rue.y + rue.h - 1)
                                      : (tx === rue.x || tx === rue.x + rue.l - 1);
                if (!bout) continue;
                const vers = L.Monde.cotePourLeDetour(rue, tx, ty);
                // ⚠️ ET ON VERIFIE QUE LE PANNEAU DIT VRAI : du cote montre, il
                // doit y avoir une chaussee QUI N'EST PAS la rue barree
                // elle-meme. Sans ca, le panneau montre la voie d'a cote du
                // chantier et envoie droit dans la barricade.
                let mene = false;
                if (vers) {
                    const sortie = vertical ? (ty === rue.y ? -1 : 1) : (tx === rue.x ? -1 : 1);
                    const ox = vertical ? tx : tx + sortie * 3;
                    const oy = vertical ? ty + sortie * 3 : ty;
                    for (let d = 1; d <= 6 && !mene; d++) {
                        const cx = vertical ? ox + vers * d : ox;
                        const cy = vertical ? oy : oy + vers * d;
                        const dedans = cx >= rue.x && cx < rue.x + rue.l && cy >= rue.y && cy < rue.y + rue.h;
                        if (L.Monde.estRoute(cx, cy) && !dedans) mene = true;
                    }
                }
                bouts.push({ tx: tx, ty: ty, vers: vers, mene: mene });
            }
        }
        // Et au MILIEU, il n'y a pas de panneau : on ferme une rue par ses
        // extremites, on ne la cloture pas.
        const milieu = { tx: rue.x + Math.floor(rue.l / 2), ty: rue.y + Math.floor(rue.h / 2) };
        const auMilieu = vertical ? (milieu.ty === rue.y || milieu.ty === rue.y + rue.h - 1)
                                  : (milieu.tx === rue.x || milieu.tx === rue.x + rue.l - 1);
        return { bouts: bouts, auMilieu: auMilieu, vertical: vertical,
                 rue: { x: rue.x, y: rue.y, l: rue.l, h: rue.h } };
    }""")
    assert not r.get("pasDeRue"), "aucun jour ne donne une rue barrée"
    assert r["auMilieu"] is False, "la rue est barrée sur toute sa longueur : %s" % r["rue"]
    assert len(r["bouts"]) >= 2, "une rue barrée sans bouts : %s" % r
    # ⚠️ **CHAQUE bout parle.** Une rue barrée part d'un croisement et finit à
    # un autre : il y a donc une rue qui croise à ses deux extrémités, et un
    # bout muet est un automobiliste qu'on laisse devant une barricade sans
    # rien lui dire.
    muets = [b for b in r["bouts"] if not b["vers"]]
    assert not muets, "des bouts de la rue barrée ne montrent aucun détour : %s" % muets
    for b in r["bouts"]:
        assert b["vers"] in (-1, 1), b
        # ⚠️ **Le panneau dit VRAI** : du côté montré il y a une chaussée, et
        # ce n'est pas la voie d'à côté du chantier — sinon la flèche envoie
        # droit dans la barricade.
        assert b["mene"] is True, "le panneau montre un côté sans rue : %s" % b


def test_le_chantier_a_ses_ouvriers_et_on_ne_les_fauche_pas(banc, paquet):
    """⚠️ **Intouchables, comme les enfants.** Un chantier où l'on fauche
    l'équipe au premier passage n'est pas un chantier, c'est une cible. Et
    c'est une propriété de l'ENTITÉ, pas de l'archétype : un ouvrier qui rentre
    chez lui, lui, est un passant comme un autre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(77);
        const p = L.B.partie, j = L.B.joueur, TT = L.TT;
        let e = null;
        for (let jour = 1; jour <= 60 && !e; jour++) {
            p.jour = jour;
            const b = L.Monde.entraveDuJour();
            if (b.slug === 'entrave') e = b;
        }
        if (!e) return { pasDeChantier: true };
        // Dans la bulle, mais hors champ : c'est la qu'ils naissent.
        j.x = (e.x + 18) * TT; j.y = (e.y + 18) * TT;
        L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        const nes = L.Entites.naitreLesOuvriers();
        const encore = L.Entites.naitreLesOuvriers();
        const gars = L.B.entites.filter(function (q) { return q.chantier; });
        // Un ouvrier ORDINAIRE, lui, reste un passant : l'archetype n'a pas bouge.
        const arch = L.Entites.archetype('ouvrier');
        const passant = L.Entites.creerPieton(j.x + 40, j.y, arch);
        return { nes: nes, encore: encore, combien: gars.length,
                 intouchables: gars.every(function (q) { return q.intouchable; }),
                 figes: gars.every(function (q) { return q.etat === 'fige' && q.plante; }),
                 metier: gars.length ? gars[0].metier : null,
                 surLaVoie: gars.every(function (q) {
                     const tx = Math.floor(q.x / TT), ty = Math.floor(q.y / TT);
                     return tx >= e.x - 1 && tx <= e.x + e.l && ty >= e.y - 1 && ty <= e.y + e.h;
                 }),
                 archIntouchable: !!arch.intouchable, passantIntouchable: !!passant.intouchable };
    }""")
    assert not r.get("pasDeChantier"), "aucun jour ne donne une voie fermée"
    assert r["nes"] >= 1, "personne ne travaille au chantier : %s" % r
    assert r["combien"] <= 2, "toute une équipe de voirie : %s" % r["combien"]
    assert r["encore"] == 0, "les ouvriers se dédoublent à chaque ronde"
    assert r["intouchables"] is True, "on peut faucher l'équipe du chantier"
    assert r["figes"] is True and r["metier"] == "chantier", r
    assert r["surLaVoie"] is True, "les ouvriers travaillent à côté du chantier : %s" % r
    # ⚠️ L'archétype n'a PAS bougé : un ouvrier qui rentre chez lui est un
    # passant comme un autre, et la ville n'est pas devenue intouchable.
    assert r["archIntouchable"] is False and r["passantIntouchable"] is False, (
        "tous les ouvriers de la ville sont devenus intouchables : %s" % r
    )


# --- Le char en panne --------------------------------------------------------


def test_la_fiche_de_la_panne_se_tient():
    """Une entrave qu'on n'a **pas** vue venir : ni cônes, ni panneau, ni liste
    validée par Python. Elle dure une **heure**, pas un jour — une entrave du
    jour change la ville, une panne ne fait que la contrarier."""
    f = vehicules.TRAFIC["panne"]
    assert 0 < f["chance_par_heure"] <= 1
    assert 0 < f["minutes"] < 24 * 60, "une panne qui dure plus qu'une journée n'est plus une panne"
    assert f["detresse_images"] > 0
    slugs = {v["slug"] for v in vehicules.de_phase(1)}
    assert f["slugs"] and set(f["slugs"]) <= slugs, f["slugs"]


def test_un_char_en_panne_bat_ses_feux_repart_et_n_est_pas_mal_gare(banc, paquet):
    """⚠️ **`laisse` veut dire « le JOUEUR l'a abandonné ici »**, et c'est lui
    seul que la fourrière suit. Marquer la panne ainsi la faisait déclarer MAL
    GARÉE : le HUD nageait dans « la fourrière va passer » pendant qu'un camion
    battait ses feux de détresse. Un char en panne n'est pas mal garé — il est
    en panne."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const p = L.B.partie, f = L.B.defs.conduite.trafic.panne;
        // On cherche une heure ou la panne tombe : elle se tire du JOUR et de
        // l'HEURE, donc elle est la meme a chaque partie — c'est voulu.
        let v = null;
        for (let h = 0; h < 24 && !v; h++) {
            p.heure = (h + 0.5) / 24;
            B_panne_reset(L);
            L.Vehicules.majPanne();
            v = L.B.entites.find(function (q) { return q.panneT > 0; }) || null;
        }
        function B_panne_reset(L) { L.B.panneHeure = -1; }
        if (!v) return { pasDePanne: true };
        // ⚠️ On mesure ce que la FOURRIERE fait, pas ce que `malGare` rend :
        // un camion arrete sur la chaussee EST sur la chaussee — la question
        // est de savoir si le lot le suit, et il ne suit que ce que le joueur
        // a laisse (`laisse`).
        L.B.msg = null;
        v.malGareT = 0;
        for (let i = 0; i < 4; i++) { L.B.t += 60; L.Missions.majMalGares(); }
        const out = { slug: v.slug, arret: Math.abs(v.vitesse) < 0.01, laisse: !!v.laisse,
                      suivi: v.malGareT > 0, msg: L.B.msg, duree: v.panneT,
                      conducteur: v.conducteur, etat: v.etat };
        // Elle ne compte pas dans les places de stationnement de la ville.
        const stationnes = L.B.entites.filter(function (q) {
            return q.type === 'vehicule' && !q.conducteur && q.etat !== 'epave' && !(q.panneT > 0);
        }).length;
        out.stationnesSansElle = stationnes;
        // Et elle s'en va quand son heure est finie.
        v.panneT = 2;
        o.frame(4);
        out.partie = L.B.entites.indexOf(v) < 0;
        return out;
    }""")
    assert not r.get("pasDePanne"), "aucune heure de la journée ne donne une panne"
    f = vehicules.TRAFIC["panne"]
    assert r["slug"] in f["slugs"], r["slug"]
    assert r["arret"] is True and r["conducteur"] is None and r["etat"] == "stationne"
    assert r["laisse"] is False, "la panne est marquée comme abandonnée par le joueur"
    assert r["suivi"] is False, "la fourrière suit un char en panne : %s" % r
    assert "MAL GARÉ" not in (r["msg"] or ""), "le HUD annonce la fourrière devant un char en panne : %s" % r["msg"]
    assert r["duree"] > 0
    assert r["partie"] is True, "la panne ne repart jamais"


def test_une_panne_ne_tire_pas_un_seul_de_du_jeu(banc, paquet):
    """⚠️ **La leçon du pilote des deux-roues, rejouée.** Ce qui naît pour le
    DÉCOR ne doit pas décaler le hasard du jeu : chaque dé tiré déplace tous
    ceux qui suivent. Une panne qui prenait un dé au passage (sa couleur, sa
    place) a fait tomber quatre juges d'un coup — et aucun ne parlait de
    pannes. `majPanne` tire donc tout au `hash2` du jour et de l'heure.

    ⚠️ **ON MESURE LA MAIN DE LA PANNE, PAS LE SILLAGE DE LA PANNE.** Le juge
    comparait le total des dés de six cents images, avec panne et sans. C'était
    une coïncidence de graine, pas une règle : un char en panne est une ENTRAVE
    — c'est tout son sens — et le trafic qui cherche où faire naître le suivant
    réessaie autour de lui, ce qui tire des dés en toute légitimité. Mesuré sur
    dix graines de partie, la comparaison des totaux tombait déjà d'elle-même
    sur deux d'entre elles (6 : −87 dés, 10 : −807), sans qu'aucune panne ait
    pris quoi que ce soit. Le juge ne tenait que sur la graine 5.

    On compte donc les dés tirés PENDANT `majPanne` — sa couleur, sa place, son
    modèle. C'est la règle elle-même, et aucun remous de la ville ne la bouge."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(5);
        // ⚠️ On l'allume PAR SA FICHE : la panne doit vraiment tomber, sinon le
        // juge compte les des d'une chose qui n'arrive pas.
        const garde = L.B.defs.conduite.trafic.panne.chance_par_heure;
        L.B.defs.conduite.trafic.panne.chance_par_heure = 1;
        const vrai = L.B.rng;
        let total = 0, dedans = 0, sites = [];
        L.B.rng = function () {
            total++;
            // ⚠️ La PILE, pas un drapeau : `majPanne` tire par la main de ce
            // qu'elle appelle (`placeDeLaPanne`, `creer`), et c'est justement
            // la que le de s'etait glisse la premiere fois.
            const pile = new Error().stack;
            if (pile.indexOf('majPanne') >= 0) {
                dedans++;
                if (sites.length < 5) sites.push(pile.slice(0, 200));
            }
            return vrai();
        };
        o.frame(600);
        L.B.rng = vrai;
        L.B.defs.conduite.trafic.panne.chance_par_heure = garde;
        const pannes = L.B.entites.filter(function (q) { return q.panneT > 0; }).length;
        return { total: total, dedans: dedans, sites: sites, pannes: pannes };
    }""")
    assert r["pannes"] >= 1, "aucune panne n'est tombée : le juge ne mesure rien (%s)" % r
    assert r["total"] > 100, "le jeu ne tire plus de dés du tout : le juge ne mesure rien (%s)" % r
    assert r["dedans"] == 0, (
        "la panne a tiré %s dés du jeu — tout ce qui suit est décalé : %s"
        % (r["dedans"], r["sites"])
    )


def test_une_panne_ne_s_efface_pas_sous_celui_qui_la_tient(banc, paquet):
    """⚠️ **Un char que quelqu'un TIENT ne s'efface pas.** L'heure de la panne
    finie, le compte à rebours retirait le char de la ville sans regarder qui
    était dedans : on montait dans la remorqueuse en panne, et elle disparaissait
    sous le joueur — qui restait accroché (`dansVehicule`) à une entité absente
    de la ville, invisible et immobile, et rien ne le lui disait. La charge sur
    la fourche s'en allait de la même façon. Tenu, le char cesse simplement
    d'être en panne — ses feux s'éteignent — et redevient un char ordinaire :
    c'est `peupler` qui l'oubliera, loin et hors champ, comme tous les autres."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, out = {};
        // 1. LE JOUEUR AU VOLANT : la remorqueuse en panne, on monte dedans,
        //    et l'heure finit pendant qu'il la conduit.
        const rem = L.Vehicules.creer('remorqueuse', j.x + 40, j.y, 0, { etat: 'stationne' });
        L.Entites.indexer();
        rem.panneT = 3;
        out.monte = L.Vehicules.monter(j, rem);
        o.frame(8);
        out.volant = { la: L.B.entites.indexOf(rem) >= 0, dedans: j.dansVehicule === rem, feux: rem.panneT };
        // 2. LA CHARGE SUR LA FOURCHE : elle aussi est tenue par quelqu'un.
        const charge = L.Vehicules.creer('auto', rem.x - Math.cos(rem.angle) * 28,
                                         rem.y - Math.sin(rem.angle) * 28, rem.angle, { etat: 'stationne' });
        L.Entites.indexer();
        charge.panneT = 3;
        out.accroche = L.Vehicules.basculerCrochet(rem);
        o.frame(8);
        out.fourche = { la: L.B.entites.indexOf(charge) >= 0, sur: charge.remorqueePar === rem, feux: charge.panneT };
        return out;
    }""")
    assert r["monte"] is True, "le joueur n'est pas monté : le juge ne mesure rien (%s)" % r
    assert r["volant"]["la"] is True, "la panne s'efface sous le joueur : %s" % r["volant"]
    assert r["volant"]["dedans"] is True, r["volant"]
    assert r["volant"]["feux"] == 0, "un char qu'on conduit bat encore ses feux de détresse : %s" % r["volant"]
    assert r["accroche"] is True, "rien à accrocher derrière : le juge ne mesure rien (%s)" % r
    assert r["fourche"]["la"] is True, "la panne s'efface de la fourche : %s" % r["fourche"]
    assert r["fourche"]["sur"] is True and r["fourche"]["feux"] == 0, r["fourche"]


# --- La ville coupable d'elle-même : le vol de char --------------------------


def test_la_fiche_du_vol_de_char_se_tient():
    """⚠️ **Il se voit, ou il n'a pas lieu** : un vol hors champ est du travail
    qu'on fait pour personne. La portée doit donc rester dans ce qu'un écran
    montre, et le voleur doit avoir le temps d'atteindre le char sans le
    poursuivre pour l'éternité."""
    f = pietons.VOL_DE_CHAR
    assert 0 < f["chance_par_minute"] <= 1
    assert 0 < f["portee_px"] < f["rayon_px"] <= 400
    assert 0 < f["marche_images"] <= 60 * 30, "un voleur qui poursuit un char une demi-heure"
    assert f["peur"] >= 1
    assert pietons.exporter()["vol_de_char"] == f, "une fiche que le navigateur ne lirait pas"


def test_un_char_se_fait_voler_sous_tes_yeux(banc, paquet):
    """⚠️ **Ce n'est PAS le joueur qui le paie.** La police du jeu est centrée
    sur lui : signaler le geste d'un autre lui mettrait une étoile. Les
    passants s'écartent, le voleur part avec le char, et c'est tout.

    ⚠️ Et il ne touche ni au char du joueur, ni à celui qu'il a **laissé**
    quelque part : un char abandonné appartient à la fourrière, pas aux
    voleurs — deux systèmes qui se disputent le même char, c'est l'un des deux
    qui ment."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(19);
        const j = L.B.joueur, f = L.B.defs.pietons.vol_de_char;
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y + 40; L.Monde.centrerCamera(j.x, j.y);
        // Un char gare sous les yeux du joueur, et un passant a cote.
        const v = o.char('auto', 30, 0, 0);
        const arch = L.Entites.archetype('passant');
        const voleur = L.Entites.creerPieton(j.x + 60, j.y + 20, arch);
        voleur.etat = 'flane';
        L.Entites.indexer();
        const etoiles0 = L.B.recherche.etoiles;
        // On force la minute a tomber : la fiche tire a l'empreinte.
        let parti = false, essais = 0;
        for (let m = 0; m < 400 && !parti; m++) {
            L.B.volMinute = -1;
            L.B.partie.heure = (m % 1440) / 1440;
            essais += L.Entites.majVolDeChar();
            if (voleur.etat === 'vole_un_char') parti = true;
        }
        const viseLeBon = voleur.charVise === v;
        // Il marche jusqu'au char et il s'en va avec.
        for (let i = 0; i < 400 && L.B.entites.indexOf(voleur) >= 0; i++) o.frame(1);
        return { essais: essais, parti: parti, viseLeBon: viseLeBon,
                 voleurPartiAvec: L.B.entites.indexOf(voleur) < 0,
                 charRoule: v.conducteur === 'trafic' && v.etat === 'roule', vole: !!v.vole,
                 etoiles: L.B.recherche.etoiles - etoiles0,
                 crimes: L.B.crimes.filter(function (c) { return c.t > 0; }).length };
    }""")
    assert r["parti"] is True, "personne ne vole jamais rien : %s" % r
    assert r["viseLeBon"] is True, "le voleur vise un autre char que celui qu'on voit"
    assert r["voleurPartiAvec"] is True, "le voleur reste planté à côté du char"
    assert r["charRoule"] is True and r["vole"] is True, "le char ne part pas : %s" % r
    # ⚠️ LE POINT QUI COMPTE : aucune étoile pour le joueur. Le geste d'un
    # autre ne se paie pas sur son dossier.
    assert r["etoiles"] == 0, "le joueur écope de %s étoile(s) pour un vol qu'il n'a pas commis" % r["etoiles"]


def test_le_voleur_de_moto_part_dessus(banc, paquet):
    """Retour de Martin : « un voleur qui vole une moto n'apparait pas
    dessus ». ⚠️ Dans une auto, le voleur disparaît : on ne voit pas le volant,
    et le trafic est déjà fait de conducteurs invisibles. Mais une moto du
    trafic **montre** son pilote — volée, elle partait vide. C'est **le voleur**
    qui doit être en selle, avec ses couleurs, et c'est lui qui en descend si
    le joueur la lui prend."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(19);
        const j = L.B.joueur;
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y + 40; L.Monde.centrerCamera(j.x, j.y);
        // Il ne reste que la moto : c'est elle qu'on veut voir partir.
        for (const e of L.B.entites.slice()) if (e.type === 'vehicule') L.Entites.retirer(e);
        const v = o.char('moto', 30, 0, 0);
        const voleur = L.Entites.creerPieton(j.x + 60, j.y + 20, L.Entites.archetype('passant'));
        voleur.etat = 'flane';
        L.Entites.indexer();
        const couleurs = JSON.stringify(voleur.swaps);
        for (let m = 0; m < 400 && voleur.etat !== 'vole_un_char'; m++) {
            L.B.volMinute = -1;
            L.B.partie.heure = (m % 1440) / 1440;
            L.Entites.majVolDeChar();
        }
        const vise = voleur.charVise === v;
        for (let i = 0; i < 400 && L.B.entites.indexOf(voleur) >= 0; i++) o.frame(1);
        const images = function () {
            const ctx = L.Base.ecran(); let n = 0;
            ctx.drawImage = function () { n++; };
            L.Vehicules.dessinerUn(ctx, v, 0, 0);
            return n;
        };
        const out = { vise: vise, parti: L.B.entites.indexOf(voleur) < 0, roule: v.conducteur === 'trafic',
                      couleurs: couleurs, cavalier: JSON.stringify(L.Vehicules.cavalierDe(v)), images: images() };
        // Le joueur la lui reprend : c'est le voleur qui descend.
        j.x = v.x; j.y = v.y + 12; v.vitesse = 0;
        L.Vehicules.monter(j, v);
        const sortis = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.etat === 'temoin' && e.menace === j; });
        out.repris = j.dansVehicule === v;
        out.sorti = sortis.length ? JSON.stringify(sortis[sortis.length - 1].swaps) : null;
        return out;
    }""")
    assert r["vise"] is True and r["parti"] is True and r["roule"] is True, "le décor du juge est faux : %s" % r
    assert r["cavalier"] == r["couleurs"], "la moto volée part sans son voleur dessus : %s" % r
    assert r["images"] == 2, "la moto volée se peint en %s image(s) : personne en selle" % r["images"]
    assert r["repris"] is True, "le décor du juge est faux : le joueur n'a pas repris la moto (%s)" % r
    assert r["sorti"] == r["couleurs"], "ce n'est pas le voleur qui descend de la moto reprise : %s" % r


def test_un_voleur_ne_touche_ni_au_char_du_joueur_ni_a_celui_qu_il_a_laisse(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(19);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y + 40; L.Monde.centrerCamera(j.x, j.y);
        // On ecarte les chars du decor : il ne doit rester que les deux nôtres.
        for (const e of L.B.entites.slice()) if (e.type === 'vehicule') L.Entites.retirer(e);
        const sien = o.char('auto', 30, 0, 0);
        j.dernierVehicule = sien;
        const laisse = o.char('taxi', -30, 0, 0);
        laisse.laisse = true;
        const arch = L.Entites.archetype('passant');
        const voleur = L.Entites.creerPieton(j.x + 60, j.y + 20, arch);
        voleur.etat = 'flane';
        L.Entites.indexer();
        let commence = 0;
        for (let m = 0; m < 400; m++) {
            L.B.volMinute = -1;
            L.B.partie.heure = (m % 1440) / 1440;
            commence += L.Entites.majVolDeChar();
        }
        return { commence: commence, etat: voleur.etat, vise: voleur.charVise ? voleur.charVise.slug : null };
    }""")
    assert r["commence"] == 0, "un voleur s'en prend au char du joueur ou à celui qu'il a laissé : %s" % r
    assert r["etat"] == "flane" and r["vise"] is None


#: Une tuile d'eau a trois tuiles au plus d'une voie, une rive praticable a
#: cote : la ou une chaloupe volee trouvait une rue a prendre. ⚠️ Cherchee dans
#: la carte, pas dans `amarrages` : les amarrages bougent avec le port, et le
#: juge doit rester vrai le jour ou ils changent de rive.
_EAU_PRES_D_UNE_VOIE = """
    function eauPresDUneVoie(L) {
        const c = L.Monde.carte, croix = [[1, 0], [-1, 0], [0, 1], [0, -1]];
        for (let ty = 4; ty < c.h - 4; ty++) {
            for (let tx = 4; tx < c.w - 4; tx++) {
                if (!L.Monde.estEau(tx, ty)) continue;
                const rive = croix.map(function (d) { return { x: tx + d[0], y: ty + d[1] }; }).find(function (r) {
                    return !L.Monde.estEau(r.x, r.y) && !L.Monde.bloque(r.x, r.y, L.Monde.MASQUE_VEHICULE); });
                if (!rive) continue;
                let voie = false;
                for (let dy = -3; dy <= 3 && !voie; dy++) {
                    for (let dx = -3; dx <= 3 && !voie; dx++) voie = '<>^v'.indexOf(L.Monde.fleche(tx + dx, ty + dy)) >= 0;
                }
                if (voie) return { x: tx, y: ty, rive: rive };
            }
        }
        return null;
    }
"""


def test_un_voleur_ne_part_pas_avec_une_chaloupe(banc, paquet):
    """⚠️ **Retour de Martin, capture à l'appui : « un bateau sur la route ?? »**
    — une chaloupe arrêtée dans sa voie au passage piéton, cap à l'est.

    Une coque amarrée est `stationne` comme une auto garée, et pour un passant
    du quai c'était le premier char à l'écran. Volée, elle passait au trafic,
    et le trafic roule sur des rails sans lire une tuile. Mesuré avant : visée,
    emportée, puis quatre cent cinquante images sur la chaussée.

    ⚠️ Le témoin compte autant que la règle : une auto garée au même endroit,
    elle, se fait voler. Sans lui, un voleur qui ne vole plus rien du tout
    passerait ce juge."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(19);
        const TT = L.TT, j = L.B.joueur;
        """ + _EAU_PRES_D_UNE_VOIE + """
        const eau = eauPresDUneVoie(L);
        if (!eau) return { eau: null };
        j.x = eau.rive.x * TT + 8; j.y = eau.rive.y * TT + 8; L.Monde.centrerCamera(j.x, j.y);
        for (const e of L.B.entites.slice()) if (e.type === 'vehicule') L.Entites.retirer(e);
        const coque = L.Vehicules.creer('bateau', eau.x * TT + 8, eau.y * TT + 8, 0, { etat: 'stationne' });
        function passant() {
            const q = L.Entites.creerPieton(j.x + 20, j.y, L.Entites.archetype('passant'));
            q.etat = 'flane';
            L.Entites.indexer();
            return q;
        }
        function tenter(voleur) {
            let commence = 0;
            for (let m = 0; m < 400 && voleur.etat !== 'vole_un_char'; m++) {
                L.B.volMinute = -1;
                L.B.partie.heure = (m % 1440) / 1440;
                commence += L.Entites.majVolDeChar();
            }
            return commence;
        }
        const voleur = passant();
        const surLaCoque = tenter(voleur);
        const viseLaCoque = voleur.charVise === coque;
        // Et la ville vit par-dessus : il ne doit toujours pas la prendre.
        let auSec = 0;
        for (let i = 0; i < 1500 && L.B.entites.indexOf(coque) >= 0; i++) {
            o.frame(1);
            j.x = eau.rive.x * TT + 8; j.y = eau.rive.y * TT + 8; L.Monde.centrerCamera(j.x, j.y);
            if (!L.Monde.estEau(Math.floor(coque.x / TT), Math.floor(coque.y / TT))) auSec++;
        }
        const conduite = coque.conducteur;
        // Le temoin : une auto garee sur la rive, au meme endroit, et un passant
        // de plus (volee, la chaloupe emportait son voleur avec elle). N'importe
        // quel passant a portee peut s'en charger : on demande si QUELQU'UN la vise.
        const auto = o.char('auto', 0, 0, 0);
        const temoin = passant();
        const surLAuto = tenter(temoin);
        const viseLAuto = L.B.entites.some(function (q) { return q.charVise === auto; });
        return { eau: eau, surLaCoque: surLaCoque, viseLaCoque: viseLaCoque, auSec: auSec,
                 conduite: conduite, surLAuto: surLAuto, viseLAuto: viseLAuto };
    }""")
    assert r["eau"], "la carte n'a plus d'eau à trois tuiles d'une voie : le juge ne mesure plus rien"
    assert r["surLaCoque"] == 0 and not r["viseLaCoque"], "un voleur vise une chaloupe amarrée : %s" % r
    assert r["conduite"] is None, "la chaloupe a trouvé un conducteur : %s" % r
    assert r["auSec"] == 0, "la chaloupe a passé %s images hors de l'eau : %s" % (r["auSec"], r)
    assert r["surLAuto"] > 0 and r["viseLAuto"], "le témoin est tombé — plus aucun vol ici : %s" % r


def test_le_trafic_ne_conduit_pas_une_coque(banc, paquet):
    """⚠️ **Le trafic roule sur des rails et ne lit aucune tuile** — c'est ce
    qui l'empêche de couper les coins, et c'est aussi pourquoi `tuileInterdite`,
    la règle qui tient une coque sur l'eau, n'y est jamais consultée. Le voleur
    ne confie plus de chaloupe au trafic ; ce juge est pour le prochain chemin
    qui le ferait. Mesuré avant : la coque prend la voie la plus proche."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(19);
        const TT = L.TT, j = L.B.joueur;
        """ + _EAU_PRES_D_UNE_VOIE + """
        const eau = eauPresDUneVoie(L);
        if (!eau) return { eau: null };
        j.x = eau.rive.x * TT + 8; j.y = eau.rive.y * TT + 8; L.Monde.centrerCamera(j.x, j.y);
        for (const e of L.B.entites.slice()) if (e.type === 'vehicule') L.Entites.retirer(e);
        const coque = L.Vehicules.creer('bateau', eau.x * TT + 8, eau.y * TT + 8, 0,
                                        { conducteur: 'trafic', etat: 'roule' });
        L.Entites.indexer();
        let auSec = 0;
        for (let i = 0; i < 900 && L.B.entites.indexOf(coque) >= 0; i++) {
            o.frame(1);
            j.x = eau.rive.x * TT + 8; j.y = eau.rive.y * TT + 8; L.Monde.centrerCamera(j.x, j.y);
            if (!L.Monde.estEau(Math.floor(coque.x / TT), Math.floor(coque.y / TT))) auSec++;
        }
        return { eau: eau, auSec: auSec, conducteur: coque.conducteur, etat: coque.etat,
                 bouge: Math.round(Math.hypot(coque.x - (eau.x * TT + 8), coque.y - (eau.y * TT + 8))) };
    }""")
    assert r["eau"], "la carte n'a plus d'eau à trois tuiles d'une voie : le juge ne mesure plus rien"
    assert r["auSec"] == 0, "le trafic a sorti une coque de l'eau (%s images au sec) : %s" % (r["auSec"], r)
    assert r["conducteur"] is None and r["etat"] == "stationne", "le trafic garde la coque en main : %s" % r
