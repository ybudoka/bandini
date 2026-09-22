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


def test_f04_acheter_un_couteau_chasser_les_cravates_puis_les_trois_caches(banc):
    """`acheter` (M16) : un article ARME (`Combat.ramasserArme`) remplit `B.partie.armes`,
    ce que `majObjectif` regarde — une bouchée (bière, café) ne laisse rien dans le sac, et
    n'aurait jamais fait avancer l'objectif.

    ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : la fin disait « trois paquets,
    retrouvés » sans qu'on en ramasse un. On les cherche maintenant aux trois coins de la ville,
    au volant : derrière l'hôtel (sud-ouest), au pied du phare (est), puis le troisième, qu'un
    Cravate emporte en moto — rattrapé, cogné, il lâche la caisse — et on revient au terminus."""
    r = banc("function (L, o) {" + OUTILS + ROUTE + """
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
        o.frame(2); fermer(L);
        const t = { apresCravates: etape(L), ligneHotel: L.Histoire.ligneObjectif() };
        // Les trois caches, au volant.
        const v = unChar(L, j.x, j.y); auVolant(L, v);
        const hotel = L.Histoire.lieu('hotel'), phare = L.Histoire.lieu('phare');
        t.versHotel = rouler(L, o, v, hotel.x, hotel.y, 3, function () { fermer(L); }, function () { return etape(L) !== 2; });
        t.apresHotel = etape(L);
        t.versPhare = rouler(L, o, v, phare.x, phare.y, 3, function () { fermer(L); }, function () { return etape(L) !== 3; });
        for (let k = 0; k < 3; k++) { o.frame(1); fermer(L); }
        t.apresPhare = etape(L);
        const f = B.mission.fuyard;
        t.fuyard = f ? { slug: f.slug, dPhare: Math.round(Math.hypot(f.x - phare.x, f.y - phare.y)) } : null;
        t.chasse = rattraper(L, o, v, function () { fermer(L); });
        t.caisse = laCaisse(L, o, function () { fermer(L); });
        t.apresCaisse = etape(L);
        auVolant(L, v);
        const mo2 = L.Histoire.donneur('mo');
        t.retour = rouler(L, o, v, mo2.x, mo2.y, 3, function () { fermer(L); });
        L.Vehicules.descendre(j, true);
        const mo3 = L.Histoire.donneur('mo');
        j.x = mo3.x - 16; j.y = mo3.y; L.Entites.indexer();
        finir(L, o);
        return Object.assign(t, { avant: avant, apresBouchee: apresBouchee, apresArme: apresArme, ligne: ligne,
                 fait: !!B.partie.missionsFaites.f04, argent: argent.map(function (a) { return a.montant; }) });
    }""")
    assert r["avant"] == 0
    assert r["apresBouchee"] == 0, "une bouchée (B.partie.objets) ne fait PAS avancer `acheter`"
    assert r["apresArme"] == 1 and r["ligne"].startswith("CHASSE"), "un article `arme` avance l'objectif"
    assert r["apresCravates"] == 2 and r["ligneHotel"].startswith("LE PREMIER PAQUET"), r
    assert r["apresHotel"] == 3 and r["versHotel"] > 15 * 60, "l'hôtel, au sud-ouest : %s" % r
    assert r["apresPhare"] == 4 and r["versPhare"] > 30 * 60, "le phare, à l'autre bout : %s" % r
    assert r["fuyard"] and r["fuyard"]["slug"] == "moto" and r["fuyard"]["dPhare"] < 16 * 16, (
        "le troisième file en moto, du phare : %s" % r["fuyard"])
    assert r["chasse"]["tombe"] and r["caisse"] == {"porteur": True, "caisse": True}, r
    assert r["apresCaisse"] == 5, "la caisse ramassée : on retourne voir Mo %s" % r
    assert r["retour"] > 20 * 60, "le terminus est loin du phare : %s images" % r["retour"]
    assert r["fait"] is True and r["argent"] == [150]


def test_f05_boulots_autobus_compte_jusqu_a_quatre_puis_la_run_du_phare(banc):
    """`boulots` (M16) généralise `courses` : `sorte` nomme un compteur de
    `economie.BOULOTS`/`SORTES` — l'autobus n'en avait pas avant cette tranche. Un cycle
    complet au klaxon (ramasse, route, livraison) prouve le branchement ; les trois
    suivants ne rejouent que le compteur, comme `courses` le fait déjà pour le taxi.

    ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : après les quatre arrêts, la
    dernière run va au phare de La Pointe, à l'heure (quatre minutes : l'autobus y roule en
    une), on y attend Ovila vingt secondes, puis on ramène l'autobus au terminus."""
    r = banc("function (L, o) {" + OUTILS + ROUTE + """
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
        o.frame(2); fermer(L);
        const etapeBoulots = etape(L), ligne = L.Histoire.ligneObjectif();
        // La run du phare, à la vitesse d'un autobus (2,4 px par image, sous ses 2,6).
        const phare = L.Histoire.lieu('phare');
        const run = rouler(L, o, v, phare.x, phare.y, 2.4, function () { fermer(L); }, function () { return etape(L) !== 2; });
        const apresRun = etape(L), ligneAttente = L.Histoire.ligneObjectif();
        let attente = 0;
        for (; attente < 3000 && etape(L) === 3; attente++) { v.vie = v.vieMax; o.frame(1); fermer(L); }
        const apresAttente = etape(L);
        const l = L.Histoire.lieuDeLivraison('terminus');
        const retour = rouler(L, o, v, l.x, l.y, 2.4, function () { fermer(L); }, function () { return etape(L) !== 4; });
        v.vitesse = 0;
        finir(L, o);
        return { etapeMonte: etapeMonte, pris: pris, avantCycle: avantCycle, apresCycle: apresCycle,
                 etapeBoulots: etapeBoulots, ligne: ligne, run: run, apresRun: apresRun, ligneAttente: ligneAttente,
                 attente: attente, apresAttente: apresAttente, retour: retour,
                 fait: !!B.partie.missionsFaites.f05, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["etapeMonte"] == 1, "monté dans l'autobus : le boulot suit"
    assert r["pris"] is True, "le klaxon prend le contrat — `SORTES.autobus` existe"
    assert r["avantCycle"] == 0 and r["apresCycle"] == 1, "un cycle complet compte pour un arrêt"
    assert r["etapeBoulots"] == 2 and r["ligne"].startswith("LA DERNIÈRE RUN"), r
    assert r["apresRun"] == 3 and 30 * 60 < r["run"] < 240 * 60, "le phare, loin mais à l'heure : %s" % r
    assert r["ligneAttente"].startswith("ATTENDS OVILA"), r
    assert r["apresAttente"] == 4 and 20 * 60 <= r["attente"] <= 20 * 60 + 5, "vingt secondes pour Ovila : %s" % r
    assert r["retour"] > 30 * 60, "le terminus est à l'autre bout : %s images" % r["retour"]
    assert r["fait"] is True and r["argent"] and r["argent"][0] in (200, 300), r


def test_f05_la_run_du_phare_se_rate_a_quatre_minutes(banc):
    """`chrono_s` sur la run du phare : l'autobus qui ne bouge plus rate la mission à 240 s,
    pas avant — c'est le chrono, pas un char brisé (on le garde entier)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        commencer(L, o, 'f05');
        const v = B.mission.vehicule;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        o.frame(2); fermer(L);
        B.partie.boulots.autobus = 4;
        o.frame(2); fermer(L);
        const run = etape(L);
        let k = 0;
        for (; k < 20000 && B.partie.mission; k++) { v.vie = v.vieMax; o.frame(1); fermer(L); }
        return { run: run, images: k, rate: !B.partie.mission && !B.partie.missionsFaites.f05 };
    }""")
    assert r["run"] == 2 and r["rate"], r
    assert 240 * 60 - 5 <= r["images"] <= 240 * 60 + 5, "raté au chrono, à quatre minutes : %s" % r


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
    const vus = {};
    let i = 0;
    for (; i < 12000 && B.partie.mission && B.partie.mission.etape === 0; i++) {
      if (!c.attendLeJoueur) {
        mien.x = c.x - Math.cos(c.angle) * ECART; mien.y = c.y - Math.sin(c.angle) * ECART;
        mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
      }
      o.frame(1); fermerTout();
      if (i % 20 === 0) lignes.push(L.Histoire.ligneObjectif());
      ['garage', 'terminus'].forEach(function (n) {
        const l = L.Histoire.lieu(n);
        vus[n] = Math.min(vus[n] || 1e9, Math.round(Math.hypot(l.x - c.x, l.y - c.y)));
      });
    }
    const poste = L.Histoire.lieu('poste');
    const fin = { images: i, vus: vus, etapeFilee: etape(L), dPoste: Math.round(Math.hypot(poste.x - c.x, poste.y - c.y)) };
"""

#: La mission finie ou ratée : il repart dans le trafic, pas escamoté sous nos yeux.
LACHER = """
    finir(L, o);
    fin.libre = c.mission === null && B.entites.indexOf(c) >= 0;
"""

#: Ce qui vient APRÈS la filature (Martin, 22 sept. 2026 : « plus long ») : on paie, on va
#: démolir l'autre char du stool derrière l'hôtel (on descend, on tire dessus de trois tuiles),
#: et on sème la police dans l'hôtel même.
APRES_F06 = """
    for (let k = 0; k < 5; k++) { o.frame(1); fermerTout(); }
    fin.apresPaie = { etape: etape(L), argent: B.partie.argent };
    const autre = B.mission && B.mission.chars ? B.mission.chars[2] : null;
    const hotel = L.Histoire.lieu('hotel');
    fin.autre = autre ? { slug: autre.slug, etat: autre.etat, dHotel: Math.round(Math.hypot(autre.x - hotel.x, autre.y - hotel.y)) } : null;
    fin.versHotel = rouler(L, o, mien, autre.x, autre.y, 3, fermerTout, function () { return Math.hypot(mien.x - autre.x, mien.y - autre.y) < 110; });
    L.Vehicules.descendre(j, true);
    const d = Math.hypot(autre.x - j.x, autre.y - j.y) || 1;
    j.x = autre.x + (j.x - autre.x) / d * 56; j.y = autre.y + (j.y - autre.y) / d * 56; L.Entites.indexer();
    let coups = 0;
    for (; coups < 40 && autre.etat !== 'epave'; coups++) { L.Vehicules.endommager(autre, 30, j); for (let k = 0; k < 20; k++) { o.frame(1); fermerTout(); } }
    for (let k = 0; k < 5; k++) { o.frame(1); fermerTout(); }
    fin.demoli = { coups: coups, etape: etape(L), etoiles: B.recherche.etoiles };
    fin.cache = seCacher(L, o, fermerTout);
""" + LACHER

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


#: Rouler, rattraper, se cacher — comme un joueur, au banc (22 sept. 2026, « des missions plus
#: longues ») : les trajets suivent `Monde.cheminRoute` à trois pixels par image (la vitesse d'une
#: berline en ville), ce qui mesure aussi ce que dure l'étape ; le fuyard se rattrape en collant à
#: son pare-choc (et en le cognant, comme on le cogne au volant) ; la police se sème DEDANS, porte
#: poussée, le temps que les étoiles tombent (`Police.decroitre`).
ROUTE = """
  function unChar(L, x, y) {
    const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
    const a = L.Histoire.tuileDeRue(x, y, 10);
    return L.Vehicules.creer('auto', a.x, a.y, CAP[a.sens], { etat: 'stationne' });
  }
  function auVolant(L, v) {
    const j = L.B.joueur;
    if (j.dansVehicule) L.Vehicules.descendre(j, true);
    j.x = v.x + 10; j.y = v.y; L.Entites.indexer();
    L.Vehicules.monter(j, v); L.Entites.indexer();
  }
  function versPoint(L, o, v, x, y, pas, apres, stop) {
    let n = 0;
    while (n < 20000) {
      const d = Math.hypot(x - v.x, y - v.y);
      if (d <= pas || (stop && stop())) break;
      v.angle = Math.atan2(y - v.y, x - v.x);
      v.x += (x - v.x) / d * pas; v.y += (y - v.y) / d * pas; v.vitesse = 0; v.vx = 0; v.vy = 0;
      if (L.B.joueur.dansVehicule === v) { L.B.joueur.x = v.x; L.B.joueur.y = v.y; }
      o.frame(1); if (apres) apres(); n++;
    }
    return n;
  }
  function rouler(L, o, v, x, y, pas, apres, stop) {
    const ch = L.Monde.cheminRoute(v.x, v.y, x, y) || [];
    let n = 0;
    for (let k = 0; k < ch.length && !(stop && stop()); k++) n += versPoint(L, o, v, ch[k].x, ch[k].y, pas, apres, stop);
    if (!(stop && stop())) n += versPoint(L, o, v, x, y, pas, apres, stop);
    return n;
  }
  function rattraper(L, o, v, apres) {
    const B = L.B, j = B.joueur;
    let n = 0, coups = 0;
    for (; n < 6000 && B.partie.mission && !B.mission.fuyardTombe; n++) {
      const f = B.mission.fuyard;
      v.x = f.x - Math.cos(f.angle) * 30; v.y = f.y - Math.sin(f.angle) * 30; v.angle = f.angle;
      v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y;
      if (n > 0 && n % 120 === 0) { L.Vehicules.endommager(f, f.vieMax * 0.2, j); coups++; }
      o.frame(1); if (apres) apres();
    }
    return { images: n, coups: coups, tombe: !!(B.mission && B.mission.fuyardTombe) };
  }
  function laCaisse(L, o, apres) {
    const B = L.B, j = B.joueur;
    const e = B.mission.entites.find(function (q) { return q.porteLaCaisse; });
    if (!e) return { porteur: false, caisse: false };
    if (j.dansVehicule) L.Vehicules.descendre(j, true);
    j.x = e.x - 14; j.y = e.y; L.Entites.indexer();
    L.Entites.assommer(e); o.frame(2); if (apres) apres();
    const c = B.mission.entites.find(function (q) { return q.objet === 'caisse'; });
    if (!c) return { porteur: true, caisse: false };
    j.x = c.x; j.y = c.y; L.Entites.indexer();
    for (let k = 0; k < 10; k++) { o.frame(1); if (apres) apres(); }
    return { porteur: true, caisse: true };
  }
  function seCacher(L, o, apres) {
    const B = L.B, j = B.joueur;
    if (j.dansVehicule) L.Vehicules.descendre(j, true);
    const pieces = L.Monde.carte.def.interieurs || {};
    const porte = (L.Monde.carte.def.portes || []).filter(function (q) { return q.interieur && pieces[q.interieur]; })
      .sort(function (a, b) { return Math.hypot(a.x * 16 - j.x, a.y * 16 - j.y) - Math.hypot(b.x * 16 - j.x, b.y * 16 - j.y); })[0];
    const loin = Math.round(Math.hypot(porte.x * 16 + 8 - j.x, (porte.y + 1) * 16 - j.y));
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    const entre = !!B.interieur;
    let n = 0;
    for (; n < 9000 && B.recherche.etoiles > 0; n++) { o.frame(1); if (apres) apres(); }
    L.Jeu.sortir(); o.fondu();
    for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
    for (let k = 0; k < 10; k++) { o.frame(1); if (apres) apres(); }
    return { images: n, porte: porte.lieu, loin: loin, entre: entre, dehors: !B.interieur };
  }
"""


def test_f06_on_sort_du_casse_croute_et_on_le_file_jusqu_au_poste(banc):
    """⚠️ Martin, 22 sept. 2026 : « mission deuxième service impossible à faire, on se fait voir
    tout de suite en sortant de la cantine ». Rouge avant : `suivre` posait le fuyard de m50 sur
    la tuile de rue la plus proche de la porte du casse-croûte — à 44 px, sous `proche` (48) —,
    et la mission ratait à la première image dehors. Et rien ne la faisait jamais avancer :
    `suivre` n'avait pas de `lieu`.

    Ici on la joue comme lui : garé devant, Bouchard dedans, la porte, son char. Le stool attend
    qu'on soit au volant, roule au poste ; à six tuiles derrière lui, il y arrive, on paie, la
    mission est faite — et son char repart dans le trafic, pas escamoté sous nos yeux.

    ⚠️ Martin, ensuite : « je veux que ce soit plus long ». Le poste est à deux coins de rue
    (15 à 20 s) : le stool fait un détour (`par`) — le garage, puis le terminus. Mesuré sur
    six graines : 57 à 74 s de filature.

    ⚠️ Et encore plus long (« des missions plus longues », le même jour) : APRÈS la filature, pas
    un second détour — on paie, puis on démolit l'autre char du stool derrière l'hôtel Bandini
    (sa copie de la déposition y dort), et on sème la police que le boum a réveillée."""
    r = banc(F06.replace("SUITE", DERRIERE.replace("ECART", "96") + ROUTE + APRES_F06))
    assert r["dSortie"] >= 5 * 16, "il naît à cinq tuiles au moins de la porte : %s" % r["dSortie"]
    assert r["aPied"]["etape"] == 0 and r["aPied"]["attend"] is True, "à pied, il attend : %s" % r["aPied"]
    assert r["aPied"]["ligne"].endswith("PRENDS UN CHAR"), r["aPied"]
    assert r["etapeFilee"] == 1 and r["dPoste"] < 8 * 16, "filé jusqu'au poste, l'objectif avance : %s" % r
    assert r["vus"]["garage"] < 5 * 16 and r["vus"]["terminus"] < 5 * 16, "le détour, étape par étape : %s" % r["vus"]
    assert r["images"] > 40 * 60, "une vraie filature, plus deux coins de rue : %s images" % r["images"]
    # APRÈS la filature : on paie, puis l'autre char du stool, puis la police.
    assert r["apresPaie"] == {"etape": 2, "argent": 300}, "payé au poste : 500 − 200 $ %s" % r["apresPaie"]
    assert r["autre"] and r["autre"]["slug"] == "auto" and r["autre"]["etat"] == "stationne", r["autre"]
    assert r["autre"]["dHotel"] < 10 * 16, "son autre char dort derrière l'hôtel : %s" % r["autre"]
    assert r["versHotel"] > 15 * 60, "l'hôtel est à l'autre bout de la ville : %s images" % r["versHotel"]
    assert r["demoli"]["etape"] == 3 and r["demoli"]["etoiles"] >= 2, "démoli, la police arrive : %s" % r["demoli"]
    assert r["cache"]["entre"] and r["cache"]["dehors"] and r["cache"]["loin"] < 8 * 16, r["cache"]
    assert r["cache"]["images"] > 20 * 60, "deux étoiles se sèment, elles ne s'effacent pas : %s" % r["cache"]
    assert r["fait"] is True and 300 in r["argent"], "200 $ payés, 300 $ de prime : %s" % r
    assert r["libre"], "son char repart dans le trafic"


def test_f06_trop_pres_il_te_voit_trop_loin_on_le_perd(banc):
    """`suivre` se juge avec une MARGE, et le dit : collé à son pare-choc, « TROP PRÈS ! » puis
    raté (une seconde et demie de méfiance) ; resté garé, « TU LE PERDS ! N S » puis raté
    (cinq secondes, comme le tracé des courses). ⚠️ Garé, il démarre et passe à notre hauteur :
    ce frôlement ne le rend pas méfiant — seul compte ce qu'il voit dans son rétroviseur."""
    pres = banc(F06.replace("SUITE", DERRIERE.replace("ECART", "30") + LACHER))
    assert pres["fait"] is False and pres["etape"] is None, "collé : raté %s" % pres
    assert pres["images"] < 200, "raté vite, pas au bout de la route : %s" % pres["images"]
    assert any(ligne.endswith("TROP PRÈS !") for ligne in pres["lignes"]), pres["lignes"]
    loin = banc(F06.replace("SUITE", GARE))
    assert loin["fait"] is False and loin["etape"] is None, "garé : raté %s" % loin
    # Il nous voit un instant en passant (« TROP PRÈS ! » peut clignoter), mais c'est de
    # l'avoir PERDU que ça rate, pas de méfiance.
    assert any("TU LE PERDS !" in ligne for ligne in loin["lignes"]), "garé, raté par méfiance : %s" % loin["lignes"]


def test_h02_on_file_le_commis_ti_paul_jase_on_seme_et_on_rapporte(banc):
    """h02 file comme f06 (`suivre`, même patron), mais dehors : Ginette se tient devant
    l'hôpital. Le commis naît à bonne distance, attend qu'on soit au volant, traverse la
    ville, et c'est SON arrivée au dépanneur (`lieu`) qui fait passer à la suite. ⚠️ Plus longue (22 sept. 2026) : on fait jaser Ti-Paul au
    bouton, on vide les poches du commis, il crie au voleur (une étoile, semée en se
    cachant pour vrai), et on rapporte les pilules à Ginette, à l'autre bout de la ville."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'h01']);
        const argent = paiements(L);
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
            o.frame(1); ecouter(L);
        }
        const dep = L.Histoire.lieu('depanneur');
        const file = { images: i, etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                       dDepanneur: Math.round(Math.hypot(dep.x - c.x, dep.y - c.y)) };
        jouer(L, o);
        const accueil = serrer(L, o, 'tipaul');
        const vol = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        const victime = B.mission.entites.find(function (e) { return e.pickpocket === true; });
        victime.angle = 0;
        j.x = victime.x - 12; j.y = victime.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        const vole = L.Combat.pickpocket(j);
        jouer(L, o);
        const semer = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), loin: loinDe(L, 'depanneur', 'hopital') };
        const g2 = L.Histoire.donneur('ginette');
        j.x = g2.x - 16; j.y = g2.y; L.Entites.indexer();
        finir(L, o);
        return { dNaissance: dNaissance, file: file, accueil: accueil, vol: vol, vole: vole, semer: semer, cache: cache,
                 retour: retour, dites: dites, fait: !!B.partie.missionsFaites.h02,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dNaissance"] >= 5 * 16, r
    f = r["file"]
    assert f["etape"] == 1 and f["ligne"].startswith("FAIS JASER TI-PAUL"), f"arrivé au dépanneur, on va voir Ti-Paul : {f}"
    assert f["dDepanneur"] < 8 * 16, f"il s'est rangé au dépanneur : {f}"
    assert f["images"] > 60 * 60, f"une vraie filature, d'un bout à l'autre de la ville : {f['images']} images"
    assert r["accueil"] == "accueil", "au bouton, Ti-Paul jase (sa poignée de main)"
    assert r["vol"]["etape"] == 2 and r["vol"]["ligne"].startswith("REPRENDS"), r["vol"]
    assert r["vole"] is True
    assert r["semer"]["etape"] == 3 and r["semer"]["ligne"].startswith("IL CRIE AU VOLEUR") and r["semer"]["etoiles"] >= 1, r["semer"]
    assert r["cache"]["dedans"] and r["cache"]["apres"] == 0, f"semée en se cachant : {r['cache']}"
    assert r["retour"]["etape"] == 4 and r["retour"]["loin"] > 200, f"les pilules à rapporter, loin : {r['retour']}"
    for dite in ("pendant:ginette:1", "accueil:tipaul:1", "pendant:ginette:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and 250 in r["argent"], r

#: Les missions allongées (22 sept. 2026, Martin : « des missions plus longues ») : ce que
#: leurs juges partagent — la nuit, se cacher pour semer, parler au bouton, et les
#: répliques qu'on a entendues (`dites`), pour juger que chaque étape neuve PARLE.
PLUS_LONGUES = """
  const dites = [];
  function ecouter(L) {
    let g = 0;
    while (L.B.cinema && g < 100) {
      const c = L.B.cinema;
      if (c.partie) c.lignes.forEach(function (l) { const k = c.partie + ':' + l.qui + ':' + (l.objectif === undefined ? '' : l.objectif); if (dites.indexOf(k) < 0) dites.push(k); });
      L.Histoire.suivante(); g++;
    }
  }
  // Quelques images, en passant les répliques qui s'ouvrent : un `pendant` part une image
  // APRÈS le changement d'étape, et tant qu'il parle, aucun objectif n'avance.
  function jouer(L, o, n) { for (let k = 0; k < (n || 6); k++) { o.frame(1); ecouter(L); } }
  function laNuit(L, o) {
    let h = L.B.partie.heure;
    for (let k = 0; k < 400 && !L.Monde.estNuit(h); k++) h = (h + 0.005) % 1;
    L.B.partie.heure = h; o.frame(2);
  }
  function aPied(L) { if (L.B.joueur.dansVehicule) L.Vehicules.descendre(L.B.joueur, true); }
  // Serrer la main au BOUTON : à deux pas de lui, ACTION.
  function serrer(L, o, slug) {
    aPied(L);
    const d = L.Histoire.donneur(slug), j = L.B.joueur;
    j.x = d.x - 16; j.y = d.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
    o.frame(1); j.angle = 0; j.face = 'droite'; L.Missions.majInvite(j); o.tape('KeyE', 2);
    const partie = L.B.cinema ? L.B.cinema.partie : null;
    ecouter(L); jouer(L, o);
    return partie;
  }
  // Semer : à pied, dans la pièce la plus proche, jusqu'à zéro étoile — puis ressortir.
  function seCacher(L, o) {
    const B = L.B, j = B.joueur;
    aPied(L);
    const avant = B.recherche.etoiles;
    let p = null, d = 1e12;
    (L.Monde.carte.def.portes || []).forEach(function (q) {
      if (!q.interieur) return;
      const dd = Math.pow(q.x * 16 + 8 - j.x, 2) + Math.pow((q.y + 1) * 16 + 8 - j.y, 2);
      if (dd < d) { d = dd; p = q; }
    });
    j.x = p.x * 16 + 8; j.y = (p.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(p); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    const dedans = !!B.interieur;
    let n = 0;
    for (; n < 9000 && B.recherche.etoiles > 0; n++) o.frame(1);
    L.Jeu.sortir(); o.fondu();
    for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
    jouer(L, o);
    return { avant: avant, dedans: dedans, images: n, porte: p.lieu, apres: B.recherche.etoiles };
  }
  function loinDe(L, a, b) { const p = L.Histoire.lieu(a), q = L.Histoire.lieu(b); return Math.round(Math.hypot(p.x - q.x, p.y - q.y) / 16); }
"""


def test_h01_trois_transports_puis_le_phare_puis_les_cles_a_ginette(banc):
    """h01 jouée de bout en bout, les trois étapes neuves comprises : la nuit tombe à
    l'hôpital, l'ambulance, un vrai transport au klaxon (le blessé, puis l'urgence) et le
    compteur pour les deux autres ; puis l'urgence du phare, à l'autre bout de la ville ;
    le gardien ramené à l'urgence (`livrer` : l'ambulance est encore le char de la
    mission) ; et les clés rendues à Ginette, au bouton — sa poignée de main se dit, et la
    mission se ferme."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        const h = L.Histoire.lieu('hopital');
        j.x = h.x; j.y = h.y + 20; L.Entites.indexer();
        commencer(L, o, 'h01');
        let hh = B.partie.heure;
        for (let k = 0; k < 400 && L.Monde.estNuit(hh); k++) hh = (hh + 0.005) % 1;
        B.partie.heure = hh; o.frame(2);
        const deJour = { etape: etape(L), attend: B.mission.attend };
        laNuit(L, o); ecouter(L);
        const etapeNuit = etape(L);
        const v = B.mission.vehicule;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        jouer(L, o);
        const etapeMonte = etape(L), ambulance = v.slug;
        // Un transport pour vrai : le klaxon, le blessé, l'urgence.
        const b = L.Missions.boulot, pris = b.klaxon(v);
        for (let k = 0; k < 600 && b.etape === 'ramasse'; k++) {
            if (b.client) { v.x = b.client.x; v.y = b.client.y; v.vitesse = 0; }
            o.frame(1); ecouter(L);
        }
        for (let k = 0; k < 600 && b.etape === 'route'; k++) {
            if (b.destination) { v.x = b.destination.x; v.y = b.destination.y; v.vitesse = 0; }
            o.frame(1); ecouter(L);
        }
        const unTransport = (b.faits.ambulance || 0) - B.mission.boulotsDepart;
        b.faits.ambulance = B.mission.boulotsDepart + 3;
        jouer(L, o);
        const etapePhare = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), loin: loinDe(L, 'hopital', 'phare') };
        const ph = L.Histoire.lieu('phare');
        v.x = ph.x; v.y = ph.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
        for (let k = 0; k < 10 && etape(L) === 3; k++) { o.frame(1); ecouter(L); }
        const etapeRetour = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), dans: j.dansVehicule === v };
        const baie = L.Histoire.lieuDeLivraison('hopital');
        v.x = baie.x; v.y = baie.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
        for (let k = 0; k < 10 && etape(L) === 4; k++) { o.frame(1); ecouter(L); }
        const etapeCles = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), aPied: !j.dansVehicule };
        const accueil = serrer(L, o, 'ginette');
        finir(L, o);
        return { deJour: deJour, etapeNuit: etapeNuit, etapeMonte: etapeMonte, ambulance: ambulance, pris: pris,
                 unTransport: unTransport, etapePhare: etapePhare, etapeRetour: etapeRetour, etapeCles: etapeCles,
                 accueil: accueil, dites: dites, fait: !!B.partie.missionsFaites.h01,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["deJour"] == {"etape": 0, "attend": "ATTENDS LA NUIT"}, r["deJour"]
    assert r["etapeNuit"] == 1 and r["ambulance"] == "ambulance" and r["etapeMonte"] == 2, r
    assert r["pris"] is True and r["unTransport"] == 1, f"un vrai transport au klaxon compte : {r}"
    assert r["etapePhare"]["etape"] == 3 and r["etapePhare"]["ligne"].startswith("URGENCE AU PHARE"), r["etapePhare"]
    assert r["etapePhare"]["loin"] > 150, f"le phare, à l'autre bout de la ville : {r['etapePhare']['loin']} tuiles"
    assert r["etapeRetour"]["etape"] == 4 and r["etapeRetour"]["dans"], f"au phare en ambulance : on ramène le gardien : {r}"
    assert r["etapeCles"]["etape"] == 5 and r["etapeCles"]["aPied"], f"livré à l'urgence, on descend : {r['etapeCles']}"
    assert r["accueil"] == "accueil", f"au bouton, Ginette parle (sa poignée de main) : {r}"
    for dite in ("pendant:lachance:3", "pendant:lachance:4", "accueil:ginette:5"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and 300 in r["argent"], r


def test_f07_la_cantine_les_poches_par_derriere_puis_le_complice(banc):
    """`pickpocket` (M16) : `Combat.pickpocket` ne assomme PAS sa victime — elle `fuit`,
    poches vides (`argent = 0`). C'est ce signal que `majObjectif` doit guetter, pas
    `assomme` (un vol par-derrière ne le produit jamais).

    ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : le voleur boit l'argent à la
    cantine des Quais, à l'autre bout de la ville — il n'existe qu'une fois qu'on y est (posé
    près du joueur) —, et, sa clé prise, son complice file en moto avec la caisse : rattrapé,
    cogné, il la lâche. Puis le kiosque."""
    r = banc("function (L, o) {" + OUTILS + ROUTE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'f04']);
        const argent = paiements(L);
        commencer(L, o, 'f07');
        o.frame(1); fermer(L);   // le « pendant » de l'objectif 0 ouvre une boîte
        const t = { depart: etape(L), personneAuKiosque: !B.mission.entites.some(function (e) { return e.pickpocket; }) };
        const th = L.Histoire.donneur('thibodeau');
        const v = unChar(L, th.x, th.y); auVolant(L, v);
        const cantine = L.Histoire.lieu('cantine');
        t.versCantine = rouler(L, o, v, cantine.x, cantine.y, 3, function () { fermer(L); }, function () { return etape(L) !== 0; });
        for (let k = 0; k < 3; k++) { o.frame(1); fermer(L); }
        L.Vehicules.descendre(j, true);
        const victime = B.mission.entites.find(function (e) { return e.pickpocket === true; });
        const avant = { etape: etape(L), argent: victime.argent, vivant: victime.vivant,
                        dCantine: Math.round(Math.hypot(victime.x - cantine.x, victime.y - cantine.y)) };
        // Par-derrière : la victime regarde vers l'est (loin du joueur, à l'ouest), le
        // joueur la regarde — de face pour LUI, de dos pour ELLE. `faceA` lit `e.face`
        // (un nom de direction, `REGARDS`) avant `e.angle` — les deux doivent s'accorder.
        victime.angle = 0; victime.face = 'droite';
        j.x = victime.x - 12; j.y = victime.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        const vole = L.Combat.pickpocket(j);
        o.frame(2); fermer(L);
        const apres = { etape: etape(L), argent: victime.argent, vivant: victime.vivant, etat: victime.etat };
        const f = B.mission.fuyard;
        t.fuyard = f ? { slug: f.slug, dCantine: Math.round(Math.hypot(f.x - cantine.x, f.y - cantine.y)) } : null;
        auVolant(L, v);
        t.chasse = rattraper(L, o, v, function () { fermer(L); });
        t.caisse = laCaisse(L, o, function () { fermer(L); });
        t.apresCaisse = etape(L);
        auVolant(L, v);
        const th2 = L.Histoire.donneur('thibodeau');
        t.retour = rouler(L, o, v, th2.x, th2.y, 3, function () { fermer(L); });
        L.Vehicules.descendre(j, true);
        const th3 = L.Histoire.donneur('thibodeau');
        j.x = th3.x - 16; j.y = th3.y; L.Entites.indexer();
        finir(L, o);
        return Object.assign(t, { avant: avant, vole: vole, apres: apres, fait: !!B.partie.missionsFaites.f07,
                 argent: argent.map(function (a) { return a.montant; }) });
    }""")
    assert r["depart"] == 0 and r["personneAuKiosque"], "le voleur n'est pas au kiosque : il boit à la cantine %s" % r
    assert r["versCantine"] > 20 * 60, "la cantine des Quais, à l'autre bout : %s images" % r["versCantine"]
    assert r["avant"]["etape"] == 1 and r["avant"]["argent"] > 0 and r["avant"]["vivant"] is True
    assert r["avant"]["dCantine"] < 12 * 16, "il boit devant la cantine : %s" % r["avant"]
    assert r["vole"] is True, "par-derrière, à portée : le vol réussit"
    assert r["apres"]["argent"] == 0 and r["apres"]["vivant"] is True and r["apres"]["etat"] != "assomme", (
        "un vol par-derrière laisse la victime vivante et EN FUITE — jamais assommée")
    assert r["apres"]["etape"] == 2, "poches vides : l'objectif avance quand même"
    assert r["fuyard"] and r["fuyard"]["slug"] == "moto" and r["fuyard"]["dCantine"] < 16 * 16, r["fuyard"]
    assert r["chasse"]["tombe"] and r["caisse"] == {"porteur": True, "caisse": True}, r
    assert r["apresCaisse"] == 3, "la caisse rattrapée : on retourne au kiosque %s" % r
    assert r["retour"] > 20 * 60, "le kiosque est loin des Quais : %s images" % r["retour"]
    assert r["fait"] is True and 200 in r["argent"], "200 $ de récompense (en plus des poches volées)"


def test_f09_proteger_marco_jusqu_au_kiosque_filer_le_troisieme_puis_le_garage(banc):
    """`proteger` (M16) : la cible nous suit ; morte, échec `protege_mort` ; arrivée à
    `lieu`, l'objectif avance — sans lui, l'objectif ne se terminait JAMAIS (corrigé cette
    tranche-ci : il ne faisait que garder).

    ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : la fin disait « j'ai vu où le reste
    de l'argent dort » sans qu'on l'ait vu. Après l'embuscade, le troisième Cravate se pousse en
    char : on le file jusqu'à l'hôtel Bandini (l'argent y DORT), Marco monté avec nous, puis on
    le ramène au garage — la fin se dit devant lui, chez lui."""
    r = banc("function (L, o) {" + OUTILS + ROUTE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm50', 'f01', 'f06']);
        const argent = paiements(L);
        commencer(L, o, 'f09');
        const protege = B.mission.protege;
        const avant = { etape: etape(L), protege: !!protege, vivant: protege && protege.vivant };
        const kiosque = L.Histoire.lieu('kiosque');
        j.x = kiosque.x; j.y = kiosque.y; protege.x = kiosque.x; protege.y = kiosque.y; L.Entites.indexer();
        o.frame(2);
        const arrive = etape(L), ligne = L.Histoire.ligneObjectif();
        fermer(L);
        const cibles = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const t = { nCibles: cibles.length };
        cibles.forEach(function (e) { L.Entites.assommer(e); });
        o.frame(2); fermer(L);
        t.apresCravates = etape(L);
        const c = B.mission.suivi;
        t.suivi = c ? { attend: c.attendLeJoueur, d: Math.round(Math.hypot(c.x - j.x, c.y - j.y)) } : null;
        // Un char, Marco monte avec nous (arrêté à côté de lui), puis on file à six tuiles.
        const mien = unChar(L, j.x, j.y);
        protege.x = mien.x + 14; protege.y = mien.y + 14; L.Entites.indexer();
        auVolant(L, mien);
        for (let k = 0; k < 30; k++) { mien.vitesse = 0; o.frame(1); fermer(L); }
        t.marcoMonte = protege.dansVehicule === mien;
        let i = 0;
        for (; i < 12000 && B.partie.mission && etape(L) === 2; i++) {
            if (!c.attendLeJoueur) {
                mien.x = c.x - Math.cos(c.angle) * 96; mien.y = c.y - Math.sin(c.angle) * 96;
                mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
            }
            o.frame(1); fermer(L);
        }
        const hotel = L.Histoire.lieu('hotel');
        t.filature = i; t.apresFilature = etape(L); t.dHotel = Math.round(Math.hypot(hotel.x - c.x, hotel.y - c.y));
        t.marcoFile = protege.dansVehicule === mien;
        const garage = L.Histoire.lieu('garage');
        let marcoArrive = null;
        t.retour = rouler(L, o, mien, garage.x, garage.y, 3, function () { if (B.partie.mission) marcoArrive = protege.dansVehicule === mien; fermer(L); },
                          function () { return etape(L) !== 3; });
        t.marcoArrive = marcoArrive;
        finir(L, o);
        return Object.assign(t, { avant: avant, arrive: arrive, ligne: ligne, fait: !!B.partie.missionsFaites.f09,
                 argent: argent.map(function (a) { return a.montant; }), rentre: !!protege.rentre });
    }""")
    assert r["avant"] == {"etape": 0, "protege": True, "vivant": True}
    assert r["arrive"] == 1 and r["ligne"].startswith("REPOUSSE"), "arrivé au kiosque, vivant : l'objectif avance"
    assert r["nCibles"] == 2 and r["apresCravates"] == 2, r
    assert r["suivi"] and r["suivi"]["attend"] is True and r["suivi"]["d"] >= 5 * 16, "le troisième attend qu'on ait un char : %s" % r
    assert r["marcoMonte"] is True, "Marco monte dans le char arrêté à côté de lui"
    assert r["apresFilature"] == 3 and r["dHotel"] < 8 * 16, "filé jusqu'à l'hôtel : %s" % r
    assert r["filature"] > 40 * 60, "de l'autre bout de la ville : %s images" % r["filature"]
    assert r["marcoFile"] is True and r["marcoArrive"] is True, "Marco reste dans le char jusqu'au garage : %s" % r
    assert r["retour"] > 15 * 60, "l'hôtel est loin du garage : %s images" % r["retour"]
    assert r["fait"] is True and r["argent"] == [250] and r["rentre"], r

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


def test_q03_detruire_le_camion_puis_les_boulonneux_la_police_et_gege(banc):
    """`detruire` (M16) : réutilise `poserLeChar` comme `monter`, mais c'est
    `B.mission.chars[etape]` que `majObjectif` surveille — on ne roule pas dedans, on le
    casse. ⚠️ Plus longue (22 sept. 2026) : les Boulonneux de Prévost ARRIVENT sur le
    joueur devant l'usine (`loin`), le camion en feu amène deux étoiles qu'on sème en se
    cachant pour vrai, et on revient chez Gégé, à la cantine, à l'autre bout de la ville."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        commencer(L, o, 'q03');
        o.frame(1); ecouter(L);   // le « pendant » de l'objectif 0 ouvre une boîte : la fermer avant de jouer
        const camion = B.mission.chars[0];
        const avant = { etape: etape(L), camion: camion ? camion.slug : null, etat: camion ? camion.etat : null };
        j.x = camion.x + 60; j.y = camion.y; L.Entites.indexer();
        camion.etat = 'epave';
        jouer(L, o);
        const apres = etape(L);
        const gars = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        const bagarre = { n: gars.length, groupe: gars.map(function (e) { return e.archetype || e.arch || ''; }),
                          courent: gars.every(function (e) { return e.etat === 'attaque_joueur'; }),
                          pres: Math.max.apply(null, gars.map(function (e) { return Math.round(Math.hypot(e.x - j.x, e.y - j.y) / 16); })) };
        gars.forEach(function (e) { L.Entites.assommer(e); });
        jouer(L, o);
        const semer = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), loin: loinDe(L, 'usine', 'cantine') };
        const gege = L.Histoire.donneur('gege');
        j.x = gege.x - 16; j.y = gege.y; L.Entites.indexer();
        finir(L, o);
        return { avant: avant, apres: apres, bagarre: bagarre, semer: semer, cache: cache, retour: retour, dites: dites,
                 fait: !!B.partie.missionsFaites.q03, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["avant"] == {"etape": 0, "camion": "camion", "etat": "stationne"}, r["avant"]
    assert r["apres"] == 1, "le camion est une épave : `detruire` avance"
    assert r["bagarre"]["n"] == 3 and r["bagarre"]["courent"] and r["bagarre"]["pres"] <= 12, (
        f"trois Boulonneux arrivent sur le joueur, à la course : {r['bagarre']}")
    assert r["semer"]["etape"] == 2 and r["semer"]["ligne"].startswith("LA POLICE") and r["semer"]["etoiles"] >= 2, r["semer"]
    assert r["cache"]["dedans"] and r["cache"]["apres"] == 0 and r["cache"]["images"] > 60, f"semée en se cachant : {r['cache']}"
    assert r["retour"]["etape"] == 3 and r["retour"]["ligne"].startswith("RETOURNE"), r["retour"]
    assert r["retour"]["loin"] > 200, f"la cantine, à l'autre bout de la ville : {r['retour']['loin']} tuiles"
    for dite in ("pendant:gege:1", "pendant:gege:2", "pendant:gege:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300]


def test_e12_le_phare_la_rampe_de_la_pointe_la_police_puis_le_depanneur(banc):
    """`sauter` (M16) : le vol se compte comme le défi *Le Grand Saut* (`vol_px`), tant que
    le véhicule est en l'air (`v.z > 0`) — dans n'importe quelle rampe de la ville, `ou` ne
    servant qu'à pointer le GPS.

    ⚠️ Des missions plus longues (Martin, 22 sept. 2026) : du dépanneur au phare de La Pointe,
    à l'autre bout de la ville (le décor de la vidéo) ; un VRAI saut, à fond sur la rampe au
    pied du phare (`rampe:erables` ne se résolvait pas : aucune rampe aux Érables) ; la police
    qu'il attire se sème dedans ; puis le coupé retourne au dépanneur — c'est le char de l'oncle."""
    r = banc("function (L, o) {" + OUTILS + ROUTE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        commencer(L, o, 'e12');
        const v = B.mission.vehicule, t = { slug: v.slug };
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        o.frame(2); fermer(L);
        t.monte = etape(L);
        const phare = L.Histoire.lieu('phare');
        t.versPhare = rouler(L, o, v, phare.x, phare.y, 3, function () { fermer(L); }, function () { return etape(L) !== 1; });
        for (let k = 0; k < 5; k++) { o.frame(1); fermer(L); }
        t.auPhare = etape(L);
        // La rampe que le GPS montre, et le saut pour vrai : six tuiles d'élan, pied au plancher
        // (`carte.ELAN_RAMPE` en donne sept ; à huit, on est dans le mur d'en arrière).
        const ou = L.Histoire.resoudre('rampe:pointe', { donneur: 'xavier' });
        const r = ou && L.Monde.carte.rampes.find(function (q) { return q.x * 16 + 8 === ou.x && q.y * 16 + 8 === ou.y; });
        t.rampe = r ? { x: r.x, y: r.y, dPhare: Math.round(Math.hypot(ou.x - phare.x, ou.y - phare.y)) } : null;
        rouler(L, o, v, (r.x - r.dx * 6) * 16 + 8, (r.y - r.dy * 6) * 16 + 8, 3, function () { fermer(L); });
        v.x = (r.x - r.dx * 6) * 16 + 8; v.y = (r.y - r.dy * 6) * 16 + 8; v.angle = Math.atan2(r.dy, r.dx);
        v.vitesse = v.def.vitesse_max;
        o.touche('KeyW');
        let zmax = 0, k = 0;
        for (; k < 400 && etape(L) === 2; k++) { o.frame(1); fermer(L); zmax = Math.max(zmax, v.z); }
        o.relacher('KeyW');
        t.saut = { images: k, zmax: Math.round(zmax), vol: B.mission ? Math.round(B.mission.vol) : null, etape: etape(L), etoiles: B.recherche.etoiles };
        for (let q = 0; q < 60; q++) { o.frame(1); fermer(L); }
        t.atterri = { z: v.z, etat: v.etat, vie: v.vie, mission: !!B.partie.mission };
        t.cache = seCacher(L, o, function () { fermer(L); });
        t.apresSemer = etape(L);
        auVolant(L, v);
        const dep = L.Histoire.lieuDeLivraison('depanneur');
        t.versDepanneur = rouler(L, o, v, dep.x, dep.y, 3, function () { fermer(L); }, function () { return etape(L) !== 4; });
        v.vitesse = 0;
        for (let q = 0; q < 30 && etape(L) === 4; q++) { o.frame(1); fermer(L); }
        t.livre = etape(L);
        const xav = L.Histoire.donneur('xavier');
        j.x = xav.x - 16; j.y = xav.y; L.Entites.indexer();
        finir(L, o);
        t.fait = !!B.partie.missionsFaites.e12; t.argent = argent.map(function (a) { return a.montant; });
        return t;
    }""")
    assert r["slug"] == "sport" and r["monte"] == 1
    assert r["auPhare"] == 2 and r["versPhare"] > 30 * 60, "le phare, à l'autre bout de la ville : %s" % r
    assert r["rampe"] and r["rampe"]["dPhare"] < 20 * 16, "`rampe:pointe` se résout, au pied du phare : %s" % r["rampe"]
    assert r["saut"]["etape"] == 3 and r["saut"]["vol"] >= 40 and r["saut"]["zmax"] > 0, "un vrai saut : %s" % r["saut"]
    assert r["saut"]["etoiles"] >= 2, "un coupé qui vole, ça se remarque : %s" % r["saut"]
    assert r["atterri"]["z"] == 0 and r["atterri"]["etat"] != "epave" and r["atterri"]["mission"], (
        "retombé entier, la mission continue : %s" % r["atterri"])
    # La porte la plus proche d'où le coupé retombe : celle du phare, à une quinzaine de tuiles.
    assert r["cache"]["entre"] and r["cache"]["dehors"] and r["cache"]["loin"] < 20 * 16, r["cache"]
    assert r["apresSemer"] == 4 and r["cache"]["images"] > 20 * 60, "semée pour vrai, dedans : %s" % r["cache"]
    assert r["livre"] == 5 and r["versDepanneur"] > 30 * 60, "le coupé ramené au dépanneur : %s" % r
    assert r["fait"] is True and r["argent"] and r["argent"][0] in (200, 300), r
