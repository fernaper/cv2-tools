# MIT License
# Copyright (c) 2019 Fernando Perez
import numpy as np
import time
import cv2

try:
    from PIL import Image
except ModuleNotFoundError as e:
    pass

try:
    # It is usefull if you want to detect scene changes
    import imagehash
except ModuleNotFoundError as e:
    pass

try:
    # It is usefull if you want to track objects
    import dlib
except ModuleNotFoundError as e:
    pass


from queue import Queue
from threading import Thread


class ManagerCV2():
    """ ManagerCV2 helps to manage videos and streams

    With this Class you are capable to iterate a video frame by frame (if you want,
    you can also limit the FPS).
    Also you can add keystrokes with your own callbacks methods in a easiest way.
    At the same time you can ask to this manager the index of the current frame
    (self.count_frames) and the FPS processing average.

    Finally you can set a method to execute when finishing the iteration.
    """


    _tries_reconnect_stream = 10

    class KeystrokeManager():
        """ KeystrokeManager helps to manage all keystroke during the for of the manager

        With this Class ManagerCV2 is capable to manage easily each keystroke.
        """

        def __init__(self, **kwargs):
            """ KeystrokeManager constructor.

            Have in mind that with this class you will never get an error when
            you ask for an attribute that doesn't exist.
            It will create with the value: False

            Thats cool because su can pass no params to this constructor, and
            then when you need to chek if a keystroke was pressed (you really
            check the param, not the keystroke itself), if it was never pressed
            the param doesn't exist, but we take care of it for you :)

            Keyword arguments:
                Each keyword argument that you pass to the constructor will be
                an attribute for this object.
            """
            self.__dict__.update(kwargs)

        def __getattr__ (self, attr):
            """ getattr

            Have in mind that this method is called each time that you try to get
            an attribute that doesn't exist.
            We manage it creating this attribute an giving a value of False.
            This is because we want to inform that the asociated with this parameter
            wasen't pressed yet.
            """
            self.__dict__[attr] = False
            return False

        def execute_management(self, *args):
            """ execute_management

            Each time a relevant key is pressed, it will set the associated
            param to True. So you can manage it and decide what to do in each
            case.
            """
            for arg in args:
                value = getattr(self, arg)
                setattr(self, arg, not value)


    def __init__(self, video, is_stream=False, fps_limit=0, queue_size=256, detect_scenes=False, show_video=False):
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
        queue_size -- The maximum number of frames to store in the queue (for multiprocessing). (Default: 256)
        detect_scenes -- Bool to indicate if you want to detect changes of scenes,
                         it will have an small impact on the frame rate. Almost 0
                         if it is a video and you set fps_limit < 60. (Default: False)
        show_video -- Bool to indicate if you want to show the video (with cv2.imshow).
                      If you use the method `add_keystroke` you don't need to use this param
                      (its fine if you still want to put it to True).
                      Also, if you doesn't want to show the video, let it a False. (Default: False)
        """
        # Video/Stream managment attributes
        self.video = video
        self.is_stream = is_stream
        self.stream = video
        self.fps_limit = fps_limit
        self.show_video = show_video
        self.queue_size = queue_size
        self.stream_error = False
        self.stopped = False
        self.queue = None
        self.queue_thread = None
        self.awake_thread = None

        # Keystrokes attributes
        self.key_manager = ManagerCV2.KeystrokeManager()
        self.last_keystroke = -1
        self.__keystroke_dict = {
            # The first three elements will have allways the same length
            'keystroke':[],
            'wait_key':[],
            'keystroke_args':[],
            'exit_keystrokes':[],
        }

        self.ret_handler = None
        self.ret_handler_args = ()
        self.ret_handler_kwargs = {}

        # Additional features
        self.initial_time = None
        self.final_time = None
        self.count_frames = 0

        # Scene detection
        self.detect_scenes = detect_scenes
        self.new_scene = False
        self.previous_frame_hash = None
        self.hash_distance = 25

        # Tracking algorithm
        self.selector_tracker = None
        self.trackers = []


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
        if self.stopped and self.queue.qsize() == 0:
            self.end_iteration()

        frame, frame_hash = self.queue.get(block=True)

        # This is how it comunicates with the thread (to indicate it takes something)
        if not self.queue_awake.full():
            self.queue_awake.put(None)

        # If we get a frame but it is None, it means that we finished the queue
        if frame is None:
            self.end_iteration()

        # If we must detect scenes it will help us
        if self.detect_scenes:
            if not self.previous_frame_hash:
                self.new_scene = True
            else:
                self.new_scene = (frame_hash - self.previous_frame_hash > self.hash_distance)

            self.previous_frame_hash = frame_hash

        self.final_time = time.time()
        self.count_frames += 1

        # If they press one of the keystrokes, it will raise the method
        for i, wait_key in enumerate(self.__keystroke_dict['wait_key']):
            self.last_keystroke = cv2.waitKey(wait_key)

            if self.last_keystroke in self.__keystroke_dict['keystroke']:
                index = self.__keystroke_dict['keystroke'].index(self.last_keystroke)

                self.key_manager.execute_management(*self.__keystroke_dict['keystroke_args'][index])
                if self.last_keystroke in self.__keystroke_dict['exit_keystrokes']:
                    self.end_iteration()

        # If we doesn't add a keystroke we should at least wait a minimum in order to
        # be capable to reproduce the video with cv2.imshow (if you indicated that you want
        # tho display the video)
        # Also, you can wait by yourself (without using Management)
        if self.show_video and not self.__keystroke_dict['wait_key']:
            cv2.waitKey(1)

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
                # In case of streaming it means that we could lose some frames
                # so this variable is usefull to check it
                self.stream_error = bool(ret)

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

                frame_hash = None
                if self.detect_scenes:
                    frame_hash = imagehash.dhash(Image.fromarray(frame))
                self.queue.put((frame,frame_hash))
                queue_size = self.queue.qsize()
            else:
                # I want to wait until someone awake me
                self.queue_awake.get()


    def stop_queue(self):
        self.stopped = True
        self.queue.put((None,None))


    def set_tracking(self, selector, frame):
        self.selector_tracker = selector
        self.trackers = []

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = rgb_frame.shape

        for selection in self.selector_tracker.zones:
            if self.selector_tracker.normalized:
                selection = (int(selection[0]*width),
                             int(selection[1]*height),
                             int(selection[2]*width),
                             int(selection[3]*height))
            tracker = dlib.correlation_tracker()
            tracker.start_track(rgb_frame, dlib.rectangle(*selection))
            self.trackers.append(tracker)


    def get_tracking(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = rgb_frame.shape

        for i, tracker in enumerate(self.trackers):
            tracker.update(rgb_frame)
            pos = tracker.get_position()
            selection = (int(pos.left()),int(pos.top()), int(pos.right()), int(pos.bottom()))
            if self.selector_tracker.normalized:
                selection = (selection[0]/width,
                             selection[1]/height,
                             selection[2]/width,
                             selection[3]/height)
            self.selector_tracker.zones[i] = selection
        return self.selector_tracker


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


    def add_keystroke(self, keystroke, wait_key, *args, exit=False):
        """ Method to execute when pressed a key

        Arguments:
        keystroke -- Key to check if pressed
        waitkey -- Ms to wait key (it works exactly as cv2.waitKey)
        args -- Arguments to pass to the method
        """
        self.__keystroke_dict['keystroke'].append(keystroke)
        self.__keystroke_dict['wait_key'].append(wait_key)
        self.__keystroke_dict['keystroke_args'].append(args)
        if exit:
            self.__keystroke_dict['exit_keystrokes'].append(keystroke)


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


    def is_error_last_frame(self):
        """ If we lose the last frame it will return True eoc False (only usefull for streams)"""
        return self.stream_error
