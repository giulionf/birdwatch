import logging
from collections import Callable
from datetime import timedelta, datetime
import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from timer import Timer


class StreamRecorder:

    def __init__(self, video_length: timedelta.seconds, fps: int, callback: Callable):
        self.__buffer = []
        self.__video_length = video_length
        self.__callback = callback
        self.__fps = fps
        self.__max_pre_event_frames = (video_length / 2) * fps
        self.__post_event_timer = Timer(video_length / 2)  # half after trigger
        self.__active = False

    def push_frame(self, frame: np.array):
        if self.__active and self.__post_event_timer.elapsed():
            self.__active = False
            video_path = self.__save_video()
            self.__callback(video_path)
            self.__buffer = []

        self.__buffer.append(frame)
        n_remove = max(0, len(self.__buffer) - self.__max_pre_event_frames)
        self.__buffer = self.__buffer[n_remove:]
        logging.info(f"Recording Video Frame. Buffer size: {len(self.__buffer)}")

    def start_recording(self):
        self.__active = True
        self.__post_event_timer.start()

    def __save_video(self):
        video_path = f'{datetime.now().strftime("%d-%b-%Y_%H-%M-%S")}.mp4'
        video = ImageSequenceClip(self.__buffer, fps=self.__fps)
        video.write_videofile(video_path, codec="libx264")
        logging.info(f"Saving video at {video_path}")
        return video_path

    def is_active(self):
        return not self.__timer.elapsed() and self.__active
