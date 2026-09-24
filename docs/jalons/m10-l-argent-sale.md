# M10 L'argent sale

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : M10 — L'argent sale (**ajout**, taille 3)_

_Ce que ça donne :_ une raison de se lever le matin — la dette de Rocco.

- **Le shylock** : 15 000 $, un intérêt par jour, des rappels au téléphone, puis des hommes
  de main qui te trouvent où que tu sois. Rembourser ouvre une des deux fins (M13).
- **Guichets** : les défoncer au camion (bruyant, 2★, la caisse par terre) ou poser un
  **skimmer** et revenir le lendemain (silencieux, lent, il peut être trouvé).
- **Assurance et fraude** : assurer un char au garage, le faire disparaître, encaisser —
  trois fois de suite et l'assureur enquête.
- **La run** (ajouté le 15 sept. 2026, de la tournée du net) : le commerce d'un district à
  l'autre — acheter bas, vendre haut. C'est le cœur de Chinatown Wars, et ici il ne demande
  ni marchandise neuve ni personnage neuf : **la contrebande de Sven** (caisses de cigarettes
  et de boisson) s'achète au quai et se revend au dépanneur, à la taverne, au bar, à la
  cantine. Un prix par district qui **bouge chaque jour** (la graine du jour, comme les
  entraves), affiché au comptoir ; le stock se transporte dans le coffre, donc un char qui
  brûle brûle la run avec.
  - ⚠️ **Ce qui empêche la machine à argent** : la police **fouille**. Se faire arrêter avec
    des caisses, c'est les perdre en entier (et c'est pour ça que l'île — pas de police — vaut
    le détour). Le prix d'achat monte avec ce qu'on a déjà acheté dans la journée, et la
    marge d'une run complète reste **sous celle d'une mission de l'arc où on se trouve** :
    un commerce qui paie mieux que l'histoire vide l'histoire.
  - ⚠️ **Et un garde-fou de ton, tranché ici** : de la boisson et du tabac de contrebande,
    pas de la drogue. Le jeu se moque de la ville, il ne vend pas ça.
- `economie.py` : dette, intérêts **bornés**, primes, seuils de suspicion.
- **Juges** : la dette ne dépasse jamais son plafond ; un joueur qui ne fait rien ne devient
  pas insolvable en une nuit ; la fraude rapporte **moins à l'heure** que le travail honnête
  — sinon le jeu se joue tout seul et le taxi ne sert plus à rien.

## Notes

**1re vague : la dette de Rocco**, celle qui donne une raison de se lever le matin.

- ⚠️ **Aucun lieu neuf, et c'est un choix de design, pas une économie** : un shylock ne
  tient pas un comptoir où l'on vient payer, il **envoie du monde**. Les rappels arrivent,
  puis les hommes de main te trouvent où que tu sois — et c'est À EUX qu'on paie. La
  collecte devient une scène au lieu d'un menu.

✅ **2e vague livrée** (15 sept. 2026) : **les guichets** — une caisse de banque posée dans
la rue, encastrée **sous une vitrine**, sur l'abord, servie depuis la dalle (12 dans la
ville, espacés, tirés dans leur propre dé) ; `lourd: 2.5` sur la fiche du décor — un
quatrième mot dans `verifier_ce_qui_casse.py`, toujours avec `casse` — fait qu'il **ne cède
qu'au camion ou à l'autobus**, une berline s'y arrête ; il cède aussi à huit balles de
pistolet ou à l'explosion d'à côté. Quand il cède, **la caisse tombe en six liasses**
(300–900 $) qu'on ramasse en passant, à pied ; c'est un **délit à deux étoiles** quoi que ce
soit qui l'ait ouvert, et il se répare au lever du jour comme le reste. **Le skimmer**
s'achète chez Josée (350 $ — pas une arme : `MARCHE_NOIR.objets`), se pose sur un guichet
par ACTION, **lit pendant la nuit** (350–900 $) ou se fait trouver (trois fois sur dix), et
se vide au même guichet le lendemain ; trois posés à la fois au plus, et l'invite du HUD dit
exactement ce qu'ACTION va faire (poser, attendre, vider). Il se pose aussi sur une machine
distributrice de la rue — dans son menu, **en plus des articles** et jamais à leur place :
on peut poser un skimmer et acheter une canette dans la même visite, l'un n'empêche pas
l'autre ; la machine d'une salle d'attente, elle, ne se skime pas, et une machine défoncée
emporte le skimmer avec sa caisse. **L'assurance** au garage :
Ti-Guy couvre ce qui est garé devant, sans demander à qui c'est — la moitié du prix neuf,
**jamais plus de 900 $**, prime de 30 % ; le char qui brûle, plie ou coule ouvre une
réclamation qu'on **encaisse au garage** ; à la troisième, **l'assureur enquête** : quatre
jours sans police, une page au casier, puis le dossier se classe.

- ⚠️ **La règle de tout M10, jugée char par char** : la caisse d'un guichet vaut moins
  qu'une journée honnête, trois skimmers moins qu'une journée de taxi, et la fraude — sur
  les 300 s qu'elle prend au moins — moins que le taxi **à l'heure** ; frauder avec un char
  qu'on a payé perd de l'argent, ce n'est payant qu'avec un char volé. 7 juges Python + 4 de
  banc ; 1558 tests.

✅ **3e vague livrée** (15 sept. 2026) : **la run de Sven** — la cale du Norvégien, un
comptoir de contrebande sur les planches des Quais (un ambulant `sur: "quai"`, sans tarif ni
coupon : ses prix vivent dans `economie.CONTREBANDE`). Cigarettes et boisson — ⚠️ pas de
drogue, tranché — s'achètent **dans le coffre du char garé à côté** (90 px ; sans char, la
cale ne vend rien : elle ne se porte pas), huit caisses au plus, et **le prix monte de 10 %
par caisse déjà prise dans la journée**. Elles se revendent au comptoir de quatre commerces
(dépanneur, bar, cantine, casse-croûte — la ville n'a pas de taverne) au **prix du jour du
district**, tiré du jour et du district par `hash2` (pas un dé), affiché au comptoir même
sans cargaison, entre 0,7 et 1,3 fois le prix de vente : le mauvais district fait **perdre**
de l'argent, et c'est jugé. Un char qui brûle ou coule emporte la run ; **la police
fouille** : arrêté, le char saisi part au lot sans ses caisses.

- ⚠️ Jugé : la meilleure run possible (coffre plein, vendu au meilleur prix qui existe) vaut
  moins que la plus grosse mission de l'arc et moins que le taxi **à l'heure** sur les 240 s
  qu'elle prend au moins. 6 juges Python + 3 de banc ; ⚠️ un juge de défi tombé pour une
  raison à lui — il lisait le **dernier** message du HUD après deux minutes ; le vendeur de
  la cale a décalé les dés, un facteur en colère a fait le reste — lit maintenant le verdict
  à l'instant où il tombe. 1567 tests. **M10 est livré en entier** : la dette, les guichets,
  le skimmer, l'assurance, la run
