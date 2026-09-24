"""Le piratage (M16, demande de Martin, 21 sept. 2026 : « de l'infiltration et du
hacking ») — une séquence de 4 directions au bouton ACTION, avec le MÊME axe unifié
que la marche. Premier usage en jeu : m53 (le chalutier), objectif `pirater` (étape 2).

⚠️ Sauter directement à l'étape `pirater` est sûr : `resoudre(o.ou, m)` ne dépend
d'aucun véhicule posé (contrairement à `monter`/`livrer`) — un simple point du
mouillage (`carte.mouillages`, `navires.py`)."""

PRELUDE = """
    L.Jeu.commencer();
    const j = L.B.joueur;
    L.Histoire.commencer('m53');
    o.frame(2); L.B.cinema = null; L.B.scene = null;
    L.B.partie.mission.etape = 2;                    // l'objectif `pirater`
    const o2 = L.Histoire.objectif();
    const cible = L.Histoire.resoudre(o2.ou, L.Histoire.courante());
    j.x = cible.x; j.y = cible.y; L.Monde.centrerCamera(j.x, j.y);
    L.Entites.indexer();
"""


def test_on_ouvre_le_piratage_au_bouton_pres_du_terminal(banc):
    """⚠️ Hors de portée, ACTION ne fait rien ; dans le rayon de l'objectif, il ouvre
    `B.piratage` — via `Missions.interagir`, la même chaîne que parler ou monter, pas
    un raccourci à part."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const loin = { avant: !!L.B.piratage };
        j.x = cible.x + 400; j.y = cible.y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        o.tape('KeyE', 2);
        loin.apres = !!L.B.piratage;
        j.x = cible.x; j.y = cible.y; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        o.tape('KeyE', 2);
        return { loin: loin, pres: { ouvert: !!L.B.piratage, longueur: L.B.piratage && L.B.piratage.sequence.length,
                 etape: L.B.piratage && L.B.piratage.etape, fige: { vx: j.vx, vy: j.vy } } };
    }""")
    assert not r["loin"]["avant"] and not r["loin"]["apres"], "le piratage s'ouvre hors de portée"
    assert r["pres"]["ouvert"], "ACTION près du terminal n'ouvre pas le piratage"
    assert r["pres"]["etape"] == 2
    assert r["pres"]["longueur"] == 4, "m53 : longueur 4 (sa fiche)"
    assert r["pres"]["fige"] == {"vx": 0, "vy": 0}, "le joueur bouge encore pendant le piratage"


def test_la_bonne_sequence_avance_l_objectif(banc):
    """⚠️ Le bouton n'est pas lu : c'est l'AXE (`Entree.axe`, unifié clavier/manette/
    tactile) qui donne la direction, au même seuil que la roue d'armes
    (`Combat.creneauVise`). On la rejoue au clavier, une touche tenue puis relâchée
    par flick — un appui qui ne redescend jamais sous le seuil ne recompte pas deux fois."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        o.tape('KeyE', 2);
        const seq = L.B.piratage.sequence;
        const TOUCHE = { haut: 'KeyW', bas: 'KeyS', gauche: 'KeyA', droite: 'KeyD' };
        const progres = [];
        seq.forEach(function (dir, i) {
            o.touche(TOUCHE[dir]);
            o.frame(3);
            // ⚠️ Le DERNIER cran ferme `B.piratage` dans la même image (succès) : rien à
            // lire dessus une fois la séquence complète, seulement avant.
            progres.push(i < seq.length - 1 ? (L.B.piratage ? L.B.piratage.pos : -1) : null);
            o.relacher(TOUCHE[dir]);
            o.frame(3);                                  // redescend sous le seuil bas
        });
        return { progres: progres, fini: !L.B.piratage, etape: L.B.partie.mission.etape,
                 objectif: L.Histoire.ligneObjectif() };
    }""")
    assert r["progres"] == [1, 2, 3, None], f"la séquence n'avance pas un cran à la fois : {r['progres']}"
    assert r["fini"], "le piratage reste ouvert alors que la séquence est complète"
    assert r["etape"] == 3, "l'objectif suivant (les deux Morues qui accourent) n'a pas pris la suite"


def test_une_mauvaise_direction_recommence_la_sequence(banc):
    """Une direction fautive remet `pos` à 0 et compte une erreur — sans fermer le
    piratage : on peut se reprendre."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        o.tape('KeyE', 2);
        const seq = L.B.piratage.sequence;
        const TOUCHE = { haut: 'KeyW', bas: 'KeyS', gauche: 'KeyA', droite: 'KeyD' };
        const AUTRE = { haut: 'bas', bas: 'haut', gauche: 'droite', droite: 'gauche' };
        // La première, correcte — puis la deuxième, VOLONTAIREMENT fautive.
        o.touche(TOUCHE[seq[0]]); o.frame(3); o.relacher(TOUCHE[seq[0]]); o.frame(3);
        const apresUne = { pos: L.B.piratage.pos, ratees: L.B.piratage.ratees };
        o.touche(TOUCHE[AUTRE[seq[1]]]); o.frame(3); o.relacher(TOUCHE[AUTRE[seq[1]]]); o.frame(3);
        return { apresUne: apresUne, apresFaute: { pos: L.B.piratage.pos, ratees: L.B.piratage.ratees },
                 ouvert: !!L.B.piratage };
    }""")
    assert r["apresUne"] == {"pos": 1, "ratees": 0}
    assert r["apresFaute"] == {"pos": 0, "ratees": 1}, "une direction fautive ne remet pas la séquence à zéro"
    assert r["ouvert"], "une seule erreur ferme déjà le piratage — `essais` (3) n'est pas lu"


def test_trop_d_erreurs_declenche_l_alarme(banc):
    """Au-delà de `essais` (3 pour m53), la mission est ratée — échec `alarme`, nouveau
    dans `ECHECS` (M16, 21 sept. 2026)."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        o.tape('KeyE', 2);
        const seq = L.B.piratage.sequence;
        const TOUCHE = { haut: 'KeyW', bas: 'KeyS', gauche: 'KeyA', droite: 'KeyD' };
        const AUTRE = { haut: 'bas', bas: 'haut', gauche: 'droite', droite: 'gauche' };
        const fauxCoup = function () { const t = TOUCHE[AUTRE[seq[0]]]; o.touche(t); o.frame(3); o.relacher(t); o.frame(3); };
        for (let i = 0; i < 3; i++) fauxCoup();           // trois erreurs
        const avantLaQuatrieme = { ouvert: !!L.B.piratage, mission: !!L.B.partie.mission };
        fauxCoup();                                       // la quatrième : au-dela de `essais`
        return { avantLaQuatrieme: avantLaQuatrieme, apres: { ouvert: !!L.B.piratage, mission: !!L.B.partie.mission },
                 msg: L.B.msg };
    }""")
    assert r["avantLaQuatrieme"] == {"ouvert": True, "mission": True}, "trois erreurs ratent déjà la mission (essais=3)"
    assert r["apres"] == {"ouvert": False, "mission": False}, "l'alarme ne fait pas rater la mission"
    assert "RATÉE" in (r["msg"] or ""), r["msg"]


def test_frappe_abandonne_sans_faire_rater(banc):
    """⚠️ FRAPPE referme le piratage comme `Combat.majRoue` referme la roue au
    relâchement d'ARME (même geste, même porte) : on garde sa progression pour
    plus tard, la mission continue."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        o.tape('KeyE', 2);
        const avant = { ouvert: !!L.B.piratage, mission: !!L.B.partie.mission };
        o.tape('KeyX', 2);                                // FRAPPE (attaque)
        return { avant: avant, apres: { ouvert: !!L.B.piratage, mission: !!L.B.partie.mission,
                 etape: L.B.partie.mission && L.B.partie.mission.etape } };
    }""")
    assert r["avant"] == {"ouvert": True, "mission": True}
    assert r["apres"]["ouvert"] is False, "FRAPPE ne referme pas le piratage"
    assert r["apres"]["mission"] and r["apres"]["etape"] == 2, "abandonner ne doit pas faire rater la mission"


def test_le_bouton_change_d_etiquette_et_revient(banc):
    """⚠️ FRAPPE change de sens pendant le piratage (`Entree.contexte('piratage')`) —
    sans quoi le joueur au doigt verrait « FRAPPE » sur un bouton qui abandonne."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        const b = o.doc.querySelector('#boutons b[data-a="attaque"]');
        // ⚠️ `Entree.contexte` n'écrit le bouton qu'au CHANGEMENT : partir d'un autre
        // contexte pour que « pied » s'écrive vraiment, pas seulement dans l'état interne.
        L.Entree.contexte('vehicule'); L.Entree.contexte('pied');
        const avant = b.textContent;
        o.tape('KeyE', 2);
        const pendant = b.textContent;
        o.tape('KeyX', 2);
        return { avant: avant, pendant: pendant, apres: b.textContent };
    }""")
    assert r["avant"] == "FRAPPE"
    assert r["pendant"] == "ABANDONNER"
    assert r["apres"] == "FRAPPE", "le bouton ne reprend pas son sens après le piratage"


def test_le_hud_dessine_la_sequence_sans_lever_d_erreur(banc):
    """Un dessin de plus par image (`Hud.dessinerPiratage`) : le piratage ouvert ne doit pas
    faire planter le rendu, ni disparaître dès la première image — et c'est bien LUI qui a
    dessiné, pas seulement le reste du HUD (`noter('piratage', …)` pose son ancre)."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        o.tape('KeyE', 2);
        o.frame(5);
        return { ouvert: !!L.B.piratage, rects: L.B.stats.rects > 0,
                 ancre: L.Hud.ancres().some(function (a) { return a.nom === 'piratage'; }) };
    }""")
    assert r["ouvert"] and r["rects"] and r["ancre"], "le HUD n'a pas dessiné la séquence du piratage"
