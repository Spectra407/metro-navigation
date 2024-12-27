# NOMS : Kenny Ly, Théo Houlachi, Léonard Shi, Eva Delarue

import turtle
import tkinter
import math
import random

'''CLASS PILE'''
class Pile:
    def __init__(self):
        self._data = []

    def taille(self):
        return len(self._data)

    def estvide(self):
        return self.taille() == 0

    def empile(self, s):
        self._data.append(s)

    def depile(self):
        if self.estvide():
            raise LookupError('La pile est vide')
        return self._data.pop()

    def sommet(self):
        if self.estvide():
            raise LookupError('La pile est vide')
        return self._data[-1]

    def change_sommet(self, s):
        if self.estvide():
            raise LookupError('La pile est vide')
        self._data[-1] = s

    def __str__(self):
        return 'Pile: ' + ', '.join([str(item) for item in self._data])

'''CLASS GRAPHE'''
# Classes pour représenter les graphes
# On définit deux classes: Sommet et Graphe

# Un sommet connaît son nom (une chaîne) et ses voisins (un
# dictionnaire qui associe des sommets à des poids d'arêtes)

# version 2: supporte les graphes orientés et non orientés

class Sommet:
    def __init__(self, nom):
        '''Crée un sommet relié à aucune arête'''
        self._nom = nom
        self._voisins = {}

    def ajouteVoisin(self, v, poids=1):
        '''Ajoute ou modifie une arête entre moi et v'''
        self._voisins[v] = poids

    def listeVoisins(self):
        '''Liste tous les voisins'''
        return self._voisins.keys()

    def estVoisin(self, v):
        '''Retourne un booléen: True si je suis voisin de v, False sinon'''
        return v in self._voisins

    def poids(self, v):
        '''Retourne le poids de l'arête qui me connecte à v'''
        if v in self._voisins:
            return self._voisins[v]
        return None

    def __str__(self):
        '''Retourne mon nom'''
        return str(self._nom)

# Un graphe connaît ses sommets
# C'est un dictionnaire qui associe des noms avec des sommets
class Graphe:
    def __init__(self, oriente=True):
        '''Crée un graphe vide'''
        self._sommets = {}
        self._oriente = oriente

    def estOriente(self):
        return self._oriente

    def sommet(self, nom):
        '''Retourne le sommet de ce nom'''
        if nom in self._sommets:
            return self._sommets[nom]
        return None

    def listeSommets(self, noms=False):
        '''Liste tous les sommets'''
        if noms:
            return list(self._sommets.keys())
        else:
            return list(self._sommets.values())

    def ajouteSommet(self, nom):
        '''Ajoute un nouveau sommet'''
        if nom in self._sommets:
            return None  # sommet déjà présent
        nouveauSommet = Sommet(nom)
        self._sommets[nom] = nouveauSommet

    def ajouteArete(self, origine, destination, poids=1):
        '''Relie les deux sommets par une arête.
           Crée les sommets s'ils n'existent pas déjà'''
        self.ajouteSommet(origine)  # ne fait rien si les
        self.ajouteSommet(destination)  # sommets existent déjà
        s1 = self.sommet(origine)
        s2 = self.sommet(destination)
        s1.ajouteVoisin(s2, poids)
        if not self._oriente and origine != destination:
            s2.ajouteVoisin(s1, poids)

    def listeAretes(self, noms=False):
        '''Liste toutes les arêtes'''
        aretes = []
        for origine in self.listeSommets():
            for dest in origine.listeVoisins():
                if not self.estOriente() and str(origine) > str(dest):
                    continue  # compter chaque arête une seule fois si non oriente
                if noms:
                    aretes.append((str(origine), str(dest), origine.poids(dest)))
                else:
                    aretes.append((origine, dest, origine.poids(dest)))
        return aretes

    def __str__(self):
        '''Représente le graphe comme une chaîne'''
        return ', '.join(a + ' / ' + b + ':' + str(c) for (a, b, c) in self.listeAretes(True))


'''ÉTAPE 1: ALGORITHME POUR TROUVER LA STATION LA PLUS PROCHE DES COORDONNÉES DONNÉES'''
def depart_metro(dico, coord): # distance euclidienne
    '''Prend en argument un dictionnaire {station: coordonnées} ainsi que les coordonnées de départ de l'utilisateur,
    et retourne le nom de la station la plus proche.'''
    noms_stations = list(dico.keys())
    distance = []
    for position in dico.values():
        a, b = position          # les coordonnées des stations du dictionnaire
        c, d = coord             # les coordonnées de l'utilisateur
        distance.append(math.sqrt((c-a)**2 + (d-b)**2))    # Trouve la distance entre les coordonnées et toutes les stations du système de métro
    i = distance.index(min(distance))     # Trouve l'index de la distance la plus petite dans la liste
    return noms_stations[i]        # Retourne le nom de la station associé à l'index trouvé précédemment


'''ÉTAPE 2: ALGORITHME POUR TROUVER LE TRAJET DE METRO LE PLUS COURT'''
def lire_fichier_graphe(nom_fichier):
    '''Fabrique un graphe non orienté à partir du fichier. Retourne le graphe.'''
    G = Graphe(oriente= False)
    with open(nom_fichier, 'r', encoding='utf-8') as fp:
        for ligne in fp:
            if ligne == '' or ligne[0] == '#' or ligne == '\n':   # Saute la ligne si c'est un commentaire ou une ligne vide
                continue
            (depart, arrivee, poids) = ligne.strip().split()      # Crée une arête
            G.ajouteArete(depart, arrivee, int(poids))
    return G

def dijkstra(G, depart, destination):
    '''Trouve le chemin le plus court entre le point de départ et d'arrivée,
    et retourne la distance entre le point de départ et d'arrivée ainsi que
    chaque sommet parcouru pour se rendre du point de départ au point d'arrivée.'''
    if depart == destination:   # Si la station d'arrivée est la même que la station de départ, le nom de la station est retourné
        return [str(depart)]

    stations = set(G.listeSommets())
    precedent = {station: None for station in stations}   # Dictionnaire {station: station précédente pour le trajet le plus court à emprunter}
    dist = {station: math.inf for station in stations}    # Commence avec toutes les stations à une distance infinie du point de départ
    dist[depart] = 0

    while len(stations) > 0:
        distance_min = math.inf
        for station in stations:
            distance = dist[station]
            if distance < distance_min:
                (station_actuelle, distance_min) = (station, dist[station])
        stations.remove(station_actuelle)

        for voisin in station_actuelle.listeVoisins():
            if voisin in stations:
                nouvelle_distance = dist[station_actuelle] + station_actuelle.poids(voisin)  # Vérifie si la nouvelle distance est plus efficace
                if nouvelle_distance < dist[voisin]:
                    dist[voisin] = nouvelle_distance
                    precedent[voisin] = station_actuelle    # On change la valeur du dictionnaire : pour se rendre à la station 'voisin', le plus rapide moyen serait à partir de la station 'station_actuelle'

                    if voisin == destination:        # Si la prochaine station est le point d'arrivée, le chemin le plus court a été trouvé
                        chemin = [str(destination)]
                        while precedent[destination] is not None:        # Retrace l'entièreté du chemin à l'envers à l'aide du dictionnaire 'precedent'
                            destination = precedent[destination]
                            chemin.append(str(destination))               # Ajoute à la liste 'chemin' une version lisible des stations parcourues
                        chemin.reverse()
                        return chemin    # Retourne la liste de toutes les stations du trajet le plus court.


'''ÉTAPE 3: DEMANDER LE INPUT DE L'UTILISATEUR'''
# Le point de départ est choisit en cliquant sur l'interface graphique!
destination = input("Entrez le nom de la station de métro pour votre destination (Si il y a des espaces, utilisez plutôt des '-'): ").upper()


'''ÉTAPE 4: INITIALISATION DE TURTLE'''
# Fonctions nécessaires pour faciliter le tracé turtle
def read_coords(nom_fichier):
    '''Prend en argument un fichier txt et retourne une pile contenant chaque coordonnée à suivre.'''
    coords_pile = Pile()
    with open(nom_fichier, 'r', encoding='utf-8') as fp:
        for ligne in fp:
            coord = tuple(ligne.strip().split()[1:3])    # Trouve les coordonnées du fichier txt et les transforme en tuple
            coords_pile.empile(coord)       # Met les coordonnées dans une pile
        return coords_pile

def dictionnaire_stations(nom_fichier):
    '''Prend en argument un fichier txt et retourne le dictionnaire de chaque station présente et ses coordonnées.'''
    dictionnaire = {}
    with open(nom_fichier, 'r', encoding='utf-8') as fp:
        for ligne in fp:
            (nom, coord_x, coord_y) =  ligne.strip().split()    # Crée un tuple avec le nom de la station et ses coordonnées x et y
            dictionnaire[nom] = (int(coord_x), int(coord_y))    # Ajoute au dictionnaire les clés et valeurs du tuple
    return dictionnaire


# Paramètres de l'écran
carte = turtle.Screen()
carte.title("Carte STM")     # Nom de la fenêtre Turtle
carte.bgcolor("black")
WIDTH = 1000
HEIGHT = 1000
carte.setup(width=WIDTH, height=HEIGHT, startx=300, starty=0)

# Paramètres de la tortue initiale
pointeur = turtle.Turtle()
pointeur.shape("blank")      # Le Turtle qui dessine est invisible
pointeur.pensize(15)
pointeur.speed(0)
pointeur.penup()

curseur = turtle.Turtle()
curseur.shape("blank")
curseur.color("DarkBlue")
curseur.pensize(2)
curseur.speed(0)
curseur.penup()

# Dessin de la rivière
def parcours_riviere(liste):
    '''Prend en argument une liste de coordonnées et trace les rivières'''
    curseur.pendown()
    for i in liste:
        curseur.goto(i[0], i[1])
    curseur.penup()

liste_riviere1 = [(-400,50), (-350,80), (-300,120), (-260,140), (-220,140), (-195,180), (-165,240), (-150,300), (-120,350), (-100,390), (-80,420), (0,500)]
curseur.pensize(25)
curseur.goto(-500,-100)
curseur.color("DarkBlue")
parcours_riviere(liste_riviere1)

liste_riviere2 = [(440,200), (400,140), (360,100), (320,60), (300,0), (300,-60), (320,-100), (340,-150), (400,-180), (380,-100), (350, -10), (340, 80)]
curseur.goto(500,350)
parcours_riviere(liste_riviere2)

liste_riviere3 = [(400,-180), (500,-220), (500,-500), (200,-500), (300, -300), (340,-150)]
curseur.goto(340,-150)
curseur.fillcolor("DarkBlue")
curseur.begin_fill()
parcours_riviere(liste_riviere3)
curseur.end_fill()


curseur.pensize(2)
turtle.tracer(0) # Accélère la vitesse de turtle pour les dessins décoratifs
curseur.pencolor("gray")
def arbre_triangulaire(x, y):
    '''Fonction qui dessine un arbre triangulaire situé à des coordonnées x et y'''
    curseur.penup()
    curseur.goto(x, y)
    curseur.setheading(90)
    curseur.pendown()
    curseur.forward(7)
    curseur.right(90)
    curseur.forward(5)
    curseur.left(100)
    curseur.forward(33)
    curseur.left(160)
    curseur.forward(33)
    curseur.left(100)
    curseur.forward(5)
    curseur.right(90)
    curseur.forward(7)
    curseur.left(90)
    curseur.forward(1)

def skyline(x, y):
    '''Fonction qui dessine une ville situé à des coordonnées x et y'''
    curseur.penup()
    curseur.goto(x,y)
    nombre_batiments = random.randint(4, 7)
    curseur.pendown()
    curseur.forward(5)
    for i in range(nombre_batiments):
        curseur.setheading(90)
        hauteur = random.randint(25, 150)
        curseur.pendown()
        curseur.forward(hauteur)
        curseur.right(90)
        epaisseur = random.randint(10, 30)
        curseur.forward(epaisseur)
        curseur.right(90)
        curseur.forward(hauteur)
        curseur.left(90)
        curseur.forward(5)
        curseur.penup()
    curseur.pendown()
    curseur.goto(x, y)


# Dessin du bonhomme allumette :)
def aziz(x, y):
    '''Fonction qui dessine un petit bonhomme allumette situé à des coordonnées x et y'''
    curseur.setheading(0)
    curseur.pencolor("white")
    curseur.pensize(2)
    curseur.penup()
    curseur.goto(x, y+20)
    curseur.pendown()
    curseur.circle(5)
    curseur.penup()
    curseur.goto(x, y+20)
    curseur.setheading(270)
    curseur.pendown()
    curseur.forward(5)
    curseur.left(90)
    curseur.forward(5)
    curseur.penup()
    curseur.goto(x, y+15)
    curseur.setheading(180)
    curseur.pendown()
    curseur.forward(5)
    curseur.penup()
    curseur.goto(x, y+15)
    curseur.setheading(270)
    curseur.pendown()
    curseur.forward(6)
    curseur.left(30)
    curseur.forward(9)
    curseur.backward(9)
    curseur.right(60)
    curseur.forward(9)
    curseur.penup()
    curseur.goto(x+10,y+25)
    curseur.write("Aziz")


# Dessin des arbres
for i in range(40):
    x = random.randint(40, 250)
    y = random.randint(220, 490)
    arbre_triangulaire(x, y)

for i in range(20):
    x = random.randint(410, 500)
    y = random.randint(-170, 130)
    arbre_triangulaire(x, y)

# Dessin des villes
skyline(-420, 270)
skyline(-275, -25)
skyline(-450, -250)
skyline(-250, -400)


# Dessin des lignes du metro
def dessin_ligne(couleur):
    '''Fonction qui dessine chacune des lignes du réseau individuellement en faisant appel à des fichiers txt'''
    pointeur.pencolor(couleur)
    fichier = couleur + ".txt"       # crée une variable du nom du fichier txt en prenant en compte l'argument de la fonction
    ligne = read_coords(fichier)
    depile = ligne.depile()
    pointeur.setpos(int(depile[0]), int(depile[1]))
    pointeur.pendown()              # commence le traçage des lignes du réseau
    while not ligne.estvide():      # continue de dépiler les stations de la pile tant qu'elle n'est pas vide
        depile = ligne.depile()
        pointeur.goto(int(depile[0]), int(depile[1]))     # trace la ligne entre deux stations distinctes
    pointeur.penup()               # arrête le traçage

dessin_ligne("orange")
dessin_ligne("blue")
dessin_ligne("green")
dessin_ligne("yellow")

# Le dictionnaire final contient chaque station et ses coordonnées
dictio_orange = dictionnaire_stations('orange.txt')
dictio_bleu = dictionnaire_stations('blue.txt')
dictio_vert = dictionnaire_stations('green.txt')
dictio_jaune = dictionnaire_stations('yellow.txt')
liste_dictio = [dictio_orange, dictio_bleu, dictio_vert, dictio_jaune]
dictio_final = {}
for i in liste_dictio:
    dictio_final.update(i)

'''Affichage des points correspondant aux stations'''

# Liste des stations ayant un point blanc de plus grande taille (terminus et intersections)
intersections_terminus = ["MONTMORENCY", "CÔTE-VERTU","JEAN-TALON", "BERRI-UQAM", "LONGUEUIL","LIONEL-GROULX", "HONORÉ-BEAUGRAND", "ANGRIGNON", "SNOWDON", "SAINT-MICHEL"]


'''Affichage du nom de toutes les stations sur la carte'''
# Beaucoup de cas différents sont présents afin qu'aucun nom ne se chevauche ou chevauche la ligne de métro, il faut
# donc beaucoup d'exceptions spécifiques pour que l'affichage de tous les noms soit sans défaut


# Liste de toutes les exceptions de placement de noms possibles
exceptions_gauche = ["MONTMORENCY", "VILLA-MARIA", "NAMUR", "DE-LA-SAVANE", "DU-COLLÈGE", "CÔTE-VERTU", "DE-CASTELNAU", "PARC",
                     "ACADIE", "ÉDOUARD-MONTPETIT", "UNIVERSITÉ-DE-MONTRÉAL", "SAINT-LAURENT", "PLACE-DES-ARTS", "MCGILL", "PEEL",
                     "GUY-CONCORDIA", "ATWATER"]
exceptions_gauche_extreme = ["SHERBROOKE", "BERRI-UQAM"]
exceptions_haut_gauche = ["CÔTE-DES-NEIGES"]
exceptions_bas_gauche = ["VENDÔME","SNOWDON", "CÔTE-SAINTE-CATHERINE", "PLAMONDON", "OUTREMONT"]
exceptions_bas = ["DE-LA-CONCORDE"]
exceptions_bas_centre = ["PLACE-SAINT-HENRI"]
exceptions_droite = ["CHAMP-DE-MARS", "PLACE-D'ARMES", "SQUARE-VICTORIA-OACI", "BONAVENTURE", "LUCIEN-L'ALLIER", "GEORGES-VANIER",
                         "SAINT-MICHEL", "D'IBERVILLE", "FABRE", "HONORÉ-BEAUGRAND", "RADISSON", "LANGELIER", "CADILLAC", "ASSOMPTION",
                         "VIAU", "PIE-IX", "JOLIETTE", "PRÉFONTAINE", "FRONTENAC", "PAPINEAU", "BEAUDRY", "CHARLEVOIX", "LASALLE",
                         "DE-L'ÉGLISE", "JEAN-DRAPEAU", "LONGUEUIL"]
exceptions_droite_extreme = ["VERDUN", "MONK", "ANGRIGNON"]
exceptions_bas_droite = ["JOLICOEUR"]

pointeur.color("white")     # pour écrire les noms des stations en blanc
for dictio_key in dictio_final.keys():
    coord_dictio = dictio_final[dictio_key]              # prend le tuple des coordonnées de chaque station
    pointeur.setpos(coord_dictio[0], coord_dictio[1])    # place le Turtle sur la coordonnée de chaque station
    if dictio_key in intersections_terminus:             # si la station est dans la liste de terminus ou d'intersections, on dessine un plus gros point
        pointeur.dot(15, "white")
    else:
        pointeur.dot(10, "white")

    # Exceptions de chaque type de placement des noms sur la carte
    # Beaucoup de code mais le résultat est vraiment beau!
    if dictio_key in exceptions_gauche:
        pointeur.setheading(20)
        pointeur.backward(20)
        pointeur.write(dictio_key, align='right')
    elif dictio_key in exceptions_gauche_extreme:
        pointeur.setheading(20)
        pointeur.backward(25)
        pointeur.write(dictio_key, align='right')
    elif dictio_key in exceptions_haut_gauche:
        pointeur.setheading(0)
        pointeur.backward(10)
        pointeur.write(dictio_key, align='right')
    elif dictio_key in exceptions_bas_gauche:
        pointeur.setheading(70)
        pointeur.backward(25)
        pointeur.write(dictio_key, align='right')
    elif dictio_key in exceptions_bas:
        pointeur.setheading(270)
        pointeur.forward(30)
        pointeur.write(dictio_key)
    elif dictio_key in exceptions_bas_centre:
        pointeur.setheading(270)
        pointeur.forward(35)
        pointeur.write(dictio_key, align= 'center')
    elif dictio_key in exceptions_droite:
        pointeur.setheading(340)
        pointeur.forward(20)
        pointeur.write(dictio_key)
    elif dictio_key in exceptions_bas_droite:
        pointeur.setheading(320)
        pointeur.forward(25)
        pointeur.write(dictio_key)
    elif dictio_key in exceptions_droite_extreme:
        pointeur.setheading(340)
        pointeur.forward(25)
        pointeur.write(dictio_key)
    else:
        pointeur.setheading(0)
        pointeur.forward(20)
        pointeur.write(dictio_key)


'''ÉTAPE 5: TURTLE DU TRAJET LE PLUS COURT'''
# Étape 1: Départ à la première station de métro, la ligne rouge est l'itinéraire à emprunter
turtle.tracer(1)        # Ralentit la vitesse de turtle pour voir le trajet dessiné

def fonction_principale(x, y):
    '''Fonction principale qui tracera le trajet optimal selon les coordonnées où l'utilisateur clique'''
    coord_depart = (x,y)
    station_proche = depart_metro(dictio_final, coord_depart)
    pointeur.penup()
    pointeur.setpos(coord_depart[0], coord_depart[1])
    pointeur.color('red')
    pointeur.speed(5)
    pointeur.pendown()

    aziz(coord_depart[0], coord_depart[1])  # Dessin de Aziz

    pointeur.goto(int(dictio_final[station_proche][0]), int(dictio_final[station_proche][1]))

    # Étape 2: Trajet de métro jusqu'à la destination
    graphe = lire_fichier_graphe('caps_metro.txt')
    depart_sommet = graphe.sommet(station_proche)
    destination_sommet = graphe.sommet(destination)
    trajet_metro = dijkstra(graphe, depart_sommet, destination_sommet)
    for current_station in trajet_metro:
        pointeur.goto(int(dictio_final[current_station][0]), int(dictio_final[current_station][1]))
    pointeur.penup()

carte.onscreenclick(fonction_principale)       # Permet le choix de la position de départ à l'aide d'un click de la souris

'''FIN DU TURTLE'''
carte.mainloop()
