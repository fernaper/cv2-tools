import cv2
import numpy as np
from cv2_tools.Selection import SelectorCV2

x_mouse = 0
y_mouse = 0

def mouse_drawing(event, x, y, flags, params):
    global x_mouse,y_mouse

    x_mouse = x
    y_mouse = y
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Left click")

def main():
    global x_mouse,y_mouse

    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Frame")
    cv2.setMouseCallback("Frame", mouse_drawing)
    while True:
        selector = SelectorCV2()
        _, frame = cap.read()
        cv2.circle(frame, (x_mouse,y_mouse), 5, (0, 0, 255), -1)
        selector.add_zone((100,100,200,200), tags='Hola')
        frame = selector.draw(frame, coordinates=(x_mouse,y_mouse))

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
        elif key == ord("d"):
            circles = []
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
