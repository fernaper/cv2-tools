# This test needs face_recognition library
# You can install it with: pip install face_recognition
import argparse

import face_recognition
import cv2

from cv2_tools.Management import ManagerCV2
from cv2_tools.Selection import SelectorCV2
from cv2_tools.Storage import StorageCV2

def face_detector(frame, scale, details):
    # Step 1: Prepare the frame for the facial recognition library
    rgb_small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)[:, :, ::-1]

    # Step 2: Create a selector
    selector = SelectorCV2(color=(200,90,0), filled=True, show_vertexes=True)

    # Step 3: Get face locations and for each one add zone with tag
    face_locations = face_recognition.face_locations(rgb_small_frame)

    if not face_locations:
        selector.add_free_tags((-10,-10), 'Faces not detected')
        return selector

    for i, face_location in enumerate(face_locations):
        # I rescale the output, so it will be correctly drawn on our original frame
        y1, x2, y2, x1 = [position/scale for position in face_location]
        selector.add_zone((x1,y1,x2,y2), 'Face {}'.format(i))

    # Step 4: Get face landmarks and for each one add polygon
    if details:
        face_landmarks_list = face_recognition.face_landmarks(frame)
        for face_landmarks in face_landmarks_list:
            for facial_feature in face_landmarks:
                #box = facial_feature in ['chin', 'left_eyebrow', 'right_eyebrow']
                selector.add_polygon(face_landmarks[facial_feature], surrounding_box=False, tags=facial_feature)

    return selector


def detection(video, stream, fps, scale, details):
    manager_cv2 = ManagerCV2(cv2.VideoCapture(video), is_stream=stream, fps_limit=fps)
    manager_cv2.add_keystroke(27, 1, exit=True)
    manager_cv2.add_keystroke(ord('d'), 1, 'detect')
    manager_cv2.key_manager.detect = True # I want to start detecting
    selector = None
    frames_tracking = 0

    for frame in manager_cv2:
        if manager_cv2.key_manager.detect:
            # I'm using the frame counter from the manager
            # So I will recalculate de detection each 20 frames
            # The other ones, I will continue using the same selector (so it will not change)
            #   NOTE: It is == 1 (and not == 0) because in the first iteration we
            #    get the first frame, so count_frames = 1.
            #    This is how I manage to ensure that in the first loop it is True
            #    so selector exist and doesn't raise an error.
            if manager_cv2.count_frames % 20 == 1:
                new_selector = face_detector(frame, scale, details)
                if not selector or frames_tracking >= 30 or len(new_selector.zones) >= len(selector.zones):
                    selector = new_selector
                    frames_tracking = 0
                manager_cv2.set_tracking(selector, frame)
            else:
                # The other frames I wil get the tracking of the last detections
                selector = manager_cv2.get_tracking(frame)
                frames_tracking += 1
            frame = selector.draw(frame)

        cv2.imshow('Face detection example', frame)

    print('FPS: {}'.format(manager_cv2.get_fps()))
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--video', default=0,
        help='input video/stream (default 0, it is your main webcam)')

    parser.add_argument('-s', '--stream',
        help='if you pass it, it means that the video is an streaming',
        action='store_true')

    parser.add_argument('-d', '--details',
        help='if you pass it, it means that you want to see the facial vertexes',
        action='store_true')

    parser.add_argument('--scale', type=float, default=1,
        help='optional parameter to resize the input to the face_recognition library')

    parser.add_argument('-f', '--fps', default=0,
        help='int parameter to indicate the limit of FPS (default 0, it means no limit)',
        type=int)

    args = parser.parse_args()

    if type(args.video) is str and args.video.isdigit():
        args.video = int(args.video)

    detection(args.video, args.stream, args.fps, args.scale, args.details)
