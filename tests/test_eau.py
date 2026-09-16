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


def test_le_chenal_du_pont_est_un_pari_pas_une_promenade():
    """⚠️ Si l'on nage, La Pointe n'est plus une ile — sauf si la traversee se
    paie. Elle doit coûter assez pour qu'on hesite, et pas assez pour qu'elle
    soit impossible : sinon l'eau redevient un mur, avec une animation en plus.

    ⚠️ **Les deux berges sont gratuites depuis le 16 sept. 2026** : la tuile
    d'eau qui touche la terre est de l'eau BASSE, on y a pied (`Monde.eauBasse`).
    Une traversee en paie donc deux de moins — 72 points au lieu de 88 — et ce
    juge doit compter comme le jeu compte, sinon il garde une marge qui n'existe
    plus et le jour ou le chenal s'elargit, il rougit trop tard.
    """
    chenal = _chenal_du_pont()
    prix = (chenal - 2) * cout_par_tuile()
    assert prix <= SOUFFLE, (
        f"le chenal fait {chenal} tuiles, soit {prix:.0f} points de souffle sur {SOUFFLE} : "
        "on ne peut pas le traverser, l'eau est redevenue un mur"
    )
    assert prix >= SOUFFLE * 0.6, (
        f"le chenal ne coûte que {prix:.0f} points sur {SOUFFLE} : ce n'est plus un pari, "
        "c'est une promenade, et le pont ne sert plus a rien"
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
    assert len(carte.composantes_marchables(CARTE)) == 1


def test_le_bateau_est_le_seul_a_flotter():
    """⚠️ Un char dans l'eau coule, et le bateau non — et c'est sa FICHE qui le
    dit (`eau`, deja la pour sa friction et son adherence), pas une classe
    ecrite dans le JavaScript. Une deuxieme verite a tenir a jour, c'est une
    deuxieme verite qui finit par mentir."""
    from app import vehicules
    flottent = [v["slug"] for v in vehicules.CATALOGUE if v["eau"]]
    assert flottent == ["bateau"], flottent
