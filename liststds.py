import requests
from bs4 import BeautifulSoup
import os


def make_std_list():
    # 캐릭터들 목록이 있는 페이지에 접근
    req = requests.get("https://bluearchive.wiki/wiki/Characters")
    soup = BeautifulSoup(req.content, "html.parser")

    std_table = soup.find("tbody")
    std_button_list = std_table.find_all("tr")[1:]

    if os.path.isfile('학생 명부.txt'):
        os.remove("학생 명부.txt")
    std_file = open("학생 명부.txt", 'w')

    std_list = []

    # 캐릭터 이름만 추출해 리스트에 저장
    for std in std_button_list:
        name = std.find_all('td')[1].find('a').get_text()
        std_list.append(name)

    # "학생 명부.txt에 학생 이름 작성"
    for i in range(0, len(std_list)):
        std_file.write(std_list[i] + "\n")
        if i+1 < len(std_list):
            # 이름 앞글자가 바뀔 때마다 줄바꿈
            if std_list[i][0] != std_list[i+1][0]:
                std_file.write("\n")

    std_file.close()

    os.system("notepad 학생 명부.txt")
