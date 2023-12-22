import sys
import wave

from FileType import FileType
from math import ceil
from typing import Callable

USE_BYTE_SKIP = True

class WavType(FileType):
    
    @staticmethod
    def encode(
        input_audio_path: str,
        secret_message: bytes,
        nr_lsb_used: int,
        select_output_path: Callable[[], str]
    ) -> None:

        audio = wave.open(input_audio_path, "r")
        sample_width = audio.getsampwidth()
        nr_frames = audio.getnframes()
        nr_samples = nr_frames * audio.getnchannels()

        message_length = len(secret_message)
        nr_bytes_available = (nr_samples * nr_lsb_used * sample_width) // 8
        file_size = message_length.to_bytes(
            nr_bytes_available.bit_length(), byteorder=sys.byteorder
        )
        final_message = file_size + secret_message

        if len(final_message) > nr_bytes_available:
            raise ValueError(
                f"Only able to encode {nr_bytes_available} bytes \
                    in audio, but message length is {len(final_message)} bytes!"
            )
        
        audio_frames = [t for t in audio.readframes(nr_frames)]

        if nr_lsb_used == 1 and USE_BYTE_SKIP:
            maximum_bytes_in_audio = nr_bytes_available - nr_bytes_available.bit_length()
            audio_frames = FileType.encode_message_in_carrier_list(audio_frames, file_size, 1)
            audio_frames[nr_bytes_available.bit_length() * 8:] = FileType.encode_message_in_carrier_list_skip(
                audio_frames[nr_bytes_available.bit_length() * 8:], secret_message, maximum_bytes_in_audio)
        else:
            audio_frames = FileType.encode_message_in_carrier_list(audio_frames, final_message, nr_lsb_used)

        encoded_audio = wave.open(select_output_path(), "w")
        encoded_audio.setparams(audio.getparams())
        encoded_audio.writeframes(bytes(audio_frames))
        encoded_audio.close()
    
    @staticmethod
    def decode(
        encoded_audio_path: str,
        nr_lsb_used: int
    ) -> bytes:
        audio = wave.open(encoded_audio_path, "r")
        sample_width = audio.getsampwidth()
        nr_frames = audio.getnframes()
        nr_samples = nr_frames * audio.getnchannels()
        audio_frames = [t for t in audio.readframes(nr_frames)]

        nr_bytes_available = (nr_samples * nr_lsb_used * sample_width) // 8
        file_size = nr_bytes_available.bit_length()
        rightmost_bit_index = int(ceil(8 * file_size / nr_lsb_used))

        bytes_to_recover = int.from_bytes(
            WavType.decode_message_from_carrier(
                audio_frames[:rightmost_bit_index], rightmost_bit_index, nr_lsb_used
            ),
            byteorder=sys.byteorder,
        )
        maximum_bytes_in_audio = nr_bytes_available - file_size

        if bytes_to_recover > maximum_bytes_in_audio:
            raise ValueError("No secret message hidden in this audio with this app, or audio is corrupted!")
        
        if nr_lsb_used == 1 and USE_BYTE_SKIP:
            return FileType.decode_message_from_carrier_skip(audio_frames[file_size * 8:],
                                                              8 * (bytes_to_recover), maximum_bytes_in_audio)
        else:
            return FileType.decode_message_from_carrier(audio_frames,
                                                        8 * (bytes_to_recover + file_size), nr_lsb_used)[file_size:]
