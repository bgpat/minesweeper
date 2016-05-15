#!/usr/bin/env python3

import json
import threading
import websocket
import tornado.httpclient
import tornado.ioloop


class WebSocketClient(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.token = None
        self.connection = None
        self.data = None

    def run(self):
        print('run')
        while self.connection:
            try:
                self.on_message(self.connection.recv())
            except:
                break

    def connect(self):
        url = 'ws://%s:%d/%s' % (self.host, self.port, self.token)
        self.connection = websocket.create_connection(url)
        self.start()
        self.connection.on_message = self.on_message
        self.connection.on_error = self.on_error
        self.connection.on_close = self.on_close
        self.connection.run_forever()

    def write_message(self, message):
        self.connection.send(message)

    def on_message(self, res):
        self.data = json.loads(res)
        print('on_message', self.data)

    def on_close(self, ws):
        print('close', ws)

    def on_error(self, ws, error):
        print('error')

    def login(self, name, password, mode='login'):
        if self.connection:
            self.connection.close()
        req = tornado.httpclient.AsyncHTTPClient()
        url = 'http://%s:%d/%s' % (self.host, self.port, mode)
        h = {'content-type': 'application/json'}
        b = json.dumps({'name': name, 'password': password})
        req.fetch(url, self.authorize, method='POST', headers=h, body=b)

    def authorize(self, res):
        if res.error:
            print(res.error)
            return
        try:
            data = json.loads(res.body.decode('utf-8'))
            self.token = data['token']
            print(self.token)
            self.connect()
        except:
            pass

if __name__ == '__main__':
    websocket.enableTrace(True)
    ws = WebSocketClient('localhost', 5677)
    ws.login('test', 'password')
    tornado.ioloop.IOLoop.instance().start()
