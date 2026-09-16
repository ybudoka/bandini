"""Ça travaille : les chantiers en jeu.

⚠️ Python a jugé la géométrie de chaque phase (`test_chantiers.py`). Ici on juge
ce que le JEU en fait : poser la bonne phase le bon jour, jamais sous les yeux,
jamais sur quelqu'un, et défaire proprement ce qui appartenait à la maison.

⚠️ `Chantiers.maj` ne regarde qu'une image sur `CADENCE` (30) : un juge qui veut
voir une phase se poser laisse tourner au moins deux cadences.
"""

from app import chantiers

#: Loin de tout chantier : le joueur y est posé quand on veut qu'une phase ait le
#: droit de se poser. Choisi à l'exécution (voir `LOIN`).
LOIN = """
  function loin(L) {
    const liste = L.Chantiers.liste;
    const w = L.Monde.carte.w, h = L.Monde.carte.h;
    for (let y = 4; y < h - 4; y += 3) {
      for (let x = 4; x < w - 4; x += 3) {
        if (L.Monde.solidite(x, y) !== 0 || !L.Monde.carte.legende[L.Monde.carte.sol[y][x]].trottoir) continue;
        const assez = liste.every(function (ch) {
          const d = ch.def;
          return Math.abs(x - (d.x + d.l / 2)) > 60 || Math.abs(y - (d.y + d.h / 2)) > 40;
        });
        if (assez) return { x: x * 16 + 8, y: y * 16 + 8 };
      }
    }
    throw new Error('aucun trottoir loin des chantiers');
  }
  // ⚠️ L'horloge des chantiers SEULE, sans faire tourner la ville : en cent
  // images, le reste du jeu range ce qui traîne loin du joueur (un char garé,
  // une arme par terre) et le juge ne mesurerait plus rien.
  function tourner(L, cadences) {
    for (let k = 0; k < cadences * L.Chantiers.CADENCE + 1; k++) L.Chantiers.maj();
  }
  function poserLeJoueur(L, p) {
    const j = L.B.joueur; j.x = p.x; j.y = p.y; j.vx = 0; j.vy = 0; j.intouchable = true;
    L.Entites.indexer(); L.Monde.centrerCamera(j.x, j.y);
  }
"""


def _juge(corps: str) -> str:
    return "function (L, o) {" + LOIN + corps + "}"


def test_le_premier_matin_porte_ses_chantiers(banc):
    r = banc(_juge("""
        L.Jeu.commencer();
        const carte = L.Monde.carte;
        return L.Chantiers.liste.map(function (ch) {
            const d = ch.def;
            const rangees = [];
            let incoherent = 0;
            for (let j = 0; j < d.h; j++) {
                rangees.push(carte.sol[d.y + j].slice(d.x, d.x + d.l));
                for (let i = 0; i < d.l; i++) {
                    const g = carte.sol[d.y + j][d.x + i];
                    if (carte.solide[(d.y + j) * carte.w + d.x + i] !== ((carte.legende[g] || {}).solide || 0)) incoherent++;
                }
            }
            return { id: d.id, posee: ch.posee, decalage: d.decalage, rangees: rangees,
                     attendues: d.phases[ch.posee].sol, incoherent: incoherent,
                     machines: ch.machines.map(function (e) { return e.decor; }) };
        });
    """))
    assert len(r) >= 2
    for ch in r:
        assert ch["posee"] == ch["decalage"], ch
        assert ch["rangees"] == ch["attendues"], f"chantier {ch['id']} : le sol n'est pas celui du jour"
        assert ch["incoherent"] == 0, "la solidité ne suit pas le sol posé"
        assert tuple(ch["machines"]) == chantiers.MACHINES.get(ch["posee"], ()), ch


def test_le_jeu_et_le_generateur_lisent_la_meme_horloge(banc, paquet):
    """⚠️ Deux formules pour une horloge : un juge les compare jour par jour, sinon
    le jour où l'une change, deux appareils voient deux villes."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const sortie = [];
        for (const debut of [1, 5]) {
            L.B.partie.chantiers = { debut: debut };
            for (let jour = 1; jour <= 30; jour++) {
                L.B.partie.jour = jour;
                sortie.push(L.Chantiers.liste.map(function (ch) { return L.Chantiers.phaseVoulue(ch.def); }));
            }
        }
        return sortie;
    }""")
    attendu = []
    for debut in (1, 5):
        for jour in range(1, 31):
            attendu.append([chantiers.phase_du_jour(ch, jour, debut) for ch in paquet["carte"]["chantiers"]])
    assert r == attendu


def test_une_phase_ne_se_pose_jamais_sous_les_yeux(banc):
    """⚠️ Le piège 4 du plan : recuire en plein jeu se voit. Devant le chantier, la
    phase du lendemain ATTEND ; dès qu'on tourne le coin, elle se pose."""
    r = banc(_juge("""
        L.Jeu.commencer();
        const ch = L.Chantiers.liste.find(function (c) { return c.posee < 4; });
        const d = ch.def;
        const avant = ch.posee;
        poserLeJoueur(L, { x: (d.x + d.l / 2) * 16, y: (d.y + d.h + 2) * 16 });
        L.B.partie.jour += d.pas;
        o.frame(100);
        const devant = ch.posee;
        poserLeJoueur(L, loin(L));
        o.frame(100);
        return { avant: avant, devant: devant, apres: ch.posee, voulue: L.Chantiers.phaseVoulue(d) };
    """))
    assert r["voulue"] == r["avant"] + 1
    assert r["devant"] == r["avant"], "la phase s'est posée sous les yeux du joueur"
    assert r["apres"] == r["voulue"], "hors de vue, la phase du jour doit se poser"


def test_le_neuf_attend_que_personne_ne_soit_dans_l_empreinte(banc):
    """Un char garé sur le terrain rasé, et le lendemain le neuf remonte ses murs :
    il faut attendre qu'il soit parti, sinon il est muré dedans."""
    r = banc(_juge("""
        L.Jeu.commencer();
        const ch = L.Chantiers.liste.find(function (c) { return c.posee >= 1 && c.posee <= 3; });
        const d = ch.def;
        // Une tuile de sol dans l'empreinte, loin des machines.
        let place = null;
        for (let j = 0; j < d.h && !place; j++) {
            for (let i = 0; i < d.l && !place; i++) {
                const x = d.x + i, y = d.y + j;
                if (d.masque[j][i] !== 'X' || L.Monde.solidite(x, y) !== 0) continue;
                if (ch.machines.some(function (e) { return Math.abs(e.x - (x * 16 + 8)) < 20 && Math.abs(e.y - (y * 16 + 8)) < 20; })) continue;
                place = { x: x * 16 + 8, y: y * 16 + 8 };
            }
        }
        const v = L.Vehicules.creer('auto', place.x, place.y, 0, { etat: 'stationne' });
        poserLeJoueur(L, loin(L));
        L.B.partie.jour += 30;                       // le neuf, pour sûr
        tourner(L, 3);
        const garee = ch.posee;
        L.Entites.retirer(v);
        tourner(L, 3);
        return { garee: garee, partie: ch.posee, derniere: d.phases.length - 1 };
    """))
    assert r["garee"] < r["derniere"], "le neuf a muré un char garé sur le chantier"
    assert r["partie"] == r["derniere"]


def test_le_neuf_remonte_ses_murs_et_la_demolition_les_ouvre(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const ch = L.Chantiers.liste[0], d = ch.def;
        const solides = function () {
            let n = 0;
            for (let j = 0; j < d.h; j++) for (let i = 0; i < d.l; i++) {
                if (d.masque[j][i] === 'X' && L.Monde.solidite(d.x + i, d.y + j) === 1) n++;
            }
            return n;
        };
        let taille = 0;
        d.masque.forEach(function (r) { for (const c of r) if (c === 'X') taille++; });
        const vus = {};
        for (const phase of [0, 2, 3, 4]) { L.Chantiers.appliquer(0, phase); vus[phase] = solides(); }
        return { taille: taille, vus: vus };
    }""")
    assert r["vus"]["0"] == r["taille"]
    assert r["vus"]["2"] == 0 and r["vus"]["3"] == 0, "un terrain rasé garde des murs"
    assert r["vus"]["4"] == r["taille"], "le neuf n'a pas repris toute son empreinte"


def test_les_machines_travaillent_et_arretent_puis_s_en_vont(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const ch = L.Chantiers.liste[0];
        const parPhase = {};
        for (let phase = 0; phase < ch.def.phases.length; phase++) {
            L.Chantiers.appliquer(0, phase);
            const machines = L.B.entites.filter(function (e) { return e.machineDe === ch.def.id; });
            parPhase[phase] = machines.map(function (e) {
                return { decor: e.decor, solide: e.solide,
                         indexee: L.Entites.decorAutour(e.x, e.y, 4).indexOf(e) >= 0 };
            });
        }
        return parPhase;
    }""")
    for phase, machines in r.items():
        attendues = chantiers.MACHINES.get(int(phase), ())
        assert tuple(m["decor"] for m in machines) == attendues, (phase, machines)
        for m in machines:
            assert m["solide"], f"{m['decor']} ne bloque personne"
            assert m["indexee"], f"{m['decor']} n'est pas dans l'index du décor : le char la traverse"


def test_une_maison_rasee_n_avale_plus_personne(banc):
    """Les gens rentrent chez eux par les portes condamnées. Sur un terrain rasé,
    il n'y a plus de chez-eux — et personne n'y marche plus pour rentrer.

    ⚠️ On ne juge PAS la liste des portes : elle ne bouge pas, exprès (son ordre
    compte pour tout ce qui y tire au sort). On juge ce que les gens en FONT."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ Un chantier qui A une porte : sur une maison sans porte, le juge
        // verifierait l'absence de rien et passerait sans la regle.
        const i = L.Chantiers.liste.findIndex(function (c) {
            return c.def.phases[0].sol.some(function (r, j) {
                for (let k = 0; k < r.length; k++) if ((r[k] === 'd' || r[k] === 'D') && c.def.masque[j][k] === 'X') return true;
                return false;
            });
        });
        if (i < 0) throw new Error('aucun chantier ne porte de porte : le juge ne prouverait rien');
        const ch = L.Chantiers.liste[i], d = ch.def;
        const porte = L.Monde.carte.portesFermees.find(function (q) {
            return q.x >= d.x && q.x < d.x + d.l && q.y >= d.y && q.y < d.y + d.h && d.masque[q.y - d.y][q.x - d.x] === 'X';
        });
        const vus = {};
        for (const phase of [0, 2]) {
            L.Chantiers.appliquer(i, phase);
            const passant = L.Entites.creerPieton(porte.x * 16 + 8, (porte.y + 2) * 16 + 8, L.Entites.archetype('passant'));
            passant.etat = 'flane';
            const envoye = L.Entites.envoyerAUnePorte(passant);
            vus[phase] = { sert: L.Entites.porteQuiSert(porte),
                           versElle: envoye && passant.porteBut === porte };
            L.Entites.retirer(passant);
        }
        return vus;
    }""")
    assert r["0"]["sert"] and r["0"]["versElle"], "la maison debout n'avale plus son voisin qui rentre"
    assert not r["2"]["sert"], "une maison rasée sert encore de porte"
    assert not r["2"]["versElle"], "un passant marche rentrer chez lui dans un terrain rasé"


def test_ce_qui_appartenait_a_la_maison_tombe_avec_elle(banc):
    """Une façade de logement, un équipement de toit, un tag, une fenêtre allumée :
    tout ça était à la MAISON. Sur un terrain rasé, ça flotterait au-dessus de rien."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const carte = L.Monde.carte, def = carte.def;
        const ch = L.Chantiers.liste[0], d = ch.def;
        const siennes = function (x, y) {
            return x >= d.x && x < d.x + d.l && y >= d.y && y < d.y + d.h && d.masque[y - d.y][x - d.x] === 'X';
        };
        // ⚠️ Aucune maison en chantier de cette ville n'a de fenetre allumee : on en
        // allume une, sinon le juge verifierait qu'aucune lampe absente ne brille.
        let place = null;
        d.masque.forEach(function (r, j) { for (let k = 0; k < r.length && !place; k++) if (r[k] === 'X') place = [d.x + k, d.y + j]; });
        carte.lampes.push({ x: place[0] * 16 + 8, y: place[1] * 16 + 8, r: 20, c: 'rgba(255,212,150,0.22)' });
        const lampesSiennes = carte.lampes.filter(function (l) { return siennes(Math.floor(l.x / 16), Math.floor(l.y / 16)); });
        const etat = function () {
            let effacees = 0, total = 0;
            d.masque.forEach(function (r, j) {
                for (let i = 0; i < r.length; i++) if (r[i] === 'X') { total++; if (L.Chantiers.efface(d.x + i, d.y + j)) effacees++; }
            });
            return { effacees: effacees, total: total,
                     lampesAllumees: lampesSiennes.filter(function (l) { return !l.demolie; }).length,
                     toitsVisibles: (def.toits || []).filter(function (t) { return siennes(t.x, t.y) && !L.Chantiers.efface(t.x, t.y); }).length };
        };
        L.Chantiers.appliquer(0, 0); const debout = etat();
        L.Chantiers.appliquer(0, 2); const rase = etat();
        // Et ailleurs dans la ville, rien n'est effacé.
        const ailleurs = L.Chantiers.efface(d.x - 3, d.y - 3);
        return { debout: debout, rase: rase, lampes: lampesSiennes.length, ailleurs: ailleurs };
    }""")
    assert r["lampes"] >= 1
    assert r["debout"]["lampesAllumees"] == r["lampes"], "la maison debout s'est éteinte"
    assert r["debout"]["effacees"] == 0, "la maison debout a perdu sa façade"
    assert r["rase"]["effacees"] == r["rase"]["total"]
    assert r["rase"]["lampesAllumees"] == 0, "une fenêtre s'allume au-dessus d'un terrain rasé"
    assert r["rase"]["toitsVisibles"] == 0
    assert r["ailleurs"] is False


def test_le_cache_ne_se_vide_qu_autour_du_chantier(banc):
    """Poser une phase recuit les morceaux du chantier et de ses bords — pas la ville."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const carte = L.Monde.carte, ch = L.Chantiers.liste[0], d = ch.def;
        carte.morceaux.clear();
        const mw = Math.ceil(carte.w / 16), mh = Math.ceil(carte.h / 16);
        for (let my = 0; my < mh; my++) for (let mx = 0; mx < mw; mx++) carte.morceaux.set(mx + ',' + my, {});
        const avant = carte.morceaux.size;
        L.Chantiers.appliquer(0, (ch.posee + 1) % d.phases.length);
        const touches = [];
        for (let my = 0; my < mh; my++) for (let mx = 0; mx < mw; mx++) {
            if (!carte.morceaux.has(mx + ',' + my)) touches.push([mx, my]);
        }
        return { avant: avant, touches: touches, d: { x: d.x, y: d.y, l: d.l, h: d.h } };
    }""")
    assert r["touches"], "rien n'a été recuit : le chantier ne se verrait pas"
    d = r["d"]
    for mx, my in r["touches"]:
        assert (d["x"] - 1) // 16 <= mx <= (d["x"] + d["l"]) // 16, (mx, my)
        assert (d["y"] - 1) // 16 <= my <= (d["y"] + d["h"] + 1) // 16, (mx, my)
    assert len(r["touches"]) <= 9


def test_une_vieille_partie_repart_de_son_jour(banc):
    """⚠️ Le piège 5 : la phase voyage dans la sauvegarde. Une partie d'avant les
    chantiers, rouverte au trentième jour, ne découvre pas trois bâtiments neufs
    qu'elle n'a jamais vus tomber : elle repart de son premier matin."""
    r = banc("""function (L, o) {
        const neuve = L.Sauvegarde.completer(null, L.B.defs);
        const vieille = L.Sauvegarde.completer({ jour: 30, argent: 10 }, L.B.defs);
        const gardee = L.Sauvegarde.completer({ jour: 30, chantiers: { debut: 12 } }, L.B.defs);
        L.B.partie = vieille;
        L.Jeu.commencer();
        return { neuve: neuve.chantiers, vieille: vieille.chantiers, gardee: gardee.chantiers,
                 phases: L.Chantiers.liste.map(function (ch) { return [ch.posee, ch.def.decalage]; }) };
    }""")
    assert r["neuve"] == {"debut": 1}
    assert r["vieille"] == {"debut": 30}
    assert r["gardee"] == {"debut": 12}, "une sauvegarde qui connaît ses chantiers les garde"
    for posee, decalage in r["phases"]:
        assert posee == decalage


def test_une_sauvegarde_dans_un_mur_neuf_ressort_devant_la_porte(banc):
    r = banc("""function (L, o) {
        const ch0 = L.B.defs.carte.chantiers[0];
        let place = null;
        ch0.masque.forEach(function (r, j) { for (let i = 0; i < r.length && !place; i++) if (r[i] === 'X') place = [ch0.x + i, ch0.y + j]; });
        L.B.partie.x = place[0] * 16 + 8; L.B.partie.y = place[1] * 16 + 8;
        L.B.partie.jour = 60;                        // le neuf est debout
        L.Jeu.commencer();
        const j = L.B.joueur;
        const tx = Math.floor(j.x / 16), ty = Math.floor(j.y / 16);
        return { solidite: L.Monde.solidite(tx, ty), posee: L.Chantiers.liste[0].posee };
    }""")
    assert r["posee"] == chantiers.DERNIERE
    assert r["solidite"] == 0, "le joueur reparaît dans un mur neuf"


def test_rien_ne_bouge_quand_on_est_dans_une_piece(banc):
    """Dans un intérieur, la carte active est la pièce : poser une phase y
    écrirait des murs dans le dépanneur."""
    r = banc(_juge("""
        L.Jeu.commencer();
        poserLeJoueur(L, loin(L));
        const ch = L.Chantiers.liste.find(function (c) { return c.posee < 4; });
        L.B.partie.jour += ch.def.pas * 2;
        L.B.interieur = { slug: 'essai' };
        tourner(L, 3);
        const dedans = ch.posee;
        L.B.interieur = null;
        tourner(L, 3);
        return { dedans: dedans, dehors: ch.posee, voulue: L.Chantiers.phaseVoulue(ch.def) };
    """))
    assert r["dedans"] < r["voulue"], "une phase s'est posée pendant qu'on était dans une pièce"
    assert r["dehors"] == r["voulue"]


def test_un_objet_par_terre_ne_finit_pas_mure(banc):
    r = banc(_juge("""
        L.Jeu.commencer();
        const ch = L.Chantiers.liste.find(function (c) { return c.posee >= 1 && c.posee <= 3; });
        const d = ch.def;
        let place = null;
        for (let j = 0; j < d.h && !place; j++) for (let i = 0; i < d.l && !place; i++) {
            if (d.masque[j][i] === 'X' && L.Monde.solidite(d.x + i, d.y + j) === 0) place = { x: (d.x + i) * 16 + 8, y: (d.y + j) * 16 + 8 };
        }
        const arme = L.Entites.creer('ramassage', place.x, place.y, { r: 4, objet: 'arme', arme: 'pistolet', munitions: 6, t: 0, solide: false });
        poserLeJoueur(L, loin(L));
        L.B.partie.jour += 60;
        tourner(L, 3);
        return { posee: ch.posee, solidite: L.Monde.solidite(Math.floor(arme.x / 16), Math.floor(arme.y / 16)),
                 encore: L.B.entites.indexOf(arme) >= 0 };
    """))
    assert r["posee"] == chantiers.DERNIERE
    assert r["encore"]
    assert r["solidite"] == 0, "l'arme lâchée sur le chantier est murée dans le neuf"


def test_la_boule_se_balance_et_la_grue_tourne(banc):
    """Une articulation par machine, et elle BOUGE : chaque pose peint autre chose."""
    r = banc("""function (L, o) {
        const empreinte = function (nom, pose) {
            const f = L.DECORS[nom], traces = [];
            const faux = { fillRect: function (x, y, w, h) { traces.push([Math.round(x), Math.round(y), w, h]); } };
            Object.defineProperty(faux, 'fillStyle', { set: function () {}, get: function () { return ''; } });
            f.peindre(faux, f.w, f.h, pose);
            return JSON.stringify(traces);
        };
        const sortie = {};
        for (const nom of ['grue_a_boule', 'grue', 'pelleteuse']) {
            const f = L.DECORS[nom];
            const poses = new Set();
            for (let p = 0; p < f.variantes; p++) poses.add(empreinte(nom, p));
            sortie[nom] = { variantes: f.variantes, distinctes: poses.size, anime: f.anime, arrete: f.arrete, solide: f.solide };
        }
        return sortie;
    }""")
    for nom, f in r.items():
        assert f["anime"] and f["variantes"] >= 4, nom
        assert f["distinctes"] >= f["variantes"] // 2, f"{nom} ne bouge pas : {f}"
        assert f["solide"] and f["arrete"], f"{nom} : un char la traverse"
