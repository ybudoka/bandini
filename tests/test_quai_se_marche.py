"""Le quai se marche, et la ville est moins sale.

⚠️ **Mesure d'abord.** Retour de Martin : « il y a trop de saleté partout et
impossible d'aller sur une partie du quai, il est clôturé, sans chemin à
pied ». Les deux étaient vrais, et le second avait TROIS causes empilées :

1. **La barrière du cargo fermait tout un quai.** « Le quai du cargo » est une
   zone conditionnelle (fermée le jour, décor `chaine`) qui prenait la RÉGION
   de quai du contrebandier — et depuis que le quai a avalé la baie, cette
   région faisait **61 × 26 tuiles, eau comprise**. C'est la « clôture » de la
   capture : une chaîne le long du trottoir et en travers du quai.
2. **Deux semis posaient des bornes d'amarrage sur la même lèvre** — le quai
   (écart 6) et la grève (écart 3) — soit une borne ou un pneu tous les trois
   pas. Une borne ARRÊTE un piéton.
3. **La cargaison couvrait tout le tablier** : une soixantaine de caisses
   SOLIDES sur dix rangées de profondeur. **191 tuiles de quai** étaient
   inatteignables à pied.

Et **303 objets de saleté** dans la ville.
"""

from __future__ import annotations

import pytest

from app import carte


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


def atteignables(ville) -> set[tuple[int, int]]:
    """Ce qu'un piéton atteint depuis l'autobus, sans enjamber une clôture, en
    contournant tout le décor SOLIDE (`carte.DECOR_SOLIDE`).

    ⚠️ **Et depuis le quai de l'île** : on y arrive par l'eau, jamais à pied,
    et une planche de son quai n'est pas « enfermée » pour autant — c'est
    l'autre terre ferme, et elle se juge depuis sa chaloupe."""
    sol, L, H = ville["sol"], ville["largeur"], ville["hauteur"]
    bloque = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE}
    departs = [(ville["apparition"]["joueur"]["x"] // 16, ville["apparition"]["joueur"]["y"] // 16)]
    for amarre in ville["ile"]["amarrages"]:
        departs += [n for n in ((amarre["x"] + 1, amarre["y"]), (amarre["x"] - 1, amarre["y"]),
                                (amarre["x"], amarre["y"] + 1), (amarre["x"], amarre["y"] - 1))
                    if sol[n[1]][n[0]] == "Q" and n not in bloque]
    # ⚠️ **Et depuis le bout du pont de l'aéroport** (21 sept. 2026) : on y arrive
    # à la nage, par la travée manquante — ses planches ne sont pas « enfermées »,
    # elles sont de l'autre côté de l'eau.
    pont = ville["aeroport"]["pont"]
    bout = pont["y"] + pont["nord"] + pont["trou"]
    departs += [(x, bout) for x in range(pont["x"], pont["x"] + pont["l"]) if carte.marchable(sol[bout][x])]
    vus, pile = set(departs), list(departs)
    while pile:
        x, y = pile.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (0 <= n[0] < L and 0 <= n[1] < H and n not in vus
                    and carte.marchable(sol[n[1]][n[0]]) and n not in bloque):
                vus.add(n)
                pile.append(n)
    return vus


def test_aucun_quai_ni_terrain_vague_ne_se_referme(ville):
    """⚠️ **LE JUGE QUI MANQUAIT.** Le générateur ne savait pas ce qui arrête un
    piéton — la solidité d'un décor vit dans sa fiche de DESSIN — et il a pu
    murer 191 tuiles de quai sans que rien ne rougisse. Toute tuile libre d'un
    quai, d'une friche ou d'un trottoir se rejoint maintenant à pied depuis
    l'autobus.

    ⚠️ On ne juge PAS le gazon : une cour arrière fermée d'une palissade s'y
    rejoint en ENJAMBANT, et c'est voulu (« le prix d'une clôture »)."""
    sol, L, H = ville["sol"], ville["largeur"], ville["hauteur"]
    bloque = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE}
    vus = atteignables(ville)
    for glyphe, nom in (("Q", "quai"), (";", "friche"), (".", "trottoir")):
        libres = [(x, y) for y in range(H) for x in range(L)
                  if sol[y][x] == glyphe and (x, y) not in bloque]
        enfermees = [t for t in libres if t not in vus]
        assert libres, f"plus une tuile de {nom} dans la ville"
        assert not enfermees, (
            f"{len(enfermees)} tuiles de {nom} enfermées par du décor : {enfermees[:6]}")


def test_la_barriere_du_cargo_ferme_un_mouillage_pas_un_quai(ville):
    """Une zone conditionnelle ferme un ENDROIT — l'enclos où l'on décharge —
    pas tout le port. Et jamais l'apron : on longe le quai par le bord de
    l'eau, cargo ou pas."""
    sol = ville["sol"]
    b = next(b for b in ville["barrieres"] if b["slug"] == "cargo")
    for y in range(b["y"], b["y"] + b["h"]):
        for x in range(b["x"], b["x"] + b["l"]):
            assert sol[y][x] == "Q", (
                f"la chaîne du cargo passe sur « {carte.LEGENDE[sol[y][x]]['nom']} » en {(x, y)}")
    assert b["l"] * b["h"] <= 200, f"le mouillage fait {b['l']} x {b['h']} : c'est un quai entier"
    # Sous la barrière, il reste une rangée de quai qui longe l'eau.
    dessous = [(x, b["y"] + b["h"]) for x in range(b["x"], b["x"] + b["l"])]
    assert all(sol[y][x] == "Q" for x, y in dessous), (
        "la barrière du cargo descend jusqu'au bord : on ne longe plus le quai")


def test_le_quai_se_traverse_meme_barriere_fermee(ville):
    """La barrière ARRÊTE un piéton quand elle est fermée : on la traite comme
    un mur, et le quai qui la porte doit rester d'un seul tenant — tout ce qu'on
    atteignait sur ses planches sans elle, on l'atteint encore avec elle."""
    sol, L, H = ville["sol"], ville["largeur"], ville["hauteur"]
    b = next(b for b in ville["barrieres"] if b["slug"] == "cargo")
    ferme = {(x, y) for y in range(b["y"], b["y"] + b["h"]) for x in range(b["x"], b["x"] + b["l"])}
    solide = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE}

    def planches(depart, bloque):
        vus, pile = {depart}, [depart]
        while pile:
            x, y = pile.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (0 <= n[0] < L and 0 <= n[1] < H and n not in vus
                        and sol[n[1]][n[0]] == "Q" and n not in bloque):
                    vus.add(n)
                    pile.append(n)
        return vus

    # Une planche libre juste sous la barrière : on part de là.
    depart = next((x, b["y"] + b["h"]) for x in range(b["x"], b["x"] + b["l"])
                  if (x, b["y"] + b["h"]) not in solide)
    sans = planches(depart, solide) - ferme
    avec = planches(depart, solide | ferme)
    coupees = sorted(sans - avec)
    assert len(sans) > 100, f"le juge ne part pas d'un quai : {len(sans)} planches"
    assert not coupees, f"la barrière du cargo coupe le quai en deux : {coupees[:6]}"


def test_une_seule_main_amarre_le_quai(ville):
    """⚠️ La grève amarrait AUSSI sur les planches — deux semis, deux écarts, et
    une borne tous les trois pas. Le quai amarre chez lui, et ses bornes
    gardent leur écart."""
    sol = ville["sol"]
    L, H = ville["largeur"], ville["hauteur"]
    bornes = [(d["x"], d["y"]) for d in ville["decor"]
              if d["type"] == "poteau_amarrage" and sol[d["y"]][d["x"]] == "Q"]
    assert bornes, "plus une borne d'amarrage sur le port"
    # ⚠️ L'écart vaut sur UN MÊME QUAI. Deux quais séparés par une darse ont
    # chacun leur lèvre, et deux bornes qui se font face par-dessus six tuiles
    # d'eau ne forment pas une palissade.
    masse: dict[tuple[int, int], int] = {}
    for depart in [(x, y) for y in range(H) for x in range(L) if sol[y][x] == "Q"]:
        if depart in masse:
            continue
        numero = len(set(masse.values()))
        pile = [depart]
        masse[depart] = numero
        while pile:
            x, y = pile.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= n[0] < L and 0 <= n[1] < H and n not in masse and sol[n[1]][n[0]] == "Q":
                    masse[n] = numero
                    pile.append(n)
    for i, (x, y) in enumerate(bornes):
        for px, py in bornes[i + 1:]:
            if masse[(x, y)] != masse[(px, py)]:
                continue
            assert abs(px - x) + abs(py - y) >= carte.ECART_BORNE_AMARRAGE, (
                f"deux bornes d'amarrage à {abs(px - x) + abs(py - y)} pas : ({x}, {y}) et ({px}, {py})")


def test_la_cargaison_laisse_l_apron_libre(ville):
    """L'apron est la bande où l'on travaille : rien de solide ne s'y empile,
    sauf ce qui sert au bateau (la borne d'amarrage)."""
    sol, L, H = ville["sol"], ville["largeur"], ville["hauteur"]
    levre = {(x, y) for y in range(H) for x in range(L) if sol[y][x] == "Q"
             and any(not (0 <= x + dx < L and 0 <= y + dy < H) or sol[y + dy][x + dx] == "~"
                     for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    apron = {(x + i, y + j) for x, y in levre
             for i in range(-carte.QUAI_APRON, carte.QUAI_APRON + 1)
             for j in range(-carte.QUAI_APRON, carte.QUAI_APRON + 1)
             if abs(i) + abs(j) <= carte.QUAI_APRON}
    genants = [(d["type"], d["x"], d["y"]) for d in ville["decor"]
               if (d["x"], d["y"]) in apron and sol[d["y"]][d["x"]] == "Q"
               and d["type"] in carte.DECOR_SOLIDE and d["type"] != "poteau_amarrage"]
    assert not genants, f"de la cargaison sur l'apron : {genants[:6]}"


def test_la_ville_est_moins_sale(ville):
    """303 objets de saleté, c'était « trop de saleté partout ». Le plafond est
    celui que Martin a accepté à l'œil, pas un chiffre rond.

    ⚠️ **Il se mesure par MILLE TUILES, pas en objets** (17 sept. 2026). « Trop
    de saleté partout » parle de ce qu'on voit à l'écran, donc d'une densité :
    un plafond en objets se fait rougir par une ville qui grandit, et il l'a été
    le jour où le port a gagné une rangée de blocs profonds — 209 objets pour
    200 permis, alors que la densité n'avait pas bougé (3,2 pour mille, puis
    3,5). Les 303 du départ faisaient 5,1 pour mille ; les 192 acceptés à l'œil,
    3,2."""
    sale = {"debris", "ordures", "pneu", "baril", "caisse"}
    n = sum(1 for d in ville["decor"] if d["type"] in sale)
    marchables = sum(1 for ligne in ville["sol"] for g in ligne if carte.marchable(g))
    pour_mille = 1000 * n / marchables
    assert 1.0 <= pour_mille <= 4.0, (
        f"{n} objets de saleté sur {marchables} tuiles marchables — {pour_mille:.1f} pour mille")
    assert carte.PART_DECHET >= 10, "un terrain vague plus chargé qu'une sur dix"


def test_le_decor_solide_dit_ce_que_disent_les_fiches(banc, paquet):
    """⚠️ **Deux vérités, donc un juge** — même parade que `FLOTTANTS`. La
    solidité vit dans la fiche de dessin ; le générateur en a besoin pour ne
    rien murer. La liste Python doit couvrir EXACTEMENT les décors solides que
    le générateur pose, sinon `degager_le_decor` croira qu'on passe là où l'on
    ne passe pas."""
    r = banc("""function (L, o) {
        return Object.keys(L.DECORS).filter(function (k) { return !!L.DECORS[k].solide; }).sort();
    }""")
    poses = {d["type"] for d in paquet["carte"]["decor"]}
    attendu = sorted(t for t in r if t in poses)
    assert paquet["carte"]["decor_solide"] == sorted(carte.DECOR_SOLIDE)
    assert sorted(carte.DECOR_SOLIDE & poses) == attendu, (
        "le générateur et le dessin ne s'entendent pas sur ce qui arrête un piéton : "
        f"en trop {sorted((carte.DECOR_SOLIDE & poses) - set(attendu))}, "
        f"manquants {sorted(set(attendu) - carte.DECOR_SOLIDE)}")
