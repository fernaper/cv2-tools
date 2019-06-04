import argparse

from cv2_tools.Management import ManagerCV2
from cv2_tools.Selection import SelectorCV2
import cv2


def scenes_detector(video, stream, fps):
    manager_cv2 = ManagerCV2(cv2.VideoCapture(video), is_stream=stream, fps_limit=fps, detect_scenes=True)
    manager_cv2.add_keystroke(27, 1, exit=True)

    count = 0
    for frame in manager_cv2:
        selector = SelectorCV2(color=(200,90,0), filled=True)
        if manager_cv2.new_scene:
            count += 1
        selector.add_free_tags((-10,-10), 'Scene: {}'.format(count))
        frame = selector.draw(frame)
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

    scenes_detector(args.video, args.stream, args.fps)
