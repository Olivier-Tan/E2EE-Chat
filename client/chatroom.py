import sys
import os
import threading
import queue
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common.protocol import aes_encrypt, aes_decrypt

def open_chatroom(sock, aes_key, username, recipient, incoming_queue):
    print(f"Chatting with {recipient}. Type messages below.")

    def receiver():
        while True:
            try:
                msg = incoming_queue.get(timeout=0.5)
                print(f"\n[{msg['from']}] {aes_decrypt(aes_key, msg['message'])}")
                print("> ", end="", flush=True)
            except queue.Empty:
                continue

    threading.Thread(target=receiver, daemon=True).start()

    while True:
        try:
            msg = input("> ")
            if msg.lower() == "exit":
                break
            encrypted = aes_encrypt(aes_key, msg).decode()
            sock.send(json.dumps({
                "cmd": "message",
                "from": username,
                "to": recipient,
                "message": encrypted
            }).encode())
        except Exception as e:
            print("Error in chatroom:", e)
            break;