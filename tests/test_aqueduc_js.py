"""M12, 8e vague — le bris d'aqueduc, au banc.

⚠️ **Il arrive à une HEURE, pas à l'aube.** L'entrave du jour et la rue barrée
sont tirées au lever du jour et tiennent la journée ; celui-ci coule pendant
`minutes` minutes de jeu, puis la ville trouve la vanne.
"""

#: Cale la partie à une minute de jeu donnée, la conduite crevée à coup sûr.
#: ⚠️ On force `chance_par_heure` à 1 : un juge qui attend un tirage à trois
#: dixièmes mesure la chance, pas la règle.
POSER = """
    function poser(L, minute) {
      L.B.partie.jour = 3;
      L.B.partie.heure = (minute % 1440) / 1440;
      return L.Monde.brisDAqueduc();
    }
"""


def test_un_bris_coule_puis_la_ville_ferme_la_vanne(banc):
    """⚠️ **Une heure, un bris, et jamais deux qui se chevauchent.** C'est la
    fiche qui le garantit (`minutes` vaut moins de 60, un juge Python le tient) :
    sans cette borne, l'eau de 8 h coulerait encore pendant celle de 9 h, et
    « une conduite lâche » deviendrait « la ville fuit de partout »."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const f = L.B.defs.carte.aqueduc;
        f.chance_par_heure = 1;
        const debut = 8 * 60;
        const out = { au_debut: !!poser(L, debut), milieu: !!poser(L, debut + 20) };
        // ⚠️ La minute où l'eau s'arrête : `minutes` après le haut de l'heure.
        const fini = poser(L, debut + f.minutes + 1);
        out.apres = !!fini;
        // Et le suivant est un AUTRE bris : une conduite ne relâche pas au même
        // endroit une heure plus tard.
        const a = poser(L, debut), b = poser(L, debut + 60);
        out.ailleurs = !!(a && b && (a.x !== b.x || a.y !== b.y));
        out.une_tuile = !!(a && a.l === 1 && a.h === 1);
        return out;
    }""" % POSER)
    assert r["au_debut"], "la conduite n'a pas lâché au haut de l'heure"
    assert r["milieu"], "l'eau s'est arrêtée au milieu de l'heure"
    assert not r["apres"], "la ville n'a jamais trouvé la vanne"
    assert r["ailleurs"], "deux heures d'affilée, la même conduite"
    # ⚠️ C'est LA propriété sur laquelle tout repose : un trou d'une tuile ne
    # touche pas au champ de direction, donc il ne peut pas couper la ville.
    assert r["une_tuile"], "un bris couvre plus d'une tuile"


def test_un_bris_arrete_les_chars_et_pas_les_jambes(banc):
    """⚠️ **Un trou d'eau qui arrêterait tout le monde serait un mur**, et la
    ville n'en a pas : c'est la règle du pont de La Pointe, fermé aux chars et
    jamais aux jambes. On traverse la gerbe à pied, on se mouille, on passe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        L.B.defs.carte.aqueduc.chance_par_heure = 1;
        const b = poser(L, 9 * 60 + 5);
        if (!b) return { pose: false };
        return {
          pose: true,
          char: !!L.Monde.barriereA(b.x, b.y, 'vehicule'),
          pieton: !!L.Monde.barriereA(b.x, b.y, 'pieton'),
          // Le carnet liste ce qui est fermé, avec sa raison.
          carnet: L.Monde.barrieresFermees().filter(function (q) { return q.slug === 'aqueduc'; })
                   .map(function (q) { return q.raison; }),
          // Pas de cônes : un bris ne se pose pas, il gicle.
          decor: b.decor,
        };
    }""" % POSER)
    assert r["pose"], "aucun bris n'a été tiré"
    assert r["char"], "un char passe dans le trou comme si de rien n'était"
    assert not r["pieton"], "on ne peut plus traverser la rue à pied"
    assert r["carnet"] == ["BRIS D'AQUEDUC"], "le carnet ne le liste pas : %s" % r["carnet"]
    assert r["decor"] is None, "un bris s'est fait poser des cônes"


def test_la_gerbe_coule_tant_que_le_bris_coule(banc):
    """⚠️ **Ce n'est pas un effet de plus** : c'est le `jet_eau` de la
    borne-fontaine défoncée, tel quel — il crache ses gouttes et TIENT son
    souffle. Il meurt au bout de ses dix secondes ; un bris dure une heure de
    jeu, donc on le renouvelle au lieu de le refaire."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const f = L.B.defs.carte.aqueduc;
        f.chance_par_heure = 1;
        const b = poser(L, 10 * 60 + 2);
        if (!b) return { pose: false };
        // On va voir : la gerbe ne naît que dans la bulle du joueur.
        // ⚠️ SUR LE TROTTOIR, et intouchable. Planté au milieu de la chaussée,
        // il se faisait faucher par le trafic, et l'hôpital le renvoyait à
        // deux mille pixels de là : la gerbe sortait de la bulle et le juge
        // mesurait un oubli par distance en croyant mesurer une minuterie.
        const bord = L.Entites.trottoirLePlusProche(b.x, b.y);
        L.B.joueur.x = bord.x; L.B.joueur.y = bord.y;
        L.B.joueur.invincible = 99999;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.majAqueduc();
        const gerbes = function () {
          return L.B.entites.filter(function (q) { return q.type === 'jet_eau' && q.aqueduc; });
        };
        const pendant = gerbes().length;
        // ⚠️ ON FAIT AVANCER LE TEMPS pour de vrai : le `jet_eau` de la borne
        // meurt au bout de ses dix secondes (600 images), et sans image qui
        // passe la minuterie ne descend jamais — le juge aurait mesuré le
        // renouvellement sans jamais le mettre à l'épreuve.
        // ⚠️ ON REGARDE CHAQUE IMAGE, et pas seulement la dernière : le jet de
        // la borne meurt au bout de ses dix secondes, et `majAqueduc` n'en
        // refait un qu'à son prochain battement — une gerbe qui repart une
        // demi-seconde plus tard passerait pour intacte à qui ne la regarde
        // qu'à la fin, alors qu'à l'écran l'eau s'arrête net puis reprend.
        let creux = 0, doubles = 0;
        for (let i = 0; i < L.Entites.JET_EAU_IMAGES + 60; i++) {
          o.frame(1);
          const n = gerbes().length;
          if (n === 0) creux++;
          if (n > 1) doubles++;
        }
        const tenue = gerbes().length;
        const coule = !!L.Monde.brisDAqueduc();
        // La vanne est fermée : l'eau s'arrête.
        poser(L, 10 * 60 + f.minutes + 2);
        L.Entites.majAqueduc();
        const apres = gerbes().length;
        // Et loin de là, on ne crache pas dans le vide.
        poser(L, 11 * 60 + 2);
        const loin = L.Monde.brisDAqueduc();
        L.B.joueur.x = loin.x * L.TT + 8 + 4000;
        L.Entites.majAqueduc();
        return { pose: true, pendant: pendant, tenue: tenue, apres: apres,
                 creux: creux, doubles: doubles, coule: coule, horsBulle: gerbes().length };
    }""" % POSER)
    assert r["pose"], "aucun bris n'a été tiré"
    assert r["pendant"] == 1, "la gerbe n'a pas jailli (%s)" % r["pendant"]
    assert r["coule"], "la vanne s'est fermée pendant la mesure : le juge ne mesure rien"
    assert r["tenue"] == 1, "la gerbe s'est dédoublée ou s'est éteinte (%s)" % r["tenue"]
    assert r["creux"] == 0, "l'eau s'est arrêtée %s images au milieu du bris" % r["creux"]
    assert r["doubles"] == 0, "deux gerbes au même endroit (%s images)" % r["doubles"]
    assert r["apres"] == 0, "l'eau coule encore après la vanne"
    assert r["horsBulle"] == 0, "une gerbe crache à l'autre bout de la ville"


def test_un_bris_ne_tire_pas_un_seul_de_du_jeu(banc):
    """⚠️ **La leçon du char en panne, rejouée une fois de plus.** Ce qui
    s'allume pour la ville ne doit pas décaler le hasard du jeu : chaque dé tiré
    déplace tous ceux qui suivent, et une panne qui prenait un dé au passage a
    fait tomber quatre juges d'un coup.

    Ce qu'on mesure est le TIRAGE — vingt-quatre fois par jour de jeu, la ville
    décide si une conduite lâche et laquelle. Loin du bris, rien ne jaillit, et
    rien ne doit coûter non plus."""
    def compter(chance):
        return banc("""function (L, o) {
            L.Jeu.commencer();
            L.graine(8);
            // ⚠️ On éteint le bris PAR SA FICHE : c'est la seule façon d'être
            // sûr que les deux parties ne diffèrent QUE par lui.
            L.B.defs.carte.aqueduc.chance_par_heure = %s;
            // ⚠️ Loin de TOUTE conduite : sinon la gerbe jaillit sous le
            // joueur, ses gouttes tirent des dés, et le juge ne mesure plus le
            // tirage mais les particules.
            const TT = L.TT, c = L.Monde.carte, liste = L.B.defs.carte.aqueducs;
            const loin = L.Entites.BULLE_OUBLI + 200;
            let place = null;
            for (let ty = 5; ty < c.h - 5 && !place; ty += 5) {
              for (let tx = 5; tx < c.w - 5 && !place; tx += 5) {
                const x = tx * TT + 8, y = ty * TT + 8;
                if (!L.Monde.marchablePieton(tx, ty)) continue;
                if (liste.every(function (a) {
                      return Math.hypot(a.x * TT + 8 - x, a.y * TT + 8 - y) > loin;
                    })) place = { x: x, y: y };
              }
            }
            L.B.joueur.x = place.x; L.B.joueur.y = place.y;
            L.Monde.centrerCamera(place.x, place.y);
            const vrai = L.B.rng;
            let n = 0;
            L.B.rng = function () { n++; return vrai(); };
            o.frame(600);
            L.B.rng = vrai;
            return { des: n, gerbes: L.B.entites.filter(function (q) { return q.aqueduc; }).length };
        }""" % chance)

    avec, sans = compter(1), compter(0)
    assert avec["gerbes"] == sans["gerbes"] == 0, (
        "une gerbe a jailli sous le joueur : le juge ne mesure plus le tirage (%s, %s)"
        % (avec, sans))
    assert avec["des"] == sans["des"], (
        "le tirage du bris a pris %s dés du jeu : tout ce qui suit est décalé"
        % (avec["des"] - sans["des"]))


def test_devant_un_bris_le_trafic_se_deporte_et_passe(banc):
    """⚠️ **C'est le paiement de toute la vague**, et c'est aussi ce qui la rend
    inoffensive : le trou ne fait qu'une tuile, la voie d'à côté va dans le même
    sens, et le char se déporte une tuile avant puis continue. Rien n'a été
    ajouté au trafic pour ça — un bris est une barrière comme les autres, et
    `peutSortir` les consulte déjà.

    Le juge mesure les trois choses qui peuvent mal tourner : il ne se déporte
    pas (il fonce dans l'eau), il ne passe jamais (la rue est coupée), ou il
    reste planté (il s'empile devant, et la rue derrière avec lui)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(62);
        const j = L.B.joueur, TT = L.TT, p = L.B.partie;
        const f = L.B.defs.carte.aqueduc;
        f.chance_par_heure = 1;
        p.jour = 3;
        p.heure = (7 * 60 + 2) / 1440;
        const b = L.Monde.brisDAqueduc();
        if (!b) return { pose: false };
        const pas = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] }[L.Monde.fleche(b.x, b.y)];
        j.x = (b.x + 6) * TT; j.y = (b.y + 6) * TT;
        L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        const amont = { x: (b.x - pas[0] * 5) * TT + 8, y: (b.y - pas[1] * 5) * TT + 8 };
        const v = L.Vehicules.creer('auto', amont.x, amont.y, Math.atan2(pas[1], pas[0]),
                                    { conducteur: 'trafic', etat: 'roule' });
        L.Entites.indexer();
        const voie0 = pas[0] ? Math.floor(v.y / TT) : Math.floor(v.x / TT);
        let plante = 0, pire = 0, passe = false, changeDeVoie = false, dedans = 0;
        for (let i = 0; i < 700; i++) {
            o.frame(1);
            if (L.B.entites.indexOf(v) < 0) break;
            plante = Math.abs(v.vitesse) < 0.05 ? plante + 1 : 0;
            if (plante > pire) pire = plante;
            const voie = pas[0] ? Math.floor(v.y / TT) : Math.floor(v.x / TT);
            if (voie !== voie0) changeDeVoie = true;
            if (Math.floor(v.x / TT) === b.x && Math.floor(v.y / TT) === b.y) dedans++;
            const long = pas[0] ? Math.floor(v.x / TT) : Math.floor(v.y / TT);
            const bout = pas[0] ? b.x + pas[0] * 2 : b.y + pas[1] * 2;
            if ((pas[0] > 0 || pas[1] > 0) ? long > bout : long < bout) passe = true;
        }
        return { pose: true, changeDeVoie: changeDeVoie, passe: passe, pire: pire, dedans: dedans,
                 coule: !!L.Monde.brisDAqueduc(),
                 cycle: 2 * (L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images) };
    }""")
    assert r["pose"], "aucun bris n'a été tiré"
    assert r["coule"], "la vanne s'est fermée pendant la mesure : le juge ne mesure rien"
    assert r["changeDeVoie"] is True, "le char ne se déporte pas devant le bris : %s" % r
    assert r["dedans"] == 0, "le char a roulé dans le trou : %s" % r
    assert r["passe"] is True, "le char ne passe jamais le bris : %s" % r
    assert r["pire"] < r["cycle"], "un char reste planté %s images devant l'eau : %s" % (r["pire"], r)
