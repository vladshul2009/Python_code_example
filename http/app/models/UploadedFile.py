from core.models.ModelCore import ModelCore as ModelCore
from app.models.UserFile import UserFile


class UploadedFile(ModelCore):

    __table__ = 'upload_files'

    def formatDefault(self):
        return self._left_keys(['id', 'file'])

    def save_file(self):
        from core.models.Connection import Connection
        with Connection.get_db().transaction():
            user_file = UserFile()
            user_file.file = self.file
            user_file.user_id = self.user_id
            user_file.file_name = self.file_name
            user_file.save()
            self.delete()

    @staticmethod
    def get_by_urls(urls, is_single=False):
        if type(urls) is not list:
            urls = [urls]
        for i, url in enumerate(urls):
            url_exploded = url.split('/')
            urls[i] = url_exploded.pop()
        if is_single:
            return UploadedFile.where('file_name', urls.pop()).first()
        else:
            return UploadedFile.where_in('file_name', urls).get()
