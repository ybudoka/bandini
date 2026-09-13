"""Le moteur JS sous Node, contre le paquet que le serveur sert VRAIMENT.

Chaque test passe une fonction `(L, o) => resultat` au banc (tests/banc.js) :
L = window.BANDINI, o = outils (frame, touche, pad, pointeur, singe...).
"""

import json

import pytest

from app import economie


def test_le_moteur_charge_et_expose_son_api(banc, paquet):
    r = banc("""function (L, o) {
        return { etat: L.B.etat, cles: Object.keys(L).sort(), version: L.B.defs.version,
                 carte: [L.Monde.carte.w, L.Monde.carte.h], fetchs: o.fetchs.length };
    }""")
    assert r["etat"] == "titre"
    for cle in ("B", "Base", "Atlas", "Entree", "Son", "Monde", "Entites", "Combat", "Vehicules",
                "Police", "Missions", "Hud", "Jeu", "Sauvegarde", "SPRITES", "TUILES"):
        assert cle in r["cles"], cle
    assert r["carte"] == [paquet["carte"]["largeur"], paquet["carte"]["hauteur"]]
    assert r["fetchs"] == 1


def test_les_sprites_sont_integres(banc):
    r = banc("""function (L, o) {
        const problemes = [];
        for (const nom in L.SPRITES) problemes.push.apply(problemes, L.Atlas.valider(nom, L.SPRITES[nom]));
        for (const ch in L.POLICE_PIXEL) if (L.POLICE_PIXEL[ch].length !== 15) problemes.push('police ' + ch);
        const legende = L.B.defs.carte.legende;
        for (const g in legende) if (!L.TUILES[g]) problemes.push('tuile sans peintre : ' + g);
        return problemes;
    }""")
    assert r == []


def test_le_joueur_marche_et_ne_traverse_pas_les_murs(banc):
    # On mesure vers l'OUEST : a l'est du terminus se tient Ti-Guy, et depuis
    # que la foule ne se traverse plus, un personnage fige est un obstacle.
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const x0 = j.x;
        o.touche('KeyA'); o.frame(60); o.relacher('KeyA');
        const x1 = j.x;
        o.touche('ShiftLeft'); o.touche('KeyA'); o.frame(60); o.relacher('KeyA'); o.relacher('ShiftLeft');
        const x2 = j.x;
        // Vers le haut, un batiment se trouve sur le chemin : on doit s'arreter dessus.
        o.touche('KeyW'); o.frame(900); o.relacher('KeyW');
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { marche: x0 - x1, sprint: x1 - x2, sol: L.Monde.solidite(tx, ty), y: j.y, etat: L.B.etat,
                 dataEtat: o.elements.bandini.dataset.etat };
    }""")
    assert r["marche"] > 50
    assert r["sprint"] > r["marche"] * 1.4, "le sprint doit etre nettement plus rapide"
    assert r["sol"] in (0, 3), "le joueur a fini dans un mur"
    assert r["y"] > 0
    assert r["etat"] == "jeu" and r["dataEtat"] == "jeu"


#: Trouve une tuile de cloture (par sa solidite) avec du libre au nord et au sud,
#: vide la rue de tout le monde, et pose le joueur une tuile AU NORD. Le meme
#: decor pour les trois juges de cloture.
DEVANT_UNE_CLOTURE = """
    function devantUneCloture(L, o, solide) {
        const c = L.Monde.carte;
        for (let ty = 3; ty < c.h - 3; ty++) {
            for (let tx = 3; tx < c.w - 3; tx++) {
                if (L.Monde.solidite(tx, ty) !== solide) continue;
                if (L.Monde.solidite(tx, ty - 1) !== 0 || L.Monde.solidite(tx, ty - 2) !== 0) continue;
                if (L.Monde.solidite(tx, ty + 1) !== 0 || L.Monde.solidite(tx, ty + 2) !== 0) continue;
                // ⚠️ La rue se vide, DECOR COMPRIS : un arbre pose dans une cour
                // arretait le joueur avant la cloture, et le juge mesurait un
                // buisson en croyant mesurer une palissade.
                L.B.entites = L.B.entites.filter(function (e) { return e.type === 'joueur'; });
                L.Entites.reindexerDecor(); L.Entites.indexer();
                const j = L.B.joueur;
                j.x = tx * L.TT + 8; j.y = (ty - 1) * L.TT + 8;
                L.Monde.centrerCamera(j.x, j.y);
                return { tx: tx, ty: ty, j: j };
            }
        }
        return null;
    }
"""


def test_on_ne_traverse_plus_une_cloture_en_courant(banc):
    """⚠️ La demande de Martin : « des clotures, mais si elles ne sont pas
    barbelees, qu'on puisse passer par-dessus ». On passait par-dessus TOUTES —
    sans meme ralentir : `f` etait solide 3, donc le masque des pietons ne la
    voyait pas. Une cloture n'arretait que les chars.

    Maintenant on l'ENJAMBE, et ca coute : une seconde en haut, immobile, sans
    frapper — c'est ce prix-la qui fait d'une cloture un choix (couper par la
    cour, ou faire le tour) plutot qu'un trait de peinture."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        const place = devantUneCloture(L, o, 4);
        if (!place) throw new Error('aucune cloture enjambable dans la ville');
        const j = place.j, regles = L.Entites.reglesCloture();
        const y0 = j.y;
        o.touche('KeyS'); o.touche('ShiftLeft');          // on POUSSE, et en courant
        o.frame(6);
        const pendant = { enjambe: !!j.enjambe, y: j.y, tuile: Math.floor(j.y / L.TT),
                          cloture: place.ty, z: j.z };
        // Ce qu'on ne peut PAS faire en haut d'une cloture : frapper.
        o.touche('Space'); o.frame(2); o.relacher('Space');
        const frappe = j.etat;
        let images = 6, zMax = 0;
        for (let i = 0; i < 200 && j.enjambe; i++) { o.frame(1); images++; zMax = Math.max(zMax, j.z); }
        o.relacher('KeyS'); o.relacher('ShiftLeft');
        const apres = { tuile: Math.floor(j.y / L.TT), x: j.x, enjambe: !!j.enjambe, z: j.z,
                        colonne: Math.floor(j.x / L.TT) };
        return { pendant: pendant, frappe: frappe, images: images, zMax: zMax, apres: apres,
                 duree: regles.enjambe_images, y0: Math.floor(y0 / L.TT) };
    }""" % DEVANT_UNE_CLOTURE)
    assert r["pendant"]["enjambe"] is True, "on pousse une cloture et rien ne se passe"
    assert r["pendant"]["tuile"] == r["y0"], "on a traverse la cloture en courant"
    assert r["frappe"] != "attaque", "on frappe en haut d'une cloture"
    assert r["zMax"] > 0, "le corps ne se souleve jamais : rien ne dit qu'il est EN HAUT"
    assert r["duree"] - 4 <= r["images"] <= r["duree"] + 12, (
        "l'enjambee doit durer ce que les donnees disent (%s images) : %s" % (r["duree"], r["images"])
    )
    assert r["apres"]["tuile"] == r["pendant"]["cloture"] + 1, "on ne retombe pas de l'autre cote"
    assert r["apres"]["enjambe"] is False and r["apres"]["z"] == 0


def test_le_barbele_ne_se_passe_pas(banc):
    """Le barbele se met la ou quelqu'un a paye pour que personne n'entre : ni a
    pied, ni en char, ni en l'enjambant. Sans ca, il ne veut rien dire."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        const place = devantUneCloture(L, o, 5);
        if (!place) throw new Error('aucun barbele dans la ville');
        const j = place.j;
        const tuile0 = Math.floor(j.y / L.TT);
        o.touche('KeyS'); o.touche('ShiftLeft');
        let enjambe = false;
        for (let i = 0; i < 240; i++) { o.frame(1); if (j.enjambe) enjambe = true; }
        o.relacher('KeyS'); o.relacher('ShiftLeft');
        const tuile = Math.floor(j.y / L.TT);
        // ⚠️ Le char en DERNIER, et la mesure du joueur avant : un char lance
        // dans le dos du joueur le pousse, et on mesurerait sa poussee en
        // croyant mesurer le barbele.
        const v = L.Vehicules.creer('auto', place.tx * L.TT + 8, (place.ty - 3) * L.TT + 8, Math.PI / 2, { etat: 'stationne' });
        j.x = v.x - 60;                                  // on se tasse de sa route
        for (let i = 0; i < 90; i++) { v.vitesse = 4; L.Vehicules.maj(); }
        return { enjambe: enjambe, tuile: tuile, tuile0: tuile0, cloture: place.ty,
                 char: Math.floor(v.y / L.TT) };
    }""" % DEVANT_UNE_CLOTURE)
    assert r["enjambe"] is False, "on enjambe le barbele"
    assert r["tuile"] == r["tuile0"], "on est passe a travers le barbele"
    assert r["char"] < r["cloture"], "un char a franchi le barbele"


def test_la_manette_a_une_zone_morte_radiale(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.pad([0.1, 0.05]); o.frame(2);
        const morte = Object.assign({}, L.Entree.axe);
        o.pad([0.6, 0]); o.frame(2);
        const demi = Object.assign({}, L.Entree.axe);
        o.pad([0, -1]); o.frame(2);
        const plein = Object.assign({}, L.Entree.axe);
        o.pad([0, 0], [0, 1]); o.frame(2);
        const bouton = L.entree('esquive');
        o.pad(null); o.frame(2);
        return { morte: morte, demi: demi, plein: plein, bouton: bouton.pad, apres: L.Entree.axe.source };
    }""")
    assert r["morte"]["mag"] == 0
    assert r["demi"]["source"] == "manette" and 0.45 < r["demi"]["mag"] < 0.6 and r["demi"]["y"] == 0
    assert r["plein"]["mag"] == 1 and r["plein"]["y"] == -1
    assert r["bouton"] is True
    assert r["apres"] == "clavier"


def test_le_joystick_tactile_deplace_le_joueur(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, x0 = j.x;
        // Le centre de #croix est en (90, 570) d'apres son faux rectangle.
        // On tire vers la GAUCHE : a l'est du terminus, Ti-Guy fait obstacle
        // depuis que la foule ne se traverse plus.
        o.pointeur('pointerdown', 90, 570, 1);
        o.pointeur('pointermove', 30, 570, 1);
        o.frame(60);
        const pendant = Object.assign({}, L.Entree.axe);
        o.pointeur('pointerup', 30, 570, 1);
        o.frame(2);
        o.bouton('esquive', 'pointerdown');
        o.frame(1);
        const tenu = L.entree('esquive').tactile;
        o.bouton('esquive', 'pointerup');
        return { dx: j.x - x0, pendant: pendant, tenu: tenu, apres: L.Entree.axe.mag,
                 tactile: o.doc.body.classList.contains('tactile') };
    }""")
    assert r["pendant"]["source"] == "tactile" and r["pendant"]["x"] < -0.9
    assert r["dx"] < -40
    assert r["tenu"] is True
    assert r["apres"] == 0
    assert r["tactile"] is True


def test_la_recherche_monte_puis_retombe(banc, paquet):
    palier1 = paquet["recherche"]["paliers"][1]["decroissance_s"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Police.signalerCrime('mort_policier', 100, 100, true);
        const apres = L.B.recherche.etoiles;
        o.frame(%d * 60 - 5);
        const avantDecroissance = L.B.recherche.etoiles;
        o.frame(10);
        return { apres: apres, avant: avantDecroissance, fin: L.B.recherche.etoiles,
                 nonVu: (function () { L.Police.signalerCrime('pickpocket', 0, 0, false); return L.B.recherche.etoiles; })() };
    }""" % palier1)
    assert r["apres"] == 1
    assert r["avant"] == 1
    assert r["fin"] == 0
    assert r["nonVu"] == 0, "un crime non vu ne donne pas d'etoile"


def test_le_cone_de_vision(banc):
    r = banc("""function (L, o) {
        const c = L.Police.dansLeCone;
        const demi = 45 * Math.PI / 180;
        return [c(0, 0, 0, demi, 100, 80, 0), c(0, 0, 0, demi, 100, -80, 0), c(0, 0, 0, demi, 100, 60, 70),
                c(0, 0, 0, demi, 100, 200, 0), c(0, 0, Math.PI, demi, 100, -80, 0)];
    }""")
    assert r == [True, False, False, False, True]


def test_les_amendes_du_navigateur_sont_celles_de_python(banc):
    cas = [(1000, 1, 0), (1000, 2, 3), (50, 5, 20), (100000, 3, 7), (0, 1, 0)]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        return %s.map(function (c) { return [L.Missions.amende(c[0], c[1], c[2]), L.Missions.potDeVin(c[1], c[2]),
                                              L.Missions.factureHopital(c[0])]; });
    }""" % json.dumps(cas))
    for (argent, etoiles, casier), (amende, pot, hopital) in zip(cas, r):
        assert amende == economie.amende(argent, etoiles, casier)
        assert pot == economie.pot_de_vin(etoiles, casier)
        assert hopital == economie.facture_hopital(argent)


def test_la_sauvegarde_fait_l_aller_retour_et_complete_un_vieux_blob(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.argent = 1234; L.B.partie.casier = 2;
        L.Missions.sauvegarderPartie();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        const vieux = L.Sauvegarde.completer({ argent: 7 }, L.B.defs);
        return { argent: brut.argent, casier: brut.casier, x: brut.x, vieux: vieux,
                 cles: Object.keys(L.etatInitial(L.B.defs)).sort() };
    }""")
    assert r["argent"] == 1234 and r["casier"] == 2 and isinstance(r["x"], int)
    assert r["vieux"]["argent"] == 7
    assert sorted(r["vieux"].keys()) == r["cles"]
    assert r["vieux"]["armes"]["poings"] == {"mun": None}


@pytest.mark.parametrize("graine", [1, 2])
def test_le_singe_ne_casse_rien(banc, graine):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.singe(3000, %d);
        const j = L.B.joueur, c = L.Monde.carte;
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { etat: L.B.etat, dedans: j.x >= 0 && j.y >= 0 && j.x <= c.pxW && j.y <= c.pxH,
                 sol: L.Monde.solidite(tx, ty), t: L.B.t, argent: L.B.partie.argent, nan: isNaN(j.x) || isNaN(j.y) };
    }""" % graine)
    assert r["etat"] in ("jeu", "pause")
    assert r["dedans"] and r["sol"] in (0, 3) and not r["nan"]
    assert r["argent"] >= 0
    assert r["t"] > 1000


# --- M1 : la ville ---------------------------------------------------------


def test_la_ville_recue_est_celle_du_serveur(banc, paquet):
    r = banc("""function (L, o) {
        const c = L.Monde.carte, d = L.B.defs.carte;
        const types = {};
        L.B.defs.carte.decor.forEach(function (m) { types[m.type] = true; });
        return { w: c.w, h: c.h, portes: c.portes.length, points: c.points.length,
                 decor: L.B.defs.carte.decor.length, lampes: c.lampes.length,
                 zones: c.zones.length, sansPeintre: Object.keys(d.legende).filter(function (g) { return !L.TUILES[g]; }),
                 decorSansPeintre: Object.keys(types).filter(function (t) { return !L.DECORS[t]; }),
                 typesDecor: Object.keys(types).sort() };
    }""")
    carte = paquet["carte"]
    assert [r["w"], r["h"]] == [carte["largeur"], carte["hauteur"]]
    assert r["portes"] == len(carte["portes"]) >= 8
    assert r["points"] == len(carte["points_interet"])
    assert r["decor"] == len(carte["decor"]) > 100
    assert r["lampes"] == len(carte["lampes"]) > 40
    assert r["zones"] >= 2
    assert r["sansPeintre"] == [], "une tuile de la legende n'a pas de peintre"
    assert r["decorSansPeintre"] == [], "un decor de la carte n'a pas de peintre"
    assert len(r["typesDecor"]) >= 6, r["typesDecor"]


def test_le_joueur_et_les_lieux_sont_sur_des_tuiles_marchables(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const dur = L.Monde.solidite(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT));
        const lieux = L.Monde.carte.points.map(function (p) {
            return [p.slug, L.Monde.solidite(p.x, p.y), !!L.Monde.porteA(p.x, p.y - 1)];
        });
        return { dur: dur, lieux: lieux, zone: L.Monde.zoneA(j.x, j.y).slug,
                 horsCarte: L.Monde.porteA(-1, -1) };
    }""")
    assert r["dur"] in (0, 3), "le joueur apparait dans un mur"
    for slug, dur, porte in r["lieux"]:
        assert dur in (0, 3), f"{slug} : on ne peut pas s'en approcher"
        assert porte is True, f"{slug} : pas de porte au-dessus du point d'interet"
    assert r["zone"] == "faubourg"
    assert r["horsCarte"] is None


def test_le_cache_de_morceaux_ne_gonfle_pas_quand_on_traverse_la_ville(banc):
    """Un cache non borne, c'est 20 Mo de canevas et un telephone qui rame."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const vus = [];
        // On traverse la ville en diagonale, en rendant a chaque saut.
        for (let i = 0; i < 40; i++) {
            j.x = 40 + (c.pxW - 80) * i / 39;
            j.y = 40 + (c.pxH - 80) * i / 39;
            L.Monde.centrerCamera(j.x, j.y);
            L.Jeu.rendre();
            vus.push(L.B.stats.morceaux);
        }
        return { max: Math.max.apply(null, vus), plafond: L.Monde.MORCEAUX_MAX,
                 images: L.B.stats.images, fin: L.B.stats.morceaux };
    }""")
    assert r["max"] <= r["plafond"], f"{r['max']} morceaux en cache pour un plafond de {r['plafond']}"
    assert r["fin"] > 0 and r["images"] > 0


def test_la_mini_carte_est_cuite_une_seule_fois(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const a = L.Monde.miniCarte(), b = L.Monde.miniCarte();
        L.Hud.dessiner();
        return { meme: a === b, w: a.width, h: a.height,
                 eau: L.Monde.couleurMini('~'), mur: L.Monde.couleurMini('B'),
                 route: L.Monde.couleurMini('#'), herbe: L.Monde.couleurMini(','),
                 taille: [L.Hud.MINI.l, L.Hud.MINI.h] };
    }""")
    assert r["meme"] is True, "la mini-carte est repeinte a chaque appel"
    assert [r["w"], r["h"]] == [paquet["carte"]["largeur"], paquet["carte"]["hauteur"]]
    assert len({r["eau"], r["mur"], r["route"], r["herbe"]}) == 4, "les familles doivent se distinguer"
    assert r["taille"] == [64, 48]


def test_on_se_trouve_sur_la_carte_et_l_objectif_ne_bat_pas_pareil(banc):
    """⚠️ La demande de Martin : « un icone clignotant pour savoir ou on est ».
    Le joueur ETAIT dessine — un carre blanc de 2 px — mais depuis M8 la ville
    fait 421 x 213 tuiles et ce carre s'est perdu dans le gris. Ce n'etait pas un
    manque, c'etait une regression : il etait lisible sur le Faubourg.

    Deux pieges, et le test tient les deux : un repere qui clignote s'EFFACE une
    image sur deux (on ne cache pas la seule chose qu'on cherche — le joueur
    pulse, il ne disparait jamais), et deux choses qui battent au meme rythme se
    confondent (l'anneau du joueur contre le losange de l'objectif)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        // Un objectif a deux pas, dans le cadre de la mini-carte.
        L.Histoire.cible = function () { return { x: j.x + 40, y: j.y + 40, nom: 'ESSAI', couleur: '#e8b33c' }; };
        const joueur = [], cible = [], rayons = [];
        for (let i = 0; i < 96; i++) {
            o.frame(1);
            const m = L.Hud.marqueurs();
            joueur.push(m.joueur ? 1 : 0);
            rayons.push(m.joueur ? m.joueur.r : -1);
            cible.push(m.cible && m.cible.visible ? 1 : 0);
        }
        const m = L.Hud.marqueurs();
        return { joueur: joueur, cible: cible, rayons: rayons,
                 formes: [m.joueur.forme, m.cible.forme], dedans: m.cible.dedans,
                 pulse: L.Hud.PULSE_JOUEUR, battement: L.Hud.BATTEMENT_CIBLE };
    }""")
    assert all(r["joueur"]), "le repere du joueur disparait : on cache ce qu'on cherche"
    assert len(set(r["rayons"])) > 2, "l'anneau du joueur ne pulse pas : rien ne le ramene a l'oeil"
    assert 0 in r["cible"] and 1 in r["cible"], "l'objectif ne clignote plus"
    assert r["formes"] == ["anneau", "losange"], "les deux reperes ont la meme forme"
    assert r["pulse"] != r["battement"], "le joueur et l'objectif battent au meme rythme"
    assert r["dedans"] is True


def test_une_cible_hors_du_cadre_devient_une_fleche_et_pas_une_position(banc):
    """⚠️ Sur la mini-carte, une cible hors cadre BORNEE au bord est un mensonge :
    le code la collait au coin, et un objectif a deux cents tuiles s'affichait
    exactement comme un objectif a trois tuiles. Une fleche dit la direction ;
    une position inventee dit le contraire de la verite."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        function marqueurPour(dx, dy) {
            L.Histoire.cible = function () {
                return { x: Math.max(8, Math.min(c.pxW - 8, j.x + dx)),
                         y: Math.max(8, Math.min(c.pxH - 8, j.y + dy)), nom: 'LOIN', couleur: '#e8b33c' };
            };
            o.frame(1);
            const m = L.Hud.marqueurs().cible;
            return { forme: m.forme, x: m.x, y: m.y, dedans: m.dedans };
        }
        const est = marqueurPour(2400, 0);          // tout a l'est
        const sud = marqueurPour(0, 1200);          // tout au sud
        const pres = marqueurPour(32, 16);          // a deux pas
        return { est: est, sud: sud, pres: pres, mini: [L.Hud.MINI.x, L.Hud.MINI.y, L.Hud.MINI.l, L.Hud.MINI.h] };
    }""")
    assert r["est"]["forme"] == "fleche" and r["est"]["dedans"] is False
    assert r["sud"]["forme"] == "fleche" and r["sud"]["dedans"] is False
    assert (r["est"]["x"], r["est"]["y"]) != (r["sud"]["x"], r["sud"]["y"]), (
        "deux objectifs dans deux directions differentes pointent au meme endroit"
    )
    mx, my, large, haut = r["mini"]
    for cote in ("est", "sud"):
        assert mx <= r[cote]["x"] <= mx + large and my <= r[cote]["y"] <= my + haut, r[cote]
    assert r["pres"]["forme"] == "losange" and r["pres"]["dedans"] is True


def test_la_legende_de_la_carte_se_derive_de_la_table_des_couleurs(banc, paquet):
    """⚠️ Une legende recopiee a la main ment des qu'on ajoute un lieu — c'est
    exactement ce qui etait arrive a la table des couleurs : dix lieux declares,
    seize sur la carte, six gris. La legende se batit donc DEPUIS les donnees, et
    chaque lieu de la ville y a sa ligne."""
    familles = paquet["carte"]["familles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const carte = L.Monde.carte;
        const legende = L.Hud.legendeDeLaCarte(carte);
        const couleurs = carte.points.map(function (p) { return { slug: p.slug, famille: p.famille, couleur: L.Hud.couleurDeLieu(p) }; });
        // Et la carte plein ecran la dessine pour de vrai.
        L.Jeu.ouvrirCarte();
        const avant = L.B.stats.rects;
        o.frame(1);
        return { legende: legende, couleurs: couleurs, etat: L.B.etat, rects: L.B.stats.rects - avant,
                 points: carte.points.length };
    }""")
    attendues = {f: familles[f]["couleur"] for f in familles}
    for lieu in r["couleurs"]:
        assert lieu["famille"] in attendues, lieu
        assert lieu["couleur"] == attendues[lieu["famille"]], lieu
    vues = [e["famille"] for e in r["legende"]]
    assert vues == [f for f in familles if f in vues], "la legende doit suivre l'ordre de la table"
    assert set(vues) == {lieu["famille"] for lieu in r["couleurs"]}, (
        "la legende et les blips ne parlent pas des memes familles"
    )
    for entree in r["legende"]:
        assert entree["libelle"] == familles[entree["famille"]]["libelle"]
    assert r["etat"] == "carte" and r["rects"] > 0


def test_le_decor_solide_arrete_le_joueur_mais_pas_un_buisson(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        function pousser(type) {
            const d = L.B.entites.find(function (e) { return e.decor === type; });
            if (!d) return null;
            j.x = d.x; j.y = d.y + 20; j.vx = 0; j.vy = 0;
            for (let i = 0; i < 30; i++) L.Entites.deplacerCercle(j, 0, -1.2, L.Monde.MASQUE_PIETON);
            return Math.round(j.y - d.y);
        }
        return { arbre: pousser('arbre'), buisson: pousser('buisson'),
                 lampadaire: pousser('lampadaire') };
    }""")
    assert r["arbre"] is not None and r["arbre"] > 0, "on traverse les arbres"
    assert r["buisson"] is not None and r["buisson"] <= 0, "un buisson ne doit pas bloquer"
    assert r["lampadaire"] <= 0, "un lampadaire ne doit pas bloquer"


def test_on_ne_se_tient_pas_DANS_le_decor(banc):
    """Retour de Martin, capture a l'appui : le joueur debout au milieu du
    camion-restaurant, dans la carrosserie.

    ⚠️ La cause n'etait pas la collision mais sa FORME. Le camion fait 44 px
    de large et 8 px de profond ; son seul cercle (r 16) tenait dans la
    profondeur, alors il laissait 6 px de carrosserie libres de chaque cote.
    Chaque decor carre porte maintenant une boite `sol`, et ce juge pousse le
    joueur dessus par les quatre cotes : il doit rester DEHORS.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const dedans = [], vus = {};
        for (const d of L.B.entites) {
            if (!d.decor || !d.solide) continue;
            const f = L.DECORS[d.decor];
            if (!f || !f.sol || vus[d.decor]) continue;
            vus[d.decor] = true;
            [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (c) {
                j.x = d.x + c[0] * 60; j.y = d.y + c[1] * 60; j.vx = 0; j.vy = 0;
                for (let i = 0; i < 120; i++) L.Entites.deplacerCercle(j, -c[0] * 1.2, -c[1] * 1.2, L.Monde.MASQUE_PIETON);
                // Le cercle du joueur mord-il la boite au sol du decor ?
                const mordX = f.sol[0] + j.r - Math.abs(j.x - d.x);
                const mordY = f.sol[1] + j.r - Math.abs(j.y - d.y);
                const mord = Math.min(mordX, mordY);
                if (mord > 0.01) dedans.push({ decor: d.decor, cote: c.join(','), mord: +mord.toFixed(2) });
            });
        }
        return { dedans: dedans, boites: Object.keys(vus).sort() };
    }""")
    assert "camion_cuisine" in r["boites"], "le camion-restaurant de la capture doit etre teste"
    assert r["dedans"] == [], "le joueur se tient dans le dessin d'un decor"


def test_la_portee_de_recherche_couvre_la_plus_grosse_empreinte(banc):
    """⚠️ Le piege du jour ou l'on ajoutera un decor plus large : la recherche
    du decor autour de soi est un CERCLE, l'empreinte est une BOITE. Si le
    rayon ne va pas jusqu'au COIN de la boite, le decor n'est meme pas trouve
    — pas de collision ratee, pas de test rouge : rien, on lui passe au
    travers. Ce juge refait le calcul sur chaque decor solide.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const trop = [];
        const rayonHumain = 5;             // joueur et pietons ont tous r = 5
        for (const nom in L.DECORS) {
            const f = L.DECORS[nom];
            if (!f.solide) continue;
            const coin = f.sol ? Math.hypot(f.sol[0] + rayonHumain, f.sol[1] + rayonHumain) : f.r + rayonHumain;
            const exige = coin - rayonHumain;
            if (exige > L.Entites.PORTEE_DECOR) trop.push({ decor: nom, exige: +exige.toFixed(1) });
        }
        return { trop: trop, portee: L.Entites.PORTEE_DECOR };
    }""")
    assert r["trop"] == [], f"PORTEE_DECOR ({r['portee']}) ne couvre pas ces decors"


def test_la_foule_ne_se_traverse_plus(banc):
    """Retour de Martin : « empeche que les choses se chevauchent ».

    ⚠️ Personne ne poussait personne : deux passants qui se croisaient se
    superposaient EXACTEMENT. Mesure avant correctif, en marchant deux minutes
    dans la ville : 1032 paires enfoncees l'une dans l'autre en 960 images,
    jusqu'a 9,9 px — deux corps de 10 px parfaitement confondus. Apres : 0,1 px
    au pire, des la premiere image (personne ne NAIT non plus dans quelqu'un).
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        let paires = 0, pire = 0, images = 0, nes = 0;
        // Naitre dans quelqu'un se voit a un chevauchement PLEIN (meme pixel) :
        // les deux branches de placeDeNaissance rendent un centre de tuile.
        const touches = ['KeyD', 'KeyW', 'KeyA', 'KeyS'];
        for (let bloc = 0; bloc < 24; bloc++) {
            const t = touches[bloc % 4];
            o.touche(t);
            for (let k = 0; k < 40; k++) {
                o.frame(1); images++;
                const gens = L.B.entites.filter(L.Entites.deboutDansLaFoule);
                for (let a = 0; a < gens.length; a++) {
                    for (let b = a + 1; b < gens.length; b++) {
                        const d = Math.hypot(gens[a].x - gens[b].x, gens[a].y - gens[b].y);
                        const chevauche = gens[a].r + gens[b].r - d;
                        if (chevauche > 0) { paires++; pire = Math.max(pire, chevauche); }
                        if (chevauche > gens[a].r + gens[b].r - 0.001) nes++;
                    }
                }
            }
            o.relacher(t);
        }
        return { images: images, paires: paires, pire: +pire.toFixed(2), nes_empiles: nes };
    }""")
    assert r["images"] == 960
    assert r["pire"] < 1.0, f"deux personnes se chevauchent de {r['pire']} px"
    assert r["nes_empiles"] == 0, "on ne nait pas dans quelqu'un"


def test_courir_ne_permet_pas_de_traverser_les_gens(banc, paquet):
    """⚠️ Le plafond de separation doit passer DEVANT les jambes les plus
    rapides du jeu. Fixe a 1,5 px, il arretait bien le joueur qui MARCHE
    (1,2 px/image) et laissait passer celui qui SPRINTE (2,1) : il suffisait
    de tenir MAJ pour entrer dans le vendeur.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const pas = L.Entites.pasDeDemele();
        const t = L.B.entites.find(function (e) { return e.personnage === 'ti_guy'; });
        function foncer(sprint) {
            j.x = t.x - 40; j.y = t.y; j.vx = 0; j.vy = 0;
            if (sprint) o.touche('ShiftLeft');
            o.touche('KeyD'); o.frame(120); o.relacher('KeyD');
            if (sprint) o.relacher('ShiftLeft');
            return +Math.hypot(j.x - t.x, j.y - t.y).toFixed(1);
        }
        return { pas: pas, marche: foncer(false), sprint: foncer(true), r: j.r + t.r };
    }""")
    vitesses = paquet["recherche"]["vitesses"]
    assert r["pas"] > vitesses["joueur_sprint"], "on sprinte plus vite qu'on ne se demele"
    assert r["marche"] >= r["r"] - 0.5, "on entre dans un personnage en marchant"
    assert r["sprint"] >= r["r"] - 0.5, "on entre dans un personnage en courant"


def test_celui_qui_tient_son_poste_cede_puis_revient(banc):
    """⚠️ « Fige » veut dire « il tient son poste », pas « c'est un poteau ».
    Vraiment immobile, un donneur plante sur le trottoir bouchait la rue POUR
    TOUJOURS : l'agent lance aux trousses du joueur venait buter dessus et y
    restait — 260 images sur place, l'arrestation n'arrivait jamais. Il se
    laisse donc bousculer de quelques pixels, et il rentre chez lui.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const t = L.B.entites.find(function (e) { return e.personnage === 'ti_guy'; });
        o.frame(2);
        const poste = { x: t.plante ? t.plante.x : t.x, y: t.plante ? t.plante.y : t.y };
        j.x = poste.x - 40; j.y = poste.y; j.vx = 0; j.vy = 0;
        o.touche('ShiftLeft'); o.touche('KeyD'); o.frame(240);
        const pousse = Math.hypot(t.x - poste.x, t.y - poste.y);
        o.relacher('KeyD'); o.relacher('ShiftLeft');
        j.x = poste.x - 200; j.y = poste.y;              // on le lache
        o.frame(180);
        return { pousse: +pousse.toFixed(1), rentre: +Math.hypot(t.x - poste.x, t.y - poste.y).toFixed(1),
                 etat: t.etat };
    }""")
    assert r["pousse"] > 0.5, "on doit pouvoir le tasser un peu, sinon il bouche la rue"
    assert r["pousse"] < 12, f"on l'a promene de {r['pousse']} px : il n'est plus a son poste"
    assert r["rentre"] < 1, "lache, il doit revenir a sa place"
    assert r["etat"] == "fige"


def test_le_son_survit_a_l_absence_d_audio(banc, paquet):
    """Sous Node il n'y a pas d'AudioContext : le jeu doit jouer quand meme."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Son.reveiller();
        const avant = L.B.t;
        for (const nom in L.Son.SFX) L.Son.SFX[nom]();
        L.Son.boucle('sirene', true); L.Son.boucle('sirene', false);
        o.tape('KeyD', 30);
        return { charges: L.Son.charges, pret: L.Son.pret(), contexte: L.Son.contexte,
                 avance: L.B.t > avant, sons: L.B.defs.audio.echantillons.length,
                 sansFichier: L.B.defs.audio.echantillons.filter(function (e) { return !e.fichiers.length; }).map(function (e) { return e.slug; }) };
    }""")
    assert r["contexte"] is None and r["pret"] is False
    assert r["charges"] == 0, "rien ne doit se charger sans AudioContext"
    assert r["avance"] is True, "la boucle s'est arretee sur un son"
    assert r["sons"] == len(paquet["audio"]["echantillons"])
    assert r["sansFichier"] == [], f"sons declares sans fichier : {r['sansFichier']}"


# --- M2 : pietons et poings ------------------------------------------------

def test_la_rue_se_peuple_puis_s_oublie(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(600);
        const j = L.B.joueur;
        // ⚠️ Les marchands derriere leur kiosque ne sont pas la foule.
        const pietons = L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.metier; });
        const loin = pietons.filter(function (e) {
            return Math.hypot(e.x - j.x, e.y - j.y) > L.Entites.BULLE_OUBLI + 80;
        });
        const dansLEcran = pietons.filter(function (e) { return L.Entites.visibleAEcran(e.x, e.y, 0); });
        // On se teleporte a l'autre bout : la foule doit suivre, pas rester la.
        const c = L.Monde.carte;
        j.x = c.pxW - 200; j.y = c.pxH - 200;
        L.Monde.centrerCamera(j.x, j.y);
        o.frame(600);
        const apres = L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.metier; });
        const proches = apres.filter(function (e) {
            return Math.hypot(e.x - j.x, e.y - j.y) < L.Entites.BULLE_OUBLI;
        });
        return { avant: pietons.length, loin: loin.length, vus: dansLEcran.length,
                 apres: apres.length, proches: proches.length, max: L.Entites.MAX_PIETONS,
                 sol: apres.map(function (e) { return L.Monde.solidite(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT)); }) };
    }""")
    # +1 : une mere nait avec son petit, et la bulle compte les vivants AVANT.
    assert 4 <= r["avant"] <= r["max"] + 1, "la rue est vide ou bondee"
    assert r["loin"] == 0, "des pietons trainent hors de la bulle"
    assert r["vus"] > 0, "personne a l'ecran"
    assert r["proches"] == r["apres"] > 0, "la foule n'a pas suivi le joueur"
    assert all(s in (0, 3) for s in r["sol"]), "un pieton est ne dans un mur"


def test_l_arc_de_melee_touche_devant_et_pas_derriere(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(4);
        const devant = o.poser('passant', 14, 0);
        const derriere = o.poser('passant', -14, 0);
        o.viser(devant);
        L.Combat.frapper(L.B.joueur, false);
        for (let i = 0; i < 20; i++) { L.Entites.indexer(); L.Combat.maj(); }
        return { devant: devant.vie, derriere: derriere.vie, max: devant.vieMax };
    }""")
    assert r["devant"] < r["max"], "le coup n'a pas porte devant"
    assert r["derriere"] == r["max"], "le coup a porte DERRIERE le joueur"


def test_un_coup_ne_compte_qu_une_fois(banc, paquet):
    degats = next(a for a in paquet["armes"] if a["slug"] == "poings")["degats"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(5);
        const cible = o.poser('ouvrier', 12, 0);
        o.viser(cible);
        const avant = cible.vie;
        L.Combat.frapper(L.B.joueur, false);
        for (let i = 0; i < 30; i++) { L.Entites.indexer(); L.Combat.maj(); }
        return { perdu: avant - cible.vie };
    }""")
    assert r["perdu"] == degats, f"un coup a enleve {r['perdu']} au lieu de {degats}"


def test_les_poings_assomment_et_le_couteau_tue(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(6);
        function cogner(arme, arch) {
            L.B.joueur.arme = arme;
            if (arme !== 'poings') L.B.partie.armes[arme] = { mun: null, usure: 0 };
            const c = o.poser(arch, 12, 0);
            c.courage = 0;
            for (let coup = 0; coup < 30 && c.vie > 0; coup++) {
                L.B.joueur.x = c.x - 12; L.B.joueur.y = c.y;
                o.viser(c);
                L.Combat.frapper(L.B.joueur, false);
                for (let i = 0; i < 30; i++) { L.Entites.indexer(); L.Combat.maj(); }
            }
            const etat = { vivant: c.vivant, etat: c.etat, vie: c.vie };
            // ⚠️ On retire le corps avant la manche suivante : sinon le couteau
            // acheve le KO d'a cote (ce qui est juste, mais fausse le compte).
            L.Entites.retirer(c);
            L.Entites.indexer();
            return etat;
        }
        const poing = cogner('poings', 'passant');
        const lame = cogner('couteau', 'passante');
        return { poing: poing, lame: lame, tues: L.B.partie.stats.tues,
                 decals: L.B.decals.length, sang: L.B.options.sang };
    }""")
    assert r["poing"]["vivant"] is True and r["poing"]["etat"] == "assomme", \
        "les poings doivent assommer, pas tuer — c'est ce qui separe 1 etoile de 3"
    assert r["lame"]["vivant"] is False and r["lame"]["etat"] == "mort"
    assert r["tues"] == 1
    assert r["decals"] > 0, "pas une goutte de sang"


def test_le_sang_et_les_particules_sont_plafonnes(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        for (let i = 0; i < 400; i++) {
            L.Entites.sang(j.x + (i % 40), j.y + (i % 30), 8);
            L.Entites.particule(j.x, j.y, 0, 0, 60, '#fff', 1);
        }
        return { decals: L.B.decals.length, particules: L.B.particules.length,
                 maxD: L.Entites.MAX_DECALS, maxP: L.Entites.MAX_PARTICULES };
    }""")
    assert r["decals"] == r["maxD"], "les decalques de sang ne sont pas plafonnes"
    assert r["particules"] == r["maxP"], "les particules ne sont pas plafonnees"


def test_l_arme_du_mort_se_ramasse(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(8);
        const cravate = o.poser('cravate', 14, 0);
        const armeDeLaCravate = cravate.arme;
        L.Entites.tuer(cravate, L.B.joueur);
        L.Entites.indexer();
        const objet = L.Combat.objetSousLaMain(L.B.joueur);
        o.tape('KeyE', 2);
        return { arme: armeDeLaCravate, objet: objet ? objet.arme : null,
                 sac: Object.keys(L.B.partie.armes).sort(), porte: L.B.joueur.arme,
                 restes: L.B.entites.filter(function (e) {
                     return e.type === 'ramassage' && e.arme === 'batte';
                 }).length };
    }""")
    assert r["arme"] == "batte"
    assert r["objet"] == "batte", "le mort n'a pas lache son arme"
    assert "batte" in r["sac"] and r["porte"] == "batte"
    assert r["restes"] == 0, "l'arme ramassee traine encore par terre"


def test_le_pickpocket_se_fait_dans_le_dos(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(9);
        const j = L.B.joueur;
        const face = o.poser('dame', 14, 0);
        face.argent = 40;
        L.Entites.regarder(face, -1, 0);            // elle regarde le joueur
        const deFace = L.Combat.pickpocket(j);
        L.Entites.regarder(face, 1, 0);             // elle lui tourne le dos
        L.Entites.indexer();
        const argentAvant = L.B.partie.argent;
        const deDos = L.Combat.pickpocket(j);
        return { deFace: deFace, deDos: deDos, gain: L.B.partie.argent - argentAvant,
                 reste: face.argent, etat: face.etat, crimes: L.B.partie.stats.crimes };
    }""")
    assert r["deFace"] is False, "on fait les poches de quelqu'un qui nous regarde"
    assert r["deDos"] is True and r["gain"] == 40 and r["reste"] == 0
    assert r["etat"] == "fuit"
    assert r["crimes"] >= 1


def test_le_pistolet_tire_touche_et_compte_ses_balles(banc, paquet):
    pistolet = next(a for a in paquet["armes"] if a["slug"] == "pistolet")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(11);
        const j = L.B.joueur;
        // La rue est peuplee des le depart : on la vide, la visee assistee
        // irait chercher le premier passant venu.
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        L.Entites.indexer();
        j.arme = 'pistolet';
        L.B.partie.armes.pistolet = { mun: 12, usure: 0 };
        const cible = o.poser('ouvrier', 90, 0);
        cible.courage = 0;
        o.viser(cible);
        const avant = cible.vie;
        L.Combat.frapper(j);
        let projectiles = 0;
        for (let i = 0; i < 40; i++) {
            L.Entites.indexer();
            projectiles = Math.max(projectiles, L.B.entites.filter(function (e) { return e.type === 'projectile'; }).length);
            L.Combat.majProjectiles();
        }
        return { perdu: avant - cible.vie, mun: L.B.partie.armes.pistolet.mun,
                 projectiles: projectiles, etoiles: L.B.recherche.etoiles,
                 restants: L.B.entites.filter(function (e) { return e.type === 'projectile'; }).length };
    }""")
    assert r["perdu"] == pistolet["degats"], "la balle n'a pas touche"
    assert r["mun"] == 11, "la balle n'a pas ete comptee"
    assert r["projectiles"] == 1
    assert r["restants"] == 0, "un projectile traine apres avoir touche"


def test_rien_n_est_compte_sans_temoin(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        // Personne autour : le crime passe inapercu.
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        L.Entites.indexer();
        const seul = L.Police.quelqu_un_voit(j.x, j.y, null);
        // Un passant qui regarde dans notre direction, lui, voit tout.
        const temoin = o.poser('passant', 40, 0);
        L.Entites.regarder(temoin, -1, 0);
        L.Entites.indexer();
        const vu = L.Police.quelqu_un_voit(j.x, j.y, null);
        // ... mais pas s'il est assomme.
        temoin.etat = 'assomme';
        const assomme = L.Police.quelqu_un_voit(j.x, j.y, null);
        temoin.etat = 'flane';
        // ... ni s'il regarde ailleurs.
        L.Entites.regarder(temoin, 1, 0);
        const dosTourne = L.Police.quelqu_un_voit(j.x, j.y, null);
        return { seul: seul, vu: vu, assomme: assomme, dosTourne: dosTourne };
    }""")
    assert r["seul"] is False, "un crime sans temoin ne doit rien declencher"
    assert r["vu"] is True, "un passant en face ne voit rien ?"
    assert r["assomme"] is False, "un temoin assomme ne temoigne pas"
    assert r["dosTourne"] is False, "un temoin de dos ne voit pas"


def test_la_bagarre_tient_le_budget(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(13);
        o.singe(2500, 3, ['KeyW', 'KeyA', 'KeyS', 'KeyD', 'Space', 'ShiftLeft', 'KeyE', 'Tab']);
        const s = L.B.stats;
        return { etat: L.B.etat, entites: L.B.entites.length, actifs: s.actifs,
                 particules: L.B.particules.length, decals: L.B.decals.length,
                 images: s.images, morceaux: s.morceaux,
                 nan: isNaN(L.B.joueur.x) || isNaN(L.B.joueur.y) };
    }""")
    assert r["etat"] in ("jeu", "pause")
    assert not r["nan"]
    assert r["actifs"] <= 30, f"{r['actifs']} pietons actifs"
    assert r["particules"] <= 300 and r["decals"] <= 150
    assert r["images"] <= 160, f"{r['images']} drawImage par image"


def test_un_meurtre_vu_fait_monter_les_etoiles(banc, paquet):
    """La chaine complete : je tue, quelqu'un voit, il le raconte a un agent,
    et LA la police le sait — pas avant (M4 : un temoin se rachete)."""
    gravite = paquet["recherche"]["delits"]["mort_pieton"]["etoiles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(21);
        function meurtre(avecTemoin) {
            L.Police.remiseAZero();
            L.B.crimes.length = 0;
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
            const victime = o.poser('passant', 14, 0);
            let temoin = null;
            if (avecTemoin) {
                temoin = o.poser('passante', 60, 0);
                temoin.probaTemoin = 1; temoin.etat = 'flane';
                L.Entites.regarder(temoin, -1, 0);
            }
            L.Entites.indexer();
            L.Entites.tuer(victime, L.B.joueur);
            const surLeCoup = { etoiles: L.B.recherche.etoiles, chaleur: L.B.recherche.chaleur,
                                temoin: temoin ? temoin.etat : null, crime: !!(temoin && temoin.crime) };
            if (!temoin) return { surLeCoup: surLeCoup };
            // Un agent arrive dans le coin, de dos : le temoin court le lui dire.
            const a = L.Police.creerAgent(temoin.x + 40, temoin.y, 'flane');
            L.Entites.regarder(a, 1, 0);
            L.Entites.indexer();
            let quand = -1;
            for (let i = 0; i < 400 && quand < 0; i++) { o.frame(1); if (temoin.crime && temoin.crime.rapporte) quand = i; }
            return { surLeCoup: surLeCoup, quand: quand,
                     chaleur: L.B.recherche.chaleur + L.B.recherche.etoiles * 100 };
        }
        const sansTemoin = meurtre(false);
        const avecTemoin = meurtre(true);
        return { sans: sansTemoin, avec: avecTemoin,
                 chaleurParGravite: L.B.defs.recherche.chaleur_par_gravite };
    }""")
    assert r["sans"]["surLeCoup"]["chaleur"] == 0, "un meurtre que personne ne voit ne chauffe pas"
    assert r["avec"]["surLeCoup"]["chaleur"] == 0 and r["avec"]["surLeCoup"]["etoiles"] == 0, \
        "sans agent dans le coin, la police ne sait rien encore"
    assert r["avec"]["surLeCoup"]["temoin"] == "temoin" and r["avec"]["surLeCoup"]["crime"] is True
    assert 0 <= r["avec"]["quand"] < 400, "le temoin n'a pas rejoint l'agent"
    assert r["avec"]["chaleur"] == gravite * r["chaleurParGravite"], \
        "le temoin n'a pas transmis la gravite du crime"


def test_des_armes_de_fortune_trainent_en_ville(banc, paquet):
    fortunes = {a["slug"] for a in paquet["armes"] if a["usures"] > 0 and a["prix"] == 0}
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(900);
        const objets = L.B.entites.filter(function (e) { return e.type === 'ramassage'; });
        // On en ramasse une et on la casse a force de cogner.
        const arme = objets.length ? objets[0].arme : null;
        let usure = null, casse = null;
        if (arme) {
            L.Combat.ramasserArme(arme, null);
            L.B.joueur.arme = arme;
            const def = L.Combat.armeDef(arme);
            for (let coup = 0; coup < def.usures + 1; coup++) {
                const cible = o.poser('ouvrier', 12, 0);
                cible.vie = 999; cible.vieMax = 999;
                o.viser(cible);
                L.Combat.frapper(L.B.joueur, false);
                for (let i = 0; i < 40; i++) { L.Entites.indexer(); L.Combat.maj(); }
                L.Entites.retirer(cible);
            }
            usure = def.usures;
            casse = !L.B.partie.armes[arme];
        }
        return { objets: objets.length, armes: objets.map(function (e) { return e.arme; }),
                 arme: arme, usure: usure, casse: casse, porte: L.B.joueur.arme };
    }""")
    assert r["objets"] > 0, "aucune arme de fortune ne traine dans la rue"
    assert set(r["armes"]) <= fortunes, r["armes"]
    assert r["casse"] is True, f"la {r['arme']} n'a pas casse apres {r['usure']} coups"
    assert r["porte"] == "poings", "on garde une arme cassee a la main"


# --- La vie de rue : enfants, meres, kiosques, la Brume -------------------


def test_un_enfant_ne_peut_pas_etre_touche(banc):
    """⚠️ Regle du moteur, pas consigne : RIEN n'atteint un enfant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const j = L.B.joueur;
        const petit = o.poser('enfant', 12, 0);
        o.viser(petit);
        const avant = petit.vie;
        // Au poing, au couteau, et d'une balle en pleine poitrine.
        j.arme = 'couteau'; L.B.partie.armes.couteau = { mun: null, usure: 0 };
        for (let coup = 0; coup < 6; coup++) {
            L.Combat.frapper(j, true);
            for (let i = 0; i < 30; i++) { L.Entites.indexer(); L.Combat.maj(); }
        }
        const auCouteau = petit.vie;
        const direct = L.Entites.blesser(petit, 999, j, {});
        return { avant: avant, auCouteau: auCouteau, direct: direct,
                 vivant: petit.vivant, etat: petit.etat, tues: L.B.partie.stats.tues,
                 intouchable: petit.intouchable, sprite: petit.sprite };
    }""")
    assert r["intouchable"] is True and r["sprite"] == "enfant"
    assert r["auCouteau"] == r["avant"], "un enfant a perdu de la vie"
    assert r["direct"] is False, "blesser() a accepte de toucher un enfant"
    assert r["vivant"] is True and r["tues"] == 0
    assert r["etat"] == "fuit", "il devrait detaler"


def test_la_mere_ne_sort_pas_sans_son_petit(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(32);
        const mere = o.poser('mere', 30, 0);
        mere.etat = 'flane';
        const petit = mere.petit;
        // On eloigne le petit : il doit revenir vers elle.
        petit.x = mere.x + 120; petit.y = mere.y + 80;
        const avant = Math.hypot(petit.x - mere.x, petit.y - mere.y);
        o.frame(240);
        const apres = Math.hypot(petit.x - mere.x, petit.y - mere.y);
        return { arch: petit ? petit.arch : null, avant: avant, apres: apres,
                 suit: petit.suit === mere };
    }""")
    assert r["arch"] == "enfant", "la mere est sortie sans son petit"
    assert r["suit"] is True
    assert r["apres"] < r["avant"], "le petit ne rejoint pas sa mere"


def test_le_kiosque_vend_de_la_vie_contre_de_l_argent(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === 'hotdog'; })[0];
        j.x = etal.x; j.y = etal.y + 22; j.vie = 40; L.B.partie.argent = 100;
        L.Entites.indexer();
        const achat = L.Missions.interagir(j);
        const apres = { vie: j.vie, argent: L.B.partie.argent };
        // Sans le sou, on ne mange pas.
        L.B.partie.argent = 1; j.vie = 40;
        const refus = L.Missions.interagir(j);
        const vendeurs = L.B.entites.filter(function (e) { return e.metier === 'ambulant'; }).length;
        const etals = L.B.entites.filter(function (e) { return e.type === 'ambulant'; }).length;
        return { achat: achat, apres: apres, refus: refus, vieApresRefus: j.vie,
                 argentApresRefus: L.B.partie.argent, vendeurs: vendeurs, etals: etals };
    }""")
    assert r["achat"] is True
    assert r["apres"]["argent"] == 100 - tarifs["hotdog"]
    assert r["apres"]["vie"] == 40 + tarifs["hotdog_pv"]
    assert r["refus"] is True and r["vieApresRefus"] == 40 and r["argentApresRefus"] == 1
    assert r["etals"] >= 6 and r["vendeurs"] == r["etals"], "un kiosque sans personne derriere"


def test_manger_redonne_du_souffle_et_le_cafe_reveille(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    cafe = paquet["economie"]["cafe"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.heure = 0.4;                    // la roulotte a cafe est ouverte
        L.B.partie.argent = 200;
        function acheter(slug) {
          const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === slug; })[0];
          j.x = etal.x; j.y = etal.y + 22;
          L.Entites.indexer();
          return L.Missions.interagir(j);
        }
        j.endurance = 20; j.vie = 40;
        const hotdog = acheter('hotdog');
        const apres = { souffle: j.endurance, vie: j.vie, cafeine: j.cafeine };
        // Manger a plein souffle ne fait pas deborder la barre.
        j.endurance = 100; acheter('hotdog');
        const plein = j.endurance;
        j.endurance = 20;
        const achatCafe = acheter('cafe');
        return { hotdog: hotdog, apres: apres, plein: plein, achatCafe: achatCafe,
                 souffleCafe: j.endurance, cafeine: j.cafeine };
    }""")
    assert r["hotdog"] is True
    assert r["apres"]["souffle"] == 20 + tarifs["hotdog_souffle"]
    assert r["apres"]["vie"] == 40 + tarifs["hotdog_pv"]
    assert r["apres"]["cafeine"] == 0, "un hot-dog nourrit, il ne reveille pas"
    assert r["plein"] == 100, "le souffle deborde"
    assert r["achatCafe"] is True
    assert r["souffleCafe"] == 20 + tarifs["cafe_souffle"]
    assert r["cafeine"] == cafe["duree_s"] * 60


def test_le_cafe_fait_courir_deux_fois_plus_longtemps(banc, paquet):
    """⚠️ Ce qui s'achete, c'est la DUREE du sprint, jamais sa vitesse.

    On mesure les deux : combien d'images on tient au sprint d'un souffle
    plein a zero (ca doit doubler), et la distance parcourue par image (elle
    ne doit pas bouger d'un pixel — sinon la police ne rattrape plus personne).
    """
    cafe = paquet["economie"]["cafe"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        function tenir() {
          j.endurance = 100;
          const depart = { x: j.x, y: j.y };
          let n = 0;
          o.touche('ShiftLeft'); o.touche('KeyA');
          while (j.endurance > 0 && n < 2000) { o.frame(1); n++; }
          o.relacher('KeyA'); o.relacher('ShiftLeft');
          return { images: n, px: Math.hypot(j.x - depart.x, j.y - depart.y) };
        }
        const ajeun = tenir();
        L.Missions.cafeine(j);
        const pose = j.cafeine;
        const souscafe = tenir();
        return { ajeun: ajeun, souscafe: souscafe, pose: pose, reste: j.cafeine };
    }""")
    assert r["ajeun"]["images"] > 0 and r["souscafe"]["images"] < 2000
    # Le rapport, pas le compte : la premiere image d'une course part avant que
    # l'axe ne soit lu, et une image d'ecart ne dit rien de l'equilibrage.
    assert r["souscafe"]["images"] / r["ajeun"]["images"] > 1 / cafe["depense"] - 0.15
    assert r["pose"] == cafe["duree_s"] * 60
    assert r["reste"] == r["pose"] - r["souscafe"]["images"], "la minuterie doit tomber d'une image par image"
    vitesse_ajeun = r["ajeun"]["px"] / r["ajeun"]["images"]
    vitesse_cafe = r["souscafe"]["px"] / r["souscafe"]["images"]
    assert abs(vitesse_cafe - vitesse_ajeun) < 0.05, "le cafe accelere le joueur : la police ne le rattrapera plus"


def test_le_kiosque_a_journaux_ferme_la_nuit(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const journaux = L.Missions.commerceDe('journaux');
        const camion = L.Missions.commerceDe('camion_cuisine');
        L.B.partie.heure = 0.5;
        const midi = [L.Missions.ouvert(journaux), L.Missions.ouvert(camion)];
        L.B.partie.heure = 0.95;
        const nuit = [L.Missions.ouvert(journaux), L.Missions.ouvert(camion)];
        return { midi: midi, nuit: nuit, heures: journaux.heures };
    }""")
    assert r["midi"] == [True, True]
    assert r["nuit"] == [False, True], "le camion-restaurant, lui, veille"


def test_la_compagnie_se_paie_et_refuse_quand_la_police_cherche(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(33);
        const j = L.B.joueur;
        const fille = o.poser('racoleuse', 12, 0);
        fille.etat = 'arret';
        L.Entites.indexer();
        j.vie = 50; L.B.partie.argent = 200;
        L.B.recherche.etoiles = 2;
        const recherche = L.Missions.interagir(j);
        const apresRecherche = { vie: j.vie, argent: L.B.partie.argent };
        L.B.recherche.etoiles = 0;
        const ok = L.Missions.interagir(j);
        return { metier: fille.metier, recherche: recherche, apresRecherche: apresRecherche,
                 ok: ok, vie: j.vie, argent: L.B.partie.argent, fondu: !!L.B.fondu };
    }""")
    assert r["metier"] == "compagnie"
    assert r["recherche"] is True and r["apresRecherche"]["argent"] == 200, \
        "elle a servi alors que la police cherchait le joueur"
    assert r["ok"] is True
    assert r["argent"] == 200 - tarifs["compagnie"]
    assert r["vie"] == 50 + tarifs["compagnie_pv"]
    assert r["fondu"] is True, "ca doit passer par un fondu, pas par une scene"


def test_la_fille_de_la_brume_a_une_silhouette_a_elle(banc):
    """⚠️ Retour de Martin : « on ne distingue plus les prostituées, elles sont
    trop pareilles que tout le monde. » Elles etaient le corps commun repeint
    en rose — et a douze pixels de large, sous la teinte de nuit, une couleur
    ne distingue rien. Ce juge tient le CONTOUR : la jupe s'evase plus large
    que les epaules (personne d'autre), et sous l'ourlet les jambes sont de la
    peau la ou tout le monde a du pantalon."""
    r = banc(r"""function (L, o) {
        // La largeur de chaque rangee du dessin de face, pixels poses.
        function largeurs(nom) {
            return L.SPRITES[nom].poses.bas[0].map(function (l) { return l.replace(/\./g, '').length; });
        }
        const f = largeurs('racoleuse'), j = largeurs('joueur');
        const jambes = L.SPRITES.racoleuse.poses.bas[0][13];
        L.Jeu.commencer();
        const fille = o.poser('racoleuse', 12, 0);
        return { sprite: fille.sprite, epaulesF: f[7], jupeF: Math.max(f[11], f[12], f[13]),
                 epaulesJ: j[7], hanchesJ: Math.max(j[11], j[12], j[13]),
                 jambes: jambes, cheveux: fille.swaps.h, robe: fille.swaps.c,
                 poses: Object.keys(L.Atlas.cuire('racoleuse', L.SPRITES.racoleuse, null).poses).sort() };
    }""")
    assert r["sprite"] == "racoleuse", "elle porte encore le corps de tout le monde"
    assert r["jupeF"] - r["epaulesF"] >= 4, "la jupe ne s'evase pas : de loin, c'est un passant"
    assert r["hanchesJ"] - r["epaulesJ"] <= 1, "le corps commun, lui, tombe droit — c'est le contraste"
    assert "s" in r["jambes"] and "p" not in r["jambes"], "les jambes ne sont pas nues sous l'ourlet"
    assert r["cheveux"] == "#f2d27a" and r["robe"] == "#ff3d8e"
    # ⚠️ Elle meurt comme les autres : sans `couche`, un KO restait debout.
    for pose in ("bas", "haut", "cote", "gauche", "droite", "couche"):
        assert pose in r["poses"], pose


def test_la_fille_de_la_brume_tient_son_coin(banc):
    """Le deuxieme signe, celui qu'on lit avant meme la robe : elle ATTEND.
    Elle flanait comme tout le monde dix secondes apres etre apparue."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(34);
        const fille = o.poser('racoleuse', 20, 0);
        const passante = o.poser('passante', -20, 0);
        fille.etat = 'flane'; passante.etat = 'flane';
        const p0 = { x: fille.x, y: fille.y };
        let ecartFille = 0, cheminPassante = 0, arrets = 0;
        let px = passante.x, py = passante.y;
        for (let i = 0; i < 80; i++) {
            o.frame(30);
            if (fille.etat === 'arret') arrets++;
            ecartFille = Math.max(ecartFille, Math.hypot(fille.x - p0.x, fille.y - p0.y));
            cheminPassante += Math.hypot(passante.x - px, passante.y - py);
            px = passante.x; py = passante.y;
        }
        return { poste: !!fille.poste, arrets: arrets,
                 fille: Math.round(ecartFille), passante: Math.round(cheminPassante) };
    }""")
    assert r["poste"] is True, "elle n'a pas de coin a tenir"
    assert r["fille"] < 80, "en 40 s elle a quitte son coin"
    # ⚠️ On mesure le CHEMIN de la passante, pas son ecart au depart : une
    # flaneuse qui revient sur ses pas fait un long chemin et un petit ecart.
    # L'ecart tombait a 113 px sur certaines graines — le seuil jugeait le
    # hasard du trajet, pas le fait qu'elle flane.
    assert r["passante"] > 400, "⚠️ une passante, elle, doit continuer de flaner"
    assert r["arrets"] > 30, "elle marche plus qu'elle n'attend"


def test_le_hud_nomme_la_fille_de_la_brume(banc, paquet):
    """Derniere preuve, a bout de bras : l'invite ACTION la nomme et donne le
    prix — avant, on appuyait sur ACTION en esperant que c'en etait une."""
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const fille = o.poser('racoleuse', 14, 0);
        fille.etat = 'arret';
        L.Entites.indexer();
        L.Missions.majInvite(j);
        const pres = L.B.invite;
        fille.x = j.x + 200; fille.y = j.y + 200;
        L.Entites.indexer();
        L.Missions.majInvite(j);
        return { pres: pres, loin: L.B.invite };
    }""")
    assert r["pres"] == "LA BRUME — " + str(tarifs["compagnie"]) + " $"
    assert r["loin"] != r["pres"], "l'invite la promet alors qu'elle est partie"


# --- M3 : vehicules ----------------------------------------------------------


def test_on_vole_un_char_et_on_en_descend(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(41);
        const j = L.B.joueur;
        j.y += 40;                                  // loin de la porte du terminus : E y entrerait
        const v = o.char('auto', 24, 0, 0);
        const avantVol = L.B.partie.stats.volees;
        o.tape('KeyE', 2);
        const dedans = { conducteur: v.conducteur === j, dansVehicule: j.dansVehicule === v,
                         dessine: j.dessine, contexte: o.elements.tactile.querySelectorAll('[data-a]')[0].textContent };
        o.tape('KeyE', 2);
        return { dedans: dedans, dehors: { conducteur: v.conducteur, dansVehicule: j.dansVehicule, dessine: j.dessine },
                 volees: L.B.partie.stats.volees - avantVol, vole: v.vole,
                 loin: Math.hypot(j.x - v.x, j.y - v.y) };
    }""")
    assert r["dedans"]["conducteur"] and r["dedans"]["dansVehicule"] and r["dedans"]["dessine"] is False
    assert r["dedans"]["contexte"] == "KLAXON", "les boutons tactiles n'ont pas change d'etiquette"
    assert r["dehors"]["conducteur"] is None and r["dehors"]["dansVehicule"] is None and r["dehors"]["dessine"] is True
    assert r["volees"] == 1 and r["vole"] is True
    assert 8 < r["loin"] < 40, "le joueur doit descendre A COTE du char"


def test_la_vitesse_max_et_la_marche_arriere(banc, paquet):
    auto = next(v for v in paquet["vehicules"] if v["slug"] == "auto")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        // ⚠️ On mesure la physique, pas la chance : sans trafic sur la ligne.
        // (Un char du trafic s'y trouvait selon la graine, et bloquait la mesure.)
        L.B.defs.conduite.trafic.vehicules_max = 0;
        L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(function (e) { L.Entites.retirer(e); });
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const x0 = v.x;
        o.touche('KeyW'); o.frame(300); o.relacher('KeyW');
        const pleine = v.vitesse, x1 = v.x;
        o.touche('KeyS'); o.frame(200);
        const recul = v.vitesse;
        o.relacher('KeyS');
        return { pleine: pleine, avance: x1 - x0, recul: recul, y: v.y - d.y,
                 sol: L.Monde.solidite(Math.floor(v.x / L.TT), Math.floor(v.y / L.TT)) };
    }""")
    assert r["pleine"] > auto["vitesse_max"] * 0.95, f"{r['pleine']} px/image, la voiture n'atteint pas sa vitesse"
    assert r["pleine"] <= auto["vitesse_max"] + 1e-6
    assert r["avance"] > 800, "elle n'a pas avance"
    assert -auto["vitesse_recul"] - 1e-6 <= r["recul"] < -0.3, "la marche arriere ne marche pas"
    assert abs(r["y"]) < 4, "elle a devie en ligne droite"
    assert r["sol"] == 0


def test_le_frein_a_main_fait_deriver(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function virage(freinMain) {
            const j = L.B.joueur, d = o.ligneDroite();
            j.x = d.x; j.y = d.y;
            if (j.dansVehicule) L.Vehicules.descendre(j, true);
            const v = o.char('auto', 0, 0, 0);
            v.vitesse = 3.5; v.vx = 3.5; v.vy = 0;
            L.Vehicules.monter(j, v);
            let ecartMax = 0;
            for (let i = 0; i < 25; i++) {
                L.Vehicules.majPhysique(v, { gaz: 1, frein: 0, direction: 1, freinMain: freinMain });
                const capVitesse = Math.atan2(v.vy, v.vx);
                ecartMax = Math.max(ecartMax, Math.abs(L.Vehicules.courbeBraquage ? (capVitesse - v.angle) : 0));
            }
            L.Entites.retirer(v);
            return ecartMax;
        }
        return { sans: virage(false), avec: virage(true) };
    }""")
    assert r["avec"] > r["sans"] * 1.3, f"la derive au frein a main ({r['avec']:.2f}) ne depasse pas la conduite normale ({r['sans']:.2f})"


def test_un_mur_fait_mal_mais_ne_se_traverse_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('auto', 0, 0, -Math.PI / 2);   // plein nord : le bord de la carte
        L.Vehicules.monter(j, v);
        const vie0 = v.vie;
        o.touche('KeyW'); o.frame(120); o.relacher('KeyW');
        let dedans = false;
        for (const c of L.Vehicules.cercles(v)) {
            if (L.Monde.bloque(Math.floor(c.x / L.TT), Math.floor(c.y / L.TT), L.Monde.MASQUE_VEHICULE)) dedans = true;
        }
        return { perdu: vie0 - v.vie, chocs: v.chocs, dedans: dedans, vitesse: Math.abs(v.vitesse), y: v.y };
    }""")
    assert r["perdu"] > 0, "le mur n'a pas fait de degats"
    assert r["chocs"] >= 1
    assert r["dedans"] is False, "le char est entre dans le mur"
    assert r["vitesse"] < 1.5
    assert r["y"] > 0


def test_le_trafic_roule_3000_images_sans_se_bloquer(banc, paquet):
    maximum = paquet["conduite"]["trafic"]["vehicules_max"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(43);
        o.frame(1200);
        // ⚠️ On ne suit un char que tant qu'il est LA : la bulle d'oubli retire
        // ceux qui s'eloignent du joueur, et un char retire ne bouge plus —
        // le test les prenait pour des chars bloques.
        const suivis = new Map();
        L.B.entites.forEach(function (e) { if (e.type === 'vehicule' && e.conducteur === 'trafic') suivis.set(e.id, { x: e.x, y: e.y, d: 0, images: 0 }); });
        for (let i = 0; i < 1800; i++) {
            o.frame(1);
            L.B.entites.forEach(function (e) {
                const s = suivis.get(e.id);
                if (!s) return;
                s.d += Math.hypot(e.x - s.x, e.y - s.y); s.x = e.x; s.y = e.y; s.images++;
            });
        }
        const chars = L.B.entites.filter(function (e) { return e.type === 'vehicule'; });
        let dansUnMur = 0, horsRoute = 0;
        chars.forEach(function (v) {
            const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
            if (L.Monde.solidite(tx, ty) === 1) dansUnMur++;
            if (v.conducteur === 'trafic' && !L.Monde.estRoute(tx, ty)) horsRoute++;
        });
        const presents = Array.from(suivis.values()).filter(function (s) { return s.images >= 600; });
        const distances = presents.map(function (s) { return s.d / s.images * 1800; });   // ramene a 1800 images
        const bouges = distances.filter(function (d) { return d > 300; }).length;
        return { roulent: chars.filter(function (v) { return v.conducteur === 'trafic'; }).length,
                 suivis: distances.length, bouges: bouges, dansUnMur: dansUnMur, horsRoute: horsRoute,
                 total: chars.length, epaves: chars.filter(function (v) { return v.etat === 'epave'; }).length,
                 ms: L.B.stats.ms };
    }""")
    assert r["roulent"] >= 3, "le trafic ne se peuple pas"
    assert r["roulent"] <= maximum
    assert r["dansUnMur"] == 0, "un char est dans un mur"
    assert r["horsRoute"] <= 1, f"{r['horsRoute']} chars du trafic hors de la route"
    assert r["epaves"] == 0, "le trafic s'entretue tout seul"
    assert r["suivis"] >= 3 and r["bouges"] >= r["suivis"] * 0.6, \
        f"{r['bouges']}/{r['suivis']} chars ont roule : le trafic se bloque"


def test_renverser_un_pieton_est_un_crime(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(44);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const victime = o.poser('passant', 90, 0);
        const enfant = o.poser('enfant', 90, 30);
        const crimes = L.B.partie.stats.crimes;
        v.vitesse = 3.5; v.vx = 3.5; v.vy = 0;
        o.touche('KeyW'); o.frame(60); o.relacher('KeyW');
        return { vie: victime.vie, max: victime.vieMax, etat: victime.etat, crimes: L.B.partie.stats.crimes - crimes,
                 enfant: enfant.vie === enfant.vieMax && enfant.vivant };
    }""")
    assert r["vie"] < r["max"], "le pieton n'a pas ete renverse"
    assert r["crimes"] >= 1, "renverser quelqu'un n'est pas compte comme un crime"
    assert r["enfant"] is True, "un enfant a ete touche par un char"


def test_un_char_explose_et_brule_ce_qui_l_entoure(banc, paquet):
    ph = paquet["conduite"]["physique"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(45);
        const v = o.char('auto', 60, 0, 0);
        const voisin = o.poser('ouvrier', 60, 18);
        voisin.courage = 0;
        const loin = o.poser('passant', 60, 300);
        L.Entites.indexer();
        L.Vehicules.endommager(v, 9999, L.B.joueur);
        return { etat: v.etat, vie: v.vie, voisin: voisin.vie, voisinMax: voisin.vieMax,
                 loin: loin.vie === loin.vieMax, decals: L.B.decals.length,
                 particules: L.B.particules.length, crimes: L.B.partie.stats.crimes };
    }""")
    assert r["etat"] == "epave" and r["vie"] == 0
    assert r["voisin"] < r["voisinMax"], "l'explosion n'a pas touche le voisin"
    assert ph["explosion_rayon_px"] < 300
    assert r["loin"] is True, "l'explosion a porte a 300 px"
    assert r["particules"] > 20 and r["decals"] >= 1
    assert r["crimes"] >= 1, "faire exploser un char n'est pas un crime ?"


def test_le_carjacking_se_voit_toujours(banc, paquet):
    gravite = paquet["recherche"]["delits"]["carjacking"]["etoiles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(46);
        const j = L.B.joueur;
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        const v = o.char('auto', 20, 0, 0);
        v.conducteur = 'trafic'; v.etat = 'roule';
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
        const temoins = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.etat === 'temoin'; }).length;
        return { conducteur: v.conducteur === j, temoins: temoins,
                 chaleur: L.B.recherche.chaleur + L.B.recherche.etoiles * 100,
                 gravite: L.B.defs.recherche.chaleur_par_gravite };
    }""")
    assert r["conducteur"] is True
    assert r["temoins"] == 1, "la victime du carjacking doit sortir et temoigner"
    assert r["chaleur"] == gravite * r["gravite"], "le carjacking n'a pas chauffe la police"


def test_les_feux_alternent_et_les_t_n_en_ont_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const inters = L.Monde.carte.intersections;
        const croix = inters.find(function (i) { return i.bras.length === 4; });
        const te = inters.find(function (i) { return i.bras.length === 3; });
        const cycle = 2 * (L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images);
        const releves = [];
        for (let t = 0; t < cycle; t += 30) {
            L.B.t = t - croix.decalage;
            releves.push([L.Monde.feuVert(croix, '^'), L.Monde.feuVert(croix, '>')]);
        }
        const deuxVerts = releves.filter(function (r) { return r[0] && r[1]; }).length;
        const nsVert = releves.filter(function (r) { return r[0]; }).length;
        const eoVert = releves.filter(function (r) { return r[1]; }).length;
        return { deuxVerts: deuxVerts, nsVert: nsVert, eoVert: eoVert, total: releves.length,
                 teVert: L.Monde.feuVert(te, '^') && L.Monde.feuVert(te, '>') };
    }""")
    assert r["deuxVerts"] == 0, "les deux sens ont ete verts en meme temps"
    assert r["nsVert"] > 0 and r["eoVert"] > 0
    assert abs(r["nsVert"] - r["eoVert"]) <= 1, "un sens est favorise"
    assert r["teVert"] is True, "un T n'a pas de feu : on y passe a vue"


def test_le_taxi_paie_la_course_selon_la_douceur(banc, paquet):
    boulot = paquet["economie"]["boulots"]["taxi"]
    civil = next(p for p in paquet["personnages"] if p["slug"] == "civil")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(47);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('taxi', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const argent0 = L.B.partie.argent;
        o.tape('Space', 2);                              // klaxon : un client
        const t = L.Missions.taxi;
        const etape1 = t.etape, client = t.client;
        const hele = client && client.bulle ? client.bulle.texte : null;
        if (client) { v.x = client.x + 10; v.y = client.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        const etape2 = t.etape, dest = t.destination;
        if (dest) { v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        return { etape1: etape1, etape2: etape2, etape3: t.etape, hele: hele,
                 gain: L.B.partie.argent - argent0, courses: t.courses };
    }""")
    assert r["etape1"] == "attente" and r["etape2"] == "course" and r["etape3"] is None
    assert r["hele"] == civil["heler"], \
        "un client qui attend un taxi sans rien dire est un passant de plus (bulle du « civil »)"
    assert r["courses"] == 1
    assert r["gain"] >= boulot["base"] + boulot["prime"], \
        "une course sans un choc doit donner le pourboire plein"


def test_l_hopital_ramasse_le_joueur_et_le_facture(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 400;
        L.Entites.blesser(j, 9999, null, {});
        const pendant = { vivant: j.vivant, fondu: !!L.B.fondu };
        o.frame(90);
        const hopital = L.Monde.carte.points.find(function (p) { return p.slug === 'hopital'; });
        return { pendant: pendant, vie: j.vie, max: j.vieMax, argent: L.B.partie.argent,
                 loin: Math.hypot(j.x - hopital.x * L.TT, j.y - hopital.y * L.TT), etat: L.B.etat };
    }""")
    assert r["pendant"]["vivant"] is True and r["pendant"]["fondu"] is True
    assert r["vie"] == r["max"], "le joueur ne s'est pas reveille en pleine forme"
    assert r["argent"] < 400, "l'hopital n'a pas facture"
    assert r["loin"] < 48, "le joueur ne s'est pas reveille a l'hopital"
    assert r["etat"] == "jeu"


def test_la_radio_suit_le_char(banc, paquet):
    stations = [r["slug"] for r in paquet["audio"]["radios"]]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const v = o.char('auto', 24, 0, 0);
        L.Vehicules.monter(j, v);
        const auVolant = L.Son.Radio.demandee;
        o.tape('Tab', 2);
        const suivante = L.Son.Radio.demandee;
        const parcours = [suivante];
        for (let i = 0; i < 4; i++) { L.Son.Radio.suivante(); parcours.push(L.Son.Radio.demandee); }
        L.Vehicules.descendre(j, true);
        return { auVolant: auVolant, suivante: suivante, parcours: parcours, apres: L.Son.Radio.demandee,
                 defaut: v.def.radio };
    }""")
    assert r["auVolant"] == r["defaut"] == "la_brume", "l'auto doit allumer La Brume"
    assert r["suivante"] != r["auVolant"], "le bouton RADIO ne change pas de station"
    assert None in r["parcours"], "le cycle doit passer par le silence"
    assert set(s for s in r["parcours"] if s) <= set(stations)
    assert r["apres"] is None, "la radio joue encore une fois descendu"


# --- La rue dans la vraie vie : trottoirs, passages, feux, stops, velos ----


def test_les_pietons_restent_sur_les_trottoirs(banc):
    """⚠️ La regle de la ville : on ne pose pas le pied sur la chaussee. Le
    passage pieton est la seule exception — et un pieton pousse sur la rue
    par un char regagne le trottoir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(51);
        let surLaChaussee = 0, surUnPassage = 0, releves = 0;
        for (let i = 0; i < 2400; i++) {
            o.frame(1);
            if (i < 300 || i % 30) continue;
            L.B.entites.forEach(function (e) {
                if (e.type !== 'pieton' || !e.vivant || e.recul > 0) return;
                const tx = Math.floor(e.x / L.TT), ty = Math.floor(e.y / L.TT);
                releves++;
                if (L.Monde.estChaussee(tx, ty)) surLaChaussee++;
                if (L.Monde.estPassage(tx, ty)) surUnPassage++;
            });
        }
        return { releves: releves, chaussee: surLaChaussee, passage: surUnPassage };
    }""")
    assert r["releves"] > 200
    assert r["chaussee"] <= r["releves"] * 0.03, \
        f"{r['chaussee']} releves de pietons sur la chaussee (sur {r['releves']})"
    assert r["passage"] > 0, "personne ne traverse jamais"


def test_un_pieton_attend_au_feu_avant_de_traverser(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        const inter = c.intersections.find(function (i) { return i.feux; });
        // Le passage a l'ouest du croisement, sur la rue est-ouest : tuile '='.
        const tx = inter.x - 1, ty = inter.y;
        const est = L.Monde.glyphe(tx, ty);
        L.B.t = -inter.decalage;                      // phase 0 : nord-sud roule, est-ouest est au rouge
        const rougeEO = !L.Monde.feuVert(inter, '>');
        const surAuRouge = L.Entites.traverseeSure(tx, ty, [0, 1]);
        L.B.t += Math.floor((L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images));
        const vertEO = L.Monde.feuVert(inter, '>');
        const surAuVert = L.Entites.traverseeSure(tx, ty, [0, 1]);
        return { glyphe: est, rougeEO: rougeEO, surAuRouge: surAuRouge, vertEO: vertEO, surAuVert: surAuVert };
    }""")
    assert r["glyphe"] == "=", "la tuile choisie n'est pas un passage de la rue est-ouest"
    assert r["rougeEO"] is True and r["surAuRouge"] is True, "au rouge des chars, le pieton doit pouvoir traverser"
    assert r["vertEO"] is True and r["surAuVert"] is False, "au vert des chars, le pieton doit attendre"


def test_le_trafic_reste_dans_sa_voie(banc):
    """Sur des rails : un char du trafic ne coupe plus un coin, jamais."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(52);
        let horsRoute = 0, releves = 0, tournes = 0;
        const caps = new Map();
        for (let i = 0; i < 3000; i++) {
            o.frame(1);
            if (i < 200 || i % 20) continue;
            L.B.entites.forEach(function (v) {
                if (v.type !== 'vehicule' || v.conducteur !== 'trafic' || v.def.classe === 'velo' && false) return;
                releves++;
                const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
                if (!L.Monde.estRoute(tx, ty)) horsRoute++;
                const avant = caps.get(v.id);
                if (avant !== undefined && Math.abs(L.ecartAngle ? 0 : 0) === 0 && Math.abs(v.sens !== avant ? 1 : 0)) tournes++;
                caps.set(v.id, v.sens);
            });
        }
        return { releves: releves, horsRoute: horsRoute, tournes: tournes,
                 velos: L.B.entites.filter(function (v) { return v.type === 'vehicule' && v.def.classe === 'velo'; }).length };
    }""")
    assert r["releves"] > 300
    # 1 % : un char pousse d'une demi-tuile par un voisin a un coin, le temps
    # de regagner sa voie. Au-dela, c'est le trafic qui coupe les coins.
    assert r["horsRoute"] <= r["releves"] * 0.01, f"{r['horsRoute']} releves de trafic hors de la route"
    assert r["tournes"] > 3, "le trafic ne tourne jamais"


def test_un_char_se_deporte_pour_contourner_un_pieton(banc):
    """Sur un boulevard, un pieton plante au milieu de la voie ne bloque plus :
    le char se tasse dans la voie d'a cote — par la gauche — et repart."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(61);
        const T = L.TT;
        const b = o.boulevard(true);
        if (!b) return { trouve: false };
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const y0 = b.y;
        const v = L.Vehicules.creer('auto', b.x, y0, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        v.vitesse = 1.2;
        // Un passant fige au milieu de la chaussee, cinq tuiles devant.
        const p = L.Entites.creerPieton(b.x + 5 * T, y0, null);
        p.etat = 'fige';
        let yMin = y0, depasse = false, renverse = false, voie = null;
        for (let i = 0; i < 400; i++) {
            L.Entites.indexer();
            L.Vehicules.majConducteur(v);
            v.x += v.vx; v.y += v.vy;
            yMin = Math.min(yMin, v.y);
            if (!p.vivant) renverse = true;
            if (depasse) continue;
            if (v.x > p.x + 24) {
                depasse = true;
                voie = L.Monde.fleche(Math.floor(v.x / T), Math.floor(v.y / T));   // ou roule-t-il en doublant ?
            }
        }
        return { trouve: true, depasse: depasse, deports: v.deports || 0, renverse: renverse,
                 gauche: Math.round(y0 - yMin), voie: voie };
    }""")
    assert r["trouve"], "aucun boulevard a deux voies dans le meme sens sur la carte"
    assert r["deports"] >= 1, "le char n'a jamais essaye de se tasser"
    assert r["gauche"] >= 10, f"il s'est tasse de {r['gauche']} px : ce n'est pas la voie de gauche"
    assert r["depasse"], "le char n'a jamais depasse le pieton"
    assert r["renverse"] is False, "⚠️ on contourne le pieton, on ne le fauche pas"
    assert r["voie"] == ">", "en doublant, le char n'etait pas dans une voie de son sens"


def test_sur_une_rue_a_deux_voies_le_char_attend(banc):
    """⚠️ Le pendant du test precedent : sans voie parallele dans son sens, se
    deporter serait rouler a contresens. Le char attend, comme avant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(62);
        const T = L.TT;
        const b = o.boulevard(false);
        if (!b) return { trouve: false };
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const y0 = b.y;
        const v = L.Vehicules.creer('auto', b.x, y0, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        v.vitesse = 1.2;
        const p = L.Entites.creerPieton(b.x + 5 * T, y0, null);
        p.etat = 'fige';
        let ecart = 0;
        for (let i = 0; i < 180; i++) {
            L.Entites.indexer();
            L.Vehicules.majConducteur(v);
            v.x += v.vx; v.y += v.vy;
            ecart = Math.max(ecart, Math.abs(v.y - y0));
        }
        return { trouve: true, deports: v.deports || 0, ecart: Math.round(ecart),
                 arrete: Math.abs(v.vx) + Math.abs(v.vy) < 0.05, avant: v.x < p.x };
    }""")
    assert r["trouve"], "aucune rue a une seule voie par sens sur la carte"
    assert r["deports"] == 0, "le char s'est deporte a contresens"
    assert r["ecart"] <= 4, f"il a quitte sa voie de {r['ecart']} px"
    assert r["arrete"] and r["avant"], "le char n'a pas attendu derriere le pieton"


def test_on_ne_se_deporte_pas_dans_une_voie_occupee(banc):
    """La voie d'a cote n'est libre que si personne n'y roule — devant COMME
    derriere. Un char qui arrive vite par la gauche a la priorite ; celui qui
    est coince reste derriere son pieton plutot que de lui couper la route."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(63);
        const T = L.TT;
        const b = o.boulevard(true);
        if (!b) return { trouve: false };
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const y0 = b.y;
        const v = L.Vehicules.creer('auto', b.x, y0, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        v.vitesse = 1.2;
        const p = L.Entites.creerPieton(b.x + 5 * T, y0, null);
        p.etat = 'fige';
        // Un char arrete dans la voie de gauche, juste a cote du pieton.
        const mur = L.Vehicules.creer('auto', b.x + 5 * T, y0 - T, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        mur.vitesse = 0;
        let ecart = 0;
        for (let i = 0; i < 180; i++) {
            L.Entites.indexer();
            L.Vehicules.majConducteur(v);
            v.x += v.vx; v.y += v.vy;
            ecart = Math.max(ecart, Math.abs(v.y - y0));
        }
        return { trouve: true, deports: v.deports || 0, ecart: Math.round(ecart), avant: v.x < p.x };
    }""")
    assert r["trouve"], "aucun boulevard a deux voies dans le meme sens sur la carte"
    assert r["deports"] == 0, "le char s'est tasse dans une voie occupee"
    assert r["ecart"] <= 4, f"il a quitte sa voie de {r['ecart']} px"
    assert r["avant"], "le char a traverse le pieton au lieu d'attendre"


def test_les_feux_et_les_stops_sont_poses(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        const feux = L.B.entites.filter(function (e) { return e.type === 'feu'; });
        const stops = L.B.entites.filter(function (e) { return e.type === 'stop'; });
        const croix = c.intersections.filter(function (i) { return i.feux; }).length;
        const tes = c.intersections.filter(function (i) { return i.stop; }).length;
        const bienPlaces = feux.concat(stops).filter(function (e) {
            return L.Monde.solidite(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT)) === 0 && !L.Monde.estRoute(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT));
        }).length;
        // Un T dont le bras ouest manque : la tige est a l'est, on y arrive en roulant vers l'ouest.
        const sansOuest = c.intersections.find(function (i) { return i.bras.length === 3 && i.bras.indexOf('O') < 0; });
        return { feux: feux.length, croix: croix, stops: stops.length, tes: tes,
                 bienPlaces: bienPlaces, stopSansOuest: sansOuest ? sansOuest.stop : null };
    }""")
    assert r["feux"] == r["croix"] * 2 > 0
    assert r["stops"] == r["tes"] > 0
    assert r["bienPlaces"] == r["feux"] + r["stops"], "un feu ou un stop est sur la route ou dans un mur"
    assert r["stopSansOuest"] == "<", "le STOP est pour ceux qui arrivent par la tige"


def test_un_char_s_arrete_au_stop_puis_repart(banc, paquet):
    arret = paquet["conduite"]["trafic"]["arret_images"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(53);
        const c = L.Monde.carte;
        // Un T dont la tige arrive par l'est (sens '<') : on cherche sa ligne d'arret.
        const inter = c.intersections.find(function (i) { return i.stop === '<'; });
        let sx = -1, sy = -1;
        for (const cle in c.arrets) {
            const xy = cle.split(',').map(Number);
            if (c.arrets[cle] !== '<') continue;
            if (L.Monde.intersectionA(xy[0] - 1, xy[1]) === inter) { sx = xy[0]; sy = xy[1]; break; }
        }
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const v = L.Vehicules.creer('auto', sx * L.TT + 8 + 40, sy * L.TT + 8, Math.PI, { conducteur: 'trafic', etat: 'roule', sens: '<' });
        v.vitesse = 1.5;
        let immobile = 0, arrive = false, reparti = false;
        for (let i = 0; i < 600; i++) {
            L.Entites.indexer(); L.Vehicules.majConducteur(v); v.x += v.vx; v.y += v.vy;
            const tx = Math.floor(v.x / L.TT);
            if (tx === sx && Math.abs(v.vx) + Math.abs(v.vy) < 0.01) { immobile++; arrive = true; }
            if (arrive && tx < sx) { reparti = true; break; }
        }
        return { trouve: sx >= 0, arrive: arrive, immobile: immobile, reparti: reparti };
    }""")
    assert r["trouve"], "aucune ligne d'arret de T trouvee"
    assert r["arrive"] and r["immobile"] >= arret - 2, f"le char ne s'est arrete que {r['immobile']} images au STOP"
    assert r["reparti"], "le char n'est jamais reparti du STOP"


def test_on_prend_le_velo_du_cycliste(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(54);
        const j = L.B.joueur;
        const velo = o.char('velo', 16, 0, 0);
        velo.conducteur = 'trafic'; velo.etat = 'roule';
        L.Entites.indexer();
        const crimes = L.B.partie.stats.crimes;
        L.Vehicules.monter(j, velo);
        const cycliste = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.etat === 'temoin'; }).length;
        o.touche('KeyW'); o.frame(120); o.relacher('KeyW');
        return { dedans: j.dansVehicule === velo, cycliste: cycliste, crimes: L.B.partie.stats.crimes - crimes,
                 vitesse: velo.vitesse, max: velo.def.vitesse_max, moteur: L.Son.boucleActive('moteur'),
                 radio: L.Son.Radio.demandee };
    }""")
    assert r["dedans"] is True
    assert r["cycliste"] == 1, "le cycliste doit tomber et temoigner"
    assert r["crimes"] >= 1
    assert r["vitesse"] > r["max"] * 0.8, "le velo n'avance pas"
    assert r["moteur"] is False and r["radio"] is None, "un velo n'a ni moteur ni radio"


def test_l_ambiance_joue_a_pied_et_cede_a_la_radio(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const aPied = L.Son.Ambiance.demandee;
        const j = L.B.joueur;
        const v = o.char('auto', 24, 0, 0);
        L.Vehicules.monter(j, v);
        const auVolant = { ambiance: L.Son.Ambiance.demandee, radio: L.Son.Radio.demandee };
        L.Vehicules.descendre(j, true);
        return { aPied: aPied, auVolant: auVolant, descendu: L.Son.Ambiance.demandee };
    }""")
    assert r["aPied"] == "ville", "la ville doit avoir sa musique a pied"
    assert r["auVolant"]["ambiance"] is None and r["auVolant"]["radio"] == "la_brume", \
        "au volant, la radio remplace l'ambiance"
    assert r["descendu"] == "ville", "descendu, l'ambiance revient"


def test_la_rumeur_suit_la_foule_et_les_passants_parlent(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(61);
        const j = L.B.joueur;
        // Sans audio sous Node : on verifie la mecanique, pas le son.
        const avant = L.Son.Voix.dernierT;
        const p = o.poser('passante', 12, 0);
        p.etat = 'flane';
        o.frame(2);
        const parle = p.aParle === true;
        const rumeur = typeof L.Son.Rumeur.maj === 'function';
        return { parle: parle, rumeur: rumeur, dernierT: L.Son.Voix.dernierT, avant: avant,
                 passage: typeof L.Son.jouerA === 'function' };
    }""")
    assert r["parle"] is True, "un passant qui nous frole doit tenter de parler"
    assert r["rumeur"] and r["passage"]


def test_deux_chars_qui_tournent_a_gauche_ne_se_bloquent_pas(banc):
    """⚠️ Le blocage de Martin : deux chars entrent au vert par des bouts
    opposes, tous deux pour tourner a gauche, se retrouvent nez a nez au
    milieu de la boite — et chacun attend l'autre. Un croisement ne doit
    accueillir un char que s'il peut le laisser ressortir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(72);
        const c = L.Monde.carte;
        // Un croisement a feux a quatre voies (rue est-ouest large).
        const inter = c.intersections.find(function (i) { return i.feux && i.l === 4 && i.h === 4; });
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
        // ⚠️ Le joueur regarde de pres : hors de sa bulle, un char est oublie
        // et le test croirait a un blocage.
        const j = L.B.joueur;
        j.x = (inter.x - 1) * L.TT + 8; j.y = (inter.y - 1) * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        // Phase : est-ouest au vert.
        L.B.t = -inter.decalage + L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images + 5;
        const T = L.TT;
        // A arrive de l'ouest sur la voie interieure (rangee y+2), B de l'est sur la voie interieure (rangee y+1).
        const a = L.Vehicules.creer('auto', (inter.x - 6) * T + 8, (inter.y + 2) * T + 8, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        const b = L.Vehicules.creer('auto', (inter.x + inter.l + 5) * T + 8, (inter.y + 1) * T + 8, Math.PI, { conducteur: 'trafic', etat: 'roule', sens: '<' });
        a.vitesse = 1.5; b.vitesse = 1.5;
        a.sortie = ['gauche', 'droit', 'droite']; b.sortie = ['gauche', 'droit', 'droite'];
        const boite = function (v) { return v.x >= inter.x * T && v.x < (inter.x + inter.l) * T && v.y >= inter.y * T && v.y < (inter.y + inter.h) * T; };
        let dansLaBoiteEnsemble = 0, sortis = 0;
        for (let i = 0; i < 2400; i++) {
            o.frame(1);
            if (boite(a) && boite(b)) dansLaBoiteEnsemble++;
        }
        const aParti = Math.hypot(a.x - (inter.x - 6) * T, a.y - (inter.y + 2) * T) > 8 * T && !boite(a);
        const bParti = Math.hypot(b.x - (inter.x + inter.l + 5) * T, b.y - (inter.y + 1) * T) > 8 * T && !boite(b);
        return { ensemble: dansLaBoiteEnsemble, aParti: aParti, bParti: bParti, aSens: a.sens, bSens: b.sens,
                 aSol: L.Monde.estRoute(Math.floor(a.x / T), Math.floor(a.y / T)),
                 bSol: L.Monde.estRoute(Math.floor(b.x / T), Math.floor(b.y / T)) };
    }""")
    assert r["ensemble"] == 0, f"les deux chars ont partage la boite pendant {r['ensemble']} images"
    assert r["aParti"] and r["bParti"], f"un char est reste coince : {r}"
    assert r["aSol"] and r["bSol"], "un char a fini hors de la route"


def test_les_passages_ont_une_tuile_pleine_et_une_en_bout(banc):
    """Le passage fait deux tuiles ; les bandes n'en couvrent que les deux
    tiers, collees au croisement. Chaque passage a donc exactement une tuile
    interieure (pleine) et une exterieure (en bout), jamais deux pleines."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        const compte = { '=': [0, 0, 0], ':': [0, 0, 0] };
        for (let y = 0; y < c.h; y++) for (let x = 0; x < c.w; x++) {
            const g = c.sol[y][x];
            if (g === '=' || g === ':') compte[g][L.Monde.varianteDePassage(g, x, y)]++;
        }
        return compte;
    }""")
    for g in ("=", ":"):
        pleines, ouest, est = r[g]
        assert pleines > 0 and ouest > 0 and est > 0, r
        assert pleines == ouest + est, f"passage « {g} » : {pleines} pleines pour {ouest + est} en bout"


def test_une_case_de_stationnement_se_peint_et_se_gare(banc):
    """Une case fait deux tuiles : le FOND (ligne de nez, butoir) et l'ouverture
    sur l'allee. Le peintre ne le sait pas du generateur, il le LIT dans les
    voisines — et c'est la meme lecture qui met une auto stationnee dans ses
    lignes plutot qu'en travers du terrain."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, NEZ = { '^': [0, -1], 'v': [0, 1], '<': [-1, 0], '>': [1, 0] };
        let fonds = 0, ouvertes = 0, mauvaises = 0;
        const coins = {}, cases = [];
        for (let y = 1; y < c.h - 1; y++) for (let x = 1; x < c.w - 1; x++) {
            const g = c.sol[y][x], nez = NEZ[g];
            if (!nez) continue;
            const v = L.Monde.varianteDeCase(g, x, y);
            const fond = (v & 1) !== 0;
            if (fond !== (c.sol[y + nez[1]][x + nez[0]] !== g)) mauvaises++;
            if (fond) fonds++; else ouvertes++;
            coins[v & 3] = (coins[v & 3] || 0) + 1;
            cases.push([x, y]);
        }
        // ⚠️ Une auto ne se stationne QUE hors de l'ecran, entre 180 et 560 px
        // du joueur : on se plante donc au milieu du coin le plus fourni en
        // cases, sinon on juge un quartier ou il n'y a rien a peupler.
        let mieux = cases[0], n = 0;
        for (let i = 0; i < cases.length; i += 8) {
            const p = cases.filter(function (k) {
                return Math.abs(k[0] - cases[i][0]) < 30 && Math.abs(k[1] - cases[i][1]) < 30;
            }).length;
            if (p > n) { n = p; mieux = cases[i]; }
        }
        L.B.joueur.x = mieux[0] * L.TT; L.B.joueur.y = mieux[1] * L.TT;
        o.frame(900);
        const gares = L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.etat === 'stationne'; });
        const poses = gares.map(function (v) {
            const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
            const g = c.sol[ty][tx], nez = NEZ[g];
            return {
                case: !!nez,
                angle: !!nez && Math.abs(Math.atan2(nez[1], nez[0]) - v.angle) < 0.01,
                centree: (v.x % L.TT === 8 && v.y % L.TT === 0) || (v.y % L.TT === 8 && v.x % L.TT === 0),
            };
        });
        return { fonds: fonds, ouvertes: ouvertes, mauvaises: mauvaises, coins: coins, poses: poses };
    }""")
    assert r["mauvaises"] == 0, "une tuile de fond mal lue : le butoir se peint du mauvais bord"
    assert r["fonds"] > 0 and r["fonds"] == r["ouvertes"], \
        f"{r['fonds']} fonds pour {r['ouvertes']} ouvertures : une case n'a pas deux tuiles"
    assert set(r["coins"]) == {"0", "1", "2", "3"}, \
        f"le peintre n'a jamais vu les quatre coins d'une rangee : {r['coins']}"
    assert r["poses"], "aucune auto ne s'est stationnee en 900 images"
    for pose in r["poses"]:
        assert pose["case"], "une auto stationnee hors d'une case"
        assert pose["angle"], "une auto stationnee de travers dans sa case"
        assert pose["centree"], "une auto stationnee a cheval sur ses lignes"


# --- M5 : interieurs et economie ----------------------------------------------


def test_le_fondu_de_porte_noircit_avant_de_changer_de_scene(banc):
    """⚠️ Le defaut que Martin a nomme « la transition n'est pas juste » : la
    piece se chargeait PUIS le fondu partait de transparent. Sa premiere moitie
    noircissait donc sur la scene deja changee — on voyait la piece une image,
    l'ecran noircissait, il s'eclaircissait sur la meme piece. Ce test mesure la
    scene a CHAQUE image : aucune ne doit montrer la nouvelle avant le noir
    complet, et la porte doit s'entendre la, au noir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        const villeW = c.w;
        // La porte s'entend-elle, et QUAND ?
        const sons = [];
        const vraiSon = L.Son.SFX.porte;
        L.Son.SFX.porte = function () { sons.push({ noir: L.B.transition ? L.B.transition.t : -1, dedans: !!L.B.interieur }); return vraiSon.apply(null, arguments); };
        L.Jeu.entrer(porte);
        const images = [];
        for (let i = 0; i < 120 && L.B.transition; i++) {
            o.frame(1);
            const tr = L.B.transition;
            // L'alpha du noir, comme le HUD le calcule : 0 -> 1, puis 1 -> 0.
            const alpha = tr ? (tr.t <= tr.ferme ? tr.t / tr.ferme : 1 - (tr.t - tr.ferme) / tr.ouvre) : 0;
            images.push({ alpha: Math.round(alpha * 1000) / 1000, w: L.Monde.carte.w, dedans: !!L.B.interieur });
        }
        const entree = images.length;
        // Et au retour : plus vif qu'a l'aller.
        L.Jeu.sortir();
        const sortie = o.fondu();
        return { villeW: villeW, images: images, entree: entree, sortie: sortie, sons: sons,
                 dedans: L.B.interieur, w: L.Monde.carte.w };
    }""")
    change = [i for i, im in enumerate(r["images"]) if im["dedans"]]
    assert change, "on n'est jamais entre"
    premiere = change[0]
    assert r["images"][premiere]["alpha"] == 1.0, (
        "la nouvelle scene se montre a %s de noir : le fondu clignote"
        % r["images"][premiere]["alpha"]
    )
    for im in r["images"][:premiere]:
        assert im["w"] == r["villeW"] and not im["dedans"], "la piece est chargee avant le noir"
        assert im["alpha"] < 1.0
    assert r["images"][-1]["alpha"] < 0.2, "le fondu ne finit pas en clair"
    assert r["sons"][0] == {"noir": premiere + 1, "dedans": True}, (
        "la porte doit s'entendre AU NOIR, a l'image du changement : %s" % r["sons"]
    )
    assert len(r["sons"]) == 2 and r["sons"][1]["dedans"] is False, (
        "la porte de sortie s'entend aussi au noir, une fois la rue revenue : %s" % r["sons"]
    )
    assert r["sortie"] < r["entree"], "sortir doit etre plus vif qu'entrer"
    assert 30 <= r["entree"] <= 90 and r["sortie"] >= 20, (
        "un fondu de porte se sent : ni un clignotement, ni une attente (%s, %s)"
        % (r["entree"], r["sortie"])
    )


def test_le_jeu_est_fige_pendant_un_fondu_de_porte(banc):
    """⚠️ La simulation continuait pendant le fondu : on pouvait sortir d'une
    piece et se faire renverser par un char qu'on n'a pas vu venir, sur un ecran
    noir ou l'on ne controle rien. Un menu fige deja tout ; une porte pareil."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.frame(2);
        // Un passant qui marche, un char qui roule : rien de tout ca ne doit
        // avancer d'un pixel pendant le noir.
        const passant = o.poser('flaneur', 24, 0);
        passant.etat = 'flane';
        const char = o.char('auto', -30, 0, 0);
        char.etat = 'roule'; char.vitesse = 3;
        j.vie = 60;
        const avant = { t: L.B.t, vie: j.vie, px: passant.x, py: passant.y, cx: char.x, heure: L.B.partie.heure };
        L.Jeu.entrer(porte);
        const images = o.fondu();
        const apres = { t: L.B.t, vie: j.vie, px: passant.x, py: passant.y, cx: char.x, heure: L.B.partie.heure };
        // Et une fois dedans, le jeu repart : le temps passe de nouveau.
        o.frame(5);
        return { avant: avant, apres: apres, images: images, repart: L.B.t - apres.t, dedans: !!L.B.interieur };
    }""")
    assert r["dedans"] is True and r["images"] > 20
    assert r["apres"]["t"] == r["avant"]["t"], "le temps de jeu a passe pendant le fondu"
    assert r["apres"]["heure"] == r["avant"]["heure"], "l'heure a avance pendant le fondu"
    assert r["apres"]["vie"] == r["avant"]["vie"], "le joueur a pris des coups pendant le fondu"
    assert r["apres"]["px"] == r["avant"]["px"] and r["apres"]["py"] == r["avant"]["py"], "un passant a marche pendant le fondu"
    assert r["apres"]["cx"] == r["avant"]["cx"], "un char a roule pendant le fondu"
    assert r["repart"] == 5, "le jeu n'est pas reparti apres le fondu"


def test_sortir_pendant_le_fondu_d_entree_ramene_devant_la_porte(banc):
    """⚠️ Le cas qui casse tout : ressortir alors que le fondu d'entree joue
    encore. La scene ne change qu'au noir — celui qui sort avant ne trouverait
    aucun interieur, la sortie serait refusee, et le joueur se reveillerait
    dedans sans l'avoir demande."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        const x0 = porte.x * L.TT + 8, y0 = (porte.y + 1) * L.TT + 10;
        j.x = x0; j.y = y0;
        // Aller-retour normal, d'abord : on revient au pixel.
        o.entrer(porte);
        o.sortir();
        const normal = { x: j.x, y: j.y, dedans: L.B.interieur };
        // Puis on ressort AVANT le noir : trois images de fondu, et on repart.
        j.x = x0; j.y = y0;
        L.Jeu.entrer(porte);
        o.frame(3);
        const avantLeNoir = { dedans: !!L.B.interieur, fondu: !!L.B.transition };
        const sorti = L.Jeu.sortir();
        o.fondu();
        // L'elan qui reste au pas de la porte, avant que le jeu reprenne la main.
        const elan = { garde: Math.abs(j.vy) > 0, vers: j.vy > 0, face: j.face };
        // La camera ne saute pas : elle est deja posee quand le jeu repart.
        const cam = { x: L.B.cam.x, y: L.B.cam.y };
        o.frame(1);
        const bouge = Math.hypot(L.B.cam.x - cam.x, L.B.cam.y - cam.y);
        return { normal: normal, avantLeNoir: avantLeNoir, sorti: sorti, dedans: L.B.interieur,
                 x: j.x, y: j.y, x0: x0, y0: y0, bouge: bouge, elan: elan };
    }""")
    assert r["normal"]["dedans"] is None and (r["normal"]["x"], r["normal"]["y"]) == (r["x0"], r["y0"]), (
        "un aller-retour par la porte doit ramener a la tuile EXACTE"
    )
    assert r["avantLeNoir"] == {"dedans": False, "fondu": True}
    assert r["sorti"] is True, "sortir pendant le fondu d'entree a ete refuse"
    assert r["dedans"] is None, "on est reste dedans"
    assert (r["x"], r["y"]) == (r["x0"], r["y0"]), "on ne revient pas devant la porte"
    assert r["bouge"] < 2, "la camera saute a la premiere image jouable : %s px" % r["bouge"]
    assert r["elan"] == {"garde": True, "vers": True, "face": "bas"}, (
        "on sort d'une porte avec un reste d'elan vers la rue, pas d'un arret complet : %s" % r["elan"]
    )


def test_on_entre_dans_la_planque_et_on_en_ressort(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // Ce qui ne bouge pas : ni les pietons (oublies quand on s'eloigne), ni les
        // chars, ni les armes de fortune (semees au fil des images).
        const fixes = function () { return L.B.entites.filter(function (e) { return ['pieton', 'vehicule', 'ramassage', 'projectile'].indexOf(e.type) < 0; }).length; };
        const dehors = { entites: fixes(), w: c.w };
        o.tape('KeyE', 3);
        // La porte passe par un fondu : la piece se charge AU NOIR, pas au clic.
        const pendant = { interieur: L.B.interieur, t: L.B.t, fondu: !!L.B.transition };
        o.fondu();
        const dedans = { interieur: L.B.interieur ? L.B.interieur.slug : null, w: L.Monde.carte.w, entites: L.B.entites.length,
                         nuit: L.Monde.ambiance().alpha, cam: L.B.cam.x < 0,
                         sol: L.Monde.solidite(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT)),
                         invite: (function () { j.x = L.B.interieur.sortie.x * L.TT + 8; j.y = (L.B.interieur.sortie.y - 1) * L.TT + 8; L.Missions.majInvite(j); return L.B.invite; })() };
        o.tape('KeyE', 3);
        o.fondu();
        return { dehors: dehors, pendant: pendant, dedans: dedans, apres: { interieur: L.B.interieur, w: L.Monde.carte.w, entites: fixes(),
                 pres: Math.hypot(j.x - porte.x * L.TT - 8, j.y - (porte.y + 1) * L.TT - 10) } };
    }""")
    assert r["pendant"]["fondu"] is True, "passer une porte doit lancer un fondu"
    assert r["pendant"]["interieur"] is None, "la piece est chargee AVANT le noir : le fondu clignote"
    assert r["dedans"]["interieur"] == "planque" and r["dedans"]["w"] < r["dehors"]["w"]
    assert r["dedans"]["entites"] == 1, "la ville est entree avec nous"
    assert r["dedans"]["nuit"] == 0 and r["dedans"]["cam"] is True, "une piece se centre et n'a pas de nuit"
    assert r["dedans"]["sol"] == 0 and r["dedans"]["invite"] == "SORTIR"
    assert r["apres"]["interieur"] is None and r["apres"]["w"] == r["dehors"]["w"]
    assert r["apres"]["entites"] == r["dehors"]["entites"], "la ville n'est pas revenue telle quelle"
    assert r["apres"]["pres"] < 20, "on doit ressortir devant la porte"


def test_le_menu_fige_le_jeu_et_se_navigue(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const t0 = L.B.t;
        let choisi = null;
        L.Hud.ouvrirMenu({ titre: 'ESSAI', items: [
            { libelle: 'UN', faire: function () { choisi = 'un'; return true; } },
            { libelle: 'DEUX', faire: function () { choisi = 'deux'; return true; } },
            { libelle: 'TROIS', actif: false, faire: function () { choisi = 'trois'; return true; } },
        ] });
        o.frame(30);
        const fige = L.B.t === t0;
        o.tape('KeyS', 2);
        const curseur = L.B.menu.curseur;
        o.tape('KeyE', 2);
        const ferme = L.B.menu === null;
        L.Hud.ouvrirMenu({ titre: 'ESSAI', items: [{ libelle: 'X', faire: function () { return true; } }] });
        o.tape('Space', 2);
        return { fige: fige, curseur: curseur, choisi: choisi, ferme: ferme, retour: L.B.menu === null,
                 etiquette: o.elements.tactile.querySelectorAll('[data-a]')[1].textContent };
    }""")
    assert r["fige"] is True, "le temps passe pendant un menu"
    assert r["curseur"] == 1 and r["choisi"] == "deux" and r["ferme"] is True
    assert r["retour"] is True, "FRAPPE doit fermer un menu"


def test_la_planque_dort_sauve_et_garde_le_coffre(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        L.B.partie.argent = 250; j.vie = 30;
        const jour = L.B.partie.jour;
        // Le coffre.
        const coffre = L.B.interieur.points.find(function (p) { return p.type === 'coffre'; });
        j.x = coffre.x * L.TT + 8; j.y = coffre.y * L.TT + 8 + 12;
        L.Missions.utiliserPoint(j);
        const menuCoffre = L.B.menu.titre;
        L.B.menu.items[0].faire();          // deposer 100
        L.Hud.fermerMenu();
        // Le lit.
        const lit = L.B.interieur.points.find(function (p) { return p.type === 'lit'; });
        j.x = lit.x * L.TT + 8; j.y = lit.y * L.TT + 8 + 12;
        L.Missions.utiliserPoint(j);
        L.B.menu.items[0].faire();          // dormir
        L.Hud.fermerMenu();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        return { menuCoffre: menuCoffre, coffre: L.B.partie.planque.coffre, poches: L.B.partie.argent,
                 jour: L.B.partie.jour - jour, heure: L.B.partie.heure, vie: j.vie,
                 sauve: { coffre: brut.planque.coffre, jour: brut.jour, x: brut.x }, fondu: !!L.B.fondu,
                 dehorsX: porte.x * L.TT + 8 };
    }""")
    assert r["menuCoffre"] == "LE COFFRE"
    assert r["coffre"] == 100 and r["poches"] == 150
    assert r["jour"] == 1 and 0.25 < r["heure"] < 0.35, "on se reveille le lendemain matin"
    assert r["vie"] == 100 and r["fondu"] is True
    assert r["sauve"]["coffre"] == 100 and r["sauve"]["jour"] == r["jour"] + 1
    assert abs(r["sauve"]["x"] - r["dehorsX"]) < 4, "la sauvegarde doit retenir la position DEHORS, devant la porte"


def test_le_garage_rachete_repare_et_repeint(banc, paquet):
    eco = paquet["economie"]
    auto = next(v for v in paquet["vehicules"] if v["slug"] == "auto")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'garage'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        const v = o.char('auto', 20, 8, 0);
        v.vie = 50; v.vole = true;
        o.entrer(porte);
        L.B.partie.argent = 1000;
        const point = L.B.interieur.points.find(function (p) { return p.type === 'reparer'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        L.Missions.utiliserPoint(j);
        const menu = L.B.menu;
        const libelles = menu.items.map(function (i) { return i.libelle; });
        const vente = L.Missions.prixDeVente(v);
        const item = function (debut) { return (L.B.menu.items.find(function (i) { return i.libelle.indexOf(debut) === 0; }) || { faire: function () { throw new Error(debut + ' absent de ' + L.B.menu.items.map(function (i) { return i.libelle; }).join('|')); } }); };
        item('REPARER').faire();
        const apresReparation = { vie: v.vie, argent: L.B.partie.argent };
        item('REPEINDRE').faire();
        const apresPeinture = { vole: v.vole, argent: L.B.partie.argent };
        L.Missions.utiliserPoint(j);
        item('VENDRE').faire();
        return { libelles: libelles, vente: vente, apresReparation: apresReparation, apresPeinture: apresPeinture,
                 argent: L.B.partie.argent, reste: L.B.exterieur.entites.indexOf(v) >= 0 };
    }""")
    assert any(libelle.startswith("VENDRE") for libelle in r["libelles"]) and "REPARER" in r["libelles"]
    assert r["vente"] == round(auto["prix"] * eco["vente_fraction"] * 0.5)
    assert r["apresReparation"]["vie"] == auto["vie"]
    assert r["apresReparation"]["argent"] == 1000 - 50 * eco["reparation_par_pv"]
    assert r["apresPeinture"]["vole"] is False and r["apresPeinture"]["argent"] == r["apresReparation"]["argent"] - eco["repeinte"]
    assert r["reste"] is False, "le char vendu est encore devant le garage"
    assert r["argent"] > r["apresPeinture"]["argent"], "la vente n'a rien rapporte"


def test_l_armurerie_et_la_boutique_vendent(banc, paquet):
    batte = next(a for a in paquet["armes"] if a["slug"] == "batte")
    coupe_vent = next(t for t in paquet["tenues"] if t["slug"] == "coupe_vent")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        function entrer(lieu, type) {
            if (L.B.interieur) o.sortir();
            const porte = c.portes.find(function (p) { return p.lieu === lieu; });
            j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
            o.entrer(porte);
            const point = L.B.interieur.points.find(function (p) { return p.type === type; });
            j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
            L.Missions.utiliserPoint(j);
            return L.B.menu;
        }
        L.B.partie.argent = 500;
        const gus = entrer('armurerie', 'acheter');
        gus.items.find(function (i) { return i.libelle === %s; }).faire();
        const apresBaton = { arme: !!L.B.partie.armes.batte, argent: L.B.partie.argent, titre: gus.titre };
        L.Hud.fermerMenu();
        const rosa = entrer('vetements', 'acheter');
        rosa.items.find(function (i) { return i.libelle === 'COUPE-VENT BLEU'; }).faire();
        return { apresBaton: apresBaton, tenue: L.B.partie.tenue, tenues: L.B.partie.tenues, argent: L.B.partie.argent,
                 swap: j.swaps.c, titre: rosa.titre };
    }""" % json.dumps(batte["nom"].upper()))
    assert r["apresBaton"]["titre"] == "CHEZ GUS" and r["apresBaton"]["arme"] is True
    assert r["apresBaton"]["argent"] == 500 - batte["prix"]
    assert r["titre"] == "BOUTIQUE ROSA" and r["tenue"] == "coupe_vent" and "coupe_vent" in r["tenues"]
    assert r["swap"] == coupe_vent["couleur"], "la tenue doit changer la couleur du chandail"
    assert r["argent"] == 500 - batte["prix"] - coupe_vent["prix"]


def test_un_achat_unique_se_voit_tout_de_suite_au_comptoir(banc, paquet):
    """⚠️ Un menu est une PHOTO de l'etat au moment ou on l'ouvre. Le comptoir,
    lui, reste ouvert entre deux achats : sans un rafraichissement, le pistolet
    deja paye garde son prix, se rachete une deuxieme fois, et les munitions de
    l'arme qu'on vient d'acheter n'apparaissent qu'a la prochaine visite."""
    pistolet = next(a for a in paquet["armes"] if a["slug"] == "pistolet")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'armurerie'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const point = L.B.interieur.points.find(function (p) { return p.type === 'acheter'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        L.B.partie.argent = 2000;
        L.Missions.utiliserPoint(j);
        const menu = L.B.menu;
        function ligne(m, libelle) { return m.items.find(function (i) { return i.libelle === libelle; }) || null; }
        const avant = ligne(menu, 'PISTOLET');
        const rang = menu.items.indexOf(avant);
        menu.curseur = rang;
        // On achete par le vrai chemin : la touche ACTION, et le menu reste ouvert.
        o.tape('KeyE', 2);
        const apres = ligne(L.B.menu, 'PISTOLET');
        const etat = { ouvert: L.B.menu === menu, detail: apres && apres.detail, actif: apres && apres.actif,
                       sur: L.B.menu && L.B.menu.sur, munitions: !!ligne(L.B.menu, 'MUNITIONS PISTOLET'),
                       curseur: L.B.menu && L.B.menu.curseur };
        // Et on rappuie : un achat unique ne se paie pas deux fois.
        o.tape('KeyE', 2);
        return { avant: avant.detail, rang: rang, etat: etat, argent: L.B.partie.argent,
                 mun: L.B.partie.armes.pistolet ? L.B.partie.armes.pistolet.mun : 0 };
    }""")
    assert r["avant"] == "%d $" % pistolet["prix"]
    assert r["etat"]["ouvert"] is True, "le comptoir s'est ferme sous les doigts du joueur"
    assert r["etat"]["detail"] == "DEJA A TOI", "le comptoir affiche encore le prix d'une arme payee"
    assert r["etat"]["actif"] is False
    assert r["etat"]["sur"] == "%d $" % (2000 - pistolet["prix"]), "le magot affiche n'a pas bouge"
    assert r["etat"]["munitions"] is True, "les munitions de l'arme achetee n'apparaissent pas"
    assert r["etat"]["curseur"] == r["rang"], "le curseur a saute sous le pouce"
    assert r["argent"] == 2000 - pistolet["prix"], "le pistolet s'est paye deux fois"
    assert r["mun"] == pistolet["chargeur"], "l'arme achetee doit venir avec son chargeur"


def test_une_propriete_s_achete_et_rapporte(banc, paquet):
    kiosque = next(p for p in paquet["economie"]["proprietes"] if p["slug"] == "kiosque")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'kiosque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        L.B.partie.argent = 2000;
        const ouvert = L.Missions.acheterPropriete(porte);
        L.B.menu.items[0].faire();
        L.Hud.fermerMenu();
        const achete = !!L.B.partie.proprietes.kiosque;
        L.Missions.revenusDuJour(); L.Missions.revenusDuJour(); L.Missions.revenusDuJour(); L.Missions.revenusDuJour();
        const caisse = L.B.partie.proprietes.kiosque.caisse;
        // Dedans, on ramasse la caisse.
        o.entrer(porte);
        const point = L.B.interieur.points.find(function (p) { return p.type === 'caisse'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        L.Missions.utiliserPoint(j);
        const avant = L.B.partie.argent;
        L.B.menu.items[0].faire();
        L.Missions.majInvite(j);
        return { invite: invite, ouvert: ouvert, achete: achete, caisse: caisse, gain: L.B.partie.argent - avant,
                 reste: L.B.partie.proprietes.kiosque.caisse, deuxieme: L.Missions.acheterPropriete(porte) };
    }""")
    assert r["invite"].startswith("ACHETER"), r["invite"]
    assert r["ouvert"] is True and r["achete"] is True
    assert r["caisse"] == kiosque["revenu_par_jour"] * paquet["economie"]["caisse_jours_max"], "la caisse doit plafonner"
    assert r["gain"] == r["caisse"] and r["reste"] == 0
    assert r["deuxieme"] is False, "une propriete a soi ne se rachete pas"


def test_les_paquets_caches_se_ramassent_et_paient(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const paquets = L.B.entites.filter(function (e) { return e.type === 'paquet'; });
        const n = paquets.length;
        const argent = L.B.partie.argent;
        for (let i = 0; i < 10; i++) {
            const q = L.B.entites.find(function (e) { return e.type === 'paquet'; });
            j.x = q.x; j.y = q.y;
            L.Entites.indexer();
            L.Missions.maj();
        }
        L.Missions.sauvegarderPartie();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        return { n: n, restants: L.B.entites.filter(function (e) { return e.type === 'paquet'; }).length,
                 gain: L.B.partie.argent - argent, sauves: Object.keys(brut.paquets).length };
    }""")
    assert r["n"] == 20
    assert r["restants"] == 10
    assert r["gain"] == 10 * tarifs["paquet"] + tarifs["paquets_prime_10"]
    assert r["sauves"] == 10, "les paquets ramasses doivent etre sauvegardes"


def test_le_journal_du_matin_raconte_hier(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.stats.tues = 0;
        L.Missions.nouveauJour();
        const calme = L.B.dialogue ? L.B.dialogue.lignes[0] : null;
        L.B.dialogue = null;
        L.B.partie.stats.tues = 2;
        L.Missions.nouveauJour();
        const sang = L.B.dialogue ? L.B.dialogue.lignes[0] : null;
        return { calme: calme, sang: sang, qui: L.B.dialogue.qui };
    }""")
    assert r["qui"] == "LE CLAIRON DE LA BAIE"
    assert r["calme"] == "BRUME SUR LE BASSIN"
    assert r["sang"] == "UN MORT DANS LA RUE"


# --- Les gestes : le corps bouge quand on agit ----------------------------


def test_le_coup_a_un_elan_et_une_pose_de_coup(banc):
    """⚠️ Le bras est DANS le sprite : la pose de coup le tend. Un bras dessine
    par-dessus faisait un troisieme bras (Martin)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.Entites.regarder(j, 1, 0);
        const repos = { pose: L.Entites.nomDePose(j), arme: L.Entites.pose(j).arme, dx: L.Entites.pose(j).dx };
        L.Combat.frapper(j, false);
        const phases = {};
        for (let i = 0; i < 40 && j.etat === 'attaque'; i++) {
            const p = L.Entites.pose(j);
            if (!phases[j.phase]) phases[j.phase] = { dx: p.dx, pose: L.Entites.nomDePose(j), image: !!L.Entites.imageDe(j).canvas };
            L.Entites.indexer(); L.Combat.maj();
        }
        // Toutes les directions ont leur pose de coup, gauche par miroir.
        const cuit = L.Atlas.cuire('joueur', L.SPRITES.joueur, null);
        const poses = ['frappe_bas', 'frappe_haut', 'frappe_droite', 'frappe_gauche'].filter(function (n) { return !!cuit.poses[n]; });
        // Une batte se voit dans la main, au repos et au coup ; la main est celle de la pose.
        L.B.partie.armes.batte = { mun: null, usure: 0 }; j.arme = 'batte';
        const mainRepos = L.Entites.imageDe(j).main;
        L.Combat.frapper(j, false);
        for (let i = 0; i < 40 && j.phase !== 'actif'; i++) { L.Entites.indexer(); L.Combat.maj(); }
        const mainCoup = L.Entites.imageDe(j).main;
        const armeTenue = L.Entites.pose(j).arme && L.Entites.pose(j).arme.slug;
        L.Entites.regarder(j, -1, 0);
        const gauche = L.Entites.imageDe(j);
        // ⚠️ L'arme doit se voir dans les QUATRE directions. La main n'est
        // decrite que du cote droit : a gauche elle se miroite (Martin : plus
        // d'arme des qu'il allait a gauche).
        const mains = {};
        [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
            L.Entites.regarder(j, d[0], d[1]);
            j.etat = 'debout'; j.phase = null;
            const marche = L.Entites.imageDe(j);
            j.etat = 'attaque'; j.phase = 'actif';
            const coup = L.Entites.imageDe(j);
            j.etat = 'debout'; j.phase = null;
            mains[j.face] = { marche: !!marche.main, coup: !!coup.main, pose: coup.pose };
        });
        L.Jeu.rendre();
        return { repos: repos, phases: phases, poses: poses, mainRepos: mainRepos, mainCoup: mainCoup, armeTenue: armeTenue,
                 gauche: { pose: gauche.pose, miroir: gauche.miroir }, mains: mains, images: L.B.stats.images };
    }""")
    assert r["repos"]["pose"] == "droite" and r["repos"]["arme"] is None and r["repos"]["dx"] == 0
    assert r["phases"]["anticipation"]["pose"] == "droite", "on arme le coup dans la pose de marche"
    assert r["phases"]["actif"]["pose"] == "frappe_droite" and r["phases"]["actif"]["image"] is True
    assert r["phases"]["anticipation"]["dx"] < 0 < r["phases"]["actif"]["dx"], "on recule puis on se jette"
    assert sorted(r["poses"]) == ["frappe_bas", "frappe_droite", "frappe_gauche", "frappe_haut"]
    assert r["armeTenue"] == "batte"
    assert r["mainRepos"] != r["mainCoup"], "la main du coup n'est pas celle du repos"
    assert r["gauche"] == {"pose": "frappe_gauche", "miroir": True}
    for face in ("bas", "haut", "droite", "gauche"):
        assert r["mains"][face]["marche"], "l'arme n'est pas dans la main en marchant vers " + face
        assert r["mains"][face]["coup"], "l'arme n'est pas dans la main en frappant vers " + face
        assert r["mains"][face]["pose"] == "frappe_" + face
    assert r["images"] > 0


def test_la_roulade_tourne_et_le_recul_chancelle(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(81);
        const j = L.B.joueur;
        j.roule = L.Combat.ROULADE_IMAGES / 2;
        const roule = L.Entites.pose(j).rot;
        j.roule = 0;
        const cible = o.poser('ouvrier', 14, 0);
        cible.vx = 1.5; cible.recul = 5;
        const chancelle = L.Entites.pose(cible).rot;
        j.animT = 5; j.animType = 'ramasse';
        const penche = L.Entites.pose(j);
        return { roule: roule, chancelle: chancelle, penche: penche.echelleY, dy: penche.dy };
    }""")
    assert abs(abs(r["roule"]) - 3.14159) < 0.05, "a mi-roulade, le corps est a l'envers"
    assert r["chancelle"] != 0
    assert r["penche"] < 1 and r["dy"] > 0, "ramasser courbe le dos"


def test_la_police_pixel_sait_ecrire_tout_ce_que_le_jeu_affiche(banc):
    """Un glyphe absent tombe sur « ? » : HÔPITAL, CASSE-CROÛTE, BÂTON… Martin
    l'a vu a l'ecran. Chaque nom du jeu doit se normaliser en glyphes connus."""
    r = banc("""function (L, o) {
        const d = L.B.defs;
        const textes = [];
        d.armes.forEach(function (a) { textes.push(a.nom); });
        d.vehicules.forEach(function (v) { textes.push(v.nom); });
        d.tenues.forEach(function (t) { textes.push(t.nom); });
        d.magasins.forEach(function (m) { textes.push(m.nom); });
        d.ambulants.forEach(function (m) { textes.push(m.nom); });
        d.carte.points_interet.forEach(function (p) { textes.push(p.nom); });
        d.carte.zones.forEach(function (z) { textes.push(z.nom); });
        Object.keys(d.carte.interieurs).forEach(function (k) { textes.push(d.carte.interieurs[k].nom); });
        d.journal.forEach(function (j) { textes.push(j.titre, j.texte); });
        d.audio.voix.forEach(function (v) { textes.push(v.texte); });
        d.audio.radios.forEach(function (r) { textes.push(r.nom); });
        d.economie.proprietes.forEach(function (p) { textes.push(p.nom); });
        d.pietons.catalogue.forEach(function (p) { textes.push(p.nom); });
        ['DORMIR JUSQU’AU MATIN', 'REVEIL A L’HOPITAL — 30 $', 'Baie-des-Brumes… la brume'].forEach(function (t) { textes.push(t); });
        // La fortune du HUD : toLocaleString colle une espace fine insecable entre les milliers.
        textes.push((1078).toLocaleString('fr-CA') + ' $', (1250000).toLocaleString('fr-CA') + ' $');
        const inconnus = {};
        textes.forEach(function (t) {
            for (const ch of L.Atlas.normaliser(t)) if (ch !== ' ' && !L.POLICE_PIXEL[ch]) inconnus[ch] = (inconnus[ch] || 0) + 1;
        });
        return { n: textes.length, inconnus: inconnus, hopital: L.Atlas.normaliser('Hôpital de Baie-des-Brumes'),
                 largeur: L.Atlas.largeurTexte('Œuvre', 1),
                 argent: L.Atlas.normaliser((1078).toLocaleString('fr-CA') + ' $') };
    }""")
    assert r["n"] > 40
    assert r["inconnus"] == {}, f"glyphes que la police ne sait pas ecrire : {r['inconnus']}"
    assert r["hopital"] == "HOPITAL DE BAIE-DES-BRUMES"
    assert r["argent"] == "1 078 $", "le separateur des milliers doit devenir une vraie espace"
    assert r["largeur"] == 6 * 4 - 1, "la largeur doit compter le OE en deux lettres"


def test_la_pause_a_un_menu_des_options_et_un_bilan(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.tape('Escape', 2);
        const pause = { etat: L.B.etat, menu: L.B.menu && L.B.menu.titre };
        // OPTIONS : troisieme ligne ; on bascule le sang.
        L.B.menu.items.find(function (i) { return i.libelle === 'OPTIONS'; }).faire();
        const options = L.B.menu.titre;
        const sangAvant = L.B.options.sang;
        L.B.menu.items.find(function (i) { return i.libelle === 'SANG'; }).faire(L.B.menu.items[0]);
        const sangApres = L.B.options.sang;
        const sauvees = JSON.parse(o.store[L.Sauvegarde.CLE_OPTIONS]).sang;
        L.B.menu.items.find(function (i) { return i.libelle === 'RETOUR'; }).faire();
        L.B.menu.items.find(function (i) { return i.libelle === 'BILAN DE LA SESSION'; }).faire();
        const bilan = { titre: L.B.menu.titre, lignes: L.B.menu.items.length };
        o.tape('Escape', 2);
        return { pause: pause, options: options, sangAvant: sangAvant, sangApres: sangApres, sauvees: sauvees,
                 bilan: bilan, etat: L.B.etat, menu: L.B.menu };
    }""")
    assert r["pause"] == {"etat": "pause", "menu": "PAUSE"}
    assert r["options"] == "OPTIONS" and r["sangApres"] == (not r["sangAvant"]) and r["sauvees"] == r["sangApres"]
    assert r["bilan"]["titre"] == "BILAN" and r["bilan"]["lignes"] >= 9
    assert r["etat"] == "jeu" and r["menu"] is None, "Echap doit reprendre et fermer le menu"


# --- M4 : la police -----------------------------------------------------------


def test_le_a_etoile_contourne_un_batiment_et_ne_gele_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, j = L.B.joueur;
        // Un batiment garanti : on part devant sa porte et on vise derriere lui (la ruelle).
        const porte = c.portes.find(function (p) { return p.lieu === 'armurerie'; });
        const x0 = porte.x * L.TT + 8, y0 = (porte.y + 1) * L.TT + 8;
        let ty = porte.y - 1;
        while (ty > 0 && L.Monde.solidite(porte.x, ty) === 1) ty--;
        const x1 = porte.x * L.TT + 8, y1 = ty * L.TT + 8;
        const t0 = Date.now();
        const chemin = L.Monde.chemin(x0, y0, x1, y1, L.Monde.MASQUE_PIETON);
        const ms = Date.now() - t0;
        let traverseUnMur = false;
        (chemin || []).forEach(function (p) { if (L.Monde.solidite(Math.floor(p.x / L.TT), Math.floor(p.y / L.TT)) === 1) traverseUnMur = true; });
        const direct = Math.abs(y1 - y0) / L.TT;
        // La file : deux demandes servies par image, la troisieme attend.
        let servies = 0;
        for (let i = 0; i < 3; i++) L.Monde.demanderChemin(x0, y0, x1, y1, L.Monde.MASQUE_PIETON, function () { servies++; });
        L.Monde.majChemins();
        const apresUneImage = servies, enAttente = L.Monde.cheminsEnAttente;
        L.Monde.majChemins();
        // Une cible dans un mur : null, tout de suite.
        const impossible = L.Monde.chemin(x0, y0, porte.x * L.TT + 8, porte.y * L.TT + 8, L.Monde.MASQUE_PIETON);
        return { trouve: !!chemin, longueur: chemin ? chemin.length : 0, direct: direct, traverseUnMur: traverseUnMur,
                 ms: ms, apresUneImage: apresUneImage, enAttente: enAttente, servies: servies, impossible: impossible };
    }""")
    assert r["trouve"], "pas de chemin pour contourner l'armurerie"
    assert r["traverseUnMur"] is False
    assert r["longueur"] > r["direct"], "le chemin doit faire le tour, pas passer a travers"
    assert r["ms"] < 50
    assert r["apresUneImage"] == 2 and r["enAttente"] == 1 and r["servies"] == 3
    assert r["impossible"] is None


def test_un_char_coince_dix_secondes_est_debloque(banc):
    """Quelle qu'en soit la cause (ici : le joueur plante devant, de travers
    dans la boite), un char du trafic qui ne bouge plus repart — par lui-meme
    (la cascade de sorties) ou par le chien de garde. Et un char qui fait du
    SUR-PLACE (il bouge sans avancer : un va-et-vient) se fait mordre aussi :
    la capture de Martin montrait un char jamais immobile, jamais debloque."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(95);
        const c = L.Monde.carte, j = L.B.joueur, T = L.TT;
        const inter = c.intersections.find(function (i) { return i.feux && i.l === 4; });
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
        // Un char de travers au milieu de la boite, sans cible, le joueur colle devant lui.
        const v = L.Vehicules.creer('auto', (inter.x + 1) * T + 12, (inter.y + 1) * T + 10, 0.6, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        v.cible = { x: v.x, y: v.y, tx: inter.x + 1, ty: inter.y + 1 };
        j.x = v.x + Math.cos(0.6) * 24; j.y = v.y + Math.sin(0.6) * 24;
        L.Monde.centrerCamera(j.x, j.y);
        const x0 = v.x, y0 = v.y, angle0 = v.angle;
        let bouge = 0;
        for (let i = 0; i < 1500; i++) {
            o.frame(1);
            j.x = v.x + Math.cos(v.angle) * 24; j.y = v.y + Math.sin(v.angle) * 24;   // le joueur reste devant
            if (Math.hypot(v.x - x0, v.y - y0) > 40 && !bouge) bouge = i;
        }
        const droit = Math.abs(Math.sin(2 * v.angle)) < 0.2;
        // Le sur-place : un char qu'on ramene chaque image a son point de depart.
        const w = L.Vehicules.creer('auto', (inter.x + 1) * T + 8, (inter.y + 1) * T + 8, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        const wx = w.x, wy = w.y;
        let mordu = -1;
        // ⚠️ Le joueur reste colle au char et en vie A CHAQUE IMAGE. Deux
        // raisons, et la seconde a deja fait passer ce test pour un bogue du
        // chien de garde : la bulle d'oubli retire un char loin du joueur, et un
        // joueur plante vingt secondes au milieu d'un croisement finit par se
        // faire renverser — l'hopital l'emmene a l'autre bout de la ville, le
        // char est oublie, et plus personne ne surveille rien.
        for (let i = 0; i < 1400 && mordu < 0; i++) {
            j.x = wx; j.y = wy + 40; j.vie = j.vieMax; j.invincible = 30;
            L.Monde.centrerCamera(j.x, j.y);
            o.frame(1);
            if (w.debloques) mordu = i; else { w.x = wx; w.y = wy; }
        }
        return { bouge: bouge, debloques: v.debloques || 0, droit: droit, angle0: angle0,
                 surRoute: L.Monde.estRoute(Math.floor(v.x / T), Math.floor(v.y / T)), mordu: mordu };
    }""")
    assert 0 < r["bouge"] < 700, "le char n'est jamais reparti (seul, ou par le chien de garde a 600 images)"
    assert 600 <= r["mordu"] < 1300, "un char qui bouge sans avancer doit se faire mordre par le chien de garde"
    assert r["surRoute"], "le char debloque a fini hors de la route"


def test_un_char_sort_de_chaque_t_par_la_tige_sans_tourner_en_rond(banc):
    """Martin : « ils tournent en rond dans l'intersection ». Par la tige d'un
    T, la sortie prevue est souvent impossible depuis la rangee ou l'on entre :
    le char doit quand meme sortir, par n'importe quel bras, sans repasser
    par la boite."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(97);
        const c = L.Monde.carte, j = L.B.joueur, T = L.TT;
        const tes = c.intersections.filter(function (i) { return i.stop; });
        const resultats = [];
        tes.forEach(function (inter, k) {
            if (k % 3) return;                        // un T sur trois : assez pour couvrir les quatre tiges
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
            j.x = (inter.x - 1) * T + 8; j.y = (inter.y - 1) * T + 8;
            L.Monde.centrerCamera(j.x, j.y);
            // La ligne d'arret de la tige : la tuile 'S' dont le sens est celui du stop.
            let sx = -1, sy = -1;
            for (const cle in c.arrets) {
                if (c.arrets[cle] !== inter.stop) continue;
                const xy = cle.split(',').map(Number);
                const p = { '<': [-1, 0], '>': [1, 0], '^': [0, -1], 'v': [0, 1] }[inter.stop];
                if (L.Monde.intersectionA(xy[0] + p[0], xy[1] + p[1]) === inter) { sx = xy[0]; sy = xy[1]; break; }
            }
            if (sx < 0) { resultats.push({ inter: k, stop: inter.stop, erreur: 'pas de ligne d arret' }); return; }
            const p = { '<': [-1, 0], '>': [1, 0], '^': [0, -1], 'v': [0, 1] }[inter.stop];
            const v = L.Vehicules.creer('auto', (sx - p[0] * 2) * T + 8, (sy - p[1] * 2) * T + 8, Math.atan2(p[1], p[0]), { conducteur: 'trafic', etat: 'roule', sens: inter.stop });
            v.sortie = ['droit', 'gauche', 'droite'];   // tout droit : impossible, c'est la tige
            let entre = false, sorti = false, boucles = 0, derniere = null;
            const vus = new Set();
            for (let i = 0; i < 1500 && !sorti; i++) {
                o.frame(1);
                const tx = Math.floor(v.x / T), ty = Math.floor(v.y / T);
                const cle = tx + ',' + ty;
                const dedans = tx >= inter.x - 2 && tx < inter.x + inter.l + 2 && ty >= inter.y - 2 && ty < inter.y + inter.h + 2;
                if (dedans) {
                    entre = true;
                    // Une boucle, c'est REVENIR sur une tuile deja quittee — pas y rester.
                    if (cle !== derniere) { if (vus.has(cle)) boucles++; vus.add(cle); derniere = cle; }
                }
                else if (entre && L.Monde.fleche(tx, ty) !== '.' && L.Monde.fleche(tx, ty) !== '+') sorti = true;
            }
            resultats.push({ inter: k, stop: inter.stop, entre: entre, sorti: sorti, boucles: boucles, sens: v.sens, debloques: v.debloques || 0 });
        });
        return resultats;
    }""")
    assert r, "aucun T"
    for res in r:
        assert "erreur" not in res, res
        assert res["entre"] and res["sorti"], f"le char n'est pas ressorti du T : {res}"
        assert res["debloques"] == 0, f"le chien de garde a du intervenir : {res}"
        assert res["boucles"] <= 1, f"le char a tourne en rond dans le T : {res}"
