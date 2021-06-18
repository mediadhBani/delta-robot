import serial as serial
import click
import time

class Kossel:
    def __init__(self, port: str, height: float, forearm: float,
                 in_radius: float, out_radius: float):

        self._x, self._y, self._z = 0, 0, height

        self._s = serial.Serial(port, 250000)
        self.h = (0, 0, height)

        self._s.write(b'G90\n')
        self.home() 

        time.sleep(2)

    def home(self):
        self._s.write(b'G28\n')  # initialisation de la position
        self._x, self._y, self._z = self.h
        time.sleep(2)

    def goto(self, x: float=0, y: float=0, z: float=0, pause: float=0):
        if self.can_reach(x, y, z):
            self._x, self._y , self._z = x, y, z
            self._s.write(bytes(f'G1 X{x} Y{y} Z{z}\n', encoding='utf-8'))

            time.sleep(pause)
        else:
            print(f"WRN Can't reach target : X{x} Y{y} Z{z}")
    
    def move(self, x: float=0, y: float=0, z: float=0, pause: float=0):
        self.goto(self._x + x, self._y + y, self._z + z, pause)

    def can_reach(self, x: float, y: float, z: float):
        # if self.L**2 - (self.r - self.R + x)**2 - 
        return True
        

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

    ser.write(b'G90\n')  # coordonnees absolues
    time.sleep(1)

    ser.close()
