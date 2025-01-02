import logging
from datetime import datetime
import pytz

class TimezoneFormatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp, pytz.timezone('Asia/Shanghai'))
        return dt

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat()
        return s

def init_logging(log_file):
    formatter = TimezoneFormatter(
        fmt='%(asctime)s - %(levelname)s - Task %(task_id)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.DEBUG,  # 记录所有级别的日志
        handlers=[handler, console_handler]
    )