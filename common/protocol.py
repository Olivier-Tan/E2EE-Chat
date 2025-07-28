from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import base64

def generate_rsa_keys():
    key = RSA.generate(2048)
    return key.export_key(), key.publickey().export_key()

def rsa_encrypt(pub_key_pem, data):
    pubkey = RSA.import_key(pub_key_pem)
    cipher = PKCS1_OAEP.new(pubkey)
    return base64.b64encode(cipher.encrypt(data))

def rsa_decrypt(priv_key_pem, data_b64):
    privkey = RSA.import_key(priv_key_pem)
    cipher = PKCS1_OAEP.new(privkey)
    return cipher.decrypt(base64.b64decode(data_b64))

def generate_aes_key():
    return get_random_bytes(16)

def aes_encrypt(aes_key, data):
    cipher = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext)

def aes_decrypt(aes_key, encrypted_b64):
    raw = base64.b64decode(encrypted_b64)
    nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
    cipher = AES.new(aes_key, AES.MODE_EAX, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()