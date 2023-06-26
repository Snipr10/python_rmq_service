import os
import random
import requests

def get_proxy():
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


    proxy_candidates = AllProxy.objects.filter(v6=0).exclude(id__in=IgProxyBanned.objects.all().values_list('proxy_id', flat=True))
    ig_proxy_count = 0
    fb_proxy_count = 0

    for can in proxy_candidates:
        proxy_str = ""
        try:
            proxy_str = f"{can.login}:{can.proxy_password}@{can.ip}:{can.port}"
            proxies = {'https': f'http://{proxy_str}'}
            # try:
            #     if requests.get("https://www.facebook.com/", proxies=proxies, timeout=10).ok:
            #         fb_proxy_count += 1
            # except Exception as e:
            #     print(f"{fb_proxy_count} {e}")

            try:
                if requests.get("https://www.instagram.com", proxies=proxies, timeout=10).ok:
                    ig_proxy_count += 1
                else:
                    raise Exception("not ok")
            except Exception as e:
                IgProxyBanned.objects.create(proxy_id=can.id)
                print(f"{ig_proxy_count} {e}")
            print(f"Proxy count {ig_proxy_count}")
        except Exception as e:
            print(f"{proxy_str} {e}")

if __name__ == "__main__":
    get_proxy()