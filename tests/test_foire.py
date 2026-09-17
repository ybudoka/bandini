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
    """« Plus compacte » : l'enceinte ne prend pas le bloc entier, et DEDANS il
    n'y a pas de grand gazon vide.

    ⚠️ Le juge mesurait une SURFACE (52 × 31 ne passe plus sous 55 × 22), et ce
    n'était pas ce que Martin avait dit : sa capture montrait un terrain vague
    avec une roue perdue au milieu. Le petit train et la montagne russe ont
    demandé dix rangs de plus, et ils les REMPLISSENT. Ce qui se juge donc, c'est
    le vide : le plus grand carré de gazon où il n'y a rien — ni décor, ni allée,
    ni voie, ni montagne russe au-dessus. Mesuré : 7 × 7 sur la foire refaite que
    Martin a vue en ligne, 6 × 6 avec le train et la montagne russe. La première
    foire (sept objets sur 80 × 33) en avait des dizaines."""
    f = ville["foire"]
    largeur, hauteur = carte.FOIRE["enceinte"]
    assert f["l"] <= largeur and f["h"] <= hauteur, f"l'enceinte fait {f['l']} x {f['h']}"
    enclos = {(x, y) for y, x0, x1 in ville["foire_enclos"] for x in range(x0, x1 + 1)}
    plein = {(d["x"], d["y"]) for d in ville["decor"]}
    plein |= {(x, y) for x, y in enclos if ville["sol"][y][x] in "gT"}
    z = ville["montagne_russe"]["zone"]
    plein |= {(x, y) for x in range(z["x"], z["x"] + z["l"]) for y in range(z["y"], z["y"] + z["h"])}
    vide = 0
    for x, y in enclos:
        k = vide + 1
        while all((x + i, y + j) in enclos and (x + i, y + j) not in plein
                  for i in range(k) for j in range(k)):
            vide, k = k, k + 1
    assert vide <= 7, f"un gazon vide de {vide} x {vide} dans la foire"


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


def test_les_manèges_sont_a_l_echelle_de_la_grande_roue():
    """Retour de Martin, captures à l'appui : « grossis ça pour que ce soit
    proportionnel avec les autres manèges ». À 30 et 34 px de large, les tasses
    et les chaises volantes avaient la taille d'un kiosque à limonade, posées
    entre la grande roue (84 × 92) et la montagne russe.

    ⚠️ Et la BOÎTE AU SOL suit le plancher : un carrousel qui ne grandit qu'à
    l'écran, on marche sur ses chevaux. Les chaises volantes en sont dispensées
    — elles tournent en l'air, comme la roue."""
    roue_l, roue_h = mesure_de_dessin("grande_roue", "w"), mesure_de_dessin("grande_roue", "h")
    for nom in MANEGES:
        large = mesure_de_dessin(nom, "w")
        assert large >= 0.65 * roue_l, f"{nom} : {large} px de large, un jouet à côté de la roue ({roue_l})"
    assert mesure_de_dessin("chaises_volantes", "h") >= 0.7 * roue_h, "les chaises volantes tournent au ras du sol"
    for nom in ("carrousel", "tasses"):
        demi = boite_de_dessin(nom)[0]
        assert 2 * demi >= 0.8 * mesure_de_dessin(nom, "w"), f"{nom} : on marche sur le plancher"


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


# --- Le petit train et la montagne russe ------------------------------------------
#: Martin : « ajoute un petit train qui fait le tour de la foire et une énorme
#: montagne russe ».


def hauteur_de_dessin(nom):
    """La hauteur d'un décor, lue dans sa fiche de dessin (`sprites.js`)."""
    import re
    from pathlib import Path
    source = (Path(__file__).resolve().parent.parent / "static/js/sprites.js").read_text(encoding="utf-8")
    return int(re.search(nom + r": \{[^}]*?\bh: (\d+)", source).group(1))


def _fiche_de_dessin(nom):
    """La ligne de la fiche d'un décor dans `sprites.js`. ⚠️ `(?<!\\w)` : sans
    lui, `tasses` trouverait n'importe quel `…_tasses: {` plus haut."""
    import re
    from pathlib import Path
    source = (Path(__file__).resolve().parent.parent / "static/js/sprites.js").read_text(encoding="utf-8")
    return re.search(r"(?<!\w)" + nom + r": \{[^\n]*", source).group(0)


def mesure_de_dessin(nom, cle):
    """`w` ou `h` d'un décor, lu dans sa fiche."""
    import re
    return int(re.search(r"\b" + cle + r": (\d+)", _fiche_de_dessin(nom)).group(1))


def boite_de_dessin(nom):
    """La demi-boîte au sol (`sol`) d'un décor."""
    import re
    m = re.search(r"\bsol: \[(\d+), (\d+)\]", _fiche_de_dessin(nom))
    return int(m.group(1)), int(m.group(2))


def test_le_petit_train_fait_le_tour_de_la_foire(ville):
    """« Un petit train qui fait le tour de la foire. » Une voie FERMÉE d'une
    tuile d'épais, dans l'enceinte, qui entoure tout ce qui se visite — et
    l'arche est DEHORS : pour entrer, on traverse les rails."""
    voie = [tuple(t) for t in ville["train_de_foire"]["voie"]]
    assert len(set(voie)) == len(voie) >= 40
    for (ax, ay), (bx, by) in zip(voie, voie[1:] + voie[:1]):
        assert abs(ax - bx) + abs(ay - by) == 1, f"la voie saute de ({ax}, {ay}) à ({bx}, {by})"
    sol = ville["sol"]
    for x, y in voie:
        assert sol[y][x] == "T" and dans_l_enclos(ville, x, y), f"la voie sort de l'enceinte en ({x}, {y})"
    rails = {(x, y) for y, ligne in enumerate(sol) for x, g in enumerate(ligne) if g == "T"}
    assert rails == set(voie), "des rails qui ne sont pas sur la boucle"
    xs, ys = [x for x, _ in voie], [y for _, y in voie]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    f = ville["foire"]
    assert x1 - x0 >= f["l"] * 0.8 and y1 - y0 >= f["h"] * 0.7, "la voie ne fait pas le tour"
    for k in ville["kiosques_de_foire"]:
        assert x0 < k["x"] < x1 and y0 < k["y"] < y1, f"le kiosque {k['slug']} est hors du tour"
    roue = ville["roue"]
    assert x0 < roue["x"] < x1 and y0 < roue["y"] < y1, "la grande roue est hors du tour"
    b = next(x for x in ville["barrieres"] if x["slug"] == "foire")
    assert b["y"] > y1, "l'arche est à l'intérieur de la voie"
    # ⚠️ Et l'allée d'entrée la COUPE : la voie passe devant l'arche.
    assert (b["x"] + 1, y1) in rails
    assert sol[y1 - 1][b["x"] + 1] == "g" and sol[y1 + 1][b["x"] + 1] == "g", "l'allée d'entrée ne traverse pas la voie"


def test_rien_ne_se_pose_sur_la_voie_ni_contre(ville):
    """Un kiosque, une table ou un pied de montagne russe CONTRE les rails, et
    un wagon le frôle ou le traverse. Une tuile de dégagement tout autour."""
    voie = {tuple(t) for t in ville["train_de_foire"]["voie"]}
    for d in ville["decor"]:
        contre = [(d["x"] + dx, d["y"] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                  if (d["x"] + dx, d["y"] + dy) in voie]
        assert not contre, f"un {d['type']} contre la voie en ({d['x']}, {d['y']})"


def test_la_montagne_russe_est_la_plus_grosse_chose_de_la_ville(ville):
    """« Une ÉNORME montagne russe. » Plus haute que la grande roue, et de loin ;
    plus large que l'écran (30 tuiles). Et elle est DANS la foire : tout ce
    qu'elle survole est dans l'enceinte, et pas sur la voie du train."""
    mr = ville["montagne_russe"]
    haut = max(p[2] for p in mr["voie"])
    assert haut >= 1.5 * hauteur_de_dessin("grande_roue"), f"{haut} px de haut : elle n'écrase pas la grande roue"
    assert mr["zone"]["l"] > 30, "elle tient dans l'écran"
    voie_du_train = {tuple(t) for t in ville["train_de_foire"]["voie"]}
    for x, y, _z in mr["voie"]:
        tuile = (int(x // 16), int((y - 4) // 16))
        assert dans_l_enclos(ville, *tuile), f"elle survole le dehors en {tuile}"
        assert tuile not in voie_du_train, f"elle pose sur la voie du train en {tuile}"


def test_la_montagne_russe_a_sa_chaine_et_son_looping(ville):
    """La chaîne monte D'UN TRAIT ce qui fait toute la descente, et le looping
    est un vrai tour : dans le plan x-z, la voie tourne de 360°, et son sommet
    est à deux rayons de son creux."""
    import math
    mr = ville["montagne_russe"]
    v, fiche = mr["voie"], carte.FOIRE["montagne_russe"]
    c0, c1 = mr["chaine"]
    assert all(v[i + 1][2] >= v[i][2] - 0.05 for i in range(c0, c1)), "la chaîne redescend"
    assert v[c1][2] - v[c0][2] >= 0.8 * fiche["hauteur_px"], "la chaîne ne monte pas au sommet"
    b0, b1 = mr["boucle"]
    tour, avant = 0.0, None
    for i in range(b0, b1):
        angle = math.atan2(v[i + 1][2] - v[i][2], v[i + 1][0] - v[i][0])
        if avant is not None:
            tour += (angle - avant + math.pi) % (2 * math.pi) - math.pi
        avant = angle
    assert abs(tour) >= 2 * math.pi * 0.9, f"le looping ne tourne que de {math.degrees(abs(tour)):.0f}°"
    hauteurs = [p[2] for p in v[b0:b1 + 1]]
    assert max(hauteurs) - min(hauteurs) >= 1.9 * fiche["boucle_px"]
    # La voie est régulière et fermée : un point tous les `pas_px`, en 3D.
    for i in range(len(v)):
        pas = math.dist(v[i], v[(i + 1) % len(v)])
        assert pas <= fiche["pas_px"] * 1.6, f"la voie saute de {pas:.1f} px au point {i}"


def test_la_montagne_russe_tient_sur_ses_pieds(ville):
    """⚠️ Elle est EN L'AIR : on passe dessous. Tout ce qui est plus haut que
    son lit a un pied d'acier à moins d'une longueur et demie de pied — sauf le
    haut du looping, qui ne repose sur rien. Les pieds sont des décors solides,
    sur le gazon de la foire : jamais sur une allée (on passe sous la voie, pas
    au travers d'un tréteau)."""
    mr = ville["montagne_russe"]
    fiche = carte.FOIRE["montagne_russe"]
    v, n, pas = mr["voie"], len(mr["voie"]), fiche["pas_px"]
    pieds = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] == "pied_montagne_russe"}
    assert pieds == {(tx, ty) for _i, tx, ty in mr["supports"]}, "un pied sans décor, ou un décor sans pied"
    assert "pied_montagne_russe" in carte.DECOR_SOLIDE
    for x, y in pieds:
        assert ville["sol"][y][x] == "," and dans_l_enclos(ville, x, y), f"un pied sur ({x}, {y})"
    portes = [i for i, _tx, _ty in mr["supports"]]
    assert len(portes) >= 12
    b0, b1 = mr["boucle"]
    for i, (_x, _y, z) in enumerate(v):
        if z <= fiche["pied_des_px"] or (b0 <= i <= b1 and z > 8 + fiche["boucle_px"]):
            continue
        loin = min(min(abs(i - j), n - abs(i - j)) for j in portes) * pas
        assert loin <= 1.5 * fiche["pied_px"], f"la voie flotte à {z:.0f} px, à {loin} px de son pied (point {i})"


# --- Au banc : ils roulent ------------------------------------------------------


def test_le_train_fait_le_tour_sans_quitter_ses_rails(banc, paquet):
    """Un tour complet, chaque wagon toujours sur une tuile de voie, et attelés :
    l'écart d'un wagon au suivant ne bouge pas (un peu moins en courbe, la
    corde)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const F = L.Foire, t = F.train, d = t.def, TT = L.TT;
        const rails = new Set(d.voie.map(function (c) { return c[0] + ',' + c[1]; }));
        let parcouru = 0, hors = 0, ecartMin = 1e9, ecartMax = 0, images = 0;
        while (parcouru < t.n + 20 && images < 6000) {
          const avant = t.s;
          F.maj(); images++;
          parcouru += (t.s - avant + t.n) % t.n;
          const liste = F.wagons();
          liste.forEach(function (p, k) {
            if (!rails.has(Math.floor(p.x / TT) + ',' + Math.floor(p.y / TT))) hors++;
            if (k > 0) {
              const e = Math.hypot(p.x - liste[k - 1].x, p.y - liste[k - 1].y);
              ecartMin = Math.min(ecartMin, e); ecartMax = Math.max(ecartMax, e);
            }
          });
        }
        // Et dans le jeu, c'est la boucle qui le fait avancer.
        const s0 = t.s; o.frame(30);
        return { parcouru: parcouru, n: t.n, images: images, hors: hors, ecartMin: ecartMin, ecartMax: ecartMax,
                 ecart: d.ecart_px, wagons: F.wagons().length, attendus: d.wagons + 1,
                 dansLeJeu: (t.s - s0 + t.n) % t.n };
    }""")
    assert r["parcouru"] >= r["n"], f"le train n'a pas fait le tour : {r}"
    assert r["hors"] == 0, f"{r['hors']} fois un wagon hors des rails"
    assert r["wagons"] == r["attendus"] >= 4
    assert r["ecart"] * 0.8 <= r["ecartMin"] and r["ecartMax"] <= r["ecart"] + 0.5, r
    assert r["dansLeJeu"] > 10, "la boucle du jeu ne fait pas avancer le train"


def test_le_train_s_arrete_devant_quelqu_un_et_siffle(banc, paquet):
    """⚠️ Un train de foire ne renverse personne. Planté sur les rails devant la
    locomotive, on la voit s'arrêter avant de nous toucher, siffler, et repartir
    quand on s'écarte. On n'a pas bougé d'un pixel et pas perdu un point de vie."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const F = L.Foire, t = F.train, j = L.B.joueur, f = L.Monde.carte.def.foire, TT = L.TT;
        let sifflets = 0;
        const vrai = L.Son.SFX.sifflet_train;
        L.Son.SFX.sifflet_train = function () { sifflets++; return vrai.apply(null, arguments); };
        const p = F.pointDuTrain(t.s + 70);
        j.x = p.x; j.y = p.y; j.invincible = 999999;
        L.Monde.centrerCamera(j.x, j.y);
        const vie = j.vie;
        let pres = 1e9;
        for (let i = 0; i < 300; i++) {
          o.frame(1);
          const loco = F.pointDuTrain(t.s);
          pres = Math.min(pres, Math.hypot(loco.x - j.x, loco.y - j.y));
        }
        const bouge = Math.hypot(j.x - p.x, j.y - p.y), arrete = t.v === 0 && t.bloque;
        // On s'écarte : au milieu de l'allée.
        j.x = (f.x + Math.floor(f.l / 2)) * TT + 8; j.y = (L.Monde.carte.def.kiosques_de_foire[0].y + 2) * TT + 8;
        const s0 = t.s;
        o.frame(120);
        return { pres: pres, bouge: bouge, arrete: arrete, sifflets: sifflets, vie: vie, vieApres: j.vie,
                 repart: (t.s - s0 + t.n) % t.n };
    }""")
    assert r["arrete"], f"le train ne s'est pas arrêté : {r}"
    assert r["pres"] >= 12, f"la locomotive est venue à {r['pres']:.1f} px"
    assert r["bouge"] < 0.5, f"le train nous a poussés de {r['bouge']:.1f} px"
    assert r["vieApres"] == r["vie"]
    assert r["sifflets"] >= 1, "il ne siffle pas"
    assert r["repart"] > 20, "il ne repart pas quand on s'écarte"


def test_on_ne_passe_pas_a_travers_un_wagon(banc, paquet):
    """On marche droit sur le flanc d'un wagon arrêté : on s'y bute, on ne le
    traverse pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const F = L.Foire, t = F.train, d = t.def, j = L.B.joueur, TT = L.TT;
        const k = L.Monde.carte.def.kiosques_de_foire[0];
        // Le train arrêté, le 2e wagon sur la voie ouest, à la hauteur de l'allée.
        const voie = d.voie, x0 = Math.min.apply(null, voie.map(function (c) { return c[0]; }));
        const cible = { x: x0 * TT + 8, y: (k.y + 2) * TT + 8 };
        let meilleur = 0, loin = 1e9;
        for (let s = 0; s < t.n; s++) {
          const q = F.pointDuTrain(s - 2 * d.ecart_px), e = Math.hypot(q.x - cible.x, q.y - cible.y);
          if (e < loin) { loin = e; meilleur = s; }
        }
        t.s = meilleur; d.vitesse = 0; t.v = 0;
        const w = F.wagons()[2];
        j.x = w.x + 30; j.y = w.y; j.invincible = 999999;
        L.Monde.centrerCamera(j.x, j.y);
        L.Entites.indexer();
        let plusPres = 1e9;
        o.touche('KeyA');
        for (let i = 0; i < 90; i++) { o.frame(1); plusPres = Math.min(plusPres, j.x - w.x); }
        o.relacher('KeyA');
        return { plusPres: plusPres, depart: 30, r: j.r, verticale: Math.abs(Math.cos(w.a)) };
    }""")
    assert r["verticale"] < 0.1, "le wagon choisi n'est pas sur la voie ouest"
    assert r["plusPres"] < r["depart"] - 5, f"on n'a pas marché : {r}"
    assert r["plusPres"] >= 5 + r["r"] - 0.5, f"on est entré dans le wagon ({r['plusPres']:.1f} px de son axe)"


def test_la_montagne_russe_monte_au_pas_et_plonge(banc, paquet):
    """La chaîne au pas, la descente à toute allure, le looping passé sans la
    vitesse plancher (⚠️ c'est la gravité qui le passe, pas la ceinture), et
    quatre secondes en gare à chaque tour."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const F = L.Foire, m = F.montagne, d = m.def;
        const dans = function (tr, i) { return i >= tr[0] && i <= tr[1]; };
        let chaine = [], vMax = 0, boucleMin = 1e9, enGare = 0, gares = [], images = 0;
        const tours0 = m.tours;
        while (m.tours < tours0 + 2 && images < 8000) {
          // La vitesse d'une image se decide a l'endroit d'OU l'on part.
          const i = F.pointDeMontagne(m.s).i;
          F.maj(); images++;
          if (m.attente > 0) { enGare++; continue; }
          if (enGare) { gares.push(enGare); enGare = 0; }
          if (dans(d.chaine, i)) chaine.push(m.v);
          if (dans(d.boucle, i)) boucleMin = Math.min(boucleMin, m.v);
          vMax = Math.max(vMax, m.v);
        }
        return { tours: m.tours - tours0, images: images, chaineMin: Math.min.apply(null, chaine),
                 chaineMax: Math.max.apply(null, chaine), vMax: vMax, boucleMin: boucleMin, gares: gares,
                 d: { chaine: d.vitesse_chaine, vitesse_min: d.vitesse_min, gare_images: d.gare_images } };
    }""")
    d = r["d"]
    assert r["tours"] == 2, f"elle ne boucle pas ses tours : {r}"
    assert r["chaineMin"] == r["chaineMax"] == d["chaine"], "la chaîne ne tire pas au pas"
    assert r["vMax"] >= 5 * d["chaine"], f"elle ne plonge pas : {r['vMax']:.2f} px/image au plus"
    assert r["boucleMin"] > d["vitesse_min"] + 0.5, f"le looping ne passe que par la vitesse plancher : {r['boucleMin']:.2f}"
    assert r["gares"] and all(g >= d["gare_images"] - 1 for g in r["gares"]), r["gares"]


def test_la_foire_qui_roule_ne_tire_aucun_de(banc, paquet):
    """⚠️ Chaque dé consommé décale tous ceux qui suivent : le train, les
    chariots, leur dessin et leurs collisions n'en tirent aucun."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const F = L.Foire, B = L.B, j = B.joueur;
        let tires = 0;
        const vrai = B.rng;
        B.rng = function () { tires++; return vrai(); };
        const p = F.pointDuTrain(F.train.s + 40);
        j.x = p.x; j.y = p.y;
        for (let i = 0; i < 3000; i++) {
          F.maj();
          F.bloquer(j);
          F.ajouterVisibles([], F.montagne.ox, F.montagne.oy);
        }
        B.rng = vrai;
        return tires;
    }""")
    assert r == 0, f"{r} dés tirés"


def test_on_voit_la_montagne_russe_meme_quand_son_pied_est_hors_champ(banc, paquet):
    """⚠️ Son sommet dépasse de neuf tuiles au-dessus de sa rangée : le tri des
    entités (40 px de marge sous l'écran) l'aurait effacée dès que son pied
    sortait par le bas, sommet à l'écran. Et on la dessine pour de vrai."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const F = L.Foire, m = F.montagne, VH = L.VH;
        const cy = m.ySud - VH - 40, cx = m.ox + 40;
        const vus = [];
        F.ajouterVisibles(vus, cx, cy);
        const moities = vus.filter(function (e) { return e.id < 900000002; }).length;
        const avant = L.B.stats.images;
        vus.forEach(function (e) { e.peindreFoire(L.Base.nouveauCanvas(8, 8).getContext('2d')); });
        return { moities: moities, sommet: m.oy, ecranBas: cy + VH, images: L.B.stats.images - avant };
    }""")
    assert r["sommet"] < r["ecranBas"], "le juge ne regarde pas le sommet"
    assert r["moities"] == 2, f"la montagne russe disparaît quand son pied sort de l'écran : {r}"
    assert r["images"] >= 2


def test_la_voie_se_peint_droite_en_courbe_et_en_passage_a_niveau(banc, paquet):
    """La tuile de voie lit ses voisines : droite, en courbe dans les quatre
    coins, et des planches là où l'allée d'entrée la traverse. ⚠️ Une courbe
    peinte en équerre sous un train qui tourne rond, c'est un train qui
    déraille."""
    r = banc("""function (L, o) {
        const d = L.B.defs.carte, voie = d.train_de_foire.voie, M = L.Monde;
        const masques = {};
        let planches = 0;
        for (const c of voie) {
          const v = M.varianteDeRail(c[0], c[1]);
          masques[v & 15] = (masques[v & 15] || 0) + 1;
          if (v & 16) planches++;
        }
        function traces(v) {
          const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d');
          ctx.traces = [];
          L.TUILES.T(ctx, v, L.TT);
          return JSON.stringify(ctx.traces);
        }
        const peints = [10, 5, 3, 6, 12, 9].map(traces);
        return { masques: masques, planches: planches, differents: new Set(peints).size,
                 planche: traces(10 | 16) !== traces(10) };
    }""")
    assert {int(k) for k in r["masques"]} == {10, 5, 3, 6, 12, 9}, r["masques"]
    assert all(r["masques"][k] == 1 for k in ("3", "6", "12", "9")), "une boucle a quatre coins"
    assert r["planches"] == 3, "l'allée d'entrée (trois tuiles) ne croise pas la voie sur des planches"
    assert r["differents"] == 6 and r["planche"]
