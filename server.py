import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 12345))
server.listen(5)
while True:
    client_socket, client_address = server.accept()
    print('Connection from: ', client_address)

    data = bytes('','utf-8')
    while len(data)<100000:
        temp = client_socket.recv(1024)
        data = data + temp
        if temp == b'':
            break


    print('Received: ', data)
    # client_socket.send(data.upper())
    client_socket.close()
    print('Client disconnected')