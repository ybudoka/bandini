"""« Valide que les véhicules n'arrêtent pas sur un passage à piéton. »

Demande de Martin. Depuis que le trottoir fait UNE tuile, la traverse est
collée à la ligne d'arrêt : un char qui attend le CENTRE de sa tuile sur la
ligne peint tout ce qui dépasse ses huit pixels d'avant sur les bandes — et
c'est là, précisément, que le seul piéton qui a le droit d'être sur la
chaussée doit passer.

Les juges d'ici mesurent les promesses de la fiche : le **nez à la
ligne** pour tout le parc (et pas seulement pour l'autobus, qui y arrivait par
la seule vertu de sa longueur), **la ville entière** qui ne garde plus une
seule attente sur une traverse, et **la panne** — la seule entrave qui campe
quarante minutes sur une voie — qui ne se pose jamais contre un passage.
"""

import json

import pytest

from app import vehicules

#: ⚠️ **LA MEME APPROCHE POUR TOUS LES JUGES**, et elle est choisie, pas prise au
#: hasard : une ligne d'arrêt d'un croisement **à feux** (un T n'a qu'un STOP, et
#: un STOP se franchit), avec **huit tuiles de voie droite derrière** — de quoi
#: arriver lancé — et la traverse bien juste après elle. Écrite une fois ici,
#: posée dans le JS de chaque juge : deux copies de la même recherche, c'est deux
#: juges qui ne mesurent plus la même rue le jour où la ville bouge.
CHERCHER_LIGNE = """(function (L) {
    const PAS = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] };
    const c = L.Monde.carte;
    for (const cle in c.arrets) {
        const sens = c.arrets[cle], p = PAS[sens];
        const sx = parseInt(cle.split(',')[0], 10), sy = parseInt(cle.split(',')[1], 10);
        const inter = L.Monde.intersectionA(sx + p[0], sy + p[1]);
        if (!inter || !inter.feux) continue;
        if (!L.Monde.estPassage(sx + p[0], sy + p[1])) continue;
        let droit = true;
        for (let k = 1; k <= 8; k++) if (L.Monde.fleche(sx - p[0] * k, sy - p[1] * k) !== sens) droit = false;
        if (droit) return { sx: sx, sy: sy, sens: sens, p: p, inter: inter };
    }
    return null;
})(L)"""

#: Tout ce qui roule sur la rue : la chaloupe ne voit jamais une ligne d'arret.
ROULANTS = [v["slug"] for v in vehicules.CATALOGUE if not v["eau"]]


def test_chaque_char_du_catalogue_s_arrete_le_nez_a_la_ligne(banc):
    """⚠️ **LE JUGE DE LA FICHE.** Un feu rouge tenu, une approche droite, et
    tout le parc l'un apres l'autre : le nez ne doit pas depasser la ligne
    d'arret d'un pixel, et il doit quand meme y arriver — s'arreter une tuile
    avant n'est pas mieux, c'est un autre defaut.

    Mesure d'avant (banc du 17 sept. 2026) : berline 4,9 px dans les bandes,
    remorqueuse 10, camion 12, autobus 24 — la traverse entiere."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.heure = 0.5;                      // plein jour : pas de clignotant
        const TT = L.TT;
        const ligne = CHERCHER(L);
        if (!ligne) return { trouve: false };
        const p = ligne.p;
        // Le feu ROUGE, tenu : `feuDeCirculation` est une pure fonction de `B.t`,
        // qu'on fige apres l'avoir amene sur le rouge.
        for (let k = 0; k < 2000 && L.Monde.feuDeCirculation(ligne.inter, ligne.sens) !== 'rouge'; k++) L.B.t++;
        const bord = { x: ligne.sx * TT + 8 + p[0] * 8, y: ligne.sy * TT + 8 + p[1] * 8 };
        const chars = {};
        for (const slug of SLUGS) {
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
            const depart = { x: (ligne.sx - p[0] * 4) * TT + 8, y: (ligne.sy - p[1] * 4) * TT + 8 };
            const v = L.Vehicules.creer(slug, depart.x, depart.y, Math.atan2(p[1], p[0]),
                                        { conducteur: 'trafic', etat: 'roule', sens: ligne.sens });
            if (!v) { chars[slug] = null; continue; }
            v.vitesse = v.def.vitesse_max * L.B.defs.conduite.trafic.vitesse_ville;
            for (let i = 0; i < 400; i++) {
                L.Entites.indexer();
                L.Vehicules.majConducteur(v);
                v.x += v.vx; v.y += v.vy;
            }
            const nx = v.x + Math.cos(v.angle) * v.def.longueur / 2;
            const ny = v.y + Math.sin(v.angle) * v.def.longueur / 2;
            chars[slug] = {
                // Ce qui DEPASSE la ligne, le long de la marche : positif = dans la traverse.
                depasse: Math.round(((nx - bord.x) * p[0] + (ny - bord.y) * p[1]) * 100) / 100,
                arrete: Math.abs(v.vx) + Math.abs(v.vy) < 0.05,
                sorti: Math.abs((v.y - depart.y) * p[0] + (v.x - depart.x) * p[1]) > 6,
            };
            L.Entites.retirer(v);
        }
        return { trouve: true, chars: chars };
    }""".replace("CHERCHER(L)", CHERCHER_LIGNE).replace("SLUGS", json.dumps(ROULANTS)))
    assert r["trouve"], "aucune ligne d'arrêt de croisement à feux avec huit tuiles droites derrière"
    for slug in ROULANTS:
        etat = r["chars"][slug]
        assert etat, f"{slug} n'a pas pu naître sur la rue"
        assert etat["arrete"], f"{slug} ne s'est pas arrêté au feu rouge"
        assert etat["depasse"] <= 0, f"{slug} attend {etat['depasse']} px DANS la traverse"
        assert etat["depasse"] > -18, f"{slug} s'arrête {-etat['depasse']} px avant la ligne : il n'y arrive pas"
        assert not etat["sorti"], f"{slug} a quitté sa voie en s'arrêtant"


def test_le_long_char_repart_au_vert_et_franchit_la_ligne(banc):
    """⚠️ **L'AUTRE MOITIE, ET ELLE COMPTE AUTANT.** S'arreter avant la ligne ne
    vaut rien si l'on n'en repart pas : un autobus qui freine une tuile plus tot
    pourrait tres bien ne plus jamais trouver la raison d'avancer. Au vert, il
    passe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.heure = 0.5;
        const TT = L.TT;
        const ligne = CHERCHER(L);
        if (!ligne) return { trouve: false };
        const p = ligne.p;
        for (let k = 0; k < 2000 && L.Monde.feuDeCirculation(ligne.inter, ligne.sens) !== 'rouge'; k++) L.B.t++;
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const v = L.Vehicules.creer('autobus', (ligne.sx - p[0] * 4) * TT + 8, (ligne.sy - p[1] * 4) * TT + 8,
                                    Math.atan2(p[1], p[0]), { conducteur: 'trafic', etat: 'roule', sens: ligne.sens });
        v.vitesse = v.def.vitesse_max * L.B.defs.conduite.trafic.vitesse_ville;
        for (let i = 0; i < 400; i++) { L.Entites.indexer(); L.Vehicules.majConducteur(v); v.x += v.vx; v.y += v.vy; }
        const avantLaLigne = (v.x - ligne.sx * TT - 8) * p[0] + (v.y - ligne.sy * TT - 8) * p[1] <= 0;
        // Le vert, maintenant : le meme char, le meme croisement.
        for (let k = 0; k < 2000 && L.Monde.feuDeCirculation(ligne.inter, ligne.sens) !== 'vert'; k++) L.B.t++;
        for (let i = 0; i < 400; i++) { L.Entites.indexer(); L.Vehicules.majConducteur(v); v.x += v.vx; v.y += v.vy; }
        const franchi = (v.x - ligne.sx * TT - 8) * p[0] + (v.y - ligne.sy * TT - 8) * p[1];
        return { trouve: true, avantLaLigne: avantLaLigne, franchi: Math.round(franchi) };
    }""".replace("CHERCHER(L)", CHERCHER_LIGNE))
    assert r["trouve"], "aucune ligne d'arrêt de croisement à feux avec huit tuiles droites derrière"
    assert r["avantLaLigne"], "l'autobus a attendu au-delà de la ligne d'arrêt"
    assert r["franchi"] > 32, f"au vert, l'autobus n'a avancé que de {r['franchi']} px : il reste planté"


@pytest.mark.parametrize("graine", [1, 2, 5])
def test_la_ville_n_a_plus_une_seule_attente_sur_une_traverse(banc, graine):
    """⚠️ **LA VILLE, PAS UN BANC.** Le juge d'au-dessus tient un char sur une
    approche choisie ; celui-ci laisse la ville vivre et compte les nez posés
    sur les bandes pendant qu'ils ATTENDENT (feu, stop, boîte).

    Mesure d'avant, graine 5, 2 000 images : **5 550 relevés**, jusqu'à douze
    pixels de nez dans les bandes.

    ⚠️ Il ne compte que les ATTENTES. Un char qui cède à un piéton déjà engagé
    s'arrête forcément devant lui, donc sur la traverse — c'est la règle, pas le
    défaut. Et un char surpris DANS la boîte par une file qui se fige devant lui
    reste un autre mécanisme, nommé dans la fiche."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(GRAINE);
        L.Vehicules.monter(L.B.joueur, o.char('auto', 0, 0, 0));
        const TT = L.TT;
        let releves = 0, pire = 0;
        for (let k = 0; k < 1500; k++) {
            o.frame(1);
            for (const v of L.B.entites) {
                if (v.type !== 'vehicule' || !v.attendFeu || v.arretT > 0) continue;
                if (v.conducteur !== 'trafic' && v.conducteur !== 'ligne') continue;
                if (Math.abs(v.vitesse) > 0.05) continue;
                const nx = v.x + Math.cos(v.angle) * v.def.longueur / 2;
                const ny = v.y + Math.sin(v.angle) * v.def.longueur / 2;
                const tx = Math.floor(nx / TT), ty = Math.floor(ny / TT);
                if (!L.Monde.estPassage(tx, ty)) continue;
                const p = [Math.round(Math.cos(v.angle)), Math.round(Math.sin(v.angle))];
                const bord = p[0] > 0 ? tx * TT : p[0] < 0 ? (tx + 1) * TT : p[1] > 0 ? ty * TT : (ty + 1) * TT;
                const dans = p[0] ? (nx - bord) * p[0] : (ny - bord) * p[1];
                if (dans <= 0.5) continue;                 // le nez SUR la ligne, pas dedans
                // ⚠️ SURPRIS PAR LE FEU, IL S'ARRETE OU IL EST — c'est la regle de
                // `pointDArret` (« jamais derriere soi »), pas une attente mal posee : le
                // feu a tourne quand il etait deja dans sa distance de freinage. On juge
                // la REGLE : le point d'arret qu'elle donne, recalcule depuis la ligne ;
                // un char arrete au-dela de ce point a ete surpris, un char arrete dessus
                // avec le nez dans les bandes, c'est la regle qui ment. Ce juge tenait
                // par la graine (un camion surpris a la graine 1 des le 21 sept. 2026,
                // quand les velos ont change la chronologie du trafic ; trois graines sur
                // trente-six sur la base, le hasard decale d'un a trois tirages).
                let lx = tx, ly = ty;                      // du nez, sur les bandes, on recule jusqu'a la ligne
                for (let n = 0; n < 3 && L.Monde.fleche(lx, ly) !== 'S'; n++) { lx -= p[0]; ly -= p[1]; }
                if (L.Monde.fleche(lx, ly) === 'S') {
                    const regle = L.Vehicules.pointDArret({ x: -1e9 * p[0], y: -1e9 * p[1], def: v.def }, lx, ly, p);
                    if ((v.x - regle.x) * p[0] + (v.y - regle.y) * p[1] > 0.5) continue;
                }
                releves++;
                pire = Math.max(pire, dans);
            }
        }
        return { releves: releves, pire: Math.round(pire * 10) / 10 };
    }""".replace("GRAINE", str(graine)))
    assert r["releves"] == 0, (
        f"{r['releves']} images d'attente le nez dans une traverse (au pire {r['pire']} px)"
    )


def test_la_panne_ne_se_pose_jamais_contre_une_traverse(banc):
    """⚠️ **L'AUTRE MOITIE DE LA FICHE.** Le trafic n'attend plus sur les bandes,
    encore faut-il que personne n'y campe : une panne tient QUARANTE MINUTES de
    jeu sur sa voie, là où un char au feu repart. Elle ne se posait jamais sur
    la ligne d'arrêt ni dans le croisement (`placeDeLaPanne` exige une flèche),
    mais la voie qui précède une traverse est une voie comme une autre — et une
    caisse de 48 px la couvre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const TT = L.TT, j = L.B.joueur;
        const PAS = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] };
        const long = Math.max.apply(null, L.B.defs.conduite.trafic.panne.slugs.map(function (s) {
            return L.B.defs.vehicules.find(function (d) { return d.slug === s; }).longueur;
        }));
        const depart = { x: j.x, y: j.y };
        let places = 0, fautes = 0;
        for (let n = 0; n < 400; n++) {
            // On promene le joueur dans la ville : la panne se tire autour de lui.
            const a = n / 400 * Math.PI * 2, d = 400 + (n % 7) * 260;
            j.x = depart.x + Math.cos(a) * d; j.y = depart.y + Math.sin(a) * d;
            const place = L.Vehicules.placeDeLaPanne(n * 7919 + 13);
            if (!place) continue;
            places++;
            const p = PAS[place.sens];
            // La caisse, pas le centre : de la moitie de la plus longue, de chaque bord.
            for (let px = -long / 2; px <= long / 2; px += 4) {
                const tx = Math.floor((place.x + p[0] * px) / TT), ty = Math.floor((place.y + p[1] * px) / TT);
                if (L.Monde.estPassage(tx, ty)) { fautes++; break; }
            }
        }
        return { places: places, fautes: fautes, long: long };
    }""")
    assert r["places"] > 100, f"seulement {r['places']} places de panne tirées : le juge ne mesure rien"
    assert r["fautes"] == 0, f"{r['fautes']} pannes sur {r['places']} posées en travers d'une traverse"


def test_le_degagement_de_la_panne_couvre_la_plus_longue_caisse():
    """⚠️ Le dégagement est en TUILES, les caisses en pixels : deux tuiles de
    chaque bord doivent couvrir la demi-longueur du plus long char qui tombe en
    panne. Le jour où l'autobus grandit, c'est ici que ça se voit."""
    panne = vehicules.TRAFIC["panne"]
    plus_long = max(vehicules.par_slug(slug)["longueur"] for slug in panne["slugs"])
    assert panne["ecart_traverse_tuiles"] * 16 >= plus_long / 2, (
        f"{panne['ecart_traverse_tuiles']} tuiles ne couvrent pas les {plus_long / 2} px "
        "de la plus longue caisse qui tombe en panne"
    )


def test_le_chien_de_garde_ne_mord_pas_un_long_char_sage(banc):
    """⚠️ **LE PIEGE DE LA TUILE D'AVANT.** Un char de plus de 32 px attend
    maintenant sur la tuile qui PRECEDE la ligne d'arrêt : le croisement est
    alors à deux tuiles de lui, et `attenteLegitime`, qui n'en regardait qu'une,
    répondait « il n'attend rien de légitime ». Dix secondes d'un feu rouge — et
    il en dure jusqu'à 480 images, plus l'attente de boîte — et le chien de
    garde téléportait un camion parfaitement poli au milieu de la voie.

    C'est exactement la faute réparée à M8 pour le trafic ordinaire, reparue par
    l'autre bout : un char sage ne doit jamais être « débloqué »."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.heure = 0.5;
        const TT = L.TT;
        const ligne = CHERCHER(L);
        if (!ligne) return { trouve: false };
        const p = ligne.p;
        for (let k = 0; k < 2000 && L.Monde.feuDeCirculation(ligne.inter, ligne.sens) !== 'rouge'; k++) L.B.t++;
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const v = L.Vehicules.creer('autobus', (ligne.sx - p[0] * 4) * TT + 8, (ligne.sy - p[1] * 4) * TT + 8,
                                    Math.atan2(p[1], p[0]), { conducteur: 'trafic', etat: 'roule', sens: ligne.sens });
        v.vitesse = v.def.vitesse_max * L.B.defs.conduite.trafic.vitesse_ville;
        // ⚠️ Le feu reste rouge (`B.t` est fige) : on tient le char bien plus
        // longtemps que le seuil du chien de garde, dix secondes.
        for (let i = 0; i < 900; i++) {
            L.Entites.indexer();
            L.Vehicules.majConducteur(v);
            v.x += v.vx; v.y += v.vy;
        }
        const surLaTuileDAvant = Math.floor(v.x / TT) !== ligne.sx || Math.floor(v.y / TT) !== ligne.sy;
        return { trouve: true, debloques: v.debloques || 0, surLaTuileDAvant: surLaTuileDAvant };
    }""".replace("CHERCHER(L)", CHERCHER_LIGNE))
    assert r["trouve"], "aucune ligne d'arrêt de croisement à feux avec huit tuiles droites derrière"
    assert r["surLaTuileDAvant"], (
        "l'autobus n'attend pas sur la tuile d'avant : le juge ne mesure pas ce qu'il croit"
    )
    assert r["debloques"] == 0, "le chien de garde a « débloqué » un autobus arrêté à un feu rouge"
