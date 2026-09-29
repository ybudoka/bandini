"""Le vieux maître revient de Floride (c05 à c08, l'arc d'Irène et des Mantes), JOUÉ au banc — docs/jalons/l-ecole-rivale.md.

Martin, 29 sept. 2026 : « les deux » — Irène appelle en Floride, et Victor Tam, le vieux maître de l'ÉCOLE LA MANTE,
reprend ses élèves un par un. Chaque mission se joue au bouton, de la poignée de main à la prime : c05 (Irène, puis le
maître dans sa salle, puis trois frimeurs), c06 (la filature de Kenny jusqu'à chez Gus, et le duel), c07 (Monsieur
Bois, le camion de Gilles, et la technique en échange), c08 (l'escorte du maître au Dragon d'or, et les derniers
frimeurs). Et ce qui change au quartier quand l'école rouvre se juge contre le même monde avant : la salle, la rue,
le calme.
"""

from outils_missions import OUTILS as OUTILS_MISSIONS, PLUS_LONGUES

from app import mantes, missions, techniques

OUTILS = OUTILS_MISSIONS + PLUS_LONGUES + """
  const AVANT = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'c01', 'c02', 'c03', 'c04'];
  function dansLaPorte(L, o, lieu) {
    const B = L.B, j = B.joueur, M = L.Monde;
    aPied(L);
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    return B.interieur ? B.interieur.slug : null;
  }
  function dehors(L, o) {
    L.Jeu.sortir(); o.fondu();
    for (let k = 0; k < 200 && L.B.interieur; k++) o.frame(1);
    return !L.B.interieur;
  }
  // Jouer jusqu'à ce que la mission, sa scène et ses répliques soient finies (plafonné).
  function auBout(L, o) {
    const B = L.B;
    for (let k = 0; k < 6000 && (B.partie.mission || B.scene || B.cinema || B.finEnAttente); k++) { o.frame(1); ecouter(L); }
  }
  function commencerChez(L, o, lieu, slug) {
    const B = L.B;
    dansLaPorte(L, o, lieu); jouer(L, o);
    serrer(L, o, slug);
    for (let k = 0; k < 6000 && (B.scene || B.cinema); k++) { o.frame(1); ecouter(L); }
    jouer(L, o);
    return { mission: B.partie.mission && B.partie.mission.slug, etape: etape(L), ligne: L.Histoire.ligneObjectif() };
  }
  // Les hommes de l'étape en cours : où ils sont nés, ce qu'ils tiennent, leur vie.
  function hommes(L) {
    const B = L.B, e0 = etape(L);
    return B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && e.etape === e0 && e.vivant; });
  }
  function coucherTous(L, o) {
    const eux = hommes(L);
    eux.forEach(function (e) { L.Entites.assommer(e); });
    jouer(L, o, 6);
    return eux.length;
  }
  function dansLaZone(L, e, slug) {
    const z = (L.Monde.carte.def.zones || []).filter(function (q) { return q.slug === slug; }).pop();
    const tx = e.x / 16, ty = e.y / 16;
    return !!z && tx >= z.x && tx < z.x + z.l && ty >= z.y && ty < z.y + z.h;
  }
"""


def test_le_maitre_n_est_dans_sa_salle_qu_une_fois_revenu_de_floride(banc):
    """`arrive_apres` : avant la chute du Pouce (c04), sa salle n'a que ses élèves — des Mantes, du gang ; une fois
    revenu, il se tient devant le sac, face à la salle, parmi eux. Sans mission pour lui, il dit son repos."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B;
        faites(L, AVANT.slice(0, -1));
        function visite() {
            const ici = dansLaPorte(L, o, 'ecole_mante'); jouer(L, o);
            const m = L.Histoire.donneur('maitre');
            const pt = B.interieur.points.find(function (p) { return p.type === 'maitre'; });
            const eleves = B.entites.filter(function (e) { return e.type === 'pieton' && e.arch === 'mante'; });
            const r = { ici: ici, maitre: !!m, place: m && pt ? Math.round(Math.hypot(m.x - (pt.x * 16 + 8), m.y - (pt.y * 16 + 8))) : null,
                        face: m ? m.face : null, eleves: eleves.length,
                        gang: eleves.filter(function (e) { return e.gang === 'mantes'; }).length };
            if (m) {
                // Sans mission pour lui : son repos, dans la boîte (`Hud.dialogue`), avec son visage.
                const j = B.joueur;
                j.x = m.x - 16; j.y = m.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
                o.frame(1); j.angle = 0; j.face = 'droite'; L.Missions.majInvite(j); o.tape('KeyE', 2);
                const d = B.dialogue;
                r.repos = d ? { qui: d.qui, texte: d.lignes[0], visage: d.visage && d.visage.slug } : null;
            }
            dehors(L, o);
            return r;
        }
        const avant = visite();
        B.partie.missionsFaites.c04 = 1;
        const apres = visite();
        return { avant: avant, apres: apres };
    }""")
    assert r["avant"]["ici"] == mantes.SLUG and r["avant"]["maitre"] is False, f"en Floride jusqu'à c04 : {r['avant']}"
    assert r["avant"]["eleves"] == 3 and r["avant"]["gang"] == 3, r["avant"]
    a = r["apres"]
    assert a["maitre"] is True and a["place"] <= 16 and a["face"] == "bas", f"revenu, il se tient devant le sac : {a}"
    assert a["eleves"] == 3 and a["gang"] == 3, "avant les portes ouvertes, ses élèves sont encore du gang"
    assert a["repos"] == {"qui": "Victor Tam", "texte": missions.personnage("maitre")["repos"][1], "visage": "maitre"}, \
        f"sans mission pour lui, il dit son repos : {a}"


def test_c05_irene_le_maitre_et_les_trois_frimeurs(banc):
    """c05, _Le droit de table_ : Irène au bout du bar ; à l'école, le maître serre la main (il se nomme) ; les trois
    frimeurs attendent sur LEUR territoire, aux poings et à 70 de vie ; couchés, la mission se ferme chez Irène
    (500 $)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, AVANT);
        const argent = paiements(L);
        const debut = commencerChez(L, o, 'nord_casino', 'irene');
        dehors(L, o); jouer(L, o);
        dansLaPorte(L, o, 'ecole_mante'); jouer(L, o);
        const accueil = serrer(L, o, 'maitre');
        const apres = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        dehors(L, o); jouer(L, o, 30);
        const eux = hommes(L).map(function (e) {
            return { gang: e.gang, arme: e.arme || null, vie: e.vieMax, chez: dansLaZone(L, e, 'mantes') };
        });
        const n = coucherTous(L, o);
        auBout(L, o);
        return { debut: debut, accueil: accueil, apres: apres, eux: eux, n: n, dites: dites,
                 fait: !!B.partie.missionsFaites.c05, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["debut"]["mission"] == "c05" and r["debut"]["ligne"].startswith("VA VOIR LEUR VIEUX MAÎTRE"), r["debut"]
    assert r["accueil"] == "accueil", "au bouton, le maître serre la main (sa poignée de main dite)"
    assert r["apres"]["etape"] == 1 and r["apres"]["ligne"].startswith("RAMÈNE LES TROIS FRIMEURS"), r["apres"]
    assert len(r["eux"]) == 3 and r["n"] == 3, r["eux"]
    for e in r["eux"]:
        assert e == {"gang": "mantes", "arme": None, "vie": 70, "chez": True}, f"trois frimeurs aux poings, chez eux : {e}"
    for dite in ("pendant:irene:0", "accueil:maitre:0", "pendant:maitre:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and 500 in r["argent"], r


def test_c06_la_filature_de_kenny_et_le_duel_devant_chez_gus(banc):
    """c06, _Le chemin de chez Gus_ : le char de Kenny (une sport) naît à bonne distance de l'école et attend qu'on
    soit au volant ; on le file jusqu'à l'armurerie ; là, Kenny — le chef des Mantes, aux poings, 160 de vie —
    attend à la porte de Gus ; couché, la mission se ferme (700 $)."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, AVANT.concat(['c05']));
        const argent = paiements(L);
        const debut = commencerChez(L, o, 'ecole_mante', 'maitre');
        dehors(L, o); jouer(L, o);
        const c = B.mission.suivi;
        const kenny = c ? { slug: c.slug, d: Math.round(Math.hypot(c.x - j.x, c.y - j.y)) } : null;
        const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
        const arret = L.Histoire.tuileDeRue(j.x, j.y, 10);
        const mien = L.Vehicules.creer('auto', arret.x, arret.y, CAP[arret.sens], { etat: 'stationne' });
        j.x = mien.x + 10; j.y = mien.y; L.Entites.indexer();
        L.Vehicules.monter(j, mien); L.Entites.indexer();
        let i = 0;
        for (; i < 20000 && B.partie.mission && B.partie.mission.etape === 0; i++) {
            if (!c.attendLeJoueur) {
                mien.x = c.x - Math.cos(c.angle) * 96; mien.y = c.y - Math.sin(c.angle) * 96;
                mien.vitesse = 0; mien.vx = 0; mien.vy = 0; j.x = mien.x; j.y = mien.y;
            }
            o.frame(1); ecouter(L);
        }
        const g = L.Histoire.lieu('armurerie');
        const file = { images: i, etape: etape(L), ligne: L.Histoire.ligneObjectif(),
                       dGus: Math.round(Math.hypot(g.x - c.x, g.y - c.y)) };
        aPied(L); o.frame(1); ecouter(L);
        const duel = hommes(L).map(function (e) {
            return { gang: e.gang, chef: !!e.chef, arme: e.arme || null, vie: e.vieMax,
                     dGus: Math.round(Math.hypot(g.x - e.x, g.y - e.y) / 16) };
        });
        coucherTous(L, o);
        auBout(L, o);
        return { debut: debut, kenny: kenny, file: file, duel: duel, dites: dites,
                 fait: !!B.partie.missionsFaites.c06, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["debut"]["mission"] == "c06" and r["debut"]["ligne"].startswith("SUIS LE CHAR DE KENNY"), r["debut"]
    assert r["kenny"]["slug"] == "sport" and r["kenny"]["d"] >= 5 * 16, f"son char de frime, à bonne distance : {r['kenny']}"
    f = r["file"]
    assert f["etape"] == 1 and f["ligne"].startswith("UN DUEL À MAINS NUES"), f
    assert f["dGus"] < 8 * 16 and f["images"] > 20 * 60, f"une vraie filature, jusqu'à chez Gus : {f}"
    assert len(r["duel"]) == 1, r["duel"]
    d = r["duel"][0]
    assert d["gang"] == "mantes" and d["chef"] and d["arme"] is None and d["vie"] == 160, d
    assert d["dGus"] <= 6, f"Kenny attend à la porte de chez Gus : {d}"
    for dite in ("pendant:maitre:0", "pendant:maitre:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and 700 in r["argent"], r


def test_c07_monsieur_bois_revient_et_le_maitre_t_apprend_la_main_de_la_mante(banc):
    """c07, _Monsieur Bois_ : le camion de Gilles attend à la fourrière (prêté : il ne se vend pas) ; livré à la porte
    de l'école sans une bosse, la mission paie sa prime de sans-dégâts, et le maître t'APPREND le retournement du
    poignet (`donne.technique`) — tu ne le savais pas avant. Le rejouer quand on le sait déjà n'apprend rien de
    plus et ne plante pas."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, AVANT.concat(['c05', 'c06']));
        const argent = paiements(L);
        const avant = !!B.partie.techniques.retournement_poignet;
        const debut = commencerChez(L, o, 'ecole_mante', 'maitre');
        dehors(L, o); jouer(L, o);
        const v = B.mission.vehicule;
        const f = L.Histoire.lieu('fourriere');
        const camion = v ? { slug: v.slug, prete: v.aQui || null, dFourriere: Math.round(Math.hypot(v.x - f.x, v.y - f.y) / 16) } : null;
        j.x = v.x + 10; j.y = v.y; L.Entites.indexer();
        L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o, 10);
        const monte = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        // À l'école, sans une bosse : le camion posé devant la porte, à l'arrêt.
        const e = L.Histoire.lieuDeLivraison('ecole_mante');
        const t = L.Histoire.tuileDeRue(e.x, e.y, 6);
        v.x = t.x; v.y = t.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; L.Entites.indexer();
        jouer(L, o, 20);
        const livre = { etape: etape(L), dans: !!j.dansVehicule };
        auBout(L, o);
        const sait = !!B.partie.techniques.retournement_poignet;
        const fait = !!B.partie.missionsFaites.c07, payes = argent.map(function (a) { return a.montant; });
        // La refaire en la sachant déjà (le menu de saut des missions) : rien de plus à apprendre, rien qui plante.
        delete B.partie.missionsFaites.c07;
        L.Histoire.commencer('c07'); B.cinema = null; B.scene = null;
        L.Histoire.reussir();
        return { avant: avant, debut: debut, camion: camion, monte: monte, livre: livre, dites: dites, sait: sait,
                 encore: !!B.partie.techniques.retournement_poignet, refaite: !!B.partie.missionsFaites.c07,
                 fait: fait, argent: payes };
    }""")
    assert r["avant"] is False, "le banc part d'une partie qui ne sait pas la technique"
    assert r["debut"]["mission"] == "c07" and r["debut"]["ligne"].startswith("MONSIEUR BOIS EST DANS LE CAMION"), r["debut"]
    assert r["camion"] == {"slug": "camion", "prete": "gilles", "dFourriere": r["camion"]["dFourriere"]}, r["camion"]
    assert r["camion"]["dFourriere"] <= 8, r["camion"]
    assert r["monte"]["etape"] == 1 and r["monte"]["ligne"].startswith("RAMÈNE MONSIEUR BOIS"), r["monte"]
    for dite in ("pendant:maitre:0", "pendant:maitre:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["livre"] == {"etape": None, "dans": False}, f"livré à la porte de l'école, on en descend : {r['livre']}"
    assert r["fait"] is True and r["argent"] == [900], f"la prime, et la moitié de plus sans une bosse : {r['argent']}"
    assert r["sait"] is True, "le maître t'apprend la main de la mante"
    assert r["encore"] is True and r["refaite"] is True, "refaite en la sachant, rien ne plante"


def test_c08_l_escorte_du_maitre_et_l_ecole_qui_rouvre(banc):
    """c08, _Les portes ouvertes_ : dehors, le maître se pose à la porte de son école (il ne se tient pas en ville) et
    nous suit ; au Dragon d'or, les quatre derniers frimeurs arrivent en courant (nés
    hors de l'écran), aux poings ; couchés, la mission se ferme (1 200 $), et le maître NE SE SAUVE PAS : il reste
    planté devant le Dragon d'or, où sa fin se dit devant nous. Le gang est calme, et le Clairon aura sa une."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        faites(L, AVANT.concat(['c05', 'c06', 'c07']));
        const argent = paiements(L);
        const debut = commencerChez(L, o, 'ecole_mante', 'maitre');
        dehors(L, o); jouer(L, o);
        const m = B.mission.protege;
        const porte = (L.Monde.carte.def.portes || []).find(function (q) { return q.lieu === 'ecole_mante'; });
        const pose = m ? { perso: m.personnage, dPorte: Math.round(Math.hypot(m.x - (porte.x * 16 + 8), m.y - (porte.y * 16 + 8)) / 16),
                           suit: !!m.suit } : null;
        // On le rejoint, il nous suit ; puis on marche jusqu'au Dragon d'or, à petits pas, lui derrière.
        j.x = m.x + 20; j.y = m.y; L.Entites.indexer(); jouer(L, o, 10);
        const suit = !!m.suit;
        const c = L.Histoire.lieu('nord_casino');
        let i = 0;
        for (; i < 4000 && etape(L) === 0; i++) {
            const dx = c.x - j.x, dy = c.y - j.y, d = Math.hypot(dx, dy);
            if (d > 40 && Math.hypot(m.x - j.x, m.y - j.y) < 48) { j.x += dx / d * 1.5; j.y += dy / d * 1.5; }
            if (i % 200 === 199 && Math.hypot(m.x - j.x, m.y - j.y) > 48) { m.x = j.x - 20; m.y = j.y; }
            L.Entites.indexer(); o.frame(1); ecouter(L);
        }
        const arrive = { etape: etape(L), ligne: L.Histoire.ligneObjectif(), images: i,
                         dLui: Math.round(Math.hypot(m.x - c.x, m.y - c.y) / 16) };
        jouer(L, o, 30);
        const eux = hommes(L).map(function (e) {
            return { gang: e.gang, arme: e.arme || null, vie: e.vieMax, dLui: Math.round(Math.hypot(e.x - m.x, e.y - m.y) / 16) };
        });
        coucherTous(L, o);
        auBout(L, o);
        jouer(L, o, 120);
        return { debut: debut, pose: pose, suit: suit, arrive: arrive, eux: eux, dites: dites,
                 apres: { vivant: m.vivant, etat: m.etat, dCasino: Math.round(Math.hypot(m.x - c.x, m.y - c.y) / 16),
                          toujours: B.entites.indexOf(m) >= 0 },
                 calmes: B.partie.calmes.slice(), une: B.partie.manchetteForcee || null,
                 fait: !!B.partie.missionsFaites.c08, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["debut"]["mission"] == "c08" and r["debut"]["ligne"].startswith("ESCORTE LE MAÎTRE"), r["debut"]
    assert r["pose"]["perso"] == "maitre" and r["pose"]["dPorte"] <= 4, f"dehors, il sort de son école avec nous : {r['pose']}"
    assert r["suit"] is True, "on sort avec lui : il nous suit"
    a = r["arrive"]
    assert a["etape"] == 1 and a["ligne"].startswith("LES DERNIERS FRIMEURS"), a
    assert a["dLui"] <= 8, f"il est arrivé avec nous : {a}"
    assert len(r["eux"]) == 4, r["eux"]
    for e in r["eux"]:
        assert e["gang"] == "mantes" and e["arme"] is None and e["vie"] == 80, e
    for dite in ("pendant:maitre:0", "pendant:maitre:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and 1200 in r["argent"], r
    ap = r["apres"]
    assert ap["toujours"] and ap["vivant"] and ap["etat"] == "fige" and ap["dCasino"] <= 8, \
        f"la mission finie, il ne se sauve pas avec les figurants : {ap}"
    assert "mantes" in r["calmes"] and r["une"] == "ecole_rouverte", r


def test_l_ecole_rouverte_contre_le_meme_monde_avant(banc):
    """LE MONDE D'APRÈS, jugé contre le même monde avant (la même graine, la même place) : dans la salle, les élèves
    ne sont plus du gang, tiennent leur place et font face au maître, qui compte (sa bulle) ; dans la rue, sur leur
    territoire, beaucoup moins de Mantes naissent ; les Cravates, elles, n'ont pas changé."""
    r = banc("function (L, o) {" + OUTILS + """
        const B = L.B;
        function monde(fini) {
            L.Jeu.commencer(); L.graine(11);
            faites(L, AVANT.concat(['c05', 'c06', 'c07']));
            if (fini) { B.partie.missionsFaites.c08 = 1; B.partie.calmes.push('mantes'); }
            dansLaPorte(L, o, 'ecole_mante'); jouer(L, o, 3);
            const m = L.Histoire.donneur('maitre');
            const eleves = B.entites.filter(function (e) { return e.type === 'pieton' && e.arch === 'mante'; });
            const salle = { eleves: eleves.length, gang: eleves.filter(function (e) { return !!e.gang; }).length,
                            figes: eleves.filter(function (e) { return e.etat === 'fige'; }).length,
                            face: eleves.filter(function (e) {
                                const a = Math.atan2(m.y - e.y, m.x - e.x), d = Math.abs(Math.atan2(Math.sin(a - e.angle), Math.cos(a - e.angle)));
                                return d < 0.8;
                            }).length,
                            bulles: [] };
            // Il compte, deux secondes sur quatre : on regarde sa bulle pendant quatre secondes.
            for (let k = 0; k < 240; k++) {
                o.frame(1);
                const t = m && m.bulle ? m.bulle.texte : null;
                if (salle.bulles.indexOf(t) < 0) salle.bulles.push(t);
            }
            salle.bulles.sort();
            dehors(L, o);
            // La rue : planté au milieu de leur territoire, on compte qui naît.
            const z = (L.Monde.carte.def.zones || []).filter(function (q) { return q.slug === 'mantes'; }).pop();
            const j = B.joueur, vus = new Set();
            let mantes = 0, tous = 0;
            j.x = (z.x + z.l / 2) * 16; j.y = (z.y + z.h / 2) * 16; L.Entites.indexer();
            for (let k = 0; k < 60 * 240; k++) {
                if (k % 600 === 0) {
                    // On vide la foule pour la voir renaître : c'est la naissance qu'on juge, pas la foule d'avant.
                    B.entites.filter(function (e) { return e.type === 'pieton' && !e.personnage && !e.metier; })
                      .forEach(function (e) { L.Entites.retirer(e); });
                }
                o.frame(1);
                B.entites.forEach(function (e) {
                    if (e.type !== 'pieton' || vus.has(e.id) || e.metier) return;
                    vus.add(e.id); tous++; if (e.gang === 'mantes') mantes++;
                });
            }
            return { salle: salle, rue: { mantes: mantes, tous: tous },
                     parts: { mantes: L.Entites.partDehors('mantes'), cravates: L.Entites.partDehors('cravates') } };
        }
        return { avant: monde(false), apres: monde(true) };
    }""")
    av, ap = r["avant"], r["apres"]
    assert av["salle"]["eleves"] == 3 and av["salle"]["gang"] == 3, av["salle"]
    assert av["salle"]["bulles"] == [missions.personnage("maitre")["heler"]], \
        f"avant les portes ouvertes, pas de cours — il a c08 pour toi : {av['salle']}"
    assert ap["salle"] == {"eleves": 3, "gang": 0, "figes": 3, "face": 3, "bulles": [mantes.REPRISE["bulle"], None]}, ap["salle"]
    assert av["parts"] == {"mantes": 0.5, "cravates": 0.5} and ap["parts"] == {"mantes": mantes.REPRISE["part_dehors"], "cravates": 0.5}
    pa = av["rue"]["mantes"] / max(1, av["rue"]["tous"])
    pb = ap["rue"]["mantes"] / max(1, ap["rue"]["tous"])
    assert av["rue"]["tous"] >= 40 and ap["rue"]["tous"] >= 40, r
    # Mesuré (graine 11, quatre minutes) : 149 Mantes sur 280 naissances avant, 33 sur 124 après.
    assert pa >= 0.3 and pb <= pa * 0.6 and ap["rue"]["mantes"] * 2 <= av["rue"]["mantes"], \
        f"moins de Mantes dans la rue quand l'école rouvre : {av['rue']} → {ap['rue']}"


def test_ce_qu_un_donneur_apprend_existe_et_se_paie_au_dojo():
    """`donne.technique` nomme une technique du répertoire qu'on PAIE au DOJO DION (jamais un coup de rue gratuit) :
    c'est un cadeau, pas un doublon des poings."""
    from app import missions
    donnees = [(m["slug"], m["donne"]["technique"]) for m in missions.CATALOGUE if m["donne"].get("technique")]
    assert donnees == [("c07", "retournement_poignet")], donnees
    for slug, t in donnees:
        tech = next((x for x in techniques.CATALOGUE if x["slug"] == t), None)
        assert tech and not tech["gratuite"] and tech["prix"] > 0, f"{slug} : {t} n'est pas une technique payante"
