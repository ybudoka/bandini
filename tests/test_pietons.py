"""Le catalogue des passants — et ce que le navigateur en fait."""

import pytest

from app import armes, carte, pietons


#: Les metiers qui se tiennent quelque part au lieu de marcher. ⚠️ Le CRIEUR
#: en est : un crieur de journaux tient un coin de rue — c'est meme tout son
#: metier, et un crieur qui se promene ne crie a personne.
POSTES = {"ambulant", "musicien", "amuseur", "jongleur", "echassier", "crieur"}

#: Les SORTES : celles qui ont un corps a elles et une routine a elles. ⚠️ La
#: liste est ici et pas dans le juge, parce que trois juges la lisent — et une
#: liste recopiee trois fois finit par ne plus dire la meme chose aux trois.
SORTES = {"musicien", "amuseur", "jongleur", "echassier", "exhibitionniste",
          "contractuelle", "touriste", "ivrogne", "jogger", "facteur",
          "crieur", "laveur", "pickpocket"}


@pytest.mark.parametrize("pieton", pietons.CATALOGUE, ids=lambda p: p["slug"])
def test_un_pieton_est_jouable(pieton):
    assert pieton["nom"]
    assert set(pieton["couleurs"]) == {"c", "h", "s", "p"}, pieton["slug"]
    for couleur in pieton["couleurs"].values():
        assert couleur.startswith("#") and len(couleur) == 7, couleur
    # ⚠️ Ceux qui TIENNENT UN POSTE ne marchent pas : un marchand derriere son
    # kiosque, un musicien a son coin de rue, un amuseur au milieu de son
    # attroupement. Leur vitesse nulle est ce qui le dit — et c'est le metier
    # qui les range la, pas leur slug.
    if pieton["metier"] in POSTES:
        assert pieton["vitesse"] == 0.0, pieton["slug"]
    else:
        assert 0.5 <= pieton["vitesse"] <= 1.5, pieton["slug"]
    assert 0.0 <= pieton["courage"] <= 1.0
    assert 0.0 <= pieton["temoin"] <= 1.0
    assert 20 <= pieton["vie"] <= 150
    mini, maxi = pieton["argent"]
    assert 0 <= mini <= maxi <= 200
    if pieton["arme"]:
        assert armes.par_slug(pieton["arme"]), pieton["arme"]


def test_les_enfants_sont_intouchables():
    """⚠️ Le jeu est adulte : on y meurt, le sang coule. Un enfant, non.

    C'est une regle du catalogue, donc du moteur — pas une consigne qu'on
    peut oublier d'appliquer dans une branche du code de combat.
    """
    enfants = [p for p in pietons.CATALOGUE if p["sprite"] == "enfant"]
    assert enfants, "plus d'enfants dans la ville ?"
    for enfant in enfants:
        assert enfant["intouchable"] is True, enfant["slug"]
        assert enfant["arme"] is None
        assert enfant["courage"] == 0.0, "un enfant ne riposte pas"
    for pieton in pietons.CATALOGUE:
        if pieton["accompagne"]:
            accompagne = pietons.par_slug(pieton["accompagne"])
            assert accompagne and accompagne["intouchable"], pieton["slug"]


def test_les_metiers_ont_leurs_heures():
    for pieton in pietons.CATALOGUE:
        if pieton["metier"]:
            assert pieton["frequence"] == 0.0, \
                f"{pieton['slug']} : un metier ne nait pas au hasard dans la rue"
        if pieton["heures"]:
            debut, fin = pieton["heures"]
            assert 0 <= debut < 1 and 0 <= fin < 1
    nuit = pietons.par_slug("racoleuse")
    assert pietons.travaille_a(nuit, 0.95) and not pietons.travaille_a(nuit, 0.5)
    assert pietons.de_metier("compagnie") and pietons.de_metier("ambulant")


def test_la_fille_de_la_brume_ne_porte_les_couleurs_de_personne():
    """⚠️ Retour de Martin (13 sept. 2026) : on ne les distinguait plus. Son
    rose etait celui de la passante a une nuance pres, et ses cheveux ceux de
    la moitie du catalogue. Le CONTOUR est dans sprites.js (`racoleuse`) ; ici
    on garde l'autre moitie : aucune de ses couleurs ne se recroise ailleurs.
    La peau, elle, se partage — c'est une peau."""
    fille = pietons.par_slug("racoleuse")
    assert fille["sprite"] == "racoleuse", "elle a repris le corps de tout le monde"
    for autre in pietons.CATALOGUE:
        if autre["slug"] == "racoleuse":
            continue
        for cle in ("c", "h", "p"):
            assert autre["couleurs"][cle].lower() != fille["couleurs"][cle].lower(), \
                f"{autre['slug']} porte la meme couleur « {cle} » que la fille de la Brume"


def test_les_slugs_sont_uniques():
    assert len(pietons.SLUGS) == len(set(pietons.SLUGS))


def test_il_y_a_du_monde_ordinaire_dans_la_rue():
    ordinaires = pietons.ordinaires()
    assert len(ordinaires) >= 5
    assert sum(p["frequence"] for p in ordinaires) > 0
    # ⚠️ Un membre de gang n'apparait JAMAIS au hasard dans la rue : il sort
    # de son territoire. Sinon on croise des Cravates a l'autre bout de la ville.
    for pieton in ordinaires:
        assert pieton["gang"] is None


def test_le_courage_va_du_fuyard_au_bagarreur():
    courages = sorted(p["courage"] for p in pietons.CATALOGUE)
    assert courages[0] == 0.0, "personne ne fuit sans se poser de question ?"
    assert courages[-1] >= 0.8, "personne ne riposte ?"


def test_les_gangs_ont_un_territoire_et_un_archetype():
    zones = {z["slug"] for z in carte.exporter()["zones"]}
    for gang in pietons.GANGS:
        assert pietons.par_slug(gang["pieton"]), gang["pieton"]
        assert gang["zone"] in zones, f"{gang['slug']} : territoire {gang['zone']} absent de la carte"
        assert 1 <= gang["membres"] <= 30


def test_les_reactions_sont_des_durees_credibles():
    reactions = pietons.REACTIONS
    assert reactions["recul_images"] < reactions["ko_images"]
    assert 1 <= reactions["fuite_secondes"] <= 30
    assert 0 < reactions["pickpocket_dos_degres"] <= 180


def test_l_agent_de_police_est_un_pieton_arme_qui_ne_nait_pas_au_hasard():
    agent = pietons.par_slug("policier")
    assert agent and agent["metier"] == "police" and agent["frequence"] == 0.0
    # Les gars du lot : un metier, donc jamais dans la rue ; du courage, une
    # batte, et surtout PAS d'arme a feu — ils ripostent, ils n'abattent pas.
    gardiens = pietons.de_metier("gardien")
    assert gardiens and all(g["frequence"] == 0.0 for g in gardiens)
    assert all(g["courage"] >= 0.9 and g["arme"] == "batte" for g in gardiens)
    assert agent["arme"] == "pistolet" and agent["courage"] == 1.0
    assert agent["temoin"] == 0.0, "un agent ne temoigne pas : il agit"
    assert agent not in pietons.ordinaires()


def test_les_trois_sortes_ont_un_corps_a_elles():
    """⚠️ Demande de Martin : « des amuseurs publics, des musiciens de rue, des
    exhibitionnistes. »

    La ville avait 24 archetypes pour QUATRE corps : vingt et un portaient
    celui du joueur avec un echange de palette. Une sorte etait donc une
    couleur et trois chiffres — et le depot a deja paye ce defaut une fois,
    avec les filles de la Brume qu'on ne distinguait plus de personne.

    La regle : UNE SORTE = UN CORPS + UNE ROUTINE. Ce juge tient la premiere
    moitie (un sprite a elle, un metier a elle) ; le banc tient la seconde.

    ⚠️ Les CINQ de la deuxieme vague sont jugees ici aussi, et par la meme
    regle : une sorte ajoutee sans corps a elle serait un costume, qu'elle soit
    de la premiere fournee ou de la dixieme."""
    sortes = SORTES
    trouves = {p["slug"] for p in pietons.CATALOGUE if p["slug"] in sortes}
    assert trouves == sortes, f"il en manque : {sortes - trouves}"
    for slug in sortes:
        p = next(q for q in pietons.CATALOGUE if q["slug"] == slug)
        # ⚠️ Un corps A ELLE : pas `joueur`, pas celui d'une autre sorte.
        assert p["sprite"] == slug, f"{slug} porte le corps « {p['sprite']} »"
        # ⚠️ Et un metier : c'est le crochet que le moteur lit pour lui donner
        # ce qu'elle FAIT. Sans lui, ce n'est qu'un costume.
        assert p["metier"] == slug, f"{slug} n'a pas de metier a lui"
        assert p["frequence"] == 0.0, f"{slug} nait au hasard dans la foule"
    # Les corps ne se partagent pas : autant de sprites que de sortes.
    corps = {next(q for q in pietons.CATALOGUE if q["slug"] == s)["sprite"] for s in sortes}
    assert len(corps) == len(sortes), f"deux sortes se partagent un corps : {corps}"


def test_les_sortes_qui_viennent_avec_ont_leurs_quartiers():
    """⚠️ Huit sortes qui naissent PARTOUT, ce n'est plus de la variete, c'est
    de la figuration : on les croise toutes dans la meme rue et on cesse de les
    voir. Chacune de la deuxieme vague declare donc ses quartiers — un touriste
    sur les Quais et pas dans La Shop, un facteur aux Erables et pas au port.

    Un quartier se reconnait a ses enseignes, a ses toits et a sa gang ; il doit
    aussi se reconnaitre a QUI Y MARCHE."""
    districts = {d["slug"] for d in carte.DISTRICTS}
    deuxieme = {"contractuelle", "touriste", "ivrogne", "jogger", "facteur",
                "crieur", "laveur", "pickpocket"}
    for slug in sorted(deuxieme):
        p = pietons.par_slug(slug)
        assert p is not None, f"{slug} n'est pas au catalogue"
        assert p["districts"], f"{slug} n'a pas de quartiers : elle naitra partout"
        inconnus = set(p["districts"]) - districts
        assert not inconnus, f"{slug} habite un quartier qui n'existe pas : {inconnus}"
    # ⚠️ Et elles ne sont pas toutes dans le meme : deux quartiers au moins
    # doivent en accueillir, sinon la regle ne sert a rien.
    couverts = {d for slug in deuxieme for d in pietons.par_slug(slug)["districts"]}
    assert len(couverts) >= 3, f"les cinq tiennent dans {couverts} : ce n'est plus une repartition"


def test_ce_qu_une_sorte_dit_vit_en_python():
    """⚠️ « Une fiche que le navigateur ne lisait pas » — le depot a paye ce
    defaut huit fois. Le symetrique coute aussi cher : un mot ecrit en dur dans
    `entites.js` est un mot que personne ne peut relire, corriger ni juger
    depuis la source de verite. `missions.py` le dit deja pour l'histoire ; ce
    qu'une sorte dit dans la rue n'est pas d'une autre nature.

    Ce juge tient les deux bouts : chaque parole appartient a un metier qui
    existe, et aucune n'est vide."""
    metiers = {p["metier"] for p in pietons.CATALOGUE if p["metier"]}
    for metier, mots in pietons.PAROLES.items():
        assert metier in metiers, f"« {metier} » n'est le metier de personne"
        assert mots, f"{metier} n'a rien a dire"
        for cle, valeur in mots.items():
            textes = valeur if isinstance(valeur, list) else [valeur]
            assert textes, f"{metier}.{cle} est vide"
            for texte in textes:
                assert isinstance(texte, str) and texte.strip(), f"{metier}.{cle} : {texte!r}"
    # Le paquet les porte : sans ca, le navigateur ne les verrait pas.
    assert pietons.exporter()["paroles"] == pietons.PAROLES
