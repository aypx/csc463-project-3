'''
Script for server
@author: hao
'''

import config
import protocol
import os
from socket import *
class server:

    # Constructor: load the server information from config file
    def __init__(self):
        self.port, self.path=config.config().readServerConfig()

    # Get the file names from shared directory
    def getFileList(self):
        return os.listdir(self.path)
    
    # Function to send file list to client       
    def listFile(self, serverSocket):
        serverSocket.send(protocol.prepareFileList(protocol.HEAD_LIST, self.getFileList()))

    # Function to send a file to client       
    def sendFile(self,serverSocket,fileName):
        f = open(fileName,'rb')
        l = f.read(1024) # each time we only send 1024 bytes of data
        while (l):
            serverSocket.send(l)
            l = f.read(1024)

    # Function to receive file from client
    def receiveFile(self, connectionSocket, msg):
        fileName, fileSize = msg.split('\n')
        fileSize = int(fileSize)

        filePath = self.path + "/" + fileName

        # Open a new file and save uploaded data
        with open(filePath, 'wb') as f:
            remaining = fileSize

            # Receive file in 1024 byte chunks
            while remaining > 0:
                data = connectionSocket.recv(min(1024, remaining))

                if not data:
                    break

                f.write(data)
                remaining -= len(data)

    # Main function of server, start the file sharing service
    def start(self):
        serverPort=self.port
        serverSocket=socket(AF_INET,SOCK_STREAM)
        serverSocket.bind(('',serverPort))
        serverSocket.listen(20)
        print('The server is ready to receive')
        while True:
            connectionSocket, addr = serverSocket.accept()
            dataRec = connectionSocket.recv(1024)

            # Read full upload message
            if dataRec[:3] == protocol.HEAD_UPLOAD.encode():
                while len(dataRec) < 1024:
                    dataRec += connectionSocket.recv(1024 - len(dataRec))

                dataRec = dataRec.rstrip(b'\0')

            # Decode client message
            header, msg = protocol.decodeMsg(dataRec.decode())
            # Main logic of the program, send different content to client according to client's requests
            if(header==protocol.HEAD_REQUEST):
                self.listFile(connectionSocket)
            elif(header==protocol.HEAD_DOWNLOAD):
                self.sendFile(connectionSocket, self.path+"/"+msg)
            # Receive the file uploaded by client
            elif(header==protocol.HEAD_UPLOAD):
                self.receiveFile(connectionSocket, msg)
            else:
                connectionSocket.send(protocol.prepareMsg(protocol.HEAD_ERROR, "Invalid Message"))
            connectionSocket.close()

def main():
    s=server()
    s.start()

if __name__ == "__main__":
    main()
