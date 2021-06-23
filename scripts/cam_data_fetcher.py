import cv2
import numpy as np
import send_pos as sp
import collections
import time

# intervalles de couleur
BLACK = ((0, 0, 0), (255, 255, 25))
BLUE = (150, 63, 63), (190, 255, 255)
RED = (0, 63, 63), (10, 255, 255)

COLOR = RED

# nombre erreurs à considérer pour correcteur intégral
ERR_DEPTH = 5

# coefficients PID
POS_PID = {'i': 100}
VEL_PID = {'i': 10000}

FRAME_HEIGHT, FRAME_WIDTH = 480, 640            # hauteur, largeur image
FRAME_AREA = FRAME_HEIGHT * FRAME_WIDTH         # aire image
FRAME_CENTER = (FRAME_WIDTH/2, FRAME_HEIGHT/2)  # centre image

KERNEL = np.ones((3, 3), np.uint8)  # filtre débruitage
PAUSE = 100                         # temps pause entre deux images en ms

# matrice passage repère image à repère imprimante
TRANSFER_MATRIX = np.full((2, 2), 1/np.sqrt(2))
TRANSFER_MATRIX[0, 0] *= -1

# connexion avec l'imprimante
delta = sp.Kossel('COM7', height=322.5, forearm=217, in_radius=75, out_radius=80)
delta.goto(z=150, pause=12)  # placer tête impression 100 mm au dessus du plateau

# connexion avec la caméra
vid = cv2.VideoCapture(0)

# correcteur intégral : erreur / distance euclidienne sur 10 itérations
dist = collections.deque(0 for _ in range(ERR_DEPTH))
pos_err = np.zeros((ERR_DEPTH, 2))

while True:
    _, frame = vid.read()

    # traitement de l'image :
    pov = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # conversion BGR vers HSV
    pov = cv2.inRange(pov, *COLOR)                # binarisation
    pov = cv2.erode(pov, KERNEL)                  # débruitage
    # pov = cv2.bitwise_not(pov)                  # inversion binarisation

    # calcul des moments de Legendre
    mmt = cv2.moments(pov)

    # si surface repérée suffisamment grande
    if mmt['m00'] > FRAME_HEIGHT * FRAME_WIDTH / 100:
        cx, cy = mmt['m10'] / mmt['m00'], mmt['m01'] / mmt['m00']
        cv2.ellipse(pov, ((cx, cy), (20, 20), 0), (255, 0, 0), 2)

        # erreur normalisée
        err = [cx * 2/FRAME_WIDTH - 1, cy * 2/FRAME_HEIGHT - 1]

        # ajout nouvelle, retrait plus ancienne distance euclidienne
        dist.append(np.linalg.norm(err))
        dist.popleft()

        print(-sum(pos_err), sum(dist) * VEL_PID['i'])
        if dist[-1] > .02:
            err = TRANSFER_MATRIX @ err * POS_PID['i']
            np.roll(pos_err, 1, axis=0)
            pos_err[0, :] = err
            delta.move(*(-sum(pos_err)), v=sum(dist) * VEL_PID['i'])

            time.sleep(PAUSE / 1e3)

    cv2.ellipse(pov, (FRAME_CENTER, (20, 20), 0), (192, 192, 192), 2)
    cv2.imshow("Capture", pov)

    if cv2.waitKey(PAUSE) & 0xFF == ord('q'):
        vid.release()
        cv2.destroyAllWindows()
        break

    elif cv2.waitKey(PAUSE) & 0xFF == ord('h'):
        delta.home()
        dist = collections.deque(0 for _ in range(ERR_DEPTH))
        pos_err = np.zeros((ERR_DEPTH, 2))
        delta.goto(z=150, pause=12)