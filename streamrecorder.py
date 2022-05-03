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
        self.__timer = Timer(video_length)
        self.__active = False

    def push_frame(self, frame: np.array):
        if not self.__active:
            return

        if self.__active and self.__timer.elapsed():
            self.__active = False
            video_path = self.__save_video()
            self.__callback(video_path)

        self.__buffer.append(frame)
        logging.info(f"Recording Video Frame.")

    def start_recording(self):
        self.__active = True
        self.__timer.start()

    def __save_video(self):
        video_path = f'{datetime.now().strftime("%d-%b-%Y_%H-%M-%S")}.mp4'
        video = ImageSequenceClip(self.__buffer, fps=self.__fps)
        video.write_videofile(video_path, codec="libx264")
        logging.info(f"Saving video at {video_path}")
        self.__buffer = []
        self.__callback(video_path)
        return video_path

    def is_active(self):
        return not self.__timer.elapsed() and self.__active
