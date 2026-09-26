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

_Rien de livré._
