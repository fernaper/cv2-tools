import numpy as np
import cv2

def get_lighter_color(color):
    add = 255 - max(color)
    add = min(add,30)
    return (color[0] + add, color[1] + add, color[2] + add)

def add_tags(frame, size, position, tags, alpha=0.75, color=(20, 20, 20), inside=False, margin=5, font_info=(cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (255,255,255), 1)):
    f_width, f_height = size
    font, font_scale, font_color, thickness = font_info

    x1, y1, _, _ = position

    text_width = -1
    text_height = -1
    line_height = -1
    for tag in tags:
        size = cv2.getTextSize(tag, font, font_scale, thickness)
        text_width = max(text_width,size[0][0])
        text_height = max(text_height, size[0][1])
        line_height = max(line_height, text_height + size[1] + margin)

    # If we dont have enought space or we want to put the text inside
    inside = inside or y1 - (margin*2 + text_height)*len(tags) - text_height - margin <= 0
    overlay = frame.copy()
    text_overlay = frame.copy()

    for i, tag in enumerate(tags):
        reverse_i = len(tags) - i
        if inside:
            cv2.rectangle(overlay, (x1 + margin, y1 + (margin*2 + text_height)*(i+1) - text_height - margin), (x1 + text_width + margin*3, y1 + (margin*2 + text_height)*(i+1) + text_height - margin), color,-1)
            cv2.putText(text_overlay, tag, (x1 + margin*2, y1 + (margin*2 + text_height)*(i+1)), font, font_scale, font_color, thickness)
        else:
            cv2.rectangle(overlay, (x1 + margin, y1 - (margin*2 + text_height)*reverse_i - text_height - margin), (x1 + text_width + margin*3, y1 - (margin*2 + text_height)*reverse_i + text_height - margin), color,-1)
            cv2.putText(text_overlay, tag, (x1 + margin*2, y1 - (margin*2 + text_height)*reverse_i), font, font_scale, font_color, thickness)
        y1 += margin
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.addWeighted(text_overlay, alpha, frame, 1, 0, frame)

    return frame

def add_peephole(frame, position, alpha=0.95, color=(110,70,45), thickness=2, line_length = 7):
    x1, y1, x2, y2 = position

    thickness = min(thickness,2)

    cv2.line(frame,(x1, y1),(x1 + line_length, y1), color, thickness+1)
    cv2.line(frame,(x2, y1),(x2 - line_length, y1), color, thickness+1)
    cv2.line(frame,(x1, y2),(x1 + line_length, y2), color, thickness+1)
    cv2.line(frame,(x2, y2),(x2 - line_length, y2), color, thickness+1)

    cv2.line(frame,(x1, y1),(x1, y1 + line_length), color, thickness+1)
    cv2.line(frame,(x1, y2),(x1, y2 - line_length), color, thickness+1)
    cv2.line(frame,(x2, y1),(x2, y1 + line_length), color, thickness+1)
    cv2.line(frame,(x2, y2),(x2, y2 - line_length), color, thickness+1)

    cv2.line(frame,(x1, int((y1 + y2) / 2)),(x1 + line_length, int((y1 + y2) / 2)), color, thickness-1)
    cv2.line(frame,(x2, int((y1 + y2) / 2)),(x2 - line_length, int((y1 + y2) / 2)), color, thickness-1)
    cv2.line(frame,(int((x1 + x2) / 2), y1),(int((x1 + x2) / 2), y1 + line_length), color, thickness-1)
    cv2.line(frame,(int((x1 + x2) / 2), y2),(int((x1 + x2) / 2), y2 - line_length), color, thickness-1)

    return frame

def select_zone(frame, size, position, tags, alpha=0.9, color=(110,70,45), thickness=2, peephole=True):
    f_width, f_height = size
    x1, y1, x2, y2 = position
    line_length = 10

    overlay = frame.copy()
    if peephole:
        overlay = add_peephole(frame, position, alpha=alpha, color=color)
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color,2)

    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    frame = add_tags(frame, size, position, tags)
    return frame

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    f_width = cap.get(3)
    f_height = cap.get(4)
    while True:
        ret, frame = cap.read()
        if ret:
            keystroke = cv2.waitKey(1)
            frame = select_zone(frame, (f_width, f_height), (225,100,425,400), ['Fer', 'Hombre', 'Joven'], color=(130,58,14))
            cv2.imshow("Webcam", frame)
            # True if escape 'esc' is pressed
            if keystroke == 27:
                break
    cv2.destroyAllWindows()
    cv2.VideoCapture(0).release()
