import re

from core.middlewares.CoreMiddleware import CoreMiddleware


class EmailPassword(CoreMiddleware):
    def handle(self):
        json_data = self.get_controller().json()
        email = json_data.get('email')
        if email:
            email = email.strip()
        password = json_data.get('password')
        if not email or not password:
            self.send_message("Email and password are required.")
        else:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                self.send_message("Incorrect email format.")
        if self.get_next():
            json_data['email'] = email
            self.get_controller().set_json_data(json_data)
