import os
import zipfile
import tkinter as tk
from tkinter import ttk


def make_zip(path, window: tk.Tk, log_text: tk.Text, exp_type: str):
    if os.path.isdir(path):
        zip_file = zipfile.ZipFile(path + f"/{path[2:-1]}.zip", "w")

        for audio in os.listdir(path):
            try:
                if audio.endswith(exp_type):
                    zip_file.write(os.path.join(path, audio), compress_type=zipfile.ZIP_DEFLATED)
                    log_text.insert(1.0, f".zip에 {audio} 파일 추가됨\n")
                    window.update()

                    os.remove(os.path.join(path, audio))
                    log_text.insert(1.0, f"{audio} 파일 삭제됨\n")
            except Exception as e:
                log_text.insert(1.0, f".zip 생성 중 오류 발생...\n오류메시지: {e}\n")
            window.update()
        zip_file.close()

        log_text.insert(1.0, f".zip 파일 생성 완료!\n")
        window.update()
