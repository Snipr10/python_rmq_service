import datetime
import json

import os
import time

import django.db
import pika

from utils import get_chanel, get_sphinx_id, get_md5_text, FIRST_DATE


def read_reslut_while():
    while True:
        try:
            read_tasks()
        except Exception:
            time.sleep(10)


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
    update_sphinx_rmq = []
    def callback(ch, method, properties, body):
        try:
            django.db.close_old_connections()
            body = json.loads(body.decode("utf-8"))
            print(body)
            for r in body:
                try:

                    created_date = datetime.datetime.fromisoformat(r.get("taken_at"))

                    print(f"FIRST_DATE {created_date}")
                    if created_date < FIRST_DATE:
                        continue
                    print("created_date < FIRST_DATE")

                    owner_id = r.get("user").get("pk")
                    owner_sphinx_id = get_sphinx_id(owner_id)


                    post_id = r.get("pk")
                    print(f"post id {post_id}")
                    post_sphinx_id = get_sphinx_id(r.get("code"))
                    post.append(
                        IgPost(
                            id=post_id,
                            owner_id=owner_id,
                            shortcode=r.get("code"),
                            owner_sphinx_id=owner_sphinx_id,
                            content=r.get("caption_text"),
                            created_date=created_date,
                            comments=r.get("comment_count"),
                            likes=r.get("like_count"),
                            sphinx_id=post_sphinx_id,
                            content_hash=get_md5_text(r.get("caption_text"))
                        )
                    )



                    users.append(
                        IgUser(
                            id=owner_id,
                            sphinx_id=owner_sphinx_id,
                            name=r.get("user").get("full_name"),
                            screen_name=r.get("user").get("username"),
                            logo=r.get("user").get("profile_pic_url"),
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
                    update_sphinx_rmq.append(post_sphinx_id)
                    if len(post) > 10:
                        django.db.close_old_connections()
                        try:
                            IgUser.objects.bulk_create(users, batch_size=200, ignore_conflicts=True)
                        except Exception as e:
                            print(f"IgUser: {e}")
                        try:
                            IgPost.objects.bulk_update(post, ['last_modified', 'comments', 'likes', 'created_date'], batch_size=200)
                            users.clear()
                        except Exception as e:
                            print(f"IgUser: {e}")
                        try:
                            IgPost.objects.bulk_create(post, batch_size=200, ignore_conflicts=True)
                            post.clear()
                        except Exception as e:
                            print(f"IgPost: {e}")
                        try:
                            IgMedia.objects.bulk_create(media, batch_size=200, ignore_conflicts=True)
                            media.clear()
                        except Exception as e:
                            print(f"IgMedia: {e}")
                except Exception as e:
                    print(f"insta_key_result{e}")
            add_update_index_to_rmq(update_sphinx_rmq)
        except Exception as e:
            print(f"callback{e}")
            django.db.close_old_connections()

    channel.basic_consume(queue='insta_key_result', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

rmq_settings = "amqp://post_index:R2ghtt9hebLv@192.168.5.46:5672/post_index"

def add_update_index_to_rmq(sphinx_ids, attempts=0):
    print("add_update_index_to_rmq")
    try:
        if len(sphinx_ids) < 10000:
            parameters = pika.URLParameters(    )
            connection = pika.BlockingConnection(parameters=parameters)
            channel = connection.channel()
            for sphinx_id in sphinx_ids:
                rmq_json_data = {
                    "id": sphinx_id,
                    "network_id": 7
                }
                channel.basic_publish(exchange='',
                                      routing_key='post_index',
                                      body=json.dumps(rmq_json_data))
            channel.close()
    except Exception as e:
        print(f"can not save {e}")
if __name__ == "__main__":
    read_tasks()
