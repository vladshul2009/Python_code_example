from core.models.ModelCore import ModelCore
from orator.orm import accessor


class Whatsnew(ModelCore):

    __table__ = 'whats_new'
    __hidden__ = ['id', 'platform', 'app_name']
'''
    @accessor
    def version(self):
        return 'V' + self.get_raw_attribute('version')
'''