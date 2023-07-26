import datetime
import json
import os
import random
import time
from django.db.models import Q
from instagrapi import Client
import random
import requests

def update_while_session():
    while True:
        try:
            print("update_while")
            update()
        except Exception as e:
            print(f"update_while {e}")
            time.sleep(10)
        time.sleep(1 * 60)

def update_new_while_session():
    while True:
        try:
            print("update_while")
            update_new()
        except Exception as e:
            print(f"update_while {e}")
            time.sleep(10)
        time.sleep(1 * 60)

def challenge_code_handler(username, choice):
    from instagrapi.mixins.challenge import ChallengeChoice
    if choice == ChallengeChoice.SMS:
        return None
    elif choice == ChallengeChoice.EMAIL:
        return None
    return False


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
    import django.db

    django.setup()
    import pymysql
    import django.db
    from utils import update_time_timezone
    from django.utils import timezone

    pymysql.install_as_MySQLdb()
    from core.models import Sessions, Keyword, SourcesItems, Sources, KeywordSource, AllProxy, IgProxyBanned
    django.db.close_old_connections()

    i = 0
    for s in Sessions.objects.filter(is_active__lte=19, settings__isnull=True).order_by("-id")[:10]:
        eror = "not ok"
        i += 1
        print(i)
        print(s.id)
        if s.old_settings is not None:
            print("old_settings")
            if "authorization_data" in str(s.old_settings):
                try:
                    sessings_cook = s.old_settings
                    try:
                        sessings_cook = json.loads(str(s.old_settings.replace("'", '"')))

                    except Exception  as e:
                        print(f"sessings_cook 1 {e}")
                        try:
                            print(str(s.old_settings))
                            sessings_cook = json.loads(str(s.old_settings))

                        except Exception as e:
                            print(f"sessings_cook 2 {e}")

                    cl = Client(
                        proxy="http://tools-admin_metamap_com:456f634698@193.142.249.56:30001",
                        settings=sessings_cook
                    )
                    cl.challenge_code_handler = challenge_code_handler

                    message = cl.private.get(
                        'https://i.instagram.com/api/v1/fbsearch/search_engine_result_page/',
                        params={'query': "бассейн", 'next_max_id': None},
                        proxies=cl.private.proxies
                    ).json().get('message')

                    if message is not None:
                        raise Exception(message)

                    s.error_message = "ok"
                    settings = cl.get_settings()
                    settings["authorization_data"] = cl.authorization_data
                    settings["cookies"] = {
                        "sessionid": cl.authorization_data["sessionid"]
                    }
                    s.settings = json.dumps(settings)

                    s.is_active = 1
                    django.db.close_old_connections()

                    s.save(update_fields=["settings", "is_active", "error_message"])
                    continue
                except Exception as e:
                    eror = str(e)
                    print(f"old_settings {e}")
        if s.old_session_id:
            try:
                print("old_session_id 1")

                cl = Client(
                    proxy="http://tools-admin_metamap_com:456f634698@193.142.249.56:30001",
                )
                cl.challenge_code_handler = challenge_code_handler
                cl.login_by_sessionid(
                    s.old_session_id)
                message = cl.private.get(
                    'https://i.instagram.com/api/v1/fbsearch/search_engine_result_page/',
                    params={'query': "бассейн", 'next_max_id': None},
                    proxies=cl.private.proxies
                ).json().get('message')

                if message is not None:
                    raise Exception(message)

                settings = cl.get_settings()
                settings["authorization_data"] = cl.authorization_data
                settings["cookies"] = {
                    "sessionid": cl.authorization_data["sessionid"]
                }
                s.settings = json.dumps(settings)
                s.error_message = "ok"
                s.old_settings = json.dumps(settings)

                s.is_active = 1
                django.db.close_old_connections()
                s.save(update_fields=["settings", "is_active", "error_message", "old_settings"])
                continue
            except Exception as e:
                eror = str(e)
                print(f"old_session_id {e}")
        if s.login is not None and s.password is not None:
            try:
                cl = Client(
                    proxy="http://tools-admin_metamap_com:456f634698@193.142.249.56:30001",
                )
                cl.challenge_code_handler = challenge_code_handler
                cl.login(s.login, s.password)

                message = cl.private.get(
                    'https://i.instagram.com/api/v1/fbsearch/search_engine_result_page/',
                    params={'query': "бассейн", 'next_max_id': None},
                    proxies=cl.private.proxies
                ).json().get('message')

                if message is not None:
                    raise Exception(message)

                settings = cl.get_settings()
                settings["authorization_data"] = cl.authorization_data
                settings["cookies"] = {
                    "sessionid": cl.authorization_data["sessionid"]
                }
                s.settings = json.dumps(settings)
                s.old_settings = json.dumps(settings)
                s.is_active = 1
                s.error_message = "ok"
                django.db.close_old_connections()
                s.save(update_fields=["settings", "is_active", "error_message", "old_settings"])
                continue
            except Exception as e:
                eror = str(e)
                print(f"login {e}")
                s.is_active = 20
                s.settings = None
                s.error_message = eror
                s.save()
        django.db.close_old_connections()
        s.settings = None
        s.error_message = eror
        s.is_active = 20
        s.save()


def update_new():
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
    import django.db

    django.setup()
    import pymysql
    import django.db
    from utils import update_time_timezone
    from django.utils import timezone

    pymysql.install_as_MySQLdb()
    from core.models import Sessions, Keyword, SourcesItems, Sources, KeywordSource, AllProxy, IgProxyBanned
    django.db.close_old_connections()
    proxies = [
        "bxxkro3bt05zq96wi0gnv9b:RNW78Fm5@fast.froxy.com:10000",
        "8qevqqam4dgm9ibix83i1mr:RNW78Fm5@fast.froxy.com:10000",
        "p48gtd0e12otayal34e7ueb:RNW78Fm5@fast.froxy.com:10000",
        "1rstkmb0mdzqgakkxkhvq6e:RNW78Fm5@fast.froxy.com:10000",
        "npvxw6bb5xdgbrd5vsaolhr:RNW78Fm5@fast.froxy.com:10000",
    ]
    i = 0

    for s in Sessions.objects.filter(is_active__gte=19, is_active__lte=23, error_message__contains="wait a few minutes before you try").order_by("is_active","-id")[:10]:
        try:
            print(f"{s.id} : {proxies[i]}")
            cl = Client(
                proxy=f"http://{proxies[i]}")

            cl.challenge_code_handler = challenge_code_handler
            cl.login(s.login, s.password)

            settings = cl.get_settings()
            settings["authorization_data"] = cl.authorization_data
            settings["cookies"] = {
                "sessionid": cl.authorization_data["sessionid"]
            }
            s.settings = str(settings)
            s.old_settings = json.dumps(settings)
            s.is_active = 1
            s.error_message = "ok"
            django.db.close_old_connections()
            s.save(update_fields=["settings", "is_active", "error_message", "old_settings"])
        except Exception as e:
            s.is_active = s.is_active +1
            s.error_message = str(e)
            django.db.close_old_connections()
            s.save(update_fields=["is_active", "error_message"])
            print(f"{s.id} : {e}")

            i += 1
            if len(proxies) == i:
                i = 0
