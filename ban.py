# -*- coding: utf-8 -*-
"""
座標について

E -> プレイヤー2の持ち駒

A1 B1 C1        0  1  2
A2 B2 C2  --->  3  4  5
A3 B3 C3  --->  6  7  8
A4 B4 C4        9 10 11 

D -> プレイヤー1の持ち駒
"""

import koma
import copy
import collections

class Board:
    str2index = {x: i for i, x in enumerate([chr(ord('A') + x) + str(y)
                                             for y in range(1, 5) for x in range(3)])}
    index2str = {i: x for i, x in enumerate([chr(ord('A') + x) + str(y)
                                             for y in range(1, 5) for x in range(3)])}

    # Board命令で返ってきた文字列を引数として盤面を生成する。
    def __init__(self, bd):
        bd = bd.split(", ")
        bd[-1] = bd[-1].rstrip(",")  # 最後にカンマが残ってしまうので、それを除去

        self.board = []  # 盤面情報
        self.turn = 1  # 手番
        self.capturedPiece1 = []  # プレイヤー1の持ち駒
        self.capturedPiece2 = []  # プレイヤー2の持ち駒
        # (使ったメソッド, 動かす前のインデックス, 動かした先のインデックス, 動かす前の駒, 動かした先の駒)
        self.moveHistory = collections.deque() # 指し手の履歴
        self.pieces = {
            "c1" : koma.Chick(1),
            "c2" : koma.Chick(2),
            "h1" : koma.Hen(1),
            "h2" : koma.Hen(2),
            "e1" : koma.Elephant(1),
            "e2" : koma.Elephant(2),
            "g1" : koma.Giraffe(1),
            "g2" : koma.Giraffe(2),
            "l1" : koma.Lion(1),
            "l2" : koma.Lion(2),
        }

        for i in range(12):
            c, k = bd[i].split(" ")
            if k == "--":
                self.board.append(None)
            else:
                self.board.append(self.pieces[k])

        for x in bd:
            c, k = x.split(" ")
            if c[0] == 'D':
                self.capturedPiece1.append(self.pieces[k])
            elif c[0] == 'E':
                self.capturedPiece2.append(self.pieces[k])


    # 動ける場所のインデックスのリストを返す
    def movablePlace(self, src):
        ret = []
        for dst in self.board[src].getNextMove()[src]:
            if self.board[dst] is None \
                    or self.board[src].player != self.board[dst].player:
                ret.append(dst)
        return ret

    # 次の手の盤面を生成する関数(情報としてはboard.boardのみ)
    def makeNextBoard(self):
        ret = []
        for i in range(12):
            # 駒がない、または自分の駒ではない場合はスキップする
            if self.board[i] is None or self.board[i].player != self.turn: continue

            mov = self.movablePlace(i)
            for dst in mov:
                bd = copy.deepcopy(self)
                bd.move(i, dst)
                ret.append(bd.board)

        if self.turn == 1:
            for i in range(len(self.capturedPiece1)):
                for j in range(12):
                    if self.board[j] is not None: continue

                    bd = copy.deepcopy(self)
                    bd.c_move(i, self.capturedPiece1[i], j)
                    ret.append(bd.board)
        else:
            for i in range(len(self.capturedPiece2)):
                for j in range(12):
                    if self.board[j] is not None: continue

                    bd = copy.deepcopy(self)
                    bd.c_move(i, self.capturedPiece2[i], j)
                    ret.append(bd.board)
        return ret

    # 盤上の駒を動かす
    # 相手のコマを取った場合にはTrueを返す
    def move(self, si, di):
        self.moveHistory.appendleft(tuple(["move", si, di, copy.copy(self.board[si]), \
                                           copy.copy(self.board[di])]))

        # 駒を取る時
        if self.board[di] is not None:
            if self.board[si].player == 1:
                if isinstance(self.board[di], koma.Elephant):
                    self.capturedPiece1.append(self.pieces["e1"])
                elif isinstance(self.board[di], koma.Giraffe):
                    self.capturedPiece1.append(self.pieces["g1"])
                elif isinstance(self.board[di], koma.Lion):
                    self.capturedPiece1.append(self.pieces["l1"])
                else:
                    self.capturedPiece1.append(self.pieces["c1"])
            else:
                if isinstance(self.board[di], koma.Elephant):
                    self.capturedPiece2.append(self.pieces["e2"])
                elif isinstance(self.board[di], koma.Giraffe):
                    self.capturedPiece2.append(self.pieces["g2"])
                elif isinstance(self.board[di], koma.Lion):
                    self.capturedPiece2.append(self.pieces["l2"])
                else:
                    self.capturedPiece2.append(self.pieces["c2"])
                    
        # 駒を動かす時
        if self.board[si].player == 1:
            if isinstance(self.board[si], koma.Chick) and 0 <= di <= 2:
                self.board[di] = self.pieces["h1"]
            else:
                self.board[di] = copy.copy(self.board[si])
        else:
            if isinstance(self.board[si], koma.Chick) and 9 <= di <= 11:
                self.board[di] = self.pieces["h2"]
            else:
                self.board[di] = copy.copy(self.board[si])

        self.board[si] = None

    # moveで動かしたのを復元する関数
    def restore_move(self):
        func, si, di, sp, dp = self.moveHistory.popleft()

        if func == "move":
            self.board[si] = sp
            self.board[di] = dp
            if dp is not None:  # 動かした先に駒があった場合
                if sp.player == 1:
                    self.capturedPiece1.pop(-1)
                else:
                    self.capturedPiece2.pop(-1)
        else:
            if sp.player == 1:
                self.capturedPiece1.insert(si, sp)
            else:
                self.capturedPiece2.insert(si, sp)
            self.board[di] = None

    # 持ち駒を動かす(持ち駒のindex, 移動先のindex)
    def c_move(self, ci, p, di):
        self.moveHistory.appendleft(tuple(["c_move", ci, di, copy.copy(p), None]))
        if p.player == 1:
            self.board[di] = self.capturedPiece1.pop(ci)
        else:
            self.board[di] = self.capturedPiece2.pop(ci)

    # playerのライオンがトライしているか
    def isTried(self, player):
        if player == 1:
            # 0 1 2を見てライオンがいるかどうか
            for i in range(3):
                if isinstance(self.board[i], koma.Lion) and self.board[i].player == player:
                    return True

        else:
            # 9 10 11を見てライオンがいるかどうか
            for i in range(9, 12):
                if isinstance(self.board[i], koma.Lion) and self.board[i].player == player:
                    return True
        return False

    # playerが相手のライオンをキャッチしているか
    def isCatchedLion(self, player):
        if player == 1:
            for i in range(12):
                if isinstance(self.board[i], koma.Lion) and self.board[i].player != player:
                    return False
        else:
            for i in range(12):
                if isinstance(self.board[i], koma.Lion) and self.board[i].player != player:
                    return False

        return True

    # 評価値を計算
    def calcBoard(self):
        value = 0

        for i, x in enumerate(self.board):
            if x is None: continue
            if x.player == 1:
                value += x.retValue()  # 駒自体の点数
                if not isinstance(x, koma.Lion):  # ライオン以外で動ける範囲で点数
                    value += len(self.movablePlace(i)) * 2
            else:
                value -= x.retValue()
                if not isinstance(x, koma.Lion):
                    value -= len(self.movablePlace(i)) * 2

        for x in self.capturedPiece1:
            value += x.retValue() + x.retValue()//4
        for x in self.capturedPiece2:
            value -= x.retValue() + x.retValue()//4

        return value

    # デバッグ用
    def showBoard(self):
        if len(self.capturedPiece2) == 0:
            print("持ち駒：なし")
        else:
            print("持ち駒：" + str(self.capturedPiece2))

        for i in range(4):
            line = ""
            for j in range(3):
                b = self.board[i * 3 + j]
                if b is not None:
                    line += str(b) + " "
                else:
                    line += "-- "
            print(line)

        if len(self.capturedPiece1) == 0:
            print("持ち駒：なし")
        else:
            print("持ち駒：" + str(self.capturedPiece1))
