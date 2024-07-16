import json

import os
import datetime
import time

from django.db.models import Q
from django.utils import timezone
import django.db

from utils import get_chanel, update_time_timezone
import pika


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
    from core.models import Sources, KeywordSource, Keyword, SourcesSpecial
    from django.forms.models import model_to_dict

    channel = get_chanel()

    Keyword.objects.filter(network_id=7, taken=1).update(taken=0)

    while True:
        try:
            django.db.close_old_connections()

            for k in Keyword.objects.filter(network_id=7, disabled=0,
                                            last_modified__gte=datetime.date(1999, 1, 1),
                                            id__in=(13082527,
                                                    13082528,
                                                    13082529,
                                                    13082530,
                                                    13082531,
                                                    13082532,
                                                    13082533,
                                                    13082534,
                                                    13082535,
                                                    13082554,
                                                    13082555,
                                                    13082556,
                                                    13082557,
                                                    13082558,
                                                    13082559,
                                                    13082560,
                                                    13082561,
                                                    13082562,
                                                    13082563,
                                                    13082564,
                                                    13082565,
                                                    13082566,
                                                    13082567,
                                                    13082568,
                                                    13082569,
                                                    13082570,
                                                    13082571,
                                                    13083148,
                                                    13083149,
                                                    13083150,
                                                    13083151,
                                                    13083152,
                                                    13083153,
                                                    13083154,
                                                    13083155,
                                                    13083156,
                                                    13083157,
                                                    13083158,
                                                    13083159,
                                                    13083160,
                                                    13083161,
                                                    13083162,
                                                    13083163,
                                                    13083164,
                                                    13083165,
                                                    13083166,
                                                    13083167,
                                                    13083168,
                                                    13083169,
                                                    13083170,
                                                    13083171,
                                                    13083172,
                                                    13083173,
                                                    13083174,
                                                    )
                                            ):
                if len(k.keyword) > 20 and len(k.keyword.split(" ")) >= 4:
                    print(k.keyword)
                    k.disabled = 1
                    k.save(update_fields=["disabled"])
        except Exception as e:
            print(f"Keyword {e}")
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

                last_hour_keys_ids = list(Keyword.objects.filter(network_id=7, disabled=0,
                                                                 last_modified__lte=datetime.datetime.now() - datetime.timedelta(
                                                                     minutes=60)
                                                                 ).values_list('id', flat=True))

                source_special = SourcesSpecial.objects.filter(keyword_id__in=last_hour_keys_ids)
                key_words = []
                if len(source_special) == 0:

                    key_source = KeywordSource.objects.filter(
                        source_id__in=list(select_sources.values_list('id', flat=True)))

                    key_words = Keyword.objects.filter(network_id=7, taken=0, disabled=0,
                                                       id__in=list(key_source.values_list('keyword_id', flat=True)),
                                                       last_modified__gte=datetime.date(1999, 1, 1),
                                                       ).order_by('-last_modified')
                    key_words = list(key_words)

                if len(key_words) < 50:
                    key_words_non_s = Keyword.objects.filter(network_id=7, taken=0, disabled=0,
                                                       id__in=list(source_special.values_list('keyword_id', flat=True)),
                                                       last_modified__gte=datetime.date(1999, 1, 1),
                                                       ).order_by('-last_modified')
                    key_words.extend(list(key_words_non_s))
                if len(key_words) == 0:
                    time.sleep(1 * 60)
                    continue
                # elif len(key_words) < 5:
                #     key_words = list(key_words)
                #     key_words.extend(key_words)
                #     key_words.extend(key_words)

                key_words_ids = []

                for key_word in key_words[:50]:
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
                                          properties=pika.BasicProperties(
                                              expiration='300000',
                                          ),
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
