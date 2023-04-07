import json

import os
import datetime
import time

from django.db.models import Q
from django.utils import timezone
import django.db

from utils import get_chanel, update_time_timezone


def add_tasks_while():
    while True:
        try:
            add_tasks()
        except Exception:
            time.sleep(10)


def add_tasks():
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
    from core.models import Sources, SourcesItems
    from django.forms.models import model_to_dict

    channel = get_chanel()

    SourcesItems.objects.filter(taken=1, network_id=7).update(taken=0)

    while True:
        try:
            res = channel.queue_declare(
                queue='insta_source_parse',
            )
            print('Messages in queue tasks %d' % res.method.message_count)
            # TODO
            if res.method.message_count < 10:
                print(1)
                select_sources = Sources.objects.filter(
                    Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
                    status=1)
                print(2)
                sources_items = SourcesItems.objects.filter(
                    network_id=7,
                    disabled=0,
                    taken=0,
                    source_id__in=list(select_sources.values_list('id', flat=True))
                ).order_by('last_modified')
                print(3)
                if len(sources_items) == 0:
                    time.sleep(5 * 60)
                    continue
                source_ids = []
                for sources_item in sources_items[:100]:
                    print(4)

                    time_s = select_sources.get(id=sources_item.source_id).sources
                    if time_s is None:
                        time_s = 0
                    print(5)

                    if sources_item.last_modified is None or (
                            sources_item.last_modified + datetime.timedelta(minutes=time_s) <
                            update_time_timezone(timezone.localtime())):
                        body = model_to_dict(sources_item)
                        body['last_modified'] = body['last_modified'].isoformat()
                        channel.basic_publish(exchange='',
                                              routing_key='insta_source_parse',
                                              body=json.dumps(body))
                    sources_item.taken = 1
                    source_ids.append(sources_item)
                    print(6)
                print(7)
                SourcesItems.objects.bulk_update(source_ids, ['taken'],
                                                 batch_size=200)
                print(8)
                time.sleep(60)
            else:
                time.sleep(5 * 60)
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
    add_tasks()
