"""L'Île-aux-Corneilles : la ville a une île, et elle ne le savait pas.

Demande de Martin (15 sept. 2026) : « tu peux extensionner la carte au besoin ».

⚠️ **Mesuré d'abord : on n'agrandit rien.** La carte fait 419 × 211 tuiles et
23 % en sont de l'eau ; la baie seule est un rectangle d'eau pleine de 117 × 93
qui ne sert qu'à se noyer. L'île se pose DEDANS : la carte garde sa taille, sa
trame, ses rues et tous ses juges de géométrie.

⚠️ **Une île se DESSINE, elle ne se génère pas** — comme une pièce
(`carte._piece`) et pour la même raison : c'est un lieu, pas un quartier de
plus. Les missions de l'arc I (M16) y écriront la cloche de Sœur Jeanne, le
hangar de Sven et la cache sous la chapelle ; elles ont besoin que la chapelle
soit à la même place d'une graine à l'autre. Le plan ci-dessous est la vérité,
et `poser` le recopie tuile pour tuile.

⚠️ **Posée APRÈS le filet**, et c'est ce qui la laisse exister :
`boucher_les_poches` bouche toute terre qu'on ne rejoint pas à pied depuis le
terminus. Une île, par définition, ne se rejoint pas à pied — posée avant, il
la noyait en entier sans rien dire.

⚠️ **Elle ne déplace rien de la ville.** Posée après le dictionnaire de la
ville, sans un seul tirage d'un dé : les amarrages, les zones, la grève et les
plages sont déjà calculés, et ceux qu'elle ajoute s'ajoutent au bout. Les
chantiers, les lignes d'autobus et le mobilier viennent APRÈS elle et n'ont
rien à y faire (pas une rue, pas un bâtiment démolissable). Un juge bâtit la
ville avec et sans l'île, et compare.

⚠️ **Loin, pas fermée.** Trente tuiles d'eau jusqu'à la rive la plus proche :
28 à payer (la première et la dernière sont de l'eau basse), 224 points de
souffle, 112 avec un café. On n'y va donc pas à la nage sur un coup de tête —
il faut le café ET l'estomac plein (160 points). C'est la barrière la plus
honnête du jeu : elle n'est pas fermée, elle est loin. Et la chaloupe qui
mouille au quai de l'île est le chemin du retour.

⚠️ **Pas de police** (`refuge`), et c'est la seule idée mécanique de la fiche :
aucun agent n'y naît, l'hélico s'en va, les étoiles y descendent et n'y montent
pas. Le reste — Roy qui finit par le savoir (M11), le char qu'on y laisse
refroidir (i04) — vient avec les missions.
"""

from __future__ import annotations

from . import carte

#: La fiche de l'île. ⚠️ `x`, `y` : le coin nord-ouest du PLAN en tuiles de
#: ville. Choisi par la mesure, pas au jugé : c'est la place qui met la terre de
#: l'île à trente tuiles d'eau de la rive la plus proche (le pari de la nage)
#: tout en laissant le large à plus de soixante tuiles de toute terre
#: (`test_eau.test_on_ne_va_meme_pas_au_milieu_de_la_baie`).
ILE: dict = {
    "slug": "ile",
    "nom": "L'Île-aux-Corneilles",
    "x": 203,
    "y": 139,
    # ⚠️ De l'eau tout autour, sur au moins tant de tuiles : sinon la levée de
    # sable d'une rive frôle celle de l'île, et « loin » redevient « à côté ».
    "ceinture": 4,
    # Trente habitants l'hiver : trois passants à la fois, et presque personne
    # la nuit. Aucun char n'y roule (il n'y a pas une rue), aucune police.
    "pietons": 3,
    "vehicules": 0,
    "police": 0,
    "rythme": (0.15, 0.7, 0.5),
}

#: ⚠️ LE PLAN. Une rangée de texte par rangée de tuiles, le nord en haut.
#:
#: Le sol : `~` eau, `s` sable, `,` herbe, `;` friche, `g` sentier, `Q` quai,
#: `.` dalle, `w` palissade de bois.
#: Le décor posé dessus (`DECORS`) : `A` arbre, `b` buisson, `p` poteau
#: d'amarrage, `k` caisse, `r` baril, `n` pneu, `L` corde à linge, `l`
#: lampadaire.
#: `m` : une tuile d'eau où une chaloupe attend (`amarrages`).
#: Les bâtiments (`BATIMENTS`) : une lettre ou un chiffre par bâtiment, et `D`
#: sous sa façade là où est sa porte — la fiche dit quelle porte c'est.
#:
#: Au nord-ouest, le quai et sa jetée, face au port du Faubourg ; au milieu, la
#: chapelle et son couvent, le petit cimetière dans sa palissade ; le long du
#: grand chemin, six maisons ; au sud-ouest, l'usine à poisson fermée depuis
#: quinze ans et sa vieille jetée ; à l'est, au bout du chemin, le hangar sans
#: nom.
PLAN: tuple[str, ...] = (
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~~~~,,,,,,,,,,,~~~~~~~~~~~~~~~~~~~",
    "~~~~~QQ~~~~~~~~~,,,,,,,,,,,,,,,~~~~~~~~~~~~~~~~~",
    "~~~~pQQ~~~~~,,,,,,,,,,,,,,,,,,,~~~~~~~~~~~~~~~~~",
    "~~~~~QQ~~,,,,,,,,,A,CCCCCCC,A,,,,~~~~~~~~~~~~~~~",
    "~~~~~QQ~,,,,b,,,,b,,CCCCCCC,,,,,,,,,,,~~~~~~~~~~",
    "~~~~mQQ,,,,,,,,,,,,,CCCCCCC,,VVVVVVVV,,,~~~~~~~~",
    "~~~~~QQ,,,,,,,b,b,,,CCCCCCC,,VVVVVVVV,,,,,~~~~~~",
    "~~~~~QQ,,,,A,,,,,,,,CCCCCCC,,VVVVVVVV,,,,,,~~~~~",
    "~~~~QQQQQl,,b,,.,b,,CCCDCCC,,VVVDVVVV,,,,,,,~~~~",
    "~~~~QQQkQQ,,,,,g,,,....g........g.....,,,,,,~~~~",
    "~~~~QQQQQQggggggggggggggggggggggggggggggggg,,~~~",
    "~~~~QQQQkQ,g,,,,,,,,,,,,,,,,,,,,,,,,,,gHHHHHH,~~",
    "~~~~~,,,,,,g,,,,,,,,,,,,,,,,,,,,,,,,,,gHHHHHH,~~",
    "~~~~~,,,,,,g,11111,,,,,22222,,,,33333,gHHHHHH,~~",
    "~~~~~,,,,,,g,11111L,,,,22222L,,,33333LgHHDHHH,,~",
    "~~~~~,,,A,,g,11D11,,,,,22D22,,,,33D33,gggg,,,,~~",
    "~~~~~,,,,,,g,,,g,,,,,,,,,g,,,,,,,,g,,,g,,,,,,,~~",
    "~~~~~,,,,,ggggggggggggggggggggggggggggg,,,,,,~~~",
    "~~~~~UUUUUUUg,,,,,,,,g,,,,,,,,,g,,,,,,,,,,,,~~~~",
    "~~~~~UUUUUUUg66666,,,g,44444,,,g,55555,,,,,~~~~~",
    "~~~~~UUUUUUUg66D66,L,g,44D44L,,g,55D55,,,~~~~~~~",
    "~~~~~UUUDUUUg,,g,,,,,g,,,g,,,,,g,,,g,,~~~~~~~~~~",
    "~~~~~;;;;;n;g,,g,,,ggggggggggggggg,g,~~~~~~~~~~~",
    "~~~~~;r;;;;rg,,,,,,,,,,,,,,,,,,,,,,~~~~~~~~~~~~~",
    "~~~~~~~QQQ,,,,,,,,,,,,,,,,,,,,,,,,~~~~~~~~~~~~~~",
    "~~~~~~~QQQ~~,,,,,,~~~~,,,,,~~~~~~~~~~~~~~~~~~~~~",
    "~~~~~~~QQQm~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
)

#: Les glyphes du plan qui sont du sol tel quel.
SOLS = frozenset("~s,;gQ.w")

#: Les glyphes du plan qui posent un décor, et le sol qu'il y a dessous.
DECORS: dict[str, tuple[str, str]] = {
    "A": (",", "arbre"),
    "b": (",", "buisson"),
    "p": ("Q", "poteau_amarrage"),
    "k": ("Q", "caisse"),
    "r": (";", "baril"),
    "n": (";", "pneu"),
    "L": (",", "corde_a_linge"),
    "l": ("Q", "lampadaire"),
}

#: Là où une chaloupe attend. ⚠️ HORS du plafond de la ville (`AMARRAGES`) : les
#: dix-huit places de la baie sont prises, et une île sans bateau à quai est
#: une île d'où l'on revient à la nage — le pari une deuxième fois, sans café.
AMARRE = "m"

#: La porte d'un bâtiment, sous sa façade.
PORTE = "D"

#: Les bâtiments, par leur lettre au plan.
#:
#: `toit`    la couverture (`carte.LEGENDE`) : l'ardoise de la chapelle et du
#:           couvent, la tôle de l'usine et du hangar, deux versants aux maisons ;
#: `porte`   `lieu` (on entre, et c'est un repère de la carte), `visite` (on
#:           entre, sans repère), `peinte` (une porte fermée, peinte sur la
#:           façade comme celle d'un logement) ou `condamnee` ;
#: `etages`  pour une porte peinte : combien d'étages de fenêtres on lit ;
#: `clocher` la tuile de toit (relative au bâtiment) où se dresse le clocher.
#:
#: ⚠️ L'usine est CONDAMNÉE, et le hangar s'ouvre sans rien promettre : le
#: premier est fermé depuis quinze ans, le second n'a pas de nom sur la porte.
BATIMENTS: dict[str, dict] = {
    "C": {"toit": "E", "porte": "lieu", "slug": "chapelle", "nom": "Chapelle Sainte-Anne",
          "interieur": "chapelle", "famille": "repere", "clocher": (3, 3)},
    "V": {"toit": "E", "porte": "peinte", "etages": 2},
    "U": {"toit": "B", "porte": "condamnee"},
    "H": {"toit": "B", "porte": "visite", "slug": "hangar_ile", "nom": "Le hangar sans nom",
          "interieur": "hangar_ile"},
    "1": {"toit": "P", "porte": "peinte", "etages": 1},
    "2": {"toit": "P", "porte": "peinte", "etages": 2},
    "3": {"toit": "P", "porte": "peinte", "etages": 1},
    "4": {"toit": "P", "porte": "peinte", "etages": 1},
    "5": {"toit": "P", "porte": "peinte", "etages": 1},
    "6": {"toit": "P", "porte": "peinte", "etages": 1},
}

#: Les pièces de l'île. ⚠️ À la mesure de leur bâtiment, murs compris : la
#: chapelle fait 7 × 6 dehors, donc 9 × 8 dedans ; le hangar 6 × 4, donc 8 × 6
#: (`test_carte.test_la_piece_a_les_mesures_de_son_batiment`).
PIECES: dict[str, dict] = {
    # La chapelle : l'autel au fond, deux rangées de bancs, l'allée au milieu.
    # Le tronc des pauvres est sur l'autel — et on peut le fouiller.
    "chapelle": carte._piece("chapelle", "Chapelle Sainte-Anne", porte="maison", plan="""
BBBWBWBBB
B  ccc  B
Bn     nB
B       B
Bhhh hhhB
B       B
Bhhh hhhB
BBBBDBBBB
""", points=(carte._pt("fouiller", 4, 1),)),
    # Le hangar sans nom : un moteur sur un banc, des étagères, un établi, un
    # classeur. Personne n'y range de filets.
    "hangar_ile": carte._piece("hangar_ile", "Le hangar sans nom", sol="u", porte="maison", plan="""
BBBBBBBB
Bmm  eeB
Bmm    B
B  aa kB
Bn aa  B
BBBBBDBB
""", points=(carte._pt("fouiller", 5, 1),)),
}


def boite() -> tuple[int, int, int, int]:
    """Le rectangle du plan, en tuiles de ville : x, y, largeur, hauteur."""
    return ILE["x"], ILE["y"], len(PLAN[0]), len(PLAN)


def _batiments() -> dict[str, set[tuple[int, int]]]:
    """Les tuiles de chaque bâtiment, relatives au plan, portes comprises."""
    tuiles: dict[str, set[tuple[int, int]]] = {}
    for y, ligne in enumerate(PLAN):
        for x, glyphe in enumerate(ligne):
            if glyphe in BATIMENTS:
                tuiles.setdefault(glyphe, set()).add((x, y))
    for y, ligne in enumerate(PLAN):
        for x, glyphe in enumerate(ligne):
            if glyphe == PORTE:
                tuiles[PLAN[y - 1][x]].add((x, y))
    return tuiles


def _verifier_le_plan() -> None:
    """Le plan se juge au chargement du module, comme une pièce.

    ⚠️ Un glyphe inconnu, une rangée trop courte, une porte qui n'est sous
    aucun bâtiment ou un bâtiment qui n'en a pas : ça lève ICI, avant le premier
    test — le plan est écrit à la main, et une faute de frappe ne doit pas
    attendre qu'on la croise en jouant.
    """
    largeur = len(PLAN[0])
    connus = SOLS | set(DECORS) | set(BATIMENTS) | {AMARRE, PORTE}
    for y, ligne in enumerate(PLAN):
        if len(ligne) != largeur:
            raise ValueError(f"île : la rangée {y} fait {len(ligne)} tuiles au lieu de {largeur}")
        inconnus = set(ligne) - connus
        if inconnus:
            raise ValueError(f"île : glyphes inconnus {sorted(inconnus)} rangée {y}")
    for x, glyphe in enumerate(PLAN[0] + PLAN[-1]):
        if glyphe != "~":
            raise ValueError("île : de la terre sur le pourtour du plan")
    for ligne in PLAN:
        if ligne[0] != "~" or ligne[-1] != "~":
            raise ValueError("île : de la terre sur le pourtour du plan")
    for y, ligne in enumerate(PLAN):
        for x, glyphe in enumerate(ligne):
            if glyphe == PORTE and PLAN[y - 1][x] not in BATIMENTS:
                raise ValueError(f"île : une porte en {(x, y)} sous aucun bâtiment")
    for lettre, tuiles in _batiments().items():
        xs = [t[0] for t in tuiles]
        ys = [t[1] for t in tuiles]
        if len(tuiles) != (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1):
            raise ValueError(f"île : le bâtiment {lettre} n'est pas un rectangle")
        portes = [t for t in tuiles if PLAN[t[1]][t[0]] == PORTE]
        if len(portes) != 1 or portes[0][1] != max(ys):
            raise ValueError(f"île : le bâtiment {lettre} doit avoir une porte, sous sa façade")
        fiche = BATIMENTS[lettre]
        if fiche["porte"] in ("lieu", "visite") and fiche["interieur"] not in PIECES:
            raise ValueError(f"île : le bâtiment {lettre} ouvre sur une pièce qui n'existe pas")


_verifier_le_plan()


def zone() -> dict:
    """La zone de l'île, comme celles des districts — et `refuge` en plus.

    ⚠️ `district: "ile"` et pas un des cinq : c'est lui que lit la musique
    (`musique.AMBIANCES_DE_DISTRICT`) et le choix des passants. ⚠️ La zone doit
    être la DERNIÈRE de la liste : `Monde.zoneA` garde la dernière qui contient
    le point, et le rectangle de l'île est dans celui de la baie.
    """
    x, y, largeur, hauteur = boite()
    return {"slug": ILE["slug"], "nom": ILE["nom"], "district": ILE["slug"],
            "x": x, "y": y, "l": largeur, "h": hauteur,
            "gang": None, "brume": False, "pietons": ILE["pietons"],
            "vehicules": ILE["vehicules"], "police": ILE["police"],
            "rythme": list(ILE["rythme"]), "rares": [], "refuge": True}


def poser(chantier, ville: dict) -> dict:
    """Pose l'île dans la ville déjà bâtie. Rend sa fiche pour le paquet.

    ⚠️ Lève ValueError si la place n'est plus de l'eau, ceinture comprise : le
    jour où une rive avance dans la baie, on le sait à la construction — pas en
    voyant un quai sortir d'une plage.
    """
    x0, y0, largeur, hauteur = boite()
    marge = ILE["ceinture"]
    for y in range(y0 - marge, y0 + hauteur + marge):
        for x in range(x0 - marge, x0 + largeur + marge):
            if not (0 <= x < chantier.largeur and 0 <= y < chantier.hauteur) or chantier.sol[y][x] != "~":
                raise ValueError(f"île : la place n'est plus de l'eau en {(x, y)}")

    # Le sol d'abord : décors, amarres et portes posent sur ce qu'on y lit.
    amarrages = []
    for j, ligne in enumerate(PLAN):
        for i, glyphe in enumerate(ligne):
            x, y = x0 + i, y0 + j
            if glyphe in SOLS:
                chantier.sol[y][x] = glyphe
            elif glyphe in DECORS:
                chantier.sol[y][x] = DECORS[glyphe][0]
            elif glyphe == AMARRE:
                chantier.sol[y][x] = "~"
                amarrages.append({"x": x, "y": y})

    tuiles = _batiments()
    lampes_avant = len(chantier.lampes)
    for lettre in sorted(tuiles):
        _batir(chantier, lettre, tuiles[lettre])

    for j, ligne in enumerate(PLAN):
        for i, glyphe in enumerate(ligne):
            if glyphe in DECORS:
                if not chantier.poser_decor(DECORS[glyphe][1], x0 + i, y0 + j):
                    raise ValueError(f"île : le décor {glyphe} ne se pose pas en {(i, j)}")
                if DECORS[glyphe][1] == "lampadaire":
                    chantier.lampes.append({"x": x0 + i, "y": y0 + j})

    # ⚠️ La ville et le chantier partagent leurs LISTES (le décor, les portes,
    # les lampes) : c'est ce qui fait que ce qu'on pose ici arrive dans le
    # paquet. Une méthode du chantier qui en RÉASSIGNE une au lieu de l'allonger
    # (`degager_le_devant` le fait pour le décor) détacherait la ville, et tout
    # le décor posé ensuite — l'île, les abribus, les arbres de rue — partirait
    # dans une liste que plus personne ne lit. Mesuré : 337 décors perdus.
    if ville["decor"] is not chantier.decor:
        raise ValueError("île : le décor du chantier n'est plus celui de la ville")
    for rangee in range(y0, y0 + hauteur):
        ville["sol"][rangee] = "".join(chantier.sol[rangee])
    ville["interieurs"].update(PIECES)
    ville["amarrages"].extend(amarrages)
    ville["zones"].append(zone())
    return {"slug": ILE["slug"], "nom": ILE["nom"], "x": x0, "y": y0, "l": largeur, "h": hauteur,
            "amarrages": amarrages, "lampes": len(chantier.lampes) - lampes_avant}


def _batir(chantier, lettre: str, relatives: set[tuple[int, int]]) -> None:
    """Un bâtiment de l'île : son toit, sa façade, sa porte.

    ⚠️ La même règle que `carte._Chantier.batiment_forme` — une tuile dont la
    voisine du sud n'est pas au bâtiment est une façade —, mais SANS UN DÉ : la
    couverture est celle de la fiche, et rien n'est tiré. ⚠️ Et le bâtiment
    n'entre PAS dans `chantier.batiments` : c'est la liste où les chantiers
    choisissent quoi démolir, et on ne démolit pas la chapelle d'une île où
    aucune grue ne débarque.
    """
    fiche = BATIMENTS[lettre]
    x0, y0 = ILE["x"], ILE["y"]
    tuiles = {(x0 + x, y0 + y) for x, y in relatives}
    facades = []
    for tx, ty in sorted(tuiles):
        if (tx, ty + 1) in tuiles:
            chantier.sol[ty][tx] = fiche["toit"]
        else:
            chantier.sol[ty][tx] = "F"
            facades.append((tx, ty))
    px, py = next((x0 + x, y0 + y) for x, y in relatives if PLAN[y][x] == PORTE)
    gauche = min(t[0] for t in facades)
    large = max(t[0] for t in facades) - gauche + 1

    if fiche.get("clocher"):
        cx, cy = fiche["clocher"]
        bx, by = min(t[0] for t in tuiles), min(t[1] for t in tuiles)
        chantier.toits.append({"x": bx + cx, "y": by + cy, "type": "clocher"})

    genre = fiche["porte"]
    if genre in ("lieu", "visite"):
        chantier.sol[py][px] = "D"
        porte = {"x": px, "y": py, "interieur": fiche["interieur"], "lieu": fiche["slug"],
                 "vitrine": [gauche, large]}
        if genre == "visite":
            # ⚠️ Le NOM voyage sur la porte, comme celui d'un commerce ordinaire :
            # sans repère sur la carte, c'est le seul endroit où il se lit.
            porte["nom"] = fiche["nom"]
        else:
            chantier.points.append({"type": fiche["slug"], "slug": fiche["slug"], "nom": fiche["nom"],
                                    "x": px, "y": py + 1, "famille": fiche["famille"]})
            # La porte de la chapelle est éclairée : c'est la seule lumière de l'île
            # qu'on voit du large, la nuit.
            chantier.lampes.append({"x": px, "y": py + 1, "r": 30, "c": "fenetre"})
        chantier.portes.append(porte)
        _reserver_le_devant(chantier, px, py)
    elif genre == "condamnee":
        chantier.sol[py][px] = "d"
        _reserver_le_devant(chantier, px, py)
    else:
        _poser_residence(chantier, facades, px, py, fiche["etages"])


def _reserver_le_devant(chantier, px: int, py: int, peinte: bool = False) -> None:
    """Les deux tuiles devant une porte : rien ne s'y pose.

    ⚠️ PAS `carte._Chantier.degager_le_devant` : il dégage aussi le décor déjà
    posé en RÉASSIGNANT la liste, et la ville, bâtie avant l'île, garde l'ancienne
    (voir `poser`). Sur l'île, il n'y a rien à dégager — le décor se pose APRÈS
    les portes, et `poser_decor` refuse une tuile réservée.
    """
    for j in (1, 2):
        chantier.reserve.add((px, py + j))
        if peinte:
            chantier.devants_peints.add((px, py + j))


def _poser_residence(chantier, facades: list[tuple[int, int]], px: int, py: int, etages: int) -> None:
    """Des fenêtres et une porte peinte : une maison où l'on habite.

    ⚠️ La couche peinte de `carte._Chantier.poser_residence`, sans son dé : la
    couleur du mur se lit à la position (toujours la même d'une graine à
    l'autre), et on n'accroche pas d'escalier de fer à une maison de pêcheur.
    """
    from . import devantures

    gauche = min(t[0] for t in facades)
    dispo = max(t[0] for t in facades) - gauche + 1
    large = min(4, dispo)
    x0 = min(max(px - large // 2, gauche), gauche + dispo - large)
    motifs = "".join("P" if x0 + i == px else chantier.sol[py][x0 + i] for i in range(large))
    chantier.portes_peintes.add((px, py))
    _reserver_le_devant(chantier, px, py, peinte=True)
    chantier.residences.append({
        "x": x0, "y": py, "l": large, "etages": etages, "motifs": motifs,
        "escalier": 0, "porte": px - x0,
        "mur": (px * 7 + py * 3) % len(devantures.MURS),
        "balcon": 0,
    })
    for i in range(large):
        chantier.murs_tagges.add((x0 + i, py))
