# MIT License
# Copyright (c) 2019 Fernando Perez
from cv2_tools.Selection import SelectorCV2
import cv2_tools

import base64
import zlib
import json

def json_zip(original_dict):
    """ Internal function. It receives a dict and generates a comppressed dict with metadata"""
    return {
        'meta':{
            'cv2_tools-version':cv2_tools.__version__
        },
        'b64_data': base64.b64encode(
            zlib.compress(
                json.dumps(original_dict).encode('utf-8')
            )
        ).decode('ascii'),
    }


def json_unzip(compressed_dict, insist=True):
    """ Internal function. It receives a compressed dict and returns the original one."""
    try:
        assert (compressed_dict['b64_data'])
    except:
        if insist:
            raise RuntimeError("JSON not in the expected format {'b64_data': zipstring}")
        else:
            return compressed_dict

    try:
        compressed_dict = zlib.decompress(base64.b64decode(compressed_dict['b64_data']))
    except:
        raise RuntimeError("Could not decode/unzip the contents")

    try:
        compressed_dict = json.loads(compressed_dict)
    except:
        raise RuntimeError("Could interpret the unzipped contents")

    return compressed_dict


# TODO: Make it possible to process half of a video in the first time, and
# reproduce the first half and process and save the second one
class StorageCV2():
    """ StorageCV2 helps to save and load previous selections.

    Some times, your detection process can't go on real time, but you want to
    reproduce it at an stable amount of FPS, or you can try to avoid expensive
    API calls when you're processing the same video again.

    This is exactly why this class exists. With it you can make it works in
    synergy with SelectorCV2 to save and load previous process.

    The data stored in the file is practically as required and a post-compression
    is carried out.

    Json data structure (before comppression):

    {
        'default_parameters': {
            'alpha': alpha,
            'color': color,
            'color_by_tag':{},
            'filled': filled,
            'peephole': peephole,
            'normalized': normalized,
            'thickness': thickness,
            'margin': margin,
            'closed_polygon': closed_polygon
        },
        'frames': [
            {
                'zones':[[x1,x2,y1,y2],...],
                'all_tags':[['text',...],...],
                'free_tags':[], # Not always
                'polygon_zones': [
                    [(x,y),..],
                    ...
                ],
                'specific_properties': {
                    {
                        0: {
                            'alpha':alpha,
                            'color':color,
                            'filled':filled,
                            'peephole':peephole
                        },
                        ...
                    }
                }
            },
            ...
        ]

    }

    Json data structure (after compression):

    {
        'meta':{
            'cv2_tools-version':cv2_tools.__version__
        },
        'b64_data': comprressed data
    }

    """


    def __init__(self, path=''):
        """  StorageCV2 constructor.

        Keyword arguments:
        path -- Path with the compressed json to load. (default '')
        """
        self.complete_structure = {}
        if path:
            self.load_from_file(path)
        self.count_frames = 0


    def __iter__(self):
        self.count_frames = 0
        return self


    def __next__(self):
        if self.count_frames >= len(self.complete_structure['frames']):
            raise StopIteration

        info_frame = self.complete_structure['frames'][self.count_frames]

        selector = SelectorCV2(**self.complete_structure['default_parameters'])

        specific_properties = {}
        if 'specific_properties' in info_frame:
            specific_properties = info_frame['specific_properties']

        for i, zone in enumerate(info_frame['zones']):
            properties = {}
            if specific_properties and i in specific_properties:
                properties = specific_properties[i]

            selector.add_zone(zone, tags=info_frame['all_tags'][i], specific_properties=properties)

        for polygon in info_frame['polygon_zones']:
            selector.add_polygon(polygon, surrounding_box=False)

        if 'free_tags' in info_frame:
            for free_tag in info_frame['free_tags']:
                coordinates = free_tag.pop('coordinates')
                tags = free_tag.pop('tags')
                # This is how we can pass all the other params to the function in an easy way
                selector.add_free_tags(coordinates,tags, **free_tag)

        self.count_frames += 1

        return selector


    def load_from_selector(self, selector):
        """ Internal method to initial data from SelectorCV2"""

        self.complete_structure = {
            'default_parameters': {
                'alpha': selector.alpha,
                'color': selector.color,
                'color_by_tag': selector.color_by_tag,
                'filled': selector.filled,
                'peephole': selector.peephole,
                'normalized': selector.normalized,
                'thickness': selector.thickness,
                'margin': selector.margin,
                'closed_polygon': selector.closed_polygon
            },
            'frames':[]
        }


    def add_frame(self, selector):
        """ Method to add last frame selection

        Arguments:
        selector -- SelectorCV2 object with the last frame information
        """

        # If it is the first call
        if not self.complete_structure:
            self.load_from_selector(selector)

        frame_structure = {
            'polygon_zones':selector.polygon_zones,
            'zones':selector.zones,
            'all_tags':selector.all_tags,
            'free_tags':selector.free_tags
        }

        if selector.specific_properties:
            frame_structure['specific_properties'] = selector.specific_properties

        self.complete_structure['frames'].append(frame_structure)


    def load_from_file(self, path):
        """ Internal method to load data from file(path)"""

        with open(path) as json_file:
            self.complete_structure = json_unzip(json.load(json_file))

        # We need to change key types from string to int in specific_properties
        for i, frame in enumerate(self.complete_structure['frames']):
            if 'specific_properties' in self.complete_structure['frames'][i]:
                self.complete_structure['frames'][i]['specific_properties'] = {
                    int(k):v for k,v in self.complete_structure['frames'][i]['specific_properties'].items()
                }


    def save(self, path):
        """ Method to save the necessari data (compressed) into file (path)"""

        with open(path, 'w') as outfile:
            json.dump(json_zip(self.complete_structure), outfile)
