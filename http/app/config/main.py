import app.middlewares.HandleErrors as HandleErrors

config = {
    "title": "Application title",
    "description": "App description",
    "host": "http://46.101.254.89",
    "reset_pass_expires": 720,  # in hours
    "email_regexp": r"[^@]+@[^@]+\.[^@]+",
    "server_timezone": "+2",
    "lang": {
        "default": "en",
        "localedir": "/home/dev/dev/http/app/resources/lang"
    },
    "user_contacts": {
        "limit": 20
    },
    "user_messages": {
        "limit": 20
    },
    "home_screen": {
        "favourite_limit": 3,
        "last_connections_limit": 3,
        "more_connections_limit": 3,
        "birthday_limit": 3,
    },
    "redis": {
        "port": 6379
    },
    "user_pushes": {
        "text_limit": 200,
        "device_types": ['android', 'ios'],

        "android_key": "AIzaSyABjOsv0wjhnfhamxkfJpJZ12l8mzycpyY",
        "android_server": "https://fcm.googleapis.com/fcm/send",

        # commands for generating certs
        # openssl x509 -in aps_development.cer -inform der -out PushChatCert.pem
        # openssl pkcs12 -in apns-dev-cert.p12 -out apns-dev-cert.pem -nodes -clcerts
        "ios_key_password": "/home/dev/dev/http/app/resources/certificates/dev_key.pem",
        "ios_cert_path": "/home/dev/dev/http/app/resources/certificates/dev_cert.pem"
    },
    "flic_pushes": {
        "android_key": "AIzaSyBOsRZPY7RB1jONHWoIO9UZnSm4WngC9A0",
        "android_server": "https://fcm.googleapis.com/fcm/send",
        # "ios_key_password": "/home/dev/dev/http/app/resources/certificates/DevPushKey.pem",
        # "ios_cert_path": "/home/dev/dev/http/app/resources/certificates/DevPushCertificate.pem"
        "ios_key_password": "/home/dev/dev/http/app/resources/certificates/PushKey.pem",
        "ios_cert_path": "/home/dev/dev/http/app/resources/certificates/PushCertificate.pem"
    },
    "root_dir": "/home/dev/dev",
    "upload_dir": "/static/uploads/",
    "errors": {
        404: HandleErrors.handle_404,
        500: HandleErrors.handle_500
    },
    "response_codes": {
        "error": 400,
        "api_token_error": 401,
        "message": 418,
        "error_and_message": 422,
        "nothing_changed": 204
    },
    "mail": {
        "host": "ideus.biz",
        "from_email": "denis.efimov@ideus.biz",
        "from_name": "Denis Efimov",
        "port": 26,
        "ssl": False,
        "user": "denis.efimov@ideus.biz",
        "password": "22efimov33"
    },
    "flic_mail": {
        "host": "smtp.gmail.com",
        "from_email": "headupapp@gmail.com",
        "from_name": "HeadupApp",
        "port": 587,
        "tls": True,
        "user": "headupapp@gmail.com",
        "password": "MyApp123"
    },
    "admin_emails": [
        'denis.efimov@ideus.biz',
        # 'vyacheslav.konovalenko@ideus.biz',
        # 'anton.zubko@ideus.biz',
        # 'shiloanton@gmail.com'
    ]
}
