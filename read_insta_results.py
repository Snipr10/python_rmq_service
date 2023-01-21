import datetime
import json

import os
import django.db

from utils import get_chanel, get_sphinx_id, get_md5_text


def read_tasks():
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
    from core.models import IgUser, IgPost, IgMedia, UpdateIndex

    channel = get_chanel()
    users = []
    post = []
    sphinx_ids = []
    media = []
    update_sphinx = []


    def callback(ch, method, properties, body):
        try:
            body = json.loads(body.decode("utf-8"))
            print(body)
            for r in body:
                owner_id = r.get("user").get("pk")
                owner_sphinx_id = get_sphinx_id(owner_id)
                users.append(
                    IgUser(
                        id=owner_id,
                        sphinx_id=owner_sphinx_id,
                        name=r.get("user").get("full_name"),
                        screen_name=r.get("user").get("username"),
                        logo=r.get("user").get("profile_pic_url"),
                    )
                )
                post_id = r.get("pk")
                post_sphinx_id = get_sphinx_id(r.get("code"))

                post.append(
                    IgPost(
                        id=post_id,
                        owner_id=owner_id,
                        shortcode=r.get("code"),
                        owner_sphinx_id=owner_sphinx_id,
                        content=r.get("caption_text"),
                        created_date=datetime.datetime.fromisoformat(r.get("taken_at")),
                        comments=r.get("comment_count"),
                        likes=r.get("like_count"),
                        sphinx_id=post_sphinx_id,
                        content_hash=get_md5_text(r.get("caption_text"))
                    )
                )
                sphinx_ids.append(post_sphinx_id)
                media.append(
                    IgMedia(
                        id=post_id,
                        url=r.get("thumbnail_url"),
                    )
                )
                update_sphinx.append(UpdateIndex(id=post_id, network_id=7, sphinx_id=post_sphinx_id))
                if len(post) > 10:
                    django.db.close_old_connections()
                    try:
                        IgUser.objects.bulk_create(users, batch_size=200, ignore_conflicts=True)
                    except Exception as e:
                        print(f"IgUser: {e}")
                    try:
                        IgPost.objects.bulk_create(post, batch_size=200, ignore_conflicts=True)
                    except Exception as e:
                        print(f"IgPost: {e}")
                    try:
                        IgMedia.objects.bulk_create(media, batch_size=200, ignore_conflicts=True)
                    except Exception as e:
                        print(f"IgMedia: {e}")
        except Exception as e:
            print(f"callback{e}")
            django.db.close_old_connections()

    channel.basic_consume(queue='insta_key_result', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    read_tasks()
