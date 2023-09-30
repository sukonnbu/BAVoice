from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msg_box
import main


def get_text():
    text = select_text.get("1.0", END).strip()

    std_list = []
    while True:
        linespace_index = int(text.find("\n"))

        if linespace_index != -1:
            std_list.append(text[0:linespace_index].strip())
            text = text[linespace_index + 1:]
        else:
            std_list.append(text.strip())
            break

    print(std_list)
    return std_list


def download_voices():
    std_list = get_text()
    std_num = len(std_list)

    for i in range(0, std_num):
        main.crawl_voices(std_list[i], exp_combobox.get(), zip_var.get())
        set_prg_bar(round((100 / std_num) * (i+1), 1))

    msg_box.showinfo("알림", "다운로드 완료")


def set_prg_bar(value):
    p_var.set(value)
    prg_text.set(f"{value} %")

    prg_bar.update()


window = Tk()
window.title("BAaudio GUI")
window.resizable(False, False)

mainframe = ttk.Frame(window, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)


title_lab = Label(mainframe, text="Student List to Download")
title_lab.grid(column=2, row=1)
select_text = Text(mainframe)
select_text.grid(column=2, row=2)

conv_lab = Label(mainframe, text="Convert to: ").grid(column=2, row=3)
exp_vals = [".wav", ".mp3", ".ogg"]
exp_combobox = ttk.Combobox(mainframe, height=3, values=exp_vals, state="readonly")
exp_combobox.set(".wav")
exp_combobox.grid(column=2, row=4)

zip_var = IntVar()
zip_chkbox = Checkbutton(mainframe, text=".zip 파일로 압축하기", variable=zip_var)
zip_chkbox.select()
zip_chkbox.grid(column=2, row=4, sticky=(E))

get_button = Button(mainframe, text="DOWNLOAD", command=download_voices)
get_button.grid(column=2, row=5)

prg_text = StringVar()
prg_text.set("0 %")
prg_lab = Label(mainframe, textvariable=prg_text)
prg_lab.grid(column=2, row=6)

p_var = DoubleVar()
prg_bar = ttk.Progressbar(mainframe, maximum=100, length=150, variable=p_var)
prg_bar.grid(column=2, row=7)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

window.mainloop()
