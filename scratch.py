#!/usr/bin/env python3

import sys
import threading
import tornado.ioloop
import blockext
import client

host = 'localhost'
port = 5677


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


@blockext.command('fetch ranking')
def fetch_ranking():
    ws.get_ranking()


@blockext.reporter('ranking')
def ranking():
    if ws.ranking:
        return ':'.join(['%s/%d/%d' % (u[0], u[1], u[2]) for u in ws.ranking])


@blockext.command('reset_all')
def reset_all():
    global ws
    print('reset', host, port)
    ws = client.WebSocketClient(host, port)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        port = sys.argv[2]
    scratch = BlockextThread()
    scratch.start()
    reset_all()
    tornado.ioloop.IOLoop.instance().start()
