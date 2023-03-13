from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
import pytz
from django.utils.timezone import now


# class User(AbstractUser):
#     def __str__(self):
#         return self.id


class Owner(models.Model):
    id = models.IntegerField(primary_key=True)
    screen_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    sphinx_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    avatar = models.CharField(max_length=255)
    last_modified = models.DateTimeField(default=now)
    followers = models.IntegerField(default=0)
    screen_prefix = models.CharField(max_length=20)
    # friendly = models.IntegerField(default=0)

    class Meta:
        db_table = 'prsr_parser_ok_users'


class Posts(models.Model):
    id = models.IntegerField(primary_key=True)
    owner_id = models.IntegerField(null=True, blank=True)
    from_id = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=datetime(1, 1, 1, 0, 0, tzinfo=pytz.UTC))
    likes = models.IntegerField(default=0)
    reposts = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    found_date = models.DateField(auto_now_add=True)
    last_modified = models.DateTimeField(default=now)
    content_hash = models.CharField(max_length=32, null=True, blank=True)
    url = models.CharField(max_length=4096)
    sphinx_id = models.CharField(max_length=4096)

    class Meta:
        db_table = 'prsr_parser_ok_posts'


class PostContent(models.Model):
    id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=10000)
    url = models.CharField(max_length=4096)

    class Meta:
        db_table = 'prsr_parser_ok_post_content'


class Sources(models.Model):
    uid = models.IntegerField(default=0)
    published = models.IntegerField(default=1)
    status = models.BooleanField(default=0)
    type = models.CharField(default="profiles", max_length=4096)
    retro = models.DateField(null=True, blank=True)
    retro_max = models.DateField(null=True, blank=True)
    networks = models.IntegerField(default=0)
    # last_modify = models.DateTimeField(null=True, blank=True)
    # links_modify = models.DateTimeField(null=True, blank=True)
    # n2_modify = models.DateTimeField(null=True, blank=True)
    taken = models.BooleanField(default=1)
    linking = models.BooleanField(default=0)
    sources = models.IntegerField(default=15)
    profiles = models.IntegerField(default=15)
    stats_params = models.CharField(null=True, blank=True, max_length=4096)

    class Meta:
        db_table = 'prsr_parser_sources'


class SourcesItems(models.Model):
    source_id = models.IntegerField()
    network_id = models.IntegerField(default=0)
    type = models.IntegerField(default=1)
    data = models.CharField(default='nexta_live', max_length=4096)
    last_modified = models.DateTimeField(null=True, blank=True)
    # reindexed = models.DateTimeField(null=True, blank=True)
    taken = models.BooleanField(default=0)
    reindexing = models.BooleanField(default=0)
    disabled = models.BooleanField(default=0)
    forced = models.BooleanField(default=0)

    class Meta:
        db_table = 'prsr_parser_source_items'


class Keyword(models.Model):
    id = models.IntegerField(primary_key=True)
    network_id = models.IntegerField(default=0)
    keyword = models.CharField(default='nexta_live', max_length=4096)
    enabled = models.IntegerField(default=0)
    # created_date = models.DateTimeField(null=True, blank=True)
    # modified_date = models.DateTimeField(null=True, blank=True)
    # depth = models.DateField(null=True, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    taken = models.BooleanField(default=0)
    reindexing = models.BooleanField(default=0)
    forced = models.BooleanField(default=0)
    disabled = models.BooleanField(default=0)

    class Meta:
        db_table = 'prsr_parser_keywords'


class KeywordSource(models.Model):
    keyword_id = models.IntegerField(primary_key=True)
    source_id = models.IntegerField()

    class Meta:
        db_table = 'prsr_parser_source_keywords'


class AllProxy(models.Model):
    ip = models.CharField(max_length=256)
    port = models.IntegerField()
    login = models.CharField(max_length=256)
    proxy_password = models.CharField(max_length=256)
    # last_used = models.DateTimeField(null=True, blank=True)
    # last_used_y = models.DateTimeField(null=True, blank=True)
    failed = models.IntegerField()
    errors = models.IntegerField()
    foregin = models.IntegerField()
    banned_fb = models.IntegerField()
    banned_y = models.IntegerField()
    banned_tw = models.IntegerField()
    # valid_untill = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=256)
    v6 = models.IntegerField()
    # last_modified = models.DateTimeField(null=True, blank=True)
    checking = models.BooleanField()

    class Meta:
        db_table = 'prsr_parser_proxy'


class Proxy(models.Model):
    id = models.IntegerField(primary_key=True)
    taken = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    errors = models.IntegerField(default=0)
    banned = models.BooleanField(default=False)

    class Meta:
        db_table = 'prsr_parser_proxy_ok'


class UpdateIndex(models.Model):
    created_date = models.DateField(default=datetime.min)
    owner_id = models.IntegerField()
    network_id = models.IntegerField(default=8)
    sphinx_id = models.CharField(max_length=127)

    class Meta:
        db_table = 'prsr_update_index'


class Sessions(models.Model):
    login = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    start_parsing = models.DateTimeField(null=True, blank=True)
    last_parsing = models.DateTimeField(null=True, blank=True)
    is_active = models.IntegerField(default=1, db_index=True)
    taken = models.BooleanField(default=False)
    proxy_id = models.IntegerField(null=True, blank=True)
    session_id = models.CharField(max_length=256, null=True, blank=True)
    error_message = models.CharField(max_length=256)
    old_session_id = models.CharField(max_length=256, null=True, blank=True)
    old_settings = models.CharField(max_length=1024, null=True, blank=True)
    settings = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        db_table = 'prsr_parser_ig_session'


class IgUser(models.Model):
    id = models.IntegerField(primary_key=True)
    sphinx_id = models.IntegerField()
    name = models.CharField(max_length=255, null=True, blank=True)
    screen_name = models.CharField(max_length=255, null=True, blank=True)
    logo = models.CharField(max_length=255, null=True, blank=True)
    followers = models.IntegerField(default=0)
    friendly = models.IntegerField(default=0)
    district = models.IntegerField(default=0)
    last_modify = models.DateTimeField(default=now)
    found_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'prsr_parser_ig_users'
class IgPost(models.Model):
    id = models.IntegerField(primary_key=True)
    owner_id = models.IntegerField()
    shortcode = models.CharField(max_length=255, null=True, blank=True)
    owner_sphinx_id = models.IntegerField(default=0)
    content = models.CharField(max_length=4096, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    comments = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    sphinx_id = models.IntegerField()
    found_date = models.DateField(auto_now_add=True)
    last_modified = models.DateTimeField(default=now)
    content_hash = models.CharField(max_length=32, null=True, blank=True)
    group_id = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        db_table = 'prsr_parser_ig_posts'


class IgMedia(models.Model):
    id = models.IntegerField(primary_key=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    media_type = models.IntegerField(default=0)

    class Meta:
        db_table = 'prsr_parser_ig_media'


class Bot(models.Model):
    id = models.IntegerField(primary_key=True)
    nework = models.IntegerField(default=0)
    banned = models.IntegerField()
    login = models.CharField(max_length=256)
    password = models.CharField(max_length=256)

    class Meta:
        db_table = 'prsr_parser_bot'
