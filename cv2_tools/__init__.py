from cv2_tools.Utils import webcam_test, get_complete_help

name = 'cv2_tools'
help = '''
MIT License
Copyright (c) 2019 Fernando Perez
For more information visit: https://github.com/fernaper/cv2-tools
Also you can write complete_help to view full information'''
__version__ = '2.4.0'

complete_help = '''
{} - v{}
{}
{}
'''.format(name, __version__, help, get_complete_help())
