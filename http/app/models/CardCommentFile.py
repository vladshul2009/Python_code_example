from orator.orm import has_one

from core.models.ModelCore import ModelCore


class CardCommentFile(ModelCore):
    __table__ = 'card_comment_files'

    def format_default(self):
        return self._left_keys(['id', 'file'])

    @has_one
    def card_comment(self):
        from app.models.CardComment import CardComment
        return CardComment
