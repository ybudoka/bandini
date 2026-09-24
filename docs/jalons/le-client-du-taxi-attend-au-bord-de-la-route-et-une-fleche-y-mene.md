# Le client du taxi attend au bord de la route, et une flèche y mène

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

Demande de Martin (17 sept. 2026) : « pour la mission du taxi et tout ce qui est taxi, il
faut que les clients attendent sur le bord de la route. et je veux les flèches pour savoir
où trouver le client. » Mesuré avant : le client naît par `Entites.placeDeNaissance()` — un
pas de porte une fois sur trois, sinon n'importe quelle tuile marchable hors route (un parc,
une arrière-cour), à 40 px près d'une chaussée ou à dix tuiles. Et la flèche au bord de
l'écran comme celle de la mini-carte ne suivent que `Histoire.cible()` : le boulot n'a qu'un
point qui clignote sur la mini-carte, et seulement s'il tombe dans son cadre.

**Livré.** Le client naît sur un **trottoir collé à une voie** où roule un char, et que CE
char rejoint (`Entites.placeAuBordDeLaRoute`, la route de `atteignableEnChar`) : tiré parmi
toutes les places de la couronne de naissance, hors de l'écran, sans bloquer une porte ni
tomber sur un meuble ; deux fois plus loin si la couronne n'en a pas. Il regarde la rue et
hèle. Le blessé de l'ambulance aussi, par la même machine. Un taxi sur l'île ne trouve
personne et le dit (« PERSONNE N'ATTEND DANS LE COIN ») au lieu de poser un client de
l'autre côté de l'eau. Le client ne s'oublie plus quand on s'éloigne (`peupler`) : prendre
le mauvais coin de rue faisait tomber la course. Les flèches : au bord de l'écran, la flèche
et ses mètres vont au **boulot** quand il y en a un (bleu vers le client, or vers la course)
— l'objectif de l'histoire reste sur la mini-carte ; au bord de la mini-carte, une flèche
quand le client ou la course sort du cadre ; sur la carte plein écran, un pointeur qui
oscille au-dessus (`Hud.cibleDuBoulot`, lu par `Hud.marqueurs()`). Regardé dans Chromium.

Juges (`test_client_au_bord_de_la_route_js.py`), chacun vu rouge sans sa règle : le client
attend sur le trottoir d'une rue que le char rejoint (seize départs, taxi et ambulance) ; il
naît hors de l'écran et regarde la rue ; il attend quand on prend le mauvais coin de rue ;
sur l'île, personne n'attend (sans la règle de la route, il naissait à 766 px, sur le
continent) ; une flèche mène au client puis à la course (mutations : la flèche de l'écran
rendue à l'histoire, la flèche de la mini-carte retirée).

- ⚠️ Au bord de l'écran, UNE flèche : deux de deux couleurs, chacune avec ses mètres, se
  marcheraient dessus au même bord. Un boulot pris pendant une mission cache donc la flèche
  de la mission à l'écran, pas sur la mini-carte.
- ⚠️ Sur la carte plein écran, pas de carré : les lieux sont des carrés, et ceux de « TES
  PLACES » sont dorés comme la course — la capture l'a montré, pas un juge.
