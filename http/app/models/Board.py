from orator import SoftDeletes
from orator.orm import has_many, has_one, belongs_to_many
import datetime

from core.models.ModelCore import ModelCore
from app.models.User import User
from app.models.Card import Card


class Board(ModelCore, SoftDeletes):
    __table__ = 'boards'

    __hidden__ = ['updated_at', 'deleted_at']

    rules_create = {
        'name': 'required',
        'owner_id': 'required|integer'
    }

    def format_details(self):
        files_map = {}
        comment_files = self.card_comments_files().get()
        for comment_file in comment_files:
            if files_map.get(comment_file.id):
                files_map[comment_file.id].append(comment_file.format_default())
            else:
                files_map[comment_file.id] = [comment_file.format_default()]

        comments_map = {}
        comments = self.comments().order_by('created_at', 'DESC').get()
        for comment in comments:
            formatted_comment = comment.format_default()
            if comments_map.get(comment.card_id):
                comments_map[comment.card_id].append(formatted_comment)
            else:
                comments_map[comment.card_id] = [formatted_comment]

        # TODO: make optimization for this one like it made above, and we will have only 4 simple queries
        lists = []
        board_lists = self.lists().order_by('position', 'ASC').get()
        for _list in board_lists:
            list_cards = _list.cards().order_by('position', 'ASC').get()
            cards = []
            for card in list_cards:
                formatted_card = card.format_default()
                formatted_card['comments'] = []
                if comments_map.get(formatted_card['id']):
                    formatted_card['comments'] = comments_map.get(formatted_card['id'])

                cards.append(formatted_card)
            formatted_list = _list.format_default()
            formatted_list['cards'] = cards
            lists.append(formatted_list)
        response = self._left_keys(['id', 'name'])
        response['lists'] = lists
        return response

    def format_list(self):
        return self._left_keys(['id', 'name'])

    # denormalization fo faster access
    @has_many
    def comments(self):
        from app.models.CardComment import CardComment
        return CardComment

    # denormalization fo faster access
    @has_many('board_id', 'id')
    def card_comments_files(self):
        from app.models.CardComment import CardComment
        return CardComment.where('kind', '<>', 'text')

    @has_many
    def lists(self):
        from app.models.BoardList import BoardList
        return BoardList

    @has_many
    def cards(self):
        return Card

    @has_one
    def owner(self):
        from app.models.User import User
        return User

    def is_owner(self, user_id):
        return str(self.owner_id) == str(user_id)

    @staticmethod
    def user_has_access(board, user_id):
        if str(board.owner_id) == str(user_id):
            return True
        user_assigned = Board.where('id', board.id).where_has('users', lambda q: q.where('user_id', '=', user_id)).count()
        if user_assigned:
            return True
        return False

    @belongs_to_many('board_users', 'board_id', 'user_id')
    def users(self):
        return User

    def user_ids(self):
        return self.users().get().lists('id')
