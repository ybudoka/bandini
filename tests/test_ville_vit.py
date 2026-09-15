"""M12, 1re vague — le rythme de la ville : les feux clignotent la nuit, les
heures de pointe ont une direction, et la chaussée a des nids-de-poule.

⚠️ Les trois tiennent la même promesse : **la ville change d'une heure à
l'autre sans qu'on regénère une seule tuile**. Tout vient de la fiche, et le
navigateur n'invente rien.
"""

import itertools

import pytest

from app import carte, vehicules


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
