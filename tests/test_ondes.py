"""M15, 2e vague — ce qui passe sur les ondes : la radio qui parle, et la police.

⚠️ Les douze clips de radio (animateurs de La Brume et de Taxi-Radio, six pubs)
étaient générés, déclarés et téléchargés au démarrage depuis le 16 sept. 2026 —
et aucune ligne du jeu ne les jouait. Les juges d'ici regardent donc ce qui PASSE
(`Son.Ondes.dites`), pas ce qui est déclaré.
"""

from app import audio, economie, missions


def _voix(genre):
    return [v for v in audio.VOIX + audio.VOIX_DE_LA_POLICE if v["genre"] == genre]


# --- Les fiches ----------------------------------------------------------------------


def test_les_stations_qui_parlent_ont_de_quoi_dire():
    """Chaque station qui parle existe, et chaque sorte de clip qu'elle dit en
    compte au moins deux : à tour de rôle, une seule réplique serait un disque rayé."""
    stations = audio.ONDES["stations"]
    assert stations, "aucune station ne parle"
    for station, genres in stations.items():
        assert audio.station_existe(station), f"{station} n'est pas une station"
        for genre in genres:
            assert len(_voix(genre)) >= 2, f"{station} dit des « {genre} » et n'en a pas deux"
    assert "le_choc" not in stations, "personne au micro du Choc : c'est le propos de la station"


def test_l_animateur_laisse_passer_deux_tounes():
    """« Un clip toutes les deux ou trois boucles » : ni un animateur qui ne
    lâche pas le micro, ni une station où l'on n'entend jamais personne."""
    boucles = [r["duree_s"] for r in audio.RADIOS if r["slug"] in audio.ONDES["stations"]]
    bas, haut = audio.ONDES["intervalle_s"]
    assert bas >= 1.5 * max(boucles), "l'animateur parle entre chaque toune"
    assert haut <= 3.5 * min(boucles), "on attend plus de trois tounes pour entendre quelqu'un"
    assert audio.ONDES["premiere_s"] < bas, "la première voix doit venir vite : on sait qu'on est à la radio"


def test_une_jumelle_a_toi_vise_un_commerce_qui_s_achete():
    """⚠️ Les premières jumelles annonçaient Chez Gus, Boutique Rosa et Ti-Paul
    « sous nouvelle administration » — trois commerces que personne ne peut
    acheter : elles ne pouvaient jamais jouer."""
    achetables = {p["slug"] for p in economie.PROPRIETES}
    pubs = _voix("pub")
    for pub in pubs:
        if pub.get("a_toi"):
            assert pub.get("propriete"), f"{pub['slug']} : une jumelle « à toi » sans propriété"
        if pub.get("propriete"):
            assert pub["propriete"] in achetables, f"{pub['slug']} : « {pub['propriete']} » ne s'achète pas"
    visees = {p["propriete"] for p in pubs if p.get("propriete")}
    assert visees, "aucune pub ne change quand on achète"
    for propriete in visees:
        les_deux = [p for p in pubs if p.get("propriete") == propriete]
        assert sorted(bool(p.get("a_toi")) for p in les_deux) == [False, True], \
            f"{propriete} : il faut sa pub ET sa jumelle, une de chaque"


def test_la_police_a_deux_repliques_par_evenement():
    evenements = set(audio.EVENEMENTS_DE_POLICE)
    for v in audio.VOIX_DE_LA_POLICE:
        assert v["evenement"] in evenements, f"{v['slug']} : événement inconnu"
    for evenement in evenements:
        assert len([v for v in audio.VOIX_DE_LA_POLICE if v["evenement"] == evenement]) >= 2, evenement


def test_la_police_n_a_la_voix_ni_d_un_passant_ni_d_un_personnage():
    """Une voix de la rue au bout du scanner, on croirait que la passante d'à côté
    appelle la police ; celle d'un personnage, qu'il s'est fait engager."""
    prises = {v["voix"] for v in audio.VOIX} | {p["voix"] for p in missions.PERSONNAGES}
    for v in audio.VOIX_DE_LA_POLICE:
        assert v["voix"] not in prises, f"{v['slug']} parle avec la voix de {v['voix']}"


def test_le_paquet_porte_ce_que_les_ondes_lisent():
    exporte = {v["slug"]: v for v in audio.exporter()["voix"]}
    for v in audio.VOIX_DE_LA_POLICE:
        assert exporte[v["slug"]]["evenement"] == v["evenement"]
    for v in _voix("pub"):
        assert exporte[v["slug"]].get("propriete") == v.get("propriete")
        assert bool(exporte[v["slug"]].get("a_toi")) == bool(v.get("a_toi"))
    assert audio.exporter()["ondes"]["stations"] == audio.ONDES["stations"]
    # ⚠️ Ce qui passe sur les ondes ne s'affiche nulle part : son texte ne voyage
    # pas (le paquet est a son plafond). Une bulle de passant, elle, le garde.
    for v in audio.VOIX + audio.VOIX_DE_LA_POLICE:
        assert ("texte" in exporte[v["slug"]]) is (v["genre"] not in audio.GENRES_DES_ONDES), v["slug"]


# --- Au banc -------------------------------------------------------------------------

#: Allume une station et fait tourner les ondes `secondes` secondes, image par
#: image, en comptant les dés tirés. Rend ce qui est passé.
_ECOUTER = """
    function ecouter(L, station, secondes, pendant) {
        L.Son.Radio.jouer(station);
        let des = 0;
        const rng = L.B.rng;
        L.B.rng = function () { des++; return rng(); };
        const t0 = L.B.t;
        for (let i = 0; i < secondes * 60; i++) {
            L.B.t++;
            if (pendant) pendant(L.B.t - t0);
            L.Son.Ondes.maj();
        }
        L.B.rng = rng;
        return { des: des, dites: L.Son.Ondes.dites.map(function (d) { return { slug: d.slug, t: d.t - t0, bande: d.bande }; }) };
    }
"""


def test_la_radio_parle_entre_les_tounes(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        return ecouter(L, 'taxi_radio', 600);
    }""" % _ECOUTER)
    dites = r["dites"]
    assert r["des"] == 0, "les ondes tirent des dés : tout le hasard du jeu se décale"
    assert len(dites) >= 4, f"la radio ne parle pas : {dites}"
    reglages = audio.ONDES
    assert abs(dites[0]["t"] - reglages["premiere_s"] * 60) <= 1, "la première voix n'arrive pas à l'heure"
    for a, b in zip(dites, dites[1:]):
        ecart = (b["t"] - a["t"]) / 60
        assert reglages["intervalle_s"][0] <= ecart <= reglages["intervalle_s"][1], f"{ecart} s entre deux voix"
    genres = {v["slug"]: v["genre"] for v in audio.VOIX}
    assert [genres[d["slug"]] for d in dites[:4]] == ["radio_taxi", "pub", "radio_taxi", "pub"], dites
    animateur = [d["slug"] for d in dites if genres[d["slug"]] == "radio_taxi"]
    assert len(set(animateur[:3])) == min(3, len(animateur)), f"l'animateur se répète avant d'avoir tout dit : {animateur}"
    assert all(d["bande"] == "radio" for d in dites)


def test_la_radio_parle_aussi_dans_la_vraie_partie(banc):
    """Le même geste, par la boucle du jeu : `jeu.js` appelle bien les ondes."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Son.Radio.jouer('la_brume');
        o.frame(%d);
        return L.Son.Ondes.dites.map(function (d) { return d.slug; });
    }""" % (audio.ONDES["premiere_s"] * 60 + 30))
    genres = {v["slug"]: v["genre"] for v in audio.VOIX}
    assert r and genres[r[0]] == "radio_brume", f"La Brume ne parle pas en jouant : {r}"


def test_le_choc_ne_parle_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        return ecouter(L, 'le_choc', 400);
    }""" % _ECOUTER)
    assert r["dites"] == [], "quelqu'un parle au micro du Choc"


def test_la_radio_attend_la_fin_d_une_replique_de_mission(banc):
    """⚠️ La mission passe devant tout le monde : tant qu'une réplique joue,
    l'animateur garde son clip pour après."""
    premiere = audio.ONDES["premiere_s"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const mission = { slug: 'essai' };
        return ecouter(L, 'taxi_radio', %d, function (t) {
            L.Son.Voix.enCours = t < %d ? mission : null;
        });
    }""" % (_ECOUTER, premiere + 30, (premiere + 10) * 60))
    assert len(r["dites"]) == 1, r
    assert r["dites"][0]["t"] >= (premiere + 10) * 60, "l'animateur a parlé par-dessus la mission"


def test_la_pub_de_ton_bar_dit_que_c_est_le_tien(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const tour = function () {
            const vus = [];
            for (let i = 0; i < 12; i++) { const v = L.Son.Ondes.pub(); if (v) vus.push(v.slug); }
            return vus;
        };
        const avant = tour();
        L.B.partie.proprietes.bar = { jour: 1, caisse: 0 };
        return { avant: avant, apres: tour() };
    }""")
    assert "pub_bar_r" in r["avant"] and "pub_bar_a_toi_r" not in r["avant"], r["avant"]
    assert "pub_bar_a_toi_r" in r["apres"], f"la radio annonce ton bar comme s'il était encore à vendre : {r['apres']}"
    assert "pub_bar_r" not in r["apres"], r["apres"]
    assert "pub_garage_r" in r["apres"], "posséder le bar a changé la pub du garage"


def test_la_police_parle_a_la_radio(banc):
    """Les étoiles, l'hélico et le barrage passent par le scanner — par le vrai
    chemin de `police.js`, pas en appelant les ondes à la main."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite(), r = L.B.recherche, dit = {};
        j.x = d.x; j.y = d.y; j.intouchable = true;
        L.B.defs.conduite.trafic.vehicules_max = 0;
        L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(function (e) { L.Entites.retirer(e); });
        const dernier = function () { const l = L.Son.Ondes.dites; return l.length ? l[l.length - 1].slug : null; };
        const attendre = function () { L.B.t += 60 * 60; };
        L.Police.etoilesAuMoins(1); dit.repere = dernier(); attendre();
        L.Police.etoilesAuMoins(3); dit.poursuite = dernier(); attendre();
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v); v.vitesse = 3;
        L.Police.poserBarrage(v); dit.barrage = dernier(); attendre();
        r.etoiles = 5; L.B.t -= L.B.t % 60;
        L.Police.maj(); dit.helico = dernier(); attendre();
        r.etoiles = 1; r.vu = 1e9;
        L.Police.maj(); dit.perdu = dernier();
        return dit;
    }""")
    evenements = {v["slug"]: v["evenement"] for v in audio.VOIX_DE_LA_POLICE}
    for evenement, slug in r.items():
        assert slug and evenements.get(slug) == evenement, f"{evenement} : la radio a dit {slug}"


def test_le_scanner_n_est_pas_une_alarme(banc):
    """Deux messages ne se collent pas, le même événement ne se redit pas à chaque
    étoile, et il revient ensuite avec son autre réplique. Jamais par-dessus une
    réplique de mission."""
    repos = audio.ONDES["police_repos_s"]
    mort = audio.ONDES["police_temps_mort_s"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const O = L.Son.Ondes, dit = [];
        dit.push(O.police('repere'));
        L.B.t += 60;          dit.push(O.police('barrage'));         // colle au premier
        L.B.t += %d * 60;     dit.push(O.police('repere'));          // trop tot pour le meme
        L.B.t += %d * 60;     dit.push(O.police('repere'));          // son autre replique
        L.B.t += %d * 60;
        L.Son.Voix.enCours = { slug: 'mission' };
        dit.push(O.police('helico'));                                // une mission parle
        L.Son.Voix.enCours = null;
        return dit;
    }""" % (mort, repos, repos))
    assert r[0] == "police_repere_1_r"
    assert r[1] is None, "deux messages collés"
    assert r[2] is None, "le même événement redit à chaque étoile"
    assert r[3] == "police_repere_2_r", "à tour de rôle, la deuxième réplique vient après la première"
    assert r[4] is None, "le scanner parle par-dessus une réplique de mission"


def test_une_replique_de_mission_coupe_les_ondes(banc):
    """Avec du son : ce qui passe sur les ondes ATTEINT la sortie, baisse la
    musique, et se tait quand une réplique de mission commence."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        L.Son.Voix.charger();
        for (let i = 0; i < 6; i++) await o.attendre();
        const clip = L.Son.Voix.liste().find(function (v) { return v.genre === 'radio_taxi' && v.fichier; });
        if (!clip) return { clip: null };
        const passe = L.Son.Ondes.dire(clip, 'radio');
        const ctx = L.Son.contexte;
        const sortie = !!passe && ctx.atteintLaSortie(passe.source);
        const baisse = L.Son.Ondes.enCours !== null;
        L.Son.Voix.parler('inexistante');
        return { clip: clip.slug, sortie: sortie, baisse: baisse, apres: L.Son.Ondes.enCours };
    }""")
    assert r["clip"], "aucun clip de Taxi-Radio sur le disque : le juge ne mesure rien"
    assert r["sortie"] is True, "l'animateur « parle » et on n'entend rien"
    assert r["baisse"] is True
    assert r["apres"] is None, "une réplique de mission a commencé et la radio parle encore"
