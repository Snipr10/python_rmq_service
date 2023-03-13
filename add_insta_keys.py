import json

import os
import datetime
import time

from django.db.models import Q
from django.utils import timezone
import django.db

from utils import get_chanel, update_time_timezone


def add_keys_while():
    while True:
        try:
            add_keys()
        except Exception:
            time.sleep(10)


def add_keys():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_rmq_service.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    import django

    django.setup()
    import pymysql

    pymysql.install_as_MySQLdb()
    from core.models import Sources, KeywordSource, Keyword
    from django.forms.models import model_to_dict

    channel = get_chanel()

    Keyword.objects.filter(network_id=7, taken=1).update(taken=0)

    while True:
        try:
            for k in Keyword.objects.filter(network_id=7, enabled=1, disabled=0):
                if len(k) > 20 and len(k.split(" ")) > 4:
                    k.disabled = 1
                    k.save(update_fields=["disabled"])
        except Exception as e:
            print(e)
        try:
            res = channel.queue_declare(
                queue='insta_source_parse_key',
            )
            print('Messages in queue Key %d' % res.method.message_count)
            # TODO
            if res.method.message_count < 10:
                select_sources = Sources.objects.filter(
                    Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
                    status=1)

                key_source = KeywordSource.objects.filter(
                    source_id__in=list(select_sources.values_list('id', flat=True)))
                #
                # Keyword.objects.filter(network_id=7, enabled=1, taken=0,
                #                        id__in=list(key_source.values_list('keyword_id', flat=True)),
                #                        last_modified__isnull=True,
                #                        ).update(last_modified=datetime.date(1999, 1, 1))

                key_words = Keyword.objects.filter(network_id=7, enabled=1, taken=0, disabled=0,
                                                   id__in=list(key_source.values_list('keyword_id', flat=True)),
                                                   last_modified__gte=datetime.date(1999, 1, 1),
                                                   ).order_by('last_modified')

                if len(key_words) == 0:
                    time.sleep(5 * 60)
                    continue
                key_words_ids = []
                for key_word in key_words[:100]:
                    body = model_to_dict(key_word)
                    try:
                        if body['created_date']:
                            body['created_date'] = body['created_date'].isoformat()
                    except Exception:
                        pass
                    try:
                        if body['modified_date']:
                            body['modified_date'] = body['modified_date'].isoformat()
                    except Exception:
                        pass
                    try:
                        if body['last_modified']:
                            body['last_modified'] = body['last_modified'].isoformat()
                    except Exception:
                        pass
                    try:
                        if body['depth']:
                            body['depth'] = body['depth'].isoformat()
                    except Exception:
                        pass

                    channel.basic_publish(exchange='',
                                          routing_key='insta_source_parse_key',
                                          body=json.dumps(body))
                    key_word.taken = 1
                    key_words_ids.append(key_word)
                Keyword.objects.bulk_update(key_words_ids, ['taken'],
                                            batch_size=200)
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
    add_keys()
