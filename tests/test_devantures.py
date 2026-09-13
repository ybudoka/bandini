"""Les devantures et les graffitis : une couche peinte qui ne doit rien casser.

⚠️ La regle qui tient tout : une devanture se PEINT par-dessus des murs qui
existent deja. Elle ne deplace pas une tuile, ne change pas une solidite, ne
bouche pas une porte. Le jour ou elle le ferait, ce sont les juges de
circulation et de connexite qui tomberaient — trois fichiers plus loin, sans
qu'on comprenne pourquoi. D'ou les juges d'ici : ils gardent la frontiere.
"""

import pytest

from app import carte, devantures

TUILE = carte.TUILE_PX
#: Les glyphes sur lesquels une enseigne a le droit de se poser.
MURS_DEVANTURE = frozenset({"W", "F", "D", "d", "G"})


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


@pytest.fixture(scope="module")
def sol(ville):
    return ville["sol"]


def test_la_ville_a_des_devantures(ville):
    assert len(ville["devantures"]) >= 60, len(ville["devantures"])
    assert len(ville["graffitis"]) >= 15, len(ville["graffitis"])


def test_chaque_enseigne_tient_dans_son_bandeau(ville):
    """⚠️ Un nom trop long deborde du bandeau et se lit par-dessus le mur du
    voisin. On renonce a l'enseigne plutot que de couper le nom."""
    for d in ville["devantures"]:
        assert devantures.tient_en(d["texte"], d["l"], TUILE), (
            f"{d['texte']!r} ({devantures.largeur_texte_px(d['texte'])} px) "
            f"sur {d['l']} tuiles ({d['l'] * TUILE} px)")


def test_une_enseigne_est_posee_sur_un_mur(ville, sol):
    """Une enseigne dans le vide flotterait au-dessus du trottoir."""
    for d in ville["devantures"]:
        for i in range(d["l"]):
            g = sol[d["y"]][d["x"] + i]
            assert g in MURS_DEVANTURE, f"{d['texte']} : tuile « {g} » en ({d['x'] + i},{d['y']})"


def test_une_enseigne_se_voit_depuis_la_rue(ville, sol):
    """⚠️ Au moins une tuile du bandeau doit donner sur du marchable : une
    enseigne collee au mur du voisin, personne ne la lira jamais."""
    for d in ville["devantures"]:
        vues = [i for i in range(d["l"])
                if carte.marchable(sol[d["y"] + 1][d["x"] + i])]
        assert vues, f"{d['texte']} en ({d['x']},{d['y']}) ne donne sur rien"


def test_deux_enseignes_ne_se_marchent_pas_dessus(ville):
    pris: dict[tuple[int, int], str] = {}
    for d in ville["devantures"]:
        for i in range(d["l"]):
            cle = (d["x"] + i, d["y"])
            assert cle not in pris, f"{d['texte']} recouvre {pris[cle]} en {cle}"
            pris[cle] = d["texte"]


def test_la_largeur_reste_dans_les_bornes(ville):
    for d in ville["devantures"]:
        assert carte._Chantier.ENSEIGNE_MIN <= d["l"] <= carte._Chantier.ENSEIGNE_ETIREE, d


def test_les_genres_existent(ville):
    for d in ville["devantures"]:
        assert 0 <= d["genre"] < len(devantures.GENRES), d
    for g in ville["graffitis"]:
        assert 0 <= g["couleur"] < len(devantures.COULEURS_TAG), g
        assert g["motif"] in devantures.MOTIFS, g


def test_la_devanture_ne_change_aucune_solidite():
    """⚠️ LE juge de la frontiere. Poser une enseigne transforme des façades
    (`F`) en vitrines (`W`) — et ces deux-la DOIVENT avoir exactement la meme
    solidite, sinon une rue commercante deviendrait franchissable (ou un mur
    pousserait au milieu du trottoir) sans qu'aucun autre test ne le voie."""
    assert carte.LEGENDE["W"]["solide"] == carte.LEGENDE["F"]["solide"] == 1
    for glyphe in MURS_DEVANTURE:
        assert carte.LEGENDE[glyphe].get("solide") == 1, glyphe


def test_la_planque_n_a_pas_d_enseigne(ville):
    """Une planque avec son nom sur le mur n'est plus une planque."""
    noms = {d["texte"] for d in ville["devantures"]}
    assert "LA PLANQUE DE ROCCO" not in noms
    assert "PLANQUE" not in noms
    planque = next(p for p in ville["points_interet"] if p["slug"] == "planque")
    for d in ville["devantures"]:
        if d["y"] == planque["y"] - 1:
            assert not (d["x"] <= planque["x"] < d["x"] + d["l"]), d


def test_les_lieux_garantis_portent_leur_enseigne(ville):
    """Un magasin nomme doit se reconnaître de la rue — c'est la moitie de ce
    qui fait qu'on le retrouve sans regarder la carte."""
    attendus = {"armurerie", "vetements", "garage", "bar", "casse_croute",
                "depanneur", "hotel", "cantine", "usine"}
    posees = {d["texte"] for d in ville["devantures"] if d["porte"]}
    manquants = []
    for slug in sorted(attendus):
        choix = devantures.enseigne_speciale(slug, slug)
        assert choix is not None, slug
        if choix[0] not in posees:
            manquants.append(slug)
    assert not manquants, f"sans enseigne : {manquants}"


def test_un_graffiti_est_sur_un_mur_nu(ville, sol):
    """⚠️ Jamais sur une vitrine ni sur une route : un commerce lave sa vitre,
    et un tag peint sur l'asphalte n'est pas un tag."""
    enseignes = {(d["x"] + i, d["y"]) for d in ville["devantures"] for i in range(d["l"])}
    for g in ville["graffitis"]:
        glyphe = sol[g["y"]][g["x"]]
        assert glyphe in ("F", "d"), f"tag « {g['texte']} » sur « {glyphe} »"
        assert (g["x"], g["y"]) not in enseignes, g


def test_un_graffiti_se_voit_depuis_la_rue(ville, sol):
    for g in ville["graffitis"]:
        assert carte.marchable(sol[g["y"] + 1][g["x"]]), g


def test_deux_graffitis_ne_se_superposent_pas(ville):
    places = [(g["x"], g["y"]) for g in ville["graffitis"]]
    assert len(places) == len(set(places))


def test_les_gangs_ne_taguent_que_chez_eux(ville):
    """⚠️ Le tag dit le TERRITOIRE : voir « CRAVATES » sur un mur apprend au
    joueur chez qui il est. Un nom de gang a l'autre bout de la ville detruit
    cette information au lieu de la donner."""
    cours = [(z["x"], z["y"], z["l"], z["h"], z["gang"])
             for z in ville["zones"] if z.get("gang")]
    assert cours, "aucune cour de gang : le juge ne prouverait rien"
    par_gang: dict[str, tuple[str, ...]] = devantures.TAGS_GANG
    for g in ville["graffitis"]:
        proprietaire = next((gang for gang, mots in par_gang.items() if g["texte"] in mots), None)
        if proprietaire is None:
            continue
        proche = any(zx - 8 <= g["x"] < zx + zl + 8 and zy - 8 <= g["y"] < zy + zh + 8
                     for zx, zy, zl, zh, gang in cours if gang == proprietaire)
        assert proche, f"« {g['texte']} » en ({g['x']},{g['y']}) loin de toute cour {proprietaire}"


def test_chaque_quartier_a_ses_propres_commerces():
    """Une poissonnerie aux Erables et une garderie sur les quais, et les cinq
    districts redeviennent le meme quartier repeint."""
    vus: dict[str, set[str]] = {}
    for district, liste in devantures.COMMERCES.items():
        noms = {nom for nom, _ in liste}
        assert len(noms) == len(liste), f"{district} : deux fois le meme nom"
        vus[district] = noms
    assert vus["quais"] & {"POISSONNERIE", "CORDAGES"}
    assert not (vus["erables"] & {"POISSONNERIE", "CHANTIER NAVAL"})
    assert not (vus["shop"] & {"FLEURISTE ROSE"})


def test_tous_les_noms_du_catalogue_tiennent_sur_une_enseigne():
    """Un nom qu'aucune bande ne peut porter ne s'afficherait jamais : autant
    le savoir ici plutot que de chercher pourquoi ce commerce est muet."""
    maxi = carte._Chantier.ENSEIGNE_ETIREE
    for district, liste in devantures.COMMERCES.items():
        for nom, famille in liste:
            assert devantures.tient_en(nom, maxi, TUILE), f"{district} : {nom!r} trop long"
            assert famille in devantures.INDEX_GENRE, f"{nom!r} : genre inconnu {famille!r}"
    for slug, (nom, famille) in devantures.ENSEIGNES.items():
        assert devantures.tient_en(nom, maxi, TUILE), f"{slug} : {nom!r} trop long"
        assert famille in devantures.INDEX_GENRE, f"{slug} : genre inconnu {famille!r}"


def test_un_tag_pose_tient_dans_les_murs_contigus(ville, sol):
    """⚠️ Un tag a le droit de deborder sur le mur d'a cote — pas sur le
    trottoir ni sur une vitrine. On compte la place reelle et on verifie que le
    mot y rentre."""
    for g in ville["graffitis"]:
        place = 1
        while place < 3 and g["x"] + place < len(sol[0]) \
                and sol[g["y"]][g["x"] + place] in ("F", "d"):
            place += 1
        assert devantures.tient_en(g["texte"], place, TUILE, marge=0), (
            f"« {g['texte']} » ({devantures.largeur_texte_px(g['texte'])} px) "
            f"sur {place} tuile(s) en ({g['x']},{g['y']})")


def test_le_plus_court_des_tags_tient_toujours_sur_un_mur():
    """Il doit rester quelque chose a ecrire sur un mur isole, sinon les murs
    seuls ne sont jamais tagues."""
    courts = [m for m in devantures.TAGS_LIBRES
              if devantures.tient_en(m, 1, TUILE, marge=0)]
    assert courts, "aucun tag ne tient sur une seule tuile"


def test_chaque_devanture_eclaire_son_trottoir(ville):
    """Sans lumiere, tout ce travail disparaît la moitie du temps de jeu."""
    vitrines = [lampe for lampe in ville["lampes"] if lampe.get("c") == "vitrine"]
    assert len(vitrines) == len(ville["devantures"])
    for lampe in vitrines:
        assert lampe["r"] > 0


def test_le_meme_grain_donne_la_meme_rue():
    a = carte.generer(graine=4242)
    b = carte.generer(graine=4242)
    assert a["devantures"] == b["devantures"]
    assert a["graffitis"] == b["graffitis"]


def test_une_autre_graine_donne_d_autres_enseignes():
    a = carte.generer(graine=1)
    b = carte.generer(graine=2)
    assert a["devantures"] != b["devantures"]


@pytest.mark.parametrize("graine", [1, 7, 99, 777])
def test_les_regles_tiennent_sur_d_autres_graines(graine):
    ville = carte.generer(graine=graine)
    sol = ville["sol"]
    assert ville["devantures"], graine
    for d in ville["devantures"]:
        assert devantures.tient_en(d["texte"], d["l"], TUILE), (graine, d)
        for i in range(d["l"]):
            assert sol[d["y"]][d["x"] + i] in MURS_DEVANTURE, (graine, d)
    for g in ville["graffitis"]:
        assert sol[g["y"]][g["x"]] in ("F", "d"), (graine, g)
