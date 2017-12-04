#!/usr/bin/env python3
"""Example for aiohttp.web websocket server
"""

import asyncio
import json
import os

import aioredis
from aiohttp.web import (Application, Response, WebSocketResponse, WSMsgType)
from app.helpers.Config import Config

WS_FILE = os.path.join(os.path.dirname(__file__), 'websocket.html')

users = []

import settings
settings.CUR_APP_NAME = 'app'

async def wshandler(request):
    resp = WebSocketResponse()
    ok, protocol = resp.can_prepare(request)
    if not ok:
        with open(WS_FILE, 'rb') as fp:
            return Response(body=fp.read(), content_type='text/html')

    await resp.prepare(request)

    try:
        # перебираем всех уже подключенных пользователей и рассылаем им сообщение
        # for ws in request.app['sockets']:
        #     ws.send_str('Someone joined')
        # добавляем новое соединение
        # if resp not in request.app['sockets']:
        request.app['sockets'].append(resp)

        # перебираем свои сообщения
        async for msg in resp:
            if msg.type == WSMsgType.TEXT:
                try:
                    # if msg.data:
                    #     message_obj = Message()
                    #     message_obj.id_from = 80
                    #     message_obj.id_to_user = 94
                    #     message_obj.message = msg.data
                    #     message_obj.save()
                    json_data = json.loads(msg.data)
                except:
                    json_data = {}

                data = json_data.get('data')
                if data is None or type(data) is not dict:
                    data = {}
                try:
                    from sockets.routes.routes import routes_map
                    command = json_data.get('command')
                    command_not_found = True
                    if type(command) is str and command:
                        for route in routes_map:
                            if command == route[0]:
                                handler = route[1](data, route=route)
                                if getattr(handler, command):
                                    command_not_found = False
                                    before_return = True
                                    if hasattr(handler, '_before'):
                                        before_return = getattr(handler, '_before')(resp)
                                    if before_return:
                                        is_async = asyncio.iscoroutinefunction(getattr(handler, command))
                                        if is_async:
                                            await getattr(handler, command)(resp)
                                        else:
                                            getattr(handler, command)(resp)
                    if command_not_found is True:
                        from sockets.handlers.BaseHandler import BaseHandler
                        handler = BaseHandler(resp)
                        handler.make_response({"command": command}, 'command_not_found', resp)
                except Exception as e:
                    handler.make_response({"error": "exception"}, str(e), resp)
            else:
                return resp
        return resp
    finally:
        # разрываем соединение
        from sockets.helpers.Socket import Socket
        Socket.update_last_connection(resp)
        Socket.del_client(resp)
        request.app['sockets'].remove(resp)
        # for ws in request.app['sockets']:
        #     ws.send_str('Someone disconnected.')


async def on_shutdown(app):
    for ws in app['sockets']:
        await ws.close()

async def init(loop):
    app = Application(loop=loop)
    app['sockets'] = []
    app.router.add_get('/', wshandler)
    app.on_shutdown.append(on_shutdown)

    #init redis
    from app.helpers.Redis import Redis
    redis_port = Config.get('redis.port')
    conn = await aioredis.create_connection(
        ('localhost', redis_port))
    Redis.set_connection(conn)

    return app



loop = asyncio.get_event_loop()
app = loop.run_until_complete(init(loop))
# run_app(app)

async def background_loop():
    from http.digimundus.models import Notification
    while True:
        await Notification.start_socket_task()
        await asyncio.sleep(5)

future = asyncio.run_coroutine_threadsafe(background_loop(), loop)
