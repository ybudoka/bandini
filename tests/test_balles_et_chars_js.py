"""Des bagarres de gangs vivantes, vague 5a — les balles et les chars (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md).

Martin (1er oct. 2026) : les balles s'arrêtent sur les chars, et les abîment — les siennes aussi. Avant, une balle
traversait la tôle (seule celle qui aurait touché le conducteur mordait la carrosserie) : se cacher derrière un char ne
protégeait de rien.
"""

#: Un tireur à l'ouest, une cible plantée et increvable à l'est, et — si `angle` n'est pas null — un char garé
#: entre les deux.
LIGNE = """
    function ligne(L, angle, armeSlug) {
      const j = L.B.joueur;
      const y = j.y + 40, x0 = j.x - 80;
      const t = L.Entites.creerPieton(x0, y, L.Entites.archetype('cravate'));
      const m = L.Entites.creerPieton(x0 + 120, y, L.Entites.archetype('morue'));
      t.etat = 'fige'; t.arme = armeSlug; t.armeDeGang = null;
      m.etat = 'fige'; m.vie = m.vieMax = 1e6;
      let v = null;
      if (angle !== null) v = L.Vehicules.creer('auto', x0 + 60, y, angle, { etat: 'stationne', couleur: '#777777' });
      L.Entites.indexer();
      return { t: t, m: m, v: v };
    }
    // Cinq balles : la dispersion d'un tireur de gang (doublee) ecarte d'environ le rayon d'une cible a cette
    // distance — une seule balle peut manquer, et le temoin ne mesurerait rien.
    function tirerEtAttendre(L, o, d, armeSlug) {
      for (let k = 0; k < 5; k++) {
        d.t.etat = 'fige';
        L.Combat.tirer(d.t, L.Combat.armeDef(armeSlug), d.m);
        for (let i = 0; i < 40; i++) { d.t.etat = 'fige'; d.m.etat = 'fige'; o.frame(1); }
      }
    }
"""


def test_la_balle_s_arrete_sur_le_char_et_l_abime(banc):
    """Le char garé entre le tireur et sa cible prend la balle : la cible n'a rien, la tôle si. ⚠️ Le témoin, sans
    char, prouve que la balle atteint la cible."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(70);
        %s
        const a = ligne(L, null, 'pistolet');
        tirerEtAttendre(L, o, a, 'pistolet');
        const temoin = 1e6 - a.m.vie;
        for (const e of [a.t, a.m]) L.Entites.retirer(e);
        const b = ligne(L, 0, 'pistolet');
        tirerEtAttendre(L, o, b, 'pistolet');
        return { temoin: temoin, cible: 1e6 - b.m.vie, tole: b.v.vieMax - b.v.vie };
    }""" % LIGNE)
    assert r["temoin"] > 0, "sans char, la balle n'atteint pas sa cible : le juge ne mesure rien (%s)" % r
    assert r["cible"] == 0, "la balle a traversé le char (%s)" % r
    assert r["tole"] > 0, "la balle n'a pas abîmé le char (%s)" % r


def test_une_balle_rapide_ne_saute_pas_un_char_de_travers(banc):
    """La carabine avance de plus de pixels par image qu'un char n'est large de travers (14 px) : on teste le
    SEGMENT de son pas, pas seulement le point où elle tombe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(71);
        %s
        const d = ligne(L, Math.PI / 2, 'carabine');
        tirerEtAttendre(L, o, d, 'carabine');
        return { cible: 1e6 - d.m.vie, tole: d.v.vieMax - d.v.vie, vproj: L.Combat.armeDef('carabine').vitesse_projectile };
    }""" % LIGNE)
    assert r["cible"] == 0 and r["tole"] > 0, r


def test_ta_balle_aussi_abime_un_char_vide(banc):
    """⚠️ Avant : « tirer sur le capot d'un char vide ne fait toujours rien ». Martin : les tiennes aussi."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(72);
        const j = L.B.joueur;
        for (let i = 0; i < 90; i++) o.frame(1);
        // A bout portant : plus loin, la balle peut tomber avant sur un passant ou un lampadaire du terminus.
        const v = L.Vehicules.creer('auto', j.x + 30, j.y, 0, { etat: 'stationne', couleur: '#777777' });
        L.Entites.indexer();
        L.Combat.ramasserArme('pistolet', 12);
        j.arme = 'pistolet';
        L.Entites.regarder(j, v.x - j.x, v.y - j.y);
        L.Combat.tirer(j, L.Combat.armeDef('pistolet'));
        for (let i = 0; i < 40; i++) o.frame(1);
        return { tole: v.vieMax - v.vie };
    }""")
    assert r["tole"] > 0, r


def test_le_char_du_tireur_ne_l_arrete_pas(banc):
    """`Vehicules.coupeLaLigne` épargne le char qu'on lui dit d'épargner : celui du tireur."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const v = L.Vehicules.creer('auto', j.x + 60, j.y, 0, { etat: 'stationne', couleur: '#777777' });
        L.Entites.indexer();
        const coupe = L.Vehicules.coupeLaLigne(j.x, j.y, j.x + 120, j.y, null);
        const epargne = L.Vehicules.coupeLaLigne(j.x, j.y, j.x + 120, j.y, v);
        const aCote = L.Vehicules.coupeLaLigne(j.x, j.y + 30, j.x + 120, j.y + 30, null);
        return { coupe: coupe === v, epargne: epargne, aCote: aCote };
    }""")
    assert r == {"coupe": True, "epargne": None, "aCote": None}, r


def test_un_gang_s_abrite_derriere_un_char(banc):
    """Une rue dégagée, sans mur pour se cacher : pas d'abri. Un char garé entre lui et sa cible : un abri, caché
    par le char."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, c = L.Monde.carte;
        const t = L.Entites.creerPieton(j.x, j.y, L.Entites.archetype('cravate'));
        t.arme = 'pistolet'; t.armeDeGang = 'pistolet';
        const m = L.Entites.creerPieton(j.x, j.y, L.Entites.archetype('morue'));
        // Une rue degagee : pas d'abri sans char.
        let lieu = null;
        for (let ty = 5; ty < c.h - 5 && !lieu; ty += 2) for (let tx = 5; tx < c.w - 5 && !lieu; tx += 2) {
          if (!L.Monde.estChaussee(tx, ty) || !L.Monde.estChaussee(tx + 7, ty)) continue;
          t.x = tx * TT + 8; t.y = ty * TT + 8; m.x = t.x + 7 * TT; m.y = t.y;
          if (!L.Monde.ligneLibre(t.x, t.y, m.x, m.y)) continue;
          if (!L.Rixe.abriPour(t, m)) lieu = { x: t.x, y: t.y };
        }
        if (!lieu) return { lieu: null };
        const v = L.Vehicules.creer('auto', t.x + 24, t.y, Math.PI / 2, { etat: 'stationne', couleur: '#777777' });
        L.Entites.indexer();
        const a = L.Rixe.abriPour(t, m);
        return { lieu: lieu, abri: a, parLeChar: a ? L.Vehicules.coupeLaLigne(a.x, a.y, m.x, m.y, null) === v : false };
    }""")
    assert r["lieu"], "aucune rue dégagée sans abri : le juge ne mesure rien"
    assert r["abri"] and r["parLeChar"], "il ne s'abrite pas derrière le char (%s)" % r


def test_les_balles_perdues_abiment_sans_faire_sauter_et_les_tiennes_si(banc):
    """Martin (1er oct. 2026) : « abîmer sans exploser ». Les balles qui ne sont pas les tiennes (un gang, un agent)
    abîment la tôle mais ne descendent pas un char sous 1 PV : pas d'épaves en chaîne autour d'une rixe. Les tiennes,
    elles, le font toujours sauter."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(73);
        %s
        const d = ligne(L, 0, 'pistolet');
        for (let k = 0; k < 6; k++) tirerEtAttendre(L, o, d, 'pistolet');      // trente balles de gang
        const gang = { vie: d.v.vie, etat: d.v.etat };
        const j = L.B.joueur;
        for (let i = 0; i < 90; i++) o.frame(1);
        L.Combat.ramasserArme('pistolet', 48);
        j.arme = 'pistolet';
        j.x = d.v.x - 30; j.y = d.v.y; L.Monde.centrerCamera(j.x, j.y);
        for (let k = 0; k < 8 && d.v.etat !== 'epave'; k++) {
          L.Entites.regarder(j, d.v.x - j.x, d.v.y - j.y);
          L.Combat.tirer(j, L.Combat.armeDef('pistolet'));
          for (let i = 0; i < 25; i++) o.frame(1);
        }
        return { gang: gang, toi: d.v.etat };
    }""" % LIGNE)
    assert r["gang"]["vie"] >= 1 and r["gang"]["etat"] != "epave", "les balles d'un gang ont fait sauter le char (%s)" % r
    assert r["toi"] == "epave", "tes balles ne le font plus sauter (%s)" % r


def test_le_char_ou_tu_es_saute_sous_les_balles_des_autres(banc):
    """« Abîmer sans exploser » épargne les chars autour d'une rixe — pas celui où TU es : les balles qui te visent,
    d'un gang ou d'un agent, le font sauter comme avant (la police te sortait de ton char à coups de pistolet)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(74);
        %s
        const d = ligne(L, 0, 'pistolet'), j = L.B.joueur;
        for (let i = 0; i < 90; i++) o.frame(1);
        j.x = d.v.x; j.y = d.v.y + 20;
        L.Vehicules.monter(j, d.v);
        for (let k = 0; k < 10 && d.v.etat !== 'epave'; k++) tirerEtAttendre(L, o, d, 'pistolet');
        return { dans: j.dansVehicule === d.v || d.v.etat === 'epave', etat: d.v.etat, vie: d.v.vie };
    }""" % LIGNE)
    assert r["dans"], "le joueur n'est pas monté : le juge ne mesure rien (%s)" % r
    assert r["etat"] == "epave", "le char où tu es ne saute plus sous les balles (%s)" % r
