import os
import uuid

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


    try:
        with open("fb_2.txt", "r") as f:
            for line in f:
                split_ = line.split("|")
                username, password = split_[0].split(":")
                _, app_version, _ = split_[1][:split_[1].find("(")].strip().split(" ")
                android_, dpi, resolution, manufacturer, model, device, cpu, _, version_code = split_[1][
                                                                                               split_[1].find("(") + 1:
                                                                                               split_[
                                                                                                   1].find(")")].split(
                    ";")
                android_version, android_release = android_.split("/")

                device_id, phone_id, client_session_id, advertising_id = split_[2].split(";")
                for s in split_[3].split(";"):
                    if "session" in s:
                        sessionid = s.split("=")[-1]
                        break
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
                Sessions.objects.create(
                    login=username,
                    password=password,
                    proxy_id=1,
                    session_id=sessionid,
                    error_message=None,
                    old_session_id=sessionid,
                    settings=settings,
                    old_settings=settings
                )
    except Exception as e:
        print(e)
