"""Se battre, sous Node : mêlée, couteau, sang, pickpocket, pistolet, budget de la
bagarre, armes de fortune, gestes du coup, poing américain.

Découpé de `test_moteur_js.py` (vague D, 29 sept. 2026) : même banc, mêmes juges.
"""


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
            // ⚠️ **LA RUE SE VIDE AVANT CHAQUE MANCHE.** Un coup touche TOUT ce
            // qui est à portée : un passant de plus à côté de la cible, et le
            // couteau en tue deux (17 sept. 2026, la trame a bougé et le juge
            // comptait deux morts pour un). On ne juge que le corps qu'on frappe.
            for (const q of L.B.entites.slice()) {
                if (q === L.B.joueur || q.type === 'joueur') continue;
                if (q.type === 'pieton' || q.type === 'vehicule') L.Entites.retirer(q);
            }
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
        const americain = cogner('poing_americain', 'ouvrier');
        const lame = cogner('couteau', 'passante');
        return { poing: poing, americain: americain, lame: lame, tues: L.B.partie.stats.tues,
                 decals: L.B.decals.length, sang: L.B.options.sang };
    }""")
    assert r["poing"]["vivant"] is True and r["poing"]["etat"] == "assomme", \
        "les poings doivent assommer, pas tuer — c'est ce qui separe 1 etoile de 3"
    assert r["americain"]["vivant"] is True and r["americain"]["etat"] == "assomme", \
        "le poing americain est un poing plus lourd : il assomme aussi (%s)" % r["americain"]
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
        // ⚠️ **RIEN D'AUTRE SOUS LA MAIN.** ACTION sert le premier venu — une
        // porte, un personnage, un comptoir — et l'arme au sol passe après (voir
        // `Missions.interagir`). Le 17 sept. 2026, la trame a bougé, le terminus
        // a changé de voisinage, et le E ramassait autre chose. On s'écarte de la
        // porte et on vide les alentours : ce juge parle de l'arme du mort.
        const j0 = L.B.joueur;
        j0.y += 40;
        for (const q of L.B.entites.slice()) {
            if (q === j0 || q.type === 'joueur') continue;
            if (q.type === 'pieton' || q.type === 'vehicule' || q.type === 'ramassage') L.Entites.retirer(q);
        }
        L.Entites.indexer();
        const cravate = o.poser('cravate', 14, 0);
        const armeDeLaCravate = cravate.arme;
        L.Entites.tuer(cravate, L.B.joueur);
        L.Entites.indexer();
        // ⚠️ On regarde l'arme : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(L.B.joueur, 1, 0);
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
        // ⚠️ **LA RUE SE VIDE** : `pickpocket` sert le plus commode, pas celui
        // qu'on vise, et un passant de dos à côté de la dame suffit à faire dire
        // « oui » au juge qui attendait « non » (17 sept. 2026, la trame a bougé).
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        L.Entites.indexer();
        const face = o.poser('dame', 14, 0);
        face.argent = 40;
        // ⚠️ Le joueur, lui, regarde la dame : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 1, 0);
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
        // ⚠️ **ET LA BALLE A BESOIN DE QUATRE-VINGT-DIX PIXELS DE RUE.** Au
        // terminus, le jour où la trame a bougé (17 sept. 2026), un mur se
        // trouvait entre le canon et la cible : la balle s'arrêtait dessus et le
        // juge lisait « la balle n'a pas touché ». Le boulevard du nord est droit.
        const c0 = L.Monde.carte;
        for (let y = 0; y < 12; y++) {
          let pris = false;
          for (let x = 40; x < 80; x++) if (c0.voie[y][x] === '>') {
            j.x = x * L.TT + 8; j.y = y * L.TT + 8; L.Monde.centrerCamera(j.x, j.y); pris = true; break;
          }
          if (pris) break;
        }
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


def test_la_bagarre_tient_le_budget(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(13);
        o.singe(2500, 3, ['KeyW', 'KeyA', 'KeyS', 'KeyD', 'Space', 'ShiftLeft', 'KeyE', 'Tab']);
        const s = L.B.stats;
        // ⚠️ `vivant` : un CADAVRE n'est pas un flaneur. `peupler()` compte
        // « e.vivant && !e.metier » — c'est SA definition du budget, et c'est
        // elle qu'on juge. Un corps laisse par terre par le singe faisait
        // compter vingt-neuf personnes pour vingt-huit vivantes : le moteur
        // tenait son budget et le juge accusait un emballement.
        let flaneurs = 0, metiers = 0, morts = 0;
        const histoire = {};
        for (const e of L.B.entites) {
            if (e.type === 'pieton' && e.actif && e.vivant && e.metier === 'histoire') histoire[e.personnage] = (histoire[e.personnage] || 0) + 1;
            if (e.type !== 'pieton' || !e.actif) continue;
            if (!e.vivant) { morts++; continue; }
            // ⚠️ Le PETIT QUI SUIT SA MERE nait avec elle : le budget se decide a la
            // naissance (`peupler`), et une mere nee a vingt-sept flaneurs en fait
            // vingt-neuf. Le juge tenait tant que la graine ne faisait pas naitre de
            // paire au bord du budget (21 sept. 2026, graine 13).
            if (e.suit) continue;
            if (e.metier || e.personnage) metiers++; else flaneurs++;
        }
        return { etat: L.B.etat, entites: L.B.entites.length, actifs: s.actifs,
                 flaneurs: flaneurs, metiers: metiers, morts: morts,
                 budget: L.Entites.MAX_PIETONS,
                 vendeurs: (L.Monde.carte.def.ambulants || []).length,
                 histoire: histoire,
                 particules: L.B.particules.length, decals: L.B.decals.length,
                 images: s.images, morceaux: s.morceaux,
                 nan: isNaN(L.B.joueur.x) || isNaN(L.B.joueur.y) };
    }""")
    assert r["etat"] in ("jeu", "pause")
    assert not r["nan"]
    # ⚠️ LE BUDGET, C'EST CELUI DES FLANEURS, et il vaut `MAX_PIETONS` : c'est
    # le seul nombre que `peupler()` tienne. Le reste de la figuration ne se
    # regule pas par la foule — les douze vendeurs des kiosques de la ville
    # naissent avec elle et ne dorment jamais, les amuseurs, les trois
    # personnages de l'histoire et les agents de patrouille s'ajoutent
    # par-dessus. Le juge disait `actifs <= 30` : arithmetiquement intenable
    # (22 + 12 font deja 34), il ne tenait que tant que le singe ne traversait
    # pas un quartier dense, et il est tombe le jour ou la ville a bouge d'une
    # tuile. On mesure donc les deux separement, et on garde un plafond sur le
    # total pour attraper un emballement.
    #
    # ⚠️ ET LE CHIFFRE SE LIT DANS LE MOTEUR, il ne se recopie pas ici. Il
    # etait ecrit « 22 » en dur : le jour ou le centre-ville a demande plus de
    # monde (demande de Martin) et ou `MAX_PIETONS` est passe a 28, le juge
    # n'a pas dit « le budget a change », il a dit « emballement ». Un plafond
    # recopie dans un juge finit toujours par juger l'ancien.
    assert r["flaneurs"] <= r["budget"], (
        f"{r['flaneurs']} flaneurs vivants, le budget est de {r['budget']} "
        f"({r['morts']} corps par terre, qui ne comptent pas)"
    )
    # ⚠️ **LES VENDEURS SE LISENT DANS LA CARTE, EUX AUSSI.** Chaque kiosque et
    # chaque camion fait naitre UN vendeur fixe pour toute la partie
    # (`creerAmbulants`) — douze quand ce plafond a ete ecrit, treize depuis le
    # quai du contrebandier. Le « +28 » les rangeait dedans, c'est-a-dire qu'il
    # recopiait un nombre du moteur, exactement ce que la note du dessus
    # interdit. Il est tombe le 16 sept. 2026 sans qu'aucun budget ait bouge :
    # a HEAD, le singe finissait COINCE dans un coin vide de la carte (10, 1),
    # avec un seul pieton a metier autour de lui ; apres le changement du port,
    # sa marche au hasard l'a mene au centre-ville (146, 6) — treize vendeurs,
    # une bagarre de quatre, les trois personnages de l'histoire, deux agents.
    # Le plafond ne tenait que tant que le singe ne voyait personne.
    # ⚠️ **ET LES PERSONNAGES DE L'HISTOIRE AUSSI.** Posés dehors devant leur porte, ils ne
    # dorment jamais, comme les vendeurs : « les trois personnages de l'histoire » quand le
    # « +28 » a été écrit, seize depuis les donneurs de M16 — et le juge a crié à
    # l'emballement (72 pour 69, 25 sept. 2026) sans qu'un seul budget ait bougé. On les
    # compte — et les trois du « +28 » en sortent (+25) : le juge ne se relâche pas d'une
    # personne. Le vrai garde-fou est ailleurs : un personnage n'est jamais posé DEUX fois.
    doubles = {qui: n for qui, n in r["histoire"].items() if n > 1}
    assert not doubles, f"des personnages posés plusieurs fois : {doubles}"
    personnages = sum(r["histoire"].values())
    assert r["actifs"] <= r["budget"] + r["vendeurs"] + personnages + 25, (
        f"{r['actifs']} pietons actifs ({r['metiers']} a un metier, "
        f"dont {r['vendeurs']} vendeurs fixes et {personnages} personnages de l'histoire)"
    )
    assert r["particules"] <= 300 and r["decals"] <= 150
    assert r["images"] <= 160, f"{r['images']} drawImage par image"


def test_des_armes_de_fortune_trainent_en_ville(banc, paquet):
    """⚠️ La casse (une arme de fortune qui lâche après `usures` coups, et on
    retombe aux poings) se juge dans `test_armes_js::test_une_arme_de_fortune_casse_en_le_disant`,
    au coup près et avec son bruit (vague C, 28 sept. 2026). Ici : elles traînent
    bel et bien dans la rue, et ce ne sont que des armes de fortune."""
    fortunes = {a["slug"] for a in paquet["armes"] if a["usures"] > 0 and a["prix"] == 0}
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(900);
        const objets = L.B.entites.filter(function (e) { return e.type === 'ramassage'; });
        return { objets: objets.length, armes: objets.map(function (e) { return e.arme; }) };
    }""")
    assert r["objets"] > 0, "aucune arme de fortune ne traine dans la rue"
    assert set(r["armes"]) <= fortunes, r["armes"]


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


def test_le_poing_americain_se_tient_en_bout_de_poing_et_se_ramasse_en_arme(banc):
    """Martin : « l'arme poing americain devrait etre seulement un tip gris au
    bout des poings, mais quelque chose de plus gros a ramasser ».

    ⚠️ Un seul dessin servait aux deux : tenu, le 12 x 6 du sol depassait du
    poing comme une planche, aussi large que le torse ; par terre, gris sans
    contour, il se perdait dans le gris du trottoir. On juge ce que le VRAI
    dessin des entites cuit pour l'arme (`Entites.dessiner`), pas le catalogue
    des peintres : c'est ce chemin qui choisissait le mauvais."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, E = L.Entites;
        // Le banc ne garde aucun pixel : chaque peintre d'arme repasse sur un
        // canevas qui note ses traits, et on en garde la boite et le plus sombre.
        const cuites = [];
        const cuire = L.Atlas.cuirePeintre;
        L.Atlas.cuirePeintre = function (cle, w, h, peintre) {
            if (/^(objet|main)[|]/.test(cle)) {
                const traits = [];
                const t = { fillStyle: '', clearRect: function () {},
                            fillRect: function (x, y, lw, lh) { if (lw > 0 && lh > 0) traits.push([x, y, lw, lh, String(t.fillStyle)]); } };
                peintre(t, w, h);
                const c = { cle: cle, x0: w, y0: h, x1: -1, y1: -1, sombre: 1 };
                traits.forEach(function (r) {
                    c.x0 = Math.min(c.x0, r[0]); c.y0 = Math.min(c.y0, r[1]);
                    c.x1 = Math.max(c.x1, r[0] + r[2] - 1); c.y1 = Math.max(c.y1, r[1] + r[3] - 1);
                    const v = parseInt(r[4].slice(1), 16);
                    c.sombre = Math.min(c.sombre, (0.299 * (v >> 16 & 255) + 0.587 * (v >> 8 & 255) + 0.114 * (v & 255)) / 255);
                });
                cuites.push(c);
            }
            return cuire.call(this, cle, w, h, peintre);
        };
        function dessin(prep) {
            cuites.length = 0;
            const garde = B.entites;
            B.entites = [j];
            j.x = 3000; j.y = 3000; j.vx = 0; j.vy = 0; j.invincible = 0;
            prep();
            E.dessiner(o.ctx, { x: j.x - L.VW / 2, y: j.y - L.VH / 2 });
            B.entites = garde;
            return cuites.slice();
        }
        B.partie.armes.poing_americain = { mun: null, usure: 0 };
        B.partie.armes.batte = { mun: null, usure: 0 };
        const coup = dessin(function () { j.arme = 'poing_americain'; j.face = 'droite'; j.angle = 0; j.etat = 'attaque'; j.phase = 'actif'; });
        const repos = dessin(function () { j.arme = 'poing_americain'; j.face = 'bas'; j.etat = 'flane'; j.phase = null; });
        const batte = dessin(function () { j.arme = 'batte'; j.face = 'droite'; j.etat = 'attaque'; j.phase = 'actif'; });
        const sol = dessin(function () {
            j.arme = null; j.etat = 'flane'; j.phase = null;
            E.creer('ramassage', j.x + 20, j.y, { r: 4, objet: 'arme', arme: 'poing_americain', munitions: null, t: 0, solide: false });
        });
        return { coup: coup, repos: repos, batte: batte, sol: sol };
    }""")
    for moment in ("coup", "repos"):
        tenu = r[moment]
        assert [c["cle"] for c in tenu] == ["main|poing_americain"], (
            "au %s, la main tient le dessin du sol : %s" % (moment, tenu))
        c = tenu[0]
        assert c["x1"] - c["x0"] + 1 <= 2 and c["y1"] - c["y0"] + 1 <= 3, "un bout, pas une planche : %s" % c
        # La prise est le pixel (2, 5) de la toile (`dessinerArme`) : le bout
        # couvre la main, il ne flotte pas devant.
        assert c["x0"] <= 2 <= c["x1"] and c["y0"] <= 5 <= c["y1"], "le bout n'est pas sur le poing : %s" % c
    assert [c["cle"] for c in r["batte"]] == ["objet|batte"], "les autres armes se tiennent comme elles se ramassent"
    assert [c["cle"] for c in r["sol"]] == ["objet|poing_americain"], r["sol"]
    sol = r["sol"][0]
    assert sol["x1"] - sol["x0"] + 1 >= 13 and sol["y1"] - sol["y0"] + 1 >= 6, "par terre, une vraie arme : %s" % sol
    # ⚠️ Le trottoir est gris (#8f8c86), l'acier aussi : sans un trait sombre,
    # l'arme tombee ne se voit pas.
    assert sol["sombre"] < 0.25, "par terre, l'acier se perd dans le trottoir : %s" % sol


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


def test_le_joueur_touche_chancelle_puis_se_redresse(banc):
    """Martin : « regarde pourquoi mon personnage est croche. » `blesser` pose un
    `recul` (8 images, 22 si on est renverse) et seule la mise a jour des
    PIETONS le decomptait : le joueur restait penche de 0,22 rad, du cote de sa
    marche, jusqu'a la fin de la partie — au premier coup recu."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(81);
        const j = L.B.joueur;
        const lu = function () { return { recul: j.recul, rot: L.Entites.pose(j).rot }; };
        const avant = lu();
        L.Entites.blesser(j, 1, null, {});
        const petit = lu();
        o.frame(12);
        const petitApres = lu();
        L.Entites.blesser(j, 1, null, { renverse: true });
        const gros = lu();
        o.frame(30);
        const grosApres = lu();
        return { avant: avant, petit: petit, petitApres: petitApres, gros: gros, grosApres: grosApres };
    }""")
    assert r["avant"]["rot"] == 0, r
    assert r["petit"]["rot"] != 0 and r["gros"]["rot"] != 0, "le coup fait chanceler : %s" % r
    assert r["petitApres"] == {"recul": 0, "rot": 0}, "le petit coup est oublie en 12 images : %s" % r
    assert r["grosApres"] == {"recul": 0, "rot": 0}, "le corps renverse se redresse en 30 images : %s" % r
