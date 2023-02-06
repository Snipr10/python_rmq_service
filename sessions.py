import os
import time

from instagrapi import Client




def update_session_id_while():
    while True:
        try:
            update_session_id()
        except Exception:
            time.sleep(30 * 60)


def update_session_id():
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
    from core.models import Sessions, AllProxy
    from core.models import Bot
    from utils import update_time_timezone
    from django.utils import timezone

    sessions = list(Sessions.objects.all().values_list('login', flat=True))
    print(sessions)
    for s in Sessions.objects.filter(session_id__isnull=True, is_active__lte=20):
        try:
            proxy = AllProxy.objects.filter(port__in=[30001, 30010]).order_by('?')[0]
            cl = Client(
                proxy=f"http://{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}",
            )

            cl.login(s.login, s.password)
            s_id = cl.authorization_data['sessionid']
            s.is_active = 1
            s.session_id = s_id
            s.save()
        except Exception as e:
            s.is_active += 1
            s.save()
            print(f"{s.login} {e} {proxy.id}")

    # for b in Bot.objects.filter(nework=7, banned=0):
    #     if b.login not in sessions:
    #         try:
    #             proxy = AllProxy.objects.filter(port__in=[30001, 30010]).order_by('?')[0]
    #             cl = Client(
    #                 proxy=f"http://{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}",
    #             )
    #             cl.login(b.login, b.password)
    #             Sessions.objects.create(
    #                 login=b.login,
    #                 password=b.password,
    #                 start_parsing=update_time_timezone(timezone.localtime()),
    #                 last_parsing=update_time_timezone(timezone.localtime()),
    #                 is_active=1,
    #                 taken=0,
    #                 proxy_id=proxy.id,
    #                 session_id=cl.authorization_data['sessionid']
    #             )
    #             print(f"Created {b.login}")
    #
    #         except Exception as e:
    #             print(f"Bot session {e} {b.login} {proxy.id}")
    #             pass


if __name__ == '__main__':
    while True:
        try:
            update_session_id()
        except Exception:
            time.sleep(5 * 60)

