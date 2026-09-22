# Suivre sans se faire voir : le stool attend qu'on soit au volant, roule jusqu'au poste, et le filage tolère un écart

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 22 sept. 2026 : « mission deuxième service impossible à faire, on se fait voir tout
de suite en sortant de la cantine ». Trois défauts de l'objectif `suivre` (f06, et h02 qui
le copie). (1) Le stool naît sur la tuile de rue la plus proche de la porte du casse-croûte
(`poserLeFuyard`, fait pour m50) : on sort à pied à moins de 3 tuiles de lui, `proche`
échoue à la première image. (2) Il roule en `fuite` + `poursuite` : il brûle les feux et
prend la sortie qui l'éloigne de toi — à pied, le temps de trouver un char, il est à plus de
10 tuiles. (3) `suivre` n'a AUCUNE condition de réussite : rien ne lit de `lieu`, le juge du
banc force l'étape à la main. Le correctif : un stool à part du fuyard — il naît à bonne
distance de la porte, moteur en marche, et attend que tu sois au volant ; il roule comme le
trafic (feux, vitesse de ville) vers le `lieu` de l'objectif (`poste` pour f06, `depanneur`
pour h02), aux croisements par `Monde.cheminRoute` ; l'objectif avance quand il y arrive ;
trop près ou trop loin se tolère un moment (un avertissement au HUD, puis l'échec), comme le
tracé des courses. Juge de banc : sortir du casse-croûte par la porte ne rate plus, et une
filature jouée jusqu'au poste finit la mission.
