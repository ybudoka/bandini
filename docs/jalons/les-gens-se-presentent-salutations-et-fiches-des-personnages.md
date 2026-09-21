# Les gens se présentent : salutations et fiches des personnages

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026) : « il faut améliorer les dialogues, normalement les gens
se présentent avant de parler comme "C'est XXX" ou "Salut c'est XXX" ou "Salut XXX, tu sais
je suis qui ? je suis XXX" et plus. Je veux que tu améliores et documentes », puis « sois
varié et contextuel selon la personnalité des personnages avec les salutations », puis « je
veux aussi que tu fasses des fiches pour chaque personnage, leur histoire et leur
personnalité ».

- ⚠️ Aujourd'hui, un appel ne dit pas qui appelle (m50 : « Cousin, j'ai une faveur ») et
  les autres se nomment d'un mot sec, sans salutation (« Bouchard. », « Raymonde. ») ; aucun
  échec ne dit son nom alors qu'il se dit TOUJOURS au combiné, sept fins sur treize sont au
  téléphone sans nom, Ti-Guy accueille le joueur sans se nommer, et les quatre contacts de
  m6 serrent la main sans dire le leur. Ce qu'on fait : 1) la règle, écrite dans `docs/jeu-d-acteur.md` — au téléphone et
  à la première rencontre, on se nomme, une fois par conversation, avec une salutation qui
  est celle DU personnage (Bouchard ne dit pas « allô mon chou ») ; 2) un juge qui la tient
  là où elle se vérifie (l'appel, l'échec, la fin au combiné, la première réplique de
  chacun) ; 3) les répliques réécrites, et leurs voix seulement régénérées (`--refaire`, ≈
  40 voix) ; 4) une fiche par personnage dans `docs/personnages/` : son histoire, sa
  personnalité, sa façon de parler et de saluer, sa voix, sa gestuelle, ses liens et ses
  missions.

## Notes

⚠️ **Livré le 21 sept. 2026** — la règle et son juge, 37 répliques réécrites et 1 neuve, leurs **38 voix**
régénérées (oui de Martin), et **douze fiches** de personnages.

**Ce qui est livré**

- **La règle** (`docs/jeu-d-acteur.md` § 3.11) : au téléphone — l'appel, l'échec (toujours au combiné), la
  fin quand le donneur n'est pas là, un `pendant` dit de loin — et à la première rencontre, la première
  réplique dit le nom de celui qui parle, **une fois**, dans **sa** salutation ; déjà connu, en personne, une
  salutation sans nom. Une table des formes, chacune avec son exemple du jeu : « C'est X. », « Salut, c'est
  X. », « X. » (le sec), « Ici le sergent X. », « X au bout du fil! », « Moi, c'est X. », « Tu me replaces
  pas? C'est moi, X! » (la forme de Martin, Ti-Guy au terminus), « Tu me connais pas encore. X. » (Josée),
  « Prénom Nom, titre. », « C'est encore X! », « C'est pas X qui t'appelle, OK? » (Bouchard, l'échec de m4).
- **Le juge**, dans `app/missions/__init__.py` : `noms_dits` (les mots du `nom`, moins les titres :
  « le sergent » ne nomme pas Bouchard), `se_nomme` (mot entier, sans la casse), `on_le_rencontre` (le client
  du taxi et le narrateur n'y sont pas soumis), `dans_l_ordre_ou_on_les_entend`, `erreurs_de_presentation`
  (la première réplique de chacun, dans l'ordre du catalogue) ; et trois reproches de plus dans
  `erreurs_de_mise_en_scene` (l'appel, l'échec, la fin au combiné). **26 reproches** sur le catalogue d'avant.
  `scripts/verifier_missions.py` les dit, et son `--squelette` se nomme au combiné. Trois juges neufs dans
  `tests/test_mise_en_scene.py` ; **ils rougissent tous les trois** quand `se_nomme` répond toujours oui
  (mutation faite, puis défaite).
- **Les répliques**, chacune dans la salutation de son personnage : les appels de m3, m4, m5, m50, q02, s03,
  m51 ; les **treize échecs** ; les **sept fins au combiné** (m4, m5, m6, q02, s03, m51, m97) ; cinq `pendant`
  dits de loin (m1, m5, q02, s03, m51) ; Ti-Guy au terminus (m1) ; les quatre poignées de main de m6. Et une
  **neuve** : l'accueil de Lulu à m50 — la poignée de main de l'objectif 1 était muette, et m50 peut se jouer
  avant m6 (« Te v'là, toi! Lulu, la sœur de Josée. C'est Marco qui t'envoie pour le cargo? ») ; `lulu-m50-9`,
  ajoutée à la fin, aucun mp3 payé ne change de nom.
- **Les 38 voix** : `--voix --refaire <les 38 slugs> --masters ~/elevenlabs-audio/bandini-voix-v3-masters-2026-09-16`,
  ≈ 3 950 caractères (27 968 restaient, remise à zéro le 17 oct.), 0 en échec ; Julia (Thibodeau) et
  l'annonceur (Ovila) séchés au passage (`comment=voix isolee`). Mesuré sans oreille : pas de trou de plus de
  0,7 s au milieu d'une phrase ; seule `marco-m3-1` finit sur une queue de 1,05 s sous −45 dB (après « du
  cash? », en fin de fichier). Le juge des voix coupées par leur scène
  (`test_aucune_voix_de_scene_n_est_coupee_par_la_suivante`, avec la durée de chaque mp3) passe : aucune
  des 38 ne se fait couper ; ses quatre `xfail` stricts sont les coupures d'avant (intros de m4, m5, m97, fin
  de m3). ⚠️ **Martin n'a pas encore écouté.**
- **Douze fiches** dans `docs/personnages/` (une par personnage de `PERSONNAGES`, plus Rocco, l'absent), et
  leur index : l'histoire, la personnalité (ce qu'il veut, ce qu'il cache), comment il parle et ce qu'il ne
  dit jamais, ses balises de base, **comment il salue et se présente** (au téléphone, à la première
  rencontre, connu, quand ça va mal), sa gestuelle, ses liens, le canon par mission, ce qui l'attend dans M16,
  et ce qui reste à trancher. Les faits dits en jeu portent le slug de leur mission ; le reste est une bible
  proposée, à contredire.
- **La doc suit** : `jeu-d-acteur.md` (§ 3.7, § 3.7 bis « Lire la fiche avant d'écrire », § 3.11, la liste de
  contrôle, les sources), `comment-monter-les-missions.md` (§ 3 : un donneur a sa fiche ; § 5 : l'exemple se
  nomme, et la règle jugée), `missions-en-scene.md`, `ecrire-drole.md` (règle 7 : la salutation peut être la
  blague), `voix-de-l-histoire.md`, `carte.md` § 5, le plan (« Où est le reste »), `architecture.md`
  (`docs/personnages/` couvert d'un trait, comme `docs/jalons/`, dans `verifier_carte_du_depot.py`).

**Ce que l'écriture a montré**

- ⚠️ **Le nom coûte une phrase, et une réplique n'en a que deux** (`. `, `! `, `? ` comptés). « Salut, le
  jeune. C'est Bouchard. J'ai une petite tournée… » en faisait trois : le nom se glisse par une virgule
  (« Salut, le jeune, c'est Bouchard. »).
- ⚠️ **`test_une_ligne_attend_une_voix_encore_en_chargement` avançait de « durée de la ligne 1 + 3 »
  images** : dès que la réplique 1 de Ti-Guy est devenue plus longue que la 2, la 2 passait aussi. Le juge
  voulait dire « la ligne passe quand sa voix finit » : borné à 23 images (« maintenant + 20 » est franchi en
  21, la ligne la plus courte en dure 114).
- ⚠️ **Trois bancs de m50 supposaient une poignée de main muette** (`test_histoire_js.py` : le fuyard qui file,
  le fuyard qui ne naît pas sous le char garé, Lulu qui dit d'attendre la noirceur) : ils appuyaient sur E et
  attendaient l'objectif suivant deux images plus tard. Avec l'accueil, la poignée de main se dit d'abord —
  comme à m6 et m51 — et l'objectif avance quand elle est finie. Les bancs passent l'accueil comme ACTION le
  ferait, et vérifient qu'il est dit (`lulu-m50-9`).
- **Ce que le juge ne voit pas** : un `pendant` dit de loin (la distance se décide en jeu, `present()`) — les
  cinq ont été nommés à la main ; un chemin hors du catalogue (m50 avant m6) — l'accueil de m50 le couvre.
- **La suite complète** (7 groupes en parallèle, puis `test_navigateur.py` seul, `BANDINI_TESTS_OBLIGATOIRES=1`,
  sur `fbf75d2` + ce travail) : 3 857 verts, 4 `xfail`, 14 sautés ; 5 rouges — les trois bancs de m50
  ci-dessus (ajustés, rejugés verts) et deux **d'avant** qui échouent aussi sur `fbf75d2` seul :
  `test_la_foule_ne_se_traverse_plus` et `test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler`.
- **Rouge d'avant, pas de moi** : `test_definitions.py::test_le_paquet_reste_leger` (44 075 octets gzip à
  `75f6485`, 44 232 à `fbf75d2`, pour un plafond de 44 000). Les noms ajoutés aux répliques y mettent
  **≈ 250 octets de plus** : le texte des dialogues voyage encore dans le paquet. Relever le plafond, ou sortir
  les dialogues du paquet (M16), est à Martin.

**À trancher par Martin** (l'index est dans `docs/personnages/README.md`)

1. **Rocco : oncle et mort (l'ouverture), ou cousin et « parti se faire oublier » (Ti-Guy, m1) ?**
2. **Marco est-il le vrai cousin de Rocco ?** (la fiche le propose : ça donne à m97 sa raison)
3. **Deux Réjean** : Bouchard (la vision) et Prévost (M16).
4. **La fin de m51 passe au combiné** alors qu'on rapporte les enveloppes au casse-croûte.
