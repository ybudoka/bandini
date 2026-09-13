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


# --- On doit TOUJOURS voir une porte -------------------------------------------
# ⚠️ Retour de Martin : « assure-toi qu'on voit toujours une porte même si elle
# peut être différente quand il y a une devanture ». Le bandeau, l'auvent et la
# vitrine couvraient toute la bande : on lisait le nom du commerce et on ne
# voyait plus par ou entrer. La devanture porte donc `motifs`, une lettre par
# tuile, qui dit au peintre ce qu'il y a dessous.

#: « W » vitrine · « D » porte qu'on ouvre · « d » condamnee · « G » garage
#: · « P » porte PEINTE (le sol reste un mur : elle ne promet rien).
MOTIFS_CONNUS = frozenset("WDdGP")
PORTES_VISIBLES = frozenset("DdGP")


def test_chaque_devanture_dit_ce_qu_il_y_a_dessous(ville):
    for d in ville["devantures"]:
        assert len(d["motifs"]) == d["l"], d
        assert set(d["motifs"]) <= MOTIFS_CONNUS, d


def test_on_voit_toujours_une_porte(ville):
    """La garantie que Martin a demandee, en un juge."""
    sans = [d["texte"] for d in ville["devantures"]
            if not set(d["motifs"]) & PORTES_VISIBLES]
    assert not sans, f"devantures sans aucune porte visible : {sans}"


def test_le_masque_dit_la_verite_du_sol(ville, sol):
    """⚠️ Sauf « P » : celle-la est peinte sur un mur plein, et c'est justement
    ce qui fait qu'elle ne s'ouvre pas."""
    for d in ville["devantures"]:
        for i, lettre in enumerate(d["motifs"]):
            glyphe = sol[d["y"]][d["x"] + i]
            attendu = "W" if lettre == "P" else lettre
            assert glyphe == attendu, (
                f"{d['texte']} tuile {i} : le masque dit « {lettre} », le sol « {glyphe} »")


def test_une_porte_peinte_ne_remplace_jamais_une_vraie(ville):
    for d in ville["devantures"]:
        if "P" in d["motifs"]:
            assert not set(d["motifs"]) & set("DdG"), (
                f"{d['texte']} : une porte peinte alors qu'il y en a une vraie ({d['motifs']})")
            assert d["motifs"].count("P") == 1, d


def test_une_porte_peinte_donne_sur_le_trottoir(ville, sol):
    """Une porte peinte contre le mur du voisin ne se verrait jamais."""
    for d in ville["devantures"]:
        i = d["motifs"].find("P")
        if i < 0:
            continue
        devant = sol[d["y"] + 1][d["x"] + i]
        assert carte.marchable(devant), f"{d['texte']} : porte peinte devant « {devant} »"


def test_une_porte_ouvrable_est_une_vraie_porte(ville):
    """⚠️ Le sens inverse du juge precedent : un « D » dans le masque doit
    correspondre a une porte du catalogue, sinon on peint une poignee doree —
    la promesse qu'on peut entrer — sur un mur."""
    vraies = {(p["x"], p["y"]) for p in ville["portes"]}
    for d in ville["devantures"]:
        for i, lettre in enumerate(d["motifs"]):
            if lettre == "D":
                assert (d["x"] + i, d["y"]) in vraies, f"{d['texte']} : fausse porte ouvrable"


def test_les_commerces_visitables_montrent_leur_porte(ville):
    """Les treize lieux qu'on peut visiter doivent tous exhiber leur porte."""
    visitables = [d for d in ville["devantures"] if d["porte"]]
    assert len(visitables) >= 10, len(visitables)
    for d in visitables:
        assert "D" in d["motifs"], f"{d['texte']} se visite mais ne montre pas de porte"


@pytest.mark.parametrize("graine", [1, 7, 99, 777])
def test_on_voit_toujours_une_porte_sur_d_autres_graines(graine):
    ville = carte.generer(graine=graine)
    for d in ville["devantures"]:
        assert set(d["motifs"]) & PORTES_VISIBLES, (graine, d)
        assert len(d["motifs"]) == d["l"], (graine, d)


# --- Les logements ---------------------------------------------------------------
# ⚠️ Deuxieme retour de Martin (13 sept. 2026) : « plus de variete de commerces,
# ou bien enleve des devantures pour mettre des residences ». Les deux. Une
# residence est la MEME chose qu'une devanture pour la carte : une couche
# peinte, zero solidite touchee. Les juges ci-dessous gardent cette frontiere-la
# exactement comme ceux des enseignes.


def test_la_ville_a_des_logements(ville):
    assert len(ville["residences"]) >= 50, len(ville["residences"])


def test_on_habite_dans_les_quartiers_ou_l_on_habite(ville):
    """Le Faubourg et les Erables ont des logements ; La Shop, c'est des
    entrepots — un immeuble a logements au milieu de la ferraille dirait le
    contraire de ce que le quartier raconte."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    quartiers = {}
    for residence in ville["residences"]:
        district = chantier.district_en(residence["x"], residence["y"])
        quartiers[district] = quartiers.get(district, 0) + 1
    assert quartiers.get("faubourg", 0) >= 10, quartiers
    assert quartiers.get("erables", 0) >= 10, quartiers


def test_une_residence_est_posee_sur_un_mur(ville, sol):
    for r in ville["residences"]:
        for i in range(r["l"]):
            g = sol[r["y"]][r["x"] + i]
            assert g in MURS_DEVANTURE, f"logement en ({r['x'] + i},{r['y']}) : tuile « {g} »"


def test_une_residence_se_voit_depuis_la_rue(ville, sol):
    for r in ville["residences"]:
        vues = [i for i in range(r["l"]) if carte.marchable(sol[r["y"] + 1][r["x"] + i])]
        assert vues, f"logement en ({r['x']},{r['y']}) ne donne sur rien"


def test_rien_ne_se_peint_deux_fois_sur_le_meme_mur(ville):
    """⚠️ Une enseigne par-dessus un immeuble a logements, et on lirait
    « BOULANGERIE » entre deux rangees de fenetres."""
    pris: dict[tuple[int, int], str] = {}
    for couche, nom in ((ville["devantures"], "enseigne"), (ville["residences"], "logement")):
        for p in couche:
            for i in range(p["l"]):
                cle = (p["x"] + i, p["y"])
                assert cle not in pris, f"{nom} par-dessus {pris[cle]} en {cle}"
                pris[cle] = nom


def test_le_masque_d_un_logement_dit_la_verite_du_sol(ville, sol):
    for r in ville["residences"]:
        assert len(r["motifs"]) == r["l"], r
        for i, lettre in enumerate(r["motifs"]):
            glyphe = sol[r["y"]][r["x"] + i]
            if lettre == "P":
                assert glyphe in ("F", "W"), r
            else:
                assert glyphe == lettre, r


def test_on_voit_toujours_par_ou_l_on_rentre_chez_soi(ville):
    for r in ville["residences"]:
        assert set(r["motifs"]) & PORTES_VISIBLES, f"logement sans porte : {r}"
        assert 0 <= r["porte"] < r["l"], r
        assert r["motifs"][r["porte"]] in PORTES_VISIBLES, r


def test_les_etages_restent_dans_les_bornes(ville):
    for r in ville["residences"]:
        assert 1 <= r["etages"] <= 3, r
        assert r["escalier"] in (-1, 0, 1), r
        assert 0 <= r["mur"] < len(devantures.MURS), r
        assert r["balcon"] in (0, 1), r
        # Un escalier exterieur sans etage a monter n'est qu'un obstacle.
        assert r["etages"] >= 2 or r["escalier"] == 0, r


def test_l_escalier_exterieur_descend_sur_du_marchable(ville, sol):
    """⚠️ Il se peint sur la tuile SOUS la porte : s'il tombait dans un mur ou
    sur la chaussee, on verrait des marches de fer au milieu de la rue."""
    for r in ville["residences"]:
        if r["etages"] < 2:
            continue
        x, y = r["x"] + r["porte"], r["y"] + 1
        assert carte.marchable(sol[y][x]), f"escalier dans « {sol[y][x]} » en ({x},{y})"


def test_un_logement_ne_change_aucune_solidite(ville, sol):
    """Le juge de la frontiere, comme pour les enseignes : la couche peinte ne
    transforme pas une tuile. Une residence ne repeint meme pas les vitrines."""
    for r in ville["residences"]:
        for i in range(r["l"]):
            assert carte.LEGENDE[sol[r["y"] + 0][r["x"] + i]].get("solide") == 1


def test_les_familles_de_brique_se_tiennent(ville):
    for m in devantures.MURS:
        assert set(m) == {"slug", "brique", "joint", "cadre", "vitre", "allumee", "porte"}
        for cle, valeur in m.items():
            if cle != "slug":
                assert valeur.startswith("#") and len(valeur) == 7, m
    assert set(devantures.FER) == {"barreau", "marche", "arete", "ombre"}


def test_une_fenetre_allumee_n_est_pas_un_lampadaire(ville):
    """Trois sortes de lumiere, trois comportements. La fenetre est la plus
    faible et la plus rare : une rue ou toutes les fenetres brillent a trois
    heures du matin ment sur la ville."""
    fenetres = [lampe for lampe in ville["lampes"] if lampe.get("c") == "fenetre"]
    assert fenetres, "aucune fenetre allumee : la nuit, les logements sont des blocs noirs"
    assert len(fenetres) <= len(ville["residences"]) * 0.6, "toute la ville veille"
    for lampe in fenetres:
        assert lampe["r"] < 45, "une fenetre n'eclaire pas comme un lampadaire"


# --- La variete des enseignes ----------------------------------------------------


def test_chaque_quartier_a_de_quoi_ne_pas_se_repeter():
    """⚠️ Mesure du 13 sept. 2026 : huit noms pour vingt-quatre vitrines a La
    Shop donnaient sept « FERRAILLE ». Il faut au moins de quoi habiller une rue
    entiere sans revenir sur ses pas."""
    for district, liste in devantures.COMMERCES.items():
        assert len(liste) >= 14, f"{district} : {len(liste)} noms seulement"


def test_deux_enseignes_pareilles_ne_se_voient_pas_du_meme_trottoir(ville):
    """La regle de `choisir_enseigne`, jugee sur la ville finie."""
    par_nom: dict[str, list[tuple[int, int]]] = {}
    for d in ville["devantures"]:
        par_nom.setdefault(d["texte"], []).append((d["x"], d["y"]))
    for nom, places in par_nom.items():
        for i, a in enumerate(places):
            for b in places[i + 1:]:
                ecart = max(abs(a[0] - b[0]), abs(a[1] - b[1]))
                assert ecart >= devantures.DISTANCE_DOUBLON, \
                    f"deux « {nom} » a {ecart} tuiles l'une de l'autre ({a} et {b})"


def test_la_rue_porte_plusieurs_familles_de_commerce(ville):
    """Sept familles pour cent commerces, c'etait deux rues de la meme couleur.
    Toutes doivent servir — sinon autant les enlever du catalogue."""
    genres = {d["genre"] for d in ville["devantures"]}
    assert len(genres) >= 8, f"seulement {len(genres)} familles sur {len(devantures.GENRES)}"


@pytest.mark.parametrize("graine", [1, 7, 99, 777])
def test_les_logements_tiennent_sur_d_autres_graines(graine):
    ville = carte.generer(graine=graine)
    sol = ville["sol"]
    assert ville["residences"], graine
    for r in ville["residences"]:
        assert len(r["motifs"]) == r["l"], (graine, r)
        assert set(r["motifs"]) & PORTES_VISIBLES, (graine, r)
        for i in range(r["l"]):
            assert sol[r["y"]][r["x"] + i] in MURS_DEVANTURE, (graine, r)
