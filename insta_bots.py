import os
import uuid
from instagrapi import Client
def challenge_code_handler(username, choice):
    from instagrapi.mixins.challenge import ChallengeChoice
    if choice == ChallengeChoice.SMS:
        return None
    elif choice == ChallengeChoice.EMAIL:
        return None
    return False


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
    from core.models import Sessions, AllProxy, IgProxyBanned


    try:
        with open("insta.txt", "r") as f:
            for line in f:
                settings = None
                split_ = line.split("|")
                split_ = [x  for x in split_ if x and len(x)>2]
                username, password = split_[0].split(":")

                for ss in split_:
                    try:
                        for s in ss.split(";"):
                            if "session" in s:
                                sessionid = s.split("=")[-1]
                                break
                    except Exception:
                        pass
                try:
                    _, app_version, _ = split_[1][:split_[1].find("(")].strip().split(" ")
                except Exception:
                    app_version = 25
                try:
                    android_, dpi, resolution, manufacturer, model, device, cpu, _, version_code = split_[1][
                                                                                                   split_[1].find("(") + 1:
                                                                                                   split_[
                                                                                                       1].find(")")].split(
                        ";")
                    android_version, android_release = android_.split("/")

                    device_id, phone_id, client_session_id, advertising_id = split_[2].split(";")

                    settings = {
                        "uuids": {
                            "phone_id": phone_id,
                            "uuid": uuid.uuid4().urn[9:],
                            "client_session_id": client_session_id,
                            "advertising_id": advertising_id,
                            "device_id": device_id
                        },
                        'authorization_data': {'ds_user_id': sessionid.split("%")[0],
                                               'sessionid': sessionid,
                                               },
                        'cookies': {
                            'sessionid': sessionid
                        },  # set here your saved cookies
                        "last_login": None,
                        "device_settings": {
                            "cpu": cpu.strip(),
                            "dpi": dpi.strip(),
                            "model": model.strip(),
                            "device": device.strip(),
                            "resolution": resolution.strip(),
                            "app_version": app_version,
                            "manufacturer": manufacturer.strip(),
                            "version_code": version_code.strip(),
                            "android_release": android_release,
                            "android_version": android_version
                        },
                        "user_agent": split_[1]
                    }
                except Exception as e:
                    print(f"settings {e}")

                    settings = None
                at = 0
                proxy = None
                while at < 5:
                    if settings is None:
                        try:
                            print(1)
                            proxy = AllProxy.objects.filter(
                                port__in=[30001, 30010, 30011]
                            ).exclude(
                                id__in=IgProxyBanned.objects.all().values_list('id', flat=True)
                            ).order_by('?')[0]

                            cl = Client(
                                proxy=f"http://{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}",
                            )

                            cl.challenge_code_handler = challenge_code_handler

                            cl.login_by_sessionid(sessionid)
                            settings = cl.get_settings()
                        except Exception as e:
                            print(f"steart {e}")
                    at += 1
                django.db.close_old_connections()

                Sessions.objects.create(
                    login=username,
                    password=password,
                    proxy_id=proxy.id if proxy is not None else None,
                    session_id=sessionid,
                    error_message=None,
                    old_session_id=sessionid,
                    settings=settings,
                    old_settings=settings
                )
    except Exception as e:
        print(f"unable {e}")
