import requests
from bs4 import BeautifulSoup
import os

req = requests.get("https://bluearchive.wiki/wiki/Characters")
soup = BeautifulSoup(req.content, "html.parser")

std_table = soup.find("tbody")
std_list = std_table.find_all("tr")[1:]
if os.path.isfile('학생 명부.txt'):
    os.remove("학생 명부.txt")
std_file = open("학생 명부.txt", 'w')

for std in std_list:
    name = std.find_all('td')[1].find('a').get_text()
    print(name)
    std_file.write(name + '\n')
