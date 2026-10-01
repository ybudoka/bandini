def test_accueil(client):
    reponse = client.get("/")
    assert reponse.status_code == 200
    html = reponse.get_data(as_text=True)
    assert 'id="toile"' in html
    assert "/api/definitions" in html
    assert "/api/carte" in html
    assert 'id="tactile"' in html
    assert 'data-etat="chargement"' in html


def test_la_page_dit_combien_de_scripts_elle_charge(client):
    """La barre du lancement compte les scripts a mesure qu'ils arrivent
    (`chargement.js`) : le total vient de la page, et il doit etre le vrai."""
    import re

    html = client.get("/").get_data(as_text=True)
    annonces = int(re.search(r'data-scripts="(\d+)"', html).group(1))
    charges = re.findall(r'<script src="[^"]*/static/js/[^"]+\.js', html)
    assert annonces == len(charges) > 10, (annonces, len(charges))
    assert charges[0].endswith("/chargement.js"), "le compteur doit arriver AVANT les scripts qu'il compte"


def test_la_taille_decompressee_voyage_avec_les_paquets(client):
    """⚠️ Derriere nginx, la longueur de la reponse est celle du gzip ; le
    navigateur lit, lui, des octets decompresses. `X-Octets` est ce que la barre
    de chargement compte — il doit valoir le corps, a l'octet pres."""
    for url in ("/api/definitions", "/api/carte"):
        reponse = client.get(url)
        assert int(reponse.headers["X-Octets"]) == len(reponse.get_data()), url


#: Toutes les routes qui passent par `routes._revalide` (un paquet signé et son ETag).
ROUTES_DES_PAQUETS = ("/api/definitions", "/api/carte", "/api/musiques", "/api/suite", "/api/collections",
                      "/api/mission/m1", "/api/carte/bloc/rang")


def test_les_paquets_partent_compresses_au_plus_fort(client, paquets):
    """⚠️ La vague 2 des districts (docs/jalons/charger-les-districts-autour-du-joueur.md) : nginx compresse au
    niveau 1 (98 Ko de carte sur le fil quand les juges en comptaient 70). Le serveur envoie donc lui-même le
    corps compressé UNE fois au niveau 9 (`Paquet.fil`) à tout navigateur qui accepte gzip : le même JSON, à
    l'octet près, la même empreinte, la taille décompressée pour la barre, et `Vary` pour les caches."""
    import gzip

    for url in ROUTES_DES_PAQUETS:
        r = client.get(url, headers={"Accept-Encoding": "gzip, deflate, br"})
        assert r.status_code == 200, url
        assert r.headers.get("Content-Encoding") == "gzip", f"{url} part sans être compressé"
        assert "Accept-Encoding" in r.headers.get("Vary", ""), url
        corps = gzip.decompress(r.get_data())
        assert corps == client.get(url).get_data(), url
        assert int(r.headers["X-Octets"]) == len(corps), url
        assert client.get(url, headers={"Accept-Encoding": "gzip", "If-None-Match": r.headers["ETag"]}).status_code == 304
    carte = paquets.carte
    assert gzip.decompress(carte.fil) == carte.corps
    assert len(carte.fil) <= len(gzip.compress(carte.corps, 6)), "le fil doit être au plus fort"
    assert carte.fil == gzip.compress(carte.corps, 9, mtime=0), "les mêmes octets à chaque construction (mtime=0)"


def test_un_client_qui_ne_decompresse_pas_recoit_le_json(client):
    """Sans `Accept-Encoding` (ou `gzip;q=0`), le corps part tel quel : jamais d'octets qu'il ne saurait lire."""
    for entetes in ({}, {"Accept-Encoding": "identity"}, {"Accept-Encoding": "gzip;q=0, br"}):
        r = client.get("/api/carte", headers=entetes)
        assert "Content-Encoding" not in r.headers, entetes
        assert r.get_json()["largeur"] > 0, entetes


def test_sante(client):
    donnees = client.get("/sante").get_json()
    assert donnees["ok"] is True
    assert donnees["version"].count(".") == 2


def test_definitions_avec_etag(client):
    reponse = client.get("/api/definitions")
    assert reponse.status_code == 200
    assert reponse.mimetype == "application/json"
    etag = reponse.headers["ETag"]
    assert etag.startswith('"') and len(etag) == 18
    paquet = reponse.get_json()
    assert paquet["empreinte"] == etag.strip('"')
    assert len(paquet["vehicules"]) >= 4
    assert "carte" not in paquet, "la carte voyage a part (/api/carte)"

    revalide = client.get("/api/definitions", headers={"If-None-Match": etag})
    assert revalide.status_code == 304
    assert revalide.headers["ETag"] == etag
    # nginx renvoie un ETag FAIBLE quand il compresse : il doit revalider aussi.
    faible = client.get("/api/definitions", headers={"If-None-Match": "W/" + etag})
    assert faible.status_code == 304
    autre = client.get("/api/definitions", headers={"If-None-Match": '"autre"'})
    assert autre.status_code == 200


def test_carte_avec_etag(client):
    """La ville, a part : la meme revalidation que les definitions, ETag faible
    compris, et l'empreinte que les definitions annoncent."""
    reponse = client.get("/api/carte")
    assert reponse.status_code == 200
    assert reponse.mimetype == "application/json"
    etag = reponse.headers["ETag"]
    carte = reponse.get_json()
    assert carte["empreinte"] == etag.strip('"')
    assert carte["largeur"] > 0
    assert client.get("/api/definitions").get_json()["carte_empreinte"] == carte["empreinte"]
    assert client.get("/api/carte", headers={"If-None-Match": etag}).status_code == 304
    assert client.get("/api/carte", headers={"If-None-Match": "W/" + etag}).status_code == 304
    assert client.get("/api/carte", headers={"If-None-Match": '"autre"'}).status_code == 200


def test_une_mission_a_jouer_avec_etag(client):
    """Tout ce qu'une mission demande pour se JOUER : hors du paquet depuis le
    24 sept. 2026, une reponse par mission, la meme revalidation que les deux autres.

    ⚠️ **404 pour un slug inconnu**, et pas un objet vide : le navigateur ne demande que
    ce qu'il a lu dans le catalogue, alors un slug inconnu est un defaut de notre cote —
    un 200 vide le cacherait, et la mission s'ouvrirait sur une boite muette."""
    from app import missions
    reponse = client.get("/api/mission/m2")
    assert reponse.status_code == 200
    assert reponse.mimetype == "application/json"
    etag = reponse.headers["ETag"]
    corps = reponse.get_json()
    assert corps["empreinte"] == etag.strip('"')
    assert corps["slug"] == "m2"
    # Les quatre temps du dialogue, ses deux scenes, et les voix qui les disent.
    for partie in ("appel", "intro", "fin", "echec"):
        assert corps["dialogue"][partie], partie
    assert corps["scenes"]["intro"] and corps["scenes"]["fin"]
    # Et ce qu'elle demande de FAIRE : les objectifs pesaient les deux tiers du catalogue.
    assert corps["objectifs"] and all(o["type"] for o in corps["objectifs"])
    assert corps["voix"] and all(v["mission"] == "m2" for v in corps["voix"])
    # ⚠️ Le JEU des repliques ne voyage pas : il sert a generer les voix, jamais a jouer.
    assert all("jeu" not in ligne for lignes in corps["dialogue"].values() for ligne in lignes)

    assert client.get("/api/mission/m2", headers={"If-None-Match": etag}).status_code == 304
    # nginx renvoie un ETag FAIBLE quand il compresse : il doit revalider aussi.
    assert client.get("/api/mission/m2", headers={"If-None-Match": "W/" + etag}).status_code == 304
    assert client.get("/api/mission/m2", headers={"If-None-Match": '"autre"'}).status_code == 200
    assert client.get("/api/mission/pas-une-mission").status_code == 404

    # Chaque mission du catalogue a la sienne, et une seule empreinte les nomme toutes.
    paquet = client.get("/api/definitions").get_json()
    assert len(paquet["missions_empreinte"]) == 16
    for mission in missions.CATALOGUE:
        assert client.get(f"/api/mission/{mission['slug']}").status_code == 200, mission["slug"]


def test_le_paquet_ne_porte_plus_ce_qui_sert_a_jouer(client):
    """⚠️ Le CATALOGUE reste — titre, donneur, prerequis, recompense : ce que le carnet, le
    GPS et le telephone lisent, et il faut l'avoir en entier. Ce qui sert a la JOUER n'y
    est plus. Une mission qui ramenerait son dialogue ou ses objectifs dans le paquet le
    remettrait au-dessus de son plafond sans que rien d'autre ne rougisse."""
    from app import missions
    paquet = client.get("/api/definitions").get_json()
    # ⚠️ Les PETITES JOBS (`passant`, 1er oct. 2026) voyagent PLIÉES à part (`jobs`, `Jobs.deplier`) : le catalogue
    # entier, c'est les missions plus les jobs, chacune une seule fois.
    jobs = [j[0] for j in paquet["jobs"]]
    assert sorted([m["slug"] for m in paquet["missions"]] + jobs) == sorted(m["slug"] for m in missions.CATALOGUE)
    assert set(jobs) == {m["slug"] for m in missions.CATALOGUE if m.get("passant")}
    for mission in paquet["missions"]:
        for cle in missions.HORS_DU_PAQUET:
            assert cle not in mission, f"{mission['slug']} porte encore « {cle} » dans le paquet"
        assert mission["titre"] and mission["donneur"], mission["slug"]
    # Les voix de l'histoire qui restent sont celles qui n'appartiennent a AUCUNE mission.
    # (Le journal et les repos, en séries depuis le 30 sept. 2026 : on les déplie comme `Son.Voix`.)
    from app import audio
    # (Et celles du Clairon dans la suite du paquet depuis le 30 sept. 2026 : `/api/suite`, `voix_de_la_suite`.)
    suite = client.get("/api/suite").get_json()["voix_de_la_suite"]
    restent = {v["mission"] for v in audio.deplier_les_series(paquet["audio"], suite)}
    assert {"journal", "ouverture", "repos"} <= restent
    assert not restent & {m["slug"] for m in missions.CATALOGUE}, "une voix de mission est revenue au paquet"


def test_le_tableau_des_scores_n_existe_plus(client):
    """Retire le 17 sept. 2026 (demande de Martin) : plus de route, et plus un mot
    dans la page — ni bouton, ni voile, ni adresse a appeler."""
    assert client.get("/api/scores").status_code == 404
    assert client.post("/api/scores", json={}).status_code == 404
    html = client.get("/").get_data(as_text=True)
    assert "score" not in html.lower()


def test_corps_trop_gros(client):
    """La borne du site (16 Ko), mesuree sur la seule route qui prend un corps."""
    gros = client.post("/api/compte/inscription", data="x" * 20_000,
                       content_type="application/json")
    assert gros.status_code == 413


def test_404(client):
    reponse = client.get("/nulle-part")
    assert reponse.status_code == 404
    assert "Cul-de-sac" in reponse.get_data(as_text=True)


def test_statiques(client, racine):
    html = client.get("/").get_data(as_text=True)
    import re

    scripts = re.findall(r"/static/js/([a-z_]+\.js)", html)
    assert len(scripts) >= 10
    for nom in scripts:
        assert client.get(f"/static/js/{nom}").status_code == 200, nom
        assert (racine / "static" / "js" / nom).exists()
    assert client.get("/static/css/styles.css").status_code == 200
    assert client.get("/static/img/favicon.svg").status_code == 200


def test_chaque_statique_porte_l_empreinte_de_son_contenu(client, racine):
    """⚠️ La vague 3 des districts (docs/jalons/charger-les-districts-autour-du-joueur.md) : les scripts font 93 %
    de ce qui voyage avant l'écran titre, et ils portaient tous `?v=<version>` — chaque mise en ligne les faisait
    TOUS repartir (1,56 Mo, dix secondes en « 3G rapide »). Chaque adresse porte maintenant l'empreinte de SON
    fichier, et la version n'y paraît plus."""
    import hashlib
    import re

    from app.version import VERSION

    html = client.get("/").get_data(as_text=True)
    adresses = re.findall(r'(?:src|href)="(/static/[^"?]+)\?v=([^"&]+)"', html)
    assert len([a for a in adresses if a[0].startswith("/static/js/")]) == int(re.search(r'data-scripts="(\d+)"', html).group(1))
    assert any(a[0].endswith("/styles.css") for a in adresses)
    for chemin, v in adresses:
        attendue = hashlib.sha256((racine / chemin.lstrip("/")).read_bytes()).hexdigest()[:12]
        assert v == attendue, chemin
    assert f"?v={VERSION}" not in html


def test_une_mise_en_ligne_ne_change_pas_l_adresse_d_un_script_qui_n_a_pas_change(client, monkeypatch):
    """Deux constructions de versions différentes, les mêmes fichiers : les mêmes adresses, à l'octet près — le
    cache du navigateur rend tout sans rien redemander."""
    import re

    import app as paquet_app

    def adresses():
        return re.findall(r'(?:src|href)="(/static/[^"]+)"', client.get("/").get_data(as_text=True))

    avant = adresses()
    monkeypatch.setattr(paquet_app, "VERSION", "999.0.0")
    apres = adresses()
    assert "999.0.0" in client.get("/").get_data(as_text=True), "la version du pied de page a bien changé"
    assert avant == apres and len(avant) > 80


def test_l_empreinte_d_un_fichier_suit_son_contenu_et_lui_seul(tmp_path):
    """Un fichier qui change sous le serveur (le serveur de dev ne redémarre pas pour un script) change SON
    empreinte, et pas celle des autres."""
    import os

    from app.statiques import Empreintes

    (tmp_path / "js").mkdir()
    a, b = tmp_path / "js" / "a.js", tmp_path / "js" / "b.js"
    a.write_text("const A = 1;\n")
    b.write_text("const B = 2;\n")
    empreintes = Empreintes(tmp_path)
    ea, eb = empreintes("js/a.js"), empreintes("js/b.js")
    assert ea != eb and len(ea) == 12
    a.write_text("const A = 3;\n")
    os.utime(a, ns=(a.stat().st_atime_ns, a.stat().st_mtime_ns + 1_000_000))
    assert empreintes("js/a.js") != ea
    assert empreintes("js/b.js") == eb
