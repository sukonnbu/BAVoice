import main
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg_box
from tkinter.scrolledtext import ScrolledText


def get_text(window: tk.Tk, log_text: ScrolledText):
    text = select_text.get("1.0", tk.END).strip()

    std_list = []
    while True:
        next_linespace_index = int(text.find("\n"))

        if next_linespace_index != -1:
            std_list.append(text[0:next_linespace_index].strip())
            text = text[next_linespace_index + 1:]
        else:
            std_list.append(text.strip())
            break
    log_text['state'] = "normal"
    log_text.insert(1.0, str(std_list) + "\n")
    log_text['state'] = "disabled"
    window.update()

    return std_list


def download_voices(window, sub_p_var, sub_prg_bar, log_text):
    set_prg_bar(0)
    std_list = get_text(window, log_text)
    std_num = len(std_list)

    for i in range(0, std_num):
        std = main.Character(std_list[i], exp_combobox.get(), zip_var.get())
        std.crawl_voices(window, sub_p_var, sub_prg_bar, log_text)
        set_prg_bar(round((100 / std_num) * (i+1), 1))

    log_text['state'] = "normal"
    log_text.insert(1.0, f"다운로드 완료!\n")
    log_text['state'] = "disabled"
    window.update()
    msg_box.showinfo("알림", "다운로드 완료")


def set_prg_bar(value):
    main_p_var.set(value)
    prg_text.set(f"{value} %")

    main_prg_bar.update()


window = tk.Tk()
window.title("BAVoice GUI")
window.iconbitmap("icon.ico")
window.resizable(False, False)

mainframe = ttk.Frame(window, padding="3 3 12 12")
mainframe.grid(column=0, row=0)
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)

logo_img = Image.open("Logo.png")
logo_img = logo_img.resize((500, 110))
img = ImageTk.PhotoImage(logo_img)

title_logo = tk.Label(mainframe, image=img)
title_logo.grid(column=2, row=1, columnspan=3)

title_lab = tk.Label(mainframe, text="Student List to Download:", font="arial")
title_lab.grid(column=2, row=2)
select_text = ScrolledText(mainframe, width=65, height=10)
select_text.grid(column=2, row=3)

conv_lab = tk.Label(mainframe, text="Convert to: ")
conv_lab.grid(column=2, row=5)
exp_vals = [".wav", ".mp3", ".ogg"]
exp_combobox = ttk.Combobox(mainframe, height=3, values=exp_vals, state="readonly")
exp_combobox.set(".wav")
exp_combobox.grid(column=2, row=6)

zip_var = tk.IntVar()
zip_chkbox = tk.Checkbutton(mainframe, text=".zip 파일로 압축하기", variable=zip_var)
zip_chkbox.select()
zip_chkbox.grid(column=2, row=6, sticky=tk.E)

get_button = tk.Button(
    mainframe, text="DOWNLOAD", command=lambda: download_voices(window, sub_p_var, sub_prg_bar, log_text)
)
get_button.grid(column=2, row=7)


prg_text = tk.StringVar()
prg_text.set("0 %")
prg_lab = tk.Label(mainframe, textvariable=prg_text)
prg_lab.grid(column=2, row=8)

main_p_var = tk.DoubleVar()
main_prg_bar = ttk.Progressbar(mainframe, maximum=100, length=400, variable=main_p_var)
main_prg_bar.grid(column=2, row=9, columnspan=3)

sub_p_var = tk.DoubleVar()
sub_prg_bar = ttk.Progressbar(mainframe, maximum=100, length=400, variable=sub_p_var)
sub_prg_bar.grid(column=2, row=10, columnspan=3)

log_text = ScrolledText(mainframe, width=65, height=15, state="disabled")
log_text.grid(column=2, row=4)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

window.mainloop()
