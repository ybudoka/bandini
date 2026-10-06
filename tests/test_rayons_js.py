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


def test_chaque_enseigne_decidee_vend_son_rayon_au_comptoir(banc):
    """Toutes les enseignes à comptoir, une par une, dans une pièce de leur famille : le menu porte l'enseigne
    et vend son rayon — ni plus, ni le comptoir de sa couleur."""
    genres = rayons.noms_des_enseignes()
    cas = [[nom, sorted(genres[nom])[0], slug] for nom, slug in sorted(rayons.ENSEIGNES.items())
           if slug not in rayons.POINTS]
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
        B.interieur = Object.assign({}, I[porte.interieur], { nom: 'BIJOUTERIE' });
        const attente = libelles(L.Missions.menuDuPoint(pointDe(L, porte.interieur)));
        const dep = I.depanneur, pt = dep.points.find(function (q) { return q.type === 'emplettes'; });
        B.interieur = dep;
        const depanneur = libelles(L.Missions.menuDuPoint(pt));
        B.interieur = null;
        return { attente: attente, depanneur: depanneur };
    }""" % TROUVER)
    assert "BIJOUTERIE" in rayons.EN_ATTENTE
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
