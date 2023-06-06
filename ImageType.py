from PIL import Image
from FileType import FileType
from typing import List, cast
from math import ceil
import sys

COMPRESSION_LEVEL = 1
USE_BYTE_SKIP = True

class ImageType(FileType):
    def __init__(self):
        pass
    
    @staticmethod
    def encode(
        input_image_path: str,
        secret_message: bytes,
        nr_lsb_used: int,
        select_output_path
    ) -> None:
        image = Image.open(input_image_path)
        image = ImageType.encode_message_in_image(image, secret_message, nr_lsb_used)

        is_animated = getattr(image, "is_animated", False)
        image.save(select_output_path(), compress_level=COMPRESSION_LEVEL, save_all=is_animated)
    
    @staticmethod
    def encode_message_in_image(
        input_image: Image.Image,
        secret_message: bytes,
        nr_lsb_used: int
    ) -> Image.Image:
        color_data = [v for t in input_image.getdata() for v in t]

        message_length = len(secret_message)
        max_bytes_to_encode = ImageType.max_bytes_to_encode(input_image, nr_lsb_used)
        file_size = message_length.to_bytes(
            max_bytes_to_encode.bit_length(), byteorder=sys.byteorder
        )
        final_message = file_size + secret_message

        if len(final_message) > max_bytes_to_encode:
            raise ValueError(
                f"Only able to encode {max_bytes_to_encode} bytes \
                    in image, but message length is {len(final_message)} bytes!"
            )
        
        if nr_lsb_used == 1 and USE_BYTE_SKIP:
            maximum_bytes_in_image = max_bytes_to_encode - max_bytes_to_encode.bit_length()
            color_data = ImageType.encode_message_in_carrrier_list(color_data, final_message, 1)
            color_data[max_bytes_to_encode.bit_length() * 8:] = ImageType.encode_message_in_carrier_list_skip(
                color_data[max_bytes_to_encode.bit_length() * 8:], secret_message, maximum_bytes_in_image)
        else:
            color_data = ImageType.encode_message_in_carrrier_list(color_data, final_message, nr_lsb_used)

        input_image.putdata(
            cast(List[int], list(zip(*[iter(color_data)] * len(input_image.getdata()[0]))))
        )
        return input_image
    

    @staticmethod
    def decode(
        encoded_image_path: str,
        nr_lsb_used: int
    ) -> bytes:
        steg_image = Image.open(encoded_image_path)
        secret_message = ImageType.recover_message_from_image(steg_image, nr_lsb_used)
        return secret_message

    @staticmethod
    def recover_message_from_image(
        steg_image: Image.Image,
        nr_lsb_used: int
    ) -> bytes:
        color_data = [v for t in steg_image.getdata() for v in t]

        max_bytes_to_encode = ImageType.max_bytes_to_encode(steg_image, nr_lsb_used)
        file_size = max_bytes_to_encode.bit_length()
        rightmost_bit_index = int(ceil(8 * file_size / nr_lsb_used))

        bytes_to_recover = int.from_bytes(
            ImageType.decode_message_from_carrier(
                color_data[:rightmost_bit_index], rightmost_bit_index, nr_lsb_used
            ),
            byteorder=sys.byteorder,
        )

        maximum_bytes_in_image = max_bytes_to_encode - file_size
        
        if bytes_to_recover > maximum_bytes_in_image:
            raise ValueError("No secret message hidden in this image with this app, or image is corrupted!")
        
        if nr_lsb_used == 1 and USE_BYTE_SKIP:
            return ImageType.decode_message_from_carrier_skip(color_data[file_size * 8:],
                                                              8 * (bytes_to_recover), maximum_bytes_in_image)
        else:
            return ImageType.decode_message_from_carrier(color_data[file_size * 8 / nr_lsb_used:],
                                                        8 * (bytes_to_recover), nr_lsb_used)

        
    @staticmethod
    def max_bytes_to_encode(image: Image.Image, nr_lsb_used: int) -> int:
        return int(ceil(3 * image.size[0] * image.size[1] * nr_lsb_used / 8))
