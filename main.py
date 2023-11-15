import os
import requests
import convert
import makezip
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg_box


class Character:
    def __init__(self, name: str, exp_type: str, is_zip: int):
        self.name = name
        self.exp_type = exp_type
        self.is_zip = is_zip

    def crawl_voices(self, sub_prg_bar: ttk.Progressbar, sub_p_var: tk.DoubleVar, log_text: tk.Text):
        res = requests.get(f'https://bluearchive.wiki/wiki/{self.name}/audio')
        soup = BeautifulSoup(res.content, 'html.parser')
        path = ''

        audio_list = soup.findAll('audio')

        if audio_list:
            name = self.name.replace(" ", "_")
            path = f"./{name}/"

            if not os.path.isdir(path):
                os.makedirs(path)

            for i in range(0, len(audio_list)):

                source = audio_list[i].find('source')
                title = audio_list[i]['data-mwtitle']
                src = "https:" + source['src']
                log_text.insert(tk.END, src + " 다운로드 중...")
                print(src, "다운로드 중")

                if not os.path.isfile(path + title):
                    try:
                        urlretrieve(src, path + title)
                        log_text.insert(tk.END, src + " 다운로드 성공")
                        print(src, "다운로드 성공")
                    except Exception as e:
                        log_text.insert(tk.END, src + " 다운로드 실패...\n오류메세지: " + e)

                sub_p_var.set(i/len(audio_list) * 100)

        else:
            msg_box.showerror("오류", "잘못된 학생 이름입니다.\n올바른 학생 이름을 찾으려면 'liststds.py'를 실행하세요.")

        log_text.insert(tk.END, "오디오 다운로드 완료\n보이스 개수 :" + str(len(audio_list)))

        convert.convert_to(path, self.exp_type)

        if self.is_zip == 1:
            makezip.make_zip(path, self.exp_type)
