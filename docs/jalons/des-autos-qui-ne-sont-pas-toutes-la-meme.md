# Des autos qui ne sont pas toutes la même

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « je veux aussi avoir parfois des différences structurelles, pas juste
la couleur ». Toutes les autos de la ville étaient la même berline repeinte ; le taxi et la
police, eux, sont une flotte et le restent. **Livré** : quatre silhouettes pour l'`auto` du
catalogue — la **berline**, la **compacte** (le toit file jusqu'au hayon), la **familiale**
(le toit va au bout, une vitre de custode et des barres de toit) et la **camionnette**
(cabine courte, benne ouverte dont on voit le fond) —, une sur deux reste une berline
(`SPRITES.auto.variantes`, pondérées).

- ⚠️ **Ce qui fait une silhouette, c'est l'habitacle** : la berline est découpée en `CAISSE`
  commune (roues, caisse pincée, ceinture, portières, pare-chocs, phares) et
  `habitacle(...)`, une recette à quatre nombres d'où se placent seuls les montants, le
  cadre des vitres et le reflet — la berline recoupée est identique **au pixel** à celle
  d'avant sur les 32 caps. Même empreinte, mêmes roues : c'est encore une `auto`, et elle se
  conduit pareil.
- ⚠️ **La silhouette ne tire pas de dé** (`Vehicules.silhouetteDe` la lit sur la position de
  naissance, comme la tête du pilote) ; ⚠️ **elle revient telle quelle** du lot et de la
  planque (`sprite` dans la fourrière et dans `planque.vehicule`), et un taxi ne revient pas
  en camionnette.
- ⚠️ **Vu en chemin, et corrigé** : le lot, la planque, la peinture et l'escorte d'une
  mission rendaient au char sa couleur seule (`{ c: couleur }`), sans rehaut ni ombre —
  invisible tant que le char roulait sur son toit ; depuis que la berline montre son toit et
  le cadre de ses vitres, une auto bleue en revenait avec les tons rouges de la palette.
  `nuances(couleur)` partout. 3 juges neufs, **rouge avant sur chaque règle** (sans
  variantes : « les autos ne varient pas : {'auto': 240} » ; au dé : « naître auto a tiré
  des dés » ; lot sans silhouette : « la camionnette revient du lot en auto » ; lot sans
  nuances : « l'auto bleue revient du lot sans ses tons »). 2233 tests
