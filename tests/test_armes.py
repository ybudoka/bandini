import re
from pathlib import Path

from app import armes

RACINE = Path(__file__).resolve().parent.parent


def test_les_poings_d_abord_et_gratuits():
    premiere = armes.CATALOGUE[0]
    assert premiere["slug"] == "poings" and premiere["prix"] == 0 and premiere["type"] == "melee"


def test_catalogue_coherent():
    slugs = [a["slug"] for a in armes.CATALOGUE]
    assert len(slugs) == len(set(slugs))
    for a in armes.CATALOGUE:
        assert a["type"] in armes.TYPES
        assert a["degats"] >= 0 and a["portee"] > 0 and a["cadence"] >= 1
        if a["type"] == "tir":
            assert a["chargeur"] and a["munitions_max"] and a["chargeur"] <= a["munitions_max"]
            assert a["vitesse_projectile"] > 0
        if a["type"] == "melee":
            assert a["chargeur"] is None
        if a["usures"]:
            assert a["prix"] == 0, "une arme improvisee ne s'achete pas"


def test_les_prix_montent_dans_l_ordre_d_achat():
    prix = [a["prix"] for a in armes.achetables()]
    assert prix == sorted(prix)
    assert armes.par_slug("fusil")["plombs"] == 6
    assert armes.ORDRE_CYCLE[0] == "poings"


def test_chaque_arme_a_son_son():
    """Un son PAR ARME : jusqu'au 13 sept. 2026, tout jouait le coup de poing,
    le pistolet et le fusil compris. Le slug doit exister au catalogue audio
    (`test_audio` verifie de son cote que le navigateur a l'effet, avec repli)."""
    from app import audio

    for a in armes.CATALOGUE:
        assert a["son"] in audio.SLUGS, f"{a['slug']} : son {a['son']!r} inconnu de audio.CATALOGUE"
    assert armes.par_slug("poings")["son"] == "coup", "les poings gardent le coup de poing"
    sons = [a["son"] for a in armes.CATALOGUE]
    assert len(sons) == len(set(sons)), "deux armes qui font le meme bruit : on ne sait pas laquelle on tient"


def test_le_poing_americain_cogne_un_peu_plus_fort_que_les_poings():
    """Demande de Martin (16 sept. 2026) : « les hommes de Sal sont a main nue
    ou poing americain (un peu plus fort) ». UN PEU : au-dessus des poings,
    sous le baton qu'ils portaient jusque-la. Et c'est encore un coup de
    poing — il ASSOMME, comme les poings et rien d'autre : sans ca, ramasser
    celui d'un homme de Sal ferait d'un KO un meurtre, et la difference vaut
    deux etoiles."""
    poings, americain, batte = (armes.par_slug(s) for s in ("poings", "poing_americain", "batte"))
    assert americain and americain["type"] == "melee"
    assert poings["degats"] < americain["degats"] < batte["degats"], (
        f"poings {poings['degats']}, poing americain {americain['degats']}, baton {batte['degats']}"
    )
    assert [a["slug"] for a in armes.CATALOGUE if a["assomme"]] == ["poings", "poing_americain"]
    assert not americain["renverse"] and not americain["saigne"], "un poing ne projette ni ne coupe"
    assert not americain["usures"], "l'acier ne casse pas au quatrieme coup"


def test_le_poing_americain_s_achete_chez_gus():
    """Martin (17 sept. 2026) : « on devrait aussi pouvoir l'acheter ». Jusque-la
    il valait 0 $ et ne se vendait nulle part : on ne l'avait qu'en couchant un
    homme de Sal. Chez Gus, EN TETE de vitrine : il cogne a peine plus que les
    poings, il coute donc moins que tout ce que Gus vend d'autre — et la vitrine
    se lit du moins cher au plus cher, comme le catalogue."""
    from app import magasins

    americain = armes.par_slug("poing_americain")
    gus = magasins.par_slug("armurerie")
    assert americain in armes.achetables(), "le poing americain ne se vend pas"
    assert gus["articles"][0] == "poing_americain", gus["articles"]
    prix = [armes.par_slug(s)["prix"] for s in gus["articles"]]
    assert prix == sorted(prix) and len(set(prix)) == len(prix), f"la vitrine de Gus : {prix}"
    assert americain["prix"] == min(a["prix"] for a in armes.achetables())


def test_chaque_arme_qu_on_tient_a_son_dessin():
    """L'arme se voit dans la main et dans la roue : `OBJETS[def.sprite]`. Une
    arme sans dessin retombe EN SILENCE sur la barre grise du `defaut` — le
    poing americain d'un homme de Sal aurait ete le meme trait gris qu'un
    tuyau. Les poings, eux, ne se dessinent pas : c'est la main."""
    source = (RACINE / "static" / "js" / "sprites.js").read_text(encoding="utf-8")
    bloc = source[source.index("const OBJETS = {"):]
    bloc = bloc[:bloc.index("\n};")]
    dessins = set(re.findall(r"^\s+([a-z_]+): function", bloc, re.M))
    for a in armes.CATALOGUE:
        if a["slug"] != "poings":
            assert a["sprite"] in dessins, f"{a['slug']} : pas de OBJETS.{a['sprite']} dans sprites.js"


def test_trois_armes_a_feu_qui_repondent_a_trois_questions():
    """« Ils sont trois » : la mitraillette, la seule automatique, plus rapide
    et moins forte par balle que le pistolet, et dont la dispersion s'ouvre.
    « Il est loin » : la carabine, la plus longue portee, sans dispersion, un
    passant d'une balle. « Ils sont groupes » : le Molotov, en cloche, et le
    seul qui laisse du feu. Une arme de plus sans raison de la choisir
    n'ajoute rien — c'est la fiche du plan."""
    mit, car, mol, pis = (armes.par_slug(s) for s in ("mitraillette", "carabine", "molotov", "pistolet"))
    assert [a["slug"] for a in armes.CATALOGUE if a["auto"]] == ["mitraillette"]
    assert mit["dispersion_max"] > mit["dispersion"] > 0
    assert mit["cadence"] < pis["cadence"] and mit["degats"] < pis["degats"]
    tirs = [a for a in armes.CATALOGUE if a["type"] == "tir"]
    assert car["portee"] == max(a["portee"] for a in tirs) and car["dispersion"] == 0
    assert car["degats"] >= max(a["degats"] for a in armes.CATALOGUE if a["slug"] != "carabine")
    assert mol["cloche"] is True and mol["feu_s"] > 0
    assert [a["slug"] for a in armes.CATALOGUE if a["feu_s"]] == ["molotov"]
    for a in armes.CATALOGUE:
        if not a["auto"]:
            assert a["dispersion_max"] == a["dispersion"], f"{a['slug']} : une dispersion qui s'ouvre sans rafale"
    assert armes.REGLES["rafale_images"] > 0
    assert armes.REGLES["incendie"]["rayon_px"] > 0 and armes.REGLES["incendie"]["degats_par_seconde"] > 0


def test_aucune_portee_ne_depasse_ce_que_l_ecran_montre():
    """La vue fait `VW` px et le joueur est au milieu : au-dela de VW/2 on tire
    sur ce qu'on ne voit pas. ⚠️ La borne se LIT dans base.js, elle n'est pas
    recopiee ici — le jour ou la vue change, ce juge suit."""
    source = (RACINE / "static" / "js" / "base.js").read_text(encoding="utf-8")
    vw = int(re.search(r"^const VW = (\d+);", source, re.M).group(1))
    for a in armes.CATALOGUE:
        if a["type"] == "tir":
            assert a["portee"] <= vw // 2, f"{a['slug']} : {a['portee']} px, l'ecran en montre {vw // 2}"


def test_un_coup_de_feu_fait_du_bruit_et_le_marche_noir_le_vend():
    """Toute arme qui DETONE (a poudre : type tir, des etoiles a la sortir, pas
    une bouteille) declare le rayon `bruit` que la police entend. La fronde et
    le Molotov ne detonent pas. Et ce qui fait du bruit se vend au marche
    noir, munitions comprises — les trois nouvelles n'ont pas de vitrine chez
    Gus."""
    from app import magasins

    mn = magasins.MARCHE_NOIR
    gus = magasins.par_slug("armurerie")
    for a in armes.CATALOGUE:
        detone = a["type"] == "tir" and a["etoiles_usage"] > 0 and not a["feu_s"]
        if detone:
            assert a["bruit"] > 0, a["slug"]
            assert a["slug"] in mn["articles"] and a["slug"] in mn["munitions"], a["slug"]
        else:
            assert a["bruit"] == 0, f"{a['slug']} ne detone pas"
    for slug in ("molotov", "mitraillette", "carabine"):
        assert slug in mn["articles"] and slug in mn["munitions"]
        assert slug not in gus["articles"] and slug not in gus["munitions"], f"{slug} : pas de vitrine"
    assert armes.par_slug("carabine")["bruit"] > armes.par_slug("pistolet")["bruit"]


def test_les_regles_des_armes_voyagent():
    from app import definitions

    paquet = definitions.assembler()
    assert paquet["armes_regles"] == armes.REGLES
    for a in paquet["armes"]:
        for cle in ("auto", "dispersion_max", "bruit", "feu_s", "assomme"):
            assert cle in a, f"{a['slug']} : {cle}"
