import asyncio
import aioredis
import uvloop
import datetime
import importlib
import json
from os.path import expanduser
from urllib.parse import urlparse, parse_qsl

from aiohttp import hdrs
from aiohttp import web
from aiohttp_swagger import *

from core.helpers.Config import Config

App = web.Application()
request_object = {}

import settings
settings.CUR_APP_NAME = 'app'

# https://habrahabr.ru/post/282972/
# @TODO: it doesn't work with aioredis
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def handle(request):
    try:
        # request.rel_url is instance of "URL" object
        # remove hash from url
        url = str(request.rel_url).replace('#', '')
        url_params = url.split('?')
        get_params = None
        # if we have get params
        if len(url_params) > 1:
            # cut get params from main route
            url = url_params[0]
            # get string of get params
            parsed_url = urlparse(url_params[1])
            # convert get params from string to dictionary
            get_params = parse_qsl(parsed_url.path)

        # print(request.match_info)

        # set current_route as it was added in request_object
        current_route = url.split('/')
        action = current_route.pop()
        # if we using not /api/v1/controller/action and just controller/action (for frontend)
        if len(current_route) >= 3:
            version = current_route[2]
        else:
            version = 'v1'
        handler = request_object.get(url)
        if handler is not None:
            current_route = '/'.join(current_route) + '/' + action
        else:
            current_route = '/'.join(current_route) + '/{action}'

        handler = request_object.get(current_route)

        # if controller.action exists
        if handler is not None and len(handler) in range(1, 3):
            controller_class = handler[0]

            # create controller object
            instance = controller_class(request)
            # init get parameters
            instance.set_get_params(get_params)
            # check if controller is upload - we need other handler

            # check for existing controller's action
            versionized_action_exists = hasattr(instance, action + '_' + version)
            action_exists = hasattr(instance, action)
            if action_exists or versionized_action_exists:
                if versionized_action_exists:
                    is_async = asyncio.iscoroutinefunction(getattr(instance, action + '_' + version))
                else:
                    is_async = asyncio.iscoroutinefunction(getattr(instance, action))

                if is_async is False:
                    json_data = None
                    post_params = await request.post()
                    try:
                        json_data = await request.json()
                    except Exception:
                        pass

                    # init parameters
                    instance.set_post_params(post_params)
                    instance.set_json_data(json_data)

                    # execute middlewares
                    if len(handler) == 2:
                        if instance.get_request().method != 'OPTIONS':
                            middlewares = handler[1]
                            for middleware in middlewares:
                                middleware_module = importlib.import_module('app.middlewares.' + middleware, middleware)
                                middleware_obj = getattr(middleware_module, middleware)(instance)
                                middleware_obj.handle()
                                if middleware_obj.get_next() is False:
                                    return send_response(web, middleware_obj.get_controller())
                        # execute controller action from route
                        if hasattr(instance, '_before'):
                            getattr(instance, '_before')()
                        result = getattr(instance, 'index')(action, version)
                        # return web.HTTPFound('http://absolute.url/and/path/if/you/want')
                        if result is not None:
                            return result
                else:
                    # middlewares ???
                    await getattr(instance, 'index_async')(action, version)
            else:
                # call handle_404 from middlewares/HandleErrors
                return web.Response(status=404)
        else:
            raise Exception('Can not find route for url ' + url)
        log_text = "<div><ul><li style='color: blue;'>" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + "</li>"
        headers_str = '<ul>'
        for header in request.headers:
            headers_str += "<li><strong>{0}</strong>: {1}</li>".format(header, request.headers[header])
        log_text += "<li><i>" + str(request.rel_url) + "</i></li>"
        log_text += "<li>" + headers_str + "</ul></li>"
        log_text += "<li>" + str(instance.json()) + "</li>"
        log_text += "<li>" + str(instance.get_response()) + "</li></ul></div>"
        log_filename = expanduser("~") + "/dev/static_" + settings.CUR_APP_NAME + "/apilog/" + datetime.datetime.now().strftime("%Y-%m-%d") + ".html"
        logfile = open(log_filename, 'a')
        logfile.write(log_text)
        logfile.close()
        return send_response(web, instance)

    except Exception as exception:
        from app.helpers.Mailer import Mailer
        from time import gmtime, strftime
        import traceback
        import random
        import string

        for email in Config.get('admin_emails'):
            mailer = Mailer()
            mailer.to(email)
            mailer.subject('Exception Error')
            raw_html = ''
            for raw in traceback.format_exc().splitlines():
                raw_html += raw + '</br >'
            html = '<html><body>' + raw_html + '</body></html>'
            s = string.ascii_lowercase + string.digits
            filename = strftime("%Y-%m-%d_%H:%M:%S_", gmtime()) + ''.join(random.sample(s, 10)) + '.html'
            file_exception = open('/home/dev/dev/static_' + settings.CUR_APP_NAME + '/exceptions/' + filename, 'w')
            file_exception.write(html)
            file_exception.close()
            html_msg = '<html><body><a href="http://46.101.254.89/static_' + settings.CUR_APP_NAME + '/exceptions/' \
                       + filename + '">' + str(exception) + '</a></body></html>'
            mailer.html(html_msg)
            mailer.send()
        return web.Response(status=500)


def send_response(web, controller_object):
    cors_headers = {hdrs.ACCESS_CONTROL_ALLOW_ORIGIN: '*',
                    hdrs.ACCESS_CONTROL_ALLOW_METHODS: 'GET,HEAD,OPTIONS,POST,PUT',
                    hdrs.ACCESS_CONTROL_ALLOW_HEADERS: 'Access-Control-Allow-Origin, Access-Control-Allow-Headers, Access-Control-Allow-Methods, Origin, Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers',
                    hdrs.ACCESS_CONTROL_ALLOW_CREDENTIALS: 'true'}
    if controller_object.get_response_format() == 'json':
        response = json.dumps(controller_object.get_response(), ensure_ascii=False)
        return web.json_response(text=response, status=controller_object.get_status(), headers=cors_headers)
    elif controller_object.get_response_format() == 'html' or controller_object.get_response_format() == 'text':
        response = controller_object.get_response()
        content_type = 'text/html' if controller_object.get_response_format() == 'html' else 'text/plain'
        return web.Response(text=response, status=controller_object.get_status(), content_type=content_type,
                            headers=cors_headers)
    else:
        # Exception, unknown response format
        pass


def error_handler(overrides):
    async def middleware(App, handler):
        async def middleware_handler(request):
            try:
                response = await handler(request)
                override = overrides.get(response.status)
                if override is None:
                    return response
                else:
                    return await override(request, response)
            except web.HTTPException as ex:
                override = overrides.get(ex.status)
                if override is None:
                    raise
                else:
                    return await override(request, ex)

        return middleware_handler

    return middleware


def handle_route(route_element):
    exception_message = 'Invalid routes settings. Please check __your_app_/routes/routes.py'
    if len(route_element) in range(2, 4):
        route_params, controller_class = route_element[0].split(':'), route_element[1]
        if len(route_params) in range(2, 4):
            method, route = route_params[0], route_params[1]  # route = /api/v1/home/{action}
            check_routes(route)
            middlewares = []
            if len(route_element) == 3:
                middlewares = route_element[2]
            request_object[route] = (controller_class, middlewares)
            if method == 'get':
                App.router.add_get(route, handle)
            elif method == 'post':
                App.router.add_post(route, handle)
            elif method == 'options&post':
                App.router.add_route(hdrs.METH_OPTIONS, route, handle)
                App.router.add_post(route, handle)
            elif method == 'any':
                App.router.add_get(route, handle)
                App.router.add_post(route, handle)
            else:
                raise Exception('Runtime error: routes must contain only get:|post:|options:|any: prefixes')
        else:
            raise Exception(exception_message)
    else:
        raise Exception(exception_message)


# check routes for reserved CoreController methods
def check_routes(route_string):
    disallowed_routes = ["/get", "/post", "/input", "/setStatus", "/getStatus", "/makeResponse", "/setPostParams",
                         "/setGetParams"]
    for disallowed_url in disallowed_routes:
        if disallowed_url == route_string:
            raise Exception('Please do not use route name ' + disallowed_url + ' it was reserved for CoreController.')


# # handle all defined routes in http/app/routes/routes.py
import app.routes.routes as routes
for route_element in routes.routes_map:
    handle_route(route_element)

swaggerDescription = "Description of api for mobile developers."
# @TODO: get it from config app title
swaggerTitle = "aiohttp framework"

# @TODO: get swagger url from config
setup_swagger(App, swagger_from_file="swagger.yaml", swagger_url="/api/v1/doc", description=swaggerDescription,
              title=swaggerTitle)

# @TODO: get swagger url from config
setup_swagger(App, swagger_from_file="swagger_flic.yaml", swagger_url="/api/v1/doc_flic", description="Description of api for FLIC developers.",
              title="FLIC")


# App.router.add_get('/', handle)
# App.router.add_get('/{name}', handle)


# add middlewares for appliction
def setup_middlewares(App):
    print('errors setup')
    error_middleware = error_handler(Config.get("errors"))
    App.middlewares.append(error_middleware)


# application entry point
setup_middlewares(App)
# web.run_app(App, port=8001)

loop = asyncio.get_event_loop()

async def init_redis(port):
    from app.helpers.Redis import Redis
    conn = await aioredis.create_connection(
        ('localhost', port), loop=loop)
    Redis.set_connection(conn)
    # conn.close()
    # await conn.wait_closed()

redis_port = Config.get('redis.port')
loop.run_until_complete(init_redis(redis_port))
