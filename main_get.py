import json

import pika

if __name__ == "__main__":
    parameters = pika.URLParameters("amqp://crawlers:rAt5HbgN9odP@192.168.5.46:5672/crawlers")
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel(channel_number=1)


    def callback(ch, method, properties, body):
        try:
            body = json.loads(body.decode("utf-8"))
            res = {
                "id":body.get("id"),
                "last_modified": '2023-01-01 01:01:01.000'
                   }
            print(body)

            channel.basic_publish(exchange='',
                                  routing_key='insta_source_parse_result',
                                  body=json.dumps(res))
        except Exception as e:
            print(f"callback{e}")


    # channel.queue_declare(
    #     queue='insta_source_parse_result',
    # )
    channel.basic_consume(queue='insta_source_parse', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

