# This test needs face_recognition library
# You can install it with: pip install face_recognition
import face_recognition
import cv2

import opencv_draw_tools as cv2_tools

def face_detector(frame, scale=0.25):
    small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    rgb_small_frame = small_frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_small_frame)
    zones = []
    tags = []
    for i, face_location in enumerate(face_locations):
        y1, x2, y2, x1 = [position/scale for position in face_location]
        zones.append((x1,y1,x2,y2))
        tags.append(['Face {}'.format(i)])
    return cv2_tools.select_multiple_zones(frame, zones, all_tags=tags,
                    color=(14,28,200), filled=True)

def main():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            keystroke = cv2.waitKey(1)
            frame = face_detector(frame, 0.5)
            cv2.imshow('Example face_recognition', frame)
            # True if escape 'esc' is pressed
            if keystroke == 27:
                print('Exit')
                break
    cv2.destroyAllWindows()
    cv2.VideoCapture(0).release()

if __name__ == '__main__':
    main()
