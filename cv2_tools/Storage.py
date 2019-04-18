from cv2_tools.Selection import SelectorCV2
import cv2_tools

import base64
import zlib
import json

"""
Json structure:

{
    'default_parameters': {
        'alpha': alpha,
        'color': color,
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
            'all_tags':[['text',...],...],,
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
"""

def json_zip(j):
    return {
        'meta':{
            'cv2_tools-version':cv2_tools.__version__
        },
        'b64_data': base64.b64encode(
            zlib.compress(
                json.dumps(j).encode('utf-8')
            )
        ).decode('ascii'),
    }


def json_unzip(j, insist=True):
    try:
        assert (j['b64_data'])
    except:
        if insist:
            raise RuntimeError("JSON not in the expected format {'b64_data': zipstring}")
        else:
            return j

    try:
        j = zlib.decompress(base64.b64decode(j['b64_data']))
    except:
        raise RuntimeError("Could not decode/unzip the contents")

    try:
        j = json.loads(j)
    except:
        raise RuntimeError("Could interpret the unzipped contents")

    return j


class StorageCV2():


    def __init__(self, path=''):
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

        self.count_frames += 1

        return selector


    def load_from_selector(self, selector):
        self.complete_structure = {
            'default_parameters': {
                'alpha': selector.alpha,
                'color': selector.color,
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
        # If it is the first call
        if not self.complete_structure:
            self.load_from_selector(selector)

        frame_structure = {
            'polygon_zones':selector.polygon_zones,
            'zones':selector.zones,
            'all_tags':selector.all_tags
        }

        if selector.specific_properties:
            frame_structure['specific_properties'] = selector.specific_properties

        self.complete_structure['frames'].append(frame_structure)


    def load_from_file(self, path):
        with open(path) as json_file:
            self.complete_structure = json_unzip(json.load(json_file))

        # We need to change key types from string to int in specific_properties
        for i, frame in enumerate(self.complete_structure['frames']):
            if 'specific_properties' in self.complete_structure['frames'][i]:
                self.complete_structure['frames'][i]['specific_properties'] = {
                    int(k):v for k,v in self.complete_structure['frames'][i]['specific_properties'].items()
                }


    def save(self, path):
        with open(path, 'w') as outfile:
            json.dump(json_zip(self.complete_structure), outfile)
