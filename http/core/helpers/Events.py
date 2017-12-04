from core.helpers.Mailer import Mailer
from core.helpers.Config import Config


class Events:

    @staticmethod
    def password_reset(dict_obj):
        mailer = Mailer()
        mailer.to(dict_obj.get('email'))
        mailer.subject('Password recovery')
        restore_url = Config.get('host') + '/user/change_password?reset_token=' + dict_obj.get('reset_pass_token')
        raw_html = '<p>To restore your password using browser please click <a href="' + restore_url + '">here</a></p>'
        if dict_obj.get('app_name') is not None:
            raw_html += '<p>To restore your password using application please click <a href="' + restore_url + '&redirect=' + dict_obj.get('app_name') + '">here</a></p>'
        html_msg = '<!DOCTYPE html><html><body>' + raw_html + '</body></html>'
        mailer.html(html_msg)
        mailer.send()

    @staticmethod
    def client_error_callback(data):
        raw_html = str(data)
        html_msg = '<!DOCTYPE html><html><body>' + raw_html + '</body></html>'
        for email in Config.get('admin_emails'):
            mailer = Mailer()
            mailer.to(email)
            mailer.subject('Client error callback')
            raw_html
            mailer.html(html_msg)
            mailer.send()