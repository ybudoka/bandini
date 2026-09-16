"""Le bord de l'eau, 4e vague — la foire de La Pointe.

⚠️ **« Une foire, c'est beaucoup de choses et beaucoup de monde. »** Retour de
Martin, capture à l'appui : la première version posait sept objets au hasard sur
80 × 33 tuiles de gazon (« c'est assez décevant »). Puis, dans l'ordre : « plein
de kiosques, de vendeurs, de mascottes », « de l'exagération », « clôturée — pas
un carré, des clôtures asymétriques — et une entrée avec une arche, et ça doit
coûter quelque chose d'entrer », « plus compacte ». Ces juges tiennent chacune de
ces phrases.
"""

import pytest

from app import carte, economie

MANEGES = ("carrousel", "tasses", "chaises_volantes")
JEUX = ("galerie_tir", "marteau_force", "peche_canards")


@pytest.fixture(scope="module")
def ville():
    return carte.exporter()


def fuite_de_la_foire(ville, sol):
    """Remplit l'intérieur à 4-voisinage sans traverser la clôture ni l'arche :
    rend la première tuile du DEHORS atteinte, ou None."""
    b = next(x for x in ville["barrieres"] if x["slug"] == "foire")
    arche = {(x, b["y"]) for x in range(b["x"], b["x"] + b["l"])}
    enclos = {(x, y) for y, x0, x1 in ville["foire_enclos"] for x in range(x0, x1 + 1)}
    depart = next(iter(enclos))
    vus, pile = {depart}, [depart]
    while pile:
        x, y = pile.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in vus or (nx, ny) in arche:
                continue
            glyphe = sol[ny][nx]
            if glyphe == "f" or carte.LEGENDE[glyphe].get("solide") in (1, 3):
                continue
            if (nx, ny) not in enclos:
                return (nx, ny)
            vus.add((nx, ny))
            pile.append((nx, ny))
    return None


def dans_l_enclos(ville, x, y):
    return any(b[0] == y and b[1] <= x <= b[2] for b in ville["foire_enclos"])


def test_la_pointe_a_une_foire_et_une_seule():
    pointe = next(d for d in carte.DISTRICTS if d["slug"] == "pointe")
    assert sum(ligne.count("f") for ligne in pointe["plan"]) == 1
    assert sum(ligne.count("f") for d in carte.DISTRICTS for ligne in d["plan"]) == 1
    assert sum(ligne.count("n") for ligne in pointe["plan"]) >= 1, "la foire a mangé tout le bois"


def test_la_foire_est_compacte(ville):
    """« Plus compacte » : l'enceinte ne prend pas le bloc entier, elle en prend
    le milieu — et le reste redevient le bois de La Pointe."""
    f = ville["foire"]
    largeur, hauteur = carte.FOIRE["enceinte"]
    assert f["l"] <= largeur and f["h"] <= hauteur, f"l'enceinte fait {f['l']} x {f['h']}"
    # L'écran fait 30 × 17 tuiles : une foire compacte se voit presque en entier.
    assert f["l"] * f["h"] <= 55 * 22, "la foire s'étale"


def test_plein_de_kiosques_et_les_manèges_en_double(ville):
    """« Plein de kiosques » et « de l'exagération ». ⚠️ Et c'est la DENSITÉ qui
    dit « foire », pas les objets : la première version en avait sept."""
    kiosques = ville["kiosques_de_foire"]
    assert len(kiosques) >= 20, f"{len(kiosques)} kiosques : ce n'est pas plein"
    assert len({k["slug"] for k in kiosques}) >= 10, "tous les kiosques vendent la même chose"
    decor = [d for d in ville["decor"] if dans_l_enclos(ville, d["x"], d["y"])]
    for quoi in MANEGES:
        assert sum(1 for d in decor if d["type"] == quoi) >= 2, f"{quoi} n'est pas en double"
    assert sum(1 for d in ville["decor"] if d["type"] == "grande_roue") == 1
    # Un jeu d'adresse n'est posé qu'une fois : c'est un défi, il a un panneau.
    for quoi in JEUX:
        assert sum(1 for k in kiosques if k["slug"] == quoi) == 1, f"{quoi} posé deux fois"


def test_l_allee_est_illuminee(ville):
    """⚠️ Une foire éteinte à 21 h 50, c'était la capture de Martin. Une guirlande
    tous les DEUX kiosques, au halo assez large pour couvrir le voisin : une par
    comptoir dépassait le plafond de 50 lumières du rendu, et les feux du
    carrefour d'à côté se seraient éteints."""
    sortes = set(carte.FOIRE["lampes"])
    lampes = [(lampe["x"], lampe["y"], lampe["r"]) for lampe in ville["lampes"] if lampe.get("c") in sortes]
    assert len(lampes) >= 12, "la foire est dans le noir"
    for k in ville["kiosques_de_foire"]:
        eclaire = any(((lx - k["x"]) * 16) ** 2 + ((ly - k["y"] + 1) * 16) ** 2 <= r * r
                      for lx, ly, r in lampes)
        assert eclaire, f"le kiosque {k['slug']} en ({k['x']}, {k['y']}) est dans le noir"


def test_tout_ce_qui_est_de_la_foire_est_dans_l_enceinte(ville):
    """La palissade clôt la foire : rien de ce qui en fait partie n'est dehors, et
    rien n'est sur l'eau ni sur la chaussée."""
    for k in ville["kiosques_de_foire"]:
        assert dans_l_enclos(ville, k["x"], k["y"]), f"{k['slug']} est hors de l'enceinte"
    roue = ville["roue"]
    assert dans_l_enclos(ville, roue["x"], roue["y"]), "la grande roue est dehors"
    for d in ville["decor"]:
        if d["type"] in MANEGES + ("table_pique_nique",) and ville["foire"]["x"] <= d["x"] < ville["foire"]["x"] + ville["foire"]["l"]:
            glyphe = ville["sol"][d["y"]][d["x"]]
            assert not carte.LEGENDE[glyphe].get("route") and glyphe != "~", d


def test_la_cloture_n_est_pas_un_carre(ville):
    """⚠️ « Pas un carré, des clôtures asymétriques. » La palissade rentre de 0 à
    2 tuiles par marches : le bord ouest de l'enceinte ne tombe pas à la même
    colonne d'une rangée à l'autre, ni le bord nord d'une colonne à l'autre."""
    rangees: dict[int, list[int]] = {}
    for y, x0, x1 in ville["foire_enclos"]:
        rangees.setdefault(y, []).extend([x0, x1])
    ouest = {min(xs) for xs in rangees.values()}
    est = {max(xs) for xs in rangees.values()}
    assert len(ouest) > 1 or len(est) > 1, "la palissade est un rectangle"
    f = ville["foire"]
    sol = ville["sol"]
    palissade = [(x, y) for y in range(f["y"], f["y"] + f["h"])
                 for x in range(f["x"], f["x"] + f["l"]) if sol[y][x] == "f"]
    assert len(palissade) > 100, "la foire n'est pas clôturée"
    # Le nord : la première rangée de palissade n'est pas la même partout.
    nord = {min(y for x2, y in palissade if x2 == x) for x in {x for x, _ in palissade}}
    assert len(nord) > 1, "le bord nord de la palissade est droit d'un bout à l'autre"


def test_l_arche_est_a_l_ouverture_et_elle_se_paie(ville):
    """« Une entrée avec une arche, et ça doit coûter quelque chose d'entrer. »
    L'arche est à cheval sur la seule ouverture de la palissade, et la barrière
    de l'arche est une fiche comme les autres — `payer`, le prix vient de
    `economie.FOIRE`, et resquiller coûte l'étoile de `forcer`."""
    b = next(x for x in ville["barrieres"] if x["slug"] == "foire")
    assert b["condition"] == {"payer": "foire"}
    assert b["prix"] == economie.FOIRE["entree"] > 0
    assert b["forcer"] == {"etoiles": economie.FOIRE["etoiles_resquille"]}
    assert b["dedans"] == "N"
    sol = ville["sol"]
    for x in range(b["x"], b["x"] + b["l"]):
        assert sol[b["y"]][x] != "f", "l'ouverture de l'arche est bouchée"
    # De part et d'autre de l'ouverture : la clôture.
    assert sol[b["y"]][b["x"] - 1] == "f" and sol[b["y"]][b["x"] + b["l"]] == "f"
    arche = [d for d in ville["decor"] if d["type"] == "portique_foire"]
    assert len(arche) == 1
    assert (arche[0]["x"], arche[0]["y"]) == (b["x"] + 1, b["y"]), "l'arche n'est pas à l'ouverture"


def test_on_n_entre_que_par_l_arche(ville):
    """⚠️ **LE JUGE QUI COMPTE, et il est né d'un vrai trou.** La première
    palissade sautait toute tuile déjà occupée par un décor : une table posée
    sur le bord laissait une tuile de gazon dans la clôture, et on entrait dans
    la foire sans passer par l'arche. Personne ne l'aurait vu à l'œil — c'est un
    juge qui cherchait où sauter qui l'a trouvé.

    Le juge remplit l'intérieur à 4-voisinage sans traverser la palissade ni
    l'ouverture de l'arche : il ne doit JAMAIS atteindre le dehors."""
    fuite = fuite_de_la_foire(ville, ville["sol"])
    assert fuite is None, f"la clôture a un trou : on sort (et on entre) par {fuite}"


def test_le_juge_de_la_cloture_voit_un_trou_quand_il_y_en_a_un(ville):
    """⚠️ **Le rouge-avant, prouvé autrement — et il faut dire pourquoi.** Le trou
    d'origine venait d'une table posée sur le bord ; depuis que la cour à manger a
    été déplacée, remettre le défaut ne rouvre plus de trou sur la graine livrée,
    et le juge d'au-dessus passerait même sans la correction. On prouve donc
    qu'il SAIT voir un trou : on en perce un, loin de l'arche, et il doit fuir."""
    b = next(x for x in ville["barrieres"] if x["slug"] == "foire")
    sol = [list(ligne) for ligne in ville["sol"]]
    x = b["x"] + b["l"] + 4
    y = next(yy for yy in range(b["y"] - 3, b["y"] + 1) if sol[yy][x] == "f")
    sol[y][x] = ","
    assert fuite_de_la_foire(ville, ["".join(r) for r in sol]) is not None, (
        "le juge ne voit pas un trou percé dans la clôture")


def test_la_foire_ne_tire_pas_dans_le_de_de_la_ville():
    chantier = carte._Chantier(carte.PLAN, carte.GRAINE)
    for y in range(4, 40):
        for x in range(4, 90):
            chantier.sol[y][x] = ","
    avant_ville, avant_foire = chantier.des.etat, chantier.des_foire.etat
    chantier._foire(6, 6, 80, 33)
    assert chantier.des.etat == avant_ville, "la foire a tiré dans le dé de la ville"
    assert chantier.des_foire.etat != avant_foire
    assert chantier.roue and chantier.foire_entree and chantier.foire_enclos


# --- Au banc ---------------------------------------------------------------------

ARCHE = """
    function arche(L) { return L.Monde.barrieres().find(function (q) { return q.slug === 'foire'; }); }
"""


def test_on_paie_a_l_arche_une_fois_par_jour_et_on_ressort_librement(banc, paquet):
    """⚠️ **Un billet par JOUR**, pas par passage : une foire qui refacture chaque
    aller-retour au hot-dog d'en face est un péage. Et on RESSORT sans payer —
    une barrière qui se paie ne doit pas enfermer."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const b = arche(L), TT = L.TT, j = L.B.joueur, p = L.B.partie;
        p.argent = 100;
        // Dehors, sous l'arche : on se bute, le billet se prend.
        j.x = (b.x + 1) * TT + 8; j.y = (b.y + 1) * TT + 8;
        const fermeeAvant = L.Monde.barriereFermee(b);
        const bloque = L.Monde.barriereBloque(j, b.x + 1, b.y);
        const argent1 = p.argent;
        // Deuxième passage, même jour : rien.
        const bloque2 = L.Monde.barriereBloque(j, b.x + 1, b.y);
        const argent2 = p.argent;
        // Le lendemain, on ressort du DEDANS sans billet : libre.
        p.jour += 1;
        j.x = (b.x + 1) * TT + 8; j.y = (b.y - 1) * TT + 8;
        const sortie = L.Monde.barriereBloque(j, b.x + 1, b.y);
        const argent3 = p.argent;
        // Et sans argent, dehors : l'arche arrête.
        p.argent = 3;
        j.x = (b.x + 1) * TT + 8; j.y = (b.y + 1) * TT + 8;
        const fauche = L.Monde.barriereBloque(j, b.x + 1, b.y);
        return { fermeeAvant: fermeeAvant, bloque: bloque, argent1: argent1, bloque2: bloque2,
                 argent2: argent2, sortie: sortie, argent3: argent3, fauche: fauche,
                 prix: b.prix, raison: j.bute ? j.bute.raison : null };
    }""" % ARCHE)
    assert r["fermeeAvant"] is True, "l'arche est ouverte sans billet"
    assert r["bloque"] is False and r["argent1"] == 100 - r["prix"], "le billet ne s'est pas pris"
    assert r["bloque2"] is False and r["argent2"] == r["argent1"], "on a payé deux fois le même jour"
    assert r["sortie"] is False and r["argent3"] == r["argent2"], "on paie pour SORTIR de la foire"
    assert r["fauche"] is True, "on entre sans argent"


def test_resquiller_par_la_cloture_coute_une_etoile(banc, paquet):
    """⚠️ La clôture s'enjambe comme toutes celles du jeu — un mur qui
    ment serait pire. Mais la retombée DANS la foire sans billet coûte l'étoile
    de l'arche : c'est le prix de ne pas payer le prix. Avec son billet, rien."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const b = arche(L), TT = L.TT, j = L.B.joueur, p = L.B.partie;
        // Une tuile de palissade du sud, loin de l'arche, avec la foire derrière.
        let cloture = null;
        for (let dx = 2; dx < 24 && !cloture; dx++) {
          for (const x of [b.x + b.l + dx, b.x - 1 - dx]) {
            for (let y = b.y - 3; y <= b.y + 3; y++) {
              if (L.Monde.glyphe(x, y) === 'f' && L.Monde.dansLaFoire(x, y - 1)
                  && !L.Monde.dansLaFoire(x, y + 1) && L.Monde.marchablePieton(x, y + 1)) { cloture = { x: x, y: y }; break; }
            }
            if (cloture) break;
          }
        }
        if (!cloture) return { cloture: false };
        function sauter() {
          L.B.recherche.etoiles = 0;
          j.enjambe = null; j.z = 0;
          // ⚠️ CONTRE la palissade, pas au milieu de la tuile d'en dessous : la
          // cloture se cherche a `r + 2` pixels devant soi, et depuis le centre
          // d'une tuile de seize ces sept pixels retombent dans la tuile ou l'on
          // est deja — le juge croyait sauter une cloture qu'il ne touchait pas.
          j.x = cloture.x * TT + 8; j.y = (cloture.y + 1) * TT + j.r + 0.5;
          L.Entites.indexer();
          const parti = L.Entites.enjamber(j, 0, -1);
          for (let i = 0; i < 80 && j.enjambe; i++) L.Entites.majEnjambe(j);
          return { parti: parti, etoiles: L.B.recherche.etoiles, dedans: L.Monde.dansLaFoire(Math.floor(j.x / TT), Math.floor(j.y / TT)) };
        }
        p.billets = {};
        const sansBillet = sauter();
        p.billets = { foire: p.jour };
        const avecBillet = sauter();
        return { cloture: true, sans: sansBillet, avec: avecBillet };
    }""" % ARCHE)
    assert r["cloture"], "aucune tuile de palissade à enjamber"
    assert r["sans"]["parti"] and r["sans"]["dedans"], "on n'a pas franchi la palissade"
    assert r["sans"]["etoiles"] >= 1, "resquiller n'a rien coûté"
    assert r["avec"]["etoiles"] == 0, "on paie une étoile avec son billet en poche"


def test_la_foire_se_remplit_de_monde_et_de_mascottes(banc, paquet):
    """« Beaucoup de monde », « des mascottes ». ⚠️ Ils naissent DANS l'enceinte,
    y restent, et personne n'apparaît sous les yeux du joueur. Au premier essai,
    la foule naissait au bout de la foire, hors de la bulle — et `peupler`
    l'effaçait à l'image suivante : six forains sur trente."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, TT = L.TT, f = L.Monde.carte.def.foire, k = L.Monde.carte.def.kiosques_de_foire;
        B.joueur.x = (f.x + 20) * TT + 8; B.joueur.y = (k[0].y + 1) * TT + 8;
        B.joueur.invincible = 999999;
        L.Monde.centrerCamera(B.joueur.x, B.joueur.y);
        let vus = 0, salue = false;
        for (let i = 0; i < 900; i++) {
          o.frame(1);
          // ⚠️ On GUETTE le salut pendant toute la mesure : a la derniere image,
          // il se peut qu'aucune mascotte ne soit arretee — ca mesurait l'instant.
          if (!salue) salue = B.entites.some(function (e) {
            return e.metier === 'mascotte' && e.etat === 'arret' && (e.poseFixe === 3 || e.poseFixe === 4); });
          for (const e of B.entites) if ((e.metier === 'forain' || e.metier === 'mascotte') && e.t < 2
                                            && L.Entites.visibleAEcran(e.x, e.y, 0)) vus++;
        }
        const gens = B.entites.filter(function (e) { return e.metier === 'forain' || e.metier === 'mascotte'; });
        const dehors = gens.filter(function (e) {
          return !L.Monde.dansLaFoire(Math.floor(e.x / TT), Math.floor(e.y / TT)); }).length;
        const mascottes = gens.filter(function (e) { return e.metier === 'mascotte'; });
        return { forains: gens.length - mascottes.length, mascottes: mascottes.length, dehors: dehors,
                 vus: vus, salue: salue, voulus: B.defs.pietons.foule_de_foire };
    }""")
    assert r["forains"] >= r["voulus"]["forains"] * 0.8, f"{r['forains']} forains : ce n'est pas beaucoup de monde"
    assert r["mascottes"] == r["voulus"]["mascottes"], "il manque des mascottes"
    assert r["dehors"] <= 2, f"{r['dehors']} forains sont sortis de l'enceinte"
    assert r["vus"] == 0, "quelqu'un est apparu à l'écran"
    assert r["salue"], "aucune mascotte ne salue"


def test_les_manèges_tournent_et_on_n_y_monte_pas(banc, paquet):
    r = banc("""function (L, o) {
        const out = {};
        for (const nom of %s) {
          const d = L.DECORS[nom];
          out[nom] = d ? { anime: d.anime || 0, variantes: d.variantes || 0,
                           arrete: d.arrete || 0, pv: d.pv || 0, solide: !!d.solide } : null;
        }
        return out;
    }""" % list(MANEGES + ("grande_roue",)))
    for nom, d in r.items():
        assert d, f"{nom} n'a aucun dessin"
        assert d["anime"] > 0 and d["variantes"] > 1, f"{nom} ne tourne pas"
        assert d["arrete"] > 0 and d["pv"] == 0 and d["solide"], nom


def test_chaque_kiosque_a_un_vendeur_peint(banc, paquet):
    """« Plein de vendeurs. » ⚠️ Peints dans le kiosque, pas posés comme des
    entités — et deux kiosques voisins n'ont pas le même visage : la variante
    se tire à l'empreinte de la tuile."""
    r = banc("""function (L, o) {
        const out = {};
        for (const k of L.B.defs.carte.kiosques_de_foire) {
          const d = L.DECORS[k.slug];
          out[k.slug] = d ? { variantes: d.variantes || 0, peint: typeof d.peindre } : null;
        }
        return out;
    }""")
    for slug, d in r.items():
        assert d, f"le kiosque {slug} n'a pas de dessin"
        assert d["peint"] == "function"
        if slug not in JEUX:
            assert d["variantes"] >= 4, f"{slug} a toujours le même vendeur"
