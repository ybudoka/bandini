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
    assert r["detail"] == "RIEN A EFFACER"
    assert r["casier"] == 0, "casier negatif : %s" % r


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
