"""Des photos pour le Clairon, côté catalogue (docs/jalons/des-photos-pour-le-clairon.md) : Louise existe, se
nomme dans sa salutation seulement, et ce qu'elle paie tient l'économie."""

from app import economie, missions, photos


def test_louise_est_un_personnage_devant_le_kiosque_et_n_a_pas_de_repos():
    p = missions.personnage("louise")
    assert p and p["ou"] == "porte:kiosque" and p["arrive_apres"]
    assert not [r for r in missions.repliques_de_repos() if r["qui"] == "louise"], "elle ouvre son menu, pas un repos"


def test_elle_se_nomme_une_fois_dans_sa_salutation():
    textes = {r["cle"]: r["texte"] for r in photos.REPLIQUES}
    assert "Louise Tremblay-Dion" in textes["salut"]
    assert all("Louise" not in t for c, t in textes.items() if c != "salut")


def test_le_meilleur_sujet_paie_le_plus_et_toi_le_plus_cher():
    assert photos.meilleur(["personnage", "feu", "vol"]) == "feu"
    assert photos.meilleur(["poursuite", "toi"]) == "toi"
    assert photos.meilleur([]) is None
    assert max(photos.SUJETS, key=lambda s: photos.SUJETS[s]["prix"]) == "toi"


def test_une_photo_par_jour_ne_vaut_pas_une_mission():
    """Une par jour : au mieux 300 $, moins que la prime d'une mission du milieu (m6 et ses sœurs)."""
    plus_chere = max(s["prix"] for s in photos.SUJETS.values()) + photos.REGLES["par_etoile"] * 5
    assert plus_chere <= 400
    assert economie.gain_boulot(economie.BOULOTS["taxi"]) <= plus_chere
