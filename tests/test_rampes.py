"""Les rampes — et surtout ce qu'il y a AUTOUR d'elles.

⚠️ Ces juges sont nes d'un retour de Martin : « c'est quoi ces lignes
jaunes ? ». Les rampes existaient depuis M3, elles etaient posees dans la cour
cloturee des gangs, et on ne pouvait ni les reconnaitre ni les prendre. Une
rampe ne se juge donc pas sur elle-meme (deux tuiles, un glyphe) mais sur sa
PISTE : de l'elan devant, de la place derriere, et rien de solide dans les
deux. Un juge qui se contenterait de compter les rampes aurait ete vert tout
ce temps-la.
"""

import pytest

from app import carte, missions, vehicules

CARTE = carte.generer()
SOL = CARTE["sol"]
LARGEUR, HAUTEUR = len(SOL[0]), len(SOL)
RAMPES = CARTE["rampes"]

NOMS = {(1, 0): "est", (-1, 0): "ouest", (0, 1): "sud", (0, -1): "nord"}


def roulable(x: int, y: int) -> bool:
    """⚠️ Solidite 0, pas « marchable » : une cloture (solidite 3) laisse
    passer un pieton et arrete un char. C'est tout le probleme qu'on repare."""
    return 0 <= x < LARGEUR and 0 <= y < HAUTEUR and carte.solidite(SOL[y][x]) == 0


def course(x: int, y: int, dx: int, dy: int, voulu: int) -> int:
    n = 0
    while n < voulu and roulable(x + dx * (n + 1), y + dy * (n + 1)):
        n += 1
    return n


def test_il_y_a_des_rampes():
    assert len(RAMPES) >= 6, f"seulement {len(RAMPES)} rampes dans toute la ville"


@pytest.mark.parametrize("rampe", RAMPES, ids=lambda r: f"{r['x']},{r['y']}")
def test_une_rampe_est_une_paire_pied_levre(rampe):
    """Le dessin lit la paire pour savoir dans quel sens ca grimpe : un pied
    sans levre, c'est une rampe qui se peint vers l'est quoi qu'il arrive."""
    x, y, dx, dy = rampe["x"], rampe["y"], rampe["dx"], rampe["dy"]
    assert (dx, dy) in NOMS, rampe
    assert SOL[y][x] == "R", f"le pied annonce en {x},{y} n'est pas dans le sol"
    assert SOL[y + dy][x + dx] == "J", f"la levre de {x},{y} n'est pas dans le sol"


@pytest.mark.parametrize("rampe", RAMPES, ids=lambda r: f"{r['x']},{r['y']}")
def test_une_rampe_a_son_elan_et_sa_reception(rampe):
    """LE juge de ce travail. Avant lui : deux tuiles collees a un grillage,
    qu'on ne pouvait aborder qu'en roulant sur le trottoir."""
    x, y, dx, dy = rampe["x"], rampe["y"], rampe["dx"], rampe["dy"]
    elan = course(x, y, -dx, -dy, carte.ELAN_RAMPE)
    reception = course(x + dx, y + dy, dx, dy, carte.RECEPTION_RAMPE)
    assert elan >= carte.ELAN_RAMPE, \
        f"rampe {x},{y} vers le {NOMS[(dx, dy)]} : {elan} tuiles d'elan seulement"
    assert reception >= carte.RECEPTION_RAMPE, \
        f"rampe {x},{y} vers le {NOMS[(dx, dy)]} : on retombe sur un mur apres {reception} tuiles"


@pytest.mark.parametrize("rampe", RAMPES, ids=lambda r: f"{r['x']},{r['y']}")
def test_une_rampe_ne_coupe_aucune_voie_de_circulation(rampe):
    """Le trafic roule sur des rails : un tremplin au milieu d'une voie
    enverrait un char dans le decor a chaque tour."""
    voie = CARTE["voie"]
    for tx, ty in ((rampe["x"], rampe["y"]),
                   (rampe["x"] + rampe["dx"], rampe["y"] + rampe["dy"])):
        assert voie[ty][tx] == ".", f"rampe {tx},{ty} posee sur une voie « {voie[ty][tx]} »"


def test_aucune_rampe_n_est_enfermee():
    """Une rampe dans une poche que `boucher_les_poches` a refermee n'existe
    plus dans le sol : elle ne doit pas rester dans la liste, sinon le defi du
    Grand Saut promet un tremplin disparu."""
    grands = max(carte.composantes_marchables(CARTE), key=len)
    for rampe in RAMPES:
        assert (rampe["x"], rampe["y"]) in grands, \
            f"rampe {rampe['x']},{rampe['y']} hors de la ville marchable"


def test_les_rampes_ne_sont_pas_toutes_dans_le_meme_quartier():
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    quartiers = {chantier.district_en(r["x"], r["y"]) for r in RAMPES}
    assert len(quartiers) >= 3, f"toutes les rampes sont dans {quartiers}"


def test_les_skateux_ont_leur_tremplin():
    """« Les Skateux qui tiennent le stationnement » (DISTRICTS) : La Pointe
    n'avait pas UNE tuile de stationnement, la phrase etait une legende."""
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    pointe = [r for r in RAMPES if chantier.district_en(r["x"], r["y"]) == "pointe"]
    assert pointe, "La Pointe n'a pas de tremplin : les Skateux n'ont plus de terrain"


def vol_en_moto(tuiles_d_elan: int) -> float:
    """Combien de pixels une moto vole en sortant d'une rampe apres cet elan,
    partie d'arret. ⚠️ Le juge REFAIT le calcul avec la physique du paquet
    plutot que de relire une constante : si quelqu'un ralentit la moto ou
    adoucit l'impulsion demain, c'est ici que ca tombera."""
    moto = next(m for m in vehicules.CATALOGUE if m["slug"] == "moto")
    physique = vehicules.PHYSIQUE
    vitesse = distance = 0.0
    while distance < tuiles_d_elan * 16:
        vitesse = (vitesse + moto["acceleration"]) * moto["friction"]
        distance += vitesse
    vz = vitesse * physique["rampe_impulsion"]
    return vitesse * (2 * vz / physique["gravite"])


@pytest.mark.parametrize("rampe", RAMPES, ids=lambda r: f"{r['x']},{r['y']}")
def test_une_rampe_permet_le_vol_du_defi(rampe):
    """Le Grand Saut demande 60 px de vol en moto : une rampe qui ne les
    permet pas est un tremplin sur lequel le defi du jeu est impossible, et
    rien nulle part ne le dirait.

    ⚠️ C'est ce juge qui a corrige la mesure d'elan : a sept tuiles (le premier
    chiffre, choisi au gout), la moto ne volait que 54 px.
    """
    defi = next(d for d in missions.DEFIS if d["slug"] == "saut")
    vol = vol_en_moto(carte.ELAN_RAMPE)
    assert vol >= defi["vol_px"], \
        f"l'elan garanti ne donne que {vol:.0f} px de vol, le defi en demande {defi['vol_px']}"
    reception = course(rampe["x"] + rampe["dx"], rampe["y"] + rampe["dy"],
                       rampe["dx"], rampe["dy"], 30)
    assert reception * 16 >= vol, \
        f"rampe {rampe['x']},{rampe['y']} : on vole {vol:.0f} px et le degage n'en fait que {reception * 16}"


def test_aucun_obstacle_colle_au_pied():
    for rampe in RAMPES:
        x, y = rampe["x"] - rampe["dx"], rampe["y"] - rampe["dy"]
        assert roulable(x, y), f"rampe {rampe['x']},{rampe['y']} : un obstacle colle au pied"


def test_la_cour_d_avant_se_ferait_refuser_sa_rampe():
    """LA preuve par le bug remis. On refait la cour des gangs telle qu'elle
    etait — une bande de trottoir, un grillage devant, du bati derriere — et
    `poser_rampe` doit dire NON.

    ⚠️ Elle avait pourtant vingt et une tuiles d'elan : le long du trottoir,
    entre la cloture et les murs. C'est pour ca qu'un juge qui ne compterait
    que les tuiles libres serait passe a cote — ce qui manquait, ce n'etait pas
    de la place, c'etait un endroit ou un char va SANS monter sur le trottoir.
    """
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    x0, y0 = 40, 40
    for j in range(-9, 10):
        for i in range(-9, 10):
            chantier.sol[y0 + j][x0 + i] = "F"          # du bati tout autour
    for i in range(-9, 10):
        chantier.sol[y0][x0 + i] = "."                  # la bande de trottoir
        chantier.sol[y0 + 1][x0 + i] = "f"              # la cloture de la cour
    assert chantier.poser_rampe(x0, y0) is False, "la cour d'avant passe encore"
    # Le meme endroit en asphalte de stationnement : la, oui.
    for i in range(-9, 10):
        chantier.sol[y0][x0 + i] = "p"
    assert chantier.poser_rampe(x0, y0) is True, "un stationnement degage devrait passer"


def test_le_dessin_sait_ou_ca_grimpe(banc):
    """Le peintre ne connait ni le generateur ni la liste : il lit la paire
    dans le sol. Le pied doit donc retrouver le sens que Python a choisi, et
    la levre le meme sens avec son bit a elle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        return (c.rampes || []).map(function (r) {
            return { x: r.x, y: r.y, dx: r.dx, dy: r.dy,
                     pied: L.Monde.varianteDeRampe('R', r.x, r.y),
                     levre: L.Monde.varianteDeRampe('J', r.x + r.dx, r.y + r.dy) };
        });
    }""")
    assert r, "le banc ne voit aucune rampe"
    sens = {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}
    for rampe in r:
        attendu = sens[(rampe["dx"], rampe["dy"])]
        assert rampe["pied"] == attendu * 2, f"pied {rampe}"
        assert rampe["levre"] == attendu * 2 + 1, f"levre {rampe}"


def test_le_panneau_du_grand_saut_se_pose_sur_une_rampe(banc):
    """Le panneau se posait sur la premiere rampe trouvee en balayant la carte
    du coin haut-gauche. Les rampes ayant demenage, il aurait atterri a l'autre
    bout de la ville — il se pose maintenant sur la plus proche du depart."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.entites.find(function (e) { return e.type === 'panneau' && e.defi === 'saut'; });
        const c = L.Monde.carte;
        if (!p) return { trouve: false };
        const proches = (c.rampes || []).map(function (q) {
            return Math.abs(q.x * 16 - p.x) + Math.abs(q.y * 16 - p.y);
        }).sort(function (a, b) { return a - b; });
        const depart = c.apparition.joueur;
        const distances = (c.rampes || []).map(function (q) {
            return Math.abs(q.x - depart.x) + Math.abs(q.y - depart.y);
        }).sort(function (a, b) { return a - b; });
        const laSienne = (c.rampes || []).map(function (q) {
            return { d: Math.abs(q.x * 16 - p.x) + Math.abs(q.y * 16 - p.y),
                     depart: Math.abs(q.x - depart.x) + Math.abs(q.y - depart.y) };
        }).sort(function (a, b) { return a.d - b.d; })[0];
        return { trouve: true, colle: proches[0], sienne: laSienne.depart, plusProche: distances[0] };
    }""")
    assert r["trouve"], "aucun panneau pour Le Grand Saut : le defi est injouable"
    assert r["colle"] <= 5 * 16, f"le panneau est a {r['colle']} px de la rampe la plus proche"
    assert r["sienne"] == r["plusProche"], \
        "le panneau n'est pas sur la rampe la plus proche du depart"
