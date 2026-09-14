"""Les terrains de banlieue — ce qui fait qu'un terrain a l'air habité.

⚠️ M8 a eu raison sur le principe et le dit dans son propre code : « la
banlieue se reconnait au VIDE autour des maisons, pas aux maisons ». Mais ce
vide etait litteralement vide — du gazon, un arbre par dix tuiles, pose au
sort. Or un terrain de banlieue est le CONTRAIRE du vide : il est plein des
traces de la vie de quelqu'un.

Ces juges-la tiennent les trois promesses qui coutent : une entree rejoint
TOUJOURS la rue, un sentier relie la porte a la rue sans passer par la
piscine, et la part d'entrees avec une auto se MESURE au lieu de se croire.
"""

import pytest

from app import carte

CARTE = carte.exporter()
SOL = CARTE["sol"]
LARGEUR, HAUTEUR = CARTE["largeur"], CARTE["hauteur"]
ZONE = {z["slug"]: z for z in CARTE["zones"]}["erables"]

#: Les glyphes d'une entree de voiture : de l'asphalte de terrain, avec ou
#: sans case. ⚠️ Les memes que le stationnement — c'est voulu : une entree EST
#: un stationnement d'une place, et `placeStationnee()` y gare une auto sans
#: une ligne de code de plus.
ENTREE = set("p^v<>")


def _dans_les_erables(x: int, y: int) -> bool:
    return (ZONE["x"] <= x < ZONE["x"] + ZONE["l"]
            and ZONE["y"] <= y < ZONE["y"] + ZONE["h"])


def _blocs(glyphes: set[str]) -> list[set[tuple[int, int]]]:
    """Les groupes de tuiles de ces glyphes, d'un seul tenant, dans Les Érables."""
    tuiles = {(x, y) for y in range(ZONE["y"], ZONE["y"] + ZONE["h"])
              for x in range(ZONE["x"], ZONE["x"] + ZONE["l"]) if SOL[y][x] in glyphes}
    blocs, vus = [], set()
    for depart in sorted(tuiles):
        if depart in vus:
            continue
        bloc, pile = {depart}, [depart]
        while pile:
            cx, cy = pile.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                voisin = (cx + dx, cy + dy)
                if voisin in tuiles and voisin not in bloc:
                    bloc.add(voisin)
                    pile.append(voisin)
        vus |= bloc
        blocs.append(bloc)
    return blocs


def test_la_banlieue_a_des_entrees_et_des_piscines():
    """Le décor du juge : sans ça, tout ce qui suit passerait pour rien."""
    entrees = [b for b in _blocs(ENTREE) if len(b) <= 8]
    assert len(entrees) >= 15, f"{len(entrees)} entrées de voiture dans Les Érables"
    piscines = _blocs({"o"})
    assert piscines, "aucune piscine dans toute la banlieue"
    for bloc in piscines:
        # ⚠️ Un bloc de deux sur deux, jamais un L : un L n'est pas une
        # piscine, c'est une flaque.
        xs = {x for x, _ in bloc}
        ys = {y for _, y in bloc}
        assert len(bloc) == len(xs) * len(ys), f"une piscine en L en {sorted(bloc)[0]}"


def test_toute_entree_de_voiture_rejoint_la_chaussee():
    """⚠️ Même règle que « toute rangée de stationnement touche une allée » :
    une entrée qui ne rejoint pas la rue n'est pas une entrée, c'est un carré
    d'asphalte. Et une auto garée dedans n'en sortirait jamais."""
    orphelines = []
    for bloc in _blocs(ENTREE):
        if len(bloc) > 8:
            continue                      # un vrai stationnement, pas une entrée
        touche = False
        for (x, y) in bloc:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < LARGEUR and 0 <= ny < HAUTEUR):
                    continue
                if (nx, ny) in bloc:
                    continue
                proprietes = carte.LEGENDE[SOL[ny][nx]]
                if proprietes.get("route") or proprietes.get("trottoir"):
                    touche = True
        if not touche:
            orphelines.append(sorted(bloc)[0])
    assert not orphelines, f"{len(orphelines)} entrées ne rejoignent rien : {orphelines[:4]}"


def test_un_sentier_mene_a_chaque_porte_de_banlieue_sans_passer_par_la_piscine():
    """⚠️ Sans sentier, on marche sur le gazon pour entrer chez les gens — et
    c'est précisément ce qui donne l'impression du « pas fini ».

    Et ⚠️ **une piscine ne coupe jamais un sentier** : elle se pose derrière la
    maison, après le sentier, justement pour ça."""
    portes = [p for p in CARTE["portes"] if _dans_les_erables(p["x"], p["y"])]
    assert portes, "le juge n'a trouvé aucune porte dans Les Érables : il ne prouve rien"
    sans_sentier, noyees = [], []
    for porte in portes:
        x, y = porte["x"], porte["y"]
        chemin = []
        for k in range(1, 12):
            if not (0 <= y + k < HAUTEUR):
                break
            glyphe = SOL[y + k][x]
            if glyphe == "o":
                noyees.append((x, y))
                break
            chemin.append(glyphe)
            proprietes = carte.LEGENDE[glyphe]
            if proprietes.get("route"):
                break                     # on a rejoint la rue
            if not proprietes.get("trottoir") and glyphe != ".":
                break                     # du gazon, du bâti : le sentier s'arrête là
        else:
            continue
        if not any(carte.LEGENDE[g].get("route") for g in chemin):
            sans_sentier.append((x, y))
    assert not noyees, f"un sentier passe dans une piscine : {noyees[:3]}"
    # ⚠️ Pas toutes : une maison au fond d'une cour, derrière une autre, n'a pas
    # de ligne droite vers la rue. Ce qu'on exige, c'est que la règle tienne
    # pour la GRANDE MAJORITÉ — sinon elle n'existe pas.
    part = 1 - len(sans_sentier) / len(portes)
    assert part >= 0.8, (
        f"seulement {part:.0%} des portes de banlieue ont un sentier jusqu'à la rue "
        f"({len(sans_sentier)} sur {len(portes)})"
    )


@pytest.mark.parametrize("graine", (carte.GRAINE, 1, 2))
def test_une_entree_sur_trois_porte_une_auto(graine):
    """⚠️ Pas toutes, et c'est une MESURE, pas une intention. Si chaque bungalow
    porte une case, la banlieue se remplit de chars stationnés et le budget
    d'entités y passe ; si aucune n'en porte, l'entrée est un carré gris."""
    chantier = carte._Chantier(carte.PLAN, graine)
    vues = {"entrees": 0, "cases": 0}
    vrai = carte._Chantier._terrain_de_banlieue

    def espion(self, parcelle, boite, porte):
        avant = sum(ligne.count("p") + ligne.count("^") for ligne in map("".join, self.sol))
        cases = sum(ligne.count("^") for ligne in map("".join, self.sol))
        vrai(self, parcelle, boite, porte)
        if sum(ligne.count("p") + ligne.count("^") for ligne in map("".join, self.sol)) > avant:
            vues["entrees"] += 1
        if sum(ligne.count("^") for ligne in map("".join, self.sol)) > cases:
            vues["cases"] += 1

    carte._Chantier._terrain_de_banlieue = espion
    try:
        chantier.eaux()
        chantier.rues()
        chantier.croisements()
        chantier.ilots()
    finally:
        carte._Chantier._terrain_de_banlieue = vrai
    assert vues["entrees"] >= 15, f"{vues['entrees']} entrées seulement (graine {graine})"
    part = vues["cases"] / vues["entrees"]
    attendu = carte._Chantier.PART_ENTREE_AVEC_CASE
    assert attendu / 2 <= part <= attendu * 1.6, (
        f"{part:.0%} des entrées portent une auto, la fiche en veut {attendu:.0%} "
        f"({vues['cases']} sur {vues['entrees']}, graine {graine})"
    )


def test_les_quatre_tuiles_de_la_piscine_font_un_rond(banc):
    """⚠️ Retour de Martin, en regardant l'écran : « piscine ronde stp et pas
    4 carrés ». Peintes chacune pour soi, les quatre tuiles montraient quatre
    margelles et quatre bassins.

    Chaque tuile porte donc un QUART du disque, et elle sait lequel en lisant
    ses voisines. Ce juge tient ce dont le peintre a besoin : les quatre tuiles
    d'une piscine rendent quatre variantes DIFFÉRENTES, une par coin — si elles
    rendaient la même, on serait revenu aux quatre carrés."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        let coin = null;
        for (let y = 1; y < c.h - 2 && !coin; y++) {
            for (let x = 1; x < c.w - 2; x++) {
                if (c.sol[y][x] !== 'o') continue;
                if (c.sol[y][x + 1] === 'o' && c.sol[y + 1][x] === 'o' && c.sol[y + 1][x + 1] === 'o'
                    && c.sol[y - 1][x] !== 'o' && c.sol[y][x - 1] !== 'o') { coin = { x: x, y: y }; break; }
            }
        }
        if (!coin) return { trouve: false };
        // ⚠️ Les quatre bits bas seulement : les bits hauts sont du bruit.
        const quart = function (dx, dy) {
            return L.Monde.varianteDeTuile('o', coin.x + dx, coin.y + dy) & 15;
        };
        return { trouve: true, hg: quart(0, 0), hd: quart(1, 0), bg: quart(0, 1), bd: quart(1, 1) };
    }""")
    assert r["trouve"] is True, "aucune piscine 2 x 2 dans la ville : le juge ne prouve rien"
    # nord=1, est=2, sud=4, ouest=8 — le centre du cercle est du côté des voisines.
    assert r["hg"] == 2 | 4, f"le coin haut-gauche ne voit pas ses voisines est et sud : {r}"
    assert r["hd"] == 8 | 4, f"le coin haut-droit : {r}"
    assert r["bg"] == 1 | 2, f"le coin bas-gauche : {r}"
    assert r["bd"] == 1 | 8, f"le coin bas-droit : {r}"
    assert len({r["hg"], r["hd"], r["bg"], r["bd"]}) == 4, (
        "les quatre tuiles se peignent pareil : c'est quatre carrés, pas un rond"
    )


def test_la_piscine_n_est_pas_la_baie():
    """⚠️ Hors terre : on y entre debout, on ne s'y noie pas. Solidité 3 comme un
    meuble — un piéton la traverse, une auto non, et aucun juge de connexité ne
    s'en émeut. Elle n'est donc PAS de l'eau au sens du masque du nageur."""
    piscine = carte.LEGENDE["o"]
    assert piscine["solide"] == 3, piscine
    assert carte.marchable("o"), "on ne peut pas entrer dans sa propre piscine"
    assert carte.solidite("o") != carte.solidite("~"), "la piscine est de l'eau : on s'y noie"
    # ⚠️ Et elle se peint EN BLOC : sans ce drapeau, chaque tuile ignore ses
    # voisines et l'on retombe sur quatre carrés.
    assert piscine["bloc"] is True, piscine
