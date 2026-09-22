/* Bandini — le décor, les bêtes et les gens répondent (P4).

   ⚠️ PYTHON DÉCIDE, ICI ON JOUE. Quel décor donne quel geste, ce que chacun rend
   et les mots que la rue répond viennent du paquet (`B.defs.interactions`, écrit
   dans `app/interactions.py`) : ce fichier ne garde aucun nombre.

   Sept gestes, et pas un menu : on REGARDE la chose (`faceA`, comme tout le reste
   depuis « on agit sur ce qu'on regarde ») et on appuie sur ACTION.

   ⚠️ ACTION GARDE SON ORDRE (`Missions.interagir`), et c'est le point délicat :
   - **les gens qui font un métier de rue** (le pourboire, la photo) passent AVANT
     le bouclier humain — le bouclier est le dernier de la chaîne, et il prend
     n'importe quel passant. Sauf DERRIÈRE l'artiste, quand ses poches se
     prennent : un pourboire ne vole pas le geste du pickpocket ;
   - **le décor** passe APRÈS tout le reste, et refuse de servir quand une porte,
     une arme par terre ou un char sont sous la main : ils sont servis par
     l'appelant, APRÈS nous — on leur volerait le bouton (la leçon du garage).
   Une seule fonction dit ce qui est sous la main, et l'invite du HUD comme le
   geste la lisent : le bouton ne promet jamais ce qu'ACTION ne ferait pas.

   ⚠️ RIEN NE SE SAUVEGARDE, sauf ce qui a déjà sa case : les bacs fouillés vont
   dans `partie.fouilles` (la clé `rue:tx,ty`, la valeur est le jour), à côté des
   tiroirs. La soif d'une fontaine et ce qu'on a bu ne survivent pas à la partie.
*/

const Interactions = (function () {
  'use strict';

  function cfg() { return B.defs && B.defs.interactions; }

  //: Les fontaines qu'on vient de vider : tuile -> l'image où l'on a de nouveau soif.
  const fontaines = {};

  function tuile(e) { return Math.floor(e.x / TT) + ',' + Math.floor(e.y / TT); }

  function dans(table, cle) {
    return Array.isArray(table) ? table.indexOf(cle) >= 0 : Object.prototype.hasOwnProperty.call(table, cle);
  }

  // --- Qui peut agir -------------------------------------------------------------

  /** Le joueur est debout, dehors, et libre de ses mains. ⚠️ Les mêmes gardes que
      le combat : au volant, dans un manège, en haut d'une clôture, la roue d'armes
      ouverte, un piratage en cours, ou quelqu'un dans les bras, ACTION a déjà un
      sens ailleurs. */
  function peutAgir(j) {
    return !!(j && j.vivant && !j.dansVehicule && !j.manege && !j.enjambe && !j.alite && !j.assis
      && !j.otage && !j.roule && !B.interieur && !B.cinema && !B.menu && !B.roue && !B.piratage && !B.transition && cfg());
  }

  // --- Ce qui est sous la main : les gens ----------------------------------------

  function disponible(e) {
    return e.vivant && e.etat !== 'fuit' && e.etat !== 'assomme' && e.etat !== 'temoin' && !e.personnage && !e.mission;
  }

  /** L'artiste de rue à qui l'on peut donner un dollar. Sans un dollar, personne :
      ACTION retombe sur ce qui suit, comme avant. */
  function artisteSousLaMain(j) {
    const c = cfg().pourboire;
    if (B.partie.argent < c.montant) return null;
    return Entites.pietonsAutour(j.x, j.y, c.portee_px).find(function (e) {
      return c.metiers.indexOf(e.metier) >= 0 && disponible(e) && faceA(j, e.x, e.y) && !Combat.pochesAPrendre(j, e);
    }) || null;
  }

  /** Le touriste qui n'a pas encore été pris en photo par nous. */
  function touristeSousLaMain(j) {
    const c = cfg().photo;
    return Entites.pietonsAutour(j.x, j.y, c.portee_px).find(function (e) {
      return e.metier === c.metier && !e.photoPrise && disponible(e) && faceA(j, e.x, e.y) && !Combat.pochesAPrendre(j, e);
    }) || null;
  }

  /** Le chat CONFIANT à portée de main : `Entites.majBete` pose `e.confiance`
      (au pas, sans arme, sans char) — ici, on ne fait que le lire et mesurer
      la distance de la main, pas celle de la fuite. `!e.fuite` : un chat qui
      détale encore n'est pas un chat qu'on caresse. */
  function chatSousLaMain(j) {
    const c = cfg().caresser;
    return Entites.betes().find(function (e) {
      return e.espece === c.espece && e.confiance && !e.fuite && dist2(j.x, j.y, e.x, e.y) < c.portee_px * c.portee_px;
    }) || null;
  }

  function mot(liste) { return liste[Math.floor(B.rng() * liste.length)]; }

  function donnerUnPourboire(j, artiste) {
    const c = cfg().pourboire;
    Missions.payer(c.montant, 'POURBOIRE');
    // ⚠️ La pièce change de poche pour de vrai, comme celle des badauds
    // (`quitterLeSpectacle`) : fouiller l'artiste rapporte ce qu'on lui a laissé.
    artiste.argent = (artiste.argent || 0) + c.montant;
    artiste.chapeauT = (B.defs.pietons.spectacle && B.defs.pietons.spectacle.applaudit_images) || 40;
    Entites.bulle(artiste, mot(c.merci[artiste.metier] || c.merci.musicien), { duree: 90 });
    j.animT = 12; j.animType = 'ramasse';
    Son.SFX.argent();
    return true;
  }

  /** Le flash d'un appareil : la même gerbe blanche que celle du touriste devant
      une vitrine (`Entites.majPhoto`), posée sur lui. */
  function flash(x, y) {
    for (let i = 0; i < 10; i++) {
      const a = B.rng() * Math.PI * 2, v = 0.3 + B.rng() * 0.9;
      Entites.particule(x, y, Math.cos(a) * v, Math.sin(a) * v * 0.6, 8 + B.rng() * 6, '#ffffff', 2, 0);
    }
  }

  function prendreLaPhoto(j, t) {
    const c = cfg().photo;
    t.photoPrise = true;
    t.etat = 'arret'; t.minuterie = c.pose_images; t.vx = 0; t.vy = 0;
    Entites.regarder(t, j.x - t.x, j.y - t.y);
    flash(t.x, t.y - 8);
    // ⚠️ Il paie de SA poche : pas de puits sans fond, et un touriste fauché dit
    // merci quand même.
    const brut = c.pourboire[0] + Math.floor(B.rng() * (c.pourboire[1] - c.pourboire[0] + 1));
    const sou = Math.min(t.argent || 0, brut);
    Entites.bulle(t, mot(c.merci), { duree: 120 });
    j.animT = 12; j.animType = 'ramasse';
    if (sou > 0) { t.argent -= sou; Missions.encaisser(sou, 'PHOTO'); }
    else Son.SFX.ramasse();
    return true;
  }

  /** Caresser le chat : rien à gagner, juste un mot au HUD et une pause — le seul
      des huit gestes qui ne rapporte rien. ⚠️ Un `Hud.message`, pas une bulle : les
      bêtes vivent dans `B.betes` (pas `B.entites`), et `dessinerBetes` ne dessine
      aucune bulle — en poser une ne se serait jamais vue. Il s'assoit comme il le
      fait déjà entre deux pas (`e.humeur = 'pose'`), le temps qu'on le flatte. */
  function caresserLeChat(j, chat) {
    const c = cfg().caresser;
    chat.humeur = 'pose'; chat.vx = 0; chat.vy = 0; chat.minuterie = 90;
    Hud.message(mot(c.mots));
    j.animT = 20; j.animType = 'ramasse';
    Son.SFX.ramasse();
    return true;
  }

  // --- Ce qui est sous la main : le décor ----------------------------------------

  function refusAsseoir(j) {
    const r = cfg().asseoir.refus;
    if (B.recherche.etoiles > 0) return r.police;
    if (j.saigne > 0) return r.saigne;
    return null;
  }

  function fouilleDuJour(bac) {
    const p = B.partie;
    return !!p.fouilles && p.fouilles['rue:' + tuile(bac)] === p.jour;
  }

  function jetDe(borne) {
    return B.entites.find(function (e) {
      return e.type === 'jet_eau' && !e.aqueduc && Math.abs(e.x - borne.x) < 2 && Math.abs(e.y - borne.y) < 2;
    }) || null;
  }

  function fontaineSeche(f) { return (fontaines[tuile(f)] || 0) > B.t; }

  /** Un barbecue déjà vidé aujourd'hui : la MÊME case que les bacs fouillés
      (`partie.fouilles`), préfixée `bbq:` pour ne jamais collider avec la
      tuile d'une poubelle voisine. */
  function mangeDuJour(bbq) {
    const p = B.partie;
    return !!p.fouilles && p.fouilles['bbq:' + tuile(bbq)] === p.jour;
  }

  /** Un parcomètre déjà forcé aujourd'hui : la MÊME case que les bacs fouillés
      (`partie.fouilles`), préfixée `parc:`. */
  function videDuJour(p) {
    const partie = B.partie;
    return !!partie.fouilles && partie.fouilles['parc:' + tuile(p)] === partie.jour;
  }

  /** Les six gestes de décor, dans l'ordre où l'on tranche à distance égale. `refus`
      dit pourquoi ce n'est pas possible MAINTENANT (le HUD l'écrit, ACTION le dit) —
      un refus se montre, comme « FERMÉ » devant un kiosque. */
  const SUR_LE_DECOR = [
    { geste: 'asseoir', table: function (c) { return c.asseoir.sieges; }, portee: function (c) { return c.asseoir.portee_px; },
      refus: function (j) { return refusAsseoir(j); },
      invite: function (c) { return c.asseoir.invite; }, faire: sAsseoir },
    { geste: 'fouiller', table: function (c) { return c.fouiller.decors; }, portee: function (c) { return c.fouiller.portee_px; },
      refus: function (j, d) { return fouilleDuJour(d) ? cfg().fouiller.deja : null; },
      invite: function (c) { return c.fouiller.invite; }, faire: fouiller },
    { geste: 'boire', table: function (c) { return c.boire.decors; }, portee: function (c) { return c.boire.portee_px; },
      refus: function (j, d) { return fontaineSeche(d) ? cfg().boire.encore : null; },
      invite: function (c) { return c.boire.invite; }, faire: boire },
    { geste: 'barbecue', table: function (c) { return c.barbecue.decors; }, portee: function (c) { return c.barbecue.portee_px; },
      refus: function (j, d) { return mangeDuJour(d) ? cfg().barbecue.deja : null; },
      invite: function (c) { return c.barbecue.invite; }, faire: manger },
    { geste: 'parcometre', table: function (c) { return c.parcometre.decors; }, portee: function (c) { return c.parcometre.portee_px; },
      refus: function (j, d) { return videDuJour(d) ? cfg().parcometre.deja : null; },
      invite: function (c) { return c.parcometre.invite; }, faire: forcerLeParcometre },
    { geste: 'borne', table: function (c) { return c.borne.decors; }, portee: function (c) { return c.borne.portee_px; },
      refus: function () { return null; },
      invite: function (c, j, d) { return jetDe(d) ? c.borne.invite_fermer : c.borne.invite_ouvrir; }, faire: ouvrirLaBorne },
  ];

  /** Le geste de décor sous la main : `{ geste, decor, refus, invite }`, ou null.

      ⚠️ La porte, l'arme par terre et le char passent AVANT nous — ils sont servis
      par l'appelant (`Combat.maj`, `Vehicules.maj`) une fois qu'`interagir` a rendu
      `false`, et un banc ne doit pas voler ACTION à la porte d'à côté. */
  function decorSousLaMain(j) {
    if (!peutAgir(j)) return null;
    if (Monde.porteDevant(j) || Combat.objetSousLaMain(j) || Vehicules.vehiculeSousLaMain(j)) return null;
    // ⚠️ Quelqu'un a la poche pleine ET le dos tourne, devant nous : ACTION fait ses poches
    // (`Combat.maj`, apres `interagir`), et un banc ne lui vole pas le geste.
    if (Combat.victimeDesPoches(j)) return null;
    const c = cfg();
    let meilleur = null, dMin = Infinity, largeur = 0;
    SUR_LE_DECOR.forEach(function (g) { largeur = Math.max(largeur, g.portee(c)); });
    for (const d of Entites.decorAutour(j.x, j.y, largeur)) {
      if (d.type !== 'decor' || d.brise) continue;
      const e = dist2(j.x, j.y, d.x, d.y);
      if (e >= dMin || !faceA(j, d.x, d.y)) continue;
      for (const g of SUR_LE_DECOR) {
        if (!dans(g.table(c), d.decor) || e > g.portee(c) * g.portee(c)) continue;
        dMin = e;
        const refus = g.refus(j, d);
        meilleur = { geste: g, decor: d, refus: refus, invite: refus || g.invite(c, j, d) };
        break;
      }
    }
    return meilleur;
  }

  // --- Les gestes ----------------------------------------------------------------

  function sAsseoir(j, banc) {
    const s = cfg().asseoir.sieges[banc.decor];
    // ⚠️ Comme le lit d'hôpital : une pose déjà dessinée (celle du patient), rien
    // d'autre. On garde OÙ l'on se tenait pour s'y relever, et ce qu'on avait de
    // vie pour sentir le premier coup.
    j.assis = { x: banc.x + s.dx, y: banc.y + s.dy, avant: { x: j.x, y: j.y, face: j.face }, vie: j.vie, t: 0 };
    j.x = j.assis.x; j.y = j.assis.y; j.vx = 0; j.vy = 0; j.roule = 0;
    j.face = s.pose;
    // La pression qui nous assied ne monte pas non plus dans le char d'à côté.
    j.descenduT = B.t;
    return true;
  }

  /** Se lever : là où l'on se tenait, et — si c'est le stick qui nous lève — dans
      le sens où l'on poussait. */
  function seLever(j, dx, dy) {
    const a = j.assis;
    j.assis = null;
    if (!a) return;
    j.x = a.avant.x; j.y = a.avant.y; j.vx = 0; j.vy = 0;
    j.face = a.avant.face || 'bas';
    if (dx || dy) Entites.regarder(j, dx, dy);
  }

  /** Une image assise, appelée par `Entites.majJoueur` : vrai tant qu'on est assis
      (rien d'autre ne bouge), faux si l'on vient de se lever — et le pas qui
      suit est le nôtre, dans la même image, comme au sortir d'un lit. */
  function majAssis(j) {
    const a = j.assis, c = cfg();
    if (!a) return false;
    // Ailleurs que sur le banc (l'hôpital, le poste, une porte) : on n'est plus assis.
    if (!c || !j.vivant || j.dansVehicule || B.interieur || dist2(j.x, j.y, a.x, a.y) > 81) { j.assis = null; return false; }
    if (Entree.axe.mag > 0) { seLever(j, Entree.axe.x, Entree.axe.y); return false; }
    if (Entree.neuf('action')) {
      // ⚠️ La pression qui nous lève est dépensée : sinon `Combat.maj`, plus loin
      // dans la même image, en ferait un pickpocket, ou nous rassoirait aussitôt.
      seLever(j, 0, 0);
      j.gesteT = B.t; j.descenduT = B.t;
      Entree.videPresse();
      return true;
    }
    // Un coup donné, une arme sortie, un sprint, un coup reçu : on est debout.
    // ⚠️ ARME se lit TENUE (`bas`), pas a la pression : la roue et le retour rapide se decident au relacher.
    if (Entree.neuf('attaque') || Entree.bas('arme') || Entree.neuf('esquive') || j.vie < a.vie || j.saigne > 0) {
      seLever(j, 0, 0);
      return false;
    }
    const v = B.defs.recherche.vitesses;
    j.endurance = Math.min(v.endurance, j.endurance + v.endurance_par_image * 0.6 * c.asseoir.souffle_x);
    if (++a.t % c.asseoir.pv_images === 0 && j.vie < j.vieMax * c.asseoir.pv_plafond) Missions.soigner(j, 1);
    a.vie = j.vie;
    j.vx = 0; j.vy = 0;
    return true;
  }

  function choisirLaTrouvaille(table, facteurRien, nuit) {
    // ⚠️ LA NUIT A SES HABITUDES (`fouiller.la_nuit`) : la nuit, le rat de la table
    // est un raton, et il pese plus lourd. Toujours UN `B.rng()` : la nuit change ce
    // que le de rend, pas combien on en tire.
    const poids = function (e) {
      if (e[1] === 'rien') return e[0] * facteurRien;
      if (nuit && e[1] === nuit.remplace) return e[0] * nuit.poids;
      return e[0];
    };
    const rend = function (slug) { return nuit && slug === nuit.remplace ? nuit.par : slug; };
    let total = 0;
    table.forEach(function (e) { total += poids(e); });
    let tirage = B.rng() * total;
    for (const e of table) {
      tirage -= poids(e);
      if (tirage < 0) return rend(e[1]);
    }
    return rend(table[table.length - 1][1]);
  }

  function fouiller(j, bac) {
    const c = cfg().fouiller, p = B.partie;
    j.animT = 16; j.animType = 'ramasse';
    if (fouilleDuJour(bac)) { Hud.message(c.deja); Son.SFX.erreur(); return true; }
    p.fouilles = p.fouilles || {};
    p.fouilles['rue:' + tuile(bac)] = p.jour;
    // ⚠️ Le quartier dit la poubelle : `Monde.standingA` lit le bloc sous le bac.
    const standing = Monde.standingA(Math.floor(bac.x / TT), Math.floor(bac.y / TT));
    const facteur = c.standing[standing] === undefined ? 1 : c.standing[standing];
    const nuit = c.la_nuit && Monde.estNuit(p.heure) ? c.la_nuit : null;
    const slug = choisirLaTrouvaille(c.tables[c.decors[bac.decor]], facteur, nuit);
    const t = c.trouvailles[slug];
    // Le raton ne reste pas dans la poubelle : on le voit filer.
    if (nuit && slug === nuit.par) Entites.fairePartirUnRaton(bac.x, bac.y + 4);
    if (t.argent) {
      const gain = t.argent[0] + Math.floor(B.rng() * (t.argent[1] - t.argent[0] + 1));
      Missions.encaisser(gain, t.texte);
    } else if (t.pv > 0) {
      Missions.soigner(j, t.pv);
      Missions.nourrir(j, t.souffle || 0);
      Hud.message(t.texte + ' +' + t.pv + ' PV');
      Son.SFX.ramasse();
    } else if (t.pv < 0) {
      // ⚠️ La morsure ne tue jamais : il reste toujours un point.
      j.vie = Math.max(1, j.vie + t.pv);
      B.partie.vie = j.vie;
      Hud.message(t.texte + ' ' + t.pv + ' PV');
      Son.SFX.touche();
    } else {
      Hud.message(t.texte);
    }
    return true;
  }

  function boire(j, fontaine) {
    const c = cfg().boire;
    j.animT = 30; j.animType = 'ramasse';
    if (fontaineSeche(fontaine)) { Hud.message(c.encore); return true; }
    fontaines[tuile(fontaine)] = B.t + c.repit_images;
    j.endurance = Math.min(B.defs.recherche.vitesses.endurance, j.endurance + c.souffle);
    Hud.message(c.message);
    Son.SFX.nage();
    return true;
  }

  function manger(j, bbq) {
    const c = cfg().barbecue, p = B.partie;
    j.animT = 24; j.animType = 'ramasse';
    if (mangeDuJour(bbq)) { Hud.message(c.deja); Son.SFX.erreur(); return true; }
    p.fouilles = p.fouilles || {};
    p.fouilles['bbq:' + tuile(bbq)] = p.jour;
    Missions.soigner(j, c.pv);
    Missions.nourrir(j, c.souffle);
    Hud.message(c.message);
    Son.SFX.ramasse();
    return true;
  }

  /** Forcer un parcomètre : un délit (`recherche.DELITS.parcometre`), comme défoncer une
      distributrice — un passant qui l'a vu peut aller le raconter
      (`Police.signalerCrime`/`quelqu_un_voit`, le même appel que la distributrice). */
  function forcerLeParcometre(j, p) {
    const c = cfg().parcometre, partie = B.partie;
    j.animT = 20; j.animType = 'ramasse';
    if (videDuJour(p)) { Hud.message(c.deja); Son.SFX.erreur(); return true; }
    partie.fouilles = partie.fouilles || {};
    partie.fouilles['parc:' + tuile(p)] = partie.jour;
    const gain = c.argent[0] + Math.floor(B.rng() * (c.argent[1] - c.argent[0] + 1));
    Missions.encaisser(gain, c.message);
    Son.SFX.argent();
    Police.signalerCrime('parcometre', p.x, p.y, Police.quelqu_un_voit(p.x, p.y, null));
    return true;
  }

  function ouvrirLaBorne(j, borne) {
    const c = cfg().borne, jet = jetDe(borne);
    j.animT = 14; j.animType = 'ramasse';
    if (jet) { Entites.retirer(jet); return true; }
    // ⚠️ La gerbe d'une borne défoncée, telle quelle (`Entites.creer('jet_eau')`) : elle
    // crache, elle s'entend de loin, et elle s'éteint seule. Seule la durée change.
    Entites.creer('jet_eau', borne.x, borne.y, { minuterie: c.duree_images, dessine: false, solide: false, r: 0 });
    Son.SFX.borne_cassee();
    return true;
  }

  // --- La chaîne d'ACTION ---------------------------------------------------------

  /** Avant le bouclier humain : ceux qui travaillent dans la rue. */
  function utiliserSurLesGens(j) {
    // ⚠️ UNE PRESSION, UN GESTE. `Vehicules.maj` rappelle `interagir` dans la meme image
    // quand un char est sous la main : sans ce garde, le pourboire partait deux fois.
    if (j && j.gesteT === B.t) return true;
    if (!peutAgir(j)) return false;
    const artiste = artisteSousLaMain(j);
    if (artiste) { j.gesteT = B.t; return donnerUnPourboire(j, artiste); }
    const touriste = touristeSousLaMain(j);
    if (touriste) { j.gesteT = B.t; return prendreLaPhoto(j, touriste); }
    return false;
  }

  /** Une bête confiante — le chat qui se laisse approcher. Ni un décor (elle bouge,
      elle vit dans `B.betes`), ni des gens (`Combat.otageSousLaMain` ne la voit
      jamais) : sa propre place dans la chaîne, entre les deux — après le bouclier
      humain (ce n'est jamais une prise d'otage), avant le décor (elle ne lui vole
      rien, il n'y a rien d'autre à caresser sous la main en même temps). */
  function utiliserSurLesBetes(j) {
    if (j && j.gesteT === B.t) return true;
    if (!peutAgir(j)) return false;
    const chat = chatSousLaMain(j);
    if (!chat) return false;
    j.gesteT = B.t;
    return caresserLeChat(j, chat);
  }

  /** Après tout le reste : le décor. */
  function utiliserSurLeDecor(j) {
    if (j && j.gesteT === B.t) return true;
    const s = decorSousLaMain(j);
    if (!s) return false;
    j.gesteT = B.t;
    if (s.refus) {
      j.animT = 10; j.animType = 'ramasse';
      Hud.message(s.refus); Son.SFX.erreur();
      return true;
    }
    return s.geste.faire(j, s.decor);
  }

  function inviteGens(j) {
    if (!peutAgir(j)) return null;
    const c = cfg();
    if (artisteSousLaMain(j)) return c.pourboire.invite + ' — ' + c.pourboire.montant + ' $';
    if (touristeSousLaMain(j)) return c.photo.invite;
    return null;
  }

  function inviteBetes(j) {
    if (!peutAgir(j)) return null;
    return chatSousLaMain(j) ? cfg().caresser.invite : null;
  }

  function inviteDecor(j) {
    if (j && j.assis) return 'SE LEVER';
    const s = decorSousLaMain(j);
    return s ? s.invite : null;
  }

  // --- À chaque image ---------------------------------------------------------------

  /** Se rafraîchir dans la gerbe d'une borne. ⚠️ Le souffle seulement, et seulement
      quand on ne le dépense pas : on ne court pas dans l'eau en reprenant son souffle. */
  function maj() {
    const j = B.joueur, c = cfg();
    if (!j || !c || j.assis || j.dansVehicule || j.nage || B.interieur || B.t % 4 !== 0) return;
    if (Entree.bas('esquive')) return;
    const r = c.borne.rayon_px;
    let dedans = false;
    for (const e of B.entites) {
      if (e.type === 'jet_eau' && dist2(e.x, e.y, j.x, j.y) < r * r) { dedans = true; break; }
    }
    if (!dedans) return;
    const v = B.defs.recherche.vitesses;
    // Quatre images d'un coup : la reprise ordinaire (`* 0,6`) est déjà comptée par
    // `majJoueur`, on n'ajoute que le facteur de plus.
    j.endurance = Math.min(v.endurance, j.endurance + v.endurance_par_image * 0.6 * (c.borne.souffle_x - 1) * 4);
    if (B.t % 24 === 0) Entites.remous(j.x, j.y + 2, 1);
  }

  /** Une nouvelle partie n'hérite pas de la soif de l'ancienne. */
  function oublier() {
    for (const k in fontaines) delete fontaines[k];
  }

  return { peutAgir, artisteSousLaMain, touristeSousLaMain, chatSousLaMain, decorSousLaMain,
           utiliserSurLesGens, utiliserSurLesBetes, utiliserSurLeDecor,
           inviteGens, inviteBetes, inviteDecor, majAssis, seLever, maj, oublier, fouilleDuJour, fontaineSeche, jetDe };
})();
