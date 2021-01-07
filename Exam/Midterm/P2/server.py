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
    def __init__(self, number):
        self.number = number
        self.online = True
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
                Users.append(User(userNumber))
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
        self.sendTCPmessage(f'Welcome, you are user{self.userNumber}.')
        response = []

        while True:
            commands = self.getTCPcommand().strip().split()
            response.clear()

            if len(commands) != 1:
                response.append('Usage: list-users/get-ip/exit')
            elif commands[0] == 'list-users':
                firstFlag = True
                for user in Users:
                    if user.online:
                        if firstFlag:
                            response.append(f'user{user.number}')
                            firstFlag = False
                        else:
                            response.append(f'\nuser{user.number}')
            elif commands[0] == 'get-ip':
                response.append(f'IP: {self.ip}:{self.port}')
            elif commands[0] == 'exit':
                for user in Users:
                    if user.number == self.userNumber:
                        user.online = False
                break
            else:
                response.append('Usage: list-users/get-ip/exit')

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


if __name__ == "__main__":
    try:
        print('Start server.')
        exeServer()
    except KeyboardInterrupt:
        print('\nExit server.')
        TCPsocket.close()

