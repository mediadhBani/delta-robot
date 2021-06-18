import cv2
import numpy as np
from send_pos import Kossel

BLACK = ((0, 0, 0), (255, 255, 25))
RED = (0, 63, 63), (10, 255, 255)
BLUE = (150, 63, 63), (190, 255, 255)
H, W = 480, 640
# R = np.array([[-.5, -np.sqrt(3)/2], [-.5, np.sqrt(3)/2]])
R = np.full((2, 2), -1/np.sqrt(2)); R[0, 0] *= -1

CLR = RED

vid = cv2.VideoCapture(1)  # caméra secondaire (usb)

delta = Kossel('COM7', 322.5, 150, 75, 80)
delta.goto(z=100, pause=2)

while True:
    _, frame = vid.read()

    pov = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # conversion BGR vers HSV
    pov = cv2.inRange(pov, *CLR)                  # binarisation
    # pov = cv2.bitwise_not(pov)                  # inversion binarisation

    mmt = cv2.moments(pov)

    if mmt['m00']:
        cx, cy = mmt['m10'] / mmt['m00'], mmt['m01'] / mmt['m00']
        print(cx, cy)
        cv2.ellipse(pov, ((cx, cy), (30, 30), 0), (255, 0, 0), 2)

        # centrage
        err = (cx * 2/W - 1, cy * 2/H - 1)
        err = R @ err * 2
        # ex, ey = ex - 10, ey - 10
        # print(err)
        delta.move(*err)

    cv2.ellipse(pov, ((W/2, H/2), (30, 30), 0), (192, 192, 192), 2)
    cv2.imshow("Capture", pov)

    if cv2.waitKey(20) & 0xFF == ord('q'):
        vid.release()
        cv2.destroyAllWindows()
        break

    elif cv2.waitKey(20) & 0xFF == ord('h'):
        delta.home()
        delta.goto(z=100, pause=3)
        pass