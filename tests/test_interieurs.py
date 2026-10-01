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
import villes

from app import armes, carte, devantures, economie, magasins, missions, pietons

#: ⚠️ Au niveau du module, payée à la collecte : les juges se paramètrent par ses pièces. Elle vient de
#: `villes` — la ville gardée du processus, que les autres fichiers reçoivent ensuite sans la régénérer.
VILLE = villes.exporter()

#: ⚠️ TOUTES LES PIECES DE LA VILLE, dessinees et posees. Les juges d'a cote ne
#: lisaient que `carte.INTERIEURS` — le catalogue du module — et depuis que les
#: commerces et les logements se POSENT a la mesure de leur batiment, c'est la
#: moitie la plus nombreuse qui echappait a tout : quarante-sept pieces sur
#: soixante-quatre. Elles passent maintenant les memes juges que les seize
#: dessinees, et sur la ville livree.
PIECES: dict[str, dict] = VILLE["interieurs"]

#: Les pieces POSEES seules (le reste est dessine a la main).
POSEES = {s: p for s, p in PIECES.items() if s not in carte.INTERIEURS}

#: Les meubles : tout ce qui n'est ni plancher, ni mur, ni porte.
MEUBLES = frozenset(g for g, p in carte.LEGENDE.items() if p.get("meuble"))

#: Ce qu'un point peut demander au navigateur. ⚠️ Cette liste est la moitie
#: d'un contrat : l'autre moitie est dans `missions.js` (`LIBELLES` et
#: `menuDuPoint`), et `tests/test_interieurs_js.py` verifie que les deux
#: s'accordent. Un type ajoute ici sans son cas la-bas est un comptoir mort.
TYPES_SERVIS = frozenset({
    "lit", "coffre", "garde_robe", "vendre", "reparer", "repeindre", "acheter",
    "hotdog", "soigner", "caisse", "journal", "casier",
    "fourriere", "emplettes", "salon", "escalier", "fouiller",
    # Les concessionnaires : le comptoir qui vend les chars du lot.
    "concession",
    # L'ascenseur du garage souterrain (`Souterrain.descendreAPied`, docs/jalons/le-grand-garage-souterrain.md).
    "ascenseur",
    # La voûte de la caisse populaire (`Caisse.agir`) : le casse, ou une porte d'acier qui le dit.
    "voute",
    # La planque qu'on décore : le catalogue Beausoleil, sur la table (`Decoration.menuCatalogue`).
    "catalogue",
    # M11, 2e vague — les deux moities du meme choix : effacer une page, sur,
    # cher, une fois par jour (l'avocat) ou payer d'avance et revenir demain
    # sans savoir ce qu'on a achete (le comptoir du fond de La Shop).
    "avocat", "hacker",
    # La machine distributrice d'une salle d'attente : le terminus, le poste,
    # l'urgence. Sa sorte est sur le point, son menu dans `magasins`.
    "distributrice",
    # Le metro : monter dans la rame au quai, en descendre dans la rame
    # (`Metro.utiliser`). Un geste, pas un menu.
    "rame",
    # Le videopoker du Brouillard et du depanneur (`videopoker.py`, `Missions.menuVideopoker`).
    "videopoker",
    # Le comptoir de Mireille au DOJO DION (docs/jalons/le-dojo-du-quartier.md).
    "cours",
    # La machine à sous du casino du Dragon d'or (`machine_a_sous.py`, `Casino.menu`).
    "machine_a_sous",
    # Les tables du Dragon d'or (`tables_de_jeu.py`, `Tables.menu`).
    "blackjack", "roulette", "poker", "sic_bo", "baccara",
    # La barbotte du Pouce, au tripot du sous-sol (`tripot.py`, `Tripot.menu`).
    "barbotte",
})
#: ⚠️ Le point d'un PERSONNAGE posé dedans (`ou: "point:<type>"` — le sergent, Josée, Lulu,
#: Ovila, le Dr Lachance) est servi par `Histoire.personnageDuPoint`, et se lit dans le
#: catalogue : écrit à la main, il avait oublié le docteur.
TYPES_SERVIS = TYPES_SERVIS | {p["ou"][len("point:"):] for p in missions.PERSONNAGES if p["ou"].startswith("point:")}


@pytest.mark.parametrize("slug", sorted(PIECES))
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
    piece = PIECES[slug]
    sortie = piece["apparition"]
    for point in piece["points"]:
        ecart = math.hypot(point["x"] - sortie["x"], point["y"] - sortie["y"])
        assert ecart >= carte.RAYON_POINT, (
            f"{slug} : le point {point['type']} est a {ecart:.2f} tuile de la sortie "
            f"— il volerait ACTION a la porte"
        )


@pytest.mark.parametrize("slug", sorted(PIECES))
def test_une_piece_est_meublee(slug):
    """⚠️ LE juge de la demande de Martin. Une piece de quinze tuiles sur neuf
    avec un comptoir de sept tuiles, c'est 5 % de meubles : on entre, on voit
    du plancher. Un dixieme de la piece, au minimum, doit etre quelque chose —
    et il faut au moins deux SORTES de meubles, sinon c'est le comptoir vide
    d'avant avec un comptoir plus long."""
    piece = PIECES[slug]
    tuiles = "".join(piece["sol"])
    meubles = [g for g in tuiles if g in MEUBLES]
    aire = piece["largeur"] * piece["hauteur"]
    assert len(meubles) >= aire * 0.10, f"{slug} : {len(meubles)} meubles pour {aire} tuiles"
    assert len(set(meubles)) >= 2, f"{slug} : un seul genre de meuble ({set(meubles)})"


@pytest.mark.parametrize("slug", sorted(PIECES))
def test_une_piece_donne_quelque_chose_a_faire(slug):
    """Un comptoir qui ne donne rien est une porte qu'on ouvre pour rien."""
    piece = PIECES[slug]
    assert piece["points"], f"{slug} : aucun point d'action"
    for point in piece["points"]:
        assert point["type"] in TYPES_SERVIS, f"{slug} : « {point['type']} » n'est servi nulle part"


@pytest.mark.parametrize("slug", sorted(PIECES))
def test_une_piece_dit_quel_plancher_elle_a(slug):
    """⚠️ Un meuble ne couvre pas toute sa tuile : le peintre doit savoir quoi
    mettre DESSOUS. Sans `plancher`, chaque table etait un trou noir dans le
    plancher — et rien, cote Python, ne s'en serait apercu."""
    piece = PIECES[slug]
    plancher = piece["plancher"]
    assert carte.solidite(plancher) == 0, f"{slug} : on ne marche pas sur « {plancher} »"
    assert carte.LEGENDE[plancher].get("dedans"), f"{slug} : « {plancher} » n'est pas un plancher"


def test_deux_points_ne_se_marchent_pas_dessus():
    """⚠️ `pointSousLaMain` prend le plus proche dans un rayon d'une tuile et
    demie : deux points colles, et l'un des deux est injoignable a jamais.

    ⚠️ Sauf DEUX ESCALIERS (des etages dedans aussi) : on se tient DESSUS une marche, et c'est elle que
    `pointSousLaMain` prend (`faceA` : dessus) — l'etage du milieu d'une petite piece n'a pas d'autre place
    (`test_etages_js.py` monte et redescend au bouton, depuis chaque marche)."""
    for slug, piece in PIECES.items():
        for i, a in enumerate(piece["points"]):
            for b in piece["points"][i + 1:]:
                ecart = max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"]))
                assez = 1 if a["type"] == b["type"] == "escalier" else 2
                assert ecart >= assez, f"{slug} : {a['type']} et {b['type']} se touchent"


def test_l_escalier_monte_et_redescend():
    """Un escalier qui ne ramene pas est un cul-de-sac : on serait pris en haut
    (la porte du haut sort dehors, mais on ne l'a pas choisie)."""
    escaliers = 0
    for slug, piece in PIECES.items():
        for point in piece["points"]:
            if point["type"] != "escalier":
                continue
            escaliers += 1
            cible = point.get("vers")
            assert cible in PIECES, f"{slug} : l'escalier mene a « {cible} »"
            retours = [q for q in PIECES[cible]["points"]
                       if q["type"] == "escalier" and q.get("vers") == slug]
            assert retours, f"{cible} : aucun escalier ne redescend vers {slug}"
    assert escaliers, "aucun escalier de toute la ville : les plex n'ont plus d'etage"
    assert escaliers, "aucun escalier dans toute la ville : les plex n'ont plus d'etage"


def test_chaque_comptoir_ordinaire_vend_quelque_chose():
    """Un point `emplettes` nomme une famille de commerce ; cette famille doit
    avoir un comptoir, et chaque article doit pointer sur quelque chose."""
    for slug, piece in PIECES.items():
        for point in piece["points"]:
            if point["type"] != "emplettes":
                continue
            genre = point.get("genre")
            assert genre in magasins.COMPTOIRS, f"{slug} : pas de comptoir « {genre} »"


def test_les_articles_des_comptoirs_existent():
    tenues = {t["slug"] for t in magasins.TENUES}
    for genre, comptoir in magasins.COMPTOIRS.items():
        # ⚠️ Un comptoir de BLOC (la cabane à sucre) n'est pas une famille de devantures : il n'y en a qu'un.
        # Ceux des ENSEIGNES non plus (le bingo, le Rialto, les quilles, le lave-auto).
        assert genre in devantures.INDEX_GENRE or comptoir.get("bloc") or comptoir.get("enseigne"), \
            f"comptoir « {genre} » : famille inconnue"
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
            # (Les gains d'un article qui nourrit : `test_reclame::test_un_article_qui_nourrit_a_ses_deux_gains_dans_les_tarifs`.)
            if article["effet"]:
                assert article["effet"] in magasins.EFFETS, article


def test_chaque_famille_de_commerce_sait_se_meubler():
    """Une famille sans mobilier, et toutes les portes de cette couleur-la
    ouvriraient sur rien.

    ⚠️ C'est le contrat qui a remplace « une piece dessinee par famille » : la
    famille dit QUOI meubler (les frigos de l'epicerie, les machines de
    l'atelier), la mesure du batiment dit combien. Un genre de devanture ajoute
    sans sa palette leve ici, pas en jouant.
    """
    for genre in devantures.GENRES:
        fiche = carte.MOBILIER.get(genre["slug"])
        assert fiche, f"{genre['slug']} : pas de mobilier"
        assert fiche["fond"].strip() and fiche["allee"].strip(), f"{genre['slug']} : motifs vides"
        type_, sorte = fiche["point"]
        assert type_ in TYPES_SERVIS, f"{genre['slug']} : « {type_} » n'est servi nulle part"
        if type_ == "emplettes":
            assert sorte in magasins.COMPTOIRS, f"{genre['slug']} : pas de comptoir « {sorte} »"


def test_chaque_famille_de_commerce_ouvre_une_porte():
    """⚠️ Il faut qu'un batiment tire cette enseigne-la, qu'il soit assez grand
    ET qu'il gagne le de : trois chances qui se multiplient, et quatre familles
    sur dix restaient des couleurs d'enseigne qui ne menent jamais a rien
    (`premiere_du_genre`). Le de decide du NOMBRE de portes, pas de l'existence
    d'un pan entier de la ville."""
    ouvertes = {p["lieu"].rsplit("_", 1)[0] for p in VILLE["portes"] if p.get("nom")}
    manquantes = [g["slug"] for g in devantures.GENRES if g["slug"] not in ouvertes]
    assert not manquantes, f"des familles qui n'ouvrent nulle part : {manquantes}"
    assert "logement" in ouvertes, "aucun logement ne s'ouvre dans toute la ville"


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
        assert porte["interieur"] in PIECES, porte
        assert PIECES[porte["interieur"]]["points"], f"{porte['lieu']} ouvre sur une piece vide"


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
    # ⚠️ Les pieces POSEES aussi (`VILLE["interieurs"]`) : le comptoir de Mireille est celui du
    # DOJO DION, une piece de commerce reprise sur la ville finie (`poser_le_dojo`).
    points = {(slug, p["type"]) for slug, piece in {**carte.INTERIEURS, **VILLE["interieurs"]}.items()
              for p in piece["points"]}
    types = {t for _, t in points}
    for personnage in missions.PERSONNAGES:
        ou = personnage["ou"]
        if not ou.startswith("point:"):
            continue
        assert ou[6:] in types, f"{personnage['slug']} se tient sur « {ou} », qui n'existe nulle part"


def test_les_lieux_des_missions_existent():
    """Chaque `lieu` d'objectif est une porte, un point de la ville, ou un mouillage
    (`mouillage:<slug>[:n]`, m52-m54) — de l'eau, sans porte ni point d'intérêt."""
    lieux = {p["slug"] for p in VILLE["points_interet"]}
    lieux |= {p["lieu"] for p in VILLE["portes"]}
    # Un lieu DANS UN BLOC de carte (la villa du maire, l'infiltration) : déclaré par son bloc.
    from app import blocs
    lieux |= set(blocs.lieux_des_blocs())
    mouillages = VILLE["mouillages"]
    for mission in missions.CATALOGUE:
        for objectif in mission["objectifs"]:
            slug = objectif.get("lieu")
            if not slug:
                continue
            if slug.startswith("mouillage:"):
                deux = slug[len("mouillage:"):].split(":")
                n = int(deux[1]) if len(deux) > 1 else 0
                pareils = [m for m in mouillages if m["slug"] == deux[0]]
                assert n < len(pareils), f"{mission['slug']} : « {slug} » introuvable"
                continue
            # Le quai du traversier (m99, M13) : une escale que la ville trace (`traversier.ESCALES`).
            if slug.startswith("traversier:"):
                assert slug[len("traversier:"):] in {q["district"] for q in VILLE["traversier"]["escales"]}, \
                    f"{mission['slug']} : « {slug} » introuvable"
                continue
            # ⚠️ L'amarrage le plus près d'un lieu (`amarrage:<lieu>`, m53 : le relais de la rive nord,
            # `Histoire.amarragePres`) : une forme neuve de fbd00fce (29 sept. 2026), apprise alors à
            # test_missions et test_barrieres mais pas ici — ce juge rougissait sur un lieu valide. Il
            # exige ce que le résolveur exige : un lieu connu, et des amarrages dans la ville.
            if slug.startswith("amarrage:"):
                assert slug[len("amarrage:"):] in lieux and VILLE["amarrages"], \
                    f"{mission['slug']} : « {slug} » introuvable"
                continue
            # Un lieu DE L'ÎLE qu'on rejoint par l'eau (`ile:<lieu>`, i04) — une porte de l'île ; et le quai de la NAVETTE
            # (`navette:<escale>`) : une escale qu'elle trace.
            if slug.startswith("ile:"):
                assert slug[len("ile:"):] in lieux, f"{mission['slug']} : « {slug} » introuvable"
                continue
            if slug.startswith("navette:"):
                assert slug[len("navette:"):] in {q["district"] for q in VILLE["navette"]["escales"]}, \
                    f"{mission['slug']} : « {slug} » introuvable"
                continue
            assert slug in lieux, f"{mission['slug']} : « {slug} » introuvable"
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
    for slug, piece in PIECES.items():
        for gens in piece["gens"]:
            assert gens["qui"] in carte.QUI_DEDANS, f"{slug} : « {gens['qui']} »"


def test_les_commerces_ont_quelqu_un_derriere_le_comptoir():
    """Une boutique vide a minuit, passe ; une boutique vide tout le temps, non."""
    boutiques = [s for s, p in POSEES.items() if p["porte"] == "commerce"]
    assert boutiques, "aucune piece de commerce ordinaire"
    for slug in boutiques:
        gens = PIECES[slug]["gens"]
        # ⚠️ Le DOJO DION n'a pas de commis : c'est Mireille, un personnage, qui tient son
        # comptoir (le point `cours`, docs/jalons/le-dojo-du-quartier.md).
        if any(p["type"] == "cours" for p in PIECES[slug]["points"]):
            continue
        # ⚠️ L'ÉCOLE LA MANTE non plus (`mantes.py`) : ce sont ses élèves qui la tiennent — des Mantes.
        if gens and all(g["qui"] == "mante" for g in gens):
            continue
        assert any(g["qui"] == "commis" for g in gens), f"{slug} : personne au comptoir"


def test_chaque_piece_dit_quelle_porte_on_pousse():
    """Le bruit de la porte vient de la piece : le bois d'un logement, la
    vitre et la porte metalique d'un commerce. ⚠️ Un logement qui sonne comme un
    depanneur, c'est ce qu'on entendait avant — et le taxi aussi."""
    for slug, piece in PIECES.items():
        assert piece["porte"] in carte.GENRES_DE_PORTE, slug
    for slug in ("planque", "hotel_chambre"):
        assert carte.INTERIEURS[slug]["porte"] == "maison", slug
    for slug in ("depanneur", "bar", "hotel", "terminus"):
        assert carte.INTERIEURS[slug]["porte"] == "commerce", slug
    # ⚠️ Et les pieces POSEES le disent aussi : un logement sonne comme une
    # maison, un commerce comme une vitrine. C'est `piece_de_logement` qui le
    # pose, et rien d'autre ne le dirait.
    logements = [s for s, p in POSEES.items() if "logement" in s]
    assert logements, "aucun logement pose dans la ville"
    assert all(POSEES[s]["porte"] == "maison" for s in logements)
    # Et chaque porte de la ville mene a une piece qui sait ce qu'elle est.
    for porte in VILLE["portes"]:
        assert VILLE["interieurs"][porte["interieur"]]["porte"] in carte.GENRES_DE_PORTE, porte


#: Les meubles qui se peignent PAR LEURS VOISINES (`varianteDeBloc`, monde.js) :
#: la fiche dit `bloc`. Retour de Martin (13 sept. 2026) : « les lits doivent
#: vraiment avoir l'air de lits, juste un set d'oreillers et des couvertes ;
#: actuellement c'est 2 ou 4 cases avec chacune leur oreiller » — puis le
#: billard etait huit tabourets, le tapis trois chemins de couloir.
BLOCS = frozenset(g for g, p in carte.LEGENDE.items() if p.get("bloc"))


def _blocs(sol: list[str], g: str):
    """Les composantes 4-connexes du glyphe `g` : (x0, y0, large, haut, tuiles)."""
    tuiles = {(x, y) for y, ligne in enumerate(sol) for x, glyphe in enumerate(ligne) if glyphe == g}
    vus: set[tuple[int, int]] = set()
    for depart in sorted(tuiles):
        if depart in vus:
            continue
        bloc, front = set(), [depart]
        while front:
            x, y = front.pop()
            if (x, y) in bloc:
                continue
            bloc.add((x, y))
            front.extend(v for v in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if v in tuiles)
        vus |= bloc
        xs, ys = [x for x, _ in bloc], [y for _, y in bloc]
        yield min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, bloc


def test_les_blocs_sont_le_lit_la_table_le_tapis_et_la_machine():
    """La liste est courte a dessein : un glyphe `bloc` a un peintre qui lit le
    masque, et un peintre qui l'ignore prendrait le masque pour du bruit.

    ⚠️ La PISCINE (« o ») est la cinquieme, et la premiere qui vit DEHORS :
    quatre tuiles qui font un rond, chacune peignant son quart, le centre du
    cercle du cote de ses voisines. Elle est ici pour la meme raison que les
    quatre autres — son peintre lit le masque — et ce juge est le rappel qu'on
    n'ajoute pas un `bloc` sans lui donner un peintre qui le lise. Peintes
    chacune pour soi, les quatre tuiles montraient quatre carres avec quatre
    margelles : c'est la premiere chose que Martin a vue a l'ecran.

    ⚠️ Le LIT D'HOPITAL (« r ») est le sixieme : une place, la tete au nord, et
    son peintre lit le masque pour ne mettre la tete de lit et l'oreiller qu'a
    la tuile de tete — c'est la que se couche le malade.

    ⚠️ Le FOYER (« Y ») et la PEAU D'OURS (« U ») du chalet du rang (26 sept. 2026) : l'âtre
    court d'une tuile à l'autre (une bûche, une ouverture, pas deux cheminées collées), et la
    bête de deux sur deux peint chacun son quart (une tête, quatre pattes, pas quatre oursons)."""
    # ⚠️ Le TATAMI du DOJO DION (« A ») aussi : son peintre lit le masque pour ne border de noir
    # que les cotes ou le tatami s'arrete, comme le galon du tapis.
    # ⚠️ L'ALLEE DE QUILLES (« [ ») de meme : les quilles au bout nord, les dalots sur ses bords.
    # ⚠️ La TABLE DE JEU du Dragon d'or (« ! ») : la bordure de bois seulement la ou le feutre s'arrete.
    # ⚠️ La PISCINE CREUSEE d'une villa (« ? ») : la margelle seulement au bord (`villas.py`, le jardin).
    assert BLOCS == {"l", "a", "y", "m", "o", "r", "Y", "U", "A", "[", "!", "?"}


@pytest.mark.parametrize("slug", sorted(PIECES))
def test_un_bloc_est_un_rectangle_plein_et_deux_blocs_ne_se_touchent_pas(slug):
    """⚠️ Le corollaire du dessin par les voisines : une tuile `l` qui en touche
    une autre continue le MEME lit — une seule tete, un seul oreiller, une
    couverture d'un tenant. Deux lits colles seraient donc peints comme UN lit
    de quatre de large, et un bloc en L n'aurait ni tete ni bord droit. Un bloc
    est un rectangle plein ; un lit, en plus, fait au plus deux tuiles de cote.

    ⚠️ Il a rougi une fois le jour ou il a ete ecrit : dans la taverne, la table
    de gauche touchait le billard, et les deux faisaient un meuble en L de
    quatre tuiles sur quatre."""
    sol = PIECES[slug]["sol"]
    for g in sorted(BLOCS):
        for x0, y0, large, haut, bloc in _blocs(sol, g):
            nom = carte.LEGENDE[g]["nom"]
            assert len(bloc) == large * haut, f"{slug} : un bloc de {nom} en L en {x0},{y0} — deux {nom}s qui se touchent ?"
            if g == "l":
                assert large <= 2 and haut <= 2, f"{slug} : un lit de {large} × {haut} tuiles en {x0},{y0}"
            if g == "r":
                # Un lit d'hopital est un lit d'UNE place : une tuile sur deux.
                assert (large, haut) == (1, 2), f"{slug} : un lit d'hôpital de {large} × {haut} tuiles en {x0},{y0}"


def test_de_deux_escaliers_qui_se_repondent_un_seul_descend():
    """L'invite dit MONTER ou DESCENDRE selon le `descend` du point (Martin, 29 sept. 2026 : en haut de l'escalier
    du tripot, elle disait MONTER). Deux pièces reliées ont chacune leur marche : une monte, l'autre descend — le
    sous-sol du Dragon d'or, les soins de l'hôpital, la chambre de l'hôtel, l'étage de chaque plex."""
    paires, fautes = 0, []
    for slug, piece in PIECES.items():
        for pt in piece["points"]:
            if pt["type"] != "escalier":
                continue
            retour = [q for q in PIECES[pt["vers"]]["points"] if q["type"] == "escalier" and q.get("vers") == slug]
            if len(retour) != 1 or bool(pt.get("descend")) == bool(retour[0].get("descend")):
                fautes.append((slug, pt["vers"], pt.get("descend"), [q.get("descend") for q in retour]))
            paires += 1
    assert not fautes, fautes[:8]
    assert paires >= 8, paires
    assert any(p.get("descend") for p in PIECES["nord_casino"]["points"] if p["type"] == "escalier")
    assert not any(p.get("descend") for p in PIECES["nord_tripot"]["points"] if p["type"] == "escalier")
