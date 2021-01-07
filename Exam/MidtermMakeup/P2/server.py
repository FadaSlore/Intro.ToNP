#!/usr/bin/env python3
import socket
import argparse
import select
import threading

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

if not args.port.isdecimal():
    print('port should be an interger')
    exit()

host = 'localhost'
port = int(args.port)
address = (host, port)

TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
TCPsocket.bind(address)
TCPsocket.listen(20)

inputs = []
inputs.append(TCPsocket.fileno())

# shared memeory
class User():
    def __init__(self, userID, ip, port):
        self.userID = userID
        self.ip = ip
        self.port = port
        self.online = True
Users = []
UserIDs = []

def exeServer():
    while True:
        readable, _, _ = select.select(inputs, [], [])

        for sockfd in readable:
            if sockfd is TCPsocket.fileno():
                client, address = TCPsocket.accept()
                thread = TCPClientThread(client, address[0], address[1])
                thread.start()

class TCPClientThread(threading.Thread):
    def __init__(self, socketfd, ip, port):
        threading.Thread.__init__(self)
        self.socketfd = socketfd
        # localhost?
        self.ip = ip
        self.port = port
        self.userID = None

    def run(self):
        print(f'New connection from {self.ip}:{self.port}.')
        self.sendTCPmessage('Hello, please assign your username: ')
        while True:
            userName = self.getTCPcommand().strip()
            # print('userName: ', userName)
            existFlag = False
            for user in Users:
                if user.userID == userName:
                    existFlag = True
            if existFlag:
                self.sendTCPmessage('The username is already used!\nHello, please assign your username: ')
            else:
                self.userID = userName
                self.sendTCPmessage(f'Welcome, {self.userID}')
                break
        
        Users.append(User(self.userID, self.ip, self.port))
        UserIDs.append(self.userID)
        UserIDs.sort(key = str.lower)
        # print('UserIDs: ', UserIDs)

        response = []

        while True:
            commands = self.getTCPcommand().strip().split()
            response.clear()

            if len(commands) != 1:
                response.append('Usage: list-users/sort-users/exit')
            elif commands[0] == 'list-users' or commands[0] == 'sort-users':
                firstFlag = True
                for userID in UserIDs:
                    for user in Users:
                        if user.userID == userID and user.online:
                            if firstFlag:
                                response.append(f'{user.userID} {user.ip}:{user.port}')
                                firstFlag = False
                            else:
                                response.append(f'\n{user.userID} {user.ip}:{user.port}')
            # elif commands[0] == 'sort-users':
            #     firstFlag = True
            #     for user in Users:
                # response.append(f'IP: {self.ip}:{self.port}')
            elif commands[0] == 'exit':
                for user in Users:
                    if user.userID == self.userID:
                        user.online = False
                break
            else:
                response.append('Usage: list-users/sort-users/exit')

            message = ''.join(response)
            self.sendTCPmessage(message)
        self.sendTCPmessage(f'Bye, {self.userID}.')
        print(f'{self.userID} {self.ip}:{self.port} disconnected.')
        self.socketfd.close()

    def getTCPcommand(self):
        command = []
        while True:
            part = self.socketfd.recv(1024)
            command.append(str(part, 'utf-8'))
            if len(part) < 1024:
                break
        commands = ''.join(command)
        return commands

    def sendTCPmessage(self, message):
        self.socketfd.sendall(message.encode('utf-8'))


if __name__ == "__main__":
    try:
        print('Start server.')
        exeServer()
    except KeyboardInterrupt:
        print('\nExit server.')
        TCPsocket.close()

