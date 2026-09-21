# Le narrateur du Clairon de la Baie

← [les personnages](README.md) · [le jeu d'acteur](../jeu-d-acteur.md)

> « T'arrives avec cinquante piastres pis un billet aller simple. Bonne chance, le jeune. » — l'ouverture

## En bref

| | |
|---|---|
| Slug | `narrateur` |
| Rôle | la voix du journal _Le Clairon de la Baie_ : il ouvre le jeu, lit la manchette chaque matin, et fermera le jeu (le générique, M13) |
| Où | nulle part (`ou` vide) : on ne lui parle jamais, on l'entend |
| Voix | **annonceur centre d'achat 1** — une voix générée, un vieil homme qui soupire (partagée avec Ovila : jamais dans le même dialogue) ; passée à l'isolateur (`VOIX_A_SECHER`) |
| Bulle | aucune |
| Missions | aucune : l'**ouverture** (`OUVERTURE`, quatre phrases) et le **journal** du matin (`journal.py`) |

## Son histoire

Personne ne sait son nom. Il a écrit les chiens écrasés du _Clairon_ pendant quarante ans, puis les
nécrologies, puis plus rien ; aujourd'hui, il lit. Il a vu passer trois maires, deux incendies du port et
toute la carrière de Rocco Bandini, en entrefilets. C'est lui qui te dit, avant que tu descendes du car,
que ton oncle est mort, ce dont tu hérites et ce que tu dois (l'ouverture) — et c'est lui qui racontera,
un matin, comment tout ça a fini.

## Sa personnalité

- **Ce qu'il veut** : que l'histoire soit bien racontée. Il n'a pas de camp.
- **Ce qu'il cache** : de la tendresse pour les perdants.
- **Sa nature** : un soupir fait homme. Tout l'amuse un peu, rien ne le surprend.

## Comment il parle

- **La voix d'un journal parlé de province** : des phrases posées, un mot d'esprit par paragraphe (« du
  monde qui se mêle de ses affaires », l'ouverture).
- **Il tutoie le joueur, et lui seul** : « Bonne chance, le jeune. » Le reste du temps, il parle de la ville
  à la troisième personne, ou vouvoie son lecteur dans le journal (« Votre char a disparu? »).
- **Balises de base** : `[serious]`, `[matter-of-fact]`, `[dramatic]` pour une manchette, `[somber]` pour une
  mort, `[wryly]`/`[sarcastic]` pour la chute ; `[sighs]` pour le corps.
- **Ce qu'il ne dit jamais** : « je » ; son nom.

## Comment il salue et se présente

**Il ne se présente pas, et c'est voulu.** L'ouverture n'a **aucun nom** au-dessus de sa boîte (`anonyme` dans
`histoire.js`) : c'est une voix qu'on entend, pas quelqu'un à qui l'on parle. Le journal le présente à sa
place — le titre du _Clairon_ et la manchette du matin. La règle « qui parle se nomme » ne le vise pas : il
n'est jamais au téléphone et on ne le rencontre jamais (`missions.on_le_rencontre` le dit).

## Ses liens

Avec tout le monde, et avec personne : il les a tous imprimés.

## Ce qu'il a dit (le canon)

- L'ouverture : Baie-des-Brumes, « un port, du brouillard » ; ton oncle Rocco est mort le mois passé ; le
  garage, la planque, le nom ; la dette de quinze mille piastres à Sal le Barbier ; cinquante piastres et un
  billet aller simple.
- Le journal : les manchettes du matin et les leçons (`journal.py`).

## À trancher

- Son **passé de chroniqueur** est une proposition de cette fiche.
