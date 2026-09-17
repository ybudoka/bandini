"""Un kiosque ferme n'a personne derriere (17 sept. 2026).

Retour de Martin, capture a l'appui — la cabane a fruits de mer, un marchand
au comptoir : « cantine, restaurant ou commerce ferme, il ne faut pas qu'il y
ait quelqu'un ». Le marchand etait pose au chargement et n'en partait jamais :
ACTION repondait « FERME » a quelqu'un qui attendait de servir.
"""

#: Le marchand a les pieds 11 px au-dessus de l'ancre de son kiosque.
DERRIERE = 11


def _heures(paquet):
    return {c["slug"]: c["heures"] for c in paquet["ambulants"]}


def test_charge_la_nuit_les_kiosques_fermes_sont_vides(banc, paquet):
    """Une partie qui reprend a 23 h 17 : les trois kiosques qui ont des
    heures sont vides, ceux qui n'en ont pas ont leur marchand."""
    heures = _heures(paquet)
    r = banc("""function (L, o) {
        L.B.partie.heure = 0.97;
        L.Jeu.commencer();
        return L.B.entites.filter(function (e) { return e.type === 'ambulant'; }).map(function (etal) {
            const derriere = L.B.entites.filter(function (q) {
                return q.type === 'pieton' && q.metier === 'ambulant'
                    && Math.hypot(q.x - etal.x, q.y - (etal.y - %(derriere)d)) < 4;
            });
            return { slug: etal.slug, derriere: derriere.length };
        });
    }""" % {"derriere": DERRIERE})
    fermes = [k for k in r if heures[k["slug"]]]
    ouverts = [k for k in r if not heures[k["slug"]]]
    assert len(fermes) >= 5 and len(ouverts) >= 5, r
    assert {k["slug"] for k in fermes} >= {"journaux", "cafe", "fruits_de_mer"}
    assert all(k["derriere"] == 0 for k in fermes), f"quelqu'un derriere un kiosque ferme : {fermes}"
    assert all(k["derriere"] == 1 for k in ouverts), f"un kiosque ouvert sans marchand : {ouverts}"


def test_hors_champ_il_s_efface_a_la_fermeture_et_revient_a_l_ouverture(banc, paquet):
    """Loin des yeux : a la fermeture le marchand n'est plus dans la ville, a
    l'ouverture il est de retour a son comptoir — et c'est la boucle de jeu
    qui le fait, pas un appel du juge."""
    debut, fin = _heures(paquet)["fruits_de_mer"]
    r = banc("""function (L, o) {
        L.B.partie.heure = %(ouvert)s;
        L.Jeu.commencer();
        const j = L.B.joueur;
        const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === 'fruits_de_mer'; })[0];
        const avant = etal.vendeur;
        // A une demi-bulle, hors champ.
        const dx = etal.x + 360 < L.Monde.carte.w * 16 ? 360 : -360;
        j.x = etal.x + dx; j.y = etal.y; L.Monde.centrerCamera(j.x, j.y);
        const visible = L.Entites.visibleAEcran(etal.x, etal.y - %(derriere)d, 24);
        L.B.partie.heure = %(ferme)s;
        o.frame(61);
        const ferme = { lien: !!etal.vendeur, dansLaVille: L.B.entites.indexOf(avant) >= 0 };
        j.x = etal.x; j.y = etal.y + 22; L.Entites.indexer(); L.Missions.majInvite(j);
        const invite = L.B.invite;
        L.B.partie.argent = 100;
        const achat = L.Missions.interagir(j);
        const argent = L.B.partie.argent;
        j.x = etal.x + dx; j.y = etal.y; L.Monde.centrerCamera(j.x, j.y);
        L.B.partie.heure = %(ouvert)s;
        o.frame(61);
        const v = etal.vendeur;
        return { avant: !!avant, visible: visible, ferme: ferme, invite: invite, achat: achat, argent: argent,
                 revenu: v ? { vivant: v.vivant, etat: v.etat, commerce: v.commerce,
                               ecart: Math.hypot(v.x - etal.x, v.y - (etal.y - %(derriere)d)),
                               dansLaVille: L.B.entites.indexOf(v) >= 0 } : null };
    }""" % {"ouvert": (debut + fin) / 2, "ferme": (fin + 1) / 2, "derriere": DERRIERE})
    assert r["avant"] is True, "la cabane ouverte n'avait pas de marchand"
    assert r["visible"] is False, "le juge devait regarder ailleurs"
    assert r["ferme"] == {"lien": False, "dansLaVille": False}, f"il est reste a la fermeture : {r['ferme']}"
    assert r["invite"].endswith("FERMÉ") and "$" not in r["invite"], r["invite"]
    assert r["achat"] is True and r["argent"] == 100, "une cabane fermee a vendu"
    assert r["revenu"], "personne n'est revenu a l'ouverture"
    assert r["revenu"]["dansLaVille"] and r["revenu"]["vivant"] and r["revenu"]["etat"] == "fige"
    assert r["revenu"]["commerce"] == "fruits_de_mer"
    assert r["revenu"]["ecart"] < 4, f"il est revenu a cote de son comptoir : {r['revenu']}"


def test_sous_nos_yeux_il_s_en_va_a_pied_et_ne_nait_pas(banc, paquet):
    """Qu'on regarde la cabane a l'heure de fermer : le marchand ne s'evapore
    pas, il quitte son comptoir a pied. Et qu'on la regarde a l'heure d'ouvrir :
    personne n'apparait derriere tant qu'on la fixe."""
    debut, fin = _heures(paquet)["fruits_de_mer"]
    r = banc("""function (L, o) {
        L.B.partie.heure = %(ouvert)s;
        L.Jeu.commencer();
        L.graine(7);
        const j = L.B.joueur;
        const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === 'fruits_de_mer'; })[0];
        const v = etal.vendeur;
        j.x = etal.x; j.y = etal.y + 40; L.Monde.centrerCamera(j.x, j.y);
        const visible = L.Entites.visibleAEcran(etal.x, etal.y - %(derriere)d, 24);
        L.B.partie.heure = %(ferme)s;
        o.frame(61);
        const partant = { lien: !!etal.vendeur, commerce: v.commerce, etat: v.etat, allure: v.allure,
                          dansLaVille: L.B.entites.indexOf(v) >= 0 };
        o.frame(300);
        const parti = L.B.entites.indexOf(v) < 0 || Math.hypot(v.x - etal.x, v.y - (etal.y - %(derriere)d)) > 16;
        // L'ouverture, sous nos yeux : personne ne nait au comptoir.
        L.B.partie.heure = %(ouvert)s;
        o.frame(61);
        const sousLeRegard = !!etal.vendeur;
        return { visible: visible, partant: partant, parti: parti, sousLeRegard: sousLeRegard };
    }""" % {"ouvert": (debut + fin) / 2, "ferme": (fin + 1) / 2, "derriere": DERRIERE})
    assert r["visible"] is True, "le juge devait regarder la cabane"
    p = r["partant"]
    assert p["dansLaVille"] is True, "il s'est evapore sous nos yeux"
    assert p["lien"] is False and p["commerce"] is None, p
    assert p["etat"] != "fige" and p["allure"] > 0, f"il reste plante au comptoir : {p}"
    assert r["parti"] is True, "cinq secondes apres la fermeture, il est encore au comptoir"
    assert r["sousLeRegard"] is False, "un marchand est ne sous le regard"
