"""M10, première vague — la dette de Rocco, celle qui donne une raison de se lever.

⚠️ **Elle ne se rembourse pas à un comptoir**, et ce n'est pas une économie de
géographie : un shylock n'attend pas derrière une caisse, il ENVOIE DU MONDE.
Les rappels arrivent au téléphone, puis les hommes de Sal te trouvent où que tu
sois — et c'est à eux qu'on paie. La collecte est une scène, pas un menu de plus
dans une pièce.
"""

from app import economie


def test_la_dette_ne_depasse_jamais_son_plafond():
    """⚠️ Une dette qui double pendant qu'on dort n'est plus une pression, c'est
    une partie perdue au réveil. On la fait monter cent nuits d'affilée et on
    regarde où elle s'arrête."""
    plafond = round(economie.DETTE["montant"] * economie.DETTE["plafond"])
    dette = economie.DETTE["montant"]
    for _ in range(100):
        dette = economie.dette_du_lendemain(dette)
        assert dette <= plafond, f"la dette a dépassé son plafond : {dette} > {plafond}"
    assert dette == plafond, "elle n'atteint jamais son plafond : l'intérêt ne mord pas"


def test_un_joueur_qui_ne_fait_rien_ne_devient_pas_insolvable_en_une_nuit():
    """⚠️ LE JUGE DE LA FICHE. L'intérêt d'une seule nuit, **au pire moment**
    (dette au plafond), doit rester sous ce qu'une journée rapporte honnêtement.
    Sinon le taxi ne sert plus à rien et il n'y a plus de décision, seulement une
    descente.

    ⚠️ L'étalon est `PROPRIETES` : c'est le seul revenu du jeu qui se compte en
    dollars PAR JOUR et qui ne dépend pas de l'habileté du joueur — donc le seul
    auquel on puisse comparer un intérêt quotidien sans inventer un chiffre."""
    plafond = round(economie.DETTE["montant"] * economie.DETTE["plafond"])
    pire_nuit = economie.dette_du_lendemain(plafond - 1) - (plafond - 1)
    interet_au_plafond = round(plafond * economie.DETTE["interet_par_jour"])
    honnete = economie.revenu_honnete_par_jour()
    assert honnete > 0
    assert interet_au_plafond < honnete, (
        f"la dette coûte {interet_au_plafond} $ par nuit et le travail honnête en "
        f"rapporte {honnete} $ : il n'y a plus de décision, seulement une descente"
    )
    assert pire_nuit >= 0


def test_la_dette_pese_sur_une_partie_entiere_pas_sur_une_nuit():
    """Elle doit être une raison de se lever le matin, pas un compte à rebours.
    ⚠️ Un jour de jeu fait huit minutes : vingt nuits, c'est près de trois heures
    de partie — l'échelle de « devenir le boss »."""
    jours = economie.jours_avant_le_plafond()
    assert jours >= 10, f"la dette plafonne en {jours} nuits : c'est un compte à rebours"
    assert jours <= 60, f"la dette met {jours} nuits à monter : personne ne la sentira"


def test_le_telephone_sonne_avant_que_les_hommes_ne_viennent():
    """⚠️ On a le temps de faire quelque chose, et c'est ce qui en fait une
    pression plutôt qu'une embuscade. Un recouvrement qui commence par des coups
    n'est pas une dette, c'est un accident."""
    f = economie.DETTE
    assert f["rappel_jour"] >= 1
    assert f["rappel_jour"] < f["collecte_jour"], (
        "les hommes arrivent avant le premier appel : on ne peut rien anticiper"
    )


def test_un_acompte_reste_atteignable():
    """Le plus petit versement doit se ramasser en une journée de travail, sinon
    la seule réponse à la dette est de fuir — et fuir n'est pas une décision."""
    assert 0 < economie.DETTE["acompte_min"] <= economie.revenu_honnete_par_jour()


def test_la_fiche_descend_au_navigateur():
    """⚠️ Le défaut qui revient : une fiche que le navigateur ne lisait pas. La
    table est calculée **ici**, borne comprise — le navigateur n'a qu'à indexer,
    et deux formules pour un seul nombre finissent toujours par diverger."""
    paquet = economie.exporter()
    assert paquet["dette"] == economie.DETTE
    table = paquet["dettes"]
    assert table[0] == economie.DETTE["montant"]
    assert table[-1] == round(economie.DETTE["montant"] * economie.DETTE["plafond"])
    assert table == sorted(table), "la table redescend : ce n'est plus un intérêt"


# --- La dette en jeu ---------------------------------------------------------

DECOR = """
    L.Jeu.commencer();
    L.graine(23);
    const p = L.B.partie, f = L.B.defs.economie.dette, j = L.B.joueur;
    const d = o.ligneDroite();
    j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
    const nuits = function (n) {
        for (let i = 0; i < n; i++) { p.jour += 1; L.Missions.nouveauJour(); }
    };
"""


def test_la_nuit_fait_monter_la_dette_et_le_plafond_la_retient(banc):
    """⚠️ Le navigateur INDEXE la table du serveur, il ne refait pas l'intérêt.
    Deux formules pour un seul nombre finissent toujours par diverger — et c'est
    la borne qu'on perdrait en premier."""
    r = banc("""function (L, o) {
        %s
        const depart = p.dette;
        nuits(1);
        const apresUne = p.dette;
        nuits(200);
        return { depart: depart, apresUne: apresUne, apresCent: p.dette,
                 plafond: L.B.defs.economie.dettes[L.B.defs.economie.dettes.length - 1] };
    }""" % DECOR)
    assert r["depart"] == economie.DETTE["montant"], "la partie ne commence pas endettée : %s" % r
    assert r["apresUne"] > r["depart"], "la nuit ne coûte rien : %s" % r
    assert r["apresUne"] == economie.dette_du_lendemain(r["depart"]), (
        "le navigateur refait l'intérêt au lieu de lire la table : %s" % r
    )
    assert r["apresCent"] == r["plafond"], "le plafond ne retient rien : %s" % r


def test_personne_ne_vient_avant_le_jour_dit_puis_ils_viennent(banc):
    """⚠️ Le téléphone d'abord, les hommes ensuite. Et **une seule visite par
    jour** : sans ça, la dette n'est plus une pression, c'est un harcèlement dont
    on ne peut rien faire."""
    r = banc("""function (L, o) {
        %s
        p.jour = f.collecte_jour - 1;
        for (let i = 0; i < 60; i++) { L.B.t += 30; L.Missions.majCollecteurs(); }
        const avant = L.Missions.collecteurs().length;
        p.jour = f.collecte_jour;
        for (let i = 0; i < 60; i++) { L.B.t += 30; L.Missions.majCollecteurs(); }
        const venus = L.Missions.collecteurs().length;
        // On les renvoie, et personne ne prend le relais le même jour.
        L.Missions.collecteurs().forEach(function (e) { L.Entites.retirer(e); });
        for (let i = 0; i < 60; i++) { L.B.t += 30; L.Missions.majCollecteurs(); }
        const memeJour = L.Missions.collecteurs().length;
        // Le lendemain, ils reviennent.
        p.jour += 1;
        for (let i = 0; i < 60; i++) { L.B.t += 30; L.Missions.majCollecteurs(); }
        return { avant: avant, venus: venus, memeJour: memeJour,
                 lendemain: L.Missions.collecteurs().length, hommes: f.hommes };
    }""" % DECOR)
    assert r["avant"] == 0, "ils viennent avant le jour dit : %s" % r
    assert r["venus"] == r["hommes"], "ils ne viennent pas, ou pas au bon nombre : %s" % r
    assert r["memeJour"] == 0, "ils se relaient dans la même journée : %s" % r
    assert r["lendemain"] == r["hommes"], "ils ne reviennent jamais : %s" % r


def test_on_les_paie_en_main_propre_et_la_dette_ne_passe_jamais_sous_zero(banc):
    """⚠️ C'est à EUX qu'on paie — la collecte est une scène, pas un menu dans
    une pièce. Et le jour où la dette tombe à zéro, ils rentrent chez eux : c'est
    la seule chose qui les fait partir pour de bon."""
    r = banc("""function (L, o) {
        %s
        p.jour = f.collecte_jour; p.argent = 100000;
        for (let i = 0; i < 60; i++) { L.B.t += 30; L.Missions.majCollecteurs(); }
        const homme = L.Missions.collecteurs()[0];
        homme.x = j.x + 12; homme.y = j.y;
        L.Entites.indexer();
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        const ouvert = L.Missions.interagir(j);
        const menu = L.B.menu;
        const titre = menu ? menu.titre : null;
        // Un acompte : ils s'en vont pour aujourd'hui, la dette baisse.
        const detteAvant = p.dette, argentAvant = p.argent;
        menu.items.find(function (q) { return q.montant === f.acompte_min; }).faire();
        const apresAcompte = { dette: p.dette, paye: argentAvant - p.argent,
                               restent: L.Missions.collecteurs().length };
        // Tout régler : la dette tombe à zéro, et pas en dessous.
        p.argent = 100000;
        L.Missions.rembourser(999999, 'TOUT');
        return { invite: invite, ouvert: ouvert, titre: titre,
                 detteAvant: detteAvant, apresAcompte: apresAcompte,
                 finale: p.dette, acompte: f.acompte_min };
    }""" % DECOR)
    assert r["ouvert"] is True and r["titre"] == "LES HOMMES DE SAL", (
        "ACTION n'ouvre pas la collecte : %s" % r
    )
    assert r["invite"] == "PAYER SAL — %s $" % r["detteAvant"], (
        "le HUD n'annonce pas ce qu'ACTION va faire : %s" % r
    )
    assert r["apresAcompte"]["paye"] == r["acompte"], "l'acompte ne coûte pas son prix : %s" % r
    assert r["apresAcompte"]["dette"] == r["detteAvant"] - r["acompte"], (
        "payer ne réduit pas la dette : c'est un impôt, pas un recouvrement (%s)" % r
    )
    assert r["apresAcompte"]["restent"] == 0, "l'acompte ne les renvoie pas : %s" % r
    assert r["finale"] == 0, "la dette passe sous zéro : %s" % r


def test_ce_qu_ils_prennent_de_force_compte_sur_la_dette(banc):
    """⚠️ Des hommes de main qui volent sans rien effacer seraient un impôt, pas
    un recouvrement — et le joueur n'aurait aucune raison de les laisser
    approcher plutôt que de fuir chaque fois. Ce qu'ils prennent doit compter."""
    r = banc("""function (L, o) {
        %s
        p.jour = f.collecte_jour; p.argent = 1000;
        for (let i = 0; i < 60; i++) { L.B.t += 30; L.Missions.majCollecteurs(); }
        const homme = L.Missions.collecteurs()[0];
        const detteAvant = p.dette, argentAvant = p.argent;
        homme.x = j.x + 10; homme.y = j.y;
        L.Entites.indexer();
        L.B.t += 30; L.Missions.majCollecteurs();
        return { detteAvant: detteAvant, dette: p.dette,
                 argentAvant: argentAvant, argent: p.argent, part: f.prend };
    }""" % DECOR)
    pris = r["argentAvant"] - r["argent"]
    assert pris > 0, "ils te frôlent sans rien prendre : %s" % r
    assert pris == round(r["argentAvant"] * r["part"]), (
        "ils ne prennent pas la part de la fiche : %s" % r
    )
    assert r["detteAvant"] - r["dette"] == pris, (
        "ce qu'ils prennent ne compte pas sur la dette : c'est un impôt (%s)" % r
    )
