from constraint import *
import pprint

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

def get_possible_positions(width, height, all_selected_zones, all_tags_shapes):
    problem = Problem()
    for i, rectangle in enumerate(all_selected_zones):
        tag_width, tag_height = all_tags_shapes[i]
        problem.addVariable('zone_{}'.format(i), [(rectangle[2], rectangle[3] - tag_height, rectangle[2] + tag_width, rectangle[3], 'bottom_right'),
                                                  (rectangle[0] - tag_width, rectangle[3] - tag_height, rectangle[0], rectangle[3], 'bottom_left'),
                                                  (rectangle[0], rectangle[1], rectangle[0]+tag_width, rectangle[1]+tag_height, 'inside'),
                                                  (rectangle[0], rectangle[1] - tag_height, rectangle[0] + tag_width, rectangle[1], 'top')])
        # Only accepts zones inside the frame
        problem.addConstraint(lambda zone: rectangle_collision_rectangle(zone[:-1], (0,0,width, height)), ('zone_{}'.format(i),))
        # Only accpets tags not inside other selections
        problem.addConstraint(lambda zone: not rectangle_collision_list_rectangles(zone[:-1], all_selected_zones), ('zone_{}'.format(i),))

    for i in range(len(all_selected_zones) - 1):
        # Only accepts tags not collisioning with other tags
        problem.addConstraint(lambda zone_1, zone_2:
            not rectangle_collision_rectangle(zone_1[:-1], zone_2[:-1]), ('zone_{}'.format(i), 'zone_{}'.format(i+1))
        )

    best_solution = None
    score = 0
    solutions = problem.getSolutions()
    for solution in solutions:
        current_score = 0
        for key in solution.keys():
            position = solution[key][4]
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
            info_zone = best_solution['zone_{}'.format(i)]
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
    pprint.pprint(get_possible_positions(width, height, all_selected_zones, all_tags_shapes))
