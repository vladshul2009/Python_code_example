#import app.config.db as db_config
import core.models.Connection as Connection
import datetime, time
from core.models.Position import Position
from core.helpers.Config import Config

ConnStaticClass = Connection.Connection
postgres = Config.get('postgres', 'db_config')
ConnStaticClass.init({'postgres': postgres})
ConectionModel = ConnStaticClass.get_model()


class ModelCore(ConectionModel):

    date_format = 'unix_timestamp'
    _array_fields = []

    # left only specified keys in dictionary
    def _left_keys(self, keys):
        data = self.to_dict()
        new_dict = {}
        if data:
            for key in keys:
                key_to_set = data.get(key)
                if key_to_set is not None:
                    new_dict[key] = data[key]
                else:
                    new_dict[key] = ""
        return new_dict

    # remove specified keys from dictionary
    def _unset_keys(self, keys):
        data = self.to_dict()
        new_dict = {}
        if data:
            for key, val in data.items():
                if key not in keys:
                    new_dict[key] = val
        return new_dict

    def get_date_format(self):
        if self.date_format is not None:
            if self.date_format != 'unix_timestamp':
                return self.date_format
        return '%Y-%m-%d %H:%M:%S.%f'

    # orator method for format data (created_at, updated_at)
    def _format_date(self, date):
        if self.date_format is not None:
            if self.date_format == 'unix_timestamp':
                str_date = super()._format_date(date)
                if type(str_date) is str:
                    dt = datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S.%f")
                    seconds = int(time.mktime(dt.timetuple()))
                    server_timezone = Config.get('server_timezone')
                    if server_timezone:
                        shift = int(server_timezone) * 3600
                        seconds += shift
                    return seconds
                else:
                    return None
            else:
                return super()._format_date(date)
        return super()._format_date(date)

    def validate(self, rules='rules', messages=None):
        from core.validator.Validator import Validator
        if type(rules) is not dict:
            rules = getattr(self, rules)
        return Validator.validate(self.to_dict(), rules, messages)

    def save(self):
        if len(self._array_fields) > 0:
            for field_name in self._array_fields:
                if hasattr(self, field_name):
                    value = getattr(self, field_name)
                    if type(value) is list:
                        if len(value) > 0:
                            setattr(self, field_name, str(value).replace('[', '{').replace(']', '}'))
                        else:
                            setattr(self, field_name, '{}')
        if isinstance(self, Position):
            self.set_new_pos()
        return super().save()
