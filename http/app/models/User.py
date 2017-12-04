import datetime
import hashlib
import random
import time
import uuid

from orator.orm import has_many, has_one, belongs_to_many, accessor
from orator import SoftDeletes

from core.helpers.Config import Config
from core.models.Model import Model


class User(Model.core(), SoftDeletes):
    __table__ = 'users'

    def generate_token(self):
        self.api_token = str(uuid.uuid4())

    def format_default(self):
        response = self._left_keys(['id', 'api_token', 'email', 'first_name', 'last_name', 'photo'])
        response['friendsCount'] = random.randrange(0, 1000)
        return response

    def format_contact(self):
        response = self._left_keys(['id', 'first_name', 'last_name', 'photo'])
        return response

    def format_admin(self):
        response = self._left_keys(['id', 'email', 'created_at', 'first_name', 'last_name', 'photo', 'birthday'])
        return response

    @accessor
    def last_connection(self):
        if self.get_raw_attribute('last_connection'):
            dt = datetime.datetime.strptime(str(self.get_raw_attribute('last_connection')), "%Y-%m-%d %H:%M:%S.%f")
            return int(time.mktime(dt.timetuple()))
        return ''

    def get_last_message(self):
        last_message = None
        last_message_my = None
        last_message_notmy = None
        if self.last_message_my:
            last_message_my = self.last_message_my
        if self.last_message_notmy:
            last_message_notmy = self.last_message_notmy
        if last_message_my and last_message_notmy:
            last_message = last_message_my if last_message_my.created_at >= last_message_notmy.created_at else last_message_notmy
        elif last_message_my:
            last_message = last_message_my
        elif last_message_notmy:
            last_message = last_message_notmy
        if last_message is not None:
            last_message = last_message.format_last(self.id)
        else:
            last_message = {}
        return last_message

    def format_list(self):
        response = self._left_keys(['id', 'first_name', 'last_name', 'birthday', 'photo', 'email'])
        return response

    @has_many
    def files(self):
        return Model.load('UserFile')

    @has_many
    def socials(self):
        return Model.load('UserSocial')

    @has_many('owner_id')
    def boards(self):
        return Model.load('Board')

    @has_many('creator_id')
    def cards(self):
        return Model.load('Card')

    @has_many('author_id')
    def card_comments(self):
        return Model.load('CardComment')

    @has_many
    def contacts(self):
        return Model.load('Contact')

    @has_many
    def favorites(self):
        return Model.load('Favorite')

    @has_one('id_to_user', 'id')
    def last_message_my(self):
        return Model.load('Message').order_by('created_at', 'desc')

    @has_one('id_from', 'id')
    def last_message_notmy(self):
        return Model.load('Message').order_by('created_at', 'desc')

    @belongs_to_many('acl_groups_users', 'user_id', 'group_id')
    def acl_groups(self):
        return Model.load('ACL_Group')

    def reset_password(self):
        self.reset_pass_token = str(uuid.uuid4())
        date_timestamp = (Config.get('reset_pass_expires') * 3600) + int(time.time())
        date_expire = datetime.datetime.fromtimestamp(date_timestamp).isoformat(' ')
        self.reset_pass_expires = date_expire
        self.save()

    def password_correct(self, password):
        return hashlib.sha1(str(password).encode('utf-8')).hexdigest() == self.password

    def set_password(self, password):
        self.password = hashlib.sha1(password.encode('utf-8')).hexdigest()

    def restore_password_expired(self):
        expired_timestamp = int(time.mktime(self.reset_pass_expires.timetuple()))
        current_timestamp = int(time.time())
        return expired_timestamp < current_timestamp

    async def update_last_connection(self):
        self.last_connection = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.save()

    def save(self):
        if hasattr(self, 'photo') and self.photo and (
                        self.photo.find('http://') != -1 or self.photo.find('https://') != -1):
            import urllib.request
            try:
                file_name = str(uuid.uuid4()) + '.jpg'
                # save image from url to our server
                urllib.request.urlretrieve(self.photo, Config.get('root_dir') + Config.get('upload_dir') + file_name)
                # save to database correct path
                self.photo = Config.get('upload_dir') + file_name
            except:
                pass
        super().save()

    def add_role_group(self, name):
        result = False
        group = Model.load('ACL_Group').where('group', '=', name).first()
        if group is not None:
            try:
                self.acl_groups().attach(group)
                result = True
            except:
                pass
        else:
            raise Exception('group with alias "api" not found.')
        return result

    def has_role_group(self, name):
        has_group = False
        user = User.where('id', '=', self.id).first()
        group_aliases = []
        if user.acl_groups:
            for group_obj in user.acl_groups:
                group_aliases.append(group_obj.group)
            if name in group_aliases:
                has_group = True
        return has_group
