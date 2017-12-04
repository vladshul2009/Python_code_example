from core.helpers.CoreHelpers import CoreHelpers
from sockets.helpers.Socket import Socket

from app.models.Message import Message


class BaseHandler:
    _command_ok = None
    _command_receiver = None
    _json_data = {}
    __receivers = []

    def __init__(self, data, route=None):
        self._json_data = data
        if route is not None and route[2] is not None:
            for route_command in route[2]:
                route_arr = route_command.strip().split(':')
                if route_arr[0] == 'ok':
                    self._command_ok = route_arr[1]
                if route_arr[0] == 'receiver':
                    self._command_receiver = route_arr[1]

    def is_logged_in(self, ws=None, with_error_response=True):
        if ws is not None and getattr(ws, 'user_id', False):
            Socket.update_last_connection(ws)
            return True
        if with_error_response:
            self.make_response({}, 'do_login', ws)
        return False

    def authorize(self, ws):
        Socket.authorize(ws, self._json_data)
        if not getattr(ws, 'user_id', False):
            self.make_response({}, "do_login", ws)
        else:
            Socket.update_last_connection(ws)
            self.make_response({"value": True}, self._command_ok, ws)
            count = Message.count_unread(ws.user_id)
            if count > 0:
                self.make_response({'count_unread': count}, 'new_messages', ws)

    def make_response(self, data, command, receiver=None):
        data = CoreHelpers.convert_to_string(data)
        import json
        response = {
            'command': command,
            'data': data
        }
        response = json.dumps(response, ensure_ascii=False)
        if receiver is not None:
            receiver.send_str(response)
        elif len(self.__receivers) > 0:
            for receiver in self.__receivers:
                receiver.send_str(response)

    def add_reciever(self, receiver):
        if receiver not in self.__receivers and self.is_logged_in(receiver):
            self.__receivers.append(receiver)

    def del_reciever(self, reciever):
        if reciever in self.__receivers:
            self.__receivers.remove(reciever)
