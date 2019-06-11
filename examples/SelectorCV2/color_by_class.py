from cv2_tools.Selection import SelectorCV2
import cv2
import numpy as np


def simple_selector():
    classes = {
        'dog':(200,0,0),
        'cat':(120,120,90),
        'human':(0,0,250),
        'goat':(55,100,250),
        'lion':(0,250,250),
    }

    class_keys = [*classes] + ['default\nclass']
    height = 700
    width = 700
    count = 0

    frame = np.zeros((height,width,3), np.uint8)

    selector = SelectorCV2(color=(250,250,250), color_by_tag=classes, filled=True)

    for x in [100, 300, 500]:
        for y in [100, 300, 500]:
            selector.add_zone((x,y,x+60,y+60), tags=class_keys[count%len(class_keys)])
            count += 1

    frame = selector.draw(frame)
    cv2.imshow("Black frame", frame)
    cv2.waitKey(0)

if __name__ == '__main__':
    simple_selector()
