# Écrire un accent (sans le mal orthographier)

← [le jeu d'acteur](jeu-d-acteur.md) § 3.8 · [Sven](personnages/sven.md) · [les voix de l'histoire](voix-de-l-histoire.md)

Comment donner à une réplique la couleur d'un accent étranger — Sven parle un français
correct avec une voix norvégienne, et d'autres viendront (M16, « les 34 personnages de
plus ») — **sans casser le juge qui garde le texte affiché et la voix identiques.** Écrit
le 22 sept. 2026, après que Martin a demandé comment respeller phonétiquement un accent.

## 1. La contrainte qui décide de tout

Chaque réplique porte deux chaînes : `texte` (affichée dans la boîte de dialogue) et
`jeu=` (envoyée telle quelle à ElevenLabs — `interpretation.dit()`, `app/interpretation.py:363`,
retourne `JEU.get(slug, texte)` sans reconstruction). Un juge exige qu'elles disent
**les mêmes mots** :

```python
# tests/test_interpretation.py:38-45
def test_le_jeu_dit_exactement_les_mots_de_la_boite(voix):
    dit = interpretation.dit(voix)
    assert interpretation.mots(dit) == interpretation.mots(voix["texte"])
```

`mots()` (`app/interpretation.py:372`) retire les balises `[...]`, met en minuscules
(`casefold`), puis découpe sur `\w+` — **les tirets et les apostrophes séparent déjà les
mots**, y compris ceux qui existent dans l'orthographe normale (« aujourd'hui » →
`aujourd`, `hui`). Résultat : toucher à l'intérieur d'un mot dans `jeu=` — lui ajouter une
apostrophe, un tiret, une lettre en trop — change son ou ses tokens, et le juge rougit.

⚠️ **Les trois trucs qu'ElevenLabs recommande officiellement pour respeller un mot
phonétiquement — majuscules, tirets, apostrophes autour d'une lettre, orthographe
alternative complète (source : [Best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices))
— sont donc bloqués ici dès qu'ils ajoutent de la ponctuation ou changent une lettre**,
sauf un seul (§ 3). Et même s'ils passaient le juge, le texte affiché doit rester du
français correct (`docs/ecrire-drole.md` § 5 : « accents corrects ») — un mot respellé
dans la boîte serait lu comme une faute, pas comme un accent.

## 2. Ce qui marche déjà : le vocabulaire et la syntaxe

C'est la technique en place pour Sven (`docs/personnages/sven.md`), et elle ne touche à
rien que le juge surveille — `texte` et `jeu` restent le même français, juste un
français **construit différemment** :

> « Un français correct, pas québécois : pas de sacre, pas de diminutif, pas de
> "pantoute" — c'est ce qui le marque comme n'étant "pas d'ici", plus encore que
> l'accent. »

| Levier | Ce que ça donne | Exemple (Sven, m52) |
|---|---|---|
| Pas de contraction familière | phrases pleines, jamais relâchées | « Je ne sais pas » et non « J'sais pas » |
| Pas de sacre ni diminutif | un registre neutre, presque administratif | « mon grand », « right-là » : jamais |
| Phrases courtes, sujet-verbe-complément | un rythme économe, sans fioriture | « Propre. C'est tout ce que je demande. » |
| Vocabulaire précis plutôt qu'idiomatique | pas d'expression imagée du cru | « discret » plutôt que « qui se tient tranquille » |

Cette recette se transpose à toute origine à venir : ce qui rend un personnage
« pas d'ici » à l'oreille, c'est presque toujours **ce qu'il ne dit jamais** (le sacre,
le diminutif, l'expression figée) plus qu'un accent posé sur les syllabes.

## 3. La prosodie — un levier libre, au-delà d'ElevenLabs

Ce que la vraie phonétique d'une langue change dans un accent, ce sont d'abord des
**sons** : quel `r`, quel `u`, quelle voyelle nasale un locuteur remplace par celle de sa
langue première. Des exemples réels, purement à l'oreille — `v` assourdi en `f` en fin de
mot chez un germanophone, `u` français lu `ou` chez un anglophone ou un hispanophone, un
`r` moins guttural ([Lingoda](https://www.lingoda.com/blog/fr/erreurs-de-prononciation-que-les-anglophones-font-en-francais/),
[passerelle-fle](https://passerelle-fle.over-blog.net/pages/Les-difficultes-de-prononciation-de-locuteurs-germanophones-d-allemagne-au-cours-de-l-apprentissage-du-francais-premiere-partie--2025594.html)).
Ça, seules la voix et la balise d'accent (§ 4) peuvent le porter : aucune lettre de
`jeu=` ne peut bouger sans casser le juge (§ 1).

Mais la phonétique dit aussi comment une langue **rythme** la phrase — et ça, la
ponctuation le porte très bien, parce que `mots()` (`app/interpretation.py:372`)
l'ignore complètement : virgule, point de suspension, point, tout disparaît avant la
comparaison. `jeu=` peut donc respirer, couper une phrase en deux, hésiter, **sans
qu'un seul mot ne change** — un levier resté ouvert, qu'aucun juge ne surveille. C'est
aussi ce qu'ElevenLabs recommande pour toute réplique, accent ou pas : de très longues
phrases confondent le modèle ; couper aux endroits où on marquerait normalement une
pause aide beaucoup ([Best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)).

| Origine | Ce que dit la phonétique | Ce que ça donne dans `jeu=` |
|---|---|---|
| Scandinave (Sven : Norvège) | langue à **accent de hauteur** — la mélodie monte et descend sur la syllabe portée, un débit presque chanté et mesuré, jamais pressé ([Alma Musica](https://www.alma-musica.net/html/documents/nordic.html), [Wiktionnaire — norvégien](https://fr.wiktionary.org/wiki/Annexe:Prononciation/norv%C3%A9gien)) | une pause franche avant le mot qui porte l'idée, pas un débit continu — « Sven. … J'ai du travail pour quelqu'un de discret. » |
| Anglophone | rythme **accentuel** (stress-timed) : les syllabes non accentuées se compriment entre deux temps forts, à l'inverse du français qui les étale ([Linguistic Rhythm in Foreign Accent — Yuan](https://www.ling.upenn.edu/~jiahong/publications/c01.pdf)) | des groupes de mots collés, puis une coupure nette — pas un débit régulier |
| Hispanophone / italophone | rythme **syllabique**, voyelles pleines non réduites — un débit égal, presque mécanique, à l'oreille française (même source) | peu de pauses courtes ; la phrase coule jusqu'au bout de l'idée, pas de respiration au milieu |

⚠️ Ce ne sont pas des règles vérifiées par un juge — comme tout ce document au-delà de
§ 1 et § 5, **c'est une audition qui tranche**, pas une formule. Et ça complète § 2 sans
le remplacer : le rythme appuie le vocabulaire — les phrases courtes de Sven (§ 2) sont
déjà, sans le nommer, un choix qui suit l'accent de hauteur du norvégien.

## 4. Ce qui marche : une balise d'accent, une fois, en tête

⚠️ **Confirmé à l'oreille par Martin le 22 sept. 2026** (« c'est mieux ») — c'est la
recette retenue pour Sven, et pour toute voix multilingue à venir (M16, « les 34
personnages de plus »).

Eleven v3 comprend des balises entre crochets comme `[French accent]`, `[German accent]`,
`[Norwegian accent]` — n'importe où dans le script selon la doc officielle ([v3 Audio
Tags](https://elevenlabs.io/blog/eleven-v3-audio-tags-emulating-accents-with-precision)),
mais **la règle retenue dans ce projet** (`docs/jeu-d-acteur.md` § 3.8) est plus prudente :
**une seule balise d'accent par réplique, en tête** — elle prendrait la place de
l'émotion si elle traînait au milieu. `ACCENTS` (`app/interpretation.py`, à côté de
`TONS` et `CORPS`) est la liste fermée de ce qui a été écouté et validé ; un juge
(`test_une_balise_d_accent_est_seule_et_en_tete`, `tests/test_interpretation.py`)
garde la règle « une seule, en tête » pour toute réplique qui en porte une.

Ce que ça donne pour Sven (`app/missions/m52.py`) :

```python
_l("sven", "Sven. J'ai du travail pour quelqu'un de discret. Le quai, ce soir.",
   jeu="[Norwegian accent][calm] Sven. [matter-of-fact] J'ai du travail… pour "
       "quelqu'un de discret… [firmly] le quai, ce soir.")
```

**Avant d'ajouter un accent pour un nouveau personnage** : écouter d'abord (générer une
seule réplique, jamais les 26 d'un coup — c'est ce qui a été fait ici), puis seulement
si ça sonne bon, ajouter la balise à `ACCENTS` et régénérer le reste. Une fois la balise
retenue, la prosodie (§ 3) est le levier suivant à travailler — une pause de plus avant
le mot qui porte l'idée, sur les répliques qui n'en avaient encore aucune à l'intérieur
d'une phrase, comme ci-dessus (« du travail… pour »).

### Ce qui n'a pas été retenu : des majuscules à l'intérieur d'un mot

Essayé avant de trouver la balise d'accent — écarté une fois celle-ci confirmée
meilleure. Seul truc de respelling qui **passe** le juge tel quel (`casefold()` ignore
la casse, donc une majuscule au milieu d'un mot ne change aucun token) : la doc
ElevenLabs en donne un exemple pour forcer l'appui sur une syllabe (`trapezii` →
`trapezIi`, [Best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)) —
mais c'est documenté pour lever une ambiguïté de prononciation anglaise, pas pour
fabriquer un accent. Reste une piste si une origine à venir n'a pas de balise
`[<pays> accent]` reconnue par v3 : un essai à l'oreille, pas une recette.

## 5. Ce qui reste fermé

Respeller vraiment un mot phonétiquement (« aujourd'hui » → « ossheurD'hui ») pour
que la voix le prononce autrement **exige que `texte` et `jeu` divergent**, ce que le
juge interdit par conception (`docs/voix-de-l-histoire.md` : « la voix dit les mêmes
mots que la boîte »). Le débloquer voudrait dire soit :

- accepter un texte affiché à l'orthographe modifiée (contraire à `docs/ecrire-drole.md`,
  « accents corrects ») — écarté ;
- ou ajouter un troisième champ (une prononciation propre à la voix, jamais affichée,
  exemptée du juge mot-à-mot) — un changement d'architecture, pas une astuce d'écriture.

**À trancher par Martin** si le besoin se présente vraiment — ce document ne le fait
pas de lui-même.

## Sources

- [Best practices — ElevenLabs](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- [Eleven v3 Audio Tags: Master AI Accent Emulation — ElevenLabs](https://elevenlabs.io/blog/eleven-v3-audio-tags-emulating-accents-with-precision)
- [Audio Tags 101: Directing emotional TTS in Eleven v3 — ElevenLabs](https://elevenlabs.io/blog/v3-audiotags)
- [Erreurs de prononciation que les anglophones font en français — Lingoda](https://www.lingoda.com/blog/fr/erreurs-de-prononciation-que-les-anglophones-font-en-francais/)
- [Difficultés de prononciation des germanophones en français — passerelle-fle](https://passerelle-fle.over-blog.net/pages/Les-difficultes-de-prononciation-de-locuteurs-germanophones-d-allemagne-au-cours-de-l-apprentissage-du-francais-premiere-partie--2025594.html)
- [Prononciation des langues scandinaves — Alma Musica](https://www.alma-musica.net/html/documents/nordic.html)
- [Annexe:Prononciation/norvégien — Wiktionnaire](https://fr.wiktionary.org/wiki/Annexe:Prononciation/norv%C3%A9gien)
- [Linguistic Rhythm in Foreign Accent — Jiahong Yuan (UPenn)](https://www.ling.upenn.edu/~jiahong/publications/c01.pdf)
