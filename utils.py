import hashlib
import datetime

import pika
from datetime import timedelta


def get_chanel():
    parameters = pika.URLParameters("amqp://crawlers:rAt5HbgN9odP@192.168.5.46:5672/crawlers")
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    return channel


def update_time_timezone(my_time):
    return my_time + timedelta(hours=3)


def get_sphinx_id(url):
    m = hashlib.md5()
    m.update(('https://t.me/{}'.format(url)).encode())
    return int(str(int(m.hexdigest()[:16], 16))[:16])

def get_md5_text(text):
    if text is None:
        text = ''
    m = hashlib.md5()
    m.update(text.encode())
    return str(m.hexdigest())


FIRST_DATE = datetime.datetime.fromisoformat('2022-04-01T01:00:00')

