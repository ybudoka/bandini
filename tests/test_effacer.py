"""M11, deuxieme vague — effacer une page du casier.

⚠️ **Deux comptoirs qui n'ont de sens que l'un contre l'autre.** Un seul aurait
ete un bouton « annuler la partie » ; deux, c'est un choix, et c'est le choix
qui est le jeu. L'avocat est la CERTITUDE (une page, tout de suite, cher, une
fois par jour) ; le comptoir du fond de La Shop est LE PARI (moins cher a
sortir de sa poche, paye d'avance, des nouvelles le lendemain seulement, et
parfois une page DE PLUS).

Les juges d'ici tiennent les trois bornes sans lesquelles M11 s'effondre :
l'espérance du pari reste sous la certitude a prix egal, effacer coute toujours
plus cher que porter, et aucun des deux ne vide un casier plein d'un coup.
"""

import pytest

from app import economie


def test_le_pari_ne_bat_jamais_la_certitude_a_prix_egal():
    """⚠️ LE JUGE QUI TIENT TOUT LE RESTE. Si le comptoir du fond effacait plus
    de pages par dollar que l'avocat, l'avocat ne servirait plus a rien et le
    choix disparaitrait — il ne resterait qu'un comptoir moins cher, et M11
    serait un bouton.

    On compare ce qu'une page coute EN MOYENNE de chaque cote, dossier vierge
    et dossier epais : la borne doit tenir aux deux bouts, sinon elle ne tient
    qu'au debut de la partie."""
    esperance = economie.esperance_hacker()
    assert esperance > 0, "le comptoir du fond n'efface rien en moyenne : personne n'irait"
    avocat_pages = economie.EFFACER["avocat"]["pages"]
    for casier in (0, 5, economie.CASIER_MAX):
        par_page_sur = economie.prix_effacer("avocat", casier) / avocat_pages
        par_page_pari = economie.prix_effacer("hacker", casier) / esperance
        assert par_page_pari > par_page_sur, (
            f"casier {casier} : le pari efface a {par_page_pari:.0f} $ la page et la "
            f"certitude a {par_page_sur:.0f} $ — l'avocat ne sert plus a rien"
        )


def test_effacer_coute_toujours_plus_cher_que_porter():
    """⚠️ Sinon le casier ne veut plus rien dire, et tout M11 avec lui. Une page
    de dossier coute au plus `AMENDE_BASE[5 etoiles] * AMENDE_PAR_CASIER` a
    l'arrestation ; la faire disparaitre doit couter davantage, au comptoir le
    MOINS cher des deux et au dossier le plus mince."""
    ce_que_la_page_coute = max(economie.AMENDE_BASE) * economie.AMENDE_PAR_CASIER
    assert ce_que_la_page_coute > 0
    moins_cher = min(economie.prix_effacer(quoi, 0) for quoi in economie.EFFACER)
    assert moins_cher > ce_que_la_page_coute, (
        f"effacer coute {moins_cher} $ et porter coute {ce_que_la_page_coute} $ : "
        "on nettoierait son dossier par economie"
    )


def test_le_prix_monte_avec_l_epaisseur_du_dossier():
    """Vingt pages ne se nettoient pas au tarif de deux — c'est la meme regle
    que l'amende, et c'est elle qui fait qu'un gros casier PESE."""
    for quoi in economie.EFFACER:
        mince = economie.prix_effacer(quoi, 0)
        epais = economie.prix_effacer(quoi, economie.CASIER_MAX)
        assert epais > mince * 2, f"{quoi} : {mince} $ a vide, {epais} $ a plein"


def test_le_tirage_du_pari_est_un_vrai_tirage():
    """⚠️ Les chances font UN, il y a de quoi perdre et de quoi gagner, et
    personne ne vide un casier plein d'une visite. Une table dont la somme
    derive ne tire plus rien : le dernier cas rafle tout ce qui manque."""
    tirage = economie.EFFACER["hacker"]["tirage"]
    assert abs(sum(chance for _, chance in tirage) - 1.0) < 1e-9, tirage
    assert all(chance > 0 for _, chance in tirage), "un cas qui n'arrive jamais n'est pas un cas"
    gains = [pages for pages, _ in tirage]
    assert min(gains) < 0, "on ne risque rien : ce n'est pas un pari, c'est un rabais"
    assert max(gains) > economie.EFFACER["avocat"]["pages"], (
        "le pari ne paie jamais mieux que la certitude : personne ne le prendrait"
    )
    assert max(gains) < economie.CASIER_MAX, (
        "une seule visite vide un casier plein — le dossier ne veut plus rien dire"
    )


def test_le_pari_fait_attendre_et_la_certitude_se_repose():
    """Le delai et le repos ne sont pas de la decoration : ce sont eux qui
    empechent d'acheter vingt pages d'affilee sans bouger de sa chaise."""
    assert economie.EFFACER["hacker"]["delai_jours"] >= 1, "on saurait tout de suite : plus de pari"
    assert economie.EFFACER["avocat"]["par_jour"] == 1, "il travaillerait en boucle"


@pytest.mark.parametrize("quoi", sorted(economie.EFFACER))
def test_la_fiche_descend_au_navigateur(quoi):
    """⚠️ Le defaut qui revient : une fiche que le navigateur ne lisait pas. Le
    menu indexe `prix_effacer[quoi][casier]` — s'il manque une case, le comptoir
    demande `undefined` dollars et encaisse zero."""
    paquet = economie.exporter()
    assert quoi in paquet["effacer"], quoi
    table = paquet["prix_effacer"][quoi]
    assert len(table) == economie.CASIER_MAX + 1, f"{quoi} : {len(table)} cases"
    assert table == [economie.prix_effacer(quoi, c) for c in range(economie.CASIER_MAX + 1)]


def test_le_lieu_neuf_du_pari_est_bien_a_la_shop():
    """⚠️ C'est le TRAJET qui fait le risque : La Shop tombe a 0,15 la nuit, et
    y aller quand il travaille, c'est y aller seul. Un comptoir de plus au bar
    n'aurait rien coute a personne — ce juge tient la decision de geographie."""
    from app import carte
    shop = next(d for d in carte.DISTRICTS if d["slug"] == "shop")
    assert any("E" in rangee for rangee in shop["plan"]), (
        "le comptoir du fond a demenage hors de La Shop : le trajet ne coute plus rien"
    )
    portes = [p for p in carte.exporter()["portes"] if p.get("lieu") == "electronique"]
    assert len(portes) == 1, f"{len(portes)} portes pour Electronique Turcotte"


def test_l_avocat_tient_la_table_du_fond_du_brouillard():
    """Aucun lieu neuf pour lui : la table des personnages le place au Brouillard
    depuis le debut, et un avocat qui tient salon au fond d'une taverne est plus
    juste qu'une etude a lui. ⚠️ Mais il ne doit pas voler la porte ni le
    comptoir de Josee — `test_interieurs` le verifie deja, celui-ci verifie
    qu'il est bien LA."""
    from app import carte
    bar = carte.INTERIEURS["bar"]
    types = [p["type"] for p in bar["points"]]
    assert "avocat" in types, types
    assert "contact" in types, "Josee a disparu du bar"


def test_me_desjardins_est_assis_la_ou_l_on_vise():
    """⚠️ Retour de Martin : « je ne vois pas d'image de l'avocat dans le bar ».
    Le jeu promettait un avocat (« PARLER A L'AVOCAT ») et montrait une table
    vide : le point etait un comptoir invisible. Il est maintenant ASSIS, et
    trois choses doivent tenir ensemble, sinon le defaut revient par un autre
    bout :

    - il est sur une CHAISE, a cote d'une TABLE — un avocat qui tient salon ;
    - son point est SA tuile : on vise l'homme qu'on voit (sur la table, le pas
      d'a cote de lui etait a deux tuiles, hors de `RAYON_POINT`) ;
    - il a un CORPS A LUI : un complet fonce sur le corps commun est une Cravate."""
    from app import carte, pietons
    bar = carte.INTERIEURS["bar"]
    sol = bar["sol"]
    avocats = [g for g in bar["gens"] if g["qui"] == "avocat"]
    assert len(avocats) == 1, bar["gens"]
    x, y = avocats[0]["x"], avocats[0]["y"]
    assert sol[y][x] == "h", f"il n'est pas sur une chaise : « {sol[y][x]} »"
    voisins = [sol[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    assert "a" in voisins, "il est assis loin de toute table"
    point = next(p for p in bar["points"] if p["type"] == "avocat")
    assert (point["x"], point["y"]) == (x, y), "son point n'est pas la ou on le voit"
    fiche = pietons.par_slug("avocat")
    assert fiche and fiche["sprite"] == "avocat", "il porte le corps commun : c'est une Cravate"
    assert fiche["frequence"] == 0.0, "l'avocat nait au hasard dans la rue"


# --- Les deux comptoirs, en jeu --------------------------------------------

#: Entre par la porte qui mene au comptoir demande et s'y plante. ⚠️ On rouvre
#: le menu par `menuDuPoint` a chaque fois plutot que de rejouer `utiliserPoint`
#: : le joueur ne bouge pas, et c'est bien la MEME visite qu'on rejoue.
ALLER = """
    const allerAu = function (type) {
        const c = L.Monde.carte, j = L.B.joueur;
        const porte = c.portes.find(function (p) {
            return (c.def.interieurs[p.interieur].points || []).some(function (q) {
                return q.type === type;
            });
        });
        if (!porte) return null;
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const point = L.B.interieur.points.find(function (p) { return p.type === type; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8;
        return function () { return L.Missions.menuDuPoint(point); };
    };
    const item = function (menu, mot) {
        return menu.items.find(function (i) { return i.libelle.indexOf(mot) >= 0; });
    };
"""


def test_l_avocat_efface_une_page_et_ferme_boutique_pour_la_journee(banc):
    """⚠️ La certitude : une page, tout de suite, contre de l'argent — et plus
    rien avant demain. Sans le repos, on achetait vingt pages d'affilee sans se
    lever de sa chaise, et le casier n'etait plus qu'un compte a payer."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const p = L.B.partie, menu = allerAu('avocat');
        p.casier = 4; p.argent = 50000; p.jour = 3;
        const prix = L.B.defs.economie.prix_effacer.avocat[4];
        const avant = item(menu(), 'EFFACER');
        const actif = avant.actif;
        avant.faire();
        const apres = { casier: p.casier, argent: p.argent };
        // Le meme jour : il a fini sa journee.
        const meme = item(menu(), 'EFFACER');
        // Demain : il retravaille.
        p.jour = 4;
        const demain = item(menu(), 'EFFACER');
        return { actif: actif, prix: prix, casier: apres.casier, paye: 50000 - apres.argent,
                 memeJour: meme.actif, detailMemeJour: meme.detail, demain: demain.actif };
    }""" % ALLER)
    assert r["actif"] is True, "le comptoir est ferme alors qu'on a le dossier et l'argent : %s" % r
    assert r["casier"] == 3, "il n'a pas efface une page : %s" % r
    assert r["paye"] == r["prix"], "il ne prend pas le prix de la fiche : %s" % r
    assert r["memeJour"] is False, "il travaille deux fois le meme jour : %s" % r
    assert r["demain"] is True, "il ne rouvre jamais : %s" % r


def test_l_avocat_ne_rend_jamais_un_casier_negatif(banc):
    """Un dossier blanc n'a rien a effacer, et le comptoir le DIT — il ne prend
    pas l'argent pour rien."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const p = L.B.partie, menu = allerAu('avocat');
        p.casier = 0; p.argent = 50000; p.jour = 3;
        const vide = item(menu(), 'EFFACER');
        // Et une seule page : on descend a zero, pas en dessous.
        p.casier = 1;
        item(menu(), 'EFFACER').faire();
        return { actifAVide: vide.actif, detail: vide.detail, casier: p.casier, argent: p.argent };
    }""" % ALLER)
    assert r["actifAVide"] is False, "il efface une page d'un dossier blanc : %s" % r
    assert r["detail"] == "RIEN À EFFACER"
    assert r["casier"] == 0, "casier negatif : %s" % r


def test_on_voit_l_avocat_assis_et_on_lui_parle_du_pas_d_a_cote(banc):
    """Dans le jeu, pas seulement dans le plan : on pousse la porte du Brouillard
    et Me Desjardins est la, dans SON corps (la cravate rouge), assis, et il y
    reste. ⚠️ Et chaque pas libre autour de lui — a sa droite, devant lui — ouvre
    son menu : c'est la qu'un joueur qui le VOIT va se planter pour lui parler."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        allerAu('avocat');
        const j = L.B.joueur, point = L.B.interieur.points.find(function (p) { return p.type === 'avocat'; });
        const eux = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.arch === 'avocat'; });
        if (eux.length !== 1) return { combien: eux.length };
        const e = eux[0], avant = [e.x, e.y];
        // On se tasse avant de laisser tourner : `allerAu` nous a pose sur sa chaise.
        j.x = 6 * L.TT + 8; j.y = 6 * L.TT + 8;
        L.Entites.indexer();
        o.frame(300);
        // Les pas autour de LUI, pas autour du point : c'est lui qu'on voit.
        const ex = Math.floor(e.x / L.TT), ey = Math.floor(e.y / L.TT), pas = {};
        [[1, 0], [0, 1], [-1, 1], [1, 1]].forEach(function (d) {
            const tx = ex + d[0], ty = ey + d[1];
            if (!L.Monde.marchablePieton(tx, ty) || L.Monde.estMeuble(tx, ty)) return;
            j.x = tx * L.TT + 8; j.y = ty * L.TT + 8;
            // ⚠️ On le regarde : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
            L.Entites.regarder(j, e.x - j.x, e.y - j.y);
            L.B.menu = null;
            L.Missions.majInvite(j);
            const invite = L.B.invite;
            L.Missions.utiliserPoint(j);
            pas[tx + ',' + ty] = { invite: invite, titre: L.B.menu ? L.B.menu.titre : null };
        });
        L.B.menu = null;
        const def = L.SPRITES[e.sprite];
        return { combien: 1, sprite: e.sprite, pose: L.Entites.imageDe(e).pose, etat: e.etat,
                 tuile: [ex, ey], point: [point.x, point.y],
                 cravate: !!(def.pal.t && def.poses.assis_bas[0].join('').indexOf('t') >= 0),
                 bouge: Math.hypot(e.x - avant[0], e.y - avant[1]), pas: pas };
    }""" % ALLER)
    assert r["combien"] == 1, f"{r['combien']} avocat(s) au Brouillard : la table est vide"
    assert r["sprite"] == "avocat" and r["cravate"], f"il n'a pas son corps a lui : {r}"
    assert r["pose"] == "assis_bas" and r["etat"] == "fige", f"il n'est pas assis : {r}"
    assert r["bouge"] < 1, f"trois cents images plus tard, il s'est leve : {r}"
    assert len(r["pas"]) >= 3, f"on ne peut pas l'approcher : {r['pas']}"
    for tuile, vu in r["pas"].items():
        assert vu["invite"] == "PARLER À L’AVOCAT", f"a {tuile}, le HUD promet {vu['invite']!r}"
        assert vu["titre"] == "ME DESJARDINS", f"a {tuile}, ACTION n'ouvre pas son menu : {vu}"


def test_le_comptoir_du_fond_se_paie_d_avance_et_repond_le_lendemain(banc):
    """⚠️ TOUT LE PARI TIENT DANS CES DEUX LIGNES : l'argent part aujourd'hui,
    la nouvelle arrive demain. Sans le delai, ce serait un avocat moins cher ;
    avec, c'est un trajet de plus, une nuit a La Shop, et de quoi se refaire un
    casier entre-temps."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const p = L.B.partie, menu = allerAu('hacker');
        p.casier = 6; p.argent = 50000; p.jour = 2;
        const prix = L.B.defs.economie.prix_effacer.hacker[6];
        item(menu(), 'ENTRER DANS LE FICHIER').faire();
        const paye = 50000 - p.argent, casierLeJourMeme = p.casier;
        // Le meme jour : rien a prendre.
        const m1 = menu();
        const attend = item(m1, 'IL Y TRAVAILLE');
        const rienAPrendre = !item(m1, 'PRENDRE LES NOUVELLES');
        // Le lendemain : la nouvelle est la.
        p.jour = 3;
        const m2 = menu();
        const nouvelles = item(m2, 'PRENDRE LES NOUVELLES');
        nouvelles.faire();
        // Et la commande est consommee : on ne la reprend pas deux fois.
        const encore = !!item(menu(), 'PRENDRE LES NOUVELLES');
        return { prix: prix, paye: paye, casierLeJourMeme: casierLeJourMeme,
                 attend: !!attend, rienAPrendre: rienAPrendre, encore: encore,
                 commande: p.nettoyage.commande };
    }""" % ALLER)
    assert r["paye"] == r["prix"], "il ne prend pas le prix de la fiche : %s" % r
    assert r["casierLeJourMeme"] == 6, "il a efface le jour meme : ce n'est plus un delai (%s)" % r
    assert r["attend"] is True and r["rienAPrendre"] is True, "on peut encaisser tout de suite : %s" % r
    assert r["encore"] is False, "on prend les nouvelles deux fois : %s" % r
    assert r["commande"] is None, "la commande reste ouverte apres coup : %s" % r


def test_le_tirage_du_comptoir_du_fond_suit_la_table_du_serveur(banc):
    """⚠️ Le defaut qui revient : une fiche que le navigateur ne lisait pas. On
    joue le comptoir quatre cents fois et on compte ce qui sort — si le tirage
    etait code en dur dans le JS, la table pourrait changer sans que rien ne
    bouge en jeu.

    On mesure aussi qu'AUCUNE visite ne vide un casier plein, et qu'un casier
    ne devient jamais negatif du mauvais cote du tirage."""
    tirage = economie.EFFACER["hacker"]["tirage"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(5);
        %s
        const p = L.B.partie, menu = allerAu('hacker');
        const compte = {}; let pire = 0, plusHaut = 0;
        p.argent = 99999999; p.jour = 1;
        for (let n = 0; n < 400; n++) {
            p.casier = 10; p.argent = 99999999;
            item(menu(), 'ENTRER DANS LE FICHIER').faire();
            p.jour += 1;
            item(menu(), 'PRENDRE LES NOUVELLES').faire();
            const d = 10 - p.casier;                 // pages effacees, negatif = page de plus
            compte[d] = (compte[d] || 0) + 1;
            if (p.casier < pire) pire = p.casier;
            plusHaut = Math.max(plusHaut, d);
        }
        return { compte: compte, tours: 400, pire: pire, plusHaut: plusHaut,
                 max: L.B.defs.economie.casier_max };
    }""" % ALLER)
    assert r["pire"] >= 0, "un casier negatif est sorti du tirage : %s" % r
    assert r["plusHaut"] < r["max"], "une seule visite peut vider un casier plein : %s" % r
    for pages, chance in tirage:
        vu = r["compte"].get(str(pages), 0) / r["tours"]
        assert abs(vu - chance) < 0.08, (
            f"{pages} page(s) sort {vu:.0%} du temps, la fiche dit {chance:.0%} — "
            f"le navigateur ne lit pas la table ({r['compte']})"
        )


# --- L'autre moitie de l'avocat : sortir de prison ---------------------------


def test_la_provision_coute_plus_cher_qu_une_arrestation_ordinaire():
    """⚠️ Une assurance qui rapporte TOUJOURS n'est pas une assurance, c'est un
    salaire. La provision doit couter plus qu'une arrestation ordinaire (trois
    etoiles) a dossier egal : elle n'est payante que pour les grosses nuits,
    celles ou l'on sort a quatre ou cinq etoiles — et il faut avoir DECIDE, le
    matin, qu'on allait en faire une."""
    fortune = economie.FORTUNE_MAX
    for casier in range(0, economie.CASIER_MAX + 1, 5):
        provision = economie.prix_provision(casier)
        ordinaire = economie.amende(fortune, 3, casier)
        assert provision > ordinaire, (
            f"casier {casier} : la provision coute {provision} $ et l'amende ordinaire "
            f"{ordinaire} $ — on la prendrait tous les matins"
        )
    # ... et elle doit tout de même pouvoir payer : sans ça, personne ne la prend.
    assert economie.prix_provision(0) < economie.amende(fortune, 5, 0) * 2, (
        "même une nuit à cinq étoiles ne la rentabilise pas : c'est un article mort"
    )


def test_la_provision_efface_l_amende_et_rien_d_autre(banc):
    """⚠️ « Il te sort de prison sans amende » — SANS AMENDE, pas innocent. La
    page s'ajoute quand meme, les armes partent quand meme : sans ca, se faire
    arreter expres deviendrait un trajet gratuit vers le poste, et la police
    ne serait plus qu'un taxi."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const p = L.B.partie, menu = allerAu('avocat');
        p.casier = 3; p.argent = 50000; p.jour = 5;
        const prix = L.B.defs.economie.prix_provision[3];
        item(menu(), 'RETENIR').faire();
        const apresAchat = { argent: p.argent, retenu: p.nettoyage.provision };
        // ⚠️ Il a donne sa journee : on ne peut pas AUSSI lui faire effacer
        // une page aujourd'hui. C'est le choix, et c'est tout le comptoir.
        const effacerAussi = item(menu(), 'EFFACER').actif;
        o.sortir();
        p.argent = 9000; L.B.recherche.etoiles = 5;
        p.armes = { poings: { mun: null }, pistolet: { mun: 10 } };
        const casierAvant = p.casier;
        L.Missions.prison(null);
        o.fondu();
        return { prix: prix, paye: 50000 - apresAchat.argent, retenu: apresAchat.retenu,
                 effacerAussi: effacerAussi,
                 argentApres: p.argent, casierApres: p.casier, casierAvant: casierAvant,
                 armes: Object.keys(p.armes), provisionApres: p.nettoyage.provision };
    }""" % ALLER)
    assert r["paye"] == r["prix"], "il ne prend pas le prix de la fiche : %s" % r
    assert r["retenu"] is True
    assert r["effacerAussi"] is False, "il retient ET efface le même jour : %s" % r
    assert r["argentApres"] == 9000, "l'amende a été prélevée malgré la provision : %s" % r
    assert r["casierApres"] == r["casierAvant"] + 1, (
        "la page ne s'ajoute pas : l'arrestation devient gratuite (%s)" % r
    )
    assert r["armes"] == ["poings"], "les armes ne sont pas confisquées : %s" % r
    assert r["provisionApres"] is False, "la provision sert deux fois : %s" % r


def test_sans_provision_l_amende_tombe(banc):
    """Le temoin du juge d'a cote : sans provision, la meme arrestation coute.
    Sans cette mesure-la, « l'argent n'a pas bouge » ne prouverait rien."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        p.casier = 3; p.argent = 9000; p.nettoyage.provision = false;
        L.B.recherche.etoiles = 5;
        L.Missions.prison(null);
        o.fondu();
        return { argent: p.argent, attendu: L.B.defs.economie.amendes[4][3] };
    }""")
    assert r["argent"] < 9000, "une arrestation à cinq étoiles ne coûte rien : %s" % r
    assert r["argent"] == 9000 - min(9000, r["attendu"]), r
