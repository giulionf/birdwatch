from collections import Callable
from datetime import timedelta
import logging
import cv2
import numpy as np
from detection import utils
from detection.object_detector import ObjectDetector, ObjectDetectorOptions
from timer import Timer
from streamrecorder import StreamRecorder


class VideoStreamDetector:

    def __init__(self,
                 rtsp_url: str,
                 model_weights_path: str,
                 class_to_detect: str,
                 callback: Callable,
                 rtsp_buff_size: int,
                 pause_after_detection: timedelta.seconds,
                 pause_after_processing: timedelta.seconds,
                 video_sequence_length: timedelta.seconds,
                 restart_time: timedelta.seconds,
                 detection_threshold: float,
                 max_detection_count: int,
                 detector_threads: int,
                 video_fps: int,
                 debug: bool):

        options = ObjectDetectorOptions(
            num_threads=detector_threads,
            score_threshold=detection_threshold,
            max_results=max_detection_count,
            enable_edgetpu=False)

        self.__detector = ObjectDetector(model_path=model_weights_path, options=options)
        self.__rtsp_url = rtsp_url
        self.__rtsp_buff_size = rtsp_buff_size
        self.__model_weights_path = model_weights_path
        self.__class_to_detect = class_to_detect
        self.__post_detection_timeout = Timer(pause_after_detection)
        self.__post_processing_timeout = Timer(pause_after_processing)
        self.__restart_timer = Timer(restart_time)
        self.__stream_recorder = StreamRecorder(video_sequence_length, video_fps, callback)
        self.__debug = debug

    def start(self):
        logging.info(f"Connecting to video stream at {self.__rtsp_url}")

        # Set up video stream
        video_stream = cv2.VideoCapture(self.__rtsp_url)
        video_stream.set(cv2.CAP_PROP_BUFFERSIZE, self.__rtsp_buff_size)
        self.__restart_timer.start()

        # Start the video loop
        while not self.__restart_timer.elapsed() or self.__stream_recorder.is_active():
            success, frame = video_stream.read()
            if not success:
                continue

            self.on_frame_received(frame)

            if cv2.waitKey(20) & 0xFF == ord('q'):
                break

    def on_frame_received(self, frame: np.array):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.__stream_recorder.push_frame(frame)

        if self.__post_detection_timeout.elapsed() and self.__post_processing_timeout.elapsed():
            frame, detections = self.__run_detection(frame)
            self.__post_processing_timeout.start()

            if self.__found_object_of_interest(detections):
                self.__stream_recorder.start_recording()
                self.__post_detection_timeout.start()

        if self.__debug:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imshow("Frame", frame)

    def __run_detection(self, frame):
        detections = self.__detector.detect(frame)
        frame = utils.visualize(frame, detections)
        logging.info(f"Running Detection: {detections}")
        return frame, detections

    def __found_object_of_interest(self, detections):
        return any([detection.categories[0].label == self.__class_to_detect for detection in detections])
