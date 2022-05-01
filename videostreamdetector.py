from collections import Callable
from datetime import timedelta, datetime
import logging
import cv2
import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

from detection import utils
from detection.object_detector import ObjectDetector, ObjectDetectorOptions


class VideoStreamDetector:

    def __init__(self,
                 rtsp_url: str,
                 model_weights_path: str,
                 class_to_detect: str,
                 callback: Callable,
                 rtsp_buff_size: int = 5,
                 pause_after_detection: timedelta.seconds = 30,
                 video_sequence_length: timedelta.seconds = 5,
                 detection_threshold: float = 0.65,
                 max_detection_count: int = 3,
                 detector_threads: int = 4,
                 processing_fps = 1,
                 debug: bool = False):

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
        self.__pause_after_detection = pause_after_detection
        self.__video_sequence_length = video_sequence_length
        self.__callback = callback
        self.__last_frame_time = datetime.now() - timedelta(days=9999)
        self.__last_recording_frame_time = datetime.now() - timedelta(days=9999)
        self.__last_detection_time = datetime.now() - timedelta(days=9999)
        self.__video_buff = []
        self.__fps_buff = []
        self.__processing_fps = processing_fps
        self.__debug = debug

    def start(self):
        logging.info(f"Connecting to video stream at {self.__rtsp_url}")
        # Set up video stream
        video_stream = cv2.VideoCapture(self.__rtsp_url)
        video_stream.set(cv2.CAP_PROP_BUFFERSIZE, self.__rtsp_buff_size)

        # Start the video loop
        while video_stream.isOpened():
            success, frame = video_stream.read()
            if not success:
                continue

            self.on_frame_received(frame)

            if cv2.waitKey(20) & 0xFF == ord('q'):
                break

    def on_frame_received(self, frame: np.array):
        now = datetime.now()
        delta_last_detection = (now - self.__last_detection_time).total_seconds()
        delta_last_frame_processed = (now - self.__last_frame_time).total_seconds()

        if delta_last_detection < self.__video_sequence_length:
            self.__record_video(frame)

        elif len(self.__video_buff) > 0:
            self.__save_video()

        elif delta_last_detection > self.__pause_after_detection and delta_last_frame_processed > self.__processing_fps:
            frame = self.__detect_objects(frame)

        if self.__debug:
            cv2.imshow("Frame", frame)

    def __record_video(self, frame):
        logging.info("Recording at full speed.")
        delta_last_frame = (datetime.now() - self.__last_recording_frame_time).total_seconds()
        fps = 1.0 / delta_last_frame
        self.__video_buff.append(frame)
        self.__fps_buff.append(fps)
        self.__last_recording_frame_time = datetime.now()

    def __save_video(self):
        fps = np.mean(self.__fps_buff)
        fps = max(1, min(60, fps))
        video_path = f'{self.__last_detection_time.strftime("%d-%b-%Y_%H-%M-%S")}.mp4'
        video = ImageSequenceClip(self.__video_buff, fps=fps)
        video.write_videofile(video_path, codec="libx264")
        logging.info(f"Saving video. FPS={fps:.2f}.")
        self.__video_buff = []
        self.__fps_buff = []
        self.__callback(video_path)

    def __detect_objects(self, frame):
        logging.info("Running Detection.")
        detections = self.__detector.detect(frame)
        frame = utils.visualize(frame, detections)

        if any([detection.categories[0].label == self.__class_to_detect for detection in detections]):
            self.__last_detection_time = datetime.now()
        self.__last_frame_time = datetime.now()
        self.__last_recording_frame_time = datetime.now()
        return frame
