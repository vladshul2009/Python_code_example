from core.models.ModelCore import ModelCore as ModelCore
from orator.orm import belongs_to, has_one
from app.models.User import User


class Contact(ModelCore):

    __table__ = 'user_contacts'
    __timestamps__ = None

    @belongs_to
    def user(self):
        return User

    @has_one('id', 'contact_id')
    def contact(self):
        return User
