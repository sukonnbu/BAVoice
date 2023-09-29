import tkinter as tk

import main

window = tk.Tk(screenName="BAaudio GUI")


def getText() :
    text = selectText.get("1.0", tk.END).strip()

    stdList = []
    for i in range(1, 5):
        linespaceIndex = int(text.find("\n"))

        if linespaceIndex != -1:
            stdList.append(text[0:linespaceIndex].strip())
            text = text[linespaceIndex + 1:]
        else:
            stdList.append(text.strip())
            break

    print(stdList)
    return stdList

def download_voices():
    stdList = getText()
    for std in stdList:
        main.crawlVoices(std)

lab = tk.Label(text="hello")

selectText = tk.Text()

getButton = tk.Button(text="send", command=download_voices)


lab.pack()
selectText.pack()
getButton.pack()
window.mainloop()
