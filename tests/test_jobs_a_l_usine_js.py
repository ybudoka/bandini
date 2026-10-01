"""Deux petites jobs à l'usine (M16, la toute fin, 1er oct. 2026) — la règle de l'usine, au banc.

La porte de l'usine est derrière la chaîne de sa cour, qui ferme la nuit (`carte.BARRIERES`). Une job dont un lieu est
derrière une barrière d'heure (`missions.barriere_d_heure`) :
- ne s'offre qu'aux heures où cette barrière est OUVERTE (`Jobs.aLHeure`) — ni au carnet, ni au téléphone, jamais ;
- prise, elle tient la barrière ouverte jusqu'à sa fin (`Monde.barriereFermee`) : la nuit qui tombe pendant la job ne
  ferme pas la chaîne sur elle — elle ne peut pas finir porte fermée ; finie, la chaîne se referme.

- t08 jouée au bouton : trois boîtes, ramassées au coin à pied, portées à la porte (au volant, rien ne compte), chacune
  quitte le sac en arrivant ; l'ouvrier paie.
- t10 jouée au bouton : le machiniste te suit jusqu'à l'usine, sous son chrono ; trop lent, il le dit en personne."""

from test_jobs_js import AIDES as AIDES_JOBS

from outils_missions import outils

BASE = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6']"

AIDES = AIDES_JOBS + outils("heure") + """
  function chaine(L) { return L.Monde.carte.def.barrieres.find(function (b) { return b.slug === 'usine'; }); }
  function prendre(L, o, slug, dy) {
    poserA(L, 'usine', dy || 48);
    L.Jobs.offrir(slug, true);
    const e = L.B.job.e;
    return { pris: luiParler(L, o), e: e };
  }
"""


def test_une_job_a_l_usine_ne_s_offre_que_le_jour_et_jamais_au_carnet(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        recharger(L);
        function offertes() { return L.Jobs.offertes().map(function (m) { return m.slug; }); }
        heure(L, false); const jour = offertes(), fermeeLeJour = L.Monde.barriereFermee(chaine(L));
        heure(L, true); const nuit = offertes(), fermeeLaNuit = L.Monde.barriereFermee(chaine(L));
        // La nuit, en ville dans La Shop, la cadence levée : aucun passant ne vient offrir t08 ni t10.
        poserA(L, 'usine', 48);
        const venues = [];
        for (let k = 0; k < 6; k++) {
          B.jobRepos = 0; p.jobOfferte = null;
          for (let n = 0; n < 400 && !B.job; n++) { o.frame(1); poserA(L, 'usine', 48); heure(L, true); }
          if (B.job) { venues.push(B.job.slug); L.Jobs.oublier(); }
          p.jour++;
        }
        const carnet = L.Histoire.disponibles().filter(function (m) { return m.slug === 't08' || m.slug === 't10'; }).length;
        const m = L.Histoire.mission('t08');
        return { jour: jour, nuit: nuit, fermeeLeJour: fermeeLeJour, fermeeLaNuit: fermeeLaNuit, venues: venues,
                 carnet: carnet, barriere: m.barriere };
    }""")
    assert r["barriere"] == "usine", r
    assert r["fermeeLeJour"] is False and r["fermeeLaNuit"] is True, r
    assert {"t08", "t10"} <= set(r["jour"]), f"le jour, la cour est ouverte : {r}"
    assert not {"t08", "t10"} & set(r["nuit"]), f"la nuit, la cour est fermée — pas d'offre : {r}"
    assert len(r["nuit"]) > 0, f"les autres jobs s'offrent la nuit comme avant : {r}"
    assert not {"t08", "t10"} & set(r["venues"]), f"un passant est venu offrir une job d'usine la nuit : {r}"
    assert r["carnet"] == 0, r


def test_t08_trois_boites_a_pied_et_la_chaine_attend_la_job(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        const j = recharger(L);
        heure(L, false);
        const argent = paiements(L);
        const d = prendre(L, o, 't08');
        jouer(L, o, 4);
        const usine = L.Histoire.lieu('usine');
        const boites = [];
        let auVolant = null, nuit = null;
        for (let k = 0; k < 3; k++) {
          // La boîte attend au coin de la ruelle : on y marche.
          const b = B.entites.find(function (e) { return e.type === 'ramassage' && e.objetDeMission === 'boite'; });
          const avant = etape(L);
          if (b) { j.x = b.x; j.y = b.y + 2; L.Entites.indexer(); }
          jouer(L, o, 4);
          const prise = { posee: !!b, dessin: b && b.objet, loin: b ? Math.round(Math.hypot(b.x - usine.x, b.y - usine.y) / 16) : null,
                          avant: avant, apres: etape(L), sac: (p.objets || {}).boite || 0 };
          // La deuxième : la nuit tombe en chemin — la chaîne ne se ferme pas sur la job.
          if (k === 1) {
            heure(L, true);
            nuit = { estNuit: L.Monde.estNuit(), fermee: L.Monde.barriereFermee(chaine(L)) };
          }
          // La troisième : au volant, à la porte, rien ne compte.
          if (k === 2) {
            const v = L.Vehicules.creer('auto', usine.x, usine.y, 0, { etat: 'stationne', couleur: '#777777' });
            L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o, 4);
            auVolant = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), sac: (p.objets || {}).boite || 0 };
            L.Vehicules.descendre(j, true); L.Entites.retirer(v); L.Entites.indexer();
          }
          j.x = usine.x; j.y = usine.y + 6; L.Entites.indexer(); jouer(L, o, 4);
          prise.porte = etape(L); prise.sacApres = (p.objets || {}).boite || 0;
          boites.push(prise);
        }
        versLui(L); jouer(L, o, 4);
        finir(L, o); jouer(L, o, 4);
        const apres = L.Monde.barriereFermee(chaine(L));
        return { pris: d.pris, boites: boites, auVolant: auVolant, nuit: nuit, apres: apres, dites: dites,
                 fait: !!p.missionsFaites.t08, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["pris"]["mission"] == "t08", r
    for k, b in enumerate(r["boites"]):
        assert b["posee"] and b["dessin"] == "boite" and 8 <= b["loin"] <= 12, (k, b)
        assert b["apres"] == b["avant"] + 1 and b["sac"] == 1, f"ramassée à pied, elle est dans le sac : {k} {b}"
        assert b["porte"] == b["apres"] + 1 and b["sacApres"] == 0, f"posée à la porte, elle quitte le sac : {k} {b}"
    assert r["auVolant"]["etape"] == 5 and "À PIED" in r["auVolant"]["ligne"] and r["auVolant"]["sac"] == 1, r["auVolant"]
    assert r["nuit"] == {"estNuit": True, "fermee": False}, f"la nuit tombée, la chaîne attend la job : {r['nuit']}"
    assert r["apres"] is True, "la job finie, la nuit, la chaîne se referme"
    assert "pendant:passant:2" in r["dites"] and "pendant:passant:4" in r["dites"], r["dites"]
    assert r["fait"] is True and r["argent"] == [45], r


def test_t10_le_machiniste_pointe_a_l_heure(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        const j = recharger(L);
        heure(L, false);
        const argent = paiements(L);
        const d = prendre(L, o, 't10', 16 * 14);
        jouer(L, o, 4);
        const e = d.e, usine = L.Histoire.lieu('usine');
        // Il te suit : on marche jusqu'à la porte de l'usine, lui sur nos talons.
        const suit = e.suit === j || B.mission.protege === e;
        let n = 0;
        for (; n < 900 && p.mission; n++) {
          const dx = usine.x - j.x, dy = usine.y + 4 - j.y, dd = Math.hypot(dx, dy);
          if (dd > 3) { j.x += dx / dd * 1.5; j.y += dy / dd * 1.5; }
          if (Math.hypot(e.x - j.x, e.y - j.y) > 40) { e.x = j.x - 10; e.y = j.y; }
          L.Entites.indexer(); o.frame(1); ecouter(L);
        }
        finir(L, o);
        return { pris: d.pris, suit: suit, n: n, fait: !!p.missionsFaites.t10, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["pris"]["mission"] == "t10" and r["suit"] is True, r
    assert r["fait"] is True and r["argent"] == [40], r


def test_t10_trop_lent_il_le_dit_en_personne(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + BASE + """);
        recharger(L);
        heure(L, false);
        prendre(L, o, 't10', 16 * 14);
        jouer(L, o, 4);
        let n = 0;
        for (; n < 6000 && p.mission; n++) { o.frame(1); poserA(L, 'usine', 16 * 14); }
        passer(L, o);
        const rate = textes.filter(function (t) { return t.indexOf('Boulonneux engagent') >= 0; });
        return { n: n, rate: rate.length, fait: !!p.missionsFaites.t10, mission: p.mission };
    }""")
    assert r["mission"] is None and r["fait"] is False, r
    assert 75 * 60 - 120 <= r["n"] <= 75 * 60 + 120, f"le chrono est de 75 s : {r}"
    assert r["rate"] >= 1, f"raté, il le dit en personne : {r}"


def test_chaque_dessin_d_objet_se_peint_par_terre():
    """⚠️ Vu en capture (1er oct. 2026) : la boîte de t08 était dans `OBJETS` et dans le sac, mais pas dans les objets
    qu'on peint PAR TERRE (`OBJETS_PAR_TERRE` d'`entites.js`) — elle tombait invisible au coin de la ruelle. Chaque
    dessin d'objet de mission (`missions.DESSINS_D_OBJET`) a son peintre, se pose (`infiltration.js`) et se voit."""
    import re
    from pathlib import Path

    from app import missions
    racine = Path(__file__).resolve().parent.parent / "static" / "js"
    entites = (racine / "entites.js").read_text(encoding="utf-8")
    par_terre = re.search(r"const OBJETS_PAR_TERRE = \{([^}]*)\}", entites).group(1)
    poses = re.search(r"const DESSINS = \{([^}]*)\}", (racine / "infiltration.js").read_text(encoding="utf-8")).group(1)
    sprites = (racine / "sprites.js").read_text(encoding="utf-8")
    for d in missions.DESSINS_D_OBJET:
        assert re.search(rf"\b{d}: true", par_terre), f"{d} ne se peint pas par terre"
        assert re.search(rf"\b{d}: true", poses), f"{d} ne se pose pas"
        assert re.search(rf"^  {d}: function", sprites, re.M), f"{d} n'a pas de peintre"
