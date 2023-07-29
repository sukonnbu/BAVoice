import os

character = input("원하는 블루아카 캐릭터를 영문으로 입력하세요(예시: Azusa) : ")
path = f"./{character}/"
src_list = os.listdir(path)
os.makedirs(path + "converted/")

for audio in src_list:
    os.system(f"ffmpeg.exe -i ./{path}/{audio} ./{path}/converted/{audio[:-4]}.wav")
