# L'écran du compte se lit d'un coup d'œil

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (22 sept. 2026), capture à l'appui : « améliore cet écran ». Connecté, l'écran du compte
empilait tout au même rang : le décor (l'enseigne du TERMINUS) se lisait à travers la liste des
parties, « 4590 $ » se cassait sur deux lignes, les trois parties ne s'alignaient pas, « Ajouter un
NIP à cet appareil » était le bouton le plus large de l'écran, et « Effacer mon compte » avait le
même poids que « Se déconnecter ».

On le range en trois blocs nommés : **Tes parties** (un tableau : partie, jour, argent en milliers
séparés, date — les colonnes alignées, rien ne se casse, et sur un téléphone la date passe sous la
ligne), **Cet appareil** (le NIP : un champ court, un bouton court, et une ligne qui dit à quoi il
sert), puis les boutons. « Effacer mon compte » descend sous « Ce qu'on garde », en rouge discret :
il se trouve sans chercher, mais on ne le prend plus pour un bouton de tous les jours. Le voile du
compte devient opaque.

⚠️ Aucun identifiant ne change : les juges du compte, du NIP et de l'effacement les suivent tous.

## Notes

Livré le 22 sept. 2026.

- **Il sort de la boîte du jeu** : `#voile-compte` est en `position: fixed` sur toute la fenêtre,
  fond opaque, `z-index: 20` (au-dessus des commandes tactiles). En portrait, la boîte faisait
  390×219 et l'on n'y lisait que deux lignes à la fois ; le juge « tout l'écran du compte
  s'atteint » mesure maintenant contre le voile (`DANS_LE_COMPTE`) et exige qu'il couvre la
  fenêtre. `DANS_L_ECRAN` (la boîte) reste pour l'écran titre.
- **Tes parties sur le serveur** : une rangée par case, quatre `span` (`compte-parties__partie`,
  `__jour`, `__argent`, `__quand`) sur des colonnes partagées (`subgrid`) ; l'argent en milliers
  (`toLocaleString('fr-CA')`). Sous 34em de large (requête de conteneur `compte`), la date passe
  sous la rangée.
- **Cet appareil** : le NIP dans son bloc, un champ de 7em, « Ajouter un NIP » / « Retirer le
  NIP », et une ligne qui dit ce qu'il fait (le jeu le demande à chaque lancement).
- **Effacer mon compte** descend sous « Ce qu'on garde », en `bouton--discret` rouge ; la
  confirmation est `bouton--danger`, « Non, le garder » reste le bouton mis en avant.
- Une seule largeur pour tout (`--compte-l`, en `rem`) : en `em`, la rubrique (12px) et la
  liste (15px) n'avaient pas la même largeur et les filets ne s'alignaient pas.
