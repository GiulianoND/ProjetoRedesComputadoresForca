# Aplicação de Chat
#
# Criado por Giuliano Damasceno e Rodrigo Raupp
# Client side, v 1.0

import threading
from socket import *
import maskpass

serverIP = '127.0.0.1'
serverPort = 5005

clientSocket = socket(AF_INET, SOCK_STREAM)

logged_in = False
currentServer = ''

#função request solicita ao servidor alguma ação
def request(message, client):
	encodedMessage = message.encode()
	client.send(encodedMessage)

#função messageFromServer resgata a resposta à solicitação feita anteriormente
def messageFromServer(client):
    reply_message = client.recv(1024)
    decodedMessage = reply_message.decode()
    return decodedMessage

#função messageFromChat é chamada ao entrar em uma sala para receber as mensagens do chat (roda em thread)
def messageFromChat():
    while True:
        decodedMessage = messageFromServer(clientSocket)
        splitMessage = decodedMessage.split(' ')
        if splitMessage[0] == 'LEAVESERVER':
            break
        #   NEWMSG #SERVER1 USER BEGIN "textextextextext..."
        index = decodedMessage.find('BEGIN')
        chatMessage = splitMessage[2] + ': ' + decodedMessage[index + 6:]
        print(chatMessage)

#sendMessageToChat solicita ao servidor para enviar mensagem para a sala em que o cliente está (roda em thread)
def sendMessageToChat():
    while True:
        message = input('>')
        if message == '\leave':
            request('LEAVE ' + currentServer, clientSocket)
            break
        #   SENDMSG #SERVER1 USER BEGIN "textextextextext..."
        totalMessage = 'SENDMSG ' + currentServer + ' ' + user + ' ' + 'BEGIN ' + message
        request(totalMessage, clientSocket)

        
#tela inicial da aplicação: oferece opções de login, cadastro e fechar programa

print('Welcome!')
clientSocket.connect((serverIP, serverPort)) #conecta com o servidor

while True:
    op = int(input('1. Login to your account\n2. Create an user\n3. Quit\n'))
    if op == 1:
        user = input('User: ')
        password = maskpass.askpass(prompt = 'Password: ', mask = '*')
        message = 'LOGIN ' + user + ' ' + password
        encodedMessage = message.encode()

        clientSocket.send(encodedMessage) #envia a mensagem de login
        replyMessage = clientSocket.recv(1024) #espera a resposta
        decodedMessage = replyMessage.decode()
        if decodedMessage == 'AUTHEN 200 ' + user:
            print('Failed connecting with your user. Try again.')
        elif decodedMessage == 'AUTHEN 300 ' + user:
            print('User not found. Try again.')
        elif decodedMessage == ('AUTHEN 100 ' + user):
            print('User ' + user + ' online!')
            logged_in = True
            break
    elif op == 2:
        user = input('User: ')
        password = maskpass.askpass(prompt = 'Password: ', mask = '*')
        message = 'REGISTER ' + user + ' ' + password
        encodedMessage = message.encode()

        clientSocket.send(encodedMessage) #envia a mensagem de login
        replyMessage = clientSocket.recv(1024) #espera a resposta
        decodedMessage = replyMessage.decode()
        if decodedMessage == 'REGISTER 200 ' + user:
            print('User already registered.')
        elif decodedMessage == 'REGISTER 300 ' + user:
            print('Failed to register. Try again.')
        elif decodedMessage == ('REGISTER 100 ' + user):
            print('User ' + user + ' registered!')

    elif op == 3:
        message = 'FORCEQUIT'
        encodedMessage = message.encode()
        clientSocket.send(encodedMessage) #envia a mensagem
        replyMessage = clientSocket.recv(1024)
        print(replyMessage.decode())
        clientSocket.close()
        break
    else:
        print('Not available')

#caso o cliente logou com usuário e senha, é oferecida lista com salas para entrar e iniciar conversa
if logged_in:
    while True:
        message = 'SERVERSLIST'
        encodedMessage = message.encode()
        clientSocket.send(encodedMessage) #envia a mensagem
        reply_message = clientSocket.recv(1024)
        decodedMessage = reply_message.decode()
        print('Type prefered room: ')
        server_list = decodedMessage[5:].split(' ')
        server_list.remove('')
        for server in server_list:
            print(server)
        print('\\exit to close program')
        serverOption = input('>')

        if serverOption == '\exit': #é necessário fazer o fechamento da conexão TCP
            request('SHUTDOWN', clientSocket)
            clientSocket.close()
            break
        
        replyMessage = 'CONNECT ' + serverOption
        request(replyMessage, clientSocket)
        reply = messageFromServer(clientSocket)
        
        if reply == 'SERVERCONNECT 100 ' + serverOption:
            currentServer = serverOption
            print('Welcome to room ' + serverOption + '!  Type \\leave to leave.')
            
            receive_message = threading.Thread(target = messageFromChat)
            write_thread = threading.Thread(target = sendMessageToChat)
            
            receive_message.start()
            write_thread.start()

            receive_message.join()
            write_thread.join()
        currentServer = ''