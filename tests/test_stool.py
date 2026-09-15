"""M11, troisieme vague — le stool : celui qui n'a rien vu, et qui te reconnait.

⚠️ **Ce n'est pas un temoin, et la difference est tout le personnage.** Le
temoin porte un CRIME : il a vu quelque chose, il court le raconter, son
silence vaut vingt piastres. Le stool n'a rien vu — il a reconnu ta FACE, parce
que ta face est dans le journal et sur les affiches. Il n'a besoin d'aucun
delit, il part telephoner, et ce qu'il donne au poste n'est pas de la chaleur :
c'est un SIGNALEMENT, donc un PLANCHER d'etoiles.

C'est ce qui referme M11 : la premiere vague a fait que le dossier allonge le
cone des agents, celle-ci fait qu'il transforme les passants en delateurs.
"""

from app import recherche


def test_le_stool_ne_se_confond_pas_avec_un_temoin():
    """⚠️ S'il coutait le meme prix et donnait la meme chose, ce serait un
    temoin avec un autre nom. Son silence coute plus cher (il marchande QUI TU
    ES, pas ce qu'il a vu) et il pose un PLANCHER d'etoiles la ou le temoin ne
    fait qu'ajouter de la chaleur."""
    from app import economie
    stool = recherche.STOOL
    assert stool["prix"] > economie.TARIFS["silence_temoin"], (
        "le silence du stool coute le prix de celui d'un temoin : ce sont deux "
        "personnages pour une seule regle"
    )
    assert 0 < stool["etoiles"] <= recherche.ETOILES_MAX, stool["etoiles"]


def test_le_stool_ne_naît_pas_sans_dossier():
    """Un dossier mince ne dit rien a personne — on n'est pas encore quelqu'un.
    ⚠️ C'est le minimum qui fait que la premiere heure de jeu est tranquille,
    et que la denonciation ARRIVE au lieu d'avoir toujours ete la."""
    assert recherche.STOOL["casier_minimum"] > 0, "on est reconnu des le premier matin"
    assert recherche.STOOL["casier_minimum"] < recherche.ETOILES_MAX * 4


def test_le_stool_doit_etre_devant_toi():
    """⚠️ LE JUGE DE LA FICHE M11 : « le stool ne nait pas dans le dos d'un
    joueur immobile ». Un cone de 360 degres, c'est un dos ; une denonciation
    qu'on ne peut pas voir venir n'est pas une regle, c'est une taxe."""
    assert 0 < recherche.STOOL["devant_degres"] < 360


def test_la_rue_ne_se_relaie_pas_au_telephone():
    """Le repit : apres un appel ou un achat, personne ne recommence tout de
    suite. ⚠️ Sans lui, un gros casier n'est plus une regle, c'est une
    condamnation — on paie, on repart, et le suivant decroche."""
    assert recherche.STOOL["repit_s"] >= 30
    assert recherche.STOOL["chance_max"] < 1.0, "a chance 1, chaque occasion en produit un"


def test_le_stool_a_de_quoi_parler():
    """Ce qu'il dit doit se lire comme une RECONNAISSANCE, pas comme une
    accusation — c'est ce qui fait froid dans le dos. Et il repond quand on le
    paie : un silence achete en silence ne se sent pas.

    ⚠️ Ses mots vivent dans `recherche.STOOL`, pas dans `pietons.PAROLES` :
    cette table-la range ce qu'une SORTE de gens dit — un metier, un corps, une
    routine. Le stool n'est aucune sorte : c'est un ETAT que n'importe quel
    passant peut prendre, et c'est precisement ce qui le rend inquietant."""
    mots = recherche.STOOL["dit"]
    for cle in ("reconnait", "achete"):
        assert mots.get(cle), cle
        assert mots[cle] == mots[cle].upper(), f"{cle} : la bulle se lit en capitales"


def test_la_fiche_descend_au_navigateur():
    """⚠️ Le defaut qui revient : une fiche que le navigateur ne lisait pas."""
    paquet = recherche.exporter()
    assert paquet["stool"] == recherche.STOOL
    assert paquet["stool"]["dit"] == recherche.STOOL["dit"]


# --- Le stool en jeu --------------------------------------------------------

#: Le decor commun : un joueur au casier epais, plante sur une ligne droite,
#: qui REGARDE vers l'est. ⚠️ On force la chance a 1 : a trois pour cent la
#: page, attendre le hasard c'est jouer a pile ou face avec le juge — on met la
#: regle au maximum et on mesure la REGLE. Le taux livre, lui, se juge en
#: Python, au-dessus.
DECOR = """
    L.Jeu.commencer();
    L.graine(31);
    const f = L.B.defs.recherche.stool, j = L.B.joueur;
    f.chance_par_page = 1; f.chance_max = 1;
    L.B.partie.casier = 8;
    const d = o.ligneDroite();
    j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
    L.Entites.regarder(j, 1, 0);          // il regarde vers l'est
    const occasions = function (n) {
        for (let i = 0; i < n; i++) { L.B.t += f.occasion_images; L.Police.majStools(); }
    };
"""


def test_le_stool_ne_naît_jamais_dans_le_dos_du_joueur(banc):
    """⚠️ LE JUGE DE LA FICHE, mesure sur place. Le meme passant, a la meme
    distance, devant puis derriere : devant il te reconnait, derriere il ne
    peut pas. C'est la seule facon de rendre la denonciation JOUABLE — on la
    voit partir, on a le temps de payer ou de frapper.

    ⚠️ Et le temoin du juge est indispensable : sans la mesure « devant », un
    stool qui ne naitrait JAMAIS passerait ce juge au vert."""
    r = banc("""function (L, o) {
        %s
        const essai = function (dx, dy) {
            L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.agent; })
                       .forEach(function (e) { L.Entites.retirer(e); });
            const p = o.poser('passant', dx, dy);
            p.etat = 'flane'; p.porteBut = null;
            L.B.recherche.stoolT = 0;
            L.Entites.indexer();
            occasions(40);
            return { stool: !!p.stool, porte: !!p.porteBut };
        };
        // ⚠️ DEUX FACONS D'ETRE DERRIERE, et la deuxieme est la vraie epreuve.
        // Pile dans le dos, c'est 180 degres : meme un cone de 359 l'exclut, et
        // le juge passait au vert en ne prouvant rien. Par-dessus l'epaule,
        // c'est 146 degres — dehors a 100, dedans a 359. C'est cette
        // mesure-la qui tient la regle.
        const devant = essai(70, 0), dos = essai(-70, 0), epaule = essai(-60, -40);
        return { devant: devant, dos: dos, epaule: epaule };
    }""" % DECOR)
    assert r["devant"]["stool"] is True, (
        "le décor du juge est faux : personne ne te reconnaît même de face (%s)" % r
    )
    assert r["devant"]["porte"] is True, "il te reconnaît et ne va nulle part : %s" % r
    assert r["dos"]["stool"] is False, (
        "il te reconnaît DE DOS : la dénonciation n'est plus jouable (%s)" % r
    )
    assert r["epaule"]["stool"] is False, (
        "il te reconnaît par-dessus ton épaule : le cône est trop large (%s)" % r
    )


def test_sans_dossier_personne_ne_te_reconnaît(banc):
    """Le temoin de la regle du casier : le meme passant, au meme endroit, une
    fois avec un dossier et une fois sans."""
    r = banc("""function (L, o) {
        %s
        const essai = function (casier) {
            L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.agent; })
                       .forEach(function (e) { L.Entites.retirer(e); });
            L.B.partie.casier = casier;
            const p = o.poser('passant', 70, 0);
            p.etat = 'flane'; p.porteBut = null;
            L.B.recherche.stoolT = 0;
            L.Entites.indexer();
            occasions(40);
            return !!p.stool;
        };
        const blanc = essai(0), sousLeSeuil = essai(L.B.defs.recherche.stool.casier_minimum - 1);
        const epais = essai(8);
        return { blanc: blanc, sousLeSeuil: sousLeSeuil, epais: epais };
    }""" % DECOR)
    assert r["epais"] is True, "le décor du juge est faux : même à huit pages, personne (%s)" % r
    assert r["blanc"] is False, "un dossier blanc se fait dénoncer : %s" % r
    assert r["sousLeSeuil"] is False, "le minimum de la fiche ne tient pas : %s" % r


def test_son_appel_pose_un_plancher_et_pas_de_la_chaleur(banc):
    """⚠️ TOUTE LA DIFFERENCE AVEC LE TEMOIN. Un delit vu pose de la CHALEUR :
    il en faut trois pour une etoile. Un signalement telephone pose un
    PLANCHER : deux etoiles d'un coup, parce que le poste sait maintenant qui
    te chercher. `police.js` le disait deja en toutes lettres (« la difference
    entre quelqu'un a vu et quelqu'un a appele ») ; il manquait quelqu'un pour
    decrocher.

    ⚠️ Et `dernierVu` tombe SUR LE SEUIL, pas sur le joueur : c'est ce que le
    stool a donne, et c'est la que les autos vont chercher. On a donc quelques
    secondes pour ne plus y etre — sans ca, l'appel serait un mouchard colle
    dans le dos."""
    r = banc("""function (L, o) {
        %s
        const p = o.poser('passant', 70, 0);
        p.etat = 'flane'; p.porteBut = null;
        L.B.recherche.stoolT = 0;
        L.Entites.indexer();
        occasions(40);
        const avant = L.B.recherche.etoiles;
        // On le plante loin du joueur pour que le seuil ne soit pas ses pieds.
        p.x = j.x + 300; p.y = j.y + 200;
        L.Police.appelDuStool(p);
        const r2 = L.B.recherche;
        return { etaitStool: true, avant: avant, apres: r2.etoiles,
                 plancher: L.B.defs.recherche.stool.etoiles,
                 chaleur: r2.chaleur, encoreStool: !!p.stool,
                 vuX: Math.round(r2.dernierVu.x), vuY: Math.round(r2.dernierVu.y),
                 seuilX: Math.round(p.x), seuilY: Math.round(p.y),
                 joueurX: Math.round(j.x), joueurY: Math.round(j.y),
                 repit: r2.stoolT > L.B.t };
    }""" % DECOR)
    assert r["avant"] == 0, "le décor du juge est faux : on a déjà des étoiles (%s)" % r
    assert r["apres"] >= r["plancher"], "l'appel n'a rien donné : %s" % r
    assert r["chaleur"] == 0, "un signalement chauffe l'ambiance au lieu de nommer : %s" % r
    assert r["encoreStool"] is False, "il reste un stool après avoir appelé : %s" % r
    assert (r["vuX"], r["vuY"]) == (r["seuilX"], r["seuilY"]), (
        "la police va chercher où était le JOUEUR, pas où le stool a téléphoné : %s" % r
    )
    assert (r["vuX"], r["vuY"]) != (r["joueurX"], r["joueurY"])
    assert r["repit"] is True, "la rue peut se relayer au téléphone tout de suite : %s" % r


def test_on_achete_son_silence_et_ca_coute_plus_cher_qu_un_temoin(banc):
    """Il marchande QUI TU ES, pas ce qu'il a vu — et le prix monte avec le
    dossier, comme l'amende, comme l'avocat. ⚠️ Le HUD doit l'annoncer AVANT
    qu'on appuie : une invite qui dit autre chose que ce qu'ACTION va faire est
    pire que pas d'invite du tout."""
    r = banc("""function (L, o) {
        %s
        const p = o.poser('passant', 70, 0);
        p.etat = 'flane'; p.porteBut = null;
        L.B.recherche.stoolT = 0;
        L.Entites.indexer();
        occasions(40);
        const prix = L.Police.prixDuStool();
        // On s'approche a portee de main, et on regarde ce que le HUD annonce.
        p.x = j.x + 12; p.y = j.y;
        L.Entites.indexer();
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        L.B.partie.argent = 10;
        const tropPauvre = L.Missions.interagir(j);
        const encoreStool = L.Police.estStool(p);
        L.B.partie.argent = 50000;
        L.Missions.interagir(j);
        return { prix: prix, invite: invite, tropPauvre: tropPauvre,
                 encoreStoolQuandPauvre: encoreStool,
                 achete: !L.Police.estStool(p), porte: !!p.porteBut,
                 paye: 50000 - L.B.partie.argent, dit: p.bulle ? p.bulle.texte : null,
                 repit: L.B.recherche.stoolT > L.B.t,
                 silenceTemoin: L.B.defs.economie.tarifs.silence_temoin };
    }""" % DECOR)
    assert r["prix"] > r["silenceTemoin"], "il vend au prix d'un témoin : %s" % r
    assert r["invite"] == "ACHETER SON SILENCE — %s $" % r["prix"], (
        "le HUD n'annonce pas ce qu'ACTION va faire : %s" % r
    )
    assert r["tropPauvre"] is True and r["encoreStoolQuandPauvre"] is True, (
        "sans l'argent, il se tait quand même : %s" % r
    )
    assert r["achete"] is True and r["porte"] is False, "il continue vers le téléphone : %s" % r
    assert r["paye"] == r["prix"], "il ne prend pas le prix de la fiche : %s" % r
    assert r["dit"] == recherche.STOOL["dit"]["achete"], "il ne dit rien : %s" % r
    assert r["repit"] is True, "un autre peut décrocher tout de suite : %s" % r


def test_assomme_il_n_appelle_pas(banc):
    """⚠️ La deuxieme facon de le faire taire, et elle a son prix en etoiles :
    assommer quelqu'un dans la rue, ca se voit. Mais il marchait jusqu'a la
    porte LES YEUX FERMES — `majPorte` ne regardait pas s'il tenait debout, et
    ca ne comptait guere tant qu'il s'agissait de rentrer souper."""
    r = banc("""function (L, o) {
        %s
        const p = o.poser('passant', 70, 0);
        p.etat = 'flane'; p.porteBut = null;
        L.B.recherche.stoolT = 0;
        L.Entites.indexer();
        occasions(40);
        const avantCoup = { stool: L.Police.estStool(p), porte: !!p.porteBut };
        L.Entites.assommer(p);
        o.frame(5);
        return { avantCoup: avantCoup, apres: L.Police.estStool(p),
                 porte: !!p.porteBut, etat: p.etat };
    }""" % DECOR)
    assert r["avantCoup"]["stool"] is True, "le décor du juge est faux : pas de stool (%s)" % r
    assert r["etat"] == "assomme"
    assert r["porte"] is False, "un homme assommé continue son chemin : %s" % r
    assert r["apres"] is False, "il téléphone dans les pommes : %s" % r


def test_un_seul_stool_a_la_fois(banc):
    """⚠️ Sans ca, un gros casier n'est plus une regle, c'est une condamnation :
    on paie le premier, le deuxieme decroche, et la rue entiere se relaie."""
    r = banc("""function (L, o) {
        %s
        const gens = [o.poser('passant', 60, 0), o.poser('passant', 80, 10),
                      o.poser('passant', 70, -10)];
        gens.forEach(function (p) { p.etat = 'flane'; p.porteBut = null; });
        L.B.recherche.stoolT = 0;
        L.Entites.indexer();
        occasions(60);
        return { stools: gens.filter(function (p) { return L.Police.estStool(p); }).length };
    }""" % DECOR)
    assert r["stools"] == 1, "%s stools en même temps : la rue se relaie au téléphone" % r["stools"]


def test_changer_de_tete_fait_taire_celui_qui_est_deja_en_route(banc):
    """⚠️ LE SEUL LEVIER QUE LE JOUEUR AIT VRAIMENT CONTRE LE STOOL. Le casier ne
    redescend qu'en payant l'avocat ou le comptoir du fond ; du linge neuf, lui,
    se trouve a la friperie pour quelques piastres. Sans ca, un gros dossier
    n'etait plus une regle : c'etait une taxe qu'on paie jusqu'a la fin de la
    partie.

    ⚠️ Et celui qui etait DEJA en route raccroche : il cherchait une tete qui
    n'existe plus. Un repit qui ne vaudrait que pour les prochains laisserait le
    telephone sonner quand meme."""
    r = banc("""function (L, o) {
        %s
        const p = o.poser('passant', 70, 0);
        p.etat = 'flane'; p.porteBut = null;
        L.B.recherche.stoolT = 0;
        L.Entites.indexer();
        occasions(40);
        const enRoute = { stool: L.Police.estStool(p), porte: !!p.porteBut };
        L.Missions.porterTenue('coupe_vent');
        const apres = { stool: L.Police.estStool(p), porte: !!p.porteBut };
        // ... et personne ne prend le relais pendant le repit.
        const repit = L.B.recherche.stoolT - L.B.t;
        occasions(10);
        const relais = L.B.entites.filter(L.Police.estStool).length;
        return { enRoute: enRoute, apres: apres, relais: relais,
                 repitImages: repit,
                 voulu: L.B.defs.recherche.stool.repit_deguisement_s * 60 };
    }""" % DECOR)
    assert r["enRoute"]["stool"] is True, "le décor du juge est faux : pas de stool (%s)" % r
    assert r["apres"]["stool"] is False, "il te reconnaît encore en coupe-vent : %s" % r
    assert r["apres"]["porte"] is False, "il continue vers le téléphone : %s" % r
    assert r["relais"] == 0, "un autre prend le relais pendant le répit : %s" % r
    assert r["repitImages"] == r["voulu"], "le répit ne vient pas de la fiche : %s" % r
    # ⚠️ Et il est plus long que celui d'un simple achat : payer un gars, c'est
    # payer UN gars ; changer de tête, c'est ne plus être le même.
    assert recherche.STOOL["repit_deguisement_s"] > recherche.STOOL["repit_s"]
