"""Le compte vu du JEU (M14, 2e vague) : ce qui monte, ce qui descend, ce qu'on demande.

La 1re vague a livre le serveur (`test_comptes.py`, `test_bd.py`) ; ici, c'est
`static/js/compte.js` sous le banc Node, avec un faux `/api/compte/` qu'on
programme reponse par reponse (`reseau=`).

⚠️ La regle que chaque juge de ce fichier protege : **un compte est un confort**.
Serveur eteint, session coupee, deux versions en desaccord — le jeu arrive au
titre et se joue. Rien ici ne doit jamais barrer le chemin de JOUER.
"""

import json

#: Une partie d'ici, telle que `Sauvegarde` la garde.
def partie(jour=5, argent=1200, secondes=600, missions=1, sauvee_le=1_750_000_000_000):
    return {"jour": jour, "argent": argent, "x": 100, "y": 100,
            "stats": {"secondes": secondes},
            "missionsFaites": {f"m{i}": 1 for i in range(missions)},
            "sauveeLe": sauvee_le}


def apercu(jour=5, argent=1200, secondes=600, missions=1):
    return {"jour": jour, "argent": argent, "secondes": secondes, "missions": missions}


def stockage(cases=None, compteurs=None, sync=None):
    """Ce que le navigateur gardait AVANT le chargement."""
    out = {}
    for n, p in (cases or {}).items():
        out["bandini-partie-v1" if n == 1 else f"bandini-partie-v1-{n}"] = json.dumps(p)
    if compteurs:
        out["bandini-compteur-v1"] = json.dumps({str(n): v for n, v in compteurs.items()})
    if sync:
        out["bandini-compte-sync-v1"] = json.dumps(sync)
    return out


def ouvert(parties=(), pseudo="martin"):
    """La reponse de `POST /api/compte/ouvrir` quand cet appareil porte un compte."""
    return {"statut": 200, "corps": {"compte": {"pseudo": pseudo, "parties": list(parties)}}}


def case(n, compteur=0, apercu_=None, sauvee_le="2026-09-17T20:00:00Z"):
    return {"emplacement": n, "compteur": compteur, "sauvee_le": sauvee_le, "apercu": apercu_}


#: Laisse la file du compte se vider : chaque appel est une promesse de plus.
CALME = """
      function calme(o, n) {
        let p = Promise.resolve();
        for (let i = 0; i < (n || 8); i++) p = p.then(function () { return o.attendre(); });
        return p;
      }
"""


# --- Personne n'a de compte : le jeu ne change pas d'un poil ---------------------------


def test_sans_compte_le_jeu_arrive_au_titre_et_se_tait(banc):
    """⚠️ Le juge le plus important du fichier : l'ouverture part, le serveur dit
    « personne », et plus rien ne bouge. Un jeu qui bavarde avec le serveur alors
    que personne n'a de compte est un jeu qui a oublie qu'il se joue hors ligne."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          return { etat: L.B.etat, compte: L.Compte.etat().etat,
                   appels: o.compte.appels.map(function (a) { return a.chemin; }),
                   bouton: o.elements['bouton-compte'].textContent };
        });
    }""")
    assert r["etat"] == "titre"
    assert r["compte"] == "ferme"
    assert r["appels"] == ["ouvrir"]


def test_serveur_eteint_le_jeu_joue_quand_meme(banc):
    """⚠️ `fetch` qui part en erreur (wifi coupe, serveur mort) : on le dit a
    l'ecran, et on ne casse rien. C'est le cas du salon un soir de panne."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          return { etat: L.B.etat, compte: L.Compte.etat().etat,
                   mot: o.elements['compte-mot'].textContent,
                   parties: o.elements['compte-parties'].enfants.length };
        });
    }""", reseau={"*": {"panne": True}})
    assert r["etat"] == "titre"
    assert r["compte"] == "hors-ligne"
    assert "Pas de réseau" in r["mot"]
    assert r["parties"] == 0


def test_la_base_tombee_ne_tombe_pas_sur_le_jeu(banc):
    """503 : `bd.Indisponible` cote serveur. Le compte le dit, la ville tourne."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          return { etat: L.B.etat, compte: L.Compte.etat().etat, mot: o.elements['compte-mot'].textContent };
        });
    }""", reseau={"ouvrir": {"statut": 503, "corps": {"erreur": "les comptes sont indisponibles pour l'instant"}}})
    assert r["etat"] == "titre"
    assert r["compte"] == "indisponible"
    assert "indisponibles" in r["mot"]


# --- L'ouverture passe en premier, et seule --------------------------------------------


def test_rien_ne_double_l_ouverture(banc):
    """⚠️ LE PIEGE DE LA 1re VAGUE, cote jeu. `POST /api/compte/ouvrir` tourne le
    jeton d'appareil ; un appel de compte parti AVANT sa reponse arriverait avec
    un jeton deja remplace et passerait pour un vol — tous les appareils coupes.
    La file est ce qui l'empeche, et c'est une CONNEXION qui le prouve : elle
    n'attend pas d'etre « ouvert » pour partir. Sans la file, elle double
    l'ouverture."""
    r = banc("""function (L, o) {""" + CALME + """
        const entre = L.Compte.connecter({ pseudo: 'martin', mot_de_passe: 'un-mot-de-passe' });
        return calme(o, 4).then(function () {
          // L'ouverture est encore en vol : rien d'autre n'est parti.
          const pendant = o.compte.appels.map(function (a) { return a.chemin; });
          o.compte.rendre('ouvrir');
          return calme(o).then(function () { return entre; }).then(function () {
            return { pendant: pendant, apres: o.compte.appels.map(function (a) { return a.chemin; }) };
          });
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": {"tenu": True, "statut": 200, "corps": {"compte": None}},
                     "connexion": ouvert([case(1, 0), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 4}}})
    assert r["pendant"] == ["ouvrir"], "un appel de compte est parti avant la reponse de l'ouverture"
    assert r["apres"][:2] == ["ouvrir", "connexion"]


def test_une_montee_attend_de_savoir_a_qui_elle_parle(banc):
    """L'autre garde-fou, plus simple : tant que l'ouverture n'a pas repondu, on
    ne sait meme pas si cet appareil porte un compte — rien ne monte."""
    r = banc("""function (L, o) {""" + CALME + """
        const monte = L.Compte.monter(1);
        return calme(o, 4).then(function () {
          const pendant = o.compte.appels.map(function (a) { return a.chemin; });
          o.compte.rendre('ouvrir');
          return calme(o).then(function () { return monte; }).then(function () {
            return { pendant: pendant, apres: o.compte.appels.map(function (a) { return a.chemin; }) };
          });
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": dict(tenu=True, **ouvert([case(1, 0), case(2), case(3)])),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 4}}})
    assert r["pendant"] == ["ouvrir"]
    assert r["apres"] == ["ouvrir", "parties/1"]


# --- Le compteur, et ce qui monte ------------------------------------------------------


def test_chaque_sauvegarde_locale_avance_le_compteur(banc):
    """⚠️ Un compteur, jamais une horloge : deux appareils n'ont pas la meme
    heure, et c'est le seul ordre que le serveur comprend."""
    r = banc("""function (L, o) {
        const avant = L.Sauvegarde.compteur(1);
        L.Sauvegarde.ecrire({ jour: 6 }, 1);
        L.Sauvegarde.ecrire({ jour: 7 }, 1);
        const apres = L.Sauvegarde.compteur(1);
        L.Sauvegarde.effacer(2);
        return { avant: avant, apres: apres, efface: L.Sauvegarde.compteur(2),
                 garde: JSON.parse(o.store['bandini-compteur-v1'] || '{}') };
    }""", stockage=stockage(cases={1: partie()}, compteurs={1: 4}))
    assert r["avant"] == 4
    assert r["apres"] == 6, "deux sauvegardes, deux crans"
    assert r["efface"] == 1, "une case videe garde un compteur QUI AVANCE"
    assert r["garde"]["1"] == 6


def test_une_partie_d_avant_le_compteur_ne_passe_pas_pour_une_case_vide(banc):
    """⚠️ La partie de Martin est la depuis des semaines et n'a pas de compteur.
    A zero, elle passerait pour une case vide, et la premiere connexion la
    remplacerait par celle du compte sans rien demander."""
    r = banc("""function (L, o) {
        return { un: L.Sauvegarde.compteur(1), deux: L.Sauvegarde.compteur(2) };
    }""", stockage=stockage(cases={1: partie()}))
    assert r["un"] == 1
    assert r["deux"] == 0, "une case vide reste a zero : c'est ce qui dit qu'il n'y a rien ici"


def test_l_instantane_qui_monte_est_celui_qui_est_ecrit(banc):
    """Octet pour octet : ce que le serveur recoit est ce que `Sauvegarde` garde."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Sauvegarde.ecrire(L.Sauvegarde.completer(L.Sauvegarde.lire(1), L.B.defs), 1);
          return L.Compte.monter(1);
        }).then(function () {
          const envoi = o.compte.appels.filter(function (a) { return a.chemin === 'parties/1'; }).pop();
          return { corps: envoi.corps, methode: envoi.methode,
                   local: JSON.parse(o.store['bandini-partie-v1']),
                   compteur: L.Sauvegarde.compteur(1), empreinte: L.B.defs.empreinte };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": ouvert([case(1, 5, apercu()), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 6,
                                                            "sauvee_le": "2026-09-17T21:00:00Z"}}})
    assert r["methode"] == "POST", "sendBeacon ne sait faire que POST : les deux chemins sont les memes"
    assert r["corps"]["compteur"] == r["compteur"] == 5
    assert r["corps"]["partie"] == r["local"], "ce qui monte est ce qui est ecrit"
    assert r["corps"]["empreinte"] == r["empreinte"]


def test_rien_ne_remonte_deux_fois(banc):
    """⚠️ La partie se sauve toutes les dix secondes ; le serveur n'a pas besoin
    de les voir toutes. Une montee sans rien de neuf ne part pas."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.monter(1); })
          .then(function () { return L.Compte.monter(1); })
          .then(function () { return calme(o); })
          .then(function () {
            return o.compte.appels.filter(function (a) { return a.chemin === 'parties/1'; }).length;
          });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": ouvert([case(1, 3, apercu()), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 4}}})
    assert r == 1


def test_effacer_une_case_la_vide_aussi_sur_le_compte(banc):
    """⚠️ `partie: null` — et le compteur avance, sinon la vieille copie du
    serveur reviendrait remplir la case qu'on vient de vider."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Jeu.effacerPartie(1);
          return L.Compte.monter(1);
        }).then(function () {
          const envoi = o.compte.appels.filter(function (a) { return a.chemin === 'parties/1'; }).pop();
          return { corps: envoi.corps, compteur: L.Sauvegarde.compteur(1) };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4},
                               sync={"compte": "martin", "cases": {"1": {"envoye": 4, "serveur": 4}}}),
             reseau={"ouvrir": ouvert([case(1, 4, apercu()), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 5}}})
    assert r["corps"]["partie"] is None
    assert r["corps"]["compteur"] == 5 == r["compteur"]


def test_le_retour_au_titre_met_le_compte_a_jour(banc):
    """⚠️ Un des trois moments qui comptent : on vient de reposer la manette, et
    c'est la que la partie doit etre sur le compte — pas dans une minute et
    demie. Le repos de `apresEcriture` a deja servi : seul le retour au titre
    peut expliquer la seconde montee."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          // La premiere ecriture monte ; la seconde tombe dans le repos.
          L.Sauvegarde.ecrire({ jour: 8, argent: 40, stats: { secondes: 20 } }, 1);
          return calme(o);
        }).then(function () {
          const avant = o.compte.appels.filter(function (a) { return a.chemin === 'parties/1'; }).length;
          L.Sauvegarde.ecrire({ jour: 9, argent: 50, stats: { secondes: 30 } }, 1);
          L.Jeu.retourTitre();
          return calme(o).then(function () {
            const envoi = o.compte.appels.filter(function (a) { return a.chemin === 'parties/1'; });
            return { avant: avant, apres: envoi.length, dernier: envoi[envoi.length - 1].corps.partie.jour };
          });
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4},
                               sync={"compte": "martin", "cases": {"1": {"envoye": 4, "serveur": 4}}}),
             reseau={"ouvrir": ouvert([case(1, 4, apercu()), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 6}}})
    assert r["avant"] == 1
    assert r["apres"] == 2, "le retour au titre monte la partie qu'on vient de jouer"
    # ⚠️ `retourTitre` sauvegarde d'abord : ce qui monte est la partie du jeu,
    # pas celle qu'on avait ecrite a la main juste avant.
    assert r["dernier"] >= 1


# --- Ce qui se decide tout seul --------------------------------------------------------


def test_une_case_vide_ici_recoit_la_partie_du_compte(banc):
    """« commencer au telephone et finir a l'ordi » : sur l'ordi, la case est
    vide et il n'y a rien a perdre — elle descend sans qu'on demande rien.

    ⚠️ Elle descend TELLE QUELLE : sa date de sauvegarde est celle du telephone,
    et le compteur local se pose sur celui du serveur. Redatee a maintenant, elle
    repartirait aussitot vers le serveur comme une version plus neuve."""
    servie = partie(jour=18, argent=9000, secondes=12000, sauvee_le=1_700_000_000_000)
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          return { local: JSON.parse(o.store['bandini-partie-v1'] || 'null'),
                   compteur: L.Sauvegarde.compteur(1), jour: L.B.partie.jour,
                   appels: o.compte.appels.map(function (a) { return a.chemin; }) };
        });
    }""",
             reseau={"ouvrir": ouvert([case(1, 7, apercu(jour=18, argent=9000, secondes=12000)), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 7,
                                                            "partie": servie, "empreinte": ""}}})
    assert r["local"] == servie, "la partie du serveur arrive telle quelle"
    assert r["compteur"] == 7
    assert r["jour"] == 18, "et la partie chargee au titre devient celle-la"
    assert r["appels"] == ["ouvrir", "parties/1"]


def test_une_case_vide_sur_le_compte_recoit_la_partie_d_ici(banc):
    """L'autre sens, tout aussi silencieux : le serveur n'a rien dans cette case."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          const envoi = o.compte.appels.filter(function (a) { return a.chemin === 'parties/1'; }).pop();
          return { envoi: envoi ? envoi.corps.compteur : null, decision: L.Compte.decision(1) };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": ouvert([case(1, 0), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 4}}})
    assert r["envoi"] == 4
    assert r["decision"] == "rien", "une fois montee, la case est d'accord des deux cotes"


def test_jouer_depuis_la_version_du_serveur_ne_pose_aucune_question(banc):
    """Le cas de tous les jours : un seul appareil, qui joue et qui monte. Le
    temoin dit que ma partie descend de celle du serveur — elle monte, point."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return { decision: L.Compte.decision(1), conflit: L.Compte.conflit(1) }; });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 9},
                               sync={"compte": "martin", "cases": {"1": {"envoye": 6, "serveur": 6}}}),
             reseau={"ouvrir": ouvert([case(1, 6, apercu()), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 9}}})
    assert r["decision"] == "rien"
    assert r["conflit"] is None


# --- Et ce que le joueur tranche -------------------------------------------------------


def test_deux_versions_sans_temoin_se_demandent(banc):
    """⚠️ Un appareil qui se connecte a un compte alors qu'il a deja des parties :
    rien ne dit laquelle vient de l'autre. Ecraser en silence serait perdre une
    soiree de jeu — on demande, une fois."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          const m = L.Hud.menuParties();
          return { decision: L.Compte.decision(1), detail: m.items[0].detail, aide: m.aide,
                   local: JSON.parse(o.store['bandini-partie-v1']),
                   appels: o.compte.appels.map(function (a) { return a.chemin; }) };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": ouvert([case(1, 9, apercu(jour=18, argent=9000, secondes=12000)), case(2), case(3)])})
    assert r["decision"] == "trancher"
    assert r["appels"] == ["ouvrir"], "on ne touche a rien tant que le joueur n'a pas tranche"
    assert r["local"]["jour"] == 5, "la partie d'ici n'a pas bouge"
    assert r["detail"] == "DEUX VERSIONS"
    assert "TON COMPTE" in r["aide"]


def test_le_refus_du_serveur_devient_une_question_jamais_une_fusion(banc):
    """409 : le serveur rend la sienne et ne fusionne rien. Le jeu non plus."""
    servie = partie(jour=18, argent=9000, secondes=12000)
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.monter(1); }).then(function (res) {
          return { res: res, decision: L.Compte.decision(1), conflit: L.Compte.conflit(1),
                   local: JSON.parse(o.store['bandini-partie-v1']) };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": ouvert([case(1, 0), case(2), case(3)]),
                     "parties/1": {"statut": 409, "corps": {"erreur": "la partie du serveur est plus avancée",
                                                            "serveur": {"emplacement": 1, "compteur": 12,
                                                                        "partie": servie, "empreinte": ""}}}})
    assert r["res"]["conflit"] is True
    assert r["decision"] == "trancher"
    assert r["local"]["jour"] == 5, "rien ne s'ecrase par-dessus la partie d'ici"
    assert r["conflit"]["serveur"]["jour"] == 18


def test_une_reponse_qu_on_ne_comprend_pas_n_efface_rien(banc):
    """⚠️ Un 200 sans le champ `partie` (un proxy, une page d'erreur en JSON) :
    la case d'ici reste ou elle est. Le contraire s'appelle perdre une partie."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.prendre(1); }).then(function () {
          return { local: JSON.parse(o.store['bandini-partie-v1'] || 'null'), compteur: L.Sauvegarde.compteur(1) };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4},
                               sync={"compte": "martin", "cases": {"1": {"envoye": 4, "serveur": 4}}}),
             reseau={"ouvrir": ouvert([case(1, 4, apercu()), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"bonjour": "je ne suis pas le serveur"}}})
    assert r["local"]["jour"] == 5
    assert r["compteur"] == 4


def test_prendre_celle_du_compte(banc):
    """Le joueur a tranche : la partie du serveur descend, et elle repart de son
    compteur a lui — sinon la prochaine sauvegarde se ferait refuser."""
    servie = partie(jour=18, argent=9000, secondes=12000, sauvee_le=1_700_000_000_000)
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          const m = L.Hud.menuVersions(1);
          m.items[1].faire();
          return calme(o);
        }).then(function () {
          return { local: JSON.parse(o.store['bandini-partie-v1']), compteur: L.Sauvegarde.compteur(1),
                   jour: L.B.partie.jour, decision: L.Compte.decision(1) };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": ouvert([case(1, 9, apercu(jour=18, argent=9000, secondes=12000)), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 9,
                                                            "partie": servie, "empreinte": ""}}})
    assert r["local"] == servie
    assert r["compteur"] == 9
    assert r["jour"] == 18, "au titre, la partie chargee suit"
    assert r["decision"] == "rien"


def test_garder_celle_d_ici_passe_par_dessus(banc):
    """L'autre choix : la mienne monte AU-DESSUS du compteur du serveur. C'est le
    seul endroit du jeu qui passe par-dessus un refus, et il vient d'un geste."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.menuVersions(1).items[0].faire();
          return calme(o);
        }).then(function () {
          const envoi = o.compte.appels.filter(function (a) { return a.chemin === 'parties/1'; }).pop();
          return { corps: envoi.corps, compteur: L.Sauvegarde.compteur(1), decision: L.Compte.decision(1) };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": ouvert([case(1, 9, apercu(jour=18, argent=9000)), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 10}}})
    assert r["corps"]["compteur"] == 10, "au-dessus des 9 du serveur"
    assert r["corps"]["partie"]["jour"] == 5, "celle d'ici"
    assert r["compteur"] == 10, "le compteur local suit, sinon la suivante se ferait refuser"
    assert r["decision"] == "rien"


def test_une_partie_en_cours_ne_se_remplace_pas_sous_les_pieds(banc):
    """⚠️ La case est vide ici et pleine sur le compte : elle descend toute seule.
    Mais la reponse met une seconde a venir, et pendant ce temps on a presse
    JOUER. La poser maintenant, c'est la faire ecraser dix secondes plus tard par
    la sauvegarde automatique de la partie neuve — l'autre appareil aurait perdu
    sa soiree sans que personne ne comprenne. Elle attend le titre, en question."""
    servie = partie(jour=18, argent=9000, secondes=12000)
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o, 3).then(function () {
          L.Jeu.jouerPartie(1);
          o.frame(2);
          o.compte.rendre('parties/1');
          return calme(o);
        }).then(function () {
          return { etat: L.B.etat, jour: L.B.partie.jour,
                   local: JSON.parse(o.store['bandini-partie-v1'] || 'null'),
                   conflit: !!L.Compte.conflit(1) };
        });
    }""",
             reseau={"ouvrir": ouvert([case(1, 7, apercu(jour=18, argent=9000, secondes=12000)), case(2), case(3)]),
                     "parties/1": {"tenu": True, "statut": 200,
                                   "corps": {"emplacement": 1, "compteur": 7, "partie": servie, "empreinte": ""}}})
    assert r["etat"] == "jeu"
    assert r["jour"] == 1, "la partie neuve qu'on joue reste celle qu'on joue"
    assert r["local"] is None or r["local"]["jour"] != 18, "rien ne s'ecrit par-dessus la case jouee"
    assert r["conflit"] is True, "elle devient une question, posee au retour au titre"


def test_au_retour_au_titre_la_partie_qui_attendait_est_proposee(banc):
    """La suite de l'histoire : on repose la manette, on revient au titre, et la
    version qui n'avait pas pu se poser est la, en question. ⚠️ Elle ne descend
    toujours pas toute seule — on a joue depuis, et c'est au joueur de dire
    laquelle des deux il garde."""
    servie = partie(jour=18, argent=9000, secondes=12000)
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o, 3).then(function () {
          L.Jeu.jouerPartie(1);
          o.frame(2);
          o.compte.rendre('GET parties/1');
          return calme(o);
        }).then(function () {
          L.Jeu.retourTitre();
          return calme(o);
        }).then(function () {
          const attente = { decision: L.Compte.decision(1), local: JSON.parse(o.store['bandini-partie-v1']).jour,
                            detail: L.Hud.menuParties().items[0].detail };
          L.Hud.menuVersions(1).items[1].faire();
          return calme(o).then(function () {
            attente.apres = JSON.parse(o.store['bandini-partie-v1']);
            attente.appels = o.compte.appels.map(function (a) { return a.methode + ' ' + a.chemin; });
            return attente;
          });
        });
    }""",
             reseau={"ouvrir": ouvert([case(1, 7, apercu(jour=18, argent=9000, secondes=12000)), case(2), case(3)]),
                     "GET parties/1": {"tenu": True, "statut": 200,
                                       "corps": {"emplacement": 1, "compteur": 7, "partie": servie, "empreinte": ""}},
                     # La sauvegarde du retour au titre part avec un compteur de
                     # partie neuve : le vrai serveur la refuse et rend la sienne.
                     "POST parties/1": {"statut": 409, "corps": {"erreur": "la partie du serveur est plus avancée",
                                                                 "serveur": {"emplacement": 1, "compteur": 7,
                                                                             "partie": servie, "empreinte": ""}}}})
    assert r["decision"] == "trancher", "la question attend au titre"
    assert r["local"] == 1, "et rien n'a encore ete remplace"
    assert r["detail"] == "DEUX VERSIONS"
    assert r["apres"] == servie, "le joueur tranche, et celle du compte se pose enfin"
    assert r["appels"].count("GET parties/1") == 1, "la partie etait deja en main : pas un GET de plus"


# --- L'onglet s'en va ------------------------------------------------------------------


def test_la_page_qui_s_en_va_envoie_la_partie(banc):
    """Le geste, pas la fonction : `pagehide` sur la fenetre, comme le navigateur
    le joue quand on ferme l'onglet ou qu'on change d'application."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Sauvegarde.ecrire({ jour: 9, argent: 50, stats: { secondes: 30 } }, 1);
          o.fenetreEvenement('pagehide', { persisted: false });
          return { beacons: o.compte.beacons.length, corps: (o.compte.beacons[0] || {}).corps };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4},
                               sync={"compte": "martin", "cases": {"1": {"envoye": 4, "serveur": 4}}}),
             reseau={"ouvrir": ouvert([case(1, 4, apercu()), case(2), case(3)])})
    assert r["beacons"] == 1
    assert r["corps"]["partie"]["jour"] == 9


def test_une_page_mise_de_cote_n_envoie_rien(banc):
    """⚠️ `persisted` : le navigateur RANGE la page (bfcache) — changer
    d'application sur telephone. Elle peut revenir ; rien ne part, et surtout
    pas le son qu'on refermerait pour rien."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Sauvegarde.ecrire({ jour: 9 }, 1);
          o.fenetreEvenement('pagehide', { persisted: true });
          return o.compte.beacons.length;
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4},
                               sync={"compte": "martin", "cases": {"1": {"envoye": 4, "serveur": 4}}}),
             reseau={"ouvrir": ouvert([case(1, 4, apercu()), case(2), case(3)])})
    assert r == 0


def test_le_beacon_porte_la_partie_et_son_compteur(banc):
    """Le depart de la page, joue comme le navigateur le joue."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Sauvegarde.ecrire({ jour: 9, argent: 50, stats: { secondes: 30 } }, 1);
          const parti = L.Compte.partir();
          const b = o.compte.beacons[0];
          return { parti: parti, url: b && b.url, type: b && b.type, corps: b && b.corps,
                   compteur: L.Sauvegarde.compteur(1) };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4},
                               sync={"compte": "martin", "cases": {"1": {"envoye": 4, "serveur": 4}}}),
             reseau={"ouvrir": ouvert([case(1, 4, apercu()), case(2), case(3)])})
    assert r["parti"] is True
    assert r["url"] == "/api/compte/parties/1"
    assert r["type"] == "application/json", "sans ce type, Flask ne lit pas le corps"
    assert r["corps"]["compteur"] == 5 == r["compteur"]
    assert r["corps"]["partie"]["jour"] == 9


def test_pas_de_beacon_sans_compte_ni_sur_une_case_a_trancher(banc):
    """⚠️ Un beacon dont personne ne lit la reponse ne doit JAMAIS partir sur une
    case en desaccord : il ecraserait celle de l'autre appareil sans un mot, et
    la question que le jeu s'apprete a poser n'aurait plus d'objet."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          return { parti: L.Compte.partir(), beacons: o.compte.beacons.length, decision: L.Compte.decision(1) };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": ouvert([case(1, 9, apercu(jour=18)), case(2), case(3)])})
    assert r["decision"] == "trancher"
    assert r["parti"] is False
    assert r["beacons"] == 0


# --- L'ecran ---------------------------------------------------------------------------


def test_l_ecran_du_compte_montre_les_trois_cases(banc):
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          const liste = o.elements['compte-parties'];
          L.Hud.majCompte();
          return { voile: !o.elements['voile-compte'].hidden, bouton: o.elements['bouton-compte'].textContent,
                   form: o.elements['compte-form'].hidden, partir: o.elements['bouton-compte-deconnexion'].hidden,
                   lignes: liste.enfants.map(function (li) { return li.enfants.map(function (s) { return s.textContent; }); }) };
        });
    }""",
             reseau={"ouvrir": ouvert([case(1, 9, apercu(jour=18, argent=9000)), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 9,
                                                            "partie": partie(jour=18, argent=9000), "empreinte": ""}}})
    assert r["voile"] is True
    assert r["bouton"] == "Compte : martin"
    assert r["form"] is True, "connecte, on ne redemande pas un mot de passe"
    assert r["partir"] is False
    assert len(r["lignes"]) == 3, "deux passes ne doivent pas empiler six lignes"
    assert r["lignes"][0][0] == "Partie 1 · jour 18 · 9000 $"
    assert r["lignes"][1][0] == "Partie 2 · vide"


def test_se_connecter_depuis_l_ecran(banc):
    """Le mot de passe LIE l'appareil, une fois — et il ne reste pas dans le champ."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          o.elements['compte-pseudo'].value = 'martin';
          o.elements['compte-passe'].value = 'un-mot-de-passe';
          return L.Hud.envoyerCompte('connexion');
        }).then(function () { return calme(o); }).then(function () {
          const appel = o.compte.appels.filter(function (a) { return a.chemin === 'connexion'; })[0];
          return { appel: appel, passe: o.elements['compte-passe'].value,
                   etat: o.elements['compte-etat'].textContent, compte: L.Compte.etat().etat,
                   bouton: o.elements['bouton-compte'].textContent };
        });
    }""",
             reseau={"ouvrir": {"statut": 200, "corps": {"compte": None}},
                     "connexion": ouvert([case(1), case(2), case(3)])})
    assert r["appel"]["corps"]["pseudo"] == "martin"
    assert r["appel"]["corps"]["mot_de_passe"] == "un-mot-de-passe"
    assert r["appel"]["corps"]["appareil"], "le serveur garde de quoi reconnaitre l'appareil"
    assert r["passe"] == "", "le mot de passe ne traine pas dans un champ"
    assert r["compte"] == "ouvert"
    assert r["bouton"] == "Compte : martin"


def test_l_ecran_refuse_un_champ_vide_sans_appeler_le_serveur(banc):
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          o.elements['compte-pseudo'].value = 'martin';
          const rendu = L.Hud.envoyerCompte('connexion');
          return { rendu: rendu, etat: o.elements['compte-etat'].textContent,
                   appels: o.compte.appels.map(function (a) { return a.chemin; }) };
        });
    }""")
    assert r["rendu"] is None
    assert "mot de passe" in r["etat"]
    assert r["appels"] == ["ouvrir"]


def test_une_session_coupee_se_dit_et_ne_monte_plus_rien(banc):
    """⚠️ Un jeton perime revenu : le serveur a delie TOUS les appareils. Le jeu
    le dit en francais, referme le compte, et ne monte plus rien."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          return { compte: L.Compte.etat().etat, message: o.elements['compte-etat'].textContent,
                   form: o.elements['compte-form'].hidden };
        }).then(function (vue) {
          return L.Compte.monter(1).then(function () {
            vue.appels = o.compte.appels.map(function (a) { return a.chemin; });
            return vue;
          });
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4}),
             reseau={"ouvrir": {"statut": 401, "corps": {"erreur": "ce compte a été ouvert ailleurs avec une vieille session : "
                                                                   "tous les appareils sont déconnectés, reconnecte-toi",
                                                         "coupe": True}}})
    assert r["compte"] == "ferme"
    assert "déconnectés" in r["message"]
    assert r["form"] is False, "on redemande un mot de passe"
    assert r["appels"] == ["ouvrir"], "plus rien ne monte avec un jeton coupe"


def test_se_deconnecter_monte_la_partie_avant_de_partir(banc):
    """⚠️ Partir en laissant sur le serveur une version plus vieille que celle
    qu'on vient de jouer, c'est perdre sa soiree au prochain appareil."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          // La premiere ecriture monte (rien n'est encore parti) ; la seconde
          // tombe dans le repos de `apresEcriture` et ne monte pas toute seule.
          L.Sauvegarde.ecrire({ jour: 8, argent: 40, stats: { secondes: 20 } }, 1);
          return calme(o);
        }).then(function () {
          L.Sauvegarde.ecrire({ jour: 9, argent: 50, stats: { secondes: 30 } }, 1);
          return L.Compte.deconnecter();
        }).then(function (v) {
          return { etat: v.etat, appels: o.compte.appels.map(function (a) { return a.chemin; }),
                   bouton: o.elements['bouton-compte'].textContent };
        });
    }""",
             stockage=stockage(cases={1: partie()}, compteurs={1: 4},
                               sync={"compte": "martin", "cases": {"1": {"envoye": 4, "serveur": 4}}}),
             reseau={"ouvrir": ouvert([case(1, 4, apercu()), case(2), case(3)]),
                     "parties/1": {"statut": 200, "corps": {"emplacement": 1, "compteur": 5}}},
             )
    assert r["appels"] == ["ouvrir", "parties/1", "parties/1", "deconnexion"], "la partie monte AVANT la deconnexion"
    assert r["etat"] == "ferme"
    assert r["bouton"] == "Compte"


# =========================================================================================
# LE NIP (M14, 3e vague) : un verrou d'ECRAN sur un appareil deja lie, jamais un second
# mot de passe. Tout se decide en local (PBKDF2 -> AES-GCM, WebCrypto) — le serveur ne
# voit ni ne connait jamais le NIP, et un jeton n'est expose en clair qu'une fois, a
# l'activation (`POST /api/compte/nip`).
# =========================================================================================


def test_sans_nip_rien_ne_change_a_l_ouverture(banc):
    """⚠️ Regression a ne jamais perdre : sans NIP configure sur cet appareil, la
    session longue s'ouvre TOUTE SEULE, exactement comme les 1re et 2e vagues — le
    NIP est facultatif, il ne remplace jamais rien par defaut."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          return { etat: L.Compte.etat().etat, configure: L.Compte.etat().nipConfigure,
                   appels: o.compte.appels.map(function (a) { return a.chemin; }) };
        });
    }""")
    assert r["configure"] is False
    assert r["appels"] == ["ouvrir"]


def test_avec_un_nip_configure_rien_ne_part_au_demarrage(banc):
    """⚠️ Le coeur du verrou : `init()` ne doit MEME PAS appeler l'ouverture quand un
    NIP est configure sur cet appareil. Un jeu qui bavarde avec le serveur avant
    d'avoir vu le NIP n'est pas un verrou, c'est une case a cocher."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          return { etat: L.Compte.etat().etat, appels: o.compte.appels.length,
                   configure: L.Compte.etat().nipConfigure };
        });
    }""", stockage={"bandini-nip-v1": json.dumps({"sel": "AA==", "iv": "AA==", "corps": "AA==", "essais": 0})})
    assert r["etat"] == "verrouille"
    assert r["appels"] == 0
    assert r["configure"] is True


def test_verrouille_le_jeu_se_joue_sans_toucher_au_reseau(banc):
    """Un compte est un confort, jamais une condition — meme verrouille : JOUER
    joue, une partie se sauve, le retour au titre ne parle a personne."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Jeu.jouerPartie(1);
          o.frame(5);
          L.Jeu.retourTitre();
          return calme(o);
        }).then(function () {
          return { etat: L.B.etat, appels: o.compte.appels.length, beacons: o.compte.beacons.length };
        });
    }""", stockage={"bandini-nip-v1": json.dumps({"sel": "AA==", "iv": "AA==", "corps": "AA==", "essais": 0})})
    assert r["etat"] == "titre"
    assert r["appels"] == 0
    assert r["beacons"] == 0


def test_activer_un_nip_chiffre_le_jeton_et_rien_de_plus(banc):
    """⚠️ `activerNip` va chercher le jeton en clair — LA SEULE FOIS qu'il transite
    par le reseau depuis la 1re vague — et le chiffre localement. Le blob range en
    local n'a pas d'autre forme que sel + iv + corps chiffre + compteur d'essais."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); })
          .then(function (res) {
            const blob = JSON.parse(o.store['bandini-nip-v1'] || 'null');
            return { res: res, appels: o.compte.appels.map(function (a) { return a.chemin; }),
                     blob: blob && Object.keys(blob).sort(), essais: blob && blob.essais,
                     configure: L.Compte.etat().nipConfigure };
          });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)]),
                  "nip": {"statut": 200, "corps": {"jeton": "un-jeton-de-test-1234567890"}}})
    assert r["res"]["ok"] is True
    assert r["appels"] == ["ouvrir", "nip"]
    assert r["blob"] == ["corps", "essais", "iv", "sel"]
    assert r["essais"] == 0
    assert r["configure"] is True


def test_activer_un_nip_refuse_les_plus_tapes_et_les_formats_invalides(banc):
    """⚠️ La liste noire et le format se verifient AVANT tout appel reseau — refuser
    un NIP trop facile ne doit pas d'abord exposer le jeton pour rien."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          return Promise.all(['1234', '0000', String(new Date().getFullYear()), '12', 'abcd', '99999', ''].map(function (nip) {
            return L.Compte.activerNip(nip);
          }));
        }).then(function (resultats) {
          return { ok: resultats.map(function (r) { return r.ok; }),
                   appels: o.compte.appels.map(function (a) { return a.chemin; }) };
        });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)])})
    assert r["ok"] == [False] * 7
    assert r["appels"] == ["ouvrir"], "aucun de ces refus ne doit parler au serveur"


def test_un_nip_valide_et_pas_dans_la_liste_est_accepte(banc):
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.nipRefus('4821'); });
    }""")
    assert r is None


def test_deverrouiller_avec_le_bon_nip_rouvre_normalement(banc):
    """Le chemin heureux, sur DEUX chargements distincts — la vraie forme d'un
    rechargement de page, localStorage garde ce qui a ete ecrit, rien de plus."""
    premier = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); })
          .then(function () { return o.store; });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)], pseudo="Rocco"),
                  "nip": {"statut": 200, "corps": {"jeton": "un-jeton-de-test"}}})
    r = banc("""function (L, o) {
        const avant = { etat: L.Compte.etat().etat, appels: o.compte.appels.length };
        return L.Compte.deverrouiller('4821').then(function (res) {
          return { avant: avant, ok: res.ok, etat: res.etat, pseudo: res.pseudo,
                   appels: o.compte.appels.map(function (a) { return a.chemin; }) };
        });
    }""", stockage=premier, reseau={"ouvrir": ouvert([case(1), case(2), case(3)], pseudo="Rocco")})
    assert r["avant"] == {"etat": "verrouille", "appels": 0}
    assert r["ok"] is True
    assert r["etat"] == "ouvert"
    assert r["pseudo"] == "Rocco"
    assert r["appels"] == ["ouvrir"]


def test_cinq_echecs_effacent_le_nip_local_sans_toucher_au_reseau(banc):
    """⚠️ Le compte ne se bloque JAMAIS : la preuve la plus directe est qu'aucun de
    ces cinq essais ne parle au serveur — tout se joue en local, et un NIP faux
    LEVE (l'etiquette d'authentification d'AES-GCM), il ne rend pas une reponse
    qu'on pourrait mal lire."""
    premier = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); })
          .then(function () { return o.store; });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)]),
                  "nip": {"statut": 200, "corps": {"jeton": "un-jeton-de-test"}}})
    r = banc("""function (L, o) {
        let p = Promise.resolve();
        const tentatives = [];
        for (let i = 0; i < 5; i++) {
          p = p.then(function () { return L.Compte.deverrouiller('9081'); })
               .then(function (res) { tentatives.push(res); });
        }
        return p.then(function () {
          return { tentatives: tentatives.map(function (t) { return { ok: t.ok, motif: t.motif, essaisRestants: t.essaisRestants }; }),
                   configure: L.Compte.etat().nipConfigure, appels: o.compte.appels.length };
        });
    }""", stockage=premier)
    assert [t["ok"] for t in r["tentatives"]] == [False] * 5
    assert [t["essaisRestants"] for t in r["tentatives"]] == [4, 3, 2, 1, 0]
    assert [t["motif"] for t in r["tentatives"]][:4] == ["faux"] * 4
    assert r["tentatives"][-1]["motif"] == "efface"
    assert r["configure"] is False
    assert r["appels"] == 0, "le compte ne se bloque jamais : rien de tout cela ne parle au serveur"


def test_apres_l_effacement_le_mot_de_passe_reouvre_l_appareil(banc):
    """Le NIP local est parti ; le jeton d'appareil, lui, n'a pas bouge cote serveur —
    c'est le mot de passe qui relie a nouveau, comme au tout premier jour."""
    premier = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); })
          .then(function () {
            let p = Promise.resolve();
            for (let i = 0; i < 5; i++) p = p.then(function () { return L.Compte.deverrouiller('9081'); });
            return p;
          }).then(function () { return o.store; });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)]),
                  "nip": {"statut": 200, "corps": {"jeton": "un-jeton-de-test"}}})
    assert "bandini-nip-v1" not in premier
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          return { etat: L.Compte.etat().etat, configure: L.Compte.etat().nipConfigure };
        });
    }""", stockage=premier, reseau={"ouvrir": ouvert([case(1), case(2), case(3)], pseudo="Rocco")})
    assert r["configure"] is False
    assert r["etat"] == "ouvert", "sans NIP local, l'ouverture reprend toute seule"


def test_retirer_le_nip_est_purement_local(banc):
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); })
          .then(function () {
            L.Compte.desactiverNip();
            return { configure: L.Compte.etat().nipConfigure,
                     appels: o.compte.appels.map(function (a) { return a.chemin; }) };
          });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)]),
                  "nip": {"statut": 200, "corps": {"jeton": "un-jeton"}}})
    assert r["configure"] is False
    assert r["appels"] == ["ouvrir", "nip"]


def test_se_deconnecter_efface_aussi_le_nip_local(banc):
    """⚠️ Se deconnecter, c'est oublier CET appareil : un NIP qui survivrait
    rouvrirait un verrou sur un compte qui n'est plus lie a rien."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); })
          .then(function () { return L.Compte.deconnecter(); })
          .then(function () { return { configure: L.Compte.etat().nipConfigure }; });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)]),
                  "nip": {"statut": 200, "corps": {"jeton": "un-jeton"}},
                  "deconnexion": {"statut": 200, "corps": {"compte": None}}})
    assert r["configure"] is False


def test_activer_un_nip_sans_compte_ouvert_est_refuse(banc):
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); });
    }""")  # personne n'a de compte : l'ouverture rend `{compte: null}`
    assert r["ok"] is False


def test_l_ecran_montre_le_nip_seul_puis_le_reglage_une_fois_ouvert(banc):
    """L'ecran DOM : le formulaire de NIP seul quand verrouille, le reglage du NIP
    (ajouter/retirer) une fois le compte ouvert — jamais les deux en meme temps."""
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          return { nip: !o.elements['nip-form'].hidden, form: !o.elements['compte-form'].hidden,
                   bouton: o.elements['bouton-compte'].textContent };
        });
    }""", stockage={"bandini-nip-v1": json.dumps({"sel": "AA==", "iv": "AA==", "corps": "AA==", "essais": 0})})
    assert r["nip"] is True
    assert r["form"] is False
    assert r["bouton"] == "Compte verrouillé"


def test_deverrouiller_depuis_l_ecran_ouvre_le_compte(banc):
    premier = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); })
          .then(function () { return o.store; });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)], pseudo="Rocco"),
                  "nip": {"statut": 200, "corps": {"jeton": "un-jeton-de-test"}}})
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          o.elements['nip-code'].value = '4821';
          return L.Hud.deverrouillerNip();
        }).then(function () {
          return { bouton: o.elements['bouton-compte'].textContent,
                   nip: !o.elements['nip-form'].hidden, form: !o.elements['compte-form'].hidden,
                   code: o.elements['nip-code'].value };
        });
    }""", stockage=premier, reseau={"ouvrir": ouvert([case(1), case(2), case(3)], pseudo="Rocco")})
    assert r["bouton"] == "Compte : Rocco"
    assert r["nip"] is False
    assert r["code"] == "", "le NIP ne traine pas dans le champ apres coup"


def test_un_nip_faux_le_dit_a_l_ecran_avec_le_compte_d_essais(banc):
    premier = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); })
          .then(function () { return o.store; });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)]),
                  "nip": {"statut": 200, "corps": {"jeton": "un-jeton-de-test"}}})
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          o.elements['nip-code'].value = '9081';
          return L.Hud.deverrouillerNip();
        }).then(function () { return o.elements['nip-etat'].textContent; });
    }""", stockage=premier)
    assert "incorrect" in r
    assert "4" in r


def test_mot_de_passe_plutot_montre_le_formulaire_sans_toucher_au_nip(banc):
    """⚠️ Un contournement d'UN chargement, pas un « oublie mon NIP » : le blob local
    reste intact apres coup."""
    premier = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () { return L.Compte.activerNip('4821'); })
          .then(function () { return o.store; });
    }""", reseau={"ouvrir": ouvert([case(1), case(2), case(3)]),
                  "nip": {"statut": 200, "corps": {"jeton": "un-jeton-de-test"}}})
    r = banc("""function (L, o) {""" + CALME + """
        return calme(o).then(function () {
          L.Hud.montrerCompte();
          o.elements['bouton-nip-mot-de-passe'].dispatch('click', {});
          return { nip: !o.elements['nip-form'].hidden, form: !o.elements['compte-form'].hidden,
                   configure: L.Compte.etat().nipConfigure };
        });
    }""", stockage=premier)
    assert r == {"nip": False, "form": True, "configure": True}
