"""Le propriétaire qui sort quand on dévisse son enseigne (P4, des choses à collectionner, vague 6) : qui sort de
chaque commerce, et comment, se lit À L'EMPREINTE du commerce — jamais un dé ; il sort par une vraie porte de la
devanture ; personne ne sort d'une porte tenue ; ce qu'il crie voyage avec les collections, avec deux voix de passant.
"""

import json
import pathlib

from app import audio, devisser, interpretation
from tests import villes

#: Ce que l'empreinte donne sur la ville livrée, écrit EN TOUTES LETTRES (un juge qui relirait `devisser.proprio` changerait
#: avec lui) : le tempérament, le genre, la vis du réveil et l'habit. Les cinq autres ne sortent jamais.
ATTENDU = {
    "bingo": ("court", "f", 3, "pyjama"),
    "clairon": ("appelle", "f", 4, "pyjama"),
    "lave_auto": ("appelle", "f", 3, "pyjama"),
    "quilles": ("court", "h", 2, "robe"),
    "cantine": ("appelle", "h", 2, "robe"),
    "mah_jong": ("appelle", "h", 2, "robe"),
    "ti_pout": ("court", "f", 2, "robe"),
}


def _export():
    v = villes.generer()
    return v, devisser.exporter(devisser.poser(v))


def test_qui_sort_de_chaque_commerce_est_ecrit_a_son_empreinte():
    _, out = _export()
    vus = {f["slug"]: (f["proprio"]["humeur"], f["proprio"]["genre"], f["proprio"]["reveil"], f["proprio"]["tenue"]["habit"])
           for f in out["liste"] if f.get("proprio")}
    assert vus == ATTENDU
    # Les deux tempéraments et les deux habits, au moins une fois chacun : sinon Martin ne verrait qu'une moitié.
    assert {h for h, *_ in vus.values()} == {"court", "appelle"}
    assert {t[3] for t in vus.values()} == {"pyjama", "robe"}


def test_personne_ne_sort_d_une_porte_tenue_ni_d_une_devanture_sans_porte():
    """Chez Ti-Paul, c'est Ti-Paul ; au Dragon d'or, le portier du casino. ⚠️ Écrit à la main, en synthétique : ces deux
    commerces ont une vraie porte, et l'empreinte seule y ferait sortir quelqu'un (Ti-Paul : `court`, le Dragon d'or :
    `appelle`)."""
    assert devisser.proprio("tipaul", [10, 10]) is None
    assert devisser.proprio("dragon_or", [10, 10]) is None
    assert devisser.proprio("bingo", None) is None, "une devanture sans porte fait sortir quelqu'un"
    assert devisser.proprio("bingo", [10, 10]) is not None


def test_il_sort_par_une_porte_de_sa_devanture():
    v, out = _export()
    devs = {(d["x"], d["y"]): d for d in v["devantures"]}
    for f in out["liste"]:
        if not f.get("proprio"):
            continue
        px, py = f["proprio"]["porte"]
        d = devs[(f["x"], f["y"])]
        assert py == d["y"] and d["x"] <= px < d["x"] + d["l"], f["slug"]
        assert v["sol"][py][px] in ("D", "d"), f"{f['slug']} : il sortirait d'un mur ({v['sol'][py][px]})"


def test_l_empreinte_ne_tire_aucun_de():
    source = pathlib.Path(devisser.__file__).read_text(encoding="utf-8")
    assert "import random" not in source and "random." not in source
    assert devisser.proprio("cantine", [1, 2]) == devisser.proprio("cantine", [1, 2])


def test_ce_qu_il_crie_voyage_avec_les_collections_et_deux_voix_de_passant(paquets):
    defs = paquets.definitions.corps.decode("utf-8")
    col = json.loads(paquets.collections.corps)
    p = col["enseignes"]["proprio"]
    for r in devisser.REPLIQUES_PROPRIO:
        assert r["texte"] not in defs, "le proprio pèse sur le premier écran"
        assert p["repliques"][r["qui"]][r["cle"]] == r["texte"]
        assert interpretation.JEU[f"proprio-{r['qui']}-{r['cle']}"] == r["jeu"]
    assert {s["prefixe"] for s in p["voix"]} == {"proprio-h-", "proprio-f-"}
    for qui in ("h", "f"):
        assert set(p["repliques"][qui]) == {"sort", "court", "appelle", "lache"}, qui
    voix = {v["slug"]: v["voix"] for v in audio.voix_proprio()}
    assert voix["proprio-h-sort"] == audio.VOIX_PAR_GENRE["homme"]
    assert voix["proprio-f-sort"] == audio.VOIX_PAR_GENRE["femme"]
    assert all(v["slug"] in {x["slug"] for x in audio.toutes_les_voix()} for v in audio.voix_proprio())
