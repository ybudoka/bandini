# Fruits de mer, hommes-sandwichs et des comptoirs garnis

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« ajoute des commerces de fruits de mer et des solliciteurs
hommes-sandwichs », puis « ajoute aussi plus de bouffe et de choses à manger et à boire dans
tous les magasins, où ça fit »). **Les fruits de mer** : une **cabane** de trottoir
(`fruits_de_mer`, guédille au homard, toit de tôles rayées, deux homards sur la glace,
l'enseigne HOMARD au pied) que le générateur ne pose **qu'aux Quais et à La Pointe** —
`AMBULANTS[].districts` enferme un commerce chez lui comme `pietons.districts` enferme un
passant, et un juge vérifie que c'est le port qu'on mange ; huit enseignes de plus (FRUITS
DE MER, HOMARD VIVANT, CRABE DES NEIGES…) dans les deux districts qui touchent l'eau ; la
poissonnerie sert guédille, crevettes de Matane et chaudrée.

- ⚠️ Le toit de la cabane s'arrête à la rangée 3 : le marchand a les pieds 11 px au-dessus
  de l'ancre, ses yeux tombent à la rangée 5 — un toit plus bas les cachait et on se faisait
  servir par un chapeau (le camion-restaurant avait eu la même leçon, avec son guichet
  troué). **L'homme-sandwich** (`pietons.homme_sandwich`, métier `reclame`) : un
  **solliciteur**. `carte.reclames` lui donne un **poste** de trottoir à 5–14 tuiles du
  kiosque pour lequel il crie (le hot-dog, la poutine, la guédille — pas le journal ni le
  café : `AMBULANTS[].reclame` est son boniment, None = personne), tiré dans **son propre
  dé** (`des_reclame`) pour ne pas déplacer un paquet caché à l'autre bout de la ville ; il
  naît à son poste, le jour, hors champ (`naitreLesHommesSandwichs`), il fait les cent pas
  dans un rayon de six tuiles (le `poste` de la Brume, plus large), et quand il te voit à
  six tuiles il **vient vers toi** (`aborde`, à la vitesse d'un piéton, jamais en courant),
  s'arrête à 22 px, te regarde et **crie son boniment** dans une bulle pendant trois
  secondes (`boniment`, voix ElevenLabs « Approchez, approchez, venez voir ! » — genre
  `crieur`, dite par **Léo**, la voix de pub du compte, poussée au style : avec Felix,
  l'homme de tous les jours, Martin les trouvait « pas assez vendeur ») ; ACTION devant lui
  donne un **coupon** : la prochaine bouchée à SON kiosque à moitié prix, **une fois**, et
  il expire au bout de trois minutes (`RECLAME`, sur le joueur comme la caféine — trois
  minutes ne méritent pas une sauvegarde) ; l'invite le dit (« KIOSQUE À HOT-DOGS — 5 $
  (COUPON) ») et la caisse le fait, même calcul (`prixAmbulant`).
- ⚠️ **Un solliciteur n'est pas un mur ni un radar** : il regarde une image sur dix, il
  n'aborde **que celui qui flâne** (au-dessus de la marche, il te laisse : un homme-sandwich
  qui se jetait dans les jambes du joueur au sprint le ralentissait de 10 % — le juge du
  café l'a mesuré, la police rattrapait à cause d'une pancarte), il lâche prise si tu cours,
  si la chaussée ou un mur barre le chemin ou si ça fait quatre secondes qu'il n'arrive pas,
  et une fois son boniment fait il te laisse **vingt secondes de paix** (`repos_images`) —
  sans ça il te suivait d'un bout à l'autre de la rue en répétant la même phrase, et un
  personnage qu'on veut frapper n'est pas de la vie de rue, c'est une plaie.
- ⚠️ **Deuxième archétype à avoir son propre sprite** (`homme_sandwich`, 14 × 16) : une
  pancarte plus large que les épaules, bande rouge et deux lignes d'écriture, un « A » de
  deux planches vu de côté — même leçon que la Brume, un contour se lit là où une couleur ne
  dit rien ; son `c` est la pancarte, pas un chandail. **Les comptoirs garnis** : de quoi
  manger et boire dans **toutes** les familles où ça a du sens — soupe aux pois, pâté
  chinois, pointe de tarte et liqueur au dépanneur ; beigne et liqueur au comptoir de
  service ; liqueur et barre de chocolat à la quincaillerie (le présentoir à côté de la
  caisse) ; ailes de poulet, chips et shooter de rye au bar ; chips, chocolat et liqueur au
  magasin ; sandwich et liqueur à la cantine de la shop ; jus d'orange et chocolat à la
  pharmacie ; poutine, soupe et liqueur au casse-croûte garanti. La **friperie n'en vend
  pas** : ça ne fitte pas, et un comptoir qui vend n'importe quoi ne dit plus où l'on est.
- ⚠️ Toujours la même borne, et un juge fait la division : **au dollar, rien ne bat le
  hot-dog** (6,5 points par dollar) — ce qu'on achète au comptoir, on l'achète parce qu'on
  est devant. 14 juges Python (`test_reclame.py`) + 5 de banc (`test_reclame_js.py` : il
  naît à son poste le jour et pas la nuit, il vient et il parle sans courir puis se tait, le
  coupon rabat le prix une fois et expire, la cabane sert une guédille, les comptoirs et le
  casse-croûte ont de quoi manger)
