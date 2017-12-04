import mimetypes
import os
import uuid

import magic

from app.controllers.BaseController import BaseController
from core.helpers.Config import Config
from app.models.UploadedFile import UploadedFile
from app.models.User import User


class UploadController(BaseController):
    async def send(self):
        user_exists = await self.__set_user()
        if user_exists:
            reader = await self.get_request().multipart()
            # /!\ Don't forget to validate your inputs /!\

            file = await reader.next()

            # filename = file.filename
            unique_filename = str(uuid.uuid4())

            # You cannot rely on Content-Length if transfer is chunked.
            size = 0
            file_path = os.path.join(Config.get('upload_dir'), unique_filename)
            path = Config.get('root_dir') + file_path
            with open(path, 'wb') as f:
                while True:
                    chunk = await file.read_chunk()  # 8192 bytes by default.
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)

            mime_type = magic.from_file(path, mime=True)
            file_extension = mimetypes.guess_extension(mime_type, False)
            if file_extension == '.jpe':
                file_extension = '.jpeg'
            os.rename(path, path + file_extension)
            file_path += file_extension
            file_model = UploadedFile()
            file_model.file = file_path
            file_model.file_name = unique_filename + file_extension
            file_model.user_id = self.get_user().id
            file_model.save()

            # self.make_response(file_model.formatDefault())
            self.make_response(file_model.formatDefault())

    async def __set_user(self):
        api_token = None
        headers = self.get_request().headers
        try:
            api_token = headers['Api-Token']
        except KeyError:
            pass

        if api_token is None or not api_token:
            api_token = self.get('api_token')

        if api_token is not None:
            user = User.where('api_token', '=', api_token).first()
            if user is not None:
                self.set_user(user)
                return True
            else:
                self.make_actions(["api_token_is_invalid"])
                return False
        else:
            self.make_actions(["api_token_is_required"])
        return False
