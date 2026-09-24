"""M12, 7e vague — la bagarre de gangs, au banc.

⚠️ **Le joueur n'est ni la cause ni la cible.** Trois mécanismes du dépôt ne
connaissaient qu'une seule réponse à la violence : « s'en prendre au joueur ».
`alerter` retournait contre lui toute gang à portée, `blesser` faisait de même
du blessé, et `majAttaque` y ramenait tout piéton qui finissait son coup. Chacun
a son juge ici.
"""

#: Va se planter en vue d'une frontière, et allume la rixe. ⚠️ Il ESSAIE
#: plusieurs points : la frontière passe au milieu d'une rue qui longe parfois
#: l'eau, un quai ou une façade, et un point sans trottoir des deux bords n'est
#: pas un lieu de bagarre — c'est exactement ce que le jeu vérifie aussi.
ALLUMER = """
    function allumer(L) {
      const f = L.B.defs.pietons.bagarre, TT = L.TT, j = L.B.joueur;
      const d = (f.trop_pres_px + f.rayon_px) / 2;
      for (const ligne of L.B.defs.pietons.frontieres) {
        const vertical = ligne.axe === 'v';
        const debut = vertical ? ligne.y : ligne.x;
        for (let k = 3; k < ligne.long - 3; k++) {
          const le = debut + k;
          const cx = (vertical ? ligne.x : le) * TT + 8, cy = (vertical ? le : ligne.y) * TT + 8;
          for (const sens of [-1, 1]) {
            j.x = cx + (vertical ? sens * d : 0);
            j.y = cy + (vertical ? 0 : sens * d);
            L.Monde.centrerCamera(j.x, j.y);
            L.Entites.indexer();
            const nes = L.Entites.allumerLaBagarre(f);
            if (nes >= f.membres * 2) { L.Entites.indexer(); return { ligne: ligne, nes: nes }; }
            for (let i = L.B.entites.length - 1; i >= 0; i--) {
              if (L.B.entites[i].bagarre) L.Entites.retirer(L.B.entites[i]);
            }
            L.Entites.indexer();
          }
        }
      }
      return null;
    }
    function rixeurs(L) {
      return L.B.entites.filter(function (e) { return e.bagarre; });
    }
"""


def test_deux_gangs_se_tombent_dessus_a_leur_frontiere(banc):
    """Le geste lui-même : deux camps, chacun de son bord de la rue, qui se
    rejoignent et se cognent dessus.

    ⚠️ `a` est la gang du petit côté (ouest ou nord) et `b` celle du grand : si
    la convention de `pietons.frontieres` ne tenait pas, les deux camps seraient
    nés du même trottoir et se seraient battus sans jamais traverser la rue."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(11);
        %s
        const trouve = allumer(L);
        if (!trouve) return { trouve: false };
        const f = L.B.defs.pietons.bagarre, TT = L.TT;
        const gens = rixeurs(L);
        const vertical = trouve.ligne.axe === 'v';
        const bord = vertical ? trouve.ligne.x * TT : trouve.ligne.y * TT;
        // De quel côté de la ligne chacun est-il né ?
        const cotes = {};
        for (const e of gens) {
          const ou = (vertical ? e.x : e.y) < bord ? 'petit' : 'grand';
          (cotes[e.gang] = cotes[e.gang] || {})[ou] = true;
        }
        const vieAvant = gens.reduce(function (s, e) { return s + e.vie; }, 0);
        const vus = gens.filter(function (e) { return L.Entites.visibleAEcran(e.x, e.y, 0); }).length;
        o.frame(420);
        const vivants = gens.filter(function (e) { return e.vivant; });
        return {
          trouve: true, nes: trouve.nes, membres: f.membres,
          gangs: Object.keys(cotes).length,
          a: cotes[trouve.ligne.a] || {}, b: cotes[trouve.ligne.b] || {},
          vus: vus,
          vieApres: vivants.reduce(function (s, e) { return s + e.vie; }, 0)
            + (gens.length - vivants.length) * 0,
          vieAvant: vieAvant,
          touches: gens.filter(function (e) { return !e.vivant || e.vie < e.vieMax; }).length,
        };
    }""" % ALLUMER)
    assert r["trouve"], "aucune frontière de la ville n'a ses deux trottoirs"
    assert r["nes"] == r["membres"] * 2, "un camp est arrivé incomplet"
    assert r["gangs"] == 2, "une seule gang s'est présentée"
    # ⚠️ Chacun de SON bord — c'est la convention de `frontieres()` qui le dit.
    assert r["a"] == {"petit": True}, "la gang du petit côté n'y est pas"
    assert r["b"] == {"grand": True}, "la gang du grand côté n'y est pas"
    # ⚠️ Et personne ne s'est matérialisé sous les yeux du joueur.
    assert r["vus"] == 0, "des hommes sont apparus à l'écran"
    assert r["touches"] >= 2, "ils se sont regardés en chiens de faïence"
    assert r["vieApres"] < r["vieAvant"], "personne n'a pris un coup"


def test_le_joueur_ne_paie_pas_la_bagarre(banc):
    """⚠️ **Ce n'est PAS lui qui la paie**, et ça se vérifie sur les deux
    compteurs qui le suivent. Pas d'étoile : la police du jeu est centrée sur
    lui, et signaler le geste d'un autre lui en mettrait une. Et pas un mort à
    son nom : `stats.tues` tire la manchette du Clairon (« UN MORT DANS LA
    RUE », « NUIT ROUGE AU FAUBOURG ») et le bilan de fin de mission — créditer
    le joueur d'une rixe qu'il a regardée de loin est un mensonge imprimé.

    ⚠️ Rouge avant : `tuer` comptait TOUTE mort de piéton, quelle qu'en soit la
    cause. Le même défaut créditait déjà le joueur des passants fauchés par un
    char du trafic."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ Ce juge mesure le crime d'autrui SANS méprise : la méprise (M12) a les siens
        // (`test_crime_d_autrui_js.py`), et une empreinte qui tombe bien ne doit rien y changer.
        L.B.defs.recherche.autrui.chance = 0;
        L.graine(12);
        %s
        const trouve = allumer(L);
        if (!trouve) return { trouve: false };
        // On les rend fragiles : il FAUT des morts, sinon le juge ne mesure
        // que la moitié de ce qu'il annonce.
        for (const e of rixeurs(L)) e.vie = 6;
        L.B.partie.stats.tues = 0;
        L.B.recherche.etoiles = 0;
        L.B.crimes.length = 0;
        o.frame(600);
        return { trouve: true, tues: L.B.partie.stats.tues,
                 etoiles: L.B.recherche.etoiles,
                 crimes: L.B.crimes.length,
                 morts: rixeurs(L).filter(function (e) { return !e.vivant; }).length };
    }""" % ALLUMER)
    assert r["trouve"], "aucune frontière n'a ses deux trottoirs"
    assert r["morts"] >= 1, "personne n'est tombé : le juge ne mesure rien (%s)" % r
    assert r["tues"] == 0, "le joueur est crédité de %s morts qu'il n'a pas faits" % r["tues"]
    assert r["etoiles"] == 0, "le joueur écope de %s étoiles pour une rixe" % r["etoiles"]
    assert r["crimes"] == 0, "la rixe a été signalée comme un crime du joueur"


def test_ceux_qui_se_battent_ne_se_retournent_pas_contre_le_joueur(banc):
    """⚠️ **Le défaut central de la vague, et il tenait en trois endroits.**
    `attaque_joueur` est le seul état d'attaque du jeu, et trois mécanismes y
    ramenaient tout le monde : `alerter` (toute gang à portée d'un coup),
    `blesser` (le blessé lui-même) et `majAttaque` (tout piéton qui finit son
    coup). Six hommes qui se tapaient dessus se retournaient donc contre le
    joueur au premier poing — et il n'avait rien fait, il passait par là.

    Le juge regarde CHAQUE image, pas seulement la dernière : le défaut est un
    aller-retour, et un état lu une fois sur cent l'aurait manqué."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(13);
        %s
        const trouve = allumer(L);
        if (!trouve) return { trouve: false };
        const f = L.B.defs.pietons.bagarre;
        let contreLeJoueur = 0, fuites = 0, coups = 0;
        for (let i = 0; i < 600; i++) {
          o.frame(1);
          for (const e of rixeurs(L)) {
            if (e.etat === 'attaque_joueur') contreLeJoueur++;
            if (e.etat === 'attaque') coups++;
            // ⚠️ On ne compte une fuite que s'il restait quelqu'un DEBOUT en
            // face : une fois le dernier rival à terre, la rixe est finie et
            // celui qui s'en va redevient un passant comme un autre.
            if (e.etat === 'fuit' && e.vivant && L.Entites.rivalDe(e, f)) fuites++;
          }
        }
        return { trouve: true, contreLeJoueur: contreLeJoueur, fuites: fuites, coups: coups };
    }""" % ALLUMER)
    assert r["trouve"], "aucune frontière n'a ses deux trottoirs"
    assert r["coups"] > 0, "personne n'a frappé : le juge ne mesure rien (%s)" % r
    assert r["contreLeJoueur"] == 0, "la rixe s'est retournée contre le joueur (%s images)" % r["contreLeJoueur"]
    assert r["fuites"] == 0, "un homme de la rixe a détalé au lieu de se battre"


def test_le_joueur_qui_cogne_recoit_la_gang_sur_le_dos(banc):
    """L'autre moitié de la règle, et elle compte autant : on a appris à la
    rixe à ignorer le joueur, il ne faut pas qu'elle l'ignore quand il ENTRE
    dedans. Un coup de sa part, et la gang lui tombe dessus comme chez elle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(14);
        %s
        const trouve = allumer(L);
        if (!trouve) return { trouve: false };
        o.frame(60);
        const cible = rixeurs(L).find(function (e) { return e.vivant; });
        // ⚠️ Le courage est un DÉ (0,9 pour une Cravate) : un juge qui le
        // laisse rouler mesure la chance, pas la règle. On le met à 1 et on
        // mesure ce qu'on annonce — qu'un coup du joueur rouvre la riposte.
        cible.courage = 1;
        L.Entites.blesser(cible, 5, L.B.joueur, {});
        return { trouve: true, etat: cible.etat };
    }""" % ALLUMER)
    assert r["trouve"], "aucune frontière n'a ses deux trottoirs"
    assert r["etat"] == "attaque_joueur", (
        "le joueur a cogné et la gang l'a ignoré (%s)" % r["etat"])


def test_la_bagarre_finit(banc):
    """⚠️ Deux survivants qui se tapent dessus jusqu'à la fin des temps ne sont
    pas une bagarre : c'est un décor qui grince. Elle s'arrête au bout de son
    temps, ou dès qu'il ne reste plus personne debout en face."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(15);
        %s
        const trouve = allumer(L);
        if (!trouve) return { trouve: false };
        const f = L.B.defs.pietons.bagarre;
        o.frame(f.duree_images + 120);
        const restes = rixeurs(L);
        return { trouve: true,
                 debout: restes.filter(function (e) { return e.vivant; }).length,
                 encore: restes.filter(function (e) { return e.etat === 'bagarre'; }).length };
    }""" % ALLUMER)
    assert r["trouve"], "aucune frontière n'a ses deux trottoirs"
    assert r["encore"] == 0, "%s hommes se battent encore après la durée de la fiche" % r["encore"]


def test_une_rixe_ne_tire_pas_un_seul_de_du_jeu(banc):
    """⚠️ **La leçon du char en panne, rejouée.** Ce qui s'allume pour la ville
    ne doit pas décaler le hasard du jeu : chaque dé tiré déplace tous ceux qui
    suivent, et une panne qui prenait un dé au passage a fait tomber quatre
    juges d'un coup — dont aucun ne parlait de pannes.

    Ici, ce qu'on mesure est le TIRAGE : mille quatre cent quarante fois par
    jour de jeu, `majBagarre` décide si une rixe commence. Loin de toute
    frontière il ne se passe rien — et il ne doit rien coûter non plus."""
    def compter(chance):
        return banc("""function (L, o) {
            L.Jeu.commencer();
            L.graine(6);
            const f = L.B.defs.pietons.bagarre, TT = L.TT, c = L.Monde.carte;
            // Un coin de ville hors de portée de toute frontière : `majBagarre`
            // y tire sa minute et repart les mains vides.
            let place = null;
            for (let ty = 5; ty < c.h - 5 && !place; ty += 5) {
              for (let tx = 5; tx < c.w - 5 && !place; tx += 5) {
                const x = tx * TT + 8, y = ty * TT + 8;
                if (L.Monde.marchablePieton(tx, ty) && !L.Entites.frontiereProche(x, y, f)) place = { x: x, y: y };
              }
            }
            L.B.joueur.x = place.x; L.B.joueur.y = place.y;
            L.Monde.centrerCamera(place.x, place.y);
            // ⚠️ On éteint la rixe PAR SA FICHE : c'est la seule façon d'être
            // sûr que les deux parties ne diffèrent QUE par elle.
            f.chance_par_minute = %s;
            const vrai = L.B.rng;
            let n = 0;
            L.B.rng = function () { n++; return vrai(); };
            o.frame(600);
            L.B.rng = vrai;
            return { des: n, rixes: L.B.entites.filter(function (e) { return e.bagarre; }).length };
        }""" % chance)

    avec, sans = compter(1), compter(0)
    assert avec["rixes"] == sans["rixes"] == 0, (
        "une rixe a eu lieu loin de toute frontière : le juge ne mesure plus le tirage (%s, %s)"
        % (avec, sans))
    assert avec["des"] == sans["des"], (
        "le tirage de la rixe a pris %s dés du jeu : tout ce qui suit est décalé"
        % (avec["des"] - sans["des"]))


def test_seules_deux_gangs_se_frappent_entre_elles(banc):
    """⚠️ **La seule inimitié que la ville connaisse.** L'arc de mêlée refusait
    tout piéton contre tout piéton (« ils ne se battent pas entre eux ») ; il
    laisse passer deux gangs, et RIEN d'autre. Écrit là plutôt que dans l'état
    `bagarre`, c'est le même test qui protège le passant venu regarder : un coup
    perdu dans une rixe ne doit pas le faucher."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(21);
        const cas = [['passant', 'passant'], ['cravate', 'passant'],
                     ['cravate', 'cravate'], ['cravate', 'morue'], ['morue', 'cravate']];
        const out = [];
        for (const [qui, sur] of cas) {
          // ⚠️ On repart d'une rue vide : un badaud oublié dans l'arc d'un tour
          // précédent ferait mentir le suivant.
          for (let i = L.B.entites.length - 1; i >= 0; i--) {
            if (L.B.entites[i].type === 'pieton') L.Entites.retirer(L.B.entites[i]);
          }
          const a = o.poser(qui, 60, 0), b = o.poser(sur, 78, 0);
          a.arme = 'poings';
          a.angle = Math.atan2(b.y - a.y, b.x - a.x);
          const avant = b.vie;
          L.Combat.frapper(a, false);
          for (let i = 0; i < 24; i++) { L.Entites.indexer(); L.Combat.maj(); }
          out.push([qui, sur, avant - b.vie]);
        }
        return out;
    }""")
    perdu = {(qui, sur): d for qui, sur, d in r}
    assert perdu[("passant", "passant")] == 0, "deux passants se sont battus"
    assert perdu[("cravate", "passant")] == 0, "une gang a frappé un passant qui regardait"
    assert perdu[("cravate", "cravate")] == 0, "une gang s'est battue avec elle-même"
    assert perdu[("cravate", "morue")] > 0, "les deux gangs se sont ignorées"
    assert perdu[("morue", "cravate")] > 0, "l'inimitié ne va que dans un sens"


def test_le_brave_ne_se_jette_pas_sur_le_joueur_pour_le_geste_d_un_autre(banc):
    """⚠️ **`alerter` ne connaissait qu'une riposte : le joueur.** Une gang à
    portée d'un coup lui tombait dessus, et un passant courageux aussi — quel
    qu'en soit l'auteur. Ça se voyait déjà sans la rixe : un char du trafic qui
    fauchait quelqu'un, ou le voleur de char livré la vague d'avant, retournaient
    toute la gang du coin contre un joueur qui passait par là.

    Quand la menace est quelqu'un d'AUTRE, le courage ne peut pas se traduire en
    riposte — `attaque_joueur` ne sait viser que lui. On s'écarte, comme les
    autres. Et quand c'est bien lui, la règle d'avant reprend telle quelle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(22);
        const out = {};
        for (const qui of ['autre', 'joueur']) {
          for (let i = L.B.entites.length - 1; i >= 0; i--) {
            if (L.B.entites[i].type === 'pieton') L.Entites.retirer(L.B.entites[i]);
          }
          const gang = o.poser('cravate', 30, 0), brave = o.poser('ouvrier', -30, 0);
          brave.courage = 1;                     // on mesure la règle, pas le dé
          const tiers = o.poser('passant', 0, 30);
          L.Entites.indexer();
          L.Entites.alerter(tiers.x, tiers.y, qui === 'joueur' ? L.B.joueur : tiers, 3);
          out[qui] = { gang: gang.etat, brave: brave.etat };
        }
        return out;
    }""")
    assert r["autre"]["gang"] != "attaque_joueur", (
        "la gang s'en prend au joueur pour le geste d'un autre")
    assert r["autre"]["brave"] != "attaque_joueur", (
        "le brave s'en prend au joueur pour le geste d'un autre")
    # L'autre moitié : quand c'est bien lui, rien n'a changé.
    assert r["joueur"]["gang"] == "attaque_joueur", "la gang ne répond plus au joueur"
    assert r["joueur"]["brave"] == "attaque_joueur", "le brave ne répond plus au joueur"


def test_une_rixe_qu_on_ne_voit_pas_ne_s_entend_pas(banc):
    """⚠️ Retour de Martin (16 sept. 2026) : « même que je veux pas entendre quand
    on les voit pas ». La rixe naît EXPRÈS hors de l'écran (personne ne se
    matérialise sous les yeux du joueur) — et chaque coup, chaque grognement
    partait au plein volume : on entendait six hommes se battre sans en voir un.

    On la laisse se battre hors champ, puis on va se planter à côté : les mêmes
    hommes, les mêmes coups, et seul l'écran décide."""
    r = banc("""async function (L, o) {
        const joues = o.brancherAudio(true);
        L.Jeu.commencer();
        L.Son.reveiller();
        L.graine(11);
        %s
        const trouve = allumer(L);
        if (!trouve) return { trouve: false };
        // ⚠️ **DE QUOI TENIR TOUT LE JUGE.** Six hommes qui se tapent dessus
        // pendant 420 images hors champ finissent par s'entretuer, et il n'en
        // reste plus assez pour se battre quand on arrive : le 17 sept. 2026,
        // un simple changement de rythme du trafic (« Les chars s'arretent
        // avant le passage ») a suffi a faire tomber un homme de plus, et ce
        // juge est tombe avec — sur `debout`, pas sur une seule de ses
        // assertions de son. Il mesure ce qu'on ENTEND, pas qui gagne : on leur
        // donne de la vie, et l'attrition cesse de decider a sa place.
        for (const e of rixeurs(L)) e.vie = 900;
        const vrai = L.Son.depuis, appels = [];
        L.Son.depuis = function (qui, effet) {
            const n = joues.length;
            const v = vrai(qui, effet);
            if (qui && qui.bagarre) {
                appels.push({ v: v, sources: joues.length - n,
                              vu: L.Entites.visibleAEcran(qui.x, qui.y, 8) });
            }
            return v;
        };
        // ⚠️ CENT CINQUANTE IMAGES HORS CHAMP, pas sept secondes. Mesure du
        // 17 sept. 2026 : en 420 images, un camp entier y passait (trois morts
        // sur six), les survivants n'avaient plus d'adversaire et la rixe etait
        // FINIE avant qu'on aille la voir — le juge concluait « a cote, on
        // n'entend rien » d'une bagarre qui n'existait plus. On mesure le
        // silence sur les premiers coups, pas sur la fin du monde.
        o.frame(150);
        const horsChamp = appels.splice(0);
        // On va voir : au milieu de ceux qui sont encore debout.
        const debout = rixeurs(L).filter(function (e) { return e.vivant && e.etat !== 'assomme'; });
        // ⚠️ ON FORCE LA REGLE, on ne joue pas la duree de la rixe. Elle dure
        // vingt-cinq secondes (`bagarre.duree_images`) et on vient d'en brûler
        // sept hors champ : le jour ou la ville a change autour (4e vague des
        // quartiers, 17 sept. 2026), les coups tombaient apres la fenetre et le
        // juge concluait « a cote, on n'entend rien ». Ce qu'il prouve n'est pas
        // le tempo d'une bagarre : c'est qu'a cote, ca s'entend.
        for (const e of rixeurs(L)) if (e.bagarreT !== undefined) e.bagarreT = Math.max(e.bagarreT, 900);
        const j = L.B.joueur;
        j.x = debout.reduce(function (s, e) { return s + e.x; }, 0) / debout.length;
        j.y = debout.reduce(function (s, e) { return s + e.y; }, 0) / debout.length;
        L.Monde.centrerCamera(j.x, j.y);
        L.Entites.indexer();
        // ⚠️ ON ECOUTE JUSQU'A ENTENDRE, pas trois cents images. Les coups d'une
        // rixe ne tombent pas a heure fixe : le jour ou la ville a change autour
        // (4e vague des quartiers, 17 sept. 2026), les six hommes se tapaient
        // encore dessus mais le premier coup arrivait apres la fenetre — et le
        // juge concluait « on n'entend rien ». Ce qu'il prouve n'est pas le tempo
        // de la bagarre : c'est qu'a cote, ca s'entend.
        for (let i = 0; i < 600 && !appels.length; i++) o.frame(1);
        o.frame(120);
        const enVue = appels.splice(0);
        L.Son.depuis = vrai;
        return { trouve: true, horsChamp: horsChamp, enVue: enVue, debout: debout.length };
    }""" % ALLUMER)
    assert r["trouve"], "aucune frontière de la ville n'a ses deux trottoirs"
    hors = r["horsChamp"]
    assert hors, "personne n'a frappé ni encaissé hors champ : le juge ne mesure rien"
    assert not any(a["vu"] for a in hors), "la rixe est entrée dans l'écran : ce n'est plus hors champ"
    assert all(a["v"] == 0 and a["sources"] == 0 for a in hors), (
        "on entend une rixe qu'on ne voit pas : %s" % [a for a in hors if a["v"] or a["sources"]][:3])
    assert r["debout"] >= 2, "la rixe s'est finie avant qu'on aille la voir"
    vue = r["enVue"]
    entendus = [a for a in vue if a["v"] > 0]
    assert entendus and all(a["sources"] > 0 for a in entendus), (
        "à côté de la rixe, on n'entend rien : %s" % vue[:3])
    assert all(a["vu"] for a in entendus), "on a entendu quelqu'un qu'on ne voyait pas"
