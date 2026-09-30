# La patinoire du parc — deuxième vague

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Tranché par Martin le 30 sept. 2026, après la livraison : les chars dérapent sur la glace —
une porte de service au sud des bandes (celle de la surfaceuse) s'ouvre aux chars, et un
char sur la glace glisse (l'adhérence du dérapage des saisons, lot 6a) ; les trois mots du
guichet de Madame Thibodeau dits par sa voix (Julia) ; la rumeur de la glace à 64 kbit/s (le
plafond des sons de lieu relevé d'autant, décision de Martin) ; et le plafond du paquet du
premier écran relevé à 242 000 bruts (décision de Martin : les foyers de l'hiver et la
patinoire l'avaient dépassé).

## Notes

### ✅ Livré (30 sept. 2026)

- **Les chars sur la glace** : une porte de service (la surfaceuse) de deux tuiles au milieu du côté des bandes qui
  donne sur le trottoir (`patinoire._service`, marquée `service`). L'hiver, un char n'entre sur la glace que par
  elle, et n'en ressort que par elle (`Patinoire.bloqueChar`) ; dessus, il glisse : `Patinoire.adherence` et
  `Patinoire.frein`, lus par `Vehicules` à côté de la neige et du verglas (0,15 et 0,2) — le dérapage des saisons
  (lot 6a) fait le reste : il sous-vire, il freine long. Les pneus d'hiver en rendent une part, comme ailleurs.
- **La voix de Madame Thibodeau au guichet** : ses quatre répliques (`patinoire.REPLIQUES`, trois mots et le
  « t'as pas ça sur toi? ») dites par sa voix, Julia, séchée à l'isolateur ; le jeu collé à la réplique
  (`interpretation.JEU`). La série voyage dans la fiche (la suite du paquet), chargée en approchant de la glace.
  Le texte du HUD vient des mêmes répliques : ce qu'on lit est ce qu'on entend.
- **La rumeur de la glace à 64 kbit/s** (48 Ko) : le plafond des sons de lieu avait déjà été porté à 3 Mo par une
  autre session le même jour — rien à relever.
- **Le paquet du premier écran relevé à 242 000 bruts** (Martin) : les foyers de l'hiver l'avaient mené à 241 290,
  la patinoire à 241 568.
