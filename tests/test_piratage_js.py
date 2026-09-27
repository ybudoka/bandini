"""Le piratage (M16, demande de Martin, 21 sept. 2026 : « de l'infiltration et du
hacking ») — depuis le 27 sept. 2026, un LABYRINTHE ÉLECTRIFIÉ (`static/js/circuit.js`) : ACTION
près du terminal l'ouvre, on guide l'étincelle au stick de la prise au port, un fil touché est un
zap, et au-delà de `essais` zaps l'alarme sonne. Premier usage en jeu : m53 (le chalutier),
objectif `pirater` (étape 2). Le module seul a ses juges dans `test_circuit_js.py`.

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

#: Le pilote du banc, AU CLAVIER : une touche tenue à la fois, du centre d'une case de la
#: solution au centre de la suivante, puis tout droit dans le port. Le même que celui de
#: `test_sven_missions_js.py` (m53 et m54 de bout en bout).
PILOTE = """
    function piloter(L, o) {
        const TOUCHE = { haut: 'KeyW', bas: 'KeyS', gauche: 'KeyA', droite: 'KeyD' };
        const C = L.Circuit;
        let tenue = null;
        const tenir = function (t) { if (tenue !== t) { if (tenue) o.relacher(tenue); if (t) o.touche(t); tenue = t; } };
        const p = L.B.piratage.circuit.plan;
        for (let i = 1; i < p.solution.length && L.B.piratage; i++) {
            const cx = (p.solution[i].c + 0.5) * C.CASE, cy = (p.solution[i].r + 0.5) * C.CASE;
            for (let k = 0; k < 60 && L.B.piratage; k++) {
                const e = L.B.piratage.circuit, dx = cx - e.x, dy = cy - e.y;
                if (Math.abs(dx) < C.VITESSE / 2 + 0.05 && Math.abs(dy) < C.VITESSE / 2 + 0.05) break;
                tenir(Math.abs(dx) >= C.VITESSE / 2 + 0.05 ? (dx > 0 ? TOUCHE.droite : TOUCHE.gauche) : (dy > 0 ? TOUCHE.bas : TOUCHE.haut));
                o.frame(1);
            }
        }
        for (let k = 0; k < 40 && L.B.piratage; k++) { tenir(TOUCHE.droite); o.frame(1); }
        tenir(null);
    }
"""

#: Tout droit vers le haut, touche tenue, jusqu'au zap suivant (au pire la bordure de la boîte).
ZAPPER = """
    function zapper(L, o) {
        const avant = L.B.piratage.circuit.zaps;
        o.touche('KeyW');
        for (let k = 0; k < 200 && L.B.piratage && L.B.piratage.circuit.zaps === avant; k++) o.frame(1);
        o.relacher('KeyW'); o.frame(1);
    }
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
        const c = L.B.piratage && L.B.piratage.circuit;
        return { loin: loin, pres: { ouvert: !!L.B.piratage, taille: c && [c.plan.cols, c.plan.rangs],
                 etape: L.B.piratage && L.B.piratage.etape, fige: { vx: j.vx, vy: j.vy } } };
    }""")
    assert not r["loin"]["avant"] and not r["loin"]["apres"], "le piratage s'ouvre hors de portée"
    assert r["pres"]["ouvert"], "ACTION près du terminal n'ouvre pas le piratage"
    assert r["pres"]["etape"] == 2
    assert r["pres"]["taille"] == [7, 4], "m53 : longueur 4 → un labyrinthe de 7 × 4 (sa fiche)"
    assert r["pres"]["fige"] == {"vx": 0, "vy": 0}, "le joueur bouge encore pendant le piratage"


def test_guider_l_etincelle_jusqu_au_port_avance_l_objectif(banc):
    """⚠️ Le bouton n'est pas lu : c'est l'AXE (`Entree.axe`, unifié clavier/manette/tactile)
    qui pousse l'étincelle — ici au clavier, une touche tenue à la fois, sans toucher un fil."""
    r = banc("""function (L, o) {""" + PRELUDE + PILOTE + """
        o.tape('KeyE', 2);
        const c = L.B.piratage.circuit;
        piloter(L, o);
        return { fini: !L.B.piratage, zaps: c.zaps, etape: L.B.partie.mission.etape };
    }""")
    assert r["zaps"] == 0, "le pilote au milieu des couloirs a touché un fil"
    assert r["fini"], "le piratage reste ouvert alors que l'étincelle est au port"
    assert r["etape"] == 3, "l'objectif suivant (les deux Morues qui accourent) n'a pas pris la suite"


def test_un_fil_touche_zappe_sans_fermer(banc):
    """Un zap compte une erreur, ramène l'étincelle à la prise et secoue l'écran — sans fermer
    le piratage : on peut se reprendre."""
    r = banc("""function (L, o) {""" + PRELUDE + ZAPPER + """
        o.tape('KeyE', 2);
        const c = L.B.piratage.circuit, prise = { x: c.x, y: c.y };
        L.B.cam.secousse = 0;
        zapper(L, o);
        const e = L.B.piratage.circuit;
        return { zaps: e.zaps, note: L.B.mission.zaps && L.B.mission.zaps[2], secousse: L.B.cam.secousse > 0,
                 retour: e.x === prise.x && e.y === prise.y, ouvert: !!L.B.piratage };
    }""")
    assert r["zaps"] == 1 and r["note"] == 1, r
    assert r["retour"], "le zap ne ramène pas l'étincelle à la prise"
    assert r["secousse"], "un zap ne secoue pas l'écran"
    assert r["ouvert"], "un seul zap ferme déjà le piratage — `essais` (3) n'est pas lu"


def test_trop_de_zaps_declenchent_l_alarme(banc):
    """Au-delà de `essais` (3 pour m53), la mission est ratée — échec `alarme`, nouveau
    dans `ECHECS` (M16, 21 sept. 2026)."""
    r = banc("""function (L, o) {""" + PRELUDE + ZAPPER + """
        o.tape('KeyE', 2);
        for (let i = 0; i < 3; i++) zapper(L, o);                // trois zaps
        const avantLeQuatrieme = { ouvert: !!L.B.piratage, mission: !!L.B.partie.mission };
        zapper(L, o);                                             // le quatrième : au-delà de `essais`
        return { avantLeQuatrieme: avantLeQuatrieme, apres: { ouvert: !!L.B.piratage, mission: !!L.B.partie.mission },
                 msg: L.B.msg };
    }""")
    assert r["avantLeQuatrieme"] == {"ouvert": True, "mission": True}, "trois zaps ratent déjà la mission (essais=3)"
    assert r["apres"] == {"ouvert": False, "mission": False}, "l'alarme ne fait pas rater la mission"
    assert "RATÉE" in (r["msg"] or ""), r["msg"]


def test_frappe_abandonne_sans_faire_rater_et_les_zaps_restent(banc):
    """⚠️ FRAPPE referme le piratage comme `Combat.majRoue` referme la roue au relâchement
    d'ARME : la mission continue. ⚠️ Mais les zaps RESTENT comptés à la réouverture — sinon
    abandonner remettrait le compteur à zéro gratuitement — et c'est le MÊME labyrinthe."""
    r = banc("""function (L, o) {""" + PRELUDE + ZAPPER + """
        o.tape('KeyE', 2);
        const plan = JSON.stringify(L.B.piratage.circuit.plan);
        zapper(L, o);
        o.frame(L.Circuit.IMMUNITE);
        const avant = { ouvert: !!L.B.piratage, mission: !!L.B.partie.mission };
        o.tape('KeyX', 2);                                // FRAPPE (attaque)
        const apres = { ouvert: !!L.B.piratage, mission: !!L.B.partie.mission,
                        etape: L.B.partie.mission && L.B.partie.mission.etape };
        o.tape('KeyE', 2);
        const c = L.B.piratage && L.B.piratage.circuit;
        return { avant: avant, apres: apres, rouvert: { zaps: c && c.zaps, meme: !!c && JSON.stringify(c.plan) === plan } };
    }""")
    assert r["avant"] == {"ouvert": True, "mission": True}
    assert r["apres"]["ouvert"] is False, "FRAPPE ne referme pas le piratage"
    assert r["apres"]["mission"] and r["apres"]["etape"] == 2, "abandonner ne doit pas faire rater la mission"
    assert r["rouvert"]["zaps"] == 1, "abandonner a remis les zaps à zéro"
    assert r["rouvert"]["meme"], "rouvrir le même terminal a changé de labyrinthe"


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


def test_le_hud_dessine_le_labyrinthe_sans_lever_d_erreur(banc):
    """Un dessin de plus par image (`Hud.dessinerPiratage` → `Circuit.dessiner`) : le piratage
    ouvert ne doit pas faire planter le rendu, ni disparaître dès la première image — et c'est
    bien LUI qui a dessiné, pas seulement le reste du HUD (`noter('piratage', …)` pose son ancre)."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        o.tape('KeyE', 2);
        o.frame(5);
        return { ouvert: !!L.B.piratage, rects: L.B.stats.rects > 0,
                 ancre: L.Hud.ancres().some(function (a) { return a.nom === 'piratage'; }) };
    }""")
    assert r["ouvert"] and r["rects"] and r["ancre"], "le HUD n'a pas dessiné le labyrinthe du piratage"
