import cv2
import time
import unittest

from cv2_tools.Management import ManagerCV2

class TestFrames(unittest.TestCase):

    def test_fast_counter(self):
        cap = cv2.VideoCapture('media/sample_video.mp4')
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        manager_cv2 = ManagerCV2(cap)

        for _ in manager_cv2:
            pass
        
        self.assertEqual(int(total_frames), manager_cv2.count_frames, 'Examinated frames should be equals')


    def test_slow_counter(self):
        cap = cv2.VideoCapture('media/sample_video.mp4')
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        manager_cv2 = ManagerCV2(cap)

        for _ in manager_cv2:
            if manager_cv2.count_frames % 20 == 0:
                time.sleep(0.02)

        self.assertEqual(int(total_frames), manager_cv2.count_frames, 'Examinated frames should be equals')


if __name__ == "__main__":
    unittest.main()
