"""M15, première vague — comment la rue parle, et quand elle se tait.

⚠️ Deux des trois morceaux sont des **correctifs**, et l'un d'eux réparait une
promesse écrite dans le code et jamais tenue : `audio.VOIX` disait « jamais deux
fois de suite le même » alors que le moteur tirait au hasard **sans aucune
mémoire**. Un tirage au hasard PEUT sortir deux fois le même — c'est même sa
définition.
"""

import pytest

from app import audio


def test_les_reglages_de_la_parole_tiennent_ensemble():
    """⚠️ Les trois nombres se décident ENSEMBLE, et c'est pour ça qu'ils sont
    dans une seule fiche.

    La mémoire doit rester **plus courte que la plus petite banque**, sinon la
    règle se retourne contre elle-même : on exclut tout, il ne reste rien à
    tirer, et plus personne ne parle."""
    p = audio.PAROLE
    assert p["temps_mort_images"] >= 240, "la rue parle plus souvent qu'avant, pas moins"
    assert 0 < p["chance"] < 1, "parler doit rester une chance, pas une certitude"
    # ⚠️ **UNE BANQUE, C'EST UN GENRE ET UN CONTEXTE** depuis la 2e vague, plus
    # seulement un genre : « quatre répliques d'homme » peut très bien vouloir dire
    # deux la nuit et deux le jour, et la mémoire s'y retournerait contre elle-même
    # sans que ce juge-ci ne voie rien. Un genre sans contexte (le crieur, la Brume)
    # est une banque à lui tout seul.
    #
    # ⚠️ Et on ne compte QUE les banques où l'on tire : ce qui passe sur les ondes se
    # dit à tour de rôle (`Ondes.aTourDeRole`), la mémoire ne le regarde pas.
    banques: dict[tuple[str, str], int] = {}
    for voix in audio.VOIX:
        if voix["genre"] in audio.GENRES_DES_ONDES:
            continue
        cle = (voix["genre"], voix.get("quand", audio.CONTEXTE_DE_DEPART))
        banques[cle] = banques.get(cle, 0) + 1
    plus_petite = min(banques.values())
    assert p["memoire"] < plus_petite, (
        f"la mémoire ({p['memoire']}) atteint la plus petite banque ({plus_petite}) : "
        f"il ne resterait rien à tirer — {banques}"
    )


def test_chaque_contexte_a_ses_repliques_dans_les_deux_genres():
    """⚠️ **LA VILLE SE MET À TE RECONNAÎTRE** (M15, 2e vague) : quatre banques au
    lieu d'une, et c'est la ville qui choisit — huit répliques disaient bonjour
    pendant qu'on saignait, une arme à la main, à trois heures du matin.

    ⚠️ **Un contexte sans banque est du code mort ; une banque sans contexte est
    huit clips qui ne sortiront jamais.** Le juge tient les deux listes ensemble :
    celle des règles (`PAROLE["contextes"]`, en Python, dans l'ordre) et celle des
    répliques (`quand`).

    ⚠️ Et chaque banque doit rester **plus grande que la mémoire, plus deux** : deux
    de plus pour que ce soit encore un tirage et pas une alternance."""
    p = audio.PAROLE
    contextes = [c["quand"] for c in p["contextes"]]
    assert contextes, "la ville n'a plus qu'un seul monde"
    assert len(contextes) == len(set(contextes)), f"deux règles pour le même contexte : {contextes}"
    attendus = set(contextes) | {audio.CONTEXTE_DE_DEPART}
    vus = {v["quand"] for v in audio.VOIX if v.get("quand")}
    assert vus == attendus, (
        f"les règles parlent de {sorted(attendus)} et les répliques de {sorted(vus)} : "
        "ce qui n'est que d'un côté ne se joue jamais"
    )
    for quand in sorted(attendus):
        for genre in ("homme", "femme"):
            banque = [v for v in audio.VOIX if v.get("quand") == quand and v["genre"] == genre]
            assert len(banque) >= p["memoire"] + 2, (
                f"la banque « {genre} / {quand} » n'a que {len(banque)} répliques : "
                f"on en écarte {p['memoire']}, il n'en reste pas de quoi tirer"
            )
            slugs = [v["slug"] for v in banque]
            assert len(slugs) == len(set(slugs)), f"{genre} / {quand} : deux fois le même slug"
            textes = [v["texte"] for v in banque]
            assert len(textes) == len(set(textes)), f"{genre} / {quand} : deux fois le même texte"
    # ⚠️ Et le `quand` VOYAGE : c'est le navigateur qui choisit la banque, à l'image.
    # Sans lui dans le paquet, les quatre banques n'en font qu'une, et tout le reste
    # marche — c'est le genre d'oubli qui ne se voit qu'à l'oreille.
    exporte = {v["slug"]: v for v in audio.exporter()["voix"]}
    for voix in audio.VOIX:
        assert exporte[voix["slug"]].get("quand") == voix.get("quand"), voix["slug"]


def test_le_seuil_de_la_celebrite_est_atteignable():
    """⚠️ Un contexte qu'on ne peut pas atteindre, ce sont huit clips morts : « on t'a
    vu dans le Clairon » à partir de plus de missions qu'il n'en existe ne se dirait
    jamais."""
    from app import missions
    regle = next(c for c in audio.PAROLE["contextes"] if c["quand"] == "celebre")
    assert 0 < regle["missions_min"] < len(missions.CATALOGUE), (
        f"{regle['missions_min']} missions pour être célèbre, et le jeu en a "
        f"{len(missions.CATALOGUE)}"
    )


def test_la_rumeur_tombe_puis_remonte_doucement():
    """⚠️ Elle TOMBE d'un coup et REMONTE doucement. C'est la chute qui se
    remarque, et c'est la remontée lente qui fait qu'on se sent surveillé encore
    un moment après avoir rangé l'arme."""
    r = audio.RUMEUR
    assert 0 < r["peur_part"] < 0.5, "une rue qui a peur doit vraiment se taire"
    assert r["cri_part"] > 1, "après un coup de feu, la foule crie — elle ne murmure pas"
    assert r["peur_images"] >= 120, "la peur passe trop vite pour se sentir"
    # La remontée met au moins deux secondes à retrouver le plein volume.
    assert r["retour_par_image"] * 120 <= 1.0, (
        "la rumeur revient d'un coup : une foule qui reprend son murmure à la seconde "
        "où l'arme rentre dans la poche n'a pas eu peur"
    )


def test_le_clairon_a_de_quoi_enseigner():
    """Le repli « rien à signaler » enseigne une chose par matin calme. ⚠️ Chaque
    leçon dit par quelle statistique on PROUVE qu'on sait déjà : sans elle, le
    jeu expliquerait le taxi à quelqu'un qui a fait trente courses."""
    from app import journal
    assert len(journal.LECONS) >= 4, "le journal a vite fini d'enseigner"
    slugs = [le["slug"] for le in journal.LECONS]
    assert len(slugs) == len(set(slugs)), "deux leçons portent le même slug"
    for lecon in journal.LECONS:
        for champ in ("slug", "cle", "titre", "texte", "lu"):
            assert lecon.get(champ), f"{lecon.get('slug')} : « {champ} » manque"
        assert lecon["titre"] == lecon["titre"].upper(), lecon["slug"]
        # ⚠️ `lu` est ce que le narrateur DIT : en casse naturelle, sinon le TTS
        # épelle les majuscules. Même règle que les manchettes.
        assert lecon["lu"] != lecon["lu"].upper(), (
            f"{lecon['slug']} : le narrateur va épeler les majuscules"
        )


@pytest.mark.parametrize("lecon", [le for le in __import__("app.journal", fromlist=["x"]).LECONS],
                         ids=lambda le: le["slug"])
def test_chaque_lecon_a_sa_voix_declaree(lecon):
    """⚠️ Le narrateur les lit comme une manchette. Tant que les mp3 n'existent
    pas, `exporter()` ne les déclare pas et l'encadré s'affiche sans voix —
    c'est la règle d'`audio.py`, et c'est elle qui permet d'écrire le texte
    avant de dépenser un crédit."""
    voix = {v["slug"] for v in audio.voix_journal()}
    assert f"narrateur-journal-{lecon['slug']}" in voix


def test_le_tirage_des_repliques_passe_par_le_hasard_du_jeu(banc):
    """⚠️ « Jamais deux fois de suite le même » était ÉCRIT dans `audio.VOIX` et
    FAUX dans le moteur : le tirage passait par `Math.random()`, sans mémoire.
    Sur quatre répliques par genre, une chance sur quatre de répéter la
    précédente — dans une rue passante, on entendait « Fait frette, hein? »
    trois fois en vingt secondes.

    ⚠️ Et le tirage passe maintenant par `B.rng()`. Tout le hasard du jeu y
    passe déjà : c'est ce qui rend le banc reproductible, donc juge. Cette
    ligne-là lui échappait — et c'était précisément celle qu'on voulait
    pouvoir tester."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ On juge `tirer`, pas `dire` : `dire` a besoin de tampons charges,
        // donc de fichiers mp3 — le banc n'en a aucun. La REGLE, elle, n'a
        // besoin de rien, et c'est elle qu'on veut tenir.
        const voix = L.B.defs.audio.voix.filter(function (v) { return v.genre === 'homme'; });
        const suite = function (graine) {
            L.graine(graine);
            L.Son.Voix.dernieres = [];
            const dits = [];
            for (let i = 0; i < 12; i++) {
                const v = L.Son.Voix.tirer(voix);
                dits.push(v ? v.slug : null);
            }
            return dits;
        };
        const a = suite(7), b = suite(7), c = suite(8);
        let deuxDeSuite = 0;
        for (let i = 1; i < a.length; i++) if (a[i] && a[i] === a[i - 1]) deuxDeSuite++;
        return { a: a, memeGraine: a.join() === b.join(), autreGraine: a.join() !== c.join(),
                 deuxDeSuite: deuxDeSuite, banque: voix.length,
                 memoire: L.B.defs.audio.parole.memoire };
    }""")
    assert all(r["a"]), "personne ne parle : le juge ne prouve rien"
    # ⚠️ REPRODUCTIBLE : même graine, même suite. C'est ça qui fait du banc un
    # juge, et c'est ce que `Math.random()` interdisait.
    assert r["memeGraine"] is True, "deux parties de même graine ne disent pas la même chose"
    assert r["autreGraine"] is True, "la graine ne change rien : ce n'est plus du hasard"
    # ⚠️ Et jamais deux fois de suite la même — la promesse enfin tenue.
    assert r["deuxDeSuite"] == 0, (
        "%s répétitions immédiates sur douze répliques : %s" % (r["deuxDeSuite"], r["a"])
    )


def test_la_rue_se_tait_devant_une_arme_et_crie_apres_un_coup_de_feu(banc):
    """⚠️ L'ajout le moins cher de toute la vague, et celui qui se sent le plus.
    Une rue qui se tait d'un coup dit « ils t'ont vu » mieux qu'une étoile de
    plus — et elle le dit **avant** que tu regardes le HUD."""
    r = banc("""function (L, o) {
        const R = function () { return L.Son.Rumeur; };
        // ⚠️ `L.Jeu.commencer()` D'ABORD : le joueur n'existe pas avant, et
        // `L.B.joueur` vaut null.
        L.Jeu.commencer();
        const j = L.B.joueur;
        // ⚠️ ON MESURE CONTRE LA FOULE DU MOMENT, jamais contre une lecture
        // d'il y a dix secondes : le volume voulu suit le nombre de gens
        // autour, et ce nombre bouge pendant qu'on marche. Comparer « revenue »
        // a un « calme » pris quatre cents images plus tot, c'est mesurer la
        // densite du quartier, pas la rumeur.
        const mesure = function () {
            const gens = L.Entites.pietonsAutour(j.x, j.y, 200)
              .filter(function (e) { return !e.metier; }).length;
            return { v: +R().volume.toFixed(3), voulu: +Math.min(1, gens / 10).toFixed(3) };
        };
        j.arme = 'poings';
        for (let i = 0; i < 300; i++) o.frame(1);
        const calme = mesure();
        // Une arme au poing : la rue tombe.
        j.arme = 'batte';
        for (let i = 0; i < 60; i++) o.frame(1);
        const peur = mesure();
        // On la range : elle remonte, mais pas d'un coup.
        j.arme = 'poings';
        o.frame(30);
        const justeApres = mesure();
        for (let i = 0; i < 400; i++) o.frame(1);
        const revenue = mesure();
        // ⚠️ UNE FOULE QUI N'EST PAS DEJA AU PLAFOND. Le murmure voulu vaut
        // `gens / 10`, borne a 1 : a dix passants autour, il vaut deja le maximum,
        // et un cri — qui ne peut pas depasser 1 non plus — ne peut plus etre
        // « plus fort que le murmure ». Le juge passait tant que le depart avait
        // moins de dix passants a cette image-la ; le 16 sept. 2026, un tirage de
        // ville en a mis plus. On eclaircit donc a cinq, et c'est la REGLE qu'on
        // juge, plus la densite du quartier.
        L.Entites.pietonsAutour(j.x, j.y, 200)
          .filter(function (e) { return !e.metier; })
          .slice(5)
          .forEach(function (e) { L.Entites.retirer(e); });
        L.Entites.indexer();
        // Un coup de feu : elle ne murmure pas, elle CRIE.
        R().crier();
        o.frame(15);
        const cri = mesure();
        return { calme: calme, peur: peur, justeApres: justeApres, revenue: revenue, cri: cri };
    }""")
    assert r["calme"]["v"] > 0.05, "la rue est déjà muette : le juge ne prouve rien (%s)" % r
    # Au calme, la rumeur colle à la foule du moment.
    assert abs(r["calme"]["v"] - r["calme"]["voulu"]) < 0.06, "la rumeur ne suit pas la foule : %s" % r
    assert r["peur"]["v"] < r["peur"]["voulu"] * 0.5, "la rue ne se tait pas devant une arme : %s" % r
    # ⚠️ Elle TOMBE d'un coup et REMONTE doucement.
    assert r["justeApres"]["v"] < r["justeApres"]["voulu"] * 0.9, (
        "elle a retrouvé son murmure en une demi-seconde : elle n'a pas eu peur (%s)" % r
    )
    assert r["revenue"]["v"] >= r["revenue"]["voulu"] * 0.8, "elle ne revient jamais : %s" % r
    # ⚠️ Et après un coup de feu, elle crie — plus fort que le murmure que CETTE
    # foule-là mérite. Comparer au volume du début, c'était comparer deux
    # quartiers ; comparer au voulu du moment, c'est juger la règle.
    assert r["cri"]["v"] > r["cri"]["voulu"], (
        "une foule qui murmure pareil avant et après un coup de feu n'est pas une foule, "
        "c'est un bruit de fond (%s)" % r
    )


def test_la_ville_te_parle_selon_ce_qui_se_passe(banc):
    """Chaque contexte se force par le **vrai chemin du jeu** — une arme à la main,
    des missions au compteur, l'heure au ciel — et pas en posant le contexte à la
    main. Un contexte qu'on ne peut pas atteindre, ce sont huit clips morts.

    ⚠️ **Ni la peur ni la nuit ne se redéfinissent dans `son.js`** : la peur est
    celle qui fait déjà taire la rumeur, la nuit est celle du ciel
    (`Monde.estNuit`). C'est pour ça que ce juge-ci sort une batte et avance
    l'horloge au lieu de toucher à un drapeau.

    ⚠️ Et l'**ordre** compte : quand la rue a peur, elle ne demande pas
    d'autographe. La première règle qui passe gagne, comme une manchette."""
    regles = [c["quand"] for c in audio.PAROLE["contextes"]]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, V = L.Son.Voix;
        const midi = 0.5, nuit = 0.95;
        L.B.partie.heure = midi;
        L.B.partie.stats.missions = 0;
        j.arme = 'poings';
        for (let i = 0; i < 30; i++) o.frame(1);
        const rien = V.quand();
        // La rue a peur : une arme a la main, par le chemin d'`Entites.maj`.
        j.arme = 'batte';
        for (let i = 0; i < 30; i++) o.frame(1);
        const peur = V.quand();
        // On la range : la peur s'epuise.
        j.arme = 'poings';
        L.Son.Rumeur.peurT = 0; L.Son.Rumeur.criT = 0;
        const rangee = V.quand();
        // On t'a vu dans le Clairon.
        L.B.partie.stats.missions = %d;
        const celebre = V.quand();
        // ... mais la rue qui a peur ne demande pas d'autographe.
        L.Son.Rumeur.taire();
        const peurDAbord = V.quand();
        L.Son.Rumeur.peurT = 0;
        // La nuit, celle du ciel.
        L.B.partie.stats.missions = 0;
        L.B.partie.heure = nuit;
        const laNuit = V.quand();
        return { rien: rien, peur: peur, rangee: rangee, celebre: celebre,
                 peurDAbord: peurDAbord, nuit: laNuit, estNuit: L.Monde.estNuit(),
                 depart: V.depart() };
    }""" % next(c["missions_min"] for c in audio.PAROLE["contextes"] if c["quand"] == "celebre"))
    assert r["depart"] == audio.CONTEXTE_DE_DEPART
    assert r["rien"] == audio.CONTEXTE_DE_DEPART, "la rue normale n'est pas normale : %s" % r
    assert r["peur"] == "peur", "une batte à la main et la ville dit bonjour : %s" % r
    assert r["rangee"] == audio.CONTEXTE_DE_DEPART, "la peur ne passe jamais : %s" % r
    assert r["celebre"] == "celebre", "on a fait ses missions et personne ne s'en aperçoit : %s" % r
    assert r["peurDAbord"] == "peur", "la rue demande un autographe en ayant peur : %s" % r
    assert r["estNuit"] is True, "le juge n'a pas réussi à faire nuit : %s" % r
    assert r["nuit"] == "nuit", "il fait nuit et les gens souhaitent une belle journée : %s" % r
    # ⚠️ Ce juge-ci ne sait forcer que ces trois-là : un contexte de plus en Python
    # sans son chemin ici (ni dans `son.js`) passerait inaperçu, et ne se jouerait
    # jamais. Les deux listes tiennent ensemble ou pas du tout.
    assert set(regles) == {"peur", "celebre", "nuit"}, (
        f"un contexte que ce juge ne sait pas atteindre : {regles}"
    )


def test_une_banque_sans_clip_se_rabat_sur_la_rue_normale(banc):
    """⚠️ Les vingt-quatre répliques des contextes **n'ont pas encore de mp3** (le
    quota ElevenLabs est à sec jusqu'au 17 oct. 2026), et ça ne doit pas faire taire
    un passant : `audio.exporter()` ne déclare que les fichiers présents, et la
    banque vide se rabat sur `normal`. C'est la même règle que pour les leçons du
    Clairon, du côté du joueur.

    ⚠️ Et un genre **sans** contexte (le crieur, la fille de la Brume) tire dans tout
    ce qu'il a : un homme-sandwich crie son spécial pareil à trois heures du matin."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const V = L.Son.Voix;
        const du = function (genre) {
            return V.liste().filter(function (v) { return v.genre === genre; });
        };
        const slugs = function (liste) { return liste.map(function (v) { return v.slug; }); };
        const hommes = du('homme');
        const normales = hommes.filter(function (v) { return v.quand === 'normal'; });
        return {
            // La banque du contexte, quand elle est la.
            nuit: slugs(V.banque(hommes, 'nuit')).length,
            nuitEstDeNuit: slugs(V.banque(hommes, 'nuit')).every(function (s) {
                return hommes.find(function (v) { return v.slug === s; }).quand === 'nuit';
            }),
            // Rien de charge pour ce contexte : on retombe sur la rue normale.
            filet: slugs(V.banque(normales, 'nuit')),
            attendu: slugs(normales),
            // Un genre sans `quand` : tout ce qu'il a.
            crieur: slugs(V.banque(du('crieur'), 'nuit')).length,
            crieurEnTout: du('crieur').length,
        };
    }""")
    assert r["nuit"] >= 4 and r["nuitEstDeNuit"] is True, "la nuit ne tire pas dans sa banque : %s" % r
    assert r["filet"] == r["attendu"], "une banque sans clip fait taire le passant : %s" % r
    assert r["crieur"] == r["crieurEnTout"] > 0, "le crieur s'est mis à avoir des contextes : %s" % r


def test_les_repliques_d_un_contexte_ne_se_chargent_pas_au_demarrage(banc):
    """⚠️ **VINGT-QUATRE RÉPLIQUES DE PLUS AURAIENT FAIT SAUTER LE BUDGET DE
    DÉMARRAGE** : mesure du 24 sept. 2026, les bruitages du premier écran pesaient
    2,34 Mo pour un plafond de 2,5, et vingt-quatre clips de 40 Ko en font 960. Elles
    arrivent **un contexte à la fois**, la première fois qu'on y entre — exactement
    comme un bruit de quartier ou une pièce de musique.

    ⚠️ Le juge **pose un fichier** à chaque réplique de contexte : sans ça, aucune n'a
    de mp3 (le quota est à sec), rien ne serait demandé de toute façon, et le juge ne
    mesurerait rien. On compte les VRAIES requêtes (`o.fetchs`), pas la taille d'un
    `Set` — un `Set` n'enfle pas quand on y remet ce qui y est déjà, même sans le
    garde."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        // ⚠️ Les mp3 des contextes n'existent pas encore : on leur en pose un, sinon
        // il n'y a rien a ne pas telecharger.
        const contextuelles = L.Son.Voix.liste().filter(function (v) { return v.quand && v.quand !== 'normal'; });
        contextuelles.forEach(function (v) { v.fichier = 'voix-' + v.slug + '.mp3'; });
        const nomme = function (depuis) {
            return o.fetchs.slice(depuis).map(function (f) { return String(f.url || f); });
        };
        // ⚠️ Le jeu a deja charge ses voix au premier geste : on remet le compteur
        // a zero pour REJOUER ce chargement-la, celui du premier ecran, maintenant
        // que les fichiers des contextes existent aux yeux du navigateur.
        L.Son.Voix.chargees = false;
        L.Son.Voix.contextesCharges.clear();
        const avant = o.fetchs.length;
        L.Son.Voix.charger();
        const auDemarrage = nomme(avant);
        const apresCharger = o.fetchs.length;
        L.Son.Voix.chargerContexte('nuit');
        const laNuit = nomme(apresCharger);
        const apresNuit = o.fetchs.length;
        L.Son.Voix.chargerContexte('nuit');
        L.Son.Voix.chargerContexte('nuit');
        return {
            demarrage: auDemarrage.length,
            contextuellesAuDemarrage: auDemarrage.filter(function (u) { return /voix-(peur|celebre|nuit)_/.test(u); }),
            nuit: laNuit.length,
            nuitEstDeNuit: laNuit.every(function (u) { return /voix-nuit_/.test(u); }),
            deuxieme: o.fetchs.length - apresNuit,
            combien: contextuelles.length,
        };
    }""")
    assert r["combien"] == 24, "ce ne sont plus vingt-quatre répliques de contexte : %s" % r
    assert r["demarrage"] > 0, "le démarrage ne télécharge aucune voix : le juge ne mesure rien"
    assert r["contextuellesAuDemarrage"] == [], (
        "des répliques de contexte partent au premier écran : %s" % r["contextuellesAuDemarrage"]
    )
    assert r["nuit"] == 8 and r["nuitEstDeNuit"] is True, "entrer dans la nuit ne charge pas la nuit : %s" % r
    assert r["deuxieme"] == 0, "chaque rencontre retélécharge le contexte : %s requêtes de plus" % r["deuxieme"]


def test_un_passant_tire_dans_la_banque_du_moment(banc):
    """La règle et le tirage sont jugés à part (l'un n'a besoin de rien, l'autre de
    mp3) — reste à prouver que `dire` les **branche** : qu'il demande le contexte du
    moment, charge sa banque et tire dedans.

    ⚠️ Sans ça, les vingt-quatre répliques seraient écrites, déclarées, chargées — et
    jamais dites. C'est la panne du 16 sept. 2026 (« la radio ne parlait pas »),
    qu'on ne refait pas deux fois."""
    r = banc("""async function (L, o) {
        // ⚠️ AVEC DU SON : `chargerContexte` ne demande rien sans AudioContext (meme
        // garde que `Quartier.charger`), et c'est justement ce chargement-la qu'on juge.
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        const V = L.Son.Voix;
        L.B.partie.heure = 0.95;                 // la nuit, celle du ciel
        const vues = [];
        const vraie = V.banque;
        V.banque = function (liste, quand) { vues.push(quand); return vraie(liste, quand); };
        V.dernierT = -99999;
        V.dire('homme', 0, 0);
        V.banque = vraie;
        return { vues: vues, charge: Array.from(V.contextesCharges) };
    }""")
    assert r["vues"] == ["nuit"], "`dire` ne demande pas dans quel monde on est : %s" % r
    assert "nuit" in r["charge"], "`dire` ne charge pas la banque du moment : %s" % r
