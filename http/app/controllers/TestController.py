from app.controllers.BaseController import BaseController
from core.helpers.Mailer import Mailer


class TestController(BaseController):

    a = 1

    def __init__(self, request):
        super().__init__(request)

    def test(self):
        post = self.input()
        self.make_response(post, format='json')

    def mail_test(self):
        m = Mailer()
        m.text('Text test!')
        m.to('d.yefimov@gmail.com')
        m.subject('Test message')
#        m.file_attach(file='file', filename='file.bin')
        m.string_attach({'data': 'Text file', 'filename': 'test.txt'})
        result = m.send()
        self.make_response(result, format='json')


    def t1(self):
        self.make_response({'val': 't1'})

    async def t2(self):
        from core.helpers.Mailer import Mailer
        import time, asyncio

        for i in range(10):
            await asyncio.sleep(1)
            # time.sleep(1)
        mailer = Mailer()
        mailer.to('vyacheslav.konovalenko@ideus.biz')
        mailer.subject('async test')
        html_msg = '<html><body>it works!</body></html>'
        mailer.html(html_msg)
        mailer.send()

    def test2(self):

        from core.models.Model import Model
        user = Model.load('User').where('id', 60).first()
        user = Model.load('User').where('id', 60).first()
        user = Model.load('User').where('id', 60).first()

        self.make_response({'var': user.id})

        # import asyncio
        # # try:
        # #     self.t2().send(None)
        # # except:
        # #     pass
        # loop = asyncio.get_event_loop()
        # # loop.create_task(self.t2())
        # asyncio.ensure_future(self.t2(), loop=loop)
        #
        # self.t1()

    def pathtest(self):
        from core.helpers.CoreHelpers import CoreHelpers
        path = CoreHelpers.get_base_path('static')
        self.make_response(path)
