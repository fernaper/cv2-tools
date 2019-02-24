from opencv_draw_tools.SelectZone import *

name = 'opencv_draw_tools'
help = '''
MIT License
Copyright (c) 2019 Fernando Perez
For more information visit: https://github.com/fernaper/opencv-draw-tools
Also you can write complete_help'''
__version__ =  '0.1.5'

try:
    complete_help = '''
    {} - {}
    {}
    {}
    '''.format(name, __version__, help, get_complete_help())
except Exception as e:
    complete_help = '''
    {} - {}
    {}
    '''.format(name, __version__, help)
