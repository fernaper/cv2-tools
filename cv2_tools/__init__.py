from cv2_tools.utils import webcam_test, get_complete_help

name = 'cv2_tools'
help = '''
MIT License
Copyright (c) 2019 Fernando Perez
For more information visit: https://github.com/fernaper/opencv-draw-tools
Also you can write complete_help to view full information'''
__version__ =  '2.0.2'

complete_help = '''
{} - v{}
{}
{}
'''.format(name, __version__, help, get_complete_help())
