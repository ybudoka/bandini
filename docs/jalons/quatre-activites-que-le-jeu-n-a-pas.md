# Quatre activités que le jeu n'a pas

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Ce que le net apprend : quatre activités que le jeu n'a pas (**ajout**, taille 2)_

_Demande de Martin (15 sept. 2026) :_ « regarde sur le net pour des idées de missions ».

En comparant Bandini aux classiques vus d'en haut (GTA 1 et 2, Chinatown Wars) et aux
inventaires de « tout ce qu'il y a à faire » des GTA 3D, **la ville a déjà presque tout** : les
paquets cachés (20), les défis de saut (3, cinq de plus dans M16), quatre boulots au klaxon,
les propriétés, le marché noir. Quatre choses manquent, et chacune se paie en données, pas en
moteur.

1. **Les boulots montent en grade** — **livré le 15 sept. 2026**, quelques heures après
   l'écriture de cette fiche (`aee8543`). Trois paliers par boulot (10, 25, 50) et une
   récompense qui **change la partie**, presque jamais de l'argent : +10 % puis +25 % de vie
   pour l'ambulance, le rachat au lot à moitié puis gratuit pour le remorquage, l'hôpital à
   moitié prix pour la pizza, et à 50 le **char à la planque** dans les quatre cas. ⚠️ Quand
   deux paliers portent le même type, c'est le **plus fort** qui compte, pas la somme.
2. **Deux boulots de plus**, et aucun ne demande un véhicule neuf (⚠️ la refonte des
   véhicules passe avant tout char de plus) :
   - **La patrouille** — dans une auto-patrouille **volée**, un point rouge sur la mini-carte :
     un fuyard à rattraper avant la fin du chrono. C'est la _vigilante_ des GTA, et Bandini lui
     donne ce qu'elle n'a nulle part ailleurs : tu fais la police **avec un casier**, dans un
     char qui n'est pas à toi. Récompense de palier : `casier −1` tous les cinq (M11).
   - **Pompier volontaire** — au Québec, les pompiers d'un village sont des volontaires qu'on
     appelle chez eux. Un feu quelque part, un extincteur, un chrono (`eteindre` arrive avec
     M16). Pas de camion à dessiner : ce qui compte, c'est d'arriver.
3. **La liste du quai** (le _wheeler-dealing_ de GTA 2, le quai d'exportation de GTA III) :
   Sven — ou Ti-Loup si on l'a brûlé — affiche **quatre modèles** sur une ardoise au quai. Les
   livrer, sans bosse, un par jour. La liste se renouvelle. ⚠️ C'est l'activité qui donne enfin
   une raison de **regarder** le parc automobile : aujourd'hui un coupé sport et une berline
   valent pareil dès qu'ils roulent.
4. **Les frénésies** (les _rampages_). Une icône cachée, une arme, un chrono, un compte à
   faire. C'est le classique du genre, et c'est trois lignes de données : `tuer` + `chrono_s`
   + une arme imposée. ⚠️ Deux garde-fous, et ils ne sont pas négociables : **les enfants
   restent intouchables** (ils le sont déjà, dans le code, pour tout le monde), et une frénésie
   se déclenche **exprès** — jamais un objectif qu'on reçoit au téléphone. C'est la seule
   activité du jeu qui ne prétend pas être autre chose que du chaos, et c'est à Martin de dire
   si la ville en veut.

**Juges** : un palier de boulot ne se donne qu'une fois et sa récompense existe (un char à la
planque est vraiment garé) ; aucun palier ne paie mieux à l'heure qu'une mission ; la
patrouille ne compte que les vrais fuyards ; la liste du quai ne demande que des modèles qui
existent au catalogue et qu'on peut trouver dans la ville ; une frénésie ne touche jamais un
intouchable.

## Notes

sorti de la tournée du net : des **paliers** de boulot avec récompense permanente (**livrés
le 15 sept.**, `aee8543` : +25 % de vie à 25 ambulances, le char à la planque à 50), deux
boulots de plus sans un seul véhicule neuf (**la patrouille** — la _vigilante_, mais avec un
casier et un char volé — et **pompier volontaire**), **la liste du quai** (quatre modèles
demandés, sans bosse) et **les frénésies**, à trancher par Martin ; ⚠️ les enfants restent
intouchables

**Pompier volontaire — livré le 18 sept. 2026** (2e des 4 activités) : pas de caserne ni de
camion à dessiner — un feu se déclare sur une façade (`app/incendies.py`, la règle et les
candidats ; `static/js/incendies.js`, qui brûle), à l'empreinte de l'heure comme le bris
d'aqueduc (jamais au dé du jeu) ; on arrive à pied ou en char, on l'éteint à l'extincteur (le
jet attire la flamme, `combat.js` → `Incendies.majJet`), et la prime tombe — une fois, bornée
sous ce que rapporte le boulot le plus riche. ⚠️ Jamais une cour de gang ni un lieu garanti ;
un feu est CONTINU, pas un changement discret — sa fumée se voit de loin, et c'est par elle
qu'on le trouve. ⚠️ Rien ne se sauvegarde : un feu éteint se re-déclare au rechargement, le
prix de garder la ville déterministe. Juges : `tests/test_incendies.py` (la règle, la borne
d'équilibre, les candidats) et `tests/test_incendies_js.py` (il se déclare à l'heure, il
s'éteint au jet, il ne se re-déclare pas).

**La patrouille — livrée le 26 sept. 2026** (3e des 4 activités) : dans une auto-patrouille (volée,
forcément), **allumer la sirène** prend le contrat (`boulot: "patrouille"` sur la fiche du char, le même
bouton que l'ambulance). Un suspect — un adulte, jamais un enfant : il serait intouchable — détale d'un
trottoir à 140 px au moins, le GPS le pointe ; on le **rattrape** avant soixante secondes : **à terre et
vivant**, c'est une arrestation (50 $ et ce que le chrono laisse des 40 de prime). Percuté par
l'auto-patrouille, il reste au sol (plaqué, pas renversé : ce n'est PAS un délit) ; mort, ça ne compte
pas ; trop tard ou trop loin, il s'évapore. Les paliers (un type neuf, `casier`) : le poste te rend ton
dossier — une page de moins à 5 arrestations, une à 15, deux à 30. Juges : `tests/test_patrouille_js.py`
(la sirène et la fuite, l'arrestation sans délit — assommé, et renversé au volant sur une rue dégagée —,
mort ou trop tard, le casier au palier) ; quatre mutations les font rougir. ⚠️ Vu en l'écrivant : le juge
au volant ne renversait personne — le quartier avait tiré un **enfant** comme suspect.

**La liste du quai — livrée le 26 sept. 2026** : Sven affiche **quatre modèles** (`economie.LISTE_DU_QUAI`,
tirés à l'empreinte de la période parmi ce que la ville fait rouler : auto, taxi, moto, camion, et les
rares — sport, luxe, cabriolet) ; la liste se renouvelle tous les quatre jours, la même pour tout le monde.
Près de sa jetée, la ligne du bas la dit (« LA LISTE DE SVEN : … (LIVRÉ) ») ; au volant d'un modèle
demandé, à l'arrêt au bout de la jetée, il le prend — 40 % du prix neuf (mieux que le garage), **un par
jour**, et **sans bosse** (90 % de sa vie, sinon « TROP DE BOSSES »). Juges : `tests/test_liste_du_quai_js.py`
(hors liste rien, cabossé refusé, propre payé et parti, pas deux le même jour, oui le lendemain, la liste
qui change ; la même pour deux graines) ; trois mutations les font rougir. Restent **les frénésies**, à
trancher par Martin.

**1er oct. 2026 : l'ardoise suit le choix** (M16, les deux restes — la fiche : « Sven, ou Ti-Loup si on l'a
brûlé »). Qui a fait sauter les camions de Sven pour Josée (`q11`) ne livre plus à sa jetée : l'ardoise reste vide
jusqu'à ce que Ti-Loup la reprenne (`q15`, _La liste de Ti-Loup_, la variante de `q14`) — les mêmes modèles, la même
règle, livrés à son lot de la fourrière (« LA LISTE DE TI-LOUP », « TI-LOUP — … »). La règle est à Python
(`economie.LISTE_DU_QUAI["brule"]`), `Missions.donneurDuQuai` la lit. Juge :
`tests/test_liste_de_ti_loup_js.py` (Sven, personne, puis Ti-Loup — et Sven plus jamais après q11).

**1er oct. 2026 : la liste s'ouvre après `q14`** (Martin : « comme le disait la fiche » — _La liste du Norvégien_
la donne en récompense). Livrée le 26 sept., elle était ouverte dès le début de la partie ; maintenant Sven n'a pas
d'ardoise pour toi avant `q14` (`economie.LISTE_DU_QUAI["ouvre"]`) : il ne prend rien, la ligne du bas se tait, et
`q14` finit sur « SVEN T'OUVRE L'ARDOISE DU QUAI ». Le côté de Josée ne change pas (`q11`, puis Ti-Loup après `q15`).
Juges : `test_la_liste_s_ouvre_apres_q14` (`tests/test_liste_du_quai_js.py`, le reste du banc joue avec `q14`
faite) et le cas « Sven sans `q14` » de `tests/test_liste_de_ti_loup_js.py`.

**Les frénésies — livrées le 28 sept. 2026** (4e et dernière des 4 activités ; Martin : « la frénésie on
y va ») : huit crânes rouges, **un par district de terre**, cachés dans une ruelle (`app/frenesies.py` : la
friche aux Friches et l'herbe à la Gare de triage, qui n'en ont pas) — la plus proche de la cour de la gang
visée sans y être, ou du centre ; hors des chantiers, à huit tuiles d'un paquet, rejointe à pied depuis la
rue. Une RÈGLE, pas un dé, posée après la bande nord : la ville d'avant est la même à l'octet. On marche
dessus **exprès**, à pied, hors mission et hors défi (`static/js/frenesies.js`) : l'arme du catalogue est
**prêtée** (tenue, sans fin de munitions, rendue à la fin), le chrono et le compte s'écrivent en rouge en
haut (« FRÉNÉSIE 3/10 CRAVATES 1:12 »), et la gang visée **rapplique** hors de l'écran (quatre autour du
joueur au moins : sinon le compte dépend d'une cour peuplée par hasard). Réussie : un son, la prime une fois
(150 à 250 $, jamais plus que la mission médiane ; 500 $ de plus pour les huit), le carnet, et
`partie.frenesies` — sauvegardé, lu au BILAN (« FRÉNÉSIES 3 / 8 ») ; l'icône ne revient plus. Ratée (le
temps, l'hôpital, la prison, une porte), elle attend qu'on s'éloigne et qu'on revienne.

Les huit : les Cravates au pistolet (Faubourg, 10 en 2:00) et à la carabine (Petit-Canton), les Chevreuils à
la batte (Érables, 8 en 1:30) et à la mitraillette (Friches, 15), les Morues au fusil (Quais), les Skateux au
couteau (La Pointe), les Boulonneux au Molotov (Gare de triage), et **quatre chars** au Molotov à la Shop —
une balle ne mord pas la tôle d'un char vide, seul le feu le fait.

- ⚠️ **Les enfants restent intouchables**, deux fois : `Entites.blesser` les refuse à tout le monde, et
  `Frenesies.compte` ne compte jamais un intouchable (juge synthétique : un enfant « de la gang » ne compte pas).
- ⚠️ **L'arme prêtée ne se garde pas** : la sauvegarde écrite pendant une frénésie écrit le sac d'avant
  (`sansLePret`) — sans ça, un rechargement rendait un pistolet à 999 balles.
- ⚠️ **Rien au démarrage** : le crâne se peint, ce n'est pas un décor (un décor de plus au chargement décale
  le numéro de tout ce qui naît ensuite). Les renforts naissent pendant la frénésie seulement.
- ⚠️ **Pas de chars au triage** : la Gare est une cour de rails sans trafic ; une frénésie de chars y était
  impossible (vu à la capture).
- Sons : `frenesie` (le coup qui lance) et `frenesie_fin` (la fanfare), générés par ElevenLabs, synthèse en
  filet ; **pas écoutés** — à Martin de les juger.
- Juges : `tests/test_frenesies.py` (une par district, une ruelle libre de son district, un paquet ou un mur
  la chassent, rejointe à pied, une arme du catalogue, aucune ne paie mieux qu'une mission, elles ne
  déplacent rien, la bande nord sait les décaler) et `tests/test_frenesies_js.py` (l'icône lance la frénésie
  et prête l'arme, ni au volant ni pendant une mission, les enfants et les passants ne comptent jamais,
  réussie elle paie une fois et se sauvegarde, le temps la rate, la sauvegarde n'emporte pas l'arme, les
  chars du joueur seulement, la gang rapplique et l'hôpital la rate, le bilan) ; vingt mutations les font
  toutes rougir.

**La ligne est livrée** : les quatre activités sont là.
