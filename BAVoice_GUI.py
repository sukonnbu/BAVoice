import main
import liststds
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg_box
from tkinter.scrolledtext import ScrolledText
import webbrowser
import threading


def start_download():
    download_thread = threading.Thread(target=download_voices)
    download_thread.daemon = True
    download_thread.start()


# 학생 명부 열기
def open_std_list():
    std_list_thread = threading.Thread(target=liststds.make_std_list)
    std_list_thread.daemon = True
    std_list_thread.start()


# 입력란의 텍스트를 읽어 줄별로 나눔
def get_text():
    text = select_text.get("1.0", tk.END).strip()
    std_list = []
    
    while True:
        next_linespace_index = int(text.find("\n"))

        if next_linespace_index == -1:
            std_list.append(text.strip())
            break
        else:
            std_list.append(text[0:next_linespace_index].strip())
            text = text[next_linespace_index + 1:]

    set_log(str(std_list))

    return std_list


# 음성 다운로드
def download_voices():
    select_text['state'] = "disabled"
    zip_chkbox['state'] = "disabled"
    exp_combobox['state'] = "disabled"
    download_button['state'] = "disabled"

    set_prg_bar("main", 0)
    std_list = get_text()
    std_num = len(std_list)

    for i in range(0, std_num):
        std = main.Character(std_list[i], exp_combobox.get(), zip_var.get())
        std.crawl_voices(set_prg_bar, set_log)
        set_prg_bar("main", round((100 / std_num) * (i+1), 1))

    set_log("다운로드 완료!")

    msg_box.showinfo("알림", "다운로드 완료")
    select_text['state'] = "normal"
    zip_chkbox['state'] = "normal"
    exp_combobox['state'] = "normal"
    download_button['state'] = "normal"


# 프로그레스 바 설정
def set_prg_bar(type: str, value: float):
    if type == "main":
        main_p_var.set(value)
        prg_text.set(f"{value} %")

        main_prg_bar.update()

    elif type == "sub":
        sub_p_var.set(value)

        sub_prg_bar.update()


# 로그 메시지 출력
def set_log(text: str):
    log_text['state'] = "normal"
    log_text.insert(1.0, text + "\n")
    log_text['state'] = "disabled"
    window.update()


# 화면 기본 설정
window = tk.Tk()
window.title("BAVoice GUI")
window.iconbitmap("icon.ico")
window.resizable(False, False)

mainframe = ttk.Frame(window, padding="3 3 12 12")
mainframe.grid(column=0, row=0)
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)


# 메뉴 바
menubar = tk.Menu(window)
window.config(menu=menubar)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Check STD's Name", command=open_std_list)
file_menu.add_command(
    label="RVC",
    command=lambda: webbrowser.open_new("https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI")
)
menubar.add_cascade(label="File", menu=file_menu)


# 기본 화면 구성
logo_img = Image.open("Logo.png")
logo_img = logo_img.resize((500, 110))
img = ImageTk.PhotoImage(logo_img)

title_logo = tk.Label(mainframe, image=img)
title_logo.grid(column=2, row=1, columnspan=3)

title_lab = tk.Label(mainframe, text="Student List to Download:", font="arial")
title_lab.grid(column=2, row=2)


select_text = ScrolledText(mainframe, width=65, height=10)
select_text.grid(column=2, row=3)

log_text = ScrolledText(mainframe, width=65, height=15, state="disabled")
log_text.grid(column=2, row=4)


# 다운로드 설정
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


# 다운로드 버튼
download_button = tk.Button(
    mainframe, text="DOWNLOAD", command=start_download
)
download_button.grid(column=2, row=7)


# 주 프로그레스 바
prg_text = tk.StringVar()
prg_text.set("0 %")
prg_lab = tk.Label(mainframe, textvariable=prg_text)
prg_lab.grid(column=2, row=8)

main_p_var = tk.DoubleVar()
main_prg_bar = ttk.Progressbar(mainframe, maximum=100, length=400, variable=main_p_var)
main_prg_bar.grid(column=2, row=9, columnspan=3)

# 부 프로그레스 바
sub_p_var = tk.DoubleVar()
sub_prg_bar = ttk.Progressbar(mainframe, maximum=100, length=400, variable=sub_p_var)
sub_prg_bar.grid(column=2, row=10, columnspan=3)


# 화면의 요소 간의 거리를 조정
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

window.mainloop()
