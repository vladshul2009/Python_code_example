from app.controllers.BaseController import BaseController
from app.models.User import User
from core.helpers.Config import Config
import importlib


class AdminController(BaseController):

    _json_data = None
    _headers = None
    _method = None

    def _before(self):
        self._json_data = self.json()
        self._headers = self.get_request().headers
        self._method = self.get_request().method

    def main(self):
        template = open('/home/dev/dev/static/admin/release/index.html', 'r')
        self.make_response(template.read(), format='html')

    def login(self):
        template = open('/home/dev/dev/static/admin/release/auth.html', 'r')
        self.make_response(template.read(), format='html')

    def get_users(self):
        response = None
        if self._method == 'POST':
            if not self._json_data:
                self.make_message('Required params is absent')
                return
            else:
                data_table = self._json_data.get('data_table')
                pagination = data_table.get('pagination')
                limit = int(pagination['number'])
                offset = int(pagination['start'])
                order = data_table.get('sort')
                search = data_table.get('search')
                if order:
                    order_field = order['predicate']
                    order_asc = 'DESC' if order['reverse'] else 'ASC'
                else:
                    order_field = 'id'
                    order_asc = 'ASC'
                query = User.order_by(order_field, order_asc).limit(limit).offset(offset)
                if search:
                    for key in search['predicateObject'].keys():
                        if key == 'birthday':
                            query.where_raw("birthday = to_date('" + search['predicateObject']['birthday'] + "', 'YYYY-MM-DD')")
                        else:
                            query.where(key, 'ilike', '%' + search['predicateObject'][key] + '%')
                users = query.get()
                formatted_users = []
                for list_user in users:
                    formatted_users.append(list_user.format_admin())
                response = {'users': formatted_users, 'count': len(formatted_users)}
        self.make_response(response)

    # actions list: user
    def get_one(self):
        response = None
        if self._method == 'POST':
            if not self._json_data:
                self.make_message('Required params is absent')
                return
            else:
                action = self._json_data.get('action')
                if action:
                    config = Config.get('get_one.' + action, 'admin')
                    if config.get('model') and config.get('field'):
                        field = config.get('field')
                        if self._json_data.get(field) is not None:
                            arr = config.get('model').strip().split(':')
                            model_name = arr[0]
                            formatter = arr[1]
                            model = getattr(importlib.import_module('app.models.' + model_name, model_name), model_name)
                            model_result = model.where(field, '=', self._json_data.get(field)).first()
                            if model_result is not None:
                                response = getattr(model_result, formatter)()
                            else:
                                response = {}
                        else:
                            raise Exception('Param "' + field + '" is required')
                    else:
                        raise Exception('Params "model" and "field" are required')
                else:
                    self.make_message('Action is not defined')
                    return
        self.make_response(response)
