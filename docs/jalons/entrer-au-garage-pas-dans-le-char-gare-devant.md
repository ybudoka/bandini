# Entrer au garage, pas dans le char garé devant

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

bug de Martin (« quand on veut entrer au garage et qu'un véhicule est devant, quand on
choisit "entrer" on entre dans le véhicule au lieu du bâtiment »).

- ⚠️ Une seule pression d'ACTION est lue **deux fois dans la même image** : `Combat.maj`
  ouvre le menu ACHETER / ENTRER de la propriété (ou lance le fondu de la porte), puis
  `Vehicules.maj` relit la même pression et fait monter dans le char garé devant. Au moment
  de choisir ENTRER, `Jeu.entrer` refuse : on est déjà au volant. **La porte gagne sur la
  portière** : un char ne se prend plus dans l'image où un menu vient de s'ouvrir ou un
  fondu vient de partir — un menu et un fondu figent déjà tout le jeu (`Jeu.maj`), à plus
  forte raison la portière d'à côté. Deux juges de banc : une seule pression devant le
  garage ouvre le menu **sans** prendre le char, puis ENTRER mène dedans ; et à une porte à
  soi (sans menu), le fondu part et le char reste là. 1033 tests
