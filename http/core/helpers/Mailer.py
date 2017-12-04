#from app.config.main import config
from io import BytesIO
import emails
from core.helpers.Config import Config


class Mailer:
    __config = None
    __html = None
    __text = None
    __subject = None
    __from_email = None
    __from_name = None
    __to = None
    __cc = None
    __bcc = None
    __files_attachments = []
    __strings_attachments = []

    def __init__(self, config_name='mail'):
        self.__config = Config.get(config_name, 'main')

    def html(self, html):
        """
        :param html: Email text in html format
        :type html: str
        """
        self.__html = html

    def text(self, text):
        """

        :param text: Email text in text format
        :type: text: str
        """
        self.__text = text

    def to(self, to):
        self.__to = to

    def cc(self, cc):
        self.__cc = cc

    def bcc(self, bcc):
        self.__bcc = bcc

    def subject(self, subject):
        self.__subject = subject

    def mail_from(self, from_email, from_name=''):
        self.__from_email = from_email
        self.__from_name = from_name

    def file_attach(self, file):
        self.__files_attachments.append(file)

    def string_attach(self, params):
        self.__strings_attachments.append(params)

    def send(self):
        message = emails.Message(html=self.__html,
                                 text=self.__text,
                                 subject=self.__subject,
                                 mail_from=(self.__from_name if self.__from_name is not None else self.__config['from_name'],
                                            self.__from_email if self.__from_email is not None else self.__config['from_email']),
                                 cc=self.__cc,
                                 bcc=self.__bcc)
        for file_attach in self.__files_attachments:
            message.attach(data=open(file_attach['file'], 'rb'), filename=file_attach['filename'])
        for string_attach in self.__strings_attachments:
            buffer = BytesIO()
            b = bytearray()
            b.extend(string_attach['data'].encode())
            buffer.write(b)
            buffer.seek(0)
            message.attach(data=buffer, filename=string_attach['filename'])
        response = message.send(to=self.__to, smtp={'host': self.__config['host'],
                                                    'port': self.__config['port'],
                                                    'tls': self.__config['tls'],
                                                    'user': self.__config['user'],
                                                    'password': self.__config['password']})
        return True if response.status_code == 250 else False
