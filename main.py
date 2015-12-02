# -*- coding: utf-8 -*-

import socket
import time
import copy
import random
import ban

#serverName = "localhost"
serverName = "10.2.77.149"
serverPort = 4444

# プレイヤー1の場合
def alpha_beta1(turn, board, depth, alpha, beta):
    if depth <= 0: return board.calcBoard()

    if turn:    # 自分の手番
        if board.isTried(1): return 5000

        for i in range(12):
            if board.board[i] is None or board.board[i].player != 1: continue

            ret = board.movablePlace(i)
            for x in ret:
                board.move(i, x)
                if board.isCatchedLion(1):
                    board.restore_move()
                    return 5000

                alpha = max(alpha, alpha_beta1(not turn, board, depth-1, alpha, beta))
                board.restore_move()
                if alpha >= beta: return beta

        for i in range(len(board.capturedPiece1)):
            for j in range(12):
                if board.board[j] is not None: continue

                board.c_move(i, board.capturedPiece1[i], j)
                alpha = max(alpha, alpha_beta1(not turn, board, depth-1, alpha, beta))
                board.restore_move()

                if alpha >= beta: return beta

        return alpha
                
    else:                       # 相手の手番
        if board.isTried(2): return -5000

        for i in range(12):
            if board.board[i] is None or board.board[i].player != 2: continue

            ret = board.movablePlace(i)
            for x in ret:
                board.move(i, x)
                if board.isCatchedLion(2):
                    board.restore_move()
                    return -5000

                beta = min(beta, alpha_beta1(not turn, board, depth-1, alpha, beta))
                board.restore_move()
                if alpha >= beta: return alpha

        for i in range(len(board.capturedPiece2)):
            for j in range(12):
                if board.board[j] is not None: continue

                board.c_move(i, board.capturedPiece2[i], j)
                beta = min(beta, alpha_beta1(not turn, board, depth-1, alpha, beta))
                board.restore_move()
                if alpha >= beta: return alpha
                    
        return beta

# プレイヤー2の時
def alpha_beta2(turn, board, depth, alpha, beta):
    if depth <= 0: return board.calcBoard()
    
    if turn:                    # 自分の手番
        if board.isTried(2): return -5000
            
        for i in range(12):
            if board.board[i] is None or board.board[i].player != 2: continue

            ret = board.movablePlace(i)
            for x in ret:
                board.move(i, x)
                if board.isCatchedLion(2):
                    board.restore_move()
                    return -5000

                beta = min(beta, alpha_beta2(not turn, board, depth-1, alpha, beta))
                board.restore_move()
                if alpha >= beta: return alpha

        for i in range(len(board.capturedPiece2)):
            for j in range(12):
                if board.board[j] is not None: continue
                
                board.c_move(i, board.capturedPiece2[i], j)
                beta = min(beta, alpha_beta2(not turn, board, depth-1, alpha, beta))
                board.restore_move()
                if alpha >= beta: return alpha

        return beta

    else:                       # 相手の手番
        if board.isTried(1): return 5000
            
        for i in range(12):
            if board.board[i] is None or board.board[i].player != 1: continue

            ret = board.movablePlace(i)
            for x in ret:
                board.move(i, x)
                if board.isCatchedLion(1):
                    board.restore_move()
                    return 5000

                alpha = max(alpha, alpha_beta2(not turn, board, depth-1, alpha, beta))
                board.restore_move()
                if alpha >= beta: return beta

        for i in range(len(board.capturedPiece1)):
            for j in range(12):
                if board.board[j] is not None: continue
                    
                board.c_move(i, board.capturedPiece1[i], j)
                alpha = max(alpha, alpha_beta2(not turn, board, depth-1, alpha, beta))
                board.restore_move()
                if alpha >= beta: return beta
                    
        return alpha
        


def first_search(player, board):
    start = time.time()
    
    ret_board = None
    board.turn = player
    val = 0
    winFlag = False
    nextMoveList = []

    if player == 1:
        val = -9999
    else:
        val = 9999

    print("探索：")
    searchList = []
    for i in range(12):
        if board.board[i] is None or board.board[i].player != player: continue

        ret = board.movablePlace(i)

        for x in ret:
            bd = copy.deepcopy(board)
            bd.move(i, x)
            if bd.isCatchedLion(player): return (bd, ban.Board.index2str[i], ban.Board.index2str[x])
            searchList.append([bd, ban.Board.index2str[i], ban.Board.index2str[x]])

    if player == 1:
        for i in range(len(board.capturedPiece1)):
            for j in range(12):
                if board.board[j] is not None: continue
                
                bd = copy.deepcopy(board)
                bd.c_move(i, board.capturedPiece1[i], j)
                searchList.append([bd, "D"+str(i+1), ban.Board.index2str[j]])

        for bd in searchList:
            if (len(bd[0].capturedPiece1)+len(bd[0].capturedPiece2)) >= 5:
                s_result = alpha_beta1(False, bd[0], 5, -9999, 9999)
            elif (len(bd[0].capturedPiece1)+len(bd[0].capturedPiece2)) >= 3:
                s_result = alpha_beta1(False, bd[0], 6, -9999, 9999)
            else:
                s_result = alpha_beta1(False, bd[0], 7, -9999, 9999)
            print("評価値：" + str(s_result))
            bd[0].showBoard()

            if s_result == 5000:
                winFlag = True
                nextMoveList.append(tuple(bd))

            if s_result == val:
                if random.randint(1, 2) == 1:
                    ret_board = bd
                    print(ret_board)
            if s_result > val:
                val = s_result
                ret_board = bd
                print(ret_board)

            if time.time() - start > 120: break        
    else:
        for i in range(len(board.capturedPiece2)):
            for j in range(12):
                if board.board[j] is not None: continue
                
                bd = copy.deepcopy(board)
                bd.c_move(i, board.capturedPiece2[i], j)
                searchList.append([bd, "E"+str(i+1), ban.Board.index2str[j]])

        for bd in searchList:
            if (len(bd[0].capturedPiece1)+len(bd[0].capturedPiece2)) >= 5:
                s_result = alpha_beta2(False, bd[0], 5, -9999, 9999)
            elif (len(bd[0].capturedPiece1)+len(bd[0].capturedPiece2)) >= 3:
                s_result = alpha_beta2(False, bd[0], 6, -9999, 9999)
            else:
                s_result = alpha_beta2(False, bd[0], 7, -9999, 9999)
            print("評価値：" + str(s_result))
            bd[0].showBoard()

            if s_result == -5000:
                winFlag = True
                nextMoveList.append(tuple(bd))

            if s_result == val:
                if random.randint(1, 2) == 1:
                    ret_board = bd
                    print(ret_board)
            if s_result < val:
                val = s_result
                ret_board = bd
                print(ret_board)

            if time.time() - start > 120: break # 2分を超えていたら強制的に探索を打ち切る

    elapsed_time = time.time() - start
    print()
    print("# elapsed_time:{0}[sec]".format(elapsed_time))

    if winFlag:
        return random.choice(nextMoveList)
    
    return tuple(ret_board)

def isMatchBoard(b1, b2):
    for i in range(12):
        if type(b1[i]) != type(b2[i]):
            return False
    return True

def isCheating(prevBoard, recvBoard):
    prevBoard.turn = anoPlayer
    print("-> " + str(recvBoard.board))
    for x in prevBoard.makeNextBoard():
        print(x)
        if isMatchBoard(recvBoard.board, x): return False
        
    return True

BUFSIZE = 1024

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
    line = "board"
    s.send((line + "\n").encode())
    time.sleep(0.1)
    ret = s.recv(BUFSIZE).rstrip().decode()
    board = ban.Board(ret)
    if prevBoard is not None:
        if isMatchBoard(prevBoard.board, board.board):
            if board.calcBoard() > 1000:
                print("Player1 win!")
                input("")
                break
            elif board.calcBoard() < -1000:
                print("Player2 win!")
                input("")
                break
            else:
                continue
        else:
            if isCheating(prevBoard, board):
                if player == 1:
                    print("Player2 is cheating")
                    input("")
                    break
                else:
                    print("Player1 is cheating")
                    input("")
                    break
            else:
                if board.calcBoard() > 1000:
                    print("Player1 win!")
                    input("")
                    break
                elif board.calcBoard() < -1000:
                    print("Player2 win!")
                    input("")
                    break
                elif board.isTried(player):
                    print("Player" + str(player) + " lion is tried")
                    input("")
                    break

    while True:
        line = "turn"
        s.send((line + "\n").encode())
        time.sleep(0.1)
        ret = s.recv(BUFSIZE).rstrip().decode()
        if str(player) in ret: break
        
    
    board.turn = player
    board.showBoard()

    prevBoard, src, dst = first_search(player, board)

    print("")
    print("決定した手：")
    prevBoard.showBoard()
    
    line = "mv " + src + " " + dst
    print(line)
    s.send((line + "\n").encode())
    time.sleep(0.1)
    print(s.recv(BUFSIZE).rstrip().decode())

    time.sleep(1)

print("bye")
s.close()
