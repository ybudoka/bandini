"""L'écran ne tremble pas sous un dialogue — au banc (Martin, 8 oct. 2026).

« Quand on termine une mission en tuant un personnage, l'écran saute jusqu'à la fin du dialogue. »

⚠️ LA SECOUSSE DU DERNIER COUP. Chaque coup du joueur secoue la caméra (`Combat`, `B.cam.secousse` à 0,5 ou 0,9 ;
une explosion, 1,2), et la secousse ne s'amortissait QUE dans `Monde.majCamera`, qui ne tourne qu'avec la ville.
Le coup qui couche le dernier homme gagne la mission dans la même image, la scène de fin fige la ville… et la
secousse restait à 0,9 : `Jeu.rendre` tirait la vue au hasard de ±3,6 px à chaque image, jusqu'à la dernière
réplique. Une fin gagnée au calme (`retourner`) ne secouait rien : c'est pour ça que seule une fin « en tuant »
sautait. Même chose pour un dialogue qui fige la ville à pied (une réplique `pendant`, un appel).

On juge ce que l'on VOIT : la vue que `rendre` passe à `Monde.dessinerSol`, image par image — après les
quarante premières, le temps que la secousse retombe comme elle retombe en ville (× 0,9 par image : une
demi-seconde depuis 0,9).
"""

from outils_missions import OUTILS, PLUS_LONGUES

#: Les images où la secousse du coup a le droit de retomber, comme dans la ville qui roule.
RETOMBE = 40

AVANT_Q13 = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'e01', 'q02', 'q04', 'v01', 'q05', 'q06', 'q11']"

#: La vue peinte à chaque image (`Jeu.rendre` → `Monde.dessinerSol(ctx, vue)`).
ESPION = """
  function espionnerLaVue(L) {
    const vues = [], vrai = L.Monde.dessinerSol;
    L.Monde.dessinerSol = function (ctx, vue) { vues.push({ x: vue.x, y: vue.y }); return vrai.apply(null, arguments); };
    return vues;
  }
  // Combien d'images la vue a bougé d'une image à l'autre, sur `vues` à partir de `debut`.
  function sauts(vues, debut) {
    let n = 0;
    for (let i = Math.max(1, debut); i < vues.length; i++) {
      if (Math.abs(vues[i].x - vues[i - 1].x) > 0.01 || Math.abs(vues[i].y - vues[i - 1].y) > 0.01) n++;
    }
    return n;
  }
"""


def test_la_scene_de_fin_gagnee_au_poing_ne_tremble_pas(banc):
    """q13, _La nuit des Morues_ : elle finit sur le bosco (`tuer`, `chef`). On le couche au poing — FRAPPE
    martelée, comme Martin — et la scène de fin part sous le coup. Ses deux coupes déplacent la caméra (deux sauts
    voulus) ; tout le reste du temps, la vue ne bouge pas d'un pixel."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ESPION + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; j.invincible = 1e6;
        faites(L, """ + AVANT_Q13 + """);
        p.libere = ['faubourg']; p.faubourgLibere = true;
        commencer(L, o, 'q13'); jouer(L, o);
        const h = L.Histoire.lieu('hotel');
        j.x = h.x; j.y = h.y + 8; L.Entites.indexer(); jouer(L, o, 30);
        laNuit(L, o); jouer(L, o, 30);
        for (let v = 1; v <= 2; v++) {
            jouer(L, o, 30);
            const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === v && e.vivant; });
            eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o);
        }
        jouer(L, o, 30);
        const chef = B.mission.entites.find(function (e) { return e.cible && e.etape === 3 && e.vivant; });
        chef.vie = 1; chef.etat = 'fige';
        j.x = chef.x - 14; j.y = chef.y; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        // FRAPPE martelée jusqu'à ce que la scène de fin parte.
        let n = 0;
        for (; n < 300 && !B.scene; n++) {
            if (n % 6 === 0) o.touche('Space'); else if (n % 6 === 3) o.relacher('Space');
            o.frame(1);
        }
        o.relacher('Space');
        const scene = !!B.scene, secousse = B.cam.secousse;
        const vues = espionnerLaVue(L);
        let images = 0;
        while (B.scene && images < 3000) { o.frame(1); images++; }
        return { scene: scene, fait: !!p.missionsFaites.q13, secousse: secousse, images: images,
                 sauts: sauts(vues, """ + str(RETOMBE) + """), apres: B.cam.secousse };
    }""")
    assert r["scene"] and r["fait"], "la mission se gagne sous le coup, et sa scène de fin part"
    assert r["secousse"] > 0.05, "le coup qui gagne secoue bien la caméra (sans quoi ce juge ne mord pas)"
    assert r["images"] > 600, "la scène se joue jusqu'au bout"
    assert r["sauts"] <= 6, f"l'écran saute pendant la scène de fin : la vue bouge sur {r['sauts']} images sur {r['images']}"


def test_un_dialogue_qui_fige_la_ville_ne_tremble_pas(banc):
    """À pied, une réplique fige la ville (`Jeu.maj`, `B.cinema`) — un `pendant`, un appel. Un coup donné juste
    avant ne la fait pas trembler jusqu'au bout."""
    r = banc("function (L, o) {" + ESPION + """
        L.Jeu.commencer();
        while (L.B.menu) o.tape('Escape', 2);
        const B = L.B, j = B.joueur; j.invincible = 1e6;
        const e = o.poser(null, 14, 0); e.vie = 500;
        j.angle = 0; j.face = 'droite';
        // Le coup PORTE quelques images après l'appui (l'élan) : c'est là que la caméra secoue.
        o.touche('Space'); o.frame(1); o.relacher('Space');
        for (let k = 0; k < 40 && B.cam.secousse < 0.3; k++) o.frame(1);
        const secousse = B.cam.secousse;
        L.Histoire.direLignes([{ qui: 'josee', texte: 'Viens me voir au port, pis vite. On a du monde à recevoir.', slug: 'aucune-voix' }], {});
        const cinema = !!B.cinema;
        const vues = espionnerLaVue(L);
        let images = 0;
        while (B.cinema && images < 1000) { o.frame(1); images++; }
        return { secousse: secousse, cinema: cinema, images: images, sauts: sauts(vues, """ + str(RETOMBE) + """) };
    }""")
    assert r["secousse"] > 0.05, "le coup secoue la caméra (sans quoi ce juge ne mord pas)"
    assert r["cinema"] and r["images"] > 120, "la réplique se dit, la ville figée"
    assert r["sauts"] == 0, f"l'écran tremble sous la réplique : la vue bouge sur {r['sauts']} images sur {r['images']}"
