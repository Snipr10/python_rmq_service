import ast
import json

import os
import datetime
import time
from datetime import timedelta
import django.db

from django.db.models import Q
from django.utils import timezone

from utils import get_chanel, update_time_timezone


def add_sessions_while():
    while True:
        try:
            add_sessions()
        except Exception:
            time.sleep(10)


def add_sessions():
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
    from core.models import Sources, AllProxy, Keyword, Sessions
    from django.forms.models import model_to_dict

    channel = get_chanel()
    Sessions.objects.filter(taken=1).update(taken=0)

    while True:
        try:
            res = channel.queue_declare(
                queue='insta_source_ig_session_new',
            )
            print('Messages in queue session %d' % res.method.message_count)
            # print(update_time_timezone(
            #             timezone.localtime()) - timedelta(minutes=5))
            # TODO
            if res.method.message_count < 10:
                print("try add")
                # select_sessions = Sessions.objects.filter(
                #     Q(last_parsing__isnull=True) | Q(last_parsing__lte=update_time_timezone(
                #         timezone.localtime()) - timedelta(minutes=5)),
                #     Q(start_parsing__isnull=True) | Q(start_parsing__lte=update_time_timezone(
                #         timezone.localtime()) - timedelta(minutes=5)),
                #     taken=0, is_active__lte=10, session_id__isnull=False).order_by("last_parsing")
                select_sessions = Sessions.objects.filter(
                    Q(last_parsing__isnull=True) | Q(last_parsing__lte=update_time_timezone(
                        timezone.localtime()) - timedelta(minutes=5)),
                    Q(start_parsing__isnull=True) | Q(start_parsing__lte=update_time_timezone(
                        timezone.localtime()) - timedelta(minutes=5)),
                    taken=0, is_active__lte=10, settings__isnull=False, proxy_id__isnull=False).order_by("last_parsing")
                proxy_ids = []
                for session in select_sessions[:100]:
                    proxy_ids.append(session.proxy_id)
                print(select_sessions)
                proxyies_select = AllProxy.objects.filter(id__in=proxy_ids)
                sessions_id = []
                for session in select_sessions[:100]:
                    try:
                        print(session.id)
                        body = model_to_dict(session)
                        if body['start_parsing']:
                            body['start_parsing'] = body['start_parsing'].isoformat()

                        if body['last_parsing']:
                            body['last_parsing'] = body['last_parsing'].isoformat()

                        proxy = proxyies_select.get(id=body['proxy_id'])
                        body['proxy_ip'] = proxy.ip
                        body['proxy_port'] = proxy.port
                        body['proxy_login'] = proxy.login
                        body['proxy_pass'] = proxy.proxy_password

                        if body.get("settings"):
                            try:
                                body['settings'] = ast.literal_eval(body.get("settings"))
                            except Exception:
                                body['settings'] = json.loads(body.get("settings"))


                        channel.basic_publish(exchange='',
                                              routing_key='insta_source_ig_session_new',
                                              body=json.dumps(body))
                        session.taken = 1
                        session.start_parsing = update_time_timezone(timezone.localtime())
                        sessions_id.append(session)
                    except Exception as e:
                        print(e)
                        session.error_message = f"proxy {session.proxy_id} {str(e)}"
                        session.proxy_id = None
                        session.save()
                Sessions.objects.bulk_update(sessions_id, ['taken', 'start_parsing'],
                                             batch_size=200)
                time.sleep(60)
            else:
                time.sleep(2 * 60)
        except Exception as e:


            try:
                print(e)
                try:
                    channel.stop_consuming()
                except Exception:
                    pass
                channel = get_chanel()
                django.db.close_old_connections()
            except Exception as e:
                print(e)

if __name__ == "__main__":
    add_sessions()
