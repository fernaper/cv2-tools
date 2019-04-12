# This test needs face_recognition library
# You can install it with: pip install face_recognition
import face_recognition
import cv2

try:
    # If we use this import we are testing the github version
    import opencv_draw_tools.SelectZone as cv2_tools
    print('Testing mode')
except:
    import opencv_draw_tools as cv2_tools

def face_detector(frame, scale=0.25):
    small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    rgb_small_frame = small_frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_small_frame)

    selector = cv2_tools.SelectorCV2(color=(200,90,0), filled=True)
    for i, face_location in enumerate(face_locations):
        y1, x2, y2, x1 = [position/scale for position in face_location]
        selector.add_zone((x1,y1,x2,y2),'Face {}'.format(i))

    face_landmarks_list = face_recognition.face_landmarks(frame)
    for face_landmarks in face_landmarks_list:
        for facial_feature in face_landmarks:
            selector.add_polygon(face_landmarks[facial_feature])

    return selector.draw(frame)


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
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
