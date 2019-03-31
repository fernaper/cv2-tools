from constraint import *
import cv2

class Rectangle():

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def __str__(self):
        return 'Rect(x1:{},y1:{},x2:{},y2:{})'.format(self.x1, self.y1, self.x2, self.y2)

    def __repr__(self):
        return 'Rectangle(x1:{},y1:{},x2:{},y2:{})'.format(self.x1, self.y1, self.x2, self.y2)

def position_inside_rectangle(x, y, rectangle):
    return x >= rectangle.x1 and x <= rectangle.x2 and \
           y >= rectangle.y1 and y <= rectangle.y2

def rectangle_collision_rectangle(rectangle1, rectangle2):
    if position_inside_rectangle(rectangle1.x1, rectangle1.y1, rectangle2) or \
       position_inside_rectangle(rectangle1.x2, rectangle1.y1, rectangle2) or \
       position_inside_rectangle(rectangle1.x1, rectangle1.y2, rectangle2) or \
       position_inside_rectangle(rectangle1.x2, rectangle1.y2, rectangle2):
        return True
    if position_inside_rectangle(rectangle2.x1, rectangle2.y1, rectangle1) or \
       position_inside_rectangle(rectangle2.x2, rectangle2.y1, rectangle1) or \
       position_inside_rectangle(rectangle2.x1, rectangle2.y2, rectangle1) or \
       position_inside_rectangle(rectangle2.x2, rectangle2.y2, rectangle1):
        return True
    if rectangle1.x1 <= rectangle2.x1 and rectangle1.y1 >= rectangle2.y1 and \
       rectangle1.x2 >= rectangle2.x2 and rectangle1.y2 <= rectangle2.y2:
        return True
    if rectangle2.x1 <= rectangle1.x1 and rectangle2.y1 >= rectangle1.y1 and \
       rectangle2.x2 >= rectangle1.x2 and rectangle2.y2 <= rectangle1.y2:
        return True
    return False

def rectangle_collision_list_rectangles (rectangle, list_rectangles):
    for r in list_rectangles:
        if rectangle_collision_rectangle(rectangle, r):
            return True
    return False

def is_valid(position, frame_shape, other_selected_zones):
    width, height = frame_shape
    return position.x1 >= 0 and position.x2 > position.x1 and position.y1 >= 0 and \
        position.y2 > position.y1 and position.x2 <= width and position.y2 <= height and \
        not rectangle_collision_list_rectangles(position, other_selected_zones)

def get_possible_positions(width, height, all_selected_zones, all_tags_shapes, margin=5, frame=[]):
    problem = Problem()
    conflict_zones = []
    for i, rectangle in enumerate(all_selected_zones):
        tag_width, tag_height = all_tags_shapes[i]
        bottom_right = Rectangle(rectangle.x2, rectangle.y2 - tag_height - margin, rectangle.x2 + tag_width, rectangle.y2 - margin*2)
        bottom_left  = Rectangle(rectangle.x1 - tag_width, rectangle.y2 - tag_height - margin, rectangle.x1, rectangle.y2 - margin*2)
        inside       = Rectangle(rectangle.x1, rectangle.y1, rectangle.x1 + tag_width, rectangle.y1 + tag_height + margin*2)
        top          = Rectangle(rectangle.x1 + margin, rectangle.y1 - tag_height - margin, rectangle.x1 + tag_width, rectangle.y1)

        sides = [(bottom_right, 'bottom_right'),
                (bottom_left, 'bottom_left'),
                (inside, 'inside'),
                (top, 'top')]
        valid_sides = []
        other_selected_zones = all_selected_zones[:i] + all_selected_zones[i+1:]
        for side in sides:
            # Only accepts zones inside the frame with tags not inside other selections
            if is_valid(side[0], (width,height), other_selected_zones):
                valid_sides.append(side)
        if valid_sides:
            problem.addVariable('zone_{}'.format(i), valid_sides)
        else:
            conflict_zones.append(i)

    for i in range(len(all_selected_zones)):
        if i in conflict_zones:
            continue
        # Only accepts tags not collisioning with other tags
        for j in range(i+1,len(all_selected_zones)):
            if j not in conflict_zones:
                problem.addConstraint(lambda zone_1, zone_2:
                    not rectangle_collision_rectangle(zone_1[0], zone_2[0]), ('zone_{}'.format(i), 'zone_{}'.format(j))
                )

    best_solution = None
    score = 0
    solutions = problem.getSolutions()
    for solution in solutions:
        current_score = 0
        for key in solution.keys():
            position = solution[key][1]
            info_zone = solution[key]
            if position == 'bottom_right':
                current_score += 4
            elif position == 'bottom_left':
                current_score += 3
            elif position == 'inside':
                current_score += 2
            else:
                current_score += 1
        if current_score > score:
            score = current_score
            best_solution = solution

    final_ans = []
    if best_solution:
        for i in range(len(all_selected_zones)):
            zone_name = 'zone_{}'.format(i)
            if zone_name not in best_solution:
                final_ans.append(None)
                continue
            info_zone, position_name = best_solution[zone_name]
            # This is for testing where this method thinks tags will be poisitionated
            if len(frame):
                cv2.rectangle(frame, (info_zone.x1,info_zone.y1),(info_zone.x2, info_zone.y2), (0,255,0),0)
            if info_zone.x1 >= 0 and info_zone.x2 <= width and info_zone.y1 >= 0 and info_zone.y2 <= height:
                final_ans.append(position_name)
            else:
                # If there is not a really good solution, just lets the method add_tags decide the position
                final_ans.append(None)
    return final_ans

if __name__ == '__main__':
    width = 1280
    height = 720
    all_selected_zones = [(100,100,200,300), (220,100,400,300)]
    all_tags_shapes = [(70,80), (70,80)]
    print(get_possible_positions(width, height, all_selected_zones, all_tags_shapes))
