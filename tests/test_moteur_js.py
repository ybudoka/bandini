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
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const x0 = j.x;
        o.touche('KeyD'); o.frame(60); o.relacher('KeyD');
        const x1 = j.x;
        o.touche('ShiftLeft'); o.touche('KeyD'); o.frame(60); o.relacher('KeyD'); o.relacher('ShiftLeft');
        const x2 = j.x;
        // Vers le haut, un batiment se trouve sur le chemin : on doit s'arreter dessus.
        o.touche('KeyW'); o.frame(900); o.relacher('KeyW');
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { x0: x0, x1: x1, x2: x2, sol: L.Monde.solidite(tx, ty), y: j.y, etat: L.B.etat,
                 dataEtat: o.elements.bandini.dataset.etat };
    }""")
    assert r["x1"] > r["x0"] + 50
    assert r["x2"] - r["x1"] > (r["x1"] - r["x0"]) * 1.4, "le sprint doit etre nettement plus rapide"
    assert r["sol"] in (0, 3), "le joueur a fini dans un mur"
    assert r["y"] > 0
    assert r["etat"] == "jeu" and r["dataEtat"] == "jeu"


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
        o.pointeur('pointerdown', 90, 570, 1);
        o.pointeur('pointermove', 150, 570, 1);
        o.frame(60);
        const pendant = Object.assign({}, L.Entree.axe);
        o.pointeur('pointerup', 150, 570, 1);
        o.frame(2);
        o.bouton('esquive', 'pointerdown');
        o.frame(1);
        const tenu = L.entree('esquive').tactile;
        o.bouton('esquive', 'pointerup');
        return { dx: j.x - x0, pendant: pendant, tenu: tenu, apres: L.Entree.axe.mag,
                 tactile: o.doc.body.classList.contains('tactile') };
    }""")
    assert r["pendant"]["source"] == "tactile" and r["pendant"]["x"] > 0.9
    assert r["dx"] > 40
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
    """La chaine complete : je tue, quelqu'un voit, la police le sait."""
    gravite = paquet["recherche"]["delits"]["mort_pieton"]["etoiles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(21);
        function meurtre(avecTemoin) {
            L.Police.remiseAZero();
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
            const victime = o.poser('passant', 14, 0);
            if (avecTemoin) {
                const temoin = o.poser('passante', 60, 0);
                L.Entites.regarder(temoin, -1, 0);
            }
            L.Entites.indexer();
            L.Entites.tuer(victime, L.B.joueur);
            return { etoiles: L.B.recherche.etoiles, chaleur: L.B.recherche.chaleur };
        }
        const sansTemoin = meurtre(false);
        const avecTemoin = meurtre(true);
        return { sans: sansTemoin, avec: avecTemoin,
                 chaleurParGravite: L.B.defs.recherche.chaleur_par_gravite };
    }""")
    assert r["sans"]["chaleur"] == 0, "un meurtre que personne ne voit ne chauffe pas"
    assert r["avec"]["chaleur"] + r["avec"]["etoiles"] * 100 == gravite * r["chaleurParGravite"], \
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


# --- M3 : vehicules ----------------------------------------------------------


def test_on_vole_un_char_et_on_en_descend(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(41);
        const j = L.B.joueur;
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
        const suivis = new Map();
        L.B.entites.forEach(function (e) { if (e.type === 'vehicule' && e.conducteur === 'trafic') suivis.set(e.id, { x: e.x, y: e.y, d: 0 }); });
        for (let i = 0; i < 1800; i++) {
            o.frame(1);
            L.B.entites.forEach(function (e) {
                const s = suivis.get(e.id);
                if (!s) return;
                s.d += Math.hypot(e.x - s.x, e.y - s.y); s.x = e.x; s.y = e.y;
            });
        }
        const chars = L.B.entites.filter(function (e) { return e.type === 'vehicule'; });
        let dansUnMur = 0, horsRoute = 0;
        chars.forEach(function (v) {
            const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
            if (L.Monde.solidite(tx, ty) === 1) dansUnMur++;
            if (v.conducteur === 'trafic' && !L.Monde.estRoute(tx, ty)) horsRoute++;
        });
        const distances = Array.from(suivis.values()).map(function (s) { return s.d; });
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
    tarifs = paquet["economie"]["tarifs"]
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
        if (client) { v.x = client.x + 10; v.y = client.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        const etape2 = t.etape, dest = t.destination;
        if (dest) { v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        return { etape1: etape1, etape2: etape2, etape3: t.etape, gain: L.B.partie.argent - argent0, courses: t.courses };
    }""")
    assert r["etape1"] == "attente" and r["etape2"] == "course" and r["etape3"] is None
    assert r["courses"] == 1
    assert r["gain"] >= tarifs["taxi_base"] + tarifs["taxi_pourboire_max"], \
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
