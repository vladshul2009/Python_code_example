import abc
import hashlib

from core.helpers.Config import Config
from core.helpers.CoreHelpers import CoreHelpers


class CoreController(metaclass=abc.ABCMeta):
    __response = None
    __request = None
    __status = 200
    __postParams = None
    __getParams = None
    __json_data = None
    __response_format = None
    __response_hash = ''

    def __init__(self, request):
        self.__request = request

    def index(self, action, version):
        return self.__do_command(version, action)

    def __do_command(self, version, command):
        action = command + '_' + version
        if hasattr(self, action):
            if getattr(self, '_before'):
                self._before()
            return getattr(self, action)()
        elif hasattr(self, command):
            return getattr(self, command)()
        else:
            self.set_status(404).make_response({}, actions=["method_not_found"])

    async def index_async(self, action, version):
        await self.__do_command_async(version, action)

    async def __do_command_async(self, version, command):
        action = command + '_' + version
        if hasattr(self, action):
            await getattr(self, action)()
        elif hasattr(self, command):
            await getattr(self, command)()
        else:
            self.set_status(404).make_response({}, actions=["method_not_found"])

    def reset_response(self):
        self.__response = None

    def make_response(self, data, message=None, actions=[], format='json', values_is_string=True):
        self.__response_format = format
        if self.__response:
            raise Exception("You can execute make_response only once per request.")

        if format == 'json':
            if values_is_string:
                data = CoreHelpers.convert_to_string(data=data)
                self.__response_hash = CoreHelpers.response_hash
                if self.__json_data is not None and self.__json_data.get('hash') is not None:
                    md5 = hashlib.md5()
                    md5.update(self.__response_hash.encode('utf-8'))
                    server_hash = md5.hexdigest()
                    if server_hash == self.__json_data.get('hash'):
                        self.set_status(Config.get('response_codes.nothing_changed'))
                        data = {}
            self.__response = {
                "data": data,
                "actions": actions,
                "message": "" if message is None else str(message)
            }
        elif format == 'html' or format == 'text':
            self.__response = str(data)
        else:
            raise Exception('Unknown response format.')

    def make_actions(self, actions):
        self.set_status(Config.get('response_codes.error'))
        self.make_response({}, actions=actions)

    def make_message(self, message, actions=[]):
        self.set_status(Config.get('response_codes.message'))
        self.make_response({}, message=message, actions=actions)

    def get_response_format(self):
        return self.__response_format

    def get_response(self):
        return self.__response

    def get_request(self):
        return self.__request

    def set_status(self, status):
        if type(status) != int:
            raise Exception("Response status code must be integer.")
        if status < 100 or status >= 600:
            raise Exception("Incorrect response status code: " + status)

        self.__status = status
        return self

    def set_api_token_error_status(self):
        self.set_status(Config.get('response_codes.api_token_error'))

    def get_status(self):
        return self.__status

    def set_post_params(self, post):
        self.__postParams = self.__make_dict(post.items())
        return self

    def set_get_params(self, get):
        self.__getParams = self.__make_dict(get)
        return self

    def set_json_data(self, json_data):
        self.__json_data = json_data
        return self

    def get(self, name=None, default=None):
        if self.__getParams is None:
            return None
        if name is None:
            return self.__getParams
        elif name in self.__getParams:
            return self.__getParams[name]
        else:
            return default

    def post(self, name=None, default=None):
        if self.__postParams is None:
            return None
        if name is None:
            return self.__postParams
        elif name in self.__postParams:
            return self.__postParams[name]
        else:
            return default

    def json(self):
        return self.__json_data

    def input(self, name=None, default=None):
        result = {**self.__getParams, **self.__postParams}
        if name is None:
            return result
        elif name in result:
            return result[name]
        else:
            return default

    def __make_dict(self, mdict):
        result = {}
        if mdict is not None:
            for element in mdict:
                dict_key = element[0][:-2] if element[0][-2:] == '[]' else element[0]
                if dict_key in result:
                    result[dict_key].append(element[1])
                else:
                    result[dict_key] = [element[1]]
            for key in result.keys():
                if len(result[key]) == 1:
                    result[key] = result[key][0]
        return result

    def __add_to_response_hash(self, key, value):
        if self.__response_hash != '':
            self.__response_hash += '|'
        self.__response_hash += key + '=' + value

    def get_response_hash(self):
        return self.__response_hash

    # left only specified keys in dictionary
    def left_keys(self, data, keys):
        new_dict = {}
        if data:
            for key, val in data.items():
                if key in keys:
                    new_dict[key] = val
        return new_dict

    # remove specified keys from dictionary
    def unset_keys(self, data, keys):
        new_dict = {}
        if data:
            for key, val in data.items():
                if key not in keys:
                    new_dict[key] = val
        return new_dict
