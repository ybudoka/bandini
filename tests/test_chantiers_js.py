"""Ça travaille : les chantiers en jeu.

⚠️ Python a jugé la géométrie de chaque phase (`test_chantiers.py`). Ici on juge
ce que le JEU en fait : poser la bonne phase le bon jour, jamais sous les yeux,
jamais sur quelqu'un, et défaire proprement ce qui appartenait à la maison.

⚠️ `Chantiers.maj` ne regarde qu'une image sur `CADENCE` (30) : un juge qui veut
voir une phase se poser laisse tourner au moins deux cadences.
"""

from app import chantiers, vehicules

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
        assert tuple(m.removesuffix("_ouest") for m in ch["machines"]) == chantiers.MACHINES.get(ch["posee"], ()), ch


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
        # La grue à boule tournée vers l'ouest est la même machine, en miroir.
        assert tuple(m["decor"].removesuffix("_ouest") for m in machines) == attendues, (phase, machines)
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


# --- 2e vague : le chantier travaille ----------------------------------------------------


def test_la_boule_touche_le_mur_au_pixel_pres(banc):
    """⚠️ La boule frappe POUR VRAI : à la pose du coup, son dernier pixel touche le
    premier pixel du mur — et à aucune autre pose elle n'y entre. Des deux côtés :
    la grue tournée vers l'ouest est un miroir, ancre comprise."""
    r = banc(_juge("""
        L.Jeu.commencer();
        const traces = [];
        const faux = { fillRect: function (x, y, w, h) { traces.push([x, y, w, h]); } };
        Object.defineProperty(faux, 'fillStyle', { set: function () {}, get: function () { return ''; } });
        return L.Chantiers.liste.map(function (ch, i) {
            L.Chantiers.appliquer(i, 1);
            const e = ch.machines.find(function (m) { return m.frappe; });
            const f = L.DECORS[e.decor];
            const bords = [];
            for (let p = 0; p < f.variantes; p++) {
                traces.length = 0;
                f.peindre(faux, f.w, f.h, p);
                // Les deux rectangles de la boule : les derniers peints avant son reflet.
                const boule = traces.slice(-3, -1);
                const g = Math.min.apply(null, boule.map(function (q) { return q[0]; }));
                const dr = Math.max.apply(null, boule.map(function (q) { return q[0] + q[2] - 1; }));
                bords.push([e.x - f.ancre[0] + g, e.x - f.ancre[0] + dr]);
            }
            const mx = e.frappe[0], my = e.frappe[1];
            return { id: ch.def.id, decor: e.decor, sens: e.sens, ex: e.x, frappe: f.frappe, bords: bords,
                     mur: [mx * 16, (mx + 1) * 16 - 1],
                     solide: [L.Monde.solidite(mx, my), L.Monde.solidite(mx, my - 1)],
                     contact: L.Chantiers.CONTACT_X };
        });
    """))
    assert {c["sens"] for c in r} == {1, -1}, "il faut juger les deux côtés : " + str(r)
    for c in r:
        assert c["solide"] == [1, 1], f"chantier {c['id']} : la boule frappe un mur qui n'est pas là"
        gauche, droite = c["mur"]
        for pose, (g, d) in enumerate(c["bords"]):
            if c["sens"] > 0:
                assert d < gauche, (c["id"], pose, "la boule entre dans le mur")
                if pose == c["frappe"]:
                    assert d == gauche - 1, (c["id"], "au coup, la boule ne touche pas le mur")
                    assert c["ex"] + c["contact"] == gauche, "la poussière ne part pas du mur"
            else:
                assert g > droite, (c["id"], pose, "la boule entre dans le mur")
                if pose == c["frappe"]:
                    assert g == droite + 1, (c["id"], "au coup, la boule ne touche pas le mur")
                    assert c["ex"] - c["contact"] == droite + 1, "la poussière ne part pas du mur"


def test_le_coup_part_a_la_pose_qu_on_voit_et_le_chantier_se_tait_la_nuit(banc):
    """Le son, la poussière et la secousse partent à la PREMIÈRE image de la pose
    du coup. La nuit : plus un son, et les machines à leur pose de repos."""
    r = banc(_juge("""
        L.Jeu.commencer();
        L.Chantiers.appliquer(0, 1);
        const ch = L.Chantiers.liste[0];
        const e = ch.machines.find(function (m) { return m.frappe; });
        const f = L.DECORS[e.decor];
        poserLeJoueur(L, { x: e.x, y: e.y + 48 });
        const rumeurs = [];
        L.Son.SFX.rumeur_chantier = function (v) { rumeurs.push(v); };
        const tourne = function (n) {
            let secousse = 0;
            for (let k = 0; k < n; k++) {
                L.B.cam.secousse = 0;
                L.Chantiers.maj();
                secousse = Math.max(secousse, L.B.cam.secousse);
                L.B.t++;
            }
            return secousse;
        };
        L.B.partie.heure = 0.5;
        const t0 = L.B.t, particules = L.B.particules.length;
        const secousse = tourne(1300);
        const jour = L.Chantiers.journal.filter(function (x) { return x.t >= t0; });
        const coups = jour.filter(function (x) { return x.son === 'boule'; }).map(function (x) {
            return [L.Entites.poseDuDecor(f, x.t, false), L.Entites.poseDuDecor(f, x.t + 1, false)];
        });
        const rumeurJour = rumeurs.slice();
        L.B.partie.heure = 0.95;
        rumeurs.length = 0;
        const t1 = L.B.t;
        tourne(1300);
        const poses = new Set();
        for (let t = 0; t < f.anime * f.variantes; t++) poses.add(L.Entites.poseDuDecor(f, t));
        return { coups: coups, sons: jour.map(function (x) { return x.son; }), frappe: f.frappe,
                 particules: L.B.particules.length - particules, secousse: secousse,
                 rumeurJour: Math.min.apply(null, rumeurJour), nuit: L.Monde.estNuit(),
                 sonsDeNuit: L.Chantiers.journal.filter(function (x) { return x.t >= t1; }).length,
                 rumeurNuit: Math.max.apply(null, rumeurs), posesDeNuit: Array.from(poses) };
    """))
    assert len(r["coups"]) >= 7, r["sons"]
    for avant, pendant in r["coups"]:
        assert pendant == r["frappe"], "le coup part sur une autre pose que celle du coup"
        assert avant == r["frappe"] - 1, "le coup part en retard sur la pose qu'on voit"
    assert "marteau_piqueur" in r["sons"], "ce qu'on ne voit pas ne s'entend jamais"
    assert r["particules"] > 0, "pas de poussière au coup"
    assert r["secousse"] > 0, "à deux pas du coup, la rue ne tremble pas"
    assert r["rumeurJour"] > 0.5, "à deux pas du chantier, pas de rumeur"
    assert r["nuit"]
    assert r["sonsDeNuit"] == 0, "le chantier travaille la nuit"
    assert r["rumeurNuit"] == 0
    assert r["posesDeNuit"] == [0], "la nuit, les machines bougent encore"


def test_on_entend_le_chantier_avant_de_le_voir(banc):
    """La rumeur suit la distance : forte devant, plus faible au bout de la rue,
    rien au loin — et rien dans une pièce."""
    r = banc(_juge("""
        L.Jeu.commencer();
        L.B.partie.heure = 0.5;
        const ch = L.Chantiers.liste.find(function (c) { return c.posee >= 1 && c.posee <= 3; });
        const d = ch.def;
        const vus = [];
        L.Son.SFX.rumeur_chantier = function (v) { vus.push(v); };
        const mesure = function (p) { poserLeJoueur(L, p); vus.length = 0; L.Chantiers.travailler(); return vus[vus.length - 1]; };
        const cx = (d.x + d.l / 2) * 16, bas = (d.y + d.h) * 16;
        const pres = mesure({ x: cx, y: bas + 40 });
        const moyen = mesure({ x: cx, y: bas + 250 });
        const auLoin = mesure(loin(L));
        poserLeJoueur(L, { x: cx, y: bas + 40 });
        L.B.interieur = { banc: true };
        vus.length = 0; L.Chantiers.travailler();
        const piece = vus[vus.length - 1];
        L.B.interieur = null;
        return { pres: pres, moyen: moyen, loin: auLoin, piece: piece };
    """))
    assert r["pres"] > 0.8, r
    assert 0 < r["moyen"] < r["pres"], r
    assert r["loin"] == 0, r
    assert r["piece"] == 0, "on entend le chantier depuis une pièce"


def test_la_grue_se_dessine_tant_que_sa_fleche_est_a_l_ecran(banc):
    """⚠️ Un décor sortait de la liste de dessin à 48 px de l'écran, mesurés à son
    PIED : la grue — 112 px de large, 90 au-dessus de sa tuile — surgissait d'un
    coup en montant la rue. Et la nuit, elle se peint à sa pose de repos."""
    r = banc(_juge("""
        L.Jeu.commencer();
        L.B.partie.heure = 0.5;
        const f = L.DECORS.grue, cam = L.B.cam;
        const g = L.Entites.creer('decor', cam.x + 200, cam.y + 100, { decor: 'grue', r: 7, dessine: true, v: 0 });
        const compte = function (x, y) {
            g.x = x; g.y = y;
            L.Entites.dessiner(o.ctx, cam);
            return L.B.stats.entites;
        };
        const sousLEcran = compte(cam.x + 200, cam.y + L.VH + f.h + 20);
        const flecheEnBas = compte(cam.x + 200, cam.y + L.VH + f.ancre[1] - 10);
        const aGauche = compte(cam.x - f.w - 20, cam.y + 100);
        const flecheAGauche = compte(cam.x - 50, cam.y + 100);
        const cles = [];
        const cuire = L.Atlas.cuirePeintre;
        L.Atlas.cuirePeintre = function (cle) { if (cle.indexOf('decor|grue|') === 0) cles.push(cle); return cuire.apply(null, arguments); };
        L.B.t = 7 * f.anime;
        compte(cam.x + 200, cam.y + 100);
        const jour = cles.slice();
        cles.length = 0;
        L.B.partie.heure = 0.95;
        compte(cam.x + 200, cam.y + 100);
        L.Atlas.cuirePeintre = cuire;
        return { sousLEcran: sousLEcran, flecheEnBas: flecheEnBas, aGauche: aGauche,
                 flecheAGauche: flecheAGauche, jour: jour, nuit: cles };
    """))
    assert r["flecheEnBas"] == r["sousLEcran"] + 1, "le pied sous l'écran, la flèche visible : la grue ne se peint pas"
    assert r["flecheAGauche"] == r["aGauche"] + 1, "le pied à gauche de l'écran, la flèche visible : la grue ne se peint pas"
    assert r["jour"] == ["decor|grue|7"], r
    assert r["nuit"] == ["decor|grue|0"], "la nuit, la grue tourne encore"


def test_une_fleche_qui_depasse_retient_la_phase(banc):
    """⚠️ Le chantier hors de vue, mais la flèche de sa grue encore à l'écran :
    la phase attend — une grue qui s'évapore se voit autant qu'un mur."""
    r = banc(_juge("""
        L.Jeu.commencer();
        const ch = L.Chantiers.liste[0], d = ch.def;
        const g = d.phases[3].machines[0];
        g.x = d.x + d.l - 1;                     // au bord est : la flèche dépasse de l'empreinte
        L.Chantiers.appliquer(0, 3);
        poserLeJoueur(L, loin(L));
        for (const e of L.B.entites.slice()) {
            if (e === L.B.joueur || !(e.type === 'pieton' || e.type === 'agent' || e.type === 'vehicule')) continue;
            if (e.x > (d.x - 2) * 16 && e.x < (d.x + d.l + 2) * 16 && e.y > (d.y - 2) * 16 && e.y < (d.y + d.h + 2) * 16) L.Entites.retirer(e);
        }
        const f = L.DECORS.grue;
        L.B.cam.x = g.x * 16 + 8 - f.ancre[0] + f.w - 4;
        L.B.cam.y = (d.y + d.h / 2) * 16 - L.VH / 2;
        L.B.partie.jour += 60;
        tourner(L, 3);
        const retenue = ch.posee;
        L.B.cam.x += 16;
        tourner(L, 3);
        return { retenue: retenue, apres: ch.posee, voulue: L.Chantiers.phaseVoulue(d),
                 horsEmpreinte: L.B.cam.x - 16 > (d.x + d.l) * 16 + 40 };
    """))
    assert r["horsEmpreinte"], "le juge doit placer l'écran hors de la marge de l'empreinte"
    assert r["voulue"] == 4
    assert r["retenue"] == 3, "la phase s'est posée sous la flèche de la grue"
    assert r["apres"] == 4


def test_les_sons_du_chantier_sortent_avec_ou_sans_leur_fichier(banc):
    """Le filet, comme partout : avant que les fichiers arrivent, chaque son de
    chantier se synthétise — et tout ce qui démarre atteint la sortie. Trop loin,
    rien ne part. Fichiers chargés, la boule joue son échantillon ; le bip de
    recul, lui, reste synthétisé (trois bips à 1050 Hz) : il n'a pas de fichier."""
    r = banc("""async function (L, o) {
        const joues = o.brancherAudio(true);
        L.Jeu.commencer();
        L.Son.reveiller();
        const j = L.B.joueur, SFX = L.Son.SFX;
        const sons = ['boule', 'marteau_piqueur', 'godet', 'bip_recul', 'marteau', 'scie', 'plaque'];
        const filet = {};
        for (const son of sons) {
            const n = joues.length;
            const v = SFX.chantier(son, j.x + 60, j.y, 340);
            filet[son] = { volume: v, joues: joues.length - n };
        }
        const n = joues.length;
        const loinV = SFX.chantier('boule', j.x + 500, j.y, 460);
        const loin = joues.length - n;
        await o.attendre(); await o.attendre(); await o.attendre();
        const ctx = L.Son.contexte;
        const m = joues.length;
        SFX.chantier('boule', j.x + 60, j.y, 460);
        const bouleFichier = joues.slice(m).map(function (x) { return x.quoi; });
        const k = joues.length;
        SFX.chantier('bip_recul', j.x + 60, j.y, 340);
        const bips = joues.slice(k).filter(function (x) { return x.quoi === 'ton' && x.hz === 1050; }).length;
        SFX.rumeur_chantier(0.5);
        const rumeur = L.Son.volumeBoucle('chantier');
        SFX.rumeur_chantier(0);
        return { filet: filet, loin: loin, loinV: loinV, bouleFichier: bouleFichier, bips: bips,
                 charge: L.Son.estCharge('boule'), rumeur: rumeur, eteinte: L.Son.boucleActive('chantier'),
                 muettes: ctx.sourcesMuettes() };
    }""")
    for son, f in r["filet"].items():
        assert f["volume"] > 0 and f["joues"] > 0, f"{son} : sans fichier, le chantier est muet"
    assert r["loin"] == 0 and r["loinV"] == 0, "un coup de boule s'entend à l'autre bout de la ville"
    assert r["charge"], "le fichier de la boule ne se charge pas"
    assert r["bouleFichier"] == ["echantillon"], "fichier chargé, la boule joue encore sa synthèse"
    assert r["bips"] == 3
    assert r["rumeur"] and r["rumeur"] > 0, "la rumeur du chantier ne tourne pas"
    assert r["eteinte"] is False, "la rumeur ne s'éteint pas"
    assert r["muettes"] == 0, "un son de chantier démarre sans atteindre la sortie"


# --- 3e vague : la tranchée et l'équipe -------------------------------------------------

#: Une toile qui note ce qu'on y peint : chaque `fillRect` avec sa couleur du moment.
ENREGISTREUR = """
  function enregistreur() {
    const log = []; let style = '';
    return new Proxy({}, {
      get: function (t, k) {
        if (k === 'log') return log;
        if (k === 'fillStyle') return style;
        return function () { if (k === 'fillRect') log.push([style].concat(Array.from(arguments))); };
      },
      set: function (t, k, v) { if (k === 'fillStyle') style = v; return true; },
    });
  }
  // Le chantier dont la phase est `phase`, ou celui qui a une tranchée à cette phase.
  function avecTranchee(L) {
    const i = L.Chantiers.liste.findIndex(function (c) { return c.def.tranchee && c.def.tranchee.length; });
    if (i < 0) throw new Error('aucun chantier n\\'a de tranchée');
    return i;
  }
"""


def test_une_plaque_claque_sous_les_roues_et_ne_coute_rien(banc):
    """⚠️ Un nid-de-poule est un accident, une plaque d'acier est un décor qu'on
    sent : elle claque et elle secoue, elle ne coûte rien. Même répit que les
    nids (sans lui, un char lent la claque à chaque image), et rien à l'arrêt."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = avecTranchee(L), ch = L.Chantiers.liste[i], t = ch.def.tranchee, TT = L.TT;
        const claque = [];
        const vrai = L.Son.SFX.chantier;
        L.Son.SFX.chantier = function (son, x, y, portee) { claque.push([son, Math.round(x), Math.round(y), portee]); return 1; };
        const j = L.B.joueur;
        j.x = t[0][0] * TT + 8; j.y = t[0][1] * TT + 8; L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        v.x = t[0][0] * TT + 8; v.y = t[0][1] * TT + 8; L.Entites.indexer();
        const out = {};
        for (const phase of [0, 1, 2, 3, 4]) {
            L.Chantiers.appliquer(i, phase);
            out['phase' + phase] = t.map(function (c) { return L.Monde.plaqueDAcier(c[0], c[1]); });
        }
        out.ailleurs = L.Monde.plaqueDAcier(t[0][0] + 5, t[0][1] + 5);
        L.Chantiers.appliquer(i, 2);
        // 1. A L'ARRET
        v.vitesse = 0; v.vx = 0; v.vy = 0; v.plaqueT = 0;
        const vie0 = v.vie;
        L.B.cam.secousse = 0; claque.length = 0;
        for (let k = 0; k < 10; k++) L.Vehicules.majPlaque(v);
        out.arret = { claque: claque.length, secousse: L.B.cam.secousse };
        // 2. EN ROULANT : une fois, le temps du répit
        v.vitesse = 2; v.vx = 2; v.vy = 0; v.plaqueT = 0;
        for (let k = 0; k < 10; k++) L.Vehicules.majPlaque(v);
        out.roule = { claque: claque.slice(), perdu: vie0 - v.vie, secousse: L.B.cam.secousse, repit: v.plaqueT };
        // 3. Le répit passé, elle claque de nouveau.
        v.plaqueT = 0; claque.length = 0;
        L.Vehicules.majPlaque(v);
        out.encore = claque.length;
        // 4. En l'air, rien.
        v.plaqueT = 0; v.z = 12; claque.length = 0;
        L.Vehicules.majPlaque(v);
        out.enLAir = claque.length;
        v.z = 0;
        // 5. Le trafic claque aussi, mais la caméra ne tremble que pour le joueur.
        const autre = o.char('auto', 0, 0, 0);
        autre.x = t[1][0] * TT + 8; autre.y = t[1][1] * TT + 8; autre.vitesse = 2; autre.vx = 2; autre.vy = 0; autre.plaqueT = 0;
        L.B.cam.secousse = 0; claque.length = 0;
        L.Vehicules.majPlaque(autre);
        out.trafic = { claque: claque.length, secousse: L.B.cam.secousse };
        L.Son.SFX.chantier = vrai;
        return out;
    """))
    ph = vehicules.PHYSIQUE
    assert r["phase0"] == [False, False] and r["phase1"] == [False, False], "des plaques avant que le terrain soit rasé"
    assert r["phase2"] == [True, True] and r["phase3"] == [True, True], "la tranchée n'a pas ses plaques"
    assert r["phase4"] == [False, False], "le neuf debout, les plaques claquent encore"
    assert r["ailleurs"] is False
    assert r["arret"] == {"claque": 0, "secousse": 0}, f"un char à l'arrêt claque : {r['arret']}"
    assert [c[0] for c in r["roule"]["claque"]] == ["plaque"], f"une plaque, un claquement, puis le répit : {r['roule']}"
    assert r["roule"]["perdu"] == 0, "une plaque d'acier ne coûte rien"
    assert abs(r["roule"]["secousse"] - ph["plaque_secousse"]) < 1e-9, r["roule"]
    assert r["roule"]["repit"] > 0, "aucun répit : la plaque claque à chaque image"
    assert r["encore"] == 1, "le répit passé, elle ne claque plus"
    assert r["enLAir"] == 0, "un char qui saute claque sur la plaque"
    assert r["trafic"]["claque"] == 1 and r["trafic"]["secousse"] == 0, f"le trafic, lui : {r['trafic']}"


def test_les_plaques_survivent_a_une_porte(banc):
    """⚠️ Comme les nids : l'index vit SUR LA CARTE. Une pièce passe par `charger` ;
    ressorti, la tranchée doit encore claquer."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = avecTranchee(L), t = L.Chantiers.liste[i].def.tranchee, c = L.Monde.carte;
        L.Chantiers.appliquer(i, 2);
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        const j = L.B.joueur;
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.Monde.centrerCamera(j.x, j.y);
        L.Jeu.entrer(porte);
        o.fondu();
        const dedans = !!L.B.interieur;
        L.Jeu.sortir();
        o.fondu();
        return { dedans: dedans, dehors: L.B.interieur === null,
                 plaques: t.map(function (x) { return L.Monde.plaqueDAcier(x[0], x[1]); }) };
    """))
    assert r["dedans"] and r["dehors"], r
    assert r["plaques"] == [True, True], "ressorti d'une pièce, la tranchée ne claque plus"


def test_la_tranchee_se_peint_selon_la_phase_et_recuit_son_morceau(banc):
    """Des plaques d'acier jusqu'au neuf, l'asphalte refait ensuite, rien avant.
    Et le morceau de rue se recuit à chaque changement : sans cela, la couche
    peinte du cache garde l'ancienne rue."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = avecTranchee(L), ch = L.Chantiers.liste[i], t = ch.def.tranchee, c = L.Monde.carte;
        const mx = Math.floor(t[0][0] / 16), my = Math.floor(t[0][1] / 16);
        const cle = mx + ',' + my;
        const px = (t[0][0] - mx * 16) * 16, py = (t[0][1] - my * 16) * 16;
        const dedans = function (r) { return r[1] >= px && r[1] < px + 32 && r[2] >= py && r[2] < py + 16; };
        const sortie = {};
        for (const phase of [0, 1, 2, 3, 4]) {
            // ⚠️ Le cache doit être REMPLI avant : un juge qui regarde un cache
            // vide ne verrait pas qu'on ne le vide plus.
            c.morceaux.set(cle, { cuit: true });
            L.Chantiers.appliquer(i, phase);
            const encore = c.morceaux.has(cle);
            const ctx = enregistreur();
            L.Chantiers.peindre(ctx, mx, my);
            const sur = ctx.log.filter(dedans).map(function (r) { return r[0]; });
            sortie[phase] = { acier: sur.indexOf('#7e858d') >= 0, refait: sur.indexOf('#25262c') >= 0,
                              ruban: sur.indexOf('#e8b33c') >= 0, encore: encore };
        }
        // ⚠️ Et une tranchée qui tombe dans un AUTRE morceau que la marge du bâtiment
        // (sur la graine livrée, elle est toujours dans le même) : la tranchée
        // recuit le sien, elle ne compte pas sur celui de la façade.
        const loinTuile = [t[0][0], t[0][1] + 32];
        ch.def.tranchee = [loinTuile, [loinTuile[0] + 1, loinTuile[1]]];
        const autre = Math.floor(loinTuile[0] / 16) + ',' + Math.floor(loinTuile[1] / 16);
        c.morceaux.set(autre, { cuit: true });
        L.Chantiers.appliquer(i, 2);
        sortie.autreMorceau = c.morceaux.has(autre);
        return sortie;
    """))
    for phase in "01":
        assert not r[phase]["acier"] and not r[phase]["refait"], f"la rue est peinte avant la tranchée : {r[phase]}"
    for phase in "23":
        assert r[phase]["acier"] and r[phase]["ruban"], f"phase {phase} : pas de plaques : {r[phase]}"
        assert not r[phase]["refait"]
    assert r["4"]["refait"] and not r["4"]["acier"], f"le neuf debout, la rue n'est pas refaite : {r['4']}"
    for phase in "01234":
        assert not r[phase]["encore"], "le morceau de la tranchée n'est pas recuit au changement de phase"
    assert r["autreMorceau"] is False, "la tranchée ne recuit pas son propre morceau"


def test_la_tranchee_ne_change_pas_sous_les_yeux(banc):
    """⚠️ Des plaques qui surgissent au milieu de la rue se voient autant qu'un mur :
    la caméra sur la TRANCHÉE (le bâtiment, lui, est plus haut que l'écran), la phase
    qui la change attend — et se pose dès qu'on a tourné le coin."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = L.Chantiers.liste.findIndex(function (c) {
            return c.posee === 1 && c.def.tranchee.length && c.def.phases[2].tranchee !== c.def.phases[1].tranchee;
        });
        if (i < 0) throw new Error('aucun chantier qui gagne sa tranchée à la prochaine phase');
        const ch = L.Chantiers.liste[i], d = ch.def, t = d.tranchee;
        // La tranchée tout en haut de l'écran : l'immeuble est au-dessus, hors de vue.
        poserLeJoueur(L, { x: t[0][0] * 16 + 8, y: t[0][1] * 16 + L.VH / 2 - 4 });
        const cam = L.B.cam;
        const immeubleVu = (d.y + d.h) * 16 + 40 > cam.y;
        const tranchee = t[0][1] * 16 + 16 > cam.y && t[0][1] * 16 < cam.y + L.VH;
        L.B.partie.jour += d.pas;
        o.frame(100);
        const devant = ch.posee;
        poserLeJoueur(L, loin(L));
        o.frame(100);
        return { immeubleVu: immeubleVu, tranchee: tranchee, devant: devant, apres: ch.posee, voulue: L.Chantiers.phaseVoulue(d) };
    """))
    assert not r["immeubleVu"] and r["tranchee"], f"le montage ne tient pas : {r}"
    assert r["devant"] == 1, "les plaques sont apparues sous les yeux du joueur"
    assert r["apres"] == r["voulue"] == 2, "hors de vue, la phase du jour doit se poser"


def _equipe(o_corps: str) -> str:
    return _juge(ENREGISTREUR + """
        // L'équipe du TERRAIN : le signaleur, lui, a ses propres juges.
        function equipe(L, id) {
            return L.B.entites.filter(function (e) { return e.equipeDe === id && e.vivant && e.posteDe !== 'signal'; });
        }
        // Le joueur au sud des postes, à portée de la bulle mais hors de l'écran.
        function auSud(L, ch, tuile) {
            poserLeJoueur(L, { x: tuile[0] * 16 + 8, y: tuile[1] * 16 + 8 + 300 });
        }
        L.Jeu.commencer();
        const i = L.Chantiers.liste.findIndex(function (c) { return c.def.phases[2].equipe.length === 2; });
        const ch = L.Chantiers.liste[i], d = ch.def, postes = d.phases[2].equipe, id = d.id;
        L.Chantiers.appliquer(i, 2);
    """ + o_corps)


def test_l_equipe_prend_son_poste_hors_de_l_ecran(banc):
    """Un ouvrier par poste, planté, intouchable, hors de la foule — et jamais sous
    les yeux du joueur, ni trop loin pour qu'on l'oublie aussitôt."""
    r = banc(_equipe("""
        // Loin : personne.
        poserLeJoueur(L, loin(L));
        L.Chantiers.equiper();
        const loinN = equipe(L, id).length;
        // Sur les postes : ils seraient vus naître.
        poserLeJoueur(L, { x: postes[0][0] * 16 + 8, y: postes[0][1] * 16 + 8 });
        L.Chantiers.equiper();
        const surPlaceN = equipe(L, id).length;
        // Au sud, à portée de la bulle, hors de l'écran.
        auSud(L, ch, postes[0]);
        L.Chantiers.equiper();
        const gens = equipe(L, id);
        const premiere = gens.length;
        L.Chantiers.equiper(); L.Chantiers.equiper();
        return { loinN: loinN, surPlaceN: surPlaceN, premiere: premiere, apres: equipe(L, id).length,
                 postes: postes, gens: gens.map(function (e) {
                     return { tx: Math.floor(e.x / 16), ty: Math.floor(e.y / 16), poste: e.posteDe, metier: e.metier,
                              intouchable: e.intouchable, etat: e.etat, chantier: !!e.chantier, arch: e.arch,
                              plante: !!e.plante, dansLaListe: L.B.entites.indexOf(e) >= 0 };
                 }),
                 voie: L.B.entites.filter(function (e) { return e.chantier; }).length };
    """))
    assert r["loinN"] == 0, "l'équipe naît à l'autre bout de la ville"
    assert r["surPlaceN"] == 0, "l'équipe naît sous les yeux du joueur"
    assert r["premiere"] == 2 and r["apres"] == 2, f"un poste, un homme — jamais deux : {r}"
    assert sorted((g["tx"], g["ty"]) for g in r["gens"]) == sorted(tuple(p) for p in r["postes"]), r["gens"]
    for g in r["gens"]:
        assert g["arch"] == "ouvrier" and g["metier"] == "chantier", g
        assert g["intouchable"] and g["etat"] == "fige" and g["plante"], g
        assert not g["chantier"], "marqué `chantier` : il passerait pour un ouvrier de la voie fermée"
    assert r["voie"] == 0


def test_l_equipe_rentre_la_nuit_et_avec_la_phase(banc):
    """Le jour elle travaille ; la nuit elle rentre — hors de l'écran seulement ;
    et une phase sans équipe (le neuf) la renvoie chez elle."""
    r = banc(_equipe("""
        auSud(L, ch, postes[0]);
        L.B.partie.heure = 0.5;
        L.Chantiers.equiper();
        const jour = equipe(L, id).length;
        // La nuit, hors de l'écran : ils rentrent.
        L.B.partie.heure = 0.95;
        L.Chantiers.equiper();
        const nuit = equipe(L, id).length;
        // Et ils ne naissent pas la nuit.
        L.Chantiers.equiper();
        const nuitBis = equipe(L, id).length;
        // Le matin, ils reviennent ; le neuf, ils repartent.
        L.B.partie.heure = 0.5;
        L.Chantiers.equiper();
        const matin = equipe(L, id).length;
        L.Chantiers.appliquer(i, 4);
        auSud(L, ch, postes[0]);
        L.Chantiers.equiper();
        const neuf = equipe(L, id).length;
        // La nuit, mais sous les yeux : personne ne les voit disparaître.
        L.Chantiers.appliquer(i, 2);
        auSud(L, ch, postes[0]);
        L.Chantiers.equiper();
        const avant = equipe(L, id);
        const e = avant[0];
        poserLeJoueur(L, { x: e.x, y: e.y + 30 });
        L.B.partie.heure = 0.95;
        L.Chantiers.equiper();
        return { jour: jour, nuit: nuit, nuitBis: nuitBis, matin: matin, neuf: neuf, sousLesYeux: equipe(L, id).length,
                 avant: avant.length };
    """))
    assert r["jour"] == 2, r
    assert r["nuit"] == 0 and r["nuitBis"] == 0, f"la nuit, l'équipe est encore au travail : {r}"
    assert r["matin"] == 2, f"au matin, l'équipe ne revient pas : {r}"
    assert r["neuf"] == 0, f"personne ne travaille sur un bâtiment neuf : {r}"
    assert r["sousLesYeux"] == r["avant"], f"l'équipe disparaît sous les yeux du joueur : {r}"


def test_l_equipe_regarde_passer(banc):
    """À moins de `REGARD` pixels, le visage tourné vers le joueur ; sinon vers la
    machine du jour."""
    r = banc(_equipe("""
        auSud(L, ch, postes[0]);
        L.B.partie.heure = 0.5;
        L.Chantiers.equiper();
        const e = equipe(L, id)[0];
        const face = function (x, y) {
            poserLeJoueur(L, { x: x, y: y });
            e.face = 'bas';
            L.Chantiers.maj();
            return e.face;
        };
        const proche = { est: face(e.x + 40, e.y), ouest: face(e.x - 40, e.y), nord: face(e.x, e.y - 40), sud: face(e.x, e.y + 40) };
        const m = ch.machines[0];
        const eloigne = face(e.x + 60, e.y + L.Chantiers.REGARD + 200);
        const dx = m.x - e.x, dy = m.y - e.y;
        const versLaMachine = Math.abs(dx) >= Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
        return { proche: proche, eloigne: eloigne, versLaMachine: versLaMachine };
    """))
    assert r["proche"] == {"est": "droite", "ouest": "gauche", "nord": "haut", "sud": "bas"}, r["proche"]
    assert r["eloigne"] == r["versLaMachine"], f"loin du joueur, il ne regarde pas sa machine : {r}"


def test_l_equipe_suit_la_phase(banc):
    """⚠️ Un poste pris par l'homme d'hier reste « pris » : sans le renvoi de
    l'équipe au changement de phase, il resterait planté là où la grue se pose."""
    r = banc(_juge(ENREGISTREUR + """
        L.Jeu.commencer();
        const i = L.Chantiers.liste.findIndex(function (c) { return c.def.phases[3].equipe.length === 2; });
        const ch = L.Chantiers.liste[i], d = ch.def, id = d.id;
        const equipe = function () { return L.B.entites.filter(function (e) { return e.equipeDe === id && e.vivant && e.posteDe !== 'signal'; }); };
        L.B.partie.heure = 0.5;
        L.Chantiers.appliquer(i, 2);
        poserLeJoueur(L, { x: d.phases[2].equipe[0][0] * 16 + 8, y: d.phases[2].equipe[0][1] * 16 + 8 + 300 });
        L.Chantiers.equiper();
        const hier = equipe();
        L.Chantiers.appliquer(i, 3);
        const apresChangement = equipe().length, hierEncore = hier.filter(function (e) { return L.B.entites.indexOf(e) >= 0; }).length;
        L.Chantiers.equiper();
        return { hier: hier.length, apresChangement: apresChangement, hierEncore: hierEncore,
                 aujourdhui: equipe().map(function (e) { return [Math.floor(e.x / 16), Math.floor(e.y / 16)]; }),
                 postes: d.phases[3].equipe };
    """))
    assert r["hier"] == 2
    assert r["apresChangement"] == 0 and r["hierEncore"] == 0, f"l'équipe d'hier est restée : {r}"
    assert sorted(r["aujourdhui"]) == sorted(r["postes"]), f"l'équipe du jour n'est pas aux postes de la phase : {r}"


# --- 4e vague : le signaleur --------------------------------------------------------------

#: Un chantier dont le signaleur a huit tuiles de voie droite derrière lui (côté d'où vient
#: le trafic) : ni croisement ni ligne d'arrêt, pour qu'aucun feu ne brouille la mesure.
SIGNALEUR = """
  // Le signaleur tel que le jeu le lit : Python n'envoie que sa tuile [x, y] ; la voie est
  // la rangée dessous, et son sens se lit sur la carte.
  function sig(L, ch) {
    const s = ch.def.signaleur;
    return { x: s[0], y: s[1], voie: s[1] + 1, sens: L.Monde.fleche(s[0], s[1] + 1) };
  }
  function droit(L, ch) {
    const s = sig(L, ch), c = L.Monde.carte, p = { '<': 1, '>': -1 }[s.sens], voie = s.y + 1;
    for (let k = 0; k <= 8; k++) {
      const x = s.x + p * k;
      if (c.voie[voie][x] !== s.sens || L.Monde.intersectionA(x, voie) || c.arrets[x + ',' + voie]) return false;
    }
    return true;
  }
  function chantierDuSignaleur(L) {
    const i = L.Chantiers.liste.findIndex(function (c) { return c.def.signaleur && c.def.phases[2].tranchee === 'plaques' && droit(L, c); });
    if (i < 0) throw new Error('aucun chantier dont le signaleur ait une voie droite derrière lui');
    return i;
  }
  // Le joueur au sud du poste du signaleur, à portée de la bulle mais hors de l'écran.
  function auSudDuSignaleur(L, s) { poserLeJoueur(L, { x: s.x * 16 + 8, y: s.y * 16 + 8 + 300 }); }
  function homme(L, id) {
    return L.B.entites.find(function (e) { return e.equipeDe === id && e.posteDe === 'signal' && e.vivant; });
  }
  function palette(L, id) {
    return L.B.entites.find(function (e) { return e.type === 'decor' && e.palette === id; });
  }
  function char(L, ch, tuiles, extra) {
    const s = sig(L, ch), p = { '<': 1, '>': -1 }[s.sens];
    const v = L.Vehicules.creer('auto', (s.x + p * tuiles) * 16 + 8, (s.y + 1) * 16 + 8, s.sens === '<' ? Math.PI : 0,
                                Object.assign({ conducteur: 'trafic', etat: 'roule', sens: s.sens }, extra || {}));
    return v;
  }
"""


def _signal(corps: str) -> str:
    return _juge(SIGNALEUR + """
        L.Jeu.commencer();
        const i = chantierDuSignaleur(L), ch = L.Chantiers.liste[i], d = ch.def, s = sig(L, ch), id = d.id;
        L.B.partie.heure = 0.5;
        L.Chantiers.appliquer(i, 2);
    """ + corps)


def test_le_signaleur_nait_avec_sa_palette_et_s_en_va_avec_elle(banc):
    """Un homme sur son trottoir, intouchable, tourné vers la route, avec une palette
    dans la main — et jamais une palette qui dit ARRÊT toute seule."""
    r = banc(_signal("""
        const avant = { homme: !!homme(L, id), palette: !!palette(L, id) };
        // Sous les yeux : il ne naît pas.
        poserLeJoueur(L, { x: s.x * 16 + 8, y: s.y * 16 + 8 });
        L.Chantiers.equiper();
        const surPlace = !!homme(L, id);
        auSudDuSignaleur(L, s);
        L.Chantiers.equiper();
        const e = homme(L, id), p = palette(L, id);
        e.face = 'haut';
        L.Chantiers.maj();
        const jour = { tx: Math.floor(e.x / 16), ty: Math.floor(e.y / 16), intouchable: e.intouchable, etat: e.etat,
                       metier: e.metier, chantier: !!e.chantier, face: e.face, arch: e.arch,
                       palette: !!p, decor: p && p.decor, solide: p && p.solide, aCote: p && Math.abs(p.x - e.x) < 12 && p.y >= e.y,
                       pose0: L.Entites.poseDuDecor(L.DECORS.panneau_signaleur, 0, false),
                       pose1: L.Entites.poseDuDecor(L.DECORS.panneau_signaleur, 180, false) };
        // Une seule palette, un seul homme, même après plusieurs passes.
        L.Chantiers.equiper(); L.Chantiers.equiper();
        const combien = { hommes: L.B.entites.filter(function (q) { return q.equipeDe === id && q.posteDe === 'signal'; }).length,
                          palettes: L.B.entites.filter(function (q) { return q.palette === id; }).length };
        // La phase 3 le garde ; le neuf et la démolition non.
        const parPhase = {};
        for (const phase of [0, 1, 3, 4]) {
            L.Chantiers.appliquer(i, phase);
            auSudDuSignaleur(L, s);
            L.Chantiers.equiper();
            parPhase[phase] = { homme: !!homme(L, id), palette: !!palette(L, id) };
        }
        // La nuit, hors de l'écran : il rentre, et la palette avec lui.
        L.Chantiers.appliquer(i, 2);
        auSudDuSignaleur(L, s);
        L.Chantiers.equiper();
        const jourBis = { homme: !!homme(L, id), palette: !!palette(L, id) };
        L.B.partie.heure = 0.95;
        // ⚠️ Un homme resté sous les yeux la nuit : le DESSIN (la pose par défaut) et la
        // LOGIQUE (`false`, jamais de repos) disent la même chose — sinon la palette
        // montre ARRÊT pendant que le trafic passe.
        const f = L.DECORS.panneau_signaleur;
        const poseDeNuit = [L.Entites.poseDuDecor(f, 200), L.Entites.poseDuDecor(f, 200, false), L.Monde.estNuit()];
        L.Chantiers.equiper();
        const nuit = { homme: !!homme(L, id), palette: !!palette(L, id) };
        // L'homme parti (oublié loin du joueur) : la palette ne reste pas seule.
        L.B.partie.heure = 0.5;
        L.Chantiers.equiper();
        L.Entites.retirer(homme(L, id));
        poserLeJoueur(L, loin(L));
        L.Chantiers.equiper();
        const orpheline = { homme: !!homme(L, id), palette: !!palette(L, id) };
        return { avant: avant, surPlace: surPlace, jour: jour, combien: combien, parPhase: parPhase, jourBis: jourBis,
                 nuit: nuit, orpheline: orpheline, poste: [s.x, s.y], poseDeNuit: poseDeNuit };
    """))
    assert r["avant"] == {"homme": False, "palette": False}
    assert r["surPlace"] is False, "le signaleur naît sous les yeux du joueur"
    j = r["jour"]
    assert (j["tx"], j["ty"]) == tuple(r["poste"]), j
    assert j["arch"] == "ouvrier" and j["intouchable"] and j["etat"] == "fige" and j["metier"] == "chantier", j
    assert not j["chantier"], "marqué `chantier`, il passerait pour un ouvrier de la voie fermée"
    assert j["face"] == "bas", "le signaleur ne regarde pas la route"
    assert j["palette"] and j["decor"] == "panneau_signaleur" and not j["solide"] and j["aCote"], j
    assert (j["pose0"], j["pose1"]) == (0, 1), "la palette ne dit pas ARRÊT puis LENTEMENT"
    assert r["combien"] == {"hommes": 1, "palettes": 1}, r["combien"]
    assert r["parPhase"]["0"] == r["parPhase"]["1"] == r["parPhase"]["4"] == {"homme": False, "palette": False}, r["parPhase"]
    assert r["parPhase"]["3"] == {"homme": True, "palette": True}, r["parPhase"]
    assert r["jourBis"] == {"homme": True, "palette": True}
    assert r["nuit"] == {"homme": False, "palette": False}, "la nuit, le signaleur est encore là"
    assert r["poseDeNuit"] == [1, 1, True], f"le dessin et la logique de la palette divergent la nuit : {r['poseDeNuit']}"
    assert r["orpheline"] == {"homme": False, "palette": False}, "la palette reste seule sur le trottoir"


def test_le_trafic_lit_la_palette(banc):
    """`signalDevant` : ARRÊT seulement, sur sa voie, dans son sens, avant lui, à moins
    de six tuiles, et jamais pour une poursuite ni une rame. Et `obstacleDevant` le
    lit — la conduite ordinaire du trafic n'a rien d'autre à savoir."""
    r = banc(_signal("""
        auSudDuSignaleur(L, s);
        L.Chantiers.equiper();
        const dist = function (v) { return L.Chantiers.signalDevant(v); };
        const v = char(L, ch, 4);
        const out = { longueur: v.def.longueur, anime: L.DECORS.panneau_signaleur.anime,
                      patience: L.B.defs.conduite.trafic.patience_images };
        L.B.t = 0;                                           // la palette dit ARRÊT
        out.arret = dist(v);
        out.obstacle = L.Vehicules.obstacleDevant(v);
        L.B.t = 180;                                         // ... puis LENTEMENT
        out.lentement = dist(v);
        out.obstacleLent = L.Vehicules.obstacleDevant(v);
        L.B.t = 0;
        // Le même char, ailleurs : ce que le signaleur ne dit pas à tout le monde.
        const ailleurs = function (retouche) {
            const w = char(L, ch, 4); retouche(w); const r = dist(w); L.Entites.retirer(w); return r;
        };
        out.autreRangee = ailleurs(function (w) { w.y += 16; });
        out.autreSens = ailleurs(function (w) { w.sens = s.sens === '<' ? '>' : '<'; });
        out.dejaPasse = char(L, ch, -3) && (function () { const w = char(L, ch, -3); const r = dist(w); L.Entites.retirer(w); return r; })();
        out.trop_loin = (function () { const w = char(L, ch, L.Chantiers.PORTEE_SIGNAL_TUILES + 3); const r = dist(w); L.Entites.retirer(w); return r; })();
        out.poursuite = ailleurs(function (w) { w.poursuite = true; });
        out.rame = ailleurs(function (w) { w.rails = true; });
        // Sans son homme (oublié loin du joueur, la palette avec lui), personne ne dit rien.
        L.Entites.retirer(homme(L, id));
        poserLeJoueur(L, loin(L));
        L.Chantiers.equiper();
        out.sansHomme = dist(v);
        return out;
    """))
    marge = r["longueur"] / 2
    assert r["anime"] < r["patience"], \
        "l'ARRÊT dure plus que la patience du trafic : il forcerait le passage au lieu de l'obéir"
    assert abs(r["arret"] - (4 * 16 - marge)) < 1e-6, f"la distance de l'ARRÊT n'est pas celle du nez : {r}"
    assert r["obstacle"] <= r["arret"], "la conduite ordinaire ne lit pas le signaleur"
    assert r["lentement"] == float("inf") or r["lentement"] is None, f"LENTEMENT arrête le trafic : {r}"
    # (JSON rend l'infini par `null`.)
    assert r["obstacleLent"] is None or r["obstacleLent"] > r["arret"], "LENTEMENT arrête encore le trafic"
    for cas in ("autreRangee", "autreSens", "dejaPasse", "trop_loin", "poursuite", "rame", "sansHomme"):
        assert r[cas] is None or r[cas] == float("inf"), f"le signaleur arrête aussi ce cas-là : {cas} = {r[cas]}"


def test_un_char_du_trafic_s_arrete_a_l_arret_et_repart_a_lentement(banc):
    """⚠️ Le geste, pas la fonction : un vrai char de trafic sur la voie du signaleur
    s'arrête avant la tranchée tant que la palette dit ARRÊT, sans jamais la passer, et
    repart quand elle dit LENTEMENT — en moins de trois secondes d'attente, sous la
    patience du trafic (il ne force pas le passage)."""
    r = banc(_signal("""
        auSudDuSignaleur(L, s);
        L.Chantiers.equiper();
        const v = char(L, ch, 5);
        L.B.t = 0;
        const sens = { '<': 1, '>': -1 }[s.sens], mx = homme(L, id).x;
        const avance = function () { return (v.x - mx) * sens; };      // > 0 : il n'a pas passé le signaleur
        const trace = [];
        let force = 0;
        for (let k = 0; k < 175; k++) {
            L.Chantiers.maj();
            o.frame(1);
            if (v.force > 0) force++;
            if (k % 25 === 0) trace.push([Math.round(avance()), +v.vitesse.toFixed(2)]);
        }
        const arrete = { avance: avance(), vitesse: v.vitesse, force: force, patience: v.patience, t: L.B.t };
        L.B.t = 180;
        for (let k = 0; k < 200; k++) o.frame(1);
        return { arrete: arrete, trace: trace, apres: avance(), vitesseApres: v.vitesse, present: L.B.entites.indexOf(v) >= 0 };
    """))
    a = r["arrete"]
    assert a["vitesse"] < 0.1, f"le char roule encore sous ARRÊT : {r['trace']}"
    assert a["avance"] > 16, f"le char a passé le signaleur sous ARRÊT : {r['trace']}"
    assert a["force"] == 0, f"le char force le passage pendant ARRÊT (patience {a['patience']}) : {r['trace']}"
    assert r["present"], "le char a disparu"
    assert r["apres"] < 0, f"à LENTEMENT, le char n'a pas repris sa route : {r}"
