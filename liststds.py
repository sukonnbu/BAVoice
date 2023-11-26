import requests
from bs4 import BeautifulSoup
import os


def make_std_list():
    req = requests.get("https://bluearchive.wiki/wiki/Characters")
    soup = BeautifulSoup(req.content, "html.parser")

    std_table = soup.find("tbody")
    std_button_list = std_table.find_all("tr")[1:]

    if os.path.isfile('학생 명부.txt'):
        os.remove("학생 명부.txt")
    std_file = open("학생 명부.txt", 'w')

    std_list = []
    for std in std_button_list:
        name = std.find_all('td')[1].find('a').get_text()
        std_list.append(name)

    print(std_list)

    for i in range(0, len(std_list)):
        std_file.write(std_list[i] + "\n")
        if i+1 < len(std_list):
            if std_list[i][0] != std_list[i+1][0]:
                std_file.write("\n")

    std_file.close()

    os.system("notepad 학생 명부.txt")


if __name__ == "__main__":
    make_std_list()
