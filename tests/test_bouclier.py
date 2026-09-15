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
    const victime = function () {
        const p = o.poser('passant', 14, 0);
        p.etat = 'flane'; p.porteBut = null;
        L.Entites.indexer();
        return p;
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
        L.Missions.interagir(j);
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
        L.Missions.interagir(j);
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
        const sansOtage = mesurer(90);
        // ⚠️ ON POSE LA VICTIME APRES LE TEMOIN, pas avant : pendant les
        // quatre-vingt-dix images sans otage, l'agent tire vingt balles vers
        // le joueur — et celui qu'on voulait prendre en otage se tenait
        // exactement dans la trajectoire. Il mourait, et le juge accusait « il
        // tire malgre l'otage » alors qu'il n'y avait pas d'otage du tout.
        const p = victime();
        L.Missions.interagir(j);
        const avecOtage = mesurer(90);
        return { sansOtage: sansOtage, avecOtage: avecOtage,
                 tientEncore: !!j.otage,
                 recul: L.B.defs.recherche.police.bouclier_recul_px };
    }""" % DECOR)
    assert r["tientEncore"] is True, "le décor du juge est faux : l'otage a lâché (%s)" % r
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
        L.Missions.interagir(j);
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
        L.Missions.interagir(j);
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
