import sys
import os
import socket
import json
import threading
from queue import Queue

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.protocol import (
    generate_rsa_keys,
    rsa_encrypt,
    rsa_decrypt,
    generate_aes_key,
    aes_encrypt,
    aes_decrypt
)

username = input("Username: ")
priv, pub = generate_rsa_keys()

sock = socket.socket()
sock.connect(("127.0.0.1", 12345))

sock.send(json.dumps({
    "cmd": "register",
    "username": username,
    "pubkey": pub.decode()
}).encode())

# Globals
aes_key = None
chat_partner = None
incoming_messages = Queue()
pending_invite = {}

def handle_server():
    global aes_key, chat_partner
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data.strip():
                continue
            msg = json.loads(data)

            if msg["cmd"] == "invite":
                print(f"Received invite from {msg['from']}")
                aes_key = rsa_decrypt(priv, msg["aes_key"].encode())
                chat_partner = msg["from"]
                print(f"Chat started with {chat_partner}")

            elif msg["cmd"] == "message":
                incoming_messages.put(msg)

            elif msg["cmd"] == "pubkey":
                pending_invite["pubkey"] = msg["pubkey"]

            elif msg["cmd"] == "error":
                print("Error:", msg["message"])

        except Exception as e:
            print("Connection error:", e)
            break

def show_messages():
    while True:
        try:
            msg = incoming_messages.get(timeout=0.5)
            decrypted = aes_decrypt(aes_key, msg["message"])
            print(f"\n[{msg['from']}] {decrypted}")
            print("> ", end="", flush=True)
        except:
            continue

threading.Thread(target=handle_server, daemon=True).start()

while True:
    choice = input("1. Invite\n2. Wait for invite\n3. Exit\n> ")

    if choice == "1":
        recipient = input("Invite who? ")
        aes_key = generate_aes_key()
        pending_invite.clear()
        pending_invite["username"] = recipient
        pending_invite["pubkey"] = None

        sock.send(json.dumps({
            "cmd": "get_pubkey",
            "username": recipient
        }).encode())

        while pending_invite["pubkey"] is None:
            continue

        pubkey = pending_invite["pubkey"].encode()
        encrypted_aes_key = rsa_encrypt(pubkey, aes_key)

        chat_partner = recipient
        print(f"Chat started with {chat_partner}")

        sock.send(json.dumps({
            "cmd": "invite",
            "from": username,
            "to": recipient,
            "aes_key": encrypted_aes_key.decode()
        }).encode())
        break

    elif choice == "2":
        print("Waiting for someone to invite you...")
        while aes_key is None:
            continue
        break

    elif choice == "3":
        print("Exiting.")
        exit()

threading.Thread(target=show_messages, daemon=True).start()

while True:
    msg = input("> ")
    if msg.lower() == "exit":
        break
    encrypted = aes_encrypt(aes_key, msg).decode()
    sock.send(json.dumps({
        "cmd": "message",
        "from": username,
        "to": chat_partner,
        "message": encrypted
    }).encode())