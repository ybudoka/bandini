"""Le train au banc (docs/jalons/le-train.md) : une heure, pas un dé."""

HEURE = """
function presDe(L, tx, ty) {               // la ville ne vit qu'autour du joueur (la bulle) : on l'y pose
  const j = L.B.joueur;
  j.x = tx * L.TT + 8; j.y = ty * L.TT + 8; j.vx = 0; j.vy = 0;
  L.Monde.centrerCamera(j.x, j.y);
  L.Entites.indexer();
}
function aLHeure(L, t) {                   // place la partie à t images depuis le premier matin
  const jour = L.B.defs.economie.jour_secondes * 60;
  L.B.partie.jour = 1 + Math.floor(t / jour);
  L.B.partie.heure = (t % jour) / jour;
}
"""


def test_le_train_est_une_heure(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const d = L.Train.donnees(), vus = [];
        for (let t = 0; t < d.periode; t += 97) vus.push(JSON.stringify(L.Train.etat(t)));
        const encore = [];
        for (let t = 0; t < d.periode; t += 97) encore.push(JSON.stringify(L.Train.etat(t)));
        const plus = JSON.stringify(L.Train.etat(1234 + d.periode)) === JSON.stringify(L.Train.etat(1234));
        return { pareil: vus.join() === encore.join(), plus: plus, n: vus.filter(v => v !== 'null').length };
    }""" % HEURE)
    assert r["pareil"] and r["plus"] and r["n"] > 20


def test_il_s_arrete_a_ses_trois_gares_dans_les_deux_sens(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = L.Train.donnees(), arrets = [];
        for (let t = 0; t < d.periode; t += 30) {
          const e = L.Train.etat(t);
          if (e && e.gare && e.vitesse === 0) {
            const cle = e.sens + ' ' + e.gare;
            if (arrets.indexOf(cle) < 0) arrets.push(cle);
          }
        }
        return arrets;
    }""")
    assert r == ["1 Les Friches", "1 Petit-Canton", "1 Gare centrale",
                 "-1 Gare centrale", "-1 Petit-Canton", "-1 Les Friches"]


def test_le_train_ne_tire_pas_un_de(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        L.graine(5);
        const tirage = L.B.rng; let des = 0;
        L.B.rng = function () { if (String(new Error().stack).indexOf('train.js') >= 0) des++; return tirage(); };
        let vu = 0;
        for (let k = 0; k < 40; k++) {
          aLHeure(L, k * 311);
          o.frame(3);
          if (L.Train.etat(L.Autobus.tempsDeLaPartie())) vu++;
        }
        L.B.rng = tirage;
        return { des: des, vu: vu };
    }""" % HEURE)
    assert r["vu"] > 5 and r["des"] == 0


def test_sans_train_rien_ne_casse(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        delete L.B.defs.carte.train;
        o.frame(30);
        return { d: L.Train.donnees(), e: L.Train.etat(1000) };
    }""")
    assert r == {"d": None, "e": None}


def test_les_piliers_sont_solides_et_la_rue_passe_dessous(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(2);
        const d = L.Train.donnees(), M = L.Monde;
        const pilier = d.piliers.every(function (x) { return M.bloque(x, d.rang, M.MASQUE_PIETON); });
        const rue = [113, 114, 115, 116, 191, 192].every(function (x) { return !M.bloque(x, d.rang, M.MASQUE_VEHICULE); });
        const rampe = [97, 106, 274, 283].every(function (x) { return M.bloque(x, d.rang, M.MASQUE_PIETON); });
        return { pilier: pilier, rue: rue, rampe: rampe };
    }""")
    assert r == {"pilier": True, "rue": True, "rampe": True}


def test_les_piliers_reviennent_sur_une_carte_rebatie(banc):
    # ⚠️ Une carte rebâtie (`Monde.charger`, le retour d'un bloc qui en referait une) oublie ce qu'on y a posé :
    # le train la remarque. Hors de la ville (un bloc, une pièce), il ne marque rien.
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(2);
        const d = L.Train.donnees(), M = L.Monde, x = d.piliers[0];
        M.charger(L.B.defs.carte);
        const oublie = !M.bloque(x, d.rang, M.MASQUE_PIETON);
        o.frame(2);
        return { oublie: oublie, revenu: M.bloque(x, d.rang, M.MASQUE_PIETON) };
    }""")
    assert r == {"oublie": True, "revenu": True}


ATTENTE = HEURE + """
function avantLePassage(L, i, avance) {    // t tel que le passage i se ferme dans `avance` images
  const d = L.Train.donnees();
  for (let t = 0; t < d.periode; t++) if (!L.Train.passageFerme(i, t) && L.Train.passageFerme(i, t + avance)) return t;
  return -1;
}
"""


def test_les_barrieres_se_relisent_a_l_heure(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const t = avantLePassage(L, 1, 60), d = L.Train.donnees();
        return { t: t, avant: L.Train.passageFerme(1, t), apres: L.Train.passageFerme(1, t + 120),
                 loin: L.Train.passageFerme(1, t + Math.floor(d.periode / 2)) };
    }""" % ATTENTE)
    assert r["t"] >= 0 and r == {**r, "avant": False, "apres": True, "loin": False}


def test_un_char_attend_au_passage(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const t0 = avantLePassage(L, 1, 90);
        aLHeure(L, t0);
        presDe(L, 350, 14);
        // un char du trafic qui monte (flèche '^') la rue 353-354, à six tuiles sous la voie
        const v = L.Vehicules.creer('auto', (354 + 0.5) * L.TT, 12.5 * L.TT, -Math.PI / 2,
                                      { conducteur: 'trafic', etat: 'roule', sens: '^', couleur: '#cc3333' });
        L.Entites.indexer();
        const vie = v.vie;
        let plusHaut = 99;
        let devant = 0;                               // le témoin : le train a couvert le passage
        for (let k = 0; k < 1600; k++) {
          o.frame(1);
          // tant que c'est fermé : ensuite, il a le droit de traverser
          if (L.Train.passageFerme(1, L.Autobus.tempsDeLaPartie())) plusHaut = Math.min(plusHaut, (v.y - v.def.longueur / 2) / L.TT);
          const e = L.Train.etat(L.Autobus.tempsDeLaPartie());
          if (e) { const x = L.Train.etendue(e); if (x[0] < 355 * L.TT && x[1] > 353 * L.TT) devant++; }
        }
        return { plusHaut: plusHaut, intact: v.vie === vie, devant: devant > 0 };
    }""" % ATTENTE)
    assert r["plusHaut"] >= 7.0 - 0.01   # le NEZ n'a jamais passé le bord de la voie (rang 7)
    assert r["devant"] and r["intact"]   # et le train, passé devant lui, ne l'a pas touché


def test_la_police_en_poursuite_ne_s_arrete_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        aLHeure(L, avantLePassage(L, 1, 60) + 90);          // le passage est fermé
        const v = L.Vehicules.creer('auto', (354 + 0.5) * L.TT, 9.5 * L.TT, -Math.PI / 2,
                                      { conducteur: 'trafic', etat: 'roule', sens: '^', couleur: '#cc3333' });
        v.sens = '^';
        const sage = L.Train.signalDevant(v);
        v.poursuite = true;
        const police = L.Train.signalDevant(v);
        return { sage: isFinite(sage), police: isFinite(police) };
    }""" % ATTENTE)
    assert r == {"sage": True, "police": False}    # le témoin : sans poursuite, le même char s'arrête


def test_on_n_attend_jamais_sur_la_voie(banc):
    # ⚠️ Le passage 353-354 est à la bouche du carrefour du boulevard : la ligne d'arrêt de ce carrefour (la
    # tuile « S ») tombe SUR la voie. Un char qui y attendait son tour attendait sur les rails — et le train
    # qui passe le prenait de plein fouet. La ligne recule d'une tuile, hors des rails.
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const d = L.Train.donnees();
        let t0 = -1;                                   // un moment où le passage reste ouvert 400 images
        for (let t = 0; t < d.periode && t0 < 0; t += 20) {
          let ouvert = true;
          for (let k = 0; k < 400 && ouvert; k += 10) ouvert = !L.Train.passageFerme(1, t + k);
          if (ouvert) t0 = t;
        }
        aLHeure(L, t0);
        presDe(L, 350, 14);
        const v = L.Vehicules.creer('auto', (354 + 0.5) * L.TT, 12.5 * L.TT, -Math.PI / 2,
                                    { conducteur: 'trafic', etat: 'roule', sens: '^', couleur: '#cc3333' });
        L.Entites.indexer();
        let arrete = 0, surLaVoie = 0;
        for (let k = 0; k < 300; k++) {
          o.frame(1);
          if (v.vitesse < 0.05 && v.y > 5 * L.TT) { arrete++; if (Math.abs(v.y - d.yPx) <= L.TT) surLaVoie++; }
        }
        return { t0: t0, arrete: arrete, surLaVoie: surLaVoie };
    }""" % ATTENTE)
    assert r["t0"] >= 0 and r["arrete"] > 0 and r["surLaVoie"] == 0


def test_au_volant_on_defonce_la_barriere(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        aLHeure(L, avantLePassage(L, 1, 60) + 90);          // fermé, le train encore loin
        presDe(L, 350, 14);
        const v = L.Vehicules.creer('auto', 354.5 * L.TT, 7.5 * L.TT, -Math.PI / 2, { couleur: '#cc3333' });
        const avant = L.Train.brisee(1);
        L.B.joueur.dansVehicule = v;
        v.vx = 0; v.vy = -3;
        o.frame(1);
        const apres = L.Train.brisee(1);
        L.B.joueur.dansVehicule = null;
        return { avant: avant, apres: apres };
    }""" % ATTENTE)
    assert r == {"avant": False, "apres": True}


DEVANT = ATTENTE + """
function trainDevant(L, x, avance) {       // t où la tête arrive à x (px) dans `avance` images, vers l'est, au sol
  const d = L.Train.donnees();
  for (let t = 0; t < d.periode; t++) {
    const e = L.Train.etat(t + avance);
    if (e && e.sens > 0 && e.tete >= x && e.vitesse > 2) return t;
  }
  return -1;
}
"""


def test_un_char_sur_la_voie_est_pousse_et_prend_feu(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const x = 330.5 * L.TT, y = L.Train.donnees().yPx;
        aLHeure(L, trainDevant(L, x, 60));
        presDe(L, 330, 11);
        const v = L.Vehicules.creer('auto', x, y, 0, { couleur: '#cc3333' });
        L.Entites.indexer();
        const vie = v.vie;
        for (let k = 0; k < 120; k++) o.frame(1);
        return { hors: Math.abs(v.y - y) > L.TT, vie: v.vie < vie * 0.2 || !v.vivant };
    }""" % DEVANT)
    assert r == {"hors": True, "vie": True}


def test_un_char_arrete_sur_le_passage_est_pousse(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const x = 353.5 * L.TT, y = L.Train.donnees().yPx;
        aLHeure(L, trainDevant(L, x, 60));
        presDe(L, 350, 11);
        const v = L.Vehicules.creer('auto', x, y, -Math.PI / 2, { couleur: '#cc3333' });
        L.Entites.indexer();
        for (let k = 0; k < 120; k++) o.frame(1);
        return Math.abs(v.y - y) > L.TT;
    }""" % DEVANT)
    assert r is True


def test_le_joueur_sur_la_voie_se_reveille_a_l_hopital(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const x = 80.5 * L.TT, y = L.Train.donnees().yPx;   // loin de la gare des Friches : il roule vite
        aLHeure(L, trainDevant(L, x, 60));
        presDe(L, 80, 6);
        let hopital = false;
        const avant = L.Missions.hopital;
        L.Missions.hopital = function () { hopital = true; return avant.apply(this, arguments); };
        for (let k = 0; k < 120; k++) o.frame(1);
        return hopital;
    }""" % DEVANT)
    assert r is True


def test_sous_le_viaduc_le_train_ne_touche_personne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const x = 191.5 * L.TT, y = L.Train.donnees().yPx;
        aLHeure(L, trainDevant(L, x, 60));
        presDe(L, 191, 6);
        // ⚠️ Pas la vie : l'hôpital la rend pleine, et « même vie » ne prouverait rien. On guette les coups.
        let coups = 0;
        const blesser = L.Entites.blesser;
        L.Entites.blesser = function (e, n, source) { if (source && source.type === 'train') coups++; return blesser.apply(this, arguments); };
        for (let k = 0; k < 120; k++) o.frame(1);
        L.Entites.blesser = blesser;
        const e = L.Train.etat(L.Autobus.tempsDeLaPartie() - 60), ext = L.Train.etendue(e);
        return { coups: coups, passe: ext[1] > x };      // le témoin : le train est bien passé au-dessus
    }""" % DEVANT)
    assert r == {"coups": 0, "passe": True}


def test_les_sons_du_train_se_jouent_sans_fichier(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const S = L.Son.SFX;
        return ['klaxon_train', 'cloche_passage', 'roulement_train'].map(function (k) {
          try { S[k](100, 100, 1); return typeof S[k]; } catch (e) { return String(e); }
        });
    }""")
    assert r == ["function", "function", "function"]


def test_la_ligne_sur_la_grande_carte(banc):
    # Un pixel par tuile : pleine au sol, doublée sur le viaduc, en pointillé dans le tunnel, et trois gares.
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const pts = {}, faux = { fillStyle: '', fillRect: function (x, y, w, h) { pts[x + ',' + y] = w + 'x' + h; } };
        L.Train.dessinerSurLaCarte(faux, function (x, y) { return { x: Math.floor(x / L.TT), y: Math.floor(y / L.TT) }; });
        const d = L.Train.donnees(), a = function (x, y) { return !!pts[x + ',' + y]; };
        const tunnel = [];
        for (let x = d.tunnel; x < d.tunnel + 12; x++) tunnel.push(a(x, 6));
        return { sol: a(30, 6) && !a(30, 5), viaduc: a(200, 5) && a(200, 7) && !a(200, 6),
                 tunnel: tunnel.filter(Boolean).length, gares: d.gares.map(function (g) { return pts[(g[1] - 2) + ',4']; }) };
    }""")
    assert r["sol"] and r["viaduc"] and 3 <= r["tunnel"] <= 5 and r["gares"] == ["5x5", "5x5", "5x5"]


def test_un_long_char_qui_deborde_sur_la_voie_est_pousse(banc):
    # ⚠️ Le train regardait le CENTRE des chars : un autobus debout dans la rue, le nez sur les rails et le centre
    # à 18 px, passait dessous sans une égratignure (la relecture finale l'a mesuré).
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const d = L.Train.donnees(), x = 353.5 * L.TT;
        aLHeure(L, trainDevant(L, x, 60));
        presDe(L, 350, 11);
        const v = L.Vehicules.creer('autobus', x, d.yPx + 18 + L.TT, -Math.PI / 2, { couleur: '#cc3333' });
        v.y = d.yPx + v.def.longueur / 2 - 4;               // le nez 4 px sur la voie
        L.Entites.indexer();
        const vie = v.vie;
        for (let k = 0; k < 120; k++) o.frame(1);
        const nez = v.y - v.def.longueur / 2;
        return { degats: v.vie < vie || !v.vivant, degage: nez > d.yPx + 10 || v.y + v.def.longueur / 2 < d.yPx - 10 };
    }""" % DEVANT)
    assert r == {"degats": True, "degage": True}


def test_engage_sur_la_voie_on_ne_s_y_arrete_pas(banc):
    # ⚠️ « Jamais derrière soi » : un char qui avait passé la ligne reculée quand le carrefour se remplissait
    # s'arrêtait là où il était — sur les rails. Engagé, il va jusqu'au carrefour.
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const d = L.Train.donnees();
        let t0 = -1;
        for (let t = 0; t < d.periode && t0 < 0; t += 20) {
          let ouvert = true;
          for (let k = 0; k < 300 && ouvert; k += 10) ouvert = !L.Train.passageFerme(2, t + k);
          if (ouvert) t0 = t;
        }
        aLHeure(L, t0);
        presDe(L, 410, 14);
        // un STOP au carrefour du boulevard : à la ligne, on s'immobilise — mais la ligne est sur les rails
        const inter = L.Monde.intersectionA(416, 5);
        if (inter) inter.stop = '^';
        const v = L.Vehicules.creer('auto', 416.5 * L.TT, 0, -Math.PI / 2,
                                    { conducteur: 'trafic', etat: 'roule', sens: '^', couleur: '#cc3333' });
        v.y = 7 * L.TT + v.def.longueur / 2 - 3;          // le nez vient de passer la ligne reculée
        v.vitesse = 1;
        L.Entites.indexer();
        let surLaVoie = 0;
        for (let k = 0; k < 200; k++) {
          o.frame(1);
          const nez = v.y - v.def.longueur / 2, queue = v.y + v.def.longueur / 2;
          if (v.vitesse < 0.05 && nez < d.yPx + 10 && queue > d.yPx - 10) surLaVoie++;
        }
        return { t0: t0, surLaVoie: surLaVoie, stop: !!inter };
    }""" % ATTENTE)
    assert r["t0"] >= 0 and r["stop"] and r["surLaVoie"] == 0
