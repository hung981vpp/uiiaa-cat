import cv2
import numpy as np
import sys
import time
from threading import Thread
from playsound import playsound

class VideoToAscii:
    def __init__(self, video_path, width=80):
        self.video_path = video_path
        self.width = width
        self.__video_capture = cv2.VideoCapture(video_path)

        # Kiểm tra xem video có mở thành công không
        if not self.__video_capture.isOpened():
            raise ValueError(f"Error: Could not open video file {video_path}")

       # Lấy thuộc tính của video
        frame_width = int(self.__video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.__video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if frame_width == 0 or frame_height == 0:
            raise ValueError("Error: Invalid video dimensions")

         # Tính toán chiều cao duy trì tỉ lệ khung hình (điều chỉnh theo tỉ lệ ký tự ASCII)
        self.height = int(frame_height * (width / frame_width) * 0.5)

        # Định nghĩa các ký tự ASCII
        self.__ascii_chars = "_%*-=+#: "

    def __pixel_to_ascii(self, pixel):
        # Chuyển đổi pixel sang giá trị xám
        gray_value = pixel[0] * 0.114 + pixel[1] * 0.587 + pixel[2] * 0.299

        # Bỏ qua các pixel rất sáng bằng cách trả về ký tự khoảng trắng
        if gray_value > 230:  
            return " "

        ascii_char = self.__ascii_chars[int((gray_value / 255) * (len(self.__ascii_chars) - 1))]

        # Thêm màu sử dụng mã escape ANSI
        r, g, b = int(pixel[2]), int(pixel[1]), int(pixel[0])
        return f"\033[38;2;{r};{g};{b}m{ascii_char}\033[0m"

    def __frame_to_ascii(self, frame):
        ascii_art = []
        for row in frame:
            ascii_row = "".join(self.__pixel_to_ascii(pixel) for pixel in row)
            ascii_art.append(ascii_row)
        return ascii_art

    def play(self):
        try:
            first_frame = True
            previous_frame = ["" for _ in range(self.height)]
            while True:
                ret, frame = self.__video_capture.read()
                if not ret:
                    break

                # Thay đổi kích thước khung hình
                resized_frame = cv2.resize(frame, (self.width, self.height))

                # Chuyển đổi khung hình sang ASCII
                ascii_frame = self.__frame_to_ascii(resized_frame)

                 # Hiển thị khung hình từng dòng một
                for i, ascii_row in enumerate(ascii_frame):
                    if first_frame or ascii_row != previous_frame[i]:
                        print(f"\033[{i+1};0H{ascii_row}")  # Move cursor to the correct line and overwrite

                previous_frame = ascii_frame
                first_frame = False

                time.sleep(0.0109)  # Điều chỉnh tốc độ phát lại

        except KeyboardInterrupt:
            pass
        finally:
            self.__video_capture.release()

def play_music(audio_path):
    try:
        playsound(audio_path)
    except Exception as e:
        print(f"Error playing audio: {e}")

if __name__ == "__main__":
    video_path = sys.argv[1] if len(sys.argv) > 1 else "cat.mp4"  # đường dẫn video
    audio_path = "cat.mp3"  # Đường dẫn âm thanh

    try:
       # Bắt đầu phát âm thanh trên một luồng riêng biệt
        music_thread = Thread(target=play_music, args=(audio_path,), daemon=True)
        music_thread.start()

         # Bắt đầu phát video ASCII
        video_to_ascii = VideoToAscii(video_path, width=100) 
        video_to_ascii.play()
        print('\033[1;36m #Hwungg🥀')
    except Exception as e:
        print(f"Error: {e}")
