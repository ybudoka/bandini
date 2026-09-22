"""L'eau : ce qu'elle coute, et ce qu'elle ne doit jamais rendre possible.

⚠️ Le vrai enjeu de l'eau n'est pas la noyade, c'est le PONT. M8 a bati sa
geographie sur une regle — une rue dont tous les blocs voisins sont de l'eau est
noyee, et le pont fait l'unique exception. Depuis qu'on nage, cette regle ne
tient plus par la collision : elle tient par le SOUFFLE. Ces juges-la refont
donc le calcul sur la carte livree, parce que c'est un calcul et pas un gout —
si quelqu'un elargit le chenal, ralentit la nage ou allonge la barre
d'endurance, c'est ici que ca tombe.
"""

from collections import deque

import pytest

from app import carte, economie, recherche

CARTE = carte.exporter()
SOL = CARTE["sol"]
LARGEUR, HAUTEUR = CARTE["largeur"], CARTE["hauteur"]
ZONES = {z["slug"]: z for z in CARTE["zones"]}

NAGE = recherche.NAGE
SOUFFLE = recherche.VITESSES["endurance"]


def cout_par_tuile(cafe: bool = False) -> float:
    """Ce qu'une tuile d'eau coute de souffle. ⚠️ C'est LE nombre : tout le
    reste de ce fichier en decoule."""
    depense = economie.CAFE["depense"] if cafe else 1.0
    return carte.TUILE_PX / NAGE["vitesse"] * NAGE["souffle_par_image"] * depense


def tuiles_au_plus(cafe: bool = False, surplus: bool = False) -> float:
    """Combien de tuiles d'eau on peut traverser d'une traite, au mieux."""
    barre = SOUFFLE + (economie.SOUFFLE["surplus_max"] if surplus else 0)
    return barre / cout_par_tuile(cafe)


def test_une_tuile_d_eau_coute_ce_que_la_fiche_dit():
    """Le calcul, ecrit une fois, verifie ici — pour que les trois juges qui
    suivent parlent tous du meme nombre."""
    assert cout_par_tuile() == pytest.approx(8.0), cout_par_tuile()
    assert tuiles_au_plus() == pytest.approx(12.5)
    # Cafe (la depense de moitie) ET l'estomac plein : le plafond absolu.
    assert tuiles_au_plus(cafe=True, surplus=True) == pytest.approx(40.0)


def _chenal_du_pont() -> int:
    """La largeur d'eau que le pont enjambe, en tuiles."""
    pont = CARTE["ponts"][0]
    if pont["h"] >= pont["l"]:
        x = pont["x"] + pont["l"] // 2
        haut = pont["y"]
        while haut > 0 and SOL[haut - 1][x] == "~":
            haut -= 1
        bas = pont["y"] + pont["h"]
        while bas < HAUTEUR and SOL[bas][x] == "~":
            bas += 1
        return bas - haut
    y = pont["y"] + pont["h"] // 2
    gauche = pont["x"]
    while gauche > 0 and SOL[y][gauche - 1] == "~":
        gauche -= 1
    droite = pont["x"] + pont["l"]
    while droite < LARGEUR and SOL[y][droite] == "~":
        droite += 1
    return droite - gauche


def _nage_la_plus_courte_vers_la_pointe() -> int:
    """Le plus court passage d'EAU entre La Pointe et le reste de la ville, le
    pont defait — en tuiles, et par l'eau seulement.

    ⚠️ **Ce n'est pas la largeur du chenal sous le tablier, et c'est tout
    l'interet.** Mesure du 17 sept. 2026, le jour ou le chenal est passe a 24
    tuiles (`carte.RANGEES`) : il en mesurait bien 24 sous le pont, et se
    nageait en 11 a son coin nord-ouest, parce que le sable des deux rives s'y
    etait avance — la regle du tiers (`carte.PLAGES`) le permettait enfin. Un
    juge qui lit UNE colonne ne voit pas ca ; celui-ci fait le tour de l'eau.
    """
    sol = [list(ligne) for ligne in SOL]
    pont = CARTE["ponts"][0]
    for y in range(pont["y"], pont["y"] + pont["h"]):
        for x in range(pont["x"], pont["x"] + pont["l"]):
            sol[y][x] = "~"                  # on defait le pont : reste la nage
    # ⚠️ Les îles ne sont pas « le reste de la ville » : ni celle des Corneilles, ni
    # celle de l'aéroport (21 sept. 2026), dont le pont inachevé part justement de
    # La Pointe — sa travée manquante se nage, et c'est voulu (`test_aeroport`).
    iles = (CARTE["ile"], CARTE["aeroport"])

    def dans_l_ile(x: int, y: int) -> bool:
        return any(ile["x"] <= x < ile["x"] + ile["l"] and ile["y"] <= y < ile["y"] + ile["h"]
                   for ile in iles)

    foire = CARTE["foire"]
    depart = (foire["x"] + foire["l"] // 2, foire["y"] + foire["h"] // 2)
    assert sol[depart[1]][depart[0]] != "~", "la foire est a l'eau ?"
    pointe = {depart}
    file = deque([depart])
    while file:                              # la terre de La Pointe, d'un tenant
        x, y = file.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            voisin = (x + dx, y + dy)
            if (voisin in pointe or not (0 <= voisin[0] < LARGEUR and 0 <= voisin[1] < HAUTEUR)
                    or sol[voisin[1]][voisin[0]] == "~"):
                continue
            pointe.add(voisin)
            file.append(voisin)
    dist = {t: 0 for t in pointe}
    file = deque(pointe)
    while file:
        x, y = file.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < LARGEUR and 0 <= ny < HAUTEUR) or (nx, ny) in dist:
                continue
            if sol[ny][nx] != "~":
                if not dans_l_ile(nx, ny):
                    return dist[(x, y)] + 1  # la premiere rive qui n'est pas elle
                continue
            dist[(nx, ny)] = dist[(x, y)] + 1
            file.append((nx, ny))
    raise AssertionError("La Pointe ne voit aucune rive : elle est seule au monde ?")


def test_le_chenal_du_pont_est_un_pari_pas_une_promenade():
    """⚠️ Si l'on nage, La Pointe n'est plus une ile — sauf si la traversee se
    paie. Elle doit coûter assez pour qu'on hesite, et pas assez pour qu'elle
    soit impossible : sinon l'eau redevient un mur, avec une animation en plus.

    ⚠️ **Depuis le 17 sept. 2026, le chenal fait 24 tuiles et le prix a monte
    d'un cran** (demande de Martin : « allonge le pont et eloigne-la du reste de
    la ville »). A jeun, c'est fini : 160 points de souffle sur 100. Avec un
    cafe, ca passe — de justesse. La Pointe se range donc entre la ville, qu'on
    traverse a pied, et l'Ile-aux-Corneilles, qui demande le cafe ET l'estomac
    plein (`test_ile.test_a_la_nage_c_est_un_pari`). Trois crans, trois
    endroits : c'est la geographie qui se lit dans le souffle.

    ⚠️ **Les deux berges sont gratuites depuis le 16 sept. 2026** : la tuile
    d'eau qui touche la terre est de l'eau BASSE, on y a pied (`Monde.eauBasse`).
    Une traversee en paie donc deux de moins, et ce juge compte comme le jeu
    compte — sinon il garde une marge qui n'existe plus.
    """
    nage = _nage_la_plus_courte_vers_la_pointe()
    a_payer = nage - 2
    assert a_payer * cout_par_tuile() > SOUFFLE, (
        f"{nage} tuiles d'eau jusqu'a La Pointe, soit {a_payer * cout_par_tuile():.0f} points "
        f"de souffle sur {SOUFFLE} : on y va a jeun, sur un coup de tete, et le pont ne sert "
        "plus a rien"
    )
    assert a_payer * cout_par_tuile(cafe=True) <= SOUFFLE, (
        f"{nage} tuiles d'eau jusqu'a La Pointe : meme avec un cafe il en coute "
        f"{a_payer * cout_par_tuile(cafe=True):.0f} points sur {SOUFFLE} — l'eau est redevenue "
        "un mur, avec une animation en plus"
    )
    assert a_payer * cout_par_tuile(cafe=True) >= SOUFFLE * 0.6, (
        f"{nage} tuiles d'eau : le cafe en laisse trop — ce n'est plus un pari, c'est une "
        "promenade"
    )


def test_le_tablier_va_d_une_rive_a_l_autre():
    """⚠️ Le pont commence et finit sur la TERRE : un tablier qui s'arrete sur
    l'eau se conduit droit dans la baie, et un tablier qui mord sur le quartier
    est une rue, pas un pont. Le juge le dit en un chiffre — la largeur d'eau
    sous le tablier est exactement sa longueur."""
    pont = CARTE["ponts"][0]
    assert _chenal_du_pont() == pont["h"], (
        f"le tablier fait {pont['h']} tuiles et le chenal {_chenal_du_pont()} : "
        "le pont ne va pas d'une rive a l'autre"
    )


def _loin_de_toute_terre() -> tuple[int, int, int]:
    """La tuile d'eau la plus eloignee de la terre ferme, et sa distance."""
    infini = LARGEUR * HAUTEUR
    dist = [[infini] * LARGEUR for _ in range(HAUTEUR)]
    file: deque = deque()
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            if SOL[y][x] != "~":
                dist[y][x] = 0
                file.append((x, y))
    while file:
        x, y = file.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < LARGEUR and 0 <= ny < HAUTEUR and dist[ny][nx] == infini:
                dist[ny][nx] = dist[y][x] + 1
                file.append((nx, ny))
    return max((dist[y][x], x, y) for y in range(HAUTEUR) for x in range(LARGEUR)
               if SOL[y][x] == "~")


def test_on_ne_va_meme_pas_au_milieu_de_la_baie():
    """⚠️ « On ne traverse pas la baie, quel que soit le cafe bu. »

    Et le juge ne mesure pas une traversee — il n'y a rien de l'autre cote, la
    baie touche le bord de la carte. Il mesure la chose qui compte vraiment :
    le point d'eau le plus loin de toute terre. Si l'on ne peut pas meme
    l'ATTEINDRE, on ne risque pas de traverser quoi que ce soit ; et comme il
    faut revenir, la marge reelle est du double.
    """
    loin, x, y = _loin_de_toute_terre()
    plafond = tuiles_au_plus(cafe=True, surplus=True)
    # ⚠️ La premiere tuile est de l'eau basse, elle ne se paie pas : on compte
    # ce que la traversee coûte VRAIMENT, une tuile de moins.
    assert loin - 1 > plafond * 1.5, (
        f"le large de la baie est a {loin} tuiles de la terre en {(x, y)}, et l'on peut "
        f"en nager {plafond:.0f} : la baie devient un raccourci"
    )


def test_l_eau_ne_relie_aucun_trottoir():
    """⚠️ Les juges de connexite gardent leur sens. `composantes_marchables`
    continue d'ignorer l'eau : il sert a prouver qu'aucun trottoir n'est
    enclave, et si l'eau reliait les rives, il ne dirait plus rien du tout."""
    assert not carte.marchable("~"), "l'eau est devenue marchable : tous les juges de connexite mentent"
    # ⚠️ L'île est un deuxième îlot, et c'est ce juge qui le prouve : si l'eau
    # reliait les rives, la ville et l'île n'en feraient plus qu'un.
    terres = carte.composantes_par_terre(CARTE)
    assert len(terres["ville"]) == 1 and len(terres["ile"]) == 1, {t: len(g) for t, g in terres.items()}


def test_le_bateau_est_le_seul_a_flotter():
    """⚠️ Un char dans l'eau coule, et le bateau non — et c'est sa FICHE qui le
    dit (`eau`, deja la pour sa friction et son adherence), pas une classe
    ecrite dans le JavaScript. Une deuxieme verite a tenir a jour, c'est une
    deuxieme verite qui finit par mentir.

    ⚠️ LES bateaux depuis le 21 sept. 2026 : la chaloupe, le chalutier et le
    porte-conteneurs — et ce sont les seuls de leur classe."""
    from app import vehicules
    flottent = [v["slug"] for v in vehicules.CATALOGUE if v["eau"]]
    assert flottent == ["bateau", "chalutier", "porte_conteneurs"], flottent
    assert flottent == [v["slug"] for v in vehicules.CATALOGUE if v["classe"] == "bateau"]
