import zlib

from functools import partial
from ImageType import ImageType
from OneTimePad import OneTimePad
from typing import Callable
from VideoType import VideoType
from WavType import WavType

"""
[1, 9]
The higher the number the smaller the resulted message
(At the cost of being more computationally intensive)
"""
COMPRESSION_LEVEL = 9

class Controller:
    
    def handle_encode(
        self,
        filepath: str,
        secret_message: str,
        nr_lsb_used: int,
        apply_encryption: bool,
        select_output_path: Callable
        ):
        exception = None
        mask = None
        try:
            # Compress and encrypt the secret message if requested
            compressed_message = zlib.compress(bytes(secret_message,'utf-8'), COMPRESSION_LEVEL)

            if apply_encryption: 
                otp = OneTimePad(len(compressed_message))
                final_message = otp.encrypt(compressed_message)
                mask = otp.get_hexmask()
            else:
                final_message = compressed_message

            # Determine the carrier's extension and call the appropriate encoding function
            extension = (filepath.split('.'))[1]
            select_output_path = partial(select_output_path, extension)
            match extension:
                case "png":
                    ImageType.encode(filepath, final_message, nr_lsb_used, select_output_path)
                case "jpg":
                    ImageType.encode(filepath, final_message, nr_lsb_used, select_output_path)
                case "wav":
                    WavType.encode(filepath, final_message, nr_lsb_used, select_output_path)
                case "mp4":
                    VideoType.encode(filepath, final_message, nr_lsb_used, select_output_path)
                case default:
                    raise ValueError(f"Unable to support encoding for {extension} files!")
        except Exception as e:
            exception = e
        
        return mask, exception

    def handle_decode(
        self,
        filepath: str,
        nr_lsb_used: int,
        mask: bytes
        ):
        exception = None
        decompressed_message = None
        try:
            # Determine the carrier's extension and call the appropriate decoding function
            extension = (filepath.split('.'))[1]
            match extension:
                case "png":
                    secret_message = ImageType.decode(filepath, nr_lsb_used)
                case 'jpg':
                    secret_message = ImageType.decode(filepath, nr_lsb_used)
                case "wav":
                    secret_message = WavType.decode(filepath, nr_lsb_used)
                case "mp4":
                    secret_message = VideoType.decode(filepath, nr_lsb_used)
                case default:
                    raise ValueError(f"Unable to support decoding for {extension} files!")
            
            # Decrypt the message if a valid mask is given
            if len(mask):
                if len(mask) != len(secret_message):
                    raise ValueError(f"The length of the mask({len(mask)}) doesn't match with the length of the message ({len(secret_message)})!")
                
                decrypted_message = OneTimePad.decrypt(secret_message, mask)
            else:
                decrypted_message = secret_message
            
            # Decompress the message
            decompressed_message = zlib.decompress(decrypted_message)

        except Exception as e:
            exception = e
        
        return decompressed_message, exception
