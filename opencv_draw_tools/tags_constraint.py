from constraint import *
import cv2

def position_inside_rectangle(position, rectangle):
    return position[0] > rectangle[0] and position[0] < rectangle[2] and \
           position[1] > rectangle[1] and position[1] < rectangle[3]

def rectangle_collision_rectangle(rectangle1, rectangle2):
    return position_inside_rectangle((rectangle1[0],rectangle1[1]),rectangle2) or \
           position_inside_rectangle((rectangle1[0],rectangle1[3]),rectangle2) or \
           position_inside_rectangle((rectangle1[2],rectangle1[1]),rectangle2) or \
           position_inside_rectangle((rectangle1[2],rectangle1[3]),rectangle2)

def rectangle_collision_list_rectangles (rectangle, list_rectangles):
    for r in list_rectangles:
        if rectangle_collision_rectangle(rectangle, r):
            return True
    return False

def is_valid(position, frame_shape, other_selected_zones):
    x1, y1, x2, y2 = position
    width, height = frame_shape
    return x1 >= 0 and x2 > x1 and y1 >= 0 and y2 > y1 and x2 <= width and y2 <= height and \
        not rectangle_collision_list_rectangles(position, other_selected_zones)

def get_possible_positions(width, height, all_selected_zones, all_tags_shapes, margin=5, frame=[]):
    problem = Problem()
    conflict_zones = []
    for i, rectangle in enumerate(all_selected_zones):
        tag_width, tag_height = all_tags_shapes[i]
        sides = [(rectangle[2], rectangle[3] - tag_height - margin, rectangle[2] + tag_width, rectangle[3] - margin*2, 'bottom_right'),
                (rectangle[0] - tag_width, rectangle[3] - tag_height - margin, rectangle[0], rectangle[3] - margin*2, 'bottom_left'),
                (rectangle[0], rectangle[1], rectangle[0] + tag_width, rectangle[1] + tag_height + margin*2, 'inside'),
                (rectangle[0] + margin, rectangle[1] - tag_height - margin, rectangle[0] + tag_width, rectangle[1], 'top')]
        valid_sides = []
        other_selected_zones = all_selected_zones[:i] + all_selected_zones[i+1:]
        for side in sides:
            # Only accepts zones inside the frame with tags not inside other selections
            if is_valid(side[:-1], (width,height), other_selected_zones):
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
                    not rectangle_collision_rectangle(zone_1[:-1], zone_2[:-1]), ('zone_{}'.format(i), 'zone_{}'.format(j))
                )

    best_solution = None
    score = 0
    solutions = problem.getSolutions()
    for solution in solutions:
        current_score = 0
        for key in solution.keys():
            position = solution[key][4]
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
            info_zone = best_solution[zone_name]
            # This is for testing where this method thinks tags will be poisitionated
            if len(frame):
                #print(info_zone)
                cv2.rectangle(frame, (info_zone[0],info_zone[1]),(info_zone[2], info_zone[3]), (0,255,0),0)
            if info_zone[0] >= 0 and info_zone[2] <= width and info_zone[1] >= 0 and info_zone[3] <= height:
                final_ans.append(info_zone[4])
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
