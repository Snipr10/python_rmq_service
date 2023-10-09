import datetime
import json
import os
import random
import time
from django.db.models import Q
from instagrapi import Client
import random
import requests
from django.db.models import F
def get_proxy():
    from core.models import Sources, SourcesItems, Sessions, AllProxy

    pro = []
    for p in AllProxy.objects.filter(Q(port=30001) | Q(port=8000)):
        try:
            proxy = f'http://{p.login}:{p.proxy_password}@{p.ip}:{p.port}'
            if requests.get("https://www.instagram.com/",
                            proxies = { 'https' : proxy}
                            ).ok:
                pro.append((proxy, p.id))
        except Exception:
            pass
    return pro
def sessions_start():

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
    import random

    pymysql.install_as_MySQLdb()
    from core.models import Sources, SourcesItems, Sessions, AllProxy
    from django.forms.models import model_to_dict

    # p = "DduuwE:XfUCU6@45.157.36.96:8000"
    from instagrapi import Client
    i = 0
    while True:
        try:
            proxy = get_proxy()
            if len(proxy) == 0:
                return
            print(proxy)
            for s in Sessions.objects.filter(settings__isnull=True, is_active__lte=5, proxy_id__isnull=True).order_by('-id'):
                i += 1
                if i > 50:
                    break
                s.is_active += 1
                s.save()
                po = random.choice(proxy)
                p_id = po[1]
                p = po[0]
                print(p_id)
                print(p)
                try:

                    print(s.id)
                    cl = Client(
                        proxy=f"http://" + p,
                        settings=s.old_settings
                    )
                    print(1)
                    cl.account_info()
                    s.settings = s.old_settings
                    settings = cl.get_settings()

                    settings["authorization_data"] = cl.authorization_data
                    settings["cookies"] = {
                        "sessionid": cl.authorization_data["sessionid"]
                    }
                    s.settings = json.dumps(settings)
                    s.is_active = 1
                    s.proxy_id = p_id
                    s.save()
                    continue
                except Exception as e:
                    try:
                        cl = Client(
                            proxy=f"http://" + p,
                        )
                        print(2)
                        try:
                            cl.login_by_sessionid(s.old_session_id)
                        except Exception:
                            pass
                        print(3)

                        cl.login(s.login, s.password, relogin=True)
                        print(4)

                        cl.account_info()
                        print(5)

                        settings = cl.get_settings()

                        settings["authorization_data"] = cl.authorization_data
                        settings["cookies"] = {
                            "sessionid": cl.authorization_data["sessionid"]
                        }
                        s.settings = json.dumps(settings)
                        s.error_message = "ok"
                        s.old_settings = json.dumps(settings)
                        s.is_active = 1
                        s.proxy_id = p_id
                        s.save()
                    except Exception as e:
                        print(e)
        except Exception as e:
                print(e)