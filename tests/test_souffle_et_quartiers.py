"""M15, 2e vague — on s'entend respirer, et un quartier s'entend avant de se voir.

Deux sons qui ne disent rien de neuf et rendent lisible ce qui ne l'était qu'à
l'oeil : la barre d'endurance (le souffle), et le district où l'on est (ses bruits).
"""

from app import audio, carte


# --- Les fiches ----------------------------------------------------------------------


def test_chaque_district_s_entend():
    """Trois bruits ou plus par district, tous au catalogue, et au moins un qui
    n'a pas d'heures : un quartier qui se tait toute la nuit n'a pas de nuit."""
    sons = audio.QUARTIERS["sons"]
    for district in (d["slug"] for d in carte.DISTRICTS):
        assert district in sons, f"{district} ne s'entend pas"
        assert len(sons[district]) >= 3, f"{district} n'a que {len(sons[district])} bruit(s)"
        assert any("heures" not in e for e in sons[district]), f"{district} se tait toute la nuit"
        for e in sons[district]:
            fiche = audio.par_slug(e["slug"])
            assert fiche, f"{district} : « {e['slug']} » n'est pas au catalogue"
            assert not fiche["boucle"], f"{e['slug']} : un bruit de quartier est un événement, pas une nappe"
    assert set(sons) <= {d["slug"] for d in carte.DISTRICTS}, "un bruit pour un district qui n'existe pas"


def test_on_ne_tond_pas_son_gazon_a_trois_heures_du_matin():
    for district, liste in audio.QUARTIERS["sons"].items():
        for e in liste:
            if "heures" in e:
                debut, fin = e["heures"]
                assert 0 <= debut < 1 and 0 <= fin <= 1, f"{district}/{e['slug']} : heures hors de la journée"
    tondeuse = [e for e in audio.QUARTIERS["sons"]["erables"] if e["slug"] == "tondeuse"][0]
    assert tondeuse["heures"][0] > 0.3 and tondeuse["heures"][1] < 0.85


def test_le_souffle_se_lit_sans_regarder_la_barre():
    s = audio.SOUFFLE
    assert 0 < s["seuil"] < 0.6, "on ne s'entend respirer qu'essoufflé — mais on doit s'entendre"
    assert s["bas"] < s["reprise"], "le souffle repart plus haut qu'il n'est tombé"
    assert s["descend_par_image"] < s["monte_par_image"], "on halète encore un moment après s'être arrêté"
    assert audio.par_slug("souffle")["boucle"] is True
    assert audio.par_slug("reprise")["boucle"] is False


# --- Au banc -------------------------------------------------------------------------


def test_le_souffle_monte_puis_repart(banc):
    """Par la vraie boucle du jeu : essoufflé, on s'entend haleter ; la barre
    remonte, le halètement redescend DOUCEMENT, et une inspiration dit qu'on peut
    de nouveau courir — une seule."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, max = L.B.defs.recherche.vitesses.endurance, S = L.Son.Souffle;
        const avant = S.volume;
        j.endurance = 0.05 * max;
        let haut = 0, auRepos = null, reprisesA = null;
        for (let i = 0; i < 600; i++) {
            o.frame(1);
            haut = Math.max(haut, S.volume);
            if (auRepos === null && j.endurance >= (1 - L.B.defs.audio.souffle.seuil) * max) auRepos = S.volume;
            if (reprisesA === null && S.reprises > 0) reprisesA = j.endurance / max;
        }
        return { avant: avant, haut: haut, auRepos: auRepos, reprises: S.reprises, reprisesA: reprisesA,
                 fin: S.volume, endurance: j.endurance / max };
    }""")
    reglages = audio.SOUFFLE
    assert r["avant"] == 0, "on s'entend respirer avant d'avoir couru"
    assert r["haut"] > 0.5, f"essoufflé, on ne s'entend pas haleter ({r['haut']})"
    assert r["auRepos"] is not None and r["auRepos"] > 0.1, \
        f"le halètement s'est coupé net à la seconde où la barre est remontée : {r}"
    assert r["reprises"] == 1, f"{r['reprises']} inspirations pour une seule reprise de souffle"
    assert abs(r["reprisesA"] - reglages["reprise"]) < 0.02, f"le souffle repart à {r['reprisesA']}"
    assert r["fin"] == 0 and r["endurance"] > 0.9


def test_au_volant_on_ne_s_entend_pas_respirer(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, S = L.Son.Souffle;
        L.Vehicules.monter(j, o.char('auto', 24, 0, 0));
        j.endurance = 0;
        for (let i = 0; i < 120; i++) S.maj(j);
        return S.volume;
    }""")
    assert r == 0, "on halète au volant"


#: Pose le joueur dans `district` (une tuile de chaussée ou de trottoir), fait
#: tourner les bruits de quartier `secondes` secondes a `heure`, en comptant les dés.
_ECOUTER = """
    function ecouter(L, district, heure, secondes, dedans) {
        const c = L.Monde.carte, j = L.B.joueur, TT = L.TT;
        let place = null;
        for (let y = 2; y < c.h - 2 && !place; y += 3) {
            for (let x = 2; x < c.w - 2 && !place; x += 3) {
                const z = L.Monde.zoneA(x * TT + 8, y * TT + 8);
                if (z && z.district === district) place = { x: x * TT + 8, y: y * TT + 8 };
            }
        }
        if (!place) return { place: null };
        j.x = place.x; j.y = place.y;
        L.B.partie.heure = heure;
        L.B.interieur = dedans ? {} : null;
        L.Son.Quartier.entendus.length = 0;
        let des = 0;
        const rng = L.B.rng;
        L.B.rng = function () { des++; return rng(); };
        const t0 = L.B.t;
        for (let i = 0; i < secondes * 60; i++) { L.B.t++; L.B.partie.heure = heure; L.Son.Quartier.maj(); }
        L.B.rng = rng;
        L.B.interieur = null;
        return { place: place, des: des, entendus: L.Son.Quartier.entendus.map(function (e) {
            return { slug: e.slug, t: e.t - t0, district: e.district, d: Math.hypot(e.x - place.x, e.y - place.y) }; }) };
    }
"""


def test_un_quartier_s_entend_avant_de_se_voir(banc):
    districts = [d["slug"] for d in carte.DISTRICTS if d["slug"] != "baie"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const vus = {};
        for (const d of %s) vus[d] = ecouter(L, d, 0.5, 240);
        return vus;
    }""" % (_ECOUTER, repr(districts)))
    q = audio.QUARTIERS
    for district, vu in r.items():
        assert vu["place"], f"aucune tuile de {district} : le juge ne mesure rien"
        assert vu["des"] == 0, f"{district} : les bruits de quartier tirent des dés"
        entendus = vu["entendus"]
        assert len(entendus) >= 4, f"{district} ne s'entend pas : {entendus}"
        sien = {e["slug"] for e in q["sons"][district]}
        a_midi = [e for e in q["sons"][district] if "heures" not in e or e["heures"][0] <= 0.5 < e["heures"][1]]
        assert all(e["district"] == district and e["slug"] in sien for e in entendus), entendus
        for a, b in zip(entendus, entendus[1:]):
            assert q["intervalle_s"][0] * 60 <= b["t"] - a["t"] <= q["intervalle_s"][1] * 60, entendus
        # À tour de rôle : on a tout entendu avant d'entendre deux fois la même chose.
        premiers = [e["slug"] for e in entendus[:len(a_midi)]]
        assert len(set(premiers)) == len(premiers), f"{district} se répète avant d'avoir tout dit : {premiers}"
        assert all(abs(e["d"] - q["distance_px"]) < 1 for e in entendus), "le bruit ne vient pas de loin"


def test_la_nuit_le_quartier_a_d_autres_bruits(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        return { nuit: ecouter(L, 'erables', 0.1, 240), dedans: ecouter(L, 'erables', 0.5, 240, true) };
    }""" % _ECOUTER)
    de_jour = {e["slug"] for e in audio.QUARTIERS["sons"]["erables"] if "heures" in e}
    nuit = [e["slug"] for e in r["nuit"]["entendus"]]
    assert nuit, "les Érables se taisent toute la nuit"
    assert not set(nuit) & de_jour, f"on tond son gazon la nuit : {nuit}"
    assert r["dedans"]["entendus"] == [], "on entend la rue à travers les murs d'une pièce"


def test_les_bruits_de_quartier_ne_se_chargent_pas_au_demarrage(banc):
    """⚠️ Treize sons de plus au premier geste doublerait presque le budget des
    bruitages (2,83 Mo pour 2,5 Mo) — `Quartier.charger` les demande un
    district à la fois, en y entrant, jamais tous ensemble."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        L.Son.chargerEchantillons();
        for (let i = 0; i < 6; i++) await o.attendre();
        const slugs = new Set();
        Object.values(L.B.defs.audio.quartiers.sons).forEach(function (l) {
            l.forEach(function (e) { slugs.add(e.slug); });
        });
        const avant = [...slugs].filter(function (s) { return L.Son.estCharge(s); });
        const zone = L.Monde.zoneA(L.B.joueur.x, L.B.joueur.y);
        L.Son.Quartier.charger(zone.district);
        for (let i = 0; i < 6; i++) await o.attendre();
        const apres = (L.B.defs.audio.quartiers.sons[zone.district] || [])
            .filter(function (e) { return L.Son.estCharge(e.slug); }).length;
        return { avant: avant, district: zone.district, apres: apres,
                 total: (L.B.defs.audio.quartiers.sons[zone.district] || []).length };
    }""")
    assert r["avant"] == [], f"des bruits de quartier sont déjà là au premier geste : {r['avant']}"
    assert r["apres"] == r["total"] > 0, f"{r['district']} : {r['apres']}/{r['total']} chargés après y être entré"


def test_la_vraie_boucle_du_jeu_fait_vivre_le_souffle_et_les_quartiers(banc):
    """`jeu.js` appelle bien `Son.Souffle.maj` et `Son.Quartier.maj` — pas
    seulement mes propres appels directs dans les juges d'au-dessus."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        j.endurance = 0;
        L.B.partie.heure = 0.5;
        L.B.defs.audio.quartiers.intervalle_s = [0.1, 0.1];   // avant le premier tour
        o.frame(30);
        const souffle = L.Son.Souffle.volume;
        o.frame(60);
        return { souffle: souffle, quartier: L.Son.Quartier.entendus.length };
    }""")
    assert r["souffle"] > 0, "jeu.js n'appelle jamais Son.Souffle.maj"
    assert r["quartier"] > 0, "jeu.js n'appelle jamais Son.Quartier.maj"


def test_un_district_ne_se_recharge_pas_a_chaque_bruit(banc):
    """`Quartier.charger` ne redemande le réseau qu'une fois par district — pas
    à chaque coup dans `Quartier.maj` — sinon chaque bruit de quartier
    retéléchargerait tout son quartier. Compte les VRAIES requêtes (`o.fetchs`),
    pas seulement `chargees.size` (un `Set` n'enfle pas si on rajoute deux fois
    ce qui y est déjà, même sans le garde)."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        const zone = L.Monde.zoneA(L.B.joueur.x, L.B.joueur.y);
        const avant = o.fetchs.length;
        L.Son.Quartier.charger(zone.district);
        const apresUn = o.fetchs.length;
        L.Son.Quartier.charger(zone.district);
        L.Son.Quartier.charger(zone.district);
        return { premiere: apresUn - avant, ensuite: o.fetchs.length - apresUn };
    }""")
    assert r["premiere"] > 0, "entrer dans un district ne télécharge rien : le juge ne mesure rien"
    assert r["ensuite"] == 0, f"redemander le même district retéléphone : {r['ensuite']} requêtes de plus"


def test_le_souffle_s_entend_vraiment(banc):
    """Avec du son : la boucle joue, atteint la sortie, et s'éteint quand on a
    repris son souffle."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        L.Son.chargerEchantillons();
        for (let i = 0; i < 6; i++) await o.attendre();
        const j = L.B.joueur, S = L.Son.Souffle;
        if (!L.Son.estCharge('souffle')) return { charge: false };
        j.endurance = 0;
        for (let i = 0; i < 60; i++) S.maj(j);
        const joue = L.Son.boucleActive('souffle');
        const volume = L.Son.volumeBoucle('souffle');
        j.endurance = L.B.defs.recherche.vitesses.endurance;
        for (let i = 0; i < 600; i++) S.maj(j);
        return { charge: true, joue: joue, volume: volume, apres: L.Son.boucleActive('souffle') };
    }""")
    assert r["charge"], "le souffle n'est pas sur le disque : le juge ne mesure rien"
    assert r["joue"] is True and r["volume"] > 0, r
    assert r["apres"] is False, "on halète encore, souffle repris depuis dix secondes"
