#!/usr/bin/env python3
import socket
import argparse
import threading
import select
import sys

parser = argparse.ArgumentParser()
parser.add_argument('serverIP')
parser.add_argument('serverPort')
args = parser.parse_args()

if not args.serverPort.isdecimal():
    print('Port should be an interger.')
    exit()

serverIP = args.serverIP
serverPort = int(args.serverPort)
serverAddress = (serverIP, serverPort)

TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
TCPsocket.connect(serverAddress)

leaveFlag = False

def exeClient():
    # Welcome message
    response = getTCPresponse()
    print(response)

    global leaveFlag
    # thread for receive
    thread = receiveThread()
    thread.start()

    while True:
        command = None
        commands = None
        readable = select.select([sys.stdin], [] ,[], 0)[0]
        if readable:
            command = sys.stdin.readline().strip()
            commands = command.split()
        if commands:
            TCPsocket.sendall(command.encode('utf-8'))
            if commands[0] == 'exit':
                leaveFlag = True
                break
    TCPsocket.close()

class receiveThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global leaveFlag
        while True:
            response = getTCPresponse()
            TCPresponse = response.strip().split()
            if TCPresponse:
                print(response)
            if leaveFlag:
                break


def getTCPresponse():
    response = []
    while True:
        part = TCPsocket.recv(1024)
        response.append(str(part, 'utf-8'))
        if len(part) < 1024:
            break
    TCPresponse = ''.join(response)
    return TCPresponse


if __name__ == "__main__":
    try:
        exeClient()
    except (KeyboardInterrupt, OSError, Exception) as e:
        TCPsocket.sendall('exit'.encode('utf-8'))
        TCPsocket.close()
        print(e)







