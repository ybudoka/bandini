"""Le bord de l'eau, 2e vague — les enfants jouent.

⚠️ **Jouer, c'est un `metier`, pas un costume.** La règle des sortes de gens est
écrite trois fois dans `pietons.py`, et le dépôt l'a déjà payée avec les filles
de la Brume : une sorte sans routine est un déguisement.
"""

#: Pose le joueur sur une grève et y fait naître les enfants.
POSER = """
    function greve(L) {
      const c = L.Monde.carte, TT = L.TT;
      function eau(tx, ty, d) {
        return L.Monde.estEau(tx + d, ty) || L.Monde.estEau(tx - d, ty)
            || L.Monde.estEau(tx, ty + d) || L.Monde.estEau(tx, ty - d);
      }
      // ⚠️ UNE VRAIE GREVE, pas le premier grain de sable venu. La carte porte
      // des bouts de rivage de quelques tuiles ; le premier trouve en balayant
      // du nord n'en comptait QUE CINQ dans toute la bulle, dont aucune hors
      // champ — il n'y naissait personne, et le juge accusait le moteur.
      let mieux = null, plus = 0;
      for (let ty = 6; ty < c.h - 6; ty += 2) {
        for (let tx = 6; tx < c.w - 6; tx += 2) {
          if (L.Monde.glyphe(tx, ty) !== 's' || !L.Monde.marchablePieton(tx, ty)) continue;
          if (!eau(tx, ty, 1) && !eau(tx, ty, 2)) continue;
          let n = 0;
          for (let dy = -12; dy <= 12; dy++) for (let dx = -12; dx <= 12; dx++) {
            if (L.Monde.glyphe(tx + dx, ty + dy) === 's') n++;
          }
          if (n > plus) { plus = n; mieux = { tx: tx, ty: ty, x: tx * TT + 8, y: ty * TT + 8, sable: n }; }
        }
      }
      return plus >= 40 ? mieux : null;
    }
    function enfants(L) {
      return L.B.entites.filter(function (e) { return e.metier === 'baigneur' && e.vivant; });
    }
"""


def test_des_enfants_naissent_sur_la_greve_et_jouent(banc, paquet):
    """Une grève vide est exactement ce qu'on avait avant la vague. ⚠️ Et ils
    naissent **hors champ** : personne ne voit apparaître un enfant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        %s
        const g = greve(L);
        if (!g) return { greve: false };
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        let vus = 0;
        for (let i = 0; i < 900; i++) {
          o.frame(1);
          for (const e of enfants(L)) if (e.t < 2 && L.Entites.visibleAEcran(e.x, e.y, 0)) vus++;
        }
        const baigneurs = enfants(L);
        const petits = baigneurs.filter(function (e) { return e.sprite === 'enfant'; });
        const jeux = {};
        for (const e of baigneurs) if (e.jeu) jeux[e.jeu] = (jeux[e.jeu] || 0) + 1;
        const f = L.B.defs.pietons.plage;
        return { greve: true, n: petits.length, max: f.enfants,
                 grands: baigneurs.length - petits.length, maxGrands: f.adultes,
                 jeux: Object.keys(jeux), vus: vus,
                 intouchables: petits.every(function (e) { return e.intouchable; }) };
    }""" % POSER)
    assert r["greve"], "aucune grève trouvée sur la carte"
    assert r["n"] > 0, "pas un enfant sur la grève"
    assert r["n"] <= r["max"], "plus d'enfants que la fiche n'en veut (%s)" % r["n"]
    # ⚠️ ET DES GRANDS — Martin : « des gens s'il y a beaucoup de place ». Deux
    # plafonds, pas un : les enfants nés les premiers ne prennent pas leur place.
    assert r["grands"] > 0, "pas un grand sur la plage : des enfants seuls, c'est une cour d'école"
    assert r["grands"] <= r["maxGrands"], "plus de grands que la fiche n'en veut (%s)" % r["grands"]
    assert r["jeux"], "des enfants sur la grève, et aucun ne joue"
    assert r["vus"] == 0, "un enfant est apparu à l'écran"
    # ⚠️ Il reste un enfant : intouchable sur la grève comme ailleurs.
    assert r["intouchables"], "un enfant de la plage a perdu son intouchabilité"


def test_un_enfant_ne_depasse_jamais_la_premiere_tuile_d_eau(banc, paquet):
    """⚠️ **LE JUGE QUI COMPTE.** `intouchable` veut dire aujourd'hui « aucune
    arme, aucun char » ; sur la grève il doit dire aussi « pas l'eau ».

    ⚠️ **Mesuré, pour ne pas s'attribuer un correctif** : aucun piéton ne se noie
    dans le jeu — le souffle et `noyade` n'existent que pour le joueur. Ce juge
    ne répare donc rien : il **épingle** la garantie.

    ⚠️ Et ce qui la tient n'est aucun des deux gardes écrits pour ça : c'est
    qu'on ne donne **jamais** à un enfant de destination au-delà de la première
    tuile, et qu'il s'immobilise dès qu'il y a le pied. Mesuré — neutraliser l'un
    ou l'autre garde ne fait tomber aucun juge ; ce sont des ceintures, et elles
    sont commentées comme telles."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(32);
        %s
        const g = greve(L);
        if (!g) return { greve: false };
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        let auLarge = 0, dansLEau = 0, morts = 0, baigneurs = 0;
        for (let i = 0; i < 1800; i++) {
          o.frame(1);
          // ⚠️ LE GESTE, PAS LA CHANCE — la leçon du juge du ballon, apprise ici
          // le 16 sept. 2026. Le jeu se choisit à l'empreinte du baigneur et de
          // l'instant, et il dure une à trois minutes : en trente secondes, chacun
          // tire UNE fois. Le jour où la plage a gagné le soleil et la promenade,
          // puis la foire a changé la ville ailleurs, plus personne n'a tiré la
          // baignade, et le juge est tombé sur « il ne mesure rien ». On envoie
          // donc chaque baigneur à l'eau, par la même porte que la routine
          // (`bordDeLEau`) ; ce qu'on mesure ensuite — il s'arrête à la première
          // tuile — ne dépend plus d'un tirage.
          for (const e of enfants(L)) {
            if (e.envoye || e.etat !== 'flane' && e.etat !== 'arret' && e.etat !== 'cap') continue;
            const bord = L.Entites.bordDeLEau(e);
            if (!bord) continue;
            e.envoye = true;
            e.jeu = 'baignade'; e.jeuT = 400;
            e.cap = bord; e.capT = 0; e.etat = 'cap'; e.barbote = true;
          }
          for (const e of enfants(L)) {
            const tx = Math.floor(e.x / L.TT), ty = Math.floor(e.y / L.TT);
            if (!L.Monde.estEau(tx, ty)) continue;
            dansLEau++;
            // De l'eau sur les QUATRE cotes : il n'a plus de terre a portee.
            const cerne = L.Monde.estEau(tx + 1, ty) && L.Monde.estEau(tx - 1, ty)
                       && L.Monde.estEau(tx, ty + 1) && L.Monde.estEau(tx, ty - 1);
            if (cerne) auLarge++;
          }
          morts += L.B.entites.filter(function (e) {
            return e.metier === 'baigneur' && !e.vivant; }).length;
        }
        baigneurs = enfants(L).length;
        return { greve: true, auLarge: auLarge, dansLEau: dansLEau, morts: morts, n: baigneurs };
    }""" % POSER)
    assert r["greve"], "aucune grève trouvée"
    assert r["n"] > 0, "plus un enfant à la fin : le juge ne mesure rien"
    # ⚠️ Et il faut qu'ils y soient ENTRÉS : sans cette ligne, le juge passerait
    # tout aussi bien sur une plage où personne ne se mouille jamais les pieds.
    assert r["dansLEau"] > 0, "aucun enfant n'est entré dans l'eau : le juge ne mesure rien"
    assert r["auLarge"] == 0, "un enfant est parti au large (%s images)" % r["auLarge"]
    assert r["morts"] == 0, "un enfant est mort sur la grève"


def test_un_enfant_ne_joue_pas_au_chateau_sans_chateau(banc, paquet):
    """⚠️ Un enfant qui « joue au château » sans château à portée est un enfant
    planté devant rien. On choisit parmi ce qui est **là** — et si le château
    qu'il rebâtissait n'y est plus, il s'en cherche un autre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(33);
        %s
        const g = greve(L);
        if (!g) return { greve: false };
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        o.frame(600);
        // On rase tous les châteaux de la bulle : plus personne ne peut y jouer.
        for (const d of L.B.entites.filter(function (e) { return e.decor === 'chateau_sable'; })) {
          L.Entites.briser(d);
        }
        L.Entites.indexer();
        o.frame(300);
        const restants = enfants(L).filter(function (e) { return e.jeu === 'chateau'; });
        const debout = L.B.entites.filter(function (e) {
          return e.decor === 'chateau_sable' && !e.brise; }).length;
        return { greve: true, joueursDeChateau: restants.length, debout: debout,
                 n: enfants(L).length };
    }""" % POSER)
    assert r["greve"], "aucune grève trouvée"
    assert r["n"] > 0, "plus un enfant : le juge ne mesure rien"
    assert r["debout"] == 0, "des châteaux ont survécu : le juge ne mesure rien"
    assert r["joueursDeChateau"] == 0, (
        "%s enfants jouent encore au château sans château" % r["joueursDeChateau"])


def test_le_ballon_va_d_un_enfant_a_l_autre_et_ne_reste_pas_seul(banc, paquet):
    """Deux enfants et un ballon qui va de l'un à l'autre. C'est tout, et ça
    suffit — un décor qui **bouge** se voit de trois écrans.

    ⚠️ Et un enfant oublié **emporte son ballon** : sans ça, la balle reste à
    voler toute seule au bord de l'eau, pour toujours."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(34);
        %s
        const g = greve(L);
        if (!g) return { greve: false };
        const f = L.B.defs.pietons.plage;
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        // On force le jeu de ballon sur deux enfants : le juge mesure le GESTE,
        // pas la chance d'un tirage à trois branches.
        let paire = null;
        for (let i = 0; i < 1200 && !paire; i++) {
          o.frame(1);
          const petits = enfants(L);
          for (let a = 0; a < petits.length && !paire; a++) {
            for (let b = a + 1; b < petits.length; b++) {
              const d = Math.hypot(petits[a].x - petits[b].x, petits[a].y - petits[b].y);
              if (d < f.ballon_px && d > f.ballon_min_px) {
                paire = [petits[a], petits[b]]; break;
              }
            }
          }
        }
        // ⚠️ **ET S'ILS NE SE RAPPROCHENT PAS D'EUX-MÊMES, ON LES RAPPROCHE.** Le
        // juge forçait déjà le jeu et lançait lui-même le ballon — « le geste, pas
        // la chance » — mais il attendait encore que deux enfants tombent à
        // portée par hasard. Mesuré le 16 sept. 2026 : même grève, mêmes quatre
        // enfants, et leurs promenades changent dès que la ville change ailleurs
        // (ce jour-là, les chaloupes ont quitté les mares du nord pour le port).
        // On pose un second enfant à mi-portée d'un premier, sur du sol où l'on
        // se tient (la grève borde un bout de quai et de gazon : un enfant qui
        // joue au bord de l'eau n'a pas toujours du sable des deux côtés) ; tout
        // ce que le juge mesure ensuite — le vol, les deux côtés, le ballon qu'on
        // emporte — ne dépend pas de la façon dont ils se sont trouvés.
        if (!paire) {
          // ⚠️ Le plus PROCHE du joueur d'abord : un ballon ne vole que s'il est
          // actif, et il ne l'est que dans la bulle de celui qui regarde.
          const j = L.B.joueur, d = (f.ballon_min_px + f.ballon_px) / 2;
          const petits = enfants(L).sort(function (u, v) {
            return Math.hypot(u.x - j.x, u.y - j.y) - Math.hypot(v.x - j.x, v.y - j.y); });
          for (let k = 0; k < petits.length && !paire; k++) {
            const a = petits[k], b = petits[(k + 1) %% petits.length];
            if (a === b) break;
            for (const [dx, dy] of [[d, 0], [-d, 0], [0, d], [0, -d]]) {
              const tx = Math.floor((a.x + dx) / L.TT), ty = Math.floor((a.y + dy) / L.TT);
              if (L.Monde.marchablePieton(tx, ty) && !L.Monde.estEau(tx, ty)) {
                b.x = a.x + dx; b.y = a.y + dy;
                j.x = a.x + dx / 2; j.y = a.y + dy / 2 - 5 * L.TT;
                L.Monde.centrerCamera(j.x, j.y);
                L.Entites.indexer();
                paire = [a, b]; break;
              }
            }
          }
        }
        if (!paire) return { greve: true, paire: false };
        const [a, b] = paire;
        // ⚠️ On LANCE le ballon nous-mêmes. Le choix du jeu se tire à l'empreinte
        // de l'enfant (jamais au dé du jeu) : attendre qu'il tombe sur « ballon »
        // serait mesurer un tirage, pas le geste que ce juge annonce.
        a.jeu = 'ballon'; a.jeuT = 600;
        L.Entites.lancerLeBallon(a, b, L.B.defs.pietons.plage);
        const ballons = function () {
          return L.B.entites.filter(function (e) { return e.type === 'ballon' && e.actif; });
        };
        const avant = ballons().length;
        const cotes = {};
        let bouge = 0, x0 = ballons()[0] ? ballons()[0].x : 0;
        for (let i = 0; i < 400; i++) {
          o.frame(1);
          const bal = ballons()[0];
          if (!bal) break;
          if (Math.abs(bal.x - x0) > 0.01) bouge++;
          x0 = bal.x;
          cotes[bal.vers === a ? 'a' : 'b'] = true;
        }
        // On oublie les deux enfants : le ballon doit partir avec eux.
        L.B.joueur.x += 4000;
        o.frame(120);
        return { greve: true, paire: true, avant: avant, bouge: bouge,
                 cotes: Object.keys(cotes).length, orphelins: ballons().length };
    }""" % POSER)
    assert r["greve"], "aucune grève trouvée"
    assert r["paire"], "jamais deux enfants assez proches pour se lancer un ballon"
    assert r["avant"] == 1, "le ballon n'est pas apparu (%s)" % r["avant"]
    assert r["bouge"] > 50, "le ballon n'a pas bougé (%s images)" % r["bouge"]
    assert r["cotes"] == 2, "le ballon ne va que dans un sens"
    assert r["orphelins"] == 0, "un ballon vole tout seul après l'oubli des enfants"


def test_les_baigneurs_ne_naissent_que_sur_une_plage_declaree(banc, paquet):
    """Retour de Martin : des gens « s'il y a beaucoup de place, pas juste des
    petits morceaux de plage ». ⚠️ Pas au bord d'un étang de parc : son liseré de
    sable touche l'eau aussi, et la première règle (« du sable avec l'eau à trois
    tuiles ») y faisait naître des enfants. C'est la carte qui dit où sont les
    plages (`plages`), pas le sable."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(35);
        %s
        const c = L.Monde.carte, TT = L.TT, plages = c.def.plages;
        const baigneurs = function () {
          return L.B.entites.filter(function (e) { return e.metier === 'baigneur' && e.vivant; });
        };
        // Un bord d'étang : du sable qui touche l'eau, à soixante tuiles de toute plage.
        let etang = null;
        for (let ty = 2; ty < c.h - 2 && !etang; ty++) {
          for (let tx = 2; tx < c.w - 2 && !etang; tx++) {
            if (L.Monde.glyphe(tx, ty) !== 's' || !L.Monde.marchablePieton(tx, ty)) continue;
            if (!(L.Monde.estEau(tx + 1, ty) || L.Monde.estEau(tx - 1, ty)
                  || L.Monde.estEau(tx, ty + 1) || L.Monde.estEau(tx, ty - 1))) continue;
            const loin = plages.every(function (p) {
              const dx = Math.max(p.x - tx, 0, tx - (p.x + p.l));
              const dy = Math.max(p.y - ty, 0, ty - (p.y + p.h));
              return dx + dy > 60;
            });
            if (loin) etang = { x: tx * TT + 8, y: ty * TT + 8 };
          }
        }
        if (!etang) return { etang: false };
        // ⚠️ À CÔTÉ de l'étang, pas dessus : on naît HORS CHAMP, et un joueur posé
        // sur l'étang l'avait à l'écran — personne n'y naissait de toute façon, et
        // le juge passait même sans la règle (mesuré en la retirant).
        let horsChamp = false;
        for (const [dx, dy] of [[22, 0], [-22, 0], [0, 14], [0, -14]]) {
          L.B.joueur.x = etang.x + dx * TT; L.B.joueur.y = etang.y + dy * TT;
          L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
          if (!L.Entites.visibleAEcran(etang.x, etang.y, 24)) { horsChamp = true; break; }
        }
        if (!horsChamp) return { etang: true, horsChamp: false };
        L.Entites.indexer();
        o.frame(900);
        const aLEtang = baigneurs().length;
        // Puis une vraie plage : chacun y naît DEDANS.
        const g = greve(L);
        if (!g) return { etang: true, greve: false };
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        let nes = 0, horsPlage = 0;
        for (let i = 0; i < 900; i++) {
          o.frame(1);
          for (const e of baigneurs()) {
            if (e.t >= 2) continue;
            nes++;
            if (!L.Entites.plageEn(Math.floor(e.x / TT), Math.floor(e.y / TT))) horsPlage++;
          }
        }
        return { etang: true, greve: true, aLEtang: aLEtang, nes: nes, horsPlage: horsPlage };
    }""" % POSER)
    assert r["etang"], "aucun bord d'étang loin des plages : le juge ne mesure rien"
    assert r.get("horsChamp", True), "l'étang reste à l'écran : le juge ne mesure rien"
    assert r["greve"], "aucune grève trouvée"
    assert r["aLEtang"] == 0, "%s baigneurs au bord d'un étang de parc" % r["aLEtang"]
    assert r["nes"] > 0, "personne n'est né sur la plage : le juge ne mesure rien"
    assert r["horsPlage"] == 0, "%s baigneurs nés hors d'une plage déclarée" % r["horsPlage"]


def test_un_grand_se_fait_bronzer_sur_une_serviette_libre(banc, paquet):
    """Le jeu des grands, comme le château est celui des petits : une serviette ou
    une chaise longue LIBRE, et on y reste. ⚠️ Libre : deux baigneurs sur la même
    serviette, c'est un corps dans l'autre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(36);
        %s
        const g = greve(L);
        if (!g) return { greve: false };
        const TT = L.TT;
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        o.frame(900);
        const grands = enfants(L).filter(function (e) { return e.sprite !== 'enfant'; });
        if (grands.length < 2) return { greve: true, grands: grands.length };
        const a = grands[0], b = grands[1];
        // ⚠️ Le geste, pas la chance : on lui donne le jeu, comme le juge du ballon.
        const lit = L.Entites.litLibre(a, 400);
        if (!lit) return { greve: true, grands: grands.length, lit: false };
        a.jeu = 'bronzer'; a.lit = lit; a.jeuT = 5000;
        a.cap = { x: lit.x * TT + 8, y: lit.y * TT + 8 }; a.capT = 0; a.etat = 'cap';
        const prisPourB = L.Entites.litLibre(b, 100000) === lit;
        let auSoleil = 0;
        for (let i = 0; i < 900; i++) {
          o.frame(1);
          const d = Math.hypot(a.x - (lit.x * TT + 8), a.y - (lit.y * TT + 8));
          if (d <= 14 && a.etat === 'arret' && a.jeu === 'bronzer') auSoleil++;
        }
        return { greve: true, grands: grands.length, lit: true, prisPourB: prisPourB,
                 auSoleil: auSoleil, vivant: a.vivant };
    }""" % POSER)
    assert r["greve"], "aucune grève trouvée"
    assert r["grands"] >= 2, "moins de deux grands sur la plage (%s)" % r["grands"]
    assert r["lit"], "pas une serviette ni une chaise longue à portée"
    assert not r["prisPourB"], "la même serviette est libre pour deux baigneurs"
    assert r["auSoleil"] > 300, "il n'est jamais resté sur sa serviette (%s images)" % r["auSoleil"]
