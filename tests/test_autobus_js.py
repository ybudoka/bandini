"""Les autobus au banc : ils passent aux arrêts, on monte, on roule, on descend.

Demande de Martin (16 sept. 2026) : « des arrêts d'autobus pour se déplacer
réellement d'un arrêt à l'autre selon un tracé, et des bus qui passent aux
arrêts aussi ».

⚠️ **On ne fait pas attendre le banc une minute de jeu par autobus.** L'horaire
est une fonction de l'heure (`Autobus.placeALHeure`) : `AMENER` règle l'heure de
la partie pour que l'autobus d'une ligne soit à `avance` tuiles EN AMONT de
l'arrêt — hors de l'écran, dans la bulle — et il arrive de lui-même.
"""

#: Le joueur sur le trottoir de l'arrêt ; l'heure réglée pour qu'un autobus
#: de la ligne arrive d'`avance` tuiles plus haut sur son tracé.
AMENER = """
    function amener(L, numero, avance) {
      const d = L.Autobus.donnees();
      const ligne = d.lignes.find(function (l) { return l.numero === numero; });
      // Un arrêt qui n'est PAS le premier de la boucle : on veut une voie droite
      // en amont, pas le raccord de la fin de boucle.
      const o = ligne.ordre[Math.floor(ligne.ordre.length / 2)];
      const a = d.arrets[o.arret];
      const j = L.B.joueur;
      j.x = a.quai[0] * L.TT + 8; j.y = a.quai[1] * L.TT + 8;
      L.Monde.centrerCamera(j.x, j.y);
      const h = d.horaire, jour = L.B.defs.economie.jour_secondes * 60;
      const cible = ((o.i - avance) % ligne.n + ligne.n) % ligne.n * L.TT;
      const temps = ((cible % ligne.longueurPx) + ligne.longueurPx) % ligne.longueurPx / h.vitesse_px;
      L.B.partie.jour = 2;
      // ⚠️ En plein jour : a quatre heures du matin, les feux clignotent et la
      // ville se vide — une autre mesure.
      let t = temps;
      while (t / jour < 0.4) t += ligne.longueurPx / h.vitesse_px;
      L.B.partie.heure = (t / jour) % 1;
      return { ligne: ligne, arret: a, o: o };
    }
    function attendreLAutobus(L, o, a, max) {
      for (let i = 0; i < max; i++) {
        o.frame(1);
        const v = L.B.entites.find(function (q) { return q.conducteur === 'ligne' && q.arretT > 0 && q.arret === a.id; });
        if (v) return { v: v, images: i };
      }
      return null;
    }
"""


def test_l_autobus_passe_a_l_abribus_ou_l_on_attend_et_on_monte(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const m = amener(L, 2, 45);
        const j = L.B.joueur;
        const attente = L.Autobus.texteDAttente(j);
        const arrive = attendreLAutobus(L, o, m.arret, 4000);
        if (!arrive) return { arrive: false, attente: attente };
        const v = arrive.v;
        const out = { arrive: true, images: arrive.images, attente: attente,
                      ecart_px: Math.hypot(v.x - (m.arret.x * L.TT + 8), v.y - (m.arret.y * L.TT + 8)),
                      invite: L.B.invite, argent: L.B.partie.argent };
        o.tape('KeyE', 1);
        out.passager = j.passager === v;
        out.dansVehicule = j.dansVehicule === v;
        out.dessine = j.dessine;
        out.paye = out.argent - L.B.partie.argent;
        out.invite_a_bord = L.B.invite;
        out.conducteur = v.conducteur;
        return out;
    }""" % AMENER)
    assert r["arrive"], f"aucun autobus à l'arrêt ({r['attente']})"
    assert r["attente"] and "DANS" in r["attente"], r["attente"]
    assert r["ecart_px"] < 8, f"arrêté à {r['ecart_px']:.0f} px de son arrêt"
    assert r["invite"].startswith("MONTER — LIGNE 2"), r["invite"]
    assert r["passager"] and r["dansVehicule"] and not r["dessine"]
    assert r["paye"] == 3
    # ⚠️ La pression qui fait monter ne fait pas redescendre dans la même image.
    assert r["invite_a_bord"].startswith("DESCENDRE"), r["invite_a_bord"]
    assert r["conducteur"] == "ligne", "le passager a pris le volant"


def test_a_bord_on_demande_l_arret_et_on_descend_au_suivant(banc):
    """On roule POUR DE VRAI : l'autobus suit son tracé, ne s'arrête qu'à l'arrêt
    demandé, et le joueur se retrouve sur le trottoir de cet arrêt-là."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const m = amener(L, 2, 45);
        const j = L.B.joueur;
        const arrive = attendreLAutobus(L, o, m.arret, 4000);
        if (!arrive) return { arrive: false };
        const v = arrive.v;
        o.tape('KeyE', 1);
        const argent = L.B.partie.argent;
        // ⚠️ On laisse PASSER un arrêt sans rien demander : l'autobus doit filer
        // devant l'abribus. Demander tout de suite l'arrêt suivant ne prouvait rien
        // — il s'y serait arrêté de toute façon, s'il s'arrêtait partout.
        for (let i = 0; i < 200; i++) o.frame(1);
        const saute = L.Autobus.prochainArret(v);
        let arretsSautes = 0;
        for (let i = 0; i < 9000 && L.Autobus.prochainArret(v) === saute; i++) {
          o.frame(1);
          if (v.arretT > 0) arretsSautes++;
        }
        const prochain = L.Autobus.prochainArret(v);
        o.tape('KeyE', 1);
        const demande = v.demande;
        let passes = 0, suivi = true, arretes = [];
        for (let i = 0; i < 9000 && j.passager; i++) {
          o.frame(1);
          if (j.passager && (Math.abs(j.x - v.x) > 0.01 || Math.abs(j.y - v.y) > 0.01)) suivi = false;
          if (v.arretT > 0 && arretes.indexOf(v.arret) < 0) arretes.push(v.arret);
          passes++;
        }
        return { arrive: true, demande: demande, prochain: prochain && prochain.id, suivi: suivi,
                 arretes: arretes, descendu: !j.passager, dessine: j.dessine,
                 tuile: [Math.floor(j.x / L.TT), Math.floor(j.y / L.TT)],
                 quai: prochain && prochain.quai, paye: argent - L.B.partie.argent,
                 conducteur: v.conducteur, images: passes, saute: saute && saute.id, arretsSautes: arretsSautes };
    }""" % AMENER)
    assert r["arrive"]
    assert r["demande"]
    assert r["saute"] != r["prochain"], "le juge n'a laissé passer aucun arrêt"
    assert r["arretsSautes"] == 0, "l'autobus s'est arrêté à un arrêt que personne n'a demandé"
    assert r["suivi"], "le passager ne suit pas son autobus"
    assert r["descendu"], f"toujours à bord après {r['images']} images"
    assert r["arretes"] == [r["prochain"]], f"arrêts servis {r['arretes']}, demandé {r['prochain']}"
    assert r["tuile"] == r["quai"], f"descendu en {r['tuile']}, le trottoir de l'arrêt est {r['quai']}"
    assert r["dessine"] and r["paye"] == 0 and r["conducteur"] == "ligne"


def test_recherche_ou_fauche_le_chauffeur_n_ouvre_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const m = amener(L, 2, 45);
        const j = L.B.joueur;
        const arrive = attendreLAutobus(L, o, m.arret, 4000);
        if (!arrive) return { arrive: false };
        L.B.recherche.etoiles = 1;
        o.tape('KeyE', 1);
        const recherche = { passager: !!j.passager, msg: L.B.msg };
        L.B.recherche.etoiles = 0;
        L.B.partie.argent = 2;
        o.tape('KeyE', 1);
        return { arrive: true, recherche: recherche, fauche: { passager: !!j.passager, msg: L.B.msg, argent: L.B.partie.argent } };
    }""" % AMENER)
    assert r["arrive"]
    assert not r["recherche"]["passager"] and "CHAUFFEUR" in r["recherche"]["msg"]
    assert not r["fauche"]["passager"] and "PAS ASSEZ" in r["fauche"]["msg"] and r["fauche"]["argent"] == 2


def test_forcer_la_descente_ne_casse_pas_la_ligne(banc):
    """⚠️ L'hôpital, une arrestation, un autobus en feu : tout ce qui appelle
    `Vehicules.descendre(j, true)` sur un passager doit le poser à côté, pas garer
    l'autobus « laissé » pour la fourrière ni lui retirer son chauffeur."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const m = amener(L, 2, 45);
        const j = L.B.joueur;
        const arrive = attendreLAutobus(L, o, m.arret, 4000);
        if (!arrive) return { arrive: false };
        const v = arrive.v;
        o.tape('KeyE', 1);
        for (let i = 0; i < 240; i++) o.frame(1);
        const roule = Math.abs(v.vitesse) > 0.2;
        L.Vehicules.descendre(j, true);
        return { arrive: true, roule: roule, passager: !!j.passager, dans: !!j.dansVehicule, dessine: j.dessine,
                 conducteur: v.conducteur, laisse: v.laisse, a_bord: !!v.passager };
    }""" % AMENER)
    assert r["arrive"] and r["roule"]
    assert not r["passager"] and not r["dans"] and r["dessine"] and not r["a_bord"]
    assert r["conducteur"] == "ligne" and not r["laisse"]


def test_l_autobus_suit_son_trace_et_guette_le_feu_le_nez_hors_du_carrefour(banc):
    """Un autobus fait trois tuiles. ⚠️ Arrêté le centre sur la ligne d'arrêt,
    comme le trafic, son nez dépassait de 24 px dans le carrefour : les chars qui
    tournaient l'accrochaient et il restait pris huit cents images."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        amener(L, 1, 60);
        const d = L.Autobus.donnees();
        const surLeTrace = {};
        for (const l of d.lignes) surLeTrace[l.numero] = new Set(l.tuiles.map(function (t) { return t[0] + ',' + t[1]; }));
        let releves = 0, horsTrace = 0, attentes = 0, nezDedans = 0, bloqueMax = 0;
        for (let i = 0; i < 5000; i++) {
          o.frame(1);
          if (i %% 5) continue;
          for (const v of L.B.entites) {
            if (v.type !== 'vehicule' || v.conducteur !== 'ligne') continue;
            releves++;
            const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
            let pres = false;
            for (let dx = -1; dx <= 1 && !pres; dx++) for (let dy = -1; dy <= 1 && !pres; dy++) if (surLeTrace[v.ligne].has((tx + dx) + ',' + (ty + dy))) pres = true;
            if (!pres) horsTrace++;
            bloqueMax = Math.max(bloqueMax, v.bloqueT || 0);
            if (v.attendFeu && !(v.arretT > 0) && Math.abs(v.vitesse) < 0.05) {
              attentes++;
              const nx = v.x + Math.cos(v.angle) * (v.def.longueur / 2 - 2), ny = v.y + Math.sin(v.angle) * (v.def.longueur / 2 - 2);
              if (L.Monde.intersectionA(Math.floor(nx / L.TT), Math.floor(ny / L.TT))) nezDedans++;
            }
          }
        }
        return { releves: releves, horsTrace: horsTrace, attentes: attentes, nezDedans: nezDedans, bloqueMax: bloqueMax };
    }""" % AMENER)
    assert r["releves"] > 300, r
    assert r["horsTrace"] <= r["releves"] * 0.01, f"{r['horsTrace']} relevés hors du tracé"
    assert r["attentes"] > 20, "aucun autobus n'a attendu un feu : le juge ne mesure rien"
    assert r["nezDedans"] == 0, f"{r['nezDedans']} attentes le nez dans le carrefour"


def test_un_autobus_ne_tire_pas_un_de_du_jeu(banc):
    """⚠️ Sa place vient de l'heure, sa couleur de sa ligne, sa silhouette est
    donnée : un décor qui tire un dé décale tout ce qui naît après — la leçon du
    char en panne. On compte les dés tirés PENDANT le code des autobus."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        amener(L, 2, 45);
        L.graine(77);
        const tirage = L.B.rng;
        let dansLesAutobus = 0, total = 0;
        L.B.rng = function () {
          total++;
          if (String(new Error().stack).indexOf('autobus.js') >= 0) dansLesAutobus++;
          return tirage();
        };
        let nes = 0;
        const vus = new Set();
        for (let i = 0; i < 1500; i++) {
          o.frame(1);
          for (const v of L.B.entites) if (v.conducteur === 'ligne' && !vus.has(v)) { vus.add(v); nes++; }
        }
        return { nes: nes, dansLesAutobus: dansLesAutobus, total: total };
    }""" % AMENER)
    assert r["nes"] >= 1, "aucun autobus n'est né : le juge ne mesure rien"
    assert r["dansLesAutobus"] == 0, f"{r['dansLesAutobus']} dés tirés par les autobus"


def test_la_grande_carte_montre_les_lignes(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = L.Autobus.donnees();
        const tuiles = d.lignes.reduce(function (s, l) { return s + l.n; }, 0);
        function mesurer(avecLignes) {
          const garde = L.B.defs.carte.autobus;
          if (!avecLignes) L.B.defs.carte.autobus = null;
          L.B.etat = 'carte';
          const avant = L.B.stats.rects;
          L.Hud.dessiner(o.ctx);
          L.B.defs.carte.autobus = garde;
          return L.B.stats.rects - avant;
        }
        return { avec: mesurer(true), sans: mesurer(false), tuiles: tuiles };
    }""")
    # Un rectangle par tuile de tracé, et deux par arrêt, en plus de la carte d'avant.
    assert r["avec"] - r["sans"] >= r["tuiles"], r
