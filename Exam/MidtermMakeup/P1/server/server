#!/usr/bin/env python3
import socket
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

if not args.port.isdecimal():
    print('port should be an interger')
    exit()

host = 'localhost'
port = int(args.port)
address = (host, port)

UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPsocket.bind(address)

def exeServer():
    while True:
        raw_data, clientAddress = UDPsocket.recvfrom(1024)
        command = raw_data.decode('utf-8')
        # print(f'UDPconnection: {address[0]}:{address[1]}')
        # print('Command: ', command)
        commands = command.strip().split()

        response = []
        if commands:
            # receive file
            if commands[0] == 'send-file':
                if len(commands) == 1:
                    sendUDPresponse('No file to send.', clientAddress)
                
                fileNumber = len(commands) - 1
                while fileNumber:
                    raw_name, _ = UDPsocket.recvfrom(1024)
                    fileName = raw_name.decode('utf-8')
                    receive_file(fileName)
                    fileNumber -= 1
                
            elif commands[0] == 'exit':
                sendUDPresponse('Bye.', clientAddress)
            else:
                sendUDPresponse('Unsupport command.', clientAddress)

def sendUDPresponse(message, address):
    UDPsocket.sendto(message.encode('utf-8'), address)


def receive_file(fileName):
    try:
        receiveFile = open(fileName, 'wb')
    except OSError as e:
        print('Open file error: ', e)
        return
    
    # receiveList = []
    while True:
        part, _ = UDPsocket.recvfrom(1024)
        receiveFile.write(part)
        # receiveList.append(part)
        if len(part) < 1024:
            break
    receiveFile.close()



if __name__ == "__main__":
    print('Turn on the Server.')
    try:
        exeServer()
    except KeyboardInterrupt:
        UDPsocket.close()
        print('\nExit server.')









