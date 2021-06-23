import serial as serial
import click
import numpy as np
import time

DEFAULT_VELOCITY = 1000

class Kossel:
    def __init__(self, port: str, height: float, forearm: float, in_radius: float, out_radius: float):

        self._x, self._y, self._z = 0, 0, height
        self._height = height
        self._forearm = forearm
        self._in_radius, self._out_radius = in_radius, out_radius

        self._s = serial.Serial(port, 250000)

        self._s.write(b'G90\n')
        self.home()

    def home(self, pause=5):
        self._s.write(b'G0 F2000\nG28\n')  # initialisation de la position
        self._x, self._y, self._z = 0, 0, self._height
        time.sleep(pause)

    def goto(self, x: float = 0, y: float = 0, z: float = 0, v: float = DEFAULT_VELOCITY, pause: float = 0):
        if self.can_reach(x, y, z):
            self._x, self._y, self._z = x, y, z
            self._s.write(bytes(f'G0 X{x} Y{y} Z{z} F{v}\n', encoding='utf-8'))

            time.sleep(pause)
        else:
            print(f"WRN Can't reach target : X{x} Y{y} Z{z}")

    def move(self, x: float = 0, y: float = 0, z: float = 0, v: float = DEFAULT_VELOCITY, pause: float = 0):
        self.goto(self._x + x, self._y + y, self._z + z, v, pause)

    def can_reach(self, x: float, y: float, z: float):
        return x**2 + y**2 <= self._out_radius**2


if __name__ == '__main__':
    try:
        ser = serial.Serial('COM7', 250000)
    except Exception:
        print("Le port de l'imprimante est occupé ou inexistant.")
        exit(1)

    time.sleep(1)

    ser.write(b'G91\n')  # deplacements relatifs
    time.sleep(1)

    while True:
        c = click.getchar(echo=False)

        if c == 'z':  # mouvement x+
            ser.write(b'G0 X5\n')

        elif c == 's':  # mouvement x-
            ser.write(b'G0 X-5\n')

        elif c == 'e':  # mouvement y+
            ser.write(b'G0 Y5\n')

        elif c == 'd':  # mouvement y-
            ser.write(b'G0 Y-5\n')

        elif c == 'r':  # mouvement z+
            ser.write(b'G0 Z5\n')

        elif c == 'f':  # mouvement z-
            ser.write(b'G0 Z-5\n')

        elif c == 'h':  # retour position home
            ser.write(b'G28\n')

        elif c == 'q':  # quitter
            break

    ser.write(b'G90\n')  # coordonnees absolues
    time.sleep(1)

    ser.close()
