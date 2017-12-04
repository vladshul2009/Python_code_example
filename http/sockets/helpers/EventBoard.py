import json

from app.models.Notification import Notification


class EventBoard:

    @staticmethod
    def _get_notification(name, entity, action):
        notification = Notification()
        notification.entity = name
        notification.entity_id = entity.id
        notification.kind = 'socket'
        notification.action = action
        return notification

    @staticmethod
    def board_created():
        pass

    @staticmethod
    def board_updated(board, ws):
        n = EventBoard._get_notification('board', board, 'updated')
        n.sender_id = ws.user_id
        n.user_ids = board.user_ids()
        message = 'User ' + str(ws.user_id) + ' updated board: ' + board.name
        result = {
            'command': 'board_updated',
            'data': {'message': message, 'board': board.format_list()}
        }
        push_result = {
            'title': 'Board updated.',
            'data': {},
            'message': message
        }
        n.data = json.dumps(result, ensure_ascii=False)
        n.push_data = json.dumps(push_result, ensure_ascii=False)
        n.save()

    @staticmethod
    def board_deleted(board, ws):
        Notification.where({'entity_id': board.id, 'entity': 'board'}).delete()
        n = EventBoard._get_notification('board', board, 'deleted')
        n.sender_id = ws.user_id
        n.user_ids = board.user_ids()
        message = 'User ' + str(ws.user_id) + ' deleted board: ' + board.name
        result = {
            'command': 'board_deleted',
            'data': {'message': message}
        }
        push_result = {
            'title': 'Board deleted.',
            'data': {},
            'message': message
        }
        n.data = str(result)
        n.push_data = json.dumps(push_result, ensure_ascii=False)
        n.save()

    @staticmethod
    def board_list_created(board_list, ws):
        board = board_list.board
        if board is not None:
            n = EventBoard._get_notification('board_list', board_list, 'board_list_created')
            n.sender_id = ws.user_id
            n.user_ids = board.user_ids()
            message = 'User ' + str(ws.user_id) + ' created board list: ' + board_list.name
            result = {
                'command': 'board_list_created',
                'data': {'message': message}
            }
            push_result = {
                'title': 'Board list created.',
                'data': {},
                'message': message
            }
            n.data = str(result)
            n.push_data = json.dumps(push_result, ensure_ascii=False)
            n.save()

    @staticmethod
    def board_list_updated(board_list, ws):
        board = board_list.board
        if board is not None:
            n = EventBoard._get_notification('board_list', board_list, 'board_list_updated')
            n.sender_id = ws.user_id
            n.user_ids = board.user_ids()
            message = 'User ' + str(ws.user_id) + ' updated board list: ' + board_list.name
            result = {
                'command': 'board_list_updated',
                'data': {'message': message}
            }
            push_result = {
                'title': 'Board list updated.',
                'data': {},
                'message': message
            }
            n.data = str(result)
            n.push_data = json.dumps(push_result, ensure_ascii=False)
            n.save()

    @staticmethod
    def board_list_deleted(board_list, ws):
        Notification.where({'entity_id': board_list.id, 'entity': 'board_list'}).delete()
        board = board_list.board
        if board is not None:
            n = EventBoard._get_notification('board_list', board_list, 'board_list_updated')
            n.sender_id = ws.user_id
            n.user_ids = board.user_ids()
            message = 'User ' + str(ws.user_id) + ' deleted board list: ' + board_list.name
            result = {
                'command': 'board_list_deleted',
                'data': {'message': message}
            }
            push_result = {
                'title': 'Board list deleted.',
                'data': {},
                'message': message
            }
            n.data = str(result)
            n.push_data = json.dumps(push_result, ensure_ascii=False)
            n.save()

    @staticmethod
    def card_created(card, board_list, ws):
        board = board_list.board
        if board is not None:
            n = EventBoard._get_notification('card', card, 'card_created')
            n.sender_id = ws.user_id
            n.user_ids = board.user_ids()
            message = 'User ' + str(ws.user_id) + ' created card: ' + card.name
            result = {
                'command': 'card_created',
                'data': {'message': message, 'card': card.format_default()}
            }
            push_result = {
                'title': 'Card created.',
                'data': {},
                'message': message
            }
            n.data = str(result)
            n.push_data = json.dumps(push_result, ensure_ascii=False)
            n.save()

    @staticmethod
    def card_updated(card, ws):
        n = EventBoard._get_notification('card', card, 'card_created')
        n.sender_id = ws.user_id
        n.user_ids = card.board_list.board.user_ids()
        message = 'User ' + str(ws.user_id) + ' created card: ' + card.name
        result = {
            'command': 'card_updated',
            'data': {'message': message, 'card': card.format_default()}
        }
        push_result = {
            'title': 'Card updated.',
            'data': {},
            'message': message
        }
        n.data = str(result)
        n.push_data = json.dumps(push_result, ensure_ascii=False)
        n.save()

    @staticmethod
    def card_moved(card, ws):
        n = EventBoard._get_notification('card', card, 'card_moved')
        n.sender_id = ws.user_id
        n.user_ids = card.board_list.board.user_ids()
        message = 'User ' + str(ws.user_id) + ' moved card to another position: ' + card.name
        result = {
            'command': 'card_moved',
            'data': {'message': message, 'card': card.format_default()}
        }
        push_result = {
            'title': 'Card moved.',
            'data': {},
            'message': message
        }
        n.data = str(result)
        n.push_data = json.dumps(push_result, ensure_ascii=False)
        n.save()

    @staticmethod
    def card_deleted(card, ws):
        Notification.where({'entity_id': card.id, 'entity': 'card'}).delete()
        n = EventBoard._get_notification('card', card, 'card_deleted')
        n.sender_id = ws.user_id
        n.user_ids = card.board_list.board.user_ids()
        message = 'User ' + str(ws.user_id) + ' deleted card: ' + card.name
        result = {
            'command': 'card_deleted',
            'data': {'message': message}
        }
        push_result = {
            'title': 'Card moved.',
            'data': {},
            'message': message
        }
        n.data = str(result)
        n.push_data = json.dumps(push_result, ensure_ascii=False)
        n.save()

    @staticmethod
    def card_comment_added(card_comment, card, ws):
        n = EventBoard._get_notification('card_comment', card, 'card_comment_added')
        n.sender_id = ws.user_id
        n.user_ids = card.board_list.board.user_ids()
        message = 'User ' + str(ws.user_id) + ' commented card: ' + card.name
        result = {
            'command': 'card_comment_added',
            'data': {'message': message}
        }
        push_result = {
            'title': 'Card comment added.',
            'data': {},
            'message': message
        }
        n.data = str(result)
        n.push_data = json.dumps(push_result, ensure_ascii=False)
        n.save()

    @staticmethod
    def card_comment_updated(card_comment, card, ws):
        n = EventBoard._get_notification('card_comment', card, 'card_comment_added')
        n.sender_id = ws.user_id
        n.user_ids = card.board_list.board.user_ids()
        message = 'User ' + str(ws.user_id) + ' updated card comment: ' + card.name
        result = {
            'command': 'card_comment_updated',
            'data': {'message': message}
        }
        push_result = {
            'title': 'Card comment updated.',
            'data': {},
            'message': message
        }
        n.data = str(result)
        n.push_data = json.dumps(push_result, ensure_ascii=False)
        n.save()

    @staticmethod
    def card_comment_deleted(card_comment, ws):
        card = card_comment.card
        n = EventBoard._get_notification('card_comment', card, 'card_comment_deleted')
        n.sender_id = ws.user_id
        n.user_ids = card.board_list.board.user_ids()
        message = 'User ' + str(ws.user_id) + ' deleted card: ' + card.name
        result = {
            'command': 'card_comment_deleted',
            'data': {'message': message}
        }
        push_result = {
            'title': 'Card comment deleted.',
            'data': {},
            'message': message
        }
        n.data = str(result)
        n.push_data = json.dumps(push_result, ensure_ascii=False)
        n.save()
