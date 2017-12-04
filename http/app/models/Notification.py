from orator import SoftDeletes
from orator.orm import has_many, has_one, belongs_to_many
import datetime
import asyncio, json

from core.models.ModelCore import ModelCore
from app.models.User import User
from core.helpers.Redis import Redis
from core.helpers.PushNotification import PushNotification
from sockets.helpers.Socket import Socket


class Notification(ModelCore):
    __table__ = 'notifications'

    __hidden__ = ['updated_at']
    _array_fields = ['user_ids', 'pushes_accepted']

    rules_create = {
        'entity': 'required',
        'entity_id': 'required|integer',
        'kind': 'required',
        'data': 'required',
        'sender_id': 'required|integer',
        'user_ids': 'required',
        'action': 'required',
    }

    @staticmethod
    async def start_socket_task():
        notifications = Notification.order_by('created_at', 'asc').get()
        # notifications = Notification.where('entity', entity).order_by('created_at', 'asc').get()

        for notification in notifications:
            # parameter determine how fast a clients will recieve new notifications
            # (0.0001: 0.1 ms) - 30-35% cpu loading on the cheapest digital ocean server for 50k notifications raws
            await asyncio.sleep(0.0001)
            await notification.handle()

    async def handle(self):
        if self.user_ids:
            user_ids_remove = []
            user_ids_pushes = []
            loop = asyncio.get_event_loop()
            for user_id in self.user_ids:
                if self.kind == 'socket':
                    is_sent = await self.__handle_socket(user_id)
                    if is_sent:
                        user_ids_remove.append(user_id)
                    else:
                        user_ids_pushes.append(user_id)

            user_ids_pushes = list(set(user_ids_pushes) - set(self.pushes_accepted))

            if user_ids_pushes:
                # call async push sending
                asyncio.ensure_future(self.__handle_pushes(user_ids_pushes), loop=loop)

            self.user_ids = list(set(self.user_ids) - set(user_ids_remove))
            if self.user_ids:
                if self.get_dirty():
                    self.save()
            else:
                self.delete()
        else:
            self.delete()

    def __get_json(self, json_db_data):
        from core.helpers.CoreHelpers import CoreHelpers
        data = json_db_data.replace('\'', '"')
        json_data = CoreHelpers.convert_to_string(json.loads(data))
        response = json.dumps(json_data, ensure_ascii=True)
        return response

    async def __handle_pushes(self, user_ids):
        users = User.where_in('id', user_ids).get()
        sent_pushes = [];

        for user in users:
            if self.push_data:
                try:
                    from core.helpers.CoreHelpers import CoreHelpers
                    data = self.push_data.replace('\'', '"')
                    push_data = CoreHelpers.convert_to_string(json.loads(data))

                    msg = push_data.get('message', '')
                    title = push_data.get('title')
                    data = push_data.get('data')

                    push = PushNotification(user)
                    # push.send_push(msg, title, data)
                    # push.send_push_debug(msg, title, data)
                    sent_pushes.append(user.id)
                # we need "except pass" cuz deviceOs or push_token can be empty and exception will thrown
                except Exception as e:
                    pass

        self.pushes_accepted += sent_pushes
        self.save()

    async def __handle_socket(self, user_id):
        client = Socket.clients(user_id)
        if client is not None:
            response = self.__get_json(self.data)
            client.send_str(response)
            return True
        return False

    async def is_busy(self):
        result = await Redis.getbit(self.entity, self.id)
        return result == 1 or result == '1' or result == b'1'

    async def set_busy(self):
        return await Redis.setbit(self.entity, self.id, 1)

    async def set_free(self):
        return await Redis.setbit(self.entity, self.id, 0)

    def save(self):
        if self.user_ids:
            super().save()