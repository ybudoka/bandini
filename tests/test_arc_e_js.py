"""L'arc E jusqu'à sa libération (M16, 29 sept. 2026) — e04, e06, e07 et e10 JOUÉES au bouton, sur le modèle de
`test_arc_q_js.py`.

- e04, _La course des Chevreuils_ : Jo (qui n'est devant le dépanneur qu'après e01) lance son pilote en sport ; on
  le rattrape, ses clés tombent, on les rapporte — `calme: chevreuils`, et Jo s'en va se cacher chez les siens.
- e06, _Le maire ne dort pas chez lui_ : la berline du maire attend qu'on soit au volant, et on la file jusqu'à
  l'hôtel (`suivre`, collé derrière elle au pixel, comme `test_chute_du_pouce_js.py`).
- e07, _La clé de la villa_ : la clé est dans la poche du chauffeur (`pickpocket` + `objet: cle_villa`), puis la
  villa du maire comme v02 — le dossier du bureau d'en haut, sans une étoile.
- e10, _Diane veut la paix_ : deux coins de Chevreuils, leur chef, la police ; et **les Érables sont libérés, dans
  le monde** — leur cour redevient « Les Érables », le gang sort du jeu, et _Marco te vend_ (m97, trois districts)
  s'ouvre."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_infiltration_js import OUTILS as OUTILS_VILLA

AVANT_E = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01']"

#: Le fuyard d'un `ramasser` (le patron de `test_quatre_missions_js.py`).
RATTRAPER = """
  function rattraper(L, o) {
    const B = L.B, j = B.joueur, f = B.mission.fuyard;
    if (!f) return null;
    L.Vehicules.endommager(f, 999, j); jouer(L, o, 2);
    const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
    if (porteur) L.Entites.assommer(porteur);
    jouer(L, o, 2);
    const caisse = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
    if (caisse) { j.x = caisse.x; j.y = caisse.y; L.Entites.indexer(); }
    jouer(L, o);
    return !!caisse;
  }
"""


def test_e04_le_pilote_des_chevreuils_ses_cles_et_les_chevreuils_te_respectent(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RATTRAPER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6']);
        L.Jeu.retourTitre(); L.Jeu.commencer();
        const avant = { jo: !!L.Histoire.donneur('jo'), diane: !!L.Histoire.donneur('diane') };
        faites(L, ['e01']);
        L.Jeu.retourTitre(); L.Jeu.commencer();
        const j = B.joueur; j.invincible = 1e6;
        const apres = { jo: !!L.Histoire.donneur('jo'), diane: !!L.Histoire.donneur('diane') };
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('jo');
        commencer(L, o, 'e04'); jouer(L, o);
        const f = B.mission.fuyard, depart = f ? { x: f.x, y: f.y } : null;
        jouer(L, o, 300);
        const fuite = { etape: etape(L), slug: f && f.slug, ligne: L.Histoire.ligneObjectif(),
                        avance: f ? Math.round(Math.hypot(f.x - depart.x, f.y - depart.y) / 16) : 0 };
        const caisse = rattraper(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        aPied(L);
        const jo = L.Histoire.donneur('jo');
        j.x = jo.x - 16; j.y = jo.y; L.Entites.indexer();
        finir(L, o);
        const fait = !!p.missionsFaites.e04, calmes = p.calmes.slice();
        L.Jeu.retourTitre(); L.Jeu.commencer();
        return { avant: avant, apres: apres, dispo: dispo && dispo.slug, fuite: fuite, caisse: caisse, retour: retour,
                 dites: dites, fait: fait, argent: argent.map(function (a) { return a.montant; }), calmes: calmes,
                 joParti: !L.Histoire.donneur('jo'), dianeLa: !!L.Histoire.donneur('diane') };
    }""")
    assert r["avant"] == {"jo": False, "diane": False}, f"avant e01, personne devant le dépanneur : {r['avant']}"
    assert r["apres"] == {"jo": True, "diane": True}, r["apres"]
    assert r["dispo"] == "e04"
    assert r["fuite"]["etape"] == 0 and r["fuite"]["slug"] == "sport" and r["fuite"]["avance"] > 10, r["fuite"]
    assert r["caisse"] and r["retour"]["etape"] == 1 and r["retour"]["ligne"].startswith("RAPPORTE SES CLÉS"), r
    for dite in ("pendant:jo:0", "pendant:jo:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300] and r["calmes"] == ["chevreuils"], r
    assert r["joParti"] and r["dianeLa"], "Jo se cache chez les siens ; Diane reste au dépanneur"


def test_e06_la_berline_du_maire_filee_jusqu_a_l_hotel(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        faites(L, """ + AVANT_E + """);
        L.Jeu.retourTitre(); L.Jeu.commencer();
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('diane');
        commencer(L, o, 'e06'); jouer(L, o);
        const c = B.mission.suivi;
        const berline = { slug: c && c.slug, attend: c && c.attendLeJoueur, d: c ? Math.round(Math.hypot(c.x - j.x, c.y - j.y)) : null };
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const arret = L.Histoire.tuileDeRue(j.x, j.y, 10);
        const mien = L.Vehicules.creer('auto', arret.x, arret.y, CAP[arret.sens], { etat: 'stationne' });
        j.x = mien.x + 10; j.y = mien.y; L.Entites.indexer();
        L.Vehicules.monter(j, mien); L.Entites.indexer();
        let i = 0;
        for (; i < 20000 && B.partie.mission && B.partie.mission.etape === 0; i++) {
            if (!c.attendLeJoueur) {
                mien.x = c.x - Math.cos(c.angle) * 96; mien.y = c.y - Math.sin(c.angle) * 96;
                mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
            }
            o.frame(1); ecouter(L);
        }
        const h = L.Histoire.lieu('hotel');
        const file = { images: i, etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                       dHotel: Math.round(Math.hypot(h.x - c.x, h.y - c.y) / 16) };
        jouer(L, o);
        aPied(L);
        const d = L.Histoire.donneur('diane');
        j.x = d.x - 16; j.y = d.y; L.Entites.indexer();
        finir(L, o);
        return { dispo: dispo && dispo.slug, berline: berline, file: file, dites: dites, fait: !!B.partie.missionsFaites.e06,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "e06", "Diane donne e06 après les drifts de Ti-Paul"
    assert r["berline"]["slug"] == "luxe" and r["berline"]["attend"] is True, r["berline"]
    f = r["file"]
    assert f["etape"] == 1 and f["ligne"].startswith("RACONTE TOUT À DIANE"), f
    assert f["dHotel"] < 10 and f["images"] > 20 * 60, f"une vraie filature, jusqu'à l'hôtel : {f}"
    for dite in ("pendant:diane:0", "pendant:diane:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300]


def test_e07_la_cle_dans_la_poche_du_chauffeur_puis_le_dossier_du_maire(banc):
    r = banc("async function (L, o) {" + OUTILS_VILLA + """
        L.Jeu.commencer();
        const B = L.B;
        ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'e06'].forEach(function (s) { B.partie.missionsFaites[s] = 1; });
        L.Jeu.retourTitre(); L.Jeu.commencer();
        const j = B.joueur; j.invincible = 1e6;
        const dispo = L.Histoire.disponibleDe('diane');
        const avant = !!(B.partie.objets || {}).cle_villa;
        commencer(L, o, 'e07');
        const victime = B.mission.entites.find(function (e) { return e.pickpocket === true; });
        const t = { dispo: dispo && dispo.slug, avant: avant, victime: !!victime };
        victime.angle = 0; victime.etat = 'flane'; victime.vx = 0; victime.vy = 0;
        j.x = victime.x - 12; j.y = victime.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        t.vole = L.Combat.pickpocket(j);
        for (let k = 0; k < 6; k++) { o.frame(1); fermer(L); }
        t.apresVol = etat(L);
        nuit(L);
        t.entre = await entrerALaVilla(L, o);
        for (let k = 0; k < 6; k++) { o.frame(1); fermer(L); }
        t.trou = entrerParLeTrou(L, o);
        t.service = aller(L, o, { x: 20, y: 32 }, 20000, function () { return etape(L) >= 3; });
        t.dossier = aller(L, o, lieu(L, 'villa_bureau'), 60000, function () { return etape(L) >= 4; });
        t.apresDossier = etat(L);
        t.sortie = ressortir(L, o, function () { return etape(L) >= 5; });
        t.dehors = sortirDeLaVilla(L, o);
        const d = L.Histoire.donneur('diane');
        if (d) { j.x = d.x - 16; j.y = d.y; L.Entites.indexer(); }
        for (let k = 0; k < 400 && B.partie.mission; k++) { o.frame(1); fermer(L); }
        t.fait = !!B.partie.missionsFaites.e07;
        t.dossierGarde = (B.partie.objets || {}).dossier_maire || 0;
        return t;
    }""")
    assert r["dispo"] == "e07" and r["avant"] is False and r["victime"], r
    assert r["apresVol"]["etape"] == 1 and r["apresVol"]["objets"].get("cle_villa") == 1, (
        f"la clé de la porte de service vient de la poche du chauffeur : {r['apresVol']}")
    assert r["entre"] and r["trou"] is True, r
    assert r["service"] is True and r["dossier"] is True, r
    assert r["apresDossier"]["objets"].get("dossier_maire") == 1 and r["apresDossier"]["etoiles"] == 0, r
    assert r["sortie"] is True and r["dehors"], r
    assert r["fait"] is True and r["dossierGarde"] == 1, "le dossier reste au sac (e11, c02)"


def test_e10_deux_coins_leur_chef_puis_les_erables_sont_libres_et_marco_peut_vendre(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        // ⚠️ m97 exige la fin de l'arc F (f12, Martin, 29 sept. 2026) : elle est faite, pour que « Marco peut
        // vendre » ne tienne qu'aux districts.
        faites(L, """ + AVANT_E + """.concat(['e04', 'e06', 'e07', 'f01', 'f02', 'f03', 'f06', 'f08', 'f09', 'f10', 'f12']));
        L.Jeu.retourTitre(); L.Jeu.commencer();
        const B = L.B, p = B.partie, j = B.joueur; j.invincible = 1e6;
        p.libere = ['faubourg', 'quais']; p.faubourgLibere = true;
        const T = L.Territoires, d = T.donnees();
        const aShop = Object.keys(d.ilots).find(function (k) { return d.ilots[k].gang === 'boulonneux' && !d.ilots[k].coeur; });
        p.territoires = {}; p.territoires[aShop] = 'chevreuils';
        const marcoAvant = L.Histoire.disponibles().some(function (m) { return m.slug === 'm97'; });
        const argent = paiements(L);
        const dispo = L.Histoire.disponibleDe('diane');
        commencer(L, o, 'e10'); jouer(L, o);
        const cour = L.Histoire.resoudre('zone:chevreuils', null), dep = L.Histoire.lieu('depanneur');
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 0; });
        const coins = { n: eux.length, coins: eux.map(function (e) { return e.coin; }).filter(function (c, k, t) { return t.indexOf(c) === k; }).length,
                        cour: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - cour.x, e.y - cour.y) / 16); })),
                        dep: Math.min.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - dep.x, e.y - dep.y) / 16); })) };
        j.x = cour.x; j.y = cour.y; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const chef = B.mission.entites.find(function (e) { return e.cible && e.etape === 1; });
        const leChef = { etape: etape(L), chef: !!(chef && chef.chef), ligne: L.Histoire.ligneObjectif() };
        L.Entites.assommer(chef); jouer(L, o);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        const di = L.Histoire.donneur('diane');
        j.x = di.x - 16; j.y = di.y; L.Entites.indexer();
        finir(L, o);
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs);
        return { marcoAvant: marcoAvant, dispo: dispo && dispo.slug, coins: coins, leChef: leChef, semer: semer, cache: cache,
                 dites: dites, fait: !!p.missionsFaites.e10, argent: argent.map(function (a) { return a.montant; }),
                 libere: p.libere.slice(), relue: relue.libere, manchette: p.manchetteForcee || null,
                 chasse: L.Entites.gangChasse('chevreuils'), horsJeu: T.horsJeu('chevreuils'), rendu: p.territoires[aShop] || null,
                 nom: L.Hud.nomIci(j, L.Monde.zoneA(cour.x, cour.y)),
                 marco: L.Histoire.disponibles().some(function (m) { return m.slug === 'm97'; }) };
    }""")
    assert r["marcoAvant"] is False, "avec deux districts, Marco n'a pas encore de raison de te vendre"
    assert r["dispo"] == "e10", "Diane donne e10 après la course de Jo et le dossier"
    c = r["coins"]
    assert c["n"] == 6 and c["coins"] == 2 and c["cour"] <= 14 and c["dep"] > 20, f"six Chevreuils, deux coins, loin du dépanneur : {c}"
    assert r["leChef"]["etape"] == 1 and r["leChef"]["chef"] and r["leChef"]["ligne"].startswith("LEUR CHEF ARRIVE"), r["leChef"]
    assert r["semer"]["etape"] == 2 and r["semer"]["etoiles"] >= 2 and r["cache"]["apres"] == 0, r
    for dite in ("pendant:diane:0", "pendant:diane:1", "pendant:diane:2", "pendant:diane:3"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [600]
    assert r["libere"] == ["faubourg", "quais", "erables"] and r["relue"] == r["libere"], r
    assert r["manchette"] == "erables_liberes"
    assert r["chasse"] and r["horsJeu"] and r["rendu"] is None, "les Chevreuils sortent du jeu et rendent leur coin"
    assert r["nom"] == {"nom": "Les Érables", "gang": None}, r["nom"]
    assert r["marco"] is True, "trois districts libérés : Marco te vend (m97, M13)"
