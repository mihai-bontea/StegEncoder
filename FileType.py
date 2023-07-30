from math import ceil
from time import time
from typing import List
import numpy as np

SKIP_BYTES = True

class FileType:
    
    @staticmethod
    def encode_message_in_carrier_bytes_skip(
        carrier: bytes,
        secret_message: bytes,
        skip_over: int
    ) -> bytes:
        message_length = len(secret_message)
        new_secret_message_len_in_bytes = skip_over * (message_length * 8 - 1) + message_length * 8
        
        payload_bits = np.unpackbits(
            np.frombuffer(secret_message, dtype=np.uint8, count=message_length)
        )

        carrier_bits = np.unpackbits(
            np.frombuffer(carrier, dtype=np.uint8, count=new_secret_message_len_in_bytes).view(np.uint8)
        ).reshape(new_secret_message_len_in_bytes, 8)

        payload_index = 0
        for carrier_index in range(0, len(carrier_bits), (skip_over + 1)):
            carrier_bits[carrier_index][7] = payload_bits[payload_index]
            payload_index += 1
        
        return np.packbits(carrier_bits).tobytes() + carrier[new_secret_message_len_in_bytes:]
    
    @staticmethod
    def encode_message_in_carrier_list_skip(
        carrier: List[np.uint8],
        secret_message: bytes,
        bytes_available: int
    ) -> List[np.uint8]:
        """
        Returns the modified carrier bytes after the secret message has been encoded inside with
        the skip bytes feature enabled.
        """
        message_length = len(secret_message)
        skip = 0
        while skip * (message_length * 8 - 1) + len(secret_message) * 8 <= bytes_available:
            skip += 1

        new_secret_message_len_in_bytes = skip * (message_length * 8 - 1) + message_length * 8
        carrier_bytes = np.array(carrier[:new_secret_message_len_in_bytes], dtype=np.uint8).tobytes()
        modified = FileType.encode_message_in_carrier_bytes_skip(carrier_bytes, secret_message, skip)
        carrier[:new_secret_message_len_in_bytes] = np.frombuffer(modified, dtype=np.uint8).tolist()
        return carrier
    
    @staticmethod
    def encode_message_in_carrier_bytes(
        carrier: bytes,
        secret_message: bytes,
        nr_lsb_used: int
    ) -> bytes:
        message_length = len(secret_message)
        payload_bits = np.zeros(shape=(message_length, 8), dtype=np.uint8)
        payload_bits[:message_length, :] = np.unpackbits(
            np.frombuffer(secret_message, dtype=np.uint8, count=message_length)
        ).reshape(message_length, 8)

        bytes_modified = int(ceil(message_length * 8 / nr_lsb_used))
        payload_bits.resize(bytes_modified * nr_lsb_used)

        carrier_bits = np.unpackbits(
            np.frombuffer(carrier, dtype=np.uint8, count=bytes_modified).view(np.uint8)
        ).reshape(bytes_modified, 8)

        carrier_bits[:, 8 - nr_lsb_used : 8] = payload_bits.reshape(
            bytes_modified, nr_lsb_used
        )

        return np.packbits(carrier_bits).tobytes() + carrier[bytes_modified :]

    @staticmethod
    def encode_message_in_carrier_list(
        carrier: List[np.uint8],
        secret_message: bytes,
        nr_lsb_used: int
    ) -> List[np.uint8]:
        """
        Returns the modified carrier bytes after the secret message has been encoded inside.
        """
        rightmost_bit_index = int(ceil(len(secret_message) * 8 / nr_lsb_used))
        carrier_bytes = np.array(carrier[:rightmost_bit_index], dtype=np.uint8).tobytes()
        
        modified = FileType.encode_message_in_carrier_bytes(carrier_bytes, secret_message, nr_lsb_used)
        carrier[:rightmost_bit_index] = np.frombuffer(modified, dtype=np.uint8).tolist()
        return carrier

    @staticmethod
    def decode_message_from_carrier(
        carrier: List[np.uint8],
        message_len_in_bits: int,
        nr_lsb_used: int
    ) -> bytes:
        """
        Returns the bytes of te secret message stored inside the carrier bytes.
        """
        message_len_in_bytes = int(ceil(message_len_in_bits / nr_lsb_used))
        carrier_bytes = np.array(carrier[:message_len_in_bytes], dtype=np.uint8).tobytes()
        message_bits = np.unpackbits(
            np.frombuffer(carrier_bytes, dtype=np.uint8, count=message_len_in_bytes).view(np.uint8)
        ).reshape(message_len_in_bytes, 8)[:, 8 - nr_lsb_used : 8]
        return np.packbits(message_bits).tobytes()[: message_len_in_bits // 8]
    
    @staticmethod
    def decode_message_from_carrier_skip(
        carrier: List[np.uint8],
        message_len_in_bits: int,
        bytes_available: int
    ) -> bytes:
        """
        Returns the bytes of the secret message stored inside the carrier bytes with the skip bytes feature enabled.
        """
        skip = 0
        while skip * (message_len_in_bits - 1) + message_len_in_bits <= bytes_available:
            skip += 1

        new_secret_message_len = skip * (message_len_in_bits - 1) + message_len_in_bits
        carrier_bytes = np.array(carrier[:new_secret_message_len], dtype=np.uint8).tobytes()

        message_bits = np.unpackbits(
            np.frombuffer(FileType.skip_carrier_bytes(carrier_bytes, skip), dtype=np.uint8, count=message_len_in_bits).view(np.uint8)
        ).reshape(message_len_in_bits, 8)[:, 8 - 1 : 8]
        return np.packbits(message_bits).tobytes()[: message_len_in_bits // 8]

    @staticmethod
    def skip_carrier_bytes(
        carrier_bytes: bytes,
        skip_over: int
    ) -> bytes:
        """
        Returns the bytes of the carrier that actually contain bits from the secret message,
        jumping over 'skip_over' unmodified bytes.
        """
        temp = bytearray()
        for index in range(0, len(carrier_bytes), skip_over + 1):
            temp.append(carrier_bytes[index])
        return bytes(temp)