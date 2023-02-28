import os
import time
import random

import requests
from instagrapi import Client
from random import randint
from time import sleep


def update_session_id_while():
    while True:
        try:
            update_session_id()
        except Exception:
            time.sleep(30 * 60)
        time.sleep(30 * 60)

def challenge_code_handler(username, choice):
    from instagrapi.mixins.challenge import ChallengeChoice
    if choice == ChallengeChoice.SMS:
        return None
    elif choice == ChallengeChoice.EMAIL:
        return None
    return False

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
    import django.db

    sessions = list(Sessions.objects.all().values_list('login', flat=True))
    print(sessions)

    try:
        accounts = Sessions.objects.filter()
        proxies_set = set()
        for a in accounts:
            proxies_set.add(a.proxy_id)
        proxies_list = list(proxies_set)
        print(f"proxies_list {proxies_list}")
        work_proxy = []
        work_proxy_ids = []
        proxy_candidates = AllProxy.objects.filter(ip__in=[30001, 30011, 30010])
        for can in proxy_candidates:
            try:
                proxy_str = ""
                proxy_str = f"{can.login}:{can.proxy_password}@{can.ip}:{can.port}"
                proxies = {'https': f'http://{proxy_str}'}
                if requests.get("https://www.instagram.com/", proxies=proxies, timeout=10).ok:
                    work_proxy.append(can)
                    work_proxy_ids.append(can.id)

            except Exception as e:
                print(f"{proxy_str} {e}")
        print(f"work_proxy {work_proxy}")
        print(f"work_proxy_ids {work_proxy_ids}")

        exist_proxy = AllProxy.objects.filter(id__in=proxies_list)
        for e_p in exist_proxy:
            try:
                proxy_str = ""
                proxy_str = f"{e_p.login}:{e_p.proxy_password}@{e_p.ip}:{e_p.port}"
                proxies = {'https': f'http://{proxy_str}'}
                if requests.get("https://www.instagram.com/", proxies=proxies, timeout=10).ok:
                    work_proxy.append(e_p)
                    work_proxy_ids.append(e_p.id)
            except Exception as e:
                print(f"{proxy_str} {e}")
        print(f"work_proxy {work_proxy}")
        print(f"work_proxy_ids {work_proxy_ids}")
        for a in accounts:
            if a.proxy_id not in work_proxy_ids:
                a.proxy_id = random.choice(work_proxy_ids)
                a.save(update_fields=["proxy_id"])
                print(f"account {a}")
    except Exception as e:
        print(e)


    django.db.close_old_connections()

    for s in Sessions.objects.filter(session_id__isnull=True, is_active__lte=20):

        sleep(randint(35, 150))

        try:
            if random.choice([True, False]):
                proxy = AllProxy.objects.filter(port__in=[30001, 30010]).order_by('?')[0]
            else:
                try:
                    proxy = AllProxy.objects.filter(id=s.proxy_id)[0]
                except Exception:
                    proxy = AllProxy.objects.filter(port__in=[30001, 30010]).order_by('?')[0]

            cl = Client(
                proxy=f"http://{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}",
            )
            cl.challenge_code_handler = challenge_code_handler

            cl.login(s.login, s.password)
            s_id = cl.authorization_data['sessionid']
            s.is_active = 1
            s.proxy_id = proxy.id
            s.session_id = s_id
            s.old_session_id = s_id
            s.error_message = ""
            django.db.close_old_connections()
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

