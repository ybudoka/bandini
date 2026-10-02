"""Les bateaux ne sont pas des chars, vague 5 — l'habillage.

Le compteur en nœuds, le bouton de la corne, des pas sur un pont en montant à bord, le diesel du chalutier et du
cargo, les feux de navigation (rouge à bâbord, vert à tribord, blanc à la poupe), et l'épave qui coule au lieu de
flotter. (L'hiver des chaloupes est à la foire fermée l'hiver.)"""

from app import audio

AIDES = """
    function pleinLarge(L) {
        const c = L.Monde.carte;
        for (let ty = 8; ty < c.h - 8; ty++) for (let tx = 8; tx < c.w - 8; tx++) {
            let plein = true;
            for (let dy = -4; dy <= 4 && plein; dy++) for (let dx = -4; dx <= 4 && plein; dx++) if (!L.Monde.estEau(tx + dx, ty + dy)) plein = false;
            if (plein) return { x: tx * L.TT + 8, y: ty * L.TT + 8 };
        }
        return null;
    }
    function coque(L, slug, p) {
        const j = L.B.joueur; j.x = p.x; j.y = p.y; L.Monde.centrerCamera(p.x, p.y);
        return L.Vehicules.creer(slug, p.x, p.y, 0, { etat: 'stationne' });
    }
"""


def test_les_sons_des_bateaux_sont_au_catalogue_et_se_chargent_a_part():
    slugs = {e["slug"] for e in audio.CATALOGUE}
    assert {"a_bord", "moteur_diesel"} <= slugs, "les sons des bateaux ne sont pas au catalogue"
    assert set(audio.LIEUX.get("bateaux", [])) >= {"a_bord", "moteur_diesel"}, \
        "les sons des bateaux se chargent au premier écran (il est plein)"
    diesel = next(e for e in audio.CATALOGUE if e["slug"] == "moteur_diesel")
    assert diesel["boucle"], "le diesel ne tourne pas en boucle"


def test_le_compteur_d_une_coque_est_en_noeuds(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), v = coque(L, 'bateau', p), a = L.Vehicules.creer('auto', p.x, p.y, 0, { etat: 'stationne' });
        v.vitesse = v.def.vitesse_max; a.vitesse = a.def.vitesse_max;
        return { coque: L.Hud.compteur(v), auto: L.Hud.compteur(a) };
    }""")
    assert r["auto"].endswith("KM/H"), r
    assert r["coque"] == "22 NŒUDS", f"la chaloupe à fond : {r['coque']}"


def test_le_bouton_d_une_coque_dit_sa_corne_et_n_a_pas_de_frein(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), j = L.B.joueur, E = L.Entree;
        const vus = []; const vrai = E.contexte; E.contexte = function (nom) { vus.push(nom); return vrai.apply(this, arguments); };
        function monte(slug) {
            const v = coque(L, slug, p); L.Vehicules.monter(j, v);
            const nom = vus[vus.length - 1], e = E.etiquettesTactiles(nom);
            L.Vehicules.descendre(j, true); L.Entites.retirer(v);
            return { contexte: nom, e: e };
        }
        const r = { chalutier: monte('chalutier'), chaloupe: monte('bateau'), vedette: monte('vedette') };
        E.contexte = vrai;
        return r;
    }""")
    assert r["chalutier"]["e"]["attaque"] == "CORNE", r["chalutier"]
    assert r["chaloupe"]["e"]["attaque"] == "KLAXON", r["chaloupe"]
    assert r["chalutier"]["e"]["esquive"] == "·", f"une coque a encore un FREIN sous l'esquive : {r['chalutier']}"
    assert r["vedette"]["e"]["attaque"] == "SIRÈNE", r["vedette"]


def test_on_monte_a_bord_a_pied_et_le_chalutier_tourne_au_diesel(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), j = L.B.joueur, S = L.Son;
        let aBord = 0, bequille = 0; const lieux = [], boucles = [];
        const vrais = [S.SFX.aBord, S.SFX.enfourcher, S.Lieu.charger, S.boucle, S.estCharge];
        S.SFX.aBord = function () { aBord++; }; S.SFX.enfourcher = function () { bequille++; };
        S.Lieu.charger = function (l) { lieux.push(l); };
        S.boucle = function (slug, actif) { boucles.push([slug, !!actif]); };
        let diesel = true; S.estCharge = function (slug) { return slug === 'moteur_diesel' ? diesel : vrais[4].apply(S, arguments); };
        const c = coque(L, 'chalutier', p); L.Vehicules.monter(j, c);
        const chalutier = boucles.filter(function (b) { return b[1]; }).map(function (b) { return b[0]; });
        boucles.length = 0; L.Vehicules.descendre(j, true);
        const coupe = boucles.some(function (b) { return b[0] === 'moteur_diesel' && !b[1]; });
        L.Entites.retirer(c);
        boucles.length = 0; diesel = false;
        const d = coque(L, 'chalutier', p); L.Vehicules.monter(j, d);
        const sansDiesel = boucles.filter(function (b) { return b[1]; }).map(function (b) { return b[0]; });
        L.Vehicules.descendre(j, true); L.Entites.retirer(d);
        boucles.length = 0;
        const ch = coque(L, 'bateau', p); L.Vehicules.monter(j, ch);
        const chaloupe = boucles.filter(function (b) { return b[1]; }).map(function (b) { return b[0]; });
        [S.SFX.aBord, S.SFX.enfourcher, S.Lieu.charger, S.boucle, S.estCharge] = vrais;
        return { aBord: aBord, bequille: bequille, lieux: lieux, chalutier: chalutier, coupe: coupe, sansDiesel: sansDiesel, chaloupe: chaloupe };
    }""")
    assert r["aBord"] >= 1 and r["bequille"] == 0, f"on enfourche une coque comme un vélo : {r}"
    assert "bateaux" in r["lieux"], "les sons des bateaux ne se chargent pas en montant à bord"
    assert "moteur_diesel" in r["chalutier"], f"le chalutier tourne au hors-bord : {r['chalutier']}"
    assert r["coupe"], "le diesel tourne encore quand on descend"
    assert "moteur_bateau" in r["sansDiesel"], f"sans le diesel chargé, le chalutier est muet : {r['sansDiesel']}"
    assert "moteur_bateau" in r["chaloupe"] and "moteur_diesel" not in r["chaloupe"], r["chaloupe"]


def test_les_feux_de_navigation_rouge_a_babord_vert_a_tribord_blanc_a_la_poupe(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const hex = function (c) { return [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)]; };
        const out = {};
        ['bateau', 'chalutier', 'porte_conteneurs', 'vedette'].forEach(function (slug) {
            const def = L.Vehicules.vehiculeDef(slug);
            const lampes = L.Vehicules.lampesDeLaMachine(def.sprite);
            out[slug] = lampes.map(function (l) { return { lettre: l.lettre, w: l.w, rgb: hex(l.teinte) }; });
        });
        return out;
    }""")
    for slug, lampes in r.items():
        rouges = [x for x in lampes if x["lettre"] == "J"]
        verts = [x for x in lampes if x["lettre"] == "Z"]
        poupe = [x for x in lampes if x["lettre"] == "t"]
        assert rouges and verts, f"{slug} n'a pas ses feux de côté : {lampes}"
        assert all(x["w"] < 0 for x in rouges) and all(x["w"] > 0 for x in verts), f"{slug} : rouge à tribord ? {lampes}"
        assert all(x["rgb"][0] > 180 and x["rgb"][1] < 110 for x in rouges), f"{slug} : le feu de bâbord n'est pas rouge"
        assert all(x["rgb"][1] > 160 and x["rgb"][0] < 140 for x in verts), f"{slug} : le feu de tribord n'est pas vert"
        assert poupe and all(min(x["rgb"]) > 200 for x in poupe), f"{slug} : le feu de poupe n'est pas blanc : {poupe}"


def test_une_coque_en_epave_coule(banc):
    """Détruite, une coque coule et s'efface en quelques secondes — elle ne flotte plus en fumant quarante."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = pleinLarge(L), j = L.B.joueur;
        j.x = p.x; j.y = p.y - 60; L.Monde.centrerCamera(p.x, p.y); j.invincible = 99999;
        const v = L.Vehicules.creer('bateau', p.x, p.y, 0, { etat: 'stationne' });
        let naufrage = 0; const vrai = L.Naufrage.poser; L.Naufrage.poser = function () { naufrage++; return vrai.apply(this, arguments); };
        L.Vehicules.endommager(v, 99999);
        const epave = v.etat === 'epave';
        o.frame(300);
        L.Naufrage.poser = vrai;
        return { epave: epave, encore: L.B.entites.indexOf(v) >= 0, naufrage: naufrage };
    }""")
    assert r["epave"], "la coque n'est pas devenue une épave"
    assert not r["encore"], "l'épave d'une coque flotte encore après cinq secondes"
    assert r["naufrage"] == 1, "l'épave s'efface sans couler (ni bulle ni tache d'huile)"
