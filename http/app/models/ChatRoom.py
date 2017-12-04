from core.models.ModelCore import ModelCore as ModelCore
from orator.orm import belongs_to
from orator import SoftDeletes
from app.models.User import User


class ChatRoom(ModelCore, SoftDeletes):

    __table__ = 'chat_rooms'
    _array_fields = ['user_ids']

    @belongs_to('creator_id')
    def creator(self):
        return User
