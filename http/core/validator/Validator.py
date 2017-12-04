from core.validator.Rules import Rules
from core.validator.Result import Result
from core.helpers.Config import Config


class Validator:

    @staticmethod
    def validate(data, rules, messages = None):
        if messages is None:
            #from app.config.validation import config as validation_messages
            #messages = validation_messages
            messages = Config.get('validation_messages', 'validation')

        result = Result(messages)
        for attr, attr_rules in rules.items():
            attr_rules_list = attr_rules.strip().split('|')
            if len(attr_rules_list) >= 1:
                for rule in attr_rules_list:
                    rule_arr = rule.split(':')
                    static_method = 'validate' + '_' + rule
                    if len(rule_arr) == 1:
                        passed = getattr(Rules, static_method)(attr, data.get(attr))
                        if passed is False:
                            result.add_error(attr, rule, data.get(attr))
                    elif len(rule_arr) == 2:
                        static_method = 'validate' + '_' + rule_arr[0]
                        passed = getattr(Rules, static_method)(attr, data.get(attr), rule_arr[1])
                        if passed is False:
                            result.add_error(attr, rule_arr[0], data.get(attr), rule_arr[1])
                    elif len(rule_arr) == 3:
                        static_method = 'validate' + '_' + rule_arr[0]
                        passed = getattr(Rules, static_method)(attr, data.get(attr), rule_arr[1], rule_arr[2])
                        if passed is False:
                            result.add_error(attr, rule_arr[0], data.get(attr), rule_arr[1], rule_arr[2])
        return result

    '''
    rules:

    present (exists)
    regex
    in:ios,android
    array
    bool
    number
    string
    same:field
    required
    required_if:field,value
    required_with:foo,bar
    email
    unique:users
    min:3
    max:10
    '''