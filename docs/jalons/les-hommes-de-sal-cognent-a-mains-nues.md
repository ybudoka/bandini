# Les hommes de Sal cognent à mains nues

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « les hommes de Sal sont à main nue ou poing américain (un peu plus
fort) ».

- ⚠️ **Mesuré avant : ils arrivaient la batte à la main.** Ils naissent dans le corps d'un
  **Cravate** (`Entites.archetype('cravate')`), et la fiche du Cravate porte un **bâton** :
  chaque coup enlevait **18** points au joueur, et chacun laissait **sa batte** par terre
  quand on le couchait. **Un poing américain** entre au catalogue, juste après les poings :
  **12** de dégâts, entre les poings (8) et le bâton (18), même portée et même cadence que
  le poing ; il ne se vend nulle part, on le ramasse sur celui qu'on a couché. Les hommes de
  Sal sortent **tour à tour** à mains nues et au poing américain
  (`economie.DETTE["armes"]`) : à deux, on voit toujours les deux mains.
- ⚠️ **Et il ASSOMME, comme les poings.** La règle vivait en dur dans `combat.js`
  (`arme.slug === 'poings'`) ; elle est maintenant un champ de l'arme (`assomme`). Sans ça,
  ramasser le poing américain d'un homme de Sal changeait un KO en meurtre — deux étoiles de
  différence pour un coup de poing plus lourd. Son dessin (quatre anneaux : ce sont les
  trous qui le nomment à seize pixels, sans eux c'est la barre grise du `defaut`) et son
  bruitage (ElevenLabs, deux variantes, avec son filet synthétisé) — **écouté par Martin le
  17 sept. 2026 : bons**. 4 juges neufs ou étendus, **rouges sans leur règle** (9
  mutations) : les hommes de Sal frappent le joueur pour 8 et pour 12, jamais pour 18, et
  couchés ne laissent que le poing américain ; le poing américain est entre les poings et le
  bâton, et seuls eux deux assomment ; un ouvrier frappé au poing américain tombe assommé,
  pas mort ; chaque arme qu'on tient a son dessin. La roue est jugée jusqu'au catalogue
  entier (quatorze armes).
