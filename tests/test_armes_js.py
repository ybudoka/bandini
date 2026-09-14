"""Les sons des armes — un par arme, et ceux d'autour (a vide, casse, degainer).

⚠️ Jusqu'au 13 sept. 2026, `majAttaque` et `tirer` appelaient `SFX.coup` pour
tout le monde : la batte, le couteau, le pistolet et le fusil faisaient un coup
de poing. Ces juges regardent QUEL effet le combat demande, en remplacant les
effets par des compteurs — le banc n'a ni oreille ni AudioContext, et c'est
justement ce qui rend la question nette : on ne juge pas le son, on juge que
le combat demande le bon.
"""


def _espion(effets):
    """Le JS qui remplace chaque effet nomme par un compteur, dans `compte`."""
    return "const compte = {}; " + "".join(
        f"L.Son.SFX.{e} = function () {{ compte.{e} = (compte.{e} || 0) + 1; }}; " for e in effets)


def test_une_batte_ne_fait_pas_un_coup_de_poing(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["coup", "batte"]) + """
        const j = L.B.joueur;
        L.B.partie.armes.batte = { mun: null, usure: 0 }; j.arme = 'batte';
        L.Combat.frapper(j, false);
        for (let i = 0; i < 40; i++) { L.Entites.indexer(); L.Combat.maj(); }
        return compte;
    }""")
    assert r.get("batte") == 1, r
    assert not r.get("coup"), "la batte a fait un coup de poing"


def test_les_poings_font_toujours_le_coup_de_poing(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["coup"]) + """
        L.Combat.frapper(L.B.joueur, false);
        for (let i = 0; i < 40; i++) { L.Entites.indexer(); L.Combat.maj(); }
        return compte;
    }""")
    assert r.get("coup") == 1, r


def test_le_pistolet_tire_et_clique_a_vide(banc):
    """Le coup de feu, puis — chargeur vide — un clic sec, pas le buzzer des
    menus : celui-la faisait croire que le bouton etait casse."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["coup", "pistolet", "vide", "erreur"]) + """
        const j = L.B.joueur;
        L.B.partie.armes.pistolet = { mun: 1, usure: 0 }; j.arme = 'pistolet';
        const tire = L.Combat.frapper(j, false);
        j.etat = 'flane'; j.phase = null;            // la cadence ne nous retient pas
        const aVide = L.Combat.frapper(j, false);
        return { tire: tire, aVide: aVide, mun: L.B.partie.armes.pistolet.mun, compte: compte };
    }""")
    assert r["tire"] is True and r["aVide"] is False
    assert r["mun"] == 0
    assert r["compte"].get("pistolet") == 1
    assert r["compte"].get("vide") == 1, "la gachette a vide doit cliquer"
    assert not r["compte"].get("coup") and not r["compte"].get("erreur")


def test_un_policier_qui_tire_fait_un_coup_de_feu(banc):
    """Le meme chemin pour les PNJ : `Combat.tirer(agent, pistolet)`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["coup", "pistolet"]) + """
        const agent = o.poser('policier', 40, 0);
        L.Combat.tirer(agent, L.Combat.armeDef('pistolet'));
        return compte;
    }""")
    assert r.get("pistolet") == 1 and not r.get("coup"), r


def test_une_arme_de_fortune_casse_en_le_disant(banc):
    """Chaque coup de cone fait un bruit de cone, et la casse fait une casse —
    pas le buzzer de refus."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["cone", "casse", "erreur", "coup"]) + """
        const j = L.B.joueur;
        L.Combat.ramasserArme('cone', null); j.arme = 'cone';
        const def = L.Combat.armeDef('cone');
        for (let coup = 0; coup < def.usures; coup++) {
            const cible = o.poser('ouvrier', 12, 0);
            cible.vie = 999; cible.vieMax = 999;
            o.viser(cible);
            L.Combat.frapper(j, false);
            for (let i = 0; i < 40; i++) { L.Entites.indexer(); L.Combat.maj(); }
            L.Entites.retirer(cible);
        }
        return { usures: def.usures, casse: !L.B.partie.armes.cone, arme: j.arme, compte: compte };
    }""")
    assert r["casse"] is True and r["arme"] == "poings"
    assert r["compte"].get("cone") == r["usures"]
    assert r["compte"].get("casse") == 1
    assert not r["compte"].get("erreur") and not r["compte"].get("coup")


def test_changer_d_arme_degaine(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["menu", "degainer"]) + """
        const j = L.B.joueur;
        L.B.partie.armes.batte = { mun: null, usure: 0 };
        L.Combat.cycler(j);
        return { arme: j.arme, compte: compte };
    }""")
    assert r["arme"] == "batte"
    assert r["compte"].get("degainer") == 1 and not r["compte"].get("menu")


def test_le_jet_de_l_extincteur_s_entend_tant_qu_il_sort(banc):
    """`SFX.jet(actif)` recoit la verite a chaque image : vrai tant que le
    bouton est tenu et qu'il reste de la poudre, faux des qu'on lache."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const jets = [];
        L.Son.SFX.jet = function (actif) { jets.push(!!actif); };
        const j = L.B.joueur;
        L.B.partie.armes.extincteur = { mun: 30, usure: 0 }; j.arme = 'extincteur'; L.B.partie.arme = 'extincteur';
        o.frame(2);
        const avant = jets.slice();
        o.touche('KeyJ'); o.frame(12);
        const tenu = jets.slice(avant.length);
        o.relacher('KeyJ'); o.frame(4);
        const lache = jets.slice(avant.length + tenu.length);
        return { avant: avant, tenu: tenu, lache: lache, mun: L.B.partie.armes.extincteur.mun };
    }""")
    assert r["avant"] and not any(r["avant"]), "sans bouton, pas de jet"
    assert r["tenu"][-1] is True and r["tenu"].count(True) >= 8, r["tenu"]
    assert r["lache"][-1] is False, "bouton lache, le jet doit se taire"
    assert r["mun"] < 30, "le jet n'a pas depense de poudre"


def test_le_jet_tourne_en_boucle_ou_souffle_par_a_coups(banc):
    """Avec l'echantillon : UNE boucle, allumee puis eteinte — pas un depart par
    image. Sans lui : le filet, un souffle court par a-coups."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        let souffles = 0;
        const vrai = L.Son.SFX.extincteur;
        L.Son.SFX.extincteur = function () { souffles++; return vrai(); };
        const j = L.B.joueur;
        L.B.partie.armes.extincteur = { mun: 60, usure: 0 }; j.arme = 'extincteur'; L.B.partie.arme = 'extincteur';
        const charge = L.Son.estCharge('extincteur');
        o.touche('KeyJ'); o.frame(30);
        const pendant = L.Son.boucleActive('extincteur');
        o.relacher('KeyJ'); o.frame(4);
        return { charge: charge, pendant: pendant, apres: L.Son.boucleActive('extincteur'), souffles: souffles };
    }""")
    if r["charge"]:
        assert r["pendant"] is True and r["apres"] is False
        assert r["souffles"] == 0, "avec la boucle, pas de souffle par a-coups"
    else:
        assert r["souffles"] >= 3, "sans echantillon, le filet doit souffler"
        assert r["pendant"] is False
