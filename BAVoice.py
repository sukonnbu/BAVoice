import main

downloadListFile = open(r"./download_list.txt", 'r')

downloadList = downloadListFile.readlines()
print(downloadList)
for std in downloadList:
    std = std.strip()
    print(f"{std} 보이스 다운로드중...")

    main.crawlVoices(std)
