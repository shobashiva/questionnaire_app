from Crypto.Cipher import AES
from Crypto.Protocol import KDF
import base64

class AESCipher():

    def __init__(self): 
        password = 'EzyRydey'
        salt = b'\x49\x76\x61\x6e\x20\x4d\x65\x64\x76\x65\x64\x65\x76'
        password_derived_bytes = KDF.PBKDF2(password, salt, 48, 1000)
        self.key = password_derived_bytes[:32]
        self.iv = password_derived_bytes[32:48]
        self.bs = 16

    def encrypt(self, plaintext):
        plaintext = self._pad(plaintext)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(plaintext))

    def decrypt(self, ciphertext):
        ciphertext = base64.b64decode(ciphertext)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self._unpad(cipher.decrypt(ciphertext)).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

# text = 'p@$$w0rd'
# cipher = AESCipher()
# encrypted = cipher.encrypt(text)
# print(encrypted)
# print(cipher.decrypt(encrypted))