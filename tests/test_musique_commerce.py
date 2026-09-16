"""La musique des commerces — demande de Martin (16 sept. 2026).

« Nouvelle musique pour quand on entre dans les commerces, des chansons
différentes, contextuelles. »

⚠️ **C'est le LIEU qui choisit, pas le hasard** : entrer chez l'armurier et
entrer dans une boutique de linge ne se ressemblent pas. Une seule musique
« d'intérieur » aurait été un rideau tiré sur seize pièces différentes.
"""

from app import audio, carte, musique


def test_chaque_morceau_de_commerce_existe_et_est_instrumental():
    """Une toune chantée par-dessus une conversation de comptoir, on n'entend
    ni l'une ni l'autre — la règle des radios vaut ici."""
    slugs = {m["slug"] for m in musique.exporter()}
    for lieu, morceau in musique.MUSIQUES_DE_COMMERCE.items():
        assert morceau in slugs, f"{lieu} renvoie à « {morceau} », qui n'existe pas"
    fiches = {m["slug"]: m for m in audio.MUSIQUES}
    for style in musique.COMMERCES:
        fiche = fiches.get(style["slug"])
        assert fiche, f"{style['slug']} n'a pas d'invite de génération"
        assert "no vocals" in fiche["prompt"] or "instrumental" in fiche["prompt"], style["slug"]
        # ⚠️ Sous la voix du marchand : une musique de commerce qu'on remarque
        # est une musique de commerce ratée.
        assert 0 < style["volume"] <= 0.4, f"{style['slug']} joue trop fort"


def test_le_navigateur_recoit_la_carte_des_lieux():
    """⚠️ « Une fiche que le navigateur ne lisait pas » — le dépôt a payé ce
    défaut huit fois. La carte vit en Python ; si le paquet ne la porte pas,
    elle n'existe que pour nous."""
    e = audio.exporter()
    assert e["musiques_de_commerce"] == musique.MUSIQUES_DE_COMMERCE
    declares = {m["slug"] for m in e["musiques"]}
    for morceau in set(musique.MUSIQUES_DE_COMMERCE.values()):
        assert morceau in declares, morceau


def test_chaque_lieu_de_la_carte_existe_vraiment():
    """Une entrée qui nomme une pièce inexistante est une toune que personne
    n'entendra jamais — et rien ne le dirait."""
    ville = carte.exporter()
    lieux = set(ville["interieurs"]) if isinstance(ville["interieurs"], dict) else set()
    for lieu in musique.MUSIQUES_DE_COMMERCE:
        assert lieu in lieux, f"« {lieu} » n'est pas une pièce de la ville"


def test_ce_qui_n_est_pas_un_commerce_reste_silencieux():
    """⚠️ Le silence dit ce qu'aucune toune ne dirait : le poste de police,
    l'hôpital, la planque et la chambre d'hôtel ne sont pas des commerces. On
    n'y met pas de musique d'ambiance, et c'est un choix, pas un oubli."""
    for lieu in ("poste", "hopital", "planque", "hotel_chambre"):
        assert lieu not in musique.MUSIQUES_DE_COMMERCE, (
            f"« {lieu} » a reçu une musique de commerce")


def test_deux_commerces_voisins_ne_sonnent_pas_pareil():
    """Le point de la demande : des chansons **différentes**. Quatre morceaux
    pour neuf pièces, mais jamais le même dans deux familles qui se suivent."""
    par_morceau = {}
    for lieu, morceau in musique.MUSIQUES_DE_COMMERCE.items():
        par_morceau.setdefault(morceau, []).append(lieu)
    assert len(par_morceau) >= 4, "tous les commerces jouent la même chose"
    # ⚠️ Et chacun a sa couleur : ni la même tonique, ni le même tempo.
    toniques = {s["tonique"] for s in musique.COMMERCES}
    bpms = {s["bpm"] for s in musique.COMMERCES}
    assert len(toniques) == len(musique.COMMERCES), "deux commerces dans le même ton"
    assert len(bpms) == len(musique.COMMERCES), "deux commerces au même tempo"


def test_le_bouton_radio_ne_tombe_jamais_sur_une_toune_de_boutique(banc, paquet):
    """⚠️ Le bouton RADIO d'un char parcourt les **stations**. Tomber sur la
    musique d'ambiance d'une boutique de linge en roulant serait un défaut
    qu'on mettrait des mois à comprendre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const stations = L.Son.Radio.stations().map(function (s) { return s.slug; });
        return { stations: stations,
                 carte: Object.keys(L.B.defs.audio.musiques_de_commerce).length };
    }""")
    assert r["carte"] > 0, "le navigateur ne reçoit pas la carte des commerces"
    for morceau in set(musique.MUSIQUES_DE_COMMERCE.values()):
        assert morceau not in r["stations"], f"{morceau} est dans le bouton RADIO"


def test_en_entrant_dans_un_commerce_sa_toune_joue(banc, paquet):
    """Le geste lui-même. ⚠️ Elle démarre **au noir**, avec la porte : la rue se
    tait, et ce qu'on entend en ouvrant les yeux est déjà celle d'ici."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const carte = L.B.defs.audio.musiques_de_commerce;
        const portes = L.Monde.carte.portes.filter(function (p) {
          const lieu = L.Monde.porteA(p.x, p.y);
          return lieu && lieu.lieu && carte[lieu.lieu];
        });
        if (!portes.length) return { porte: false };
        const p = portes[0];
        const lieu = L.Monde.porteA(p.x, p.y).lieu;
        const avant = L.Son.Mus.courante;
        const ok = o.entrer(p);
        const dedans = L.Son.Mus.courante;
        o.sortir();
        return { porte: true, ok: ok, lieu: lieu, attendu: carte[lieu],
                 avant: avant, dedans: dedans, apres: L.Son.Mus.courante };
    }""")
    assert r["porte"], "aucune porte de commerce sur la carte"
    assert r["ok"], "on n'est pas entré"
    assert r["dedans"] == r["attendu"], (
        "dans %s on entend « %s » au lieu de « %s »" % (r["lieu"], r["dedans"], r["attendu"]))
    assert r["dedans"] != r["avant"], "la musique de la rue a suivi à l'intérieur"
    assert r["apres"] != r["attendu"], "la toune du commerce joue encore dehors"
