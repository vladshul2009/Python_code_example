#!/usr/bin/env python3
"""Example for aiohttp.web websocket server
"""

import asyncio
import json
import os
import socket

from aiohttp.web import (Application, Response, WebSocketResponse, WSMsgType, run_app)
from aiohttp import UnixConnector

from app.models.Message import Message
from app.models.User import User

WS_FILE = os.path.join(os.path.dirname(__file__), 'websocket.html')
UNIX_SOCKET = '/tmp/http_to_socket.soc'

users = []


async def wshandler(request):
    resp = WebSocketResponse()
    ok, protocol = resp.can_prepare(request)
    if not ok:
        with open(WS_FILE, 'rb') as fp:
            return Response(body=fp.read(), content_type='text/html')

    await resp.prepare(request)

    try:
        # перебираем всех уже подключенных пользователей и рассылаем им сообщение
        for ws in request.app['sockets']:
            ws.send_str('Someone joined')
        # добавляем новое соединение
        # if resp not in request.app['sockets']:
        request.app['sockets'].append(resp)

        # ws.send_str('{"actions": ["do_login"]}')
        # return resp

        # if getattr(resp, 'user_id') is not None:
        # перебираем свои сообщения
        async for msg in resp:
            if msg.type == WSMsgType.TEXT:
                try:
                    json_data = json.loads(msg.data)
                except Exception:
                    json_data = {}

                id_to = None
                message = None
                user_to = None
                message_obj = None

                try:
                    id_to = json_data.get('id_to', False)
                    message = json_data.get('message')
                except Exception:
                    pass

                if id_to:
                    user_to = User.where('id', '=', id_to).first()
                # @TODO: add check - is he in contact list?
                if user_to and getattr(resp, 'user_id', False) and message:
                    message_obj = Message()
                    message_obj.id_from = resp.user_id
                    message_obj.id_to = user_to.id
                    message_obj.message = message
                    message_obj.is_viewed = False
                    message_obj.save()
                # перебираем все соединения
                for i, ws in enumerate(request.app['sockets']):
                    # если это не я
                    if ws is not resp:
                        try:
                            # if id_to and getattr(resp, 'user_id', False) and message and str(id_to) == str(ws.user_id):
                            if user_to and message_obj:
                                # reciever is online
                                if getattr(ws, 'user_id', False) and str(id_to) == str(ws.user_id):
                                    send_object = {
                                        'id_to': user_to.id,
                                        'id_from': resp.user_id,
                                        'message': message
                                    }
                                    ws.send_str(str(send_object))
                                    message_obj.is_viewed = True
                                    message_obj.save()
                            else:
                                pass
                        except Exception:
                            pass
                            # ws.send_str(json_data.get('message'))
                    # если это я
                    else:
                        if not getattr(ws, 'user_id', False):
                            try:
                                api_token = json_data.get('api_token')
                                if api_token is not None and api_token:
                                    user = User.where('api_token', '=', api_token).first()
                                    if user is not None:
                                        request.app['sockets'][i].user_id = user.id
                                        resp.user_id = user.id
                                        resp.send_str('{"authorized": true}')
                                    else:
                                        resp.send_str(get_relogin())
                                else:
                                    resp.send_str(get_relogin())
                            except Exception:
                                resp.send_str(get_relogin())
                        else:
                            resp.send_str('{"ok": true}')
            else:
                return resp
        return resp
    finally:
        # разрываем соединение
        request.app['sockets'].remove(resp)
        for ws in request.app['sockets']:
            ws.send_str('Someone disconnected.')


async def on_shutdown(app):
    for ws in app['sockets']:
        await ws.close()
    # if os.path.exists(UNIX_SOCKET):
    #     os.remove(UNIX_SOCKET)



def get_relogin():
    return '{"actions": ["do_login"]}'


async def listen_unix(app):
    if os.path.exists(UNIX_SOCKET):
        os.remove(UNIX_SOCKET)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind(UNIX_SOCKET)
    try:
        while True:
            datagram = server.recv(1024)
            if not datagram:
                break
            else:
                print(datagram.decode('utf-8'))
                for ws in app['sockets']:
                    ws.send_str(datagram.decode('utf-8'))
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        server.close()
        if os.path.exists(UNIX_SOCKET):
            os.remove(UNIX_SOCKET)
    finally:
        server.close()
        if os.path.exists(UNIX_SOCKET):
            os.remove(UNIX_SOCKET)
    return True


async def test_sleep():
    await sleep()


async def start_background_tasks(app):
    app['unix_listener'] = app.loop.create_task(listen_unix(app))
    app['unix_listener'] = app.loop.create_task(test_sleep())


async def cleanup_background_tasks(app):
    await app['unix_listener']


async def init(loop):
    app = Application(loop=loop)
    app['sockets'] = []
    app.router.add_get('/', wshandler)

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    app.on_shutdown.append(on_shutdown)

    return app


loop = asyncio.get_event_loop()
app = loop.run_until_complete(init(loop))

run_app(app)

