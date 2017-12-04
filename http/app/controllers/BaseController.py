from core.controllers.CoreController import CoreController as CoreController
from core.helpers.Config import Config
from core.helpers.Lang import Lang


class BaseController(CoreController):

    __user = None

    def __init__(self, request):
        super().__init__(request)

    def index(self, action, version):
        self.__set_lang()
        return super().index(action, version)

    def set_user(self, user):
        self.__user = user

    def get_user(self):
        return self.__user

    def __set_lang(self):
        default_lang = Config.get('default.lang')
        current_lang = None
        get_params = self.get()
        if get_params is not None and 'lang' in get_params:
            if Lang.exists(get_params['lang']):
                current_lang = get_params['lang']
        if current_lang is None:
            post_params = self.post()
            if post_params is not None and 'lang' in post_params:
                if Lang.exists(post_params['lang']):
                    current_lang = post_params['lang']
        if current_lang is None:
            current_lang = default_lang
        Lang.set(current_lang)

    def get_offset(self):
        offset = 0
        try:
            json_data = self.json()
            offset = int(json_data['offset']) if json_data and 'offset' in json_data.keys() else 0
        except:
            pass
        return offset
