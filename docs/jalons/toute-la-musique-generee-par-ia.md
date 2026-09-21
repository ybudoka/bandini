# Toute la musique générée par IA

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Toute la musique est générée par IA (**correctif**, taille 2) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « je veux que toutes les musiques soient des musiques générées par IA. »

Il en restait **quinze écrites en notes** : le thème du menu, les deux stations de char du
camion et de la remorqueuse, les cinq ambiances de district, la poursuite, la bagarre et les
cinq pièces du musicien de rue. Elles sont maintenant **quinze mp3 ElevenLabs Music** —
641 secondes, **5,2 Mo**, 30 crédits la seconde (mesuré : 1 350 crédits pour les 45 s du thème).

**La porte était écrite depuis le premier jour, mot pour mot.** `musique.py` s'explique en
tête de fichier depuis M7 : « le jour où Martin veut une vraie pièce jouée par de vrais
instruments, elle se posera **par-dessus** comme les radios — c'est la même règle que partout
dans `audio.py` : l'échantillon quand il existe, la synthèse sinon ». C'est exactement ce qui a
été fait, et c'est pour ça que la fiche est petite : rien n'a été remplacé, un étage a été posé.

- **Les notes restent, et ce n'est pas de la sentimentalité** — c'est la règle 1 d'`audio.py`.
  `exporter()` ne déclare que les fichiers **réellement présents** ; un dépôt frais, une
  génération ratée, un réseau coupé, et le séquenceur reprend le morceau exactement là où il
  est écrit. Le joueur n'a jamais un trou de musique. Un juge remet le cas : mp3 introuvable →
  les oscillateurs repartent.
- ⚠️ **Le slug ne change pas, et c'est tout l'intérêt.** Le chef d'orchestre demande
  `amb_quais` comme avant, le bouton RADIO du camion demande `station_camion`, l'hystérésis aux
  frontières, la queue des musiques d'état et l'échelle de priorité **n'apprennent rien**.
  Seul `son.js` sait, morceau par morceau, si c'est le fichier ou le séquenceur qui joue.
- ⚠️ **Deux volumes par morceau, et il en fallait deux.** Dans le séquenceur, le volume du
  morceau **multiplie** celui de chaque voix (0,11 à 0,45) : `titre` à 0,85 sort à un dixième
  de l'échelle. Un mp3, lui, arrive normalisé à −1 dBFS — le même chiffre saturerait. Python
  déclare les deux (`musique.py` pour les notes, `audio.MUSIQUES` pour le fichier) et le
  navigateur prend celui de la source qui joue.
- ⚠️ **Trois états de chargement, pas deux.** « en cours » n'est pas « ratée » : pendant le
  téléchargement on se **tait** quelques centaines de millisecondes, comme une vraie radio
  qu'on allume, plutôt que de lancer un bout de séquenceur qu'il faudrait couper net à
  l'arrivée du fichier. « ratée » rend la main aux notes pour de bon.
- ⚠️ **Deux clés de tampon** (`musique-` et `rue-`) : le musicien de rue joue **par-dessus**
  l'ambiance du district, comme un moteur de char — deux boucles tournent donc en même temps,
  et une clé partagée ferait que l'une chasserait l'autre. Son volume vient de la **distance**
  et se repose à chaque image (`Son.volumeBoucle` le rend lisible pour un juge) ; sa main
  gratte **en mesure** sur l'horloge audio, au tempo que Python déclare, puisqu'un mp3 n'a pas
  de « pas ».
- ⚠️ **Rien ne se charge au démarrage.** Une ambiance arrive quand on entre dans son district,
  une station au premier tour de clé, la toune du musicien quand on s'en approche. Le dépôt,
  lui, porte les 5,2 Mo.
- ⚠️ **On ne génère que ce que le jeu joue.** Une pièce dont le slug ne correspond à aucun
  morceau de `musique.py` serait un fichier **payé** que personne ne jouerait jamais :
  `musiques_manquantes()` filtre sur ce que `musique.exporter()` rend vraiment.

**Et un vrai défaut trouvé en chemin, qui ne touchait pas qu'au mp3.** `Son.Rue.tick()` passe
en tête de `maj()` dans `jeu.js`, alors qu'`Entites.maj()` — celui qui **demande** la toune du
musicien le plus proche — tourne tout à la fin, juste avant `B.t++`. La demande que le tick lit
porte donc **toujours** le numéro de l'image précédente, et le test d'égalité stricte
(`demandeT !== B.t`) réduisait le musicien au silence à l'image suivant chacune de ses
demandes, sans arrêt : sa musique ne démarrait **jamais**, ni en notes ni en fichier, et rien
ne le disait — `Entites` continuait sagement à la demander. Une image de retard est désormais
normale ; au-delà, plus personne ne joue. Le bug a été remis exprès pour vérifier que le juge
tombe.

⚠️ **Ce qu'aucun test ne dit** : si c'est beau. Quatre masters sortent à 0,0 dBFS (poursuite,
bagarre, le reel du trottoir) — au plafond, comme les radios de M3, et tenus en dessous par le
`volume` du catalogue. C'est l'oreille de Martin qui tranche, et `--refaire <slug>` qui refait.

**Juges** : 11 Python (`test_musique.py` — couverture : aucun morceau sans musique générée ;
aucune pièce payée pour un morceau qui n'existe pas ; le musicien de rue reste **un homme seul
avec une guitare** ; aucune batterie sous un district ; aucune voix chantée ; la boucle tient
24 s ; le budget du dépôt) et 6 de banc (`test_son_js.py` — le mp3 boucle **et** le séquenceur
se tait ; un mp3 qui n'arrive pas rend la main aux notes ; le ducking atteint les musiques en
mp3 ; le musicien suit la distance et s'arrête quand on le laisse derrière ; le musicien et le
district jouent ensemble ; le musicien n'est pas coupé à chaque image).

## Notes

demande de Martin : « je veux que toutes les musiques soient des musiques générées par IA ».
Les **15 pièces écrites en notes** (thème du menu, 2 stations de char, 5 ambiances de
district, poursuite, bagarre, 5 pièces du musicien de rue) deviennent des mp3 ElevenLabs
Music — c'est la porte que `musique.py` annonce depuis le premier jour : « le jour où Martin
veut une vraie pièce jouée par de vrais instruments, elle se posera **par-dessus** comme les
radios ». La synthèse reste le **filet** : un fichier absent, et le séquenceur reprend
