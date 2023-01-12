import json

import pika

if __name__ == "__main__":
    parameters = pika.URLParameters("amqp://crawlers:rAt5HbgN9odP@192.168.5.46:5672/crawlers")
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel(channel_number=0)
    res = channel.queue_declare(
        queue='insta_test',
        durable=True,
        exclusive=False,
        auto_delete=False,
        passive=True
    )
    print('Messages in queue %d' % res.method.message_count)
