# -*- coding=utf-8 -*-
import os
import sqlite3

import keyring
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

# for mac
my_pass = keyring.get_password('Chrome Safe Storage', 'Chrome')
my_pass = my_pass.encode('utf8')
iterations = 1003
cookie_file = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Cookies')

# for linux
# my_pass = 'peanuts'.encode('utf8')
# iterations = 1
# cookie_file = cookie_file or os.path.expanduser('~/.config/chromium/Default/Cookies')

salt = b'saltysalt'
length = 16
iv = b' ' * length


def expand_str(token):
    token_len = len(token)


expand_len = (token_len // length + 1) * length - token_len
return token.encode('ascii') + b'\x0c' * expand_len


def aes_encrypt(token):
    key = PBKDF2(my_pass, salt, length, iterations)


cipher = AES.new(key, AES.MODE_CBC, IV=iv)
enc_token = cipher.encrypt(token)
return b'v10' + enc_token


def aes_decrypt(token):
    key = PBKDF2(my_pass, salt, length, iterations)


cipher = AES.new(key, AES.MODE_CBC, IV=iv)
dec_token = cipher.decrypt(token)
return dec_token


def query_cookies():
    with sqlite3.connect(cookie_file) as conn:
        result = conn.execute(
            "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key = 'walis127.eleme'").fetchall()
    return result


def write_cookies(enc_token):
    with sqlite3.connect(cookie_file) as conn:
        b = sqlite3.Binary(enc_token)


sql = """update cookies set encrypted_value = ? where name = 'remember_token'"""
conn.execute(sql, (b,))


def change_user(token):
    write_cookies(ase_encrypt(expand_str(token)))
