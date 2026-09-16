"""La sieste — le lit mène aussi au SOIR.

Demande de Martin : « ajoute un mécanisme pour passer de jour à nuit ». Le lit ne
menait qu'au matin (7 h 12), et dehors la nuit ne tombe qu'à 19 h 52 : une
mission `nuit` prise au réveil faisait attendre **4 min 15 réelles** sous
« ATTENDS LA NUIT », sans rien à faire. Le lit propose maintenant DORMIR
JUSQU'AU SOIR — le jour seulement.

⚠️ Une sieste n'est pas une nuit : elle rend **un quart** de la vie (choix de
Martin), pas tout, et elle ne passe jamais minuit.
"""

MATIN = "DORMIR JUSQU’AU MATIN"
SOIR = "DORMIR JUSQU’AU SOIR"

#: Entre dans la planque, puis rouvre le menu du lit à l'heure voulue.
#:
#: ⚠️ L'heure se pose APRÈS l'entrée : c'est le menu qui la lit, et on veut
#: voir ce qu'il offre à cette heure-là, pas celle où l'on a passé la porte.
AU_LIT = """
    function entrerALaPlanque(L, o) {
      L.Jeu.commencer();
      const j = L.B.joueur;
      const porte = L.Monde.carte.portes.find(function (p) { return p.lieu === 'planque'; });
      j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
      o.entrer(porte);
    }
    function menuDuLit(L, heure) {
      if (L.B.menu) L.Hud.fermerMenu();
      L.B.partie.heure = heure;
      const j = L.B.joueur;
      const lit = L.B.interieur.points.find(function (p) { return p.type === 'lit'; });
      j.x = lit.x * L.TT + 8; j.y = lit.y * L.TT + 8 + 12;
      L.Missions.utiliserPoint(j);
      return L.B.menu;
    }
    function ligne(menu, libelle) {
      return menu.items.find(function (i) { return i.libelle === libelle; });
    }
"""


def test_la_sieste_mene_au_soir_le_meme_jour(banc, paquet):
    """Au lit à 9 h 36, blessé, essoufflé, deux étoiles au dos : on se réveille
    à 20 h 45 LE MÊME JOUR, et dehors c'est la nuit pour de vrai.

    ⚠️ « Dehors » compte : dans la pièce, `estNuit()` dit toujours non — les
    intérieurs sont éclairés. C'est en ressortant qu'on lit ce que la mission
    lira."""
    r = banc("""function (L, o) {
        %s
        entrerALaPlanque(L, o);
        const p = L.B.partie, j = L.B.joueur;
        const menu = menuDuLit(L, 0.40);
        const libelles = menu.items.map(function (i) { return i.libelle; });
        j.vie = 30; j.endurance = 20; j.surplus = 15; L.B.recherche.etoiles = 2;
        const jour = p.jour;
        ligne(menu, '%s').faire();
        const fondu = !!L.B.transition;
        L.Hud.fermerMenu();
        o.fondu();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        const r = { libelles: libelles, jour: p.jour - jour, heure: p.heure, texte: L.Monde.heureTexte(),
                    vie: j.vie, vieMax: j.vieMax, endurance: j.endurance, surplus: j.surplus,
                    etoiles: L.B.recherche.etoiles, fondu: fondu,
                    sauve: { heure: brut.heure, jour: brut.jour - p.jour } };
        o.sortir();
        r.dehors = { nuit: L.Monde.estNuit(), clignote: L.Monde.feuxClignotent() };
        return r;
    }""" % (AU_LIT, SOIR))
    sieste = paquet["economie"]["sieste"]
    assert SOIR in r["libelles"], "le lit n'offre pas la sieste en plein jour"
    assert r["libelles"].index(MATIN) < r["libelles"].index(SOIR), (
        "la nuit complète doit rester AVANT la sieste : la main qui appuie deux fois pour dormir la connaît"
    )
    assert r["fondu"] is True, "la sieste passe au noir, comme le sommeil"
    assert r["jour"] == 0, "une sieste ne passe pas minuit"
    assert r["heure"] == sieste["reveil"] and r["texte"] == "20:45"
    assert r["vie"] == min(r["vieMax"], 30 + round(r["vieMax"] * sieste["soin"]))
    assert r["endurance"] == 100 and r["surplus"] == 0, "un somme rend le souffle, pas l'avance achetée"
    assert r["etoiles"] == 0, "la police lâche le morceau pendant qu'on dort, comme la nuit"
    assert r["sauve"] == {"heure": sieste["reveil"], "jour": 0}, "la sieste sauve la partie, à l'heure du réveil"
    assert r["dehors"] == {"nuit": True, "clignote": True}, (
        "on se réveille à la brune : dehors, la mission de nuit attend encore"
    )


def test_une_sieste_rend_un_quart_de_la_vie_pas_plus(banc):
    """Quatre siestes, quatre santés de départ : +25, jamais au-dessus du plein.
    Et la même blessure, soignée par une vraie nuit, remonte au plein — c'est
    la moitié qui prouve que la sieste soigne MOINS, pas seulement qu'elle soigne."""
    r = banc("""function (L, o) {
        %s
        entrerALaPlanque(L, o);
        const p = L.B.partie, j = L.B.joueur;
        const apres = [10, 60, 90, 100].map(function (vie) {
          p.heure = 0.40; j.vie = vie;
          L.Missions.dormirJusquAuSoir(); o.fondu();
          return j.vie;
        });
        p.heure = 0.40; j.vie = 10;
        L.Missions.dormir(); o.fondu();
        return { apres: apres, nuit: j.vie, vieMax: j.vieMax, soin: L.B.defs.economie.sieste.soin };
    }""" % AU_LIT)
    assert r["soin"] == 0.25, "choix de Martin : une sieste soigne à 25 %"
    assert r["vieMax"] == 100
    assert r["apres"] == [35, 85, 100, 100]
    assert r["nuit"] == 100, "une vraie nuit, elle, rend tout"


def test_le_lit_n_offre_le_soir_que_le_jour(banc):
    """La nuit, le lit ne propose que le matin : elle est déjà là, la mission
    n'attend plus. Et ce refus est ce qui garantit que la sieste ne passe
    jamais minuit.

    ⚠️ Les heures sont choisies LOIN des bascules (6 h 25, 19 h 52) : un juge
    posé sur la minute où la teinte franchit le seuil clignoterait à la
    première retouche de la table des teintes."""
    r = banc("""function (L, o) {
        %s
        entrerALaPlanque(L, o);
        const offres = {};
        [0.10, 0.30, 0.50, 0.80, 0.84, 0.95].forEach(function (h) {
          const m = menuDuLit(L, h);
          offres[h] = { soir: !!ligne(m, '%s'), matin: !!ligne(m, '%s') };
        });
        L.Hud.fermerMenu();
        // Appelee quand meme passe l'heure du reveil, elle ne fait pas reculer le temps.
        const p = L.B.partie, jour = p.jour;
        p.heure = 0.95;
        L.Missions.dormirJusquAuSoir(); o.fondu();
        return { offres: offres, recule: { heure: p.heure, jour: p.jour - jour } };
    }""" % (AU_LIT, SOIR, MATIN))
    offres = {float(h): v for h, v in r["offres"].items()}
    assert {h for h, v in offres.items() if v["soir"]} == {0.30, 0.50, 0.80}, offres
    assert all(v["matin"] for v in offres.values()), "la nuit complète s'offre à toute heure, comme avant"
    assert r["recule"] == {"heure": 0.95, "jour": 0}


def test_le_reveil_tombe_dans_la_nuit_sans_la_manger(banc):
    """`reveil` a deux bornes. Trop tôt, et on se lève à la brune devant
    « ATTENDS LA NUIT » — l'attente qu'on voulait supprimer. Trop tard, et la
    sieste mange la nuit qu'elle est venue chercher.

    La nuit se mesure ici minute par minute, DEHORS (`estNuit(heure)`), avec la
    table des teintes que le joueur voit : le juge suit la table si on la
    retouche, au lieu de recopier 19 h 52 en dur."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const reveil = L.B.defs.economie.sieste.reveil;
        let debut = null, fin = null;
        for (let m = 12 * 60; m < 36 * 60; m++) {
          const nuit = L.Monde.estNuit((m % 1440) / 1440);
          if (nuit && debut === null) debut = m;
          if (!nuit && debut !== null && fin === null) fin = m;
        }
        L.B.partie.heure = reveil;
        return { reveil: reveil * 1440, debut: debut, fin: fin,
                 clignote: L.Monde.feuxClignotent(),
                 clignoteDepuis: L.B.defs.conduite.trafic.clignotant_depuis * 1440 };
    }""")
    assert r["debut"] < r["reveil"] < r["fin"], "on doit se réveiller DANS la nuit"
    assert r["reveil"] >= r["clignoteDepuis"] and r["clignote"], (
        "au réveil, les feux doivent déjà clignoter : la ville a fini de passer à la nuit"
    )
    reste = (r["fin"] - r["reveil"]) / (r["fin"] - r["debut"])
    assert reste >= 0.85, f"la sieste mange la nuit : il n'en reste que {reste:.0%}"
