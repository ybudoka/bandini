"""On agit sur ce qu'on regarde (20 sept. 2026, demande de Martin) : pour activer
une interaction — une porte, un char, un comptoir, quelqu'un — le personnage
doit FAIRE FACE a ce qu'il veut activer, a moins d'une exception dite.

Un seul calcul, `faceA` (base.js), lu par toutes les fonctions « sous la main » ;
l'invite du HUD lit les memes, donc le bouton ne promet jamais ce qu'il
refuserait. Ces juges disent la regle, puis les portes, les portieres, les gens,
les comptoirs et les deux exceptions : ce qu'on a sous les pieds, et la porte
qu'on a dans le dos en entrant.
"""

import json

# Les quatre regards que le sprite montre, comme un vecteur (dx, dy).
REGARDS = {"haut": (0, -1), "bas": (0, 1), "gauche": (-1, 0), "droite": (1, 0)}


def test_le_cone_couvre_toute_direction_sans_jamais_voir_de_cote(paquet):
    """Les deux chiffres du paquet tiennent la regle : a 45 degres ou plus, chaque
    diagonale est visee d'au moins un regard (aucune direction n'est hors de
    portee) ; sous 90, on ne voit jamais ce qui est sur le cote. Et « sous les
    pieds » ne depasse pas une demi-tuile."""
    regard = paquet["recherche"]["regard"]
    assert 45 <= regard["demi_cone_degres"] < 90, regard
    assert 0 < regard["dessus_px"] <= paquet["tuile_px"] // 2, regard


def test_faire_face_c_est_ce_que_le_sprite_montre(banc, paquet):
    """⚠️ Le regard est l'un des QUATRE dessines, pas l'angle fin du stick : ce
    que le joueur voit est ce que le jeu juge. Chacun couvre +/- `demi_cone`
    autour de lui, donc les diagonales se recouvrent, et le dos ne couvre rien."""
    regard = paquet["recherche"]["regard"]
    r = banc("""function (L, o) {
        const dirs = %(dirs)s, demi = %(demi)s * Math.PI / 180;
        const j = { x: 100, y: 100, angle: 0, face: 'bas' };
        const vise = function (a) { return L.faceA(j, j.x + Math.cos(a) * 20, j.y + Math.sin(a) * 20); };
        const table = {};
        for (const face of Object.keys(dirs)) {
            j.face = face;
            table[face] = {};
            for (const cible of Object.keys(dirs)) table[face][cible] = vise(Math.atan2(dirs[cible][1], dirs[cible][0]));
        }
        // La bordure du cone : un degre en dedans passe, un degre en dehors non.
        j.face = 'droite';
        const bord = { dedans: vise(demi - Math.PI / 180), dehors: vise(demi + Math.PI / 180) };
        // Une diagonale (bas-droite) se vise de deux regards.
        const diagonale = {};
        for (const face of Object.keys(dirs)) { j.face = face; diagonale[face] = vise(Math.PI / 4); }
        // Sous les pieds on n'a pas a regarder — et pas plus loin que `dessus_px`.
        j.face = 'haut';
        const dessus = { pres: L.faceA(j, j.x + 4, j.y + 4), loin: L.faceA(j, j.x + 14, j.y + 14) };
        // Une pose qui n'est pas un regard (couche, assis) : l'angle fin prend le relais.
        const posee = { x: 100, y: 100, face: 'alite', angle: Math.PI };
        const pose = { devant: L.faceA(posee, 60, 100), derriere: L.faceA(posee, 140, 100) };
        return { table: table, bord: bord, diagonale: diagonale, dessus: dessus, pose: pose };
    }""" % {"dirs": json.dumps({k: list(v) for k, v in REGARDS.items()}), "demi": regard["demi_cone_degres"]})
    for face in REGARDS:
        for cible in REGARDS:
            assert r["table"][face][cible] is (face == cible), (
                f"regard {face}, cible {cible} : {r['table'][face][cible]}")
    assert r["bord"] == {"dedans": True, "dehors": False}, r["bord"]
    assert r["diagonale"] == {"haut": False, "gauche": False, "bas": True, "droite": True}, r["diagonale"]
    assert r["dessus"] == {"pres": True, "loin": False}, "sous les pieds, on n'a pas a regarder"
    assert r["pose"] == {"devant": True, "derriere": False}, r["pose"]


def test_une_porte_ne_s_ouvre_que_de_face_et_l_invite_le_dit(banc):
    """Devant une facade : « ENTRER » n'apparait qu'en regardant la porte, et
    ACTION dos tourne ne fait rien. Le meme calcul pour l'invite et pour le
    geste — c'est le but."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'depanneur'; }) || c.portes[0];
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        const dirs = %(dirs)s;
        const vues = {};
        for (const face of Object.keys(dirs)) {
            L.Entites.regarder(j, dirs[face][0], dirs[face][1]);
            L.Missions.majInvite(j);
            vues[face] = { porte: !!L.Monde.porteDevant(j), invite: L.B.invite || null };
        }
        // Le dos tourne : ACTION n'entre pas.
        L.Entites.regarder(j, 0, 1);
        o.tape('KeyE', 2); o.fondu();
        const dos = L.B.interieur !== null;
        // De face : elle entre.
        L.Entites.regarder(j, 0, -1);
        o.tape('KeyE', 2); o.fondu();
        return { vues: vues, dos: dos, deFace: L.B.interieur !== null };
    }""" % {"dirs": json.dumps({k: list(v) for k, v in REGARDS.items()})})
    for face, vue in r["vues"].items():
        assert vue["porte"] is (face == "haut"), f"regard {face} : {vue}"
        assert (vue["invite"] == "ENTRER") is (face == "haut"), f"regard {face} : {vue}"
    assert r["dos"] is False, "ACTION a ouvert une porte qu'on ne regardait pas"
    assert r["deFace"] is True, "ACTION n'a pas ouvert la porte qu'on regardait"


def test_de_l_interieur_la_porte_de_sortie_se_prend_sans_se_retourner(banc):
    """⚠️ L'EXCEPTION DE LA SORTIE. En entrant, on regarde vers le fond de la
    piece : la porte est dans le dos, et c'est le jeu qui nous y a mis. Sortir
    doit rester le geste vif que le bloquant du 13 sept. 2026 a garanti (« chez
    Ti-Paul, il est impossible de sortir ») — pas un demi-tour a deviner."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'depanneur'; }) || c.portes[0];
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const dirs = %(dirs)s;
        const vues = {};
        for (const face of Object.keys(dirs)) {
            L.Entites.regarder(j, dirs[face][0], dirs[face][1]);
            L.Missions.majInvite(j);
            vues[face] = { porte: !!L.Monde.porteDevant(j), invite: L.B.invite || null };
        }
        L.Entites.regarder(j, 0, -1);            // le dos a la porte, comme en entrant
        o.tape('KeyE', 2); o.fondu();
        return { vues: vues, dehors: L.B.interieur === null };
    }""" % {"dirs": json.dumps({k: list(v) for k, v in REGARDS.items()})})
    for face, vue in r["vues"].items():
        assert vue["porte"] is True and vue["invite"] == "SORTIR", f"regard {face} : {vue}"
    assert r["dehors"] is True, "on est reste enferme : ACTION n'a pas fait sortir"


def test_une_portiere_ne_s_ouvre_que_de_face(banc):
    """Un char stationne a cote de soi : « MONTER » et ACTION ne le voient que
    regardes. ⚠️ Et `otageSousLaMain` s'ecarte devant un char qu'on regarde, pas
    devant un char qu'on a dans le dos — c'est la passante qu'on regarde qui
    compte."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        // Pas d'etal a portee : la roulotte a cafe du depart passerait avant la portiere.
        for (const e of L.B.entites.filter(function (q) { return q.type === 'ambulant'; })) L.Entites.retirer(e);
        const v = L.Vehicules.creer('auto', j.x + 22, j.y, Math.PI / 2, { etat: 'stationne' });
        L.Entites.indexer();
        const dirs = %(dirs)s;
        const vues = {};
        for (const face of Object.keys(dirs)) {
            L.Entites.regarder(j, dirs[face][0], dirs[face][1]);
            L.Missions.majInvite(j);
            vues[face] = { char: L.Vehicules.vehiculeSousLaMain(j) === v, invite: L.B.invite || null };
        }
        L.Entites.regarder(j, -1, 0);            // le dos tourne
        o.tape('KeyE', 2);
        const dos = !!j.dansVehicule;
        L.Entites.regarder(j, 1, 0);             // de face
        o.tape('KeyE', 2);
        return { vues: vues, dos: dos, deFace: !!j.dansVehicule };
    }""" % {"dirs": json.dumps({k: list(v) for k, v in REGARDS.items()})})
    for face, vue in r["vues"].items():
        assert vue["char"] is (face == "droite"), f"regard {face} : {vue}"
        assert (vue["invite"] or "").startswith("MONTER") is (face == "droite"), f"regard {face} : {vue}"
    assert r["dos"] is False, "ACTION est montee dans un char qu'on ne regardait pas"
    assert r["deFace"] is True, "ACTION n'est pas montee dans le char qu'on regardait"


def test_on_parle_a_quelqu_un_en_le_regardant(banc):
    """Les gens auxquels ACTION s'adresse — les hommes de Sal, l'homme-sandwich,
    la fille de la Brume, le temoin qu'on fait taire, le stool, un personnage de
    l'histoire — ne se servent que regardes. Une seule table : chacun est pose a
    dix-huit pixels a droite, on le regarde, puis on lui tourne le dos."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.Entites.regarder(j, 1, 0);
        const portes = {
            collecteur: [function (e) { e.collecteur = true; }, L.Missions.collecteurSousLaMain],
            crieur: [function (e) { e.metier = 'reclame'; }, L.Missions.crieurSousLaMain],
            fille: [function (e) { e.metier = 'compagnie'; }, L.Missions.filleSousLaMain],
            temoin: [function (e) { e.etat = 'temoin'; e.crime = { rapporte: false }; }, L.Missions.temoinSousLaMain],
            stool: [function (e) { e.stool = true; e.porteBut = { x: 0, y: 0 }; }, L.Missions.stoolSousLaMain],
            personnage: [function (e) { e.personnage = 'sergent'; }, L.Histoire.personnageSousLaMain],
        };
        const vues = {};
        for (const nom of Object.keys(portes)) {
            const e = L.Entites.creerPieton(j.x + 18, j.y, L.Entites.archetypeDeRue());
            portes[nom][0](e);
            L.Entites.indexer();
            const trouve = function () { const q = portes[nom][1](j); return !!q && (q === e || q.personnage === e.personnage); };
            L.Entites.regarder(j, 1, 0);
            const deFace = trouve();
            L.Entites.regarder(j, -1, 0);
            const dos = trouve();
            L.Entites.retirer(e); L.Entites.indexer();
            vues[nom] = { deFace: deFace, dos: dos };
        }
        return vues;
    }""")
    for nom, vue in r.items():
        assert vue == {"deFace": True, "dos": False}, f"{nom} : {vue}"


def test_un_comptoir_se_sert_de_face(banc):
    """Dedans, un point d'action (comptoir, caisse, lit...) demande le regard —
    la porte, elle, n'a pas besoin de lui (juge d'en haut)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'depanneur'; }) || c.portes[0];
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const p = L.B.interieur.points[0];
        if (!p) return { pasDePoint: true };
        j.x = (p.x + 0.5) * L.TT; j.y = (p.y + 1.5) * L.TT;            // une tuile sous le point
        L.Entites.regarder(j, 0, -1);
        const deFace = L.Missions.pointSousLaMain(j) === p;
        L.Entites.regarder(j, 0, 1);
        const dos = L.Missions.pointSousLaMain(j) === p;
        return { deFace: deFace, dos: dos, type: p.type };
    }""")
    assert not r.get("pasDePoint"), "le depanneur n'a aucun point d'action"
    assert r["deFace"] is True, f"le point {r['type']} n'est pas sous la main quand on le regarde"
    assert r["dos"] is False, f"le point {r['type']} se sert dos tourne"


def test_une_arme_par_terre_se_ramasse_de_face_ou_sous_les_pieds(banc):
    """⚠️ L'EXCEPTION DES PIEDS. Une arme a dix-huit pixels demande le regard ;
    la meme tombee la ou l'on se tient (`dessus_px`) n'en demande pas : la, il
    n'y a plus de direction a regarder."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const arme = L.Entites.creer('ramassage', j.x - 14, j.y, { r: 4, objet: 'arme', arme: 'pistolet', munitions: 6, t: 0, solide: false });
        L.Entites.indexer();
        L.Entites.regarder(j, -1, 0);
        const deFace = L.Combat.objetSousLaMain(j) === arme;
        L.Entites.regarder(j, 1, 0);
        const dos = L.Combat.objetSousLaMain(j) === arme;
        arme.x = j.x + 3; arme.y = j.y; L.Entites.indexer();
        const dessous = L.Combat.objetSousLaMain(j) === arme;
        return { deFace: deFace, dos: dos, dessous: dessous };
    }""")
    assert r["deFace"] is True and r["dos"] is False, r
    assert r["dessous"] is True, "une arme sous les pieds doit se ramasser sans regarder"


def test_l_edicule_du_metro_se_prend_de_face(banc):
    """On descend au metro en regardant l'edicule, pas en lui tournant le dos
    sur le trottoir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, def = L.Monde.carte.def;
        const s = def.metro.stations[0];
        const cote = def.sol[s.y + 1] && def.sol[s.y + 1][s.x] === '.' ? 1 : -1;
        j.x = (s.x + 0.5) * L.TT; j.y = (s.y + cote + 0.5) * L.TT;
        L.Entites.indexer();
        L.Entites.regarder(j, 0, -cote);
        const deFace = !!L.Metro.ediculeSousLaMain(j);
        L.Entites.regarder(j, 0, cote);
        const dos = !!L.Metro.ediculeSousLaMain(j);
        return { deFace: deFace, dos: dos };
    }""")
    assert r == {"deFace": True, "dos": False}, r


def test_un_etal_une_machine_un_guichet_un_panneau_se_servent_de_face(banc):
    """Le reste de la rue : pose a une tuile d'eux, on les voit regardes, on ne
    les voit plus le dos tourne."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const trouve = function (f) { return L.B.entites.find(f); };
        const panneau = L.Entites.creer('panneau', j.x + 400, j.y + 400,
            { decor: 'panneau', r: 3, solide: false, dessine: true, vivant: false, defi: 'x' });
        const cibles = {
            etal: [trouve(function (e) { return e.type === 'ambulant'; }), L.Missions.etalSousLaMain],
            machine: [trouve(function (e) { return e.type === 'decor' && e.decor === 'distributrice_liqueur'; }),
                      L.Missions.distributriceSousLaMain],
            guichet: [trouve(function (e) { return e.type === 'decor' && e.decor === 'guichet'; }),
                      L.Missions.guichetSousLaMain],
            panneau: [panneau, L.Histoire.panneauSousLaMain],
        };
        const vues = {};
        for (const nom of Object.keys(cibles)) {
            const e = cibles[nom][0];
            if (!e) { vues[nom] = { absent: true }; continue; }
            j.x = e.x; j.y = e.y + 14; L.Entites.indexer();
            L.Entites.regarder(j, 0, -1);
            const deFace = !!cibles[nom][1](j);
            L.Entites.regarder(j, 0, 1);
            vues[nom] = { deFace: deFace, dos: !!cibles[nom][1](j) };
        }
        return vues;
    }""")
    for nom, vue in r.items():
        assert not vue.get("absent"), f"la ville n'a pas de {nom} pour le juge"
        assert vue == {"deFace": True, "dos": False}, f"{nom} : {vue}"


def test_le_bouclier_et_les_poches_demandent_de_regarder_la_victime(banc):
    """Prendre quelqu'un en otage, lui faire les poches : on le regarde. Les poches
    demandent DEJA d'etre dans son dos — regarder, c'est ce qu'on fait en le
    suivant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        L.Combat.ramasserArme('pistolet', 12);
        j.arme = 'pistolet';
        const p = o.poser('passant', 14, 0);
        p.porteBut = null; p.argent = 40; p.angle = 0;       // il nous tourne le dos
        L.Entites.indexer();
        L.Entites.regarder(j, -1, 0);
        const dos = { otage: !!L.Combat.otageSousLaMain(j), poches: L.Combat.pickpocket(j) };
        L.Entites.regarder(j, 1, 0);
        const deFace = { otage: !!L.Combat.otageSousLaMain(j), poches: L.Combat.pickpocket(j) };
        return { dos: dos, deFace: deFace };
    }""")
    assert r["dos"] == {"otage": False, "poches": False}, r
    assert r["deFace"] == {"otage": True, "poches": True}, r


def test_les_maneges_et_les_comptoirs_de_la_foire_demandent_de_regarder(banc):
    """Le train, la montagne russe, la grande roue et un comptoir de jeu : au moins
    un regard les voit, au moins un ne les voit pas — et jamais les quatre, ce que
    donnerait un manege qu'on sert dos tourne."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const F = L.Foire, j = L.B.joueur, TT = L.TT;
        j.invincible = 999999;
        const poses = {};
        // Le petit train, a quai, le joueur sur le quai a cote du wagon 1.
        poses.train = function () {
            const t = F.train; t.s = t.sGare; t.v = 0; t.attente = t.def.gare_images;
            const w = F.wagons()[1];
            j.x = w.x + 2; j.y = t.def.quai[2] * TT + 8;
            return function () { return !!F.sousLaMain(j); };
        };
        // Le chariot 1 de la montagne, en gare, le joueur douze pixels sous lui.
        poses.montagne = function () {
            const m = F.montagne, d = m.def;
            m.s = m.sGare; m.v = 0; m.attente = d.gare_images;
            const p = F.pointDeMontagne(m.s - d.ecart_px);
            j.x = p.x + 1; j.y = p.y + 12;
            return function () { return !!F.sousLaMain(j); };
        };
        // La grande roue : douze pixels sous le point de montee.
        poses.roue = function () {
            const R = F.roue;
            j.x = R.x; j.y = R.y + R.devant + 12;
            return function () { return !!F.sousLaMain(j); };
        };
        // Un comptoir de jeu : deux tuiles sous lui.
        poses.comptoir = function () {
            const g = F.jeux().find(function (q) { return q.slug === 'galerie_tir'; });
            j.x = g.x * TT + 8; j.y = (g.y + 2) * TT + 8;
            return function () { return F.jeuSousLaMain(j) === 'galerie_tir'; };
        };
        const dirs = { haut: [0, -1], bas: [0, 1], gauche: [-1, 0], droite: [1, 0] };
        const vues = {};
        for (const nom of Object.keys(poses)) {
            const voit = poses[nom]();
            L.Entites.indexer();
            vues[nom] = {};
            for (const face of Object.keys(dirs)) {
                L.Entites.regarder(j, dirs[face][0], dirs[face][1]);
                vues[nom][face] = voit();
            }
        }
        return vues;
    }""")
    for nom, vue in r.items():
        assert any(vue.values()), f"{nom} : aucun regard ne le voit : {vue}"
        assert not all(vue.values()), f"{nom} se sert dos tourne : {vue}"
