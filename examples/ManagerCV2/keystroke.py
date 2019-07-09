import argparse

from cv2_tools.Management import ManagerCV2
import cv2


def key_manager(video, stream, fps):
    # Step 1: Create ManagerCV2 as in `basci.py`
    manager_cv2 = ManagerCV2(cv2.VideoCapture(video), is_stream=stream, fps_limit=fps)

    # Step 2: Add as much keystrokes as you want
    # Have in mind that each keystroke will be associated to a list of attributes
    # Each time you press an added key, the associated attributes will change theis
    # values, so if it was at False, it will change to True and vice versa
    # The second param means miliseconds to wait (if <= 0 it will stop until prressed)

    # I decide to add an exit keystroke pressing `esc` (it is asociated with an empty list of attributes)
    manager_cv2.add_keystroke(27, 1, exit=True)
    # Press `h` to the attribute `hello` to True
    # Then the same with the other ones...
    manager_cv2.add_keystroke(ord('h'), 1, 'hello')
    manager_cv2.add_keystroke(ord('f'), 1, 'flip')
    manager_cv2.add_keystroke(ord('g'), 1, 'gray')
    manager_cv2.add_keystroke(ord('c'), 1, 'cartoon')

    # Basic for (check `basic.py`)
    for frame in manager_cv2:
        # I want to print only one time hello when someone activates this flag
        if manager_cv2.key_manager.hello:
            print('Hello world')
            manager_cv2.key_manager.hello = False

        # Manage the flip
        if manager_cv2.key_manager.flip:
            frame = cv2.flip(frame,1)

        # Manage if you want to draw the cartoon
        if manager_cv2.key_manager.cartoon:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_blur = cv2.medianBlur(gray, 5)
            edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 5)

            # If it is also gray have in mind
            if manager_cv2.key_manager.gray:
                color = cv2.bilateralFilter(gray, 9, 300, 300)
            else:
                color = cv2.bilateralFilter(frame, 9, 300, 300)

            frame = cv2.bitwise_and(color, color, mask=edges)

        # If it is not a cartoon but it is gray
        elif manager_cv2.key_manager.gray:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Finally show the generated frame
        cv2.imshow("Frame", frame)

    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--video', default=0,
        help='input video/stream (default 0, it is your main webcam)')

    parser.add_argument('-s', '--stream',
        help='if you pass it, it means that the video is an streaming',
        action='store_true')

    parser.add_argument('-f', '--fps', default=0,
        help='int parameter to indicate the limit of FPS (default 0, it means no limit)',
        type=int)

    args = parser.parse_args()

    if type(args.video) is str and args.video.isdigit():
        args.video = int(args.video)

    key_manager(args.video, args.stream, args.fps)
