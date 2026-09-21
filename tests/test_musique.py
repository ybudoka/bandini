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
    """⚠️ Ce juge dit encore exactement ce qu'il disait, et il compte PLUS
    depuis que toute la musique est generee par IA (14 sept. 2026) : `musique.py`
    reste le FILET, et un filet ne telecharge rien. Le mp3 se pose a cote, dans
    `audio.MUSIQUES`, et `audio.exporter()` les marie. Le jour ou ce juge
    tombe, c'est que le fichier s'est glisse dans les notes — et qu'un depot
    frais, une generation ratee ou un reseau coupe rendraient le jeu muet."""
    assert "fichier" not in theme
    for voix in theme["voix"]:
        assert voix["forme"] in ("sine", "square", "triangle", "sawtooth", "bruit"), voix["forme"]


def test_le_theme_pese_moins_qu_une_seconde_de_mp3():
    """⚠️ **Relevé de 48 à 52 Ko le 17 sept. 2026** — l'orgue de la foire, et
    rien d'autre. Mesuré avant de toucher au chiffre : la valse pèse **2 318
    octets** pour 28,8 s de notes, là où le mp3 qu'elle remplace en pèse 240 Ko.
    Le budget dit « le filet reste plus léger qu'une seconde de mp3 » ; un
    morceau de plus qui coûte deux Ko ne le dément pas. Ce qui le démentirait,
    c'est de le relever de deux Ko à chaque ajout — il monte donc d'un cran
    franc, une fois."""
    import json
    octets = len(json.dumps(audio.exporter()["musiques"]))
    assert octets < 52000, f"{octets} octets : le catalogue enfle"


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


# --- Les cinq pieces du musicien de rue -------------------------------------


@pytest.fixture(scope="module")
def rues():
    return musique.rues()


def test_le_musicien_a_cinq_pieces(rues):
    """⚠️ Demande de Martin : « je veux que le musicien fasse vraiment de la
    musique, 5 musiques differentes ».

    La fiche « des sortes de gens » le promettait deja — « il joue, et CA
    S'ENTEND » — et ce qui a ete livre est un corps avec une guitare dessinee
    dessus et ZERO note. Le jeu avait le sequenceur, dix morceaux et un chef
    d'orchestre ; l'homme a la guitare etait muet."""
    assert len(rues) == 5, "cinq, pas quatre et pas six"
    slugs = {m["slug"] for m in rues}
    assert slugs == {s["slug"] for s in musique.RUE}
    assert all(m["nom"] for m in rues), "une piece sans titre ne s'annonce pas"
    # ⚠️ Le bouton RADIO d'un char ne doit JAMAIS tomber sur le gars du
    # trottoir : c'est ce que dit `station`, et c'est Python qui le dit.
    assert all(m["station"] is False for m in rues)
    # Et le paquet les porte.
    portees = {m["slug"] for m in audio.exporter()["musiques"]}
    assert slugs <= portees, f"le navigateur ne les verrait pas : {slugs - portees}"


def test_la_meme_graine_donne_la_meme_piece():
    """⚠️ Meme raison que pour les stations : une toune qui change a chaque
    demarrage du serveur, c'est un ETag qui bouge sans raison, un paquet qui ne
    se met jamais en cache, et une piece qu'on ne peut plus corriger."""
    for style in musique.RUE:
        assert musique.generer_rue(style) == musique.generer_rue(style), style["slug"]


def test_toutes_les_notes_d_une_piece_de_rue_sont_dans_sa_gamme(rues):
    for piece, style in zip(rues, musique.RUE, strict=True):
        for voix in piece["voix"]:
            for note in voix["notes"]:
                demi = (int(note[1]) - style["tonique"]) % 12
                assert demi in style["gamme"], \
                    f"{piece['slug']} / {voix['role']} : {note} hors de la gamme"
                assert MIDI_MIN <= note[1] <= MIDI_MAX, note


def test_une_piece_de_rue_est_UN_GARS_AVEC_UNE_GUITARE(rues):
    """⚠️ DEUX VOIX, PAS QUATRE. Une station de radio a une basse, une nappe, un
    chant et une batterie — c'est un groupe dans un studio. Un gars tout seul
    sur un trottoir a six cordes : il gratte un accord de la main droite et
    chante la melodie par-dessus. Quatre voix sous un mime auraient sonne comme
    un haut-parleur, pas comme un musicien."""
    for piece in rues:
        roles = [v["role"] for v in piece["voix"]]
        assert roles == ["gratte", "chant"], f"{piece['slug']} : {roles}"
        assert all(v["forme"] != "bruit" for v in piece["voix"]), \
            f"{piece['slug']} : une batterie sur le trottoir"


def test_aucune_piece_de_rue_ne_deborde_de_sa_boucle(rues):
    for piece in rues:
        for voix in piece["voix"]:
            motif = voix.get("motif", piece["pas"])
            assert piece["pas"] % motif == 0, f"{piece['slug']} / {voix['role']}"
            for note in voix["notes"]:
                assert 0 <= note[0] < motif, \
                    f"{piece['slug']} / {voix['role']} : pas {note[0]} hors du motif {motif}"


def test_la_melodie_d_une_piece_de_rue_ne_se_mord_pas(rues):
    """Un oscillateur par note : deux notes du chant qui se recouvrent sonnent
    comme un accord qu'on n'a pas ecrit."""
    for piece in rues:
        chant = next(v for v in piece["voix"] if v["role"] == "chant")
        notes = sorted(chant["notes"], key=lambda n: n[0])
        for avant, apres in zip(notes, notes[1:]):
            assert avant[0] + avant[2] <= apres[0], \
                f"{piece['slug']} : la note du pas {avant[0]} mord sur {apres[0]}"


def test_une_piece_de_rue_tourne_assez_longtemps(rues):
    """⚠️ On s'arrete devant un musicien plus longtemps qu'une boucle de douze
    secondes. Le nombre de tours se CALCULE sur le tempo (`RUE_SECONDES_MIN`) :
    a deux tours fixes, le reel bouclait en 14 s et la valse en 12, et on
    entendait la couture avant d'avoir fini de regarder."""
    for piece in rues:
        duree = musique.duree_s(piece)
        assert musique.RUE_SECONDES_MIN <= duree <= 90, f"{piece['slug']} : {duree:.1f} s"


def test_les_cinq_pieces_ne_sonnent_pas_pareil(rues):
    """⚠️ Cinq morceaux qu'on prend pour un seul, ce sont quatre morceaux payes
    pour rien. Cinq tempos, cinq tonalites, cinq melodies — et une seule a
    TROIS TEMPS, ce qui s'entend meme sans rien connaitre a la musique."""
    assert len({m["bpm"] for m in rues}) == 5, "deux pieces au meme tempo"
    assert len({s["tonique"] for s in musique.RUE}) == 5, "deux pieces dans le meme ton"
    chants = [tuple(n[1] for n in next(v for v in m["voix"] if v["role"] == "chant")["notes"])
              for m in rues]
    assert len(set(chants)) == 5, "deux pieces avec la meme melodie"
    valses = [s for s in musique.RUE if s["mesure"] == 6]
    assert len(valses) == 1, f"il faut une valse, et une seule : {[s['slug'] for s in valses]}"


def test_le_volume_d_une_piece_de_rue_ne_sature_pas(rues):
    """Les deux voix passent dans le meme gain, et ce gain est DEJA multiplie
    par la distance : au plus fort, on est colle sur le musicien."""
    for piece in rues:
        pire = 0.0
        for pas in range(piece["pas"]):
            total = 0.0
            for voix in piece["voix"]:
                motif = voix.get("motif", piece["pas"])
                for note in voix["notes"]:
                    if note[0] != pas % motif:
                        continue
                    relatif = note[3] if len(note) > 3 else 1
                    total += voix["volume"] * relatif * piece["volume"]
            pire = max(pire, total)
        assert pire <= 1.0, f"{piece['slug']} : {pire:.2f}"


def test_le_musicien_de_rue_se_tasse_sous_une_poursuite():
    """⚠️ Ce n'est pas une piste, c'est un SON DU MONDE : il joue par-dessus
    l'ambiance du district, comme un moteur de char, et son volume vient de la
    distance. Il n'a qu'une regle de priorite — quand la police te court apres,
    la toune du guitariste n'a plus d'importance — et elle est ecrite ici,
    comme le reste de l'echelle."""
    assert "rue" not in musique.ECHELLE, "le musicien de rue n'est pas une piste"
    sous = musique.MUSIQUE["rue_sous_etat"]
    assert 0 < sous < 1, sous
    assert audio.exporter()["musique"]["rue_sous_etat"] == sous, "le navigateur ne le lirait pas"


def test_n_importe_quel_morceau_s_ecoute_avant_d_etre_livre():
    """⚠️ `par_slug` ne cherchait que dans `MORCEAUX` — le seul theme ecrit a la
    main. Les stations, les ambiances et les pieces de rue etaient donc
    INECOUTABLES avec `scripts/musique_apercu.py`, alors que c'est exactement a
    ca qu'il sert : juger une musique a l'oreille avant de la deployer. Cinq
    pieces de rue qu'on ne peut pas ecouter, ce sont cinq pieces qu'on livre en
    esperant."""
    for morceau in audio.exporter()["musiques"]:
        trouve = musique.par_slug(morceau["slug"])
        assert trouve is not None, f"{morceau['slug']} ne s'ecoute pas"
        assert trouve["slug"] == morceau["slug"]


# --- Toute la musique est generee par IA (14 sept. 2026) --------------------
#
# ⚠️ Demande de Martin : « je veux que toutes les musiques soient des musiques
# generees par IA ». Ce qui se juge ici n'est evidemment pas la musique — c'est
# l'oreille de Martin qui le fait — mais les trois choses qui la rendraient
# fausse sans qu'on s'en apercoive : un morceau qu'on aurait OUBLIE de generer
# (il resterait synthetise, et personne ne l'entendrait comme un manque), une
# piece PAYEE que le jeu ne joue pas, et un prompt qui ne decrit plus ce qu'on
# VOIT a l'ecran.


def test_chaque_morceau_du_jeu_a_sa_musique_generee():
    """LA demande, en un juge : plus un seul morceau ne reste en synthese."""
    oublies = sorted(audio.slugs_de_musique() - {p["slug"] for p in audio.MUSIQUES})
    assert not oublies, (
        f"ces morceaux n'ont aucune musique generee : {oublies} — ils resteraient "
        "joues par les oscillateurs, et rien ne le dirait")


def test_on_ne_genere_que_la_musique_que_le_jeu_joue():
    """⚠️ Une piece dont le slug ne correspond a aucun morceau serait un fichier
    PAYE que personne ne jouerait jamais. Le filtre coute une ligne."""
    connus = audio.slugs_de_musique()
    for piece in audio.musiques_manquantes():
        assert piece["slug"] in connus, f"{piece['slug']} : paye pour rien"


def test_chaque_piece_nomme_un_morceau_une_seule_fois():
    slugs = [p["slug"] for p in audio.MUSIQUES]
    assert len(slugs) == len(set(slugs)), f"deux pieces du meme nom : {slugs}"


def test_chaque_piece_a_un_volume_qui_va_avec_un_mp3():
    """⚠️ Le volume d'un mp3 n'est PAS celui des notes : dans le sequenceur, le
    volume du morceau multiplie celui de chaque voix (0,11 a 0,45), donc
    `titre` a 0,85 sort a un dixieme de l'echelle. Un fichier arrive normalise
    a -1 dBFS ; le meme chiffre saturerait."""
    for piece in audio.MUSIQUES:
        v = piece["volume"]
        assert 0 < v <= 0.6, (
            f"{piece['slug']} : volume {v} — au-dela de 0,6 un mp3 normalise "
            "couvre les moteurs, les sirenes et les voix")


def test_chaque_boucle_dure_assez_pour_ne_pas_se_mordre_la_queue():
    """⚠️ Sous vingt-quatre secondes, on entend la boucle recommencer : on
    s'arrete devant un musicien plus longtemps que ca, et on traverse un
    district bien plus longtemps encore."""
    for piece in audio.MUSIQUES:
        assert 24 <= piece["duree_s"] <= 90, f"{piece['slug']} : {piece['duree_s']} s"


def test_aucune_musique_ne_chante():
    """Une voix chantee par-dessus une sirene : on n'entend plus ni l'une ni
    l'autre. C'est la meme regle que pour les radios depuis M3."""
    for piece in audio.MUSIQUES:
        assert "no vocals" in piece["prompt"], f"{piece['slug']} : le prompt laisse chanter"


def test_le_musicien_de_rue_reste_un_homme_seul():
    """⚠️ La fiche du morceau ecrit le dit en majuscules — « DEUX VOIX, PAS
    QUATRE » : un gars tout seul sur un trottoir n'a pas de batteur derriere
    lui. Un prompt qui laisse arriver un groupe donne une musique qui ne colle
    plus a ce qu'on VOIT, et le musicien de rue n'a plus aucun interet."""
    rues = [p for p in audio.MUSIQUES if p["slug"].startswith("rue_")]
    assert len(rues) == 5, "les cinq pieces du musicien de rue : %s" % [p["slug"] for p in rues]
    for piece in rues:
        assert "solo" in piece["prompt"], f"{piece['slug']} : rien ne dit qu'il est seul"
        assert "guitar" in piece["prompt"], f"{piece['slug']} : il a une guitare dans les mains"
        assert "no drums" in piece["prompt"], f"{piece['slug']} : il n'a pas de batteur"
        assert "no other instruments" in piece["prompt"], f"{piece['slug']} : un groupe arriverait"


def test_les_ambiances_de_district_ne_battent_pas_la_mesure():
    """Elles jouent SOUS la rumeur, les moteurs et les voix. Une ambiance de
    district qu'on remarque est une ambiance de district ratee."""
    for slug in musique.AMBIANCES_DE_DISTRICT.values():
        piece = audio.piece_par_slug(slug)
        assert piece is not None, slug
        assert "no drums" in piece["prompt"], f"{slug} : une batterie sous un district"


def test_le_paquet_marie_les_notes_et_le_fichier():
    """Le navigateur recoit les deux et choisit : le mp3 s'il est la, les notes
    sinon. ⚠️ `fichier` ne se declare que si le fichier est VRAIMENT sur le
    disque — sinon le navigateur irait chercher un 404."""
    for morceau in audio.exporter()["musiques"]:
        assert morceau["voix"], f"{morceau['slug']} : plus de filet"
        assert "fichier" in morceau and "volume_fichier" in morceau, morceau["slug"]
        if morceau["fichier"] is not None:
            assert audio.chemin_musique(morceau["slug"]).is_file(), morceau["slug"]
            assert morceau["volume_fichier"], f"{morceau['slug']} : un mp3 sans volume"


def test_les_musiques_ne_marchent_pas_sur_les_radios():
    """Deux catalogues, deux prefixes : `musique-*.mp3` et `radio-*.mp3`. Un
    nom partage ferait qu'une station ecraserait un district sur le disque."""
    noms = ([audio.nom_fichier_musique(p["slug"]) for p in audio.MUSIQUES]
            + [audio.nom_fichier_radio(r) for r in audio.RADIOS + audio.AMBIANCES])
    assert len(noms) == len(set(noms)), "deux musiques ecrivent dans le meme fichier"


def test_la_musique_generee_tient_dans_le_budget():
    """⚠️ Ce que ca PESE, et c'est le vrai prix de la demande. A 64 kbit/s, une
    seconde fait 8 Ko : les quinze pieces sont le plus gros poste du dossier
    audio. Elles ne se chargent JAMAIS au demarrage — une ambiance arrive quand
    on entre dans son district, une station au premier tour de cle — mais le
    depot, lui, les porte toutes."""
    secondes = sum(p["duree_s"] for p in audio.MUSIQUES)
    ko = secondes * 8
    # ⚠️ Relevé de 6 000 à 12 000 Ko le 16 sept. 2026, sur décision de Martin
    # (« tu peux augmenter les budgets... pas de sens »). Ce plafond-ci n'a
    # jamais eu la raison de celui des bruitages : **une musique ne se
    # télécharge qu'au tour de clé ou à l'entrée d'une pièce**, jamais au
    # démarrage. Il ne servait qu'à nous faire écrire des boucles courtes
    # qu'on entend reboucler.
    assert ko < 12000, f"{secondes} s de musique, soit {ko} Ko : le depot enfle"


def test_le_fondu_enchaine_est_ecrit_une_fois_et_le_navigateur_le_lit():
    """⚠️ Demande de Martin (20 sept. 2026) : « les transitions de musique doivent
    toujours se faire en crossover, a moins que ce soit necessaire pour l'effet et
    l'ambiance ». `fondu_s` etait declare depuis le premier jour et le JS ne le
    lisait jamais — d'ou des pistes coupees net. Il y a maintenant DEUX durees, et
    la vive est plus courte que la lente : c'est l'exception qui garde la regle."""
    r = audio.exporter()["musique"]
    assert r["fondu_s"] > 0, "sans fondu, chaque changement de piste est une coupure"
    assert 0 < r["fondu_vif_s"] < r["fondu_s"], (r["fondu_vif_s"], r["fondu_s"])


def test_le_volume_baisse_et_remonte_graduellement_les_chiffres_sont_ecrits_une_fois():
    """⚠️ Demande de Martin (20 sept. 2026) : « il faut aussi baisser les volumes et
    les monter graduellement ». Le quart etait ecrit en dur, deux fois, dans le JS ;
    il est maintenant ici, avec la duree de la descente et celle de la remontee — et
    la remontee est PLUS LENTE : deux repliques d'une conversation ne la laissent pas
    revenir entre les deux."""
    r = audio.exporter()["musique"]
    assert 0 < r["ducking"] < 1, r["ducking"]
    assert 0 < r["baisse_s"] < r["remonte_s"], (r["baisse_s"], r["remonte_s"])
