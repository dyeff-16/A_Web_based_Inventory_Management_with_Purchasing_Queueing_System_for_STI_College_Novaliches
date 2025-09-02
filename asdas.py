from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)

original = b"MySecretValue"
encrypted = cipher.encrypt(original)
print("Encrypted:", encrypted)

# Decrypt
decrypted = cipher.decrypt(encrypted)
print("Decrypted:", decrypted)