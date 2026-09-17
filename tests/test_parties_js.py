"""Trois parties, et on les gère — le choix des parties au titre.

Demande de Martin : « on devrait pouvoir avoir 3 sauvegardes et les gérer ». Une
seule partie vivait dans le `localStorage`, et le titre n'avait qu'un bouton
JOUER : recommencer, c'était perdre sa partie.

Ce que ces juges tiennent, et qui n'est pas évident :

1. **La partie d'avant ne bouge pas.** Elle était sous `bandini-partie-v1` ; elle
   y reste et devient l'emplacement 1 sans une écriture.
2. **Une ville posée pour une partie ne sert pas à une autre.** Changer de partie
   après avoir joué RECHARGE la page — et le choix se rouvre tout seul dessus.
3. **Une partie effacée ne revient pas** — ni par la sauvegarde automatique de
   celle qu'on avait en mémoire, ni par un ACTION de trop (le curseur de la
   confirmation s'ouvre sur NON).
4. **Copier, c'est copier à l'octet**, et écraser se demande comme effacer.

⚠️ Tous les gestes passent par les BOUTONS (`o.tape`) : un juge qui appelle la
fonction ne voit pas un menu qui ne s'ouvre pas.
"""

import json

import pytest

UN, DEUX, TROIS = "bandini-partie-v1", "bandini-partie-v1-2", "bandini-partie-v1-3"
ACTIF = "bandini-emplacement-v1"
ROUVRIR = "bandini-rouvrir-parties"

OUTILS = """
    function ici(L) { const m = L.B.menu; return m ? m.items[m.curseur].libelle : null; }
    function libelles(L) { return L.B.menu ? L.B.menu.items.map(function (i) { return i.libelle; }) : null; }
    /** Descend jusqu'a la ligne qui commence par `debut` (BAS, comme au pouce). */
    function aller(L, o, debut) {
      for (let k = 0; k < 12 && ici(L).indexOf(debut) !== 0; k++) o.tape('KeyS', 1);
      if (ici(L).indexOf(debut) !== 0) throw new Error('pas de ligne ' + debut + ' dans ' + libelles(L));
    }
    function quitterVersLeTitre(L, o) {
      o.tape('Escape', 1);
      aller(L, o, 'QUITTER VERS LE TITRE');
      o.tape('KeyE', 1);
    }
"""


@pytest.fixture(scope="module")
def partie(paquet):
    """Une partie sauvegardée comme le jeu l'écrit : posée dans la ville, ouverture vue."""
    app = paquet["carte"]["apparition"]["joueur"]

    def faire(jour, argent, secondes=600, **extra):
        p = {"version": 1, "jour": jour, "argent": argent, "x": app["x"] * 16 + 8, "y": app["y"] * 16 + 8,
             "ouvertureVue": True, "stats": {"secondes": secondes}, "missionsFaites": {}}
        p.update(extra)
        return json.dumps(p)

    return faire


def test_la_partie_d_avant_les_emplacements_est_la_partie_1(banc, partie):
    vieille = partie(7, 321, 4000)
    r = banc("function (L, o) {" + OUTILS + """
        const chargee = { jour: L.B.partie.jour, emplacement: L.Sauvegarde.emplacement() };
        o.tape('KeyE', 1);
        const menu = { titre: L.B.menu && L.B.menu.titre, libelles: libelles(L), ici: ici(L), voile: L.Hud.voileCourant,
                       aide: L.B.menu && L.B.menu.aide };
        // FRAPPE referme le choix : on revient au titre, pas dans la partie.
        o.tape('Space', 1);
        const ferme = { etat: L.B.etat, menu: !!L.B.menu, voile: L.Hud.voileCourant };
        o.tape('KeyE', 1);
        const brut = o.store['bandini-partie-v1'], cles = Object.keys(o.store).sort();
        o.tape('KeyE', 1);
        return { chargee: chargee, menu: menu, ferme: ferme, etat: L.B.etat, jour: L.B.partie.jour,
                 scene: !!(L.B.scene || L.B.ouverture), brut: brut, cles: cles,
                 ecrite: JSON.parse(o.store['bandini-partie-v1']).jour, rechargements: o.rechargements() };
    }""", stockage={UN: vieille})
    assert r["chargee"] == {"jour": 7, "emplacement": 1}, "la partie d'avant se charge comme la partie 1"
    assert r["menu"]["titre"] == "PARTIES" and r["menu"]["voile"] is None
    assert r["menu"]["libelles"][:3] == ["1  JOUR 7 · 321 $", "2  NOUVELLE PARTIE", "3  NOUVELLE PARTIE"]
    assert r["menu"]["ici"].startswith("1  "), "le curseur attend sur la derniere partie jouee"
    assert r["menu"]["aide"] == "0 MISSION", "une partie d'avant n'a pas de date : on ne l'invente pas"
    assert r["ferme"] == {"etat": "titre", "menu": False, "voile": "titre"}
    assert r["etat"] == "jeu" and r["jour"] == 7 and not r["scene"], "deux ACTION : on continue, sans ouverture"
    assert r["brut"] == vieille, "ouvrir, fermer et rouvrir le choix n'ecrit rien"
    assert r["cles"] == [UN], "aucune migration : pas une cle de plus tant qu'on n'a rien choisi"
    assert r["ecrite"] == 7, "et la partie qu'on joue se sauvegarde a sa place"
    assert r["rechargements"] == 0


def test_sans_aucune_partie_jouer_commence_tout_de_suite(banc):
    """Trois fois « NOUVELLE PARTIE » devant quelqu'un qui ouvre le jeu pour la
    premiere fois, c'est un menu qui ne choisit rien."""
    r = banc("""function (L, o) {
        o.elements['bouton-jouer'].dispatch('click', {});
        return { etat: L.B.etat, menu: !!L.B.menu, ouverture: !!(L.B.scene || L.B.ouverture),
                 emplacement: L.Sauvegarde.emplacement() };
    }""")
    assert r == {"etat": "jeu", "menu": False, "ouverture": True, "emplacement": 1}


def test_le_bouton_jouer_de_la_page_ouvre_le_choix(banc, partie):
    """Au doigt et a la souris, JOUER est un bouton de la page, pas ACTION."""
    r = banc("""function (L, o) {
        // ENTREE sur le bouton qui a le focus : la touche descend, PUIS le clic.
        o.touche('Enter');
        o.elements['bouton-jouer'].dispatch('click', {});
        o.frame(2); o.relacher('Enter'); o.frame(1);
        return { etat: L.B.etat, menu: L.B.menu && L.B.menu.titre, voile: L.Hud.voileCourant };
    }""", stockage={UN: partie(7, 321)})
    assert r == {"etat": "titre", "menu": "PARTIES", "voile": None}, (
        "le clic ouvre le choix, et la touche qui l'a produit n'y choisit rien"
    )


def test_une_partie_neuve_dans_la_2_ne_touche_pas_a_la_1(banc, partie, paquet):
    vieille = partie(7, 321)
    r = banc("function (L, o) {" + OUTILS + """
        o.tape('KeyE', 1);
        o.tape('KeyS', 1);
        const choisie = ici(L);
        o.tape('KeyE', 1);
        const neuve = { etat: L.B.etat, jour: L.B.partie.jour, argent: L.B.partie.argent,
                        ouverture: !!(L.B.scene || L.B.ouverture) };
        L.Histoire.passerOuverture();
        L.Missions.sauvegarderPartie();
        const ecrite = JSON.parse(o.store['bandini-partie-v1-2']);
        return { choisie: choisie, neuve: neuve, un: o.store['bandini-partie-v1'], actif: o.store['bandini-emplacement-v1'],
                 jourEcrit: ecrite.jour, date: typeof ecrite.sauveeLe, dateEnMemoire: 'sauveeLe' in L.B.partie,
                 maintenant: Date.now(), ecriteLe: ecrite.sauveeLe };
    }""", stockage={UN: vieille})
    assert r["choisie"] == "2  NOUVELLE PARTIE"
    assert r["neuve"] == {"etat": "jeu", "jour": 1, "argent": paquet["economie"]["argent_depart"], "ouverture": True}
    assert r["jourEcrit"] == 1 and r["actif"] == "2", "elle s'ecrit dans la 2, et la 2 devient la derniere jouee"
    assert r["un"] == vieille, "la partie 1 n'a pas bouge d'un octet"
    assert r["date"] == "number" and abs(r["maintenant"] - r["ecriteLe"]) < 60_000
    assert r["dateEnMemoire"] is False, "l'horloge murale part avec la copie ecrite, pas dans l'etat du jeu"


def test_changer_de_partie_apres_avoir_joue_recharge_la_page_et_rouvre_le_choix(banc, partie):
    un, deux = partie(7, 321), partie(12, 4300)
    avant = banc("function (L, o) {" + OUTILS + """
        o.tape('KeyE', 1); o.tape('KeyE', 1);                 // on joue la 1
        quitterVersLeTitre(L, o);
        o.tape('KeyE', 1); o.tape('KeyE', 1);                 // et on la reprend : meme ville
        const reprise = { etat: L.B.etat, jour: L.B.partie.jour, rechargements: o.rechargements() };
        quitterVersLeTitre(L, o);
        o.tape('KeyE', 1); o.tape('KeyS', 1);
        const choisie = ici(L);
        o.tape('KeyE', 1);                                    // la 2, dans une ville posee pour la 1
        return { reprise: reprise, choisie: choisie, etat: L.B.etat, jour: L.B.partie.jour, menu: !!L.B.menu,
                 rechargements: o.rechargements(), store: o.store, session: o.session };
    }""", stockage={UN: un, DEUX: deux})
    assert avant["reprise"] == {"etat": "jeu", "jour": 7, "rechargements": 0}, "reprendre la MEME partie ne recharge rien"
    assert avant["choisie"] == "2  JOUR 12 · 4300 $"
    assert avant["rechargements"] == 1, "une ville posee pour la 1 ne sert pas a la 2"
    assert avant["etat"] == "titre" and avant["jour"] == 7, "la 2 ne se joue PAS dans la ville de la 1"
    assert avant["store"][ACTIF] == "2" and avant["session"][ROUVRIR] == "2"
    assert avant["store"][DEUX] == deux

    apres = banc("function (L, o) {" + OUTILS + """
        const rouvert = { titre: L.B.menu && L.B.menu.titre, ici: ici(L), voile: L.Hud.voileCourant,
                          drapeau: 'bandini-rouvrir-parties' in o.session };
        o.tape('KeyE', 1);
        return { rouvert: rouvert, etat: L.B.etat, jour: L.B.partie.jour, rechargements: o.rechargements() };
    }""", stockage=avant["store"], session=avant["session"])
    assert apres["rouvert"] == {"titre": "PARTIES", "ici": "2  JOUR 12 · 4300 $", "voile": None, "drapeau": False}, (
        "au retour, le choix est deja ouvert sur la partie prise — et le drapeau ne sert qu'une fois"
    )
    assert apres["etat"] == "jeu" and apres["jour"] == 12 and apres["rechargements"] == 0

    # ⚠️ Et si la case prise est VIDE : le choix se rouvre sur ELLE, pas sur la
    # premiere partie qui existe (Chromium l'a attrape, le banc n'y pensait pas).
    vide = banc("function (L, o) {" + OUTILS + """
        return { ici: ici(L), jour: L.B.partie.jour };
    }""", stockage={UN: un, ACTIF: "2"}, session={ROUVRIR: "2"})
    assert vide == {"ici": "2  NOUVELLE PARTIE", "jour": 1}


def test_effacer_demande_et_n_efface_que_celle_la(banc, partie):
    un, deux, trois = partie(7, 321), partie(12, 4300), partie(3, 90)
    r = banc("function (L, o) {" + OUTILS + """
        o.tape('KeyE', 1);
        aller(L, o, 'EFFACER UNE PARTIE'); o.tape('KeyE', 1);
        const liste = { titre: L.B.menu.titre, libelles: libelles(L) };
        o.tape('KeyS', 1); o.tape('KeyE', 1);                  // la 2
        const question = { titre: L.B.menu.titre, ici: ici(L) };
        o.tape('KeyE', 1);                                    // un ACTION de trop : NON
        const garde = { titre: L.B.menu.titre, deux: o.store['bandini-partie-v1-2'] };
        aller(L, o, 'EFFACER UNE PARTIE'); o.tape('KeyE', 1);
        o.tape('KeyS', 1); o.tape('KeyE', 1);
        o.tape('Space', 1);                                   // FRAPPE : on recule, on n'efface pas
        const recule = { titre: L.B.menu.titre, deux: o.store['bandini-partie-v1-2'] };
        o.tape('KeyE', 1);                                    // la 2 encore (le curseur n'a pas bouge)
        o.tape('KeyS', 1); o.tape('KeyE', 1);                  // OUI
        return { liste: liste, question: question, garde: garde, recule: recule,
                 titre: L.B.menu.titre, ici: ici(L), store: o.store };
    }""", stockage={UN: un, DEUX: deux, TROIS: trois})
    assert r["liste"]["titre"] == "EFFACER QUELLE PARTIE?"
    assert r["liste"]["libelles"] == ["1  JOUR 7 · 321 $", "2  JOUR 12 · 4300 $", "3  JOUR 3 · 90 $", "RETOUR"]
    assert r["question"] == {"titre": "EFFACER LA PARTIE 2?", "ici": "NON, LA GARDER"}, "le curseur s'ouvre sur NON"
    assert r["garde"] == {"titre": "PARTIES", "deux": deux}
    assert r["recule"] == {"titre": "EFFACER QUELLE PARTIE?", "deux": deux}
    assert r["titre"] == "PARTIES" and r["ici"] == "2  NOUVELLE PARTIE", "on revient sur la place liberee"
    assert DEUX not in r["store"]
    assert r["store"][UN] == un and r["store"][TROIS] == trois, "les deux autres n'ont pas bouge d'un octet"


def test_effacer_la_partie_chargee_ne_la_laisse_pas_revenir(banc, partie):
    """⚠️ La partie effacee est encore dans `B.partie`. Si elle y restait, la
    sauvegarde automatique la reecrirait dix secondes plus tard — et une partie
    neuve dans la meme case se jouerait dans la ville de l'ancienne."""
    un = partie(7, 321)
    effacer = """
        o.tape('KeyE', 1);
        aller(L, o, 'EFFACER UNE PARTIE'); o.tape('KeyE', 1);
        o.tape('KeyE', 1);                                    // la 1
        o.tape('KeyS', 1); o.tape('KeyE', 1);                  // OUI
    """
    sans_ville = banc("function (L, o) {" + OUTILS + effacer + """
        const memoire = L.B.partie.jour;
        o.tape('KeyE', 1);                                    // 1  NOUVELLE PARTIE
        const joue = { etat: L.B.etat, jour: L.B.partie.jour, rechargements: o.rechargements() };
        L.Histoire.passerOuverture();
        L.Missions.sauvegarderPartie();
        return { memoire: memoire, joue: joue, ecrite: JSON.parse(o.store['bandini-partie-v1']).jour };
    }""", stockage={UN: un})
    assert sans_ville["memoire"] == 1, "effacer la partie chargee la remplace en memoire, tout de suite"
    assert sans_ville["joue"] == {"etat": "jeu", "jour": 1, "rechargements": 0}
    assert sans_ville["ecrite"] == 1, "la sauvegarde ecrit la partie neuve, pas l'effacee"

    apres_avoir_joue = banc("function (L, o) {" + OUTILS + """
        o.tape('KeyE', 1); o.tape('KeyE', 1);
        quitterVersLeTitre(L, o);
    """ + effacer + """
        o.tape('KeyE', 1);                                    // 1  NOUVELLE PARTIE, dans la ville de l'ancienne
        return { etat: L.B.etat, rechargements: o.rechargements(), existe: 'bandini-partie-v1' in o.store };
    }""", stockage={UN: un})
    assert apres_avoir_joue == {"etat": "titre", "rechargements": 1, "existe": False}


def test_copier_recopie_a_l_octet_et_demande_avant_d_ecraser(banc, partie):
    un, trois = partie(7, 321), partie(3, 90)
    r = banc("function (L, o) {" + OUTILS + """
        o.tape('KeyE', 1);
        aller(L, o, 'COPIER UNE PARTIE'); o.tape('KeyE', 1);
        const quelle = { titre: L.B.menu.titre, ici: ici(L) };
        o.tape('KeyE', 1);                                    // la 1
        const vers = { titre: L.B.menu.titre, libelles: libelles(L),
                       details: L.B.menu.items.map(function (i) { return i.detail || ''; }) };
        o.tape('KeyE', 1);                                    // vers la 2, vide : pas de question
        const copiee = { titre: L.B.menu.titre, ici: ici(L), deux: o.store['bandini-partie-v1-2'] };
        aller(L, o, 'COPIER UNE PARTIE'); o.tape('KeyE', 1);
        o.tape('KeyE', 1);                                    // la 1
        o.tape('KeyS', 1); o.tape('KeyE', 1);                  // vers la 3, pleine
        const question = { titre: L.B.menu.titre, ici: ici(L) };
        o.tape('KeyE', 1);                                    // NON
        const gardee = o.store['bandini-partie-v1-3'];
        aller(L, o, 'COPIER UNE PARTIE'); o.tape('KeyE', 1);
        o.tape('KeyE', 1); o.tape('KeyS', 1); o.tape('KeyE', 1);
        o.tape('KeyS', 1); o.tape('KeyE', 1);                  // OUI
        return { quelle: quelle, vers: vers, copiee: copiee, question: question, gardee: gardee,
                 store: o.store, ici: ici(L) };
    }""", stockage={UN: un, TROIS: trois})
    assert r["quelle"] == {"titre": "COPIER QUELLE PARTIE?", "ici": "1  JOUR 7 · 321 $"}
    assert r["vers"]["titre"] == "COPIER LA 1 VERS"
    assert r["vers"]["libelles"] == ["2  VIDE", "3  JOUR 3 · 90 $", "RETOUR"], "on ne se copie pas sur soi-meme"
    assert r["vers"]["details"] == ["", "ÉCRASÉE", ""]
    assert r["copiee"] == {"titre": "PARTIES", "ici": "2  JOUR 7 · 321 $", "deux": un}, "copiee a l'octet"
    assert r["question"] == {"titre": "ÉCRASER LA PARTIE 3?", "ici": "NON, LA GARDER"}
    assert r["gardee"] == trois
    assert r["store"][TROIS] == un and r["store"][UN] == un and r["ici"] == "3  JOUR 7 · 321 $"


def test_copier_par_dessus_la_partie_chargee_la_remplace_en_memoire(banc, partie):
    un, deux = partie(7, 321), partie(12, 4300)
    r = banc("function (L, o) {" + OUTILS + """
        o.tape('KeyE', 1);
        aller(L, o, 'COPIER UNE PARTIE'); o.tape('KeyE', 1);
        o.tape('KeyS', 1); o.tape('KeyE', 1);                  // la 2
        o.tape('KeyE', 1);                                    // vers la 1, pleine
        o.tape('KeyS', 1); o.tape('KeyE', 1);                  // OUI
        const memoire = L.B.partie.jour;
        aller(L, o, '1  '); o.tape('KeyE', 1);
        const joue = { etat: L.B.etat, jour: L.B.partie.jour };
        L.Missions.sauvegarderPartie();
        return { memoire: memoire, joue: joue, ecrite: JSON.parse(o.store['bandini-partie-v1']).jour };
    }""", stockage={UN: un, DEUX: deux})
    assert r["memoire"] == 12, "la partie chargee est remplacee par la copie"
    assert r["joue"] == {"etat": "jeu", "jour": 12}
    assert r["ecrite"] == 12, "l'ancienne partie 1, restee en memoire, ne se reecrit pas par-dessus la copie"


def test_les_listes_s_ouvrent_sur_une_partie_qui_existe(banc, partie):
    """Une case vide est grisee : un curseur pose dessus n'a l'air de rien
    choisir, et ACTION n'y rend qu'un bip."""
    r = banc("function (L, o) {" + OUTILS + """
        o.tape('KeyE', 1);
        const parties = ici(L);
        aller(L, o, 'COPIER UNE PARTIE'); o.tape('KeyE', 1);
        const copier = ici(L);
        o.tape('Space', 1);
        aller(L, o, 'EFFACER UNE PARTIE'); o.tape('KeyE', 1);
        return { parties: parties, copier: copier, effacer: ici(L) };
    }""", stockage={TROIS: partie(3, 90)})
    assert r == {"parties": "3  JOUR 3 · 90 $", "copier": "3  JOUR 3 · 90 $", "effacer": "3  JOUR 3 · 90 $"}


def test_on_choisit_sa_partie_a_la_manette(banc, partie):
    """La croix de Martin est un AXE (8BitDo en Bluetooth) : le stick du banc fait pareil."""
    un, deux = partie(7, 321), partie(12, 4300)
    r = banc("""function (L, o) {
        // ⚠️ Chaque appui TENU deux images : la boucle avance a pas fixe, et un
        // appui d'une seule image tombe parfois entre deux pas.
        o.pad([0, 0], [1, 0]); o.frame(2); o.pad([0, 0], [0, 0]); o.frame(2);   // ACTION
        const titre = L.B.menu && L.B.menu.titre;
        o.pad([0, 0.9], [0, 0]); o.frame(2); o.pad([0, 0], [0, 0]); o.frame(2);  // BAS
        const ici = L.B.menu.items[L.B.menu.curseur].libelle;
        o.pad([0, 0], [1, 0]); o.frame(2); o.pad(null); o.frame(1);              // ACTION
        return { titre: titre, ici: ici, etat: L.B.etat, jour: L.B.partie.jour };
    }""", stockage={UN: un, DEUX: deux})
    assert r == {"titre": "PARTIES", "ici": "2  JOUR 12 · 4300 $", "etat": "jeu", "jour": 12}


def test_choisir_sa_partie_a_la_manette_dit_que_le_son_attend(banc, partie):
    """La manette n'est pas un geste pour le navigateur : commencer au pad, c'est
    commencer muet. Le titre le disait ; le choix des parties est devenu l'endroit
    ou l'on commence, il doit le dire a son tour."""
    r = banc("""function (L, o) {
        o.brancherAudio(false);
        L.Son.sonder();
        o.pad([0, 0], [1, 0]); o.frame(2); o.pad([0, 0], [0, 0]); o.frame(2);
        const auTitre = L.B.msg;
        // Le message se lit A L'IMAGE ou la partie commence : une image plus tard,
        // la ville a deja pu parler par-dessus (les hommes de Sal, au jour 7).
        o.pad([0, 0], [1, 0]);
        for (let k = 0; k < 3 && L.B.etat !== 'jeu'; k++) o.frame(1);
        return { auTitre: auTitre, etat: L.B.etat, msg: L.B.msg };
    }""", stockage={UN: partie(7, 321)})
    assert r["auTitre"] is None, "le choix s'ouvre : on ne joue pas encore, rien a dire"
    assert r["etat"] == "jeu" and r["msg"] == "SON EN ATTENTE — TOUCHE L'ÉCRAN"


def test_la_date_se_dit_comme_on_la_dit(banc):
    r = banc("""function (L, o) {
        const maintenant = new Date(2026, 8, 16, 22, 5).getTime();
        return [new Date(2026, 8, 16, 9, 7).getTime(), new Date(2026, 8, 15, 23, 59).getTime(),
                new Date(2026, 7, 31, 21, 40).getTime()].map(function (t) { return L.Hud.quand(t, maintenant); })
          .concat([L.Hud.tempsDeJeu(25 * 60 + 59), L.Hud.tempsDeJeu(3 * 3600 + 5 * 60)]);
    }""")
    assert r == ["AUJOURD'HUI À 9 H 07", "HIER À 23 H 59", "LE 31 AOÛT À 21 H 40", "25 MIN", "3 H 05"]
