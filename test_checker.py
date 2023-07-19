import datetime
import os
import random
import time
from django.db.models import Q
from instagrapi import Client
import random
import requests


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
    for s in Sessions.objects.filter():
        eror = "not ok"
        i += 1
        print(i)
        if s.old_settings is not None:
            if "authorization_data" in s.old_settings:
                try:
                    cl = Client(
                        proxy="http://tools-admin_metamap_com:456f634698@193.142.249.56:30001",
                        settings=s.old_settings
                    )
                    cl.challenge_code_handler = challenge_code_handler

                    print(cl.user_id_from_username('anya_grad'))
                    s.settings = s.old_settings
                    s.is_active = 1
                    s.save()
                    continue
                except Exception as e:
                    eror = str(e)
                    print(f"old_settings {e}")
        if s.old_session_id:
            try:
                cl = Client(
                    proxy="http://tools-admin_metamap_com:456f634698@193.142.249.56:30001",
                )
                cl.challenge_code_handler = challenge_code_handler
                cl.login_by_sessionid(
                    s.old_session_id)
                print(cl.user_id_from_username('anya_grad'))

                settings = cl.get_settings()
                settings["authorization_data"] = cl.authorization_data
                settings["cookies"] = {
                    "sessionid": cl.authorization_data["sessionid"]
                }
                s.settings = settings
                s.old_settings = settings
                s.is_active = 1
                s.save()
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
                print(cl.user_id_from_username('anya_grad'))

                settings = cl.get_settings()
                settings["authorization_data"] = cl.authorization_data
                settings["cookies"] = {
                    "sessionid": cl.authorization_data["sessionid"]
                }
                s.settings = settings
                s.old_settings = settings
                s.is_active = 1
                s.save()
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


update()
