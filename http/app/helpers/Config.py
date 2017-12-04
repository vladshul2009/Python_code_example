import importlib
import settings


class Config:

    # get dictionary value by path "socials.facebook.api_url"
    @staticmethod
    def get(value_path, dict_or_filename='main'):
        if type(dict_or_filename) is dict:
            return Config.__find_value(value_path, dict_or_filename)
        elif type(dict_or_filename) is str:
            config_module = importlib.import_module(settings.CUR_APP_NAME + '.config.' + dict_or_filename, 'config')
            config_dict = getattr(config_module, 'config')
            return Config.__find_value(value_path, config_dict)
        else:
            raise Exception('dict_obj must be dictionary instance.')

    @staticmethod
    def __find_value(value_path, dict_obj):
        if value_path.find('.') != -1:
            exploded = value_path.split('.')
            value = dict_obj.get(exploded[0])
            for key in exploded:
                val = value.get(key) if type(value) is dict else None
                if val is not None:
                    value = val
            return value
        return dict_obj.get(value_path)
