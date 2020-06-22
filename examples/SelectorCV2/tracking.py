import argparse

from cv2_tools.Management import ManagerCV2
from cv2_tools.Selection import SelectorCV2
import cv2

'''
    Check first ManagerCV2 examples, here I assume that you know how it works.
'''


def manage_keys(manager_cv2, selection):
    x1,y1,x2,y2 = selection
    if manager_cv2.key_manager.grow:
        x2 += 0.1
        y2 += 0.1
        manager_cv2.key_manager.grow = False

    if manager_cv2.key_manager.shrink:
        x2 = max(x1,x2-0.1)
        y2 = max(y1, y2-0.1)
        manager_cv2.key_manager.shrink = False

    if manager_cv2.key_manager.up:
        y1 -= 0.1
        y2 -= 0.1
        manager_cv2.key_manager.up = False

    if manager_cv2.key_manager.left:
        x1 -= 0.1
        x2 -= 0.1
        manager_cv2.key_manager.left = False

    if manager_cv2.key_manager.down:
        y1 += 0.1
        y2 += 0.1
        manager_cv2.key_manager.down = False

    if manager_cv2.key_manager.right:
        x1 += 0.1
        x2 += 0.1
        manager_cv2.key_manager.right = False

    return (x1,y1,x2,y2)


def simple_selector(video, stream, fps):
    manager_cv2 = ManagerCV2(cv2.VideoCapture(video), is_stream=stream, fps_limit=fps)
    manager_cv2.add_keystroke(27, 1, exit=True)
    manager_cv2.add_keystroke(ord('+'), 1, 'grow')
    manager_cv2.add_keystroke(ord('-'), 1, 'shrink')
    manager_cv2.add_keystroke(ord('w'), 1, 'up')
    manager_cv2.add_keystroke(ord('a'), 1, 'left')
    manager_cv2.add_keystroke(ord('s'), 1, 'down')
    manager_cv2.add_keystroke(ord('d'), 1, 'right')
    manager_cv2.add_keystroke(ord(' '), 1, 'track')

    # Im preparing a selection with the coordinates (x1,y1,x2,y2):
    #   x1,y1 -------- x2,y1
    #    |               |
    #   x1,y2 -------- x2,y2
    selection = (0.1,0.1,0.3,0.3)
    tracking = False

    for frame in manager_cv2:
        '''
            For this example controles are:
                - `+` to grow up selection
                - `-` to shrink down selection
                - `w`, `a`, `s`, `d` to move the selection
        '''
        selection = manage_keys(manager_cv2, selection)

        selector = SelectorCV2(color=(0,0,200), filled=True, normalized=True)
        selector.add_zone(selection)

        if manager_cv2.key_manager.track:
            if not tracking:
                manager_cv2.set_tracking(selector, frame)
            else:
                selector = manager_cv2.get_tracking(frame)
                selection = selector.zones[0]
            tracking = True
        else:
            tracking = False

        # Finally when you execute the draw function it actually prints all the selections
        # until now it didn't print anything, only store the data.
        frame = selector.draw(frame)
        cv2.imshow("Frame", frame)

    print(manager_cv2.get_fps())

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

    simple_selector(args.video, args.stream, args.fps)
