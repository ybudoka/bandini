# Le fondu de l'hôpital et de la prison

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Le fondu de l'hôpital et de la prison (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « il faut corriger le fade out et in quand on va à l'hôpital ou qu'on
se fait enfermer. »

Les portes avaient reçu leur machine : `transiter([fermer, ouvrir], faire)` noircit sur la
scène qu'on quitte, change **au noir**, éclaircit sur la nouvelle, et fige le jeu pendant.
⚠️ **Quatre changements de scène étaient restés derrière** — l'hôpital, la prison, la
compagnie (« on reprend son souffle ») et le coucher (« le lendemain matin »). Ils faisaient
ceci :

```js
Hud.fondu(150, "REVEIL A L’HOPITAL — " + facture + " $");
setTimeoutJeu(60, function () {
  /* on téléporte le joueur */
});
```

⚠️ **Le vrai défaut n'était pas le fondu, c'étaient DEUX HORLOGES que rien ne liait.**
`Hud.fondu` comptait dans le **dessin** (`dessinerFondu`), `setTimeoutJeu` comptait dans la
**mise à jour** (`majMinuteries`). Rien n'attachait le 60 au 150 : changer l'un ne bougeait
pas l'autre, et le changement de scène pouvait glisser n'importe où sur la courbe sans
qu'aucun test ne bronche. Tout le reste en découlait :

- **Le décor changeait à 80 % de noir, pas au noir.** `dessinerFondu` montait l'alpha à
  `t / durée × 2` : à l'image 60 d'un fondu de 150, on était à **0,8**. On se regardait
  disparaître de la rue et réapparaître à l'hôpital à travers un voile transparent d'un
  cinquième.
- **Le texte s'écrivait sur une rue qu'on voyait encore** : entre 35 % et 75 % du fondu, donc
  avant le noir et fini avant la clarté. « RÉVEIL À L'HÔPITAL — 120 $ » se lisait par-dessus
  le trottoir où l'on venait de tomber.
- **Et le jeu n'était pas figé.** Pendant les deux secondes et demie, la ville continuait de
  tourner, la caméra restait sur l'ancien endroit, et le joueur gisait à 1 PV au milieu de la
  rue — un char pouvait lui repasser dessus pendant l'écran noir.

Ce qui a été livré, dans l'ordre de ce qui se voit :

- **Les quatre passent par `Jeu.transiter()`**, exporté pour l'occasion (il était interne à
  `jeu.js`, et `missions.js` en avait besoin). Une seule horloge, et la scène change **pile**
  à alpha 1.
- **Un fondu qui raconte quelque chose tient le noir.** La machine a gagné un troisième
  nombre — `[fermer, tenir, ouvrir]`. ⚠️ Une porte, on la passe : rien à tenir, et les trois
  fondus de porte gardent leurs deux nombres. Mais l'hôpital, la prison et la nuit font
  **passer du temps**, et ce temps se sent dans le noir : `[40, 70, 40]` pour l'hôpital et la
  prison, `[32, 56, 32]` pour une nuit, `[24, 42, 24]` pour la compagnie. Le noir tenu fait la
  moitié de la durée — plus court, on n'a pas fini de lire ; plus long, on attend.
- **Le texte ne se dessine que pendant `tenir`**, quand l'écran est vraiment plein. Il n'est
  plus une option du HUD : il appartient à la transition, comme sa durée.
- **La ville est figée**, comme pour une porte : le même `if (B.etat === 'jeu' && B.transition)`
  la couvre, sans une ligne de plus. C'est ce qui règle le joueur à 1 PV laissé dans la rue.
- ⚠️ **Un fondu par-dessus un autre n'en empile plus deux.** `transiter()` appelle lui-même
  `finirTransition()` : celui qui joue finit tout de suite — sa scène change, **une fois** —
  et le nouveau repart du clair. C'était déjà la règle des portes ; se faire arrêter pendant
  le fondu de l'hôpital la demandait aussi, et personne ne l'aurait vue en la codant quatre
  fois à la main.
- **Ce qui disparaît** : `Hud.fondu`, `dessinerFondu`, `B.fondu`, et — puisque plus personne ne
  s'en servait — `setTimeoutJeu`, ses minuteries et `majMinuteries`. **Il ne reste plus une
  seule deuxième horloge dans le jeu**, et c'était tout l'objet du correctif.
- ⚠️ **Un juge du trafic a cassé, et il avait raison de casser.** Celui du char hors voie
  (`tests/test_trace_js.py`) posait un char roulant à 32 px du joueur : il l'écrasait, et
  depuis que l'hôpital fige la ville, ses 120 images de surveillance ne surveillaient plus
  rien. Ce test juge le trafic, pas la santé du joueur — il le rend intouchable, et il dit
  pourquoi.
- **Juges (2 neufs)** : le premier mesure, image par image, l'alpha **à l'instant exact** où
  le joueur est téléporté (1,0 exigé) et l'alpha à **chaque** fois que le texte est écrit
  (`Atlas.texte` est espionné : le banc ne garde aucun pixel), pendant qu'un passant et un
  char servent de témoins que rien ne bouge dans le noir. Le second se fait arrêter au beau
  milieu du fondu de l'hôpital et vérifie qu'on se réveille bien à l'hôpital **puis** au poste,
  chacun une fois, sans un fondu resté ouvert. Quatre juges existants ont été rejoués à la
  nouvelle machine : la compagnie, l'hôpital, le coucher au lit de la planque et le souffle
  perdu la nuit lisent maintenant `B.transition`, et jouent le fondu avant de mesurer.

## Notes

demande de Martin (« il faut corriger le fade out et in quand on va à l'hôpital ou qu'on se
fait enfermer ») : quatre changements de scène — l'hôpital, la prison, la compagnie, le
coucher — étaient restés sur `Hud.fondu` + `setTimeoutJeu`, soit **deux horloges** que rien
ne liait : l'une comptait dans le dessin, l'autre dans la mise à jour. On se regardait donc
disparaître de la rue à **80 % de noir**, le texte se lisait par-dessus le trottoir où l'on
venait de tomber, et la ville continuait de tourner pendant les deux secondes et demie — un
char pouvait repasser sur un joueur à 1 PV. Les quatre passent maintenant par la machine des
portes, `Jeu.transiter()`, qui n'a **qu'une** horloge et change la scène **pile** à alpha 1.
Elle gagne pour eux un troisième nombre, `[fermer, tenir, ouvrir]` : une porte, on la
passe ; une nuit, un séjour à l'hôpital **font passer du temps**, et ce temps se sent dans
le noir tenu, où le texte s'écrit — et **seulement** là. `Hud.fondu`, `setTimeoutJeu` et
leurs minuteries sont supprimés : plus une seule deuxième horloge dans le jeu
