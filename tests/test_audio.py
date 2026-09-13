"""Le catalogue des sons — et le fait que le jeu sonne meme sans les fichiers."""

import re

import pytest

from app import audio

RACINE_JS = audio.RACINE_STATIQUE / "js"


@pytest.mark.parametrize("echantillon", audio.CATALOGUE, ids=lambda e: e["slug"])
def test_un_echantillon_est_generable(echantillon):
    """Les bornes sont celles d'ElevenLabs : hors d'elles, l'appel serait refuse."""
    assert echantillon["slug"] and re.fullmatch(r"[a-z_]+", echantillon["slug"])
    assert echantillon["nom"]
    assert echantillon["categorie"] in audio.CATEGORIES
    assert 0.5 <= echantillon["duree_s"] <= 30.0
    assert 0 < echantillon["volume"] <= 1.0
    assert 1 <= echantillon["variantes"] <= 4
    assert len(echantillon["prompt"]) >= 20, "une recette trop courte donne n'importe quoi"
    assert "no music" in echantillon["prompt"] or echantillon["categorie"] != "sfx", \
        "un bruitage avec de la musique dessous est inutilisable"


def test_les_slugs_sont_uniques():
    assert len(audio.SLUGS) == len(set(audio.SLUGS))


def test_le_catalogue_ne_declare_que_des_fichiers_presents():
    for echantillon in audio.exporter()["echantillons"]:
        for nom in echantillon["fichiers"]:
            chemin = audio.RACINE_STATIQUE / audio.DOSSIER / nom
            assert chemin.is_file(), nom
            assert chemin.stat().st_size > 500, f"{nom} est vide ou tronque"


def test_aucun_fichier_orphelin():
    assert audio.orphelins() == [], "des .mp3 que le catalogue ne reclame plus"


def test_le_poids_audio_reste_raisonnable():
    """Un telephone en 3G telecharge les BRUITAGES au demarrage : on se tient
    loin du megaoctet. Les radios, elles, n'arrivent qu'au tour de cle."""
    dossier = audio.RACINE_STATIQUE / audio.DOSSIER
    fichiers = list(dossier.glob("*.mp3")) if dossier.is_dir() else []
    bruitages = [f for f in fichiers if not f.name.startswith(("radio-", "histoire-"))]
    radios = [f for f in fichiers if f.name.startswith("radio-")]
    histoire = [f for f in fichiers if f.name.startswith("histoire-")]
    assert sum(f.stat().st_size for f in bruitages) < 600_000
    for fichier in bruitages:
        assert fichier.stat().st_size < 80_000, fichier.name
    for fichier in radios:
        assert 100_000 < fichier.stat().st_size < 700_000, fichier.name
    assert sum(f.stat().st_size for f in radios) < 2_000_000
    # Les voix de l'histoire se chargent par mission : une replique reste legere.
    for fichier in histoire:
        assert fichier.stat().st_size < 150_000, fichier.name
    assert sum(f.stat().st_size for f in histoire) < 3_000_000


@pytest.mark.parametrize("radio", audio.RADIOS, ids=lambda r: r["slug"])
def test_une_station_est_generable(radio):
    assert radio["nom"] and radio["style"]
    assert "instrumental" in radio["prompt"] or "no vocals" in radio["prompt"], \
        "une voix chantee sous une sirene, c'est illisible"
    assert 20 <= radio["duree_s"] <= 90
    assert 0 < radio["volume"] <= 1


def test_chaque_char_de_phase_1_a_une_station_qui_existe():
    from app import vehicules

    for vehicule in vehicules.de_phase(1):
        if vehicule["radio"]:
            assert audio.radio_par_slug(vehicule["radio"]), vehicule["slug"]
    assert any(v["radio"] for v in vehicules.de_phase(1)), "aucun char n'a de radio"


def test_les_radios_ne_sont_pas_chargees_au_demarrage(paquet):
    """Les radios sont dans `radios`, jamais dans `echantillons` : sinon
    `chargerEchantillons()` telechargerait un mega de jazz avant la premiere
    image."""
    slugs = {e["slug"] for e in paquet["audio"]["echantillons"]}
    for radio in paquet["audio"]["radios"]:
        assert radio["slug"] not in slugs
        assert "fichier" in radio


def test_le_navigateur_ne_reclame_que_des_slugs_du_catalogue():
    """`Son.joue('x')` dans le JS doit correspondre a un son declare en Python."""
    source = (RACINE_JS / "son.js").read_text(encoding="utf-8")
    demandes = set(re.findall(r"joue\('([a-z_]+)'\)", source))
    assert demandes, "plus personne ne joue d'echantillon ?"
    assert demandes <= set(audio.SLUGS), demandes - set(audio.SLUGS)


def test_chaque_effet_garde_son_repli_synthetise():
    """⚠️ Le filet : un `joue(...)` sans `else` synthetise laisse un silence."""
    source = (RACINE_JS / "son.js").read_text(encoding="utf-8")
    bloc = source[source.index("const SFX = {"):source.index("// --- La musique")]
    for ligne in bloc.splitlines():
        if "joue(" not in ligne:
            continue
        assert re.search(r"if \(!joue\('[a-z_]+'\)\)\s*\S", ligne), ligne.strip()


def test_les_fichiers_sont_servis(client, paquet):
    audios = paquet["audio"]
    assert audios["echantillons"], "le paquet ne dit rien de l'audio"
    servis = 0
    for echantillon in audios["echantillons"]:
        for nom in echantillon["fichiers"]:
            reponse = client.get(f"/static/{audios['dossier']}/{nom}")
            assert reponse.status_code == 200, nom
            servis += 1
    assert servis >= len(audio.CATALOGUE), "des sons du catalogue ne sont pas servis"


def test_l_ambiance_et_les_voix_sont_declarees_a_part(paquet):
    """L'ambiance n'est pas une radio (elle joue a pied) et les voix ne sont
    pas des bruitages (elles ont un texte et une voix nommee)."""
    audios = paquet["audio"]
    assert len(audios["ambiances"]) >= 1
    for ambiance in audios["ambiances"]:
        assert ambiance["slug"] not in {r["slug"] for r in audios["radios"]}
        assert 0 < ambiance["volume"] <= 0.5, "la musique de fond doit rester sous la rumeur"
    assert len(audios["voix"]) >= 6
    genres = {v["genre"] for v in audios["voix"]}
    assert genres == {"homme", "femme"}, "il faut des hommes ET des femmes qui parlent"
    for voix in audio.VOIX:
        assert 2 <= len(voix["texte"]) <= 40, "une replique de passant tient en quelques mots"
        assert voix["voix"] and not voix["voix"].startswith("__"), \
            f"{voix['slug']} : la voix ElevenLabs n'est pas nommee"


def test_le_choc_est_du_techno_maintenant():
    """Martin trouvait le punk trop hardcore pour la moto."""
    choc = audio.radio_par_slug("le_choc")
    assert choc["style"] == "techno" and "techno" in choc["prompt"]
    assert "punk" not in choc["prompt"]


def test_la_rumeur_et_les_passages_existent():
    for slug in ("foule", "passage_auto", "passage_moto", "sonnette"):
        assert audio.par_slug(slug), slug
    assert audio.par_slug("foule")["boucle"] is True, "la rumeur doit boucler"
    assert audio.par_slug("passage_auto")["variantes"] >= 2


def test_les_voix_de_l_histoire_sont_declarees_par_mission(paquet):
    """Chaque replique de l'histoire est servie avec son personnage et sa
    mission, pour que le navigateur ne charge que celles de la mission en
    cours — jamais au demarrage."""
    histoire = paquet["audio"]["histoire"]
    assert len(histoire) >= 30
    assert {v["mission"] for v in histoire} == {"m1", "m2", "m3", "m4", "m5", "journal"}, \
        "les cinq missions, et le journal lu par le narrateur"
    assert all(v["qui"] and v["partie"] for v in histoire)
    assert any(v["telephone"] for v in histoire), "les appels sont marques : la voix vient du combine"
    assert all(v["fichier"] is None or v["fichier"].startswith("histoire-") for v in histoire)
    slugs = {v["slug"] for v in histoire} | {v["slug"] for v in paquet["audio"]["voix"]}
    assert len(slugs) == len(histoire) + len(paquet["audio"]["voix"]), "un slug de voix par replique"
