"""Les lignes d'autobus, jugées en Python : le tracé, les arrêts, les abribus.

Demande de Martin (16 sept. 2026) : « des arrêts d'autobus pour se déplacer
réellement d'un arrêt à l'autre selon un tracé, et des bus qui passent aux
arrêts aussi ».

⚠️ **Python trace, le navigateur roule.** `vehicules.js` ne choisit jamais une
rue : tout ce qui peut rater — un pas à contresens, une tuile que la ville ferme
un jour, un demi-tour au milieu d'un carrefour, un abribus devant une porte — se
juge ici, sur la ville que le navigateur reçoit.
"""

import pytest

from app import autobus, carte


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


def boucles(ville):
    return {ligne["numero"]: autobus.derouler(ligne["trace"]) for ligne in ville["autobus"]["lignes"]}


def arrets(ville):
    return [autobus.detail(ville, rang) for rang in range(len(ville["autobus"]["arrets"]))]


def test_chaque_ligne_est_une_boucle_qui_obeit_aux_fleches(ville):
    """Chaque pas du tracé est un pas que `carte.suivre_voie` permet — le même
    juge que la connexité des rues — et le dernier ramène au premier."""
    for numero, tuiles in boucles(ville).items():
        assert len(tuiles) > 200, f"ligne {numero} : {len(tuiles)} tuiles, ce n'est pas une ligne"
        for i, (x, y) in enumerate(tuiles):
            suivante = tuiles[(i + 1) % len(tuiles)]
            assert suivante in carte.suivre_voie(ville, x, y), (
                f"ligne {numero}, pas {i} : {(x, y)} -> {suivante} n'est pas permis")


def test_aucun_trace_ne_passe_la_ou_la_ville_peut_fermer(ville):
    """⚠️ Les entraves, les rues barrées, les bris d'aqueduc et les barrières
    qui arrêtent les chars sont des LISTES : un tracé qui en traverse une verrait
    un jour son autobus devant des cônes, et il ne saurait pas quoi faire."""
    fermables = set()
    rectangles = ville["fermetures"] + ville["entraves"] + ville["ponts"]
    rectangles += [b for b in ville["barrieres"] if "vehicule" in b["arrete"]]
    for r in rectangles:
        fermables |= {(x, y) for x in range(r["x"], r["x"] + r["l"]) for y in range(r["y"], r["y"] + r["h"])}
    fermables |= {(a["x"], a["y"]) for a in ville["aqueducs"]}
    for numero, tuiles in boucles(ville).items():
        dedans = sorted(set(tuiles) & fermables)
        assert not dedans, f"ligne {numero} passe sur {len(dedans)} tuiles fermables, dont {dedans[:3]}"


def test_une_seule_manoeuvre_par_boite_et_comme_le_trafic(ville):
    """⚠️ Deux virages dans la même boîte, c'est un DEMI-TOUR au milieu du
    carrefour : l'autobus en travers de la voie d'en face attendait le char qui
    l'attendait. Une boîte se traverse donc tout droit, avec UN virage — là où il
    mène à une voie (`Vehicules.peutSortir`) : à gauche au fond, pas à l'entrée —
    ou avec UN déport : une tuile de côté, et le même cap en sortant."""
    reseau = autobus._Reseau(ville)
    for numero, tuiles in boucles(ville).items():
        n = len(tuiles)
        depart = next(i for i in range(n) if ville["voie"][tuiles[i][1]][tuiles[i][0]] != "+")
        i = depart
        while i < depart + n:
            b = tuiles[i % n]
            if ville["voie"][b[1]][b[0]] != "+":
                i += 1
                continue
            # La boîte, de la tuile d'avant à la tuile d'après.
            j = i
            while ville["voie"][tuiles[j % n][1]][tuiles[j % n][0]] == "+":
                j += 1
            chemin = [tuiles[k % n] for k in range(i - 1, j + 1)]
            pas = [(q[0] - p[0], q[1] - p[1]) for p, q in zip(chemin, chemin[1:])]
            changements = [k for k in range(1, len(pas)) if pas[k] != pas[k - 1]]
            if len(changements) == 1:
                k = changements[0]
                t = chemin[k]
                assert reseau.peut_sortir(t[0], t[1], pas[k]), f"ligne {numero} tourne en {t} vers un mur"
            elif changements:
                k1, k2 = changements[0], changements[-1]
                assert len(changements) == 2 and k2 == k1 + 1 and pas[k2] == pas[k1 - 1], (
                    f"ligne {numero} manœuvre {len(changements)} fois dans la boîte de {chemin[1]} : {pas}")
            i = j


def test_chaque_arret_longe_le_trottoir_sur_une_voie_droite(ville):
    """Un autobus fait trois tuiles : arrêté à cheval sur une ligne d'arrêt ou un
    passage piéton, il bloquerait le carrefour. Le trottoir est à sa DROITE (on
    roule à droite), l'abri juste derrière."""
    sol, voie = ville["sol"], ville["voie"]
    boites = {(x, y) for i in ville["intersections"]
              for x in range(i["x"], i["x"] + i["l"]) for y in range(i["y"], i["y"] + i["h"])}
    for a in arrets(ville):
        dx, dy = autobus.PAS[a["sens"]]
        rx, ry = autobus.a_droite(dx, dy)
        for k in range(-autobus.ARRETS["droit"], autobus.ARRETS["droit"] + 1):
            tx, ty = a["x"] + dx * k, a["y"] + dy * k
            assert voie[ty][tx] == a["sens"] and (tx, ty) not in boites, f"{a['nom']} : pas une voie droite en {(tx, ty)}"
            assert sol[ty + ry][tx + rx] == ".", f"{a['nom']} : pas de trottoir à droite en {(tx, ty)}"
        assert sol[a["abri"][1]][a["abri"][0]] in ("_", ","), f"{a['nom']} : l'abri n'est pas derrière le trottoir"


#: Le dessin de l'abri selon le côté où est la RUE, vue de l'abri. ⚠️ Écrit ici
#: en toutes lettres, pas relu dans `autobus.ABRIS` : un juge qui relit la table
#: qu'il juge ne rougit jamais.
REGARDE = {(0, 1): "abribus", (0, -1): "abribus_nord", (1, 0): "abribus_est", (-1, 0): "abribus_ouest"}


def test_chaque_arret_a_son_abribus_qui_regarde_la_rue(ville):
    decor = {(d["x"], d["y"]): d["type"] for d in ville["decor"]}
    for a in arrets(ville):
        rue = (a["x"] - a["quai"][0], a["y"] - a["quai"][1])
        assert decor.get(tuple(a["abri"])) == REGARDE[rue], (
            f"{a['nom']} : {decor.get(tuple(a['abri']))} au lieu de {REGARDE[rue]}")


def test_un_abribus_n_est_jamais_devant_une_porte(ville):
    """« Jamais rien devant la porte d'une maison, d'un commerce ou autre » — ni
    juste à côté : on sort d'une porte sur deux tuiles de profondeur."""
    devant = set()
    for p in ville["portes"]:
        for j in (1, 2):
            for i in (-1, 0, 1):
                devant.add((p["x"] + i, p["y"] + j))
    for a in arrets(ville):
        assert tuple(a["abri"]) not in devant, f"l'abribus de {a['nom']} est devant une porte"


def test_le_parvis_du_terminus_reste_nu(ville):
    """Le car de l'ouverture y dépose le cousin, qui marche jusqu'à la porte."""
    nus = autobus.parvis(ville)
    for a in arrets(ville):
        dx, dy = autobus.PAS[a["sens"]]
        for k in (-1, 0, 1):
            t = (a["abri"][0] + dx * k, a["abri"][1] + dy * k)
            assert k != 0 or t not in nus, f"l'abribus de {a['nom']} est sur le parvis du terminus"


def test_les_arrets_sont_a_leur_place_dans_la_boucle(ville):
    tuiles = boucles(ville)
    par_id = {a["id"]: a for a in arrets(ville)}
    for ligne in ville["autobus"]["lignes"]:
        n = len(tuiles[ligne["numero"]])
        indices = [i for _id, i in ligne["arrets"]]
        assert indices == sorted(indices), f"ligne {ligne['numero']} : arrêts dans le désordre"
        for id_, i in ligne["arrets"]:
            a = par_id[id_]
            assert tuiles[ligne["numero"]][i] == (a["x"], a["y"])
            assert ligne["numero"] in a["lignes"]
        # ⚠️ Assez d'arrêts pour qu'on s'en serve, pas un par pâté de maisons.
        ecarts = [(indices[(k + 1) % len(indices)] - indices[k]) % n for k in range(len(indices))]
        assert min(ecarts) >= 8, f"ligne {ligne['numero']} : deux arrêts à {min(ecarts)} tuiles"
        assert max(ecarts) <= 2 * autobus.ARRETS["ecart"][1], f"ligne {ligne['numero']} : {max(ecarts)} tuiles sans arrêt"


def test_chaque_ligne_part_du_terminus_et_sert_ses_lieux(ville):
    """Un arrêt porte le nom de chaque lieu que la ligne promet de servir, et il
    est à deux pas de sa porte."""
    par_id = {a["id"]: a for a in arrets(ville)}
    lieux = {p["slug"]: p for p in ville["points_interet"]}
    for fiche, ligne in zip(autobus.LIGNES, ville["autobus"]["lignes"]):
        assert fiche["passe_par"][0] == "terminus"
        servis = [par_id[id_] for id_, _i in ligne["arrets"]]
        for slug in fiche["passe_par"]:
            lieu = lieux[slug]
            proches = [a for a in servis if a["nom"].startswith(lieu["nom"])]
            assert proches, f"ligne {fiche['numero']} ne s'arrête pas à {lieu['nom']}"
            a = proches[0]
            assert abs(a["quai"][0] - lieu["x"]) + abs(a["quai"][1] - lieu["y"]) <= autobus.ARRETS["rayon_nom"] + 2


def test_les_arrets_ont_des_noms_qu_on_peut_dire(ville):
    """« 3e Rue / 5e Avenue » ou le nom d'un lieu — jamais deux fois le même."""
    noms = [a["nom"] for a in ville["autobus"]["arrets"]]
    assert len(noms) == len(set(noms)), "deux arrêts portent le même nom"
    assert autobus.ordinal(1) == "1re" and autobus.ordinal(3) == "3e"
    assert any(" Rue / " in n or " Avenue / " in n for n in noms)


def test_l_horaire_fait_passer_les_autobus(ville):
    """Assez d'autobus pour qu'on n'attende pas une journée : un par tant de
    tuiles de tracé, deux au moins par ligne."""
    horaire = ville["autobus"]["horaire"]
    for ligne in ville["autobus"]["lignes"]:
        assert ligne["autobus"] >= 2
        attente_images = ligne["longueur"] * 16 / horaire["vitesse_px"] / ligne["autobus"]
        assert attente_images / 60 < 90, f"ligne {ligne['numero']} : un autobus toutes les {attente_images / 60:.0f} s"


def test_derouler_rend_ce_que_coins_a_plie(ville):
    for tuiles in boucles(ville).values():
        assert autobus.derouler(autobus.coins(tuiles)) == tuiles


def test_les_lignes_ne_deplacent_rien_de_la_ville(monkeypatch):
    """⚠️ Leur propre ordre, APRÈS la ville : une ligne de plus ne déplace ni un
    arbre, ni un paquet, ni une enseigne. Sans les lignes ni le mobilier, la ville
    est la même tuile pour tuile, et le décor d'avant est le même, dans le même
    ordre — les nouveaux meubles ne font que s'ajouter au bout.

    ⚠️ La saleté se déplace APRÈS les lignes (`salete.deplacer`) et contourne
    leurs abribus, comme le mobilier : on la retire des deux villes."""
    from app import metro, mobilier, salete
    monkeypatch.setattr(salete, "deplacer", lambda chantier, ville, graine: {})
    avec = carte.generer()
    monkeypatch.setattr(autobus, "tracer", lambda chantier, ville: {"lignes": [], "arrets": [], "horaire": {}})
    monkeypatch.setattr(mobilier, "semer", lambda chantier, ville, graine: {})
    # ⚠️ Le metro se creuse ENTRE les lignes et le mobilier : sans les abribus, ses
    # edicules tomberaient ailleurs. Il part donc avec eux.
    monkeypatch.setattr(metro, "creuser", lambda chantier, ville: {})
    sans = carte.generer()
    for cle in sans:
        # ⚠️ La tournée des éboueurs se trace APRÈS tout le reste, sur les voies et
        # loin des abribus et du décor : sans eux, ses bacs tombent ailleurs. Elle ne
        # pose rien dans la ville (`test_eboueurs.py`), elle en dépend seulement.
        # Le tramway aussi : ses arrêts se tiennent loin des abribus.
        if cle in ("decor", "autobus", "metro", "eboueurs", "tramway"):
            continue
        assert avec[cle] == sans[cle], f"« {cle} » a bougé"
    assert avec["decor"][:len(sans["decor"])] == sans["decor"]
    ajoutes = {d["type"] for d in avec["decor"][len(sans["decor"]):]}
    usage = {"parcometre", "boite_aux_lettres", "bac_recyclage", "palettes", "benne"}   # le mobilier de l'usage
    assert ajoutes <= {"arbre", "bac_fleurs", *usage, *autobus.ABRIS.values(), *autobus.BANCS.values(),
                       *metro.EDICULES.values()}, ajoutes
