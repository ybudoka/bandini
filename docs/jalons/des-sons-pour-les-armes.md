# Des sons pour les armes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« fait moi des sons pour les armes ») : toutes les armes jouaient le
**coup de poing** — la batte, le couteau, le pistolet et le fusil aussi (`majAttaque` et
`tirer` appelaient `SFX.coup`), le jet d'extincteur ne faisait aucun bruit, et un chargeur
vide comme une arme qui casse faisaient le **buzzer de refus** des menus. Chaque arme porte
maintenant son `son` (`armes.py`) et le combat passe par `SFX.arme(def)` ; **16 échantillons
ElevenLabs** (batte ×2, couteau ×2, pelle, cône, bouteille, fronde, pistolet ×2, fusil ×2,
le **jet en boucle** tenu par `SFX.jet(actif)` à chaque image, la gâchette **à vide**, la
**casse**, le **dégainage**), ≈ 141 Ko, chacun avec son repli synthétisé ; budget des
bruitages relevé à 800 Ko.

- ⚠️ Au passage, un **hoquet** au départ du jet : la première pression partait par le chemin
  de la mêlée (anticipation, quatre images de jet, deux de repos) avant que le maintien ne
  prenne le relais — invisible, mais audible avec une boucle.
- ⚠️ **Martin n'a pas encore écouté** : `batte-1` et `batte-2` sont sortis très courts (0,18
  et 0,26 s), à refaire s'ils ne sonnent pas (`--refaire batte`)
- ⚠️ **Correctif, 15 sept. 2026** (retour de Martin : « le son des bornes-fontaines brisées
  n'est pas correct ») : la borne jouait **`SFX.choc`** — la tôle froissée d'une collision —
  au bris **et toutes les 24 images pendant les dix secondes du jet**. Mesuré : **26 sons
  d'accident de char pour une borne défoncée**, dont le premier en doublon avec le char qui
  vient de la renverser (`heurterDecor` joue déjà `choc` à la même image). Deux sons
  désormais, et la frontière est nette : **le bruit de l'impact appartient à ce qui a
  défoncé**, la borne n'a que son bouchon et son eau. `borne_cassee` — le bouchon qui saute,
  la tôle qui cède, l'eau qui s'ouvre — **une seule fois** ; `borne_jet(force)` — un souffle
  **tenu**, appelé à chaque image avec la vérité du moment (le patron de `jet()` de
  l'extincteur), dont le volume **suit la distance** (portée 260 px) et qui se tait quand la
  gerbe meurt.
- ⚠️ Les deux sont **entièrement synthétisés** : le seau des bruitages est à 14 Ko de son
  plafond, et le navigateur ne réclame au catalogue que des slugs que Python déclare (un
  juge le tient) — le jour d'une séance ElevenLabs, la fiche gagnera ses deux entrées et ces
  fonctions leur repli, ensemble. 2 juges de banc, rouge-avant prouvé (26 chocs)
