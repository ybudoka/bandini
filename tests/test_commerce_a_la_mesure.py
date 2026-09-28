"""Le commerce à la mesure de son bâtiment (docs/jalons/le-commerce-a-la-mesure-de-son-batiment.md).

Demande de Martin (27 sept. 2026) : « valide la grandeur des bâtiments avec ce qu'il y a comme
commerce, il faut que ce soit logique ». Mesuré avant : un HÔTEL DES QUAIS dans 24 tuiles, un
CHANTIER NAVAL dans 42, une MACHINERIE dans 24 — et un TATOUAGE dans un hangar de 90. Quinze
enseignes sur quatre-vingt-dix-huit.

⚠️ **La part se mesure PAR LA CONSTRUCTION**, pas dans `aires_des_devantures` que le passage lit :
un espion sur `poser_devanture` compte, au moment où l'enseigne se pose, les tuiles du bâtiment au
droit de sa vitrine. Un juge qui relirait la table qu'il juge ne rougirait pas le jour où elle ment.
"""

from __future__ import annotations

import pytest

from app import carte, devantures, vitrines

#: ⚠️ LA VILLE D'AVANT (27 sept. 2026) : la bande nord se pose en tout dernier et décale la ville de
#: 110 rangées ; la part se lit dans le repère de la construction, `nord=False`.


def _mesuree(graine: int = carte.GRAINE, sans_passage: bool = False) -> tuple[dict, dict]:
    """(ville, {(x, y) du bandeau: tuiles de bâtiment derrière la vitrine})."""
    aires: dict[tuple[int, int], int] = {}
    original = carte._Chantier.poser_devanture
    passage = vitrines.a_la_mesure

    def espion(self, facades, ancre, genre, special=None, enseigne=None, bande=None):
        avant = len(self.devantures)
        pose = original(self, facades, ancre, genre, special, enseigne, bande)
        if pose and special is None and bande is not None:
            x0, large = bande
            d = self.devantures[avant]
            aires[(d["x"], d["y"])] = len({(tx, ty) for tx, ty in self.tuiles_du_batiment
                                           if x0 <= tx < x0 + large})
        return pose

    carte._Chantier.poser_devanture = espion
    if sans_passage:
        vitrines.a_la_mesure = lambda *a, **k: {}
    try:
        # ⚠️ Générée sous l'espion : la ville gardée des juges (`villes`) ne le verrait pas.
        ville = carte.generer(graine=graine, nord=False)
    finally:
        carte._Chantier.poser_devanture = original
        vitrines.a_la_mesure = passage
    return ville, aires


@pytest.fixture(scope="module")
def mesuree():
    return _mesuree()


def _hors_mesure(ville: dict, aires: dict) -> list[tuple[str, int]]:
    return [(d["texte"], aires[(d["x"], d["y"])]) for d in ville["devantures"]
            if (d["x"], d["y"]) in aires and not devantures.a_sa_taille(d["texte"], aires[(d["x"], d["y"])])]


def test_chaque_enseigne_a_la_mesure_de_son_batiment(mesuree):
    ville, aires = mesuree
    assert len(aires) >= 80, len(aires)
    assert not _hors_mesure(ville, aires)


@pytest.mark.parametrize("graine", [1, 7, 99])
def test_a_la_mesure_sur_d_autres_graines(graine):
    ville, aires = _mesuree(graine)
    assert aires, graine
    assert not _hors_mesure(ville, aires), graine


def test_sans_le_passage_la_ville_ment():
    """⚠️ Le juge MORD : sans `a_la_mesure`, l'hôtel des Quais retourne dans sa boutique. Le standing
    choisit déjà à la mesure (il ne tire plus un TATOUAGE pour un hangar) — ce qui reste vient de la
    construction, qui tire le nom sans regarder le mur."""
    ville, aires = _mesuree(sans_passage=True)
    assert len(_hors_mesure(ville, aires)) >= 5, _hors_mesure(ville, aires)


def test_le_passage_ne_touche_que_des_noms(mesuree):
    """Rien d'autre ne bouge : ni une tuile, ni un bandeau, ni une couleur, ni une porte."""
    ville, _ = mesuree
    sans, _ = _mesuree(sans_passage=True)
    assert ville["sol"] == sans["sol"]
    cles = ("x", "y", "l", "genre", "motifs", "porte", "pancarte")
    assert [{k: d.get(k) for k in cles} for d in ville["devantures"]] == \
        [{k: d.get(k) for k in cles} for d in sans["devantures"]]
    assert [p["x"] for p in ville["portes"]] == [p["x"] for p in sans["portes"]]


def test_un_nom_renomme_garde_sa_famille(mesuree):
    """La pièce derrière la porte est meublée par la famille : la renommer en épicerie laisserait
    une quincaillerie derrière le bandeau."""
    ville, _ = mesuree
    familles = {nom: f for liste in (*devantures.COMMERCES.values(), devantures.COMMERCES_COSSUS,
                                     devantures.COMMERCES_PAUVRES) for nom, f in liste}
    speciaux = {texte for texte, _ in devantures.ENSEIGNES.values()} | {
        texte for texte, _ in devantures.CARROSSERIES.values()} | {"DOJO DION", "BINGO", "CINÉMA RIALTO",
                                                                     "SALLE DE QUILLES", "QUILLES", "LAVE-AUTO",
                                                                     devantures.A_LOUER}
    for d in ville["devantures"]:
        if d["texte"] in familles and d["texte"] not in speciaux:
            assert devantures.GENRES[d["genre"]]["slug"] == familles[d["texte"]], d


def test_chaque_nom_range_existe():
    """Une faute de frappe dans `TAILLE_DU_NOM` rangerait un nom qui n'existe pas, et le vrai
    resterait moyen sans que personne le voie."""
    connus = {nom for liste in (*devantures.COMMERCES.values(), devantures.COMMERCES_COSSUS,
                                devantures.COMMERCES_PAUVRES) for nom, _ in liste}
    connus |= {texte for texte, _ in devantures.CARROSSERIES.values()} | {"QUILLES"}
    connus |= {nom for noms in devantures.RESERVE.values() for nom in noms}
    assert set(devantures.TAILLE_DU_NOM) <= connus, set(devantures.TAILLE_DU_NOM) - connus
    assert set(devantures.TAILLE_DU_NOM.values()) <= set(devantures.TAILLES)


def test_une_grande_salle_ne_tient_pas_dans_une_boutique():
    """Les bornes elles-mêmes : ce qui est grand ne descend pas où va le petit."""
    petit, grand = devantures.TAILLES["petit"], devantures.TAILLES["grand"]
    assert grand[0] > 20 and petit[1] < 60
    assert not devantures.a_sa_taille("HÔTEL DES QUAIS", 24)
    assert not devantures.a_sa_taille("TATOUAGE", 90)
    assert devantures.a_sa_taille("TAVERNE DU PORT", 24)


def test_la_reserve_loge_chaque_famille_a_chaque_taille():
    """Chaque famille a, dans sa réserve, un nom de chaque taille qui tient sur le plus étroit des
    bandeaux (deux tuiles) — c'est ce qui garantit que le passage trouve toujours."""
    for famille in (g["slug"] for g in devantures.GENRES):
        noms = devantures.RESERVE[famille]
        for taille in ("petit", "moyen", "grand"):
            assert any(devantures.taille_du_nom(nom) == taille and devantures.tient_en(nom, 2)
                       for nom in noms), (famille, taille)


def test_la_reserve_ne_contredit_pas_les_catalogues():
    """Un nom de réserve qui existe déjà au catalogue sous une autre famille changerait la pièce."""
    familles = {nom: f for liste in (*devantures.COMMERCES.values(), devantures.COMMERCES_COSSUS,
                                     devantures.COMMERCES_PAUVRES) for nom, f in liste}
    for famille, noms in devantures.RESERVE.items():
        for nom in noms:
            assert familles.get(nom, famille) == famille, (nom, famille)
