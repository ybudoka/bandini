# Les contacts du tour parlent à la poignée de main

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (20 sept. 2026), sur l'intro du tour du propriétaire : « il manque aussi des voix pour
cette animation » et « il faudrait aussi enrichir leur dialogue en même temps ». Réponses de Martin :
**à la poignée de main** (pas dans le montage), **une réplique chacun**.

- ⚠️ **Mesuré avant** : les quatre contacts de m6 (Ti-Paul, Lulu, Raymonde, Ovila) n'avaient AUCUNE
  réplique. Un objectif `parler` s'accomplit en parlant à sa cible, et `Histoire.parler` faisait alors
  `avancer()` tout de suite : la poignée de main était muette. Seules Josée (huit répliques) et leur bulle
  de hèlement (« Salut, l'ami! ») parlaient.
- **Une partie `accueil`** (`_a(qui, texte, objectif)`), comptée APRÈS `renvoi` dans `PARTIES` — aucun
  mp3 déjà payé ne change de nom : `tipaul-m6-9`, `lulu-m6-10`, `raymonde-m6-11`, `ovila-m6-12`. Elle
  se dit **en personne** à la poignée de main, puis l'objectif avance (`dire` appelle `fin` une fois la
  boîte fermée, et tout de suite quand la fiche n'écrit rien : la poignée muette d'avant). Le juge de
  forme refuse un accueil accroché à un objectif qui n'est pas un `parler` dont `qui` est la cible.
- **Un mot de chacun, dans son registre** : le bavard (« rien passe sans que je le sache »), la sœur qui
  materne (« t'as l'air d'un fantôme »), la syndicaliste qui jauge (« ça reste à voir »), le gardien qui
  guette (« je vois tout ce qui entre »). Leur jeu garde le registre de leur repos : `cheerful`/`knowingly`,
  `warmly`/`teasing`, `firmly`, `calm`. Le plafond de répliques passe à 12 **pour m6 seulement**
  (`PLAFONDS` dans `test_missions.py`) : les autres restent à 10.
- **Quatre voix** (347 caractères) : 5,9 s, 7,0 s, 6,4 s et 5,1 s ; −19,5 LUFS ; pas un trou d'une
  seconde (le plus long, 0,96 s, chez Lulu, juste avant « fantôme »). Suivant le guide du jeu d'acteur,
  UNE réplique clé (Ti-Paul, la plus risquée : deux tons dans la phrase) a été générée d'abord et Martin
  l'a écoutée (« ça va ») avant le reste. ⚠️ Les trois autres n'ont été que mesurées : `--refaire <slug>`
  si l'une sonne faux.
- **Deux juges** : la poignée de main au banc (chaque contact : sa boîte, en personne, sa voix demandée,
  l'objectif n'avance qu'à la fermeture ; sans `accueil`, il avance à l'instant — rouge avec l'ancienne
  poignée muette) et la forme (`test_mise_en_scene.py`).
