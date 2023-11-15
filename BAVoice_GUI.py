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
    global sub_prg_bar
    global sub_p_var
    set_prg_bar(0)
    std_list = get_text()
    std_num = len(std_list)

    for i in range(0, std_num):
        std = main.Character(std_list[i], exp_combobox.get(), zip_var.get())
        std.crawl_voices(sub_prg_bar, sub_p_var)
        set_prg_bar(round((100 / std_num) * (i+1), 1))

    msg_box.showinfo("알림", "다운로드 완료")


def set_prg_bar(value):
    main_p_var.set(value)
    prg_text.set(f"{value} %")

    main_prg_bar.update()


window = Tk()
window.title("BAVoice GUI")
window.resizable(False, False)

mainframe = ttk.Frame(window, padding="3 3 12 12")
mainframe.grid(column=0, row=0)
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)


title_lab = Label(mainframe, text="Student List to Download:", font="arial")
title_lab.grid(column=2, row=1)
select_text = Text(mainframe)
select_text.grid(column=2, row=2)

conv_lab = Label(mainframe, text="Convert to: ")
conv_lab.grid(column=2, row=3)
exp_vals = [".wav", ".mp3", ".ogg"]
exp_combobox = ttk.Combobox(mainframe, height=3, values=exp_vals, state="readonly")
exp_combobox.set(".wav")
exp_combobox.grid(column=2, row=4)

zip_var = IntVar()
zip_chkbox = Checkbutton(mainframe, text=".zip 파일로 압축하기", variable=zip_var)
zip_chkbox.select()
zip_chkbox.grid(column=2, row=4, sticky=E)

get_button = Button(mainframe, text="DOWNLOAD", command=download_voices)
get_button.grid(column=2, row=5)

prg_text = StringVar()
prg_text.set("0 %")
prg_lab = Label(mainframe, textvariable=prg_text)
prg_lab.grid(column=2, row=6)

main_p_var = DoubleVar()
main_prg_bar = ttk.Progressbar(mainframe, maximum=100, length=500, variable=main_p_var)
main_prg_bar.grid(column=2, row=7, columnspan=3)

sub_p_var = DoubleVar()
sub_prg_bar = ttk.Progressbar(mainframe, maximum=100, length=500, variable=sub_p_var)
sub_prg_bar.grid(column=2, row=8, columnspan=3)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

window.mainloop()
