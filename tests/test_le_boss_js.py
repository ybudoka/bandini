"""M13 — _Le Boss_ (m98), JOUÉE au banc : de l'appel au générique, puis la ville d'après.

Quatre districts libérés et quatre propriétés : le téléphone sonne, c'est Josée. Au Brouillard, ACTION devant
elle — l'intro ; dehors, les Cravates du maire arrivent, et **les Morues, les Skateux et les Boulonneux à tes
côtés** (`allies`) en couchent pour toi sans jamais te toucher ; puis la police du maire, à cinq étoiles
(`survivre` + `etoiles`) ; Bouchard rappelle ses chiens (`treve`) ; la garde du maire devant l'Hôtel Bandini ; la
chambre, où le maire Tanguay se présente à la poignée de main, rend le billet de Rocco et s'en va. Puis le
générique — le narrateur, la musique à lui, les chiffres et « DÉCHIRÉE » —, le BILAN, et **la ville qui a changé de
couleur** : les gangs revenus à tes couleurs, les saluts, plus de rixe aux frontières, la carte à l'or des
Bandini, le Clairon, et la sauvegarde qui garde tout ça.

Un seul banc joue la partie (`_partie`, une minute de Node) ; chaque juge en lit un morceau.
"""

import json

import pytest

from app import missions, pietons
from outils_missions import OUTILS, PLUS_LONGUES, outils
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER

AVANT = json.dumps([s for s in missions.ordre_topologique() if s not in ("m98", "m99")])

#: Une partie qui a tout fait avant m98 : les cinq districts libres, les quatre propriétés (l'hôtel compris),
#: la dette de Rocco encore due — et pas de quoi sacrer son camp (m99 demande 15 000 $).
PREPARER = """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT + """);
        p.libere = ['faubourg', 'quais', 'erables', 'pointe', 'shop']; p.faubourgLibere = true;
        p.enVente = ['hotel'];
        ['kiosque', 'bar', 'garage', 'hotel'].forEach(function (s) { p.proprietes[s] = { jour: 1, caisse: 0 }; });
        p.argent = 3000; p.dette = 15000;
"""


@pytest.fixture(scope="module")
def _partie(banc):
    return banc("function (L, o) {" + OUTILS + outils("coucher", "images") + PLUS_LONGUES + RECHARGER + DEDANS
                + PREPARER + """
        const j = recharger(L);
        const out = { dispo: L.Histoire.disponibles().map(function (m) { return m.slug; }) };
        // --- L'appel : le téléphone sonne tout seul.
        let n = 0;
        for (; n < 4000 && !(B.cinema && B.cinema.partie === 'appel'); n++) o.frame(1);
        out.appel = { mission: B.cinema && B.cinema.mission, qui: B.cinema && B.cinema.lignes[0].qui };
        ecouter(L); jouer(L, o);
        // --- Au Brouillard, ACTION devant Josée : l'intro se JOUE (une scène), puis la mission.
        dedans(L, o, 'bar');
        serrer(L, o, 'josee');
        let scene = 0, k = 0;
        for (; k < 5000 && (B.scene || B.cinema); k++) { if (B.scene) scene++; o.frame(1); ecouter(L); }
        out.intro = { scene: scene, mission: p.mission && p.mission.slug, etape: etape(L) };
        // --- 0 → 1 : on sort ; les Cravates du maire arrivent, les alliés aussi, de l'autre bout de la rue.
        sortir(L, o); jouer(L, o, 10);
        const allies = (B.mission.allies || []).slice();
        out.siege = { etape: etape(L), allies: allies.map(function (e) { return e.gang; }).sort(),
                      etats: allies.map(function (e) { return e.etat; }),
                      cibles: B.mission.entites.filter(function (e) { return e.cible && e.etape === 1; }).length };
        // Ce que les alliés frappent : les hommes du maire, jamais toi ni l'un des leurs.
        const coups = [], vrai = L.Entites.blesser;
        L.Entites.blesser = function (e, d, s) {
          if (s && s.allie) coups.push(e.type === 'joueur' ? 'joueur' : (e.cible ? 'cible' : (e.allie ? 'allie' : 'autre')));
          return vrai.apply(null, arguments);
        };
        j.invincible = 1e6;
        for (let q = 0; q < 1500 && etape(L) === 1; q++) { o.frame(1); ecouter(L); }
        L.Entites.blesser = vrai;
        out.combat = { cible: coups.filter(function (c) { return c === 'cible'; }).length,
                       autres: coups.filter(function (c) { return c !== 'cible'; }), kos: B.mission.kos };
        // Rien ne les retourne contre toi : un coup que TU portes près d'eux (`alerter`), ni un coup qu'ils prennent.
        const a0 = allies.find(function (e) { return e.vivant && e.etat !== 'assomme'; });
        const cravate = B.mission.entites.find(function (e) { return e.cible && e.vivant && e.etat !== 'assomme'; });
        if (a0) {
          L.Entites.alerter(a0.x, a0.y, j, 2);
          // ⚠️ Pris en plein geste contre un Cravate (les allies frappent a leur echeance, plus au metronome) : on
          // lit l'etat d'avant le coup, comme pour `blesse` — un allie retourne contre toi lirait `attaque_joueur`.
          const apresAlerte = a0.etat === 'attaque' ? a0.avantLeCoup : a0.etat;
          if (cravate) L.Entites.blesser(a0, 1, cravate);
          out.fideles = { alerte: apresAlerte, blesse: a0.etat === 'attaque' ? a0.avantLeCoup : a0.etat };
        }
        coucher(L, o); jouer(L, o, 5);
        // --- 2 : la police du maire, à cinq étoiles — les alliés restent.
        out.police = { etape: etape(L), etoiles: B.recherche.etoiles, allies: (B.mission.allies || []).length };
        for (let q = 0; q < 600; q++) { o.frame(1); ecouter(L); }
        out.police.tient = { etape: etape(L), etoiles: B.recherche.etoiles };
        p.mission.debutT = B.t - 90 * 60; jouer(L, o, 5);
        // --- 3 : Bouchard rappelle ses chiens ; les alliés rentrent chez eux.
        out.treve = { etape: etape(L), etoiles: B.recherche.etoiles, allies: B.mission.allies || null,
                      rentres: allies.filter(function (e) { return !e.allie && !e.mission; }).length };
        const h = L.Histoire.lieu('hotel');
        j.x = h.x; j.y = h.y + 10; L.Entites.indexer(); jouer(L, o, 10);
        // --- 4 : la garde du maire devant ta porte.
        const gardes = B.mission.entites.filter(function (e) { return e.cible && e.etape === 4; });
        out.garde = { etape: etape(L), n: gardes.length, arch: gardes.map(function (e) { return e.arch; }) };
        for (let q = 0; q < 120; q++) { o.frame(1); ecouter(L); }
        coucher(L, o); jouer(L, o, 5);
        const gps = L.Histoire.cible();
        out.chambre = { etape: etape(L), gps: gps ? Math.round(Math.hypot(gps.x - h.x, gps.y - h.y)) : null };
        // --- 5 : l'escalier du hall, la chambre ; le maire est là.
        dedans(L, o, 'hotel');
        L.Jeu.changerEtage('hotel_chambre'); o.fondu();
        for (let q = 0; q < 200 && !(B.interieur && B.interieur.slug === 'hotel_chambre'); q++) o.frame(1);
        out.chambre.piece = B.interieur && B.interieur.slug;
        out.chambre.maire = !!L.Histoire.donneur('maire');
        // ACTION devant lui, au bouton — et on regarde tout jusqu'au BILAN, sans rien passer que les boîtes.
        const m = L.Histoire.donneur('maire');
        j.x = m.x - 16; j.y = m.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        o.frame(1); j.angle = 0; j.face = 'droite'; L.Missions.majInvite(j); o.tape('KeyE', 2);
        const vus = { lignes: [], cartons: [], musique: null, anonyme: true, maireParti: false, generique: false };
        let vu = null, g = 0;
        const gen = B.defs.missions.find(function (q) { return q.slug === 'm98'; }).scenes.generique;
        for (; g < 15000 && (B.scene || B.cinema || B.generiqueEnAttente || B.finEnAttente); g++) {
          const c = B.cinema, l = c && c.lignes[Math.max(0, c.i)];
          if (l && vu !== c.lignes.indexOf(l) + ':' + l.slug) {
            vu = c.lignes.indexOf(l) + ':' + l.slug;
            vus.lignes.push(l.qui + (l.telephone ? '@' : ''));
            if (l.qui === 'narrateur' && !c.anonyme) vus.anonyme = false;
          }
          if (B.scene && B.scene.plans === gen) vus.generique = true;
          if (B.scene && B.scene.carton && B.scene.carton.texte && vus.cartons.indexOf(B.scene.carton.texte) < 0) vus.cartons.push(B.scene.carton.texte);
          if (B.scene && B.scene.carton && B.scene.carton.logo && vus.cartons.indexOf('LOGO:' + B.scene.carton.sous) < 0) vus.cartons.push('LOGO:' + B.scene.carton.sous);
          if (B.scene && B.scene.musique && !vus.musique) vus.musique = B.scene.musique;
          if (B.generiqueEnAttente && !L.Histoire.donneur('maire')) vus.maireParti = true;
          o.frame(1);
          if (c && g % 20 === 0) L.Histoire.suivante();
        }
        out.fin = { vus: vus, menu: B.menu ? B.menu.titre : null, faite: !!p.missionsFaites.m98,
                    boss: p.boss, fins: Object.keys(p.fins || {}), dette: p.dette, manchette: p.manchetteForcee };
        // --- La ville d'après. On ferme le BILAN et on sort ; le maire n'est plus dans sa chambre.
        L.Hud.fermerMenu();
        L.Jeu.quitterLaPiece(); o.fondu();
        for (let q = 0; q < 200 && B.interieur; q++) o.frame(1);
        out.apres = { dehors: !B.interieur };
        dedans(L, o, 'hotel'); L.Jeu.changerEtage('hotel_chambre'); o.fondu();
        for (let q = 0; q < 200 && !(B.interieur && B.interieur.slug === 'hotel_chambre'); q++) o.frame(1);
        out.apres.chambre = B.interieur && B.interieur.slug;
        out.apres.maire = !!L.Histoire.donneur('maire');
        L.Jeu.quitterLaPiece(); o.fondu();
        for (let q = 0; q < 200 && B.interieur; q++) o.frame(1);
        // Dans la cour des Morues : elles sont revenues, à tes couleurs.
        const z = L.Monde.carte.zones.find(function (q) { return q.slug === 'morues'; });
        const t = L.Histoire.tuileLibre((z.x + z.l / 2) * 16 + 8, (z.y + z.h / 2) * 16 + 8, 8);
        j.x = t.x; j.y = t.y; L.Entites.indexer();
        images(L, o, 900);
        const or = B.defs.pietons.boss.couleur;
        const morues = B.entites.filter(function (e) { return e.type === 'pieton' && e.gang === 'morues' && e.vivant && !e.cible; });
        out.apres.morues = { n: morues.length, or: morues.filter(function (e) { return e.swaps && e.swaps.c === or; }).length };
        out.apres.nom = L.Hud.nomIci(j);
        // On te salue : des passants posés à deux pas, un par un, puis un membre des Morues.
        function salut(arch, dore) {
          for (let q = 0; q < 24; q++) {
            const w = L.Histoire.tuileLibre(j.x + 20, j.y, 3);
            const e = L.Entites.creerPieton(w.x, w.y, L.Entites.archetype(arch));
            e.etat = 'arret'; e.minuterie = 4000; if (dore) L.Entites.auxCouleursDuBoss(e);
            L.Entites.indexer();
            B.salutBossT = 0;
            images(L, o, 12);
            if (e.bulle) return e.bulle.texte;
            L.Entites.retirer(e);
          }
          return null;
        }
        out.apres.salut = { passant: salut('passant', false), morue: salut('morue', true) };
        // Plus de rixe aux frontières — et le banc sait en allumer une quand on n'est pas boss.
        const f = B.defs.pietons.bagarre, chance = f.chance_par_minute;
        f.chance_par_minute = 1;
        const ligne = B.defs.pietons.frontieres[0];
        const vert = ligne.axe === 'v', mi = (vert ? ligne.y : ligne.x) + Math.floor(ligne.long / 2);
        const cx = (vert ? ligne.x : mi) * 16 + 8, cy = (vert ? mi : ligne.y) * 16 + 8;
        let place = null;
        for (let r = 22; r <= 30 && !place; r++) {
          for (let a = 0; a < 16 && !place; a++) {
            const q = L.Histoire.tuileLibre(cx + Math.cos(a * Math.PI / 8) * r * 16, cy + Math.sin(a * Math.PI / 8) * r * 16, 1);
            if (q && L.Entites.frontiereProche(q.x, q.y, f)) place = q;
          }
        }
        j.x = place.x; j.y = place.y; L.Entites.indexer();
        B.rixeMinute = null; const rixeBoss = L.Entites.majBagarre();
        const boss = p.boss; p.boss = null;
        B.rixeMinute = null; const rixeAvant = L.Entites.majBagarre();
        p.boss = boss; f.chance_par_minute = chance;
        out.apres.rixe = { boss: rixeBoss, sans: rixeAvant };
        // La grande carte : les districts à l'or des Bandini, et rien sans le boss.
        const ctx = { fillRect: function () {}, set globalAlpha(v) {}, set fillStyle(v) {} };
        const pos = function (x, y) { return { x: x, y: y }; };
        const teints = L.Hud.dessinerLaVilleDuBoss(ctx, L.Monde.carte, pos);
        p.boss = null; const teintsAvant = L.Hud.dessinerLaVilleDuBoss(ctx, L.Monde.carte, pos); p.boss = boss;
        out.apres.carte = { boss: teints, sans: teintsAvant };
        // La sauvegarde garde le boss ; une partie abîmée ne le devient pas.
        const abimee = JSON.parse(JSON.stringify(p)); abimee.boss = 'oui';
        out.sauve = { relue: L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs).boss,
                      abimee: L.Sauvegarde.completer(abimee, B.defs).boss };
        const j2 = recharger(L);
        out.sauve.recharge = B.partie.boss;
        // Et la partie continue : on marche.
        const x0 = j2.x, y0 = j2.y;
        o.touche('KeyD'); o.frame(40); o.relacher('KeyD');
        o.touche('KeyS'); o.frame(40); o.relacher('KeyS');
        out.sauve.bouge = Math.round(Math.hypot(j2.x - x0, j2.y - y0));
        out.dites = dites;
        return out;
    }""")


def test_m98_s_ouvre_au_telephone_quand_la_ville_est_prete(_partie):
    r = _partie
    assert r["dispo"] == ["m98"], "tout le reste est fait, et m99 veut 15 000 $"
    assert r["appel"] == {"mission": "m98", "qui": "josee"}, r["appel"]
    assert "appel:josee:" in r["dites"]


def test_m98_ne_s_ouvre_pas_sans_quatre_districts_et_quatre_proprietes(banc):
    r = banc("function (L, o) {" + outils("faites") + PREPARER + """
        const oui = !!L.Histoire.disponibleDe('josee');
        p.libere = ['faubourg', 'quais', 'erables'];
        const troisDistricts = !!L.Histoire.disponibleDe('josee');
        p.libere = ['faubourg', 'quais', 'erables', 'pointe']; delete p.proprietes.hotel;
        const troisProprietes = !!L.Histoire.disponibleDe('josee');
        return { oui: oui, troisDistricts: troisDistricts, troisProprietes: troisProprietes };
    }""")
    assert r == {"oui": True, "troisDistricts": False, "troisProprietes": False}, r


def test_l_intro_se_joue_chez_josee_puis_on_sort(_partie):
    r = _partie
    assert r["intro"]["scene"] > 60, "l'intro est une scène, pas une boîte"
    assert r["intro"]["mission"] == "m98" and r["intro"]["etape"] == 0, r["intro"]
    assert "pendant:josee:0" in r["dites"]


def test_le_siege_du_brouillard_les_allies_couchent_les_cravates_et_jamais_toi(_partie):
    r = _partie
    s = r["siege"]
    assert s["etape"] == 1 and s["cibles"] == 6, s
    assert s["allies"] == ["boulonneux", "boulonneux", "morues", "morues", "skateux", "skateux"], s
    assert set(s["etats"]) == {"allie"}, s
    c = r["combat"]
    assert c["cible"] >= 10 and c["kos"] >= 3, f"les alliés ne se battent pas : {c}"
    assert c["autres"] == [], f"un allié a frappé autre chose qu'un homme du maire : {c['autres']}"
    assert r["fideles"] == {"alerte": "allie", "blesse": "allie"}, r["fideles"]
    assert "pendant:zed:1" in r["dites"]


def test_la_police_du_maire_a_cinq_etoiles_puis_bouchard_rappelle_ses_chiens(_partie):
    r = _partie
    assert r["police"]["etape"] == 2 and r["police"]["etoiles"] == 5 and r["police"]["allies"] == 6, r["police"]
    assert r["police"]["tient"] == {"etape": 2, "etoiles": 5}, "on TIENT, le chrono court"
    t = r["treve"]
    assert t["etape"] == 3 and t["etoiles"] == 0, t
    assert t["allies"] is None and t["rentres"] == 6, "les alliés rentrent chez eux"
    assert "pendant:bouchard:3" in r["dites"]


def test_la_garde_du_maire_puis_la_chambre_douze(_partie):
    r = _partie
    assert r["garde"] == {"etape": 4, "n": 4, "arch": ["garde"] * 4}, r["garde"]
    c = r["chambre"]
    assert c["etape"] == 5 and c["gps"] is not None and c["gps"] < 32, "la flèche mène à la porte de l'hôtel"
    assert c["piece"] == "hotel_chambre" and c["maire"], c
    assert "pendant:norbert:4" in r["dites"]


def test_le_maire_cede_rend_le_billet_puis_le_generique(_partie):
    f = _partie["fin"]
    v = f["vus"]
    lignes = v["lignes"]
    # La poignée de main (le maire se présente), la fin devant lui, Josée chez elle, puis le narrateur.
    assert lignes[:3] == ["maire", "maire", "maire"], lignes
    assert lignes[3:5] == ["josee@", "josee@"], lignes
    assert lignes[5:] == ["narrateur"] * 5, lignes
    assert v["maireParti"], "le maire est encore dans la chambre quand le générique part"
    assert v["generique"] and v["anonyme"], v
    assert v["musique"] == "generique_boss", "le générique du Boss a sa musique à lui"
    assert v["cartons"] == ["3 000 $", "5", "4", str(len(missions.CATALOGUE) - 1), "1", "DÉCHIRÉE",
                            "LOGO:LE BOSS"], v["cartons"]
    assert f["menu"] == "BILAN" and f["faite"] and f["fins"] == ["m98"], f
    assert f["boss"] == {"jour": 1} and f["dette"] == 0 and f["manchette"] == "le_boss", f


def test_la_ville_d_apres_a_change_de_couleur(_partie):
    a = _partie["apres"]
    assert a["dehors"] and a["chambre"] == "hotel_chambre" and not a["maire"], "le maire a quitté l'hôtel pour de bon"
    assert a["morues"]["n"] >= 1 and a["morues"]["or"] == a["morues"]["n"], a["morues"]
    assert a["nom"] == {"nom": "Les Quais", "gang": None, "boss": True}, a["nom"]
    assert a["salut"]["passant"] in pietons.BOSS["passants"], a["salut"]
    assert a["salut"]["morue"] in pietons.BOSS["gangs_saluts"], a["salut"]
    assert a["rixe"]["boss"] == 0 and a["rixe"]["sans"] > 0, a["rixe"]
    assert a["carte"]["boss"] == 5 and a["carte"]["sans"] == 0, a["carte"]


def test_la_sauvegarde_garde_le_boss_et_la_partie_continue(_partie):
    s = _partie["sauve"]
    assert s["relue"] == {"jour": 1} and s["abimee"] is None, s
    assert s["recharge"] == {"jour": 1}, s
    assert s["bouge"] > 10, "après le générique, le joueur ne bouge plus"
