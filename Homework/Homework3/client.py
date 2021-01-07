#!/usr/bin/env python3
import socket
import argparse
import datetime
import threading
import select
import sys

parser = argparse.ArgumentParser()
parser.add_argument('serverIP')
parser.add_argument('serverPort')
args = parser.parse_args()

serverIP = args.serverIP
serverPort = int(args.serverPort)
serverAddress = (serverIP, serverPort)

TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class ChatroomServer():
    def __init__(self, socketfd, address, chatroomName):
        self.socketfd = socketfd
        self.address = address
        self.chatroomName = chatroomName
        self.close = True
        self.record = []

    def addChatRecord(self, message):
        self.record.append(message)
        if len(self.record) > 3:
            del self.record[0]

ChatroomServers = []

class ChatroomClient():
    def __init__(self, socketfd, address, userName):
        self.socketfd = socketfd
        self.address = address
        self.userName = userName

class ChatroomServerThread(threading.Thread):
    def __init__(self, serverStatus):
        threading.Thread.__init__(self)
        self.serverStatus = serverStatus
        self.clients = []

    def run(self):
        # print('Run ChatroomServer Thread...')
        self.serverStatus.socketfd.listen(10)
        self.serverStatus.close = False
        inputs = []
        inputs.append(self.serverStatus.socketfd.fileno())
        while True:
            if self.serverStatus.close:
                for chatroomClient in self.clients:
                    if chatroomClient.userName != self.serverStatus.chatroomName:
                        # send message to inform other clients that chatroom owner is leave
                        chatroomClient.socketfd.sendall('leave'.encode('utf-8'))
                break

            readable, _, err = select.select(inputs, [], [], 0)
            # print('select')
            for sockfd in readable:
                if sockfd is self.serverStatus.socketfd.fileno():
                    client, address = self.serverStatus.socketfd.accept()
                    thread = ChatroomClientThread(client, address, self.clients, self.serverStatus)
                    thread.start()
        self.serverStatus.socketfd.close()
        # print('Leave Server Thread.')


class ChatroomClientThread(threading.Thread):
    def __init__(self, socketfd, address, clients, serverStatus):
        threading.Thread.__init__(self)
        self.userName = None
        self.socketfd = socketfd
        self.address = address
        self.clients = clients
        self.serverStatus = serverStatus

    def run(self):
        # print('Run ChatroomClient Thread...')
        # get userName
        self.userName = str(self.socketfd.recv(1024), 'utf-8')
        # add client
        self.clients.append(ChatroomClient(self.socketfd, self.address, self.userName))
        # message for new attender
        if self.userName != self.serverStatus.chatroomName:
            self.broadcastMessage(f'sys [{datetime.datetime.now().strftime("%H:%M")}]: {self.userName} join us.')

        # send welcome message
        self.socketfd.sendall('*****************************\n** Welcome to the chatroom **\n*****************************'.encode('utf-8'))

        firstFlag = True
        for chatRecord in self.serverStatus.record:
            if firstFlag:
                self.socketfd.sendall('\n'.encode('utf-8'))
                firstFlag = False
            self.socketfd.sendall(chatRecord.encode('utf-8'))

        while True:
            if self.serverStatus.close:
                break
            command = self.getChatroomCommand()
            commands = command.strip().split()
            if commands:
                if command == 'detach':
                    if self.userName == self.serverStatus.chatroomName:
                        self.socketfd.sendall('detach'.encode('utf-8'))
                        break
                    else:
                        message = f'{self.userName} [{datetime.datetime.now().strftime("%H:%M")}]: {command}'
                        self.broadcastMessage(message)
                        self.serverStatus.addChatRecord(f'{message}\n')
                elif command =='leave-chatroom':
                    if self.userName == self.serverStatus.chatroomName:
                        # leave and close the chatroom
                        self.socketfd.sendall('leave-chatroom'.encode('utf-8'))
                        self.serverStatus.close = True
                        TCPsocket.sendall('close-chatroom'.encode('utf-8'))
                        break
                    else:
                        # leave the chatroom
                        self.socketfd.sendall('leave-chatroom'.encode('utf-8'))
                        # broadcast message for dropout
                        self.broadcastMessage(f'sys [{datetime.datetime.now().strftime("%H:%M")}]: {self.userName} leave us.')
                        break
                else:
                    message = f'{self.userName} [{datetime.datetime.now().strftime("%H:%M")}]: {command}'
                    self.broadcastMessage(message)
                    self.serverStatus.addChatRecord(f'{message}\n')
        # remove leave client
        for chatroomClient in self.clients:
            if chatroomClient.socketfd == self.socketfd:
                self.clients.remove(chatroomClient)
                break
        self.socketfd.close()
        # print('Leave Client Thread.')

    def getChatroomCommand(self):
        command = []
        while True:
            part = self.socketfd.recv(1024)
            command.append(str(part, 'utf-8'))
            if len(part) < 1024:
                break
        commands = ''.join(command)
        return commands

    def broadcastMessage(self, message):
        for chatroomclient in self.clients:
            if chatroomclient.userName != self.userName:
                chatroomclient.socketfd.sendall(message.encode('utf-8'))


joinChatroomLeave = []

def exe_joinChatroom(userName, address):
    # connect socket
    chatroomSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chatroomSocket.connect(address)

    # send userName
    chatroomSocket.sendall(userName.encode('utf-8'))

    # input handler
    joinChatroomLeave.clear()
    receiveThread = joinChatroomReceiveThread(chatroomSocket)
    receiveThread.start()

    while True:
        if len(joinChatroomLeave):
            break
        # command = input('')
        # commands = command.strip().split()

        command = ''
        commands = None
        readable = select.select([sys.stdin], [], [], 0)[0]
        if readable:
            command = sys.stdin.readline().strip()
            commands = command.split()

        if commands:
            chatroomSocket.sendall(command.encode('utf-8'))

    receiveThread.join()
    chatroomSocket.close()


class joinChatroomReceiveThread(threading.Thread):
    def __init__(self, socketfd):
        threading.Thread.__init__(self)
        self.socketfd = socketfd

    def run(self):
        # print('Run Chatroom Receive Thread...')
        # chatroom receive handler
        while True:
            response = getTCPresponse(self.socketfd)
            chatroomResponse = response.strip().split()
            if chatroomResponse:
                # print('response: ', response)
                if response == 'detach' or response == 'leave-chatroom':
                    # chatroom owner detach or client leave-chatroom
                    joinChatroomLeave.append(1)
                    break
                elif response == 'leave':
                    # chatroom owner leave-chatroom
                    print(f'sys [{datetime.datetime.now().strftime("%H:%M")}]: the chatroom is close.')
                    joinChatroomLeave.append(1)
                    break
                else:
                    print(response)
        # print('Leave Receive Thread.')


def getTCPresponse(sock):
    response = []
    while True:
        part = sock.recv(1024)
        response.append(str(part, 'utf-8'))
        if len(part) < 1024:
            break
    TCPresponse = ''.join(response)
    return TCPresponse


def exeClient():
    TCPConnect = False
    randomNumber = -1
    chatroomPort = -1
    chatroomCreate = False
    currentUserName = None
    print('********************************\n** Welcome to the BBS server. **\n********************************')

    while True:
        command = input('% ')
        commands = command.strip().split()
        if commands:
            # register: UDP
            if commands[0] == 'register':
                UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                UDPsocket.sendto(command.encode('utf-8'), serverAddress)
                response, _ = UDPsocket.recvfrom(1024)
                UDPresponse = response.decode('utf-8')
                print(UDPresponse)
                UDPsocket.close()
            # whoami: UDP
            elif commands[0] == 'whoami':
                UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sendMessage = str(command + ' ' + str(randomNumber))

                UDPsocket.sendto(sendMessage.encode('utf-8'), serverAddress)
                response, _ = UDPsocket.recvfrom(1024)
                UDPresponse = response.decode('utf-8')
                print(UDPresponse)
                UDPsocket.close()
            # list-chatroom: UDP
            elif commands[0] == 'list-chatroom':
                UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sendMessage = str(command + ' ' + str(randomNumber))
                UDPsocket.sendto(sendMessage.encode('utf-8'), serverAddress)

                response = []
                while True:
                    part, _ = UDPsocket.recvfrom(1024)
                    response.append(str(part, 'utf-8'))
                    if len(part) < 1024:
                        break
                UDPresponse = ''.join(response)
                print(UDPresponse)
                UDPsocket.close()
            # attach
            elif commands[0] == 'attach':
                if randomNumber == -1:
                    print('Please login first.')
                    continue

                existFlag = False
                for server in ChatroomServers:
                    if server.chatroomName == currentUserName:
                        existFlag = True
                        if server.close:
                            print('Please restart-chatroom first.\n')
                        else:
                            # start running chatroom and receive the lastest three messages
                            exe_joinChatroom(currentUserName, server.address)
                            print('Welcome back to BBS.')

                if not existFlag:
                    print('Please create-chatroom first.')

            else:
                if TCPConnect == False :
                    # TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    TCPsocket.connect(serverAddress)
                    TCPConnect = True

                TCPsocket.sendall(command.encode('utf-8'))
                response = getTCPresponse(TCPsocket)
                TCPresponse = response.strip().split()

                if TCPresponse[0] == 'Welcome,':
                    randomNumber = TCPresponse[2]
                    currentUserName = TCPresponse[1][0:len(TCPresponse[1])-1]
                    # check randomNumber
                    # print('randomNumber: ', randomNumber)
                    print(TCPresponse[0], TCPresponse[1])
                elif TCPresponse[0] == 'Bye,':
                    randomNumber = -1
                    currentUserName = None
                    print(response)
                elif TCPresponse[0] == 'exit':
                    TCPsocket.close()
                    break
                # create-chatroom or restart-chatroom success
                elif TCPresponse[0] == 'start':
                    print(' '.join(TCPresponse[0:4]))

                    socketfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    address = (TCPresponse[4], int(TCPresponse[5]))
                    socketfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    socketfd.bind(address)
                    chatroomServer = ChatroomServer(socketfd, address, currentUserName)

                    for server in ChatroomServers:
                        if server.chatroomName == currentUserName:
                            chatroomServer.record = server.record
                            ChatroomServers.remove(server)
                            break

                    ChatroomServers.append(chatroomServer)

                    # exeChatroomServer
                    chatroomServerThread = ChatroomServerThread(chatroomServer)
                    chatroomServerThread.start()

                    while True:
                        if not chatroomServer.close:
                            exe_joinChatroom(currentUserName, chatroomServer.address)
                            break
                    # leave chatroom: send close message to bbs server
                    print('Welcome back to BBS.')

                # join-chatroom success
                elif TCPresponse[0] == 'join':
                    address = (TCPresponse[1], int(TCPresponse[2]))
                    # join other's chatroom
                    exe_joinChatroom(currentUserName, address)
                    print('Welcome back to BBS.')
                else:
                    print(response)



if __name__ == '__main__':
    try:
        exeClient()
    except (KeyboardInterrupt, OSError, Exception) as e:
        TCPsocket.send('exit'.encode('utf-8'))
        print(e)


