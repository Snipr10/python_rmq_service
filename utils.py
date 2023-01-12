import pika
from datetime import timedelta


def get_chanel():
    parameters = pika.URLParameters("amqp://crawlers:rAt5HbgN9odP@192.168.5.46:5672/crawlers")
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    return channel


def update_time_timezone(my_time):
    return my_time + timedelta(hours=3)
