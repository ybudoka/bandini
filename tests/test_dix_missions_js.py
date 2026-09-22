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


#: Le parcours de Martin (22 sept. 2026) : garé devant le casse-croûte, on entre, Bouchard
#: donne f06 DEDANS, on sort par la porte, on monte dans son char. `SUITE` joue ce qui vient
#: après ; `c` est le stool, `mien` notre char, `fermer()` passe les répliques.
F06 = "function (L, o) {" + OUTILS + """
    L.Jeu.commencer(); L.graine(6);
    const B = L.B, j = B.joueur, M = L.Monde; j.invincible = 1e6;
    faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01']);
    B.partie.argent = 500;
    const argent = paiements(L);
    const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === 'casse_croute' && q.interieur; });
    const arret = L.Histoire.tuileDeRue(porte.x * 16 + 8, (porte.y + 1) * 16 + 10, 10);
    const mien = L.Vehicules.creer('auto', arret.x, arret.y, CAP[arret.sens], { etat: 'stationne' });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    L.Histoire.commencer('f06');
    passer(L, o);
    const c = B.mission.suivi;
    L.Jeu.sortir(); o.fondu();
    for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
    function fermerTout() { fermer(L); }
    fermerTout();
    const dSortie = Math.round(Math.hypot(c.x - j.x, c.y - j.y));
    // À pied, cinq secondes : il attend qu'on soit au volant, rien ne rate.
    for (let i = 0; i < 300 && B.partie.mission; i++) { o.frame(1); fermerTout(); }
    const aPied = { etape: etape(L), attend: c.attendLeJoueur, ligne: L.Histoire.ligneObjectif() };
    j.x = mien.x + 10; j.y = mien.y; L.Entites.indexer();
    L.Vehicules.monter(j, mien); L.Entites.indexer();
    const lignes = [];
    SUITE
    return Object.assign({ dSortie: dSortie, aPied: aPied, etape: etape(L), fait: !!B.partie.missionsFaites.f06,
                           argent: argent.map(function (a) { return a.montant; }),
                           lignes: lignes.filter(function (l, k) { return l && lignes.indexOf(l) === k; }) }, fin);
}"""

#: Suivre à `ECART` pixels derrière lui, au pixel (le char collé à son pare-choc
#: arrière, chaque image), jusqu'à ce que l'objectif avance ou que ça rate.
DERRIERE = """
    let i = 0;
    for (; i < 12000 && B.partie.mission && B.partie.mission.etape === 0; i++) {
      if (!c.attendLeJoueur) {
        mien.x = c.x - Math.cos(c.angle) * ECART; mien.y = c.y - Math.sin(c.angle) * ECART;
        mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
      }
      o.frame(1); fermerTout();
      if (i % 20 === 0) lignes.push(L.Histoire.ligneObjectif());
    }
    const poste = L.Histoire.lieu('poste');
    const fin = { images: i, etapeFilee: etape(L), dPoste: Math.round(Math.hypot(poste.x - c.x, poste.y - c.y)) };
    finir(L, o);
    fin.libre = c.mission === null && B.entites.indexOf(c) >= 0;
"""

#: Rester garé : il démarre, s'éloigne, et on le perd. ⚠️ Garé à côté de sa voie, devant
#: lui : il passe à notre hauteur en partant — c'est ce frôlement que le rétroviseur excuse.
GARE = """
    const hx = Math.cos(c.angle), hy = Math.sin(c.angle);
    mien.x = c.x + hx * 40 - hy * 22; mien.y = c.y + hy * 40 + hx * 22; j.x = mien.x; j.y = mien.y;
    L.Entites.indexer();
    let i = 0;
    for (; i < 3000 && B.partie.mission; i++) {
      o.frame(1); fermerTout();
      if (i % 20 === 0 && B.partie.mission) lignes.push(L.Histoire.ligneObjectif());
    }
    const fin = { images: i };
"""


def test_f06_on_sort_du_casse_croute_et_on_le_file_jusqu_au_poste(banc):
    """⚠️ Martin, 22 sept. 2026 : « mission deuxième service impossible à faire, on se fait voir
    tout de suite en sortant de la cantine ». Rouge avant : `suivre` posait le fuyard de m50 sur
    la tuile de rue la plus proche de la porte du casse-croûte — à 44 px, sous `proche` (48) —,
    et la mission ratait à la première image dehors. Et rien ne la faisait jamais avancer :
    `suivre` n'avait pas de `lieu`.

    Ici on la joue comme lui : garé devant, Bouchard dedans, la porte, son char. Le stool attend
    qu'on soit au volant, roule au poste ; à six tuiles derrière lui, il y arrive, on paie, la
    mission est faite — et son char repart dans le trafic, pas escamoté sous nos yeux."""
    r = banc(F06.replace("SUITE", DERRIERE.replace("ECART", "96")))
    assert r["dSortie"] >= 5 * 16, "il naît à cinq tuiles au moins de la porte : %s" % r["dSortie"]
    assert r["aPied"]["etape"] == 0 and r["aPied"]["attend"] is True, "à pied, il attend : %s" % r["aPied"]
    assert r["aPied"]["ligne"].endswith("PRENDS UN CHAR"), r["aPied"]
    assert r["etapeFilee"] == 1 and r["dPoste"] < 8 * 16, "filé jusqu'au poste, l'objectif avance : %s" % r
    assert r["fait"] is True and 300 in r["argent"], "200 $ payés, 300 $ de prime : %s" % r
    assert r["libre"], "son char repart dans le trafic"


def test_f06_trop_pres_il_te_voit_trop_loin_on_le_perd(banc):
    """`suivre` se juge avec une MARGE, et le dit : collé à son pare-choc, « TROP PRÈS ! » puis
    raté (une seconde et demie de méfiance) ; resté garé, « TU LE PERDS ! N S » puis raté
    (cinq secondes, comme le tracé des courses). ⚠️ Garé, il démarre et passe à notre hauteur :
    ce frôlement ne le rend pas méfiant — seul compte ce qu'il voit dans son rétroviseur."""
    pres = banc(F06.replace("SUITE", DERRIERE.replace("ECART", "30")))
    assert pres["fait"] is False and pres["etape"] is None, "collé : raté %s" % pres
    assert pres["images"] < 200, "raté vite, pas au bout de la route : %s" % pres["images"]
    assert any(ligne.endswith("TROP PRÈS !") for ligne in pres["lignes"]), pres["lignes"]
    loin = banc(F06.replace("SUITE", GARE))
    assert loin["fait"] is False and loin["etape"] is None, "garé : raté %s" % loin
    # Il nous voit un instant en passant (« TROP PRÈS ! » peut clignoter), mais c'est de
    # l'avoir PERDU que ça rate, pas de méfiance.
    assert any("TU LE PERDS !" in ligne for ligne in loin["lignes"]), "garé, raté par méfiance : %s" % loin["lignes"]


def test_h02_le_commis_roule_jusqu_au_depanneur(banc):
    """h02 file comme f06 (`suivre`, même patron), mais dehors : Ginette se tient devant
    l'hôpital. Le commis naît à bonne distance, attend qu'on soit au volant, et c'est SON
    arrivée au dépanneur (`lieu`) qui fait passer au vol des pilules."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'h01']);
        const g = L.Histoire.donneur('ginette');
        j.x = g.x - 16; j.y = g.y; L.Entites.indexer();
        commencer(L, o, 'h02');
        o.frame(1); fermer(L);
        const c = B.mission.suivi;
        const dNaissance = Math.round(Math.hypot(c.x - j.x, c.y - j.y));
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const arret = L.Histoire.tuileDeRue(j.x, j.y, 10);
        const mien = L.Vehicules.creer('auto', arret.x, arret.y, CAP[arret.sens], { etat: 'stationne' });
        j.x = mien.x + 10; j.y = mien.y; L.Entites.indexer();
        L.Vehicules.monter(j, mien); L.Entites.indexer();
        let i = 0;
        for (; i < 12000 && B.partie.mission && B.partie.mission.etape === 0; i++) {
            if (!c.attendLeJoueur) {
                mien.x = c.x - Math.cos(c.angle) * 96; mien.y = c.y - Math.sin(c.angle) * 96;
                mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
            }
            o.frame(1); fermer(L);
        }
        const dep = L.Histoire.lieu('depanneur');
        return { dNaissance: dNaissance, images: i, etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                 dDepanneur: Math.round(Math.hypot(dep.x - c.x, dep.y - c.y)) };
    }""")
    assert r["dNaissance"] >= 5 * 16, r
    assert r["etape"] == 1 and r["ligne"].startswith("REPRENDS"), "arrivé au dépanneur, on passe au vol : %s" % r
    assert r["dDepanneur"] < 8 * 16, r


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
