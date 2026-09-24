"""L'ouverture — la ligne d'histoire commence par une scene, pas par un menu.

Le jeu ne disait JAMAIS sa premisse : l'ecran titre est un voile HTML, et
`Jeu.commencer()` posait le bonhomme devant le terminus avec un message de 150
images. L'oncle Rocco, le garage, les quinze mille piastres de Sal vivaient dans
`docs/plan.md`, dans `economie.DETTE` et dans une replique de Ti-Guy qu'il fallait
aller chercher.

Ce que ces juges tiennent, et qui n'est pas evident :

1. **Le texte est la source** (`missions.OUVERTURE`), la voix se deduit de sa
   place, et les chiffres qu'il annonce sont ceux du jeu — une premisse qui dit
   « cinquante piastres » pendant que le catalogue en donne cent est un mensonge
   de plus, pas une introduction.
2. **La musique existe des DEUX cotes** : un mp3 se genere, des notes le
   remplacent. Un morceau qui n'a ni l'un ni l'autre est un silence qu'on
   deploie.
3. **L'ouverture ne change pas la partie.** C'est le juge central : une partie
   jouee avec l'ouverture et une partie jouee sans doivent etre la MEME — meme
   tuile, meme monde, meme prochain de a tirer. Une animation qui deplace le
   hasard n'est plus une animation, c'est une regle du jeu.
4. **Elle se passe, et elle ne se rejoue pas.**
"""

from app import audio, economie, missions, musique

#: Les chiffres de la premisse, ecrits comme on les dit. ⚠️ Le juge ci-dessous
#: exige que la NARRATION suive le CATALOGUE : le jour ou l'argent de depart ou
#: la dette changent, la phrase du narrateur doit changer avec — sinon
#: l'ouverture ment des la premiere seconde du jeu. Un chiffre absent de cette
#: table fait echouer le test, et c'est voulu : il faut alors ecrire son mot ici.
EN_LETTRES = {50: "cinquante", 100: "cent", 15000: "quinze mille", 20000: "vingt mille"}


def test_l_ouverture_dit_ce_que_le_jeu_ne_dit_nulle_part():
    textes = " ".join(ligne["texte"].lower() for ligne in missions.OUVERTURE)
    assert 3 <= len(missions.OUVERTURE) <= 6, "quatre phrases, pas dix : on la passe, mais on ne l'endure pas"
    assert "rocco" in textes, "qui est mort, et de qui l'on herite"
    assert "sal" in textes, "a qui l'on doit"
    depart = economie.ARGENT_DEPART
    dette = economie.DETTE["montant"]
    assert depart in EN_LETTRES and dette in EN_LETTRES, (
        f"ecrire {depart} et {dette} dans EN_LETTRES : la narration doit pouvoir les dire"
    )
    assert EN_LETTRES[depart] in textes, "avec combien on debarque — le catalogue a change, la phrase doit suivre"
    assert EN_LETTRES[dette] in textes, "ce qu'on doit — le catalogue a change, la phrase doit suivre"


def test_chaque_replique_de_l_ouverture_a_son_personnage_et_son_slug():
    lignes = missions.repliques_ouverture()
    assert len(lignes) == len(missions.OUVERTURE)
    for i, ligne in enumerate(lignes, start=1):
        assert missions.personnage(ligne["qui"]) is not None, f"{ligne['qui']} n'est pas au catalogue"
        assert ligne["slug"] == f"{ligne['qui']}-ouverture-{i}", "le slug suit la PLACE de la ligne"
        assert ligne["mission"] == "ouverture" and ligne["partie"] == "ouverture"
        assert not ligne["telephone"], "le narrateur n'appelle personne"
    assert len({ligne["slug"] for ligne in lignes}) == len(lignes), "un slug par replique"


def test_le_narrateur_de_l_ouverture_est_celui_du_journal():
    """⚠️ Le MEME homme aux deux bouts. C'est ce qui fait une ligne d'histoire
    plutot que deux animations : la voix qui ouvre le jeu est celle qui lira la
    manchette du lendemain matin, et un jour le generique de la fin."""
    ouverture = {v["voix"] for v in audio.voix_ouverture()}
    journal = {v["voix"] for v in audio.voix_journal()}
    assert len(ouverture) == 1 and ouverture == journal


def test_les_voix_de_l_ouverture_se_generent_comme_le_journal():
    voix = audio.voix_ouverture()
    assert len(voix) == len(missions.OUVERTURE)
    assert all(v["histoire"] and v["mission"] == "ouverture" for v in voix)
    assert all(v["texte"] and v["voix"] for v in voix), "une recette complete : le texte et la voix"
    toutes = {v["slug"] for v in audio.toutes_les_voix()}
    assert {v["slug"] for v in voix} <= toutes, "elles passent par le meme generateur que le reste"
    assert len(toutes) == len(audio.toutes_les_voix()), "aucun slug en double dans tout le catalogue"


def test_la_musique_de_l_ouverture_existe_des_deux_cotes():
    """⚠️ Un mp3 ET des notes. `scripts/audio_elevenlabs.py --musiques` ne
    genere que les slugs que `musique.py` connait (`manquants_musique`) : une
    recette dans `audio.MUSIQUES` sans morceau ecrit ne se genere JAMAIS, et
    personne ne s'en apercoit — le jeu joue simplement le silence."""
    recette = audio.piece_par_slug("ouverture")
    assert recette is not None, "la recette ElevenLabs manque"
    ecrit = musique.par_slug("ouverture")
    assert ecrit is not None, "le filet en notes manque : sans mp3, l'ouverture serait muette"
    assert ecrit["voix"], "un morceau sans voix ne joue rien"
    assert abs(musique.duree_s(ecrit) - recette["duree_s"]) <= 5, (
        "le prompt et les notes doivent durer la meme chose : c'est la meme piece, pas deux"
    )
    for voix in ecrit["voix"]:
        for note in voix["notes"]:
            assert 20 <= note[1] <= 10000, "une hauteur (ou une coupure de bruit) plausible"
            assert note[2] > 0, "une note de duree nulle ne s'entend pas"


def test_le_paquet_porte_le_texte_de_l_ouverture(paquet):
    lignes = paquet["ouverture"]
    assert [ligne["slug"] for ligne in lignes] == [ligne["slug"] for ligne in missions.repliques_ouverture()]
    assert all(ligne["texte"] for ligne in lignes), "le texte voyage : la voix n'est qu'un ajout"
    declarees = {v["slug"] for v in paquet["audio"]["histoire"] if v["mission"] == "ouverture"}
    assert declarees == {ligne["slug"] for ligne in lignes}, "chaque phrase a sa voix declaree"


# --- Le banc : ce que le navigateur en FAIT ----------------------------------------


def test_jouer_lance_l_ouverture_et_commencer_ne_la_lance_pas(banc):
    """⚠️ DEUX FONCTIONS, et c'est la moitie qui compte. `commencer()` pose une
    partie — c'est ce qu'appellent cent tests qui veulent une ville, pas une
    introduction. `jouer()` est le GESTE."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const sansOuverture = !!L.B.ouverture;
        L.Jeu.retourTitre();
        L.B.partie.x = null; L.B.partie.y = null; L.B.partie.ouvertureVue = false;
        L.Jeu.jouer();
        const o1 = L.B.ouverture;
        // ⚠️ Le car de la SCENE : les autobus de ligne passent aussi au terminus.
        const car = L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'autobus' && e.conducteur !== 'ligne'; });
        return { sansOuverture: sansOuverture, avec: !!o1, etat: L.B.etat,
                 cars: car.length, loin: car.length ? Math.hypot(car[0].x - o1.arret.x, car[0].y - o1.arret.y) : 0,
                 cache: L.B.joueur.dessine, lignes: L.B.cinema ? L.B.cinema.lignes.length : 0,
                 qui: L.B.cinema ? L.B.cinema.lignes[0].qui : null,
                 demandee: L.Son.Voix.demandees[L.Son.Voix.demandees.length - 1],
                 boite: L.B.dialogue && L.B.dialogue.qui, texte: L.B.dialogue && L.B.dialogue.lignes[0] };
    }""")
    assert r["sansOuverture"] is False, "`commencer()` ne raconte rien : il pose une partie"
    assert r["avec"] is True and r["etat"] == "jeu"
    assert r["cars"] == 1, "un autobus, et un seul"
    assert r["loin"] > 200, "il arrive de hors champ : un car qui apparait dans le cadre s'est allume"
    assert r["cache"] is False, "on ne voit pas encore le bonhomme : il est dans le car"
    assert r["lignes"] == 4 and r["qui"] == "narrateur"
    assert r["demandee"] == "narrateur-ouverture-1", "la premiere phrase demande sa voix"
    assert r["boite"] == "", "aucun nom au-dessus de la boite : c'est une voix, pas quelqu'un a qui l'on parle"
    assert "Baie-des-Brumes" in r["texte"]


def test_l_ouverture_se_termine_toute_seule_et_rend_la_ville(banc):
    r = banc("""function (L, o) {
        L.Jeu.retourTitre();
        L.B.partie.x = null; L.B.partie.y = null; L.B.partie.ouvertureVue = false;
        L.Jeu.jouer();
        const quai = { x: L.B.ouverture.quai.x, y: L.B.ouverture.quai.y };
        let images = 0;
        while (L.B.ouverture && images < 3000) { o.frame(1); images++; }
        const cars = L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'autobus' && e.conducteur !== 'ligne'; }).length;
        return { images: images, reste: !!L.B.ouverture, cinema: !!L.B.cinema, etat: L.B.etat,
                 cars: cars, dessine: L.B.joueur.dessine, vivant: L.B.joueur.vivant,
                 ecart: Math.hypot(L.B.joueur.x - quai.x, L.B.joueur.y - quai.y),
                 etoiles: L.B.recherche.etoiles, vue: L.B.partie.ouvertureVue,
                 sauvee: !!(o.store['bandini-partie-v1'] || '').match(/ouvertureVue":true/) };
    }""")
    assert r["reste"] is False, "l'ouverture se termine TOUJOURS : sans ca, on ne joue jamais"
    assert 300 < r["images"] < 3000, "elle dure quelques secondes, pas une minute"
    assert r["cinema"] is False and r["etat"] == "jeu"
    assert r["cars"] == 0, "le car s'en va pour de vrai : sinon c'est un char de plus a voler, ne au premier geste"
    assert r["dessine"] is True and r["vivant"] is True
    assert r["ecart"] < 1, "on descend exactement ou l'on serait descendu sans elle"
    assert r["etoiles"] == 0, "personne n'a rien vole : le car n'appartient a personne"
    assert r["vue"] is True and r["sauvee"] is True, "le drapeau part dans la sauvegarde tout de suite"


def test_on_passe_l_ouverture_et_on_tombe_au_meme_endroit(banc):
    """⚠️ Une ouverture qu'on ne peut pas passer devient une punition a la
    deuxieme partie. FRAPPE (« PASSER ») et PAUSE la sautent toutes les deux."""
    r = banc("""function (L, o) {
        function neuve() {
            L.Jeu.retourTitre();
            L.B.partie.x = null; L.B.partie.y = null; L.B.partie.ouvertureVue = false;
            L.Jeu.jouer();
        }
        neuve();
        o.frame(30);
        o.tape('Space', 2);                       // FRAPPE = PASSER
        const apresFrappe = { ouverture: !!L.B.ouverture, cinema: !!L.B.cinema,
                              x: L.B.joueur.x, y: L.B.joueur.y, dessine: L.B.joueur.dessine,
                              cars: L.B.entites.filter(function (e) { return e.slug === 'autobus' && e.conducteur !== 'ligne'; }).length };
        neuve();
        o.frame(30);
        o.tape('Escape', 2);                      // PAUSE aussi
        const apresPause = { ouverture: !!L.B.ouverture, etat: L.B.etat, x: L.B.joueur.x, y: L.B.joueur.y };
        // ⚠️ Les COMMANDES s'ouvrent au bout de l'ouverture, passee ou non
        // (`test_commandes_js.py`) : ACTION les ferme, comme le dit leur pied.
        const aide = L.B.menu && L.B.menu.titre;
        o.tape('KeyE', 2);
        // Et la partie continue : on bouge. ⚠️ LES QUATRE DIRECTIONS, pas une :
        // le terminus a un mur a l'est de sa porte, et un juge qui ne pousse
        // que vers la droite accuse l'ouverture d'un mur de la carte.
        let bouge = 0;
        ['KeyW', 'KeyS', 'KeyA', 'KeyD'].forEach(function (touche) {
            const x0 = L.B.joueur.x, y0 = L.B.joueur.y;
            o.tape(touche, 20);
            // ⚠️ UN PIXEL SUFFIT A PROUVER QUE LA COMMANDE PASSE. Le pas de la
            // porte du terminus est un coin serre (mur au nord, batiment a
            // l'est) : mesure faite, on n'y gagne que deux pixels vers le haut.
            // Un juge qui exige une vraie marche juge la carte, pas l'ouverture.
            if (Math.hypot(L.B.joueur.x - x0, L.B.joueur.y - y0) >= 1) bouge++;
        });
        return { frappe: apresFrappe, pause: apresPause, bouge: bouge, aide: aide };
    }""")
    assert r["frappe"]["ouverture"] is False and r["frappe"]["cinema"] is False
    assert r["frappe"]["dessine"] is True and r["frappe"]["cars"] == 0
    assert r["pause"]["ouverture"] is False and r["pause"]["etat"] == "jeu", "PAUSE saute la scene, elle n'ouvre pas le menu"
    assert abs(r["frappe"]["x"] - r["pause"]["x"]) < 1 and abs(r["frappe"]["y"] - r["pause"]["y"]) < 1, (
        "les deux facons de passer laissent au meme endroit"
    )
    assert r["aide"] == "COMMANDES", "passer la scene mene aux commandes, comme la voir jusqu'au bout"
    assert r["bouge"] >= 1, "et on joue des qu'on les ferme : les commandes sont rendues"


def test_l_ouverture_ne_change_rien_a_la_partie(banc):
    """LE JUGE CENTRAL. Une partie jouee avec l'ouverture doit etre EXACTEMENT
    celle qu'on aurait jouee sans : meme tuile, meme monde, meme prochain de.

    ⚠️ Le de compte autant que la position. `Vehicules.creer` tire une couleur
    quand on ne lui en donne pas, `Entites.poussiere` tire des angles : un seul
    de consomme ici et tout ce qui nait ensuite (le trafic, la foule, les
    archetypes) tombe ailleurs. L'ouverture aurait alors change le jeu sans que
    personne ne puisse dire ou."""
    r = banc("""function (L, o) {
        function mesurer(avecOuverture) {
            L.Jeu.retourTitre();
            L.graine(987654);
            L.B.partie.x = null; L.B.partie.y = null; L.B.partie.ouvertureVue = false;
            if (avecOuverture) {
                L.Jeu.jouer();
                let n = 0;
                while (L.B.ouverture && n < 3000) { o.frame(1); n++; }
            } else {
                L.Jeu.commencer();
            }
            return { x: L.B.joueur.x, y: L.B.joueur.y, vie: L.B.joueur.vie,
                     entites: L.B.entites.length,
                     pietons: L.B.entites.filter(function (e) { return e.type === 'pieton'; }).length,
                     vehicules: L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).length,
                     de: L.B.rng() };
        }
        return { sans: mesurer(false), avec: mesurer(true) };
    }""")
    assert r["avec"]["x"] == r["sans"]["x"] and r["avec"]["y"] == r["sans"]["y"], "meme tuile"
    assert r["avec"]["vie"] == r["sans"]["vie"]
    assert r["avec"]["entites"] == r["sans"]["entites"], "le car est parti, et rien n'est ne de plus"
    assert r["avec"]["pietons"] == r["sans"]["pietons"]
    assert r["avec"]["vehicules"] == r["sans"]["vehicules"]
    assert r["avec"]["de"] == r["sans"]["de"], (
        "AUCUN de tire par l'ouverture : sinon tout ce qui nait ensuite tombe ailleurs"
    )


def test_une_partie_en_cours_ne_revoit_pas_l_ouverture(banc):
    r = banc("""function (L, o) {
        // Une partie deja jouee : on a une position dans la ville.
        L.Jeu.retourTitre();
        L.B.partie.ouvertureVue = false; L.B.partie.x = 900; L.B.partie.y = 900;
        L.Jeu.jouer();
        const enCours = !!L.B.ouverture;
        // Une partie neuve, mais dont l'ouverture a deja ete vue.
        L.Jeu.retourTitre();
        L.B.partie.ouvertureVue = true; L.B.partie.x = null; L.B.partie.y = null;
        L.Jeu.jouer();
        const dejaVue = !!L.B.ouverture;
        // ... et on la revoit quand ON la demande, MEME A L'AUTRE BOUT DE LA VILLE.
        // ⚠️ La scene se joue au terminus (c'est la qu'est le car) : le juge
        // verifie qu'on revient exactement ou l'on etait. Une animation qui
        // deplace le joueur n'est plus une animation.
        L.Jeu.retourTitre(); L.Jeu.commencer();
        const loin = L.Histoire.lieu('garage');
        L.B.joueur.x = loin.x; L.B.joueur.y = loin.y;
        L.Entites.dansLaCarte(L.B.joueur);
        const depart = { x: L.B.joueur.x, y: L.B.joueur.y };
        const revue = L.Histoire.ouverture(true);
        const rejoue = L.B.ouverture && L.B.ouverture.rejoue;
        const auTerminus = L.B.ouverture
            ? Math.hypot(L.B.ouverture.quai.x - depart.x, L.B.ouverture.quai.y - depart.y) : 0;
        let n = 0;
        while (L.B.ouverture && n < 3000) { o.frame(1); n++; }
        return { enCours: enCours, dejaVue: dejaVue, revue: revue, rejoue: !!rejoue, fini: !L.B.ouverture,
                 auTerminus: auTerminus, vue: L.B.partie.ouvertureVue,
                 revenu: Math.hypot(L.B.joueur.x - depart.x, L.B.joueur.y - depart.y),
                 dessine: L.B.joueur.dessine };
    }""")
    assert r["enCours"] is False, "celui qui joue depuis trois jours n'a pas besoin qu'on lui presente son oncle"
    assert r["dejaVue"] is False, "une introduction qu'on revoit a chaque chargement devient un peage"
    assert r["revue"] is True and r["rejoue"] is True, "mais elle se revoit quand on la demande (LE CARNET)"
    assert r["fini"] is True and r["dessine"] is True
    assert r["auTerminus"] > 100, "la scene se joue au terminus, la ou est le car — pas la ou on se trouve"
    assert r["revenu"] < 1, "et on revient exactement ou l'on etait : revoir l'ouverture ne teleporte personne"
    assert r["vue"] is True, "et la revoir ne remet pas le drapeau a zero : elle ne rejouera pas d'elle-meme"


def test_la_ville_est_figee_et_le_hud_se_tait_pendant_l_ouverture(banc):
    """⚠️ Figee pour deux raisons, et la seconde est la vraie : une scene ou un
    char peut entrer dans le champ n'est plus une scene, et une partie qui
    avance pendant qu'on regarde n'est plus la meme partie."""
    r = banc("""function (L, o) {
        L.Jeu.retourTitre();
        L.B.partie.x = null; L.B.partie.y = null; L.B.partie.ouvertureVue = false;
        L.Jeu.jouer();
        o.frame(20);
        // ⚠️ Le noir se mesure TOT : il descend en 45 images (`Histoire.OUV.noir`),
        // et une mesure prise a la centieme ne verrait plus que la ville.
        o.ctx.traces = []; L.Hud.dessiner(); const tot = o.ctx.traces.slice();
        const chars = L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.conducteur === 'trafic'; });
        const avant = chars.map(function (v) { return [v.x, v.y]; });
        const t0 = L.B.t;
        o.frame(60);
        const bouge = chars.filter(function (v, i) { return Math.hypot(v.x - avant[i][0], v.y - avant[i][1]) > 0.5; }).length;
        // ⚠️ L'horloge se lit AVANT de passer la scene : deux images de jeu
        // apres, et le juge s'accuse lui-meme.
        const horloge = L.B.t - t0;
        // ⚠️ ON JUGE LES RECTANGLES DESSINES, PAS LEUR NOMBRE. Compter les
        // `fillRect` accuserait l'ouverture : le titre « BANDINI » en corps 4
        // s'ecrit pixel par pixel, et une scene silencieuse en dessine plus
        // qu'un HUD complet. Ce qu'on veut savoir est ailleurs : la barre de
        // vie (6, 6, 60, 5) est-elle la ?
        function barreDeVie(traces) {
            return traces.some(function (r) { return r[0] === 6 && r[1] === 6 && r[2] === 60 && r[3] === 5; });
        }
        function pleinEcran(traces) {
            return traces.some(function (r) { return r[0] === 0 && r[1] === 0 && r[2] === L.VW && r[3] === L.VH; });
        }
        // ⚠️ `.slice()` : le banc ECRIT dans le tableau qu'il tient. Garder la
        // reference, c'est laisser les images suivantes ecrire dans la mesure
        // qu'on vient de prendre — et le juge s'accuse lui-meme, une deuxieme
        // fois.
        o.ctx.traces = []; L.Hud.dessiner(); const pendant = o.ctx.traces.slice();
        L.Histoire.passerOuverture();
        o.frame(2);
        o.ctx.traces = []; L.Hud.dessiner(); const apres = o.ctx.traces.slice();
        o.ctx.traces = null;
        return { trafic: chars.length, bouge: bouge, horloge: horloge,
                 viePendant: barreDeVie(pendant), vieApres: barreDeVie(apres), noir: pleinEcran(tot) };
    }""")
    assert r["horloge"] == 0, "l'horloge du monde ne tourne pas : le temps ne passe pas pendant une scene"
    assert r["bouge"] == 0, "le trafic attend : personne n'entre dans le champ"
    assert r["viePendant"] is False, "vie, etoiles, argent, mini-carte : le HUD se tait pendant la scene"
    assert r["vieApres"] is True, "... et il revient des que la ville est rendue"
    assert r["noir"] is True, "et c'est bien la scene qu'on voit : son noir couvre l'ecran, pas celui d'une porte"


def test_les_fichiers_de_l_ouverture_se_prechauffent_avant_le_premier_geste(banc):
    """⚠️ Elle est le SEUL son qu'il faut avoir avant de le jouer : elle part a
    la seconde ou l'on presse JOUER, et un narrateur qui arrive trois phrases en
    retard ne raconte plus rien. Tout le reste (12 Mo en 166 fichiers) se charge
    a l'usage, et doit le rester."""
    r = banc("""function (L, o) {
        // ⚠️ `o.fetchs` garde des OBJETS (`{ url }`), pas des chaines.
        const demandes = o.fetchs.map(function (f) { return f.url || String(f); })
                                 .filter(function (u) { return u.indexOf('.mp3') > 0; });
        const attendus = L.Histoire.fichiersDeLOuverture();
        return { etat: L.B.etat, demandes: demandes.length, attendus: attendus.length,
                 tous: attendus.length > 0 && attendus.every(function (f) {
                     return demandes.some(function (u) { return u.indexOf(f) >= 0; }); }),
                 parcimonie: demandes.length <= attendus.length };
    }""")
    assert r["etat"] == "titre", "on est encore sur l'ecran titre : personne n'a touche a rien"
    assert r["attendus"] == 5, "une musique et quatre voix : les mp3 sont generes"
    assert r["tous"] is True, "la musique et les quatre voix de l'ouverture sont demandees"
    assert r["parcimonie"] is True, "et rien d'autre : prechauffer largement, c'est avaler la ville sur un forfait"
