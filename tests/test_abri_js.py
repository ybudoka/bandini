"""L'abri — ce qui ne peut pas répondre ne se fait pas taper.

Deux retours de Martin, un même principe. **Dans un char**, un passant ne doit
pas pouvoir nous faire de dommage : la tôle est entre lui et nous. **Au
téléphone**, où le jeu nous cloue sur place, la ville doit s'arrêter avec nous —
encaisser des coups qu'on ne peut pas rendre n'est pas une difficulté, c'est une
punition pour avoir décroché.

⚠️ La règle du char existait **déjà**, écrite une fois pour le feu : un brasier
mord le CHAR et saute qui est dedans (`majBrasiers`). Le poing et la balle ne la
connaissaient pas. Ces juges tiennent les trois chemins ensemble.
"""


#: Pose le joueur au milieu d'une rue droite (une balle ne doit pas casser sur
#: un mur avant d'arriver), le monte dans une berline À LUI — un char volé
#: ferait venir la police au milieu de la mesure — et rend le char.
#:
#: ⚠️ La simulation est menée À LA MAIN (`B.t++`, `indexer`, `Combat.maj`),
#: comme le juge du molotov : le trafic et la foule n'ont rien à dire ici, et
#: une auto-patrouille qui passe au mauvais moment ferait un juge qui clignote.
AU_VOLANT = """
    function surLaRue(L, o) {
      const j = L.B.joueur, ligne = o.ligneDroite();
      j.x = ligne.x; j.y = ligne.y;
      L.Monde.centrerCamera(j.x, j.y);
      L.Entites.indexer();
      return j;
    }
    function auVolant(L, o) {
      const j = L.B.joueur;
      const v = o.char('auto', 0, 0, 0);
      v.aToi = true;
      L.Vehicules.monter(j, v);
      L.Entites.indexer();
      return v;
    }
    function assaillant(L, dx, arme) {
      const j = L.B.joueur;
      const e = L.Entites.creerPieton(j.x + dx, j.y, L.Entites.archetypeDeRue());
      e.arme = arme;
      e.intouchable = false;
      L.Entites.regarder(e, j.x - e.x, j.y - e.y);
      L.Entites.indexer();
      return e;
    }
    function tourner(L, images) {
      for (let i = 0; i < images; i++) { L.B.t++; L.Entites.indexer(); L.Combat.maj(); }
    }
"""


def test_un_poing_ne_traverse_pas_la_portiere(banc):
    """Le même passant, le même coup, à un mètre : à pied il nous touche, au
    volant il tape sur de la tôle.

    ⚠️ Les deux moitiés comptent. Sans celle « à pied », le juge serait vert le
    jour où le passant cesserait de frapper tout court — et il ne mesurerait
    plus rien."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const j = surLaRue(L, o);
        // À pied, d'abord : le coup porte.
        j.vie = j.vieMax;
        const premier = assaillant(L, 12, 'poings');
        L.Combat.frapper(premier, false);
        tourner(L, 40);
        const aPied = j.vieMax - j.vie;
        L.Entites.retirer(premier);
        // Puis au volant, au même endroit, avec le même coup.
        j.vie = j.vieMax;
        const v = auVolant(L, o);
        const e = assaillant(L, 12, 'poings');
        L.Combat.frapper(e, false);
        tourner(L, 40);
        return { aPied: aPied, auVolant: j.vieMax - j.vie, dansVehicule: j.dansVehicule === v,
                 porte: (e.touches || []).length, ecart: Math.hypot(e.x - j.x, e.y - j.y) };
    }""" % AU_VOLANT)
    assert r["aPied"] > 0, "à pied, le passant ne frappe même pas : le juge ne mesure rien"
    assert r["dansVehicule"], "le joueur n'est pas monté"
    assert r["ecart"] < 18, "le passant n'est jamais arrivé à portée de poing"
    assert r["auVolant"] == 0, "un poing traverse la portière"


def test_une_balle_mord_la_tole_pas_le_conducteur(banc):
    """Un passant armé tire sur le char : la carrosserie encaisse, pas nous.

    ⚠️ Et elle encaisse VRAIMENT. Retirer le conducteur de la liste des cibles
    sans rien mettre à la place rendrait le char intraversable ET intouchable :
    la police pourrait vider ses chargeurs dessus sans jamais rien obtenir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const j = surLaRue(L, o);
        j.vie = j.vieMax;
        const v = auVolant(L, o);
        const vieChar = v.vie;
        const tireur = assaillant(L, 46, 'pistolet');
        // ⚠️ **UNE RAFALE, PAS UNE BALLE.** Une arme DISPERSE — `Combat.tirer`
        // dévie chaque balle de `(B.rng() - 0.5) * dispersion * 2` — et le juge
        // n'en tirait qu'une : il pariait donc sur l'état du dé au moment où il
        // arrive là, c'est-à-dire sur tout ce que la ville a tiré avant lui. Le
        // pari s'est perdu le 16 sept. 2026, quand le port a touché l'eau : la
        // balle est passée à côté d'un char de trente pixels à quarante-six
        // pixels de distance, et le juge a conclu qu'elle « s'était évaporée ».
        // Cinq balles ne changent rien à ce qu'il mesure — la tôle encaisse, le
        // conducteur non — et elles l'enlèvent au hasard.
        for (let k = 0; k < 5; k++) L.Combat.tirer(tireur, L.Combat.armeDef('pistolet'));
        const balles = L.B.entites.filter(function (e) { return e.type === 'projectile'; }).length;
        tourner(L, 30);
        return { balles: balles, perdu: j.vieMax - j.vie, tole: vieChar - v.vie,
                 dansVehicule: j.dansVehicule === v,
                 reste: L.B.entites.filter(function (e) { return e.type === 'projectile'; }).length };
    }""" % AU_VOLANT)
    assert r["balles"] > 0, "le passant n'a pas tiré : le juge ne mesure rien"
    assert r["dansVehicule"], "le joueur n'est pas monté"
    assert r["perdu"] == 0, "une balle traverse la tôle et touche le conducteur"
    assert r["tole"] > 0, "la balle n'a rien fait au char non plus : elle s'est évaporée"
    assert r["reste"] == 0, "la balle vole encore"


#: Attend l'appel de Madame Thibodeau (il vient quelques secondes après M1).
#: Rend le numéro de l'image où il sonne, ou -1.
DECROCHER = """
    function decrocher(L, o) {
      L.B.partie.missionsFaites.m1 = 1;
      for (let i = 0; i < 900; i++) { o.frame(1); if (L.B.cinema) return i; }
      return -1;
    }
    function photo(L) {
      return L.B.entites.filter(function (e) { return e.type === 'pieton' || e.type === 'vehicule'; })
        .map(function (e) { return { id: e.id, x: e.x, y: e.y }; });
    }
    function bouges(avant, apres) {
      const ou = {};
      apres.forEach(function (e) { ou[e.id] = e; });
      return avant.filter(function (e) {
        const q = ou[e.id];
        return q && (Math.abs(q.x - e.x) > 0.01 || Math.abs(q.y - e.y) > 0.01);
      }).length;
    }
"""


def test_le_telephone_fige_la_ville(banc):
    """Au téléphone, à pied : personne ne bouge, l'horloge du jeu s'arrête — et
    la réplique, elle, avance."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const sonne = decrocher(L, o);
        if (sonne < 0) return { sonne: sonne };
        const avant = photo(L), tAvant = L.B.t, cAvant = L.B.cinema.t, iAvant = L.B.cinema.i;
        const lignes = L.B.cinema.lignes.length;
        o.frame(30);
        const pendant = bouges(avant, photo(L));
        const fige = { t: L.B.t - tAvant, replique: L.B.cinema ? L.B.cinema.t - cAvant : -1 };
        // ACTION passe à la suivante, même la ville arrêtée — et sur la
        // dernière réplique, ACTION raccroche : c'est la même avancée.
        o.tape('KeyE', 2);
        const suite = L.B.cinema ? L.B.cinema.i - iAvant
          : (iAvant + 1 >= lignes ? 1 : -1);
        // Et quand on raccroche, la ville repart.
        L.Histoire.finir();
        const repart = photo(L);
        o.frame(30);
        return { sonne: sonne, pendant: pendant, monde: avant.length, fige: fige, suite: suite,
                 apres: bouges(repart, photo(L)), tFin: L.B.t };
    }""" % DECROCHER)
    assert r["sonne"] >= 0, "le téléphone n'a jamais sonné"
    assert r["monde"] > 5, "la ville est vide : le juge ne mesure rien"
    assert r["pendant"] == 0, "la ville continue pendant qu'on ne peut pas bouger"
    assert r["fige"]["t"] == 0, "l'horloge du jeu tourne pendant l'appel"
    assert r["fige"]["replique"] == 30, "la réplique n'avance plus : on ne peut plus raccrocher"
    assert r["suite"] == 1, "ACTION ne passe plus la réplique"
    assert r["apres"] > 0, "la ville ne repart pas une fois l'appel fini"
    assert r["tFin"] > 0, "l'horloge du jeu n'est jamais repartie"


def test_au_volant_l_appel_ne_fige_rien(banc):
    """Le même appel, au volant : là on PEUT bouger, donc la ville tourne et le
    char répond toujours au gaz.

    ⚠️ C'est la moitié qui empêche le remède d'être pire que le mal : figer un
    char lancé parce que le téléphone sonne, c'est un mur au milieu de la rue."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const j = L.B.joueur;
        const v = o.char('auto', 0, 0, 0);
        v.aToi = true;
        L.Vehicules.monter(j, v);
        L.Entites.indexer();
        const sonne = decrocher(L, o);
        if (sonne < 0) return { sonne: sonne };
        const avant = photo(L), tAvant = L.B.t;
        o.touche('KeyW');
        o.frame(30);
        o.relacher('KeyW');
        return { sonne: sonne, auVolant: j.dansVehicule === v, pendant: bouges(avant, photo(L)),
                 t: L.B.t - tAvant, vitesse: v.vitesse, cinema: !!L.B.cinema };
    }""" % DECROCHER)
    assert r["sonne"] >= 0, "le téléphone n'a jamais sonné"
    assert r["auVolant"], "le joueur n'est plus au volant"
    assert r["cinema"], "l'appel s'est arrêté avant la mesure"
    assert r["t"] == 30, "l'horloge du jeu s'est arrêtée alors qu'on conduit"
    assert r["pendant"] > 0, "la ville s'est figée alors qu'on peut encore rouler"
    assert r["vitesse"] > 0, "le char ne répond plus au gaz pendant l'appel"
