from orator.orm import belongs_to_many

from core.models.ModelCore import ModelCore


class ACL_Group(ModelCore):
    __table__ = 'acl_groups'

    @belongs_to_many('acl_groups_users')
    def users(self):
        from app.models.User import User
        return User
