"""Le camion de crème glacée, au banc (docs/jalons/le-camion-de-creme-glacee.md).

Il attend garé dans la rue du dépanneur des Érables, et naît quand on approche ; au klaxon, sa
tournée ; sa ritournelle joue quand il roule et se tait quand il s'arrête ; les enfants à vélo le
suivent sans jamais toucher la rue ; et la police le soupçonne moins, tant qu'on n'y tire pas.
"""

from app import economie, vehicules

#: Le joueur à 300 px de la place du camion (hors champ), et les images qu'il faut pour qu'il naisse.
APPROCHE = """
  function approcher(L, o) {
    const B = L.B, j = B.joueur, M = L.Missions;
    const place = M.placeDuCamion();
    j.x = place.x + 300; j.y = place.y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
    for (let k = 0; k < 130; k++) o.frame(1);
    return B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'creme_glacee'; });
  }
  function auVolant(L, o) {
    const c = approcher(L, o)[0], j = L.B.joueur;
    L.Vehicules.monter(j, c);
    return c;
  }
"""


def test_il_attend_gare_pres_du_depanneur_et_nait_quand_on_approche(banc):
    r = banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const B = L.B;
        const auDemarrage = B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'creme_glacee'; }).length;
        const camions = approcher(L, o);
        for (let k = 0; k < 130; k++) o.frame(1);
        const encore = B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'creme_glacee'; }).length;
        const c = camions[0], place = L.Missions.placeDuCamion();
        return { auDemarrage: auDemarrage, n: camions.length, encore: encore, gare: c && c.etat,
                 pres: c ? Math.round(Math.hypot(c.x - place.x, c.y - place.y)) : null };
    }""")
    assert r["auDemarrage"] == 0, "il est né au démarrage : un identifiant de plus pour toute la partie"
    assert r["n"] == 1 and r["encore"] == 1, r
    assert r["gare"] == "stationne" and r["pres"] < 16, r


def test_au_klaxon_la_tournee_et_la_ritournelle_quand_il_roule(banc):
    r = banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions;
        const demandes = [];
        const vrai = L.Son.Rue.demander;
        L.Son.Rue.demander = function (slug, v) { demandes.push(slug); return vrai.apply(null, arguments); };
        const c = auVolant(L, o);
        o.tape('KeyJ', 2);
        const tournee = { slug: M.boulot.slug, etape: M.boulot.etape, dest: M.boulot.destination };
        // A l'arret : silence.
        c.vitesse = 0; c.vx = 0; c.vy = 0;
        demandes.length = 0; o.frame(10);
        const arret = demandes.filter(function (s) { return s === 'creme_glacee'; }).length;
        // En roulant : la ritournelle.
        c.vitesse = 1.5; c.vx = 1.5;
        demandes.length = 0; for (let k = 0; k < 10; k++) { c.vitesse = 1.5; o.frame(1); }
        const roule = demandes.filter(function (s) { return s === 'creme_glacee'; }).length;
        // Au premier arret, une vente.
        const argent = B.partie.argent;
        c.x = M.boulot.destination.x; c.y = M.boulot.destination.y; c.vitesse = 0; c.vx = 0; c.vy = 0;
        L.Entites.indexer(); o.frame(3);
        return { tournee: tournee, arret: arret, roule: roule, vente: B.partie.argent - argent, etapes: M.boulot.etapesFaites };
    }""")
    assert r["tournee"]["slug"] == "creme_glacee" and r["tournee"]["etape"] == "route" and r["tournee"]["dest"], r
    assert r["arret"] == 0, "la ritournelle joue à l'arrêt"
    assert r["roule"] >= 8, "la ritournelle ne joue pas quand il roule"
    assert r["vente"] > 0 and r["etapes"] == 1, r


def test_les_enfants_a_velo_suivent_la_ritournelle_sans_toucher_la_rue(banc):
    r = banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, Mo = L.Monde;
        const c = auVolant(L, o);
        o.tape('KeyJ', 2);
        // Un enfant a velo sur un trottoir, a 150 px.
        let place = null;
        for (let r = 4; r < 14 && !place; r++) for (let dx = -r; dx <= r && !place; dx++) {
            const tx = Math.floor(c.x / 16) + dx, ty = Math.floor(c.y / 16) - r;
            if (Mo.estTrottoir(tx, ty)) place = { x: tx * 16 + 8, y: ty * 16 + 8 };
        }
        const e = L.Entites.creerPieton(place.x, place.y, L.Entites.archetype('enfant_velo'));
        L.Entites.indexer();
        c.vitesse = 1.2; c.vx = 1.2;
        let surLaRue = 0;
        for (let k = 0; k < 400; k++) {
            c.vitesse = 1.2;
            o.frame(1);
            if (Mo.estChaussee(Math.floor(e.x / 16), Math.floor(e.y / 16))) surLaRue++;
        }
        return { suit: !!e.poste, poste: e.poste ? Math.round(Math.hypot(e.poste.x - c.x, e.poste.y - c.y)) : null,
                 surLaRue: surLaRue, vivant: e.vivant };
    }""")
    assert r["suit"], "l'enfant n'entend pas la ritournelle"
    assert r["poste"] is not None and r["poste"] < 80, r
    assert r["surLaRue"] == 0, f"l'enfant a roulé {r['surLaRue']} images sur la chaussée"
    assert r["vivant"]


def test_la_police_le_soupconne_moins_tant_qu_on_n_y_tire_pas(banc):
    """Le même délit, vu : dans le camion, la moitié de la chaleur ; une arme sortie, toute."""
    r = banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const B = L.B, P = L.Police;
        const c = auVolant(L, o);
        function chaleur(type) {
            B.recherche.chaleur = 0; B.recherche.redites = {};
            P.signalerCrime(type, B.joueur.x, B.joueur.y, true);
            return B.recherche.chaleur;
        }
        const dansLeCamion = chaleur('carjacking'), armeDansLeCamion = chaleur('arme_sortie');
        L.Vehicules.descendre(B.joueur, true);
        const aPied = chaleur('carjacking');
        return { dansLeCamion: dansLeCamion, aPied: aPied, arme: armeDansLeCamion, armeAPied: chaleur('arme_sortie') };
    }""")
    part = vehicules.par_slug("creme_glacee")["discret"]
    assert abs(r["dansLeCamion"] - r["aPied"] * part) < 0.01, r
    assert r["arme"] == r["armeAPied"], "une arme sortie dans le camion chauffe moins"


def test_la_tournee_tient_l_economie():
    f = economie.BOULOTS["creme_glacee"]
    taxi = economie.gain_boulot(economie.BOULOTS["taxi"])
    assert taxi <= economie.gain_boulot(f) <= 4 * taxi
    assert vehicules.par_slug("creme_glacee")["frequence"] == 0, "il ne roule pas dans le trafic"
