from core.models.ModelCore import ModelCore as ModelCore
from sockets.helpers.Socket import Socket
from orator.orm import has_one


class Message(ModelCore):

    __table__ = 'messages'

    def format_default(self):
        response = self._left_keys(['id', 'message', 'created_at', 'kind', 'is_updated'])
        return response

    def format_last(self, user_id):
        is_mine = False
        if self.id_from == user_id:
            is_mine = True
        response = self._left_keys(['id', 'message', 'created_at', 'kind', 'is_updated'])
        response['is_mine'] = is_mine
        return response

    def format_sender(self):
        response = self._left_keys(['id', 'message', 'created_at', 'kind', 'is_updated', 'id_to_chat', 'id_to_user'])
        if response.get('id_to_chat'):
            del response['id_to_user']
        if response.get('id_to_user'):
            del response['id_to_chat']
            response['user_id'] = response['id_to_user']
            del response['id_to_user']
        response['is_owner'] = True
        return response

    def format_receiver(self):
        response = self._left_keys(['id', 'message', 'created_at', 'kind', 'is_updated', 'id_from'])
        response['user_id'] = response['id_from']
        del response['id_from']
        response['is_owner'] = False
        return response

    @has_one('id_to_chat', 'id')
    def chat(self):
        from app.models.ChatRoom import ChatRoom
        return ChatRoom

    @staticmethod
    def count_unread(user_id):
        return Message.where('id_to_user', user_id).where('is_viewed', False).count()
