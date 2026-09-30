"""Le camion de crème glacée, au banc (docs/jalons/le-camion-de-creme-glacee.md).

Il attend garé hors de la rue, à côté du dépanneur des Érables, et naît quand on approche ; au klaxon, sa
tournée ; sa ritournelle joue quand il roule et se tait quand il s'arrête ; les enfants à vélo le
suivent sans jamais toucher la rue ; et la police le soupçonne moins, tant qu'on n'y tire pas.
"""

import pytest

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


@pytest.fixture(scope="module")
def camion_puis_tournee(banc):
    """UN banc : on approche (il naît, garé), on le regarde encore 130 images — puis on monte, et
    c'est la tournée.

    ⚠️ La 1re partie ne fait que LIRE : le camion est né par `approcher` et on n'y touche pas.
    La 2e trouvait, dans son banc, le même camion né et garé par le même `approcher` — on y monte
    directement, au lieu d'approcher une seconde fois."""
    return banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions;
        const auDemarrage = B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'creme_glacee'; }).length;
        const camions = approcher(L, o);
        for (let k = 0; k < 130; k++) o.frame(1);
        const encore = B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'creme_glacee'; }).length;
        const c = camions[0], place = M.placeDuCamion();
        // Son emprise : les quatre coins et le milieu de ses flancs, sur la carte et contre le decor.
        const L2 = 15, l2 = 7.5, ca = Math.cos(c.angle), sa = Math.sin(c.angle), surLaRue = [], touche = [];
        for (const [u, w] of [[L2, l2], [L2, -l2], [-L2, l2], [-L2, -l2], [0, l2], [0, -l2], [0, 0]]) {
            const x = c.x + u * ca - w * sa, y = c.y + u * sa + w * ca;
            if (L.Monde.estRoute(Math.floor(x / 16), Math.floor(y / 16))) surLaRue.push([Math.round(x), Math.round(y)]);
        }
        for (const e of B.entites) {
            if (e === c || !{ decor: 1, panneau: 1, feu: 1, stop: 1 }[e.type]) continue;
            const u = (e.x - c.x) * ca + (e.y - c.y) * sa, w = -(e.x - c.x) * sa + (e.y - c.y) * ca;
            if (Math.abs(u) < L2 + (e.r || 4) && Math.abs(w) < l2 + (e.r || 4)) touche.push(e.decor || e.type);
        }
        const nait = { auDemarrage: auDemarrage, n: camions.length, encore: encore, gare: c && c.etat,
                       pres: c ? Math.round(Math.hypot(c.x - place.x, c.y - place.y)) : null,
                       surLaRue: surLaRue, touche: touche,
                       porte: Math.round(Math.hypot(c.x - (L.Histoire.lieu('depanneur') || {}).x, c.y - (L.Histoire.lieu('depanneur') || {}).y)) };
        // --- La tournee, au volant du meme camion.
        const demandes = [];
        const vrai = L.Son.Rue.demander;
        L.Son.Rue.demander = function (slug, v) { demandes.push(slug); return vrai.apply(null, arguments); };
        L.Vehicules.monter(B.joueur, c);
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
        return { nait: nait,
                 tournee: { tournee: tournee, arret: arret, roule: roule, vente: B.partie.argent - argent, etapes: M.boulot.etapesFaites } };
    }""")


def test_il_attend_gare_pres_du_depanneur_et_nait_quand_on_approche(camion_puis_tournee):
    r = camion_puis_tournee["nait"]
    assert r["auDemarrage"] == 0, "il est né au démarrage : un identifiant de plus pour toute la partie"
    assert r["n"] == 1 and r["encore"] == 1, r
    assert r["gare"] == "stationne" and r["pres"] < 16, r


def test_il_attend_hors_de_la_chaussee_sans_toucher_le_decor(camion_puis_tournee):
    """Martin (30 sept. 2026) : garé dans la voie devant Ti-Paul, il bloquait le trafic. Aucun coin de
    son emprise sur la chaussée, aucun décor sous lui — et il reste à côté du dépanneur."""
    r = camion_puis_tournee["nait"]
    assert not r["surLaRue"], f"le camion attend sur la chaussée : {r['surLaRue']}"
    assert not r["touche"], f"le camion attend dans le décor : {r['touche']}"
    assert r["porte"] < 12 * 16, f"le camion attend à {r['porte']} px du dépanneur"


@pytest.fixture(scope="module")
def sortie_du_camion(banc):
    """UN banc : on approche, on monte, et on écrase l'accélérateur (le bouton, pas `vitesse`)."""
    return banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const Mo = L.Monde, c = auVolant(L, o), x0 = c.x, y0 = c.y;
        let rue = -1;
        o.touche('KeyW');
        for (let k = 0; k < 90 && rue < 0; k++) {
            o.frame(1);
            if (Mo.estRoute(Math.floor(c.x / 16), Math.floor(c.y / 16))) rue = k;
        }
        o.relacher('KeyW');
        return { rue: rue, parcouru: Math.round(Math.hypot(c.x - x0, c.y - y0)), vie: c.vie, vieMax: c.vieMax };
    }""")


def test_il_rejoint_la_rue_tout_droit(sortie_du_camion):
    """Garé hors de la chaussée, il doit en sortir d'un coup d'accélérateur, le nez devant."""
    r = sortie_du_camion
    assert r["rue"] >= 0, f"à l'accélérateur, le camion n'atteint pas la rue : {r}"
    assert r["vie"] == r["vieMax"], f"le camion a cogné quelque chose en sortant : {r}"


def test_au_klaxon_la_tournee_et_la_ritournelle_quand_il_roule(camion_puis_tournee):
    r = camion_puis_tournee["tournee"]
    assert r["tournee"]["slug"] == "creme_glacee" and r["tournee"]["etape"] == "route" and r["tournee"]["dest"], r
    assert r["arret"] == 0, "la ritournelle joue à l'arrêt"
    assert r["roule"] >= 8, "la ritournelle ne joue pas quand il roule"
    assert r["vente"] > 0 and r["etapes"] == 1, r


@pytest.fixture(scope="module")
def enfants_puis_police(banc):
    """UN banc : au volant, la tournée et un enfant à vélo qui la suit — puis, toujours au volant du
    camion, ce que la police en pense.

    ⚠️ La police se lit en posant la chaleur à zéro avant chaque délit (`chaleur`), comme son juge
    le faisait ; on remet aussi les étoiles et les crimes, que 400 images de tournée auraient pu
    laisser. Le camion est le même : on n'approche pas une seconde fois."""
    return banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, Mo = L.Monde, P = L.Police;
        const c = auVolant(L, o);
        // La tournee se juge DANS LA RUE du depanneur, qu'il longe dans le sens de sa voie : garé sur l'allée d'a cote, pousse
        // tout droit, il traverserait les terrains et l'enfant, sur son trottoir, le perdrait.
        const lieu = L.Histoire.lieu('depanneur'), rue = L.Histoire.tuileDeRue(lieu.x, lieu.y, 10);
        c.x = rue.x; c.y = rue.y; c.angle = { '>': 0, 'v': Math.PI / 2, '<': Math.PI, '^': -Math.PI / 2 }[rue.sens]; L.Entites.indexer();
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
        const enfants = { suit: !!e.poste, poste: e.poste ? Math.round(Math.hypot(e.poste.x - c.x, e.poste.y - c.y)) : null,
                          surLaRue: surLaRue, vivant: e.vivant };
        // --- La police : le meme delit, vu, dans le camion puis a pied.
        c.vitesse = 0; c.vx = 0; c.vy = 0;
        if (B.joueur.dansVehicule !== c) L.Vehicules.monter(B.joueur, c);
        B.recherche.etoiles = 0; B.crimes.length = 0;
        function chaleur(type) {
            B.recherche.chaleur = 0; B.recherche.redites = {};
            P.signalerCrime(type, B.joueur.x, B.joueur.y, true);
            return B.recherche.chaleur;
        }
        const dansLeCamion = chaleur('carjacking'), armeDansLeCamion = chaleur('arme_sortie');
        L.Vehicules.descendre(B.joueur, true);
        const aPied = chaleur('carjacking');
        return { enfants: enfants,
                 police: { dansLeCamion: dansLeCamion, aPied: aPied, arme: armeDansLeCamion, armeAPied: chaleur('arme_sortie') } };
    }""")


def test_les_enfants_a_velo_suivent_la_ritournelle_sans_toucher_la_rue(enfants_puis_police):
    r = enfants_puis_police["enfants"]
    assert r["suit"], "l'enfant n'entend pas la ritournelle"
    assert r["poste"] is not None and r["poste"] < 80, r
    assert r["surLaRue"] == 0, f"l'enfant a roulé {r['surLaRue']} images sur la chaussée"
    assert r["vivant"]


def test_la_police_le_soupconne_moins_tant_qu_on_n_y_tire_pas(enfants_puis_police):
    """Le même délit, vu : dans le camion, la moitié de la chaleur ; une arme sortie, toute."""
    r = enfants_puis_police["police"]
    part = vehicules.par_slug("creme_glacee")["discret"]
    assert abs(r["dansLeCamion"] - r["aPied"] * part) < 0.01, r
    assert r["arme"] == r["armeAPied"], "une arme sortie dans le camion chauffe moins"


def test_la_tournee_tient_l_economie():
    # « Entre le taxi et quatre fois le taxi » : `test_economie::test_chaque_boulot_vaut_la_peine…`
    # le juge pour CHAQUE boulot — à condition que la tournée en soit un.
    assert "creme_glacee" in economie.BOULOTS
    assert vehicules.par_slug("creme_glacee")["frequence"] == 0, "il ne roule pas dans le trafic"
