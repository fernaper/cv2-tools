# MIT License
# Copyright (c) 2019 Fernando Perez
from cv2_tools.Managment import ManagerCV2
import cv2


def main():
    manager_cv2 = ManagerCV2(cv2.VideoCapture(0), is_stream=True, keystroke=27, wait_key=1, fps_limit=60)

    for frame in manager_cv2:
        frame = cv2.flip(frame, 1)
        cv2.imshow('Example easy manager', frame)
    cv2.destroyAllWindows()
    print(manager_cv2.get_fps())

if __name__ == '__main__':
    main()
