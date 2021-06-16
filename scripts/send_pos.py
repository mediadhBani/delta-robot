from typing_extensions import ParamSpecKwargs
import serial as serial
import click
import time

class Kossel:
    def __init__(self, port: str, height: float):
        self._x, self._y, self._z = 0, 0, height
        self._h = [0, 0, height]  # position home
        self._s = serial.Serial(port, 250000)

        self.home()

    def home(self):
        self._s.write(b'G28\n')  # initialisation de la position
        time.sleep(1)
        self._x, self._y, self._z = self._h

    def goto_ar(self, d1: float=0, d2: float=0, d3: float=0):
        pass

    def goto_op(self, x: float=0, y: float=0, z: float=0):
        if 0 < z <= self._h:
            self._s.write(bytes(f'G90\nG1 X{x} Y{y} Z{z}\n', encoding='utf-8'))
            self._x, self._y, self._z = x, y, z

        else:
            print(f"Position inatteignable : X{x} Y{y} Z{z}")

    def move_ar(self, d1: float=0, d2: float=0, d3: float=0):
        pass

    def move_op(self, x: float=0, y: float=0, z: float=0):
        if self.is_within_range_op(self._x + x, self._y + y, self._z + z):
            self._s.write(bytes(f'G91\nG1 X{x} Y{y} Z{z}\n', encoding='utf-8'))
        else:
            print(f"Mouvement interdit : X{x} Y{y} Z{z}")

    def is_within_range_op(self, x: float, y: float, z: float):
        pass
    
    def is_within_range_ar(self, d1: float, d2: float, d3: float):
        pass

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
            ser.write(b'G1 X5\n')

        elif c == 's':  # mouvement x-
            ser.write(b'G1 X-5\n')
        
        elif c == 'e':  # mouvement y+
            ser.write(b'G1 Y5\n')
        
        elif c == 'd':  # mouvement y-
            ser.write(b'G1 Y-5\n')
        
        elif c == 'r':  # mouvement z+
            ser.write(b'G1 Z5\n')

        elif c == 'f':  # mouvement z-
            ser.write(b'G1 Z-5\n')
        
        elif c == 'h':  # retour position home
            ser.write(b'G28\n')

        elif c == 'q':  # quitter
            break

        time.sleep(.2)

    ser.write(b'G90\n')  # coordonnees absolues
    time.sleep(1)

    ser.close()
