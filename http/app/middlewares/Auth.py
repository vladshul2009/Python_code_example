from core.middlewares.CoreMiddleware import CoreMiddleware
from app.models.User import User
from core.helpers.Config import Config


class Auth(CoreMiddleware):

    def handle(self):
        self.__check_token()

    def __check_token(self):
        headers = self.get_controller().get_request().headers
        json_data = self.get_controller().json()
        api_token = None
        try:
            api_token = headers['Api-Token']
        except:
            pass

        if api_token is None:
            try:
                api_token = self.get_controller().input('api_token')
            except:
                pass

        if api_token is None:
            try:
                api_token = json_data.get('api_token')
            except:
                pass

        if api_token is not None:
            user = User.where('api_token', '=', api_token).first()
            if user:
                user.update_last_connection()
                self.get_controller().set_user(user)
            else:
                self.send_message('Invalid api_token value.')
                self.set_api_token_error_status()
        else:
            self.send_message('Parameter api_token is required.')
            self.set_api_token_error_status()
