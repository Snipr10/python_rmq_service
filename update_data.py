import datetime
import os
import random
import time
from django.db.models import Q
from instagrapi import Client
import random
import requests

def update_while():
    while True:
        try:
            print("update_while")
            update()
        except Exception as e:
            print(f"update_while {e}")
            time.sleep(10)
        time.sleep(5 * 60)


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
    try:
        print("Keyword")
        Keyword.objects.filter(network_id=7, taken=1).update(taken=0)
    except Exception as e:
        print(f"Keyword update {e}")
    try:
        print("SourcesItems")
        SourcesItems.objects.filter(taken=1, network_id=7).update(taken=0)
    except Exception as e:
        print(f"SourcesItems update {e}")
    try:
        print("Sessions")
        Sessions.objects.filter(is_active__lte=10, taken=1).update(
            taken=0,
            start_parsing=update_time_timezone(timezone.localtime()),
            last_parsing=update_time_timezone(timezone.localtime()),
        )
    except Exception as e:
        print(f"Sessions update {e}")
    try:
        print("select_sources")
        select_sources = Sources.objects.filter(published=1, status=1)

        key_source = KeywordSource.objects.filter(
            source_id__in=list(select_sources.values_list('id', flat=True)))

        Keyword.objects.filter(network_id=7, enabled=1, taken=0, disabled=0) \
            .exclude(id__in=list(key_source.values_list('keyword_id', flat=True))).update(disabled=1)
    except Exception as e:
        print(f"key_source update {e}")
    try:
        print("select_sources")
        select_sources = Sources.objects.filter(published=1,
                                                status=1)
        sources_items = SourcesItems.objects.filter(network_id=7,
                                                    disabled=0,
                                                    ).exclude(
            source_id__in=list(select_sources.values_list('id', flat=True)))

        sources_items.update(disabled=1)

    except Exception as e:
        print(f"sources_items update {e}")
    # try:
    #     print("proxies_select")
    #
    #     proxies_select = AllProxy.objects.filter(Q(
    #         port__in=[30001, 30010, 30011, 8000]) | Q(login="sega364pd")
    #     # ).exclude(
    #     #     id__in=IgProxyBanned.objects.all().values_list('id', flat=True)
    #                                              )
    #     proxies_ig_ids = []
    #     for can in proxies_select:
    #         proxy_str = ""
    #         try:
    #             proxy_str = f"{can.login}:{can.proxy_password}@{can.ip}:{can.port}"
    #             proxies = {'https': f'http://{proxy_str}'}
    #             try:
    #                 if requests.get("https://www.instagram.com", proxies=proxies, timeout=10).ok:
    #                     proxies_ig_ids.append(can.id)
    #             except Exception as e:
    #                 print(f"{e}")
    #
    #         except Exception as e:
    #             print(f"{proxy_str} {e}")
    #     print("proxies_select")
    #
    #     # for s in Sessions.objects.filter(settings__isnull=True, old_settings__isnull=False):
    #     #     try:
    #     #         if s.is_active > 15:
    #     #             continue
    #     #         if True:
    #     #             # if "proxy" in s.error_message.lower() or "connect" in s.error_message.lower() or "500" in s.error_message.lower():
    #     #             try:
    #     #                 IgProxyBanned.objects.create(proxy_id=s.proxy_id)
    #     #             except Exception:
    #     #                 pass
    #     #             s.error_message = ""
    #     #             s.settings = s.old_settings
    #     #             s.proxy_id = random.choice(proxies_ig_ids)
    #     #             s.is_active += 1
    #     #             s.save()
    #     #     except Exception:
    #     #         pass
    #     all_proxy = AllProxy.objects.filter()
    #     all_proxy_ids = all_proxy.values_list('id', flat=True)
    #     for s in Sessions.objects.filter(settings__isnull=False, old_settings__isnull=False):
    #         try:
    #             if s.proxy_id not in all_proxy_ids:
    #                 try:
    #                     AllProxy.objects.get(id=s.proxy_id)
    #                 except Exception:
    #                     s.proxy_id = proxies_select.order_by('?').first()
    #                     s.save()
    #         except Exception:
    #             pass
    # except Exception:
    #     pass
    # try:
    #     for s in Sessions.objects.filter(settings__isnull=True):
    #         try:
    #             username = s.login
    #             password = s.password
    #             if not password or not username:
    #                 continue
    #             settings = None
    #             if "login_required" in s.error_message.lower() or "please wait a few minutes" in s.error_message.lower():
    #                 proxy = AllProxy.objects.filter(
    #                     port__in=[30001, 30010, 30011]
    #                 ).order_by('?').first()
    #
    #                 cl = Client(
    #                     proxy=f"http://{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}",
    #                     settings={}
    #                 )
    #
    #                 def challenge_code_handler(username, choice):
    #                     from instagrapi.mixins.challenge import ChallengeChoice
    #                     if choice == ChallengeChoice.SMS:
    #                         return None
    #                     elif choice == ChallengeChoice.EMAIL:
    #                         return None
    #                     return False
    #
    #                 cl.challenge_code_handler = challenge_code_handler
    #
    #                 cl.login(username=username, password=password, relogin=True)
    #                 settings = cl.settings
    #                 settings["authorization_data"] = cl.authorization_data
    #                 settings["cookies"] = {
    #                     "sessionid": cl.authorization_data["sessionid"]
    #                 }
    #                 s.settings = settings
    #                 s.old_settings = settings
    #                 s.error_message = "new"
    #                 s.is_active = 1
    #                 try:
    #                     s.proxy_id = proxy.id
    #                 except Exception:
    #                     pass
    #                 s.save()
    #                 print(f"save {s}")
    #         except Exception as e:
    #             try:
    #                 s.error_message = e
    #                 s.save()
    #             except Exception:
    #                 pass
    #             print(f"login_required {e}")
    # except Exception as e:
    #     print(f"proxy banned {e}")
    try:
        SourcesItems.objects.filter(network_id=7, disabled=0, last_modified__isnull=True).update(
            last_modified=datetime.datetime(2000, 1, 1))

    except Exception as e:
        print(e)
    try:
        SourcesItems.objects.filter(network_id=7, disabled=0,
                                    last_modified__lte=datetime.datetime(1999, 1, 1)).update(
            last_modified=datetime.datetime(2000, 1, 1))
    except Exception as e:
        print(e)
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute('''UPDATE prsr_parser_keywords SET last_modified = "2000-01-01 01:01:02" WHERE network_id = 7 AND last_modified < "2000-01-01 01:01:01"''')
    except Exception as e:
        print(e)
    # try:
    #     proxies_select = AllProxy.objects.filter(
    #         port__in=[30001, 30010, 30010]
    #     )
    #     for s in Sessions.objects.filter(proxy_id__isnull=True):
    #         s.proxy_id = proxies_select.order_by('?').first()
    #         s.save(update_fields=["proxy_id"])
    # except Exception as e:
    #     print(e)


if __name__ == "__main__":
    update()
