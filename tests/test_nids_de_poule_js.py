"""Les nids-de-poule qui mordent, au banc (docs/jalons/les-nids-de-poule-qui-mordent.md).

Ils se voient sur la chaussée ; pris à grande vitesse, le volant ne répond plus une fraction de
seconde (au joueur seulement) ; le camion d'asphalte attend devant la fourrière et naît quand on
approche ; au klaxon, le boulot de voirie : un nid bouché l'est pour de bon, même après un
chargement ; et le Clairon du lundi en fait le décompte. Et d'abord (M12, 1re vague, en fin de fichier) :
ils sont sur la chaussée, hors croisement et espacés ; un nid secoue et coûte ses points une seule fois ;
et une porte ne les efface pas.
"""

import itertools

import pytest
import villes

from app import carte, economie, vehicules

#: Le joueur a 300 px de la place du camion (hors champ), et les images qu'il faut pour qu'il naisse.
APPROCHE = """
  function approcher(L, o) {
    const B = L.B, j = B.joueur, M = L.Missions;
    const place = M.placeDeLAsphalte();
    j.x = place.x + 300; j.y = place.y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
    for (let k = 0; k < 130; k++) o.frame(1);
    return B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'asphalte'; });
  }
"""

#: Un nid de la ville avec deux tuiles de chaussee libre de chaque cote sur son rang.
UN_NID = """
  function unNid(L) {
    const Mo = L.Monde;
    for (const cle of Mo.carte.nids) {
      const i = cle.indexOf(','), tx = +cle.slice(0, i), ty = +cle.slice(i + 1);
      let ok = true;
      for (let k = -6; k <= 3 && ok; k++) ok = Mo.estChaussee(tx + k, ty) && !Mo.bloque(tx + k, ty, Mo.MASQUE_VEHICULE);
      if (ok) return { tx: tx, ty: ty, x: tx * 16 + 8, y: ty * 16 + 8 };
    }
    return null;
  }
"""


def test_ils_se_voient_sur_la_chaussee(banc):
    """Un nid a l'ecran se peint (une image de plus au compteur) ; hors champ, rien."""
    r = banc("function (L, o) {" + UN_NID + """
        L.Jeu.commencer();
        const B = L.B, Mo = L.Monde, n = unNid(L);
        const peints = [];
        const ctx = { drawImage: function (img, x, y) { peints.push([x, y]); } };
        Mo.dessinerNids(ctx, { x: n.x - 100, y: n.y - 100 });
        const ici = peints.filter(function (p) { return p[0] === n.tx * 16 - (n.x - 100) && p[1] === n.ty * 16 - (n.y - 100); }).length;
        peints.length = 0;
        Mo.dessinerNids(ctx, { x: -5000, y: -5000 });
        return { total: Mo.carte.nids.size, ici: ici, loin: peints.length };
    }""")
    assert r["total"] > 20, r
    assert r["ici"] == 1, "le nid sous la camera ne s'est pas peint"
    assert r["loin"] == 0, r


def test_pris_vite_le_volant_ne_repond_plus(banc):
    """A pleine vitesse sur un nid : `sansControle`, et le volant tenu a fond ne braque pas ; au
    pas, rien. Le trafic, lui, ne derape pas."""
    r = banc("function (L, o) {" + UN_NID + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, V = L.Vehicules, n = unNid(L);
        B.entites = B.entites.filter(function (e) { return e === j || !(e.type === 'vehicule' || e.type === 'pieton' || e.type === 'police') || Math.hypot(e.x - n.x, e.y - n.y) > 300; });
        function passer(vitesse, auVolant) {
            const v = V.creer('auto', n.x - 40, n.y, 0, { etat: 'stationne' });
            if (auVolant) V.monter(j, v); else v.etat = 'roule';
            v.vitesse = vitesse; v.vx = vitesse; v.vy = 0; v.angle = 0;
            if (auVolant) { j.x = v.x; j.y = v.y; }
            L.Entites.indexer();
            // Le volant tenu a droite tout du long : on mesure ce qu'il tourne, image par image,
            // pendant que le nid l'aveugle (et apres).
            // ⚠️ La direction a de l'inertie : sans la main, les roues reviennent au centre en
            // quelques images. On juge donc la FIN de l'aveuglement (sous six images restantes).
            let sans = 0, tourneSans = 0, tourneApres = 0;
            if (auVolant) o.touche('KeyD');
            for (let k = 0; k < 40; k++) {
                const avant = v.angle, aveugle = v.sansControle > 0 && v.sansControle <= 6;
                o.frame(1);
                if (v.sansControle > 0) sans++;
                if (aveugle && v.sansControle > 0) tourneSans = Math.max(tourneSans, Math.abs(v.angle - avant));
                else if (sans && !(v.sansControle > 0)) tourneApres = Math.max(tourneApres, Math.abs(v.angle - avant));
            }
            if (auVolant) { o.relacher('KeyD'); V.descendre(j, true); }
            const out = { sans: sans, tourneSans: tourneSans, tourneApres: tourneApres };
            B.entites.splice(B.entites.indexOf(v), 1);
            return out;
        }
        const ph = B.defs.conduite.physique;
        return { vite: passer(ph.nid_derape_vitesse + 1.5, true), lent: passer(1.4, true), trafic: passer(ph.nid_derape_vitesse + 1.5, false) };
    }""")
    assert r["vite"]["sans"] > 0, "a pleine vitesse, le nid n'a rien fait au volant"
    assert r["vite"]["tourneSans"] < 0.005, "le volant tenu a tourne le char pendant qu'il ne repondait plus"
    assert r["vite"]["tourneApres"] > 0.04, "le volant ne revient jamais"
    assert r["lent"]["sans"] == 0, "au pas, le nid enleve le volant"
    assert r["trafic"]["sans"] == 0, "le trafic derape sur les nids"


def test_le_camion_attend_devant_la_fourriere_et_nait_quand_on_approche(banc):
    r = banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const B = L.B;
        const combien = function () { return B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'asphalte'; }).length; };
        const place0 = L.Missions.placeDeLAsphalte(), j = B.joueur;
        // Loin (a 900 px) : il n'existe pas.
        j.x = place0.x + 900; j.y = place0.y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        for (let k = 0; k < 130; k++) o.frame(1);
        const auDemarrage = combien();
        // Sous les yeux : il ne pousse pas devant nous.
        j.x = place0.x + 40; j.y = place0.y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        for (let k = 0; k < 130; k++) o.frame(1);
        const sousLesYeux = combien();
        const camions = approcher(L, o);
        for (let k = 0; k < 130; k++) o.frame(1);
        const encore = B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'asphalte'; }).length;
        const c = camions[0], place = L.Missions.placeDeLAsphalte();
        const f = L.Monde.carte.def.fourriere.grille;
        return { auDemarrage: auDemarrage, sousLesYeux: sousLesYeux, n: camions.length, encore: encore, gare: c && c.etat,
                 pres: c ? Math.round(Math.hypot(c.x - place.x, c.y - place.y)) : null,
                 grille: Math.round(Math.hypot(place.x - (f.x + f.largeur / 2) * 16, place.y - f.y * 16)) };
    }""")
    assert r["auDemarrage"] == 0, "il est ne loin du joueur : un identifiant de plus pour toute la partie"
    assert r["sousLesYeux"] == 0, "il est apparu a l'ecran"
    assert r["n"] == 1 and r["encore"] == 1, r
    assert r["gare"] == "stationne" and r["pres"] < 16, r
    assert r["grille"] < 12 * 16, r


def test_un_passant_ne_vole_pas_le_camion_qui_attend(banc):
    """Le vol de char de la rue prend un char gare que personne ne conduit — pas le camion
    d'asphalte, ni celui de creme glacee : il n'y en a qu'un, et vole il ne revenait jamais."""
    r = banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const B = L.B, E = L.Entites, j = B.joueur;
        const c = approcher(L, o)[0];
        B.defs.pietons.vol_de_char.chance_par_minute = 1;
        function essai(char) {
            // Rien d'autre a voler : le char seul a l'ecran, un passant qui flane a cote.
            B.entites = B.entites.filter(function (e) { return e === char || e === j || !(e.type === 'vehicule' || e.type === 'pieton'); });
            j.x = char.x + 60; j.y = char.y; L.Monde.centrerCamera(j.x, j.y);
            const p = E.creerPieton(char.x + 20, char.y + 20, E.archetype('passant'));
            p.etat = 'flane';
            E.indexer();
            B.volMinute = null;
            return { vole: E.majVolDeChar(), vise: p.charVise === char };
        }
        const camion = essai(c);
        const auto = L.Vehicules.creer('auto', c.x, c.y + 40, 0, { etat: 'stationne', couleur: '#888' });
        const temoin = essai(auto);
        return { camion: camion, temoin: temoin };
    }""")
    assert r["temoin"] == {"vole": 1, "vise": True}, f"le vol de char ne vole rien : le juge ne prouve rien ({r})"
    assert r["camion"] == {"vole": 0, "vise": False}, r


def test_au_klaxon_un_nid_bouche_l_est_pour_de_bon(banc):
    """Au volant du camion, le klaxon : un nid-de-poule pour destination. Arrete dessus : paye, le
    nid quitte la carte et la partie s'en souvient — meme rechargee sur une carte neuve."""
    r = banc("function (L, o) {" + APPROCHE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, Mo = L.Monde, p = B.partie;
        const c = approcher(L, o)[0];
        L.Vehicules.monter(B.joueur, c);
        o.tape('KeyJ', 2);
        const d = M.boulot.destination;
        const cle = Math.floor(d.x / 16) + ',' + Math.floor(d.y / 16);
        const surUnNid = Mo.carte.nids.has(cle), slug = M.boulot.slug;
        // A 30 px : rien.
        c.x = d.x + 30; c.y = d.y; c.vitesse = 0; c.vx = 0; c.vy = 0; B.joueur.x = c.x; B.joueur.y = c.y;
        L.Entites.indexer(); o.frame(3);
        const aCote = M.boulot.etapesFaites || 0;
        const argent = p.argent;
        c.x = d.x; c.y = d.y; B.joueur.x = c.x; B.joueur.y = c.y;
        L.Entites.indexer(); o.frame(3);
        const paye = p.argent - argent, bouche = !Mo.carte.nids.has(cle), retenu = (p.nidsBouches || []).indexOf(cle) >= 0;
        // Recharge : une carte neuve (tous ses nids), la partie relue.
        const sauvee = JSON.parse(JSON.stringify(p));
        Mo.charger(B.defs.carte);
        const revenu = Mo.carte.nids.has(cle);
        B.partie = L.Sauvegarde.completer(sauvee, B.defs);
        o.frame(1);
        return { surUnNid: surUnNid, slug: slug, aCote: aCote, paye: paye, bouche: bouche, retenu: retenu,
                 revenu: revenu, apres: Mo.carte.nids.has(cle), etapes: M.boulot.etapesFaites };
    }""")
    assert r["slug"] == "voirie" and r["surUnNid"], r
    assert r["aCote"] == 0, "a 30 px du trou, le nid s'est bouche"
    assert r["paye"] > 0 and r["bouche"] and r["retenu"] and r["etapes"] == 1, r
    assert r["revenu"], "la carte neuve n'a pas ses nids : le juge ne prouve rien"
    assert not r["apres"], "rechargee, la partie a oublie le nid bouche"


def test_le_clairon_du_lundi_fait_le_decompte(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, p = B.partie;
        const lignes = [];
        for (let jour = 1; jour <= 8; jour++) { p.jour = jour; lignes.push(M.decompteDesNids()); }
        p.jour = 8; p.nidsBouches = ['1,1', '2,2'];
        return { lignes: lignes, total: L.Monde.carte.nids.size, avec: M.decompteDesNids() };
    }""")
    lundis = [i + 1 for i, ligne in enumerate(r["lignes"]) if ligne]
    assert lundis == [1, 8], r["lignes"]
    assert f"{r['total']} NIDS-DE-POULE EN VILLE" in r["lignes"][0]
    assert "BOUCHÉS" not in r["lignes"][0]
    assert r["avec"].endswith("2 BOUCHÉS PAR TOI"), r["avec"]


def test_la_voirie_tient_l_economie():
    # (« Entre le taxi et quatre fois le taxi » : `test_economie::test_chaque_boulot_vaut_la_peine…`,
    # qui passe chaque boulot de `BOULOTS` — la voirie comprise.)
    assert "voirie" in economie.BOULOTS
    assert vehicules.par_slug("asphalte")["frequence"] == 0, "il ne roule pas dans le trafic"
    assert [p["type"] for p in economie.PALIERS["voirie"]][-1] == "char"


# --- Où ils sont, ce qu'ils coûtent, et qu'une porte ne les efface pas (M12, 1re vague) ----------------


@pytest.fixture(scope="module")
def ville():
    return villes.generer()


def test_les_nids_sont_sur_la_chaussee_hors_croisement_et_espaces(ville):
    """⚠️ **Jamais dans un croisement** — on y freine déjà, on y regarde le
    feu, et une secousse au milieu d'un virage se lit comme un bogue de
    collision. Jamais sur une ligne d'arrêt non plus : c'est là qu'on est
    immobile. Et jamais deux collés : deux nids côte à côte ne font pas un
    nid-de-poule, ils font une rue défoncée."""
    fiche = carte.NIDS_DE_POULE
    nids = ville["nids_de_poule"]
    lo, hi = fiche["par_ville"]
    assert lo <= len(nids) <= hi, f"{len(nids)} nids-de-poule"
    sol = ville["sol"]
    boites = [(i["x"], i["y"], i["l"], i["h"]) for i in ville["intersections"]]
    arrets = {tuple(int(n) for n in cle.split(",")) for cle in ville["arrets"]}
    for n in nids:
        glyphe = sol[n["y"]][n["x"]]
        assert carte.LEGENDE[glyphe].get("route"), f"un nid sur « {glyphe} »"
        assert not carte.LEGENDE[glyphe].get("trottoir"), "un nid sur une traverse"
        assert (n["x"], n["y"]) not in arrets, f"un nid sur une ligne d'arrêt : {n}"
        for bx, by, bl, bh in boites:
            assert not (bx <= n["x"] < bx + bl and by <= n["y"] < by + bh), f"un nid dans un croisement : {n}"
    for a, b in itertools.combinations(nids, 2):
        ecart = abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])
        assert ecart >= fiche["ecart"], f"deux nids collés : {a} et {b}"
    # Et ils sont répandus : tous dans un coin, c'est une rue défoncée, pas une ville.
    moitie = ville["largeur"] // 2
    assert any(n["x"] < moitie for n in nids) and any(n["x"] >= moitie for n in nids)


def test_un_nid_secoue_et_coute_deux_points_une_seule_fois(banc, paquet):
    """⚠️ Un répit après chaque nid : sans lui, un char lent le paie à chaque
    image de la tuile, et un nid devient un piège au lieu d'un cahot."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, ph = L.B.defs.conduite.physique;
        const nid = L.Monde.carte.def.nids_de_poule[0];
        j.x = nid.x * TT + 8; j.y = nid.y * TT + 8; L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        v.x = nid.x * TT + 8; v.y = nid.y * TT + 8; L.Entites.indexer();
        const out = { indexe: L.Monde.nidDePoule(nid.x, nid.y),
                      ailleurs: L.Monde.nidDePoule(nid.x + 3, nid.y + 3) };
        // 1. A L'ARRET : un char immobile ne tombe pas dans un nid.
        v.vitesse = 0; v.vx = 0; v.vy = 0; v.nidT = 0;
        const vie0 = v.vie;
        L.B.cam.secousse = 0;
        for (let i = 0; i < 10; i++) L.Vehicules.majNidDePoule(v);
        out.arret = { perdu: vie0 - v.vie, secousse: L.B.cam.secousse };
        // 2. EN ROULANT : une fois, et une seule, le temps du répit.
        v.vitesse = 2; v.vx = 2; v.vy = 0; v.nidT = 0;
        const vie1 = v.vie;
        for (let i = 0; i < 10; i++) L.Vehicules.majNidDePoule(v);
        out.roule = { perdu: vie1 - v.vie, secousse: L.B.cam.secousse, repit: v.nidT };
        // 3. Le répit passé, on le paie de nouveau.
        v.nidT = 0;
        const vie2 = v.vie;
        L.Vehicules.majNidDePoule(v);
        out.encore = vie2 - v.vie;
        return out;
    }""")
    ph = vehicules.PHYSIQUE
    assert r["indexe"] is True and r["ailleurs"] is False, "l'index des nids ne dit pas la vérité : %s" % r
    assert r["arret"]["perdu"] == 0 and r["arret"]["secousse"] == 0, "un char à l'arrêt tombe dans un nid : %s" % r["arret"]
    assert r["roule"]["perdu"] == ph["nid_degats"], "le nid ne coûte pas ce que la fiche dit : %s" % r["roule"]
    assert abs(r["roule"]["secousse"] - ph["nid_secousse"]) < 1e-9, r["roule"]
    assert r["roule"]["repit"] > 0, "aucun répit : le nid se paie à chaque image"
    assert r["encore"] == ph["nid_degats"], "le répit passé, le nid ne se sent plus : %s" % r


def test_un_nid_secoue_encore_apres_une_porte(banc, paquet):
    """⚠️ Vu le 16 sept. 2026 : après être entré dans n'importe quel bâtiment et
    ressorti, plus un seul nid ne secouait la ville jusqu'au rechargement. Les
    nids vivaient dans le MODULE de `monde.js` ; une pièce passe par `charger`,
    qui les remplaçait par les siens (aucun), et `restaurer` ne rendait que la
    carte. Le cœur de la ville, pareil : demandé depuis une pièce, il restait au
    milieu de la pièce. On passe par la vraie porte, fondus compris."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, c = L.Monde.carte;
        const nid = c.def.nids_de_poule[0];
        const coeur = L.Monde.coeurDeLaVille();
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 10;
        L.Monde.centrerCamera(j.x, j.y);
        L.Jeu.entrer(porte);
        o.fondu();
        const out = { dedans: !!L.B.interieur, coeurDedans: L.Monde.coeurDeLaVille() };
        L.Jeu.sortir();
        o.fondu();
        out.dehors = L.B.interieur === null;
        out.indexe = L.Monde.nidDePoule(nid.x, nid.y);
        const apres = L.Monde.coeurDeLaVille();
        out.memeCoeur = apres.x === coeur.x && apres.y === coeur.y;
        out.coeurDedansEstLeSien = out.coeurDedans.x === coeur.x && out.coeurDedans.y === coeur.y;
        // Et un char qui roule dessus le sent.
        const v = o.char('auto', 0, 0, 0);
        v.x = nid.x * TT + 8; v.y = nid.y * TT + 8; v.vitesse = 2; v.vx = 2; v.vy = 0; v.nidT = 0;
        const vie = v.vie;
        L.Vehicules.majNidDePoule(v);
        out.perdu = vie - v.vie;
        return out;
    }""")
    assert r["dedans"] and r["dehors"], f"l'aller-retour par la porte n'a pas marché : {r}"
    assert r["indexe"] is True, "ressorti d'une pièce, la ville n'a plus de nids-de-poule"
    assert r["perdu"] == vehicules.PHYSIQUE["nid_degats"], f"le nid ne se sent plus : {r}"
    assert r["memeCoeur"], "le cœur de la ville est resté dans la pièce"
    assert r["coeurDedansEstLeSien"], "demandé depuis une pièce, le cœur de la ville est celui de la pièce"
