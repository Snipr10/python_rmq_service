import json

import os
import datetime

from utils import get_chanel, update_time_timezone
from django.db.models import Q
from django.utils import timezone

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
    from core.models import Sources, SourcesItems

    channel = get_chanel()
    res = channel.queue_declare(
        queue='insta_test',
        durable=True,
        exclusive=False,
        auto_delete=False,
        passive=True
    )
    while True:
        channel.queue_declare(queue='insta_test')

        print('Messages in queue %d' % res.method.message_count)
        # TODO
        if res.method.message_count < 10:
            print(123)
            select_sources = Sources.objects.filter(
                Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
                status=1)
            print(select_sources)
            sources_items = SourcesItems.objects.filter(
                network_id=3,
                disabled=0,
                taken=0,
                source_id__in=list(select_sources.values_list('id', flat=True))
                                                        ).order_by('last_modified')
            print(sources_items)

            for sources_item in sources_items:
                print(sources_item)
                time_s = select_sources.get(id=sources_item.source_id).sources
                if time_s is None:
                    time_s = 0

                if sources_item.last_modified is None or (
                        sources_item.last_modified + datetime.timedelta(minutes=time_s) <
                        update_time_timezone(timezone.localtime())):
                    channel.basic_publish(exchange='',
                                          routing_key='insta_test',
                                          body=json.dumps({
                                              "text": sources_item.id,
                                          }))
