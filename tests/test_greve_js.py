"""Le bord de l'eau, 1re vague — au banc.

⚠️ **Aucun juge de géométrie ne parlait du sable** : un décor de plage vit à deux
tuiles de l'eau, là où aucun décor n'allait jamais. C'était une ligne de juge à
écrire *exprès*, pas à découvrir.
"""

MEUBLES = ("parasol", "serviette", "table_pique_nique", "chateau_sable",
           "poteau_amarrage", "belvedere", "bouee")


def test_chaque_meuble_de_greve_a_un_dessin(banc, paquet):
    """Un décor sans fiche `DECORS` est **invisible** — `dessiner` fait
    `if (!d) continue`, sans un mot. Six fiches semées et cinq dessinées, ça ne
    se voit pas dans un test Python : ça se voit à l'écran, ou jamais."""
    r = banc("""function (L, o) {
        const out = {};
        for (const quoi of %s) {
          const d = L.DECORS[quoi];
          out[quoi] = d ? { w: d.w, h: d.h, ancre: !!d.ancre, peint: typeof d.peindre } : null;
        }
        return out;
    }""" % list(MEUBLES))
    for quoi in MEUBLES:
        d = r[quoi]
        assert d, f"{quoi} est semé dans la ville et n'a aucun dessin"
        assert d["peint"] == "function", f"{quoi} n'a pas de peintre"
        assert d["ancre"] and d["w"] > 0 and d["h"] > 0, f"{quoi} : {d}"


def test_seule_la_bouee_declare_flotter(banc, paquet):
    """⚠️ Le seul décor du jeu qui ait raison de flotter le **dit** (`flotte`),
    et c'est ce drapeau qui permet de juger les autres. Sans lui, « aucun décor
    sur l'eau » serait une phrase qu'on répète en espérant."""
    r = banc("""function (L, o) {
        const flottants = Object.keys(L.DECORS).filter(function (k) { return L.DECORS[k].flotte; });
        return { flottants: flottants, parasolSolide: !!L.DECORS.parasol.solide,
                 belvedereArrete: L.DECORS.belvedere.arrete || 0,
                 chateauPv: L.DECORS.chateau_sable.pv };
    }""")
    # ⚠️ **Une seule vérité, vérifiée des deux côtés** : la liste vit en Python
    # (`carte.FLOTTANTS`), le paquet la porte, et les fiches de dessin doivent
    # dire exactement la même chose. Deux listes, c'est deux vérités le jour où
    # l'une bouge.
    assert r["flottants"] == paquet["carte"]["flottants"], (
        "le dessin et la fiche ne s'entendent pas : %s contre %s"
        % (r["flottants"], paquet["carte"]["flottants"]))
    assert r["flottants"] == ["bouee"], "un autre décor s'est mis à nager : %s" % r["flottants"]
    # ⚠️ Le parasol est la seule chose du lot qu'on ne heurte pas : on passe dessous.
    assert r["parasolSolide"] is False, "on se cogne dans un parasol"
    # Le belvédère ARRÊTE au lieu de bloquer, comme les kiosques : on y monte.
    assert r["belvedereArrete"] > 0, "le belvédère ne retient personne"
    # Le décor le plus fragile de la table : un char qui roule sur la grève le rase.
    assert r["chateauPv"] <= 10, "un château de sable qui encaisse"


def test_un_chateau_de_sable_se_rase_et_revient_au_matin(banc, paquet):
    """⚠️ **Le seul du lot qui ait une règle**, et c'est ce qui en fait autre
    chose qu'un ornement. Un enfant qui recommence son château tous les jours,
    c'est une blague que la ville raconte sans qu'on l'écrive."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const chateau = L.B.entites.find(function (e) { return e.decor === 'chateau_sable'; });
        if (!chateau) return { trouve: false };
        const avant = !!chateau.brise;
        L.Entites.briser(chateau);
        const casse = !!chateau.brise;
        L.Entites.reparerLeDecor();
        return { trouve: true, avant: avant, casse: casse, apres: !!chateau.brise };
    }""")
    assert r["trouve"], "aucun château de sable n'est né avec la ville"
    assert r["avant"] is False, "un château déjà cassé au lever du jour"
    assert r["casse"] is True, "le château a encaissé"
    assert r["apres"] is False, "le château n'est pas revenu au matin"


def test_un_parasol_varie_d_une_tuile_a_l_autre_sans_tirer_un_de(banc, paquet):
    """⚠️ Le décor est cuit **une fois par type** : sans variante, tous les
    parasols de la ville sont du même rouge. Le crochet existait pour les
    `DECALS` (`d.v`) ; c'est la première fiche de décor à en avoir besoin.

    ⚠️ Et la variante se tire à l'**empreinte de la tuile**, jamais au dé du
    jeu — un décor qui consomme `B.rng()` décale tout ce qui suit, et cette
    leçon-là a déjà fait tomber quatre juges sans rapport."""
    r = banc("""function (L, o) {
        const vrai = L.B.rng;
        let des = 0;
        L.B.rng = function () { des++; return vrai(); };
        L.Jeu.commencer();
        const desApres = des;
        L.B.rng = vrai;
        const parasols = L.B.entites.filter(function (e) { return e.decor === 'parasol'; });
        const vues = {};
        for (const p of parasols) vues[p.v] = (vues[p.v] || 0) + 1;
        // Deux fois la même ville : la même tuile doit rendre la même variante.
        const repere = parasols.map(function (p) { return [p.x, p.y, p.v]; });
        L.Jeu.commencer();
        const encore = L.B.entites.filter(function (e) { return e.decor === 'parasol'; })
                        .map(function (p) { return [p.x, p.y, p.v]; });
        return { n: parasols.length, variantes: Object.keys(vues).length,
                 stable: JSON.stringify(repere) === JSON.stringify(encore),
                 max: L.DECORS.parasol.variantes, des: desApres };
    }""")
    assert r["n"] > 4, "trop peu de parasols pour juger (%s)" % r["n"]
    assert r["variantes"] > 1, "tous les parasols de la ville ont la même couleur"
    assert r["variantes"] <= r["max"], "une variante hors de la fiche"
    assert r["stable"], "la même tuile ne rend pas la même couleur deux fois"


def test_le_semis_de_la_greve_tient_a_l_ecran(banc, paquet):
    """Le juge qui relie les deux moitiés : ce que Python sème doit être ce que
    le navigateur dessine — et rien de ce qui est semé ne doit se retrouver sur
    l'eau, sauf ce qui déclare flotter."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const sur = { eau: [], sansDessin: [] };
        for (const d of L.Monde.carte.def.decor) {
          const fiche = L.DECORS[d.type];
          if (!fiche) { sur.sansDessin.push(d.type); continue; }
          const glyphe = L.Monde.glyphe(d.x, d.y);
          if (glyphe === '~' && !fiche.flotte) sur.eau.push(d.type + '@' + d.x + ',' + d.y);
        }
        return sur;
    }""")
    assert r["sansDessin"] == [], "des décors semés sans dessin : %s" % set(r["sansDessin"])
    assert r["eau"] == [], "des décors flottent sans le déclarer : %s" % r["eau"][:5]
