import argparse

from cv2_tools.Management import ManagerCV2
from cv2_tools.Selection import SelectorCV2
import cv2

'''
    Check first ManagerCV2 examples, here I assume that you know how it works.
'''


vertex = []

def mouse_drawing(event, x, y, flags, params):
    global vertex

    if event == cv2.EVENT_LBUTTONDOWN:
        vertex.append((x,y))

    if event == cv2.EVENT_RBUTTONDOWN:
        vertex = []


def simple_selector(video, stream, fps):
    manager_cv2 = ManagerCV2(cv2.VideoCapture(video), is_stream=stream, fps_limit=fps)
    manager_cv2.add_keystroke(27, 1, exit=True)
    manager_cv2.add_keystroke(ord('c'), 1, 'close') # It will manage if we want to close the polygon or not
    manager_cv2.add_keystroke(ord('b'), 1, 'box') # It will add or not the surrounding box

    cv2.namedWindow("Polygon")
    cv2.setMouseCallback("Polygon", mouse_drawing)

    for frame in manager_cv2:
        # The best way to make it works is creating the selection inside the loop
        # You can specify lot of optional parameters like:
        # alpha, color, polygon_color, normalized, thickness, filled, peephole, closed_polygon and show_vertexes
        # Check documentation for more information of each one
        selector = SelectorCV2(
            color=(0,100,220), filled=True, thickness=3,
            closed_polygon=manager_cv2.key_manager.close,
            polygon_color=(170,25,130), show_vertexes=True
        )

        # We add the polygon specifying the vertexes (list of touples of two elements)
        # Also optionaly, we decide to add a surrounding box to the polygon if we press the box key,
        # and for this example we also add a tag, but this is not necessary
        selector.add_polygon(vertex, surrounding_box=manager_cv2.key_manager.box, tags='This is the first\nPolygon')

        # Finally when you execute the draw function it actually prints all the selections
        # until now it didn't print anything, only store the data.
        frame = selector.draw(frame)
        cv2.imshow("Polygon", frame)


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
