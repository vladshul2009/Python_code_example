from core.middlewares.CoreMiddleware import CoreMiddleware


class AuthRole(CoreMiddleware):
    name = None

    def handle(self):
        if self.name is not None:
            self.set_next(False)
            user = self.get_controller().get_user()
            if user is not None:
                if user.has_role_group(self.name):
                    self.set_next(True)
            if self.get_next() is False:
                self.send_message('Permission denied.')
        else:
            raise Exception('Group alias is None.')
