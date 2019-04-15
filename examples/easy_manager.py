# MIT License
# Copyright (c) 2019 Fernando Perez
from cv2_tools.Management import ManagerCV2
import cv2


def main():
    manager_cv2 = ManagerCV2(cv2.VideoCapture(0), is_stream=True, fps_limit=60)
    manager_cv2.add_keystroke(27, 1, print, 'Pressed esc. Exiting', exit=True)
    manager_cv2.add_keystroke(113, 1, print, 'Pressed', 'Q')
    for frame in manager_cv2:
        frame = cv2.flip(frame, 1)
        cv2.imshow('Example easy manager', frame)
    cv2.destroyAllWindows()
    print('FPS: {}'.format(manager_cv2.get_fps()))

if __name__ == '__main__':
    main()
