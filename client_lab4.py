import socket

HOST = '127.0.0.1'
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    with open('test.txt', 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            s.sendall(data)