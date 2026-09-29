# L'esquive : la roulade doit servir

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026 : « oui, durcir le défi ». Le défi s'appelle l'esquive, et un boxeur
qui ne roule jamais le gagne (vie 0,56) ; retirer l'invulnérabilité de la roulade ne fait
rougir aucun juge, et `roulades >= 3` compte les appuis sur la touche, pas les roulades
faites (voir [quatre juges rouges](quatre-juges-rouges-sur-dev.md#notes)). Durcir le DÉFI
(pas seulement le juge) : sans rouler, on perd ; en roulant au bon moment, on gagne ; et le
juge le prouve des deux côtés, avec les roulades vraiment faites.

- ⚠️ Le défi doit rester gagnable par un joueur humain : mesurer la fenêtre, pas seulement
  le résultat du juge.

## Notes

Livré le 29 sept. 2026. **Pourquoi on gagnait sans rouler** : le cousin était un débardeur ordinaire —
il courait à 1,28 px/image (le joueur, 2,0) et ne frappait qu'au tic des passants (`e.t % 40`, s'il était
à moins de 18 px pile à ce moment-là), après 5 images d'élan (83 ms : invisible). Tourner en rond le semait.
Mesuré au banc avant : sans rouler, sonné de justesse (vie 0,38 contre un seuil de 0,40, 7 coups sur
9 en 25 s — pile ou face selon le cercle) ; en roulant à l'aveugle toutes les 50 images, **gagné (0,50)** ;
et le juge roulait une image après l'élan, un réflexe de machine.

**Le cousin boxe** (`Rue`, `boxer` ; ses nombres dans la fiche, `missions.DEFIS`) : il court comme toi
(`allure` 0,95 → 1,45), il ne frappe plus au tic (`coupsDictes`, `Entites`) mais **annonce** chaque coup
à moins de 20 px — un cercle rouge au sol qui se referme pendant `annonce_s` (0,35 s), il te suit encore —,
puis l'élan d'une tape et le coup, plus long et plus large (portée 16 + 6 px, arc 1,6 rad, 13 de dégâts),
puis il souffle 1,2 s. Collé, il boxe sur place (lancé à ta vitesse, il poussait un joueur planté hors du
ring : « ESQUIVER, PAS FUIR » au lieu de « IL T'A SONNÉ »). Le panneau le dit : « SON CERCLE SE REFERME :
ROULE ! ».

**La fenêtre** : le poing part 26 images (433 ms) après que le cercle apparaît. Une roulade pressée entre
la 6e et la 25e image (≈ 110 à 420 ms, 19 images ≈ 320 ms) passe ; avant, elle est finie quand le coup
tombe et il t'a rattrapé ; après, c'est trop tard. De la 7e à la 15e, de côté, on sort de sa portée ;
de la 18e à la 25e, sous le poing, ce sont les images d'invincibilité qui sauvent.

Mesuré après (graines 1A2B3C4D, 7, 23 — identiques : l'épreuve ne tire aucun dé ; et quatre côtés
d'entrée dans le ring) : sans rouler, sonné en 7,9 s (0,35) ; planté au milieu, en 5,7 s ; roulades à
l'aveugle, en 11,6 s ; roulade après le coup, en 7,9 s ; roulade à 200 ms de côté ou à 367 ms à travers
lui, gagné à 1,00 (17 coups, 17 roulades faites, aucune touche) ; réflexe qui varie de 10 à 22 images,
gagné à 0,74. Les juges : `test_l_esquive_se_gagne_sans_frapper[tot|sous_le_poing]` (roulades FAITES,
comptées sur `j.roule`), `test_l_esquive_se_perd_sans_rouler_au_bon_moment[jamais|hasard|apres]`.
Mutations : sans l'invincibilité de la roulade, les deux gagnants rougissent ; cousin inoffensif (0 de
dégâts), les trois perdants et le planté rougissent ; cousin muet, tout rougit ; l'ancien pas (0,95),
gagnants et perdants rougissent ; roulade refusée (coût 250), les gagnants rougissent.

⚠️ Le souffle est juste : 17 roulades × 25 = 425, il en reste ~25 à la fin. Qui sprinte beaucoup (le même
bouton, tenu) peut manquer de souffle pour la roulade suivante — à essayer manette en main.
