import os
import tkinter.messagebox
import requests
import convert
import makezip
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from tkinter import messagebox as msg_box


# 생성자에 ( 캐릭터 이름 / 확장자 / 압축 여부 ) 전달
class Character:
    def __init__(self, name: str, exp_type: str, is_zip: int):
        self.name = name
        self.exp_type = exp_type
        self.is_zip = is_zip

    def crawl_voices(self, set_prg_bar, set_log):
        # 음성이 저장된 페이지에 접근
        res = requests.get(f'https://bluearchive.wiki/wiki/{self.name}/audio')
        soup = BeautifulSoup(res.content, 'html.parser')
        path = ''

        # 음성 요소들만 뽑아냄
        audio_list = soup.findAll('audio')

        if audio_list:
            name = self.name.replace(" ", "_")
            path = f"./{name}/"

            if os.path.isdir(path):
                is_proceed = tkinter.messagebox.askokcancel("확인", f"{path} 폴더가 이미 존재합니다. 이대로 진행하시겠습니까?")
                if not is_proceed:
                    return
            else:
                os.makedirs(path)

            for i in range(0, len(audio_list)):
                # 관련 정보 추출
                source = audio_list[i].find('source')
                title = audio_list[i]['data-mwtitle']
                src = "https:" + source['src']

                set_log(f"{src}\n다운로드 중...")

                # 다운로드
                if not os.path.isfile(path + title):
                    try:
                        urlretrieve(src, path + title)

                        set_log("다운로드 성공!")

                    except Exception as e:
                        set_log(f"다운로드 실패...\n오류메시지: {e}")

                else:
                    set_log("다운로드 성공!")

                set_prg_bar("sub", i/len(audio_list) * 100)

        else:
            msg_box.showerror("오류", "잘못된 학생 이름입니다.\n올바른 학생 이름을 찾으려면 'liststds.py'를 실행하세요.")

        set_log(f"오디오 다운로드 완료\n보이스 개수: {len(audio_list)}")

        # 지정된 확장자로 변환
        convert.convert_to(path, set_prg_bar, set_log, self.exp_type)

        # 파일 압축
        if self.is_zip == 1:
            makezip.make_zip(path, set_log, self.exp_type)
