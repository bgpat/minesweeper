#!/usr/bin/env python3

import os
import sqlite3
import binascii
import passlib.hash
import minesweeper


class UserManager(dict):
    path = 'user.db'

    def __init__(self):
        dict.__init__(self)
        self.connection = sqlite3.connect(self.path)
        self.create_table()
        self.board = None

    def __del__(self):
        self.connection.close()

    def create_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS `users` (
            `name` TEXT PRIMARY KEY,
            `password` TEXT NOT NULL,
            `score` INTEGER NOT NULL DEFAULT '0',
            `highscore` INTEGER NOT NULL DEFAULT '0'
        )'''
        self.connection.execute(sql)

    def login(self, name, password):
        user = User(self, name, password)
        if user.authenticated:
            self[user.token] = user
            return user
        return False

    def register(self, name, password):
        user = User(self, name, password)
        if user.authenticated is None:
            self[user.token] = user
            user.insert()
            return user
        return False

    def rewrite(self):
        for u in self.values():
            u.ms.board = self.board


class User():
    def __init__(self, manager, name, password):
        self.manager = manager
        self.cursor = manager.connection.cursor()
        self.ws = None
        self.name = name
        self.password = password
        self.token = binascii.hexlify(os.urandom(16)).decode('utf-8')
        self.authenticated = self.authorize()
        self.score = 0
        self.highscore = 0
        self.select()
        self.ms = minesweeper.MineSweeper(self.manager.board)
        self.ms.score = self.score
        self.ms.highscore = self.highscore

    def authorize(self):
        sql = 'SELECT `password` FROM `users` WHERE `name` = ?'
        self.cursor.execute(sql, (self.name,))
        self.manager.connection.commit()
        res = self.cursor.fetchone()
        if res is None:
            return None
        return passlib.hash.sha256_crypt.verify(self.password, res[0])

    def select(self):
        if not self.authenticated:
            return
        sql = 'SELECT `score`, `highscore` FROM `users` WHERE `name` = ?'
        self.cursor.execute(sql, (self.name,))
        self.manager.connection.commit()
        res = self.cursor.fetchone()
        self.score = res[0]
        self.highscore = res[0]

    def insert(self):
        sql = 'INSERT INTO `users` (`name`, `password`) VALUES(?, ?)'
        password = passlib.hash.sha256_crypt.encrypt(self.password)
        self.cursor.execute(sql, (self.name, password))
        self.manager.connection.commit()

    def update(self):
        if not self.authenticated:
            return
        sql = '''UPDATE `users`
            SET `score` = ?,
                `highscore` = ?
            WHERE `name` = ?'''
        data = (
            self.ms.score,
            self.ms.highscore,
            self.name,
        )
        print('update', data)
        self.cursor.execute(sql, data)
        self.manager.connection.commit()
