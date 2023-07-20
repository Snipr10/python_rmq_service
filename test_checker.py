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
        time.sleep(5 * 60)


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

    django.setup()
    import pymysql
    import django.db
    from utils import update_time_timezone
    from django.utils import timezone

    pymysql.install_as_MySQLdb()
    from core.models import Sessions, Keyword, SourcesItems, Sources, KeywordSource, AllProxy, IgProxyBanned
    django.db.close_old_connections()

    i = 0
    for s in Sessions.objects.filter(is_active__lte=19, settings__isnull=True).order_by("-id"):
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
                s.save(update_fields=["settings", "is_active", "error_message", "old_settings"])
                continue
            except Exception as e:
                eror = str(e)
                print(f"login {e}")
                s.is_active = 20
                s.settings = None
                s.error_message = eror
                s.save()
        s.settings = None
        s.error_message = eror
        s.is_active = 20
        s.save()


# update()
