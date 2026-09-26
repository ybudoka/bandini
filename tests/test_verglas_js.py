"""La tempête de verglas, au banc (docs/jalons/la-tempete-de-verglas.md).

Trois jours, les mêmes pour tout le monde ; des quartiers au noir (plus une lampe allumée) qui se
rallument quand ça fond ; les chars glissent ; la police voit moins loin et tarde ; des génératrices à
livrer, en camion, pendant la tempête seulement ; le Clairon l'annonce. Derrière son option : éteinte,
elle n'existe pas.
"""

from app import verglas

#: Un jour de tempete (le deuxieme, le plein), la nuit, l'option allumee ou non.
TEMPETE = """
  function tempete(L, allumee, jour, heure) {
    const B = L.B;
    B.options.verglas = allumee;
    B.partie.jour = jour === undefined ? B.defs.verglas.tempete.premier + 1 : jour;
    B.partie.heure = heure === undefined ? 23 / 24 : heure;
    L.Verglas.oublier();
  }
"""


def test_les_memes_trois_jours_pour_tout_le_monde_puis_ca_fond(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const V = L.Verglas, jours = [];
        for (const g of [1, 777]) {
            L.graine(g);
            const j = [];
            for (let d = 1; d <= 100; d++) if (V.intensiteA(d, 0.5)) j.push(d);
            jours.push(j);
        }
        const t = L.B.defs.verglas.tempete, dernier = t.premier + t.jours - 1;
        return { jours: jours, arrivee: +V.intensiteA(t.premier, 1 / 24).toFixed(2),
                 fonte: +V.intensiteA(dernier, 21 / 24).toFixed(2), lendemain: V.intensiteA(dernier + 1, 0.1),
                 noirs: [V.quartiersNoirsA(t.premier + 1), V.quartiersNoirsA(t.premier + 1)] };
    }""")
    t = verglas.TEMPETE
    attendu = [t["premier"] + n * t["tous_les"] + k for n in range(4) for k in range(t["jours"])]
    assert r["jours"][0] == r["jours"][1] == [d for d in attendu if d <= 100], r["jours"]
    assert 0 < r["arrivee"] < 1 and 0 < r["fonte"] < 1 and r["lendemain"] == 0, r
    assert r["noirs"][0] == r["noirs"][1] and len(r["noirs"][0]) == verglas.PANNES["par_jour"][1], r["noirs"]


def test_eteint_il_n_existe_pas(banc):
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        tempete(L, false);
        const V = L.Verglas;
        return { option: L.B.options.verglas, i: V.intensite(), adh: V.adherence(), vision: V.vision(),
                 retard: V.retardPolice(), noirs: V.quartiersNoirs().size, clairon: V.ligneDuClairon() };
    }""")
    assert r == {"option": False, "i": 0, "adh": 1, "vision": 1, "retard": 1, "noirs": 0, "clairon": None}, r


def test_un_quartier_au_noir_n_a_plus_une_lampe_et_tout_se_rallume_apres(banc):
    """La nuit, la caméra sur une lampe d'un quartier au noir : sans l'option, des lampes de ce
    quartier brillent ; pendant la tempête, plus une ; le lendemain de la fonte, elles reviennent. Et
    la nuit y est plus noire — pas ailleurs."""
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        const B = L.B, V = L.Verglas, Mo = L.Monde;
        tempete(L, true);
        const noirs = V.quartiersNoirs();
        const district = function (x, y) { const z = Mo.zoneA(x, y); return z ? z.district : null; };
        const l = Mo.carte.lampes.find(function (q) { return noirs.has(district(q.x, q.y)) && !q.panne && !q.eteinte && q.c !== 'fenetre'; });
        const cam = { x: l.x - 240, y: l.y - 135 };
        B.cam.x = cam.x; B.cam.y = cam.y;
        const auNoir = function () {
            return Mo.lampesVisibles(cam).filter(function (q) { return noirs.has(district(q.x + cam.x, q.y + cam.y)); }).length;
        };
        const pendant = auNoir(), nuit = Mo.ambiance(), noire = V.ambiance(nuit).alpha;
        tempete(L, false);
        const sansOption = auNoir();
        const t = B.defs.verglas.tempete;
        tempete(L, true, t.premier + t.jours);
        const apres = auNoir();
        // Ailleurs (un quartier qui a du courant) : la nuit ordinaire.
        tempete(L, true);
        const clair = Mo.carte.zones.find(function (z) { return z.district && z.slug === z.district && !noirs.has(z.district) && z.district !== 'baie'; });
        B.cam.x = (clair.x + clair.l / 2) * 16 - 240; B.cam.y = (clair.y + clair.h / 2) * 16 - 135;
        const ailleurs = V.ambiance(nuit).alpha;
        return { pendant: pendant, sansOption: sansOption, apres: apres, nuit: nuit.alpha, noire: noire, ailleurs: ailleurs };
    }""")
    assert r["sansOption"] > 0, f"aucune lampe du quartier à l'écran : le juge ne prouve rien ({r})"
    assert r["pendant"] == 0, f"une lampe brille dans un quartier au noir : {r}"
    assert r["apres"] == r["sansOption"], f"la tempête finie, le quartier ne s'est pas rallumé : {r}"
    assert r["noire"] > r["nuit"] and r["ailleurs"] == r["nuit"], r


def test_sur_la_glace_le_char_glisse(banc):
    """Le même virage, volant à fond, à la même vitesse : sur la glace, la vitesse suit le nez de moins
    près (le char dérape)."""
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, V = L.Vehicules, p = o.boulevard(true);
        function virage(allumee) {
            tempete(L, allumee, undefined, 0.5);
            B.entites = B.entites.filter(function (e) { return e === j || !(e.type === 'vehicule' || e.type === 'pieton' || e.type === 'police'); });
            const v = V.creer('auto', p.x, p.y, 0, { etat: 'stationne', couleur: '#888' });
            V.monter(j, v); j.x = v.x; j.y = v.y;
            v.vitesse = 3.2; v.vx = 3.2; v.vy = 0; v.angle = 0;
            L.Entites.indexer();
            o.touche('KeyD'); o.touche('KeyW');
            let glisse = 0;
            for (let k = 0; k < 14; k++) {
                o.frame(1);
                const cap = Math.atan2(v.vy, v.vx);
                glisse = Math.max(glisse, Math.abs(Math.atan2(Math.sin(v.angle - cap), Math.cos(v.angle - cap))));
            }
            o.relacher('KeyD'); o.relacher('KeyW');
            V.descendre(j, true);
            B.entites.splice(B.entites.indexOf(v), 1);
            return glisse;
        }
        const sec = virage(false), glace = virage(true);
        return { sec: +sec.toFixed(3), glace: +glace.toFixed(3), adh: L.Verglas.adherence() };
    }""")
    assert r["adh"] == verglas.EFFETS["adherence"], r
    assert r["glace"] > r["sec"] * 1.3, f"sur la glace, le char ne glisse pas plus : {r}"


def test_la_police_debordee_voit_moins_loin_et_tarde(banc):
    """Un agent à 70 % de sa portée, en ligne droite : vu par beau temps, pas sur la glace. Et les
    renforts d'une étoile neuve tardent de `retard_police`."""
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        const B = L.B, P = L.Police, j = B.joueur, M = L.Monde;
        const portee = B.defs.recherche.vision.policier.jour * 16;
        let agent = null;
        for (let r = 0; r < 80 && !agent; r++) {
            for (let dy = -r; dy <= r && !agent; dy++) for (let dx = -r; dx <= r && !agent; dx++) {
                const tx = Math.floor(j.x / 16) + dx, ty = Math.floor(j.y / 16) + dy;
                if (!M.estChaussee(tx, ty)) continue;
                const px = tx * 16 + 8, py = ty * 16 + 8;
                for (let k = 0; k < 4 && !agent; k++) {
                    const a = k * Math.PI / 2, x = px - Math.cos(a) * portee * 0.7, y = py - Math.sin(a) * portee * 0.7;
                    if (M.ligneLibre(x, y, px, py)) { agent = { x: x, y: y, angle: a }; j.x = px; j.y = py; }
                }
            }
        }
        if (!agent) return { libre: false };
        tempete(L, false, undefined, 0.5);
        const clair = P.voit(agent, j.x, j.y, 'policier');
        tempete(L, true, undefined, 0.5);
        const glace = P.voit(agent, j.x, j.y, 'policier');
        function renforts(allumee) {
            tempete(L, allumee, undefined, 0.5);
            const rc = B.recherche;
            rc.etoiles = 0; rc.etoilesAvant = 0; rc.renfortN = 0; o.frame(1);
            rc.chaleur = 100; rc.etoiles = 2;
            o.frame(1);
            return rc.renfortN;
        }
        return { libre: true, clair: clair, glace: glace, sec: renforts(false), verglas: renforts(true) };
    }""")
    assert r["libre"], "aucune ligne dégagée autour du joueur : le juge ne mesure rien"
    assert r["clair"] is True and r["glace"] is False, r
    assert r["sec"] > 0, f"aucun renfort en route : le juge ne mesure rien ({r})"
    assert abs(r["verglas"] - r["sec"] * verglas.EFFETS["retard_police"]) <= 2, r


def test_des_generatrices_en_camion_pendant_la_tempete_seulement(banc):
    """Au klaxon d'un camion : rien par beau temps ; pendant la tempête, une génératrice pour un lieu
    d'un quartier au noir, payée à l'arrivée."""
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, j = B.joueur, Mo = L.Monde;
        tempete(L, true, B.defs.verglas.tempete.premier - 1, 0.5);
        const v = o.char('camion', 30, 0, 0);
        L.Vehicules.monter(j, v);
        o.tape('KeyJ', 2);
        const beauTemps = M.boulot.slug;
        tempete(L, true, undefined, 0.5);
        o.tape('KeyJ', 2);
        const d = M.boulot.destination;
        const z = d ? Mo.zoneA(d.x, d.y) : null;
        const noirs = Array.from(L.Verglas.quartiersNoirs());
        const argent = B.partie.argent;
        v.x = d.x; v.y = d.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y;
        L.Entites.indexer(); o.frame(3);
        return { beauTemps: beauTemps, slug: M.boulot.slug, district: z && z.district, noirs: noirs,
                 paye: B.partie.argent - argent, etapes: M.boulot.etapesFaites };
    }""")
    assert r["beauTemps"] is None, f"par beau temps, le klaxon d'un camion a pris un boulot : {r}"
    assert r["slug"] == "generatrices" and r["district"] in r["noirs"], r
    assert r["paye"] > 0 and r["etapes"] == 1, r


def test_le_clairon_l_annonce_la_veille_puis_nomme_les_quartiers(banc):
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        const B = L.B, V = L.Verglas, t = B.defs.verglas.tempete;
        const lignes = {};
        for (const d of [t.premier - 2, t.premier - 1, t.premier, t.premier + 1, t.premier + t.jours]) {
            tempete(L, true, d, 0.3); lignes[d - t.premier] = V.ligneDuClairon();
        }
        // Au lever du jour, pour vrai : la ligne tombe sous la manchette (ou au message).
        tempete(L, true, t.premier + 1, 0.3);
        B.dialogue = null; B.msg = null;
        L.Missions.nouveauJour();
        const dit = JSON.stringify(B.dialogue || '') + JSON.stringify(B.msg || '');
        const noms = V.quartiersNoirsA(t.premier + 1).map(function (s) {
            return L.Monde.carte.zones.find(function (z) { return z.district === s && z.slug === s; }).nom.toUpperCase();
        });
        return { lignes: lignes, dit: dit, noms: noms };
    }""")
    ligne = r["lignes"]
    assert ligne["-2"] is None and ligne["-1"] == verglas.CLAIRON["veille"], ligne
    assert all(n in ligne["1"] for n in r["noms"]) and ligne["1"].startswith("VERGLAS"), ligne
    assert ligne["3"] is None, ligne
    assert ligne["1"] in r["dit"], "au lever du jour, le Clairon ne dit rien du verglas"


def test_la_glace_se_peint_sans_tirer_de_de(banc):
    """Allumée, la glace se peint (le reflet, des branches sur les trottoirs) ; éteinte, rien. Cent
    images de verglas entre deux tirages de `B.rng()` : le tirage suivant ne change pas."""
    r = banc("function (L, o) {" + TEMPETE + """
        L.Jeu.commencer();
        const B = L.B, V = L.Verglas, j = B.joueur;
        const appels = { rect: 0, image: 0 };
        const ctx = { fillRect: function () { appels.rect++; }, drawImage: function () { appels.image++; }, set fillStyle(c) {} };
        const cam = { x: j.x - 240, y: j.y - 135 };
        tempete(L, false);
        V.dessinerSol(ctx, cam);
        const eteinte = appels.rect + appels.image;
        tempete(L, true);
        let images = 0;
        for (let k = 0; k < 40 && !images; k++) { appels.rect = 0; appels.image = 0; V.dessinerSol(ctx, { x: cam.x + k * 480, y: cam.y }); images = appels.image; }
        L.graine(9);
        const temoin = [B.rng(), B.rng()];
        L.graine(9);
        for (let k = 0; k < 100; k++) { B.t++; V.dessinerSol(ctx, cam); V.adherence(); V.vision(); V.lampeAuNoir(L.Monde.carte.lampes[k]); V.ambiance(L.Monde.ambiance()); }
        return { eteinte: eteinte, rect: appels.rect, images: images, temoin: temoin, apres: [B.rng(), B.rng()] };
    }""")
    assert r["eteinte"] == 0, r
    assert r["rect"] >= 1 and r["images"] >= 1, r
    assert r["apres"] == r["temoin"], "le verglas a tiré au dé du jeu"
