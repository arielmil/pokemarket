from cryptography.fernet import Fernet
key = Fernet.generate_key()
with open('./.key.bin', 'wb') as file_object:   file_object.write(key)
