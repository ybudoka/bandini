# Aucun son n'a jamais joué

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (« j'ai le son de la page titre, mais rien ensuite ») — et c'était bien
pire que ça. Dans `echantillon()`, **`source.connect(gain)` manquait** : la source n'entrait
dans aucune chaîne. Tout le reste était juste — le fichier se téléchargeait (200), se
décodait (tampon de 0,68 s, pic 0,22), la source démarrait, le gain était au bon volume
**et** relié au maître. Aucune erreur, aucun 404, aucune trace : **aucun des 79 fichiers
ElevenLabs n'a jamais été entendu** — ni un bruitage, ni une voix, ni une radio, ni
l'ambiance.

- ⚠️ Et le filet de synthèse ne prenait pas le relais, parce que `joue()` rend `true` dès
  que l'objet existe : ni échantillon, ni repli, **silence**. Deux pannes se masquaient
  l'une l'autre — le son retenu par le navigateur empêchait de découvrir celle-ci, et la
  musique du menu (de la **synthèse**, elle) l'a révélée en sonnant seule.
- ⚠️ Ce qui manquait, ce n'était pas un test de plus mais un test d'une autre **nature** :
  tous nos juges vérifiaient l'intention (fichiers servis, tampons décodés, sources
  démarrées, volumes justes) et tous étaient verts. Désormais on écoute la **sortie** : au
  banc, le faux AudioContext trace ses branchements et `atteintLaSortie(noeud)` exige un
  chemin jusqu'à la destination (3 juges, vérifiés en remettant le bug) ; au navigateur, un
  `AnalyserNode` posé sur la sortie mesure ce qui sort vraiment (3 juges : la synthèse, un
  échantillon, l'ambiance, le thème). Mesures après correctif : échantillon −35,7 dB
  (avant : **silence**), ambiance −25,8 dB, et l'écart menu/jeu retombe de **136 dB à 2,6
  dB**.
- ⚠️ **La même soudure manquait une seconde fois**, dans `Voix.parler()` : retour de Martin
  (« je n'entends pas les voix des gens dans les dialogues »). Les 44 répliques se
  chargeaient, `enCours` se posait, la radio baissait, le texte défilait — et rien ne
  sortait ; un juge existant vérifiait même que la réplique « se décode et baisse la
  radio », et il était vert. D'où un juge d'une portée plus large que les deux cas connus :
  `ctx.sourcesMuettes()` au banc recense **toute** source qui a démarré sans atteindre la
  sortie, quel que soit le chemin — on fait sonner bruitages, boucles, musique, répliques
  (dont une au téléphone, qui a un filtre de plus) et on exige zéro. Les deux bugs ont été
  remis exprès pour vérifier que les juges tombent.
- ⚠️ Effet de bord découvert au passage : ouvrir un `AudioContext` dès le chargement (pour
  savoir si le son est accordé) en laisse un ouvert par page — le navigateur en limite le
  nombre, et la suite navigateur devenait instable ; `Son.fermer()` sur `pagehide` rend la
  carte son. Et `Son.estCharge(slug)` répond « ce son est-il prêt ? » sans le **jouer** :
  les attentes de test le faisaient en démarrant une source à chaque sondage, jusqu'à faire
  caler le contexte
