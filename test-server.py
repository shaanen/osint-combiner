import socket

# For testing the messages sent by other scripts

TCP_IP = 'localhost'
TCP_PORT = 5040
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print('Connection address:', addr)
while True:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break
    print("received data:", data)
conn.close()
