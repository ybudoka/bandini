"""Le cabriolet rose et sa conductrice, au banc.

Demande de Martin (21 sept. 2026) : « une voiture type corvette, rose, avec une
femme en robe rose qui la pilote et en descend si volée. Elle va plus vite. »

`test_vehicules.py` juge la fiche (la vitesse, la rareté, qui est au volant) et
`test_pietons.py` la robe ; ceux-ci regardent le JEU : elle naît dans le trafic
avec sa conductrice, on la VOIT au volant du bon côté, elle ne se gare jamais, et
c'est elle — pas un passant tiré au hasard — qui sort de la voiture qu'on lui vole.
"""

# Le décor commun : le joueur sur une ligne droite, et de quoi compter ce qu'on peint.
DECOR = """
        L.Jeu.commencer();
        const d = o.ligneDroite();
        const j = L.B.joueur; j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const ctx = L.Base.ecran(), vrai = ctx.drawImage;
        const images = function (v) {
            const mises = [];
            ctx.drawImage = function (img) { mises.push(img); };
            L.Vehicules.dessinerUn(ctx, v, 0, 0);
            ctx.drawImage = vrai;
            return mises;
        };
        const elle = L.B.defs.pietons.catalogue.find(function (p) { return p.slug === 'conductrice'; });
"""


def test_le_cabriolet_du_trafic_nait_avec_sa_conductrice_et_on_la_voit(banc):
    """Un char du trafic n'a personne de dessiné au volant — sauf ce qui a une
    selle (`assisDedans`). Le cabriolet en a une, et la fiche dit QUI la tient :
    la conductrice, en robe, pas un passant tiré de la rue. ⚠️ **Sans un dé de
    plus** : le catalogue la nomme, la naissance consomme les mêmes dés que celle
    du sport à côté d'elle — chaque dé tiré pour un décor déplace tout ce qui
    naît après."""
    r = banc("""function (L, o) {""" + DECOR + """
        L.graine(7);
        const nait = function (slug, options) {
            const rng = L.B.rng; let n = 0;
            L.B.rng = function () { n++; return rng(); };
            const v = L.Vehicules.creer(slug, j.x + 40, j.y, 0, options);
            L.B.rng = rng;
            return { v: v, des: n };
        };
        const roule = { conducteur: 'trafic', etat: 'roule' };
        const cab = nait('cabriolet', roule), sport = nait('sport', roule), berline = nait('auto', roule);
        const gare = nait('cabriolet', { etat: 'stationne' });
        L.Entites.indexer();
        const caps = L.Vehicules.ROTATIONS, K = L.SPRITES.cabriolet.machine.profondeur;
        const assise = L.SPRITES.cabriolet.machine.assise;
        let vus = 0, pire = 0, pireLong = 0;
        for (let i = 0; i < caps; i++) {
            const a = i * 2 * Math.PI / caps;
            cab.v.angle = a;
            const m = images(cab.v);
            if (m.length === 2) vus++;
            // OU elle est assise, dans le repere de la machine : `lateral` vers sa gauche,
            // `long` vers son nez. Le siege du conducteur est a gauche (w < 0 vers l'est).
            const cav = L.Vehicules.imageDuCavalier(L.SPRITES.cabriolet, cab.v, L.Vehicules.cavalierDe(cab.v));
            const corps = L.Atlas.cuire('joueur', L.SPRITES.joueur, L.Vehicules.cavalierDe(cab.v));
            const dx = cav.x + corps.ancre[0] - cab.v.x, dy = (cav.y + corps.ancre[1] - cab.v.y) / K;
            const lateral = dx * Math.sin(a) - dy * Math.cos(a), long = dx * Math.cos(a) + dy * Math.sin(a);
            pire = Math.max(pire, Math.abs(lateral + assise[1]));      // assise[1] = -3 : a gauche
            pireLong = Math.max(pireLong, Math.abs(long - assise[0]));
        }
        return {
            caps: caps, vus: vus,
            pilote: cab.v.pilote, robe: elle.couleurs,
            cavalier: L.Vehicules.cavalierDe(cab.v),
            des: { cabriolet: cab.des, sport: sport.des },
            berline: { cavalier: L.Vehicules.cavalierDe(berline.v), pilote: berline.v.pilote || null },
            gare: { cavalier: L.Vehicules.cavalierDe(gare.v), images: images(gare.v).length },
            ecartLateral: pire, ecartLong: pireLong, posture: L.SPRITES.cabriolet.posture,
        };
    }""")
    assert r["pilote"] is not None and r["pilote"]["arch"] == "conductrice", \
        f"le cabriolet du trafic n'a pas sa conductrice : {r['pilote']}"
    assert r["pilote"]["swaps"] == r["robe"], "elle ne porte pas ses couleurs : la robe rose"
    assert r["cavalier"] == r["robe"], "`cavalierDe` ne la rend pas : personne ne la peint"
    assert r["vus"] == r["caps"], f"on ne la voit au volant qu'à {r['vus']} caps sur {r['caps']}"
    assert r["posture"] == "volant", "elle tient le volant, elle ne barre pas une chaloupe"
    assert r["des"]["cabriolet"] == r["des"]["sport"], \
        f"sa naissance tire {r['des']['cabriolet']} dé(s), celle du sport {r['des']['sport']}"
    # Un char du trafic ordinaire n'a personne de dessiné, et un cabriolet garé non plus.
    assert r["berline"] == {"cavalier": None, "pilote": None}, f"la berline a quelqu'un de dessiné : {r['berline']}"
    assert r["gare"] == {"cavalier": None, "images": 1}, f"un cabriolet garé n'est pas vide : {r['gare']}"
    # Et elle est ASSISE au siège du conducteur, à tous les caps : à gauche, derrière le milieu.
    assert r["ecartLateral"] <= 1.3, (
        f"elle n'est pas du côté du volant : jusqu'à {r['ecartLateral']:.1f} px d'écart au siège gauche"
    )
    assert r["ecartLong"] <= 1.3, f"elle n'est pas sur son siège : {r['ecartLong']:.1f} px d'écart le long de la caisse"


def test_si_on_la_vole_elle_descend_en_robe_rose(banc, paquet):
    """⚠️ « Elle descend si volée » — c'est CELLE QUI CONDUIT qui sort, et elle sort
    en robe : le carjacking la fait sortir, témoigner et fuir, comme n'importe
    quel conducteur du trafic, mais avec SON corps (`conductrice`) et pas celui
    d'un passant tiré au hasard qui aurait ses couleurs.

    ⚠️ Et c'est l'identité du PILOTE qui décide (`pilote.arch`), pas le slug de la
    voiture : le voleur qui aurait emporté un cabriolet garé (`emporterLeChar`)
    est un voleur — c'est lui qui en descend, avec ses couleurs à lui."""
    gravite = paquet["recherche"]["delits"]["carjacking"]["etoiles"]
    r = banc("""function (L, o) {""" + DECOR + """
        L.graine(46);
        const passants = function () { return L.B.entites.filter(function (e) { return e.type === 'pieton'; }); };
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        const v = L.Vehicules.creer('cabriolet', j.x + 20, j.y, 0, { conducteur: 'trafic', etat: 'roule' });
        L.Entites.indexer();
        const chaleur = function () { return L.B.recherche.chaleur + L.B.recherche.etoiles * 100; };
        const avant = chaleur();
        L.Vehicules.monter(j, v);
        const sortis = passants();
        const out = {
            elle: sortis.map(function (e) { return { arch: e.arch, sprite: e.sprite, swaps: e.swaps, etat: e.etat, menace: e.menace === j }; }),
            robe: elle.couleurs,
            aVolant: v.conducteur === j, pilote: v.pilote,
            chaleur: chaleur() - avant, gravite: L.B.defs.recherche.chaleur_par_gravite,
            vole: v.vole, auVolant: L.Vehicules.cavalierDe(v) !== null,
        };
        // Le voleur : un cabriolet garé qu'un passant a emporte n'a PAS sa conductrice.
        L.Vehicules.descendre(j, true);
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        const w = L.Vehicules.creer('cabriolet', j.x + 60, j.y + 30, 0, { etat: 'stationne' });
        w.conducteur = 'trafic'; w.etat = 'roule';
        const voleur = { c: '#123456', h: '#654321', s: '#abcdef', p: '#fedcba' };
        w.pilote = { swaps: voleur };
        L.Entites.indexer();
        L.Vehicules.monter(j, w);
        out.voleur = passants().map(function (e) { return { arch: e.arch, sprite: e.sprite, swaps: e.swaps, etat: e.etat }; });
        out.couleursDuVoleur = voleur;
        // Et le conducteur d'une berline reste un passant de la rue.
        L.Vehicules.descendre(j, true);
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        const b = L.Vehicules.creer('auto', j.x - 60, j.y + 30, 0, { conducteur: 'trafic', etat: 'roule' });
        L.Entites.indexer();
        L.Vehicules.monter(j, b);
        out.berline = passants().map(function (e) { return { arch: e.arch, sprite: e.sprite }; });
        return out;
    }""")
    assert len(r["elle"]) == 1, f"le carjacking a fait sortir {len(r['elle'])} personne(s)"
    sortie = r["elle"][0]
    assert sortie["arch"] == "conductrice" and sortie["sprite"] == "conductrice", \
        f"ce n'est pas elle qui descend : {sortie}"
    assert sortie["swaps"] == r["robe"], "elle descend sans sa robe rose"
    assert sortie["etat"] == "temoin" and sortie["menace"], "elle doit crier, témoigner et fuir"
    assert r["aVolant"] and r["pilote"] is None, "le joueur est au volant, et elle n'y est plus"
    assert r["auVolant"], "le joueur, à son tour, se voit au volant d'un cabriolet"
    assert r["vole"] is True
    assert r["chaleur"] == gravite * r["gravite"], "le carjacking n'a pas chauffé la police"
    # Le voleur d'un cabriolet garé : un passant de la rue, en couleurs de voleur.
    assert len(r["voleur"]) == 1
    assert r["voleur"][0]["arch"] != "conductrice" and r["voleur"][0]["sprite"] != "conductrice", \
        f"le voleur est devenu la conductrice : {r['voleur']}"
    assert r["voleur"][0]["swaps"] == r["couleursDuVoleur"], "le voleur descend avec les couleurs d'une autre"
    assert len(r["berline"]) == 1 and r["berline"][0]["sprite"] != "conductrice", r["berline"]


def test_elle_ne_se_gare_jamais_et_roule_avec_sa_conductrice(banc):
    """⚠️ `au_volant` dit que le char est TOUJOURS mené : une voiture qu'on lui
    aurait laissée, sans personne à faire descendre, ne serait plus la sienne.
    Garée, elle n'aurait pas de conductrice — et pourtant elle naîtrait de la
    même fiche. Le peuplement ne la gare donc jamais ; il la fait naître en
    circulation, avec elle.

    On isole la fiche (aucun autre type ne naît) et on compte, en deux temps :
    zéro cabriolet garé quand la ville ne demande que des chars garés, et des
    cabriolets en circulation, tous avec leur conductrice, quand elle demande du
    trafic. ⚠️ Et un TÉMOIN : dans le même décor, avec l'auto seule, des chars se
    garent — sinon « zéro cabriolet garé » ne prouve que l'absence de place."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(11);
        const j = L.B.joueur, c = L.Monde.carte;
        // Le stationnement le mieux entoure de la ville : la tuile du FOND d'une case
        // (celle que `placeStationnee` cherche), avec le plus de cases autour.
        const NEZ = { '^': [0, -1], 'v': [0, 1], '<': [-1, 0], '>': [1, 0] };
        const fonds = [];
        for (let y = 2; y < c.h - 1; y++) for (let x = 1; x < c.w - 1; x++) {
            const g = L.Monde.glyphe(x, y), nez = NEZ[g];
            if (!nez || L.Monde.glyphe(x + nez[0], y + nez[1]) === g || L.Monde.glyphe(x - nez[0], y - nez[1]) !== g) continue;
            fonds.push([x, y]);
        }
        let meilleur = null, nb = -1;
        fonds.forEach(function (f) {
            const n = fonds.filter(function (g) { return Math.hypot(g[0] - f[0], g[1] - f[1]) < 24; }).length;
            if (n > nb) { nb = n; meilleur = f; }
        });
        j.x = meilleur[0] * L.TT + 8; j.y = meilleur[1] * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        L.Monde.rythme = function () { return 1; };
        const seul = function (slug) {
            L.B.defs.vehicules.forEach(function (v) { v.frequence = v.slug === slug ? 1 : 0; });
        };
        const cycle = function (n, voulu) {
            const zone = L.Monde.zoneA(j.x, j.y);
            zone.vehicules = voulu;
            if (zone.rares.indexOf('cabriolet') < 0) zone.rares = zone.rares.concat(['cabriolet']);
            const vus = { roulent: 0, gares: 0, pilotes: [] };
            for (let i = 1; i <= n; i++) {
                L.B.t = 40 * i;
                L.Entites.indexer();
                L.Vehicules.peupler();
                for (const e of L.B.entites.slice()) {
                    if (e.type !== 'vehicule' || e.conducteur === j) continue;
                    if (e.conducteur === 'trafic') { vus.roulent++; vus.pilotes.push(e.pilote ? e.pilote.arch || null : null); }
                    else if (e.etat === 'stationne' && !e.gareDeService) vus.gares++;
                    L.Entites.retirer(e);
                }
            }
            return vus;
        };
        seul('auto');
        const temoin = cycle(200, 0);
        seul('cabriolet');
        const garee = cycle(200, 0);
        const circule = cycle(120, 9);
        return { temoin: temoin, garee: garee, circule: circule, places: nb };
    }""")
    assert r["temoin"]["gares"] > 0, f"le décor du juge est faux : rien ne se gare, même une auto ({r['temoin']}, {r['places']} places)"
    assert r["garee"]["gares"] == 0, f"un cabriolet s'est garé, sans personne au volant : {r['garee']}"
    assert r["circule"]["roulent"] > 0, f"le cabriolet ne naît plus dans le trafic : {r['circule']}"
    assert all(a == "conductrice" for a in r["circule"]["pilotes"]), \
        f"un cabriolet du trafic est né sans sa conductrice : {r['circule']['pilotes']}"
