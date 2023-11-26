import os
import zipfile
import tkinter as tk
from tkinter.scrolledtext import ScrolledText


# 파일 압축
def make_zip(path, window: tk.Tk, log_text: ScrolledText, exp_type: str):
    # 압축파일 생성
    zip_file = zipfile.ZipFile(path + f"/{path[2:-1]}.zip", "w")

    for audio in os.listdir(path):
        try:
            if audio.endswith(exp_type):
                # 음성 파일 추가
                zip_file.write(os.path.join(path, audio), compress_type=zipfile.ZIP_DEFLATED)
                log_text['state'] = "normal"
                log_text.insert(1.0, f".zip에 {audio} 파일 추가됨\n")
                log_text['state'] = "disabled"
                window.update()

                os.remove(os.path.join(path, audio))
                log_text['state'] = "normal"
                log_text.insert(1.0, f"{audio} 파일 삭제됨\n")
                log_text['state'] = "disabled"

        except Exception as e:
            log_text['state'] = "normal"
            log_text.insert(1.0, f".zip 생성 중 오류 발생...\n오류메시지: {e}\n")
            log_text['state'] = "disabled"

        window.update()

    zip_file.close()

    log_text['state'] = "normal"
    log_text.insert(1.0, f".zip 파일 생성 완료\n")
    log_text['state'] = "disabled"
    window.update()
