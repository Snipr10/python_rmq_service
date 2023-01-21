import os
from django.utils import timezone

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
    from core.models import Sessions

    res = []
    with open("creds.txt", 'r', encoding='utf-8') as f:
        for line in f:
            domains = line.split("|")[0]
            cred = domains.split(":")
            res.append(Sessions(
                login=cred[0],
                password=cred[1],
                proxy_id=1,
                start_parsing=timezone.localtime(),
                last_parsing=timezone.localtime())
            )
    Sessions.objects.bulk_create(res, batch_size=200, ignore_conflicts=True)
    print(res)
