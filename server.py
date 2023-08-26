# Aplicação de Chat
#
# Criado por Giuliano Damasceno e Rodrigo Raupp
# Server side, v 1.0

import json
import threading
import random
from socket import *

#alocando servidor
serverIP = '127.0.0.1'
serverPort = 5005
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen()

#inicializando variáveis para localizar o usuário no chat
clients = []
users = []
server_names = ["#Iniciar"]
server_clients = [[]]
donoDaRodada = 0
interacoes = 0
bancoDePalavras = ["teste", 'aloha']
palavra = []
palavraEscondida = []
sessãoDeJogo = 0
letrasEscolhidas = []
print("Inicializando servidor... Pronto!")


#Inicia jogo
def iniciaJogo(palavra):
    global palavraEscondida
    for letra in palavra:
        palavraEscondida.append("_")

#função reply responde às mensagens de protocolo trocadas com os clientes
def reply(message, client):
	encodedMessage = message.encode()
	client.send(encodedMessage)

#verifica vez do cliente
def isVezDoClient(client, id):
	global donoDaRodada
	global interacoes
	if(client == server_clients[id][donoDaRodada]):
		interacoes = interacoes+1
		donoDaRodada =  interacoes % len(server_clients[id])
		return True
	return False

def iniciaJogo(palavraSorteada):
    global palavraEscondida
    global palavra
    palavra = palavraSorteada
    for letra in palavra:
        palavraEscondida.append("_")
    
#servidor recebe mensagem de um usuário e repassa para os usuários que estão nessa sala
def transmission(message, server, user, client):
	global palavraEscondida
	global palavra
	global letrasEscolhidas
	id = server_names.index(server)
	if(isVezDoClient(client, id) == False):
		reply('NEWMSG '+ server + ' ' + user + ' BEGIN ' + "Não é a sua vez", client)
	else:
		flagDePontos = 0
		vitoria = 1
		for i in range(len(palavra)):
			if(palavra[i] == message and (palavra[i] != palavraEscondida[i])):
				palavraEscondida[i] = palavra[i]
				flagDePontos = flagDePontos+1
		
		for i in range(len(palavra)):
			if(palavraEscondida[i] != palavra[i]):
				vitoria = 0
				break
		if(vitoria == 1):
			reply('NEWMSG '+ server + ' ' + user + ' BEGIN ' + 'Jogo finalizado '.join(palavraEscondida), x)

		letrasEscolhidas.append(message)
		



		for x in server_clients[id]:
			#client.send(message)
			#	NEWMSG #SERVER1 USER BEGIN "textextextextext..."
				reply('NEWMSG '+ server + ' ' + user + ' BEGIN ' + ' '.join(palavraEscondida), x)

#tratamento das mensagens enviadas pelo cliente
def clientController(client):
	global sessãoDeJogo
	while True:
		message = client.recv(4000)
		decoded_message = message.decode()
		info = decoded_message.split(' ') #		CONNECT #games   info = ["CONNECT", "#games"]
		if(sessãoDeJogo == 0):
			palavra = bancoDePalavras[random.randint(0,len(bancoDePalavras))-1]
			sessãoDeJogo = 1
			iniciaJogo(list(palavra))
		if (info[0] == 'FORCEQUIT') or (info[0] == 'SHUTDOWN'):
			reply('GOODBYE', client)
			#clients.remove(client)
			if info[0] == 'SHUTDOWN':
				clients.remove(client)
				users.remove(user)
			client.close()
			break

		elif info[0] == 'LOGIN':  # 			LOGIN rodrigolaforet abcd		info = ["LOGIN", "rodrigolaforet", "abcd"]
			user = info[1]
			password = info[2]
			f = open('users.json')
			userInformations = json.load(f)
			if(userInformations.get(user) != None and userInformations[user] == password):
				reply('AUTHEN 100 ' + user, client)
				clients.append(client)
				users.append(user)
			elif (userInformations.get(user) != None and userInformations[user] != password):
				reply('AUTHEN 200 ' + user, client)
			else:
				reply('AUTHEN 300 ' + user, client)
			f.close()

		elif info[0] == 'REGISTER':  # 			REGISTER rodrigolaforet abcd		info = ["REGISTER", "rodrigolaforet", "abcd"]
			user = info[1]
			password = info[2]
			
			try: 
				with open('users.json', 'r') as f:
					userInformations = json.load(f)
				if(userInformations.get(user) == None):
					userInformations[user] = password
					with open('users.json', 'w') as f:
						json.dump(userInformations, f)
					reply('REGISTER 100 ' + user, client)
				else:
					reply('REGISTER 200 ' + user, client)
				
			except Exception as e:
				reply('REGISTER 300 ' + user, client)

		elif info[0] == 'SERVERSLIST':
			answer = 'LOBBY '
			for server in server_names:
				answer = answer + server + ' '
			reply(answer, client)
		
		elif info[0] == 'CONNECT':
			if info[1] in server_names:
				server_clients[server_names.index(info[1])].append(client)
				#currentServer = info[1]
				reply('SERVERCONNECT 100 ' + info[1], client)
			else:
				reply('SERVERCONNECT 300 ' + info[1], client) 
		
		elif info[0] == 'SENDMSG':
			#	SENDMSG #SERVER1 USER BEGIN "textextextextext..."
			server_name = info[1]
			userMessage = info[2]
			position = decoded_message.find("BEGIN ")
			transmission(decoded_message[position+6 :], server_name, userMessage, client)
		
		elif info[0] == 'LEAVE':
			server_clients[server_names.index(info[1])].remove(client)
			reply('LEAVESERVER', client)

		else:
			reply('ERR 999', client)


def welcome():
	while True:
		connectionSocket, addr = serverSocket.accept()

		thread = threading.Thread(target = clientController, args = (connectionSocket,))
		thread.start()

welcome()
