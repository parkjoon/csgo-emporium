from cryptography.fernet import Fernet

def encrypt(password, data):
    f = Fernet(password)
    return f.encrypt(data)

def decrypt(password, data):
    f = Fernet(password)
    return f.decrypt(data)
