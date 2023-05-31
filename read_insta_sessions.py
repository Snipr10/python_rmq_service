import json

import os
import datetime
import time

import django.db

from utils import get_chanel, update_time_timezone


def read_sessions_while():
    while True:
        try:
            read_sessions()
        except Exception:
            time.sleep(10)


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
    from django.db.models import F

    channel = get_chanel()
    result = []
    result_ban = []
    result_ban_ids = []
    result_ok = []

    def callback(ch, method, properties, body):
        try:
            body = json.loads(body.decode("utf-8"))
            try:
                error_message= body.get("error_message", "")
            except Exception:
                error_message = ""
            if body.get("banned"):
                result_ban.append(
                    Sessions(
                        id=body.get("id"),
                        last_parsing=update_time_timezone(datetime.datetime.fromisoformat(body.get("last_parsing"))),
                        session_id=None,
                        settings=None,
                        taken=0,
                        error_message=error_message,
                    )
                )
                result_ban_ids.append(body.get("id"))
            else:
                result_ok.append(
                    Sessions(
                        id=body.get("id"),
                        last_parsing=update_time_timezone(datetime.datetime.fromisoformat(body.get("last_parsing"))),
                        taken=0,
                        settings=body.get("settings"),
                        session_id=body.get("session_id"),
                        is_active=1,
                        error_message="ok",
                    )
                )
            # result.append(
            #     Sessions(
            #         id=body.get("id"),
            #         last_parsing=datetime.datetime.fromisoformat(body.get("last_parsing")),
            #         taken=0,
            #         is_active=not body.get("banned"),
            #     )
            # )
            # if len(result) > 10:
            #     django.db.close_old_connections()
            #     Sessions.objects.bulk_update(result, ['last_parsing', 'taken', 'is_active'], batch_size=200)
            #     result.clear()
            if len(result_ok) > 0:
                django.db.close_old_connections()
                Sessions.objects.bulk_update(result_ok, ['last_parsing', 'taken', 'is_active', 'error_message', 'session_id', 'settings'], batch_size=200)
                result_ok.clear()
            if len(result_ban) > 0:
                django.db.close_old_connections()
                Sessions.objects.bulk_update(result_ban, ['last_parsing', 'taken', 'session_id',  'error_message', 'settings'], batch_size=200)
                Sessions.objects.filter(id__in=result_ban_ids).update(is_active=F('is_active') + 1)
                result_ban_ids.clear()
                result_ban.clear()
        except Exception as e:
            print(f"callback{e}")
            django.db.close_old_connections()

    channel.basic_consume(queue='insta_source_ig_session_parse', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    read_sessions()
