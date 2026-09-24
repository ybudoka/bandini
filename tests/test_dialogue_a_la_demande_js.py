"""M16 — ce qu'une mission dit, montre et avec quelles voix : hors du paquet.

Le paquet des définitions était **au-dessus de ses deux plafonds** le 24 sept. 2026
(369 224 octets bruts pour 250 000, 75 138 gzip pour 54 000) : trois sessions l'avaient
grossi le même jour sans se voir. Le catalogue y reste — le carnet, le GPS et le
téléphone le lisent en entier — et les répliques, les scènes et la déclaration des voix
partent sur `/api/dialogue/<slug>`.

⚠️ **Un texte ne peut pas arriver en retard**, contrairement à une voix : une réplique
sans son mp3 s'affiche quand même (`Son.Voix.attendue` la dit dès qu'il arrive), un
dialogue absent n'a **rien** à afficher. Les juges d'ici partent donc d'un **catalogue
nu** (`poser_les_dialogues=False`) et attendent vraiment le réseau.
"""


def test_le_banc_pose_les_dialogues_par_defaut(banc):
    """⚠️ **CE JUGE-CI EXPLIQUE LES CENT AUTRES.** `o.frame()` est synchrone, et une
    réponse de `fetch` arrive sur une micro-tâche : entre deux images du banc il n'y en a
    aucune. Une centaine de juges qui jouent une mission de bout en bout devraient chacun
    devenir asynchrones pour attendre un texte qui, dans le vrai jeu, est arrivé pendant
    qu'on marchait vers le donneur. Le banc le pose donc d'avance — et c'est pour ça que
    le chemin du téléchargement a les juges d'ici, qui partent d'un catalogue nu."""
    r = banc("""function (L, o) {
        const m = L.B.defs.missions[0];
        const voix = L.Son.Voix.histoire().filter(function (v) { return v.mission === m.slug; });
        return { dialogue: !!m.dialogue, scenes: !!m.scenes, voix: voix.length };
    }""")
    assert r["dialogue"] is True and r["scenes"] is True
    assert r["voix"] > 0, "les voix de la mission ne sont pas déclarées : le banc ne joue rien"


def test_un_catalogue_nu_n_a_ni_repliques_ni_scenes(banc):
    """Le paquet ne porte que le catalogue — et il le porte EN ENTIER : `disponibles()`
    et le carnet en ont besoin pour savoir quelle mission est possible."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const m = L.B.defs.missions[0];
        return { combien: L.B.defs.missions.length, dialogue: !!m.dialogue, scenes: !!m.scenes,
                 titre: m.titre, objectifs: m.objectifs.length,
                 dispo: L.Histoire.disponibles().map(function (x) { return x.slug; }) };
    }""", poser_les_dialogues=False)
    assert r["dialogue"] is False and r["scenes"] is False
    assert r["combien"] >= 30 and r["titre"] and r["objectifs"] > 0
    assert r["dispo"] == ["m1"], "le catalogue nu ne dit plus quelle mission est possible : %s" % r


def test_la_bulle_d_un_donneur_demande_son_texte(banc):
    """⚠️ **C'EST LÀ QUE LA MARGE SE GAGNE.** Un donneur est visible à plusieurs secondes
    de marche : sa bulle qui s'allume demande son texte, et la porte n'attend jamais.

    ⚠️ Et **une seule fois** : `majBulles` tourne à chaque image, sur toutes les entités.
    Une demande par image, ce sont soixante requêtes par seconde."""
    r = banc("""async function (L, o) {
        L.Jeu.commencer();
        const avant = o.fetchs.length;
        o.frame(1); o.frame(1); o.frame(1);
        const demandes = o.fetchs.slice(avant).map(function (f) { return String(f.url); })
          .filter(function (u) { return u.indexOf('/api/dialogue/') === 0; });
        await o.attendre();
        const m = L.Histoire.disponibles()[0];
        return { demandes: demandes, texte: !!(m && m.dialogue) };
    }""", poser_les_dialogues=False)
    assert r["demandes"], "la bulle de Ti-Guy ne demande pas son texte"
    assert len(r["demandes"]) == 1, "une demande par image : %s" % r["demandes"]
    assert "/api/dialogue/m1" in r["demandes"][0]
    assert r["texte"] is True, "le texte est arrivé mais la mission ne l'a pas"


def test_on_parle_au_donneur_et_la_mission_part_quand_son_texte_arrive(banc, dialogues):
    """La porte elle-même, depuis un catalogue nu : ACTION sur le donneur, le texte
    arrive, l'intro se joue et les voix de la mission sont déclarées.

    ⚠️ Sans la déclaration des voix, le texte s'afficherait et **personne ne parlerait** —
    `Son.Voix.histoire()` lit la liste du paquet, et celles d'une mission n'y sont plus."""
    r = banc("""async function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, t = L.Histoire.donneur('ti_guy');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        o.viser(t);
        const parle = L.Missions.interagir(j);
        const tout_de_suite = !!L.B.cinema;
        // Le texte vole : on laisse passer les micro-taches, comme le vrai navigateur.
        for (let i = 0; i < 4; i++) await o.attendre();
        const cinema = L.B.cinema;
        const voix = L.Son.Voix.histoire().filter(function (v) { return v.mission === 'm1'; });
        return { parle: parle, tout_de_suite: tout_de_suite, mission: L.B.partie.mission && L.B.partie.mission.slug,
                 lignes: cinema ? cinema.lignes.length : 0, qui: cinema ? cinema.lignes[0].qui : null,
                 slug: cinema ? cinema.lignes[0].slug : null, voix: voix.length,
                 demandee: L.Son.Voix.demandees[0] };
    }""", poser_les_dialogues=False)
    assert r["parle"] is True, "ACTION sur le donneur ne fait rien"
    assert r["tout_de_suite"] is False, "la boîte s'ouvre avant que le texte soit là"
    assert r["mission"] == "m1", "la mission ne se pose pas quand son texte arrive : %s" % r
    assert 1 <= r["lignes"] <= len(dialogues["m1"]["dialogue"]["intro"])
    assert r["qui"] == "ti_guy" and r["slug"] == "ti_guy-m1-1"
    assert r["voix"] == len(dialogues["m1"]["voix"]), "les voix de la mission ne sont pas déclarées"
    assert r["demandee"] == "ti_guy-m1-1", "la réplique demande sa voix"


def test_deux_coups_d_action_ne_posent_pas_la_mission_deux_fois(banc):
    """⚠️ Le texte vole, le joueur appuie encore : sans garde, la mission se poserait deux
    fois et son intro se jouerait deux fois.

    ⚠️ **ON COMPTE LES DEMANDES DE VOIX, pas `cinema.i`** : trois intros jouées d'affilée
    laissent la dernière au début, et `i === 0` était vrai des deux côtés — le juge
    passait, la garde neutralisée. Ce qu'on entendrait, c'est la première réplique
    demandée trois fois."""
    r = banc("""async function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, t = L.Histoire.donneur('ti_guy');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        o.viser(t);
        L.Missions.interagir(j);
        L.Missions.interagir(j);
        L.Missions.interagir(j);
        for (let i = 0; i < 4; i++) await o.attendre();
        const cinema = L.B.cinema;
        return { lignes: cinema ? cinema.lignes.length : 0,
                 premiere: L.Son.Voix.demandees.filter(function (s) { return s === 'ti_guy-m1-1'; }).length,
                 demandes: o.fetchs.map(function (f) { return String(f.url); })
                   .filter(function (u) { return u.indexOf('/api/dialogue/m1') === 0; }).length };
    }""", poser_les_dialogues=False)
    assert r["demandes"] == 1, "%s demandes pour le même dialogue" % r["demandes"]
    assert r["premiere"] == 1, "la première réplique est dite %s fois : l'intro s'est rejouée (%s)" % (r["premiere"], r)


def test_un_reseau_qui_tombe_ne_ferme_pas_la_mission(banc):
    """⚠️ On OUBLIE la demande qui a échoué : la porte redemandera. Sans ça, un réseau qui
    tombe une fois fermerait la mission pour le reste de la partie."""
    r = banc("""async function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, t = L.Histoire.donneur('ti_guy');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        o.viser(t);
        L.Missions.interagir(j);
        for (let i = 0; i < 4; i++) await o.attendre();
        const apresLaPanne = !!L.B.cinema;
        // On rappuie : le reseau est revenu.
        L.Missions.interagir(j);
        for (let i = 0; i < 4; i++) await o.attendre();
        return { apresLaPanne: apresLaPanne, ensuite: !!L.B.cinema,
                 mission: L.B.partie.mission && L.B.partie.mission.slug };
    }""", poser_les_dialogues=False, dialogues_panne=1)
    assert r["apresLaPanne"] is False, "la boîte s'ouvre alors que le texte n'est jamais arrivé"
    assert r["ensuite"] is True and r["mission"] == "m1", \
        "le réseau est revenu et la mission reste fermée : %s" % r


def test_une_partie_reprise_en_pleine_mission_demande_son_texte(banc):
    """⚠️ Une partie sauvegardée l'est bien après son intro : elle a `partie.mission` et
    pas une ligne de son dialogue. Tout ce que `maj()` lit ensuite — les répliques
    `pendant`, la fin, l'échec — le cherche dedans."""
    r = banc("""async function (L, o) {
        L.Jeu.commencer();
        // Une partie reprise : la mission est en cours, son texte n'est pas la.
        L.Histoire.reinitialiser('m2');
        L.B.partie.missionsFaites = { m1: true };
        L.B.partie.mission = { slug: 'm2', etape: 0 };
        L.B.mission = null;
        const avant = o.fetchs.length;
        o.frame(1); o.frame(1);
        const demandes = o.fetchs.slice(avant).map(function (f) { return String(f.url); })
          .filter(function (u) { return u.indexOf('/api/dialogue/m2') === 0; });
        for (let i = 0; i < 4; i++) await o.attendre();
        o.frame(1);
        const m = L.Histoire.courante();
        return { demandes: demandes.length, texte: !!(m && m.dialogue), vivant: !!L.B.joueur.vivant };
    }""", poser_les_dialogues=False)
    assert r["demandes"] >= 1, "une partie reprise en pleine mission ne demande pas son texte"
    assert r["texte"] is True and r["vivant"] is True, r


def test_le_telephone_ne_sonne_pas_pour_une_mission_sans_texte(banc):
    """⚠️ Le combiné décroche sur une réplique d'appel : sans elle, il sonnerait dans le
    vide et le joueur irait voir un donneur qui n'a rien à dire. On demande donc le texte
    **avant** la sonnerie — elle a `DELAI_APPEL` (dix secondes) pour arriver.

    Ici le réseau ne répond jamais : le téléphone doit rester muet, et le délai ne doit
    même pas partir."""
    r = banc("""async function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        p.missionsFaites = { m1: true };
        p.appels = {}; p.appelT = null;
        for (let i = 0; i < 900; i++) { o.frame(1); if (i % 100 === 0) await o.attendre(); }
        const m = L.Histoire.disponibles()[0];
        return { sonnerie: !!L.B.sonnerie, appelT: p.appelT, dispo: m && m.slug,
                 texte: !!(m && m.dialogue), appels: Object.keys(p.appels).length };
    }""", poser_les_dialogues=False, dialogues_panne=99)
    assert r["dispo"] == "m2", "ce n'est pas m2 qui devrait appeler : %s" % r
    assert r["texte"] is False, "le réseau a répondu : le juge ne mesure rien"
    assert r["sonnerie"] is False, "le téléphone sonne pour une mission qui n'a rien à dire"
    assert r["appelT"] is None, "le délai de l'appel part sans que le texte soit demandé"
    assert r["appels"] == 0, "l'appel est marqué comme fait alors qu'il n'a jamais été dit"
