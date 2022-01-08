import os
import vlc
import time
from cryptography.fernet import Fernet

KEY = Fernet.generate_key()

def encryptFile(filePath, destPath=None, key=None):
    if not key:
        key = KEY
    fernet = Fernet(key)

    with open(filePath, 'rb') as binaryFile:
        original = binaryFile.read()

    encrypted = fernet.encrypt(original)
    if destPath:
        filePath = os.path.join(destPath, os.path.basename(filePath))
    with open(filePath, 'wb') as encryptedFile:
        encrypted = b'%s#####%s' % (key, encrypted)
        encryptedFile.write(encrypted)


def decryptFile(filePath, destPath=None, key=None):
    # using the key
    if not key:
        key = KEY
    fernet = Fernet(key)

    # opening the encrypted file
    with open(filePath, 'rb') as enc_file:
        encrypted = enc_file.read()
    # print(encrypted.split(b'#####')[0])
    key, encrypted = encrypted.split(b'#####')
    fernet = Fernet(key)

    # decrypting the file
    decrypted = fernet.decrypt(encrypted)

    # opening the file in write mode and
    # writing the decrypted data
    if destPath:
        filePath = os.path.join(destPath, os.path.basename(filePath))
    with open(filePath, 'wb') as dec_file:
        dec_file.write(decrypted)
    return filePath


if __name__ == '__main__':
    # print(KEY)
    # encryptFile(r"D:\2-Dev-Vatapiganapathi bhaje1.mp4")
    path = decryptFile(r"D:\2-Dev-Vatapiganapathi bhaje1.mp4", destPath=r"D:\testing")

