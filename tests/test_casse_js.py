"""Le casse de la caisse populaire (M16, arc X, vague 15, 1er oct. 2026) — x01 à x04 JOUÉES au bouton, et la caisse.

- x01 : la caisse vue de dehors, la voûte regardée de près (le plan dans le sac), le fourgon filé jusqu'à Mado.
- x02 : le coupé du touriste volé, refusé à la planque tant qu'il n'est pas repeint, puis livré repeint.
- x03 : l'uniforme de livreur enfilé chez Rosa, le gérant qui ne signe que pour un livreur, Fernand qui salue, Rosa.
- x04 : le coup, dans les deux combinaisons extrêmes — tout préparé (l'uniforme, le coupé dans la ruelle) et rien
  (Fernand qui reconnaît, deux étoiles à l'entrée, le coupé qui n'existe pas) : la minuterie, les gardes du fourgon,
  les sacs, quatre étoiles semées, Josée — et la dernière coupe de Sal fermée.

⚠️ Dans la caisse, `majObjectif` dort : chaque objet entre au sac DEDANS (`caisse.js`) et l'objectif avance à la
sortie. Le joueur est invincible (`recharger`) : on juge l'enchaînement, pas la bagarre.
"""

import json

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_d_js import CHEZ_JOSEE
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER

from app import missions

#: Tout le catalogue avant le casse — Josée et Rosa n'ont plus que lui à donner.
AVANT = json.dumps([m["slug"] for m in missions.CATALOGUE
                    if not m["slug"].startswith("x0") and m["slug"] not in ("m97", "m98", "m99")])

CAISSE = """
  // Ce que Josée DIT (le texte des répliques `pendant`), pour juger les `si`/`sauf`.
  const textes = [];
  const ecouter0 = ecouter;
  ecouter = function (L) { if (L.B.cinema && L.B.cinema.partie === 'pendant') L.B.cinema.lignes.forEach(function (l) { if (textes.indexOf(l.texte) < 0) textes.push(l.texte); }); ecouter0(L); };
  function aLaCaisse(L, o) { const c = L.Histoire.lieu('caisse_pop'), j = L.B.joueur; aPied(L); j.x = c.x; j.y = c.y; L.Entites.indexer(); jouer(L, o, 10); }
  // Devant la voûte, la face au mur, et ACTION au bouton.
  function aLaVoute(L, o) {
    const v = L.B.interieur.points.find(function (q) { return q.type === 'voute'; }), j = L.B.joueur;
    j.x = v.x * 16 + 8; j.y = (v.y + 1) * 16 + 8; j.face = 'haut'; j.angle = -Math.PI / 2; L.Entites.indexer();
    o.frame(1); j.face = 'haut'; j.angle = -Math.PI / 2;
  }
  function action(L, o) { L.Missions.majInvite(L.B.joueur); const inv = L.B.invite; o.tape('KeyE', 2); return inv; }
  function vigile(L) { return L.B.entites.find(function (e) { return e.vigile; }) || null; }
"""


def test_x01_le_reperage_la_voute_puis_le_fourgon_jusqu_a_mado(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_JOSEE + CAISSE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT + """);
        const j = recharger(L);
        const argent = paiements(L);
        const chez = chezJosee(L, o);
        aLaCaisse(L, o);
        const arrive = etape(L);
        const piece = dedans(L, o, 'caisse_pop');
        aLaVoute(L, o);
        const avant = !!(p.objets && p.objets.plan_caisse);
        jouer(L, o, 150);
        const plan = !!(p.objets && p.objets.plan_caisse);
        const encore = etape(L);
        sortir(L, o);
        const c = B.mission.suivi;
        const fourgon = { etape: etape(L), slug: c && c.slug, attend: c && c.attendLeJoueur };
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const arret = L.Histoire.tuileDeRue(j.x, j.y, 10);
        const mien = L.Vehicules.creer('auto', arret.x, arret.y, CAP[arret.sens], { etat: 'stationne' });
        j.x = mien.x + 10; j.y = mien.y; L.Entites.indexer();
        L.Vehicules.monter(j, mien); L.Entites.indexer();
        let i = 0;
        for (; i < 30000 && p.mission && p.mission.etape === 2; i++) {
          if (!c.attendLeJoueur) {
            mien.x = c.x - Math.cos(c.angle) * 110; mien.y = c.y - Math.sin(c.angle) * 110;
            mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
          }
          o.frame(1); ecouter(L);
        }
        const m = L.Histoire.lieu('casse_croute');
        const file = { images: i, dMado: Math.round(Math.hypot(m.x - c.x, m.y - c.y) / 16) };
        finir(L, o);
        return { chez: chez, arrive: arrive, piece: piece, avant: avant, plan: plan, encore: encore, fourgon: fourgon,
                 file: file, dites: dites, fait: !!p.missionsFaites.x01, argent: argent.map(function (a) { return a.montant; }),
                 ouvertes: ['x02', 'x03', 'x04'].map(function (s) { return L.Histoire.disponibles().some(function (q) { return q.slug === s; }); }) };
    }""")
    assert r["chez"]["mission"] == "x01", r["chez"]
    assert r["arrive"] == 1 and r["piece"] == "caisse_pop", r
    assert r["avant"] is False and r["plan"] is True, "le plan entre au sac après deux secondes devant la voûte"
    assert r["encore"] == 1, "dedans, l'objectif dort : il avance à la sortie"
    assert r["fourgon"] == {"etape": 2, "slug": "camion", "attend": True}, r["fourgon"]
    assert r["file"]["dMado"] < 12 and r["file"]["images"] > 10 * 60, r["file"]
    for dite in ("pendant:josee:0", "pendant:josee:1", "pendant:josee:2"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [100], r
    assert r["ouvertes"] == [True, True, True], "le repérage ouvre les deux préparatifs et le coup"


def test_x02_le_coupe_ne_se_livre_que_repeint(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_JOSEE + CAISSE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT + """.concat(['x01']));
        const j = recharger(L);
        const argent = paiements(L);
        serrer(L, o, 'gus'); passer(L, o); ecouter(L);
        const chez = { mission: p.mission ? p.mission.slug : null };
        const v = B.mission.vehicule;
        const h = L.Histoire.lieu('hotel');
        const coupe = { slug: v && v.slug, hotel: v ? Math.round(Math.hypot(v.x - h.x, v.y - h.y) / 16) : null };
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const vole = { etape: etape(L), etoiles: B.recherche.etoiles };
        const baie = L.Histoire.lieuDeLivraison('planque');
        v.x = baie.x; v.y = baie.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); jouer(L, o, 20);
        const refuse = { etape: etape(L), attend: B.mission.attend };
        L.Missions.repeindre(v); jouer(L, o, 20);
        finir(L, o);
        return { chez: chez, coupe: coupe, vole: vole, refuse: refuse, dites: dites, fait: !!p.missionsFaites.x02,
                 etoiles: B.recherche.etoiles, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "x02", r["chez"]
    assert r["coupe"]["slug"] == "sport" and r["coupe"]["hotel"] <= 14, r["coupe"]
    assert r["vole"] == {"etape": 1, "etoiles": 2}, r["vole"]
    assert r["refuse"]["etape"] == 1 and r["refuse"]["attend"].startswith("FAIS-LE REPEINDRE"), r["refuse"]
    assert r["fait"] is True and r["argent"] == [150] and r["etoiles"] == 0, r
    for dite in ("pendant:gus:0", "pendant:gus:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"


def test_x03_l_uniforme_le_gerant_signe_pour_un_livreur_et_fernand_salue(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CAISSE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT + """.concat(['x01']));
        const j = recharger(L);
        const argent = paiements(L);
        const appel = serrer(L, o, 'rosa'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        const au_sac = p.tenues.indexOf('livreur') >= 0;
        dedans(L, o, 'vetements');
        const porte = enfiler(L, 'UNIFORME DE LIVREUR');
        sortir(L, o);
        const enfile = etape(L);
        aLaCaisse(L, o);
        const arrive = etape(L);
        dedans(L, o, 'caisse_pop'); jouer(L, o, 4);
        const salut = (vigile(L) || {}).bulle || null;
        const g = B.entites.find(function (e) { return e.gerant; });
        function chezLeGerant() { j.x = g.x + 16; j.y = g.y; j.face = 'gauche'; j.angle = Math.PI; L.Entites.indexer(); o.frame(1); j.face = 'gauche'; j.angle = Math.PI; }
        p.tenue = 'chandail';
        chezLeGerant(); const invite = action(L, o);
        const refuse = !!(p.objets && p.objets.bordereau);
        p.tenue = 'livreur';
        chezLeGerant(); action(L, o);
        const signe = !!(p.objets && p.objets.bordereau);
        const bulle = g.bulle || null;
        sortir(L, o);
        const rapporte = etape(L);
        versLui(L, 'rosa'); finir(L, o);
        return { mission: mission, au_sac: au_sac, porte: porte, enfile: enfile, arrive: arrive, salut: salut, invite: invite,
                 refuse: refuse, signe: signe, bulle: bulle, rapporte: rapporte, dites: dites, fait: !!p.missionsFaites.x03,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "x03" and r["au_sac"] is True, r
    assert r["porte"] == "livreur" and r["enfile"] == 1 and r["arrive"] == 2, r
    assert r["salut"] and "SALUT" in r["salut"]["texte"], f"Fernand salue un livreur : {r['salut']}"
    assert r["invite"] == "LIVRER LE COLIS", r["invite"]
    assert r["refuse"] is False and r["signe"] is True, "le gérant ne signe que pour un livreur"
    assert r["rapporte"] == 3, r
    for dite in ("pendant:rosa:0", "pendant:rosa:1", "pendant:rosa:2", "pendant:rosa:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [100], r


COUP = """
  // Le coup, de la porte du bar à Josée : rend ce qu'on a vu à chaque étape.
  function coup(L, o, uniforme) {
    const B = L.B, p = B.partie, j = B.joueur;
    if (uniforme) { p.tenues.push('livreur'); p.tenue = 'livreur'; }
    const argent = paiements(L);
    const chez = chezJosee(L, o);
    const coupe = B.mission.chars && B.mission.chars[2] ? B.mission.chars[2].slug : null;
    aLaCaisse(L, o);
    const arrive = etape(L);
    dedans(L, o, 'caisse_pop');
    o.frame(2);
    const f = vigile(L);
    const entree = { etoiles: B.recherche.etoiles, vigile: f && f.etat };
    aLaVoute(L, o);
    const invite = action(L, o);
    const alarme = { phase: L.Caisse.etat().phase, etoiles: B.recherche.etoiles };
    let i = 0, colle = 1e9, fernand = 1e9;
    for (; i < 4200 && L.Caisse.etat().phase === 'minuterie'; i++) {
      o.frame(1); j.vie = j.vieMax;
      B.entites.forEach(function (e) {
        if (!e.vivant) return;
        const d = Math.hypot(e.x - j.x, e.y - j.y);
        if (e.gardeDuFourgon) colle = Math.min(colle, d);
        if (e.vigile) fernand = Math.min(fernand, d);
      });
    }
    const gardes = B.entites.filter(function (e) { return e.gardeDuFourgon; }).length;
    const tenu = { images: i, phase: L.Caisse.etat().phase, etoiles: B.recherche.etoiles, colle: Math.round(colle), fernand: Math.round(fernand) };
    aLaVoute(L, o);
    const prendre = action(L, o);
    const sacs = !!(p.objets && p.objets.sacs_caisse);
    sortir(L, o);
    const dehors = { etape: etape(L), etoiles: B.recherche.etoiles, vehicule: B.mission.vehicule && B.mission.vehicule.slug };
    if (etape(L) === 2) {
      const v = B.mission.vehicule;
      j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
    }
    const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
    const cache = seCacher(L, o);
    const b = L.Histoire.lieu('bar'); aPied(L); j.x = b.x; j.y = b.y; L.Entites.indexer(); jouer(L, o, 10);
    const auBar = etape(L);
    dedans(L, o, 'bar'); serrer(L, o, 'josee'); finir(L, o);
    return { chez: chez, coupe: coupe, arrive: arrive, entree: entree, invite: invite, alarme: alarme, tenu: tenu,
             gardes: gardes, prendre: prendre, sacs: sacs, dehors: dehors, semer: semer, cache: cache, auBar: auBar,
             textes: textes, fait: !!p.missionsFaites.x04, fermees: p.fermees,
             argent: argent.map(function (a) { return a.montant; }) };
  }
"""


def _coup(banc, faites, uniforme):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_JOSEE + CAISSE + COUP + """
        L.Jeu.commencer(); L.graine(6);
        faites(L, """ + AVANT + """.concat(""" + json.dumps(faites) + """));
        recharger(L);
        return coup(L, o, """ + ("true" if uniforme else "false") + """);
    }""")


def _commun(r):
    assert r["chez"]["mission"] == "x04", r["chez"]
    assert r["arrive"] == 1, r
    assert r["invite"] == "LA MINUTERIE!", r["invite"]
    assert r["alarme"]["phase"] == "minuterie" and r["alarme"]["etoiles"] >= 3, r["alarme"]
    assert r["tenu"]["phase"] == "ouverte" and 59 * 60 <= r["tenu"]["images"] <= 61 * 60, r["tenu"]
    assert r["tenu"]["etoiles"] >= 3, "dans la caisse, l'alarme sonne : on ne se fait pas oublier"
    assert r["gardes"] == 6, f"trois vagues de deux gardes du fourgon : {r['gardes']}"
    # ⚠️ Ils VIENNENT jusqu'à toi, derrière le comptoir (par la porte battante) — collés au comptoir, la minute ne
    # coûtait rien.
    assert r["tenu"]["colle"] <= 20 and r["tenu"]["fernand"] <= 20, r["tenu"]
    assert r["prendre"] == "PRENDRE LES SACS" and r["sacs"] is True, r
    assert r["semer"]["etoiles"] == 4 and r["cache"]["apres"] == 0, r
    assert r["auBar"] == 5, r
    assert r["fait"] is True and r["argent"] == [2500], r
    assert "d08" in r["fermees"], "le casse ferme la dernière coupe de Sal"


def test_x04_tout_prepare_l_uniforme_ouvre_la_porte_et_le_coupe_attend(banc):
    r = _coup(banc, ["x01", "x02", "x03"], uniforme=True)
    _commun(r)
    assert r["coupe"] == "sport", "le coupé du x02 attend dans la ruelle"
    assert r["entree"] == {"etoiles": 0, "vigile": "fige"}, f"en livreur, Fernand ne bronche pas : {r['entree']}"
    assert r["dehors"]["etape"] == 2 and r["dehors"]["vehicule"] == "sport", r["dehors"]
    assert r["semer"]["etape"] == 3, r
    assert any("l'uniforme de Rosa" in t for t in r["textes"]) and any("coupé repeint" in t for t in r["textes"]), r["textes"]
    assert not any(t.startswith("Pas d'uniforme") or t.startswith("Pas de char") for t in r["textes"]), r["textes"]


def test_x04_rien_de_prepare_fernand_reconnait_et_on_seme_avec_ce_qui_roule(banc):
    r = _coup(banc, ["x01"], uniforme=False)
    _commun(r)
    assert r["coupe"] is None, "sans x02, aucun coupé ne naît"
    assert r["entree"]["etoiles"] == 2 and r["entree"]["vigile"] == "attaque_joueur", \
        f"sans uniforme, Fernand reconnaît et l'alarme sonne : {r['entree']}"
    assert r["dehors"]["etape"] == 3, "l'objectif `monter` du coupé se saute (`si: x02`)"
    assert any(t.startswith("Pas d'uniforme") for t in r["textes"]) and any(t.startswith("Pas de char") for t in r["textes"]), r["textes"]
    assert not any("coupé repeint" in t for t in r["textes"]), r["textes"]


def test_qui_doit_changer_de_cote_du_comptoir_passe_par_la_porte_battante(banc):
    """Un piéton ne cherche pas son chemin : le vigile, de l'autre bord du comptoir des guichets, y restait collé
    (vu en capture, la minute du coup ne coûtait rien). `caisse.js` le fait passer par la porte battante. Le joueur
    se tient derrière les guichets, au bout opposé à la battante ; Fernand, en colère, part de la salle d'attente."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = recharger(L);
        dedans(L, o, 'caisse_pop'); o.frame(2);
        const b = B.interieur.battante, f = B.entites.find(function (e) { return e.vigile; });
        const loin = b.x <= 2 ? B.interieur.largeur - 3 : 2;           // l'autre bout du comptoir, derrière
        j.x = loin * 16 + 8; j.y = (b.y - 1) * 16 + 8;
        f.x = loin * 16 + 8; f.y = (b.y + 2) * 16 + 8; f.plante = null; f.poste = null; f.etat = 'attaque_joueur';
        L.Entites.indexer();
        let d = 1e9;
        for (let i = 0; i < 900; i++) { o.frame(1); j.vie = j.vieMax; j.x = loin * 16 + 8; j.y = (b.y - 1) * 16 + 8; d = Math.min(d, Math.hypot(f.x - j.x, f.y - j.y)); }
        return { d: Math.round(d), passe: f.y < b.y * 16 };
    }""")
    assert r["passe"] is True and r["d"] <= 20, f"Fernand est resté collé au comptoir : {r}"
