import os
import time


def update_while():
    while True:
        try:
            update()
        except Exception:
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

    Sessions.objects.filter(taken=1).update(taken=0)
    Keyword.objects.filter(network_id=7, taken=1).update(taken=0)
    SourcesItems.objects.filter(taken=1, network_id=7).update(taken=0)


if __name__ == "__main__":
    update()
