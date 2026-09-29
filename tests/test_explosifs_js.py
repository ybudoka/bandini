"""La grenade et la dynamite : on allume, la meche brule dans la main, on lance, ca saute.

`docs/jalons/les-explosifs.md`, vague 1. Le geste : APPUYER allume (la meche brule des cet
instant), RELACHER lance. La tenir, c'est la « cuire » — trop longtemps, elle saute dans la main.
"""

PRELUDE = """
    L.Jeu.commencer();
    const j = L.B.joueur;
    let booms = [];
    const f = L.Explosions.faire;
    L.Explosions.faire = function (x, y, o) { booms.push({ x: x, y: y, t: L.B.t, rayon: o.rayon }); return f.apply(this, arguments); };
    function donner(slug) { L.B.partie.armes[slug] = { mun: 3, usure: 0 }; j.arme = slug; }
    function images(n) { for (let i = 0; i < n; i++) { L.B.t++; L.Entites.indexer(); L.Combat.majLances(); L.Combat.majEnMain(j); } }
"""


def test_la_grenade_saute_au_bout_de_sa_meche_et_pas_avant(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        L.Combat.allumerMeche(j);
        L.Combat.lacherMeche(j, 1);
        images(148); const avant = booms.length;
        images(4);
        return { avant: avant, apres: booms.length, mun: L.B.partie.armes.grenade.mun };
    }""")
    assert r == {"avant": 0, "apres": 1, "mun": 2}


def test_la_tenir_la_cuit(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        L.Combat.allumerMeche(j);
        images(100);                       // tenue 100 images sur 150
        L.Combat.lacherMeche(j, 1);
        images(47); const avant = booms.length;
        images(5);
        return { avant: avant, apres: booms.length };
    }""")
    assert r == {"avant": 0, "apres": 1}


def test_trop_tenue_elle_saute_dans_la_main(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('dynamite');
        const vie = j.vie;
        L.Combat.allumerMeche(j);
        images(245);
        return { booms: booms.length, blesse: j.vie < vie, enMain: !!j.enMain,
                 pres: booms.length > 0 && Math.hypot(booms[0].x - j.x, booms[0].y - j.y) < 16 };
    }""")
    assert r["booms"] == 1 and r["blesse"] and not r["enMain"] and r["pres"], r


def test_changer_d_arme_la_laisse_tomber_et_elle_saute_quand_meme(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        L.Combat.allumerMeche(j);
        j.arme = 'poings';
        images(160);
        return { booms: booms.length, enMain: !!j.enMain };
    }""")
    assert r == {"booms": 1, "enMain": False}


def test_dans_l_eau_la_meche_s_eteint(banc):
    """Lancee sur la baie : un remous, pas d'explosion."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const c = L.Monde.carte;
        let eau = null;
        for (let y = 2; y < c.h - 2 && !eau; y++) for (let x = 2; x < c.w - 2; x++) if (L.Monde.estEau(x, y)) { eau = { x: x * L.TT + 8, y: y * L.TT + 8 }; break; }
        const g = L.Combat.lancer(j, L.Combat.armeDef('grenade'), 150, 0);
        g.x = eau.x; g.y = eau.y; g.z = 0; g.vz = 0;
        images(200);
        return { booms: booms.length, reste: L.B.entites.filter(function (e) { return e.type === 'lance'; }).length };
    }""")
    assert r == {"booms": 0, "reste": 0}


def test_la_grenade_rebondit_sur_le_mur_la_dynamite_non(banc):
    """Lancee droit dans une facade a bout portant : la grenade revient, la dynamite reste au pied du mur."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const c = L.Monde.carte;
        function versLeMur() {                        // un mur plein a l'est, a 3 tuiles, du sol libre entre
          for (let y = 3; y < c.h - 3; y++) for (let x = 3; x < c.w - 6; x++) {
            if (L.Monde.solidite(x, y) || L.Monde.solidite(x + 1, y) || L.Monde.solidite(x + 2, y)) continue;
            if (L.Monde.solidite(x + 3, y) === 1) return { x: x * L.TT + 8, y: y * L.TT + 8, mur: (x + 3) * L.TT };
          }
        }
        const p = versLeMur(); j.x = p.x; j.y = p.y; j.angle = 0;
        const g = L.Combat.lancer(j, L.Combat.armeDef('grenade'), 999, 1);
        const d = L.Combat.lancer(j, L.Combat.armeDef('dynamite'), 999, 1);
        images(90);
        return { gx: g.x, dx: d.x, mur: p.mur };
    }""")
    assert r["gx"] < r["mur"] and r["dx"] < r["mur"], "rien ne traverse le mur"
    assert r["mur"] - r["dx"] < 8, f"la dynamite tombe au pied du mur : {r}"
    assert r["mur"] - r["gx"] > 16, f"la grenade devait revenir d'au moins une tuile : {r}"


def test_la_triche_munitions_ne_vide_pas_le_sac(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        L.B.partie.triches = Object.assign(L.B.partie.triches || {}, { munitions: true });
        L.Combat.allumerMeche(j);
        return { mun: L.B.partie.armes.grenade.mun, allumee: !!j.enMain };
    }""")
    assert r == {"mun": 3, "allumee": True}


def test_passer_une_porte_laisse_la_meche_dehors(banc):
    """Un changement de scene (porte, arrestation, hopital) lache la meche la ou l'on etait."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade');
        const c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.Combat.allumerMeche(j);
        o.frame(60);                                   // la meche brule 60 images dans la main
        o.entrer(porte);
        const dedans = !!L.B.interieur, enMain = !!j.enMain;
        const ici = L.B.entites.filter(function (e) { return e.type === 'lance'; }).length;
        o.frame(600);
        o.sortir();
        const vie = j.vie;
        o.frame(300);
        // ⚠️ La relecture du 29 sept. 2026 : rangee avec la ville, la grenade restait FIGEE
        // dehors, et sautait au retour — a 6 px du joueur, qui finissait a 1 PV.
        return { dedans: dedans, enMain: enMain, ici: ici, booms: booms.length, vie: j.vie === vie,
                 dehors: L.B.entites.filter(function (e) { return e.type === 'lance'; }).length };
    }""")
    assert r == {"dedans": True, "enMain": False, "ici": 0, "booms": 0, "vie": True, "dehors": 0}, r


def test_au_bouton_on_allume_puis_on_lance(banc):
    """Le vrai geste : appuyer allume, relacher lance — pas de coup de poing, pas de balle."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade'); L.B.partie.arme = 'grenade';
        o.frame(2);
        o.touche('KeyJ'); o.frame(3);
        const allumee = !!j.enMain;
        o.frame(20);
        o.relacher('KeyJ'); o.frame(1);
        return { allumee: allumee, enMain: !!j.enMain,
                 lancees: L.B.entites.filter(function (e) { return e.type === 'lance'; }).length,
                 balles: L.B.entites.filter(function (e) { return e.type === 'projectile'; }).length };
    }""")
    assert r == {"allumee": True, "enMain": False, "lancees": 1, "balles": 0}, r


def test_monter_dans_un_char_la_laisse_tomber(banc):
    """Par la vraie boucle : au volant, `majGestes` sort tout de suite — la meche doit tomber avant."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        donner('grenade'); L.B.partie.arme = 'grenade';
        o.frame(2);
        L.Combat.allumerMeche(j);
        const v = o.char('auto', 0, 20);
        j.dansVehicule = v;
        o.frame(2);
        return { enMain: !!j.enMain, lancees: L.B.entites.filter(function (e) { return e.type === 'lance'; }).length };
    }""")
    assert r == {"enMain": False, "lancees": 1}, r


def test_on_voit_la_grenade_voler_et_son_ombre(banc):
    """En l'air, deux peintures : son ombre au sol, et l'objet leve de `z` — plus haut que l'ombre."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const g = L.Combat.lancer(j, L.Combat.armeDef('grenade'), 150, 1);
        images(6);
        const ctx = o.ctx, poses = [];
        ctx.drawImage = function (img, x, y) { poses.push(y); };
        ctx.translate = function (x, y) { poses.push(y); };
        L.Combat.dessinerLance(ctx, g, L.B.cam.x, L.B.cam.y);
        return { z: g.z, poses: poses };
    }""")
    assert r["z"] > 4, r
    assert len(r["poses"]) >= 2, "l'ombre et l'objet : deux peintures"
    assert min(r["poses"]) < max(r["poses"]) - 4, f"l'objet doit etre peint au-dessus de son ombre : {r}"


def test_le_jeu_peint_ce_qui_vole(banc):
    """`Entites.dessiner` passe la main a `Combat.dessinerLance` — sinon elle vole invisible, comme la bouteille."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const g = L.Combat.lancer(j, L.Combat.armeDef('dynamite'), 150, 1);
        let peinte = 0; const d = L.Combat.dessinerLance;
        L.Combat.dessinerLance = function (ctx, e) { if (e === g) peinte++; return d.apply(this, arguments); };
        L.Jeu.rendre();
        return peinte;
    }""")
    assert r == 1


def test_les_sons_des_explosifs_arrivent_avec_le_premier_explosif(banc):
    """Ramasser ou allumer un explosif demande ses sons (`Son.Lieu.charger('explosifs')`), une fois."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const demandes = [];
        L.Son.Lieu.charger = function (lieu) { demandes.push(lieu); };
        L.Combat.ramasserArme('pistolet', 12);
        const apresPistolet = demandes.length;
        L.Combat.ramasserArme('grenade', 3);
        j.arme = 'grenade';
        L.Combat.allumerMeche(j);
        return { apresPistolet: apresPistolet, demandes: demandes };
    }""")
    assert r["apresPistolet"] == 0
    assert r["demandes"] and set(r["demandes"]) == {"explosifs"}, r


def test_un_chantier_ouvert_a_sa_dynamite_et_elle_ne_revient_pas(banc):
    """Au pied de la benne d'un chantier qui travaille : trois batons. Ramasses, ils ne reviennent pas."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const ch = L.Chantiers.liste.find(function (c) {
          const ph = c.posee >= 0 ? c.def.phases[c.posee] : null;
          return c.def.conteneur && ph && ph.machines.length;
        });
        if (!ch) return { saute: 'aucun chantier ouvert' };
        L.Chantiers.poserLaDynamite(ch, true);
        const b = L.B.entites.find(function (e) { return e.type === 'ramassage' && e.arme === 'dynamite'; });
        j.x = b.x; j.y = b.y;
        L.Combat.ramasser(j, b);
        const sac = L.B.partie.armes.dynamite;
        L.Chantiers.poserLaDynamite(ch, true);
        return { posee: !!b, sac: sac ? sac.mun : null,
                 revient: L.B.entites.some(function (e) { return e.type === 'ramassage' && e.arme === 'dynamite'; }) };
    }""")
    assert r == {"posee": True, "sac": 3, "revient": False}, r


def test_la_dynamite_du_chantier_attend_et_revient_si_on_l_a_oubliee(banc):
    """Elle ne s'efface pas au bout d'une minute comme une arme lachee ; et oubliee hors
    de la bulle (pas ramassee), le chantier la repose."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const ch = L.Chantiers.liste.find(function (c) {
          const ph = c.posee >= 0 ? c.def.phases[c.posee] : null;
          return c.def.conteneur && ph && ph.machines.length;
        });
        L.Chantiers.poserLaDynamite(ch, true);
        const b = ch.dynamite;
        j.x = b.x + 30; j.y = b.y;
        b.t = 5000;
        o.frame(2);
        const reste = L.B.entites.indexOf(b) >= 0;
        L.Entites.retirer(b);                          // oubliee (hors bulle), pas ramassee
        L.Chantiers.poserLaDynamite(ch, true);
        return { reste: reste, revient: !!ch.dynamite && ch.dynamite !== b && L.B.entites.indexOf(ch.dynamite) >= 0 };
    }""")
    assert r == {"reste": True, "revient": True}, r


def _rue_libre():
    """Une rangee de route libre sur 20 tuiles vers l'est : le joueur y est pose, cap a l'est."""
    return """
        const c = L.Monde.carte;
        let ok = null;
        for (let y = 130; y < c.h - 3 && !ok; y++) for (let x = 5; x < c.w - 24; x++) {
          let libre = true; for (let k = 0; k < 20; k++) if (L.Monde.solidite(x + k, y) || !c.route[y * c.w + x + k]) libre = false;
          if (libre) { ok = { x: x * L.TT + 8, y: y * L.TT + 8 }; break; }
        }
        j.x = ok.x; j.y = ok.y; j.angle = 0;
        L.B.entites.filter(function (e) { return e.type === 'vehicule' || e.type === 'pieton'; }).forEach(function (e) { L.Entites.retirer(e); });
        L.Entites.indexer();
    """


def test_on_la_lance_a_la_portee_de_sa_fiche(banc):
    """Un lancer plein s'arrete autour de la `portee` du catalogue — pas au bout de la rue."""
    r = banc("""function (L, o) {""" + PRELUDE + _rue_libre() + """
        const res = {};
        ['grenade', 'dynamite'].forEach(function (slug) {
          const def = L.Combat.armeDef(slug);
          const g = L.Combat.lancer(j, def, 999, 1);
          images(200);
          res[slug] = { d: Math.round(g.x - j.x), portee: def.portee, vx: Math.abs(g.vx) };
          L.Entites.retirer(g);
        });
        return res;
    }""")
    for slug, m in r.items():
        assert 0.6 * m["portee"] <= m["d"] <= 1.15 * m["portee"], f"{slug} : {m}"
        assert m["vx"] < 0.05, f"{slug} roule encore : {m}"


def test_la_grenade_rebondit_sur_le_flanc_d_un_char(banc):
    """Un char gare a 125 px, la ou elle arrive au ras du sol : elle se cogne a la tole et retombe
    devant — elle ne le traverse pas."""
    r = banc("""function (L, o) {""" + PRELUDE + _rue_libre() + """
        const v = o.char('auto', 125, 0);
        const g = L.Combat.lancer(j, L.Combat.armeDef('grenade'), 999, 1);
        images(120);
        return { gx: g.x, arriere: v.x - v.def.longueur / 2 };
    }""")
    assert r["gx"] < r["arriere"], r


def test_la_grenade_se_pose_sur_le_toit_d_un_char(banc):
    """A 90 px, elle redescend au-dessus du char : elle tombe SUR le toit (14 px), pas a travers.
    (Plus pres, a 50 px, elle est au sommet de sa cloche et passe par-dessus — c'est voulu.)"""
    r = banc("""function (L, o) {""" + PRELUDE + _rue_libre() + """
        const v = o.char('auto', 90, 0);
        const g = L.Combat.lancer(j, L.Combat.armeDef('grenade'), 999, 1);
        let surLeToit = 0, dansLaTole = 0;
        for (let i = 0; i < 120; i++) {
          images(1);
          const dedans = Math.abs(g.x - v.x) < v.def.longueur / 2 && Math.abs(g.y - v.y) < v.def.largeur / 2;
          if (dedans && g.z >= 13.9) surLeToit++;
          if (dedans && g.z < 13.9) dansLaTole++;
        }
        return { surLeToit: surLeToit, dansLaTole: dansLaTole };
    }""")
    assert r["surLeToit"] > 0 and r["dansLaTole"] == 0, r


def test_une_grenade_au_pied_d_un_char_le_detruit(banc):
    """Tombee a 14 px de son centre (l'essai du 29 sept. 2026 : le char restait a 23/100, sans feu) :
    il saute, ou il brule assez pour sauter tout seul."""
    r = banc("""function (L, o) {""" + PRELUDE + _rue_libre() + """
        const res = {};
        ['grenade', 'dynamite'].forEach(function (slug, k) {
          const v = o.char('auto', 80, k * 60);
          const g = L.Combat.lancer(j, L.Combat.armeDef(slug), 1, 0);
          g.x = v.x - 14; g.y = v.y; g.z = 0; g.vz = 0;
          images(3);
          res[slug] = { etat: v.etat, part: v.vie / v.vieMax };
        });
        return res;
    }""")
    for slug, m in r.items():
        assert m["etat"] == "epave" or m["part"] < 0.2, f"{slug} : {m}"


def test_la_chaine_de_chars_ne_passe_pas_la_porte(banc):
    """Un char en attente d'exploser (la chaine) quand on passe une porte saute DEHORS, avant le
    noir — pas dans la piece, sur la carte de la piece."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        const a = o.char('auto', 160, 0), b = o.char('auto', 194, 0);
        a.vie = 1; b.vie = 1;
        const ou = [];
        const f2 = L.Explosions.faire;
        L.Explosions.faire = function () { ou.push(L.B.interieur ? 'dedans' : 'dehors'); return f2.apply(this, arguments); };
        L.Vehicules.endommager(a, 999, null);
        const enFile = b.etat !== 'epave';
        L.Jeu.entrer(porte);
        o.fondu();
        o.frame(5);
        return { enFile: enFile, dedans: !!L.B.interieur, ou: ou };
    }""")
    assert r["enFile"] and r["dedans"], r
    assert r["ou"] == ["dehors", "dehors"], f"le deuxieme char a saute dans la piece : {r}"


def test_en_coop_le_deuxieme_joueur_lache_aussi_sa_meche(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.Jeu.basculerCoop();
        const j2 = L.B.coop.entite;
        j2.arme = 'grenade'; L.B.partie.armes.grenade = { mun: 3, usure: 0 };
        L.Combat.allumerMeche(j2);
        const c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        const allumee = !!j2.enMain;
        L.Jeu.entrer(porte);
        return { allumee: allumee, enMain: !!j2.enMain };
    }""")
    assert r == {"allumee": True, "enMain": False}, r
