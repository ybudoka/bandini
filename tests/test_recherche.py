from app import economie, recherche


def test_paliers_contigus_et_monotones():
    assert [p["etoiles"] for p in recherche.PALIERS] == list(range(6))
    zero = recherche.PALIERS[0]
    assert zero["agents_pied"] == 0 and zero["autos"] == 0 and not zero["tirent"]
    for a, b in zip(recherche.PALIERS, recherche.PALIERS[1:]):
        assert b["agents_pied"] >= a["agents_pied"]
        assert b["autos"] >= a["autos"]
        assert b["decroissance_s"] > a["decroissance_s"]
        assert b["tirent"] >= a["tirent"]
    assert recherche.PALIERS[5]["barrages"] and recherche.PALIERS[5]["helico"]
    assert recherche.ETOILES_MAX == 5


def test_delits():
    for nom, d in recherche.DELITS.items():
        assert d["etoiles"] >= 1, nom
        assert isinstance(d["temoin"], bool)
    assert recherche.DELITS["mort_policier"]["etoiles"] > recherche.DELITS["mort_pieton"]["etoiles"]
    assert recherche.DELITS["carjacking"]["temoin"] is False
    # ⚠️ Sortir son char du lot sans payer : bruyant (les gardiens sont la pour
    # ca), et le meme nombre d'etoiles que l'economie annonce — deux tables,
    # une seule verite.
    from app import economie
    assert recherche.DELITS["fourriere"]["temoin"] is False
    assert recherche.DELITS["fourriere"]["etoiles"] == economie.FOURRIERE["etoiles_vol"]


def test_vision():
    for genre in ("policier", "auto_police", "pieton", "helico"):
        v = recherche.VISION[genre]
        assert 0 < v["angle"] <= 180
        assert v["nuit"] <= v["jour"]
    assert recherche.VISION["alarme_rayon"] > 0


def test_export_complet():
    e = recherche.exporter()
    for cle in ("paliers", "delits", "vision", "temoins", "deguisement", "vitesses", "tuile_px"):
        assert cle in e
    assert e["vitesses"]["joueur_sprint"] > e["vitesses"]["policier"] > e["vitesses"]["pieton_course"]


def test_la_police_de_terrain_est_bornee():
    police = recherche.POLICE
    assert 1 <= police["patrouille_par_zone_max"] <= 6
    assert 1 <= police["regarde_toutes_les_images"] <= 10, "un agent qui regarde trop rarement rate tout"
    assert 8 <= police["arrestation_px"] <= 24
    assert police["poursuite_abandon_s"] < recherche.PALIERS[1]["decroissance_s"] * 2
    assert 0.5 <= police["auto_vitesse"] <= 1.0
    assert police["tir_cadence_s"] > 0 and police["tir_portee_tuiles"] <= recherche.VISION["policier"]["jour"]
    assert 1 <= police["prison_heures"] <= 12
    assert recherche.PALIERS[3]["tirent"] and not recherche.PALIERS[2]["tirent"], "on tire a partir de 3 etoiles"


def test_un_casier_epais_se_voit_de_loin_mais_pas_a_l_infini():
    """⚠️ M11 : « plus le dossier est épais, plus les agents te reconnaissent de
    loin ». C'est la seule façon de faire PESER un casier autrement qu'au
    comptoir des amendes — vingt pages ne changent rien à ce qu'on lit dans le
    HUD, elles changent la distance à laquelle on se fait reconnaître.

    ⚠️ **Le plafond est la règle, pas le détail.** Sans lui, vingt pages
    feraient voir la police à seize tuiles en pleine nuit, et il n'y aurait plus
    une ruelle où souffler. Le juge le tient à casier absurde : la portée reste
    bornée quel que soit le dossier."""
    v = recherche.VISION
    par_page, plafond = v["casier_portee_par_page"], v["casier_portee_max"]
    assert 0 < par_page < 0.2, par_page
    assert 1 < plafond <= 2, plafond

    def portee(casier: int) -> float:
        return min(plafond, 1 + par_page * max(0, casier))

    assert portee(0) == 1.0, "un casier vierge ne change rien"
    assert portee(1) > 1.0, "la première page ne se voit pas"
    # ⚠️ Le plafond DOIT mordre à casier plein, sinon il ne protège de rien.
    assert portee(economie.CASIER_MAX) == plafond, (
        f"à {economie.CASIER_MAX} pages la portée vaut {portee(economie.CASIER_MAX)} : "
        f"le plafond de {plafond} ne sert à rien"
    )
    for absurde in (100, 10_000, 10**9):
        assert portee(absurde) == plafond, f"casier {absurde} : {portee(absurde)}"
    # Et la portée de nuit reste sous celle du jour, même au plafond : la nuit
    # protège toujours quelqu'un.
    for genre in ("policier", "auto_police"):
        cone = v[genre]
        assert cone["nuit"] * plafond <= cone["jour"] * plafond * 1.01
        assert cone["nuit"] < cone["jour"], genre
