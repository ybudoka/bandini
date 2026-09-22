"""Les juges de banc des neuf types de M16, un par mission qui l'introduit (21 sept. 2026).

Chacun des huit types neufs qu'utilisent les dix missions de cette tranche (`acheter`,
`boulots`, `suivre`, `payer`, `pickpocket`, `proteger`, `detruire`, `sauter`) est joué ici
au moins une fois, de l'appel à la récompense ou jusqu'au point qui prouve que l'objectif
peut avancer — sur le modèle de `test_cinq_missions_js.py`. `eteindre` n'est pas de la
partie : `Incendies.feuActif()` dépend de l'heure ambiante de la ville (`jour:heure`), pas
d'un feu que la mission pourrait allumer elle-même — aucune des dix ne s'en sert.
"""

OUTILS = """
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
  function fermer(L) { let g = 0; while (L.B.cinema && g < 100) { L.Histoire.suivante(); g++; } }
  function faites(L, slugs) { slugs.forEach(function (s) { L.B.partie.missionsFaites[s] = 1; }); }
  function paiements(L) {
    const liste = [], vrai = L.Missions.encaisser;
    L.Missions.encaisser = function (montant, raison) { liste.push({ montant: montant, raison: raison || null }); return vrai.apply(null, arguments); };
    return liste;
  }
  function commencer(L, o, slug) {
    L.Histoire.commencer(slug);
    L.B.cinema = null; L.B.scene = null;
  }
  function finir(L, o) { for (let k = 0; k < 400 && L.B.partie.mission; k++) o.frame(1); passer(L, o); }
"""


def test_f04_acheter_un_couteau_puis_chasser_les_cravates(banc):
    """`acheter` (M16) : un article ARME (`Combat.ramasserArme`) remplit `B.partie.armes`,
    ce que `majObjectif` regarde — une bouchée (bière, café) ne laisse rien dans le sac, et
    n'aurait jamais fait avancer l'objectif."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        commencer(L, o, 'f04');
        const avant = etape(L);
        // Une bouchée achetée ne remplit rien : l'objectif ne doit PAS avancer.
        B.partie.objets.biere = true;
        o.frame(2);
        const apresBouchee = etape(L);
        // Un article `arme` (`Combat.ramasserArme`), lui, remplit `B.partie.armes` — c'est
        // exactement ce que fait le menu du comptoir à l'achat réel.
        L.Combat.ramasserArme('couteau', null);
        o.frame(2);
        fermer(L);   // le « pendant » de l'objectif 1 (tuer) ouvre une boîte à son tour
        const apresArme = etape(L), ligne = L.Histoire.ligneObjectif();
        const mo = L.Histoire.donneur('mo');
        j.x = mo.x + 200; j.y = mo.y; L.Entites.indexer();
        const cibles = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        cibles.forEach(function (e) { L.Entites.assommer(e); });
        o.frame(2);
        const etapeRetour = etape(L);
        const mo2 = L.Histoire.donneur('mo');
        j.x = mo2.x - 16; j.y = mo2.y; L.Entites.indexer();
        finir(L, o);
        return { avant: avant, apresBouchee: apresBouchee, apresArme: apresArme, ligne: ligne,
                 etapeRetour: etapeRetour, fait: !!B.partie.missionsFaites.f04,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["avant"] == 0
    assert r["apresBouchee"] == 0, "une bouchée (B.partie.objets) ne fait PAS avancer `acheter`"
    assert r["apresArme"] == 1 and r["ligne"].startswith("CHASSE"), "un article `arme` avance l'objectif"
    assert r["etapeRetour"] == 2
    assert r["fait"] is True and r["argent"] == [150]


def test_f05_boulots_autobus_compte_jusqu_a_quatre(banc):
    """`boulots` (M16) généralise `courses` : `sorte` nomme un compteur de
    `economie.BOULOTS`/`SORTES` — l'autobus n'en avait pas avant cette tranche. Un cycle
    complet au klaxon (ramasse, route, livraison) prouve le branchement ; les trois
    suivants ne rejouent que le compteur, comme `courses` le fait déjà pour le taxi."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        commencer(L, o, 'f05');
        const v = B.mission.vehicule;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        o.frame(2); fermer(L);
        const etapeMonte = etape(L);
        const b = L.Missions.boulot;
        const pris = b.klaxon(v);
        const avantCycle = B.partie.boulots.autobus || 0;
        // Un cycle réel : on va chercher le client, puis la destination.
        for (let k = 0; k < 600 && b.etape === 'ramasse'; k++) {
            if (b.client) { v.x = b.client.x; v.y = b.client.y; v.vitesse = 0; }
            o.frame(1);
        }
        for (let k = 0; k < 600 && b.etape === 'route'; k++) {
            if (b.destination) { v.x = b.destination.x; v.y = b.destination.y; v.vitesse = 0; }
            o.frame(1);
        }
        const apresCycle = B.partie.boulots.autobus || 0;
        // Les trois arrêts suivants : le compteur, comme `courses` pour le taxi.
        B.partie.boulots.autobus = 4;
        o.frame(2);
        const etapeBoulots = etape(L), ligne = L.Histoire.ligneObjectif();
        const l = L.Histoire.lieu('terminus');
        v.x = l.x; v.y = l.y; v.vitesse = 0; j.x = l.x; j.y = l.y; L.Entites.indexer();
        finir(L, o);
        return { etapeMonte: etapeMonte, pris: pris, avantCycle: avantCycle, apresCycle: apresCycle,
                 etapeBoulots: etapeBoulots, ligne: ligne, fait: !!B.partie.missionsFaites.f05,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["etapeMonte"] == 1, "monté dans l'autobus : le boulot suit"
    assert r["pris"] is True, "le klaxon prend le contrat — `SORTES.autobus` existe"
    assert r["avantCycle"] == 0 and r["apresCycle"] == 1, "un cycle complet compte pour un arrêt"
    assert r["etapeBoulots"] == 2 and r["ligne"].startswith("RAMÈNE L'AUTOBUS")
    assert r["fait"] is True and 300 in r["argent"], "200 $, +50 % : l'autobus est rendu sans bosse"


def test_f06_suivre_de_pres_ou_de_loin_puis_payer(banc):
    """`suivre` (M16) : trop loin (`loin`) échoue en `chrono`, trop près (`proche`) échoue en
    `etoile` — mesuré ici sur la voiture du témoin. `payer` (M16) : `Missions.payer` règle le
    silence, sans autre interaction — dès que l'argent y est, l'objectif avance."""
    def jouer(pos):
        return banc("function (L, o) {" + OUTILS + """
            L.Jeu.commencer(); L.graine(6);
            const B = L.B, j = B.joueur; j.invincible = 1e6;
            faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01']);
            B.partie.argent = 500;
            const argent = paiements(L);
            commencer(L, o, 'f06');
            o.frame(1); fermer(L);   // le « pendant » de l'objectif 0 ouvre une boîte
            const v = B.mission.fuyard;
            // Figé : sinon le fuyard (`conducteur: 'trafic'`) roule tout seul et l'écart
            // qu'on vient de poser ne dit plus rien à l'image suivante.
            v.conducteur = null; v.vitesse = 0; v.vx = 0; v.vy = 0;
            j.x = v.x + (POS); j.y = v.y; L.Entites.indexer();
            o.frame(3);
            return { etape: etape(L), raison: B.partie.mission ? null : 'rate',
                     v: !!v, fait: !!B.partie.missionsFaites.f06 };
        }""".replace("POS", str(pos)))
    loin = jouer(11 * 16)     # au-delà de `loin: 10` tuiles (16 px/tuile)
    proche = jouer(1 * 16)    # en-deçà de `proche: 3` tuiles
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01']);
        B.partie.argent = 500;
        const argent = paiements(L);
        commencer(L, o, 'f06');
        o.frame(1); fermer(L);
        const v = B.mission.fuyard;
        v.conducteur = null; v.vitesse = 0; v.vx = 0; v.vy = 0;
        j.x = v.x + 6 * 16; j.y = v.y; L.Entites.indexer();
        o.frame(3);
        const etapeSuivi = etape(L);
        // À portée, ni trop loin ni trop près : `suivre` n'avance PAS tout seul — il n'a
        // pas de `lieu` (arrivée au poste, hors de la portée de ce juge-ci) : on force
        // l'étape suivante à la main, comme le ferait l'arrivée. Sans argent d'abord :
        // `payer` ne fait rien tant que ça n'y est pas.
        B.partie.argent = 0;
        B.partie.mission.etape = 1;
        o.frame(2);
        const etapeSansArgent = etape(L);
        B.partie.argent = 500;
        finir(L, o);
        return { etapeSuivi: etapeSuivi, etapeSansArgent: etapeSansArgent,
                 fait: !!B.partie.missionsFaites.f06, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert loin["v"] and loin["raison"] == "rate", "trop loin : on le perd (`echouer('chrono')`)"
    assert proche["v"] and proche["raison"] == "rate", "trop près : il nous repère (`echouer('etoile')`)"
    assert r["etapeSuivi"] == 0, "à bonne distance, `suivre` tient — il n'avance que par son `lieu`"
    assert r["etapeSansArgent"] == 1, "sans les 200 $, `payer` ne fait rien"
    assert r["fait"] is True and 300 in r["argent"], "300 $ (récompense) : `payer` ferme la mission, sans `retourner`"


def test_f07_pickpocket_vide_les_poches_par_derriere(banc):
    """`pickpocket` (M16) : `Combat.pickpocket` ne assomme PAS sa victime — elle `fuit`,
    poches vides (`argent = 0`). C'est ce signal que `majObjectif` doit guetter, pas
    `assomme` (un vol par-derrière ne le produit jamais)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'f04']);
        const argent = paiements(L);
        commencer(L, o, 'f07');
        o.frame(1); fermer(L);   // le « pendant » de l'objectif 0 ouvre une boîte
        const victime = B.mission.entites.find(function (e) { return e.pickpocket === true; });
        const avant = { etape: etape(L), argent: victime.argent, vivant: victime.vivant };
        // Par-derrière : la victime regarde vers l'est (loin du joueur, à l'ouest), le
        // joueur la regarde — de face pour LUI, de dos pour ELLE. `faceA` lit `e.face`
        // (un nom de direction, `REGARDS`) avant `e.angle` — les deux doivent s'accorder.
        victime.angle = 0;
        j.x = victime.x - 12; j.y = victime.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        const vole = L.Combat.pickpocket(j);
        o.frame(2);
        const apres = { etape: etape(L), argent: victime.argent, vivant: victime.vivant, etat: victime.etat };
        const t2 = L.Histoire.donneur('thibodeau');
        j.x = t2.x - 16; j.y = t2.y; L.Entites.indexer();
        finir(L, o);
        return { avant: avant, vole: vole, apres: apres, fait: !!B.partie.missionsFaites.f07,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["avant"]["etape"] == 0 and r["avant"]["argent"] > 0 and r["avant"]["vivant"] is True
    assert r["vole"] is True, "par-derrière, à portée : le vol réussit"
    assert r["apres"]["argent"] == 0 and r["apres"]["vivant"] is True and r["apres"]["etat"] != "assomme", (
        "un vol par-derrière laisse la victime vivante et EN FUITE — jamais assommée")
    assert r["apres"]["etape"] == 1, "poches vides : l'objectif avance quand même"
    assert r["fait"] is True and 200 in r["argent"], "200 $ de récompense (en plus des poches volées)"


def test_f09_proteger_marco_jusqu_au_kiosque_ou_le_perdre_en_chemin(banc):
    """`proteger` (M16) : la cible nous suit ; morte, échec `protege_mort` ; arrivée à
    `lieu`, l'objectif avance — sans lui, l'objectif ne se terminait JAMAIS (corrigé cette
    tranche-ci : il ne faisait que garder)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01', 'f06']);
        commencer(L, o, 'f09');
        const protege = B.mission.protege;
        const avant = { etape: etape(L), protege: !!protege, vivant: protege && protege.vivant };
        const kiosque = L.Histoire.lieu('kiosque');
        j.x = kiosque.x; j.y = kiosque.y; protege.x = kiosque.x; protege.y = kiosque.y; L.Entites.indexer();
        o.frame(2);
        const arrive = etape(L), ligne = L.Histoire.ligneObjectif();
        return { avant: avant, arrive: arrive, ligne: ligne };
    }""")
    assert r["avant"] == {"etape": 0, "protege": True, "vivant": True}
    assert r["arrive"] == 1 and r["ligne"].startswith("REPOUSSE"), "arrivé au kiosque, vivant : l'objectif avance"

    rm = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01', 'f06']);
        commencer(L, o, 'f09');
        L.Entites.assommer(B.mission.protege);
        o.frame(2);
        return { protege: !!B.partie.mission };
    }""")
    assert rm["protege"] is False, "protégé assommé : la mission échoue (`protege_mort`)"


def test_q03_detruire_le_camion_avant_l_usine(banc):
    """`detruire` (M16) : réutilise `poserLeChar` comme `monter`, mais c'est
    `B.mission.chars[etape]` que `majObjectif` surveille — on ne roule pas dedans, on le
    casse."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        commencer(L, o, 'q03');
        o.frame(1); fermer(L);   // le « pendant » de l'objectif 0 ouvre une boîte : la fermer avant de jouer
        const camion = B.mission.chars[0];
        const avant = { etape: etape(L), camion: camion ? camion.slug : null, etat: camion ? camion.etat : null };
        camion.etat = 'epave';
        o.frame(2);
        const apres = etape(L);
        const gege = L.Histoire.donneur('gege');
        j.x = gege.x - 16; j.y = gege.y; L.Entites.indexer();
        finir(L, o);
        return { avant: avant, apres: apres, fait: !!B.partie.missionsFaites.q03,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["avant"] == {"etape": 0, "camion": "camion", "etat": "stationne"}, r["avant"]
    assert r["apres"] == 1, "le camion est une épave : `detruire` avance"
    assert r["fait"] is True and r["argent"] == [300]


def test_e12_sauter_la_rampe_des_erables_quarante_px_de_vol(banc):
    """`sauter` (M16) : le vol se compte comme le défi *Le Grand Saut* (`vol_px`), tant que
    le véhicule est en l'air (`v.z > 0`) — dans n'importe quelle rampe de la ville, `ou` ne
    servant qu'à pointer le GPS."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        commencer(L, o, 'e12');
        const v = B.mission.vehicule;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        o.frame(2);
        fermer(L);   // le « pendant » de l'objectif 1 (sauter) ouvre une boîte
        const etapeMonte = etape(L);
        const sousLeVol = B.mission.vol;
        // Sous la barre (39/40) : `sauter` ne bouge pas. ⚠️ `v.z` retombe à chaque image
        // (la gravité, hors de la portée de ce juge-ci — c'est le défi Le Grand Saut qui la
        // couvre) : ici on ne juge QUE le seuil que `majObjectif` compare à `vol_px`.
        // `z` assez haut pour rester positif après la gravité de l'image (elle joue
        // AVANT `majObjectif` — un `z` pile à 6 retombait à 0 avant que le juge le voie).
        v.z = 60; v.vx = 0; v.vy = 0; B.mission.vol = 39;
        o.frame(1);
        const etapeSousLaBarre = etape(L);
        v.z = 60; B.mission.vol = 40;
        o.frame(2);
        const apresVol = etape(L), ligne = etapeSousLaBarre === 1 ? L.Histoire.ligneObjectif() : null;
        v.z = 0;
        L.Vehicules.descendre(j, true);   // à pied pour aller voir Xavier — `j.x/y` suit le char tant qu'on y est
        const xav = L.Histoire.donneur('xavier');
        j.x = xav.x - 16; j.y = xav.y; L.Entites.indexer();
        finir(L, o);
        return { etapeMonte: etapeMonte, sousLeVol: sousLeVol, etapeSousLaBarre: etapeSousLaBarre,
                 apresVol: apresVol, ligne: ligne,
                 fait: !!B.partie.missionsFaites.e12, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["etapeMonte"] == 1 and r["sousLeVol"] == 0
    assert r["etapeSousLaBarre"] == 1, "39/40 px de vol : `sauter` ne bouge pas encore"
    assert r["apresVol"] == 2, f"40 px de vol : `sauter` avance : {r}"
    assert r["fait"] is True and r["argent"] == [200]
