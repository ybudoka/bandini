"""Les zones conditionnelles, cote navigateur : le pont arrete un char et pas
un pieton tant que m2 n'est pas faite, un char lance pousse les cones et le
paie en degats, la cour de l'usine ferme la nuit (on pousse, on enjambe,
l'etoile tombe a la retombee — et on ressort librement), le trafic fait
demi-tour au lieu de s'empiler, et le carnet liste ce qui est ferme."""

from app import carte


def test_le_pont_arrete_les_chars_et_pas_les_jambes_avant_m2(banc, paquet):
    pont = next(b for b in carte.BARRIERES if b["slug"] == "pont")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, b = L.Monde.carte.def.barrieres.find(function (q) { return q.slug === 'pont'; });
        const x = (b.x + 1) * TT + 8;                      // la voie qui descend
        const out = { fermee: L.Monde.barriereFermee(b) };
        // ⚠️ LE TRAFIC DU HASARD N'EST PAS CE QU'ON JUGE. Un camion rentrait dans
        // le char au depart et un velo au milieu du pont : vingt-quatre points de
        // carrosserie, alors que le juge compte au point pres ce que la barriere
        // coute. Il tenait par chance de graine — livrer le lot du poste a change
        // trois meubles a l'autre bout de la ville, le trafic est tombe ailleurs,
        // et ce juge est tombe avec. On coupe les naissances et on vide la rue.
        L.B.defs.conduite.trafic.vehicules_max = 0;
        function vider() {
            L.B.entites.filter(function (e) {
                return e !== j && e !== j.dansVehicule && (e.type === 'vehicule' || e.type === 'pieton');
            }).forEach(function (e) { L.Entites.retirer(e); });
        }
        function partir(y) { vider(); j.x = x; j.y = y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer(); }
        // 1. Au pas : le char se bute aux cones, et le HUD dit pourquoi.
        partir((b.y - 3) * TT);
        let v = L.Vehicules.creer('auto', x, j.y, Math.PI / 2, { etat: 'stationne' }); L.Entites.indexer();
        L.Vehicules.monter(j, v);
        v.vitesse = 1.0; v.vx = 0; v.vy = 1.0;
        for (let i = 0; i < 90; i++) { v.vitesse = Math.max(v.vitesse, 0.9); v.vy = Math.max(v.vy, 0.9); o.frame(1); }
        out.lent = { y: v.y / TT, msg: L.B.msg, vie: v.vie };
        L.Vehicules.descendre(j, true); L.Entites.retirer(v);
        // 2. Lance : il pousse les cones, y laisse des degats, et traverse.
        partir((b.y - 8) * TT);
        v = L.Vehicules.creer('auto', x, j.y, Math.PI / 2, { etat: 'stationne' }); L.Entites.indexer();
        L.Vehicules.monter(j, v);
        // ⚠️ On lache le gaz DES QU'ON A TRAVERSE : tenu 360 images, le char
        // finissait dans un mur trois rues plus loin, et c'est ce mur qu'on
        // aurait compte dans les degats des cones.
        function traverser() {
            o.touche('KeyW');
            for (let i = 0; i < 40 * (b.h + 12) && v.y < (b.y + b.h + 1) * TT; i++) o.frame(1);
            o.relacher('KeyW');
        }
        traverser();
        out.lance = { y: v.y / TT, vie: v.vie, vieMax: v.vieMax };
        // ⚠️ ET LE DERNIER ESSAI SE FAIT AU PAS, comme le premier. Plein gaz sur
        // douze tuiles, le char derive d'une demi-tuile et racle le garde-fou du
        // pont : des points de carrosserie qui n'ont rien a voir avec la
        // barriere. Le juge tenait par chance de graine — retirer trois meubles
        // a l'autre bout de la ville (le lot du poste) le faisait tomber.
        L.Vehicules.descendre(j, true); L.Entites.retirer(v);
        // 3. A pied : les jambes passent.
        partir((b.y - 2) * TT); j.x = b.x * TT + 8;       // le trottoir du pont
        o.touche('KeyS'); o.frame(150); o.relacher('KeyS');
        out.pied = { y: j.y / TT };
        // 4. Le carnet la liste ; m2 faite, elle s'ouvre et le carnet se tait.
        // ⚠️ LA ligne du pont, pas « une ligne FERMÉ » : le quai du cargo est
        // ferme le jour, et il est midi.
        const lignePont = function () { return L.Missions.menuCasier().items.some(function (i) { return i.libelle === 'FERMÉ — ' + b.nom.toUpperCase() && i.detail === b.raison; }); };
        out.carnetAvant = lignePont();
        L.B.partie.missionsFaites.m2 = true;
        out.ouverte = !L.Monde.barriereFermee(b);
        out.carnetApres = lignePont();
        partir((b.y - 3) * TT);
        v = L.Vehicules.creer('auto', x, j.y, Math.PI / 2, { etat: 'stationne' }); L.Entites.indexer();
        L.Vehicules.monter(j, v);
        v.vitesse = 1.0; v.vx = 0; v.vy = 1.0;
            // ⚠️ Le budget d'images suit la LONGUEUR DU PONT : 300 images faisaient
            // onze tuiles de tablier, pas vingt-quatre (17 sept. 2026, le chenal
            // élargi). À 0,9 px par image, il faut une quarantaine d'images par
            // tuile, et de quoi prendre son élan de chaque côté.
        for (let i = 0; i < 40 * (b.h + 6) && v.y < (b.y + b.h + 1) * TT; i++) {
            v.vitesse = Math.max(v.vitesse, 0.9); v.vy = Math.max(v.vy, 0.9); v.vx = 0;
            o.frame(1);
        }
        out.apres = { y: v.y / TT, vie: v.vie };
        out.b = { y: b.y, h: b.h };
        return out;
    }""")
    b = r["b"]
    # ⚠️ La fiche doit COUTER quelque chose, sinon le juge compare zero a zero :
    # il relit `forcer.degats` pour son attendu, et une fiche a zero le rendait
    # vert (mutation du 17 sept. 2026).
    assert pont["forcer"]["degats"] > 0, pont
    assert r["fermee"] is True
    assert r["lent"]["y"] < b["y"] + 0.5, f"au pas, le char est entre sur le pont : {r['lent']}"
    assert r["lent"]["msg"] == pont["raison"], r["lent"]
    assert r["lent"]["vie"] == r["lance"]["vieMax"], "se buter aux cones ne coute rien"
    assert r["lance"]["y"] > b["y"] + b["h"], f"lance, le char n'a pas traverse : {r['lance']}"
    assert r["lance"]["vie"] == r["lance"]["vieMax"] - pont["forcer"]["degats"], "forcer coute les degats de la fiche, une fois"
    assert r["pied"]["y"] > b["y"] + 2, f"a pied, on est arrete : {r['pied']}"
    assert r["carnetAvant"] is True and r["ouverte"] is True and r["carnetApres"] is False
    assert r["apres"]["y"] > b["y"] + b["h"] and r["apres"]["vie"] == r["lance"]["vieMax"], "m2 faite, le pont coute encore"


def test_la_cour_de_l_usine_ferme_la_nuit(banc, paquet):
    usine = next(b for b in carte.BARRIERES if b["slug"] == "usine")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, p = L.B.partie;
        const b = L.Monde.carte.def.barrieres.find(function (q) { return q.slug === 'usine'; });
        const devant = L.Monde.carte.def.points_interet.find(function (q) { return q.slug === 'usine'; });
        // La nuit, pour de vrai : la premiere heure ou le monde le dit.
        for (const h of [0.95, 0.02, 0.9, 0.85, 0.1]) { p.heure = h; if (L.Monde.estNuit()) break; }
        const out = { nuit: L.Monde.estNuit(), fermee: L.Monde.barriereFermee(b) };
        // On ecarte ce qui trainerait dans la ruelle, et on vient du sud.
        for (const e of L.B.entites.slice()) if ((e.type === 'pieton' || e.type === 'vehicule') && Math.abs(e.x - devant.x * TT) < 80 && Math.abs(e.y - devant.y * TT) < 80) L.Entites.retirer(e);
        const yc = b.y + b.h - 1;                           // la rangee de la chaine, au sud
        function partir() { j.x = devant.x * TT + 8; j.y = (yc + 1) * TT + 8; j.buteT = 0; j.forceT = 0; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer(); }
        partir();
        L.B.recherche.etoiles = 0; L.B.recherche.chaleur = 0;
        o.touche('KeyW'); o.frame(30);
        out.bute = { y: j.y / TT, msg: L.B.msg, buteT: j.buteT };
        // On insiste : l'enjambee part, on retombe DEDANS, et l'etoile tombe.
        o.frame(120); o.relacher('KeyW');
        out.dedans = { y: j.y / TT, etoiles: L.B.recherche.etoiles, msg: L.B.msg };
        // De l'interieur, on ressort librement.
        o.touche('KeyS'); o.frame(90); o.relacher('KeyS');
        out.sorti = { y: j.y / TT };
        // Le jour : on entre sans rien payer.
        p.heure = 0.5; L.B.recherche.etoiles = 0;
        partir();
        o.touche('KeyW'); o.frame(60); o.relacher('KeyW');
        out.jour = { nuit: L.Monde.estNuit(), fermee: L.Monde.barriereFermee(b), y: j.y / TT, etoiles: L.B.recherche.etoiles };
        out.yc = yc;
        return out;
    }""")
    yc = r["yc"]
    assert r["nuit"] is True and r["fermee"] is True
    assert r["bute"]["y"] > yc + 0.9, f"la nuit, on entre dans la cour : {r['bute']}"
    assert r["bute"]["msg"] == usine["raison"], r["bute"]
    assert r["dedans"]["y"] < yc, f"apres une seconde a pousser, on n'a pas enjambe : {r['dedans']}"
    assert r["dedans"]["etoiles"] >= usine["forcer"]["etoiles"], "forcer la cour ne coute pas l'etoile de la fiche"
    assert "FRANCHI" in (r["dedans"]["msg"] or "")
    assert r["sorti"]["y"] > yc + 0.9, f"dedans, on ne ressort plus : {r['sorti']}"
    assert r["jour"]["nuit"] is False and r["jour"]["fermee"] is False
    assert r["jour"]["y"] < yc and r["jour"]["etoiles"] == 0, f"le jour, la cour coute encore : {r['jour']}"


def test_le_trafic_fait_demi_tour_devant_les_cones(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, b = L.Monde.carte.def.barrieres.find(function (q) { return q.slug === 'pont'; });
        const x = (b.x + 1) * TT + 8;
        j.x = b.x * TT - 40; j.y = (b.y - 5) * TT; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        const v = L.Vehicules.creer('auto', x, (b.y - 6) * TT + 8, Math.PI / 2, { conducteur: 'trafic', etat: 'roule', sens: 'v' });
        L.Entites.indexer();
        let plusBas = v.y, entre = false;
        // ⚠️ « S'empiler », ce n'est pas « être arrêté » : devant la couronne
        // il y a un FEU, et s'arrêter au rouge est ce qu'on attend d'eux. Ce
        // qu'on mesure, c'est qui reste PLANTÉ — on compte, pour chaque char,
        // ses images d'affilée à l'arrêt dans l'approche, et on garde le pire.
        const plantes = new Map();
        let pire = 0;
        for (let i = 0; i < 600; i++) {
            o.frame(1);
            for (const e of L.B.entites) {
                if (e.type !== 'vehicule' || e.conducteur !== 'trafic') continue;
                const dansLApproche = Math.abs(e.x - x) < TT && e.y > (b.y - 6) * TT && e.y < b.y * TT;
                const n = (dansLApproche && Math.abs(e.vitesse) < 0.05) ? (plantes.get(e) || 0) + 1 : 0;
                plantes.set(e, n);
                if (n > pire) pire = n;
            }
            if (!v.actif || L.B.entites.indexOf(v) < 0) break;
            plusBas = Math.max(plusBas, v.y);
            if (v.y >= b.y * TT - 4) entre = true;
        }
        const encore = L.B.entites.indexOf(v) >= 0;
        const t = L.B.defs.conduite.trafic;
        return { entre: entre, plusBas: plusBas / TT, encore: encore, y: v.y / TT, sens: v.sens,
                 vitesse: v.vitesse, pire: pire, cycle: 2 * (t.feu_vert_images + t.feu_orange_images), bY: b.y };
    }""")
    assert r["entre"] is False, f"le trafic est entre sur le pont ferme : {r}"
    # Un cycle de feu complet, et de la marge : au-dela, ce n'est plus un feu
    # qu'on attend, c'est un mur devant lequel on a renonce.
    assert r["pire"] < r["cycle"], f"un char reste plante {r['pire']} images devant les cones : {r}"
    if r["encore"]:
        assert r["sens"] == "^" or r["y"] < r["bY"] - 4, f"le char n'a pas fait demi-tour : {r}"
