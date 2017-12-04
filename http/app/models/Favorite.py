from core.models.ModelCore import ModelCore as ModelCore
from app.models.User import User
from orator.orm import belongs_to, has_one

class Favorite(ModelCore):

    __table__ = 'user_favorites'
    __timestamps__ = None

    @belongs_to
    def user(self):
        return User

    @has_one('id', 'favorite_id')
    def favorite(self):
        return User

    def format_favorite(self):
        response = self.favorite.format_contact()
        return response