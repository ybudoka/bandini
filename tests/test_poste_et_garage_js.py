"""Le poste a son stationnement, le garage sa vraie porte (17 sept. 2026) — au banc.

Demande de Martin : « ajoute toujours un stationnement au poste de police avec
une ou des vehicules de police stationnes et aussi pour le garage, il faut une
vraie porte de garage ou on stationne pour vendre ou faire des missions. la
porte ouvre seule des qu'on est devant en voiture. »

La ville (le lot, la porte, la baie) se juge dans `test_poste_et_garage.py`.
Ici, ce qui vit : les autos-patrouilles qui s'y garent, le rideau qui monte
quand on arrive au volant, et le menu du garage quand on s'arrete devant — au
bouton, parce que c'est le bouton qui vend.
"""

import unicodedata


def _sans_accent(texte):
    """⚠️ Les libelles du jeu prennent leurs accents (« RÉPARER ») : un juge qui
    les epelle a la main tombe le jour ou la vague des accents passe."""
    return "".join(c for c in unicodedata.normalize("NFD", texte) if not unicodedata.combining(c))


#: Ce que fait la boucle de jeu autour du joueur : on lui laisse le temps de
#: passer plusieurs fois par `peupler` (une image sur vingt).
IMAGES_DE_PEUPLER = 80

#: Arriver devant le garage au volant, pour de vrai : un char nez au nord sur la
#: chaussee, quatre tuiles sous le rideau, gaz jusqu'a la baie, frein jusqu'a
#: l'arret. La rue est videe autour (le trafic et les passants du hasard ne sont
#: pas ce qu'on juge).
ARRIVER = """
    function arriver(L, o, vitesseMax) {
        const j = L.B.joueur, TT = L.TT;
        const pg = L.Monde.porteDeGarage('garage'), baie = L.Monde.baieDeLaPorteDeGarage(pg);
        j.x = baie.x; j.y = baie.y + 3 * TT; L.Monde.centrerCamera(j.x, j.y);
        L.B.entites.filter(function (e) { return (e.type === 'vehicule' || e.type === 'pieton') && e !== j
            && Math.hypot(e.x - baie.x, e.y - baie.y) < 260; }).forEach(function (e) { L.Entites.retirer(e); });
        const v = L.Vehicules.creer('auto', baie.x, baie.y + 3 * TT, -Math.PI / 2, { etat: 'stationne', couleur: '#c0392b' });
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
        const trajet = [];
        o.touche('KeyW');
        for (let k = 0; k < 400 && v.y > baie.y + 2; k++) {
            if (Math.abs(v.vitesse) > vitesseMax) { o.relacher('KeyW'); } else o.touche('KeyW');
            o.frame(1);
            trajet.push({ y: (v.y - baie.y) / TT, ouverture: pg.ouverture, menu: !!L.B.menu });
        }
        o.relacher('KeyW');
        o.touche('KeyS');
        for (let k = 0; k < 200 && v.vitesse > 0.05 && !L.B.menu; k++) o.frame(1);
        o.relacher('KeyS');
        // ⚠️ Le frein tenu passe en marche arriere : on laisse le char s'immobiliser.
        for (let k = 0; k < 120 && Math.abs(v.vitesse) >= 0.05 && !L.B.menu; k++) o.frame(1);
        return { v: v, pg: pg, baie: baie, trajet: trajet };
    }
"""


def test_les_autos_patrouilles_se_garent_dans_les_cases_du_poste(banc, paquet):
    """On arrive au poste : les places `garees` ont chacune leur auto-patrouille,
    nez au nord, a cheval sur les deux tuiles de sa case, sans conducteur — et
    rien n'a ete tire au de du jeu pour les poser."""
    police = next(v for v in paquet["vehicules"] if v["slug"] == "police")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT;
        const lot = L.Monde.carte.def.stationnement_du_poste;
        const cx = (lot.x + lot.largeur / 2) * TT, cy = (lot.y + 1) * TT;
        // Plante devant le lot, il a l'ecran : rien ne pousse sous les yeux.
        j.x = cx; j.y = cy + 4 * TT; L.Monde.centrerCamera(j.x, j.y);
        const dansLeChamp = L.Entites.visibleAEcran(cx, cy, 24);
        o.frame(%(images)d);
        const sousLesYeux = L.B.entites.filter(function (e) { return e.gareDeService; }).length;
        // A une demi-bulle, hors champ : elles naissent la ou on ne les voit pas.
        j.x = cx + 330; j.y = cy + 60; L.Monde.centrerCamera(j.x, j.y);
        const visible = L.Entites.visibleAEcran(cx, cy, 24);
        const avant = L.B.entites.filter(function (e) { return e.gareDeService; }).length;
        // Le de du jeu : compte pendant UN passage du lot, appele a la main.
        let des = 0;
        const rng = L.B.rng;
        L.B.rng = function () { des++; return rng.apply(null, arguments); };
        const nees = L.Vehicules.majGaresDeService();
        L.B.rng = rng;
        const posees = L.B.entites.filter(function (e) { return e.gareDeService; });
        posees.forEach(function (e) { L.Entites.retirer(e); });
        o.frame(%(images)d);
        const garees = L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.gareDeService; });
        return { dansLeChamp: dansLeChamp, sousLesYeux: sousLesYeux, visible: visible, avant: avant, nees: nees, des: des, garees: lot.garees,
                 places: lot.places.slice(0, lot.garees).map(function (p) { return { x: p.x, y: p.y }; }),
                 chars: garees.map(function (e) {
                     return { slug: e.slug, tx: e.x / TT, ty: e.y / TT, angle: e.angle, etat: e.etat,
                              conducteur: e.conducteur, couleur: e.couleur, place: lot.places.indexOf(e.gareDeService) };
                 }) };
    }""" % {"images": IMAGES_DE_PEUPLER})
    assert r["dansLeChamp"] is True, "le juge devait avoir le lot sous les yeux"
    assert r["sousLesYeux"] == 0, "une auto-patrouille est apparue dans le lot, a l'ecran"
    assert r["visible"] is False, "le juge devait regarder ailleurs"
    assert r["avant"] == 0, "des autos-patrouilles au poste avant d'y aller : la bulle ne sert a rien"
    assert r["nees"] == r["garees"] >= 1
    assert r["des"] == 0, f"{r['des']} des du jeu tires pour garer des chars de decor"
    assert len(r["chars"]) == r["garees"], f"la boucle de jeu n'a pas garni le lot : {r['chars']}"
    for char in r["chars"]:
        place = r["places"][char["place"]]
        assert char["slug"] == "police" and char["couleur"] == police["couleurs"][0]
        assert char["etat"] == "stationne" and char["conducteur"] is None, char
        # Nez au nord, a cheval sur la case : le milieu de la tuile en x, la
        # couture entre ses deux tuiles en y.
        assert abs(char["angle"] + 3.14159265 / 2) < 1e-6, char
        assert abs(char["tx"] - (place["x"] + 0.5)) < 1e-6 and abs(char["ty"] - (place["y"] + 1)) < 1e-6, char
    assert len({c["place"] for c in r["chars"]}) == len(r["chars"]), "deux chars sur la meme place"


def test_une_auto_patrouille_prise_ne_revient_pas_tant_qu_elle_existe(banc):
    """On vole une auto-patrouille du lot et on l'emmene ailleurs : sa place
    reste vide tant que le char vit — sinon le poste fabriquerait des chars a
    voler a la chaine."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT;
        const lot = L.Monde.carte.def.stationnement_du_poste;
        const cx = (lot.x + lot.largeur / 2) * TT, cy = (lot.y + 1) * TT;
        j.x = cx + 330; j.y = cy + 60; L.Monde.centrerCamera(j.x, j.y);
        o.frame(%(images)d);
        const v = L.B.entites.find(function (e) { return e.gareDeService === lot.places[0]; });
        if (!v) return { pris: false };
        L.Vehicules.monter(j, v);
        L.Vehicules.descendre(j, true);
        v.x = cx + 260; v.y = cy + 90; j.x = cx + 330; j.y = cy + 60; L.Monde.centrerCamera(j.x, j.y);
        L.Entites.indexer();
        o.frame(%(images)d);
        const surLaPlace = L.B.entites.filter(function (e) {
            return e.type === 'vehicule' && Math.hypot(e.x - (lot.places[0].x + 0.5) * TT, e.y - (lot.places[0].y + 1) * TT) < 4;
        }).length;
        return { pris: true, existe: L.B.entites.indexOf(v) >= 0, surLaPlace: surLaPlace };
    }""" % {"images": IMAGES_DE_PEUPLER})
    assert r["pris"], "pas d'auto-patrouille a voler au poste"
    assert r["existe"], "le juge devait garder le char vole dans la bulle"
    assert r["surLaPlace"] == 0, "le lot a refait une auto-patrouille a la place de celle qu'on a volee"


def test_au_volant_le_rideau_se_leve_des_qu_on_arrive_et_le_menu_s_ouvre_a_l_arret(banc):
    r = banc("""function (L, o) {
        %(arriver)s
        L.Jeu.commencer();
        const a = arriver(L, o, 1.6);
        const menu = L.B.menu;
        // Le rideau montait-il AVANT qu'on soit gare ? Ou en etait le char quand
        // il a commence a monter ?
        const debut = a.trajet.find(function (p) { return p.ouverture > 0; });
        return { debut: debut || null, fin: a.pg.ouverture, arrete: Math.abs(a.v.vitesse) < 0.3,
                 menu: menu && { titre: menu.titre, items: menu.items.map(function (i) { return i.libelle; }), curseur: menu.curseur },
                 menuEnRoulant: a.trajet.some(function (p) { return p.menu; }),
                 auVolant: L.B.joueur.dansVehicule === a.v };
    }""" % {"arriver": ARRIVER})
    assert r["debut"], "le rideau ne s'est jamais leve"
    assert r["debut"]["y"] > 2.5, f"le rideau ne monte qu'une fois gare (a {r['debut']['y']:.1f} tuiles)"
    assert r["menuEnRoulant"] is False, "le menu s'est ouvert pendant qu'on roulait"
    assert r["fin"] == 1 and r["arrete"] and r["auVolant"]
    assert r["menu"], "arrete devant le rideau leve, le menu du garage ne s'ouvre pas"
    assert r["menu"]["titre"] == "GARAGE ROCCO BANDINI"
    libelles = [_sans_accent(i) for i in r["menu"]["items"]]
    assert any(i.startswith("VENDRE") for i in libelles) and "REPARER" in libelles, libelles
    assert any(i.startswith("REPEINDRE") for i in libelles), libelles


def test_deux_pressions_d_action_devant_le_rideau_ne_vendent_pas_le_char(banc):
    """Le menu s'ouvre tout seul au moment ou l'on freine — c'est-a-dire au
    moment ou la main appuie sur ACTION pour descendre. Deux pressions laissent
    le char a soi ; le menu ne revient pas tant qu'on reste dans la baie ; on
    ressort, on revient, et c'est BAS puis ACTION qui vend."""
    r = banc("""function (L, o) {
        %(arriver)s
        L.Jeu.commencer();
        L.B.partie.argent = 0;
        const a = arriver(L, o, 1.6);
        const ouvert = !!L.B.menu;
        o.tape('KeyE', 2);
        const apresUne = { menu: !!L.B.menu, auVolant: L.B.joueur.dansVehicule === a.v };
        o.tape('KeyE', 2);
        const apresDeux = { argent: L.B.partie.argent, existe: L.B.entites.indexOf(a.v) >= 0 };
        // Toujours dans la baie (on vient peut-etre de descendre) : il ne revient pas.
        if (L.B.joueur.dansVehicule !== a.v) L.Vehicules.monter(L.B.joueur, a.v);
        a.v.x = a.baie.x; a.v.y = a.baie.y; a.v.vitesse = 0;
        o.frame(60);
        const revient = !!L.B.menu;
        // On ressort de la baie, on revient : le menu, et BAS + ACTION vend.
        a.v.y = a.baie.y + 3 * L.TT; o.frame(3);
        a.v.y = a.baie.y; o.frame(3);
        const rouvert = !!L.B.menu;
        o.tape('ArrowDown', 2);
        const ligne = L.B.menu && L.B.menu.items[L.B.menu.curseur].libelle;
        o.tape('KeyE', 2);
        return { ouvert: ouvert, apresUne: apresUne, apresDeux: apresDeux, revient: revient, rouvert: rouvert, ligne: ligne,
                 argent: L.B.partie.argent, vendu: L.B.entites.indexOf(a.v) < 0,
                 aPied: !L.B.joueur.dansVehicule, joueurDansLaCarte: !L.Monde.bloque(Math.floor(L.B.joueur.x / L.TT), Math.floor(L.B.joueur.y / L.TT), L.Monde.MASQUE_PIETON) };
    }""" % {"arriver": ARRIVER})
    assert r["ouvert"], "pas de menu devant le rideau"
    assert r["apresUne"]["menu"] is False, "ACTION n'a pas referme le menu (REPARTIR en tete)"
    assert r["apresDeux"]["existe"] and r["apresDeux"]["argent"] == 0, "deux pressions d'ACTION ont vendu le char"
    assert r["revient"] is False, "le menu revient en boucle tant qu'on reste gare"
    assert r["rouvert"], "on ressort et on revient : le menu ne se rouvre pas"
    assert r["ligne"].startswith("VENDRE"), r["ligne"]
    assert r["vendu"] and r["argent"] > 0, "BAS + ACTION n'a pas vendu le char"
    assert r["aPied"] and r["joueurDansLaCarte"], "vendu du volant, le joueur est reste dans un char qui n'existe plus"


def test_a_pied_ou_trop_loin_le_rideau_reste_baisse(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT;
        const pg = L.Monde.porteDeGarage('garage'), baie = L.Monde.baieDeLaPorteDeGarage(pg);
        j.x = baie.x; j.y = baie.y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        o.frame(40);
        const aPied = { ouverture: pg.ouverture, menu: !!L.B.menu };
        const v = L.Vehicules.creer('auto', baie.x, baie.y + 6 * TT, -Math.PI / 2, { etat: 'stationne', couleur: '#c0392b' });
        L.Entites.indexer(); L.Vehicules.monter(j, v);
        o.frame(40);
        return { aPied: aPied, loin: pg.ouverture };
    }""")
    assert r["aPied"] == {"ouverture": 0, "menu": False}, "le rideau se leve pour un pieton"
    assert r["loin"] == 0, "le rideau se leve pour un char a six tuiles"


def test_le_char_d_une_mission_se_livre_devant_le_rideau_sans_menu(banc):
    """« ou on stationne pour vendre ou faire des missions » : une livraison au
    garage vise la baie du rideau (la fleche y mene), le rideau se leve pour le
    char de la mission, et AUCUN menu ne s'ouvre par-dessus l'objectif."""
    r = banc("""function (L, o) {
        %(arriver)s
        L.Jeu.commencer();
        const pg = L.Monde.porteDeGarage('garage'), baie = L.Monde.baieDeLaPorteDeGarage(pg);
        const vise = L.Histoire.lieuDeLivraison('garage');
        const ailleurs = L.Histoire.lieuDeLivraison('bar');
        const bar = L.Histoire.lieu('bar');
        // Un char de mission : `mission` pose, comme M1 et M4 le font.
        const creer = L.Vehicules.creer;
        L.Vehicules.creer = function (slug, x, y, angle, options) { const v = creer(slug, x, y, angle, options); if (v) v.mission = 'm1'; return v; };
        const a = arriver(L, o, 1.6);
        L.Vehicules.creer = creer;
        o.frame(30);
        return { vise: vise, baie: baie, ailleurs: ailleurs, bar: bar, ouverture: pg.ouverture, menu: !!L.B.menu };
    }""" % {"arriver": ARRIVER})
    assert (r["vise"]["x"], r["vise"]["y"]) == (r["baie"]["x"], r["baie"]["y"]), "la livraison au garage ne vise pas la baie"
    assert (r["ailleurs"]["x"], r["ailleurs"]["y"]) == (r["bar"]["x"], r["bar"]["y"]), "un lieu sans rideau a change de cible"
    assert r["ouverture"] == 1, "le rideau reste baisse devant le char de la mission"
    assert r["menu"] is False, "le menu du garage s'ouvre par-dessus la livraison d'une mission"


def test_le_panneau_de_la_livraison_ne_se_plante_pas_devant_le_rideau(banc, paquet):
    """Le panneau du defi se posait trois tuiles a l'ouest de la porte de Ti-Guy —
    pile dans la baie. Pousse a l'est, il tombait sous le nez de Marco, et ACTION
    lui parlait au lieu de lire le panneau : on le juge au bouton."""
    livraison = next(d for d in paquet["defis"] if d["slug"] == "livraison")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        const pg = L.Monde.porteDeGarage('garage');
        const panneaux = B.entites.filter(function (e) { return e.type === 'panneau'; }).map(function (e) {
            return { defi: e.defi, devant: L.Monde.devantLaPorteDeGarage(pg, e.x, e.y, 2, 1) };
        });
        const p = B.entites.find(function (e) { return e.type === 'panneau' && e.defi === 'livraison'; });
        if (!p) return { panneaux: panneaux };
        j.x = p.x; j.y = p.y + 8; L.Entites.indexer();
        o.tape('KeyE', 2);
        return { panneaux: panneaux, menu: B.menu && B.menu.titre };
    }""")
    assert any(p["defi"] == "livraison" for p in r["panneaux"]), "le panneau de la livraison a disparu"
    assert not any(p["devant"] for p in r["panneaux"]), f"un panneau plante devant le rideau : {r['panneaux']}"
    assert r["menu"] == livraison["titre"].upper(), f"ACTION au panneau ouvre « {r['menu']} » au lieu du defi"
