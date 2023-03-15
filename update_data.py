import os
import random
import time
from django.db.models import Q


def update_while():
    while True:
        try:
            print("update_while")
            update()
        except Exception as e:
            print(f"update_while {e}")
            time.sleep(10)
        time.sleep(15 * 60)


def update():
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
    import django.db
    from utils import update_time_timezone
    from django.utils import timezone

    pymysql.install_as_MySQLdb()
    from core.models import Sessions, Keyword, SourcesItems, Sources, KeywordSource
    django.db.close_old_connections()
    try:
        Keyword.objects.filter(network_id=7, taken=1).update(taken=0)
    except Exception as e:
        print(f"Keyword update {e}")
    try:
        SourcesItems.objects.filter(taken=1, network_id=7).update(taken=0)
    except Exception as e:
        print(f"SourcesItems update {e}")
    try:

        Sessions.objects.filter(is_active__lte=10, taken=1).update(
            taken=0,
            start_parsing=update_time_timezone(timezone.localtime()),
            last_parsing=update_time_timezone(timezone.localtime()),
        )
    except Exception as e:
        print(f"Sessions update {e}")
    try:
        select_sources = Sources.objects.filter(published=1, status=1)

        key_source = KeywordSource.objects.filter(
            source_id__in=list(select_sources.values_list('id', flat=True)))

        Keyword.objects.filter(network_id=7, enabled=1, taken=0, disabled=0) \
            .exclude(id__in=list(key_source.values_list('keyword_id', flat=True))).update(disabled=1)
    except Exception as e:
        print(f"key_source update {e}")
    try:
        select_sources = Sources.objects.filter(published=1,
                                                status=1)
        sources_items = SourcesItems.objects.filter(network_id=7,
                                                    disabled=0,
                                                    ).exclude(
            source_id__in=list(select_sources.values_list('id', flat=True)))

        sources_items.update(disabled=1)

    except Exception as e:
        print(f"sources_items update {e}")
    # proxy_ids = []
    # for s in Sessions.objects.all():
    #     proxy_ids.append(s.proxy_id)
    # for s in Sessions.objects.filter(is_active__gte=10):
    #     s.proxy_id = random.choice(proxy_ids)
    #     s.taken = 0
    #     s.is_active = 1
    #     s.save()
    # Sessions.objects.filter(taken=1).update(taken=0, is_active=1)


if __name__ == "__main__":
    update()
