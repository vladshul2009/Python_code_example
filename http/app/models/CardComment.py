from orator import SoftDeletes
from orator.orm import has_one, has_many, belongs_to

from core.models.ModelCore import ModelCore


class CardComment(ModelCore, SoftDeletes):
    __table__ = 'card_comments'

    def format_default(self):
        from app.helpers.Config import Config
        response = self._left_keys(['id', 'author_id', 'card_id', 'comment', 'created_at', 'kind'])
        if response['kind'] != 'text':
            response['comment'] = Config.get('host') + response['comment']
        return response

    @belongs_to('board_id')
    def board(self):
        from app.models.Board import Board
        return Board

    @belongs_to('card_id')
    def card(self):
        from app.models.Card import Card
        return Card

    @has_one
    def author(self):
        from app.models.User import User
        return User
