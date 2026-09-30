"""M15, 2e vague — ce qui passe sur les ondes : la radio qui parle, et la police.

⚠️ Les douze clips de radio (animateurs de La Brume et de Taxi-Radio, six pubs)
étaient générés, déclarés et téléchargés au démarrage depuis le 16 sept. 2026 —
et aucune ligne du jeu ne les jouait. Les juges d'ici regardent donc ce qui PASSE
(`Son.Ondes.dites`), pas ce qui est déclaré.
"""

import re

import pytest

from app import audio, economie, journal, missions


def _voix(genre):
    return [v for v in audio.VOIX + audio.VOIX_DE_LA_POLICE if v["genre"] == genre]


# --- Les fiches ----------------------------------------------------------------------


def test_les_stations_qui_parlent_ont_de_quoi_dire():
    """Chaque station qui parle existe, et chaque sorte de clip qu'elle dit en
    compte au moins deux : à tour de rôle, une seule réplique serait un disque rayé.

    ⚠️ **Sauf ce qui n'a pas de clip à lui** (`audio.GENRES_SANS_CLIP`) : le bulletin
    de nouvelles rejoue la manchette du Clairon, et c'est exactement ce qui le rend
    gratuit. Le juge ne l'excuse pas, il exige le contraire — un `bulletin` qui se
    mettrait à avoir ses propres clips aurait cessé d'être ce bulletin-là."""
    stations = audio.ONDES["stations"]
    assert stations, "aucune station ne parle"
    for station, genres in stations.items():
        assert audio.station_existe(station), f"{station} n'est pas une station"
        for genre in genres:
            if genre in audio.GENRES_SANS_CLIP:
                assert not _voix(genre), f"{genre} a des clips à lui : il ne rejoue plus rien"
                continue
            assert len(_voix(genre)) >= 2, f"{station} dit des « {genre} » et n'en a pas deux"
    assert "le_choc" not in stations, "personne au micro du Choc : c'est le propos de la station"


def test_le_bulletin_lit_une_nouvelle_et_jamais_une_lecon():
    """⚠️ **LE BULLETIN NE COÛTE PAS UN CLIP** : il rejoue la voix que le narrateur a
    déjà pour la manchette du matin — donc il faut qu'il en ait une pour **chacune**,
    sans quoi la radio se tairait les jours où il s'est passé quelque chose.

    ⚠️ Et une **leçon** n'est pas une nouvelle : « Le saviez-vous? Un coup de klaxon
    dans un taxi vous trouve un client » à la radio, ce n'est pas un bulletin, c'est
    un mode d'emploi. Le repli du Clairon enseigne ; la station, elle, joue sa
    musique."""
    assert "bulletin" in audio.GENRES_SANS_CLIP
    assert any("bulletin" in genres for genres in audio.ONDES["stations"].values()), \
        "aucune station ne lit les nouvelles"
    dites = {v["slug"] for v in audio.voix_journal()}
    for manchette in journal.REGLES + journal.SPECIALES + journal.MATINS:
        assert f"narrateur-journal-{manchette['slug']}" in dites, \
            f"{manchette['slug']} : le narrateur n'a pas de voix, la radio ne pourra pas la lire"
    # ⚠️ Le repos est ce qui empêche le bulletin de devenir une alarme : la manchette
    # ne change qu'au lever du jour, et sans repos la station la redirait entre
    # chaque paire de tounes.
    assert audio.ONDES["bulletin_repos_s"] > audio.ONDES["intervalle_s"][1], \
        "le bulletin repasse avant la voix suivante : c'est une alarme, pas une nouvelle"


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
    for v in audio.VOIX_DE_LA_POLICE:
        assert audio.VOIX_RESERVEES.get(v["voix"]) == "police", f"{v['slug']} : {v['voix']} n'est pas reservee"
    assert audio.voix_partagees_a_tort() == []


def test_une_voix_reservee_prise_ailleurs_se_voit():
    """La table n'est bonne que si elle mord : Frederic donne au Grand Mo."""
    mo = missions.personnage("mo")
    avant = mo["voix"]
    try:
        mo["voix"] = audio.VOIX_AGENT
        assert any("mo" in e and audio.VOIX_AGENT in e for e in audio.voix_partagees_a_tort())
    finally:
        mo["voix"] = avant


def test_le_paquet_porte_ce_que_les_ondes_lisent():
    exporte = {v["slug"]: v for v in audio.exporter()["voix"]}
    for v in audio.VOIX_DE_LA_POLICE:
        assert exporte[v["slug"]]["evenement"] == v["evenement"]
    for v in audio.VOIX:
        assert exporte[v["slug"]].get("meteo") == v.get("meteo"), v["slug"]
    for v in _voix("pub"):
        assert exporte[v["slug"]].get("propriete") == v.get("propriete")
        assert bool(exporte[v["slug"]].get("a_toi")) == bool(v.get("a_toi"))
    assert audio.exporter()["ondes"]["stations"] == audio.ONDES["stations"]
    # ⚠️ Ce qui passe sur les ondes ne s'affiche nulle part : son texte ne voyage
    # pas (le paquet est a son plafond). Une bulle de passant, elle, le garde.
    for v in audio.VOIX + audio.VOIX_DE_LA_POLICE:
        assert ("texte" in exporte[v["slug"]]) is (v["genre"] not in audio.GENRES_DES_ONDES), v["slug"]


#: Les animateurs : ce qu'une station dit d'elle-meme, hors pubs et bulletin.
_ANIMATEURS = sorted({g for genres in audio.ONDES["stations"].values() for g in genres
                      if g.startswith("radio_")})

#: Les mots du temps qu'il fait. ⚠️ « La Brume » est le nom d'une station, pas un ciel :
#: il n'y est pas.
_MOTS_DU_TEMPS = re.compile(
    r"\b(pluie|pleut|mouille|averse|orage|neige|neigeux|tempête|poudrerie|charrue|verglas|glacé|glace"
    r"|brouillard|fait beau|beau temps|soleil|canicule|chaleur|frette)\b", re.IGNORECASE)


def test_une_replique_qui_parle_du_temps_porte_sa_meteo():
    """⚠️ Taxi-Radio criait « y fait beau à Baie-des-Brumes! » en pleine tempête de neige,
    et La Brume annonçait la pluie un soir de janvier sec (Martin, 30 sept. 2026). Une
    réplique d'animateur qui nomme le temps porte sa `meteo`, sans quoi elle passerait
    par tous les ciels ; une `meteo` est un ciel que les ondes savent lire."""
    for genre in _ANIMATEURS:
        for v in _voix(genre):
            if "meteo" in v:
                assert v["meteo"] in audio.METEOS, f"{v['slug']} : « {v['meteo']} » n'est pas un ciel"
            else:
                assert not _MOTS_DU_TEMPS.search(v["texte"]), \
                    f"{v['slug']} parle du temps sans dire lequel : « {v['texte']} »"


def test_une_replique_d_un_ciel_ne_part_pas_au_demarrage():
    """⚠️ Le premier écran n'avait plus que 6 Ko de marge (`test_le_poids_audio_reste_raisonnable`) :
    une réplique qui dit la tempête ne sert qu'un soir de tempête, elle arrive avec son ciel
    (`Son.Voix.chargerMeteo`), comme une réplique de contexte arrive avec son contexte."""
    a_la_volee = {v["slug"] for v in audio.voix_a_la_volee()}
    marquees = [v["slug"] for v in audio.VOIX if v.get("meteo")]
    assert marquees
    assert set(marquees) <= a_la_volee, set(marquees) - a_la_volee


def test_par_tous_les_temps_l_animateur_a_de_quoi_dire():
    """Sous chaque ciel, chaque animateur garde au moins deux répliques : une réplique
    marquée qui se tait ne doit pas laisser un disque rayé derrière elle."""
    for genre in _ANIMATEURS:
        for ciel in audio.METEOS:
            dites = [v["slug"] for v in _voix(genre) if v.get("meteo") in (None, ciel)]
            assert len(dites) >= 2, f"{genre} sous « {ciel} » : {dites}"


# --- Au banc -------------------------------------------------------------------------
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
        return { des: des, dites: L.Son.Ondes.dites.map(function (d) { return { slug: d.slug, t: d.t - t0, bande: d.bande, banque: d.banque }; }) };
    }
"""


@pytest.fixture(scope="module")
def ecoutes(banc):
    """⚠️ **UN BANC POUR LES SIX JUGES QUI ÉCOUTENT UNE STATION** (vague C, 28 sept. 2026) : ils
    commençaient chacun une partie pour allumer une radio et compter ce qui passait. Une partie
    ici, et six écoutes l'une après l'autre.

    ⚠️ **CHAQUE ÉCOUTE REPART DES ONDES D'UNE PARTIE QUI COMMENCE** : tout l'état de `Son.Ondes`
    (le tour de rôle, ce qui est passé, le repos des bulletins, la station comptée) est remis tel
    qu'il était au sortir de `Jeu.commencer`, ainsi que la manchette de la veille et la voix de
    mission. Sans ça, la deuxième écoute hériterait du tour de rôle de la première — l'animateur
    ne dirait plus sa première réplique — et `dites` porterait les voix de la précédente.
    ⚠️ `hier` passe en dernier : c'est la seule qui charge la voix du narrateur (`bulletin`)."""
    premiere = audio.ONDES["premiere_s"]
    return banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const O = L.Son.Ondes;
        const CLES = ['enCours', 'dites', 'tours', 'station', 'prochaineT', 'n', 'policeT', 'derniers', 'bulletins'];
        const copie = function (x) { return x === undefined ? undefined : JSON.parse(JSON.stringify(x)); };
        const zero = {};
        CLES.forEach(function (k) { zero[k] = copie(O[k]); });
        const veille = L.B.partie.derniereManchette;
        function ecoute(station, secondes, manchette, pendant) {
            CLES.forEach(function (k) { O[k] = copie(zero[k]); });
            L.Son.Voix.enCours = null;
            L.B.partie.derniereManchette = manchette;
            return ecouter(L, station, secondes, pendant);
        }
        const mission = { slug: 'essai' };
        return {
            tounes: ecoute('taxi_radio', 600, veille),
            choc: ecoute('le_choc', 400, veille),
            mission: ecoute('taxi_radio', %d, veille, function (t) {
                L.Son.Voix.enCours = t < %d ? mission : null;
            }),
            lecon: ecoute('taxi_radio', 400, L.B.defs.journal_lecons[0]),
            sans: ecoute('la_brume', 400, null),
            hier: ecoute('taxi_radio', 400, L.B.defs.journal[0]),
        };
    }""" % (_ECOUTER, premiere + 30, (premiere + 10) * 60))


def test_la_radio_parle_entre_les_tounes(ecoutes):
    r = ecoutes["tounes"]
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


def test_le_choc_ne_parle_pas(ecoutes):
    r = ecoutes["choc"]
    assert r["dites"] == [], "quelqu'un parle au micro du Choc"


def test_la_radio_attend_la_fin_d_une_replique_de_mission(ecoutes):
    """⚠️ La mission passe devant tout le monde : tant qu'une réplique joue,
    l'animateur garde son clip pour après."""
    premiere = audio.ONDES["premiere_s"]
    r = ecoutes["mission"]
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
        // ⚠️ Le juge saute le temps a la main (`attendre`) : les renforts d'une etoile
        // neuve, eux, comptent leurs images (`renfort_s`, la tolerance du 22 sept. 2026),
        // et l'helico des cinq etoiles n'arriverait jamais a la seule image jouee.
        L.B.defs.recherche.police.renfort_s = 0;
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
        // ⚠️ Une réplique NEUTRE : celle d'un ciel n'est pas chargée au démarrage (`chargerMeteo`).
        const clip = L.Son.Voix.liste().find(function (v) { return v.genre === 'radio_taxi' && !v.meteo && v.fichier; });
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


def test_la_radio_lit_ce_que_tu_as_fait_hier(ecoutes):
    """⚠️ **LE SEUL MOMENT DE LA STATION QUI NE SOIT PAS LE MÊME POUR TOUT LE MONDE.**
    L'animateur et les pubs sont écrits d'avance ; le bulletin, lui, rejoue la
    manchette que le Clairon a lue au lever — donc ce que TU as fait hier, dans un
    char que tu viens de voler.

    ⚠️ Et il la prend dans la banque du **narrateur** (`histoire-`), pas dans celle
    des ondes : c'est ce qui fait qu'il n'a coûté aucun crédit."""
    r = ecoutes["hier"]
    assert r["des"] == 0, "les ondes tirent des dés : tout le hasard du jeu se décale"
    nouvelles = [d for d in r["dites"] if d["banque"] == "histoire"]
    assert nouvelles, f"la radio ne lit jamais les nouvelles : {r['dites']}"
    manchette = journal.REGLES[0]["slug"]
    assert nouvelles[0]["slug"] == f"narrateur-journal-{manchette}", nouvelles
    assert nouvelles[0]["bande"] == "radio", "le bulletin sort du scanner de police"
    # ⚠️ Il passe DANS le tour de rôle, pas à la place de l'animateur : une station
    # qui ne dirait que les nouvelles n'aurait plus d'animateur.
    genres = {v["slug"]: v["genre"] for v in audio.VOIX}
    assert [genres.get(d["slug"], "bulletin") for d in r["dites"][:3]] \
        == ["radio_taxi", "pub", "bulletin"], r["dites"]


def test_la_radio_ne_lit_pas_une_lecon_aux_nouvelles(ecoutes):
    """⚠️ « Le saviez-vous? Un coup de klaxon dans un taxi vous trouve un client » :
    au Clairon c'est une leçon, à la radio ce serait un mode d'emploi. La station
    joue sa musique à la place.

    ⚠️ Et **elle ne se tait pas pour autant** : le tour de rôle prend le premier
    genre qui a quelque chose à dire. Sans ça, un matin sans nouvelle rendrait la
    station muette deux minutes — on entendrait le trou, pas la règle."""
    r = ecoutes["lecon"]
    assert [d for d in r["dites"] if d["banque"] == "histoire"] == [], \
        f"la radio lit une leçon aux nouvelles : {r['dites']}"
    genres = {v["slug"]: v["genre"] for v in audio.VOIX}
    assert [genres.get(d["slug"], "bulletin") for d in r["dites"][:4]] \
        == ["radio_taxi", "pub", "radio_taxi", "pub"], \
        f"la station se tait au lieu de passer au suivant : {r['dites']}"


def test_la_meme_nouvelle_ne_repasse_pas_a_chaque_paire_de_tounes(banc):
    """⚠️ La manchette ne change qu'au **lever du jour** : sans repos, la station la
    redirait toutes les quatre minutes, et une nouvelle qu'on entend dix fois n'est
    plus une nouvelle — c'est une alarme, la faute déjà faite au scanner de police.

    ⚠️ Le repos est par manchette : un jour neuf passe tout de suite."""
    repos = audio.ONDES["bulletin_repos_s"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const O = L.Son.Ondes, dit = [];
        L.B.partie.derniereManchette = L.B.defs.journal[0];
        dit.push(O.bulletin());
        L.B.t += 60 * 60;     dit.push(O.bulletin());       // une minute plus tard
        L.B.t += %d * 60;     dit.push(O.bulletin());       // apres le repos
        L.B.partie.derniereManchette = L.B.defs.journal[1];
        dit.push(O.bulletin());                             // une autre nouvelle
        return dit.map(function (v) { return v && v.slug; });
    }""" % repos)
    premiere = f"narrateur-journal-{journal.REGLES[0]['slug']}"
    assert r[0] == premiere
    assert r[1] is None, "la radio redit la nouvelle une minute plus tard"
    assert r[2] == premiere, "elle ne la redit plus jamais : les nouvelles de midi n'existent pas"
    assert r[3] == f"narrateur-journal-{journal.REGLES[1]['slug']}", \
        "un jour neuf attend le repos de la veille"


def test_sans_manchette_la_radio_parle_quand_meme(ecoutes):
    """Le premier matin, rien n'a encore été lu : le bulletin n'a rien à dire, et la
    station ne doit pas s'en apercevoir."""
    r = ecoutes["sans"]
    assert [d for d in r["dites"] if d["banque"] == "histoire"] == []
    assert len(r["dites"]) >= 4, f"la station se tait faute de nouvelles : {r['dites']}"


def test_le_bulletin_s_entend_vraiment(banc):
    """Avec du son : le bulletin prend le clip du **narrateur** (`histoire-`) et
    atteint la sortie.

    ⚠️ C'est la panne du 16 sept. 2026 prise par l'autre bout : là, douze clips
    existaient et rien ne les jouait ; ici, il serait facile qu'il « passe » —
    `dites` le note, la musique baisse, le juge est vert — sans qu'on entende un
    mot, parce qu'il serait allé chercher son clip dans la mauvaise banque."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        L.B.partie.derniereManchette = L.B.defs.journal[0];
        L.Son.Voix.chargerHistoire('journal');
        for (let i = 0; i < 8; i++) await o.attendre();
        const v = L.Son.Ondes.bulletin();
        const passe = v && L.Son.Ondes.dire(v, 'radio');
        return { slug: v && v.slug, banque: v && v.banque,
                 sortie: !!passe && L.Son.contexte.atteintLaSortie(passe.source) };
    }""")
    assert r["slug"] == f"narrateur-journal-{journal.REGLES[0]['slug']}", r
    assert r["banque"] == "histoire", "le bulletin cherche son clip chez les ondes : %s" % r
    assert r["sortie"] is True, "le bulletin « passe » et on n'entend rien : %s" % r


def test_la_radio_dit_le_temps_qu_il_fait(banc):
    """⚠️ **CE QUE L'ANIMATEUR DIT DU TEMPS, LE CIEL LE CONFIRME** (Martin, 30 sept. 2026).
    Les deux stations tournent vingt minutes sous chacun des cinq ciels, trouvés dans les
    fonctions pures du jour et de l'heure : rien de ce qui passe ne contredit le ciel, et
    la réplique de ce ciel-là passe au moins une fois — la radio le dit, elle ne fait pas
    que se taire. Sans un dé : le tour de rôle reste un tour de rôle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const O = L.Son.Ondes, B = L.B;
        const CLES = ['enCours', 'dites', 'tours', 'station', 'prochaineT', 'n', 'policeT', 'derniers', 'bulletins'];
        const copie = function (x) { return x === undefined ? undefined : JSON.parse(JSON.stringify(x)); };
        const zero = {};
        CLES.forEach(function (k) { zero[k] = copie(O[k]); });
        const P = L.Pluie, N = L.Neige, Br = L.Brouillard, V = L.Verglas;
        const force = {
            pluie: function (j, h) { return P.intensiteA(j, h); }, neige: function (j, h) { return N.intensiteA(j, h); },
            brouillard: function (j, h) { return Br.intensiteA(j, h); }, verglas: function (j, h) { return V.intensiteA(j, h); },
        };
        // Un moment ou ce ciel-la est plein et les autres absents (« beau » : aucun).
        function trouver(ciel) {
            for (let j = 1; j < 800; j++) for (let q = 0; q < 48; q++) {
                const h = q / 48;
                const ok = Object.keys(force).every(function (k) {
                    return k === ciel ? force[k](j, h) > 0.9 : force[k](j, h) === 0;
                });
                if (ok) return { jour: j, heure: h };
            }
            return null;
        }
        const res = {};
        ['beau', 'pluie', 'neige', 'brouillard', 'verglas'].forEach(function (ciel) {
            const m = trouver(ciel);
            if (!m) { res[ciel] = null; return; }
            B.options.brouillard = ciel === 'brouillard';
            B.options.verglas = ciel === 'verglas';
            B.partie.jour = m.jour; B.partie.heure = m.heure;
            res[ciel] = { moment: m, lu: O.ciel(), stations: {} };
            ['la_brume', 'taxi_radio'].forEach(function (station) {
                CLES.forEach(function (k) { O[k] = copie(zero[k]); });
                L.Son.Voix.enCours = null;
                B.partie.derniereManchette = null;
                // Qui demande quel ciel, et quand : avant la premiere voix, pas apres.
                const demandes = [], vraie = L.Son.Voix.chargerMeteo;
                L.Son.Voix.chargerMeteo = function (x) { demandes.push({ meteo: x, n: O.dites.length, avance: O.prochaineT - B.t }); };
                res[ciel].stations[station] = ecouter(L, station, 1200);
                L.Son.Voix.chargerMeteo = vraie;
                res[ciel].stations[station].demandes = demandes;
            });
        });
        return res;
    }""" % _ECOUTER)
    meteo = {v["slug"]: v.get("meteo") for v in audio.VOIX}
    for ciel in audio.METEOS:
        assert r[ciel], f"aucun moment de « {ciel} » en 800 jours"
        lu = r[ciel]["lu"]
        assert [k for k in audio.METEOS if lu[k]] == [ciel], f"{ciel} : les ondes lisent {lu} ({r[ciel]['moment']})"
        for station, ecoute in r[ciel]["stations"].items():
            assert ecoute["des"] == 0, "les ondes tirent des dés : tout le hasard du jeu se décale"
            dites = [d["slug"] for d in ecoute["dites"]]
            menteuses = [s for s in dites if meteo.get(s) not in (None, ciel)]
            assert not menteuses, f"{station} sous « {ciel} » dit {menteuses}"
            a_dire = {v["slug"] for v in audio.VOIX if v.get("meteo") == ciel
                      and v["genre"] in audio.ONDES["stations"][station]}
            if a_dire:
                assert a_dire & set(dites), f"{station} sous « {ciel} » ne le dit jamais : {dites}"
            # ⚠️ Les répliques d'un ciel ne partent pas au démarrage : la station les
            # demande AVANT la première voix, sinon la première passerait muette.
            avant = [d for d in ecoute["demandes"] if d["n"] == 0]
            assert {d["meteo"] for d in avant} == {ciel}, f"{station} sous « {ciel} » demande {avant[:3]}"
            assert max(d["avance"] for d in avant) >= 5 * 60, \
                f"{station} sous « {ciel} » demande son ciel au moment de parler : trop tard pour l'entendre"
