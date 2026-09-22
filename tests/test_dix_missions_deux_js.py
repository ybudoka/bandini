"""Les juges de banc des mécaniques neuves de la deuxième tranche de dix missions
(22 sept. 2026) — sur le modèle de `test_dix_missions_js.py` : `sans_etoile` (déclarée
depuis le premier commit de M16, jamais jouée par une mission avant `q04`) et le nouveau
résolveur de lieu `foire` (`histoire.js::lieuFoire`/`poserDonneurFoire`), qui pose le
Bonimenteur vivant à l'arche — pas `point:` — et prouve qu'un donneur `foire` héle,
répond au GPS et se retrouve par `retourner`. Les sept autres missions du lot ne
réutilisent que des types déjà prouvés (v1, ou `suivre`/`pickpocket`/`proteger` de la
première tranche) ; `scripts/verifier_missions.py --detail` les couvre statiquement.
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


def test_p13_le_bonimenteur_existe_pickpocket_puis_retourner(banc):
    """La foire devient un vrai lieu de mission (22 sept. 2026) : le Bonimenteur est posé
    `ou: "foire"`, vivant à l'arche — contrairement à un donneur `point:` (Bouchard,
    Lachance), il est hélable, le GPS le trouve, et `retourner` fonctionne vraiment.
    `pickpocket` reprend le patron déjà prouvé de f07."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        const argent = paiements(L);
        // Posé dès le début de partie par `poserDonneurFoire` — avant même d'avoir la mission.
        const avantMission = L.Histoire.donneur('bonimenteur');
        commencer(L, o, 'p13');
        o.frame(1); fermer(L);   // le « pendant » de l'objectif 0 ouvre une boîte
        const victime = B.mission.entites.find(function (e) { return e.pickpocket === true; });
        victime.angle = 0;
        j.x = victime.x - 12; j.y = victime.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        const vole = L.Combat.pickpocket(j);
        o.frame(2);
        const apresVol = etape(L);
        const bon = L.Histoire.donneur('bonimenteur');
        j.x = bon.x - 16; j.y = bon.y; L.Entites.indexer();
        finir(L, o);
        return { existeAvant: !!avantMission, vole: vole, apresVol: apresVol,
                 bonTrouve: !!bon, fait: !!B.partie.missionsFaites.p13,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["existeAvant"] is True, "le Bonimenteur est posé à l'arche dès le début de partie"
    assert r["vole"] is True, "par-derrière, à portée : le vol réussit"
    assert r["apresVol"] == 1, "poches vides : l'objectif avance"
    assert r["bonTrouve"] is True, "vivant en ville : `Histoire.donneur` le retrouve toujours"
    assert r["fait"] is True and 200 in r["argent"], (
        "`retourner` referme la mission — impossible avec un donneur `point:` (voir f06/h01)")


def test_p14_proteger_le_bonimenteur_jusqu_au_poste(banc):
    """`proteger` une deuxième fois (le Bonimenteur, posé `ou: "foire"`, monte avec le
    joueur) : arrivée au poste, l'objectif avance ; les Skateux tendent une embuscade
    près de lui — même patron que f09."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'p13']);
        const argent = paiements(L);
        commencer(L, o, 'p14');
        const protege = B.mission.protege;
        const avant = { etape: etape(L), protege: !!protege, vivant: protege && protege.vivant };
        const poste = L.Histoire.lieu('poste');
        j.x = poste.x; j.y = poste.y; protege.x = poste.x; protege.y = poste.y; L.Entites.indexer();
        o.frame(2); fermer(L);   // l'arrivée ouvre le « pendant » de l'objectif 1 (tuer)
        const arrive = etape(L), ligne = L.Histoire.ligneObjectif();
        const cibles = B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; });
        cibles.forEach(function (e) { L.Entites.assommer(e); });
        finir(L, o);
        return { avant: avant, arrive: arrive, ligne: ligne, fait: !!B.partie.missionsFaites.p14,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["avant"] == {"etape": 0, "protege": True, "vivant": True}
    assert r["arrive"] == 1 and r["ligne"].startswith("REPOUSSE"), "arrivé au poste, vivant : l'objectif avance"
    assert r["fait"] is True and 350 in r["argent"]


def test_q04_sans_etoile_echoue_vu_reussit_discret(banc):
    """`sans_etoile` (M16, déclarée depuis le premier commit, jamais jouée par une
    mission avant celle-ci) : `majObjectif` échoue en `etoile` dès que
    `B.recherche.etoiles > 0`, tant que l'objectif la porte — posée ici sur `monter` ET
    `livrer`."""
    vu = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'q02']);
        commencer(L, o, 'q04');
        B.recherche.etoiles = 1;
        o.frame(1);
        return { rate: !B.partie.mission };
    }""")
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'q02']);
        const argent = paiements(L);
        commencer(L, o, 'q04');
        const v = B.mission.vehicule;
        j.x = v.x + 20; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer();
        o.frame(2); fermer(L);   // le « pendant » de l'objectif 1 (livrer) ouvre une boîte
        const etapeMonte = etape(L);
        const l = L.Histoire.lieu('bar');
        v.x = l.x; v.y = l.y; v.vitesse = 0; j.x = l.x; j.y = l.y; L.Entites.indexer();
        finir(L, o);
        return { etapeMonte: etapeMonte, fait: !!B.partie.missionsFaites.q04,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert vu["rate"] is True, "vu, étoile > 0, `sans_etoile` sur l'objectif en cours : échec immédiat"
    assert r["etapeMonte"] == 1
    assert r["fait"] is True and 400 in r["argent"], "discret de bout en bout : la mission se rend"
