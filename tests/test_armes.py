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
    # ⚠️ Ce qui SAUTE (`lance`, `pose`) n'entre pas dans la comparaison : ses degats sont
    # ceux du centre d'une explosion qui baisse avec la distance, pas une balle.
    assert car["degats"] >= max(a["degats"] for a in armes.CATALOGUE
                                if a["slug"] != "carabine" and a["type"] not in ("lance", "pose") and not a["souffle"])
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
        if a["type"] in ("tir", "lance"):
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
    import villes

    paquet = villes.assembler()
    assert paquet["armes_regles"] == armes.REGLES
    for a in paquet["armes"]:
        for cle in ("auto", "dispersion_max", "bruit", "feu_s", "assomme", "meche", "souffle", "rebond"):
            assert cle in a, f"{a['slug']} : {cle}"


def test_ce_qui_se_lance_a_sa_meche_et_son_souffle():
    """La grenade et la dynamite : on les allume, la meche brule, elles sautent.
    La grenade rebondit, la dynamite non ; la dynamite coute moins cher et
    souffle plus large (« les explosifs », 28 sept. 2026)."""
    lancees = [a for a in armes.CATALOGUE if a["type"] == "lance"]
    assert sorted(a["slug"] for a in lancees) == ["dynamite", "grenade"]
    for a in lancees:
        assert a["meche"] > 0 and a["souffle"] > 0 and a["cloche"] is True, a["slug"]
        assert a["bruit"] == 0, "le bruit est celui de l'explosion (REGLES), pas du lancer"
    g, d = armes.par_slug("grenade"), armes.par_slug("dynamite")
    assert g["rebond"] is True and d["rebond"] is False
    assert d["prix"] < g["prix"] and d["souffle"] > g["souffle"] and d["meche"] > g["meche"]
    for a in armes.CATALOGUE:
        if a["type"] not in ("lance", "pose"):
            assert a["meche"] == 0 and a["rebond"] is False, a["slug"]
            assert a["souffle"] == 0 or a["slug"] == "lance_roquettes", a["slug"]
    assert armes.REGLES["explosion"]["bruit_tuiles"] > armes.par_slug("carabine")["bruit"]


def test_le_marche_noir_vend_ce_qui_saute():
    from app import magasins

    mn, gus = magasins.MARCHE_NOIR, magasins.par_slug("armurerie")
    for slug in ("grenade", "dynamite"):
        assert slug in mn["articles"] and slug in mn["munitions"], slug
        assert slug not in gus["articles"], f"{slug} : pas de vitrine chez Gus"


def test_les_sons_des_explosifs_ne_pesent_pas_sur_le_premier_ecran():
    """La grenade se degoupille, la dynamite s'allume : deux sons, et le rebond. Ils ne
    s'entendent que chez qui en a un — ils se chargent a la demande (`audio.LIEUX`), pas
    au demarrage : le plafond de la 3G du premier ecran etait plein a 6 Ko pres."""
    from app import audio

    assert armes.par_slug("grenade")["son"] == "goupille"
    assert armes.par_slug("dynamite")["son"] == "meche"
    assert armes.par_slug("plastic")["son"] == "detonateur"
    assert armes.par_slug("lance_roquettes")["son"] == "roquette"
    assert set(audio.LIEUX["explosifs"]) == {"goupille", "meche", "rebond", "detonateur", "roquette"}


def test_le_c4_se_pose_et_saute_quand_on_veut():
    """Le C4 (les explosifs, vague 3) : on le pose, sans mèche ni cloche, il a un souffle ; trois charges au plus ;
    le marché noir le vend, et c'est (pour l'instant) le plus cher de tout le catalogue."""
    from app import magasins

    c4 = armes.par_slug("plastic")
    assert c4["type"] == "pose" and c4["meche"] == 0 and c4["cloche"] is False and c4["souffle"] > 0
    assert c4["prix"] < armes.par_slug("lance_roquettes")["prix"]
    assert "plastic" in magasins.MARCHE_NOIR["articles"] and "plastic" in magasins.MARCHE_NOIR["munitions"]
    r = armes.REGLES["c4"]
    assert r["max"] == 3 and 0 < r["tenir_images"] <= 60 and r["colle_px"] > 0


def test_le_lance_roquettes_tire_droit_et_saute_a_l_impact():
    """Vague 4b : il tire droit (pas en cloche), sa roquette a un souffle, une par chargeur, et c'est l'arme la plus
    chère du jeu ; le marché noir la vend."""
    from app import magasins

    lr = armes.par_slug("lance_roquettes")
    assert lr["type"] == "tir" and lr["cloche"] is False and lr["souffle"] > 0 and lr["chargeur"] == 1
    assert lr["prix"] == max(a["prix"] for a in armes.achetables()) and lr["bruit"] > 0
    assert "lance_roquettes" in magasins.MARCHE_NOIR["articles"] and "lance_roquettes" in magasins.MARCHE_NOIR["munitions"]
