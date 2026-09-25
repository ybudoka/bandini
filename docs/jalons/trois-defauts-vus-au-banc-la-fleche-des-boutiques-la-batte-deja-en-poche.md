# Trois défauts vus au banc : la flèche des boutiques, la batte déjà en poche, ACTION près d'un char

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 25 sept. 2026 (« oui ») : les trois défauts vus en jouant les missions plus longues au banc, et
laissés dans les notes de [des missions plus longues](des-missions-plus-longues.md#notes).

- **`boutique:artisan` et `boutique:industrie` ne mènent nulle part.** `boutiquex` cherche le mot dans le
  TEXTE des enseignes ; « artisan » est le GENRE de la devanture (la quincaillerie). Pas de flèche, pas de
  losange, et la coupe d'intro du défaut de f04 et p01 ne trouve pas son lieu.
- **Dans p01, acheter la batte est fait d'avance** pour qui a joué m2 (qui la donne) : `acheter` regarde
  la poche, pas l'achat.
- **À 36 px d'un char, ACTION y remonte au lieu de parler à la personne** qu'on regarde.

## Notes

Livré le 25 sept. 2026. Juges : `tests/test_trois_defauts_js.py` (les trois mordent, vérifié en retirant
chaque règle).

- **La flèche des boutiques** : `boutiquex` (`histoire.js`) reconnaît un GENRE de devanture
  (`B.defs.devantures.genres`) et mène à la devanture la plus proche de ce genre, une qu'on VISITE d'abord
  (une porte peinte ne vend rien). Un mot d'enseigne se cherche encore dans le texte. ⚠️ Ça répare aussi
  deux des [neuf juges rouges](neuf-juges-rouges-sur-dev.md) : les intros de f04 et p01
  (`test_chaque_intro_se_joue_seule_et_rend_la_ville[f04-défaut]`, `[p01-défaut]`), dont la coupe du
  défaut allait vers `boutique:artisan`.
- **La batte déjà en poche** : `acheter` passe encore (le comptoir affiche « DÉJÀ À TOI » et ne revend
  pas une arme qu'on a), mais le jeu le DIT — « DÉJÀ DANS TES POCHES ». `avancer` note si l'article était
  en poche quand l'étape a commencé ; un vrai achat ne le dit pas. Vaut pour toute mission `acheter`.
- **ACTION près d'un char : pas un défaut.** Rejoué au banc sous dix placements : la personne passe
  toujours avant la portière (`Missions.interagir` d'abord). Ce qu'on avait vu : un camion garé contre
  Ti-Paul REPOUSSAIT le joueur hors de portée de voix (22 px). Le commentaire du juge de q02, qui accusait
  l'ordre, est corrigé, et un juge tient maintenant cet ordre.
