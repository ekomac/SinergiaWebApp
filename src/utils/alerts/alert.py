from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToastAlert(object):
    topic: str = ""
    status: str = ""
    title: str = ""
    message: str = ""
    timestamp: datetime = ""

    def __gen_id(self):
        y = self.timestamp.year
        mo = self.timestamp.month
        d = self.timestamp.day
        h = self.timestamp.hour
        m = self.timestamp.minute
        s = self.timestamp.second
        mi = self.timestamp.microsecond
        return f'{self.topic}-{y}{mo}{d}{h}{m}{s}{mi}'

    def __get_timestamp_dict(self):
        timestamp_dict = {
            'year': self.timestamp.year,
            'month': self.timestamp.month,
            'day': self.timestamp.day,
            'hour': self.timestamp.hour,
            'minute': self.timestamp.minute,
        }
        return timestamp_dict

    def get_as_dict(self):
        return {
            'id': self.__gen_id(),
            'topic': self.topic,
            'status': self.status,
            'title': self.title,
            'message': self.message,
            'timestamp': self.__get_timestamp_dict(),
        }
