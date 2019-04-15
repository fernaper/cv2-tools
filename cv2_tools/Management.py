# MIT License
# Copyright (c) 2019 Fernando Perez
import time
import cv2

# TODO: Document ManagerCV2
class ManagerCV2():

    _tries_reconnect_stream = 10

    def __init__(self, video, is_stream=False, fps_limit=0):
        self.video = video
        self.is_stream = is_stream
        self.stream = video
        self.fps_limit = fps_limit

        self.last_keystroke = -1
        self.keystroke_manager = {
            # The first three elements will have allways the same length
            'keystroke':[],
            'wait_key':[],
            'keystroke_handler':[],
            'keystroke_args':[],
            'exit_keystrokes':[],
        }

        self.ret_handler = None
        self.ret_handler_args = ()

        self.initial_time = None
        self.final_time = None
        self.count_frames = 0


    def __iter__(self):
        self.initial_time = time.time()
        self.last_frame_time = self.initial_time
        self.count_frames = 0
        self.last_keystroke = -1
        return self


    def __next__(self):
        ret, frame = self.video.read()
        self.final_time = time.time()

        if self.is_stream:
            for i in range(ManagerCV2._tries_reconnect_stream):
                ret, frame = self.video.read()
                if ret:
                    break
                if i+1 == ManagerCV2._tries_reconnect_stream:
                    self.end_iteration()
        elif not ret:
                self.end_iteration()

        for i, wait_key in enumerate(self.keystroke_manager['wait_key']):
            self.last_keystroke = cv2.waitKey(wait_key)

            if self.last_keystroke in self.keystroke_manager['keystroke']:
                index = self.keystroke_manager['keystroke'].index(self.last_keystroke)

                self.keystroke_manager['keystroke_handler'][index](*self.keystroke_manager['keystroke_args'][index])
                if self.last_keystroke in self.keystroke_manager['exit_keystrokes']:
                    self.end_iteration()

        self.count_frames += 1

        # Here we limit the speed (if we want constant frames)
        if self.fps_limit:
            time_to_sleep = (1 / self.fps_limit) - (time.time() - self.last_frame_time)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

            self.last_frame_time = time.time()
        return frame


    def set_ret_handler(self, method, *args):
        self.ret_handler = method
        self.ret_handler_args = args


    def add_keystroke(self, keystroke, wait_key, method, *args, exit=False):
        self.keystroke_manager['keystroke'].append(keystroke)
        self.keystroke_manager['wait_key'].append(wait_key)
        self.keystroke_manager['keystroke_handler'].append(method)
        self.keystroke_manager['keystroke_args'].append(args)
        if exit:
            self.keystroke_manager['exit_keystrokes'].append(keystroke)


    def get_last_keystroke(self):
        return self.last_keystroke


    def end_iteration(self, *args):
        self.video.release()
        if self.ret_handler:
            self.ret_handler(*self.ret_handler_args)
        raise StopIteration


    def get_fps(self):
        return round(self.count_frames / (self.final_time - self.initial_time),3)
