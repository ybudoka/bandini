"""Le feu de bâtiment (P4) au banc : il se déclare à l'heure, on l'éteint.

⚠️ On pousse l'heure jusqu'à la minute où un feu doit brûler (l'empreinte de
l'heure est déterministe : `Incendies.feuActifA` le dit sans dé), puis on
Approche le joueur avec l'extincteur en main et on juge l'étreinte.
"""

AMENER = """
    function amener(L, avance) {
        L.Jeu.commencer();
        const d = L.Incendies.donnees(), r = d.regle;
        // Cherche une heure (jour 2, heures 8..16) où un feu brûle, sans dé.
        let fe = null, heure = null;
        for (let hh = 8; hh <= 16 && !fe; hh++) {
            const cand = L.Incendies.feuActifA(2, hh / 24);
            if (cand) { fe = cand; heure = hh / 24; }
        }
        if (!fe) return { aucun: true };
        // On se met à la minute `avance` du feu, hors de l'écran de la façade.
        L.B.partie.jour = 2;
        L.B.partie.heure = heure + (avance || 0) / (24 * 60);
        const p = { x: fe.f.x * L.TT + 8, y: fe.f.y * L.TT + 14 };
        const j = L.B.joueur;
        j.x = p.x - 30 * L.TT; j.y = p.y - 30 * L.TT;   // hors de l'écran
        L.Monde.centrerCamera(j.x, j.y);
        return { fe: fe, r: r, p: p, j: j };
    }
"""


def test_le_feu_se_declare_et_dit_son_nom(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L);
        if (a.aucun) return { aucun: true };
        // On s'approche pour que le feu s'allume à l'écran.
        let signale = false, cible = null;
        for (let i = 0; i < 300; i++) {
            o.frame(1);
            a.j.x = a.p.x; a.j.y = a.p.y + 8; L.Monde.centrerCamera(a.j.x, a.j.y);
            if (L.Incendies.cible()) cible = L.Incendies.cible();
            if (L.B.msg && L.B.msg.indexOf('INCENDIE') === 0) signale = true;
        }
        const fe = L.Incendies.feuActif();
        return { aucun: false, feu: !!fe, nom: fe && L.Incendies.position && L.Incendies.position(fe).nom,
                 signale: signale, cible: cible && cible.nom };
    }""")
    assert not r.get("aucun"), "aucune heure de feu trouvée au jour 2"
    assert r["feu"], "le feu ne brûle pas à l'heure choisie"
    assert r["nom"], "le feu n'a pas de nom (devanture)"
    assert r["signale"], "on ne signale pas le feu qu'on voit"
    assert r["cible"] == r["nom"], "la cible de carte ne dit pas le nom du feu"


def test_l_extincteur_eteint_le_feu_et_paie_une_fois(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L);
        if (a.aucun) return { aucun: true };
        // On donne l'extincteur, on se mire sur le feu, et on tient le jet.
        const j = a.j;
        L.B.partie.armes.extincteur = { mun: 100, usure: 0 };
        j.arme = 'extincteur';
        j.x = a.p.x; j.y = a.p.y + 8; L.Monde.centrerCamera(j.x, j.y);
        j.angle = -Math.PI / 2;          // vise le mur au nord
        const avant = L.B.partie.argent;
        // ⚠️ On TIENT le jet, comme le fait le bouton : phase active tenue.
        j.etat = 'attaque'; j.arc = L.Combat.armeDef('extincteur'); j.phase = 'actif'; j.phaseT = 9999;
        let eteint = false, argent = 0;
        for (let i = 0; i < 120; i++) {
            o.frame(1);
            a.j.x = a.p.x; a.j.y = a.p.y + 8; L.Monde.centrerCamera(a.j.x, a.j.y);
            if (!L.Incendies.feuActif()) eteint = true;
        }
        argent = L.B.partie.argent;
        return { aucun: false, eteint: eteint, gagne: argent - avant };
    }""")
    assert not r.get("aucun")
    assert r["eteint"], "le feu n'est pas éteint au jet d'extincteur"
    assert r["gagne"] == a_incendies_prime(), f"l'extincteur n'a pas payé la prime : {r['gagne']}"


def a_incendies_prime():
    # La prime, lue dans le paquet — sans importer le JS.
    from app import incendies
    return incendies.REGLE["prime"]


def test_le_feu_ne_se_redeclare_pas_dans_l_heure_apres_eteint(banc):
    r = banc("function (L, o) {" + AMENER + """
        const a = amener(L);
        if (a.aucun) return { aucun: true };
        const j = a.j;
        L.B.partie.armes.extincteur = { mun: 100, usure: 0 };
        j.arme = 'extincteur';
        j.x = a.p.x; j.y = a.p.y + 8; j.angle = -Math.PI / 2;
        j.etat = 'attaque'; j.arc = L.Combat.armeDef('extincteur'); j.phase = 'actif'; j.phaseT = 9999;
        for (let i = 0; i < 120; i++) { o.frame(1); a.j.x = a.p.x; a.j.y = a.p.y + 8; L.Monde.centrerCamera(a.j.x, a.j.y); }
        const apresEteintro = !!L.Incendies.feuActif();
        // On recule (le feu allumé ne se recrée pas), et l'heure avance encore.
        for (let i = 0; i < 60; i++) { o.frame(1); a.j.x = a.p.x - 20 * L.TT; a.j.y = a.p.y - 20 * L.TT; L.Monde.centrerCamera(a.j.x, a.j.y); }
        return { aucun: false, apresEteintro: apresEteintro, encore: !!L.Incendies.feuActif() };
    }""")
    assert not r.get("aucun")
    assert r["apresEteintro"] is False, "le feu brûle encore après l'extinction"