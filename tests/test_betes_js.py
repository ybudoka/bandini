"""M12, 9e vague — les goélands et les chats.

⚠️ **La vie qui n'est pas humaine.** « Ils ne comptent pour rien — ni témoins,
ni victimes — et c'est précisément ce qui les rend vivants : ils ne sont là que
pour être là. »
"""

#: Va planter le joueur là où une bête peut vivre, et l'y fait naître.
POSER = """
    function coin(L, espece) {
      const c = L.Monde.carte, TT = L.TT;
      for (let ty = 4; ty < c.h - 4; ty += 1) {
        for (let tx = 4; tx < c.w - 4; tx += 1) {
          if (!L.Entites.chezElle(espece, tx, ty)) continue;
          // Un coin qui en porte plusieurs : une seule tuile isolée ne laisse
          // pas la bête faire deux pas.
          let n = 0;
          for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) {
            if (L.Entites.chezElle(espece, tx + dx, ty + dy)) n++;
          }
          if (n < 12) continue;
          return { tx: tx, ty: ty, x: tx * TT + 8, y: ty * TT + 8 };
        }
      }
      return null;
    }
    function betes(L, espece) {
      // ⚠️ Elles ne sont PAS dans `B.entites` : elles ont leur liste, et c'est
      // la seule facon de tenir « elles ne comptent pour rien ».
      return L.Entites.betes().filter(function (e) { return !espece || e.espece === espece; });
    }
    function poser(L, espece, loin) {
      const p = coin(L, espece);
      if (!p) return null;
      L.B.joueur.x = p.x + (loin || 0); L.B.joueur.y = p.y;
      L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
      L.Entites.indexer();
      return p;
    }
"""


def test_chacune_vit_chez_elle(banc, paquet):
    """⚠️ **Chacun chez soi**, sinon ce ne sont pas deux bêtes mais deux dessins
    du même animal : le goéland au bord de l'eau, le chat dans les ruelles."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const out = {};
        for (const espece of ['goeland', 'chat']) {
          const p = coin(L, espece);
          if (!p) { out[espece] = null; continue; }
          L.B.joueur.x = p.x + 300; L.B.joueur.y = p.y;
          L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
          L.Entites.indexer();
          for (let i = 0; i < 400; i++) o.frame(1);
          const vues = betes(L, espece);
          out[espece] = {
            n: vues.length,
            chezElles: vues.every(function (e) {
              return L.Entites.chezElle(espece, Math.floor(e.x / L.TT), Math.floor(e.y / L.TT))
                  || e.fuite > 0;
            }),
            max: L.B.defs.pietons.betes[espece].combien,
          };
          for (const e of vues) L.Entites.retirer(e);
        }
        // Et les coins ne se confondent pas.
        const g = coin(L, 'goeland'), c = coin(L, 'chat');
        return { out: out, gChat: L.Entites.chezElle('chat', g.tx, g.ty),
                 cGoeland: L.Entites.chezElle('goeland', c.tx, c.ty) };
    }""" % POSER)
    for espece in ("goeland", "chat"):
        d = r["out"][espece]
        assert d, f"aucun coin pour un {espece} dans toute la ville"
        assert d["n"] > 0, f"pas un seul {espece}"
        assert d["n"] <= d["max"], f"{d['n']} {espece}s pour un plafond de {d['max']}"
        assert d["chezElles"], f"un {espece} a quitté son coin"
    assert not r["gChat"], "le coin du goéland est aussi celui du chat"
    assert not r["cGoeland"], "la ruelle du chat est aussi celle du goéland"


def test_rien_au_monde_ne_peut_atteindre_une_bete(banc, paquet):
    """⚠️ **LE JUGE QUI COMPTE.** Un goéland qu'on pourrait tuer serait une
    **cible** — et une cible demande un score, un crime, un juge. Elles ne sont
    ni témoins, ni victimes : `type: 'bete'` n'est ni `pieton` ni `joueur`, donc
    l'arc de mêlée ne les voit pas, `alerter` et `pietonsAutour` non plus, et
    `foule()` ne les compte pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(41);
        %s
        const p = poser(L, 'goeland', 260);
        if (!p) return { coin: false };
        for (let i = 0; i < 300; i++) o.frame(1);
        const vues = betes(L);
        if (!vues.length) return { coin: true, n: 0 };
        const g = vues[0];
        // On le colle au joueur et on frappe : l'arc ne doit pas le voir.
        g.x = L.B.joueur.x + 12; g.y = L.B.joueur.y;
        g.fuite = 0;
        L.Entites.indexer();
        o.viser(g);
        const avant = { x: g.x, y: g.y };
        L.Combat.frapper(L.B.joueur, false);
        for (let i = 0; i < 24; i++) { L.Entites.indexer(); L.Combat.maj(); }
        const blesse = L.Entites.blesser(g, 99, L.B.joueur, {});
        return {
          coin: true, n: vues.length,
          blesse: blesse,
          vivante: betes(L).indexOf(g) >= 0,
          // Elle n'entre dans aucun index de personnes.
          dansLaFoule: L.Entites.pietonsAutour(avant.x, avant.y, 40)
                         .some(function (q) { return q === g; }),
          // Ni témoin : `alerter` ne la voit pas.
          etat: g.etat === undefined ? null : g.etat,
          crimes: L.B.crimes.length, etoiles: L.B.recherche.etoiles,
        };
    }""" % POSER)
    assert r["coin"], "aucun coin de goéland"
    assert r["n"] > 0, "pas un goéland : le juge ne mesure rien"
    assert r["blesse"] is False, "on a blessé un goéland"
    assert r["vivante"], "le goéland a disparu sous un coup"
    assert r["dansLaFoule"] is False, "une bête est comptée parmi les gens"
    assert r["crimes"] == 0 and r["etoiles"] == 0, "frapper une bête est devenu un crime"


def test_elles_partent_avant_qu_on_les_touche(banc, paquet):
    """⚠️ Leur distance de fuite est plus grande que la portée de tout ce qui
    pourrait les atteindre. C'est ce qui évite d'avoir à répondre à « que se
    passe-t-il si je lui roule dessus » : **on n'y arrive pas** — même le chat
    confiant (`confiance_px`, 20 px) reste hors de portée d'un poing (12 px).

    ⚠️ Le goéland **s'élève** — l'altitude est un décalage de dessin, pas une
    position : rien ne se cogne dans un oiseau."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(42);
        %s
        const out = {};
        for (const espece of ['goeland', 'chat']) {
          for (const e of betes(L)) L.Entites.retirer(e);
          const p = poser(L, espece, 300);
          if (!p) { out[espece] = null; continue; }
          for (let i = 0; i < 400 && !betes(L, espece).length; i++) o.frame(1);
          const vues = betes(L, espece);
          if (!vues.length) { out[espece] = { n: 0 }; continue; }
          // ⚠️ **LA PLUS PROCHE, pas la première de la liste.** Une bête restée
          // d'un tour précédent, à deux mille pixels, est hors de la bulle : elle
          // ne bouge plus, et le juge la voyait « ne pas fuir » (0 px en 240
          // images, 17 sept. 2026). On approche celle qu'on approche.
          const bete = vues.slice().sort(function (a, b) {
            return Math.hypot(a.x - L.B.joueur.x, a.y - L.B.joueur.y)
                 - Math.hypot(b.x - L.B.joueur.x, b.y - L.B.joueur.y); })[0];
          const fiche = L.B.defs.pietons.betes[espece];
          // ⚠️ Le chat SEUL a une confiance (`confiance_px`, 2e vague, 22 sept. 2026) :
          // au pas, sans arme — l'état par défaut du joueur ici —, c'est CETTE
          // distance-là qui le fait fuir, pas `fuite_px` (réservé au sprint et à
          // l'arme au poing). Le goéland n'a pas cette clé : `fuite_px` pour lui.
          const seuil = fiche.confiance_px !== undefined ? fiche.confiance_px : fiche.fuite_px;
          const d0 = Math.hypot(bete.x - L.B.joueur.x, bete.y - L.B.joueur.y);
          // On s'approche : au seuil, elle doit être déjà partie.
          L.B.joueur.x = bete.x + seuil - 6; L.B.joueur.y = bete.y;
          L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
          o.frame(2);
          const partie = bete.fuite > 0;
          let monte = 0, eloigne = 0;
          const avant = Math.hypot(bete.x - L.B.joueur.x, bete.y - L.B.joueur.y);
          for (let i = 0; i < 60 && betes(L, espece).indexOf(bete) >= 0; i++) {
            o.frame(1);
            if (bete.altitude > monte) monte = bete.altitude;
          }
          eloigne = Math.hypot(bete.x - L.B.joueur.x, bete.y - L.B.joueur.y) - avant;
          out[espece] = { n: vues.length, d0: d0, partie: partie, monte: monte, eloigne: eloigne,
                          portee: seuil, pose: bete.v };
        }
        // Une portée de poing, pour comparer.
        const poings = paquetArme(L);
        return { out: out, poings: poings };
        function paquetArme(L) {
          const a = L.B.defs.armes.find(function (q) { return q.slug === 'poings'; });
          return a ? a.portee : 0;
        }
    }""" % POSER)
    for espece in ("goeland", "chat"):
        d = r["out"][espece]
        assert d and d["n"] > 0, f"pas un seul {espece} : le juge ne mesure rien"
        assert d["partie"], f"le {espece} n'a pas bougé quand on s'est approché"
        assert d["eloigne"] > 10, f"le {espece} ne s'éloigne pas ({d['eloigne']})"
        # ⚠️ Elle part de plus loin que le poing ne porte : on ne peut pas l'atteindre.
        assert d["portee"] > r["poings"], (
            f"un {espece} fuit à {d['portee']} px et un poing porte à {r['poings']}")
    assert r["out"]["goeland"]["monte"] > 4, "le goéland s'envole sans s'élever"
    assert r["out"]["chat"]["monte"] == 0, "le chat vole"


def test_le_chat_laisse_approcher_qui_marche_doucement_et_sans_arme(banc, paquet):
    """⚠️ **2e vague, « caresser le chat » (22 sept. 2026).** Le chat SEUL a une
    confiance (`pietons.BETES["chat"]["confiance_px"]`) : au pas, sans arme, il
    laisse venir bien plus près qu'un `fuite_px` normal — assez pour
    `interactions.CARESSER`. Courir (`esquive` tenue) ou sortir une arme, et il
    redevient aussi farouche que le goéland, qui n'a jamais cette clé."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(7);
        %s
        function approcher(sprint, arme) {
          for (const e of betes(L)) L.Entites.retirer(e);
          const p = poser(L, 'chat', 300);
          if (!p) return { pasDeChat: true };
          for (let i = 0; i < 400 && !betes(L, 'chat').length; i++) o.frame(1);
          const vues = betes(L, 'chat');
          if (!vues.length) return { pasDeChat: true };
          const chat = vues[0];
          L.B.joueur.arme = arme || 'poings';
          if (sprint) o.bouton('esquive', 'pointerdown');
          // Entre les deux portées : plus loin que `confiance_px` (rien à y craindre,
          // confiant), bien plus près que `fuite_px` (un chat ordinaire fuirait déjà).
          const c = L.B.defs.pietons.betes.chat;
          L.B.joueur.x = chat.x + c.confiance_px + 10; L.B.joueur.y = chat.y;
          L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
          o.frame(3);
          const out = { fuite: chat.fuite > 0, confiance: !!chat.confiance };
          if (sprint) o.bouton('esquive', 'pointerup');
          return out;
        }
        return { doux: approcher(false, null), sprint: approcher(true, null), arme: approcher(false, 'batte') };
    }""" % POSER)
    for cas in ("doux", "sprint", "arme"):
        assert not r[cas].get("pasDeChat"), f"{cas} : aucun chat dans toute la ville"
    assert r["doux"]["confiance"] and not r["doux"]["fuite"], \
        f"au pas, sans arme, à confiance_px le chat aurait dû rester : {r['doux']}"
    assert not r["sprint"]["confiance"] and r["sprint"]["fuite"], \
        f"au sprint, le chat aurait dû fuir comme avant : {r['sprint']}"
    assert not r["arme"]["confiance"] and r["arme"]["fuite"], \
        f"une arme à la main, le chat aurait dû fuir comme avant : {r['arme']}"


def test_une_bete_ne_tire_pas_un_seul_de_du_jeu(banc, paquet):
    """⚠️ **La leçon des dés, et c'est la quatrième fois cette semaine.** La
    dernière, les enfants de la grève naissaient au hasard et **le pickpocket a
    cessé de voler** — un juge qui ne parle pas de plage, tombé parce que chaque
    dé consommé décale tous ceux qui suivent.

    ⚠️ Le juge compte les dés **par appelant**, et pas en comparant deux parties :
    la comparaison globale mesurait autre chose qu'elle n'annonçait — le nombre de
    `remous` des enfants qui barbotent varie tout seul d'une partie à l'autre, et
    la différence qu'on lisait n'était pas celle des bêtes. Ici on nomme les
    fonctions des bêtes, et on exige qu'aucune n'apparaisse dans le compte."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(9);
        %s
        const p = coin(L, 'goeland');
        L.B.joueur.x = p.x + 300; L.B.joueur.y = p.y;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        const parSite = {};
        const vrai = L.B.rng;
        L.B.rng = function () {
          // Toute la pile : un dé tiré par une bête s'y voit, même si elle le
          // tire à travers une fonction commune.
          const pile = new Error().stack || '';
          for (const nom of ['naitreLesBetes', 'majBete', 'placeDeBete', 'avancerLaBete',
                             'sEnvoler', 'majFuite', 'chezElle']) {
            if (pile.indexOf(nom) >= 0) parSite[nom] = (parSite[nom] || 0) + 1;
          }
          return vrai();
        };
        o.frame(900);
        L.B.rng = vrai;
        return { parSite: parSite, betes: betes(L).length };
    }""" % POSER)
    assert r["betes"] > 0, "aucune bête n'a vécu : le juge ne mesure rien"
    assert r["parSite"] == {}, (
        "les bêtes ont tiré dans le dé du jeu : %s — tout ce qui suit est décalé"
        % r["parSite"])
