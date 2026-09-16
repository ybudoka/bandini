"""Le port touche enfin l'eau.

⚠️ **Mesure d'abord**, et c'est elle qui donne raison à Martin (« c'est le
quai ?! je ne savais même pas que c'était un quai — **il y a une route entre le
quai et l'eau** ») : **16 des 1 818 tuiles de quai touchaient l'eau, soit
0,9 %**. La coupe du port, du nord au sud, donnait un boulevard, dix tuiles de
planches, **un deuxième boulevard à quatre voies**, une plage de sable, puis la
baie. Un débardeur traversait une autoroute et une plage pour rejoindre son
cargo.

⚠️ Et la cause n'était pas dans le semis, elle était dans la **trame** : la
rangée de quai et la rangée d'eau étaient deux blocs, et la trame met une rue
entre deux blocs. Le chiffre dormait dans `docs/plan.md` depuis la 1re vague du
bord de l'eau ; on avait corrigé le semis des poteaux d'amarrage au lieu de la
géographie.
"""

from __future__ import annotations

import pytest

from app import carte

#: Ce qui n'a RIEN à faire entre un quai et sa baie.
ENTRE_DEUX_INTERDIT = {"route", "trottoir", "abord"}


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


@pytest.fixture(scope="module")
def quais(ville):
    """La boîte du district des Quais — celui que Martin a montré."""
    return next(z for z in ville["zones"] if z.get("district") and z["slug"] == "quais")


def test_la_fiche_du_port_se_tient():
    """⚠️ `j` est de l'eau POUR LA TRAME, et c'est ce qui efface la rue : une rue
    qui ne longe que des blocs `j` est soit dans la baie, soit en travers du
    port. Sans cette ligne, la rangée avalée aurait gardé son boulevard."""
    assert "j" in carte.EAUX, "un quai sur l'eau doit noyer les rues qui le longent"
    assert "j" in carte.QUAIS and "q" in carte.QUAIS
    assert carte.QUAI_TABLIER >= 6, "un tablier de moins de six tuiles n'est pas un quai"
    assert carte.QUAI_TIRANT_MIN >= 3, "pas assez d'eau devant pour qu'un bateau approche"
    # ⚠️ Et le plan le DIT : la rangée d'eau des Quais est avalée par la rangée
    # de quai. C'est de là que tout vient ; un juge qui ne lirait que le sol
    # rendrait le jour où quelqu'un remet deux blocs séparés.
    plan = next(d["plan"] for d in carte.DISTRICTS if d["slug"] == "quais")
    assert any("j" in ligne for ligne in plan), "les Quais n'ont plus de quai sur l'eau"
    rangee = next(i for i, ligne in enumerate(plan) if "j" in ligne)
    assert set(plan[rangee + 1]) <= {"^", "<"}, (
        "la rangée sous le quai n'est pas avalée : la trame y remettra une rue")


def test_rien_entre_le_quai_et_la_baie(ville, quais):
    """⚠️ **LE DÉFAUT QUE MARTIN A VU**, et le juge le dit dans ses termes : en
    descendant depuis n'importe quelle planche du port, la première tuile qui
    n'est pas du quai est de l'eau. Pas une chaussée, pas un trottoir, pas une
    plage."""
    sol, hauteur = ville["sol"], ville["hauteur"]
    y0, y1 = quais["y"], quais["y"] + quais["h"]
    planches = 0
    for x in range(quais["x"], quais["x"] + quais["l"]):
        for y in range(y0, y1):
            if sol[y][x] != "Q":
                continue
            planches += 1
            for cy in range(y + 1, y1 + 1):
                if cy >= hauteur:
                    break                       # le large : le quai borde le monde
                glyphe = sol[cy][x]
                if glyphe == "Q":
                    continue
                assert glyphe == "~", (
                    f"en descendant du quai en ({x}, {y}) on tombe sur "
                    f"« {carte.LEGENDE[glyphe]['nom']} » en ({x}, {cy}) avant l'eau")
                break
    assert planches > 500, f"presque plus de quai dans les Quais : {planches} tuiles"


def test_le_quai_a_le_pied_dans_l_eau(ville):
    """Le chiffre de la mesure, retourné en garantie : **0,9 % des planches
    touchaient l'eau**. Une tuile de quai sur dix, au moins, doit être une
    LÈVRE — c'est là qu'on amarre, c'est là qu'on décharge, et c'est tout ce
    qu'un quai est censé faire."""
    sol, L, H = ville["sol"], ville["largeur"], ville["hauteur"]
    planches = [(x, y) for y in range(H) for x in range(L) if sol[y][x] == "Q"]
    levre = [(x, y) for x, y in planches
             if any(not (0 <= x + dx < L and 0 <= y + dy < H) or sol[y + dy][x + dx] == "~"
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    part = len(levre) / len(planches)
    assert part >= 0.10, f"seulement {part:.1%} du quai touche l'eau ({len(levre)} tuiles)"


def test_plus_de_plage_au_port(ville, quais):
    """Une plage de sable entre un boulevard et un cargo, c'est ce qu'il y avait
    — 294 tuiles. Le sable est une image de GRÈVE ; au port, la planche entre
    dans l'eau."""
    sol = ville["sol"]
    sable = [(x, y) for y in range(quais["y"], quais["y"] + quais["h"])
             for x in range(quais["x"], quais["x"] + quais["l"])
             if sol[y][x] == "s"]
    colle = [(x, y) for x, y in sable
             if any(sol[y + dy][x + dx] == "Q"
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if 0 <= x + dx < ville["largeur"] and 0 <= y + dy < ville["hauteur"])]
    assert not colle, f"du sable contre le quai : {colle[:5]}"


def test_on_amarre_au_quai(ville):
    """⚠️ Ce qui manquait le plus, et qui découle de la géographie : une borne
    d'amarrage. On ne peut pas en poser sur un quai qui ne touche pas l'eau —
    le semis de la grève n'en trouvait que seize tuiles dans toute la ville, et
    c'est pour ça qu'il avait fallu aller chercher les 199 tuiles de TROTTOIR
    du bord. Le port s'amarre maintenant chez lui."""
    sol, L, H = ville["sol"], ville["largeur"], ville["hauteur"]
    bornes = [d for d in ville["decor"] if d["type"] == "poteau_amarrage"
              and sol[d["y"]][d["x"]] == "Q"]
    # ⚠️ Pas vingt : une borne tous les onze pas (`ECART_BORNE_AMARRAGE`). Plus
    # serrées, elles faisaient une palissade — Martin a vu une clôture.
    assert len(bornes) >= 8, f"{len(bornes)} bornes d'amarrage sur tout le port"
    for d in bornes:
        x, y = d["x"], d["y"]
        assert any(not (0 <= x + dx < L and 0 <= y + dy < H) or sol[y + dy][x + dx] == "~"
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), (
            f"une borne d'amarrage à sec en {(x, y)}")


def test_le_quai_est_un_quai_et_pas_un_plancher(ville):
    """Un port, ça porte : des caisses, des barils, ce qu'on n'a pas ramassé.
    Le quai n'avait qu'UNE sorte de décor — la caisse — et un objet par quinze
    tuiles."""
    sol = ville["sol"]
    dessus: dict[str, int] = {}
    for d in ville["decor"]:
        if sol[d["y"]][d["x"]] == "Q":
            dessus[d["type"]] = dessus.get(d["type"], 0) + 1
    for quoi in ("caisse", "baril", "poteau_amarrage", "pneu"):
        assert dessus.get(quoi, 0) > 0, f"pas un seul {quoi} sur le port : {dessus}"
    planches = sum(ligne.count("Q") for ligne in sol)
    total = sum(dessus.values())
    # ⚠️ **UNE FOURCHETTE.** Ce juge exigeait « au moins un objet par douze
    # tuiles », et le quai l'a tenu en devenant un plancher d'entrepôt — une
    # soixantaine de caisses solides sur dix rangées, 191 tuiles murées. Un quai
    # porte ce qu'on y charge CONTRE LA RUE et garde son milieu pour marcher.
    assert 12 <= planches / total <= 40, (
        f"un objet par {planches / total:.0f} tuiles de quai : entrepôt ou plancher nu ?")


def test_les_appontements_partent_du_quai(ville, quais):
    """⚠️ Une jetée qui ne touche pas la terre est une île, et personne n'y va.
    Elles avancent dans la baie DEPUIS le tablier, et c'est aussi ce qui donne
    au port sa dentelure : une lèvre parfaitement droite sur soixante tuiles se
    lit comme un mur."""
    sol = ville["sol"]
    planches = {(x, y) for y in range(quais["y"], quais["y"] + quais["h"])
                for x in range(quais["x"], quais["x"] + quais["l"]) if sol[y][x] == "Q"}
    assert planches, "plus un quai dans les Quais"
    # ⚠️ Le port des Quais est coupé en DARSES (les anciennes rues verticales) :
    # on ne demande donc pas une seule masse, on demande que chaque masse touche
    # le bord nord du district — c'est par là qu'on y descend du boulevard.
    masses, reste = [], set(planches)
    while reste:
        depart = min(reste)
        pile, groupe = [depart], {depart}
        reste.discard(depart)
        while pile:
            x, y = pile.pop()
            for cx, cy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (cx, cy) in reste:
                    reste.discard((cx, cy))
                    groupe.add((cx, cy))
                    pile.append((cx, cy))
        masses.append(groupe)
    for groupe in masses:
        haut = min(y for _, y in groupe)
        assert carte.marchable(sol[haut - 1][min(x for x, y in groupe if y == haut)]), (
            f"un morceau de quai de {len(groupe)} tuiles auquel on n'accède pas")
    # ⚠️ Et le port AVANCE dans la baie. On mesure le fond de chaque colonne :
    # la lèvre ordinaire est la médiane, un appontement est une colonne qui
    # descend nettement plus bas. C'est la dentelure elle-même qu'on mesure, pas
    # un motif de tuiles — une jetée de deux tuiles de large n'a de l'eau des
    # deux côtés sur aucune de ses colonnes.
    fonds = {}
    for x in range(quais["x"], quais["x"] + quais["l"]):
        colonne = [y for y in range(quais["y"], quais["y"] + quais["h"]) if sol[y][x] == "Q"]
        if colonne:
            fonds[x] = max(colonne)
    levre = sorted(fonds.values())[len(fonds) // 2]
    avancees = [x for x, fond in fonds.items() if fond >= levre + 3]
    assert len(avancees) >= 4, (
        f"{len(avancees)} colonnes avancent dans la baie : le port n'a pas d'appontement")


def test_l_eau_du_port_rejoint_la_baie(ville, quais):
    """Un bassin fermé est un piège : la 3e vague du bord de l'eau y amarre des
    chaloupes, et une coque qui n'en sort pas est un char dans un garage muré."""
    sol, L, H = ville["sol"], ville["largeur"], ville["hauteur"]
    depart = next((x, y) for y in range(H - 1, -1, -1) for x in range(L) if sol[y][x] == "~")
    pile, vues = [depart], {depart}
    while pile:
        x, y = pile.pop()
        for cx, cy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= cx < L and 0 <= cy < H and (cx, cy) not in vues and sol[cy][cx] == "~":
                vues.add((cx, cy))
                pile.append((cx, cy))
    au_port = [(x, y) for y in range(quais["y"], quais["y"] + quais["h"])
               for x in range(quais["x"], quais["x"] + quais["l"]) if sol[y][x] == "~"]
    coupees = [c for c in au_port if c not in vues]
    assert not coupees, f"{len(coupees)} tuiles d'eau du port ne rejoignent pas la baie"


def test_la_rue_de_service_reste_derriere(ville, quais):
    """On efface la rue qui passait DEVANT le quai, pas celle qui le dessert. Un
    port où aucun camion n'arrive n'est pas un port."""
    sol = ville["sol"]
    haut = min(y for y in range(quais["y"], quais["y"] + quais["h"])
               for x in range(quais["x"], quais["x"] + quais["l"]) if sol[y][x] == "Q")
    colonnes = [x for x in range(quais["x"], quais["x"] + quais["l"]) if sol[haut][x] == "Q"]
    route = [x for x in colonnes
             if any(carte.LEGENDE[sol[y][x]].get("route") for y in range(max(0, haut - 5), haut))]
    assert len(route) >= len(colonnes) * 0.8, (
        f"{len(colonnes) - len(route)} colonnes de quai sur {len(colonnes)} n'ont pas "
        "de rue derrière elles")
