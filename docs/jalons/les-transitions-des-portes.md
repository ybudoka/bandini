# Les transitions des portes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les transitions d'entrée et de sortie (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Retour de Martin :_ « il faut améliorer les transitions quand on entre et sort des endroits.
La transition n'est pas juste. »

⚠️ **Elle n'était pas juste parce qu'elle arrivait dans le mauvais ordre.** `Jeu.entrer()`
chargeait la pièce, téléportait le joueur, recentrait la caméra — **puis** appelait
`Hud.fondu(40)`. Or ce fondu va de transparent à noir puis à transparent : sa première moitié
noircissait donc sur la scène **déjà changée**. On voyait la pièce une image, l'écran
noircissait, il s'éclaircissait sur la même pièce. Ce n'est pas un fondu enchaîné, c'est un
clignotement — et l'œil le sait même quand on n'arrive pas à le nommer.

L'ordre juste : **noircir sur l'ancienne scène → changer au noir → éclaircir sur la
nouvelle**. C'est maintenant `Jeu.transiter(durée, faire)` : `B.transition` porte le fondu,
et `faire()` — tout le changement de scène, sans exception — ne s'exécute qu'**au noir**.
⚠️ _Ajouté le 13 sept. 2026 :_ cette fiche disait ici que « la prison et l'hôpital le font
depuis M4 ». **C'était faux**, et ça a coûté le correctif d'après : ils étaient sur `Hud.fondu`
et changeaient de scène à 80 % de noir — voir « Le fondu de l'hôpital et de la prison ».

Ce qui a été livré avec l'ordre :

- **Le jeu se fige pendant le fondu.** `maj()` ne fait plus avancer que la transition quand
  il y en a une, exactement comme un menu ouvert (`if (B.menu) return`). Avant, la simulation
  continuait : on pouvait sortir d'une pièce et se faire renverser par un char qu'on n'a pas
  vu venir, pendant un écran noir où l'on ne contrôle rien.
- **Des durées qui se sentent, et asymétriques** : entrer 26 + 20 images (0,77 s — on pousse
  une porte, on veut le sentir), sortir 15 + 11 (0,43 s — on veut retourner au jeu), l'étage
  20 + 16. Les 40 images d'avant, partagées en deux, étaient juste assez pour clignoter et
  pas assez pour lire.
- **La caméra ne saute plus.** `poserDansLaPorte()` la pose **au noir**, sur la cible exacte
  que `majCamera` viserait à la première image (position + avance de l'élan) : personne ne
  voit le saut, et l'amorti n'a rien à rattraper quand le jeu repart. Le juge mesure moins de
  2 px de déplacement à la première image jouable.
- **Le son au bon moment.** `Son.SFX.porte()` est dans `faire()` : la porte s'entend **au
  noir**, à l'image du changement. Le juge le vérifie en espionnant l'appel.
- **On ne repart pas d'un arrêt complet.** La face et la moitié d'un pas de marche restent
  dans le sens de la porte (`ELAN_DE_PORTE`) — ça se sent traversé, pas téléporté.
- ⚠️ **Le cas qui casse tout : passer une porte pendant qu'un autre fondu joue.** Comme la
  scène ne change qu'au noir, `sortir()` appelé avant le noir d'une entrée ne trouverait
  aucun intérieur, refuserait — et le joueur se réveillerait dedans sans l'avoir demandé.
  `finirTransition()` termine donc le fondu en cours (changement compris) avant d'en lancer un
  autre. Entrer puis sortir ramène **au pixel** devant la porte, fondu interrompu ou non.
- ⚠️ **Le noir doit avoir été DESSINÉ avant qu'on éclaircisse.** La boucle rattrape jusqu'à
  quatre images de simulation entre deux images dessinées : sans le drapeau `vu` que le HUD
  pose, la première image de la nouvelle scène pouvait se montrer à 94 % de noir — donc se
  montrer. C'est le seul endroit où le rendu parle à la simulation, et c'est pour ça.
- **Au banc** : `o.entrer(porte)`, `o.sortir()` et `o.fondu()` laissent jouer le fondu — un
  test qui lirait `B.interieur` juste après `Jeu.entrer()` lirait encore la rue. 3 juges
  neufs : la scène et l'alpha mesurés **à chaque image** (aucune ne montre la nouvelle avant
  le noir complet), le gel (ni `B.t`, ni l'heure, ni un passant, ni un char ne bougent), et la
  sortie **pendant** le fondu d'entrée.

## Notes

retour de Martin (« la transition n'est pas juste ») : elle ne l'était pas parce qu'elle
arrivait **dans le mauvais ordre** — `entrer()` chargeait la pièce, _puis_ lançait le fondu,
dont la première moitié noircissait donc sur la scène déjà changée. Ce n'était pas un fondu
enchaîné, c'était un clignotement. `Jeu.transiter()` remet l'ordre : **noircir sur
l'ancienne → changer au noir → éclaircir sur la nouvelle**, le jeu **figé** pendant (un char
ne te renverse plus sur un écran noir), des durées **asymétriques** (entrer 46 images,
sortir 26), la caméra posée au noir sur la cible que l'amorti viserait, la porte qui
s'entend au noir, et un reste d'élan au pas de la porte. 3 juges de banc : la scène mesurée
**à chaque image**, le gel (ni temps, ni passant, ni char), et sortir **pendant** le fondu
d'entrée
