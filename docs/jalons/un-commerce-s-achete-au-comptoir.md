# Un commerce s'achète au comptoir

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « pour acheter un commerce c'est à l'intérieur ». La porte du kiosque, du
Brouillard et du garage ouvrait un menu ACHETER / ENTRER **sur le trottoir**
(`Missions.acheterPropriete`), et l'invite de la rue disait « ACHETER KIOSQUE DE MADAME
THIBODEAU ». **La porte n'est plus qu'une porte** (ENTRER, un fondu, rien à choisir) et la
fonction est partie. **L'achat se fait dedans** : la caisse du kiosque et du Brouillard dit
« ACHETER <LE NOM> » et son menu offre ACHETER LE COMMERCE, avec ce que ça rapporte par
jour ; une fois payé, la même caisse dit « LA CAISSE » et se vide dans nos poches.

- ⚠️ **La ligne vit là où PRENDRE LA CAISSE vivra** — dans les menus bâtis sur `items`
  (`menuDuPoint` enveloppe maintenant `menuDuComptoir`), pas dans ceux qui ont les leurs :
  l'avocat à sa table du Brouillard ne vend pas le bar. C'est ce qui sert le **garage**, qui
  n'a pas de point `caisse` : l'achat passe dans le menu du comptoir.
- ⚠️ **Et EN DERNIER** : `ouvrirMenu` pose le curseur sur la première ligne qui se choisit,
  et au garage, les deux pressions d'ACTION qui vendent un char auraient payé le garage 4500
  $. L'Hôtel Bandini (phase 2) dit toujours « CE N'EST PAS À TOI ». 3 juges par le bouton
  (`test_moteur_js.py`), qui remplacent les deux de la porte : le kiosque de la rue au
  comptoir puis à la caisse pleine ; au garage, deux pressions vendent le char et n'achètent
  rien ; la porte du garage gagne sur le char garé devant, **à vendre comme à soi**.
  Rouge-avant : 3 sur 4 sur l'ancien code (le cas « à soi » est un garde-fou, vert avant) ;
  l'achat remis **en tête** du menu fait rougir le juge du garage. 2461 tests.
