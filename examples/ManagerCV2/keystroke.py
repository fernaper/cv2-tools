import argparse

from cv2_tools.Management import ManagerCV2
import cv2


def key_manager(video, stream, fps):
    manager_cv2 = ManagerCV2(cv2.VideoCapture(video), is_stream=stream, fps_limit=fps)
    manager_cv2.add_keystroke(27, 1, exit=True)
    manager_cv2.add_keystroke(ord('f'), 1, 'flip')
    manager_cv2.add_keystroke(ord('g'), 1, 'gray')
    manager_cv2.add_keystroke(ord('c'), 1, 'cartoon')

    # With that simple for you will get your video, frame by frame 52% faster
    # than if you use the typical `while True`
    for frame in manager_cv2:
        if manager_cv2.key_manager.flip:
            frame = cv2.flip(frame,1)

        if manager_cv2.key_manager.cartoon:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 5)
            color = cv2.bilateralFilter(frame, 9, 300, 300)
            frame = cv2.bitwise_and(color, color, mask=edges)

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
