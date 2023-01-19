import json

import os
import datetime
import django.db

from utils import get_chanel


def read_sessions():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_rmq_service.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    print(1)
    import django

    django.setup()
    import pymysql

    pymysql.install_as_MySQLdb()
    from core.models import Sessions

    channel = get_chanel()
    result = []

    def callback(ch, method, properties, body):
        try:
            body = json.loads(body.decode("utf-8"))
            print(body)
            result.append(
                Sessions(
                    id=body.get("id"),
                    last_parsing=datetime.datetime.fromisoformat(body.get("last_parsing")),
                    taken=0
                )
            )
            if len(result) > 10:
                Sessions.objects.bulk_update(result, ['last_parsing', 'taken'], batch_size=200)
                result.clear()

        except Exception as e:
            print(f"callback{e}")
            django.db.close_old_connections()

    channel.basic_consume(queue='insta_source_ig_session_parse', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    read_sessions()
