"""M11, troisieme vague — le bouclier humain : une sortie de secours, jamais un abri.

⚠️ **Toute la fiche tient dans cette phrase.** Un otage qu'on tient
indefiniment, c'est l'invincibilite : on traverse la ville derriere un bonhomme
et la police regarde. Trois choses l'en empechent, et elles vont ensemble : il
SE DEBAT, il se degage tout seul au bout de `tenue_max_s`, et le compteur MONTE
tant qu'on le tient. On gagne du temps, on ne gagne pas la partie — et on
ressort plus recherche qu'on est entre.
"""

from app import recherche


def test_tenir_quelqu_un_coute_plus_que_ca_ne_rapporte():
    """⚠️ Le juge qui empeche le bouclier de devenir un abri. Le tenir douze
    secondes doit couter au moins une etoile de chaleur EN PLUS des deux que le
    delit pose — sinon on s'installe derriere lui et on attend que ca passe."""
    b = recherche.BOUCLIER
    monte = b["chaleur_par_s"] * b["tenue_max_s"] * recherche.CHALEUR_PAR_GRAVITE
    assert monte >= recherche.CHALEUR_ETOILE, (
        f"le tenir au maximum ne monte que de {monte} points de chaleur, "
        f"il en faut {recherche.CHALEUR_ETOILE} pour une etoile : c'est un abri gratuit"
    )
    assert b["tenue_max_s"] <= 20, "on le tient une eternite"
    assert 0 < b["debat_s"] < b["tenue_max_s"], "il ne se debat jamais avant de se degager"


def test_la_prise_se_tient_sans_se_faire_attendre():
    """⚠️ Le geste le plus grave d'ACTION est le seul qui demande qu'on insiste
    — parce qu'il est LE DERNIER de la chaine, donc celui qu'on faisait par
    accident. La demi-seconde se juge des deux cotes : assez longue pour
    n'etre plus une pression, assez courte pour qu'une sortie de secours
    s'ouvre AVANT la deuxieme balle."""
    b = recherche.BOUCLIER
    assert b["saisie_s"] >= 0.35, "une pression le declenche encore : ce n'est pas un maintien"
    assert b["saisie_s"] < recherche.POLICE["tir_cadence_s"], (
        "on mange une deuxieme balle avant d'avoir son bouclier : la sortie de secours est fermee"
    )
    # Et ce qu'on passe a l'attraper doit rester petit devant ce qu'on passe a
    # le tenir, sinon la prise mange la sortie qu'elle ouvre.
    assert b["saisie_s"] * 8 <= b["tenue_max_s"], "on l'attrape presque aussi longtemps qu'on le tient"
    assert b["saisie_s"] < b["debat_s"], "il se debat avant meme d'etre pris"


def test_le_bouclier_est_un_delit_bruyant():
    """⚠️ `temoin: False` — un bouclier humain se voit de l'autre bout de la
    rue, et c'est tout son interet. Inutile de convaincre un temoin de quelque
    chose que tout le monde regarde."""
    delit = recherche.DELITS["otage"]
    assert delit["temoin"] is False, "il faudrait un temoin pour un geste qu'on fait en public"
    assert delit["etoiles"] >= 2, "prendre quelqu'un en otage vaut moins qu'un carjacking ?"


def test_on_ne_court_pas_avec_quelqu_un_dans_les_bras():
    """Sans ca, le bouclier devenait la meilleure facon de traverser la ville :
    plus vite que la police et a l'abri de ses balles."""
    assert 0 < recherche.BOUCLIER["vitesse"] < 1


def test_la_police_recule_au_lieu_de_cueillir():
    """⚠️ Sans le recul, le bouclier ne servait a RIEN : les agents cessaient de
    tirer et venaient te prendre a la main, ce qui est pire que de tirer. Le
    recul doit les tenir plus loin que leur bras."""
    assert (recherche.POLICE["bouclier_recul_px"]
            > recherche.POLICE["arrestation_px"] * 3)


def test_la_fiche_descend_au_navigateur():
    """⚠️ Le defaut qui revient : une fiche que le navigateur ne lisait pas."""
    paquet = recherche.exporter()
    assert paquet["bouclier"] == recherche.BOUCLIER
    assert "otage" in paquet["delits"]
    assert paquet["police"]["bouclier_recul_px"] == recherche.POLICE["bouclier_recul_px"]


# --- Le bouclier en jeu ------------------------------------------------------

DECOR = """
    L.Jeu.commencer();
    L.graine(19);
    const j = L.B.joueur, f = L.B.defs.recherche.bouclier;
    const d = o.ligneDroite();
    j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
    L.Entites.regarder(j, 1, 0);
    L.Combat.ramasserArme('pistolet', 12);
    j.arme = 'pistolet';                  // ramasser ne dit pas qu'on la sort
    // ⚠️ ON LE LAISSE FIGE, comme `o.poser` le rend — le decor le remettait a
    // `flane`, et depuis que la prise se tient une demi-seconde ca ne
    // mesurait plus le bouclier. `o.ligneDroite` pose le joueur AU MILIEU DE
    // LA CHAUSSEE, et un pieton sur la chaussee court vers le trottoir le
    // plus proche a `pieton_course` — il sortait des vingt-six pixels de la
    // fiche a la vingt-cinquieme image et la prise tombait avec lui. Ce n'est
    // pas une victime qui s'echappe, c'est un passant qui n'a rien a faire
    // dans la rue : ceux du jeu sont sur le trottoir. Ce qu'on juge ici est
    // le bouclier, pas l'IA des pietons.
    const victime = function () {
        const p = o.poser('passant', 14, 0);
        p.porteBut = null;
        L.Entites.indexer();
        return p;
    };
    // ⚠️ ON TIENT ACTION. Le juge fait le geste que le joueur fait : la
    // pression ARME la prise, c'est le maintien qui la prend. Appeler
    // `Missions.interagir` ne suffit plus — et c'est tout le sujet.
    const saisir = function (images) {
        o.touche('KeyE');
        for (let i = 0; i < (images || Math.round(f.saisie_s * 60) + 2); i++) o.frame(1);
        o.relacher('KeyE');
    };
"""


def test_a_mains_nues_on_ne_prend_personne(banc):
    """⚠️ IL FAUT UNE ARME. A mains nues, « prendre en otage » n'est qu'une
    prise : rien ne dit a la police pourquoi elle devrait s'arreter, et le geste
    n'aurait aucune lecture a l'ecran."""
    r = banc("""function (L, o) {
        %s
        const p = victime();
        j.arme = 'poings';
        const aMainsNues = !!L.Combat.otageSousLaMain(j);
        j.arme = 'pistolet';
        const arme = !!L.Combat.otageSousLaMain(j);
        return { aMainsNues: aMainsNues, arme: arme };
    }""" % DECOR)
    assert r["arme"] is True, "le décor du juge est faux : personne à portée (%s)" % r
    assert r["aMainsNues"] is False, "on prend un otage à mains nues : %s" % r


def test_une_pression_ne_prend_personne_un_maintien_oui(banc):
    """⚠️ **LE JUGE DE LA DEMANDE DE MARTIN** : « il faudrait tenir le bouton
    plus longtemps pour eviter de le faire par accident ». Le bouclier est le
    DERNIER de la chaine d'ACTION — ce que le bouton fait quand il n'a rien
    trouve d'autre a faire. Une pression suffisait : on visait une porte d'un
    pas trop loin, une arme par terre, et on repartait avec un bonhomme dans
    les bras et deux etoiles.

    On mesure les deux cotes dans le meme decor : taper ne prend personne,
    tenir prend — et l'invite du HUD dit qu'il faut tenir."""
    r = banc("""function (L, o) {
        %s
        const p = victime();
        // ⚠️ IL NOUS REGARDE, comme quelqu'un qu'on met en joue. Dans le dos,
        // une tape lui fait les poches (`test_taper_fait_les_poches...`) : il
        // s'enfuit, et la prise tenue plus bas ne trouvait plus personne.
        L.Entites.regarder(p, -1, 0);
        o.frame(1);
        const invite = L.B.invite;               // ce que le HUD promet ici
        // Taper : une fois, puis trois de plus comme on tape sur un bouton qui
        // ne repond pas. ⚠️ La premiere se lit SEULE : quatre pressions d'un
        // coup prenaient l'otage puis le lachaient, et « pas d'otage » etait
        // vrai a la fin pour la mauvaise raison.
        o.tape('KeyE', 4);
        const uneFois = !!j.otage;
        for (let i = 0; i < 3; i++) o.tape('KeyE', 4);
        const tape = { otage: uneFois || !!j.otage,
                       pression: L.B.recherche.chaleur + L.B.recherche.etoiles };
        // Tenir, mais pas assez longtemps : toujours personne. ⚠️ Dix images
        // de marge, pas deux : le banc avance la simulation par pas variables
        // (une image en vaut parfois deux), et un juge qui frole la borne
        // rougit un jour sur deux sans que rien n'ait change.
        saisir(Math.round(f.saisie_s * 60) - 10);
        const presque = !!j.otage;
        saisir();
        return { tape: tape, presque: presque, tenu: j.otage === p, invite: invite,
                 images: Math.round(f.saisie_s * 60) };
    }""" % DECOR)
    assert r["images"] > 8, "le décor du juge est faux : la fiche ne demande presque rien (%s)" % r
    assert r["tape"]["otage"] is False, (
        "une pression prend encore quelqu'un en otage : c'est le bug de Martin (%s)" % r
    )
    assert r["tape"]["pression"] == 0, "taper le bouton a suffi à se faire chercher : %s" % r
    assert r["presque"] is False, "un maintien trop court le prend quand même : %s" % r
    assert r["tenu"] is True, "on tient le bouton et rien ne se passe : %s" % r
    assert "TENIR" in (r["invite"] or ""), (
        "le HUD promet un bouclier sans dire qu'il faut tenir : %s" % r
    )


def test_taper_fait_les_poches_tenir_prend_l_otage(banc):
    """⚠️ **LE JUGE DU RETOUR DE MARTIN** : « je n'arrive plus a voler les gens ».
    La portee du bouclier couvre celle des poches : l'arme a la main, TOUTE
    victime des poches est aussi un otage. Depuis que la prise se tient, la
    pression armait la prise, rendait `true`, et n'allait jamais plus loin. Le
    juge des poches (`test_moteur_js`) appelle `Combat.pickpocket` directement :
    il ne passait pas par le bouton, et il n'a rien vu.

    On passe donc par le BOUTON, dans le dos d'un passant qui a de l'argent :
    une tape vide ses poches et ne prend personne ; une prise tenue prend
    l'otage et ne lui vide PAS les poches en chemin."""
    r = banc("""function (L, o) {
        %s
        const dosTourne = function () {
            const p = victime();
            p.argent = 40;
            L.Entites.regarder(p, 1, 0);          // il regarde ailleurs que nous
            return p;
        };
        const a = dosTourne();
        const avant = L.B.partie.argent;
        o.tape('KeyE', 2);
        const tape = { gain: L.B.partie.argent - avant, reste: a.argent, otage: !!j.otage };
        // ⚠️ On RETIRE le premier : il fuit a quelques pixels, et le bouclier
        // prend le premier passant a portee — on mesurerait le mauvais.
        L.Entites.retirer(a);
        L.Entites.indexer();
        const b = dosTourne();
        const avantPrise = L.B.partie.argent;
        saisir();
        return { tape: tape, arme: j.arme,
                 prise: { otage: j.otage === b, gain: L.B.partie.argent - avantPrise,
                          reste: b.argent } };
    }""" % DECOR)
    assert r["arme"] != "poings", "le décor du juge est faux : on est à mains nues (%s)" % r
    assert r["tape"]["otage"] is False, "une tape a pris un otage : %s" % r
    assert r["tape"]["gain"] == 40 and r["tape"]["reste"] == 0, (
        "l'arme à la main, une tape dans le dos ne fait pas les poches : "
        "c'est le bug de Martin (%s)" % r
    )
    assert r["prise"]["otage"] is True, "tenir le bouton ne prend plus personne : %s" % r
    assert r["prise"]["gain"] == 0 and r["prise"]["reste"] == 40, (
        "la prise tenue lui a fait les poches en chemin : %s" % r
    )


def test_le_prendre_coute_deux_etoiles_et_le_tenir_en_coute_plus(banc):
    """⚠️ On gagne du temps, on ne gagne pas la partie : le compteur monte tant
    qu'on le tient. C'est la seule chose qui empeche le bouclier d'etre un abri."""
    r = banc("""function (L, o) {
        %s
        const p = victime();
        // ⚠️ ON MESURE LA PRESSION, pas les etoiles. `DELITS[x].etoiles` est une
        // GRAVITE qui alimente la chaleur, pas un nombre d'etoiles : un delit de
        // gravite 2 pose 70 points quand il en faut 100 pour une etoile. Et la
        // chaleur RETOMBE a zero chaque fois qu'une etoile se pose — la lire
        // seule, c'est voir le compteur baisser au moment ou il monte.
        const pression = function () {
            const r = L.B.recherche;
            return r.etoiles * L.B.defs.recherche.chaleur_etoile + r.chaleur;
        };
        const avant = pression();
        saisir();
        const pris = { otage: j.otage === p, pression: pression(),
                       dit: p.bulle ? p.bulle.texte : null };
        for (let i = 0; i < 120; i++) o.frame(1);   // deux secondes
        return { avant: avant, pris: pris, apres: pression(),
                 tientEncore: j.otage === p,
                 gravite: L.B.defs.recherche.delits.otage.etoiles,
                 parGravite: L.B.defs.recherche.chaleur_par_gravite };
    }""" % DECOR)
    assert r["avant"] == 0, "le décor du juge est faux : on est déjà recherché (%s)" % r
    assert r["pris"]["otage"] is True, "ACTION ne l'a pas attrapé : %s" % r
    assert r["pris"]["pression"] >= r["gravite"] * r["parGravite"], (
        "le prendre ne coûte rien : %s" % r
    )
    assert r["pris"]["dit"] == recherche.BOUCLIER["dit"]["pris"], "il ne dit rien : %s" % r
    assert r["tientEncore"] is True, "il s'est dégagé en deux secondes : %s" % r
    assert r["apres"] > r["pris"]["pression"], (
        "le compteur ne monte pas pendant qu'on le tient : c'est un abri gratuit (%s)" % r
    )


def test_il_se_debat_et_finit_par_se_degager(banc):
    """⚠️ La borne qui fait du bouclier une SORTIE et pas un abri. On le tient
    le temps de sortir de la ligne de tir, pas le temps de traverser la ville."""
    r = banc("""function (L, o) {
        %s
        const p = victime();
        saisir();
        let images = 0;
        while (j.otage && images < 60 * 60) { o.frame(1); images++; }
        return { images: images, libre: !j.otage, encoreOtage: !!p.otage,
                 fuit: p.etat === 'fuit', dit: p.bulle ? p.bulle.texte : null,
                 max: L.B.defs.recherche.bouclier.tenue_max_s * 60 };
    }""" % DECOR)
    assert r["libre"] is True, "il ne se dégage jamais : %s" % r
    assert r["images"] <= r["max"] + 2, "il se tient plus longtemps que la fiche : %s" % r
    assert r["images"] > r["max"] * 0.5, "il se dégage bien avant l'heure : %s" % r
    assert r["encoreOtage"] is False, "il reste marqué otage après s'être dégagé : %s" % r
    assert r["fuit"] is True, "il repart flâner comme si de rien n'était : %s" % r
    assert r["dit"] == recherche.BOUCLIER["dit"]["libre"], "il part sans un mot : %s" % r


def test_la_police_ne_tire_plus_et_recule(banc):
    """⚠️ SANS LE RECUL, LE BOUCLIER NE SERT A RIEN. Les agents cessaient de
    tirer et venaient te cueillir a la main — ce qui est pire que de tirer, et
    c'est exactement ce que le juge attrape : on mesure les deux."""
    r = banc("""function (L, o) {
        %s
        // Un agent lance a nos trousses, a trois etoiles : il tire.
        L.Police.etoilesAuMoins(3);
        const a = L.Police.creerAgent(j.x + 60, j.y, 'poursuit');
        L.Entites.indexer();
        // ⚠️ `intouchable` : sinon l'agent nous CUEILLE a la huitieme image du
        // temoin et tout le reste se mesure sur un joueur en prison. Le
        // drapeau n'arrete que l'arrestation (`Missions.arrestation`), pas le
        // tir ni la marche — les deux seules choses qu'on mesure ici.
        j.intouchable = true;
        const mesurer = function (images) {
            a.x = j.x + 60; a.y = j.y; a.etat = 'poursuit'; a.chemin = null;
            let tirs = 0;
            for (let i = 0; i < images; i++) {
                a.vuT = 0;
                o.frame(1);
                if (a.etat === 'attaque') tirs++;
            }
            return { tirs: tirs, dFin: Math.round(Math.hypot(a.x - j.x, a.y - j.y)) };
        };
        // ⚠️ L'OTAGE D'ABORD, ET ON LE LACHE ENSUITE — l'ordre inverse de
        // celui que ce juge avait, et c'est la prise qui se TIENT qui l'a
        // impose. La victime se tient a quatorze pixels DEVANT un joueur que
        // vingt balles cherchent : les quatre-vingt-dix images sans otage la
        // tuaient (c'etait deja ecrit ici), et la demi-seconde de saisie la
        // tuait a son tour. On mesure donc le recul d'abord, on le lache, et
        // on remesure : le meme agent, la meme distance de depart, seul
        // l'otage change.
        const p = victime();
        saisir();
        const avecOtage = mesurer(90);
        const tenaitEncore = !!j.otage;          // il ne s'est pas degage pendant la mesure
        L.Combat.lacherOtage(false);
        const sansOtage = mesurer(90);
        return { sansOtage: sansOtage, avecOtage: avecOtage,
                 tenaitEncore: tenaitEncore,
                 recul: L.B.defs.recherche.police.bouclier_recul_px };
    }""" % DECOR)
    assert r["tenaitEncore"] is True, "le décor du juge est faux : l'otage a lâché (%s)" % r
    assert r["sansOtage"]["tirs"] > 0, (
        "le décor du juge est faux : l'agent ne tirait pas même sans otage (%s)" % r
    )
    assert r["sansOtage"]["dFin"] < r["recul"], (
        "le décor du juge est faux : l'agent n'est jamais venu assez près (%s)" % r
    )
    assert r["avecOtage"]["tirs"] == 0, "il tire malgré l'otage : %s" % r
    assert r["avecOtage"]["dFin"] >= r["recul"] - 12, (
        "il ne recule pas : il vient te cueillir à la main, ce qui est pire que de tirer (%s)" % r
    )


def test_il_reste_devant_toi_entre_toi_et_eux(banc):
    """C'est ce qui fait de lui un BOUCLIER et pas un prisonnier qu'on traine.
    ⚠️ Et on le POUSSE au lieu de le poser : sinon on le glisse dans un mur et
    il y reste."""
    r = banc("""function (L, o) {
        %s
        const p = victime();
        saisir();
        const mesures = [];
        [[1, 0], [0, 1], [-1, 0], [0, -1]].forEach(function (dir) {
            L.Entites.regarder(j, dir[0], dir[1]);
            for (let i = 0; i < 12; i++) o.frame(1);
            const dx = p.x - j.x, dy = p.y - j.y;
            // Le produit scalaire avec la direction du regard : positif = devant.
            mesures.push({ devant: +(dx * dir[0] + dy * dir[1]).toFixed(1),
                           loin: +Math.hypot(dx, dy).toFixed(1),
                           mur: L.Monde.bloque(Math.floor(p.x / L.TT), Math.floor(p.y / L.TT),
                                               L.Monde.MASQUE_PIETON) });
        });
        return { mesures: mesures, devant: L.B.defs.recherche.bouclier.devant_px,
                 tientEncore: !!j.otage };
    }""" % DECOR)
    assert r["tientEncore"] is True, "il s'est dégagé pendant la mesure : %s" % r
    for m in r["mesures"]:
        assert m["devant"] > 0, "il n'est pas devant : %s" % r
        assert m["loin"] <= r["devant"] + 6, "il traîne loin derrière : %s" % r
        assert m["mur"] is False, "on l'a glissé dans un mur : %s" % r


def test_on_marche_moins_vite_avec_quelqu_un_dans_les_bras(banc):
    """⚠️ La fiche disait `vitesse` et personne ne la lisait — le défaut qui
    revient. Sans cette ligne, le bouclier humain devenait la meilleure façon de
    traverser la ville : plus vite que la police et à l'abri de ses balles.

    On mesure la MÊME course, sur la même ligne droite, dans le même sens :
    seul l'otage change."""
    r = banc("""function (L, o) {
        %s
        const course = function (images) {
            const x0 = j.x, y0 = j.y;
            o.touche('KeyD');
            for (let i = 0; i < images; i++) o.frame(1);
            o.relacher('KeyD');
            return Math.hypot(j.x - x0, j.y - y0);
        };
        const libre = course(60);
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        L.Entites.regarder(j, 1, 0);
        const p = victime();
        saisir();
        const pris = !!j.otage;
        const charge = course(60);
        return { libre: Math.round(libre), charge: Math.round(charge), pris: pris,
                 voulu: L.B.defs.recherche.bouclier.vitesse,
                 tientEncore: !!j.otage };
    }""" % DECOR)
    assert r["pris"] is True and r["tientEncore"] is True, (
        "le décor du juge est faux : pas d'otage pendant la course (%s)" % r
    )
    assert r["libre"] > 30, "le décor du juge est faux : il n'a pas couru (%s)" % r
    assert r["charge"] < r["libre"], "on court aussi vite avec quelqu'un dans les bras : %s" % r
    # ⚠️ Et c'est bien la fraction de la fiche, pas « un peu moins vite » : un
    # ralentissement au jugé serait un nombre que personne ne peut relire.
    assert abs(r["charge"] / r["libre"] - r["voulu"]) < 0.12, (
        "le ralentissement ne vient pas de la fiche : %s" % r
    )
