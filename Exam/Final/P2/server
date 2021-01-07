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

clientName = ['A', 'B', 'C', 'D']

ACCOUNT1 = 0
ACCOUNT2 = 0

def exeServer():
    userNumber = -1
    while True:
        readable, _, _ = select.select(inputs, [], [])

        for sockfd in readable:
            if sockfd is TCPsocket.fileno():
                client, address = TCPsocket.accept()
                userNumber += 1
                if userNumber > 4:
                    userNumber = 0
                print(f'New connection from {address[0]}:{address[1]} {clientName[userNumber]}.')
                thread = TCPClientThread(client, address[0], address[1], clientName[userNumber])
                thread.start()

class TCPClientThread(threading.Thread):
    def __init__(self, socketfd, ip, port, userName):
        threading.Thread.__init__(self)
        self.socketfd = socketfd
        self.ip = ip
        self.port = port
        self.userName = userName

    def run(self):
        global ACCOUNT1
        global ACCOUNT2
        self.sendTCPmessage(f'**************************\n* Welcome to the TCP server. *\n**************************')

        while True:
            commands = self.getTCPcommand().strip().split()
            
            if commands[0] == 'show-accounts':
                self.sendTCPmessage(f'ACCOUNT1: {ACCOUNT1}\nACCOUNT2: {ACCOUNT2}')
            elif commands[0] == 'deposit':
                if len(commands) != 3:
                    self.sendTCPmessage('Usage: deposit <account> <money>')
                else:
                    try:
                        money = int(commands[2])
                        if money <= 0:
                            self.sendTCPmessage('Deposit a non-positive number into accounts.')
                        else:
                            if commands[1] == 'ACCOUNT1':
                                ACCOUNT1 += money
                                self.sendTCPmessage(f'Successfully deposits {money} into {commands[1]}')
                            elif commands[1] == 'ACCOUNT2':
                                ACCOUNT2 += money
                                self.sendTCPmessage(f'Successfully deposits {money} into {commands[1]}')
                            else:
                                self.sendTCPmessage(f'{commands[1]} does not exist.')
                    except ValueError:
                        self.sendTCPmessage('<money> should be an integer.')
            elif commands[0] == 'withdraw':
                if len(commands) != 3:
                    self.sendTCPmessage('Usage: withdraw <account> <money>')
                else:
                    try:
                        money = int(commands[2])
                        if money <= 0:
                            self.sendTCPmessage('Withdraw a non-positive number into accounts.')
                        else:
                            if commands[1] == 'ACCOUNT1':
                                if ACCOUNT1 < money:
                                    self.sendTCPmessage('Withdraw excess money from accounts.')
                                else:
                                    ACCOUNT1 -= money
                                    self.sendTCPmessage(f'Successfully deposits {money} into {commands[1]}')
                            elif commands[1] == 'ACCOUNT2':
                                if ACCOUNT2 < money:
                                    self.sendTCPmessage('Withdraw excess money from accounts.')
                                else:
                                    ACCOUNT2 -= money
                                    self.sendTCPmessage(f'Successfully deposits {money} into {commands[1]}')
                            else:
                                self.sendTCPmessage(f'{commands[1]} does not exist.')
                    except ValueError:
                        self.sendTCPmessage('<money> should be an integer.')
                    
            elif commands[0] == 'exit':
                self.sendTCPmessage(f'Bye, {self.userName}.')
                break
            else:
                self.sendTCPmessage('Unsupport command')

        print(f'{self.userName} {self.ip}:{self.port} disconnected.')
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

