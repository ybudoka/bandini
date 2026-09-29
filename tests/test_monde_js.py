"""La ville qu'on touche, sous Node : toits, clôtures, eau, décor, borne défoncée,
sol des îlots, fosses d'arbre, et les trois vitesses du joueur contre les murs.

Découpé de `test_moteur_js.py` (vague D, 29 sept. 2026) : même banc, mêmes juges.
"""


def test_le_joueur_a_trois_vitesses_et_ne_traverse_pas_les_murs(banc, paquet):
    """⚠️ TROIS vitesses, un seul bouton — et la COURSE EST LA VITESSE PAR
    DEFAUT (demande de Martin : « on court quand même tout le temps, avec la
    grandeur de la carte »). Pousser le pouce à fond, ou n'importe quelle
    touche de direction, c'est courir ; l'effleurer, c'est marcher ; le bouton,
    c'est sprinter — et lui seul coûte du souffle.

    On mesure vers l'OUEST : à l'est du terminus se tient Ti-Guy, et depuis que
    la foule ne se traverse plus, un personnage figé est un obstacle."""
    v = paquet["recherche"]["vitesses"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        function versLOuest(images) { const x = j.x; o.frame(images); return x - j.x; }
        // 1. Au clavier, sans rien : on COURT.
        o.touche('KeyA');
        const course = versLOuest(60);
        o.relacher('KeyA');
        // 2. Le pouce a peine pousse : on MARCHE.
        o.pad([-0.5, 0], [0, 0, 0, 0]);
        const marche = versLOuest(60);
        o.pad(null);
        // 3. Le bouton : on SPRINTE.
        j.endurance = 100;
        o.touche('ShiftLeft'); o.touche('KeyA');
        const sprint = versLOuest(60);
        o.relacher('KeyA'); o.relacher('ShiftLeft');
        // Vers le haut, un batiment se trouve sur le chemin : on doit s'arreter dessus.
        o.touche('KeyW'); o.frame(900); o.relacher('KeyW');
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { marche: marche, course: course, sprint: sprint,
                 sol: L.Monde.solidite(tx, ty), y: j.y, etat: L.B.etat,
                 dataEtat: o.elements.bandini.dataset.etat };
    }""")
    assert r["course"] > 50, "au clavier, sans rien, on doit courir"
    assert r["marche"] > 0, "le pouce a peine poussé doit quand même avancer"
    assert r["course"] > r["marche"] * 1.3, (
        "courir n'est pas plus rapide que marcher : %s contre %s" % (r["course"], r["marche"])
    )
    assert r["sprint"] > r["course"] * 1.15, (
        "le sprint doit être nettement plus rapide que la course : %s contre %s" % (r["sprint"], r["course"])
    )
    # Les trois vitesses du paquet, dans l'ordre, et le policier à la course.
    assert v["joueur_marche"] < v["joueur_course"] < v["joueur_sprint"]
    assert v["policier"] == v["joueur_course"], (
        "le policier doit courir exactement à la vitesse de la course : %s contre %s"
        % (v["policier"], v["joueur_course"])
    )
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


def test_une_cloture_nord_sud_ne_se_peint_pas_comme_une_est_ouest(banc):
    """⚠️ Bug de Martin : « les clotures qui sont nord-sud ne sont pas dans le
    bon sens. » Les trois peintres ne savaient dessiner qu'est-ouest — lisses en
    travers de toute la tuile, poteaux a x=2 et x=13, planches cote a cote — et
    une cloture qui descend du nord au sud etait une PILE DE PANNEAUX VUS DE
    FACE. Elles lisent maintenant leurs voisines (`varianteDeCloture`), comme les
    passages pietons, les cases de stationnement et les rampes le font deja.

    ⚠️ La PREMIERE version de ce juge exigeait que le nord-sud soit l'est-ouest
    TOURNE. Elle a sorti les clotures de leur premier bug, puis elle a verrouille
    le suivant, que Martin a nomme aussitot : « les clotures nord-sud doivent
    etre plus vues de haut, donc mince ». Un panneau tourne de 90 degres reste
    un panneau — sept pixels de large, pose a plat.

    La regle juste est deja ecrite deux fois dans le depot : la camera regarde
    d'en haut avec juste assez de face au SUD (les facades de la ville, les
    meubles des interieurs). Une cloture est-ouest montre donc sa HAUTEUR ; une
    cloture nord-sud ne montre que son EPAISSEUR. Le juge mesure cette largeur,
    et il tourne pour les trois glyphes."""
    r = banc("""function (L, o) {
        function peindre(glyphe, variante) {
            const c = L.Base.nouveauCanvas(L.TT, L.TT);
            const ctx = c.getContext('2d');
            ctx.traces = [];
            L.TUILES[glyphe](ctx, variante, L.TT);
            return ctx.traces;
        }
        // Ce que le dessin OCCUPE sur un axe (0 = x, 1 = y), le fond d'herbe
        // mis de cote : c'est la hauteur d'une cloture vue de face, et la
        // largeur d'une cloture vue par la tranche.
        function etendue(traces, axe) {
            let min = 99, max = -1;
            for (const t of traces) {
                if (t[2] >= L.TT && t[3] >= L.TT) continue;      // le fond, pas la cloture
                if (t[axe] < min) min = t[axe];
                if (t[axe] + t[axe + 2] > max) max = t[axe] + t[axe + 2];
            }
            return max < 0 ? 0 : max - min;
        }
        const sortie = {};
        for (const glyphe of ['f', 'w', 'X']) {
            const est_ouest = peindre(glyphe, 2 | 8);       // elle continue a l'est et a l'ouest
            const nord_sud = peindre(glyphe, 1 | 4);        // elle continue au nord et au sud
            const bout = peindre(glyphe, 8);                // elle s'arrete ici, vers l'ouest
            const boutNS = peindre(glyphe, 1);              // elle s'arrete ici, vers le nord
            const coin = peindre(glyphe, 1 | 2);            // un coin nord-est
            sortie[glyphe] = {
                est_ouest: est_ouest, nord_sud: nord_sud,
                // La hauteur de celle qu'on voit de face, la largeur de celle
                // qu'on prend par la tranche.
                hauteurEO: etendue(est_ouest, 1),
                largeurNS: etendue(nord_sud, 0),
                // Le poteau du centre : ce qui tient le tournant et ferme un bout.
                poteauBout: bout.some(function (t) { return t[0] === 7 && t[2] === 2; }),
                poteauCoin: coin.some(function (t) { return t[0] === 7 && t[2] === 2; }),
                poteauDroit: est_ouest.some(function (t) { return t[0] === 7 && t[2] === 2; }),
                // Un bout tout en nord-sud ferme par un CHAPEAU, pas par un piquet.
                chapeauNS: boutNS.some(function (t) { return t[1] === 7 && t[3] === 2; }),
                // ⚠️ Le fond d'herbe fait 16 x 16 : sans le mettre de cote, il
                // passerait pour un poteau debout a lui tout seul.
                piquetNS: boutNS.some(function (t) {
                    return !(t[2] >= L.TT && t[3] >= L.TT) && t[3] >= 10;
                }),
            };
        }
        return sortie;
    }""")
    for glyphe, mesure in r.items():
        assert mesure["est_ouest"], f"{glyphe} : une cloture est-ouest ne dessine rien"
        assert mesure["nord_sud"] != mesure["est_ouest"], (
            f"{glyphe} : le nord-sud se peint exactement comme l'est-ouest — elle est couchee"
        )
        # ⚠️ Le juge du bug de Martin : une cloture nord-sud se prend par la
        # tranche, donc elle occupe NETTEMENT moins large qu'une est-ouest
        # n'occupe haut. Tournee, elle faisait exactement la meme mesure.
        assert mesure["largeurNS"] * 2 <= mesure["hauteurEO"], (
            f"{glyphe} : le nord-sud fait {mesure['largeurNS']} px de large pour "
            f"{mesure['hauteurEO']} px de haut a l'est-ouest — c'est un panneau, pas une tranche"
        )
        assert mesure["largeurNS"] >= 2, f"{glyphe} : le nord-sud a disparu"
        assert mesure["chapeauNS"] is True, f"{glyphe} : un bout nord-sud sans chapeau de poteau"
        assert mesure["piquetNS"] is False, (
            f"{glyphe} : un poteau debout au bout d'un brin vu par la tranche"
        )
        assert mesure["poteauBout"] is True, f"{glyphe} : un bout de course sans poteau — coupe au couteau"
        assert mesure["poteauCoin"] is True, f"{glyphe} : un coin sans poteau — la maille flotte"
        assert mesure["poteauDroit"] is False, f"{glyphe} : un poteau au milieu d'une ligne droite"


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


def test_un_toit_porte_son_bord_et_ses_versants(banc):
    """⚠️ Un toit etait peint TUILE PAR TUILE, chacune ignorant les autres : un
    carre de couleur et des points tires de `hash2`. C'est une texture, pas un
    toit — et une texture uniforme ne peut pas etre realiste, parce qu'un vrai
    toit vu d'en haut ne se lit ni par son grain ni par sa couleur. Il se lit par
    son BORD.

    Ce juge mesure les deux choses que le voisinage doit apprendre a la tuile :
    ou le toit s'arrete (le bord), et sur quel versant on est (la pente). Il
    compare aussi les cuissons : un bord ne se peint pas comme un plein toit,
    sinon il n'y a pas de bord."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        // Un toit plat assez large pour avoir un DEDANS et des bords.
        let plein = null, bord = null;
        for (let ty = 2; ty < c.h - 2 && !plein; ty++) {
            for (let tx = 2; tx < c.w - 2 && !plein; tx++) {
                const g = L.Monde.glyphe(tx, ty);
                if ('BEO'.indexOf(g) < 0) continue;
                const v = L.Monde.varianteDeToit(g, tx, ty);
                // ⚠️ Un bord et un plein DU MEME GLYPHE : chaque toit a son peintre,
                // et comparer le bord d'un toit plat au plein d'un toit a versants
                // ne compare rien. Le juge prenait le premier de chaque et tenait
                // par chance — il est tombe le jour ou la ville a bouge d'une tuile.
                if ((v & 15) === 0 && (!bord || bord.g === g)) { plein = { g: g, x: tx, y: ty, v: v }; }
                else if ((v & 15) !== 0 && (!bord || (plein && plein.g !== bord.g && plein.g === g))) { bord = { g: g, x: tx, y: ty, v: v }; }
            }
        }
        function peindre(glyphe, variante) {
            const t = L.Base.nouveauCanvas(L.TT, L.TT);
            const ctx = t.getContext('2d');
            ctx.traces = [];
            L.TUILES[glyphe](ctx, variante, L.TT);
            return ctx.traces;
        }
        // La pente : les versants d'un toit de maison, du nord au sud.
        let pente = null;
        for (let ty = 2; ty < c.h - 2 && !pente; ty++) {
            for (let tx = 2; tx < c.w - 2 && !pente; tx++) {
                if (L.Monde.glyphe(tx, ty) !== 'P') continue;
                let haut = ty;
                while (L.Monde.glyphe(tx, haut - 1) === 'P') haut--;
                let bas = ty;
                while (L.Monde.glyphe(tx, bas + 1) === 'P') bas++;
                if (bas - haut < 1) continue;
                const versants = [];
                for (let y = haut; y <= bas; y++) versants.push((L.Monde.varianteDePente('P', tx, y) >> 4) & 3);
                pente = { versants: versants, hauteur: bas - haut + 1 };
            }
        }
        return { plein: plein, bord: bord, pente: pente,
                 tracePlein: plein ? peindre(plein.g, plein.v).length : 0,
                 traceBord: bord ? peindre(bord.g, bord.v).length : 0,
                 memeGrain: plein && bord
                   ? JSON.stringify(peindre(plein.g, (plein.v & 240))) === JSON.stringify(peindre(plein.g, (plein.v & 240) | 15))
                   : true };
    }""")
    assert r["plein"] and r["bord"], "aucun toit plat avec un dedans et un bord"
    assert r["bord"]["v"] & 15, "la tuile de bord n'a pas de bord"
    # ⚠️ « Pas pareil », et non « plus » : le bord d'un toit a versants remplace
    # le grain par une arete et peut compter MOINS de rectangles que son plein.
    # Le juge disait « plus » et tenait par chance sur le premier toit venu.
    assert r["traceBord"] != r["tracePlein"], "un bord se peint comme un plein toit"
    assert r["memeGrain"] is False, "les quatre bords ne changent rien au dessin"
    assert r["pente"], "aucun toit a deux versants dans la ville"
    versants = r["pente"]["versants"]
    assert versants[0] == 0, f"la premiere rangee doit etre le versant nord : {versants}"
    assert versants[-1] == 2, f"la derniere doit etre le versant sud : {versants}"
    assert versants == sorted(versants), f"les versants doivent se suivre du nord au sud : {versants}"
    assert versants.count(1) <= 1, f"une seule ligne de faite : {versants}"


def test_l_eau_n_est_plus_un_mur(banc, paquet):
    """⚠️ Demande de Martin : « l'eau ne doit plus être un mur, mais qu'on puisse
    soit y nager ou s'y noyer, à pied ou dans un véhicule. »

    C'était littéralement un mur : `MASQUE_PIETON` et `MASQUE_VEHICULE`
    comptaient l'eau comme une façade, et on s'arrêtait au bord de la baie —
    ce qui est le plus étrange dans une ville qui s'appelle Baie-des-Brumes.

    ⚠️ Le vrai enjeu n'est pas la noyade, c'est le **pont** : la géographie de M8
    tenait par la collision, elle tient maintenant par le **souffle**. Les
    nombres se jugent côté Python (`test_eau.py`) ; ici, c'est le moteur."""
    nage = paquet["recherche"]["nage"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const j = L.B.joueur, c = L.Monde.carte, TT = L.TT, out = {};

        // Une rive : une tuile qu'on foule, avec six tuiles d'eau plein est.
        let rive = null;
        for (let y = 4; y < c.h - 4 && !rive; y++) {
            for (let x = 4; x < c.w - 10; x++) {
                if (!L.Monde.marchablePieton(x, y) || L.Monde.estEau(x, y)) continue;
                // ⚠️ DE L'EAU SUR SEPT RANGEES, pas un filet d'une tuile. Sur
                // un chenal mince, l'agent longe la berge au sec et arrive a
                // portee d'arrestation sans se mouiller : le juge mesurait
                // alors un agent qui contourne, pas un agent qui refuse de
                // nager. ⚠️ Trois rangees ont suffi jusqu'au 14 sept. 2026 et
                // ne suffisent plus : la ville a bouge (« l'interieur a la
                // mesure du batiment »), la premiere rive trouvee est devenue
                // une langue de sable, et l'agent la contournait par une
                // rangee seche QUATRE tuiles plus haut — hors de la fenetre
                // que ce juge regardait. La ville en offre trente-quatre a
                // sept rangees : on prend celles-la.
                let eau = true;
                for (let k = 1; k <= 9; k++) {
                    for (let dy = -3; dy <= 3; dy++) if (!L.Monde.estEau(x + k, y + dy)) eau = false;
                }
                if (eau) { rive = { x: x, y: y }; break; }
            }
        }
        out.rive = rive;

        // 1. LES DEUX MASQUES NE DISENT PAS LA MEME CHOSE.
        out.masques = {
            pieton: L.Monde.bloque(rive.x + 2, rive.y, L.Monde.MASQUE_PIETON),
            nageur: L.Monde.bloque(rive.x + 2, rive.y, L.Monde.MASQUE_NAGEUR),
            flanerie: L.Monde.marchablePieton(rive.x + 2, rive.y),
        };

        // 2. ON ENTRE DANS L'EAU, ET LE SOUFFLE PART.
        j.x = rive.x * TT + 8; j.y = rive.y * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        j.endurance = 100; j.surplus = 0; j.cafeine = 0;
        o.touche('KeyD');
        let entre = -1;
        for (let i = 0; i < 180 && entre < 0; i++) { o.frame(1); if (j.nage) entre = i; }
        // ⚠️ ON MESURE AU LARGE, pas au premier pixel mouille. La premiere tuile
        // est de l'eau BASSE depuis le 16 sept. 2026 — on y a pied, elle ne
        // coûte rien (`Monde.eauBasse`, et ses propres juges) — alors une
        // seconde comptee depuis l'entree comptait seize images de patauge et
        // trouvait 22 points la ou la fiche en promet 30.
        let large = -1;
        for (let i = 0; i < 180 && large < 0; i++) {
            o.frame(1);
            if (!L.Monde.eauBasse(Math.floor(j.x / TT), Math.floor(j.y / TT))) large = i;
        }
        const souffle0 = j.endurance;
        for (let i = 0; i < 60; i++) o.frame(1);
        o.relacher('KeyD');
        out.nage = { entre: entre >= 0, large: large >= 0, dansLEau: L.Entites.dansLEau(j),
                     souffleAvant: Math.round(souffle0), souffleApres: Math.round(j.endurance),
                     tuiles: Math.round((j.x / TT) - rive.x) };

        // 3. A BOUT DE SOUFFLE, ON COULE — et on se reveille a l'hopital.
        j.endurance = 3; j.surplus = 0;
        const hopital = c.points.find(function (p) { return p.slug === 'hopital'; });
        let noye = -1;
        for (let i = 0; i < 120 && noye < 0; i++) { o.frame(1); if (L.B.transition) noye = i; }
        o.fondu();
        // ⚠️ On se reveille DANS un lit de l'hopital, plus sur son trottoir : on se
        // leve et on ressort — c'est le pas de sa porte qui dit ou l'on etait.
        const lit = { piece: L.B.interieur && L.B.interieur.slug, alite: !!j.alite, nage: !!j.nage };
        L.Entites.seLever(j, 0, 1);
        o.sortir();
        out.noyade = { noye: noye >= 0, lit: lit,
                       auSec: !L.Entites.dansLEau(j),
                       souffle: Math.round(j.endurance),
                       pres: hopital ? Math.round(Math.hypot(j.x - (hopital.x * TT + 8), j.y - (hopital.y * TT + 8))) : null };

        // 4. UN CHAR DANS L'EAU COULE, ET IL EST PERDU.
        const eau = { x: (rive.x + 4) * TT + 8, y: rive.y * TT + 8 };
        j.x = rive.x * TT + 8; j.y = rive.y * TT + 8;
        j.endurance = 100; L.Monde.centrerCamera(j.x, j.y);
        const v = L.Vehicules.creer('auto', eau.x, eau.y, 0, { etat: 'stationne' });
        const bateau = L.Vehicules.creer('bateau', eau.x, eau.y + 3 * TT, 0, { etat: 'stationne' });
        L.Entites.indexer();
        let sombre = -1;
        for (let i = 0; i < 400 && sombre < 0; i++) { o.frame(1); if (L.B.entites.indexOf(v) < 0) sombre = i; }
        out.char = { sombre: sombre >= 0, images: sombre,
                     coule_s: L.B.defs.recherche.nage.coule_s,
                     // ⚠️ Et il n'est PAS a la fourriere : couler ne doit pas
                     // devenir le moyen commode de se faire rembourser une epave.
                     auLot: (L.B.partie.fourriere || []).some(function (q) { return q.slug === 'auto'; }),
                     bateauFlotte: L.B.entites.indexOf(bateau) >= 0 };
        if (L.B.entites.indexOf(bateau) >= 0) L.Entites.retirer(bateau);

        // 5. UN AGENT NAGE DERRIERE TOI.
        // ⚠️ SIX tuiles au large, pas trois : a trois, l'agent arrive a portee
        // d'arrestation depuis la rive et s'arrete — le juge mesurait alors un
        // agent qui te passe les menottes, pas un agent qui nage.
        j.x = (rive.x + 6) * TT + 8; j.y = rive.y * TT + 8;
        j.endurance = 100; j.surplus = 60;
        L.Monde.centrerCamera(j.x, j.y);
        L.Police.remiseAZero();
        // ⚠️ Sans etoile, `Police.gere` renvoie l'agent a la flanerie des la
        // premiere image : un agent « en poursuite » sans recherche ne poursuit
        // personne, et le juge aurait mesure un promeneur.
        L.Police.etoilesAuMoins(2);
        const agent = L.Police.creerAgent(rive.x * TT + 8, rive.y * TT + 8, 'poursuit');
        agent.but = { x: j.x, y: j.y };
        agent.vuT = 0;
        L.Entites.indexer();
        let mouille = false;
        for (let i = 0; i < 300 && !mouille; i++) { o.frame(1); if (L.Entites.dansLEau(agent)) mouille = true; }
        out.police = { mouille: mouille, vitesse: L.B.defs.recherche.nage.vitesse };
        L.Entites.retirer(agent);

        // 6. AUCUN PASSANT ORDINAIRE NE SE BAIGNE.
        j.x = rive.x * TT + 8; j.y = rive.y * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        let baigneurs = 0, vus = 0;
        for (let i = 0; i < 600; i++) {
            o.frame(1);
            for (const e of L.B.entites) {
                if (e.type !== 'pieton' || e.agent || !e.vivant) continue;
                // ⚠️ Sauf les enfants de la grève, qui BARBOTENT par métier (la
                // 2e vague du bord de l'eau). Ce juge a raison sur le fond — une
                // flânerie qui mène à la baie est le genre de chose qu'on ne voit
                // qu'en jeu — et ce n'est pas lui qu'on jette : c'est l'exception
                // qu'on nomme. Ils ont leur propre juge, qui tient qu'ils ne
                // dépassent jamais la première tuile d'eau.
                if (e.metier === 'baigneur') continue;
                vus++;
                if (L.Entites.dansLEau(e)) baigneurs++;
            }
        }
        out.passants = { baigneurs: baigneurs, vus: vus };
        return out;
    }""")

    assert r["rive"], "le juge n'a pas trouvé de rive : la carte n'a plus d'eau ?"
    # ⚠️ Les deux masques : l'eau arrête un corps de piéton, jamais un nageur.
    assert r["masques"] == {"pieton": True, "nageur": False, "flanerie": False}, (
        "les masques ne disent plus ce qu'ils doivent dire : %s" % r["masques"]
    )
    n = r["nage"]
    assert n["entre"] is True and n["dansLEau"] is True, "on ne rentre pas dans l'eau : %s" % n
    assert n["large"] is True, "on n'a jamais quitté l'eau basse : le juge ne prouve rien (%s)" % n
    assert n["tuiles"] >= 1, "on n'avance pas dans l'eau : %s" % n
    # Le souffle part, et il part vite : 0,5 par image — AU LARGE.
    attendu = nage["souffle_par_image"] * 60
    assert n["souffleAvant"] - n["souffleApres"] >= attendu * 0.8, (
        "nager ne coûte presque rien : %s (attendu ~%s en une seconde)" % (n, attendu)
    )
    no = r["noyade"]
    assert no["noye"] is True, "à bout de souffle, on ne coule pas : %s" % no
    assert no["auSec"] is True, "on se réveille dans l'eau : %s" % no
    assert no["souffle"] >= 100, "on se réveille sans souffle : %s" % no
    assert no["lit"] == {"piece": "hopital", "alite": True, "nage": False}, (
        "on ne se réveille pas couché dans un lit de l'hôpital — ou encore en train de nager : %s" % no
    )
    assert no["pres"] is not None and no["pres"] < 64, "on ne ressort pas devant l'hôpital : %s" % no
    ch = r["char"]
    assert ch["sombre"] is True, "un char dans l'eau flotte : %s" % ch
    assert ch["images"] >= ch["coule_s"] * 60 * 0.8, (
        "il coule instantanément : on n'a pas le temps d'en sortir (%s)" % ch
    )
    assert ch["auLot"] is False, "un char noyé revient à la fourrière : %s" % ch
    # ⚠️ Le bateau, lui, flotte — et c'est sa fiche qui le dit, pas une classe
    # écrite dans le JavaScript.
    assert ch["bateauFlotte"] is True, "la chaloupe coule aussi : %s" % ch
    assert r["police"]["mouille"] is True, (
        "un agent lancé derrière le joueur s'arrête au bord : l'eau devient l'exploit "
        "anti-police le plus simple du jeu (%s)" % r["police"]
    )
    p = r["passants"]
    assert p["vus"] > 500, "le juge n'a croisé personne : il ne prouve rien (%s)" % p
    assert p["baigneurs"] == 0, (
        "un passant s'est mis à l'eau : `marchablePieton` doit garder l'eau, et une "
        "flânerie qui mène à la baie est le genre de chose qu'on ne voit qu'en jeu (%s)" % p
    )


def test_le_decor_arrete_ou_casse_sous_un_char_et_la_ville_se_repare(banc):
    """⚠️ Demande de Martin : « une interaction réaliste avec le décor — les bris
    de poteau, de banc de parc et d'arbre. »

    Le décor était **solide pour les piétons et fantôme pour les chars** : un
    autobus traversait un arbre, un kiosque et une fontaine sans ralentir. Le
    défonçage de M9 ne cassait que des **tuiles** (clôtures, bornes) ; le décor
    n'était ni un obstacle ni une chose qui casse. C'est la moitié d'un monde.

    Deux familles, et **c'est la fiche qui décide** : ce qui **arrête** un char
    (un arbre, une fontaine — sauf au-dessus d'une masse) et ce qui **casse**
    sous lui (un banc, un lampadaire). Le juge lance une berline puis un camion
    sur les deux, vérifie que le bris laisse des **débris**, éteint la lampe du
    poteau tombé, compte une **conduite dangereuse**, et que tout est debout le
    lendemain."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(91);
        const j = L.B.joueur;
        const out = {};

        /* Lance `slug` sur le premier decor de ce type, et dit ce qui s'est
           passe. Le char arrive par le sud, a pleine vitesse. */
        function foncer(slug, type) {
            // ⚠️ Un decor avec DE LA PLACE AU SUD : sinon le char bute sur la
            // facade d'a cote avant d'atteindre l'arbre, et on mesurerait un
            // mur en croyant mesurer un arbre.
            //
            // ⚠️ Et de la place VIDE DE DECOR, pas seulement de tuiles. Le
            // 15 sept. 2026, un buisson est entre dans l'index du decor — il
            // portait `casse` depuis toujours mais `solide: false` l'en tenait
            // dehors, et rien ne pouvait le toucher. Des qu'un char a pu le
            // coucher, celui du couloir d'approche a mange une part de l'elan
            // de la berline : elle finissait a UN pixel de l'ancre de l'arbre
            // au lieu d'un cheveu avant, et le juge criait « une berline
            // traverse un arbre » alors qu'elle s'arretait dessus. On mesurait
            // un buisson en croyant mesurer un arbre.
            const corridorLibre = function (e) {
                return !L.B.entites.some(function (q) {
                    if (q === e || q.type !== 'decor' || q.brise) return false;
                    const f = L.DECORS[q.decor] || {};
                    if (!f.casse && !f.arrete) return false;
                    const dy = q.y - e.y;
                    return Math.abs(q.x - e.x) < 24 && dy > 0 && dy < 90;
                });
            };
            const d = L.B.entites.find(function (e) {
                if (e.decor !== type || e.brise) return false;
                const tx = Math.floor(e.x / L.TT);
                for (let k = 1; k <= 6; k++) {
                    const ty = Math.floor(e.y / L.TT) + k;
                    for (let dx = -1; dx <= 1; dx++) {
                        if (L.Monde.bloque(tx + dx, ty, L.Monde.MASQUE_VEHICULE)) return false;
                    }
                }
                return corridorLibre(e);
            });
            if (!d) return null;
            j.x = d.x; j.y = d.y + 70;
            L.Monde.centrerCamera(j.x, j.y);
            const v = L.Vehicules.creer(slug, d.x, d.y + 70, -Math.PI / 2, { etat: 'roule' });
            L.Vehicules.monter(j, v);
            v.vitesse = v.def.vitesse_max; v.vx = 0; v.vy = -v.def.vitesse_max;
            const crimes0 = L.B.partie.stats.crimes;
            // ⚠️ On ne force PAS la vitesse a chaque image : un arbre qui
            // arrete doit pouvoir renvoyer le char. Le forcer, ce serait
            // pousser soi-meme le char au travers et croire que l'arbre est
            // fantome.
            for (let i = 0; i < 60; i++) L.Vehicules.avancer(v);
            const r = { brise: !!d.brise, passe: v.y < d.y,
                        // ⚠️ Seulement les debris NES D'UN BRIS (`e.debris` porte
                        // l'image) : la ville en pose deja 88 a la main, dans la
                        // cour de la fourriere et les terrains vagues.
                        debris: L.B.entites.filter(function (e) { return e.debris; }).length,
                        crimes: L.B.partie.stats.crimes - crimes0,
                        solide: d.solide };
            L.Vehicules.descendre(j, true);
            L.Entites.retirer(v);
            return r;
        }

        out.berlineArbre = foncer('auto', 'arbre');          // un arbre arrete une berline
        out.camionArbre = foncer('camion', 'arbre');         // un camion le deracine
        out.berlineBanc = foncer('auto', 'banc');            // un banc cede sous n'importe quoi

        // Le lampadaire : son poteau tombe, SA LUMIERE S'ETEINT.
        const lampe = L.B.entites.find(function (e) { return e.decor === 'lampadaire' && !e.brise; });
        const avant = L.Monde.carte.lampes.filter(function (l) { return l.eteinte; }).length;
        L.Entites.briser(lampe);
        out.lampe = { eteintes: L.Monde.carte.lampes.filter(function (l) { return l.eteinte; }).length - avant,
                      solide: lampe.solide, brise: lampe.brise };

        // Le plafond des debris : une nuit a tout casser doit tenir le rythme.
        const cassables = L.B.entites.filter(function (e) {
            const f = L.DECORS[e.decor] || {};
            return e.type === 'decor' && !e.brise && (f.casse || f.arrete);
        });
        for (const d of cassables) L.Entites.briser(d);
        out.plafond = { debris: L.B.entites.filter(function (e) { return e.debris; }).length,
                        max: L.Entites.DEBRIS_MAX, casses: cassables.length };

        // Et le lendemain, tout est debout — par `nouveauJour()`, pas en
        // appelant la reparation a la main : c'est le lever du jour qui repare,
        // et c'est ce lien-la qu'il faut juger.
        // ⚠️ On compte les brises AVANT :
        // le camion en a couche d'autres sur son passage, et une soustraction
        // faite en Python se tromperait de ce qu'elle mesure.
        const brisesAvant = L.B.entites.filter(function (e) { return e.type === 'decor' && e.brise; }).length;
        const brisesRestants = function () { return L.B.entites.filter(function (e) { return e.type === 'decor' && e.brise; }).length; };
        L.B.partie.jour++;
        L.Missions.nouveauJour();
        const remis = brisesAvant - brisesRestants();
        out.lendemain = { remis: remis, brisesAvant: brisesAvant,
                          // ⚠️ Seulement les debris NES D'UN BRIS (`e.debris` porte
                        // l'image) : la ville en pose deja 88 a la main, dans la
                        // cour de la fourriere et les terrains vagues.
                        debris: L.B.entites.filter(function (e) { return e.debris; }).length,
                          brises: L.B.entites.filter(function (e) { return e.type === 'decor' && e.brise; }).length,
                          eteintes: L.Monde.carte.lampes.filter(function (l) { return l.eteinte; }).length };
        return out;
    }""")
    a, c, b = r["berlineArbre"], r["camionArbre"], r["berlineBanc"]
    assert a and c and b, "il manque un arbre ou un banc dans la ville"
    assert a["brise"] is False and a["passe"] is False, (
        "une berline traverse un arbre : %s" % a
    )
    assert c["brise"] is True and c["passe"] is True, (
        "un camion doit déraciner l'arbre et passer : %s" % c
    )
    assert b["brise"] is True and b["passe"] is True, "un banc doit céder sous une berline : %s" % b
    assert b["solide"] is False, "un décor cassé reste solide : on bute sur des planches"
    assert b["debris"] >= 1, "le bris ne laisse aucun débris : c'est une disparition, pas un bris"
    # ⚠️ Casser est un délit : sinon défoncer est gratuit, et un char lourd
    # vaut plus qu'un char rapide.
    assert c["crimes"] >= 1, "déraciner un arbre au camion n'est pas un délit : %s" % c
    assert r["lampe"] == {"eteintes": 1, "solide": False, "brise": True}, (
        "un lampadaire à terre continue d'éclairer : %s" % r["lampe"]
    )
    assert r["plafond"]["casses"] > r["plafond"]["max"], "pas assez de décor cassé pour tester le plafond"
    assert r["plafond"]["debris"] <= r["plafond"]["max"], (
        "%s débris pour un plafond de %s" % (r["plafond"]["debris"], r["plafond"]["max"])
    )
    matin = r["lendemain"]
    assert matin["remis"] == matin["brisesAvant"] > 0, (
        "tout ce qui était cassé n'a pas été remis : %s" % matin
    )
    assert (matin["debris"], matin["brises"], matin["eteintes"]) == (0, 0, 0), (
        "le lendemain, la ville doit être debout, déblayée et rallumée : %s" % matin
    )


def test_le_decor_solide_arrete_le_joueur_mais_pas_un_buisson(banc):
    """⚠️ Le lampadaire BLOQUE maintenant, et c'est le correctif : il était
    `solide: false`, donc fantôme pour tout le monde — on le traversait à pied
    comme en char. Un poteau de deux pixels de rayon qu'on traverse, c'est la
    moitié d'un monde."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        // ⚠️ PAS LE PREMIER VENU : celui qui a LE PAS LIBRE AU SUD. On pose le
        // joueur vingt pixels sous le decor et on pousse vers le nord ; si cette
        // tuile-la est une cloture ou un mur, on ne mesure plus le decor, on
        // mesure son voisinage. Le juge est tombe le jour ou les cours arriere
        // se sont cloturees pour de bon : le premier buisson de la liste avait
        // une palissade juste en dessous, et « un buisson ne doit pas bloquer »
        // accusait le buisson.
        function pousser(type) {
            const d = L.B.entites.find(function (e) {
                if (e.decor !== type) return false;
                const tx = Math.floor(e.x / L.TT), ty = Math.floor(e.y / L.TT);
                return !L.Monde.bloque(tx, ty, L.Monde.MASQUE_PIETON)
                    && !L.Monde.bloque(tx, ty + 1, L.Monde.MASQUE_PIETON);
            });
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
    assert r["lampadaire"] is not None and r["lampadaire"] > 0, "on traverse les lampadaires"


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


def test_une_borne_defoncee_crache_et_ca_s_entend(banc):
    """⚠️ **Retour de Martin : « les trucs jaunes ne sont pas prioritaires aux
    feux » · « mets-les rouges, les bornes » · « et un jet d'eau avec son si on
    les défonce ».**

    La borne-fontaine était une **tuile** (`'b'`, solide), et une tuile ne se
    casse pas : elle ne pouvait ni tomber sous un char, ni gicler. C'est
    maintenant un **décor** avec sa fiche — donc une masse, une résistance, un
    bris. Le jet est une **entité invisible** qui vit ses dix secondes et crache
    des particules : le patron du brasier du Molotov, et la même raison — on ne
    repeint pas une tuile à chaque image pour un effet qui passe.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const borne = L.B.entites.find(function (e) { return e.decor === 'borne_fontaine'; });
        const fiche = L.DECORS.borne_fontaine;
        L.B.joueur.x = borne.x + 30; L.B.joueur.y = borne.y;
        const avant = L.B.particules.length;
        const casse = L.Entites.briser(borne);
        o.frame(1);
        const jet = L.B.entites.find(function (e) { return e.type === 'jet_eau'; });
        const apres = L.B.particules.length;
        o.frame(40);
        const encore = !!L.B.entites.find(function (e) { return e.type === 'jet_eau'; });
        if (jet) jet.minuterie = 1;
        o.frame(3);
        return { bornes: L.B.entites.filter(function (e) { return e.decor === 'borne_fontaine'; }).length,
                 casse: casse, brise: borne.brise, solide: borne.solide,
                 fiche: { casse: fiche.casse, solide: fiche.solide },
                 jet: !!jet, gouttes: apres - avant, encore: encore,
                 tari: !L.B.entites.find(function (e) { return e.type === 'jet_eau'; }),
                 son: !!(L.Son && L.Son.SFX && L.Son.SFX.borne_cassee && L.Son.SFX.borne_jet) };
    }""")
    assert r["bornes"] > 0, "aucune borne-fontaine dans la ville"
    assert r["fiche"]["casse"] and r["fiche"]["solide"],         "une borne qu'on ne peut pas defoncer n'est qu'une tache de peinture"
    assert r["casse"] is True and r["brise"] is True and r["solide"] is False
    assert r["jet"] is True, "une borne defoncee ne crache pas"
    assert r["gouttes"] > 0, f"le jet ne fait aucune goutte : {r['gouttes']}"
    assert r["encore"] is True, "le jet s'arrete dans la seconde"
    assert r["tari"] is True, "⚠️ le jet ne tarit jamais : la rue reste une fontaine"
    # ⚠️ DEUX sons, et c'est le correctif du 15 sept. 2026 : le bouchon qui
    # saute (une fois) et le souffle qui se TIENT. Un seul, et c'est le défaut
    # qu'on vient de réparer — le choc d'un accident de char rejoué seize fois.
    # Ce qu'ils jouent vraiment est jugé dans `test_son_js.py`.
    assert r["son"] is True, "le bris et le jet n'ont pas chacun leur bruit"


def test_le_sol_d_un_ilot_ne_se_repete_plus_toutes_les_quatre_tuiles(banc):
    """⚠️ Demande de Martin : « fais une passe visuelle d'amélioration de tous
    les pâtés de maison ».

    Le trottoir, l'herbe et la ruelle font **43 % de la ville** à eux trois
    (28 %, 10,5 %, 4,7 % des tuiles) — c'est de loin la plus grande surface
    qu'elle ait. Les trois se peignaient avec **quatre** tuiles de 16 px,
    tirées sur `hash2 % 4`, répétées d'un bout à l'autre du Faubourg. De loin,
    ce n'était pas un sol, c'était du papier peint.

    ⚠️ Et le trottoir faisait pire : il peignait son **joint de dalle sur chaque
    tuile**, en haut et à gauche. Un trait tous les seize pixels dans les deux
    sens, sur le quart de la ville — ce qu'on lisait alors, c'était la grille de
    la carte. Une dalle de béton fait maintenant DEUX tuiles de côté, et chaque
    tuile lit sa parité pour savoir de quel coin de dalle elle est (la même
    règle que la case de stationnement, qui ne peint que sa ligne de gauche pour
    ne pas doubler celle de sa voisine).
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function peindre(g, v) {
            const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d');
            ctx.traces = [];
            L.TUILES[g](ctx, v, L.TT);
            return JSON.stringify(ctx.traces);
        }
        // Combien de tuiles DIFFERENTES un carre de 8 x 8 donne, par sol.
        const distinctes = {};
        for (const g of ['.', ',', 'x']) {
            const vues = {};
            for (let y = 40; y < 48; y++) {
                for (let x = 40; x < 48; x++) vues[peindre(g, L.Monde.varianteDeSol(g, x, y))] = 1;
            }
            distinctes[g] = Object.keys(vues).length;
        }
        // La dalle : les quatre parites d'un carre de 2 x 2, sans l'usure.
        const dalle = [[0, 0], [1, 0], [0, 1], [1, 1]].map(function (p) {
            return L.Monde.varianteDeSol('.', 100 + p[0], 100 + p[1]) & 3;
        });
        // Qui peint un joint : une bande de 1 px sur tout un cote de la tuile.
        function joints(v) {
            const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d');
            ctx.traces = [];
            L.TUILES['.'](ctx, v, L.TT);
            const t = ctx.traces;
            return {
                ouest: t.some(function (q) { return q[0] === 0 && q[1] === 0 && q[2] === 1 && q[3] === L.TT; }),
                nord: t.some(function (q) { return q[0] === 0 && q[1] === 0 && q[2] === L.TT && q[3] === 1; }),
            };
        }
        return { distinctes: distinctes, dalle: dalle, usures: L.Monde.USURES_DE_SOL,
                 joints: [0, 1, 2, 3].map(joints) };
    }""")
    for glyphe, combien in r["distinctes"].items():
        assert combien > 4, (
            f"le sol « {glyphe} » ne donne que {combien} tuiles differentes sur 64 : "
            "c'est du papier peint"
        )
    assert r["usures"] >= 8, "moins de huit usures, et on reconnait la tuile d'a cote"
    assert sorted(r["dalle"]) == [0, 1, 2, 3], (
        f"les quatre coins d'une dalle ne se distinguent pas : {r['dalle']}")
    # ⚠️ UNE dalle sur quatre porte ses deux joints, une seule n'en porte aucun :
    # c'est ca, une dalle de deux tuiles de cote. Quatre tuiles qui peignent
    # chacune ses deux joints, c'est un quadrillage de seize pixels.
    j = r["joints"]
    assert sum(1 for q in j if q["ouest"] and q["nord"]) == 1, j
    assert sum(1 for q in j if not q["ouest"] and not q["nord"]) == 1, j
    assert sum(1 for q in j if q["ouest"]) == 2 and sum(1 for q in j if q["nord"]) == 2, j


def test_un_arbre_plante_dans_le_beton_a_une_fosse(banc):
    """⚠️ Demande de Martin : « les arbres qui sont sur un trottoir doivent avoir
    un petit rond de terre à leur pied ». Un arbre planté dans le béton sans rien
    à son pied n'est pas planté, il est **posé** — et c'est ce qu'on voyait sur
    la place publique du Faubourg, quatre arbres debout sur des dalles.

    ⚠️ C'est la **légende** qui décide, pas le dessin : `terre` dit d'un sol
    qu'on peut y planter sans rien découper (le gazon, le sable, l'allée de
    parc). Le jour où l'on plantera des arbres de rue pour de bon — il n'y en a
    que quatre aujourd'hui, 583 sur 596 sont sur du gazon — chacun aura sa fosse
    sans qu'on touche à une ligne.

    ⚠️ Et c'est une **couche peinte**, cuite avec le morceau : rien ne s'y cogne,
    et elle passe sous les entités. Peinte à chaque image sous chaque arbre, elle
    recouvrirait les pieds de celui qui marche juste au nord.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, def = c.def;
        const arbres = (def.decor || []).filter(function (d) { return d.type === 'arbre'; });
        const dansLeBeton = arbres.filter(function (d) {
            return !(def.legende[def.sol[d.y][d.x]] || {}).terre;
        });
        // Les fosses indexees, sans les doublons de morceau.
        const vues = {};
        c.fosses.forEach(function (liste) {
            liste.forEach(function (f) { vues[f.x + ',' + f.y] = def.sol[f.y][f.x]; });
        });
        // Ce que le peintre pose AU PIED du tronc (l'ancre est en (8, 15)).
        const ctx = L.Base.nouveauCanvas(L.TT, 2 * L.TT).getContext('2d');
        ctx.traces = [];
        L.FACADES.fosseDArbre(ctx, 8, 15);
        const terre = ctx.traces.filter(function (t) { return t[4] === '#4f4030'; });
        const large = Math.max.apply(null, terre.map(function (t) { return t[2]; }));
        return {
            arbres: arbres.length, dansLeBeton: dansLeBeton.length,
            fosses: Object.keys(vues).length,
            sols: Object.keys(vues).map(function (k) { return vues[k]; }),
            rangees: terre.length, large: large,
            hautes: terre.map(function (t) { return t[1]; }),
            centrees: terre.every(function (t) { return t[0] + t[2] / 2 === 8; }),
        };
    }""")
    assert r["arbres"] > 100, "il n'y a presque pas d'arbres : le juge ne mesure rien"
    assert r["dansLeBeton"] > 0, "aucun arbre de rue dans la ville livrée"
    assert r["fosses"] == r["dansLeBeton"], (
        f"{r['fosses']} fosses pour {r['dansLeBeton']} arbres plantés dans le béton")
    assert "," not in r["sols"], f"une fosse creusée dans le gazon : {r['sols']}"
    # Un ROND : plusieurs rangées, plus large au milieu qu'aux bouts, centré sur
    # le tronc. ⚠️ Une seule rangée pleine largeur serait une barre, pas un rond.
    assert r["rangees"] >= 5, f"la fosse n'a que {r['rangees']} rangées : ce n'est pas un rond"
    assert r["large"] >= 10 and r["large"] <= 16, f"fosse large de {r['large']} px"
    assert r["centrees"], "la fosse n'est pas centrée sur le tronc"
    assert max(r["hautes"]) - min(r["hautes"]) + 1 == r["rangees"], "la fosse a un trou"
