import datetime
from cryptography.fernet import Fernet, InvalidToken


def validatorEncrypt(value):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    message = str(value).encode()
    secretKeyFile = "license.key"
    with open(secretKeyFile, 'wb') as secret:
        secretKey = b'%s#####%s' % (key, fernet.encrypt(message))
        secret.write(secretKey)
    return secretKeyFile


def validatorDecrypt(secretKey):
    with open(secretKey, 'rb') as secret:
        secretKey = secret.read()

    try:
        key, token = secretKey.split(b'#####')
    except ValueError:
        print("Invalid secret key")
        return False
    fernet = Fernet(key)
    hexCode = token
    try:
        message = float(fernet.decrypt(hexCode))
    except InvalidToken:
        print("Invalid secret key")
        return False
    except:
        print("Other error")
        return False
    return message


def validate(secretKey):
    timeStamp = validatorDecrypt(secretKey)
    if not timeStamp:
        return False
    currentTime = datetime.datetime.now()
    print(currentTime.timestamp())
    if timeStamp < currentTime.timestamp():
        return False
    else:
        return True


# if __name__ == '__main__':
#     # print(validatorEncrypt(1641670000))
#     print(validate("license.key"))
