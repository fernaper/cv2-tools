# MIT License
# Copyright (c) 2019 Fernando Perez
import cv2

from cv2_tools.Utils import *


# TODO: Document SelectorCV2
class SelectorCV2():


    def __init__(self, alpha=0.9, color=(110,70,45), normalized=False, thickness=2,
                 filled=False, peephole=True, margin=5, closed_polygon=False):
        self.zones = []
        self.polygon_zones = []
        self.all_tags = []
        # Visual parameters: It is going to be all the default values
        self.alpha = alpha
        self.color = color
        self.normalized = normalized
        self.thickness = thickness
        self.filled = filled
        self.peephole = peephole
        self.margin = margin
        # Polygon
        self.closed_polygon = closed_polygon
        # From index (polygon_zones) -> {
        #   'alpha': alpha,
        #   'color': color,
        #   'filled': filled,
        #   'peephole': peephole,
        # }
        # If someone is set to None or does not exist, this parameter is also set to default
        self.specific_properties = {}


    def set_properties(self, alpha=None, color=None, normalized=None,
                       thickness=None, filled=None, peephole=None,
                       margin=None):
        if alpha is not None:
            self.alpha = alpha
        if color is not None:
            self.color = color
        if normalized is not None:
            self.normalized = normalized
        if thickness is not None:
            self.thickness = thickness
        if filled is not None:
            self.filled = filled
        if peephole is not None:
            self.peephole = peephole
        if margin is not None:
            self.margin = margin


    def add_zone(self, zone, tags=None, specific_properties={}):
        self.zones.append(zone)
        if tags and type(tags) is not list:
            tags = [tags]
        elif not tags:
            tags = []
        self.all_tags.append(tags)

        # Add specific_properties if there are someone
        if specific_properties:
            index = len(self.zones)-1
            self.specific_properties[index] = {}
            for attribute in ['alpha', 'color', 'filled', 'peephole']:
                if attribute in specific_properties:
                    self.specific_properties[index][attribute] = specific_properties[attribute]


    def add_polygon(self, polygon, surrounding_box=False, tags=None):
        if not polygon:
            return

        self.polygon_zones.append(polygon)

        if surrounding_box:
            min_x, min_y, max_x, max_y = polygon[0][0], polygon[0][1], 0, 0
            for position in polygon:
                if position[0] < min_x:
                    min_x = position[0]
                if position[0] > max_x:
                    max_x = position[0]
                if position[1] < min_y:
                    min_y = position[1]
                if position[1] > max_y:
                    max_y = position[1]

            self.zones.append((min_x, min_y, max_x, max_y))

            if tags and type(tags) is not list:
                tags = [tags]
            elif not tags:
                tags = []
            self.all_tags.append(tags)


    def set_range_valid_rectangles(self, origin, destination):
        self.zones = self.zones[origin:destination]
        self.all_tags = self.all_tags[origin:destination]


    def set_valid_rectangles(self, indexes):
        # This if is just for efficiency
        if not indexes:
            self.zones = []
            self.all_tags = []
            return

        for i in range(len(self.zones)):
            if i not in indexes:
                self.zones.pop(i)
                self.all_tags.pop(i)


    def draw(self, frame, fx=1, fy=1, interpolation=cv2.INTER_LINEAR):
        next_frame = select_multiple_zones(
            frame.copy(),
            self.zones,
            all_tags=self.all_tags,
            alpha=self.alpha,
            color=self.color,
            normalized=self.normalized,
            thickness=self.thickness,
            filled=self.filled,
            peephole=self.peephole,
            margin=self.margin,
            specific_properties=self.specific_properties)

        next_frame = select_polygon(
            next_frame,
            all_vertexes=self.polygon_zones,
            color=self.color,
            thickness=self.thickness,
            closed=self.closed_polygon
        )

        return cv2.resize(next_frame, (0,0), fx=fx, fy=fy, interpolation=interpolation)
