# MIT License
# Copyright (c) 2019 Fernando Perez
import cv2

from cv2_tools.Utils import *


class SelectorCV2():
    """ SelectorCV2 helps to select information in frames.

    This is the original idea of the library, being capable to select multiple
    zones with enough intelligence to decide how to show as much information as
    possible without covering relevant data.

    It has two important functionalities:
     - add_zone: To draw a rectangle (with tags)
     - add_polygon: To draw a polygon (if you add a zone to it, you can also add tags,
     in next versions, we will be capable to add tags without a zone).
    """


    def __init__(self, alpha=0.9, color=(110,70,45), polygon_color=(110,45,93), color_by_tag={}, normalized=False,
                 thickness=2, filled=False, peephole=True, margin=5, closed_polygon=False,
                 show_vertexes=False):
        """  SelectorCV2 constructor.

        Keyword arguments:
        alpha -- transparency of the selected zone on the image (default 0.9)
                 1 means totally visible and 0 totally invisible
        color -- color of the selected zones, touple with 3 elements BGR (default (110,70,45) -> dark blue)
                 BGR = Blue - Green - Red
        polygon_color -- color of the polygons, same structure as color
        color_by_tag -- dict from string to color (BGR). The string is the first tag of a selection.
                        So, if you want to draw a class with a color, you can easily do it. (default {})
        normalized -- boolean parameter, if True, position provided normalized (between 0 and 1)
                      else you should provide concrete values (default False)
        thickness -- thickness of the drawing in pixels (default 2)
        filled -- boolean parameter, if True, it will draw a filled rectangle with one-third opacity compared to the rectangle (default False)
        peephole -- boolean parameter, if True, it also draws additional effects, so it looks like a peephole
        margin -- extra margin in pixels to be separeted with the selected zone (default 5)
        closed_polygon -- boolean parameter, if True, when you pass a polygon, it will draw the polygon closing it (default False)
        show_vertexes -- boolean parameter, if True, when you pass a polygon, it will draw small circles on each vertex (default False)
        """

        self.zones = []
        self.polygon_zones = []
        self.all_tags = []
        self.free_tags = []
        # Visual parameters: It is going to be all the default values
        self.alpha = alpha
        self.color = color
        self.polygon_color = polygon_color
        self.color_by_tag = color_by_tag
        self.normalized = normalized
        self.thickness = thickness
        self.filled = filled
        self.peephole = peephole
        self.margin = margin
        self.show_vertexes = show_vertexes
        # Polygon
        self.closed_polygon = closed_polygon
        # From index (polygon_zones) -> {
        #   'alpha': alpha,
        #   'color': color,
        #   'filled': filled,
        #   'peephole': peephole,
        # }
        self.specific_properties = {}


    def set_properties(self, alpha=None, color=None, polygon_color=None, color_by_tag=None,
                       normalized=None, thickness=None, filled=None, peephole=None,
                       margin=None, closed_polygon=None, show_vertexes=None):
        """  Set default properties.

        Note: All parameters are setted to None, but this is because, this method
        doesn't change an attribute if the parameter is None. So if you want to change
        only one attribute, you don't need to pass the other ones.

        Keyword arguments:
        alpha -- transparency of the selected zone on the image (default None)
                 1 means totally visible and 0 totally invisible
        color -- color of the selected zones, touple with 3 elements BGR (default None)
                 BGR = Blue - Green - Red
        polygon_color -- color of the polygons, same structure as color
        color_by_tag -- dict from string to color (BGR). The string is the first tag of a selection.
                        So, if you want to draw a class with a color, you can easily do it. (default {})
        normalized -- boolean parameter, if True, position provided normalized (between 0 and 1) (default None)
                      else you should provide concrete values (default None)
        thickness -- thickness of the drawing in pixels (default None)
        filled -- boolean parameter, if True, it will draw a filled rectangle with one-third opacity compared to the rectangle (default None)
        peephole -- boolean parameter, if True, it also draws additional effects, so it looks like a peephole (default None)
        margin -- extra margin in pixels to be separeted with the selected zone (default None)
        closed_polygon -- boolean parameter, if True, when you pass a polygon, it will draw the polygon closing it (default None)
        """
        if alpha is not None:
            self.alpha = alpha
        if color is not None:
            self.color = color
        if polygon_color is not None:
            self.polygon_color = polygon_color
        if color_by_tag is not None:
            self.color_by_tag = color_by_tag
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
        if closed_polygon is not None:
            self.closed_polygon = closed_polygon
        if show_vertexes is not None:
            self.show_vertexes = show_vertexes


    def add_zone(self, zone, tags=None, specific_properties={}):
        """  Add a new zone.

        Arguments:
        zone -- tuple with 4 elements (x1, y1, x2, y2)
                This elements should be between 0 and 1 in case it is normalized
                or between 0 and frame height/width (it value not in the margins,
                it will show a warning, unless you set the variable IGNORE_ERRORS
                to True in Utils.py).

        Keyword arguments:
        tags -- Tags to attach to the selection (default None)
        specific_properties -- Optional parameter. If you want to change specifically
                how to draw the current zone, you can pass a dictionary with all the
                attributes you want to change (from the previously setted as default).

                specific_properties should follow the next structure (ignoring as much
                keys as you want):
                {
                    'alpha': value,   (transparency of the selected zone on the image)
                    'color': value,   (color of the selected zones, touple with 3 elements BGR)
                    'filled': value,  (boolean parameter, if True, it will draw a filled rectangle with one-third opacity compared to the rectangle)
                    'peephole': value, (boolean parameter, if True, it also draws additional effects, so it looks like a peephole)
                    'thickness': value (int parameter, you can specify the thickness of the selection)
                }
                Note: You can't specify some attributes as: normalized or closed_polygon (we are considering add some of them)
        """
        if not self.normalized:
            zone = [int(x) for x in zone]
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
            for attribute in ['alpha', 'color', 'filled', 'peephole', 'thickness']:
                if attribute in specific_properties:
                    self.specific_properties[index][attribute] = specific_properties[attribute]


    def add_polygon(self, polygon, surrounding_box=False, tags=None):
        """  Add a new polygon.

        Arguments:
        polygon -- list of points. Each point is a touple (x1, y1)
                This elements should be between 0 and 1 in case it is normalized
                or between 0 and frame height/width (if value not in the margins,
                and variable IGNORE_ERRORS in Utils.py was set to False, it will
                show a warning.

        Keyword arguments:
        surrounding_box -- boolean parameter. If it is True, it will draw a
                rectangle around the polygon
        tags -- Tags to attach to the selection. (default None)
        """
        if not polygon:
            return

        self.polygon_zones.append(polygon)

        # If we don't have any tags and we don't want to add a surrounding box
        # just skip all of this stuff (this will do our system faster)
        if tags or surrounding_box:
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

            # We specify not to show the surrounding box
            if not surrounding_box:
                index = len(self.zones)-1
                self.specific_properties[index] = {
                    'thickness':0
                }


    def add_free_tags(self, coordinates, tags, alpha=0.75, color=(20,20,20),
                      font=cv2.FONT_HERSHEY_COMPLEX_SMALL, font_scale=0.75,
                      font_color=(255,255,255), thickness=1, **kwargs):
        """  Add tags not asociated with selections.

        Arguments:
        coordinates -- touple of two ints (x1,y1).
        tags -- string or list of strings with all the tags to write.
                It supports \n character.

        Keyword Arguments:
        alpha -- transparency of the tags background on the image (default 0.75)
                 1 means totally visible and 0 totally invisible
        color -- color of the tags background, touple with 3 elements BGR (default (20,20,20) -> almost black)
                 BGR = Blue - Green - Red
        font -- opencv font (default cv2.FONT_HARSHEY_COMPLEX_SMALL)
        font_scale -- scale of the fontm between 0 and 1 (default 0.75)
        font_color -- color of the tags text, touple with 3 elements BGR (default (255,255,255) -> white)
                      BGR = Blue - Green - Red
        thickness -- thickness of the text in pixels (default 1)
        kwargs -- We have added this field to avoid compatibility errors with previous
                  and future versions, but it is not really used,
                  we use it to ignore extra fields
        """
        font_info = (font, font_scale, font_color, thickness)
        if type(tags) == str:
            tags = [tags]
        self.free_tags.append({
            'coordinates':coordinates,
            'tags':tags,
            'color':color,
            'font_info':font_info,
            'alpha':alpha
        })


    def set_range_valid_rectangles(self, origin, destination):
        """ It is going to be proably a deprecated method """
        self.zones = self.zones[origin:destination]
        self.all_tags = self.all_tags[origin:destination]


    def set_valid_rectangles(self, indexes):
        """ It is going to be proably a deprecated method """

        # This if is just for efficiency
        if not indexes:
            self.zones = []
            self.all_tags = []
            return

        for i in range(len(self.zones)):
            if i not in indexes:
                self.zones.pop(i)
                self.all_tags.pop(i)


    def draw(self, frame, coordinates=(-1,-1), draw_tags=True, fx=1, fy=1, interpolation=cv2.INTER_LINEAR):
        """  Draw all selections.

        Arguments:
        frame -- opencv frame object where you want to draw

        Keyword arguments:
        coordinates -- if indicated, the system will draw tags inside the selected
                       coordinates. If not passed, the system will draw all the
                       tags (default (-1,-1))
        draw_tags -- boolean value, if false, the system won't draw any tag
                     (default True)
        fx -- frame horizonal scale (default 1)
        fy -- frame vertical scale (default 1)
        interpolation -- cv2 default scaling algorithm (default cv2.INTER_LINEAR)
        """

        if coordinates != (-1,-1):
            all_tags = []
            for zone, tags in zip(self.zones, self.all_tags):
                # zone = (x1,y1,x2,y2)
                if coordinates[0] >= zone[0] and coordinates[0] <= zone[2] and \
                   coordinates[1] >= zone[1] and coordinates[1] <= zone[3]:
                    all_tags.append(tags)
                else:
                    all_tags.append([])
        else:
            all_tags = self.all_tags

        # Step 1: Draw polygons
        next_frame = select_polygon(
            frame.copy(),
            all_vertexes=self.polygon_zones,
            color=self.polygon_color,
            thickness=self.thickness,
            closed=self.closed_polygon,
            show_vertexes=self.show_vertexes
        )

        # Step 2: Draw selections
        next_frame = select_multiple_zones(
            next_frame,
            self.zones,
            all_tags=all_tags,
            alpha=self.alpha,
            color=self.color,
            normalized=self.normalized,
            thickness=self.thickness,
            filled=self.filled,
            peephole=self.peephole,
            margin=self.margin,
            color_by_tag=self.color_by_tag,
            specific_properties=self.specific_properties)

        # Step 3: Draw free tags
        for free_tag in self.free_tags:
            next_frame = draw_free_tag(
                next_frame,
                free_tag['coordinates'],
                free_tag['tags'],
                alpha=free_tag['alpha'],
                color=free_tag['color'],
                font_info=free_tag['font_info']
            )

        return cv2.resize(next_frame, (0,0), fx=fx, fy=fy, interpolation=interpolation)
