from sockets.handlers.BaseHandler import BaseHandler
from sockets.helpers.Socket import Socket

from app.models.ChatRoom import ChatRoom
from app.models.Message import Message
from app.models.User import User
from app.models.UserFile import UserFile


class ChatHandler(BaseHandler):

    def create_chat_room(self, ws):
        if self.is_logged_in(ws):
            data = self._json_data
            title = data.get('title')
            user_ids = data.get('user_ids')
            chat_room = ChatRoom()
            chat_room.creator_id = ws.user_id
            chat_room.title = title
            room_user_ids = []
            if user_ids is not None and type(user_ids) is list:
                users = User.where_in('id', user_ids).get()
                for user in users:
                    room_user_ids.append(user.id)
            chat_room.user_ids = room_user_ids
            chat_room.save()
            self.make_response({'ok': True, 'ident': chat_room.id}, self._command_ok, ws)

    def del_chat_room(self, ws):
        if self.is_logged_in(ws):
            data = self._json_data
            chat_id = data.get('chat_id')
            if chat_id is not None:
                chat_room = ChatRoom.where('id', '=', chat_id).first()
                if chat_room is not None and chat_room.creator_id == ws.user_id:
                    chat_room.delete()
                    self.make_response({'ok': True}, self._command_ok, ws)

    def add_user_to_chat(self, ws):
        if self.is_logged_in(ws):
            data = self._json_data
            chat_id = data.get('chat_id')
            user_ids = data.get('user_ids')
            if chat_id is not None:
                chat_room = ChatRoom.where('id', '=', chat_id).first()
                if chat_room is not None and str(ws.user_id) == str(chat_room.creator_id):
                    if chat_room.user_ids is None:
                        chat_room.user_ids = []
                    users = User.where_in('id', user_ids).get()
                    updated = False
                    for user in users:
                        if user.id not in chat_room.user_ids:
                            chat_room.user_ids.append(user.id)
                            updated = True
                    if updated is True:
                        chat_room.save()
                    self.make_response({'ok': True}, self._command_ok, ws)

    # if user_ids is empty user will delete himself
    def del_user_from_chat(self, ws):
        if self.is_logged_in(ws):
            data = self._json_data
            chat_id = data.get('chat_id')
            user_ids = data.get('user_ids')
            if user_ids is None:
                user_ids = [ws.user_id]
            if chat_id is not None and user_ids:
                chat_room = ChatRoom.where('id', '=', chat_id).first()
                if chat_room is not None:
                    if chat_room.user_ids is not None:
                        chat_room.user_ids = list(set(chat_room.user_ids) - set(user_ids))
                        chat_room.save()
                    self.make_response({'ok': True}, self._command_ok, ws)

    def message(self, ws):
        if self.is_logged_in(ws):
            chat_to = None
            user_to = None
            message_obj = None
            data = self._json_data

            possible_kinds = ['text', 'doc', 'image'];
            kind = data.get('kind', 'text')
            if kind not in possible_kinds:
                kind = 'text'
            id_to_user = data.get('id_to_user', False)
            id_to_chat = data.get('id_to_chat', False)
            message = data.get('message')

            if message and type(message) is str:
                message_obj = Message()
                message_obj.id_from = ws.user_id
                message_obj.message = message
                message_obj.kind = kind
                if id_to_user:
                    user_to = User.where('id', '=', id_to_user).first()
                    if user_to is not None:
                        message_obj.id_to_user = user_to.id
                        message_obj.save()
                elif id_to_chat:
                    chat_to = ChatRoom.where('id', '=', id_to_chat).first()
                    if chat_to is not None:
                        message_obj.id_to_chat = chat_to.id
                        message_obj.save()

            if not message_obj.id:
                message_obj = None
            if message_obj is not None:
                if kind == 'image':
                    user_file = UserFile.get_by_urls(message, is_single=True)
                    if user_file is not None:
                        user_file.message_id = message_obj.id
                        user_file.save()
                if chat_to is not None:
                    # response = {'id_to_chat': id_to_chat, 'message': message, 'ident': message_obj.id, 'kind': kind}
                    for chat_user_id in chat_to.user_ids:
                        reciever = Socket.clients(chat_user_id)
                        if reciever is not None and str(chat_user_id) != str(ws.user_id):
                            self.make_response(message_obj.format_receiver(), self._command_receiver, reciever)
                elif user_to:
                    # response = {'id_to_user': id_to_user, 'message': message, 'ident': message_obj.id, 'kind': kind}
                    reciever = Socket.clients(user_to.id)
                    if reciever is not None and str(user_to.id) != str(ws.user_id):
                        message_obj.is_viewed = True
                        message_obj.save()
                        self.make_response(message_obj.format_receiver(), self._command_receiver, reciever)
                self.make_response(message_obj.format_sender(), self._command_ok, ws)
            else:
                self.make_response({"ok": False}, self._command_ok, ws)

    def update_message(self, ws):
        if self.is_logged_in(ws):
            data = self._json_data
            message_id = data.get('message_id')
            message = data.get('message')
            if message_id is not None and message is not None and type(message) is str:
                message_obj = Message.where('id', message_id).first()
                if message_obj is not None and str(message_obj.id_from) == str(ws.user_id):
                    message_obj.is_updated = True
                    message_obj.message = message
                    message_obj.save()
                    if message_obj.id_to_user:
                        reciever = Socket.clients(message_obj.id_to_user)
                        if self.is_logged_in(reciever, with_error_response=False):
                            self.make_response(message_obj.format_receiver(), self._command_receiver, reciever)
                    elif message_obj.id_to_chat:
                        if message_obj.chat is not None:
                            if message_obj.chat.user_ids is not None and type(message_obj.chat.user_ids) is list:
                                for user_id in message_obj.chat.user_ids:
                                    reciever = Socket.clients(user_id)
                                    if self.is_logged_in(reciever, with_error_response=False):
                                        self.make_response(message_obj.format_receiver(), self._command_receiver, reciever)
                    self.make_response(message_obj.format_sender(), self._command_ok, ws)

    def unread_messages(self, ws):
        if self.is_logged_in(ws):
            data = self._json_data
            limit = data.get('limit', 20)
            if type(limit) is str:
                limit = int(limit)
            if limit > 500:
                limit = 20
            messages = Message.where('id_to_user', ws.user_id)\
                .where('is_viewed', False)\
                .order_by('created_at', 'desc')\
                .limit(limit)\
                .get()
            for message in messages:
                # optimize "where id in()" ?
                message.is_viewed = True
                message.save()
                self.make_response(message.format_receiver(), self._command_ok, ws)
            count = Message.count_unread(ws.user_id)
            if count > 0:
                self.make_response({'count_unread': count}, 'new_messages', ws)
