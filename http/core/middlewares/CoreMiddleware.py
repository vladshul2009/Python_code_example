import abc
from core.helpers.Config import Config


class CoreMiddleware(metaclass=abc.ABCMeta):

    __controller = None
    __next = True

    def __init__(self, controller):
        self.__controller = controller

    @abc.abstractmethod
    def handle(self):
        ...

    def get_next(self):
        return self.__next

    def get_controller(self):
        return self.__controller

    def set_next(self, is_next):
        self.__next = is_next
        return self

    def get_response(self):
        return self.__controller.get_response()

    def send_actions(self, actions):
        self.set_next(False)
        self.get_controller().set_status(Config.get('response_codes.error'))
        self.get_controller().make_response({}, actions=actions)

    def send_message(self, message):
        self.set_next(False)
        self.get_controller().set_status(Config.get('response_codes.message'))
        self.get_controller().make_response({}, message=message)

    def set_api_token_error_status(self):
        self.get_controller().set_status(Config.get('response_codes.api_token_error'))