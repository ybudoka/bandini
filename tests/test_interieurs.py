"""Les juges des interieurs — ce qui doit etre vrai AVANT d'ouvrir une porte.

⚠️ Le probleme que ces tests gardent fermé : « on ouvre une porte et il n'y a
jamais rien, juste des comptoirs vides » (Martin, 13 sept. 2026). Une piece
peut etre vide de trois facons, et aucune ne se voit sur une capture d'ecran :
elle n'a pas de meubles, ses comptoirs ne donnent rien, ou personne ne s'y
tient. Un juge par facon.

Le plan de chaque piece est deja verifie a l'import (`carte._piece` : porte
unique, plancher d'un seul tenant, points atteignables) — ici on juge ce qu'il
y a DEDANS, et les promesses que les portes de la ville font au joueur.
"""

import math

import pytest

from app import armes, carte, devantures, economie, magasins, missions, pietons

VILLE = carte.exporter()

#: Les meubles : tout ce qui n'est ni plancher, ni mur, ni porte.
MEUBLES = frozenset(g for g, p in carte.LEGENDE.items() if p.get("meuble"))

#: Ce qu'un point peut demander au navigateur. ⚠️ Cette liste est la moitie
#: d'un contrat : l'autre moitie est dans `missions.js` (`LIBELLES` et
#: `menuDuPoint`), et `tests/test_moteur_js.py` verifie que les deux
#: s'accordent. Un type ajoute ici sans son cas la-bas est un comptoir mort.
TYPES_SERVIS = frozenset({
    "lit", "coffre", "garde_robe", "vendre", "reparer", "repeindre", "acheter",
    "hotdog", "soigner", "caisse", "journal", "contact", "sergent", "casier",
    "fourriere", "emplettes", "salon", "escalier", "fouiller",
})


@pytest.mark.parametrize("slug", sorted(carte.INTERIEURS))
def test_aucun_comptoir_ne_vole_la_porte(slug):
    """⚠️ Le bloquant du 13 sept. 2026 : « chez Ti-Paul, il est impossible de
    sortir ». Six pieces etaient sans issue, et la cause tenait a deux rayons qui
    ne se parlaient pas : ACTION attrape un point d'action dans **1,6 tuile
    autour** de soi, alors que la porte n'accepte que la tuile collee a elle. Un
    comptoir pose assez pres de l'unique tuile de sortie prenait donc ACTION a
    chaque fois — et chez Ti-Paul, le point du journal etait PILE dessus.

    Le jeu fait maintenant passer la porte avant le comptoir ; ce juge-ci garde
    la porte de sortie libre, pour que le piege ne se redessine pas. ⚠️ Il
    rougissait six fois le jour ou il a ete ecrit. C'est le genre de regle qu'on
    ne voit qu'en jouant et qui se verifie en trois lignes."""
    piece = carte.INTERIEURS[slug]
    sortie = piece["apparition"]
    for point in piece["points"]:
        ecart = math.hypot(point["x"] - sortie["x"], point["y"] - sortie["y"])
        assert ecart >= carte.RAYON_POINT, (
            f"{slug} : le point {point['type']} est a {ecart:.2f} tuile de la sortie "
            f"— il volerait ACTION a la porte"
        )


@pytest.mark.parametrize("slug", sorted(carte.INTERIEURS))
def test_une_piece_est_meublee(slug):
    """⚠️ LE juge de la demande de Martin. Une piece de quinze tuiles sur neuf
    avec un comptoir de sept tuiles, c'est 5 % de meubles : on entre, on voit
    du plancher. Un dixieme de la piece, au minimum, doit etre quelque chose —
    et il faut au moins deux SORTES de meubles, sinon c'est le comptoir vide
    d'avant avec un comptoir plus long."""
    piece = carte.INTERIEURS[slug]
    tuiles = "".join(piece["sol"])
    meubles = [g for g in tuiles if g in MEUBLES]
    aire = piece["largeur"] * piece["hauteur"]
    assert len(meubles) >= aire * 0.10, f"{slug} : {len(meubles)} meubles pour {aire} tuiles"
    assert len(set(meubles)) >= 2, f"{slug} : un seul genre de meuble ({set(meubles)})"


@pytest.mark.parametrize("slug", sorted(carte.INTERIEURS))
def test_une_piece_donne_quelque_chose_a_faire(slug):
    """Un comptoir qui ne donne rien est une porte qu'on ouvre pour rien."""
    piece = carte.INTERIEURS[slug]
    assert piece["points"], f"{slug} : aucun point d'action"
    for point in piece["points"]:
        assert point["type"] in TYPES_SERVIS, f"{slug} : « {point['type']} » n'est servi nulle part"


@pytest.mark.parametrize("slug", sorted(carte.INTERIEURS))
def test_une_piece_dit_quel_plancher_elle_a(slug):
    """⚠️ Un meuble ne couvre pas toute sa tuile : le peintre doit savoir quoi
    mettre DESSOUS. Sans `plancher`, chaque table etait un trou noir dans le
    plancher — et rien, cote Python, ne s'en serait apercu."""
    piece = carte.INTERIEURS[slug]
    plancher = piece["plancher"]
    assert carte.solidite(plancher) == 0, f"{slug} : on ne marche pas sur « {plancher} »"
    assert carte.LEGENDE[plancher].get("dedans"), f"{slug} : « {plancher} » n'est pas un plancher"


def test_deux_points_ne_se_marchent_pas_dessus():
    """⚠️ `pointSousLaMain` prend le plus proche dans un rayon d'une tuile et
    demie : deux points colles, et l'un des deux est injoignable a jamais."""
    for slug, piece in carte.INTERIEURS.items():
        for i, a in enumerate(piece["points"]):
            for b in piece["points"][i + 1:]:
                ecart = max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"]))
                assert ecart >= 2, f"{slug} : {a['type']} et {b['type']} se touchent"


def test_l_escalier_monte_et_redescend():
    """Un escalier qui ne ramene pas est un cul-de-sac : on serait pris en haut
    (la porte du haut sort dehors, mais on ne l'a pas choisie)."""
    for slug, piece in carte.INTERIEURS.items():
        for point in piece["points"]:
            if point["type"] != "escalier":
                continue
            cible = point.get("vers")
            assert cible in carte.INTERIEURS, f"{slug} : l'escalier mene a « {cible} »"
            retours = [q for q in carte.INTERIEURS[cible]["points"]
                       if q["type"] == "escalier" and q.get("vers") == slug]
            assert retours, f"{cible} : aucun escalier ne redescend vers {slug}"


def test_chaque_comptoir_ordinaire_vend_quelque_chose():
    """Un point `emplettes` nomme une famille de commerce ; cette famille doit
    avoir un comptoir, et chaque article doit pointer sur quelque chose."""
    for slug, piece in carte.INTERIEURS.items():
        for point in piece["points"]:
            if point["type"] != "emplettes":
                continue
            genre = point.get("genre")
            assert genre in magasins.COMPTOIRS, f"{slug} : pas de comptoir « {genre} »"


def test_les_articles_des_comptoirs_existent():
    tenues = {t["slug"] for t in magasins.TENUES}
    for genre, comptoir in magasins.COMPTOIRS.items():
        assert genre in devantures.INDEX_GENRE, f"comptoir « {genre} » : famille inconnue"
        assert comptoir["articles"], f"{genre} : comptoir vide"
        for article in comptoir["articles"]:
            cibles = [article["tarif"], article["arme"], article["tenue"]]
            assert sum(1 for c in cibles if c) == 1, f"{genre}/{article['slug']} : une seule sorte d'article"
            if article["tarif"]:
                assert article["tarif"] in economie.TARIFS, article
            if article["arme"]:
                arme = armes.par_slug(article["arme"])
                assert arme and arme["prix"] > 0, f"{genre} : l'arme {article['arme']} ne se vend pas"
            if article["tenue"]:
                assert article["tenue"] in tenues, article
            for cle in ("gain_pv", "gain_souffle"):
                if article[cle]:
                    assert article[cle] in economie.TARIFS, article
            if article["effet"]:
                assert article["effet"] in magasins.EFFETS, article


def test_ce_qui_se_mange_au_comptoir_nourrit_moins_que_le_kiosque():
    """⚠️ Un depanneur depanne, il ne nourrit pas : au dollar, son sandwich doit
    rester moins bon que le hot-dog du trottoir. Sinon les kiosques — qui sont
    dehors, donc dans le risque — ne servent plus a rien."""
    from app import economie
    tarifs = economie.TARIFS
    reference = (tarifs["hotdog_pv"] + tarifs["hotdog_souffle"]) / tarifs["hotdog"]
    for genre, comptoir in magasins.COMPTOIRS.items():
        for article in comptoir["articles"]:
            if not article["tarif"] or not (article["gain_pv"] or article["gain_souffle"]):
                continue
            # ⚠️ Le CAFE est hors concours : il ne se paie pas pour ce qu'il
            # rend tout de suite, mais pour l'effet qui dure (`economie.CAFE`).
            # Le compter ici reviendrait a dire qu'un cafe a 4 $ nourrit mieux
            # qu'un hot-dog : vrai sur le papier, faux dans la partie.
            if article["effet"]:
                continue
            gain = tarifs.get(article["gain_pv"], 0) + tarifs.get(article["gain_souffle"], 0)
            assert gain / tarifs[article["tarif"]] <= reference, \
                f"{genre}/{article['slug']} : meilleur que le kiosque a hot-dogs"


def test_chaque_famille_de_commerce_ouvre_sur_une_piece():
    """Un genre sans interieur, et toutes les portes de cette couleur-la
    ouvriraient sur rien."""
    for genre in devantures.GENRES:
        slug = carte.INTERIEUR_DE_GENRE.get(genre["slug"])
        assert slug in carte.INTERIEURS, f"{genre['slug']} : pas de piece"
    assert carte.INTERIEUR_LOGEMENT in carte.INTERIEURS


def test_les_meubles_restent_dedans():
    """⚠️ Un lit sur un trottoir voudrait dire qu'un plan de piece a ete peint
    sur la ville. Personne ne le verrait avant de tomber dessus en jouant."""
    dedans = set(carte.DEDANS)
    for y, ligne in enumerate(VILLE["sol"]):
        trouve = set(ligne) & dedans
        assert not trouve, f"rangee {y} : {sorted(trouve)} en pleine ville"


def test_toutes_les_portes_de_la_ville_menent_quelque_part():
    """Y compris les nouvelles : un commerce ordinaire qui s'ouvre, un logement."""
    for porte in VILLE["portes"]:
        assert porte["interieur"] in carte.INTERIEURS, porte
        piece = carte.INTERIEURS[porte["interieur"]]
        assert piece["points"], f"{porte['lieu']} ouvre sur une piece vide"


def test_les_commerces_ordinaires_s_ouvrent_pour_de_vrai():
    """⚠️ La moitie du travail des devantures etait perdue : sur cent seize
    enseignes, seize menaient quelque part. Il en faut assez pour qu'on ait
    envie de pousser une porte au hasard — et pas toutes, sinon la ville n'a
    plus de facade, seulement des entrees."""
    # ⚠️ La marque d'une porte ordinaire, c'est son NOM : le lieu garanti, lui,
    # tient son nom de son interieur.
    ordinaires = [p for p in VILLE["portes"] if p.get("nom")]
    assert len(ordinaires) >= 15, f"{len(ordinaires)} portes ordinaires seulement"
    assert len(ordinaires) < len(VILLE["devantures"]), "tout s'ouvre : la rue n'a plus de facade"
    for porte in ordinaires:
        assert porte.get("nom"), f"{porte['lieu']} : une porte sans nom d'enseigne"
        assert VILLE["sol"][porte["y"]][porte["x"]] == "D"


def test_chaque_donneur_de_mission_a_sa_place():
    """⚠️ Bouchard mange au casse-croute, Josee tient le fond du Brouillard :
    leur `ou` nomme un point d'interieur, et ce point doit exister. Sans lui,
    M4 et M5 sont indonnables — et rien d'autre ne le dirait."""
    points = {(slug, p["type"]) for slug, piece in carte.INTERIEURS.items()
              for p in piece["points"]}
    types = {t for _, t in points}
    for personnage in missions.PERSONNAGES:
        ou = personnage["ou"]
        if not ou.startswith("point:"):
            continue
        assert ou[6:] in types, f"{personnage['slug']} se tient sur « {ou} », qui n'existe nulle part"


def test_les_lieux_des_missions_existent():
    """Chaque `lieu` d'objectif est une porte ou un point de la ville."""
    lieux = {p["slug"] for p in VILLE["points_interet"]}
    lieux |= {p["lieu"] for p in VILLE["portes"]}
    for mission in missions.CATALOGUE:
        for objectif in mission["objectifs"]:
            if objectif.get("lieu"):
                assert objectif["lieu"] in lieux, f"{mission['slug']} : « {objectif['lieu']} » introuvable"
    for defi in missions.DEFIS:
        for lieu in defi.get("points", []) + ([defi["lieu"]] if defi.get("lieu") else []):
            assert lieu in lieux, f"{defi['slug']} : « {lieu} » introuvable"


def test_le_casse_croute_et_le_bar_ont_de_quoi_asseoir_leur_donneur():
    """⚠️ Le juge du retour de Martin, applique aux missions : un donneur assis
    devant un mur nu, ce n'est pas une scene. Il faut une table (ou un
    comptoir) a portee de main de son point."""
    for piece_slug, type_point in (("casse_croute", "sergent"), ("bar", "contact")):
        piece = carte.INTERIEURS[piece_slug]
        point = next(p for p in piece["points"] if p["type"] == type_point)
        autour = [piece["sol"][point["y"] + dy][point["x"] + dx]
                  for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
        assert set(autour) & MEUBLES, f"{piece_slug} : {type_point} n'a rien devant lui"


def test_les_gens_des_pieces_existent():
    """Un commis qui n'est pas au catalogue des pietons ne naîtrait jamais."""
    slugs = {p["slug"] for p in pietons.CATALOGUE}
    assert "commis" in slugs, "le commis doit exister pour tenir les comptoirs"
    for slug, piece in carte.INTERIEURS.items():
        for gens in piece["gens"]:
            assert gens["qui"] in carte.QUI_DEDANS, f"{slug} : « {gens['qui']} »"


def test_les_commerces_ont_quelqu_un_derriere_le_comptoir():
    """Une boutique vide a minuit, passe ; une boutique vide tout le temps, non."""
    boutiques = [s for s in carte.INTERIEURS if s.startswith("boutique_")]
    assert boutiques, "aucune piece de commerce ordinaire"
    for slug in boutiques:
        gens = carte.INTERIEURS[slug]["gens"]
        assert any(g["qui"] == "commis" for g in gens), f"{slug} : personne au comptoir"


def test_chaque_piece_dit_quelle_porte_on_pousse():
    """Le bruit de la porte vient de la piece : le bois d'un logement, la
    vitre et la porte metalique d'un commerce. ⚠️ Un logement qui sonne comme un
    depanneur, c'est ce qu'on entendait avant — et le taxi aussi."""
    for slug, piece in carte.INTERIEURS.items():
        assert piece["porte"] in carte.GENRES_DE_PORTE, slug
    for slug in ("logement", "logement_haut", "planque", "hotel_chambre"):
        assert carte.INTERIEURS[slug]["porte"] == "maison", slug
    for slug in ("depanneur", "bar", "boutique_bouffe", "hotel", "terminus"):
        assert carte.INTERIEURS[slug]["porte"] == "commerce", slug
    # Et chaque porte de la ville mene a une piece qui sait ce qu'elle est.
    for porte in VILLE["portes"]:
        assert VILLE["interieurs"][porte["interieur"]]["porte"] in carte.GENRES_DE_PORTE, porte
