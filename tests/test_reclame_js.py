"""Les hommes-sandwichs et la cabane a fruits de mer, vus du jeu (13 sept. 2026).

`test_reclame.py` juge le catalogue et la carte ; ici on regarde ce que le
navigateur en fait : le solliciteur nait a son poste, il vient vers toi, il te
tient le crachoir dans une bulle, son coupon rabat le prix du kiosque une
fois, et la cabane sert une guedille comme le kiosque sert un hot-dog.
"""


def test_l_homme_sandwich_nait_a_son_poste_le_jour_et_pas_la_nuit(banc, paquet):
    """Un par poste (`carte.reclames`), a l'interieur de la bulle du joueur,
    et seulement dans ses heures."""
    postes = paquet["carte"]["reclames"]
    heures = next(p for p in paquet["pietons"]["catalogue"] if p["slug"] == "homme_sandwich")["heures"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const poste = L.Monde.carte.def.reclames[0];
        // On se met a une bulle du poste, hors ecran : il doit naitre a la prochaine ronde.
        // ⚠️ DU COTE QUI RESTE DANS LA CARTE. Le juge se mettait toujours a l'est,
        // et il a tenu tant que le poste 0 avait vingt-deux tuiles de ville a sa
        // droite. Le 16 sept. 2026, les kiosques ont change d'ordre et le poste 0
        // est tombe a vingt et une tuiles du bord est : le joueur etait pose HORS
        // DU MONDE, et « personne n'est ne au poste » accusait l'homme-sandwich.
        const dx = poste.x * 16 + 8 + 360 < L.Monde.carte.w * 16 ? 360 : -360;
        j.x = poste.x * 16 + 8 + dx; j.y = poste.y * 16 + 8; L.Monde.centrerCamera(j.x, j.y);
        L.B.partie.heure = %(jour)s;
        for (const e of L.B.entites.slice()) if (e.metier === 'reclame') L.Entites.retirer(e);
        // ⚠️ `retirer` ote de la liste, pas de la GRILLE : en partie, `indexer`
        // la refait a chaque image. Sans lui ici, le crieur qu'on vient d'oter
        // tient encore sa place aux yeux de `placeLibre`, et personne ne nait.
        // Le juge a tenu tant que le poste 0 etait hors de la bulle du depart.
        L.Entites.indexer();
        const nes = L.Entites.naitreLesHommesSandwichs(false);
        const crieurs = L.B.entites.filter(function (e) { return e.metier === 'reclame'; });
        const c = crieurs[0];
        const ou = c ? { x: Math.floor(c.x / 16), y: Math.floor(c.y / 16), sprite: c.sprite, kiosque: c.kiosque, boniment: c.boniment, poste: !!c.poste } : null;
        // Une deuxieme ronde n'en fait pas naitre un deuxieme au meme poste.
        const encore = L.Entites.naitreLesHommesSandwichs(false);
        // La nuit, personne ne crie.
        for (const e of L.B.entites.slice()) if (e.metier === 'reclame') L.Entites.retirer(e);
        L.B.partie.heure = %(nuit)s;
        const laNuit = L.Entites.naitreLesHommesSandwichs(false);
        return { nes: nes, ou: ou, poste: { x: poste.x, y: poste.y, commerce: poste.commerce }, encore: encore, laNuit: laNuit,
                 valide: L.Atlas.valider('homme_sandwich', L.SPRITES.homme_sandwich) };
    }""" % {"jour": (heures[0] + heures[1]) / 2, "nuit": 0.97})
    assert r["valide"] == [], r["valide"]
    assert r["nes"] >= 1, "personne n'est ne au poste"
    assert r["ou"]["x"] == r["poste"]["x"] and r["ou"]["y"] == r["poste"]["y"], "il n'est pas ne a son poste"
    assert r["ou"]["sprite"] == "homme_sandwich" and r["ou"]["poste"] is True
    assert r["ou"]["kiosque"] == r["poste"]["commerce"]
    assert r["ou"]["boniment"], "il n'a rien a crier"
    assert r["encore"] == 0, "deux hommes-sandwichs au meme poste"
    assert r["laNuit"] == 0, "un homme-sandwich qui crie a minuit"
    assert len(postes) >= 5


def test_l_homme_sandwich_vient_vers_toi_et_te_tient_le_crachoir(banc, paquet):
    """Il te repere a six tuiles, il marche vers toi (jamais en courant), il
    s'arrete a portee et sa bulle porte le boniment de son kiosque — puis il
    se tait et te laisse la paix."""
    r = paquet["reclame"]
    res = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(12);
        const j = L.B.joueur;
        // Un bout de trottoir droit, sans personne : on juge le solliciteur,
        // pas la geometrie du terminus ni la foule.
        const c0 = L.Monde.carte;
        let t = null;
        for (let y = 2; y < c0.h - 2 && !t; y++) for (let x = 2; x < c0.w - 8 && !t; x++) {
            let ok = true;
            for (let k = 0; k < 6; k++) if (c0.sol[y][x + k] !== '.' || !L.Monde.marchablePieton(x + k, y)) ok = false;
            if (ok) t = { x: x, y: y };
        }
        j.x = t.x * 16 + 8; j.y = t.y * 16 + 8; L.Monde.centrerCamera(j.x, j.y);
        for (const e of L.B.entites.slice()) if (e.type === 'pieton') L.Entites.retirer(e);
        const c = o.poser('homme_sandwich', 64, 0);
        c.etat = 'flane'; c.kiosque = 'hotdog'; c.boniment = 'HOT-DOG MOITIÉ PRIX';
        L.B.partie.heure = 0.5;
        const d0 = Math.hypot(c.x - j.x, c.y - j.y);
        let aborde = false, boniment = null, vitesseMax = 0, dMin = d0, images = 0;
        for (let i = 0; i < 300 && c.etat !== 'boniment'; i++) {
            o.frame(1); images++;
            if (c.etat === 'aborde') { aborde = true; vitesseMax = Math.max(vitesseMax, Math.hypot(c.vx, c.vy)); }
            dMin = Math.min(dMin, Math.hypot(c.x - j.x, c.y - j.y));
        }
        if (c.etat === 'boniment') boniment = { texte: c.bulle ? c.bulle.texte : null, face: c.face, d: Math.hypot(c.x - j.x, c.y - j.y), dit: L.Son.Voix.dernierT };
        // Il finit par se taire, et il ne recommence pas tout de suite.
        o.frame(%(boniment)d + 5);
        const apres = { etat: c.etat, bulle: !!c.bulle, repos: c.repos };
        return { d0: d0, aborde: aborde, boniment: boniment, vitesseMax: vitesseMax, dMin: dMin, images: images, apres: apres,
                 course: L.B.defs.recherche.vitesses.pieton_course };
    }""" % {"boniment": r["boniment_images"]})
    assert res["aborde"] is True, "il ne vient pas"
    assert res["boniment"] is not None, f"il n'a jamais parle ({res})"
    assert res["boniment"]["texte"] == "HOT-DOG MOITIÉ PRIX"
    assert res["boniment"]["d"] <= r["portee_px"] + 4, "il parle de trop loin"
    assert res["boniment"]["face"] == "gauche", "il ne te regarde pas"
    assert res["vitesseMax"] < res["course"], "un solliciteur ne court pas"
    # ⚠️ « Il se tait » ne veut pas dire « il remarche » : un pieton a poste
    # s'arrete tout seul une fois sur trois (`majPieton`), et exiger `flane`
    # revenait a jouer ce de-la a chaque fois que la ville bougeait d'une tuile.
    # Ce qui compte est qu'il ait FINI son boniment et ferme sa bulle.
    assert res["apres"]["etat"] in ("flane", "arret"), f"il ne se tait jamais : {res['apres']}"
    assert res["apres"]["bulle"] is False, "sa bulle ne se ferme pas"
    assert res["apres"]["repos"] > 0, "il va recommencer tout de suite"


def test_le_coupon_rabat_le_prix_du_kiosque_une_fois(banc, paquet):
    """ACTION devant lui : un coupon. Le kiosque coute alors `rabais` fois le
    prix — l'invite le dit, la caisse le fait — et une seule fois. Et il expire."""
    r = paquet["reclame"]
    tarifs = paquet["economie"]["tarifs"]
    res = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        // ⚠️ **UN SEUL ÉTAL SOUS LA MAIN.** L'invite ACTION nomme le plus proche,
        // et la ville pose ses ambulants où elle veut : le 17 sept. 2026, la trame
        // a bougé et une roulotte à café s'est installée au terminus PUIS à côté
        // du kiosque à hot-dogs — c'est elle que le juge lisait, deux fois. On ne
        // garde que le kiosque dont ce juge parle.
        for (const q of L.B.entites.slice()) {
            if (q.type === 'ambulant' && q.slug !== 'hotdog') L.Entites.retirer(q);
        }
        L.B.defs.ambulants = (L.B.defs.ambulants || []).filter(function (a) { return a.slug === 'hotdog'; });
        const c = o.poser('homme_sandwich', 14, 0);
        c.etat = 'boniment'; c.minuterie = 500; c.kiosque = 'hotdog'; c.boniment = 'HOT-DOG MOITIÉ PRIX';
        // ⚠️ On regarde l'homme-sandwich : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        o.viser(c);
        L.Entites.indexer();
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        const pris = L.Missions.interagir(j);
        const coupons = Object.assign({}, j.coupons);
        const deuxFois = L.Missions.interagir(j);
        const apresCrieur = { etat: c.etat, repos: c.repos };
        // Au kiosque : le prix de l'invite et celui de la caisse.
        const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === 'hotdog'; })[0];
        c.x = j.x + 400; c.y = j.y + 400;
        j.x = etal.x; j.y = etal.y + 22; j.vie = 10; L.B.partie.argent = 100;
        o.viser(etal);                                     // au kiosque : on le regarde, lui
        L.Entites.indexer();
        L.Missions.majInvite(j);
        const inviteKiosque = L.B.invite;
        L.Missions.interagir(j);
        const argent1 = L.B.partie.argent;
        L.Missions.majInvite(j);
        const inviteApres = L.B.invite;
        L.Missions.interagir(j);
        const argent2 = L.B.partie.argent;
        // Un coupon qu'on n'utilise pas expire.
        j.coupons = { hotdog: 3 };
        o.frame(5);
        return { invite: invite, pris: pris, coupons: coupons, deuxFois: deuxFois, apresCrieur: apresCrieur,
                 inviteKiosque: inviteKiosque, argent1: argent1, inviteApres: inviteApres, argent2: argent2,
                 expire: !j.coupons.hotdog };
    }""")
    prix = tarifs["hotdog"]
    rabattu = round(prix * r["rabais"])
    assert res["invite"] == "PRENDRE LE COUPON — KIOSQUE À HOT-DOGS"
    assert res["pris"] is True and res["coupons"]["hotdog"] == r["coupon_s"] * 60
    assert res["deuxFois"] is True and res["apresCrieur"]["etat"] == "flane" and res["apresCrieur"]["repos"] > 0
    assert res["inviteKiosque"] == "KIOSQUE À HOT-DOGS — " + str(rabattu) + " $ (COUPON)"
    assert res["argent1"] == 100 - rabattu, "la caisse n'a pas fait le prix de l'invite"
    assert res["inviteApres"] == "KIOSQUE À HOT-DOGS — " + str(prix) + " $", "le coupon a servi deux fois"
    assert res["argent2"] == 100 - rabattu - prix
    assert res["expire"] is True, "le coupon n'expire pas"


def test_la_cabane_sert_une_guedille(banc, paquet):
    """Comme le kiosque a hot-dogs : de la vie et du souffle contre de
    l'argent, un marchand derriere, et l'enseigne dessinee."""
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === 'fruits_de_mer'; })[0];
        if (!etal) return { etal: false };
        const vendeur = L.B.entites.find(function (e) { return e.metier === 'ambulant' && e.commerce === 'fruits_de_mer'; });
        j.x = etal.x; j.y = etal.y + 22; j.vie = 40; j.endurance = 20; L.B.partie.argent = 100; L.B.partie.heure = 0.5;
        // ⚠️ On regarde la cabane : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        o.viser(etal);
        L.Entites.indexer();
        const achat = L.Missions.interagir(j);
        const d = L.DECORS.cabane_fruits_de_mer;
        const ctx = L.Base.nouveauCanvas(d.w, d.h).getContext('2d');
        ctx.traces = [];
        d.peindre(ctx, d.w, d.h);
        return { etal: true, achat: achat, vie: j.vie, souffle: j.endurance, argent: L.B.partie.argent,
                 vendeur: !!vendeur, rects: ctx.traces.length, r: d.r, sol: d.sol, portee: L.Entites.PORTEE_DECOR };
    }""")
    assert r["etal"] is True, "aucune cabane a fruits de mer dans la ville"
    assert r["achat"] is True
    assert r["argent"] == 100 - tarifs["guedille"]
    assert r["vie"] == 40 + tarifs["guedille_pv"]
    assert r["souffle"] == min(100, 20 + tarifs["guedille_souffle"])
    assert r["vendeur"] is True, "personne derriere la cabane"
    assert r["rects"] > 20, "la cabane ne se dessine pas"
    # Son empreinte tient dans la portee de recherche du decor solide.
    assert (r["sol"][0] ** 2 + r["sol"][1] ** 2) ** 0.5 < r["portee"]


def test_le_casse_croute_et_les_comptoirs_ont_de_quoi_manger(banc, paquet):
    """Demande de Martin : de la bouffe et a boire partout ou ca fitte. Le
    casse-croute garanti sert plus qu'un hot-dog, et le comptoir du bar plus
    qu'une biere."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.interieur = { slug: 'casse_croute', nom: 'Casse-croûte' };
        const menu = L.Missions.menuDuPoint({ type: 'hotdog' });
        const bar = L.Missions.menuComptoir({ type: 'emplettes', genre: 'nuit' }, []);
        const depanneur = L.Missions.menuComptoir({ type: 'emplettes', genre: 'bouffe' }, []);
        L.B.interieur = null;
        return { casse: menu.items.map(function (i) { return i.libelle; }),
                 bar: bar.items.map(function (i) { return i.libelle; }),
                 depanneur: depanneur.items.map(function (i) { return i.libelle; }) };
    }""")
    assert {"HOT-DOG", "POUTINE", "SOUPE AUX POIS", "LIQUEUR", "CAFÉ"} <= set(r["casse"])
    assert {"GROSSE BIÈRE", "AILES DE POULET", "SHOOTER DE RYE", "CHIPS"} <= set(r["bar"])
    assert {"SANDWICH", "SOUPE AUX POIS", "PÂTÉ CHINOIS", "LIQUEUR"} <= set(r["depanneur"])
