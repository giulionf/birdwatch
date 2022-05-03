from datetime import timedelta, datetime


class Timer:

    def __init__(self, trigger_duration: timedelta.seconds):
        self.__timestamp = datetime.now() - timedelta(days=9999)
        self.__trigger_duration = trigger_duration

    def start(self):
        self.__timestamp = datetime.now()

    def seconds_since(self):
        return (datetime.now() - self.__timestamp).total_seconds()

    def elapsed(self):
        return self.seconds_since() > self.__trigger_duration
