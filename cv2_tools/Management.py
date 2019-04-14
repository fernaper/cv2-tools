# MIT License
# Copyright (c) 2019 Fernando Perez
import time
import cv2

# TODO: Document ManagerCV2
class ManagerCV2():

    _tries_reconnect_stream = 10

    def __init__(self, video, is_stream=False, keystroke=-1, wait_key=-1, fps_limit=0):
        self.video = video
        self.is_stream = is_stream
        self.stream = video
        self.fps_limit = fps_limit

        self.keystroke = keystroke
        self.wait_key = wait_key

        self.last_keystroke = -1
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

        if self.wait_key != -1:
            self.last_keystroke = cv2.waitKey(self.wait_key)
            if self.last_keystroke == self.keystroke:
                self.end_iteration()

        self.count_frames += 1

        # Here we limit the speed (if we want constant frames)
        if self.fps_limit:
            time_to_sleep = (1 / self.fps_limit) - (time.time() - self.last_frame_time)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

            self.last_frame_time = time.time()
        return frame


    def get_last_keystroke(self):
        return self.last_keystroke


    def end_iteration(self):
        self.video.release()
        raise StopIteration


    def get_fps(self):
        return round(self.count_frames / (self.final_time - self.initial_time),3)
