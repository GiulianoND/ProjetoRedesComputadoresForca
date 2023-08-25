def iniciaJogo(palavra):
    palavraEscondida = ""
    for letra in palavra:
        palavraEscondida = palavraEscondida + "_ "
    
    print(palavraEscondida)



server_clients = [["teste","giu","aleluia"],[],[],[],[]]
vezDoclient = 0

def verificaVezDoClient(client, id):
    print(server_clients[id][client])
    if(client == server_clients[id][client]):
        vezDoclient = server_clients[id][client]
        print("True")
    print("False")

verificaVezDoClient("giu", 0)