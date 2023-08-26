import random

bancoDePalavras = ["teste", 'ab'] 
palavra = ["a","b"]
def iniciaJogo(palavra):
    palavraEscondida = []
    for letra in palavra:
        palavraEscondida.append("_")
    print(len(palavra))
    for i in range(len(palavra)):
        print(i)


iniciaJogo(list(bancoDePalavras[random.randint(0,len(bancoDePalavras))-1]))
server_clients = [["teste","giu","aleluia"],[],[],[],[]]
vezDoclient = 0

def verificaVezDoClient(client, id):
    print(server_clients[id][client])
    if(client == server_clients[id][client]):
        vezDoclient = server_clients[id][client]
        print("True")
    print("False")

