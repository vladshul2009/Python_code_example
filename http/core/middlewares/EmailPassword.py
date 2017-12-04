from core.middlewares.CoreMiddleware import CoreMiddleware
import re


class EmailPassword(CoreMiddleware):

    def handle(self):
        email = self.get_controller().post('email').strip()
        password = self.get_controller().post('password')
        if not email or not password:
            self.send_errors(["Email and password are required."])
        else:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                self.send_message("Incorrect email format.")
        if self.get_next():
            post = self.get_controller().post()
            post['email'] = email
            self.get_controller().set_post_params(post)