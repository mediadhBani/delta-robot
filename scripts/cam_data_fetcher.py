import cv2

NOIR = ((0, 0, 0), (255, 255, 25))
H, W = 480, 640  # TODO

vid = cv2.VideoCapture(1)  # caméra secondaire (usb)

while True:
    _, frame = vid.read()

    pov = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # conversion BGR vers HSV
    pov = cv2.inRange(pov, *NOIR)                 # binarisation
    pov = cv2.bitwise_not(pov)                    # inversion binarisation

    mmt = cv2.moments(pov)

    cx, cy = mmt['m10'] / mmt['m00'], mmt['m01'] / mmt['m00']

    cv2.ellipse(pov, ((cx, cy), (50, 50), 0), (127, 127, 127), 2)

    cv2.imshow("Capture", pov)

    if cv2.waitKey(40) & 0xFF == ord('q'):
        vid.release()
        cv2.destroyAllWindows()
        break
