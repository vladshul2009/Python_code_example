from core.models.ModelCore import ModelCore as ModelCore
from orator.orm import belongs_to


class UserFile(ModelCore):

    __table__ = 'user_files'

    @belongs_to
    def user(self):
        from app.models.User import User
        return User

    def formatDefault(self):
        return self._left_keys(['id', 'file', 'created_at'])

    @staticmethod
    def get_by_urls(urls, is_single=False):
        if type(urls) is not list:
            urls = [urls]
        for i, url in enumerate(urls):
            url_exploded = url.split('/')
            urls[i] = url_exploded.pop()
        if is_single:
            return UserFile.where('file_name', urls.pop()).first()
        else:
            return UserFile.where_in('file_name', urls).get()
