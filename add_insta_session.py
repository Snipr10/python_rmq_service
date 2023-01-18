import json

import os
import datetime
import time
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from utils import get_chanel, update_time_timezone

if __name__ == "__main__":
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

    while True:
        res = channel.queue_declare(
            queue='insta_source_ig_session_new',
        )
        print('Messages in queue %d' % res.method.message_count)
        # TODO
        if res.method.message_count < 10:
            select_sessions = Sessions.objects.filter(
                Q(last_parsing__isnull=True) | Q(last_parsing__lte=update_time_timezone(
                    timezone.localtime()) - timedelta(minutes=5)), taken=0)
            print(f"select_sources {select_sessions}")
            proxy_ids = []
            for session in select_sessions[:100]:
                proxy_ids.append(session.proxy_id)
            proxyies_select = AllProxy.objects.filet(id__in=proxy_ids)
            sessions_id = []
            for session in select_sessions[:100]:

                print(model_to_dict(session))
                body = model_to_dict(session)
                if body['start_parsing']:
                    body['start_parsing'] = body['start_parsing'].isoformat()
                if body['last_parsing']:
                    body['last_parsing'] = body['last_parsing'].isoformat()
                proxy = proxy_ids.get(id=body['proxy_id'])
                body['proxy_ip'] = proxy.ip
                body['proxy_port'] = proxy.port
                body['proxy_login'] = proxy.login
                body['proxy_pass'] = proxy.proxy_password

                print(body)
                channel.basic_publish(exchange='',
                                      routing_key='insta_source_ig_session_new',
                                      body=json.dumps(body))
                session.taken = 1
                session.start_parsing = update_time_timezone(timezone.localtime())
                sessions_id.append(session)
            Sessions.objects.bulk_update(sessions_id, ['taken', 'start_parsing'],
                                         batch_size=200)
            time.sleep(60)
