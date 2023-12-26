import os
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from tkinter import messagebox as msg_box


def crawl_voices(name: str, set_prg_bar, set_log):
    # 음성이 저장된 페이지에 접근
    res = requests.get(f'https://bluearchive.wiki/wiki/{name}/audio')
    soup = BeautifulSoup(res.content, 'html.parser')

    # 음성 요소들만 뽑아냄
    audio_list = soup.findAll('audio')

    name = name.replace(" ", "_")
    path = f"./{name}/"

    if os.path.isdir(path):
        is_proceed = msg_box.askokcancel("확인", f"{path} 폴더가 이미 존재합니다. 이대로 진행하시겠습니까?")
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

        set_prg_bar("sub", (i+1)/len(audio_list) * 100)

    set_log(f"오디오 다운로드 완료\n보이스 개수: {len(audio_list)}")
