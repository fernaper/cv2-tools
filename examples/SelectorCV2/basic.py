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
        x2 += 10
        y2 += 10
        manager_cv2.key_manager.grow = False

    if manager_cv2.key_manager.shrink:
        x2 = max(x1,x2-10)
        y2 = max(y1, y2-10)
        manager_cv2.key_manager.shrink = False

    if manager_cv2.key_manager.up:
        y1 -= 10
        y2 -= 10
        manager_cv2.key_manager.up = False

    if manager_cv2.key_manager.left:
        x1 -= 10
        x2 -= 10
        manager_cv2.key_manager.left = False

    if manager_cv2.key_manager.down:
        y1 += 10
        y2 += 10
        manager_cv2.key_manager.down = False

    if manager_cv2.key_manager.right:
        x1 += 10
        x2 += 10
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

    # Im preparing a selection with the coordinates (x1,y1,x2,y2):
    #   x1,y1 -------- x2,y1
    #    |               |
    #   x1,y2 -------- x2,y2
    selection = (10,10,60,60)

    for frame in manager_cv2:
        '''
            For this example controles are:
                - `+` to grow up selection
                - `-` to shrink down selection
                - `w`, `a`, `s`, `d` to move the selection
        '''
        selection = manage_keys(manager_cv2, selection)

        # The best way to make it works is creating the selection inside the loop
        # You can specify lot of optional parameters like:
        # alpha, color, polygon_color, normalized, thickness, filled, peephole, closed_polygon and show_vertexes
        # Check documentation for more information of each one
        selector = SelectorCV2(color=(0,0,200), filled=True)

        # You can add multiple zones to a selector
        # Each zone must receive a `selection`, it also could receive `tags` (it could be
        # a string or a list of strings)
        # There is another optional parameter `specific_properties`
        # This is a dictionary. The keys are the name of the attributes that you want
        # to modify from the original selector (so if you want to draw with the same selector
        # two selections in a different way, you can do it), ofcourse the value is
        # the specific value that you want for this parameter
        selector.add_zone(selection, tags=['Some tags', 'With\ngroups'])

        # Finally when you execute the draw function it actually prints all the selections
        # until now it didn't print anything, only store the data.
        frame = selector.draw(frame)
        cv2.imshow("Frame", frame)

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
