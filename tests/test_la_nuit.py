"""La nuit a ses habitudes — ce que les catalogues disent de la nuit.

⚠️ Les heures de nuit sont écrites ICI en toutes lettres, pas relues dans le
code : `Monde.estNuit` dit nuit quand la teinte passe 0,4 d'opacité, soit de
19 h 53 (0,828) à 6 h 24 (0,267). Un juge qui relirait la constante qu'il juge
changerait avec elle.
"""

import re

import villes

from app import pietons, vehicules
from app.carte import USAGES

NUIT_DEBUT = 0.828   # 19 h 53
NUIT_FIN = 0.267     # 6 h 24


def test_la_plage_ferme_avant_la_nuit_et_ouvre_apres():
    """La nuit, personne ne se baigne : la plage ouvre après la fin de la nuit
    et ferme avant qu'elle tombe — au coucher du soleil, pas dans le noir."""
    ouvre, ferme = pietons.PLAGE["heures"]
    assert ouvre < ferme, "la plage ne passe pas minuit : elle ferme le soir du même jour"
    assert NUIT_FIN <= ouvre, "la plage ouvre avant la fin de la nuit"
    assert ferme <= NUIT_DEBUT, "la plage ferme après la tombée de la nuit : on s'y baigne dans le noir"
    assert (ferme - ouvre) * 24 >= 8, "une plage ouverte moins de huit heures est une plage fermée"


def test_l_heure_de_la_plage_n_est_pas_sur_l_enfant():
    """⚠️ Toute la ville se sert de l'archétype `enfant` : lui donner des heures
    ferait disparaître le petit de la mère qui le promène."""
    enfant = next(p for p in pietons.CATALOGUE if p["slug"] == "enfant")
    assert enfant["heures"] is None


def test_la_nuit_on_gare_plus_de_chars_et_d_abord_chez_soi():
    t = vehicules.TRAFIC
    n = t["garer_la_nuit"]
    assert t["stationnes_max"] < n["max"] <= 20, "la nuit, plus de chars garés que le jour, sans noyer la bulle"
    assert n["usage"] in USAGES, "un usage que la carte ne connaît pas ne serait jamais préféré"
    # Une part devant les commerces (le bar, le dépanneur), mais une petite :
    # sinon la nuit ne déplacerait rien.
    assert 0 < n["ailleurs"] <= 0.3


# --- Vague 2 : ce qu'on voit ---------------------------------------------------------

def test_les_fenetres_se_couchent_dans_la_nuit_et_se_levent_avant_le_jour():
    from app import nuit
    debut, fin = nuit.FENETRES["coucher"]
    lever = nuit.FENETRES["lever"]
    # Le coucher : de 22 h à 3 h du matin (écrit ici, pas relu).
    assert debut >= 22 / 24 and fin <= 27 / 24 and debut < fin
    # Le lever : dans la nuit encore, sinon on allumerait en plein jour.
    assert 4 / 24 <= lever[0] < lever[1] <= NUIT_FIN
    # Entre le dernier coucher et le premier lever, la rue est noire.
    assert fin - 1 < lever[0], "une fenêtre se lèverait avant que la dernière se couche"


def test_un_lampadaire_pauvre_gresille_sans_etre_mort_et_la_ville_ne_bouge_pas():
    """Parmi les lampadaires pauvres qui marchent encore, une part grésille — un
    drapeau sur la lampe, pas une tuile : les lampes restent où elles étaient."""
    from app import carte, mobilier
    # ⚠️ La ville d'avant (27 sept. 2026) : lue par un `_Chantier`, dans SON repère (`app/nord.py`).
    ville = villes.generer(nord=False)
    # ⚠️ Sous le patch, `carte.generer` direct : le cache de `villes` rendrait la ville d'avant.
    original = mobilier.eclairer
    mobilier.eclairer = lambda chantier, bords, solides: {}
    try:
        sans = carte.generer(nord=False)
    finally:
        mobilier.eclairer = original
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    lampes = ville["lampes"]
    gresillent = [lampe for lampe in lampes if lampe.get("gresille")]
    assert gresillent, "pas un lampadaire qui grésille dans toute la ville"
    assert not [lampe for lampe in gresillent if lampe.get("panne")], "mort ET qui grésille : il faut choisir"
    assert not [lampe for lampe in gresillent if lampe.get("c")], "une fenêtre ou une vitrine ne grésille pas"
    ailleurs = [lampe for lampe in gresillent if chantier.standing_en(lampe["x"], lampe["y"]) != "pauvre"]
    assert not ailleurs, f"{len(ailleurs)} lampadaires grésillent hors d'un quartier pauvre"
    # Une part, pas tous : moins d'un sur trois de ceux qui marchent encore en pauvre.
    pauvres = [lampe for lampe in lampes if not lampe.get("c") and not lampe.get("panne")
               and chantier.standing_en(lampe["x"], lampe["y"]) == "pauvre"]
    assert len(gresillent) <= len(pauvres) / 3, f"{len(gresillent)} grésillent sur {len(pauvres)}"
    # La ville ne bouge pas : les mêmes lampes, aux mêmes places.
    assert [(lampe["x"], lampe["y"]) for lampe in lampes] == [(lampe["x"], lampe["y"]) for lampe in sans["lampes"]]


# --- Vague 3 : qui est dehors ------------------------------------------------------------

def test_le_last_call_sonne_a_trois_heures_devant_les_bars_de_la_ville():
    from app import devantures, nuit
    lc = nuit.LAST_CALL
    assert lc["heure"] == 3 / 24, "au Québec, les bars ferment à 3 h"
    assert lc["heure"] < lc["jusqu_a"] <= 4 / 24, "à 4 h, la rue est retombée"
    assert 2 <= lc["fetards"][0] <= lc["fetards"][1] <= 6, "une grappe, pas une foule"
    assert lc["portee_px"] < 520, "le bar doit être dans la bulle, sinon on ne les voit pas vivre"
    bars = villes.assembler()["nuit"]["last_call"]["bars"]
    assert len(bars) >= 5, "presque pas de bars dans la ville"
    ville = villes.assembler()["carte"]
    nuit_ = devantures.genre_index("nuit")
    noms = {d["texte"] for d in ville["devantures"] if d["genre"] == nuit_}
    assert all(b["nom"] in noms for b in bars)
    assert devantures.A_LOUER not in {b["nom"] for b in bars}, "un local à louer n'a pas de dernier service"
    for b in bars:
        assert b["y"] == b["porte"][1] + 1 and b["x"] == b["porte"][0], "on sort DEVANT la porte"
    for texte in lc["chansons"] + lc["chicane"]["mots"]:
        assert texte == texte.upper() and texte.strip() == texte, texte
    assert 0 < lc["chicane"]["part"] < 0.5, "la plupart des fêtards chantent : une part seulement cogne"


def test_le_camelot_passe_a_l_aube_et_le_journal_est_rentre_le_matin():
    from app import nuit
    camelot = next(p for p in pietons.CATALOGUE if p["slug"] == "camelot")
    debut, fin = camelot["heures"]
    assert 4 / 24 <= debut < fin <= NUIT_FIN, "le camelot passe à l'aube, avant le jour"
    crieur = next(p for p in pietons.CATALOGUE if p["slug"] == "crieur")
    assert debut < crieur["heures"][0], "le camelot lance le journal avant que le crieur le crie"
    assert fin < nuit.CAMELOT["rentre_a"] <= 10 / 24, "on rentre le journal le matin, après qu'il est passé"
    assert camelot["metier"] == "camelot" and camelot["frequence"] == 0.0
    assert pietons.PAROLES["camelot"]["lance"].isupper()


def test_la_nuit_le_rat_de_la_poubelle_est_un_raton_et_le_raton_ne_sort_que_la_nuit():
    from app import interactions
    f = interactions.FOUILLER["la_nuit"]
    assert f["par"] in interactions.TROUVAILLES and f["poids"] > 1
    raton = pietons.BETES["raton"]
    debut, fin = raton["heures"]
    assert debut >= NUIT_DEBUT - 0.01 and fin <= NUIT_FIN + 0.01, "le raton sort la nuit, pas à la brunante"
    assert raton["fuite_px"] < pietons.BETES["chat"]["fuite_px"], "le raton se laisse approcher plus que le chat"


# --- Vague 4 : ce que ça change au jeu ----------------------------------------------------

def test_les_comptoirs_ferment_la_nuit_ouvrent_avant_le_jeu_et_le_bar_ferme_au_last_call():
    from app import carte, magasins, nuit
    for famille, comptoir in magasins.COMPTOIRS.items():
        ouvre, ferme = comptoir["heures"]
        # Le jeu commence à 8 h 24 : tout est déjà ouvert — le jour ne change pas.
        assert ouvre <= 8 / 24, f"{famille} ouvre après 8 h"
        if famille == "nuit":
            assert ferme == nuit.LAST_CALL["heure"], "le bar ferme à l'heure du last call"
        else:
            assert 20 / 24 <= ferme <= 23 / 24, f"{famille} ferme à {ferme * 24:.1f} h"
    c = nuit.COMPTOIRS
    assert "depanneur" in c["toujours_ouverts"], "un dépanneur, ça reste ouvert"
    assert all(slug in carte.INTERIEURS for slug in c["toujours_ouverts"])
    assert c["ferme"] == c["ferme"].upper()


def test_l_arroseuse_sort_au_creux_de_la_nuit_et_mouille_sans_noyer():
    from app import neige, nuit
    a = nuit.ARROSEUSE
    debut, fin = a["heures"]
    # En pleine nuit : après minuit, et rentrée avant le jour.
    assert 0 < debut < fin <= NUIT_FIN, "l'arroseuse travaille au creux de la nuit"
    # Moins glissant que la neige : une rue arrosée n'est pas une patinoire.
    assert neige.EFFETS["adherence"] < a["adherence"] < 1
    assert 0.6 <= a["frein"] < 1
    assert 10 <= a["mouille_minutes"] <= 120
    assert neige.tracer_charrue(villes.generer()) is not None, "l'arroseuse fait la tournée de la charrue : il en faut une"


def test_le_plafond_de_lampes_tient_les_lampadaires_ET_les_feux(racine):
    """⚠️ `Base.fin` plafonnait à **25** lampes par image, taillé pour les
    lampadaires seuls — c'est aussi ce que `Monde.lampesVisibles` en rend au
    plus. Les feux s'y ajoutent maintenant : sous ce plafond-là, ils
    **éteindraient** les lampadaires au lieu de s'ajouter à eux. Les trois
    nombres se **lisent dans le JS**, ils ne sont pas recopiés ici.
    """
    js = lambda nom: (racine / "static" / "js" / nom).read_text(encoding="utf-8")  # noqa: E731
    plafond = int(re.search(r"^  const LAMPES_MAX = (\d+);", js("base.js"), re.M).group(1))
    lampadaires = int(re.search(r"out\.length >= (\d+)\) break;", js("monde.js")).group(1))
    feux = int(re.search(r"^  const LAMPES_FEUX_MAX = (\d+);", js("vehicules.js"), re.M).group(1))
    # Et depuis « la nuit a ses habitudes », les phares des chars menés — comptés
    # en CHARS depuis « des phares à la mesure de chaque char » : tant de chars, à
    # tant de lampes au plus.
    chars = int(re.search(r"^  const CHARS_ECLAIRES_MAX = (\d+);", js("vehicules.js"), re.M).group(1))
    par_char = int(re.search(r"^  const LAMPES_PAR_CHAR_MAX = (\d+);", js("vehicules.js"), re.M).group(1))
    assert re.search(r"^  const LAMPES_PHARES_MAX = CHARS_ECLAIRES_MAX \* LAMPES_PAR_CHAR_MAX;", js("vehicules.js"), re.M)
    phares = chars * par_char
    assert plafond >= lampadaires + feux + phares + 1, (
        f"{lampadaires} lampadaires + {feux} feux + {phares} phares + le projecteur de l'helico ne "
        f"tiennent pas sous un plafond de {plafond} : les feux en eteindraient"
    )


def test_les_feux_s_allument_au_meme_seuil_de_brune_que_les_lampadaires(racine):
    """Deux seuils voudraient dire deux réponses à « fait-il noir ? », et la
    deuxième serait fausse un jour — on verrait les feux s'allumer une heure
    avant (ou après) les lampadaires de la même rue."""
    js = lambda nom: (racine / "static" / "js" / nom).read_text(encoding="utf-8")  # noqa: E731
    lampadaires = float(re.search(r"ambiance\(\)\.alpha < ([\d.]+)\)", js("monde.js")).group(1))
    feux = float(re.search(r"^  const BRUNE = ([\d.]+);", js("vehicules.js"), re.M).group(1))
    assert feux == lampadaires, f"les feux s'allument a {feux}, les lampadaires a {lampadaires}"
