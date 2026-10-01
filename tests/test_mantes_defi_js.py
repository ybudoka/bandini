"""Les Mantes provoquent, au banc (docs/jalons/les-mantes-provoquent-et-le-petit-canton-a-sa-musique.md).

Martin (29 sept. 2026) : sur LEUR territoire, un Mante qui te voit de près vient te défier même à mains nues, une
réplique en bulle ; hors de leur territoire, ils font comme les autres gangs. Les juges de la fiche : un joueur qui
TRAVERSE le territoire se fait défier ; hors du territoire, non ; les Cravates d'à côté n'ont pas changé. Et ce qui
rend ça juste, un garde-fou à la fois (`Entites.defier`), sans un dé.

⚠️ La rue est vidée et le trafic coupé : un passant de plus ou un char qui passe changeraient ce qu'on mesure. Les
rangées viennent de la carte (mesurées le 29 sept. 2026) : la rangée 17 est un trottoir continu de la colonne 100 à
268 — elle traverse le territoire des Mantes (colonnes 148 à 189, rangées 0 à 31) d'ouest en est ; la rangée 47 est au
Petit-Canton, sous leur territoire ; la rangée 180, dans la cour des Cravates.
"""

import pytest

from app import mantes

#: Une partie, la rue vide, le joueur posé sur la tuile (tx, ty), mains nues.
PREPARER = """
    function preparer(L, tx, ty) {
        L.Jeu.commencer();
        L.B.defs.conduite.trafic.vehicules_max = 0;
        for (let i = L.B.entites.length - 1; i >= 0; i--) {
            const q = L.B.entites[i];
            if (q.type === 'pieton' || q.type === 'vehicule') L.Entites.retirer(q);
        }
        const j = L.B.joueur;
        j.x = tx * L.TT + 8; j.y = ty * L.TT + 8; j.arme = 'poings';
        L.Monde.centrerCamera(j.x, j.y);
        L.Entites.indexer();
        return j;
    }
    // Un homme de `arch` a (dx, dy) du joueur, qui flane.
    function flaneur(o, arch, dx, dy) { const e = o.poser(arch, dx, dy); e.etat = 'flane'; return e; }
    // Le joueur marche vers l'est (ESQUIVE jamais, FRAPPE jamais) ; on note ce que font les autres. `avantImage`,
    // s'il est donne, passe avant chaque image.
    function marcher(L, o, gens, images, avantImage) {
        const j = L.B.joueur, defis = [], proche = { d: 1e9 };
        const avant = gens.map(function (e) { return e.etat; });
        o.touche('KeyD');
        for (let t = 0; t < images; t++) {
            if (avantImage) avantImage(t);
            o.frame(1);
            gens.forEach(function (e, i) {
                proche.d = Math.min(proche.d, Math.hypot(e.x - j.x, e.y - j.y));
                if (e.etat === 'attaque_joueur' && avant[i] !== 'attaque_joueur') {
                    defis.push({ t: t, qui: i, bulle: e.bulle && e.bulle.texte, salut: e.salut,
                                 d: Math.round(Math.hypot(e.x - j.x, e.y - j.y)),
                                 tuile: [Math.floor(j.x / L.TT), Math.floor(j.y / L.TT)],
                                 chez: L.Territoires.gangA(j.x, j.y) });
                }
                avant[i] = e.etat;
            });
            if (defis.length === 1 && defis[0].immobile === undefined) defis[0].immobile = 0;
            if (defis.length && defis[0].t < t && gens[defis[0].qui].vx === 0 && gens[defis[0].qui].vy === 0
                && gens[defis[0].qui].salut > 0) defis[0].immobile++;
        }
        o.relacher('KeyD');
        return { defis: defis, proche: Math.round(proche.d), x: Math.floor(j.x / L.TT) };
    }
"""


def test_un_joueur_qui_traverse_leur_territoire_se_fait_defier(banc):
    """Le juge de la fiche. Mains nues, le joueur marche d'ouest en est sur la rangée 17, d'avant leur territoire
    jusqu'à la rue principale ; deux Mantes flânent au milieu. Le premier qui le voit de près s'arrête, se tourne,
    dit sa réplique en bulle (`salut`), puis attaque — et UN seul : l'autre regarde le film."""
    r = banc("""function (L, o) {
        %s
        const j = preparer(L, 136, 17);
        const a = flaneur(o, 'mante', 20 * 16, -16), b = flaneur(o, 'mante', 28 * 16, 16);
        const out = marcher(L, o, [a, b], 900);
        out.defiees = [a, b].filter(function (e) { return e.defie; }).length;
        return out;
    }""" % PREPARER)
    assert r["defis"], f"personne n'a défié le joueur qui traversait : {r}"
    d = r["defis"][0]
    assert d["chez"] == "mantes" and 148 <= d["tuile"][0] < 190, f"défié hors de leur territoire : {r}"
    assert d["bulle"] in mantes.PROVOCATION["repliques"], r
    assert d["d"] <= mantes.PROVOCATION["portee_px"], r
    assert d["salut"] == mantes.PROVOCATION["salut_images"], r
    assert d["immobile"] >= mantes.PROVOCATION["salut_images"] - 5, f"il n'a pas pris la pose : {r}"
    assert len(r["defis"]) == 1 and r["defiees"] == 1, f"deux défis coup sur coup : {r}"


def test_un_mante_arrete_devant_une_vitrine_te_voit_passer_quand_meme(banc):
    """⚠️ Vu au banc : le premier Mante croisé était `arret` (une pause devant une vitrine), et l'`arret` sort avant la
    règle de l'arme au poing — il a laissé passer le joueur à un pas. Planté là pour de bon, il défie quand même."""
    r = banc("""function (L, o) {
        %s
        preparer(L, 136, 17);
        const a = flaneur(o, 'mante', 20 * 16, -16);
        a.etat = 'arret'; a.minuterie = 5000;
        const out = marcher(L, o, [a], 500);
        out.arret = a.minuterie > 4000;
        return out;
    }""" % PREPARER)
    assert r["arret"], r
    assert len(r["defis"]) == 1 and r["defis"][0]["bulle"] in mantes.PROVOCATION["repliques"], r


def test_hors_de_leur_territoire_un_mante_ne_defie_pas_mains_nues(banc):
    """Le témoin : la même marche, les mêmes deux Mantes à côté — mais sur la rangée 47, au Petit-Canton sous leur
    territoire. Mains nues, ils font comme les autres gangs : rien."""
    r = banc("""function (L, o) {
        %s
        preparer(L, 136, 47);
        const a = flaneur(o, 'mante', 20 * 16, -16), b = flaneur(o, 'mante', 28 * 16, 16);
        return marcher(L, o, [a, b], 900);
    }""" % PREPARER)
    assert r["proche"] <= mantes.PROVOCATION["portee_px"], f"le joueur n'est jamais passé près d'eux : {r}"
    assert r["defis"] == [], r


@pytest.mark.parametrize("arme", ["poings", "batte"])
def test_les_cravates_n_ont_pas_change(banc, arme):
    """Chez elles, dans leur cour : à mains nues, les Cravates laissent passer ; l'arme au poing, elles attaquent —
    comme avant, et sans bulle de défi."""
    r = banc("""function (L, o) {
        %s
        const j = preparer(L, 196, 180);
        j.arme = 'ARME';
        const a = flaneur(o, 'cravate', 10 * 16, -16), b = flaneur(o, 'cravate', 20 * 16, 16);
        // ⚠️ DEUX FLÂNEURS QUI FLÂNENT (1er oct. 2026) : la rue vidée, ce sont les deux seuls qu'on peut tirer pour
        // rentrer souper (`quelquUnRentre`) ou s'arrêter devant une vitrine — et en route vers sa porte, ou arrêté, un
        // Cravate ne prend plus l'arme au poing pour une provocation. Le témoin tombait sur 2 graines sur 13 le 30 sept.
        // (d34eff4b), sur 5 le 1er oct. — la graine par défaut comprise depuis les braseros de l'hiver (253f58e3).
        // Il ne juge que la provocation : 13 sur 13 des deux côtés.
        a.butT = b.butT = 1e9;
        const out = marcher(L, o, [a, b], 420, function () { a.porteBut = null; b.porteBut = null; });
        out.gang = a.gang;
        out.chez = L.Territoires.gangA(a.x, a.y);
        return out;
    }""".replace("ARME", arme) % PREPARER)
    assert r["gang"] == "cravates", r
    assert r["proche"] <= 6 * 16, r
    if arme == "poings":
        assert r["defis"] == [], r
    else:
        assert r["defis"], f"le témoin ne mord pas : l'arme au poing chez les Cravates n'a rien fait : {r}"
        assert all(d.get("bulle") not in mantes.PROVOCATION["repliques"] for d in r["defis"]), r


def test_pas_au_moment_ou_l_on_sort_de_l_ecole(banc):
    """On sort de l'ÉCOLE LA MANTE, un Mante flâne à deux pas de la porte : il laisse le temps de voir où l'on est
    (`sortie_images`), puis il vient."""
    r = banc("""function (L, o) {
        %s
        preparer(L, 136, 17);
        const porte = L.Monde.carte.def.portes.find(function (p) { return p.interieur === 'ecole_mante'; });
        const j = L.B.joueur, TT = L.TT;
        j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        o.entrer(porte);
        const dedans = L.B.interieur && L.B.interieur.slug;
        o.sortir();
        const m = flaneur(o, 'mante', 24, 8);
        let defi = null;
        for (let t = 0; t < 700 && defi === null; t++) {
            o.frame(1);
            if (m.etat === 'attaque_joueur') defi = t;
            m.x = j.x + 24; m.y = j.y + 8;        // il reste a deux pas : on ne mesure que l'attente
        }
        return { dedans: dedans, defi: defi, chez: L.Territoires.gangA(j.x, j.y) };
    }""" % PREPARER)
    assert r["dedans"] == "ecole_mante" and r["chez"] == "mantes", r
    assert r["defi"] is not None, f"personne ne l'a défié, même après : {r}"
    assert r["defi"] >= mantes.PROVOCATION["sortie_images"] - 20, f"défié sur le pas de la porte : {r}"


def test_les_garde_fous_un_a_un_et_sans_un_de(banc):
    """`Entites.defier`, garde-fou par garde-fou : un Mante à deux tuiles, chez lui, le joueur mains nues. Chaque
    garde refuse seule ; la première fois qu'on les lève toutes, il défie. Puis : un défi à la fois, le délai avant
    le deuxième, un Mante ne défie qu'une fois — et pas un seul `B.rng()` dans tout ça."""
    r = banc("""function (L, o) {
        %s
        const j = preparer(L, 160, 17), B = L.B, E = L.Entites, etat0 = j.etat;
        // ⚠️ Poses AVANT l'espion : `creerPieton` tire ses des, le defi non.
        const m = flaneur(o, 'mante', 32, 0), n = flaneur(o, 'mante', -32, 0), p = flaneur(o, 'mante', 0, 24);
        let des = 0;
        const rng = B.rng;
        B.rng = function () { des++; return rng.apply(this, arguments); };
        const garde = function (nom, poser, lever) { poser(); const v = E.defier(m); lever(); return [nom, v]; };
        const refus = [
            garde('dedans', function () { B.interieur = { slug: 'x' }; }, function () { B.interieur = null; }),
            garde('sortie', function () { j.sortiA = B.t - 10; }, function () { delete j.sortiA; }),
            garde('a_terre', function () { j.auSol = 30; }, function () { j.auSol = 0; }),
            garde('assomme', function () { j.etat = 'assomme'; }, function () { j.etat = etat0; }),
            garde('en_l_air', function () { j.vol = { t: 0 }; }, function () { j.vol = null; }),
            garde('tenu', function () { j.saisiPar = n; }, function () { j.saisiPar = null; }),
            garde('en_char', function () { j.dansVehicule = { id: 1 }; }, function () { j.dansVehicule = null; }),
            garde('arme', function () { j.arme = 'batte'; }, function () { j.arme = 'poings'; }),
            garde('defi', function () { B.defi = { slug: 'x' }; }, function () { B.defi = null; }),
            garde('frenesie', function () { B.frenesie = { slug: 'x' }; }, function () { B.frenesie = null; }),
            garde('mission_sans_eux', function () { B.partie.mission = { slug: 'm2', etape: 0 }; },
                  function () { B.partie.mission = null; }),
            garde('loin', function () { m.x = j.x + 96; }, function () { m.x = j.x + 32; }),
            garde('hors_territoire', function () { j.y += 30 * 16; m.y += 30 * 16; }, function () { j.y -= 30 * 16; m.y -= 30 * 16; }),
        ];
        // Une mission qui LES NOMME (un objectif `groupe: 'mantes'`) : le defi part.
        const courante = L.Histoire.courante;
        B.partie.mission = { slug: 'm2', etape: 0 };
        L.Histoire.courante = function () { return { slug: 'c9', objectifs: [{ type: 'tuer', groupe: 'mantes' }] }; };
        const premier = E.defier(m);
        L.Histoire.courante = courante;
        B.partie.mission = null;
        const bulle = m.bulle && m.bulle.texte, salut = m.salut;
        const delai = B.defs.mantes.provocation.delai_images;
        // Un defi a la fois : le delai passe, m est encore sur le joueur — n regarde le film.
        B.t += delai;
        const pendant = E.defier(n);
        // Le combat fini (m s'en va) : le deuxieme vient.
        m.etat = 'flane';
        const deuxieme = E.defier(n);
        // Le combat fini aussi (n s'en va) : un troisieme attend le delai...
        n.etat = 'flane';
        const tropTot = E.defier(p);
        // ...et chacun ne defie qu'une fois dans sa vie : le delai passe, m ne revient pas, p oui.
        B.t += delai;
        const uneFois = E.defier(m), troisieme = E.defier(p);
        B.rng = rng;
        return { refus: refus, premier: premier, bulle: bulle, salut: salut, pendant: pendant, tropTot: tropTot,
                 deuxieme: deuxieme, uneFois: uneFois, troisieme: troisieme, des: des };
    }""" % PREPARER)
    assert [nom for nom, v in r["refus"] if v] == [], f"un garde-fou laisse passer : {r['refus']}"
    assert r["premier"] is True, f"toutes les gardes levées, il ne défie pas : {r}"
    assert r["bulle"] in mantes.PROVOCATION["repliques"] and r["salut"] == mantes.PROVOCATION["salut_images"], r
    assert r["pendant"] is False, "un deuxième défi pendant que le premier Mante est sur le joueur"
    assert r["tropTot"] is False, "le deuxième n'a pas attendu le délai"
    assert r["deuxieme"] is True, r
    assert r["uneFois"] is False and r["troisieme"] is True, f"un Mante a défié deux fois : {r}"
    assert r["des"] == 0, f"{r['des']} dés tirés par le défi"


def test_les_repliques_tiennent_dans_une_bulle():
    """Une bulle, une ligne : courtes, en majuscules comme toutes les bulles, et jamais deux fois la même."""
    reps = mantes.PROVOCATION["repliques"]
    assert len(reps) == len(set(reps)) >= 6
    for texte in reps:
        assert len(texte) <= 26 and texte == texte.upper(), texte
