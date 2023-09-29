from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgBox
import main

def getText():
    text = selectText.get("1.0", END).strip()

    stdList = []
    while True:
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
    stdNumber = len(stdList)

    for i in range(0, stdNumber):
        main.crawlVoices(stdList[i])
        setPrgBar(round((100 / stdNumber) * (i+1), 1))

    msgBox.showinfo("알림", "다운로드 완료")

def setPrgBar(value):
    p_var.set(value)
    lab_text.set(f"{value} %")

    prg_bar.update()


window = Tk()
window.title("BAaudio GUI")
window.resizable(False, False)

mainframe = ttk.Frame(window, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)


lab = Label(mainframe, text="Student List to Download")
lab.grid(column=2, row=1)
selectText = Text(mainframe)
selectText.grid(column=2, row=2)
getButton = Button(mainframe, text="DOWNLOAD", command=download_voices)
getButton.grid(column=2, row=3)

lab_text = StringVar()
lab_text.set("0 %")
prg_lab = Label(mainframe, textvariable=lab_text)
prg_lab.grid(column=2, row=4)

p_var = DoubleVar()
prg_bar = ttk.Progressbar(mainframe, maximum=100, length=150, variable=p_var)
prg_bar.grid(column=2, row=5)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

window.mainloop()
