"""Les aides JS des juges qui JOUENT des missions au banc — une seule copie.

Le même bloc (`passer`, `etape`, `fermer`, `faites`, `paiements`, `finir`…) était recopié en tête
de chaque fichier qui joue des missions ; ce module garde ce qui était IDENTIQUE, mot pour mot,
d'un fichier à l'autre. Une aide qui a divergé pour un fichier (un `boite` qui lit aussi le texte,
un `paiements` qui ne garde que les montants, un `finir` qui ferme les répliques en route) reste
dans ce fichier : elle n'est pas « la même », et l'aligner changerait ce que le juge regarde.

    OUTILS = outils("passer", "etape", "fermer") + '''
      function boite(L) { … }        // ce qui est propre au fichier
    '''

Les aides sont des déclarations `function` : collées dans `function (L, o) { … }`, leur ordre
ne compte pas (elles sont hissées).
"""

_AIDES = {
    "passer": """\
  function passer(L, o) {
    let n = 0;
    while ((L.B.scene || L.B.cinema) && n < 6000) { o.frame(1); if (L.B.cinema && n % 30 === 0) L.Histoire.suivante(); n++; }
  }
""",
    "etape": """\
  function etape(L) { return L.B.partie.mission ? L.B.partie.mission.etape : null; }
""",
    "faites": """\
  function faites(L, slugs) { slugs.forEach(function (s) { L.B.partie.missionsFaites[s] = 1; }); }
""",
    "paiements": """\
  function paiements(L) {
    const liste = [], vrai = L.Missions.encaisser;
    L.Missions.encaisser = function (montant, raison) { liste.push({ montant: montant, raison: raison || null }); return vrai.apply(null, arguments); };
    return liste;
  }
""",
    "commencer": """\
  function commencer(L, o, slug) {
    L.Histoire.commencer(slug);
    L.B.cinema = null; L.B.scene = null;
  }
""",
    "finir": """\
  function finir(L, o) { for (let k = 0; k < 400 && L.B.partie.mission; k++) o.frame(1); passer(L, o); }
""",
    "heure": """\
  function heure(L, nuit) {
    let h = L.B.partie.heure;
    for (let k = 0; k < 400 && L.Monde.estNuit(h) !== nuit; k++) h = (h + 0.005) % 1;
    L.B.partie.heure = h;
  }
""",
    "ici": """\
  function ici(L, l) { const j = L.B.joueur; j.x = l.x; j.y = l.y; L.Entites.indexer(); }
""",
    "images": """\
  function images(L, o, n) { for (let k = 0; k < n; k++) { o.frame(1); fermer(L); } }
""",
    # Coucher les hommes de l'étape en cours (les K.-O. se font au poing ailleurs : ici, c'est
    # l'enchaînement qu'on juge — qu'ils naissent, qu'on les trouve, que l'étape avance).
    "coucher": """\
  function coucher(L, o) {
    const e0 = etape(L);
    const eux = L.B.mission.entites.filter(function (e) { return e.cible && e.etape === e0 && e.vivant; });
    eux.forEach(function (e) { L.Entites.assommer(e); });
    images(L, o, 4);
    return eux.length;
  }
""",
}


def _fermer(plafond: int) -> str:
    return (
        "  function fermer(L) { let g = 0; while (L.B.cinema && g < "
        + str(plafond)
        + ") { L.Histoire.suivante(); g++; } }\n"
    )


def outils(*noms: str, plafond: int = 100) -> str:
    """Les aides `noms`, dans cet ordre. `plafond` : combien de répliques `fermer` passe au plus
    (100 ; p01 et les actes de Sven en passent 200)."""
    inconnues = [n for n in noms if n != "fermer" and n not in _AIDES]
    assert not inconnues, f"aides inconnues : {inconnues}"
    return "\n" + "".join(_fermer(plafond) if n == "fermer" else _AIDES[n] for n in noms)


#: La trousse des deux tranches de dix missions (M16), reprise par les quatre missions et l'arc F.
OUTILS = outils("passer", "etape", "fermer", "faites", "paiements", "commencer", "finir")

#: Les missions allongées (22 sept. 2026, Martin : « des missions plus longues ») : ce que
#: leurs juges partagent — la nuit, se cacher pour semer, parler au bouton, et les
#: répliques qu'on a entendues (`dites`), pour juger que chaque étape neuve PARLE.
PLUS_LONGUES = """
  const dites = [];
  function ecouter(L) {
    let g = 0;
    while (L.B.cinema && g < 100) {
      const c = L.B.cinema;
      if (c.partie) c.lignes.forEach(function (l) { const k = c.partie + ':' + l.qui + ':' + (l.objectif === undefined ? '' : l.objectif); if (dites.indexOf(k) < 0) dites.push(k); });
      L.Histoire.suivante(); g++;
    }
  }
  // Quelques images, en passant les répliques qui s'ouvrent : un `pendant` part une image
  // APRÈS le changement d'étape, et tant qu'il parle, aucun objectif n'avance.
  function jouer(L, o, n) { for (let k = 0; k < (n || 6); k++) { o.frame(1); ecouter(L); } }
  function laNuit(L, o) {
    let h = L.B.partie.heure;
    for (let k = 0; k < 400 && !L.Monde.estNuit(h); k++) h = (h + 0.005) % 1;
    L.B.partie.heure = h; o.frame(2);
  }
  function aPied(L) { if (L.B.joueur.dansVehicule) L.Vehicules.descendre(L.B.joueur, true); }
  // Serrer la main au BOUTON : à deux pas de lui, ACTION.
  function serrer(L, o, slug) {
    aPied(L);
    const d = L.Histoire.donneur(slug), j = L.B.joueur;
    j.x = d.x - 16; j.y = d.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
    o.frame(1); j.angle = 0; j.face = 'droite'; L.Missions.majInvite(j); o.tape('KeyE', 2);
    const partie = L.B.cinema ? L.B.cinema.partie : null;
    ecouter(L); jouer(L, o);
    return partie;
  }
  // Semer : à pied, dans la pièce la plus proche, jusqu'à zéro étoile — puis ressortir.
  function seCacher(L, o) {
    const B = L.B, j = B.joueur;
    aPied(L);
    const avant = B.recherche.etoiles;
    let p = null, d = 1e12;
    (L.Monde.carte.def.portes || []).forEach(function (q) {
      if (!q.interieur) return;
      const dd = Math.pow(q.x * 16 + 8 - j.x, 2) + Math.pow((q.y + 1) * 16 + 8 - j.y, 2);
      if (dd < d) { d = dd; p = q; }
    });
    j.x = p.x * 16 + 8; j.y = (p.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(p); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    const dedans = !!B.interieur;
    let n = 0;
    for (; n < 9000 && B.recherche.etoiles > 0; n++) o.frame(1);
    L.Jeu.sortir(); o.fondu();
    for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
    jouer(L, o);
    return { avant: avant, dedans: dedans, images: n, porte: p.lieu, apres: B.recherche.etoiles };
  }
  function loinDe(L, a, b) { const p = L.Histoire.lieu(a), q = L.Histoire.lieu(b); return Math.round(Math.hypot(p.x - q.x, p.y - q.y) / 16); }
"""
