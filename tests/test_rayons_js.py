"""Des comptoirs qui vendent ce que dit l'enseigne, au banc (docs/jalons/des-comptoirs-qui-vendent-ce-que-dit-l-enseigne.md) :
le comptoir d'un commerce lit le rayon au nom de SA porte."""

import json

from app import magasins, rayons

#: Une porte de commerce ordinaire de chaque famille d'emplettes, et la pièce derrière.
TROUVER = """
    function portesDe(L, genre) {
        const c = L.Monde.carte, I = c.def.interieurs;
        return c.portes.filter(function (p) {
            const piece = p.interieur && I[p.interieur];
            return piece && /^(nord_)?[a-z]+_\\d+$/.test(p.interieur)
                && (piece.points || []).some(function (q) { return q.type === 'emplettes' && q.genre === genre; });
        });
    }
    function pointDe(L, slug) {
        return L.Monde.carte.def.interieurs[slug].points.find(function (q) { return q.type === 'emplettes'; });
    }
    function libelles(menu) { return menu.items.map(function (q) { return q.libelle; }); }
"""


def _attendu(slug: str) -> list[str]:
    """Le menu SANS char garé devant : un commerce de l'auto le dit une fois, et ne propose ni pièce ni service."""
    comptoir = rayons.RAYONS.get(slug) or magasins.COMPTOIRS[slug]
    auto = [a for a in comptoir["articles"] if a.get("piece") or a.get("service")]
    return (["GARE UN CHAR DEVANT LA PORTE"] if auto else []) + [a["nom"].upper() for a in comptoir["articles"]
                                                                 if a not in auto]
# ⚠️ Un meuble s'affiche sous le nom du catalogue Beausoleil (« LE TÉLÉVISEUR ») : `_meuble` le prend tel quel.


def test_chaque_enseigne_decidee_vend_son_rayon_au_comptoir(banc):
    """Toutes les enseignes à comptoir, une par une, dans une pièce de leur famille : le menu porte l'enseigne
    et vend son rayon — ni plus, ni le comptoir de sa couleur."""
    genres = rayons.noms_des_enseignes()
    # ⚠️ Sans les rayons à SERVICES (vague 3) : leurs lignes se calculent (le prix des soins, le coffre) — ils ont leurs
    # juges à eux, plus bas.
    cas = [[nom, sorted(genres[nom])[0], slug] for nom, slug in sorted(rayons.ENSEIGNES.items())
           if slug not in rayons.POINTS and not any(a.get("service") for a in (rayons.RAYONS.get(slug) or {}).get("articles", []))
           and not genres[nom] & {"savoir", "service"}]       # le présentoir et le fauteuil : leurs juges, plus bas
    r = banc("""function (L) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, I = L.Monde.carte.def.interieurs, vus = {}, sans = [];
        B.partie.heure = 0.5;
        for (const [nom, genre] of %s) {
            const porte = portesDe(L, genre)[0];
            if (!porte) { sans.push(genre); continue; }
            B.interieur = Object.assign({}, I[porte.interieur], { nom: nom });
            const menu = L.Missions.menuDuPoint(pointDe(L, porte.interieur));
            vus[nom] = { titre: menu.titre, items: libelles(menu) };
        }
        B.interieur = null;
        return { vus: vus, sans: sans };
    }""" % (TROUVER, json.dumps(cas)))
    assert not r["sans"], f"aucune porte de ces familles dans la ville : {r['sans']}"
    faux = []
    for nom, _genre, slug in cas:
        vu = r["vus"][nom]
        if vu["titre"] != nom or vu["items"] != _attendu(slug):
            faux.append((nom, slug, vu))
    assert not faux, faux[:3]


def test_une_enseigne_en_attente_et_un_lieu_garanti_gardent_le_comptoir_de_leur_famille(banc):
    """La moitié qui empêche le juge d'au-dessus de passer à vide : sans rayon, rien ne change."""
    r = banc("""function (L) {
        %s
        L.Jeu.commencer();
        const B = L.B, I = L.Monde.carte.def.interieurs, porte = portesDe(L, 'commerce')[0];
        B.partie.heure = 0.5;
        B.interieur = Object.assign({}, I[porte.interieur], { nom: 'UNE ENSEIGNE INCONNUE' });
        const attente = libelles(L.Missions.menuDuPoint(pointDe(L, porte.interieur)));
        const dep = I.depanneur, pt = dep.points.find(function (q) { return q.type === 'emplettes'; });
        B.interieur = dep;
        const depanneur = libelles(L.Missions.menuDuPoint(pt));
        B.interieur = null;
        return { attente: attente, depanneur: depanneur };
    }""" % TROUVER)
    assert "UNE ENSEIGNE INCONNUE" not in rayons.ENSEIGNES   # (plus rien n'attend : un nom inconnu)
    assert r["attente"] == _attendu("commerce"), r
    assert all(n in r["depanneur"] for n in _attendu("bouffe")), r


def test_a_la_vraie_porte_d_une_boulangerie_action_achete_du_pain(banc):
    """Au BOUTON, par la vraie porte : on la renomme BOULANGERIE, on entre (`Jeu.entrer`, qui donne son nom à la
    pièce), on presse ACTION sur la première ligne — le pain est payé et mangé."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, porte = portesDe(L, 'bouffe')[0];
        const point = pointDe(L, porte.interieur);       // ⚠️ avant d'entrer : dedans, `Monde.carte` est la pièce
        porte.nom = 'BOULANGERIE';
        B.partie.heure = 0.5;
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
        L.Jeu.entrer(porte);
        for (let k = 0; k < 240 && (!B.interieur || B.transition); k++) o.frame(1);
        if (!B.interieur) return { dedans: false };
        if (B.transition) o.fondu();
        const faire = function () { return L.Missions.menuDuPoint(point); };
        const menu = faire();
        menu.refaire = faire;
        B.partie.argent = 100; j.vie = 10;
        L.Hud.ouvrirMenu(menu);
        menu.curseur = 0;
        const premier = menu.items[0].libelle;
        o.tape('KeyE', 2);
        const out = { dedans: true, nom: B.interieur.nom, premier: premier, argent: B.partie.argent, vie: j.vie };
        if (L.B.menu) L.Hud.fermerMenu();
        return out;
    }""" % TROUVER)
    assert r["dedans"], r
    assert r["nom"] == "BOULANGERIE" and r["premier"] == "PAIN DE MÉNAGE", r
    assert r["argent"] == 100 - rayons.BOUCHEES["pain"][0], r
    assert r["vie"] > 10, r


def test_aux_sports_action_achete_le_baton_et_au_magasin_de_bottes_on_les_enfile(banc):
    """Vague 2a, au BOUTON, par de vraies portes : aux SPORTS BEAULIEU, le bâton au prix de Gus fois la marge du
    rayon, et il est dans les mains ; aux BOTTES DE TRAVAIL, les bottes d'hiver payées, rangées et portées."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur;
        function acheter(genre, nom) {
            const porte = portesDe(L, genre)[0], point = pointDe(L, porte.interieur);
            porte.nom = nom;
            B.partie.heure = 0.5;
            j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
            L.Jeu.entrer(porte);
            for (let k = 0; k < 240 && (!B.interieur || B.transition); k++) o.frame(1);
            if (!B.interieur) return null;
            if (B.transition) o.fondu();
            B.partie.argent = 1000;                 // ⚠️ avant le menu : une ligne trop chère s'y écrit inactive
            const faire = function () { return L.Missions.menuDuPoint(point); };
            const menu = faire();
            menu.refaire = faire;
            L.Hud.ouvrirMenu(menu);
            menu.curseur = 0;
            const out = { nom: B.interieur.nom, premier: menu.items[0].libelle, detail: menu.items[0].detail };
            o.tape('KeyE', 2);
            out.argent = B.partie.argent;
            if (L.B.menu) L.Hud.fermerMenu();
            L.Jeu.sortir();
            for (let k = 0; k < 240 && (B.interieur || B.transition); k++) o.frame(1);
            return out;
        }
        const sports = acheter('commerce', 'SPORTS BEAULIEU');
        sports.arme = !!B.partie.armes.batte;
        const bottes = acheter('mode', 'BOTTES DE TRAVAIL');
        bottes.rangees = B.partie.tenues.indexOf('bottes_hiver') >= 0;
        bottes.pieds = B.partie.pieds;
        return { sports: sports, bottes: bottes };
    }""" % TROUVER)
    from app import armes
    baton = round(armes.par_slug("batte")["prix"] * rayons.RAYONS["sports"]["marge"])
    s, b = r["sports"], r["bottes"]
    assert s and s["nom"] == "SPORTS BEAULIEU" and s["premier"] == "BÂTON" and s["detail"] == f"{baton} $", s
    assert s["argent"] == 1000 - baton and s["arme"], s
    prix = next(t["prix"] for t in magasins.TENUES if t["slug"] == "bottes_hiver")
    assert b and b["nom"] == "BOTTES DE TRAVAIL" and b["premier"] == "BOTTES D'HIVER", b
    assert b["argent"] == 1000 - prix and b["rangees"] and b["pieds"] == "bottes_hiver", b


def test_aux_pneus_on_pose_les_pneus_d_hiver_sur_le_char_gare_devant(banc):
    """Vague 2b, au BOUTON, par une vraie porte renommée PNEUS DESCHAMPS : un char garé devant, ACTION sur la
    première ligne — les pneus d'hiver sont payés au prix de Ti-Guy et posés SUR CE CHAR ; à la PEINTURE AUTO, le
    même char repeint ; à la CARROSSERIE, cabossé, il repart neuf."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, porte = portesDe(L, 'industrie')[0], point = pointDe(L, porte.interieur);
        B.partie.heure = 0.5;
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
        const v = L.Vehicules.creer('auto', j.x + 24, j.y + 8, 0, { etat: 'stationne', couleur: '#c0392b' });
        L.Entites.indexer();
        function premier(nom, avant) {
            porte.nom = nom;
            j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
            L.Jeu.entrer(porte);
            for (let k = 0; k < 240 && (!B.interieur || B.transition); k++) o.frame(1);
            if (!B.interieur) return null;
            if (B.transition) o.fondu();
            if (avant) avant();
            B.partie.argent = 2000;                 // ⚠️ avant le menu : une ligne trop chère s'y écrit inactive
            const faire = function () { return L.Missions.menuDuPoint(point); };
            const menu = faire();
            menu.refaire = faire;
            L.Hud.ouvrirMenu(menu);
            menu.curseur = 0;
            const out = { libelle: menu.items[0].libelle, detail: menu.items[0].detail };
            o.tape('KeyE', 2);
            out.argent = B.partie.argent;
            if (L.B.menu) L.Hud.fermerMenu();
            L.Jeu.sortir();
            for (let k = 0; k < 240 && (B.interieur || B.transition); k++) o.frame(1);
            return out;
        }
        const pneus = premier('PNEUS DESCHAMPS');
        pneus.pose = !!(v.mods && v.mods.pneus);
        v.vole = true;
        const peinture = premier('PEINTURE AUTO');
        peinture.vole = v.vole;
        const carrosserie = premier('DÉBOSSELAGE', function () { v.vie = Math.round(v.vieMax / 2); });
        carrosserie.neuf = v.vie === v.vieMax;
        return { pneus: pneus, peinture: peinture, carrosserie: carrosserie };
    }""" % TROUVER)
    from app import economie, garage
    prix = next(q["prix"] for q in garage.PIECES if q["slug"] == "pneus")
    p, pe, c = r["pneus"], r["peinture"], r["carrosserie"]
    assert p and p["libelle"] == "POSER : PNEUS D'HIVER" and p["detail"] == f"{prix} $", p
    assert p["argent"] == 2000 - prix and p["pose"], p
    assert pe and pe["libelle"] == "REPEINDRE (EFFACE LE VOL)" and pe["argent"] == 2000 - economie.REPEINTE, pe
    assert pe["vole"] is False, pe
    assert c and c["libelle"] == "RÉPARER LE CHAR" and c["argent"] < 2000 and c["neuf"], c


def test_a_la_radio_tv_on_achete_le_televiseur_et_il_arrive_le_lendemain_a_la_planque(banc):
    """Vague 2c, au BOUTON, par une vraie porte renommée RADIO-TV DUMAS : le téléviseur payé au prix du catalogue,
    commandé pour la planque de Rocco — livré le lendemain, comme chez Gisèle."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        for (let k = 0; k < 5 && !L.Collections.catalogue(); k++) o.frame(1);
        const B = L.B, j = B.joueur, porte = portesDe(L, 'commerce')[0], point = pointDe(L, porte.interieur);
        porte.nom = 'RADIO-TV DUMAS';
        B.partie.heure = 0.5;
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
        L.Jeu.entrer(porte);
        for (let k = 0; k < 240 && (!B.interieur || B.transition); k++) o.frame(1);
        if (!B.interieur) return null;
        if (B.transition) o.fondu();
        B.partie.argent = 2000;
        const faire = function () { return L.Missions.menuDuPoint(point); };
        const menu = faire();
        menu.refaire = faire;
        L.Hud.ouvrirMenu(menu);
        menu.curseur = 0;
        const out = { libelle: menu.items[0].libelle, detail: menu.items[0].detail };
        o.tape('KeyE', 2);
        out.argent = B.partie.argent;
        out.apres = L.Missions.menuDuPoint(point).items[0].detail;
        out.livreAujourdhui = L.Decoration.livre('planque', 'televiseur');
        B.partie.jour += 1;
        out.livreDemain = L.Decoration.livre('planque', 'televiseur');
        if (L.B.menu) L.Hud.fermerMenu();
        return out;
    }""" % TROUVER)
    from app import decoration
    prix = next(m["prix"] for m in decoration.MEUBLES if m["slug"] == "televiseur")
    assert r and r["libelle"] == "LE TÉLÉVISEUR" and r["detail"] == f"{prix} $", r
    assert r["argent"] == 2000 - prix and r["apres"] == "LIVRÉ DEMAIN", r
    assert not r["livreAujourdhui"] and r["livreDemain"], r


def test_a_la_bijouterie_la_chaine_se_porte_au_cou_et_rosa_ne_la_vend_pas(banc):
    """Vague 2d, au BOUTON, par une vraie porte renommée BIJOUTERIE : la chaîne en or payée, rangée, portée AU COU
    (`partie.cou`) et dessinée (`Garderobe.duJoueur` : l'accessoire `chaine`) ; chez Rosa, elle n'est pas à vendre —
    elle n'y paraît qu'une fois à soi, pour la remettre."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, porte = portesDe(L, 'commerce')[0], point = pointDe(L, porte.interieur);
        const chezRosa = function () {
            return L.Missions.menuVetements().items.map(function (q) { return q.libelle; }).filter(function (l) {
                return l === 'CHAÎNE EN OR'; }).length;
        };
        const avant = chezRosa();
        porte.nom = 'BIJOUTERIE';
        B.partie.heure = 0.5;
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
        L.Jeu.entrer(porte);
        for (let k = 0; k < 240 && (!B.interieur || B.transition); k++) o.frame(1);
        if (!B.interieur) return null;
        if (B.transition) o.fondu();
        B.partie.argent = 1000;
        const faire = function () { return L.Missions.menuDuPoint(point); };
        const menu = faire();
        menu.refaire = faire;
        L.Hud.ouvrirMenu(menu);
        menu.curseur = 0;
        const out = { premier: menu.items[0].libelle, avant: avant };
        o.tape('KeyE', 2);
        if (L.B.menu) L.Hud.fermerMenu();
        out.argent = B.partie.argent;
        out.cou = B.partie.cou;
        out.accessoires = j.tenue.accessoires;
        out.apres = chezRosa();
        return out;
    }""" % TROUVER)
    prix = next(t["prix"] for t in magasins.TENUES if t["slug"] == "chaine_or")
    assert r and r["premier"] == "CHAÎNE EN OR" and r["argent"] == 1000 - prix, r
    assert r["cou"] == "chaine_or" and "chaine" in r["accessoires"], r
    assert r["avant"] == 0 and r["apres"] == 1, r


#: Entrer par une vraie porte de la famille `genre`, renommée `nom`, et ouvrir le menu de son point (le comptoir, ou
#: le fauteuil d'une pièce de service). `avant` : ce qu'on pose une fois dedans.
ENTRER = """
    function ouvrir(L, o, genre, nom, type, devant) {
        const B = L.B, j = B.joueur, I = L.Monde.carte.def.interieurs, c = L.Monde.carte;
        const porte = c.portes.find(function (p) {
            const piece = p.interieur && I[p.interieur];
            return piece && /^(nord_)?[a-z]+_\\d+$/.test(p.interieur)
                && (piece.points || []).some(function (q) { return q.type === type && (type !== 'emplettes' || q.genre === genre); });
        });
        if (!porte) return null;
        const point = I[porte.interieur].points.find(function (q) { return q.type === type; });
        porte.nom = nom;
        B.partie.heure = 0.5;
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
        if (devant) devant(j);                       // un char garé devant CETTE porte-ci
        L.Jeu.entrer(porte);
        for (let k = 0; k < 240 && (!B.interieur || B.transition); k++) o.frame(1);
        if (!B.interieur) return null;
        if (B.transition) o.fondu();
        return point;
    }
    function presser(L, o, point, ligne) {
        const B = L.B, faire = function () { return L.Missions.menuDuPoint(point); };
        const menu = faire();
        menu.refaire = faire;
        L.Hud.ouvrirMenu(menu);
        menu.curseur = menu.items.findIndex(function (q) { return q.libelle.indexOf(ligne) === 0; });
        const avant = { libelles: menu.items.map(function (q) { return q.libelle; }), curseur: menu.curseur };
        if (menu.curseur >= 0) o.tape('KeyE', 2);
        if (B.transition) o.fondu();
        if (L.B.menu) L.Hud.fermerMenu();
        return avant;
    }
    function sortir(L, o) {
        L.Jeu.sortir();
        for (let k = 0; k < 240 && (L.B.interieur || L.B.transition); k++) o.frame(1);
    }
"""


def test_les_services_au_bouton(banc):
    """Vague 3a, au BOUTON, par de vraies portes : la CLINIQUE soigne au PV manquant, la BUANDERIE fait lâcher une
    étoile, la BANQUE dépose au coffre de la planque (et plus de coupe de cheveux), les PRÊTS RAPIDES prennent un
    versement sur la dette, le PRÊT SUR GAGES rachète le couteau, l'HÔTEL fait dormir jusqu'au matin."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, p = B.partie, out = {};
        let pt = ouvrir(L, o, 'sante', 'CLINIQUE', 'emplettes');
        p.argent = 1000; j.vie = 40;
        out.clinique = presser(L, o, pt, 'TE FAIRE SOIGNER');
        out.clinique.vie = j.vie; out.clinique.argent = p.argent;
        sortir(L, o);
        pt = ouvrir(L, o, 'service', 'BUANDERIE', 'salon');
        p.argent = 1000; B.recherche.etoiles = 2;
        out.buanderie = presser(L, o, pt, 'LAVER TON LINGE');
        out.buanderie.etoiles = B.recherche.etoiles; out.buanderie.argent = p.argent;
        sortir(L, o);
        pt = ouvrir(L, o, 'service', 'BANQUE', 'salon');
        p.argent = 1000; p.planque.coffre = 0;
        out.banque = presser(L, o, pt, 'DÉPOSER 100 $');
        out.banque.coffre = p.planque.coffre; out.banque.argent = p.argent;
        sortir(L, o);
        pt = ouvrir(L, o, 'service', 'PRÊTS RAPIDES', 'salon');
        p.argent = 5000; const dette = p.dette;
        out.preteur = presser(L, o, pt, 'DONNER');
        out.preteur.avant = dette; out.preteur.apres = p.dette;
        sortir(L, o);
        pt = ouvrir(L, o, 'commerce', 'PRÊT SUR GAGES', 'emplettes');
        p.argent = 0; p.armes.couteau = { mun: null };
        out.gages = presser(L, o, pt, 'LAISSER COUTEAU');
        out.gages.couteau = !!p.armes.couteau; out.gages.argent = p.argent;
        sortir(L, o);
        pt = ouvrir(L, o, 'nuit', 'HÔTEL DES QUAIS', 'emplettes');
        p.argent = 1000; const jour = p.jour; j.vie = 10;
        out.hotel = presser(L, o, pt, 'DORMIR JUSQU');
        for (let k = 0; k < 400 && B.transition; k++) o.frame(1);
        out.hotel.jour = p.jour - jour; out.hotel.vie = j.vie; out.hotel.argent = p.argent;
        return out;
    }""" % ENTRER)
    from app import economie
    c, bu, ba, pr, g, h = (r[k] for k in ("clinique", "buanderie", "banque", "preteur", "gages", "hotel"))
    assert c["curseur"] >= 0 and c["vie"] == 100 and c["argent"] == 1000 - 30, c
    assert bu["curseur"] >= 0 and bu["etoiles"] == 1 and bu["argent"] == 1000 - 15, bu
    assert "BLOND" not in ba["libelles"] and ba["coffre"] == 100 and ba["argent"] == 900, ba
    assert pr["curseur"] >= 0 and pr["apres"] == pr["avant"] - economie.DETTE["acompte_min"], pr
    assert not g["couteau"] and g["argent"] == round(60 * rayons.GAGES), g
    assert h["jour"] == 1 and h["argent"] == 1000 - 40 * rayons.RAYONS["hotel"]["marge"], h


def test_les_autres_services_se_proposent_et_la_ferraille_achete_l_epave(banc):
    """Le reste de la vague 3a : les ASSURANCES et le LAVE-AUTO travaillent sur le char garé devant ; la FERRAILLE
    l'achète même en épave, et il quitte la rue ; le CLUB VIDÉO loue le film du soir ; le CLUB MAH-JONG ouvre la table
    de sic bo ; le MOTEL fait dormir jusqu'au soir."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, p = B.partie, out = {};
        function menu(genre, nom, type, devant) {
            const pt = ouvrir(L, o, genre, nom, type, devant);
            const libelles = L.Missions.menuDuPoint(pt).items.map(function (q) { return q.libelle; });
            return { pt: pt, libelles: libelles };
        }
        p.argent = 5000;
        // Un char garé devant la porte d'assurances : posé où le joueur sortira.
        const v = L.Vehicules.creer('auto', 0, 0, 0, { etat: 'stationne', couleur: '#c0392b' });
        v.x = 0; v.y = 0;
        function garer(j) { v.x = j.x + 24; v.y = j.y + 8; L.Entites.indexer(); }
        out.assurances = menu('service', 'ASSURANCES', 'salon').libelles; sortir(L, o);
        out.assurances2 = menu('service', 'ASSURANCES', 'salon', garer).libelles; sortir(L, o);
        out.lavage = menu('industrie', 'LAVE-AUTO', 'emplettes', garer).libelles; sortir(L, o);
        v.etat = 'epave';
        const f = menu('industrie', 'FERRAILLE', 'emplettes', garer);
        out.ferraille = presser(L, o, f.pt, 'VENDRE');
        out.ferraille.parti = B.exterieur.entites.indexOf(v) < 0;
        out.ferraille.argent = p.argent;
        sortir(L, o);
        out.video = menu('nuit', 'CLUB VIDÉO', 'emplettes').libelles; sortir(L, o);
        const mj = menu('nuit', 'CLUB MAH-JONG', 'emplettes');
        const m = L.Missions.menuDuPoint(mj.pt);
        L.Hud.ouvrirMenu(m);
        m.curseur = m.items.findIndex(function (q) { return q.libelle === 'LA TABLE DE SIC BO'; });
        o.tape('KeyE', 2);
        out.table = L.B.menu && L.B.menu !== m ? L.B.menu.titre : null;       // le menu de la table, pas le comptoir
        if (L.B.menu) L.Hud.fermerMenu();
        sortir(L, o);
        out.motel = menu('nuit', 'MOTEL LA POINTE', 'emplettes').libelles;
        return out;
    }""" % ENTRER)
    assert r["assurances"][0] == "GARE UN CHAR DEVANT LA PORTE", r["assurances"]
    assert r["assurances2"][0].startswith("ASSURER "), r["assurances2"]
    assert r["lavage"][0] == "LAVER LE CHAR (UNE ÉTOILE DE MOINS)", r["lavage"]
    assert r["ferraille"]["libelles"][0].endswith("À LA FERRAILLE") and r["ferraille"]["parti"], r["ferraille"]
    assert r["ferraille"]["argent"] > 5000, r["ferraille"]
    assert r["video"][0].startswith("LOUER UN FILM — "), r["video"]
    assert r["table"], r
    assert r["motel"][:2] == ["DORMIR JUSQU’AU MATIN", "DORMIR JUSQU’AU SOIR"], r["motel"]


def test_le_taxi_te_depose_devant_chez_rosa(banc):
    """Vague 3b, au BOUTON, par une vraie porte renommée TAXI DIAMANT : la course CHEZ ROSA payée à la distance, et l'on
    sort de la pièce devant la porte de la boutique, à l'autre bout de la ville."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, p = B.partie;
        const pt = ouvrir(L, o, 'service', 'TAXI DIAMANT', 'salon');
        if (!pt) return null;
        p.argent = 500;
        const avant = presser(L, o, pt, 'CHEZ ROSA');
        for (let k = 0; k < 400 && (B.interieur || B.transition); k++) o.frame(1);
        const rosa = L.Monde.carte.portes.find(function (q) { return q.lieu === 'vetements'; });
        return { avant: avant, dehors: !B.interieur, argent: p.argent,
                 loin: Math.hypot(j.x - (rosa.x * 16 + 8), j.y - (rosa.y + 1) * 16) };
    }""" % ENTRER)
    assert r and r["avant"]["curseur"] >= 0, r
    assert r["dehors"] and r["loin"] < 40, r
    assert rayons.TAXI_BASE < 500 - r["argent"] < 200, r


def test_le_phare_sur_la_pellicule_le_studio_le_developpe_et_rachete_la_photo(banc):
    """Vague 3c, au BOUTON : un déclic avec la porte du phare dans le cadre la met sur la pellicule ; au STUDIO LAU,
    DÉVELOPPER la fait entrer dans l'album, et la photo du jour se vend à la moitié du prix de Louise."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, p = B.partie, out = {};
        const phare = L.Monde.carte.portes.find(function (q) { return q.lieu === 'phare'; });
        B.photo = {};
        L.Photos.declic({ x: phare.x * 16 - 100, y: phare.y * 16 - 60 });
        out.pellicule = (p.pellicule || []).slice();
        out.dit = B.photo.dit;
        B.photo = null;
        const pt = ouvrir(L, o, 'service', 'STUDIO LAU', 'salon');
        p.argent = 100;
        p.photo = { sujet: 'feu', prix: 150, jour: p.jour - 3 };
        out.dev = presser(L, o, pt, 'DÉVELOPPER');
        out.album = Object.keys(p.album || {});
        out.argentDev = p.argent;
        out.rachat = presser(L, o, pt, 'VENDRE : ');
        out.argent = p.argent; out.photo = p.photo;
        return out;
    }""" % ENTRER)
    from app import photos
    assert r["pellicule"] == ["phare"] and "PHARE" in r["dit"], r
    assert "L’ALBUM DES LIEUX" in r["dev"]["libelles"] and r["album"] == ["phare"], r
    assert r["argentDev"] == 100 - photos.PHOTOGRAPHE["developper"], r
    assert r["argent"] == r["argentDev"] + 75 and r["photo"] is None, r


def test_le_portrait_se_tire_avec_la_tenue_du_jour_et_se_pose_au_mur_de_la_planque(banc):
    """Vague 3c, 2e partie, au BOUTON : au PHOTOGRAPHE, TON PORTRAIT payé et tiré avec la tenue du jour
    (`partie.portrait`) ; le lendemain, il est au mur de la planque de Rocco. Et l'album des lieux complet y pose son
    cadre."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        for (let k = 0; k < 5 && !L.Collections.catalogue(); k++) o.frame(1);
        const B = L.B, p = B.partie, out = {};
        const pt = ouvrir(L, o, 'service', 'PHOTOGRAPHE', 'salon');
        p.argent = 500;
        out.achat = presser(L, o, pt, 'TON PORTRAIT');
        out.argent = p.argent; out.portrait = p.portrait;
        out.aujourdhui = L.Decoration.presents('planque').indexOf('portrait') >= 0;
        p.jour += 1;
        out.demain = L.Decoration.presents('planque').indexOf('portrait') >= 0;
        out.cadreAvant = L.Decoration.presents('planque').indexOf('cadre_lieux') >= 0;
        p.album = {};
        B.defs.photos.album.forEach(function (a) { p.album[a[0]] = 1; });
        out.cadreApres = L.Decoration.presents('planque').indexOf('cadre_lieux') >= 0;
        out.chalet = L.Decoration.presents('chalet').indexOf('cadre_lieux') >= 0;
        return out;
    }""" % ENTRER)
    assert r["achat"]["curseur"] >= 0 and r["argent"] == 440, r
    assert r["portrait"] and r["portrait"]["haut"] and r["portrait"]["peau"], r
    assert not r["aujourdhui"] and r["demain"], r
    assert not r["cadreAvant"] and r["cadreApres"] and not r["chalet"], r


def test_la_soupe_pour_qui_est_casse_et_la_replique_de_l_ecole(banc):
    """Vague 3d, au BOUTON : à la MISSION DU PORT, cassé, un bol de soupe gratuit (une fois par jour) ; riche, il ne se
    sert pas. À l'ÉCOLE (le présentoir d'une pièce du savoir), plus de Clairon : RIEN À VENDRE ICI, et sa réplique."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, p = B.partie, out = {};
        let pt = ouvrir(L, o, 'sante', 'MISSION DU PORT', 'emplettes');
        p.argent = 500;
        out.riche = L.Missions.menuDuPoint(pt).items[0];
        p.argent = 3; j.vie = 30;
        out.casse = presser(L, o, pt, 'UN BOL DE SOUPE');
        out.vie = j.vie; out.argent = p.argent;
        out.deux = L.Missions.menuDuPoint(pt).items[0];
        sortir(L, o);
        pt = ouvrir(L, o, 'savoir', 'ÉCOLE', 'journal');
        const m = L.Missions.menuDuPoint(pt);
        out.ecole = { items: m.items.map(function (q) { return q.libelle; }), aide: m.aide };
        return out;
    }""" % ENTRER)
    assert r["riche"]["actif"] is False and r["riche"]["detail"] == "POUR CEUX QUI SONT CASSÉS", r
    assert r["casse"]["curseur"] >= 0 and r["vie"] > 30 and r["argent"] == 3, r
    assert r["deux"]["actif"] is False and r["deux"]["detail"] == "À DEMAIN", r
    assert r["ecole"]["items"] == ["RIEN À VENDRE ICI"], r
    assert r["ecole"]["aide"] == "« " + rayons.REPLIQUES["ÉCOLE"].upper() + " »", r


def test_au_barbier_de_la_ville_la_coupe_fait_oublier_ta_face(banc):
    """La vraie porte du BARBIER (`enseignes.ENSEIGNES`, Martin, 6 oct. 2026) : sans renommer quoi que ce soit, on y
    entre, et le fauteuil coupe les cheveux — la seule pièce de service de la ville à garder la coupe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, porte = L.Monde.carte.portes.find(function (q) { return q.lieu === 'barbier'; });
        if (!porte) return null;
        const point = L.Monde.carte.def.interieurs.barbier.points.find(function (q) { return q.type === 'salon'; });
        B.partie.heure = 0.5;
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
        L.Jeu.entrer(porte);
        for (let k = 0; k < 240 && (!B.interieur || B.transition); k++) o.frame(1);
        if (B.transition) o.fondu();
        return { nom: B.interieur && B.interieur.nom, items: L.Missions.menuDuPoint(point).items.map(function (q) { return q.libelle; }) };
    }""")
    assert r and r["nom"] == "BARBIER", r
    assert "BLOND" in r["items"] and "POIVRE ET SEL" in r["items"], r


def test_le_velo_devant_la_porte_le_grossiste_et_le_chantier_naval(banc):
    """Vague 4a, au BOUTON : à LOCATION VÉLOS, le vélo loué attend DANS LA RUE devant la porte (pas dans la pièce) ; au
    GROSSISTE, les caisses du char garé devant se vendent au prix du jour ; au CHANTIER NAVAL, le bateau amarré devant
    repart neuf."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, p = B.partie, out = {};
        let pt = ouvrir(L, o, 'commerce', 'LOCATION VÉLOS', 'emplettes');
        p.argent = 100;
        out.velo = presser(L, o, pt, 'LOUER UN VÉLO');
        out.dansLaPiece = B.entites.some(function (e) { return e.type === 'vehicule' && e.slug === 'velo'; });
        sortir(L, o);
        out.dehors = B.entites.some(function (e) { return e.type === 'vehicule' && e.slug === 'velo' && e.aToi
                                                     && Math.hypot(e.x - j.x, e.y - j.y) < 60; });
        out.argentVelo = p.argent;
        // Le vélo loué s'en va : la porte du grossiste est peut-être la même, et il passerait pour le char devant.
        B.entites.forEach(function (e) { if (e.slug === 'velo' && e.aToi) { e.x = 10; e.y = 10; } });
        const v = L.Vehicules.creer('auto', 0, 0, 0, { etat: 'stationne', couleur: '#c0392b' });
        const slug = Object.keys(B.defs.economie.contrebande.marchandises)[0];
        v.cargaison = {}; v.cargaison[slug] = 2;
        pt = ouvrir(L, o, 'commerce', 'GROSSISTE', 'emplettes', function (j) { v.x = j.x + 24; v.y = j.y + 8; L.Entites.indexer(); });
        p.argent = 0;
        out.grossiste = presser(L, o, pt, 'VENDRE 2 CAISSES');
        out.argentGros = p.argent; out.cargaison = v.cargaison[slug];
        sortir(L, o);
        const b = L.Vehicules.creer('bateau', 0, 0, 0, { etat: 'stationne', couleur: '#ecf0f1' });
        pt = ouvrir(L, o, 'marine', 'CHANTIER NAVAL', 'emplettes', function (j) { b.x = j.x + 40; b.y = j.y + 30; b.vie = 10; L.Entites.indexer(); });
        p.argent = 5000;
        out.chantier = presser(L, o, pt, 'RÉPARER LE BATEAU');
        out.neuf = b.vie === b.vieMax;
        return out;
    }""" % ENTRER)
    assert r["velo"]["curseur"] >= 0 and not r["dansLaPiece"] and r["dehors"] and r["argentVelo"] == 92, r
    assert r["grossiste"]["curseur"] >= 0 and r["argentGros"] > 0 and r["cargaison"] == 0, r["grossiste"]
    assert r["chantier"]["curseur"] >= 0 and r["neuf"], r


def test_les_rayons_arrivent_par_leur_propre_requete(banc):
    """Les rayons voyagent seuls (`/api/rayons`, 6 oct. 2026) : partis d'un paquet NU, le jeu va les chercher, et la
    BOULANGERIE vend son pain une fois qu'ils sont là — avant, elle sert le comptoir de son genre, sans planter."""
    r = banc("""function (L, o) {
        %s
        const B = L.B;
        const avant = !!B.defs.rayons;
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        for (let k = 0; k < 10 && !L.Suite.rayons.arrivee(); k++) o.frame(1);
        const pt = ouvrir(L, o, 'bouffe', 'BOULANGERIE', 'emplettes');
        return { avant: avant, arrivee: L.Suite.rayons.arrivee(),
                 items: L.Missions.menuDuPoint(pt).items.map(function (q) { return q.libelle; }) };
    }""" % ENTRER, poser_la_suite=False)
    # (`avant` : la demande arrive avant même la première image du banc, comme celle de la suite.)
    assert r["arrivee"], r
    assert r["items"][0] == "PAIN DE MÉNAGE", r


def test_la_lanterne_va_dans_la_piece_d_en_arriere(banc):
    """Vague 4b, au BOUTON : chez LANTERNES FUNG, la lanterne payée, livrée le lendemain dans la pièce d'en arrière
    (pas dans la planque, pleine) ; par la vraie planque, le passage y mène, et elle y pend au mur."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        for (let k = 0; k < 5 && !L.Collections.catalogue(); k++) o.frame(1);
        const B = L.B, j = B.joueur, p = B.partie, out = {};
        const pt = ouvrir(L, o, 'commerce', 'LANTERNES FUNG', 'emplettes');
        p.argent = 500;
        out.achat = presser(L, o, pt, 'LA LANTERNE');
        out.argent = p.argent;
        sortir(L, o);
        p.jour += 1;
        out.arriere = L.Decoration.presents('planque_arriere');
        out.planque = L.Decoration.presents('planque');
        const porte = L.Monde.carte.portes.find(function (q) { return q.lieu === 'planque'; });
        j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 10;
        L.Jeu.entrer(porte);
        for (let k = 0; k < 240 && (!B.interieur || B.transition); k++) o.frame(1);
        if (B.transition) o.fondu();
        const passage = B.interieur.points.find(function (q) { return q.type === 'escalier'; });
        j.x = passage.x * 16 + 8; j.y = passage.y * 16 + 8;
        L.Missions.majInvite(j);
        out.invite = B.invite;
        L.Missions.utiliserPoint(j);
        for (let k = 0; k < 240 && B.transition; k++) o.frame(1);
        if (B.transition) o.fondu();
        out.piece = B.interieur && B.interieur.slug;
        out.decors = B.entites.filter(function (e) { return e.deLaPlanque; }).map(function (e) { return e.decor; });
        return out;
    }""" % ENTRER)
    assert r["achat"]["curseur"] >= 0 and r["argent"] == 420, r
    assert r["arriere"] == ["lanterne"] and "lanterne" not in r["planque"], r
    assert r["invite"] == "LA PIÈCE D’EN ARRIÈRE" and r["piece"] == "planque_arriere", r
    assert r["decors"] == ["lanterne"], r


def test_les_disques_un_a_la_fois_et_le_tatouage(banc):
    """Vague 4c, au BOUTON : chez DISQUES VOGUE, le premier titre, puis le deuxième — dans l'ordre ; la collection
    complète pose la discothèque à la pièce d'en arrière. Au TATOUAGE, la police oublie ta face, et l'encre se voit."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        for (let k = 0; k < 5 && !L.Collections.catalogue(); k++) o.frame(1);
        const B = L.B, j = B.joueur, p = B.partie, out = {};
        let pt = ouvrir(L, o, 'savoir', 'DISQUES VOGUE', 'journal');
        p.argent = 500;
        const titres = B.defs.rayons.collections.disques;
        out.un = presser(L, o, pt, titres[0].toUpperCase());
        out.deux = presser(L, o, pt, titres[1].toUpperCase());
        out.n = p.collectionsDesComptoirs.disques;
        out.avant = L.Decoration.presents('planque_arriere').indexOf('discotheque') >= 0;
        p.collectionsDesComptoirs.disques = 12;
        out.apres = L.Decoration.presents('planque_arriere').indexOf('discotheque') >= 0;
        out.fini = L.Missions.menuDuPoint(pt).items.map(function (q) { return q.libelle; });
        sortir(L, o);
        pt = ouvrir(L, o, 'mode', 'TATOUAGE', 'emplettes');
        p.argent = 500; B.recherche.etoiles = 2; B.recherche.chaleur = 300;
        out.tatou = presser(L, o, pt, 'TE FAIRE TATOUER');
        out.etoiles = B.recherche.etoiles; out.encre = j.tenue.accessoires.indexOf('tatouage') >= 0;
        out.encore = L.Missions.menuDuPoint(pt).items[0].libelle;
        return out;
    }""" % ENTRER)
    assert r["un"]["curseur"] >= 0 and r["deux"]["curseur"] >= 0 and r["n"] == 2, r
    assert not r["avant"] and r["apres"] and "TU LES AS TOUS" in r["fini"], r
    assert r["tatou"]["curseur"] >= 0 and r["etoiles"] == 0 and r["encre"], r
    assert r["encore"] == "TU AS DÉJÀ LE TIEN", r


def test_le_bouquet_offert_achete_un_temoin_de_moins(banc):
    """Vague 4c, 2e partie, au BOUTON : chez le FLEURISTE, un bouquet ; dehors, devant un passant ordinaire, l'invite
    dit OFFRIR LE BOUQUET, ACTION le lui donne — et ce passant-là ne te dénoncera plus (`Reputation.denonce`)."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        const B = L.B, j = B.joueur, p = B.partie, out = {};
        const pt = ouvrir(L, o, 'commerce', 'FLEURISTE', 'emplettes');
        p.argent = 100;
        out.achat = presser(L, o, pt, 'UN BOUQUET');
        out.cadeaux = Object.assign({}, p.cadeaux);
        sortir(L, o);
        const arch = L.Entites.archetype('passant') || L.Entites.archetype('client');
        const e = L.Entites.creerPieton(j.x, j.y + 14, arch);
        e.etat = 'fige'; e.metier = null; e.gang = null;
        j.face = 'bas'; j.angle = Math.PI / 2;
        L.Missions.majInvite(j);
        out.invite = B.invite;
        out.avant = L.Reputation.denonce(e, 0, e.x, e.y);
        o.tape('KeyE', 2);
        out.ami = !!e.ami; out.reste = p.cadeaux.bouquet;
        out.apres = L.Reputation.denonce(e, 0, e.x, e.y);
        return out;
    }""" % ENTRER)
    assert r["achat"]["curseur"] >= 0 and r["cadeaux"] == {"bouquet": 1}, r
    assert r["invite"] == "OFFRIR LE BOUQUET", r
    assert r["ami"] and r["reste"] == 0, r
    assert r["apres"] is False, r
