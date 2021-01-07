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
    def __init__(self, number, userName, socketfd, ip, port):
        self.number = number
        self.userName = userName
        self.socketfd = socketfd
        self.ip = ip
        self.port = port
        self.online = True
        self.mute = False
Users = []

def exeServer():
    userNumber = 0
    while True:
        readable, _, _ = select.select(inputs, [], [])

        for sockfd in readable:
            if sockfd is TCPsocket.fileno():
                client, address = TCPsocket.accept()
                userNumber += 1
                print(f'New connection from {address[0]}:{address[1]} user{userNumber}.')
                Users.append(User(userNumber, f'user{userNumber}', client, address[0], address[1]))
                thread = TCPClientThread(client, address[0], address[1], userNumber)
                thread.start()

class TCPClientThread(threading.Thread):
    def __init__(self, socketfd, ip, port, userNumber):
        threading.Thread.__init__(self)
        self.socketfd = socketfd
        self.ip = ip
        self.port = port
        self.userNumber = userNumber

    def run(self):
        self.sendTCPmessage(f'**************************\n* Welcome to the BBS server. *\n**************************\nWelcome, user{self.userNumber}.')
        response = []

        while True:
            commands = self.getTCPcommand().strip().split()
            response.clear()

            if commands[0] == 'mute':
                if len(commands) != 1:
                    response.append('Usage: mute')
                else:
                    for user in Users:
                        if user.number == self.userNumber:
                            if user.mute:
                                response.append('You are already in mute mode.')
                            else:
                                user.mute = True
                                response.append('Mute mode.')
                            break
            elif commands[0] == 'unmute':
                if len(commands) != 1:
                    response.append('Usage: unmute')
                else:
                    for user in Users:
                        if user.number == self.userNumber:
                            if user.mute:
                                user.mute = False
                                response.append('Unmute mode.')
                            else:
                                response.append('You are already in unmute mode.')
                            break
            elif commands[0] == 'yell':
                if len(commands) == 1:
                    response.append('Usage: yell <message>')
                else:
                    message = ' '.join(commands[1:])
                    self.sendPublicMessage(f'user{self.userNumber}: {message}')
            elif commands[0] == 'tell':
                if len(commands) < 3:
                    response.append('Usage: yell <message>')
                else:
                    receiver = commands[1]
                    message = ' '.join(commands[2:])
                    returnValue = self.sendPrivateMessage(receiver, f'user{self.userNumber} told you: {message}')
                    if returnValue == 0:
                        response.append(f'{receiver} does not exist.')
                    elif returnValue == 1:
                        response.append(f'{receiver} is yourself.')
                    elif returnValue == 2:
                        response.append(f'{receiver} is in mute mode.')
            elif commands[0] == 'exit':
                if len(commands) != 1:
                    response.append('Usage: exit')
                else:
                    for user in Users:
                        if user.number == self.userNumber:
                            user.online = False
                    break
            else:
                response.append('Unsupport command.')

            message = ''.join(response)
            self.sendTCPmessage(message)
        self.sendTCPmessage(f'Bye, user{self.userNumber}.')
        print(f'user{self.userNumber} {self.ip}:{self.port} disconnected.')
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

    def sendPublicMessage(self, message):
        for user in Users:
            if user.number != self.userNumber:
                if user.online and not user.mute:
                    user.socketfd.sendall(message.encode('utf-8'))

    def sendPrivateMessage(self, receiver, message):
        for user in Users:
            if user.userName == receiver:
                if user.number == self.userNumber:
                    return 1
                if user.mute:
                    return 2
                user.socketfd.sendall(message.encode('utf-8'))
                return 3
        return 0


if __name__ == "__main__":
    try:
        print('Start server.')
        exeServer()
    except KeyboardInterrupt:
        print('\nExit server.')
        TCPsocket.close()

