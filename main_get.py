
if __name__ == "__main__":
    parameters = pika.URLParameters("amqp://crawlers:rAt5HbgN9odP@192.168.5.46:5672/crawlers")
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel(channel_number=i)


    def callback(ch, method, properties, body):
        try:
            body = json.loads(body.decode("utf-8"))
            print(body)
        except Exception as e:
            print(f"callback{e}")

    channel.basic_consume(queue='insta_test', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

