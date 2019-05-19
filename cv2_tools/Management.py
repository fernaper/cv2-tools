# MIT License
# Copyright (c) 2019 Fernando Perez
import numpy as np
import time
import cv2

from queue import Queue
from threading import Thread


class ManagerCV2():
    """ ManagerCV2 helps to manage videos and streams

    With this Class you are capable to iterete a video frame by frame (if you want,
    you can also limit the FPS).
    Also you can add keystrokes with your own callbacks methods in a easiest way.
    At the same time you can ask to this manager the index of the current frame
    (self.count_frames) and the FPS processing average.

    Finally you can set a method to execute when finishing the iteration.
    """


    _tries_reconnect_stream = 10


    def __init__(self, video, is_stream=False, fps_limit=0, queue_size=256):
        """  ManagerCV2 constructor.

        Arguments:
        video -- cv2.VideoCapture that it is going to manage

        Keyword arguments:
        is_stream -- Bool to indicate if it is an stream or not.
                 It is not necessary to set it to True if you are using an stream.
                 It is only for managing streams issuess.
                 On a stream it is possible to lose frames, so, if you set is_stream
                 to True, it will try to reconnect the stream as many times as
                 `ManagerCV2._tries_reconnect_stream` indicates. (Default: False)
        fps_limit -- You can set with it the maximum FPS of the video. If you
                     set it to 0, it means no limit. (Default: 0)
        queue_size -- The maximum number of frames to store in the queue. (Default: 256)
        """
        # Video/Stream managment attributes
        self.video = video
        self.is_stream = is_stream
        self.stream = video
        self.fps_limit = fps_limit
        self.queue_size = queue_size
        self.stopped = False
        self.queue = None
        self.queue_thread = None
        self.awake_thread = None

        # Keystrokes attributes
        self.last_keystroke = -1
        self.keystroke_manager = {
            # The first three elements will have allways the same length
            'keystroke':[],
            'wait_key':[],
            'keystroke_handler':[],
            'keystroke_args':[],
            'keystroke_kwargs':[],
            'exit_keystrokes':[],
        }

        self.ret_handler = None
        self.ret_handler_args = ()
        self.ret_handler_kwargs = {}

        self.initial_time = None
        self.final_time = None
        self.count_frames = 0


    def __iter__(self):
        self.initial_time = time.time()
        self.last_frame_time = self.initial_time
        self.final_time = self.initial_time
        self.count_frames = 0
        self.last_keystroke = -1

        # All queue management
        self.stopped = False
        self.queue = Queue(maxsize=self.queue_size)
        self.queue_awake = Queue(maxsize=1)

        self.queue_thread = Thread(target=self.fill_queue, args=())
        self.queue_thread.daemon = True
        self.queue_thread.start()
        return self


    def __next__(self):
        # Get frame from queue if not stopped yet
        if self.stopped:
            self.end_iteration()

        frame = self.queue.get()

        # This is how it comunicates with the thread (to indicate it takes something)
        if not self.queue_awake.full():
            self.queue_awake.put(None)

        # If we get a frame but it is None, it means that we finished the queue
        if type(frame) == type(None):
            self.end_iteration()

        self.final_time = time.time()
        self.count_frames += 1

        # If they press one of the keystrokes, it will raise the method
        for i, wait_key in enumerate(self.keystroke_manager['wait_key']):
            self.last_keystroke = cv2.waitKey(wait_key)

            if self.last_keystroke in self.keystroke_manager['keystroke']:
                index = self.keystroke_manager['keystroke'].index(self.last_keystroke)

                self.keystroke_manager['keystroke_handler'][index](
                    *self.keystroke_manager['keystroke_args'][index],
                    **self.keystroke_manager['keystroke_kwargs'][index])
                if self.last_keystroke in self.keystroke_manager['exit_keystrokes']:
                    self.end_iteration()

        # Here we limit the speed (if we want constant frames)
        if self.fps_limit:
            time_to_sleep = (1 / self.fps_limit) - (time.time() - self.last_frame_time)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

            self.last_frame_time = time.time()
        return frame


    def fill_queue(self):
        # keep looping infinitely
        while True:
            # If the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            if not self.queue.full():
                ret, frame = self.video.read()
                # If it is a streaming we will try to reconnect
                if self.is_stream and not ret:
                    exit = False
                    for i in range(ManagerCV2._tries_reconnect_stream):
                        ret, frame = self.video.read()
                        if ret:
                            break
                        if i+1 == ManagerCV2._tries_reconnect_stream:
                            self.stop_queue()
                            return
                elif not ret:
                    self.stop_queue()
                    return

                self.queue.put(frame)
            else:
                # I want to wait until someone awake me
                self.queue_awake.get()


    def stop_queue(self):
        self.stop_queue = True
        self.queue.put(None)


    def set_ret_handler(self, method, *args, **kwargs):
        """ Method to execute when finished Video/Stream

        Arguments:
        method -- Method to execute
        args -- Arguments to pass to the method
        kwargs -- Keyword argoments to pass to the method
        """
        self.ret_handler = method
        self.ret_handler_args = args
        self.ret_handler_kwargs = kwargs


    def add_keystroke(self, keystroke, wait_key, method, *args, **kwargs):
        """ Method to execute when pressed a key

        Arguments:
        keystroke -- Key to check if pressed
        waitkey -- Ms to wait key (it works exactly as cv2.waitKey)
        method -- Method to execute
        args -- Arguments to pass to the method
        kwargs -- Keyword arguments to pass to the method
                  Note that this method can receive and exit param (you
                  can't pass a param with the same name to your own method)
        """
        exit = False
        if 'exit' in kwargs:
            exit = kwargs['exit']
            kwargs.pop('exit', None)

        self.keystroke_manager['keystroke'].append(keystroke)
        self.keystroke_manager['wait_key'].append(wait_key)
        self.keystroke_manager['keystroke_handler'].append(method)
        self.keystroke_manager['keystroke_args'].append(args)
        self.keystroke_manager['keystroke_kwargs'].append(kwargs)
        if exit:
            self.keystroke_manager['exit_keystrokes'].append(keystroke)


    def get_last_keystroke(self):
        """ Check the last pressed keystroke (not neccesarily in the last frame)"""
        return self.last_keystroke


    def end_iteration(self):
        """ Internal method to finish iteration, with the previous configuration"""
        self.stopped = True
        self.video.release()
        if self.ret_handler:
            self.ret_handler(*self.ret_handler_args, **self.ret_handler_kwargs)
        raise StopIteration


    def get_fps(self):
        """ Get average FPS"""
        return round(self.count_frames / (self.final_time - self.initial_time),3)
