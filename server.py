#!/usr/bin/env python3

import re
import json
import sqlite3
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
            name = re.sub(r'[^A-Za-z0-9\-_]', '', data['name'])
            password = re.sub(r'[^A-Za-z0-9\-_]', '', data['password'])
            if req.path == '/login':
                res = self.login(name, password)
            if req.path == '/register':
                res = self.register(name, password)
            if res is not None:
                self.write(res)
        except Exception as e:
            self.set_status(401)
            print(e)

    def login(self, name, password):
        global user_manager
        user = user_manager.login(name, password)
        if user:
            return {'token': user.token}
        self.set_status(401)

    def register(self, name, password):
        global user_manager
        if len(name) == 0 or len(password) == 0:
            self.set_status(400)
            return
        user = user_manager.register(name, password)
        if user:
            return {'token': user.token}
        self.set_status(409)


class RankingHandler(tornado.web.RequestHandler):
    path = 'user.db'

    def __init__(self, *args, **kwargs):
        tornado.web.RequestHandler.__init__(self, *args, **kwargs)
        self.connection = sqlite3.connect(self.path)

    def get(self):
        sql = '''SELECT `name`, `score`, `highscore` FROM `users`
            ORDER BY `score` DESC'''
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()
        res = cursor.fetchall()
        self.write(json.dumps(res))


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        global user_manager
        tornado.websocket.WebSocketHandler.__init__(self, *args, **kwargs)
        self.ms = minesweeper.MineSweeper(user_manager.board)
        self.manager = user_manager
        self.manager.board = self.ms.board

    def open(self, token):
        try:
            u = self.manager[token]
            u.ws = self
            self.write_message(str(u.ms))
        except:
            self.write_message('error')

    def on_message(self, message):
        token = self.path_args[0]
        (op, i, j) = message.split(' ')
        ms = self.manager[token].ms
        if op == 'open':
            res = self.ms.board.open(int(i), int(j))
            if res is False:
                ms.reset_score()
            else:
                ms.add_score(res)
        if op == 'flag':
            self.ms.board.flag(int(i), int(j))
        bombs = self.ms.board.count_bombs()
        remains = self.ms.board.count_remains()
        print(self.ms.board.debug(), bombs, remains)
        if bombs == remains:
            self.ms.board.generate()
        self.manager[token].update()
        for u in self.manager.values():
            if not u.ws:
                print('error', u.token, u.ws)
                continue
            print(hash(self.ms.board), hash(u.ms.board))
            u.ws.write_message(str(u.ms))

    def on_close(self):
        token = self.path_args[0]
        del self.manager[token]
        print('close')

    def check_origin(self, origin):
        return True

app = tornado.web.Application([
    ('/(.{32})', WebSocketHandler),
    ('/login', LoginHandler),
    ('/register', LoginHandler),
    ('/ranking', RankingHandler),
])
ms_tmp = minesweeper.MineSweeper()
user_manager = user.UserManager()
user_manager.board = ms_tmp.board

if __name__ == '__main__':
    app.listen(5677)
    tornado.ioloop.IOLoop.instance().start()
