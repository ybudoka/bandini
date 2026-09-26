"""Le 6/49 du dépanneur : les règles (docs/jalons/le-6-49-du-depanneur.md). Le banc
(`test_loto_js.py`) juge le billet et le tirage."""

from app import economie, loto


def test_les_chances_sont_les_vraies():
    """Trois bons numéros une fois sur 57, six une fois sur quatorze millions — et toutes les
    issues d'un billet font 1."""
    assert round(1 / loto.chance(3)) == 57
    assert round(1 / loto.chance(6)) == 13_983_816
    assert abs(sum(loto.chance(b) for b in range(loto.NUMEROS + 1)) - 1) < 1e-12


def test_un_billet_rend_moins_du_cinquieme_de_ce_qu_il_coute():
    """⚠️ Presque personne ne gagne : en moyenne, un billet de 2 $ rend moins de 40 cents. Un jeu
    d'argent ne bat jamais un boulot honnête."""
    assert loto.retour_moyen() < 0.2


def test_le_gros_lot_est_plafonne():
    """Le lot grandit avec les bons numéros, et le gros lot reste une fortune du JEU, pas une
    qui casse l'économie."""
    lots = [loto.LOTS[b] for b in sorted(loto.LOTS)]
    assert lots == sorted(lots) and len(set(lots)) == len(lots)
    assert loto.LOTS[6] <= 25_000 < economie.exporter()["fortune_max"]
    assert min(loto.LOTS) == 3, "deux bons numéros ne paient rien : c'est ce qui fait rire"
