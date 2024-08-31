from cryptography.fernet import Fernet

def set_key(username):
    key = Fernet.generate_key()
    distraction_name = "$$$^^^PM" + username + "PM^^^$$$"
    file = open(distraction_name + ".key", "wb")
    file.write(key)
    file.close()

def encrypt_some(username, password):
    distraction_name = "$$$^^^PM" + username + "PM^^^$$$"
    file = open(distraction_name + ".key", "rb")
    key = file.read()
    file.close()
    encoded_username = username.encode()
    f = Fernet(key)
    encrypted_username = f.encrypt(encoded_username)
    encoded_password = password.encode()
    f = Fernet(key)
    encrypted_password = f.encrypt(encoded_password)
    encrypted_list = (encrypted_username, encrypted_password)
    return encrypted_list

def encrypt_all(username, user, password, email, info):
    distraction_name = "$$$^^^PM" + username + "PM^^^$$$"
    file = open(distraction_name + ".key", "rb")
    key = file.read()
    file.close()
    f = Fernet(key)
    encoded_username = user.encode()
    encrypted_username = f.encrypt(encoded_username)
    encoded_password = password.encode()
    encrypted_password = f.encrypt(encoded_password)
    encoded_email = email.encode()
    encrypted_email = f.encrypt(encoded_email)
    encoded_info = info.encode()
    encrypted_info = f.encrypt(encoded_info)
    encrypted_list = (encrypted_username, encrypted_password, encrypted_email, encrypted_info)
    return encrypted_list

def get_key(username):
    distraction_name = "$$$^^^PM" + username + "PM^^^$$$"
    file = open(distraction_name + ".key", "rb")
    key = file.read()
    file.close()
    return key

def decrypt(encrypted_username, key):
    f = Fernet(key)
    decrypted_username = f.decrypt(encrypted_username)
    original_username = decrypted_username.decode()
    return original_username

def decrypt_tables(tables, key):
    tables_original = []
    for table in tables:
        f = Fernet(key)
        decrypted = f.decrypt(table)
        original = decrypted.decode()
        tables_original.append(original)
    return tables_original
