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

sequenceNumber = 0
bufferSize = 1024
endOfFile = 'END OF FILE.'

class package():
    def __init__(self, data):
        global sequenceNumber
        self.sequenceNumber = sequenceNumber
        sequenceNumber += 1
        self.length = len(data)
        self.payload = data

def exeServer():
    while True:
        raw_data, clientAddress = UDPsocket.recvfrom(1024)
        command = raw_data.decode('utf-8')
        print(f'UDPconnection: {address[0]}:{address[1]}')
        print('Command: ', command)
        commands = command.strip().split()

        response = []
        if commands:
            # get file list
            if commands[0] == 'get-file-list':
                response.append('Files:')
                for entry in os.scandir('.'):
                    if entry.is_file():
                        response.append(entry.name)
                message = ' '.join(response)
                sendUDPresponse(message, clientAddress)
            # get file (multiple files)
            elif commands[0] == 'get-file':
                if len(commands) == 1:
                    sendUDPresponse('Usage: get-file {file-name1} {file-name2} {file-name3}...', clientAddress)
                fileNames = []
                for fileName in commands[1:]:
                    fileNames.append(fileName)
                print('Files: ', fileNames)
                for fileName in fileNames:
                    send_file(fileName, clientAddress)
            elif commands[0] == 'exit':
                sendUDPresponse('Bye.', clientAddress)
            else:
                sendUDPresponse('Unsupport command.', clientAddress)

def sendUDPresponse(message, address):
    UDPsocket.sendto(message.encode('utf-8'), address)


def send_file(fileName, clientAddress):
    UDPsocket.sendto(f'{fileName}'.encode('utf-8'), clientAddress)

    try:
        sendFile = open(fileName, 'rb')
    except OSError as e:
        print('Open file error: ', e)
        return
    sendList = []
    part = sendFile.read(bufferSize)
    while part:
        UDPsocket.sendto(part, clientAddress)
        sendList.append(part)
        part = sendFile.read(bufferSize)
    sendFile.close()
    print('Length for the lastest part: ', len(sendList[-1]))
    if len(sendList[-1]) == bufferSize:
        UDPsocket.sendto(b'', clientAddress)
        sendList.append(b'')

    # UDPsocket.sendto('END OF FILE.'.encode('utf-8'), clientAddress)
    



if __name__ == "__main__":
    print('Turn on the Server.')
    try:
        exeServer()
    except KeyboardInterrupt:
        UDPsocket.close()
        print('Exit server.')









