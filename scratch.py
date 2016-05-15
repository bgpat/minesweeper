#!/usr/bin/env python3

import threading
import tornado.ioloop
import blockext
import client


class BlockextThread(threading.Thread):
    def run(self):
        blockext.run('minesweeper', 'minesweeper', 5678)


@blockext.command('login %s:%s')
def login(name, password, mode='login'):
    ws.login(name, password, mode)


@blockext.command('register %s:%s')
def register(name, password):
    ws.login(name, password, mode='register')


@blockext.predicate('authenticated')
def authenticated():
    return ws.token is not None


@blockext.command('open %n %n')
def open(i, j):
    ws.write_message('open %d %d' % (int(i), int(j)))


@blockext.command('flag %n %n')
def flag(i, j):
    ws.write_message('flag %d %d' % (int(i), int(j)))


@blockext.reporter('board')
def board():
    if ws.data:
        return ws.data['board']


@blockext.reporter('score')
def score():
    if ws.data:
        return ws.data['score']


@blockext.reporter('highscore')
def highscore():
    if ws.data:
        return ws.data['highscore']


@blockext.reporter('remains')
def remains():
    if ws.data:
        return ws.data['remains']


@blockext.reporter('bombs')
def bombs():
    if ws.data:
        return ws.data['bombs']


@blockext.reporter('flags')
def flags():
    if ws.data:
        return ws.data['flags']

if __name__ == '__main__':
    scratch = BlockextThread()
    scratch.start()
    ws = client.WebSocketClient('localhost', 5677)
    tornado.ioloop.IOLoop.instance().start()
