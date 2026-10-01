"""Les frénésies (P4) : où dorment les icônes, ce qu'elles prêtent, ce qu'elles paient.

⚠️ Les règles sont écrites ICI en toutes lettres (la ruelle, le district, l'écart aux
paquets, le chemin jusqu'à la rue) : un juge qui relirait `frenesies.CACHETTES` changerait
avec la constante qu'il garde.
"""

import json
import statistics

import pytest

from app import armes, carte, frenesies, nord, pietons

TERRES = {"faubourg", "erables", "shop", "quais", "pointe", "friches", "canton", "gare"}


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def test_une_frenesie_par_district_de_terre(ville):
    districts = [f["district"] for f in ville["frenesies"]]
    assert sorted(districts) == sorted(TERRES), f"une frénésie par district de terre, pas {districts}"
    assert len({f["slug"] for f in ville["frenesies"]}) == len(TERRES)
    # La ville d'avant la bande nord n'en a que cinq : ce qui n'a pas de district ne se pose pas.
    avant = carte.generer(nord=False)
    assert sorted(f["district"] for f in avant["frenesies"]) == sorted(TERRES - {"friches", "canton", "gare"})


def test_l_icone_dort_dans_une_ruelle_libre_de_son_district(ville):
    zones = ville["zones"]
    sol = ville["sol"]
    cours = [z for z in zones if z.get("gang")]
    pris = {(o["x"], o["y"]) for cle in ("decor", "paquets", "scenes", "ambulants", "reclames", "points_interet")
            for o in ville.get(cle) or []}
    for f in ville["frenesies"]:
        x, y = f["x"], f["y"]
        d = next(z for z in zones if z["slug"] == f["district"] and not z.get("gang"))
        assert d["x"] <= x < d["x"] + d["l"] and d["y"] <= y < d["y"] + d["h"], f"{f['slug']} hors de son district"
        # Une ruelle ; la friche ou l'herbe seulement là où le district n'a pas une ruelle.
        ruelles = any(sol[yy][xx] == "x" for yy in range(d["y"], d["y"] + d["h"])
                      for xx in range(d["x"], d["x"] + d["l"]))
        assert sol[y][x] == "x" or (not ruelles and sol[y][x] in ";,"), f"{f['slug']} sur « {sol[y][x]} »"
        assert not any(c["x"] <= x < c["x"] + c["l"] and c["y"] <= y < c["y"] + c["h"] for c in cours), \
            f"{f['slug']} dans une cour de gang"
        assert (x, y) not in pris, f"{f['slug']} sur un décor, un paquet ou un lieu"
        assert all(max(abs(p["x"] - x), abs(p["y"] - y)) >= 8 for p in ville["paquets"]), \
            f"{f['slug']} collée à un paquet caché"


def _fiche(slug):
    return next(f for f in frenesies.FRENESIES if f["slug"] == slug)


def test_un_paquet_cache_chasse_l_icone_a_huit_tuiles(ville):
    """⚠️ Sur la ville livrée, aucun paquet n'est près d'une icône : le cas s'écrit à la main — un
    paquet posé à trois tuiles de la cachette la fait partir à huit tuiles au moins de lui."""
    f = next(q for q in ville["frenesies"] if q["slug"] == "cravates")
    px, py = f["x"] + 3, f["y"]
    v = dict(ville, paquets=list(ville["paquets"]) + [{"numero": 99, "x": px, "y": py}])
    ailleurs = frenesies.cachette(v, _fiche("cravates"))
    assert ailleurs and max(abs(ailleurs[0] - px), abs(ailleurs[1] - py)) >= 8, ailleurs


def test_une_ruelle_muree_n_est_pas_une_cachette(ville):
    """⚠️ Même chose pour le chemin : la cachette livrée se rejoint déjà. On l'emmure (des murs autour,
    sur une copie du sol) — elle ne doit plus être choisie."""
    f = next(q for q in ville["frenesies"] if q["slug"] == "cravates")
    sol = [list(r) for r in ville["sol"]]
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx or dy:
                sol[f["y"] + dy][f["x"] + dx] = "B"
    v = dict(ville, sol=["".join(r) for r in sol])
    assert frenesies.cachette(v, _fiche("cravates")) != (f["x"], f["y"]), "une ruelle emmurée reste la cachette"


def test_on_rejoint_chaque_icone_a_pied_depuis_la_rue(ville):
    """De l'icône, un piéton atteint un trottoir ou une rue sans passer un mur ni une clôture."""
    sol = ville["sol"]
    for f in ville["frenesies"]:
        vus, bord, atteint = {(f["x"], f["y"])}, [(f["x"], f["y"])], False
        for _ in range(40):
            suivant = []
            for (cx, cy) in bord:
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if (nx, ny) in vus:
                        continue
                    fiche = carte.LEGENDE.get(sol[ny][nx], {})
                    if fiche.get("route") or fiche.get("trottoir"):
                        atteint = True
                    if carte.solidite(sol[ny][nx]) in (0, 3):
                        vus.add((nx, ny))
                        suivant.append((nx, ny))
            bord = suivant
            if atteint or not bord:
                break
        assert atteint, f"l'icône {f['slug']} ({f['x']},{f['y']}) ne se rejoint pas à pied"


def test_une_arme_du_catalogue_une_cible_qui_existe():
    catalogue = {a["slug"]: a for a in armes.CATALOGUE}
    gangs = {g["slug"] for g in pietons.GANGS}
    for f in frenesies.FRENESIES:
        assert f["arme"] in catalogue, f"{f['slug']} prête une arme hors catalogue"
        a = catalogue[f["arme"]]
        assert a["prix"] > 0 and not a["foire"] and a["type"] != "jet", f"{f['slug']} prête un jouet"
        assert f["cible"] in ("gang", "chars")
        if f["cible"] == "gang":
            assert f["gang"] in gangs, f"{f['slug']} vise une gang qui n'existe pas"
        else:
            # Une balle ne mord pas la tôle d'un char vide : seul le feu du Molotov le fait.
            assert a["feu_s"] > 0, f"{f['slug']} détruit des chars sans une arme qui les brûle"
        assert f["n"] > 0 and 30 <= f["chrono_s"] <= 300


def test_aucune_frenesie_ne_paie_mieux_qu_une_mission(paquet):
    recompenses = [m.get("recompense", 0) for m in paquet["missions"]]
    mediane = statistics.median(recompenses)
    for f in frenesies.FRENESIES:
        assert 0 < f["prime"] <= mediane, f"{f['slug']} paie {f['prime']} $, plus que la mission médiane ({mediane} $)"
    assert frenesies.REGLE["bonus_toutes"] <= max(recompenses)


def test_les_frenesies_ne_deplacent_rien(monkeypatch):
    """Posées en tout dernier et sans un dé : la ville avec elles est la ville sans elles, à l'octet."""
    vu = {}
    vraie = frenesies.poser

    def espion(v):
        vu["avant"] = json.dumps(v, sort_keys=True)
        out = vraie(v)
        vu["apres"] = json.dumps(v, sort_keys=True)
        return out

    monkeypatch.setattr(frenesies, "poser", espion)
    v = carte.generer()
    # ⚠️ Des booléens, pas deux chaînes de plusieurs Mo : pytest en calculerait le diff pendant des minutes.
    avant, apres = json.loads(vu["avant"]), json.loads(vu["apres"])
    touchees = sorted(k for k in set(avant) | set(apres) if avant.get(k) != apres.get(k))
    assert not touchees, f"poser les frénésies a touché la ville : {touchees}"
    # ⚠️ Les cartes de hockey (`collectionner`) se posent APRÈS elles, et lisent leurs icônes : hors de la comparaison.
    # Et la régate (i07), posée en tout dernier : sa propre clé, rien d'autre (`test_regate`).
    sans = {k: val for k, val in v.items() if k not in ("frenesies", "frenesies_regle", "collections", "regate")}
    derniere = json.dumps(sans, sort_keys=True) == vu["avant"]
    assert derniere, "les frénésies ne se posent pas en dernier"


def test_la_bande_nord_sait_les_decaler():
    assert "frenesies" in nord.DECALAGES and "frenesies_regle" in nord.DECALAGES


def test_elles_voyagent_dans_le_paquet(paquet):
    assert paquet["carte"]["frenesies"], "les frénésies ne voyagent pas avec la carte"
    assert paquet["carte"]["frenesies_regle"]["rayon_px"] > 0
