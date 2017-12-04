from core.helpers.Config import Config
import urllib.request, requests, json
# how to fix lib error:
# 1. get apns.py from here https://github.com/djacobs/PyAPNs
# 2. replace apns.py here /usr/local/lib/python3.5/dist-packages/apns.py
from apns import APNs, Payload


class PushNotification:

    __push_token = None
    __device_os = None

    def __init__(self, user):
        self.__set_device(user.device_os)
        self.__set_push_token(user.push_token)

    def __send_to_ios(self, message):
        payload = Payload(alert=message, sound="default", badge=1)

        apns = APNs(use_sandbox=True,
                    cert_file=Config.get('user_pushes.ios_cert_path'),
                    key_file=Config.get('user_pushes.ios_key_password'))

        apns.gateway_server.send_notification(self.__push_token, payload)

    def __send_to_android(self, message, title, data):
        data = self.__get_formatted_android(message, title, data)
        headers = {'Content-Type': 'application/json', 'Authorization': 'key=' + Config.get('user_pushes.android_key')}
        try:
            # response format: {'success': 1, 'results': [{'message_id': '0:1484578305084796%cecede4ccecede4c'}], 'canonical_ids': 0, 'failure': 0, 'multicast_id': 4756401486043037727}
            response = requests.post(Config.get('user_pushes.android_server'), data=data, headers=headers).json()
        except:
            pass

    def send_push(self, message, title=None, data={}):
        if not self.__push_token:
            self.__empty_token()
        if not self.__check_device(self.__device_os):
            self.__unknown_device()
        # ok
        if self.__device_os == 'android':
            self.__send_to_android(message, title, data)
        elif self.__device_os == 'ios':
            self.__send_to_ios(message)

    def send_push_debug(self, message, title=None, data={}):
        from core.helpers.Mailer import Mailer
        title = title if title else ''
        mailer = Mailer()
        mailer.to('vyacheslav.konovalenko@ideus.biz')
        mailer.subject(title)
        html_msg = '<html><body>' + message + '</body></html>'
        mailer.html(html_msg)
        mailer.send()

    def __set_device(self, device_os):
        if self.__check_device(device_os):
            self.__device_os = device_os
        else:
            raise Exception('Unknown device type: ' + str(device_os))

    def __set_push_token(self, push_token):
        if push_token:
            self.__push_token = push_token
        else:
            self.__empty_token()

    def __get_formatted_android(self, message, title, data):
        response = dict(
            notification=dict(
                body=message,
                title=title,
                ic_notification='ic_launcher'
            ),
            data=data,
            to=self.__push_token
        )
        return json.dumps(response).encode('utf8')
        # return str.encode(str(response))

    def __empty_token(self):
        raise Exception('push_token is empty')

    def __unknown_device(self):
        raise Exception('Unknown device type: ' + str(self.__device_os))

    def __check_device(self, device_os):
        return device_os in Config.get('user_pushes.device_types')
