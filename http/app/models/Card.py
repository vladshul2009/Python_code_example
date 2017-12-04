from orator import SoftDeletes
from orator.orm import has_many, has_one, belongs_to

from core.models.ModelCore import ModelCore
from core.models.Position import Position


class Card(ModelCore, SoftDeletes, Position):
    __table__ = 'cards'
    _position_group = ['board_list_id']
    _position_add_to_end = False
    _array_fields = ['assignee_ids']

    def format_default(self):
        # files = []
        # for comment in self.files_comments().get():
        #     files.append(comment.format_default())
        response = self._left_keys(['id', 'name', 'color', 'board_list_id'])
        # response['files'] = files
        return response

    @has_many
    def files_comments(self):
        from app.models.CardComment import CardComment
        return CardComment.where('kind', '<>', 'text')

    @has_one
    def creator(self):
        from app.models.User import User
        return User

    @belongs_to
    def board_list(self):
        from app.models.BoardList import BoardList
        return BoardList

    @belongs_to('board_id')
    def board(self):
        from app.models.Board import Board
        return Board

    def user_has_access(self, user_id):
        from app.models.Board import Board
        board = self.board
        if board:
            return Board.user_has_access(board, user_id)
        return False
