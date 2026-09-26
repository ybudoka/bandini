# La tempête de verglas

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui génial »)._

_Ce que ça donne :_ un événement rare et mémorable — la glace fait tomber les fils, des quartiers entiers
passent au noir, et la ville change de règles pour trois jours.

- **Quand** : une fois par partie, trois jours de suite, calculés (pas un dé qui pourrait ne jamais tomber).
- **La glace** : l'adhérence tombe partout (le mécanisme de la neige de M12), les arbres et les fils cassent.
- **Le noir** : des quartiers sans électricité — les lampadaires, les enseignes et les fenêtres s'éteignent
  (les lampes existent, avec leur direction) ; seuls les phares éclairent.
- **Le boulot** : livrer des génératrices et du bois de chauffage (`boulots`).
- **La police débordée** : elle voit moins loin et vient moins vite — le meilleur soir pour un coup (une
  mission M16 peut s'y accrocher).

⚠️ **Ce qui guette** : éteindre des quartiers touche au rendu de nuit et à l'éclairage déjà juge par
plusieurs juges ; l'événement doit laisser la ville exactement comme avant quand il finit.

**Juges** : les trois jours viennent pour tout le monde au même moment ; un quartier noir n'a plus de lampe
allumée ; tout se rallume après ; la police voit moins loin pendant.

### Le plan (26 sept. 2026)

La recette de la neige et du brouillard : **Python règle, le navigateur givre** (`app/verglas.py`,
`static/js/verglas.js`) — une pure fonction du jour et de l'heure, aucun dé, aucun état ; **derrière une
option** (« VERGLAS (ESSAI) », non par défaut) : sans elle, tout vaut 1 et rien ne se peint, le jeu
d'avant octet pour octet.

1. **Le calendrier** : trois jours de suite, au jour 9, puis tous les 40 jours (une fois pour une partie
   ordinaire ; une longue partie la revoit). La pluie verglaçante arrive dans la nuit du premier jour, la
   glace fond le soir du troisième.
2. **La glace** : l'adhérence et le freinage tombent (les points d'accroche de la neige), le trafic lève
   le pied ; un reflet bleuté sur la ville, des éclats qui scintillent sur la chaussée, et des branches
   cassées sur les trottoirs (peintes à l'empreinte de la tuile, sans entité).
3. **Le noir** : chaque jour, quelques quartiers sans courant (à l'empreinte de la tempête et du jour) —
   leurs lampes s'éteignent (lampadaires, fenêtres, enseignes : `carte.lampes`), et la nuit y est plus
   noire ; seuls les phares éclairent.
4. **La police débordée** : elle voit moins loin (`vision`), et ses renforts et ses dépêches tardent.
5. **Le boulot** : dans un camion, pendant la tempête seulement, le klaxon prend une livraison de
   génératrices vers les quartiers au noir (trois arrêts).
6. **Le Clairon** : la veille, l'annonce ; chaque matin de tempête, les quartiers au noir.
7. **Après** : tout se rallume de soi-même (une fonction du jour), un juge le tient.

## Notes

_Livré le 26 sept. 2026._ ⚠️ **Derrière l'option « VERGLAS (ESSAI) »** (PAUSE › OPTIONS), éteinte par
défaut comme la neige et le brouillard : pour la voir, l'allumer et aller au jour 9 (ou 49, 89…).

- **Le calendrier** (`app/verglas.py`, `static/js/verglas.js`) : trois jours au jour 9, puis tous les 40
  jours — les mêmes pour tout le monde (une pure fonction du jour, `intensiteA`). La pluie verglaçante
  prend dans la nuit du premier jour (pleine à 3 h), la glace fond le soir du troisième (de 18 h à minuit).
- **La glace** : l'adhérence (×0,4) et le freinage (×0,55) tombent, aux mêmes points d'accroche que la
  neige (`Vehicules`), et le trafic et les autobus lèvent le pied (×0,7). À l'écran : la chaussée vernie
  de bleu, par bandes (le premier essai, un voile sur toute la ville, ne se voyait pas sur le gris), des
  éclats qui scintillent, et des branches cassées gainées de glace sur les trottoirs — tout à
  l'empreinte de la tuile, sans entité ni dé.
- **Le noir** : chaque jour de tempête, deux, trois puis deux quartiers perdent le courant, à
  l'empreinte de la tempête et du jour (`quartiersNoirsA`, parmi le Faubourg, les Érables, les Quais,
  le Shop, La Pointe et l'île). Leurs lampes s'éteignent — lampadaires, fenêtres, enseignes, tout ce qui
  est dans `carte.lampes` (`Monde.lampesVisibles` lit `Verglas.lampeAuNoir` ; le district se calcule une
  fois par lampe) — et la nuit y est plus noire quand la caméra y est (`Verglas.ambiance`). Seuls les
  phares éclairent. Rien à rallumer : la tempête finie, la fonction rend « rien », et le juge le vérifie.
- **La police débordée** : sa vue ×0,6 (les trois portées de `police.js`, à côté du brouillard), et ses
  renforts et les dépêches des témoins tardent ×1,6.
- **Les génératrices** (`BOULOTS.generatrices`) : dans un camion, pendant la tempête seulement, le klaxon
  prend trois livraisons vers un lieu d'un quartier au noir. Hors tempête, le klaxon d'un camion reste un
  klaxon (sans message : on ne le répète pas à chaque coup). Paliers courts (5, 12, 25 : trois jours tous
  les quarante) : +10 % de vie, l'hôpital à moitié prix, le camion à la planque.
- **Le Clairon** : la veille, « PLUIE VERGLAÇANTE DEMAIN : HYDRO-BAIE PRÉVOIT TROIS JOURS DIFFICILES. » ;
  chaque matin de tempête, « VERGLAS : PAS DE COURANT DANS … » avec les quartiers.
- **Juges** : `test_verglas.py` (les nombres, les quartiers existent, le paquet, l'économie) et
  `test_verglas_js.py` (les mêmes jours pour deux graines, éteint il n'existe pas, un quartier au noir
  sans une lampe et rallumé après, la nuit plus noire là seulement, le char qui glisse plus, la police
  qui ne voit plus à 70 % de sa portée et dont les renforts tardent, les génératrices seulement pendant,
  le Clairon, le dessin sans dé). Chaque juge a été vu rougir sous sa mutation.
- **Pas fait, à dire** : les **fils** (la ville n'a pas de poteaux électriques à faire tomber) ; les
  **arbres** restent debout (les branches cassées sont peintes au sol) ; les **feux de circulation** d'un
  quartier au noir restent allumés ; la ligne du Clairon n'est pas dite par le narrateur (du texte,
  comme le décompte des nids) ; et le **rythme sur le vrai téléphone** reste à mesurer avant d'allumer
  l'option pour tout le monde (la dette du plan). Une mission M16 peut s'accrocher au « meilleur soir
  pour un coup ».
