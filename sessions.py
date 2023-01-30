import os
from django.utils import timezone
from instagrapi import Client

if __name__ == '__main__':

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

    for s in Sessions.objects.filter(session_id__isnull=True):
        try:
            proxy = AllProxy.objects.filter(port=30001).order_by('?')[0]
            cl = Client(
                proxy=f"http://{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}",
            )

            cl.login(s.login, s.password)
            s_id = cl.authorization_data['sessionid']
            s.session_id = s_id
            s.save()
        except Exception as e:
            print(f"{s.login} {e}")
