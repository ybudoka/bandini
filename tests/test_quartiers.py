"""Des quartiers qu'on reconnaît — 1re vague : le standing se déclare, et la
saleté se déplace.

Demande de Martin (16 sept. 2026) : « je veux des cartiers plus reconnaissable,
plus riche et propre avec des commerce plus riche, des cartiers plus pauvre et
sale ».

⚠️ **Mesuré d'abord** : le zonage existait (les lettres du `plan`), le standing
n'existait nulle part, et la saleté ne suivait que le genre des îlots — 30 objets
en cossu, 40 en ordinaire, 159 en pauvre une fois la grille écrite. Et Martin
avait renvoyé « trop de saleté partout » le jour même : **le total ne monte pas**.

Les juges comparent la ville à elle-même **sans** `salete.deplacer` : c'est la
seule façon de dire « rien d'autre n'a bougé » sans recopier la ville d'hier.
"""

from __future__ import annotations

import json

import pytest

from app import carte, chantiers, devantures, mobilier, pietons, salete, vitrines

#: La saleté qu'on compte : ce qu'on jette par terre, sur la friche d'un terrain
#: vague (`;`) ou au pied d'un mur (`_`). ⚠️ En toutes lettres, pas relu dans
#: `carte.DECHETS` ni `salete.AU_PIED_DES_MURS` : un juge qui relit la table
#: qu'il juge ne rougit pas.
DECHETS = {"debris", "ordures", "pneu", "baril", "caisse", "matelas", "caddie"}
SOLS_SALES = {";", "_"}

#: Le rapport de densité exigé entre un quartier pauvre et un ordinaire.
CINQ_FOIS = 5


def _sans(*quoi):
    """Génère la ville avec ces fonctions remplacées par rien."""
    originaux = [(module, nom, getattr(module, nom)) for module, nom in quoi]
    for module, nom, _ in originaux:
        setattr(module, nom, lambda *a, **k: {})
    try:
        return carte.generer()
    finally:
        for module, nom, fonction in originaux:
            setattr(module, nom, fonction)


@pytest.fixture(scope="module")
def villes():
    """`ville` : la ville livrée. `avant` et `apres` : sans le mobilier de rue,
    sans puis avec le déplacement de la saleté."""
    ville = carte.generer()
    avant = _sans((salete, "deplacer"), (mobilier, "semer"))
    apres = _sans((mobilier, "semer"))
    return ville, avant, apres


@pytest.fixture(scope="module")
def tout_part():
    """⚠️ LA RÈGLE DE POSE SOUS CHARGE. Sur la ville livrée, huit déchets
    seulement se reposent : aucun ne tombe à côté d'un autre décor, et un juge
    qui ne lit qu'eux resterait vert sans `_place_libre` (mutation vue le
    16 sept. 2026). Ici TOUTE la saleté part, pauvre comprise, et se repose :
    une quarantaine de poses pour mettre la règle à l'épreuve. `(avant, apres)`."""
    garde = dict(salete.GARDE)
    salete.GARDE.update({k: 0.0 for k in salete.GARDE})
    try:
        apres = _sans((mobilier, "semer"))
    finally:
        salete.GARDE.update(garde)
    return _sans((salete, "deplacer"), (mobilier, "semer")), apres


@pytest.fixture(scope="module")
def chantier():
    return carte._Chantier(carte.PLAN, carte.GRAINE)


def dechets(ville):
    return [d for d in ville["decor"]
            if d["type"] in DECHETS and ville["sol"][d["y"]][d["x"]] in SOLS_SALES]


def saletes(ville):
    """Chaque saleté de la ville : (sorte, x, y)."""
    return ([("dechet", d["x"], d["y"]) for d in dechets(ville)]
            + [("tag", g["x"], g["y"]) for g in ville["graffitis"]]
            + [("nid", n["x"], n["y"]) for n in ville["nids_de_poule"]])


# --- Le standing se déclare ---------------------------------------------------


def test_chaque_bloc_declare_son_standing():
    """Pas de défaut silencieux : un bloc bâtissable dit `+`, `=` ou `-`, un bloc
    d'eau dit `~`, et un bloc avalé dit ce que dit son maître."""
    maitre = carte.regions_du_plan(carte.PLAN)
    assert len(carte.STANDING) == len(carte.PLAN)
    for by, ligne in enumerate(carte.PLAN):
        assert len(carte.STANDING[by]) == len(ligne)
        for bx, _glyphe in enumerate(ligne):
            mx, my = maitre[(bx, by)]
            lettre = carte.STANDING[by][bx]
            if carte.PLAN[my][mx] == "~":
                assert lettre == "~", f"le bloc d'eau {(bx, by)} déclare {lettre!r}"
            else:
                assert lettre in "+=-", f"le bloc {(bx, by)} ({carte.PLAN[my][mx]}) déclare {lettre!r}"
            assert lettre == carte.STANDING[my][mx], f"{(bx, by)} ne dit pas ce que dit son maître {(mx, my)}"


@pytest.mark.parametrize("slug, rangee, colonne, lettre, message", [
    ("erables", 0, 0, "?", "ne declare pas"),
    ("baie", 2, 3, "=", "bloc d'eau"),
    ("erables", 1, 1, "-", "son maitre"),         # un `<` qui ne dit pas ce que dit son maître
])
def test_une_grille_fautive_ne_se_charge_pas(slug, rangee, colonne, lettre, message):
    districts = []
    for d in carte.DISTRICTS:
        if d["slug"] == slug:
            lignes = list(d["standing"])
            lignes[rangee] = lignes[rangee][:colonne] + lettre + lignes[rangee][colonne + 1:]
            d = {**d, "standing": tuple(lignes)}
        districts.append(d)
    with pytest.raises(ValueError, match=message):
        carte._assembler_le_standing(tuple(districts), carte.PLAN)


def test_une_grille_sans_la_forme_du_plan_ne_se_charge_pas():
    districts = tuple({**d, "standing": d["standing"][:-1]} if d["slug"] == "shop" else d
                      for d in carte.DISTRICTS)
    with pytest.raises(ValueError, match="forme du plan"):
        carte._assembler_le_standing(districts, carte.PLAN)


def test_le_standing_ne_suit_pas_le_district():
    """Le Faubourg a sa rue chic et son coin pauvre ; les Quais et La Shop ne
    sont pas pauvres d'un bout à l'autre."""
    for district in carte.DISTRICTS:
        if district["slug"] in ("faubourg", "quais", "shop"):
            lettres = set("".join(district["standing"])) - {"~"}
            assert len(lettres) >= 2, f"{district['nom']} n'a qu'un standing : {lettres}"


def test_une_rue_se_coupe_en_deux(chantier):
    """Chaque moitié de rue est du standing du bloc qu'elle borde — la coupe de
    `rect_district`, écrite ici en toutes lettres."""
    x = 0
    for i, (rue, colonne) in enumerate(zip(carte.RUES_V, carte.COLONNES)):
        if i > 0:
            ouest, est = x + rue // 2 - 1, x + rue // 2
            y = chantier.yb[1] + 2                    # au milieu de la 2e rangée de blocs
            attendu_ouest = carte.STANDINGS.get(carte.STANDING[1][i - 1])
            attendu_est = carte.STANDINGS.get(carte.STANDING[1][i])
            assert chantier.standing_en(ouest, y) == attendu_ouest, (i, ouest)
            assert chantier.standing_en(est, y) == attendu_est, (i, est)
        x += rue + colonne


# --- La saleté se déplace -----------------------------------------------------


def test_zero_salete_en_cossu_et_cinq_fois_plus_en_pauvre(villes, chantier):
    ville, _avant, _apres = villes
    terre: dict[str | None, int] = {}
    for y, ligne in enumerate(ville["sol"]):
        for x, glyphe in enumerate(ligne):
            if glyphe != "~":
                s = chantier.standing_en(x, y)
                terre[s] = terre.get(s, 0) + 1
    compte: dict[str | None, int] = {}
    en_cossu = []
    for sorte, x, y in saletes(ville):
        s = chantier.standing_en(x, y)
        compte[s] = compte.get(s, 0) + 1
        if s == "cossu":
            en_cossu.append((sorte, x, y))
    assert not en_cossu, f"{len(en_cossu)} saletés en quartier cossu, dont {en_cossu[:3]}"
    pauvre = compte.get("pauvre", 0) / terre["pauvre"]
    ordinaire = compte.get("ordinaire", 0) / terre["ordinaire"]
    assert ordinaire > 0, "un quartier ordinaire sans une saleté n'est plus ordinaire"
    assert pauvre >= CINQ_FOIS * ordinaire, (
        f"pauvre {1000 * pauvre:.2f}, ordinaire {1000 * ordinaire:.2f} par mille tuiles")


def test_la_salete_se_deplace_sans_s_ajouter(villes):
    """⚠️ « trop de saleté partout » : aucune des trois sortes ne monte."""
    _ville, avant, apres = villes
    for sorte in ("dechet", "tag", "nid"):
        n_avant = sum(1 for s in saletes(avant) if s[0] == sorte)
        n_apres = sum(1 for s in saletes(apres) if s[0] == sorte)
        assert n_apres <= n_avant, f"{sorte} : {n_avant} avant, {n_apres} après"
        assert n_apres >= 0.9 * n_avant, f"{sorte} : {n_avant} avant, {n_apres} après — elle s'est perdue"


def test_hors_de_la_salete_la_ville_ne_bouge_pas(villes):
    """Le déplacement ne touche que la saleté : pas une tuile, pas un paquet,
    pas un abribus, et pas un autre décor. La poubelle qui déborde est la même
    poubelle."""
    _ville, avant, apres = villes
    touchees = {"decor", "graffitis", "nids_de_poule"}
    for cle in avant:
        if cle == "chantiers":
            # ⚠️ Sans leurs annexes : elles LISENT la ville finie (`chantiers.completer`).
            assert chantiers.sans_annexes(avant[cle]) == chantiers.sans_annexes(apres[cle]), cle
        elif cle not in touchees:
            assert json.dumps(avant[cle], sort_keys=True) == json.dumps(apres[cle], sort_keys=True), cle

    def reste(ville):
        sales = {(d["x"], d["y"]) for d in dechets(ville)}
        return [{**d, "type": "poubelle" if d["type"] == "poubelle_pleine" else d["type"]}
                for d in ville["decor"] if (d["x"], d["y"]) not in sales]

    assert reste(avant) == reste(apres)


@pytest.mark.parametrize("quelle", ["livree", "tout_part"])
def test_ce_qui_se_pose_est_au_pied_d_un_mur_pauvre(villes, tout_part, chantier, quelle):
    avant, apres = villes[1:] if quelle == "livree" else tout_part
    deja = {(d["x"], d["y"]) for d in avant["decor"]}
    poses = [d for d in dechets(apres) if (d["x"], d["y"]) not in deja]
    assert len(poses) >= (5 if quelle == "livree" else 30), f"{len(poses)} déchets reposés"
    devant = {(p["x"] + i, p["y"] + j) for p in apres["portes"] for j in (1, 2, 3) for i in (-1, 0, 1)}
    for d in poses:
        x, y = d["x"], d["y"]
        assert chantier.standing_en(x, y) == "pauvre", f"{d['type']} en {(x, y)} hors d'un quartier pauvre"
        assert apres["sol"][y][x] == "_", f"{d['type']} en {(x, y)} sur « {apres['sol'][y][x]} »"
        murs = [apres["sol"][y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        assert any(carte.LEGENDE[m].get("solide") == 1 for m in murs), f"{d['type']} en {(x, y)} loin d'un mur"
        assert (x, y) not in devant, f"{d['type']} en {(x, y)} devant une porte"
        voisins = [e for e in apres["decor"] if e is not d and abs(e["x"] - x) <= 1 and abs(e["y"] - y) <= 1]
        assert not voisins, f"{d['type']} en {(x, y)} collé à {voisins[0]['type']}"


@pytest.mark.parametrize("quelle", ["livree", "tout_part"])
def test_rien_ne_se_ferme_a_pied(villes, tout_part, quelle):
    """⚠️ Un sac d'ordures ARRÊTE un piéton. Tout ce qu'on atteignait à pied
    avant s'atteint encore — moins les tuiles que la saleté occupe."""
    avant, apres = villes[1:] if quelle == "livree" else tout_part

    def atteignables(ville):
        sol, largeur, hauteur = ville["sol"], ville["largeur"], ville["hauteur"]
        bloque = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE}
        depart = (ville["apparition"]["joueur"]["x"], ville["apparition"]["joueur"]["y"])
        vus, pile = {depart}, [depart]
        while pile:
            x, y = pile.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (0 <= n[0] < largeur and 0 <= n[1] < hauteur and n not in vus
                        and carte.franchissable(sol[n[1]][n[0]]) and n not in bloque):
                    vus.add(n)
                    pile.append(n)
        return vus

    pris = {(d["x"], d["y"]) for d in apres["decor"]} - {(d["x"], d["y"]) for d in avant["decor"]}
    perdus = (atteignables(avant) - pris) - atteignables(apres)
    assert not perdus, f"{len(perdus)} tuiles qu'on n'atteint plus à pied, dont {sorted(perdus)[:4]}"


def test_la_poubelle_deborde_en_pauvre_et_seulement_la(villes, chantier):
    ville, avant, _apres = villes
    poubelles = [d for d in ville["decor"] if d["type"] in ("poubelle", "poubelle_pleine")]
    assert len(poubelles) == sum(1 for d in avant["decor"] if d["type"] == "poubelle")
    pleines = 0
    for d in poubelles:
        pauvre = chantier.standing_en(d["x"], d["y"]) == "pauvre"
        assert (d["type"] == "poubelle_pleine") == pauvre, f"{d['type']} en {(d['x'], d['y'])}"
        pleines += pauvre
    assert pleines >= 20, f"{pleines} poubelles qui débordent dans toute la ville"


def test_les_nids_deplaces_restent_des_nids(villes):
    """Espacés, sur la chaussée, hors croisement — la règle de `NIDS_DE_POULE`,
    écrite ici en chiffres."""
    ville, _avant, _apres = villes
    nids = [(n["x"], n["y"]) for n in ville["nids_de_poule"]]
    for i, (x, y) in enumerate(nids):
        assert carte.LEGENDE[ville["sol"][y][x]].get("route"), f"nid en {(x, y)} hors de la chaussée"
        for inter in ville["intersections"]:
            assert not (inter["x"] <= x < inter["x"] + inter["l"] and inter["y"] <= y < inter["y"] + inter["h"])
        for px, py in nids[i + 1:]:
            assert abs(px - x) + abs(py - y) >= 7, f"deux nids collés en {(x, y)} et {(px, py)}"


# --- Le propre se voit aussi --------------------------------------------------


def test_une_rue_cossue_est_plantee_une_rue_pauvre_ne_l_est_pas(villes, chantier):
    """Les arbres et les bacs à fleurs du bord des rues (`mobilier.semer`)."""
    ville, _avant, apres = villes
    ajoutes = ville["decor"][len(apres["decor"]):]
    abords: dict[str | None, int] = {}
    for y, ligne in enumerate(ville["sol"]):
        for x, glyphe in enumerate(ligne):
            if glyphe == "_":
                s = chantier.standing_en(x, y)
                abords[s] = abords.get(s, 0) + 1
    arbres: dict[str | None, int] = {}
    for d in ajoutes:
        s = chantier.standing_en(d["x"], d["y"])
        if d["type"] == "arbre":
            arbres[s] = arbres.get(s, 0) + 1
        elif d["type"] == "bac_fleurs":
            assert s == "cossu", f"un bac à fleurs en {(d['x'], d['y'])}, quartier {s}"
    assert not arbres.get("pauvre"), f"{arbres.get('pauvre')} arbres de rue en quartier pauvre"
    assert arbres["cossu"] / abords["cossu"] > arbres["ordinaire"] / abords["ordinaire"], (arbres, abords)
    # ⚠️ ET DANS LE FAUBOURG. Les Érables sont plantés serré par leur district :
    # sans le standing, « cossu plus planté qu'ordinaire » tenait tout seul. Au
    # Faubourg, c'est le standing seul qui sépare la rue chic des autres.
    au_faubourg: dict[str | None, list[int]] = {}
    for y, ligne in enumerate(ville["sol"]):
        for x, glyphe in enumerate(ligne):
            if glyphe == "_" and chantier.district_en(x, y) == "faubourg":
                au_faubourg.setdefault(chantier.standing_en(x, y), [0, 0])[0] += 1
    for d in ajoutes:
        if d["type"] == "arbre" and chantier.district_en(d["x"], d["y"]) == "faubourg":
            au_faubourg[chantier.standing_en(d["x"], d["y"])][1] += 1
    chic, ordinaire = (au_faubourg[s][1] / au_faubourg[s][0] for s in ("cossu", "ordinaire"))
    assert chic >= 2 * ordinaire, f"la rue chic du Faubourg : {au_faubourg}"
    bacs = sum(1 for d in ajoutes if d["type"] == "bac_fleurs")
    assert bacs >= 10, f"{bacs} bacs à fleurs dans toute la ville"


# --- Le moteur lit la même grille ---------------------------------------------


def test_le_moteur_lit_les_memes_grilles(banc, chantier):
    """Python décide, JS calcule : `Monde.standingA` et `Monde.usageA` disent la
    même chose que `standing_en` et `usage_en`, tuile pour tuile — et ressorti
    d'une pièce, encore."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const lettre = { cossu: '+', ordinaire: '=', pauvre: '-' };
        const carte = function () {
            const lignes = [];
            for (let y = 0; y < L.Monde.carte.h; y++) {
                let l = '';
                for (let x = 0; x < L.Monde.carte.w; x++) l += lettre[L.Monde.standingA(x, y)] || '~';
                lignes.push(l);
            }
            return lignes;
        };
        const usages = [];
        for (let y = 0; y < L.Monde.carte.h; y += 3) {
            const l = [];
            for (let x = 0; x < L.Monde.carte.w; x += 3) l.push(L.Monde.usageA(x, y));
            usages.push(l);
        }
        const dehors = carte();
        const ville = L.Monde.carte;
        const porte = ville.def.portes.find(function (p) { return p.interieur; });
        L.Monde.entrer(porte);
        const dedans = L.Monde.standingA(1, 1);
        L.Monde.restaurer(ville);
        return { dehors: dehors, dedans: dedans, ressorti: L.Monde.standingA(10, 10), usages: usages,
                 usageDedans: (L.Monde.entrer(porte), L.Monde.usageA(1, 1)) };
    }""")
    lettre = {"cossu": "+", "ordinaire": "=", "pauvre": "-", None: "~"}
    for y, ligne in enumerate(r["dehors"]):
        attendu = "".join(lettre[chantier.standing_en(x, y)] for x in range(len(ligne)))
        assert ligne == attendu, f"rangée {y} : le moteur et le générateur ne s'entendent pas"
    assert r["dedans"] is None
    assert r["ressorti"] == chantier.standing_en(10, 10)
    for j, ligne in enumerate(r["usages"]):
        attendu = [chantier.usage_en(3 * i, 3 * j) for i in range(len(ligne))]
        assert ligne == attendu, f"rangée {3 * j} : l'usage du moteur n'est pas celui du générateur"
    assert r["usageDedans"] is None


# --- 2e vague : le zonage se lit ------------------------------------------------


#: Ce que le plan dit, lu dans ses lettres et écrit ici en toutes lettres : La Shop
#: est industrielle sauf son parc et son bloc de commerces, Les Érables habitent
#: sauf leur rangée commerçante et la cour des Chevreuils (une cour, pas une rue).
USAGES_ATTENDUS = {
    "shop": ("iiiiiip", "iiiiiip", "iiiiiii", "iiiiiii", "iiiiiic", "iiiiiic"),
    "erables": ("rrrpr", "rrrpr", "rrrrr", "rrrrr", "ccirr", "rrrrr"),
    "baie": ("~~~~~~~",) * 6,
}


def test_l_usage_se_deduit_du_plan():
    maitre = carte.regions_du_plan(carte.PLAN)
    lettres = {fiche["lettre"] for fiche in carte.USAGES.values()}
    assert len(lettres) == len(carte.USAGES), "deux usages partagent une lettre"
    grille = carte.grille_des_usages(carte.PLAN)
    for by, ligne in enumerate(grille):
        for bx, lettre in enumerate(ligne):
            mx, my = maitre[(bx, by)]
            assert lettre in lettres, f"le bloc {(bx, by)} n'a pas d'usage"
            assert lettre == grille[my][mx], f"{(bx, by)} ne dit pas l'usage de son maître"
    for district in carte.DISTRICTS:
        attendu = USAGES_ATTENDUS.get(district["slug"])
        if attendu:
            lu = tuple(ligne[district["bx"]:district["bx"] + len(district["plan"][0])]
                       for ligne in grille[district["by"]:district["by"] + len(district["plan"])])
            assert lu == attendu, f"{district['nom']} : {lu}"
    for fiche in carte.USAGES.values():
        assert fiche["couleur"].startswith("#") and fiche["libelle"], fiche


def test_chaque_lieu_garanti_a_un_usage():
    for glyphe in carte.SPECIAUX:
        assert carte.usage_du_glyphe(glyphe) in carte.USAGES, glyphe


#: Où chaque meuble de l'usage a le droit d'être — en toutes lettres.
USAGE_DU_MEUBLE = {"parcometre": "commercial", "boite_aux_lettres": "residentiel",
                   "bac_recyclage": "residentiel", "palettes": "industriel", "benne": "industriel"}


def test_le_mobilier_dit_l_usage(villes, chantier):
    ville, _avant, apres = villes
    ajoutes = ville["decor"][len(apres["decor"]):]
    compte: dict[str, int] = {}
    for d in ajoutes:
        if d["type"] in USAGE_DU_MEUBLE:
            usage = chantier.usage_en(d["x"], d["y"])
            assert usage == USAGE_DU_MEUBLE[d["type"]], f"{d['type']} en {(d['x'], d['y'])}, quartier {usage}"
            compte[usage] = compte.get(usage, 0) + 1
    for usage, minimum in (("commercial", 15), ("residentiel", 10), ("industriel", 15)):
        assert compte.get(usage, 0) >= minimum, f"{compte.get(usage, 0)} meubles d'usage en {usage}"


def test_le_zonage_ne_touche_ni_une_tuile_ni_un_arbre(villes, monkeypatch):
    """⚠️ Une couche peinte et un semis de plus, dans son propre dé : sans le
    mobilier de l'usage, la ville est la même glyphe pour glyphe, et le décor le
    même objet pour objet, dans le même ordre."""
    ville, _avant, _apres = villes
    monkeypatch.setattr(mobilier, "MEUBLES_PAR_USAGE", {})
    sans = carte.generer()
    for cle in ville:
        if cle == "chantiers":
            assert chantiers.sans_annexes(ville[cle]) == chantiers.sans_annexes(sans[cle]), cle
        elif cle != "decor":
            assert json.dumps(ville[cle], sort_keys=True) == json.dumps(sans[cle], sort_keys=True), cle
    assert [d for d in ville["decor"] if d["type"] not in USAGE_DU_MEUBLE] == sans["decor"]


def _tuile(ville, chantier, glyphe, usage, standing, district=None):
    for y, ligne in enumerate(ville["sol"]):
        for x, g in enumerate(ligne):
            if g == glyphe and chantier.usage_en(x, y) == usage and chantier.standing_en(x, y) == standing \
                    and (district is None or chantier.district_en(x, y) == district):
                return x, y
    raise AssertionError(f"aucun « {glyphe} » {usage} {standing} {district or ''} dans la ville")


def _luminance(couleur):
    r, g, b = (int(couleur[i:i + 2], 16) for i in (1, 3, 5))
    return 0.3 * r + 0.59 * g + 0.11 * b


def test_le_sol_se_peint_selon_le_quartier(banc, villes, chantier):
    """Le peintre de morceau lit l'usage et le standing : un trottoir de rue chic
    n'a pas le béton d'une cour d'usine, l'abord d'une maison est une bande de
    gazon, celui d'une usine de l'asphalte."""
    ville = villes[0]
    tuiles = {
        "chic": (".", *_tuile(ville, chantier, ".", "commercial", "cossu")),
        "usine": (".", *_tuile(ville, chantier, ".", "industriel", "pauvre")),
        "maison": ("_", *_tuile(ville, chantier, "_", "residentiel", "cossu")),
        "hangar": ("_", *_tuile(ville, chantier, "_", "industriel", "pauvre")),
        "commerce": ("_", *_tuile(ville, chantier, "_", "commercial", "ordinaire")),
    }
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const sortie = {};
        for (const nom in o.tuiles) {
            const t = o.tuiles[nom], couleurs = [];
            const ctx = { set fillStyle(c) { couleurs.push(c); }, get fillStyle() { return couleurs[couleurs.length - 1]; },
                          fillRect: function () {} };
            const v = L.Monde.varianteDeTuile(t[0], t[1], t[2]);
            L.TUILES[t[0]](ctx, v, 16);
            sortie[nom] = { v: v, fond: couleurs[0], couleurs: couleurs, glyphe: L.Monde.glyphe(t[1], t[2]) };
        }
        return sortie;
    }""".replace("o.tuiles", json.dumps(tuiles)))
    for nom, (glyphe, _x, _y) in tuiles.items():
        assert r[nom]["glyphe"] == glyphe, f"{nom} : le glyphe a changé"
    assert _luminance(r["usine"]["fond"]) < _luminance(r["chic"]["fond"]) - 20, (r["usine"]["fond"], r["chic"]["fond"])
    rv, gv, bv = (int(r["maison"]["fond"][i:i + 2], 16) for i in (1, 3, 5))
    assert gv > rv and gv > bv, f"l'abord d'une maison n'est pas du gazon : {r['maison']['fond']}"
    assert _luminance(r["hangar"]["fond"]) < _luminance(r["commerce"]["fond"]), (r["hangar"]["fond"], r["commerce"]["fond"])
    assert r["commerce"]["fond"] != r["maison"]["fond"] != r["hangar"]["fond"]


def test_la_carte_peint_le_zonage(banc, paquet, villes, chantier):
    """La carte plein écran teint chaque bloc de son usage — pas les rues — et sa
    légende se bâtit depuis la table, dans son ordre."""
    ville = villes[0]
    table = paquet["carte"]["zonage"]
    route = next((x, y) for y, ligne in enumerate(ville["sol"]) for x, g in enumerate(ligne)
                 if carte.LEGENDE[g].get("route") and not carte.LEGENDE[g].get("trottoir"))
    bloc = _tuile(ville, chantier, "_", "industriel", "pauvre")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.ouvrirCarte();
        const avant = L.B.stats.images;
        o.frame(1);
        return { legende: L.Hud.legendeDuZonage(L.Monde.carte), etat: L.B.etat,
                 images: L.B.stats.images - avant, calque: !!L.Monde.calqueDeZonage(),
                 route: L.Monde.couleurDeZonage(%d, %d), bloc: L.Monde.couleurDeZonage(%d, %d) };
    }""" % (*route, *bloc))
    assert r["etat"] == "carte" and r["calque"], r
    # ⚠️ L'ordre ÉCRIT en Python, pas celui du paquet (qui trie ses clés).
    assert [e["usage"] for e in r["legende"]] == list(carte.USAGES), "la légende ne suit pas la table"
    for e in r["legende"]:
        assert e["couleur"] == table[e["usage"]]["couleur"] and e["libelle"] == table[e["usage"]]["libelle"]
    assert r["route"] is None, "le calque teint la chaussée"
    assert r["bloc"] == table["industriel"]["couleur"]


# --- 3e vague : les commerces montent et descendent ------------------------------


#: Les enseignes du standing, en toutes lettres (pas relues dans `devantures`).
COSSUES = {"BIJOUTERIE", "FLEURISTE", "BISTRO", "GALERIE D'ART", "TAILLEUR", "CHOCOLATIER",
           "BOUTIQUE DE VIN", "PARFUMERIE", "ANTIQUAIRE", "FROMAGERIE", "SALON DE THÉ",
           "HAUTE COUTURE", "MAROQUINERIE", "ENCADREUR", "TRAITEUR", "SPA"}
PAUVRES = {"PRÊT SUR GAGES", "CHÈQUES CASH", "BINGO", "DÉPANNEUR 24 H", "À LOUER", "TOUT À 1 $",
           "BRIC-À-BRAC", "PRÊTS RAPIDES", "VIDÉO POKER", "LIQUIDATION", "TATOUAGE", "BIÈRE ET VIN"}


def _ordinaires(ville):
    """Les devantures qui ne sont pas un lieu garanti (son enseigne, et sa porte)."""
    speciaux = {texte for texte, _ in devantures.ENSEIGNES.values()}
    return [d for d in ville["devantures"] if not (d["texte"] in speciaux and d.get("porte"))]


def test_aucune_enseigne_cossue_en_pauvre_ni_l_inverse(villes, chantier):
    ville = villes[0]
    cossues = pauvres = 0
    for d in _ordinaires(ville):
        s = chantier.standing_en(d["x"], d["y"])
        if s == "pauvre":
            assert d["texte"] not in COSSUES, f"« {d['texte']} » en quartier pauvre, en {(d['x'], d['y'])}"
            pauvres += d["texte"] in PAUVRES
        else:
            assert d["texte"] not in PAUVRES, f"« {d['texte']} » en quartier {s}, en {(d['x'], d['y'])}"
        if s == "cossu":
            cossues += d["texte"] in COSSUES
    assert cossues >= 3, f"{cossues} enseignes cossues"
    assert pauvres >= 8, f"{pauvres} enseignes pauvres"


def test_la_facade_suit_le_standing(villes, chantier):
    """Une devanture et un logement portent le standing de leur bloc ; en pauvre,
    une vitrine sur trois est placardée (`B`), et nulle part ailleurs."""
    ville = villes[0]
    lettre = {"cossu": "+", "pauvre": "-"}
    # ⚠️ Jamais de planches au-dessus d'un guichet ou d'une machine : ils sont
    # encastrés dans la vitrine.
    machines = {(m["x"], m["y"] - 1) for m in ville["decor"]
                if m["type"] == "guichet" or m["type"].startswith("distributrice")}
    for d in ville["devantures"]:
        for i, m in enumerate(d["motifs"]):
            assert m != "B" or (d["x"] + i, d["y"]) not in machines, f"une machine sous des planches en {(d['x'] + i, d['y'])}"
    vitrines = placardees = 0
    for d in _ordinaires(ville):
        s = chantier.standing_en(d["x"], d["y"])
        assert d.get("standing") == lettre.get(s), (d["texte"], d.get("standing"), s)
        if s != "pauvre":
            assert "B" not in d["motifs"], f"{d['texte']} placardé en quartier {s}"
        elif d["texte"] != "À LOUER":
            vitrines += d["motifs"].count("W") + d["motifs"].count("B")
            placardees += d["motifs"].count("B")
    assert 0.2 <= placardees / vitrines <= 0.5, f"{placardees} vitrines placardées sur {vitrines}"
    for r in ville["residences"]:
        assert r.get("standing") == lettre.get(chantier.standing_en(r["x"], r["y"])), r


def test_un_local_a_louer_ne_s_ouvre_pas_et_ne_s_allume_pas(villes):
    ville = villes[0]
    locaux = [d for d in ville["devantures"] if d["texte"] == "À LOUER"]
    assert locaux, "pas un local à louer dans toute la ville"
    lampes = {(lampe["x"], lampe["y"]) for lampe in ville["lampes"] if lampe.get("c") == "vitrine"}
    machines = {(m["x"], m["y"] - 1) for m in ville["decor"]
                if m["type"] == "guichet" or m["type"].startswith("distributrice")}
    for d in locaux:
        assert "D" not in d["motifs"], d
        for i, m in enumerate(d["motifs"]):
            assert m != "W" or (d["x"] + i, d["y"]) in machines, f"une vitrine du local vide en {(d['x'] + i, d['y'])}"
        assert (d["x"] + d["l"] // 2, d["y"] + 1) not in lampes, f"le local à louer en {(d['x'], d['y'])} est allumé"


def test_les_commerces_montent_sans_rien_deplacer(villes, monkeypatch):
    """⚠️ LA LEÇON DE LA VAGUE. Tirés pendant la construction, les noms
    changeaient la largeur des bandeaux et les portes peintes : rampes perdues,
    barrière du cargo déplacée, dix juges tombés. Sans `monter_et_descendre`, la
    ville est la même tuile pour tuile ; les devantures ne diffèrent que par leur
    nom, leurs planches et leur standing ; les portes par leur nom ; les lampes par
    la vitrine éteinte d'un local vide."""
    # ⚠️ LES CARROSSERIES DES DEUX COTES, comme `devants.deplacer` ailleurs : posees sur
    # la ville FINIE, elles choisissent leur facade d'apres les noms et les planches (un
    # local A LOUER n'en devient pas une). La comparaison reste celle des commerces.
    monkeypatch.setattr(carte._Chantier, "poser_les_carrosseries", lambda self, ville_: [])
    ville = carte.generer()
    monkeypatch.setattr(vitrines, "monter_et_descendre", lambda chantier, ville: {})
    sans = carte.generer()
    changent = {"devantures", "residences", "portes", "lampes"}
    for cle in ville:
        if cle not in changent:
            assert json.dumps(ville[cle], sort_keys=True) == json.dumps(sans[cle], sort_keys=True), cle

    def geometrie(devanture):
        return {k: v for k, v in devanture.items() if k not in ("texte", "motifs", "standing")} | {
            "motifs": devanture["motifs"].replace("B", "W")}

    assert [geometrie(d) for d in ville["devantures"]] == [geometrie(d) for d in sans["devantures"]]
    assert [{k: v for k, v in r.items() if k != "standing"} for r in ville["residences"]] == sans["residences"]
    assert [{k: v for k, v in p.items() if k != "nom"} for p in ville["portes"]] \
        == [{k: v for k, v in p.items() if k != "nom"} for p in sans["portes"]]
    manquantes = [lampe for lampe in sans["lampes"] if lampe not in ville["lampes"]]
    assert all(lampe.get("c") == "vitrine" for lampe in manquantes), manquantes
    assert len(manquantes) == sum(1 for d in ville["devantures"] if d["texte"] == "À LOUER")


@pytest.fixture(scope="module")
def sans_eclairage():
    original = mobilier.eclairer
    mobilier.eclairer = lambda chantier, bords, solides: {}
    try:
        return carte.generer()
    finally:
        mobilier.eclairer = original


def test_la_nuit_se_redistribue(villes, sans_eclairage, chantier):
    """Un lampadaire sur trois en panne en pauvre, une plus grande portée en
    cossu — et ⚠️ pas un poteau de plus : le décor est celui d'avant."""
    ville = villes[0]

    def poteaux(v):
        return [lampe for lampe in v["lampes"] if not lampe.get("c")]

    assert [(lampe["x"], lampe["y"]) for lampe in poteaux(ville)] \
        == [(lampe["x"], lampe["y"]) for lampe in poteaux(sans_eclairage)], "des lampadaires ont bougé"
    assert [d for d in ville["decor"] if d["type"] == "lampadaire"] \
        == [d for d in sans_eclairage["decor"] if d["type"] == "lampadaire"]
    en_pauvre = [lampe for lampe in poteaux(ville) if chantier.standing_en(lampe["x"], lampe["y"]) == "pauvre"]
    en_panne = [lampe for lampe in en_pauvre if lampe.get("panne")]
    assert 0.2 <= len(en_panne) / len(en_pauvre) <= 0.5, f"{len(en_panne)} en panne sur {len(en_pauvre)}"
    for lampe in poteaux(ville):
        s = chantier.standing_en(lampe["x"], lampe["y"])
        if lampe.get("panne"):
            assert s == "pauvre", lampe
        # La portée d'un lampadaire ordinaire est celle du moteur (44 px, pas de `r`).
        if s == "cossu":
            assert lampe.get("r", 44) > 44, f"le lampadaire cossu en {(lampe['x'], lampe['y'])} ne porte pas plus loin"
        else:
            assert lampe.get("r", 44) == 44, lampe


def test_une_piece_de_commerce_suit_le_standing():
    """Un comptoir qui barre la pièce chez les pauvres, deux plantes à l'entrée
    chez les riches."""
    def piece(standing):
        sol = carte.piece_de_commerce("essai", "commerce", 10, 7, 5, standing=standing)["sol"]
        return sum(ligne.count("c") for ligne in sol), sum(ligne.count("n") for ligne in sol[-2:])

    comptoir_ordinaire, plantes_ordinaires = piece(None)
    comptoir_pauvre, plantes_pauvres = piece("pauvre")
    _, plantes_cossues = piece("cossu")
    assert comptoir_pauvre > comptoir_ordinaire, (comptoir_pauvre, comptoir_ordinaire)
    assert plantes_pauvres == 0 and plantes_ordinaires == 1 and plantes_cossues == 2


def test_la_facade_se_peint_selon_le_standing(banc):
    """Le lettrage doré en cossu, un néon à moitié éteint et des planches en
    pauvre ; le fer rouillé et les jardinières des logements."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const genres = L.B.defs.devantures.genres, murs = L.B.defs.devantures.murs, fer = L.B.defs.devantures.fer;
        const peindre = function (quoi, objet) {
            const couleurs = [], lettres = [];
            const ctx = { set fillStyle(c) { couleurs.push(c); }, get fillStyle() { return couleurs[couleurs.length - 1]; },
                          fillRect: function () {}, save: function () {}, restore: function () {}, translate: function () {}, rotate: function () {} };
            const vrai = L.Atlas.texte;
            L.Atlas.texte = function (c, t, x, y, couleur) { lettres.push(couleur); };
            try {
                if (quoi === 'devanture') L.FACADES.devanture(ctx, objet, genres[0], 0, 32);
                else L.FACADES.residence(ctx, objet, murs[0], fer, 0, 32);
            } finally { L.Atlas.texte = vrai; }
            return { couleurs: couleurs, lettres: lettres };
        };
        const d = function (standing) { return { x: 40, y: 20, l: 3, genre: 0, texte: 'ESSAI', pancarte: 0, motifs: 'WBW', standing: standing }; };
        const r = function (standing) { return { x: 40, y: 20, l: 4, etages: 3, motifs: 'FFPF', escalier: 0, porte: 2, mur: 0, balcon: 1, standing: standing }; };
        return { lettre: genres[0].lettres, chic: peindre('devanture', d('+')), miteux: peindre('devanture', d('-')),
                 logementChic: peindre('residence', r('+')), logementMiteux: peindre('residence', r('-')),
                 logement: peindre('residence', r(undefined)) };
    }""")
    assert r["chic"]["lettres"] == ["#f2d27a"], r["chic"]["lettres"]
    assert len(set(r["miteux"]["lettres"])) == 2 and r["lettre"] in r["miteux"]["lettres"], r["miteux"]["lettres"]
    assert "#7a6448" in r["miteux"]["couleurs"], "pas une planche sur la vitrine placardée"
    assert "#4a3226" in r["logementMiteux"]["couleurs"] and "#4a3226" not in r["logement"]["couleurs"], "le fer n'a pas rouillé"
    assert "#3f8d38" in r["logementChic"]["couleurs"] and "#3f8d38" not in r["logement"]["couleurs"], "pas de jardinière"


def test_un_lampadaire_en_panne_n_eclaire_pas(banc, villes):
    ville = villes[0]
    panne = next(lampe for lampe in ville["lampes"] if lampe.get("panne"))
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.heure = 0.95;
        const TT = L.TT, j = L.B.joueur;
        j.x = %d * TT + 8; j.y = %d * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        const cam = L.B.cam;
        const vues = L.Monde.lampesVisibles(cam).map(function (l) { return [Math.floor((l.x + Math.round(cam.x)) / TT), l.y + Math.round(cam.y)]; });
        return { vues: vues, n: vues.length };
    }""" % (panne["x"], panne["y"]))
    assert r["n"] > 0, "la nuit n'allume rien : le juge ne mesure rien"
    assert all(tx != panne["x"] or abs(py - (panne["y"] * 16 + 2)) > 1 for tx, py in r["vues"]), "le lampadaire en panne éclaire"


# --- 4e vague : le standing se vit ----------------------------------------------


#: Qui marche où, en toutes lettres (pas relu dans `pietons.CATALOGUE`).
STANDINGS_DES_SORTES = {"touriste": ("cossu", "ordinaire"), "jogger": ("cossu", "ordinaire"),
                        "ivrogne": ("pauvre",), "pickpocket": ("pauvre",)}


def test_qui_marche_dit_le_standing(chantier, villes):
    """Chaque sorte qui a un standing peut naître QUELQUE PART : son district et
    son standing doivent se croiser dans la ville, sinon c'est une sorte morte."""
    ville = villes[0]
    fiches = {p["slug"]: p for p in pietons.exporter()["catalogue"]}
    for slug, standings in STANDINGS_DES_SORTES.items():
        assert tuple(fiches[slug]["standings"] or ()) == standings, fiches[slug]
    for slug, fiche in fiches.items():
        if not fiche.get("standings"):
            continue
        places = 0
        for y in range(0, ville["hauteur"], 3):
            for x in range(0, ville["largeur"], 3):
                if not carte.marchable(ville["sol"][y][x]):
                    continue
                if fiche["districts"] and chantier.district_en(x, y) not in fiche["districts"]:
                    continue
                places += chantier.standing_en(x, y) in fiche["standings"]
        assert places > 20, f"{slug} n'a presque nulle part où naître ({places} tuiles)"


def test_l_ivrogne_ne_dort_pas_dans_la_rue_chic(banc, villes, chantier):
    """⚠️ Le district se lit au joueur, le standing à la TUILE où la sorte se pose :
    deux blocs voisins n'ont pas le même. On plante le joueur dans la rue chic du
    Faubourg, puis dans les Quais pauvres, et on regarde qui naît."""
    ville = villes[0]
    chic = _tuile(ville, chantier, "_", "commercial", "cossu", "faubourg")
    # ⚠️ Aux QUAIS : l'ivrogne a ses quartiers (`districts`), et La Shop n'en est
    # pas — un juge planté là ne verrait jamais personne et passerait pour rien.
    pauvre = _tuile(ville, chantier, "_", "industriel", "pauvre", "quais")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const TT = L.TT, nes = [];
        const voir = function (x, y) {
            const j = L.B.joueur;
            j.x = x * TT + 8; j.y = y * TT + 8; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
            for (let i = 0; i < 120; i++) {
                L.Entites.naitreLesSortes();
                for (const e of L.B.entites) {
                    if (e.type !== 'pieton' || !e.metier || e.vu) continue;
                    e.vu = 1;
                    nes.push({ arch: e.arch, tx: Math.floor(e.x / TT), ty: Math.floor(e.y / TT) });
                }
                o.frame(1);
            }
        };
        voir(%d, %d);
        voir(%d, %d);
        return nes;
    }""" % (*pauvre, *chic))
    vus = set()
    for ne in r:
        standings = STANDINGS_DES_SORTES.get(ne["arch"])
        if not standings:
            continue
        vus.add(ne["arch"])
        rang = chantier.standing_en(ne["tx"], ne["ty"])
        assert rang in standings, f"un {ne['arch']} en quartier {rang}, en {(ne['tx'], ne['ty'])}"
    assert vus, "aucune sorte à standing n'est née : le juge ne mesure rien"


def test_pas_de_char_rare_dans_une_rue_pauvre(banc, paquet):
    """Une décapotable dans la rue chic du Faubourg, pas devant le prêteur sur
    gages — et une minoune qui casse plus vite."""
    fiche = paquet["conduite"]["standing"]
    rares = [v["slug"] for v in paquet["vehicules"] if v.get("rare")]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const zone = L.Monde.carte.zones.find(function (z) { return z.slug === 'faubourg'; });
        const tirer = function (standing) {
            const vus = {};
            for (let i = 0; i < 400; i++) {
                const t = L.Vehicules.typeDeRue(zone, standing);
                if (t) vus[t.slug] = (vus[t.slug] || 0) + 1;
            }
            return vus;
        };
        return { rares: zone.rares, cossu: tirer('cossu'), pauvre: tirer('pauvre'), ordinaire: tirer('ordinaire') };
    }""")
    assert r["rares"], "le Faubourg ne déclare aucun char rare : le juge ne mesure rien"
    for slug in rares:
        assert slug not in r["pauvre"], f"un {slug} dans une rue pauvre"
    assert any(slug in r["cossu"] for slug in rares), f"aucun char rare dans la rue chic : {r['cossu']}"
    assert fiche["pauvre"]["usure"] < 1 and fiche["cossu"]["usure"] == 1


def test_une_minoune_a_moins_de_carrosserie(banc, villes, chantier):
    """Un char qui naît dans une rue pauvre a la carrosserie qu'il lui reste
    (`usure`) ; celui d'une rue cossue est entier. ⚠️ On suit les chars par leur
    naissance, pas par l'endroit où on les trouve : un char roule, et la bulle en
    garde d'autres, nés ailleurs."""
    ville = villes[0]
    pauvre = _tuile(ville, chantier, "_", "industriel", "pauvre", "quais")
    cossu = _tuile(ville, chantier, "_", "residentiel", "cossu", "erables")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const TT = L.TT, j = L.B.joueur, vus = {};
        const rouler = function (x, y, images) {
            j.x = x * TT + 8; j.y = y * TT + 8; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
            const nes = [];
            for (let i = 0; i < images; i++) {
                o.frame(1);
                for (const v of L.B.entites) {
                    if (v.type !== 'vehicule' || v.rails || vus[v.id]) continue;
                    vus[v.id] = 1;
                    nes.push({ usure: v.usure === undefined ? null : v.usure, part: v.vie / v.vieMax });
                }
            }
            return nes;
        };
        return { pauvre: rouler(%d, %d, 1200), cossu: rouler(%d, %d, 1200) };
    }""" % (*pauvre, *cossu))
    minounes = [v for v in r["pauvre"] if v["usure"] is not None]
    assert len(minounes) >= 3, f"presque aucune minoune dans le quartier pauvre : {r['pauvre'][:5]}"
    for v in minounes:
        assert abs(v["part"] - v["usure"]) < 0.02, v
        assert 0.5 <= v["usure"] <= 0.7, v
    entiers = [v for v in r["cossu"] if v["usure"] is None]
    assert len(entiers) >= 3, f"aucun char entier dans le quartier cossu : {r['cossu'][:5]}"
    for v in entiers:
        assert v["part"] == 1, v


def test_la_police_arrive_plus_vite_chez_les_riches(banc, paquet):
    """⚠️ Voler chez les riches paie, et ça se paie : plus de patrouilles et un
    témoin qui téléphone plus vite en cossu ; l'inverse en pauvre."""
    table = paquet["recherche"]["standing"]
    assert table["cossu"]["patrouille"] > table["ordinaire"]["patrouille"] > table["pauvre"]["patrouille"]
    assert table["cossu"]["depeche"] < table["ordinaire"]["depeche"] < table["pauvre"]["depeche"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.heure = 0.55;
        const zone = L.Monde.carte.zones.find(function (z) { return z.slug === 'faubourg'; });
        return { cossu: L.Police.agentsVoulus(zone, 'cossu'), ordinaire: L.Police.agentsVoulus(zone, 'ordinaire'),
                 pauvre: L.Police.agentsVoulus(zone, 'pauvre') };
    }""")
    assert r["cossu"] > r["ordinaire"] > r["pauvre"], r


def test_le_temoin_telephone_plus_vite_chez_les_riches(banc, villes, chantier):
    """⚠️ La table ne suffit pas : c'est `Police.maj` qui fait téléphoner le
    témoin, et le retirer de là laissait le juge d'au-dessus vert (mutation du
    21 sept. 2026). Un témoin loin de tout agent, au même âge du crime, a déjà
    appelé en cossu et pas encore en pauvre."""
    ville = villes[0]
    tuiles = {}
    for y, ligne in enumerate(ville["sol"]):
        for x, g in enumerate(ligne):
            if g == "_":
                tuiles.setdefault(chantier.standing_en(x, y), (x, y))
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const TT = L.TT, t = L.B.defs.recherche.temoins, tuiles = %s;
        t.cherche_policier_tuiles = 0;           // aucun agent assez proche : il telephone
        L.B.rng = function () { return 0; };     // des que son delai est passe
        const seuil = t.delai_depeche_s * 60;
        const appelle = function (standing, part) {
            const e = L.Entites.creerPieton(tuiles[standing][0] * TT + 8, tuiles[standing][1] * TT + 8,
                                            L.Entites.archetypeDeRue());
            e.etat = 'temoin';
            e.crime = { t: L.B.t - Math.round(seuil * part), rapporte: false, gravite: 0, x: e.x, y: e.y };
            L.Police.maj();
            const a = e.crime.rapporte;
            L.Entites.retirer(e);
            return a;
        };
        const vus = {};
        for (const part of [0.8, 1.3, 1.8]) {
            vus[part] = {};
            for (const s of ['cossu', 'ordinaire', 'pauvre']) vus[part][s] = appelle(s, part);
        }
        return vus;
    }""" % json.dumps(tuiles))
    assert r["0.8"] == {"cossu": True, "ordinaire": False, "pauvre": False}, r
    assert r["1.3"] == {"cossu": True, "ordinaire": True, "pauvre": False}, r
    assert r["1.8"] == {"cossu": True, "ordinaire": True, "pauvre": True}, r


def test_les_tiroirs_d_un_logement_disent_le_quartier(banc, paquet):
    parts = paquet["economie"]["fouille_standing"]
    assert parts["cossu"] > parts["ordinaire"] > parts["pauvre"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.rng = function () { return 0.5; };
        return { cossu: L.Missions.gainDeFouille('cossu'), ordinaire: L.Missions.gainDeFouille('ordinaire'),
                 pauvre: L.Missions.gainDeFouille('pauvre'), rien: L.Missions.gainDeFouille(null) };
    }""")
    assert r["cossu"] > r["ordinaire"] > r["pauvre"] >= 1, r
    assert r["rien"] == r["ordinaire"], "sans standing, la fouille reste celle d'avant"
