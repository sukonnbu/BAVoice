import os
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


def convert_to(
        path, window: tk.Tk, sub_p_var: tk.DoubleVar, sub_prg_bar: ttk.Progressbar, log_text: ScrolledText, exp_type
):
    if os.path.isdir(path) and exp_type != ".ogg":
        src_list = os.listdir(path)

        for i in range(0, len(src_list)):
            try:
                os.system(f"ffmpeg.exe -i ./{path}/{src_list[i]} ./{path}/{src_list[i][:-4]}{exp_type} -loglevel quiet")
                os.remove(f"./{path}/{src_list[i]}")

                log_text['state'] = "normal"
                log_text.insert(1.0, f"./{path}/{src_list[i]} 파일 삭제\n")
                log_text['state'] = "disabled"
            except Exception as e:
                log_text['state'] = "normal"
                log_text.insert(1.0, f"파일 변환중 오류 발생...\n오류메시지: {e}\n")
                log_text['state'] = "disabled"
            window.update()

            sub_p_var.set(i/len(src_list)*100)
            sub_prg_bar.update()
