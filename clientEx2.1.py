import socket


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 12345))
s.send(b'Yahel Jacoby 208384420 Yoav Tamir 316554724')
data = s.recv(100)
print("Server sent: ", data)
s.close()