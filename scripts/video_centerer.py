"""
@brief Script pour centrer la caméra montée sur l'effecteur du robot sur une
cible colorée.
"""

import cv2
import itertools
import matplotlib.pyplot as plt
import numpy as np
import pickle
import robot_model as rm


# intervalles de couleur HSV (0-179, 0-255, 0-255)
BLUE = (93, 80, 82), (125, 255, 255)
GREEN = (62, 127, 95), (89, 255, 255)
YELLOW = (12, 120, 141), (41, 255, 255)

# constantes utiles (capture)
CAM_ID = 0                                        # id de la caméra
COLOR = YELLOW                                    # couleur à détecter
DUREE = 20                                        # durée capture [s]
FRAME_HEIGHT, FRAME_WIDTH = 480, 640              # hauteur, largeur image
FRAME_AREA = FRAME_HEIGHT * FRAME_WIDTH           # aire image
FRAME_CENTER = FRAME_WIDTH / 2, FRAME_HEIGHT / 2  # centre image
KERNEL = np.ones((3, 3), np.uint8)                # filtre débruitage
PAUSE = .2                                        # cadençage [s]
PORT = 'COM7'                                     # port USB robot

# constantes utiles (commande)
MIN_AREA_TRIGGER = FRAME_AREA * .01  # aire minimale déclenchement commande
MIN_DIST_TRIGGER = 0**2              # distance minimale déclenchement commande
Z_PLANE = 150                        # plan XY de hauteur donnée [mm]

################################################################################

# connexion au robot
robot = rm.Kossel(PORT, height=322.5, forearm=217, in_radius=75, out_radius=80)

# connexion à la caméra
capture = cv2.VideoCapture(CAM_ID)

# variables de travail
arret_urgence = False            # pour forcer l'arrêt du programme
fig = plt.figure()
pause_ms = int(PAUSE * 1e3 / 2)  # pause des waitKey [ms]
temps = [.2 * i for i in range(int(DUREE / PAUSE))]
stats = open('stats.csv', 'w')   # fichier pour contenir statistiques utiles

# espace des paramètres : [intégral, proprtionnel, vitesse]
parametres = [[0, 4e-2, 1, 4], [0, 1, 2, 5, 10, 20], [200, 500, 2000, 5000]]

for ki, kp, vel in itertools.product(*parametres):
    # initialisation du test
    robot.home()
    robot.goto(0, 0, Z_PLANE, v=8000, pause=10)  # placement effecteur
    sum_ex, sum_ey = 0, 0                        # erreurs correcteur intégral
    data_x, data_y = [], []                      # enregistrement erreurs

    # l'asservissement est lancé pour `DUREE` secondes
    for i in range(len(temps)):
        _, frame = capture.read()  # capture de l'image

        # traitement de l'image :
        pov = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # conversion BGR vers HSV
        pov = cv2.inRange(pov, *COLOR)                # binarisation
        pov = cv2.medianBlur(pov, 3)                  # débruitage
        # pov = cv2.bitwise_not(pov)                    # inversion binarisation

        # calcul des moments de Legendre
        mmt = cv2.moments(pov)

        # si surface repérée suffisamment grande (évite de réagir aux bruits)
        if mmt['m00'] > MIN_AREA_TRIGGER:
            # barycentre du masque
            cx, cy = mmt['m10'] / mmt['m00'], mmt['m01'] / mmt['m00']

            # témoin visuel position barycentre
            cv2.ellipse(pov, ((cx, cy), (20, 20), 0), (255, 0, 0), 2)

            # erreur normalisée
            ex, ey = cx * 2/FRAME_WIDTH - 1, cy * 2/FRAME_HEIGHT - 1

            # envoi de la commande si distance minimale vérifiée
            if ex**2 + ey**2 > MIN_DIST_TRIGGER:
                # passage repère image vers repère robot
                u, v = (ex - ey) / np.sqrt(2), (-ex - ey) / np.sqrt(2)

                # composante intégrale
                sum_ex += u
                sum_ey += v

                # commande en sortie du correcteur
                cmd_x = sum_ex * ki + u * kp
                cmd_y = sum_ey * ki + v * kp

                robot.move(cmd_x, cmd_y, v=vel)
        else:
            ex, ey = float('nan'), float('nan')

        # récupération données
        data_x.append(ex)
        data_y.append(ey)

        # témoin visuel valeur consigne
        cv2.ellipse(pov, (FRAME_CENTER, (20, 20), 0), (192, 192, 192), 2)

        # affichage
        cv2.imshow("Capture", pov)

        if cv2.waitKey(pause_ms) == 27:  # bouton echap = arrêt du programme
            print("Arrêt d'urgence.")
            arret_urgence = True

    # tracé de la figure
    titre = f"I{ki:.0e}P{kp:.0e}V{vel}"
    plt.clf()
    plt.plot(temps, data_x, label="err x")
    plt.plot(temps, data_y, label="err y")
    plt.title(titre)
    plt.legend()
    plt.xlabel("temps [s]")
    plt.ylabel("erreur [float]")

    # enregistrement
    file = open(titre.replace('.', ',') + '.mpl', 'wb')
    pickle.dump(fig, file)
    file.close()

    # statistiques : erreurs absolues en x et y
    abs_x = [abs(e) for e in data_x if e != float('nan')]
    abs_y = [abs(e) for e in data_y if e != float('nan')]

    if abs_x or abs_y:
        avg_x, avg_y = np.mean(abs_x), np.mean(abs_y)  # moyennes x y
        std_x, std_y = np.std(abs_x), np.std(abs_y)    # ecart-types x y
        stats.write(f"{ki},{kp},{vel},{avg_x},{avg_y},{std_x},{std_y}\n")
    
    if arret_urgence:  # demande d'arrêt
        break

# fin du programme
capture.release()
cv2.destroyAllWindows()
robot.close()
stats.close()