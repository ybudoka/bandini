"""Les chars du trafic, sous Node : feux, stops, déport, sortie de T, char coincé,
virage à gauche, passages, stationnement, chevauchement — et la ville qui roule
3 000 images (les trottoirs se jugent sur ce même banc).

Découpé de `test_moteur_js.py` (vague D, 29 sept. 2026) : même banc, mêmes juges.
"""

import pytest


def test_le_feu_pieton_s_eteint_avant_que_les_chars_repartent(banc, paquet):
    """⚠️ Demande de Martin : « pour les piétons, il faut ajouter des lumières de
    priorité, et sinon ils ne passent pas. »

    La règle existait (`traverseeSure`) mais **personne ne la voyait** — et elle
    **se trompait d'un temps** : `!feuVert(...)` est vrai pendant l'**orange**
    aussi, donc les piétons s'engageaient exactement quand les chars accélèrent
    pour vider le croisement, le pire moment du cycle.

    Un vrai feu piéton ne s'allume pas au rouge : il s'éteint **avant** que les
    chars repartent. Ce juge parcourt un cycle entier, image par image."""
    t = paquet["conduite"]["trafic"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const cycle = 2 * (L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images);
        const inter = L.Monde.carte.intersections.find(function (i) { return i.feux; });
        const t0 = L.B.t;
        const suite = [];
        for (let k = 0; k < cycle; k++) {
            L.B.t = t0 + k;
            suite.push({
                // Le pieton qui traverse la rue est-ouest (passage « = »).
                pieton: L.Monde.feuPieton(inter, '>'),
                mesChars: L.Monde.feuVert(inter, '>'),
                lesAutres: L.Monde.feuVert(inter, '^'),
            });
        }
        L.B.t = t0;
        // Le blanc, jamais avec le vert de MA rue, jamais pendant un orange.
        let avecMesChars = 0, pendantOrange = 0, blanc = 0, degage = 0;
        for (const p of suite) {
            if (p.pieton === 'blanc') blanc++;
            if (p.pieton === 'degage') degage++;
            if (p.pieton === 'blanc' && p.mesChars) avecMesChars++;
            if (p.pieton === 'blanc' && !p.mesChars && !p.lesAutres) pendantOrange++;
        }
        // Le DEGAGEMENT : combien d'images entre la derniere blanche et le
        // moment ou mes chars repartent.
        // ⚠️ On tourne EN ROND : la fenetre commence a une phase quelconque, et
        // la derniere image blanche tombe souvent apres le dernier vert de la
        // fenetre. Chercher en avant sans reboucler, c'est ne rien trouver une
        // fois sur deux — et le juge dirait « pas de degagement » pour un
        // degagement parfait.
        let dernierBlanc = -1, apres = null;
        for (let k = 0; k < cycle; k++) {
            if (suite[k].pieton !== 'blanc') continue;
            if (suite[(k + 1) % cycle].pieton === 'blanc') continue;
            dernierBlanc = k;                 // la DERNIERE d'une plage blanche
        }
        for (let k = 1; k <= cycle; k++) {
            if (suite[(dernierBlanc + k) % cycle].mesChars) { apres = k - 1; break; }
        }
        return { cycle: cycle, blanc: blanc, degage: degage,
                 avecMesChars: avecMesChars, pendantOrange: pendantOrange,
                 degagementMesure: apres,
                 sansFeux: L.Monde.feuPieton({ feux: false }, '>') };
    }""")

    assert r["blanc"] > 0, "le feu piéton n'est jamais blanc : personne ne traverse plus"
    # ⚠️ LE DÉFAUT D'ORIGINE, tenu des deux côtés.
    assert r["avecMesChars"] == 0, (
        "le blanc s'allume pendant le vert des chars de sa rue (%s images)" % r["avecMesChars"]
    )
    assert r["pendantOrange"] == 0, (
        "le blanc s'allume pendant l'orange (%s images) : c'est exactement le moment où les "
        "chars accélèrent pour vider le croisement" % r["pendantOrange"]
    )
    # ⚠️ Et il s'éteint AVANT que les chars repartent : le dégagement, plus
    # l'orange, séparent la dernière image blanche du premier char qui roule.
    attendu = t["feu_pieton_degagement_images"] + t["feu_orange_images"]
    assert r["degagementMesure"] == attendu, (
        "le dégagement vaut %s images au lieu de %s : on s'engage trop tard"
        % (r["degagementMesure"], attendu)
    )
    assert r["degage"] == t["feu_pieton_degagement_images"], r["degage"]
    # Sans feux (un T), il n'y a pas de feu piéton : on traverse quand c'est libre.
    assert r["sansFeux"] == "aucun"


def test_les_vehicules_ne_se_chevauchent_pas(banc):
    """Retour de Martin, 21 sept. 2026 : « les véhicules ne devraient jamais pouvoir
    se chevaucher ».

    ⚠️ Deux chars « sur des rails » (le trafic, une ligne d'autobus) ne se
    poussaient PLUS DU TOUT l'un l'autre une fois pris ensemble
    (`heurterVehicules` sautait la paire au complet : « sur des rails, on ne se
    pousse pas », posé pour un autre bug — un vélo impatient qui plantait le nez
    d'un autobus dans le carrefour). Le remède avait bien empêché ce cas-là, mais
    laissait n'importe quel autre chevauchement entre deux chars sur rails
    TENIR pour de bon, faute d'un garde-fou qui les sépare. Corrigé : celui qui
    ATTEND LÉGITIMEMENT (feu rouge, stop, boîte) ne bouge jamais, c'est l'autre
    qui absorbe toute la séparation ; si aucun des deux n'attend, le partage aux
    masses d'avant suffit — la même règle que pour la foule
    (`test_la_foule_ne_se_traverse_plus`), appliquée aux chars.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        let paires = 0, pire = 0, images = 0;
        let gros = 0, plusLong = 0, creuse = 0;
        const durees = {}, profond = {}, creuseT = {};
        function pireChevauchement(a, b) {
            let p = -Infinity;
            for (const ca of L.Vehicules.cercles(a)) {
                for (const cb of L.Vehicules.cercles(b)) {
                    p = Math.max(p, ca.r + cb.r - Math.hypot(ca.x - cb.x, ca.y - cb.y));
                }
            }
            return p;
        }
        const touches = ['KeyD', 'KeyW', 'KeyA', 'KeyS'];
        for (let bloc = 0; bloc < 24; bloc++) {
            const t = touches[bloc % 4];
            o.touche(t);
            for (let k = 0; k < 40; k++) {
                o.frame(1); images++;
                const vs = L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.etat !== 'epave' && !e.aBord; });
                const vues = {};
                for (let a = 0; a < vs.length; a++) {
                    for (let b = a + 1; b < vs.length; b++) {
                        if (vs[a] === vs[b].remorque || vs[a] === vs[b].remorqueePar) continue;
                        const chevauche = pireChevauchement(vs[a], vs[b]);
                        if (chevauche > 0) { paires++; pire = Math.max(pire, chevauche); }
                        const cle = vs[a].id + '-' + vs[b].id;
                        // ⚠️ Meme methode que la foule : ce qui compte, c'est qu'un
                        // chevauchement se DEFAIT, pas qu'il n'en existe jamais un —
                        // deux chars qui se frolent se rapprochent une image, la
                        // separation les defait a la suivante.
                        if (chevauche > 1) {
                            gros++;
                            durees[cle] = (durees[cle] || 0) + 1;
                            plusLong = Math.max(plusLong, durees[cle]);
                            vues[cle] = true;
                            if (profond[cle] !== undefined && chevauche > profond[cle] + 0.01) {
                                creuseT[cle] = (creuseT[cle] || 0) + 1;
                                if (creuseT[cle] >= 2) creuse++;
                            } else creuseT[cle] = 0;
                            profond[cle] = chevauche;
                        }
                    }
                }
                for (const cle in durees) if (!vues[cle]) { durees[cle] = 0; delete profond[cle]; delete creuseT[cle]; }
            }
            o.relacher(t);
        }
        return { images: images, paires: paires, pire: +pire.toFixed(2), gros: gros, plusLong: plusLong, creuse: creuse };
    }""")
    assert r["images"] == 960
    assert r["creuse"] == 0, (
        f"{r['creuse']} fois un chevauchement de véhicules s'est CREUSÉ au lieu de se défaire : "
        "deux chars restent pris l'un dans l'autre"
    )
    assert r["plusLong"] <= 8, f"un chevauchement de véhicules tient {r['plusLong']} images d'affilée"
    assert r["pire"] < 8.0, f"deux véhicules s'enfoncent de {r['pire']} px l'un dans l'autre"


@pytest.fixture(scope="module")
def la_ville_roule(banc):
    """⚠️ **TROIS JUGES, UNE PARTIE** (vague C, 28 sept. 2026) : le trafic qui ne se
    bloque pas, le trafic qui reste dans sa voie et les piétons qui restent sur les
    trottoirs laissaient chacun la ville tourner deux ou trois mille images, le
    joueur immobile au départ, sans rien y toucher — seule la graine changeait (43,
    52, 51). Ce ne sont que des LECTURES du même monde : une seule partie de 3 000
    images les fait toutes, chacune sur la fenêtre qu'elle regardait. Les deux
    graines abandonnées ont été rejouées sur les trois règles avant la fusion
    (43, 51 et 52 : toutes vertes)."""
    return banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(43);
        // --- le trafic ne se bloque pas (images 1200 a 3000) ---
        // ⚠️ On ne suit un char que tant qu'il est LA : la bulle d'oubli retire
        // ceux qui s'eloignent du joueur, et un char retire ne bouge plus —
        // le test les prenait pour des chars bloques.
        //
        // ⚠️ Et on suit TOUS ceux qui passent, pas seulement ceux qui etaient
        // la a la premiere image : le joueur ne bouge pas, donc la plupart des
        // chars presents au depart s'en vont en quelques secondes. L'echantillon
        // tombait alors a deux ou trois, et le juge se mettait a dependre du
        // tirage plutot que du trafic. Un char BLOQUE, lui, reste dans la bulle
        // et accumule des images sans avancer d'un pixel : c'est exactement ce
        // qu'on cherche, et elargir l'echantillon le trouve mieux.
        const suivis = new Map();
        // --- la voie (des l'image 200, une sur 20) ---
        let horsRoute = 0, releves = 0, tournes = 0;
        const caps = new Map();
        // --- les trottoirs (des l'image 300, une sur 30) ---
        let surLaChaussee = 0, surUnPassage = 0, relevesPietons = 0;
        for (let i = 0; i < 3000; i++) {
            o.frame(1);
            if (i >= 1200) {
                L.B.entites.forEach(function (e) {
                    if (e.type !== 'vehicule' || e.conducteur !== 'trafic') return;
                    const s = suivis.get(e.id);
                    if (!s) { suivis.set(e.id, { x: e.x, y: e.y, d: 0, images: 0 }); return; }
                    s.d += Math.hypot(e.x - s.x, e.y - s.y); s.x = e.x; s.y = e.y; s.images++;
                });
            }
            if (i >= 200 && i % 20 === 0) {
                L.B.entites.forEach(function (v) {
                    if (v.type !== 'vehicule' || v.conducteur !== 'trafic') return;
                    // ⚠️ Un velo parti sur le trottoir ou au parc (`horsRue`) y est de son
                    // plein gre : ce n'est pas un char qui coupe un coin (`test_velos_js`).
                    if (v.horsRue) return;
                    releves++;
                    const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
                    if (!L.Monde.estRoute(tx, ty)) horsRoute++;
                    const avant = caps.get(v.id);
                    if (avant !== undefined && v.sens !== avant) tournes++;
                    caps.set(v.id, v.sens);
                });
            }
            if (i >= 300 && i % 30 === 0) {
                L.B.entites.forEach(function (e) {
                    if (e.type !== 'pieton' || !e.vivant || e.recul > 0) return;
                    // Le marchand du camion-restaurant tient son comptoir sur un
                    // stationnement : il n'y marche pas, il y est pose par la carte.
                    if (e.commerce) return;
                    const tx = Math.floor(e.x / L.TT), ty = Math.floor(e.y / L.TT);
                    relevesPietons++;
                    if (L.Monde.estChaussee(tx, ty)) surLaChaussee++;
                    if (L.Monde.estPassage(tx, ty)) surUnPassage++;
                });
            }
        }
        const chars = L.B.entites.filter(function (e) { return e.type === 'vehicule'; });
        let dansUnMur = 0, horsRouteFin = 0;
        chars.forEach(function (v) {
            const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
            if (L.Monde.solidite(tx, ty) === 1) dansUnMur++;
            if (v.conducteur === 'trafic' && !L.Monde.estRoute(tx, ty)) horsRouteFin++;
        });
        const presents = Array.from(suivis.values()).filter(function (s) { return s.images >= 300; });
        const distances = presents.map(function (s) { return s.d / s.images * 1800; });   // ramene a 1800 images
        const bouges = distances.filter(function (d) { return d > 300; }).length;
        return { trafic: { roulent: chars.filter(function (v) { return v.conducteur === 'trafic'; }).length,
                           suivis: distances.length, bouges: bouges, dansUnMur: dansUnMur, horsRoute: horsRouteFin,
                           total: chars.length, epaves: chars.filter(function (v) { return v.etat === 'epave'; }).length,
                           ms: L.B.stats.ms },
                 voie: { releves: releves, horsRoute: horsRoute, tournes: tournes },
                 trottoirs: { releves: relevesPietons, chaussee: surLaChaussee, passage: surUnPassage } };
    }""")


def test_le_trafic_roule_3000_images_sans_se_bloquer(la_ville_roule, paquet):
    maximum = paquet["conduite"]["trafic"]["vehicules_max"]
    r = la_ville_roule["trafic"]
    assert r["roulent"] >= 3, "le trafic ne se peuple pas"
    assert r["roulent"] <= maximum
    assert r["dansUnMur"] == 0, "un char est dans un mur"
    assert r["horsRoute"] <= 1, f"{r['horsRoute']} chars du trafic hors de la route"
    assert r["epaves"] == 0, "le trafic s'entretue tout seul"
    assert r["suivis"] >= 3 and r["bouges"] >= r["suivis"] * 0.6, \
        f"{r['bouges']}/{r['suivis']} chars ont roule : le trafic se bloque"


def test_les_feux_alternent_et_les_t_n_en_ont_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const inters = L.Monde.carte.intersections;
        const croix = inters.find(function (i) { return i.bras.length === 4; });
        const te = inters.find(function (i) { return i.bras.length === 3; });
        const cycle = 2 * (L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images);
        const releves = [];
        for (let t = 0; t < cycle; t += 30) {
            L.B.t = t - croix.decalage;
            releves.push([L.Monde.feuVert(croix, '^'), L.Monde.feuVert(croix, '>')]);
        }
        const deuxVerts = releves.filter(function (r) { return r[0] && r[1]; }).length;
        const nsVert = releves.filter(function (r) { return r[0]; }).length;
        const eoVert = releves.filter(function (r) { return r[1]; }).length;
        return { deuxVerts: deuxVerts, nsVert: nsVert, eoVert: eoVert, total: releves.length,
                 teVert: L.Monde.feuVert(te, '^') && L.Monde.feuVert(te, '>') };
    }""")
    assert r["deuxVerts"] == 0, "les deux sens ont ete verts en meme temps"
    assert r["nsVert"] > 0 and r["eoVert"] > 0
    assert abs(r["nsVert"] - r["eoVert"]) <= 1, "un sens est favorise"
    assert r["teVert"] is True, "un T n'a pas de feu : on y passe a vue"


def test_les_pietons_restent_sur_les_trottoirs(la_ville_roule):
    """⚠️ La regle de la ville : on ne pose pas le pied sur la chaussee. Le
    passage pieton est la seule exception — et un pieton pousse sur la rue
    par un char regagne le trottoir."""
    r = la_ville_roule["trottoirs"]
    assert r["releves"] > 200
    assert r["chaussee"] <= r["releves"] * 0.03, \
        f"{r['chaussee']} releves de pietons sur la chaussee (sur {r['releves']})"
    assert r["passage"] > 0, "personne ne traverse jamais"


def test_le_trafic_reste_dans_sa_voie(la_ville_roule):
    """Sur des rails : un char du trafic ne coupe plus un coin, jamais."""
    r = la_ville_roule["voie"]
    assert r["releves"] > 300
    # 1 % : un char pousse d'une demi-tuile par un voisin a un coin, le temps
    # de regagner sa voie. Au-dela, c'est le trafic qui coupe les coins.
    assert r["horsRoute"] <= r["releves"] * 0.01, f"{r['horsRoute']} releves de trafic hors de la route"
    assert r["tournes"] > 3, "le trafic ne tourne jamais"


@pytest.fixture(scope="module")
def deports(banc):
    """⚠️ **TROIS SCÈNES DE DÉPORT, UN BANC** (vague C, 28 sept. 2026). Aucune ne
    joue d'image : un char, un piéton figé, `majConducteur` à la main. Chacune
    repart de ce que son juge avait au départ — SA graine (61, 62, 63), la rue vidée
    de ses chars — et retire ce qu'elle a posé en partant."""
    return banc("""function (L, o) {
        L.Jeu.commencer();
        const T = L.TT;
        function scene(graine, deuxVoiesParSens) {
            L.graine(graine);
            const b = o.boulevard(deuxVoiesParSens);
            if (!b) return null;
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
            const y0 = b.y;
            const v = L.Vehicules.creer('auto', b.x, y0, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
            v.vitesse = 1.2;
            // Un passant fige au milieu de la chaussee, cinq tuiles devant.
            const p = L.Entites.creerPieton(b.x + 5 * T, y0, null);
            p.etat = 'fige';
            return { b: b, y0: y0, v: v, p: p };
        }
        function ranger(s, autres) {
            [s.v, s.p].concat(autres || []).forEach(function (e) { L.Entites.retirer(e); });
            L.Entites.indexer();
        }
        const out = {};

        // test_un_char_se_deporte_pour_contourner_un_pieton
        (function () {
            const s = scene(61, true);
            if (!s) { out.contourne = { trouve: false }; return; }
            const v = s.v, p = s.p, y0 = s.y0;
            let yMin = y0, depasse = false, renverse = false, voie = null;
            for (let i = 0; i < 400; i++) {
                L.Entites.indexer();
                L.Vehicules.majConducteur(v);
                v.x += v.vx; v.y += v.vy;
                yMin = Math.min(yMin, v.y);
                if (!p.vivant) renverse = true;
                if (depasse) continue;
                if (v.x > p.x + 24) {
                    depasse = true;
                    voie = L.Monde.fleche(Math.floor(v.x / T), Math.floor(v.y / T));   // ou roule-t-il en doublant ?
                }
            }
            out.contourne = { trouve: true, depasse: depasse, deports: v.deports || 0, renverse: renverse,
                              gauche: Math.round(y0 - yMin), voie: voie };
            ranger(s);
        })();

        // test_sur_une_rue_a_deux_voies_le_char_attend
        (function () {
            const s = scene(62, false);
            if (!s) { out.deuxVoies = { trouve: false }; return; }
            const v = s.v, p = s.p, y0 = s.y0;
            let ecart = 0;
            for (let i = 0; i < 180; i++) {
                L.Entites.indexer();
                L.Vehicules.majConducteur(v);
                v.x += v.vx; v.y += v.vy;
                ecart = Math.max(ecart, Math.abs(v.y - y0));
            }
            out.deuxVoies = { trouve: true, deports: v.deports || 0, ecart: Math.round(ecart),
                              arrete: Math.abs(v.vx) + Math.abs(v.vy) < 0.05, avant: v.x < p.x };
            ranger(s);
        })();

        // test_on_ne_se_deporte_pas_dans_une_voie_occupee
        (function () {
            const s = scene(63, true);
            if (!s) { out.occupee = { trouve: false }; return; }
            const v = s.v, p = s.p, y0 = s.y0, b = s.b;
            // Un char arrete dans la voie de gauche, juste a cote du pieton.
            const mur = L.Vehicules.creer('auto', b.x + 5 * T, y0 - T, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
            mur.vitesse = 0;
            let ecart = 0;
            for (let i = 0; i < 180; i++) {
                L.Entites.indexer();
                L.Vehicules.majConducteur(v);
                v.x += v.vx; v.y += v.vy;
                ecart = Math.max(ecart, Math.abs(v.y - y0));
            }
            out.occupee = { trouve: true, deports: v.deports || 0, ecart: Math.round(ecart), avant: v.x < p.x };
            ranger(s, [mur]);
        })();
        return out;
    }""")


def test_un_char_se_deporte_pour_contourner_un_pieton(deports):
    """Sur un boulevard, un pieton plante au milieu de la voie ne bloque plus :
    le char se tasse dans la voie d'a cote — par la gauche — et repart."""
    r = deports["contourne"]
    assert r["trouve"], "aucun boulevard a deux voies dans le meme sens sur la carte"
    assert r["deports"] >= 1, "le char n'a jamais essaye de se tasser"
    assert r["gauche"] >= 10, f"il s'est tasse de {r['gauche']} px : ce n'est pas la voie de gauche"
    assert r["depasse"], "le char n'a jamais depasse le pieton"
    assert r["renverse"] is False, "⚠️ on contourne le pieton, on ne le fauche pas"
    assert r["voie"] == ">", "en doublant, le char n'etait pas dans une voie de son sens"


def test_sur_une_rue_a_deux_voies_le_char_attend(deports):
    """⚠️ Le pendant du test precedent : sans voie parallele dans son sens, se
    deporter serait rouler a contresens. Le char attend, comme avant."""
    r = deports["deuxVoies"]
    assert r["trouve"], "aucune rue a une seule voie par sens sur la carte"
    assert r["deports"] == 0, "le char s'est deporte a contresens"
    assert r["ecart"] <= 4, f"il a quitte sa voie de {r['ecart']} px"
    assert r["arrete"] and r["avant"], "le char n'a pas attendu derriere le pieton"


def test_on_ne_se_deporte_pas_dans_une_voie_occupee(deports):
    """La voie d'a cote n'est libre que si personne n'y roule — devant COMME
    derriere. Un char qui arrive vite par la gauche a la priorite ; celui qui
    est coince reste derriere son pieton plutot que de lui couper la route."""
    r = deports["occupee"]
    assert r["trouve"], "aucun boulevard a deux voies dans le meme sens sur la carte"
    assert r["deports"] == 0, "le char s'est tasse dans une voie occupee"
    assert r["ecart"] <= 4, f"il a quitte sa voie de {r['ecart']} px"
    assert r["avant"], "le char a traverse le pieton au lieu d'attendre"


def test_les_feux_et_les_stops_sont_poses(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        const feux = L.B.entites.filter(function (e) { return e.type === 'feu'; });
        const stops = L.B.entites.filter(function (e) { return e.type === 'stop'; });
        const croix = c.intersections.filter(function (i) { return i.feux; }).length;
        const tes = c.intersections.filter(function (i) { return i.stop; }).length;
        const bienPlaces = feux.concat(stops).filter(function (e) {
            return L.Monde.solidite(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT)) === 0 && !L.Monde.estRoute(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT));
        }).length;
        // Un T dont le bras ouest manque : la tige est a l'est, on y arrive en roulant vers l'ouest.
        const sansOuest = c.intersections.find(function (i) { return i.bras.length === 3 && i.bras.indexOf('O') < 0; });
        return { feux: feux.length, croix: croix, stops: stops.length, tes: tes,
                 bienPlaces: bienPlaces, stopSansOuest: sansOuest ? sansOuest.stop : null };
    }""")
    # ⚠️ QUATRE, un par coin : un tricolore ne montre qu'une rue, il en faut
    # donc un en face de chaque approche. A deux, il manquait un feu a deux
    # coins sur quatre.
    assert r["feux"] == r["croix"] * 4 > 0
    assert r["stops"] == r["tes"] > 0
    assert r["bienPlaces"] == r["feux"] + r["stops"], "un feu ou un stop est sur la route ou dans un mur"
    assert r["stopSansOuest"] == "<", "le STOP est pour ceux qui arrivent par la tige"


# ⚠️ Le gabarit du mat se LIT dans `DECORS.feu`, il ne se recopie pas ici — et
# le miroir avec. Un mat dont le bras part vers l'ouest peint tout a l'envers ;
# un juge qui chercherait la lentille a sa place « de droite » ne verrait rien
# et dirait « le feu est eteint » alors qu'il brille.
GABARIT_JS = """
        const F = L.DECORS.feu;
        function miroir(x, l, bras) { return bras > 0 ? x : F.w - x - l; }
        function ancre(e) { return e.bras > 0 ? F.ancre : F.ancreMiroir; }
        function coin(e, cx, cy) {                       // le coin haut-gauche du sprite
            return [Math.round(e.x - ancre(e)[0] - cx), Math.round(e.y - ancre(e)[1] - cy)];
        }
        function lentilleDe(e, rang) {                   // le coin de la lentille du rang
            return miroir(F.lentilles[rang], F.lentilleCote, e.bras);
        }
        function boiteDesTetes(e) {                      // [bord gauche, largeur] du boitier pieton
            const large = e.traverses.length > 1 ? F.boitier.l : 7;
            return [miroir(F.tete.x, large, e.bras), large];
        }
        function teteDe(e, i) {                          // le coin de la i-e ampoule pieton
            const [bord, large] = boiteDesTetes(e), deux = e.traverses.length > 1;
            const cote = deux ? 3 : 4;
            return [deux ? (i === 0 ? bord + 1 : bord + large - 1 - cote) : bord + ((large - cote) >> 1), cote];
        }
"""


def test_une_ampoule_allumee_pose_une_lampe_de_la_couleur_de_sa_phase(banc):
    """⚠️ Un feu ÉTAIT de la peinture. `Base.fin` compose la nuit en
    **multipliant** toute l'image par la teinte de l'heure, puis rajoute les
    lampes en `lighter` par-dessus ; un feu n'avait aucune lampe, il ne
    recevait donc que la multiplication — comme une brique. À minuit, le vert
    (46, 204, 113) tombait à (16, 76, 57).

    La lentille allumée pose maintenant sa lampe, **de la couleur de sa
    phase** — et elle seule, puisqu'un tricolore n'en allume qu'une. Et **rien
    du tout en plein jour**.
    """
    r = banc("""function (L, o) {""" + GABARIT_JS + """
        L.Jeu.commencer();
        const inter = L.Monde.carte.intersections.find(function (i) { return i.feux; });
        const feu = L.B.entites.find(function (e) { return e.type === 'feu' && e.inter === inter; });
        const t = L.B.defs.conduite.trafic;
        const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
        const sens = feu.axe === 'ns' ? '^' : '>';
        L.B.joueur.x = feu.x; L.B.joueur.y = feu.y;
        const RANG = { rouge: 0, jaune: 1, vert: 2 };
        // La lampe de la lentille des CHARS, retrouvee a sa place a l'ecran :
        // le mat en porte d'autres (les tetes pieton) et les trois autres coins
        // aussi, et un juge qui lirait « il y a du vert quelque part »
        // passerait au vert du coin d'en face.
        function releve(heure, phase) {
            L.B.partie.heure = heure;
            L.B.t = ((phase - inter.decalage) % cycle + cycle) % cycle;
            L.Monde.centrerCamera(feu.x, feu.y);
            o.frame(1);
            const cx = Math.round(L.B.cam.x), cy = Math.round(L.B.cam.y);
            const [x, y] = coin(feu, cx, cy);
            const couleur = L.Monde.feuDeCirculation(inter, sens);
            const lx = x + lentilleDe(feu, RANG[couleur]) + 1.5, ly = y + F.lentilleY + 1.5;
            const lampes = L.Vehicules.lampesDesFeux();
            const l = lampes.find(function (q) { return q.x === lx && q.y === ly; });
            // ⚠️ « Ailleurs » veut dire DANS CE BOITIER-CI, pas n'importe ou sur
            // la rangee : les quatre mats d'un croisement sont a la meme
            // hauteur d'ecran, et le juge accusait le feu d'en face.
            return { total: lampes.length, couleur: couleur, c: l ? l.c : null,
                     ailleurs: lampes.filter(function (q) {
                         return q.y === ly && q.x !== lx && q.x >= x && q.x < x + F.w;
                     }).length };
        }
        const milieuVert = Math.floor(t.feu_vert_images / 2);
        // ⚠️ **PAS MINUIT** (15 sept. 2026) : a minuit, les feux CLIGNOTENT
        // maintenant, et un clignotant n'a pas de cycle a viser. Ce qu'il faut
        // ici, c'est l'heure ou il fait assez sombre pour que les lampes
        // s'allument ET ou le tricolore tourne encore — juste avant que la
        // ville bascule (`trafic.clignotant_depuis`).
        const nuit = t.clignotant_depuis - 0.02;
        return { vert: releve(nuit, milieuVert),
                 rouge: releve(nuit, cycle / 2 + milieuVert),
                 jaune: releve(nuit, t.feu_vert_images + Math.floor(t.feu_orange_images / 2)),
                 midi: releve(0.5, milieuVert) };
    }""")
    couleurs = {}
    for nom in ("vert", "rouge", "jaune"):
        x = r[nom]
        assert x["couleur"] == nom, f"la phase visee n'est pas la bonne : {x}"
        assert x["c"], f"la lentille {nom} n'eclaire pas la nuit : {x}"
        assert x["ailleurs"] == 0, \
            f"une autre lentille du meme boitier eclaire aussi : un tricolore n'en allume qu'une ({x})"
        couleurs[nom] = x["c"]
    assert len(set(couleurs.values())) == 3, f"deux phases jettent la meme lumiere : {couleurs}"
    assert r["midi"]["total"] == 0 and r["midi"]["c"] is None, \
        f"un feu qui eclaire en plein soleil : {r['midi']}"


def test_l_orange_qui_clignote_n_eclaire_pas_pendant_qu_il_est_eteint(banc):
    """Le dégagement du feu piéton **clignote** : un orange fixe se lit
    « attends », un orange qui bat se lit « finis, mais ne pars plus ».

    ⚠️ Sa lampe doit battre AVEC lui. Un halo qui reste allumé pendant que
    l'ampoule est éteinte, c'est un clignotant qui ne clignote plus — on le
    verrait battre à l'œil et briller en continu sur le trottoir.
    """
    r = banc("""function (L, o) {""" + GABARIT_JS + """
        L.Jeu.commencer();
        const t = L.B.defs.conduite.trafic;
        const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
        const mat = L.B.entites.find(function (e) { return e.type === 'feu' && e.traverses.length; });
        const inter = mat.inter, sens = mat.traverses[0] === '=' ? '>' : '^';
        L.B.joueur.x = mat.x; L.B.joueur.y = mat.y;
        // ⚠️ Pas minuit : les feux y clignotent depuis le 15 sept. 2026, et un
        // feu pieton s'eteint avec eux. On se met juste avant la bascule.
        L.B.partie.heure = t.clignotant_depuis - 0.02;
        // Deux images du MEME degagement (il dure 120 images), de parite
        // contraire au clignotant (il bat aux 8).
        const cibles = [];
        for (let phase = 1; phase < cycle && cibles.length < 2; phase++) {
            L.B.t = phase;
            if (L.Monde.feuPieton(inter, sens) !== 'degage') continue;
            const eteint = (phase >> 3) % 2 === 0;
            if (!cibles.some(function (c) { return c.eteint === eteint; })) cibles.push({ phase: phase, eteint: eteint });
        }
        return cibles.map(function (c) {
            L.B.t = c.phase - 1;                       // `o.frame` avance l'horloge d'une image
            L.Monde.centrerCamera(mat.x, mat.y);
            o.frame(1);
            const cx = Math.round(L.B.cam.x), cy = Math.round(L.B.cam.y);
            const [x, y] = coin(mat, cx, cy);
            const [col, cote] = teteDe(mat, 0);
            const l = L.Vehicules.lampesDesFeux().find(function (q) {
                return q.x === x + col + cote / 2 && q.y === y + F.tete.y + 3.5;
            });
            return { eteint: c.eteint, vise: c.phase, t: L.B.t,
                     etat: L.Monde.feuPieton(inter, sens), lampe: l ? l.c : null };
        });
    }""")
    assert len(r) == 2 and {x["eteint"] for x in r} == {True, False}, \
        f"le clignotant n'a pas ete pris des deux cotes : {r}"
    for x in r:
        assert x["t"] == x["vise"], f"l'horloge a derive : visee {x['vise']}, arrivee {x['t']}"
        assert x["etat"] == "degage", f"on a quitte le degagement : {x}"
    eteint = next(x for x in r if x["eteint"])
    allume = next(x for x in r if not x["eteint"])
    assert eteint["lampe"] is None, "l'ampoule est eteinte et le trottoir reste eclaire"
    assert allume["lampe"], "l'ampoule est allumee et n'eclaire rien"


def test_un_tricolore_n_allume_qu_une_lentille_a_la_fois(banc):
    """⚠️ **LE JUGE QUI MANQUAIT**, et il a servi deux fois. Les feux ont
    d'abord été **muets** du jour où on les a posés (l'entité portait
    `decor: 'feu'`, et `Entites.dessiner` teste `if (e.decor)` **avant**
    `if (e.type === 'feu')` : la branche générique peignait le boîtier cuit et
    s'en allait) ; rien ne le disait, parce que **tous les juges des feux
    parlaient de l'horloge** et aucun du **dessin**.

    Il tient maintenant la promesse d'un tricolore : à chaque instant du
    cycle, **une seule lentille allumée**, à la colonne de sa couleur, et de
    **sa forme** — le rouge carré, le jaune en losange, le vert rond, comme un
    vrai feu québécois. On mesure les rectangles peints, en plein jour, là où
    aucune lampe ne vient aider.
    """
    r = banc("""function (L, o) {""" + GABARIT_JS + """
        L.Jeu.commencer();
        const inter = L.Monde.carte.intersections.find(function (i) { return i.feux; });
        const feu = L.B.entites.find(function (e) { return e.type === 'feu' && e.inter === inter; });
        const t = L.B.defs.conduite.trafic;
        const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
        L.B.joueur.x = feu.x; L.B.joueur.y = feu.y;
        L.B.partie.heure = 0.5;                                   // plein midi : aucune lampe
        const sens = feu.axe === 'ns' ? '^' : '>';
        const releves = [];
        for (const phase of [0, t.feu_vert_images - 5, t.feu_vert_images + 5, cycle / 2 + 5,
                             cycle / 2 + t.feu_vert_images + 5]) {
            L.B.t = ((phase - inter.decalage) % cycle + cycle) % cycle - 1;
            L.Monde.centrerCamera(feu.x, feu.y);
            const c = L.Base.debut();
            c.traces = [];
            o.frame(1);
            const traces = c.traces; c.traces = null;
            const cx = Math.round(L.B.cam.x), cy = Math.round(L.B.cam.y);
            const [x, y] = coin(feu, cx, cy);
            // Tout ce qui a ete peint DANS le boitier des chars : le reste du
            // mat est cuit dans la fiche, donc un rectangle ici est forcement
            // une lentille vive.
            const dans = traces.filter(function (q) {
                return q[0] >= x && q[0] < x + F.w
                    && q[1] >= y + F.lentilleY && q[1] < y + F.lentilleY + F.lentilleCote;
            });
            // A quelle lentille (rang 0, 1, 2) chaque pixel peint touche-t-il ?
            const rangs = {};
            for (const q of dans) {
                for (let px = q[0]; px < q[0] + q[2]; px++) {
                    for (let rang = 0; rang < 3; rang++) {
                        const c0 = x + lentilleDe(feu, rang);
                        if (px >= c0 && px < c0 + F.lentilleCote) rangs[rang] = true;
                    }
                }
            }
            releves.push({ couleur: L.Monde.feuDeCirculation(inter, sens),
                           vert: L.Monde.feuVert(inter, sens),
                           rangs: Object.keys(rangs).map(Number).sort(),
                           pleins: dans.filter(function (q) { return q[2] === 3 && q[3] === 3; }).length,
                           barres: dans.filter(function (q) { return q[2] === 1 && q[3] === 3; }).length,
                           coins: dans.filter(function (q) { return q[2] === 1 && q[3] === 1; }).length });
        }
        return releves;
    }""")
    rang = {"rouge": 0, "jaune": 1, "vert": 2}
    vus = set()
    for x in r:
        vus.add(x["couleur"])
        assert x["rangs"] == [rang[x["couleur"]]], \
            f"feu {x['couleur']} : lentilles allumees aux rangs {x['rangs']}, il en faut UNE, la {rang[x['couleur']]}e"
        assert x["vert"] == (x["couleur"] == "vert"), \
            "ce que le feu MONTRE et ce que le char RESPECTE ne disent pas la meme chose"
        # La forme : le carre est plein, le losange est une croix (une barre
        # verticale + une horizontale), le cercle est un plein aux coins adoucis.
        if x["couleur"] == "rouge":
            assert x["pleins"] == 1 and x["barres"] == 0, f"le rouge n'est pas un carre plein : {x}"
            assert x["coins"] == 1, f"le rouge n'a que son coeur comme pixel isole : {x}"
        elif x["couleur"] == "jaune":
            assert x["pleins"] == 0 and x["barres"] == 1, f"le jaune n'est pas un losange : {x}"
        else:
            assert x["pleins"] == 1 and x["coins"] == 5, \
                f"le vert n'est pas un cercle (un plein + quatre coins adoucis + le coeur) : {x}"
    assert vus == {"rouge", "jaune", "vert"}, f"le cycle n'a pas montre les trois couleurs : {vus}"


def test_de_chaque_approche_un_feu_de_son_axe_est_en_face(banc):
    """Un tricolore ne montre **qu'une rue** — c'est ce qu'est un tricolore.
    Il faut donc qu'en arrivant à un croisement, un feu de **son** axe soit
    dans le champ, sinon on ne sait pas si c'est à soi de passer.

    ⚠️ Ça tient à une diagonale : nord-est et sud-ouest portent le nord-sud,
    nord-ouest et sud-est l'est-ouest. Qui arrive du sud a les deux coins nord
    devant lui, donc un de chaque diagonale, donc un « ns ». Le juge le
    vérifie **pour les quatre approches, à tous les croisements de la ville**
    — c'est la propriété qui justifie l'assignation, pas le goût.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const TT = L.TT;
        const manque = [], sansAxe = [];
        const feux = L.B.entites.filter(function (e) { return e.type === 'feu'; });
        const parInter = new Map();
        for (const e of feux) {
            if (!e.axe) sansAxe.push(e.id);
            if (!parInter.has(e.inter)) parInter.set(e.inter, []);
            parInter.get(e.inter).push(e);
        }
        for (const [inter, mats] of parInter) {
            const haut = inter.y * TT, bas = (inter.y + inter.h) * TT;
            const gauche = inter.x * TT, droite = (inter.x + inter.l) * TT;
            // Les deux coins « en face » de chaque approche, et l'axe qu'il faut y voir.
            const approches = [['^', 'ns', function (e) { return e.y < haut; }],
                               ['v', 'ns', function (e) { return e.y > bas; }],
                               ['>', 'eo', function (e) { return e.x > droite; }],
                               ['<', 'eo', function (e) { return e.x < gauche; }]];
            for (const [sens, axe, enFace] of approches) {
                if (!mats.some(function (e) { return enFace(e) && e.axe === axe; }))
                    manque.push(inter.i + ':' + sens);
            }
        }
        return { feux: feux.length, sansAxe: sansAxe.length, manque: manque.length,
                 exemples: manque.slice(0, 5),
                 axes: { ns: feux.filter(function (e) { return e.axe === 'ns'; }).length,
                         eo: feux.filter(function (e) { return e.axe === 'eo'; }).length } };
    }""")
    assert r["sansAxe"] == 0, f"{r['sansAxe']} mats sans axe : ils ne savent pas quelle rue ils montrent"
    assert r["manque"] == 0, \
        f"{r['manque']} approches sans feu de leur axe en face (ex. {r['exemples']})"
    assert r["axes"]["ns"] == r["axes"]["eo"] == r["feux"] // 2, \
        f"les deux axes ne se partagent pas les mats : {r['axes']}"


def test_un_char_respecte_le_feu_qu_on_lui_montre_sauf_la_sirene(banc):
    """« Les véhicules le respectent, sauf exception. » Le char du trafic lit
    **`Monde.feuVert`**, qui découle de **`feuDeCirculation`**, qui est ce que
    le mât **peint** : une seule phrase, lue deux fois.

    ⚠️ Et le **jaune n'est pas vert** : un char qui arrive à la ligne d'arrêt
    sur le jaune s'arrête. Sans ça, le dégagement du feu piéton ne servirait à
    rien — le croisement ne se viderait jamais.

    ⚠️ **L'exception, c'est la sirène** : en poursuite, on brûle le feu, le
    STOP et la boîte. Une auto-patrouille qui attend au rouge pendant que le
    joueur s'enfuit n'est pas une poursuite.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, t = L.B.defs.conduite.trafic;
        const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
        // Une ligne d'arret ('S') qui donne sur un croisement a feux.
        let arret = null;
        for (const k in c.arrets) {
            const [tx, ty] = k.split(',').map(Number), sens = c.arrets[k];
            const p = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] }[sens];
            const inter = L.Monde.intersectionA(tx + p[0], ty + p[1]);
            if (inter && inter.feux) { arret = { tx: tx, ty: ty, sens: sens, inter: inter }; break; }
        }
        const angle = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 }[arret.sens];
        function essai(couleurVoulue, sirene) {
            // On se cale sur la phase voulue, puis on pose un char sur la ligne d'arret.
            let phase = 0;
            for (; phase < cycle; phase++) {
                L.B.t = phase;
                if (L.Monde.feuDeCirculation(arret.inter, arret.sens) === couleurVoulue) break;
            }
            const v = L.Vehicules.creer('auto', arret.tx * L.TT + 8, arret.ty * L.TT + 8, angle,
                                        { conducteur: 'trafic', etat: 'roule', sens: arret.sens,
                                          poursuite: sirene || undefined });
            const depart = { x: v.x, y: v.y };
            for (let i = 0; i < 90; i++) { L.B.t = phase; o.frame(1); }   // l'horloge du feu FIGEE
            const avance = Math.hypot(v.x - depart.x, v.y - depart.y);
            const dedans = !!L.Monde.intersectionA(Math.floor(v.x / L.TT), Math.floor(v.y / L.TT));
            L.Entites.retirer(v);
            return { couleur: L.Monde.feuDeCirculation(arret.inter, arret.sens),
                     vert: L.Monde.feuVert(arret.inter, arret.sens),
                     avance: Math.round(avance), dedans: dedans };
        }
        return { rouge: essai('rouge', false), jaune: essai('jaune', false),
                 vert: essai('vert', false), sirene: essai('rouge', true) };
    }""")
    assert r["rouge"]["couleur"] == "rouge" and r["rouge"]["vert"] is False
    assert r["rouge"]["avance"] <= 8, f"un char a franchi le rouge : {r['rouge']['avance']} px"
    assert r["jaune"]["couleur"] == "jaune" and r["jaune"]["vert"] is False, \
        "le jaune compte comme vert : le croisement ne se viderait jamais"
    assert r["jaune"]["avance"] <= 8, f"un char est parti sur le jaune : {r['jaune']['avance']} px"
    assert r["vert"]["avance"] > 16, f"un char est reste plante au vert : {r['vert']['avance']} px"
    assert r["sirene"]["avance"] > 16, \
        f"une sirene a attendu au rouge : {r['sirene']['avance']} px — l'exception n'en est plus une"


def test_un_char_s_arrete_au_stop_puis_repart(banc, paquet):
    arret = paquet["conduite"]["trafic"]["arret_images"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(53);
        const c = L.Monde.carte;
        // Un T dont la tige arrive par l'est (sens '<') : on cherche sa ligne d'arret.
        const inter = c.intersections.find(function (i) { return i.stop === '<'; });
        let sx = -1, sy = -1;
        for (const cle in c.arrets) {
            const xy = cle.split(',').map(Number);
            if (c.arrets[cle] !== '<') continue;
            if (L.Monde.intersectionA(xy[0] - 1, xy[1]) === inter) { sx = xy[0]; sy = xy[1]; break; }
        }
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const v = L.Vehicules.creer('auto', sx * L.TT + 8 + 40, sy * L.TT + 8, Math.PI, { conducteur: 'trafic', etat: 'roule', sens: '<' });
        v.vitesse = 1.5;
        let immobile = 0, arrive = false, reparti = false;
        for (let i = 0; i < 600; i++) {
            L.Entites.indexer(); L.Vehicules.majConducteur(v); v.x += v.vx; v.y += v.vy;
            const tx = Math.floor(v.x / L.TT);
            if (tx === sx && Math.abs(v.vx) + Math.abs(v.vy) < 0.01) { immobile++; arrive = true; }
            if (arrive && tx < sx) { reparti = true; break; }
        }
        return { trouve: sx >= 0, arrive: arrive, immobile: immobile, reparti: reparti };
    }""")
    assert r["trouve"], "aucune ligne d'arret de T trouvee"
    assert r["arrive"] and r["immobile"] >= arret - 2, f"le char ne s'est arrete que {r['immobile']} images au STOP"
    assert r["reparti"], "le char n'est jamais reparti du STOP"


def test_deux_chars_qui_tournent_a_gauche_ne_se_bloquent_pas(banc):
    """⚠️ Le blocage de Martin : deux chars entrent au vert par des bouts
    opposes, tous deux pour tourner a gauche, se retrouvent nez a nez au
    milieu de la boite — et chacun attend l'autre. Un croisement ne doit
    accueillir un char que s'il peut le laisser ressortir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(72);
        const c = L.Monde.carte;
        // Un croisement a feux a quatre voies (rue est-ouest large).
        const inter = c.intersections.find(function (i) { return i.feux && i.l === 4 && i.h === 4; });
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
        // ⚠️ Le joueur regarde de pres : hors de sa bulle, un char est oublie
        // et le test croirait a un blocage.
        const j = L.B.joueur;
        j.x = (inter.x - 1) * L.TT + 8; j.y = (inter.y - 1) * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        // Phase : est-ouest au vert.
        L.B.t = -inter.decalage + L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images + 5;
        const T = L.TT;
        // A arrive de l'ouest sur la voie interieure (rangee y+2), B de l'est sur la voie interieure (rangee y+1).
        const a = L.Vehicules.creer('auto', (inter.x - 6) * T + 8, (inter.y + 2) * T + 8, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        const b = L.Vehicules.creer('auto', (inter.x + inter.l + 5) * T + 8, (inter.y + 1) * T + 8, Math.PI, { conducteur: 'trafic', etat: 'roule', sens: '<' });
        a.vitesse = 1.5; b.vitesse = 1.5;
        a.sortie = ['gauche', 'droit', 'droite']; b.sortie = ['gauche', 'droit', 'droite'];
        const boite = function (v) { return v.x >= inter.x * T && v.x < (inter.x + inter.l) * T && v.y >= inter.y * T && v.y < (inter.y + inter.h) * T; };
        let dansLaBoiteEnsemble = 0, sortis = 0;
        for (let i = 0; i < 2400; i++) {
            // ⚠️ LE JOUEUR NE SE FAIT PAS RENVERSER : il regarde a une tuile de la
            // boite, un des deux chars pouvait le faucher, et il se reveillait a
            // l'hopital — `Monde.carte` devenait la PIECE, `estRoute` repondait non
            // sur de l'asphalte, et le juge accusait le trafic. Mesure le 17 sept.
            // 2026 : 1 graine sur 40 tombait deja ainsi, et l'Ile-aux-Corneilles
            // (quarante decors de plus, donc d'autres numeros d'entite) en changeait
            // seulement laquelle. C'est la parade du juge des amuseurs.
            j.invincible = 60;
            o.frame(1);
            if (boite(a) && boite(b)) dansLaBoiteEnsemble++;
        }
        const aParti = Math.hypot(a.x - (inter.x - 6) * T, a.y - (inter.y + 2) * T) > 8 * T && !boite(a);
        const bParti = Math.hypot(b.x - (inter.x + inter.l + 5) * T, b.y - (inter.y + 1) * T) > 8 * T && !boite(b);
        return { ensemble: dansLaBoiteEnsemble, aParti: aParti, bParti: bParti, aSens: a.sens, bSens: b.sens,
                 aSol: L.Monde.estRoute(Math.floor(a.x / T), Math.floor(a.y / T)),
                 bSol: L.Monde.estRoute(Math.floor(b.x / T), Math.floor(b.y / T)) };
    }""")
    assert r["ensemble"] == 0, f"les deux chars ont partage la boite pendant {r['ensemble']} images"
    assert r["aParti"] and r["bParti"], f"un char est reste coince : {r}"
    assert r["aSol"] and r["bSol"], "un char a fini hors de la route"


def test_les_passages_ont_une_tuile_pleine_et_une_en_bout(banc):
    """⚠️ **Reformule le 15 sept. 2026, le trottoir a une tuile.** Le passage
    faisait deux tuiles — une pleine, une en bout — et le juge tenait cette
    forme. Depuis que la traverse fait la largeur du trottoir, une tuile, il
    n'y a plus de bout : chaque tuile de passage est PLEINE, et le peintre y
    met ses bandes entieres. Une tuile « en bout » qui reapparaitrait serait
    une traverse de deux tuiles revenue par la fenetre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        const compte = { '=': [0, 0, 0], ':': [0, 0, 0] };
        for (let y = 0; y < c.h; y++) for (let x = 0; x < c.w; x++) {
            const g = c.sol[y][x];
            if (g === '=' || g === ':') compte[g][L.Monde.varianteDePassage(g, x, y)]++;
        }
        return compte;
    }""")
    for g in ("=", ":"):
        pleines, ouest, est = r[g]
        assert pleines > 100, f"passage « {g} » : {pleines} tuiles pleines seulement — {r}"
        assert ouest == 0 and est == 0, (
            f"passage « {g} » : {ouest + est} tuiles en bout — une traverse fait plus d'une tuile"
        )


def test_une_case_de_stationnement_se_peint_et_se_gare(banc):
    """Une case fait deux tuiles : le FOND (ligne de nez, butoir) et l'ouverture
    sur l'allee. Le peintre ne le sait pas du generateur, il le LIT dans les
    voisines — et c'est la meme lecture qui met une auto stationnee dans ses
    lignes plutot qu'en travers du terrain."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, NEZ = { '^': [0, -1], 'v': [0, 1], '<': [-1, 0], '>': [1, 0] };
        let fonds = 0, ouvertes = 0, mauvaises = 0;
        const coins = {}, cases = [];
        for (let y = 1; y < c.h - 1; y++) for (let x = 1; x < c.w - 1; x++) {
            const g = c.sol[y][x], nez = NEZ[g];
            if (!nez) continue;
            const v = L.Monde.varianteDeCase(g, x, y);
            const fond = (v & 1) !== 0;
            if (fond !== (c.sol[y + nez[1]][x + nez[0]] !== g)) mauvaises++;
            if (fond) fonds++; else ouvertes++;
            coins[v & 3] = (coins[v & 3] || 0) + 1;
            cases.push([x, y]);
        }
        // ⚠️ Une auto ne se stationne QUE hors de l'ecran, entre 180 et 560 px
        // du joueur : on se plante donc au milieu du coin le plus fourni en
        // cases, sinon on juge un quartier ou il n'y a rien a peupler.
        let mieux = cases[0], n = 0;
        for (let i = 0; i < cases.length; i += 8) {
            const p = cases.filter(function (k) {
                return Math.abs(k[0] - cases[i][0]) < 30 && Math.abs(k[1] - cases[i][1]) < 30;
            }).length;
            if (p > n) { n = p; mieux = cases[i]; }
        }
        L.B.joueur.x = mieux[0] * L.TT; L.B.joueur.y = mieux[1] * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        // ⚠️ ON FORCE LA REGLE, on ne joue pas sa probabilite — c'est la meme
        // lecon que la chute de l'ivrogne. Un char ne se gare que lorsque le
        // trafic ROULANT est au complet (`roulent >= voulu`, `vehicules.js`) :
        // le juge esperait donc qu'en 900 images le quartier finisse par
        // remplir ses rues, ce qui depend de trois tirages de de. Il a tenu
        // jusqu'au jour ou une routine de plus a decale le hasard. On met le
        // trafic voulu a zero : la condition est vraie tout de suite, et on
        // mesure ce qu'on veut mesurer — OU se gare un char, pas QUAND.
        const zone = L.Monde.zoneA(L.B.joueur.x, L.B.joueur.y);
        if (zone) zone.vehicules = 0;
        o.frame(900);
        // ⚠️ **UNE COQUE AMARREE N'EST PAS UNE AUTO GAREE.** Depuis la 3e vague
        // du bord de l'eau, une chaloupe nait `etat: 'stationne'` — dans la
        // BAIE, ce qui est exactement sa place — et ce juge-ci exige que tout
        // vehicule stationne soit dans une case peinte. Il ne s'en apercevait
        // pas tant que le coin le plus fourni en cases tombait loin de l'eau ;
        // le jour ou le port a touche la baie, le coin a bouge et le juge a
        // accuse le stationnement d'un bateau au mouillage. `def.eau` dit la
        // difference, et c'est la fiche qui la porte (`vehicules.py`).
        const gares = L.B.entites.filter(function (e) {
            return e.type === 'vehicule' && e.etat === 'stationne' && !(e.def && e.def.eau); });
        const poses = gares.map(function (v) {
            const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
            const g = c.sol[ty][tx], nez = NEZ[g];
            return {
                case: !!nez,
                angle: !!nez && Math.abs(Math.atan2(nez[1], nez[0]) - v.angle) < 0.01,
                centree: (v.x % L.TT === 8 && v.y % L.TT === 0) || (v.y % L.TT === 8 && v.x % L.TT === 0),
            };
        });
        return { fonds: fonds, ouvertes: ouvertes, mauvaises: mauvaises, coins: coins, poses: poses };
    }""")
    assert r["mauvaises"] == 0, "une tuile de fond mal lue : le butoir se peint du mauvais bord"
    assert r["fonds"] > 0 and r["fonds"] == r["ouvertes"], \
        f"{r['fonds']} fonds pour {r['ouvertes']} ouvertures : une case n'a pas deux tuiles"
    assert set(r["coins"]) == {"0", "1", "2", "3"}, \
        f"le peintre n'a jamais vu les quatre coins d'une rangee : {r['coins']}"
    assert r["poses"], "aucune auto ne s'est stationnee en 900 images"
    for pose in r["poses"]:
        assert pose["case"], "une auto stationnee hors d'une case"
        assert pose["angle"], "une auto stationnee de travers dans sa case"
        assert pose["centree"], "une auto stationnee a cheval sur ses lignes"


def test_un_char_coince_dix_secondes_est_debloque(banc):
    """Quelle qu'en soit la cause (ici : le joueur plante devant, de travers
    dans la boite), un char du trafic qui ne bouge plus repart — par lui-meme
    (la cascade de sorties) ou par le chien de garde. Et un char qui fait du
    SUR-PLACE (il bouge sans avancer : un va-et-vient) se fait mordre aussi :
    la capture de Martin montrait un char jamais immobile, jamais debloque."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(95);
        const c = L.Monde.carte, j = L.B.joueur, T = L.TT;
        const inter = c.intersections.find(function (i) { return i.feux && i.l === 4; });
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
        // Un char de travers au milieu de la boite, sans cible, le joueur colle devant lui.
        const v = L.Vehicules.creer('auto', (inter.x + 1) * T + 12, (inter.y + 1) * T + 10, 0.6, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        v.cible = { x: v.x, y: v.y, tx: inter.x + 1, ty: inter.y + 1 };
        j.x = v.x + Math.cos(0.6) * 24; j.y = v.y + Math.sin(0.6) * 24;
        L.Monde.centrerCamera(j.x, j.y);
        const x0 = v.x, y0 = v.y, angle0 = v.angle;
        let bouge = 0;
        // ⚠️ Le joueur reste en vie ICI AUSSI (la raison est plus bas) : plante
        // devant un char qui repart, il se fait renverser. Le Petit-Canton a
        // deplace la ville (27 sept. 2026) et il en est mort — reveille a
        // l'hopital, la seconde moitie jouait dans une piece, sans un char a
        // surveiller.
        for (let i = 0; i < 1500; i++) {
            j.vie = j.vieMax; j.invincible = 30;
            o.frame(1);
            j.x = v.x + Math.cos(v.angle) * 24; j.y = v.y + Math.sin(v.angle) * 24;   // le joueur reste devant
            if (Math.hypot(v.x - x0, v.y - y0) > 40 && !bouge) bouge = i;
        }
        const droit = Math.abs(Math.sin(2 * v.angle)) < 0.2;
        // Le sur-place : un char qu'on ramene chaque image a son point de depart.
        const w = L.Vehicules.creer('auto', (inter.x + 1) * T + 8, (inter.y + 1) * T + 8, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        const wx = w.x, wy = w.y;
        let mordu = -1;
        // ⚠️ Le joueur reste colle au char et en vie A CHAQUE IMAGE. Deux
        // raisons, et la seconde a deja fait passer ce test pour un bogue du
        // chien de garde : la bulle d'oubli retire un char loin du joueur, et un
        // joueur plante vingt secondes au milieu d'un croisement finit par se
        // faire renverser — l'hopital l'emmene a l'autre bout de la ville, le
        // char est oublie, et plus personne ne surveille rien.
        for (let i = 0; i < 1400 && mordu < 0; i++) {
            j.x = wx; j.y = wy + 40; j.vie = j.vieMax; j.invincible = 30;
            L.Monde.centrerCamera(j.x, j.y);
            o.frame(1);
            if (w.debloques) mordu = i; else { w.x = wx; w.y = wy; }
        }
        const dedans = L.B.interieur ? L.B.interieur.slug : null;
        return { bouge: bouge, debloques: v.debloques || 0, droit: droit, angle0: angle0, dedans: dedans,
                 surRoute: L.Monde.estRoute(Math.floor(v.x / T), Math.floor(v.y / T)), mordu: mordu };
    }""")
    assert r["dedans"] is None, "le joueur a fini dans une piece : dehors, plus rien ne roule"
    assert 0 < r["bouge"] < 700, "le char n'est jamais reparti (seul, ou par le chien de garde a 600 images)"
    assert 600 <= r["mordu"] < 1300, "un char qui bouge sans avancer doit se faire mordre par le chien de garde"
    assert r["surRoute"], "le char debloque a fini hors de la route"


def test_un_char_sort_de_chaque_t_par_la_tige_sans_tourner_en_rond(banc):
    """Martin : « ils tournent en rond dans l'intersection ». Par la tige d'un
    T, la sortie prevue est souvent impossible depuis la rangee ou l'on entre :
    le char doit quand meme sortir, par n'importe quel bras, sans repasser
    par la boite."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(97);
        const c = L.Monde.carte, j = L.B.joueur, T = L.TT;
        const tes = c.intersections.filter(function (i) { return i.stop; });
        const resultats = [];
        tes.forEach(function (inter, k) {
            if (k % 3) return;                        // un T sur trois : assez pour couvrir les quatre tiges
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
            j.x = (inter.x - 1) * T + 8; j.y = (inter.y - 1) * T + 8;
            L.Monde.centrerCamera(j.x, j.y);
            // La ligne d'arret de la tige : la tuile 'S' dont le sens est celui du stop.
            let sx = -1, sy = -1;
            for (const cle in c.arrets) {
                if (c.arrets[cle] !== inter.stop) continue;
                const xy = cle.split(',').map(Number);
                const p = { '<': [-1, 0], '>': [1, 0], '^': [0, -1], 'v': [0, 1] }[inter.stop];
                if (L.Monde.intersectionA(xy[0] + p[0], xy[1] + p[1]) === inter) { sx = xy[0]; sy = xy[1]; break; }
            }
            if (sx < 0) { resultats.push({ inter: k, stop: inter.stop, erreur: 'pas de ligne d arret' }); return; }
            const p = { '<': [-1, 0], '>': [1, 0], '^': [0, -1], 'v': [0, 1] }[inter.stop];
            const v = L.Vehicules.creer('auto', (sx - p[0] * 2) * T + 8, (sy - p[1] * 2) * T + 8, Math.atan2(p[1], p[0]), { conducteur: 'trafic', etat: 'roule', sens: inter.stop });
            v.sortie = ['droit', 'gauche', 'droite'];   // tout droit : impossible, c'est la tige
            let entre = false, sorti = false, boucles = 0, derniere = null;
            const vus = new Set();
            for (let i = 0; i < 1500 && !sorti; i++) {
                o.frame(1);
                const tx = Math.floor(v.x / T), ty = Math.floor(v.y / T);
                const cle = tx + ',' + ty;
                const dedans = tx >= inter.x - 2 && tx < inter.x + inter.l + 2 && ty >= inter.y - 2 && ty < inter.y + inter.h + 2;
                if (dedans) {
                    entre = true;
                    // Une boucle, c'est REVENIR sur une tuile deja quittee — pas y rester.
                    if (cle !== derniere) { if (vus.has(cle)) boucles++; vus.add(cle); derniere = cle; }
                }
                else if (entre && L.Monde.fleche(tx, ty) !== '.' && L.Monde.fleche(tx, ty) !== '+') sorti = true;
            }
            resultats.push({ inter: k, stop: inter.stop, entre: entre, sorti: sorti, boucles: boucles, sens: v.sens, debloques: v.debloques || 0 });
        });
        return resultats;
    }""")
    assert r, "aucun T"
    for res in r:
        assert "erreur" not in res, res
        assert res["entre"] and res["sorti"], f"le char n'est pas ressorti du T : {res}"
        assert res["debloques"] == 0, f"le chien de garde a du intervenir : {res}"
        assert res["boucles"] <= 1, f"le char a tourne en rond dans le T : {res}"
