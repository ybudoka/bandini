"""Ce qui se paie, sous Node : kiosques, café, souffle en surplus, compagnie de la
Brume, garage, armurerie, commerce, paquets cachés, planque, journal du matin.

Découpé de `test_moteur_js.py` (vague D, 29 sept. 2026) : même banc, mêmes juges.
"""

import json

import pytest


@pytest.fixture(scope="module")
def etals(banc):
    """⚠️ **DEUX PASSAGES AUX ÉTALS, UN BANC** (vague C, 28 sept. 2026) : le kiosque qui
    vend de la vie, puis manger et le café. Aucun ne joue d'image — on se pose devant
    l'étal et on appuie. ⚠️ Entre les deux, on remet ce que le second avait au départ :
    la caféine à zéro (le premier n'en donne pas, mais on ne le suppose pas), la vie et
    le souffle pleins, l'argent de la partie neuve ; le reste, il le pose lui-même."""
    return banc("""function (L, o) {
        L.Jeu.commencer();
        const neuf = { vie: L.B.joueur.vie, endurance: L.B.joueur.endurance, cafeine: L.B.joueur.cafeine,
                       argent: L.B.partie.argent, heure: L.B.partie.heure };
        const out = {};
        // test_le_kiosque_vend_de_la_vie_contre_de_l_argent
        out.kiosque = (function () {
            const j = L.B.joueur;
            const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === 'hotdog'; })[0];
            j.x = etal.x; j.y = etal.y + 22; j.vie = 40; L.B.partie.argent = 100;
            // ⚠️ On regarde le kiosque : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
            L.Entites.regarder(j, 0, -1);
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
        })();
        // test_manger_redonne_du_souffle_et_le_cafe_reveille
        L.B.joueur.vie = neuf.vie; L.B.joueur.endurance = neuf.endurance; L.B.joueur.cafeine = neuf.cafeine;
        L.B.partie.argent = neuf.argent; L.B.partie.heure = neuf.heure;
        out.manger = (function () {
            const j = L.B.joueur;
            L.B.partie.heure = 0.4;                    // la roulotte a cafe est ouverte
            L.B.partie.argent = 200;
            function acheter(slug) {
              const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === slug; })[0];
              j.x = etal.x; j.y = etal.y + 22;
              // ⚠️ On regarde l'étal : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
              L.Entites.regarder(j, 0, -1);
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
        })();
        return out;
    }""")


def test_le_kiosque_vend_de_la_vie_contre_de_l_argent(etals, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = etals["kiosque"]
    assert r["achat"] is True
    assert r["apres"]["argent"] == 100 - tarifs["hotdog"]
    assert r["apres"]["vie"] == 40 + tarifs["hotdog_pv"]
    assert r["refus"] is True and r["vieApresRefus"] == 40 and r["argentApresRefus"] == 1
    assert r["etals"] >= 6 and r["vendeurs"] == r["etals"], "un kiosque sans personne derriere"


def test_manger_redonne_du_souffle_et_le_cafe_reveille(etals, paquet):
    tarifs = paquet["economie"]["tarifs"]
    cafe = paquet["economie"]["cafe"]
    r = etals["manger"]
    assert r["hotdog"] is True
    assert r["apres"]["souffle"] == 20 + tarifs["hotdog_souffle"]
    assert r["apres"]["vie"] == 40 + tarifs["hotdog_pv"]
    assert r["apres"]["cafeine"] == 0, "un hot-dog nourrit, il ne reveille pas"
    assert r["plein"] == 100, "le souffle deborde"
    assert r["achatCafe"] is True
    assert r["souffleCafe"] == 20 + tarifs["cafe_souffle"]
    assert r["cafeine"] == cafe["duree_s"] * 60


def test_le_souffle_en_surplus_s_achete_et_ne_revient_pas_tout_seul(banc, paquet):
    """⚠️ Le defaut que Martin a nomme : « le souffle monte seul actuellement ».
    Il remonte de 0,24 par image des qu'on arrete de courir — une barre vide se
    remplit en sept secondes — et `nourrir` plafonnait a 100. Une poutine a 18 $
    rendait donc 70 points qu'on aurait eus gratuitement en s'arretant quatre
    secondes : le kiosque ne servait a rien, malgre l'intention inverse ecrite
    dans le depot depuis M5.

    Le surplus est ce que la regeneration ne peut PAS donner. Ce test tient les
    quatre promesses d'un coup : il se remplit par-dessus, il se depense en
    premier, il ne revient jamais tout seul, et il est passager."""
    souffle = paquet["economie"]["souffle"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const plein = L.B.defs.recherche.vitesses.endurance;
        // 1. Manger a barre pleine : la base ne bouge plus, le surplus monte.
        j.endurance = plein; j.surplus = 0;
        L.Missions.nourrir(j, 40);
        const pardessus = { base: j.endurance, surplus: j.surplus };
        // 2. Et jamais au-dela du plafond.
        L.Missions.nourrir(j, 9999);
        const plafonne = j.surplus;
        // 3. A l'arret, il ne remonte pas d'un point — la base, si.
        j.endurance = 40; j.surplus = 20;
        o.frame(120);
        const repos = { base: j.endurance, surplus: j.surplus };
        // 4. Au sprint, c'est le surplus qui part en premier.
        j.endurance = 100; j.surplus = 20;
        o.touche('ShiftLeft'); o.touche('KeyA');
        let images = 0;
        while (j.surplus > 0 && images < 400) { o.frame(1); images++; }
        const videSurplus = { base: j.endurance, images: images };
        o.relacher('KeyA'); o.relacher('ShiftLeft');
        // 5. Passager : une nuit l'efface.
        j.surplus = 30;
        L.Missions.dormir(); o.fondu();
        const apresLaNuit = j.surplus;
        return { pardessus: pardessus, plafonne: plafonne, repos: repos,
                 videSurplus: videSurplus, apresLaNuit: apresLaNuit, plein: plein };
    }""")
    assert r["pardessus"] == {"base": r["plein"], "surplus": 40}, (
        "manger a barre pleine doit monter le SURPLUS, pas la base"
    )
    assert r["plafonne"] == souffle["surplus_max"], "le surplus depasse son plafond"
    assert r["repos"]["surplus"] == 20, "le surplus remonte tout seul : il ne vaut plus rien"
    assert r["repos"]["base"] > 40, "la base, elle, doit remonter a l'arret"
    # ⚠️ Une image de jeu peut en rattraper une deuxieme (l'accumulateur de la
    # boucle) : la base a le droit de perdre le cout d'une image ou deux apres
    # que le surplus est tombe a zero, pas davantage.
    depense = paquet["recherche"]["vitesses"]["endurance_par_image"]
    assert r["videSurplus"]["base"] >= 100 - depense * 2, (
        "la base a baisse avant le surplus : on depense d'abord ce qui revient gratuitement"
    )
    assert 0 < r["videSurplus"]["images"] < 400
    assert r["apresLaNuit"] == 0, "une nuit rend le souffle, pas l'avance achetee"


def test_traverser_la_ville_en_courant_ne_coute_rien(banc, paquet):
    """⚠️ Le défaut mesuré : le modèle d'endurance avait été réglé pour le
    Faubourg de 157 tuiles, et M8 a **quintuplé la ville** sans que personne y
    revienne. Un souffle complet valait 4,2 s de course — **33 tuiles sur
    421** — et la vitesse qu'on pouvait tenir (courir, puis marcher pour
    souffler) tombait **sous celle du policier**. La barre ne récompensait
    rien : elle taxait le déplacement.

    Le juge se compare donc à la **taille de la ville**, pas à un nombre
    choisi une fois pour toutes : on traverse d'un bout à l'autre en courant,
    et la barre ne bouge pas d'un point."""
    largeur = paquet["carte"]["largeur"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        // Une longue ligne droite : la rue la plus degagee qu'on trouve, et on
        // y court le temps qu'il faudrait pour traverser la ville.
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        j.endurance = 100; j.surplus = 0;
        const souffle0 = j.endurance;
        const images = Math.ceil(%d * L.TT / L.B.defs.recherche.vitesses.joueur_course);
        o.touche('KeyD');
        let bouge = 0, avant = j.x, souffleMin = j.endurance;
        for (let i = 0; i < images; i++) {
            // ⚠️ La rue est une VOIE : le trafic arretait le joueur a un feu,
            // puis l'envoyait a l'hopital, qui rend 100 de souffle. On la vide
            // a chaque image — c'est la course qu'on juge, pas la circulation.
            L.B.entites = L.B.entites.filter(function (e) {
                return e === j || (e.type !== 'vehicule' && e.type !== 'pieton');
            });
            o.frame(1);
            bouge += Math.abs(j.x - avant); avant = j.x;
            souffleMin = Math.min(souffleMin, j.endurance);
        }
        o.relacher('KeyD');
        return { souffle0: souffle0, souffle: j.endurance, souffleMin: souffleMin, images: images,
                 bouge: Math.round(bouge), largeurPx: %d * L.TT };
    }""" % (largeur, largeur))
    # ⚠️ Sans cette mesure, le juge restait vert sans avoir couru : `bouge`
    # etait calcule, jamais affirme, et le joueur finissait a l'hopital apres
    # 4 000 px sur 7 344 — l'hopital rendait le souffle plein. On exige les
    # quatre cinquiemes de la largeur de la ville, parcourus a la course.
    assert r["bouge"] >= 0.8 * r["largeurPx"], (
        "le joueur n'a couru que %d px sur %d : il n'a pas traversé la ville, le souffle ne prouve rien"
        % (r["bouge"], r["largeurPx"])
    )
    assert r["souffle"] == r["souffleMin"] == r["souffle0"] == 100, (
        "courir a coûté du souffle : %s (au plus bas %s) au lieu de %s"
        % (r["souffle"], r["souffleMin"], r["souffle0"])
    )
    # ⚠️ La mesure doit porter sur la VILLE ENTIERE, sinon elle ne dit rien :
    # 421 tuiles a la vitesse de course, c'est pres d'une minute de touche
    # tenue. Si ce chiffre tombe, c'est que la ville a retreci — pas que le
    # souffle va mieux.
    assert r["images"] > 45 * 60, (
        "traverser la ville ne demande que %.0f s de course : la mesure ne porte plus sur la ville"
        % (r["images"] / 60)
    )


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
        // ⚠️ **SUR LE BOULEVARD DU POURTOUR, là où il y a de quoi courir.** Le
        // juge sprintait vers l'OUEST depuis le terminus : le jour où la trame a
        // bougé (17 sept. 2026), un mur s'y trouvait et le joueur a parcouru ZÉRO
        // pixel à jeun — on comparait un mur à une course. Le boulevard du nord
        // traverse toute la ville et il est droit d'un bout à l'autre.
        const c = L.Monde.carte;
        let place = null;
        for (let y = 0; y < 12 && !place; y++) {
          for (let x = 40; x < 80; x++) if (c.voie[y][x] === '>') { place = { x: x * L.TT + 8, y: y * L.TT + 8 }; break; }
        }
        j.x = place.x; j.y = place.y; L.Monde.centrerCamera(j.x, j.y);
        function tenir() {
          j.endurance = 100;
          j.x = place.x; j.y = place.y; L.Monde.centrerCamera(j.x, j.y);
          const depart = { x: j.x, y: j.y };
          let n = 0;
          o.touche('ShiftLeft'); o.touche('KeyD');
          while (j.endurance > 0 && n < 2000) {
            for (const v of L.B.entites.slice()) if (v.type === 'vehicule') L.Entites.retirer(v);
            // ⚠️ On mesure le JOUEUR, pas la foule : une flaneuse plantee sur
            // le trajet coutait 44 images de bousculade (mesure du 13 sept.
            // 2026, le jour ou huit enseignes de plus ont deplace les portes
            // par ou les passants naissent) et la vitesse tombait de 5 %.
            for (const e of L.Entites.pietonsAutour(j.x, j.y, 60)) L.Entites.retirer(e);
            o.frame(1); n++;
          }
          o.relacher('KeyD'); o.relacher('ShiftLeft');
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


def test_la_compagnie_se_paie_et_refuse_quand_la_police_cherche(la_brume, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = la_brume["compagnie"]
    assert r["metier"] == "compagnie"
    assert r["recherche"] is True and r["apresRecherche"]["argent"] == 200, \
        "elle a servi alors que la police cherchait le joueur"
    assert r["ok"] is True
    assert r["argent"] == 200 - tarifs["compagnie"]
    assert r["vie"] == 50 + tarifs["compagnie_pv"]
    assert r["fondu"] is True, "ca doit passer par un fondu, pas par une scene"


@pytest.fixture(scope="module")
def la_brume(banc):
    """⚠️ **LA FILLE DE LA BRUME, DEUX FOIS, UN BANC** (vague C, 28 sept. 2026) : l'invite
    qui la nomme (aucune image jouée), puis la compagnie qui se paie. ⚠️ Le second
    juge vidait déjà la rue lui-même et posait SA graine (33) : il repart donc du
    même monde qu'avant, l'invite remise à rien et la fille d'avant retirée avec le
    reste de la rue."""
    return banc("""function (L, o) {
        L.Jeu.commencer();
        const out = {};
        // test_le_hud_nomme_la_fille_de_la_brume
        out.invite = (function () {
            const j = L.B.joueur;
            // ⚠️ **PAS DE ROULOTTE DANS LE DOS.** L'invite ACTION nomme ce qu'il y a
            // de plus proche, et la ville pose ses ambulants où elle veut : le jour
            // où la trame a bougé (17 sept. 2026), une roulotte à café s'est
            // installée au terminus et c'est elle que le juge lisait. Ce juge-ci
            // parle de la fille, pas de ce qui se vend à côté.
            L.B.defs.ambulants = [];
            for (const q of L.B.entites.slice()) if (q !== j && q.type !== 'joueur') L.Entites.retirer(q);
            const fille = o.poser('racoleuse', 14, 0);
            fille.etat = 'arret';
            // ⚠️ On regarde la fille : l'invite n'apparaît que pour ce qu'on regarde (test_regard_js.py).
            L.Entites.regarder(j, 1, 0);
            L.Entites.indexer();
            L.Missions.majInvite(j);
            const pres = L.B.invite;
            fille.x = j.x + 200; fille.y = j.y + 200;
            L.Entites.indexer();
            L.Missions.majInvite(j);
            return { pres: pres, loin: L.B.invite };
        })();
        // test_la_compagnie_se_paie_et_refuse_quand_la_police_cherche
        L.B.invite = null;
        out.compagnie = (function () {
            L.graine(33);
            const j = L.B.joueur;
            // ⚠️ **PAS DE ROULOTTE DANS LE DOS.** ACTION sert le plus proche : le jour
            // où la trame a bougé (17 sept. 2026), une roulotte à café s'est installée
            // au terminus, et le juge a vu 4 $ de café là où il attendait un refus.
            L.B.defs.ambulants = [];
            for (const q of L.B.entites.slice()) if (q !== j && q.type !== 'joueur') L.Entites.retirer(q);
            const fille = o.poser('racoleuse', 12, 0);
            fille.etat = 'arret';
            // ⚠️ On regarde la fille : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
            L.Entites.regarder(j, 1, 0);
            L.Entites.indexer();
            j.vie = 50; L.B.partie.argent = 200;
            L.B.recherche.etoiles = 2;
            const recherche = L.Missions.interagir(j);
            const apresRecherche = { vie: j.vie, argent: L.B.partie.argent };
            L.B.recherche.etoiles = 0;
            const ok = L.Missions.interagir(j);
            const fondu = !!L.B.transition;
            o.fondu();
            return { metier: fille.metier, recherche: recherche, apresRecherche: apresRecherche,
                     ok: ok, vie: j.vie, argent: L.B.partie.argent, fondu: fondu };
        })();
        return out;
    }""")


def test_le_hud_nomme_la_fille_de_la_brume(la_brume, paquet):
    """Derniere preuve, a bout de bras : l'invite ACTION la nomme et donne le
    prix — avant, on appuyait sur ACTION en esperant que c'en etait une."""
    tarifs = paquet["economie"]["tarifs"]
    r = la_brume["invite"]
    assert r["pres"] == "LA BRUME — " + str(tarifs["compagnie"]) + " $"
    assert r["loin"] != r["pres"], "l'invite la promet alors qu'elle est partie"


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
        const fondu = !!L.B.transition;
        L.Hud.fermerMenu();
        o.fondu();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        return { menuCoffre: menuCoffre, coffre: L.B.partie.planque.coffre, poches: L.B.partie.argent,
                 jour: L.B.partie.jour - jour, heure: L.B.partie.heure, vie: j.vie,
                 sauve: { coffre: brut.planque.coffre, jour: brut.jour, x: brut.x }, fondu: fondu,
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
        item('RÉPARER').faire();
        const apresReparation = { vie: v.vie, argent: L.B.partie.argent };
        item('REPEINDRE').faire();
        const apresPeinture = { vole: v.vole, argent: L.B.partie.argent };
        L.Missions.utiliserPoint(j);
        item('VENDRE').faire();
        return { libelles: libelles, vente: vente, apresReparation: apresReparation, apresPeinture: apresPeinture,
                 argent: L.B.partie.argent, reste: L.B.exterieur.entites.indexOf(v) >= 0 };
    }""")
    assert any(libelle.startswith("VENDRE") for libelle in r["libelles"]) and "RÉPARER" in r["libelles"]
    assert r["vente"] == round(auto["prix"] * eco["vente_fraction"] * 0.5)
    assert r["apresReparation"]["vie"] == auto["vie"]
    assert r["apresReparation"]["argent"] == 1000 - 50 * eco["reparation_par_pv"]
    assert r["apresPeinture"]["vole"] is False and r["apresPeinture"]["argent"] == r["apresReparation"]["argent"] - eco["repeinte"]
    assert r["reste"] is False, "le char vendu est encore devant le garage"
    assert r["argent"] > r["apresPeinture"]["argent"], "la vente n'a rien rapporte"


def test_le_taxi_de_marco_ne_se_vend_pas(banc, paquet):
    """⚠️ Demande de Martin : « il ne faut pas pouvoir vendre le taxi de Marco. »

    M3 pose le taxi à `porte:garage` — **la porte même** du garage où Ti-Guy
    rachète n'importe quel char garé devant. Trois pas et 175 $ : le taxi sort
    du monde, et l'objectif attend un char qui n'existe plus. ⚠️ Le pire n'est
    pas l'argent, c'est que **la mission ne rate même pas** : `livrer` ne fait
    échouer que sur une épave, donc `p.mission` reste pris, le téléphone ne
    sonne plus jamais, et l'histoire s'arrête là — il faut se faire arrêter
    pour s'en sortir.

    Le juge tient les trois temps, et le troisième est celui qui compte :
    pendant la mission, **après la livraison** (`mission` tombe, `aQui` reste :
    le taxi est à Marco pour toujours), et le char de n'importe qui, qui lui se
    vend encore — sinon on aurait réparé la fuite en fermant le garage.
    """
    marco = next(p for p in paquet["personnages"] if p["slug"] == "marco")
    auto = next(v for v in paquet["vehicules"] if v["slug"] == "auto")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'garage'; });
        function alaPorte() { j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10; }
        function garer(v) { v.x = j.x + 20; v.y = j.y + 8; v.etat = 'stationne'; v.vitesse = 0; L.Entites.indexer(); }
        // Le comptoir du garage : on se plante devant et on ouvre le menu.
        function comptoir() {
            const point = L.B.interieur.points.find(function (p) { return p.type === 'vendre'; });
            j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
            L.Missions.utiliserPoint(j);
            return L.B.menu.items.find(function (i) { return i.libelle.indexOf('VENDRE') === 0; });
        }
        function essayerDeVendre(v) {
            L.B.partie.argent = 0;
            // ⚠️ Sans char devant la porte, le menu n'a pas de ligne VENDRE :
            // on la remplace par une ligne morte, sinon le juge tombe sur un
            // « undefined » au lieu de dire ce qui cloche.
            const item = comptoir() || { libelle: 'AUCUNE VENTE', detail: '', actif: false, faire: function () { return false; } };
            const vendu = item.faire();
            const r = { libelle: item.libelle, detail: item.detail, actif: item.actif !== false,
                        vendu: vendu, argent: L.B.partie.argent, la: L.B.exterieur.entites.indexOf(v) >= 0 };
            L.Hud.fermerMenu();
            return r;
        }

        L.Histoire.commencer('m3');                 // Marco prête son taxi
        const taxi = L.B.mission.vehicule;
        // Le trafic de la rue n'a rien a faire ici : le char devant la porte
        // doit etre CELUI qu'on teste, pas le premier passant.
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' || e === taxi; });
        alaPorte(); garer(taxi);
        o.entrer(porte);
        const pendant = essayerDeVendre(taxi);
        o.sortir();

        // La livraison, la vraie : on ramene le taxi au garage et la mission
        // se termine toute seule — c'est la qu'on efface `mission`.
        // ⚠️ La livraison est le DERNIER objectif (le phare et l'étoile à semer passent avant,
        // depuis « des missions plus longues ») : on la cherche plutôt que de la compter.
        L.B.partie.mission.etape = L.B.defs.missions.find(function (m) { return m.slug === 'm3'; }).objectifs.length - 1;
        const g = L.Histoire.lieu('garage');
        taxi.x = g.x; taxi.y = g.y; taxi.vitesse = 0;
        j.x = taxi.x; j.y = taxi.y;
        L.Vehicules.monter(j, taxi);
        o.frame(3);
        // La fin de M3 est une SCENE (Marco fait le tour du taxi) : on la passe.
        L.Scenes.passer();
        L.B.dialogue = null; L.B.cinema = null;
        const livre = { faite: !!L.B.partie.missionsFaites.m3, mission: taxi.mission, aQui: taxi.aQui };

        alaPorte(); garer(taxi);
        o.entrer(porte);
        const apres = essayerDeVendre(taxi);
        o.sortir();

        // Et le char de n'importe qui, a la meme place, se vend toujours.
        L.Entites.retirer(taxi);
        alaPorte();
        const v = o.char('auto', 0, 0, 0);
        garer(v);
        o.entrer(porte);
        const autre = essayerDeVendre(v);
        return { pendant: pendant, livre: livre, apres: apres, autre: autre };
    }""")
    attendu = "IL EST À " + marco["nom"].upper()
    for quand, etat in (("pendant la mission", r["pendant"]), ("apres la livraison", r["apres"])):
        assert etat["actif"] is False, f"{quand} : le garage propose encore d'acheter le taxi de Marco"
        assert etat["detail"] == attendu, f"{quand} : le menu ne dit pas a qui il est ({etat['detail']})"
        assert etat["vendu"] is False and etat["argent"] == 0, f"{quand} : la vente a rapporte de l'argent"
        assert etat["la"] is True, f"{quand} : le taxi a disparu de devant le garage"
    # ⚠️ La livraison efface `mission` — et c'est pour ca que `aQui` existe :
    # sans lui, le taxi redeviendrait vendable la minute ou Marco le recupere.
    assert r["livre"]["faite"], "la mission ne s'est pas terminee : le juge ne prouve rien"
    assert r["livre"]["mission"] is None and r["livre"]["aQui"] == "marco"
    # ⚠️ `vendu` est le retour de `faire` : au comptoir, il garde le menu ouvert
    # (`false`) — la vente se juge a l'argent et au char parti, plus bas.
    assert r["autre"]["actif"] is True and r["autre"]["argent"] > 0, (
        "plus personne ne peut vendre un char au garage : %s" % r["autre"]
    )
    assert r["autre"]["argent"] == round(auto["prix"] * paquet["economie"]["vente_fraction"])
    assert r["autre"]["la"] is False, "le char vendu est encore devant le garage"


@pytest.fixture(scope="module")
def comptoirs(banc, paquet):
    """⚠️ **TROIS COMPTOIRS, UN BANC** (vague C, 28 sept. 2026) : Gus et Rosa, le poing
    américain, le pistolet qu'on ne paie qu'une fois. Chacun entrait par la porte de
    l'armurerie dans sa partie à lui ; ils entrent maintenant l'un après l'autre dans la
    même, et ⚠️ AVANT CHACUN on remet ce qu'avait son juge au départ : menu fermé,
    dehors, le sac, la tenue et le chandail de la partie neuve (`remettre`). Sans ça,
    la batte achetée chez Gus serait « DÉJÀ À TOI » pour le suivant."""
    batte = next(a for a in paquet["armes"] if a["slug"] == "batte")
    return banc("""function (L, o) {
        L.Jeu.commencer();
        const neuf = JSON.stringify({ armes: L.B.partie.armes, tenue: L.B.partie.tenue, tenues: L.B.partie.tenues,
                                      arme: L.B.joueur.arme, swaps: L.B.joueur.swaps, argent: L.B.partie.argent });
        const depart = { x: L.B.joueur.x, y: L.B.joueur.y };
        function remettre() {
            if (L.B.menu) L.Hud.fermerMenu();
            if (L.B.interieur) o.sortir();
            const n = JSON.parse(neuf), p = L.B.partie, j = L.B.joueur;
            p.armes = n.armes; p.tenue = n.tenue; p.tenues = n.tenues; p.argent = n.argent;
            j.arme = n.arme; j.swaps = n.swaps;
            j.x = depart.x; j.y = depart.y;
        }
        const out = {};
        // test_l_armurerie_et_la_boutique_vendent
        remettre();
        out.boutiques = (function () {
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
            gus.items.find(function (i) { return i.libelle === NOM_BATTE; }).faire();
            const apresBaton = { arme: !!L.B.partie.armes.batte, argent: L.B.partie.argent, titre: gus.titre };
            L.Hud.fermerMenu();
            const rosa = entrer('vetements', 'acheter');
            rosa.items.find(function (i) { return i.libelle === 'COUPE-VENT BLEU'; }).faire();
            return { apresBaton: apresBaton, tenue: L.B.partie.tenue, tenues: L.B.partie.tenues, argent: L.B.partie.argent,
                     swap: j.swaps.c, titre: rosa.titre };
        })();
        // test_le_poing_americain_se_paie_au_comptoir_de_gus
        remettre();
        out.poing = (function () {
            const j = L.B.joueur, c = L.Monde.carte, p = L.B.partie;
            const porte = c.portes.find(function (x) { return x.lieu === 'armurerie'; });
            j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
            o.entrer(porte);
            const point = L.B.interieur.points.find(function (x) { return x.type === 'acheter'; });
            j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
            p.argent = 100;
            L.Missions.utiliserPoint(j);
            const menu = L.B.menu;
            function ligne(m) { return m.items.find(function (i) { return i.libelle === 'POING AMÉRICAIN'; }) || null; }
            const avant = ligne(menu);
            if (!avant) return { titre: menu.titre, libelles: menu.items.map(function (i) { return i.libelle; }) };
            const rang = menu.items.indexOf(avant);
            menu.curseur = rang;
            o.tape('KeyE', 2);
            const apres = ligne(L.B.menu);
            return { titre: menu.titre, rang: rang, avant: avant.detail, actif: avant.actif,
                     apres: apres && apres.detail, argent: p.argent, sac: p.armes.poing_americain || null };
        })();
        // test_un_achat_unique_se_voit_tout_de_suite_au_comptoir
        remettre();
        out.pistolet = (function () {
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
        })();
        return out;
    }""".replace("NOM_BATTE", json.dumps(batte["nom"].upper())))


def test_l_armurerie_et_la_boutique_vendent(comptoirs, paquet):
    batte = next(a for a in paquet["armes"] if a["slug"] == "batte")
    coupe_vent = next(t for t in paquet["tenues"] if t["slug"] == "coupe_vent")
    r = comptoirs["boutiques"]
    assert r["apresBaton"]["titre"] == "CHEZ GUS" and r["apresBaton"]["arme"] is True
    assert r["apresBaton"]["argent"] == 500 - batte["prix"]
    assert r["titre"] == "BOUTIQUE ROSA" and r["tenue"] == "coupe_vent" and "coupe_vent" in r["tenues"]
    assert r["swap"] == coupe_vent["couleur"], "la tenue doit changer la couleur du chandail"
    assert r["argent"] == 500 - batte["prix"] - coupe_vent["prix"]


def test_le_poing_americain_se_paie_au_comptoir_de_gus(comptoirs, paquet):
    """Martin : « on devrait aussi pouvoir l'acheter ». Par le vrai chemin : la
    porte de Chez Gus, le point `acheter`, la touche ACTION — et il entre dans
    le sac avec les autres, pret pour la roue."""
    americain = next(a for a in paquet["armes"] if a["slug"] == "poing_americain")
    r = comptoirs["poing"]
    assert r["titre"] == "CHEZ GUS"
    assert "avant" in r, "pas de poing americain au comptoir de Gus : %s" % r.get("libelles")
    assert r["rang"] == 0, "en tete de vitrine, c'est le moins cher"
    assert r["avant"] == "%d $" % americain["prix"] and r["actif"] is True
    assert r["argent"] == 100 - americain["prix"], "le poing americain ne s'est pas paye"
    assert r["sac"] is not None, "paye, mais pas dans le sac"
    assert r["apres"] == "DÉJÀ À TOI"


def test_un_achat_unique_se_voit_tout_de_suite_au_comptoir(comptoirs, paquet):
    """⚠️ Un menu est une PHOTO de l'etat au moment ou on l'ouvre. Le comptoir,
    lui, reste ouvert entre deux achats : sans un rafraichissement, le pistolet
    deja paye garde son prix, se rachete une deuxieme fois, et les munitions de
    l'arme qu'on vient d'acheter n'apparaissent qu'a la prochaine visite."""
    pistolet = next(a for a in paquet["armes"] if a["slug"] == "pistolet")
    r = comptoirs["pistolet"]
    assert r["avant"] == "%d $" % pistolet["prix"]
    assert r["etat"]["ouvert"] is True, "le comptoir s'est ferme sous les doigts du joueur"
    assert r["etat"]["detail"] == "DÉJÀ À TOI", "le comptoir affiche encore le prix d'une arme payee"
    assert r["etat"]["actif"] is False
    assert r["etat"]["sur"] == "%d $" % (2000 - pistolet["prix"]), "le magot affiche n'a pas bouge"
    assert r["etat"]["munitions"] is True, "les munitions de l'arme achetee n'apparaissent pas"
    assert r["etat"]["curseur"] == r["rang"], "le curseur a saute sous le pouce"
    assert r["argent"] == 2000 - pistolet["prix"], "le pistolet s'est paye deux fois"
    assert r["mun"] == pistolet["chargeur"], "l'arme achetee doit venir avec son chargeur"


def test_un_commerce_s_achete_au_comptoir_et_rapporte(banc, paquet):
    """Retour de Martin : « pour acheter un commerce c'est a l'interieur ».

    La porte du kiosque ouvrait un menu ACHETER / ENTRER sur le trottoir. Elle
    n'est plus qu'une porte : on entre, on va a la caisse, et c'est la qu'on
    achete — puis la meme caisse se vide dans nos poches. Tout par le bouton."""
    kiosque = next(p for p in paquet["economie"]["proprietes"] if p["slug"] == "kiosque")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const libelles = function () { return L.B.menu ? L.B.menu.items.map(function (i) { return i.libelle; }) : null; };
        const choisi = function () { return L.B.menu ? L.B.menu.items[L.B.menu.curseur].libelle : null; };
        L.B.partie.argent = 2000;
        const porte = c.portes.find(function (p) { return p.lieu === 'kiosque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // ⚠️ On regarde la porte : dehors, ENTRER n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        L.Missions.majInvite(j);
        const dehors = L.B.invite;
        o.tape('KeyE', 1);
        const aLaPorte = { menu: libelles(), fondu: !!L.B.transition };
        o.fondu();
        const dedans = L.B.interieur && L.B.interieur.slug;
        const point = L.B.interieur.points.find(function (p) { return p.type === 'caisse'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        // Et la caisse aussi : on la regarde (elle est au-dessus du joueur).
        L.Entites.regarder(j, 0, -1);
        L.Missions.majInvite(j);
        const inviteCaisse = L.B.invite;
        o.tape('KeyE', 2);
        const comptoir = { menu: libelles(), choisi: choisi(), aide: L.B.menu && L.B.menu.aide };
        o.tape('KeyE', 2);
        const achete = { ouvert: !!L.B.menu, a_soi: !!L.B.partie.proprietes.kiosque, argent: L.B.partie.argent };
        // Le comptoir reste ouvert apres l'achat : on le quitte comme le joueur, a Echap.
        o.tape('Escape', 2);
        achete.ferme = !L.B.menu;
        for (let i = 0; i < 4; i++) L.Missions.revenusDuJour();
        const caisse = L.B.partie.proprietes.kiosque.caisse;
        L.Missions.majInvite(j);
        const inviteApres = L.B.invite;
        o.tape('KeyE', 2);
        const aSoi = { menu: libelles(), choisi: choisi() };
        const avant = L.B.partie.argent;
        o.tape('KeyE', 2);
        return { dehors: dehors, aLaPorte: aLaPorte, dedans: dedans, inviteCaisse: inviteCaisse,
                 comptoir: comptoir, achete: achete, caisse: caisse, inviteApres: inviteApres, aSoi: aSoi,
                 gain: L.B.partie.argent - avant, reste: L.B.partie.proprietes.kiosque.caisse };
    }""")
    assert r["dehors"] == "ENTRER", "la porte promet encore un achat sur le trottoir"
    assert r["aLaPorte"]["menu"] is None, "la porte ouvre encore un menu : %s" % r["aLaPorte"]["menu"]
    assert r["aLaPorte"]["fondu"] is True and r["dedans"] == "kiosque"
    assert r["inviteCaisse"] == "ACHETER " + kiosque["nom"].upper()
    assert r["comptoir"]["menu"] == ["ACHETER LE COMMERCE"], r["comptoir"]["menu"]
    assert r["comptoir"]["choisi"] == "ACHETER LE COMMERCE"
    assert str(kiosque["revenu_par_jour"]) in r["comptoir"]["aide"], "le comptoir ne dit pas ce que ca rapporte"
    assert r["achete"] == {"ouvert": True, "a_soi": True, "argent": 2000 - kiosque["prix"], "ferme": True}, (
        "l'achat du commerce doit laisser le comptoir ouvert, et Echap le fermer : %s" % r["achete"])
    assert r["caisse"] == kiosque["revenu_par_jour"] * paquet["economie"]["caisse_jours_max"], "la caisse doit plafonner"
    assert r["inviteApres"] == "LA CAISSE"
    assert r["aSoi"]["menu"] == ["PRENDRE LA CAISSE"], "un commerce a soi ne se rachete pas : %s" % r["aSoi"]["menu"]
    assert r["gain"] == r["caisse"] and r["reste"] == 0


def test_au_garage_deux_pressions_vendent_le_char_et_n_achetent_pas_le_garage(banc, paquet):
    """Le garage n'a pas de caisse : l'achat passe dans le menu du comptoir,
    comme PRENDRE LA CAISSE une fois le garage a soi. ⚠️ EN DERNIER — le
    curseur s'ouvre sur la premiere ligne qui se choisit, et la main qui
    appuie deux fois pour vendre un char aurait paye le garage."""
    garage = next(p for p in paquet["economie"]["proprietes"] if p["slug"] == "garage")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        L.B.partie.argent = 2 * %d;
        const porte = c.portes.find(function (p) { return p.lieu === 'garage'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // ⚠️ On regarde la porte : dehors, ENTRER n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        o.char('auto', 20, 0, 0);
        o.tape('KeyE', 1);
        o.fondu();
        const point = L.B.interieur.points.find(function (p) { return p.type === 'vendre'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        // Et le comptoir aussi : on le regarde (il est au-dessus du joueur).
        L.Entites.regarder(j, 0, -1);
        o.tape('KeyE', 2);
        const menu = L.B.menu ? L.B.menu.items.map(function (i) { return i.libelle; }) : null;
        const choisi = L.B.menu ? L.B.menu.items[L.B.menu.curseur].libelle : null;
        const avant = L.B.partie.argent;
        o.tape('KeyE', 2);
        return { dedans: L.B.interieur.slug, menu: menu, choisi: choisi,
                 a_soi: !!L.B.partie.proprietes.garage, depense: avant - L.B.partie.argent };
    }""" % garage["prix"])
    assert r["dedans"] == "garage"
    assert r["menu"] and r["menu"][-1] == "ACHETER LE COMMERCE", r["menu"]
    assert r["choisi"].startswith("VENDRE"), r["choisi"]
    assert r["a_soi"] is False, "deux pressions au comptoir ont achete le garage"
    assert r["depense"] <= 0


@pytest.mark.parametrize("a_soi", [False, True], ids=["a_vendre", "a_soi"])
def test_devant_le_garage_la_porte_gagne_sur_le_char_gare_devant(banc, a_soi):
    """Bug de Martin : devant le garage, un char gare devant la porte, et
    « ENTRER » faisait monter dans le char au lieu d'entrer dans le batiment.

    Une seule pression d'ACTION, deux lecteurs dans la meme image :
    `Combat.maj` passe la porte, puis `Vehicules.maj` relisait la meme
    pression et prenait la portiere d'a cote — on se reveillait dans la piece
    au volant. A vendre ou a soi, la porte ne demande rien : elle s'ouvre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'garage'; });
        if (%s) L.B.partie.proprietes.garage = { jour: L.B.partie.jour, caisse: 0 };
        L.B.partie.argent = 99999;             // de quoi acheter : la porte ne doit pas le proposer
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // ⚠️ On regarde la porte : dehors, ENTRER n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        // ⚠️ Le char est DANS LE REGARD, a cote de la porte : depuis que ACTION n'agit que
        // sur ce qu'on regarde, un char a l'est de quelqu'un qui regarde la porte au nord
        // n'etait plus a portee de rien — et la course entre les deux lecteurs ne se jouait plus.
        const v = o.char('auto', 12, -12, 0);  // gare devant, a portee de portiere
        const pres = L.Vehicules.vehiculeSousLaMain(j) === v, devant = L.Monde.porteDevant(j) === porte;
        o.tape('KeyE', 1);                     // UNE pression
        const fondu = !!L.B.transition, menu = !!L.B.menu, auVolant = !!j.dansVehicule;
        o.fondu();
        return { pres: pres, devant: devant, fondu: fondu, menu: menu, auVolant: auVolant,
                 dedans: L.B.interieur ? L.B.interieur.slug : null, attendu: porte.interieur,
                 encoreAuVolant: !!j.dansVehicule, conducteur: v.conducteur === j };
    }""" % ("true" if a_soi else "false"))
    assert r["pres"] is True and r["devant"] is True, "le decor du test : un char a portee ET la porte devant"
    assert r["menu"] is False and r["fondu"] is True, "la porte d'un commerce ouvre un menu au lieu de s'ouvrir"
    assert r["auVolant"] is False, "la meme pression d'ACTION a passe la porte ET pris la portiere"
    assert r["dedans"] == r["attendu"], "ENTRER n'a pas mene dans le garage"
    assert r["encoreAuVolant"] is False and r["conducteur"] is False


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


def test_le_journal_du_matin_raconte_hier_et_enseigne_les_matins_calmes(banc, paquet):
    """⚠️ Le repli « rien à signaler » ENSEIGNE maintenant une chose.

    Le jeu a des boulots au klaxon, une fourrière, un marché noir, des
    propriétés — et rien n'expliquait rien : M1 apprend à marcher et à voler un
    char, après quoi le joueur est tout seul. Un matin où il ne s'est rien passé
    est exactement la place libre, et elle ne coûte pas une fenêtre de plus.

    Le juge tient les trois règles qui comptent : **on enseigne ce qu'il n'a pas
    fait**, **jamais deux fois la même**, et quand il n'y a plus rien à
    apprendre le repli **redevient** « rien à signaler » — ce qui est une bonne
    nouvelle, pas une panne."""
    lecons = paquet["journal_lecons"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        // 1. Un matin calme : il enseigne.
        p.stats.tues = 0;
        L.Missions.nouveauJour();
        const premiere = L.B.dialogue ? L.B.dialogue.lignes[0] : null;
        L.B.dialogue = null;
        // 2. Jamais deux fois la meme : le lendemain, une autre.
        const lues = [];
        for (let jour = 0; jour < 4; jour++) {
            L.Missions.nouveauJour();
            lues.push(L.B.dialogue ? L.B.dialogue.lignes[1] : null);
            L.B.dialogue = null;
        }
        // 3. ⚠️ On n'enseigne QUE ce qu'il n'a pas fait : on remet a zero les
        //    lecons lues, mais on declare avoir tout fait.
        for (const l of (L.B.defs.journal_lecons || [])) p.stats[l.cle] = 9;
        // ⚠️ UN JOUR POUR RIEN D'ABORD : `nouveauJour` compare a HIER, et l'on
        // vient de faire neuf courses d'un coup — ce qui est une manchette, pas
        // un matin calme. Ce premier passage absorbe l'ecart ; le suivant est
        // le vrai matin calme de quelqu'un qui sait deja tout.
        L.Missions.nouveauJour();
        L.B.dialogue = null;
        p.leconsLues = [];
        L.Missions.nouveauJour();
        const toutSu = L.B.dialogue ? L.B.dialogue.lignes[0] : null;
        L.B.dialogue = null;
        // 4. Et le sang passe AVANT la lecon : une manchette est une manchette.
        p.stats.tues = 2;
        L.Missions.nouveauJour();
        const sang = L.B.dialogue ? L.B.dialogue.lignes[0] : null;
        return { premiere: premiere, lues: lues, toutSu: toutSu, sang: sang,
                 qui: L.B.dialogue.qui };
    }""")
    assert r["qui"] == "LE CLAIRON DE LA BAIE"
    assert r["premiere"] == "LE SAVIEZ-VOUS?", (
        "un matin calme n'enseigne rien : %s" % r["premiere"]
    )
    # ⚠️ Jamais deux fois la même — et c'est la règle qui manquait partout
    # ailleurs dans ce dépôt, répliques des passants comprises.
    dites = [x for x in r["lues"] if x]
    assert len(dites) == len(set(dites)), "le journal enseigne deux fois la même chose : %s" % dites
    assert len(dites) >= 3, "le journal cesse d'enseigner après deux jours : %s" % dites
    # ⚠️ Tout su : le repli ne reprend plus « Brume sur le bassin » a l'infini,
    # il VARIE entre les matins calmes — la bonne nouvelle reste la meme, un
    # matin ou rien n'arrive, mais il ne se lit plus mot pour mot pareil.
    matins = {m["titre"] for m in paquet["journal_matins"]}
    assert r["toutSu"] in matins, (
        "il enseigne encore, ou le matin calme ne varie pas : %s" % r["toutSu"]
    )
    assert r["sang"] == "UN MORT DANS LA RUE", "une leçon passe avant un mort : %s" % r["sang"]
    # Les leçons retenues grandissent pendant les quatre premiers jours : les
    # leçons distinctes ci-dessus le prouvent, encore faut-il qu'il y en ait.
    assert len(lecons) >= 4, "moins de quatre leçons : le journal a vite fini d'enseigner"


def test_les_matins_calmes_ne_se_redisent_pas_deux_fois_de_suite(banc, paquet):
    """⚠️ « Brume sur le bassin » était le SEUL matin normal, et un joueur qui
    avait tout appris le lisait mot pour mot chaque jour. Les matins calmes
    (`journal_matins`) VARIENT, tirés dans le dé du jeu sans jamais redire le
    précédent — la même règle que les répliques de la rue, et reproductible
    parce que le tirage passe par `B.rng()`."""
    matins = [m["slug"] for m in paquet["journal_matins"]]
    assert len(matins) >= 2, "moins de deux matins calmes : rien à faire varier"
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        // Tout su : on enseigne a personne, il ne reste que les matins calmes.
        for (const l of (L.B.defs.journal_lecons || [])) p.stats[l.cle] = 9;
        // ⚠️ On rebase le journal d'hier sur les stats d'AUJOURD'HUI : sinon
        // `courses = 9` ferait une manchette (le taxi qui ne dort pas, min 3),
        // pas un matin calme. Le delta doit etre zero pour ne rien signaler.
        p.journal = { crimes: p.stats.crimes || 0, tues: p.stats.tues || 0, volees: p.stats.volees || 0,
                      courses: p.stats.courses || 0, hospitalisations: p.stats.hospitalisations || 0 };
        const titres = [];
        for (let jour = 0; jour < 8; jour++) {
            L.Missions.nouveauJour();
            const m = p.derniereManchette;
            titres.push(m ? m.slug : null);
            const s = p.stats;
            p.journal = { crimes: s.crimes || 0, tues: s.tues || 0, volees: s.volees || 0,
                          courses: s.courses || 0, hospitalisations: s.hospitalisations || 0,
                          matin: m ? m.slug : null };
        }
        return { titres: titres, lues: L.B.dialogue ? L.B.dialogue.lignes[0] : null };
    }""")
    titres = r["titres"]
    # Chaque matin tire est bien un matin calme, jamais une manchette ni lecon.
    assert all(t in matins for t in titres), f"pas des matins calmes : {titres}"
    # Jamais deux fois de suite le meme.
    for a, b in zip(titres, titres[1:]):
        assert a != b, f"deux matins calmes identiques de suite : {titres}"
    # Et le bassin est assez large pour qu'on en voie plus d'un sur huit jours.
    assert len(set(titres)) >= 2, f"les matins ne varient pas : {titres}"
