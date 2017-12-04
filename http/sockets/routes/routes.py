from sockets.handlers.ChatHandler import ChatHandler
from sockets.handlers.BoardHandler import BoardHandler


routes_map = {
    ('authorize', ChatHandler, ('ok:authorized',)),
    ('message', ChatHandler, ('ok:receive_message', 'receiver:receive_message')),
    ('update_message', ChatHandler, ('ok:message_sent', 'receiver:receive_message')),
    ('unread_messages', ChatHandler, ('ok:receive_message',)),
    ('create_chat_room', ChatHandler, ('ok:room_created',)),
    ('del_chat_room', ChatHandler, ('ok:chat_deleted',)),
    ('add_user_to_chat', ChatHandler, ('ok:users_added',)),
    ('del_user_from_chat', ChatHandler, ('ok:users_deleted',)),

    # our "demo" application aka trello:
    ('create_board', BoardHandler, ('ok:board_created',)),
    ('update_board', BoardHandler, ('ok:board_updated',)),
    ('delete_board', BoardHandler, ('ok:board_deleted',)),
    ('create_board_list', BoardHandler, ('ok:board_list_created',)),
    ('update_board_list', BoardHandler, ('ok:board_list_updated',)),
    ('delete_board_list', BoardHandler, ('ok:board_list_deleted',)),
    ('create_card', BoardHandler, ('ok:card_created',)),
    ('update_card', BoardHandler, ('ok:card_updated',)),
    ('delete_card', BoardHandler, ('ok:card_deleted',)),
    ('add_card_comment', BoardHandler, ('ok:card_commented',)),
    ('update_card_comment', BoardHandler, ('ok:comment_updated',)),
    ('delete_card_comment', BoardHandler, ('ok:comment_deleted',)),
    ('add_card_files', BoardHandler, ('ok:card_files_added',)),
    ('add_card_assigners', BoardHandler, ('ok:card_assigners_added',)),
    ('del_card_assigners', BoardHandler, ('ok:card_assigners_deleted',)),
    ('get_board', BoardHandler, ('ok:board_found',)),
    ('get_boards', BoardHandler, ('ok:boards',)),
    ('move_board_list', BoardHandler, ('ok:board_list_moved',)),
    ('move_card', BoardHandler, ('ok:card_moved',)),
    ('add_board_users', BoardHandler, ('ok:users_added',)),
    ('delete_board_users', BoardHandler, ('ok:board_users_deleted',)),
    ('test', BoardHandler, ('ok:tested',)),
}
