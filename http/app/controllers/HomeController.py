from app.controllers.BaseController import BaseController as BaseController
from app.models.User import User as User

class HomeController(BaseController):

    def __init__(self, request):
        super().__init__(request)
        print('home controller')

    def login(self):
        self.make_response("login action", format='html')

    def test(self):
        print('executed test')

    def test2(self):
        user = User.find(1)
        print(user)

    def test3(self):
        response = {
            "key": "value",
            "integer": 12,
            "float": 1.22,
            "float2": 1.234444,
            "bool": True,
            "None": None,
            "list3": [1, 2, 3, [
                4, 5, {
                    "a": 123,
                    "b": 3.5,
                    "c": [1, 2, 3, True]
                }, 6, [7, 8, 9, [10, 11, [12, 13]]]
            ]]
        }
        self.make_response(response)

