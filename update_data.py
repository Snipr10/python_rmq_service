import os
import random
import time


def update_while():
    while True:
        try:
            print("update_while")
            update()
        except Exception as e:
            print(f"update_while {e}")
            time.sleep(10)
        time.sleep(15*60)


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

    pymysql.install_as_MySQLdb()
    from core.models import Sessions, Keyword, SourcesItems
    django.db.close_old_connections()

    Keyword.objects.filter(network_id=7, taken=1).update(taken=0)
    SourcesItems.objects.filter(taken=1, network_id=7).update(taken=0)
    Sessions.objects.filter(is_active__lte=10, taken=1).update(taken=0)
    #
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
