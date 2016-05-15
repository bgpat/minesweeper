#!/usr/bin/env python3

import json
import tornado.ioloop
import tornado.web
import tornado.websocket
import minesweeper
import user


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        req = self.request
        self.add_header('accept', 'application/json')
        if 'application/json' not in req.headers.get('content-type'):
            self.set_status(406)
            return
        try:
            data = json.loads(req.body.decode('utf-8'))
            res = None
            if req.path == '/login':
                res = self.login(data)
            if req.path == '/register':
                res = self.register(data)
            if res is not None:
                self.write(res)
        except Exception as e:
            self.set_status(401)
            self.write(e)

    def login(self, data):
        user = app.user_manager.login(data['name'], data['password'])
        if user:
            return {'token': user.token}
        self.set_status(401)

    def register(self, data):
        user = app.user_manager.register(data['name'], data['password'])
        if user:
            return {'token': user.token}
        self.set_status(409)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        tornado.websocket.WebSocketHandler.__init__(self, *args, **kwargs)
        self.ms = minesweeper.MineSweeper()

    def open(self, token):
        try:
            u = app.user_manager[token]
            u.ws = self
            print(str(u.ms))
            self.write_message(str(u.ms))
        except:
            self.write_message('error')

    def on_message(self, message):
        token = self.path_args[0]
        (op, i, j) = message.split(' ')
        ms = app.user_manager[token].ms
        if op == 'open':
            res = ms.board.open(int(i), int(j))
            if res is False:
                ms.reset_score()
            else:
                ms.add_score(res)
        if op == 'flag':
            ms.board.flag(int(i), int(j))
        print(ms.board)
        for u in app.user_manager.values():
            if not u.ws:
                print('error', u.token, u.ws)
                continue
            u.ws.write_message(str(u.ms))

    def on_close(self):
        token = self.path_args[0]
        del app.user_manager[token]
        print('close')

    def check_origin(self, origin):
        return True

app = tornado.web.Application([
    ('/(.{32})', WebSocketHandler),
    ('/login', LoginHandler),
    ('/register', LoginHandler),
])
app.user_manager = user.UserManager()

if __name__ == '__main__':
    app.listen(5677)
    tornado.ioloop.IOLoop.instance().start()
