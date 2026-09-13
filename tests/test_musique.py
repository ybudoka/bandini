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
    assert octets < 16000, f"{octets} octets : le catalogue enfle"
