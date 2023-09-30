import os
import requests
import convert
import makezip
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from tkinter import messagebox as msg_box


def crawl_voices(character: str, exp_type: str, is_zip: int):
    res = requests.get(f'https://bluearchive.wiki/wiki/{character}/audio')
    soup = BeautifulSoup(res.content, 'html.parser')
    path = ''

    audio_list = soup.findAll('audio')

    if audio_list:

        character = character.replace(" ", "_")
        path = f"./{character}/"

        if not os.path.isdir(path):
            os.makedirs(path)

        for audio in audio_list:

            source = audio.find('source')
            title = audio['data-mwtitle']
            src = "https:" + source['src']
            print(src, "다운로드중...")

            if not os.path.isfile(path + title):
                try:
                    urlretrieve(src, path + title)
                    print(src, "다운로드 성공")
                except Exception as e:
                    print(src, "다운로드 실패...\n오류메세지: ", e)

    else:
        msg_box.showerror("오류", "잘못된 학생 이름입니다.\n올바른 학생 이름을 찾으려면 'liststds.py'를 실행하세요.")

    print("오디오 다운로드 완료\n보이스 개수 : ", len(audio_list))

    convert.convert_to(path, exp_type)

    if is_zip == 1:
        makezip.make_zip(path, exp_type)


if __name__ == "__main__":
    character = input("원하는 블루아카 캐릭터를 영문으로 입력하세요(예시: Azusa) : ")
    crawl_voices(character, ".wav", 1)
