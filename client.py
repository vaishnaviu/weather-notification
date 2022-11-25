import sys
import socket
import os
import json

def main():
    port = int(os.getenv('SERVER_PORT'))
    host = os.getenv('SERVER_HOST')
    subscriptionData  = { 'clientName': str(os.getenv('CLIENT_NAME')),
               'location': 'Santa Clara, CA',
               'topic': 'Daily'
            }
    ## convert to string
    stringData = json.dumps(subscriptionData)
    socketId = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socketId.connect((host,port))
    socketId.send(stringData.encode())
    while True:
        data = socketId.recv(2048).decode()
        print(data)

if __name__ == '__main__':
    main()