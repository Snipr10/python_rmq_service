import json

import os
import datetime
import time

import django.db

from utils import get_chanel, update_time_timezone


def read_tasks_while():
    while True:
        try:
            read_tasks()
        except Exception:
            time.sleep(10)


def read_tasks():
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
    from core.models import SourcesItems

    channel = get_chanel()
    result = []

    def callback(ch, method, properties, body):
        try:
            body = json.loads(body.decode("utf-8"))
            print(body)
            result.append(
                SourcesItems(
                    id=body.get("id"),
                    last_modified=update_time_timezone(datetime.datetime.fromisoformat(body.get("last_modified"))),
                    taken=0,
                    disabled=body.get("disabled", 0)
                )
            )
            if len(result) > 1:
                django.db.close_old_connections()
                SourcesItems.objects.bulk_update(result, ['last_modified', 'taken', 'disabled'], batch_size=200)
                result.clear()
        except Exception as e:
            print(f"callback{e}")
            django.db.close_old_connections()

    channel.basic_consume(queue='insta_source_parse_result', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    read_tasks()
