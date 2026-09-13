"""Le theme du menu : ce qu'on ne peut pas entendre, on le juge.

⚠️ On ne peut pas ecouter une musique dans un test. Ce qui se juge, c'est ce
qui la rendrait fausse ou inecoutable sans qu'on s'en apercoive : une note hors
du clavier, une voix qui deborde de sa boucle, deux notes au meme instant dans
la meme voix (elles s'annulent), une boucle trop courte (on entend la couture),
un volume cumule qui sature. Le reste — est-ce que c'est beau — c'est l'oreille
de Martin, et aucun test ne la remplace.
"""

import pytest

from app import audio, musique

#: Le clavier d'un piano : 21 (la0) a 108 (do8). Une note hors de la est une
#: faute de frappe, jamais un choix.
MIDI_MIN, MIDI_MAX = 21, 108


@pytest.fixture(scope="module")
def theme():
    return musique.par_slug("titre")


def test_le_menu_a_un_theme(theme):
    assert theme is not None, "le menu d'accueil doit avoir une musique"
    assert theme["nom"]
    assert theme["voix"], "un theme sans voix ne joue rien"


def test_le_paquet_porte_la_musique():
    paquet = audio.exporter()
    assert "musiques" in paquet, "le navigateur ne recevrait aucune musique"
    slugs = [m["slug"] for m in paquet["musiques"]]
    assert "titre" in slugs
    assert len(slugs) == len(set(slugs)), f"deux morceaux du meme nom : {slugs}"


def test_toutes_les_notes_sont_sur_le_clavier(theme):
    for voix in theme["voix"]:
        if voix["forme"] == "bruit":
            continue
        for pas, hauteur, *reste in voix["notes"]:
            assert MIDI_MIN <= hauteur <= MIDI_MAX, f"{voix['role']} pas {pas} : {hauteur}"


def test_le_bruit_filtre_dans_l_audible(theme):
    for voix in theme["voix"]:
        if voix["forme"] != "bruit":
            continue
        for pas, coupure, *reste in voix["notes"]:
            assert 200 <= coupure <= 16000, f"{voix['role']} pas {pas} : {coupure} Hz"


def test_aucune_voix_ne_deborde_de_sa_boucle(theme):
    """⚠️ Une note posee au-dela du motif ne joue JAMAIS : le sequenceur prend
    le pas modulo le motif, et elle disparaît sans bruit."""
    for voix in theme["voix"]:
        motif = voix.get("motif", theme["pas"])
        for pas, hauteur, *reste in voix["notes"]:
            assert 0 <= pas < motif, f"{voix['role']} : pas {pas} hors du motif {motif}"


def test_chaque_motif_se_repete_un_nombre_entier_de_fois(theme):
    """Sinon la derniere repetition est coupee en plein milieu, et la boucle
    revient sur une mesure tronquee — ca s'entend tout de suite."""
    for voix in theme["voix"]:
        motif = voix.get("motif", theme["pas"])
        assert theme["pas"] % motif == 0, f"{voix['role']} : {theme['pas']} n'est pas un multiple de {motif}"


def test_une_voix_ne_joue_jamais_deux_notes_au_meme_instant(theme):
    """⚠️ Sauf la nappe, qui plaque des accords : c'est justement son role."""
    for voix in theme["voix"]:
        if voix["role"] == "nappe":
            continue
        departs = [n[0] for n in voix["notes"]]
        doubles = {p for p in departs if departs.count(p) > 1}
        assert not doubles, f"{voix['role']} : deux notes au pas {sorted(doubles)}"


def test_les_notes_d_une_voix_ne_se_chevauchent_pas(theme):
    """Un oscillateur par note : deux notes qui se recouvrent dans la meme voix
    sonnent comme un accord qu'on n'a pas ecrit."""
    for voix in theme["voix"]:
        if voix["role"] == "nappe":
            continue
        notes = sorted(voix["notes"], key=lambda n: n[0])
        for avant, apres in zip(notes, notes[1:]):
            fin = avant[0] + avant[2]
            assert fin <= apres[0], f"{voix['role']} : la note du pas {avant[0]} mord sur {apres[0]}"


def test_la_boucle_dure_assez_pour_ne_pas_tourner_en_rond(theme):
    """Sous un menu ou l'on reste parfois une minute, une boucle de dix secondes
    devient une sonnerie d'ascenseur."""
    duree = musique.duree_s(theme)
    assert 25 <= duree <= 120, f"{duree:.1f} s"


def test_le_volume_cumule_ne_sature_pas(theme):
    """⚠️ Toutes les voix passent dans le meme gain : si leurs volumes cumules
    depassent 1, les notes fortes ecretent et la musique grince."""
    pire = 0.0
    for pas in range(theme["pas"]):
        total = 0.0
        for voix in theme["voix"]:
            motif = voix.get("motif", theme["pas"])
            dans = pas % motif
            for note in voix["notes"]:
                if note[0] != dans:
                    continue
                relatif = note[3] if len(note) > 3 else 1
                total += voix["volume"] * relatif * theme["volume"]
        pire = max(pire, total)
    assert pire <= 1.0, f"pas le plus charge : {pire:.2f}"


def test_la_melodie_commence_et_finit_dans_le_ton(theme):
    """En la mineur : la boucle doit boucler sur un la, sinon la reprise
    sonne comme une question sans reponse."""
    chant = next(v for v in theme["voix"] if v["role"] == "chant")
    derniere = max(chant["notes"], key=lambda n: n[0])
    assert derniere[1] % 12 == 9, f"la derniere note du chant n'est pas un la : {derniere}"


def test_la_musique_ne_reclame_aucun_fichier(theme):
    """Tout l'interet : le theme ne coute ni octet a telecharger, ni credit a
    generer. Le jour ou l'on pose un vrai enregistrement, ce sera un ajout
    explicite — pas un fichier qui se serait glisse la."""
    assert "fichier" not in theme
    for voix in theme["voix"]:
        assert voix["forme"] in ("sine", "square", "triangle", "sawtooth", "bruit"), voix["forme"]


def test_le_theme_pese_moins_qu_une_seconde_de_mp3():
    import json
    octets = len(json.dumps(audio.exporter()["musiques"]))
    assert octets < 48000, f"{octets} octets : le catalogue enfle"


# --- M9 : les stations procedurales -----------------------------------------


@pytest.fixture(scope="module")
def stations():
    return musique.stations()


def test_une_station_par_char_qui_en_demande_une(stations):
    from app import vehicules

    slugs = {s["slug"] for s in stations}
    assert slugs == {s["slug"] for s in musique.STATIONS}
    demandees = {v["radio"] for v in vehicules.de_phase(1) if v["radio"]}
    assert slugs <= demandees, f"station generee que personne n'ecoute : {slugs - demandees}"


def test_la_meme_graine_donne_la_meme_toune():
    """⚠️ Tout tient a ca. Une station qui change a chaque demarrage du
    serveur, c'est un ETag qui bouge sans raison, un paquet qui ne se met
    jamais en cache, et une toune qu'on ne peut plus corriger — on ne
    retrouverait pas celle qu'on veut changer."""
    for style in musique.STATIONS:
        a = musique.generer_station(style)
        b = musique.generer_station(style)
        assert a == b, style["slug"]


def test_toutes_les_notes_d_une_station_sont_dans_sa_gamme(stations):
    """⚠️ Le juge qui remplace l'oreille. Une seule note hors de la gamme
    s'entend tout de suite, et personne ne debogue une fausse note en
    conduisant un camion. Par construction, chaque hauteur se batit sur un
    degre — ce test verifie que la construction tient."""
    for station, style in zip(stations, musique.STATIONS, strict=True):
        for voix in station["voix"]:
            if voix["forme"] == "bruit":
                continue          # une percussion n'a pas de hauteur
            for note in voix["notes"]:
                demi = (int(note[1]) - style["tonique"]) % 12
                assert demi in style["gamme"], \
                    f"{station['slug']} / {voix['role']} : {note} hors de la gamme"
                assert MIDI_MIN <= note[1] <= MIDI_MAX, note


def test_une_station_tourne_assez_longtemps_sans_se_mordre_la_queue(stations):
    for station in stations:
        assert musique.duree_s(station) >= 30, f"{station['slug']} : la boucle s'entend"
        for voix in station["voix"]:
            motif = voix.get("motif", station["pas"])
            assert motif <= station["pas"]
            for note in voix["notes"]:
                assert note[0] < motif, f"{station['slug']} : une note hors de son motif"
        # Les trois voix jouees plus la batterie : le sequenceur en tient trois
        # a la fois sans forcer, et la batterie ne compte pas comme une voix.
        assert len(station["voix"]) == 4


def test_deux_stations_ne_sonnent_pas_pareil(stations):
    """Deux graines, deux tonalites, deux tempos : sinon le camion et la
    remorqueuse ont la meme radio et la station procedurale ne sert a rien."""
    assert len({s["bpm"] for s in stations}) == len(stations)
    chants = [tuple(n[1] for n in next(v for v in s["voix"] if v["role"] == "chant")["notes"])
              for s in stations]
    assert len(set(chants)) == len(chants)
