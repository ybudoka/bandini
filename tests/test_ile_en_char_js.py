"""Un char sur l'île (M16, vague 16, 1er oct. 2026) — par la navette, au bouton, et i04 jouée.

La navette de l'île (le deuxième bateau des Quais, `navette.py`) prend les chars sur son pont, comme le traversier.
Ce qui manquait, c'est le CHEMIN D'UN JOUEUR : arriver par la rue des Quais, monter sur le pont, débarquer à la vieille
jetée de l'île — un char y sortait-il seulement ? — rouler jusqu'au hangar de Léo par la gravelle et l'herbe, sans
couler, et revenir. ⚠️ Un juge qui part de la cible hérite de ses erreurs (« juge posé dans l'axe de la cible ») : ici,
on part de la rue, quatorze tuiles au nord du quai, et on conduit au bouton sur un chemin trouvé dans la carte.
"""

import json

from outils_ile_en_char import PILOTE
from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_p_js import RECHARGER

from app import missions

#: L'heure (en heures) : la navette est à quai aux Quais juste avant l'heure impaire, à l'île juste avant la paire.
TRAJET = """
  function heure(L, h) { L.B.partie.heure = (h % 24) / 24; }
  function tuile(e) { return [Math.floor(e.x / 16), Math.floor(e.y / 16)]; }
  // Le milieu du pont : sa deuxième rangée (la première touche l'eau, la troisième est la cabine).
  function pont(L, k) { const q = L.Navette.donnees().escales[k]; return { x: (q.x + 4) * 16 + 8, y: (q.y + 1) * 16 + 8 }; }
  function hangar(L) { const p = L.Monde.carte.def.portes.find(function (q) { return q.lieu === 'hangar_ile'; }); return { x: p.x * 16 + 8, y: (p.y + 2) * 16 + 8 }; }
  function conduire(L, o, v, vers) {
    const c = cheminDuChar(L, { x: v.x, y: v.y }, vers);
    return c ? piloter(L, o, v, c, 3000) : { images: 0, arrive: 9999, eau: null, degats: null, sansChemin: true };
  }
"""


def test_un_char_de_la_rue_des_quais_au_hangar_de_l_ile_et_retour(banc):
    r = banc("function (L, o) {" + PILOTE + TRAJET + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, N = L.Navette;
        j.intouchable = true; j.invincible = 1e6;
        if (B.menu && L.Hud.fermerMenu) L.Hud.fermerMenu();
        const a = N.donnees().escales[0];
        // La rue qui longe le quai, quatorze tuiles plus au nord : une voie qui descend vers lui (`v`).
        // (La plus au nord de dix à quatorze tuiles : la rue tourne parfois avant.)
        let depart = null;
        for (let dy = 14; dy >= 8 && !depart; dy--) {
          for (let x = a.x - 8; x < a.x && !depart; x++) if (B.defs.carte.voie[a.y - dy][x] === 'v') depart = { x: x * 16 + 8, y: (a.y - dy) * 16 + 8 };
        }
        heure(L, 0.7); o.frame(2);
        j.x = depart.x; j.y = depart.y; L.Monde.centrerCamera(j.x, j.y);
        const v = L.Vehicules.creer('luxe', depart.x, depart.y, Math.PI / 2, { etat: 'stationne' });
        L.Entites.indexer(); L.Vehicules.monter(j, v); o.frame(2);
        const vie0 = v.vie;
        const monte = conduire(L, o, v, pont(L, 0));
        heure(L, 0.999); o.frame(20);
        const aBord = !!v.aBord;
        heure(L, 1.4); o.frame(2);
        const enMer = { aBord: !!v.aBord, eau: L.Monde.estEau(tuile(v)[0], tuile(v)[1]) };
        heure(L, 1.8); o.frame(20);
        const ile = { aBord: !!v.aBord, tuile: tuile(v), refuge: L.Police.auRefuge ? L.Police.auRefuge() : null };
        const auHangar = conduire(L, o, v, hangar(L));
        // Le retour : la navette est à l'île avant l'heure paire ; on remonte sur son pont, elle part, on débarque aux Quais.
        // ⚠️ Une heure de jeu, c'est vingt secondes : du hangar au quai, il faut près d'une heure de route — la navette
        // ne reste à quai que vingt minutes. On l'attend au bout de la jetée, comme un joueur.
        const q1 = N.donnees().escales[1];
        const jetee = conduire(L, o, v, { x: (q1.acces[0][0] + 1) * 16 + 8, y: (q1.acces[0][1] - 1) * 16 + 8 });
        heure(L, 3.66); o.frame(2);
        const remonte = conduire(L, o, v, pont(L, 1));
        heure(L, 3.999); o.frame(20);
        const aBordRetour = !!v.aBord;
        heure(L, 4.8); o.frame(20);
        const retour = { aBord: !!v.aBord, tuile: tuile(v) };
        const enVille = conduire(L, o, v, depart);
        return { monte: monte, aBord: aBord, enMer: enMer, ile: ile, auHangar: auHangar, jetee: jetee, remonte: remonte,
                 aBordRetour: aBordRetour, retour: retour, enVille: enVille, degats: Math.round(vie0 - v.vie),
                 b: [N.donnees().escales[1].x, N.donnees().escales[1].y] };
    }""")
    # ⚠️ Un coin du pont : en tournant de la rue sur le pont (deux rangées), le centre du char mord le bord de l'eau
    # quelques images — il ne coule pas (trois secondes, `coule_s`). Au-delà d'une seconde, c'est un piège.
    assert r["monte"]["arrive"] <= 20 and r["monte"]["eau"] < 60, f"de la rue jusqu'au pont : {r['monte']}"
    assert r["aBord"] is True and r["enMer"] == {"aBord": True, "eau": True}, r
    assert r["ile"]["aBord"] is False and r["b"][0] <= r["ile"]["tuile"][0] < r["b"][0] + 8, r["ile"]
    assert r["auHangar"]["arrive"] <= 20 and r["auHangar"]["eau"] == 0, f"de la jetée au hangar : {r['auHangar']}"
    assert r["jetee"]["arrive"] <= 20 and r["jetee"]["eau"] == 0, f"du hangar à la jetée : {r['jetee']}"
    assert r["remonte"]["arrive"] <= 20 and r["remonte"]["eau"] < 60 and r["aBordRetour"] is True, r
    assert r["retour"]["aBord"] is False and r["enVille"]["arrive"] <= 20 and r["enVille"]["eau"] < 60, r
    assert r["degats"] <= 20, f"un aller-retour qui coûte {r['degats']} PV : un coin de mur, un baril ?"


#: Tout le catalogue avant i04 — Léo n'a plus qu'elle à donner.
AVANT_I04 = json.dumps([m["slug"] for m in missions.CATALOGUE if m["slug"] not in ("i04", "m97", "m98", "m99")])


def test_i04_la_berline_chaude_refroidit_une_journee_dans_le_hangar_de_leo(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + PILOTE + TRAJET + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, N = L.Navette;
        faites(L, """ + AVANT_I04 + """);
        const j = recharger(L);
        const argent = paiements(L);
        heure(L, 10);
        const appel = serrer(L, o, 'leo'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        // 0. La berline, derrière la cantine.
        const v = B.mission.vehicule;
        const berline = { slug: v && v.slug, cantine: v ? Math.round(Math.hypot(v.x - L.Histoire.lieu('cantine').x, v.y - L.Histoire.lieu('cantine').y) / 16) : null };
        aPied(L); j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const chaud = { etape: etape(L), etoiles: B.recherche.etoiles };
        // 1. Le pont de la navette aux Quais, avant l'heure impaire.
        heure(L, 12.7); o.frame(2);
        const pq = pont(L, 0);
        v.x = pq.x; v.y = pq.y; v.vitesse = 0; v.vx = 0; v.vy = 0; v.angle = 0; L.Entites.indexer(); o.frame(2);
        heure(L, 12.999); jouer(L, o, 20);
        const embarque = { etape: etape(L), aBord: !!v.aBord };
        heure(L, 13.8); jouer(L, o, 20);
        const ile = { aBord: !!v.aBord, refuge: L.Police.auRefuge(), etoiles: B.recherche.etoiles };
        // 2. Au hangar, par la gravelle — au bouton. Léo le rentre.
        const route = conduire(L, o, v, hangar(L)); jouer(L, o, 30);
        const livre = { etape: etape(L), rentre: B.entites.indexOf(v) < 0, aPied: !j.dansVehicule };
        // 3. Une journée : la ligne dit ce qui reste ; une heure ne suffit pas, vingt-quatre oui.
        jouer(L, o, 5);
        const attend = L.Histoire.ligneObjectif();
        p.jour += 0; heure(L, (p.heure * 24) + 3); jouer(L, o, 5);
        const troisHeures = etape(L);
        p.jour += 1; jouer(L, o, 10);
        const refroidi = etape(L);
        // 4. Le char repeint, sur la terre devant le hangar.
        const w = B.mission.vehicule;
        const neuf = { slug: w && w.slug, autre: w !== v, eau: w ? L.Monde.estEau(Math.floor(w.x / 16), Math.floor(w.y / 16)) : null,
                       pres: w ? Math.round(Math.hypot(w.x - hangar(L).x, w.y - hangar(L).y) / 16) : null };
        aPied(L); j.x = w.x + 12; j.y = w.y; L.Entites.indexer(); L.Vehicules.monter(j, w); L.Entites.indexer(); jouer(L, o);
        const reprend = etape(L);
        // 5. La navette du retour : le pont à l'île avant l'heure paire.
        heure(L, 15.7); o.frame(2);
        const pi = pont(L, 1);
        w.x = pi.x; w.y = pi.y; w.vitesse = 0; w.vx = 0; w.vy = 0; w.angle = Math.PI; L.Entites.indexer(); o.frame(2);
        heure(L, 15.999); jouer(L, o, 20);
        const retour = etape(L);
        heure(L, 16.8); jouer(L, o, 20);
        // 6. À la planque.
        const baie = L.Histoire.lieuDeLivraison('planque');
        w.x = baie.x; w.y = baie.y; w.vitesse = 0; j.x = w.x; j.y = w.y; L.Entites.indexer(); jouer(L, o, 10);
        finir(L, o);
        return { mission: mission, berline: berline, chaud: chaud, embarque: embarque, ile: ile, route: route, livre: livre,
                 attend: attend, troisHeures: troisHeures, refroidi: refroidi, neuf: neuf, reprend: reprend, retour: retour,
                 dites: dites, fait: !!p.missionsFaites.i04, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["mission"] == "i04", r
    assert r["berline"]["slug"] == "luxe" and r["berline"]["cantine"] <= 12, r["berline"]
    assert r["chaud"] == {"etape": 1, "etoiles": 3}, r["chaud"]
    assert r["embarque"] == {"etape": 2, "aBord": True}, r["embarque"]
    assert r["ile"]["aBord"] is False and r["ile"]["refuge"] is True, r["ile"]
    assert r["route"]["arrive"] <= 20 and r["route"]["eau"] == 0, r["route"]
    assert r["livre"] == {"etape": 3, "rentre": True, "aPied": True}, r["livre"]
    assert "ENCORE" in r["attend"] and r["troisHeures"] == 3 and r["refroidi"] == 4, r
    assert r["neuf"]["slug"] == "luxe" and r["neuf"]["autre"] and r["neuf"]["eau"] is False and r["neuf"]["pres"] <= 6, r["neuf"]
    assert r["reprend"] == 5 and r["retour"] == 6, r
    for dite in ("pendant:leo:0", "pendant:leo:1", "pendant:leo:2", "pendant:leo:3", "pendant:leo:4", "pendant:leo:5"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [100], r
