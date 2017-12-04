from core.models.ModelCore import ModelCore as ModelCore
from app.models.User import User
from orator.orm import belongs_to

class UserSocial(ModelCore):

    __table__ = 'user_socials'

    # alias is social driver: facebook, instagram, twitter etc
    @staticmethod
    def find_by_ident(social_ident, alias):
        # convert to str cuz postgres throw error when field is string and we are searching by integer
        return UserSocial.where('social_ident', '=', str(social_ident)).where('alias', '=', alias).first()

    @belongs_to
    def user(self):
        return User