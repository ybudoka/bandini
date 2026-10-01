"""Des bagarres de gangs vivantes, et armées — la fiche (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md)."""

from pathlib import Path

import villes

from app import armes, pietons, rixes

RIXE_JS = Path(__file__).resolve().parent.parent / "static" / "js" / "rixe.js"


def test_la_fiche_du_contact_se_tient():
    """Des chiffres qui se contredisent font un combat qui grince."""
    f = rixes.CONTACT
    assert 0 < f["cercle_px"] < f["portee_px"], "sa place doit être à portée de coup"
    assert 0 <= f["cadence_ecart"] < f["cadence_images"]
    # Il revient de son recul AVANT son prochain coup : sinon il frappe dans le vide, de loin.
    assert f["recul_images"] < f["cadence_images"] - f["cadence_ecart"]
    assert 0 < f["recul_allure"] <= 1
    assert 0 < f["tourne_min"] <= f["tourne_max"]
    assert 0 < f["pas_images"] < f["tourne_min"], "un pas de côté plus long que l'attente entre deux"
    assert 0 <= f["esquive_pct"] <= 100
    assert 0 < f["bouge_px"] < 1, "une cible qui marche doit compter comme une cible qui bouge"
    assert 0 < f["coince_images"] < f["cadence_images"], "coincé plus longtemps qu'un coup : il ne frapperait plus"
    assert f["places"] >= 4, "trois assaillants doivent pouvoir s'étaler"
    assert 0 < f["place_px"] < f["cercle_px"], "« à sa place » plus large que le cercle : il frapperait de partout"
    assert 0 < f["contourne_rad"] < 3.14159, "contourner d'un demi-tour, c'est traverser"


def test_le_paquet_porte_la_fiche_des_rixes():
    """⚠️ « Une fiche que le navigateur ne lisait pas » — le dépôt a payé ce défaut huit fois."""
    assert villes.assembler()["rixes"] == rixes.exporter()


def test_le_cerveau_ne_tire_aucun_de_du_jeu():
    """⚠️ Un dé tiré ici décalerait tout le hasard de la ville : tout se lit à l'empreinte."""
    source = RIXE_JS.read_text(encoding="utf-8")
    assert "B.rng" not in source and "Math.random" not in source


def test_l_arsenal_se_tient():
    """Chaque gang a une arme qui TIRE, et sa fourchette de distance tient dans sa portée. Les Mantes n'en ont
    pas : elles ont l'école (la fiche du jalon)."""
    par_slug = {a["slug"]: a for a in armes.CATALOGUE}
    gangs = {g["slug"] for g in pietons.GANGS}
    assert set(rixes.ARSENAL) <= gangs, "une arme pour un gang qui n'existe pas"
    assert "mantes" not in rixes.ARSENAL
    for gang, slug in rixes.ARSENAL.items():
        a = par_slug[slug]
        assert a["type"] == "tir", f"{gang} : {slug} ne tire pas"
        assert a["chargeur"], f"{slug} n'a pas de chargeur : le tireur ne rechargerait jamais"
        dmin, dmax = rixes.TIR["distances"][slug]
        assert 0 < dmin < dmax <= a["portee"], f"{slug} : {dmin}-{dmax} hors de sa portée {a['portee']}"
    assert rixes.PART_ARMEE >= 2, "un sur un, ce n'est plus un arsenal, c'est une armée"


def test_le_molotov_tombe_dans_sa_fourchette():
    """La bouteille part en cloche et retombe au bout d'environ 30 images, quelle que soit la cible : le lanceur
    doit se tenir à cette distance-là, sinon elle casse à ses pieds ou derrière la cible."""
    m = next(a for a in armes.CATALOGUE if a["slug"] == "molotov")
    # z part de 6, monte de 1,6 et perd 0,12 par image (`combat.js`, `majProjectiles`).
    z, vz, n = 6.0, 1.6, 0
    while z > 0:
        z += vz
        vz -= 0.12
        n += 1
    chute = m["vitesse_projectile"] * n
    dmin, dmax = rixes.TIR["distances"]["molotov"]
    assert dmin <= chute <= dmax, f"la bouteille tombe à {chute:.0f} px, hors de {dmin}-{dmax}"


def test_la_fiche_du_tir_se_tient():
    t = rixes.TIR
    assert 1 <= t["salve"][0] <= t["salve"][1]
    assert t["lever_images"] > 0 and t["recharge_images"] > t["entre_salves_images"] > 0
    assert 0 < t["degats_contre_joueur"] <= 1
    assert t["dispersion_facteur"] >= 1, "un homme de gang ne tire pas mieux que toi"
    assert t["abri_tuiles"] >= 2


def test_le_paquet_porte_l_arsenal():
    d = villes.assembler()["rixes"]
    assert d["arsenal"] == rixes.ARSENAL and d["part_armee"] == rixes.PART_ARMEE
    assert d["tir"]["distances"]["pistolet"] == list(rixes.TIR["distances"]["pistolet"])


def test_la_fiche_du_moral_se_tient():
    """Vague 3 : le blessé, la déroute."""
    m = rixes.MORAL
    assert 0 < m["blesse_part"] < m["deroute_part"] <= 1
    assert 0 < m["boite_allure"] < 1, "il boite : plus lent qu'un fuyard sain"
    assert m["camp_px"] >= 120
    assert m["camp_images"] >= 120, "un camp qu'on oublie avant qu'il ait perdu quelqu'un"
    assert m["blesse_mots"] and m["deroute_mots"]
    assert villes.assembler()["rixes"]["moral"]["deroute_mots"] == list(m["deroute_mots"])


def test_la_fiche_des_renforts_se_tient():
    """Vague 4 : ils naissent hors de l'écran (la vue fait 480 × 270 : à plus de 276 px, on est dehors) et dans la
    bulle d'oubli (520 px), sinon ils s'effacent à l'image suivante."""
    r = rixes.RENFORTS
    dmin, dmax = r["distance_px"]
    assert 276 < dmin < dmax < 520
    assert dmin < r["joueur_max_px"] < 520, "un renfort né hors de la bulle d'oubli s'efface aussitôt"
    assert 1 <= r["max_par_appel"] <= r["max_par_combat"]
    assert r["en_char_sur"] >= 1 and r["cris"]
    assert villes.assembler()["rixes"]["renforts"]["cris"] == list(r["cris"])


def test_la_fiche_des_lancers_se_tient():
    """Vague 5b : un homme sans arme à feu lance une brique ou une bouteille, à distance, une fois par combat."""
    lan = rixes.LANCER
    dmin, dmax = lan["distance_px"]
    assert rixes.CONTACT["portee_px"] < dmin < dmax, "on lance de plus loin qu'on ne frappe"
    assert lan["chance_sur"] >= 1 and lan["geste_images"] > 0 and lan["vol_images"] > 0
    assert set(lan["objets"]) == {"brique", "bouteille"}
    assert all(o["degats"] > 0 for o in lan["objets"].values())
    assert villes.assembler()["rixes"]["lancer"]["distance_px"] == list(lan["distance_px"])
