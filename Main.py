import os
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve

character = input("원하는 블루아카 캐릭터를 영문으로 입력하세요(예시: Azusa) : ")
path = f"./{character}/"
os.makedirs(path)

res = requests.get(f'https://bluearchive.wiki/wiki/{character}/audio')
soup = BeautifulSoup(res.content, 'html.parser')

audio_list = soup.findAll('audio')


for audio in audio_list:
    source = audio.find('source')
    title = audio['data-mwtitle']
    src = "https:" + source['src']
    #print(title, src)
    urlretrieve(src, path + title)


src_list = os.listdir(path)
print(src_list)
os.makedirs(path + "converted/")

for audio in src_list:
    os.system(f"ffmpeg.exe -i ./{path}/{audio} ./{path}/converted/{audio[:-4]}.wav")
