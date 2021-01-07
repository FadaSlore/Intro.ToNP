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

def exeClient():
    while True:
        command = input('% ').strip()
        commands = command.split()
        if commands:
            UDPsocket.sendto(command.encode('utf-8'), serverAddress)

            if commands[0] == 'get-file':
                if len(commands) == 1:
                    printUDPresponse()
                
                fileNumber = len(commands) - 1
                while fileNumber:
                    raw_name, _ = UDPsocket.recvfrom(1024)
                    fileName = raw_name.decode('utf-8')
                    receive_file(fileName)
                    fileNumber -= 1
            else:
                printUDPresponse()
            
            if command == 'exit':
                break
    UDPsocket.close()
                
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







