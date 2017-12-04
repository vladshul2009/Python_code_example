from core.models.Connection import Connection


class Position:

    _position = 'position'
    _position_group = []
    _position_add_to_end = True

    def move_down(self):
        self.__move('>', 'ASC')

    def move_up(self):
        self.__move('<', 'DESC')

    def __move(self, sign, order):
        where = self.__class__.where(self._position, sign, getattr(self, self._position))
        where = self.__group_condition(where)
        next_item = where.order_by(self._position, order).first()
        if next_item is not None:
            next_pos = getattr(next_item, self._position)
            setattr(next_item, self._position, getattr(self, self._position))
            setattr(self, self._position, next_pos)
            next_item.save()
            self.save()

    def __group_condition(self, where):
        for pos_group in self._position_group:
            if where is None:
                where = self.__class__.where(pos_group, '=', getattr(self, pos_group))
            else:
                where.where(pos_group, '=', getattr(self, pos_group))
        return where

    def set_pos(self, pos):
        current_pos = getattr(self, self._position)
        where = self.__class__.where(self._position, '=', current_pos)
        where = self.__group_condition(where)
        change_item = where.first()
        if change_item is not None:
            if current_pos < pos:
                where = self.__class__.where(self._position, '>', current_pos)\
                    .where(self._position, '<=', pos)
                where = self.__group_condition(where)
                items = where.get()
                self.__update_positions(items, '-')
                setattr(self, self._position, pos)
                self.save()
            elif current_pos > pos:
                where = self.__class__.where(self._position, '<', current_pos)\
                    .where(self._position, '>=', pos)
                where = self.__group_condition(where)
                items = where.get()
                self.__update_positions(items, '+')
                setattr(self, self._position, pos)
                self.save()
        else:
            pass
            # do we need it?

    def __update_positions(self, items, sign):
        for item in items:
            value = getattr(item, self._position)
            new_value = value - 1 if sign == '-' else value + 1
            setattr(item, self._position, new_value)
            item.save()

    def get_last_pos(self):
        where = self.__group_condition(None)
        last_pos = where.max(self._position)
        return 0 if last_pos is None else last_pos

    def move_first(self):
        self.set_pos(1)

    def move_last(self):
        self.set_pos(self.get_last_pos())

    def set_new_pos(self):
        if self.exists is False:
            last_pos = self.get_last_pos()
            if self._position_add_to_end is True:
                self.set_attribute(self._position, 1 + last_pos)
            elif self._position_add_to_end is False:
                # Connection.get_db.table(self.__class__.__table__).increment('position')
                result = Connection.get_db().table(self.get_table())
                for pos_group in self._position_group:
                    result.where(pos_group, '=', getattr(self, pos_group))
                result.increment('position')
                self.set_attribute(self._position, 1)
            else:
                raise Exception('parameter _position_add_to_end must be bool.')
