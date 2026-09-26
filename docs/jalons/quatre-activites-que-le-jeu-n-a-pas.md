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
