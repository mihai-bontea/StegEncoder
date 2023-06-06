from secrets import randbelow
from hashlib import sha256

LOW_GEN = -100000000
HIGH_GEN = 100000000

class OneTimePad:
    def __init__(self, message_length):
        random_number = self.get_random_number()
        self.mask = sha256(str(random_number).encode('utf-8')).digest()
        self.hexmask = sha256(str(random_number).encode('utf-8')).hexdigest()

        while len(self.mask) < message_length:
            random_number = self.get_random_number()
            self.mask += sha256(str(random_number).encode('utf-8')).digest()
            self.hexmask += sha256(str(random_number).encode('utf-8')).hexdigest()

        # Truncate the length of the mask such that it's equal to the message length
        length_difference = len(self.mask) - message_length
        if length_difference != 0:
            self.mask = self.mask[:-length_difference]
            self.hexmask = self.hexmask[:-length_difference * 2]
        
    def get_random_number(self):
        return randbelow(HIGH_GEN - LOW_GEN) + HIGH_GEN

    def get_mask(self):
        return self.mask

    def get_hexmask(self):
        return self.hexmask
    
    def encrypt(self, message):
        return bytes(x ^ y for x, y in zip(message, self.mask))
    
    @staticmethod
    def decrypt(ciphertext, mask):
        return bytes(x ^ y for x, y in zip(ciphertext, mask))
