import os
import tkinter as tk
from tkinter import ttk


def convert_to(path, window:tk.Tk, sub_p_var: tk.DoubleVar, sub_prg_bar: ttk.Progressbar, log_text: tk.Text, exp_type: str):
    if os.path.isdir(path) and exp_type != ".ogg":
        src_list = os.listdir(path)

        for i in range(0,len(src_list)):
            try:
                os.system(f"ffmpeg.exe -i ./{path}/{src_list[i]} ./{path}/{src_list[i][:-4]}{exp_type}")
                os.remove(f"./{path}/{src_list[i]}")
                log_text.insert(1.0, f"./{path}/{src_list[i]} 파일 삭제\n")
            except Exception as e:
                log_text.insert(1.0, f"파일 변환중 오류 발생...\n오류메시지: {e}\n")
            window.update()

            sub_p_var.set(i/len(src_list)*100)
            sub_prg_bar.update()
