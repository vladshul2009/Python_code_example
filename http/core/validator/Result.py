from core.helpers.Config import Config


class Result:

    __errors_in_fields = []
    __errors = []
    __passed = True
    __all_messages = True

    def __init__(self, messages_config):
        self.__all_messages = messages_config

    def add_error(self, attr_name, rule, value, *args):
        self.__passed = False
        if attr_name not in self.__errors_in_fields:
            self.__errors_in_fields.append(attr_name)
        attr_name_readable = self.__all_messages.get('attrs').get(attr_name)
        message = self.__all_messages.get(attr_name + '.' + rule)
        if message is None:
            message = self.__all_messages.get(rule)
        if message is not None:
            if attr_name_readable is not None:
                message = message.replace(':attr', attr_name_readable)
            if len(args):
                if rule in ['min', 'max', 'in'] and args[0]:
                    message = message.replace(':' + rule, args[0])
            message = message.replace(':value', str(value))
            error = {
                'attr': attr_name,
                'rule': rule,
                'message': message
            }
            if error not in self.__errors:
                self.__errors.append(error)
        else:
            raise Exception('Please define message for rule ' + rule)

    def errors(self, name=None):
        if name is not None:
            error_by_name = None
            for error in self.__errors:
                if error.get('attr') == name:
                    if error_by_name is None:
                        error_by_name = error
            if error_by_name is not None:
                return error_by_name
            else:
                return None
        else:
            return self.__errors

    def messages(self, name=None):
        if self.__errors:
            messages = []
            for error in self.__errors:
                if name is not None and error.get('attr') == name:
                    return error['message']
                else:
                    messages.append(error['message'])
            if name is not None:
                return ''
            return messages
        else:
            return None

    def fails(self):
        return not self.__passed

    def passes(self):
        return self.__passed
