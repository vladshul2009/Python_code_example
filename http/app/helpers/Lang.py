from core.helpers.Config import Config
import gettext


class Lang:

    __lang = Config.get('lang.default')

    @staticmethod
    def set(lang):
        Lang.__lang = lang

    @staticmethod
    def get():
        return Lang.__lang

    @staticmethod
    def translate(message):
        localedir = Config.get('lang.localedir')
        t = gettext.translation('messages', localedir, languages=[Lang.__lang])
        return t.gettext(message)

    @staticmethod
    def exists(lang):
        mo_files = gettext.find('messages', Config.get('lang.localedir'), [lang])
        return True if mo_files else False

_ = Lang.translate
