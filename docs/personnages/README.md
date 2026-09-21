# Les personnages de Bandini

← [le plan](../plan.md) · [le jeu d'acteur](../jeu-d-acteur.md) · [la recette des missions](../comment-monter-les-missions.md)

Une fiche par personnage de `missions.PERSONNAGES` : qui il est, d'où il vient, ce qu'il veut, comment il
parle — et **comment il salue et se présente**. Demande de Martin (21 sept. 2026) : « je veux aussi que tu
fasses des fiches pour chaque personnage, leur histoire et leur personnalité ».

**À quoi elles servent.** Avant d'écrire une réplique, on lit la fiche de celui qui la dit : sa salutation,
ses mots, ce qu'il ne dit jamais, les balises qui lui vont. Un sprite de seize pixels n'a pas de visage — ce
qui fait reconnaître Josée, c'est qu'elle ne dit jamais bonjour ; Lulu, qu'elle t'appelle « mon grand ».
Ces habitudes ne tiennent d'une mission à l'autre que si elles sont écrites quelque part : ici.

## Ce qui fait foi

Chaque fiche mêle deux sortes de faits.

- **Ce que le jeu a déjà dit** — une réplique, l'ouverture, la carte — porte le slug de sa mission entre
  parenthèses : « veuve (m2) ». On ne le contredit pas. Si une fiche doit changer, la réplique change avec
  elle, et sa voix se régénère (`--refaire`).
- **Le reste est la bible**, proposée le 21 sept. 2026 pour que les prochaines missions aient de quoi jouer :
  une enfance, une blessure, une manie. On s'en sert tant que Martin ne l'a pas contredite ; ce qu'il tranche
  remplace la proposition. Les contradictions déjà dans le jeu sont listées en bas de chaque fiche, sous
  « À trancher », et rassemblées ci-dessous.

## Les fiches

| Personnage | Slug | Où il se tient | Voix (ElevenLabs) | Missions |
|---|---|---|---|---|
| [Ti-Guy Lelièvre](ti-guy.md) | `ti_guy` | devant le terminus, puis au garage | Felix Tabarnak | m1 · m4 (au combiné) |
| [Madame Thibodeau](madame-thibodeau.md) | `thibodeau` | devant son kiosque | Julia | m2 · m51 |
| [Marco « le Cousin »](marco.md) | `marco` | devant le garage | Québec Tremblay | m3 · m50 · f01 · m97 |
| [Le sergent Réjean Bouchard](sergent-bouchard.md) | `bouchard` | au casse-croûte, dedans | Khaivan | m4 · m51 |
| [Josée « la Chef » Pelletier](josee.md) | `josee` | au bar Le Brouillard, dedans | Jeanne Mance | m5 · m6 |
| [Ti-Paul Gagnon](ti-paul.md) | `tipaul` | devant son dépanneur | Québec Tremblay | m6 · e01 · m51 |
| [Lucienne « Lulu » Pelletier](lulu.md) | `lulu` | à la cantine des Quais, dedans | Claudia | m6 · m50 · q02 · m51 |
| [Raymonde Fortin](raymonde.md) | `raymonde` | devant l'usine Prévost | Nadine | m6 · s03 |
| [Ovila Saint-Onge](ovila.md) | `ovila` | au phare, dedans | annonceur centre d'achat 1 | m6 |
| [Le narrateur du Clairon](le-narrateur.md) | `narrateur` | nulle part : c'est une voix | annonceur centre d'achat 1 | l'ouverture, le journal |
| [Le client du taxi](le-client-du-taxi.md) | `civil` | sur la banquette arrière | Alexandre | m3 |
| [Rocco Bandini](rocco.md) | — | absent : c'est lui qu'on remplace | — | partout, en creux |

⚠️ **Deux voix sont partagées**, et c'est pourquoi leurs personnages ne parlent **jamais dans le même
dialogue** (jugé) : Québec Tremblay fait Marco **et** Ti-Paul, l'annonceur fait le narrateur **et** Ovila.
Ce qui les distingue alors, c'est l'écriture — les mots, la salutation, le rythme : Marco parle bas et
court, Ti-Paul parle vite et trop ; le narrateur soupire, Ovila vouvoie.

## Qui parle se nomme — la salutation de chacun, d'un coup d'œil

La règle (`docs/jeu-d-acteur.md` § 3.11, jugée) : **au téléphone et à la première rencontre, on se nomme,
une fois par conversation** — et chacun le fait **à sa façon**. Le tableau est l'aide-mémoire ; la fiche
dit pourquoi.

| Qui | Au téléphone | À la première rencontre | Déjà connu, en personne | Ce qu'il ne dit jamais |
|---|---|---|---|---|
| Ti-Guy | « Ti-Guy au bout du fil! », « C'est Ti-Guy. » | « C'est moi, Ti-Guy, tu me replaces pas? » — il croit qu'on le connaît | « Heille, le cousin! » | « bonjour », « monsieur » |
| Mme Thibodeau | « C'est Madame Thibodeau, du kiosque. » — le « Madame » toujours | la même, en personne | « Mon p'tit! » | son prénom ; un sacre |
| Marco | « Cousin, c'est Marco. » ; bas : « C'est Marco. Parle pas trop fort, cousin » | « Salut, c'est Marco, le Cousin. » | « Cousin. » | « monsieur » ; un mot de trop |
| Bouchard | « Ici le sergent Bouchard. » (la 1re fois), puis « Salut, le jeune, c'est Bouchard. », « Bouchard. » | le grade d'abord | « Le jeune. » | « merci », « s'il vous plaît » |
| Josée | « Josée. » — un nom, un point, l'affaire | « Tu me connais pas encore. Josée, on m'appelle la Chef. » | rien : elle commence par ce qu'elle veut | « allô », « salut », un cri |
| Ti-Paul | « C'est Ti-Paul, du dépanneur! », « C'est Ti-Paul, l'ami. » | « Salut, l'ami! Moi, c'est Ti-Paul » | « Salut, l'ami! » | une phrase courte |
| Lulu | « Allô, mon grand, c'est Lulu! », « C'est encore Lulu! » | « Allô, mon grand! Moi, c'est Lulu, la sœur de Josée. » | « Te v'là, toi! » | une menace ; « au revoir » sans « mange » |
| Raymonde | « Raymonde, du syndicat. », « Raymonde. » | « Raymonde Fortin, présidente du syndicat. » — nom complet, titre, pas de sourire | « Le syndicat. » | « allô mon chou » ; « madame » |
| Ovila | (il n'appelle pas encore) | « Ovila Saint-Onge, pour vous servir. » — il vouvoie | « Bonsoir. » | le tutoiement ; une hâte |
| le narrateur | — | ne se présente pas : c'est le journal qui parle | — | « je » |
| le client | — | ne se présente pas ; il se trahit (« j'suis de la police ») | — | son nom |

⚠️ **Une salutation qui change dit quelque chose.** Marco qui appelle d'un « Marco. » sec, sans
« cousin » devant (m97), c'est la trahison avant la trahison. Bouchard qui dit « C'est pas Bouchard qui
t'appelle, OK? » (l'échec de m4), c'est un flic qui a peur. Rompre l'habitude d'un personnage est un outil —
à condition qu'elle existe, et donc qu'elle soit écrite ici.

## Ceux dont on parle, sans fiche encore

On les nomme dans les répliques, on ne les rencontre pas (encore). Une fiche naît avec leur entrée dans
`PERSONNAGES` — leurs traits de départ sont dans la fiche de M16, [« Les 34 personnages de
plus »](../jalons/m16-cent-missions.md#les-34-personnages-de-plus).

- **Sal « le Barbier » Ferraro** — le shylock à qui Rocco doit 15 000 piastres, « qui compte les jours »
  (l'ouverture). Le fil des deux fins (M13).
- **Réjean Prévost** — le patron de l'usine, qui retient la paie des gars de Raymonde (s03).
- **Les Cravates**, les **Morues**, les **Chevreuils** — les gangs du Faubourg, des Quais et des Érables
  (`pietons.GANGS`) : Josée est la Chef des Morues.
- **Le docker** qui file avec le colis de Marco (m50), **le chauffeur** qui s'est pogné la main dans sa
  glacière (q02) : des silhouettes, pas des personnages.

## Écrire une fiche

Un personnage neuf dans `PERSONNAGES` = **sa fiche ici, dans le même passage**, et sa ligne dans les deux
tableaux ci-dessus. Les sections, dans cet ordre (copier une fiche existante) :

1. **En bref** — slug, rôle, où, voix, bulle (`heler`), couleurs, missions ;
2. **Son histoire** — d'où il vient, ce qui l'a fait tel qu'il est ; les faits dits en jeu portent leur slug ;
3. **Sa personnalité** — ce qu'il veut, ce qu'il cache, ce qui le fait craquer ;
4. **Comment il parle** — registre, mots à lui, rythme, ce qu'il ne dit jamais, ses balises de base ;
5. **Comment il salue et se présente** — au téléphone, à la première rencontre, connu, quand ça va mal ;
6. **Son corps** — les gestes qui sont les siens (§ 2.4 du jeu d'acteur) ;
7. **Ses liens** — avec chacun des autres ;
8. **Ce qu'il a dit** (le canon, par mission) et **ce qui l'attend** (M16) ;
9. **À trancher** — les contradictions, pour Martin.

## À trancher par Martin

Relevé le 21 sept. 2026 en écrivant les fiches ; aucune n'a été corrigée d'autorité.

1. **Rocco : mort ou en fuite ? Oncle ou cousin ?** L'ouverture dit « ton **oncle** Rocco est **mort** le
   mois passé » ; à m1, Ti-Guy t'accueille comme « le **cousin** de Rocco » et dit que « Rocco est **parti se
   faire oublier** ». Voir [rocco.md](rocco.md) — deux lectures possibles, une seule à garder.
2. **Marco est-il un vrai cousin ?** Il se dit « le Cousin » et appelle le joueur « cousin » ; Bouchard est
   « un ami de la famille » (m3). La fiche propose qu'il soit le vrai cousin de Rocco — ce qui donne à m97
   (« t'as bâti un nom sur mon dos ») sa raison. Voir [marco.md](marco.md).
3. **Deux Réjean.** La vision prénomme le sergent **Réjean** Bouchard, et M16 le patron de l'usine
   **Réjean** Prévost. Aucun des deux prénoms n'est dit en jeu : on peut encore en changer un.
4. **La fin de m51 au combiné, à deux pas du sergent.** On rapporte les enveloppes au casse-croûte, mais
   Bouchard est dedans et le joueur à la porte : sa fin passe au téléphone. Elle se nomme donc (« Bouchard. »),
   mais une vraie remise en main propre (un `retourner`, ou une scène qui le fait sortir) jouerait mieux.
