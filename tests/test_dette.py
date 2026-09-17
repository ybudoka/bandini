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


def test_le_narrateur_du_matin_attend_la_fin_de_la_sonnerie(banc):
    """Retour de Martin (17 sept. 2026) : « il y a une sonnerie trop forte avant
    qu'il parle ». Le rappel de Sal et la manchette du Clairon partaient dans la
    MEME image : le combiné sonnait par-dessus les premiers mots du narrateur.

    ⚠️ Au banc, aucun mp3 n'est décodé : la sonnerie est celle de la synthèse
    (0,37 s, soit 22 images). C'est cet écart-là qu'on mesure."""
    r = banc("""function (L, o) {
        %s
        p.jour = f.rappel_jour; p.rappelJour = -1; p.dette = 15000;
        L.B.dialogue = null;
        L.Missions.nouveauJour();
        const sonne = { attend: !!L.B.manchette, images: L.B.manchette && L.B.manchette.t - L.B.t,
                        dialogue: L.B.dialogue && L.B.dialogue.qui, voix: L.Son.Voix.demandees.length,
                        msg: L.B.msg };
        let dit = -1;
        for (let i = 0; i < 120 && dit < 0; i++) { o.frame(1); if (!L.B.manchette) dit = i; }
        return { sonne: sonne, dit: dit, dialogue: L.B.dialogue && L.B.dialogue.qui,
                 voix: L.Son.Voix.demandees[L.Son.Voix.demandees.length - 1],
                 duree: L.Son.SFX.telephone() };
    }""" % DECOR)
    assert r["sonne"]["attend"] is True, "la manchette ne s'est pas mise en attente : %s" % r["sonne"]
    assert r["sonne"]["dialogue"] is None, "le Clairon parle par-dessus la sonnerie : %s" % r["sonne"]
    assert r["sonne"]["voix"] == 0, "la voix du narrateur est demandée pendant que ça sonne"
    assert "SAL" in (r["sonne"]["msg"] or ""), "le rappel de Sal ne s'affiche plus : %s" % r["sonne"]
    images = round(r["duree"] * 60)                      # 60 images font une seconde
    assert images <= r["dit"] + 1 <= images + 2, (
        "la manchette part %s images après la sonnerie, qui en dure %s" % (r["dit"] + 1, images))
    assert r["dialogue"] == "LE CLAIRON DE LA BAIE", "la manchette ne se dit jamais : %s" % r
    assert (r["voix"] or "").startswith("narrateur-journal-"), "le narrateur ne lit pas la manchette : %s" % r


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


def test_le_menu_des_hommes_se_joue_vraiment(banc):
    """⚠️ Retour de Martin, capture à l'appui : « il n'y a pas de sélection dans
    ce menu ». La collecte était le SEUL menu du jeu posé à la main
    (`B.menu = menuDette(...)`) au lieu de passer par `Hud.ouvrirMenu` — donc
    ouvert **sans curseur** : aucune ligne surlignée, HAUT et BAS le mettaient à
    `NaN`, ACTION ne choisissait rien et les boutons de l'écran tactile
    continuaient d'annoncer FRAPPE et ACTION au lieu de RETOUR et CHOISIR. On ne
    pouvait pas payer, au moment le plus tendu du jeu.

    ⚠️ Et il s'ouvre sur l'ACOMPTE, pas sur « LA DETTE » : la première ligne est
    un en-tête qui se lit et ne se choisit pas. Le juge va jusqu'au bout — il
    descend d'un cran, appuie, et regarde l'argent sortir de la poche."""
    r = banc("""function (L, o) {
        %s
        p.jour = f.collecte_jour; p.argent = 2575;
        for (let i = 0; i < 60; i++) { L.B.t += 30; L.Missions.majCollecteurs(); }
        const homme = L.Missions.collecteurs()[0];
        homme.x = j.x + 12; homme.y = j.y;
        L.Entites.indexer();
        L.Missions.interagir(j);
        const m = L.B.menu;
        const sous = m.items[m.curseur] || {};
        // ⚠️ `null` plutot que `undefined` : sans ca, un menu ouvert SANS curseur
        // (le defaut d'origine) disparait du JSON et le juge meurt d'une KeyError
        // au lieu de dire ce qu'il a vu.
        const ouverture = { titre: m.titre, curseur: typeof m.curseur === 'number' ? m.curseur : null,
                            libelle: sous.libelle,
                            montant: sous.montant || 0, choix: !!sous.faire,
                            etiquette: o.doc.querySelector('#boutons b[data-a="action"]').textContent };
        o.tape('KeyS', 2);                      // BAS : le curseur descend d'un cran
        const apresBas = L.B.menu ? L.B.menu.curseur : null;
        const detteAvant = p.dette, argentAvant = p.argent;
        o.tape('KeyE', 2);                      // ACTION : on donne ce qui est sous le pouce
        return { ouverture: ouverture, apresBas: apresBas, ferme: L.B.menu === null,
                 paye: argentAvant - p.argent, efface: detteAvant - p.dette,
                 restent: L.Missions.collecteurs().length, acompte: f.acompte_min };
    }""" % DECOR)
    o = r["ouverture"]
    assert o["titre"] == "LES HOMMES DE SAL"
    assert o["curseur"] == 1 and o["choix"] is True, (
        "le menu s'ouvre sur une ligne qu'on ne peut pas choisir : %s" % r
    )
    assert o["montant"] == r["acompte"], "il doit s'ouvrir sur l'acompte : %s" % r
    assert o["etiquette"] == "CHOISIR", (
        "les boutons de l'écran annoncent encore le jeu, pas le menu : %s" % r
    )
    assert r["apresBas"] == 2, "BAS ne descend pas le curseur : %s" % r
    assert r["paye"] == r["acompte"] * 4, "ACTION ne donne pas la ligne sous le pouce : %s" % r
    assert r["efface"] == r["paye"], "ce qu'on donne ne descend pas la dette : %s" % r
    assert r["restent"] == 0 and r["ferme"] is True, "l'acompte ne les renvoie pas : %s" % r


def test_les_hommes_de_sal_cognent_a_mains_nues_ou_au_poing_americain(banc):
    """⚠️ Demande de Martin : « les hommes de Sal sont à main nue ou poing
    américain (un peu plus fort) ». Ils naissent dans le corps d'un Cravate, et
    la fiche du Cravate porte un BÂTON : le recouvrement arrivait la batte à la
    main, et la laissait par terre quand on le couchait.

    Le juge ne s'arrête pas à `e.arme` : il laisse chacun frapper le joueur et
    compte ce que le coup enlève — c'est le coup qui dit ce qu'on a dans la
    main. Puis il les couche, et regarde ce qui tombe."""
    r = banc("""function (L, o) {
        %s
        p.jour = f.collecte_jour;
        for (let i = 0; i < 60; i++) { L.B.t += 30; L.Missions.majCollecteurs(); }
        const def = function (slug) {
            return L.B.defs.armes.find(function (a) { return a.slug === slug; }) || {};
        };
        const hommes = L.Missions.collecteurs();
        const coups = [];
        for (const homme of hommes) {
            // Les autres attendent loin : un seul coup à la fois sur le joueur.
            hommes.forEach(function (q) { q.x = j.x + 300; q.y = j.y; });
            homme.x = j.x - 12; homme.y = j.y;
            homme.angle = 0;
            j.vie = 100;
            L.Entites.indexer();
            L.Combat.frapper(homme, false);
            for (let i = 0; i < 30; i++) { L.Entites.indexer(); L.Combat.maj(); }
            coups.push(100 - j.vie);
        }
        const avant = L.B.entites.filter(function (e) { return e.type === 'ramassage'; }).length;
        hommes.forEach(function (q) { L.Entites.assommer(q); });
        const tombe = L.B.entites.filter(function (e) { return e.type === 'ramassage'; })
            .slice(avant).map(function (e) { return e.arme; });
        return { hommes: hommes.length, coups: coups, tombe: tombe,
                 poings: def('poings').degats, americain: def('poing_americain').degats,
                 batte: def('batte').degats };
    }""" % DECOR)
    assert r["hommes"] >= 2, "il faut deux hommes pour voir les deux mains : %s" % r
    assert r["poings"] < r["americain"] < r["batte"], "le poing américain n'est pas « un peu plus fort » : %s" % r
    assert r["batte"] not in r["coups"], "un homme de Sal cogne encore au bâton : %s" % r
    assert set(r["coups"]) == {r["poings"], r["americain"]}, (
        "ils doivent frapper à mains nues ET au poing américain, rien d'autre : %s" % r
    )
    assert r["tombe"] == ["poing_americain"] * r["coups"].count(r["americain"]), (
        "couchés, ils doivent laisser leur poing américain — et rien d'autre : %s" % r
    )


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


def test_la_dette_se_lit_dans_le_carnet(banc):
    """⚠️ Une pression qu'on subit sans jamais pouvoir la regarder n'est pas une
    pression, c'est une malchance — la même règle que le carnet du poste. Et
    elle **disparaît** de la page le jour où elle est réglée : une ligne à zéro
    serait une dette qu'on traîne pour rien."""
    r = banc("""function (L, o) {
        %s
        const lire = function () {
            const m = L.Hud.menuCarnet();
            const l = m.items.find(function (q) { return q.libelle === 'LA DETTE DE ROCCO'; });
            return l ? l.detail : null;
        };
        const due = lire();
        L.Missions.rembourser(999999, 'TOUT');
        return { due: due, reglee: lire(), dette: p.dette };
    }""" % DECOR)
    assert r["due"] == "%s $" % economie.DETTE["montant"], (
        "le carnet ne dit pas ce qu'on doit : %s" % r
    )
    assert r["dette"] == 0
    assert r["reglee"] is None, "la dette réglée traîne encore dans le carnet : %s" % r
