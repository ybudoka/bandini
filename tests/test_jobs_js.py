"""Un passant qui donne une job (M16, arc T, 1er oct. 2026) — `static/js/jobs.js`, au banc.

- Un passant ORDINAIRE se présente : un archétype de la rue, de son district, à quelques tuiles, qui marche jusqu'à
  toi en te hélant (sa bulle, sa voix de passant). ACTION à côté de lui : son intro, puis la job — sans téléphone.
- Il naît À L'EMPREINTE : ni dé tiré à la ville, ni numéro pris à sa suite ; sa tenue vient de la garde-robe de son
  archétype, à l'empreinte de la demi-journée.
- La cadence : jamais pendant une mission, ni au volant, ni à trois étoiles ; une offre par demi-journée ; une minute et
  demie au moins après la dernière mission. Une job ne s'offre jamais au téléphone ni au carnet.
- Quatre jobs jouées au bouton : le lunch des gars (t02), un lift au terminus (t03), la sacoche (t05), la pelle du
  vieux (t13) ; et ratée, c'est en personne qu'il le dit."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_p_js import RECHARGER

BASE = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6']"

AIDES = OUTILS + PLUS_LONGUES + RECHARGER + """
  const textes = [];
  const DIALOGUE = L.Hud.dialogue;
  L.Hud.dialogue = function (qui, lignes) { textes.push(qui + ': ' + lignes.join(' ')); return DIALOGUE.apply(null, arguments); };
  function poserA(L, lieu, dy) { const l = L.Histoire.lieu(lieu), j = L.B.joueur; j.x = l.x; j.y = l.y + (dy || 0); j.vx = 0; j.vy = 0; L.Entites.indexer(); return l; }
  // Planté là (à pied, sans bouger) jusqu'à ce qu'un passant attende à côté : la cadence levée (`B.jobRepos`).
  function attendreUnPassant(L, o, lieu, dy) {
    const B = L.B, l = poserA(L, lieu, dy);
    B.jobRepos = B.t + 30;
    let n = 0;
    for (; n < 2400 && !(B.job && B.job.phase === 'attend'); n++) { o.frame(1); poserA(L, lieu, dy); }
    return B.job ? { slug: B.job.slug, arch: B.job.e.arch, n: n, id: B.job.e.id, tenue: !!B.job.e.tenue,
                     bulle: B.job.e.bulle && B.job.e.bulle.texte } : null;
  }
  // Lui parler AU BOUTON : à deux pas, face à lui, ACTION.
  function luiParler(L, o) {
    const B = L.B, e = B.job.e, j = B.joueur;
    j.x = e.x - 14; j.y = e.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
    o.frame(1); j.angle = 0; j.face = 'droite'; L.Missions.majInvite(j); o.tape('KeyE', 2);
    const r = { mission: B.partie.mission && B.partie.mission.slug, intro: !!(B.scene || B.cinema) };
    passer(L, o); ecouter(L);
    return r;
  }
  function versLui(L) { const e = L.B.job.e, j = L.B.joueur; j.x = e.x - 14; j.y = e.y; L.Entites.indexer(); }
"""


def test_un_passant_de_la_rue_se_presente_te_hele_et_vient_a_toi(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        recharger(L);
        poserA(L, 'cantine', 40);
        B.jobRepos = B.t + 30;
        let n = 0, ne = null;
        for (; n < 2400 && !(B.job && B.job.phase === 'attend'); n++) {
          o.frame(1); poserA(L, 'cantine', 40);
          if (B.job && !ne) { const e = B.job.e, j = B.joueur; ne = { d: Math.round(Math.hypot(e.x - j.x, e.y - j.y) / 16), district: L.Monde.zoneA(e.x, e.y).district }; }
        }
        const e = B.job.e, j = B.joueur;
        const m = L.Histoire.mission(B.job.slug);
        return { ne: ne, slug: B.job.slug, arch: e.arch, attend: Math.round(Math.hypot(e.x - j.x, e.y - j.y)),
                 bulle: e.bulle && e.bulle.texte, hele: m.dialogue.hele[0].texte, district: m.passant.district,
                 personnage: e.personnage, tenue: !!e.tenue, id: e.id, offerte: p.jobOfferte, demi: L.Jobs.demiJournee() };
    }""")
    assert r["ne"]["d"] >= 7 and r["ne"]["d"] <= 12 and r["ne"]["district"] == "quais", r
    # Une job des Quais (le débardeur, le vieux) ou de partout (le gérant de la taverne) — jamais d'ailleurs.
    assert r["district"] in ("quais", None) and r["arch"] in ("docker", "itinerant", "passant"), f"un passant d'ici : {r}"
    assert r["attend"] <= 22, f"il s'arrête à portée de parole : {r}"
    assert r["bulle"] == r["hele"], f"sa bulle est son hèlement : {r}"
    assert r["personnage"] in ("passant", "passante") and r["tenue"] and r["id"] >= 1e9, r
    assert r["offerte"] == r["demi"], r


def test_il_nait_sans_de_ni_numero_et_sa_tenue_vient_de_l_empreinte(banc):
    """⚠️ La ville d'une partie où il se présente est la même, au tirage près : le dé de la ville ne bouge pas, ni
    le prochain numéro d'entité. Et le même passant, la même demi-journée, a la même tenue."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        recharger(L);
        poserA(L, 'cantine', 40);
        function prochain() { const e = L.Entites.creer('decor', 0, 0); L.Entites.retirer(e); return e.id; }
        L.graine(77); const de = B.rng(); const id0 = prochain();
        L.graine(77); const e = L.Jobs.offrir('t02'); const de2 = B.rng(); const id1 = prochain();
        const tenue = JSON.stringify(e.tenue);
        L.Jobs.offrir('t02');
        const tenue2 = JSON.stringify(B.job.e.tenue);
        return { de: de, de2: de2, id0: id0, id1: id1, ne: !!e, idPassant: e.id, tenue: tenue === tenue2,
                 enRobe: (L.B.defs.garderobe || {}).garde_robes ? !!L.B.defs.garderobe.garde_robes.docker : null };
    }""")
    assert r["ne"] and r["idPassant"] >= 1e9, r
    assert r["de"] == r["de2"], f"il a tiré un dé de la ville : {r}"
    assert r["id1"] == r["id0"] + 1, f"il a pris un numéro de la ville : {r}"
    assert r["tenue"] is True, r


def test_jamais_pendant_une_mission_ni_au_volant_ni_deux_fois_la_meme_demi_journee(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        const j = recharger(L);
        function attendre(n) { for (let k = 0; k < n && !B.job; k++) { o.frame(1); poserA(L, 'cantine', 40); } return !!B.job; }
        // Trop tôt : une minute et demie après la dernière mission (ou le chargement).
        poserA(L, 'cantine', 40);
        B.jobRepos = B.t + L.Jobs.PAS_AVANT;
        const tot = attendre(120);
        // Pendant une mission.
        B.jobRepos = 0;
        L.Histoire.commencer('m50'); B.cinema = null; B.scene = null;
        const enMission = attendre(120);
        p.mission = null; B.mission = null;
        // Au volant.
        B.jobRepos = 0;
        const v = L.Vehicules.creer('auto', j.x, j.y, 0, { etat: 'stationne', couleur: '#777777' });
        L.Vehicules.monter(j, v); L.Entites.indexer();
        let auVolant = false;
        for (let k = 0; k < 120 && !B.job; k++) { o.frame(1); v.x = j.x; v.vitesse = 0; }
        auVolant = !!B.job;
        L.Vehicules.descendre(j, true);
        // À pied, la cadence levée : il vient.
        B.jobRepos = 0;
        const vient = attendre(240);
        // Laissé en plan : il s'en va — et pas d'autre la même demi-journée.
        const e = B.job && B.job.e;
        for (let k = 0; k < 2000 && B.job; k++) { o.frame(1); j.x = e.x + 400; j.y = e.y; }
        const parti = { job: !!B.job, personnage: e.personnage, etat: e.etat };
        B.jobRepos = 0;
        const encore = attendre(240);
        // La demi-journée suivante : il en vient un.
        p.heure = p.heure < 0.5 ? 0.6 : 0.1; if (p.heure < 0.5) p.jour++;
        B.jobRepos = 0;
        const demain = attendre(240);
        return { tot: tot, enMission: enMission, auVolant: auVolant, vient: vient, parti: parti, encore: encore, demain: demain };
    }""")
    assert r["tot"] is False, "pas avant une minute et demie sans mission"
    assert r["enMission"] is False and r["auVolant"] is False, r
    assert r["vient"] is True, r
    assert r["parti"] == {"job": False, "personnage": None, "etat": "flane"}, f"laissé en plan, il redevient un passant : {r}"
    assert r["encore"] is False and r["demain"] is True, f"une offre par demi-journée : {r}"


def test_une_job_ne_s_offre_ni_au_telephone_ni_au_carnet(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        recharger(L);
        const jobs = L.Jobs.offertes().map(function (m) { return m.slug; });
        const dispo = L.Histoire.disponibles().filter(function (m) { return m.passant; }).length;
        const passant = L.Histoire.disponibleDe('passant'), passante = L.Histoire.disponibleDe('passante');
        return { jobs: jobs, dispo: dispo, passant: passant, passante: passante };
    }""")
    assert set(r["jobs"]) >= {"t02", "t03", "t05", "t13"}, r
    assert r["dispo"] == 0 and r["passant"] is None and r["passante"] is None, r


def test_t02_le_lunch_des_gars(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        recharger(L);
        const argent = paiements(L);
        poserA(L, 'cantine', 40);
        const e = L.Jobs.offrir('t02');
        for (let k = 0; k < 600 && B.job.phase !== 'attend'; k++) { o.frame(1); poserA(L, 'cantine', 40); }
        const pris = luiParler(L, o);
        const telephone = textes.some(function (t) { return t.indexOf('TÉLÉPHONE') >= 0; });
        poserA(L, 'cantine'); jouer(L, o, 10);
        const cantine = etape(L);
        versLui(L); jouer(L, o, 10);
        finir(L, o); jouer(L, o, 4);
        return { pris: pris, cantine: cantine, textes: textes, telephone: telephone, fait: !!p.missionsFaites.t02,
                 argent: argent.map(function (a) { return a.montant; }), parti: !B.job && e.personnage === null };
    }""")
    assert r["pris"] == {"mission": "t02", "intro": True}, r
    assert r["cantine"] == 1, r
    dites = " | ".join(r["textes"])
    assert "Le débardeur: T'as des jambes?" in dites and "Encore chauds!" in dites, dites
    assert r["telephone"] is False, "un passant n'a pas ton numéro : tout se dit en personne"
    assert r["fait"] is True and r["argent"] == [30] and r["parti"] is True, r


def test_t02_trop_lent_le_debardeur_te_le_dit_en_personne(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        recharger(L);
        poserA(L, 'cantine', 40);
        L.Jobs.offrir('t02', true);
        luiParler(L, o);
        poserA(L, 'cantine'); jouer(L, o, 10);
        // Le lunch refroidit : on traîne à la cantine.
        let n = 0;
        for (; n < 7000 && p.mission; n++) { o.frame(1); poserA(L, 'cantine'); }
        const rate = textes.filter(function (t) { return t.indexOf('bottes') >= 0; });
        return { rate: rate, mission: p.mission, fait: !!p.missionsFaites.t02, job: !!B.job };
    }""")
    assert r["mission"] is None and r["fait"] is False, r
    assert r["rate"] and "TÉLÉPHONE" not in r["rate"][0] and r["rate"][0].startswith("Le débardeur"), r


def test_t02_trop_lent_et_loin_un_simple_job_ratee(banc):
    """Martin, 1er oct. 2026 : loin du passant, l'échec ne se dit pas — un simple « JOB RATÉE » au HUD ; sa voix
    seulement s'il est là (le juge d'avant)."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        recharger(L);
        poserA(L, 'cantine', 40);
        L.Jobs.offrir('t02', true);
        luiParler(L, o);
        poserA(L, 'cantine'); jouer(L, o, 10);
        // Le lunch refroidit : on est parti loin, au phare.
        const msgs = [];
        let n = 0;
        for (; n < 7000 && p.mission; n++) { o.frame(1); poserA(L, 'phare'); if (typeof B.msg === 'string') msgs.push(B.msg); }
        const rate = textes.filter(function (t) { return t.indexOf('bottes') >= 0; });
        return { rate: rate, mission: p.mission, fait: !!p.missionsFaites.t02,
                 jobRatee: msgs.some(function (t) { return t.indexOf('JOB RATÉE') === 0; }),
                 missionRatee: msgs.some(function (t) { return t.indexOf('MISSION RATÉE') === 0; }) };
    }""")
    assert r["mission"] is None and r["fait"] is False, r
    assert r["jobRatee"] and not r["missionRatee"], r
    assert not r["rate"], f"le débardeur est loin : il ne te le dit pas : {r}"


def test_t03_un_lift_au_terminus(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        const j = recharger(L);
        const argent = paiements(L);
        poserA(L, 'bar', 30);
        const e = L.Jobs.offrir('t03', true);
        const pris = luiParler(L, o);
        // Un char à l'arrêt à côté d'elle : elle monte ; puis le terminus.
        const v = L.Vehicules.creer('auto', e.x + 10, e.y, 0, { etat: 'stationne', couleur: '#777777' });
        j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o, 30);
        const monte = e.dansVehicule === v;
        const t = L.Histoire.lieu('terminus');
        v.x = t.x; v.y = t.y + 24; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
        finir(L, o);
        return { pris: pris, monte: monte, textes: textes, fait: !!p.missionsFaites.t03,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["pris"]["mission"] == "t03", r
    assert r["monte"] is True, r
    dites = " | ".join(r["textes"])
    assert "La dame à la valise: Mon autobus pour Rimouski" in dites and "Juste à temps!" in dites, dites
    assert r["fait"] is True and r["argent"] == [40], r


def test_t05_la_sacoche_reprise_par_derriere(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        const j = recharger(L);
        const argent = paiements(L);
        poserA(L, 'kiosque', 30);
        L.Jobs.offrir('t05', true);
        const pris = luiParler(L, o);
        const voleur = B.mission.entites.find(function (e) { return e.pickpocket; });
        const qui = voleur && voleur.arch;
        // Par-derrière : dans son dos, face à lui, ACTION.
        voleur.vx = 0; voleur.vy = 0; voleur.angle = 0; voleur.face = 'droite'; voleur.etat = 'arret'; voleur.minuterie = 600;
        j.x = voleur.x - 12; j.y = voleur.y; j.face = 'droite'; j.angle = 0; L.Entites.indexer();
        L.Missions.majInvite(j); o.tape('KeyE', 2); jouer(L, o, 10);
        const vole = etape(L);
        versLui(L); jouer(L, o, 10);
        finir(L, o);
        return { pris: pris, qui: qui, vole: vole, fait: !!p.missionsFaites.t05, textes: textes,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["pris"]["mission"] == "t05" and r["qui"] == "itinerant", r
    assert r["vole"] == 1, r
    assert r["fait"] is True and r["argent"][-1] == 50, r


def test_t13_la_pelle_du_vieux_et_il_te_la_laisse(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        const j = recharger(L);
        const argent = paiements(L);
        poserA(L, 'cantine', 40);
        L.Jobs.offrir('t13', true);
        const pris = luiParler(L, o);
        jouer(L, o, 10);
        const morues = B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
        const pose = { n: morues.length, gang: morues.map(function (e) { return e.gang; }) };
        // Loin du vieux avant de coucher la Morue : sinon `retourner` se fait dans la même image.
        j.x += 300; L.Entites.indexer();
        morues.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const couche = etape(L);
        versLui(L); jouer(L, o, 10);
        finir(L, o);
        return { pris: pris, pose: pose, couche: couche, fait: !!p.missionsFaites.t13, pelle: !!p.armes.pelle,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["pris"]["mission"] == "t13", r
    assert r["pose"] == {"n": 1, "gang": ["morues"]} and r["couche"] == 1, r
    assert r["fait"] is True and r["pelle"] is True and r["argent"] == [20], r


# --- Sept jobs de plus (même vague) : le char au lot, le BMX, la tournée du Clairon, le feu de camp, la gageure, les
# mariés, l'autobus manqué — chacune jouée au bouton, de la rue à la prime.

CHAR = """
  function auVolant(L, o, v) {
    const j = L.B.joueur;
    if (j.dansVehicule) L.Vehicules.descendre(j, true);
    j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o, 3);
    return j.dansVehicule === v;
  }
  function rouler(L, o, v, lieu, dy) {
    const j = L.B.joueur, l = L.Histoire.lieuDeLivraison(lieu) || L.Histoire.lieu(lieu);
    v.x = l.x; v.y = l.y + (dy || 0); v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); jouer(L, o, 8);
  }
  function aPiedPres(L, o, e) { const j = L.B.joueur; if (j.dansVehicule) L.Vehicules.descendre(j, true); j.x = e.x - 14; j.y = e.y; L.Entites.indexer(); jouer(L, o, 8); }
"""


def _jouee(banc, corps):
    return banc("function (L, o) {" + AIDES + CHAR + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        const j = recharger(L);
        const argent = paiements(L);
    """ + corps + """
        return Object.assign(r, { textes: textes, argent: argent.map(function (a) { return a.montant; }) });
    }""")


def test_t01_son_char_au_lot_seme_et_ramene_aux_erables(banc):
    r = _jouee(banc, """
        poserA(L, 'depanneur', 30);
        const e = L.Jobs.offrir('t01', true);
        const pris = luiParler(L, o);
        const v = B.mission.vehicule;
        const lot = v ? Math.round(Math.hypot(v.x - L.Histoire.lieu('fourriere').x, v.y - L.Histoire.lieu('fourriere').y) / 16) : null;
        auVolant(L, o, v);
        const etoiles = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        const seme = etape(L);
        auVolant(L, o, v); rouler(L, o, v, 'depanneur');
        const livre = etape(L);
        aPiedPres(L, o, e); finir(L, o);
        const r = { pris: pris.mission, lot: lot, etoiles: etoiles, seme: seme, livre: livre, fait: !!p.missionsFaites.t01 };
    """)
    assert r["pris"] == "t01" and r["lot"] is not None and r["lot"] <= 6, r
    assert r["etoiles"] == {"etape": 1, "etoiles": 1} and r["seme"] == 2 and r["livre"] == 3, r
    assert r["fait"] is True and r["argent"] == [80], r


def test_t04_le_bmx_repris_au_skateux(banc):
    r = _jouee(banc, """
        poserA(L, 'phare', 30);
        L.Jobs.offrir('t04', true);
        const pris = luiParler(L, o);
        jouer(L, o, 10);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
        j.x += 300; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const couche = etape(L);
        versLui(L); jouer(L, o, 10); finir(L, o);
        const r = { pris: pris.mission, gangs: eux.map(function (e) { return e.gang; }), couche: couche, fait: !!p.missionsFaites.t04 };
    """)
    assert r["pris"] == "t04" and r["gangs"] == ["skateux"] and r["couche"] == 1, r
    assert r["fait"] is True and r["argent"] == [25], r


def test_t09_six_clairons_dans_l_ordre(banc):
    r = _jouee(banc, """
        poserA(L, 'kiosque', 30);
        const e = L.Jobs.offrir('t09', true);
        const pris = luiParler(L, o);
        const vus = [];
        ['terminus', 'armurerie', 'vetements', 'bar', 'casse_croute', 'garage'].forEach(function (l) {
          poserA(L, l); jouer(L, o, 6); vus.push(B.mission && B.mission.course ? B.mission.course.i : etape(L));
        });
        const livre = etape(L);
        aPiedPres(L, o, e); finir(L, o);
        const r = { pris: pris.mission, vus: vus, livre: livre, fait: !!p.missionsFaites.t09 };
    """)
    assert r["pris"] == "t09" and r["livre"] == 1, r
    assert r["fait"] is True and r["argent"] == [60], r


def test_t11_le_feu_de_camp_contre_la_remise_du_phare(banc):
    r = _jouee(banc, """
        poserA(L, 'phare', 40);
        const e = L.Jobs.offrir('t11', true);
        const pris = luiParler(L, o);
        const feu = B.mission.feu, ph = L.Histoire.lieu('phare');
        const ou = feu ? L.Incendies.position(feu) : null;
        const brule = { feu: !!feu, arme: j.arme, pres: ou ? Math.round(Math.hypot(ou.x - ph.x, ou.y - ph.y) / 16) : null };
        o.touche('KeyJ');
        for (let k = 0; k < 400 && etape(L) === 0; k++) { j.x = ou.x; j.y = ou.y + 18; j.angle = -Math.PI / 2; o.frame(1); ecouter(L); }
        o.relacher('KeyJ'); o.frame(1);
        const eteint = etape(L);
        aPiedPres(L, o, e); finir(L, o);
        const r = { pris: pris.mission, brule: brule, eteint: eteint, fait: !!p.missionsFaites.t11 };
    """)
    assert r["pris"] == "t11" and r["brule"]["feu"] and r["brule"]["arme"] == "extincteur" and r["brule"]["pres"] <= 8, r
    assert r["eteint"] == 1 and r["fait"] is True and r["argent"] == [50], r


def test_t12_la_gageure_l_hopital_sous_le_chrono(banc):
    r = _jouee(banc, """
        poserA(L, 'bar', 30);
        const e = L.Jobs.offrir('t12', true);
        const pris = luiParler(L, o);
        poserA(L, 'hopital'); jouer(L, o, 8);
        const arrive = etape(L);
        aPiedPres(L, o, e); finir(L, o);
        const r = { pris: pris.mission, arrive: arrive, fait: !!p.missionsFaites.t12 };
    """)
    assert r["pris"] == "t12" and r["arrive"] == 1, r
    assert r["fait"] is True and r["argent"] == [70], r


def test_t14_la_mariee_au_phare_dans_la_berline_de_l_oncle(banc):
    r = _jouee(banc, """
        poserA(L, 'depanneur', 60);
        const e = L.Jobs.offrir('t14', true);
        const pris = luiParler(L, o);
        const v = B.mission.vehicule;
        const slug = v && v.slug;
        auVolant(L, o, v);
        v.x = e.x + 20; v.y = e.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); jouer(L, o, 30);
        const monte = e.dansVehicule === v;
        rouler(L, o, v, 'phare', 24); finir(L, o);
        const r = { pris: pris.mission, slug: slug, monte: monte, fait: !!p.missionsFaites.t14 };
    """)
    assert r["pris"] == "t14" and r["slug"] == "luxe" and r["monte"] is True, r
    assert r["fait"] is True and r["argent"] == [120], r


def test_t15_l_autobus_manque_jusqu_a_la_fourriere(banc):
    r = _jouee(banc, """
        poserA(L, 'terminus', 30);
        const e = L.Jobs.offrir('t15', true);
        const pris = luiParler(L, o);
        const v = L.Vehicules.creer('auto', e.x + 10, e.y, 0, { etat: 'stationne', couleur: '#777777' });
        auVolant(L, o, v); jouer(L, o, 30);
        const monte = e.dansVehicule === v;
        rouler(L, o, v, 'fourriere', 24); finir(L, o);
        const r = { pris: pris.mission, monte: monte, fait: !!p.missionsFaites.t15 };
    """)
    assert r["pris"] == "t15" and r["monte"] is True, r
    assert r["fait"] is True and r["argent"] == [40], r


def test_t06_la_biere_de_la_taverne_au_quai(banc):
    r = _jouee(banc, """
        poserA(L, 'hotel', 30);
        const e = L.Jobs.offrir('t06', true);
        const pris = luiParler(L, o);
        const v = B.mission.vehicule;
        const slug = v && v.slug;
        auVolant(L, o, v);
        rouler(L, o, v, 'cantine');
        const livre = etape(L);
        aPiedPres(L, o, e); finir(L, o);
        const r = { pris: pris.mission, slug: slug, livre: livre, fait: !!p.missionsFaites.t06 };
    """)
    assert r["pris"] == "t06" and r["slug"] == "camion" and r["livre"] == 2, r
    assert r["fait"] is True and r["argent"] == [90], r


def test_les_jobs_voyagent_pliees_et_le_jeu_les_deplie_une_fois(banc):
    """`missions.jobs_pour_le_navigateur` : une liste par job, sans noms de clés — le jeu les remet dans le catalogue
    en recevant le paquet (`Jobs.deplier`), une seule fois, et `Histoire.mission` les trouve comme les autres."""
    from app import missions
    pliees = missions.jobs_pour_le_navigateur()
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const defs = { missions: [{ slug: 'm1', titre: 'x', donneur: 'ti_guy', prerequis: [], recompense: 1 }], jobs: %s };
        L.Jobs.deplier(defs); L.Jobs.deplier(defs);
        const t02 = defs.missions.find(function (m) { return m.slug === 't02'; });
        const dansLeJeu = L.Histoire.mission('t13');
        return { n: defs.missions.length, t02: t02, jeu: !!dansLeJeu && dansLeJeu.passant,
                 doublons: L.B.defs.missions.filter(function (m) { return m.slug === 't05'; }).length };
    }""" % __import__("json").dumps(pliees))
    assert r["n"] == 1 + len(pliees), r
    assert r["t02"] == {"slug": "t02", "titre": "Le lunch des gars", "donneur": "passant", "recompense": 30,
                        "passant": "docker@quais", "prerequis": ["m6"]}, r["t02"]
    assert r["jeu"] and r["doublons"] == 1, r
