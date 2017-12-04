from orator.orm import has_one

from core.models.ModelCore import ModelCore


class CardFile(ModelCore):
    __table__ = 'card_files'

    def format_default(self):
        return self._left_keys(['id', 'file'])

    @has_one
    def card(self):
        from app.models.Card import Card
        return Card
