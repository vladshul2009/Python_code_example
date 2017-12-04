# map of routes in format 'method:controller:action': 'route'}
# example: {"get:HomeController:index": '/'}
# request methods: post|get|any

from app.controllers import UserController as usr
from app.controllers import TestController as test
from app.controllers import UploadController as upload
from app.controllers.admin import AdminController as admin
from app.controllers import FlicController as flic

# IMPORTANT: AuthRoleApi middleware must be after Auth middleware

# @TODO: make middlewares with slashes like "roles/Auth"

routes_map = [
    ("get:/api/v1/test/test2", test.TestController),

    ("post:/api/v1/upload/save_files", usr.UserController, ["Auth"]),
    ("post:/api/v1/upload/send", upload.UploadController),

    ("post:/api/v1/user/new_password", usr.UserController),
    ("any:/user/change_password", usr.UserController),
    ("post:/api/v1/user/reset_password", usr.UserController),

    ("get:/api/v1/user/test", usr.UserController),
    ("options&post:/api/v1/user/login", usr.UserController, ["EmailPassword"]),
    ("post:/api/v1/user/signup", usr.UserController, ["EmailPassword"]),
    ("post:/api/v1/user/login_social", usr.UserController),
    ("post:/api/v1/user/update_profile", usr.UserController, ["Auth", "AuthRoleApi"]),
    ("post:/api/v1/user/files", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/find_users", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/add_contact", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/delete_contact", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/contacts", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/add_favorite", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/delete_favorite", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/favorites", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/messages", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/delete", usr.UserController, ["Auth"]),
    ("post:/api/v1/user/check_update", usr.UserController),
    ("post:/api/v1/user/client_error_callback", usr.UserController),
    ("get:/api/v1/user/{action}", usr.UserController),

    ("get:/admin/login", admin.AdminController),
    ("get:/admin/main", admin.AdminController),
    ("options&post:/admin/get_users", admin.AdminController, ["Auth", "AuthRoleAdmin"]),
    ("options&post:/admin/get_one", admin.AdminController, ["Auth", "AuthRoleAdmin"]),

    ("post:/api/v1/test/{action}", test.TestController),
]
