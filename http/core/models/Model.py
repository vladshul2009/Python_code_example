import importlib
import settings


class Model:

    __models = {}

    @staticmethod
    def load(model_name):
        Model.__import_from_path(settings.CUR_APP_NAME+'.models', model_name)
        return Model.__models[model_name]

    @staticmethod
    def core():
        Model.__import_from_path('core.models', 'ModelCore')
        return Model.__models['ModelCore']

    @staticmethod
    def __import_from_path(path, model_name):
        model = Model.__models.get(model_name)
        if model is None:
            model_module = importlib.import_module(path + '.' + model_name, model_name)
            Model.__models[model_name] = getattr(model_module, model_name)
