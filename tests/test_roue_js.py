"""La roue d'armes — le selecteur du 16 sept. 2026.

⚠️ Jusqu'ici, UN bouton parcourait les TREIZE armes du catalogue d'un cran,
dans un seul sens : revenir de la carabine aux poings coutait douze pressions,
en pleine fusillade, et le HUD ne montrant que l'arme en main, on cyclait a
l'aveugle. Deux gestes remplacent ca sur le meme bouton — une TAPE bascule
entre les deux dernieres armes, TENIR ouvre la roue.

Ce que ces juges tiennent, dans l'ordre de ce qui casse le plus fort :

- **le dessin et la logique tournent dans le meme sens.** C'est LA panne qu'on
  ne verrait pas autrement : `Hud.posteDeLaRoue` place les icones, et
  `Combat.creneauVise` lit la direction du pouce. Si l'un tourne dans le sens
  des aiguilles et l'autre a l'envers, aucun test de logique ne rougit — le
  joueur pointe la carabine et le jeu degaine la pelle. Le juge refait le
  chemin complet : du creneau au pixel, du pixel a la direction, de la
  direction au creneau.
- **le monde RALENTIT, il ne fige pas.** Une roue qui fige serait une pause
  gratuite au milieu d'une fusillade ; le prix de la roue, c'est le quart de
  vitesse et un joueur cloue sur place.
- **on ne se bat pas dedans.** Sans cette porte, tenir ARME donnerait un
  ralenti a la demande : viser tranquillement, puis tirer.
"""


def _espion(effets):
    """Le JS qui remplace chaque effet nomme par un compteur, dans `compte`."""
    return "const compte = {}; " + "".join(
        f"L.Son.SFX.{e} = function () {{ compte.{e} = (compte.{e} || 0) + 1; }}; " for e in effets)


#: Quatre armes, donc quatre creneaux : HAUT, DROITE, BAS, GAUCHE — les seules
#: directions qu'un clavier donne proprement. ⚠️ L'ordre est celui du catalogue
#: (`ordre_armes`), pas celui de ces lignes.
_QUATRE = """
    L.B.partie.armes.pelle = { mun: null, usure: 0 };
    L.B.partie.armes.couteau = { mun: null, usure: 0 };
    L.B.partie.armes.carabine = { mun: 5, usure: 0 };
"""


def test_le_dessin_et_la_direction_disent_le_meme_creneau(banc):
    """Du creneau au pixel, du pixel a la direction, de la direction au creneau.

    ⚠️ Le juge qui compte le plus : une roue dessinee dans un sens et lue dans
    l'autre se joue a l'envers sans qu'aucune autre mesure ne bouge."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const faux = [];
        // ⚠️ Jusqu'au catalogue ENTIER, pas jusqu'a treize : le poing americain
        // en a fait quatorze, et une roue pleine se lit comme les autres.
        for (let n = 2; n <= L.B.defs.armes.length; n++) {
            for (let i = 0; i < n; i++) {
                const p = L.Hud.posteDeLaRoue(i, n, 240, 135);
                const dx = p.x - 240, dy = p.y - 135;
                const d = Math.hypot(dx, dy) || 1;
                const lu = L.Combat.creneauVise({ x: dx / d, y: dy / d, mag: 1 }, n);
                if (lu !== i) faux.push({ n: n, creneau: i, lu: lu, x: p.x, y: p.y });
            }
        }
        return { faux: faux, haut: L.Hud.posteDeLaRoue(0, 4, 240, 135) };
    }""")
    assert r["faux"] == [], "le dessin et la direction ne tournent pas dans le même sens"
    # Et le creneau 0 est EN HAUT : c'est la convention que tout le reste suit.
    assert r["haut"]["x"] == 240 and r["haut"]["y"] < 135


def test_une_tape_bascule_entre_les_deux_dernieres_armes(banc):
    """Les poings pour les poches, la carabine pour le toit — sans rien ouvrir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.armes.batte = { mun: null, usure: 0 };
        L.B.partie.armes.couteau = { mun: null, usure: 0 };
        L.Combat.degainer(j, 'batte');
        L.Combat.degainer(j, 'couteau');
        o.tape('Tab');
        const un = j.arme;
        o.tape('Tab');
        const deux = j.arme;
        o.tape('Tab');
        return { un: un, deux: deux, trois: j.arme, roue: !!L.B.roue };
    }""")
    assert r["un"] == "batte", "la tape n'est pas revenue à l'arme d'avant"
    assert r["deux"] == "couteau" and r["trois"] == "batte", "la bascule ne fait pas l'aller-retour"
    assert r["roue"] is False, "une tape courte ne doit pas ouvrir la roue"


def test_tenir_ouvre_la_roue_sur_l_arme_en_main(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        """ + _QUATRE + """
        L.Combat.degainer(j, 'couteau');
        o.touche('Tab');
        o.frame(L.Combat.TENIR_IMAGES);
        const avant = !!L.B.roue;
        o.frame(4);
        const roue = L.B.roue;
        return { avant: avant, ouverte: !!roue, armes: roue && roue.armes,
                 choix: roue && roue.armes[roue.choix] };
    }""")
    assert r["avant"] is False, "la roue s'ouvre avant la fin du maintien"
    assert r["ouverte"] is True
    assert r["armes"] == ["poings", "pelle", "couteau", "carabine"], "l'ordre du catalogue"
    assert r["choix"] == "couteau", "la roue s'ouvre sur ce qu'on tient déjà"


def test_la_direction_choisit_et_le_relachement_degaine(banc):
    """Quatre armes, quatre creneaux : DROITE, c'est la pelle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        """ + _QUATRE + """
        o.touche('Tab');
        o.frame(20);
        o.touche('ArrowRight');
        o.frame(3);
        const sous = L.B.roue.armes[L.B.roue.choix];
        // ⚠️ La direction revient au centre AVANT qu'on relache le bouton : le
        // choix doit tenir. Sans ca, on valide toujours le creneau du haut.
        o.relacher('ArrowRight');
        o.frame(3);
        const tient = L.B.roue.armes[L.B.roue.choix];
        o.relacher('Tab');
        o.frame(2);
        return { sous: sous, tient: tient, arme: j.arme, roue: !!L.B.roue,
                 precedente: L.B.partie.armePrecedente };
    }""")
    assert r["sous"] == "pelle", "la droite ne pointe pas le deuxième créneau"
    assert r["tient"] == "pelle", "le choix retombe quand le pouce revient au centre"
    assert r["arme"] == "pelle" and r["roue"] is False
    assert r["precedente"] == "poings", "dégainer doit retenir ce qu'on tenait"


def test_la_roue_ralentit_le_monde_sans_le_figer(banc):
    """⚠️ Le prix de la roue. Un menu fige (« le temps ne passe pas au
    comptoir ») ; une roue qui figerait serait une pause gratuite sous le feu."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _QUATRE + """
        const t0 = L.B.t;
        o.frame(40);
        const libre = L.B.t - t0;
        o.touche('Tab');
        o.frame(20);
        const t1 = L.B.t;
        o.frame(40);
        const ralenti = L.B.t - t1;
        o.relacher('Tab');
        o.frame(2);
        const t2 = L.B.t;
        o.frame(40);
        return { libre: libre, ralenti: ralenti, apres: L.B.t - t2, ralentiDef: L.Combat.RALENTI };
    }""")
    # ⚠️ On compare deux FENETRES de meme longueur, jamais un compte exact :
    # `Jeu.boucle` avance par accumulateur, donc quarante images dessinees ne
    # font pas toujours quarante `maj` — un juge qui exige le compte rond
    # rougit un jour sur deux sans rien dire de vrai.
    assert r["libre"] >= 38, "le monde n'avance pas à pleine vitesse, roue fermée"
    assert r["ralenti"] > 0, "la roue FIGE le monde au lieu de le ralentir"
    assert r["ralenti"] * 3 < r["libre"], "la roue ne ralentit pas assez (ou pas du tout)"
    assert r["ralenti"] * 5 > r["libre"], "la roue ralentit bien plus que le quart annoncé"
    assert r["apres"] >= 38, "le monde ne repart pas à pleine vitesse"


def test_le_joueur_ne_marche_plus_pendant_qu_il_choisit(banc):
    """Une seule direction, un seul role : au stick, choisir ferait marcher."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        """ + _QUATRE + """
        o.touche('Tab');
        o.frame(20);
        const x0 = j.x, y0 = j.y;
        o.touche('ArrowRight');
        o.frame(30);
        return { bouge: Math.hypot(j.x - x0, j.y - y0), vx: j.vx, vy: j.vy };
    }""")
    assert r["bouge"] < 0.001, "le joueur marche pendant qu'il choisit son arme"
    assert r["vx"] == 0 and r["vy"] == 0


def test_roue_ouverte_on_ne_se_bat_pas(banc):
    """Sans cette porte, tenir ARME donne un ralenti a la demande."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        """ + _espion(["coup", "pelle"]) + """
        L.B.partie.armes.pelle = { mun: null, usure: 0 };
        o.touche('Tab');
        o.frame(20);
        o.touche('Space');
        o.frame(40);
        return { compte: compte, charge: j.charge, etat: j.etat, roue: !!L.B.roue };
    }""")
    assert r["roue"] is True, "le décor du juge est faux : la roue n'est pas ouverte"
    assert not r["compte"], "un coup est parti pendant que la roue était ouverte"
    assert r["charge"] == 0, "le coup fort se charge pendant qu'on choisit"
    assert r["etat"] != "attaque"


def test_la_pause_referme_la_roue_sans_degainer(banc):
    """⚠️ Sinon elle reste ouverte SOUS le menu : le monde repart au ralenti et
    plus rien ne la ferme (`majRoue` ne tourne pas en pause)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        """ + _QUATRE + """
        o.touche('Tab');
        o.frame(20);
        o.touche('ArrowRight');
        o.frame(3);
        o.relacher('ArrowRight');
        o.tape('Escape');
        return { roue: !!L.B.roue, arme: j.arme, etat: L.B.etat };
    }""")
    assert r["roue"] is False, "la roue survit à la pause"
    assert r["arme"] == "poings", "la pause a dégainé le créneau sous le pouce"
    assert r["etat"] == "pause"


def test_au_volant_arme_reste_la_radio(banc):
    """ARME au volant, c'est la RADIO : la roue ne doit pas s'ouvrir dessus."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        """ + _QUATRE + """
        const v = o.char('auto', 20, 0, 0);
        L.Vehicules.monter(j, v);
        o.touche('Tab');
        o.frame(30);
        return { roue: !!L.B.roue, dedans: !!j.dansVehicule };
    }""")
    assert r["dedans"] is True, "le décor du juge est faux : le joueur n'est pas au volant"
    assert r["roue"] is False, "la roue s'ouvre au volant, par-dessus la radio"


def test_le_cycle_saute_une_arme_a_sec(banc):
    """Un pistolet a zero pris au passage, c'est un tour perdu."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.armes.batte = { mun: null, usure: 0 };
        L.B.partie.armes.pistolet = { mun: 0, usure: 0 };
        L.Combat.degainer(j, 'batte');
        L.Combat.cycler(j);
        const saute = j.arme;
        L.B.partie.armes.pistolet.mun = 3;
        L.Combat.degainer(j, 'batte');
        L.Combat.cycler(j);
        return { saute: saute, charge: j.arme, aSec: L.Combat.aSec('batte') };
    }""")
    assert r["saute"] == "poings", "le cycle a dégainé un pistolet à zéro"
    assert r["charge"] == "pistolet", "un pistolet chargé, lui, se prend au passage"
    assert r["aSec"] is False, "une arme sans chargeur n'est jamais « à sec »"


def test_avec_une_seule_arme_la_roue_ne_s_ouvre_pas(banc):
    """Les poings tout seuls : rien a choisir, et le bouton ne ment pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["menu", "degainer"]) + """
        o.touche('Tab');
        o.frame(30);
        o.relacher('Tab');
        o.frame(2);
        return { roue: !!L.B.roue, arme: L.B.joueur.arme, compte: compte };
    }""")
    assert r["roue"] is False and r["arme"] == "poings"
    assert not r["compte"], "un bouton qui ne peut rien faire ne doit rien jouer"


# --- Le panneau de la roue (30 sept. 2026) ----------------------------------------
#: Martin : « avec la roue de sélection des armes, je veux une image en plus gros
#: des armes et des statistiques de l'arme, avec un petit descriptif ». Tranché sur
#: trois maquettes : un panneau à droite de la roue — le portrait, trois barres
#: chiffrées, les munitions et le bruit, des étiquettes, le descriptif ; ni le prix
#: ni les étoiles.


def test_chaque_arme_a_son_portrait_et_son_descriptif(banc):
    """Une arme neuve au catalogue sans portrait ni descriptif ouvrirait un
    panneau vide — ou l'icone de seize pixels agrandie, deux briques. Et chaque
    portrait est un dessin À LUI, tenu dans ses 48 x 24 : deux armes qui se
    peignent pareil ne se distinguent plus d'un coup d'oeil."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const manque = [], longs = [], debordent = [], signatures = {};
        for (const def of L.B.defs.armes) {
            const f = L.Hud.ficheDArme(def.slug);
            if (!f.descriptif.length) manque.push('descriptif ' + def.slug);
            if (f.descriptif.length > 3) longs.push(def.slug + ' : ' + f.descriptif.join(' / '));
            // ⚠️ La police pixel n'a pas tout : un « ; » s'y peignait en « ? ».
            for (const ch of L.Atlas.normaliser(f.descriptif.join(' ')))
                if (ch !== ' ' && !L.Atlas.connait(ch)) manque.push('« ' + ch + ' » dans ' + def.slug);
            const peintre = L.PORTRAITS[def.slug];
            if (!peintre) { manque.push('portrait ' + def.slug); continue; }
            const ctx = o.doc.createElement('canvas').getContext('2d');
            ctx.traces = [];
            peintre(ctx);
            for (const t of ctx.traces) {
                if (t[0] < 0 || t[1] < 0 || t[0] + t[2] > 48 || t[1] + t[3] > 24) debordent.push(def.slug + ' ' + t.join(','));
            }
            signatures[def.slug] = ctx.traces.length > 12 ? JSON.stringify(ctx.traces) : null;
        }
        return { manque: manque, longs: longs, debordent: debordent, signatures: signatures };
    }""")
    assert r["manque"] == [], "des armes sans portrait ou sans descriptif, ou une lettre que la police ne sait pas écrire"
    assert r["longs"] == [], "un descriptif dépasse trois lignes"
    assert r["debordent"] == [], "un portrait sort de son cadre de 48 x 24"
    vus = {}
    for slug, sig in r["signatures"].items():
        assert sig, f"le portrait de {slug} n'est qu'une poignée de rectangles"
        assert sig not in vus, f"{slug} se peint comme {vus.get(sig)}"
        vus[sig] = slug


def test_le_panneau_dit_les_chiffres_de_l_arme(banc):
    """Les barres portent leur chiffre, et les chiffres sont ceux du jeu : la
    portée et le bruit en mètres (une tuile, comme la distance du HUD), la
    cadence en coups par seconde, les dégâts d'un coup (plombs compris)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.armes.carabine = { mun: 5, usure: 0 };
        L.B.partie.armes.pelle = { mun: null, usure: 2 };
        const f = function (s) { return L.Hud.ficheDArme(s); };
        const val = function (s) { const x = {}; f(s).barres.forEach(function (b) { x[b.libelle] = b.valeur; }); return x; };
        const part = function (s, l) { return f(s).barres.find(function (b) { return b.libelle === l; }).part; };
        return {
            carabine: val('carabine'), fusil: val('fusil'), mitraillette: val('mitraillette'),
            lignes: { carabine: f('carabine').lignes, poings: f('poings').lignes, pelle: f('pelle').lignes },
            etiquettes: { grenade: f('grenade').etiquettes, mitraillette: f('mitraillette').etiquettes,
                          fusil: f('fusil').etiquettes, poings: f('poings').etiquettes, molotov: f('molotov').etiquettes },
            parts: { cadenceMit: part('mitraillette', 'CADENCE'), porteeCar: part('carabine', 'PORTÉE'),
                     degatsPoings: part('poings', 'DÉGÂTS'), degatsPistolet: part('pistolet', 'DÉGÂTS') },
        };
    }""")
    assert r["carabine"] == {"DÉGÂTS": "60", "PORTÉE": "14 M", "CADENCE": "1,1/S"}
    assert r["fusil"]["DÉGÂTS"] == "12×6", "le fusil tire six plombs"
    assert r["mitraillette"]["CADENCE"] == "12/S"
    assert r["lignes"]["carabine"] == ["MUNITIONS 5 / 25", "BRUIT 22 M"]
    assert r["lignes"]["poings"] == ["MUNITIONS À VOLONTÉ", "SANS BRUIT"]
    assert r["lignes"]["pelle"][0] == "SE CASSE DANS 3 COUPS", "l'usure se lit sur l'arme qu'on a, pas sur la neuve"
    assert "EXPLOSE" in r["etiquettes"]["grenade"] and "REBONDIT" in r["etiquettes"]["grenade"]
    assert "AUTOMATIQUE" in r["etiquettes"]["mitraillette"]
    assert "6 PLOMBS" in r["etiquettes"]["fusil"]
    assert "ASSOMME" in r["etiquettes"]["poings"] and "BRÛLE" in r["etiquettes"]["molotov"]
    p = r["parts"]
    assert p["cadenceMit"] == 1 and p["porteeCar"] == 1, "la meilleure du catalogue remplit sa barre"
    assert 0 < p["degatsPoings"] < p["degatsPistolet"] < 1


#: Au téléphone en paysage (844 x 390, le juge des commandes tactiles), SPRINT,
#: ACTION et SAISIR commencent à x 415 en pixels du jeu : le panneau finit avant.
_POUCES_X = 412


def test_le_panneau_tient_a_droite_de_la_roue(banc):
    """À droite de la roue, sans la mordre, et dans l'écran — pour chaque arme,
    la plus bavarde comprise, et pour la roue la plus large (tout le catalogue).
    AU DOIGT, la roue glisse à gauche et le panneau finit avant les pastilles :
    elles mangeaient ses chiffres et son descriptif (vu à la capture)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const n = L.B.defs.armes.length;
        const fautes = [], droites = [];
        for (const doigt of [false, true]) {
            const bord = L.Hud.centreDeLaRoue(doigt).x + L.Hud.rayonDeLaRoue(n) + 11;
            if (L.Hud.centreDeLaRoue(doigt).x - L.Hud.rayonDeLaRoue(n) - 11 < 0) fautes.push('la roue sort à gauche');
            for (const def of L.B.defs.armes) {
                const p = L.Hud.panneauDeLaRoue(def.slug, doigt);
                if (p.x < bord || p.y < 0 || p.x + p.l > L.VW || p.y + p.h > L.VH) fautes.push(def.slug + ' ' + JSON.stringify(p));
                if (doigt) droites.push(p.x + p.l);
            }
        }
        return { fautes: fautes, droite: Math.max.apply(null, droites) };
    }""")
    assert r["fautes"] == [], "le panneau sort de l'écran ou mord la roue"
    assert r["droite"] <= _POUCES_X, "au doigt, le panneau passe sous SPRINT, ACTION ou SAISIR"


def test_le_portrait_se_dessine_en_grand_et_palit_a_sec(banc):
    """Le portrait est dessiné au double (96 x 48) pour l'arme SOUS LE POUCE ;
    à sec, il pâlit comme l'icône de son créneau."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        """ + _QUATRE + """
        L.Combat.degainer(j, 'couteau');
        o.touche('Tab');
        o.frame(20);
        const vus = [];
        const ctx = o.doc.createElement('canvas').getContext('2d');
        ctx.drawImage = function (img, x, y, w, h) { if (w === 96 && h === 48) vus.push(ctx.globalAlpha); };
        const roue = L.B.roue;
        roue.choix = roue.armes.indexOf('carabine');
        L.Hud.dessinerRoue(ctx);
        L.B.partie.armes.carabine.mun = 0;
        L.Hud.dessinerRoue(ctx);
        return vus;
    }""")
    assert r == [1, 0.35], "le grand portrait n'est pas dessiné, ou ne pâlit pas à sec"
