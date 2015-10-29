# -*- coding: utf-8 -*-

import socket
import time
import copy
import random
import ban

memo = {}

def minimax(player, board, depth):
    if str(board) in memo:
        return memo[str(board)]
    
    if depth == 0:
        return board.calcBoard()
    
    if board.calcBoard() > 1500: return 9999
    if board.calcBoard() < -1500: return -9999
    val = 0
        
    if board.turn == player: # 自分の手番
        if player == 1: val = -5000
        if player == 2: val =  5000

        # 自分がトライしてるか
        if board.isTried(board.turn):
            if player == 1: return 9999
            else: return -9999
        
        for i in range(12):
            if board.board[i] is None or board.turn != board.board[i].player: continue
            
            ret = board.movablePlace(i)
            for x in ret:
                bd = copy.deepcopy(board)
                bd.move(i, x)

                bd.turn = bd.turn%2 + 1
                score = minimax(player, bd, depth-1);

                if player == 1: val = max(val, score) # 評価値が大きくなるように
                if player == 2: val = min(val, score) # 評価値が小さくなるように

        """
        if player == 1:
            for i, p in enumerate(board.capturedPiece1):
                for dst in board.notOnBoard:
                    bd = copy.deepcopy(board)
                    bd.c_move(i, p, ban.Board.str2index[dst])
                    
                    bd.turn = bd.turn%2 + 1
                    score = minimax(player, bd, depth-1)
                    
                    val = max(val, score)
        else:
            for i, p in enumerate(board.capturedPiece2):
                for dst in board.notOnBoard:
                    bd = copy.deepcopy(board)
                    bd.c_move(i, p, ban.Board.str2index[dst])
                    
                    bd.turn = bd.turn%2 + 1
                    score = minimax(player, bd, depth-1)
                    
                    val = min(val, score)
        """
        return val
    
    else:                    # 相手の手番
        if player == 1: val =  5000
        if player == 2: val = -5000

        # 相手がトライしてるか
        if board.isTried(board.turn):
            if player == 1: return -9999
            else: return 9999
        
        for i in range(12):
            if board.board[i] is None or board.turn != board.board[i].player: continue
            
            ret = board.movablePlace(i)
            for x in ret:
                bd = copy.deepcopy(board)
                bd.move(i, x)

                bd.turn = bd.turn%2 + 1
                score = minimax(player, bd, depth-1)
                
                if player == 1: val = min(val, score) # 評価値が小さくなるように
                if player == 2: val = max(val, score) # 評価値が大きくなるように

        """
        if player == 1:
            for i, p in enumerate(board.capturedPiece1):
                for dst in board.notOnBoard:
                    bd = copy.deepcopy(board)
                    bd.c_move(i, p, ban.Board.str2index[dst])

                    bd.turn = bd.turn%2 + 1
                    score = minimax(player, bd, depth-1)

                    val = min(val, score)
        else:
            for i, p in enumerate(board.capturedPiece2):
                for dst in board.notOnBoard:
                    bd = copy.deepcopy(board)
                    bd.c_move(i, p, ban.Board.str2index[dst])
                    
                    bd.turn = bd.turn%2 + 1
                    score = minimax(player, bd, depth-1)
                    
                    val = max(val, score)
        """


        return val


def first_search(player, board):
    global memo
    ret_board = None
    board.turn = player%2 + 1  # first_searchで一回動かしてからminimaxに投げるので1->2 or 2->1にする
    val = 0

    if player == 1:
        val = -9999
    else:
        val = 9999

    print("探索：")
    for i in range(12):
        if board.board[i] is None or board.board[i].player != player: continue

        ret = board.movablePlace(i)

        for x in ret:
            bd = copy.deepcopy(board)
            bd.move(i, x)

            s_result = minimax(player, bd, 4) # とりあえず深さ2で探索する
            bd.turn = bd.turn%2 + 1
            memo[str(bd)] = s_result

            print("評価値: " + str(s_result))
            bd.showBoard()

            if s_result == val:
                if random.randint(1, 2) == 1:
                    ret_board = (bd, ban.Board.index2str[i], ban.Board.index2str[x])

            if player == 1 and s_result > val:
                val = s_result
                ret_board = (bd, ban.Board.index2str[i], ban.Board.index2str[x])
                print(ret_board)

            if player == 2 and s_result < val:
                val = s_result
                ret_board = (bd, ban.Board.index2str[i], ban.Board.index2str[x])
                print(ret_board)

    if player == 1:
        for i, p in enumerate(board.capturedPiece1):
            for dst in board.notOnBoard:
                bd = copy.deepcopy(board)
                bd.c_move(i, p, ban.Board.str2index[dst])
                
                s_result = minimax(player, bd, 4)
                bd.turn = bd.turn%2 + 1
                memo[str(bd)] = s_result
                
                print("評価値:" + str(s_result))
                bd.showBoard()
                if s_result > val:
                    ret_board = (bd, "D"+str(i+1), dst)
                    print(ret_board)
    else:
        for i, p in enumerate(board.capturedPiece2):
            for dst in board.notOnBoard:
                bd = copy.deepcopy(board)
                bd.c_move(i, p, ban.Board.str2index[dst])

                
                s_result = minimax(player, bd, 4)
                bd.turn = bd.turn%2 + 1
                memo[str(bd)] = s_result
                
                print("評価値:" + str(s_result))
                bd.showBoard()
                if s_result < val:
                    ret_board = (bd, "E"+str(i+1), dst)
                    print(ret_board) 
    
    return ret_board

def isMatchBoard(b1, b2):
    for i in range(12):
        if type(b1[i]) != type(b2[i]):
            return False
    return True

BUFSIZE = 1024

serverName = "localhost"
#serverName = "10.2.77.191"
serverPort = 4444

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverName, serverPort))
ret = s.recv(BUFSIZE).rstrip().decode()
print(ret)

prevBoard = None
if "1" in ret:
    player = 1
    anoPlayer = 2
else:
    player = 2
    anoPlayer = 1
    
    # 初期配置
    prevBoard = ban.Board("A1 g2, B1 l2, C1 e2, A2 --, B2 c2, C2 --, A3 --, B3 c1, C3 --, A4 e1, B4 l1, C4 g1,")
    

while True:
    line = "turn"    
    s.send((line + "\n").encode())
    time.sleep(0.1)
    ret = s.recv(BUFSIZE).rstrip().decode()
    if str(player) not in ret: continue
    
    line = "board"
    s.send((line + "\n").encode())
    time.sleep(0.1)
    ret = s.recv(BUFSIZE).rstrip().decode()
    board = ban.Board(ret)
    board.turn = player

    board.showBoard()

    # 反則の判定
    print("反則の判定：")
    if prevBoard is not None:
        flag = False
        prevBoard.turn = anoPlayer
        print("->" + str(board.board))
        for x in prevBoard.makeNextBoard():
            print(x)
            if isMatchBoard(board.board, x):
                flag = True
                break
        if not flag:
            print("Player " + str(anoPlayer) + " is foul")
            input("")
            break

    if board.calcBoard() > 1000:
        print("Player1 win!")
        input("")
        break
    if board.calcBoard() < -1000:
        print("Player2 win!")
        input("")
        break

    # トライしているか
    if board.isTried(player):
        print("Player" + str(player) + " lion is tried!")
        input("")
        break

    ret = first_search(player, board)
    if ret is not None:
        board, src, dst = ret
    else:
        print("Player" + str(player) + "lose...")

    print("")
    print("決定した手：")
    board.showBoard()
    
    line = "mv " + src + " " + dst
    print(line)
    s.send((line + "\n").encode())
    time.sleep(0.1)
    print(s.recv(BUFSIZE).rstrip().decode())

    prevBoard = board

    time.sleep(1)

print("bye")
s.close()
