#!/usr/bin/env python3
import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('serverIP')
parser.add_argument('serverPort')
args = parser.parse_args()

serverIP = args.serverIP
serverPort = int(args.serverPort)
serverAddress = (serverIP, serverPort)

UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

bufferSize = 1024

def exeClient():
    while True:
        command = input('% ').strip()
        commands = command.split()
        if commands:
            UDPsocket.sendto(command.encode('utf-8'), serverAddress)

            if commands[0] == 'send-file':
                if len(commands) == 1:
                    printUDPresponse()
                
                fileNames = []
                for fileName in commands[1:]:
                    fileNames.append(fileName)
                for fileName in fileNames:
                    send_file(fileName)
            else:
                printUDPresponse()
            
            if command == 'exit':
                break
    UDPsocket.close()
                
def send_file(fileName):
    UDPsocket.sendto(f'{fileName}'.encode('utf-8'), serverAddress)

    try:
        sendFile = open(fileName, 'rb')
    except OSError as e:
        print('Open file error: ', e)
        return
    
    sendList = []
    part = sendFile.read(bufferSize)
    while part:
        UDPsocket.sendto(part, serverAddress)
        sendList.append(part)
        part = sendFile.read(bufferSize)
    sendFile.close()
    # print('Length for the lastest part: ', len(sendList[-1]))
    if len(sendList[-1]) == bufferSize:
        UDPsocket.sendto(b'', serverAddress)
        sendList.append(b'')

def printUDPresponse():
    response = []
    while True:
        part, _ = UDPsocket.recvfrom(1024)
        response.append(part.decode('utf-8'))
        if len(part) < 1024:
            break
    UDPresponse = ''.join(response)
    print(UDPresponse)


if __name__ == "__main__":
    try:
        exeClient()
    except (KeyboardInterrupt, OSError, Exception) as e:
        UDPsocket.sendto('exit'.encode('utf-8'), serverAddress)
        UDPsocket.close()
        print(e)







