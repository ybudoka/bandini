# Le scanner de police a perdu ses deux voix

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Trouvé le 24 sept. 2026, en livrant la dernière partie de [M15](m15-la-ville-te-parle.md)._

_Ce que ça donne :_ la police au scanner redevient la police, et pas la dame du casse-croûte.

⚠️ **Le juge le disait déjà, et il avait raison**
(`test_ondes.py::test_la_police_n_a_la_voix_ni_d_un_passant_ni_d_un_personnage`) : les deux voix
du scanner ne doivent appartenir à personne d'autre. « Une voix de la rue au bout du scanner, on
croirait que la passante d'à côté appelle la police ; celle d'un personnage, qu'il s'est fait
engager. »

Les dix missions du 23 sept. 2026 ont donné les deux :

- **Caroline — Soft Quebec accent** est la **répartitrice** du central (`audio.VOIX_REPARTITRICE`,
  cinq répliques) et, depuis, la voix de **Mado** au casse-croûte ;
- **Alexandre Boutin — Professional** est l'**agent** sur le terrain (`audio.VOIX_AGENT`, cinq
  répliques) et, depuis, celle du **Grand Mo** et de **Gégé**.

Personne n'a rien cassé : trois sessions ont pioché dans les voix libres du compte le même jour,
et la liste des voix prises est écrite à deux endroits (`audio.py` pour la police,
`missions.PERSONNAGES` pour les gens).

**Ce que ça coûte.** Le remède n'est pas un `if` : il faut **régénérer** des clips.

⚠️ **Le quota n'est plus l'obstacle** — Martin a pris un **nouveau forfait** le 24 sept. 2026, le
jour même où cette ligne a été écrite. Il reste à choisir deux voix libres du compte
(`scripts/audio_elevenlabs.py --voix` dit lesquelles des voix nommées existent ; le compte en a
plus que le dépôt n'en nomme). Deux chemins, et c'est à Martin de trancher :

- **la police change de voix** — dix clips à refaire (`police_*_r`), deux voix libres à choisir
  dans le compte ; le scanner est un bruit de fond, personne ne le reconnaîtra ;
- **les trois personnages changent de voix** — plus de clips (Mado en a sept, Mo et Gégé les
  leurs), et trois personnages qu'on a peut-être déjà écoutés.

Le premier chemin est le moins cher et le moins risqué.

⚠️ **Et un troisième, écarté** : transposer les dix clips en post-production plutôt que de les
régénérer — la vitesse de bande (`asetrate` + `atempo`) déplace le pitch **et les formants**, donc
le corps de la voix, et le scanner coupe déjà tout sous 300 Hz ; `--refinir` rejoue la finition
depuis les masters **sans un crédit**. C'était le bon chemin tant que le quota était à sec ; il ne
l'est plus. Deux vraies voix valent mieux qu'une voix déguisée, et la transposition reste ce
qu'elle est : un outil pour réutiliser un fond, pas pour économiser des crédits qu'on a.

⚠️ **Et le vrai correctif est ailleurs** : rien n'empêche la prochaine session de reprendre une
voix déjà prise. `scripts/audio_elevenlabs.py --voix` sait dire quelles voix du compte existent ;
c'est là qu'un juge doit refuser une voix réservée à deux usages — la table de ce qui est pris,
écrite **une fois**. Sans ça, le même jour se répétera.

## Notes

_Rien de livré._
