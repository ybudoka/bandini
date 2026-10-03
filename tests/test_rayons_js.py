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
    comptoir = rayons.RAYONS.get(slug) or magasins.COMPTOIRS[slug]
    return [a["nom"].upper() for a in comptoir["articles"]]


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
