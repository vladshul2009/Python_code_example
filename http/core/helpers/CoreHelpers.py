import settings
from core.helpers.Config import Config


class CoreHelpers:
    response_hash = ''

    # check is type will converted to string
    @staticmethod
    def is_convertable(val):
        if type(val) is not bool and type(val) is not dict and type(val) is not list:
            return True
        return False

    # recursive method which converts data values to string
    @staticmethod
    def convert_to_string(data, target=None):
        if target is None:
            target = data

        if settings.CUR_APP_NAME == 'digimundus':
            return target

        if type(data) == dict:
            for key, val in data.items():
                if (key == 'file' or key == 'photo') and val:
                    val = Config.get('host') + val

                if key == 'id':
                    data['ident'] = data[key]
                    del data[key]
                    key = 'ident'

                if data[key] is None:
                    data[key] = ""
                    CoreHelpers.add_to_response_hash(key, "")
                elif CoreHelpers.is_convertable(val):
                    data[key] = str(val)
                    CoreHelpers.add_to_response_hash(key, data[key])
                elif type(val) is dict:
                    data[key] = CoreHelpers.convert_to_string(val, val)
                elif type(val) is list:
                    for i, list_val in enumerate(val):
                        if CoreHelpers.is_convertable(list_val):
                            data[key][i] = str(list_val)
                        elif type(list_val) is dict or type(list_val) is list:
                            data[key][i] = CoreHelpers.convert_to_string(list_val, list_val)
        elif type(data) == list:
            for i, list_val in enumerate(data):
                if CoreHelpers.is_convertable(list_val):
                    data[i] = str(list_val)
                else:
                    data[i] = CoreHelpers.convert_to_string(list_val, list_val)
        return target

    @staticmethod
    def add_to_response_hash(key, value):
        if CoreHelpers.response_hash != '':
            CoreHelpers.response_hash += '|'
        CoreHelpers.response_hash += key + '=' + value

    @staticmethod
    def get_base_path(path='app'):
        from pathlib import Path
        import os
        base_dir = str(Path(os.path.abspath(__file__)).parents[2])
        if path == 'base':
            return base_dir
        elif path == 'app':
            return base_dir + '/' + settings.CUR_APP_NAME
        elif path == 'static':
            return base_dir + '/' + 'static_' + settings.CUR_APP_NAME
