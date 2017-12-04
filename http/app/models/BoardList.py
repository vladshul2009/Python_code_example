from orator import SoftDeletes
from orator.orm import has_many, belongs_to

from core.models.ModelCore import ModelCore
from core.models.Position import Position
from app.models.Board import Board
from app.models.Card import Card


class BoardList(ModelCore, SoftDeletes, Position):
    __table__ = 'board_lists'

    __hidden__ = ['updated_at', 'deleted_at']

    _position_group = ['board_id']

    rules_create = {
        'name': 'required',
        'board_id': 'required'
    }

    def format_default(self):
        response = self._left_keys(['id', 'name'])
        return response

    @has_many
    def files(self):
        from app.models.UserFile import UserFile
        return UserFile

    @has_many
    def cards(self):
        return Card

    @belongs_to('board_id')
    def board(self):
        from app.models.Board import Board
        return Board

    def user_has_access(self, user_id):
        if self.board is not None:
            return Board.user_has_access(self.board, user_id)
        return False
