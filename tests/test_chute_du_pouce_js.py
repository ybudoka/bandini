"""La chute du Pouce (l'arc d'Irène au Petit-Canton), JOUÉE au banc — docs/jalons/le-quartier-chinois.md.

Martin, 29 sept. 2026 : « on fait tomber le Pouce pour de bon ». Depuis le 2 oct. 2026, c'est un CHAPITRE
(`chute_du_pouce`, docs/jalons/des-missions-en-chapitres.md, vague C) : c01 à c04 en sont les quatre actes, et chaque
juge commence l'acte là où une vieille partie le reprendrait (les missions des actes d'avant faites). L'acte 1 (le
jeton, c01) se joue dans `test_tripot_js.py`. Chaque acte se joue au bouton, de la poignée de main d'Irène au
marqueur de l'acte suivant : l'acte 2 glisse ses dés pipés dans ta manche à la barbotte (`Tripot.glisser`, un
`obtenir` dont la `table` est le tripot) ; l'acte 3 fait jaser Norbert, file le comptable et ramasse le livre au
terminus, sur le chrono — trop lent, c'est raté, et on REPREND L'ACTE 3 ; l'acte 4 rattrape la caisse du quartier, et
le chapitre est fait. Et ce qui change dans le monde quand le Pouce tombe se juge : plus de Pouce ni de gros bras, le
vieux Chan à la table, jamais de pipés, plus de méfiance — et la une du Clairon le lendemain.
"""

from outils_missions import OUTILS as OUTILS_MISSIONS, PLUS_LONGUES

from app import tripot

OUTILS = OUTILS_MISSIONS + PLUS_LONGUES + """
  const AVANT = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'];
  // Jouer jusqu'à l'étape `e` (les marqueurs et leurs répliques), sans jamais passer par-dessus.
  function jusqua(L, o, e) {
    for (let k = 0; k < 2400 && etape(L) !== null && etape(L) < e; k++) { if (L.B.transition) o.fondu(); o.frame(1); ecouter(L); }
    return etape(L);
  }
  function dansLaPorte(L, o, lieu) {
    const B = L.B, j = B.joueur, M = L.Monde;
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    return B.interieur ? B.interieur.slug : null;
  }
  function dehors(L, o) {
    L.Jeu.sortir(); o.fondu();
    for (let k = 0; k < 200 && L.B.interieur; k++) o.frame(1);
    return !L.B.interieur;
  }
  function poser(L, o, tx, ty, face) {
    const j = L.B.joueur, a = { haut: -Math.PI / 2, bas: Math.PI / 2, gauche: Math.PI, droite: 0 }[face];
    j.x = tx * 16 + 8; j.y = ty * 16 + 8; j.angle = a; j.face = face; L.Entites.indexer();
    o.frame(1); j.angle = a; j.face = face; L.Missions.majInvite(j);
  }
  // Descendre AU BOUTON : devant la marche, dans l'alcôve derrière la porte, et ACTION.
  function descendre(L, o) {
    const B = L.B, esc = B.interieur.points.find(function (p) { return p.type === 'escalier'; });
    poser(L, o, esc.x, esc.y - 1, 'bas');
    o.tape('KeyE', 2); o.fondu();
    for (let k = 0; k < 200 && B.interieur && B.interieur.slug !== 'nord_tripot'; k++) o.frame(1);
    return B.interieur && B.interieur.slug;
  }
  function aLaTable(L, o) {
    const B = L.B, pt = B.interieur.points.find(function (p) { return p.type === 'barbotte'; });
    poser(L, o, pt.x, pt.y + 1, 'haut');
    o.tape('KeyE', 2);
    return B.menu ? B.menu.titre : null;
  }
  function choisir(L, o, libelle) {
    const m = L.B.menu, i = m ? m.items.findIndex(function (x) { return x.libelle === libelle; }) : -1;
    if (i < 0) return false;
    m.curseur = i; o.tape('KeyE', 2);
    return true;
  }
  function lignes(L) { return L.B.menu ? L.B.menu.items.map(function (x) { return x.libelle; }) : null; }
  // Miser 1 000 $ au bouton jusqu'à ce que le Pouce pose ses pipés (plafonné) : les lignes du menu à ce moment.
  function jusquAuxPipes(L, o) {
    const T = L.Tripot, e = T.etat();
    for (let k = 0; k < 60; k++) {
      e.mise = 1000; e.coups = 0; e.mefiance = 0; e.propre = 0;
      choisir(L, o, 'MISER');
      const t = T.enCours();
      if (t && t.pipes) return lignes(L);
      choisir(L, o, 'LANCER');
    }
    return null;
  }
  // Jouer jusqu'à ce que la mission, sa scène et ses répliques soient finies (plafonné).
  function auBout(L, o) {
    const B = L.B;
    for (let k = 0; k < 6000 && (B.partie.mission || B.scene || B.cinema); k++) { o.frame(1); ecouter(L); }
  }
  function commencerChezIrene(L, o) {
    const B = L.B;
    dansLaPorte(L, o, 'nord_casino'); jouer(L, o);
    serrer(L, o, 'irene');
    for (let k = 0; k < 6000 && (B.scene || B.cinema); k++) { o.frame(1); ecouter(L); }
    jouer(L, o);
    return { mission: B.partie.mission && B.partie.mission.slug, etape: etape(L), ligne: L.Histoire.ligneObjectif() };
  }
  // Le fuyard d'un `ramasser` : le char casse, le porteur tombe, on ramasse la caisse à pied.
  function rattraper(L, o) {
    const B = L.B, j = B.joueur, f = B.mission.fuyard;
    if (!f) return { rate: 'pas de fuyard' };
    L.Vehicules.endommager(f, 999, j); jouer(L, o, 2);
    const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
    if (!porteur) return { rate: 'pas de porteur', etat: f.etat, tombe: !!B.mission.fuyardTombe, cinema: !!B.cinema, etape: etape(L) };
    const cravate = porteur.gang || null;
    L.Entites.assommer(porteur); jouer(L, o, 2);
    const caisse = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
    if (!caisse) return { rate: 'pas de caisse', cravate: cravate };
    j.x = caisse.x; j.y = caisse.y; L.Entites.indexer(); jouer(L, o, 2);
    return { cravate: cravate };
  }
  function ceuxDuTripot(L) {
    const B = L.B;
    return { pouce: B.entites.filter(function (e) { return e.pouce; }).length,
             gros: B.entites.filter(function (e) { return e.grosBras; }).length,
             chan: B.entites.filter(function (e) { return e.chan; }).length };
  }
"""


def test_acte_2_on_glisse_ses_des_pipes_dans_sa_manche_au_bouton(banc):
    """L'acte 2 (c02, _Une paire dans la manche_), de la poignée de main d'Irène à l'acte 3. Avant le chapitre, les
    pipés sur le feutre n'offrent que LANCER / CHANGER / DÉNONCER. Une vieille partie qui a fait c01 reprend à l'acte 2 :
    dedans, le marqueur attend qu'on sorte ; dehors, il s'ouvre. Pendant, Irène renvoie au sous-sol qui lui reparle ;
    en bas, quand le Pouce pose ses pipés, GLISSER TES DÉS apparaît : les siens entrent au sac, le coup se joue avec des
    dés honnêtes (blancs), et rien ne se pose en ville. L'objectif avance dehors : l'acte paie sa prime (500 $), c02 est
    faite, et l'acte 3 s'ouvre. ⚠️ L'`exige` de c02 (500 $ en poche) est tombé avec le chapitre : Irène a son job même
    sans le sou — c'est le Pouce qui ne triche pas sous 500 $ (`test_acte_2_envoye_par_irene…`)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, T = L.Tripot; j.invincible = 1e6;
        faites(L, AVANT.concat(['c01']));
        B.partie.argent = 400;
        const pasAssez = L.Histoire.disponibleDe('irene');
        B.partie.argent = 20000;
        const argent = paiements(L);
        // Sans la mission : les pipés, et pas de quoi les glisser.
        dansLaPorte(L, o, 'nord_casino'); descendre(L, o); aLaTable(L, o);
        const avant = jusquAuxPipes(L, o);
        choisir(L, o, 'LANCER'); L.Hud.fermerMenu();
        dehors(L, o);
        const debut = commencerChezIrene(L, o);
        dehors(L, o); jusqua(L, o, 4);
        const ouvert = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        dansLaPorte(L, o, 'nord_casino'); jouer(L, o);
        const renvoi = serrer(L, o, 'irene');
        // Dehors avant d'avoir les dés : rien ne se pose à la porte du Dragon d'or (l'objet vient du feutre).
        dehors(L, o); jouer(L, o, 5);
        const posesAvant = B.entites.filter(function (e) { return e.type === 'ramassage' && e.objetDeMission; }).length;
        dansLaPorte(L, o, 'nord_casino'); jouer(L, o);
        const ici = descendre(L, o);
        aLaTable(L, o);
        const pendant = jusquAuxPipes(L, o);
        const t = T.enCours();
        choisir(L, o, 'GLISSER TES DÉS');
        const glisse = { pipes: t.pipes, poids: t.poids, glisse: t.glisse, sac: (B.partie.objets || {}).des_pipes || 0,
                         msg: B.msg || null, lignes: lignes(L), curseur: B.menu.curseur };
        choisir(L, o, 'LANCER');
        const coup = { paires: t.paires.length, gain: t.resultat.gain };
        L.Hud.fermerMenu();
        const dedans = etape(L);
        dehors(L, o); jouer(L, o, 3);
        const poses = B.entites.filter(function (e) { return e.type === 'ramassage' && e.objetDeMission; }).length;
        jusqua(L, o, 6);
        return { pasAssez: pasAssez && pasAssez.slug, avant: avant, debut: debut, ouvert: ouvert, renvoi: renvoi, ici: ici, pendant: pendant,
                 glisse: glisse, coup: coup, dedans: dedans, poses: poses, posesAvant: posesAvant, dites: dites,
                 fait: !!B.partie.missionsFaites.c02, argent: argent.map(function (a) { return a.montant; }),
                 garde: (B.partie.objets || {}).des_pipes || 0, apres: etape(L), ligne: L.Histoire.ligneObjectif() };
    }""")
    assert r["pasAssez"] == "chute_du_pouce", "l'exige de c02 est tombé avec le chapitre : Irène a son job sans le sou"
    assert r["avant"] == ["LANCER", "CHANGER DE CÔTÉ", "DÉNONCER LES DÉS"], f"sans la mission, rien à glisser : {r['avant']}"
    assert r["debut"]["mission"] == "chute_du_pouce" and r["debut"]["etape"] == 3, f"dedans, l'acte 2 attend qu'on sorte : {r['debut']}"
    assert r["ouvert"]["etape"] == 4 and r["ouvert"]["ligne"].startswith("EMPOCHE LES DÉS JAUNES"), r["ouvert"]
    assert r["renvoi"] == "renvoi", "lui reparler pendant l'objectif : elle renvoie au sous-sol"
    assert r["ici"] == "nord_tripot"
    assert r["pendant"] == ["LANCER", "CHANGER DE CÔTÉ", "DÉNONCER LES DÉS", "GLISSER TES DÉS"], r["pendant"]
    g = r["glisse"]
    assert g["pipes"] is False and g["poids"] is None and g["glisse"] is True, f"le coup se joue honnête : {g}"
    assert g["sac"] == 1 and g["msg"] == tripot.PREUVE["nom"], g
    assert "GLISSER TES DÉS" not in g["lignes"] and g["curseur"] == 0, "une fois glissés, le curseur va sur LANCER"
    assert r["coup"]["paires"] >= 1 and r["coup"]["gain"] in (0, 1000, 1950), r["coup"]
    assert r["dedans"] == 4, "dans une pièce, l'objectif dort : il avance à la sortie"
    assert r["posesAvant"] == 0 and r["poses"] == 0, "un objet de table ne se pose nulle part en ville"
    for dite in ("pendant:irene:3", "pendant:irene:4", "renvoi:irene:4", "pendant:irene:5"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert [d for d in r["dites"] if d.startswith("intro:")] == [], "une vieille partie reprend à l'acte 2, sans l'intro de c01"
    assert r["fait"] is True and r["argent"][-1] == 500 and r["garde"] == 1, "la prime de l'acte, après les gains de la table"
    assert r["apres"] == 6 and r["ligne"].startswith("À L'HÔTEL, FAIS JASER NORBERT"), "l'acte 3 commence : la suite royale"


def test_acte_3_norbert_la_filature_et_le_livre_au_terminus(banc):
    """L'acte 3 (c03, _La suite royale_) : Irène au bar ; à l'hôtel, Norbert jase au bouton (sa poignée de main dite,
    deux répliques) ; le comptable naît à bonne distance, attend qu'on soit au volant et roule jusqu'au terminus ;
    arrivé, le livre (un registre) attend à la porte du terminus, on marche dessus : l'acte paie sa prime (600 $), et
    l'acte 4 s'ouvre là — le chauffeur du Pouce file de devant le terminus."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, AVANT.concat(['c01', 'c02']));
        const argent = paiements(L);
        const debut = commencerChezIrene(L, o);
        dehors(L, o); jusqua(L, o, 6);
        debut.ligne = L.Histoire.ligneObjectif();
        dansLaPorte(L, o, 'hotel'); jouer(L, o);
        const accueil = serrer(L, o, 'norbert');
        const apresNorbert = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        dehors(L, o); jouer(L, o);
        const c = B.mission.suivi;
        const dNaissance = Math.round(Math.hypot(c.x - j.x, c.y - j.y));
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const arret = L.Histoire.tuileDeRue(j.x, j.y, 10);
        const mien = L.Vehicules.creer('auto', arret.x, arret.y, CAP[arret.sens], { etat: 'stationne' });
        j.x = mien.x + 10; j.y = mien.y; L.Entites.indexer();
        L.Vehicules.monter(j, mien); L.Entites.indexer();
        let i = 0;
        for (; i < 15000 && B.partie.mission && B.partie.mission.etape === 7; i++) {
            if (!c.attendLeJoueur) {
                mien.x = c.x - Math.cos(c.angle) * 96; mien.y = c.y - Math.sin(c.angle) * 96;
                mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
            }
            o.frame(1); ecouter(L);
        }
        const t = L.Histoire.lieu('terminus');
        const file = { images: i, etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                       dTerminus: Math.round(Math.hypot(t.x - c.x, t.y - c.y)) };
        aPied(L); jouer(L, o);
        const livre = B.entites.find(function (e) { return e.type === 'ramassage' && e.objetDeMission === 'livre_du_pouce'; });
        const pose = livre ? { dessin: livre.objet, dTerminus: Math.round(Math.hypot(livre.x - t.x, livre.y - t.y)) } : null;
        j.x = livre.x; j.y = livre.y; L.Entites.indexer(); jouer(L, o, 3);
        const sac = (B.partie.objets || {}).livre_du_pouce || 0;
        jusqua(L, o, 10); jouer(L, o, 30);
        const fuyard = B.mission.fuyard;
        return { debut: debut, accueil: accueil, apresNorbert: apresNorbert, dNaissance: dNaissance, file: file, pose: pose,
                 sac: sac, dites: dites, fait: !!B.partie.missionsFaites.c03, argent: argent.map(function (a) { return a.montant; }),
                 apres: etape(L), fuyard: fuyard ? Math.round(Math.hypot(fuyard.x - t.x, fuyard.y - t.y) / 16) : null };
    }""")
    assert r["debut"]["mission"] == "chute_du_pouce" and r["debut"]["etape"] == 5, r["debut"]
    assert r["debut"]["ligne"].startswith("À L'HÔTEL, FAIS JASER NORBERT"), r["debut"]
    assert r["accueil"] == "accueil", "au bouton, Norbert jase (sa poignée de main)"
    assert r["apresNorbert"]["etape"] == 7 and r["apresNorbert"]["ligne"].startswith("SUIS LE COMPTABLE"), r["apresNorbert"]
    assert r["dNaissance"] >= 5 * 16, r["dNaissance"]
    f = r["file"]
    assert f["etape"] == 8 and f["ligne"].startswith("RAMASSE SON LIVRE"), f
    assert f["dTerminus"] < 8 * 16 and f["images"] > 30 * 60, f"une vraie filature, jusqu'au terminus : {f}"
    assert r["pose"] == {"dessin": "registre", "dTerminus": r["pose"]["dTerminus"]} and r["pose"]["dTerminus"] < 48, r["pose"]
    assert r["sac"] == 1
    for dite in ("pendant:irene:5", "accueil:norbert:6", "pendant:irene:7", "pendant:irene:8", "pendant:irene:9"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [600], r
    assert r["apres"] == 10 and r["fuyard"] is not None and r["fuyard"] <= 16, f"l'acte 4 part du terminus : {r}"


def test_acte_3_le_livre_repart_avec_les_rabatteurs_puis_on_reprend_l_acte(banc):
    """Le chrono du livre MORD : arrivé au terminus, qui traîne plus de trente secondes rate le chapitre — le livre
    n'est plus par terre ni dans le sac (`Infiltration.rendre`), c03 n'est pas faite, et c'est l'échec de l'acte 3
    qu'Irène dit. À vingt, il attend. Puis le menu : REPRENDRE L'ACTE 3 — et l'on repart chez Norbert, les dés du
    Pouce toujours en poche (ils sont de l'acte 2)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, AVANT.concat(['c01', 'c02']));
        B.partie.objets = B.partie.objets || {}; B.partie.objets.des_pipes = 1;
        commencer(L, o, 'chute_du_pouce'); jusqua(L, o, 6);
        // Loin du terminus (la partie commence devant) : le livre ne se ramasse pas tout seul.
        const t = L.Histoire.lieu('terminus');
        j.x = t.x + 200; j.y = t.y + 120; L.Entites.indexer();
        B.partie.mission.etape = 7; L.Histoire.avancer(); o.frame(1); fermer(L);
        jouer(L, o, 20 * 60);
        const a20 = { mission: B.partie.mission && B.partie.mission.slug, etape: etape(L),
                      livre: B.entites.some(function (e) { return e.objetDeMission === 'livre_du_pouce'; }) };
        jouer(L, o, 12 * 60);
        const rate = { apres: B.partie.mission ? B.partie.mission.slug : null, fait: !!B.partie.missionsFaites.c03,
                       livre: B.entites.some(function (e) { return e.objetDeMission === 'livre_du_pouce'; }),
                       sac: (B.partie.objets || {}).livre_du_pouce || 0,
                       echec: dites.filter(function (d) { return d.indexOf('echec:') === 0; }) };
        for (let k = 0; k < 900 && (B.transition || B.cinema || !B.menu); k++) { o.frame(1); ecouter(L); }
        const menu = B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null;
        const item = B.menu.items.find(function (x) { return x.libelle.indexOf('REPRENDRE') === 0; });
        if (item.faire(item) !== false && B.menu) L.Hud.fermerMenu();
        o.fondu(); for (let k = 0; k < 400 && B.transition; k++) o.frame(1);
        jusqua(L, o, 6);
        return { a20: a20, rate: rate, menu: menu, repris: { mission: B.partie.mission && B.partie.mission.slug, etape: etape(L),
                 ligne: L.Histoire.ligneObjectif(), des: (B.partie.objets || {}).des_pipes || 0 } };
    }""")
    assert r["a20"] == {"mission": "chute_du_pouce", "etape": 8, "livre": True}, r["a20"]
    rate = r["rate"]
    assert rate["apres"] is None and rate["fait"] is False, f"trente secondes passées, c'est raté : {rate}"
    assert rate["livre"] is False and rate["sac"] == 0, rate
    assert rate["echec"] == ["echec:irene:5"], "on entend l'échec du livre, pas celui des dés"
    assert r["menu"][:2] == ["REPRENDRE L'ACTE 3", "PLUS TARD"], r["menu"]
    rp = r["repris"]
    assert rp["mission"] == "chute_du_pouce" and rp["etape"] == 6 and rp["ligne"].startswith("À L'HÔTEL"), rp
    assert rp["des"] == 1, "rater l'acte 3 ne fait pas retomber les dés de l'acte 2"


def test_acte_4_la_caisse_rattrapee_et_le_tripot_change_de_mains(banc):
    """L'acte 4 (c04, _La barbotte change de mains_), le dernier : une vieille partie qui a fait c01 à c03 le reprend
    chez Irène ; le chauffeur du Pouce file EN CHAR de près du joueur (ici, la porte du Dragon d'or) ; cassé,
    une Cravate en descend avec la caisse ; couchée, on la ramasse ; le Pouce se nomme en se sauvant, Irène dit de
    la rapporter ; au Dragon d'or, la mission se ferme (1 500 $) et le Clairon aura sa une. Puis le monde a changé :
    plus de gros bras à la porte d'en haut, ni au sous-sol, plus de Pouce — le vieux Chan tient la barbotte, sa
    bulle le dit, le menu s'appelle autrement, n'a plus rien à dénoncer, et deux cents coups à 1 000 $ ne voient
    jamais un pipé, même avec une méfiance à cent cinquante et une semaine barrée."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, T = L.Tripot; j.invincible = 1e6;
        faites(L, AVANT.concat(['c01', 'c02', 'c03']));
        const argent = paiements(L);
        const debut = commencerChezIrene(L, o);
        dehors(L, o); jusqua(L, o, 10);
        debut.ligne = L.Histoire.ligneObjectif();
        const f = B.mission.fuyard;
        const c = L.Histoire.lieu('nord_casino');
        const fuyard = f ? { slug: f.slug, dCasino: Math.round(Math.hypot(f.x - c.x, f.y - c.y) / 16) } : null;
        jouer(L, o, 30);
        const cravate = rattraper(L, o);
        jouer(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        j.x = c.x; j.y = c.y + 8; L.Entites.indexer(); jouer(L, o, 30);
        auBout(L, o);
        const fait = !!B.partie.missionsFaites.c04 && !!B.partie.missionsFaites.chute_du_pouce, une = B.partie.manchetteForcee || null;
        const maitre = !!L.Histoire.donneur('maitre') || (L.Histoire.disponibleDe('irene') || {}).slug || null;
        // Le monde, après.
        dansLaPorte(L, o, 'nord_casino'); jouer(L, o);
        const enHaut = ceuxDuTripot(L);
        const ici = descendre(L, o); jouer(L, o);
        const enBas = ceuxDuTripot(L);
        const chan = B.entites.find(function (e) { return e.chan; });
        const pt = B.interieur.points.find(function (p) { return p.type === 'barbotte'; });
        poser(L, o, pt.x, pt.y + 1, 'haut'); jouer(L, o, 3);
        const bulle = chan && chan.bulle ? chan.bulle.texte || chan.bulle : null;
        B.partie.argent = 1e7;
        const e = T.etat(); e.mefiance = 150; e.barre = (B.partie.jour || 0) + 7;
        const titre = aLaTable(L, o);
        let pipes = 0, refus = 0, joue = null;
        for (let k = 0; k < 200; k++) {
            e.mise = 1000; e.coups = 0;
            if (!choisir(L, o, 'MISER') || !T.enCours() || T.enCours().phase !== 'joue') { refus++; continue; }
            if (!joue) joue = lignes(L);
            if (T.enCours().pipes) pipes++;
            choisir(L, o, 'LANCER');
        }
        return { debut: debut, fuyard: fuyard, cravate: cravate, retour: retour, fait: fait, une: une, dites: dites, maitre: maitre,
                 argent: argent.map(function (a) { return a.montant; }), enHaut: enHaut, ici: ici, enBas: enBas,
                 bulle: bulle, titre: titre, pipes: pipes, refus: refus, joue: joue,
                 dans: B.interieur && B.interieur.slug };
    }""")
    assert r["debut"]["mission"] == "chute_du_pouce" and r["debut"]["etape"] == 9, r["debut"]
    assert r["debut"]["ligne"].startswith("LE CHAUFFEUR DU POUCE FILE"), r["debut"]
    assert r["fuyard"]["slug"] == "auto" and r["fuyard"]["dCasino"] <= 12, f"il file en char, du Dragon d'or : {r['fuyard']}"
    assert r["cravate"] == {"cravate": "cravates"}, f"son chauffeur est une Cravate qu'il paye : {r['cravate']}"
    assert r["retour"]["etape"] == 11 and r["retour"]["ligne"].startswith("RAPPORTE LA CAISSE"), r["retour"]
    for dite in ("pendant:irene:9", "pendant:irene:10", "pendant:pouce:11", "pendant:irene:11"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"][0] == 1500, "le chapitre fait : c04 aussi, et la prime de c04 (puis les gains de la table)"
    assert r["maitre"] == "retour_du_maitre", "le vieux maître arrive après c04 : Irène a le chapitre suivant"
    assert r["une"] == "pouce_parti", "le lendemain, le Clairon fait sa une de la chute du Pouce"
    assert r["enHaut"]["gros"] == 0, f"plus de gros bras à la porte d'en haut : {r['enHaut']}"
    assert r["ici"] == "nord_tripot" and r["dans"] == "nord_tripot", "la méfiance et la semaine barrée ne ferment plus rien"
    assert r["enBas"] == {"pouce": 0, "gros": 0, "chan": 1}, r["enBas"]
    assert r["bulle"] == tripot.REPRISE["bulle"], f"le vieux Chan le dit, quand on s'approche du feutre : {r['bulle']}"
    assert r["titre"] == tripot.REPRISE["titre"], r["titre"]
    assert r["refus"] == 0 and r["pipes"] == 0, f"repris, le tripot ne pipe plus jamais : {r['pipes']} pipés, {r['refus']} refus"
    assert r["joue"] == ["LANCER", "CHANGER DE CÔTÉ"], f"plus rien à dénoncer : {r['joue']}"


def test_avant_c04_le_pouce_pipe_encore_apres_jamais(banc):
    """Le témoin de la reprise : la MÊME partie, les mêmes coups — avant c04, le Pouce est là avec ses deux gros bras
    et pipe souvent à 1 000 $ ; c04 faite, on redescend, et c'est le vieux Chan, sans un pipé. (La mutation qui
    oublie `repris()` dans `miser` fait rougir ce juge.)"""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, T = L.Tripot;
        faites(L, AVANT.concat(['c01', 'c02', 'c03']));
        B.partie.argent = 1e7;
        function visite() {
            dansLaPorte(L, o, 'nord_casino'); descendre(L, o); jouer(L, o);
            const qui = ceuxDuTripot(L);
            aLaTable(L, o);
            const e = T.etat();
            let pipes = 0;
            for (let k = 0; k < 120; k++) {
                e.mise = 1000; e.coups = 0; e.mefiance = 0; e.propre = 0; e.total = k;
                choisir(L, o, 'MISER'); if (T.enCours() && T.enCours().pipes) pipes++; choisir(L, o, 'LANCER');
            }
            L.Hud.fermerMenu(); dehors(L, o);
            return { qui: qui, pipes: pipes };
        }
        const avant = visite();
        B.partie.missionsFaites.c04 = 1;
        const apres = visite();
        return { avant: avant, apres: apres };
    }""")
    assert r["avant"]["qui"] == {"pouce": 1, "gros": 2, "chan": 0}, r["avant"]
    assert r["avant"]["pipes"] >= 40, f"avant c04, le Pouce pipe six fois sur dix : {r['avant']}"
    assert r["apres"]["qui"] == {"pouce": 0, "gros": 0, "chan": 1}, r["apres"]
    assert r["apres"]["pipes"] == 0, r["apres"]


def test_acte_2_envoye_par_irene_le_pouce_pipe_chaque_grosse_mise(banc):
    """Martin, 29 sept. 2026 : « je ne vois que peu de dés jaunes pour la mission ». Hors mission, à 500 $, le Pouce
    pipe trois fois sur cinq, et une dénonciation le fait jouer propre trois coups. Envoyé par Irène (c02, la
    preuve pas encore en poche) : la table s'ouvre à 500 $, CHAQUE mise de 500 $ et plus voit ses dés jaunes — même
    juste après les avoir dénoncés —, et sous 500 $, jamais (l'`exige` de c02 tombé avec le chapitre, c'est lui qui
    tient l'acte : sans 500 $ à miser, pas de pipés à glisser)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur, T = L.Tripot; j.invincible = 1e6;
        faites(L, AVANT.concat(['c01']));
        B.partie.argent = 1e6;
        const serie = function (mise, n) {
            const e = T.etat(); let vus = 0;
            for (let k = 0; k < n; k++) {
                e.mise = mise; e.coups = 0; e.mefiance = 0;
                choisir(L, o, 'MISER');
                const t = T.enCours();
                if (t && t.pipes) vus++;
                choisir(L, o, 'LANCER');
            }
            return vus;
        };
        // Hors mission : le hasard du Pouce, et la paix après une dénonciation.
        dansLaPorte(L, o, 'nord_casino'); descendre(L, o); aLaTable(L, o);
        const miseHors = T.etat().mise;
        const hors = serie(500, 30);
        jusquAuxPipes(L, o); choisir(L, o, 'DÉNONCER LES DÉS');
        const apresDenonceHors = serie(1000, T.regles().pipes.propre);
        const ensuiteHors = serie(1000, 10);
        L.Hud.fermerMenu(); dehors(L, o);
        // Envoyé par Irène.
        T.etat().mise = 100; T.etat().propre = 0;
        const debut = commencerChezIrene(L, o);   // chez Irène, au bout du bar : l'acte 2 s'ouvre dehors
        dehors(L, o); jusqua(L, o, 4); dansLaPorte(L, o, 'nord_casino');
        jouer(L, o); descendre(L, o); aLaTable(L, o);
        const miseMission = T.etat().mise;
        const mission = serie(500, 12);
        const petite = serie(200, 12);
        T.etat().mise = 500; choisir(L, o, 'MISER'); choisir(L, o, 'DÉNONCER LES DÉS');
        const apresDenonce = serie(1000, 6);
        return { miseHors: miseHors, hors: hors, apresDenonceHors: apresDenonceHors, ensuiteHors: ensuiteHors, debut: debut.mission,
                 miseMission: miseMission, mission: mission, petite: petite, apresDenonce: apresDenonce,
                 preuve: (B.partie.objets || {}).des_pipes || 0 };
    }""")
    assert r["debut"] == "chute_du_pouce", r
    assert r["miseHors"] == tripot.MISES[0] and 10 <= r["hors"] < 30 and r["apresDenonceHors"] == 0, r
    assert r["ensuiteHors"] > 0, "après ses coups propres, le Pouce ne ressort plus ses pipés"
    assert r["miseMission"] == tripot.PIPES["seuil"], r
    assert r["mission"] == 12 and r["petite"] == 0 and r["apresDenonce"] == 6, r
    assert r["preuve"] == 0, "on n'a rien glissé : la mission attend toujours ses dés"
