import numpy as np
import cv2

def get_lighter_color(color):
    add = 255 - max(color)
    add = min(add,30)
    return (color[0] + add, color[1] + add, color[2] + add)

def add_tags(frame, position, tags, tag_position=None, alpha=0.75, color=(20, 20, 20), inside=False, margin=5, font_info=(cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (255,255,255), 1)):
    f_height, f_width = frame.shape[:2]
    font, font_scale, font_color, thickness = font_info
    x1, y1, x2, y2 = position

    text_width = -1
    text_height = -1
    line_height = -1
    for tag in tags:
        size = cv2.getTextSize(tag, font, font_scale, thickness)
        text_width = max(text_width,size[0][0])
        text_height = max(text_height, size[0][1])
        line_height = max(line_height, text_height + size[1] + margin)

    '''
        If not tags position are provided:
            - First try to put the text on the Bottom Rigth corner
            - If it doesn't fit, try to put the text on the Bottom Left corner
            - If it doesn't fit, try to put the text Inside the rectangle
            - If it doesn't fit, try to put the text On top of the rectangle
    '''
    if not tag_position:
        fits_right = x2 + text_width + margin*3 <= f_width
        fits_left = x1 - (text_width + margin*3) >= 0
        fits_below = (text_height + margin)*len(tags) - margin <= y2 - thickness
        fits_inside = x1 + text_width + margin*3 <= x2 - thickness and y1 + (margin*2 + text_height)*len(tags) + text_height - margin <= y2 - thickness

        if fits_right and fits_below:
            tag_position = 'bottom_right'
        elif fits_left and fits_below:
            tag_position = 'bottom_left'
        elif fits_inside:
            tag_position = 'inside'
        else:
            tag_position = 'top'
    else:
        valid = ['bottom_right', 'bottom_left', 'inside', 'top']
        if tag_position not in ['bottom_right', 'bottom_left', 'inside', 'top']:
            raise ValueError('Error, invalid tag_position ({}) must be in: {}'.format(tag_position, valid))

    overlay = frame.copy()
    for i, tag in enumerate(tags):
        reverse_i = len(tags) - i
        if tag_position == 'top':
            cv2.rectangle(overlay, (x1 + margin, y1 - (margin*2 + text_height)*reverse_i - text_height - margin), (x1 + text_width + margin*3, y1 - (margin*2 + text_height)*reverse_i + text_height - margin), color,-1)
        elif tag_position == 'inside':
            cv2.rectangle(overlay, (x1 + margin, y1 + (margin*2 + text_height)*(i+1) - text_height - margin), (x1 + text_width + margin*3, y1 + (margin*2 + text_height)*(i+1) + text_height - margin), color,-1)
        elif tag_position == 'bottom_left':
            cv2.rectangle(overlay, (x1 - (text_width + margin*3), y2 - (margin*2 + text_height)*reverse_i - text_height - margin), (x1 - margin, y2 - (margin*2 + text_height)*reverse_i + text_height - margin), color,-1)
        elif tag_position == 'bottom_right':
            cv2.rectangle(overlay, (x2 + margin, y2 - (margin*2 + text_height)*reverse_i - text_height - margin), (x2 + text_width + margin*3, y2 - (margin*2 + text_height)*reverse_i + text_height - margin), color,-1)
        y1 += margin
        y2 += margin
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    x1, y1, x2, y2 = position
    for i, tag in enumerate(tags):
        reverse_i = len(tags) - i
        if tag_position == 'top':
            cv2.putText(frame, tag, (x1 + margin*2, y1 - (margin*2 + text_height)*reverse_i), font, font_scale, font_color, thickness)
        elif tag_position == 'inside':
            cv2.putText(frame, tag, (x1 + margin*2, y1 + (margin*2 + text_height)*(i+1)), font, font_scale, font_color, thickness)
        elif tag_position == 'bottom_left':
            cv2.putText(frame, tag, (x1 - (text_width + margin*2), y2 - (margin*2 + text_height)*reverse_i), font, font_scale, font_color, thickness)
        elif tag_position == 'bottom_right':
            cv2.putText(frame, tag, (x2 + margin*2, y2 - (margin*2 + text_height)*reverse_i), font, font_scale, font_color, thickness)
        y1 += margin
        y2 += margin

    return frame

def add_peephole(frame, position, alpha=0.5, color=(110,70,45), thickness=2, line_length = 7):
    x1, y1, x2, y2 = position
    # Min value of thickness = 2
    thickness = min(thickness,2)
    # If the selected zone is too small don't draw
    if x2 - x1 > thickness*2 + line_length  and y2 - y1 > thickness*2 + line_length:
        overlay = frame.copy()
        # Draw horizontal lines of the corners
        cv2.line(overlay,(x1, y1),(x1 + line_length, y1), color, thickness+1)
        cv2.line(overlay,(x2, y1),(x2 - line_length, y1), color, thickness+1)
        cv2.line(overlay,(x1, y2),(x1 + line_length, y2), color, thickness+1)
        cv2.line(overlay,(x2, y2),(x2 - line_length, y2), color, thickness+1)
        # Draw vertical lines of the corners
        cv2.line(overlay,(x1, y1),(x1, y1 + line_length), color, thickness+1)
        cv2.line(overlay,(x1, y2),(x1, y2 - line_length), color, thickness+1)
        cv2.line(overlay,(x2, y1),(x2, y1 + line_length), color, thickness+1)
        cv2.line(overlay,(x2, y2),(x2, y2 - line_length), color, thickness+1)
        # Added extra lines that gives the peephole effect
        cv2.line(overlay,(x1, int((y1 + y2) / 2)),(x1 + line_length, int((y1 + y2) / 2)), color, thickness-1)
        cv2.line(overlay,(x2, int((y1 + y2) / 2)),(x2 - line_length, int((y1 + y2) / 2)), color, thickness-1)
        cv2.line(overlay,(int((x1 + x2) / 2), y1),(int((x1 + x2) / 2), y1 + line_length), color, thickness-1)
        cv2.line(overlay,(int((x1 + x2) / 2), y2),(int((x1 + x2) / 2), y2 - line_length), color, thickness-1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    return frame

def select_zone(frame, position, tags, tag_position=None, alpha=0.9, color=(110,70,45), normalized=False, thickness=2, peephole=True):
    f_height, f_width = frame.shape[:2]
    x1, y1, x2, y2 = position
    if normalized:
        x1 *= f_width
        x2 *= f_width
        y1 *= f_height
        y2 *= f_height
    # Auto adjust the limits of the selected zone
    x2 = int(min(max(x2, thickness*2), f_width - thickness))
    y2 = int(min(max(y2, thickness*2), f_height - thickness))
    x1 = int(min(max(x1, thickness), x2 - thickness))
    y1 = int(min(max(y1, thickness), y2 - thickness))
    position = (x1, y1, x2, y2)

    if peephole:
        frame = add_peephole(frame, position, alpha=alpha, color=color)
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color,2)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    frame = add_tags(frame, position, tags, tag_position=tag_position)
    return frame

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    f_width = cap.get(3)
    f_height = cap.get(4)
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        if ret:
            keystroke = cv2.waitKey(1)
            frame = select_zone(frame, (0.33,0.2,0.66,0.8), ['Programmer', 'Example', 'Core'], color=(130,58,14), normalized=True)
            cv2.imshow("Webcam", frame)
            # True if escape 'esc' is pressed
            if keystroke == 27:
                break
    cv2.destroyAllWindows()
    cv2.VideoCapture(0).release()
