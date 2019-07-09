import argparse

from cv2_tools.Management import ManagerCV2
import cv2


def simple_manager(video, stream, fps):
    # Create a manager passing video input
    # Also I inform if it is an stream or not (it is not completly necessary but
    # in some cases is usefull)
    # Finally I put a limit of FPS (this is more important if it is not an stream,
    # by default it will try to consume the video as fast as possible, and you could
    # want to show it at real time)
    manager_cv2 = ManagerCV2(cv2.VideoCapture(video), is_stream=stream, fps_limit=fps)

    # I decide that I want to exit by pressing `esc` (if you want to see more
    # about this, check the example `keystroke.py`)
    manager_cv2.add_keystroke(27, 1, exit=True)

    # With that simple for you will get your video, frame by frame 52% faster
    # than if you use the typical `while True`
    for frame in manager_cv2:
        cv2.imshow('Example easy manager', frame)

    cv2.destroyAllWindows()

    # You can check easily your frame rate at any time (you don't need to wait
    # unitl the for ends)
    print('FPS: {}'.format(manager_cv2.get_fps()))


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

    simple_manager(args.video, args.stream, args.fps)
