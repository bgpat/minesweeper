#!/usr/bin/env python3

import random
import json


class MineSweeper():
    rows = 20
    columns = 30
    offset = {'x': -240, 'y': 140}
    size = 16
    bombs = random.randrange(60, 120)

    def __init__(self, board=None):
        if board is None:
            print('create new board')
            self.new_board()
        else:
            print('copy board', id(board))
            self.board = board
        self.score = 0
        self.highscore = 0

    def new_board(self):
        self.board = Board(self.rows, self.columns, self.bombs)

    def reset_score(self):
        self.score = 0

    def add_score(self, score):
        self.score += score
        if self.highscore < self.score:
            self.highscore = self.score

    def __str__(self):
        return json.dumps({
            'score': self.score,
            'highscore': self.highscore,
            'board': str(self.board),
            'remains': self.board.count_remains(),
            'bombs': self.board.count_bombs(),
            'flags': self.board.count_flags(),
        })


class Board(list):
    def __init__(self, rows, columns, bombs):
        list.__init__(self)
        self.rows = rows
        self.columns = columns
        self.bombs = bombs
        for i in range(rows):
            list.append(self, [Block(i, j) for j in range(columns)])
        self.generate()

    def generate(self):
        for row in self:
            for block in row:
                block.opened = False
                block.flag = False
                block.bomb = False
                block.number = None
        for x in random.sample(range(self.rows * self.columns), self.bombs):
            i = x % self.rows
            j = int(x / self.rows)
            self[i][j].bomb = True
            self[i][j].number = 9
        self.calculate()

    def calculate(self):
        for row in self:
            for block in row:
                if block.bomb and False:
                    continue
                block.number = sum([
                    self.get(block.i - 1, block.j - 1).bomb,
                    self.get(block.i - 1, block.j).bomb,
                    self.get(block.i - 1, block.j + 1).bomb,
                    self.get(block.i, block.j - 1).bomb,
                    self.get(block.i, block.j + 1).bomb,
                    self.get(block.i + 1, block.j - 1).bomb,
                    self.get(block.i + 1, block.j).bomb,
                    self.get(block.i + 1, block.j + 1).bomb
                ])

    def get(self, i, j):
        i = int(i)
        j = int(j)
        if i < 0 or self.rows <= i or j < 0 or self.columns <= j:
            return Block()
        return self[i][j]

    def open(self, i, j):
        block = self.get(i, j)
        if block.number is None or block.opened or block.flag:
            return 0
        block.opened = True
        if block.bomb:
            return False
        if block.number == 0:
            return 1 + sum([
                self.open(i - 1, j - 1),
                self.open(i - 1, j),
                self.open(i - 1, j + 1),
                self.open(i, j - 1),
                self.open(i, j + 1),
                self.open(i + 1, j - 1),
                self.open(i + 1, j),
                self.open(i + 1, j + 1)
            ])
        return 1

    def flag(self, i, j):
        block = self.get(i, j)
        block.flag ^= 1

    def count_remains(self):
        return sum([sum([not b.opened for b in r]) for r in self])

    def count_bombs(self):
        return sum([sum([b.bomb and not b.opened for b in r]) for r in self])

    def count_flags(self):
        return sum([sum([b.flag for b in r]) for r in self])

    def get_flags(self):
        return ''.join([''.join([str(int(b.flag)) for b in r]) for r in self])

    def set_flags(self, flags):
        for i in range(self.rows):
            for j in range(self.columns):
                if flags[i * self.rows + j] == '1':
                    self.flag(i, j)

    def debug(self):
        return '\n'.join([' '.join([str(b) for b in row]) for row in self])

    def __str__(self):
        return ''.join([''.join([str(b) for b in row]) for row in self])

    def __hash__(self):
        b = ''.join([''.join([str(int(b.bomb)) for b in r]) for r in self])
        return int(b, 2)


class Block():
    def __init__(self, i=None, j=None):
        self.bomb = False
        self.flag = False
        self.opened = False
        self.number = None
        self.i = i
        self.j = j

    def __str__(self):
        if not self.opened:
            return 'f' if self.flag else '-'
        if self.bomb:
            return '*'
        return str(self.number)
