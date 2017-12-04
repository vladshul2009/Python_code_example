from core.helpers.Config import Config

class Rules:

    __rules = [
        'required', 'present', 'regex', 'in', 'array', 'boolean', 'number', 'integer', 'string', 'same', 'required_if',
        'required_with', 'email', 'unique', 'min', 'max'
    ]

    @staticmethod
    def validate_boolean(attr, value):
        return type(value) is bool

    @staticmethod
    def validate_required(attr, value):
        if value is not None and value != '':
            return True
        return False

    @staticmethod
    def validate_integer(attr, value):
        value = int(value)
        if value > 0:
            return True
        return False

    @staticmethod
    def validate_string(attr, value):
        return type(value) is str

    @staticmethod
    def validate_min(attr, value, min_val):
        return int(value) >= int(min_val)

    @staticmethod
    def validate_max(attr, value, max_val):
        return int(value) <= int(max_val)

    @staticmethod
    def validate_in(attr, value, in_values):
        in_values = in_values.strip().split(',')
        return str(value) in in_values

    @staticmethod
    def validate_unique(attr, value, table):
        #import app.config.db as db_config
        from core.models.Connection import Connection
        #Connection.init(db_config.connection)
        Connection.init(Config.get('config', 'db_config'))
        db = Connection.get_db()
        result = not db.table(table).where(attr, '=', value).count() > 0
        return result

    @staticmethod
    def validate_email(attr, value):
        import re
        result = re.match(Config.get('email_regexp'), value)
        return False if result is None else True
