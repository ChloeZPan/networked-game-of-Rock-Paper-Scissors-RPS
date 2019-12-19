#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Zeyi Pan'

import socket
import pickle
import time
import sys
import re


class Game:
    client_name = None
    server_name = None
    client_move = None
    server_move = None
    moves = [None, None]
    client_result = None
    server_result = None
    winner_name = None
    move = {'r': 0, 'p': 1, 's': 2}
    full_name = {'r': 'rock', 'p': 'paper', 's': 'scissors'}

    def result(self, move1, move2):
        """rock 0 paper 1 scissors 2
           loss 0 win 1 draw 2"""
        c1 = self.move[move1]
        c2 = self.move[move2]
        if c1 - c2 == -2 or c1 - c2 == 1:
            c_result = 1
            s_result = 0
        elif c1 - c2 == -1 or c1 - c2 == 2:
            c_result = 0
            s_result = 1
        else:
            c_result = 2
            s_result = 2
        if c_result == 1:
            self.winner_name = self.client_name
        if s_result == 1:
            self.winner_name = self.server_name
        result_dict = {0: 'YOU LOSE...', 1: 'YOU WIN!', 2: 'DRAW'}
        self.client_result = result_dict[c_result]
        self.server_result = result_dict[s_result]

    @property
    def make_move(self):
        move = input('Please choose from (r)ock, (p)aper, (s)cissors\n---->')
        while move not in ['r', 'p', 's']:
            move = input('(r)ock, (p)aper, (s)cissors\nYou choose...')
        return move


def start(player, type, address):
    if type == 'server':
        port = int(address)
        if port not in range(1, 65536):
            print('The port number should between 0 ~ 65535. Your port is {}'.format(port))
            sys.exit(1)
        print('Welcome {}! Finding a game...'.format(player))
        time.sleep(2)
        p = Game()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print('Error creating socket: %s'% e)
            sys.exit(1)
        try:
            s.bind(('127.0.0.1', port))
            s.listen(1)
            c, addr = s.accept()
            print('Connected by', addr)
            # step 1: receive opppnent's name
            opp_name = pickle.loads(c.recv(4096)).client_name
            p.client_name = opp_name
            print('Your opponent: {} join the game'.format(opp_name))
            # step 2: send name to opponent
            p.server_name = player
            c.send(pickle.dumps(p))
            # step 3: make a move
            move = p.make_move
            p.server_choice = move
            print('You choose {}, please wait for your opponents...'.format(move))
            # step 4: receive notice from opponent
            opp_notice = pickle.loads(c.recv(4096))
            print('{} is {}'.format(opp_name, opp_notice))
            time.sleep(2)
            notice = 'Ready!'
            # step 5: send your notice
            c.send(pickle.dumps(notice))
            # step 6: receive move and send move, then countdown to see result
            opp_move = pickle.loads(c.recv(4096))
            c.send(pickle.dumps(move))
            print('Move sent!')
            p.result(opp_move, move)
            print('3')
            time.sleep(1)
            print('2')
            time.sleep(1)
            print('1')
            time.sleep(1)
            print('GAME OVER: {}'.format(p.server_result))
            print('The winner is {}'.format(p.winner_name))
            print('opponent\'s move is {}'.format(p.full_name[opp_move]))
        except socket.error as e:
            print(e)
        c.close()
    if type == 'client':
        host = address.split(':')[0]
        if re.match('\d.\d.\d.\d', host) is None:
            print('Host format is wrong')
            sys.exit(1)
        port = int(address.split(':')[1])
        if port not in range(1, 65536):
            print('The port number should between 0 ~ 65535. Your port is {}'.format(port))
            sys.exit(1)
        print('Welcome {}! Finding a game...'.format(player))
        time.sleep(2)
        p = Game()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print('Error creating socket: %s' % e)
            sys.exit(1)
        try:
            s.connect((host, port))
        except socket.gaierror as e:
            print('Address-related error connecting to server: %s' % e)
            sys.exit(1)
            # step 1: send name to opppnent
        try:
            p.client_name = player
            s.send(pickle.dumps(p))
            # step 2: receive opponent's name
            opp_name = pickle.loads(s.recv(4096)).server_name
            p.server_name = opp_name
            print('Your opponent: {} join the game'.format(opp_name))
            # step 3: make a move
            move = p.make_move
            p.client_choice = move
            print('You choose {}, please wait for your opponent...'.format(move))
            # step 4: send your notice
            notice = 'Ready!'
            s.send(pickle.dumps(notice))
            # step 5: receive opp's notice
            opp_notice = pickle.loads(s.recv(4096))
            print('{} is {}'.format(opp_name, opp_notice))
            time.sleep(2)
            # step 6: send your move and receive move, then countdown to see the result
            s.send(pickle.dumps(move))
            print('Move sent!')
            opp_move = pickle.loads(s.recv(4096))
            p.result(move, opp_move)
            print('3')
            time.sleep(1)
            print('2')
            time.sleep(1)
            print('1')
            time.sleep(1)
            print('GAME OVER: {}'.format(p.client_result))
            print('The winner is {}'.format(p.winner_name))
            print('opponent\'s move is {}'.format(p.full_name[opp_move]))
        except socket.error as e:
            print(e)
        s.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('You should enter 3 arguments in commend line. You only entered {}.'.format(len(sys.argv)))
        sys.exit(1)
    player = sys.argv[1]
    type = sys.argv[2]
    address = sys.argv[3]
    start(player, type, address)
