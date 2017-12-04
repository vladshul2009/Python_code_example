import re, datetime
from _snack import message

from app.controllers.BaseController import BaseController
from core.helpers.Config import Config
from app.models.User import User
from app.models.Message import Message
from app.models.UserSocial import UserSocial
from app.models.Favorite import Favorite


class UserController(BaseController):
    _json_data = None
    _headers = None
    _method = None

    def _before(self):
        self._json_data = self.json()
        self._headers = self.get_request().headers
        self._method = self.get_request().method
        if self.get_user():
            user = self.get_user()
            user.update_last_connection()
            if self._json_data is not None:
                push_token = self._json_data.get('push_token')
                if push_token is not None and type(push_token) is str:
                    user.push_token = push_token
                    user.save()
                    self.set_user(user)

    def signup(self):
        """
       Client:
           - Payload: { "command": "user/signup", "params" : {email, password} }
       Server:
           - { "code" : 200, "data": {"rent": "0.37"}, "actions" : [] }
       """
        email = self._json_data['email']
        password = self._json_data['password']
        existing_user = User.where('email', '=', email).first()
        if existing_user is None:
            user = User()
            user.generate_token()
            user.email = email
            user.set_password(password)
            # @TODO: write universal validator helper
            values_to_save = self.left_keys(self._json_data, {'first_name', 'last_name'})
            for key, val in values_to_save.items():
                setattr(user, key, val)
            user.save()
            if user.add_role_group('api'):
                self.make_response(user.format_default())
            else:
                raise Exception('cant create user role.')
        else:
            self.make_message('User with such email already exists.')

    def update_profile(self):
        user = self.get_user()
        new_password = self._json_data.get('new_password')
        old_password = self._json_data.get('old_password')

        if new_password and old_password:
            if not user.is_social:
                if user.password_correct(old_password):
                    user.set_password(new_password)
                    user.save()
                    self.make_response(user.format_default())
                else:
                    self.make_message('Incorrect old password.')
            else:
                self.make_message('Please signup to change your password.')
        else:
            attrs = ['first_name', 'last_name', 'name', 'email', 'photo']
            not_empty_keys = ['email']
            for key in attrs:
                new_value = self._json_data.get(key)
                if new_value is not None and new_value:
                    if key == 'email':
                        if re.match(Config.get('email_regexp'), new_value):
                            email_exists = User.where('id', '<>', user.id).where('email', '=', new_value).exists()
                            if not email_exists:
                                user.email = new_value
                            else:
                                self.make_message("This email already taken.")
                                return
                        else:
                            self.make_message("Invalid email format.")
                            return
                    elif key == 'photo':
                        from app.models.UploadedFile import UploadedFile
                        file_object = UploadedFile.get_by_urls(new_value, is_single=True)
                        if file_object is not None:
                            user.photo = file_object.file
                            file_object.delete()
                    elif key == 'name':
                        names = new_value.strip().split(' ')
                        if len(names) == 1:
                            user.first_name = names[0]
                        elif len(names) == 2:
                            user.first_name = names[0]
                            user.last_name = names[1]
                        elif len(names) > 2:
                            user.first_name = names[0]
                            names.pop(0)
                            user.last_name = ' '.join(names)
                    else:
                        setattr(user, key, new_value)
                elif key not in not_empty_keys and new_value is not None:
                    if key is 'name':
                        user.first_name = ''
                        user.last_name = ''
                    elif key is 'photo':
                        # remove file physically
                        setattr(user, key, '')
                    else:
                        setattr(user, key, '')
            user.save()
            self.make_response(user.format_default())

    def login(self):
        if self._method == 'POST':
            message = 'Incorrect email or password.'
            email = self._json_data['email']
            password = self._json_data['password']
            user = User.where('email', '=', email).first()
            if user is not None:
                if user.password_correct(password):
                    user.update_last_connection()
                    self.make_response(user.format_default())
                else:
                    self.make_message(message)
            else:
                self.make_message(message)
        else:
            self.make_response(None)

    def reset_password(self):
        email = None
        if self._json_data is not None:
            email = self._json_data.get('email')
        if email is not None and email:
            if re.match(Config.get('email_regexp'), email):
                user = User.where('email', '=', email).first()
                if user is None:
                    user_social = UserSocial.where('email', '=', email).first()
                    if user_social is not None:
                        user = user_social.user
                if user is not None:
                    user.reset_password()

                    app_name = None
                    headers = self.get_request().headers
                    try:
                        app_name = headers['Application-Name']
                    except:
                        pass

                    from core.helpers.Events import Events
                    Events.password_reset(dict(email=email, reset_pass_token=user.reset_pass_token, app_name=app_name))

                    self.make_response({})
                else:
                    self.make_message("User with this email not found.")
            else:
                self.make_message("Incorrect email format.")
        else:
            self.make_message('Email is required.')

    # for api
    def new_password(self):
        reset_token = self._json_data.get('reset_token')
        user = User.where('reset_pass_token', '=', reset_token).first()
        if user is not None and not user.restore_password_expired():
            password = self._json_data.get('password')
            if password:
                user.set_password(password)
                user.reset_pass_token = None
                user.reset_pass_expires = None
                user.save()
                self.make_response(user.format_default())
            else:
                self.make_message('Please fill "password" field.')
        else:
            self.make_message("Reset password token is incorrect.")

    # @TODO: rewrite using templates, temponary condition
    # for web
    def change_password(self):
        redirect = None
        reset_token = self.get('reset_token')
        try:
            redirect = self.get('redirect')
        except:
            pass
        user = User.where('reset_pass_token', '=', reset_token).first()
        if user is not None and not user.restore_password_expired():
            if redirect is None:
                html = ''
                password_changed = False
                form_submited = self.post('set_new_password', False)
                if form_submited:
                    pass1 = self.post('password')
                    pass2 = self.post('password_repeat')
                    if pass1 and pass2:
                        if pass1 == pass2:
                            user.set_password(pass1)
                            user.reset_pass_token = None
                            user.reset_pass_expires = None
                            user.save()
                            password_changed = True
                            html = 'Your password was changed!'
                        else:
                            html += 'Passwords are not equal.<br/>'
                    else:
                        html += 'Please fill "password" and "repeat password" fields.<br/>'
                if not password_changed:
                    html += '<form method="POST" action="">' \
                            '<input type="password" name="password" placeholder="password"><br/>' \
                            '<input type="password" name="password_repeat" placeholder="reapeat your password"><br/>' \
                            '<input type="submit" name="set_new_password" value="Change">' \
                            '</form>'
                self.make_response(html, format='html')
            else:
                from aiohttp import web
                return web.HTTPFound(redirect + '://login/restore?reset_token=' + reset_token)
        else:
            html = 'User not found'
            self.make_response(html, format='html')

    def login_social(self):
        # self._json_data
        # social_alias = self.post('social_alias')
        # token = self.post('token')
        token = self._json_data.get('token')
        social_alias = self._json_data.get('social_alias')
        is_agree = True if self._json_data and self._json_data.get('is_agree') else False
        # if is_agree is not True:
        #     self.make_message('Please confirm terms agreement.')
        if social_alias:
            from core.helpers.Social import Social
            if token or social_alias == 'twitter':
                # response = Social.get_facebook_user(token)
                response = Social.get_user(social_alias, token, self._json_data)
                # if social_alias == 'twitter':
                # @TODO: make method in Social helper for getting user avatar
                if response is not None:
                    social_config = Social.get_config()
                    user_social = None
                    for field in Social.get_social_fields(social_alias):
                        if field[0] == 'social_ident':
                            ident_key = field[1]
                            ident_value = Config.get(ident_key, response)
                            user_social = UserSocial.find_by_ident(ident_value, social_alias)
                    if user_social is None:
                        if is_agree is not True:
                            self.make_message('Please confirm terms agreement.', ['goto_auth'])
                        else:
                            user_social = UserSocial()
                            user = User()
                            user_social.alias = social_alias
                            for field in Social.get_social_fields(social_alias):
                                social_key = field[1] if len(field) >= 2 else field[0]
                                # value = response.get(social_key)
                                value = Config.get(social_key, response)
                                # execute all function defined in fields
                                if len(field) > 2:
                                    for i, func in enumerate(field):
                                        if i > 1:
                                            value = func(value)

                                if value is not None:
                                    setattr(user_social, field[0], value)
                                    user_field_val = social_config[social_alias]['social_to_user'].get(
                                        field[0])
                                    if user_field_val is not None:
                                        setattr(user, user_field_val, value)
                            # social media returned not empty user unique identifier
                            if hasattr(user_social, 'social_ident') and user_social.social_ident:
                                user.generate_token()
                                from core.models.Connection import Connection
                                with Connection.get_db().transaction():
                                    user.is_social = True
                                    user.save()
                                    if user.add_role_group('api'):
                                        user_social.user_id = user.id
                                        user_social.save()
                                        self.make_response(user_social.user.format_default())
                                    else:
                                        user.delete()
                                        raise Exception('cant create user role.')
                            else:
                                self.make_message('Cant get social media user unique identifier.')
                    else:
                        # user already exists. wee need return existing user
                        self.make_response(user_social.user.format_default())
                else:
                    self.make_actions(['invalid_oauth2_token'])
            else:
                self.make_actions(['parameter_token_required'])
        else:
            self.make_actions(['parameter_social_alias_required'])

    def __get_message(self, last_message):
        kind = last_message.get('kind')
        if kind and kind != 'text':
            if kind == 'image':
                return '<Image>'
            if kind == 'doc':
                return '<Document>'
        return last_message['message']

    def __get_home_screen(self):
        user = self.get_user()
        users_list = []

        # user's favourites
        favorites = Favorite.where_has('favorite', lambda q: q.where('user_id', '=', user.id)) \
            .limit(Config.get('home_screen.favourite_limit')) \
            .order_by('id', 'desc') \
            .get()
        for fav in favorites:
            formatted_user = fav.favorite.format_list()
            formatted_user['last_message'] = {}
            formatted_user['favorite'] = True
            users_list.append(formatted_user)

        # last connections - last message to user or from user
        messages = Message.where({'id_from': user.id}) \
            .or_where({'id_to_user': user.id}) \
            .where_null('id_to_chat') \
            .order_by('created_at', 'desc') \
            .limit(Config.get('home_screen.last_connections_limit')) \
            .get()
        for message in messages:
            if str(message.id_from) == str(user.id):
                tmp = user.format_list()
                last_message = message.format_last(user.id)
                last_message['message'] = self.__get_message(last_message)
                tmp['last_message'] = last_message
                tmp['favorite'] = False
                users_list.append(tmp)
            elif str(message.id_to_user) == str(user.id):
                message_user = User.where('id', message.id_from).first()
                if message_user is not None:
                    tmp = message_user.format_list()
                    last_message = message.format_last(message_user.id)
                    last_message['message'] = self.__get_message(last_message)
                    tmp['last_message'] = last_message
                    tmp['favorite'] = False
                    users_list.append(tmp)

        # users with birthday today
        birthday_day = datetime.datetime.now().strftime('%d')
        birthday_month = datetime.datetime.now().strftime('%m')
        users_with_birthday = User.where_raw(
            '(EXTRACT(MONTH FROM birthday) = ' + birthday_month + ' AND EXTRACT(DAY FROM birthday) = ' + birthday_day + ')') \
            .limit(Config.get('home_screen.birthday_limit')) \
            .get()
        for user_with_b in users_with_birthday:
            formatted_user = user_with_b.format_list()
            formatted_user['last_message'] = {}
            formatted_user['favorite'] = False
            users_list.append(formatted_user)
        return users_list

    def find_users(self):
        user = self.get_user()
        is_home_screen = self._json_data.get('is_home_screen', False)
        users_list = []
        if is_home_screen:
            users_list = self.__get_home_screen()
        else:
            limit = Config.get('user_contacts.limit')
            if self._json_data is not None and self._json_data.get('limit') is not None:
                if int(self._json_data.get('limit')) > 0:
                    limit = int(self._json_data.get('limit'))

            if 'term' in self._json_data and self._json_data['term'].strip():
                term = ' | '.join(self._json_data['term'].split())
                users = User.where_raw("(textsearchable_index_col @@ to_tsquery('" + term + "') AND users.id <> " + str(
                    user.id) + ") AND (photo is not NULL or first_name is not NULL or last_name is not NULL)") \
                    .offset(self.get_offset()) \
                    .limit(limit) \
                    .get()
            else:
                users = User.where_raw(
                    '(photo is not NULL or first_name is not NULL or last_name is not NULL) AND users.id <> ' + str(
                        user.id) + '') \
                    .offset(self.get_offset()) \
                    .limit(limit) \
                    .get()

            for usr in users:
                formatted_user = usr.format_list()
                last_message = usr.get_last_message()
                if last_message:
                    # for none text messages show <Image> or <Document>
                    kind = last_message.get('kind')
                    if kind and kind != 'text':
                        if kind == 'image':
                            last_message['message'] = '<Image>'
                        if kind == 'doc':
                            last_message['message'] = '<Document>'
                formatted_user['last_message'] = last_message
                formatted_user['favorite'] = True if user.favorites.where('favorite_id', usr.id).first() is not None else False
                users_list.append(formatted_user)

        self.make_response({'users': users_list, 'count': len(users_list)})

    def add_contact(self):
        from app.models.Contact import Contact
        user_ids = self._json_data.get('user_id')
        user = self.get_user()
        if user_ids:
            if type(user_ids) is not list:
                user_ids = [user_ids]
            for usr in user_ids:
                contact = Contact.where('contact_id', usr).where('user_id', user.id).first()
                if contact is None:
                    contact = Contact()
                    contact.user_id = user.id
                    contact.contact_id = usr
                    contact.save()
        self.make_response({})

    def contacts(self):
        user = self.get_user()
        formated_users = []
        if user.contacts:
            for found_user in user.contacts:
                formated_users.append(found_user.contact.format_contact())
        self.make_response({'users': formated_users})

    def add_favorite(self):
        user_ids = self._json_data.get('user_id')
        user = self.get_user()
        if user_ids:
            if type(user_ids) is not list:
                user_ids = [user_ids]
            for usr in user_ids:
                favorite = Favorite.where('favorite_id', usr).where('user_id', user.id).first()
                if favorite is None:
                    favorite = Favorite()
                    favorite.user_id = user.id
                    favorite.favorite_id = usr
                    favorite.save()
        self.make_response({})

    def delete_favorite(self):
        user_id = self._json_data.get('user_id')
        user = self.get_user()
        if user_id:
            favorite = Favorite.where('favorite_id', user_id).where('user_id', user.id).first()
            if favorite is not None:
                favorite.delete()
        self.make_response({})

    def favorites(self):
        user = self.get_user()
        user_list = user.favorites

        return_list = []
        for favorite in user_list:
            return_list.append(favorite.format_favorite())
        self.make_response({'users': return_list})

    def messages(self):
        user = self.get_user()
        id_from = self._json_data.get('id_from')
        limit = int(self._json_data.get('limit', Config.get('user_messages.limit')))
        if id_from:
            user_from = User.where('id', '=', id_from).first()
            if user_from:
                from app.models.Message import Message
                formatted_messages = []
                messages = Message.where({'id_from': id_from, 'id_to_user': user.id})\
                    .or_where({'id_from': user.id, 'id_to_user': id_from})\
                    .order_by('created_at', 'desc')\
                    .offset(self.get_offset())\
                    .limit(limit)\
                    .get()
                for message in messages:
                    id_to_user = message.id_to_user
                    formatted_message = message.format_receiver()
                    if str(formatted_message['user_id']) == str(user.id):
                        formatted_message['is_owner'] = True
                        formatted_message['user_id'] = id_to_user
                    else:
                        formatted_message['is_owner'] = False
                    formatted_messages.append(formatted_message)
                self.make_response({'messages': formatted_messages})
            else:
                self.make_actions(['user_notfound'])
        else:
            raise Exception('id_from is required')

    def delete_contact(self):
        user_id = self._json_data.get('user_id')
        user = self.get_user()
        if user_id:
            from app.models.Contact import Contact
            contact = Contact.where('contact_id', user_id).where('user_id', user.id).first()
            if contact is not None:
                contact.delete()
        self.make_response({})

    # https://www.postgresql.org/docs/9.3/static/functions-array.html
    # WHERE user_ids @> '{17,34}'
    def create_chat_room(self):
        current_user = self.get_user()
        if self._json_data is not None:
            from app.models.ChatRoom import ChatRoom
            chat_room = ChatRoom()
            chat_room.creator_id = current_user.id
            user_ids = self._json_data.get('user_ids')
            room_user_ids = []
            if user_ids is not None and type(user_ids) is list:
                users = User.where_in('id', '=', user_ids).get()
                for user in users:
                    room_user_ids.append(user.id)
            if len(room_user_ids) > 0:
                pass
            chat_room.save()
        else:
            pass

    def add_user_to_chat(self):
        pass

    def del_user_from_chat(self):
        pass

    def save_files(self):
        if self._json_data is not None:
            file_ids = self._json_data.get('file_ids')
            file_urls = self._json_data.get('file_urls')
            uploaded_files = None
            uploaded_count = 0
            from app.models.UploadedFile import UploadedFile
            if file_ids is not None and type(file_ids) == list:
                uploaded_files = UploadedFile.where_in('id', file_ids).get()
            elif file_urls:
                uploaded_files = UploadedFile.get_by_urls(file_urls)
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    uploaded_file.save_file()
                    uploaded_count += 1
            self.make_response({'uploaded_count': uploaded_count})
        else:
            self.make_message('Please set file ids or file urls array.')

    def files(self):
        files = self.get_user().files.all()
        for i, file in enumerate(files):
            files[i] = file.format_default()
        self.make_response({"files": files})

    def delete(self):
        from core.models.Connection import Connection
        user = self.get_user()
        with Connection.get_db().transaction():
            UserSocial.where('user_id', '=', user.id).delete()
            user.delete()
            if user.email:
                user.email = '#$%^&*' + user.email
                user.save()
            self.make_response({'deleted': True})

    def check_update(self):
        app_name = self._headers['Application-Name'] if 'Application-Name' in self._headers and self._headers[
            'Application-Name'] else None
        platform = self._headers['Device-Platform'] if 'Device-Platform' in self._headers and self._headers[
            'Device-Platform'] else None
        version = self._headers['Application-Version'] if 'Application-Version' in self._headers and self._headers[
            'Application-Version'] else None

        if app_name and platform:
            from app.models.Whatsnew import Whatsnew
            required = False
            if version:
                server_version = Whatsnew.where('platform', '=', platform.lower()).where('app_name', '=', app_name) \
                    .where('required', '=', True).order_by('date', 'desc').first()
                if server_version:
                    required = self.__is_version_required(version, server_version.version)

            release = Whatsnew.where('platform', '=', platform.lower()).where('app_name', '=', app_name).order_by(
                'date', 'desc').first()
            if release:
                data_release = release.to_dict()
                if required:
                    data_release['required'] = True
                self.make_response({'release': data_release})
            else:
                self.make_response({'release': {}})
        else:
            self.make_actions(['parameter_app_name_required'])

    @staticmethod
    def __is_version_required(version_client, version_server):
        count_client = version_client.count('.')
        count_server = version_server.count('.')

        if count_client > 0:
            client_version_arr = version_client.split('.')
            server_version_arr = version_server.split('.')
            i = 0
            required = False
            data_range = count_client if count_server < count_client else count_server
            while i <= data_range:
                if i >= len(server_version_arr):
                    break
                if i >= len(client_version_arr):
                    required = True
                    break
                if client_version_arr[i] < server_version_arr[i]:
                    required = True
                    break
                i += 1
        else:
            required = True if version_server > version_client else False
        return required

    def test(self):
        from core.helpers.Lang import _
        resp = {'text': _('test')}
        self.make_response(resp)

    def client_error_callback(self):
        from core.helpers.Events import Events
        Events.client_error_callback(self._json_data)
        self.make_response({})
