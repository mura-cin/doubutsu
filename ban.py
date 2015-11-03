
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

class Board():

    str2index = {x:i for i, x in enumerate([chr(ord('A')+x) + str(y)
                                        for y in range(1,5) for x in range(3)])}
    index2str = {i:x for i, x in enumerate([chr(ord('A')+x) + str(y)
                                        for y in range(1,5) for x in range(3)])}
    
    # Board命令で返ってきた文字列を引数として盤面を生成する。
    def __init__(self, bd):
        bd = bd.split(", ")
        bd[-1] = bd[-1].rstrip(",") # 最後にカンマが残ってしまうので、それを除去
        
        self.board = []          # 盤面情報
        self.turn = 1            # 手番
        self.notOnBoard = []     # 駒が置かれていない座標
        self.capturedPiece1 = [] # プレイヤー1の持ち駒
        self.capturedPiece2 = [] # プレイヤー2の持ち駒
        
        for i in range(12):
            c, k = bd[i].split(" ")
            if k[0] == 'c':
                self.board.append(koma.Chick(int(k[1])))
            elif k[0] == 'h':
                self.board.append(koma.Hen(int(k[1])))
            elif k[0] == 'e':
                self.board.append(koma.Elephant(int(k[1])))
            elif k[0] == 'g':
                self.board.append(koma.Giraffe(int(k[1])))
            elif k[0] == 'l':
                self.board.append(koma.Lion(int(k[1])))
            else:               # 何もない
                self.board.append(None)
                self.notOnBoard.append(c)

        for x in bd:
            c, k = x.split(" ")
            if c[0] == 'D':
                if k[0] == 'c':
                    self.capturedPiece1.append(koma.Chick(1))
                elif k[0] == 'h':
                    self.capturedPiece1.append(koma.Hen(1))
                elif k[0] == 'e':
                    self.capturedPiece1.append(koma.Elephant(1))
                elif k[0] == 'g':
                    self.capturedPiece1.append(koma.Giraffe(1))
                elif k[0] == 'l':
                    self.capturedPiece1.append(koma.Lion(1))
                    
            elif c[0] == 'E':
                if k[0] == 'c':
                    self.capturedPiece2.append(koma.Chick(2))
                elif k[0] == 'h':
                    self.capturedPiece2.append(koma.Hen(2))
                elif k[0] == 'e':
                    self.capturedPiece2.append(koma.Elephant(2))
                elif k[0] == 'g':
                    self.capturedPiece2.append(koma.Giraffe(2))
                elif k[0] == 'l':
                    self.capturedPiece2.append(koma.Lion(2))

    def __str__(self):
        line = ""
        for i in range(12):
            if self.board[i] is None:
                line += "--"
                continue
            line += str(self.board[i])
        for x in self.capturedPiece1:
            line += str(x)
        for x in self.capturedPiece2:
            line += str(x)

        return line

    # 動ける場所のインデックスのリストを返す
    def movablePlace(self, src):
        ret = []
        for dst in self.board[src].nextMove[src]:
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
            for i, p in enumerate(self.capturedPiece1):
                for j in range(12):
                    if self.board[j] is not None: continue
                    
                    bd = copy.deepcopy(self)
                    bd.c_move(i, p, j)
                    ret.append(bd.board)
        else:
            for i, p in enumerate(self.capturedPiece2):
                for j in range(12):
                    if self.board[j] is not None: continue
                    
                    bd = copy.deepcopy(self)
                    bd.c_move(i, p, j)
                    ret.append(bd.board)
        return ret


    # 盤上の駒を動かす
    def move(self, si, di):
        if self.board[di] is not None:
            if self.board[si].player == 1:
                self.board[di].player = 1
                self.capturedPiece1.append(self.board[di])
            else:
                self.board[di].player = 2
                self.capturedPiece2.append(self.board[di])

        # ひよこ -> にわとりの処理
        if self.board[si].player == 1:
            if isinstance(self.board[si], koma.Chick) and 0 <= di <= 2:
                self.board[di] = koma.Hen(1)
            else:
                self.board[di] = self.board[si]
        else:
            if isinstance(self.board[si], koma.Chick) and 9 <= di <= 11:
                self.board[di] = koma.Hen(2)
            else:
                self.board[di] = self.board[si]
                
        self.board[si] = None
        
    # 持ち駒を動かす(持ち駒のindex, 持ち駒のオブジェクト, 移動先のindex)
    def c_move(self, ci, c, di):
        if c.player == 1:
            self.capturedPiece1.pop(ci)
        else:
            self.capturedPiece2.pop(ci)
        self.board[di] = c

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
                value += x.retValue() # 駒自体の点数
                if not isinstance(x, koma.Lion): # ライオン以外で動ける範囲で点数
                    value += len(self.movablePlace(i))*2                
            else:
                value -= x.retValue()
                if not isinstance(x, koma.Lion):
                    value -= len(self.movablePlace(i))*2

        for x in self.capturedPiece1:
            value += x.retValue()
        for x in self.capturedPiece2:
            value -= x.retValue()
                
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
                b = self.board[i*3 + j]
                if b is not None:
                    line += str(b) + " "
                else:
                    line += "-- "
            print(line)

        if len(self.capturedPiece1) == 0:
            print("持ち駒：なし")
        else:
            print("持ち駒：" + str(self.capturedPiece1))
                
