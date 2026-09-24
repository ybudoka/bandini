# Les musiques s'enchaînent en fondu

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (20 sept. 2026) : « les transitions de musique doivent toujours se faire en
crossover, à moins que ce soit nécessaire pour l'effet et l'ambiance ». C'est une **règle
permanente** : toute musique qui en remplace une autre le fait en fondu enchaîné, et la coupure
franche est l'exception qu'on justifie.

- ⚠️ **Mesuré avant** : rien ne s'enchaîne. `Mus.jouer` appelle `Mus.arreter`, qui coupe la
  boucle (`source.stop()`) avant que la suivante démarre ; `Radio.arreter` et
  `Ambiance.arreter` font pareil ; `musique.MUSIQUE.fondu_s` (2 s) est déclaré côté Python et
  **le JS ne le lit jamais**. Ce qui s'entend : changer de district, monter dans un char à
  radio, entrer dans un commerce, passer à la poursuite ou en revenir — chaque fois un blanc
  ou un coup sec.
- ⚠️ **Livré** (`son.js`, section « Le fondu enchaîné »). `boucle(slug, actif, volume, fondu)` :
  la piste qui sort quitte `boucles` tout de suite (sa clé est libre) et baisse sur `fondu`
  secondes ; celle qui entre monte depuis zéro. `Mus.jouer(slug, fondu)` et `Mus.arreter(fondu)`
  fondent par défaut sur `fondu_s` ; la radio enregistrée, l'ambiance enregistrée et les deux
  fins du musicien de rue passent par la même porte. **Le séquenceur (le filet, sans mp3) fait
  aussi son fondu** : l'ancienne piste reste en `Mus.sortantes` et continue de poser ses notes,
  dans sa chaîne qui baisse, jusqu'au bout de la courbe — il ne programme qu'un quart de seconde
  d'avance, sans quoi elle se serait tue avant d'avoir de quoi baisser.
- ⚠️ **Deux gains par fondu, et des courbes sin/cos.** Mesuré dans un vrai Chromium : une
  courbe posée sur un paramètre qui en suit déjà une lève `NotSupportedError` — avec un seul
  gain, changer de piste pendant la montée de l'autre fait taire la musique. D'où `entree` puis
  `sortie`. Et la puissance constante (sinus, cosinus) plutôt qu'une rampe linéaire : deux
  morceaux sans rapport sonnent deux fois moins fort au milieu d'une rampe (0,49 mesuré).
- ⚠️ **La règle, et son exception.** Le fondu est ce qui arrive **par défaut** à toute la musique.
  Une coupure franche se **demande** (`Mus.jouer(slug, 0)`, `Mus.arreter(0)`) et se justifie à
  l'appel ; aujourd'hui un seul appel le fait, `Son.fermer()` (la page s'en va). Une exception de
  **durée** existe, `musique.MUSIQUE.fondu_vif_s` (0,7 s) : la poursuite et la bagarre entrent
  vite — sinon on les entend après les avoir vues — mais **en fondu** ; le musicien de rue s'éclipse
  sur la même durée. Le retour à la ville, lui, se fait sur `fondu_s` : le joueur souffle.
- ⚠️ **Pas touché, exprès** : les moteurs, sirènes et la rumeur de la foule ne sont pas des
  musiques, ils coupent net comme avant (`boucle` sans `fondu`).
- ⚠️ **Limite connue.** Si le mp3 suivant met plus de `fondu_s` à arriver, l'ancienne piste est déjà
  partie : un blanc, comme avant, mais plus court. Garder l'ancienne jusqu'à l'arrivée de la
  nouvelle, ou précharger les districts voisins, serait la suite — pas fait.
- **Juges** : au banc, `test_une_musique_qui_en_remplace_une_autre_se_fond_dedans` (les trois
  moitiés du fondu, la puissance constante, la durée lue de Python),
  `test_eteindre_la_musique_est_un_fondu_et_zero_est_une_coupure`,
  `test_toutes_les_portes_de_la_musique_passent_par_le_fondu` (Mus, radio, ambiance, rue ×2),
  `test_le_sequenceur_fait_aussi_son_fondu_pas_seulement_le_mp3`,
  `test_la_musique_d_etat_entre_vite_mais_en_fondu_et_la_ville_revient_doucement`,
  `test_changer_de_piste_pendant_un_fondu_ne_fait_pas_planter_la_musique` ; en Python, la durée
  exportée ; et **dans un vrai Chromium**, `test_le_fondu_enchaine_marche_pour_de_vrai_dans_le_navigateur`
  (il lit la valeur des paramètres pendant que ça descend). Le faux contexte du banc note maintenant
  les courbes (`__courbes`) et l'instant d'arrêt des sources (`__arretT`), et lève la même erreur
  que le navigateur si deux courbes se chevauchent. Vus **rouges** : 15 mutations au banc (chaque
  porte, la courbe linéaire, la durée en dur, le gain unique, l'arrêt avant la fin de la courbe…) —
  et chacune ne fait tomber que la porte visée — puis 3 dans le navigateur.
