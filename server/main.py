import socket, threading, json

users = {}  # {username: {"pubkey": ..., "conn": ..., "addr": ...}}

def client_thread(conn, addr):
    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break
            handle_message(json.loads(data), conn)
    finally:
        conn.close()

def handle_message(msg, conn):
    cmd = msg['cmd']
    if cmd == "register":
        users[msg['username']] = {"pubkey": msg['pubkey'], "conn": conn}
    elif cmd == "invite":
        recipient = users.get(msg['to'])
        if recipient:
            recipient['conn'].send(json.dumps({
                "cmd": "invite",
                "from": msg['from'],
                "aes_key": msg['aes_key']
            }).encode())
    elif cmd == "message":
        recipient = users.get(msg['to'])
        if recipient:
            recipient['conn'].send(json.dumps({
                "cmd": "message",
                "from": msg['from'],
                "message": msg['message']
            }).encode())
    elif cmd == "get_pubkey":
        target = msg["username"]
        if target in users:
            conn.send(json.dumps({
                "cmd": "pubkey",
                "username": target,
                "pubkey": users[target]["pubkey"]
            }).encode())
        else:
            conn.send(json.dumps({
                "cmd": "error",
                "message": "User not found"
            }).encode())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 12345))
server.listen(5)
print("Server running on port 12345")

while True:
    conn, addr = server.accept()
    threading.Thread(target=client_thread, args=(conn, addr)).start()