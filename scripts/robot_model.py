"""
@brief Script contenant les modèles géométriques direct et inverse d'un robot
type delta linéaire (connu aussi sous le nom de Kossel ou Rostock).

@author Mohamed-iadh BANI <mohamed-iadh.bani@etu.sorbonne-universite.fr>

@date 2021-07-09
"""

import serial
import click
import time
import math as m

DEFAULT_VELOCITY = 1000  # [mm/s]
EPS = 1e-1               # [mm^2] erreur maximale équations de la sphère
PAUSE = .2               # [s]
PORT = 'COM7'            # port usb
STEP = 5                 # [mm]

class Kossel:
    def __init__(self, port, height, forearm, in_radius, out_radius):

        # position opérationnelle initiale
        self._x, self._y, self._z = 0, 0, height

        # position articulaire initiale
        self._q1, self._q2, self._q3 = 400, 400, 400

        # constantes : hauteur espace de travail, longueur bras
        self._H, self._L = height, forearm

        # constante largeur couronne
        if in_radius < out_radius:
            self._R = out_radius - in_radius
        else:
            print("\x1B[31mERR Plate radius must be greater than carri radius.")

        # connexion à l'imprimante
        try:
            self._s = serial.Serial(port, 250000)
        except serial.SerialException:
            print("\x1B[31mERR Printer port is either busy or missing.\x1B[m")
            exit(1)

        # laisser le temps à la connexion de s'établir
        time.sleep(1)

        # initialisation de la position
        self.home()
    
################################################################################

    # méthodes auxiliaires

    def home(self):
        self._s.write(b'G28\n')  # initialisation position
        self._x, self._y, self._z = 0, 0, self._H

    def close(self):
        self._s.close()

    def can_reach(self, x: float, y: float, z: float):
        eqn_sphere = [(x - self._R)**2 + y**2 + (z - self._q1)**2,
        (x + self._R/2)**2 + (y - m.sqrt(3) * self._R / 2)**2 + (z - self._q2)**2,
        (x + self._R/2)**2 + (y + m.sqrt(3) * self._R / 2)**2 + (z - self._q3)**2]

        return all(eqn <= self._L**2 for eqn in eqn_sphere)

################################################################################

    # MGI

    def goto(self, x: float = 0, y: float = 0, z: float = 0,
             v: float = DEFAULT_VELOCITY, pause: float = 0):
        if self.can_reach(x, y, z):
            self._x, self._y, self._z = x, y, z
            self._s.write(bytes(f'G0 X{x} Y{y} Z{z} F{v}\n', encoding='utf-8'))

            time.sleep(pause)
            return True
        
        print(f"WRN Can't reach target : X{x} Y{y} Z{z}")
        return False

    def move(self, x: float = 0, y: float = 0, z: float = 0,
             v: float = DEFAULT_VELOCITY, pause: float = 0):
        self.goto(self._x + x, self._y + y, self._z + z, v, pause)

    def mgd(self, a, b, c, v=DEFAULT_VELOCITY, pause=0):


        A = (b + c - 2*a) / (3 * self._R)
        B = (2 * a**2 - b**2 - c**2) / (6 * self._R)
        C = (c - b) / (m.sqrt(3) * self._R)
        D = (b**2 - c**2) / (2 * m.sqrt(3) * self._R)

        E = B - self._R
        F = A**2 + C**2 + 1
        G = A*E + C*D - a
        H = E**2 + D**2 + a**2 - self._L**2

        I = G**2 - F*H
        if I >= 0:
            z = (G + m.sqrt(G**2 - F*H)) / F
            x, y = A*z + B, C*z + D
            self._q1, self._q2, self._q3 = a, b, c
        else: 
            print(f"WRN Can't reach target : A{a} B{b} C{c}")
    
    def update(self, x, y, z):
        pass

    def dupdate(self, a, b, c):
        pass


if __name__ == '__main__':

    robot = Kossel(PORT, height=322.5, forearm=217, in_radius=75, out_radius=80)

    print("\x1B[34m1. Touches A, Z et E pour incrémenter sur X, Y et Z ;")
    print("2. Touches Q, S et D pour décrémenter sur X, Y et Z ;")
    print("3. Touche Shift ou Verr. Maj. pour passer en mode MGD ;")
    print("4. Touche echap pour quitter.\x1B[m")
    
    c = ''
    cmd = {'a': (STEP, 0, 0), 'z': (0, STEP, 0), 'e': (0, 0, STEP), 'q': (-STEP, 0, 0), 's': (0, -STEP, 0), 'd': (0, 0, -STEP)}
    mvt = {False: robot.dmove, True: robot.move}

    while c != '\x1B':
        c = click.getchar(echo=False)

        if c.lower() in mvt:
            mvt[c.lower() == c](*cmd[c.lower()], pause=PAUSE)

    robot.close()
