from FileType import FileType
import numpy as np
from typing import Callable
from math import ceil
import cv2
import sys

class VideoType(FileType):
    def __init__(self):
        pass

    @staticmethod
    def encode(
        input_video_path: str,
        secret_message: bytes,
        nr_lsb_used: int,
        select_output_path: Callable[[], str]
    ) -> None:
        cap = cv2.VideoCapture(input_video_path)

        frames_bytes = []
        while cap.isOpened():
            ret, frame = cap.read()

            if ret:
                frame_bytes = frame.tobytes()
                frames_bytes.append(frame_bytes)
            else:
                break

        all_frames_bytes = b''.join(frames_bytes)
        message_length = len(secret_message)
        nr_bytes_available = (len(all_frames_bytes) * nr_lsb_used) // 8
        file_size = message_length.to_bytes(
            nr_bytes_available.bit_length(), byteorder=sys.byteorder
        )
        final_message = file_size + secret_message
        if len(final_message) > nr_bytes_available:
            raise ValueError(
                f"Only able to encode {nr_bytes_available} bytes \
                    in video, but message length is {len(final_message)} bytes!"
            )
        
        all_frames_bytes = FileType.encode_message_in_carrier_bytes(all_frames_bytes, final_message, nr_lsb_used)

        output_file_path = select_output_path()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH ))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT ))
        print("{}x{}".format(width, height))
        print(type(width))

        try:
            out = cv2.VideoWriter(output_file_path, fourcc, fps, (width, height))
            modified_frames_np = np.frombuffer(all_frames_bytes, dtype=np.uint8)
            modified_frames_np = modified_frames_np.reshape((-1, height, width, 3))
            for frame in modified_frames_np:
                out.write(frame)
            
            out.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(str(e))
    
    def decode(
        encoded_video_path: str,
        nr_lsb_used: int
    ) -> bytes:
        cap = cv2.VideoCapture(encoded_video_path)
        frames_bytes = []
        while cap.isOpened():
            ret, frame = cap.read()

            if ret:
                frame_bytes = frame.tobytes()
                frames_bytes.append(frame_bytes)
            else:
                break

        all_frames_bytes = b''.join(frames_bytes)
        video_frames = [t for t in all_frames_bytes]
        nr_bytes_available = (len(all_frames_bytes) * nr_lsb_used) // 8
        file_size = nr_bytes_available.bit_length()
        rightmost_bit_index = int(ceil(8 * file_size / nr_lsb_used))

        bytes_to_recover = int.from_bytes(
            VideoType.decode_message_from_carrier(
                video_frames[:rightmost_bit_index], rightmost_bit_index, nr_lsb_used
            ),
            byteorder=sys.byteorder,
        )
        maximum_bytes_in_video = nr_bytes_available - file_size

        if bytes_to_recover > maximum_bytes_in_video:
            raise ValueError("No secret message hidden in this video with this app, or audio is corrupted!")

        temp = FileType.decode_message_from_carrier(video_frames,
                                                    8 * (bytes_to_recover + file_size), nr_lsb_used)[file_size:]
        return temp
