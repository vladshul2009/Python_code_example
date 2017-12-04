from app.models.User import User
from app.models.Board import Board
from app.models.Card import Card
from app.models.CardComment import CardComment
from app.models.UploadedFile import UploadedFile
from app.models.BoardList import BoardList
from sockets.handlers.BaseHandler import BaseHandler
from sockets.helpers.EventBoard import EventBoard
import datetime


class BoardHandler(BaseHandler):

    _json_data = None

    def _before(self, ws):
        self._json_data = self._json_data
        return True if self.is_logged_in(ws) else False

    def get_board(self, ws):
        board_id = self._json_data.get('board_id')
        board = Board.where('id', board_id).with_('lists').first()
        if board is not None:
            if Board.user_has_access(board, ws.user_id):
                self.make_response({'board': board.format_details()}, self._command_ok, ws)

    def get_boards(self, ws):
        user = User.where('id', ws.user_id).first()
        if user is not None:
            formatted_boards = []
            for board in user.boards:
                cards_count = board.cards().count('id')
                cards_deadline_today = board.cards().where('deadline', datetime.datetime.now().date()).count('id')
                formatted_board = board.format_list()
                formatted_board['attributes'] = {
                    'cards_count': cards_count,
                    'cards_deadline_count': cards_deadline_today
                }
                formatted_boards.append(formatted_board)
            self.make_response({'boards': formatted_boards}, self._command_ok, ws)

    def create_board(self, ws):
        board = Board()
        board.owner_id = ws.user_id
        board.name = self._json_data.get('name')
        vd = board.validate('rules_create')
        if vd.passes():
            board.save()
            formatted_board = board.format_details()
            del formatted_board['lists']
            formatted_board['attributes'] = {}
            self.make_response(formatted_board, self._command_ok, ws)
        else:
            self.make_response({'ok': False}, 'create_error', ws)

    def update_board(self, ws):
        board_id = self._json_data.get('board_id', False)
        name = self._json_data.get('name')
        if board_id and name:
            board = Board.where('id', board_id).first()
            if board is not None and board.is_owner(ws.user_id):
                board.name = name
                board.save()
                EventBoard.board_updated(board, ws)
                formatted_board = board.format_details()
                del formatted_board['lists']
                formatted_board['attributes'] = {}
                self.make_response(formatted_board, self._command_ok, ws)

    def delete_board(self, ws):
        board_id = self._json_data.get('board_id', False)
        if board_id:
            board = Board.where('id', board_id).first()
            if board is not None and board.is_owner(ws.user_id):
                EventBoard.board_deleted(board, ws)
                board.delete()
                self.make_response({}, self._command_ok, ws)

    def create_board_list(self, ws):
        board_id = self._json_data.get('board_id')
        board = Board.where('id', board_id).first()
        if board is not None and board.is_owner(ws.user_id):
            board_list = BoardList()
            board_list.board_id = board.id
            board_list.name = self._json_data.get('name')
            vd = board_list.validate('rules_create')
            if vd.passes():
                board_list.save()
                EventBoard.board_list_created(board_list, ws)
                self.make_response({'board_list': board_list.format_default()}, self._command_ok, ws)

    def update_board_list(self, ws):
        list_id = self._json_data.get('list_id', False)
        name = self._json_data.get('name')
        if list_id and name:
            board_list = BoardList.where('id', list_id).first()
            if board_list is not None and board_list.board is not None:
                if board_list.board.is_owner(ws.user_id):
                    board_list.name = name
                    board_list.save()
                    EventBoard.board_list_updated(board_list, ws)
                    self.make_response({}, self._command_ok, ws)

    def delete_board_list(self, ws):
        list_id = self._json_data.get('list_id', False)
        board_list = BoardList.where('id', list_id).first()
        if board_list is not None and board_list.board is not None:
            if board_list.board.is_owner(ws.user_id):
                EventBoard.board_list_deleted(board_list, ws)
                board_list.delete()
                self.make_response({}, self._command_ok, ws)

    def create_card(self, ws):
        data = self._json_data
        list_id = data.get('list_id')
        name = data.get('name')
        description = data.get('description', None)
        color = data.get('color', 'CCCCCC')
        deadline = data.get('deadline', None)
        if list_id is not None and name:
            board_list = BoardList.where('id', list_id).first()
            if board_list is not None:
                card = Card()
                card.board_list_id = board_list.id
                card.board_id = board_list.board_id
                card.creator_id = ws.user_id
                card.name = name
                card.description = description
                card.color = color
                card.deadline = deadline
                card.save()
                EventBoard.card_created(card, board_list, ws)
                self.make_response({'card': card.format_default()}, self._command_ok, ws)

    def update_card(self, ws):
        data = self._json_data
        card_id = data.get('card_id', False)
        name = data.get('name')
        description = data.get('description', None)
        color = data.get('color', None)
        card = Card.where('id', card_id).first()
        if card is not None and card.user_has_access(ws.user_id):
            card.name = name if name is not None else card.name
            card.description = description if description is not None else card.description
            card.color = color if color is not None else card.color
            if card.get_dirty():
                card.save()
                EventBoard.card_updated(card, ws)
            self.make_response({'card': card.format_default()}, self._command_ok, ws)

    def delete_card(self, ws):
        card_id = self._json_data.get('card_id', False)
        card = Card.where('id', card_id).first()
        if card is not None:
            if card.user_has_access(ws.user_id):
                EventBoard.card_deleted(card, ws)
                card.delete()
                self.make_response({}, self._command_ok, ws)

    def add_card_comment(self, ws):
        kinds = ['text', 'doc', 'image']
        kind = self._json_data.get('kind', 'text')
        card_id = self._json_data.get('card_id', False)
        comment = self._json_data.get('comment', False)
        if card_id and comment and kind in kinds:
            card = Card.where('id', card_id).first()
            if card is not None:
                card_comment = CardComment()
                card_comment.card_id = card.id
                card_comment.author_id = ws.user_id
                card_comment.board_id = card.board_id
                card_comment.kind = kind
                if kind is not 'text':
                    uploaded_files = UploadedFile.get_by_urls([comment])
                    for uploaded_file in uploaded_files:
                        card_comment.comment = uploaded_file.file
                        card_comment.save()
                        uploaded_file.delete()
                        EventBoard.card_comment_added(card_comment, card, ws)
                        formatted_comment = card_comment.format_default()
                        self.make_response({'card_comment': formatted_comment}, self._command_ok, ws)
                else:
                    card_comment.comment = comment
                    card_comment.save()
                    EventBoard.card_comment_added(card_comment, card, ws)
                    self.make_response({'card_comment': card_comment.format_default()}, self._command_ok, ws)

    def update_card_comment(self, ws):
        kinds = ['text', 'doc', 'image']
        kind = self._json_data.get('kind', 'text')
        comment_id = self._json_data.get('comment_id', False)
        comment = self._json_data.get('comment', '')
        if comment_id and kind in kinds:
            card_comment = CardComment.where('id', comment_id).first()
            if card_comment:
                if card_comment.author_id == ws.user_id or card_comment.board.owner_id == card_comment.author_id:
                    card_comment.kind = kind
                    if kind is not 'text':
                        uploaded_files = UploadedFile.get_by_urls([comment])
                        for uploaded_file in uploaded_files:
                            card_comment.comment = uploaded_file.file
                            card_comment.save()
                            uploaded_file.delete()
                            self.make_response({'card_comment': card_comment.format_default()}, self._command_ok, ws)
                    else:
                        card_comment.comment = comment
                        card_comment.save()
                        self.make_response({'card_comment': card_comment.format_default()}, self._command_ok, ws)
                else:
                    self.make_response({}, 'permission_denied', ws)

    def delete_card_comment(self, ws):
        comment_id = self._json_data.get('comment_id', False)
        if comment_id:
            card_comment = CardComment.where('id', comment_id).first()
            if card_comment:
                if card_comment.author_id == ws.user_id:
                    EventBoard.card_comment_deleted(card_comment, ws)
                    card_comment.delete()
                    self.make_response({}, self._command_ok, ws)

    # assign can board's owner or any user from board
    def add_card_assigners(self, ws):
        card_id = self._json_data.get('card_id', False)
        assigner_ids = self._json_data.get('assigner_ids', False)
        real_ids = []
        if card_id and assigner_ids:
            card = Card.where('id', card_id).first()
            board = card.board
            if card is not None and board is not None and board.user_has_access(board, ws.user_id):
                if assigner_ids:
                    assigners = User.where_in('id', assigner_ids).get()
                    if (assigners):
                        board_user_ids = board.user_ids()
                        for user in assigners:
                            if user.id in board_user_ids:
                                real_ids.append(user.id)
                        real_ids = list(set(real_ids) - set(card.assignee_ids))
                if real_ids:
                    card.assignee_ids += real_ids
                    card.save()
                self.make_response({'card': card.format_default(), 'assigners': card.assignee_ids}, self._command_ok, ws)

    # delete assigners can only board owner
    def del_card_assigners(self, ws):
        card_id = self._json_data.get('card_id', False)
        assigner_ids = self._json_data.get('assigner_ids', False)
        if card_id and assigner_ids:
            card = Card.where('id', card_id).first()
            board = card.board
            if card is not None and board is not None and board.is_owner(ws.user_id):
                card.assignee_ids = list(set(card.assignee_ids) - set(assigner_ids))
                card.save()
                self.make_response({'card': card.format_default(), 'assigners': card.assignee_ids}, self._command_ok, ws)

    def move_board_list(self, ws):
        data = self._json_data
        list_id = data.get('list_id')
        pos = data.get('pos')
        if list_id is not None and pos > 0:
            board_list = BoardList.where('id', list_id).first()
            if board_list is not None and board_list.user_has_access(ws.user_id):
                board_list.set_pos(pos)
                self.make_response({}, self._command_ok, ws)

    def __get_positions_order(self, board_list_id):
        positions_order = []
        cards = Card.where('board_list_id', board_list_id).order_by('position', 'asc').get()
        for list_card in cards:
            positions_order.append(list_card.id)
        return positions_order;

    def move_card(self, ws):
        data = self._json_data
        list_id = data.get('list_id', False)
        card_id = data.get('card_id')
        pos = int(data.get('pos')) + 1
        if card_id is not None and pos > 0:
            card = Card.where('id', card_id).first()
            if card is not None and card.user_has_access(ws.user_id):
                # change board list for card
                if list_id and card.board_list_id != list_id:
                    other_board_list = BoardList.where('id', list_id).first()
                    # allow move card only in a same boardboard_list
                    if other_board_list is not None and other_board_list.board_id == card.board_list.board.id:
                        card.board_list_id = other_board_list.id
                        card.position = card.get_last_pos() + 1
                        card.save()
                        if pos < card.position:
                            card.set_pos(pos)
                            EventBoard.card_moved(card, ws)
                        positions_order = self.__get_positions_order(card.board_list_id)
                        self.make_response({'cards_order': positions_order, 'list_id': card.board_list_id}, self._command_ok, ws)
                else:
                    card.set_pos(pos)
                    positions_order = self.__get_positions_order(card.board_list_id)
                    EventBoard.card_moved(card, ws)
                    self.make_response({'cards_order': positions_order, 'list_id': card.board_list_id}, self._command_ok, ws)

    def add_board_users(self, ws):
        data = self._json_data
        board_id = data.get('board_id')
        user_ids = data.get('user_ids', [])
        if user_ids and board_id:
            board = Board.where('id', board_id).first()
            user_ids = User.where_in('id', user_ids).get().lists('id')
            if board and user_ids:
                if board.is_owner(ws.user_id):
                    if ws.user_id in user_ids:
                        user_ids.remove(ws.user_id)
                    if user_ids:
                        user_ids = list(set(user_ids) - set(board.user_ids()))
                        if user_ids:
                            board.users().attach(user_ids)
                    self.make_response({'user_ids': user_ids}, self._command_ok, ws)

    def delete_board_users(self, ws):
        data = self._json_data
        board_id = data.get('board_id')
        user_ids = data.get('user_ids', [])
        if board_id:
            board = Board.where('id', board_id).first()
            if board is not None:
                if user_ids:
                    if board.is_owner(ws.user_id):
                        board.users().detach(user_ids)
                        self.make_response({}, self._command_ok, ws)
                else:
                    board.users().detach(ws.user_id)
                    self.make_response({}, self._command_ok, ws)
